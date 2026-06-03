# app/routes/bancas.py
from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import or_
from datetime import datetime
from app import db
from app.models import Banca
from flask_login import login_required
from app.utils.permissoes import administrativo_required

bancas = Blueprint('bancas', __name__)


def converter_horario(valor):
    valor = valor.strip().upper()

    if "H" in valor:
        partes = valor.split("H")
        hora = partes[0].zfill(2)
        minuto = partes[1] if len(partes) > 1 and partes[1] else "00"
        valor = f"{hora}:{minuto.zfill(2)}"

    return datetime.strptime(valor, "%H:%M").time()


@bancas.route('/')
@login_required
@administrativo_required
def visualizar_banca():
    busca = request.args.get('busca', '').strip()
    data_inicio = request.args.get('data_inicio', '').strip()
    data_fim = request.args.get('data_fim', '').strip()
    sala = request.args.get('sala', '').strip()
    nivel = request.args.get('nivel', '').strip()
    drive_status = request.args.get('drive_status', '').strip()
    site_status = request.args.get('site_status', '').strip()
    convite = request.args.get('convite', '').strip()

    query = Banca.query

    if busca:
        query = query.filter(
            or_(
                Banca.responsavel_banca.ilike(f'%{busca}%'),
                Banca.orientador.ilike(f'%{busca}%')
            )
        )

    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(Banca.data >= data_inicio_obj)

    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(Banca.data <= data_fim_obj)

    if sala:
        query = query.filter(Banca.sala == sala)

    if nivel:
        query = query.filter(Banca.nivel == nivel)

    if drive_status:
        query = query.filter(Banca.drive_status == drive_status)

    if site_status:
        query = query.filter(Banca.site_status == site_status)

    if convite == 'enviado':
        query = query.filter(Banca.convite_enviado == True)

    if convite == 'pendente':
        query = query.filter(Banca.convite_enviado == False)

    todas_bancas = query.order_by(Banca.data.asc(), Banca.horario.asc()).all()

    return render_template(
        'bancas/listarbancas.html',
        bancas=todas_bancas
    )


@bancas.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_banca():
    if request.method == 'POST':
        data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
        horario = converter_horario(request.form['horario'])

        banca = Banca(
            data=data,
            horario=horario,
            responsavel_banca=request.form['responsavel_banca'],
            orientador=request.form['orientador'],
            sala=request.form.get('sala'),
            nivel=request.form['nivel'],
            drive_status=request.form.get('drive_status', 'pendente'),
            site_status=request.form.get('site_status', 'pendente'),
            erro_sigaa=request.form.get('erro_sigaa'),
            convite_enviado=False
        )

        db.session.add(banca)
        db.session.commit()

        return redirect(url_for('bancas.visualizar_banca'))

    return render_template('bancas/cadastrarbancas.html')


@bancas.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_banca(id):
    banca = Banca.query.get_or_404(id)

    if request.method == 'POST':
        banca.data = datetime.strptime(request.form['data'], '%Y-%m-%d').date()
        banca.horario = converter_horario(request.form['horario'])
        banca.responsavel_banca = request.form['responsavel_banca']
        banca.orientador = request.form['orientador']
        banca.sala = request.form.get('sala')
        banca.nivel = request.form['nivel']
        banca.drive_status = request.form.get('drive_status', 'pendente')
        banca.site_status = request.form.get('site_status', 'pendente')
        banca.erro_sigaa = request.form.get('erro_sigaa')
        banca.convite_enviado = True if request.form.get('convite_enviado') == 'sim' else False

        db.session.commit()

        return redirect(url_for('bancas.visualizar_banca'))

    return render_template('bancas/editarbancas.html', banca=banca)


@bancas.route('/convite-enviado/<int:id>', methods=['POST'])
def marcar_convite_enviado(id):
    banca = Banca.query.get_or_404(id)
    banca.convite_enviado = True
    db.session.commit()

    return redirect(url_for('bancas.visualizar_banca'))


@bancas.route('/convite-pendente/<int:id>', methods=['POST'])
def marcar_convite_pendente(id):
    banca = Banca.query.get_or_404(id)
    banca.convite_enviado = False
    db.session.commit()

    return redirect(url_for('bancas.visualizar_banca'))


@bancas.route('/excluir/<int:id>', methods=['POST'])
def excluir_banca(id):
    banca = Banca.query.get_or_404(id)

    db.session.delete(banca)
    db.session.commit()

    return redirect(url_for('bancas.visualizar_banca'))

@bancas.route('/drive-ok/<int:id>', methods=['POST'])
def marcar_drive_ok(id):
    banca = Banca.query.get_or_404(id)

    banca.drive_status = 'OK'
    db.session.commit()

    return redirect(request.referrer or url_for('bancas.visualizar_banca'))


@bancas.route('/drive-pendente/<int:id>', methods=['POST'])
def marcar_drive_pendente(id):
    banca = Banca.query.get_or_404(id)

    banca.drive_status = 'pendente'
    db.session.commit()

    return redirect(request.referrer or url_for('bancas.visualizar_banca'))


@bancas.route('/site-ok/<int:id>', methods=['POST'])
def marcar_site_ok(id):
    banca = Banca.query.get_or_404(id)

    banca.site_status = 'OK'
    db.session.commit()

    return redirect(request.referrer or url_for('bancas.visualizar_banca'))


@bancas.route('/site-pendente/<int:id>', methods=['POST'])
def marcar_site_pendente(id):
    banca = Banca.query.get_or_404(id)

    banca.site_status = 'pendente'
    db.session.commit()

    return redirect(request.referrer or url_for('bancas.visualizar_banca'))