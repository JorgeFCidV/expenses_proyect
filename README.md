# README - App de Gestión de Gastos

## Descripción General
Esta es una aplicación web desarrollada en Python con Flask para la gestión de gastos en empresas.
Permite subir tickets o facturas simplificadas (en formato JPG, JPEG, PNG o PDF), procesarlas con OCR básico para extraer datos, clasificarlos y guardarlos. (En proyecto: Cumple con requisitos legales españoles (Orden EHA/962/2007) para homologación de imágenes)

La app es multi-tenant: soporta múltiples empresas, usuarios con roles jerárquicos (master, admin, user), y gestión de categorías, métodos de pago y cuentas analíticas por empresa.

**Características clave**:
- Subida de tickets/PDF con rotación automática y OCR básico (extrae NIF, nombre, importe, fecha, naturaleza).
- Auto-rellenado de campos en edición con datos del OCR.
- Listados de gastos por rol (master ve todo, admin ve su empresa, user solo sus gastos).
- Edición y eliminación de gastos.
- Gestión de categorías de gastos, métodos de pago y cuentas analíticas (añadir, activar/desactivar).
- Export de gastos a PDF y CSV.
- Recuperación de contraseña (simulada en terminal por ahora).
- Prevención de duplicados vía número de ticket.
- Campo 'País' (default España) y NIF opcional ('--' para gastos extranjeros).
- Interfaz responsiva con Bootstrap.

La app está en desarrollo, pero funcional para pruebas. En Fase 3 se añade OCR avanzado, PDF homologado, integración Odoo, emails reales y PWA.

## Estructura del Proyecto
```
expenses-project/
├── venv/                       # Entorno virtual (instala dependencias con pip install -r requirements.txt)
├── app/
│   ├── __init__.py             # Configuración de Flask, DB, LoginManager, creación de master
│   ├── models.py               # Modelos SQLAlchemy: User, Company, Expense, ExpenseCategory, PaymentMethod, AnalyticAccount
│   ├── routes.py               # Todas las rutas: login, logout, index, create-company, invite-user, upload, edit_expense, delete_expense, manage-categories, manage-payments, manage-analytic, export-gastos, uploads, reset-request, reset-token
│   ├── forms.py                # Formularios WTForms: LoginForm, CreateCompanyForm, InviteUserForm, UploadExpenseForm, EditExpenseForm, ExpenseCategoryForm, PaymentMethodForm, AnalyticAccountForm, ResetPasswordRequestForm, ResetPasswordForm
│   ├── utils.py                # Funciones auxiliares: save_picture (con rotación EXIF), ocr_process (con parseo para auto-rellenado, soporta PDF)
│   ├── email.py                # Funciones para emails (simulados en terminal: send_reset_password_mail, send_invite_mail)
│   ├── templates/              # Plantillas Jinja2 con Bootstrap
│   │   ├── base.html           # Template base
│   │   ├── login.html          # Login con enlace a reset
│   │   ├── master_dashboard.html # Dashboard master (empresas, usuarios, invitaciones)
│   │   ├── admin_dashboard.html  # Dashboard admin (gastos, usuarios, invitaciones, export)
│   │   ├── user_dashboard.html   # Dashboard user (gastos personales, editar/eliminar)
│   │   ├── create_company.html   # Crear empresa
│   │   ├── invite_user.html      # Invitar admin/user
│   │   ├── upload.html           # Subir ticket/PDF
│   │   ├── expense_edit.html     # Editar gasto (con auto-rellenado, vista de ticket, texto OCR)
│   │   ├── manage_categories.html # Gestionar categorías
│   │   ├── manage_payments.html   # Gestionar métodos de pago
│   │   ├── manage_analytic.html   # Gestionar cuentas analíticas
│   │   ├── reset_request.html     # Solicitar cambio contraseña
│   │   ├── reset_password.html    # Cambiar contraseña
│   └── static/
│       └── uploads/            # Carpeta para imágenes/PDF subidos
├── config.py                   # Configuraciones (SECRET_KEY, DB URI, etc.)
├── run.py                      # Entrada principal (app.run(host='0.0.0.0', port=80))
└── requirements.txt            # Dependencias (Flask, SQLAlchemy, Flask-Login, Flask-WTF, pytesseract, Pillow, psycopg2-binary, pymupdf, reportlab, etc.)
```

## Instalación y Ejecución
1. Activa el venv: `source venv/bin/activate`
2. Instala dependencias: `pip install -r requirements.txt` (incluye pymupdf, reportlab)
3. Configura DB en config.py: `SQLALCHEMY_DATABASE_URI = 'postgresql://odoo17:temporal@localhost/expense_tracker'`
4. Ejecuta: `python run.py` (o con sudo si en puerto 80)
5. Accede: http://gastos.jfcconta.eu o http://68.183.45.127:80

## Funcionalidades Implementadas
### Roles y Permisos
- **Master**: Acceso total. Crea empresas, invita admins/users, ve todos los gastos/usuarios, gestiona categorías/pagos/cuentas para todas las empresas.
- **Admin**: Gestiona su empresa(s). Invita users, ve/edit/elimin todos los gastos de su empresa, gestiona categorías/pagos/cuentas para su empresa.
- **User**: Solo ve/edit/elimin sus propios gastos. Sube tickets a sus empresas.

### Gestión de Gastos
- Subida de JPG/PNG/PDF → rotación automática → OCR básico → auto-rellenado de campos (NIF, proveedor, importe, fecha, naturaleza).
- Edición: Rellena campos, guarda y vuelve al listado.
- Eliminar: Botón en listados (con confirmación).
- Listados: Por rol (con export PDF/CSV desde admin/master).
- Campos: NIF/IVA, proveedor, cuenta analítica (select), naturaleza (select), importe, fecha, nº ticket (único), país (default España), forma de pago (select).

### Gestión de Empresas
- Master crea empresas.
- Usuarios asignados a empresas (many-to-many).

### Gestión de Categorias, Pagos, Cuentas Analíticas
- Por empresa.
- Admin/master añade, activa/desactiva.
- Defaults al crear empresa: categorías (Compras, Alojamiento, etc.), pagos (T. Débito, etc.), analítica 'General'.

### Otros
- Login/logout.
- Recuperación de contraseña (simulada en terminal).
- Prevención de duplicados con nº ticket.
- NIF opcional ('--' para extranjeros).
- País default 'España'.
- Export PDF/CSV.

## Pendiente para Fase 3
- OCR avanzado (Google Document AI para 98 % precisión).
- PDF homologado legal (con hash y sello de tiempo).
- Integración con Odoo 17 (conector OCA).
- Emails reales (Brevo + Postfix en puerto 2525).
- PWA instalable en móviles.
- Mejoras adicionales si las hay.

**VAMOS FASE 3** cuando digas. 

¡Ya tienes un MVP brutal, crack!
