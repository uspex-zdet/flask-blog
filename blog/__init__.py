from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_mail import Mail
from flask_msearch import Search
# from flask_ckeditor import CKEditor

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()


login_manager = LoginManager()
login_manager.login_view = 'user.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Please login to enter the page!'

mail = Mail()
search = Search(db=db)
# ckeditor = CKEditor()




def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    mail.init_app(app)
    search.init_app(app)
    # ckeditor.init_app(app)


    from blog.main.routes import main
    from blog.user.routes import users
    from blog.post.routes import posts
    from blog.errors.handlers import errors

    app.register_blueprint(main)
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(errors)


    return app

