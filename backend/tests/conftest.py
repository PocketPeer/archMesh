"""
Pytest configuration and fixtures for the ArchMesh test suite.

This module provides shared fixtures and configuration for all tests.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
import os
import tempfile
import shutil

# Set test environment variables
os.environ['ENVIRONMENT'] = 'test'
os.environ['DATABASE_URL'] = 'sqlite:///test.db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/1'
os.environ['PINECONE_API_KEY'] = 'test-pinecone-key'
os.environ['PINECONE_ENVIRONMENT'] = 'test-env'
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'test-password'


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_project_id():
    """Generate a sample project ID for testing."""
    return str(uuid4())


@pytest.fixture
def sample_session_id():
    """Generate a sample session ID for testing."""
    return str(uuid4())


@pytest.fixture
def mock_github_repository():
    """Mock GitHub repository data."""
    return {
        'url': 'https://github.com/test/e-commerce-platform',
        'name': 'e-commerce-platform',
        'owner': 'test',
        'branch': 'main',
        'description': 'A sample e-commerce platform for testing',
        'language': 'JavaScript',
        'stars': 100,
        'forks': 20,
        'created_at': '2023-01-01T00:00:00Z',
        'updated_at': '2023-01-01T00:00:00Z'
    }


@pytest.fixture
def mock_repository_analysis():
    """Mock repository analysis result."""
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
                'dependencies': ['user-database'],
                'health_status': 'healthy',
                'version': '1.0.0'
            },
            {
                'id': 'user-database',
                'name': 'User Database',
                'type': 'database',
                'technology': 'PostgreSQL',
                'description': 'Stores user data and authentication info',
                'health_status': 'healthy',
                'version': '13.0'
            },
            {
                'id': 'payment-service',
                'name': 'Payment Service',
                'type': 'service',
                'technology': 'Java + Spring Boot',
                'description': 'Processes payments and billing',
                'endpoints': ['/api/payments', '/api/billing'],
                'dependencies': ['payment-database'],
                'health_status': 'healthy',
                'version': '2.1.0'
            }
        ],
        'dependencies': [
            {
                'id': 'user-service-to-db',
                'from': 'user-service',
                'to': 'user-database',
                'type': 'database-call',
                'description': 'User service reads/writes to user database',
                'frequency': 'high',
                'criticality': 'critical'
            },
            {
                'id': 'payment-to-user',
                'from': 'payment-service',
                'to': 'user-service',
                'type': 'api-call',
                'description': 'Payment service validates users via user service',
                'frequency': 'medium',
                'criticality': 'high'
            }
        ],
        'technology_stack': {
            'Node.js': {
                'version': '18.0.0',
                'count': 1,
                'services': ['user-service']
            },
            'Java': {
                'version': '17.0.0',
                'count': 1,
                'services': ['payment-service']
            },
            'PostgreSQL': {
                'version': '13.0',
                'count': 1,
                'services': ['user-database']
            },
            'Express': {
                'version': '4.18.0',
                'count': 1,
                'services': ['user-service']
            },
            'Spring Boot': {
                'version': '2.7.0',
                'count': 1,
                'services': ['payment-service']
            }
        },
        'quality_score': 0.85,
        'analysis_metadata': {
            'analyzed_at': '2023-01-01T00:00:00Z',
            'services_count': 3,
            'dependencies_count': 2,
            'technologies_detected': ['Node.js', 'Java', 'PostgreSQL', 'Express', 'Spring Boot'],
            'analysis_duration_seconds': 45.2,
            'files_analyzed': 156,
            'lines_of_code': 12500,
            'test_coverage': 0.78
        }
    }


@pytest.fixture
def mock_requirements_analysis():
    """Mock requirements analysis result."""
    return {
        'structured_requirements': {
            'business_goals': [
                'Improve user experience with real-time notifications',
                'Increase system reliability and performance',
                'Reduce customer support tickets',
                'Enhance user engagement'
            ],
            'functional_requirements': [
                'Add real-time notification system for order updates',
                'Implement user preference management for notifications',
                'Add email and SMS notification capabilities',
                'Create notification templates and customization',
                'Implement notification delivery tracking',
                'Add notification history and analytics'
            ],
            'non_functional_requirements': {
                'performance': [
                    'Notification delivery time < 5 seconds',
                    'System should handle 10k concurrent notifications',
                    'API response time < 200ms for notification requests',
                    'Support 100k active users'
                ],
                'security': [
                    'Secure notification delivery with encryption',
                    'User consent management for notifications',
                    'GDPR compliance for notification data',
                    'Rate limiting for notification APIs'
                ],
                'scalability': [
                    'Horizontal scaling capability for notification service',
                    'Auto-scaling based on notification volume',
                    'Support for multiple notification channels',
                    'Load balancing across notification instances'
                ],
                'reliability': [
                    '99.9% uptime for notification service',
                    'Message delivery guarantee with retry mechanism',
                    'Graceful degradation when external services fail',
                    'Comprehensive error handling and logging'
                ],
                'maintainability': [
                    'Modular notification service architecture',
                    'Comprehensive test coverage > 80%',
                    'Clear documentation and API specifications',
                    'Monitoring and alerting for notification failures'
                ]
            },
            'constraints': [
                'Must integrate with existing e-commerce platform',
                'No downtime during deployment',
                'Budget constraint: $50k for implementation',
                'Timeline: 3 months for full implementation',
                'Must comply with existing security policies',
                'Should use existing infrastructure where possible'
            ],
            'stakeholders': [
                {
                    'name': 'Product Manager',
                    'role': 'Product Owner',
                    'concerns': ['User experience', 'Feature delivery timeline', 'Business value'],
                    'influence': 'high'
                },
                {
                    'name': 'Engineering Team',
                    'role': 'Development Team',
                    'concerns': ['Technical feasibility', 'Integration complexity', 'Code quality'],
                    'influence': 'high'
                },
                {
                    'name': 'DevOps Team',
                    'role': 'Infrastructure Team',
                    'concerns': ['Deployment strategy', 'Monitoring', 'Scalability'],
                    'influence': 'medium'
                },
                {
                    'name': 'Security Team',
                    'role': 'Security Team',
                    'concerns': ['Data protection', 'Compliance', 'Security vulnerabilities'],
                    'influence': 'high'
                }
            ]
        },
        'confidence_score': 0.92,
        'status': 'completed',
        'analysis_metadata': {
            'analyzed_at': '2023-01-01T00:00:00Z',
            'document_type': 'requirements_specification',
            'document_size': 25000,
            'extraction_method': 'llm_analysis',
            'validation_performed': True,
            'ambiguities_found': 2,
            'missing_requirements': 1
        }
    }


@pytest.fixture
def mock_architecture_design():
    """Mock architecture design result."""
    return {
        'architecture_overview': {
            'style': 'microservices',
            'integration_approach': 'Event-driven integration with message queues',
            'rationale': 'Extends existing microservices architecture with notification capabilities using event-driven patterns for minimal disruption and high scalability',
            'design_principles': [
                'Separation of concerns',
                'Event-driven architecture',
                'Fault tolerance',
                'Scalability',
                'Maintainability'
            ]
        },
        'new_services': [
            {
                'id': 'notification-service',
                'name': 'Notification Service',
                'type': 'service',
                'technology': 'Node.js + Express',
                'description': 'Handles real-time notifications via email, SMS, and push notifications',
                'endpoints': [
                    '/api/notifications',
                    '/api/templates',
                    '/api/preferences',
                    '/api/delivery-status'
                ],
                'dependencies': ['notification-database', 'message-queue', 'email-service', 'sms-service'],
                'health_check': '/health',
                'metrics_endpoint': '/metrics',
                'version': '1.0.0'
            },
            {
                'id': 'notification-database',
                'name': 'Notification Database',
                'type': 'database',
                'technology': 'MongoDB',
                'description': 'Stores notification templates, delivery status, and user preferences',
                'schema': {
                    'collections': ['notifications', 'templates', 'preferences', 'delivery_logs']
                },
                'backup_strategy': 'Daily backups with 30-day retention',
                'version': '5.0'
            },
            {
                'id': 'message-queue',
                'name': 'Message Queue',
                'type': 'component',
                'technology': 'Apache Kafka',
                'description': 'Handles asynchronous message processing for notifications and events',
                'topics': ['user-events', 'payment-events', 'notification-requests'],
                'partitions': 3,
                'replication_factor': 2,
                'retention_policy': '7 days',
                'version': '3.0.0'
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
                'dependencies': ['user-database', 'message-queue'],
                'changes': [
                    'Added notification preferences endpoint',
                    'Added event publishing for user actions',
                    'Enhanced user profile with notification settings'
                ],
                'version': '1.1.0'
            },
            {
                'id': 'payment-service',
                'name': 'Payment Service',
                'type': 'service',
                'technology': 'Java + Spring Boot',
                'description': 'Enhanced to publish payment events for order notifications',
                'endpoints': ['/api/payments', '/api/billing'],
                'dependencies': ['payment-database', 'message-queue'],
                'changes': [
                    'Added event publishing for payment events',
                    'Enhanced payment status updates',
                    'Added notification triggers for payment failures'
                ],
                'version': '2.2.0'
            }
        ],
        'integration_points': [
            {
                'id': 'user-events',
                'from_service': 'user-service',
                'to_service': 'message-queue',
                'type': 'event-stream',
                'description': 'Publishes user events (registration, profile updates) for notification processing',
                'events': ['user.registered', 'user.profile.updated', 'user.preferences.changed'],
                'implementation_notes': 'Use event sourcing pattern for reliable delivery',
                'data_format': 'JSON',
                'schema_version': '1.0'
            },
            {
                'id': 'payment-events',
                'from_service': 'payment-service',
                'to_service': 'message-queue',
                'type': 'event-stream',
                'description': 'Publishes payment events (success, failure) for order notifications',
                'events': ['payment.success', 'payment.failed', 'payment.refunded'],
                'implementation_notes': 'Add event publishing to existing payment flow',
                'data_format': 'JSON',
                'schema_version': '1.0'
            },
            {
                'id': 'notification-processing',
                'from_service': 'message-queue',
                'to_service': 'notification-service',
                'type': 'message-queue',
                'description': 'Consumes user and payment events to trigger notifications',
                'implementation_notes': 'Implement idempotent processing for reliability',
                'batch_size': 100,
                'processing_timeout': '30s'
            }
        ],
        'impact_analysis': {
            'risk_level': 'medium',
            'breaking_changes': False,
            'downtime_required': False,
            'data_migration_required': False,
            'performance_impact': 'minimal',
            'security_impact': 'low',
            'operational_impact': 'medium'
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
                        'Deploy Kafka cluster with monitoring',
                        'Setup MongoDB for notifications with backup',
                        'Configure monitoring and logging',
                        'Setup development and staging environments'
                    ],
                    'rollback': 'Remove Kafka and MongoDB instances',
                    'success_criteria': [
                        'Kafka cluster is healthy and monitored',
                        'MongoDB is accessible and backed up',
                        'Monitoring dashboards are configured'
                    ]
                },
                {
                    'phase': 2,
                    'name': 'Notification Service Deployment',
                    'description': 'Deploy and configure notification service',
                    'duration': '2-3 weeks',
                    'services': ['notification-service'],
                    'steps': [
                        'Deploy notification service with health checks',
                        'Configure email and SMS providers',
                        'Setup notification templates',
                        'Implement user preference management',
                        'Add comprehensive logging and metrics'
                    ],
                    'rollback': 'Remove notification service and disable event publishing',
                    'success_criteria': [
                        'Notification service is deployed and healthy',
                        'Email and SMS providers are configured',
                        'Templates are created and tested',
                        'User preferences API is working'
                    ]
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
                        'Integration testing for event flows',
                        'Performance testing for message queue',
                        'End-to-end testing for notification delivery',
                        'Load testing for concurrent notifications',
                        'User acceptance testing'
                    ],
                    'rollback': 'Remove event publishing and revert service changes',
                    'success_criteria': [
                        'Events are published correctly',
                        'Notifications are delivered successfully',
                        'Performance meets requirements',
                        'All tests pass',
                        'User acceptance criteria met'
                    ]
                }
            ],
            'testing_strategy': [
                'Unit testing for all new services',
                'Integration testing for event flows',
                'Performance testing for message queue',
                'End-to-end testing for notification delivery',
                'Load testing for concurrent notifications',
                'Security testing for notification APIs',
                'Chaos engineering for fault tolerance'
            ],
            'monitoring': [
                'Enhanced logging for all services',
                'Performance metrics for message queue',
                'Notification delivery tracking',
                'Error rate monitoring',
                'User engagement metrics',
                'System health dashboards',
                'Alerting for critical failures'
            ],
            'rollback_plan': 'Remove new services, disable event publishing, revert existing service changes'
        }
    }


@pytest.fixture
def mock_implementation_plan():
    """Mock implementation plan result."""
    return {
        'project_overview': {
            'project_name': 'E-commerce Notification System',
            'project_description': 'Add real-time notification capabilities to existing e-commerce platform',
            'timeline': '3 months',
            'budget': '$50,000',
            'team_size': 5,
            'risk_level': 'medium'
        },
        'phases': [
            {
                'phase': 1,
                'name': 'Infrastructure Setup',
                'duration': '2 weeks',
                'start_date': '2023-01-01',
                'end_date': '2023-01-15',
                'deliverables': [
                    'Kafka cluster deployment',
                    'MongoDB setup',
                    'Monitoring configuration'
                ],
                'resources': [
                    'DevOps Engineer (1)',
                    'Infrastructure costs'
                ],
                'dependencies': [],
                'risks': [
                    'Infrastructure setup delays',
                    'Network connectivity issues'
                ],
                'mitigation': [
                    'Use managed services where possible',
                    'Have backup infrastructure options'
                ]
            },
            {
                'phase': 2,
                'name': 'Notification Service Development',
                'duration': '3 weeks',
                'start_date': '2023-01-16',
                'end_date': '2023-02-05',
                'deliverables': [
                    'Notification service implementation',
                    'Email/SMS integration',
                    'Template management system'
                ],
                'resources': [
                    'Backend Developer (2)',
                    'Frontend Developer (1)',
                    'Third-party service costs'
                ],
                'dependencies': ['Phase 1 completion'],
                'risks': [
                    'Third-party service integration issues',
                    'Performance bottlenecks'
                ],
                'mitigation': [
                    'Early integration testing',
                    'Performance optimization'
                ]
            },
            {
                'phase': 3,
                'name': 'Integration and Testing',
                'duration': '3 weeks',
                'start_date': '2023-02-06',
                'end_date': '2023-02-26',
                'deliverables': [
                    'Service integration',
                    'Comprehensive testing',
                    'Documentation'
                ],
                'resources': [
                    'Full team (5)',
                    'QA Engineer (1)',
                    'Testing tools'
                ],
                'dependencies': ['Phase 2 completion'],
                'risks': [
                    'Integration complexity',
                    'Performance issues'
                ],
                'mitigation': [
                    'Incremental integration',
                    'Performance monitoring'
                ]
            }
        ],
        'timeline': {
            'total_duration': '8 weeks',
            'start_date': '2023-01-01',
            'end_date': '2023-02-26',
            'milestones': [
                {
                    'name': 'Infrastructure Ready',
                    'date': '2023-01-15',
                    'deliverable': 'Kafka and MongoDB deployed'
                },
                {
                    'name': 'Notification Service Complete',
                    'date': '2023-02-05',
                    'deliverable': 'Core notification functionality'
                },
                {
                    'name': 'Integration Complete',
                    'date': '2023-02-26',
                    'deliverable': 'Full system integration'
                }
            ]
        },
        'risk_mitigation': {
            'high_risks': [
                {
                    'risk': 'Third-party service failures',
                    'probability': 'medium',
                    'impact': 'high',
                    'mitigation': 'Implement fallback mechanisms and monitoring'
                },
                {
                    'risk': 'Performance degradation',
                    'probability': 'low',
                    'impact': 'high',
                    'mitigation': 'Load testing and performance monitoring'
                }
            ],
            'medium_risks': [
                {
                    'risk': 'Integration complexity',
                    'probability': 'medium',
                    'impact': 'medium',
                    'mitigation': 'Incremental integration and testing'
                }
            ],
            'low_risks': [
                {
                    'risk': 'Timeline delays',
                    'probability': 'low',
                    'impact': 'low',
                    'mitigation': 'Buffer time in schedule'
                }
            ]
        }
    }


@pytest.fixture
def mock_workflow_summary():
    """Mock workflow summary result."""
    return {
        'workflow_status': 'completed',
        'session_id': 'test-session-123',
        'project_id': 'test-project-456',
        'total_duration': '2 hours 30 minutes',
        'completed_at': '2023-01-01T02:30:00Z',
        'deliverables': {
            'existing_architecture_analysis': {
                'status': 'completed',
                'quality_score': 0.85,
                'services_analyzed': 3,
                'dependencies_mapped': 2
            },
            'structured_requirements': {
                'status': 'completed',
                'confidence_score': 0.92,
                'requirements_count': 15,
                'stakeholders_identified': 4
            },
            'proposed_architecture': {
                'status': 'completed',
                'quality_score': 0.88,
                'new_services': 3,
                'modified_services': 2
            },
            'integration_strategy': {
                'status': 'completed',
                'phases_defined': 3,
                'risk_level': 'medium',
                'estimated_duration': '8 weeks'
            },
            'implementation_plan': {
                'status': 'completed',
                'phases_planned': 3,
                'total_duration': '8 weeks',
                'budget_estimated': '$50,000'
            }
        },
        'quality_metrics': {
            'requirements_confidence': 0.92,
            'architecture_quality': 0.88,
            'integration_complexity': 0.65,
            'risk_assessment': 0.70,
            'overall_score': 0.79
        },
        'feedback_history': [
            {
                'stage': 'requirements_review',
                'reviewer': 'Product Manager',
                'decision': 'approved',
                'comments': 'Requirements are comprehensive and well-structured',
                'timestamp': '2023-01-01T01:00:00Z'
            },
            {
                'stage': 'integration_review',
                'reviewer': 'Engineering Team Lead',
                'decision': 'approved',
                'comments': 'Architecture design is solid and integration strategy is well thought out',
                'timestamp': '2023-01-01T02:00:00Z'
            }
        ],
        'next_steps': [
            'Begin Phase 1: Infrastructure Setup',
            'Setup development environment',
            'Assign team members to tasks',
            'Schedule regular progress reviews'
        ]
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        'content': '{"architecture": {"style": "microservices", "components": []}}',
        'usage': {
            'prompt_tokens': 100,
            'completion_tokens': 50,
            'total_tokens': 150
        },
        'model': 'deepseek-r1',
        'finish_reason': 'stop'
    }


@pytest.fixture
def mock_embedding():
    """Mock embedding vector for testing."""
    return [0.1, 0.2, 0.3, 0.4, 0.5] * 20  # 100-dimensional vector


@pytest.fixture
def mock_pinecone_result():
    """Mock Pinecone search result."""
    return {
        'matches': [
            {
                'id': 'chunk-1',
                'score': 0.95,
                'metadata': {
                    'project_id': 'test-project',
                    'chunk_type': 'architecture',
                    'content': 'Microservices architecture with Node.js'
                }
            },
            {
                'id': 'chunk-2',
                'score': 0.88,
                'metadata': {
                    'project_id': 'test-project',
                    'chunk_type': 'service',
                    'content': 'User service handles authentication'
                }
            }
        ]
    }


@pytest.fixture
def mock_neo4j_result():
    """Mock Neo4j query result."""
    return [
        {
            'service': {'name': 'user-service', 'technology': 'Node.js'},
            'dependencies': [
                {'name': 'user-database', 'type': 'database-call'}
            ]
        }
    ]


# Test markers for different test types
pytest_plugins = ["pytest_asyncio"]