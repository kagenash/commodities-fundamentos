import pandas as pd
import pytest

from fundamentos.analise import correlacao_movel, enriquecer, regressao, retornos_log, variacao_12_meses


def test_enriquecer_converte_para_dolar_e_real(base_sintetica):
    base = enriquecer(base_sintetica)
    esperado = base["acucar"] * 22.0462262 * base["cambio"]
    assert base["acucar_brl_t"].to_numpy() == pytest.approx(esperado.to_numpy())


def test_correlacao_movel_de_series_iguais_e_um(base_sintetica):
    retornos = retornos_log(base_sintetica)
    retornos["brent"] = retornos["acucar"]
    correlacoes = correlacao_movel(retornos, janela=12)
    assert correlacoes["brent"].to_numpy() == pytest.approx(1.0)


def test_regressao_recupera_os_coeficientes_conhecidos(base_sintetica):
    modelo = regressao(retornos_log(base_sintetica))
    assert modelo.params["brent"] == pytest.approx(0.4, abs=0.1)
    assert modelo.params["cambio"] == pytest.approx(-0.6, abs=0.15)


def test_variacao_em_12_meses():
    serie = pd.Series([100.0] + [105.0] * 11 + [112.0])
    assert variacao_12_meses(serie) == pytest.approx(12.0)
