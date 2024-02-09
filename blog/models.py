from datetime import datetime, timezone, timedelta
from flask import current_app
import jwt

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
    role = db.Column(db.String(20), index=True)
    last_seen = db.Column(db.DateTime)
    comments = db.relationship('Comment', backref='author', passive_deletes=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    likes = db.relationship('PostLike', backref='user', lazy=True, passive_deletes=True)
    comment_likes = db.relationship('CommentLike', backref='user', lazy=True, passive_deletes=True)

    # https://itsdangerous.palletsprojects.com/en/2.0.x/jws/
    # def get_reset_token(self, expires_sec=1800):
    #     s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    #     return s.dumps({'user_id': self.id}).decode('utf-8')

    # def like_post(self, post):
    #     if not self.has_liked_post(post):
    #         like = PostLike(user_id=self.id, post_id=post.id)
    #         db.session.add(like)

    # def unlike_post(self, post):
    #     if self.has_liked_post(post):
    #         PostLike.query.filter_by(
    #             user_id=self.id,
    #             post_id=post.id).delete()
    #
    # def has_liked_post(self, post):
    #     return PostLike.query.filter(
    #         PostLike.user_id == self.id,
    #         PostLike.post_id == post.id).count() > 0

    # def get_reset_token(self, expires_sec=600):
    #     s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
    #     return s.dumps({'user_id': self.id}).decode('utf-8')
    #
    # @staticmethod
    # def verify_reset_token(token):
    #     s = Serializer(current_app.config['SECRET_KEY'])
    #     try:
    #         user_id = s.loads(token)['user_id']
    #     except:
    #         return None
    #     # return User.query.get(user_id)
    #     return db.session.get(User, user_id)

    def get_reset_token(self):
        s = jwt.encode(payload={'user_id': self.id, "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=300)},
                       key= current_app.config['SECRET_KEY'])
        return s

    @staticmethod
    def verify_reset_token(token):

        try:
            encode =jwt.decode(jwt=token, key=current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id =int(encode['user_id'])
        except:
            return None
        return db.session.get(User, user_id)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'User({self.id}, {self.username}, {self.email}, {self.password}, {self.image_file})'

    # def __repr__(self):
    #     return f'User({self.id}, {self.username}, {self.email}, {self.password}, {self.image_file})'


class Post(db.Model):
    __tablename__ = "posts"
    __searchable__ = ['title', 'content']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    content = db.Column(db.Text(60), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    image_post = db.Column(db.String(30), nullable=True)

    views = db.Column(db.Integer, default=0)
    likes = db.relationship('PostLike', backref='post', lazy=True, passive_deletes=True)

    slug = db.Column(db.String(), unique=True, index=True)
    tags = db.relationship('Tag', backref='tag_post', lazy=True, cascade="all, delete-orphan")
    comments = db.relationship('Comment', backref='comment_post', lazy=True, cascade='all, delete-orphan')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'Post({self.id}, {self.title}, {self.date_posted}, {self.image_post}, {self.user_id})'


class PostLike(db.Model):
    __tablename__ = "post_likes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.id', ondelete="CASCADE"), nullable=False)

class CommentLike(db.Model):
    __tablename__ = "comment_likes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete="CASCADE"), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey(
        'comments.id', ondelete="CASCADE"), nullable=False)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    body = db.Column(db.Text(200), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    # author = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    likes = db.relationship('CommentLike', backref='comment', lazy=True, passive_deletes=True)
    def __repr__(self):
        return f'Comment({self.body}, {self.date_posted.strftime("%d.%m.%Y-%H.%M")}, {self.post_id})'


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f'Tag({self.id}, {self.name}, {self.post_id})'