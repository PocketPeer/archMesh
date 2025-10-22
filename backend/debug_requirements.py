#!/usr/bin/env python3
"""
Debug script to test requirements extraction and conversion
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.modules.requirements import InputParser, RequirementsExtractor
from app.modules.llm_service import SimpleLLMService

async def test_requirements_extraction():
    """Test the requirements extraction process"""
    
    # Test input
    input_text = "Build an e-commerce platform with user authentication, product catalog, shopping cart, and payment processing"
    
    print("=== Testing Requirements Extraction ===")
    print(f"Input: {input_text}")
    print()
    
    # Step 1: Parse Input
    parser = InputParser()
    parsed_input = parser.parse(input_text)
    print(f"Parsed Input: {parsed_input}")
    print()
    
    # Step 2: Test LLM Service directly
    llm_service = SimpleLLMService()
    print("=== Testing LLM Service Directly ===")
    try:
        llm_result = await llm_service.extract_requirements(input_text)
        print(f"LLM Result Keys: {list(llm_result.keys())}")
        print(f"Business Goals Count: {len(llm_result.get('business_goals', []))}")
        print(f"Functional Requirements Count: {len(llm_result.get('functional_requirements', []))}")
        print(f"Non-Functional Requirements Count: {len(llm_result.get('non_functional_requirements', []))}")
        print(f"Constraints Count: {len(llm_result.get('constraints', []))}")
        print(f"Stakeholders Count: {len(llm_result.get('stakeholders', []))}")
        
        # Print first business goal
        if llm_result.get('business_goals'):
            print(f"First Business Goal: {llm_result['business_goals'][0]}")
        print()
        
    except Exception as e:
        print(f"LLM Service Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Test Requirements Extractor
    print("=== Testing Requirements Extractor ===")
    extractor = RequirementsExtractor()
    try:
        extracted_requirements = await extractor.extract(parsed_input)
        print(f"Extracted Requirements:")
        print(f"  Business Goals: {len(extracted_requirements.business_goals)}")
        print(f"  Functional Requirements: {len(extracted_requirements.functional_requirements)}")
        print(f"  Non-Functional Requirements: {len(extracted_requirements.non_functional_requirements)}")
        print(f"  Constraints: {len(extracted_requirements.constraints)}")
        print(f"  Stakeholders: {len(extracted_requirements.stakeholders)}")
        
        # Print first business goal
        if extracted_requirements.business_goals:
            print(f"First Business Goal: {extracted_requirements.business_goals[0]}")
        
    except Exception as e:
        print(f"Requirements Extractor Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_requirements_extraction())
