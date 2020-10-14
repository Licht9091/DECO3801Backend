"""empty message

Revision ID: 78ff77e5ff91
Revises: 5b33fde0b3f0
Create Date: 2020-10-14 13:57:15.363098

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78ff77e5ff91'
down_revision = '5b33fde0b3f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('goals', sa.Column('fortnightlyContribution', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('goals', 'fortnightlyContribution')
    # ### end Alembic commands ###