"""empty message

Revision ID: cd09005b19a6
Revises: eef35ad9024a
Create Date: 2020-09-13 03:13:03.786868

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'cd09005b19a6'
down_revision = 'eef35ad9024a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('goals', 'userId',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    op.create_foreign_key(None, 'goals', 'users', ['userId'], ['id'], ondelete='SET NULL')
    op.drop_constraint('transactions_ibfk_3', 'transactions', type_='foreignkey')
    op.create_foreign_key(None, 'transactions', 'goals', ['goalId'], ['id'], ondelete='SET NULL')
    op.drop_constraint('users_ibfk_1', 'users', type_='foreignkey')
    op.create_foreign_key(None, 'users', 'bankaccounts', ['bankAccountId'], ['accountNumber'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.create_foreign_key('users_ibfk_1', 'users', 'bankaccounts', ['bankAccountId'], ['accountNumber'], ondelete='CASCADE')
    op.drop_constraint(None, 'transactions', type_='foreignkey')
    op.create_foreign_key('transactions_ibfk_3', 'transactions', 'goals', ['goalId'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'goals', type_='foreignkey')
    op.alter_column('goals', 'userId',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    # ### end Alembic commands ###