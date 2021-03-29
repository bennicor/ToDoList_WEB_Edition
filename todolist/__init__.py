from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from todolist.config import Config

login_manager = LoginManager()
login_manager.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
        
    from todolist.users.routes import users
    app.register_blueprint(users)

    return app
