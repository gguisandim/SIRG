from app import create_app, db
from app.models import Membro

app = create_app()


def popular_professores():
    mapeamento_emails = {
        "AMELIA MARIA ARAUJO MESQUITA": "amelia.mesquita05@gmail.com",
        "CLARICE NASCIMENTO DE MELO": "claricemelo054@gmail.com",
        "DANIELE DOROTEIA ROCHA DA SILVA DE LIMA": "danieledoroteia@gmail.com",
        "DINAIR LEAL DA HORA": "tucupi@uol.com.br",
        "DORIEDSON DO SOCORRO RODRIGUES": "doriedson@ufpa.br",
        "EMINA MARCIA NERY DOS SANTOS": "emina@ufpa.br",
        "ERINALDO VICENTE CAVALCANTI": "erinaldocavalcanti@ufpa.br",
        "FABRICIO AARAO FREIRE CARVALHO": "fafc33@gmail.com",
        "GENYLTON ODILON REGO DA ROCHA": "genylton@gmail.com",
        "JOAO PAULO DA CONCEICAO ALVES": "jpaulochee@gmail.com",
        "JOSE BITTENCOURT DA SILVA": "josebittencourtsilva@gmail.com",
        "MARCIO ANTONIO RAIOL DOS SANTOS": "marsraiol@gmail.com",
        "MARIA DE FATIMA MATOS DE SOUZA": "fmatoz@gmail.com",
        "MARIA JOSE AVIZ DO ROSARIO": "mrosario@ufpa.br",
        "MAURO CEZAR COELHO": "maurocezar.temp@ufpa.br",
        "NEY CRISTINA MONTEIRO DE OLIVEIRA": "neycmo@ufpa.br",
        "RAIMUNDO ALBERTO DE FIGUEIREDO DAMASCENO": "albertofdamasceno59@gmail.com",
        "RONALDO MARCOS DE LIMA ARAUJO": "ronaldolimaaraujo@gmail.com",
        "VIVIAN DA SILVA LOBATO": "vivianlobato@ufpa.br",
        "WILMA DE NAZARE BAIA COELHO": "wilmacoelho@yahoo.com.br",
    }

    professores_dados = [
        {"siap": "2353806", "nome": "AMELIA MARIA ARAUJO MESQUITA", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "1673903", "nome": "ANDRIO ALVES GATINHO", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "396632", "nome": "ANTONIO CARLOS MACIEL", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO"},
        {"siap": "2835103", "nome": "BENEDITA ALCIDEMA COELHO DOS SANTOS MAGALHAES", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "1212471", "nome": "CLARICE NASCIMENTO DE MELO", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "2495174", "nome": "CLEIDE CARVALHO DE MATOS", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "2549696", "nome": "DANIELE DOROTEIA ROCHA DA SILVA DE LIMA", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "2555964", "nome": "DINAIR LEAL DA HORA", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "2321894", "nome": "DORIEDSON DO SOCORRO RODRIGUES", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "327930", "nome": "EMINA MARCIA NERY DOS SANTOS", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "1244168", "nome": "ERINALDO VICENTE CAVALCANTI", "linha": "HISTÓRIA DA EDUCAÇÃO BÁSICA"},
        {"siap": "1486870", "nome": "FABRICIO AARAO FREIRE CARVALHO", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "1153154", "nome": "GENYLTON ODILON REGO DA ROCHA", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "2481484", "nome": "IRLANDA DO SOCORRO DE OLIVEIRA MILEO", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "3335913", "nome": "JADSON FERNANDO GARCIA GONCALVES", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "1269545", "nome": "JOAO PAULO DA CONCEICAO ALVES", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "2190538", "nome": "JOSE BITTENCOURT DA SILVA", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "2333806", "nome": "LEONARDO ZENHA CORDEIRO", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "1323011", "nome": "LIVIA SOUSA DA SILVA", "linha": "HISTÓRIA DA EDUCAÇÃO BÁSICA"},
        {"siap": "2220353", "nome": "MARCIO ANTONIO RAIOL DOS SANTOS", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "6328125", "nome": "MARIA DE FATIMA MATOS DE SOUZA", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "2153065", "nome": "MARIA DO SOCORRO DA COSTA COELHO", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "1152648", "nome": "MARIA JOSE AVIZ DO ROSARIO", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "2216215", "nome": "MAURO CEZAR COELHO", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "3474377", "nome": "NEIDE MARIA FERNANDES RODRIGUES DE SOUSA", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "1152656", "nome": "NEY CRISTINA MONTEIRO DE OLIVEIRA", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "326878", "nome": "RAIMUNDO ALBERTO DE FIGUEIREDO DAMASCENO", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "2337218", "nome": "RENATO PINHEIRO DA COSTA", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "1152796", "nome": "RONALDO MARCOS DE LIMA ARAUJO", "linha": "GESTÃO E ORGANIZAÇÃO DO TRABALHO PEDAGÓGICO NA ESCOLA BÁSICA"},
        {"siap": "2657198", "nome": "VIVIAN DA SILVA LOBATO", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "3171125", "nome": "WILLIAN LAZARETTI DA CONCEICAO", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
        {"siap": "2178662", "nome": "WILMA DE NAZARE BAIA COELHO", "linha": "CURRÍCULO DA EDUCAÇÃO BÁSICA"},
    ]

    for dado in professores_dados:
        email_final = mapeamento_emails.get(
            dado["nome"],
            f"{dado['nome'].split()[0].lower()}.{dado['siap']}@temp.com"
        )

        membro = Membro.query.filter_by(email=email_final).first()

        if membro:
            membro.nome = dado["nome"]
            membro.tipo = "professor"
            membro.linha_de_pesquisa = dado["linha"]
            membro.siap = dado["siap"]
            membro.ativo = True
            membro.set_password("mudar123")
            print(f"Atualizado: {membro.nome}")
        else:
            membro = Membro(
                nome=dado["nome"],
                email=email_final,
                tipo="professor",
                linha_de_pesquisa=dado["linha"],
                siap=dado["siap"],
                ativo=True,
            )
            membro.set_password("mudar123")
            db.session.add(membro)
            print(f"Criado: {membro.nome}")

    db.session.commit()
    print("Professores sincronizados com sucesso.")


with app.app_context():
    popular_professores()