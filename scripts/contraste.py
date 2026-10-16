#!/usr/bin/env python3
"""
Verifica el contraste WCAG 2.2 AA (4,5:1 texto normal) de los tokens de
assets/css/grys.css en AMBOS temas. Lee los valores directamente del CSS,
así que cualquier cambio de token queda comprobado.

  python3 scripts/contraste.py            # informe
  python3 scripts/contraste.py --md       # tabla Markdown (para docs/)
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSS = open(os.path.join(ROOT, "assets", "css", "grys.css"), encoding="utf-8").read()

# (texto, fondo, mínimo, descripción). Los fondos con alfa se componen sobre --bg.
PAIRS = [
    ("--text", "--bg", 4.5, "Texto sobre fondo"),
    ("--text", "--surface", 4.5, "Texto sobre tarjeta"),
    ("--text", "--alt", 4.5, "Texto sobre franja alterna"),
    ("--muted", "--bg", 4.5, "Texto secundario sobre fondo"),
    ("--muted", "--surface", 4.5, "Texto secundario sobre tarjeta"),
    ("--muted", "--alt", 4.5, "Texto secundario sobre franja alterna"),
    ("--link", "--bg", 4.5, "Enlace sobre fondo"),
    ("--link", "--surface", 4.5, "Enlace sobre tarjeta"),
    ("--link", "--alt", 4.5, "Enlace sobre franja alterna"),
    ("--accent", "--veil", 4.5, "Acento sobre velo (menú activo, iconos)"),
    ("--btn-fg", "--btn-bg", 4.5, "Botón primario"),
    ("--btn-fg", "--btn-hover", 4.5, "Botón primario (hover)"),
    ("--todo-fg", "--todo-bg", 4.5, "Marcador «por completar»"),
    ("--code-fg", "--code-bg", 4.5, "BibTeX / código"),
    ("--ph-fg", "--ph1", 4.5, "Texto en marcador de imagen"),
]
FIXED = [  # banda del OpenTech Lab: siempre grafito
    ("#E5E9F0", "#2E3440", 4.5, "Banda del lab (claro): texto"),
    ("#C9CED6", "#2E3440", 4.5, "Banda del lab (claro): nota"),
    ("#E5E9F0", "#232831", 4.5, "Banda del lab (oscuro): texto"),
    ("#C9CED6", "#232831", 4.5, "Banda del lab (oscuro): nota"),
    ("#2E3440", "#FFFFFF", 4.5, "Banda del lab: botón blanco"),
]


def tokens(theme):
    block = re.search(r'\[data-theme="%s"\]\{(.*?)\}' % theme, CSS, re.S).group(1)
    return dict(re.findall(r"(--[\w-]+):\s*([^;]+);", block))


def parse(c):
    c = c.strip()
    if c.startswith("#"):
        h = c[1:]
        if len(h) == 3:
            h = "".join(x * 2 for x in h)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (1.0,)
    m = re.match(r"rgba?\(([^)]+)\)", c)
    parts = [float(x) for x in m.group(1).split(",")]
    return tuple(parts[:3]) + ((parts[3] if len(parts) > 3 else 1.0),)


def over(fg, bg):
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3)) + (1.0,)


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(c[0]) + 0.7152 * ch(c[1]) + 0.0722 * ch(c[2])


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main():
    md = "--md" in sys.argv
    fails = 0
    rows = []
    for theme in ("dark", "light"):
        tk = tokens(theme)
        bg = parse(tk["--bg"])
        for fg_t, bg_t, minimum, desc in PAIRS:
            if fg_t not in tk or bg_t not in tk:
                continue
            b = over(parse(tk[bg_t]), bg)
            f = over(parse(tk[fg_t]), b)
            r = ratio(f, b)
            ok = r >= minimum
            fails += not ok
            rows.append((theme, desc, f"{tk[fg_t]} / {tk[bg_t]}", r, ok))
    for fg, bg, minimum, desc in FIXED:
        r = ratio(parse(fg), parse(bg))
        fails += r < minimum
        rows.append(("ambos", desc, f"{fg} / {bg}", r, r >= minimum))
    if md:
        print("| Tema | Uso | Colores | Contraste | AA |\n|---|---|---|---|---|")
        for th, d, c, r, ok in rows:
            print(f"| {th} | {d} | `{c}` | {r:.2f}:1 | {'✔' if ok else '✘'} |".replace(".", ",", 1) if False else
                  f"| {th} | {d} | `{c}` | {str(round(r, 2)).replace('.', ',')}:1 | {'✔' if ok else '✘'} |")
    else:
        for th, d, c, r, ok in rows:
            print(f"{'OK  ' if ok else 'FALLA'} {th:6s} {r:5.2f}:1  {d}  ({c})")
        print(f"\ncontraste: {len(rows)} pares, {fails} por debajo de AA")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
