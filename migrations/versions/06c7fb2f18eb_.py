"""empty message
Revision ID: 06c7fb2f18eb
Revises: f793b257899d
Create Date: 2020-08-31 18:02:43.042968
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '06c7fb2f18eb'
down_revision = 'f793b257899d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('goals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('goalStartDate', sa.DateTime(), nullable=True),
    sa.Column('goalEndDate', sa.DateTime(), nullable=True),
    sa.Column('goalAmount', sa.Integer(), nullable=True),
    sa.Column('totalContribution', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userId', sa.Integer(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('value', sa.Float(), nullable=True),
    sa.Column('category', sa.String(length=255), nullable=True),
    sa.Column('goalId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['goalId'], ['goals.id'], ),
    sa.ForeignKeyConstraint(['userId'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transactions')
    op.drop_table('goals')
    # ### end Alembic commands ###