"""Initial models

Revision ID: 5e773634e401
Revises: 
Create Date: 2025-10-16 13:23:44.082823

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5e773634e401'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum types
    project_domain = postgresql.ENUM('cloud-native', 'data-platform', 'enterprise', name='projectdomain')
    project_domain.create(op.get_bind())
    
    project_status = postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='projectstatus')
    project_status.create(op.get_bind())
    
    requirement_status = postgresql.ENUM('pending', 'processed', 'approved', 'rejected', name='requirementstatus')
    requirement_status.create(op.get_bind())
    
    architecture_status = postgresql.ENUM('pending', 'approved', 'rejected', name='architecturesstatus')
    architecture_status.create(op.get_bind())
    
    agent_execution_status = postgresql.ENUM('success', 'failure', 'timeout', name='agentexecutionstatus')
    agent_execution_status.create(op.get_bind())
    
    # Create projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('domain', project_domain, nullable=False),
        sa.Column('status', project_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_projects_created_at', 'projects', ['created_at'], unique=False)
    op.create_index('idx_projects_domain', 'projects', ['domain'], unique=False)
    op.create_index('idx_projects_name', 'projects', ['name'], unique=False)
    op.create_index('idx_projects_status', 'projects', ['status'], unique=False)
    
    # Create requirements table
    op.create_table('requirements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('raw_documents', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('structured_requirements', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('clarification_questions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('status', requirement_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_requirements_clarification_questions_gin', 'requirements', ['clarification_questions'], unique=False, postgresql_using='gin')
    op.create_index('idx_requirements_confidence_score', 'requirements', ['confidence_score'], unique=False)
    op.create_index('idx_requirements_created_at', 'requirements', ['created_at'], unique=False)
    op.create_index('idx_requirements_project_id', 'requirements', ['project_id'], unique=False)
    op.create_index('idx_requirements_raw_documents_gin', 'requirements', ['raw_documents'], unique=False, postgresql_using='gin')
    op.create_index('idx_requirements_status', 'requirements', ['status'], unique=False)
    op.create_index('idx_requirements_structured_requirements_gin', 'requirements', ['structured_requirements'], unique=False, postgresql_using='gin')
    
    # Create architectures table
    op.create_table('architectures',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('requirement_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('architecture_style', sa.String(length=255), nullable=True),
        sa.Column('components', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('c4_diagrams', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('technology_stack', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('alternatives', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', architecture_status, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requirement_id'], ['requirements.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_architectures_alternatives_gin', 'architectures', ['alternatives'], unique=False, postgresql_using='gin')
    op.create_index('idx_architectures_c4_diagrams_gin', 'architectures', ['c4_diagrams'], unique=False, postgresql_using='gin')
    op.create_index('idx_architectures_components_gin', 'architectures', ['components'], unique=False, postgresql_using='gin')
    op.create_index('idx_architectures_created_at', 'architectures', ['created_at'], unique=False)
    op.create_index('idx_architectures_project_id', 'architectures', ['project_id'], unique=False)
    op.create_index('idx_architectures_requirement_id', 'architectures', ['requirement_id'], unique=False)
    op.create_index('idx_architectures_status', 'architectures', ['status'], unique=False)
    op.create_index('idx_architectures_style', 'architectures', ['architecture_style'], unique=False)
    op.create_index('idx_architectures_technology_stack_gin', 'architectures', ['technology_stack'], unique=False, postgresql_using='gin')
    
    # Create workflow_sessions table
    op.create_table('workflow_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('current_stage', sa.String(length=255), nullable=True),
        sa.Column('state_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_workflow_sessions_completed_at', 'workflow_sessions', ['completed_at'], unique=False)
    op.create_index('idx_workflow_sessions_current_stage', 'workflow_sessions', ['current_stage'], unique=False)
    op.create_index('idx_workflow_sessions_is_active', 'workflow_sessions', ['is_active'], unique=False)
    op.create_index('idx_workflow_sessions_last_activity', 'workflow_sessions', ['last_activity'], unique=False)
    op.create_index('idx_workflow_sessions_project_id', 'workflow_sessions', ['project_id'], unique=False)
    op.create_index('idx_workflow_sessions_started_at', 'workflow_sessions', ['started_at'], unique=False)
    op.create_index('idx_workflow_sessions_state_data_gin', 'workflow_sessions', ['state_data'], unique=False, postgresql_using='gin')
    
    # Create agent_executions table
    op.create_table('agent_executions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_type', sa.String(length=255), nullable=False),
        sa.Column('agent_version', sa.String(length=50), nullable=True),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('llm_provider', sa.String(length=100), nullable=True),
        sa.Column('llm_model', sa.String(length=100), nullable=True),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('duration_seconds', sa.Float(), nullable=True),
        sa.Column('status', agent_execution_status, nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['workflow_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_agent_executions_agent_type', 'agent_executions', ['agent_type'], unique=False)
    op.create_index('idx_agent_executions_completed_at', 'agent_executions', ['completed_at'], unique=False)
    op.create_index('idx_agent_executions_cost_usd', 'agent_executions', ['cost_usd'], unique=False)
    op.create_index('idx_agent_executions_duration_seconds', 'agent_executions', ['duration_seconds'], unique=False)
    op.create_index('idx_agent_executions_input_data_gin', 'agent_executions', ['input_data'], unique=False, postgresql_using='gin')
    op.create_index('idx_agent_executions_llm_model', 'agent_executions', ['llm_model'], unique=False)
    op.create_index('idx_agent_executions_llm_provider', 'agent_executions', ['llm_provider'], unique=False)
    op.create_index('idx_agent_executions_output_data_gin', 'agent_executions', ['output_data'], unique=False, postgresql_using='gin')
    op.create_index('idx_agent_executions_session_id', 'agent_executions', ['session_id'], unique=False)
    op.create_index('idx_agent_executions_started_at', 'agent_executions', ['started_at'], unique=False)
    op.create_index('idx_agent_executions_status', 'agent_executions', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables in reverse order
    op.drop_table('agent_executions')
    op.drop_table('workflow_sessions')
    op.drop_table('architectures')
    op.drop_table('requirements')
    op.drop_table('projects')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS agentexecutionstatus')
    op.execute('DROP TYPE IF EXISTS architecturesstatus')
    op.execute('DROP TYPE IF EXISTS requirementstatus')
    op.execute('DROP TYPE IF EXISTS projectstatus')
    op.execute('DROP TYPE IF EXISTS projectdomain')
