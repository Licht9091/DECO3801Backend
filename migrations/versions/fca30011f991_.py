"""empty message

Revision ID: fca30011f991
Revises: 66942934361d
Create Date: 2020-09-16 09:49:55.580812

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fca30011f991'
down_revision = '66942934361d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('transactionId', sa.Integer(), nullable=True),
    sa.Column('goalId', sa.Integer(), nullable=True),
    sa.Column('ammount', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['goalId'], ['goals.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['transactionId'], ['transactions.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transaction_categories')
    # ### end Alembic commands ###