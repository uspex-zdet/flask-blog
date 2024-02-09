import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, 'blog',  '.env'))

UPLOAD_FOLDER = os.path.join(basedir, 'blog', 'static', 'profile_pics', 'users')
class Config(object):
    FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.urandom(36)
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', default=f"sqlite:///{os.path.join(basedir, 'instance', 'aila.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')

    REMEMBER_COOKIE_DURATION = timedelta(seconds=60)

    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True


class ProductionConfig(Config):
    FLASK_ENV = 'production'


class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URI',
                                        default=f"sqlite:///{os.path.join(basedir, 'instance', 'test.db')}")
    WTF_CSRF_ENABLED = False
    JWT_HEADER_TYPE = 'Bearer '
    JWT_BLACKLIST_ENABLED = False
