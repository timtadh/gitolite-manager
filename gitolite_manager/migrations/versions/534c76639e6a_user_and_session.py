"""user and session

Revision ID: 534c76639e6a
Revises: 5ab577a9406e
Create Date: 2014-08-07 11:04:41.828517

"""

# revision identifiers, used by Alembic.
revision = '534c76639e6a'
down_revision = '5ab577a9406e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('access', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=True)
    op.create_table('session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=64), nullable=True),
    sa.Column('sig', sa.LargeBinary(length=32), nullable=True),
    sa.Column('sigkey', sa.LargeBinary(length=32), nullable=True),
    sa.Column('micro', sa.LargeBinary(length=3), nullable=True),
    sa.Column('csrf', sa.LargeBinary(length=32), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('last_update', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_session_id'), 'session', ['id'], unique=True)
    op.create_index(op.f('ix_session_key'), 'session', ['key'], unique=True)
    op.create_index(op.f('ix_session_last_update'), 'session', ['last_update'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_session_last_update'), table_name='session')
    op.drop_index(op.f('ix_session_key'), table_name='session')
    op.drop_index(op.f('ix_session_id'), table_name='session')
    op.drop_table('session')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    ### end Alembic commands ###