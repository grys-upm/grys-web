# Pendientes

*Actualizado: fase 1 (16-10-2026).* Marcas: 🔴 bloquea la publicación definitiva · 🟠 hay que revisarlo · 🔵 está planificado para una fase posterior.

## A. Comprobar en la primera compilación

Aquí no se ha podido ejecutar Ruby ni Jekyll, así que estos puntos hay que confirmarlos con el registro de Actions o con una compilación local.

| # | Qué comprobar | Cómo |
|---|---|---|
| A1 | Que compila sin errores ni avisos | Paso *Compilar* en verde |
| A2 | Que existen las 44 páginas (22 × ES/EN) y las redirecciones (27 de `redirects.yml` + 2 de las fichas de muestra) | Paso *Verificar el resultado* |
| A3 | Que las fichas de muestra salen en los dos idiomas | `/grupo/equipo/nestor-lucas-martinez/`, `/en/group/team/nestor-lucas-martinez/`, `/investigacion/proyectos/nextarc/`, `/en/research/projects/nextarc/` |
| A4 | Que el selector ES/EN lleva a la página equivalente y no a la misma | Clic en EN desde `/grupo/equipo/` → `/en/group/team/`, y vuelta |
| A5 | Que jekyll-scholar funciona en la pasada inglesa | En `/en/research/publications/` el botón debe decir «BibTeX», no «Cita BibTeX». Si sale en español, scholar no pasa `page` a la plantilla y lo corrijo en la fase 3 |
| A6 | Que el BibTeX publicado no lleva `urldate`, `copyright` ni `dimensions` | Abrir cualquier `<details>` en Publicaciones |
| A7 | Que las URL antiguas redirigen | `/team/`, `/research/areas/`, `/team/nestor-lucas-martinez/` |
| A8 | Que el tema oscuro sale por defecto, sin parpadeo, y que el claro se recuerda al recargar | Navegador |
| A9 | Que con el tema oscuro se ve el logotipo negativo y con el claro el de color, en cabecera y pie | Navegador |
| A10 | Que el sitio es usable sin JavaScript: los menús se abren con foco o ratón y el cajón móvil se ve | Desactivar JS en el navegador |
| A11 | Subir `Gemfile.lock` desde el artefacto de la primera compilación | Ver docs/COMPILAR.md §1.6 |

## B. Recursos de marca

| # | Pendiente | Situación actual |
|---|---|---|
| B1 🔴 | SVG oficiales del logotipo, en color y en negativo (carpeta `01_logotipo`) | Hay PNG provisionales extraídos del mockup en `assets/img/marca/` (640×208) |
| B2 🔴 | `favicon.svg` adaptativo y su `head.html` (carpeta `03_favicon`) | Hay `favicon.ico` (16 y 32 px) y PNG de 32 px. El SVG irá después del `.ico` en `_includes/head.html` |
| B3 🟠 | `apple-touch-icon` de 180×180 px | El provisional es de 128×128 (el del mockup); no se ha ampliado para no degradarlo |
| B4 🔴 | Marca institucional de la UPM para la cofirma del pie | Hay un hueco marcado de 156 px (0,81 × 192 px) en `_includes/footer.html` |
| B5 🟠 | Marca del OpenTech Lab con la paleta unificada (§15.5) | En la fase 3 |
| B6 🟠 | Validar el azul `#52BAFF` del modo oscuro | Es el token `--link`/`--accent` en `assets/css/grys.css` |
| B7 🟠 | **Validar el nuevo velo oscuro `#324153`** | Con `rgba(82,186,255,.14)`, el del mockup, el acento daba **4,49:1** sobre el velo y **3,99:1** dentro de los menús. Ahora da 4,85:1. Ha ganado la legibilidad |
| B8 🔵 | Fuentes en `assets/fonts/` | Las descarga Actions al compilar si no están. Opcional: subirlas al repositorio para no depender de esa descarga |

## C. Datos por confirmar

| # | Pendiente |
|---|---|
| C1 🟠 | **Dirección.** El mockup pone «despacho 9401» y la web anterior «Office A9401». He usado **A9401** |
| C2 🟠 | **LinkedIn.** La web anterior tenía `linkedin_username: grys-upm` (se construía como `/in/grys-upm`). ¿Es una página de empresa (`/company/grys-upm`)? |
| C3 🟠 | **Zotero.** Se enlaza a `https://www.zotero.org/groups/5287048/grys` |
| C4 🔵 | **Convocatoria HumAMI.** La fecha límite correcta es el **6 de agosto de 2026**; se corrige al migrarla en la fase 2 |
| C5 🟠 | **NexTArc.** Programa «Chips JU · Horizon Europe», 38 socios e IP en la UPM: Néstor Lucas. Lo he deducido de los textos de la web anterior; confírmalo |

## D. Propuestas que hay que revisar (marcadas en los datos)

- Agrupación de las 11 líneas en 4 ejes.
- Asignación de proyectos a ámbitos (NexTArc → ciudad, en la muestra).
- Estado de cada proyecto. Se calculará a partir de las fechas; hoy solo NexTArc está en curso.
- Traducción al español de los puestos.
- Título en español de NexTArc (sale del mockup).

## E. Planificado

| Fase | Pendiente |
|---|---|
| 2 | Migrar los 40 miembros, 32 proyectos, 16 noticias, 6 eventos y 4 convocatorias; las 11 líneas y los 5 ámbitos; `positions.yml`, `metrics.yml`, `repos.yml`; `theses.bib` unificado; esquemas JSON; informe automático de pendientes |
| 2 | Campos `portal_upm` y `archivo_upm` en el BibTeX; script de cruce BibTeX ↔ Portal Científico y Archivo Digital; métricas calculadas desde el BibTeX |
| 2 | Fotos: solo las que se usen, en WebP; el resto se archiva fuera del repositorio |
| 3 | Componentes Liquid (pub-item con DOI, Portal Científico, Archivo Digital, Altmetric, Dimensions y Google Scholar, con las insignias oficiales en JS; project-card, member-card, filtros, pestañas…), *layouts* específicos y buscador |
| 4 | Revisión completa del bilingüe y de la accesibilidad (WCAG 2.2 AA) |
| 5 | CMS, plantillas de *issue*, lychee, Lighthouse CI, vista previa por PR, Zotero semanal, Dependabot, `CONTRIBUTING.md`, `docs/EDITORES.md`, `docs/IDENTIDAD.md` |
