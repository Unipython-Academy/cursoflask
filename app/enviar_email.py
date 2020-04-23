from app.settings.config import ConexionMail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import render_template
from app import app
from threading import Thread

def email_asincrono(server, mensaje):
    server.sendmail(mensaje['From'], mensaje['To'], mensaje.as_string())
    server.quit()


def contraseña_olvidada(usuario):

    # Configurando servidor email para contraseñas olvidadas

    mensaje = MIMEMultipart() # Creamos el objeto mensaje
    token = usuario.obtener_token_contraseña()
    password = ConexionMail.MAIL_PASSWORD
    msj = render_template('recuperar_contraseña.txt', usuario=usuario, token=token)
    mensaje['From'] = ConexionMail.MAIL_USERNAME
    mensaje['To'] = usuario.email
    mensaje['Subject'] = 'Recuperar contraseña'
    mensaje.attach(MIMEText(msj, 'plain')) # Le decimos que el mensaje contiene solamente texto plano
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(mensaje['From'], password)
    Thread(target=email_asincrono, args=(server,mensaje)).start()



