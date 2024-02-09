import os

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, FileField, SelectField
from wtforms.validators import InputRequired
from flask import flash
# from flask_ckeditor import CKEditorField


class PostForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    content = TextAreaField('Article', validators=[InputRequired()])
    category = SelectField('Category', choices=[('Cosmetics novelty', 'Cosmetics novelty'),
                                                ('Skincare', 'Skincare'), ('Decorative cosmetics', 'Decorative cosmetics'),
                                                ( 'Hand-made', 'Hand-made'),
                                                 ('Dangerous ingredients', 'Dangerous ingredients'), ('Cosmetics procedures', 'Cosmetics procedures'),
                                                ('Recipes for youth', 'Recipes for youth')])
    tag_form = StringField('Tag')
    picture = FileField('Image (png, jpg)', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Submit')

    # def valid_image_format(self, picture):
    #     picture = picture.data
    #     _, f_ext = os.path.splitext(picture.data)
    #     if f_ext != 'png' and f_ext != 'jpg':
    #         flash('The image format must be "jpg", "png"','danger' )
    #         raise ValidationError('The image format must be "jpg", "png"', 'danger')
    #


class PostUpdateForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    content = TextAreaField('Article', validators=[InputRequired()])
    category = SelectField('Category', choices=[('Cosmetics novelty', 'Cosmetics novelty'),
                                                ('Skincare', 'Skincare'), ('Decorative cosmetics', 'Decorative cosmetics'),
                                                ( 'Hand-made', 'Hand-made'),
                                                 ('Dangerous ingredients', 'Dangerous ingredients'), ('Cosmetics procedures', 'Cosmetics procedures'),
                                                ('Recipes for youth', 'Recipes for youth')])
    picture = FileField('Image (png, jpg)', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Submit')


class AddCommentForm(FlaskForm):
    body = TextAreaField('Your comment', validators=[InputRequired()])
    submit = SubmitField('Submit')


class CommentUpdateForm(FlaskForm):
    body = TextAreaField('Comment', validators=[InputRequired()])
    submit = SubmitField('Submit')

