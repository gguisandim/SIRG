# app/routes/relatorios.py
from flask import Blueprint, render_template, request, make_response
from datetime import datetime, date
from flask_login import login_required

from app.utils.permissoes import administrativo_required

from app.models import (
    Membro,
    Reuniao,
    Frequencia,
    Banca,
    Oficio
)

relatorios = Blueprint('relatorios', __name__)


def montar_dados_relatorio(ano, mes):
    if mes and 1 <= mes <= 12:
        data_inicio = date(ano, mes, 1)

        if mes == 12:
            data_fim = date(ano + 1, 1, 1)
        else:
            data_fim = date(ano, mes + 1, 1)
    else:
        data_inicio = date(ano, 1, 1)
        data_fim = date(ano + 1, 1, 1)

    total_membros = Membro.query.count()

    total_professores = Membro.query.filter_by(
        tipo='professor',
        ativo=True
    ).count()

    total_discentes = Membro.query.filter_by(
        tipo='discente',
        ativo=True
    ).count()

    professores = Membro.query.filter(
        Membro.ativo == True,
        Membro.tipo.in_(["professor", "tecnico"])
    ).order_by(Membro.nome.asc()).all()

    reunioes = Reuniao.query.filter(
        Reuniao.data >= data_inicio,
        Reuniao.data < data_fim
    ).order_by(
        Reuniao.data.asc(),
        Reuniao.horario.asc()
    ).all()

    total_reunioes = len(reunioes)

    frequencias = Frequencia.query.join(Reuniao).filter(
        Reuniao.data >= data_inicio,
        Reuniao.data < data_fim,
        Frequencia.removido == False
    ).all()

    total_presentes = sum(1 for f in frequencias if f.status == 'presente')
    total_ausentes = sum(1 for f in frequencias if f.status == 'ausente')
    total_justificados = sum(1 for f in frequencias if f.status == 'justificado')

    justificativas = [
        f for f in frequencias
        if f.justificativa
    ]

    resumo_professores = []

    for professor in professores:
        frequencias_professor = [
            f for f in frequencias
            if f.membro_id == professor.id
        ]

        presentes = sum(1 for f in frequencias_professor if f.status == 'presente')
        ausentes = sum(1 for f in frequencias_professor if f.status == 'ausente')
        justificados = sum(1 for f in frequencias_professor if f.status == 'justificado')
        total_registros = len(frequencias_professor)

        percentual_presenca = 0

        if total_registros > 0:
            percentual_presenca = round((presentes / total_registros) * 100, 2)

        resumo_professores.append({
            'professor': professor,
            'presentes': presentes,
            'ausentes': ausentes,
            'justificados': justificados,
            'total_registros': total_registros,
            'percentual_presenca': percentual_presenca
        })

    resumo_reunioes = []

    for reuniao in reunioes:
        frequencias_reuniao = [
            f for f in frequencias
            if f.reuniao_id == reuniao.id
        ]

        resumo_reunioes.append({
            'reuniao': reuniao,
            'presentes': sum(1 for f in frequencias_reuniao if f.status == 'presente'),
            'ausentes': sum(1 for f in frequencias_reuniao if f.status == 'ausente'),
            'justificados': sum(1 for f in frequencias_reuniao if f.status == 'justificado'),
            'total': len(frequencias_reuniao)
        })

    bancas = Banca.query.filter(
        Banca.data >= data_inicio,
        Banca.data < data_fim
    ).order_by(
        Banca.data.asc(),
        Banca.horario.asc()
    ).all()

    total_bancas = len(bancas)

    bancas_com_convite_pendente = [
        b for b in bancas
        if not b.convite_enviado
    ]

    bancas_com_pendencias = [
        b for b in bancas
        if b.drive_status != 'OK'
        or b.site_status != 'OK'
        or b.erro_sigaa
        or not b.convite_enviado
    ]

    oficios_internos = Oficio.query.filter_by(
        tipo='interno',
        ano=ano
    ).all()

    editais = Oficio.query.filter_by(
        tipo='edital',
        ano=ano
    ).all()

    total_oficios_internos = len(oficios_internos)
    total_editais = len(editais)

    oficios_cancelados = [
        o for o in oficios_internos
        if o.status == 'cancelado'
    ]

    editais_cancelados = [
        e for e in editais
        if e.status == 'cancelado'
    ]

    grafico_frequencia_labels = [
        'Presentes',
        'Ausentes',
        'Justificados'
    ]

    grafico_frequencia_valores = [
        total_presentes,
        total_ausentes,
        total_justificados
    ]

    meses_labels = [
        'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
    ]

    reunioes_por_mes = [0] * 12

    for reuniao in reunioes:
        mes_reuniao = reuniao.data.month
        reunioes_por_mes[mes_reuniao - 1] += 1

    niveis_labels = [
        'Defesa-Mestrado',
        'Defesa-Doutorado',
        'Qualificação-Mestrado',
        'Qualificação-Doutorado'
    ]

    bancas_por_nivel = []

    for nivel in niveis_labels:
        total = sum(1 for banca in bancas if banca.nivel == nivel)
        bancas_por_nivel.append(total)

    grafico_documentos_labels = [
        'Ofícios Internos',
        'Editais'
    ]

    grafico_documentos_valores = [
        total_oficios_internos,
        total_editais
    ]

    return {
        'ano': ano,
        'mes': mes,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'gerado_em': datetime.now(),

        'total_membros': total_membros,
        'total_professores': total_professores,
        'total_discentes': total_discentes,

        'total_reunioes': total_reunioes,
        'reunioes': reunioes,
        'resumo_reunioes': resumo_reunioes,

        'total_presentes': total_presentes,
        'total_ausentes': total_ausentes,
        'total_justificados': total_justificados,
        'resumo_professores': resumo_professores,
        'justificativas': justificativas,

        'total_bancas': total_bancas,
        'bancas': bancas,
        'bancas_com_convite_pendente': bancas_com_convite_pendente,
        'bancas_com_pendencias': bancas_com_pendencias,

        'total_oficios_internos': total_oficios_internos,
        'total_editais': total_editais,
        'oficios_internos': oficios_internos,
        'editais': editais,
        'oficios_cancelados': oficios_cancelados,
        'editais_cancelados': editais_cancelados,

        'grafico_frequencia_labels': grafico_frequencia_labels,
        'grafico_frequencia_valores': grafico_frequencia_valores,

        'meses_labels': meses_labels,
        'reunioes_por_mes': reunioes_por_mes,

        'niveis_labels': niveis_labels,
        'bancas_por_nivel': bancas_por_nivel,

        'grafico_documentos_labels': grafico_documentos_labels,
        'grafico_documentos_valores': grafico_documentos_valores
    }


@relatorios.route('/')
@login_required
@administrativo_required
def gerar_relatorio():
    ano = request.args.get('ano', datetime.now().year, type=int)
    mes = request.args.get('mes', 0, type=int)

    dados = montar_dados_relatorio(ano, mes)

    return render_template(
        'relatorios/gerar.html',
        **dados
    )


@relatorios.route('/pdf')
def gerar_pdf():
    import os

    if os.name == 'nt':
        os.environ['WEASYPRINT_DLL_DIRECTORIES'] = r'C:\msys64\ucrt64\bin'

        if os.path.exists(r'C:\msys64\ucrt64\bin'):
            os.add_dll_directory(r'C:\msys64\ucrt64\bin')

    from weasyprint import HTML

    ano = request.args.get('ano', datetime.now().year, type=int)
    mes = request.args.get('mes', 0, type=int)
    tipo = request.args.get('tipo', 'completo')

    dados = montar_dados_relatorio(ano, mes)
    dados['tipo_relatorio'] = tipo

    templates = {
        'completo': 'relatorios/pdf/relatorio_completo.html',
        'bancas': 'relatorios/pdf/relatorio_bancas.html',
        'reunioes': 'relatorios/pdf/relatorio_reunioes.html',
        'frequencia': 'relatorios/pdf/relatorio_frequencia.html',
        'documentos': 'relatorios/pdf/relatorio_documentos.html',
    }

    template = templates.get(tipo, templates['completo'])

    html = render_template(template, **dados)

    pdf = HTML(
        string=html,
        base_url=request.url_root
    ).write_pdf()

    nome_arquivo = f"relatorio_{tipo}_{ano}"

    if mes:
        nome_arquivo += f"_{mes:02d}"

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={nome_arquivo}.pdf'

    return response


@relatorios.route('/detalhado', methods=['GET', 'POST'])
def relatorio_detalhado():
    return render_template('relatorios/detalhado.html')