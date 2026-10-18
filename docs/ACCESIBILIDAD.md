# Accesibilidad y bilingüismo: cómo se revisan

Objetivo: **WCAG 2.2 nivel AA** en español y en inglés. La declaración pública está en `/accesibilidad/` (`_pages/es/accessibility.md` y `_pages/en/accessibility.md`).

## 1. Revisiones automáticas (en cada PR)

En «Comprobar PR» hay dos informes. Se ven en el **resumen de la ejecución** y se descargan completos en el artefacto `informe-accesibilidad`.

| Informe | Herramienta | Qué revisa |
|---|---|---|
| `reports/a11y/estatico.md` | `scripts/a11y_estatico.py` (Python) | ids repetidos, referencias `aria-*`/`for`/anclas rotas, imágenes sin `alt`, iframes sin `title`, saltos de encabezado, enlaces y botones sin nombre, `lang` no válido, selector de idioma, textos de interfaz en el idioma equivocado |
| `reports/a11y/axe.md` | `scripts/a11y/auditar.mjs` (Chrome sin ventana + axe-core) | todas las reglas automáticas de WCAG 2.0, 2.1 y 2.2 A/AA en **tema oscuro y claro**; **reflow a 320 px** (1.4.10); errores de JavaScript |

Detalles del informe de axe:
- Solo se cargan recursos del propio sitio: YouTube, OpenStreetMap y las insignias se bloquean.
- Las «buenas prácticas» que no son requisito WCAG van en una sección aparte.
- «Para revisar a mano» recoge lo que axe no puede decidir; un caso típico es el contraste sobre la trama de fondo.

**Desde el paso 4.2 son bloqueantes** (`--estricto`): la PR falla si aparece cualquiera de estos problemas:
- un incumplimiento WCAG;
- desplazamiento horizontal a 320 px;
- un error de JavaScript;
- un hallazgo de las comprobaciones estáticas.

Aunque falle, el informe se publica igual en el resumen y en el artefacto. Las «buenas prácticas» y la lista «para revisar a mano» no bloquean.

**Qué hacer si una PR falla por accesibilidad:** abre el resumen de la ejecución, busca la regla y el ejemplo (página y elemento) y corrige la plantilla o el dato. Los casos más habituales al editar contenido:
- **Imágenes:** en `figura.html` y en las galerías, pon siempre `alt=` y `alts=`.
- **Encabezados del texto:** empiezan por `##` y no se saltan niveles. Esto ya lo comprueba `comprobar_datos.py` antes de compilar.
- **Texto en otro idioma dentro de una frase:** márcalo con `<span lang="es">…</span>`, salvo los nombres propios muy conocidos.

## 2. Ejecutarlo en tu ordenador (opcional)

Con el sitio compilado en `_site` (ver `docs/PROBAR_EN_LOCAL.md`):

```
python scripts/a11y_estatico.py _site
npm install --prefix scripts/a11y            # la primera vez (descarga Chrome)
node scripts/a11y/auditar.mjs _site          # todas las páginas: unos minutos
node scripts/a11y/auditar.mjs _site --solo /grupo/equipo/   # solo las que contienen ese texto
```

Los informes quedan en `reports/a11y/`, que no se sube al repositorio.

## 3. Lo que ninguna herramienta comprueba (revisión manual)

Las herramientas automáticas detectan alrededor de un tercio de los problemas. El resto se revisa a mano con la lista de la fase 4.4 (teclado, lector de pantalla, zoom, textos alternativos, idioma…), que se añadirá aquí.
