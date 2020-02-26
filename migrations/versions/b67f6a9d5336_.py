"""empty message

Revision ID: b67f6a9d5336
Revises: 
Create Date: 2020-02-26 14:47:45.525762

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b67f6a9d5336'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Activity',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='活动ID'),
    sa.Column('desc', sa.String(length=256), nullable=False, comment='活动内容'),
    sa.Column('datetime', sa.DateTime(), nullable=True, comment='开始时间'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Note',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='记录ID'),
    sa.Column('content', sa.String(length=256), nullable=True, comment='记录内容'),
    sa.Column('datetime', sa.DateTime(), nullable=True, comment='创建时间'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Team',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_name', sa.String(length=32), nullable=False, comment='小组名'),
    sa.Column('desc', sa.String(length=256), nullable=True, comment='小组简介'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('team_name')
    )
    op.create_table('User',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='用户ID'),
    sa.Column('username', sa.String(length=64), nullable=False, comment='用户名'),
    sa.Column('email', sa.String(length=64), nullable=False, comment='邮箱'),
    sa.Column('stu_num', sa.String(length=32), nullable=False, comment='学号'),
    sa.Column('password', sa.String(length=128), nullable=False, comment='密码'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('stu_num'),
    sa.UniqueConstraint('username')
    )
    op.create_table('Project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('desc', sa.String(length=256), nullable=True, comment='项目简介'),
    sa.ForeignKeyConstraint(['team_id'], ['Team.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('UserPermission',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uid', sa.Integer(), nullable=True),
    sa.Column('manage_lab_task', sa.Boolean(), nullable=True, comment='管理实验室事务'),
    sa.Column('change_set', sa.Boolean(), nullable=True, comment='修改座位'),
    sa.Column('verify_asset', sa.Boolean(), nullable=True, comment='资产审核'),
    sa.Column('change_lab_info', sa.Boolean(), nullable=True, comment='修改实验室信息'),
    sa.Column('publish_lab_activity', sa.Boolean(), nullable=True, comment='发布实验室活动'),
    sa.Column('change_team_info', sa.Boolean(), nullable=True, comment='修改组信息'),
    sa.Column('publish_team_activity', sa.Boolean(), nullable=True, comment='发布组活动'),
    sa.ForeignKeyConstraint(['uid'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('UserProfile',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uid', sa.Integer(), nullable=True),
    sa.Column('phone', sa.String(length=11), nullable=False, comment='电话'),
    sa.Column('college', sa.String(length=32), nullable=False, comment='专业'),
    sa.Column('grade', sa.String(length=4), nullable=False, comment='年级'),
    sa.Column('_class', sa.String(length=2), nullable=False, comment='班级'),
    sa.ForeignKeyConstraint(['uid'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone')
    )
    op.create_table('Item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=True),
    sa.Column('item_type', sa.Enum('需求', 'bug'), server_default='需求', nullable=False, comment='类型'),
    sa.Column('desc', sa.String(length=256), nullable=True, comment='描述'),
    sa.Column('create_time', sa.DateTime(), nullable=True, comment='创建时间'),
    sa.Column('status', sa.Enum('待处理', '开发中', '测试中', '已处理'), server_default='待处理', nullable=False, comment='状态'),
    sa.Column('priority', sa.Enum('低', '普通', '高', '紧急'), server_default='普通', nullable=False, comment='优先级'),
    sa.ForeignKeyConstraint(['project_id'], ['Project.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Item')
    op.drop_table('UserProfile')
    op.drop_table('UserPermission')
    op.drop_table('Project')
    op.drop_table('User')
    op.drop_table('Team')
    op.drop_table('Note')
    op.drop_table('Activity')
    # ### end Alembic commands ###
