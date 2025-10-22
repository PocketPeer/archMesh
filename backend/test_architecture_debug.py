#!/usr/bin/env python3
"""
Test architecture generation with debug output
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.architecture.architecture_generator import ArchitectureGenerator
from app.modules.requirements.models import ExtractedRequirements, BusinessGoal, FunctionalRequirement, NonFunctionalRequirement, Constraint, Stakeholder

async def test_architecture_generation():
    """Test architecture generation with debug output"""
    print("🧪 Testing Architecture Generation...")
    
    # Create a mock ExtractedRequirements object
    mock_requirements = ExtractedRequirements(
        business_goals=[
            BusinessGoal(id="bg_1", title="E-commerce Platform", description="Build an e-commerce platform to sell products online.", priority="high", confidence=0.9)
        ],
        functional_requirements=[
            FunctionalRequirement(id="fr_1", title="User Authentication", description="Users must be able to register, login, and manage their profiles.", priority="high", confidence=0.9),
            FunctionalRequirement(id="fr_2", title="Product Catalog", description="Display a catalog of products with details, images, and pricing.", priority="high", confidence=0.9),
            FunctionalRequirement(id="fr_3", title="Shopping Cart", description="Users can add, remove, and update items in a shopping cart.", priority="high", confidence=0.9),
            FunctionalRequirement(id="fr_4", title="Payment Processing", description="Integrate with a payment gateway to process orders securely.", priority="high", confidence=0.9)
        ],
        non_functional_requirements=[
            NonFunctionalRequirement(id="nfr_1", title="Scalability", description="The platform must handle 10,000 concurrent users.", priority="high", confidence=0.8),
            NonFunctionalRequirement(id="nfr_2", title="Security", description="All user data and payment information must be securely stored and transmitted.", priority="high", confidence=0.9)
        ],
        constraints=[],
        stakeholders=[
            Stakeholder(id="s_1", title="Customers", description="End-users purchasing products.", priority="high", confidence=0.9),
            Stakeholder(id="s_2", title="Administrators", description="Manage products, orders, and users.", priority="medium", confidence=0.8)
        ]
    )
    
    domain = "cloud-native"
    
    try:
        print("📞 Calling ArchitectureGenerator...")
        generator = ArchitectureGenerator()
        architecture = await generator.generate(mock_requirements, domain)
        
        print("✅ Architecture generation completed!")
        print(f"📊 Architecture name: {architecture.name}")
        print(f"📊 Architecture style: {architecture.style}")
        print(f"📊 Components count: {len(architecture.components)}")
        print(f"📊 Technology stack: {architecture.technology_stack}")
        
        return architecture
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    asyncio.run(test_architecture_generation())
