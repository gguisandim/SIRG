# app/routes/membros.py
from flask import Blueprint, render_template, redirect, url_for, request
from sqlalchemy import or_
from app import db
from app.models import Membro
from app.forms import CadastroMembroForm
from flask_login import login_required
from app.utils.permissoes import administrativo_required
import unicodedata
import re

membros = Blueprint('membros', __name__)


def normalizar_nome(nome):
    nome = str(nome).strip().upper()

    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(c for c in nome if not unicodedata.combining(c))

    nome = re.sub(r"\s+", " ", nome)

    return nome

@membros.route('/listar')
@login_required
@administrativo_required
def listar_membros():
    busca = request.args.get('busca', '').strip()
    tipo = request.args.get('tipo', '').strip()
    linha_de_pesquisa = request.args.get('linha_de_pesquisa', '').strip()
    nivel_discente = request.args.get('nivel_discente', '').strip()
    ordem = request.args.get('ordem', 'nome_asc').strip()

    query = Membro.query.filter_by(ativo=True)

    if busca:
        query = query.filter(
            or_(
                Membro.nome.ilike(f'%{busca}%'),
                Membro.email.ilike(f'%{busca}%'),
                Membro.siap.ilike(f'%{busca}%')
            )
        )

    if tipo:
        query = query.filter(Membro.tipo == tipo)

    if linha_de_pesquisa:
        query = query.filter(Membro.linha_de_pesquisa == linha_de_pesquisa)

    if nivel_discente:
        query = query.filter(Membro.nivel_discente == nivel_discente)

    if ordem == 'nome_desc':
        query = query.order_by(Membro.nome.desc())
    elif ordem == 'tipo':
        query = query.order_by(Membro.tipo.asc(), Membro.nome.asc())
    elif ordem == 'email':
        query = query.order_by(Membro.email.asc())
    else:
        query = query.order_by(Membro.nome.asc())

    lista_membros = query.all()

    return render_template('membros/listar.html', membros=lista_membros)

# Rota para excluir membro
@membros.route('/excluir/<int:id>', methods=['POST'])
@login_required
@administrativo_required
def excluir_membro(id):
    membro = Membro.query.get_or_404(id)

    membro.ativo = False
    db.session.commit()

    return redirect(url_for('membros.listar_membros'))
# Rota para cadastrar um novo membro
@membros.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar_membro():
    form = CadastroMembroForm()

    if form.validate_on_submit():
        tipo = form.tipo.data

        membro = Membro(
            nome=normalizar_nome(form.nome.data),
            email=form.email.data.strip().lower(),
            tipo=tipo,
            linha_de_pesquisa=form.linha_de_pesquisa.data if tipo == 'professor' else None,
            siap=form.siap.data.strip() if tipo == 'professor' else None,
            nivel_discente=form.nivel_discente.data if tipo == 'discente' else None,
            ativo=True
        )

        db.session.add(membro)
        db.session.commit()

        return redirect(url_for('membros.listar_membros'))

    return render_template('membros/cadastrar.html', form=form)

# Rota para verificar a frequência dos membros
@membros.route('/verificar_frequencia')
def verificar_frequencia():
    # Lógica para verificar a frequência
    return render_template('membros/verificar_frequencia.html')

def normalizar_nome(nome):
    nome = str(nome).strip().upper()

    nome = unicodedata.normalize("NFKD", nome)
    nome = "".join(c for c in nome if not unicodedata.combining(c))

    nome = re.sub(r"\s+", " ", nome)

    return nome