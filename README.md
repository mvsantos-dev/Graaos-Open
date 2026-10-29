# Graaos Open

**Graaos — hub de inteligência de mercado do agro e da logística, com dados públicos.**

[![CI](https://github.com/mvsantos-dev/Graaos-Open/actions/workflows/ci.yml/badge.svg)](https://github.com/mvsantos-dev/Graaos-Open/actions/workflows/ci.yml)
[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue)](LICENSE)
[![Dados: CC BY 4.0](https://img.shields.io/badge/dados-CC%20BY%204.0-green)](data/LICENSE)

Este repositório é o **core aberto** do Graaos: o pipeline que baixa, confere e organiza os dados
públicos, os dados tratados que ele gera e o método. O primeiro módulo é o **Fertilizantes**:
importações brasileiras de fertilizantes (capítulo 31 do SH, posições 3102 a 3105), os insumos do
fósforo (enxofre e rocha fosfática), a relação de troca com a soja exportada, a comparação com o
mercado internacional e sinais automáticos de preço e de volume.

O site [radar.graaos.cloud](https://radar.graaos.cloud/) e o relatório mensal publicado nele
continuam gratuitos para ler. O código do site e do relatório mensal fica num repositório privado;
os números que eles mostram saem dos dados deste repositório.

**Fonte: Comex Stat/MDIC; Banco Mundial (Pink Sheet); BCB/PTAX.**

## O que tem aqui

| Parte | Onde |
| --- | --- |
| Ingestão incremental do Comex Stat (importação de fertilizantes, de enxofre e rocha fosfática e exportação de soja), da Pink Sheet do Banco Mundial e da PTAX do BCB | `src/ingest.py`, `src/benchmark.py` |
| Tabelas analíticas e o export `dashboard.json` | `src/transform.py`, `src/comparacao.py`, `src/troca.py`, `src/nutrientes.py`, `src/insumos.py`, `src/mapa.py` |
| Sinais de preço e de volume, por regras fixas, sem IA | `src/sinais.py` → `data/sinais.json` |
| Marcos de mercado (anotações escolhidas à mão, com fonte) | `data/eventos.yml`, lido por `src/eventos.py` |
| Dados brutos e tratados, de 2015-01 em diante | `data/` |
| Método, cortes e regras | [METODOLOGIA.md](METODOLOGIA.md) |
| Dicionário de campos e formato do `sinais.json` | [DADOS.md](DADOS.md) |

## Módulos do Graaos

| Módulo | Situação |
| --- | --- |
| **Fertilizantes**: volumes, origens, portos, rotas e frete, preços, mercado internacional, relação de troca com a soja, custo por nutriente, insumos do fósforo e sinais | dados neste repositório; site em [radar.graaos.cloud](https://radar.graaos.cloud/) |
| **Logística portuária**: fila, espera e terminais nos portos | planejado |
| **Grãos** | planejado |

O Graaos cobre granéis sólidos, grãos e logística. Granéis líquidos (óleos vegetais, químicos e
combustíveis) ficam de fora: ácido sulfúrico (2807), ácido fosfórico (2809) e amônia (2814) não
entram em nenhuma série.

## O que é aberto e o que será pago

- **Aberto e gratuito, para sempre:** este pipeline, os dados tratados, o método, o site
  [radar.graaos.cloud](https://radar.graaos.cloud/) e o relatório mensal, para ler.
- **Em construção, como serviço à parte:** alertas personalizados, watchlist de produtos, origens
  e portos, API e acesso via MCP.

Nada do que hoje é aberto vai migrar para a parte paga.

## Como rodar

Requer Python 3.10 ou mais recente. Nenhuma fonte pede chave, e nada aqui usa segredo.

```bash
python -m venv .venv
source .venv/bin/activate        # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.ingest --inicio 2015-01   # baixa só o que falta: Comex Stat, Pink Sheet e PTAX
python -m src.transform                 # gera as tabelas de data/processed/
python -m src.sinais                    # grava data/sinais.json
python -m src.eventos                   # confere data/eventos.yml
```

O repositório já traz a série de 2015-01 em diante, então o transform e os sinais rodam sem
baixar nada. A ingestão é incremental: só consulta os meses que ainda não estão no disco, uma
consulta por ano e por série, com pausa de 10 s entre chamadas (a API do Comex Stat responde 429 a
chamadas seguidas). Se uma fonte disser que publicou um mês e ele não vier, o comando termina com
erro (código 1).

| Opção da ingestão | O que faz |
| --- | --- |
| `--inicio AAAA-MM` | primeiro mês (a série mensal do Comex Stat começa em 1997-01) |
| `--fim AAAA-MM` | último mês; o padrão é o último publicado em cada fonte |
| `--serie todas\|fertilizantes\|soja\|insumos\|benchmark\|cambio` | série a baixar (padrão: `todas`); `insumos` é enxofre e rocha fosfática, `benchmark` é a Pink Sheet e `cambio`, a PTAX |
| `--ultimo-gravado` | imprime o último mês completo (o menor entre as cinco séries), sem chamar nenhuma fonte; com `--por-serie`, uma linha por série |
| `--forcar` | baixa de novo meses já gravados (as fontes revisam meses recentes) |
| `--atualizar-ncm` | regenera `data/ncm_fertilizantes.csv` e `data/ncm_insumos.csv` a partir da API |
| `--pausa SEG` | pausa mínima entre chamadas à API do Comex Stat (padrão: 10 s) |
| `--ssl-inseguro` | último recurso para problemas de certificado (veja [SSL](#ssl)) |

Para ler os dados em Python:

```python
from src.ingest import ler_raw, ler_soja, ler_insumos
from src.benchmark import ler_pink, ler_ptax

importacoes = ler_raw()   # data/raw/ano=AAAA/importacoes.parquet, com a coluna ano
```

As tabelas tratadas também podem ser baixadas direto de cada
[release `dados-AAAA-MM`](https://github.com/mvsantos-dev/Graaos-Open/releases): o
`dashboard.json`, o `sinais.json` e os CSVs de `data/processed/` do mês.

### Testes

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Os testes não acessam a rede (as APIs são simuladas) e conferem os dados versionados: os totais do
`dashboard.json`, o `sinais.json` em dia com ele e as tabelas de referência do mapa.

## Dados

| Pasta ou arquivo | Conteúdo |
| --- | --- |
| `data/raw/ano=AAAA/importacoes.parquet` | importações de fertilizantes: mês, NCM, país de origem, UF de destino, via, URF, US$ FOB, kg, US$ CIF, frete e seguro |
| `data/raw_soja/ano=AAAA/exportacoes.parquet` | exportação de soja em grão (NCM 12019000), só FOB e kg |
| `data/raw_insumos/ano=AAAA/importacoes.parquet` | importações de enxofre (2503) e rocha fosfática (2510), à parte: nunca entram nos totais de fertilizantes |
| `data/raw_benchmark/pink_sheet_mensal.csv` e `fonte.json` | Pink Sheet do Banco Mundial (US$/t nominal) e a edição baixada (URL, data, sha256, licença) |
| `data/raw_cambio/ptax_venda_media_mensal.csv` | PTAX venda, média mensal (SGS 3698) |
| `data/ncm_fertilizantes.csv`, `data/ncm_insumos.csv` | NCMs acompanhados e o grupo de cada um |
| `data/processed/*.csv` e `dashboard.json` | tabelas analíticas: preços, shares, HHI, sazonalidade, rotas, estados, troca, benchmark, custo por nutriente e insumos |
| `data/ref/` | tabelas de referência do mapa: país → ISO3, ponto de rótulo e continente; URF → porto e coordenadas |
| `data/sinais.json` | sinais de preço e de volume, formato versão 1 |
| `data/eventos.yml` | marcos de mercado, editados à mão |

O dicionário de cada coluna e o formato do `sinais.json` estão em [DADOS.md](DADOS.md). A coluna
`ano` dos Parquet fica no caminho (partição no estilo Hive), não dentro do arquivo. As saídas do
transform são determinísticas: os mesmos dados geram arquivos idênticos.

**A UF do Comex Stat na importação é a UF de destino da mercadoria**, qualquer que seja a sede do
importador, e não a UF do porto. **A URF não é exatamente o porto:** é a unidade da Receita onde a
carga foi desembaraçada (para fertilizantes, quase sempre o porto de chegada).

## Como ler os números

O método completo está em [METODOLOGIA.md](METODOLOGIA.md). Quatro regras valem para qualquer uso:

- **Relação de troca é "no porto", não o preço ao produtor.** É o CIF do fertilizante ÷ o FOB da
  soja exportada no mesmo mês, em US$/US$: não muda com o câmbio.
- **Custo por nutriente também é no porto.** CIF ÷ teor do nutriente no grau comercial usual; não é
  o preço ao produtor.
- **Spread contra a Pink Sheet não é ágio.** O benchmark é de outro lugar e de outro momento de
  contrato; o spread vai sempre com o preço do Brasil na mesma base.
- **Custo de insumo por tonelada de MAP é uma aproximação**, não o custo de nenhuma empresa, e é no
  porto.

## Atualização automática

O workflow [`atualizacao.yml`](.github/workflows/atualizacao.yml) roda uma vez por dia, do dia 1 ao
dia 15 de cada mês. Se o mês anterior já está gravado nas cinco séries, encerra sem chamar nenhuma
fonte. Senão, roda a ingestão incremental (Pink Sheet e PTAX primeiro; o Comex Stat só até o menor
mês das duas), o transform, os sinais e os testes. Se o mês completo avançou, commita só `data/`
como `github-actions[bot]` (mensagem `chore(dados): atualização AAAA-MM`) e cria o release
`dados-AAAA-MM` com o `dashboard.json`, o `sinais.json` e os CSVs.

- Mês completo = gravado nas cinco séries. Se faltar alguma, nada é commitado e o run fica verde,
  com um aviso de qual falta; a partir do dia 15, o job `prazo` fica vermelho dizendo qual.
- Falha de uma fonte, ou mês publicado que não vem, deixa o job vermelho e nada é commitado.
- Privilégios separados: o job que roda Python só lê o repositório e entrega `data/` como artifact;
  o único com escrita só roda git e o `gh release`, com hooks desligados, e recusa mudança fora de
  `data/`. Nenhum job usa segredo além do `GITHUB_TOKEN` do próprio Actions.

## Observações sobre as fontes

- **Comex Stat:** `https://api-comexstat.mdic.gov.br`, sem autenticação. Num período de vários
  anos, a API soma em cada ano só os meses do intervalo; por isso a ingestão consulta um ano por
  vez. Os códigos de URF mudam com reorganizações da Receita (em séries longas, agrupe por Região
  Fiscal, os dois primeiros dígitos). O MDIC pode revisar meses recentes: use `--forcar`.
- **Pink Sheet:** o endereço do xlsx muda a cada edição; o programa lê a página Commodity Markets
  do Banco Mundial, baixa o arquivo só de hosts do Banco Mundial, por HTTPS e com limite de tamanho,
  e regrava a série inteira a cada edição, listando os meses revisados.
- **PTAX:** série 3698 do SGS do BCB, em janelas de 5 anos, só os meses que faltam.

### SSL

A API do Comex Stat está atrás da Cloudflare, com certificado de uma autoridade pública. A
verificação TLS fica sempre ligada, com o bundle do `certifi`. `COMEXSTAT_CA_BUNDLE` soma CAs extras
(PEM ou DER). Como último recurso, `--ssl-inseguro` repete as chamadas sem verificação, só depois de
uma falha e só para `api-comexstat.mdic.gov.br`, com aviso no log.

## Licenças

Código: [MIT](LICENSE) · Dados tratados: [CC BY 4.0](data/LICENSE)

O crédito dos dados tratados é **"Graaos (github.com/mvsantos-dev/Graaos-Open)"**. Os dados de
origem seguem as licenças das fontes, mesmo quando aparecem nos arquivos tratados.

### Licenças das fontes

- **Comex Stat:** dados abertos do MDIC.
- **Pink Sheet:** World Bank Commodity Price Data (The Pink Sheet), do Banco Mundial, com licença
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **PTAX:** série 3698 do SGS, do Banco Central do Brasil. O Portal de Dados Abertos do BCB publica
  as séries de câmbio do dólar com licença [ODbL](https://opendatacommons.org/licenses/odbl/). A
  PTAX e os valores em reais calculados com ela seguem a mesma licença.
- **Natural Earth:** coordenadas e continentes de `data/ref/`, em
  [domínio público](https://www.naturalearthdata.com/about/terms-of-use/).

### Como citar

> Graaos (github.com/mvsantos-dev/Graaos-Open). Importação de fertilizantes no Brasil: volumes,
> origens, portos, preços e relação de troca. Dados tratados sob CC BY 4.0. Fonte: Comex Stat/MDIC;
> Banco Mundial (Pink Sheet); BCB/PTAX.

O [CITATION.cff](CITATION.cff) tem os mesmos dados em formato legível por máquina.

## Desenvolvimento

- Python 3.10+; dependências em `requirements.txt`, as de desenvolvimento em `requirements-dev.txt`.
- CI ([`ci.yml`](.github/workflows/ci.yml)): pytest em Python 3.10 e 3.13 e gitleaks em todo o
  histórico, em push e pull request, só com leitura.
- Segredos nunca entram no repositório. O pre-commit com gitleaks bloqueia vazamentos:
  `pip install pre-commit && pre-commit install`.
- Commits em português, no padrão Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).

Fonte: Comex Stat/MDIC; Banco Mundial (Pink Sheet); BCB/PTAX.
