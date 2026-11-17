import pytest

from fundamentos.conversoes import (
    centavos_lb_para_brl_t,
    centavos_lb_para_usd_t,
    estimar_producao_acucar,
    paridade_etanol_c_lb,
    premio_acucar_sobre_etanol,
    receita_acucar_por_kg_atr,
    receita_etanol_por_kg_atr,
    usd_t_para_centavos_lb,
)


def test_centavos_por_libra_para_dolar_por_tonelada():
    assert centavos_lb_para_usd_t(20) == pytest.approx(440.9245, rel=1e-6)


def test_ida_e_volta_entre_unidades():
    assert usd_t_para_centavos_lb(centavos_lb_para_usd_t(17.5)) == pytest.approx(17.5)


def test_preco_em_reais_usa_o_cambio():
    assert centavos_lb_para_brl_t(20, 5) == pytest.approx(440.9245 * 5, rel=1e-6)


def test_na_paridade_o_atr_rende_o_mesmo_nos_dois_produtos():
    etanol, cambio = 2500.0, 5.2  # valores de teste
    acucar = paridade_etanol_c_lb(etanol, cambio)
    assert receita_acucar_por_kg_atr(acucar, cambio) == pytest.approx(receita_etanol_por_kg_atr(etanol))
    assert premio_acucar_sobre_etanol(acucar, etanol, cambio) == pytest.approx(0, abs=1e-9)


def test_real_mais_fraco_baixa_a_paridade_em_dolar():
    assert paridade_etanol_c_lb(2500, 6.0) < paridade_etanol_c_lb(2500, 5.0)


def test_anidro_usa_mais_atr_por_litro_que_o_hidratado():
    assert paridade_etanol_c_lb(2500, 5.0, "anidro") < paridade_etanol_c_lb(2500, 5.0, "hidratado")


def test_estimativa_de_producao_de_acucar():
    # 600 mi t de cana x 138 kg/t = 82,8 mi t de ATR; 52% vão para o açúcar; 1,0453 kg de ATR por kg de VHP
    assert estimar_producao_acucar(600, 138, 52) == pytest.approx(41.19, abs=0.01)
