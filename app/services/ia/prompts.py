from pathlib import Path
import re


def carregar_modelo_pauta_colegiado():
    caminho = Path("app/services/ia/modelos/pauta_modelo.txt")
    return caminho.read_text(encoding="utf-8")


def carregar_modelo_ata_colegiado():
    caminho = Path("app/services/ia/modelos/ata_modelo.txt")
    return caminho.read_text(encoding="utf-8")


def normalizar_pauta_bruta(texto):
    if not texto:
        return ""

    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    texto = re.sub(r"\n{3,}", "\n\n", texto)

    linhas = [linha.strip() for linha in texto.split("\n") if linha.strip()]

    dados_gerais = []
    itens = []
    informes = []
    secao_informes = False

    for linha in linhas:
        linha = linha.strip()

        if linha.upper().startswith("INFORMES"):
            secao_informes = True
            resto = linha.replace("INFORMES:", "").replace("INFORMES", "").strip()
            if resto:
                informes.append(resto.strip("-; "))
            continue

        if secao_informes:
            informes.append(linha.strip("-; "))
            continue

        item_match = re.match(r"^(\d+)[\.\)]?\s*(.*)$", linha)

        if item_match:
            conteudo = item_match.group(2).strip()
            if conteudo:
                itens.append(conteudo.strip("; "))
        else:
            dados_gerais.append(linha)

    partes = []

    if dados_gerais:
        partes.append("DADOS GERAIS:")
        partes.extend(dados_gerais)

    if itens:
        partes.append("\nITENS DA ORDEM DO DIA:")
        for i, item in enumerate(itens, start=1):
            partes.append(f"{i}. {item}")

    if informes:
        partes.append("\nINFORMES:")
        for i, informe in enumerate(informes, start=1):
            partes.append(f"{i}. {informe}")

    return "\n".join(partes).strip()


def prompt_pauta_colegiado_com_modelo(
    titulo,
    data_reuniao,
    horario,
    local,
    tipo,
    pauta_bruta,
    modelo_pauta
):
    return f"""
Você é um assistente administrativo do Programa de Pós-Graduação em Educação Básica - PPEB.

Sua tarefa é gerar SOMENTE O CONTEÚDO DA PAUTA da reunião.

REGRAS OBRIGATÓRIAS:
- NÃO gere cabeçalho.
- NÃO gere ofício.
- NÃO gere saudação.
- NÃO gere assinatura.
- NÃO use Markdown.
- NÃO use asteriscos.
- NÃO use negrito.
- Gere apenas texto puro.
- Use somente os dados informados pelo usuário.
- Não invente pontos de pauta.
- Não exclua pontos informados pelo usuário.
- Não transforme a pauta em texto corrido.
- Preserve a estrutura numerada.

REGRAS CONTRA QUEBRA DE FORMATAÇÃO:
- A pauta deve sempre ter as seções 1, 2, 3 e 4.
- Os pontos informados pelo usuário devem entrar em "3. Ordem do dia".
- Os itens da Ordem do dia devem ser numerados como 3.1, 3.2, 3.3 etc.
- Os informes devem entrar apenas em "4. Informes".
- Os informes devem ser numerados como 4.1, 4.2, 4.3 etc.
- Não misture informes com ordem do dia.
- Não pule numeração.
- Não remova números.
- Não renumere para 1, 2, 3 dentro da Ordem do dia.
- Mantenha a ordem original dos assuntos.

ESTRUTURA OBRIGATÓRIA:

1. Leitura e aprovação de Ata
1.1. [item referente à ata, se houver]

2. Proposições
2.1. [item referente a proposições, se houver]

3. Ordem do dia
3.1. [primeiro assunto informado]
3.2. [segundo assunto informado]
3.3. [terceiro assunto informado]

4. Informes
4.1. [primeiro informe informado]
4.2. [segundo informe informado]

MODELO DE REFERÊNCIA:
\"\"\"
{modelo_pauta}
\"\"\"

DADOS DA NOVA REUNIÃO:

Título:
{titulo}

Tipo:
{tipo}

Data:
{data_reuniao}

Horário:
{horario}

Local:
{local}

PAUTA NORMALIZADA PELO SISTEMA:
\"\"\"
{pauta_bruta}
\"\"\"

Agora gere somente a pauta em texto puro.
"""


def prompt_ata_colegiado_com_modelo(
    titulo,
    data_reuniao,
    horario,
    local,
    tipo,
    pauta,
    presentes,
    justificativas,
    anotacoes,
    modelo_ata
):
    return f"""
Você é o secretário administrativo do Programa de Pós-Graduação em Educação Básica - PPEB da UFPA.

Sua tarefa é redigir a ATA formal da reunião do Colegiado, unindo a pauta aos fatos ocorridos (anotações).

REGRAS OBRIGATÓRIAS DE ESTILO E FORMATAÇÃO:
1. Escreva em formato de TEXTO CORRIDO (prosa contínua).
2. É ESTRITAMENTE PROIBIDO usar listas, tópicos ou bullet points para quebrar linhas.
3. Junte os assuntos em parágrafos densos e contínuos usando conectivos formais (Ex: "Em seguida passou-se ao ponto...").
4. PROIBIDO RESUMIR BANCAS (MUITO IMPORTANTE): Você JAMAIS deve agrupar alunos ou resumir as bancas. Para CADA aluno(a) (seja de Mestrado ou Doutorado, Qualificação ou Defesa), você deve listar individualmente e de forma completa: O título do trabalho, a banca completa (com os cargos ao lado dos nomes) e a situação, mesmo que o texto da ata fique extremamente longo.
5. REGRA DE NEGRITO: Quando o texto abordar a homologação de Bancas (Defesa ou Qualificação), você DEVE envolver em asteriscos duplos (**texto**) APENAS O NOME DO(A) DISCENTE.
6. REGRA DE MEMBROS DA BANCA E SUPLENTES:
   - Mantenha sempre a função/papel de cada professor ao lado do seu nome, rigorosamente com os parênteses originais da pauta (ex: "(Orientador do trabalho e Presidente da Banca)", "(Examinadora Interna)", etc.).
   - EXCLUA COMPLETAMENTE do texto qualquer menção a professores que atuaram como "Suplente" ou "Membro Suplente". Se a pauta citar um suplente, ignore-o e não o escreva na ata.
   - Coloque um "e" conectando o último membro da banca (já que o suplente terá sido removido).
7. A linguagem deve ser extremamente formal e impessoal.
8. Inicie o texto sempre descrevendo a data por extenso.
9. Finalize exatamente com: "Nada mais havendo a tratar, eu, [nome do responsável], lavro a presente ata que após lida e aprovada será assinada por todos os presentes."

Exemplo prático de como encadear VÁRIAS bancas SEM RESUMIR e aplicando as regras 4, 5 e 6 perfeitamente:
"...homologação de ATA de Defesa do discente **Vanderlei Maciel Pinheiro**. Título: “A IMPLEMENTAÇÃO DA LEI 10.639/2003 NO CONTEXTO DO ENSINO MÉDIO: ENTRE AVANÇOS E CONTRADIÇÕES”: A banca foi composta pelos(a): Prof. Dr. Doriedson do Socorro Rodrigues (Orientador do trabalho e Presidente da Banca - UFPA), Profa. Dra. Benedita Alcidema Coelho dos Santos (Examinadora Interna – UFPA) e Prof. Dr. João Batista do Carmo Silva (Membro externo ao Programa). Data: 06/02/2025 às 14h. Situação: APROVADO. Em seguida, homologação da Banca de Defesa da mestranda **Claudia Gatinho de Miranda**. Título: “A GESTÃO DOS RECURSOS DO PROGRAMA DINHEIRO DIRETO NA ESCOLA (PDDE) NA REDE ESTADUAL DE ENSINO DO ESTADO DO PARÁ DE 2018 A 2024”. A banca será composta pelos seguintes membros: Prof. Dr. Fabrício Aarão Freire Carvalho (Orientador e Presidente), Profa. Dra. Irlanda do Socorro de Oliveira Mileo (Membro Interno - PPEB), Profa. Dra. Maria do Socorro Vasconcelos Pereira (Membro externo ao Programa) e Prof. Dr. Mark Clark Assen de Carvalho (Membro Externo - UFAC). Data: 04/07/2025 às 10h. Situação: APROVADA..."

DADOS DA REUNIÃO:
Título: {titulo}
Tipo de reunião: {tipo}
Data: {data_reuniao}
Horário: {horario}
Local: {local}

PAUTA PREVISTA:
{pauta}

PRESENTES:
{presentes}

AUSÊNCIAS JUSTIFICADAS:
{justificativas}

OCORRÊNCIAS/DECISÕES/ANOTAÇÕES DA REUNIÃO:
{anotacoes}

EXEMPLO DE ESTRUTURA E TOM ESPERADO:
\"\"\"
{modelo_ata}
\"\"\"

Baseado estritamente nas "Ocorrências/Decisões/Anotações da Reunião" informadas acima, redija a ata completa agora, em texto puro e corrido:
"""