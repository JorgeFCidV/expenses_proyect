from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'routes.login'
login_manager.login_message_category = 'info'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # Importamos los modelos aquí para evitar import circular
    from app.models import User, Company

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes import routes
    app.register_blueprint(routes)

    with app.app_context():
        db.create_all()
        
        # Obtener el dominio configurado
        domain = getattr(app.config, "MASTER_EMAIL_DOMAIN", None)
        if not domain:
            domain_url = app.config.get("DOMAIN", "gastos.jfcconta.eu")
            import re
            domain_match = re.search(r"https?://([^/]+)", domain_url)
            domain = domain_match.group(1) if domain_match else "gastos.jfcconta.eu"

        master_email = f"master@{domain}"

        # Crear usuario master si no existe
        if not User.query.filter_by(email=master_email).first():
            master = User(
                email=master_email,
                name='Master',
                role='master',
                is_active=True
            )
            master.set_password('master123')
            db.session.add(master)
            db.session.commit()
            print(f"Usuario master creado: {master_email} / master123")
        

        # El master pertenece a TODAS las empresas (incluso las que se creen después)
        master = User.query.filter_by(role='master').first()
        if master:
            for company in Company.query.all():
                if company not in master.companies:
                    master.companies.append(company)
            db.session.commit()

        # Crear carpeta uploads
        os.makedirs(os.path.join(app.root_path, 'static/uploads'), exist_ok=True)

    return app
