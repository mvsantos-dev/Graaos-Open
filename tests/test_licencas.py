"""Licenças do repositório: código sob MIT, dados tratados de data/ sob CC BY 4.0, e o crédito
"Graaos (github.com/mvsantos-dev/Graaos-Open)" no README, no CITATION.cff e no data/LICENSE."""

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CREDITO = "Graaos (github.com/mvsantos-dev/Graaos-Open)"
FONTES = "Fonte: Comex Stat/MDIC; Banco Mundial (Pink Sheet); BCB/PTAX"


def test_codigo_mit_e_dados_tratados_cc_by():
    codigo = (RAIZ / "LICENSE").read_text(encoding="utf-8")
    assert codigo.startswith("MIT License\n") and "Copyright (c) 2026 Marcus Santos" in codigo
    dados = (RAIZ / "data" / "LICENSE").read_text(encoding="utf-8")
    assert "CC BY 4.0" in dados and f"Atribuição obrigatória: {CREDITO}" in dados
    assert "https://creativecommons.org/licenses/by/4.0/" in dados
    # os dados de origem continuam com as licenças das fontes, descritas no README
    for fonte in ("Comex Stat/MDIC", "Banco Mundial (Pink Sheet)", "BCB/PTAX: ODbL"):
        assert fonte in dados, fonte
    assert "https://github.com/mvsantos-dev/Graaos-Open#licenças-das-fontes" in dados


def test_readme_cita_licencas_credito_e_fontes():
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    topo = readme.split("\n## ", 1)[0]
    assert "[![Licença: MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-blue)](LICENSE)" in topo
    assert FONTES in topo
    assert "\n### Licenças das fontes\n" in readme
    assert "Código: [MIT](LICENSE) · Dados tratados: [CC BY 4.0](data/LICENSE)" in readme
    assert CREDITO in readme
    assert "\n## O que é aberto e o que será pago\n" in readme
    assert "Nada do que hoje é aberto vai migrar para a parte paga." in readme


def test_citation_e_documentos_com_o_credito():
    citation = (RAIZ / "CITATION.cff").read_text(encoding="utf-8")
    assert citation.startswith("cff-version: 1.2.0\n")
    assert f'name: "{CREDITO}"' in citation and "license: CC-BY-4.0" in citation
    for doc in ("METODOLOGIA.md", "DADOS.md"):
        assert FONTES in (RAIZ / doc).read_text(encoding="utf-8"), doc
    assert CREDITO in (RAIZ / "DADOS.md").read_text(encoding="utf-8")
