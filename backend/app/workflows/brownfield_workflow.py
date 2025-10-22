"""
Brownfield Workflow for ArchMesh PoC.

This workflow handles brownfield projects by analyzing existing architecture,
integrating with knowledge base, and designing new features that work
seamlessly with existing systems.
"""

import asyncio
from typing import TypedDict, Optional, Dict, Any, List, Literal
from datetime import datetime
import json

from langgraph.graph import StateGraph, END

# Try to import PostgresSaver, fallback to None if not available
try:
    from langgraph.checkpoint.postgres import PostgresSaver
except ImportError:
    try:
        from langgraph_checkpoint.postgres import PostgresSaver
    except ImportError:
        PostgresSaver = None

from loguru import logger

from app.agents.github_analyzer_agent import GitHubAnalyzerAgent
from app.agents.requirements_agent import RequirementsAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.services.local_knowledge_base_service import LocalKnowledgeBaseService
from app.config import settings


class BrownfieldWorkflowState(TypedDict):
    """State for brownfield workflow."""
    # Session and project identification
    session_id: str
    project_id: str
    
    # Brownfield specific inputs
    repository_url: str
    branch: Optional[str]
    github_token: Optional[str]
    
    # Existing architecture data
    existing_architecture: Optional[Dict[str, Any]]
    analysis_metadata: Optional[Dict[str, Any]]
    
    # Standard workflow data
    document_path: Optional[str]
    requirements: Optional[Dict[str, Any]]
    proposed_architecture: Optional[Dict[str, Any]]
    integration_strategy: Optional[Dict[str, Any]]
    
    # Human feedback and approval
    human_feedback: Optional[Dict[str, Any]]
    approval_status: Optional[Literal["approved", "rejected", "pending"]]
    feedback_history: List[Dict[str, Any]]
    
    # Workflow control
    current_stage: str
    previous_stage: Optional[str]
    errors: List[str]
    warnings: List[str]
    
    # Metadata
    created_at: Optional[str]
    updated_at: Optional[str]
    completed_at: Optional[str]


class BrownfieldWorkflow:
    """
    Workflow for brownfield projects.
    
    This workflow handles the complete process of analyzing existing systems
    and designing new features that integrate seamlessly with them.
    
    Steps:
    1. analyze_existing → Extract current architecture from GitHub
    2. parse_requirements → Parse new requirements from documents
    3. human_review_requirements → Human review of requirements
    4. design_integration → Design architecture with brownfield context
    5. human_review_integration → Human review of integration design
    6. generate_implementation_plan → Create detailed implementation plan
    7. END
    """
    
    def __init__(self, db_connection_string: Optional[str] = None):
        """
        Initialize the brownfield workflow.
        
        Args:
            db_connection_string: Optional database connection string for checkpointing
        """
        # Initialize agents
        self.github_analyzer = GitHubAnalyzerAgent()
        self.requirements_agent = RequirementsAgent()
        self.architecture_agent = ArchitectureAgent(
            knowledge_base_service=LocalKnowledgeBaseService()
        )
        
        # Initialize local knowledge base service
        self.kb_service = LocalKnowledgeBaseService()
        
        # Initialize checkpointing
        if PostgresSaver is not None:
            if db_connection_string:
                self.checkpointer = PostgresSaver.from_conn_string(db_connection_string)
            else:
                # Use default connection string
                self.checkpointer = PostgresSaver.from_conn_string(settings.database_url)
        else:
            logger.warning("PostgresSaver not available, checkpointing disabled")
            self.checkpointer = None
        
        # Build the workflow graph
        self.graph = self._build_graph()
        
        logger.info("BrownfieldWorkflow initialized successfully")
    
    def _build_graph(self) -> StateGraph:
        """Build the brownfield workflow graph."""
        workflow = StateGraph(BrownfieldWorkflowState)
        
        # Add nodes
        workflow.add_node("analyze_existing", self._analyze_existing_node)
        workflow.add_node("parse_requirements", self._parse_requirements_node)
        workflow.add_node("human_review_requirements", self._human_review_requirements_node)
        workflow.add_node("design_integration", self._design_integration_node)
        workflow.add_node("human_review_integration", self._human_review_integration_node)
        workflow.add_node("generate_implementation_plan", self._generate_implementation_plan_node)
        workflow.add_node("finalize_workflow", self._finalize_workflow_node)
        
        # Set entry point
        workflow.set_entry_point("analyze_existing")
        
        # Add edges
        workflow.add_edge("analyze_existing", "parse_requirements")
        workflow.add_edge("parse_requirements", "human_review_requirements")
        
        # Conditional edges for human review
        workflow.add_conditional_edges(
            "human_review_requirements",
            self._check_requirements_approval,
            {
                "approved": "design_integration",
                "rejected": "parse_requirements",
                "needs_revision": "parse_requirements"
            }
        )
        
        workflow.add_edge("design_integration", "human_review_integration")
        
        workflow.add_conditional_edges(
            "human_review_integration",
            self._check_integration_approval,
            {
                "approved": "generate_implementation_plan",
                "rejected": "design_integration",
                "needs_revision": "design_integration"
            }
        )
        
        workflow.add_edge("generate_implementation_plan", "finalize_workflow")
        workflow.add_edge("finalize_workflow", END)
        
        if self.checkpointer is not None:
            return workflow.compile(checkpointer=self.checkpointer)
        else:
            return workflow.compile()
    
    async def _analyze_existing_node(self, state: BrownfieldWorkflowState) -> Dict[str, Any]:
        """
        Node: Analyze existing architecture from GitHub repository.
        
        This node:
        1. Clones and analyzes the GitHub repository
        2. Extracts architecture information
        3. Indexes the analysis in the knowledge base
        4. Updates the workflow state
        """
        try:
            logger.info(
                f"Analyzing existing architecture for repository: {state['repository_url']}",
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "stage": "analyze_existing"
                }
            )
            
            # Prepare input for GitHub analyzer
            github_input = {
                "repository_url": state["repository_url"],
                "branch": state.get("branch", "main"),
                "github_token": state.get("github_token"),
                "project_id": state["project_id"]
            }
            
            # Analyze the repository
            analysis_result = await self.github_analyzer.execute(github_input)
            
            # Index the analysis in knowledge base
            try:
                await self.kb_service.index_repository_analysis(
                    project_id=state["project_id"],
                    repository_url=state["repository_url"],
                    analysis=analysis_result
                )
                logger.info(f"Successfully indexed repository analysis in knowledge base")
            except Exception as kb_error:
                logger.warning(f"Failed to index in knowledge base: {str(kb_error)}")
                # Continue workflow even if knowledge base indexing fails
            
            # Prepare analysis metadata
            analysis_metadata = {
                "analyzed_at": datetime.utcnow().isoformat(),
                "repository_url": state["repository_url"],
                "branch": state.get("branch", "main"),
                "services_count": len(analysis_result.get("services", [])),
                "dependencies_count": len(analysis_result.get("dependencies", [])),
                "technologies_detected": list(analysis_result.get("technology_stack", {}).keys()),
                "analysis_quality": analysis_result.get("quality_score", 0.0)
            }
            
            return {
                "existing_architecture": analysis_result,
                "analysis_metadata": analysis_metadata,
                "current_stage": "existing_analyzed",
                "previous_stage": "analyze_existing",
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to analyze existing architecture: {str(e)}"
            logger.error(
                error_msg,
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "error": str(e)
                }
            )
            
            return {
                "errors": state.get("errors", []) + [error_msg],
                "current_stage": "failed",
                "previous_stage": "analyze_existing",
                "updated_at": datetime.utcnow().isoformat()
            }
    
    async def _parse_requirements_node(self, state: BrownfieldWorkflowState) -> Dict[str, Any]:
        """
        Node: Parse requirements from documents.
        
        This node processes requirement documents and extracts structured
        requirements for the new features to be integrated.
        """
        try:
            logger.info(
                f"Parsing requirements for project: {state['project_id']}",
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "stage": "parse_requirements"
                }
            )
            
            if not state.get("document_path"):
                raise ValueError("Document path is required for requirements parsing")
            
            # Prepare input for requirements agent
            requirements_input = {
                "document_path": state["document_path"],
                "project_context": {
                    "project_id": state["project_id"],
                    "existing_architecture": state.get("existing_architecture"),
                    "repository_url": state["repository_url"]
                }
            }
            
            # Parse requirements
            requirements_result = await self.requirements_agent.execute(requirements_input)
            
            return {
                "requirements": requirements_result,
                "current_stage": "requirements_parsed",
                "previous_stage": "parse_requirements",
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to parse requirements: {str(e)}"
            logger.error(
                error_msg,
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "error": str(e)
                }
            )
            
            return {
                "errors": state.get("errors", []) + [error_msg],
                "current_stage": "failed",
                "previous_stage": "parse_requirements",
                "updated_at": datetime.utcnow().isoformat()
            }
    
    async def _human_review_requirements_node(self, state: BrownfieldWorkflowState) -> Dict[str, Any]:
        """
        Node: Human review of parsed requirements.
        
        This node simulates human review of requirements and can be extended
        to integrate with actual human review systems.
        """
        try:
            logger.info(
                f"Human review of requirements for project: {state['project_id']}",
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "stage": "human_review_requirements"
                }
            )
            
            # For demo purposes, we'll simulate approval
            # In a real implementation, this would integrate with a human review system
            requirements = state.get("requirements", {})
            
            # Simulate review logic
            if requirements and requirements.get("confidence_score", 0) > 0.7:
                approval_status = "approved"
                feedback = {
                    "reviewer": "system",
                    "status": "approved",
                    "comments": "Requirements look comprehensive and well-structured",
                    "reviewed_at": datetime.utcnow().isoformat()
                }
            else:
                approval_status = "needs_revision"
                feedback = {
                    "reviewer": "system",
                    "status": "needs_revision",
                    "comments": "Requirements need more detail or have low confidence score",
                    "reviewed_at": datetime.utcnow().isoformat()
                }
            
            # Update feedback history
            feedback_history = state.get("feedback_history", [])
            feedback_history.append(feedback)
            
            return {
                "approval_status": approval_status,
                "human_feedback": feedback,
                "feedback_history": feedback_history,
                "current_stage": "requirements_reviewed",
                "previous_stage": "human_review_requirements",
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to review requirements: {str(e)}"
            logger.error(
                error_msg,
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "error": str(e)
                }
            )
            
            return {
                "errors": state.get("errors", []) + [error_msg],
                "current_stage": "failed",
                "previous_stage": "human_review_requirements",
                "updated_at": datetime.utcnow().isoformat()
            }
    
    async def _design_integration_node(self, state: BrownfieldWorkflowState) -> Dict[str, Any]:
        """
        Node: Design integration with existing architecture.
        
        This node uses the brownfield-aware architecture agent to design
        new features that integrate seamlessly with existing systems.
        """
        try:
            logger.info(
                f"Designing integration architecture for project: {state['project_id']}",
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "stage": "design_integration"
                }
            )
            
            # Prepare input for architecture agent
            architecture_input = {
                "requirements": state["requirements"],
                "mode": "brownfield",
                "project_id": state["project_id"],
                "existing_architecture": state["existing_architecture"],
                "constraints": {
                    "no_breaking_changes": True,
                    "use_existing_technologies": True,
                    "minimal_disruption": True
                },
                "preferences": ["microservices", "event-driven", "api-first"],
                "domain": "brownfield-integration"
            }
            
            # Design architecture
            architecture_result = await self.architecture_agent.execute(architecture_input)
            
            # Extract integration strategy
            integration_strategy = architecture_result.get("integration_strategy", {})
            
            return {
                "proposed_architecture": architecture_result,
                "integration_strategy": integration_strategy,
                "current_stage": "integration_designed",
                "previous_stage": "design_integration",
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to design integration: {str(e)}"
            logger.error(
                error_msg,
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "error": str(e)
                }
            )
            
            return {
                "errors": state.get("errors", []) + [error_msg],
                "current_stage": "failed",
                "previous_stage": "design_integration",
                "updated_at": datetime.utcnow().isoformat()
            }
    
    async def _human_review_integration_node(self, state: BrownfieldWorkflowState) -> Dict[str, Any]:
        """
        Node: Human review of integration design.
        
        This node simulates human review of the proposed integration architecture.
        """
        try:
            logger.info(
                f"Human review of integration design for project: {state['project_id']}",
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "stage": "human_review_integration"
                }
            )
            
            # For demo purposes, we'll simulate approval
            # In a real implementation, this would integrate with a human review system
            proposed_architecture = state.get("proposed_architecture", {})
            integration_strategy = state.get("integration_strategy", {})
            
            # Simulate review logic
            if (proposed_architecture and 
                integration_strategy and 
                len(proposed_architecture.get("new_services", [])) > 0):
                approval_status = "approved"
                feedback = {
                    "reviewer": "system",
                    "status": "approved",
                    "comments": "Integration design looks solid with clear migration strategy",
                    "reviewed_at": datetime.utcnow().isoformat()
                }
            else:
                approval_status = "needs_revision"
                feedback = {
                    "reviewer": "system",
                    "status": "needs_revision",
                    "comments": "Integration design needs more detail or missing components",
                    "reviewed_at": datetime.utcnow().isoformat()
                }
            
            # Update feedback history
            feedback_history = state.get("feedback_history", [])
            feedback_history.append(feedback)
            
            return {
                "approval_status": approval_status,
                "human_feedback": feedback,
                "feedback_history": feedback_history,
                "current_stage": "integration_reviewed",
                "previous_stage": "human_review_integration",
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to review integration: {str(e)}"
            logger.error(
                error_msg,
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "error": str(e)
                }
            )
            
            return {
                "errors": state.get("errors", []) + [error_msg],
                "current_stage": "failed",
                "previous_stage": "human_review_integration",
                "updated_at": datetime.utcnow().isoformat()
            }
    
    async def _generate_implementation_plan_node(self, state: BrownfieldWorkflowState) -> Dict[str, Any]:
        """
        Node: Generate detailed implementation plan.
        
        This node creates a comprehensive implementation plan based on the
        approved integration design.
        """
        try:
            logger.info(
                f"Generating implementation plan for project: {state['project_id']}",
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "stage": "generate_implementation_plan"
                }
            )
            
            integration_strategy = state.get("integration_strategy", {})
            proposed_architecture = state.get("proposed_architecture", {})
            
            # Generate detailed implementation plan
            implementation_plan = {
                "project_overview": {
                    "project_id": state["project_id"],
                    "repository_url": state["repository_url"],
                    "total_phases": len(integration_strategy.get("phases", [])),
                    "estimated_duration": self._calculate_total_duration(integration_strategy),
                    "risk_level": proposed_architecture.get("impact_analysis", {}).get("risk_level", "medium")
                },
                "phases": integration_strategy.get("phases", []),
                "testing_strategy": integration_strategy.get("testing_strategy", []),
                "monitoring_setup": integration_strategy.get("monitoring", []),
                "rollback_procedures": integration_strategy.get("rollback_plan", ""),
                "success_criteria": self._extract_success_criteria(proposed_architecture),
                "resource_requirements": self._estimate_resource_requirements(proposed_architecture),
                "timeline": self._create_detailed_timeline(integration_strategy),
                "risk_mitigation": self._create_risk_mitigation_plan(proposed_architecture)
            }
            
            return {
                "implementation_plan": implementation_plan,
                "current_stage": "implementation_planned",
                "previous_stage": "generate_implementation_plan",
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to generate implementation plan: {str(e)}"
            logger.error(
                error_msg,
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "error": str(e)
                }
            )
            
            return {
                "errors": state.get("errors", []) + [error_msg],
                "current_stage": "failed",
                "previous_stage": "generate_implementation_plan",
                "updated_at": datetime.utcnow().isoformat()
            }
    
    async def _finalize_workflow_node(self, state: BrownfieldWorkflowState) -> Dict[str, Any]:
        """
        Node: Finalize the brownfield workflow.
        
        This node completes the workflow and prepares the final results.
        """
        try:
            logger.info(
                f"Finalizing brownfield workflow for project: {state['project_id']}",
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "stage": "finalize_workflow"
                }
            )
            
            # Create final summary
            workflow_summary = {
                "project_id": state["project_id"],
                "session_id": state["session_id"],
                "repository_url": state["repository_url"],
                "workflow_status": "completed",
                "stages_completed": [
                    "existing_analyzed",
                    "requirements_parsed",
                    "requirements_reviewed",
                    "integration_designed",
                    "integration_reviewed",
                    "implementation_planned"
                ],
                "deliverables": {
                    "existing_architecture": state.get("existing_architecture"),
                    "requirements": state.get("requirements"),
                    "proposed_architecture": state.get("proposed_architecture"),
                    "integration_strategy": state.get("integration_strategy"),
                    "implementation_plan": state.get("implementation_plan")
                },
                "quality_metrics": {
                    "analysis_quality": state.get("analysis_metadata", {}).get("analysis_quality", 0.0),
                    "requirements_confidence": state.get("requirements", {}).get("confidence_score", 0.0),
                    "architecture_quality": state.get("proposed_architecture", {}).get("quality_score", 0.0)
                },
                "feedback_history": state.get("feedback_history", []),
                "errors": state.get("errors", []),
                "warnings": state.get("warnings", [])
            }
            
            return {
                "workflow_summary": workflow_summary,
                "current_stage": "completed",
                "previous_stage": "finalize_workflow",
                "completed_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Failed to finalize workflow: {str(e)}"
            logger.error(
                error_msg,
                extra={
                    "session_id": state["session_id"],
                    "project_id": state["project_id"],
                    "error": str(e)
                }
            )
            
            return {
                "errors": state.get("errors", []) + [error_msg],
                "current_stage": "failed",
                "previous_stage": "finalize_workflow",
                "updated_at": datetime.utcnow().isoformat()
            }
    
    def _check_requirements_approval(self, state: BrownfieldWorkflowState) -> str:
        """Check if requirements are approved."""
        approval_status = state.get("approval_status", "pending")
        
        if approval_status == "approved":
            return "approved"
        elif approval_status == "rejected":
            return "rejected"
        else:
            return "needs_revision"
    
    def _check_integration_approval(self, state: BrownfieldWorkflowState) -> str:
        """Check if integration design is approved."""
        approval_status = state.get("approval_status", "pending")
        
        if approval_status == "approved":
            return "approved"
        elif approval_status == "rejected":
            return "rejected"
        else:
            return "needs_revision"
    
    def _calculate_total_duration(self, integration_strategy: Dict[str, Any]) -> str:
        """Calculate total estimated duration from integration strategy."""
        phases = integration_strategy.get("phases", [])
        total_weeks = 0
        
        for phase in phases:
            duration = phase.get("duration", "1 week")
            if "week" in duration.lower():
                try:
                    weeks = int(duration.split()[0])
                    total_weeks += weeks
                except (ValueError, IndexError):
                    total_weeks += 1
        
        return f"{total_weeks} weeks"
    
    def _extract_success_criteria(self, proposed_architecture: Dict[str, Any]) -> List[str]:
        """Extract success criteria from proposed architecture."""
        criteria = []
        
        # From implementation plan
        impl_plan = proposed_architecture.get("implementation_plan", {})
        criteria.extend(impl_plan.get("success_metrics", []))
        
        # From impact analysis
        impact_analysis = proposed_architecture.get("impact_analysis", {})
        if impact_analysis.get("breaking_changes") == False:
            criteria.append("No breaking changes to existing services")
        
        if impact_analysis.get("downtime_required") == False:
            criteria.append("Zero-downtime deployment")
        
        return criteria
    
    def _estimate_resource_requirements(self, proposed_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resource requirements for implementation."""
        new_services = proposed_architecture.get("new_services", [])
        modified_services = proposed_architecture.get("modified_services", [])
        
        return {
            "development_team_size": max(2, len(new_services) + len(modified_services)),
            "estimated_effort_hours": sum(
                service.get("estimated_effort", 40) for service in new_services + modified_services
            ),
            "infrastructure_requirements": {
                "new_services": len(new_services),
                "modified_services": len(modified_services),
                "additional_databases": len([s for s in new_services if s.get("type") == "database"])
            }
        }
    
    def _create_detailed_timeline(self, integration_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed timeline from integration strategy."""
        phases = integration_strategy.get("phases", [])
        timeline = {
            "phases": [],
            "milestones": [],
            "dependencies": []
        }
        
        current_date = datetime.utcnow()
        
        for i, phase in enumerate(phases):
            phase_info = {
                "phase_number": i + 1,
                "name": phase.get("name", f"Phase {i + 1}"),
                "description": phase.get("description", ""),
                "duration": phase.get("duration", "1 week"),
                "start_date": current_date.isoformat(),
                "services": phase.get("services", []),
                "deliverables": phase.get("deliverables", []),
                "success_criteria": phase.get("success_criteria", [])
            }
            
            timeline["phases"].append(phase_info)
            
            # Add milestone
            timeline["milestones"].append({
                "name": f"Complete {phase_info['name']}",
                "target_date": current_date.isoformat(),
                "description": f"Complete {phase_info['description']}"
            })
        
        return timeline
    
    def _create_risk_mitigation_plan(self, proposed_architecture: Dict[str, Any]) -> Dict[str, Any]:
        """Create risk mitigation plan from proposed architecture."""
        impact_analysis = proposed_architecture.get("impact_analysis", {})
        integration_strategy = proposed_architecture.get("integration_strategy", {})
        
        risks = []
        mitigations = []
        
        # Extract risks from implementation plan
        impl_plan = proposed_architecture.get("implementation_plan", {})
        for risk in impl_plan.get("risks", []):
            risks.append({
                "description": risk.get("risk", ""),
                "impact": risk.get("impact", "medium"),
                "probability": risk.get("probability", "medium"),
                "mitigation": risk.get("mitigation", "")
            })
        
        # Add brownfield-specific risks
        if impact_analysis.get("breaking_changes"):
            risks.append({
                "description": "Breaking changes to existing services",
                "impact": "high",
                "probability": "medium",
                "mitigation": "Use feature flags and gradual rollout"
            })
        
        if impact_analysis.get("data_migration"):
            risks.append({
                "description": "Data migration required",
                "impact": "high",
                "probability": "low",
                "mitigation": "Comprehensive backup and rollback procedures"
            })
        
        return {
            "risks": risks,
            "mitigation_strategies": integration_strategy.get("testing_strategy", []),
            "rollback_procedures": integration_strategy.get("rollback_plan", ""),
            "monitoring_plan": integration_strategy.get("monitoring", [])
        }
    
    async def run_workflow(
        self,
        session_id: str,
        project_id: str,
        repository_url: str,
        document_path: str,
        branch: Optional[str] = "main",
        github_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the complete brownfield workflow.
        
        Args:
            session_id: Unique session identifier
            project_id: Project identifier
            repository_url: GitHub repository URL
            document_path: Path to requirements document
            branch: Git branch to analyze (default: main)
            github_token: Optional GitHub token for private repos
            
        Returns:
            Workflow execution result
        """
        try:
            logger.info(
                f"Starting brownfield workflow",
                extra={
                    "session_id": session_id,
                    "project_id": project_id,
                    "repository_url": repository_url
                }
            )
            
            # Initialize state
            initial_state = BrownfieldWorkflowState(
                session_id=session_id,
                project_id=project_id,
                repository_url=repository_url,
                branch=branch,
                github_token=github_token,
                document_path=document_path,
                current_stage="starting",
                errors=[],
                warnings=[],
                feedback_history=[],
                created_at=datetime.utcnow().isoformat(),
                updated_at=datetime.utcnow().isoformat()
            )
            
            # Run the workflow
            result = await self.graph.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": session_id}}
            )
            
            logger.info(
                f"Brownfield workflow completed",
                extra={
                    "session_id": session_id,
                    "project_id": project_id,
                    "final_stage": result.get("current_stage", "unknown")
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(
                f"Brownfield workflow failed: {str(e)}",
                extra={
                    "session_id": session_id,
                    "project_id": project_id,
                    "error": str(e)
                }
            )
            raise
    
    async def get_workflow_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get the current status of a workflow session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Current workflow status
        """
        try:
            # Get the current state from the checkpoint
            state = await self.graph.aget_state(
                config={"configurable": {"thread_id": session_id}}
            )
            
            return {
                "session_id": session_id,
                "current_stage": state.values.get("current_stage", "unknown"),
                "status": "completed" if state.values.get("current_stage") == "completed" else "in_progress",
                "errors": state.values.get("errors", []),
                "warnings": state.values.get("warnings", []),
                "last_updated": state.values.get("updated_at")
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            return {
                "session_id": session_id,
                "status": "error",
                "error": str(e)
            }
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """Get information about the brownfield workflow."""
        return {
            "workflow_name": "Brownfield Workflow",
            "description": "Complete workflow for brownfield projects with GitHub analysis and integration design",
            "stages": [
                "analyze_existing",
                "parse_requirements", 
                "human_review_requirements",
                "design_integration",
                "human_review_integration",
                "generate_implementation_plan",
                "finalize_workflow"
            ],
            "features": [
                "GitHub repository analysis",
                "Knowledge base integration",
                "Brownfield-aware architecture design",
                "Integration strategy generation",
                "Implementation planning",
                "Human review integration",
                "Risk assessment and mitigation"
            ],
            "agents_used": [
                "GitHubAnalyzerAgent",
                "RequirementsAgent", 
                "ArchitectureAgent"
            ],
            "services_used": [
                "KnowledgeBaseService"
            ]
        }
