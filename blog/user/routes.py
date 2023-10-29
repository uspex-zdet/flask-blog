import os
import shutil
from flask import Blueprint, render_template, flash, url_for
from werkzeug.utils import redirect
from blog import bcrypt, db
from blog.models import User
from blog.user.forms import RegistrationForm, LoginForm

users = Blueprint('users', __name__)


@users.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        full_path = os.path.join(os.getcwd(), 'blog/static', 'profile_pics', user.username)
        if not os.path.exists(full_path):
            os.mkdir(full_path)
        shutil.copy(f'{os.getcwd()}/blog/static/profile_pics/default.jpg', full_path)
        flash('Your account was created. You can enter the blog', 'success')
        return redirect(url_for('users.login'))
    return render_template('signup.html', form=form, title='Registration', legend='Sign Up form:')


@users.route('/login', methods=['GET', 'POST'])
def login():
    return 'Hello'



