from flask import Flask
from config import config_options
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app(config_state):
    app = Flask(__name__)
    app.config.from_object(config_options[config_state])

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

