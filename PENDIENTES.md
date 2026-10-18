# Pendientes

*Actualizado: fase 3, paso 3.6c (18-10-2026).* Marcas: 🔴 bloquea la publicación definitiva · 🟠 hay que revisarlo o decidirlo · 🔵 planificado para una fase posterior.

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
| B1 ✅ | *Hecho (rama `imagenes`).* **Migrar las imágenes**: `python scripts/migrar_imagenes.py RUTA/grys-upm.github.io` y subir `assets/img` y `assets/convocatorias` (docs/COMPILAR.md §1.7). Son 117 imágenes y 2 PDF; ocupaban 69,7 MB en origen y quedan en WebP |
| B2 ✅ | *Hecho: con la exportación del grupo (2021–2026) y la del IP (1997–2026) hay 25 publicaciones enlazadas al Portal y 115 al Archivo Digital. Los informes, con las publicaciones que están en un solo sitio y los duplicados del Portal, se generan con `scripts/cruce_portal.py` en `reports/cruce-portal.md`.* **Exportación del Portal Científico** (CSV o RIS de las publicaciones del grupo) para ejecutar `scripts/cruce_portal.py --fuente portal … --aplicar`. Igual con el Archivo Digital |
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
- **OpenTech Lab:** revisar la traducción del texto y las capacidades (`_data/laboratorio.yml`). Hace falta una **foto del laboratorio**: ahora la página usa el vídeo del Industry Day.
- **Demostradores** (`_data/demostradores.yml`): son los dos del Industry Day 2025. Para el de lenguaje natural falta imagen o vídeo; el de Smart Fleet Manager usa una foto de la noticia.
- 🔴 **SISS: asiento registral** del Registro de la Propiedad Intelectual (y fecha y registro territorial exactos) en `_data/transferencia.yml` → `proteccion`. Ahora sale «por completar» y `comprobar_datos` avisa. ¿El controlador de potencia de transmisión tiene algún tipo de protección?
- 🔴 **Privacidad:** el texto de `/privacidad/` hay que **validarlo con el Delegado de Protección de Datos de la UPM** (proteccion.datos@upm.es) antes de pasar a producción.
- **Accesibilidad:** la declaración dice «parcialmente conforme» (autoevaluación del 18-10-2026). En la fase 4 (revisión WCAG 2.2 AA) se actualizarán la lista de incumplimientos y `a11y_revision`. Hay que confirmar con la Unidad Responsable de Accesibilidad de la UPM si el sitio debe figurar en su inventario.
- **Prensa:** revisar las descripciones breve y larga del grupo (`_data/prensa.yml`). Faltan para el kit los **logotipos en SVG** y el **manual de identidad** en PDF (ver F).
- **Transferencia** (`_data/transferencia.yml`): confirmar las dos ofertas del mockup y, si se puede, añadir el **enlace directo** a la ficha del controlador de potencia en el HUB de Innovación (ahora enlaza al catálogo del grupo).
- **TFG, TFM y doctorado:** no hay temas publicados (`_data/estudiantes.yml` → `propuestas`); la página invita a proponer uno.
- **Docencia:** faltan las asignaturas (`_data/docencia.yml` → `asignaturas`). Mientras la lista esté vacía, esa sección no aparece.
- **ODS** (`_data/ods.yml`): hay que confirmar que los ODS 9 y 2 son los declarados en el HUB de Innovación UPM (dato del mockup) y revisar la asignación de proyectos a cada ODS (propuesta). Los textos en español son traducción de la web anterior.
- **Quiénes somos:** la traducción al español de la misión, la visión y la historia; los hitos de `_data/quienes_somos.yml` salen del mockup.
- **Contacto:** marcador del mapa en las coordenadas oficiales de la ETSIST (40.388895, -3.628677). ¿Conviene situarlo en el edificio exacto del despacho A9401?
- **Proyectos destacados:** son automáticos desde el 17-10-2026. Con los datos actuales salen AFarEdge, HumAMI y NexTArc, los tres en curso; los dos primeros **no tienen imagen ni descripción** (ver E), así que en la portada aparecen con el hueco gris. Mientras tanto se pueden fijar o excluir en `_data/portada.yml`.
- Portada (`_data/portada.yml`): los proyectos destacados (NexTArc, AFarCloud y SWARMs, como en el mockup), el texto y los puntos de la banda del OpenTech Lab y el vídeo (Industry Day 2025). El título «Cuatro ejes, once líneas» (`_data/i18n`, `home.research_title`) hay que cambiarlo a mano si cambian los ejes o las líneas.
- Ámbitos: textos (`_domains/`) y asignación a 12 proyectos (`domains`).
- Traducciones del mockup: puestos y roles (`_data/positions.yml`, `roles.yml`), 32 títulos de proyecto y 10 de noticia.
- Estado de los proyectos: se calcula con las fechas. A 16-10-2026 solo NexTArc está en curso; SIMGEOSEV terminó el 31-08-2026.

## E. Datos que faltan (resumen; detalle en el informe)

- **Proyectos (34)**: falta el programa en 21; el responsable de GRyS, en 26; el rol, en 32; los socios y el presupuesto, en todos; las líneas, en todos. HumAMI y AFarEdge no tienen descripción.
- **HumAMI**: el nombre del responsable en la UPM, que no es del grupo, va en el campo `pi_name`. Falta también el rol de GRyS.
- **Miembros**: las líneas de investigación, en todos; la foto de Alejandro Botas; ORCID y Scholar de Alejandro Botas y Xi Tao; el correo de Xi Tao; las biografías de Xi Tao y Sara Lana.
- **Noticias**: 6 títulos sin traducir; 2 imágenes y varias galerías sin texto alternativo.
- **Publicaciones**: 26 sin DOI. Solo 25 tienen `portal_upm`: las exportaciones del Portal no traen el ID de la mayoría (ver G). Ninguna tiene todavía `project` ni `lines` (`_bibliography/etiquetas.yml`).
- **Textos en español**: las biografías, las descripciones de proyecto, el texto largo de las líneas y las noticias solo existen en inglés. La web lo indica con un aviso y `lang="en"`.
- **Repositorios**: 3 sin lenguaje ni descripción.

## F. Recursos de marca (sin cambios desde la fase 1)

SVG oficiales del logotipo y del favicon · marca de la UPM para el pie · marca del OpenTech Lab · validación de `#52BAFF` y del velo `#324153` · `apple-touch-icon` de 180 px.

## G. Planificado

| Fase | Pendiente |
|---|---|
| 3 | Diseño de componentes, en pasos con una PR cada uno:<br>3.1 ✅ pestañas en Equipo y Tesis<br>3.2 ✅ tabla de Proyectos con filtros<br>3.3 ✅ Publicaciones: filtros e insignias oficiales de Altmetric y Dimensions<br>3.4 ✅ publicaciones en las fichas de proyecto, línea y miembro<br>3.5 ✅ portada completa<br>3.6a ✅ páginas de texto del menú Grupo (Quiénes somos, ODS, Contacto)<br>3.6b ✅ páginas de OpenTech Lab y Colabora (Laboratorio, Demostradores, Transferencia, Estudiantes, Docencia)<br>3.6c ✅ Prensa, Accesibilidad y Privacidad<br>3.7 buscador |
| 4 | Revisión del bilingüe y de la accesibilidad (WCAG 2.2 AA) |
| Más adelante | **Completar `portal_upm` consultando el Portal publicación a publicación por DOI**. Las exportaciones CSV solo traen el ID de la ficha en 25 de las 157 coincidencias. Un script consultaría el buscador del Portal por cada DOI del BibTeX y propondría el ID, con prueba en seco y `--aplicar` como `cruce_portal.py`. Antes hay que comprobar si el Portal tiene una API o permite búsquedas automatizadas (condiciones de uso) |
| 3.6 | **Política de privacidad** (`/privacidad/`): mencionar las insignias de Altmetric y Dimensions. Solo se cargan si el visitante pulsa «Mostrar métricas de impacto», y entonces su navegador se conecta con esos servicios; la preferencia se guarda en `localStorage` (`grys-metrics`), igual que el tema (`grys-theme`). No hay cookies propias |
| Más adelante | **Descarga del BibTeX completo** (botón «⤓ BibTeX» del mockup): generar al compilar un `.bib` público sin campos internos (los mismos que `bibtex_skip_fields`) |
| Último paso de la fase 3 | **Métricas de impacto: rediseño** (decisión del 17-10-2026). La solución del paso 3.3 (botón «Mostrar métricas de impacto» y las insignias oficiales de Altmetric y Dimensions junto a cada publicación) funciona, pero no encaja con el estilo. Se mantiene el criterio de no cargarlas por defecto. Opciones que hay que valorar: (a) cifras propias con el estilo del sitio (citas y menciones) obtenidas al compilar desde las API gratuitas de Dimensions y Altmetric, sin scripts externos para el visitante; (b) insignia solo en una vista de detalle de cada publicación; (c) solo los enlaces de texto actuales |
| Datos | **Etiquetar publicaciones** con `project` y `lines` en `_bibliography/etiquetas.yml`. Hasta entonces, las fichas de proyecto y de línea muestran «por completar» en «Publicaciones» y los filtros de proyecto y línea no aparecen |
| Datos | **Revisar la autoría calculada** (fichas de miembro y filtro «Autoría»): la detección es automática por nombre; si a alguien le faltan publicaciones porque firma de otra forma, añadir esas formas en `bib_names` de su ficha |
| Más adelante | **Estilo**: revisión de detalles visuales cuando haya contenido (decisión del 17-10-2026) |
| 5 | CMS, plantillas de *issue*, lychee, Lighthouse CI, vista previa por PR, sincronización semanal con Zotero (+ `aplicar_etiquetas.py`), Dependabot y documentación para editores |
