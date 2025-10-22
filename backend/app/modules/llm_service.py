"""
Simple LLM Service for the modular ArchMesh system
"""

import json
import os
from typing import Dict, Any, List, Optional
import httpx
from loguru import logger
from dotenv import load_dotenv
from app.modules.admin.llm_logger import log_interaction
from app.modules.llm_response_parser import LLMResponseParser
from app.modules.admin.model_manager import ModelManager

# Load environment variables
load_dotenv()


class SimpleLLMService:
    """
    Simple LLM service for the modular system.
    Uses the configured API keys to make real LLM calls.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.deepseek_base_url = os.getenv("DEEPSEEK_BASE_URL", "http://localhost:11434")
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-r1:latest")
        self.fast_local_model = os.getenv("OLLAMA_FAST_MODEL", os.getenv("OLLAMA_MODEL", "llama3.2:3b"))
        self.model_manager = ModelManager()
        
    async def call_llm(self, prompt: str, system_prompt: str = "", model: str = "gpt-4o-mini", *, stage: str = "general", provider_hint: Optional[str] = None) -> str:
        """
        Make a simple LLM call using the configured provider.
        """
        try:
            # Try DeepSeek first (local, cost-effective, preferred for development)
            if self.deepseek_base_url and (provider_hint in (None, "deepseek", "ollama")):
                result = await self._call_deepseek(prompt, system_prompt)
                log_interaction({
                    "stage": stage,
                    "provider": "deepseek",
                    "model": self.deepseek_model,
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "response": result,
                })
                return result
            
            # Try OpenAI as fallback (most reliable)
            elif self.openai_api_key and (provider_hint == "openai" or model.startswith("gpt")):
                result = await self._call_openai(prompt, system_prompt, model)
                log_interaction({
                    "stage": stage,
                    "provider": "openai",
                    "model": model,
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "response": result,
                })
                return result
            
            # Try Anthropic as fallback
            elif self.anthropic_api_key and (provider_hint in (None, "anthropic")):
                result = await self._call_anthropic(prompt, system_prompt)
                log_interaction({
                    "stage": stage,
                    "provider": "anthropic",
                    "model": "claude-3-sonnet-20240229",
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "response": result,
                })
                return result
            
            else:
                logger.warning("No LLM provider available, using fallback")
                return self._fallback_response(prompt)
                
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            logger.error(f"LLM call failed - Exception type: {type(e).__name__}")
            logger.error(f"LLM call failed - Exception details: {str(e)}")
            import traceback
            logger.error(f"LLM call failed - Traceback: {traceback.format_exc()}")
            log_interaction({
                "stage": stage,
                "provider": provider_hint or "auto",
                "model": model,
                "prompt": prompt,
                "system_prompt": system_prompt,
                "error": str(e),
            })
            return self._fallback_response(prompt)
    
    async def _call_openai(self, prompt: str, system_prompt: str, model: str) -> str:
        """Call OpenAI API"""
        # Get timeout from model manager
        model_config = self.model_manager.get_model_by_id(model)
        timeout = model_config.timeout_seconds if model_config else 30
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000
                },
                timeout=httpx.Timeout(timeout)
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_openai_response(data)
            else:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
    
    def _parse_openai_response(self, data: dict) -> str:
        """Parse OpenAI API response"""
        return LLMResponseParser.parse_openai(data)
    
    async def _call_deepseek(self, prompt: str, system_prompt: str) -> str:
        """Call DeepSeek API (local Ollama) with retry and fast-model fallback."""
        # Get timeout from model manager
        model_config = self.model_manager.get_model_by_id("deepseek-r1")
        default_timeout = model_config.timeout_seconds if model_config else 300
        
        async def _call_model(model: str, timeout_s: float = None) -> str:
            if timeout_s is None:
                timeout_s = default_timeout
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.deepseek_base_url}/api/chat",
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 8000,
                            "format": "json"
                        }
                    },
                    timeout=httpx.Timeout(timeout_s)
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return self._parse_ollama_response(data)
                raise Exception(f"Ollama API error {resp.status_code}: {resp.text}")

        # Try fast local model first (more reliable)
        try:
            logger.info(f"Using fast local model: {self.fast_local_model}")
            out = await _call_model(self.fast_local_model, timeout_s=60.0)
            if out and len(out.strip()) > 2:
                return out
        except Exception as e:
            logger.warning(f"Fast local model failed: {e}")

        # Try DeepSeek as fallback
        last_err: Exception | None = None
        for attempt in range(2):
            try:
                out = await _call_model(self.deepseek_model)
                if out and len(out.strip()) > 2:
                    return out
            except Exception as e:
                last_err = e
                logger.warning(f"DeepSeek attempt {attempt+1} failed: {e}")

        raise Exception(f"All model calls failed: {last_err}")
    
    async def _call_anthropic(self, prompt: str, system_prompt: str) -> str:
        """Call Anthropic API"""
        # Get timeout from model manager
        model_config = self.model_manager.get_model_by_id("claude-3-sonnet-20240229")
        timeout = model_config.timeout_seconds if model_config else 30
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": 2000,
                    "temperature": 0.3,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=httpx.Timeout(timeout)
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_anthropic_response(data)
            else:
                raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
    
    def _parse_ollama_response(self, data: dict) -> str:
        """Parse Ollama API response (DeepSeek, Llama, etc.)"""
        return LLMResponseParser.parse_ollama(data)
    
    def _parse_anthropic_response(self, data: dict) -> str:
        """Parse Anthropic API response"""
        return LLMResponseParser.parse_anthropic(data)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when no LLM is available"""
        return f"LLM service unavailable. Original prompt: {prompt[:100]}..."
    
    async def extract_requirements(self, text: str) -> Dict[str, Any]:
        """
        Extract requirements using LLM with enhanced depth and technical analysis.
        """
        system_prompt = """You are an expert requirements analyst. Extract requirements from the given text and return a JSON response with this structure:

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

Extract relevant requirements from the text. Be thorough and accurate."""

        user_prompt = f"Analyze the following text and extract comprehensive requirements with technical depth:\n\n{text}"
        
        try:
            response = await self.call_llm(user_prompt, system_prompt + "\n\nReturn ONLY valid JSON. No Markdown, no prose.", stage="requirements_extraction", provider_hint="deepseek")
            
            return LLMResponseParser.parse_json_response(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response: {response}")
            return self._fallback_requirements(text)
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._fallback_requirements(text)
    
    async def generate_architecture_analysis(self, requirements: Dict[str, Any], domain: str = "cloud-native") -> Dict[str, Any]:
        """
        Generate comprehensive architecture analysis using LLM.
        """
        system_prompt = f"""You are an expert system architect and technical lead. Generate a comprehensive architecture analysis for a {domain} system based on the provided requirements. Return a JSON response with the following structure:

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
7. Risk assessment and mitigation"""

        user_prompt = f"""Generate a comprehensive architecture analysis for the following requirements:

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

DOMAIN: {domain}

Please provide a detailed, technically sound architecture that addresses all requirements with specific technologies, detailed component specifications, and comprehensive implementation guidance."""

        try:
            response = await self.call_llm(user_prompt, system_prompt + "\n\nReturn ONLY valid JSON. No Markdown, no prose.", stage="architecture_analysis", provider_hint="deepseek")
            
            return LLMResponseParser.parse_json_response(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM architecture response as JSON: {e}")
            logger.error(f"Response: {response}")
            return self._fallback_architecture_analysis(requirements, domain)
        except Exception as e:
            logger.error(f"LLM architecture analysis failed: {e}")
            return self._fallback_architecture_analysis(requirements, domain)

    def _parse_json_response(self, text: str) -> str:
        """Extract JSON from LLM response using the new parser"""
        return LLMResponseParser.extract_json(text)

    def _fallback_requirements(self, text: str) -> Dict[str, Any]:
        """Fallback requirements extraction using simple patterns"""
        return {
            "business_goals": [
                {
                    "id": "bg_1",
                    "title": "Business Goal",
                    "description": "Extracted from text analysis",
                    "priority": "medium",
                    "confidence": 0.5
                }
            ],
            "functional_requirements": [
                {
                    "id": "fr_1",
                    "title": "Functional Requirement",
                    "description": "System functionality requirement",
                    "priority": "high",
                    "confidence": 0.6
                }
            ],
            "non_functional_requirements": [
                {
                    "id": "nfr_1",
                    "title": "Performance Requirement",
                    "description": "System performance requirement",
                    "priority": "medium",
                    "confidence": 0.5
                }
            ],
            "constraints": [],
            "stakeholders": [
                {
                    "id": "s_1",
                    "title": "Users",
                    "description": "System users",
                    "priority": "high",
                    "confidence": 0.7
                }
            ]
        }

    def _fallback_architecture_analysis(self, requirements: Dict[str, Any], domain: str) -> Dict[str, Any]:
        """Fallback architecture analysis when LLM fails"""
        return {
            "architecture_overview": {
                "name": f"{domain.title()} System Architecture",
                "style": "microservices",
                "description": "Fallback architecture analysis",
                "rationale": "Simple microservices architecture",
                "quality_attributes": ["scalability", "maintainability"]
            },
            "components": [
                {
                    "id": "comp_1",
                    "name": "API Gateway",
                    "type": "gateway",
                    "description": "Central entry point for all requests",
                    "responsibilities": ["Request routing", "Authentication"],
                    "technologies": ["Kong", "Nginx"],
                    "interfaces": [],
                    "dependencies": [],
                    "scalability": "Horizontal scaling",
                    "security_considerations": ["Rate limiting", "SSL termination"],
                    "performance_characteristics": {
                        "expected_load": "1000 req/s",
                        "response_time": "50ms",
                        "resource_requirements": "1 CPU, 2GB RAM"
                    },
                    "data_model": {
                        "entities": [],
                        "relationships": [],
                        "storage_requirements": "Minimal"
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
