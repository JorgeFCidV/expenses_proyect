from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Asegurar carpeta uploads
    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.routes import routes
    app.register_blueprint(routes)

    login.login_view = 'routes.login'
    login.login_message = 'Por favor, inicia sesión para acceder a esta página.'

    return app
