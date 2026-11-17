from fundamentos.fontes import ler_csv_fred

CSV_CABECALHO_ATUAL = "observation_date,PSUGAISAUSDM\n2024-01-01,10.5\n2024-02-01,.\n2024-03-01,11.25\n"
CSV_CABECALHO_ANTIGO = "DATE,EXBZUS\n2024-01-01,5.0\n2024-02-01,5.5\n"


def test_le_cabecalho_atual_e_descarta_ausentes():
    serie = ler_csv_fred(CSV_CABECALHO_ATUAL, "acucar")
    assert list(serie.index.astype(str)) == ["2024-01", "2024-03"]
    assert serie.iloc[-1] == 11.25


def test_le_cabecalho_antigo():
    serie = ler_csv_fred(CSV_CABECALHO_ANTIGO, "cambio")
    assert serie.name == "cambio"
    assert list(serie) == [5.0, 5.5]
