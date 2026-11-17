"""Gera os gráficos e o resumo em Markdown."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from .analise import correlacao_movel, enriquecer, regressao, retornos_log, variacao_12_meses  # noqa: E402
from .banco import executar_consulta, salvar_precos  # noqa: E402

AZUL = "#1f4e79"
CINZA = "#7f7f7f"
LARANJA = "#c55a11"
FONTE = "Fonte: FMI e Federal Reserve, via FRED (médias mensais). Elaboração própria."


def numero_br(valor: float, casas: int = 2) -> str:
    """Formata no padrão brasileiro: 1.234,56."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def _limpar_eixo(eixo) -> None:
    eixo.grid(alpha=0.3)
    eixo.spines[["top", "right"]].set_visible(False)


def grafico_precos(base: pd.DataFrame, caminho: Path) -> None:
    """Açúcar em c/lb (em cima) e em R$/t (embaixo): o câmbio muda a leitura."""
    datas = base.index.to_timestamp()
    figura, (eixo_usd, eixo_brl) = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
    eixo_usd.plot(datas, base["acucar"], color=AZUL, linewidth=1.6)
    eixo_usd.set_ylabel("c/lb")
    eixo_usd.set_title("Açúcar nº 11 em dólar (c/lb) e em reais (R$/t)", loc="left")
    eixo_brl.plot(datas, base["acucar_brl_t"], color=CINZA, linewidth=1.6)
    eixo_brl.set_ylabel("R$/t")
    for eixo in (eixo_usd, eixo_brl):
        _limpar_eixo(eixo)
    figura.text(0.01, 0.01, FONTE, fontsize=8, color="#555555")
    figura.tight_layout(rect=(0, 0.03, 1, 1))
    figura.savefig(caminho, dpi=150)
    plt.close(figura)


def grafico_correlacao(correlacoes: pd.DataFrame, janela: int, caminho: Path) -> None:
    """Correlação móvel do retorno do açúcar com o Brent e com o câmbio."""
    datas = correlacoes.index.to_timestamp()
    figura, eixo = plt.subplots(figsize=(10, 4.5))
    eixo.plot(datas, correlacoes["brent"], color=AZUL, linewidth=1.6, label="Açúcar × Brent")
    eixo.plot(datas, correlacoes["cambio"], color=LARANJA, linewidth=1.6, label=r"Açúcar × câmbio (R\$/US\$)")
    eixo.axhline(0, color="#333333", linewidth=0.8)
    eixo.set_ylim(-1, 1)
    eixo.set_title(f"Correlação móvel de {janela} meses dos retornos mensais", loc="left")
    eixo.legend(frameon=False, loc="lower left")
    _limpar_eixo(eixo)
    figura.text(0.01, 0.01, FONTE, fontsize=8, color="#555555")
    figura.tight_layout(rect=(0, 0.04, 1, 1))
    figura.savefig(caminho, dpi=150)
    plt.close(figura)


def _linha_coeficiente(nome: str, modelo, variavel: str) -> str:
    return (
        f"| {nome} | {numero_br(modelo.params[variavel], 3)} | "
        f"{numero_br(modelo.bse[variavel], 3)} | {numero_br(modelo.pvalues[variavel], 3)} |"
    )


def _celula(valor, casas: int, sufixo: str = "") -> str:
    return "" if pd.isna(valor) else f"{numero_br(valor, casas)}{sufixo}"


def gerar_relatorio(base: pd.DataFrame, pasta_saida: Path, caminho_banco: Path, janela: int = 24) -> Path:
    """Roda o estudo completo e devolve o caminho do resumo."""
    pasta_graficos = pasta_saida / "graficos"
    pasta_graficos.mkdir(parents=True, exist_ok=True)

    base = enriquecer(base)
    retornos = retornos_log(base)
    correlacoes = correlacao_movel(retornos, janela=janela)
    modelo = regressao(retornos)

    salvar_precos(base, caminho_banco)
    variacoes = executar_consulta(caminho_banco)

    grafico_precos(base, pasta_graficos / "precos.png")
    grafico_correlacao(correlacoes, janela, pasta_graficos / "correlacao_movel.png")

    inicio, fim = base.index[0], base.index[-1]
    ultimo = base.iloc[-1]
    correlacao_total = retornos.corr()
    linhas = [
        "# Resumo do estudo",
        "",
        f"Período analisado: {inicio} a {fim} ({len(base)} meses). Gerado com `python -m fundamentos relatorio`.",
        "",
        f"## Último mês disponível ({fim})",
        "",
        "| Indicador | Valor |",
        "| --- | --- |",
        f"| Açúcar nº 11 | {numero_br(ultimo['acucar'])} c/lb ({numero_br(ultimo['acucar_usd_t'], 0)} US$/t) |",
        f"| Açúcar em reais | R$ {numero_br(ultimo['acucar_brl_t'], 0)}/t |",
        f"| Variação do açúcar em 12 meses | {numero_br(variacao_12_meses(base['acucar']), 1)}% |",
        f"| Petróleo Brent | US$ {numero_br(ultimo['brent'])}/barril |",
        f"| Câmbio | R$ {numero_br(ultimo['cambio'])} por US$ |",
        "",
        "## Açúcar, petróleo e câmbio",
        "",
        "Correlação dos retornos mensais no período todo: "
        f"açúcar × Brent = {numero_br(correlacao_total.loc['acucar', 'brent'])}; "
        f"açúcar × câmbio = {numero_br(correlacao_total.loc['acucar', 'cambio'])}.",
        f"Na janela móvel de {janela} meses, o valor mais recente é "
        f"{numero_br(correlacoes['brent'].iloc[-1])} (Brent) e {numero_br(correlacoes['cambio'].iloc[-1])} (câmbio).",
        "",
        "Regressão (MQO) do retorno mensal do açúcar, com erros-padrão robustos (HC1):",
        "",
        "| Variável | Coeficiente | Erro-padrão | p-valor |",
        "| --- | --- | --- | --- |",
        _linha_coeficiente("Constante", modelo, "const"),
        _linha_coeficiente("Brent", modelo, "brent"),
        _linha_coeficiente("Câmbio (R$/US$)", modelo, "cambio"),
        "",
        f"R² = {numero_br(modelo.rsquared)}; N = {int(modelo.nobs)} meses. "
        "Como os retornos estão em log, um coeficiente de 0,10 indica que 1% de alta na variável "
        "vem, em média, com 0,10% de alta no açúcar no mesmo mês.",
        "",
        "## Últimos 6 meses (consulta em `sql/variacao_mensal.sql`)",
        "",
        "| Mês | c/lb | R$/t | Var. no mês | Var. em 12 meses |",
        "| --- | --- | --- | --- | --- |",
    ]
    for _, linha in variacoes.tail(6).iterrows():
        linhas.append(
            f"| {linha['mes']} | {_celula(linha['acucar_c_lb'], 2)} | {_celula(linha['acucar_brl_t'], 0)} | "
            f"{_celula(linha['variacao_mes_pct'], 1, '%')} | {_celula(linha['variacao_12m_pct'], 1, '%')} |"
        )
    linhas += [
        "",
        "![Açúcar em dólar e em reais](graficos/precos.png)",
        "",
        "![Correlação móvel](graficos/correlacao_movel.png)",
    ]
    caminho = pasta_saida / "resumo.md"
    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return caminho
