from flask import Blueprint, render_template, request, flash, abort
from flask_login import  current_user
from blog.models import Post, User



main = Blueprint('main', __name__, template_folder='templates')


@main.route('/')
def home():
    return render_template("main/index.html", title="Main")


@main.route('/blog', methods=['GET'])
# @login_required
def blog():
    if current_user.is_authenticated:
        all_users = User.query.all()
        posts = Post.query.order_by(Post.date_posted.desc())
        if posts.count() > 0:
            page = request.args.get('page', 1, type=int)
            posts = posts.paginate(page=page, per_page=4)

            return render_template('main/blog.html', title='Blog', posts=posts,
                                   all_users=all_users)
        else:
            flash('No articles yet', 'info')
            return render_template('main/blog.html', title='Blog',  posts=posts, nothing=' ')
    else:
        abort(500)

@main.route('/category/<string:category_name>/')
# @login_required
def category_page(category_name):
    posts_category = Post.query.filter_by(category=category_name).all()
    return render_template('main/category_page.html', post_category=posts_category, category_name=category_name,
                           title='Category ' + category_name)

