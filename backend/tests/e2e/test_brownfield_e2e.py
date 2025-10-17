"""
End-to-end tests for the complete brownfield workflow.

These tests verify the entire brownfield workflow from API calls
through to final architecture generation.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
import json

from app.workflows.brownfield_workflow import BrownfieldWorkflow
from app.agents.github_analyzer_agent import GitHubAnalyzerAgent
from app.agents.requirements_agent import RequirementsAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.services.knowledge_base_service import KnowledgeBaseService


class TestBrownfieldE2E:
    """End-to-end tests for the complete brownfield workflow."""

    @pytest.fixture
    def mock_github_analysis_result(self):
        """Mock GitHub analysis result."""
        return {
            'repository_url': 'https://github.com/test/e-commerce-platform',
            'branch': 'main',
            'services': [
                {
                    'id': 'user-service',
                    'name': 'User Service',
                    'type': 'service',
                    'technology': 'Node.js + Express',
                    'description': 'Handles user authentication and profiles',
                    'endpoints': ['/api/users', '/api/auth'],
                    'dependencies': ['user-database']
                },
                {
                    'id': 'user-database',
                    'name': 'User Database',
                    'type': 'database',
                    'technology': 'PostgreSQL',
                    'description': 'Stores user data and authentication info'
                },
                {
                    'id': 'payment-service',
                    'name': 'Payment Service',
                    'type': 'service',
                    'technology': 'Java + Spring Boot',
                    'description': 'Processes payments and billing',
                    'endpoints': ['/api/payments', '/api/billing'],
                    'dependencies': ['payment-database']
                }
            ],
            'dependencies': [
                {
                    'from': 'user-service',
                    'to': 'user-database',
                    'type': 'database-call',
                    'description': 'User service reads/writes to user database'
                },
                {
                    'from': 'payment-service',
                    'to': 'user-service',
                    'type': 'api-call',
                    'description': 'Payment service validates users via user service'
                }
            ],
            'technology_stack': {
                'Node.js': 1,
                'Java': 1,
                'PostgreSQL': 1,
                'Express': 1,
                'Spring Boot': 1
            },
            'quality_score': 0.85,
            'analysis_metadata': {
                'analyzed_at': '2023-01-01T00:00:00Z',
                'services_count': 3,
                'dependencies_count': 2,
                'technologies_detected': ['Node.js', 'Java', 'PostgreSQL', 'Express', 'Spring Boot']
            }
        }

    @pytest.fixture
    def mock_requirements_result(self):
        """Mock requirements analysis result."""
        return {
            'structured_requirements': {
                'business_goals': [
                    'Improve user experience with real-time notifications',
                    'Increase system reliability and performance'
                ],
                'functional_requirements': [
                    'Add real-time notification system for order updates',
                    'Implement user preference management',
                    'Add email and SMS notification capabilities'
                ],
                'non_functional_requirements': {
                    'performance': [
                        'Notification delivery time < 5 seconds',
                        'System should handle 10k concurrent notifications'
                    ],
                    'security': [
                        'Secure notification delivery',
                        'User consent for notifications'
                    ],
                    'scalability': [
                        'Support 100k users',
                        'Horizontal scaling capability'
                    ],
                    'reliability': [
                        '99.9% uptime for notification service',
                        'Message delivery guarantee'
                    ]
                },
                'constraints': [
                    'Must integrate with existing e-commerce platform',
                    'No downtime during deployment',
                    'Budget constraint: $50k for implementation'
                ],
                'stakeholders': [
                    {
                        'name': 'Product Manager',
                        'role': 'Product Owner',
                        'concerns': ['User experience', 'Feature delivery timeline']
                    },
                    {
                        'name': 'Engineering Team',
                        'role': 'Development Team',
                        'concerns': ['Technical feasibility', 'Integration complexity']
                    }
                ]
            },
            'confidence_score': 0.92,
            'status': 'completed'
        }

    @pytest.fixture
    def mock_architecture_result(self):
        """Mock architecture design result."""
        return {
            'architecture_overview': {
                'style': 'microservices',
                'integration_approach': 'Event-driven integration with message queues',
                'rationale': 'Extends existing microservices architecture with notification capabilities using event-driven patterns for minimal disruption'
            },
            'new_services': [
                {
                    'id': 'notification-service',
                    'name': 'Notification Service',
                    'type': 'service',
                    'technology': 'Node.js + Express',
                    'description': 'Handles real-time notifications via email, SMS, and push notifications',
                    'endpoints': ['/api/notifications', '/api/templates', '/api/preferences'],
                    'dependencies': ['notification-database', 'message-queue', 'email-service', 'sms-service']
                },
                {
                    'id': 'notification-database',
                    'name': 'Notification Database',
                    'type': 'database',
                    'technology': 'MongoDB',
                    'description': 'Stores notification templates, delivery status, and user preferences'
                },
                {
                    'id': 'message-queue',
                    'name': 'Message Queue',
                    'type': 'component',
                    'technology': 'Apache Kafka',
                    'description': 'Handles asynchronous message processing for notifications and events'
                }
            ],
            'modified_services': [
                {
                    'id': 'user-service',
                    'name': 'User Service',
                    'type': 'service',
                    'technology': 'Node.js + Express',
                    'description': 'Enhanced with notification preferences and event publishing capabilities',
                    'endpoints': ['/api/users', '/api/auth', '/api/preferences'],
                    'dependencies': ['user-database', 'message-queue']
                },
                {
                    'id': 'payment-service',
                    'name': 'Payment Service',
                    'type': 'service',
                    'technology': 'Java + Spring Boot',
                    'description': 'Enhanced to publish payment events for order notifications',
                    'endpoints': ['/api/payments', '/api/billing'],
                    'dependencies': ['payment-database', 'message-queue']
                }
            ],
            'integration_points': [
                {
                    'from_service': 'user-service',
                    'to_service': 'message-queue',
                    'type': 'event-stream',
                    'description': 'Publishes user events (registration, profile updates) for notification processing',
                    'implementation_notes': 'Use event sourcing pattern for reliable delivery'
                },
                {
                    'from_service': 'payment-service',
                    'to_service': 'message-queue',
                    'type': 'event-stream',
                    'description': 'Publishes payment events (success, failure) for order notifications',
                    'implementation_notes': 'Add event publishing to existing payment flow'
                },
                {
                    'from_service': 'notification-service',
                    'to_service': 'message-queue',
                    'type': 'message-queue',
                    'description': 'Consumes user and payment events to trigger notifications',
                    'implementation_notes': 'Implement idempotent processing for reliability'
                }
            ],
            'impact_analysis': {
                'risk_level': 'medium',
                'breaking_changes': False,
                'downtime_required': False
            },
            'integration_strategy': {
                'phases': [
                    {
                        'phase': 1,
                        'name': 'Infrastructure Setup',
                        'description': 'Deploy message queue and notification database',
                        'duration': '1-2 weeks',
                        'services': ['message-queue', 'notification-database'],
                        'steps': [
                            'Deploy Kafka cluster',
                            'Setup MongoDB for notifications',
                            'Configure monitoring and logging'
                        ],
                        'rollback': 'Remove Kafka and MongoDB instances'
                    },
                    {
                        'phase': 2,
                        'name': 'Notification Service Deployment',
                        'description': 'Deploy and configure notification service',
                        'duration': '2-3 weeks',
                        'services': ['notification-service'],
                        'steps': [
                            'Deploy notification service',
                            'Configure email and SMS providers',
                            'Setup notification templates',
                            'Implement user preference management'
                        ],
                        'rollback': 'Remove notification service and disable event publishing'
                    },
                    {
                        'phase': 3,
                        'name': 'Integration and Testing',
                        'description': 'Integrate with existing services and comprehensive testing',
                        'duration': '2-3 weeks',
                        'services': ['user-service', 'payment-service'],
                        'steps': [
                            'Add event publishing to user service',
                            'Add event publishing to payment service',
                            'Integration testing',
                            'Performance testing',
                            'User acceptance testing'
                        ],
                        'rollback': 'Remove event publishing and revert service changes'
                    }
                ],
                'testing_strategy': [
                    'Unit testing for all new services',
                    'Integration testing for event flows',
                    'Performance testing for message queue',
                    'End-to-end testing for notification delivery',
                    'Load testing for concurrent notifications'
                ],
                'monitoring': [
                    'Enhanced logging for all services',
                    'Performance metrics for message queue',
                    'Notification delivery tracking',
                    'Error rate monitoring',
                    'User engagement metrics'
                ],
                'rollback_plan': 'Remove new services, disable event publishing, revert existing service changes'
            }
        }

    @pytest.fixture
    def mock_agents_and_services(self, mock_github_analysis_result, mock_requirements_result, mock_architecture_result):
        """Create mock agents and services for E2E testing."""
        # Mock GitHub Analyzer
        github_analyzer = Mock(spec=GitHubAnalyzerAgent)
        github_analyzer.execute = AsyncMock(return_value=mock_github_analysis_result)
        
        # Mock Requirements Agent
        requirements_agent = Mock(spec=RequirementsAgent)
        requirements_agent.execute = AsyncMock(return_value=mock_requirements_result)
        
        # Mock Architecture Agent
        architecture_agent = Mock(spec=ArchitectureAgent)
        architecture_agent.execute = AsyncMock(return_value=mock_architecture_result)
        
        # Mock Knowledge Base Service
        kb_service = Mock(spec=KnowledgeBaseService)
        kb_service.index_repository_analysis = AsyncMock(return_value={
            'indexed_chunks': 15,
            'created_nodes': 8,
            'created_relationships': 5
        })
        kb_service.search_similar_architectures = AsyncMock(return_value=[
            {
                'id': 'similar-arch-1',
                'similarity_score': 0.88,
                'metadata': {
                    'project_id': 'similar-project',
                    'architecture_type': 'microservices',
                    'technologies': ['Node.js', 'Kafka', 'MongoDB']
                }
            }
        ])
        kb_service.get_service_dependencies = AsyncMock(return_value=[
            {
                'service': {'name': 'user-service', 'technology': 'Node.js'},
                'dependencies': [
                    {'name': 'user-database', 'type': 'database-call'}
                ]
            }
        ])
        kb_service.get_context_for_new_feature = AsyncMock(return_value={
            'similar_features': [
                {
                    'feature_name': 'user-notifications',
                    'implementation_approach': 'event-driven',
                    'technologies_used': ['Node.js', 'Kafka', 'MongoDB']
                }
            ],
            'existing_services': mock_github_analysis_result['services'],
            'integration_patterns': [
                {
                    'pattern': 'event-driven',
                    'description': 'Use message queues for async communication',
                    'confidence': 0.9
                }
            ],
            'recommendations': [
                'Use event-driven architecture for notifications',
                'Implement message queues for reliability',
                'Consider MongoDB for notification storage'
            ]
        })
        
        return {
            'github_analyzer': github_analyzer,
            'requirements_agent': requirements_agent,
            'architecture_agent': architecture_agent,
            'kb_service': kb_service
        }

    @pytest.mark.asyncio
    async def test_complete_brownfield_workflow(self, mock_agents_and_services):
        """Test the complete brownfield workflow from start to finish."""
        # Setup workflow with mocked agents
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents_and_services['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents_and_services['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents_and_services['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents_and_services['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Initial state
            initial_state = {
                'session_id': 'e2e-test-session',
                'project_id': 'e2e-test-project',
                'repository_url': 'https://github.com/test/e-commerce-platform',
                'branch': 'main',
                'document_path': 'requirements.txt',
                'current_stage': 'starting',
                'errors': [],
                'warnings': [],
                'feedback_history': [],
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            # Run the complete workflow
            final_state = await workflow.run_workflow(initial_state)
            
            # Verify final state
            assert final_state['current_stage'] == 'completed'
            assert 'existing_architecture' in final_state
            assert 'requirements' in final_state
            assert 'proposed_architecture' in final_state
            assert 'integration_strategy' in final_state
            assert 'implementation_plan' in final_state
            assert 'workflow_summary' in final_state
            
            # Verify workflow summary
            summary = final_state['workflow_summary']
            assert summary['workflow_status'] == 'completed'
            assert 'deliverables' in summary
            assert 'quality_metrics' in summary
            
            # Verify deliverables
            deliverables = summary['deliverables']
            assert 'existing_architecture_analysis' in deliverables
            assert 'structured_requirements' in deliverables
            assert 'proposed_architecture' in deliverables
            assert 'integration_strategy' in deliverables
            assert 'implementation_plan' in deliverables
            
            # Verify quality metrics
            quality_metrics = summary['quality_metrics']
            assert 'requirements_confidence' in quality_metrics
            assert 'architecture_quality' in quality_metrics
            assert 'integration_complexity' in quality_metrics
            assert 'risk_assessment' in quality_metrics

    @pytest.mark.asyncio
    async def test_workflow_with_human_review_approval(self, mock_agents_and_services):
        """Test workflow with human review and approval."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents_and_services['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents_and_services['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents_and_services['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents_and_services['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Mock human feedback for requirements review
            def mock_requirements_review(state):
                return {
                    **state,
                    'approval_status': 'approved',
                    'human_feedback': {
                        'reviewer': 'Product Manager',
                        'decision': 'approved',
                        'comments': 'Requirements look good, proceed with architecture design',
                        'timestamp': '2023-01-01T00:00:00Z'
                    },
                    'feedback_history': [
                        {
                            'stage': 'requirements_review',
                            'reviewer': 'Product Manager',
                            'decision': 'approved',
                            'comments': 'Requirements look good, proceed with architecture design',
                            'timestamp': '2023-01-01T00:00:00Z'
                        }
                    ],
                    'current_stage': 'requirements_reviewed'
                }
            
            # Mock human feedback for integration review
            def mock_integration_review(state):
                return {
                    **state,
                    'approval_status': 'approved',
                    'human_feedback': {
                        'reviewer': 'Engineering Team Lead',
                        'decision': 'approved',
                        'comments': 'Architecture design is solid, integration strategy is well thought out',
                        'timestamp': '2023-01-01T00:00:00Z'
                    },
                    'feedback_history': state['feedback_history'] + [
                        {
                            'stage': 'integration_review',
                            'reviewer': 'Engineering Team Lead',
                            'decision': 'approved',
                            'comments': 'Architecture design is solid, integration strategy is well thought out',
                            'timestamp': '2023-01-01T00:00:00Z'
                        }
                    ],
                    'current_stage': 'integration_reviewed'
                }
            
            # Patch the review methods
            workflow._human_review_requirements_node = AsyncMock(side_effect=mock_requirements_review)
            workflow._human_review_integration_node = AsyncMock(side_effect=mock_integration_review)
            
            # Initial state
            initial_state = {
                'session_id': 'e2e-review-session',
                'project_id': 'e2e-review-project',
                'repository_url': 'https://github.com/test/e-commerce-platform',
                'branch': 'main',
                'document_path': 'requirements.txt',
                'current_stage': 'starting',
                'errors': [],
                'warnings': [],
                'feedback_history': [],
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            # Run the workflow
            final_state = await workflow.run_workflow(initial_state)
            
            # Verify human feedback was captured
            assert len(final_state['feedback_history']) == 2
            assert final_state['feedback_history'][0]['stage'] == 'requirements_review'
            assert final_state['feedback_history'][1]['stage'] == 'integration_review'
            assert final_state['current_stage'] == 'completed'

    @pytest.mark.asyncio
    async def test_workflow_with_human_review_rejection(self, mock_agents_and_services):
        """Test workflow with human review rejection."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents_and_services['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents_and_services['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents_and_services['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents_and_services['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Mock human feedback rejection for requirements review
            def mock_requirements_rejection(state):
                return {
                    **state,
                    'approval_status': 'rejected',
                    'human_feedback': {
                        'reviewer': 'Product Manager',
                        'decision': 'rejected',
                        'comments': 'Requirements are too vague, need more specific details',
                        'timestamp': '2023-01-01T00:00:00Z'
                    },
                    'feedback_history': [
                        {
                            'stage': 'requirements_review',
                            'reviewer': 'Product Manager',
                            'decision': 'rejected',
                            'comments': 'Requirements are too vague, need more specific details',
                            'timestamp': '2023-01-01T00:00:00Z'
                        }
                    ],
                    'current_stage': 'failed'
                }
            
            # Patch the review method
            workflow._human_review_requirements_node = AsyncMock(side_effect=mock_requirements_rejection)
            
            # Initial state
            initial_state = {
                'session_id': 'e2e-rejection-session',
                'project_id': 'e2e-rejection-project',
                'repository_url': 'https://github.com/test/e-commerce-platform',
                'branch': 'main',
                'document_path': 'requirements.txt',
                'current_stage': 'starting',
                'errors': [],
                'warnings': [],
                'feedback_history': [],
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            # Run the workflow
            final_state = await workflow.run_workflow(initial_state)
            
            # Verify workflow failed due to rejection
            assert final_state['current_stage'] == 'failed'
            assert final_state['approval_status'] == 'rejected'
            assert len(final_state['feedback_history']) == 1
            assert final_state['feedback_history'][0]['decision'] == 'rejected'

    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, mock_agents_and_services):
        """Test workflow error handling and recovery."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents_and_services['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents_and_services['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents_and_services['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents_and_services['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Mock GitHub analyzer to raise an exception
            mock_agents_and_services['github_analyzer'].execute = AsyncMock(
                side_effect=Exception('GitHub analysis failed')
            )
            
            # Initial state
            initial_state = {
                'session_id': 'e2e-error-session',
                'project_id': 'e2e-error-project',
                'repository_url': 'https://github.com/test/e-commerce-platform',
                'branch': 'main',
                'current_stage': 'starting',
                'errors': [],
                'warnings': [],
                'feedback_history': [],
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            # Run the workflow
            final_state = await workflow.run_workflow(initial_state)
            
            # Verify error handling
            assert final_state['current_stage'] == 'failed'
            assert len(final_state['errors']) > 0
            assert 'GitHub analysis failed' in final_state['errors'][0]

    @pytest.mark.asyncio
    async def test_workflow_status_monitoring(self, mock_agents_and_services):
        """Test workflow status monitoring and checkpointing."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents_and_services['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents_and_services['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents_and_services['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents_and_services['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Mock the graph state for status checking
            mock_state = Mock()
            mock_state.values = {
                'current_stage': 'integration_designed',
                'errors': [],
                'warnings': [],
                'updated_at': '2023-01-01T00:00:00Z',
                'existing_architecture': {'services': []},
                'requirements': {'confidence_score': 0.9},
                'proposed_architecture': {'quality_score': 0.85}
            }
            
            workflow.graph.aget_state = AsyncMock(return_value=mock_state)
            
            # Test status checking
            status = await workflow.get_workflow_status('test-session')
            
            assert status['session_id'] == 'test-session'
            assert status['current_stage'] == 'integration_designed'
            assert status['status'] == 'in_progress'
            assert 'progress_percentage' in status
            assert 'estimated_completion' in status

    @pytest.mark.asyncio
    async def test_workflow_with_low_confidence_requirements(self, mock_agents_and_services):
        """Test workflow with low confidence requirements."""
        # Modify requirements to have low confidence
        low_confidence_requirements = {
            'structured_requirements': {
                'business_goals': ['Unclear goals'],
                'functional_requirements': ['Vague requirements'],
                'non_functional_requirements': {
                    'performance': ['Not specified'],
                    'security': ['Basic security']
                },
                'constraints': ['Limited information'],
                'stakeholders': []
            },
            'confidence_score': 0.3,  # Low confidence
            'status': 'completed'
        }
        
        mock_agents_and_services['requirements_agent'].execute = AsyncMock(
            return_value=low_confidence_requirements
        )
        
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents_and_services['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents_and_services['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents_and_services['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents_and_services['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Initial state
            initial_state = {
                'session_id': 'e2e-low-confidence-session',
                'project_id': 'e2e-low-confidence-project',
                'repository_url': 'https://github.com/test/e-commerce-platform',
                'branch': 'main',
                'document_path': 'requirements.txt',
                'current_stage': 'starting',
                'errors': [],
                'warnings': [],
                'feedback_history': [],
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            # Run the workflow
            final_state = await workflow.run_workflow(initial_state)
            
            # Verify low confidence handling
            assert 'warnings' in final_state
            assert len(final_state['warnings']) > 0
            assert any('low confidence' in warning.lower() for warning in final_state['warnings'])

    @pytest.mark.asyncio
    async def test_workflow_performance_metrics(self, mock_agents_and_services):
        """Test workflow performance metrics collection."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents_and_services['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents_and_services['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents_and_services['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents_and_services['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Initial state
            initial_state = {
                'session_id': 'e2e-performance-session',
                'project_id': 'e2e-performance-project',
                'repository_url': 'https://github.com/test/e-commerce-platform',
                'branch': 'main',
                'document_path': 'requirements.txt',
                'current_stage': 'starting',
                'errors': [],
                'warnings': [],
                'feedback_history': [],
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            # Run the workflow
            final_state = await workflow.run_workflow(initial_state)
            
            # Verify performance metrics
            assert 'workflow_summary' in final_state
            summary = final_state['workflow_summary']
            assert 'quality_metrics' in summary
            
            quality_metrics = summary['quality_metrics']
            assert 'requirements_confidence' in quality_metrics
            assert 'architecture_quality' in quality_metrics
            assert 'integration_complexity' in quality_metrics
            assert 'risk_assessment' in quality_metrics
            assert 'overall_score' in quality_metrics
            
            # Verify metrics are within expected ranges
            assert 0 <= quality_metrics['requirements_confidence'] <= 1
            assert 0 <= quality_metrics['architecture_quality'] <= 1
            assert 0 <= quality_metrics['integration_complexity'] <= 1
            assert 0 <= quality_metrics['overall_score'] <= 1
