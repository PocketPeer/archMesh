#!/usr/bin/env python3
"""
Simple ArchMesh Demo - Requirements to Architecture Pipeline

This demo shows the simple, modular ArchMesh system in action:
1. Parse requirements from user input
2. Extract structured requirements
3. Generate architecture
4. Render diagrams
5. Generate recommendations
"""

from app.modules.requirements import InputParser, RequirementsExtractor, RequirementsValidator
from app.modules.architecture import ArchitectureGenerator, DiagramRenderer, RecommendationEngine


def main():
    """Run the simple ArchMesh demo"""
    print("🚀 ArchMesh Simple & Modular Demo")
    print("=" * 50)
    print()
    
    # Sample requirements
    requirements_text = """
    We need a modern e-commerce platform for our business.
    
    Business Goals:
    - Increase online sales by 50% within 6 months
    - Improve customer satisfaction and retention
    - Expand to international markets
    
    Functional Requirements:
    - Users should be able to browse products with search and filtering
    - Users should be able to add items to cart and checkout securely
    - Users should be able to create accounts and manage their profiles
    - Administrators should be able to manage products, orders, and customers
    - Support staff should be able to view customer orders and provide support
    
    Non-Functional Requirements:
    - System must be secure with encrypted data transmission
    - System must handle 10,000 concurrent users
    - System must respond within 2 seconds for 95% of requests
    - System must be available 99.9% of the time
    - System must be scalable to handle growth
    
    Constraints:
    - Budget: $500,000
    - Timeline: 12 months
    - Technology: Must use cloud infrastructure
    - Compliance: Must meet PCI DSS standards for payment processing
    
    Stakeholders:
    - Customers: End users who will shop on the platform
    - Administrators: Staff who manage the platform
    - Support Staff: Staff who provide customer support
    - Developers: Team building the platform
    """
    
    print("📋 Step 1: Parsing Requirements")
    print("-" * 30)
    
    # Parse requirements
    parser = InputParser()
    parsed = parser.parse(requirements_text)
    
    print(f"✅ Input parsed successfully")
    print(f"   Confidence: {parsed.confidence:.2f}")
    print(f"   Length: {len(parsed.text)} characters")
    print(f"   Word count: {parsed.metadata['word_count']}")
    print()
    
    print("🔍 Step 2: Extracting Requirements")
    print("-" * 30)
    
    # Extract requirements
    extractor = RequirementsExtractor()
    requirements = extractor.extract(parsed)
    
    print(f"✅ Requirements extracted:")
    print(f"   Business Goals: {len(requirements.business_goals)}")
    print(f"   Functional Requirements: {len(requirements.functional_requirements)}")
    print(f"   Non-Functional Requirements: {len(requirements.non_functional_requirements)}")
    print(f"   Constraints: {len(requirements.constraints)}")
    print(f"   Stakeholders: {len(requirements.stakeholders)}")
    print()
    
    # Show sample requirements
    if requirements.functional_requirements:
        print("📋 Sample Functional Requirements:")
        for req in requirements.functional_requirements[:2]:
            print(f"   - {req.title}: {req.description}")
        print()
    
    print("✅ Step 3: Validating Requirements")
    print("-" * 30)
    
    # Validate requirements
    validator = RequirementsValidator()
    validation = validator.validate(requirements)
    
    print(f"✅ Requirements validated:")
    print(f"   Status: {validation.status.value}")
    print(f"   Score: {validation.score:.2f}")
    print(f"   Issues: {len(validation.issues)}")
    print(f"   Suggestions: {len(validation.suggestions)}")
    print()
    
    print("🏗️ Step 4: Generating Architecture")
    print("-" * 30)
    
    # Generate architecture
    generator = ArchitectureGenerator()
    architecture = generator.generate(requirements)
    
    print(f"✅ Architecture generated:")
    print(f"   Name: {architecture.name}")
    print(f"   Style: {architecture.style.value}")
    print(f"   Components: {len(architecture.components)}")
    print(f"   Quality Score: {architecture.quality_score:.2f}")
    print()
    
    # Show components
    print("📋 Architecture Components:")
    for comp in architecture.components:
        print(f"   - {comp.name} ({comp.type.value})")
        print(f"     Technologies: {', '.join(comp.technologies)}")
        print(f"     Responsibilities: {', '.join(comp.responsibilities)}")
    print()
    
    # Show technology stack
    print("🔧 Technology Stack:")
    print(f"   Frontend: {', '.join(architecture.technology_stack.frontend)}")
    print(f"   Backend: {', '.join(architecture.technology_stack.backend)}")
    print(f"   Database: {', '.join(architecture.technology_stack.database)}")
    print(f"   Infrastructure: {', '.join(architecture.technology_stack.infrastructure)}")
    print()
    
    print("📊 Step 5: Rendering Diagrams")
    print("-" * 30)
    
    # Render diagrams
    renderer = DiagramRenderer()
    diagrams = renderer.render(architecture)
    
    print(f"✅ Diagrams rendered: {len(diagrams)} diagrams")
    for diagram in diagrams:
        print(f"   - {diagram.title}: {diagram.description}")
        print(f"     Type: {diagram.type.value}")
        print(f"     Content length: {len(diagram.content)} characters")
    print()
    
    print("💡 Step 6: Generating Recommendations")
    print("-" * 30)
    
    # Generate recommendations
    engine = RecommendationEngine()
    recommendations = engine.generate(architecture)
    
    print(f"✅ Recommendations generated: {len(recommendations)} recommendations")
    for rec in recommendations:
        print(f"   - {rec.title} ({rec.priority.value} priority)")
        print(f"     Impact: {rec.impact}")
        print(f"     Effort: {rec.effort}, Cost: {rec.cost}")
        print(f"     Rationale: {rec.rationale}")
    print()
    
    print("🎉 Demo Complete!")
    print("=" * 50)
    print()
    print("✅ Simple & Modular ArchMesh System Working!")
    print("   - Requirements Module: ✅ Working")
    print("   - Architecture Module: ✅ Working")
    print("   - Integration: ✅ Working")
    print()
    print("🚀 Ready for next modules:")
    print("   - Vibe Coding Module (Code Generation)")
    print("   - Admin Module (Model Management)")


if __name__ == "__main__":
    main()
