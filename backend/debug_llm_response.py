#!/usr/bin/env python3
"""
Debug script to see exactly what the LLM is returning
"""

import asyncio
import sys
import os
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.modules.llm_service import SimpleLLMService

async def debug_llm_response():
    """Debug the exact LLM response"""
    
    llm_service = SimpleLLMService()
    
    # Test input
    input_text = "Build an e-commerce platform with user authentication, product catalog, shopping cart, and payment processing"
    
    print("=== Testing LLM Response ===")
    print(f"Input: {input_text}")
    print()
    
    try:
        # Call the LLM directly
        response = await llm_service.call_llm(
            f"Analyze the following text and extract comprehensive requirements with technical depth:\n\n{input_text}",
            """You are an expert requirements analyst and system architect. Extract comprehensive requirements from the given text and return a JSON response with the following structure:

{
  "business_goals": [
    {
      "id": "bg_1",
      "title": "Goal title",
      "description": "Detailed goal description with measurable outcomes",
      "priority": "high|medium|low",
      "confidence": 0.8,
      "success_metrics": ["metric1", "metric2"],
      "assumptions": ["assumption1", "assumption2"]
    }
  ],
  "functional_requirements": [
    {
      "id": "fr_1", 
      "title": "Requirement title",
      "description": "Detailed functional requirement with acceptance criteria",
      "priority": "high|medium|low",
      "confidence": 0.9,
      "acceptance_criteria": ["criteria1", "criteria2"],
      "dependencies": ["other_requirement_id"],
      "complexity": "low|medium|high"
    }
  ],
  "non_functional_requirements": [
    {
      "id": "nfr_1",
      "title": "Performance requirement",
      "description": "Detailed non-functional requirement with specific metrics",
      "priority": "high|medium|low", 
      "confidence": 0.8,
      "metrics": {
        "response_time": "200ms",
        "throughput": "1000 req/s",
        "availability": "99.9%"
      },
      "test_scenarios": ["scenario1", "scenario2"]
    }
  ],
  "constraints": [
    {
      "id": "c_1",
      "title": "Budget constraint",
      "description": "Detailed constraint with impact analysis",
      "priority": "high|medium|low",
      "confidence": 0.9,
      "impact": "high|medium|low",
      "mitigation": "potential mitigation strategies"
    }
  ],
  "stakeholders": [
    {
      "id": "s_1",
      "title": "End users",
      "description": "Primary system users with roles and responsibilities",
      "priority": "high|medium|low",
      "confidence": 0.9,
      "roles": ["role1", "role2"],
      "pain_points": ["pain1", "pain2"]
    }
  ]
}

Extract as many relevant requirements as possible. Be thorough, accurate, and include technical depth. Focus on:
1. Measurable success criteria
2. Technical assumptions and constraints
3. Dependencies between requirements
4. Domain-specific considerations
5. Non-obvious constraints that could impact architecture

Return ONLY valid JSON. No Markdown, no prose.""",
            stage="debug_test",
            provider_hint="deepseek"
        )
        
        print("=== Raw LLM Response ===")
        print(f"Response length: {len(response)}")
        print(f"Response (first 500 chars): {response[:500]}")
        print()
        print(f"Response (last 500 chars): {response[-500:]}")
        print()
        
        # Test the extract_json method
        from app.modules.llm_response_parser import LLMResponseParser
        
        print("=== Testing extract_json method ===")
        extracted = LLMResponseParser.extract_json(response)
        print(f"Extracted length: {len(extracted)}")
        print(f"Extracted (first 200 chars): {extracted[:200]}")
        print(f"Extracted (last 200 chars): {extracted[-200:]}")
        print()
        
        # Try to parse the extracted JSON
        try:
            parsed = json.loads(extracted)
            print("=== JSON Parsing Success ===")
            print(f"Keys: {list(parsed.keys())}")
            print(f"Business Goals: {len(parsed.get('business_goals', []))}")
        except json.JSONDecodeError as e:
            print(f"=== JSON Parsing Failed ===")
            print(f"Error: {e}")
            print(f"Error position: {e.pos}")
            print(f"Error line: {e.lineno}")
            print(f"Error column: {e.colno}")
            
            # Show the problematic area
            start = max(0, e.pos - 100)
            end = min(len(extracted), e.pos + 100)
            print(f"Problematic area: {extracted[start:end]}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_llm_response())
