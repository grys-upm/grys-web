# Pendientes

*Actualizado: fase 2 (16-10-2026).* Marcas: 🔴 bloquea la publicación definitiva · 🟠 hay que revisarlo o decidirlo · 🔵 planificado para una fase posterior.

El detalle de los datos que faltan, elemento a elemento, lo genera `scripts/informe_pendientes.py` (`reports/pendientes-datos.md`). Ese informe también aparece en el resumen de cada ejecución de Actions. Lo que se decidió durante la migración está en `scripts/migracion/INFORME_MIGRACION.md`.

## A. Comprobar en la compilación de la fase 2

| # | Qué comprobar |
|---|---|
| A1 | Que compila sin errores ni avisos. Esta fase usa más Liquid y jekyll-scholar; si aparece un error, pega el registro |
| A2 | Que existen las fichas ES/EN: 40 miembros, 34 proyectos, 11 líneas y 8 noticias con página propia (las 8 breves no la tienen) |
| A3 | Tesis: que las tres consultas de jekyll-scholar (`@phdthesis`, `@mastersthesis`, `@thesis`) con `--group_by none` dan 14, 17 y 21 entradas |
| A4 | Que los recuentos calculados del BibTeX salen en Publicaciones (169) y Tesis (14/17/21) |
| A5 | Que las URL antiguas de fichas redirigen: `/team/jf/` → `/en/group/team/jose-fernan-martinez-ortega/`, `/research/projects/nextarc/`, `/news/2026-04-24-estela-professional-association-awards.html` |
| A6 | Que Equipo, Proyectos, Líneas, Ámbitos, Noticias, Eventos, Convocatorias (bloque vacío) y Software muestran los datos |

## B. Para ti (una sola vez)

| # | Pendiente |
|---|---|
| B1 🔴 | **Migrar las imágenes**: `python scripts/migrar_imagenes.py RUTA/grys-upm.github.io` y subir `assets/img` y `assets/convocatorias` (docs/COMPILAR.md §1.7). Son 117 imágenes y 2 PDF; ocupaban 69,7 MB en origen y quedan en WebP |
| B2 🟠 | **Exportación del Portal Científico** (CSV o RIS de las publicaciones del grupo) para ejecutar `scripts/cruce_portal.py --fuente portal … --aplicar`. Igual con el Archivo Digital |
| B3 🟠 | **Idioma por defecto**: ver la nota de la respuesta de esta fase |

## C. Datos contradictorios o dudosos del origen (decidir)

| # | Pendiente |
|---|---|
| C1 🟠 | **SWARMs**: termina el 2018-06-30 según el *front matter* y el 2018-07-31 según la tabla. Se ha usado la primera |
| C2 🟠 | **WoO**: termina el 2013-01-12 según el *front matter* y el 2013-12-31 según la tabla. Parece una errata; se ha usado la primera |
| C3 🟠 | **SIMGEOSEV**: el responsable en la UPM es María Castro Malpica (ICID-UPM). ¿Qué rol tiene GRyS? El rol está sin asignar |
| C4 🟠 | **AFarEdge**: el plazo de la convocatoria es el 5 de agosto en el campo y en el texto, y el 6 en el título. Se ha mantenido el 5; ¿debería ser el 6, como en HumAMI? |
| C5 🟠 | **Convocatoria NexTArc (2025)**: el título dice 23:00 y el campo, 11:00 |
| C6 🟠 | **Rol «partner» de NexTArc**: se ha deducido de «Coordinated by: Mälardalen University» |
| C7 🟠 | **Tipos de evento**: `tech_hub`, `industry_day` y `upm_investiga` pasan a `fair`; `award_ceremony`, a `award`; `honored_guest`, a `guest` |
| C8 🟠 | **PDF que no existen** en el repositorio antiguo: las ofertas de 2025 (beca IA-edge y NexTArc). Ya estaban rotos en la web anterior |
| C9 🟠 | **Imágenes de financiación** de ACCUS y SWARMs: la ruta apuntaba a ficheros que no existen (`accus/ACCUSFunding.png`, `accus/SWARMsFunding.png`). Ya estaban rotas |
| C10 🟠 | **Citas rotas** en DEMANES (4 claves) y WoO (2): las claves no están en el BibTeX. Se han marcado con «por completar» |

## D. Propuestas que hay que revisar (marcadas en los ficheros)

- Ejes de las líneas (`_data/axes.yml`) y la asignación de cada línea a un eje.
- Ámbitos: textos (`_domains/`) y asignación a 12 proyectos (`domains`).
- Traducciones del mockup: puestos y roles (`_data/positions.yml`, `roles.yml`), 32 títulos de proyecto y 10 de noticia.
- Estado de los proyectos: se calcula con las fechas. A 16-10-2026 solo NexTArc está en curso; SIMGEOSEV terminó el 31-08-2026.

## E. Datos que faltan (resumen; detalle en el informe)

- **Proyectos (34)**: falta el programa en 21; el responsable de GRyS, en 26; el rol, en 32; los socios y el presupuesto, en todos; las líneas, en todos. HumAMI y AFarEdge no tienen descripción.
- **HumAMI**: el nombre del responsable en la UPM, que no es del grupo, va en el campo `pi_name`. Falta también el rol de GRyS.
- **Miembros**: las líneas de investigación, en todos; la foto de Alejandro Botas; ORCID y Scholar de Alejandro Botas y Xi Tao; el correo de Xi Tao; las biografías de Xi Tao y Sara Lana.
- **Noticias**: 6 títulos sin traducir; 2 imágenes y varias galerías sin texto alternativo.
- **Publicaciones**: 26 sin DOI. Ninguna tiene todavía `portal_upm` ni `project` (`_bibliography/etiquetas.yml`).
- **Textos en español**: las biografías, las descripciones de proyecto, el texto largo de las líneas y las noticias solo existen en inglés. La web lo indica con un aviso y `lang="en"`.
- **Repositorios**: 3 sin lenguaje ni descripción.

## F. Recursos de marca (sin cambios desde la fase 1)

SVG oficiales del logotipo y del favicon · marca de la UPM para el pie · marca del OpenTech Lab · validación de `#52BAFF` y del velo `#324153` · `apple-touch-icon` de 180 px.

## G. Planificado

| Fase | Pendiente |
|---|---|
| 3 | Diseño de componentes: pestañas en Equipo y Tesis, filtros en Proyectos y Publicaciones, insignias oficiales de Altmetric y Dimensions, publicaciones por proyecto y por línea, buscador, portada completa y páginas de texto (Quiénes somos, ODS, Contacto, Laboratorio, Transferencia, Docencia…) |
| 4 | Revisión del bilingüe y de la accesibilidad (WCAG 2.2 AA) |
| 5 | CMS, plantillas de *issue*, lychee, Lighthouse CI, vista previa por PR, sincronización semanal con Zotero (+ `aplicar_etiquetas.py`), Dependabot y documentación para editores |
