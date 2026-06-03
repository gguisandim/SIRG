from app import create_app
from app.models import Usuario, Membro, Reuniao, Frequencia

app = create_app()

with app.app_context():
    print("\n=== USUÁRIOS ===")
    for u in Usuario.query.all():
        print(u.id, u.nome, u.email, "perfil:", u.perfil, "membro_id:", u.membro_id, "ativo:", u.ativo)

    print("\n=== MEMBROS ===")
    for m in Membro.query.all():
        print(m.id, m.nome, m.email, "tipo:", m.tipo, "ativo:", m.ativo)

    print("\n=== REUNIÕES ===")
    for r in Reuniao.query.all():
        print(r.id, r.titulo, r.data, r.tipo)

    print("\n=== FREQUÊNCIAS ===")
    for f in Frequencia.query.all():
        print(
            "freq_id:", f.id,
            "membro_id:", f.membro_id,
            "reuniao_id:", f.reuniao_id,
            "status:", f.status,
            "justificativa:", f.justificativa
        )