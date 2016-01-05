"""Add AuthUser table

Revision ID: 28eac0b42e2c
Revises: 4367a35b6f55
Create Date: 2015-12-01 16:18:26.249966

"""

# revision identifiers, used by Alembic.
revision = '28eac0b42e2c'
down_revision = '4367a35b6f55'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'auth_user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(20), index=True),
        sa.Column('password_hash', sa.String(64))
    )


def downgrade():
    op.drop_table('auth_user')
