from flask import Blueprint, request, jsonify

from app.services.ia.groq_client import GroqClient
from app.services.ia.prompts import (
    carregar_modelo_pauta_colegiado,
    prompt_pauta_colegiado_com_modelo,
    carregar_modelo_ata_colegiado,
    prompt_ata_colegiado_com_modelo,
    normalizar_pauta_bruta
)


ia = Blueprint("ia", __name__, url_prefix="/ia")


@ia.route("/teste", methods=["GET"])
def teste_ia():
    return jsonify({
        "sucesso": True,
        "mensagem": "Blueprint de IA funcionando."
    })


@ia.route("/gerar-pauta-colegiado", methods=["POST"])
def gerar_pauta_colegiado():
    dados = request.get_json(silent=True) or {}

    titulo = dados.get("titulo", "")
    data_reuniao = dados.get("data", "")
    horario = dados.get("horario", "")
    local = dados.get("local", "")
    tipo = dados.get("tipo", "")
    pauta_atual = dados.get("pauta", "")

    modelo_pauta = carregar_modelo_pauta_colegiado()
    pauta_normalizada = normalizar_pauta_bruta(pauta_atual)

    prompt = prompt_pauta_colegiado_com_modelo(
        titulo=titulo,
        data_reuniao=data_reuniao,
        horario=horario,
        local=local,
        tipo=tipo,
        pauta_bruta=pauta_normalizada,
        modelo_pauta=modelo_pauta
    )

    try:
        groq = GroqClient()
        texto = groq.gerar_texto(prompt)

        return jsonify({
            "sucesso": True,
            "tipo": "pauta_colegiado",
            "texto": texto
        })

    except Exception as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 500


@ia.route("/gerar-ata-colegiado", methods=["POST"])
def gerar_ata_colegiado():
    dados = request.get_json(silent=True) or {}

    titulo = dados.get("titulo", "")
    data_reuniao = dados.get("data", "")
    horario = dados.get("horario", "")
    local = dados.get("local", "")
    tipo = dados.get("tipo", "")
    pauta = dados.get("pauta", "")
    presentes = dados.get("presentes", "")
    justificativas = dados.get("justificativas", "")
    anotacoes = dados.get("anotacoes", "")

    modelo_ata = carregar_modelo_ata_colegiado()
    pauta_normalizada = normalizar_pauta_bruta(pauta)

    prompt = prompt_ata_colegiado_com_modelo(
        titulo=titulo,
        data_reuniao=data_reuniao,
        horario=horario,
        local=local,
        tipo=tipo,
        pauta=pauta_normalizada,
        presentes=presentes,
        justificativas=justificativas,
        anotacoes=anotacoes,
        modelo_ata=modelo_ata
    )

    try:
        groq = GroqClient()
        texto = groq.gerar_texto(prompt)

        return jsonify({
            "sucesso": True,
            "tipo": "ata_colegiado",
            "texto": texto
        })

    except Exception as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 500