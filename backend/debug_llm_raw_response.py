#!/usr/bin/env python3
"""
Debug script to see the raw LLM response for architecture analysis
"""

import asyncio
import json
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.modules.llm_service import SimpleLLMService

async def debug_raw_llm_response():
    """Debug the raw LLM response"""
    print("🔍 Debugging Raw LLM Response...")
    
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
            }
        ],
        "non_functional_requirements": [
            {
                "id": "nfr_1",
                "title": "Performance",
                "description": "Page load times under 2 seconds",
                "priority": "high",
                "confidence": 0.8
            }
        ],
        "constraints": [],
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
        print("📞 Calling LLM for architecture analysis...")
        
        # Call the LLM service directly to see the raw response
        system_prompt = f"""You are an expert system architect and technical lead. Generate a comprehensive architecture analysis for a cloud-native system based on the provided requirements. Return a JSON response with the following structure:

{{
  "architecture_overview": {{
    "name": "System Architecture Name",
    "style": "microservices|monolith|serverless|layered|event-driven",
    "description": "Comprehensive architecture description",
    "rationale": "Why this architecture was chosen",
    "quality_attributes": ["scalability", "maintainability", "security", "performance"]
  }},
  "components": [
    {{
      "id": "comp_1",
      "name": "Component Name",
      "type": "service|database|cache|gateway|monitoring|security",
      "description": "Detailed component description",
      "responsibilities": ["responsibility1", "responsibility2"],
      "technologies": ["tech1", "tech2"],
      "interfaces": [
        {{
          "name": "API Name",
          "type": "REST|GraphQL|gRPC|Event",
          "description": "Interface description",
          "endpoints": ["endpoint1", "endpoint2"]
        }}
      ],
      "dependencies": ["other_component_id"],
      "scalability": "How this component scales",
      "security_considerations": ["consideration1", "consideration2"],
      "performance_characteristics": {{
        "expected_load": "1000 req/s",
        "response_time": "200ms",
        "resource_requirements": "2 CPU, 4GB RAM"
      }},
      "data_model": {{
        "entities": ["entity1", "entity2"],
        "relationships": ["relationship1", "relationship2"],
        "storage_requirements": "100GB initial, 10GB/month growth"
      }}
    }}
  ],
  "diagrams": {{
    "c4_context": {{
      "title": "System Context Diagram",
      "description": "High-level system context",
      "code": "PlantUML code for C4 Context diagram"
    }},
    "c4_container": {{
      "title": "Container Diagram", 
      "description": "System containers and relationships",
      "code": "PlantUML code for C4 Container diagram"
    }},
    "sequence_diagrams": [
      {{
        "title": "Key Use Case Flow",
        "description": "Sequence diagram for primary use case",
        "code": "PlantUML sequence diagram code"
      }}
    ]
  }},
  "technology_stack": {{
    "frontend": ["React", "Next.js", "TypeScript"],
    "backend": ["Node.js", "Express", "TypeScript"],
    "database": ["PostgreSQL", "Redis"],
    "infrastructure": ["Docker", "Kubernetes", "AWS"],
    "monitoring": ["Prometheus", "Grafana", "ELK Stack"],
    "security": ["OAuth2", "JWT", "HTTPS"]
  }},
  "implementation_plan": {{
    "phases": [
      {{
        "id": "phase_1",
        "name": "Phase Name",
        "description": "Phase description",
        "duration": "4 weeks",
        "deliverables": ["deliverable1", "deliverable2"],
        "dependencies": ["other_phase_id"],
        "risks": ["risk1", "risk2"],
        "success_criteria": ["criteria1", "criteria2"]
      }}
    ],
    "tasks": [
      {{
        "id": "task_1",
        "title": "Task title",
        "description": "Task description",
        "phase_id": "phase_1",
        "effort": "5 days",
        "assignee": "role",
        "dependencies": ["other_task_id"],
        "acceptance_criteria": ["criteria1", "criteria2"]
      }}
    ],
    "timeline": {{
      "total_duration": "12 weeks",
      "critical_path": ["task1", "task2", "task3"],
      "milestones": [
        {{
          "name": "Milestone Name",
          "date": "2024-03-01",
          "deliverables": ["deliverable1"]
        }}
      ]
    }}
  }},
  "quality_analysis": {{
    "scalability": {{
      "current_capacity": "1000 users",
      "scaling_strategy": "Horizontal scaling with load balancers",
      "bottlenecks": ["database", "external_apis"],
      "mitigation": ["database_sharding", "caching"]
    }},
    "security": {{
      "threats": ["threat1", "threat2"],
      "mitigations": ["mitigation1", "mitigation2"],
      "compliance": ["GDPR", "SOC2"],
      "authentication": "OAuth2 + JWT",
      "authorization": "RBAC"
    }},
    "performance": {{
      "targets": {{
        "response_time": "200ms",
        "throughput": "1000 req/s",
        "availability": "99.9%"
      }},
      "optimization_strategies": ["caching", "CDN", "database_indexing"]
    }}
  }},
  "tradeoffs": [
    {{
      "aspect": "Scalability vs Complexity",
      "pros": ["High scalability", "Independent deployments"],
      "cons": ["Increased complexity", "Network latency"],
      "recommendation": "Accept complexity for scalability benefits"
    }}
  ],
  "recommendations": [
    {{
      "id": "rec_1",
      "title": "Recommendation title",
      "description": "Detailed recommendation",
      "priority": "high|medium|low",
      "impact": "high|medium|low",
      "effort": "high|medium|low",
      "rationale": "Why this recommendation",
      "implementation": "How to implement"
    }}
  ],
  "risks": [
    {{
      "id": "risk_1",
      "title": "Risk title",
      "description": "Risk description",
      "probability": "high|medium|low",
      "impact": "high|medium|low",
      "mitigation": "Risk mitigation strategy"
    }}
  ]
}}

Generate a comprehensive, technically detailed architecture that addresses all requirements. Focus on:
1. Technical depth and specificity
2. Realistic technology choices
3. Detailed component specifications
4. Comprehensive diagrams
5. Practical implementation plan
6. Quality attribute analysis
7. Risk assessment and mitigation

Return ONLY valid JSON. No Markdown, no prose."""

        user_prompt = f"""Generate a comprehensive architecture analysis for the following requirements:

REQUIREMENTS:
{json.dumps(test_requirements, indent=2)}

DOMAIN: cloud-native

Please provide a detailed, technically sound architecture that addresses all requirements with specific technologies, detailed component specifications, and comprehensive implementation guidance."""

        # Call the LLM directly
        raw_response = await llm_service.call_llm(user_prompt, system_prompt, stage="architecture_analysis", provider_hint="deepseek")
        
        print(f"📄 Raw Response Length: {len(raw_response)} characters")
        print(f"📄 Raw Response (first 500 chars): {raw_response[:500]}")
        print(f"📄 Raw Response (last 500 chars): {raw_response[-500:]}")
        
        # Try to parse as JSON
        try:
            parsed = json.loads(raw_response)
            print("✅ JSON parsing successful!")
            print(f"📊 Parsed keys: {list(parsed.keys())}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"📄 Error at position: {e.pos}")
            print(f"📄 Context around error: {raw_response[max(0, e.pos-50):e.pos+50]}")
            
            # Try to extract JSON using the parser
            from app.modules.llm_response_parser import LLMResponseParser
            extracted = LLMResponseParser.extract_json(raw_response)
            print(f"🔧 Extracted JSON (first 500 chars): {extracted[:500]}")
            
            try:
                parsed_extracted = json.loads(extracted)
                print("✅ Extracted JSON parsing successful!")
                print(f"📊 Extracted keys: {list(parsed_extracted.keys())}")
            except json.JSONDecodeError as e2:
                print(f"❌ Extracted JSON parsing also failed: {e2}")
        
        # Save full response
        with open('debug_raw_llm_response.txt', 'w') as f:
            f.write(raw_response)
        print("💾 Full response saved to debug_raw_llm_response.txt")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(debug_raw_llm_response())
