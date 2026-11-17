"""Transformações e estatísticas do estudo."""

import numpy as np
import pandas as pd

from .conversoes import centavos_lb_para_brl_t, centavos_lb_para_usd_t


def enriquecer(base: pd.DataFrame) -> pd.DataFrame:
    """Acrescenta o açúcar em US$/t e em R$/t."""
    resultado = base.copy()
    resultado["acucar_usd_t"] = centavos_lb_para_usd_t(resultado["acucar"])
    resultado["acucar_brl_t"] = centavos_lb_para_brl_t(resultado["acucar"], resultado["cambio"])
    return resultado


def retornos_log(base: pd.DataFrame, colunas=("acucar", "brent", "cambio")) -> pd.DataFrame:
    """Variação mensal em log: aproxima a variação percentual e soma bem ao longo do tempo."""
    return np.log(base[list(colunas)]).diff().dropna()


def correlacao_movel(retornos: pd.DataFrame, alvo="acucar", outras=("brent", "cambio"), janela=24) -> pd.DataFrame:
    """Correlação do alvo com cada variável numa janela móvel de N meses."""
    return pd.DataFrame(
        {coluna: retornos[alvo].rolling(janela).corr(retornos[coluna]) for coluna in outras}
    ).dropna()


def regressao(retornos: pd.DataFrame, alvo="acucar", explicativas=("brent", "cambio")):
    """MQO do retorno mensal do açúcar contra petróleo e câmbio."""
    import statsmodels.api as sm

    matriz = sm.add_constant(retornos[list(explicativas)])
    return sm.OLS(retornos[alvo], matriz).fit()


def variacao_12_meses(serie: pd.Series) -> float:
    """Variação percentual entre o último mês e o mesmo mês do ano anterior."""
    if len(serie) < 13:
        raise ValueError("São necessários pelo menos 13 meses")
    return (serie.iloc[-1] / serie.iloc[-13] - 1) * 100
