# Dados

Dicionário de campos dos arquivos de `data/`, o que o pipeline do Graaos Open grava e versiona. O
método e os cortes estão em [METODOLOGIA.md](METODOLOGIA.md).

Licença dos dados tratados: [CC BY 4.0](data/LICENSE), com o crédito
**"Graaos (github.com/mvsantos-dev/Graaos-Open)"**. Os dados de origem seguem as licenças das
fontes (README, "Licenças das fontes").

Fonte: Comex Stat/MDIC; Banco Mundial (Pink Sheet); BCB/PTAX.

Convenções:

- CSV em UTF-8, separador vírgula, ponto decimal, fim de linha `\n`; campo vazio = sem valor.
- Códigos (`co_pais`, `co_urf`, `co_ncm`) são texto, com os zeros à esquerda.
- Os Parquet são particionados por ano no estilo Hive (`ano=AAAA/`): a coluna `ano` fica no
  caminho, não dentro do arquivo. Leia com `src.ingest.ler_raw()`, `ler_soja()` e `ler_insumos()`.
- Todo arquivo de `data/processed/` sai do `python -m src.transform`, de forma determinística.

## Arquivos CSV

### `data/processed/precos_mes_grupo.csv`

Toneladas, valores e preços implícitos FOB e CIF e frete por tonelada, por mês e grupo, somando todas as origens.

| Coluna | Descrição |
| --- | --- |
| `periodo` | Mês dos dados, no formato AAAA-MM. |
| `ano` | Ano dos dados. |
| `mes` | Mês do ano (1 a 12). |
| `toneladas` | Toneladas importadas (peso líquido). |
| `vl_fob` | Valor FOB, em US$: a carga embarcada no porto de origem, sem o frete nem o seguro internacionais. |
| `vl_cif` | Valor CIF, em US$: FOB mais frete e seguro internacionais, no porto brasileiro. |
| `vl_frete` | Frete internacional, em US$. |
| `preco_fob_usd_t` | Preço implícito FOB: valor FOB ÷ toneladas, em US$/t (média ponderada pelo peso, não o preço de um contrato). |
| `preco_cif_usd_t` | Preço implícito CIF: valor CIF ÷ toneladas, em US$/t. |
| `frete_usd_t` | Frete internacional ÷ toneladas, em US$/t. |
| `grupo` | Grupo de fertilizantes: N, P, K ou NPK (sem linha TOTAL: o total é a soma dos quatro). |

### `data/processed/precos_mes_grupo_origem.csv`

O mesmo por mês, grupo e país de origem.

| Coluna | Descrição |
| --- | --- |
| `periodo` | Mês dos dados, no formato AAAA-MM. |
| `ano` | Ano dos dados. |
| `mes` | Mês do ano (1 a 12). |
| `co_pais` | Código do país de origem no Comex Stat (texto, com os zeros à esquerda). |
| `no_pais` | Nome do país de origem, como o Comex Stat o escreve. |
| `toneladas` | Toneladas importadas (peso líquido). |
| `vl_fob` | Valor FOB, em US$: a carga embarcada no porto de origem, sem o frete nem o seguro internacionais. |
| `vl_cif` | Valor CIF, em US$: FOB mais frete e seguro internacionais, no porto brasileiro. |
| `vl_frete` | Frete internacional, em US$. |
| `preco_fob_usd_t` | Preço implícito FOB: valor FOB ÷ toneladas, em US$/t (média ponderada pelo peso, não o preço de um contrato). |
| `preco_cif_usd_t` | Preço implícito CIF: valor CIF ÷ toneladas, em US$/t. |
| `frete_usd_t` | Frete internacional ÷ toneladas, em US$/t. |
| `grupo` | Grupo de fertilizantes: N, P, K ou NPK (sem linha TOTAL: o total é a soma dos quatro). |

### `data/processed/share_origem_ano.csv`

Participação de cada país de origem nas toneladas do ano e do grupo, com a variação sobre os mesmos meses do ano anterior.

| Coluna | Descrição |
| --- | --- |
| `ano` | Ano dos dados. |
| `n_meses` | Meses com dados no ano; menos de 12 é ano parcial, comparado com os mesmos meses do ano anterior. |
| `grupo` | Grupo de fertilizantes: N (nitrogenados), P (fosfatados), K (potássicos), NPK (compostos) ou TOTAL (os quatro somados). |
| `co_pais` | Código do país de origem no Comex Stat (texto, com os zeros à esquerda). |
| `no_pais` | Nome do país de origem, como o Comex Stat o escreve. |
| `toneladas` | Toneladas importadas (peso líquido). |
| `vl_fob` | Valor FOB, em US$: a carga embarcada no porto de origem, sem o frete nem o seguro internacionais. |
| `preco_fob_usd_t` | Preço implícito FOB: valor FOB ÷ toneladas, em US$/t (média ponderada pelo peso, não o preço de um contrato). |
| `share_t_pct_ano_anterior` | A mesma participação, nos mesmos meses do ano anterior, em %. |
| `toneladas_ano_anterior` | Toneladas nos mesmos meses do ano anterior (vazio quando o ano anterior não tem esses meses). |
| `var_t_pct` | Variação das toneladas sobre os mesmos meses do ano anterior, em % (vazia sem base de comparação). |
| `var_share_pp` | Variação da participação sobre os mesmos meses do ano anterior, em pontos percentuais. |
| `share_t_pct` | Participação do país nas toneladas do ano e do grupo, em %. |

### `data/processed/share_origem_produto_ano.csv`

O mesmo por produto acompanhado (ureia, sulfato de amônio, KCl, MAP, DAP, TSP e o grupo NPK), com o FOB e o CIF por tonelada.

| Coluna | Descrição |
| --- | --- |
| `ano` | Ano dos dados. |
| `n_meses` | Meses com dados no ano; menos de 12 é ano parcial, comparado com os mesmos meses do ano anterior. |
| `co_pais` | Código do país de origem no Comex Stat (texto, com os zeros à esquerda). |
| `no_pais` | Nome do país de origem, como o Comex Stat o escreve. |
| `toneladas` | Toneladas importadas (peso líquido). |
| `vl_fob` | Valor FOB, em US$: a carga embarcada no porto de origem, sem o frete nem o seguro internacionais. |
| `vl_cif` | Valor CIF, em US$: FOB mais frete e seguro internacionais, no porto brasileiro. |
| `preco_fob_usd_t` | Preço implícito FOB: valor FOB ÷ toneladas, em US$/t (média ponderada pelo peso, não o preço de um contrato). |
| `preco_cif_usd_t` | Preço implícito CIF: valor CIF ÷ toneladas, em US$/t. |
| `share_t_pct_ano_anterior` | A mesma participação, nos mesmos meses do ano anterior, em %. |
| `toneladas_ano_anterior` | Toneladas nos mesmos meses do ano anterior (vazio quando o ano anterior não tem esses meses). |
| `var_t_pct` | Variação das toneladas sobre os mesmos meses do ano anterior, em % (vazia sem base de comparação). |
| `var_share_pp` | Variação da participação sobre os mesmos meses do ano anterior, em pontos percentuais. |
| `produto` | Produto: ureia, sulfato_amonio, kcl, map, dap, tsp ou npk (as chaves dos sinais; npk é o grupo NPK inteiro). |
| `share_t_pct` | Participação do país nas toneladas do ano e do produto, em %. |

### `data/processed/share_urf_ano.csv`

Participação de cada URF (o porto de chegada, na prática) nas toneladas do ano e do grupo.

| Coluna | Descrição |
| --- | --- |
| `ano` | Ano dos dados. |
| `n_meses` | Meses com dados no ano; menos de 12 é ano parcial, comparado com os mesmos meses do ano anterior. |
| `grupo` | Grupo de fertilizantes: N (nitrogenados), P (fosfatados), K (potássicos), NPK (compostos) ou TOTAL (os quatro somados). |
| `co_urf` | Código da URF de desembaraço: a unidade da Receita Federal onde a carga é desembaraçada, na prática o porto de chegada (texto, com os zeros à esquerda). |
| `no_urf` | Nome da URF de desembaraço, como o Comex Stat o escreve. |
| `toneladas` | Toneladas importadas (peso líquido). |
| `vl_fob` | Valor FOB, em US$: a carga embarcada no porto de origem, sem o frete nem o seguro internacionais. |
| `preco_fob_usd_t` | Preço implícito FOB: valor FOB ÷ toneladas, em US$/t (média ponderada pelo peso, não o preço de um contrato). |
| `share_t_pct_ano_anterior` | A mesma participação, nos mesmos meses do ano anterior, em %. |
| `toneladas_ano_anterior` | Toneladas nos mesmos meses do ano anterior (vazio quando o ano anterior não tem esses meses). |
| `var_t_pct` | Variação das toneladas sobre os mesmos meses do ano anterior, em % (vazia sem base de comparação). |
| `var_share_pp` | Variação da participação sobre os mesmos meses do ano anterior, em pontos percentuais. |
| `share_t_pct` | Participação da URF nas toneladas do ano e do grupo, em %. |

### `data/processed/share_uf_ano.csv`

Participação de cada UF de destino da mercadoria nas toneladas do ano e do grupo.

| Coluna | Descrição |
| --- | --- |
| `ano` | Ano dos dados. |
| `n_meses` | Meses com dados no ano; menos de 12 é ano parcial, comparado com os mesmos meses do ano anterior. |
| `grupo` | Grupo de fertilizantes: N (nitrogenados), P (fosfatados), K (potássicos), NPK (compostos) ou TOTAL (os quatro somados). |
| `toneladas` | Toneladas importadas (peso líquido). |
| `vl_fob` | Valor FOB, em US$: a carga embarcada no porto de origem, sem o frete nem o seguro internacionais. |
| `preco_fob_usd_t` | Preço implícito FOB: valor FOB ÷ toneladas, em US$/t (média ponderada pelo peso, não o preço de um contrato). |
| `share_t_pct_ano_anterior` | A mesma participação, nos mesmos meses do ano anterior, em %. |
| `toneladas_ano_anterior` | Toneladas nos mesmos meses do ano anterior (vazio quando o ano anterior não tem esses meses). |
| `var_t_pct` | Variação das toneladas sobre os mesmos meses do ano anterior, em % (vazia sem base de comparação). |
| `var_share_pp` | Variação da participação sobre os mesmos meses do ano anterior, em pontos percentuais. |
| `sg_uf` | Sigla da UF de destino da mercadoria: na importação, a UF do Comex Stat é a de destino, qualquer que seja a sede do importador, e não a do porto. |
| `no_uf` | Nome da UF de destino. |
| `share_t_pct` | Participação da UF de destino nas toneladas do ano e do grupo, em %. |

### `data/processed/hhi_ano_grupo.csv`

Concentração dos fornecedores por ano e grupo: HHI, número de países de origem, país líder e CR3.

| Coluna | Descrição |
| --- | --- |
| `ano` | Ano dos dados. |
| `n_meses` | Meses com dados no ano; menos de 12 é ano parcial, comparado com os mesmos meses do ano anterior. |
| `grupo` | Grupo de fertilizantes: N (nitrogenados), P (fosfatados), K (potássicos), NPK (compostos) ou TOTAL (os quatro somados). |
| `toneladas` | Toneladas importadas no ano e no grupo. |
| `n_origens` | Países de origem com carga no ano e no grupo. |
| `hhi` | Índice Herfindahl-Hirschman: soma dos quadrados das participações (em %) dos países de origem, de 0 a 10.000. |
| `lider_co_pais` | Código do maior país de origem no Comex Stat. |
| `lider_no_pais` | Nome do maior país de origem. |
| `lider_share_pct` | Participação do maior país de origem, em %. |
| `cr3_pct` | Participação somada dos três maiores países de origem, em %. |

### `data/processed/sazonalidade_grupo.csv`

Média de toneladas de cada mês do calendário, por grupo, nos anos completos, e o índice sazonal.

| Coluna | Descrição |
| --- | --- |
| `grupo` | Grupo de fertilizantes: N (nitrogenados), P (fosfatados), K (potássicos), NPK (compostos) ou TOTAL (os quatro somados). |
| `mes` | Mês do calendário (1 a 12). |
| `toneladas_media` | Média das toneladas importadas no mês, nos anos completos. |
| `indice_sazonal` | Média do mês ÷ média dos 12 meses × 100 (100 = um mês típico). |
| `n_anos` | Anos completos na média. |
| `ano_inicial` | Primeiro ano completo da média. |
| `ano_final` | Último ano completo da média. |

### `data/processed/rotas_ano.csv`

Rotas (país de origem → URF) por ano e grupo: toneladas, valores, frete por tonelada e se a rota passa do corte de volume relevante.

| Coluna | Descrição |
| --- | --- |
| `ano` | Ano dos dados. |
| `n_meses` | Meses com dados no ano; menos de 12 é ano parcial, comparado com os mesmos meses do ano anterior. |
| `grupo` | Grupo de fertilizantes: N (nitrogenados), P (fosfatados), K (potássicos), NPK (compostos) ou TOTAL (os quatro somados). |
| `co_pais` | Código do país de origem no Comex Stat (texto, com os zeros à esquerda). |
| `no_pais` | Nome do país de origem, como o Comex Stat o escreve. |
| `co_urf` | Código da URF de desembaraço: a unidade da Receita Federal onde a carga é desembaraçada, na prática o porto de chegada (texto, com os zeros à esquerda). |
| `no_urf` | Nome da URF de desembaraço, como o Comex Stat o escreve. |
| `toneladas` | Toneladas importadas (peso líquido). |
| `vl_fob` | Valor FOB, em US$: a carga embarcada no porto de origem, sem o frete nem o seguro internacionais. |
| `vl_cif` | Valor CIF, em US$: FOB mais frete e seguro internacionais, no porto brasileiro. |
| `vl_frete` | Frete internacional, em US$. |
| `frete_usd_t` | Frete internacional ÷ toneladas, em US$/t. |
| `meses` | Meses do ano com carga na rota. |
| `frete_pct_cif` | Frete ÷ valor CIF, em %. |
| `share_t_pct` | Participação da rota nas toneladas do ano e do grupo, em %. |
| `corte_t` | Corte de volume relevante do ano, em toneladas (proporcional aos meses com dados num ano parcial). |
| `relevante` | Verdadeiro quando a rota tem pelo menos corte_t toneladas no ano: só essas entram na tabela de frete por rota. |

### `data/processed/troca_mensal.csv`

Relação de troca no porto, mês a mês, de KCl, ureia e MAP com a soja em grão exportada. Não é o preço ao produtor.

| Coluna | Descrição |
| --- | --- |
| `periodo` | Mês dos dados, no formato AAAA-MM. |
| `ano` | Ano dos dados. |
| `mes` | Mês do ano (1 a 12). |
| `produto` | Fertilizante: kcl, ureia ou map. |
| `co_ncm` | NCM do fertilizante. |
| `toneladas_fert` | Toneladas do fertilizante importadas no mês. |
| `vl_cif_fert` | Valor CIF do fertilizante, em US$. |
| `preco_cif_fert_usd_t` | Preço implícito CIF do fertilizante, em US$/t. |
| `toneladas_soja` | Toneladas de soja em grão exportadas no mês. |
| `vl_fob_soja` | Valor FOB da soja exportada, em US$. |
| `preco_fob_soja_usd_t` | Preço implícito FOB da soja exportada, em US$/t. |
| `t_soja_por_t` | Relação de troca no porto: toneladas de soja que pagam 1 t do fertilizante (CIF do fertilizante ÷ FOB da soja). É US$/US$ e não muda com o câmbio. Não é o preço ao produtor. |
| `sacas_soja_por_t` | A mesma relação em sacas de soja de {kg_saca} kg. |

### `data/processed/benchmark_mensal.csv`

Brasil x mercado internacional, mês a mês: FOB e CIF do Brasil contra a Pink Sheet do Banco Mundial, spread na base comparável e CIF em reais pela PTAX venda média do mês.

| Coluna | Descrição |
| --- | --- |
| `periodo` | Mês dos dados, no formato AAAA-MM. |
| `ano` | Ano dos dados. |
| `mes` | Mês do ano (1 a 12). |
| `ncms` | NCMs somados no produto, separados por \|. |
| `toneladas` | Toneladas importadas (peso líquido). |
| `amostra_pequena` | Verdadeiro no mês com volume abaixo do corte de amostra pequena (um navio decide o preço; o corte está na metodologia): o mês fica fora dos gráficos e das frases e continua no arquivo. |
| `ptax_brl_usd` | PTAX venda média do mês, em R$ por US$ (BCB, SGS 3698). |
| `produto` | Produto: kcl, ureia, map, dap ou tsp. |
| `grupo` | Grupo do produto (N, P ou K). |
| `serie_bm` | Série da Pink Sheet comparada (o MAP usa a do DAP). |
| `base_bm` | Base do benchmark no mês: o porto e a condição do preço de referência. |
| `comparacao` | Base comparável: FOB×FOB (benchmark FOB, contra o FOB do Brasil) ou CIF×CFR (benchmark no destino, contra o CIF do Brasil). |
| `quebra` | Verdadeiro no mês em que o Banco Mundial trocou a base da série. |
| `proxy` | Verdadeiro quando o benchmark é de outro produto: o MAP usa o DAP, porque a Pink Sheet não tem série de MAP. |
| `fob_brasil_usd_t` | Preço implícito FOB do Brasil, em US$/t. |
| `cif_brasil_usd_t` | Preço implícito CIF do Brasil, em US$/t. |
| `benchmark_usd_t` | Preço da Pink Sheet no mês, em US$/t nominais: referência de outro lugar e de outro momento de contrato, não um preço do Brasil. |
| `spread_fob_usd_t` | FOB do Brasil − benchmark, em US$/t, só na base FOB×FOB. |
| `spread_fob_pct` | O mesmo spread ÷ benchmark, em %. |
| `custo_posto_usd_t` | CIF do Brasil − benchmark, em US$/t, em qualquer base. |
| `custo_posto_pct` | O mesmo ÷ benchmark, em %. |
| `spread_usd_t` | Spread na base comparável, em US$/t: FOB do Brasil − benchmark em FOB×FOB; CIF do Brasil − benchmark em CIF×CFR. Não é ágio: o benchmark é de outro lugar e de outro momento de contrato. |
| `spread_pct` | O spread na base comparável ÷ benchmark, em %. |
| `cif_brl_t` | CIF do Brasil em reais por tonelada, pela PTAX venda média do mês. |

### `data/processed/custo_nutriente_mensal.csv`

Custo por tonelada de nutriente (N, P₂O₅ ou K₂O) no porto, mês a mês, com o crédito de N no MAP e no DAP e em reais pela PTAX venda média do mês. Não é o preço ao produtor.

| Coluna | Descrição |
| --- | --- |
| `periodo` | Mês dos dados, no formato AAAA-MM. |
| `ano` | Ano dos dados. |
| `mes` | Mês do ano (1 a 12). |
| `ncms` | NCMs somados no produto, separados por \|. |
| `toneladas` | Toneladas importadas (peso líquido). |
| `amostra_pequena` | Verdadeiro no mês com volume abaixo do corte de amostra pequena (um navio decide o preço; o corte está na metodologia): o mês fica fora dos gráficos e das frases e continua no arquivo. |
| `ptax_brl_usd` | PTAX venda média do mês, em R$ por US$ (BCB, SGS 3698). |
| `produto` | Produto: ureia, sulfato_amonio, nitrato_amonio, map, dap, tsp ou kcl. |
| `nutriente` | Nutriente principal: N, P2O5 ou K2O. |
| `teor_n_pct` | Teor de N usado, em %: o grau comercial usual (o Comex Stat não traz o teor de cada carga). |
| `teor_p2o5_pct` | Teor de P₂O₅ usado, em %. |
| `teor_k2o_pct` | Teor de K₂O usado, em %. |
| `fob_usd_t` | Preço implícito FOB do produto, em US$/t. |
| `cif_usd_t` | Preço implícito CIF do produto, em US$/t. |
| `custo_sem_credito_usd_t` | CIF ÷ teor do nutriente principal, em US$ por tonelada de nutriente, sem o crédito de N. |
| `custo_n_ureia_usd_t` | Custo do N na ureia no mesmo mês (CIF da ureia ÷ teor de N), em US$ por tonelada de N: a base do crédito de N. |
| `credito_n_usd_t` | No MAP e no DAP, o valor do N que vem junto (teor de N × custo do N na ureia), em US$ por tonelada de produto. |
| `custo_nutriente_usd_t` | Custo por tonelada do nutriente principal no porto, em US$ (no MAP e no DAP, com o crédito de N). Não é o preço ao produtor. |
| `custo_ponto_usd_t` | CIF ÷ soma dos teores (N + P₂O₅ + K₂O), em US$ por tonelada de nutriente somado. |
| `custo_nutriente_brl_t` | Custo do nutriente em reais por tonelada, pela PTAX venda média do mês. |

### `data/processed/insumos_mensal.csv`

Enxofre e rocha fosfática importados, mês a mês: toneladas, valores, preços por tonelada e, na rocha, a Pink Sheet e o spread FOB×FOB.

| Coluna | Descrição |
| --- | --- |
| `periodo` | Mês dos dados, no formato AAAA-MM. |
| `ano` | Ano dos dados. |
| `mes` | Mês do ano (1 a 12). |
| `ncms` | NCMs somados no produto, separados por \|. |
| `toneladas` | Toneladas importadas (peso líquido). |
| `vl_fob` | Valor FOB, em US$: a carga embarcada no porto de origem, sem o frete nem o seguro internacionais. |
| `vl_cif` | Valor CIF, em US$: FOB mais frete e seguro internacionais, no porto brasileiro. |
| `vl_frete` | Frete internacional, em US$. |
| `preco_fob_usd_t` | Preço implícito FOB: valor FOB ÷ toneladas, em US$/t (média ponderada pelo peso, não o preço de um contrato). |
| `preco_cif_usd_t` | Preço implícito CIF: valor CIF ÷ toneladas, em US$/t. |
| `frete_usd_t` | Frete internacional ÷ toneladas, em US$/t. |
| `amostra_pequena` | Verdadeiro no mês com volume abaixo do corte de amostra pequena do insumo (o corte está na metodologia): o mês fica fora das frases, das médias e dos sinais e, no gráfico do painel, aparece como ponto vazado; continua no arquivo. |
| `produto` | Insumo: enxofre ou rocha. |
| `serie_bm` | Série da Pink Sheet comparada (só na rocha). |
| `base_bm` | Base do benchmark (só na rocha). |
| `comparacao` | Base comparável (só na rocha: FOB×FOB). |
| `benchmark_usd_t` | Preço da Pink Sheet no mês, em US$/t nominais (só na rocha). |
| `spread_usd_t` | FOB da rocha importada − Pink Sheet, em US$/t; vazio na amostra pequena. Não é ágio: o benchmark é de outro lugar e de outro momento de contrato. |
| `spread_pct` | O spread ÷ Pink Sheet, em %. |

### `data/processed/custo_insumo_map_mensal.csv`

Custo de insumo por tonelada de MAP no porto (enxofre e rocha fosfática importados), mês a mês: uma aproximação, não o custo de nenhuma empresa nem o preço ao produtor.

| Coluna | Descrição |
| --- | --- |
| `periodo` | Mês dos dados, no formato AAAA-MM. |
| `ano` | Ano dos dados. |
| `mes` | Mês do ano (1 a 12). |
| `coef_enxofre` | Toneladas de enxofre por tonelada de MAP (aproximação técnica). |
| `coef_rocha` | Toneladas de rocha fosfática por tonelada de MAP (aproximação técnica). |
| `toneladas_enxofre` | Toneladas de enxofre importadas no mês. |
| `cif_enxofre_usd_t` | CIF do enxofre importado, em US$/t. |
| `toneladas_rocha` | Toneladas de rocha fosfática importadas no mês. |
| `cif_rocha_usd_t` | CIF da rocha fosfática importada, em US$/t. |
| `toneladas_map` | Toneladas de MAP importadas no mês. |
| `cif_map_usd_t` | CIF do MAP importado, em US$/t. |
| `custo_enxofre_usd_t` | CIF do enxofre × coef_enxofre, em US$ por tonelada de MAP. |
| `custo_rocha_usd_t` | CIF da rocha × coef_rocha, em US$ por tonelada de MAP. |
| `custo_insumo_usd_t` | Custo de insumo por tonelada de MAP no porto (a soma dos dois), em US$: uma aproximação, não o custo de nenhuma empresa. Não é o preço ao produtor. |
| `razao_custo_cif_map` | Custo de insumo ÷ CIF do MAP importado no mesmo mês. |
| `amostra_pequena_enxofre` | Verdadeiro quando o enxofre ficou abaixo do corte de amostra pequena no mês. |
| `amostra_pequena_rocha` | Verdadeiro quando a rocha fosfática ficou abaixo do corte de amostra pequena no mês. |
| `amostra_pequena_map` | Verdadeiro quando o MAP ficou abaixo do corte de amostra pequena no mês. |
| `amostra_pequena` | Verdadeiro quando qualquer um dos três está em amostra pequena: o custo do mês fica marcado e fora das frases e das médias. |

### `data/raw_benchmark/pink_sheet_mensal.csv`

Preços mensais de fertilizantes da Pink Sheet do Banco Mundial, em US$/t nominais, da edição mais recente (o Banco Mundial revisa meses passados).

| Coluna | Descrição |
| --- | --- |
| `mes` | Mês, no formato AAAA-MM. |
| `ureia` | Ureia (série Urea); a base de cada mês está em base_bm do benchmark_mensal.csv. |
| `dap` | DAP (série DAP, FOB Golfo dos EUA); também a referência do MAP. |
| `tsp` | Superfosfato triplo (série TSP). |
| `kcl` | Cloreto de potássio (série Potassium chloride); a base de cada mês está em base_bm do benchmark_mensal.csv. |
| `rocha_fosfatica` | Rocha fosfática (série Phosphate rock, FOB Norte da África). |

### `data/raw_cambio/ptax_venda_media_mensal.csv`

PTAX de venda, média mensal, do Banco Central do Brasil (SGS 3698).

| Coluna | Descrição |
| --- | --- |
| `mes` | Mês, no formato AAAA-MM. |
| `brl_por_usd` | Reais por dólar: a média simples da PTAX de venda nos dias úteis do mês. |

### `data/ncm_fertilizantes.csv`

Os NCMs de fertilizantes acompanhados e o grupo de cada um.

| Coluna | Descrição |
| --- | --- |
| `ncm` | Código NCM (8 dígitos). |
| `descricao` | Descrição oficial do NCM. |
| `grupo` | Grupo: N, P, K ou NPK (o DAP e o MAP ficam em P). |
| `sh4` | Posição do Sistema Harmonizado (4 dígitos). |
| `sh6` | Subposição do Sistema Harmonizado (6 dígitos). |

### `data/ncm_insumos.csv`

Os NCMs de enxofre e de rocha fosfática, os insumos do fósforo, guardados à parte: nunca entram nos totais de fertilizantes.

| Coluna | Descrição |
| --- | --- |
| `ncm` | Código NCM (8 dígitos). |
| `descricao` | Descrição oficial do NCM. |
| `grupo` | INSUMOS (fora dos totais de fertilizantes). |
| `sh4` | Posição do Sistema Harmonizado (4 dígitos). |
| `sh6` | Subposição do Sistema Harmonizado (6 dígitos). |

### `data/ref/paises_iso.csv`

Código do país no Comex Stat → código ISO, ponto de rótulo e continente, para o mapa de fluxos.

| Coluna | Descrição |
| --- | --- |
| `co_pais` | Código do país de origem no Comex Stat (texto, com os zeros à esquerda). |
| `no_pais` | Nome do país de origem, como o Comex Stat o escreve. |
| `iso3` | Código ISO 3166-1 alfa-3 do país. |
| `lon` | Longitude do ponto de rótulo do país (Natural Earth), em graus. |
| `lat` | Latitude do ponto de rótulo do país (Natural Earth), em graus. |
| `continente` | Continente pela classificação do Natural Earth, em código: a Rússia entra na Europa; o México, a América Central e o Caribe, na América do Norte e Central. |
| `fonte` | De onde vêm o código ISO e as coordenadas. |

### `data/ref/urf_coordenadas.csv`

URF → porto, UF e coordenadas, para o mapa de fluxos.

| Coluna | Descrição |
| --- | --- |
| `co_urf` | Código da URF de desembaraço: a unidade da Receita Federal onde a carga é desembaraçada, na prática o porto de chegada (texto, com os zeros à esquerda). |
| `no_urf` | Nome da URF de desembaraço, como o Comex Stat o escreve. |
| `lon` | Longitude, em graus. |
| `lat` | Latitude, em graus. |
| `porto` | Nome do porto (ou do lugar) da URF, como o mapa o mostra. |
| `uf` | UF onde fica a URF (não é a UF de destino da mercadoria). |
| `local_ne` | Lugar do Natural Earth usado para a coordenada. |
| `fonte` | De onde vem a coordenada. |
| `observacao` | Observação sobre o lugar (fronteira, porto seco etc.). |

## Dados brutos (Parquet)

### Importações de fertilizantes: `data/raw/ano=AAAA/importacoes.parquet`

Uma linha por mês, NCM, país de origem, UF de destino, via e URF, com FOB, peso, CIF, frete e seguro: a base de todas as tabelas. Só os NCMs de ncm_fertilizantes.csv.

| Coluna | Descrição |
| --- | --- |
| `mes` | Mês (1 a 12); o ano fica no caminho (ano=AAAA), não dentro do arquivo. |
| `co_ncm` | NCM (8 dígitos). |
| `co_pais` | Código do país de origem no Comex Stat (texto, com os zeros à esquerda). |
| `no_pais` | Nome do país de origem, como o Comex Stat o escreve. |
| `sg_uf` | Sigla da UF do produto: na importação, a UF de destino da mercadoria, qualquer que seja a sede do importador, e não a do porto. |
| `no_uf` | Nome da UF de destino. |
| `co_via` | Código da via de transporte. |
| `no_via` | Nome da via de transporte. |
| `co_urf` | Código da URF de desembaraço: a unidade da Receita Federal onde a carga é desembaraçada, na prática o porto de chegada (texto, com os zeros à esquerda). |
| `no_urf` | Nome da URF de desembaraço, como o Comex Stat o escreve. |
| `vl_fob` | Valor FOB, em US$: a carga embarcada no porto de origem, sem o frete nem o seguro internacionais. |
| `kg_liquido` | Peso líquido, em kg. |
| `vl_cif` | Valor CIF, em US$: FOB mais frete e seguro internacionais, no porto brasileiro. |
| `vl_frete` | Frete internacional, em US$. |
| `vl_seguro` | Seguro internacional, em US$. |

### Exportação de soja em grão: `data/raw_soja/ano=AAAA/exportacoes.parquet`

Uma linha por mês, com FOB e peso, só para a relação de troca no porto.

| Coluna | Descrição |
| --- | --- |
| `mes` | Mês (1 a 12); o ano fica no caminho (ano=AAAA), não dentro do arquivo. |
| `co_ncm` | NCM da soja em grão exportada. |
| `vl_fob` | Valor FOB da soja exportada, em US$. |
| `kg_liquido` | Peso líquido, em kg. |

### Importações de enxofre e rocha fosfática: `data/raw_insumos/ano=AAAA/importacoes.parquet`

As mesmas colunas das importações de fertilizantes, com os NCMs de ncm_insumos.csv, guardadas à parte: nunca entram nos totais de fertilizantes.

| Coluna | Descrição |
| --- | --- |
| `mes` | Mês (1 a 12); o ano fica no caminho (ano=AAAA), não dentro do arquivo. |
| `co_ncm` | NCM (8 dígitos). |
| `co_pais` | Código do país de origem no Comex Stat (texto, com os zeros à esquerda). |
| `no_pais` | Nome do país de origem, como o Comex Stat o escreve. |
| `sg_uf` | Sigla da UF do produto: na importação, a UF de destino da mercadoria, qualquer que seja a sede do importador, e não a do porto. |
| `no_uf` | Nome da UF de destino. |
| `co_via` | Código da via de transporte. |
| `no_via` | Nome da via de transporte. |
| `co_urf` | Código da URF de desembaraço: a unidade da Receita Federal onde a carga é desembaraçada, na prática o porto de chegada (texto, com os zeros à esquerda). |
| `no_urf` | Nome da URF de desembaraço, como o Comex Stat o escreve. |
| `vl_fob` | Valor FOB, em US$: a carga embarcada no porto de origem, sem o frete nem o seguro internacionais. |
| `kg_liquido` | Peso líquido, em kg. |
| `vl_cif` | Valor CIF, em US$: FOB mais frete e seguro internacionais, no porto brasileiro. |
| `vl_frete` | Frete internacional, em US$. |
| `vl_seguro` | Seguro internacional, em US$. |

## Blocos do `data/processed/dashboard.json`

| Bloco | Conteúdo |
| --- | --- |
| `meta` | período, grupos, unidades e notas |
| `mensal` | séries mensais por grupo: toneladas, valores, preços e frete |
| `anual` | resumo de cada ano por grupo |
| `origens` | maiores países de origem por ano e grupo |
| `urfs` | maiores URFs por ano e grupo |
| `sazonalidade` | média de toneladas de cada mês do calendário e índice sazonal |
| `rotas` | diagrama de fluxo e frete por rota, por ano e grupo |
| `origens_produto` | origens de cada produto nos anos mais recentes |
| `estados` | toneladas por UF de destino, ano e grupo |
| `nutrientes` | custo por nutriente no porto, mês a mês |
| `troca` | relação de troca no porto, mês a mês |
| `benchmark` | Brasil x Pink Sheet do Banco Mundial e PTAX, mês a mês |
| `mapa` | mapa de fluxos: países, portos, continentes e rotas por ano e grupo |
| `insumos` | enxofre, rocha fosfática e custo de insumo por tonelada de MAP |

Os blocos com séries mensais (`mensal`, `nutrientes`, `troca`, `benchmark`, `insumos`) trazem a
lista `periodos` e os valores alinhados a ela, com null no mês sem dado; os blocos em tabela trazem
`colunas` e `dados`. `benchmark` e `troca` levam 6 casas decimais (arredonde uma vez só, na
exibição).

## Outros arquivos

| Arquivo | Conteúdo |
| --- | --- |
| `data/raw_benchmark/fonte.json` | edição da Pink Sheet usada: fonte, licença, página, URL do xlsx, data de atualização, sha256, aba, unidade e colunas |
| `data/eventos.yml` | marcos de mercado: `data` (AAAA-MM-DD ou AAAA-MM), `titulo`, `fonte_url` (https://) e `produtos` (as chaves dos sinais); veja a METODOLOGIA |
| `data/sinais.json` | sinais de preço e de volume, no formato abaixo |

## Formato do `data/sinais.json` (versão 1)

Topo: `versao` (inteiro, hoje 1), `periodo` (`{inicio, fim}`, AAAA-MM), `fonte` (texto), `limites`
(os `SINAIS_*` usados), `produtos` (por chave: `nome`, `ancora`, `volume_min_t`, `pink_sheet`, que
é o nome da série ou null), `notas` (avisos de leitura) e `sinais` (lista).

Cada sinal, sempre com estes campos e nesta ordem:

| Campo | Tipo | O que é |
| --- | --- | --- |
| `id` | texto | `AAAA-MM/produto/tipo`, único e estável entre atualizações |
| `mes` | texto | mês do dado (AAAA-MM), não o da publicação |
| `produto` | texto | `ureia`, `sulfato_amonio`, `kcl`, `map`, `dap`, `tsp`, `npk`, `enxofre` ou `rocha` |
| `tipo` | texto | `media_12m`, `variacao_3m`, `recorde`, `internacional`, `troca_p90` ou `ritmo_importacao` |
| `direcao` | texto | `alta` ou `queda` (no recorde, alta = máxima e queda = mínima; na troca, sempre alta) |
| `metrica` | texto | `cif_usd_t` (CIF do Brasil, US$/t), `pink_usd_t` (Pink Sheet, US$/t), `troca_t_soja` (t de soja por t) ou `t` (toneladas) |
| `valor` | número | valor do mês na métrica (toneladas inteiras; o resto com até 6 casas) |
| `unidade` | texto | `US$/t`, `t de soja por t` ou `t` |
| `comparacao` | objeto | `base` (`media_12m`, `3_meses_antes`, `recorde_anterior`, `pink_2_meses_antes`, `percentil_90` ou `mesmo_mes_ano_anterior`), `valor` (o termo de comparação, na mesma métrica), `variacao_pct` (valor ÷ comparação − 1, em %) e os campos do tipo, abaixo |
| `nivel` | texto | `atencao` ou `forte` |
| `ancora` | texto | id do gráfico do produto no site radar.graaos.cloud (`#secao-bm`, `#secao-nutrientes`, `#precos`, `#troca`, `#grafico-enxofre`, `#grafico-rocha`) |
| `frase` | texto | frase pronta em pt-BR, com os números formatados como no site (`src/formato.py`) |

Campos a mais em `comparacao`:

- `media_12m`: `janela_meses`, `meses_validos`;
- `variacao_3m`: `mes` (o de referência), `janela_meses`;
- `recorde`: `mes` (o do recorde anterior), `desde` (primeiro mês válido da série), `meses_validos`;
- `internacional`: `mes`, `janela_meses`, `pink_serie`, `proxy` (true no MAP, comparado pelo DAP),
  `brasil_valor`, `brasil_anterior`, `brasil_variacao_pct` (o CIF do Brasil nos mesmos meses);
- `troca_p90`: `percentil`, `meses_validos`;
- `ritmo_importacao`: `mes` (o mesmo mês do ano anterior).

Ordem: por mês, depois nível (forte primeiro), produto (na ordem da lista acima) e tipo (na ordem da
tabela). Um sinal por linha e sem data de geração: o arquivo só muda quando mudam os dados ou as
regras. Regenere com `python -m src.sinais` sempre que o `dashboard.json` mudar (um teste reprova
o arquivo fora de dia).

**Estabilidade.** `versao` só muda se um campo sair, for renomeado ou mudar de tipo ou de sentido.
Campo novo (no topo, num sinal ou em `comparacao`) e tipo novo de sinal não mudam a versão; quem lê
deve ignorar o que não conhece. O `id` identifica o sinal de uma atualização para outra. O
histórico inteiro é recalculado a cada atualização, com os dados e os limites atuais, e o histórico
do Git guarda cada versão publicada.
