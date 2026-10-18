#!/usr/bin/env python3
"""
Métricas de citas de las publicaciones (Dimensions Metrics API) → _data/metricas_pubs.yml

    python scripts/metricas_dimensions.py              # actualiza si los datos tienen más de 7 días
    python scripts/metricas_dimensions.py --forzar     # actualiza ya
    python scripts/metricas_dimensions.py --max-edad 1 # umbral de antigüedad en días

Se ejecuta en GitHub Actions ANTES de compilar (deploy.yml): el visitante no se
conecta con Dimensions; las cifras van ya en el HTML. El fichero resultante se
guarda en la caché de Actions entre compilaciones (no se sube al repositorio).

· API: https://metrics-api.dimensions.ai/doi/<DOI>  (gratuita para uso no
  comercial de organizaciones registradas; exige atribución en la página donde
  se muestran los datos: la pone _includes/listas/publicaciones.html).
· Nunca rompe la compilación: si la API falla, conserva los datos anteriores
  (o deja el fichero vacío) y sale con código 0 avisando en el registro.
· Si hay DOI nuevos en papers.bib y los datos están al día, solo pide esos.
Solo usa la biblioteca estándar + PyYAML.
"""
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BIB = os.path.join(ROOT, "_bibliography", "papers.bib")
OUT = os.path.join(ROOT, "_data", "metricas_pubs.yml")
API = "https://metrics-api.dimensions.ai/doi/"
UA = "GRyS-web/1.0 (+https://grys.etsist.upm.es; gi.grys@upm.es)"

CABECERA = """\
# GENERADO por scripts/metricas_dimensions.py: NO editar a mano.
# Citas de cada publicación según Dimensions (Digital Science), por DOI en minúsculas.
# En el repositorio queda vacío; en GitHub Actions se rellena antes de compilar.
"""


def dois_del_bib(path=BIB):
    txt = open(path, encoding="utf-8").read()
    out = []
    for m in re.finditer(r"^\s*doi\s*=\s*[{\"]\s*(.+?)\s*[}\"]\s*,?\s*$", txt, re.M | re.I):
        d = m.group(1).strip().strip("{}").lower()
        d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
        if d and d not in out:
            out.append(d)
    return out


def leer(path=OUT):
    if not os.path.exists(path):
        return {}
    return yaml.safe_load(open(path, encoding="utf-8")) or {}


def escribir(datos, path=OUT):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(CABECERA)
        yaml.safe_dump(datos, fh, allow_unicode=True, sort_keys=True, default_flow_style=False)
    os.replace(tmp, path)


def pedir(doi, timeout=20):
    """Devuelve el JSON de la API, None si Dimensions no conoce el DOI. Lanza
    excepción si hay un error de red o del servicio."""
    url = API + urllib.parse.quote(doi, safe="/")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def resumir(js):
    """Solo lo que se muestra; nada si no hay citas."""
    if not js:
        return None
    citas = int(js.get("times_cited") or 0)
    if citas <= 0:
        return None
    r = {"citas": citas}
    for k_api, k in (("recent_citations", "recientes"), ("field_citation_ratio", "fcr"),
                     ("relative_citation_ratio", "rcr")):
        v = js.get(k_api)
        if isinstance(v, (int, float)) and v > 0:
            r[k] = round(float(v), 2) if k in ("fcr", "rcr") else int(v)
    return r


def main(argv=None, fetch=pedir, hoy=None, pausa=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--forzar", action="store_true", help="actualizar aunque los datos sean recientes")
    ap.add_argument("--max-edad", type=int, default=7, help="días de validez de los datos (por defecto 7)")
    ap.add_argument("--pausa", type=float, default=0.25, help="segundos entre peticiones")
    ap.add_argument("--salida", default=OUT)
    args = ap.parse_args(argv)
    hoy = hoy or datetime.date.today()
    pausa = args.pausa if pausa is None else pausa

    dois = dois_del_bib()
    prev = leer(args.salida)
    prev_items = prev.get("items") or {}
    prev_fecha = prev.get("fecha")
    if isinstance(prev_fecha, str):
        try:
            prev_fecha = datetime.date.fromisoformat(prev_fecha)
        except ValueError:
            prev_fecha = None
    consultados = set(prev.get("consultados") or [])

    al_dia = prev_fecha and (hoy - prev_fecha).days < args.max_edad and not args.forzar
    if al_dia:
        pendientes = [d for d in dois if d not in consultados]
        if not pendientes:
            print(f"metricas: al día ({prev_fecha}, {len(prev_items)} publicaciones con citas); no se consulta la API")
            return 0
        print(f"metricas: al día ({prev_fecha}); se consultan solo {len(pendientes)} DOI nuevos")
    else:
        pendientes = dois

    items = dict(prev_items) if al_dia else {}
    ok = fallos = 0
    for i, d in enumerate(pendientes):
        try:
            r = resumir(fetch(d))
            ok += 1
            consultados.add(d)
            if r:
                items[d] = r
            else:
                items.pop(d, None)
        except Exception as e:  # red, 5xx, JSON… nunca rompe la compilación
            fallos += 1
            if fallos <= 3:
                print(f"metricas: AVISO {d}: {e}", file=sys.stderr)
        if pausa and i < len(pendientes) - 1:
            time.sleep(pausa)

    if pendientes and fallos > len(pendientes) / 2:
        print(f"::warning::metricas: la API de Dimensions ha fallado en {fallos} de {len(pendientes)} "
              "consultas; se conservan los datos anteriores")
        return 0

    # Conservar datos anteriores de los DOI que hayan fallado esta vez
    for d in pendientes:
        if d not in consultados and d in prev_items:
            items[d] = prev_items[d]
    items = {d: v for d, v in items.items() if d in dois}   # DOI que ya no están en el BibTeX
    datos = {
        "fecha": hoy.isoformat() if not al_dia else prev_fecha.isoformat(),
        "fuente": "Dimensions",
        "fuente_url": "https://www.dimensions.ai",
        "total_citas": sum(v["citas"] for v in items.values()),
        "consultados": sorted(d for d in consultados if d in dois),
        "items": items,
    }
    escribir(datos, args.salida)
    print(f"metricas: {ok} consultas, {fallos} fallos; {len(items)} publicaciones con citas; "
          f"{datos['total_citas']} citas en total ({datos['fecha']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
