#!/usr/bin/env python3
"""
Debug script to test the architecture LLM service directly
"""

import asyncio
import json
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.llm_service import SimpleLLMService

async def test_architecture_analysis():
    """Test the architecture analysis LLM call"""
    print("Testing Architecture Analysis LLM Service...")
    
    # Initialize the LLM service
    llm_service = SimpleLLMService()
    
    # Test requirements
    test_requirements = {
        "business_goals": [
            {
                "id": "bg_1",
                "title": "E-commerce Platform",
                "description": "Build a comprehensive e-commerce platform",
                "priority": "high",
                "confidence": 0.9
            }
        ],
        "functional_requirements": [
            {
                "id": "fr_1",
                "title": "User Authentication",
                "description": "Users can register, login, and manage their accounts",
                "priority": "high",
                "confidence": 0.9
            },
            {
                "id": "fr_2", 
                "title": "Product Catalog",
                "description": "Display products with search and filtering",
                "priority": "high",
                "confidence": 0.9
            },
            {
                "id": "fr_3",
                "title": "Shopping Cart",
                "description": "Add/remove items, manage quantities",
                "priority": "high",
                "confidence": 0.9
            },
            {
                "id": "fr_4",
                "title": "Payment Processing",
                "description": "Secure payment processing with multiple methods",
                "priority": "high",
                "confidence": 0.9
            }
        ],
        "non_functional_requirements": [
            {
                "id": "nfr_1",
                "title": "Performance",
                "description": "Page load times under 2 seconds",
                "priority": "high",
                "confidence": 0.8
            },
            {
                "id": "nfr_2",
                "title": "Security",
                "description": "Secure handling of payment data",
                "priority": "high",
                "confidence": 0.9
            }
        ],
        "constraints": [
            {
                "id": "c_1",
                "title": "Budget",
                "description": "Cost-effective cloud-native solution",
                "priority": "medium",
                "confidence": 0.7
            }
        ],
        "stakeholders": [
            {
                "id": "s_1",
                "title": "Customers",
                "description": "End users of the platform",
                "priority": "high",
                "confidence": 0.9
            }
        ]
    }
    
    try:
        print("Calling LLM for architecture analysis...")
        result = await llm_service.generate_architecture_analysis(test_requirements, "cloud-native")
        
        print("✅ LLM call successful!")
        print(f"Response type: {type(result)}")
        print(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Check if we have the expected structure
        if isinstance(result, dict):
            print("\n📊 Architecture Overview:")
            overview = result.get("architecture_overview", {})
            print(f"  Name: {overview.get('name', 'N/A')}")
            print(f"  Style: {overview.get('style', 'N/A')}")
            print(f"  Description: {overview.get('description', 'N/A')[:100]}...")
            
            print(f"\n🔧 Components: {len(result.get('components', []))}")
            print(f"📋 Implementation Plan: {'Yes' if result.get('implementation_plan') else 'No'}")
            print(f"📊 Quality Analysis: {'Yes' if result.get('quality_analysis') else 'No'}")
            print(f"📈 Diagrams: {'Yes' if result.get('diagrams') else 'No'}")
            
            # Show first component details
            components = result.get('components', [])
            if components:
                first_comp = components[0]
                print(f"\n🔍 First Component:")
                print(f"  Name: {first_comp.get('name', 'N/A')}")
                print(f"  Type: {first_comp.get('type', 'N/A')}")
                print(f"  Technologies: {first_comp.get('technologies', [])}")
                print(f"  Responsibilities: {first_comp.get('responsibilities', [])}")
        
        # Save full response for inspection
        with open('debug_architecture_response.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Full response saved to debug_architecture_response.json")
        
        return result
        
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    asyncio.run(test_architecture_analysis())
