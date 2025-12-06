# app/models.py
from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Tabla de asociación (funciona con SQLAlchemy 2.0+)
user_company = db.Table('user_company',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('company_id', db.Integer, db.ForeignKey('company.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'master', 'admin', 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación many-to-many
    companies = db.relationship('Company', secondary=user_company,
                                lazy='select', backref=db.backref('users', lazy='dynamic'))

    @property
    def allowed_companies(self):
        if self.role == 'master':
            return Company.query.order_by(Company.name).all()
        return sorted(self.companies, key=lambda c: c.name)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    nif_iva = db.Column(db.String(20), nullable=False, unique=True)
    analytic_account = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ExpenseNature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(200), nullable=False)
    extracted_text = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    expense_nature = db.Column(db.String(100), nullable=False, default='Otros')
    nif_iva = db.Column(db.String(20))
    company_name = db.Column(db.String(120))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
