from app import create_app, db

app = create_app()

with app.app_context():
    db.session.execute(db.text(
        "ALTER TABLE frequencia ADD COLUMN anexo_justificativa VARCHAR(255)"
    ))
    db.session.commit()

print("Coluna anexo_justificativa criada.")