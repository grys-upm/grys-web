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
sys.path.insert(0, os.path.dirname(__file__))
from esquemas import normalize, validate  # noqa: E402

SCHEMAS = os.path.join(ROOT, "schemas")


def schema(name):
    import json
    with open(os.path.join(SCHEMAS, f"{name}.schema.json"), encoding="utf-8") as fh:
        return json.load(fh)


COLLECTIONS = ["members", "projects", "lines", "domains", "news", "events", "opportunities"]
RESERVED = {"id", "url", "path", "relative_path", "collection", "content", "output", "excerpt",
            "next", "previous"}
refs = []
items = {c: {} for c in COLLECTIONS}
includes = {os.path.relpath(p, os.path.join(ROOT, "_includes")).replace(os.sep, "/")
            for p in glob.glob(os.path.join(ROOT, "_includes", "**", "*"), recursive=True)}
for coll in COLLECTIONS:
    sch = schema(coll)
    for f in sorted(glob.glob(os.path.join(ROOT, f"_{coll}", "*.md"))):
        name = os.path.basename(f)
        pat = r"\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\.md" if coll in ("news",) else r"[a-z0-9][a-z0-9-]*\.md"
        if not re.fullmatch(pat, name):
            err(f"{rel(f)}: nombre de fichero no válido (minúsculas, números y guiones"
                f"{'; las noticias empiezan por AAAA-MM-DD-' if coll == 'news' else ''})")
        fm, body = front_matter(f)
        if fm is None:
            continue
        items[coll][name[:-3]] = fm
        # Campos que Jekyll reserva en los elementos de una colección: en las plantillas
        # devuelven el dato interno de Jekyll y no el escrito aquí (fallo silencioso)
        for rk in sorted(RESERVED & set(map(str, fm))):
            err(f"{rel(f)}: el campo «{rk}» está reservado por Jekyll; usa otro nombre "
                f"({'key' if rk == 'id' else 'website' if rk == 'url' else 'otro'})")
        # Enlaces internos escritos a mano: fallan en una de las dos lenguas
        for lk in re.findall(r"\]\((/(?!assets/)[^)\s]*)\)|href=\"(/(?!assets/)[^\"]*)\"", body):
            target = lk[0] or lk[1]
            err(f"{rel(f)}: enlace interno «{target}»; usa {{{{ 'colección/slug' | ref }}}} "
                "(p. ej. [AFarCloud]({{ 'projects/afarcloud' | ref }}))")
        for rf in re.findall(r"\{\{\s*'([^']+)'\s*\|\s*ref\s*\}\}", body):
            refs.append((rel(f), rf))
        for e in validate(normalize(fm), sch):
            err(f"{rel(f)}: {e}")
        for k, v in fm.items():
            if str(k).startswith(("title", "subtitle", "given", "family", "acronym")) and isinstance(v, str) \
                    and (re.search(r"[\n<>]", v) or len(v) > 250):
                err(f"{rel(f)}: «{k}» debe ser una sola línea de texto, sin HTML ni más de 250 caracteres")
        if coll == "news" and fm.get("date") and not name.startswith(str(normalize(fm["date"]))[:10]):
            err(f"{rel(f)}: la fecha del nombre del fichero y el campo date no coinciden")
        for inc in re.findall(r"{%-?\s*include\s+([\w./-]+)", body):
            if inc not in includes:
                err(f"{rel(f)}: incluye «{inc}», que no existe en _includes/")
        for src in re.findall(r'(?:src|image|photo|pdf)="?(/assets/[^"\s,]+)', body) + \
                [fm.get(k) for k in ("image", "photo", "pdf") if fm.get(k)]:
            if not os.path.exists(os.path.join(ROOT, src.lstrip("/"))):
                warn(f"{rel(f)}: falta el fichero {src} (¿pendiente de scripts/migrar_imagenes.py?)")
        for src in re.findall(r'fotos="([^"]+)"', body):
            for s1 in src.split(","):
                if not os.path.exists(os.path.join(ROOT, s1.strip().lstrip("/"))):
                    warn(f"{rel(f)}: falta el fichero {s1.strip()} (¿pendiente de scripts/migrar_imagenes.py?)")

# Claves repetidas en los YAML de _data/ (PyYAML y Jekyll se quedan con la última
# sin avisar: así se «pisó» t.home al añadir el bloque de la portada)
class _DupLoader(yaml.SafeLoader):
    pass


def _dup_mapping(loader, node, deep=False):
    seen = {}
    for k_node, _ in node.value:
        k = loader.construct_object(k_node, deep=deep)
        if k in seen:
            raise yaml.constructor.ConstructorError(
                None, None, f"clave repetida «{k}» (líneas {seen[k] + 1} y {k_node.start_mark.line + 1})",
                k_node.start_mark)
        seen[k] = k_node.start_mark.line
    return loader.construct_mapping(node, deep=deep)


_DupLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _dup_mapping)
for f in sorted(glob.glob(os.path.join(ROOT, "_data", "**", "*.yml"), recursive=True)):
    try:
        yaml.load(open(f, encoding="utf-8"), Loader=_DupLoader)
    except yaml.YAMLError as e:
        err(f"{rel(f)}: {getattr(e, 'problem', None) or e}")

# Referencias cruzadas entre colecciones
repos_data = load_yaml(os.path.join(ROOT, "_data", "repos.yml")) or []
repo_names = {r.get("name") for r in repos_data}
for e in validate(normalize(repos_data), schema("repos")):
    err(f"_data/repos.yml: {e}")
for dname in ("positions", "roles", "metrics", "axes", "portada"):
    data = load_yaml(os.path.join(ROOT, "_data", f"{dname}.yml"))
    for e in validate(normalize(data), schema(dname)):
        err(f"_data/{dname}.yml: {e}")
portada = load_yaml(os.path.join(ROOT, "_data", "portada.yml")) or {}
for s in portada.get("destacados") or []:
    if s not in items["projects"]:
        err(f"_data/portada.yml: proyecto destacado «{s}» no existe en _projects/")
for slug, p in items["projects"].items():
    for m in p.get("pi") or []:
        if m not in items["members"]:
            err(f"_projects/{slug}.md: pi «{m}» no existe en _members/")
    for r in p.get("repos") or []:
        if r not in repo_names:
            err(f"_projects/{slug}.md: repo «{r}» no está en _data/repos.yml")
for slug, o in items["opportunities"].items():
    if o.get("project") and o["project"] not in items["projects"]:
        err(f"_opportunities/{slug}.md: project «{o['project']}» no existe en _projects/")
for slug, ev in items["events"].items():
    if ev.get("news") and ev["news"] not in items["news"]:
        err(f"_events/{slug}.md: news «{ev['news']}» no existe en _news/")
    for p in ev.get("projects") or []:
        if p not in items["projects"]:
            err(f"_events/{slug}.md: proyecto «{p}» no existe en _projects/")
# .bib: el texto fuera de las entradas no puede llevar «@» (BibTeX-Ruby lo toma como una entrada)
for bib in sorted(glob.glob(os.path.join(ROOT, "_bibliography", "*.bib"))):
    btext = open(bib, encoding="utf-8").read()
    depth, start = 0, 0
    outside = []
    for i, ch in enumerate(btext):
        if ch == "@" and depth == 0:
            m_e = re.match(r"@\w+\s*\{", btext[i:])
            if not m_e:
                outside.append(i)
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth = max(0, depth - 1)
    first = re.search(r"^@\w+\s*\{", btext, re.M)
    head = btext[:first.start()] if first else btext
    for m_at in re.finditer(r"@", head):
        outside.append(m_at.start())
    for pos in sorted(set(outside)):
        line = btext.count("\n", 0, pos) + 1
        err(f"{rel(bib)}:{line}: «@» fuera de una entrada (BibTeX-Ruby avisaría «Lexer: unexpected token»)")

# Destinos del filtro ref
for where_, rf in refs:
    coll_, _, slug_ = rf.partition("/")
    if coll_ not in ("members", "projects", "lines", "news") or slug_ not in items.get(coll_, {}) and \
            not any(k.endswith("-" + slug_) for k in items.get(coll_, {})):
        err(f"{where_}: ref «{rf}» no existe (formato colección/slug, p. ej. projects/afarcloud)")

# Etiquetas propias del BibTeX (_bibliography/etiquetas.yml)
import aplicar_etiquetas  # noqa: E402
pend, unknown_keys = aplicar_etiquetas.apply(check_only=True)
if pend:
    err(f"_bibliography: {pend} campos de etiquetas.yml sin aplicar → python3 scripts/aplicar_etiquetas.py")
for k in unknown_keys:
    warn(f"_bibliography/etiquetas.yml: la clave «{k}» no está en ningún .bib")
for k, v in (aplicar_etiquetas.load_tags() or {}).items():
    for p in str(v.get("project") or "").replace(" ", "").split(","):
        if p and p not in items["projects"]:
            err(f"_bibliography/etiquetas.yml [{k}]: project «{p}» no existe en _projects/")
    for ln_id in str(v.get("lines") or "").replace(" ", "").split(","):
        if ln_id and ln_id not in items["lines"]:
            err(f"_bibliography/etiquetas.yml [{k}]: line «{ln_id}» no existe en _lines/")
    for f_ in ("portal_upm", "archivo_upm"):
        if v.get(f_) and not str(v[f_]).isdigit():
            err(f"_bibliography/etiquetas.yml [{k}]: {f_} debe ser un número")

seen_ids = {}
for slug, ln in items["lines"].items():
    if ln.get("key") != slug:
        err(f"_lines/{slug}.md: key «{ln.get('key')}» debe coincidir con el nombre del fichero")
for slug, dm in items["domains"].items():
    if dm.get("key") != slug:
        err(f"_domains/{slug}.md: key «{dm.get('key')}» debe coincidir con el nombre del fichero")
for coll in ("members", "projects", "news"):
    for slug, it in items[coll].items():
        for u in it.get("old_urls") or []:
            if u in seen_ids:
                err(f"_{coll}/{slug}.md: old_urls «{u}» repetida (también en {seen_ids[u]})")
            seen_ids[u] = f"_{coll}/{slug}.md"

# ---------------------------------------------------------------- Liquid
# Comprobación ligera (sin Ruby) de bloques abiertos/cerrados y filtros.
BLOCKS = {"if": "endif", "unless": "endunless", "for": "endfor", "case": "endcase",
          "capture": "endcapture", "comment": "endcomment", "raw": "endraw",
          "static_href": "endstatic_href", "tablerow": "endtablerow"}
SIMPLE = {"else", "elsif", "when", "assign", "include", "include_relative", "break", "continue",
          "bibliography", "cite", "reference", "increment", "decrement", "cycle", "echo", "liquid",
          "I18n_Headers", "highlight", "endhighlight", "post_url", "link"}
# Lista EXACTA de filtros disponibles: Liquid 4.0.4 (la versión que usa Jekyll 4.4),
# Jekyll 4.4 y los propios de _plugins/grys.rb. OJO: filtros de Liquid 5 como
# remove_last o replace_last NO existen aquí.
LIQUID4_FILTERS = set("""size downcase upcase capitalize escape h escape_once url_encode url_decode slice truncate truncatewords split strip lstrip rstrip strip_html strip_newlines join sort sort_natural where uniq reverse map compact replace replace_first remove remove_first append concat prepend newline_to_br date first last abs plus minus times divided_by modulo round ceil floor at_least at_most default""".split())
JEKYLL_FILTERS = set("""markdownify smartify sassify scssify slugify xml_escape cgi_escape uri_escape normalize_whitespace number_of_words array_to_sentence_string jsonify where where_exp find find_exp to_integer sort pop push shift unshift sample inspect group_by group_by_exp date_to_xmlschema date_to_rfc822 date_to_string date_to_long_string relative_url absolute_url strip_index""".split())
OWN_FILTERS = set("""route_url url_lang detail_url alt_url l10n tr bib_text url_label member ref asset_exists slug_of""".split())
FILTERS = LIQUID4_FILTERS | JEKYLL_FILTERS | OWN_FILTERS

LIQ_FILES = []
for pat in ("_layouts/*.html", "_includes/*.html", "_includes/*/*.html", "_includes/*.svg", "_pages/*/*.md",
            "*.html", "*.xml", "*.txt",
            "_members/*.md", "_projects/*.md", "_lines/*.md", "_domains/*.md", "_news/*.md",
            "_events/*.md", "_opportunities/*.md"):
    LIQ_FILES += glob.glob(os.path.join(ROOT, pat))

for f in sorted(set(LIQ_FILES)):
    text = open(f, encoding="utf-8").read()
    # Liquid 4 SÍ analiza las etiquetas dentro de {% comment %}: prohibidas ahí
    for c in re.finditer(r"{%-?\s*comment\s*-?%}(.*?){%-?\s*endcomment\s*-?%}", text, re.S):
        if re.search(r"{%|{{", c.group(1)):
            line = text.count("\n", 0, c.start()) + 1
            err(f"{rel(f)}:{line}: hay una etiqueta Liquid dentro de un comentario (Liquid la procesa); escríbela sin llaves")
    # Se vacían comentarios y raw conservando los saltos de línea (números de línea correctos)
    blank = lambda m: "\n" * m.group(0).count("\n")  # noqa: E731
    text = re.sub(r"{%-?\s*comment\s*-?%}.*?{%-?\s*endcomment\s*-?%}", blank, text, flags=re.S)
    text = re.sub(r"{%-?\s*raw\s*-?%}.*?{%-?\s*endraw\s*-?%}", blank, text, flags=re.S)
    # Mismo troceado que Liquid 4: una variable {{ … }} termina en el PRIMER «}».
    # Por eso no puede haber «}» dentro de {{ … }} (p. ej. remove: "}")
    for m in re.finditer(r"\{%.*?%\}|\{\{.*?\}\}?", text, re.S):
        tok = m.group(0)
        if tok.startswith("{{") and not tok.endswith("}}"):
            line = text.count("\n", 0, m.start()) + 1
            err(f"{rel(f)}:{line}: hay un «}}» dentro de {{{{ … }}}} y Liquid cortaría ahí la variable; "
                "usa un filtro (p. ej. bib_text) o un assign dentro de {% … %}")
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
    if re.search(r"\bsf\.relative_path\b|static_files[^%]*relative_path", text) or \
            re.search(r"for\s+\w+\s+in\s+site\.static_files", text):
        err(f"{rel(f)}: no recorras site.static_files para saber si un fichero existe "
            "(en Liquid no expone relative_path y el resultado es siempre «no»); usa el filtro asset_exists")
    for m in re.finditer(r"\b(?!page\b)(\w+)\.page_id\b", text):
        line = text.count("\n", 0, m.start()) + 1
        err(f"{rel(f)}:{line}: «{m.group(1)}.page_id» no existe en los documentos de una colección "
            f"(solo en las páginas de ficha generadas); para el slug usa «{m.group(1)} | slug_of»")
    for tag, line in stack:
        err(f"{rel(f)}:{line}: {{% {tag} %}} sin cerrar")
    for m in re.finditer(r"{{-?(.*?)-?}}", text, re.S):
        line = text.count("\n", 0, m.start()) + 1
        for flt in re.findall(r"\|\s*(\w+)", m.group(1)):
            if flt not in FILTERS:
                err(f"{rel(f)}:{line}: filtro desconocido «{flt}»")

# ---------------------------------------------------------------- informe
missing_files = [w for w in warnings if "falta el fichero" in w]
warnings = [w for w in warnings if "falta el fichero" not in w]
if missing_files:
    warnings.append(f"faltan {len(missing_files)} imágenes/PDF referenciados; ejecuta "
                    "scripts/migrar_imagenes.py (detalle: --detalle)")
    if "--detalle" in sys.argv:
        warnings += missing_files
for w in warnings:
    print(f"AVISO  {w}")
for e in errors:
    print(f"ERROR  {e}")
print(f"\ncomprobar_datos: {len(errors)} errores, {len(warnings)} avisos; "
      f"{len(pages)} páginas × {len(LANGS)} idiomas.")
sys.exit(1 if errors else 0)
