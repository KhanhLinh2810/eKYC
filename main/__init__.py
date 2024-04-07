from flask import Flask 
from flask_sqlalchemy import SQLAlchemy


from .config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from .auth import auth
    from .routes import main
    from .detection import detection
    from .recognition import recognition

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(detection)
    app.register_blueprint(recognition)

    return app