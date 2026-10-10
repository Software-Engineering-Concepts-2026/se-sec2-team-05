"""drop notes.edit_token_hash

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-09

edit token ต่อโน้ต (ADR-004) เลิกใช้แล้ว การแก้/ลบต้อง login เป็นเจ้าของ (ADR-013) จึงลบคอลัมน์ hash ทิ้ง
ใช้ batch_alter_table เพราะ SQLite ลบคอลัมน์ในตารางเดิมได้แค่ด้วยการสร้างตารางใหม่ (บน Postgres เป็น ALTER ธรรมดา)
downgrade ใส่คอลัมน์กลับเป็นค่าว่าง — hash เดิมกู้คืนไม่ได้ โน้ตที่มีอยู่จึงแก้ด้วย token ไม่ได้อีก
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
    with op.batch_alter_table('notes') as batch_op:
        batch_op.drop_column('edit_token_hash')


def downgrade() -> None:
    with op.batch_alter_table('notes') as batch_op:
        batch_op.add_column(
            sa.Column('edit_token_hash', sa.String(length=64), nullable=False, server_default='')
        )
