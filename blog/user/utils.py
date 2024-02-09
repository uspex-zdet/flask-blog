import os
import secrets
import random
import shutil

from PIL import Image
from flask import current_app, url_for
from flask_login import current_user
from flask_mail import Message

from blog import mail


def save_picture(form_picture):
    random_hex = secrets.token_hex(16)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    full_path = os.path.join(current_app.root_path, 'static', 'profile_pics/', 'users',  current_user.username, 'profile_img')
    try:
        os.remove(
            os.path.join(current_app.root_path,
                         f"static/profile_pics/users/{current_user.username}/profile_img/{current_user.image_file}"))
    except:
        print('The image was not found, it may have been deleted!')
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    picture_path = os.path.join(full_path, picture_fn)
    output_size = (360, 360)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


# def save_picture_post(form_picture):
#     random_hex = secrets.token_hex(16)
#     _, f_ext = os.path.splitext(form_picture.filename)
#     picture_fn = random_hex + f_ext
#     full_path = os.path.join(current_app.root_path, 'static', 'profile_pics/', current_user.username, 'post_images')
#     if not os.path.exists(full_path):
#         os.mkdir(full_path)
#     picture_path = os.path.join(full_path, picture_fn)
#     output_size = (500, 500)
#     i = Image.open(form_picture)
#     i.thumbnail(output_size)
#     i.save(picture_path)
#     return picture_fn


def random_avatar(user):
    full_path = os.path.join(os.getcwd(), 'blog/static', 'profile_pics', 'users',  user, 'profile_img')
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    full_path_avatar = os.path.join(os.getcwd(), 'blog/static/Avatars/')
    list_avatars = os.listdir(full_path_avatar)
    lst = random.choice(list_avatars)
    random_image_file = os.path.join(full_path_avatar, lst)
    # print('random_image_file', random_image_file)
    shutil.copy(random_image_file, full_path)
    # print('full_path', full_path)
    return lst


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password change request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f"""
    To reset your password, follow this link:
    {url_for('users.reset_token', token=token, _external=True)}

    If you have not made this request, simply ignore this letter!
    No changes will be made!

   There is no need to reply to this letter as it is generated automatically.
    """
    mail.send(msg)
