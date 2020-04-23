from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flask_wtf.file import FileRequired, FileAllowed
from app.modelos import Usuario

class FormInicio(FlaskForm):
    nombre = StringField('Usuario', validators=[DataRequired(message='Este campo es requerido')])
    contraseña = PasswordField('Contraseña', validators=[DataRequired(message='Este campo es requerido')])
    recordar = BooleanField('Recordar Usuario')
    enviar = SubmitField('Iniciar Sesión')

class FormRegistro(FlaskForm):
  username = StringField('Nombre de Usuario', validators=[DataRequired(message='Este campo es requerido')])
  email = StringField('Email', validators=[DataRequired(message='Este campo es requerido'), Email()])
  contraseña = PasswordField('Contraseña', validators=[DataRequired(message='Este campo es requerido')])
  contraseña2 = PasswordField('Repita su Contraseña', validators=[DataRequired(message='Este campo es requerido'), EqualTo('contraseña', 'Las contraseñas no coinciden')])
  submit = SubmitField('Register')
  
  def validar_username(self, username):
    usuario = Usuario.query.filter_by(username=username.data).first()
    if usuario is not None:
      raise ValidationError('Ingrese un nombre de usuario distinto.')

  def validar_email(self, email):
    usuario = Usuario.query.filter_by(email=email.data).first()
    if usuario is not None:
        raise ValidationError('Ingrese un correo electrónico distinto')

class EditarPerfil(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(message='Este campo es requerido')])
    sobre_mi = TextAreaField('Sobre mi', validators=[Length(min=0, max=140)])
    submit = SubmitField('Enviar')

    def __init__(self, usuarioActual, *args, **kwargs):
        super(EditarPerfil, self).__init__(*args, **kwargs)
        self.usuarioActual = usuarioActual

    def validate_username(self, username):
        if username.data != self.usuarioActual:
            usuario = Usuario.query.filter_by(username=self.username.data).first()
            if usuario is not None:
                raise ValidationError('El nombre de usuario ya existe, por favor intenta con otro.')

class Publicaciones(FlaskForm):
    post = TextAreaField('Escribele algo al mundo', validators=[
        DataRequired(), Length(min=1, max=140)
    ])
    imagen = FileField('Imagen')
    submit = SubmitField('Postear')


class RecuperarContraseña(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Este campo es requerido'), Email()])
    submit = SubmitField('Recuperar contraseña')

class ResetearContraseña(FlaskForm):
    contraseña = PasswordField('Contraseña', validators=[DataRequired()])
    contraseña2 = PasswordField(
        'Repetir contraseña', validators=[DataRequired(), EqualTo('contraseña')])
    submit = SubmitField('Solicitar cambio de contraseña')



