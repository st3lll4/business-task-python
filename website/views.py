from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/') # @, name of blueprint, .route, url to get to endpoint. homepage
def home():
    return render_template("home.html")

