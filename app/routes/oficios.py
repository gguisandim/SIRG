# app/routes/oficios.py
from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime
from app import db
from app.models import Oficio
from flask_login import login_required
from app.utils.permissoes import administrativo_required
from flask import Blueprint, render_template, request, redirect, url_for, jsonify

oficios = Blueprint('oficios', __name__)


@oficios.route('/')
@login_required
@administrativo_required
def listar_oficios():
    return redirect(url_for('oficios.listar_oficios_internos'))


@oficios.route('/visualizar')
@login_required
@administrativo_required
def visualizar_documentos():
    ano = request.args.get('ano', datetime.now().year, type=int)
    status = request.args.get('status', '').strip()
    busca = request.args.get('busca', '').strip()

    query = Oficio.query.filter_by(ano=ano, tipo='interno')

    if status:
        query = query.filter(Oficio.status == status)

    if busca:
        query = query.filter(
            (Oficio.numero.ilike(f'%{busca}%')) |
            (Oficio.titulo.ilike(f'%{busca}%')) |
            (Oficio.destinatario.ilike(f'%{busca}%')) |
            (Oficio.descricao.ilike(f'%{busca}%'))
        )

    documentos = query.order_by(Oficio.numero.asc()).all()

    total_oficios = Oficio.query.filter_by(tipo='interno', ano=ano).count()
    total_usados = Oficio.query.filter_by(tipo='interno', ano=ano, status='usado').count()
    total_cancelados = Oficio.query.filter_by(tipo='interno', ano=ano, status='cancelado').count()

    return render_template(
        'oficios/visualizar.html',
        documentos=documentos,
        ano=ano,
        status=status,
        busca=busca,
        total_oficios=total_oficios,
        total_usados=total_usados,
        total_cancelados=total_cancelados
    )


@oficios.route('/internos')
@login_required
@administrativo_required
def listar_oficios_internos():
    return redirect(url_for('oficios.visualizar_documentos'))


@oficios.route('/interno/novo', methods=['GET', 'POST'])
@login_required
@administrativo_required
def criar_oficio_interno():
    ano_atual = datetime.now().year

    if request.method == 'POST':
        numero = request.form['numero'].strip()
        ano = int(request.form.get('ano', ano_atual))
        titulo = request.form['titulo'].strip()
        descricao = request.form.get('descricao')
        destinatario = request.form.get('destinatario')
        template_sugerido = request.form.get('template_sugerido')
        corpo = request.form.get('corpo')

        documento_existente = Oficio.query.filter_by(
            numero=numero,
            ano=ano,
            tipo='interno'
        ).first()

        if documento_existente:
            return render_template(
                'oficios/cadastrar_interno.html',
                erro=f'Já existe um ofício com o número {numero}/{ano}.',
                ano_atual=ano_atual,
                oficio=None
            )

        oficio = Oficio(
            numero=numero,
            ano=ano,
            tipo='interno',
            titulo=titulo,
            descricao=descricao,
            destinatario=destinatario,
            status='usado',
            template_sugerido=template_sugerido,
            corpo=corpo
        )

        db.session.add(oficio)
        db.session.commit()

        return redirect(url_for('oficios.visualizar_oficio', id=oficio.id))

    return render_template(
        'oficios/cadastrar_interno.html',
        ano_atual=ano_atual,
        oficio=None
    )


@oficios.route('/interno/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@administrativo_required
def editar_oficio_interno(id):
    oficio = Oficio.query.get_or_404(id)
    ano_atual = datetime.now().year

    if request.method == 'POST':
        numero = request.form['numero'].strip()
        ano = int(request.form.get('ano', ano_atual))

        documento_existente = Oficio.query.filter(
            Oficio.numero == numero,
            Oficio.ano == ano,
            Oficio.tipo == 'interno',
            Oficio.id != oficio.id
        ).first()

        if documento_existente:
            return render_template(
                'oficios/cadastrar_interno.html',
                erro=f'Já existe outro ofício com o número {numero}/{ano}.',
                ano_atual=ano_atual,
                oficio=oficio
            )

        oficio.numero = numero
        oficio.ano = ano
        oficio.titulo = request.form['titulo'].strip()
        oficio.descricao = request.form.get('descricao')
        oficio.destinatario = request.form.get('destinatario')
        oficio.template_sugerido = request.form.get('template_sugerido')
        oficio.corpo = request.form.get('corpo')

        db.session.commit()

        return redirect(url_for('oficios.visualizar_oficio', id=oficio.id))

    return render_template(
        'oficios/cadastrar_interno.html',
        ano_atual=ano_atual,
        oficio=oficio
    )


@oficios.route('/interno/<int:id>/visualizar')
@login_required
@administrativo_required
def visualizar_oficio(id):
    oficio = Oficio.query.get_or_404(id)

    return render_template(
        'oficios/visualizar_oficio.html',
        oficio=oficio
    )

@oficios.route('/interno/gerar-ia', methods=['POST'])
@login_required
@administrativo_required
def gerar_oficio_ia():
    dados = request.get_json() or {}

    numero = dados.get('numero', '').strip()
    ano = dados.get('ano', '').strip()
    titulo = dados.get('titulo', '').strip()
    destinatario = dados.get('destinatario', '').strip()
    descricao = dados.get('descricao', '').strip()
    corpo = dados.get('corpo', '').strip()

    if not titulo and not descricao and not corpo:
        return jsonify({
            'sucesso': False,
            'erro': 'Preencha ao menos o título, a descrição ou o corpo do ofício.'
        }), 400

    prompt = f"""
Você é um assistente administrativo do Programa de Pós-Graduação em Educação Básica - PPEB/UFPA.

Sua tarefa é redigir o corpo de um ofício interno institucional.

REGRAS:
- Escreva apenas o corpo do ofício.
- Não escreva cabeçalho.
- Não escreva número do ofício.
- Não escreva data.
- Não escreva assinatura.
- Não use Markdown.
- Não use asteriscos.
- Não invente nomes, datas, cargos ou informações.
- Use linguagem formal, objetiva e institucional.
- Se já houver texto no campo "corpo atual", apenas melhore e reescreva mantendo a intenção original.

DADOS DO OFÍCIO:
Número: {numero}
Ano: {ano}
Título: {titulo}
Destinatário: {destinatario}
Descrição/contexto: {descricao}

CORPO ATUAL:
{corpo}
"""

    try:
        from app.services.ia.groq_client import GroqClient

        cliente = GroqClient()
        texto = cliente.gerar_texto(prompt)

        return jsonify({
            'sucesso': True,
            'texto': texto.strip()
        })

    except Exception as e:
        return jsonify({
            'sucesso': False,
            'erro': str(e)
        }), 500