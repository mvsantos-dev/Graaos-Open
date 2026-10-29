# Metodologia

Como o Graaos Open baixa, organiza e calcula os dados do módulo Fertilizantes. Todo número citado
aqui é um padrão do código (`src/config.py` e os módulos de `src/`) ou sai dos dados versionados em
`data/`. O dicionário de campos está em [DADOS.md](DADOS.md).

Fonte: Comex Stat/MDIC; Banco Mundial (Pink Sheet); BCB/PTAX.

## Fontes

Só dados abertos oficiais, de governo ou de organismo internacional, com licença que permite
redistribuição. Nenhuma fonte pede chave.

| Fonte | O que vem dela | Acesso | Licença |
| --- | --- | --- | --- |
| Comex Stat (MDIC) | importação de fertilizantes (capítulo 31, posições 3102 a 3105) e de enxofre (2503) e rocha fosfática (2510.10 e 2510.20); exportação de soja em grão (NCM 12019000) | `POST /general` em `https://api-comexstat.mdic.gov.br`, um ano por consulta, detalhado por país, NCM, UF, via e URF, com FOB, kg, CIF, frete e seguro | dados abertos do MDIC |
| Banco Mundial (Pink Sheet) | preços mensais internacionais de ureia, DAP, TSP, cloreto de potássio e rocha fosfática, em US$/t nominal | `CMO-Historical-Data-Monthly.xlsx`, aba "Monthly Prices", achado na página Commodity Markets | CC BY 4.0 |
| BCB (PTAX) | taxa de câmbio, dólar, venda, média mensal (média simples das PTAX dos dias úteis) | SGS, série 3698 | ODbL |
| Natural Earth v5.1.2 | ponto de rótulo e continente de cada país (1:50m); coordenadas dos portos (1:10m) | GeoJSON, só em desenvolvimento (`python -m src.mapa`) | domínio público |

**Grupos.** 3102 → N, 3103 → P, 3104 → K, 3105 → NPK, exceto DAP (310530) e MAP (310540), que
ficam em P pela convenção de mercado. `TOTAL` soma N, P, K e NPK. Os 42 NCMs (inclusive códigos de
versões antigas da NCM) estão em `data/ncm_fertilizantes.csv`, gerado da tabela auxiliar da própria
API. Enxofre e rocha fosfática formam o grupo `INSUMOS`, com NCMs em `data/ncm_insumos.csv`.

**Mês completo.** Um mês só entra quando está gravado nas cinco séries (fertilizantes, soja,
insumos, Pink Sheet e PTAX). A Pink Sheet e a PTAX são baixadas primeiro, e o Comex Stat só até o
menor mês das duas.

**Revisões.** O MDIC e o BCB podem revisar meses recentes (`--forcar` baixa de novo). O Banco
Mundial revisa meses passados e troca bases de séries: a Pink Sheet é regravada inteira a cada
edição, e o `fonte.json` registra a edição usada (data, URL e sha256).

## Contas básicas

- **Preço implícito:** valor total ÷ toneladas no recorte (média ponderada pelo peso), em US$/t.
  Não é o preço de um contrato; células com poucas toneladas podem ter preços extremos.
- **Share:** participação nas toneladas do ano e do grupo (ou do produto).
- **Variação sobre o ano anterior:** sempre sobre os mesmos meses. Num ano parcial (`n_meses` < 12),
  a base é o mesmo trecho do ano anterior; quem importou no ano anterior e parou aparece com zero.
- **HHI (Herfindahl-Hirschman):** soma dos quadrados dos shares por país de origem, em %, de 0 a
  10.000.
- **Sazonalidade:** média de toneladas de cada mês do calendário nos anos completos; índice sazonal
  = média do mês ÷ média dos 12 meses × 100.
- **Valores em reais:** só pela PTAX venda média do mês, não pelo câmbio de cada declaração (que o
  Comex Stat não publica).

## Cortes

| Corte | Valor | Onde vale |
| --- | --- | --- |
| Amostra pequena de fertilizante (`comparacao.CORTE_AMOSTRA_T`) | 10 mil t do produto no mês | benchmark, custo por nutriente e custo de insumo: o mês fica marcado e fora dos gráficos e das frases (um navio decide o preço), mas continua no CSV |
| Amostra pequena de insumo (`INSUMOS_CORTE_AMOSTRA_T`) | 30 mil t de enxofre ou de rocha no mês | fora das frases, das médias e dos sinais; o spread da rocha fica vazio |
| Rota relevante (`transform.CORTE_ROTA_T`) | 50 mil t no ano, cerca de um navio Supramax; proporcional aos meses num ano parcial | frete por rota (país de origem → URF); abaixo disso o frete por tonelada é ruidoso (cargas pequenas, contêiner, aéreas). Todas as rotas ficam no `rotas_ano.csv`, com a coluna `relevante` |
| Origem no bloco do mapa (`mapa.MINIMO_ORIGEM_T`) | 1.000 t no ano e grupo | a origem menor vai para "outros" |
| Origem por produto (`transform.MINIMO_ORIGEM_PRODUTO_T`) | 1.000 t no ano | no bloco `origens_produto` (só os 3 anos mais recentes); o CSV tem todas |
| Top do `dashboard.json` | 10 origens e 10 URFs por ano e grupo; 7 de cada lado e 2% no diagrama de rotas; 20 rotas relevantes | o resto entra em "Outros" |

## Estados e portos

- A UF do Comex Stat na importação é a **UF de destino da mercadoria**, qualquer que seja a sede do
  importador, e não a UF do porto (`share_uf_ano.csv`).
- A URF é a unidade da Receita onde a carga foi desembaraçada: quase sempre o porto de chegada, mas
  pode ser um porto seco ou uma unidade no interior. Os códigos de URF mudam com reorganizações da
  Receita; em séries longas, agrupe por Região Fiscal (os dois primeiros dígitos).
- Continentes seguem a classificação do Natural Earth: a Rússia entra na Europa; o México, a América
  Central e o Caribe, na "América do Norte e Central".

## Relação de troca no porto

```text
relação de troca = preço CIF do fertilizante (US$/t) ÷ preço FOB da soja exportada (US$/t), no mesmo mês
```

Produtos: KCl (31042090), ureia (31021010) e MAP (31054000), contra a soja em grão exportada
(12019000). As sacas são de 60 kg. A média histórica de referência é a média simples das relações
mensais de toda a série.

**É uma relação "no porto", não o preço ao produtor.** Compara a soja no embarque (FOB) com o
fertilizante no desembarque (CIF). Ficam de fora o frete interno nos dois sentidos, impostos,
armazenagem, margens da revenda e das tradings, prêmios de porto e o descasamento entre a compra do
adubo e a venda da safra. A relação é US$/US$ e **não muda com o câmbio**: não existe "troca em R$".

## Custo por nutriente

```text
custo do nutriente (US$/t)    = CIF do produto (US$/t) ÷ teor do nutriente
MAP e DAP (P₂O₅)              = (CIF − teor de N × custo do N da ureia no mês) ÷ teor de P₂O₅
custo por ponto (MAP e DAP)   = CIF ÷ (teor de N + teor de P₂O₅)
em reais (R$/t)               = custo em US$ × PTAX venda média do mês
```

| Produto | NCM | Teor usado |
| --- | --- | --- |
| Ureia | 31021010 | 46% de N |
| Sulfato de amônio | 31022100 | 21% de N |
| Nitrato de amônio | 31023000 | 34% de N |
| MAP | 31054000 | 11% de N e 52% de P₂O₅ (com crédito de N) |
| DAP | 31053000, 31053010, 31053090 | 18% de N e 46% de P₂O₅ (com crédito de N) |
| TSP | 31031030, 31031100 | 46% de P₂O₅ |
| KCl | 31042090 | 60% de K₂O |

Os teores são o grau comercial usual, porque o Comex Stat não traz o teor de cada carga. O crédito
de N desconta do MAP e do DAP o N que eles levam, pelo custo do N da ureia no mesmo mês; o CSV traz
também o custo sem o desconto. **É no porto (CIF), antes de impostos, frete interno e margens: não é
o preço ao produtor.**

## Brasil x mercado internacional (benchmark)

| Produto | NCM | Série da Pink Sheet | Base do benchmark | Comparação |
| --- | --- | --- | --- | --- |
| KCl | 31042090 | Potassium chloride | FOB Vancouver até 2019-12; CFR Brasil, granulado, desde 2020-01 | FOB×FOB até 2019-12; CIF×CFR desde 2020-01 |
| Ureia | 31021010 | Urea | FOB Mar Negro até 2022-02; FOB Oriente Médio desde 2022-03 | FOB×FOB |
| MAP | 31054000 | DAP, por aproximação (a Pink Sheet não tem MAP) | FOB Golfo dos EUA | FOB×FOB |
| DAP | 31053000, 31053010, 31053090 | DAP | FOB Golfo dos EUA | FOB×FOB |
| TSP | 31031030, 31031100 | TSP | importação no Golfo dos EUA (base de 2015 a 2017 não confirmada) | CIF×CFR |

```text
spread comparável (US$/t) = FOB Brasil − benchmark (FOB×FOB) ou CIF Brasil − benchmark (CIF×CFR)
spread comparável (%)     = spread comparável ÷ benchmark × 100
custo posto (US$/t)       = CIF Brasil − benchmark, em qualquer base
CIF em reais (R$/t)       = CIF Brasil × PTAX venda média do mês
```

**O spread não é ágio.** O benchmark é o preço num porto de referência ou no destino, num momento
de contrato diferente; o spread mistura origem, frete até o ponto de referência, prazo de contrato e
a defasagem entre o fechamento do negócio e o desembarque registrado no Comex Stat. Por isso o
spread vai sempre com o preço do Brasil na mesma base, e só se compara de um ano para outro quando a
base da série é a mesma (o CSV marca a troca de base na coluna `quebra`). O benchmark nunca é
apresentado como preço do Brasil.

Os blocos `benchmark` e `troca` do `dashboard.json` levam 6 casas, para que quem lê arredonde uma
vez só, meio para cima, e o sinal saia do número já arredondado (nunca "−0,0").

## Insumos do fósforo

Enxofre (2503) e rocha fosfática (2510) ficam em `data/raw_insumos/` e **nunca entram nos totais,
shares, mapa, rotas ou estados de fertilizantes**: o transform recusa NCM 2503 ou 2510 em
`data/raw/`, e um teste confere que os totais somam só os NCMs de `data/ncm_fertilizantes.csv`.

- **Rocha x Pink Sheet:** FOB da rocha importada contra a série Phosphate rock (FOB Norte da
  África), FOB×FOB. O spread não é ágio e vai com o FOB do Brasil.
- **Custo de insumo por tonelada de MAP:**

  ```text
  custo de insumo (US$/t de MAP) = CIF do enxofre × 0,45 + CIF da rocha fosfática × 1,7
  razão                          = custo de insumo ÷ CIF do MAP importado (31054000) no mesmo mês
  ```

  Os coeficientes (`INSUMOS_COEF_ENXOFRE` e `INSUMOS_COEF_ROCHA`) são uma aproximação técnica das
  toneladas de cada insumo por tonelada de MAP 11-52, explicada em `src/config.py`. **É uma
  aproximação, não o custo de nenhuma empresa:** ficam de fora o nitrogênio do MAP, a energia, a
  conversão, os impostos e o frete interno. É no porto, não o preço ao produtor.

## Sinais de preço e de volume

`src/sinais.py` lê o `dashboard.json` e grava em `data/sinais.json` os sinais de cada produto, mês a
mês, desde o início da série. São regras fixas em Python, **sem IA**, e **sem olhar o futuro**: cada
mês só usa os dados até ele. Os limites ficam em `src/config.py` (`SINAIS_*`) e voltam no campo
`limites` do arquivo.

Produtos: `ureia`, `sulfato_amonio`, `kcl`, `map`, `dap` e `tsp` (os NCMs do custo por nutriente),
`npk` (o grupo inteiro), `enxofre` e `rocha`.

**Mês válido para preço:** pelo menos 20 mil t do produto no mês (40 mil t para enxofre e rocha, que
chegam em poucos navios grandes), CIF presente e fora da amostra pequena. Cada mês das janelas de
comparação passa pela mesma regra; mês sem dado (null) não é zero.

| Tipo | Dispara quando | Forte quando |
| --- | --- | --- |
| `media_12m` | CIF do mês 20% ou mais acima ou abaixo da média simples dos 12 meses anteriores (pelo menos 9 válidos) | 40% ou mais |
| `variacao_3m` | CIF 15% ou mais acima ou abaixo do de 3 meses antes (os dois válidos) | 30% ou mais |
| `recorde` | CIF acima do maior (ou abaixo do menor) de todos os meses válidos anteriores, depois de 36 deles | passa o recorde anterior por 5% ou mais |
| `internacional` | Pink Sheet 10% ou mais acima ou abaixo de 2 meses antes, sem troca de base, e o CIF do Brasil andou no mesmo sentido menos da metade disso | Pink Sheet 20% ou mais |
| `troca_p90` | troca no porto (KCl, ureia e MAP) acima do percentil 90 dos meses válidos anteriores, depois de 36 deles | acima do percentil 97,5 |
| `ritmo_importacao` | toneladas do mês 25% ou mais acima ou abaixo das do mesmo mês do ano anterior, que precisa ter o volume mínimo | 50% ou mais |

- **Arredondamento:** a variação é comparada com o limite já arredondada como a frase a mostra
  (inteiro, meio para cima; na troca, 2 casas). Médias com `math.fsum`.
- **Pink Sheet:** o MAP usa o DAP como aproximação; sulfato de amônio, NPK e enxofre não têm série.
- **Troca:** sempre "no porto", nunca em R$; a soja exportada do mês também precisa do volume mínimo.
- O histórico inteiro é recalculado a cada atualização: uma revisão das fontes ou um limite novo pode
  criar, mudar ou apagar o sinal de um mês passado. O `id` (`AAAA-MM/produto/tipo`) não muda.

O formato do arquivo (versão 1) está em [DADOS.md](DADOS.md#formato-do-datasinaisjson-versão-1).

## Marcos de mercado

`data/eventos.yml` guarda eventos escolhidos à mão pelo mantenedor, cada um com data, título, fonte
(`https://`, em minúsculas) e os produtos citados (as chaves dos sinais). `src/eventos.py` lê um
subconjunto estrito do YAML, só com a biblioteca padrão, e recusa qualquer coisa fora dele
(`python -m src.eventos` confere). **O marco é uma anotação, não um dado oficial: ele marca o mês do
evento e não diz que causou a variação.**

## Limitações

- **Preço implícito é média** de todas as declarações do mês, que somam especificações e contratos
  diferentes no mesmo NCM.
- **MAP pelo DAP** no benchmark: produtos próximos, mas não iguais.
- **Bases trocadas retroativamente** pelo Banco Mundial (KCl desde 2020 para CFR Brasil; ureia para o
  Oriente Médio desde 2022-03). A série guardada é sempre a da edição mais recente.
- **Câmbio pela PTAX média do mês**, não o da data de cada declaração: serve para dimensionar o preço
  em reais, não como custo contábil.
- **Consultas de vários anos:** a API do Comex Stat soma em cada ano só os meses do intervalo; por
  isso a ingestão consulta um ano por vez.
