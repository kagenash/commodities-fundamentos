"""Linha de comando: python -m fundamentos relatorio | paridade."""

from __future__ import annotations

import argparse
from pathlib import Path

from .conversoes import paridade_etanol_c_lb, premio_acucar_sobre_etanol
from .fontes import carregar_base
from .relatorio import gerar_relatorio, numero_br


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="fundamentos", description="Fundamentos do mercado de açúcar")
    comandos = parser.add_subparsers(dest="comando", required=True)

    relatorio = comandos.add_parser("relatorio", help="baixa os dados e gera gráficos e resumo")
    relatorio.add_argument("--inicio", default="2005-01", help="primeiro mês do estudo (AAAA-MM)")
    relatorio.add_argument("--janela", type=int, default=24, help="meses da correlação móvel")
    relatorio.add_argument("--offline", action="store_true", help="usa só os CSVs já baixados")
    relatorio.add_argument("--dados", type=Path, default=Path("dados"), help="pasta do cache e do SQLite")
    relatorio.add_argument("--saida", type=Path, default=Path("relatorios"), help="pasta dos resultados")

    paridade = comandos.add_parser("paridade", help="paridade etanol x açúcar em c/lb")
    paridade.add_argument("--etanol", type=float, required=True, help="etanol na usina, em R$/m³, sem impostos")
    paridade.add_argument("--cambio", type=float, required=True, help="câmbio, em R$ por US$")
    paridade.add_argument("--acucar", type=float, help="açúcar nº 11 em c/lb, para calcular o prêmio")
    paridade.add_argument("--tipo", choices=("hidratado", "anidro"), default="hidratado")

    args = parser.parse_args(argv)
    if args.comando == "relatorio":
        base = carregar_base(args.dados / "brutos", inicio=args.inicio, atualizar=not args.offline)
        resumo = gerar_relatorio(base, args.saida, args.dados / "precos.db", janela=args.janela)
        print(f"Resumo gerado em {resumo}")
        return

    valor_paridade = paridade_etanol_c_lb(args.etanol, args.cambio, args.tipo)
    print(f"Paridade do etanol {args.tipo}: {numero_br(valor_paridade)} c/lb")
    if args.acucar is not None:
        premio = premio_acucar_sobre_etanol(args.acucar, args.etanol, args.cambio, args.tipo)
        quem_paga_mais = "açúcar" if premio > 0 else "etanol"
        print(f"Prêmio do açúcar sobre o etanol: {numero_br(premio, 1)}% (paga mais: {quem_paga_mais})")


if __name__ == "__main__":
    main()
