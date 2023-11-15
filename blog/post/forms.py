from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Article', validators=[DataRequired()])
    picture = FileField('Image (png, jpg)', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')


class PostUpdateForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Article', validators=[DataRequired()])
    picture = FileField('Image (png, jpg)', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')
