from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField, DateField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recuérdame')
    submit = SubmitField('Entrar')

class CreateCompanyForm(FlaskForm):
    name = StringField('Nombre empresa', validators=[DataRequired()])
    vat = StringField('NIF/CIF', validators=[DataRequired(), Length(9,20)])
    submit = SubmitField('Crear empresa')

class InviteUserForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    temp_password = PasswordField('Contraseña temporal', validators=[DataRequired(), Length(6)])
    company_id = SelectField('Empresa', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Invitar')

class UploadExpenseForm(FlaskForm):
    image = FileField('Foto o PDF del ticket', validators=[DataRequired(), FileAllowed(['jpg','jpeg','png','pdf'])])
    company_id = SelectField('Empresa', coerce=int, validators=[Optional()])
    submit = SubmitField('Procesar')

class EditExpenseForm(FlaskForm):
    nif_iva = StringField('NIF/IVA', validators=[Optional()])
    company_name = StringField('Proveedor', validators=[Optional()])
    analytic_account = SelectField('Cuenta analítica', coerce=int, validators=[Optional()])
    expense_nature = SelectField('Naturaleza del gasto', coerce=int, validators=[Optional()])
    amount = FloatField('Importe €', validators=[Optional()])
    date = DateField('Fecha', validators=[Optional()])
    ticket_number = StringField('Nº ticket', validators=[Optional()])
    country = StringField('País', validators=[Optional()])
    payment_method = SelectField('Forma de pago', coerce=int, validators=[Optional()])
    submit = SubmitField('Guardar')

class ExpenseCategoryForm(FlaskForm):
    name = StringField('Nombre categoría', validators=[DataRequired()])
    is_active = BooleanField('Activa')
    submit = SubmitField('Guardar categoría')

class PaymentMethodForm(FlaskForm):
    name = StringField('Nombre método', validators=[DataRequired()])
    is_active = BooleanField('Activo')
    submit = SubmitField('Guardar método')

class AnalyticAccountForm(FlaskForm):
    name = StringField('Nombre cuenta', validators=[DataRequired()])
    is_active = BooleanField('Activa')
    submit = SubmitField('Guardar cuenta')
