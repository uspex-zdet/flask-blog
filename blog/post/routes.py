import os
import PIL
import sqlalchemy
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app, jsonify
from flask_login import current_user, login_required
from slugify import slugify

from blog import db
from blog.models import Post, Comment, Tag, PostLike, CommentLike
from blog.post.forms import PostForm, PostUpdateForm, CommentUpdateForm, AddCommentForm
from blog.post.utils import save_picture_post_author


posts = Blueprint('posts', __name__, template_folder='templates')


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    try:
        if form.validate_on_submit():
            post = Post(title=form.title.data, content=form.content.data, category=form.category.data,
                        image_post=form.picture.data, author=current_user)
            if form.picture.data:
                picture_file = save_picture_post_author(form.picture.data, post)
                post.image_post = picture_file
            else:
                post.image_post = None
            # post.image_post = save_picture_post_author(form.picture.data, post)

            db.session.add(post)
            post.slug = slugify(post.title)
            db.session.flush()

            name = form.tag_form.data
            if name:
                name = name.split('/')
                for i in name:
                    tag_post = Tag(name=i)  # creating a tag
                    tag_post.post_id = post.id
                    db.session.add(tag_post)
            db.session.commit()
            flash('The article was published!', 'success')
            return redirect(url_for('main.blog'))
        else:
            if request.method == 'POST':
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f'Error: {error}')


        # except PIL.UnidentifiedImageError:
        #     flash('Выберите изображение для статьи', 'danger')
    except sqlalchemy.exc.IntegrityError:
        flash('The title  already exists! ', 'danger')

        db.session.rollback()

    if form.picture.data:
        image_file = url_for('static',
                             filename=f'profile_pics/' + 'users/' + current_user.username + '/post_images/'
                                      + current_user.image_file)
        return render_template('post/create_post.html', title='New article',
                        form_new_post=form, legend='New article', image_file=image_file)

    else:
        return render_template('post/create_post.html', title='New article',
                           form_new_post=form, legend='New article')


@posts.route('/post/<string:slug>', methods=['GET', 'POST'])
@login_required
def post(slug):
    post = Post.query.filter_by(slug=slug).first()
    comment = Comment.query.filter_by(post_id=post.id).order_by(db.desc(Comment.date_posted)).all()

    form_post = PostForm()
    form_comment = AddCommentForm()

    if request.method == 'POST' and post.author == current_user:
        # def add_tag():
        name = form_post.tag_form.data
        if name:
            name = name.split('/')
            for i in name:
                tag_post = Tag(name=i)  # создаю тег
                tag_post.post_id = post.id
                db.session.add(tag_post)
            db.session.commit()
            flash('The tag has been added to the post.', "success")
            return redirect(url_for('posts.post', slug=post.slug))

        # add_tag()
    form_post.tag_form.data = ''

    if request.method == 'POST' and form_comment.validate_on_submit():
        username = current_user.username
        comment = Comment(username=username, body=form_comment.body.data, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash("The comment to the article was added", "success")
        return redirect(url_for('posts.post', slug=post.slug))

    post.views += 1
    db.session.commit()

    if post.image_post:
        image_file = url_for('static',
                         filename=f'profile_pics/'+'users/' + post.author.username + '/post_images/' + post.image_post)
        return render_template('post/post.html', title=post.title, post=post, image_file=image_file,
                               form_add_comment=form_comment, comment=comment, form_add_tag=form_post)

    else:
        return render_template('post/post.html', title=post.title, post=post,  form_add_comment=form_comment, comment=comment, form_add_tag=form_post)


@posts.route('/post/search')
# @login_required
def search():
    # try:
    keyword = request.args.get('q')
    search_posts = Post.query.msearch(keyword, fields=['title', 'content'], limit=20)
    return render_template('post/search.html', search_posts=search_posts, title='Search')
    # except AttributeError:
    #     return redirect(url_for('users.account'))


@posts.route('/post/<string:slug>/update', methods=['GET', 'POST'])
@login_required
def update_post(slug):
    post = Post.query.filter_by(slug=slug).first()

    if post.author != current_user:
        flash('No access to update the article!', 'danger')
        return redirect(url_for('posts.post', slug=post.slug))
    form = PostUpdateForm()
    if request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.category.data = post.category

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.category = form.category.data


        post.slug = slugify(post.title)
        db.session.flush()

        db.session.commit()

        if form.picture.data:
            post.image_post = save_picture_post_author(form.picture.data, post)
        db.session.commit()
        flash('The article was updated', 'success')

        return redirect(url_for('posts.post', slug=post.slug))
    else:
        if request.method == 'POST':
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'Error: {error}')
            # flash('The image format must be "jpg", "png"', 'success')
    image_file = url_for('static',
                         filename=f'profile_pics/user/{current_user.username}/post_images/{post.image_post}')

    return render_template('post/update_post.html', title='Update the article',
                           form_post_update=form, legend='Update the article', image_file=image_file, post=post)


@posts.route('/post/comment/<int:comment_id>/update/', methods=['GET', 'POST'])
@login_required
def update_comment(comment_id):

    comment = Comment.query.filter_by(id=comment_id).first_or_404()
    form = CommentUpdateForm()
    if current_user.is_admin or comment.username == current_user.username:

        if request.method == 'GET':
            form.body.data = comment.body

        if request.method == 'POST' and form.validate_on_submit():
            comment.body = form.body.data
            db.session.commit()
            flash('The comment was updated!', 'success')
            return redirect(url_for('posts.post', slug=comment.comment_post.slug))
    else:
        flash('No access to update the comment!', 'danger')
        return redirect(url_for('posts.post', slug=comment.comment_post.slug))
    return render_template('post/update_comment.html', form_comment_update=form, title="Comment update")


@posts.route('/posts/<string:category_str>/', methods=['GET'])
# @login_required
def category(category_str):
    current_category = Post.query.filter_by(category=category_str).first()
    posts_category = Post.query.filter_by(category=category_str).all()
    return render_template('post/all_posts_category.html', post_category=posts_category,
                           current_category=current_category, title='Category ' + category_str)


@posts.route('/tags/<string:tag_str>', methods=['GET'])
# @login_required
def tag(tag_str):
    current_tag = Tag.query.filter_by(name=tag_str).first_or_404()
    name_tags = Tag.query.filter(Tag.name == current_tag.name).all()
    return render_template('post/all_post_tag.html', name_tags=name_tags,
                           current_tag=current_tag, title='Tag articles ' + current_tag.name)


@posts.route('/post/<string:slug>/delete', methods=['POST', 'GET'])
@login_required
def delete_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    if post.author != current_user:
        abort(403)
    if post.image_post:
        os.unlink(
            os.path.join(current_app.root_path,
                         f'static/profile_pics/users/{current_user.username}/post_images/{post.image_post}'))

    db.session.delete(post)
    db.session.commit()
    flash('The post has been deleted', 'success')
    return redirect(url_for('users.profile'))


@posts.route('/post/comment/<int:comment_id>/delete')
@login_required
def delete_comment(comment_id):
    single_comment = Comment.query.filter_by(id=comment_id).first_or_404()
    return_to_post = single_comment.comment_post.slug
    # print('COMMENT DELETE', single_comment)

    if current_user.is_admin or single_comment.username == current_user.username:
        db.session.delete(single_comment)
        db.session.commit()
        flash('The comment has been deleted', 'success')
    else:
        abort(403)
    return redirect(url_for('posts.post', slug=return_to_post))


@posts.route('/post/tag/<int:tag_id>/delete')
@login_required
def delete_tag(tag_id):
    tag = Tag.query.filter_by(id=tag_id).first_or_404()
    if tag.tag_post.author != current_user:
        abort(403)
    db.session.delete(tag)
    db.session.commit()
    flash('The tag has been deleted', 'success')
    return redirect(url_for('posts.post', slug=tag.tag_post.slug))


@posts.route("/like-post/<int:post_id>", methods=['POST', 'GET'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404()
    like = PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.user_id, post.likes)})


@posts.route("/like-comment/<int:comment_id>", methods=['POST'])
@login_required
def comment_like(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first_or_404()
    like = CommentLike.query.filter_by(user_id=current_user.id, comment_id=comment_id).first()

    if like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = CommentLike(user_id=current_user.id, comment_id=comment_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(comment.likes), "liked": current_user.id in map(lambda x: x.user_id, comment.likes)})