#!/usr/bin/env python3
"""
Demo script for Brownfield Architecture Agent.

This script demonstrates how to use the updated Architecture Agent
with brownfield capabilities and RAG context integration.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.agents.architecture_agent import ArchitectureAgent
from app.services.knowledge_base_service import KnowledgeBaseService


async def demo_greenfield_architecture():
    """Demo greenfield architecture design."""
    print("=" * 60)
    print("GREENFIELD ARCHITECTURE DEMO")
    print("=" * 60)
    
    # Initialize agent without knowledge base service
    agent = ArchitectureAgent()
    
    # Sample requirements for greenfield project
    requirements = {
        "structured_requirements": {
            "business_goals": [
                "Build a modern e-commerce platform",
                "Support 10,000+ concurrent users",
                "Enable mobile and web access",
                "Integrate with payment gateways",
                "Provide real-time inventory management"
            ],
            "functional_requirements": [
                "User registration and authentication",
                "Product catalog with search and filtering",
                "Shopping cart and checkout process",
                "Order management and tracking",
                "Payment processing",
                "Inventory management",
                "Customer support system",
                "Admin dashboard"
            ],
            "non_functional_requirements": {
                "performance": [
                    "Page load time < 2 seconds",
                    "API response time < 500ms",
                    "Support 10,000 concurrent users"
                ],
                "security": [
                    "HTTPS encryption",
                    "PCI DSS compliance",
                    "Data encryption at rest"
                ],
                "scalability": [
                    "Horizontal scaling capability",
                    "Auto-scaling based on load",
                    "Microservices architecture"
                ]
            },
            "constraints": [
                "Must use cloud-native technologies",
                "Budget constraint: $50,000/month",
                "Team size: 8 developers",
                "Timeline: 6 months"
            ],
            "stakeholders": [
                {
                    "name": "Product Manager",
                    "role": "Product Owner",
                    "concerns": ["User experience", "Feature delivery", "Business value"]
                },
                {
                    "name": "CTO",
                    "role": "Technical Leader",
                    "concerns": ["Architecture quality", "Scalability", "Security"]
                }
            ]
        },
        "confidence_score": 0.85
    }
    
    # Input data for greenfield design
    input_data = {
        "requirements": requirements,
        "constraints": {
            "budget": "$50,000/month",
            "team_size": 8,
            "timeline": "6 months"
        },
        "preferences": ["microservices", "cloud-native", "containerized"],
        "domain": "e-commerce",
        "mode": "greenfield",
        "session_id": "demo-greenfield-001"
    }
    
    try:
        print("Designing greenfield architecture...")
        result = await agent.execute(input_data)
        
        print(f"✅ Architecture design completed!")
        print(f"Architecture Style: {result['architecture_overview']['style']}")
        print(f"Components: {len(result['components'])}")
        print(f"Quality Score: {result.get('quality_score', 'N/A')}")
        
        # Show some key components
        print("\nKey Components:")
        for component in result['components'][:3]:
            print(f"  - {component['name']} ({component['type']}): {component['description']}")
        
        # Show technology stack
        tech_stack = result.get('technology_stack', {})
        print(f"\nTechnology Stack:")
        for category, tech in tech_stack.items():
            if isinstance(tech, dict) and 'language' in tech:
                print(f"  - {category}: {tech['language']}")
            elif isinstance(tech, dict) and 'framework' in tech:
                print(f"  - {category}: {tech['framework']}")
            elif isinstance(tech, dict) and 'primary' in tech:
                print(f"  - {category}: {tech['primary']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in greenfield design: {str(e)}")
        return None


async def demo_brownfield_architecture():
    """Demo brownfield architecture design with RAG context."""
    print("\n" + "=" * 60)
    print("BROWNFIELD ARCHITECTURE DEMO")
    print("=" * 60)
    
    # Initialize knowledge base service (mock for demo)
    kb_service = KnowledgeBaseService()
    
    # Initialize agent with knowledge base service
    agent = ArchitectureAgent(knowledge_base_service=kb_service)
    
    # Sample existing architecture (from GitHub analysis)
    existing_architecture = {
        "services": [
            {
                "id": "user-service",
                "name": "User Service",
                "type": "service",
                "technology": "Node.js + Express",
                "description": "Handles user authentication and profiles",
                "endpoints": ["/api/users", "/api/auth"],
                "dependencies": ["user-database"]
            },
            {
                "id": "user-database",
                "name": "User Database",
                "type": "database",
                "technology": "PostgreSQL",
                "description": "Stores user data and authentication info"
            },
            {
                "id": "payment-service",
                "name": "Payment Service",
                "type": "service",
                "technology": "Java + Spring Boot",
                "description": "Processes payments and billing",
                "endpoints": ["/api/payments", "/api/billing"],
                "dependencies": ["payment-database"]
            },
            {
                "id": "payment-database",
                "name": "Payment Database",
                "type": "database",
                "technology": "MySQL",
                "description": "Stores payment and transaction data"
            }
        ],
        "technology_stack": {
            "Node.js": 1,
            "Java": 1,
            "PostgreSQL": 1,
            "MySQL": 1,
            "Express": 1,
            "Spring Boot": 1
        }
    }
    
    # New requirements for brownfield project
    requirements = {
        "structured_requirements": {
            "business_goals": [
                "Add real-time notifications to existing system",
                "Improve user engagement",
                "Support push notifications",
                "Integrate with existing user and payment services"
            ],
            "functional_requirements": [
                "Real-time notification delivery",
                "Email notification templates",
                "SMS notification support",
                "Push notification for mobile apps",
                "Notification preferences management",
                "Notification history and analytics",
                "Integration with existing user service",
                "Integration with payment service for transaction notifications"
            ],
            "non_functional_requirements": {
                "performance": [
                    "Notification delivery < 5 seconds",
                    "Support 1000 notifications/minute",
                    "99.9% uptime"
                ],
                "security": [
                    "Secure notification data",
                    "User privacy compliance",
                    "Rate limiting for notifications"
                ],
                "scalability": [
                    "Horizontal scaling for notification processing",
                    "Queue-based processing",
                    "Auto-scaling based on notification volume"
                ]
            },
            "constraints": [
                "Must integrate with existing services",
                "No breaking changes to existing APIs",
                "Use existing technology stack where possible",
                "Zero downtime deployment"
            ],
            "stakeholders": [
                {
                    "name": "Product Manager",
                    "role": "Product Owner",
                    "concerns": ["User engagement", "Feature integration", "Timeline"]
                },
                {
                    "name": "Backend Team Lead",
                    "role": "Technical Lead",
                    "concerns": ["Integration complexity", "System stability", "Performance"]
                }
            ]
        },
        "confidence_score": 0.90
    }
    
    # Input data for brownfield design
    input_data = {
        "requirements": requirements,
        "constraints": {
            "no_breaking_changes": True,
            "zero_downtime": True,
            "use_existing_tech": True
        },
        "preferences": ["microservices", "event-driven", "queue-based"],
        "domain": "e-commerce",
        "mode": "brownfield",
        "project_id": "demo-project-123",
        "existing_architecture": existing_architecture,
        "session_id": "demo-brownfield-001"
    }
    
    try:
        print("Designing brownfield architecture with RAG context...")
        result = await agent.execute(input_data)
        
        print(f"✅ Brownfield architecture design completed!")
        print(f"Architecture Style: {result['architecture_overview']['style']}")
        print(f"New Services: {len(result.get('new_services', []))}")
        print(f"Modified Services: {len(result.get('modified_services', []))}")
        print(f"Integration Phases: {len(result.get('integration_strategy', {}).get('phases', []))}")
        
        # Show new services
        new_services = result.get('new_services', [])
        if new_services:
            print("\nNew Services:")
            for service in new_services:
                print(f"  - {service['name']} ({service['type']}): {service['description']}")
                print(f"    Technology: {service.get('technology', 'N/A')}")
                print(f"    Dependencies: {', '.join(service.get('dependencies', []))}")
        
        # Show modified services
        modified_services = result.get('modified_services', [])
        if modified_services:
            print("\nModified Services:")
            for service in modified_services:
                print(f"  - {service['name']}: {', '.join(service.get('modifications', []))}")
                print(f"    Breaking Changes: {service.get('breaking_changes', False)}")
                print(f"    Migration Required: {service.get('migration_required', False)}")
        
        # Show integration strategy
        integration_strategy = result.get('integration_strategy', {})
        if integration_strategy:
            print(f"\nIntegration Strategy:")
            phases = integration_strategy.get('phases', [])
            for phase in phases:
                print(f"  Phase {phase.get('phase', 'N/A')}: {phase.get('name', 'N/A')}")
                print(f"    Duration: {phase.get('duration', 'N/A')}")
                print(f"    Services: {', '.join(phase.get('services', []))}")
        
        # Show impact analysis
        impact_analysis = result.get('impact_analysis', {})
        if impact_analysis:
            print(f"\nImpact Analysis:")
            print(f"  Risk Level: {impact_analysis.get('risk_level', 'N/A')}")
            print(f"  Breaking Changes: {impact_analysis.get('breaking_changes', False)}")
            print(f"  Downtime Required: {impact_analysis.get('downtime_required', False)}")
            print(f"  Data Migration: {impact_analysis.get('data_migration', False)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in brownfield design: {str(e)}")
        return None


async def demo_agent_capabilities():
    """Demo agent capabilities and metadata."""
    print("\n" + "=" * 60)
    print("AGENT CAPABILITIES DEMO")
    print("=" * 60)
    
    # Initialize agent
    agent = ArchitectureAgent()
    
    # Get capabilities
    capabilities = agent.get_agent_capabilities()
    
    print("Agent Information:")
    print(f"  Type: {capabilities['agent_type']}")
    print(f"  Version: {capabilities['agent_version']}")
    print(f"  Modes: {', '.join(capabilities['modes'])}")
    print(f"  Knowledge Base Integration: {capabilities['knowledge_base_integration']}")
    
    print(f"\nCapabilities:")
    for capability in capabilities['capabilities']:
        print(f"  - {capability}")
    
    print(f"\nArchitecture Patterns:")
    for pattern in capabilities['architecture_patterns']:
        print(f"  - {pattern}")
    
    print(f"\nTechnology Categories:")
    for category in capabilities['technology_categories']:
        print(f"  - {category}")


async def main():
    """Main demo function."""
    print("ArchMesh Architecture Agent - Brownfield Demo")
    print("=" * 60)
    
    try:
        # Demo agent capabilities
        await demo_agent_capabilities()
        
        # Demo greenfield architecture
        greenfield_result = await demo_greenfield_architecture()
        
        # Demo brownfield architecture
        brownfield_result = await demo_brownfield_architecture()
        
        # Summary
        print("\n" + "=" * 60)
        print("DEMO SUMMARY")
        print("=" * 60)
        
        if greenfield_result:
            print("✅ Greenfield architecture design: SUCCESS")
            print(f"   - Style: {greenfield_result['architecture_overview']['style']}")
            print(f"   - Components: {len(greenfield_result['components'])}")
        else:
            print("❌ Greenfield architecture design: FAILED")
        
        if brownfield_result:
            print("✅ Brownfield architecture design: SUCCESS")
            print(f"   - Style: {brownfield_result['architecture_overview']['style']}")
            print(f"   - New Services: {len(brownfield_result.get('new_services', []))}")
            print(f"   - Integration Phases: {len(brownfield_result.get('integration_strategy', {}).get('phases', []))}")
        else:
            print("❌ Brownfield architecture design: FAILED")
        
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
