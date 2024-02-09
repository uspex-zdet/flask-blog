"""
This file (test_models.py) contains the unit tests for the models.py file.
"""

from blog.models import User, Post, Comment, CommentLike, PostLike, Tag




# def test_new_user():
#     """
#     GIVEN a User model
#     WHEN a new User is created
#     THEN check the email, password_hashed, authenticated, and active fields are defined correctly
#     """
#     user = User(username='Olena', email='fake24@gmail.com', password='12345qwert', image_file='default.jpg')
#     assert user.username == 'Olena'
#     assert user.email == 'fake24@gmail.com'
#     assert user.password == '12345qwert'
#     assert user.image_file == 'default.jpg'
#     # assert user.__repr__() == '<User: patkennedy79@gmail.com>'
#     assert user.is_authenticated
#     assert user.is_active
#     assert not user.is_anonymous




def test_new_user(new_user):

    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, email, password, image_file,role, authenticated, and active fields are defined correctly
    """
    assert new_user.username == 'Olena'
    assert new_user.email == 'fake24@gmail.com'
    assert new_user.password == '12345qwert'
    assert new_user.image_file == 'default.jpg'
    assert new_user.role == 'admin'
    assert new_user.is_authenticated
    assert new_user.is_active
    assert not new_user.is_anonymous


def test_new_post(new_post):
    """
       GIVEN a Post model
       WHEN a new Post is created
       THEN check the title, content, category, image_post and  user_id  are defined correctly
       """
    assert new_post.title == 'Title 1'
    assert new_post.content == 'Content 1'
    assert new_post.category == 'category 1'
    assert new_post.image_post == '1.jpg'
    assert new_post.user_id == '1'
    # assert new_post.views == '0'

def test_new_comment(new_comment):
    """
           GIVEN a Comment model
           WHEN a new Comment is created
           THEN check the username, body and  post_id  are defined correctly
           """
    assert new_comment.username == 'Olena'
    assert new_comment. body == 'body 1'
    assert new_comment.post_id == 'post1.id'


def test_new_post_like():
    """
               GIVEN a PostLike model
               WHEN a user likes post
               THEN check the user_id and  post_id  are defined correctly
               """

    post_like = PostLike(user_id='1', post_id='1')
    assert post_like.user_id =='1'
    assert post_like.post_id == '1'


def test_new_comment_like():
    """
               GIVEN a CommentLike model
               WHEN a user likes comment
               THEN check the user_id and  comment_id  are defined correctly
               """

    comment_like = CommentLike(user_id='1', comment_id='1')
    assert comment_like.user_id =='1'
    assert comment_like.comment_id == '1'


def test_new_tag():
    """
        GIVEN a Tag model
        WHEN a user creates a tag
        THEN check the name and  post_id  are defined correctly
        """

    tag = Tag(name='name 1', post_id='1')
    assert tag.name == 'name 1'
    assert tag.post_id == '1'

