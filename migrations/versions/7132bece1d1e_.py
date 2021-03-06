"""empty message

Revision ID: 7132bece1d1e
Revises: 77d78954e63c
Create Date: 2022-03-18 03:01:09.357067

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7132bece1d1e'
down_revision = '77d78954e63c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('pic', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player', 'pic')
    # ### end Alembic commands ###
