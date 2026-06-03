# app/routes/frequencias.py
from flask import Blueprint, render_template, request
from sqlalchemy import or_
from app.models import Frequencia, Membro, Reuniao
from flask_login import login_required
from app.utils.permissoes import administrativo_required

frequencias = Blueprint('frequencias', __name__)


@frequencias.route('/')
@login_required
@administrativo_required
def listar_frequencias():
    busca = request.args.get('busca', '').strip()
    membro_id = request.args.get('membro_id', '').strip()
    reuniao_id = request.args.get('reuniao_id', '').strip()
    status = request.args.get('status', '').strip()

    query = Frequencia.query.join(Membro).join(Reuniao)

    if busca:
        query = query.filter(
            or_(
                Membro.nome.ilike(f'%{busca}%'),
                Membro.email.ilike(f'%{busca}%'),
                Reuniao.titulo.ilike(f'%{busca}%')
            )
        )

    if membro_id:
        query = query.filter(Frequencia.membro_id == int(membro_id))

    if reuniao_id:
        query = query.filter(Frequencia.reuniao_id == int(reuniao_id))

    if status:
        query = query.filter(Frequencia.status == status)

    lista_frequencias = query.order_by(
        Reuniao.data.desc(),
        Reuniao.horario.desc(),
        Membro.nome.asc()
    ).all()

    professores = Membro.query.filter_by(tipo='professor', ativo=True).order_by(Membro.nome.asc()).all()
    reunioes = Reuniao.query.order_by(Reuniao.data.desc()).all()

    total_presentes = sum(1 for f in lista_frequencias if f.status == 'presente')
    total_ausentes = sum(1 for f in lista_frequencias if f.status == 'ausente')
    total_justificados = sum(1 for f in lista_frequencias if f.status == 'justificado')

    return render_template(
        'frequencias/listar.html',
        frequencias=lista_frequencias,
        professores=professores,
        reunioes=reunioes,
        total_presentes=total_presentes,
        total_ausentes=total_ausentes,
        total_justificados=total_justificados
    )