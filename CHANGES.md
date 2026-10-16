# Registro de cambios

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
