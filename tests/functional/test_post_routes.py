"""
This file (test_user_routes.py) contains the functional tests for the `posts` blueprint.

These tests use GETs and POSTs to different URLs to check for the proper behavior
of the `posts` blueprint.
"""
from tests.conftest import resources
from blog.models import Post, Tag, Comment, PostLike, CommentLike
from flask import url_for
from blog.errors import handlers


def test_new_post_page(test_client, init_database, log_in_fourth_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/post/new')
    assert response.status_code == 200
    assert b'New article' in response.data
    assert b'Select category:' in response.data
    assert b'Submit' in response.data
    assert b'Login' not in response.data


def test_new_post_valid_with_image_and_one_tag(test_client, init_database, log_in_fourth_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/new' page is posted to (POST)
    THEN check the response is valid
    """
    # try to create an article with an image and one tag
    response = test_client.post('/post/new', data=dict(title='Title 6', content='Content 6', category='Cosmetics novelty',
                                                     tag_form='Test', picture=(resources/'7.png').open('rb')),
                                follow_redirects=True)

    post = Post.query.filter_by(title='Title 6').first()
    post_id = post.id
    tag = Tag.query.filter_by(post_id=post_id).first()
    image = post.image_post

    assert response.status_code == 200
    assert response.request.path == "/blog"
    assert len(response.history) == 1
    assert image.encode() in response.data
    assert b'The article was published!' in response.data
    assert b'Title 6' in response.data

    # make sure the post with the image and the tag are in the database
    assert post is not None
    assert tag is not None
    assert image is not None
    assert Post.query.count() == 6
    assert Tag.query.filter_by(post_id=post_id).count() == 1

    # make sure a slug was created and added in the database
    slug = post.slug
    assert slug is not None


def test_new_post_valid_with_image_and_with_two_tags(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testin
    WHEN the '/post/new' page is posted to (POST)
    THEN check the response is valid
    """
    # try to create an article without image and with to tags via '/'
    response = test_client.post('/post/new', data=dict(title='Title 7', content='Content 7', category='Hand-made',
                                tag_form='Test1/Test2',  picture=(resources/'11.jpg').open('rb')), follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/blog"
    assert len(response.history) == 1
    assert b'The article was published!' in response.data
    assert b'Title 7' in response.data

    # make sure the post with tags is in the database
    post = Post.query.filter_by(title='Title 7').first()
    post_id = post.id
    image = post.image_post
    tag1 = Tag.query.filter_by(name='Test1').first()
    tag2 = Tag.query.filter_by(name='Test2').first()

    assert post is not None
    assert tag1 is not None
    assert tag2 is not None
    assert image is not None
    assert image.encode() in response.data
    assert Post.query.count() == 7
    assert Tag.query.filter_by(post_id=post_id).count() == 2

    # make sure a slug was created and added in the database
    slug = post.slug
    assert slug is not None


def test_new_post_valid_without_image_and_any_tags(test_client, init_database,  log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/new' page is posted to (POST)
    THEN check the response is valid
    """
    # try to create an article without an image and tags
    response = test_client.post('/post/new', data=dict(title='Title 8', content='Content 8', category='Recipes for youth'),
                                follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/blog"
    assert len(response.history) == 1
    assert b'The article was published!' in response.data
    assert b'Title 8' in response.data
    assert b'Content 8' in response.data

    # make sure the post is in the database
    post = Post.query.filter_by(title='Title 8').first()
    post_id = post.id
    assert post is not None
    assert post.image_post is None
    assert Post.query.count() == 8
    assert Tag.query.filter_by(post_id=post_id).count() == 0

    # make sure a slug was created and added into the database
    slug = post.slug
    assert slug is not None


def test_new_post_invalid_with_invalid_image_extension_format(test_client, init_database,  log_in_fourth_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/new' page is posted to (POST)
    THEN check the response is valid
    """
    # try to create an article with invalid image extension format
    response = test_client.post('/post/new', data=dict(title='Title 9', content='Content 9',
                                category='Dangerous ingredients', picture=(resources/'33.jpeg').open('rb')),
                                follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/new"
    assert len(response.history) == 0
    assert b'Title 9' in response.data
    assert b'Content 9' in response.data
    assert b'Dangerous ingredients' in response.data
    assert b'Error: File does not have an approved extension: jpg, png' in response.data

    # make sure the post is NOT in the database
    post = Post.query.filter_by(title='Title 9').first()
    assert post is None
    assert Post.query.count() == 8


def test_new_post_invalid_with_already_taken_title(test_client, init_database, log_in_fourth_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/new' page is posted to (POST)
    THEN check the response is valid
    """
    # try to create an article with already taken article
    response = test_client.post('/post/new', data=dict(title='Title 8', content='Content 10',
                                category='Dangerous ingredients'), follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/new"
    assert len(response.history) == 0
    assert b'The title  already exists! ' in response.data

    # make sure the post is NOT in the database
    post = Post.query.filter_by(content='Content 10').first()
    assert post is None
    assert Post.query.count() == 8


def test_post_page(test_client, log_in_fourth_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/title-1' or  '/post/title-6' page is requested (GET)
    THEN check the response is valid
    """

    # when you are not the author of the article
    response = test_client.get('/post/title-1')
    assert response.status_code == 200
    assert b'Olena' in response.data
    assert b'Tag:' not in response.data
    assert b'Content 1' in response.data
    assert b'Cosmetics novelty' in response.data
    assert b'category:' in response.data
    assert b'Add your comment' in response.data
    assert b'Delete' not in response.data
    assert b'Update' not in response.data

    # when you are the author of the article
    response = test_client.get('/post/title-6')

    post = Post.query.filter_by(title='Title 6').first()
    post_id = post.id
    tag = Tag.query.filter_by(post_id=post_id).first()
    tag_name = tag.name
    image = post.image_post

    assert response.status_code == 200
    assert b'Eva' in response.data
    assert b'Tag:' in response.data
    assert tag_name.encode() in response.data
    assert image.encode() in response.data
    assert b'Content 6' in response.data
    assert b'Cosmetics novelty' in response.data
    assert b'Add your comment' in response.data
    assert b'Update' in response.data
    assert b'Delete' in response.data


def test_post_add_tags_valid(test_client, log_in_default_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/title-8' page is posted a tag to (POST)
        THEN check the response is valid
        """
    # try to add one tag to the post (user is the article's author)
    response = test_client.post('/post/title-8', data=dict(tag_form="Tag test"), follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/title-8"
    assert len(response.history) == 1
    assert b'The tag has been added to the post.' in response.data
    assert b'Tag test' in response.data

    # make sure the tag is in the database
    post = Post.query.filter_by(slug='title-8').first()
    tags = Tag.query.filter_by(tag_post=post).all()
    tag = Tag.query.filter_by(name="Tag test").first()

    assert tags is not None
    assert tag.name == "Tag test"
    assert post.views == 1
    assert len(tags) == 1

    # try to add 3 tags to the post via '/' (user is the article's author)
    response = test_client.post('/post/title-8', data=dict(tag_form="One more/second/third_one"), follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/title-8"
    assert len(response.history) == 1
    assert b'The tag has been added to the post.' in response.data
    assert b'One more' in response.data
    assert b'second' in response.data
    assert b'third_one' in response.data

    # make sure the tag is in the database
    post = Post.query.filter_by(slug='title-8').first()
    tags = Tag.query.filter_by(tag_post=post).all()
    tag1 = Tag.query.filter_by(name="One more").first()
    tag2 = Tag.query.filter_by(name="second").first()
    tag3 = Tag.query.filter_by(name="third_one").first()

    assert tag1.name == "One more"
    assert tag2.name == "second"
    assert tag3.name == "third_one"
    assert post.views == 2
    assert len(tags) == 4


def test_post_add_tag_not_author_invalid(test_client, log_in_fourth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/title-8' page is posted a tag to (POST)
        THEN check the response is valid
        """
    # try to add one tag to the post (user is NOT the article's author)
    response = test_client.post('/post/title-8', data=dict(tag_form="Tag no author"), follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/title-8"
    assert len(response.history) == 0
    assert b'Tag no author' not in response.data

    # make sure the tag is NOT in the database
    post = Post.query.filter_by(slug='title-8').first()
    tags = Tag.query.filter_by(tag_post=post).all()
    tag = Tag.query.filter_by(name="Tag no author").first()

    assert tag is None
    assert post.views == 3
    assert len(tags) == 4

def test_post_add_comment_valid(test_client, log_in_fourth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/title-7' page is posted a comment to (POST)
        THEN check the response is valid
        """
    # try to add comment to the article
    response = test_client.post('/post/title-7', data=dict(body="I added new comment"), follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/title-7"
    assert len(response.history) == 1
    assert b'The comment to the article was added' in response.data
    assert b'I added new comment' in response.data

    # make sure the comment is in the database
    post = Post.query.filter_by(slug='title-7').first()
    comments = Comment.query.filter_by(comment_post=post).all()
    comment = Comment.query.filter_by(body="I added new comment").first()

    assert comment is not None
    assert comment.body == "I added new comment"
    assert post.views == 1
    assert len(comments) == 1

def test_search_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/search' page is requested (GET)
    THEN check the response is valid
    """
    post = Post.query.filter_by(slug='title-1').first()
    comments = Comment.query.filter_by(comment_post=post).all()

    response = test_client.get('/post/search', query_string=dict(q='Title 1'))
    assert response.status_code == 200
    assert b'Olena' in response.data
    assert b'Eva' not in response.data
    assert b'Title 1' in response.data
    assert b'Content 1' in response.data
    assert b'Views 1 | 2 Comments' in response.data
    assert len(comments) == 2
    assert post.views == 1


def test_update_post_page(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/title-1/update' page is requested (GET)
    THEN check the response is valid
    """
    # if the user is the author of the article
    response = test_client.get('/post/title-1/update')
    assert response.status_code == 200
    assert b'Update the article' in response.data
    assert b'Title 1' in response.data
    assert b'Content 1' in response.data
    assert b'Cosmetics novelty' in response.data

    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/title-5/update' page is requested (GET)
        THEN check the response is valid
        """
    # if the user is NOT the author of the article
    response = test_client.get('/post/title-5/update', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/post/title-5"
    assert len(response.history) == 1
    assert b'No access to update the article!' in response.data
    assert b'Title 5' in response.data
    assert b'Content 5' in response.data

def test_update_post_without_picture_valid(test_client, log_in_fourth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/title-4/update' page is posted  to update data (POST)
        THEN check the response is valid
        """
    # try to update the title and the content only
    response = test_client.post('/post/title-4/update', data=dict(title="Title New 4", content="Content New 4", category='Skincare'),
                                follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/title-new-4"
    assert len(response.history) == 1
    assert b'The article was updated' in response.data
    assert b'Title New 4' in response.data
    assert b'Content New 4' in response.data

    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/title-new-4/update' page is posted  to update data (POST)
        THEN check the response is valid
        """

    # try to update the category only
    response = test_client.post('/post/title-new-4/update',
                                data=dict(title="Title New 4", content="Content New 4", category='Dangerous ingredients'),
                                follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/title-new-4"
    assert len(response.history) == 1
    assert b'The article was updated' in response.data
    assert b'Title New 4' in response.data
    assert b'Content New 4' in response.data
    assert b'Dangerous ingredients' in response.data
    assert b'Skincare' not in response.data

    # make sure the new data is in the database
    post = Post.query.filter_by(slug='title-new-4').first()
    assert post is not None
    assert post.title == "Title New 4"
    assert post.content == "Content New 4"
    assert post.category == "Dangerous ingredients"

def test_update_post_with_picture_invalid(test_client, log_in_fourth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/title-5/update' page is posted  to update data (POST)
        THEN check the response is valid
        """
    # try to update the picture with invalid extension format
    response = test_client.post('/post/title-5/update', data=dict(title="Title New 5", content="Content New 5", category='Skincare',
                                picture=(resources/'5.tiff').open('rb')),
                                follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/title-5/update"
    assert len(response.history) == 0
    assert b'Error: File does not have an approved extension: jpg, png' in response.data
    assert b'Title New 5' in response.data
    assert b'Content New 5' in response.data

def test_update_post_with_picture_valid(test_client, log_in_fourth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/title-5/update' page is posted  to update data (POST)
        THEN check the response is valid
        """
    # try to update the picture with valid extension format
    response = test_client.post('/post/title-5/update', data=dict(title="Title New 5", content="Content New 5", category='Skincare',
                                picture=(resources/'10.png').open('rb')),
                                follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/title-new-5"
    assert len(response.history) == 1
    assert b'The article was updated' in response.data
    assert b'Title New 5' in response.data
    assert b'Content New 5' in response.data
    assert b'Skincare' in response.data


def test_get_update_comment_page_by_not_admin(test_client, log_in_fourth_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/comment/4/update' page is requested (GET)
    THEN check the response is valid
    """
    # if the user is the author of the comment
    response = test_client.get('/post/comment/4/update', follow_redirects=True)
    assert response.status_code == 200
    assert b'Update the comment' in response.data
    assert b'body 4' in response.data


    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/comment/1/update' page is requested (GET)
        THEN check the response is valid
        """
    # if the user is NOT the author of the article
    response = test_client.get('/post/comment/1/update', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/post/title-1"
    assert len(response.history) == 2
    assert b"No access to update the comment!" in response.data
    assert b'Title 1' in response.data
    assert b'Content 1' in response.data
    assert b'body 1' in response.data


def test_get_update_comment_page_by_admin(test_client, log_in_fifth_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/comment/4/update' page is requested (GET)
    THEN check the response is valid
    """
    # if the user is an admin but NOT the author of the comment
    response = test_client.get('/post/comment/4/update', follow_redirects=True)
    assert response.status_code == 200
    assert b'Update the comment' in response.data
    assert b'body 4' in response.data


def test_get_update_comment_page_for_non_existent_comment(test_client, log_in_fifth_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/post/comment/10/update' page is requested (GET)
    THEN check the response is valid
    """
    # if the user is an admin but NOT the author of the comment
    response = test_client.get('/post/comment/10/update', follow_redirects=True)
    assert response.status_code == 404
    assert len(response.history) == 1
    assert handlers.error_404(FileNotFoundError)[0].encode() in response.data
    assert b'This page does not exist. Try going somewhere else.' in response.data

    # make sure the comment with id=10 is NOT in the database
    comment = Comment.query.filter_by(id=10).first()
    assert comment is None



def test_update_comment_by_author_valid(test_client, log_in_fourth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/comment/6/update' page is posted  to update data (POST)
        THEN check the response is valid
        """
    # try to update the comment by its author
    response = test_client.post('/post/comment/6/update', data=dict(body="body 6 updated"),
                                follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/title-7"
    assert len(response.history) == 2
    assert b'The comment was updated!' in response.data
    assert b'body 6 updated' in response.data
    assert b'Content 7' in response.data


def test_update_comment_by_admin_valid(test_client, log_in_fifth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/comment/6/update' page is posted  to update data (POST)
        THEN check the response is valid
        """
    # try to update the comment by its author
    response = test_client.post('/post/comment/6/update', data=dict(body="body 6 again updated"),
                                follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == "/post/title-7"
    assert len(response.history) == 2
    assert b'The comment was updated!' in response.data
    assert b'body 6 again updated' in response.data
    assert b'Content 7' in response.data


def test_get_category_page(test_client,  log_in_fifth_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/posts/Cosmetics%20novelty/' page is requested (GET)
    THEN check the response is valid
    """

    response = test_client.get('/posts/Cosmetics%20novelty/')
    assert response.status_code == 200
    assert b'Category articles:' in response.data
    assert b'Cosmetics novelty' in response.data
    assert b'Title 1' in response.data
    assert b'Content 1' in response.data
    assert b'Title 6' in response.data
    assert b'Content 6' in response.data


def test_get_tag_page(test_client, log_in_fifth_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/tags/Test>' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/tags/Test')
    assert response.status_code == 200
    assert b'Tag articles:' in response.data
    assert b'Test' in response.data
    assert b'Title 6' in response.data
    assert b'Eva' in response.data


def test_delete_comment_invalid(test_client, log_in_fourth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/comment/no-comment/delete' page is requested (GET)
        THEN check the response is valid
        """
    # try to delete non-existent comment
    response = test_client.get('/post/comment/25/delete')

    assert response.status_code == 404
    assert response.request.path == '/post/comment/25/delete'
    assert len(response.history) == 0
    assert handlers.error_404(FileNotFoundError)[0].encode() in response.data
    assert b'Oops... Page not found!(404)' in response.data
    assert b'This page does not exist. Try going somewhere else.' in response.data

    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/comment/1/delete' page is requested (GET)
        THEN check the response is valid
        """
    # try to delete a comment when the user is neither the author nor admin
    response = test_client.get('/post/comment/1/delete')

    assert response.status_code == 403
    assert response.request.path == '/post/comment/1/delete'
    assert len(response.history) == 0
    assert handlers.error_403(FileNotFoundError)[0].encode() in response.data
    assert b"You don't have permission to do that (403)" in response.data
    assert b'Please check your account and try again' in response.data


def test_delete_comment_by_author_valid(test_client, log_in_fourth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/comment/6/delete' page is requested (GET)
        THEN check the response is valid
        """

    response = test_client.get('/post/comment/6/delete', follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/post/title-7'
    assert len(response.history) == 1
    assert b'The comment has been deleted' in response.data
    assert b'body 6 again updated' not in response.data

    # check if the comment is deleted  from the database
    post = Post.query.filter_by(slug='title-7').first()
    comment = Comment.query.filter_by(id=6).first()

    assert post is not None
    assert comment is None


def test_delete_comment_by_admin_valid(test_client, log_in_default_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/comment/2/delete' page is requested (GET)
        THEN check the response is valid
        """

    response = test_client.get('/post/comment/2/delete', follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/post/title-1'
    assert len(response.history) == 1
    assert b'The comment has been deleted' in response.data
    assert b'body 2' not in response.data

    # check if the comment is deleted  from the database
    comment = Comment.query.filter_by(id=2).first()
    assert comment is None


def test_delete_tag_invalid(test_client, log_in_fifth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/tag/20/delete' page is requested (GET)
        THEN check the response is valid
        """
    # try to delete non-existent tag
    response = test_client.get('/post/tag/20/delete')

    assert response.status_code == 404
    assert response.request.path == '/post/tag/20/delete'
    assert len(response.history) == 0
    assert handlers.error_404(FileNotFoundError)[0].encode() in response.data
    assert b'Oops... Page not found!(404)' in response.data
    assert b'This page does not exist. Try going somewhere else.' in response.data

    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/tag/7/delete' page is requested (GET)
        THEN check the response is valid
        """
    # try to delete a tag when the user is not the author
    response = test_client.get('/post/tag/7/delete')

    assert response.status_code == 403
    assert response.request.path == '/post/tag/7/delete'
    assert len(response.history) == 0
    assert handlers.error_403(FileNotFoundError)[0].encode() in response.data
    assert b"You don't have permission to do that (403)" in response.data
    assert b'Please check your account and try again' in response.data


def test_delete_tag_valid(test_client, log_in_default_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/tag/7/delete' page is requested (GET)
        THEN check the response is valid
        """

    response = test_client.get('/post/tag/7/delete', follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/post/title-7'
    assert len(response.history) == 1
    assert b'The tag has been deleted' in response.data
    assert b'Test1' not in response.data

    # check if the tag was deleted  from the database
    post = Post.query.filter_by(slug='title-7').first()
    tag = Tag.query.filter_by(id=7).first()
    assert post is not None
    assert tag is None


def test_delete_post_invalid(test_client, log_in_fifth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/no-post/delete' page is requested (GET)
        THEN check the response is valid
        """
    # try to delete non-existent article
    response = test_client.get('/post/no-post/delete')

    assert response.status_code == 404
    assert response.request.path == '/post/no-post/delete'
    assert len(response.history) == 0
    assert handlers.error_404(FileNotFoundError)[0].encode() in response.data
    assert b'Oops... Page not found!(404)' in response.data
    assert b'This page does not exist. Try going somewhere else.' in response.data

    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/title-7/delete' page is requested (GET)
        THEN check the response is valid
        """
    # try to delete an article when the user is not the author
    response = test_client.get('/post/title-7/delete')

    assert response.status_code == 403
    assert response.request.path == '/post/title-7/delete'
    assert len(response.history) == 0
    assert handlers.error_403(FileNotFoundError)[0].encode() in response.data
    assert b"You don't have permission to do that (403)" in response.data
    assert b'Please check your account and try again' in response.data


def test_delete_post_valid(test_client, log_in_default_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the '/post/title-7/delete' page is requested (GET)
        THEN check the response is valid
        """

    response = test_client.get('/post/title-7/delete', follow_redirects=True)

    assert response.status_code == 200
    assert response.request.path == '/profile'
    assert len(response.history) == 1
    assert b'The post has been deleted' in response.data

    # check if the article is deleted with all their comments and tags from the database
    post = Post.query.filter_by(slug='title-7').first()
    comments = Comment.query.filter_by(comment_post=post).all()
    tags = Tag.query.filter_by(tag_post=post).all()
    assert post is None
    assert len(comments) == 0
    assert len(tags) == 0


def test_like_invalid_no_article(test_client, log_in_fifth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the "/like-post/12" page is posted to like the article (POST)
        THEN check the response is valid
        """
    # try to like non-existent article
    response = test_client.post("/like-post/12")

    assert response.status_code == 404
    assert response.request.path == "/like-post/12"
    assert len(response.history) == 0
    assert handlers.error_404(FileNotFoundError)[0].encode() in response.data
    assert b'Oops... Page not found!(404)' in response.data
    assert b'This page does not exist. Try going somewhere else.' in response.data


def test_like_valid(test_client, log_in_fifth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the "/like-post/1" page is posted to like the article (POST)
        THEN check the response is valid
        """
    # find the amount of the post likes
    likes_before = len(PostLike.query.filter_by(post_id=1).all())

    # to like the article
    response = test_client.post("/like-post/1")

    assert response.status_code == 200
    assert response.request.path == "/like-post/1"
    assert len(response.history) == 0


    # check if the like was added to the database
    likes_after = len(PostLike.query.filter_by(post_id=1).all())
    assert likes_after == (likes_before + 1)


def test_unlike_valid(test_client, log_in_fifth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the "/like-post/1" page is posted to unlike the article(POST)
        THEN check the response is valid
        """
    # find the amount of the post likes
    likes_before = len(PostLike.query.filter_by(post_id=1).all())

    # to unlike the article
    response = test_client.post("/like-post/1")

    assert response.status_code == 200
    assert response.request.path == "/like-post/1"
    assert len(response.history) == 0


    # check if the like was deleted from the database
    likes_after = len(PostLike.query.filter_by(post_id=1).all())
    assert likes_after == (likes_before - 1)


def test_comment_like_invalid_non_existent_comment(test_client, log_in_fifth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the "/like-comment/12" page is posted to like comment (POST)
        THEN check the response is valid
        """
    # try to like  non-existent comment
    response = test_client.post("/like-comment/12")

    assert response.status_code == 404
    assert response.request.path == "/like-comment/12"
    assert len(response.history) == 0
    assert handlers.error_404(FileNotFoundError)[0].encode() in response.data
    assert b'Oops... Page not found!(404)' in response.data
    assert b'This page does not exist. Try going somewhere else.' in response.data


def test_comment_like_valid(test_client, log_in_fifth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the "/like-comment/1" page is posted to like comment (POST)
        THEN check the response is valid
        """

    # find the amount of the comment likes
    likes_before = len(CommentLike.query.filter_by(comment_id=1).all())

    # to like the comment
    response = test_client.post("/like-comment/1")

    assert response.status_code == 200
    assert response.request.path == "/like-comment/1"
    assert len(response.history) == 0

    # check if the comment like was added to the database
    likes_after = len(CommentLike.query.filter_by(comment_id=1).all())
    assert likes_after == (likes_before + 1)


def test_comment_unlike_valid(test_client, log_in_fifth_user):
    """
        GIVEN a Flask application configured for testing
        WHEN the "/like-comment/1" page is posted to unlike comment (POST)
        THEN check the response is valid
        """
    # find the amount of the comment likes
    likes_before = len(CommentLike.query.filter_by(comment_id=1).all())

    # to unlike the comment
    response = test_client.post("/like-comment/1")

    assert response.status_code == 200
    assert response.request.path == "/like-comment/1"
    assert len(response.history) == 0


    # check if the comment like was deleted from the database
    likes_after = len(CommentLike.query.filter_by(comment_id=1).all())
    assert likes_after == (likes_before - 1)






