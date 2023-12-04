import os
import shutil
from datetime import datetime

import sqlalchemy
from flask import Blueprint, render_template, flash, url_for, request
from flask_login import current_user, logout_user, login_required, login_user
from werkzeug.utils import redirect

from blog import bcrypt, db
from blog.models import User, Post
from blog.user.forms import RegistrationForm, LoginForm, UpdateAccountForm, ResetPasswordForm, RequestResetForm
from blog.user.utils import save_picture, random_avatar, send_reset_email


users = Blueprint('users', __name__, template_folder='templates')


@users.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                    image_file=random_avatar(form.username.data))
        db.session.add(user)
        db.session.commit()

        # full_path = os.path.join(os.getcwd(), 'blog/static', 'profile_pics', user.username, 'profile_img')
        # if not os.path.exists(full_path):
        #     os.makedirs(full_path)
        # shutil.copy(f'{os.getcwd()}/blog/static/profile_pics/default.jpg', full_path)
        flash('Your account was created. You can enter the blog.', 'success')
        return redirect(url_for('users.login'))
    return render_template('user/signup.html', form=form, title='Registration', legend='Sign Up form:')


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'You are logged in as a user {current_user.username}', 'info')
            return redirect(next_page) if next_page else redirect(url_for('users.profile'))
        else:
            flash('Failed to login. Please check your email or password.', 'danger')
    return render_template('user/login.html', form=form, title='Login', legend='Login form:')


@users.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(username=current_user.username).first()
    posts = Post.query.all()
    users = User.query.all()
    form = UpdateAccountForm()

    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    elif form.validate_on_submit():
        path_one = os.path.join(os.getcwd(), f'blog/static/profile_pics/{user.username}')
        path_two = os.path.join(os.getcwd(), f'blog/static/profile_pics/{form.username.data}')
        os.rename(path_one, path_two)
        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.picture.data:
            current_user.image_file = save_picture(form.picture.data)
        else:
            form.picture.data = current_user.image_file

        db.session.commit()
        flash('Your profile was updated!', 'success')
        return redirect(url_for('users.profile'))
    image_file = url_for('static',
                         filename=f'profile_pics/' + current_user.username + '/profile_img/' +
                                  current_user.image_file)
    return render_template('user/profile.html', title='Profile',
                           image_file=image_file, form=form, posts=posts, users=users, user=user)


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user) \
        .order_by(Post.date_posted.desc()) \
        .paginate(page=page, per_page=3)

    return render_template('user/user_posts.html', title='Blog', posts=posts, user=user)


@users.route('/user_delete/<string:username>', methods=['GET', 'POST'])
@login_required
def delete_user(username):
    try:
        user = User.query.filter_by(username=username).first_or_404()
        if user and user.id != 1:
            db.session.delete(user)
            db.session.commit()
            full_path = os.path.join(os.getcwd(), 'blog/static', 'profile_pics', user.username)
            shutil.rmtree(full_path)

            flash(f'User {username} was deleted!', 'info')
            return redirect(url_for('users.profile'))

    except sqlalchemy.exc.IntegrityError:
        flash(f'User {username} has content!', 'warning')
        return redirect(url_for('users.profile'))
    except FileNotFoundError:
        return redirect(url_for('users.profile'))

    else:
        flash('Administration!', 'info')
        return redirect(url_for('users.profile'))

@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Password recovery instructions were sent to the specified email.', 'info')
        return redirect(url_for('users.login'))
    return render_template('user/reset_request.html', form=form, title='Password reset')


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.blog'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Incorrect or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can login to the blog', 'success')
        return redirect(url_for('users.login'))
    return render_template('user/reset_token.html', form=form, title='Password reset')



@users.route('/logout')
def logout():
    current_user.last_seen = datetime.now()
    db.session.commit()
    logout_user()
    return redirect(url_for('main.home'))




