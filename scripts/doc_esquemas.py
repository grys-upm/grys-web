#!/usr/bin/env python3
"""
Genera docs/DATOS.md (referencia de campos de cada tipo de contenido) a partir
de los esquemas de schemas/. Ejecútalo tras cambiar un esquema:

    python3 scripts/doc_esquemas.py
"""
import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DESC = {
    "bib_names": "Formas del nombre en el BibTeX que no se reconocen solas (p. ej. «Martinez, Joser Fernan»)",
    "texto_es": "Texto en español si el cuerpo está en inglés (Markdown; ver docs/RECETAS.md)",
    "texto_en": "Texto en inglés si el cuerpo está en español (Markdown)",
    "traduccion": "Estado de texto_es/texto_en: borrador (muestra un aviso) o revisada",
    "given": "Nombre", "family": "Apellidos", "gender": "m/f: forma del puesto en español",
    "position": "Puesto (clave de _data/positions.yml)", "role": "pi = investigador/a principal; ext = colaboración externa",
    "status": "current = actual; former = antiguo; memoriam", "since": "Fecha de incorporación (AAAA-MM-DD)",
    "until": "Fecha de salida", "photo": "Ruta de la foto WebP", "orcid": "Solo el identificador (0000-0000-0000-0000)",
    "scholar": "ID de Google Scholar (user=…)", "email": "Correo (solo se muestra en miembros actuales)",
    "lines": "Ids de líneas de investigación", "lang": "Idioma en que está escrito el texto (es/en)",
    "only_lang": "Publicar solo en ese idioma", "old_urls": "URL antiguas que redirigen aquí",
    "slug": "Parte final de la URL (por defecto, el nombre del fichero)", "published": "false = no se publica",
    "acronym": "Acrónimo", "title_es": "Título en español", "title_en": "Título en inglés",
    "type": "Tipo (ver valores)", "status ": "", "programme": "Programa (Horizon Europe, Plan Estatal…)",
    "call": "Convocatoria", "funder": "Organismo financiador", "funding": "Financiación (lista)",
    "grant_ids": "Referencias / números de concesión", "start": "Inicio (AAAA-MM-DD)", "end": "Fin (AAAA-MM-DD)",
    "pi": "Responsable(s) en GRyS: slugs de _members", "pi_name": "Responsable que no es del grupo",
    "partners": "Número de socios", "budget": "Presupuesto de GRyS (€)", "domains": "Ámbitos de aplicación",
    "repos": "Repositorios (nombres de _data/repos.yml)", "doi": "DOI del proyecto (10.3030/…)",
    "website": "Web oficial", "links": "Otros enlaces (url + title)", "image": "Imagen o logotipo (WebP)",
    "date": "Fecha (AAAA-MM-DD)", "category": "Categoría", "detail": "false = noticia breve sin página propia",
    "deadline": "Plazo: «AAAA-MM-DD HH:MM:SS +0200»; después no se publica",
    "pdf": "Oferta completa en PDF", "project": "Proyecto (slug de _projects)", "line": "Línea de investigación",
    "place": "Lugar", "key": "Identificador (igual que el nombre del fichero)", "news": "Noticia relacionada (nombre del fichero sin .md)",
    "end ": "", "involvement": "Papel del grupo", "format": "Presencial, en línea o híbrido",
}
NAMES = {"members": "Miembros · `_members/<slug>.md`", "projects": "Proyectos · `_projects/<slug>.md`",
         "news": "Noticias · `_news/AAAA-MM-DD-<slug>.md`", "events": "Eventos · `_events/<nombre>.md`",
         "opportunities": "Convocatorias · `_opportunities/<nombre>.md`", "lines": "Líneas · `_lines/<id>.md`",
         "domains": "Ámbitos · `_domains/<id>.md`"}


def typ(s):
    t = s.get("type", "")
    t = " o ".join(t) if isinstance(t, list) else t
    if s.get("format") == "date":
        t = "fecha"
    if t == "array":
        inner = s.get("items", {})
        t = "lista" + (f" de {inner.get('type')}" if inner.get("type") and "enum" not in inner else "")
    return t


def main():
    out = ["# Referencia de datos", "",
           "Generado por `scripts/doc_esquemas.py` a partir de `schemas/`. "
           "**Obligatorio** = la compilación falla si falta. El resto, si falta, aparece en el informe de "
           "pendientes y en la web como «por completar».", ""]
    for key in ("members", "projects", "news", "events", "opportunities", "lines", "domains"):
        s = json.load(open(os.path.join(ROOT, "schemas", f"{key}.schema.json"), encoding="utf-8"))
        out += [f"## {NAMES[key]}", "", s.get("description", ""), "",
                "| Campo | Tipo | Obligatorio | Valores / descripción |", "|---|---|---|---|"]
        for f, p in s["properties"].items():
            vals = p.get("enum") or p.get("items", {}).get("enum")
            d = DESC.get(f, p.get("description", ""))
            if vals:
                d = (d + ": " if d else "") + ", ".join(f"`{v}`" for v in vals)
            out.append(f"| `{f}` | {typ(p)} | {'sí' if f in s.get('required', []) else ''} | {d} |")
        if "anyOf" in s:
            out.append("\nHace falta al menos uno de: " + " o ".join(
                "`" + "`, `".join(a["required"]) + "`" for a in s["anyOf"]) + ".")
        out.append("")
    open(os.path.join(ROOT, "docs", "DATOS.md"), "w", encoding="utf-8", newline="\n").write("\n".join(out))
    print("docs/DATOS.md generado")


if __name__ == "__main__":
    main()
