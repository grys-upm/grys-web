#!/usr/bin/env python3
"""
Cruza el BibTeX del sitio con una exportación del Portal Científico UPM o del
Archivo Digital UPM y genera un informe de pendientes EN AMBOS SENTIDOS.

    python3 scripts/cruce_portal.py --fuente portal  EXPORTACION.csv|.ris [--aplicar]
    python3 scripts/cruce_portal.py --fuente archivo EXPORTACION.csv|.ris [--aplicar]

Entrada: CSV (cualquier separador) o RIS. Del CSV se reconocen columnas por su
nombre (sin distinguir mayúsculas ni acentos): DOI · Título/Title ·
Año/Year/Fecha · ID/Identificador/URL/Enlace. El identificador se saca del
número o de la URL (…/ipublic/item/NNNN en el Portal; oa.upm.es/NNNN en el Archivo).

Cruce: primero por DOI; si no hay, por título normalizado y año (±1).

Salida: reports/cruce-<fuente>.md con
  1. coincidencias (y si el BibTeX ya tiene el enlace),
  2. en el BibTeX pero NO en la fuente  → pendiente de dar de alta allí,
  3. en la fuente pero NO en el BibTeX  → pendiente de añadir a Zotero,
  4. discrepancias de año o DOI.
--aplicar escribe portal_upm / archivo_upm en papers.bib (y theses.bib) para
las coincidencias que aún no lo tengan. Después hay que llevar ese dato a
Zotero (campo «Extra»), o la siguiente sincronización lo borraría.
"""
import argparse
import csv
import io
import os
import re
import sys
import unicodedata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts", "migracion"))
from bibtex_simple import dump, get, parse, set_field, unbrace  # noqa: E402

FIELD = {"portal": "portal_upm", "archivo": "archivo_upm"}
ID_RE = {"portal": r"/ipublic/item/(\d+)", "archivo": r"oa\.upm\.es/(?:id/eprint/)?(\d+)"}


def norm_text(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def norm_doi(s):
    s = (s or "").strip().lower()
    s = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", s)
    return s or None


def year_of(s):
    m = re.search(r"(19|20)\d{2}", str(s or ""))
    return int(m.group(0)) if m else None


def head_key(h):
    h = norm_text(h)
    if "doi" in h:
        return "doi"
    if h.startswith(("titulo", "title")):
        return "title"
    if h in ("ano", "year", "fecha", "date", "anopublicacion", "publicationyear") or h.startswith(("ano", "year")):
        return "year"
    if h in ("id", "identificador", "identifier", "url", "enlace", "link", "uri") or h.startswith(("url", "enlace")):
        return "id"
    return None


def read_csv(path, source):
    raw = open(path, encoding="utf-8-sig", errors="replace").read()
    dialect = csv.Sniffer().sniff(raw[:4096], delimiters=",;\t")
    rows = list(csv.reader(io.StringIO(raw), dialect))
    keys = [head_key(h) for h in rows[0]]
    out = []
    for r in rows[1:]:
        rec = {"doi": None, "title": "", "year": None, "id": None, "raw_title": ""}
        for k, v in zip(keys, r):
            if k == "doi":
                rec["doi"] = norm_doi(v)
            elif k == "title" and not rec["raw_title"]:
                rec["raw_title"], rec["title"] = v.strip(), norm_text(v)
            elif k == "year" and not rec["year"]:
                rec["year"] = year_of(v)
            elif k == "id" and not rec["id"]:
                m = re.search(ID_RE[source], v)
                rec["id"] = m.group(1) if m else (v.strip() if v.strip().isdigit() else None)
        if rec["title"] or rec["doi"]:
            out.append(rec)
    return out


def read_ris(path, source):
    out, rec = [], None
    for line in open(path, encoding="utf-8-sig", errors="replace"):
        m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", line.rstrip("\n"))
        if not m:
            continue
        tag, val = m.groups()
        if tag == "TY":
            rec = {"doi": None, "title": "", "year": None, "id": None, "raw_title": ""}
        elif rec is None:
            continue
        elif tag == "DO":
            rec["doi"] = norm_doi(val)
        elif tag in ("TI", "T1") and not rec["raw_title"]:
            rec["raw_title"], rec["title"] = val.strip(), norm_text(val)
        elif tag in ("PY", "Y1", "DA") and not rec["year"]:
            rec["year"] = year_of(val)
        elif tag in ("UR", "L2", "ID", "AN") and not rec["id"]:
            mm = re.search(ID_RE[source], val)
            if mm:
                rec["id"] = mm.group(1)
        elif tag == "ER":
            if rec["title"] or rec["doi"]:
                out.append(rec)
            rec = None
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fuente", choices=["portal", "archivo"], required=True)
    ap.add_argument("exportacion")
    ap.add_argument("--aplicar", action="store_true")
    args = ap.parse_args()
    field = FIELD[args.fuente]
    ext = os.path.splitext(args.exportacion)[1].lower()
    ext_rows = read_ris(args.exportacion, args.fuente) if ext == ".ris" else read_csv(args.exportacion, args.fuente)

    files = ["papers.bib"] + (["theses.bib"] if args.fuente == "archivo" else [])
    bibs = {f: parse(open(os.path.join(ROOT, "_bibliography", f), encoding="utf-8").read()) for f in files}
    entries = [(f, e) for f, es in bibs.items() for e in es]

    by_doi, by_title = {}, {}
    for i, r in enumerate(ext_rows):
        if r["doi"]:
            by_doi.setdefault(r["doi"], i)
        if r["title"]:
            by_title.setdefault(r["title"], []).append(i)

    matched, only_bib, diffs, used = [], [], [], set()
    for f, e in entries:
        doi = norm_doi(unbrace(get(e, "doi")))
        title = norm_text(unbrace(get(e, "title")))
        year = year_of(unbrace(get(e, "year")))
        idx, how = None, None
        if doi and doi in by_doi and by_doi[doi] not in used:
            idx, how = by_doi[doi], "DOI"
        else:
            for j in by_title.get(title, []):
                if j not in used and (ext_rows[j]["year"] is None or year is None or abs(ext_rows[j]["year"] - year) <= 1):
                    idx, how = j, "título"
                    break
        if idx is None:
            only_bib.append((f, e))
            continue
        used.add(idx)
        r = ext_rows[idx]
        matched.append((f, e, r, how))
        if r["year"] and year and r["year"] != year:
            diffs.append(f"`{e['key']}`: año {year} en BibTeX y {r['year']} en la fuente")
        if r["doi"] and doi and r["doi"] != doi:
            diffs.append(f"`{e['key']}`: DOI {doi} en BibTeX y {r['doi']} en la fuente")
        if r["doi"] and not doi:
            diffs.append(f"`{e['key']}`: sin DOI en BibTeX; la fuente da {r['doi']}")
    only_ext = [r for i, r in enumerate(ext_rows) if i not in used]

    applied = 0
    had = {e["key"] for _, e, _, _ in matched if get(e, field)}
    if args.aplicar:
        # Se guarda en etiquetas.yml (sobrevive a la sincronización con Zotero) y se aplica al .bib
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import aplicar_etiquetas as ae  # noqa: E402
        tags = ae.load_tags()
        for f, e, r, _ in matched:
            if r["id"] and not get(e, field):
                tags.setdefault(e["key"], {})[field] = r["id"]
                applied += 1
        ae.save_tags(tags)
        ae.apply()

    name = {"portal": "Portal Científico UPM", "archivo": "Archivo Digital UPM"}[args.fuente]
    out = os.path.join(ROOT, "reports", f"cruce-{args.fuente}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# Cruce BibTeX ↔ {name}\n\nFuente: `{os.path.basename(args.exportacion)}` "
                 f"({len(ext_rows)} registros) · BibTeX: {len(entries)} entradas\n\n")
        fh.write(f"| | |\n|---|---|\n| Coincidencias | {len(matched)} |\n"
                 f"| Solo en el BibTeX (dar de alta en {name}) | {len(only_bib)} |\n"
                 f"| Solo en {name} (añadir a Zotero) | {len(only_ext)} |\n| Discrepancias | {len(diffs)} |\n")
        if args.aplicar:
            fh.write(f"| Enlaces `{field}` añadidos al BibTeX | {applied} |\n")
        fh.write(f"\n## 1. Coincidencias\n\n")
        for f, e, r, how in matched:
            if e["key"] in had:
                have = "ya enlazada"
            elif r["id"]:
                have = f"{'añadido' if args.aplicar else 'propuesto'}: {field} = {r['id']}"
            else:
                have = "sin identificador en la fuente"
            fh.write(f"- `{e['key']}` ({how}) {have}\n")
        fh.write(f"\n## 2. Solo en el BibTeX: pendientes de dar de alta en {name}\n\n")
        for f, e in only_bib:
            fh.write(f"- `{e['key']}` · {unbrace(get(e, 'year'))} · {unbrace(get(e, 'title'))}\n")
        fh.write(f"\n## 3. Solo en {name}: pendientes de añadir a Zotero\n\n")
        for r in only_ext:
            fh.write(f"- {r['year'] or '¿año?'} · {r['raw_title']}{' · DOI ' + r['doi'] if r['doi'] else ''}"
                     f"{' · id ' + r['id'] if r['id'] else ''}\n")
        fh.write("\n## 4. Discrepancias\n\n" + ("".join(f"- {d}\n" for d in diffs) or "Ninguna.\n"))
    print(f"{len(matched)} coincidencias, {len(only_bib)} solo en BibTeX, {len(only_ext)} solo en la fuente, "
          f"{len(diffs)} discrepancias{f', {applied} enlaces añadidos' if args.aplicar else ''} → "
          f"{os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
