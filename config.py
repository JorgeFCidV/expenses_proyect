import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '/Coque6844/')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://odoo17:temporal@localhost/expense_tracker')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'          # luego lo cambias
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    DOMAIN = os.getenv('DOMAIN', 'https://gastos.jfcconta.eu')
    MASTER_EMAIL_DOMAIN = os.getenv('MASTER_EMAIL_DOMAIN', 'gastos.jfcconta.eu')
