"""
Simple tests for Architecture Module
"""

import pytest
from app.modules.architecture import ArchitectureGenerator, DiagramRenderer, RecommendationEngine
from app.modules.requirements import InputParser, RequirementsExtractor
from app.modules.architecture.models import ArchitectureStyle, ComponentType


class TestArchitectureModule:
    """Simple tests for Architecture Module components"""
    
    def test_architecture_generator_simple(self):
        """Test ArchitectureGenerator with simple requirements"""
        # Create simple requirements
        from app.modules.requirements.models import ExtractedRequirements, ExtractedRequirement, RequirementType
        
        requirements = ExtractedRequirements(
            functional_requirements=[
                ExtractedRequirement(
                    id="func_1",
                    type=RequirementType.FUNCTIONAL,
                    title="User Management",
                    description="Users should be able to create accounts",
                    priority="high",
                    confidence=0.8
                )
            ],
            non_functional_requirements=[
                ExtractedRequirement(
                    id="non_func_1",
                    type=RequirementType.NON_FUNCTIONAL,
                    title="Performance",
                    description="System must be fast and handle 1000 concurrent users",
                    priority="high",
                    confidence=0.9
                )
            ]
        )
        
        generator = ArchitectureGenerator()
        architecture = generator.generate(requirements)
        
        assert architecture.name is not None
        assert architecture.style in ArchitectureStyle
        assert len(architecture.components) > 0
        assert architecture.quality_score > 0.0
        assert len(architecture.technology_stack.frontend) > 0
        assert len(architecture.technology_stack.backend) > 0
        assert len(architecture.technology_stack.database) > 0
    
    def test_diagram_renderer_simple(self):
        """Test DiagramRenderer with simple architecture"""
        from app.modules.architecture.models import Architecture, ArchitectureComponent, TechnologyStack
        
        # Create simple architecture
        architecture = Architecture(
            id="test_arch",
            name="Test Architecture",
            style=ArchitectureStyle.MICROSERVICES,
            description="Test architecture",
            components=[
                ArchitectureComponent(
                    id="comp1",
                    name="Frontend",
                    type=ComponentType.FRONTEND,
                    description="Frontend application",
                    technologies=["React"],
                    responsibilities=["UI"]
                ),
                ArchitectureComponent(
                    id="comp2",
                    name="API",
                    type=ComponentType.SERVICE,
                    description="API service",
                    technologies=["Node.js"],
                    responsibilities=["API"]
                )
            ],
            technology_stack=TechnologyStack(
                frontend=["React"],
                backend=["Node.js"],
                database=["PostgreSQL"]
            )
        )
        
        renderer = DiagramRenderer()
        diagrams = renderer.render(architecture)
        
        assert len(diagrams) >= 2  # At least context and container diagrams
        assert any(diag.type.value == "c4_context" for diag in diagrams)
        assert any(diag.type.value == "c4_container" for diag in diagrams)
        
        # Check diagram content
        for diagram in diagrams:
            assert diagram.title is not None
            assert diagram.description is not None
            assert "@startuml" in diagram.content
            assert "@enduml" in diagram.content
    
    def test_recommendation_engine_simple(self):
        """Test RecommendationEngine with simple architecture"""
        from app.modules.architecture.models import Architecture, ArchitectureComponent, TechnologyStack
        
        # Create simple architecture
        architecture = Architecture(
            id="test_arch",
            name="Test Architecture",
            style=ArchitectureStyle.MICROSERVICES,
            description="Test architecture",
            components=[
                ArchitectureComponent(
                    id="comp1",
                    name="Frontend",
                    type=ComponentType.FRONTEND,
                    description="Frontend application",
                    technologies=["React"],
                    responsibilities=["UI"]
                )
            ],
            technology_stack=TechnologyStack()
        )
        
        engine = RecommendationEngine()
        recommendations = engine.generate(architecture)
        
        assert len(recommendations) > 0
        for rec in recommendations:
            assert rec.title is not None
            assert rec.description is not None
            assert rec.priority.value in ["high", "medium", "low"]
            assert rec.impact is not None
            assert rec.effort is not None
            assert rec.cost is not None
            assert rec.rationale is not None
    
    def test_end_to_end_simple(self):
        """Test complete architecture generation pipeline"""
        # Parse requirements
        parser = InputParser()
        extractor = RequirementsExtractor()
        
        input_text = """
        We need a customer management system.
        Users should be able to create accounts and manage profiles.
        The system must be secure and handle 1000 concurrent users.
        We have a budget of $50,000.
        """
        
        parsed = parser.parse(input_text)
        requirements = extractor.extract(parsed)
        
        # Generate architecture
        generator = ArchitectureGenerator()
        architecture = generator.generate(requirements)
        
        assert architecture.name is not None
        assert len(architecture.components) > 0
        assert architecture.quality_score > 0.0
        
        # Render diagrams
        renderer = DiagramRenderer()
        diagrams = renderer.render(architecture)
        
        assert len(diagrams) >= 2
        
        # Generate recommendations
        engine = RecommendationEngine()
        recommendations = engine.generate(architecture)
        
        assert len(recommendations) > 0
        
        print(f"✅ Architecture generated: {architecture.name}")
        print(f"   Components: {len(architecture.components)}")
        print(f"   Quality Score: {architecture.quality_score:.2f}")
        print(f"   Diagrams: {len(diagrams)}")
        print(f"   Recommendations: {len(recommendations)}")
