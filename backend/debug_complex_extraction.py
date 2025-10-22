#!/usr/bin/env python3
"""
Debug script to test complex requirements extraction
"""

import asyncio
import sys
import os
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.modules.llm_service import SimpleLLMService
from app.modules.llm_response_parser import LLMResponseParser

async def test_complex_extraction():
    """Test complex requirements extraction"""
    
    llm_service = SimpleLLMService()
    
    print("=== Testing Complex Requirements Extraction ===")
    
    try:
        # Test with the actual requirements extraction prompt
        response = await llm_service.call_llm(
            "Analyze the following text and extract comprehensive requirements with technical depth:\n\nBuild an e-commerce platform with user authentication, product catalog, shopping cart, and payment processing",
            """You are an expert requirements analyst. Extract requirements from the given text and return a JSON response with this structure:

{
  "business_goals": [
    {
      "id": "bg_1",
      "title": "Goal title",
      "description": "Goal description",
      "priority": "high|medium|low",
      "confidence": 0.8
    }
  ],
  "functional_requirements": [
    {
      "id": "fr_1", 
      "title": "Requirement title",
      "description": "Requirement description",
      "priority": "high|medium|low",
      "confidence": 0.9
    }
  ],
  "non_functional_requirements": [
    {
      "id": "nfr_1",
      "title": "Performance requirement",
      "description": "Performance description",
      "priority": "high|medium|low", 
      "confidence": 0.8
    }
  ],
  "constraints": [
    {
      "id": "c_1",
      "title": "Constraint title",
      "description": "Constraint description",
      "priority": "high|medium|low",
      "confidence": 0.9
    }
  ],
  "stakeholders": [
    {
      "id": "s_1",
      "title": "Stakeholder title",
      "description": "Stakeholder description",
      "priority": "high|medium|low",
      "confidence": 0.9
    }
  ]
}

Extract relevant requirements from the text. Be thorough and accurate.

Return ONLY valid JSON. No Markdown, no prose.""",
            stage="test",
            provider_hint="deepseek"
        )
        
        print(f"Raw Response (first 500 chars): {response[:500]}")
        print()
        
        # Test extract_json method
        extracted = LLMResponseParser.extract_json(response)
        print(f"Extracted JSON (first 500 chars): {extracted[:500]}")
        print()
        
        # Try to parse the extracted JSON
        try:
            parsed = json.loads(extracted)
            print("=== JSON Parsing Success ===")
            print(f"Keys: {list(parsed.keys())}")
            print(f"Business Goals: {len(parsed.get('business_goals', []))}")
            print(f"Functional Requirements: {len(parsed.get('functional_requirements', []))}")
        except json.JSONDecodeError as e:
            print(f"=== JSON Parsing Failed ===")
            print(f"Error: {e}")
            print(f"Error position: {e.pos}")
            print(f"Error line: {e.lineno}")
            print(f"Error column: {e.colno}")
            print(f"Problematic area: {extracted[max(0, e.pos-100):e.pos+100]}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complex_extraction())
