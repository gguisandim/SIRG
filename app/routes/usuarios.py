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

        # 1. Gerar o código de verificação de 6 dígitos
        codigo_verificacao = "".join(str(random.randint(0,9)) for _ in range(6))

        # 2. Guardar na sessão temporária
        session["temp_user"] = {
            "nome": form.nome.data,
            "email": email, 
            "senha": senha,
            "siap": siap
        }
        session["verification_code"] = codigo_verificacao
        
        # 3. Enviar e-mail formatado em HTML
        try:
            msg = Message(
                "Código de Verificação - SIRG",
                recipients=[email]
            )
            # Texto simples (caso o leitor de e-mail do usuário não suporte HTML)
            msg.body = f"Olá, {form.nome.data}!\n\nSeu código de validação para concluir o seu cadastro no SIRG é: {codigo_verificacao}"
            
            # Template HTML Profissional com CSS inline
            msg.html = f"""
            <div style="font-family: 'Sora', Arial, sans-serif; max-width: 550px; margin: 30px auto; padding: 40px 30px; border: 1.5px solid #e2e8f0; border-radius: 16px; background-color: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
                <div style="text-align: center; margin-bottom: 25px;">
                    <h2 style="color: #1d4ed8; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.02em;">Sistema SIRG</h2>
                    <p style="font-size: 11px; color: #64748b; margin: 6px 0 0; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Confirmação de E-mail</p>
                </div>
                
                <div style="height: 1.5px; background-color: #f1f5f9; margin-bottom: 30px;"></div>
                
                <p style="font-size: 16px; color: #1e293b; line-height: 1.6; margin-bottom: 16px; font-weight: 500;">Olá, {form.nome.data}!</p>
                
                <p style="font-size: 14px; color: #475569; line-height: 1.6; margin-bottom: 16px;">
                    Recebemos uma solicitação de cadastro para o seu e-mail no <strong>Sistema Integrado de Registros e Gestão Acadêmica (SIRG)</strong>.
                </p>
                
                <p style="font-size: 14px; color: #475569; line-height: 1.6; margin-bottom: 30px;">
                    Para concluir a validação de segurança e liberar o seu acesso, utilize o código temporário abaixo:
                </p>
                
                <div style="text-align: center; margin: 30px 0; padding: 24px; background-color: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 12px;">
                    <span style="font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #1d4ed8; font-family: 'Courier New', monospace; text-shadow: 0 1px 2px rgba(0,0,0,0.05);">{codigo_verificacao}</span>
                </div>
                
                <p style="font-size: 12px; color: #94a3b8; text-align: center; margin-top: 35px; line-height: 1.6;">
                    Este código é de uso único, temporário e pessoal.<br>
                    Se você não iniciou este cadastro no sistema, por favor desconsidere este e-mail.
                </p>
            </div>
            """
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
                auth = get_firebase_auth()
                firebase_user = auth.create_user_with_email_and_password(email, senha)

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

                session.pop("temp_user", None)
                session.pop("verification_code", None)

                login_user(usuario)

                flash("E-mail verificado com sucesso! Bem-vindo ao sistema.", "success")
                return redirect(url_for("dashboard"))

            except Exception as e:
                db.session.rollback() 
                
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

    return render_template("usuarios/verificar_codigo.html")

@usuarios.route("/reenviar-codigo")
def reenviar_codigo():
    if "temp_user" not in session:
        flash("Nenhum cadastro em andamento.", "warning")
        return redirect(url_for("usuarios.cadastrar"))

    temp_user = session.get("temp_user")
    nome = temp_user["nome"]
    email = temp_user["email"]
    
    novo_codigo = "".join(str(random.randint(0, 9)) for _ in range(6))
    session["verification_code"] = novo_codigo

    try:
        msg = Message(
            "Novo Código de Verificação - SIRG",
            recipients=[email]
        )
        msg.body = f"Seu novo código de validação para o SIRG é: {novo_codigo}"
        
        msg.html = f"""
        <div style="font-family: 'Sora', Arial, sans-serif; max-width: 550px; margin: 30px auto; padding: 40px 30px; border: 1.5px solid #e2e8f0; border-radius: 16px; background-color: #ffffff; box-shadow: 0 4px 12px rgba(0,0,0,0.03);">
            <div style="text-align: center; margin-bottom: 25px;">
                <h2 style="color: #1d4ed8; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.02em;">Sistema SIRG</h2>
                <p style="font-size: 11px; color: #64748b; margin: 6px 0 0; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Novo Código Solicitado</p>
            </div>
            
            <div style="height: 1.5px; background-color: #f1f5f9; margin-bottom: 30px;"></div>
            
            <p style="font-size: 16px; color: #1e293b; line-height: 1.6; margin-bottom: 16px; font-weight: 500;">Olá, {nome}!</p>
            
            <p style="font-size: 14px; color: #475569; line-height: 1.6; margin-bottom: 16px;">
                Você solicitou a geração de um novo código de verificação de acesso para o <strong>SIRG</strong>.
            </p>
            
            <p style="font-size: 14px; color: #475569; line-height: 1.6; margin-bottom: 30px;">
                Utilize o novo código gerado abaixo na tela do sistema:
            </p>
            
            <div style="text-align: center; margin: 30px 0; padding: 24px; background-color: #f8fafc; border: 1.5px dashed #cbd5e1; border-radius: 12px;">
                <span style="font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #1d4ed8; font-family: 'Courier New', monospace; text-shadow: 0 1px 2px rgba(0,0,0,0.05);">{novo_codigo}</span>
            </div>
            
            <p style="font-size: 12px; color: #94a3b8; text-align: center; margin-top: 35px; line-height: 1.6;">
                Este código é de uso único, temporário e pessoal.<br>
                Se você não solicitou este reenvio, por favor desconsidere este e-mail.
            </p>
        </div>
        """
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
            db.session.add(novo_membro)

        db.session.commit()
        
        login_user(usuario)
        flash('Sua conta foi criada automaticamente com o Google!', 'success')

    return redirect(url_for('home'))

@usuarios.route("/membro/<int:membro_id>/resetar-senha", methods=["POST"])
@login_required
def resetar_senha_membro(membro_id):
    flash("A redefinição de palavra-passe agora é gerida pelo Firebase.", "info")
    return redirect(url_for("membros.listar_membros"))