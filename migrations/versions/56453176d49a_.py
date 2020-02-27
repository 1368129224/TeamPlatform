"""empty message

Revision ID: 56453176d49a
Revises: 9771d83c6f0a
Create Date: 2020-02-26 15:10:33.595033

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '56453176d49a'
down_revision = '9771d83c6f0a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Team', sa.Column('user_id', sa.Integer(), nullable=True))
    op.drop_constraint('Team_ibfk_1', 'Team', type_='foreignkey')
    op.create_foreign_key(None, 'Team', 'User', ['user_id'], ['id'])
    op.drop_column('Team', 'uid')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Team', sa.Column('uid', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'Team', type_='foreignkey')
    op.create_foreign_key('Team_ibfk_1', 'Team', 'User', ['uid'], ['id'])
    op.drop_column('Team', 'user_id')
    # ### end Alembic commands ###
