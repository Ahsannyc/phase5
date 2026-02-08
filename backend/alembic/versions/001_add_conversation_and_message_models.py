"""Add Conversation and Message models.

Revision ID: 001
Revises: 
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversation_user_id'), 'conversation', ['user_id'], unique=False)
    op.create_index(op.f('ix_conversation_created_at'), 'conversation', ['created_at'], unique=False)

    # Create messages table
    op.create_table(
        'message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('tool_calls', sa.String(), nullable=True),
        sa.Column('tool_responses', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversation.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_message_conversation_id'), 'message', ['conversation_id'], unique=False)
    op.create_index(op.f('ix_message_user_id'), 'message', ['user_id'], unique=False)
    op.create_index(op.f('ix_message_created_at'), 'message', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_message_created_at'), table_name='message')
    op.drop_index(op.f('ix_message_user_id'), table_name='message')
    op.drop_index(op.f('ix_message_conversation_id'), table_name='message')
    op.drop_table('message')
    op.drop_index(op.f('ix_conversation_created_at'), table_name='conversation')
    op.drop_index(op.f('ix_conversation_user_id'), table_name='conversation')
    op.drop_table('conversation')
