"""empty message

Revision ID: f3dbbc66955f
Revises: be888448c343
Create Date: 2020-02-27 10:27:59.537535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f3dbbc66955f'
down_revision = 'be888448c343'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Team', sa.Column('activity_id', sa.Integer(), nullable=True))
    op.add_column('Team', sa.Column('teammate_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'Team', 'User', ['teammate_id'], ['id'])
    op.create_foreign_key(None, 'Team', 'Activity', ['activity_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Team', type_='foreignkey')
    op.drop_constraint(None, 'Team', type_='foreignkey')
    op.drop_column('Team', 'teammate_id')
    op.drop_column('Team', 'activity_id')
    # ### end Alembic commands ###
