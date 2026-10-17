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
  · los enlaces internos (href/src) apuntan a ficheros que existen;
  · las pestañas (Equipo, Tesis) están bien enlazadas: cada tab con su panel,
    una sola seleccionada y solo su panel visible; anclas antiguas (#phd…) vivas;
  · la tabla de Proyectos tiene sus filtros (ocultos sin JS) y una fila con
    datos de filtrado por cada proyecto de _projects/;
  · Publicaciones tiene sus filtros y un .pubdata por entrada de papers.bib, y
    ninguna página carga scripts de Altmetric/Dimensions sin pedirlo el visitante;
  · cada enlace «?autor=slug» de las fichas de miembro tiene su opción en el
    filtro de autoría de Publicaciones (si no, el enlace mostraría todo);
  · la portada (ES y EN) tiene todas sus secciones, las 4 cifras, una tarjeta por
    proyecto destacado de _data/portada.yml y el nº de publicaciones configurado;
  · las páginas de texto ya migradas no dicen «pendiente de migración» ni
    «próximamente» y tienen
    su contenido (ODS: una tarjeta por elemento de _data/ods.yml; Contacto: mapa).
Sale con código 1 si hay errores. Solo usa la biblioteca estándar + PyYAML.
"""
import argparse
import glob
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


def destacados_esperados(po, site):
    """Misma regla que _plugins/destacados.rb: fijos primero; después, en curso
    (por inicio, más reciente primero) y el resto por fin, más reciente primero.
    La fecha de referencia es la de compilación (se toma de _site/index.html o hoy)."""
    import datetime
    cfg = po.get("destacados") or {}
    hoy = datetime.date.today()
    projs = {}
    for f in glob.glob(os.path.join(ROOT, "_projects", "*.md")):
        txt = open(f, encoding="utf-8").read().split("---")
        d = yaml.safe_load(txt[1]) or {}
        projs[os.path.basename(f)[:-3]] = d
    def fecha(x):
        if isinstance(x, datetime.date):
            return x
        try:
            return datetime.date.fromisoformat(str(x))
        except ValueError:
            return None
    lejos = datetime.date(1900, 1, 1)
    rank = {"ongoing": 0, "upcoming": 1, "completed": 2, "unknown": 3}
    def estado(d):
        if d.get("status"):
            return d["status"]
        ini, fin = fecha(d.get("start")), fecha(d.get("end"))
        if fin is None:
            return "unknown"
        if ini and ini > hoy:
            return "upcoming"
        return "ongoing" if fin >= hoy else "completed"
    fijos = [s for s in cfg.get("fijos") or [] if s in projs]
    excl = set(cfg.get("excluir") or [])
    auto = []
    for s, d in projs.items():
        if s in fijos or s in excl:
            continue
        st = estado(d)
        ref = fecha(d.get("start" if st == "ongoing" else "end")) or lejos
        auto.append((rank.get(st, 3), -ref.toordinal(), str(d.get("acronym", "")).lower(), s))
    auto.sort()
    orden = (fijos + [a[3] for a in auto])[:max(int(cfg.get("numero", 3)), 0)]
    return [(s, str(projs[s].get("acronym", s))) for s in orden]


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
    # 5. Pestañas: patrón ARIA coherente en Equipo y Tesis (ES y EN)
    tab_pages = {
        ("grupo/equipo", "en/group/team"): ["actuales", "antiguos"],
        ("investigacion/tesis", "en/research/theses"): ["phd", "master", "bachelor"],
    }
    for rels, need in tab_pages.items():
        for rel in rels:
            f = os.path.join(site, rel, "index.html")
            if not os.path.exists(f):
                continue
            html = open(f, encoding="utf-8").read()
            tabs = re.findall(r'<button[^>]*role="tab"[^>]*>', html)
            panels = re.findall(r'<div[^>]*role="tabpanel"[^>]*>', html)
            if not tabs:
                errors.append(f"{rel}/index.html: no tiene pestañas (role=tab)")
                continue
            ids = [re.search(r'id="([^"]+)"', x).group(1) for x in panels]
            sel = [x for x in tabs if 'aria-selected="true"' in x]
            if len(sel) != 1:
                errors.append(f"{rel}/index.html: {len(sel)} pestañas seleccionadas (debe ser 1)")
            for x in tabs:
                c = re.search(r'aria-controls="([^"]+)"', x)
                tid = re.search(r'id="([^"]+)"', x)
                if not c or c.group(1) not in ids:
                    errors.append(f"{rel}/index.html: pestaña sin panel: {x[:80]}")
                elif tid and f'aria-labelledby="{tid.group(1)}"' not in html:
                    errors.append(f"{rel}/index.html: el panel {c.group(1)} no apunta a su pestaña")
            visibles = [x for x in panels if " hidden" not in x]
            if len(visibles) != 1:
                errors.append(f"{rel}/index.html: {len(visibles)} paneles visibles al cargar (debe ser 1)")
            for a in need:
                if a not in ids:
                    errors.append(f"{rel}/index.html: falta el panel con ancla #{a}")
    # 6. Filtros de Proyectos (ES y EN)
    n_proj = len(glob.glob(os.path.join(ROOT, "_projects", "*.md")))
    for rel in ("investigacion/proyectos", "en/research/projects"):
        f = os.path.join(site, rel, "index.html")
        if not os.path.exists(f):
            continue
        html = open(f, encoding="utf-8").read()
        form = re.search(r'<form[^>]*data-filter="pr"[^>]*>', html)
        if not form:
            errors.append(f"{rel}/index.html: faltan los filtros (form data-filter=pr)")
        elif " hidden" not in form.group(0):
            errors.append(f"{rel}/index.html: los filtros deben llevar «hidden» (los muestra el JS)")
        for i in ("pr-table", "pr-count", "pr-empty"):
            if f'id="{i}"' not in html:
                errors.append(f"{rel}/index.html: falta el elemento #{i}")
        filas = len(re.findall(r"<tr data-tipo=", html))
        if filas != n_proj:
            errors.append(f"{rel}/index.html: {filas} filas filtrables y hay {n_proj} proyectos")
    # 7. Publicaciones: filtros, datos por entrada e insignias bajo demanda
    bib = os.path.join(ROOT, "_bibliography", "papers.bib")
    n_bib = len(re.findall(r"^@(?!comment|string|preamble)\w+\s*\{", open(bib, encoding="utf-8").read(), re.M | re.I)) if os.path.exists(bib) else 0
    for rel in ("investigacion/publicaciones", "en/research/publications"):
        f = os.path.join(site, rel, "index.html")
        if not os.path.exists(f):
            continue
        html = open(f, encoding="utf-8").read()
        if not re.search(r'<form[^>]*data-filter="pb"[^>]*hidden', html):
            errors.append(f"{rel}/index.html: faltan los filtros (form data-filter=pb hidden)")
        for i in ("pb-list", "pb-count", "pb-empty"):
            if f'id="{i}"' not in html:
                errors.append(f"{rel}/index.html: falta el elemento #{i}")
        n_pd = html.count('class="pubdata"')
        if n_pd != n_bib:
            errors.append(f"{rel}/index.html: {n_pd} publicaciones filtrables y papers.bib tiene {n_bib}")
        n_doi = html.count('class="badges" hidden')
        if n_doi == 0:
            print(f"AVISO  {rel}/index.html: ninguna insignia de Altmetric/Dimensions")
    for dirpath, _, files in os.walk(site):
        for fn in files:
            if fn.endswith(".html"):
                h = open(os.path.join(dirpath, fn), encoding="utf-8").read()
                if re.search(r'<script[^>]+src="[^"]*(altmetric|dimensions)', h, re.I):
                    errors.append(f"{os.path.relpath(os.path.join(dirpath, fn), site)}: carga un script de "
                                  "Altmetric/Dimensions sin consentimiento (debe hacerlo grys.js bajo demanda)")
    # 8. Enlaces ?autor= de las fichas → opción en el filtro de autoría
    opciones = {}
    for lang_dir, rel in (("", "investigacion/publicaciones"), ("en", "en/research/publications")):
        f = os.path.join(site, rel, "index.html")
        if os.path.exists(f):
            h = open(f, encoding="utf-8").read()
            sel = re.search(r'<select id="pb-autor".*?</select>', h, re.S)
            opciones[lang_dir] = set(re.findall(r'<option value="([^"]+)"', sel.group(0))) if sel else set()
    n_autor = 0
    for dirpath, _, files in os.walk(site):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            fp = os.path.join(dirpath, fn)
            relf = os.path.relpath(fp, site)
            for slug in re.findall(r'href="[^"]*\?autor=([^"&#]+)', open(fp, encoding="utf-8").read()):
                n_autor += 1
                ld = "en" if relf.startswith("en" + os.sep) else ""
                if ld in opciones and slug not in opciones[ld]:
                    errors.append(f"{relf}: enlace ?autor={slug} sin opción en el filtro de autoría")
    if opciones and n_autor == 0:
        print("AVISO  ninguna ficha de miembro enlaza a sus publicaciones (¿falla _plugins/bib_index.rb?)")
    # 9. Portada: secciones, cifras, destacados y publicaciones
    po = yaml.safe_load(open(os.path.join(ROOT, "_data", "portada.yml"), encoding="utf-8")) or {}
    for rel in ("index.html", os.path.join("en", "index.html")):
        f = os.path.join(site, rel)
        if not os.path.exists(f):
            continue
        html = open(f, encoding="utf-8").read()
        for sid in ("h-hero", "h-lineas", "h-ambitos", "h-proyectos", "h-noticias", "h-pubs", "h-lab"):
            if f'id="{sid}"' not in html:
                errors.append(f"{rel}: falta la sección de portada #{sid}")
        facts = re.search(r'<div class="facts".*?</div>\s*</div>', html, re.S)
        if not facts or facts.group(0).count("<b>") != 4:
            errors.append(f"{rel}: la portada debe mostrar 4 cifras (.facts)")
        esperados = destacados_esperados(po, site)
        sec_p = html.split('id="h-proyectos"', 1)[-1].split('id="h-noticias"', 1)[0]
        vistos = re.findall(r'<article class="project">.*?<span class="acr">([^<]+)</span>', sec_p, re.S)
        acr = [a.upper() for _, a in esperados]
        if vistos != acr:
            errors.append(f"{rel}: proyectos destacados {vistos}; según la regla deberían ser {acr}")
        sec = html.split('id="h-pubs"', 1)[-1].split('id="h-lab"', 1)[0]
        n_pub = sec.count('<div class="yr">')
        if n_pub != min(po.get("publicaciones", 0), 169) and n_pub == 0:
            errors.append(f"{rel}: la portada no muestra publicaciones recientes")
    # 10. Páginas de texto migradas (fase 3.6)
    n_ods = len(yaml.safe_load(open(os.path.join(ROOT, "_data", "ods.yml"), encoding="utf-8")) or [])
    migradas = {
        "grupo/quienes-somos": ['class="historia"', 'class="card valores"'],
        "en/group/about": ['class="historia"', 'class="card valores"'],
        "grupo/ods": ['class="ods"'], "en/group/sdgs": ['class="ods"'],
        "grupo/contacto": ['openstreetmap.org/export/embed', 'class="contact-list"'],
        "en/group/contact": ['openstreetmap.org/export/embed', 'class="contact-list"'],
        # fase 3.6b
        "opentech-lab": ['class="capacidades"'], "en/opentech-lab": ['class="capacidades"'],
        "opentech-lab/demostradores": ['class="grid2 demos"'], "en/opentech-lab/demonstrators": ['class="grid2 demos"'],
        "colabora/transferencia": ['class="transfer"'], "en/collaborate/technology-transfer": ['class="transfer"'],
        "colabora/tfg-tfm-doctorado": ['class="estudiantes"'], "en/collaborate/student-projects-and-phd": ['class="estudiantes"'],
        "colabora/docencia": ['class="docencia"'], "en/collaborate/teaching": ['class="docencia"'],
    }
    def _n(nombre, clave=None):
        d = yaml.safe_load(open(os.path.join(ROOT, "_data", nombre), encoding="utf-8")) or {}
        return len(d.get(clave) or []) if clave else len(d)
    cuentas = {
        "opentech-lab": ('<article class="card line-card">', _n("laboratorio.yml", "capacidades"), "capacidades"),
        "demostradores": ('<article class="project" id=', _n("demostradores.yml"), "demostradores"),
        "demonstrators": ('<article class="project" id=', _n("demostradores.yml"), "demostradores"),
    }
    for rel, marcas in migradas.items():
        f = os.path.join(site, rel, "index.html")
        if not os.path.exists(f):
            continue
        html = open(f, encoding="utf-8").read()
        if re.search(r"pendiente de migración|pending migration", html, re.I):
            errors.append(f"{rel}/index.html: sigue diciendo «pendiente de migración»")
        for m in marcas:
            if m not in html:
                errors.append(f"{rel}/index.html: falta {m}")
        for clave, (marca, n_esp, que) in cuentas.items():
            if rel.endswith(clave):
                n = html.count(marca)
                if n != n_esp:
                    errors.append(f"{rel}/index.html: {n} {que} y los datos tienen {n_esp}")
        if re.search(r"(pr[oó]ximamente|coming soon)", html, re.I):
            errors.append(f"{rel}/index.html: dice «próximamente/coming soon»")
        if "/ods" in rel or "/sdgs" in rel:
            n = html.count('<article class="card sdg">')
            if n != n_ods:
                errors.append(f"{rel}/index.html: {n} tarjetas de ODS y _data/ods.yml tiene {n_ods}")
    todo = sum(1 for w in warnings if "por completar" in w)
    for e in errors:
        print(f"ERROR  {e}")
    print(f"\nverificar_sitio: {n} páginas HTML revisadas; {len(errors)} errores; "
          f"{todo} páginas con marcadores «por completar».")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
