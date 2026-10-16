#!/usr/bin/env python3
"""
Aplica _bibliography/etiquetas.yml a papers.bib y theses.bib.

    python3 scripts/aplicar_etiquetas.py            # aplica y guarda
    python3 scripts/aplicar_etiquetas.py --comprobar  # solo comprueba (código 1 si no están aplicadas)

Por qué existe: el BibTeX se regenera desde Zotero, y Zotero no conoce los
campos propios del sitio. Esos campos viven en etiquetas.yml (una entrada por
clave BibTeX) y se vuelven a escribir en el .bib tras cada sincronización:
  portal_upm   ID del ítem en el Portal Científico UPM (…/ipublic/item/<ID>)
  archivo_upm  ID en el Archivo Digital UPM (oa.upm.es/<ID>)
  project      slug(s) de _projects separados por comas
  lines        id(s) de _lines separados por comas
"""
import os
import re
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts", "migracion"))
from bibtex_simple import dump, get, parse, set_field, unbrace  # noqa: E402

FILES = ["papers.bib", "theses.bib"]
FIELDS = ["portal_upm", "archivo_upm", "project", "lines"]
TAGS = os.path.join(ROOT, "_bibliography", "etiquetas.yml")
HEADER = (
    "# Campos propios del sitio para cada entrada del BibTeX (clave → campos).\n"
    "# Sobreviven a la sincronización con Zotero: scripts/aplicar_etiquetas.py los\n"
    "# vuelve a escribir en papers.bib y theses.bib.\n"
    "#   portal_upm: ID en el Portal Científico UPM · archivo_upm: ID en oa.upm.es\n"
    "#   project: slug(s) de _projects (separados por comas) · lines: id(s) de _lines\n"
)


def load_tags():
    if not os.path.exists(TAGS):
        return {}
    return yaml.safe_load(open(TAGS, encoding="utf-8")) or {}


def save_tags(tags):
    tags = {k: {f: str(v[f]) for f in FIELDS if v.get(f) not in (None, "")} for k, v in sorted(tags.items())}
    tags = {k: v for k, v in tags.items() if v}
    with open(TAGS, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(HEADER)
        fh.write(yaml.safe_dump(tags, allow_unicode=True, sort_keys=False, width=1000))


def apply(check_only=False):
    tags = load_tags()
    changed, unknown = 0, set(tags)
    for f in FILES:
        path = os.path.join(ROOT, "_bibliography", f)
        text = open(path, encoding="utf-8").read()
        head = re.match(r"((?:%[^\n]*\n)*\n?)", text).group(1)
        entries = parse(text)
        for e in entries:
            t = tags.get(e["key"])
            if not t:
                continue
            unknown.discard(e["key"])
            for k in FIELDS:
                if t.get(k) not in (None, "") and unbrace(get(e, k)) != str(t[k]):
                    changed += 1
                    if not check_only:
                        set_field(e, k, str(t[k]))
        if changed and not check_only:
            open(path, "w", encoding="utf-8", newline="\n").write(head + dump(entries))
    return changed, sorted(unknown)


def main():
    check = "--comprobar" in sys.argv
    changed, unknown = apply(check)
    for k in unknown:
        print(f"AVISO  etiquetas.yml: la clave «{k}» no está en ningún .bib (¿ha cambiado en Zotero?)")
    if check:
        print(f"aplicar_etiquetas: {changed} campos pendientes de aplicar")
        sys.exit(1 if changed else 0)
    print(f"aplicar_etiquetas: {changed} campos escritos en el BibTeX")


if __name__ == "__main__":
    main()
