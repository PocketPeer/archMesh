"""
Integration tests for ArchMesh modules
"""

import pytest
from app.modules.requirements import InputParser, RequirementsExtractor, RequirementsValidator
from app.modules.architecture import ArchitectureGenerator, DiagramRenderer, RecommendationEngine


class TestArchMeshIntegration:
    """Integration tests for ArchMesh modules working together"""
    
    def test_requirements_to_architecture_pipeline(self):
        """Test complete pipeline from requirements to architecture"""
        # Step 1: Parse requirements
        parser = InputParser()
        extractor = RequirementsExtractor()
        validator = RequirementsValidator()
        
        input_text = """
        We need a modern e-commerce platform for our business.
        Users should be able to browse products, add items to cart, and checkout.
        The system must be secure, handle 10,000 concurrent users, and respond within 1 second.
        We have a budget of $500,000 and need it completed in 12 months.
        Our customers, administrators, and support staff will use this system.
        """
        
        # Parse and extract requirements
        parsed = parser.parse(input_text)
        requirements = extractor.extract(parsed)
        validation = validator.validate(requirements)
        
        assert validation.status.value in ["valid", "warning"]
        assert len(requirements.functional_requirements) > 0
        assert len(requirements.stakeholders) > 0
        
        # Step 2: Generate architecture
        generator = ArchitectureGenerator()
        architecture = generator.generate(requirements)
        
        assert architecture.name is not None
        assert len(architecture.components) > 0
        assert architecture.quality_score > 0.0
        
        # Step 3: Render diagrams
        renderer = DiagramRenderer()
        diagrams = renderer.render(architecture)
        
        assert len(diagrams) >= 2  # Context and container diagrams
        assert any(diag.type.value == "c4_context" for diag in diagrams)
        assert any(diag.type.value == "c4_container" for diag in diagrams)
        
        # Step 4: Generate recommendations
        engine = RecommendationEngine()
        recommendations = engine.generate(architecture)
        
        assert len(recommendations) > 0
        assert any(rec.priority.value == "high" for rec in recommendations)
        
        print(f"✅ Complete pipeline successful!")
        print(f"   Requirements: {len(requirements.functional_requirements)} functional")
        print(f"   Architecture: {architecture.name} with {len(architecture.components)} components")
        print(f"   Diagrams: {len(diagrams)} diagrams generated")
        print(f"   Recommendations: {len(recommendations)} recommendations")
    
    def test_simple_architecture_generation(self):
        """Test simple architecture generation"""
        # Simple requirements
        from app.modules.requirements.models import ExtractedRequirements, ExtractedRequirement, RequirementType
        
        requirements = ExtractedRequirements(
            functional_requirements=[
                ExtractedRequirement(
                    id="func_1",
                    type=RequirementType.FUNCTIONAL,
                    title="User Authentication",
                    description="Users should be able to login and logout",
                    priority="high",
                    confidence=0.9
                )
            ],
            non_functional_requirements=[
                ExtractedRequirement(
                    id="non_func_1",
                    type=RequirementType.NON_FUNCTIONAL,
                    title="Security",
                    description="System must be secure",
                    priority="high",
                    confidence=0.8
                )
            ],
            constraints=[
                ExtractedRequirement(
                    id="const_1",
                    type=RequirementType.CONSTRAINT,
                    title="Budget",
                    description="Budget is $50,000",
                    priority="medium",
                    confidence=0.7
                )
            ]
        )
        
        # Generate architecture
        generator = ArchitectureGenerator()
        architecture = generator.generate(requirements)
        
        # Should have basic components
        component_types = [comp.type.value for comp in architecture.components]
        assert "frontend" in component_types or "service" in component_types
        assert "database" in component_types
        
        # Should have technology stack
        assert len(architecture.technology_stack.frontend) > 0
        assert len(architecture.technology_stack.backend) > 0
        assert len(architecture.technology_stack.database) > 0
        
        # Should have reasonable quality score
        assert architecture.quality_score > 0.5
    
    def test_architecture_style_selection(self):
        """Test that architecture style is selected appropriately"""
        from app.modules.requirements.models import ExtractedRequirements, ExtractedRequirement, RequirementType
        
        # Test microservices selection
        microservices_requirements = ExtractedRequirements(
            functional_requirements=[
                ExtractedRequirement(id="f1", type=RequirementType.FUNCTIONAL, title="User Service", description="User management", priority="high", confidence=0.8),
                ExtractedRequirement(id="f2", type=RequirementType.FUNCTIONAL, title="Order Service", description="Order processing", priority="high", confidence=0.8),
                ExtractedRequirement(id="f3", type=RequirementType.FUNCTIONAL, title="Payment Service", description="Payment processing", priority="high", confidence=0.8),
                ExtractedRequirement(id="f4", type=RequirementType.FUNCTIONAL, title="Inventory Service", description="Inventory management", priority="high", confidence=0.8),
                ExtractedRequirement(id="f5", type=RequirementType.FUNCTIONAL, title="Notification Service", description="Notifications", priority="high", confidence=0.8),
                ExtractedRequirement(id="f6", type=RequirementType.FUNCTIONAL, title="Analytics Service", description="Analytics", priority="high", confidence=0.8)
            ],
            non_functional_requirements=[
                ExtractedRequirement(id="nf1", type=RequirementType.NON_FUNCTIONAL, title="Scalability", description="Handle 10000 concurrent users", priority="high", confidence=0.9)
            ]
        )
        
        generator = ArchitectureGenerator()
        architecture = generator.generate(microservices_requirements)
        
        # Should select microservices for complex system
        assert architecture.style.value == "microservices"
        
        # Should have API gateway for microservices
        component_types = [comp.type.value for comp in architecture.components]
        assert "api_gateway" in component_types
    
    def test_recommendation_prioritization(self):
        """Test that recommendations are properly prioritized"""
        from app.modules.architecture.models import Architecture, ArchitectureComponent, TechnologyStack
        
        # Create architecture without security measures
        architecture = Architecture(
            id="test_arch",
            name="Test Architecture",
            style="microservices",
            description="Test architecture",
            components=[
                ArchitectureComponent(
                    id="comp1",
                    name="Frontend",
                    type="frontend",
                    description="Frontend application",
                    technologies=["React"],
                    responsibilities=["UI"]
                )
            ],
            technology_stack=TechnologyStack(),
            quality_score=0.6  # Lower quality to trigger recommendations
        )
        
        engine = RecommendationEngine()
        recommendations = engine.generate(architecture)
        
        # Should have high priority recommendations
        high_priority = [rec for rec in recommendations if rec.priority.value == "high"]
        assert len(high_priority) > 0
        
        # Should include security recommendation
        security_recs = [rec for rec in recommendations if "security" in rec.title.lower()]
        assert len(security_recs) > 0
        
        # Should include monitoring recommendation
        monitoring_recs = [rec for rec in recommendations if "monitoring" in rec.title.lower()]
        assert len(monitoring_recs) > 0
