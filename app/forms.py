from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, FileField, SubmitField, TextAreaField, FloatField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from flask_wtf.file import FileRequired, FileAllowed
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repite Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Por favor usa un email diferente.')

class UploadExpenseForm(FlaskForm):
    company_id = SelectField('Empresa', coerce=int, validators=[DataRequired()])
    image = FileField('Imagen del Ticket', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg'], '¡Solo archivos JPG por requisitos legales en España!')
    ])
    amount = FloatField('Importe', validators=[Optional()])
    date = DateField('Fecha', validators=[Optional()])
    nif_iva = StringField('NIF/IVA', validators=[Optional(), Length(max=20)])
    company_name = StringField('Nombre Empresa', validators=[Optional()])
    notes = TextAreaField('Notas', validators=[Optional()])
    submit = SubmitField('Procesar Gasto')
