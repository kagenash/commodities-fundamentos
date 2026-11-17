import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def base_sintetica():
    """Séries inventadas, só para testar o código: não são dados de mercado.

    O retorno do açúcar é montado como 0,4 x Brent - 0,6 x câmbio + ruído,
    para que a regressão tenha coeficientes conhecidos.
    """
    gerador = np.random.default_rng(7)
    meses = 60
    retorno_brent = gerador.normal(0, 0.05, meses)
    retorno_cambio = gerador.normal(0, 0.02, meses)
    retorno_acucar = 0.4 * retorno_brent - 0.6 * retorno_cambio + gerador.normal(0, 0.01, meses)
    return pd.DataFrame(
        {
            "acucar": 15 * np.exp(np.cumsum(retorno_acucar)),
            "brent": 70 * np.exp(np.cumsum(retorno_brent)),
            "cambio": 5 * np.exp(np.cumsum(retorno_cambio)),
        },
        index=pd.period_range("2020-01", periods=meses, freq="M"),
    )
