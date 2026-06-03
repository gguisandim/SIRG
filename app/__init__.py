# app/__init__.py
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, current_user, login_required
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail
from dotenv import load_dotenv


load_dotenv()


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
mail = Mail()

login_manager.login_view = "usuarios.login"
login_manager.login_message = "Faça login para acessar o sistema."


def create_app(config_filename="config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_filename)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from .models import Membro, Reuniao, Frequencia, Oficio, Banca, Usuario

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Importando blueprints
    from .routes.usuarios import usuarios
    from .routes.membros import membros
    from .routes.reunioes import reunioes
    from .routes.frequencias import frequencias
    from .routes.relatorios import relatorios
    from .routes.oficios import oficios
    from .routes.bancas import bancas
    from .routes.ia import ia
    from .routes.justificativas import justificativas
    from app.routes.assistente import assistente

    # Registrando blueprints
    app.register_blueprint(usuarios)
    app.register_blueprint(membros, url_prefix="/membros")
    app.register_blueprint(reunioes, url_prefix="/reunioes")
    app.register_blueprint(frequencias, url_prefix="/frequencias")
    app.register_blueprint(relatorios, url_prefix="/relatorios")
    app.register_blueprint(oficios, url_prefix="/oficios")
    app.register_blueprint(bancas, url_prefix="/bancas")
    app.register_blueprint(ia)
    app.register_blueprint(assistente)
    app.register_blueprint(justificativas)

    @app.route("/")
    def home():
        if not current_user.is_authenticated:
            return redirect(url_for("usuarios.login"))

        if current_user.perfil == "professor":
            return redirect(url_for("justificativas.minhas_faltas"))

        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        if current_user.perfil == "professor":
            return redirect(url_for("justificativas.minhas_faltas"))

        return render_template("home.html")

    admin = Admin(app, name="Admin Dashboard")

    admin.add_view(ModelView(Membro, db.session))
    admin.add_view(ModelView(Reuniao, db.session))
    admin.add_view(ModelView(Frequencia, db.session))
    admin.add_view(ModelView(Oficio, db.session))
    admin.add_view(ModelView(Banca, db.session))
    admin.add_view(ModelView(Usuario, db.session))

    return app