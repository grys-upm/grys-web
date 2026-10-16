# Registro de cambios

## Fase 2 · Corrección 3 (16-10-2026)

La web ya compila. `verificar_sitio.py` encontró 16 enlaces rotos y, al revisarlos, apareció un fallo silencioso:
- **Campos reservados por Jekyll:** en los elementos de una colección, `url` e `id` devuelven el dato interno de Jekyll y no el escrito en el fichero.
  - Los eventos guardaban su web en `url` y enlazaban a páginas inexistentes (6 enlaces rotos). El campo pasa a llamarse **`website`**.
  - **Fallo silencioso:** las líneas y los ámbitos usaban `id`, así que no se veía ningún ámbito en Proyectos ni en las fichas, y la página Ámbitos salía sin proyectos. El campo pasa a llamarse **`key`**.
- **Enlaces internos en los textos:** las biografías de Mario San Emeterio y Vicente Hernández enlazaban a `/projects/…`, una dirección que ya estaba rota en la web anterior (10 enlaces rotos). Un enlace fijo, además, no puede valer para los dos idiomas. Se usa el filtro nuevo **`ref`**: `[AFarCloud]({{ 'projects/afarcloud' | ref }})` lleva a la ficha en el idioma de la página.
- **`comprobar_datos.py`:** da error si se usa un campo reservado (`id`, `url`, `path`, `content`…), si hay un enlace interno escrito a mano en el texto de un elemento y si un `ref` apunta a una ficha que no existe. He comprobado que detecta los tres casos con los datos anteriores: 38 errores.
- **Regeneración:** esquemas, `docs/DATOS.md` y los datos afectados (11 líneas, 5 ámbitos, 1 evento y 2 miembros), con el script de migración corregido.

## Fase 2 · Corrección 2 (16-10-2026)

- **Error `undefined filter remove_last`:** ese filtro es de Liquid 5 y Jekyll 4.4 usa Liquid 4.0.4. He creado el filtro propio `url_label`, que quita «https://», «www.» y la barra final, y lo uso en las fichas de miembro y de proyecto.
- **`comprobar_datos.py`:** la lista de filtros permitidos es ahora la **exacta** de Liquid 4.0.4, Jekyll 4.4 y el plugin. La anterior estaba escrita a mano e incluía `remove_last` por error. Las 38 funciones que usan las plantillas están en la lista.
- **Tesis:** se consultan por el campo `level` (`@*[level=phd]`…) y no por el tipo de entrada, porque jekyll-scholar trata `phdthesis` y `mastersthesis` como alias de `thesis`.
- **URL de noticias (preventivo):** el plugin quita siempre el prefijo `AAAA-MM-DD-` del *slug*, porque Jekyll puede rellenarlo con el nombre de fichero completo y la fecha saldría repetida en la URL.

## Fase 2 · Corrección 1 (16-10-2026)

Errores de la primera compilación de la fase 2 en Actions:
- **Error de Liquid en `_layouts/bib.html`:** `remove: "}"` dentro de `{{ … }}` cortaba la variable, porque Liquid 4 la cierra en el primer «}». Ahora se usa un filtro nuevo, `bib_text` (`_plugins/grys.rb`), que quita las llaves y las órdenes LaTeX básicas.
- **3 avisos `Lexer: unexpected token '('`:** venían de BibTeX-Ruby. El comentario de cabecera de `theses.bib` contenía «@phdthesis», «@mastersthesis» y «@thesis», y la biblioteca los tomaba como entradas. He reescrito las cabeceras de `papers.bib` y `theses.bib` sin «@» ni paréntesis; las entradas no cambian.
- **`comprobar_datos.py`** detecta ahora los dos casos antes de compilar: un «}» dentro de `{{ … }}` (con el mismo troceado que Liquid 4) y un «@» fuera de las entradas de un `.bib`. Los números de línea de sus mensajes ya son correctos.
- **Workflows:** la compilación falla también con los avisos `WARN --` de BibTeX-Ruby, que antes no se filtraban.

## Fase 2 · Datos y migración del contenido (16-10-2026)

### Migración
Todo el contenido repetible de la web anterior es ahora **un fichero de datos por elemento**. Se ha migrado con `scripts/migracion/migrar_desde_alfolio.py`, que queda en el repositorio como documentación y no hay que volver a ejecutar. No se ha inventado ningún dato: lo que falta queda vacío y lo recoge el informe de pendientes.

| Contenido | Origen | Destino | Elementos |
|---|---|---|---|
| Miembros | `_people/` | `_members/` | 40 (11 actuales, 28 antiguos, 1 *in memoriam*) |
| Proyectos | `_projects/` (+ tablas HTML «Project Information») | `_projects/` | 32 + 2 (HumAMI y AFarEdge: título y referencias de sus convocatorias; programa y fechas confirmados por el grupo; AFarEdge, además, desde CORDIS 101252360) |
| Líneas | `research-areas.md` + mockup | `_lines/` + `_data/axes.yml` | 11 líneas en 4 ejes |
| Ámbitos | mockup | `_domains/` | 5 |
| Noticias | `_news/` | `_news/` | 16 (8 con página propia y 8 breves) |
| Eventos | `_events/` | `_events/` | 6 |
| Convocatorias | `_opportunities/` | `_opportunities/` | 4 (todas caducadas: no se publican) |
| Publicaciones | `papers.bib` | `papers.bib` limpio | 169 |
| Tesis | 3 ficheros `.bib` | `theses.bib` unificado | 52 (14 de doctorado, 17 de máster y 21 de grado) |
| Puestos y roles | `_people` + mockup | `_data/positions.yml`, `roles.yml` | 10 + 2 |
| Repositorios | `repositories.yml` + mockup | `_data/repos.yml` | 13 |
| Métricas externas | Portal Científico (sep. 2026) | `_data/metrics.yml` | Scopus y tesis, con fuente y fecha |

**Transformaciones:**
- **Proyectos:** los datos de las tablas HTML pasan a campos: organismo, programa, financiación, referencias, fechas, responsable en la UPM, coordinación, DOI y enlaces. El rol y el responsable se enlazan a la ficha del miembro cuando es del grupo. AFarCloud tenía la **plantilla de ejemplo de al-folio** (imágenes `1.jpg`…`11.jpg` y cita `einstein1950meaning`); se ha eliminado.
- **Textos:** el HTML de al-folio se convierte en Markdown con *includes* propios:
  - `figure.liquid` → `figura.html`;
  - galerías *swiper* → `galeria.html`;
  - YouTube → `video.html` con `youtube-nocookie`;
  - pies de foto → `<p class="pie">`.
  Además se quitan los contenedores de Bootstrap, los emojis y `target="_blank"`, y los títulos empiezan en `h2`.
- **Nombres:** «OpenTechLab» y «Open TechLab» pasan a «OpenTech Lab»; no se tocan las URL ni los nombres de repositorio.
- **Bibliografía:**
  - fuera `urldate`, `copyright`, `dimensions`, `altmetric` y `bibtex_show`;
  - las tesis llevan el tipo correcto: `@phdthesis`, `@mastersthesis` y `@thesis`, más el campo `level`. Se han corregido 21 TFG tipados como `@phdthesis` y 1 TFM;
  - `archivo_upm` se extrae de las URL de oa.upm.es: 47 tesis y 1 publicación.
- **Campos propios del BibTeX** (`portal_upm`, `archivo_upm`, `project`, `lines`): viven en `_bibliography/etiquetas.yml` y `scripts/aplicar_etiquetas.py` los vuelve a escribir en el `.bib`. Así **sobreviven a la sincronización con Zotero**.
- **Convocatoria HumAMI:** el plazo queda en el 6-08-2026 a las 23:00, como confirmaste. También se ha corregido en el texto.
- **Redirecciones automáticas:** cada elemento lleva en `old_urls` sus URL antiguas, y estas redirigen a su ficha o a su página de lista. Por ejemplo: `/team/jf/`, `/research/projects/µswn/` y `/news/….html`.

### Sitio
- **Plugin `grys.rb`:**
  - el campo `lang` es el idioma del texto; todo se publica en ES y EN, y si el texto no está en el idioma de la página se marca con `lang="en"` y un aviso (WCAG 3.1.2);
  - estado de los proyectos calculado con las fechas en cada compilación (campo `state`);
  - fichas opcionales (`detail: false`);
  - redirecciones desde `old_urls`;
  - filtros nuevos `tr` y `member`.
- **Plugin `bib_stats.rb`:** recuentos calculados desde el BibTeX (`site.data.bib_stats`).
- **Páginas con datos:** Equipo, Líneas, Ámbitos, Proyectos, Publicaciones, Tesis, Noticias, Eventos (próximos y pasados según la fecha de compilación), Convocatorias (solo las abiertas; si no hay, el bloque vacío) y Software.
- **Fichas de detalle con su tabla de datos:**
  - miembro: puesto según el género, periodo, perfiles y proyectos que dirige;
  - proyecto: tabla completa con «por completar» en los campos mínimos que faltan;
  - línea: personas y proyectos;
  - noticia.
- **Publicaciones (`bib.html`):** enlaces a DOI, Portal Científico, Archivo Digital, Altmetric, Dimensions y Google Scholar (por ID o por título); en las tesis, también TESEO, dirección y premio.
- **Diseño:** el marcado y el CSS de esta fase son provisionales; el diseño definitivo de los componentes llega en la fase 3.

### Calidad
- **Esquemas JSON** (`schemas/*.schema.json`) para las 7 colecciones y 5 ficheros de datos, con un validador propio sin dependencias (`scripts/esquemas.py`). Al validar los datos migrados aparecieron 6 errores reales, ya corregidos: un ORCID escrito como URL, 4 tipos de evento y 1 tipo de participación fuera de la lista.
- **`comprobar_datos.py`** comprueba además:
  - referencias cruzadas: responsables, repositorios, proyecto de cada convocatoria, noticia de cada evento y etiquetas del BibTeX;
  - que el nombre de fichero de cada noticia coincide con su fecha;
  - que los *includes* usados existen y que no hay `old_urls` repetidas;
  - que las etiquetas del BibTeX están aplicadas;
  - las imágenes que faltan, como aviso.
- **Scripts nuevos:**
  - `informe_pendientes.py`: informe por elemento, que también aparece en el resumen de Actions y como artefacto;
  - `cruce_portal.py`: BibTeX ↔ Portal Científico o Archivo Digital en ambos sentidos, desde CSV o RIS;
  - `migrar_imagenes.py`: WebP de 1600 px y miniatura de 480 px;
  - `aplicar_etiquetas.py`;
  - `doc_esquemas.py`: genera `docs/DATOS.md`.
- **`verificar_sitio.py`:** las imágenes que faltan son aviso hasta la migración (`--estricto` para tratarlas como error).

### Probado aquí (sin Ruby)
- **Lector y escritor de BibTeX:** reconstruye exactamente los 7 `.bib` (2.504 campos en `papers.bib`).
- **`migrar_imagenes.py`:** con 119 imágenes y PDF sintéticos, convierte todos y no repite el trabajo en una segunda ejecución. Después, `comprobar_datos.py` da 0 avisos.
- **`cruce_portal.py`:** con un CSV sintético de 121 registros encuentra 120 coincidencias (por DOI y por título), 1 discrepancia de año, 1 registro que solo está en el Portal y 49 que solo están en el BibTeX, y aplica los enlaces a `etiquetas.yml`. Con RIS, encuentra la coincidencia.
- **Comprobaciones finales:** `comprobar_datos.py` da 0 errores; `contraste.py`, 35/35 pares AA. La sintaxis de Python, JS y los *workflows* es correcta.

### Ficheros
- **Nuevos:**
  - colecciones: `_members/` (40), `_projects/` (34), `_lines/` (11), `_domains/` (5), `_news/` (16), `_events/` (6), `_opportunities/` (4);
  - datos: `_data/{positions,roles,axes,repos,metrics}.yml`;
  - bibliografía: `_bibliography/{theses.bib,etiquetas.yml}`;
  - *plugins*: `_plugins/bib_stats.rb`;
  - *includes*: `_includes/{figura,galeria,video,puesto,rol,estado,avatar}.html`, `_includes/listas/*` (11), `_includes/fichas/*` (7);
  - esquemas: `schemas/*` (12);
  - scripts: `scripts/{esquemas,informe_pendientes,cruce_portal,migrar_imagenes,aplicar_etiquetas,doc_esquemas}.py`, `scripts/migracion/*`;
  - documentación: `docs/DATOS.md`.
- **Modificados:**
  - `_plugins/grys.rb`, `_layouts/{detail,bib}.html`, `_includes/pagehead.html`;
  - `_pages/{es,en}/{team,lines,domains,projects,publications,theses,news,events,opportunities,software}.md`;
  - `_data/routes.yml` (sección `lists`), `_data/i18n/{es,en}.yml`;
  - `_config.yml`, `_config.staging.yml` (repositorio `grys-web`);
  - `_bibliography/papers.bib`, `assets/css/grys.css`;
  - `scripts/{comprobar_datos,verificar_sitio}.py`, `.github/workflows/{deploy,pr}.yml`, `docs/COMPILAR.md`, `PENDIENTES.md`.
- **Eliminadas:** las muestras de la fase 1, sustituidas por los datos migrados.

---

## Fase 1 · Base del sitio nuevo (16-10-2026)

Es un repositorio nuevo, en paralelo a `grys-upm.github.io`. No se ha copiado nada de al-folio: la limpieza consiste en traer al sitio nuevo solo lo que se usa.

### Decisiones aplicadas
1. **Sitio Jekyll propio**, sin tema. Las gemas están fijadas: jekyll ~> 4.4.1, jekyll-polyglot ~> 1.14 y jekyll-scholar ~> 7.2. Ya no se usan Bootstrap, MDB, jQuery, Font Awesome, Tabler, MathJax, distill, giscus, disqus, plotly, echarts ni ninguna librería de CDN.
2. **Un fichero por elemento** en colecciones: `_members`, `_projects`, `_lines`, `_domains`, `_news`, `_events` y `_opportunities`.
3. **Despliegue con `actions/deploy-pages`**. El repositorio de pruebas se publica con `noindex` y la web actual no se toca.
4. **El bilingüe se adelanta a la fase 1** (estaba previsto en la 4). Las URL, las fichas y las redirecciones dependen de polyglot, y combinarlo con scholar y con fichas generadas es el principal riesgo técnico. Conviene validarlo en la primera compilación y no después del diseño.

### Hecho
- **Mapa del sitio como datos** (`_data/routes.yml`): 5 menús, las 22 páginas de la tabla con URL ES/EN, títulos y descripciones, y los patrones de las fichas de detalle.
- **44 páginas** (`_pages/es`, `_pages/en`) con `page_id` y `permalink` coherentes con el mapa. El contenido está marcado como «pendiente de migración» con la clase única `.todo`.
- **Plugin `_plugins/grys.rb`:**
  - filtros `route_url`, `url_lang`, `detail_url`, `alt_url` y `l10n`;
  - generador de fichas ES/EN a partir de las colecciones;
  - generador de redirecciones (`_data/redirects.yml` + `old_urls` de cada elemento).
- **27 redirecciones** desde las URL de la web anterior, que era solo en inglés, hacia sus equivalentes en `/en/`.
- **Estructura común:**
  - *Layouts*: `default`, `page`, `home`, `detail` (provisional), `redirect` y `bib`.
  - *Includes*: `head`, `header`, `footer` (cofirma UPM + GRyS), `pagehead`, `logo`, `lang-switch`, `theme-toggle`, `icono` e `iconos.svg`.
  - `404.html` bilingüe, `sitemap.xml` con `hreflang` y `robots.txt`.
- **Tema:**
  - oscuro por defecto, aplicado con un *script* en línea en el `<head>` antes del CSS, así que no hay parpadeo;
  - la preferencia se guarda en `localStorage` y `theme-color` cambia con el tema;
  - el logotipo pasa a negativo en oscuro sin JavaScript (CSS + `loading="lazy"`).
- **Accesibilidad de base:**
  - enlace «Saltar al contenido», regiones semánticas y un solo `<h1>` por página;
  - menús con `button[aria-expanded]` que se cierran con Esc, al hacer clic fuera o al salir con el tabulador;
  - selector de idioma con enlaces reales (`hreflang`, `aria-current`);
  - usable sin JavaScript: los menús se abren con foco o ratón y el cajón móvil queda visible.
- **CSS** (`assets/css/grys.css`): el del mockup sin la barra de herramientas, con fuentes alojadas en el sitio (`@font-face` + `font-display: swap`) y los añadidos para el sitio estático.
- **Trama de hexágonos** como **SVG estático**, con la misma geometría que el mockup (arista plana, paso 1,5 R × √3 R). Hay tres variantes: clara, oscura y banda del laboratorio.
- **Recursos de marca provisionales**, extraídos del mockup: logotipo ES/EN, compacto, isotipos N2/N3 (todos con su negativo), `favicon.ico` (16 y 32 px) y `apple-touch-icon`.
- **Publicaciones:** `papers.bib` copiado sin cambios (169 entradas) y listado mínimo con jekyll-scholar.
  - Año como `<h2>`, para que el orden de encabezados sea correcto.
  - BibTeX dentro de `<details>`.
  - Se excluyen `urldate`, `copyright`, `dimensions`, `altmetric`, `bibtex_show`, `abstract`, `keywords`, etc.
- **Muestras de colección** para validar las fichas: `_members/nestor-lucas-martinez.md` y `_projects/nextarc.md`. Solo llevan datos de la web anterior; lo que no consta queda vacío.
- **Scripts:**
  - `comprobar_datos.py`: YAML, rutas frente a páginas, claves i18n, redirecciones, colecciones, y bloques y filtros Liquid. Detecta también claves que YAML convierte en booleanos (`on`, `off`, `yes`, `no`).
  - `contraste.py`: AA de todos los pares de tokens en los dos temas.
  - `verificar_sitio.py`: comprobaciones sobre `_site`.
  - `descargar_fuentes.py`.
- **Workflows:**
  - `deploy.yml`: *push*, manual y diario a las 05:15 UTC.
  - `pr.yml`: compila y verifica cada PR y deja el sitio como artefacto.
  - La compilación falla si aparece cualquier aviso de Liquid, *Build Warning*, conflicto de destino o aviso del plugin.

### Comprobado en este entorno (sin Ruby ni Jekyll)
- `comprobar_datos.py`: 0 errores. Además lo he probado con 5 errores inyectados y los detecta todos.
- `contraste.py`: 35 pares, todos ≥ 4,5:1 (tras el ajuste del velo, ver abajo).
- `verificar_sitio.py`: probado sobre un `_site` simulado; detecta páginas que faltan, varios `h1` y enlaces rotos.
- Sintaxis de JS (`node --check`), de Python y de los YAML de los workflows.

### Conflicto resuelto a favor de la legibilidad
El token `--veil` del tema oscuro (`rgba(82,186,255,.14)`) dejaba el texto de acento en **4,49:1**, y en **3,99:1** dentro de los menús desplegables. Lo he cambiado por el opaco **`#324153`**, que da 4,85:1. Visualmente apenas cambia. Pendiente de validar (PENDIENTES B7).

### Ficheros (todos nuevos)
```
.github/workflows/deploy.yml  .github/workflows/pr.yml
.gitignore  .ruby-version  Gemfile  README.md  CHANGES.md  PENDIENTES.md
_config.yml  _config.staging.yml  404.html  sitemap.xml  robots.txt  favicon.ico
_data/routes.yml  _data/redirects.yml  _data/grupo.yml  _data/i18n/es.yml  _data/i18n/en.yml
_plugins/grys.rb
_layouts/{default,page,home,detail,redirect,bib}.html
_includes/{head,header,footer,pagehead,page-vars,logo,lang-switch,theme-toggle,icono}.html  _includes/iconos.svg
_pages/es/*.md (22)  _pages/en/*.md (22)
_members/nestor-lucas-martinez.md  _projects/nextarc.md
_bibliography/papers.bib            (copia literal del repositorio anterior)
assets/css/grys.css  assets/js/grys.js  assets/fonts/LEEME.md
assets/img/marca/ (10 logotipos/isotipos, 2 favicons, 3 tramas SVG)
scripts/{comprobar_datos,contraste,verificar_sitio,descargar_fuentes}.py
docs/COMPILAR.md
```
