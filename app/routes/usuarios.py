from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
import pyrebase
from app import db
from app.models import Usuario, Membro
from app.forms import LoginForm, CadastroUsuarioForm

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

        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            flash("Já existe um utilizador com esse e-mail no nosso sistema.", "warning")
            return render_template("usuarios/cadastrar.html", form=form)

        try:
            # Criar o utilizador no Firebase
            auth = get_firebase_auth()
            user = auth.create_user_with_email_and_password(email, senha)

            # Envia o e-mail de verificação usando o token do usuário recém-criado
            auth.send_email_verification(user['idToken'])

            # Registar o utilizador na nossa base de dados local
            membro = Membro.query.filter_by(email=email).first()

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
            flash("Erro ao cadastrar no Firebase. Verifique se o e-mail é válido.", "danger")
            print(f"Erro do Firebase: {e}")

    return render_template("usuarios/cadastrar.html", form=form)

@usuarios.route("/membro/<int:membro_id>/resetar-senha", methods=["POST"])
@login_required
def resetar_senha_membro(membro_id):
    flash("A redefinição de palavra-passe agora é gerida pelo Firebase.", "info")
    return redirect(url_for("membros.listar_membros"))