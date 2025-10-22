"""
Architecture Generator - Enhanced component for generating comprehensive architecture
"""

import uuid
from typing import List, Dict, Any
from .models import (
    Architecture, ArchitectureComponent, TechnologyStack, 
    ArchitectureStyle, ComponentType, TechnologyCategory
)
from app.modules.requirements.models import ExtractedRequirements
from app.modules.llm_service import SimpleLLMService


class ArchitectureGenerator:
    """
    Enhanced architecture generator that creates comprehensive architecture from requirements using LLM.
    
    Single responsibility: Generate detailed architecture from requirements
    """
    
    def __init__(self):
        self.llm_service = SimpleLLMService()
        
        # Enhanced technology mappings
        self.technology_mappings = {
            TechnologyCategory.FRONTEND: ["React", "Vue.js", "Angular", "Next.js", "TypeScript", "Tailwind CSS"],
            TechnologyCategory.BACKEND: ["Node.js", "Python", "Java", "C#", "Go", "Rust", "TypeScript"],
            TechnologyCategory.DATABASE: ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "InfluxDB"],
            TechnologyCategory.INFRASTRUCTURE: ["AWS", "Docker", "Kubernetes", "Nginx", "Terraform", "Helm"],
            TechnologyCategory.MONITORING: ["Prometheus", "Grafana", "ELK Stack", "Jaeger", "Zipkin"],
            TechnologyCategory.SECURITY: ["OAuth2", "JWT", "HTTPS", "Firewall", "Vault", "Istio"]
        }
        
        # Enhanced component templates
        self.component_templates = {
            "web_app": {
                "type": ComponentType.FRONTEND,
                "technologies": ["React", "Next.js", "TypeScript"],
                "responsibilities": ["User Interface", "User Experience", "Client-side Logic", "State Management"]
            },
            "api_service": {
                "type": ComponentType.SERVICE,
                "technologies": ["Node.js", "Express", "TypeScript"],
                "responsibilities": ["API Endpoints", "Business Logic", "Data Processing", "Validation"]
            },
            "database": {
                "type": ComponentType.DATABASE,
                "technologies": ["PostgreSQL", "Redis"],
                "responsibilities": ["Data Storage", "Data Persistence", "Data Retrieval", "ACID Compliance"]
            },
            "api_gateway": {
                "type": ComponentType.API_GATEWAY,
                "technologies": ["Kong", "AWS API Gateway", "Istio"],
                "responsibilities": ["Request Routing", "Authentication", "Rate Limiting", "Load Balancing"]
            }
        }
    
    async def generate(self, requirements: ExtractedRequirements, domain: str = "cloud-native") -> Architecture:
        """
        Generate comprehensive architecture from requirements using LLM.
        
        Args:
            requirements: Extracted requirements
            domain: Project domain (cloud-native, data-platform, etc.)
            
        Returns:
            Architecture: Generated comprehensive architecture
        """
        try:
            # Convert requirements to dict for LLM processing
            requirements_dict = {
                "business_goals": [req.dict() for req in requirements.business_goals],
                "functional_requirements": [req.dict() for req in requirements.functional_requirements],
                "non_functional_requirements": [req.dict() for req in requirements.non_functional_requirements],
                "constraints": [req.dict() for req in requirements.constraints],
                "stakeholders": [req.dict() for req in requirements.stakeholders]
            }
            
            # Use LLM to generate comprehensive architecture analysis
            print(f"🔍 ArchitectureGenerator: Calling LLM for domain: {domain}")
            llm_analysis = await self.llm_service.generate_architecture_analysis(requirements_dict, domain)
            print(f"✅ ArchitectureGenerator: LLM analysis received, keys: {list(llm_analysis.keys()) if isinstance(llm_analysis, dict) else 'Not a dict'}")
            
            # Convert LLM response to our Architecture model
            architecture = self._convert_llm_analysis_to_architecture(llm_analysis)
            print(f"✅ ArchitectureGenerator: Architecture converted successfully, components: {len(architecture.components)}")
            return architecture
            
        except Exception as e:
            print(f"❌ ArchitectureGenerator: LLM analysis failed: {e}")
            import traceback
            print(f"❌ ArchitectureGenerator: Traceback: {traceback.format_exc()}")
            # Fallback to simple architecture generation
            print("🔄 ArchitectureGenerator: Using fallback architecture")
            return self._generate_fallback_architecture(requirements, domain)
    
    def _convert_llm_analysis_to_architecture(self, llm_analysis: Dict[str, Any]) -> Architecture:
        """Convert LLM analysis to Architecture model"""
        overview = llm_analysis.get("architecture_overview", {})
        components_data = llm_analysis.get("components", [])
        tech_stack_data = llm_analysis.get("technology_stack", {})
        
        # Convert components
        components = []
        for comp_data in components_data:
            component = ArchitectureComponent(
                id=comp_data.get("id", str(uuid.uuid4())),
                name=comp_data.get("name", "Component"),
                type=self._map_component_type(comp_data.get("type", "service")),
                description=comp_data.get("description", ""),
                technologies=comp_data.get("technologies", []),
                responsibilities=comp_data.get("responsibilities", [])
            )
            components.append(component)
        
        # Convert technology stack
        technology_stack = TechnologyStack(
            frontend=tech_stack_data.get("frontend", []),
            backend=tech_stack_data.get("backend", []),
            database=tech_stack_data.get("database", []),
            infrastructure=tech_stack_data.get("infrastructure", []),
            monitoring=tech_stack_data.get("monitoring", []),
            security=tech_stack_data.get("security", [])
        )
        
        # Determine architecture style
        style_str = overview.get("style", "microservices")
        style = self._map_architecture_style(style_str)
        
        # Calculate quality score based on LLM analysis
        quality_score = self._calculate_enhanced_quality_score(llm_analysis)
        
        return Architecture(
            id=str(uuid.uuid4()),
            name=overview.get("name", "Generated Architecture"),
            style=style,
            description=overview.get("description", "LLM-generated architecture"),
            components=components,
            technology_stack=technology_stack,
            quality_score=quality_score,
            metadata={
                "generated_from": "llm_analysis",
                "component_count": len(components),
                "complexity": "high" if len(components) > 8 else "medium" if len(components) > 4 else "low",
                "llm_analysis": llm_analysis  # Store full LLM analysis for detailed rendering
            }
        )
    
    def _map_component_type(self, type_str: str) -> ComponentType:
        """Map string component type to enum"""
        type_mapping = {
            "service": ComponentType.SERVICE,
            "database": ComponentType.DATABASE,
            "gateway": ComponentType.API_GATEWAY,
            "cache": ComponentType.CACHE,
            "monitoring": ComponentType.MONITORING,
            "security": ComponentType.SECURITY,
            "frontend": ComponentType.FRONTEND
        }
        return type_mapping.get(type_str.lower(), ComponentType.SERVICE)
    
    def _map_architecture_style(self, style_str: str) -> ArchitectureStyle:
        """Map string architecture style to enum"""
        style_mapping = {
            "microservices": ArchitectureStyle.MICROSERVICES,
            "monolith": ArchitectureStyle.MONOLITH,
            "serverless": ArchitectureStyle.SERVERLESS,
            "layered": ArchitectureStyle.LAYERED,
            "event-driven": ArchitectureStyle.EVENT_DRIVEN
        }
        return style_mapping.get(style_str.lower(), ArchitectureStyle.MICROSERVICES)
    
    def _calculate_enhanced_quality_score(self, llm_analysis: Dict[str, Any]) -> float:
        """Calculate quality score based on LLM analysis depth"""
        score = 0.5  # Base score
        
        # Component detail factor
        components = llm_analysis.get("components", [])
        if len(components) > 0:
            avg_detail = sum(
                len(comp.get("responsibilities", [])) + 
                len(comp.get("technologies", [])) + 
                len(comp.get("interfaces", []))
                for comp in components
            ) / len(components)
            score += min(avg_detail / 10, 0.3)  # Max 0.3 for detail
        
        # Implementation plan factor
        impl_plan = llm_analysis.get("implementation_plan", {})
        if impl_plan.get("phases") and impl_plan.get("tasks"):
            score += 0.2
        
        # Quality analysis factor
        quality_analysis = llm_analysis.get("quality_analysis", {})
        if quality_analysis:
            score += 0.1
        
        # Diagrams factor
        diagrams = llm_analysis.get("diagrams", {})
        if diagrams.get("c4_context") and diagrams.get("c4_container"):
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_fallback_architecture(self, requirements: ExtractedRequirements, domain: str) -> Architecture:
        """Generate fallback architecture when LLM fails"""
        # Determine architecture style
        style = self._determine_architecture_style(requirements)
        
        # Generate components
        components = self._generate_components(requirements, style)
        
        # Generate technology stack
        technology_stack = self._generate_technology_stack(components)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(components, requirements)
        
        return Architecture(
            id=str(uuid.uuid4()),
            name=f"{style.value.title()} Architecture",
            style=style,
            description=f"Fallback architecture designed for {requirements.functional_requirements[0].title if requirements.functional_requirements else 'the system'}",
            components=components,
            technology_stack=technology_stack,
            quality_score=quality_score,
            metadata={
                "generated_from": "fallback",
                "component_count": len(components),
                "complexity": "medium" if len(components) > 5 else "low"
            }
        )
    
    def _determine_architecture_style(self, requirements: ExtractedRequirements) -> ArchitectureStyle:
        """Simple architecture style determination"""
        # Count functional requirements to determine complexity
        func_count = len(requirements.functional_requirements)
        
        # Check for scalability requirements
        has_scalability = any(
            "concurrent" in req.description.lower() or "scale" in req.description.lower()
            for req in requirements.non_functional_requirements
        )
        
        # Check for security requirements
        has_security = any(
            "secure" in req.description.lower() or "security" in req.description.lower()
            for req in requirements.non_functional_requirements
        )
        
        # Simple decision logic
        if func_count > 5 and has_scalability:
            return ArchitectureStyle.MICROSERVICES
        elif has_security and func_count > 3:
            return ArchitectureStyle.LAYERED
        elif func_count <= 3:
            return ArchitectureStyle.MONOLITH
        else:
            return ArchitectureStyle.MICROSERVICES
    
    def _generate_components(self, requirements: ExtractedRequirements, style: ArchitectureStyle) -> List[ArchitectureComponent]:
        """Generate architecture components"""
        components = []
        
        # Always add frontend
        components.append(self._create_component("frontend", "Frontend Application"))
        
        # Add backend service
        components.append(self._create_component("api_service", "API Service"))
        
        # Add database
        components.append(self._create_component("database", "Database"))
        
        # Add API Gateway for microservices
        if style == ArchitectureStyle.MICROSERVICES:
            components.append(self._create_component("api_gateway", "API Gateway"))
        
        # Add load balancer for scalability
        if any("concurrent" in req.description.lower() for req in requirements.non_functional_requirements):
            components.append(self._create_component("load_balancer", "Load Balancer"))
        
        # Add cache for performance
        if any("fast" in req.description.lower() or "performance" in req.description.lower() 
               for req in requirements.non_functional_requirements):
            components.append(self._create_component("cache", "Cache Service"))
        
        return components
    
    def _create_component(self, template_key: str, name: str) -> ArchitectureComponent:
        """Create a component from template"""
        template = self.component_templates.get(template_key, {
            "type": ComponentType.SERVICE,
            "technologies": ["Node.js"],
            "responsibilities": ["Business Logic"]
        })
        
        return ArchitectureComponent(
            id=str(uuid.uuid4()),
            name=name,
            type=template["type"],
            description=f"{name} component for the system",
            technologies=template["technologies"],
            responsibilities=template["responsibilities"]
        )
    
    def _generate_technology_stack(self, components: List[ArchitectureComponent]) -> TechnologyStack:
        """Generate technology stack from components"""
        stack = TechnologyStack()
        
        # Collect technologies by category
        for component in components:
            if component.type == ComponentType.FRONTEND:
                stack.frontend.extend(component.technologies)
            elif component.type == ComponentType.SERVICE:
                stack.backend.extend(component.technologies)
            elif component.type == ComponentType.DATABASE:
                stack.database.extend(component.technologies)
            elif component.type == ComponentType.API_GATEWAY:
                stack.infrastructure.extend(component.technologies)
        
        # Remove duplicates
        stack.frontend = list(set(stack.frontend))
        stack.backend = list(set(stack.backend))
        stack.database = list(set(stack.database))
        stack.infrastructure = list(set(stack.infrastructure))
        
        # Add default technologies if empty
        if not stack.frontend:
            stack.frontend = ["React", "Next.js"]
        if not stack.backend:
            stack.backend = ["Node.js", "Express"]
        if not stack.database:
            stack.database = ["PostgreSQL"]
        if not stack.infrastructure:
            stack.infrastructure = ["Docker", "AWS"]
        
        return stack
    
    def _calculate_quality_score(self, components: List[ArchitectureComponent], requirements: ExtractedRequirements) -> float:
        """Calculate architecture quality score"""
        score = 0.5  # Base score
        
        # Component count factor
        if len(components) >= 3:
            score += 0.2
        
        # Technology diversity factor
        all_technologies = []
        for component in components:
            all_technologies.extend(component.technologies)
        
        if len(set(all_technologies)) > 3:
            score += 0.2
        
        # Requirements coverage factor
        if len(requirements.functional_requirements) > 0:
            score += 0.1
        
        return min(score, 1.0)
