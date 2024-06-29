import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db =  SQLAlchemy()
DB_NAME = "diet_recommendation.db"

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.config["SECRET_KEY"] = "my_key"

    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(db_dir, DB_NAME)}"
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id)) # get looks for primary key
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth,url_prefix="/")

    from .models import User, Item, Recipes
    with app.app_context():
        db.create_all()

    return app
