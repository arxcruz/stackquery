"""Removing projects dependence for teams

Revision ID: 441c8759a37b
Revises: 28eac0b42e2c
Create Date: 2015-12-08 16:41:43.312232

"""

# revision identifiers, used by Alembic.
revision = '441c8759a37b'
down_revision = '28eac0b42e2c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_table('project_team_association')


def downgrade():
    op.create_table('project_team_association',
                    sa.Column('project_id', sa.INTEGER(), nullable=True),
                    sa.Column('team_id', sa.INTEGER(), nullable=True),
                    sa.ForeignKeyConstraint(['project_id'], [u'projects.id'],),
                    sa.ForeignKeyConstraint(['team_id'], [u'team.id'],)
                    )
