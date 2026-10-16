"""
Lector/escritor BibTeX mínimo y sin dependencias, pensado para la salida de
Zotero (y del propio sitio). Conserva el orden de las entradas y de los campos
y el texto de cada valor tal cual (sin interpretar LaTeX).

    from bibtex_simple import parse, dump
    entries = parse(open("papers.bib", encoding="utf-8").read())
    # entries: lista de dict {"type": "article", "key": "…", "fields": [(nombre, valor_bruto), …]}
    # valor_bruto incluye las llaves/comillas externas: "{Título}", "feb", "2026"
"""
import re

__all__ = ["parse", "dump", "get", "set_field", "drop_fields", "unbrace"]

_ENTRY = re.compile(r"@(\w+)\s*\{", re.S)
_KEY = re.compile(r"\s*([^,\s]+)\s*,")
_FIELD = re.compile(r"\s*([A-Za-z_][\w-]*)\s*=\s*")
_END = re.compile(r"\s*,?\s*\}")
_COMMA = re.compile(r"\s*,")


def _braced(s, i):
    depth, j = 0, i
    while j < len(s):
        if s[j] == "{" and (j == 0 or s[j - 1] != "\\"):
            depth += 1
        elif s[j] == "}" and s[j - 1] != "\\":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise ValueError(f"llave sin cerrar cerca de: {s[i:i + 60]!r}")


def _quoted(s, i):
    j, depth = i + 1, 0
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
        elif s[j] == '"' and depth == 0 and s[j - 1] != "\\":
            return j + 1
        j += 1
    raise ValueError(f"comillas sin cerrar cerca de: {s[i:i + 60]!r}")


def _read_value(s, i):
    """Lee un valor desde s[i]. Devuelve (valor_bruto, nueva_i). Admite concatenación con #."""
    parts = []
    while True:
        while i < len(s) and s[i] in " \t\r\n":
            i += 1
        c = s[i]
        if c == "{":
            j = _braced(s, i)
        elif c == '"':
            j = _quoted(s, i)
        else:
            j = i + re.match(r"[^,#}\s]+", s[i:]).end()
        parts.append(s[i:j])
        i = j
        k = i
        while k < len(s) and s[k] in " \t\r\n":
            k += 1
        if k < len(s) and s[k] == "#":
            parts.append("#")
            i = k + 1
            continue
        return " ".join(parts), i


def parse(text):
    entries = []
    i = 0
    while True:
        m = _ENTRY.search(text, i)
        if not m:
            break
        etype = m.group(1).lower()
        i = m.end()
        if etype in ("comment", "preamble", "string"):
            i = _braced(text, m.end() - 1)
            continue
        km = _KEY.match(text, i)
        key = km.group(1)
        i = km.end()
        fields = []
        while True:
            fm = _FIELD.match(text, i)
            if not fm:
                cm = _END.match(text, i)
                i = cm.end() if cm else i + 1
                break
            val, i = _read_value(text, fm.end())
            fields.append((fm.group(1).lower(), val))
            cm = _COMMA.match(text, i)
            if cm:
                i = cm.end()
        entries.append({"type": etype, "key": key, "fields": fields})
    return entries


def get(entry, name, default=None):
    for k, v in entry["fields"]:
        if k == name:
            return v
    return default


def unbrace(value):
    """Valor bruto → texto plano aproximado (quita llaves y comillas externas)."""
    if value is None:
        return ""
    v = value.strip()
    if (v.startswith("{") and v.endswith("}")) or (v.startswith('"') and v.endswith('"')):
        v = v[1:-1]
    return re.sub(r"[{}]", "", v).strip()


def set_field(entry, name, value, after=None):
    """Pone name = {value}. Si value ya viene entre llaves o es un número, se deja tal cual."""
    value = str(value)
    raw = value if re.fullmatch(r"\{.*\}|\d+", value, re.S) else "{" + value + "}"
    for n, (k, _) in enumerate(entry["fields"]):
        if k == name:
            entry["fields"][n] = (name, raw)
            return
    pos = len(entry["fields"])
    if after:
        for n, (k, _) in enumerate(entry["fields"]):
            if k == after:
                pos = n + 1
    entry["fields"].insert(pos, (name, raw))


def drop_fields(entry, names):
    entry["fields"] = [(k, v) for k, v in entry["fields"] if k not in names]


def dump(entries):
    out = []
    for e in entries:
        lines = [f"@{e['type']}{{{e['key']},"]
        lines += [f"\t{k} = {v}," for k, v in e["fields"]]
        if len(lines) > 1:
            lines[-1] = lines[-1][:-1]
        lines.append("}")
        out.append("\n".join(lines))
    return "\n\n".join(out) + "\n"
