"""
Enhanced Diagram Generation Service for ArchMesh.

This service provides comprehensive diagram generation capabilities including:
- C4 synthesis (Context & Containers) with PlantUML generation
- Sequence diagrams for key use-cases
- NFR mapping & trade-off notes
- Knowledge graph integration
- Round-trip editing support
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from loguru import logger


class DiagramType(Enum):
    """Supported diagram types"""
    C4_CONTEXT = "c4_context"
    C4_CONTAINER = "c4_container"
    C4_COMPONENT = "c4_component"
    C4_CODE = "c4_code"
    SEQUENCE = "sequence"
    DEPLOYMENT = "deployment"
    NFR_MAPPING = "nfr_mapping"


class OutputFormat(Enum):
    """Supported output formats"""
    PLANTUML = "plantuml"
    MERMAID = "mermaid"


class C4Level(Enum):
    """C4 model levels"""
    CONTEXT = "context"
    CONTAINER = "container"
    COMPONENT = "component"
    CODE = "code"


@dataclass
class DiagramElement:
    """Base class for diagram elements"""
    id: str
    name: str
    description: str
    type: str
    properties: Dict[str, Any]


@dataclass
class C4Element(DiagramElement):
    """C4 model element"""
    level: C4Level
    technology: Optional[str] = None
    responsibilities: List[str] = None
    interfaces: List[str] = None
    data_flows: List[str] = None


@dataclass
class Relationship:
    """Relationship between diagram elements"""
    from_id: str
    to_id: str
    label: str
    description: str
    protocol: Optional[str] = None
    data_format: Optional[str] = None


@dataclass
class NFRRequirement:
    """Non-functional requirement"""
    id: str
    name: str
    description: str
    metric: str
    target_value: str
    unit: str
    priority: str
    affected_components: List[str]


@dataclass
class DiagramConfig:
    """Configuration for diagram generation"""
    diagram_type: DiagramType
    title: str
    description: str
    include_nfr: bool = True
    include_technology_stack: bool = True
    include_data_flows: bool = True
    include_security: bool = True
    include_monitoring: bool = True


class DiagramGenerationService:
    """
    Enhanced diagram generation service with comprehensive capabilities.
    
    Features:
    - C4 synthesis with PlantUML generation
    - Sequence diagrams from workflow paths
    - NFR mapping and trade-off analysis
    - Knowledge graph integration
    - Round-trip editing support
    """
    
    def __init__(self):
        """Initialize the diagram generation service."""
        self.logger = logger.bind(service="diagram_generation")
        self.logger.info("Diagram Generation Service initialized")
    
    async def generate_c4_diagram(
        self,
        architecture_data: Dict[str, Any],
        config: DiagramConfig,
        knowledge_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate C4 diagram with PlantUML output.
        
        Args:
            architecture_data: Architecture information
            config: Diagram configuration
            knowledge_context: Additional context from knowledge base
            
        Returns:
            Dictionary containing PlantUML code and metadata
        """
        try:
            self.logger.info(f"Generating C4 {config.diagram_type.value} diagram")
            
            # Extract components and relationships
            components = self._extract_components(architecture_data, config)
            relationships = self._extract_relationships(architecture_data, components)
            nfr_requirements = self._extract_nfr_requirements(architecture_data) if config.include_nfr else []
            
            # Generate PlantUML code
            plantuml_code = self._generate_plantuml_c4(
                components, relationships, nfr_requirements, config
            )
            
            # Generate Mermaid fallback
            mermaid_code = self._generate_mermaid_c4(
                components, relationships, config
            )
            
            return {
                "diagram_type": config.diagram_type.value,
                "title": config.title,
                "description": config.description,
                "plantuml_code": plantuml_code,
                "mermaid_code": mermaid_code,
                "components": [self._serialize_component(c) for c in components],
                "relationships": [self._serialize_relationship(r) for r in relationships],
                "nfr_requirements": [self._serialize_nfr(nfr) for nfr in nfr_requirements],
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "component_count": len(components),
                    "relationship_count": len(relationships),
                    "nfr_count": len(nfr_requirements)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating C4 diagram: {str(e)}")
            raise
    
    async def generate_sequence_diagram(
        self,
        workflow_data: Dict[str, Any],
        use_cases: List[str],
        config: DiagramConfig
    ) -> Dict[str, Any]:
        """
        Generate sequence diagrams for key use-cases.
        
        Args:
            workflow_data: Workflow execution data
            use_cases: List of use-case scenarios
            config: Diagram configuration
            
        Returns:
            Dictionary containing sequence diagrams
        """
        try:
            self.logger.info(f"Generating sequence diagrams for {len(use_cases)} use-cases")
            
            sequence_diagrams = []
            
            for use_case in use_cases:
                # Extract actors and interactions
                actors = self._extract_actors(workflow_data, use_case)
                interactions = self._extract_interactions(workflow_data, use_case)
                
                # Generate PlantUML sequence diagram
                plantuml_code = self._generate_plantuml_sequence(actors, interactions, use_case)
                
                # Generate Mermaid sequence diagram
                mermaid_code = self._generate_mermaid_sequence(actors, interactions, use_case)
                
                sequence_diagrams.append({
                    "use_case": use_case,
                    "plantuml_code": plantuml_code,
                    "mermaid_code": mermaid_code,
                    "actors": actors,
                    "interactions": interactions
                })
            
            return {
                "diagram_type": "sequence",
                "title": f"Sequence Diagrams - {config.title}",
                "description": config.description,
                "sequence_diagrams": sequence_diagrams,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "use_case_count": len(use_cases),
                    "total_actors": sum(len(d["actors"]) for d in sequence_diagrams),
                    "total_interactions": sum(len(d["interactions"]) for d in sequence_diagrams)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating sequence diagrams: {str(e)}")
            raise
    
    async def generate_nfr_mapping(
        self,
        architecture_data: Dict[str, Any],
        nfr_requirements: List[NFRRequirement],
        config: DiagramConfig
    ) -> Dict[str, Any]:
        """
        Generate NFR mapping and trade-off analysis.
        
        Args:
            architecture_data: Architecture information
            nfr_requirements: List of NFR requirements
            config: Diagram configuration
            
        Returns:
            Dictionary containing NFR mapping diagrams
        """
        try:
            self.logger.info(f"Generating NFR mapping for {len(nfr_requirements)} requirements")
            
            # Map NFRs to components
            component_nfr_mapping = self._map_nfr_to_components(architecture_data, nfr_requirements)
            
            # Generate trade-off analysis
            trade_offs = self._analyze_trade_offs(nfr_requirements, component_nfr_mapping)
            
            # Generate PlantUML NFR diagram
            plantuml_code = self._generate_plantuml_nfr(component_nfr_mapping, trade_offs)
            
            # Generate Mermaid NFR diagram
            mermaid_code = self._generate_mermaid_nfr(component_nfr_mapping, trade_offs)
            
            return {
                "diagram_type": "nfr_mapping",
                "title": f"NFR Mapping - {config.title}",
                "description": config.description,
                "plantuml_code": plantuml_code,
                "mermaid_code": mermaid_code,
                "component_nfr_mapping": component_nfr_mapping,
                "trade_offs": trade_offs,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "nfr_count": len(nfr_requirements),
                    "component_count": len(component_nfr_mapping),
                    "trade_off_count": len(trade_offs)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating NFR mapping: {str(e)}")
            raise
    
    def _extract_components(
        self, 
        architecture_data: Dict[str, Any], 
        config: DiagramConfig
    ) -> List[C4Element]:
        """Extract C4 components from architecture data."""
        components = []
        
        # Extract from architecture overview
        if "architecture_overview" in architecture_data:
            overview = architecture_data["architecture_overview"]
            
            # Add system boundary
            components.append(C4Element(
                id="system",
                name=overview.get("name", "System"),
                description=overview.get("description", "Main system"),
                type="system",
                level=C4Level.CONTEXT,
                responsibilities=overview.get("responsibilities", []),
                interfaces=overview.get("interfaces", [])
            ))
        
        # Extract components
        if "components" in architecture_data:
            for comp_data in architecture_data["components"]:
                level = self._determine_c4_level(comp_data.get("type", "service"))
                
                components.append(C4Element(
                    id=comp_data.get("id", comp_data.get("name", "").lower().replace(" ", "_")),
                    name=comp_data.get("name", "Unknown Component"),
                    description=comp_data.get("description", ""),
                    type=comp_data.get("type", "service"),
                    level=level,
                    technology=comp_data.get("technology"),
                    responsibilities=comp_data.get("responsibilities", []),
                    interfaces=comp_data.get("interfaces", []),
                    data_flows=comp_data.get("data_flows", [])
                ))
        
        return components
    
    def _extract_relationships(
        self, 
        architecture_data: Dict[str, Any], 
        components: List[C4Element]
    ) -> List[Relationship]:
        """Extract relationships between components."""
        relationships = []
        
        # Create component lookup
        component_map = {comp.id: comp for comp in components}
        
        # Extract from architecture data
        if "relationships" in architecture_data:
            for rel_data in architecture_data["relationships"]:
                relationships.append(Relationship(
                    from_id=rel_data.get("from", ""),
                    to_id=rel_data.get("to", ""),
                    label=rel_data.get("label", ""),
                    description=rel_data.get("description", ""),
                    protocol=rel_data.get("protocol"),
                    data_format=rel_data.get("data_format")
                ))
        
        # Infer relationships from data flows
        for component in components:
            if component.data_flows:
                for data_flow in component.data_flows:
                    # Try to find target component
                    target_id = self._find_target_component(data_flow, component_map)
                    if target_id:
                        relationships.append(Relationship(
                            from_id=component.id,
                            to_id=target_id,
                            label="Data Flow",
                            description=f"Data flow: {data_flow}",
                            protocol="HTTP/HTTPS",
                            data_format="JSON"
                        ))
        
        return relationships
    
    def _extract_nfr_requirements(self, architecture_data: Dict[str, Any]) -> List[NFRRequirement]:
        """Extract NFR requirements from architecture data."""
        nfr_requirements = []
        
        # Extract from NFR section
        if "non_functional_requirements" in architecture_data:
            nfr_data = architecture_data["non_functional_requirements"]
            
            for nfr in nfr_data:
                nfr_requirements.append(NFRRequirement(
                    id=nfr.get("id", nfr.get("name", "").lower().replace(" ", "_")),
                    name=nfr.get("name", "Unknown NFR"),
                    description=nfr.get("description", ""),
                    metric=nfr.get("metric", ""),
                    target_value=nfr.get("target_value", ""),
                    unit=nfr.get("unit", ""),
                    priority=nfr.get("priority", "medium"),
                    affected_components=nfr.get("affected_components", [])
                ))
        
        return nfr_requirements
    
    def _determine_c4_level(self, component_type: str) -> C4Level:
        """Determine C4 level based on component type."""
        type_mapping = {
            "system": C4Level.CONTEXT,
            "user": C4Level.CONTEXT,
            "external_system": C4Level.CONTEXT,
            "container": C4Level.CONTAINER,
            "service": C4Level.CONTAINER,
            "database": C4Level.CONTAINER,
            "api": C4Level.CONTAINER,
            "component": C4Level.COMPONENT,
            "class": C4Level.CODE,
            "function": C4Level.CODE
        }
        
        return type_mapping.get(component_type.lower(), C4Level.CONTAINER)
    
    def _find_target_component(self, data_flow: str, component_map: Dict[str, C4Element]) -> Optional[str]:
        """Find target component for data flow."""
        # Simple heuristic to find target component
        for comp_id, comp in component_map.items():
            if comp.name.lower() in data_flow.lower() or comp_id in data_flow.lower():
                return comp_id
        return None
    
    def _generate_plantuml_c4(
        self,
        components: List[C4Element],
        relationships: List[Relationship],
        nfr_requirements: List[NFRRequirement],
        config: DiagramConfig
    ) -> str:
        """Generate PlantUML C4 diagram code."""
        plantuml_lines = [
            "@startuml",
            "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml",
            "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml",
            "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml",
            "",
            f"title {config.title}",
            f"note right: {config.description}",
            ""
        ]
        
        # Add components based on level
        context_components = [c for c in components if c.level == C4Level.CONTEXT]
        container_components = [c for c in components if c.level == C4Level.CONTAINER]
        component_components = [c for c in components if c.level == C4Level.COMPONENT]
        
        # Add context level
        for comp in context_components:
            plantuml_lines.append(f"Person({comp.id}, \"{comp.name}\", \"{comp.description}\")")
        
        # Add container level
        for comp in container_components:
            tech = f"\\n{comp.technology}" if comp.technology else ""
            plantuml_lines.append(f"Container({comp.id}, \"{comp.name}\", \"{comp.technology or 'Technology'}\", \"{comp.description}\")")
        
        # Add component level
        for comp in component_components:
            plantuml_lines.append(f"Component({comp.id}, \"{comp.name}\", \"{comp.technology or 'Technology'}\", \"{comp.description}\")")
        
        plantuml_lines.append("")
        
        # Add relationships
        for rel in relationships:
            plantuml_lines.append(f"Rel({rel.from_id}, {rel.to_id}, \"{rel.label}\", \"{rel.protocol or 'HTTP'}\")")
        
        plantuml_lines.append("")
        
        # Add NFR notes if enabled
        if config.include_nfr and nfr_requirements:
            plantuml_lines.append("note right")
            plantuml_lines.append("**Non-Functional Requirements:**")
            for nfr in nfr_requirements:
                plantuml_lines.append(f"- {nfr.name}: {nfr.target_value} {nfr.unit}")
            plantuml_lines.append("end note")
        
        plantuml_lines.append("@enduml")
        
        return "\\n".join(plantuml_lines)
    
    def _generate_mermaid_c4(
        self,
        components: List[C4Element],
        relationships: List[Relationship],
        config: DiagramConfig
    ) -> str:
        """Generate Mermaid C4 diagram code."""
        mermaid_lines = [
            "graph TB",
            f"%% {config.title}",
            f"%% {config.description}",
            ""
        ]
        
        # Add components
        for comp in components:
            if comp.level == C4Level.CONTEXT:
                mermaid_lines.append(f"    {comp.id}[\"👤 {comp.name}<br/>{comp.description}\"]")
            elif comp.level == C4Level.CONTAINER:
                tech = f"<br/>{comp.technology}" if comp.technology else ""
                mermaid_lines.append(f"    {comp.id}[\"🏗️ {comp.name}{tech}<br/>{comp.description}\"]")
            else:
                mermaid_lines.append(f"    {comp.id}[\"⚙️ {comp.name}<br/>{comp.description}\"]")
        
        mermaid_lines.append("")
        
        # Add relationships
        for rel in relationships:
            protocol = f" ({rel.protocol})" if rel.protocol else ""
            mermaid_lines.append(f"    {rel.from_id} -->|{rel.label}{protocol}| {rel.to_id}")
        
        # Add styling
        mermaid_lines.extend([
            "",
            "    %% Styling",
            "    classDef contextClass fill:#e1f5fe,stroke:#01579b,stroke-width:2px",
            "    classDef containerClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px",
            "    classDef componentClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px",
            ""
        ])
        
        # Apply styles
        context_components = [c.id for c in components if c.level == C4Level.CONTEXT]
        container_components = [c.id for c in components if c.level == C4Level.CONTAINER]
        component_components = [c.id for c in components if c.level == C4Level.COMPONENT]
        
        if context_components:
            mermaid_lines.append(f"    class {','.join(context_components)} contextClass")
        if container_components:
            mermaid_lines.append(f"    class {','.join(container_components)} containerClass")
        if component_components:
            mermaid_lines.append(f"    class {','.join(component_components)} componentClass")
        
        return "\\n".join(mermaid_lines)
    
    def _generate_plantuml_sequence(
        self,
        actors: List[str],
        interactions: List[Dict[str, Any]],
        use_case: str
    ) -> str:
        """Generate PlantUML sequence diagram."""
        plantuml_lines = [
            "@startuml",
            f"title {use_case} - Sequence Diagram",
            ""
        ]
        
        # Add participants
        for actor in actors:
            plantuml_lines.append(f"participant \"{actor}\" as {actor.lower().replace(' ', '_')}")
        
        plantuml_lines.append("")
        
        # Add interactions
        for interaction in interactions:
            from_actor = interaction.get("from", "").lower().replace(" ", "_")
            to_actor = interaction.get("to", "").lower().replace(" ", "_")
            message = interaction.get("message", "")
            plantuml_lines.append(f"{from_actor} -> {to_actor}: {message}")
        
        plantuml_lines.append("@enduml")
        
        return "\\n".join(plantuml_lines)
    
    def _generate_mermaid_sequence(
        self,
        actors: List[str],
        interactions: List[Dict[str, Any]],
        use_case: str
    ) -> str:
        """Generate Mermaid sequence diagram."""
        mermaid_lines = [
            "sequenceDiagram",
            f"    title {use_case}",
            ""
        ]
        
        # Add participants
        for actor in actors:
            mermaid_lines.append(f"    participant {actor}")
        
        mermaid_lines.append("")
        
        # Add interactions
        for interaction in interactions:
            from_actor = interaction.get("from", "")
            to_actor = interaction.get("to", "")
            message = interaction.get("message", "")
            mermaid_lines.append(f"    {from_actor}->>{to_actor}: {message}")
        
        return "\\n".join(mermaid_lines)
    
    def _extract_actors(self, workflow_data: Dict[str, Any], use_case: str) -> List[str]:
        """Extract actors from workflow data."""
        actors = ["User"]  # Default actor
        
        # Extract from workflow steps
        if "steps" in workflow_data:
            for step in workflow_data["steps"]:
                if "actor" in step:
                    actors.append(step["actor"])
        
        return list(set(actors))  # Remove duplicates
    
    def _extract_interactions(self, workflow_data: Dict[str, Any], use_case: str) -> List[Dict[str, Any]]:
        """Extract interactions from workflow data."""
        interactions = []
        
        # Extract from workflow steps
        if "steps" in workflow_data:
            for i, step in enumerate(workflow_data["steps"]):
                if i < len(workflow_data["steps"]) - 1:
                    next_step = workflow_data["steps"][i + 1]
                    interactions.append({
                        "from": step.get("actor", "User"),
                        "to": next_step.get("actor", "System"),
                        "message": step.get("description", f"Step {i + 1}")
                    })
        
        return interactions
    
    def _map_nfr_to_components(
        self,
        architecture_data: Dict[str, Any],
        nfr_requirements: List[NFRRequirement]
    ) -> Dict[str, List[NFRRequirement]]:
        """Map NFR requirements to components."""
        mapping = {}
        
        for nfr in nfr_requirements:
            for component_id in nfr.affected_components:
                if component_id not in mapping:
                    mapping[component_id] = []
                mapping[component_id].append(nfr)
        
        return mapping
    
    def _analyze_trade_offs(
        self,
        nfr_requirements: List[NFRRequirement],
        component_mapping: Dict[str, List[NFRRequirement]]
    ) -> List[Dict[str, Any]]:
        """Analyze trade-offs between NFR requirements."""
        trade_offs = []
        
        # Find conflicting requirements
        for component_id, nfrs in component_mapping.items():
            if len(nfrs) > 1:
                # Check for potential conflicts
                for i, nfr1 in enumerate(nfrs):
                    for nfr2 in nfrs[i + 1:]:
                        if self._are_conflicting(nfr1, nfr2):
                            trade_offs.append({
                                "component": component_id,
                                "conflict": f"{nfr1.name} vs {nfr2.name}",
                                "description": f"Trade-off between {nfr1.name} and {nfr2.name}",
                                "impact": "medium"
                            })
        
        return trade_offs
    
    def _are_conflicting(self, nfr1: NFRRequirement, nfr2: NFRRequirement) -> bool:
        """Check if two NFR requirements are conflicting."""
        # Simple heuristic for conflict detection
        conflicting_pairs = [
            ("performance", "security"),
            ("scalability", "cost"),
            ("availability", "complexity"),
            ("security", "usability")
        ]
        
        nfr1_name = nfr1.name.lower()
        nfr2_name = nfr2.name.lower()
        
        for pair in conflicting_pairs:
            if (pair[0] in nfr1_name and pair[1] in nfr2_name) or \
               (pair[1] in nfr1_name and pair[0] in nfr2_name):
                return True
        
        return False
    
    def _generate_plantuml_nfr(
        self,
        component_mapping: Dict[str, List[NFRRequirement]],
        trade_offs: List[Dict[str, Any]]
    ) -> str:
        """Generate PlantUML NFR mapping diagram."""
        plantuml_lines = [
            "@startuml",
            "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml",
            "",
            "title NFR Mapping and Trade-off Analysis",
            ""
        ]
        
        # Add components with NFR annotations
        for component_id, nfrs in component_mapping.items():
            plantuml_lines.append(f"Container({component_id}, \"{component_id}\", \"Component\", \"Component with NFR requirements\")")
            
            # Add NFR notes
            if nfrs:
                plantuml_lines.append("note right")
                plantuml_lines.append("**NFR Requirements:**")
                for nfr in nfrs:
                    plantuml_lines.append(f"- {nfr.name}: {nfr.target_value} {nfr.unit}")
                plantuml_lines.append("end note")
        
        plantuml_lines.append("")
        
        # Add trade-off notes
        if trade_offs:
            plantuml_lines.append("note bottom")
            plantuml_lines.append("**Trade-offs:**")
            for trade_off in trade_offs:
                plantuml_lines.append(f"- {trade_off['conflict']}: {trade_off['description']}")
            plantuml_lines.append("end note")
        
        plantuml_lines.append("@enduml")
        
        return "\\n".join(plantuml_lines)
    
    def _generate_mermaid_nfr(
        self,
        component_mapping: Dict[str, List[NFRRequirement]],
        trade_offs: List[Dict[str, Any]]
    ) -> str:
        """Generate Mermaid NFR mapping diagram."""
        mermaid_lines = [
            "graph TB",
            "    %% NFR Mapping and Trade-off Analysis",
            ""
        ]
        
        # Add components
        for component_id, nfrs in component_mapping.items():
            nfr_list = "\\n".join([f"- {nfr.name}: {nfr.target_value} {nfr.unit}" for nfr in nfrs])
            mermaid_lines.append(f"    {component_id}[\"🏗️ {component_id}<br/>NFRs:<br/>{nfr_list}\"]")
        
        mermaid_lines.append("")
        
        # Add trade-offs as relationships
        for trade_off in trade_offs:
            mermaid_lines.append(f"    {trade_off['component']} -.->|Trade-off| {trade_off['component']}")
        
        # Add styling
        mermaid_lines.extend([
            "",
            "    %% Styling",
            "    classDef componentClass fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px",
            "    classDef tradeoffClass fill:#fff3e0,stroke:#e65100,stroke-width:2px",
            ""
        ])
        
        component_ids = list(component_mapping.keys())
        if component_ids:
            mermaid_lines.append(f"    class {','.join(component_ids)} componentClass")
        
        return "\\n".join(mermaid_lines)
    
    def _serialize_component(self, component: C4Element) -> Dict[str, Any]:
        """Serialize component for JSON output."""
        return {
            "id": component.id,
            "name": component.name,
            "description": component.description,
            "type": component.type,
            "level": component.level.value,
            "technology": component.technology,
            "responsibilities": component.responsibilities or [],
            "interfaces": component.interfaces or [],
            "data_flows": component.data_flows or []
        }
    
    def _serialize_relationship(self, relationship: Relationship) -> Dict[str, Any]:
        """Serialize relationship for JSON output."""
        return {
            "from_id": relationship.from_id,
            "to_id": relationship.to_id,
            "label": relationship.label,
            "description": relationship.description,
            "protocol": relationship.protocol,
            "data_format": relationship.data_format
        }
    
    def _serialize_nfr(self, nfr: NFRRequirement) -> Dict[str, Any]:
        """Serialize NFR requirement for JSON output."""
        return {
            "id": nfr.id,
            "name": nfr.name,
            "description": nfr.description,
            "metric": nfr.metric,
            "target_value": nfr.target_value,
            "unit": nfr.unit,
            "priority": nfr.priority,
            "affected_components": nfr.affected_components
        }


# Factory function
def get_diagram_generation_service() -> DiagramGenerationService:
    """Get diagram generation service instance."""
    return DiagramGenerationService()
