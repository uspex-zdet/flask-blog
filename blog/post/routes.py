from flask import (Blueprint, render_template, redirect, url_for, flash, abort, request)
from flask_login import current_user, login_required
from blog import db
from blog.models import Post, Comment
from blog.post.forms import PostForm, PostUpdateForm, CommentUpdateForm
from blog.user.forms import AddCommentForm
from blog.user.utils import save_picture_post

posts = Blueprint('post', __name__, template_folder='templates')


@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, image_post=form.picture.data, author=current_user)
        if form.picture.data:
            picture_file = save_picture_post(form.picture.data)
            post.image_post = picture_file
        else:
            post.image_post = None

        db.session.add(post)
        db.session.commit()

        flash('The article was published!', 'success')
        return redirect(url_for('main.blog'))

    if form.picture.data:
        image_file = url_for('static',
                            filename=f'profile_pics/' + current_user.username + '/post_images/' + current_user.image_file)
        return render_template('post/create_post.html', title='New article',
                            form=form, legend='New article', image_file=image_file)

    else:
        return render_template('post/create_post.html', title='New article',
                               form=form, legend='New article')


@posts.route('/post/<int:post_id>', methods=['GET','POST'])
@login_required
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comment = Comment.query.filter_by(post_id=post.id).order_by(db.desc(Comment.date_posted)).all()
    post.views += 1
    db.session.commit()
    form = AddCommentForm()
    if request.method == "POST":
        if form.validate_on_submit():
            username = current_user.username
            comment = Comment(username=username, body=form.body.data, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
            flash("The comment to the article was added", "success")
            return redirect(url_for('post.post', post_id=post.id))
    if post.image_post:
        image_file = url_for('static',
                         filename=f'profile_pics/' + post.author.username + '/post_images/' + post.image_post)
        return render_template('post/post.html', title=post.title, post=post, image_file=image_file,
                               post_id=post_id, form=form, comment=comment)

    else:
        return render_template('post/post.html', title=post.title, post=post, post_id=post_id, form=form, comment=comment)


@posts.route('/search')
def search():
        keyword = request.args.get('q')
        search_posts = Post.query.msearch(keyword, fields=['title', 'content'], limit=6)
        return render_template('post/search.html', search_posts=search_posts, title='Search')



@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)
    form = PostUpdateForm()
    if request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        if form.picture.data:
            post.image_post = save_picture_post(form.picture.data)
        db.session.commit()
        flash('The article was updated', 'success')

        return redirect(url_for('post.post', post_id=post.id))

    image_file = url_for('static',
                         filename=f'profile_pics/{current_user.username}/post_images/{post.image_post}')

    return render_template('post/update_post.html', title='Update the article',
                           form=form, legend='Update the article', image_file=image_file, post=post)


@posts.route('/comment/<int:comment_id>/update', methods=['GET', 'POST'])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    form = CommentUpdateForm()

    if request.method == 'GET':
        form.body.data = comment.body

    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.commit()
        return redirect(url_for('post.post', post_id=comment.post_id))
    return render_template('post/update_comment.html', form=form)




@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('The article was deleted', 'success')
    return redirect(url_for('users.profile'))


@posts.route('/comment/<int:comment_id>/delete')
@login_required
def delete_comment(comment_id):
    single_comment = Comment.query.get_or_404(comment_id)
    db.session.delete(single_comment)
    db.session.commit()
    flash('The comment was deleted', 'success')
    return redirect(url_for('post.post', post_id=single_comment.post_id))
