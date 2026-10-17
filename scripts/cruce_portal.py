#!/usr/bin/env python3
"""
Cruza el BibTeX del sitio con una exportación del Portal Científico UPM (o del
Archivo Digital UPM) e informa de lo que falta EN CADA LADO.

    python scripts/cruce_portal.py --fuente portal EXPORTACION.csv            # solo informe
    python scripts/cruce_portal.py --fuente portal EXPORTACION.csv --aplicar  # además, enlaces

EXPORTACION.csv del Portal Científico: ficha del grupo → exportar CSV. Se puede
usar la de «publicaciones» o la de «todos los ítems» del grupo: el script se
queda solo con las filas cuyo TIPO es «Publicaciones» o «Trabajos presentados
en Congresos u Otros Eventos» y cuenta las demás.

Del Portal se leen: TÍTULO, FECHA, INDENTIFICADOR (DOI) y PIDs, de donde salen
  · «NNNN (iMarina)»                → portal_upm  (enlace …/ipublic/item/NNNN)
  · «https://oa.upm.es/NNNN/ (Archivo Digital UPM)» → archivo_upm
  · «10.xxxx/… (Crossref)»          → DOI
También acepta CSV genéricos (columnas DOI, Título, Año, ID/URL) y RIS.

Cruce: primero por DOI; si no, por título normalizado y año (±1).

Informe (reports/cruce-<fuente>.md):
  1. coincidencias y enlaces que se añadirían,
  2. en el BibTeX y NO en la fuente (solo años cubiertos por la exportación)
     → pendientes de dar de alta / asociar al grupo en el Portal,
  3. en la fuente y NO en el BibTeX → pendientes de añadir a Zotero,
  4. avisos: duplicados en el Portal, discrepancias de año o DOI, ítems sin ID.
--aplicar guarda los enlaces en _bibliography/etiquetas.yml (sobreviven a la
sincronización con Zotero) y los escribe en papers.bib. Nunca sustituye un
enlace que ya exista.
"""
import argparse
import csv
import io
import os
import re
import sys
import unicodedata
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts", "migracion"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from bibtex_simple import get, parse, unbrace  # noqa: E402

PORTAL_ITEM = "https://portalcientifico.upm.es/es/ipublic/item/{}"
ARCHIVO_ITEM = "https://oa.upm.es/{}/"
KEEP_TIPOS = {"publicaciones", "trabajos presentados en congresos u otros eventos"}


def norm_text(s):
    s = re.sub(r"\((est[aá] )?en revisi[oó]n\)", "", s or "", flags=re.I)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "", s)


def norm_doi(s):
    s = (s or "").strip().lower()
    s = re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", s)
    return s if s.startswith("10.") else None


def year_of(s):
    m = re.search(r"(19|20)\d{2}", str(s or ""))
    return int(m.group(0)) if m else None


def new_rec():
    return {"doi": None, "title": "", "raw_title": "", "year": None, "portal": [], "archivo": [], "tipo": ""}


def parse_pids(text, rec):
    for part in (text or "").split(";"):
        m = re.match(r"\s*(.*?)\s*\(([^()]+)\)\s*$", part)
        if not m:
            continue
        value, src = m.group(1), m.group(2).strip().lower()
        if src == "imarina" and value.isdigit():
            rec["portal"].append(value)
        elif src.startswith("archivo digital"):
            a = re.search(r"oa\.upm\.es/(?:id/eprint/)?(\d+)", value)
            if a:
                rec["archivo"].append(a.group(1))
        elif src == "crossref" and not rec["doi"]:
            rec["doi"] = norm_doi(value)


def head_key(h):
    n = norm_text(h)
    if n == "pids":
        return "pids"
    if n in ("tipo", "type"):
        return "tipo"
    if "doi" in n or n in ("identificador", "indentificador", "identifier"):
        return "doi"
    if n.startswith(("titulo", "title")):
        return "title"
    if n in ("ano", "year", "fecha", "date", "anopublicacion", "publicationyear"):
        return "year"
    if n in ("id", "url", "enlace", "link", "uri"):
        return "id"
    return None


def read_csv(path, source, skipped):
    raw = open(path, encoding="utf-8-sig", errors="replace").read()
    dialect = csv.Sniffer().sniff(raw[:4096], delimiters=",;\t")
    rows = list(csv.reader(io.StringIO(raw), dialect))
    keys = [head_key(h) for h in rows[0]]
    if "title" not in keys:
        sys.exit(f"No encuentro la columna del título en {os.path.basename(path)}. Cabecera: {rows[0]}")
    out = []
    for r in rows[1:]:
        rec = new_rec()
        for k, v in zip(keys, r):
            v = (v or "").strip()
            if k == "doi" and not rec["doi"]:
                rec["doi"] = norm_doi(v)
            elif k == "title" and not rec["raw_title"]:
                rec["raw_title"], rec["title"] = v, norm_text(v)
            elif k == "year" and not rec["year"]:
                rec["year"] = year_of(v)
            elif k == "tipo":
                rec["tipo"] = re.sub(r"\s+", " ", v)
            elif k == "pids":
                parse_pids(v, rec)
            elif k == "id":
                m = re.search(r"/ipublic/item/(\d+)", v)
                a = re.search(r"oa\.upm\.es/(?:id/eprint/)?(\d+)", v)
                if m:
                    rec["portal"].append(m.group(1))
                elif a:
                    rec["archivo"].append(a.group(1))
        if rec["tipo"] and rec["tipo"].lower() not in KEEP_TIPOS:
            skipped[rec["tipo"]] += 1
            continue
        if rec["title"] or rec["doi"]:
            out.append(rec)
    return out


def read_ris(path, source, skipped):
    out, rec = [], None
    for line in open(path, encoding="utf-8-sig", errors="replace"):
        m = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", line.rstrip("\n"))
        if not m:
            continue
        tag, val = m.groups()
        if tag == "TY":
            rec = new_rec()
        elif rec is None:
            continue
        elif tag == "DO":
            rec["doi"] = norm_doi(val)
        elif tag in ("TI", "T1") and not rec["raw_title"]:
            rec["raw_title"], rec["title"] = val.strip(), norm_text(val)
        elif tag in ("PY", "Y1", "DA") and not rec["year"]:
            rec["year"] = year_of(val)
        elif tag in ("UR", "L2", "ID", "AN"):
            p = re.search(r"/ipublic/item/(\d+)", val)
            a = re.search(r"oa\.upm\.es/(?:id/eprint/)?(\d+)", val)
            if p:
                rec["portal"].append(p.group(1))
            elif a:
                rec["archivo"].append(a.group(1))
        elif tag == "ER":
            if rec["title"] or rec["doi"]:
                out.append(rec)
            rec = None
    return out


def merge_duplicates(rows):
    """El Portal repite a veces una publicación (otra fila, otro ID). Se agrupan
    las filas con el mismo DOI o el mismo título normalizado y se juntan sus IDs."""
    groups, by_key = [], {}
    for r in rows:
        keys = [k for k in (("doi", r["doi"]), ("t", r["title"])) if k[1]]
        g = next((by_key[k] for k in keys if k in by_key), None)
        if g is None:
            g = {**new_rec(), "rows": 0}
            groups.append(g)
        g["rows"] += 1
        for fld in ("doi", "raw_title", "title", "year", "tipo"):
            if not g[fld] and r[fld]:
                g[fld] = r[fld]
        for fld in ("portal", "archivo"):
            g[fld] += [x for x in r[fld] if x not in g[fld]]
        for k in keys:
            by_key.setdefault(k, g)
        if g["doi"]:
            by_key.setdefault(("doi", g["doi"]), g)
    return groups


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fuente", choices=["portal", "archivo"], required=True)
    ap.add_argument("exportacion")
    ap.add_argument("--aplicar", action="store_true")
    args = ap.parse_args()
    if not os.path.isfile(args.exportacion):
        sys.exit(f"No existe el fichero {args.exportacion}")
    skipped = Counter()
    reader = read_ris if args.exportacion.lower().endswith(".ris") else read_csv
    ext_rows = reader(args.exportacion, args.fuente, skipped)
    if not ext_rows:
        sys.exit("La exportación no tiene ninguna publicación reconocible.")
    n_rows = len(ext_rows)
    ext_rows = merge_duplicates(ext_rows)
    years = [r["year"] for r in ext_rows if r["year"]]
    y_min = min(years) if years else None

    files = ["papers.bib"] + (["theses.bib"] if args.fuente == "archivo" else [])
    entries = [(f, e) for f in files
               for e in parse(open(os.path.join(ROOT, "_bibliography", f), encoding="utf-8").read())]

    by_doi, by_title = {}, {}
    for i, r in enumerate(ext_rows):
        if r["doi"]:
            by_doi.setdefault(r["doi"], i)
        if r["title"]:
            by_title.setdefault(r["title"], []).append(i)

    matched, only_bib, used = [], [], set()
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
            only_bib.append((f, e, year))
        else:
            used.add(idx)
            matched.append((f, e, ext_rows[idx], how, doi, year))
    only_ext = [r for i, r in enumerate(ext_rows) if i not in used]

    # Enlaces propuestos y avisos
    import aplicar_etiquetas as ae  # noqa: E402
    tags = ae.load_tags()
    proposals, warnings = [], []
    for f, e, r, how, doi, year in matched:
        k = e["key"]
        have = tags.get(k, {})
        add = {}
        if args.fuente == "portal" and r["portal"]:
            if len(r["portal"]) > 1 or r["rows"] > 1:
                ids = ", ".join(f"[{i}]({PORTAL_ITEM.format(i)})" for i in r["portal"])
                donde = f"{r['rows']} filas" if r["rows"] > 1 else "una fila con varios IDs"
                warnings.append(f"`{k}`: **duplicado en el Portal** ({donde}; IDs: {ids}); "
                                f"se enlaza {r['portal'][0]}. Para elegir otro, cámbialo en etiquetas.yml")
            if not have.get("portal_upm") and not get(e, "portal_upm"):
                add["portal_upm"] = r["portal"][0]
        if r["archivo"] and not have.get("archivo_upm") and not get(e, "archivo_upm"):
            add["archivo_upm"] = r["archivo"][0]
        if args.fuente == "portal" and not r["portal"]:
            warnings.append(f"`{k}`: coincide con el Portal pero la exportación no trae su identificador (iMarina)")
        if r["year"] and year and r["year"] != year:
            warnings.append(f"`{k}`: año {year} en el BibTeX y {r['year']} en la fuente")
        if r["doi"] and doi and r["doi"] != doi:
            warnings.append(f"`{k}`: DOI {doi} en el BibTeX y {r['doi']} en la fuente")
        if r["doi"] and not doi:
            warnings.append(f"`{k}`: sin DOI en el BibTeX; la fuente da {r['doi']} (corregir en Zotero)")
        proposals.append((k, how, add, have))

    added = Counter()
    if args.aplicar:
        for k, how, add, have in proposals:
            for fld, val in add.items():
                tags.setdefault(k, {})[fld] = val
                added[fld] += 1
        ae.save_tags(tags)
        ae.apply()

    only_bib_in = [(f, e, y) for f, e, y in only_bib if y_min is None or (y and y >= y_min)]
    only_bib_old = len(only_bib) - len(only_bib_in)

    name = {"portal": "Portal Científico UPM", "archivo": "Archivo Digital UPM"}[args.fuente]
    out = os.path.join(ROOT, "reports", f"cruce-{args.fuente}.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    n_portal = sum(1 for _, _, a, _ in proposals if "portal_upm" in a)
    n_arch = sum(1 for _, _, a, _ in proposals if "archivo_upm" in a)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# Cruce BibTeX ↔ {name}\n\n")
        fh.write(f"Exportación: `{os.path.basename(args.exportacion)}` · {n_rows} filas → "
                 f"{len(ext_rows)} publicaciones distintas")
        fh.write(f" ({y_min}–{max(years)})" if years else "")
        if skipped:
            fh.write(" · descartadas por tipo: " + ", ".join(f"{k} ({v})" for k, v in skipped.items()))
        fh.write(f"\nBibTeX: {len(entries)} entradas\n\n")
        fh.write("| | |\n|---|---|\n")
        fh.write(f"| Coincidencias | {len(matched)} |\n")
        fh.write(f"| → enlaces al Portal (`portal_upm`) {'añadidos' if args.aplicar else 'que se añadirían'} | {n_portal} |\n")
        fh.write(f"| → enlaces al Archivo Digital (`archivo_upm`) {'añadidos' if args.aplicar else 'que se añadirían'} | {n_arch} |\n")
        fh.write(f"| Solo en el BibTeX, desde {y_min} (pendientes en el Portal) | {len(only_bib_in)} |\n")
        fh.write(f"| Solo en el BibTeX, anteriores a {y_min} (fuera del periodo de la exportación) | {only_bib_old} |\n")
        fh.write(f"| Solo en {name} (pendientes de añadir a Zotero) | {len(only_ext)} |\n")
        fh.write(f"| Avisos | {len(warnings)} |\n\n")
        fh.write("## 1. Coincidencias\n\n")
        for k, how, add, have in proposals:
            txt = ", ".join(f"{f_} = {v}" for f_, v in add.items()) or "nada nuevo"
            fh.write(f"- `{k}` (por {how}): {txt}\n")
        fh.write(f"\n## 2. Solo en el BibTeX (desde {y_min}): pendientes de dar de alta o asociar al grupo en el Portal\n\n")
        for f, e, y in sorted(only_bib_in, key=lambda t: -(t[2] or 0)):
            fh.write(f"- {y} · {unbrace(get(e, 'title'))} · `{e['key']}`\n")
        fh.write(f"\n## 3. Solo en el {name}: pendientes de añadir a Zotero\n\n")
        for r in sorted(only_ext, key=lambda r: -(r["year"] or 0)):
            link = f" · [ficha]({PORTAL_ITEM.format(r['portal'][0])})" if r["portal"] else " · sin ID en la exportación"
            dup = f" · {r['rows']} filas en el Portal" if r["rows"] > 1 else ""
            fh.write(f"- {r['year'] or '¿año?'} · {r['tipo'] or ''} · {r['raw_title']}"
                     f"{' · DOI ' + r['doi'] if r['doi'] else ''}{link}{dup}\n")
        fh.write("\n## 4. Avisos\n\n" + ("".join(f"- {w}\n" for w in warnings) or "Ninguno.\n"))
    print(f"{n_rows} filas = {len(ext_rows)} publicaciones distintas ({y_min}–{max(years) if years else '?'})"
          + (f", {sum(skipped.values())} filas de otros tipos descartadas" if skipped else ""))
    print(f"{len(matched)} coincidencias → {n_portal} enlaces al Portal y {n_arch} al Archivo Digital "
          f"{'AÑADIDOS' if args.aplicar else 'propuestos (sin aplicar)'}")
    print(f"{len(only_bib_in)} solo en el BibTeX desde {y_min} · {len(only_ext)} solo en la fuente · {len(warnings)} avisos")
    print(f"Informe: {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
