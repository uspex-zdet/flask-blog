"""
This file (test_main_routes.py) contains the functional tests for the `main` blueprint.

These tests use GETs and POSTs to different URLs to check for the proper behavior
of the `main` blueprint.
"""
from blog import db
from blog.models import Post


def test_index_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Aila cosmetics' articles:" in response.data
    assert b'Cosmetics novelty' in response.data
    assert b'Recipes for youth' in response.data
    assert b'Profile' not in response.data
    assert b'Login' in response.data
    assert b'SignUp' in response.data


def test_blog_page_invalid(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/blog' page is requested (GET)
    THEN check the response is valid
    """

    # try to get page when user is NOT logged
    response = test_client.get('/blog')
    assert response.status_code == 500
    assert b'Something went wrong (500)' in response.data
    assert b"We're experiencing some trouble on our end. Please try again in near future" in response.data


def test_blog_first_page(test_client, init_database, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/blog' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/blog')
    assert response.status_code == 200
    assert b"Total articles:" in response.data
    assert b'Olena' in response.data
    assert b'Eva' in response.data
    assert b'Title 1' in response.data
    assert b'Title 2' in response.data
    assert b'Content 3' in response.data
    assert b'Content 5' not in response.data
    assert b'<a class="btn btn-info mb-4" href="/blog?page=1">1</a>' in response.data
    assert b'<a class="btn btn-outline-success mb-4" href="/blog?page=2">2</a>' in response.data


def test_blog_second_page(test_client, init_database, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/blog' second page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/blog', query_string=dict(page="2"))

    assert b'Eva' in response.data
    assert response.status_code == 200
    assert b'Title 5' in response.data
    assert b'Content 5'in response.data
    assert b'<a class="btn btn-info mb-4" href="/blog?page=2">2</a>' in response.data
    assert b'<a class="btn btn-outline-success mb-4" href="/blog?page=1">1</a>' in response.data


def test_blog_no_articles_yet(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/blog' page with no article yet is requested (GET)
    THEN check the response is valid
    """

    db.session.query(Post).delete()

    response = test_client.get('/blog')
    assert Post.query.count() == 0
    assert response.status_code == 200
    assert b"Total articles:" in response.data
    assert b'No articles yet' in response.data

    db.session.rollback()

    assert Post.query.count() == 5


def test_category_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/category/Category 1/ page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/category/Cosmetics novelty/')
    assert response.status_code == 200
    assert Post.query.filter_by(category='Cosmetics novelty').count() == 2
    assert b"Category articles:" in response.data
    assert b"Cosmetics novelty" in response.data
    assert b"Title 5" in response.data
    assert b'Title 1' in response.data
    assert b'Content 5' in response.data
    assert b"Skincare" not in response.data

