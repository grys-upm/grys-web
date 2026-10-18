#!/usr/bin/env python3
"""
Informe de PENDIENTES de los datos del sitio (lo que falta por completar o traducir).

    python3 scripts/informe_pendientes.py              # → reports/pendientes-datos.md
    python3 scripts/informe_pendientes.py --resumen    # solo el resumen en pantalla

No falla nunca (es informativo). En GitHub Actions se adjunta a cada compilación
y su resumen aparece en la página de la ejecución.
"""
import glob
import os
import re
import sys
from collections import OrderedDict

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "reports", "pendientes-datos.md")

# Campos que deberían estar rellenos (además de los obligatorios del esquema)
WANTED = {
    "members": {"current": ["photo", "orcid", "email", "lines", "scholar"], "former": ["since", "until"],
                "memoriam": ["since", "until"]},
    "projects": ["title_es", "start", "end", "programme", "role", "pi", "partners", "budget", "domains", "lines", "image"],
    "news": ["title_es", "category", "image"],
    "events": ["title_es", "place"],
    "opportunities": ["title_es", "line"],
    "lines": ["keywords"],
}
TRANSLATE = {"projects": ["title"], "news": ["title"], "events": ["title"], "opportunities": ["title"]}
LABEL = {"members": "Miembros", "projects": "Proyectos", "news": "Noticias", "events": "Eventos",
         "opportunities": "Convocatorias", "lines": "Líneas", "domains": "Ámbitos"}


def fm_body(path):
    s = open(path, encoding="utf-8").read()
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n?(.*)", s, re.S)
    return (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, s)


def empty(v):
    return v in (None, "", [], {})


def main():
    rows = OrderedDict()
    totals = OrderedDict()
    for coll in ("members", "projects", "lines", "news", "events", "opportunities"):
        files = sorted(glob.glob(os.path.join(ROOT, f"_{coll}", "*.md")))
        totals[coll] = [len(files), 0]
        for f in files:
            fm, body = fm_body(f)
            name = os.path.relpath(f, ROOT).replace(os.sep, "/")
            issues = []
            want = WANTED.get(coll, [])
            if isinstance(want, dict):
                want = want.get(fm.get("status"), [])
            missing = [k for k in want if empty(fm.get(k))]
            if missing:
                issues.append("faltan: " + ", ".join(missing))
            body_txt = re.sub(r"\s+", "", re.sub(r"\{%.*?%\}|<[^>]+>", "", body))
            if coll == "projects" and len(body_txt) < 40:
                issues.append("sin descripción")
            if coll == "members" and fm.get("status") == "current" and len(body_txt) < 40:
                issues.append("sin biografía")
            if fm.get("lang") == "en" and coll in ("projects", "members", "news", "lines") and len(body_txt) >= 40:
                if not fm.get("texto_es"):
                    issues.append("texto solo en inglés")
                elif fm.get("traduccion") != "revisada":
                    issues.append("traducción al español en borrador (revisar y poner «traduccion: revisada»)")
            if fm.get("lang") == "es" and coll in ("projects", "members", "news", "lines") and len(body_txt) >= 40:
                if not fm.get("texto_en"):
                    issues.append("texto solo en español")
                elif fm.get("traduccion") != "revisada":
                    issues.append("traducción al inglés en borrador (revisar y poner «traduccion: revisada»)")
            if coll == "lines" and fm.get("lang") == "en":
                pass
            n_alt = len(re.findall(r'include figura\.html[^%]*alt=""', body))
            if n_alt:
                issues.append(f"{n_alt} imagen(es) sin texto alternativo")
            for g in re.findall(r"include galeria\.html([^%]*)%", body):
                if "alts=" not in g:
                    n = len(re.search(r'fotos="([^"]*)"', g).group(1).split(","))
                    issues.append(f"galería de {n} fotos sin textos alternativos")
            n_todo = len(re.findall(r'class="todo"', body))
            if n_todo:
                issues.append(f"{n_todo} marcador(es) «por completar» en el texto")
            if issues:
                rows[name] = (fm, issues)
                totals[coll][1] += 1
    # Bibliografía
    bib_rows = []
    sys.path.insert(0, os.path.join(ROOT, "scripts", "migracion"))
    from bibtex_simple import get, parse  # noqa: E402
    papers = parse(open(os.path.join(ROOT, "_bibliography", "papers.bib"), encoding="utf-8").read())
    no_doi = [e["key"] for e in papers if not get(e, "doi")]
    no_portal = [e["key"] for e in papers if not get(e, "portal_upm")]
    no_project = [e["key"] for e in papers if not get(e, "project")]
    theses = parse(open(os.path.join(ROOT, "_bibliography", "theses.bib"), encoding="utf-8").read())
    no_sup = [e["key"] for e in theses if not get(e, "supervisor")]
    no_arch = [e["key"] for e in theses if not get(e, "archivo_upm")]
    bib_rows.append(f"Publicaciones sin DOI: {len(no_doi)} de {len(papers)}")
    bib_rows.append(f"Publicaciones sin enlace al Portal Científico (portal_upm): {len(no_portal)} de {len(papers)} "
                    "→ scripts/cruce_portal.py")
    bib_rows.append(f"Publicaciones sin proyecto asociado (project): {len(no_project)} de {len(papers)}")
    bib_rows.append(f"Tesis sin dirección (supervisor): {len(no_sup)} de {len(theses)}")
    bib_rows.append(f"Tesis sin enlace al Archivo Digital (archivo_upm): {len(no_arch)} de {len(theses)}")

    resumen = ["| Colección | Elementos | Con pendientes |", "|---|---|---|"]
    for coll, (n, k) in totals.items():
        resumen.append(f"| {LABEL[coll]} | {n} | {k} |")
    if "--resumen" in sys.argv:
        print("\n".join(resumen + [""] + ["- " + r for r in bib_rows]))
        return
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Pendientes de los datos\n\nGenerado por `scripts/informe_pendientes.py`. "
                 "En la web, lo que falta se ve con el marcador «por completar».\n\n## Resumen\n\n")
        fh.write("\n".join(resumen) + "\n\n## Bibliografía\n\n")
        fh.write("\n".join("- " + r for r in bib_rows) + "\n")
        current = None
        for name, (fm, issues) in rows.items():
            coll = name.split("/")[0][1:]
            if coll != current:
                fh.write(f"\n## {LABEL[coll]}\n\n")
                current = coll
            title = fm.get("acronym") or " ".join(x for x in (fm.get("given"), fm.get("family")) if x) or \
                fm.get("title_en") or fm.get("title_es") or ""
            fh.write(f"- **{title}** (`{name}`): " + "; ".join(issues) + "\n")
    print(f"Informe: {os.path.relpath(OUT, ROOT)}")
    print("\n".join(resumen))


if __name__ == "__main__":
    main()
