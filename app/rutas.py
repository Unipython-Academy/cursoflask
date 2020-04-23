from flask import render_template, json
from app import app, bdd
from app.formularios import FormInicio, FormRegistro, EditarPerfil, RecuperarContraseña, ResetearContraseña
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.modelos import Usuario, Pubs
from werkzeug.urls import url_parse
from datetime import datetime
from app.formularios import Publicaciones
from app.enviar_email import contraseña_olvidada
from werkzeug.utils import secure_filename
import os
from PIL import Image
import time

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = Publicaciones()
    pagina = request.args.get('pagina', 1, type=int)
    posts = current_user.pubs_seguidores().paginate(
        pagina, app.config['POSTS_PER_PAGE'], False)
    pagina_sig = url_for('index', pagina=posts.next_num) \
        if posts.has_next else None
    pagina_ant = url_for('index', pagina=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', titulo='Página de inicio', form=form, posts=posts.items, pagina_sig=pagina_sig, pagina_ant=pagina_ant)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = FormInicio()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.nombre.data).first()
        if usuario:
            if usuario.verif_clave(form.contraseña.data):
                login_user(usuario, remember=form.recordar.data)
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                flash('Usuario o contraseña inválido')
    return render_template('iniciar_sesion.html', titulo='Iniciar Sesion', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = FormRegistro()
    if form.validate_on_submit():
        usuario = Usuario(username=form.username.data, email=form.email.data)
        usuario.def_clave(form.contraseña.data)
        bdd.session.add(usuario)
        bdd.session.commit()
        flash('Usuario registrado correctamente, ahora puedes iniciar sesión.')
        return redirect(url_for('login'))
    return render_template('registro.html', titulo='Registro', form=form)


@app.route('/usuario/<username>')
@login_required
def perfil_usuario(username):
    usuario = Usuario.query.filter_by(username=username).first_or_404()
    pagina = request.args.get('pagina', 1, type=int)
    posts = usuario.pubs.order_by(Pubs.timestamp.desc()).paginate(
        pagina, app.config['POSTS_PER_PAGE'], False)
    pagina_sig = url_for('perfil_usuario', username=usuario.username, pagina=posts.next_num) \
        if posts.has_next else None
    pagina_ant = url_for('perfil_usuario', username=usuario.username, pagina=posts.prev_num) \
        if posts.has_prev else None
    return render_template('usuarios.html', usuario=usuario, posts=posts.items, pagina_sig=pagina_sig, pagina_ant=pagina_ant)


@app.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = EditarPerfil(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.sobre_mi = form.sobre_mi.data
        bdd.session.commit()
        flash('Tus cambios han sido guardados correctamente')
        return redirect(url_for('editar_perfil'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.sobre_mi.data = current_user.sobre_mi
    return render_template('editar_perfil.html', titulo='Editar Perfil', form=form)


@app.route('/seguir/<username>')
@login_required
def seguir(username):
    usuario = Usuario.query.filter_by(username=username).first()
    if usuario is None:
        flash('Usuario {} no encontrado.'.format(username))
        return redirect(url_for('index'))
    if usuario == current_user:
        flash('¡No puedes realizar esta accion contigo mismo!')
        return redirect(url_for('perfil_usuario', username=username))
    current_user.seguir(usuario)
    bdd.session.commit()
    flash('¡Ahora estas siguiendo a {}!'.format(username))
    return redirect(url_for('perfil_usuario', username=username))


@app.route('/dejar_seguir/<username>')
@login_required
def dejar_seguir(username):
    usuario = Usuario.query.filter_by(username=username).first()
    if usuario is None:
        flash('Usuario {} no encontrado.'.format(username))
        return redirect(url_for('index'))
    if usuario == current_user:
        flash('¡No puedes realizar esta accion contigo mismo!')
        return redirect(url_for('perfil_usuario', username=username))
    current_user.dejar_seguir(usuario)
    bdd.session.commit()
    flash('Dejaste de seguir a {}.'.format(username))
    return redirect(url_for('perfil_usuario', username=username))


@app.route('/explorar')
@login_required
def explorar():
    pagina = request.args.get('pagina', 1, type=int)
    posts = Pubs.query.order_by(Pubs.timestamp.desc()).paginate(
        pagina, app.config['POSTS_PER_PAGE'], False)
    pagina_sig = url_for('explorar', pagina=posts.next_num) \
        if posts.has_next else None
    pagina_ant = url_for('explorar', pagina=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", titulo='Explorar', posts=posts.items,
                           pagina_sig=pagina_sig, pagina_ant=pagina_ant)


@app.route('/recuperar_contraseña', methods=['GET', 'POST'])
def recuperar_contraseña():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RecuperarContraseña()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario is None:
            flash(
                'No existe ningún usuario con este correo electrónico en nuestros registros')
            form.email.data = ""
            redirect(url_for('recuperar_contraseña'))
        if usuario is not None:
            contraseña_olvidada(usuario)
            flash('Chequea tu email para completar la recuperación de contraseña')
            return redirect(url_for('login'))
    return render_template('recuperar_contraseña.html', titulo='Recuperar contraseña', form=form)


@app.route('/resetear_contraseña/<token>', methods=['GET', 'POST'])
def resetear_contraseña(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    usuario = Usuario.verificar_token_contraseña(token)
    if not usuario:
        return redirect(url_for('index'))
    form = ResetearContraseña()
    if form.validate_on_submit():
        usuario.def_clave(form.contraseña.data)
        bdd.session.commit()
        flash('Tu contraseña ha sido cambiada')
        return redirect(url_for('login'))
    return render_template('resetear_contraseña.html', form=form)


@app.route('/obtener_post', methods=["POST"])
def obtener_post():
    form = Publicaciones()
    if form.validate_on_submit():
        post = Pubs(cuerpo=form.post.data, autor=current_user)
        imagen = form.imagen.data
        nombre_imagen = secure_filename(
            current_user.username + '_' + imagen.filename)
        ruta_imagen = os.path.abspath(
            'app\\static\\uploads\\{}'.format(nombre_imagen))
        ruta_html = '../static/uploads/{}'.format(nombre_imagen)
        imagen.save(ruta_imagen)
        if imagen.filename != '':
            print('=== Estoy validando la imagen ===')
            imagen = Image.open(ruta_imagen)
            if imagen.width > 1980 and imagen.height > 1080:
                reducirTamaño_imagen = imagen.resize((1980, 1080))
                reducirTamaño_imagen.save(ruta_imagen, optimize=True) 
                post.post_imagen = ruta_html
            else: 
                imagen.save(ruta_imagen, optimize=True)
                post.post_imagen = ruta_html

        bdd.session.add(post)
        bdd.session.commit()
    return "Success"
    


@app.route('/ajax_posts', methods=["GET", "POST"])
@login_required
def get_posts():
    time.sleep(1) # Hacemos una pequeña espera para que la petición AJAX lea los datos correctamente.
    print('Iniciar')
    pagina = request.args.get('pagina', 1, type=int)
    posts = current_user.pubs_seguidores().paginate(
        pagina, app.config['POSTS_PER_PAGE'], False)
    pagina_sig = url_for('index', pagina=posts.next_num) \
        if posts.has_next else None
    pagina_ant = url_for('index', pagina=posts.prev_num) \
        if posts.has_prev else None
    return render_template('$ajax_posts.html', posts=posts.items, pagina_sig=pagina_sig, pagina_ant=pagina_ant)


@app.before_request  # Decorador que intercepta toda petición al servidor y ejecuta las función que se le establezca antes de realizar la que se solicito por el front-end
def ultima_sesion():
    if current_user.is_authenticated:
        current_user.ultima_sesion = datetime.utcnow()
        bdd.session.commit()
 