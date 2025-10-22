"""
Diagram Renderer - Simple component for rendering C4 diagrams
"""

from typing import List
from .models import Architecture, Diagram, DiagramType


class DiagramRenderer:
    """
    Simple diagram renderer that creates C4 diagrams from architecture.
    
    Single responsibility: Render diagrams from architecture
    """
    
    def __init__(self):
        pass
    
    def render(self, architecture: Architecture) -> List[Diagram]:
        """
        Render diagrams from architecture.
        
        Args:
            architecture: Architecture to render
            
        Returns:
            List[Diagram]: Generated diagrams
        """
        diagrams = []
        
        # Generate C4 Context diagram
        context_diagram = self._render_context_diagram(architecture)
        diagrams.append(context_diagram)
        
        # Generate C4 Container diagram
        container_diagram = self._render_container_diagram(architecture)
        diagrams.append(container_diagram)
        
        # Generate C4 Component diagram for complex architectures
        if len(architecture.components) > 4:
            component_diagram = self._render_component_diagram(architecture)
            diagrams.append(component_diagram)
        
        return diagrams
    
    def _render_context_diagram(self, architecture: Architecture) -> Diagram:
        """Render C4 Context diagram"""
        plantuml_code = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

title {architecture.name} - System Context

Person(user, "User", "System user")
System(system, "{architecture.name}", "{architecture.description}")

Rel(user, system, "Uses", "HTTPS")
@enduml"""
        
        return Diagram(
            id=f"context_{architecture.id}",
            type=DiagramType.C4_CONTEXT,
            title="System Context",
            description="High-level view of the system and its users",
            content=plantuml_code
        )
    
    def _render_container_diagram(self, architecture: Architecture) -> Diagram:
        """Render C4 Container diagram"""
        # Build container definitions
        containers = []
        relationships = []
        
        for component in architecture.components:
            if component.type.value == "frontend":
                containers.append(f'Container(frontend, "{component.name}", "{component.technologies[0] if component.technologies else "Web"}", "{component.description}")')
            elif component.type.value == "service":
                containers.append(f'Container(api, "{component.name}", "{component.technologies[0] if component.technologies else "API"}", "{component.description}")')
            elif component.type.value == "database":
                containers.append(f'ContainerDb(database, "{component.name}", "{component.technologies[0] if component.technologies else "Database"}", "{component.description}")')
            elif component.type.value == "api_gateway":
                containers.append(f'Container(gateway, "{component.name}", "{component.technologies[0] if component.technologies else "Gateway"}", "{component.description}")')
        
        # Build relationships
        if any(c.type.value == "frontend" for c in architecture.components):
            relationships.append("Rel(user, frontend, \"Uses\", \"HTTPS\")")
        
        if any(c.type.value == "api_gateway" for c in architecture.components):
            relationships.append("Rel(frontend, gateway, \"API Calls\", \"HTTPS\")")
            relationships.append("Rel(gateway, api, \"Routes\", \"HTTPS\")")
        else:
            relationships.append("Rel(frontend, api, \"API Calls\", \"HTTPS\")")
        
        if any(c.type.value == "database" for c in architecture.components):
            relationships.append("Rel(api, database, \"Reads/Writes\", \"SQL\")")
        
        plantuml_code = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

title {architecture.name} - Container Diagram

Person(user, "User", "System user")
System_Boundary(system, "{architecture.name}") {{
{chr(10).join(containers)}
}}

{chr(10).join(relationships)}
@enduml"""
        
        return Diagram(
            id=f"container_{architecture.id}",
            type=DiagramType.C4_CONTAINER,
            title="Container Diagram",
            description="Architecture showing containers and their relationships",
            content=plantuml_code
        )
    
    def _render_component_diagram(self, architecture: Architecture) -> Diagram:
        """Render C4 Component diagram for complex architectures"""
        # Simple component diagram
        plantuml_code = f"""@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title {architecture.name} - Component Diagram

Container(api, "API Service", "Node.js", "Main API service")
Container(service1, "User Service", "Node.js", "User management")
Container(service2, "Order Service", "Node.js", "Order processing")
ContainerDb(database, "Database", "PostgreSQL", "Data storage")

Rel(api, service1, "Calls", "HTTP")
Rel(api, service2, "Calls", "HTTP")
Rel(service1, database, "Reads/Writes", "SQL")
Rel(service2, database, "Reads/Writes", "SQL")
@enduml"""
        
        return Diagram(
            id=f"component_{architecture.id}",
            type=DiagramType.C4_COMPONENT,
            title="Component Diagram",
            description="Detailed view of service components",
            content=plantuml_code
        )
