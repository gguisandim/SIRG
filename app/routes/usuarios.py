from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
import pyrebase
from app import db
from app.models import Usuario, Membro
from app.forms import LoginForm, CadastroUsuarioForm
from app import oauth
import secrets

usuarios = Blueprint("usuarios", __name__, url_prefix="/usuarios")

PERFIS_ADMINISTRATIVOS = ["coordenador", "secretaria", "bolsista"]

# Função auxiliar para inicializar o Firebase
def get_firebase_auth():
    firebase = pyrebase.initialize_app(current_app.config["FIREBASE_CONFIG"])
    return firebase.auth()

@usuarios.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.perfil == "professor":
            return redirect(url_for("justificativas.minhas_faltas"))
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        senha = form.senha.data

        try:
            # 1. Fazer login no Firebase
            auth = get_firebase_auth()
            user = auth.sign_in_with_email_and_password(email, senha)

            usuario = Usuario.query.filter_by(email=email).first()

            if usuario and usuario.ativo:
                login_user(usuario)
                flash("Login realizado com sucesso.", "success")

                if usuario.perfil == "professor":
                    return redirect(url_for("justificativas.minhas_faltas"))
                return redirect(url_for("dashboard"))
            else:
                flash("O seu utilizador está desativado ou não existe no sistema local.", "warning")

        except Exception as e:
            # Se o Firebase der erro (senha errada ou utilizador inexistente), cai aqui.
            flash("E-mail ou palavra-passe inválidos.", "danger")
            print(f"Erro do Firebase: {e}")
    return render_template("usuarios/login.html", form=form)

@usuarios.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Saiu do sistema com sucesso.", "info")
    return redirect(url_for("usuarios.login"))

@usuarios.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    form = CadastroUsuarioForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        senha = form.senha.data
        siap= form.siap.data.strip()

        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            flash("Já existe um utilizador com esse e-mail no nosso sistema.", "warning")
            return render_template("usuarios/cadastrar.html", form=form)

        try:
            auth = get_firebase_auth()
            user = auth.create_user_with_email_and_password(email, senha)

            auth.send_email_verification(user['idToken'])

            membro = Membro.query.filter_by(email=email).first()

            if membro and not membro.siap:
                membro.siap = siap

            if not membro:
                membro= Membro(
                    nome=form.nome.data.strip().upper(),
                    email=email,
                    tipo="professor",
                    ativo=True
                )
                db.session.add(membro)
                db.session.flush()

            usuario = Usuario(
                nome=form.nome.data,
                email=email,
                perfil="professor",
                membro_id=membro.id if membro else None
            )
            usuario.set_password(senha)

            db.session.add(usuario)
            db.session.commit()

            flash("Utilizador cadastrado com sucesso! Enviamos um link de confirmação para o seu e-mail. Por favor, verifique-o antes de fazer login.", "success")
            return redirect(url_for("usuarios.login"))

        except Exception as e:
            db.session.rollback()
            flash("Erro ao cadastrar no Firebase. Verifique se o e-mail é válido.", "danger")
            print(f"Erro do Firebase: {e}")

    return render_template("usuarios/cadastrar.html", form=form)

@usuarios.route('/login/google')
def login_google():
    redirect_uri = url_for('usuarios.autorizado_google', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@usuarios.route('/login/google/autorizado')
def autorizado_google():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')

    if not user_info:
        flash('Erro ao tentar fazer login com o Google.', 'danger')
        return redirect(url_for('usuarios.login'))

    email = user_info.get('email').lower().strip()
    nome = user_info.get('name')

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario:
        login_user(usuario)
        flash(f'Bem-vindo de volta, {nome}!', 'success')
        
    else:
      
        usuario = Usuario(
            nome=nome,
            email=email,
            perfil='professor', # Perfil padrão que você estava usando
            ativo=True
        )
       
        senha_aleatoria = secrets.token_urlsafe(16)
        usuario.set_password(senha_aleatoria)
        
        db.session.add(usuario)

        membro_existente = Membro.query.filter_by(email=email).first()
        if not membro_existente:
            novo_membro = Membro(
                nome=nome.upper(),
                email=email,
                tipo='professor',
                ativo=True
            )
            dp.session.add(novo_membro)

        db.session.commit()
        
        login_user(usuario)
        flash('Sua conta foi criada automaticamente com o Google!', 'success')

    return redirect(url_for('home'))

@usuarios.route("/membro/<int:membro_id>/resetar-senha", methods=["POST"])
@login_required
def resetar_senha_membro(membro_id):
    flash("A redefinição de palavra-passe agora é gerida pelo Firebase.", "info")
    return redirect(url_for("membros.listar_membros"))