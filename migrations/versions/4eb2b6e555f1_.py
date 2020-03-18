"""empty message

Revision ID: 4eb2b6e555f1
Revises: 28a3cffecd20
Create Date: 2020-03-18 10:06:28.399107

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4eb2b6e555f1'
down_revision = '28a3cffecd20'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('User', 'set_num')
    op.add_column('UserProfile', sa.Column('set_num', sa.Integer(), nullable=True, comment='座位号'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('UserProfile', 'set_num')
    op.add_column('User', sa.Column('set_num', mysql.INTEGER(), autoincrement=False, nullable=True, comment='座位号'))
    # ### end Alembic commands ###
