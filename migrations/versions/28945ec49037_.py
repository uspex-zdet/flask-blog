"""empty message

Revision ID: 28945ec49037
Revises: ca61cb04704f
Create Date: 2023-12-27 06:53:04.176050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28945ec49037'
down_revision = 'ca61cb04704f'
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
    sa.ForeignKeyConstraint(['username'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post_likes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment_likes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('comment_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('views', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('slug', sa.String(), nullable=True))
        batch_op.alter_column('title',
               existing_type=sa.VARCHAR(length=100),
               type_=sa.String(length=200),
               existing_nullable=False)
        batch_op.create_index(batch_op.f('ix_posts_slug'), ['slug'], unique=True)
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_role'), ['role'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_role'))
        batch_op.drop_column('last_seen')
        batch_op.drop_column('role')

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'])
        batch_op.drop_index(batch_op.f('ix_posts_slug'))
        batch_op.alter_column('title',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=100),
               existing_nullable=False)
        batch_op.drop_column('slug')
        batch_op.drop_column('views')
        batch_op.drop_column('category')

    op.drop_table('comment_likes')
    op.drop_table('tags')
    op.drop_table('post_likes')
    op.drop_table('comments')
    # ### end Alembic commands ###