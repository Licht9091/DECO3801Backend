"""empty message

Revision ID: 5b33fde0b3f0
Revises: fca30011f991
Create Date: 2020-10-12 10:40:47.050423

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b33fde0b3f0'
down_revision = 'fca30011f991'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('budget_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('ammount', sa.Float(), nullable=True),
    sa.Column('tag', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('budget_items')
    # ### end Alembic commands ###