from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from blog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            flash('This username is already taken. Please choose different one', 'danger')
            raise ValidationError('This username is already taken. Please choose different one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            flash('This email is already taken. Please choose different one', 'danger')
            raise ValidationError('This email is already taken. Please choose different one')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Enter')
