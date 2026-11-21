"""
Etapa 3: análise das skills.

Para cada skill, marcamos se ela aparece (pelo menos uma vez) na descrição de cada vaga.
O percentual é:  vagas que citam a skill / total de vagas analisadas.

Rode sozinho com:  python -m src.analise
Saídas:
  outputs/tabelas/ranking_skills.csv
  outputs/tabelas/skills_por_senioridade.csv
  outputs/tabelas/resumo.md
  outputs/graficos/top_skills.png        (formato 4:5, ideal para o LinkedIn)
  outputs/graficos/junior_vs_senior.png
"""

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # gera imagens sem abrir janela
import matplotlib.pyplot as plt
import pandas as pd

from src import config

ARQUIVO_LIMPO = Path("data/processed/vagas_limpas.csv")
PASTA_TABELAS = Path("outputs/tabelas")
PASTA_GRAFICOS = Path("outputs/graficos")

# Cores (paleta validada para daltonismo)
FUNDO = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
TINTA_FRACA = "#898781"
GRADE = "#e1e0d9"
AZUL = "#2a78d6"
LARANJA = "#eb6834"

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


# ---------------------------------------------------------------------------
# Cálculos
# ---------------------------------------------------------------------------
def _cita_fora_da_formacao(texto: str, padrao: str) -> bool:
    """True se a skill aparece pelo menos uma vez FORA de um trecho sobre formação acadêmica."""
    for achado in re.finditer(padrao, texto):
        janela = texto[max(0, achado.start() - 120): achado.end() + 60]
        if not re.search(config.PADRAO_FORMACAO, janela):
            return True
    return False


def marcar_skills(df: pd.DataFrame) -> pd.DataFrame:
    """Cria uma coluna True/False por skill: a vaga cita ou não cita."""
    for skill, (_, padrao) in config.SKILLS.items():
        if skill in config.IGNORAR_EM_FORMACAO:
            df[skill] = df["descricao_norm"].map(lambda t: _cita_fora_da_formacao(t, padrao))
        else:
            df[skill] = df["descricao_norm"].str.contains(padrao, regex=True)
    return df


def ranking_para_grafico(ranking: pd.DataFrame) -> pd.DataFrame:
    """Ranking sem as skills que decidimos deixar fora dos gráficos."""
    return ranking[~ranking["skill"].isin(config.FORA_DO_GRAFICO)].reset_index(drop=True)


def ranking_geral(df: pd.DataFrame) -> pd.DataFrame:
    total = len(df)
    linhas = []
    for skill, (categoria, _) in config.SKILLS.items():
        n = int(df[skill].sum())
        linhas.append({"skill": skill, "categoria": categoria, "vagas": n,
                       "percentual": round(100 * n / total, 1)})
    return pd.DataFrame(linhas).sort_values("percentual", ascending=False).reset_index(drop=True)


def ranking_por_senioridade(df: pd.DataFrame) -> pd.DataFrame:
    skills = list(config.SKILLS)
    tabela = (df.groupby("senioridade")[skills].mean() * 100).round(1).T
    contagem = df["senioridade"].value_counts()
    ordem = [n for n, _ in config.SENIORIDADE] + [config.SEM_SENIORIDADE]
    tabela = tabela[[n for n in ordem if n in tabela.columns]]
    tabela.columns = [f"{c} (n={contagem[c]})" for c in tabela.columns]
    return tabela


def periodo(df: pd.DataFrame) -> str:
    datas = pd.to_datetime(df["date_posted"], errors="coerce").dropna()
    if datas.empty:
        return ""
    ini, fim = datas.min(), datas.max()
    if (ini.year, ini.month) == (fim.year, fim.month):
        return f"{MESES[fim.month - 1]}/{fim.year}"
    return f"{MESES[ini.month - 1]}/{ini.year} a {MESES[fim.month - 1]}/{fim.year}"


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def _estilo_base(fig, ax):
    fig.patch.set_facecolor(FUNDO)
    ax.set_facecolor(FUNDO)
    for lado in ["top", "right", "left", "bottom"]:
        ax.spines[lado].set_visible(False)
    ax.tick_params(axis="both", length=0, colors=TINTA_2, labelsize=13)


def _cabecalho_e_rodape(fig, titulo, subtitulo, rodape):
    fig.text(0.06, 0.965, titulo, fontsize=22, fontweight="bold", color=TINTA, va="top")
    fig.text(0.06, 0.925, subtitulo, fontsize=13, color=TINTA_2, va="top")
    fig.text(0.06, 0.025, rodape, fontsize=10.5, color=TINTA_FRACA, va="bottom")


def grafico_top_skills(ranking: pd.DataFrame, total: int, per: str) -> Path:
    dados = ranking.head(config.TOP_N_GRAFICO).iloc[::-1]  # maior em cima

    fig, ax = plt.subplots(figsize=(10.8, 13.5), dpi=100)  # 1080 x 1350 px
    _estilo_base(fig, ax)
    fig.subplots_adjust(left=0.26, right=0.93, top=0.885, bottom=0.08)

    barras = ax.barh(dados["skill"], dados["percentual"], color=AZUL, height=0.62)
    for barra, pct in zip(barras, dados["percentual"]):
        ax.text(barra.get_width() + 1, barra.get_y() + barra.get_height() / 2,
                f"{pct:.0f}%", va="center", fontsize=14, fontweight="bold", color=TINTA)

    ax.set_xlim(0, max(100, dados["percentual"].max() + 10))
    ax.xaxis.set_visible(False)
    ax.tick_params(axis="y", labelsize=15, colors=TINTA)

    _cabecalho_e_rodape(
        fig,
        "O que as vagas de Analista de Dados pedem",
        f"% das {total} vagas que citam cada skill · Indeed Brasil{' · ' + per if per else ''}",
        f"Fonte: vagas públicas do Indeed Brasil (n={total}) · Análise: {config.AUTOR}",
    )
    arquivo = PASTA_GRAFICOS / "top_skills.png"
    fig.savefig(arquivo, facecolor=FUNDO)
    plt.close(fig)
    return arquivo


def grafico_junior_vs_senior(df: pd.DataFrame, ranking: pd.DataFrame, per: str) -> Path | None:
    """Gráfico de halteres: cada skill tem um ponto para o nível inicial e outro para o mais alto."""
    contagem = df["senioridade"].value_counts()
    niveis_ok = [n for n, _ in config.SENIORIDADE
                 if contagem.get(n, 0) >= config.MIN_VAGAS_POR_NIVEL and n != "Estágio"]
    if len(niveis_ok) < 2:
        print("   ℹ️  Poucas vagas por nível para comparar senioridades — gráfico pulado.")
        return None
    baixo, alto = niveis_ok[0], niveis_ok[-1]

    skills = ranking.head(12)["skill"].tolist()
    pct_baixo = df[df["senioridade"] == baixo][skills].mean() * 100
    pct_alto = df[df["senioridade"] == alto][skills].mean() * 100
    comp = pd.DataFrame({"baixo": pct_baixo, "alto": pct_alto})
    comp["dif"] = comp["alto"] - comp["baixo"]
    comp = comp.sort_values("dif")  # maior aumento em cima

    fig, ax = plt.subplots(figsize=(10.8, 13.5), dpi=100)
    _estilo_base(fig, ax)
    fig.subplots_adjust(left=0.26, right=0.93, top=0.84, bottom=0.08)

    y = range(len(comp))
    ax.hlines(y, comp["baixo"], comp["alto"], color=GRADE, linewidth=4, zorder=1)
    ax.scatter(comp["baixo"], y, s=170, color=AZUL, edgecolor=FUNDO, linewidth=2, zorder=2,
               label=f"{baixo} (n={contagem[baixo]})")
    ax.scatter(comp["alto"], y, s=170, color=LARANJA, edgecolor=FUNDO, linewidth=2, zorder=3,
               label=f"{alto} (n={contagem[alto]})")
    for i, (_, linha) in enumerate(comp.iterrows()):
        sinal = "+" if linha["dif"] >= 0 else "−"
        ax.text(max(linha["baixo"], linha["alto"]) + 2.5, i, f"{sinal}{abs(linha['dif']):.0f} p.p.",
                va="center", fontsize=12, color=TINTA_2)

    ax.set_yticks(list(y))
    ax.set_yticklabels(comp.index, fontsize=15, color=TINTA)
    ax.set_xlim(0, 110)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    ax.grid(axis="x", color=GRADE, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", bbox_to_anchor=(0.4, 1.06), ncol=2, frameon=False,
              fontsize=13, labelcolor=TINTA_2, handletextpad=0.3)

    _cabecalho_e_rodape(
        fig,
        f"O que muda do {baixo} para o {alto}",
        f"% das vagas de cada nível que citam a skill{' · ' + per if per else ''}",
        f"Fonte: vagas públicas do Indeed Brasil · Análise: {config.AUTOR}",
    )
    arquivo = PASTA_GRAFICOS / "junior_vs_senior.png"
    fig.savefig(arquivo, facecolor=FUNDO)
    plt.close(fig)
    return arquivo


# ---------------------------------------------------------------------------
# Resumo em texto (para copiar para o README e o LinkedIn)
# ---------------------------------------------------------------------------
def escrever_resumo(df, ranking, por_nivel, per) -> Path:
    total = len(df)
    remoto = df["is_remote"].fillna(False).astype(bool).mean() * 100 if "is_remote" in df else None
    linhas = [
        "# Resumo dos resultados",
        "",
        f"- Vagas analisadas: **{total}** (Indeed Brasil{', ' + per if per else ''})",
    ]
    if remoto is not None:
        linhas.append(f"- Vagas marcadas como remotas: **{remoto:.0f}%**")
    rank_g = ranking_para_grafico(ranking)
    linhas += ["", "## Top 10 skills", "", "| # | Skill | % das vagas |", "|---|---|---|"]
    for i, r in rank_g.head(10).iterrows():
        linhas.append(f"| {i + 1} | {r['skill']} | {r['percentual']:.0f}% |")
    fora = ranking[ranking["skill"].isin(config.FORA_DO_GRAFICO)]
    if not fora.empty:
        linhas += ["", "## Contexto (fora do ranking)", ""]
        for _, r in fora.iterrows():
            linhas.append(f"- {r['percentual']:.0f}% das vagas descrevem trabalho com {r['skill']}")
    linhas += ["", "## Frases prontas para o post", ""]
    for _, r in rank_g.head(5).iterrows():
        linhas.append(f"- {r['percentual']:.0f}% das vagas pedem {r['skill']}")
    linhas += ["", "## Por senioridade (% das vagas de cada nível)", "",
               por_nivel.to_markdown() if hasattr(por_nivel, "to_markdown") else por_nivel.to_string()]
    arquivo = PASTA_TABELAS / "resumo.md"
    arquivo.write_text("\n".join(linhas), encoding="utf-8")
    return arquivo


def exportar_base_dashboard(df: pd.DataFrame) -> Path:
    """Uma linha por vaga, uma coluna Sim/Não por skill — base para Excel ou Power BI."""
    colunas = ["title", "company", "location", "date_posted", "is_remote", "senioridade", "job_url"]
    base = df[[c for c in colunas if c in df.columns]].copy()
    base.columns = [{"title": "titulo", "company": "empresa", "location": "local",
                     "date_posted": "data_publicacao", "is_remote": "remoto",
                     "job_url": "link"}.get(c, c) for c in base.columns]
    for skill in config.SKILLS:
        base[skill] = df[skill].map({True: "Sim", False: "Não"})
    arquivo = PASTA_TABELAS / "base_dashboard.csv"
    base.to_csv(arquivo, index=False, encoding="utf-8-sig", sep=";")
    return arquivo


def analisar():
    PASTA_TABELAS.mkdir(parents=True, exist_ok=True)
    PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(ARQUIVO_LIMPO, encoding="utf-8-sig")
    df["descricao_norm"] = df["descricao_norm"].fillna("")
    df = marcar_skills(df)
    total = len(df)
    per = periodo(df)

    ranking = ranking_geral(df)
    ranking.to_csv(PASTA_TABELAS / "ranking_skills.csv", index=False, encoding="utf-8-sig")
    por_nivel = ranking_por_senioridade(df)
    por_nivel.to_csv(PASTA_TABELAS / "skills_por_senioridade.csv", encoding="utf-8-sig")

    exportar_base_dashboard(df)
    rank_g = ranking_para_grafico(ranking)

    print(f"\n🏆 Skills mais pedidas ({total} vagas):")
    for i, r in rank_g.head(10).iterrows():
        print(f"   {i + 1:>2}. {r['skill']:<20} {r['percentual']:>5.1f}%  ({r['vagas']} vagas)")

    print("\n🎨 Gerando gráficos...")
    print(f"   {grafico_top_skills(rank_g, total, per)}")
    g2 = grafico_junior_vs_senior(df, rank_g, per)
    if g2:
        print(f"   {g2}")
    print(f"\n📝 Resumo: {escrever_resumo(df, ranking, por_nivel, per)}")


if __name__ == "__main__":
    analisar()
