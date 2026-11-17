-- Açúcar nº 11 por mês: preço em c/lb e em R$/t, com variação no mês e em 12 meses
-- 1 c/lb = 22,0462262 US$/t
WITH precos AS (
    SELECT
        mes,
        acucar_c_lb,
        acucar_c_lb * 22.0462262 * cambio_brl_usd AS acucar_brl_t
    FROM
        precos_mensais
)
SELECT
    mes,
    ROUND(acucar_c_lb, 2) AS acucar_c_lb,
    ROUND(acucar_brl_t, 0) AS acucar_brl_t,
    ROUND(100.0 * (acucar_c_lb / LAG(acucar_c_lb, 1) OVER (ORDER BY mes) - 1), 1) AS variacao_mes_pct,
    ROUND(100.0 * (acucar_c_lb / LAG(acucar_c_lb, 12) OVER (ORDER BY mes) - 1), 1) AS variacao_12m_pct
FROM
    precos
ORDER BY
    mes;
