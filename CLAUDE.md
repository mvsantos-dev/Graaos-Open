# CLAUDE.md: Graaos Open

Core aberto do Graaos — hub de inteligência de mercado do agro e da logística, com dados públicos.
Repositório: https://github.com/mvsantos-dev/Graaos-Open. **O repositório é PÚBLICO** (ou vai ser):
escreva tudo como se já fosse.

Aqui ficam o pipeline de dados, os dados tratados de `data/`, o método e os testes do módulo
**Fertilizantes**: importações brasileiras de fertilizantes (capítulo 31, posições 3102 a 3105), os
insumos do fósforo (enxofre 2503 e rocha fosfática 2510, à parte) e os sinais de preço e de volume,
só com dados abertos oficiais: Comex Stat/MDIC, Pink Sheet do Banco Mundial e PTAX do BCB. O site
(radar.graaos.cloud) e o relatório mensal ficam num repositório privado e não entram aqui: nada de
código, teste, workflow ou texto deles neste repositório.

## Regras inegociáveis

### Escopo

- O Graaos cobre granéis sólidos, grãos e logística. NÃO cobre granéis líquidos (óleos vegetais,
  químicos, combustíveis): nada de série, tabela ou texto sobre eles (2807, 2809 e 2814 ficam fora).
- Só o core: ingestão, transform, sinais, marcos, tabelas de referência do mapa, dados e método.

### Licenças

- Código sob MIT (`LICENSE`); dados tratados de `data/` sob CC BY 4.0 (`data/LICENSE`), com o
  crédito exato "Graaos (github.com/mvsantos-dev/Graaos-Open)" no README, no CITATION.cff e no
  data/LICENSE (há teste). Os dados de origem seguem as licenças das fontes (README, "Licenças das
  fontes").
- Pipeline, dados tratados, método, site e relatório mensal são abertos e gratuitos para ler. Nada do
  que hoje é aberto migra para a parte paga.

### Segurança (repositório público)

- NUNCA escrever chaves, tokens, senhas, URLs privadas ou credenciais em código, config, README,
  testes ou commits. Este repositório não usa nenhum segredo: as fontes não pedem chave e os
  workflows só usam o `GITHUB_TOKEN` do próprio Actions.
- Nenhuma chave está nem vai estar nas sessões de desenvolvimento: nunca pedir nem tentar ler chaves
  (nem `.env`, nem variáveis de ambiente). Os testes não usam chave nem rede.
- `.env`, `.env.*` (exceto `.env.example`), `*.key`, `*.pem` e `secrets/` ficam no `.gitignore`.
  Não remover essas linhas.
- Antes de CADA commit, rodar `git diff --cached` e conferir que não há segredos. O pre-commit com
  gitleaks (`.pre-commit-config.yaml`) bloqueia vazamentos. Se o hook não estiver instalado, rodar o
  mesmo comando dele: `gitleaks git --pre-commit --redact --staged --verbose`.
- Usar apenas dados abertos oficiais, de governo ou de organismos internacionais, com licença que
  permita redistribuição. Nunca dados de empresas ou clientes.
- Toda saída pública (README, METODOLOGIA, DADOS, release) cita as fontes que usa, no formato
  "Fonte: Comex Stat/MDIC; Banco Mundial (Pink Sheet); BCB/PTAX".

### Autoria dos commits

- Commits saem SOMENTE com a identidade git do mantenedor:
  `Marcus Santos <77951123+mvsantos-dev@users.noreply.github.com>`. Os commits antigos, com o e-mail
  noreply do nome de usuário anterior (o mesmo ID 77951123), continuam ligados à conta: nunca
  reescrever o histórico para trocá-los.
- Única exceção: os commits automáticos do `.github/workflows/atualizacao.yml` saem como
  `github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>`, sempre com a
  mensagem `chore(dados): atualização AAAA-MM` e só com arquivos de `data/`.
- NÃO adicionar `Co-Authored-By`, link de sessão nem nenhum trailer ou menção a IA em mensagens de
  commit ou descrições de PR. O `.claude/settings.json` desliga essa atribuição.
- Em sessões na nuvem, o git vem com outra identidade e assina os commits com uma chave própria.
  Antes de commitar:

  ```bash
  git config user.name "Marcus Santos"
  git config user.email "77951123+mvsantos-dev@users.noreply.github.com"
  git config commit.gpgsign false
  ```

- Mensagens de commit em português, no padrão Conventional Commits (`feat:`, `fix:`, `docs:`,
  `chore:`).

## Como trabalhar aqui

- Trabalhar a partir de `main`. Force-push só com autorização explícita.
- Python 3.10+. Dependências em `requirements.txt` (requests, pandas, pyarrow, openpyxl); as de
  desenvolvimento em `requirements-dev.txt`.
- Testes: `python -m pytest`. Não acessam a rede (as APIs são simuladas) e conferem os dados
  versionados.
- CI (`.github/workflows/ci.yml`): pytest em Python 3.10 (pandas 2) e 3.13 (pandas 3) e gitleaks em
  todo o histórico, em push e PR. Só leitura e sem nenhum segredo.
- Actions sempre em versões que rodam em Node 24 (`checkout@v6`, `setup-python@v6`, `setup-go@v6`,
  `upload-artifact@v7`, `download-artifact@v8`). Antes de trocar uma versão, conferir `runs.using`
  no `action.yml` da tag.
- Ingestão: `python -m src.ingest --inicio AAAA-MM [--fim AAAA-MM] [--serie todas|fertilizantes|soja|insumos|benchmark|cambio]`.
  `--ultimo-gravado` imprime o último mês completo, o menor entre as cinco séries, sem chamar nenhuma
  fonte (`--por-serie`: uma linha por série).
- Dados brutos: `data/raw/ano=AAAA/importacoes.parquet` (a coluna `ano` fica no caminho; leia com
  `src.ingest.ler_raw()`), `data/raw_soja/` (`ler_soja()`), `data/raw_insumos/` (`ler_insumos()`,
  NCMs em `data/ncm_insumos.csv`, separado do `ncm_fertilizantes.csv`), a Pink Sheet em
  `data/raw_benchmark/` e a PTAX em `data/raw_cambio/` (`src.benchmark.ler_pink()` e `ler_ptax()`).
- `python -m src.transform` gera `data/processed/` (CSVs e `dashboard.json`), de forma
  determinística; regenerar sempre que os dados brutos mudarem. Coluna nova num CSV ou bloco novo no
  `dashboard.json`: descrever no DADOS.md.
- `python -m src.sinais` regenera `data/sinais.json` (formato versão 1, documentado no DADOS.md: campo
  novo pode entrar; sair, renomear ou mudar o sentido de um campo = `versao` 2), sempre que o
  `dashboard.json` mudar (o teste "em dia" reprova). Regras fixas, sem IA, sem olhar o futuro; limites
  SÓ em `config.py` (`SINAIS_*`). Médias com `math.fsum`. Só biblioteca padrão no `src/sinais.py` e
  no `src/formato.py`.
- `data/eventos.yml` é editado à mão pelo mantenedor; `python -m src.eventos` confere. O marco é
  anotação, não dado oficial: nunca dizer que ele causou a variação.
- `src/mapa.py` só gera as tabelas de `data/ref/` (em desenvolvimento, `python -m src.mapa urfs` e
  `paises --manter`) e monta o bloco "mapa". País ou URF com volume relevante sem coordenada reprova
  o teste: acrescentar em `URF_LOCAL`.
- Fluxo mensal (`.github/workflows/atualizacao.yml`, dias 1 a 15): se o mês anterior já está
  gravado, encerra sem chamar nenhuma fonte; senão ingestão (Pink Sheet e PTAX primeiro; o Comex Stat
  só até o menor mês das duas), transform, sinais e testes; se o mês completo avançou, commita só
  `data/` como github-actions[bot] e cria o release `dados-AAAA-MM` com `dashboard.json`,
  `sinais.json` e os CSVs. Mês completo = gravado nas cinco séries; falta de uma = run verde com aviso
  (a partir do dia 15, o job `prazo` fica vermelho); falha de uma fonte = vermelho, nada commitado.
  Privilégios separados: o job que roda Python é só leitura; o job do commit (único com
  `contents: write`) só roda git e gh, com hooks desligados, e recusa mudança fora de `data/`. Nunca
  usar `pull_request_target`. Os testes rodam sobre o mês recém-gravado: nunca fixar valores do
  último mês nos testes com dados versionados, nem supor que as cinco séries terminam no mesmo mês.
- Não commitar dados grandes: se `data/raw/` passar de ~20 MB, colocá-lo no `.gitignore` e explicar
  no README como gerar.

## Regras de leitura dos números

- Relação de troca (`src/troca.py`): CIF de KCl 31042090, ureia 31021010 e MAP 31054000 ÷ FOB da
  soja no mesmo mês. É "no porto", não o preço ao produtor: dizer isso em toda saída pública que a
  mostrar. É US$/US$ e NÃO muda com o câmbio: nunca criar "troca em R$".
- Custo por nutriente (`src/nutrientes.py`): CIF ÷ teor do grau comercial usual (tabela `PRODUTOS`);
  MAP e DAP com crédito de N pela ureia do mesmo mês. No porto, não o preço ao produtor. R$ só pela
  PTAX venda média do mês.
- Benchmark (`src/comparacao.py`): tabela fixa NCM → série da Pink Sheet (MAP pelo DAP, aproximação);
  base FOB×FOB ou CIF×CFR. O spread NÃO é ágio: referência de outro lugar e de outro momento de
  contrato; vai sempre com o preço do Brasil da sua base. Amostra pequena: < 10 mil t no mês
  (`CORTE_AMOSTRA_T`). Blocos "benchmark" e "troca" com 6 casas; o sinal sai do número já arredondado
  (nunca "−0,0").
- Insumos (`src/insumos.py`): custo de insumo por t de MAP = CIF do enxofre × `INSUMOS_COEF_ENXOFRE`
  + CIF da rocha × `INSUMOS_COEF_ROCHA`. É uma aproximação, não o custo de nenhuma empresa, e é no
  porto. Os insumos NUNCA entram nos totais, shares, mapa, rotas ou estados de fertilizantes (o
  transform recusa NCM 2503/2510 em `data/raw/`, e há teste).
- Estados: a UF do Comex Stat na importação é a UF de DESTINO da mercadoria. Nunca chamá-la de "UF
  do importador" nem de "UF do porto".
- Grupo dos NCMs: 3102 → N, 3103 → P, 3104 → K, 3105 → NPK, exceto DAP (310530) e MAP (310540), que
  ficam em P.

## Fatos das fontes (verificados em outubro de 2026)

- Comex Stat: base `https://api-comexstat.mdic.gov.br`, sem autenticação (spec em `/docs/doc.yaml`).
  `POST /general` com `flow`, `monthDetail`, `period`, `filters`, `details` (`country, ncm, state,
  via, urf`) e `metrics` (`metricFOB, metricKG, metricCIF, metricFreight, metricInsurance`). A
  resposta traz NOMES de país, UF e via; os códigos saem de `/tables/countries`, `/tables/uf` e
  `/tables/ways`. Num período de vários anos, a API soma em cada ano só os meses do intervalo: a
  ingestão consulta um ano por vez. Rate limit agressivo (HTTP 429, "tente novamente em 10
  segundos"): pausa de 10 s e backoff exponencial. TLS sempre verificado (certificado público);
  `COMEXSTAT_CA_BUNDLE` soma CAs; `--ssl-inseguro` só depois de uma falha e só para esse host.
- Pink Sheet: xlsx `CMO-Historical-Data-Monthly.xlsx` em `thedocs.worldbank.org`, caminho que muda a
  cada edição, achado na página `https://www.worldbank.org/en/research/commodity-markets`; aba
  "Monthly Prices", nomes na linha 5 (com espaços e "**"), períodos "AAAAMmm". Edição no 2º dia útil.
  O Banco Mundial revisa meses passados: a ingestão regrava o arquivo inteiro e lista as revisões.
- PTAX: SGS 3698 em `https://api.bcb.gov.br/dados/serie/bcdata.sgs.3698/dados`, janelas de 5 anos.
  O firewall do BCB às vezes devolve HTML "Requisição inválida!" com HTTP 200: o cliente manda
  `Accept: application/json` e repete.
