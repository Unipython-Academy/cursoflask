from flask import Flask
from app.settings.config import Ajustes, ConexionMail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler
from flask_moment import Moment

app = Flask(__name__)
app.config.from_object(Ajustes)
bdd = SQLAlchemy(app)
migrate = Migrate(app, bdd)
moment = Moment(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'Por favor inicia sesión para acceder a esta página.'

from app import rutas, modelos, errores

# Configurando el servidor de email para los errores en formularios

if app.debug == False:
    if ConexionMail.MAIL_SERVER:
        autenticacion = None
        if ConexionMail.MAIL_USERNAME or ConexionMail.MAIL_PASSWORD:
            autenticacion = (ConexionMail.MAIL_USERNAME, ConexionMail.MAIL_PASSWORD)
        seguridad = None
        if ConexionMail.MAIL_USE_TLS:
            seguridad = ()
        enviar_email = SMTPHandler(
            mailhost = (ConexionMail.MAIL_SERVER, ConexionMail.MAIL_PORT),
            fromaddr = 'no-reply@' + ConexionMail.MAIL_SERVER,
            toaddrs = ConexionMail.ADMINS, subject='Fallo encontrado en nuestro Blog',
            credentials= autenticacion, secure=seguridad
        )
        enviar_email.setLevel(logging.ERROR)
        app.logger.addHandler(enviar_email)