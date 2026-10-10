"""add comments.author_name

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-11

หน้าโน้ตเคยแสดงผู้เขียนความคิดเห็นของคนอื่นเป็น "สมาชิก" ทุกคน เพราะ comments เก็บแค่ user_id
และตาราง users เป็นของ auth-service (ADR-005) จึงเก็บชื่อที่แสดง ณ ตอนโพสต์ไว้ในแถวเอง แบบเดียวกับ notes.uploader_name
คอลัมน์ว่างได้ ความคิดเห็นเดิมไม่มีชื่อ (หน้าเว็บยังแสดงเป็น "สมาชิก")
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('comments') as batch_op:
        batch_op.add_column(sa.Column('author_name', sa.String(length=120), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('comments') as batch_op:
        batch_op.drop_column('author_name')
