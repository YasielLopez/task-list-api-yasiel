"""Add goal model

Revision ID: 3a9848e193f2
Revises: b98ba1ca0dea
Create Date: 2025-05-09 05:08:10.978640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a9848e193f2'
down_revision = 'b98ba1ca0dea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('goal_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'goal', ['goal_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('goal_id')

    # ### end Alembic commands ###
