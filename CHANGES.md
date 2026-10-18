# Registro de cambios

## Fase 5 · Paso 5.4: formularios de issue que generan la PR (18-10-2026)

- **5 formularios** en *New issue*: Noticia, Evento, Convocatoria, Miembro y Proyecto. Los genera `scripts/issue_a_contenido.py --plantillas`; los puestos, líneas y ámbitos salen de los datos, y `comprobar_datos.py` avisa si quedan desfasados. Hay además enlaces al gestor y a la guía.
- **`issue-a-pr.yml`:**
  - **Permisos:** si quien abre la issue puede escribir en el repositorio, o alguien con permiso añade la etiqueta `generar-pr`, se crea el fichero.
  - **Ficheros:** el nombre sigue las reglas del sitio. Las fechas aceptan AAAA-MM-DD o DD/MM/AAAA, el plazo de las convocatorias se fija a las 23:59 de Madrid y del ORCID o de Google Scholar se aprovecha la URL completa.
  - **Relaciones:** el IP se busca por nombre entre los miembros y el proyecto por acrónimo.
  - **Adjuntos:** las imágenes se descargan a WebP (máx. 1600 px); en las noticias, la primera es la de la tarjeta y el resto forman una galería con sus descripciones. Las imágenes dentro del texto pasan a `figura.html` y el PDF de la convocatoria se descarga.
  - **Validación:** `comprobar_datos.py` revisa los datos y se abre o actualiza la PR `contenido/issue-N`, que cierra la issue al fusionarse. Los errores se contestan en un único comentario de la issue que se actualiza.
  - **Edición:** editar la issue rehace la propuesta, y si el contenido no cambia, no se vuelve a subir.
  - **Seguridad:** el texto de la issue solo llega al script por variable de entorno, nunca al intérprete de órdenes.
  - **Comprobaciones de la PR:** se lanzan solas con la aplicación opcional `grys-web-contenido`; sin ella, la PR pide cerrarla y reabrirla una vez.
- Documentación: `docs/EDITAR.md` §5 y `docs/COMPILAR.md` §9.

## Fase 5 · Paso 5.3: gestor de contenidos (18-10-2026)

- **Sveltia CMS en `/admin/`** para Noticias, Eventos, Convocatorias, Miembros y Proyectos. Solo pueden guardar quienes tengan permiso de escritura en el repositorio (equipo `web` de la organización).
- **Flujo editorial:** cada cambio se guarda en una PR (rama `cms/…`) que pasa «Comprobar PR» y tiene vista previa. «Publicar» la fusiona con *squash*, o la deja en fusión automática si las comprobaciones siguen en marcha. No hace falta saber Git.
- **`admin/config.yml` es una plantilla de Jekyll:**
  - las opciones (puestos, roles, líneas, ámbitos, repositorios) salen de `_data/` y de las colecciones;
  - los proyectos, miembros y noticias relacionados se eligen de listas;
  - las imágenes se convierten a WebP (máx. 1600 px);
  - hay botones «Imagen con pie» y «Vídeo de YouTube» que generan los `{% include %}`;
  - los campos opcionales vacíos no se escriben.
- **Comprobaciones:**
  - `comprobar_datos.py` exige que el gestor tenga todos los campos de cada esquema (si no, los borraría al guardar), que no tenga campos ajenos y que sus opciones fijas coincidan con los esquemas;
  - `verificar_sitio.py` comprueba que la plantilla genera un YAML válido, con las 5 colecciones y listas de opciones no vacías, y que no se duplica en `/en/`;
  - el gestor queda fuera de las comprobaciones del sitio público (meta `grys-herramienta`) y de `robots.txt`.
- **Vista previa:** el job «Vista previa» pone en el commit el estado `vista-previa` con su dirección, para que el gestor la enlace.
- **Documentación:**
  - guía para editores en `docs/EDITAR.md`;
  - puesta en marcha en `docs/COMPILAR.md` §8: equipo `web`, *auto-merge*, autenticador OAuth en Cloudflare y prueba.
- **Corrección:** con `cms.oauth_url` vacío, el gestor recibía `base_url: ""` y no arrancaba («must be an absolute URL»). En Liquid una cadena vacía cuenta como verdadera; ahora se comprueba que no esté vacía, y `verificar_sitio.py` da error si `base_url` no es una URL absoluta.
- `schemas/members.schema.json`: añadido `pteu` a la lista de puestos (la validación real ya la tomaba de `_data/positions.yml`).

## Fase 5 · Paso 5.2: enlaces (lychee) y Lighthouse CI (18-10-2026)

- **Enlaces nuevos** (job `enlaces` en `pr.yml`): lychee comprueba solo las URL externas añadidas en la PR. Es informativo.
- **Enlaces externos** (`enlaces.yml`): todo el sitio cada lunes y a mano. Abre, actualiza o cierra la issue «Enlaces rotos».
- **`lychee.toml`:**
  - solo comprueba http y https, con caché de 3 días entre ejecuciones;
  - excluye el propio dominio, los DOI, los sitios que bloquean robots (LinkedIn, Google Scholar, ResearchGate, ACM, IEEE…), archive.org y los incrustados.
- **Lighthouse CI** (job `lighthouse` en `pr.yml`, `lighthouserc.json`):
  - 8 páginas representativas, mediana de 3 ejecuciones;
  - error si accesibilidad < 95 o SEO < 90; aviso si rendimiento < 80 o buenas prácticas < 90;
  - se omite la auditoría `is-crawlable`, porque el sitio de pruebas lleva `noindex`;
  - tabla de puntuaciones en el resumen y los informes como artefacto, sin subirlos a servidores de Google.

  Es informativo.
- Las comprobaciones informativas están explicadas en `docs/COMPILAR.md` §3.
- **Corrección:** la primera ejecución de «Enlaces nuevos» comprobó las direcciones `http://localhost/…` de `lighthouserc.json`, que solo existen dentro de Lighthouse. Ahora se excluyen las direcciones locales y los ficheros de configuración de las comprobaciones.

## Fase 5 · Paso 5.1: vista previa de cada PR y Dependabot (18-10-2026)

- **Vista previa por PR:**
  - nuevo job `preview` en `pr.yml`: compila con la ruta `/grys-web-previews/pr-N/`, lo publica en el repositorio `grys-upm/grys-web-previews` (`scripts/vista_previa.sh`) y deja o actualiza un comentario con el enlace en la PR;
  - la página lleva la franja «Vista previa de la propuesta de cambios n.º N»;
  - `vista-previa-borrar.yml` la borra al cerrar la PR, y a mano borra las de todas las PR cerradas;
  - el repositorio de vistas previas guarda un solo commit, para que no crezca;
  - no bloquea la PR y, sin configurar, solo deja un aviso.

  Configuración en `docs/COMPILAR.md`, apartado 5.
- **Dependabot** (`.github/dependabot.yml`): acciones, gemas (sin versiones mayores) y paquetes de la auditoría, una vez al mes y agrupados.

## Fase 4 · Paso 4.4: teclado, revisión manual y declaración (18-10-2026)

- **Auditoría de teclado automática** en `auditar.mjs`. Recorre con el tabulador una página de cada plantilla (las de primer y segundo nivel, la ficha más grande de cada tipo y la portada en inglés) a 1280×900 y a 320×256 (zoom del 400 %). Comprueba:
  - enlace «Saltar al contenido» (2.4.1);
  - foco visible (2.4.7);
  - foco no tapado por la cabecera fija (2.4.11);
  - trampas de teclado (2.1.2).

  Es bloqueante, como el resto, y los hallazgos salen en el registro como `TECLADO …`.
  - **Corrección:** la primera ejecución dio 4 «foco invisible» en elementos al azar (el mismo enlace pasaba en otras páginas). Con 4 pestañas en paralelo, solo la que está al frente tiene el foco real. Las pasadas de teclado van ahora en serie, con la pestaña al frente, y el foco se vuelve a medir tras dos fotogramas antes de darlo por invisible.
- **Foco no tapado (2.4.11):** `scroll-padding-top` con la altura de la cabecera fija. Con menos de 500 px de alto útil la cabecera deja de ser fija.
- **Revisión manual:** nueva lista `docs/REVISION_ACCESIBILIDAD.md` (teclado, lector de pantalla, zoom, colores forzados, WCAG 2.2, contenido) con plantilla de resultados para una *issue*.
- **Declaración de accesibilidad (ES/EN):**
  - se quita «textos solo en inglés» de la falta de conformidad (ya hay traducción de todo);
  - se explican las traducciones provisionales y la cabecera;
  - se describen las auditorías reales.

## Fase 4 · Paso 4.3d: noticias en español (18-10-2026)

- **Borradores en español** (`texto_es`, `traduccion: borrador`) de las 8 noticias con texto; las demás solo tienen título, que ya estaba en los dos idiomas. Con esto, ningún texto se muestra solo en inglés en la versión española.
- **Inglés corregido**: primera persona en textos del grupo («recognition of my effort», «presents me»), atributo `alt` en enlaces (no válido), `<figure>` con estilos en línea en Industry Day, pie del vídeo de 2026 que decía 2023 (PENDIENTES C20). Los vídeos tienen título propio en cada idioma.
- **Proyectos**: SWARMs con la referencia nacional PCIN-2014-022-C02-02; los dos análisis de vulnerabilidades para Defensa pasan a `private`.

## Fase 4 · Paso 4.3c: textos de proyectos en español (18-10-2026)

- **Borradores en español** (`texto_es`, `traduccion: borrador`) de los 32 proyectos con texto.
- **20 proyectos antiguos** (AWARE, CI-RTI, Análisis de vulnerabilidades ×2, DISP-GW, DISP-J, EXHAUSTIF, I3RES, LifeWear, MIRACLE, Periféricos, PSAV-TIC, RIMSI, SCOS, SECUAREA, SODA, SSBJP, TAPS, TIC-Spaces, uSWN) tenían como texto un volcado de la web antigua («Organization: … Program: … PI: … DOI:»), que se veía como un único párrafo. Esos datos pasan a la cabecera y se ven en la ficha técnica en los dos idiomas:
  - `funder`, `funding`, `programme`, `call`, `grant_ids`;
  - `pi` (miembros: José-Fernán Martínez, Ana Belén García, Lourdes López, Antonio Da Silva, Vicente Hernández) o `pi_name` (CI-RTI: Enrique Alba, U. Málaga);
  - enlaces de LifeWear.
  El texto queda en una frase de financiación.
- **Inglés corregido** donde hacía falta: «recived», párrafo anidado en WoO, apartados vacíos, primera persona, textos alternativos de logotipos. Detalle en PENDIENTES C19.
- Los vídeos de DEMANES y WoO tienen título propio en cada idioma (`titulo=`), que es el nombre accesible del reproductor.

## Fase 4 · Paso 4.3b: biografías en español y anclas de las citas (18-10-2026)

- **Corrección:** el enlace de una cita a una tesis (p. ej., el TFM en DEMANES) abría Tesis, pero no la pestaña ni la entrada. jekyll-scholar solo pone `id` en su propio `<span>`, que la plantilla `_layouts/bib.html` no usa. Ahora cada entrada lleva `<h3 id="ref-<clave>">` (clave en ASCII), `cita.html` enlaza a `#ref-<clave>`, la cabecera fija no tapa el destino y la entrada se resalta. `verificar_sitio.py` comprueba que toda cita con ancla llega a un `id` existente.
- **Biografías:** borradores en español (`texto_es`, `traduccion: borrador`) de los 14 miembros con texto. Erratas corregidas en el inglés de Alejandro Botas y Estela Mora («an Predoctoral», «bachelo», «Things.s»).
- **Nuevo puesto `ppl`** (Profesor/a Permanente Laboral · Associate Professor), asignado a Néstor Lucas. Los puestos válidos se toman ahora de `_data/positions.yml`: para añadir uno basta con escribirlo allí.
- Dudas de datos detectadas al traducir: PENDIENTES C11–C14, ya resueltas: Yiting `gender: f`; nuevo puesto `pteu` (Gregorio, Vicente); Santiago `ppl`; ACCUS y Horizon Europe en la biografía de Néstor.
- **Corrección (ids repetidos):** dos claves BibTeX que solo se distinguen por una tilde (`martínez…`/`martinez…ModellingQoSWireless2007`) daban la misma ancla. El ancla la calcula ahora `bib_index.rb` y es siempre única; `comprobar_datos` avisa de claves que solo difieren en mayúsculas o tildes y de DOI repetidos (PENDIENTES C15).

## Fase 4 · Paso 4.3a: mecanismo bilingüe y citas (20-10-2026)

- **Traducciones del texto principal:** campos `texto_es` / `texto_en` y `traduccion` (`borrador` / `revisada`) en miembros, proyectos, líneas y noticias. Si existe la traducción, la página la muestra en lugar del texto original; si es borrador, con el aviso «Traducción provisional…». Receta en `docs/RECETAS.md`.
- **Primer lote de borradores:** texto en español de las 11 líneas de investigación; `title_es` de 6 noticias y de los proyectos AFarEdge y HumAMI.
- **Citas en los textos:** nuevo `_includes/cita.html` («Autor et al. (año)», enlazado a Publicaciones filtradas o a la tesis). Sustituye las claves rotas de DEMANES y WoO (salvo `HernandezDiaz2015`, sin candidato).
- **Comprobaciones nuevas:** cita a una clave inexistente (error); `texto_X` en el mismo idioma que el cuerpo (error); traducción con distintos `include` que el original (aviso). El informe de pendientes separa «texto solo en inglés» de «traducción en borrador».

## Fase 4 · Paso 4.2: correcciones de la auditoría y auditoría bloqueante (18-10-2026)

Resultado de la primera auditoría (paso 4.1, 231 páginas × 3 pasadas):
- **1 regla WCAG incumplida**: `link-name`, en 20 páginas y 136 elementos;
- **reflow a 320 px en las 231 páginas**;
- **0 errores de JavaScript**;
- **87 hallazgos estáticos.**

Correcciones:
- **Enlaces sin nombre (WCAG 2.4.4 y 4.1.2):**
  - **Vídeos:** el enlace «Ver en YouTube» salía vacío en el texto de noticias y proyectos, porque la variable `lang` del layout no existe al renderizar el contenido. `video.html` calcula ahora el idioma por su cuenta y añade el título del vídeo para lectores de pantalla.
  - **Galerías:** las fotos sin texto alternativo dejaban el enlace a la imagen grande sin nombre. Ahora llevan `aria-label` («Foto 2 de 4, a tamaño completo»); la falta de `alts` sigue en el informe de pendientes.
- **Reflow a 320 px (WCAG 1.4.10):**
  - la cabecera (logotipo y botones) medía 358 px: por debajo de 400 px el logotipo pasa a 148 px y se reducen márgenes y separaciones;
  - en las fichas, las columnas de la rejilla no podían estrecharse por debajo de su contenido (`min-width:0`), y las URL y palabras largas no se partían (`overflow-wrap`);
  - las fichas de ámbito y los grupos de botones de filtro («Todas · Revistas · Congresos · Libros y capítulos») ahora pasan a la línea siguiente.
  - las URL largas de la ficha lateral y del texto se parten (ficha de María Nieves Plaza: 870 px), y las marcas «por completar» con texto largo, como las claves de cita de DEMANES y WoO, ya pueden pasar a la línea siguiente;
  - el detalle de lo que falla (WCAG, reflow, JS) se escribe también en el registro de Actions, no solo en el resumen.
- **Saltos de encabezado (WCAG 1.3.1):**
  - página Noticias: los títulos pasan a `h2`, con el parámetro `h` en `listas/noticias.html`; en la portada siguen siendo `h3` bajo su `h2`;
  - Demostradores: las tarjetas pasan a `h2`;
  - Software: nuevo `h2` «Repositorios»;
  - bloques «sin convocatorias» y «sin resultados»: `h2`;
  - SIMGEOSEV: `###` → `##`.
- **Textos en el otro idioma (WCAG 3.1.2):**
  - la fuente de las métricas (`_data/metrics.yml` → `source`) es ahora bilingüe: «Portal Científico UPM» / «UPM Scientific Portal»;
  - «Archivo Digital UPM» dentro de una noticia en inglés va marcado con `lang="es"`.
- **Barra superior** (institución, Contacto, tema, idioma): pasa a ser `<nav aria-label="Accesos rápidos">`, para que todo el contenido esté en una región (buena práctica `region`).
- **Prevención:**
  - `comprobar_datos.py` da error si el texto de un elemento usa `#` (nivel 1) o salta niveles de encabezado; se ha probado con el caso de SIMGEOSEV;
  - `a11y_estatico.py` no revisa lo que está oculto (`hidden`: diálogo del buscador, filtros sin JavaScript), igual que axe, y cuenta las páginas sin repetir.
  - **Corrección dentro del paso:** la primera versión trataba `hidden` como `aria-hidden` y descartaba también el texto de los botones ocultos, lo que daba 604 falsos «sin nombre» («Buscar», «Cerrar», botones de filtro). Ahora `aria-hidden` solo excluye ese texto del nombre (iconos) y `hidden` hace que el elemento no se compruebe. Se ha probado con 5 casos: 2 problemas reales detectados y 0 falsos positivos.
- **`pr.yml`: auditoría BLOQUEANTE** (`--estricto` en los dos scripts). El informe se publica aunque falle.
- **`docs/ACCESIBILIDAD.md`:** qué hacer si una PR falla por accesibilidad.

## Fase 4 · Paso 4.1: auditoría automática de accesibilidad (18-10-2026)

- **`scripts/a11y/auditar.mjs`** (nuevo, con su `package.json`): auditoría con navegador real (Chrome sin ventana + axe-core) de **todas las páginas ES/EN**, salvo las redirecciones. Hace tres pasadas por página:
  - **tema oscuro** y **tema claro** a 1280 px, con todas las reglas automáticas de WCAG 2.0/2.1/2.2 A y AA, más las buenas prácticas, que se informan aparte;
  - **reflow a 320 px** (WCAG 1.4.10), que busca desplazamiento horizontal y señala los elementos que se salen;
  - además, en todas las pasadas, los **errores de JavaScript**.
  
  Solo carga recursos del propio sitio (los de terceros se bloquean), así que el resultado es repetible. Informe en `reports/a11y/axe.md` y `.json`, agrupado por regla, con impacto, criterio WCAG, páginas afectadas y ejemplos. Se ha probado de principio a fin con un navegador simulado.
- **`scripts/a11y_estatico.py`** (nuevo): 9 comprobaciones sin navegador:
  - ids repetidos y referencias `aria-*`/`for`/anclas rotas;
  - imágenes sin `alt` e iframes sin `title`;
  - saltos de encabezado;
  - enlaces y botones sin nombre accesible;
  - `lang` no válido;
  - selector de idioma que no lleva al idioma anunciado;
  - **textos de interfaz de `es.yml` que aparecen en páginas en inglés** (o al revés).
  
  Se ha probado con una página con un caso de cada: detecta los 9 sin falsos positivos.
- **`pr.yml`:** ejecuta las dos auditorías después de compilar, publica los informes en el resumen y en el artefacto `informe-accesibilidad`. **De momento solo informan**: no bloquean la PR.
- **`docs/ACCESIBILIDAD.md`** (nuevo): qué se revisa, cómo leer los informes y cómo ejecutarlos en local. **`.gitignore`:** `scripts/a11y/node_modules/` y su `package-lock.json`.
- **PENDIENTES.md:** plan de la fase 4 (4.1 a 4.4).

## Fase 3 · Paso final: métricas de impacto (A + B) (18-10-2026)

- **Citas como fichas del sitio** (opción A):
  - en cada publicación con citas: «14 citas», que enlaza a su ficha en Dimensions, y el *Field Citation Ratio* («FCR 1,8», con su explicación para lectores de pantalla);
  - en la cabecera de Publicaciones, el total de citas;
  - **la atribución que exigen las condiciones de Dimensions** al final de la página, con la fecha de actualización.
  
  Si no hay citas, no se muestra nada (nunca «0»).
- **«Más métricas»** (opción B): desplegable en cada publicación con DOI.
  - Al abrirlo, se cargan las insignias oficiales de Altmetric y Dimensions **solo de esa publicación**.
  - Los marcadores llegan con clases «pendientes» para que los scripts externos no pidan las 169 insignias al cargarse.
  - Incluye los enlaces de texto a las páginas de detalle, que funcionan sin JavaScript.
- **Desaparecen** el botón general «Mostrar métricas de impacto» y la preferencia `grys-metrics` del navegador.
- **`scripts/metricas_dimensions.py`** (nuevo) consulta la Dimensions Metrics API por DOI y escribe `_data/metricas_pubs.yml` (esquema nuevo). Funcionamiento:
  - solo consulta si los datos tienen más de N días o con `--forzar`;
  - si hay DOI nuevos, pide solo esos;
  - **nunca rompe la compilación**: si la API falla, conserva los datos anteriores.
  
  Se ha probado con una API simulada (8 casos).
- **`deploy.yml`:**
  - recupera las métricas de la caché, las actualiza si toca (`METRICAS_MAX_EDAD: 7`) y las vuelve a guardar;
  - *Run workflow* tiene la casilla **«Actualizar ya las métricas»**.
  
  `pr.yml` usa las últimas métricas guardadas, sin consultar la API.
- **Privacidad (ES/EN):** queda una sola preferencia guardada (`grys-theme`). Las insignias se cargan solo al abrir «Más métricas», y las cifras de citas se obtienen al compilar, sin conexión del visitante con Dimensions.
- **`verificar_sitio.py`:**
  - da error si alguna insignia llega con su clase oficial en el HTML, porque provocaría la carga masiva;
  - da error si se muestran citas sin la atribución a Dimensions.
- **Icono nuevo** `cita`. **`docs/RECETAS.md`:** cómo actualizar las métricas a mano.

## Fase 3 · Paso 3.7: buscador; corrección de la protección de resultados (18-10-2026)

- **Buscador** (como en el mockup): botón «Buscar» en la cabecera y atajo de teclado `/`.
  - **Índice:** se genera al compilar, uno por idioma (`/indice-busqueda.json` y `/en/indice-busqueda.json`, desde `_includes/indice-busqueda.json`). Contiene secciones, proyectos, personas, líneas, ámbitos, demostradores, noticias, eventos, repositorios y las 169 publicaciones; las publicaciones abren Publicaciones con `?q=` (DOI o título).
  - **Descarga y privacidad:** el índice se descarga la primera vez que se abre el buscador, y la búsqueda se hace en el navegador, sin enviar nada a ningún servidor.
  - **Cómo busca:** sin mayúsculas ni tildes; todas las palabras deben aparecer. Ordena primero los títulos que empiezan por la consulta y después por tipo. Muestra hasta 20 resultados con su tipo (Proyecto, Persona…) y anuncia el recuento a los lectores de pantalla.
  - **Accesibilidad:** diálogo modal (`role="dialog"`, `aria-modal`) con el foco atrapado; Esc cierra; ↑/↓ recorren los resultados; al cerrar, el foco vuelve a donde estaba.
  - **Sin JavaScript** no aparece ni el botón ni el diálogo.
  - **Prueba:** el JS se ha probado con un DOM simulado (13 casos).
- **`verificar_sitio.py`** comprueba ahora que los dos índices:
  - son JSON válido y están en su idioma;
  - tienen todos los tipos de contenido y los 34 proyectos;
  - **no tienen ninguna URL rota**.
  
  También comprueba que toda página con botón tiene el diálogo.
- **Privacidad:** una frase sobre el buscador («lo que escribes no se envía a ningún servidor»).
- **Corrección: protección de resultados.** Un programa puede estar inscrito en el Registro de la Propiedad Intelectual **y además** ser código abierto, así que son dos datos independientes:
  - `proteccion` es ahora una **lista** de títulos (registro de PI, patente, modelo de utilidad o secreto industrial), porque un resultado puede tener varios;
  - `licencia` (SPDX) va aparte, en la oferta. Si no se indica, se toma la del repositorio, y enlaza a spdx.org.
  
  Se elimina el tipo «código abierto» de `proteccion`. SISS queda con su registro de PI y la licencia pendientes, y `comprobar_datos` avisa de las dos.

## Fase 3 · Paso 3.6c: Prensa, Accesibilidad y Privacidad; protección de resultados (18-10-2026)

- **Transferencia: protección de cada resultado.** Campo nuevo `proteccion` en las ofertas (`_data/transferencia.yml`, con esquema): `tipo` (registro de PI, patente, modelo de utilidad, secreto industrial o código abierto), `numero` (asiento registral o nº de publicación), `oficina`, `fecha`, `titulares`, `url` y `licencia`.
  - La tarjeta lo muestra como ficha.
  - En patentes y modelos de utilidad sin `url`, el número enlaza a su búsqueda en Espacenet.
  - SISS queda como registro de PI **sin asiento**: sale «por completar» y `comprobar_datos` avisa.
- **Prensa** (`_data/prensa.yml`, con esquema):
  - apariciones en medios, ordenadas por fecha, con bloque vacío si no hay;
  - kit de prensa con los 6 logotipos PNG que existen;
  - descripciones breve (~50 palabras) y larga (~150) en ES/EN;
  - contacto de prensa.
  
  `comprobar_datos.py` comprueba que los ficheros del kit existen y avisa si las descripciones se salen de longitud.
- **Accesibilidad:** declaración según el RD 1112/2018:
  - situación de cumplimiento («parcialmente conforme»);
  - contenido no accesible y contenido excluido;
  - medidas adoptadas;
  - preparación (autoevaluación, 18-10-2026; fechas en el *front matter*);
  - contacto;
  - procedimiento de reclamación ante la Unidad Responsable de Accesibilidad de la UPM.
- **Privacidad:**
  - sin cookies ni analítica;
  - las 2 claves de `localStorage` (`grys-theme` y `grys-metrics`);
  - alojamiento en GitHub Pages;
  - terceros: YouTube sin cookies, OpenStreetMap y Altmetric/Dimensions solo bajo demanda;
  - datos de quien nos escribe: la UPM como responsable, con el DPD (proteccion.datos@upm.es) y la AEPD.
- **`verificar_sitio.py`:**
  - comprueba Prensa, Accesibilidad y Privacidad (ES/EN);
  - **comprueba que la política de privacidad sigue al día**: si el sitio empieza a usar otra clave de `localStorage` o a cargar otro servicio externo (en `iframe`, `script` o desde `grys.js`) sin explicarlo en Privacidad, la compilación falla.
- **`docs/RECETAS.md`:** recetas para indicar la protección de un resultado, añadir apariciones en prensa y mantener la privacidad.

## Fase 3 · Paso 3.6b: OpenTech Lab y Colabora (17-10-2026)

- **El laboratorio:**
  - texto (ES/EN) en Markdown en la página;
  - 6 capacidades en `_data/laboratorio.yml`;
  - el vídeo del Industry Day, el mismo de la portada;
  - botones «Proponer una colaboración» y «Ver demostradores».
- **Demostradores:** tarjetas desde `_data/demostradores.yml` (Smart Fleet Manager y la consulta en lenguaje natural), con autoría enlazada a la ficha, ámbitos, repositorio y dónde se presentaron.
- **Transferencia:** oferta tecnológica y formas de colaborar desde `_data/transferencia.yml`, con enlace al catálogo del grupo en el HUB de Innovación UPM.
- **TFG, TFM y doctorado:**
  - cifras de `metrics.yml`;
  - temas abiertos de `_data/estudiantes.yml`; si no hay ninguno, un bloque que invita a proponer uno;
  - tres pasos para empezar.
- **Docencia:** objetivos y, si las hay, tabla de asignaturas (`_data/docencia.yml`). **Sin «próximamente»:** la sección de asignaturas no aparece mientras la lista esté vacía.
- **5 esquemas nuevos.** `comprobar_datos.py` valida las personas, repositorios, ámbitos e iconos citados. Se ha probado con datos erróneos: detecta los 5 tipos de error.
- **`verificar_sitio.py`** comprueba ahora:
  - estas 10 páginas (ES/EN);
  - que el nº de capacidades y de demostradores coincide con los datos;
  - que ninguna página migrada dice «próximamente» ni «coming soon».
- **`docs/RECETAS.md`:** recetas para añadir temas de TFG/TFM, asignaturas, demostradores y ofertas.

## Proyectos destacados automáticos (17-10-2026)

- **`_plugins/destacados.rb`** (nuevo) elige los proyectos destacados de la portada en cada compilación:
  1. primero, los **en curso**, del más reciente al más antiguo por fecha de inicio;
  2. después, el resto por fecha de fin, del más reciente al más antiguo;
  
  con empates resueltos por acrónimo. El resultado queda en `site.data.destacados`.
- **Decisión manual opcional** en `_data/portada.yml` → `destacados`: `numero`, `fijos` (siempre primero y en ese orden) y `excluir`. El esquema y `comprobar_datos.py` validan que los slugs existen y que ninguno está en las dos listas.
- **`verificar_sitio.py`** replica la regla y comprueba que la portada muestra exactamente los proyectos esperados y en ese orden.
- **`docs/RECETAS.md`** actualizado.

## Fase 3 · Paso 3.6a: páginas del menú Grupo y ámbitos/líneas sin listas fijas (17-10-2026)

- **Quiénes somos:**
  - el texto corrido en Markdown (ES y EN) dentro de la propia página, entre `capture texto` y `endcapture`;
  - foto, valores e historia en `_data/quienes_somos.yml`, nuevo y validado con su esquema.
  
  La foto de grupo de 2023 se migra con `scripts/migrar_imagenes.py`, que tiene 2 entradas nuevas en `mapa_imagenes.yml`. Mientras no esté, no se muestra.
- **ODS:**
  - texto de entrada en la página;
  - las 9 tarjetas, en «principales» y «otros», en `_data/ods.yml` (nuevo, con esquema), con metas de la Agenda 2030 y enlaces a los proyectos.
  
  Los colores oficiales de la ONU llevan el número en blanco o negro, según cuál dé contraste ≥ 3:1.
- **Contacto:** todo desde `_data/grupo.yml`:
  - dirección, correo y teléfono;
  - responsable del grupo, el miembro con `role: pi`;
  - mapa de OpenStreetMap sin cookies de terceros, con enlaces a OSM y Google Maps;
  - **cómo llegar** (metro, Cercanías, autobuses y coche) con la información oficial de la ETSIST, con fuente;
  - accesibilidad del edificio.
- **`_layouts/page.html`:** `wide: true` quita el ancho máximo de texto en páginas a dos columnas.
- **Ámbitos y líneas sin listas fijas en los esquemas:** `comprobar_datos.py` toma las claves válidas de `domains`, `lines` e `icon` de lo que existe (`_domains/*.md`, `_lines/*.md`, `_includes/iconos.svg`). Para añadir un ámbito o una línea basta con crear su fichero.
  - Se ha probado con un ámbito nuevo: pasa sin errores.
  - Un icono, un ámbito o un proyecto de ODS inexistentes dan error, con la lista de opciones válidas.
- **`docs/RECETAS.md`** (nuevo): cómo añadir un ámbito o una línea y cómo cambiar los destacados de la portada, los ODS y los datos de contacto.
- **`verificar_sitio.py`** comprueba ahora que estas 6 páginas ya no dicen «pendiente de migración», que tienen su contenido y que hay tantas tarjetas de ODS como elementos en `ods.yml`.

## Corrección 6 · Código visible en la cabecera de todas las páginas y logos desbordados (17-10-2026)

- **Síntoma 1:** en todas las páginas interiores, encima de las migas de pan, aparecía en texto plano el bloque completo de textos de la portada: `{"facts_label"=>"El grupo en cifras", …}`.
- **Causa:** el bloque de textos de la portada (paso 3.5) se llamaba `home:`, igual que la clave existente `home: Inicio`, que es el texto del enlace «Inicio» en las migas. En YAML, una clave repetida se queda con el último valor sin avisar, así que `t.home` pasó a ser el bloque entero.
- **Solución:** el bloque pasa a llamarse **`portada:`** en `_data/i18n/{es,en}.yml`, y `_layouts/home.html` usa `t.portada`.
- **Prevención:** `comprobar_datos.py` da error ahora ante **cualquier clave repetida** en los YAML de `_data/`, con las dos líneas implicadas. Probado con el estado roto: detecta `home` en `es.yml` y `en.yml`.
- **Síntoma 2:** en las tarjetas de proyectos destacados, el logo se salía de su caja y tapaba el texto.
- **Causa:** la imagen no tenía un tamaño máximo efectivo dentro de la caja.
- **Solución:** caja de 140 px de alto y logo de 108 px como máximo, centrado y sin deformarse (`assets/css/grys.css`).

## Fase 3 · Paso 3.5: portada completa (17-10-2026)

- **Portada como en el mockup**, toda generada a partir de los datos:
  - **Cifras del grupo:** nº de proyectos (`_projects/`), documentos e índice h en Scopus y tesis doctorales (`_data/metrics.yml`), con la fuente y la fecha.
  - **Cuatro ejes con sus líneas** (`_data/axes.yml`, `_lines/`), enlazadas a cada ficha.
  - **Ámbitos de aplicación** (`_domains/`) con los acrónimos de sus proyectos; cada ámbito enlaza a su ancla en la página Ámbitos.
  - **Proyectos destacados** en tarjetas (`_includes/tarjeta-proyecto.html`), con logo, estado, ámbitos, tipo, programa y periodo.
  - **Noticias recientes** y, al lado:
    - la **agenda**, con los próximos eventos según la fecha de compilación; si no hay ninguno, el bloque vacío con «El último fue…»;
    - **«Únete al grupo»**, con el número de convocatorias abiertas o, si no hay, el texto del mockup.
  - **Publicaciones recientes** (`site.data.pubs`).
  - **Banda del OpenTech Lab**, con su vídeo de YouTube sin cookies.
- **`_data/portada.yml`** (nuevo) es el único sitio que se edita a mano: proyectos destacados, cuántas noticias, eventos y publicaciones se muestran y la banda del laboratorio en ES/EN. Lo valida `schemas/portada.schema.json` (nuevo), y `comprobar_datos.py` comprueba que los destacados existen.
- **Textos de interfaz:** bloque `home` en `_data/i18n/{es,en}.yml`.
- **`verificar_sitio.py`** comprueba ahora, en ES y en EN:
  - las 7 secciones;
  - las 4 cifras;
  - una tarjeta por cada proyecto destacado;
  - que hay publicaciones recientes.

## Corrección 5 · Filtro «Autoría» vacío (17-10-2026)

- **Síntoma:** `verificar_sitio` daba 56 errores del tipo «enlace ?autor=… sin opción en el filtro de autoría». Los enlaces de las fichas eran correctos, pero el desplegable de Publicaciones tenía todas las opciones vacías.
- **Causa:** el listado sacaba el slug de `m.page_id`, que solo existe en las páginas de ficha que genera el plugin, no en los documentos de la colección `site.members`.
- **Solución:**
  - filtro nuevo `slug_of` (`_plugins/grys.rb`), que da el slug con la misma regla que las URL de las fichas; lo usa ya el listado de Publicaciones;
  - `bib_index.rb` usa también esa regla, para que los dos lados coincidan siempre.
- **Prevención:** `comprobar_datos.py` da error si una plantilla usa `<variable>.page_id` con algo que no sea `page`, y añade `slug_of` a la lista de filtros permitidos.

## Fase 3 · Paso 3.4: publicaciones en las fichas (17-10-2026)

- **`_plugins/bib_index.rb`** (nuevo) genera dos índices de `papers.bib`:
  - `site.data.pubs`: las publicaciones de la más reciente a la más antigua, con proyectos, líneas y **miembros autores**;
  - `site.data.pub_index`: las mismas, por clave.
- **Autoría:** se calcula comparando los autores del BibTeX con `given`/`family` de `_members/`, sin tildes ni mayúsculas.
  - Debe coincidir el primer apellido. Si los dos tienen segundo apellido, también ese (Sánchez Alcón ≠ Sánchez Fernández).
  - Debe coincidir algún nombre, entero o por la inicial.
  - Para formas que no encajan hay un campo nuevo y opcional `bib_names` en los miembros (esquema y `docs/DATOS.md` actualizados).
- **Fichas:**
  - **Proyecto:** «Publicaciones del proyecto (n)», con `project` de `etiquetas.yml`.
  - **Línea:** «Publicaciones de la línea (n)», con `lines`.
  - **Miembro:** «Publicaciones recientes», con las 5 últimas y el enlace «Ver todas sus publicaciones (n)», que abre Publicaciones filtrada por esa persona.
  - Las fichas de proyecto y de línea muestran «por completar» mientras no haya etiquetas. La de miembro omite la sección si no hay ninguna publicación.
- **`_includes/pub-item.html`** (nuevo): publicación en formato breve, con título, autoría, revista, DOI, Portal y Archivo.
- **Publicaciones:** filtro nuevo **«Autoría»** (`?autor=slug`). Solo lista a los miembros que tienen publicaciones.
- **`verificar_sitio.py`** comprueba ahora que cada enlace `?autor=` tiene su opción en el filtro.
- **PENDIENTES.md:**
  - el rediseño de las métricas de impacto, que se hará en el último paso de la fase 3;
  - etiquetar las publicaciones con `project` y `lines`;
  - revisar la autoría calculada.

## Fase 3 · Paso 3.3: filtros e insignias en Publicaciones (17-10-2026)

- **Filtros en Publicaciones**, como en el mockup:
  - búsqueda por título, autoría, revista o DOI; no distingue mayúsculas ni tildes;
  - tipo: Todas / Revistas / Congresos / Libros y capítulos;
  - año;
  - proyecto y línea.
  
  Se ocultan los años que se quedan sin publicaciones. Recuento en vivo, bloque «sin resultados» y estado en la URL (`?tipo=journal&anio=2024`).
- **Proyecto y línea** salen de `project` y `lines` en `_bibliography/etiquetas.yml`. Solo se ofrecen las opciones que tienen publicaciones (`data-prune`); como aún no hay etiquetas, esos dos desplegables no aparecen.
- **Insignias oficiales de Altmetric y Dimensions:**
  - Altmetric se muestra si hay menciones y Dimensions si hay citas.
  - **No se cargan hasta que el visitante pulsa «Mostrar métricas de impacto».** Así no se conecta con terceros sin permiso y el rendimiento no se resiente (169 insignias). El navegador recuerda la elección.
  - Se mantienen los enlaces de texto a Altmetric y Dimensions, que funcionan sin JavaScript.
- **Recuentos en la cabecera:** los textos fijos en ES/EN de la plantilla pasan a `_data/i18n`, y «capítulos» incluye ahora libros y otros tipos.
- **`grys.js`:** el filtro de Proyectos se generaliza para listas (`P-list`). Se ha probado con un DOM simulado (9 casos).
- **`verificar_sitio.py`** comprueba ahora:
  - que están los filtros;
  - que hay un elemento filtrable por cada entrada de `papers.bib`;
  - que **ninguna página carga scripts de Altmetric o Dimensions por su cuenta**.
- **PENDIENTES.md:** mencionar las insignias en la política de privacidad (paso 3.6), la descarga del BibTeX completo y la revisión final de estilo.

## Fase 3 · Paso 3.2: filtros en Proyectos (17-10-2026)

- **Filtros de la tabla de Proyectos**, como en el mockup:
  - búsqueda por acrónimo, título (ES y EN) o programa; no distingue mayúsculas ni tildes;
  - tipo: Todos, Competitivos o Privados;
  - ámbito;
  - línea de investigación;
  - estado.
- **Solo se ofrecen las opciones que existen** en algún proyecto. El filtro de línea no aparece mientras ningún proyecto tenga `lines`.
- **Recuento en vivo** («12 proyectos»), anunciado a los lectores de pantalla (`aria-live`). Si no queda ningún resultado, sale el bloque vacío con el botón «Quitar filtros».
- **Filtros en la URL:** por ejemplo, `/investigacion/proyectos/?tipo=private&ambito=mar` se puede compartir y abre la tabla ya filtrada.
- **Sin JavaScript** no se muestran los filtros (atributo `hidden`) y se ve la tabla completa.
- **`verificar_sitio.py`** comprueba ahora:
  - que los filtros están presentes y ocultos sin JS;
  - que existen la tabla, el recuento y el aviso de «sin resultados»;
  - que hay una fila filtrable por cada fichero de `_projects/`.
- **Textos nuevos:** un bloque `filters` reutilizable (para Publicaciones en el paso 3.3) y `projects.count_one`, `competitive_pl`, `private_pl` y `search_ph`.

## Fase 3 · Paso 3.1: pestañas en Equipo y Tesis (17-10-2026)

- **Equipo:** tres pestañas («Miembros actuales (n)», «Antiguos miembros (n)», «In memoriam»), como en el mockup.
- **Tesis:** tres pestañas por nivel («Doctorado», «Máster», «Grado»), con el número de fichas. Si un nivel no tiene fichas, se muestra el bloque vacío del mockup.
- **Accesibilidad:** patrón ARIA `tablist`/`tab`/`tabpanel`. Con el teclado se cambia de pestaña con las flechas, Inicio y Fin; el título de cada panel sigue disponible para los lectores de pantalla.
- **Anclas:** la URL abre la pestaña correspondiente: `#actuales`, `#antiguos` y `#memoriam` en Equipo; `#phd`, `#master` y `#bachelor` en Tesis. Las redirecciones antiguas `/education/theses/<nivel>/` siguen funcionando. Al cambiar de pestaña se actualiza el ancla, así que el enlace se puede compartir.
- **Sin JavaScript:** no se muestran las pestañas y los bloques aparecen seguidos, cada uno con su título.
- **`verificar_sitio.py`** comprueba ahora:
  - que cada pestaña tiene su panel;
  - que hay una sola pestaña seleccionada y un solo panel visible al cargar;
  - que existen las anclas.
- **Textos nuevos** en `_data/i18n/{es,en}.yml`: `members.tabs`, `theses.tabs`, `theses.tab_*`, `theses.empty` y `theses.empty_hint`.
- **PENDIENTES.md:** B1 y B2 hechos, pasos de la fase 3 y la idea de completar `portal_upm` consultando el Portal por DOI.

## Cruce con el Portal Científico · `cruce_portal.py` v2 (17-10-2026)

Adaptado al formato real de la exportación CSV del Portal (ficha del grupo):
- **Identificadores desde la columna `PIDs`:**
  - `NNNN (iMarina)` → `portal_upm`, el ítem `…/ipublic/item/NNNN`;
  - `https://oa.upm.es/NNNN/ (Archivo Digital UPM)` → `archivo_upm`;
  - `10.… (Crossref)` → DOI.
  La columna `INDENTIFICADOR`, con esa errata en el nombre, se lee como DOI.
- **Una sola exportación** rellena a la vez los enlaces al Portal y al Archivo Digital.
- **Duplicados del Portal:** se agrupan las filas repetidas (mismo DOI o mismo título) y se juntan sus IDs; con la exportación del grupo, 49 filas son 41 publicaciones. El informe avisa de cada duplicado con enlaces a todos sus IDs.
- **Exportación de todos los ítems:** se acepta; solo se usan las filas de tipo «Publicaciones» y «Trabajos presentados en Congresos u Otros Eventos».
- **Periodo:** «Solo en el BibTeX» se limita a los años que cubre la exportación (desde 2021); las anteriores se cuentan aparte.
- **`--aplicar`:** nunca sustituye un enlace existente y se puede repetir sin efecto.

## Fase 2 · Corrección 4 (16-10-2026)

- **Las fotos del equipo no se veían aunque estaban subidas.** `avatar.html` comprobaba si existía la foto recorriendo `site.static_files` y comparando `sf.relative_path`, pero ese dato no está disponible en Liquid (solo `sf.path`). La comprobación salía siempre negativa y se mostraban las iniciales. Ahora se usa el filtro nuevo `asset_exists` (`_plugins/grys.rb`), que mira directamente el fichero. El mismo fallo impedía en `figura.html` ofrecer la miniatura (`srcset`), aunque la imagen sí se veía.
- **`comprobar_datos.py`:** da error si una plantilla recorre `site.static_files` para saber si existe un fichero.
- **`verificar_sitio.py`:** da error si hay fotos en `assets/img/equipo/` y la página Equipo (ES o EN) no muestra ninguna. Esta comprobación habría detectado este fallo.

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
