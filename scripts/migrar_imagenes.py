#!/usr/bin/env python3
"""
Copia al sitio nuevo SOLO las imágenes y PDF que usa (scripts/migracion/mapa_imagenes.yml),
convertidas a WebP. Se ejecuta UNA VEZ en un ordenador con el repositorio antiguo.

    python -m pip install pillow pyyaml
    python scripts/migrar_imagenes.py RUTA/AL/REPO/grys-upm.github.io

Por cada imagen genera:
  · <nombre>.webp       ancho máximo 1600 px (retratos: 800 px; logos: 800 px)
  · <nombre>-480.webp   miniatura de 480 px (tarjetas, galerías, avatares)
Los PDF se copian tal cual. No toca los originales. Si un fichero de destino ya
existe, no se vuelve a convertir (usa --forzar para rehacerlo).

Después: sube la carpeta assets/ del repositorio nuevo a GitHub
(Add file → Upload files, arrastrando las carpetas assets/img y assets/convocatorias).
"""
import argparse
import os
import shutil
import sys

try:
    import yaml
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Faltan dependencias:  python -m pip install pillow pyyaml")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAX = {"foto": 1600, "retrato": 800, "logo": 800}
THUMB = 480
QUALITY = {"foto": 80, "retrato": 82, "logo": 90}


def save_webp(im, path, width, quality):
    im = im.copy()
    if im.width > width:
        im.thumbnail((width, width * 10), Image.LANCZOS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "WEBP", quality=quality, method=6)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("origen", help="carpeta del repositorio antiguo (grys-upm.github.io)")
    ap.add_argument("--forzar", action="store_true", help="rehacer aunque el destino exista")
    args = ap.parse_args()
    origen = os.path.abspath(args.origen)
    if not (os.path.isdir(os.path.join(origen, "assets", "img")) and os.path.isdir(os.path.join(origen, "_people"))):
        sys.exit(f"«{origen}» no parece el repositorio ANTIGUO (grys-upm.github.io): "
                 "debe contener las carpetas assets/img y _people.")
    if os.path.abspath(origen) == ROOT:
        sys.exit("El argumento debe ser la carpeta del repositorio ANTIGUO, no la del nuevo.")
    print(f"Origen (web antigua): {origen}\nDestino (web nueva):  {ROOT}\n")
    args.origen = origen
    mapa = yaml.safe_load(open(os.path.join(ROOT, "scripts", "migracion", "mapa_imagenes.yml"), encoding="utf-8"))
    ok = skip = fail = 0
    before = after = 0
    for item in mapa:
        src = os.path.join(args.origen, item["from"])
        dst = os.path.join(ROOT, item["to"])
        if not os.path.exists(src):
            print(f"FALTA  {item['from']}")
            fail += 1
            continue
        if os.path.exists(dst) and not args.forzar:
            skip += 1
            continue
        before += os.path.getsize(src)
        try:
            if item["kind"] == "pdf":
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
            else:
                im = Image.open(src)
                im = ImageOps.exif_transpose(im)          # respeta la orientación de la cámara
                im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
                kind = item.get("kind", "foto")
                save_webp(im, dst, MAX.get(kind, 1600), QUALITY.get(kind, 80))
                save_webp(im, dst.replace(".webp", "-480.webp"), THUMB, QUALITY.get(kind, 80))
                after += os.path.getsize(dst.replace(".webp", "-480.webp"))
            after += os.path.getsize(dst)
            ok += 1
            print(f"OK     {item['to']}")
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"ERROR  {item['from']}: {e}")
    mb = 1024 * 1024
    print(f"\n{ok} convertidos, {skip} ya existían, {fail} con problemas. "
          f"Tamaño: {before / mb:.1f} MB → {after / mb:.1f} MB")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
