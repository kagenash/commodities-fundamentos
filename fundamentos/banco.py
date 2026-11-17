"""Base em SQLite e consultas em SQL."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

PASTA_SQL = Path(__file__).resolve().parents[1] / "sql"


def salvar_precos(base: pd.DataFrame, caminho_banco: Path) -> None:
    """Grava os preços mensais na tabela precos_mensais, substituindo a anterior."""
    tabela = pd.DataFrame(
        {
            "mes": base.index.astype(str),
            "acucar_c_lb": base["acucar"].to_numpy(),
            "brent_usd_barril": base["brent"].to_numpy(),
            "cambio_brl_usd": base["cambio"].to_numpy(),
        }
    )
    caminho_banco.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(caminho_banco)) as conexao:
        tabela.to_sql("precos_mensais", conexao, if_exists="replace", index=False)
        conexao.commit()


def executar_consulta(caminho_banco: Path, arquivo_sql: str = "variacao_mensal.sql") -> pd.DataFrame:
    """Roda uma consulta da pasta sql/ e devolve o resultado como tabela."""
    consulta = (PASTA_SQL / arquivo_sql).read_text(encoding="utf-8")
    with closing(sqlite3.connect(caminho_banco)) as conexao:
        return pd.read_sql_query(consulta, conexao)
