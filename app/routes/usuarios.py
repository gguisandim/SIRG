from flask import Blueprint, render_template, redirect, url_for, flash, current_app, session, request
from flask_login import login_user, logout_user, login_required, current_user
import pyrebase
from app import db, mail
from app.models import Usuario, Membro
from app.forms import LoginForm, CadastroUsuarioForm
from app import oauth
import secrets
import random
from flask_mail import Message

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
        siap= form.siap.data.strip() if form.siap.data else ""

        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            flash("Já existe um utilizador com esse e-mail no nosso sistema.", "warning")
            return render_template("usuarios/cadastrar.html", form=form)

        codigo_verificacao = "".join(str(random.randint(0,9)) for _ in range (6))

        session["temp_user"] = {
            "nome": form.nome.data,
            "email": email, 
            "senha": senha,
            "siap": siap
        }
        session["verification_code"] = codigo_verificacao
        

        try:
            msg = Message(
                "Código de Verificação - SIRG",
                recipients=[email]
            )
            msg.body = f"Olá, {form.nome.data}!\n\nSeu código de validação para concluir o seu cadastro no SIRG é: {codigo_verificacao}\n\nPor favor, digite esse código no sistema."
            mail.send(msg)

            flash("Enviamos um código de verificação para o seu e-mail.", "info")
            return redirect(url_for("usuarios.verificar_codigo"))

        except Exception as e:
            flash("Erro ao enviar o e-mail de verificação. Verifique se o e-mail é válido.", "danger")
            print(f"Erro ao enviar e-mail (Flask-Mail): {e}")

    return render_template("usuarios/cadastrar.html", form=form)

@usuarios.route("/verificar-codigo", methods=["GET", "POST"])
def verificar_codigo():
    if "temp_user" not in session or "verification_code" not in session:
        flash("Nenhum cadastro em andamento. Cadastre-se primeiro.", "warning")
        return redirect(url_for("usuarios.cadastrar"))

    if request.method == "POST":
        # Junta os 6 campos individuais de digito enviados pelo formulário HTML
        digit1 = request.form.get("digit1", "")
        digit2 = request.form.get("digit2", "")
        digit3 = request.form.get("digit3", "")
        digit4 = request.form.get("digit4", "")
        digit5 = request.form.get("digit5", "")
        digit6 = request.form.get("digit6", "")

        codigo_digitado = f"{digit1}{digit2}{digit3}{digit4}{digit5}{digit6}".strip()
        codigo_correto = session.get("verification_code")

        if codigo_digitado == codigo_correto:
            temp_user = session.get("temp_user")
            email = temp_user["email"]
            senha = temp_user["senha"]
            nome = temp_user["nome"]
            siap = temp_user["siap"]

            firebase_user = None 

            try:
                # 1. Cadastrar oficialmente no Firebase
                auth = get_firebase_auth()
                firebase_user = auth.create_user_with_email_and_password(email, senha)

                # 2. Registrar na base de dados local
                membro = Membro.query.filter_by(email=email).first()
                if not membro and siap:
                    membro = Membro.query.filter_by(siap=siap).first()

                if membro and siap and not membro.siap:
                    membro.siap = siap

                usuario = Usuario(
                    nome=nome,
                    email=email,
                    perfil="professor",
                    membro_id=membro.id if membro else None,
                    ativo=True
                )
                usuario.set_password(senha)

                db.session.add(usuario)
                db.session.commit()

                # Limpar a sessão temporária
                session.pop("temp_user", None)
                session.pop("verification_code", None)

                # Fazer o login automático
                login_user(usuario)

                flash("E-mail verificado com sucesso! Bem-vindo ao sistema.", "success")
                return redirect(url_for("dashboard"))

            except Exception as e:
                # 1. Desfaz qualquer tentativa pela metade no banco local
                db.session.rollback() 
                
                # 2. SE o Firebase chegou a criar o usuário, vamos apagá-lo!
                if firebase_user:
                    try:
                        auth.delete_user_account(firebase_user['idToken'])
                        print("Rollback: Usuário apagado do Firebase após erro no banco local.")
                    except Exception as delete_error:
                        print(f"Erro ao tentar apagar usuário no Firebase: {delete_error}")

                flash("Erro ao salvar cadastro. Tente novamente.", "danger")
                print(f"Erro do Sistema: {e}")
                return redirect(url_for("usuarios.cadastrar"))
        else:
            flash("Código incorreto. Por favor, verifique e digite novamente.", "danger")

    # A linha que faltava / estava com os espaços errados:
    return render_template("usuarios/verificar_codigo.html")

@usuarios.route("/reenviar-codigo")
def reenviar_codigo():
    if "temp_user" not in session:
        flash("Nenhum cadastro em andamento.", "warning")
        return redirect(url_for("usuarios.cadastrar"))

    temp_user = session.get("temp_user")
    novo_codigo = "".join(str(random.randint(0, 9)) for _ in range(6))
    session["verification_code"] = novo_codigo

    try:
        msg = Message(
            "Novo Código de Verificação - SIRG",
            recipients=[temp_user["email"]]
        )
        msg.body = f"Seu novo código de validação para o SIRG é: {novo_codigo}"
        mail.send(msg)
        flash("Um novo código foi enviado para o seu e-mail.", "info")
    except Exception as e:
        flash("Erro ao enviar o e-mail. Tente novamente.", "danger")
        print(f"Erro reenvio: {e}")

    return redirect(url_for("usuarios.verificar_codigo"))    

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
            perfil='professor', 
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