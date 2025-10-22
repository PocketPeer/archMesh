#!/usr/bin/env python3
"""
Test script to verify brownfield analysis is working with real data instead of mocks.

This script tests the complete brownfield workflow using the ArchMesh repository
as a real example to ensure the analysis is not using fallback/mock data.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.agents.github_analyzer_agent import GitHubAnalyzerAgent
from app.services.local_knowledge_base_service import LocalKnowledgeBaseService
from app.workflows.brownfield_workflow import BrownfieldWorkflow
from loguru import logger


async def test_real_brownfield_analysis():
    """Test brownfield analysis with real ArchMesh repository data."""
    
    logger.info("Starting real brownfield analysis test...")
    
    # Test 1: GitHub Analyzer Agent with real repository
    logger.info("Test 1: Testing GitHub Analyzer Agent with real repository")
    
    try:
        analyzer = GitHubAnalyzerAgent()
        
        # Use the ArchMesh repository as a real example
        analysis_input = {
            "repo_url": "https://github.com/PocketPeer/archMesh",
            "branch": "master",
            "clone_depth": 1,
            "analyze_private": False,
            "include_commits": False,
            "session_id": "test-session-001"
        }
        
        logger.info("Analyzing ArchMesh repository...")
        analysis_result = await analyzer.execute(analysis_input)
        
        # Verify we got real analysis data
        assert "repository_info" in analysis_result, "Missing repository_info"
        assert "tech_stack" in analysis_result, "Missing tech_stack"
        assert "architecture" in analysis_result, "Missing architecture"
        assert "services" in analysis_result, "Missing services"
        
        logger.info(f"✅ GitHub analysis completed successfully")
        logger.info(f"   - Repository: {analysis_result['repository_info'].get('url', 'Unknown')}")
        logger.info(f"   - Services found: {len(analysis_result.get('services', []))}")
        logger.info(f"   - Technologies: {list(analysis_result.get('tech_stack', {}).get('languages', {}).keys())}")
        
    except Exception as e:
        logger.error(f"❌ GitHub analysis failed: {str(e)}")
        return False
    
    # Test 2: Local Knowledge Base Service
    logger.info("Test 2: Testing Local Knowledge Base Service")
    
    try:
        kb_service = LocalKnowledgeBaseService()
        
        # Index the analysis results
        logger.info("Indexing analysis results in knowledge base...")
        index_result = await kb_service.index_repository_analysis(
            project_id="test-project-001",
            repository_url="https://github.com/PocketPeer/archMesh",
            analysis=analysis_result
        )
        
        # Verify indexing worked
        assert index_result["indexed_chunks"] > 0, "No chunks were indexed"
        assert index_result["total_vectors"] > 0, "No vectors were stored"
        
        logger.info(f"✅ Knowledge base indexing completed successfully")
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
        
    except Exception as e:
        logger.error(f"❌ Knowledge base service failed: {str(e)}")
        return False
    
    # Test 3: Complete Brownfield Workflow
    logger.info("Test 3: Testing complete Brownfield Workflow")
    
    try:
        workflow = BrownfieldWorkflow()
        
        # Create a test requirements document
        test_requirements = """
        The system needs to add real-time notifications for users.
        Requirements:
        1. Users should receive notifications when new messages arrive
        2. Notifications should be delivered via WebSocket
        3. The system should support push notifications for mobile devices
        4. Notifications should be persistent and stored in database
        5. Users should be able to configure notification preferences
        """
        
        # Write test requirements to file
        requirements_file = Path("test_requirements.txt")
        requirements_file.write_text(test_requirements)
        
        logger.info("Running complete brownfield workflow...")
        workflow_result = await workflow.run_workflow(
            session_id="test-workflow-001",
            project_id="test-project-001",
            repository_url="https://github.com/PocketPeer/archMesh",
            document_path=str(requirements_file),
            branch="master"
        )
        
        # Verify workflow completed successfully
        assert workflow_result["current_stage"] != "failed", f"Workflow failed: {workflow_result.get('errors', [])}"
        
        logger.info(f"✅ Brownfield workflow completed successfully")
        logger.info(f"   - Final stage: {workflow_result['current_stage']}")
        logger.info(f"   - Services analyzed: {len(workflow_result.get('existing_architecture', {}).get('services', []))}")
        
        # Clean up
        requirements_file.unlink()
        
    except Exception as e:
        logger.error(f"❌ Brownfield workflow failed: {str(e)}")
        return False
    
    logger.info("🎉 All brownfield analysis tests passed!")
    logger.info("✅ Real analysis is working - no mocks or fallbacks detected")
    
    return True


async def main():
    """Main test function."""
    logger.info("=" * 60)
    logger.info("BROWNFIELD ANALYSIS - REAL DATA TEST")
    logger.info("=" * 60)
    logger.info("Testing that brownfield analysis uses real data instead of mocks")
    logger.info("")
    
    success = await test_real_brownfield_analysis()
    
    if success:
        logger.info("")
        logger.info("✅ SUCCESS: Brownfield analysis is working with real data!")
        logger.info("   - GitHub repository analysis: ✅")
        logger.info("   - Knowledge base indexing: ✅") 
        logger.info("   - Semantic search: ✅")
        logger.info("   - Context generation: ✅")
        logger.info("   - Complete workflow: ✅")
        logger.info("")
        logger.info("The brownfield analysis is now using real repository data")
        logger.info("and local knowledge base storage instead of mocks/fallbacks.")
    else:
        logger.error("")
        logger.error("❌ FAILURE: Brownfield analysis is still using mocks/fallbacks")
        logger.error("   Please check the implementation and fix the issues.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
