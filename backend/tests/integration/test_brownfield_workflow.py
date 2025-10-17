"""
Integration tests for the Brownfield Workflow.

These tests verify the complete brownfield workflow integration
including GitHub analysis, knowledge base indexing, and architecture design.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from uuid import uuid4

from app.workflows.brownfield_workflow import BrownfieldWorkflow, BrownfieldWorkflowState
from app.agents.github_analyzer_agent import GitHubAnalyzerAgent
from app.agents.requirements_agent import RequirementsAgent
from app.agents.architecture_agent import ArchitectureAgent
from app.services.knowledge_base_service import KnowledgeBaseService


class TestBrownfieldWorkflow:
    """Test the complete brownfield workflow integration."""

    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing."""
        github_analyzer = Mock(spec=GitHubAnalyzerAgent)
        requirements_agent = Mock(spec=RequirementsAgent)
        architecture_agent = Mock(spec=ArchitectureAgent)
        kb_service = Mock(spec=KnowledgeBaseService)
        
        return {
            'github_analyzer': github_analyzer,
            'requirements_agent': requirements_agent,
            'architecture_agent': architecture_agent,
            'kb_service': kb_service
        }

    @pytest.fixture
    def mock_analysis_result(self):
        """Mock GitHub analysis result."""
        return {
            'repository_url': 'https://github.com/test/repo',
            'branch': 'main',
            'services': [
                {
                    'id': 'user-service',
                    'name': 'User Service',
                    'type': 'service',
                    'technology': 'Node.js + Express',
                    'description': 'Handles user authentication',
                    'endpoints': ['/api/users', '/api/auth'],
                    'dependencies': ['user-database']
                },
                {
                    'id': 'user-database',
                    'name': 'User Database',
                    'type': 'database',
                    'technology': 'PostgreSQL',
                    'description': 'Stores user data'
                }
            ],
            'dependencies': [
                {
                    'from': 'user-service',
                    'to': 'user-database',
                    'type': 'database-call',
                    'description': 'User service reads/writes to database'
                }
            ],
            'technology_stack': {
                'Node.js': 1,
                'PostgreSQL': 1,
                'Express': 1
            },
            'quality_score': 0.85,
            'analysis_metadata': {
                'analyzed_at': '2023-01-01T00:00:00Z',
                'services_count': 2,
                'dependencies_count': 1,
                'technologies_detected': ['Node.js', 'PostgreSQL', 'Express']
            }
        }

    @pytest.fixture
    def mock_requirements_result(self):
        """Mock requirements analysis result."""
        return {
            'structured_requirements': {
                'business_goals': ['Improve user experience', 'Increase system reliability'],
                'functional_requirements': [
                    'Add real-time notifications',
                    'Implement user preferences'
                ],
                'non_functional_requirements': {
                    'performance': ['Response time < 200ms'],
                    'security': ['OAuth 2.0 authentication'],
                    'scalability': ['Support 10k concurrent users']
                },
                'constraints': ['Must integrate with existing system'],
                'stakeholders': [
                    {
                        'name': 'Product Manager',
                        'role': 'Product Owner',
                        'concerns': ['User experience', 'Feature delivery']
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
                'integration_approach': 'Event-driven integration',
                'rationale': 'Extends existing microservices with notification capabilities'
            },
            'new_services': [
                {
                    'id': 'notification-service',
                    'name': 'Notification Service',
                    'type': 'service',
                    'technology': 'Node.js + Express',
                    'description': 'Handles real-time notifications',
                    'endpoints': ['/api/notifications'],
                    'dependencies': ['notification-database', 'message-queue']
                }
            ],
            'modified_services': [
                {
                    'id': 'user-service',
                    'name': 'User Service',
                    'type': 'service',
                    'technology': 'Node.js + Express',
                    'description': 'Enhanced with notification preferences',
                    'endpoints': ['/api/users', '/api/auth', '/api/preferences'],
                    'dependencies': ['user-database', 'message-queue']
                }
            ],
            'integration_points': [
                {
                    'from_service': 'user-service',
                    'to_service': 'message-queue',
                    'type': 'event-stream',
                    'description': 'Publishes user events for notifications'
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
                        'name': 'Deploy New Services',
                        'description': 'Deploy notification service and message queue',
                        'duration': '2-3 weeks',
                        'services': ['notification-service', 'message-queue'],
                        'steps': ['Deploy infrastructure', 'Configure services'],
                        'rollback': 'Remove new services'
                    }
                ],
                'testing_strategy': ['Integration testing', 'Performance testing'],
                'monitoring': ['Enhanced logging', 'Performance metrics'],
                'rollback_plan': 'Remove new services and revert user service changes'
            }
        }

    @pytest.mark.asyncio
    async def test_workflow_initialization(self, mock_agents):
        """Test that the workflow initializes correctly."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            assert workflow.github_analyzer == mock_agents['github_analyzer']
            assert workflow.requirements_agent == mock_agents['requirements_agent']
            assert workflow.architecture_agent == mock_agents['architecture_agent']
            assert workflow.kb_service == mock_agents['kb_service']
            assert workflow.graph is not None

    @pytest.mark.asyncio
    async def test_analyze_existing_node(self, mock_agents, mock_analysis_result):
        """Test the analyze_existing workflow node."""
        # Setup mocks
        mock_agents['github_analyzer'].execute = AsyncMock(return_value=mock_analysis_result)
        mock_agents['kb_service'].index_repository_analysis = AsyncMock()
        
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Test state
            state = BrownfieldWorkflowState(
                session_id='test-session',
                project_id='test-project',
                repository_url='https://github.com/test/repo',
                branch='main',
                current_stage='starting',
                errors=[],
                warnings=[],
                feedback_history=[],
                created_at='2023-01-01T00:00:00Z',
                updated_at='2023-01-01T00:00:00Z'
            )
            
            # Execute the node
            result = await workflow._analyze_existing_node(state)
            
            # Verify results
            assert result['existing_architecture'] == mock_analysis_result
            assert result['current_stage'] == 'existing_analyzed'
            assert 'analysis_metadata' in result
            
            # Verify agent calls
            mock_agents['github_analyzer'].execute.assert_called_once()
            mock_agents['kb_service'].index_repository_analysis.assert_called_once()

    @pytest.mark.asyncio
    async def test_parse_requirements_node(self, mock_agents, mock_requirements_result):
        """Test the parse_requirements workflow node."""
        # Setup mocks
        mock_agents['requirements_agent'].execute = AsyncMock(return_value=mock_requirements_result)
        
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Test state
            state = BrownfieldWorkflowState(
                session_id='test-session',
                project_id='test-project',
                repository_url='https://github.com/test/repo',
                document_path='requirements.txt',
                current_stage='existing_analyzed',
                errors=[],
                warnings=[],
                feedback_history=[],
                created_at='2023-01-01T00:00:00Z',
                updated_at='2023-01-01T00:00:00Z'
            )
            
            # Execute the node
            result = await workflow._parse_requirements_node(state)
            
            # Verify results
            assert result['requirements'] == mock_requirements_result
            assert result['current_stage'] == 'requirements_parsed'
            
            # Verify agent call
            mock_agents['requirements_agent'].execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_design_integration_node(self, mock_agents, mock_architecture_result):
        """Test the design_integration workflow node."""
        # Setup mocks
        mock_agents['architecture_agent'].execute = AsyncMock(return_value=mock_architecture_result)
        
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Test state
            state = BrownfieldWorkflowState(
                session_id='test-session',
                project_id='test-project',
                repository_url='https://github.com/test/repo',
                requirements={'test': 'requirements'},
                current_stage='requirements_reviewed',
                errors=[],
                warnings=[],
                feedback_history=[],
                created_at='2023-01-01T00:00:00Z',
                updated_at='2023-01-01T00:00:00Z'
            )
            
            # Execute the node
            result = await workflow._design_integration_node(state)
            
            # Verify results
            assert result['proposed_architecture'] == mock_architecture_result
            assert result['integration_strategy'] == mock_architecture_result['integration_strategy']
            assert result['current_stage'] == 'integration_designed'
            
            # Verify agent call
            mock_agents['architecture_agent'].execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_human_review_requirements_node(self, mock_agents):
        """Test the human_review_requirements workflow node."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Test state with high confidence requirements
            state = BrownfieldWorkflowState(
                session_id='test-session',
                project_id='test-project',
                requirements={'confidence_score': 0.8},
                current_stage='requirements_parsed',
                errors=[],
                warnings=[],
                feedback_history=[],
                created_at='2023-01-01T00:00:00Z',
                updated_at='2023-01-01T00:00:00Z'
            )
            
            # Execute the node
            result = await workflow._human_review_requirements_node(state)
            
            # Verify results
            assert result['approval_status'] == 'approved'
            assert result['current_stage'] == 'requirements_reviewed'
            assert 'human_feedback' in result
            assert 'feedback_history' in result

    @pytest.mark.asyncio
    async def test_human_review_integration_node(self, mock_agents):
        """Test the human_review_integration workflow node."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Test state with proposed architecture
            state = BrownfieldWorkflowState(
                session_id='test-session',
                project_id='test-project',
                proposed_architecture={'new_services': [{'name': 'test-service'}]},
                integration_strategy={'phases': []},
                current_stage='integration_designed',
                errors=[],
                warnings=[],
                feedback_history=[],
                created_at='2023-01-01T00:00:00Z',
                updated_at='2023-01-01T00:00:00Z'
            )
            
            # Execute the node
            result = await workflow._human_review_integration_node(state)
            
            # Verify results
            assert result['approval_status'] == 'approved'
            assert result['current_stage'] == 'integration_reviewed'
            assert 'human_feedback' in result
            assert 'feedback_history' in result

    @pytest.mark.asyncio
    async def test_generate_implementation_plan_node(self, mock_agents):
        """Test the generate_implementation_plan workflow node."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Test state
            state = BrownfieldWorkflowState(
                session_id='test-session',
                project_id='test-project',
                integration_strategy={
                    'phases': [
                        {
                            'phase': 1,
                            'name': 'Test Phase',
                            'duration': '1 week',
                            'services': ['test-service']
                        }
                    ],
                    'testing_strategy': ['unit tests'],
                    'monitoring': ['logging'],
                    'rollback_plan': 'revert changes'
                },
                proposed_architecture={
                    'impact_analysis': {
                        'risk_level': 'low',
                        'breaking_changes': False
                    }
                },
                current_stage='integration_reviewed',
                errors=[],
                warnings=[],
                feedback_history=[],
                created_at='2023-01-01T00:00:00Z',
                updated_at='2023-01-01T00:00:00Z'
            )
            
            # Execute the node
            result = await workflow._generate_implementation_plan_node(state)
            
            # Verify results
            assert result['current_stage'] == 'implementation_planned'
            assert 'implementation_plan' in result
            
            implementation_plan = result['implementation_plan']
            assert 'project_overview' in implementation_plan
            assert 'phases' in implementation_plan
            assert 'timeline' in implementation_plan
            assert 'risk_mitigation' in implementation_plan

    @pytest.mark.asyncio
    async def test_finalize_workflow_node(self, mock_agents):
        """Test the finalize_workflow workflow node."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Test state
            state = BrownfieldWorkflowState(
                session_id='test-session',
                project_id='test-project',
                repository_url='https://github.com/test/repo',
                existing_architecture={'services': []},
                requirements={'confidence_score': 0.9},
                proposed_architecture={'quality_score': 0.85},
                integration_strategy={'phases': []},
                implementation_plan={'project_overview': {}},
                feedback_history=[{'reviewer': 'test', 'status': 'approved'}],
                current_stage='implementation_planned',
                errors=[],
                warnings=[],
                created_at='2023-01-01T00:00:00Z',
                updated_at='2023-01-01T00:00:00Z'
            )
            
            # Execute the node
            result = await workflow._finalize_workflow_node(state)
            
            # Verify results
            assert result['current_stage'] == 'completed'
            assert 'workflow_summary' in result
            assert 'completed_at' in result
            
            workflow_summary = result['workflow_summary']
            assert workflow_summary['workflow_status'] == 'completed'
            assert 'deliverables' in workflow_summary
            assert 'quality_metrics' in workflow_summary

    @pytest.mark.asyncio
    async def test_workflow_status_checking(self, mock_agents):
        """Test workflow status checking functionality."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Mock the graph state
            mock_state = Mock()
            mock_state.values = {
                'current_stage': 'integration_designed',
                'errors': [],
                'warnings': [],
                'updated_at': '2023-01-01T00:00:00Z'
            }
            
            workflow.graph.aget_state = AsyncMock(return_value=mock_state)
            
            # Test status checking
            status = await workflow.get_workflow_status('test-session')
            
            assert status['session_id'] == 'test-session'
            assert status['current_stage'] == 'integration_designed'
            assert status['status'] == 'in_progress'

    @pytest.mark.asyncio
    async def test_workflow_info(self, mock_agents):
        """Test workflow information retrieval."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Test info retrieval
            info = workflow.get_workflow_info()
            
            assert info['workflow_name'] == 'Brownfield Workflow'
            assert 'stages' in info
            assert 'features' in info
            assert 'agents_used' in info
            assert 'services_used' in info
            
            # Verify expected stages
            expected_stages = [
                'analyze_existing',
                'parse_requirements',
                'human_review_requirements',
                'design_integration',
                'human_review_integration',
                'generate_implementation_plan',
                'finalize_workflow'
            ]
            assert all(stage in info['stages'] for stage in expected_stages)

    @pytest.mark.asyncio
    async def test_error_handling_in_analyze_existing(self, mock_agents):
        """Test error handling in analyze_existing node."""
        # Setup mocks to raise an exception
        mock_agents['github_analyzer'].execute = AsyncMock(side_effect=Exception('Analysis failed'))
        
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Test state
            state = BrownfieldWorkflowState(
                session_id='test-session',
                project_id='test-project',
                repository_url='https://github.com/test/repo',
                current_stage='starting',
                errors=[],
                warnings=[],
                feedback_history=[],
                created_at='2023-01-01T00:00:00Z',
                updated_at='2023-01-01T00:00:00Z'
            )
            
            # Execute the node
            result = await workflow._analyze_existing_node(state)
            
            # Verify error handling
            assert result['current_stage'] == 'failed'
            assert len(result['errors']) == 1
            assert 'Analysis failed' in result['errors'][0]

    @pytest.mark.asyncio
    async def test_conditional_edges_approval_logic(self, mock_agents):
        """Test the conditional edges approval logic."""
        with patch('app.workflows.brownfield_workflow.GitHubAnalyzerAgent', return_value=mock_agents['github_analyzer']), \
             patch('app.workflows.brownfield_workflow.RequirementsAgent', return_value=mock_agents['requirements_agent']), \
             patch('app.workflows.brownfield_workflow.ArchitectureAgent', return_value=mock_agents['architecture_agent']), \
             patch('app.workflows.brownfield_workflow.KnowledgeBaseService', return_value=mock_agents['kb_service']):
            
            workflow = BrownfieldWorkflow()
            
            # Test approved state
            approved_state = BrownfieldWorkflowState(
                session_id='test-session',
                project_id='test-project',
                approval_status='approved',
                current_stage='requirements_reviewed',
                errors=[],
                warnings=[],
                feedback_history=[],
                created_at='2023-01-01T00:00:00Z',
                updated_at='2023-01-01T00:00:00Z'
            )
            
            result = workflow._check_requirements_approval(approved_state)
            assert result == 'approved'
            
            # Test rejected state
            rejected_state = BrownfieldWorkflowState(
                session_id='test-session',
                project_id='test-project',
                approval_status='rejected',
                current_stage='requirements_reviewed',
                errors=[],
                warnings=[],
                feedback_history=[],
                created_at='2023-01-01T00:00:00Z',
                updated_at='2023-01-01T00:00:00Z'
            )
            
            result = workflow._check_requirements_approval(rejected_state)
            assert result == 'rejected'
            
            # Test needs revision state
            revision_state = BrownfieldWorkflowState(
                session_id='test-session',
                project_id='test-project',
                approval_status='needs_revision',
                current_stage='requirements_reviewed',
                errors=[],
                warnings=[],
                feedback_history=[],
                created_at='2023-01-01T00:00:00Z',
                updated_at='2023-01-01T00:00:00Z'
            )
            
            result = workflow._check_requirements_approval(revision_state)
            assert result == 'needs_revision'
