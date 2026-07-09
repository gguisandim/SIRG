from app import create_app, db
from app.models import Usuario

app = create_app()

with app.app_context():
    email = "lucileia@ufpa.br"

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        usuario = Usuario(
            nome="Lucileia Rosa",
            email=email,
            perfil="secretaria",
            ativo=True
        )
        usuario.set_password("123456")
        db.session.add(usuario)
        print("Usuário secretaria criado.")
    else:
        usuario.perfil = "secretaria"
        usuario.ativo = True
        usuario.set_password("123456")
        print("Usuário secretaria atualizado.")

    db.session.commit()
    print("Concluído.")