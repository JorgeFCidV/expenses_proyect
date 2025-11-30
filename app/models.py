from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
import os

serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY', 'temporal'))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')  # master, admin, user
    is_active = db.Column(db.Boolean, default=True)

    companies = db.relationship('Company', secondary='user_company', back_populates='users')
    expenses = db.relationship('Expense', backref='creator', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=3600):
        return serializer.dumps({'user_id': self.id}, salt='reset-salt')

    @staticmethod
    def verify_reset_token(token, max_age=3600):
        try:
            data = serializer.loads(token, salt='reset-salt', max_age=max_age)
            return User.query.get(data['user_id'])
        except:
            return None

user_company = db.Table('user_company',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('company_id', db.Integer, db.ForeignKey('company.id'), primary_key=True)
)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    vat = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', secondary=user_company, back_populates='companies')
    expenses = db.relationship('Expense', backref='company', lazy=True)

    # Categories and payment methods per company
    expense_categories = db.relationship('ExpenseCategory', backref='company', lazy=True, cascade="all, delete-orphan")
    payment_methods = db.relationship('PaymentMethod', backref='company', lazy=True, cascade="all, delete-orphan")
    analytic_accounts = db.relationship('AnalyticAccount', backref='company', lazy=True, cascade="all, delete-orphan")

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text)
    nif_iva = db.Column(db.String(50))
    company_name = db.Column(db.String(255))
    analytic_account = db.Column(db.String(100))
    expense_nature = db.Column(db.String(255))
    amount = db.Column(db.Numeric(10,2))
    date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    ticket_number = db.Column(db.String(50), unique=True)
    country = db.Column(db.String(50), default='España')
    payment_method = db.Column(db.String(50))

# Models for categories, payment methods, analytic accounts
class ExpenseCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class PaymentMethod(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class AnalyticAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
