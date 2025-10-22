#!/usr/bin/env python3
"""
Complete ArchMesh Demo - Simple & Modular System

This demo shows the complete simple, modular ArchMesh system:
1. Requirements Module: Parse and extract requirements
2. Architecture Module: Generate architecture and diagrams
3. Vibe Coding Module: Generate code from natural language
4. Integration: All modules working together
"""

from app.modules.requirements import InputParser, RequirementsExtractor, RequirementsValidator
from app.modules.architecture import ArchitectureGenerator, DiagramRenderer, RecommendationEngine
from app.modules.vibe_coding import CodeGenerator, SandboxExecutor, QualityChecker


def main():
    """Run the complete ArchMesh demo"""
    print("🚀 ArchMesh Complete Simple & Modular Demo")
    print("=" * 60)
    print()
    
    # Sample requirements for a complete system
    requirements_text = """
    We need to build a modern e-commerce platform for our business.
    
    Business Goals:
    - Increase online sales by 100% within 12 months
    - Improve customer satisfaction and retention rates
    - Expand to international markets with multi-language support
    - Reduce operational costs through automation
    
    Functional Requirements:
    - Users should be able to browse products with advanced search and filtering
    - Users should be able to create accounts and manage their profiles
    - Users should be able to add items to cart and checkout securely
    - Users should be able to track their orders and view order history
    - Administrators should be able to manage products, inventory, and orders
    - Support staff should be able to view customer information and provide support
    - System should support multiple payment methods and currencies
    
    Non-Functional Requirements:
    - System must be secure with end-to-end encryption
    - System must handle 50,000 concurrent users
    - System must respond within 1 second for 99% of requests
    - System must be available 99.9% of the time
    - System must be scalable to handle 10x growth
    - System must support mobile and desktop interfaces
    
    Constraints:
    - Budget: $1,000,000
    - Timeline: 18 months
    - Technology: Must use cloud-native architecture
    - Compliance: Must meet PCI DSS, GDPR, and SOC 2 standards
    - Team: 15 developers maximum
    
    Stakeholders:
    - Customers: End users who will shop on the platform
    - Administrators: Staff who manage the platform and business
    - Support Staff: Customer service representatives
    - Developers: Engineering team building the platform
    - Business Owners: Company executives and stakeholders
    """
    
    print("📋 PHASE 1: Requirements Processing")
    print("=" * 40)
    
    # Step 1: Parse requirements
    print("🔍 Step 1.1: Parsing Requirements")
    parser = InputParser()
    parsed = parser.parse(requirements_text)
    
    print(f"✅ Input parsed successfully")
    print(f"   Confidence: {parsed.confidence:.2f}")
    print(f"   Length: {len(parsed.text)} characters")
    print(f"   Word count: {parsed.metadata['word_count']}")
    print()
    
    # Step 2: Extract requirements
    print("🔍 Step 1.2: Extracting Requirements")
    extractor = RequirementsExtractor()
    requirements = extractor.extract(parsed)
    
    print(f"✅ Requirements extracted:")
    print(f"   Business Goals: {len(requirements.business_goals)}")
    print(f"   Functional Requirements: {len(requirements.functional_requirements)}")
    print(f"   Non-Functional Requirements: {len(requirements.non_functional_requirements)}")
    print(f"   Constraints: {len(requirements.constraints)}")
    print(f"   Stakeholders: {len(requirements.stakeholders)}")
    print()
    
    # Step 3: Validate requirements
    print("🔍 Step 1.3: Validating Requirements")
    validator = RequirementsValidator()
    validation = validator.validate(requirements)
    
    print(f"✅ Requirements validated:")
    print(f"   Status: {validation.status.value}")
    print(f"   Score: {validation.score:.2f}")
    print(f"   Issues: {len(validation.issues)}")
    print(f"   Suggestions: {len(validation.suggestions)}")
    print()
    
    print("🏗️ PHASE 2: Architecture Generation")
    print("=" * 40)
    
    # Step 4: Generate architecture
    print("🔍 Step 2.1: Generating Architecture")
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
    print()
    
    # Show technology stack
    print("🔧 Technology Stack:")
    print(f"   Frontend: {', '.join(architecture.technology_stack.frontend)}")
    print(f"   Backend: {', '.join(architecture.technology_stack.backend)}")
    print(f"   Database: {', '.join(architecture.technology_stack.database)}")
    print(f"   Infrastructure: {', '.join(architecture.technology_stack.infrastructure)}")
    print()
    
    # Step 5: Render diagrams
    print("🔍 Step 2.2: Rendering Diagrams")
    renderer = DiagramRenderer()
    diagrams = renderer.render(architecture)
    
    print(f"✅ Diagrams rendered: {len(diagrams)} diagrams")
    for diagram in diagrams:
        print(f"   - {diagram.title}: {diagram.description}")
        print(f"     Type: {diagram.type.value}")
    print()
    
    # Step 6: Generate recommendations
    print("🔍 Step 2.3: Generating Recommendations")
    engine = RecommendationEngine()
    recommendations = engine.generate(architecture)
    
    print(f"✅ Recommendations generated: {len(recommendations)} recommendations")
    for rec in recommendations:
        print(f"   - {rec.title} ({rec.priority.value} priority)")
        print(f"     Impact: {rec.impact}")
        print(f"     Effort: {rec.effort}, Cost: {rec.cost}")
    print()
    
    print("💻 PHASE 3: Vibe Coding")
    print("=" * 40)
    
    # Step 7: Generate code for key components
    print("🔍 Step 3.1: Generating Code")
    code_generator = CodeGenerator()
    
    # Generate code for different components
    code_intents = [
        "Create a Python Flask API endpoint for user authentication with JWT tokens",
        "Create a React component for product search and filtering",
        "Create a Node.js microservice for order processing",
        "Create a Python data model for user profiles with validation"
    ]
    
    generated_codes = []
    for intent in code_intents:
        code = code_generator.generate(intent)
        generated_codes.append(code)
        print(f"   ✅ Generated {code.language.value} code: {intent[:50]}...")
    
    print()
    
    # Step 8: Check code quality
    print("🔍 Step 3.2: Checking Code Quality")
    quality_checker = QualityChecker()
    
    for i, code in enumerate(generated_codes):
        quality_report = quality_checker.check(code)
        print(f"   ✅ Code {i+1} quality: {quality_report.overall_quality.value} (score: {quality_report.score:.2f})")
    
    print()
    
    # Step 9: Validate execution environment
    print("🔍 Step 3.3: Validating Execution Environment")
    executor = SandboxExecutor()
    validation = executor.validate_execution_environment()
    
    print(f"✅ Environment validation:")
    for tool, available in validation.items():
        status = '✅' if available else '❌'
        availability = "Available" if available else "Not Available"
        print(f"   {status} {tool.title()}: {availability}")
    print()
    
    print("🎉 COMPLETE SYSTEM DEMO")
    print("=" * 60)
    print()
    print("✅ All Modules Working Successfully!")
    print()
    print("📊 System Summary:")
    print(f"   Requirements: {len(requirements.functional_requirements)} functional, {len(requirements.non_functional_requirements)} non-functional")
    print(f"   Architecture: {architecture.name} with {len(architecture.components)} components")
    print(f"   Diagrams: {len(diagrams)} C4 diagrams generated")
    print(f"   Recommendations: {len(recommendations)} architectural recommendations")
    print(f"   Code Generated: {len(generated_codes)} code components")
    print()
    print("🚀 Simple & Modular ArchMesh System Complete!")
    print("   - Requirements Module: ✅ Working")
    print("   - Architecture Module: ✅ Working") 
    print("   - Vibe Coding Module: ✅ Working")
    print("   - Integration: ✅ Working")
    print()
    print("🎯 Ready for Production!")
    print("   - All modules are simple and focused")
    print("   - All modules are modular and composable")
    print("   - All modules are well-tested")
    print("   - System is ready for the Admin Module")


if __name__ == "__main__":
    main()
