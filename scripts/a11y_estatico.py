#!/usr/bin/env python3
"""
Comprobaciones ESTÁTICAS de accesibilidad y bilingüismo sobre el sitio compilado.
Complementan la auditoría con navegador (scripts/a11y/auditar.mjs, axe-core).

    python scripts/a11y_estatico.py _site [--estricto]

Revisa cada página HTML (salvo las de redirección):
  ids-repetidos     · el mismo id dos veces (rompe aria-*, label for, anclas)
  referencia-rota   · aria-labelledby/-describedby/-controls, label for o
                      enlace interno «#ancla» que apuntan a un id inexistente
  img-sin-alt       · <img> sin atributo alt (alt="" es válido: decorativa)
  iframe-sin-title  · <iframe> sin title
  salto-encabezado  · se salta un nivel (p. ej. h2 → h4)
  sin-nombre        · enlace o botón sin nombre accesible (texto, aria-label,
                      aria-labelledby o alt de una imagen dentro)
  lang-invalido     · atributo lang que no es un código de idioma
  idioma-cambiado   · el selector de idioma lleva a una página cuyo <html lang>
                      no coincide con el idioma anunciado
  texto-otro-idioma · un texto de interfaz de _data/i18n/es.yml aparece en una
                      página en inglés (o al revés) fuera de un elemento con lang
Escribe reports/a11y/estatico.md. Sale con 1 solo con --estricto y errores.
Solo usa la biblioteca estándar + PyYAML.
"""
import argparse
import os
import re
import sys
from collections import OrderedDict, defaultdict
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "reports", "a11y", "estatico.md")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param",
        "source", "track", "wbr", "use", "path", "circle", "rect", "polygon", "line", "stop"}
LANG_RE = re.compile(r"^[a-z]{2,3}(-[A-Za-z]{2,4})?$")
REGLAS = OrderedDict([
    ("ids-repetidos", "Ids repetidos en la página"),
    ("referencia-rota", "Referencias a ids que no existen"),
    ("img-sin-alt", "Imágenes sin atributo alt"),
    ("iframe-sin-title", "Iframes sin title"),
    ("salto-encabezado", "Saltos en la jerarquía de encabezados"),
    ("sin-nombre", "Enlaces o botones sin nombre accesible"),
    ("lang-invalido", "Atributos lang no válidos"),
    ("idioma-cambiado", "Selector de idioma que no lleva al idioma anunciado"),
    ("texto-otro-idioma", "Textos de interfaz en el idioma equivocado"),
])


class Pagina(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = defaultdict(int)
        self.refs = []            # (atributo, id)
        self.anclas = []          # "#id"
        self.problemas = []       # (regla, detalle)
        self.headings = []
        self.html_lang = None
        self.refresh = False
        self.stack = []           # [tag, oculto, lang, interactivo]
        self.textos = []          # (idioma efectivo, texto)
        self.lang_links = []      # (hreflang, href)
        self.en_head = False
        self.en_script = 0

    # --- utilidades
    def _oculto(self):
        """Fuera del árbol de accesibilidad: aria-hidden o hidden en algún antecesor."""
        return any(e[1] or e[4] for e in self.stack)

    def _sin_nombre_aria(self):
        return any(e[1] for e in self.stack)

    def _lang(self):
        for e in reversed(self.stack):
            if e[2]:
                return e[2]
        return self.html_lang

    def _texto(self, s):
        if s and s.strip() and not self.en_script and not self.en_head:
            self.textos.append((self._lang(), s))

    def _nombre(self, s):
        if not s or self._sin_nombre_aria():
            return
        for e in self.stack:
            if e[3] is not None:
                e[3].append(s)

    # --- análisis
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._comun(tag, a)
        if tag in VOID:
            return
        inter = None
        if tag == "button" or (tag == "a" and "href" in a):
            inter = []
            for k in ("aria-label", "title"):
                if (a.get(k) or "").strip():
                    inter.append(a[k])
            if a.get("aria-labelledby"):
                inter.append("(aria-labelledby)")
        lang = a.get("lang")
        aria_oculto = "aria-hidden" in a and a.get("aria-hidden") != "false"
        self.stack.append([tag, aria_oculto, lang, inter, "hidden" in a])
        if tag == "head":
            self.en_head = True
        if tag in ("script", "style"):
            self.en_script += 1

    def handle_startendtag(self, tag, attrs):
        self._comun(tag, dict(attrs))

    def _comun(self, tag, a):
        if tag == "html":
            self.html_lang = a.get("lang")
        if tag == "meta" and (a.get("http-equiv") or "").lower() == "refresh":
            self.refresh = True
        if "id" in a and a["id"]:
            self.ids[a["id"]] += 1
        for k in ("aria-labelledby", "aria-describedby", "aria-controls"):
            for i in (a.get(k) or "").split():
                self.refs.append((k, i))
        if tag == "label" and a.get("for"):
            self.refs.append(("for", a["for"]))
        if tag == "a" and (a.get("href") or "").startswith("#") and len(a["href"]) > 1:
            self.anclas.append(unquote(a["href"][1:]))
        if tag == "a" and a.get("hreflang") and a.get("lang") and a.get("href"):
            self.lang_links.append((a["hreflang"], a["href"]))
        if "lang" in a and not LANG_RE.match(a["lang"] or ""):
            self.problemas.append(("lang-invalido", f'<{tag} lang="{a["lang"]}">'))
        if tag == "img":
            if "alt" not in a:
                self.problemas.append(("img-sin-alt", a.get("src", "")[-70:]))
            elif a["alt"].strip():
                self._nombre(a["alt"])
        if tag == "iframe" and not (a.get("title") or "").strip():
            self.problemas.append(("iframe-sin-title", a.get("src", "")[:70]))
        if re.fullmatch(r"h[1-6]", tag) and not self._oculto():
            self.headings.append(int(tag[1]))
        if not self.en_head and not self.en_script:
            for k in ("aria-label", "placeholder", "title", "alt"):
                if (a.get(k) or "").strip():
                    self.textos.append((a.get("lang") or self._lang(), a[k]))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == "head":
            self.en_head = False
        if tag in ("script", "style") and self.en_script:
            self.en_script -= 1
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                e = self.stack[i]
                invisible = self._oculto()   # el propio elemento o un antecesor
                del self.stack[i:]
                if e[3] is not None and not invisible and not "".join(e[3]).strip():
                    self.problemas.append(("sin-nombre", f"<{tag}> vacío"))
                return

    def handle_data(self, data):
        self._nombre(data)
        if not self._oculto():
            self._texto(data)


def textos_i18n():
    """Textos de interfaz que solo existen en un idioma (largos, con espacios)."""
    def hojas(d, pref=""):
        out = {}
        if isinstance(d, dict):
            for k, v in d.items():
                out.update(hojas(v, f"{pref}{k}."))
        elif isinstance(d, str):
            out[pref[:-1]] = d
        return out
    es = hojas(yaml.safe_load(open(os.path.join(ROOT, "_data", "i18n", "es.yml"), encoding="utf-8")))
    en = hojas(yaml.safe_load(open(os.path.join(ROOT, "_data", "i18n", "en.yml"), encoding="utf-8")))
    def limpio(s):
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()
    sel = {"es": {}, "en": {}}
    for k in set(es) & set(en):
        a, b = limpio(es[k]), limpio(en[k])
        if a == b:
            continue
        for lg, s in (("es", a), ("en", b)):
            if len(s) >= 14 and " " in s and not re.search(r"[%{}]", s):
                sel[lg][s] = k
    return sel


def destino(site, href, desde):
    p = urlsplit(href)
    if p.scheme or p.netloc:
        return None
    path = unquote(p.path)
    if not path.startswith("/"):
        path = os.path.join(os.path.dirname("/" + desde), path)
    f = os.path.join(site, path.lstrip("/"))
    return os.path.join(f, "index.html") if path.endswith("/") else f


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("site")
    ap.add_argument("--baseurl", default="")
    ap.add_argument("--estricto", action="store_true")
    ap.add_argument("--salida", default=OUT)
    args = ap.parse_args()
    site, base = os.path.abspath(args.site), args.baseurl.rstrip("/")
    i18n = textos_i18n()
    hallazgos = defaultdict(list)    # regla → [(página, detalle)]
    langs_cache = {}
    n = 0
    for dirpath, _, files in os.walk(site):
        for fn in sorted(files):
            if not fn.endswith(".html"):
                continue
            fp = os.path.join(dirpath, fn)
            rel = os.path.relpath(fp, site).replace(os.sep, "/")
            html_txt = open(fp, encoding="utf-8", errors="replace").read()
            if 'name="grys-herramienta"' in html_txt:   # gestor de contenidos: no es del sitio público
                continue
            p = Pagina()
            p.feed(html_txt)
            if p.refresh:
                continue
            n += 1
            for regla, det in p.problemas:
                hallazgos[regla].append((rel, det))
            for i, c in p.ids.items():
                if c > 1:
                    hallazgos["ids-repetidos"].append((rel, f'id="{i}" ×{c}'))
            for k, i in p.refs:
                if i not in p.ids:
                    hallazgos["referencia-rota"].append((rel, f'{k}="{i}"'))
            for i in set(p.anclas):
                if i not in p.ids and i != "top":
                    hallazgos["referencia-rota"].append((rel, f'href="#{i}"'))
            prev = 0
            for h in p.headings:
                if prev and h > prev + 1:
                    hallazgos["salto-encabezado"].append((rel, f"h{prev} → h{h}"))
                    break
                prev = h
            for hl, href in p.lang_links:
                h2 = href[len(base):] if base and href.startswith(base) else href
                t = destino(site, h2, rel)
                if t and os.path.exists(t):
                    if t not in langs_cache:
                        q = Pagina()
                        q.feed(open(t, encoding="utf-8", errors="replace").read())
                        langs_cache[t] = q.html_lang
                    if langs_cache[t] != hl:
                        hallazgos["idioma-cambiado"].append((rel, f'{href} anuncia «{hl}» y es «{langs_cache[t]}»'))
            otro = "es" if p.html_lang == "en" else "en"
            if p.html_lang in ("es", "en"):
                vistos = set()
                texto = [(lg, re.sub(r"\s+", " ", s)) for lg, s in p.textos]
                bloque = " ".join(s for lg, s in texto if lg == p.html_lang)
                for s, clave in i18n[otro].items():
                    if s in bloque and clave not in vistos:
                        vistos.add(clave)
                        hallazgos["texto-otro-idioma"].append((rel, f"«{s[:60]}» ({otro}.yml: {clave})"))
    # Informe
    total = sum(len(v) for v in hallazgos.values())
    out = [f"## Accesibilidad · comprobaciones estáticas", "",
           f"{n} páginas revisadas · **{total} hallazgos**", "",
           "| Comprobación | Páginas | Hallazgos |", "|---|---|---|"]
    for r, nombre in REGLAS.items():
        v = hallazgos.get(r, [])
        out.append(f"| {nombre} (`{r}`) | {len({x[0] for x in v})} | {len(v)} |")
    for r, nombre in REGLAS.items():
        v = hallazgos.get(r, [])
        if not v:
            continue
        out += ["", f"### {nombre} (`{r}`)", ""]
        # agrupar por detalle (lo mismo en muchas páginas = una plantilla)
        por_det = OrderedDict()
        for pag, det in v:
            por_det.setdefault(det, []).append(pag)
        for det, pags in list(por_det.items())[:25]:
            unicas = list(dict.fromkeys(pags))
            ej = ", ".join(unicas[:3]) + (f" y {len(unicas) - 3} más" if len(unicas) > 3 else "")
            veces = f" ({len(pags)} veces)" if len(pags) != len(unicas) else ""
            out.append(f"- `{det}` · {len(unicas)} página(s){veces}: {ej}")
        if len(por_det) > 25:
            out.append(f"- … y {len(por_det) - 25} casos distintos más")
    os.makedirs(os.path.dirname(args.salida), exist_ok=True)
    open(args.salida, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"a11y_estatico: {n} páginas; {total} hallazgos → {os.path.relpath(args.salida, ROOT)}")
    for r in REGLAS:
        if hallazgos.get(r):
            print(f"  {r}: {len(hallazgos[r])}")
    return 1 if (args.estricto and total) else 0


if __name__ == "__main__":
    sys.exit(main())
