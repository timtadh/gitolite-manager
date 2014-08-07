"""repos and keys

Revision ID: 44c3b899636d
Revises: 534c76639e6a
Create Date: 2014-08-07 16:51:07.865812

"""

# revision identifiers, used by Alembic.
revision = '44c3b899636d'
down_revision = '534c76639e6a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('key',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('key', sa.String(length=1000), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_key_id'), 'key', ['id'], unique=True)
    op.create_index(op.f('ix_key_user_id'), 'key', ['user_id'], unique=False)
    op.create_table('repo',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('partner_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.ForeignKeyConstraint(['partner_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    mysql_engine='InnoDB'
    )
    op.create_index(op.f('ix_repo_id'), 'repo', ['id'], unique=True)
    op.create_index(op.f('ix_repo_partner_id'), 'repo', ['partner_id'], unique=False)
    op.create_index(op.f('ix_repo_user_id'), 'repo', ['user_id'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_repo_user_id'), table_name='repo')
    op.drop_index(op.f('ix_repo_partner_id'), table_name='repo')
    op.drop_index(op.f('ix_repo_id'), table_name='repo')
    op.drop_table('repo')
    op.drop_index(op.f('ix_key_user_id'), table_name='key')
    op.drop_index(op.f('ix_key_id'), table_name='key')
    op.drop_table('key')
    ### end Alembic commands ###
