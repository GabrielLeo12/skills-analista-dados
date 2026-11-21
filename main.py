"""
Roda o projeto inteiro: coleta -> limpeza -> análise.

    python main.py                 # tudo
    python main.py --pular-coleta  # usa os CSVs que já estão em data/raw/
"""

import argparse

from src.analise import analisar
from src.coleta import coletar
from src.limpeza import limpar

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Skills mais pedidas para Analista de Dados")
    parser.add_argument("--pular-coleta", action="store_true",
                        help="não coleta de novo; usa os arquivos de data/raw/")
    args = parser.parse_args()

    if not args.pular_coleta:
        print("=== 1/3 COLETA ===")
        coletar()
    print("\n=== 2/3 LIMPEZA ===")
    limpar()
    print("\n=== 3/3 ANÁLISE ===")
    analisar()
    print("\n🎉 Pronto! Veja a pasta outputs/")
