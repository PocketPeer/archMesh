"""
Architecture Agent for ArchMesh PoC.

This agent is responsible for designing system architectures based on requirements,
generating C4 diagrams, recommending technology stacks, and providing alternatives.
Supports both greenfield and brownfield architecture design with RAG context.
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
    - Support brownfield architecture design with RAG context
    - Generate integration strategies for existing systems
    """

    def __init__(self, knowledge_base_service: Optional[Any] = None):
        """
        Initialize the Architecture Agent.
        
        Uses Claude Opus for best-in-class architecture design capabilities
        with lower temperature for more consistent architectural decisions.
        
        Args:
            knowledge_base_service: Optional KnowledgeBaseService for brownfield context
        """
        from app.config import settings
        
        # Get task-specific LLM configuration
        provider, model = settings.get_llm_config_for_task("architecture")
        
        super().__init__(
            agent_type="architecture_designer",
            agent_version="1.1.0",
            llm_provider=provider,
            llm_model=model,
            temperature=0.5,  # Lower for more consistent architectural decisions
            max_retries=3,
            timeout_seconds=180,  # Longer timeout for complex architectural analysis
            max_tokens=6000  # More tokens for detailed architecture descriptions
        )
        
        # Knowledge base service for brownfield context
        self.kb_service = knowledge_base_service
        
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
                - mode: "greenfield" or "brownfield" (default: "greenfield")
                - project_id: UUID for brownfield mode
                - existing_architecture: Optional existing architecture data
                
        Returns:
            Dictionary containing:
                - architecture_overview: High-level architecture description
                - c4_diagram_context: Mermaid C4 diagram code
                - components: Detailed component specifications
                - technology_stack: Recommended technology stack
                - alternatives: Alternative architectural approaches
                - implementation_plan: Phased implementation guidance
                - integration_strategy: For brownfield mode
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
            mode = input_data.get("mode", "greenfield")
            project_id = input_data.get("project_id")
            existing_architecture = input_data.get("existing_architecture")
            
            logger.info(
                f"Starting architecture design",
                extra={
                    "agent_type": self.agent_type,
                    "domain": domain,
                    "mode": mode,
                    "session_id": session_id,
                }
            )
            
            # Route to appropriate execution method
            if mode == "brownfield":
                if not project_id:
                    raise ValueError("project_id is required for brownfield mode")
                return await self._execute_brownfield(input_data)
            else:
                return await self._execute_greenfield(input_data)
            
        except Exception as e:
            logger.error(
                f"Architecture design failed: {str(e)}",
                extra={
                    "agent_type": self.agent_type,
                    "domain": input_data.get("domain"),
                    "mode": input_data.get("mode"),
                    "error": str(e),
                }
            )
            raise

    async def _execute_greenfield(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute greenfield architecture design.
        
        Args:
            input_data: Input data containing requirements and constraints
            
        Returns:
            Architecture design data
        """
        requirements = input_data["requirements"]
        constraints = input_data.get("constraints", {})
        preferences = input_data.get("preferences", [])
        domain = input_data.get("domain", "cloud-native")
        session_id = input_data.get("session_id")
        
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
            "mode": "greenfield",
            "architecture_timestamp": self.start_time.isoformat() if self.start_time else None,
            "agent_version": self.agent_version,
            "requirements_summary": self._summarize_requirements(requirements),
            "design_notes": self._generate_design_notes(enhanced_data, requirements)
        }
        
        logger.info(
            f"Greenfield architecture design completed successfully",
            extra={
                "agent_type": self.agent_type,
                "domain": domain,
                "architecture_style": enhanced_data.get("architecture_overview", {}).get("style", "unknown"),
                "components_count": len(enhanced_data.get("components", [])),
                "alternatives_count": len(enhanced_data.get("alternatives", [])),
            }
        )
        
        return enhanced_data

    async def _execute_brownfield(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute brownfield architecture design with RAG context.
        
        Args:
            input_data: Input data containing requirements, project_id, and existing architecture
            
        Returns:
            Architecture design data with integration strategy
        """
        project_id = input_data["project_id"]
        requirements = input_data["requirements"]
        constraints = input_data.get("constraints", {})
        preferences = input_data.get("preferences", [])
        domain = input_data.get("domain", "cloud-native")
        session_id = input_data.get("session_id")
        existing_architecture = input_data.get("existing_architecture")
        
        # 1. Get existing architecture context from knowledge base
        context = await self._get_brownfield_context(project_id, requirements, existing_architecture)
        
        # 2. Build enhanced prompt with context
        prompt = self._build_brownfield_prompt(requirements, constraints, preferences, domain, context)
        
        # 3. Call LLM with brownfield system prompt
        messages = [
            {"role": "system", "content": self.get_brownfield_system_prompt()},
            {"role": "user", "content": prompt}
        ]
        
        response = await self._call_llm(messages)
        
        # 4. Parse and validate response
        architecture_data = self._parse_json_response(response)
        
        # 5. Generate C4 diagram with existing architecture
        c4_diagram = await self._generate_brownfield_c4_diagram(architecture_data, context)
        architecture_data["c4_diagram_context"] = c4_diagram
        
        # 6. Generate integration strategy
        integration_strategy = await self._generate_integration_strategy(
            context.get("existing_services", []),
            architecture_data
        )
        architecture_data["integration_strategy"] = integration_strategy
        
        # 7. Validate and enhance the architecture data
        enhanced_data = self._validate_and_enhance_architecture(architecture_data, requirements)
        
        # 8. Add brownfield-specific metadata
        enhanced_data["metadata"] = {
            "domain": domain,
            "mode": "brownfield",
            "project_id": project_id,
            "architecture_timestamp": self.start_time.isoformat() if self.start_time else None,
            "agent_version": self.agent_version,
            "requirements_summary": self._summarize_requirements(requirements),
            "design_notes": self._generate_design_notes(enhanced_data, requirements),
            "existing_services_count": len(context.get("existing_services", [])),
            "similar_features_found": len(context.get("similar_features", [])),
            "context_quality": self._assess_context_quality(context)
        }
        
        logger.info(
            f"Brownfield architecture design completed successfully",
            extra={
                "agent_type": self.agent_type,
                "domain": domain,
                "project_id": project_id,
                "architecture_style": enhanced_data.get("architecture_overview", {}).get("style", "unknown"),
                "components_count": len(enhanced_data.get("components", [])),
                "existing_services_count": len(context.get("existing_services", [])),
                "integration_phases": len(integration_strategy.get("phases", [])),
            }
        )
        
        return enhanced_data

    async def _get_brownfield_context(
        self,
        project_id: str,
        requirements: Dict[str, Any],
        existing_architecture: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get relevant context from knowledge base for brownfield design.
        
        Args:
            project_id: Project UUID
            requirements: New requirements
            existing_architecture: Optional existing architecture data
            
        Returns:
            Context dictionary with existing services and similar features
        """
        context = {
            "existing_services": [],
            "similar_features": [],
            "existing_patterns": [],
            "technology_stack": {},
            "integration_points": []
        }
        
        if not self.kb_service:
            logger.warning("Knowledge base service not available, using limited context")
            if existing_architecture:
                context["existing_services"] = existing_architecture.get("services", [])
                context["technology_stack"] = existing_architecture.get("technology_stack", {})
            return context
        
        try:
            # Query for similar features
            functional_reqs = requirements.get("structured_requirements", {}).get("functional_requirements", [])
            feature_desc = " ".join(functional_reqs[:5])  # Use first 5 requirements
            
            if feature_desc.strip():
                similar = await self.kb_service.search_similar_architectures(
                    query=feature_desc,
                    project_id=project_id,
                    top_k=5
                )
                context["similar_features"] = similar
            
            # Get existing services and dependencies
            services = await self.kb_service.get_service_dependencies(project_id)
            context["existing_services"] = services
            
            # Extract technology patterns from existing services
            tech_stack = {}
            for service in services:
                if "technology" in service:
                    tech = service["technology"]
                    if tech not in tech_stack:
                        tech_stack[tech] = 0
                    tech_stack[tech] += 1
            
            context["technology_stack"] = tech_stack
            
            # Get context for new feature integration
            if functional_reqs:
                feature_context = await self.kb_service.get_context_for_new_feature(
                    project_id=project_id,
                    feature_description=feature_desc
                )
                context["integration_points"] = feature_context.get("integration_points", [])
                context["existing_patterns"] = feature_context.get("patterns", [])
            
            logger.info(
                f"Retrieved brownfield context",
                extra={
                    "project_id": project_id,
                    "existing_services_count": len(context["existing_services"]),
                    "similar_features_count": len(context["similar_features"]),
                    "technology_stack_size": len(context["technology_stack"]),
                }
            )
            
        except Exception as e:
            logger.warning(f"Error retrieving brownfield context: {str(e)}")
            # Fallback to existing architecture if available
            if existing_architecture:
                context["existing_services"] = existing_architecture.get("services", [])
                context["technology_stack"] = existing_architecture.get("technology_stack", {})
        
        return context

    def get_brownfield_system_prompt(self) -> str:
        """
        Return the system prompt for brownfield architecture design.
        
        Returns:
            System prompt string for brownfield architecture design
        """
        return """You are a senior enterprise architect specializing in brownfield integrations.

Your responsibilities:
1. Analyze existing architecture and technology stack
2. Design new features that integrate seamlessly with existing systems
3. Reuse existing patterns and technologies where appropriate
4. Minimize disruption to current services
5. Identify which existing services need modifications
6. Propose migration strategies if needed
7. Consider backwards compatibility
8. Assess impact on current system

Key principles:
- **Consistency**: Use technologies already in the stack
- **Minimal Impact**: Avoid changes to stable services
- **Incremental**: Support phased rollout
- **Compatibility**: Ensure existing clients still work
- **Patterns**: Follow existing architectural patterns
- **Reuse**: Leverage existing services and components
- **Integration**: Design clear integration points

Output structured JSON with:
- Proposed architecture for new feature
- Integration points with existing services
- Required modifications to current services
- Migration strategy with phases
- Risk assessment and mitigation
- Rollback plan
- Technology stack recommendations (prefer existing)
- Implementation timeline

Focus on practical integration strategies and minimal disruption to existing systems."""

    def _build_brownfield_prompt(
        self,
        requirements: Dict[str, Any],
        constraints: Dict[str, Any],
        preferences: List[str],
        domain: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Build brownfield architecture design prompt with existing context.
        
        Args:
            requirements: New requirements
            constraints: Organizational constraints
            preferences: Architecture preferences
            domain: Project domain
            context: Existing architecture context
            
        Returns:
            Formatted prompt string for brownfield design
        """
        # Extract key information from requirements
        business_goals = requirements.get("structured_requirements", {}).get("business_goals", [])
        functional_reqs = requirements.get("structured_requirements", {}).get("functional_requirements", [])
        non_functional_reqs = requirements.get("structured_requirements", {}).get("non_functional_requirements", {})
        constraints_list = requirements.get("structured_requirements", {}).get("constraints", [])
        stakeholders = requirements.get("structured_requirements", {}).get("stakeholders", [])
        
        # Extract existing architecture information
        existing_services = context.get("existing_services", [])
        similar_features = context.get("similar_features", [])
        tech_stack = context.get("technology_stack", {})
        integration_points = context.get("integration_points", [])
        
        # Build prompt in parts to avoid f-string issues with JSON
        prompt_parts = [
            "Design architecture for new feature in EXISTING system.",
            "",
            f"PROJECT DOMAIN: {domain}",
            "",
            "NEW REQUIREMENTS:",
            "Business Goals:",
            *[f"- {goal}" for goal in business_goals[:5]],
            "",
            "Functional Requirements:",
            *[f"- {req}" for req in functional_reqs[:10]],
            "",
            "Non-Functional Requirements:"
        ]
        
        for category, reqs in non_functional_reqs.items():
            if reqs:
                prompt_parts.append(f"\n{category.upper()}:")
                for req in reqs[:3]:
                    prompt_parts.append(f"- {req}")
        
        prompt_parts.extend([
            "",
            "Constraints:",
            *[f"- {constraint}" for constraint in constraints_list[:5]],
            "",
            "Stakeholders:",
            *[f"- {stakeholder.get('name', 'Unknown')} ({stakeholder.get('role', 'Unknown')}): {', '.join(stakeholder.get('concerns', []))}" for stakeholder in stakeholders[:5]],
            "",
            "EXISTING ARCHITECTURE CONTEXT:",
            f"Existing Services ({len(existing_services)}):",
            *[f"- {service.get('name', 'Unknown')} ({service.get('type', 'service')}): {service.get('description', 'No description')} - Tech: {service.get('technology', 'Unknown')}" for service in existing_services[:10]],
            "",
            "Current Technology Stack:",
            *[f"- {tech}: {count} services" for tech, count in list(tech_stack.items())[:10]],
            "",
            f"Similar Features Found ({len(similar_features)}):",
            *[f"- {feature.get('description', 'No description')} (Score: {feature.get('score', 0):.2f})" for feature in similar_features[:5]],
            "",
            "Integration Points:",
            *([f"- {point}" for point in integration_points[:5]] if integration_points else ["None identified"]),
            "",
            "ADDITIONAL CONSTRAINTS:",
            *([f"- {key}: {value}" for key, value in constraints.items()] if constraints else ["None specified"]),
            "",
            "ARCHITECTURE PREFERENCES:",
            *([f"- {pref}" for pref in preferences] if preferences else ["No specific preferences"]),
            "",
            "Design the new feature to:",
            "1. Integrate with existing services listed above",
            f"2. Use similar technologies as existing services (prefer: {', '.join(list(tech_stack.keys())[:3])})",
            "3. Follow existing architectural patterns",
            "4. Minimize changes to current services",
            "5. Provide clear integration strategy",
            "6. Ensure backwards compatibility",
            "7. Support incremental deployment",
            "",
            "Output JSON with the following structure:",
            "- architecture_overview: style, rationale, integration_approach, key_principles",
            "- new_services: list of new services with technology and dependencies",
            "- modified_services: existing services that need changes",
            "- integration_points: connections between services",
            "- technology_stack: preferred technologies (use existing where possible)",
            "- migration_strategy: phased deployment plan with rollback",
            "- impact_analysis: risk assessment and affected services",
            "- alternatives: alternative approaches with trade-offs",
            "- implementation_plan: phases, risks, and success metrics",
            "- c4_diagram_description: description for C4 diagram generation",
            "",
            "INSTRUCTIONS:",
            "1. Prioritize existing technologies and patterns",
            "2. Minimize changes to existing services",
            "3. Design for incremental deployment",
            "4. Ensure backwards compatibility",
            "5. Provide detailed integration strategy",
            "6. Include comprehensive rollback plan",
            "7. Address all non-functional requirements",
            "8. Consider operational impact",
            "",
            "Output ONLY the JSON, wrapped in code blocks. Be comprehensive and detailed."
        ])
        
        prompt = "\n".join(prompt_parts)

        return prompt

    async def _generate_integration_strategy(
        self,
        existing_services: List[Dict[str, Any]],
        proposed_architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate detailed integration strategy for brownfield deployment.
        
        Args:
            existing_services: List of existing services
            proposed_architecture: Proposed architecture data
            
        Returns:
            Integration strategy with phases and rollback plans
        """
        try:
            # Extract new services and modified services
            new_services = proposed_architecture.get("new_services", [])
            modified_services = proposed_architecture.get("modified_services", [])
            
            # Build integration strategy
            strategy = {
                "phases": [],
                "testing_strategy": [],
                "monitoring": [],
                "rollback_plan": "Comprehensive rollback procedure",
                "risk_assessment": {
                    "high_risk_services": [],
                    "critical_dependencies": [],
                    "breaking_changes": False
                }
            }
            
            # Phase 1: Deploy new services
            if new_services:
                strategy["phases"].append({
                    "phase": 1,
                    "name": "Deploy New Services",
                    "description": "Deploy new services without affecting existing functionality",
                    "duration": "2-3 weeks",
                    "services": [service["name"] for service in new_services],
                    "steps": [
                        "Deploy new services in parallel environment",
                        "Configure service discovery and routing",
                        "Set up monitoring and logging",
                        "Perform integration testing",
                        "Deploy to staging environment",
                        "Conduct user acceptance testing"
                    ],
                    "rollback": "Remove new services and revert routing changes",
                    "testing": [
                        "Unit tests for new services",
                        "Integration tests with existing services",
                        "Load testing for new endpoints",
                        "Security testing for new APIs"
                    ],
                    "success_criteria": [
                        "All new services deployed successfully",
                        "No impact on existing services",
                        "All tests passing",
                        "Performance metrics within acceptable range"
                    ]
                })
            
            # Phase 2: Update existing services
            if modified_services:
                strategy["phases"].append({
                    "phase": 2,
                    "name": "Update Existing Services",
                    "description": "Update existing services to integrate with new functionality",
                    "duration": "1-2 weeks",
                    "services": [service["name"] for service in modified_services],
                    "steps": [
                        "Update service configurations",
                        "Deploy new endpoints",
                        "Update service dependencies",
                        "Perform regression testing",
                        "Deploy to production with feature flags",
                        "Monitor system performance"
                    ],
                    "rollback": "Revert to previous service versions",
                    "testing": [
                        "Regression tests for existing functionality",
                        "Integration tests for new features",
                        "Performance testing",
                        "Compatibility testing"
                    ],
                    "success_criteria": [
                        "Existing functionality unchanged",
                        "New features working correctly",
                        "No performance degradation",
                        "All monitoring alerts green"
                    ]
                })
            
            # Phase 3: Full integration and optimization
            strategy["phases"].append({
                "phase": 3,
                "name": "Full Integration and Optimization",
                "description": "Complete integration and optimize system performance",
                "duration": "1 week",
                "services": "All services",
                "steps": [
                    "Enable all feature flags",
                    "Optimize system performance",
                    "Fine-tune monitoring and alerting",
                    "Complete documentation updates",
                    "Conduct final system testing",
                    "Deploy to all environments"
                ],
                "rollback": "Disable feature flags and revert optimizations",
                "testing": [
                    "End-to-end system testing",
                    "Performance optimization validation",
                    "Security audit",
                    "Disaster recovery testing"
                ],
                "success_criteria": [
                    "All features working in production",
                    "Performance targets met",
                    "Security requirements satisfied",
                    "Documentation complete"
                ]
            })
            
            # Testing strategy
            strategy["testing_strategy"] = [
                "Unit testing for all new and modified components",
                "Integration testing between new and existing services",
                "End-to-end testing of complete user workflows",
                "Performance testing under expected load",
                "Security testing for new endpoints and data flows",
                "Compatibility testing with existing clients",
                "Disaster recovery and failover testing",
                "User acceptance testing with stakeholders"
            ]
            
            # Monitoring strategy
            strategy["monitoring"] = [
                "Set up alerts for new services and endpoints",
                "Monitor integration points between services",
                "Track performance metrics for new features",
                "Monitor error rates and response times",
                "Set up dashboards for system health",
                "Configure log aggregation and analysis",
                "Implement distributed tracing",
                "Set up automated health checks"
            ]
            
            # Risk assessment
            strategy["risk_assessment"] = {
                "high_risk_services": [
                    service["name"] for service in modified_services 
                    if service.get("breaking_changes", False)
                ],
                "critical_dependencies": [
                    dep for service in new_services + modified_services
                    for dep in service.get("dependencies", [])
                    if dep in [s["name"] for s in existing_services]
                ],
                "breaking_changes": any(
                    service.get("breaking_changes", False) 
                    for service in modified_services
                ),
                "data_migration_required": any(
                    service.get("migration_required", False) 
                    for service in modified_services
                ),
                "downtime_required": False,  # Assume zero-downtime deployment
                "rollback_complexity": "medium" if modified_services else "low"
            }
            
            return strategy
            
        except Exception as e:
            logger.warning(f"Error generating integration strategy: {str(e)}")
            # Return basic strategy as fallback
            return {
                "phases": [
                    {
                        "phase": 1,
                        "name": "Deploy New Services",
                        "description": "Deploy new services",
                        "duration": "2-3 weeks",
                        "steps": ["Deploy and test new services"],
                        "rollback": "Remove new services"
                    }
                ],
                "testing_strategy": ["Integration testing", "Performance testing"],
                "monitoring": ["Set up monitoring for new services"],
                "rollback_plan": "Remove new services and revert changes"
            }

    async def _generate_brownfield_c4_diagram(
        self, 
        architecture_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """
        Generate C4 diagram for brownfield architecture showing integration.
        
        Args:
            architecture_data: Proposed architecture data
            context: Existing architecture context
            
        Returns:
            Mermaid C4 diagram code
        """
        try:
            existing_services = context.get("existing_services", [])
            new_services = architecture_data.get("new_services", [])
            modified_services = architecture_data.get("modified_services", [])
            
            # Build C4 diagram showing existing and new services
            c4_diagram = """graph TB
    %% C4 Context Diagram - Brownfield Integration
    subgraph "External Systems"
        User[("👤 Users")]
        ExternalAPI[("🌐 External APIs")]
    end
    
    subgraph "Existing System"
        ExistingService1["🏢 Existing Service 1<br/>Current Functionality"]
        ExistingService2["🏢 Existing Service 2<br/>Current Functionality"]
        ExistingDB[("💾 Existing Database<br/>Current Data")]
    end
    
    subgraph "New Features"
        NewService1["🆕 New Service 1<br/>New Functionality"]
        NewService2["🆕 New Service 2<br/>New Functionality"]
        NewDB[("💾 New Database<br/>New Data")]
    end
    
    subgraph "Modified Services"
        ModifiedService["🔄 Modified Service<br/>Enhanced Functionality"]
    end
    
    subgraph "Infrastructure"
        MessageQueue[("📨 Message Queue<br/>RabbitMQ")]
        Cache[("⚡ Cache<br/>Redis")]
        Monitoring[("📊 Monitoring<br/>Prometheus + Grafana")]
    end
    
    %% User connections
    User --> ExistingService1
    User --> NewService1
    
    %% Existing system connections
    ExistingService1 --> ExistingDB
    ExistingService2 --> ExistingDB
    
    %% New system connections
    NewService1 --> NewDB
    NewService2 --> NewDB
    
    %% Integration connections
    ExistingService1 --> NewService1
    ModifiedService --> ExistingService1
    ModifiedService --> NewService1
    
    %% Infrastructure connections
    NewService1 --> MessageQueue
    NewService2 --> MessageQueue
    ModifiedService --> MessageQueue
    
    NewService1 --> Cache
    ModifiedService --> Cache
    
    %% Monitoring
    ExistingService1 --> Monitoring
    NewService1 --> Monitoring
    ModifiedService --> Monitoring
    
    %% Styling
    classDef existingClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef newClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef modifiedClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef infraClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef dataClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    
    class ExistingService1,ExistingService2 existingClass
    class NewService1,NewService2 newClass
    class ModifiedService modifiedClass
    class MessageQueue,Cache,Monitoring infraClass
    class ExistingDB,NewDB dataClass"""

            # Customize based on actual services if available
            if existing_services or new_services:
                logger.debug("Customizing brownfield C4 diagram based on actual services")
                # In a real implementation, you'd parse the services and generate
                # a more accurate diagram based on the actual architecture
            
            return c4_diagram
            
        except Exception as e:
            logger.warning(f"Error generating brownfield C4 diagram: {str(e)}")
            # Return basic diagram as fallback
            return """graph TB
    Existing["🏢 Existing System"]
    New["🆕 New Features"]
    Integration["🔄 Integration Layer"]
    
    Existing --> Integration
    Integration --> New
    
    classDef existingClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef newClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef integrationClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    
    class Existing existingClass
    class New newClass
    class Integration integrationClass"""

    def _assess_context_quality(self, context: Dict[str, Any]) -> str:
        """
        Assess the quality of brownfield context.
        
        Args:
            context: Context data from knowledge base
            
        Returns:
            Quality assessment string
        """
        try:
            existing_services_count = len(context.get("existing_services", []))
            similar_features_count = len(context.get("similar_features", []))
            tech_stack_size = len(context.get("technology_stack", {}))
            
            if existing_services_count >= 5 and similar_features_count >= 3 and tech_stack_size >= 3:
                return "high"
            elif existing_services_count >= 3 and similar_features_count >= 1 and tech_stack_size >= 2:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.warning(f"Error assessing context quality: {str(e)}")
            return "unknown"

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

Output ONLY the JSON, wrapped in code blocks. Be comprehensive and detailed."""

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
                "Quality scoring",
                "Brownfield architecture design",
                "RAG-based context integration",
                "Integration strategy generation",
                "Migration planning",
                "Rollback strategy design"
            ],
            "architecture_patterns": self.get_architecture_patterns(),
            "technology_categories": list(self.tech_categories.keys()),
            "modes": ["greenfield", "brownfield"],
            "output_format": "Structured JSON with architecture specifications, C4 diagrams, and integration strategies",
            "knowledge_base_integration": self.kb_service is not None
        }
