#!/usr/bin/env python3
"""
Debug script to test simple LLM calls
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.modules.llm_service import SimpleLLMService

async def test_simple_llm():
    """Test simple LLM calls"""
    
    llm_service = SimpleLLMService()
    
    print("=== Testing Simple LLM Call ===")
    
    try:
        # Test with a very simple prompt
        response = await llm_service.call_llm(
            "Extract requirements from: Build an e-commerce platform",
            "You are a requirements analyst. Extract requirements and return JSON: {\"requirements\": [\"requirement1\", \"requirement2\"]}",
            stage="test",
            provider_hint="deepseek"
        )
        
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_llm())
