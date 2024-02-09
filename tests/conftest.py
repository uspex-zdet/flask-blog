import os
import shutil
import pytest
from blog import create_app, db, bcrypt
from blog.models import User, Post, Comment, PostLike, CommentLike, Tag
from blog.user.utils import random_avatar
from settings import UPLOAD_FOLDER
from pathlib import Path

resources = Path(__file__).parent / "resources"
# full_path = os.path.join(os.getcwd(), 'tests/resources/33.jpeg')


@pytest.fixture(scope='module')
def new_user():
    user = User(username='Olena', email='fake24@gmail.com', password='12345qwert', image_file='default.jpg', role = 'admin')
    return user


@pytest.fixture(scope='module')
def new_post():
    post = Post(title='Title 1', content='Content 1', category='category 1', image_post='1.jpg', user_id='1')
    return post


@pytest.fixture(scope='module')
def new_comment():
    comment = Comment(username='Olena', body='body 1', post_id='post1.id')
    return comment


@pytest.fixture(scope='session')
def test_client():
    # Set the Testing configuration prior to creating the Flask application
    os.environ['CONFIG_TYPE'] = 'settings.TestingConfig'
    flask_app = create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture(scope='module')
def init_database(test_client):
    # Create the database and the database table
    db.create_all()

    # Insert user data
    default_user = User(username='Olena', email='fake24@gmail.com', password=bcrypt.generate_password_hash('12345qwert').decode('utf-8'),image_file=random_avatar('Olena'), role='admin')
    second_user = User(username='Nana', email='patrick@yahoo.com', password=bcrypt.generate_password_hash('Flask').decode('utf-8'), image_file=random_avatar('Nana'), role='user')
    third_user = User(username='Ivan', email='ivan@mail.com', password=bcrypt.generate_password_hash('Ivan777').decode('utf-8'), image_file=random_avatar('Ivan'),  role='user')
    fourth_user = User(username='Eva', email='eva21@mail.com', password=bcrypt.generate_password_hash('Eva21').decode('utf-8'), image_file=random_avatar('Eva'), role='user')
    fifth_user = User(username='Vika', email='vika@mail.com', password=bcrypt.generate_password_hash('Vika77').decode('utf-8'), image_file=random_avatar('Vika'), role='admin')
    db.session.add(default_user)
    db.session.add(second_user)
    db.session.add(third_user)
    db.session.add(fourth_user)
    db.session.add(fifth_user)

    # Commit the changes for the users
    db.session.commit()

    # Insert post data
    post1 = Post(title='Title 1', content='Content 1', category='Cosmetics novelty', image_post='1.jpg',
                 slug='title-1', user_id=default_user.id)
    post2 = Post(title='Title 2', content='Content 2', category='Skincare', image_post='2.jpg',
                 slug='title-2', user_id=default_user.id)
    post3 = Post(title='Title 3', content='Content 3', category='Hand-made', image_post='3.jpg',
                 slug='title-3', user_id=second_user.id)
    post4 = Post(title='Title 4', content='Content 4', category='Skincare', image_post='4.jpg',
                 slug='title-4', user_id=fourth_user.id)
    post5 = Post(title='Title 5', content='Content 5', category='Cosmetics novelty', image_post='5.jpg',
                 slug='title-5', user_id=fourth_user.id)
    db.session.add(post1)
    db.session.add(post2)
    db.session.add(post3)
    db.session.add(post4)
    db.session.add(post5)

    # Commit the changes for the posts
    db.session.commit()

    # Insert comment data
    comment1 = Comment(username='Olena', body='body 1', post_id=post1.id)
    comment2 = Comment(username='Nana', body='body 2', post_id=post1.id)
    comment3 = Comment(username='Ivan', body='body 3', post_id=post3.id)
    comment4 = Comment(username='Eva', body='body 4', post_id=post2.id)
    comment5 = Comment(username='Olena', body='body 5', post_id=post5.id)

    db.session.add(comment1)
    db.session.add(comment2)
    db.session.add(comment3)
    db.session.add(comment4)
    db.session.add(comment5)

    # Commit the changes for the comments
    db.session.commit()

    # Insert post like data
    post_like1 = PostLike(user_id=default_user.id, post_id=post3.id)
    post_like2 = PostLike(user_id=default_user.id, post_id=post4.id)
    post_like3 = PostLike(user_id=default_user.id, post_id=post5.id)
    post_like4 = PostLike(user_id=third_user.id, post_id=post3.id)
    post_like5 = PostLike(user_id=fourth_user.id, post_id=post1.id)
    post_like6 = PostLike(user_id=fourth_user.id, post_id=post2.id)

    db.session.add(post_like1)
    db.session.add(post_like2)
    db.session.add(post_like3)
    db.session.add(post_like4)
    db.session.add(post_like5)
    db.session.add(post_like6)

    # Commit the changes for the posts likes
    db.session.commit()

    # Insert comment like data
    comment_like1 = CommentLike(user_id=default_user.id, comment_id=comment4.id)
    comment_like2 = CommentLike(user_id=second_user.id, comment_id=comment3.id)
    comment_like3 = CommentLike(user_id=fourth_user.id, comment_id=comment1.id)
    comment_like4 = CommentLike(user_id=fourth_user.id, comment_id=comment5.id)
    comment_like5 = CommentLike(user_id=default_user.id, comment_id=comment2.id)

    db.session.add(comment_like1)
    db.session.add(comment_like2)
    db.session.add(comment_like3)
    db.session.add(comment_like4)
    db.session.add(comment_like5)

    # Commit the changes for the comments likes
    db.session.commit()

    # Insert tag data
    tag1 = Tag(name='tag 1', post_id=post1.id)
    tag2 = Tag(name='tag 2', post_id=post1.id)
    tag3 = Tag(name='tag 1', post_id=post2.id)
    tag4= Tag(name='tag 2', post_id=post4.id)
    tag5 = Tag(name='tag 3', post_id=post5.id)

    db.session.add(tag1)
    db.session.add(tag2)
    db.session.add(tag3)
    db.session.add(tag4)
    db.session.add(tag5)

    # Commit the changes for the tags
    db.session.commit()

    yield  # this is where the testing happens!
    users = User.query.all()
    # users = [second_user, fourth_user]
    for user in users:
        user_path = os.path.join(os.getcwd(), UPLOAD_FOLDER, user.username)
        full_path = user_path.replace("\\", "/")
        shutil.rmtree(full_path)

    db.drop_all()


@pytest.fixture(scope='function')
def log_in_default_user(test_client):
    test_client.post('/login',
                     data={'email':'fake24@gmail.com', 'password':'12345qwert'})

    yield  # this is where the testing happens!

    # Log out the user
    test_client.get('/logout')


@pytest.fixture(scope='function')
def log_in_second_user(test_client):
    test_client.post('login',
                     data={'email': 'patrick@yahoo.com','password': 'Flask'})

    yield   # this is where the testing happens!

    # Log out the user
    test_client.get('/logout')

@pytest.fixture(scope='function')
def log_in_fourth_user(test_client):
    test_client.post('login',
                     data={'email': 'eva21@mail.com', 'password': 'Eva21'})

    yield   # this is where the testing happens!

    # Log out the user
    test_client.get('/logout')


@pytest.fixture(scope='function')
def log_in_fifth_user(test_client):
    test_client.post('login',
                     data={'email': 'vika@mail.com', 'password': 'Vika77'})

    yield   # this is where the testing happens!

    # Log out the user
    test_client.get('/logout')

# @pytest.fixture(scope='module')
# def cli_test_client():
#     # Set the Testing configuration prior to creating the Flask application
#     os.environ['CONFIG_TYPE'] = 'config.TestingConfig'
#     flask_app = create_app()
#
#     runner = flask_app.test_cli_runner()
#
#     yield runner  # this is where the testing happens!


