from datetime import datetime

from flask import current_app
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer

from blog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    last_seen = db.Column(db.DateTime)
    user_status = db.Column(db.String(40), nullable=True, default='The best user')

    posts = db.relationship('Post', backref='author', lazy=True)

    # https://itsdangerous.palletsprojects.com/en/2.0.x/jws/
    # def get_reset_token(self, expires_sec=1800):
    #     s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    #     return s.dumps({'user_id': self.id}).decode('utf-8')

    def get_reset_token(self):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f'User({self.id}, {self.username}, {self.email}, {self.password}, {self.image_file})'


class Post(db.Model):
    __tablename__ = "posts"
    __searchable__ = ['title', 'content']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    content = db.Column(db.Text(60), nullable=False)
    image_post = db.Column(db.String(30), nullable=True)

    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Comment', backref='comment_post', lazy=True, cascade='all, delete-orphan')

    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    def __repr__(self):
        return f'Post({self.id}, {self.title}, {self.date_posted}, {self.image_post}, {self.user_id})'


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=False)
    body = db.Column(db.Text(200), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)




    def __repr__(self):
        return f'Comment({self.body}, {self.date_posted.strftime("%d.%m.%Y-%H.%M")}, {self.post_id})'


