#!/usr/bin/env python3
"""
Sincroniza _bibliography/papers.bib con la biblioteca de grupo de Zotero.

    python scripts/sincronizar_zotero.py [--grupo 5287048] [--coleccion CLAVE]
                                         [--informe reports/zotero.md] [--seco]
    (clave de la API, si la biblioteca es privada: variable ZOTERO_API_KEY)

Lo usa .github/workflows/zotero.yml (semanal y a mano), que después ejecuta
aplicar_etiquetas.py y abre una PR con el informe.

Qué hace:
  · Descarga los ítems principales (sin notas ni adjuntos) con su BibTeX
    (API v3, de 100 en 100). Las tesis se excluyen: viven en theses.bib.
  · CONSERVA LAS CLAVES BibTeX existentes, porque de ellas dependen
    etiquetas.yml, las citas (cita.html) y las anclas. Cada ítem se empareja
    con su entrada actual por, en este orden:
      1. el identificador de Zotero ya conocido (_bibliography/zotero-claves.yml);
      2. el DOI;
      3. el título y el año (y el tipo, si hay varias candidatas).
    Los ítems nuevos reciben la clave que da Zotero (con sufijo a, b… si choca).
  · Antes de reescribir, copia a etiquetas.yml los campos propios
    (portal_upm, archivo_upm, project, lines) que solo estuvieran en el .bib,
    para que aplicar_etiquetas.py los vuelva a poner.
  · Etiquetas de Zotero «proyecto:<slug>» y «linea:<id>»: si un ítem tiene
    alguna, mandan sobre project/lines de etiquetas.yml. Así se puede
    clasificar una publicación desde Zotero.
  · Quita los campos internos (urldate, copyright, file…) y, de keywords, las
    etiquetas de servicio (proyecto:, linea:, ⛔…).
  · Si dos ítems se fusionan en Zotero, los campos propios de la entrada que
    desaparece pasan a la que queda (mismo título y año).
  · Por seguridad NO borra más del 10 % de las entradas (ni ninguna si Zotero
    devuelve 0 ítems) salvo con --permitir-borrados.

Sale con 0 si todo va bien (haya cambios o no), 2 si hay un error o se
detiene por seguridad. Escribe en el informe (Markdown) el resumen, y en
GITHUB_OUTPUT «cambios=true|false».
"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts", "migracion"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from bibtex_simple import drop_fields, dump, get, parse, set_field, unbrace  # noqa: E402
import aplicar_etiquetas as etq  # noqa: E402

BIB = os.path.join(ROOT, "_bibliography", "papers.bib")
MAPA = os.path.join(ROOT, "_bibliography", "zotero-claves.yml")
API = "https://api.zotero.org"
NO_PRINCIPALES = {"note", "attachment", "annotation"}
QUITAR = {"urldate", "copyright", "dimensions", "altmetric", "bibtex_show", "file", "annotation"}
PROPIOS = set(etq.FIELDS)                       # portal_upm, archivo_upm, project, lines
ETIQUETA_SERVICIO = re.compile(r"^(proyecto:|linea:|línea:|⛔|_)", re.I)
CABECERA_MAPA = ("# Identificador de cada ítem en Zotero → clave BibTeX en papers.bib.\n"
                 "# Lo mantiene scripts/sincronizar_zotero.py: asegura que las claves no cambian\n"
                 "# aunque se corrija el título o el DOI en Zotero. No hace falta editarlo.\n")


# ------------------------------------------------------------------ descarga
def descargar(grupo, coleccion=None, clave_api=None, pausa=time.sleep):
    base = f"{API}/groups/{grupo}" + (f"/collections/{coleccion}" if coleccion else "") + "/items/top"
    cab = {"Zotero-API-Version": "3", "User-Agent": "grys-web (sincronizar_zotero.py)"}
    if clave_api:
        cab["Zotero-API-Key"] = clave_api
    items, inicio, total = [], 0, None
    while total is None or inicio < total:
        q = urllib.parse.urlencode({"format": "json", "include": "data,bibtex", "limit": 100,
                                    "start": inicio, "sort": "dateAdded", "direction": "asc"})
        for intento in range(5):
            try:
                with urllib.request.urlopen(urllib.request.Request(f"{base}?{q}", headers=cab), timeout=60) as r:
                    lote = json.loads(r.read().decode("utf-8"))
                    total = int(r.headers.get("Total-Results", len(lote)))
                    if r.headers.get("Backoff"):
                        pausa(int(r.headers["Backoff"]))
                    break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and intento < 4:
                    pausa(int(e.headers.get("Retry-After") or 5 * (intento + 1)))
                    continue
                if e.code in (403, 404):
                    raise SystemExit(f"Zotero respondió {e.code}: ¿el grupo {grupo} es privado y falta ZOTERO_API_KEY, "
                                     "o la clave no tiene acceso a ese grupo?")
                raise
        items += lote
        inicio += len(lote)
        if not lote:
            break
    return items


# ------------------------------------------------------------------ utilidades
def norm(texto):
    t = unicodedata.normalize("NFKD", unbrace(texto or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", t)


def doi_de(entry):
    d = unbrace(get(entry, "doi") or "").strip().lower()
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", d)


def firma(entry):
    """Contenido comparable de una entrada: tipo y campos de Zotero (sin los propios)."""
    return (entry["type"], tuple((k, v.strip()) for k, v in entry["fields"] if k not in PROPIOS))


def limpiar(entry, avisos):
    drop_fields(entry, QUITAR)
    kw = get(entry, "keywords")
    if kw is not None:
        quedan = [t.strip() for t in unbrace(kw).split(",") if t.strip() and not ETIQUETA_SERVICIO.match(t.strip())]
        drop_fields(entry, {"keywords"})
        if quedan:
            set_field(entry, "keywords", ", ".join(quedan))
    # Los campos propios nunca vienen de Zotero
    drop_fields(entry, PROPIOS)
    return entry


def slugs(carpeta):
    return {os.path.splitext(f)[0] for f in os.listdir(os.path.join(ROOT, carpeta)) if f.endswith(".md")}


# ------------------------------------------------------------------ sincronización
def sincronizar(items, permitir_borrados=False):
    texto = open(BIB, encoding="utf-8").read()
    cabecera = re.match(r"((?:%[^\n]*\n)*\n?)", texto).group(1)
    actuales = parse(texto)
    por_clave = {e["key"]: e for e in actuales}
    mapa = (yaml.safe_load(open(MAPA, encoding="utf-8")) or {}) if os.path.exists(MAPA) else {}
    etiquetas = etq.load_tags()
    proyectos, lineas = slugs("_projects"), slugs("_lines")
    avisos, informe = [], {"nuevas": [], "cambiadas": [], "borradas": [], "sin_etiquetar": [], "clasificadas": []}

    # 0. Campos propios que solo están en el .bib → etiquetas.yml (no se pierden)
    rescatados = 0
    for e in actuales:
        for f in PROPIOS:
            v = unbrace(get(e, f) or "")
            if v and not (etiquetas.get(e["key"]) or {}).get(f):
                etiquetas.setdefault(e["key"], {})[f] = v
                rescatados += 1

    # 1. Ítems principales de Zotero
    principales = []
    for it in items:
        d = it.get("data") or {}
        if d.get("itemType") in NO_PRINCIPALES or d.get("itemType") == "thesis" or d.get("deleted"):
            continue
        bib = parse(it.get("bibtex") or "")
        if len(bib) != 1:
            avisos.append(f"el ítem {it.get('key')} («{d.get('title', '')[:60]}») no trae BibTeX; se omite")
            continue
        principales.append((it["key"], d, limpiar(bib[0], avisos)))
    if not principales:
        raise SystemExit("Zotero no ha devuelto ninguna publicación: no se cambia nada (¿grupo o colección equivocados?)")

    # 2. Emparejar con las entradas actuales
    libres = dict(por_clave)                     # entradas aún sin ítem
    por_doi = {}
    for k, e in por_clave.items():
        if doi_de(e):
            por_doi.setdefault(doi_de(e), []).append(k)
    asignadas = {}                                # zotero key → clave bib
    pendientes = []
    for zk, d, e in principales:
        k = mapa.get(zk)
        if k in libres:
            asignadas[zk] = k
            libres.pop(k)
        else:
            pendientes.append((zk, d, e))
    sin_par = []
    for zk, d, e in pendientes:                   # por DOI
        cand = [k for k in por_doi.get(doi_de(e), []) if k in libres] if doi_de(e) else []
        if len(cand) == 1:
            asignadas[zk] = cand[0]
            libres.pop(cand[0])
        else:
            sin_par.append((zk, d, e))
    nuevas = []
    for zk, d, e in sin_par:                      # por título + año (+ tipo)
        t, y = norm(get(e, "title")), unbrace(get(e, "year") or "")
        cand = [k for k, x in libres.items() if norm(get(x, "title")) == t and unbrace(get(x, "year") or "") == y]
        # Desempates (p. ej. el mismo trabajo en dos revistas): tipo, clave, título exacto, revista o libro
        criterios = (lambda k: libres[k]["type"] == e["type"],
                     lambda k: k == e["key"] or k.rstrip("abcdefghijklmnopqrstuvwxyz") == e["key"],
                     lambda k: unbrace(get(libres[k], "title")) == unbrace(get(e, "title")),
                     lambda k: norm(get(libres[k], "journal") or get(libres[k], "booktitle"))
                     == norm(get(e, "journal") or get(e, "booktitle")))
        for criterio in criterios:
            if len(cand) <= 1:
                break
            filtradas = [k for k in cand if criterio(k)]
            if filtradas:
                cand = filtradas
        if len(cand) == 1:
            asignadas[zk] = cand[0]
            libres.pop(cand[0])
        else:
            if len(cand) > 1:
                avisos.append(f"«{unbrace(get(e, 'title'))[:60]}» ({y}) coincide con varias entradas: se trata como nueva")
            nuevas.append((zk, d, e))

    # 3. Borrados: las entradas que ya no están en Zotero
    borradas = sorted(libres)
    limite = max(1, len(actuales) // 10)
    if borradas and not permitir_borrados and len(borradas) > limite:
        raise SystemExit(f"Se borrarían {len(borradas)} de {len(actuales)} publicaciones (límite {limite}). "
                         "Revisa el grupo o la colección; si es correcto, repite con «Permitir borrados».")

    # 4. Construir el nuevo papers.bib (orden actual; las nuevas, al principio)
    usadas = set(asignadas.values()) | set(borradas)
    resultado = {}
    for zk, d, e in principales:
        if zk in asignadas:
            k = asignadas[zk]
            e["key"] = k
            if firma(e) != firma(por_clave[k]):
                antes = dict(por_clave[k]["fields"])
                ahora = dict(e["fields"])
                campos = sorted(f for f in set(antes) | set(ahora)
                                if f not in PROPIOS and antes.get(f, "").strip() != ahora.get(f, "").strip())
                if por_clave[k]["type"] != e["type"]:
                    campos.insert(0, f"tipo {por_clave[k]['type']}→{e['type']}")
                informe["cambiadas"].append((k, unbrace(get(e, "title")), campos))
        else:
            k = base = e["key"]
            for suf in "abcdefghijklmnopqrstuvwxyz":
                if k not in usadas:
                    break
                k = base + suf
            e["key"] = k
            usadas.add(k)
            asignadas[zk] = k
            informe["nuevas"].append((k, unbrace(get(e, "title")), unbrace(get(e, "year") or "")))
        resultado[k] = e

    nuevas_claves = [k for k, _, _ in informe["nuevas"]]
    orden = nuevas_claves + [e["key"] for e in actuales if e["key"] in resultado]
    entradas = [resultado[k] for k in orden]
    informe["borradas"] = [(k, unbrace(get(por_clave[k], "title"))) for k in borradas]

    # 5. Etiquetas de Zotero proyecto:/linea:
    for zk, d, e in principales:
        tags = [t.get("tag", "").strip() for t in d.get("tags") or []]
        p = [t.split(":", 1)[1].strip() for t in tags if re.match(r"^proyecto:", t, re.I)]
        ln = [t.split(":", 1)[1].strip() for t in tags if re.match(r"^l[ií]nea:", t, re.I)]
        k = asignadas[zk]
        for nombre, valores, validos, campo in (("proyecto", p, proyectos, "project"), ("línea", ln, lineas, "lines")):
            if not valores:
                continue
            buenos = [v for v in valores if v in validos]
            for v in valores:
                if v not in validos:
                    avisos.append(f"{k}: la etiqueta de Zotero «{nombre}:{v}» no corresponde a ningún {nombre}; se ignora")
            if buenos:
                nuevo = ",".join(buenos)
                if (etiquetas.get(k) or {}).get(campo) != nuevo:
                    etiquetas.setdefault(k, {})[campo] = nuevo
                    informe["clasificadas"].append((k, campo, nuevo))
    # Fusiones en Zotero: si una entrada borrada tiene el mismo título y año que
    # otra que sigue, sus campos propios (p. ej. portal_upm) pasan a esa otra.
    informe["fusionadas"] = []
    for k in borradas:
        viejas = etiquetas.pop(k, None) or {}
        x = por_clave[k]
        destino = [c for c in orden if norm(get(resultado[c], "title")) == norm(get(x, "title"))
                   and unbrace(get(resultado[c], "year") or "") == unbrace(get(x, "year") or "")]
        if destino and viejas:
            movidos = []
            for campo, v in viejas.items():
                if not (etiquetas.get(destino[0]) or {}).get(campo):
                    etiquetas.setdefault(destino[0], {})[campo] = v
                    movidos.append(campo)
            if movidos:
                informe["fusionadas"].append((k, destino[0], movidos))

    for k in orden:
        t = etiquetas.get(k) or {}
        if not t.get("project") or not t.get("lines"):
            informe["sin_etiquetar"].append(k)

    # 6. Mapa de identificadores
    nuevo_mapa = {zk: asignadas[zk] for zk, _, _ in principales}

    nuevo_texto = cabecera + dump(entradas)
    return dict(texto=nuevo_texto, cambiado=nuevo_texto != texto, etiquetas=etiquetas, mapa=nuevo_mapa,
                mapa_cambiado=nuevo_mapa != mapa, informe=informe, avisos=avisos, rescatados=rescatados,
                n_zotero=len(principales), n_antes=len(actuales), n_despues=len(entradas))


def informe_md(r, grupo, coleccion):
    i = r["informe"]
    origen = f"grupo {grupo}" + (f", colección {coleccion}" if coleccion else "")
    L = [f"## Sincronización con Zotero ({datetime.date.today().isoformat()})", "",
         f"Biblioteca de Zotero: {origen} · {r['n_zotero']} publicaciones (sin tesis, notas ni adjuntos).", "",
         f"- Publicaciones en la web: **{r['n_antes']} → {r['n_despues']}**",
         f"- Nuevas: **{len(i['nuevas'])}** · Con cambios: **{len(i['cambiadas'])}** · Borradas: **{len(i['borradas'])}**"]
    if i["clasificadas"]:
        L.append(f"- Clasificadas desde etiquetas de Zotero: {len(i['clasificadas'])}")
    if r["rescatados"]:
        L.append(f"- Campos propios copiados del .bib a etiquetas.yml: {r['rescatados']}")
    if i["nuevas"]:
        L += ["", "### Nuevas", ""] + [f"- `{k}` · {t} ({y})" for k, t, y in i["nuevas"]]
    if i["cambiadas"]:
        L += ["", "### Con cambios", ""] + [f"- `{k}` · {t[:90]} — {', '.join(c)}" for k, t, c in i["cambiadas"]]
    if i["borradas"]:
        L += ["", "### Borradas (ya no están en Zotero)", "",
              "Revisa que sea intencionado. Si alguna se cita en un texto, «Comprobar PR» fallará.", ""]
        L += [f"- `{k}` · {t}" for k, t in i["borradas"]]
    if i.get("fusionadas"):
        L += ["", "### Fusionadas en Zotero", ""] + [f"- `{k}` → `{d}`: se conservan {', '.join(c)}" for k, d, c in i["fusionadas"]]
    if i["clasificadas"]:
        L += ["", "### Clasificadas con etiquetas de Zotero", ""] + [f"- `{k}`: {c} = {v}" for k, c, v in i["clasificadas"]]
    nuevas_sin = [k for k, _, _ in i["nuevas"] if k in i["sin_etiquetar"]]
    if nuevas_sin:
        L += ["", "### Nuevas sin proyecto o línea", "",
              "Para que salgan en las fichas de proyecto y de línea, añade en Zotero las etiquetas "
              "`proyecto:<slug>` y `linea:<id>` (o edítalo en `_bibliography/etiquetas.yml`).", ""]
        L += [f"- `{k}`" for k in nuevas_sin]
    if r["avisos"]:
        L += ["", "### Avisos", ""] + [f"- {a}" for a in r["avisos"]]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grupo", default=os.environ.get("ZOTERO_GRUPO") or "5287048")
    ap.add_argument("--coleccion", default=os.environ.get("ZOTERO_COLECCION") or None)
    ap.add_argument("--informe", default=os.path.join(ROOT, "reports", "zotero.md"))
    ap.add_argument("--desde-fichero", help="JSON con los ítems (pruebas, sin red)")
    ap.add_argument("--permitir-borrados", action="store_true")
    ap.add_argument("--seco", action="store_true", help="no escribe nada; solo el informe")
    a = ap.parse_args()
    try:
        items = (json.load(open(a.desde_fichero, encoding="utf-8")) if a.desde_fichero
                 else descargar(a.grupo, a.coleccion, os.environ.get("ZOTERO_API_KEY") or None))
        r = sincronizar(items, a.permitir_borrados)
    except SystemExit as e:
        msg = str(e)
        os.makedirs(os.path.dirname(a.informe), exist_ok=True)
        open(a.informe, "w", encoding="utf-8").write(f"## Sincronización con Zotero\n\n❌ {msg}\n")
        print(f"sincronizar_zotero: {msg}")
        sys.exit(2)
    md = informe_md(r, a.grupo, a.coleccion)
    os.makedirs(os.path.dirname(a.informe), exist_ok=True)
    open(a.informe, "w", encoding="utf-8").write(md)
    hay = r["cambiado"] or r["mapa_cambiado"] or r["rescatados"] or r["informe"]["clasificadas"]
    if not a.seco:
        if r["cambiado"]:
            open(BIB, "w", encoding="utf-8", newline="\n").write(r["texto"])
        etq.save_tags(r["etiquetas"])
        with open(MAPA, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(CABECERA_MAPA)
            fh.write(yaml.safe_dump(dict(sorted(r["mapa"].items())), allow_unicode=True, sort_keys=False, width=1000))
    i = r["informe"]
    print(f"sincronizar_zotero: {r['n_zotero']} en Zotero · {len(i['nuevas'])} nuevas, {len(i['cambiadas'])} con cambios, "
          f"{len(i['borradas'])} borradas · informe: {os.path.relpath(a.informe, ROOT)}")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as fh:
            fh.write(f"cambios={'true' if hay else 'false'}\n")


if __name__ == "__main__":
    main()
