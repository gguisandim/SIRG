from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario, Membro
from app.forms import LoginForm, CadastroUsuarioForm


usuarios = Blueprint("usuarios", __name__, url_prefix="/usuarios")


PERFIS_ADMINISTRATIVOS = ["coordenador", "secretaria", "bolsista"]


@usuarios.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.perfil == "professor":
            return redirect(url_for("justificativas.minhas_faltas"))

        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data.strip().lower()).first()

        if usuario and usuario.check_password(form.senha.data) and usuario.ativo:
            login_user(usuario)
            flash("Login realizado com sucesso.", "success")

            if usuario.perfil == "professor":
                return redirect(url_for("justificativas.minhas_faltas"))

            return redirect(url_for("dashboard"))

        flash("E-mail ou senha inválidos.", "danger")

    return render_template("usuarios/login.html", form=form)


@usuarios.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("usuarios.login"))


@usuarios.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    form = CadastroUsuarioForm()

    if form.validate_on_submit():
        usuario_existente = Usuario.query.filter_by(email=form.email.data.strip().lower()).first()

        if usuario_existente:
            flash("Já existe um usuário com esse e-mail.", "warning")
            return render_template("usuarios/cadastrar.html", form=form)

        membro = Membro.query.filter_by(email=form.email.data.strip().lower()).first()

        usuario = Usuario(
            nome=form.nome.data,
            email=form.email.data.strip().lower(),
            perfil="professor",
            membro_id=membro.id if membro else None
        )

        usuario.set_password(form.senha.data)

        db.session.add(usuario)
        db.session.commit()

        flash("Usuário cadastrado com sucesso. Faça login para continuar.", "success")
        return redirect(url_for("usuarios.login"))

    return render_template("usuarios/cadastrar.html", form=form)

@usuarios.route("/membro/<int:membro_id>/resetar-senha", methods=["POST"])
@login_required
def resetar_senha_membro(membro_id):
    if current_user.perfil not in ["coordenador", "secretaria"]:
        flash("Você não tem permissão para resetar senhas.", "danger")
        return redirect(url_for("membros.listar_membros"))

    membro = Membro.query.get_or_404(membro_id)
    usuario = Usuario.query.filter_by(email=membro.email).first()

    if not usuario:
        flash("Este membro ainda não possui usuário vinculado.", "warning")
        return redirect(url_for("membros.listar_membros"))

    usuario.set_password("123456")
    db.session.commit()

    flash(f"Senha de {usuario.nome} redefinida para 123456.", "success")
    return redirect(url_for("membros.listar_membros"))