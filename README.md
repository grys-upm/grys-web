# Web del GRyS

Sitio del **Grupo de Redes y Servicios de Próxima Generación** (Universidad Politécnica de Madrid). Se publica en <https://grys.etsist.upm.es>.

Es un sitio Jekyll propio, sin tema externo. Todo el contenido se guarda como datos:

| Qué | Dónde |
|---|---|
| Menús, URL y títulos de las páginas (ES/EN) | `_data/routes.yml` |
| Textos de la interfaz | `_data/i18n/es.yml`, `_data/i18n/en.yml` |
| Contacto y enlaces institucionales | `_data/grupo.yml` |
| Redirecciones desde la web anterior | `_data/redirects.yml` y el campo `old_urls` de cada elemento |
| Texto de las páginas fijas | `_pages/es/*.md`, `_pages/en/*.md` |
| Personas, proyectos, líneas, ámbitos, noticias, eventos y convocatorias | `_members/`, `_projects/`, `_lines/`, `_domains/`, `_news/`, `_events/`, `_opportunities/` (un fichero por elemento) |
| Publicaciones y tesis | `_bibliography/*.bib` |
| Diseño | `assets/css/grys.css` (tokens de color al principio), `_layouts/`, `_includes/` |
| Lógica de rutas bilingües | `_plugins/grys.rb` |

- **Español** en `/` e **inglés** en `/en/`, con *jekyll-polyglot*.
- Las **fichas de detalle** (personas, proyectos, líneas, noticias) se generan en los dos idiomas a partir de un único fichero de datos.

## Compilar y comprobar

Ver [docs/COMPILAR.md](docs/COMPILAR.md). En resumen:

```bash
bundle install
python3 scripts/comprobar_datos.py      # datos, rutas y Liquid (sin Ruby)
python3 scripts/contraste.py            # contraste AA de los tokens, ambos temas
bundle exec jekyll build
python3 scripts/verificar_sitio.py _site
```

## Estado

Este repositorio es el **sitio nuevo en pruebas**. La web publicada sigue saliendo de `grys-upm/grys-upm.github.io` (al-folio) hasta la migración. Las fases del trabajo están en `CHANGES.md` y lo que queda pendiente en `PENDIENTES.md`.
