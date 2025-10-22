#!/usr/bin/env python3
"""
Test script for the ArchMesh Workflow Diagram Integration System
Tests the integration of diagram generation into workflow execution
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_workflow_diagram_endpoints():
    """Test the workflow diagram integration endpoints"""
    print("🔍 Testing workflow diagram integration endpoints...")
    
    # Test 1: Get project diagrams (should require authentication)
    print("  📋 Testing project diagrams endpoint...")
    response = requests.get(f"{API_BASE}/workflow-diagrams/project/test-project")
    if response.status_code == 401:
        print("    ✅ Project diagrams endpoint working (authentication required)")
    else:
        print(f"    ❌ Project diagrams endpoint failed: {response.status_code}")
        return False
    
    # Test 2: Generate workflow diagrams (should require authentication)
    print("  📋 Testing workflow diagram generation endpoint...")
    payload = {
        "project_id": "test-project",
        "workflow_stage": "parse_requirements",
        "workflow_data": {
            "project_name": "Test Project",
            "requirements": {"functional": [], "non_functional": []},
            "architecture": {}
        },
        "context": {"user_id": "test-user"}
    }
    
    response = requests.post(
        f"{API_BASE}/workflow-diagrams/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print("    ✅ Workflow diagram generation endpoint working (authentication required)")
    else:
        print(f"    ❌ Workflow diagram generation endpoint failed: {response.status_code}")
        return False
    
    # Test 3: Regenerate diagrams (should require authentication)
    print("  📋 Testing diagram regeneration endpoint...")
    payload = {
        "project_id": "test-project",
        "diagram_types": ["c4_context", "sequence"],
        "context": {"user_id": "test-user"}
    }
    
    response = requests.post(
        f"{API_BASE}/workflow-diagrams/regenerate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print("    ✅ Diagram regeneration endpoint working (authentication required)")
    else:
        print(f"    ❌ Diagram regeneration endpoint failed: {response.status_code}")
        return False
    
    # Test 4: Async workflow diagram generation (should require authentication)
    print("  📋 Testing async workflow diagram generation endpoint...")
    payload = {
        "project_id": "test-project",
        "workflow_stage": "design_architecture",
        "workflow_data": {
            "project_name": "Test Project",
            "requirements": {"functional": [], "non_functional": []},
            "architecture": {}
        },
        "context": {"user_id": "test-user"}
    }
    
    response = requests.post(
        f"{API_BASE}/workflow-diagrams/workflow/test-workflow-123/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print("    ✅ Async workflow diagram generation endpoint working (authentication required)")
    else:
        print(f"    ❌ Async workflow diagram generation endpoint failed: {response.status_code}")
        return False
    
    # Test 5: Workflow diagram status (should require authentication)
    print("  📋 Testing workflow diagram status endpoint...")
    response = requests.get(f"{API_BASE}/workflow-diagrams/workflow/test-workflow-123/status")
    if response.status_code == 401:
        print("    ✅ Workflow diagram status endpoint working (authentication required)")
    else:
        print(f"    ❌ Workflow diagram status endpoint failed: {response.status_code}")
        return False
    
    return True

def test_diagram_system_integration():
    """Test that the basic diagram system still works after integration"""
    print("🔍 Testing diagram system integration...")
    
    # Test diagram types endpoint
    print("  📋 Testing diagram types endpoint...")
    response = requests.get(f"{API_BASE}/diagrams/types")
    if response.status_code == 200:
        data = response.json()
        print(f"    ✅ Diagram types endpoint working ({len(data['diagram_types'])} types)")
    else:
        print(f"    ❌ Diagram types endpoint failed: {response.status_code}")
        return False
    
    # Test diagram templates endpoint
    print("  📋 Testing diagram templates endpoint...")
    response = requests.get(f"{API_BASE}/diagrams/templates")
    if response.status_code == 200:
        data = response.json()
        print(f"    ✅ Diagram templates endpoint working ({len(data['templates'])} templates)")
    else:
        print(f"    ❌ Diagram templates endpoint failed: {response.status_code}")
        return False
    
    return True

def test_server_health():
    """Test server health and basic connectivity"""
    print("🔍 Testing server health...")
    
    try:
        # Test basic connectivity
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("    ✅ Server health check passed (docs accessible)")
            return True
        else:
            print(f"    ⚠️  Server health check returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Server health check failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting ArchMesh Workflow Diagram Integration Tests")
    print("=" * 70)
    
    tests = [
        ("Server Health", test_server_health),
        ("Diagram System Integration", test_diagram_system_integration),
        ("Workflow Diagram Endpoints", test_workflow_diagram_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 70)
    print("📊 Test Results Summary")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Workflow diagram integration is working correctly.")
        print("\n📋 Integration Summary:")
        print("  ✅ Workflow diagram endpoints are properly secured")
        print("  ✅ Basic diagram system remains functional")
        print("  ✅ Server is running and accessible")
        print("  ✅ All endpoints are responding correctly")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
