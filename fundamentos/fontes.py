"""Download e cache das séries mensais do estudo. Fonte: FRED, sem chave de API."""

from __future__ import annotations

import io
import warnings
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import pandas as pd

URL_FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={codigo}"


@dataclass(frozen=True)
class Serie:
    codigo: str
    descricao: str
    unidade: str


SERIES = {
    "acucar": Serie("PSUGAISAUSDM", "Açúcar nº 11, preço global (FMI)", "c/lb"),
    "brent": Serie("POILBREUSDM", "Petróleo Brent, preço global (FMI)", "US$/barril"),
    "cambio": Serie("EXBZUS", "Câmbio, média mensal (Federal Reserve)", "R$ por US$"),
}


def ler_csv_fred(texto: str, nome: str) -> pd.Series:
    """Converte o CSV do FRED numa série mensal.

    Aceita o cabeçalho antigo (DATE) e o atual (observation_date); "." vira valor ausente.
    """
    tabela = pd.read_csv(io.StringIO(texto), na_values=["."])
    meses = pd.PeriodIndex(pd.to_datetime(tabela.iloc[:, 0]).dt.to_period("M"))
    valores = pd.to_numeric(tabela.iloc[:, 1], errors="coerce").to_numpy()
    return pd.Series(valores, index=meses, name=nome).dropna()


def baixar_serie(nome: str, pasta_cache: Path, atualizar: bool = True) -> pd.Series:
    """Baixa a série do FRED e guarda o CSV. Sem internet, usa o último CSV salvo."""
    serie = SERIES[nome]
    pasta_cache.mkdir(parents=True, exist_ok=True)
    arquivo = pasta_cache / f"{serie.codigo}.csv"
    if atualizar:
        pedido = Request(
            URL_FRED_CSV.format(codigo=serie.codigo),
            headers={"User-Agent": "commodities-fundamentos/0.1"},
        )
        try:
            with urlopen(pedido, timeout=30) as resposta:
                arquivo.write_bytes(resposta.read())
        except URLError as erro:
            if not arquivo.exists():
                raise RuntimeError(f"Não consegui baixar {serie.codigo} e não há cache em {arquivo}") from erro
            warnings.warn(f"Falha ao baixar {serie.codigo}; usando o cache de {arquivo}", stacklevel=2)
    if not arquivo.exists():
        raise FileNotFoundError(f"Sem cache para {serie.codigo} em {arquivo}; rode sem --offline")
    return ler_csv_fred(arquivo.read_text(encoding="utf-8"), nome)


def carregar_base(pasta_cache: Path, inicio: str | None = None, atualizar: bool = True) -> pd.DataFrame:
    """Junta as três séries nos meses em comum, a partir do mês de início."""
    base = pd.DataFrame({nome: baixar_serie(nome, pasta_cache, atualizar) for nome in SERIES}).dropna()
    if inicio:
        base = base[base.index >= pd.Period(inicio, freq="M")]
    return base
