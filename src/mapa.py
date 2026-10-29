"""Tabelas de referência do mapa de fluxos (data/ref) e bloco "mapa" do dashboard.json.

A geração de data/ref roda à mão, em desenvolvimento, e o resultado fica versionado: o
transform só lê as tabelas, sem rede.

    python -m src.mapa urfs     # data/ref/urf_coordenadas.csv
    python -m src.mapa paises   # data/ref/paises_iso.csv (consulta o Comex Stat; --manter reaproveita)

Fontes, todas abertas:
- Natural Earth 1:50m, Admin 0 – Countries: ponto de rótulo (LABEL_X, LABEL_Y) e continente de
  cada país, usados nas origens (domínio público).
- Natural Earth 1:10m, Ports e Populated Places: coordenadas dos portos (URFs).
- Comex Stat/MDIC, /tables/countries/{código}: código ISO 3166-1 alfa-3 de cada país.

Continentes: o campo CONTINENT do Natural Earth, em códigos de duas letras (CONTINENTES). É a
classificação do Natural Earth: a Rússia entra inteira na Europa; o México, a América Central e
o Caribe, na América do Norte; a Turquia, na Ásia. Ilhas em "Seven seas" ficam sem continente.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import sys
from pathlib import Path

import pandas as pd

from . import config

log = logging.getLogger("radar.mapa")

NE_VERSAO = "v5.1.2"
NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/" + NE_VERSAO + "/geojson/{}.geojson"
NE_PAISES_50 = "ne_50m_admin_0_countries"
NE_PORTOS = "ne_10m_ports"
NE_CIDADES = "ne_10m_populated_places_simple"

REF_DIR = config.DADOS_DIR / "ref"
PAISES_CSV = REF_DIR / "paises_iso.csv"
URFS_CSV = REF_DIR / "urf_coordenadas.csv"

# CONTINENT do Natural Earth -> código (duas letras) e nome em português
CONTINENTES = {"Africa": "AF", "Asia": "AS", "Europe": "EU", "North America": "NA", "Oceania": "OC", "South America": "SA"}
NOMES_CONTINENTES = {"AF": "África", "AS": "Ásia", "EU": "Europa", "NA": "América do Norte e Central", "OC": "Oceania", "SA": "América do Sul"}

# Cada URF com volume relevante -> onde ela fica no Natural Earth: camada "porto" (nome em
# ne_10m_ports) ou "cidade" (nome em ne_10m_populated_places, na UF), e o nome do porto no
# mapa (URFs no mesmo lugar viram um nó só, ex.: Salvador e Aratu). Quando o porto não está
# no Natural Earth, vale o lugar mais próximo que está, com a distância anotada. A escala do
# mapa (células de 1,5 grau, cerca de 165 km) absorve essas aproximações.
URF_LOCAL: dict[str, tuple[str, str, str, str, str]] = {
    # co_urf: (camada, nome no Natural Earth, UF, porto no mapa, observação)
    "0917800": ("porto", "Paranagua", "PR", "Paranaguá", ""),
    "0817800": ("porto", "Santos", "SP", "Santos", ""),
    "1017700": ("porto", "Rio Grande", "RS", "Rio Grande", ""),
    "0927700": ("porto", "Sao Francisco do Sul", "SC", "São Francisco do Sul", ""),
    "0727600": ("porto", "Vitoria", "ES", "Vitória", ""),
    "0517800": ("porto", "Salvador", "BA", "Salvador e Aratu", ""),
    "0517600": ("porto", "Salvador", "BA", "Salvador e Aratu", ""),
    "0517602": ("porto", "Salvador", "BA", "Salvador e Aratu", "Porto de Aratu, na Baía de Todos os Santos, a cerca de 20 km"),
    "0217800": ("porto", "Belem", "PA", "Belém", ""),
    "1015400": ("porto", "Porto Alegre", "RS", "Porto Alegre", ""),
    "1017800": ("porto", "Porto Alegre", "RS", "Porto Alegre", ""),
    "0417900": ("porto", "Recife", "PE", "Recife", ""),
    "0415100": ("porto", "Recife", "PE", "Recife", ""),
    "0440151": ("porto", "Maceio", "AL", "Maceió", ""),
    "0520100": ("porto", "Aracaju", "SE", "Aracaju", ""),
    "0717600": ("porto", "Rio de Janeiro", "RJ", "Rio de Janeiro e Itaguaí", ""),
    "0717800": ("porto", "Rio de Janeiro", "RJ", "Rio de Janeiro e Itaguaí", "Porto de Itaguaí, a cerca de 60 km a oeste"),
    "0317900": ("porto", "Fortaleza", "CE", "Fortaleza e Pecém", ""),
    "0317600": ("porto", "Fortaleza", "CE", "Fortaleza e Pecém", ""),
    "0317800": ("porto", "Fortaleza", "CE", "Fortaleza e Pecém", "Porto do Pecém, a cerca de 50 km a oeste"),
    "0317903": ("cidade", "São Luís", "MA", "São Luís (Itaqui)", ""),
    "0320151": ("cidade", "São Luís", "MA", "São Luís (Itaqui)", ""),
    "0327600": ("cidade", "São Luís", "MA", "São Luís (Itaqui)", ""),
    "0210200": ("cidade", "Santarém", "PA", "Santarém", ""),
    "0227600": ("cidade", "Manaus", "AM", "Manaus", ""),
    "0217602": ("cidade", "Abaetetuba", "PA", "Barcarena (Vila do Conde)", "Porto de Vila do Conde, em Barcarena, a cerca de 25 km"),
    "0217802": ("cidade", "Abaetetuba", "PA", "Barcarena (Vila do Conde)", "Porto de Vila do Conde, em Barcarena, a cerca de 25 km"),
    "0927502": ("cidade", "Imbituba", "SC", "Imbituba", ""),
    "0925251": ("cidade", "Imbituba", "SC", "Imbituba", ""),
    "0927800": ("cidade", "Itajaí", "SC", "Itajaí", ""),
    "0147600": ("cidade", "Corumbá", "MS", "Corumbá", "fronteira com a Bolívia (rodovia e ferrovia)"),
    "0130151": ("cidade", "Cáceres", "MT", "Cáceres", "fronteira com a Bolívia"),
    "0710251": ("cidade", "Campos", "RJ", "Campos (Açu)", "Porto do Açu, em São João da Barra, a cerca de 35 km"),
    "0240152": ("cidade", "Macapá", "AP", "Santana", "Porto de Santana, a cerca de 20 km de Macapá"),
    "0417902": ("cidade", "Cabo de Santo Agostinho", "PE", "Suape", "Porto de Suape, a cerca de 10 km"),
    "0417800": ("cidade", "Cabo de Santo Agostinho", "PE", "Suape", "Porto de Suape, a cerca de 10 km"),
}
NOMES_UF = {
    "PR": "Paraná", "SP": "São Paulo", "RS": "Rio Grande do Sul", "SC": "Santa Catarina", "ES": "Espírito Santo",
    "BA": "Bahia", "PA": "Pará", "PE": "Pernambuco", "AL": "Alagoas", "SE": "Sergipe", "RJ": "Rio de Janeiro",
    "CE": "Ceará", "MA": "Maranhão", "AM": "Amazonas", "MS": "Mato Grosso do Sul", "MT": "Mato Grosso", "AP": "Amapá",
}


# --- Natural Earth ------------------------------------------------------------------------


def baixar_ne(camada: str) -> tuple[dict, str, str]:
    """(GeoJSON, URL, sha256) de uma camada do Natural Earth na versão fixa."""
    import requests

    url = NE_URL.format(camada)
    resp = requests.get(url, timeout=180)
    resp.raise_for_status()
    return resp.json(), url, hashlib.sha256(resp.content).hexdigest()


def _iso3(props: dict) -> str:
    """ISO 3166-1 alfa-3; ISO_A3_EH corrige os -99 de França e Noruega no Natural Earth."""
    for campo in ("ISO_A3_EH", "ISO_A3", "ADM0_A3"):
        valor = str(props.get(campo) or "")
        if len(valor) == 3 and valor.isalpha():
            return valor.upper()
    return "-" + str(props.get("NAME") or "?")


def _continente(props: dict) -> str | None:
    """Código do continente do Natural Earth (None para Antártida e "Seven seas")."""
    return CONTINENTES.get(str(props.get("CONTINENT") or ""))


# --- URFs ---------------------------------------------------------------------------------


def coordenadas_urfs(urfs: pd.DataFrame, portos: dict, cidades: dict) -> pd.DataFrame:
    """Lat/lon de cada URF de `urfs` (co_urf, no_urf) pela tabela URF_LOCAL. Pura."""
    por_porto = {}
    for f in portos["features"]:
        lon, lat = f["geometry"]["coordinates"][:2]
        if -75 < lon < -28 and -35 < lat < 6:  # só o Brasil e arredores
            por_porto.setdefault(f["properties"]["name"], (lon, lat))
    por_cidade = {}
    for f in cidades["features"]:
        p = f["properties"]
        if p.get("adm0name") == "Brazil":
            por_cidade[(p["name"], p.get("adm1name"))] = tuple(f["geometry"]["coordinates"][:2])
    linhas = []
    for _, u in urfs.iterrows():
        if u["co_urf"] not in URF_LOCAL:
            raise KeyError(f"URF {u['co_urf']} ({u['no_urf']}) sem lugar em URF_LOCAL (src/mapa.py)")
        camada, nome, uf, porto, obs = URF_LOCAL[u["co_urf"]]
        if camada == "porto":
            lon, lat = por_porto[nome]
            fonte = "Natural Earth 1:10m, Ports"
        else:
            lon, lat = por_cidade[(nome, NOMES_UF[uf])]
            fonte = "Natural Earth 1:10m, Populated Places"
        linhas.append({"co_urf": u["co_urf"], "no_urf": u["no_urf"], "porto": porto, "uf": uf, "local_ne": nome, "lon": round(lon, 4),
                       "lat": round(lat, 4), "fonte": fonte, "observacao": obs})
    return pd.DataFrame(linhas).sort_values("co_urf").reset_index(drop=True)


def urfs_relevantes(processed: Path = config.PROCESSED_DIR, minimo_t: float = 10_000) -> pd.DataFrame:
    """URFs com alguma rota acima do corte ou com pelo menos `minimo_t` num ano e grupo."""
    share = pd.read_csv(processed / "share_urf_ano.csv", dtype={"co_urf": str})
    rotas = pd.read_csv(processed / "rotas_ano.csv", dtype={"co_urf": str, "co_pais": str})
    com_rota = set(rotas.loc[rotas["relevante"], "co_urf"])
    maximo = share.groupby("co_urf")["toneladas"].max()
    codigos = com_rota | set(maximo[maximo >= minimo_t].index)
    nomes = share.drop_duplicates("co_urf", keep="last").set_index("co_urf")["no_urf"]
    return pd.DataFrame({"co_urf": sorted(codigos), "no_urf": [nomes.get(c, "") for c in sorted(codigos)]})


def gerar_urfs(saida: Path = URFS_CSV) -> pd.DataFrame:
    portos, _, _ = baixar_ne(NE_PORTOS)
    cidades, _, _ = baixar_ne(NE_CIDADES)
    df = coordenadas_urfs(urfs_relevantes(), portos, cidades)
    saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(saida, index=False, encoding="utf-8", lineterminator="\n")
    log.info("%s: %d URFs", saida, len(df))
    return df


# --- Países -------------------------------------------------------------------------------


def centroides(ne50: dict) -> dict[str, tuple[float, float]]:
    """ISO3 -> (lon, lat) do ponto de rótulo do país no Natural Earth 1:50m."""
    pontos = {}
    for f in ne50["features"]:
        p = f["properties"]
        if p.get("LABEL_X") is None:
            continue
        for campo in ("ISO_A3_EH", "ISO_A3", "ADM0_A3"):
            codigo = str(p.get(campo) or "")
            if len(codigo) == 3 and codigo.isalpha():
                pontos.setdefault(codigo.upper(), (round(float(p["LABEL_X"]), 3), round(float(p["LABEL_Y"]), 3)))
    return pontos


def continentes_por_iso(ne: dict) -> dict[str, str]:
    """ISO3 -> código do continente (CONTINENT do Natural Earth)."""
    saida = {}
    for f in ne["features"]:
        p = f["properties"]
        cont = _continente(p)
        if cont is None:
            continue
        for campo in ("ISO_A3_EH", "ISO_A3", "ADM0_A3"):
            codigo = str(p.get(campo) or "")
            if len(codigo) == 3 and codigo.isalpha():
                saida.setdefault(codigo.upper(), cont)
    return saida


def gerar_paises(saida: Path = PAISES_CSV, manter: bool = False) -> pd.DataFrame:
    """Todos os países da tabela do Comex Stat com o ISO3 (detalhe de cada um) e o centróide."""
    from .ingest import ClienteComexStat, _lista

    cliente = ClienteComexStat()
    lista = _lista(cliente.get("/tables/countries", params={"language": config.IDIOMA}))
    anteriores = {}
    if manter and saida.exists():
        anteriores = pd.read_csv(saida, dtype=str, keep_default_na=False).set_index("co_pais")["iso3"].to_dict()
    ne50, _, _ = baixar_ne(NE_PAISES_50)
    pontos = centroides(ne50)
    continentes = continentes_por_iso(ne50)
    linhas = []
    for i, item in enumerate(lista, 1):
        codigo, nome = str(item["id"]), str(item["text"])
        iso3 = anteriores.get(codigo)
        if iso3 is None:
            detalhe = cliente.get(f"/tables/countries/{codigo}")
            iso3 = str((detalhe or {}).get("coPaisIsoa3") or "").strip().upper()
            log.info("%d/%d %s %s -> %s", i, len(lista), codigo, nome, iso3 or "(sem ISO3)")
        lon, lat = pontos.get(iso3, (None, None))
        linhas.append({"co_pais": codigo, "no_pais": nome, "iso3": iso3, "lon": lon, "lat": lat, "continente": continentes.get(iso3, ""),
                       "fonte": "Comex Stat/MDIC (ISO3); Natural Earth 1:50m (ponto de rótulo e continente)" if lon is not None else "Comex Stat/MDIC (ISO3)"})
    df = pd.DataFrame(linhas).sort_values("co_pais").reset_index(drop=True)
    saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(saida, index=False, encoding="utf-8", lineterminator="\n")
    log.info("%s: %d países, %d com coordenada", saida, len(df), int(df["lon"].notna().sum()))
    return df


def ler_paises(caminho: Path | None = None) -> pd.DataFrame:
    df = pd.read_csv(caminho or PAISES_CSV, dtype={"co_pais": str, "iso3": str, "continente": str}, keep_default_na=False, na_values={"lon": [""], "lat": [""]})
    if "continente" not in df.columns:
        df["continente"] = ""
    return df


def ler_urfs(caminho: Path | None = None) -> pd.DataFrame:
    return pd.read_csv(caminho or URFS_CSV, dtype={"co_urf": str}, keep_default_na=False)


# --- Bloco "mapa" do dashboard.json ------------------------------------------------------

MINIMO_ORIGEM_T = 1_000  # origem com menos que isso no ano e grupo entra em "outros"


def _linha_porto(x, custo: pd.DataFrame, indice_porto: dict, num) -> list:
    """[porto, t, variação % sobre os mesmos meses do ano anterior, frete US$/t, CIF US$/t].

    Sem os mesmos meses no ano anterior (o primeiro ano) ou porto novo: variação vazia. Frete e
    CIF são valor ÷ toneladas de todas as rotas que chegam ao porto, inclusive as abaixo do corte.
    """
    t, anterior = float(x["toneladas"]), x["anterior"]
    var = 100 * (t / anterior - 1) if pd.notna(anterior) and anterior > 0 else None
    frete = cif = None
    if x["porto"] in custo.index and custo.loc[x["porto"], "toneladas"] > 0:
        c = custo.loc[x["porto"]]
        frete, cif = c["vl_frete"] / c["toneladas"], c["vl_cif"] / c["toneladas"]
    return [indice_porto[x["porto"]], num(t, 0), num(var, 1), num(frete, 0), num(cif, 0)]


def bloco_dashboard(tabelas: dict[str, pd.DataFrame], paises: pd.DataFrame, urfs: pd.DataFrame, num) -> dict:
    """Mapa de fluxos: por ano e grupo, as origens (toneladas, share, variação, frete e CIF
    US$/t), as rotas acima do corte (agregadas por porto) e o total de cada porto.

    Só usa tabelas do transform (share_origem_ano, share_urf_ano, rotas_ano e
    precos_mes_grupo_origem) e as tabelas de referência de data/ref. Origem sem coordenada,
    ou abaixo de MINIMO_ORIGEM_T, vai para "outros_t"; rota abaixo do corte (ou para porto
    sem coordenada) não ganha arco e fica na diferença entre o total e as rotas.

    Continentes: soma de todas as origens de cada continente (inclusive as pequenas), com o
    share do total e a variação sobre os mesmos meses do ano anterior (a mesma base do
    share_origem_ano, que traz com zero quem deixou de exportar). País sem continente fica fora.
    `num(valor, casas)` é o formatador do transform.
    """
    share = tabelas["share_origem_ano"]
    rotas = tabelas["rotas_ano"]
    urf_ano = tabelas["share_urf_ano"]
    precos = tabelas["precos_mes_grupo_origem"]

    coord_pais = paises.dropna(subset=["lon", "lat"]).drop_duplicates("co_pais").set_index("co_pais")
    cont_pais = paises.drop_duplicates("co_pais").set_index("co_pais")["continente"] if "continente" in paises else pd.Series(dtype=str)
    cont_pais = cont_pais[cont_pais.isin(list(NOMES_CONTINENTES))]
    coord_urf = urfs.set_index("co_urf")
    portos = {}
    for co_urf, u in coord_urf.iterrows():
        pid = u["porto"]
        portos.setdefault(pid, {"nome": u["porto"], "uf": u["uf"], "lon": float(u["lon"]), "lat": float(u["lat"]), "urfs": []})
        portos[pid]["urfs"].append(co_urf)
    porto_da_urf = {c: u["porto"] for c, u in coord_urf.iterrows()}
    nomes_portos = sorted(portos)
    indice_porto = {nome: i for i, nome in enumerate(nomes_portos)}

    # CIF e frete US$/t por origem e ano (TOTAL = soma dos grupos)
    soma = precos.groupby(["ano", "grupo", "co_pais"], as_index=False)[["toneladas", "vl_cif", "vl_frete"]].sum()
    total = soma.groupby(["ano", "co_pais"], as_index=False)[["toneladas", "vl_cif", "vl_frete"]].sum().assign(grupo="TOTAL")
    soma = pd.concat([soma, total], ignore_index=True).set_index(["ano", "grupo", "co_pais"])

    anos = sorted(int(a) for a in share["ano"].unique())
    n_meses = share.drop_duplicates("ano").set_index("ano")["n_meses"]
    dados, usados = {}, set()
    for (ano, grupo), g in share.groupby(["ano", "grupo"], sort=True):
        ano = int(ano)
        origens, outros = [], 0.0
        for _, o in g.sort_values("toneladas", ascending=False).iterrows():
            t = float(o["toneladas"])
            if t < MINIMO_ORIGEM_T or o["co_pais"] not in coord_pais.index:
                outros += t
                continue
            chave = (ano, grupo, o["co_pais"])
            cif = frete = None
            if chave in soma.index and soma.loc[chave, "toneladas"] > 0:
                cif = soma.loc[chave, "vl_cif"] / soma.loc[chave, "toneladas"]
                frete = soma.loc[chave, "vl_frete"] / soma.loc[chave, "toneladas"]
            origens.append([o["co_pais"], num(t, 0), num(o["share_t_pct"], 1), num(o["var_t_pct"], 1), num(frete, 0), num(cif, 0)])
            usados.add(o["co_pais"])
        r = rotas[(rotas["ano"] == ano) & (rotas["grupo"] == grupo) & rotas["relevante"]]
        r = r[r["co_urf"].isin(porto_da_urf) & r["co_pais"].isin(coord_pais.index)].assign(porto=lambda x: x["co_urf"].map(porto_da_urf))
        r = r.groupby(["co_pais", "porto"], as_index=False)[["toneladas", "vl_frete"]].sum().sort_values("toneladas", ascending=False)
        lista_rotas = [[x["co_pais"], indice_porto[x["porto"]], num(x["toneladas"], 0), num(x["vl_frete"] / x["toneladas"], 0)] for _, x in r.iterrows()]
        usados.update(r["co_pais"])
        # portos: toneladas e variação sobre os mesmos meses do ano anterior (share_urf_ano, com as
        # URFs do mesmo lugar somadas), e frete e CIF US$/t de TODAS as rotas que chegam lá
        u = urf_ano[(urf_ano["ano"] == ano) & (urf_ano["grupo"] == grupo) & urf_ano["co_urf"].isin(porto_da_urf)]
        u = u.assign(porto=u["co_urf"].map(porto_da_urf)).groupby("porto", as_index=False).agg(
            toneladas=("toneladas", "sum"), anterior=("toneladas_ano_anterior", lambda x: x.sum(min_count=1)))
        todas = rotas[(rotas["ano"] == ano) & (rotas["grupo"] == grupo) & rotas["co_urf"].isin(porto_da_urf)]
        custo = todas.assign(porto=todas["co_urf"].map(porto_da_urf)).groupby("porto")[["toneladas", "vl_frete", "vl_cif"]].sum()
        total_t = float(g["toneladas"].sum())
        continentes = []
        for cont, c in g.assign(cont=g["co_pais"].map(cont_pais)).dropna(subset=["cont"]).groupby("cont"):
            t = float(c["toneladas"].sum())
            ant = c["toneladas_ano_anterior"]
            ant = float(ant.fillna(0).sum()) if ant.notna().any() else None  # sem os mesmos meses no ano anterior: sem variação
            var = 100 * (t / ant - 1) if ant else None
            if t > 0 or ant:
                continentes.append([cont, num(t, 0), num(100 * t / total_t if total_t else None, 1), num(var, 1)])
        continentes.sort(key=lambda x: (-x[1], x[0]))
        dados.setdefault(str(ano), {})[grupo] = {
            "t": num(total_t, 0),
            "origens": origens,
            "outros_t": num(outros, 0),
            "rotas": lista_rotas,
            "portos": [_linha_porto(x, custo, indice_porto, num) for _, x in u.sort_values(["toneladas", "porto"], ascending=[False, True]).iterrows()],
            "continentes": continentes,
        }
    nomes = share.drop_duplicates("co_pais", keep="last").set_index("co_pais")["no_pais"]
    return {
        "anos": anos,
        "n_meses": [int(n_meses[a]) for a in anos],
        "corte_rota_t": [num(c, 0) for c in rotas.drop_duplicates("ano").set_index("ano").reindex(anos)["corte_t"]],
        "minimo_origem_t": MINIMO_ORIGEM_T,
        "paises": {c: [str(nomes.get(c, coord_pais.loc[c, "no_pais"])), coord_pais.loc[c, "iso3"], float(coord_pais.loc[c, "lon"]), float(coord_pais.loc[c, "lat"]),
                       cont_pais.get(c)] for c in sorted(usados)},
        "continentes": NOMES_CONTINENTES,
        "colunas": {
            "origens": ["co_pais", "t", "share_pct", "var_t_pct", "frete_usd_t", "cif_usd_t"],
            "rotas": ["co_pais", "porto", "t", "frete_usd_t"],
            "portos": ["porto", "t", "var_t_pct", "frete_usd_t", "cif_usd_t"],
            "lista_portos": ["nome", "uf", "lon", "lat", "urfs"],
            "paises": ["nome", "iso3", "lon", "lat", "continente"],
            "continentes": ["continente", "t", "share_pct", "var_t_pct"],
        },
        "portos": [[portos[n]["nome"], portos[n]["uf"], portos[n]["lon"], portos[n]["lat"], portos[n]["urfs"]] for n in nomes_portos],
        "dados": dados,
        "notas": [
            "Visão geral: um arco por país de origem até o Brasil (as maiores origens do ano).",
            "Ao abrir um país ou porto, arco só para rotas com pelo menos 50 mil t no ano (proporcional aos meses num ano parcial); o resto fica em 'outras'.",
            f"Origens com menos de {MINIMO_ORIGEM_T:,} t no ano e grupo entram em 'outros'.".replace(",", "."),
            "Coordenadas: Natural Earth (domínio público); URFs no mesmo lugar aparecem como um só porto.",
            "Continentes: classificação do Natural Earth (a Rússia entra na Europa; o México, a América Central e o Caribe, na América do Norte e Central).",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m src.mapa", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("urfs", help="data/ref/urf_coordenadas.csv")
    p = sub.add_parser("paises", help="data/ref/paises_iso.csv (uma consulta ao Comex Stat por país)")
    p.add_argument("--manter", action="store_true", help="reaproveita o ISO3 já gravado e só consulta países novos")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
    if args.comando == "urfs":
        gerar_urfs()
    else:
        gerar_paises(manter=args.manter)
    return 0


if __name__ == "__main__":
    sys.exit(main())
