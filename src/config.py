"""
Configurações do projeto.

Este é o arquivo que você mais vai editar:
- TERMOS_BUSCA: o que pesquisar no Indeed
- SKILLS: a lista de ferramentas/skills e o "padrão" (regex) que encontra cada uma no texto

Os padrões são aplicados em texto já normalizado: tudo minúsculo e SEM acentos.
Por isso escrevemos "estatistic" e não "estatístic", "ingles" e não "inglês".
"""

# ---------------------------------------------------------------------------
# Coleta
# ---------------------------------------------------------------------------
TERMOS_BUSCA = [
    "analista de dados",
    "data analyst",
    "analista de BI",
    "business intelligence",
    "analista de dados junior",
    "analista de dados pleno",
    "analista de dados senior",
]

PAIS_INDEED = "Brazil"
LOCAL = "Brazil"
VAGAS_POR_TERMO = 1000      # máximo que o JobSpy tenta trazer por termo
DIAS_ATRAS = 120           # só vagas publicadas nos últimos N dias
PAUSA_ENTRE_BUSCAS = 20    # segundos entre um termo e outro (evita bloqueio)

# ---------------------------------------------------------------------------
# Limpeza: quais títulos entram na análise
# ---------------------------------------------------------------------------
# O título precisa ter pelo menos um destes padrões...
TITULO_INCLUIR = r"analista|analyst|analytics|analise de dados|estagi|\bbi\b|business intel|inteligencia de negocios"
# ...e o título precisa falar de dados/BI (evita "Analista Financeiro", "Analista de RH" etc.)
TITULO_TEMA = r"dado|data|\bbi\b|business intel|analytics|inteligencia de negocios|power bi"
# Títulos com estes padrões saem (são outras profissões)
TITULO_EXCLUIR = r"cientista|scientist|engenheir|engineer|arquitet|architect|desenvolvedor|developer|dba\b"

# ---------------------------------------------------------------------------
# Senioridade (lida só do TÍTULO da vaga — a descrição costuma confundir)
# A ordem importa: a primeira regra que bater define o nível.
# ---------------------------------------------------------------------------
SENIORIDADE = [
    ("Estágio", r"estagi|intern\b|internship"),
    ("Júnior", r"junior|\bjr\b|\bi\b$|\bi\s*[-|(]|trainee|entry level"),
    ("Pleno", r"pleno|\bpl\b|\bii\b|mid[- ]level"),
    ("Sênior", r"senior|\bsr\b|\biii\b|especialista|specialist|lead\b|lider"),
]
SEM_SENIORIDADE = "Não informado"

# ---------------------------------------------------------------------------
# Skills: nome -> (categoria, padrão regex)
# Dica: teste um padrão novo em https://regex101.com antes de adicionar.
# ---------------------------------------------------------------------------
SKILLS = {
    # Consulta e linguagens
    "SQL":            ("Linguagem", r"\bsql\b|t-sql|pl/sql|\bmysql\b|postgres|sql server|\boracle\b"),
    "Python":         ("Linguagem", r"\bpython\b|\bpandas\b"),
    "R":              ("Linguagem", r"\blinguagem r\b|\bpython\s*(?:e|ou|/|,)\s*r\b|\br\s*(?:e|ou|/|,)\s*python\b|\brstudio\b|\btidyverse\b"),
    "DAX":            ("Linguagem", r"\bdax\b"),
    "VBA / Macros":   ("Linguagem", r"\bvba\b|\bmacros?\b"),
    # Planilhas
    "Excel":          ("Planilha", r"\bexcel\b|planilhas? eletronicas?"),
    "Google Sheets":  ("Planilha", r"google sheets|planilhas? (?:do )?google"),
    # Visualização / BI
    "Power BI":       ("Visualização", r"power ?bi|\bpbi\b"),
    "Tableau":        ("Visualização", r"\btableau\b"),
    "Looker":         ("Visualização", r"\blooker\b|data studio"),
    "Qlik":           ("Visualização", r"\bqlik"),
    # Cloud
    "AWS":            ("Cloud", r"\baws\b|amazon web services|redshift|\bathena\b"),
    "Azure":          ("Cloud", r"\bazure\b|synapse|data factory|microsoft fabric"),
    "GCP / BigQuery": ("Cloud", r"\bgcp\b|google cloud|bigquery"),
    # Engenharia / dados
    "ETL":            ("Engenharia de dados", r"\betl\b|\belt\b"),
    "Data Warehouse": ("Engenharia de dados", r"data ?warehouse|\bdw\b|data ?lake|lakehouse"),
    "Modelagem de dados": ("Engenharia de dados", r"modelagem de dados|data model|modelo dimensional|star schema|modelagem dimensional"),
    "Databricks":     ("Engenharia de dados", r"databricks"),
    "Spark":          ("Engenharia de dados", r"\bspark\b|pyspark"),
    "Airflow":        ("Engenharia de dados", r"airflow"),
    "dbt":            ("Engenharia de dados", r"\bdbt\b"),
    "Git":            ("Engenharia de dados", r"\bgit\b|github|gitlab"),
    # Conceitos
    "Estatística":    ("Conceito", r"estatistic|statistic"),
    "Machine Learning": ("Conceito", r"machine learning|aprendizado de maquina|\bml\b"),
    "IA Generativa":  ("Conceito", r"ia generativa|genai|generative ai|\bllms?\b|chatgpt|engenharia de prompt"),
    "KPIs / Indicadores": ("Conceito", r"\bkpis?\b|indicadores"),
    "Storytelling":   ("Conceito", r"storytelling"),
    # Comportamental e idioma
    "Comunicação":    ("Comportamental", r"comunicacao|comunicativ|communication"),
    "Inglês":         ("Idioma", r"\bingles\b|\benglish\b"),
}

# Ajustes de método (decididos depois de ler amostras das descrições)
# 1) Skills que ficam nas tabelas, mas NÃO entram nos gráficos/ranking principal.
#    "Indicadores" quase sempre descreve a tarefa ("monitorar indicadores"), não uma skill exigida.
FORA_DO_GRAFICO = ["KPIs / Indicadores"]

# 2) Skills que NÃO contam quando aparecem só como área de formação
#    (ex.: "ensino superior em engenharia, matemática, estatística ou áreas correlatas").
IGNORAR_EM_FORMACAO = ["Estatística"]
PADRAO_FORMACAO = (r"ensino superior|graduacao|graduado|formacao|formado|cursando|bacharel"
                   r"|superior completo|superior em|areas? correlatas|areas? afins")

# Gráficos
AUTOR = "Gabriel Leonardelli"         # aparece no rodapé dos gráficos — troque pelo seu nome
TOP_N_GRAFICO = 15
MIN_VAGAS_POR_NIVEL = 20   # níveis com menos vagas que isso não entram na comparação
