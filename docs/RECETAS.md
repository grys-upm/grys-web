# Recetas: cómo se hacen los cambios más habituales

Cada receta indica qué ficheros tocar y cómo comprobarlo. Antes de subir cualquier cambio, ejecuta:

```
python scripts/comprobar_datos.py
```

Debe terminar con `0 errores`. Los campos de cada tipo de contenido están en [DATOS.md](DATOS.md).

---

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

## Indicar la protección de un resultado (registro, patente…)

En `_data/transferencia.yml`, dentro de la oferta, añade `proteccion`:

```yaml
    proteccion:
      tipo: registro_pi          # registro_pi | patente | modelo_utilidad | secreto | abierto
      numero: "M-000123/2024"    # asiento registral o nº de publicación, tal como figura en el título
      oficina: { es: "Registro Territorial de la Propiedad Intelectual de la Comunidad de Madrid", en: "Madrid Regional Intellectual Property Registry" }
      fecha: 2024-05-12          # inscripción o concesión
      titulares: { es: "Universidad Politécnica de Madrid", en: "Universidad Politécnica de Madrid" }  # opcional (es el valor por defecto)
      url: https://…             # opcional: enlace a la publicación
      licencia: Apache-2.0       # opcional: si además el código es abierto
```

- **Patentes y modelos de utilidad sin `url`:** el número enlaza solo a su búsqueda en Espacenet (p. ej. `ES2912345B2`).
- **Número vacío:** en registros, patentes y modelos de utilidad, `comprobar_datos.py` avisa y la web muestra «por completar».

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

## Cambiar datos de contacto, cómo llegar o accesibilidad

Todo está en `_data/grupo.yml`:
- correo, teléfono y dirección;
- `coords`, las coordenadas del marcador del mapa;
- `como_llegar`;
- `accesibilidad`.

La página Contacto y el pie se actualizan solos.
