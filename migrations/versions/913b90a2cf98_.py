"""empty message

Revision ID: 913b90a2cf98
Revises: 94bddbade28d
Create Date: 2020-06-22 16:28:10.066178

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '913b90a2cf98'
down_revision = '94bddbade28d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('artist_image_link', sa.String(length=500), nullable=True))
    op.add_column('Show', sa.Column('artist_name', sa.String(), nullable=True))
    op.add_column('Show', sa.Column('venue_name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Show', 'venue_name')
    op.drop_column('Show', 'artist_name')
    op.drop_column('Show', 'artist_image_link')
    # ### end Alembic commands ###