"""
Etapa 2: limpeza e classificação.

- junta todos os CSVs de data/raw/
- remove vagas repetidas (mesmo link, ou mesmo título + empresa)
- mantém só vagas de Analista de Dados / BI (filtro pelo título)
- remove vagas sem descrição
- cria colunas de texto normalizado e senioridade

Rode sozinho com:  python -m src.limpeza
Saída: data/processed/vagas_limpas.csv
"""

import re
import unicodedata
from pathlib import Path

import pandas as pd

from src import config

PASTA_RAW = Path("data/raw")
ARQUIVO_SAIDA = Path("data/processed/vagas_limpas.csv")


def normalizar(texto) -> str:
    """Minúsculas, sem acentos e com espaços simples. 'Estatística' -> 'estatistica'."""
    if not isinstance(texto, str):
        return ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    texto = re.sub(r"[*_#`>\[\]\\]", " ", texto)  # tira marcações de markdown
    return re.sub(r"\s+", " ", texto).strip()


def classificar_senioridade(titulo_norm: str) -> str:
    for nivel, padrao in config.SENIORIDADE:
        if re.search(padrao, titulo_norm):
            return nivel
    return config.SEM_SENIORIDADE


def carregar_brutos() -> pd.DataFrame:
    arquivos = sorted(PASTA_RAW.glob("*.csv"))
    if not arquivos:
        raise SystemExit("Nenhum CSV em data/raw/. Rode a coleta primeiro: python -m src.coleta")
    print(f"📂 Lendo {len(arquivos)} arquivo(s) de {PASTA_RAW}/")
    return pd.concat((pd.read_csv(a, encoding="utf-8-sig") for a in arquivos), ignore_index=True)


def limpar() -> pd.DataFrame:
    df = carregar_brutos()
    etapas = [("Vagas brutas", len(df))]

    # 1) Repetidas: o mesmo link aparece em vários termos de busca
    df = df.drop_duplicates(subset=["job_url"])
    df["titulo_norm"] = df["title"].map(normalizar)
    df["empresa_norm"] = df["company"].map(normalizar)
    df = df.drop_duplicates(subset=["titulo_norm", "empresa_norm"])
    etapas.append(("Sem repetidas", len(df)))

    # 2) Só vagas da área (pelo título)
    inclui = df["titulo_norm"].str.contains(config.TITULO_INCLUIR, regex=True)
    tema = df["titulo_norm"].str.contains(config.TITULO_TEMA, regex=True)
    exclui = df["titulo_norm"].str.contains(config.TITULO_EXCLUIR, regex=True)
    df = df[inclui & tema & ~exclui]
    etapas.append(("Só Analista de Dados/BI", len(df)))

    # 3) Precisa ter descrição (é dela que tiramos as skills)
    df["descricao_norm"] = df["description"].map(normalizar)
    df = df[df["descricao_norm"].str.len() >= 200]
    etapas.append(("Com descrição", len(df)))

    # 4) Senioridade
    df["senioridade"] = df["titulo_norm"].map(classificar_senioridade)

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8-sig")
    Path("outputs/tabelas").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(etapas, columns=["etapa", "vagas"]).to_csv("outputs/tabelas/funil_limpeza.csv", index=False, encoding="utf-8-sig")

    print("\n🧹 Funil da limpeza:")
    for nome, n in etapas:
        print(f"   {nome:<26} {n:>6}")
    print("\n📊 Vagas por senioridade:")
    print(df["senioridade"].value_counts().to_string())
    print(f"\n💾 Salvo em: {ARQUIVO_SAIDA}")
    return df


if __name__ == "__main__":
    limpar()
