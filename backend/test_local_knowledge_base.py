#!/usr/bin/env python3
"""
Test script to verify the local knowledge base service is working correctly.

This script tests the local knowledge base service without requiring external LLM services.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.local_knowledge_base_service import LocalKnowledgeBaseService
from loguru import logger


async def test_local_knowledge_base():
    """Test the local knowledge base service functionality."""
    
    logger.info("Starting local knowledge base service test...")
    
    try:
        # Initialize the service
        logger.info("Initializing Local Knowledge Base Service...")
        kb_service = LocalKnowledgeBaseService()
        
        # Check service status
        status = kb_service.get_service_status()
        capabilities = kb_service.get_service_capabilities()
        
        logger.info(f"✅ Service initialized successfully")
        logger.info(f"   - Embedder available: {status['embedder']}")
        logger.info(f"   - Graph available: {status['graph']}")
        logger.info(f"   - Embedding model: {capabilities['embedding_model']}")
        logger.info(f"   - Storage path: {capabilities['storage_path']}")
        
        # Test with mock analysis data
        logger.info("Testing with mock analysis data...")
        
        mock_analysis = {
            "repository_info": {
                "name": "archMesh",
                "url": "https://github.com/PocketPeer/archMesh",
                "description": "Architecture design and development platform"
            },
            "tech_stack": {
                "languages": {
                    "Python": 60,
                    "TypeScript": 30,
                    "JavaScript": 10
                },
                "frameworks": ["FastAPI", "Next.js", "React"],
                "databases": ["PostgreSQL", "Redis", "Neo4j"],
                "infrastructure": ["Docker", "Docker Compose"]
            },
            "architecture": {
                "architecture_style": "Microservices",
                "architecture_patterns": ["API Gateway", "Event-Driven"],
                "communication_patterns": ["REST API", "WebSocket"],
                "data_storage": {
                    "primary": "PostgreSQL",
                    "cache": "Redis",
                    "graph": "Neo4j"
                },
                "deployment": {
                    "strategy": "Containerized",
                    "orchestration": "Docker Compose"
                },
                "security": {
                    "authentication": "JWT",
                    "authorization": "Role-based"
                },
                "scalability": {
                    "horizontal": True,
                    "load_balancing": True
                }
            },
            "services": [
                {
                    "name": "API Gateway",
                    "type": "Gateway",
                    "technology": "FastAPI",
                    "responsibility": "Request routing and authentication",
                    "interfaces": ["REST API", "WebSocket"],
                    "dependencies": ["User Service", "Project Service"],
                    "scalability": "High"
                },
                {
                    "name": "User Service",
                    "type": "Microservice",
                    "technology": "FastAPI",
                    "responsibility": "User management and authentication",
                    "interfaces": ["REST API"],
                    "dependencies": ["Database"],
                    "scalability": "Medium"
                },
                {
                    "name": "Project Service",
                    "type": "Microservice",
                    "technology": "FastAPI",
                    "responsibility": "Project management and workflows",
                    "interfaces": ["REST API"],
                    "dependencies": ["User Service", "Database"],
                    "scalability": "Medium"
                }
            ]
        }
        
        # Test indexing
        logger.info("Testing repository analysis indexing...")
        index_result = await kb_service.index_repository_analysis(
            project_id="test-project-001",
            repository_url="https://github.com/PocketPeer/archMesh",
            analysis=mock_analysis
        )
        
        assert index_result["indexed_chunks"] > 0, "No chunks were indexed"
        assert index_result["total_vectors"] > 0, "No vectors were stored"
        
        logger.info(f"✅ Repository analysis indexed successfully")
        logger.info(f"   - Chunks indexed: {index_result['indexed_chunks']}")
        logger.info(f"   - Total vectors: {index_result['total_vectors']}")
        
        # Test semantic search
        logger.info("Testing semantic search...")
        search_results = await kb_service.search_similar_architectures(
            query="microservices architecture patterns",
            project_id="test-project-001",
            top_k=3
        )
        
        assert len(search_results) > 0, "No search results returned"
        assert all("score" in result for result in search_results), "Missing similarity scores"
        
        logger.info(f"✅ Semantic search completed successfully")
        logger.info(f"   - Results found: {len(search_results)}")
        logger.info(f"   - Top similarity score: {search_results[0]['score']:.3f}")
        
        # Test service dependencies
        logger.info("Testing service dependencies...")
        dependencies = await kb_service.get_service_dependencies("test-project-001")
        
        logger.info(f"✅ Service dependencies retrieved")
        logger.info(f"   - Services found: {len(dependencies)}")
        
        # Test architecture patterns
        logger.info("Testing architecture patterns...")
        patterns = await kb_service.get_architecture_patterns("test-project-001")
        
        logger.info(f"✅ Architecture patterns retrieved")
        logger.info(f"   - Patterns found: {len(patterns)}")
        
        # Test context generation
        logger.info("Testing context generation for new feature...")
        context = await kb_service.get_context_for_new_feature(
            project_id="test-project-001",
            feature_description="Add real-time notifications to the system"
        )
        
        assert "similar_features" in context, "Missing similar features"
        assert "existing_services" in context, "Missing existing services"
        assert "recommendations" in context, "Missing recommendations"
        
        logger.info(f"✅ Context generation completed successfully")
        logger.info(f"   - Similar features: {len(context['similar_features'])}")
        logger.info(f"   - Existing services: {len(context['existing_services'])}")
        logger.info(f"   - Integration approach: {context['recommendations'].get('integration_approach', 'Unknown')}")
        
        # Test multiple searches
        logger.info("Testing multiple search queries...")
        queries = [
            "API Gateway patterns",
            "database design",
            "authentication systems",
            "microservices communication"
        ]
        
        for query in queries:
            results = await kb_service.search_similar_architectures(
                query=query,
                project_id="test-project-001",
                top_k=2
            )
            logger.info(f"   - Query '{query}': {len(results)} results")
        
        logger.info("✅ Multiple search queries completed successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Local knowledge base test failed: {str(e)}")
        return False


async def main():
    """Main test function."""
    logger.info("=" * 60)
    logger.info("LOCAL KNOWLEDGE BASE SERVICE TEST")
    logger.info("=" * 60)
    logger.info("Testing local knowledge base service without external dependencies")
    logger.info("")
    
    success = await test_local_knowledge_base()
    
    if success:
        logger.info("")
        logger.info("✅ SUCCESS: Local knowledge base service is working correctly!")
        logger.info("   - Service initialization: ✅")
        logger.info("   - Repository indexing: ✅") 
        logger.info("   - Semantic search: ✅")
        logger.info("   - Service dependencies: ✅")
        logger.info("   - Architecture patterns: ✅")
        logger.info("   - Context generation: ✅")
        logger.info("   - Multiple searches: ✅")
        logger.info("")
        logger.info("The local knowledge base service is ready for brownfield analysis")
        logger.info("and can work without external vector databases or LLM services.")
    else:
        logger.error("")
        logger.error("❌ FAILURE: Local knowledge base service has issues")
        logger.error("   Please check the implementation and fix the problems.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
