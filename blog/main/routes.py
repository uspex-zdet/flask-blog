from flask import Blueprint, render_template

main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template("index.html", title="Main")


@main.route('/blog')
def blog():
    return render_template("blog.html", title="Blog")


@main.route('/novelty_page')
def novelty_page():
    return render_template('novelty_page.html')


@main.route('/skincare_page')
def skincare_page():
    return render_template('skincare_page.html')


@main.route('/decorative_page')
def decorative_page():
    return render_template('decorative_page.html')


@main.route('/hand_made_page')
def hand_made_page():
    return render_template('hand_made_page.html')


@main.route('/dangerous_page')
def dangerous_page():
    return render_template('dangerous_page.html')


@main.route('/procedures_page')
def procedures_page():
    return render_template('procedures_page.html')


@main.route('/recipes_page')
def recipes_page():
    return render_template('recipes_page.html')
