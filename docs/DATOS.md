# Referencia de datos

Generado por `scripts/doc_esquemas.py` a partir de `schemas/`. **Obligatorio** = la compilación falla si falta. El resto, si falta, aparece en el informe de pendientes y en la web como «por completar».

## Miembros · `_members/<slug>.md`

Una persona del grupo. El nombre del fichero es su slug (URL).

| Campo | Tipo | Obligatorio | Valores / descripción |
|---|---|---|---|
| `given` | string | sí | Nombre |
| `family` | string | sí | Apellidos |
| `gender` | string | sí | m/f: forma del puesto en español: `m`, `f` |
| `position` | string | sí | Puesto (clave de _data/positions.yml): `full`, `assoc`, `ppl`, `assist`, `gta`, `predoc`, `postdoc`, `r1`, `tech`, `intern`, `admin` |
| `role` | string |  | pi = investigador/a principal; ext = colaboración externa: `pi`, `ext` |
| `status` | string | sí | current = actual; former = antiguo; memoriam: `current`, `former`, `memoriam` |
| `since` | fecha |  | Fecha de incorporación (AAAA-MM-DD) |
| `until` | fecha |  | Fecha de salida |
| `photo` | string |  | Ruta de la foto WebP |
| `orcid` | string |  | Solo el identificador (0000-0000-0000-0000) |
| `scholar` | string |  | ID de Google Scholar (user=…) |
| `email` | string |  | Correo (solo se muestra en miembros actuales) |
| `website` | string |  | Web oficial |
| `portal_upm` | string |  |  |
| `scopus` | string |  |  |
| `researcherid` | string |  |  |
| `researchgate` | string |  |  |
| `linkedin` | string |  |  |
| `github` | string |  |  |
| `sciprofiles` | string |  |  |
| `lines` | lista |  | Ids de líneas de investigación: `cps`, `wsan`, `iot`, `sec`, `nca`, `rob`, `dss`, `mw`, `sw`, `edge`, `smart` |
| `bib_names` | lista de string |  | Formas del nombre en el BibTeX que no se reconocen solas (p. ej. «Martinez, Joser Fernan») |
| `lang` | string | sí | Idioma en que está escrito el texto (es/en): `es`, `en` |
| `texto_es` | string |  | Texto en español si el cuerpo está en inglés (Markdown; ver docs/RECETAS.md) |
| `texto_en` | string |  | Texto en inglés si el cuerpo está en español (Markdown) |
| `traduccion` | string |  | Estado de texto_es/texto_en: borrador (muestra un aviso) o revisada: `borrador`, `revisada` |
| `only_lang` | string |  | Publicar solo en ese idioma: `es`, `en` |
| `slug` | string |  | Parte final de la URL (por defecto, el nombre del fichero) |
| `old_urls` | lista de string |  | URL antiguas que redirigen aquí |
| `published` | boolean |  | false = no se publica |

## Proyectos · `_projects/<slug>.md`

Proyecto competitivo o contrato. El estado se calcula con las fechas.

| Campo | Tipo | Obligatorio | Valores / descripción |
|---|---|---|---|
| `acronym` | string | sí | Acrónimo |
| `title_es` | string |  | Título en español |
| `title_en` | string |  | Título en inglés |
| `type` | string | sí | Tipo (ver valores): `competitive`, `private` |
| `status` | string |  | current = actual; former = antiguo; memoriam: `ongoing`, `completed`, `upcoming`, `unknown` |
| `programme` | string |  | Programa (Horizon Europe, Plan Estatal…) |
| `programme_url` | string |  |  |
| `call` | string |  | Convocatoria |
| `funder` | string |  | Organismo financiador |
| `funding` | lista de string |  | Financiación (lista) |
| `grant_ids` | lista de string |  | Referencias / números de concesión |
| `start` | fecha |  | Inicio (AAAA-MM-DD) |
| `end` | fecha |  | Fin (AAAA-MM-DD) |
| `role` | string |  | pi = investigador/a principal; ext = colaboración externa: `coordinator`, `partner`, `subcontractor` |
| `pi` | lista de string |  | Responsable(s) en GRyS: slugs de _members |
| `pi_name` | string |  | Responsable que no es del grupo |
| `coordinator` | string |  |  |
| `coordinator_pi` | string |  |  |
| `partners` | integer o string |  | Número de socios |
| `budget` | number o string |  | Presupuesto de GRyS (€) |
| `domains` | lista |  | Ámbitos de aplicación: `campo`, `mar`, `ciudad`, `aire`, `personas` |
| `lines` | lista |  | Ids de líneas de investigación: `cps`, `wsan`, `iot`, `sec`, `nca`, `rob`, `dss`, `mw`, `sw`, `edge`, `smart` |
| `repos` | lista de string |  | Repositorios (nombres de _data/repos.yml) |
| `doi` | string |  | DOI del proyecto (10.3030/…) |
| `website` | string |  | Web oficial |
| `links` | lista de object |  | Otros enlaces (url + title) |
| `image` | string |  | Imagen o logotipo (WebP) |
| `lang` | string | sí | Idioma en que está escrito el texto (es/en): `es`, `en` |
| `texto_es` | string |  | Texto en español si el cuerpo está en inglés (Markdown; ver docs/RECETAS.md) |
| `texto_en` | string |  | Texto en inglés si el cuerpo está en español (Markdown) |
| `traduccion` | string |  | Estado de texto_es/texto_en: borrador (muestra un aviso) o revisada: `borrador`, `revisada` |
| `only_lang` | string |  | Publicar solo en ese idioma: `es`, `en` |
| `slug` | string |  | Parte final de la URL (por defecto, el nombre del fichero) |
| `old_urls` | lista de string |  | URL antiguas que redirigen aquí |
| `published` | boolean |  | false = no se publica |

## Noticias · `_news/AAAA-MM-DD-<slug>.md`



| Campo | Tipo | Obligatorio | Valores / descripción |
|---|---|---|---|
| `date` | fecha | sí | Fecha (AAAA-MM-DD) |
| `title_es` | string |  | Título en español |
| `title_en` | string |  | Título en inglés |
| `category` | string |  | Categoría: `award`, `event`, `project`, `people`, `transfer`, `lab` |
| `image` | string |  | Imagen o logotipo (WebP) |
| `lang` | string | sí | Idioma en que está escrito el texto (es/en): `es`, `en` |
| `texto_es` | string |  | Texto en español si el cuerpo está en inglés (Markdown; ver docs/RECETAS.md) |
| `texto_en` | string |  | Texto en inglés si el cuerpo está en español (Markdown) |
| `traduccion` | string |  | Estado de texto_es/texto_en: borrador (muestra un aviso) o revisada: `borrador`, `revisada` |
| `only_lang` | string |  | Publicar solo en ese idioma: `es`, `en` |
| `detail` | boolean |  | false = noticia breve sin página propia |
| `slug` | string |  | Parte final de la URL (por defecto, el nombre del fichero) |
| `slug_es` | string |  |  |
| `slug_en` | string |  |  |
| `old_urls` | lista de string |  | URL antiguas que redirigen aquí |
| `published` | boolean |  | false = no se publica |

Hace falta al menos uno de: `title_es` o `title_en`.

## Eventos · `_events/<nombre>.md`

Se clasifica en próximo/pasado según la fecha de compilación.

| Campo | Tipo | Obligatorio | Valores / descripción |
|---|---|---|---|
| `date` | fecha | sí | Fecha (AAAA-MM-DD) |
| `end` | fecha |  | Fin (AAAA-MM-DD) |
| `title_es` | string |  | Título en español |
| `title_en` | string |  | Título en inglés |
| `type` | string |  | Tipo (ver valores): `workshop`, `conference`, `seminar`, `summer_school`, `meeting`, `fair`, `award`, `other` |
| `involvement` | string |  | Papel del grupo: `organizer`, `presenter`, `participant`, `exhibitor`, `awardee`, `guest`, `attendee` |
| `place` | string |  | Lugar |
| `format` | string |  | Presencial, en línea o híbrido: `in_person`, `online`, `hybrid` |
| `website` | string |  | Web oficial |
| `projects` | lista de string |  |  |
| `news` | string |  | Noticia relacionada (nombre del fichero sin .md) |
| `summary_es` | string |  |  |
| `summary_en` | string |  |  |
| `lang` | string | sí | Idioma en que está escrito el texto (es/en): `es`, `en` |
| `old_urls` | lista de string |  | URL antiguas que redirigen aquí |
| `published` | boolean |  | false = no se publica |

Hace falta al menos uno de: `title_es` o `title_en`.

## Convocatorias · `_opportunities/<nombre>.md`

Deja de publicarse al pasar «deadline».

| Campo | Tipo | Obligatorio | Valores / descripción |
|---|---|---|---|
| `date` | fecha | sí | Fecha (AAAA-MM-DD) |
| `deadline` | string | sí | Plazo: «AAAA-MM-DD HH:MM:SS +0200»; después no se publica |
| `type` | string | sí | Tipo (ver valores): `job`, `scholarship`, `student_project`, `phd` |
| `title_es` | string |  | Título en español |
| `title_en` | string |  | Título en inglés |
| `project` | string |  | Proyecto (slug de _projects) |
| `line` | string |  | Línea de investigación: `cps`, `wsan`, `iot`, `sec`, `nca`, `rob`, `dss`, `mw`, `sw`, `edge`, `smart` |
| `pdf` | string |  | Oferta completa en PDF |
| `contact` | string |  |  |
| `lang` | string | sí | Idioma en que está escrito el texto (es/en): `es`, `en` |
| `old_urls` | lista de string |  | URL antiguas que redirigen aquí |
| `published` | boolean |  | false = no se publica |

Hace falta al menos uno de: `title_es` o `title_en`.

## Líneas · `_lines/<id>.md`



| Campo | Tipo | Obligatorio | Valores / descripción |
|---|---|---|---|
| `key` | string | sí | Identificador (igual que el nombre del fichero): `cps`, `wsan`, `iot`, `sec`, `nca`, `rob`, `dss`, `mw`, `sw`, `edge`, `smart` |
| `axis` | integer | sí |  |
| `icon` | string | sí | `campo`, `mar`, `ciudad`, `aire`, `personas`, `check`, `search`, `menu`, `net`, `doc`, `cal`, `sun`, `moon`, `mail`, `pin`, `phone`, `code`, `award`, `cap`, `lab`, `play`, `handshake`, `globe`, `news`, `mega`, `ext` |
| `order` | integer |  |  |
| `title_es` | string | sí | Título en español |
| `title_en` | string | sí | Título en inglés |
| `desc_es` | string | sí |  |
| `desc_en` | string | sí |  |
| `slug_es` | string | sí |  |
| `slug_en` | string | sí |  |
| `lang` | string |  | Idioma en que está escrito el texto (es/en): `es`, `en` |
| `texto_es` | string |  | Texto en español si el cuerpo está en inglés (Markdown; ver docs/RECETAS.md) |
| `texto_en` | string |  | Texto en inglés si el cuerpo está en español (Markdown) |
| `traduccion` | string |  | Estado de texto_es/texto_en: borrador (muestra un aviso) o revisada: `borrador`, `revisada` |
| `keywords` | lista de string |  |  |
| `old_urls` | lista de string |  | URL antiguas que redirigen aquí |

## Ámbitos · `_domains/<id>.md`



| Campo | Tipo | Obligatorio | Valores / descripción |
|---|---|---|---|
| `key` | string | sí | Identificador (igual que el nombre del fichero): `campo`, `mar`, `ciudad`, `aire`, `personas` |
| `icon` | string | sí | `campo`, `mar`, `ciudad`, `aire`, `personas`, `check`, `search`, `menu`, `net`, `doc`, `cal`, `sun`, `moon`, `mail`, `pin`, `phone`, `code`, `award`, `cap`, `lab`, `play`, `handshake`, `globe`, `news`, `mega`, `ext` |
| `order` | integer |  |  |
| `title_es` | string | sí | Título en español |
| `title_en` | string | sí | Título en inglés |
| `subtitle_es` | string |  |  |
| `subtitle_en` | string |  |  |
| `desc_es` | string | sí |  |
| `desc_en` | string | sí |  |
