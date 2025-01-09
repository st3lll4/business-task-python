from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hehehe'

    from .views import views # importing blueprints
    from .auth import auth

    app.register_blueprint(views, url_prefix='/') # can be accessed from /
    app.register_blueprint(auth, url_prefix='/')

    return app