# app/services/pauta_reuniao.py
from datetime import datetime
from pathlib import Path

from flask import render_template, current_app, request


MESES_PT = {
    1: 'janeiro',
    2: 'fevereiro',
    3: 'março',
    4: 'abril',
    5: 'maio',
    6: 'junho',
    7: 'julho',
    8: 'agosto',
    9: 'setembro',
    10: 'outubro',
    11: 'novembro',
    12: 'dezembro'
}


def data_por_extenso(data):
    return f"{data.day} de {MESES_PT[data.month]} de {data.year}"


def configurar_weasyprint_windows():
    import os

    if os.name == 'nt':
        caminho_dll = r'C:\msys64\ucrt64\bin'

        if os.path.exists(caminho_dll):
            os.environ['WEASYPRINT_DLL_DIRECTORIES'] = caminho_dll
            os.add_dll_directory(caminho_dll)


def gerar_pdf_pauta_reuniao(reuniao):
    configurar_weasyprint_windows()

    from weasyprint import HTML

    pasta_saida = Path(current_app.root_path) / 'static' / 'documentos' / 'pautas'
    pasta_saida.mkdir(parents=True, exist_ok=True)

    agora = datetime.now()

    nome_arquivo = f"pauta_reuniao_{reuniao.id}_{agora.strftime('%Y%m%d%H%M%S')}.pdf"
    caminho_pdf = pasta_saida / nome_arquivo

    html = render_template(
        'documentos/pauta_reuniao.html',
        reuniao=reuniao,
        gerado_em=agora,
        ano=agora.year,
        mes=agora.month,
        data_emissao_extenso=data_por_extenso(agora.date()),
        data_reuniao_extenso=data_por_extenso(reuniao.data)
    )

    HTML(
        string=html,
        base_url=request.url_root
    ).write_pdf(str(caminho_pdf))

    return caminho_pdf