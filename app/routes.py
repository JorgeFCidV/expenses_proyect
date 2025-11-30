from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app, make_response
from flask_login import login_required, current_user, logout_user, login_user
from app.models import User, Company, Expense, ExpenseCategory, PaymentMethod, AnalyticAccount
from app.forms import (
    LoginForm, CreateCompanyForm, InviteUserForm,
    UploadExpenseForm, EditExpenseForm, ResetPasswordRequestForm, ResetPasswordForm,
    ExpenseCategoryForm, PaymentMethodForm, AnalyticAccountForm
)
from app import db
from app.utils import save_picture, ocr_process
from app.email import send_reset_password_mail, send_invite_mail
import os
from datetime import datetime
import csv
from io import StringIO

routes = Blueprint('routes', __name__)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user, remember=form.remember.data)
            flash('¡Bienvenido!', 'success')
            return redirect(url_for('routes.index'))
        flash('Email o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('routes.login'))

@routes.route('/')
@routes.route('/index')
@login_required
def index():
    if current_user.role == 'master':
        companies = Company.query.all()
        users = User.query.order_by(User.role.desc(), User.email).all()
        return render_template('master_dashboard.html', companies=companies, users=users)
    elif current_user.role == 'admin':
        company_ids = [c.id for c in current_user.companies]
        expenses = Expense.query.filter(Expense.company_id.in_(company_ids)).order_by(Expense.id.desc()).all()
        return render_template('admin_dashboard.html', expenses=expenses, companies=current_user.companies)
    else:
        expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.id.desc()).all()
        return render_template('user_dashboard.html', expenses=expenses)

@routes.route('/create-company', methods=['GET', 'POST'])
@login_required
def create_company():
    if current_user.role != 'master':
        flash('Solo el master puede crear empresas', 'danger')
        return redirect(url_for('routes.index'))
    form = CreateCompanyForm()
    if form.validate_on_submit():
        if Company.query.filter_by(vat=form.vat.data).first():
            flash('NIF ya existe', 'danger')
        else:
            c = Company(name=form.name.data, vat=form.vat.data)
            db.session.add(c)
            db.session.commit()
            flash('Empresa creada', 'success')
            # Defaults for new company
            defaults_categories = ["Compras", "Alojamiento", "Transportes", "Restauración", "Otros"]
            for cat in defaults_categories:
                new_cat = ExpenseCategory(name=cat, company_id=c.id, is_active=True)
                db.session.add(new_cat)
            defaults_payments = ["T. Débito", "T. Crédito", "T. Prepago", "Efectivo"]
            for pm in defaults_payments:
                new_pm = PaymentMethod(name=pm, company_id=c.id, is_active=True)
                db.session.add(new_pm)
            db.session.commit()
            return redirect(url_for('routes.index'))
    return render_template('create_company.html', form=form)

@routes.route('/invite/<string:role>', methods=['GET', 'POST'])
@login_required
def invite_user(role):
    if current_user.role == 'master':
        allowed = ['admin', 'user']
        companies = Company.query.all()
    elif current_user.role == 'admin':
        allowed = ['user']
        companies = current_user.companies
    else:
        flash('Sin permiso', 'danger')
        return redirect(url_for('routes.index'))
    if role not in allowed:
        flash('Rol no permitido', 'danger')
        return redirect(url_for('routes.index'))
    form = InviteUserForm()
    form.company_id.choices = [(c.id, f"{c.name} ({c.vat})") for c in companies]
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('Email ya registrado', 'warning')
        else:
            user = User(email=form.email.data.lower(), name=form.name.data, role=role, is_active=True)
            user.set_password(form.temp_password.data)
            db.session.add(user)
            db.session.flush()
            company = Company.query.get(form.company_id.data)
            user.companies.append(company)
            db.session.commit()
            send_invite_mail(user, company, form.temp_password.data)
            flash(f'{role.capitalize()} invitado correctamente', 'success')
            return redirect(url_for('routes.index'))
    return render_template('invite_user.html', form=form, role=role)

@routes.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_expense():
    form = UploadExpenseForm()
    if form.validate_on_submit():
        filename = save_picture(form.ticket.data)
        full_path = os.path.join(current_app.root_path, 'static', 'uploads', filename)
        text = ocr_process(full_path)
        company_id = form.company_id.data or current_user.companies[0].id
        e = Expense(image_path=filename, extracted_text=text, user_id=current_user.id, company_id=company_id)
        db.session.add(e)
        db.session.commit()
        flash('Ticket subido. Completa los datos', 'success')
        return redirect(url_for('routes.edit_expense', expense_id=e.id))
    return render_template('upload.html', form=form)
@routes.route('/expense/<int:expense_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if current_user.role != "master" and expense.company_id not in [c.id for c in current_user.companies]:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('routes.index'))
    form = EditExpenseForm()
    if form.validate_on_submit():
        expense.nif_iva = form.nif_iva.data
        expense.company_name = form.company_name.data
        expense.analytic_account = form.analytic_account.data
        expense.expense_nature = form.expense_nature.data
        amount_str = request.form.get("amount", "")
        expense.amount = float(amount_str.replace(",", ".")) if amount_str else expense.amount
        fecha = request.form.get("date", "")
        if fecha:
            expense.date = datetime.strptime(fecha, "%Y-%m-%d").date()
        db.session.commit()
        flash("Gasto guardado correctamente", "success")
        return redirect(url_for("routes.index"))

    # GET: rellenamos form
    form.nif_iva.data = expense.nif_iva or ""
    form.company_name.data = expense.company_name or ""
    form.analytic_account.data = expense.analytic_account or ""
    form.expense_nature.data = expense.expense_nature or ""
    form.amount.data = expense.amount or 0.0
    form.date.data = expense.date or datetime.today().date()

    return render_template('expense_edit.html', form=form, expense=expense)

@routes.route('/uploads/<filename>')
def uploads(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'static', 'uploads'), filename)

@routes.route('/reset-request', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            send_reset_password_mail(user)
        flash('Revisa tu email para resetear tu contraseña', 'info')
        return redirect(url_for('routes.login'))
    return render_template('reset_password.html', form=form)

@routes.route('/expense/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    if current_user.role != "master" and expense.company_id not in [c.id for c in current_user.companies]:
        flash('Acceso denegado', 'danger')
        return redirect(url_for('routes.index'))
    try:
        os.remove(os.path.join(current_app.root_path, 'static', 'uploads', expense.image_path))
    except:
        pass
    db.session.delete(expense)
    db.session.commit()
    flash('Gasto eliminado correctamente', 'success')
    return redirect(url_for('routes.index'))

# GESTIÓN DE CATEGORÍAS DE GASTO (para admin)
@routes.route('/manage-categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if current_user.role not in ['master', 'admin']:
        return redirect(url_for('routes.index'))
    company_ids = [c.id for c in current_user.companies] if current_user.role == 'admin' else None
    categories = ExpenseCategory.query.filter(ExpenseCategory.company_id.in_(company_ids)) if company_ids else ExpenseCategory.query.all()
    form = ExpenseCategoryForm()
    if form.validate_on_submit():
        new_cat = ExpenseCategory(name=form.name.data, company_id=current_user.companies[0].id if current_user.role == 'admin' else request.form.get('company_id'))
        db.session.add(new_cat)
        db.session.commit()
        flash('Categoría añadida', 'success')
        return redirect(url_for('routes.manage_categories'))
    return render_template('manage_categories.html', form=form, categories=categories)

@routes.route('/category/<int:cat_id>/toggle', methods=['POST'])
@login_required
def toggle_category(cat_id):
    cat = ExpenseCategory.query.get_or_404(cat_id)
    if current_user.role != 'master' and cat.company_id not in [c.id for c in current_user.companies]:
        flash('Sin permiso', 'danger')
        return redirect(url_for('routes.manage_categories'))
    cat.is_active = not cat.is_active
    db.session.commit()
    flash('Categoría actualizada', 'success')
    return redirect(url_for('routes.manage_categories'))

# GESTIÓN DE FORMAS DE PAGO
@routes.route('/manage-payments', methods=['GET', 'POST'])
@login_required
def manage_payments():
    if current_user.role not in ['master', 'admin']:
        flash('Sin permiso', 'danger')
        return redirect(url_for('routes.index'))
    company_ids = [c.id for c in current_user.companies] if current_user.role == 'admin' else None
    methods = PaymentMethod.query.filter(PaymentMethod.company_id.in_(company_ids)) if company_ids else PaymentMethod.query.all()
    form = PaymentMethodForm()
    if form.validate_on_submit():
        new_pm = PaymentMethod(name=form.name.data, company_id=current_user.companies[0].id if current_user.role == 'admin' else request.form.get('company_id'))
        db.session.add(new_pm)
        db.session.commit()
        flash('Forma de pago añadida', 'success')
        return redirect(url_for('routes.manage_payments'))
    return render_template('manage_payments.html', form=form, methods=methods)

@routes.route('/payment/<int:pm_id>/toggle', methods=['POST'])
@login_required
def toggle_payment(pm_id):
    pm = PaymentMethod.query.get_or_404(pm_id)
    if current_user.role != 'master' and pm.company_id not in [c.id for c in current_user.companies]:
        flash('Sin permiso', 'danger')
        return redirect(url_for('routes.manage_payments'))
    pm.is_active = not pm.is_active
    db.session.commit()
    flash('Forma de pago actualizada', 'success')
    return redirect(url_for('routes.manage_payments'))

@routes.route('/manage-analytic', methods=['GET', 'POST'])
@login_required
def manage_analytic():
    if current_user.role not in ['master', 'admin']:
        flash('Sin permiso', 'danger')
        return redirect(url_for('routes.index'))
    company_ids = [c.id for c in current_user.companies] if current_user.role == 'admin' else None
    accounts = AnalyticAccount.query.filter(AnalyticAccount.company_id.in_(company_ids)) if company_ids else AnalyticAccount.query.all()
    form = AnalyticAccountForm()
    if form.validate_on_submit():
        new_acc = AnalyticAccount(name=form.name.data, company_id=current_user.companies[0].id if current_user.role == 'admin' else request.form.get('company_id'))
        db.session.add(new_acc)
        db.session.commit()
        flash('Cuenta analítica añadida', 'success')
        return redirect(url_for('routes.manage_analytic'))
    return render_template('manage_analytic.html', form=form, accounts=accounts)

@routes.route('/analytic/<int:acc_id>/toggle', methods=['POST'])
@login_required
def toggle_analytic(acc_id):
    acc = AnalyticAccount.query.get_or_404(acc_id)
    if current_user.role != 'master' and acc.company_id not in [c.id for c in current_user.companies]:
        flash('Sin permiso', 'danger')
        return redirect(url_for('routes.manage_analytic'))
    acc.is_active = not acc.is_active
    db.session.commit()
    flash('Cuenta analítica actualizada', 'success')
    return redirect(url_for('routes.manage_analytic'))

@routes.route('/reports/<format>')
@login_required
def reports(format):
    if current_user.role == 'user':
        return redirect(url_for('routes.index'))
    company_ids = [c.id for c in current_user.companies] if current_user.role == 'admin' else None
    expenses = Expense.query.filter(Expense.company_id.in_(company_ids)) if company_ids else Expense.query.all()
    if format == 'pdf':
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        response = make_response()
        response.headers["Content-Disposition"] = "attachment; filename=gastos.pdf"
        response.headers["Content-type"] = "application/pdf"
        c = canvas.Canvas(response, pagesize=letter)
        y = 750
        c.drawString(100, y, "Listado de Gastos")
        y -= 20
        for e in expenses:
            c.drawString(100, y, f"{e.date} - {e.company_name} - €{e.amount}")
            y -= 20
        c.save()
        return response
    elif format == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Fecha", "Proveedor", "Importe"])
        for e in expenses:
            writer.writerow([e.id, e.date, e.company_name, e.amount])
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=gastos.csv"
        response.headers["Content-type"] = "text/csv"
        return response
    return redirect(url_for('routes.index'))
