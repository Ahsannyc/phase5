"""extend_task_intermediate_advanced_features

Revision ID: 72c57bf36b0f
Revises: 001
Create Date: 2026-02-09 03:46:14.186930

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '72c57bf36b0f'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add Phase 5 Part A columns and indexes to task table."""
    # Add new columns for intermediate features
    op.add_column('task', sa.Column('priority', sa.VARCHAR(20), nullable=False, server_default='medium'))
    op.add_column('task', sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'))

    # Add new columns for advanced features
    op.add_column('task', sa.Column('due_date', sa.DateTime(), nullable=True))
    op.add_column('task', sa.Column('recurrence_rule', sa.VARCHAR(255), nullable=True))
    op.add_column('task', sa.Column('reminder_offset', sa.Integer(), nullable=True))

    # Create performance indexes
    op.create_index('idx_task_priority', 'task', ['priority'])
    op.create_index('idx_task_due_date', 'task', ['due_date'])
    op.create_index('idx_task_recurrence_rule', 'task', ['recurrence_rule'])
    op.create_index('idx_task_tags', 'task', ['tags'], postgresql_using='gin')
    op.create_index('idx_task_user_status', 'task', ['user_id', 'status'])


def downgrade() -> None:
    """Remove Phase 5 Part A columns and indexes from task table."""
    # Drop indexes first
    op.drop_index('idx_task_user_status', table_name='task')
    op.drop_index('idx_task_tags', table_name='task', postgresql_using='gin')
    op.drop_index('idx_task_recurrence_rule', table_name='task')
    op.drop_index('idx_task_due_date', table_name='task')
    op.drop_index('idx_task_priority', table_name='task')

    # Drop columns
    op.drop_column('task', 'reminder_offset')
    op.drop_column('task', 'recurrence_rule')
    op.drop_column('task', 'due_date')
    op.drop_column('task', 'tags')
    op.drop_column('task', 'priority')