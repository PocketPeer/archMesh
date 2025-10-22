#!/usr/bin/env python3
"""
Test JSON parsing with the LLMResponseParser
"""

import json
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.llm_response_parser import LLMResponseParser

def test_json_parsing():
    """Test JSON parsing with a sample response"""
    
    # Sample response with markdown code blocks (like what the LLM returns)
    sample_response = """```
{
  "architecture_overview": {
    "name": "Cloud-Native E-commerce Platform",
    "style": "microservices",
    "description": "Comprehensive architecture for a cloud-native e-commerce platform",
    "rationale": "To meet the business goals and requirements",
    "quality_attributes": ["scalability", "maintainability", "security", "performance"]
  },
  "components": [
    {
      "id": "comp_1",
      "name": "Authentication Service",
      "type": "service",
      "description": "Handles user authentication",
      "responsibilities": ["User login", "User registration"],
      "technologies": ["Node.js", "Express", "JWT"],
      "interfaces": [],
      "dependencies": [],
      "scalability": "Horizontal scaling",
      "security_considerations": ["Password hashing", "JWT tokens"],
      "performance_characteristics": {
        "expected_load": "1000 req/s",
        "response_time": "200ms",
        "resource_requirements": "2 CPU, 4GB RAM"
      },
      "data_model": {
        "entities": ["User", "Session"],
        "relationships": ["User has Sessions"],
        "storage_requirements": "10GB initial"
      }
    }
  ],
  "diagrams": {
    "c4_context": {
      "title": "System Context",
      "description": "High-level system context",
      "code": "@startuml\n!include C4_Context.puml\n...\n@enduml"
    },
    "c4_container": {
      "title": "Container Diagram",
      "description": "System containers",
      "code": "@startuml\n!include C4_Container.puml\n...\n@enduml"
    },
    "sequence_diagrams": []
  },
  "technology_stack": {
    "frontend": ["React", "Next.js"],
    "backend": ["Node.js", "Express"],
    "database": ["PostgreSQL"],
    "infrastructure": ["Docker", "AWS"],
    "monitoring": ["Prometheus"],
    "security": ["OAuth2", "JWT"]
  },
  "implementation_plan": {
    "phases": [
      {
        "id": "phase_1",
        "name": "Foundation",
        "description": "Basic infrastructure setup",
        "duration": "2 weeks",
        "deliverables": ["Infrastructure", "Basic APIs"],
        "dependencies": [],
        "risks": ["Learning curve"],
        "success_criteria": ["Infrastructure deployed"]
      }
    ],
    "tasks": [
      {
        "id": "task_1",
        "title": "Setup Infrastructure",
        "description": "Deploy basic infrastructure",
        "phase_id": "phase_1",
        "effort": "5 days",
        "assignee": "DevOps",
        "dependencies": [],
        "acceptance_criteria": ["Infrastructure running"]
      }
    ],
    "timeline": {
      "total_duration": "8 weeks",
      "critical_path": ["task1"],
      "milestones": [
        {
          "name": "MVP Ready",
          "date": "2024-03-01",
          "deliverables": ["Basic system"]
        }
      ]
    }
  },
  "quality_analysis": {
    "scalability": {
      "current_capacity": "100 users",
      "scaling_strategy": "Horizontal scaling",
      "bottlenecks": ["Database"],
      "mitigation": ["Caching", "Load balancing"]
    },
    "security": {
      "threats": ["Unauthorized access"],
      "mitigations": ["Authentication", "Authorization"],
      "compliance": [],
      "authentication": "OAuth2",
      "authorization": "RBAC"
    },
    "performance": {
      "targets": {
        "response_time": "500ms",
        "throughput": "100 req/s",
        "availability": "99%"
      },
      "optimization_strategies": ["Caching"]
    }
  },
  "tradeoffs": [
    {
      "aspect": "Simplicity vs Scalability",
      "pros": ["Easy to understand"],
      "cons": ["Limited scalability"],
      "recommendation": "Start simple, scale as needed"
    }
  ],
  "recommendations": [
    {
      "id": "rec_1",
      "title": "Add Monitoring",
      "description": "Implement comprehensive monitoring",
      "priority": "medium",
      "impact": "high",
      "effort": "medium",
      "rationale": "Essential for production",
      "implementation": "Add Prometheus and Grafana"
    }
  ],
  "risks": [
    {
      "id": "risk_1",
      "title": "Technical Risk",
      "description": "Technology learning curve",
      "probability": "medium",
      "impact": "medium",
      "mitigation": "Training and documentation"
    }
  ]
}
```"""

    print("🧪 Testing JSON parsing...")
    print(f"📄 Sample response length: {len(sample_response)} characters")
    print(f"📄 Sample response (first 100 chars): {sample_response[:100]}")
    
    try:
        # Test direct JSON parsing (should fail)
        direct_parse = json.loads(sample_response)
        print("✅ Direct JSON parsing succeeded (unexpected)")
    except json.JSONDecodeError as e:
        print(f"❌ Direct JSON parsing failed as expected: {e}")
    
    try:
        # Test LLMResponseParser.extract_json
        extracted = LLMResponseParser.extract_json(sample_response)
        print(f"🔧 Extracted JSON length: {len(extracted)} characters")
        print(f"🔧 Extracted JSON (first 100 chars): {extracted[:100]}")
        
        # Test parsing the extracted JSON
        parsed = json.loads(extracted)
        print("✅ Extracted JSON parsing successful!")
        print(f"📊 Parsed keys: {list(parsed.keys())}")
        
        # Test LLMResponseParser.parse_json_response
        result = LLMResponseParser.parse_json_response(sample_response)
        print("✅ LLMResponseParser.parse_json_response successful!")
        print(f"📊 Result keys: {list(result.keys())}")
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ Extracted JSON parsing failed: {e}")
        print(f"📄 Error at position: {e.pos}")
        print(f"📄 Context around error: {extracted[max(0, e.pos-50):e.pos+50]}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    test_json_parsing()
