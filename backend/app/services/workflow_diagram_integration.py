"""
Workflow Diagram Integration Service

This service integrates automatic diagram generation into the workflow system,
ensuring that diagrams are generated at appropriate stages of workflow execution.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.services.diagram_generation_service import DiagramGenerationService, DiagramType, OutputFormat
from app.services.enhanced_knowledge_base_service import EnhancedKnowledgeBaseService

logger = logging.getLogger(__name__)

class WorkflowDiagramIntegration:
    """
    Integrates diagram generation into workflow execution.
    
    This service automatically generates diagrams at key workflow stages:
    - After requirements analysis (C4 Context diagrams)
    - After architecture design (C4 Container/Component diagrams)
    - After integration design (Sequence diagrams)
    - After implementation planning (NFR mapping)
    """
    
    def __init__(self):
        self.diagram_service = DiagramGenerationService()
        self.kb_service = EnhancedKnowledgeBaseService()
        logger.info("WorkflowDiagramIntegration initialized")
    
    async def generate_workflow_diagrams(
        self,
        project_id: str,
        workflow_stage: str,
        workflow_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate appropriate diagrams based on workflow stage and data.
        
        Args:
            project_id: Project identifier
            workflow_stage: Current workflow stage
            workflow_data: Workflow execution data
            context: Additional context for diagram generation
            
        Returns:
            Dictionary containing generated diagrams and metadata
        """
        try:
            logger.info(f"Generating diagrams for project {project_id}, stage {workflow_stage}")
            
            diagrams = {}
            generation_results = {}
            
            # Determine which diagrams to generate based on workflow stage
            diagram_plan = self._get_diagram_plan(workflow_stage, workflow_data)
            
            for diagram_config in diagram_plan:
                try:
                    result = await self._generate_single_diagram(
                        project_id=project_id,
                        diagram_config=diagram_config,
                        workflow_data=workflow_data,
                        context=context
                    )
                    
                    if result:
                        diagrams[diagram_config["type"]] = result
                        generation_results[diagram_config["type"]] = {
                            "success": True,
                            "diagram_id": result.get("diagram_id"),
                            "generated_at": datetime.utcnow().isoformat()
                        }
                    else:
                        generation_results[diagram_config["type"]] = {
                            "success": False,
                            "error": "Failed to generate diagram"
                        }
                        
                except Exception as e:
                    logger.error(f"Failed to generate {diagram_config['type']} diagram: {e}")
                    generation_results[diagram_config["type"]] = {
                        "success": False,
                        "error": str(e)
                    }
            
            # Store diagram metadata in knowledge base
            await self._store_diagram_metadata(project_id, diagrams, generation_results)
            
            return {
                "diagrams": diagrams,
                "generation_results": generation_results,
                "total_diagrams": len(diagrams),
                "successful_generations": len([r for r in generation_results.values() if r.get("success")])
            }
            
        except Exception as e:
            logger.error(f"Failed to generate workflow diagrams: {e}")
            return {
                "diagrams": {},
                "generation_results": {},
                "error": str(e)
            }
    
    def _get_diagram_plan(self, workflow_stage: str, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Determine which diagrams to generate based on workflow stage.
        
        Args:
            workflow_stage: Current workflow stage
            workflow_data: Workflow execution data
            
        Returns:
            List of diagram configurations to generate
        """
        diagram_plan = []
        
        if workflow_stage in ["parse_requirements", "requirements_analysis"]:
            # Generate C4 Context diagram after requirements analysis
            diagram_plan.append({
                "type": "c4_context",
                "title": f"System Context - {workflow_data.get('project_name', 'Project')}",
                "description": "High-level system boundaries and external actors",
                "include_nfr": True,
                "include_technology_stack": True
            })
            
        elif workflow_stage in ["design_architecture", "architecture_design"]:
            # Generate C4 Container and Component diagrams after architecture design
            diagram_plan.extend([
                {
                    "type": "c4_container",
                    "title": f"Container View - {workflow_data.get('project_name', 'Project')}",
                    "description": "High-level architecture with containers",
                    "include_nfr": True,
                    "include_technology_stack": True
                },
                {
                    "type": "c4_component",
                    "title": f"Component View - {workflow_data.get('project_name', 'Project')}",
                    "description": "Detailed component interactions",
                    "include_nfr": True,
                    "include_technology_stack": True
                }
            ])
            
        elif workflow_stage in ["design_integration", "integration_design"]:
            # Generate Sequence diagrams for integration flows
            use_cases = workflow_data.get("use_cases", ["User Registration", "Order Processing"])
            diagram_plan.append({
                "type": "sequence",
                "title": f"Integration Flows - {workflow_data.get('project_name', 'Project')}",
                "description": "Integration interaction flows",
                "use_cases": use_cases
            })
            
        elif workflow_stage in ["generate_implementation_plan", "implementation_planning"]:
            # Generate NFR mapping for implementation planning
            nfr_requirements = workflow_data.get("nfr_requirements", [
                {
                    "name": "Response Time",
                    "metric": "latency",
                    "target_value": "200",
                    "unit": "ms",
                    "priority": "high"
                }
            ])
            diagram_plan.append({
                "type": "nfr_mapping",
                "title": f"NFR Mapping - {workflow_data.get('project_name', 'Project')}",
                "description": "Non-functional requirements mapping",
                "nfr_requirements": nfr_requirements
            })
        
        return diagram_plan
    
    async def _generate_single_diagram(
        self,
        project_id: str,
        diagram_config: Dict[str, Any],
        workflow_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a single diagram based on configuration.
        
        Args:
            project_id: Project identifier
            diagram_config: Diagram configuration
            workflow_data: Workflow execution data
            context: Additional context
            
        Returns:
            Generated diagram data or None if failed
        """
        try:
            diagram_type = DiagramType(diagram_config["type"])
            
            # Prepare context for diagram generation
            full_context = {
                "project_id": project_id,
                "workflow_data": workflow_data,
                "user_context": context or {},
                "requirements": workflow_data.get("requirements", {}),
                "architecture_data": workflow_data.get("architecture", {}),
                "existing_architecture": workflow_data.get("existing_architecture", {})
            }
            
            # Generate diagram
            result = await self.diagram_service.generate_diagram(
                project_id=project_id,
                diagram_type=diagram_type,
                output_format=OutputFormat.PLANTUML,  # Default to PlantUML
                context=full_context,
                architecture_data=workflow_data.get("architecture", {}),
                requirements=workflow_data.get("requirements", {}),
                use_knowledge_graph=True
            )
            
            # Add metadata
            result["diagram_id"] = f"{project_id}_{diagram_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            result["workflow_stage"] = workflow_data.get("current_stage", "unknown")
            result["generated_at"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate {diagram_config['type']} diagram: {e}")
            return None
    
    async def _store_diagram_metadata(
        self,
        project_id: str,
        diagrams: Dict[str, Any],
        generation_results: Dict[str, Any]
    ) -> None:
        """
        Store diagram metadata in the knowledge base.
        
        Args:
            project_id: Project identifier
            diagrams: Generated diagrams
            generation_results: Generation results metadata
        """
        try:
            # Store diagram metadata
            for diagram_type, diagram_data in diagrams.items():
                await self.kb_service.add_workflow_data(
                    project_id=project_id,
                    workflow_id=f"diagram_generation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    stage="diagram_generation",
                    data={
                        "diagram_type": diagram_type,
                        "diagram_data": diagram_data,
                        "generation_metadata": generation_results.get(diagram_type, {})
                    }
                )
            
            logger.info(f"Stored diagram metadata for project {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to store diagram metadata: {e}")
    
    async def get_project_diagrams(self, project_id: str) -> Dict[str, Any]:
        """
        Retrieve all diagrams for a project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Dictionary containing all project diagrams
        """
        try:
            # Get diagrams from knowledge base
            diagrams = await self.kb_service.get_project_knowledge(
                project_id=project_id,
                query="diagram",
                top_k=50
            )
            
            # Organize diagrams by type
            organized_diagrams = {}
            for diagram in diagrams:
                diagram_type = diagram.get("diagram_type", "unknown")
                if diagram_type not in organized_diagrams:
                    organized_diagrams[diagram_type] = []
                organized_diagrams[diagram_type].append(diagram)
            
            return {
                "project_id": project_id,
                "diagrams": organized_diagrams,
                "total_diagrams": len(diagrams),
                "diagram_types": list(organized_diagrams.keys())
            }
            
        except Exception as e:
            logger.error(f"Failed to get project diagrams: {e}")
            return {
                "project_id": project_id,
                "diagrams": {},
                "error": str(e)
            }
    
    async def regenerate_diagrams(
        self,
        project_id: str,
        diagram_types: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Regenerate specific diagram types for a project.
        
        Args:
            project_id: Project identifier
            diagram_types: List of diagram types to regenerate
            context: Additional context for regeneration
            
        Returns:
            Regeneration results
        """
        try:
            results = {}
            
            for diagram_type in diagram_types:
                try:
                    # Get latest workflow data
                    workflow_data = await self.kb_service.get_project_knowledge(
                        project_id=project_id,
                        query="workflow",
                        top_k=10
                    )
                    
                    # Generate diagram
                    diagram_config = {
                        "type": diagram_type,
                        "title": f"Regenerated {diagram_type} - Project {project_id}",
                        "description": f"Regenerated {diagram_type} diagram"
                    }
                    
                    result = await self._generate_single_diagram(
                        project_id=project_id,
                        diagram_config=diagram_config,
                        workflow_data=workflow_data[0] if workflow_data else {},
                        context=context
                    )
                    
                    results[diagram_type] = {
                        "success": result is not None,
                        "diagram": result
                    }
                    
                except Exception as e:
                    results[diagram_type] = {
                        "success": False,
                        "error": str(e)
                    }
            
            return {
                "project_id": project_id,
                "regeneration_results": results,
                "total_requested": len(diagram_types),
                "successful_regenerations": len([r for r in results.values() if r.get("success")])
            }
            
        except Exception as e:
            logger.error(f"Failed to regenerate diagrams: {e}")
            return {
                "project_id": project_id,
                "error": str(e)
            }
