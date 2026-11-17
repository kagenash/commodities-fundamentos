"""Conversões de unidade, paridade etanol x açúcar e estimativa de produção.

Coeficientes de ATR usados pela UNICA (kg de ATR por kg de açúcar ou por litro de etanol):
açúcar VHP 1,0453; açúcar branco 1,0495; etanol anidro 1,7492; etanol hidratado 1,6761.
"""

LIBRAS_POR_TONELADA = 2204.62262

ATR_POR_KG_ACUCAR = {"vhp": 1.0453, "branco": 1.0495}
ATR_POR_LITRO_ETANOL = {"anidro": 1.7492, "hidratado": 1.6761}


def centavos_lb_para_usd_t(preco_c_lb):
    """c/lb -> US$/t. Exemplo: 20 c/lb = 440,92 US$/t."""
    return preco_c_lb / 100 * LIBRAS_POR_TONELADA


def usd_t_para_centavos_lb(preco_usd_t):
    """US$/t -> c/lb."""
    return preco_usd_t / LIBRAS_POR_TONELADA * 100


def centavos_lb_para_brl_t(preco_c_lb, cambio_brl_usd):
    """c/lb -> R$/t: o preço do açúcar visto por quem produz no Brasil."""
    return centavos_lb_para_usd_t(preco_c_lb) * cambio_brl_usd


def receita_acucar_por_kg_atr(preco_c_lb, cambio_brl_usd, tipo="vhp"):
    """Quanto 1 kg de ATR rende, em R$, se virar açúcar."""
    return centavos_lb_para_brl_t(preco_c_lb, cambio_brl_usd) / 1000 / ATR_POR_KG_ACUCAR[tipo]


def receita_etanol_por_kg_atr(preco_brl_m3, tipo="hidratado"):
    """Quanto 1 kg de ATR rende, em R$, se virar etanol (preço na usina, sem impostos)."""
    return preco_brl_m3 / 1000 / ATR_POR_LITRO_ETANOL[tipo]


def paridade_etanol_c_lb(preco_etanol_brl_m3, cambio_brl_usd, tipo_etanol="hidratado", tipo_acucar="vhp"):
    """Preço do açúcar, em c/lb, que paga pelo ATR o mesmo que o etanol.

    Versão simplificada: não desconta os custos de exportação do açúcar (frete e porto).
    """
    receita = receita_etanol_por_kg_atr(preco_etanol_brl_m3, tipo_etanol)
    brl_por_tonelada = receita * ATR_POR_KG_ACUCAR[tipo_acucar] * 1000
    return usd_t_para_centavos_lb(brl_por_tonelada / cambio_brl_usd)


def premio_acucar_sobre_etanol(preco_acucar_c_lb, preco_etanol_brl_m3, cambio_brl_usd, tipo_etanol="hidratado"):
    """Prêmio do açúcar sobre o etanol, em %. Positivo: o açúcar paga mais pelo ATR."""
    paridade = paridade_etanol_c_lb(preco_etanol_brl_m3, cambio_brl_usd, tipo_etanol)
    return (preco_acucar_c_lb / paridade - 1) * 100


def estimar_producao_acucar(cana_mi_t, atr_kg_por_t, mix_acucar_pct, tipo="vhp"):
    """Açúcar produzido, em milhões de t, a partir da cana moída, do ATR médio e do mix açucareiro.

    Exemplo: 600 mi t de cana, ATR de 138 kg/t e mix de 52% dão cerca de 41,2 mi t de açúcar VHP.
    """
    atr_total_mi_t = cana_mi_t * atr_kg_por_t / 1000
    return atr_total_mi_t * mix_acucar_pct / 100 / ATR_POR_KG_ACUCAR[tipo]
