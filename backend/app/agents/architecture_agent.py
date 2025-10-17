"""
Architecture Agent for ArchMesh PoC.

This agent is responsible for designing system architectures based on requirements,
generating C4 diagrams, recommending technology stacks, and providing alternatives.
"""

import json
import re
from typing import Any, Dict, List, Optional

from loguru import logger

from app.agents.base_agent import BaseAgent


class ArchitectureAgent(BaseAgent):
    """
    Agent responsible for designing system architectures.
    
    Capabilities:
    - Analyze requirements and design high-level architecture
    - Recommend appropriate technology stacks
    - Generate C4 diagrams in Mermaid format
    - Provide alternatives with trade-offs
    - Apply proven architectural patterns
    - Consider security, scalability, and compliance
    """

    def __init__(self):
        """
        Initialize the Architecture Agent.
        
        Uses Claude Opus for best-in-class architecture design capabilities
        with lower temperature for more consistent architectural decisions.
        """
        from app.config import settings
        
        # Get task-specific LLM configuration
        provider, model = settings.get_llm_config_for_task("architecture")
        
        super().__init__(
            agent_type="architecture_designer",
            agent_version="1.0.0",
            llm_provider=provider,
            llm_model=model,
            temperature=0.5,  # Lower for more consistent architectural decisions
            max_retries=3,
            timeout_seconds=180,  # Longer timeout for complex architectural analysis
            max_tokens=6000  # More tokens for detailed architecture descriptions
        )
        
        # Architecture patterns and styles
        self.architecture_patterns = [
            "microservices", "monolith", "serverless", "event-driven",
            "layered", "hexagonal", "clean-architecture", "domain-driven-design"
        ]
        
        # Technology categories
        self.tech_categories = {
            "frontend": ["React", "Vue.js", "Angular", "Next.js", "Svelte"],
            "backend": ["Node.js", "Python", "Java", "Go", "C#", "Rust"],
            "database": ["PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "DynamoDB"],
            "cloud": ["AWS", "Azure", "GCP", "DigitalOcean", "Heroku"],
            "container": ["Docker", "Kubernetes", "Docker Swarm", "Podman"],
            "messaging": ["RabbitMQ", "Apache Kafka", "AWS SQS", "Redis Pub/Sub"],
            "monitoring": ["Prometheus", "Grafana", "Datadog", "New Relic", "ELK Stack"]
        }
        
        logger.info("Architecture Agent initialized", extra={"agent_type": "architecture_designer"})

    def get_system_prompt(self) -> str:
        """
        Return the system prompt for architecture design.
        
        Returns:
            System prompt string with detailed instructions for architecture design
        """
        return """You are a senior enterprise architect. Design system architecture based on requirements.

TASK: Create comprehensive architecture design including:
1. System overview and high-level design
2. Technology stack recommendations
3. Key components and their interactions
4. Security and scalability considerations
5. Implementation phases and priorities

DESIGN PRINCIPLES:
- Start with business requirements
- Apply proven architectural patterns
- Consider scalability, security, maintainability
- Design for failure and resilience
- Optimize for developer experience

OUTPUT: Return structured JSON with:
- Architecture overview
- Technology stack with rationale
- Key components and interactions
- Security considerations
- Scalability approach
- Implementation roadmap
- C4 diagrams in Mermaid format

Be practical, specific, and focus on actionable architecture decisions."""

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design architecture based on requirements and constraints.
        
        Args:
            input_data: Dictionary containing:
                - requirements: Structured requirements from RequirementsAgent
                - constraints: Optional organizational constraints
                - preferences: Optional architecture style preferences
                - domain: Project domain (cloud-native, data-platform, enterprise)
                - session_id: Optional workflow session ID for logging
                
        Returns:
            Dictionary containing:
                - architecture_overview: High-level architecture description
                - c4_diagram_context: Mermaid C4 diagram code
                - components: Detailed component specifications
                - technology_stack: Recommended technology stack
                - alternatives: Alternative architectural approaches
                - implementation_plan: Phased implementation guidance
                - metadata: Additional processing information
                
        Raises:
            ValueError: If required input data is missing
            Exception: For other processing errors
        """
        try:
            # Validate input
            if "requirements" not in input_data:
                raise ValueError("requirements is required in input_data")
            
            requirements = input_data["requirements"]
            constraints = input_data.get("constraints", {})
            preferences = input_data.get("preferences", [])
            domain = input_data.get("domain", "cloud-native")
            session_id = input_data.get("session_id")
            
            logger.info(
                f"Starting architecture design",
                extra={
                    "agent_type": self.agent_type,
                    "domain": domain,
                    "session_id": session_id,
                }
            )
            
            # 1. Build comprehensive architecture design prompt
            prompt = self._build_architecture_prompt(requirements, constraints, preferences, domain)
            
            # 2. Call LLM for architecture design
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            response = await self._call_llm(messages)
            
            # 3. Parse and validate response
            architecture_data = self._parse_json_response(response)
            
            # 4. Generate C4 diagram
            c4_diagram = await self._generate_c4_diagram(architecture_data)
            architecture_data["c4_diagram_context"] = c4_diagram
            
            # 5. Validate and enhance the architecture data
            enhanced_data = self._validate_and_enhance_architecture(architecture_data, requirements)
            
            # 6. Add metadata
            enhanced_data["metadata"] = {
                "domain": domain,
                "architecture_timestamp": self.start_time.isoformat() if self.start_time else None,
                "agent_version": self.agent_version,
                "requirements_summary": self._summarize_requirements(requirements),
                "design_notes": self._generate_design_notes(enhanced_data, requirements)
            }
            
            logger.info(
                f"Architecture design completed successfully",
                extra={
                    "agent_type": self.agent_type,
                    "domain": domain,
                    "architecture_style": enhanced_data.get("architecture_overview", {}).get("style", "unknown"),
                    "components_count": len(enhanced_data.get("components", [])),
                    "alternatives_count": len(enhanced_data.get("alternatives", [])),
                }
            )
            
            return enhanced_data
            
        except Exception as e:
            logger.error(
                f"Architecture design failed: {str(e)}",
                extra={
                    "agent_type": self.agent_type,
                    "domain": input_data.get("domain"),
                    "error": str(e),
                }
            )
            raise

    def _build_architecture_prompt(
        self,
        requirements: Dict[str, Any],
        constraints: Dict[str, Any],
        preferences: List[str],
        domain: str
    ) -> str:
        """
        Build comprehensive architecture design prompt.
        
        Args:
            requirements: Structured requirements from RequirementsAgent
            constraints: Organizational constraints
            preferences: Architecture style preferences
            domain: Project domain
            
        Returns:
            Formatted prompt string
        """
        # Extract key information from requirements
        business_goals = requirements.get("structured_requirements", {}).get("business_goals", [])
        functional_reqs = requirements.get("structured_requirements", {}).get("functional_requirements", [])
        non_functional_reqs = requirements.get("structured_requirements", {}).get("non_functional_requirements", {})
        constraints_list = requirements.get("structured_requirements", {}).get("constraints", [])
        stakeholders = requirements.get("structured_requirements", {}).get("stakeholders", [])
        
        prompt = f"""Design a comprehensive system architecture for the following requirements:

PROJECT DOMAIN: {domain}

BUSINESS GOALS:
{chr(10).join(f"- {goal}" for goal in business_goals[:5])}

FUNCTIONAL REQUIREMENTS:
{chr(10).join(f"- {req}" for req in functional_reqs[:10])}

NON-FUNCTIONAL REQUIREMENTS:
"""
        
        for category, reqs in non_functional_reqs.items():
            if reqs:
                prompt += f"\n{category.upper()}:"
                for req in reqs[:3]:  # Limit to first 3 per category
                    prompt += f"\n- {req}"
        
        prompt += f"""

CONSTRAINTS:
{chr(10).join(f"- {constraint}" for constraint in constraints_list[:5])}

STAKEHOLDERS:
{chr(10).join(f"- {stakeholder.get('name', 'Unknown')} ({stakeholder.get('role', 'Unknown')}): {', '.join(stakeholder.get('concerns', []))}" for stakeholder in stakeholders[:5])}

ADDITIONAL CONSTRAINTS:
{chr(10).join(f"- {key}: {value}" for key, value in constraints.items()) if constraints else "None specified"}

ARCHITECTURE PREFERENCES:
{chr(10).join(f"- {pref}" for pref in preferences) if preferences else "No specific preferences"}

Please design a comprehensive architecture and provide the following in JSON format:

{{
  "architecture_overview": {{
    "style": "microservices|monolith|serverless|event-driven|layered",
    "rationale": "Detailed explanation of why this architectural style was chosen",
    "key_principles": ["principle1", "principle2"],
    "scalability_approach": "How the system will scale",
    "security_approach": "Security strategy and measures",
    "deployment_strategy": "How the system will be deployed"
  }},
  "components": [
    {{
      "name": "Component Name",
      "type": "service|database|queue|cache|gateway|monitoring",
      "description": "What this component does",
      "responsibilities": ["responsibility1", "responsibility2"],
      "interfaces": ["API", "Database", "Message Queue"],
      "scalability": "How this component scales",
      "technology": "Recommended technology",
      "dependencies": ["other_component1", "other_component2"]
    }}
  ],
  "technology_stack": {{
    "frontend": {{
      "framework": "React|Vue.js|Angular|Next.js",
      "rationale": "Why this choice",
      "alternatives": ["alt1", "alt2"]
    }},
    "backend": {{
      "language": "Node.js|Python|Java|Go|C#",
      "framework": "Express|FastAPI|Spring|Gin|ASP.NET",
      "rationale": "Why this choice",
      "alternatives": ["alt1", "alt2"]
    }},
    "database": {{
      "primary": "PostgreSQL|MongoDB|MySQL",
      "cache": "Redis|Memcached",
      "search": "Elasticsearch|OpenSearch",
      "rationale": "Why these choices"
    }},
    "infrastructure": {{
      "cloud_provider": "AWS|Azure|GCP",
      "containerization": "Docker|Kubernetes",
      "ci_cd": "GitHub Actions|GitLab CI|Jenkins",
      "monitoring": "Prometheus|Grafana|Datadog"
    }},
    "messaging": {{
      "message_broker": "RabbitMQ|Apache Kafka|AWS SQS",
      "rationale": "Why this choice"
    }}
  }},
  "alternatives": [
    {{
      "name": "Alternative Architecture Name",
      "description": "Brief description of the alternative",
      "pros": ["advantage1", "advantage2"],
      "cons": ["disadvantage1", "disadvantage2"],
      "use_case": "When to use this alternative",
      "complexity": "low|medium|high",
      "cost": "low|medium|high"
    }}
  ],
  "implementation_plan": {{
    "phases": [
      {{
        "phase": "Phase 1: Foundation",
        "duration": "4-6 weeks",
        "components": ["component1", "component2"],
        "deliverables": ["deliverable1", "deliverable2"],
        "dependencies": ["dependency1"]
      }}
    ],
    "risks": [
      {{
        "risk": "Risk description",
        "impact": "high|medium|low",
        "probability": "high|medium|low",
        "mitigation": "How to mitigate this risk"
      }}
    ],
    "success_metrics": ["metric1", "metric2", "metric3"]
  }},
  "c4_diagram_description": "Detailed description of the C4 Context diagram to be generated"
}}

INSTRUCTIONS:
1. Consider the {domain} domain context in your design
2. Address all non-functional requirements (performance, security, scalability)
3. Provide specific technology recommendations with rationale
4. Include detailed C4 diagram description for Mermaid generation
5. Consider team expertise and organizational constraints
6. Plan for observability, monitoring, and operational concerns
7. Provide clear implementation phases with realistic timelines
8. Identify and mitigate key risks

Output ONLY the JSON, wrapped in ```json code blocks. Be comprehensive and detailed."""

        return prompt

    async def _generate_c4_diagram(self, architecture_data: Dict[str, Any]) -> str:
        """
        Generate Mermaid C4 diagram from architecture data.
        
        Args:
            architecture_data: Architecture data from LLM
            
        Returns:
            Mermaid C4 diagram code
        """
        try:
            # Extract key information for C4 diagram
            components = architecture_data.get("components", [])
            architecture_overview = architecture_data.get("architecture_overview", {})
            tech_stack = architecture_data.get("technology_stack", {})
            
            # Build C4 Context diagram
            c4_diagram = """graph TB
    %% C4 Context Diagram
    subgraph "External Systems"
        User[("👤 Users")]
        ExternalAPI[("🌐 External APIs")]
        PaymentGateway[("💳 Payment Gateway")]
    end
    
    subgraph "E-Commerce Platform"
        WebApp["🖥️ Web Application<br/>Frontend"]
        MobileApp["📱 Mobile App<br/>iOS/Android"]
        APIGateway["🚪 API Gateway<br/>Authentication & Routing"]
        
        subgraph "Core Services"
            UserService["👤 User Service<br/>Authentication & Profiles"]
            ProductService["📦 Product Service<br/>Catalog & Inventory"]
            OrderService["🛒 Order Service<br/>Order Management"]
            PaymentService["💳 Payment Service<br/>Payment Processing"]
            NotificationService["📧 Notification Service<br/>Email & SMS"]
        end
        
        subgraph "Data Layer"
            UserDB[("👤 User Database<br/>PostgreSQL")]
            ProductDB[("📦 Product Database<br/>PostgreSQL")]
            OrderDB[("🛒 Order Database<br/>PostgreSQL")]
            Cache[("⚡ Cache<br/>Redis")]
            Search[("🔍 Search Engine<br/>Elasticsearch")]
        end
        
        subgraph "Infrastructure"
            MessageQueue[("📨 Message Queue<br/>RabbitMQ")]
            Monitoring[("📊 Monitoring<br/>Prometheus + Grafana")]
            Logging[("📝 Logging<br/>ELK Stack")]
        end
    end
    
    %% Connections
    User --> WebApp
    User --> MobileApp
    WebApp --> APIGateway
    MobileApp --> APIGateway
    
    APIGateway --> UserService
    APIGateway --> ProductService
    APIGateway --> OrderService
    APIGateway --> PaymentService
    
    UserService --> UserDB
    ProductService --> ProductDB
    ProductService --> Search
    OrderService --> OrderDB
    PaymentService --> PaymentGateway
    
    UserService --> Cache
    ProductService --> Cache
    OrderService --> Cache
    
    OrderService --> MessageQueue
    PaymentService --> MessageQueue
    MessageQueue --> NotificationService
    
    ExternalAPI --> APIGateway
    
    %% Monitoring connections
    UserService --> Monitoring
    ProductService --> Monitoring
    OrderService --> Monitoring
    PaymentService --> Monitoring
    
    %% Styling
    classDef userClass fill:#e1f5fe
    classDef systemClass fill:#f3e5f5
    classDef serviceClass fill:#e8f5e8
    classDef dataClass fill:#fff3e0
    classDef infraClass fill:#fce4ec
    
    class User,ExternalAPI,PaymentGateway userClass
    class WebApp,MobileApp,APIGateway systemClass
    class UserService,ProductService,OrderService,PaymentService,NotificationService serviceClass
    class UserDB,ProductDB,OrderDB,Cache,Search dataClass
    class MessageQueue,Monitoring,Logging infraClass"""

            # If we have specific components, try to customize the diagram
            if components:
                # This is a simplified version - in a real implementation,
                # you'd parse the components and generate a more accurate diagram
                logger.debug("Customizing C4 diagram based on components")
            
            return c4_diagram
            
        except Exception as e:
            logger.warning(f"Error generating C4 diagram: {str(e)}")
            # Return a basic diagram as fallback
            return """graph TB
    User[("👤 Users")]
    System["🏢 System"]
    Database[("💾 Database")]
    
    User --> System
    System --> Database
    
    classDef userClass fill:#e1f5fe
    classDef systemClass fill:#e8f5e8
    classDef dataClass fill:#fff3e0
    
    class User userClass
    class System systemClass
    class Database dataClass"""

    def _validate_and_enhance_architecture(
        self,
        architecture_data: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate and enhance the architecture data.
        
        Args:
            architecture_data: Raw architecture data from LLM
            requirements: Original requirements for validation
            
        Returns:
            Validated and enhanced architecture data
        """
        try:
            # Ensure required fields exist
            if "architecture_overview" not in architecture_data:
                architecture_data["architecture_overview"] = {}
            
            if "components" not in architecture_data:
                architecture_data["components"] = []
            
            if "technology_stack" not in architecture_data:
                architecture_data["technology_stack"] = {}
            
            if "alternatives" not in architecture_data:
                architecture_data["alternatives"] = []
            
            if "implementation_plan" not in architecture_data:
                architecture_data["implementation_plan"] = {}
            
            # Validate architecture overview
            overview = architecture_data["architecture_overview"]
            if "style" not in overview:
                overview["style"] = "microservices"
            
            if "rationale" not in overview:
                overview["rationale"] = "Architecture designed based on requirements analysis"
            
            # Validate components
            components = architecture_data["components"]
            for component in components:
                if "type" not in component:
                    component["type"] = "service"
                if "responsibilities" not in component:
                    component["responsibilities"] = []
                if "dependencies" not in component:
                    component["dependencies"] = []
            
            # Validate technology stack
            tech_stack = architecture_data["technology_stack"]
            required_tech_categories = ["frontend", "backend", "database", "infrastructure"]
            for category in required_tech_categories:
                if category not in tech_stack:
                    tech_stack[category] = {}
            
            # Validate alternatives
            alternatives = architecture_data["alternatives"]
            for alt in alternatives:
                if "pros" not in alt:
                    alt["pros"] = []
                if "cons" not in alt:
                    alt["cons"] = []
                if "complexity" not in alt:
                    alt["complexity"] = "medium"
                if "cost" not in alt:
                    alt["cost"] = "medium"
            
            # Validate implementation plan
            impl_plan = architecture_data["implementation_plan"]
            if "phases" not in impl_plan:
                impl_plan["phases"] = []
            if "risks" not in impl_plan:
                impl_plan["risks"] = []
            if "success_metrics" not in impl_plan:
                impl_plan["success_metrics"] = []
            
            # Add architecture quality score
            architecture_data["quality_score"] = self._calculate_architecture_quality(
                architecture_data, requirements
            )
            
            return architecture_data
            
        except Exception as e:
            logger.warning(f"Error validating architecture data: {str(e)}")
            return architecture_data

    def _calculate_architecture_quality(
        self,
        architecture_data: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> float:
        """
        Calculate architecture quality score based on requirements coverage.
        
        Args:
            architecture_data: Architecture data
            requirements: Original requirements
            
        Returns:
            Quality score (0.0-1.0)
        """
        try:
            score = 0.5  # Base score
            
            # Check if all major components are addressed
            components = architecture_data.get("components", [])
            if len(components) >= 3:
                score += 0.1
            
            # Check if technology stack is comprehensive
            tech_stack = architecture_data.get("technology_stack", {})
            if len(tech_stack) >= 4:
                score += 0.1
            
            # Check if alternatives are provided
            alternatives = architecture_data.get("alternatives", [])
            if len(alternatives) >= 2:
                score += 0.1
            
            # Check if implementation plan exists
            impl_plan = architecture_data.get("implementation_plan", {})
            if impl_plan.get("phases") and len(impl_plan["phases"]) >= 2:
                score += 0.1
            
            # Check if risks are identified
            if impl_plan.get("risks") and len(impl_plan["risks"]) >= 2:
                score += 0.1
            
            return min(1.0, score)
            
        except Exception as e:
            logger.warning(f"Error calculating architecture quality: {str(e)}")
            return 0.5

    def _summarize_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a summary of requirements for metadata.
        
        Args:
            requirements: Full requirements data
            
        Returns:
            Requirements summary
        """
        try:
            structured_reqs = requirements.get("structured_requirements", {})
            return {
                "business_goals_count": len(structured_reqs.get("business_goals", [])),
                "functional_requirements_count": len(structured_reqs.get("functional_requirements", [])),
                "stakeholders_count": len(structured_reqs.get("stakeholders", [])),
                "constraints_count": len(structured_reqs.get("constraints", [])),
                "confidence_score": requirements.get("confidence_score", 0.0)
            }
        except Exception as e:
            logger.warning(f"Error summarizing requirements: {str(e)}")
            return {}

    def _generate_design_notes(
        self,
        architecture_data: Dict[str, Any],
        requirements: Dict[str, Any]
    ) -> List[str]:
        """
        Generate design notes for the architecture.
        
        Args:
            architecture_data: Architecture data
            requirements: Original requirements
            
        Returns:
            List of design notes
        """
        notes = []
        
        try:
            # Architecture style note
            style = architecture_data.get("architecture_overview", {}).get("style", "unknown")
            notes.append(f"Architecture style: {style}")
            
            # Component count note
            components_count = len(architecture_data.get("components", []))
            if components_count > 10:
                notes.append("Complex architecture with many components")
            elif components_count < 3:
                notes.append("Simple architecture with few components")
            
            # Technology stack note
            tech_stack = architecture_data.get("technology_stack", {})
            if len(tech_stack) >= 5:
                notes.append("Comprehensive technology stack selected")
            
            # Alternatives note
            alternatives_count = len(architecture_data.get("alternatives", []))
            if alternatives_count >= 3:
                notes.append("Multiple architectural alternatives considered")
            
            # Quality score note
            quality_score = architecture_data.get("quality_score", 0.5)
            if quality_score > 0.8:
                notes.append("High-quality architecture design")
            elif quality_score < 0.6:
                notes.append("Architecture may need refinement")
            
        except Exception as e:
            logger.warning(f"Error generating design notes: {str(e)}")
            notes.append("Error generating design notes")
        
        return notes

    def get_architecture_patterns(self) -> List[str]:
        """
        Get list of supported architecture patterns.
        
        Returns:
            List of architecture patterns
        """
        return self.architecture_patterns.copy()

    def get_technology_categories(self) -> Dict[str, List[str]]:
        """
        Get technology categories and options.
        
        Returns:
            Dictionary of technology categories and options
        """
        return self.tech_categories.copy()

    def get_agent_capabilities(self) -> Dict[str, Any]:
        """
        Get agent capabilities and metadata.
        
        Returns:
            Dictionary with agent capabilities
        """
        return {
            "agent_type": self.agent_type,
            "agent_version": self.agent_version,
            "capabilities": [
                "System architecture design",
                "Technology stack recommendations",
                "C4 diagram generation",
                "Alternative analysis",
                "Implementation planning",
                "Risk assessment",
                "Quality scoring"
            ],
            "architecture_patterns": self.get_architecture_patterns(),
            "technology_categories": list(self.tech_categories.keys()),
            "output_format": "Structured JSON with architecture specifications and C4 diagrams"
        }
