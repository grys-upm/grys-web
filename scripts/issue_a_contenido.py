#!/usr/bin/env python3
"""
Formularios de issue → ficheros de contenido (y PR).

Una sola definición (FORMULARIOS) sirve para dos cosas:
  · generar las plantillas .github/ISSUE_TEMPLATE/*.yml (las listas de
    puestos, líneas y ámbitos salen de _data/ y de las colecciones);
  · leer una issue rellenada con esas plantillas y escribir el fichero
    _news/…, _events/…, _opportunities/…, _members/… o _projects/…,
    descargando las imágenes y PDF adjuntos.

Uso:
  python scripts/issue_a_contenido.py --plantillas            regenera las plantillas
  python scripts/issue_a_contenido.py --comprobar-plantillas  sale con 1 si no están al día
  python scripts/issue_a_contenido.py --issue issue.json --salida resultado.json
      (lo usa .github/workflows/issue-a-pr.yml; issue.json = github.event.issue)

resultado.json: {"formulario": "noticia"|"" , "ok": bool, "errores": [...],
                 "avisos": [...], "ficheros": [...], "titulo": "...", "rama": "..."}
"""
import argparse
import datetime
import glob
import io
import json
import os
import re
import sys
import unicodedata
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANTILLAS = os.path.join(ROOT, ".github", "ISSUE_TEMPLATE")
CABECERA = ("# GENERADO por scripts/issue_a_contenido.py --plantillas a partir de _data/ y las\n"
            "# colecciones. No lo edites a mano: cambia el script y vuelve a generarlo.\n")
SIN_RESPUESTA = {"", "_no response_", "none", "ninguno", "ninguna"}
ADJUNTO = re.compile(r"https://(?:github\.com/user-attachments/(?:assets|files)/[^\s)\"'<>]+"
                     r"|(?:private-)?user-images\.githubusercontent\.com/[^\s)\"'<>]+)")


# ------------------------------------------------------------------ datos dinámicos
def _yaml(rel):
    p = os.path.join(ROOT, rel)
    return yaml.safe_load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def _fm(path):
    t = open(path, encoding="utf-8").read()
    m = re.match(r"---\n(.*?)\n---\n", t, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def _coleccion(nombre):
    docs = [_fm(f) for f in sorted(glob.glob(os.path.join(ROOT, f"_{nombre}", "*.md")))]
    return sorted(docs, key=lambda d: d.get("order", 99))


def opciones_dinamicas(tipo):
    """[(texto que ve quien rellena, valor que se guarda)]"""
    if tipo == "positions":
        return [(f"{v['es_m']} / {v['es_f']}" if v["es_m"] != v["es_f"] else v["es_m"], k)
                for k, v in (_yaml("_data/positions.yml") or {}).items()]
    if tipo == "lines":
        return [(d["title_es"], d["key"]) for d in _coleccion("lines")]
    if tipo == "domains":
        return [(d["title_es"], d["key"]) for d in _coleccion("domains")]
    raise ValueError(tipo)


IDIOMA = [("Español", "es"), ("Inglés", "en")]
FECHA = "AAAA-MM-DD, p. ej. 2026-11-05 (también vale 05/11/2026)"


def F(id, etiqueta, tipo="input", obligatorio=False, opciones=None, dinamico=None,
      ayuda="", ejemplo="", clave=None):
    return dict(id=id, etiqueta=etiqueta, tipo=tipo, obligatorio=obligatorio, opciones=opciones,
                dinamico=dinamico, ayuda=ayuda, ejemplo=ejemplo, clave=clave or id)


TEXTO = [
    F("lang", "Idioma en que escribes el texto", "dropdown", True, IDIOMA),
    F("texto", "Texto", "textarea", ayuda="Markdown. Encabezados con «## » (no uses «# »). "
      "Puedes arrastrar imágenes aquí: se guardarán en la web.", clave="body"),
    F("traduccion", "Traducción del texto al otro idioma (opcional)", "textarea",
      ayuda="Se publica como traducción provisional, con un aviso, hasta que alguien la revise.",
      clave="_traduccion"),
]

FORMULARIOS = {
    "noticia": dict(
        coleccion="news", nombre="📰 Nueva noticia", prefijo="[Noticia] ",
        descripcion="Propón una noticia para la web. Se convierte en una propuesta de cambios con vista previa.",
        campos=[
            F("date", "Fecha", obligatorio=True, ayuda=FECHA),
            F("title_es", "Título en español", obligatorio=True),
            F("title_en", "Título en inglés", ayuda="Si lo dejas vacío, la versión inglesa muestra el español con un aviso."),
            F("category", "Categoría", "dropdown", opciones=[
                ("Premio", "award"), ("Evento", "event"), ("Proyecto", "project"), ("Personas", "people"),
                ("Transferencia", "transfer"), ("Laboratorio", "lab")]),
            *TEXTO,
            F("imagenes", "Imágenes", "textarea", clave="_imagenes",
              ayuda="Arrastra aquí las fotos. La primera será la de la tarjeta; si hay más, se añade una galería al final."),
            F("alts", "Descripción de cada imagen", "textarea", clave="_alts",
              ayuda="Una línea por imagen, en el mismo orden: qué se ve (para quien no puede verla)."),
        ]),
    "evento": dict(
        coleccion="events", nombre="📅 Nuevo evento", prefijo="[Evento] ",
        descripcion="Añade un evento (taller, congreso, feria…). Pasa solo de «Próximos» a «Pasados» según la fecha.",
        campos=[
            F("date", "Fecha de inicio", obligatorio=True, ayuda=FECHA),
            F("end", "Fecha de fin (si dura más de un día)", ayuda=FECHA),
            F("title_es", "Título en español", obligatorio=True),
            F("title_en", "Título en inglés"),
            F("type", "Tipo", "dropdown", opciones=[
                ("Taller", "workshop"), ("Congreso", "conference"), ("Seminario", "seminar"),
                ("Escuela de verano", "summer_school"), ("Reunión", "meeting"), ("Feria", "fair"),
                ("Entrega de premios", "award"), ("Otro", "other")]),
            F("involvement", "Participación del grupo", "dropdown", opciones=[
                ("Organiza", "organizer"), ("Presenta", "presenter"), ("Participa", "participant"),
                ("Expone", "exhibitor"), ("Recibe un premio", "awardee"), ("Invitado", "guest"), ("Asiste", "attendee")]),
            F("place", "Lugar", ejemplo="ETSIST-UPM, Madrid"),
            F("format", "Formato", "dropdown", opciones=[("Presencial", "in_person"), ("En línea", "online"), ("Híbrido", "hybrid")]),
            F("website", "Página web del evento", ejemplo="https://…"),
            F("summary_es", "Resumen en español", "textarea"),
            F("summary_en", "Resumen en inglés", "textarea"),
            *TEXTO,
        ]),
    "convocatoria": dict(
        coleccion="opportunities", nombre="📣 Nueva convocatoria", prefijo="[Convocatoria] ",
        descripcion="Publica una oferta de contrato, beca, TFG/TFM o doctorado. Deja de publicarse sola al pasar el plazo.",
        campos=[
            F("deadline", "Plazo (último día)", obligatorio=True, ayuda=FECHA + ". Se cierra a las 23:59 de ese día, hora de Madrid."),
            F("date", "Fecha de publicación", ayuda=FECHA + ". Vacío = hoy."),
            F("type", "Tipo", "dropdown", True, [("Contrato", "job"), ("Beca", "scholarship"),
                                                 ("TFG o TFM", "student_project"), ("Doctorado", "phd")]),
            F("title_es", "Título en español", obligatorio=True),
            F("title_en", "Título en inglés"),
            F("project", "Proyecto (acrónimo)", ejemplo="NexTArc"),
            F("line", "Línea de investigación", "dropdown", dinamico="lines"),
            F("contact", "Correo de contacto", ejemplo="gi.grys@upm.es"),
            *TEXTO,
            F("pdf", "Convocatoria en PDF", "textarea", clave="_pdf", ayuda="Arrastra aquí el PDF (opcional)."),
        ]),
    "miembro": dict(
        coleccion="members", nombre="🧑‍🔬 Nuevo miembro", prefijo="[Miembro] ",
        descripcion="Da de alta a una persona del grupo.",
        campos=[
            F("given", "Nombre", obligatorio=True),
            F("family", "Apellidos", obligatorio=True),
            F("gender", "Género gramatical del puesto en español", "dropdown", True,
              [("Masculino (Profesor…)", "m"), ("Femenino (Profesora…)", "f")]),
            F("position", "Puesto", "dropdown", True, dinamico="positions"),
            F("since", "En el grupo desde", ayuda=FECHA),
            F("email", "Correo"),
            F("orcid", "ORCID", ejemplo="0000-0002-1825-0097"),
            F("scholar", "Google Scholar (lo que va tras «user=» en la dirección)", ejemplo="AbCdEfGhIjKl"),
            F("lines", "Líneas de investigación", "multi", dinamico="lines"),
            *TEXTO[:1],
            F("texto", "Biografía", "textarea", ayuda="Markdown, en tercera persona.", clave="body"),
            TEXTO[2],
            F("foto", "Foto", "textarea", clave="_imagenes", ayuda="Arrastra aquí una foto cuadrada (opcional)."),
        ]),
    "proyecto": dict(
        coleccion="projects", nombre="🧩 Nuevo proyecto", prefijo="[Proyecto] ",
        descripcion="Añade un proyecto de investigación o un contrato.",
        campos=[
            F("acronym", "Acrónimo", obligatorio=True),
            F("title_es", "Título en español"),
            F("title_en", "Título en inglés"),
            F("type", "Tipo", "dropdown", True, [("Competitivo (convocatoria pública)", "competitive"),
                                                 ("Contrato o convenio", "private")]),
            F("start", "Inicio", ayuda=FECHA),
            F("end", "Fin", ayuda=FECHA),
            F("programme", "Programa", ejemplo="Horizon Europe"),
            F("funder", "Financiador", ayuda="Organismos españoles con su nombre oficial en español; «European Commission» para la UE."),
            F("grant_ids", "Referencias de la ayuda (una por línea)", "textarea"),
            F("role", "Papel de la UPM", "dropdown", opciones=[("Coordinador", "coordinator"), ("Socio", "partner"),
                                                               ("Subcontratado", "subcontractor")]),
            F("pi", "Investigador/a principal del grupo (nombre y apellidos; varios separados por comas)", clave="_pi"),
            F("pi_name", "Responsable si no es del grupo"),
            F("domains", "Ámbitos de aplicación", "multi", dinamico="domains"),
            F("lines", "Líneas de investigación", "multi", dinamico="lines"),
            F("website", "Página web del proyecto", ejemplo="https://…"),
            *TEXTO,
            F("logo", "Logotipo", "textarea", clave="_imagenes", ayuda="Arrastra aquí el logotipo (opcional)."),
        ]),
}


# ------------------------------------------------------------------ plantillas
def opciones(campo):
    ops = campo["opciones"] or opciones_dinamicas(campo["dinamico"])
    for texto, _ in ops:
        if "," in texto:
            raise ValueError(f"opción con coma (rompe las listas múltiples): {texto}")
    return ops


def plantilla(clave, f):
    cuerpo = [{"type": "markdown", "attributes": {"value":
        "Rellena el formulario y pulsa **Submit new issue**. Si tienes permiso de edición en la web, "
        "en un par de minutos aparecerá aquí un enlace a la **propuesta de cambios** con su vista previa; "
        "si no, alguien del equipo web la revisará. Si te equivocas, **edita la issue** y la propuesta se rehace."}}]
    for c in f["campos"]:
        attrs = {"label": c["etiqueta"]}
        if c["ayuda"]:
            attrs["description"] = c["ayuda"]
        if c["ejemplo"]:
            attrs["placeholder"] = c["ejemplo"]
        tipo = {"input": "input", "textarea": "textarea", "dropdown": "dropdown", "multi": "dropdown"}[c["tipo"]]
        if tipo == "dropdown":
            attrs["options"] = [t for t, _ in opciones(c)]
            if c["tipo"] == "multi":
                attrs["multiple"] = True
        el = {"type": tipo, "id": c["id"], "attributes": attrs}
        if c["obligatorio"]:
            el["validations"] = {"required": True}
        cuerpo.append(el)
    doc = {"name": f["nombre"], "description": f["descripcion"], "title": f["prefijo"],
           "labels": ["contenido", clave], "body": cuerpo}
    return CABECERA + yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=1000)


def plantillas():
    return {os.path.join(PLANTILLAS, f"{k}.yml"): plantilla(k, f) for k, f in FORMULARIOS.items()}


# ------------------------------------------------------------------ lectura de la issue
def secciones(body):
    out, actual = {}, None
    for linea in (body or "").replace("\r\n", "\n").split("\n"):
        m = re.match(r"^### (.+?)\s*$", linea)
        if m:
            actual = m.group(1).strip()
            out[actual] = []
        elif actual is not None:
            out[actual].append(linea)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def detectar(body):
    s = secciones(body)
    for clave, f in FORMULARIOS.items():
        obligatorias = [c["etiqueta"] for c in f["campos"] if c["obligatorio"]]
        if obligatorias and all(e in s for e in obligatorias) and \
                sum(c["etiqueta"] in s for c in f["campos"]) >= len(f["campos"]) - 1:
            return clave, s
    return "", s


def slug(texto, maximo=60):
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    if len(t) > maximo:
        t = t[:maximo].rsplit("-", 1)[0]
    return t or "sin-titulo"


def fecha(valor, errores, etiqueta):
    v = valor.strip()
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", v) or None
    if m:
        a, mes, d = m.groups()
    else:
        m = re.fullmatch(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", v)
        if not m:
            errores.append(f"«{etiqueta}»: «{v}» no es una fecha (usa AAAA-MM-DD)")
            return None
        d, mes, a = m.groups()
    try:
        return datetime.date(int(a), int(mes), int(d))
    except ValueError:
        errores.append(f"«{etiqueta}»: «{v}» no es una fecha válida")
        return None


def plazo(d):
    """Fin del día en Madrid, en el formato de las convocatorias existentes."""
    try:
        from zoneinfo import ZoneInfo
        dt = datetime.datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=ZoneInfo("Europe/Madrid"))
        return dt.strftime("%Y-%m-%d %H:%M:%S %z")
    except Exception:
        return f"{d.isoformat()} 23:59:59 +0100"


def miembro_por_nombre(nombre):
    def norm(s):
        return re.sub(r"[^a-z]+", " ", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()).split()
    buscado = set(norm(nombre))
    for f in glob.glob(os.path.join(ROOT, "_members", "*.md")):
        d = _fm(f)
        nombre_m = set(norm(f"{d.get('given', '')} {d.get('family', '')}"))
        if buscado and buscado <= nombre_m:
            return os.path.basename(f)[:-3]
    return None


def proyecto_por_acronimo(acr):
    for f in glob.glob(os.path.join(ROOT, "_projects", "*.md")):
        if str(_fm(f).get("acronym", "")).lower() == acr.strip().lower() or os.path.basename(f)[:-3] == slug(acr):
            return os.path.basename(f)[:-3]
    return None


def descargar(url, token=None):
    """Los adjuntos de un repositorio público son públicos: primero sin
    credenciales; si falla, con el token (solo en la primera petición, no en la
    redirección al almacenamiento, que la rechazaría)."""
    def pedir(con_token):
        req = urllib.request.Request(url, headers={"User-Agent": "grys-web"})
        if con_token:
            req.add_unredirected_header("Authorization", f"token {token}")
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read(), r.headers.get("Content-Type", "")
    try:
        return pedir(False)
    except Exception:
        if not token:
            raise
        return pedir(True)


def guardar_imagen(datos, destino):
    from PIL import Image
    im = Image.open(io.BytesIO(datos))
    im.thumbnail((1600, 1600))
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "transparency" in im.info else "RGB")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    im.save(destino, "WEBP", quality=85)


def adjuntos(texto):
    return list(dict.fromkeys(ADJUNTO.findall(texto or "")))


def convertir(clave, s, numero, token=None, descargar_adjuntos=True):
    f = FORMULARIOS[clave]
    coll = f["coleccion"]
    errores, avisos, nuevos = [], [], {}
    fm, extra = {}, {}
    for c in f["campos"]:
        bruto = s.get(c["etiqueta"], "")
        valor = "" if bruto.strip().lower() in SIN_RESPUESTA else bruto.strip()
        if not valor:
            if c["obligatorio"]:
                errores.append(f"falta «{c['etiqueta']}»")
            continue
        if c["tipo"] in ("dropdown", "multi"):
            mapa = dict(opciones(c))
            elegidos = [v.strip() for v in valor.split(",")] if c["tipo"] == "multi" else [valor]
            vals = []
            for e in elegidos:
                if e not in mapa:
                    errores.append(f"«{c['etiqueta']}»: «{e}» no es una opción válida")
                else:
                    vals.append(mapa[e])
            valor = vals if c["tipo"] == "multi" else (vals[0] if vals else None)
            if valor in (None, []):
                continue
        elif c["id"] in ("date", "end", "since", "start", "deadline"):
            valor = fecha(valor, errores, c["etiqueta"])
            if valor is None:
                continue
        elif c["id"] == "grant_ids":
            valor = [l.strip(" -*") for l in valor.splitlines() if l.strip(" -*")]
        if c["clave"].startswith("_"):
            extra[c["clave"]] = valor
        else:
            fm[c["clave"]] = valor

    # --- conversiones por colección
    hoy = datetime.date.today()
    body = fm.pop("body", "") or ""
    if coll == "opportunities":
        fm.setdefault("date", hoy)
        if "deadline" in fm:
            if fm["deadline"] < hoy:
                avisos.append("el plazo ya ha pasado: la convocatoria no se mostrará")
            fm["deadline"] = plazo(fm["deadline"])
        if "project" in fm:
            p = proyecto_por_acronimo(fm["project"])
            if p:
                fm["project"] = p
            else:
                avisos.append(f"no encuentro el proyecto «{fm['project']}»; se omite")
                fm.pop("project")
    if coll == "members":
        fm["status"] = "current"
        if "scholar" in fm:
            m = re.search(r"user=([\w-]{12})", fm["scholar"])
            fm["scholar"] = m.group(1) if m else fm["scholar"]
        if "orcid" in fm:
            m = re.search(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", fm["orcid"])
            fm["orcid"] = m.group(0) if m else fm["orcid"]
    if coll == "projects" and extra.get("_pi"):
        pis = []
        for nombre in re.split(r"[,;\n]", extra["_pi"]):
            if not nombre.strip():
                continue
            m = miembro_por_nombre(nombre)
            if m:
                pis.append(m)
            else:
                avisos.append(f"«{nombre.strip()}» no es miembro del grupo: se pone como responsable externo")
                fm.setdefault("pi_name", nombre.strip())
        if pis:
            fm["pi"] = pis
    if extra.get("_traduccion"):
        otro = "en" if fm.get("lang") == "es" else "es"
        fm[f"texto_{otro}"] = extra["_traduccion"]
        fm["traduccion"] = "borrador"

    # --- nombre del fichero
    if coll in ("news", "events", "opportunities"):
        base = fm.get("date") or hoy
        nombre = f"{base.isoformat()}-{slug(fm.get('title_es') or fm.get('title_en') or 'sin-titulo')}"
    elif coll == "members":
        nombre = slug(f"{fm.get('given', '')} {fm.get('family', '')}")
    else:
        nombre = slug(fm.get("acronym", "proyecto"), 40)
    ruta = f"_{coll}/{nombre}.md"
    if os.path.exists(os.path.join(ROOT, ruta)):
        errores.append(f"ya existe «{ruta}»: para cambiarlo usa el gestor de contenidos (/admin/)")

    # --- adjuntos
    carpeta = {"news": "noticias", "events": "noticias", "members": "equipo", "projects": "proyectos"}.get(coll)
    if descargar_adjuntos and not errores:
        # imágenes dentro del texto: ![alt](adjunto) o <img alt="…" src="adjunto">
        patron = re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<url>' + ADJUNTO.pattern + r')\)'
                            r'|<img[^>]*?alt="(?P<alt2>[^"]*)"[^>]*?src="(?P<url2>' + ADJUNTO.pattern + r')"[^>]*>')
        contador = [0]

        def sust2(m):
            alt = m.group("alt") if m.group("alt") is not None else (m.group("alt2") or "")
            url = m.group("url") or m.group("url2")
            contador[0] += 1
            rel = f"/assets/img/{carpeta or 'subidas'}/{nombre}/texto-{contador[0]}.webp"
            try:
                guardar_imagen(descargar(url, token)[0], os.path.join(ROOT, rel.lstrip("/")))
                nuevos[rel] = True
                return f'{{% include figura.html src="{rel}" alt="{alt.replace(chr(34), "”")}" %}}'
            except Exception as e:
                avisos.append(f"no se pudo descargar una imagen del texto ({e}); se deja el enlace")
                return m.group(0)
        for k in ("texto_es", "texto_en"):
            if fm.get(k):
                fm[k] = patron.sub(sust2, fm[k])
        body = patron.sub(sust2, body)

        imgs = adjuntos(extra.get("_imagenes", ""))
        alts = [a.strip() for a in (extra.get("_alts") or "").splitlines() if a.strip()]
        rutas = []
        for i, url in enumerate(imgs, 1):
            rel = f"/assets/img/{carpeta or 'subidas'}/{nombre}/{i}.webp"
            try:
                guardar_imagen(descargar(url, token)[0], os.path.join(ROOT, rel.lstrip("/")))
                nuevos[rel] = True
                rutas.append(rel)
            except Exception as e:
                avisos.append(f"no se pudo descargar la imagen {i} ({e})")
        if rutas:
            campo = {"members": "photo", "news": "image", "projects": "image"}.get(coll)
            if campo:
                fm[campo] = rutas[0]
            if coll == "news" and len(rutas) > 1:
                body = body.rstrip() + '\n\n{% include galeria.html fotos="' + ",".join(rutas) + '"' + \
                    (' alts="' + "|".join(a.replace('"', "”") for a in alts[:len(rutas)]) + '"' if alts else "") + " %}\n"
        if rutas and coll == "news" and len(alts) < len(rutas):
            avisos.append("faltan descripciones de imágenes: añádelas en el gestor")
        pdfs = [u for u in adjuntos(extra.get("_pdf", ""))]
        if pdfs:
            rel = f"/assets/convocatorias/{nombre}.pdf"
            try:
                datos, tipo = descargar(pdfs[0], token)
                if not datos.startswith(b"%PDF"):
                    raise ValueError("no es un PDF")
                os.makedirs(os.path.join(ROOT, "assets", "convocatorias"), exist_ok=True)
                open(os.path.join(ROOT, rel.lstrip("/")), "wb").write(datos)
                nuevos[rel] = True
                fm["pdf"] = rel
            except Exception as e:
                avisos.append(f"no se pudo descargar el PDF ({e})")

    # --- orden de claves como en los ficheros existentes y escritura
    orden = ["date", "start", "end", "deadline", "acronym", "given", "family", "gender", "position", "status",
             "title_es", "title_en", "type", "category", "involvement", "place", "format", "programme",
             "funder", "grant_ids", "role", "pi", "pi_name", "project", "line", "contact", "pdf",
             "since", "photo", "email", "orcid", "scholar", "domains", "lines", "website", "image",
             "summary_es", "summary_en", "lang", "traduccion", "texto_es", "texto_en"]
    fm = {k: fm[k] for k in sorted(fm, key=lambda k: orden.index(k) if k in orden else 99)}
    if not body.strip() and coll == "news":
        fm["detail"] = False
    texto_fm = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000, default_flow_style=False)
    contenido = f"---\n# Creado a partir de la issue #{numero}\n{texto_fm}---\n{body.strip()}\n" if body.strip() else \
        f"---\n# Creado a partir de la issue #{numero}\n{texto_fm}---\n"
    return dict(ruta=ruta, contenido=contenido, errores=errores, avisos=avisos,
                medios=sorted(nuevos), titulo=fm.get("title_es") or fm.get("acronym") or
                f"{fm.get('given', '')} {fm.get('family', '')}".strip())


# ------------------------------------------------------------------ principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plantillas", action="store_true")
    ap.add_argument("--comprobar-plantillas", action="store_true")
    ap.add_argument("--issue")
    ap.add_argument("--salida")
    ap.add_argument("--sin-descargas", action="store_true", help="para pruebas")
    a = ap.parse_args()
    if a.plantillas or a.comprobar_plantillas:
        distintas = []
        for ruta, texto in plantillas().items():
            actual = open(ruta, encoding="utf-8").read() if os.path.exists(ruta) else None
            if actual != texto:
                distintas.append(os.path.relpath(ruta, ROOT))
                if a.plantillas:
                    os.makedirs(os.path.dirname(ruta), exist_ok=True)
                    open(ruta, "w", encoding="utf-8").write(texto)
        if a.comprobar_plantillas:
            if distintas:
                print("plantillas de issue desactualizadas: " + ", ".join(distintas))
                sys.exit(1)
            print("plantillas de issue al día")
        else:
            print(f"plantillas: {len(distintas)} actualizadas")
        return
    issue = json.load(open(a.issue, encoding="utf-8")) if a.issue else json.loads(os.environ["ISSUE"])
    clave, s = detectar(issue.get("body") or "")
    res = {"formulario": clave, "ok": False, "errores": [], "avisos": [], "ficheros": [], "titulo": "",
           "rama": f"contenido/issue-{issue.get('number')}"}
    if clave:
        r = convertir(clave, s, issue.get("number"), os.environ.get("GITHUB_TOKEN"), not a.sin_descargas)
        res.update(errores=r["errores"], avisos=r["avisos"], titulo=f"{FORMULARIOS[clave]['prefijo']}{r['titulo']}")
        if not r["errores"]:
            destino = os.path.join(ROOT, r["ruta"])
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            open(destino, "w", encoding="utf-8").write(r["contenido"])
            res["ficheros"] = [r["ruta"]] + [m.lstrip("/") for m in r["medios"]]
            res["ok"] = True
    out = json.dumps(res, ensure_ascii=False, indent=1, default=str)
    if a.salida:
        open(a.salida, "w", encoding="utf-8").write(out)
    print(out)


if __name__ == "__main__":
    main()
