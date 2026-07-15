from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    SelectField,
    TextAreaField,
    DateField,
    PasswordField,
    TimeField
)
from wtforms.validators import DataRequired, Email, Optional, ValidationError, Email
from app.models import Membro
from wtforms import TextAreaField
from wtforms.validators import Length
from wtforms.validators import DataRequired, Email, Length, Optional
from wtforms import StringField, DateField, TimeField, SelectField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired()])
    submit = SubmitField("Entrar")


class CadastroUsuarioForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    email = StringField("E-mail", validators=[DataRequired(), Email()])
    siap = StringField("SIAP", validators=[DataRequired(message="O SIAP é obrigatório.")])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Cadastrar")

class CadastroMembroForm(FlaskForm):
    nome = StringField(
        'Nome',
        validators=[DataRequired(message="O nome é obrigatório.")]
    )

    email = StringField(
        'E-mail',
        validators=[
            DataRequired(message="O e-mail é obrigatório."),
            Email(message="E-mail inválido.")
        ]
    )

    tipo = SelectField(
        'Tipo',
        choices=[
            ('professor', 'Professor'),
            ('discente', 'Discente'),
            ('tecnico', 'Técnico')
        ],
        validators=[DataRequired(message="O tipo é obrigatório.")]
    )

    linha_de_pesquisa = SelectField(
        'Linha de Pesquisa',
        choices=[
            ('', 'Nenhuma / Não se aplica'),
            ('Historia da Educação Basica', 'Historia da Educação Basica'),
            ('Currículo da Educação Básica', 'Currículo da Educação Básica'),
            (
                'Gestão e Organização do Trabalho Pedagógico Na Escola Básica',
                'Gestão e Organização do Trabalho Pedagógico Na Escola Básica'
            )
        ],
        validators=[Optional()]
    )

    siap = StringField(
        'SIAP',
        validators=[Optional()]
    )

    nivel_discente = SelectField(
        'Nível do Discente',
        choices=[
            ('', 'Nenhum / Não se aplica'),
            ('mestrado', 'Mestrado'),
            ('doutorado', 'Doutorado')
        ],
        validators=[Optional()]
    )

    submit = SubmitField('Cadastrar')

    def validate_email(self, email):
        membro = Membro.query.filter_by(email=email.data.strip().lower()).first()

        if membro:
            raise ValidationError('Este e-mail já está cadastrado no sistema.')

    def validate_siap(self, siap):
        valor = (siap.data or '').strip()

        if self.tipo.data == 'professor':
            if not valor:
                raise ValidationError('O SIAP é obrigatório para professores.')

            if not valor.isdigit():
                raise ValidationError('O SIAP deve conter apenas números.')

            if len(valor) > 8:
                raise ValidationError('O SIAP deve ter no máximo 8 dígitos.')

        else:
            if valor:
                if not valor.isdigit():
                    raise ValidationError('O SIAP deve conter apenas números.')

                if len(valor) > 8:
                    raise ValidationError('O SIAP deve ter no máximo 8 dígitos.')

    def validate_nivel_discente(self, nivel_discente):
        if self.tipo.data == 'discente' and not nivel_discente.data:
            raise ValidationError('O nível é obrigatório para discentes.')
        
class ReuniaoForm(FlaskForm):
    titulo = StringField(
        'Título da Reunião',
        validators=[DataRequired(message="O título é obrigatório.")]
    )

    data = DateField(
        'Data',
        validators=[DataRequired(message="A data é obrigatória.")]
    )

    horario = TimeField(
        'Horário',
        validators=[DataRequired(message="O horário é obrigatório.")]
    )

    tipo = SelectField(
        'Tipo de Reunião',
        choices=[
            ('', 'Selecione o tipo'),
            ('Ordinária', 'Ordinária'),
            ('Extraordinária', 'Extraordinária')
        ],
        validators=[DataRequired(message="O tipo da reunião é obrigatório.")]
    )

    local = SelectField(
        'Local',
        choices=[
            ('', 'Selecione o local'),
            ('NEB01', 'NEB01'),
            ('NEB02', 'NEB02'),
            ('NEB03', 'NEB03'),
            ('NEB04', 'NEB04'),
            ('NEB05', 'NEB05'),
            ('NEB06', 'NEB06')
        ],
        validators=[DataRequired(message="O local é obrigatório.")]
    )

    numero_oficio = IntegerField(
    'Número do Ofício',
    validators=[Optional()]
    )

    pauta = TextAreaField(
        'Pauta da Reunião',
        validators=[Optional()]
    )

    submit = SubmitField('Cadastrar Reunião')

class OficioInternoForm(FlaskForm):
    numero = StringField(
        'Número do Ofício',
        validators=[DataRequired(message="O número do ofício é obrigatório.")]
    )

    descricao = TextAreaField(
        'Descrição do Ofício',
        validators=[
            DataRequired(message="A descrição é obrigatória."),
            Length(max=300)
        ]
    )

    destinatario = StringField(
        'Destinatário',
        validators=[
            DataRequired(message="O destinatário é obrigatório."),
            Length(max=100)
        ]
    )

    submit = SubmitField('Cadastrar Ofício Interno')


class EditalForm(FlaskForm):
    numero = StringField(
        'Número do Edital',
        validators=[DataRequired(message="O número do edital é obrigatório.")]
    )

    descricao = TextAreaField(
        'Descrição do Edital',
        validators=[
            DataRequired(message="A descrição é obrigatória."),
            Length(max=300)
        ]
    )

    destinatario = StringField(
        'Destinatário / Setor Responsável',
        validators=[
            DataRequired(message="O destinatário ou setor responsável é obrigatório."),
            Length(max=100)
        ]
    )

    submit = SubmitField('Cadastrar Edital')