"""add system settings

Revision ID: 4f3b1e9c9a2a
Revises: e8cabed9172c
Create Date: 2026-07-15 14:10:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4f3b1e9c9a2a'
down_revision = 'e8cabed9172c'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('system_settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email_alerts', sa.Boolean(), nullable=True, default=True),
    sa.Column('push_notifications', sa.Boolean(), nullable=True, default=False),
    sa.Column('strict_mode', sa.Boolean(), nullable=True, default=True),
    sa.Column('auto_process_audio', sa.Boolean(), nullable=True, default=True),
    sa.Column('retention_days', sa.Integer(), nullable=True, default=180),
    sa.Column('timeout_minutes', sa.Integer(), nullable=True, default=30),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_settings_id'), 'system_settings', ['id'], unique=False)
    
    # insert initial settings
    op.execute(
        "INSERT INTO system_settings (id, email_alerts, push_notifications, strict_mode, auto_process_audio, retention_days, timeout_minutes) "
        "VALUES (1, true, false, true, true, 180, 30)"
    )

def downgrade() -> None:
    op.drop_index(op.f('ix_system_settings_id'), table_name='system_settings')
    op.drop_table('system_settings')
