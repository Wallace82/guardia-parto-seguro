"""Initial tables

Revision ID: 0001_initial_tables
Revises: 
Create Date: 2026-06-18 18:28:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial_tables'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tabela users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('admin', 'gestor', 'profissional', 'auditor', name='user_role'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(op.f('idx_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('idx_users_id'), 'users', ['id'], unique=False)

    # 2. Tabela refresh_tokens
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('idx_refresh_tokens_id'), 'refresh_tokens', ['id'], unique=False)
    op.create_index(op.f('idx_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=True)

    # 3. Tabela sessions
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('patient_code', sa.String(length=64), nullable=False),
        sa.Column('professional_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'completed', 'error', name='session_status'), nullable=False),
        sa.Column('ira_score', sa.Float(), nullable=True),
        sa.Column('ira_level', sa.String(length=20), nullable=True),
        sa.Column('score_video', sa.Float(), nullable=True),
        sa.Column('score_audio', sa.Float(), nullable=True),
        sa.Column('score_document', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['professional_id'], ['users.id']),
    )
    op.create_index(op.f('idx_sessions_id'), 'sessions', ['id'], unique=False)
    op.create_index(op.f('idx_sessions_patient_code'), 'sessions', ['patient_code'], unique=False)
    op.create_index(op.f('idx_sessions_professional_id'), 'sessions', ['professional_id'], unique=False)

    # 4. Tabela media_files
    op.create_table(
        'media_files',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('media_type', sa.Enum('video', 'audio', 'document', name='media_type'), nullable=False),
        sa.Column('filename', sa.String(length=512), nullable=False),
        sa.Column('blob_url', sa.String(length=1024), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('content_type', sa.String(length=128), nullable=True),
        sa.Column('status', sa.Enum('uploaded', 'processing', 'analyzed', 'error', name='media_status'), nullable=False),
        sa.Column('analysis_score', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('idx_media_files_id'), 'media_files', ['id'], unique=False)
    op.create_index(op.f('idx_media_files_session_id'), 'media_files', ['session_id'], unique=False)

    # 5. Tabela alerts
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.Enum('ira_threshold', 'video_anomaly', 'audio_keyword', 'document_inconsistency', 'missing_consent', name='alert_type'), nullable=False),
        sa.Column('severity', sa.Enum('moderate', 'critical', name='alert_severity'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('ira_score', sa.Float(), nullable=True),
        sa.Column('is_acknowledged', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('acknowledged_by', sa.Integer(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['acknowledged_by'], ['users.id']),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('idx_alerts_created_at'), 'alerts', ['created_at'], unique=False)
    op.create_index(op.f('idx_alerts_id'), 'alerts', ['id'], unique=False)
    op.create_index(op.f('idx_alerts_session_id'), 'alerts', ['session_id'], unique=False)


def downgrade() -> None:
    op.drop_table('alerts')
    op.drop_table('media_files')
    op.drop_table('sessions')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
    
    # Remover enums se necessário, mas dependendo do dialeto Postgres eles podem ser removidos com drop_table ou explicitamente:
    sa.Enum(name='user_role').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='session_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='media_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='media_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='alert_type').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='alert_severity').drop(op.get_bind(), checkfirst=True)
