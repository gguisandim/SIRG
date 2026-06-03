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
Você é um assistente administrativo do Programa de Pós-Graduação em Educação Básica - PPEB.

Sua tarefa é gerar uma ATA formal de reunião do Colegiado do PPEB/UFPA.

ATENÇÃO:
O modelo de ata NÃO deve ser copiado.
Use o modelo apenas como referência de estilo institucional, estrutura e linguagem.

REGRAS OBRIGATÓRIAS:
- Gere texto puro.
- NÃO use Markdown.
- NÃO use asteriscos.
- NÃO invente nomes.
- NÃO invente votos.
- NÃO invente decisões.
- NÃO invente datas.
- NÃO invente horários.
- Use somente os dados fornecidos.
- Se faltar informação, escreva entre colchetes.
- Preserve os pontos da pauta na mesma ordem.
- Não transforme informes em deliberações.
- Não reutilize conteúdo de atas anteriores.

MODELO DE REFERÊNCIA:
\"\"\"
{modelo_ata}
\"\"\"

DADOS DA NOVA ATA:

Título:
{titulo}

Tipo de reunião:
{tipo}

Data:
{data_reuniao}

Horário:
{horario}

Local:
{local}

Pauta:
\"\"\"
{pauta}
\"\"\"

Presentes:
\"\"\"
{presentes}
\"\"\"

Ausências justificadas:
\"\"\"
{justificativas}
\"\"\"

Anotações, discussões, decisões e encaminhamentos:
\"\"\"
{anotacoes}
\"\"\"

ESTRUTURA OBRIGATÓRIA:
1. Cabeçalho institucional.
2. Título formal da ata.
3. Abertura com data, horário, local e tipo da reunião.
4. Presentes.
5. Ausências justificadas.
6. Desenvolvimento da pauta.
7. Deliberações, somente se informadas.
8. Encerramento formal.

Finalize com:
"Nada mais havendo a tratar, eu, [nome do responsável], lavro a presente ata que, após aprovada, será assinada pelos presentes."
"""