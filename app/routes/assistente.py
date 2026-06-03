from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.models import Reuniao, Membro
from app.services.ia.groq_client import GroqClient


assistente = Blueprint("assistente", __name__)

groq_client = GroqClient()


def usuario_eh_admin():
    return (
        current_user.is_authenticated
        and current_user.perfil in ["admin", "coordenador", "secretaria"]
    )


@assistente.route("/assistente/perguntar", methods=["POST"])
@login_required
def perguntar_assistente():
    if not usuario_eh_admin():
        return jsonify({"erro": "Acesso não autorizado."}), 403

    dados = request.get_json(silent=True) or {}
    pergunta = dados.get("pergunta", "").strip()

    if not pergunta:
        return jsonify({"erro": "Pergunta não informada."}), 400

    contexto = buscar_contexto_no_banco(pergunta)

    prompt = f"""
Você é um assistente interno do sistema PPEB.

Responda de forma clara, objetiva e somente com base nos dados abaixo.

DADOS DO SISTEMA:
{contexto}

PERGUNTA:
{pergunta}
"""

    resposta = groq_client.gerar_texto(prompt)

    return jsonify({"resposta": resposta})


def buscar_contexto_no_banco(pergunta):
    pergunta = pergunta.lower()

    if "reunião" in pergunta or "reuniao" in pergunta or "pauta" in pergunta:
        reunioes = Reuniao.query.order_by(Reuniao.data.desc()).limit(5).all()

        if not reunioes:
            return "Nenhuma reunião cadastrada no sistema."

        return "\n".join([
            f"Reunião: {r.titulo}; Data: {r.data}; Tipo: {r.tipo}; Pauta: {r.pauta or 'Sem pauta cadastrada'}"
            for r in reunioes
        ])

    if "membro" in pergunta or "professor" in pergunta or "professores" in pergunta:
        membros = Membro.query.filter_by(ativo=True).order_by(Membro.nome.asc()).all()

        if not membros:
            return "Nenhum membro ativo cadastrado no sistema."

        return "\n".join([
            f"Membro: {m.nome}; Email: {m.email}; Tipo: {m.tipo}"
            for m in membros
        ])

    return "Nenhuma informação relevante encontrada no banco para essa pergunta."