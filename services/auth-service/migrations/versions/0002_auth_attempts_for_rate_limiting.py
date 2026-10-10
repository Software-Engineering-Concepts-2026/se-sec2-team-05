"""auth attempts for rate limiting

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-09

ตาราง `auth_attempts` ตัวนับของ rate limit ที่ login และสมัครสมาชิก (ADR-011) สร้างจาก
`alembic revision --autogenerate` แล้วเปลี่ยน index จาก batch mode เป็น `op.create_index` ธรรมดา
(ตารางใหม่ไม่ต้อง copy ข้อมูล ใช้ได้ทั้ง SQLite และ Postgres) · ตารางใหม่ล้วน ไม่แตะข้อมูลเดิม
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('auth_attempts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('kind', sa.String(length=20), nullable=False),
    sa.Column('key', sa.String(length=300), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_auth_attempts_kind_key_created', 'auth_attempts', ['kind', 'key', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_auth_attempts_kind_key_created', table_name='auth_attempts')
    op.drop_table('auth_attempts')
