"""
This file (test_user_routes.py) contains the functional tests for the `users` blueprint.

These tests use GETs and POSTs to different URLs to check for the proper behavior
of the `users` blueprint.
"""

import os
from blog.models import User, Post
from tests.conftest import resources
from blog import db
from blog.errors import handlers


def test_login_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b'Login form:' in response.data
    assert b'Forgot your password?' in response.data
    assert b'Sign Up' in response.data
    assert b'Remember me' in response.data
    assert b'Login' in response.data
    assert b'Sign Up form:' not in response.data


def test_login_valid(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    response = test_client.post('/login',
                                data=dict(email='fake24@gmail.com', password='12345qwert'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/profile"
    assert len(response.history) == 1
    assert b'You are logged in as a user Olena' in response.data
    assert b'Logout' in response.data
    assert b'Admin' in response.data   #user has admin role
    assert b'Login' not in response.data
    assert b'SignUp' not in response.data

    test_client.get('/logout')


def test_logout(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/"
    assert len(response.history) == 1
    assert b'You have left your account!' in response.data
    assert b'Profile' not in response.data
    assert b'Logout' not in response.data
    assert b'Login' in response.data
    assert b'SignUp' in response.data


def test_login_invalid(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to with invalid credentials (POST)
    THEN check an error message is returned to the user
    """
    response = test_client.post('/login',
                                data=dict(email='fake24@gmail.com', password='NOT12345qwert')) #wrong password
    assert response.status_code == 200
    assert response.request.path == "/login"
    assert b'Failed to login. Please check your email or password.' in response.data
    assert b'Forgot your password?' in response.data
    assert b'Logout' not in response.data
    assert b'Login form:' in response.data


def test_login_already_logged_in(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST) when the user is already logged in
    THEN check an error message is returned to the user
    """
    response = test_client.post('/login',
                                data=dict(email='fake24@gmail.com', password='12345qwert'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Already logged in!  Redirecting to blog' in response.data
    assert response.request.path == "/blog"
    assert len(response.history) == 1
    assert b'Logout' in response.data
    assert b'Login' not in response.data
    assert b'SignUp' not in response.data


def test_signup_invalid(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/signup' page is posted to with invalid credentials (POST)
    THEN check an error message is returned to the user
    """
    # Try registering with a confirm_password that doesn't match password
    response = test_client.post('/signup',
                                data=dict(username='Paul21', email='patkennedy79@hotmail.com',
                                          password='Flask555',
                                          confirm_password='Flask5555'))   # Does NOT match!

    assert response.status_code == 200
    assert b'Thank you for registering! Please login' not in response.data
    assert b'Error in the field "Confirm password" : Field must be equal to password.' not in response.data
    assert b'Sign Up form:' in response.data
    assert b'Logout' not in response.data
    assert b'Login' in response.data
    assert b'Already have an account?' in response.data


def test_signup_duplicated(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/signup' page is posted to (POST) using a username or an email address already registered
    THEN check an error message is returned to the user
    """

    # Try registering with an email address that is already taken
    response = test_client.post('/signup',
                                data=dict(username='Paul', email='patrick@yahoo.com',
                                          password='Flask',
                                          confirm_password='Flask'))
    assert response.status_code == 200
    assert b'This email is already taken. Please choose different one' in response.data
    assert b'Error in the field ' in response.data
    assert b'Thank you for registering! Please login' not in response.data
    assert b'Sign Up form:' in response.data

    # Try registering with a username that is already taken
    response = test_client.post('/signup',
                                data=dict(username='Ivan', email='ivan21@yahoo.com',
                                          password='Flask',
                                          confirm='Flask'))
    assert response.status_code == 200
    assert b'This username is already taken. Please choose different one' in response.data
    assert b'Error in the field ' in response.data
    assert b'Thank you for registering! Please login' not in response.data
    assert b'Sign Up form:' in response.data


def test_signup_user_is_already_logged(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/signup' page is posted to with invalid credentials (POST)
    THEN check an error message is returned to the user
    """
    # Try registering with a user that is already logged
    response = test_client.post('/signup',
                                data=dict(username='Olena', email='fake24@gmail.com',
                                          password='12345qwert',
                                          confirm_password='12345qwert'), follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/blog'
    assert len(response.history) == 1
    assert User.query.count() == 5


def test_signup_valid(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/signup' page is posted to (POST)
    THEN check the response is valid
    """
    response = test_client.post('/signup',
                                data=dict(username='Novelty', email='new123@gmail.com',
                                          password='Novelty12345',
                                          confirm_password='Novelty12345', role='user'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    assert len(response.history) == 1
    assert b'Thank you for registering! Please login' in response.data
    assert b'Logout' not in response.data
    assert b'Login form:' in response.data

    # make sure the user New is in the database
    user = User.query.filter_by(username='Novelty').first()
    assert user is not None
    assert user.email == 'new123@gmail.com'
    assert User.query.count() == 6


def test_user_delete_invalid(test_client, log_in_default_user ):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/user_delete/Olena' page  is requested (GET) and user has content
    THEN check the response is valid
    """
    # Try to delete user that has content (articles)
    response = test_client.get('/user_delete/Nana', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/profile"
    assert len(response.history) == 1
    assert b'User Nana has content!' in response.data

    # make sure the user Nana is still in the database
    user = User.query.filter_by(username='Nana').first()
    assert user is not None
    assert User.query.count() == 6

    """
    GIVEN a Flask application configured for testing
    WHEN the '/user_delete/Nana' page  is requested (GET) when the user is admin
    THEN check the response is valid
    """

    # Try to delete user with admin role
    response = test_client.get('/user_delete/Olena', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/profile"
    assert len(response.history) == 1
    assert b'Admin cannot be deleted!' in response.data

    # make sure the user Olena is still in the database
    user = User.query.filter_by(username='Olena').first()
    assert user is not None
    assert User.query.count() == 6

    """
    GIVEN a Flask application configured for testing
    WHEN the '/user_delete/NoUser' page  is requested (GET) when the user does not exist
    THEN check the response is valid
    """

    # Try to delete non-existent user
    response = test_client.get('/user_delete/NoUser', follow_redirects=True)
    assert response.status_code == 404
    assert handlers.error_404(FileNotFoundError)[0].encode() in response.data
    assert b'This page does not exist. Try going somewhere else.' in response.data

    # make sure the user NoUser is NOT in the database
    user = User.query.filter_by(username='NoUser').first()
    assert user is None
    assert User.query.count() == 6


def test_user_delete_valid(test_client, log_in_default_user ):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/user_delete/Paul' page  is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/user_delete/Ivan', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/profile"
    assert len(response.history) == 1
    assert b'User Ivan was deleted!' in response.data
    assert b'Registered users:' in response.data

    # make sure user Ivan is NOT in the database anymore
    user = User.query.filter_by(username='Ivan').first()
    assert user is None
    assert User.query.count() == 5


def test_profile_page(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/profile' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/profile')
    assert response.status_code == 200
    assert b'Olena' in response.data
    assert b'Nana' in response.data
    assert b'Novelty' in response.data
    assert b'fake24@gmail.com' in response.data
    assert b'new123@gmail.com' not in response.data
    assert b'patrick@yahoo.com' not in response.data
    assert b'Title 1' in response.data
    assert b'Title 2' in response.data
    assert b'Title 3'not in response.data
    assert b'Profile update' in response.data
    assert b'Registered users' in response.data
    assert b'List of articles:' in response.data
    assert b'Logout' in response.data
    assert b'Login' not in response.data
    assert b'SignUp' not in response.data


def test_update_user_profile_valid_without_updating_picture(test_client, log_in_second_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/profile' page  is requested (GET)
    THEN check the update profile form shows correct data and the response is valid
    """

    response = test_client.get('/profile')
    assert response.status_code == 200
    assert b'Nana' in response.data
    assert b'patrick@yahoo.com' in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/profile' page is posted to (POST) to update user profile 
    THEN check the response is valid
    """
    # find Nana picture for further checking its name in response data
    nana = User.query.filter_by(email='patrick@yahoo.com').first()
    img_nana = nana.image_file
    print(img_nana)  # print the old picture name

    # try to update user profile data without updating picture(avatar)
    response = test_client.post('/profile',
                                data=dict(username='Mike', email='mike82@yahoo.com'),
                                follow_redirects=True)

    print(nana.image_file) # print a new picture name
    assert response.status_code == 200
    assert nana.image_file.encode() in response.data
    assert img_nana == nana.image_file   # check that image_file name of user's still the same
    assert b'Your profile was updated!' in response.data
    assert User.query.count() == 5

    # make sure the username Nana is NOT in the database anymore (username was changed)
    user_nana = User.query.filter_by(username='Nana').first()
    assert user_nana is None

    # make sure the username Mike is now in the database (was changed from Nana)
    # and his email was changed from patrick@yahoo.com to mike82@yahoo.com
    user_mike = User.query.filter_by(username='Mike').first()
    assert user_mike is not None
    assert user_mike.email == 'mike82@yahoo.com'


def test_update_user_profile_picture_when_previous_picture_was_deleted_valid(test_client, log_in_fifth_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/profile' page is posted to (POST) to update user profile image
    THEN check the response is valid
    """

    # remove previous image and folder
    vika = User.query.filter_by(email='vika@mail.com').first()
    os.remove(os.path.join(os.getcwd(), 'blog/static', 'profile_pics', 'users', vika.username, 'profile_img', vika.image_file))
    os.rmdir(os.path.join(os.getcwd(), 'blog/static', 'profile_pics', 'users', vika.username, 'profile_img'))

    # try to update user picture
    response = test_client.post('/profile',
                                data=dict(username='Vika', email='vika@mail.com',
                                          picture=(resources/'43.jpg').open('rb')),
                                follow_redirects=True)

    print(vika.image_file)  # a new picture name will be printed
    assert response.status_code == 200
    assert len(response.history) == 1
    assert vika.image_file is not None
    assert b'Your profile was updated!' in response.data
    assert vika.image_file.encode() in response.data  # the new is displayed in response data


def test_update_user_profile_old_picture_to_new_picture_valid(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/profile' page is posted to (POST) to update user profile
    THEN check the response is valid
    """
    # find Olena picture for further checking its name in response data
    olena = User.query.filter_by(email='fake24@gmail.com').first()
    img_olena = olena.image_file
    print(img_olena)  # the old picture name will be printed
    # try to update user picture(avatar) only

    response = test_client.post('/profile',
                                data=dict(username='Olena', email='fake24@gmail.com',
                                          picture=(resources/'2.png').open('rb')),
                                follow_redirects=True)

    print(olena.image_file)  # a new picture name will be printed
    assert response.status_code == 200
    assert len(response.history) == 1
    assert b'Your profile was updated!' in response.data
    assert img_olena != olena.image_file
    assert olena.image_file.encode() in response.data  # the new is displayed in response data
    assert User.query.count() == 5




def test_update_user_profile_invalid_with_already_taken_username(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/profile' page is posted to (POST) to update user profile
    THEN check the response is valid
    """

    # try to update profile with already taken username
    response = test_client.post('/profile',
                                data=dict(username='Mike', email='fake24@gmail.com'))

    assert response.status_code == 200
    assert b'This username is already taken. Please choose different one' in response.data

def test_update_user_profile_invalid_with_already_taken_email(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/profile' page is posted to (POST) to update user profile
    THEN check the response is valid
    """

    # try to update profile with already taken email
    response = test_client.post('/profile',
                                data=dict(username='Olena', email='mike82@yahoo.com'))

    assert response.status_code == 200
    assert b'This username is already taken. Please choose different one' in response.data


def test_user_posts_page(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/user/Mike' page is requested (GET)
    THEN check the response is valid
    """
    mike = User.query.filter_by(email='mike82@yahoo.com').first()
    img_mike = mike.image_file

    response = test_client.get('/user/Mike')
    assert response.status_code == 200
    assert b'Mike' in response.data
    assert b'Title 3' in response.data
    assert img_mike.encode() in response.data
    assert b'Back' in response.data


def test_user_posts_second_page(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/user/Mike' second page is requested (GET)
    THEN check the response is valid
    """
    mike = User.query.filter_by(username="Mike").first()
    mike_id = mike.id

    post_mike2 = Post(title='post mike 2', content='content mike 2', category='Category 4', image_post='mike2.jpg',
                      slug='post mike 2', user_id=mike_id)
    post_mike3 = Post(title='post mike 3', content='content mike 3', category='Category 4', image_post='mike3.jpg',
                      slug='post mike 3', user_id=mike_id)
    post_mike4 = Post(title='post mike 4', content='content mike 4', category='Category 4', image_post='mike4.jpg',
                      slug='post mike 4', user_id=mike_id)
    db.session.add(post_mike2)
    db.session.add(post_mike3)
    db.session.add(post_mike4)

    response = test_client.get('/user/Mike', query_string=dict(page='2'))

    assert response.status_code == 200
    assert Post.query.filter_by(user_id=2).count() == 4
    assert b'Mike' in response.data
    assert b'Title 3' in response.data
    assert b'Back' in response.data

    db.session.rollback()
    db.session.rollback()
    db.session.rollback()

    assert Post.query.filter_by(user_id=2).count() == 1


def test_reset_request_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/reset_password' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/reset_password')

    assert response.status_code == 200
    assert response.request.path == '/reset_password'
    assert len(response.history) == 0
    assert b'Reset password' in response.data


def test_reset_request_valid(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/reset_password' page is posted to (POST) a registered email
    THEN check the response is valid
    """
    # Try to  send reset request to an existing  user in database
    response = test_client.post('/reset_password',
                                data=dict(email='fake24@gmail.com'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/login'
    assert len(response.history) == 1
    assert b'Password recovery instructions were sent to the specified email.' in response.data
    assert b'Login form:' in response.data


def test_reset_request_invalid(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/reset_password' page is posted to (POST) with unknown email
    THEN check the response is valid
    """
    # Try to do reset request with an email that is NOT in the database
    response = test_client.post('/reset_password',
                                data=dict(email='unknown33@gmail.com'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/reset_password'
    assert len(response.history) == 0
    assert b'There is no account with that email. You must register first' in response.data
    assert b'Reset password' in response.data


def test_reset_password_valid(test_client):
    """
    GIVEN a Flask application configured for testing and created token
    WHEN the '/reset_password/<token>' page is requested (GET)
    THEN check the response is valid
    """
    user = User.query.filter_by(email='fake24@gmail.com').first()
    token = User.get_reset_token(user)

    response = test_client.get(f'/reset_password/{token}')

    assert token is not None
    assert response.status_code == 200

    assert response.request.path == f'/reset_password/{token}'
    assert b'Reset password' in response.data
    """
   GIVEN a Flask application configured for testing and created token
   WHEN the '/reset_password/<token>' page is posted to (POST)
   THEN check the response is valid
   """
    response = test_client.post(f'/reset_password/{token}', data=dict(password='Test9876', confirm_password='Test9876'),
                                follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/login'
    assert len(response.history) == 1
    assert b'Your password has been updated! You can login to the blog' in response.data


def test_reset_password_invalid(test_client):
    """
    GIVEN a Flask application configured for testing and created token in URL
    WHEN the '/reset_password/<token>' page is posted to (POST)
    THEN check the response is valid
    """
    user = User.query.filter_by(email='fake24@gmail.com').first()
    token = User.get_reset_token(user)

    # Try to reset password with incorrect confirm_password
    response = test_client.post(f'/reset_password/{token}', data=dict(password='Test222',
                                                                      confirm_password='Test223'))

    assert response.status_code == 200
    assert response.request.path == f'/reset_password/{token}'
    assert b'Error in the field ' in response.data
    assert b'Field must be equal to password.' in response.data
    assert b'Reset password' in response.data

    """
    GIVEN a Flask application configured for testing and with expired token
    WHEN the '/reset_password/<token>' page is requested (GET) with invalid user
    THEN check the response is valid
    """
    # Try to reset password with expired token
    token = None
    response = test_client.get(f'/reset_password/{token}', follow_redirects=True)

    assert token is None
    assert response.status_code == 200
    assert response.request.path == '/reset_password'
    assert len(response.history) == 1
    assert b'Incorrect or expired token' in response.data
    assert b'Reset password' in response.data









