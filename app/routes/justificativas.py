from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Frequencia, Reuniao
from werkzeug.utils import secure_filename
import os


justificativas = Blueprint(
    "justificativas",
    __name__,
    url_prefix="/justificativas"
)


EXTENSOES_PERMITIDAS = {"pdf", "jpg", "jpeg", "png", "doc", "docx"}


def arquivo_permitido(nome_arquivo):
    return (
        "." in nome_arquivo
        and nome_arquivo.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS
    )


@justificativas.route("/minhas-faltas")
@login_required
def minhas_faltas():
    if not current_user.membro_id:
        faltas = []
    else:
        faltas = Frequencia.query.join(Reuniao).filter(
            Frequencia.membro_id == current_user.membro_id,
            Frequencia.removido == False
        ).order_by(
            Reuniao.data.desc(),
            Reuniao.horario.desc()
        ).all()

    return render_template(
        "justificativas/minhas_faltas.html",
        faltas=faltas
    )


@justificativas.route("/minhas-faltas/pdf")
@login_required
def relatorio_minhas_frequencias_pdf():
    if not current_user.membro_id:
        frequencias = []
    else:
        frequencias = Frequencia.query.join(Reuniao).filter(
            Frequencia.membro_id == current_user.membro_id,
            Frequencia.removido == False
        ).order_by(
            Reuniao.data.asc(),
            Reuniao.horario.asc()
        ).all()

    total_reunioes = len(frequencias)

    total_presencas = sum(
        1 for f in frequencias
        if f.status == "presente"
    )

    total_ausencias = sum(
        1 for f in frequencias
        if f.status in ["ausente", "falta"]
    )

    total_justificadas = sum(
        1 for f in frequencias
        if f.status in ["justificado", "justificada"]
    )

    frequencias_justificadas = [
        f for f in frequencias
        if f.status in ["justificado", "justificada"] or f.justificativa
    ]

    return render_template(
        "justificativas/relatorio_frequencias_pdf.html",
        frequencias=frequencias,
        frequencias_justificadas=frequencias_justificadas,
        total_reunioes=total_reunioes,
        total_presencas=total_presencas,
        total_ausencias=total_ausencias,
        total_justificadas=total_justificadas
    )


@justificativas.route("/justificar/<int:frequencia_id>", methods=["GET", "POST"])
@login_required
def justificar(frequencia_id):
    if not current_user.membro_id:
        flash("Seu usuário não está vinculado a um membro/professor cadastrado.", "warning")
        return redirect(url_for("dashboard"))

    frequencia = Frequencia.query.get_or_404(frequencia_id)

    if frequencia.membro_id != current_user.membro_id:
        flash("Você não pode justificar a falta de outro membro.", "danger")
        return redirect(url_for("justificativas.minhas_faltas"))

    reuniao = frequencia.reuniao

    if reuniao and reuniao.justificativas_encerradas:
        flash("As justificativas desta reunião foram encerradas.", "warning")
        return redirect(url_for("justificativas.minhas_faltas"))

    if request.method == "POST":
        justificativa = request.form.get("justificativa")
        arquivo = request.files.get("anexo")

        if not justificativa or not justificativa.strip():
            flash("Informe uma justificativa antes de enviar.", "warning")
            return render_template("justificativas/justificar.html", frequencia=frequencia)

        frequencia.justificativa = justificativa.strip()
        frequencia.status = "justificada"

        if arquivo and arquivo.filename:
            if not arquivo_permitido(arquivo.filename):
                flash("Formato de arquivo não permitido. Use PDF, JPG, PNG, DOC ou DOCX.", "warning")
                return render_template("justificativas/justificar.html", frequencia=frequencia)

            nome_seguro = secure_filename(arquivo.filename)

            pasta_upload = os.path.join(
                current_app.root_path,
                "static",
                "uploads",
                "justificativas"
            )

            os.makedirs(pasta_upload, exist_ok=True)

            nome_arquivo = f"frequencia_{frequencia.id}_{nome_seguro}"
            caminho_completo = os.path.join(pasta_upload, nome_arquivo)

            arquivo.save(caminho_completo)

            frequencia.anexo_justificativa = f"uploads/justificativas/{nome_arquivo}"

        db.session.commit()

        flash("Justificativa enviada com sucesso.", "success")
        return redirect(url_for("justificativas.minhas_faltas"))

    return render_template("justificativas/justificar.html", frequencia=frequencia)