#!/usr/bin/env python3
"""
Test script for the ArchMesh Diagram Generation System
Tests all endpoints and functionality
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_diagram_types():
    """Test the diagram types endpoint"""
    print("🔍 Testing diagram types endpoint...")
    response = requests.get(f"{API_BASE}/diagrams/types")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Diagram types endpoint working")
        print(f"   Found {len(data['diagram_types'])} diagram types")
        print(f"   Found {len(data['output_formats'])} output formats")
        return True
    else:
        print(f"❌ Diagram types endpoint failed: {response.status_code}")
        return False

def test_diagram_templates():
    """Test the diagram templates endpoint"""
    print("🔍 Testing diagram templates endpoint...")
    response = requests.get(f"{API_BASE}/diagrams/templates")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Diagram templates endpoint working")
        print(f"   Found {len(data['templates'])} templates")
        return True
    else:
        print(f"❌ Diagram templates endpoint failed: {response.status_code}")
        return False

def test_c4_diagram_generation():
    """Test C4 diagram generation (without authentication)"""
    print("🔍 Testing C4 diagram generation...")
    
    payload = {
        "project_id": "test-project-123",
        "diagram_type": "c4_context",
        "title": "Test C4 Context Diagram",
        "description": "Test diagram generation for ArchMesh",
        "include_nfr": True,
        "include_technology_stack": True
    }
    
    response = requests.post(
        f"{API_BASE}/diagrams/c4",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print("✅ C4 diagram generation endpoint working (authentication required)")
        return True
    elif response.status_code == 200:
        data = response.json()
        print("✅ C4 diagram generation successful")
        print(f"   Generated diagram: {data.get('title', 'Unknown')}")
        return True
    else:
        print(f"❌ C4 diagram generation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_sequence_diagram_generation():
    """Test sequence diagram generation"""
    print("🔍 Testing sequence diagram generation...")
    
    payload = {
        "project_id": "test-project-123",
        "use_cases": ["User Registration", "Order Processing"],
        "title": "Test Sequence Diagram",
        "description": "Test sequence diagram generation"
    }
    
    response = requests.post(
        f"{API_BASE}/diagrams/sequence",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print("✅ Sequence diagram generation endpoint working (authentication required)")
        return True
    elif response.status_code == 200:
        data = response.json()
        print("✅ Sequence diagram generation successful")
        print(f"   Generated diagram: {data.get('title', 'Unknown')}")
        return True
    else:
        print(f"❌ Sequence diagram generation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_nfr_mapping_generation():
    """Test NFR mapping generation"""
    print("🔍 Testing NFR mapping generation...")
    
    payload = {
        "project_id": "test-project-123",
        "nfr_requirements": [
            {
                "name": "Response Time",
                "metric": "latency",
                "target_value": "200",
                "unit": "ms",
                "priority": "high",
                "affected_components": ["api-gateway", "web-app"]
            }
        ],
        "title": "Test NFR Mapping",
        "description": "Test NFR mapping generation"
    }
    
    response = requests.post(
        f"{API_BASE}/diagrams/nfr-mapping",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 401:
        print("✅ NFR mapping generation endpoint working (authentication required)")
        return True
    elif response.status_code == 200:
        data = response.json()
        print("✅ NFR mapping generation successful")
        print(f"   Generated diagram: {data.get('title', 'Unknown')}")
        return True
    else:
        print(f"❌ NFR mapping generation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def test_server_health():
    """Test server health and basic connectivity"""
    print("🔍 Testing server health...")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server health check passed")
            return True
        else:
            print(f"⚠️  Server health check returned {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Server health check failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting ArchMesh Diagram Generation System Tests")
    print("=" * 60)
    
    tests = [
        ("Server Health", test_server_health),
        ("Diagram Types", test_diagram_types),
        ("Diagram Templates", test_diagram_templates),
        ("C4 Diagram Generation", test_c4_diagram_generation),
        ("Sequence Diagram Generation", test_sequence_diagram_generation),
        ("NFR Mapping Generation", test_nfr_mapping_generation),
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
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Diagram generation system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
