🇧🇷 **Português** | 🇺🇸 [English](README.en.md)

# Fundamentos de commodities: açúcar

Estudo em Python sobre o que move o preço internacional do açúcar, olhando para o Brasil, maior exportador do mundo. Baixa séries públicas do FRED, guarda tudo em SQLite, mede a relação do açúcar com o petróleo e o câmbio e calcula a paridade entre etanol e açúcar, com CLI (`argparse`), consultas SQL e testes.

## Comandos

| Comando | O que faz | Exemplo de uso |
|---|---|---|
| `relatorio` | Baixa do FRED o açúcar nº 11 e o Brent (FMI) e o câmbio R$/US$ (Fed), grava em SQLite, calcula correlação móvel e regressão dos retornos mensais e gera gráficos e um resumo em Markdown | `python -m fundamentos relatorio --inicio 2005-01` |
| `paridade` | Calcula o preço do açúcar (c/lb) que remunera o ATR igual ao etanol e o prêmio do açúcar sobre o etanol | `python -m fundamentos paridade --etanol 2800 --cambio 5.40 --acucar 18.5` |

## Hipóteses testadas

| Variável | Mecanismo | Sinal esperado |
|---|---|---|
| Petróleo | Gasolina cara deixa o etanol mais competitivo; mais cana vai para o etanol e sai menos açúcar | Positivo |
| Câmbio (R$/US$) | Real fraco aumenta a receita em reais do exportador e estimula as vendas | Negativo |

## Exemplos de saída

A pasta [`relatorios/`](relatorios/) contém a saída real do comando `relatorio`, com dados mensais de jan/2005 a set/2026: o [resumo](relatorios/resumo.md) e os gráficos. Os principais achados:

- Os dois sinais esperados aparecem: a correlação dos retornos mensais do açúcar é de +0,29 com o Brent e de −0,36 com o câmbio.
- Na regressão, 1% de alta do dólar contra o real vem, em média, com 0,6% de queda do açúcar no mesmo mês; 1% de alta do Brent vem com 0,13% de alta (R² = 0,15).
- A relação muda com o tempo: a correlação móvel com o câmbio, em média −0,48 entre 2009 e 2021, ficou entre −0,24 e +0,10 desde meados de 2022; a do Brent subiu de −0,22 em fevereiro para +0,29 em setembro de 2026.

![Correlação móvel](relatorios/graficos/correlacao_movel.png)

## Instalação

```bash
git clone https://github.com/kagenash/commodities-fundamentos.git
cd commodities-fundamentos
pip install -r requirements.txt
```

Requer Python 3.10+. Os CSVs baixados e o SQLite ficam em `dados/`, fora do Git; sem internet, `--offline` usa os CSVs já baixados.

## Testes

Conversões de unidade, paridade, leitura do FRED, regressão, consulta SQL e CLI têm testes unitários com dados sintéticos:

```bash
pytest -v
```

## Paridade etanol x açúcar

A usina decide o mix comparando quanto cada produto paga pelo ATR (açúcar total recuperável):

```text
paridade (c/lb) = etanol (R$/m³) × 1,0453 / (coeficiente do etanol × câmbio × 22,0462)
```

- 1,0453 kg de ATR por kg de açúcar VHP; 1,6761 kg de ATR por litro de etanol hidratado e 1,7492 por litro de anidro (coeficientes usados pela UNICA).
- 22,0462 converte US$/t em c/lb.
- Versão simplificada: usa o preço do etanol na usina, sem impostos, e não desconta frete, elevação portuária nem prêmio de polarização do VHP.

## Estrutura

```
commodities-fundamentos/
├── fundamentos/
│   ├── fontes.py          # download e cache das séries (FRED)
│   ├── conversoes.py      # unidades e paridade etanol x açúcar
│   ├── analise.py         # retornos, correlação móvel e regressão
│   ├── banco.py           # SQLite e execução das consultas
│   ├── relatorio.py       # gráficos e resumo em Markdown
│   └── __main__.py        # CLI
├── sql/
│   └── variacao_mensal.sql
├── tests/
├── relatorios/
├── requirements.txt
└── README.md
```

## Limitações e próximos passos

- São médias mensais do FMI, não fechamentos diários da ICE, e a série sai com algumas semanas de atraso.
- Correlação não é causalidade; por isso a janela móvel e a regressão com erros-padrão robustos.
- Próximo passo: ler o acompanhamento quinzenal da UNICA (moagem, ATR, mix) e estimar a produção do Centro-Sul (cana × ATR × mix ÷ 1,0453), rumo a um balanço de oferta e demanda.

## Fontes

- FRED: [PSUGAISAUSDM](https://fred.stlouisfed.org/series/PSUGAISAUSDM), [POILBREUSDM](https://fred.stlouisfed.org/series/POILBREUSDM), [EXBZUS](https://fred.stlouisfed.org/series/EXBZUS)
- UNICA: [coeficientes de conversão do ATR](https://unicadata.com.br/arquivos/pdfs/2025/05/e647d9c8d569120eb3dae2234e1cc103.pdf)

## Licença

MIT — use, adapte e compartilhe à vontade.
