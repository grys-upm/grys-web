# Recetas: cómo se hacen los cambios más habituales

Cada receta indica qué ficheros tocar y cómo comprobarlo. Antes de subir cualquier cambio, ejecuta:

```
python scripts/comprobar_datos.py
```

Debe terminar con `0 errores`. Los campos de cada tipo de contenido están en [DATOS.md](DATOS.md).

---

> **Noticias, eventos, convocatorias, miembros y proyectos** se editan normalmente desde el gestor de contenidos (`/admin/`): ver [EDITAR.md](EDITAR.md). Estas recetas sirven para editar los ficheros directamente y para todo lo demás.

## Añadir un ámbito de aplicación

1. **Crea el fichero** `_domains/<clave>.md`. La clave va en minúsculas y sin espacios, por ejemplo `industria`, y es también el nombre del fichero:

   ```yaml
   ---
   key: industria          # igual que el nombre del fichero
   icon: lab               # uno de los iconos de _includes/iconos.svg (ver abajo)
   order: 6                # posición en la página Ámbitos y en la portada
   title_es: Industria
   title_en: Industry
   subtitle_es: Fábricas conectadas
   subtitle_en: Connected factories
   desc_es: Una frase que explique qué hacemos en este ámbito.
   desc_en: One sentence explaining what we do in this domain.
   ---
   ```

2. **Asígnalo a sus proyectos:** en cada `_projects/<proyecto>.md`, añade la clave a la lista `domains`:

   ```yaml
   domains:
   - ciudad
   - industria
   ```

3. **Comprueba:** ejecuta `python scripts/comprobar_datos.py`.
   - La lista de ámbitos válidos se toma de los ficheros de `_domains/`, así que no hay que tocar ningún esquema.
   - Si escribes mal una clave en un proyecto o el icono no existe, el error te dice cuáles son las opciones válidas.

Al compilar, el ámbito aparece solo en **cuatro sitios**:
- la página Ámbitos;
- la portada;
- el filtro «Ámbito» de Proyectos;
- las etiquetas de las fichas y tarjetas de proyecto.

**Iconos disponibles** (`_includes/iconos.svg`): `campo`, `mar`, `ciudad`, `aire`, `personas`, `lab`, `net`, `globe`, `handshake`, `code`, `doc`, `cap`, `award`… Para un icono nuevo hay que añadir un `<symbol id="i-<nombre>">` en ese fichero con un dibujo SVG de 24×24 en el mismo estilo de trazo. Esto conviene que lo haga alguien con conocimientos de SVG.

**Maquetación:** la portada muestra los ámbitos en una fila de 5; con 6 o más, pasan a una segunda fila.

## Añadir una línea de investigación

Funciona igual que un ámbito, con un fichero `_lines/<clave>.md`:
- **Campos:** `key`, `axis` (número de eje de `_data/axes.yml`), `icon`, `order`, `title_es`/`title_en` y `desc_es`/`desc_en`, y el texto largo debajo del `---`.
- **Dónde se asigna:** en el campo `lines` de miembros y proyectos, y en `lines` de `_bibliography/etiquetas.yml` para las publicaciones.
- **Título de la portada:** si cambia el número de líneas o de ejes, actualiza a mano `portada.research_title` («Cuatro ejes, once líneas») en `_data/i18n/es.yml` y `en.yml`.

## Proyectos destacados de la portada

**Se eligen solos** cada vez que se compila el sitio, también en la compilación diaria:
1. primero, los proyectos **en curso**, del que empezó más tarde al que empezó antes;
2. después, el resto en **orden cronológico inverso**: los que terminaron más recientemente, primero.

Cuando un proyecto empieza o termina, la portada cambia sola.

**Decisión manual (opcional)** en `_data/portada.yml`, usando slugs (el nombre del fichero de `_projects/` sin `.md`):

```yaml
destacados:
  numero: 3            # cuántos se muestran (1 a 6)
  fijos: [swarms]      # van siempre, los primeros y en este orden
  excluir: [humami]    # no se eligen nunca automáticamente
```

- **`fijos`:** los huecos que dejan los fijos se rellenan automáticamente.
- **Errores:** `comprobar_datos.py` avisa si un slug no existe o si un proyecto está a la vez en `fijos` y en `excluir`.

## Añadir o quitar un ODS

Edita `_data/ods.yml`:
- **Principal o no:** `principal: true` lo coloca en «ODS principales»; sin ese campo va a «Otros ODS».
- **Colores:** `color` es el oficial de Naciones Unidas, y `fg` el color del número: `#000000` o `#FFFFFF`, el que dé más contraste.
- **Proyectos:** `proyectos` son slugs de `_projects/`, y `comprobar_datos.py` avisa si alguno no existe.

## Añadir un tema de TFG, TFM o doctorado

En `_data/estudiantes.yml`, añade un elemento a `propuestas`:

```yaml
propuestas:
  - nivel: tfm                     # tfg | tfm | phd
    title: { es: "Gemelo digital de una flota de drones", en: "Digital twin of a drone fleet" }
    lines: [rob, edge]             # opcional
    tutores: [nestor-lucas-martinez]
    estado: abierta                # cuando se asigne, cámbialo a «asignada» y deja de mostrarse
```

## Traducir un texto (miembros, proyectos, líneas, noticias)

El texto principal de cada ficha (lo que va después del segundo `---`) está en el idioma que indica `lang`. Para el otro idioma:

1. Añade en la cabecera `texto_es:` (si el cuerpo está en inglés) o `texto_en:` (si está en español), con el texto traducido en Markdown, sangrado con dos espacios:
   ```yaml
   lang: en
   traduccion: borrador
   texto_es: >-
     Primer párrafo de la traducción…
   ```
   Si el texto tiene varios párrafos, usa `|` en lugar de `>-` y deja una línea en blanco entre párrafos.
2. Mientras nadie la haya revisado, deja `traduccion: borrador`: la web muestra el aviso «Traducción provisional…». Cuando esté revisada, pon `traduccion: revisada` y el aviso desaparece.
3. Si el cuerpo tiene imágenes, vídeos o galerías (`{% include … %}`), copia los mismos en la traducción: la comprobación avisa si no coinciden.
4. Los títulos se traducen aparte con `title_es` / `title_en`.

Sin traducción, la página muestra el texto original con el aviso «Este texto solo está disponible en inglés».

## Añadir un puesto

Añade la clave en `_data/positions.yml` con `es_m`, `es_f` y `en` (por ejemplo, `ppl`). El orden del fichero es el orden de los grupos en la página Equipo. Después ya puedes usar esa clave en `position:` de cualquier miembro.

## Citar una publicación o tesis dentro de un texto

Escribe `{% include cita.html clave="ClaveBibTeX" %}` (la clave es la del `.bib`, lo que va tras `@article{`). Se muestra «Autor et al. (año)» enlazado: si es una publicación, a Publicaciones ya filtrada; si es una tesis, a su entrada en Tesis. Si la clave no existe, la comprobación da un error.

## Añadir o corregir una publicación

1. **En Zotero.** Añade o corrige la publicación en la biblioteca del grupo, no en `papers.bib`: los cambios hechos a mano en ese fichero se perderían en la siguiente sincronización.
2. **Clasificarla.** Ponle en Zotero las etiquetas `proyecto:<slug>` (p. ej. `proyecto:nextarc`) y `linea:<id>` (p. ej. `linea:iot`), una por proyecto o línea.
3. **Esperar o lanzar la sincronización.** Espera al lunes, o lánzala ya en *Actions → Sincronizar con Zotero → Run workflow*. Revisa y fusiona la PR que se abre.
4. **Portal Científico y Archivo Digital.** Los identificadores `portal_upm` y `archivo_upm` se ponen en `_bibliography/etiquetas.yml` (o con `scripts/cruce_portal.py`).

Las **tesis** no vienen de Zotero: se añaden a mano en `_bibliography/theses.bib`, con `level`, `supervisor` y, si lo hay, `award`.

## Añadir una asignatura

En `_data/docencia.yml` → `asignaturas`, cada elemento lleva:
- `title` y `titulacion`, en ES/EN;
- `curso` y `semestre`, opcionales;
- `profesorado`, con los slugs de `_members/`;
- `url`, opcional: la guía docente.

Mientras la lista esté vacía, la sección no aparece.

## Añadir un demostrador o una oferta tecnológica

- **Demostradores:** en `_data/demostradores.yml`, con `key`, `title`, `desc`, `personas` (slugs de miembros), `domains`, `repo` (nombre en `_data/repos.yml`), `imagen` o `video` (id de YouTube) y `presentado`.
- **Ofertas tecnológicas:** en `_data/transferencia.yml` → `ofertas`, con `icon`, `title`, `desc` y, si los hay, `repo` y `url`.

`comprobar_datos.py` avisa si una persona, un repositorio, un ámbito o un icono no existen.

## Indicar la protección de un resultado (registro, patente…) y su licencia

En `_data/transferencia.yml`, dentro de la oferta, se indican **dos cosas independientes**:
- **`proteccion`:** cómo está protegido el resultado. Es una lista, porque un mismo resultado puede tener varios títulos.
- **`licencia`:** si además se publica como **código abierto**. Un programa inscrito en el Registro de la Propiedad Intelectual puede ser también código abierto.

```yaml
    proteccion:
      - tipo: registro_pi          # registro_pi | patente | modelo_utilidad | secreto
        numero: "M-000123/2024"    # asiento registral o nº de publicación, tal como figura en el título
        oficina: { es: "Registro Territorial de la Propiedad Intelectual de la Comunidad de Madrid", en: "Madrid Regional Intellectual Property Registry" }
        fecha: 2024-05-12          # inscripción o concesión
        titulares: { es: "Universidad Politécnica de Madrid", en: "Universidad Politécnica de Madrid" }  # opcional (es el valor por defecto)
        url: https://…             # opcional: enlace a la publicación
    licencia: Apache-2.0           # opcional: identificador SPDX; si no se pone, se usa «license» del repo en _data/repos.yml
```

- **Enlaces automáticos:**
  - en patentes y modelos de utilidad sin `url`, el número enlaza a su búsqueda en Espacenet (p. ej. `ES2912345B2`);
  - la licencia enlaza a su texto en spdx.org.
- **Datos que faltan:** si el número de un registro, una patente o un modelo de utilidad está vacío, o si `licencia: ""` (vacía a propósito, pendiente), `comprobar_datos.py` avisa y la web muestra «por completar».

## Añadir una aparición en prensa

En `_data/prensa.yml` → `apariciones`:

```yaml
  - fecha: 2026-11-03
    medio: El País
    titulo: "Titular tal cual se publicó"
    url: https://…
    lang: es
    tipo: prensa      # prensa | radio | tv | web
```

Se ordenan solas por fecha, de la más reciente a la más antigua.

## Privacidad y servicios externos

Si se añade un servicio externo (un vídeo de otra plataforma, un mapa, un script) o una clave nueva de `localStorage`, hay que explicarlo en `_pages/es/privacy.md` y `_pages/en/privacy.md`. Si no se hace, `verificar_sitio.py` da error.

## Métricas de citas (Dimensions)

No hay que mantener nada: las cifras se piden a Dimensions **al compilar**, como mucho cada 7 días (`METRICAS_MAX_EDAD` en `.github/workflows/deploy.yml`).

**Para actualizarlas ya:**
1. Ve a GitHub → *Actions* → «Compilar y publicar» → *Run workflow*.
2. Marca «Actualizar ya las métricas de citas» y pulsa *Run workflow*.

**Dónde se guardan:** en la caché de Actions, no en el repositorio. Si la API falla, se publican las últimas cifras conocidas. En tu ordenador, `python scripts/metricas_dimensions.py` rellena `_data/metricas_pubs.yml` para probar, pero **no subas ese fichero con datos**: en el repositorio debe quedar vacío.

## Buscador

No hay que mantener nada: el índice se genera en cada compilación a partir de los mismos datos que las páginas. Incluye:
- las secciones de los menús;
- proyectos, personas, líneas y ámbitos;
- demostradores, noticias, eventos y repositorios;
- publicaciones, que abren Publicaciones filtrada por esa publicación.

Lo que se añade al sitio aparece solo en el buscador.

## Cambiar datos de contacto, cómo llegar o accesibilidad

Todo está en `_data/grupo.yml`:
- correo, teléfono y dirección;
- `coords`, las coordenadas del marcador del mapa;
- `como_llegar`;
- `accesibilidad`.

La página Contacto y el pie se actualizan solos.
