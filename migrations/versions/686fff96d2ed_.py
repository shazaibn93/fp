"""empty message

Revision ID: 686fff96d2ed
Revises: 617bded22462
Create Date: 2022-03-21 22:39:52.052178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '686fff96d2ed'
down_revision = '617bded22462'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('team_color', sa.String(length=10), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player', 'team_color')
    # ### end Alembic commands ###