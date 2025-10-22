#!/usr/bin/env python3
"""
Debug script to test JSON extraction
"""

import asyncio
import sys
import os
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.modules.llm_service import SimpleLLMService
from app.modules.llm_response_parser import LLMResponseParser

async def test_json_extraction():
    """Test JSON extraction process"""
    
    llm_service = SimpleLLMService()
    
    print("=== Testing JSON Extraction ===")
    
    try:
        # Test with a simple prompt
        response = await llm_service.call_llm(
            "Extract requirements from: Build an e-commerce platform",
            "You are a requirements analyst. Extract requirements and return JSON: {\"requirements\": [\"requirement1\", \"requirement2\"]}",
            stage="test",
            provider_hint="deepseek"
        )
        
        print(f"Raw Response: {response[:200]}...")
        print()
        
        # Test extract_json method
        extracted = LLMResponseParser.extract_json(response)
        print(f"Extracted JSON: {extracted[:200]}...")
        print()
        
        # Try to parse the extracted JSON
        try:
            parsed = json.loads(extracted)
            print("=== JSON Parsing Success ===")
            print(f"Keys: {list(parsed.keys())}")
        except json.JSONDecodeError as e:
            print(f"=== JSON Parsing Failed ===")
            print(f"Error: {e}")
            print(f"Error position: {e.pos}")
            print(f"Problematic area: {extracted[max(0, e.pos-50):e.pos+50]}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_json_extraction())
