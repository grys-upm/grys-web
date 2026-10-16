#!/usr/bin/env python3
"""
Descarga UNA VEZ las fuentes del manual (§8) para alojarlas en el propio sitio
(assets/fonts/). Después se suben al repositorio; el sitio publicado no hace
ninguna petición a Google Fonts ni a otros CDN.

  python3 scripts/descargar_fuentes.py

Origen: Fontsource (https://fontsource.org), que redistribuye las fuentes de
Google Fonts. Licencia de las tres familias: SIL Open Font License 1.1.
Subconjunto «latin» (cubre español e inglés: á, é, ñ, ü, ¿, ¡, €…).
Solo biblioteca estándar.
"""
import os
import sys
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEST = os.path.join(ROOT, "assets", "fonts")
CDN = "https://cdn.jsdelivr.net/fontsource/fonts/{id}@latest/latin-{weight}-{style}.woff2"

# (id de Fontsource, peso, estilo) — deben coincidir con @font-face de assets/css/grys.css
FONTS = [
    ("urbanist", 400, "normal"),
    ("urbanist", 600, "normal"),
    ("urbanist", 700, "normal"),
    ("atkinson-hyperlegible", 400, "normal"),
    ("atkinson-hyperlegible", 400, "italic"),
    ("atkinson-hyperlegible", 700, "normal"),
    ("atkinson-hyperlegible-mono", 400, "normal"),
    ("atkinson-hyperlegible-mono", 600, "normal"),
]


def main():
    os.makedirs(DEST, exist_ok=True)
    fails = 0
    for fid, weight, style in FONTS:
        url = CDN.format(id=fid, weight=weight, style=style)
        out = os.path.join(DEST, f"{fid}-latin-{weight}-{style}.woff2")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "grys-web/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if data[:4] != b"wOF2":
                raise ValueError("la respuesta no es un woff2")
            with open(out, "wb") as fh:
                fh.write(data)
            print(f"OK    {os.path.relpath(out, ROOT)}  ({len(data) // 1024} KB)")
        except Exception as e:  # noqa: BLE001
            fails += 1
            print(f"FALLO {url}\n      {e}", file=sys.stderr)
    if fails:
        print(f"\n{fails} fuentes sin descargar. Alternativa manual: descárgalas de "
              "https://fonts.google.com (Urbanist, Atkinson Hyperlegible, Atkinson Hyperlegible Mono), "
              "conviértelas a woff2 y guárdalas en assets/fonts/ con los nombres de arriba.", file=sys.stderr)
        sys.exit(1)
    print("\nListo. Añade assets/fonts/*.woff2 al repositorio.")


if __name__ == "__main__":
    main()
