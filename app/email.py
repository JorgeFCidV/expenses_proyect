from flask import current_app

def send_reset_password_mail(user):
    print("\n" + "="*50)
    print("SOLICITUD DE CAMBIO DE CONTRASEÑA")
    print(f"Usuario: {user.email}")
    print(f"Enlace (válido 1 hora): http://gastos.jfcconta.eu/reset/fake-token-para-pruebas")
    print("="*50 + "\n")

def send_invite_mail(user, company, temp_password):
    print("\n" + "="*60)
    print("NUEVA INVITACIÓN AL SISTEMA DE GASTOS")
    print(f"Nombre: {user.name}")
    print(f"Email: {user.email}")
    print(f"Empresa: {company.name} ({company.vat})")
    print(f"Contraseña temporal: {temp_password}")
    print(f"Enlace: https://gastos.jfcconta.eu")
    print("="*60 + "\n")
