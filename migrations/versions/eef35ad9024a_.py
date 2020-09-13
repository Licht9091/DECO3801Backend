"""empty message

Revision ID: eef35ad9024a
Revises: aa4c51d72d3f
Create Date: 2020-09-12 05:25:20.752832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eef35ad9024a'
down_revision = 'aa4c51d72d3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('goals', sa.Column('description', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('goals', 'description')
    # ### end Alembic commands ###