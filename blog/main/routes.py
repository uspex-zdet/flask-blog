from flask import Blueprint, render_template, request, url_for

from flask_login import login_required, current_user

from blog.models import Post, User

main = Blueprint('main', __name__, template_folder='templates')


@main.route('/')
def home():
    return render_template("main/index.html", title="Main")


@main.route('/blog', methods=['POST', 'GET'])
@login_required
def blog():
    # all_posts = Post.query.all()
    all_users = User.query.all()
    # post = Post.query.get(current_user.id)
    # if post is None:
    posts = Post.query.order_by(Post.date_posted.desc())
    # post = Post.query.first()
    # post = Post.query.filter_by(user_id=current_user.id).first()
    if posts:
        page = request.args.get('page', 1, type=int)
        # posts = Post.query.order_by(Post.date_posted.desc()) \
            # .paginate(page=page, per_page=4)
        posts= posts.paginate(page=page, per_page=4)
        # posts = Post.query.filter_by(user_id=current_user.id) \
        #     .order_by(Post.date_posted.desc()) \
        #     .paginate(page=page, per_page=2)
        # image_file = url_for('static',
        #                      filename=f'profile_pics/{current_user.username}/{post.image_post}')

        return render_template('main/blog.html', title='Blog', posts=posts,
                               all_users=all_users)
    else:
        return render_template('main/blog.html', title='Blog', nothing='No articles yet')


@main.route('/novelty_page')
def novelty_page():
    return render_template('main/novelty_page.html')


@main.route('/skincare_page')
def skincare_page():
    return render_template('main/skincare_page.html')


@main.route('/decorative_page')
def decorative_page():
    return render_template('main/decorative_page.html')


@main.route('/hand_made_page')
def hand_made_page():
    return render_template('main/hand_made_page.html')


@main.route('/dangerous_page')
def dangerous_page():
    return render_template('main/dangerous_page.html')


@main.route('/procedures_page')
def procedures_page():
    return render_template('main/procedures_page.html')


@main.route('/recipes_page')
def recipes_page():
    return render_template('main/recipes_page.html')
