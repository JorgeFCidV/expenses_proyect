from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login
from app.forms import LoginForm, RegistrationForm, UploadExpenseForm
from app.models import User, Company, Expense
from app.utils import save_picture, ocr_process  # Ahora existen
from datetime import datetime
import os

routes = Blueprint('', __name__)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@routes.route('/')
@routes.route('/index')
@login_required
def index():
    return render_template('index.html', title='Inicio')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('routes.index'))
        flash('Email o contraseña inválidos.', 'danger')
    return render_template('login.html', title='Iniciar Sesión', form=form)

@routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@routes.route('/register', methods=['GET', 'POST'])
@login_required  # Solo admins/master pueden registrar
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        user.role = 'user'  # Por defecto
        db.session.add(user)
        db.session.commit()
        flash('Usuario registrado exitosamente.', 'success')
        return redirect(url_for('routes.index'))
    return render_template('register.html', title='Registrar Usuario', form=form)

@routes.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_expense():
    companies = current_user.allowed_companies
    form = UploadExpenseForm()
    form.company_id.choices = [(c.id, c.name) for c in companies]

    if not companies:
        flash('No tienes acceso a ninguna empresa. Contacta con el administrador.', 'danger')
        return redirect(url_for('routes.index'))

    if form.validate_on_submit():
        file = request.files['image']
        if file and file.filename:
            filename = save_picture(file)
            if filename:
                # OCR
                data = ocr_process(filename)
                expense = Expense(
                    image_path=os.path.join('uploads', filename),
                    extracted_text=data.get('text', ''),
                    amount=data.get('amount', form.amount.data or 0.0),
                    date=form.date.data or datetime.utcnow().date(),
                    expense_nature=data.get('nature', 'Otros'),
                    nif_iva=form.nif_iva.data or data.get('nif', ''),
                    company_name=form.company_name.data or data.get('company_name', ''),
                    company_id=form.company_id.data,
                    user_id=current_user.id
                )
                db.session.add(expense)
                db.session.commit()
                flash('Gasto subido y procesado con OCR correctamente.', 'success')
                return redirect(url_for('routes.index'))
            flash('Error al guardar la imagen.', 'danger')
        else:
            flash('Selecciona una imagen JPG válida.', 'danger')
    return render_template('upload.html', title='Subir Gasto', form=form)

# Otras rutas (agrega más como /expenses, /admin, etc.)
@routes.route('/expenses')
@login_required
def expenses():
    user_expenses = Expense.query.filter_by(user_id=current_user.id).all()
    return render_template('expenses.html', expenses=user_expenses)
