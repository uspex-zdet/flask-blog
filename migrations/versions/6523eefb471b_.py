"""empty message

Revision ID: 6523eefb471b
Revises: 1a82e0ff3d83
Create Date: 2023-11-17 16:19:28.862889

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6523eefb471b'
down_revision = '1a82e0ff3d83'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=20), nullable=False),
    sa.Column('body', sa.Text(length=200), nullable=False),
    sa.Column('date_posted', sa.DateTime(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comments')
    # ### end Alembic commands ###