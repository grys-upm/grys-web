#!/usr/bin/env python3
"""
Comprueba los datos ANTES de compilar (no necesita Ruby ni Jekyll).

  python3 scripts/comprobar_datos.py

Revisa: sintaxis YAML de _data/ y de los front matter; mapa de rutas
(_data/routes.yml) frente a _pages/es y _pages/en; textos de interfaz con las
mismas claves en ES y EN; redirecciones; campos básicos de las colecciones.
Sale con código 1 si hay errores. Los avisos no detienen la compilación.
"""
import glob
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("Falta PyYAML:  python3 -m pip install pyyaml")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LANGS = ("es", "en")
errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


def load_yaml(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return yaml.safe_load(fh)
    except Exception as e:  # noqa: BLE001
        err(f"{rel(path)}: YAML no válido: {e}")
        return None


def front_matter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"---\r?\n(.*?)\r?\n---\r?\n?", text, re.S)
    if not m:
        err(f"{rel(path)}: falta el bloque front matter (--- … ---)")
        return None, text
    try:
        return yaml.safe_load(m.group(1)) or {}, text[m.end():]
    except Exception as e:  # noqa: BLE001
        err(f"{rel(path)}: front matter no válido: {e}")
        return None, text


# ---------------------------------------------------------------- _data
def bad_keys(node, where):
    """YAML 1.1 convierte claves como on/off/yes/no en booleanos: Liquid no las encuentra."""
    if isinstance(node, dict):
        for k, v in node.items():
            if not isinstance(k, str):
                err(f"{where}: la clave «{k}» no es texto (¿on/off/yes/no/número?); entrecomíllala o renómbrala")
            bad_keys(v, where)
    elif isinstance(node, list):
        for v in node:
            bad_keys(v, where)


for p in sorted(glob.glob(os.path.join(ROOT, "_data", "**", "*.yml"), recursive=True)):
    bad_keys(load_yaml(p), rel(p))

routes = load_yaml(os.path.join(ROOT, "_data", "routes.yml")) or {}
menus = {m["id"] for m in routes.get("menus", [])}
pages = routes.get("pages", [])
ids = [r.get("id") for r in pages]
for dup in {i for i in ids if ids.count(i) > 1}:
    err(f"routes.yml: id repetido «{dup}»")

paths = {lang: {} for lang in LANGS}
for r in pages:
    rid = r.get("id")
    if r.get("menu") not in (None, *menus):
        err(f"routes.yml [{rid}]: menú «{r.get('menu')}» inexistente")
    if not isinstance(r.get("title"), dict) or any(not r["title"].get(lang) for lang in LANGS):
        err(f"routes.yml [{rid}]: falta title.es o title.en")
    for lang in LANGS:
        path = r.get(lang)
        if not path or not path.startswith("/") or not path.endswith("/"):
            err(f"routes.yml [{rid}]: ruta {lang} «{path}» debe empezar y acabar en /")
            continue
        if path.startswith("/en/"):
            err(f"routes.yml [{rid}]: la ruta en no debe llevar /en/ (lo añade polyglot)")
        if path in paths[lang]:
            err(f"routes.yml: ruta {lang} {path} repetida ({paths[lang][path]} y {rid})")
        paths[lang][path] = rid
        # Fichero de la página
        f = os.path.join(ROOT, "_pages", lang, f"{rid}.md")
        if not os.path.exists(f):
            err(f"falta _pages/{lang}/{rid}.md (página «{rid}» en {lang})")
            continue
        fm, _ = front_matter(f)
        if fm is None:
            continue
        for key, expected in (("lang", lang), ("page_id", rid), ("permalink", path)):
            if str(fm.get(key)) != str(expected):
                err(f"{rel(f)}: {key} = «{fm.get(key)}» y debería ser «{expected}»")

for lang in LANGS:
    for f in glob.glob(os.path.join(ROOT, "_pages", lang, "*.md")):
        rid = os.path.splitext(os.path.basename(f))[0]
        if rid not in ids:
            err(f"{rel(f)}: no está en _data/routes.yml (añádela allí o bórrala)")
for f in glob.glob(os.path.join(ROOT, "_pages", "*.md")):
    warn(f"{rel(f)}: las páginas deben ir en _pages/es o _pages/en")

details = routes.get("details", {}) or {}
for coll, cfg in details.items():
    for lang in LANGS:
        if ":slug" not in str(cfg.get(lang, "")):
            err(f"routes.yml details.{coll}: la ruta {lang} debe contener :slug")
    if cfg.get("parent") not in ids:
        err(f"routes.yml details.{coll}: parent «{cfg.get('parent')}» inexistente")

# ---------------------------------------------------------------- i18n
def keys(d, prefix=""):
    out = set()
    for k, v in (d or {}).items():
        k = str(k)
        out.add(prefix + k)
        if isinstance(v, dict):
            out |= keys(v, prefix + k + ".")
    return out


i18n = {lang: load_yaml(os.path.join(ROOT, "_data", "i18n", f"{lang}.yml")) or {} for lang in LANGS}
for a, b in (("es", "en"), ("en", "es")):
    for k in sorted(keys(i18n[a]) - keys(i18n[b])):
        err(f"_data/i18n/{b}.yml: falta la clave «{k}» (está en {a}.yml)")

# ---------------------------------------------------------------- redirecciones
es_paths = set(paths["es"])
seen = set()
for r in load_yaml(os.path.join(ROOT, "_data", "redirects.yml")) or []:
    src = str(r.get("from", ""))
    if not src.startswith("/"):
        err(f"redirects.yml: «{src}» debe empezar por /")
    if src in seen:
        err(f"redirects.yml: «{src}» repetida")
    seen.add(src)
    if r.get("to") not in ids:
        err(f"redirects.yml: «{src}» apunta a «{r.get('to')}», que no existe en routes.yml")
    if r.get("lang", "es") not in LANGS:
        err(f"redirects.yml: «{src}» con idioma desconocido «{r.get('lang')}»")
    norm = src if src.endswith("/") or "." in os.path.basename(src) else src + "/"
    if norm in es_paths or norm.startswith("/en/"):
        err(f"redirects.yml: «{src}» pisaría una página real del sitio")

# ---------------------------------------------------------------- colecciones
REQUIRED = {
    "members": ["given", "family", "status"],
    "projects": ["acronym", "type"],
    "lines": ["title_es", "title_en"],
    "domains": ["title_es", "title_en"],
    "news": ["date"],
    "events": ["date"],
    "opportunities": ["deadline"],
}
for coll, req in REQUIRED.items():
    for f in sorted(glob.glob(os.path.join(ROOT, f"_{coll}", "*.md"))):
        name = os.path.basename(f)
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*\.md", name):
            err(f"{rel(f)}: el nombre del fichero solo puede llevar minúsculas, números y guiones")
        fm, body = front_matter(f)
        if fm is None:
            continue
        for k in req:
            if fm.get(k) in (None, ""):
                err(f"{rel(f)}: falta el campo obligatorio «{k}»")
        for u in fm.get("old_urls") or []:
            if not str(u).startswith("/"):
                err(f"{rel(f)}: old_urls «{u}» debe empezar por /")
        if re.search(r"{%\s*include\s", body):
            warn(f"{rel(f)}: usa {{% include %}} en el texto; revisa que exista en _includes/")

# ---------------------------------------------------------------- Liquid
# Comprobación ligera (sin Ruby) de bloques abiertos/cerrados y filtros.
BLOCKS = {"if": "endif", "unless": "endunless", "for": "endfor", "case": "endcase",
          "capture": "endcapture", "comment": "endcomment", "raw": "endraw",
          "static_href": "endstatic_href", "tablerow": "endtablerow"}
SIMPLE = {"else", "elsif", "when", "assign", "include", "include_relative", "break", "continue",
          "bibliography", "cite", "reference", "increment", "decrement", "cycle", "echo", "liquid",
          "I18n_Headers", "highlight", "endhighlight", "post_url", "link"}
FILTERS = set("""default l10n route_url url_lang detail_url alt_url relative_url absolute_url append prepend
escape escape_once xml_escape cgi_escape uri_escape url_encode strip_html strip_newlines newline_to_br
upcase downcase capitalize strip lstrip rstrip date date_to_xmlschema date_to_string date_to_long_string
split where where_exp group_by group_by_exp find first last map size join sort sort_natural reverse uniq
compact concat push pop shift unshift sample replace replace_first remove remove_first truncate
truncatewords slice plus minus times divided_by modulo abs ceil floor round at_least at_most
jsonify markdownify smartify slugify number_of_words inspect normalize_whitespace array_to_sentence_string""".split())

LIQ_FILES = []
for pat in ("_layouts/*.html", "_includes/*.html", "_includes/*.svg", "_pages/*/*.md", "*.html", "*.xml", "*.txt",
            "_members/*.md", "_projects/*.md", "_lines/*.md", "_domains/*.md", "_news/*.md",
            "_events/*.md", "_opportunities/*.md"):
    LIQ_FILES += glob.glob(os.path.join(ROOT, pat))

for f in sorted(set(LIQ_FILES)):
    text = open(f, encoding="utf-8").read()
    text = re.sub(r"{%-?\s*comment\s*-?%}.*?{%-?\s*endcomment\s*-?%}", "", text, flags=re.S)
    text = re.sub(r"{%-?\s*raw\s*-?%}.*?{%-?\s*endraw\s*-?%}", "", text, flags=re.S)
    stack = []
    for m in re.finditer(r"{%-?\s*(\w+)(.*?)-?%}", text, re.S):
        tag, rest = m.group(1), m.group(2)
        line = text.count("\n", 0, m.start()) + 1
        if tag in BLOCKS:
            stack.append((tag, line))
        elif tag.startswith("end") and tag[3:] in BLOCKS:
            if not stack or stack[-1][0] != tag[3:]:
                err(f"{rel(f)}:{line}: {{% {tag} %}} sin su apertura correspondiente")
            else:
                stack.pop()
        elif tag not in SIMPLE:
            err(f"{rel(f)}:{line}: etiqueta Liquid desconocida «{tag}»")
        if tag == "for" and "|" in rest:
            err(f"{rel(f)}:{line}: Liquid no admite filtros dentro de {{% for %}}; usa assign antes")
        if tag in ("assign", "if", "elsif", "unless") or tag == "echo":
            for flt in re.findall(r"\|\s*(\w+)", rest):
                if flt not in FILTERS:
                    err(f"{rel(f)}:{line}: filtro desconocido «{flt}»")
    for tag, line in stack:
        err(f"{rel(f)}:{line}: {{% {tag} %}} sin cerrar")
    for m in re.finditer(r"{{-?(.*?)-?}}", text, re.S):
        line = text.count("\n", 0, m.start()) + 1
        for flt in re.findall(r"\|\s*(\w+)", m.group(1)):
            if flt not in FILTERS:
                err(f"{rel(f)}:{line}: filtro desconocido «{flt}»")

# ---------------------------------------------------------------- informe
for w in warnings:
    print(f"AVISO  {w}")
for e in errors:
    print(f"ERROR  {e}")
print(f"\ncomprobar_datos: {len(errors)} errores, {len(warnings)} avisos; "
      f"{len(pages)} páginas × {len(LANGS)} idiomas.")
sys.exit(1 if errors else 0)
