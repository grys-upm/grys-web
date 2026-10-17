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

## Cambiar datos de contacto, cómo llegar o accesibilidad

Todo está en `_data/grupo.yml`:
- correo, teléfono y dirección;
- `coords`, las coordenadas del marcador del mapa;
- `como_llegar`;
- `accesibilidad`.

La página Contacto y el pie se actualizan solos.
