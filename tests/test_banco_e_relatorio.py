import pytest

from fundamentos.__main__ import main
from fundamentos.banco import executar_consulta, salvar_precos
from fundamentos.fontes import SERIES
from fundamentos.relatorio import gerar_relatorio, numero_br


def test_variacao_em_12_meses_calculada_em_sql(tmp_path, base_sintetica):
    caminho = tmp_path / "precos.db"
    salvar_precos(base_sintetica, caminho)
    resultado = executar_consulta(caminho)
    esperado = (base_sintetica["acucar"].iloc[-1] / base_sintetica["acucar"].iloc[-13] - 1) * 100
    assert len(resultado) == len(base_sintetica)
    assert resultado["variacao_12m_pct"].iloc[-1] == pytest.approx(esperado, abs=0.05)


def test_relatorio_gera_resumo_e_graficos(tmp_path, base_sintetica):
    resumo = gerar_relatorio(base_sintetica, tmp_path / "relatorios", tmp_path / "precos.db")
    assert "Último mês disponível" in resumo.read_text(encoding="utf-8")
    assert (tmp_path / "relatorios" / "graficos" / "precos.png").exists()
    assert (tmp_path / "relatorios" / "graficos" / "correlacao_movel.png").exists()


def test_linha_de_comando_offline_le_o_cache(tmp_path, base_sintetica):
    pasta_brutos = tmp_path / "dados" / "brutos"
    pasta_brutos.mkdir(parents=True)
    for nome, codigo in SERIES.items():
        linhas = ["observation_date," + codigo]
        linhas += [f"{mes.start_time:%Y-%m-%d},{valor}" for mes, valor in base_sintetica[nome].items()]
        (pasta_brutos / f"{codigo}.csv").write_text("\n".join(linhas), encoding="utf-8")
    main(["relatorio", "--offline", "--dados", str(tmp_path / "dados"), "--saida", str(tmp_path / "saida"), "--inicio", "2020-01"])
    assert (tmp_path / "saida" / "resumo.md").exists()


def test_linha_de_comando_paridade(capsys):
    main(["paridade", "--etanol", "2500", "--cambio", "5", "--acucar", "15"])
    saida = capsys.readouterr().out
    assert "Paridade do etanol hidratado" in saida
    assert "Prêmio do açúcar sobre o etanol" in saida


def test_numero_no_padrao_brasileiro():
    assert numero_br(1234.567) == "1.234,57"
    assert numero_br(-0.5, 1) == "-0,5"


def test_linha_de_comando_producao(capsys):
    main(["producao", "--cana", "600", "--atr", "138", "--mix", "52"])
    assert "Açúcar estimado: 41,2 milhões de t" in capsys.readouterr().out
