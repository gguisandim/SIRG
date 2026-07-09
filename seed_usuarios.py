from app import create_app, db
from app.models import Usuario

app = create_app()

usuarios = [
    {
        "nome": "Guilherme Sandim",
        "email": "guilhermesandim.gs@gmail.com",
        "senha": "123456",
        "perfil": "secretaria",
    },
    {
        "nome": "Professor Teste",
        "email": "professor@email.com",
        "senha": "123456",
        "perfil": "professor",
    },
]

with app.app_context():
    for dados in usuarios:
        usuario = Usuario.query.filter_by(email=dados["email"]).first()

        if usuario:
            usuario.nome = dados["nome"]
            usuario.perfil = dados["perfil"]
            usuario.ativo = True
            usuario.set_password(dados["senha"])
            print(f"Atualizado: {usuario.email}")
        else:
            usuario = Usuario(
                nome=dados["nome"],
                email=dados["email"],
                perfil=dados["perfil"],
                ativo=True,
            )
            usuario.set_password(dados["senha"])
            db.session.add(usuario)
            print(f"Criado: {usuario.email}")

    db.session.commit()
    print("Usuários sincronizados com sucesso.")