"""
Etapa 1: coleta das vagas no Indeed Brasil usando o JobSpy.

Rode sozinho com:  python -m src.coleta
Saída: data/raw/vagas_indeed_AAAA-MM-DD.csv
"""

import time
from datetime import date
from pathlib import Path

import pandas as pd
from jobspy import scrape_jobs

from src import config

PASTA_RAW = Path("data/raw")


def coletar_termo(termo: str) -> pd.DataFrame:
    """Busca um termo no Indeed e devolve um DataFrame (vazio se der erro)."""
    print(f"\n🔎 Buscando: '{termo}' ...")
    try:
        df = scrape_jobs(
            site_name=["indeed"],
            search_term=termo,
            location=config.LOCAL,
            country_indeed=config.PAIS_INDEED,
            results_wanted=config.VAGAS_POR_TERMO,
            hours_old=config.DIAS_ATRAS * 24,
            description_format="markdown",
            verbose=0,
        )
    except Exception as erro:  # o site pode mudar ou bloquear; não queremos perder o resto
        print(f"   ⚠️  Erro ao buscar '{termo}': {erro}")
        return pd.DataFrame()

    df["termo_busca"] = termo
    print(f"   ✅ {len(df)} vagas encontradas")
    return df


def coletar() -> Path:
    PASTA_RAW.mkdir(parents=True, exist_ok=True)

    resultados = []
    for i, termo in enumerate(config.TERMOS_BUSCA):
        resultados.append(coletar_termo(termo))
        if i < len(config.TERMOS_BUSCA) - 1:
            time.sleep(config.PAUSA_ENTRE_BUSCAS)

    vagas = pd.concat(resultados, ignore_index=True)
    if vagas.empty:
        raise SystemExit("Nenhuma vaga coletada. Veja a seção 'Problemas comuns' do guia.")

    arquivo = PASTA_RAW / f"vagas_indeed_{date.today().isoformat()}.csv"
    vagas.to_csv(arquivo, index=False, encoding="utf-8-sig")

    print(f"\n📦 Total bruto (com repetidas): {len(vagas)} vagas")
    print(f"💾 Salvo em: {arquivo}")
    return arquivo


if __name__ == "__main__":
    coletar()
