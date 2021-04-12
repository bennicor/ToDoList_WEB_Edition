from flask import Flask
from flask_login import LoginManager
from todolist.config import Config


login_manager = LoginManager()
login_manager.login_view = 'users.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    login_manager.init_app(app)
        
    from todolist.users.routes import users
    from todolist.main.routes import main
    from todolist.tasks.routes import tasks
    from todolist.errors.handlers import errors
    from todolist.api.routes import api
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(tasks)
    app.register_blueprint(errors)
    app.register_blueprint(api)

    return app
