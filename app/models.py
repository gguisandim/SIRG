from flask_login import UserMixin
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    perfil = db.Column(db.String(30), nullable=False, default="professor")
    ativo = db.Column(db.Boolean, default=True)

    membro_id = db.Column(db.Integer, db.ForeignKey("membro.id"), nullable=True)

    membro = db.relationship(
        "Membro",
        backref=db.backref("usuario", uselist=False)
    )

    def set_password(self, senha):
        self.password_hash = generate_password_hash(senha)

    def check_password(self, senha):
        return check_password_hash(self.password_hash, senha)


class Membro(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(128), nullable=True)

    tipo = db.Column(db.String(20), nullable=False)
    # professor, discente ou tecnico

    linha_de_pesquisa = db.Column(db.String(200), nullable=True)

    siap = db.Column(db.String(8), nullable=True)
    # Somente para professor

    nivel_discente = db.Column(db.String(30), nullable=True)
    # mestrado ou doutorado

    ativo = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<Membro {self.nome}>"
    
class Oficio(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    numero = db.Column(db.String(50), nullable=False)
    ano = db.Column(db.Integer, nullable=False, default=lambda: datetime.now().year)

    tipo = db.Column(db.String(50), nullable=False)
    # valores: interno ou edital

    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.String(500), nullable=True)
    destinatario = db.Column(db.String(150), nullable=True)

    status = db.Column(db.String(50), nullable=False, default='usado')
    # valores possíveis: usado, cancelado, reservado

    template_sugerido = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    corpo = db.Column(db.Text, nullable=True)

    __table_args__ = (
        db.UniqueConstraint('numero', 'ano', 'tipo', name='numero_ano_tipo_unico'),
    )

    def __repr__(self):
        return f'<Ofício {self.numero}/{self.ano}>'
    

class Reuniao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    numero_oficio = db.Column(db.Integer, nullable=True)
    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)
    local = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    pauta = db.Column(db.Text, nullable=True)
    ata = db.Column(db.Text, nullable=True)
    presencas = db.relationship('Frequencia', backref='reuniao', lazy=True)
    justificativas_encerradas = db.Column(db.Boolean, default=False)

class Frequencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    membro_id = db.Column(db.Integer, db.ForeignKey('membro.id'), nullable=False)
    reuniao_id = db.Column(db.Integer, db.ForeignKey('reuniao.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    justificativa = db.Column(db.String(200), nullable=True)
    anexo_justificativa = db.Column(db.String(255), nullable=True)
    removido = db.Column(db.Boolean, default=False, nullable=False)

    membro = db.relationship('Membro', backref='frequencias')
    
class Banca(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    data = db.Column(db.Date, nullable=False)
    horario = db.Column(db.Time, nullable=False)

    responsavel_banca = db.Column(db.String(150), nullable=False)
    orientador = db.Column(db.String(150), nullable=False)

    sala = db.Column(db.String(20), nullable=True)
    nivel = db.Column(db.String(80), nullable=False)

    drive_status = db.Column(db.String(20), nullable=False, default='pendente')
    site_status = db.Column(db.String(20), nullable=False, default='pendente')

    erro_sigaa = db.Column(db.Text, nullable=True)

    convite_enviado = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Banca {self.responsavel_banca} - {self.data}>'