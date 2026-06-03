# Sistema de Controle de Frequência em Reuniões de Colegiado

## Visão geral

Este sistema tem como objetivo registrar e controlar a frequência de professores em reuniões de colegiado, permitindo que a secretaria:

- cadastre professores
- cadastre reuniões
- registre presença e ausência
- informe justificativas
- gere relatórios em planilha

A proposta é ser um sistema web simples, com foco em uso administrativo e geração de histórico confiável de frequência.

---

## Objetivo

Centralizar o controle de frequência dos professores em reuniões de colegiado, reduzindo o trabalho manual da secretaria e permitindo a geração de planilhas consolidadas por período.

---

## Público-alvo

O sistema será utilizado principalmente por:

- secretaria
- coordenação
- administração do colegiado

---

## Funcionalidades principais

### 1. Cadastro de professores

Permitir:

- adicionar professor
- editar professor
- listar professores
- inativar professor

#### Campos sugeridos

- nome completo
- matrícula ou SIAPE
- e-mail
- colegiado
- status: ativo/inativo

> Observação: o ideal é inativar o professor em vez de excluí-lo, para preservar o histórico de frequência.

---

### 2. Cadastro de reuniões

Permitir:

- criar reunião
- editar reunião
- cancelar reunião
- visualizar reuniões em lista ou calendário

#### Campos sugeridos

- título
- data
- horário
- local ou link
- observações
- tipo da reunião: ordinária ou extraordinária

---

### 3. Registro de frequência

Ao abrir uma reunião, o sistema deve exibir a lista de professores ativos para marcação de presença.

#### Status possíveis

- presente
- ausente
- ausente com justificativa

Se o status for **ausente com justificativa**, o sistema deve exigir o preenchimento do campo de justificativa.

#### Exemplos de justificativa

- atestado médico
- participação em evento
- atividade institucional
- afastamento autorizado

---

### 4. Relatórios e exportação

O sistema deve permitir a geração de planilhas em formato `.xlsx` com:

#### Aba 1: Resumo geral

| Professor | Reunião 1 | Reunião 2 | Reunião 3 | Presenças | Faltas | Justificadas | % Frequência |
|----------|-----------|-----------|-----------|-----------|--------|--------------|--------------|

#### Aba 2: Detalhamento

| Data | Professor | Status | Justificativa |
|------|-----------|--------|---------------|

#### Filtros sugeridos

- por mês
- por semestre
- por ano
- por colegiado

---

## Regras de negócio

### 1. Histórico não deve ser apagado

Professores não devem ser excluídos permanentemente. O correto é:

- manter os registros antigos
- marcar o professor como inativo quando necessário

### 2. Um registro por professor em cada reunião

Cada professor deve ter apenas um registro de frequência por reunião.

### 3. Justificativa vinculada ao status

A justificativa só deve existir quando o status for **ausente com justificativa**.

### 4. Cálculo de frequência

A regra de cálculo precisa ser definida antes da implementação. Algumas opções:

#### Opção A
```text
frequência = presenças / total de reuniões
```

#### Opção B
```text
frequência = (presenças + justificadas) / total de reuniões
```

Essa decisão depende da regra institucional do colegiado.

---

## Fluxo de uso

### Antes da reunião

- a secretaria cadastra a reunião no sistema

### Após a reunião

- a secretaria abre a reunião
- marca quem compareceu
- registra ausências
- adiciona justificativas quando necessário

### No fechamento do período

- gera a planilha de frequência
- exporta em Excel
- imprime ou envia o relatório

---

## Estrutura sugerida do banco de dados

### Tabela: professores

Campos:

- id
- nome
- matricula
- email
- colegiado
- ativo

### Tabela: reunioes

Campos:

- id
- titulo
- data
- horario
- local
- observacao
- tipo
- cancelada

### Tabela: frequencias

Campos:

- id
- professor_id
- reuniao_id
- status
- justificativa
- registrado_em

---

## Relacionamentos

- um professor pode ter várias frequências
- uma reunião pode ter várias frequências
- cada frequência pertence a um professor e a uma reunião

---

## Telas sugeridas

### 1. Dashboard

Exibir:

- próximas reuniões
- total de professores ativos
- reuniões do mês
- frequência média geral

### 2. Professores

Permitir:

- listar
- cadastrar
- editar
- inativar

### 3. Reuniões

Permitir:

- listar reuniões
- criar reunião
- editar
- cancelar
- visualizar no calendário

### 4. Frequência da reunião

Exibir tabela com:

- nome do professor
- status
- justificativa

### 5. Relatórios

Permitir:

- selecionar período
- filtrar por colegiado
- gerar planilha Excel

---

## Estrutura recomendada para Flask

Uma organização simples do projeto pode ser:

```text
sistema_frequencia/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── professores.py
│   │   ├── reunioes.py
│   │   ├── frequencias.py
│   │   └── relatorios.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── professores/
│   │   ├── reunioes/
│   │   ├── frequencias/
│   │   └── relatorios/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   └── services/
│       └── exportacao_excel.py
│
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

---

## Tecnologias sugeridas

### Backend

- Flask

### Banco de dados

- SQLite para a versão inicial
- PostgreSQL para produção

### ORM

- SQLAlchemy

### Formulários

- Flask-WTF

### Migrações

- Flask-Migrate

### Exportação de planilha

- openpyxl ou pandas + openpyxl

### Calendário no frontend

- FullCalendar

---

## MVP recomendado

Para a primeira versão, o ideal é implementar apenas o essencial:

- cadastro de professores
- cadastro de reuniões
- registro de frequência
- registro de justificativas
- exportação para Excel

Isso já resolve a necessidade principal da secretaria.

---

## Evoluções futuras

Depois da primeira versão, o sistema pode incluir:

- login por perfil de usuário
- anexar comprovantes de justificativa
- dashboard com gráficos
- notificações automáticas
- assinatura digital
- geração de PDF
- importação de professores por planilha

---

## Observações importantes

- a usabilidade precisa ser simples, porque o foco é uso administrativo
- o histórico precisa ser confiável
- a planilha gerada deve ser clara e pronta para uso institucional
- a regra de cálculo da frequência deve ser definida antes de codificar os relatórios

---

## Resumo da proposta

O sistema deve permitir que a secretaria gerencie reuniões de colegiado de forma centralizada, registrando presença, ausência e justificativas dos professores, com geração final de planilhas de frequência por período.

A proposta inicial pode ser desenvolvida com Flask, banco relacional e exportação em Excel, priorizando simplicidade, confiabilidade e facilidade de operação.

---

## Próximos passos sugeridos

1. definir as regras de negócio com clareza
2. validar os campos obrigatórios
3. modelar o banco de dados
4. desenhar as telas
5. implementar o MVP
6. testar a geração das planilhas

