"""
Unit tests for the Architecture Agent brownfield functionality.

These tests verify the brownfield-specific methods and integration
with the knowledge base service.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from app.agents.architecture_agent import ArchitectureAgent


class TestArchitectureAgentBrownfield:
    """Test the brownfield functionality of the Architecture Agent."""

    @pytest.fixture
    def mock_kb_service(self):
        """Create a mock knowledge base service."""
        kb_service = Mock()
        kb_service.search_similar_architectures = AsyncMock(return_value=[
            {
                'id': 'similar-arch-1',
                'similarity_score': 0.85,
                'metadata': {
                    'project_id': 'project-1',
                    'architecture_type': 'microservices',
                    'technologies': ['Node.js', 'PostgreSQL']
                }
            }
        ])
        kb_service.get_service_dependencies = AsyncMock(return_value=[
            {
                'service_id': 'user-service',
                'dependencies': ['user-database', 'auth-service'],
                'dependents': ['payment-service']
            }
        ])
        kb_service.get_context_for_new_feature = AsyncMock(return_value={
            'similar_features': [
                {
                    'feature_name': 'user-notifications',
                    'implementation_approach': 'event-driven',
                    'technologies_used': ['Node.js', 'Kafka']
                }
            ],
            'existing_services': [
                {
                    'id': 'user-service',
                    'name': 'User Service',
                    'technology': 'Node.js',
                    'endpoints': ['/api/users']
                }
            ],
            'integration_patterns': [
                {
                    'pattern': 'event-driven',
                    'description': 'Use message queues for async communication'
                }
            ]
        })
        return kb_service

    @pytest.fixture
    def architecture_agent(self, mock_kb_service):
        """Create an Architecture Agent with mock knowledge base service."""
        with patch('app.config.settings') as mock_settings:
            mock_settings.get_llm_config_for_task.return_value = ('deepseek', 'deepseek-r1')
            agent = ArchitectureAgent(knowledge_base_service=mock_kb_service)
            return agent

    @pytest.fixture
    def sample_requirements(self):
        """Sample requirements for testing."""
        return {
            'structured_requirements': {
                'business_goals': ['Improve user experience'],
                'functional_requirements': ['Add real-time notifications'],
                'non_functional_requirements': {
                    'performance': ['Response time < 200ms'],
                    'scalability': ['Support 10k users']
                }
            },
            'confidence_score': 0.9
        }

    @pytest.fixture
    def sample_existing_architecture(self):
        """Sample existing architecture for testing."""
        return {
            'services': [
                {
                    'id': 'user-service',
                    'name': 'User Service',
                    'type': 'service',
                    'technology': 'Node.js + Express',
                    'description': 'Handles user authentication'
                }
            ],
            'dependencies': [
                {
                    'from': 'user-service',
                    'to': 'user-database',
                    'type': 'database-call'
                }
            ],
            'technology_stack': {
                'Node.js': 1,
                'PostgreSQL': 1
            }
        }

    def test_initialization_with_kb_service(self, mock_kb_service):
        """Test that the agent initializes correctly with knowledge base service."""
        with patch('app.config.settings') as mock_settings:
            mock_settings.get_llm_config_for_task.return_value = ('deepseek', 'deepseek-r1')
            agent = ArchitectureAgent(knowledge_base_service=mock_kb_service)
            
            assert agent.kb_service == mock_kb_service
            assert agent.agent_type == 'architecture_designer'
            assert agent.agent_version == '1.1.0'

    def test_initialization_without_kb_service(self):
        """Test that the agent initializes correctly without knowledge base service."""
        with patch('app.config.settings') as mock_settings:
            mock_settings.get_llm_config_for_task.return_value = ('deepseek', 'deepseek-r1')
            agent = ArchitectureAgent()
            
            assert agent.kb_service is None
            assert agent.agent_type == 'architecture_designer'
            assert agent.agent_version == '1.1.0'

    @pytest.mark.asyncio
    async def test_execute_brownfield_mode(self, architecture_agent, sample_requirements, sample_existing_architecture):
        """Test execute method in brownfield mode."""
        # Mock the brownfield execution method
        architecture_agent._execute_brownfield = AsyncMock(return_value={
            'architecture': {'style': 'microservices'},
            'integration_strategy': {'phases': []}
        })
        
        input_data = {
            'mode': 'brownfield',
            'project_id': 'test-project',
            'requirements': sample_requirements,
            'existing_architecture': sample_existing_architecture
        }
        
        result = await architecture_agent.execute(input_data)
        
        architecture_agent._execute_brownfield.assert_called_once_with(input_data)
        assert result['architecture']['style'] == 'microservices'

    @pytest.mark.asyncio
    async def test_execute_greenfield_mode(self, architecture_agent, sample_requirements):
        """Test execute method in greenfield mode."""
        # Mock the greenfield execution method
        architecture_agent._execute_greenfield = AsyncMock(return_value={
            'architecture': {'style': 'microservices'},
            'components': []
        })
        
        input_data = {
            'mode': 'greenfield',
            'requirements': sample_requirements
        }
        
        result = await architecture_agent.execute(input_data)
        
        architecture_agent._execute_greenfield.assert_called_once_with(input_data)
        assert result['architecture']['style'] == 'microservices'

    @pytest.mark.asyncio
    async def test_execute_requires_project_id_for_brownfield(self, architecture_agent, sample_requirements):
        """Test that brownfield mode requires project_id."""
        input_data = {
            'mode': 'brownfield',
            'requirements': sample_requirements
        }
        
        with pytest.raises(ValueError, match="project_id is required for brownfield mode"):
            await architecture_agent.execute(input_data)

    @pytest.mark.asyncio
    async def test_get_brownfield_context(self, architecture_agent, sample_requirements, sample_existing_architecture):
        """Test getting brownfield context from knowledge base."""
        project_id = 'test-project'
        
        result = await architecture_agent._get_brownfield_context(
            project_id, sample_requirements, sample_existing_architecture
        )
        
        # Verify knowledge base service calls
        architecture_agent.kb_service.search_similar_architectures.assert_called_once()
        architecture_agent.kb_service.get_service_dependencies.assert_called_once()
        architecture_agent.kb_service.get_context_for_new_feature.assert_called_once()
        
        # Verify result structure
        assert 'similar_architectures' in result
        assert 'existing_services' in result
        assert 'integration_patterns' in result
        assert 'technology_consistency' in result

    def test_get_brownfield_system_prompt(self, architecture_agent):
        """Test the brownfield system prompt."""
        prompt = architecture_agent.get_brownfield_system_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'brownfield' in prompt.lower()
        assert 'integration' in prompt.lower()
        assert 'existing' in prompt.lower()

    def test_build_brownfield_prompt(self, architecture_agent, sample_requirements, sample_existing_architecture):
        """Test building the brownfield prompt."""
        constraints = {'budget': 'limited'}
        preferences = ['microservices', 'event-driven']
        domain = 'e-commerce'
        context = {
            'similar_architectures': [],
            'existing_services': sample_existing_architecture['services'],
            'integration_patterns': []
        }
        
        prompt = architecture_agent._build_brownfield_prompt(
            sample_requirements, constraints, preferences, domain, context
        )
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'requirements' in prompt.lower()
        assert 'existing' in prompt.lower()
        assert 'integration' in prompt.lower()

    @pytest.mark.asyncio
    async def test_generate_integration_strategy(self, architecture_agent):
        """Test generating integration strategy."""
        existing_services = [
            {
                'id': 'user-service',
                'name': 'User Service',
                'technology': 'Node.js'
            }
        ]
        
        proposed_architecture = {
            'new_services': [
                {
                    'id': 'notification-service',
                    'name': 'Notification Service',
                    'technology': 'Node.js'
                }
            ],
            'modified_services': [
                {
                    'id': 'user-service',
                    'name': 'User Service',
                    'technology': 'Node.js'
                }
            ]
        }
        
        result = await architecture_agent._generate_integration_strategy(
            existing_services, proposed_architecture
        )
        
        assert isinstance(result, dict)
        assert 'phases' in result
        assert 'testing_strategy' in result
        assert 'monitoring' in result
        assert 'rollback_plan' in result
        
        # Verify phases structure
        phases = result['phases']
        assert isinstance(phases, list)
        if phases:
            phase = phases[0]
            assert 'phase' in phase
            assert 'name' in phase
            assert 'description' in phase
            assert 'duration' in phase
            assert 'services' in phase
            assert 'steps' in phase
            assert 'rollback' in phase

    @pytest.mark.asyncio
    async def test_generate_brownfield_c4_diagram(self, architecture_agent, sample_existing_architecture):
        """Test generating brownfield C4 diagram."""
        architecture_data = {
            'new_services': [
                {
                    'id': 'notification-service',
                    'name': 'Notification Service',
                    'type': 'service'
                }
            ],
            'modified_services': [
                {
                    'id': 'user-service',
                    'name': 'User Service',
                    'type': 'service'
                }
            ]
        }
        
        context = {
            'existing_services': sample_existing_architecture['services'],
            'integration_points': [
                {
                    'from_service': 'user-service',
                    'to_service': 'notification-service',
                    'type': 'event-stream'
                }
            ]
        }
        
        result = await architecture_agent._generate_brownfield_c4_diagram(
            architecture_data, context
        )
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'graph' in result.lower() or 'diagram' in result.lower()

    def test_assess_context_quality(self, architecture_agent):
        """Test assessing the quality of brownfield context."""
        # High quality context
        high_quality_context = {
            'similar_architectures': [
                {'similarity_score': 0.9},
                {'similarity_score': 0.8}
            ],
            'existing_services': [
                {'id': 'service-1', 'technology': 'Node.js'},
                {'id': 'service-2', 'technology': 'PostgreSQL'}
            ],
            'integration_patterns': [
                {'pattern': 'event-driven'},
                {'pattern': 'api-gateway'}
            ],
            'technology_consistency': 0.9
        }
        
        quality = architecture_agent._assess_context_quality(high_quality_context)
        assert quality > 0.7
        
        # Low quality context
        low_quality_context = {
            'similar_architectures': [],
            'existing_services': [],
            'integration_patterns': [],
            'technology_consistency': 0.3
        }
        
        quality = architecture_agent._assess_context_quality(low_quality_context)
        assert quality < 0.5

    def test_get_agent_capabilities_with_kb_service(self, architecture_agent):
        """Test agent capabilities when knowledge base service is available."""
        capabilities = architecture_agent.get_agent_capabilities()
        
        assert 'Brownfield architecture design' in capabilities['capabilities']
        assert 'RAG-based context integration' in capabilities['capabilities']
        assert 'Integration strategy generation' in capabilities['capabilities']
        assert 'brownfield' in capabilities['modes']
        assert capabilities['knowledge_base_integration'] is True

    def test_get_agent_capabilities_without_kb_service(self):
        """Test agent capabilities when knowledge base service is not available."""
        with patch('app.config.settings') as mock_settings:
            mock_settings.get_llm_config_for_task.return_value = ('deepseek', 'deepseek-r1')
            agent = ArchitectureAgent()
            
            capabilities = agent.get_agent_capabilities()
            
            assert 'Brownfield architecture design' not in capabilities['capabilities']
            assert capabilities['knowledge_base_integration'] is False

    @pytest.mark.asyncio
    async def test_execute_brownfield_with_high_confidence_context(self, architecture_agent, sample_requirements, sample_existing_architecture):
        """Test brownfield execution with high confidence context."""
        # Mock high confidence context
        high_confidence_context = {
            'similar_architectures': [
                {'similarity_score': 0.9, 'metadata': {'technologies': ['Node.js']}}
            ],
            'existing_services': sample_existing_architecture['services'],
            'integration_patterns': [
                {'pattern': 'event-driven', 'confidence': 0.9}
            ],
            'technology_consistency': 0.95
        }
        
        architecture_agent._get_brownfield_context = AsyncMock(return_value=high_confidence_context)
        architecture_agent._call_llm = AsyncMock(return_value='{"architecture": {"style": "microservices"}}')
        architecture_agent._parse_json_response = Mock(return_value={'architecture': {'style': 'microservices'}})
        architecture_agent._generate_brownfield_c4_diagram = AsyncMock(return_value='graph TD')
        architecture_agent._generate_integration_strategy = AsyncMock(return_value={'phases': []})
        architecture_agent._validate_and_enhance_architecture = Mock(return_value={'architecture': {'style': 'microservices'}})
        
        input_data = {
            'project_id': 'test-project',
            'requirements': sample_requirements,
            'existing_architecture': sample_existing_architecture,
            'constraints': {},
            'preferences': [],
            'domain': 'e-commerce'
        }
        
        result = await architecture_agent._execute_brownfield(input_data)
        
        assert 'architecture' in result
        assert 'integration_strategy' in result
        assert 'context_quality' in result
        assert result['context_quality'] > 0.7

    @pytest.mark.asyncio
    async def test_execute_brownfield_with_low_confidence_context(self, architecture_agent, sample_requirements, sample_existing_architecture):
        """Test brownfield execution with low confidence context."""
        # Mock low confidence context
        low_confidence_context = {
            'similar_architectures': [],
            'existing_services': [],
            'integration_patterns': [],
            'technology_consistency': 0.3
        }
        
        architecture_agent._get_brownfield_context = AsyncMock(return_value=low_confidence_context)
        architecture_agent._call_llm = AsyncMock(return_value='{"architecture": {"style": "microservices"}}')
        architecture_agent._parse_json_response = Mock(return_value={'architecture': {'style': 'microservices'}})
        architecture_agent._generate_brownfield_c4_diagram = AsyncMock(return_value='graph TD')
        architecture_agent._generate_integration_strategy = AsyncMock(return_value={
            'phases': [{'name': 'Phase 1', 'description': 'Initial integration'}],
            'timeline': '2 weeks',
            'risks': ['Low risk integration']
        })
        architecture_agent._validate_and_enhance_architecture = Mock(return_value={
            'architecture': {'style': 'microservices'},
            'integration_strategy': {
                'phases': [{'name': 'Phase 1', 'description': 'Initial integration'}],
                'timeline': '2 weeks',
                'risks': ['Low risk integration']
            }
        })
        
        input_data = {
            'project_id': 'test-project',
            'requirements': sample_requirements,
            'existing_architecture': sample_existing_architecture,
            'constraints': {},
            'preferences': [],
            'domain': 'e-commerce'
        }
        
        result = await architecture_agent._execute_brownfield(input_data)
        
        assert 'architecture' in result
        assert 'integration_strategy' in result
        assert 'metadata' in result
        assert 'context_quality' in result['metadata']
        assert result['metadata']['context_quality'] == 'low'
        assert 'design_notes' in result['metadata']
        assert len(result['metadata']['design_notes']) > 0

    @pytest.mark.asyncio
    async def test_brownfield_context_with_empty_kb_service(self):
        """Test brownfield context when knowledge base service returns empty results."""
        mock_kb_service = Mock()
        mock_kb_service.search_similar_architectures = AsyncMock(return_value=[])
        mock_kb_service.get_service_dependencies = AsyncMock(return_value=[])
        mock_kb_service.get_context_for_new_feature = AsyncMock(return_value={
            'similar_features': [],
            'existing_services': [],
            'integration_patterns': []
        })
        
        with patch('app.config.settings') as mock_settings:
            mock_settings.get_llm_config_for_task.return_value = ('deepseek', 'deepseek-r1')
            agent = ArchitectureAgent(knowledge_base_service=mock_kb_service)
            
            context = await agent._get_brownfield_context(
                'test-project', {}, {}
            )
            
            assert context['similar_architectures'] == []
            assert context['existing_services'] == []
            assert context['integration_patterns'] == []
            assert context['technology_consistency'] == 0.0
