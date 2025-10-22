#!/usr/bin/env python3
"""
Test script for DeepSeek local LLM integration.

This script tests the DeepSeek client and agent integration
to ensure everything is working correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.deepseek_client import DeepSeekClient, ChatDeepSeek
from app.agents.base_agent import BaseAgent
from app.config import Settings
from langchain_core.messages import HumanMessage, SystemMessage


async def test_deepseek_client():
    """Test the DeepSeek client directly."""
    print("🧪 Testing DeepSeek Client...")
    
    client = DeepSeekClient(
        base_url="http://localhost:11434",
        model="deepseek-r1",
        temperature=0.7
    )
    
    # Test health check
    print("  📡 Checking DeepSeek server health...")
    is_healthy = await client.health_check()
    if not is_healthy:
        print("  ❌ DeepSeek server is not healthy. Please ensure Ollama is running.")
        return False
    
    print("  ✅ DeepSeek server is healthy")
    
    # Test generation
    print("  🤖 Testing text generation...")
    try:
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Say 'Hello from DeepSeek!' and nothing else.")
        ]
        
        response = await client.generate(messages)
        print(f"  ✅ Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"  ❌ Generation failed: {e}")
        return False


async def test_chat_deepseek():
    """Test the ChatDeepSeek wrapper."""
    print("\n🧪 Testing ChatDeepSeek Wrapper...")
    
    chat = ChatDeepSeek(
        base_url="http://localhost:11434",
        model="deepseek-r1",
        temperature=0.7
    )
    
    try:
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="What is 2+2? Answer with just the number.")
        ]
        
        response = await chat.ainvoke(messages)
        print(f"  ✅ Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"  ❌ ChatDeepSeek test failed: {e}")
        return False


async def test_agent_integration():
    """Test agent integration with DeepSeek."""
    print("\n🧪 Testing Agent Integration...")
    
    # Create a simple test agent
    class TestAgent(BaseAgent):
        def get_system_prompt(self) -> str:
            return "You are a helpful assistant."
        
        async def execute(self, input_data):
            messages = [
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content=f"Process this input: {input_data.get('text', 'Hello')}")
            ]
            
            response = await self.llm.ainvoke(messages)
            return {
                "status": "success",
                "result": response.content,
                "provider": self.llm_provider,
                "model": self.llm_model
            }
    
    try:
        # Test with DeepSeek
        agent = TestAgent(
            agent_type="test",
            llm_provider="deepseek",
            llm_model="deepseek-r1"
        )
        
        result = await agent.execute({"text": "Test message"})
        print(f"  ✅ Agent result: {result['result']}")
        print(f"  ✅ Provider: {result['provider']}")
        print(f"  ✅ Model: {result['model']}")
        return True
        
    except Exception as e:
        print(f"  ❌ Agent integration test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 DeepSeek Integration Test Suite")
    print("=" * 50)
    
    # Check if Ollama is running
    print("📡 Checking if Ollama is running...")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                print("  ✅ Ollama is running")
            else:
                print("  ❌ Ollama is not responding correctly")
                return
    except Exception as e:
        print(f"  ❌ Cannot connect to Ollama: {e}")
        print("  💡 Please ensure Ollama is running: ollama serve")
        return
    
    # Run tests
    tests = [
        test_deepseek_client,
        test_chat_deepseek,
        test_agent_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"  🎉 All {total} tests passed!")
        print("  ✅ DeepSeek integration is working correctly")
    else:
        print(f"  ⚠️  {passed}/{total} tests passed")
        print("  ❌ Some tests failed. Please check the setup.")
    
    print("\n💡 Next steps:")
    print("  1. Set DEFAULT_LLM_PROVIDER=deepseek in your .env file")
    print("  2. Start the backend: cd backend && uvicorn app.main:app --reload")
    print("  3. The application will now use DeepSeek locally (no API costs!)")


if __name__ == "__main__":
    asyncio.run(main())
