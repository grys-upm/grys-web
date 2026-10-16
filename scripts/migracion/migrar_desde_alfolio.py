#!/usr/bin/env python3
"""
Migración ÚNICA del contenido de la web anterior (al-folio) al sitio nuevo.

    python3 scripts/migracion/migrar_desde_alfolio.py ORIGEN [--mockup MOCKUP.html] [--inventario INV.txt]

  ORIGEN       carpeta del repositorio antiguo (grys-upm.github.io)
  --mockup     mockup_grys_v4_completo.html (títulos ES y propuestas: ejes,
               ámbitos, género para el puesto en español, traducciones)
  --inventario 00_inventario.txt de exportar_repo.py (si las imágenes no están
               en ORIGEN, se comprueba su existencia con él)

Genera en el sitio nuevo: _members, _projects, _lines, _domains, _news,
_events, _opportunities, _data (positions, roles, axes, repos, metrics),
_bibliography (papers.bib limpio y theses.bib unificado) y
scripts/migracion/mapa_imagenes.yml (imágenes y PDF que hay que convertir y
copiar con scripts/migrar_imagenes.py).

Se conserva en el repositorio como documentación de cómo se obtuvo cada dato.
NO hay que volver a ejecutarlo: a partir de aquí se editan los datos nuevos.
Regla: no se inventa nada. Lo que no consta en el origen se deja vacío y lo
recoge scripts/informe_pendientes.py.
"""
import argparse
import os
import re
import sys
import unicodedata
from datetime import date

import yaml

sys.path.insert(0, os.path.dirname(__file__))
from bibtex_simple import drop_fields, dump, get, parse, set_field, unbrace  # noqa: E402

DEST = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TODAY = date(2026, 10, 16)
LOG = []          # incidencias para el informe de migración
IMAGES = {}       # ruta antigua -> {"to": ruta nueva, "kind": "foto|logo|retrato|pdf", "used_in": [...]}


def log(kind, where, msg):
    LOG.append((kind, where, msg))


# =====================================================================
#  Utilidades de texto
# =====================================================================
EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF\U0001F900-\U0001F9FF"
    "\U00002300-\U000023FF\U0000FE0F\U0000200D\U000020E3]"
)


def strip_emoji(s):
    # Solo se colapsan espacios DENTRO de la línea: la sangría (listas anidadas)
    # y los dos espacios finales (salto de línea de Markdown) se respetan.
    s = EMOJI.sub("", s)
    s = re.sub(r"(?<=\S)[ \t]{2,}(?=\S)", " ", s)
    s = re.sub(r"^([ \t]*[-*]|#+)[ \t]+", r"\1 ", s, flags=re.M)   # «-  texto» tras quitar un emoji
    return s.replace("( ", "(")


LAB = re.compile(r"(?<![\w/.\-])(OpenTechLab|Open TechLab|Open Tech Lab)(?![\w/.\-])")


def fix_names(s):
    return LAB.sub("OpenTech Lab", s)


def ascii_slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return re.sub(r"-{2,}", "-", s)


def split_fm(path):
    text = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        return {}, text
    raw = m.group(1)
    # front matter con claves repetidas (related_projects en un evento): YAML se queda con la última
    data = yaml.safe_load(raw) or {}
    return data, m.group(2)


def d(v):
    """Fecha de YAML → date (o None)."""
    if v in (None, ""):
        return None
    if hasattr(v, "date") and callable(v.date):
        return v.date()
    if isinstance(v, date):
        return v
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(v))
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


class Literal(str):
    pass


def _lit(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(Literal, _lit, Dumper=yaml.SafeDumper)


def write_md(path, data, body, header=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    clean = {k: v for k, v in data.items()}
    fm = yaml.safe_dump(clean, allow_unicode=True, sort_keys=False, width=1000, default_flow_style=False)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("---\n")
        if header:
            fh.write("".join(f"# {h}\n" for h in header))
        fh.write(fm)
        fh.write("---\n")
        body = body.strip("\n")
        if body:
            fh.write(body + "\n")


def write_yaml(path, data, header):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("".join(f"# {h}\n" if h else "#\n" for h in header))
        fh.write(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=1000))


# =====================================================================
#  Imágenes
# =====================================================================
class Images:
    def __init__(self, origen, inventario):
        self.origen = origen
        self.known = set()
        if inventario and os.path.exists(inventario):
            for line in open(inventario, encoding="utf-8"):
                parts = line.split(None, 2)
                if len(parts) == 3 and parts[1].isdigit():
                    self.known.add(parts[2].strip())

    def exists(self, rel):
        return os.path.exists(os.path.join(self.origen, rel)) or rel in self.known

    def map(self, old, new_dir, new_name=None, kind="foto", where=""):
        old = old.strip().lstrip("/")
        if not old:
            return None
        if old.endswith(("default.png",)):
            return None
        stem, ext = os.path.splitext(os.path.basename(old))
        is_pdf = ext.lower() == ".pdf"
        name = new_name or ascii_slug(stem)
        new = f"{new_dir}/{name}{ext.lower() if is_pdf else '.webp'}"
        if not self.exists(old):
            log("imagen", where, f"no existe en el repositorio antiguo: {old}")
            return None
        entry = IMAGES.setdefault(old, {"to": new, "kind": "pdf" if is_pdf else kind, "used_in": []})
        if where and where not in entry["used_in"]:
            entry["used_in"].append(where)
        return "/" + entry["to"]


# =====================================================================
#  Conversión de cuerpos (HTML de al-folio → Markdown + includes propios)
# =====================================================================
ATTR = re.compile(r'(\w+)\s*=\s*"([^"]*)"')


def q(s):
    """Valor seguro para un parámetro de include (entre comillas dobles)."""
    return (s or "").replace('"', "'").replace("\n", " ").strip()


def convert_body(body, imgs, img_dir, where):
    b = body.replace("\r\n", "\n")
    b = re.sub(r"<!--.*?-->", "", b, flags=re.S)

    # Galerías (swiper) → include galeria.html
    def galeria(m):
        paths = re.findall(r'path="([^"]+)"', m.group(0))
        news = [imgs.map(p, img_dir, where=where) for p in paths]
        news = [n for n in news if n]
        if news:
            log("alt", where, f"galería de {len(news)} fotos sin texto alternativo por foto (parámetro alts)")
        return f'\n{{% include galeria.html fotos="{",".join(news)}" %}}\n' if news else ""
    b = re.sub(r"<swiper-container.*?</swiper-container>", galeria, b, flags=re.S)

    # Figuras de al-folio (pueden ocupar varias líneas)
    def figura(m):
        attrs = dict(ATTR.findall(m.group(1)))
        new = imgs.map(attrs.get("path", ""), img_dir, where=where)
        if not new:
            return ""
        alt = attrs.get("alt") or attrs.get("title") or ""
        if alt.lower() == "example image":
            alt = ""
        if not alt:
            log("alt", where, f"imagen sin texto alternativo: {new}")
        return f'\n{{% include figura.html src="{new}" alt="{q(alt)}" %}}\n'
    b = re.sub(r"\{%-?\s*include\s+figure\.liquid(.*?)-?%\}", figura, b, flags=re.S)

    # <img>
    def img(m):
        attrs = dict(ATTR.findall(m.group(0)))
        new = imgs.map(attrs.get("src", ""), img_dir, where=where)
        if not new:
            return ""
        alt = attrs.get("alt", "")
        if not alt:
            log("alt", where, f"imagen sin texto alternativo: {new}")
        return f'\n{{% include figura.html src="{new}" alt="{q(alt)}" %}}\n'
    b = re.sub(r"<img\b[^>]*>", img, b)

    # Vídeos de YouTube
    def video(m):
        vid = m.group(1)
        return f'\n{{% include video.html youtube="{vid}" %}}\n'
    b = re.sub(r'<iframe[^>]*src="https?://www\.youtube(?:-nocookie)?\.com/embed/([\w-]+)[^"]*"[^>]*>\s*</iframe>', video, b, flags=re.S)
    if "<iframe" in b:
        log("contenido", where, "queda un <iframe> que no es de YouTube; revísalo")

    # Pies de foto
    def caption(m):
        inner = m.group(1).strip()
        inner = re.sub(r'<span style="font-weight:\s*bold;?">(.*?)</span>', r"<b>\1</b>", inner, flags=re.S)
        inner = re.sub(r'<span style="font-style:\s*italic;?">(.*?)</span>', r"<i>\1</i>", inner, flags=re.S)
        inner = re.sub(r"</?span[^>]*>", "", inner)
        inner = re.sub(r"\s*\n\s*", " ", inner)
        return f'\n<p class="pie">{inner}</p>\n'
    b = re.sub(r'<div class="caption[^"]*">(.*?)</div>', caption, b, flags=re.S)

    # Contenedores de maquetación de Bootstrap
    b = re.sub(r"</?div\b[^>]*>", "", b)

    # Enlaces internos a fichas → filtro ref (la URL depende del idioma)
    def internal(m):
        coll = {"projects": "projects", "research/projects": "projects", "team": "members"}[m.group(2)]
        slug = SLUG_FIX.get(m.group(3), ascii_slug(m.group(3).replace("µ", "u")))
        log("revisar", where, f"enlace interno {m.group(1)} → ficha {coll}/{slug}")
        return "](" + "{{ '" + coll + "/" + slug + "' | ref }}" + ")"
    b = re.sub(r"\]\((/(research/projects|projects|team)/([^/)#]+)/?)\)", internal, b)
    for other in re.findall(r"\]\((/(?!assets/)[^)]*)\)", b):
        log("enlace", where, f"enlace interno sin convertir: {other}")
    # Enlaces vacíos [texto](#)
    b = re.sub(r"\[([^\]]+)\]\(#\)", r"\1", b)

    # target/rel: el sitio nuevo no abre pestañas nuevas
    b = re.sub(r'\s+target="_blank"', "", b)
    b = re.sub(r'\s+rel="noopener noreferrer"', "", b)

    # Sangrías que kramdown tomaría por bloques de código
    b = "\n".join(l.strip() if re.match(r"\s+(\{%|<)", l) else l for l in b.split("\n"))

    b = fix_names(strip_emoji(b))
    b = re.sub(r"^(#+)\s*\*\*(.*?)\*\*\s*$", r"\1 \2", b, flags=re.M)   # ### **Título** → ### Título
    # Jerarquía de títulos: la página ya tiene el <h1>; el texto empieza en <h2>
    levels = [len(h) for h in re.findall(r"^(#+) ", b, flags=re.M)]
    if levels and min(levels) != 2:
        shift = min(levels) - 2
        b = re.sub(r"^(#+) ", lambda m: "#" * max(2, len(m.group(1)) - shift) + " ", b, flags=re.M)
    b = re.sub(r"^(#+)\s+", r"\1 ", b, flags=re.M)
    # Espacios finales: se quitan en títulos y antes de línea en blanco; en el
    # resto se dejan dos (salto de línea de Markdown, p. ej. en direcciones)
    b = re.sub(r"^(#+ .*?)[ \t]+$", r"\1", b, flags=re.M)
    b = re.sub(r"[ \t]+\n(?=[ \t]*\n|\Z)", "\n", b)
    b = re.sub(r"[ \t]{3,}\n", "  \n", b)
    b = re.sub(r"^[ \t]+$", "", b, flags=re.M)
    b = re.sub(r"\n{3,}", "\n\n", b)
    b = re.sub(r"^---\n\n(?:---\n\n)+", "---\n\n", b, flags=re.M)   # separadores repetidos
    b = re.sub(r"\A\s*---\s*\n", "", b)                                 # separador al principio
    b = re.sub(r"\n---\s*\Z", "\n", b.strip() + "\n")                   # separador al final
    return b.strip() + "\n"


# =====================================================================
#  Mockup: propuestas y traducciones
# =====================================================================
def read_mockup(path):
    js = open(path, encoding="utf-8").read()
    js = re.sub(r"data:image/png;base64,[A-Za-z0-9+/=]+", "", js)
    out = {}
    L = r'L\("((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\)'
    # Equipo: [nombre, apellidos, puesto, f, rol, slug]
    out["gender"] = {}
    for block in ("TEAM", "FORMER", "MEMORIAM"):
        m = re.search(r"const %s = \[(.*?)\n\];" % block, js, re.S)
        for g, f, pos, fem in re.findall(r'\["([^"]+)",\s*"([^"]+)",\s*"(\w+)",\s*([01])', m.group(1)):
            out["gender"][ascii_slug(g + " " + f)] = ("f" if fem == "1" else "m", pos)
    # Puestos
    m = re.search(r"const POS = \{(.*?)\n\};", js, re.S)
    out["positions"] = {k: (a, b, en) for k, a, b, en in re.findall(
        r'(\w+): \{ es: \["([^"]+)", "([^"]+)"\], en: "([^"]+)" \}', m.group(1))}
    # Líneas, ejes y ámbitos
    m = re.search(r"const LINES = \[(.*?)\n\];", js, re.S)
    out["lines"] = []
    for lid, ax, icon, t, d_ in re.findall(
            r'\{ id: "(\w+)", ax: (\d), icon: "(\w+)", t: (L\(.*?\)),\s*d: (L\(.*?\)) \}', m.group(1), re.S):
        te, tn = re.match(L, t).groups()
        de, dn = re.match(L, d_, re.S).groups()
        out["lines"].append({"id": lid, "axis": int(ax), "icon": icon, "t": (te, tn), "d": (de, dn)})
    m = re.search(r"const AXES = \{(.*?)\n\};", js, re.S)
    out["axes"] = {int(k): (a, b) for k, a, b in re.findall(r"(\d): " + L, m.group(1))}
    m = re.search(r"const DOMAINS = \[(.*?)\n\];", js, re.S)
    out["domains"] = []
    for did, t, s, d_ in re.findall(r'\{ id: "(\w+)", t: (L\(.*?\)), s: (L\(.*?\)), d: (L\(.*?\)) \}', m.group(1)):
        out["domains"].append({"id": did, "t": re.match(L, t).groups(), "s": re.match(L, s).groups(),
                               "d": re.match(L, d_).groups()})
    # Proyectos: [acr, L(es,en), tipo, estado, [ámbitos], programa?]
    m = re.search(r"const PROJECTS = \[(.*?)\n\];", js, re.S)
    out["projects"] = {}
    for acr, es, en, ty, st, doms in re.findall(
            r'\["([^"]+)",\s*' + L + r',\s*"(\w)",\s*"(\w+)",\s*\[([^\]]*)\]', m.group(1)):
        out["projects"][acr] = {"es": es, "en": en, "domains": re.findall(r'"(\w+)"', doms)}
    # Noticias y eventos: títulos ES
    m = re.search(r"const NEWS = \[(.*?)\n\];", js, re.S)
    out["news"] = {en: es for es, en in re.findall(r"t: " + L, m.group(1))}
    m = re.search(r"const EVENTS = \[(.*?)\n\];", js, re.S)
    out["events"] = {en: es for es, en in re.findall(r"t: " + L, m.group(1))}
    # Repositorios: [nombre, lenguaje, L(es,en)]
    m = re.search(r"const REPOS = \[(.*?)\n\];", js, re.S)
    out["repos"] = re.findall(r'\["([^"]+)",\s*"([^"]+)",\s*' + L + r"\]", m.group(1))
    return out


# =====================================================================
#  Miembros
# =====================================================================
POSITION_KEY = {
    "full professor": "full", "associate professor": "assoc", "assistant professor": "assist",
    "graduate teaching assistant": "gta", "predoctoral fellow": "predoc", "postdoctoral fellow": "postdoc",
    "first stage researcher (r1)": "r1", "research support technician": "tech",
    "student intern": "intern", "administrative staff": "admin",
}
ROLE_KEY = {"principal investigator": "pi", "external collaborator": "ext"}
STATUS_KEY = {"current members": "current", "former members": "former", "in memoriam": "memoriam"}
SLUG_FIX = {"jf": "jose-fernan-martinez-ortega"}


def member_slug(old_stem):
    return SLUG_FIX.get(old_stem, ascii_slug(old_stem))


def migrate_members(origen, mock, imgs):
    out = {}
    for fn in sorted(os.listdir(os.path.join(origen, "_people"))):
        if not fn.endswith(".md"):
            continue
        stem = fn[:-3]
        slug = member_slug(stem)
        where = f"_members/{slug}.md"
        fm, body = split_fm(os.path.join(origen, "_people", fn))
        given, family = str(fm.get("name", "")).strip(), str(fm.get("surname", "")).strip()
        pos_txt = str(fm.get("position", "")).strip().lower()
        role_txt = str(fm.get("role", "")).strip().lower()
        status = STATUS_KEY.get(str(fm.get("category", "")).strip().lower())
        g = mock["gender"].get(ascii_slug(given + " " + family))
        if not g:
            # nombres que el mockup escribe distinto (p. ej. «María Nieves» / «Raúl M.»)
            cands = [v for k, v in mock["gender"].items() if k.endswith(ascii_slug(family))]
            g = cands[0] if len(cands) == 1 else None
        if not g:
            log("dato", where, "género (para el puesto en español) no encontrado en el mockup")
        position = POSITION_KEY.get(pos_txt)
        if not position:
            log("dato", where, f"puesto desconocido: «{fm.get('position')}»")
        data = {
            "given": given,
            "family": family,
            "gender": g[0] if g else None,
            "position": position,
            "role": ROLE_KEY.get(role_txt),
            "status": status,
            "since": d(fm.get("start-date")),
            "until": d(fm.get("end-date")),
            "photo": imgs.map(str(fm.get("img") or ""), "assets/img/equipo", slug, "retrato", where),
            "orcid": re.sub(r"^https?://orcid\.org/", "", str(fm.get("orcid") or "")) or None,
            "scholar": fm.get("google-scholar") or None,
            "email": fm.get("email") or None,
            "website": fm.get("website") or None,
            "portal_upm": fm.get("imarina") or None,
            "scopus": str(fm.get("scopus_id")) if fm.get("scopus_id") else None,
            "researcherid": fm.get("researcher_id") or None,
            "researchgate": fm.get("researchgate") or None,
            "linkedin": fm.get("linkedin") or None,
            "github": fm.get("github") or None,
            "sciprofiles": str(fm.get("sciprofile")) if fm.get("sciprofile") else None,
            "lines": [],
            "lang": "en",
            "old_urls": [f"/team/{stem}/"],
        }
        if role_txt and role_txt not in ROLE_KEY and role_txt not in ("researcher", "team member",
                                                                       "undergraduate student", "administrative staff"):
            log("dato", where, f"rol desconocido: «{fm.get('role')}»")
        if g and position and g[1] != position:
            log("revisar", where, f"el mockup le asigna el puesto «{g[1]}» y la web anterior «{position}»; se usa el de la web")
        if data["photo"] is None and fm.get("img") and not str(fm.get("img")).endswith("default.png"):
            pass
        if status == "current" and data["until"]:
            log("revisar", where, "miembro actual con fecha de fin")
        if status == "former" and not data["until"]:
            log("dato", where, "antiguo miembro sin fecha de fin")
        b = convert_body(body, imgs, "assets/img/equipo", where)
        data = {k: v for k, v in data.items() if v not in (None, "")}
        data.setdefault("lines", [])
        write_md(os.path.join(DEST, "_members", f"{slug}.md"), data, b)
        out[slug] = data
    return out


def name_to_member(name, members):
    key = ascii_slug(re.sub(r"\(.*?\)", "", name))
    for slug, m in members.items():
        full = ascii_slug(m["given"] + " " + m["family"])
        if key == full or key.replace("-", "") == full.replace("-", ""):
            return slug
    return None


# =====================================================================
#  Proyectos
# =====================================================================
TABLE_MAP = {
    "organization": "funder", "program": "programme", "financing": "funding", "funded under": "funding",
    "id": "grant_ids", "grant id": "grant_ids", "grant agreement id": "grant_ids", "project code": "grant_ids",
    "project ids": "grant_ids", "national reference": "grant_ids", "aei reference:": "grant_ids",
    "start date": "start", "end date": "end", "pi at upm": "pi_upm", "pi": "coordinator_pi",
    "coordinated by": "coordinator", "doi": "doi", "links": "links", "website": "links",
}


def cell_values(html):
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    links = re.findall(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.S)
    paras = re.findall(r"<p>(.*?)</p>", html, re.S) or [html]
    texts = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", p)).strip() for p in paras]
    return [t for t in texts if t], [(u, re.sub(r"<[^>]+>", "", t).strip()) for u, t in links]


def migrate_projects(origen, mock, members, imgs):
    out = {}
    for fn in sorted(os.listdir(os.path.join(origen, "_projects"))):
        if not fn.endswith(".md"):
            continue
        stem = fn[:-3]
        slug = ascii_slug(stem.replace("µ", "u"))
        where = f"_projects/{slug}.md"
        fm, body = split_fm(os.path.join(origen, "_projects", fn))
        acr = str(fm.get("title", "")).strip()
        mk = mock["projects"].get(acr) or mock["projects"].get(acr.replace("µ", "μ"))
        info = {"funder": None, "programme": None, "funding": [], "grant_ids": [], "pi_upm": None,
                "coordinator": None, "coordinator_pi": None, "doi": None, "links": [], "start": None, "end": None}
        # Tabla «Project Information»
        tm = re.search(r"(?:##\s*Project Information\s*)?<table.*?</table>", body, re.S)
        if tm:
            for row in re.findall(r"<tr>(.*?)</tr>", tm.group(0), re.S):
                tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)
                if len(tds) != 2:
                    continue
                k = re.sub(r"<[^>]+>", "", tds[0]).strip().lower()
                texts, links = cell_values(tds[1])
                tgt = TABLE_MAP.get(k)
                if not tgt:
                    log("dato", where, f"fila de la tabla sin destino: «{k}»")
                elif tgt in ("funding", "grant_ids"):
                    info[tgt] += texts
                elif tgt == "links":
                    info["links"] += [{"url": u, "title": t} for u, t in links]
                elif tgt == "programme":
                    info["programme"] = texts[0] if texts else None
                    if links:
                        info["programme_url"] = links[0][0]
                elif tgt == "doi":
                    info["doi"] = texts[0] if texts else None
                else:
                    info[tgt] = texts[0] if texts else None
            body = body.replace(tm.group(0), "")
            if info.get("funder") == "European Comission":
                info["funder"] = "European Commission"
                log("corregido", where, "errata «European Comission» → «European Commission»")
        # AFarCloud: datos en texto plano + plantilla de ejemplo de al-folio
        if slug == "afarcloud":
            info.update({"funder": "European Commission", "programme": "Horizon 2020",
                         "pi_upm": "José Fernán Martínez Ortega", "doi": "10.3030/783221",
                         "grant_ids": ["783221", "PCI2018-092965"]})
            body = ("This project has received funding from the ECSEL Joint Undertaking (JU) under grant agreement "
                    "No 783221. The JU receives support from the European Union's Horizon 2020 research and "
                    "innovation programme.\n\nProject PCI2018-092965 funded by the Spanish Ministry of Science, "
                    "Innovation and Universities.\n")
            log("limpieza", where, "eliminada la plantilla de ejemplo de al-folio (texto «Every project has a "
                "beautiful feature showcase page», imágenes 1.jpg…11.jpg y cita einstein1950meaning)")
            log("revisar", where, "se han corregido erratas del texto original («recived», «th European»)")
        # Fechas: front matter (canónico) frente a la tabla
        start, end = d(fm.get("start-date")), d(fm.get("end-date"))
        for k, v in (("start", start), ("end", end)):
            tv = d(info.get(k))
            if tv and v and tv != v:
                log("conflicto", where, f"fecha {k}: front matter {v} y tabla {tv}; se usa la del front matter")
        pi_member = name_to_member(info["pi_upm"], members) if info.get("pi_upm") else None
        status_mock = None
        role = None
        if info.get("coordinator"):
            role = "partner"
            log("revisar", where, f"rol «partner» deducido de «Coordinated by: {info['coordinator']}»")
        elif info.get("pi_upm") and not pi_member:
            role = None
            log("revisar", where, f"el responsable en la UPM («{info['pi_upm']}») no es del grupo: ¿GRyS participa como "
                "equipo de trabajo de otro grupo? Rol sin asignar")
        data = {
            "acronym": acr.replace("µ", "μ"),
            "title_es": mk["es"] if mk else None,
            "title_en": str(fm.get("description", "")).strip() or None,
            "type": {"competitive": "competitive", "private": "private"}.get(str(fm.get("category", "")).strip().lower()),
            "status": status_mock,
            "programme": info.get("programme"),
            "programme_url": info.get("programme_url"),
            "call": None,
            "funder": info.get("funder"),
            "funding": info["funding"] or None,
            "grant_ids": info["grant_ids"] or None,
            "start": start,
            "end": end,
            "role": role,
            "pi": [pi_member] if pi_member else [],
            "pi_name": None if pi_member else info.get("pi_upm"),
            "coordinator": info.get("coordinator"),
            "coordinator_pi": info.get("coordinator_pi"),
            "partners": None,
            "budget": None,
            "domains": mk["domains"] if mk else [],
            "lines": [],
            "repos": [],
            "doi": info.get("doi"),
            "website": None,
            "links": info["links"] or None,
            "image": imgs.map(str(fm.get("img") or ""), f"assets/img/proyectos/{slug}", "logo", "logo", where),
            "lang": "en",
            "old_urls": [f"/research/projects/{stem.lower()}/"],
        }
        if mk is None:
            log("dato", where, "sin traducción al español en el mockup")
        # Web oficial: el enlace de la tabla que no sea CORDIS, archivo ni ITEA/ARTEMIS genérico
        for l in info["links"]:
            if "cordis.europa.eu" not in l["url"] and "web.archive.org" not in l["url"]:
                data["website"] = l["url"]
                break
        if slug == "nextarc":
            data["repos"] = ["NexTArc-AURA"]
            data["website"] = data["website"] or "https://nextarc.eu"
            log("revisar", where, "web oficial https://nextarc.eu tomada de la noticia del 24-04-2026")
        if slug == "uswn":
            data["old_urls"] = ["/research/projects/µswn/", "/research/projects/%C2%B5swn/"]
        b = convert_body(body, imgs, f"assets/img/proyectos/{slug}", where)
        b = re.sub(r"^##\s*Project Information\s*$", "", b, flags=re.M)
        data = {k: v for k, v in data.items() if v not in (None, "", [])
                or k in ("pi", "domains", "lines", "repos")}
        write_md(os.path.join(DEST, "_projects", f"{slug}.md"), data, b,
                 header=["Ámbitos (domains) y título en español: propuesta del mockup · REVISAR",
                         "Estado: se calcula con las fechas al compilar (campo «status» solo para forzarlo)"])
        out[slug] = data
    return out


def extra_projects(origen):
    """Proyectos que solo aparecen en las convocatorias (HumAMI, AFarEdge)."""
    # Datos confirmados por el grupo (16-10-2026) y, para AFarEdge, por CORDIS (101252360)
    CONFIRMED = {
        "afaredge": {"programme": "Horizon Europe", "funder": "European Commission",
                     "start": date(2026, 9, 1), "end": date(2029, 8, 31),
                     "pi": ["jose-fernan-martinez-ortega"], "role": "partner",
                     "coordinator": "CENTRIA-AMMATTIKORKEAKOULU OY (Finland)",
                     "doi": "10.3030/101252360",
                     "links": [{"url": "https://cordis.europa.eu/project/id/101252360", "title": "CORDIS"}]},
        "humami": {"programme": "Horizon Europe", "funder": "European Commission",
                   "start": date(2026, 9, 1), "end": date(2029, 8, 31)},
    }
    res = {}
    for slug, acr in (("afaredge", "AFarEdge"), ("humami", "HumAMI")):
        text = open(os.path.join(origen, "_opportunities", f"2026-07-22-{slug}-job.md"), encoding="utf-8").read()
        _, body = split_fm(os.path.join(origen, "_opportunities", f"2026-07-22-{slug}-job.md"))
        # Título largo: «**AFarEdge Project – Aggregated Intelligence for Farming at the Edge**» (en el TEXTO)
        m = re.search(r"\*\*%s Project – ([^*]+)\*\*" % acr, body)
        res[slug] = {"acronym": acr, "title_en": m.group(1).strip() if m else None,
                     "grant_ids": re.findall(r"\((?:Reference|Grant ID): ([^)]+)\)", body)}
        if not m:
            log("dato", f"_projects/{slug}.md", "no se encontró el título largo en la convocatoria")
    # La convocatoria daba «101252360-2»; CORDIS da 101252360
    res["afaredge"]["grant_ids"] = ["101252360" if g == "101252360-2" else g for g in res["afaredge"]["grant_ids"]]
    log("corregido", "_projects/afaredge.md", "referencia europea 101252360-2 → 101252360 (CORDIS)")
    for slug, r in res.items():
        c = CONFIRMED[slug]
        data = {"acronym": r["acronym"], "title_en": r["title_en"], "type": "competitive",
                "programme": c.get("programme"), "funder": c.get("funder"),
                "grant_ids": sorted(r["grant_ids"], key=lambda g: not g[0].isdigit()) or None,
                "start": c.get("start"), "end": c.get("end"), "role": c.get("role"),
                "pi": c.get("pi", []), "coordinator": c.get("coordinator"),
                "domains": [], "lines": [], "repos": [], "doi": c.get("doi"), "links": c.get("links"),
                "lang": "en"}
        data = {k: v for k, v in data.items() if v not in (None, "") or k in ("pi", "domains", "lines", "repos")}
        header = ["Proyecto creado a partir de su convocatoria de empleo (julio 2026) y de los datos",
                  "confirmados por el grupo el 16-10-2026" + (" y CORDIS." if slug == "afaredge" else ".")]
        if slug == "humami":
            header.append("El responsable en la UPM no es del grupo: indicar su nombre en «pi_name».")
            log("dato", f"_projects/{slug}.md", "falta el nombre del responsable en la UPM (pi_name; no es del grupo)")
        write_md(os.path.join(DEST, "_projects", f"{slug}.md"), data, "", header=header)
        log("dato", f"_projects/{slug}.md", "creado desde la convocatoria; falta la descripción")
    return res


# =====================================================================
#  Líneas, ejes, ámbitos, puestos, roles
# =====================================================================
LINE_SLUGS = {
    "cps": ("sistemas-ciberfisicos", "cyber-physical-systems"),
    "wsan": ("redes-de-sensores-y-actuadores", "wireless-sensor-and-actuator-networks"),
    "iot": ("internet-de-las-cosas", "internet-of-things"),
    "sec": ("seguridad-en-redes-y-servicios", "network-and-services-security"),
    "nca": ("agentes-cooperativos-en-red", "networked-cooperative-agents"),
    "rob": ("robotica-cooperativa-en-red", "networked-cooperative-robotics"),
    "dss": ("soporte-a-decisiones-e-ia", "decision-support-systems-and-ai"),
    "mw": ("middleware-semantico", "semantic-middleware"),
    "sw": ("ingenieria-de-software-avanzada", "advanced-software-engineering"),
    "edge": ("computacion-cloud-y-edge", "cloud-and-edge-computing"),
    "smart": ("dominios-inteligentes", "smart-domains"),
}


def migrate_lines(origen, mock):
    _, body = split_fm(os.path.join(origen, "_pages", "research-areas.md"))
    sections = re.split(r"^## ", body, flags=re.M)[1:]
    long_en = []
    for s in sections:
        head, _, text = s.partition("\n")
        text = text.split("\n---")[0].strip()
        long_en.append((strip_emoji(head).strip(), re.sub(r"\s*\n\s*", " ", text)))
    for n, ln in enumerate(mock["lines"]):
        es_slug, en_slug = LINE_SLUGS[ln["id"]]
        data = {
            "key": ln["id"], "axis": ln["axis"], "icon": ln["icon"], "order": n + 1,
            "title_es": ln["t"][0], "title_en": ln["t"][1],
            "desc_es": ln["d"][0], "desc_en": ln["d"][1],
            "slug_es": es_slug, "slug_en": en_slug,
            "lang": "en",
            "keywords": [],
        }
        body_en = long_en[n][1] if n < len(long_en) else ""
        write_md(os.path.join(DEST, "_lines", f"{ln['id']}.md"), data, body_en,
                 header=["Eje (axis): agrupación propuesta en el mockup · REVISAR",
                         "desc_es/desc_en: texto corto (tarjetas). Cuerpo: texto completo de la web anterior (inglés)."])
    write_yaml(os.path.join(DEST, "_data", "axes.yml"),
               [{"id": k, "title": {"es": v[0], "en": v[1]}} for k, v in sorted(mock["axes"].items())],
               ["Ejes que agrupan las 11 líneas de investigación (_lines/*.md, campo «axis»).",
                "PROPUESTA del mockup v4 · pendiente de validar por el grupo."])


def migrate_domains(mock):
    for n, dm in enumerate(mock["domains"]):
        data = {"key": dm["id"], "icon": dm["id"], "order": n + 1,
                "title_es": dm["t"][0], "title_en": dm["t"][1],
                "subtitle_es": dm["s"][0], "subtitle_en": dm["s"][1],
                "desc_es": dm["d"][0], "desc_en": dm["d"][1]}
        write_md(os.path.join(DEST, "_domains", f"{dm['id']}.md"), data, "",
                 header=["Ámbito de aplicación · PROPUESTA del mockup v4 (textos ES/EN)",
                         "Los proyectos se asignan con su campo «domains»."])


def write_positions(mock):
    pos = {k: {"es_m": a, "es_f": b, "en": en} for k, (a, b, en) in mock["positions"].items()}
    write_yaml(os.path.join(DEST, "_data", "positions.yml"), pos,
               ["Puestos: clave → es_m (masculino), es_f (femenino), en.",
                "El puesto en español se elige con el campo «gender» (m/f) de cada miembro.",
                "Traducción al español: PROPUESTA del mockup v4 · pendiente de validar."])
    roles = {"pi": {"es_m": "Investigador principal", "es_f": "Investigadora principal", "en": "Principal Investigator"},
             "ext": {"es_m": "Colaborador externo", "es_f": "Colaboradora externa", "en": "External Collaborator"}}
    write_yaml(os.path.join(DEST, "_data", "roles.yml"), roles,
               ["Roles especiales en el grupo (campo «role» de cada miembro). Vacío = investigador/a.",
                "Traducción al español: PROPUESTA · pendiente de validar."])


# =====================================================================
#  Noticias, eventos, convocatorias
# =====================================================================
NEWS_CAT = {
    "awards": "award", "research-project": "project", "career": "people", "intelectual-property": "transfer",
}
NEWS_CAT_FROM_LIST = [("award", "award"), ("hiring", "people"), ("promotion", "people"), ("workshop", "event"),
                      ("event", "event"), ("project", "project")]


def news_category(fm):
    c = str(fm.get("category") or "").strip().lower()
    if c in NEWS_CAT:
        return NEWS_CAT[c]
    cats = [str(x).lower() for x in (fm.get("categories") if isinstance(fm.get("categories"), list)
                                      else [fm.get("categories") or ""])]
    tags = [str(x).lower() for x in fm.get("tags") or []]
    for key, val in NEWS_CAT_FROM_LIST:
        if any(key in c2 for c2 in cats):
            return val
    if "projects" in tags:
        return "project"
    return None


def migrate_news(origen, mock, imgs):
    out = []
    for fn in sorted(os.listdir(os.path.join(origen, "_news"))):
        if not fn.endswith(".md"):
            continue
        stem = fn[:-3]
        where = f"_news/{stem}.md"
        fm, body = split_fm(os.path.join(origen, "_news", fn))
        title_en = fix_names(re.sub(r"\s+", " ", str(fm.get("title", "")).strip()))
        title_en = title_en.replace("'Semantic Interoperability Support System'", "“Semantic Interoperability Support System”")
        title_es = mock["news"].get(title_en)
        if not title_es:
            for en, es in mock["news"].items():
                if en.lower().replace("’", "'") == title_en.lower().replace("’", "'"):
                    title_es = es
        inline = bool(fm.get("inline"))
        b = convert_body(body, imgs, f"assets/img/noticias/{stem}", where)
        if inline and re.sub(r"[\W_]+", "", unbrace(b)).lower() == re.sub(r"[\W_]+", "", title_en).lower():
            b = ""
        first = re.search(r'src="([^"]+)"|fotos="([^",]+)', b)
        image = (first.group(1) or first.group(2)) if first else None
        data = {
            "date": d(fm.get("date")),
            "title_es": title_es,
            "title_en": title_en,
            "category": news_category(fm),
            "image": image,
            "lang": "en",
            "detail": False if not b.strip() else None,
            "old_urls": [f"/news/{stem}/", f"/news/{stem}.html"],
        }
        if not title_es:
            log("traducción", where, "sin título en español")
        if not data["category"]:
            log("dato", where, "sin categoría")
        if fm.get("images", {}) and not image:
            log("dato", where, "la noticia tenía galería y no se ha encontrado su imagen")
        data = {k: v for k, v in data.items() if v not in (None, "")}
        write_md(os.path.join(DEST, "_news", f"{stem}.md"), data, b)
        out.append(data)
    return out


EVENT_TYPE = {"tech_hub": "fair", "industry_day": "fair", "upm_investiga": "fair", "award_ceremony": "award"}
INVOLVEMENT = {"honored_guest": "guest"}


def migrate_events(origen, mock, news):
    news_by_date = {n["date"]: n for n in news}
    for fn in sorted(os.listdir(os.path.join(origen, "_events"))):
        if not fn.endswith(".md"):
            continue
        stem = fn[:-3]
        where = f"_events/{stem}.md"
        fm, body = split_fm(os.path.join(origen, "_events", fn))
        loc = fm.get("location") or {}
        title_en = fix_names(str(fm.get("title", "")).strip())
        title_es = None
        for en, es in mock["events"].items():
            a, b2 = ascii_slug(en), ascii_slug(title_en)
            if a == b2 or a.startswith(b2) or b2.startswith(a):
                title_es = es
        start, end = d(fm.get("start_date")), d(fm.get("end_date"))
        place = ", ".join(x for x in (loc.get("venue"), loc.get("city")) if x) or None
        rel_news = news_by_date.get(start)
        etype = fm.get("event_type") or None
        if etype in EVENT_TYPE:
            log("revisar", where, f"tipo «{etype}» → «{EVENT_TYPE[etype]}» (lista cerrada del esquema)")
            etype = EVENT_TYPE[etype]
        inv = fm.get("involvement") or None
        if inv in INVOLVEMENT:
            log("revisar", where, f"participación «{inv}» → «{INVOLVEMENT[inv]}»")
            inv = INVOLVEMENT[inv]
        data = {
            "date": start,
            "end": end if end and end != start else None,
            "title_es": title_es,
            "title_en": title_en,
            "type": etype,
            "involvement": inv,
            "place": place,
            "format": loc.get("format") or None,
            "website": fm.get("website") or None,
            "projects": fm.get("related_projects") or None,
            "news": (rel_news["old_urls"][0].split("/")[2]) if rel_news else None,
            "summary_en": re.sub(r"\s+", " ", str(fm.get("description") or "")).strip() or None,
            "lang": "en",
            "old_urls": [f"/events/{stem}/", f"/events/{stem}.html"],
        }
        if not title_es:
            log("traducción", where, "sin título en español")
        if data["website"] and "grys.etsist.upm.es/events/" in data["website"]:
            log("revisar", where, f"el enlace del evento apunta a una página de la web anterior que no existe: {data['website']}; se quita")
            data["website"] = None
        if rel_news:
            log("revisar", where, f"enlazado con la noticia del mismo día ({data['news']})")
        data = {k: v for k, v in data.items() if v not in (None, "")}
        b = convert_body(body, Images("", None), "assets/img/eventos", where)
        write_md(os.path.join(DEST, "_events", f"{stem}.md"), data, b)


DEADLINE_FIX = {
    # Confirmado por el grupo (16-10-2026): el plazo de HumAMI era el 6 de agosto a las 23:00
    "2026-07-22-humami-job": ("2026-08-06 23:00:00 +0200", "August 5, 2026", "August 6, 2026"),
}


def migrate_opportunities(origen, imgs):
    for fn in sorted(os.listdir(os.path.join(origen, "_opportunities"))):
        if not fn.endswith(".md"):
            continue
        stem = fn[:-3]
        where = f"_opportunities/{stem}.md"
        raw = open(os.path.join(origen, "_opportunities", fn), encoding="utf-8").read()
        fm, body = split_fm(os.path.join(origen, "_opportunities", fn))
        title_html = str(fm.get("title", ""))
        title = re.split(r"<br\s*/?>", title_html)
        title_main = re.sub(r"<[^>]+>", "", title[0]).strip()
        project = None
        for part in title[1:]:
            m = re.search(r"\(([^)–]+?)\s+Project", re.sub(r"<[^>]+>", "", part))
            if m:
                project = ascii_slug(m.group(1))
        mt = re.match(r"(Job|Scholarship) Opportunity:\s*(.*)", title_main)
        otype = {"job": "job", "scholarship": "scholarship"}[mt.group(1).lower()] if mt else None
        title_en = fix_names(mt.group(2).strip() if mt else title_main)
        dl_raw = re.search(r"^deadline:\s*(.+)$", raw, re.M).group(1).strip()
        dl = re.sub(r"\s+", " ", dl_raw)
        tdl = re.search(r"<b>Deadline</b>:\s*([^<\"]+)", title_html)
        if stem in DEADLINE_FIX:
            new, old_txt, new_txt = DEADLINE_FIX[stem]
            log("corregido", where, f"plazo {dl} → {new} (confirmado: 6 de agosto de 2026)")
            dl = new
            body = body.replace(old_txt, new_txt)
        elif tdl:
            log("revisar", where, f"el título decía «{tdl.group(1).strip()}» y el campo deadline «{dl}»; se mantiene el campo")
        pdf = None
        pm = re.search(r"\]\((/assets/opportunities/[^)]+\.pdf)\)", body)
        if pm:
            pdf = imgs.map(pm.group(1), "assets/convocatorias", where=where)
            body = re.sub(r"\[[^\]]*Download Full Offer[^\]]*\]\([^)]+\)\s*\n", "", body)
            if not pdf:
                log("enlace", where, f"el PDF de la oferta no existe en el repositorio antiguo: {pm.group(1)}")
        data = {
            "date": d(fm.get("date")),
            "deadline": dl,
            "type": otype,
            "title_en": title_en,
            "project": project,
            "line": None,
            "pdf": pdf,
            "contact": "gi.grys@upm.es",
            "lang": "en",
            "old_urls": [f"/opportunities/{stem}/", f"/opportunities/{stem}.html"],
        }
        b = convert_body(body, imgs, "assets/convocatorias", where)
        b = re.sub(r"^\*\*Job Opportunity at the GRyS Research Group \(UPM\)\*\*\s*$", "", b, flags=re.M)
        b = re.sub(r"^\*\*Scholarship Opportunity at the GRyS Research Group \(UPM\)\*\*\s*$", "", b, flags=re.M)
        data = {k: v for k, v in data.items() if v not in (None, "")}
        write_md(os.path.join(DEST, "_opportunities", f"{stem}.md"), data, b,
                 header=["Una convocatoria deja de publicarse automáticamente cuando pasa su «deadline»."])


# =====================================================================
#  Bibliografía
# =====================================================================
BIB_HEAD = {'papers.bib': '% Publicaciones del GRyS. Fuente: biblioteca Zotero del grupo, numero 5287048.\n% Campos propios del sitio: portal_upm, archivo_upm, project y lines.\n% Se mantienen en _bibliography/etiquetas.yml. Ver scripts/aplicar_etiquetas.py\n% No escribir el signo arroba en estos comentarios.\n\n', 'theses.bib': '% Tesis y trabajos fin de estudios dirigidos en el GRyS.\n% Tipos de entrada: phdthesis para doctorado, mastersthesis para master o DEA, thesis para grado.\n% Campo level: phd, master o bachelor. Lo usan los filtros y los recuentos.\n% supervisor: direccion. award: premio. archivo_upm: identificador en oa.upm.es.\n% No escribir el signo arroba en estos comentarios.\n\n'}

PAPER_DROP = {"urldate", "copyright", "dimensions", "altmetric", "bibtex_show"}
THESIS_DROP = PAPER_DROP | {"keywords", "teseo_show"}


def archivo_id(entry):
    for f in ("url", "website"):
        m = re.search(r"oa\.upm\.es/(\d+)", unbrace(get(entry, f, "")))
        if m:
            return m.group(1)
    return None


def migrate_bib(origen):
    src = os.path.join(origen, "_bibliography")
    papers = parse(open(os.path.join(src, "papers.bib"), encoding="utf-8").read())
    seen = set()
    for e in papers:
        drop_fields(e, PAPER_DROP)
        a = archivo_id(e)
        if a:
            set_field(e, "archivo_upm", a)
        if e["key"] in seen:
            log("bib", "papers.bib", f"clave repetida: {e['key']}")
        seen.add(e["key"])
    with open(os.path.join(DEST, "_bibliography", "papers.bib"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(BIB_HEAD["papers.bib"])
        fh.write(dump(papers))

    theses = []
    for fname, level, etype in (("phd_theses.bib", "phd", "phdthesis"),
                                ("master_theses.bib", "master", "mastersthesis"),
                                ("bachelor_theses.bib", "bachelor", "thesis")):
        for e in parse(open(os.path.join(src, fname), encoding="utf-8").read()):
            if e["type"] != etype:
                log("bib", "theses.bib", f"{e['key']}: tipo @{e['type']} en {fname} → @{etype}")
            e["type"] = etype
            drop_fields(e, THESIS_DROP)
            if unbrace(get(e, "website", "")) == unbrace(get(e, "url", "")):
                drop_fields(e, {"website"})
            set_field(e, "level", level, after="type" if get(e, "type") else None)
            if level == "bachelor":
                set_field(e, "type", "{Bachelor's thesis}")
            a = archivo_id(e)
            if a:
                set_field(e, "archivo_upm", a)
            if not get(e, "supervisor"):
                log("bib", "theses.bib", f"{e['key']}: sin director/a (supervisor)")
            theses.append(e)
    with open(os.path.join(DEST, "_bibliography", "theses.bib"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(BIB_HEAD["theses.bib"])
        fh.write(dump(theses))
    # Campos propios → _bibliography/etiquetas.yml (sobreviven a la sincronización con Zotero)
    sys.path.insert(0, os.path.join(DEST, "scripts"))
    import aplicar_etiquetas as ae  # noqa: E402
    tags = {}
    for e in papers + theses:
        a = unbrace(get(e, "archivo_upm"))
        if a:
            tags.setdefault(e["key"], {})["archivo_upm"] = a
    ae.save_tags(tags)
    # Citas en los cuerpos de los proyectos
    keys = {e["key"] for e in papers} | {e["key"] for e in theses}
    return keys


def check_citations(keys):
    for folder in ("_projects", "_members", "_news"):
        for fn in os.listdir(os.path.join(DEST, folder)):
            p = os.path.join(DEST, folder, fn)
            s = open(p, encoding="utf-8").read()
            def repl(m):
                ks = m.group(1).split()
                missing = [k for k in ks if k not in keys]
                if missing:
                    log("bib", f"{folder}/{fn}", f"cita a clave inexistente en el BibTeX: {', '.join(missing)} (se marca)")
                    return '<span class="todo">[ref. ' + ", ".join(ks) + "]</span>"
                return m.group(0)
            s2 = re.sub(r"\{%\s*cite\s+([^%]+?)\s*%\}", repl, s)
            if s2 != s:
                open(p, "w", encoding="utf-8", newline="\n").write(s2)


# =====================================================================
#  Repositorios y métricas
# =====================================================================
def migrate_repos(origen, mock):
    old = yaml.safe_load(open(os.path.join(origen, "_data", "repositories.yml"), encoding="utf-8"))
    names = [r.split("/", 1)[1] for r in old.get("github_repos", [])]
    by_name = {n: (lang, es, en) for n, lang, es, en in mock["repos"]}
    repos = []
    for n in list(by_name) + [x for x in names if x not in by_name]:
        lang, es, en = by_name.get(n, (None, None, None))
        if lang and " · " in lang:
            lang, lic = lang.split(" · ", 1)
        else:
            lic = None
        r = {"name": n, "owner": "grys-upm", "language": lang, "license": lic, "desc_es": es, "desc_en": en,
             "projects": [], "featured": n in by_name}
        repos.append({k: v for k, v in r.items() if v is not None})
        if n not in by_name:
            log("dato", "_data/repos.yml", f"{n}: sin lenguaje ni descripción (no estaba en el mockup)")
    write_yaml(os.path.join(DEST, "_data", "repos.yml"), repos,
               ["Repositorios de software y datos abiertos (github.com/grys-upm).",
                "desc_es/desc_en: descripción corta. featured: se muestra en «Software y datos».",
                "Fuente: _data/repositories.yml de la web anterior + descripciones del mockup v4."])


def write_metrics():
    data = {
        "scopus_docs": 150, "scopus_citations": 1935, "scopus_h": 20,
        "phd_theses": 23, "master_theses": 30, "master_theses_detail": "21 DEA/máster + 9 TFM", "bachelor_theses": 88,
        "source": "Portal Científico UPM", "source_url": "https://portalcientifico.upm.es/es/ipublic/entity/16280",
        "date": "2026-09",
    }
    write_yaml(os.path.join(DEST, "_data", "metrics.yml"), data,
               ["Métricas EXTERNAS del grupo (no se pueden calcular desde el BibTeX).",
                "Los recuentos de publicaciones y tesis del sitio se calculan del BibTeX al compilar",
                "(_plugins/bib_stats.rb → site.data.bib_stats). Estas cifras son de referencia y se",
                "muestran siempre con su fuente y su fecha. Actualizar a mano cuando cambien."])


# =====================================================================
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("origen")
    ap.add_argument("--mockup", required=True)
    ap.add_argument("--inventario")
    args = ap.parse_args()
    origen = os.path.abspath(args.origen)
    imgs = Images(origen, args.inventario)
    mock = read_mockup(args.mockup)

    for folder in ("_members", "_projects", "_lines", "_domains", "_news", "_events", "_opportunities"):
        p = os.path.join(DEST, folder)
        os.makedirs(p, exist_ok=True)
        for fn in os.listdir(p):
            os.remove(os.path.join(p, fn))

    members = migrate_members(origen, mock, imgs)
    migrate_projects(origen, mock, members, imgs)
    extra_projects(origen)
    migrate_lines(origen, mock)
    migrate_domains(mock)
    write_positions(mock)
    news = migrate_news(origen, mock, imgs)
    migrate_events(origen, mock, news)
    migrate_opportunities(origen, imgs)
    keys = migrate_bib(origen)
    check_citations(keys)
    migrate_repos(origen, mock)
    write_metrics()

    # Mapa de imágenes y PDF para scripts/migrar_imagenes.py
    mapa = [{"from": k, "to": v["to"], "kind": v["kind"], "used_in": v["used_in"]} for k, v in sorted(IMAGES.items())]
    write_yaml(os.path.join(DEST, "scripts", "migracion", "mapa_imagenes.yml"), mapa,
               ["Imágenes y PDF de la web anterior que USA el sitio nuevo (el resto no se migra).",
                "from: ruta en grys-upm.github.io · to: ruta en este repositorio · kind: foto|retrato|logo|pdf",
                "Lo procesa scripts/migrar_imagenes.py (WebP, 1600 px máx. + miniatura de 480 px)."])

    # Informe de la migración
    rep = os.path.join(DEST, "scripts", "migracion", "INFORME_MIGRACION.md")
    with open(rep, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Informe de la migración desde al-folio\n\n")
        fh.write(f"Generado por `migrar_desde_alfolio.py` el {TODAY.isoformat()}.\n\n")
        kinds = {}
        for k, w, m in LOG:
            kinds.setdefault(k, []).append((w, m))
        order = ["conflicto", "corregido", "revisar", "limpieza", "dato", "traducción", "alt", "imagen", "enlace", "bib", "contenido"]
        titles = {"conflicto": "Datos contradictorios en el origen", "corregido": "Correcciones aplicadas",
                  "revisar": "Decisiones que conviene revisar", "limpieza": "Contenido de demostración eliminado",
                  "dato": "Datos que faltan", "traducción": "Traducciones que faltan",
                  "alt": "Imágenes sin texto alternativo", "imagen": "Imágenes que no existen en el origen",
                  "enlace": "Enlaces rotos en el origen", "bib": "Bibliografía", "contenido": "Contenido"}
        for k in order + [k for k in kinds if k not in order]:
            if k not in kinds:
                continue
            fh.write(f"## {titles.get(k, k)} ({len(kinds[k])})\n\n")
            for w, m in kinds[k]:
                fh.write(f"- `{w}`: {m}\n")
            fh.write("\n")
        fh.write(f"## Imágenes y PDF que se migran ({len(IMAGES)})\n\n"
                 "Ver `mapa_imagenes.yml`.\n")
    print(f"Migración terminada: {len(members)} miembros, {len(IMAGES)} imágenes/PDF, {len(LOG)} incidencias")


if __name__ == "__main__":
    main()
