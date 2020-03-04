"""empty message

Revision ID: b568f7687093
Revises: d534ab0651e1
Create Date: 2020-03-04 21:20:22.001016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b568f7687093'
down_revision = 'd534ab0651e1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Team', sa.Column('leader_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'Team', 'User', ['leader_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Team', type_='foreignkey')
    op.drop_column('Team', 'leader_id')
    # ### end Alembic commands ###
