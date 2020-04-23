import os

bddPath = os.path.abspath('app.db')

class Ajustes(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'flask-course'
    SQLALCHEMY_DATABASE_URI = 'postgres://bufpwdjtpzcoel:bfcb328fe616c6ad1d0db4c602e78f580ba6cd4acabbea2211e5889f9f0e17b7@ec2-34-206-252-187.compute-1.amazonaws.com:5432/ddhekhobkm46k5'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE = 3

class ConexionMail(object):

    MAIL_SERVER= 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'peraltamfps@gmail.com'
    MAIL_PASSWORD = '23566727'
    ADMINS = 'peraltamfps@gmail.com'