"""
Validador mínimo de JSON Schema (subconjunto de draft 2020-12), sin dependencias.
Cubre lo que usan los esquemas de schemas/: type, enum, pattern, minLength,
minimum, maximum, format (date, email, uri), required, properties,
additionalProperties, items, anyOf.

    from esquemas import validate, normalize
    errores = validate(normalize(datos), esquema)   # lista de textos
"""
import datetime
import re

_TYPES = {
    "string": str, "integer": int, "number": (int, float), "boolean": bool,
    "array": list, "object": dict, "null": type(None),
}


def normalize(value):
    """Convierte fechas de YAML en texto ISO, como las vería un validador JSON."""
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S %z").strip()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    return value


def _is_type(value, t):
    if t == "integer" and isinstance(value, bool):
        return False
    if t == "number" and isinstance(value, bool):
        return False
    return isinstance(value, _TYPES[t])


def _fmt_ok(value, fmt):
    if fmt == "date":
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
    if fmt == "email":
        return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value))
    if fmt == "uri":
        return bool(re.match(r"[a-z][a-z0-9+.-]*:", value))
    return True


def validate(value, schema, path=""):
    errs = []
    where = path or "(raíz)"
    t = schema.get("type")
    if t:
        types = t if isinstance(t, list) else [t]
        if not any(_is_type(value, x) for x in types):
            return [f"{where}: debe ser {' o '.join(types)} (es {type(value).__name__}: {value!r})"]
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{where}: «{value}» no es válido; opciones: {', '.join(map(str, schema['enum']))}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errs.append(f"{where}: no puede estar vacío")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errs.append(f"{where}: «{value}» no tiene el formato esperado")
        if "format" in schema and not _fmt_ok(value, schema["format"]):
            errs.append(f"{where}: «{value}» no es un {schema['format']} válido")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errs.append(f"{where}: {value} < {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errs.append(f"{where}: {value} > {schema['maximum']}")
    if isinstance(value, list) and "items" in schema:
        for i, v in enumerate(value):
            errs += validate(v, schema["items"], f"{path}[{i}]")
    if isinstance(value, dict):
        for r in schema.get("required", []):
            if value.get(r) in (None, ""):
                errs.append(f"{path + '.' if path else ''}{r}: campo obligatorio")
        props = schema.get("properties", {})
        addl = schema.get("additionalProperties", True)
        for k, v in value.items():
            p = f"{path}.{k}" if path else str(k)
            if v is None:
                continue  # campo vacío: lo recoge el informe de pendientes
            if k in props:
                errs += validate(v, props[k], p)
            elif addl is False:
                errs.append(f"{p}: campo desconocido (¿errata?)")
            elif isinstance(addl, dict):
                errs += validate(v, addl, p)
    if "anyOf" in schema and not any(not validate(value, s, path) for s in schema["anyOf"]):
        alts = [", ".join(s.get("required", [])) or "?" for s in schema["anyOf"]]
        errs.append(f"{where}: necesita al menos uno de: {' | '.join(alts)}")
    return errs
