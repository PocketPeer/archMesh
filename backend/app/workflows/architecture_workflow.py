"""
Architecture Workflow for ArchMesh PoC.

This module implements a LangGraph workflow that orchestrates the process of
extracting requirements from documents and designing system architectures
with human review gates at key decision points.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.architecture_agent import ArchitectureAgent
from app.agents.requirements_agent import RequirementsAgent
from app.models import WorkflowSession, WorkflowStageEnum


def safe_enum_convert(value):
    """
    Safely convert a value to WorkflowStageEnum.
    
    Args:
        value: String or enum value to convert
        
    Returns:
        WorkflowStageEnum value
    """
    if isinstance(value, WorkflowStageEnum):
        return value
    
    if isinstance(value, str):
        try:
            return WorkflowStageEnum(value)
        except ValueError:
            # Fallback to STARTING if value is not valid
            return WorkflowStageEnum.STARTING
    
    return WorkflowStageEnum.STARTING


class ArchitectureWorkflowState(TypedDict):
    """
    State for the architecture generation workflow.
    
    This TypedDict defines the complete state that flows through the workflow,
    including input data, intermediate results, human feedback, and control flow.
    """
    # Identifiers
    session_id: str
    project_id: str
    
    # Input data
    document_path: str
    project_context: Optional[str]
    domain: str
    
    # Intermediate results
    requirements: Optional[Dict[str, Any]]
    architecture: Optional[Dict[str, Any]]
    
    # Human feedback and review
    human_feedback: Optional[Dict[str, Any]]
    review_history: List[Dict[str, Any]]
    
    # Workflow control
    current_stage: str
    previous_stage: Optional[str]
    errors: List[str]
    warnings: List[str]
    
    # Timestamps
    started_at: datetime
    last_updated: datetime
    requirements_completed_at: Optional[datetime]
    architecture_completed_at: Optional[datetime]
    
    # Metadata
    retry_count: int
    max_retries: int


class ArchitectureWorkflow:
    """
    Orchestrates the architecture generation workflow.
    
    This workflow implements a multi-stage process with human review gates:
    1. Parse Requirements → Extract structured requirements from documents
    2. Human Review Requirements → Wait for human approval/modification
    3. Design Architecture → Generate system architecture based on requirements
    4. Human Review Architecture → Wait for final human approval
    5. Complete → Workflow finished
    
    The workflow uses LangGraph for state management and PostgreSQL for persistence,
    allowing for resumable workflows and human-in-the-loop interactions.
    """
    
    def __init__(self, db_connection_string: Optional[str] = None):
        """
        Initialize the Architecture Workflow.
        
        Args:
            db_connection_string: Optional database connection string (not used in current version)
        """
        self.requirements_agent = RequirementsAgent()
        self.architecture_agent = ArchitectureAgent()
        
        # Initialize in-memory checkpointer for workflow state persistence
        # Note: PostgreSQL checkpointing not available in current LangGraph version
        self.checkpointer = MemorySaver()
        logger.info("In-memory checkpointer initialized successfully")
        
        # Build the workflow graph
        self.graph = self._build_graph()
        
        logger.info("Architecture Workflow initialized successfully")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow graph.
        
        Returns:
            Compiled StateGraph ready for execution
        """
        # Create the workflow graph
        workflow = StateGraph(ArchitectureWorkflowState)
        
        # Add workflow nodes
        workflow.add_node("parse_requirements", self._parse_requirements_node)
        workflow.add_node("human_review_requirements", self._human_review_requirements_node)
        workflow.add_node("design_architecture", self._design_architecture_node)
        workflow.add_node("human_review_architecture", self._human_review_architecture_node)
        workflow.add_node("complete", self._complete_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Set entry point
        workflow.set_entry_point("parse_requirements")
        
        # Add edges for normal flow
        workflow.add_edge("parse_requirements", "human_review_requirements")
        workflow.add_edge("design_architecture", "human_review_architecture")
        workflow.add_edge("complete", END)
        workflow.add_edge("handle_error", END)
        
        # Add conditional edges for human review decisions
        workflow.add_conditional_edges(
            "human_review_requirements",
            self._check_requirements_approval,
            {
                "approved": "design_architecture",
                "rejected": "parse_requirements",
                "needs_info": "parse_requirements",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "human_review_architecture",
            self._check_architecture_approval,
            {
                "approved": "complete",
                "rejected": "design_architecture",
                "needs_info": "design_architecture",
                "error": "handle_error"
            }
        )
        
        # Compile the graph with checkpointer
        return workflow.compile(checkpointer=self.checkpointer)

    async def _parse_requirements_node(
        self,
        state: ArchitectureWorkflowState
    ) -> Dict[str, Any]:
        """
        Node: Parse requirements from document using RequirementsAgent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with requirements data
        """
        try:
            logger.info(
                f"Parsing requirements for session {state['session_id']}",
                extra={
                    "session_id": str(state["session_id"]),
                    "project_id": str(state["project_id"]),
                    "document_path": state["document_path"],
                    "domain": state["domain"]
                }
            )
            
            # Execute requirements extraction
            requirements = await self.requirements_agent.execute({
                "document_path": state["document_path"],
                "project_context": state.get("project_context"),
                "domain": state["domain"],
                "session_id": str(state["session_id"])
            })
            
            logger.info(
                f"Requirements parsed successfully for session {state['session_id']}",
                extra={
                    "session_id": str(state["session_id"]),
                    "confidence_score": requirements.get("confidence_score", 0.0),
                    "requirements_count": len(requirements.get("structured_requirements", {}).get("functional_requirements", []))
                }
            )
            
            # Update state with requirements
            updated_state = {
                **state,
                "requirements": requirements,
                "current_stage": "requirements_review",
                "previous_stage": "parse_requirements",
                "requirements_completed_at": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
                "retry_count": 0  # Reset retry count on success
            }
            
            # Save state to database
            await self._save_state_to_database(updated_state)
            
            return updated_state
            
        except Exception as e:
            error_msg = f"Failed to parse requirements: {str(e)}"
            logger.error(
                error_msg,
                extra={
                    "session_id": str(state["session_id"]),
                    "error": str(e)
                }
            )
            
            return {
                "errors": state.get("errors", []) + [error_msg],
                "current_stage": "error",
                "last_updated": datetime.utcnow()
            }

    async def _design_architecture_node(
        self,
        state: ArchitectureWorkflowState
    ) -> Dict[str, Any]:
        """
        Node: Design architecture based on requirements using ArchitectureAgent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with architecture data
        """
        try:
            logger.info(
                f"Designing architecture for session {state['session_id']}",
                extra={
                    "session_id": str(state["session_id"]),
                    "project_id": str(state["project_id"]),
                    "domain": state["domain"]
                }
            )
            
            # Extract constraints and preferences from human feedback if available
            constraints = {}
            preferences = []
            
            if state.get("human_feedback"):
                feedback = state["human_feedback"]
                constraints = feedback.get("constraints", {})
                preferences = feedback.get("preferences", [])
            
            # Execute architecture design
            architecture = await self.architecture_agent.execute({
                "requirements": state["requirements"],
                "constraints": constraints,
                "preferences": preferences,
                "domain": state["domain"],
                "session_id": str(state["session_id"])
            })
            
            logger.info(
                f"Architecture designed successfully for session {state['session_id']}",
                extra={
                    "session_id": str(state["session_id"]),
                    "architecture_style": architecture.get("architecture_overview", {}).get("style", "unknown"),
                    "components_count": len(architecture.get("components", [])),
                    "quality_score": architecture.get("quality_score", 0.0)
                }
            )
            
            # Update state with architecture
            updated_state = {
                **state,
                "architecture": architecture,
                "current_stage": "architecture_review",
                "previous_stage": "design_architecture",
                "architecture_completed_at": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
                "retry_count": 0  # Reset retry count on success
            }
            
            # Save state to database
            await self._save_state_to_database(updated_state)
            
            return updated_state
            
        except Exception as e:
            error_msg = f"Failed to design architecture: {str(e)}"
            logger.error(
                error_msg,
                extra={
                    "session_id": str(state["session_id"]),
                    "error": str(e)
                }
            )
            
            return {
                "errors": state.get("errors", []) + [error_msg],
                "current_stage": "error",
                "last_updated": datetime.utcnow()
            }

    async def _human_review_requirements_node(
        self,
        state: ArchitectureWorkflowState
    ) -> Dict[str, Any]:
        """
        Node: Wait for human review of requirements (interrupt point).
        
        This node creates an interrupt point where the workflow pauses
        until human feedback is provided via the continue_workflow method.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with review information
        """
        logger.info(
            f"Waiting for human review of requirements for session {state['session_id']}",
            extra={
                "session_id": str(state["session_id"]),
                "current_stage": state["current_stage"]
            }
        )
        
        # Add review entry to history
        review_entry = {
            "stage": "requirements_review",
            "timestamp": datetime.utcnow(),
            "status": "pending",
            "requirements_summary": self._summarize_requirements(state.get("requirements", {}))
        }
        
        return {
            "review_history": state.get("review_history", []) + [review_entry],
            "last_updated": datetime.utcnow()
        }

    async def _human_review_architecture_node(
        self,
        state: ArchitectureWorkflowState
    ) -> Dict[str, Any]:
        """
        Node: Wait for human review of architecture (interrupt point).
        
        This node creates an interrupt point where the workflow pauses
        until human feedback is provided via the continue_workflow method.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with review information
        """
        logger.info(
            f"Waiting for human review of architecture for session {state['session_id']}",
            extra={
                "session_id": str(state["session_id"]),
                "current_stage": state["current_stage"]
            }
        )
        
        # Add review entry to history
        review_entry = {
            "stage": "architecture_review",
            "timestamp": datetime.utcnow(),
            "status": "pending",
            "architecture_summary": self._summarize_architecture(state.get("architecture", {}))
        }
        
        return {
            "review_history": state.get("review_history", []) + [review_entry],
            "last_updated": datetime.utcnow()
        }

    async def _complete_node(
        self,
        state: ArchitectureWorkflowState
    ) -> Dict[str, Any]:
        """
        Node: Mark workflow as completed.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with completion information
        """
        logger.info(
            f"Workflow completed successfully for session {state['session_id']}",
            extra={
                "session_id": str(state["session_id"]),
                "project_id": state["project_id"],
                "total_duration": (datetime.utcnow() - state["started_at"]).total_seconds()
            }
        )
        
        # Update state with completion
        updated_state = {
            **state,
            "current_stage": "completed",
            "last_updated": datetime.utcnow()
        }
        
        # Save final state to database
        await self._save_state_to_database(updated_state)
        
        return updated_state

    async def _handle_error_node(
        self,
        state: ArchitectureWorkflowState
    ) -> Dict[str, Any]:
        """
        Node: Handle workflow errors.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with error information
        """
        logger.error(
            f"Workflow error for session {state['session_id']}",
            extra={
                "session_id": str(state["session_id"]),
                "errors": state.get("errors", [])
            }
        )
        
        return {
            "current_stage": "failed",
            "last_updated": datetime.utcnow()
        }

    def _serialize_state_data(self, state: ArchitectureWorkflowState) -> dict:
        """
        Serialize workflow state data for database storage.
        
        Args:
            state: Current workflow state to serialize
            
        Returns:
            Serialized state data safe for JSON storage
        """
        def serialize_value(value):
            """Recursively serialize values for JSON storage."""
            if value is None:
                return None
            elif isinstance(value, (str, int, float, bool)):
                return value
            elif isinstance(value, datetime):
                return value.isoformat()
            elif isinstance(value, (list, tuple)):
                return [serialize_value(item) for item in value]
            elif isinstance(value, dict):
                return {k: serialize_value(v) for k, v in value.items()}
            else:
                # Convert any other type to string
                return str(value)
        
        # Create serialized state data
        serialized_data = {
            "current_stage": state.get("current_stage", "starting"),
            "stage_progress": state.get("stage_progress", 0.0),
            "completed_stages": state.get("completed_stages", []),
            # Store full requirements and architecture data for API access
            "requirements": state.get("requirements"),
            "architecture": state.get("architecture"),
            "stage_results": {
                "requirements_completed": state.get("requirements") is not None,
                "architecture_completed": state.get("architecture") is not None,
                "requirements_completed_at": state.get("requirements_completed_at"),
                "architecture_completed_at": state.get("architecture_completed_at"),
                "requirements_summary": self._summarize_requirements(state.get("requirements")) if state.get("requirements") else None,
                "architecture_summary": self._summarize_architecture(state.get("architecture")) if state.get("architecture") else None
            },
            "pending_tasks": state.get("pending_tasks", []),
            "errors": state.get("errors", []),
            "metadata": {
                "document_path": state.get("document_path"),
                "domain": state.get("domain"),
                "project_context": state.get("project_context"),
                "max_retries": state.get("max_retries", 3),
                "last_updated": state.get("last_updated")
            }
        }
        
        # Recursively serialize all values
        return serialize_value(serialized_data)

    def _summarize_requirements(self, requirements: dict) -> dict:
        """Create a summary of requirements for database storage."""
        if not requirements:
            return None
        
        try:
            structured_req = requirements.get("structured_requirements", {})
            return {
                "business_goals_count": len(structured_req.get("business_goals", [])),
                "functional_requirements_count": len(structured_req.get("functional_requirements", [])),
                "non_functional_requirements_count": sum(len(v) for v in structured_req.get("non_functional_requirements", {}).values()),
                "constraints_count": len(structured_req.get("constraints", [])),
                "stakeholders_count": len(structured_req.get("stakeholders", [])),
                "confidence_score": requirements.get("confidence_score", 0.0),
                "clarification_questions_count": len(requirements.get("clarification_questions", [])),
                "identified_gaps_count": len(requirements.get("identified_gaps", []))
            }
        except Exception:
            return {"error": "Failed to summarize requirements"}

    def _summarize_architecture(self, architecture: dict) -> dict:
        """Create a summary of architecture for database storage."""
        if not architecture:
            return None
        
        try:
            return {
                "architecture_style": architecture.get("architecture_overview", {}).get("style", "unknown"),
                "components_count": len(architecture.get("components", [])),
                "quality_score": architecture.get("quality_score", 0.0),
                "alternatives_count": len(architecture.get("alternatives", [])),
                "has_c4_diagram": bool(architecture.get("c4_diagram", {}).get("context"))
            }
        except Exception:
            return {"error": "Failed to summarize architecture"}

    async def _save_state_to_database(self, state: ArchitectureWorkflowState) -> None:
        """
        Save workflow state to database with proper serialization.
        
        Args:
            state: Current workflow state to save
        """
        try:
            from app.core.database import AsyncSessionLocal
            from sqlalchemy import select, update
            
            logger.info(f"Starting database save for session {str(state['session_id'])}")
            
            async with AsyncSessionLocal() as db:
                # Serialize state data for JSON storage
                state_data = self._serialize_state_data(state)
                
                logger.info(f"State data serialized: {str(state_data)[:200]}...")
                
                # Update the workflow session in database
                current_stage_enum = safe_enum_convert(state.get("current_stage", "starting"))
                logger.info(f"Converting stage '{state.get('current_stage', 'starting')}' to enum: {current_stage_enum}")
                
                stmt = (
                    update(WorkflowSession)
                    .where(WorkflowSession.id == state["session_id"])
                    .values(
                        current_stage=current_stage_enum,
                        state_data=state_data,
                        last_activity=datetime.utcnow(),
                        completed_at=datetime.utcnow() if state.get("current_stage") == "completed" else None
                    )
                )
                
                await db.execute(stmt)
                await db.commit()
                
                logger.info(
                    f"Saved workflow state to database for session {str(state['session_id'])}",
                    extra={
                        "session_id": str(state["session_id"]),
                        "current_stage": str(state.get("current_stage", "unknown")),
                        "completed_stages": str(state.get("completed_stages", []))
                    }
                )
                
        except Exception as e:
            logger.error(
                f"Failed to save workflow state to database: {str(e)}",
                extra={
                    "session_id": str(state.get("session_id")),
                    "error": str(e)
                }
            )
            # Don't raise - we don't want to break the workflow if database save fails

    def _check_requirements_approval(
        self,
        state: ArchitectureWorkflowState
    ) -> str:
        """
        Check human feedback for requirements approval.
        
        Args:
            state: Current workflow state
            
        Returns:
            Decision string for conditional edges
        """
        # Check if there are errors first
        if state.get("errors") and len(state["errors"]) > 0:
            return "error"
        
        feedback = state.get("human_feedback")
        if feedback is None:
            # No feedback yet, default to approved for testing
            return "approved"
        
        decision = feedback.get("decision", "pending")
        
        # Check for retry limit
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 3)
        
        if retry_count >= max_retries:
            logger.warning(
                f"Maximum retries exceeded for session {state['session_id']}",
                extra={"session_id": str(state["session_id"]), "retry_count": retry_count}
            )
            return "error"
        
        if decision == "approved":
            return "approved"
        elif decision == "rejected":
            return "rejected"
        elif decision == "needs_info":
            return "needs_info"
        else:
            # Default to waiting for feedback
            return "approved"  # For testing, auto-approve if no feedback

    def _check_architecture_approval(
        self,
        state: ArchitectureWorkflowState
    ) -> str:
        """
        Check human feedback for architecture approval.
        
        Args:
            state: Current workflow state
            
        Returns:
            Decision string for conditional edges
        """
        # Check if there are errors first
        if state.get("errors") and len(state["errors"]) > 0:
            return "error"
        
        feedback = state.get("human_feedback")
        if feedback is None:
            # No feedback yet, default to approved for testing
            return "approved"
        
        decision = feedback.get("decision", "pending")
        
        # Check for retry limit
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 3)
        
        if retry_count >= max_retries:
            logger.warning(
                f"Maximum retries exceeded for session {state['session_id']}",
                extra={"session_id": str(state["session_id"]), "retry_count": retry_count}
            )
            return "error"
        
        if decision == "approved":
            return "approved"
        elif decision == "rejected":
            return "rejected"
        elif decision == "needs_info":
            return "needs_info"
        else:
            # Default to waiting for feedback
            return "approved"  # For testing, auto-approve if no feedback

    def _summarize_requirements(self, requirements: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a summary of requirements for human review.
        
        Args:
            requirements: Full requirements data (can be None)
            
        Returns:
            Requirements summary
        """
        try:
            if requirements is None:
                return {
                    "business_goals_count": 0,
                    "functional_requirements_count": 0,
                    "stakeholders_count": 0,
                    "confidence_score": 0.0,
                    "clarification_questions_count": 0,
                    "identified_gaps_count": 0,
                    "status": "failed"
                }
            
            structured_reqs = requirements.get("structured_requirements", {})
            return {
                "business_goals_count": len(structured_reqs.get("business_goals", [])),
                "functional_requirements_count": len(structured_reqs.get("functional_requirements", [])),
                "stakeholders_count": len(structured_reqs.get("stakeholders", [])),
                "confidence_score": requirements.get("confidence_score", 0.0),
                "clarification_questions_count": len(requirements.get("clarification_questions", [])),
                "identified_gaps_count": len(requirements.get("identified_gaps", [])),
                "status": "success"
            }
        except Exception as e:
            logger.warning(f"Error summarizing requirements: {str(e)}")
            return {"status": "error", "error": str(e)}

    def _summarize_architecture(self, architecture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of architecture for human review.
        
        Args:
            architecture: Full architecture data
            
        Returns:
            Architecture summary
        """
        try:
            return {
                "architecture_style": architecture.get("architecture_overview", {}).get("style", "unknown"),
                "components_count": len(architecture.get("components", [])),
                "alternatives_count": len(architecture.get("alternatives", [])),
                "quality_score": architecture.get("quality_score", 0.0),
                "implementation_phases_count": len(architecture.get("implementation_plan", {}).get("phases", [])),
                "risks_count": len(architecture.get("implementation_plan", {}).get("risks", []))
            }
        except Exception as e:
            logger.warning(f"Error summarizing architecture: {str(e)}")
            return {}

    async def start(
        self,
        project_id: str,
        document_path: str,
        domain: str,
        project_context: Optional[str] = None,
        max_retries: int = 3,
        db: Optional[AsyncSession] = None
    ) -> tuple[str, Dict[str, Any]]:
        """
        Start a new architecture workflow.
        
        Args:
            project_id: ID of the project
            document_path: Path to the requirements document
            domain: Project domain (cloud-native, data-platform, enterprise)
            project_context: Optional project context information
            max_retries: Maximum number of retries for failed stages
            
        Returns:
            Tuple of (session_id, initial_result)
        """
        session_id = str(uuid.uuid4())
        
        # Create database session record if db is provided
        if db:
            try:
                db_workflow = WorkflowSession(
                    id=session_id,
                    project_id=project_id,
                    current_stage=WorkflowStageEnum.STARTING,
                    state_data={
                        "current_stage": "starting",
                        "stage_progress": 0.0,
                        "completed_stages": [],
                        "stage_results": {},
                        "pending_tasks": ["parse_requirements"],
                        "errors": [],
                        "metadata": {
                            "document_path": document_path,
                            "domain": domain,
                            "project_context": project_context,
                            "max_retries": max_retries
                        }
                    },
                    is_active=True,
                    started_at=datetime.utcnow(),
                    last_activity=datetime.utcnow()
                )
                db.add(db_workflow)
                await db.commit()
                logger.info(f"Created database session record for {session_id}")
            except Exception as e:
                logger.error(f"Failed to create database session record: {str(e)}")
                # Continue without database record
        
        logger.info(
            f"Starting architecture workflow",
            extra={
                "session_id": session_id,
                "project_id": project_id,
                "document_path": document_path,
                "domain": domain
            }
        )
        
        # Create initial state
        initial_state = ArchitectureWorkflowState(
            session_id=session_id,
            project_id=project_id,
            document_path=document_path,
            project_context=project_context,
            domain=domain,
            requirements=None,
            architecture=None,
            human_feedback=None,
            review_history=[],
            current_stage="starting",
            previous_stage=None,
            errors=[],
            warnings=[],
            started_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            requirements_completed_at=None,
            architecture_completed_at=None,
            retry_count=0,
            max_retries=max_retries
        )
        
        # Run workflow until first interrupt (human review)
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            result = await self.graph.ainvoke(initial_state, config)
            logger.info(f"Workflow started successfully for session {str(session_id)}")
            return session_id, result
        except Exception as e:
            logger.error(f"Failed to start workflow for session {str(session_id)}: {str(e)}")
            raise

    async def continue_workflow(
        self,
        session_id: str,
        human_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Continue workflow after human review.
        
        Args:
            session_id: Workflow session ID
            human_feedback: Human feedback and decision
            
        Returns:
            Updated workflow result
        """
        logger.info(
            f"Continuing workflow for session {session_id}",
            extra={
                "session_id": session_id,
                "decision": human_feedback.get("decision", "unknown")
            }
        )
        
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            # Get current state
            current_state = await self.graph.aget_state(config)
            
            # Update state with human feedback
            updated_state = {
                **current_state.values,
                "human_feedback": human_feedback,
                "last_updated": datetime.utcnow(),
                "retry_count": current_state.values.get("retry_count", 0) + 1
            }
            
            # Update review history
            if current_state.values.get("review_history"):
                review_history = current_state.values["review_history"].copy()
                if review_history:
                    review_history[-1]["status"] = human_feedback.get("decision", "unknown")
                    review_history[-1]["feedback"] = human_feedback
                    updated_state["review_history"] = review_history
            
            # Continue execution
            result = await self.graph.ainvoke(updated_state, config)
            
            logger.info(f"Workflow continued successfully for session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to continue workflow for session {session_id}: {str(e)}")
            raise

    async def get_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get current workflow status.
        
        Args:
            session_id: Workflow session ID
            
        Returns:
            Current workflow state
        """
        config = {"configurable": {"thread_id": session_id}}
        
        try:
            state = await self.graph.aget_state(config)
            return state.values
        except Exception as e:
            logger.error(f"Failed to get status for session {session_id}: {str(e)}")
            raise

    async def cancel_workflow(self, session_id: str) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            session_id: Workflow session ID
            
        Returns:
            True if cancelled successfully
        """
        try:
            # Update state to cancelled
            config = {"configurable": {"thread_id": session_id}}
            current_state = await self.graph.aget_state(config)
            
            updated_state = {
                **current_state.values,
                "current_stage": "cancelled",
                "last_updated": datetime.utcnow()
            }
            
            await self.graph.aupdate_state(config, updated_state)
            
            logger.info(f"Workflow cancelled for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow for session {session_id}: {str(e)}")
            return False

    def get_workflow_info(self) -> Dict[str, Any]:
        """
        Get information about the workflow.
        
        Returns:
            Workflow metadata and capabilities
        """
        return {
            "workflow_name": "Architecture Generation Workflow",
            "version": "1.0.0",
            "stages": [
                "parse_requirements",
                "human_review_requirements", 
                "design_architecture",
                "human_review_architecture",
                "complete"
            ],
            "agents_used": [
                "RequirementsAgent",
                "ArchitectureAgent"
            ],
            "human_review_points": 2,
            "supports_interruption": True,
            "supports_resumption": True,
            "checkpointing": "In-Memory"
        }
