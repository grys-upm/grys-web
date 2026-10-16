#!/usr/bin/env python3
"""
Verifica el sitio YA COMPILADO (carpeta _site) contra los criterios de aceptación.

  python3 scripts/verificar_sitio.py _site [--baseurl /web-grys]

Comprueba:
  · existen todas las páginas de _data/routes.yml en ES y EN;
  · existen las redirecciones de _data/redirects.yml;
  · cada página HTML tiene lang correcto, un solo <h1>, enlace «Saltar al
    contenido», tema oscuro por defecto y el script del tema antes del CSS;
  · no quedan restos de Liquid ({{ … }}, {% … %}) ni contenido de demostración;
  · los enlaces internos (href/src) apuntan a ficheros que existen.
Sale con código 1 si hay errores. Solo usa la biblioteca estándar + PyYAML.
"""
import argparse
import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEMO = re.compile(r"al-folio|Einstein|Godfather|distill|giscus|disqus|plotly|echarts|tikzjax", re.I)
errors, warnings = [], []


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1 = 0
        self.lang = None
        self.theme = None
        self.links = []
        self.skip = False
        self.order = []          # orden de <script> en línea y <link stylesheet> en <head>
        self.in_head = False
        self.refresh = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang, self.theme = a.get("lang"), a.get("data-theme")
        elif tag == "head":
            self.in_head = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "meta" and (a.get("http-equiv") or "").lower() == "refresh":
            self.refresh = True
        elif tag == "a" and "skip" in (a.get("class") or "").split():
            self.skip = True
        if self.in_head and tag == "script" and "src" not in a:
            self.order.append("theme-script")
        if self.in_head and tag == "link" and a.get("rel") == "stylesheet":
            self.order.append("css")
        for attr in ("href", "src"):
            v = a.get(attr)
            if not v:
                continue
            if tag == "link" and a.get("rel") not in ("stylesheet", "icon", "apple-touch-icon", "preload"):
                continue  # canonical/alternate son absolutas
            self.links.append(v)

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False


def target_file(site, base, url):
    """Convierte una URL interna en la ruta del fichero dentro de _site."""
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or not parts.path.startswith("/"):
        return None
    path = unquote(parts.path)
    if base and path.startswith(base + "/"):
        path = path[len(base):]
    elif base and path == base:
        path = "/"
    f = os.path.join(site, path.lstrip("/"))
    if path.endswith("/"):
        f = os.path.join(f, "index.html")
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site", nargs="?", default="_site")
    ap.add_argument("--baseurl", default="")
    ap.add_argument("--estricto", action="store_true", help="las imágenes que faltan son error")
    args = ap.parse_args()
    site, base = os.path.abspath(args.site), args.baseurl.rstrip("/")
    if not os.path.isdir(site):
        sys.exit(f"No existe {site}: compila primero (bundle exec jekyll build)")

    routes = yaml.safe_load(open(os.path.join(ROOT, "_data", "routes.yml"), encoding="utf-8"))
    redirects = yaml.safe_load(open(os.path.join(ROOT, "_data", "redirects.yml"), encoding="utf-8")) or []

    # 1. Páginas de la tabla en ES y EN
    for r in routes["pages"]:
        for lang, prefix in (("es", ""), ("en", "/en")):
            f = os.path.join(site, (prefix + r[lang]).lstrip("/"), "index.html")
            if not os.path.exists(f):
                errors.append(f"falta la página {r['id']} [{lang}]: {prefix}{r[lang]}")

    # 2. Redirecciones
    for r in redirects:
        src = r["from"] if r["from"].endswith("/") else r["from"] + "/"
        f = os.path.join(site, src.lstrip("/"), "index.html")
        if not os.path.exists(f):
            errors.append(f"falta la redirección {r['from']}")

    # 3. Cada HTML
    n = 0
    missing_fonts = set()
    missing_media = set()
    for dirpath, _, files in os.walk(site):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            f = os.path.join(dirpath, fn)
            relf = os.path.relpath(f, site)
            text = open(f, encoding="utf-8").read()
            p = Page()
            p.feed(text)
            if p.refresh:            # páginas de redirección
                continue
            n += 1
            expected = "en" if relf.startswith("en" + os.sep) else "es"
            if p.lang != expected and fn != "404.html":
                errors.append(f"{relf}: lang=«{p.lang}», debería ser «{expected}»")
            if p.h1 != 1:
                errors.append(f"{relf}: tiene {p.h1} <h1> (debe haber exactamente uno)")
            if not p.skip:
                errors.append(f"{relf}: falta el enlace «Saltar al contenido»")
            if p.theme != "dark":
                errors.append(f"{relf}: el tema por defecto no es oscuro (data-theme=«{p.theme}»)")
            if "theme-script" not in p.order or "css" not in p.order or p.order.index("theme-script") > p.order.index("css"):
                errors.append(f"{relf}: el script del tema debe ir en el <head> antes de la hoja de estilos")
            body = re.sub(r"<pre.*?</pre>", "", text, flags=re.S)
            if re.search(r"\{\{|\{%", body):
                errors.append(f"{relf}: quedan etiquetas Liquid sin procesar")
            if DEMO.search(re.sub(r"<(script|style)\b.*?</\1>", "", body, flags=re.S)):
                errors.append(f"{relf}: posible contenido de demostración ({DEMO.search(body).group(0)})")
            if 'class="todo"' in text:
                warnings.append(f"{relf}: tiene marcadores «por completar»")
            for url in p.links:
                if url.startswith(("mailto:", "tel:", "#", "data:")):
                    continue
                tf = target_file(site, base, url)
                if tf and not os.path.exists(tf):
                    if "/assets/fonts/" in url:
                        missing_fonts.add(url)  # no bloquea: hay fuentes de respaldo
                    elif ("/assets/img/" in url or "/assets/convocatorias/" in url) and not args.estricto:
                        missing_media.add(url)  # pendiente de scripts/migrar_imagenes.py
                    else:
                        errors.append(f"{relf}: enlace roto {url}")

    for u in sorted(missing_fonts):
        print(f"AVISO  falta la fuente {u} (se usa la de respaldo) → python scripts/descargar_fuentes.py")
    if missing_media:
        print(f"AVISO  faltan {len(missing_media)} imágenes/PDF → python scripts/migrar_imagenes.py "
              "(con --estricto cuentan como error)")
    # 4. Fotos del equipo: si existen en _site, la página Equipo debe mostrarlas
    fotos = os.path.join(site, "assets", "img", "equipo")
    if os.path.isdir(fotos) and any(f.endswith(".webp") for f in os.listdir(fotos)):
        for team in (os.path.join(site, "grupo", "equipo", "index.html"),
                     os.path.join(site, "en", "group", "team", "index.html")):
            if os.path.exists(team) and "/assets/img/equipo/" not in open(team, encoding="utf-8").read():
                errors.append(f"{os.path.relpath(team, site)}: hay fotos en assets/img/equipo/ "
                              "pero la página no muestra ninguna (¿falla avatar.html?)")
    todo = sum(1 for w in warnings if "por completar" in w)
    for e in errors:
        print(f"ERROR  {e}")
    print(f"\nverificar_sitio: {n} páginas HTML revisadas; {len(errors)} errores; "
          f"{todo} páginas con marcadores «por completar».")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
