from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, Date, Boolean, Text, ForeignKey

# Tabla asociación user-company
user_company = Table('user_company',
    db.Column('user_id', Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('company_id', Integer, db.ForeignKey('company.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(String(128), nullable=False)
    role = db.Column(String(20), default='user')  # 'master', 'admin', 'user'
    created_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Relación many-to-many con companies
    companies = db.relationship('Company', secondary=user_company, lazy='select', backref=db.backref('users', lazy='dynamic'))
    
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
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(120), nullable=False)
    nif_iva = db.Column(String(20), nullable=False, unique=True)  # Obligatorio por requisitos
    analytic_account = db.Column(String(50), nullable=True)  # Campo adicional requerido
    created_at = db.Column(DateTime, default=datetime.utcnow)

class ExpenseNature(db.Model):
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    company_id = db.Column(Integer, db.ForeignKey('company.id'), nullable=False)

class Expense(db.Model):
    id = db.Column(Integer, primary_key=True)
    image_path = db.Column(String(200), nullable=False)
    extracted_text = db.Column(Text)
    amount = db.Column(Float, nullable=False)
    date = db.Column(Date, nullable=False)
    expense_nature = db.Column(String(100), nullable=False, default='Otros')
    nif_iva = db.Column(String(20))  # De OCR o manual
    company_name = db.Column(String(120))  # De OCR o manual
    company_id = db.Column(Integer, db.ForeignKey('company.id'), nullable=False)
    user_id = db.Column(Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
