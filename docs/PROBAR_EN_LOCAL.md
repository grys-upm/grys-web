# Ver la web antes de publicarla

Hay cuatro formas de hacerlo, de menos a más instalación. Todas muestran la web en español en `/` y en inglés en `/en/`.

| Forma | Qué necesitas | Cuándo usarla |
|---|---|---|
| A. Artefacto de la PR | Python | Revisar un cambio que ya está en GitHub, sin instalar nada |
| B. Codespaces | Un navegador | Editar y ver al momento sin instalar nada |
| C. Docker | Docker Desktop | Trabajar en tu ordenador sin instalar Ruby |
| D. Ruby | Ruby 3.3 + Python | Trabajo habitual en tu ordenador; es lo más rápido |

---

## A. Descargar la web compilada de una PR

1. **Abrir una PR.** Sube el cambio a una **rama** y abre una *Pull Request*. Desde la web de GitHub, al editar un fichero, elige *Create a new branch… and start a pull request*.
2. **Esperar la comprobación.** El workflow **Comprobar PR** compila y verifica la web.
3. **Descargar la web.** En *Actions → Comprobar PR →* (la ejecución) *→ Artifacts*, descarga **sitio-compilado** y descomprímelo.
4. **Abrirla en el navegador.** En esa carpeta, ejecuta:
   ```
   python -m http.server 8000
   ```
   y abre <http://localhost:8000/>. Para parar, pulsa Ctrl+C.

No abras los `.html` con doble clic: los enlaces y estilos solo funcionan a través de un servidor.

## B. GitHub Codespaces (en el navegador)

1. **Crear el entorno.** En el repositorio, pulsa *Code → Codespaces → Create codespace on main*. La primera vez tarda unos minutos, porque instala Ruby y las gemas según `.devcontainer/devcontainer.json`.
2. **Arrancar la web.** En la terminal de abajo, escribe:
   ```
   bundle exec jekyll serve --config _config.yml,_config.staging.yml
   ```
3. **Abrir la vista previa.** Se abre sola una pestaña con la web; si no, ve a la pestaña *Ports* y abre el puerto 4000.
4. **Guardar los cambios.** Edita los ficheros y recarga la página para verlos. Para guardarlos en GitHub, usa el panel *Source Control* (*Commit* y *Sync*).

Codespaces tiene una cuota de uso; si se agota, depende de la configuración de la organización. Para al terminar: *Codespaces → Stop*.

## C. Docker (sin instalar Ruby)

1. **Instalar Docker.** Instala [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. **Arrancar la web.** En la carpeta del proyecto, ejecuta:
   ```
   docker compose up
   ```
3. **Abrirla.** Ve a <http://localhost:4000/>. La página se recarga sola al guardar un fichero.
4. **Parar.** Pulsa Ctrl+C.

La primera vez tarda unos minutos. Las gemas quedan en `vendor/bundle/`, que ya está en `.gitignore`.

## D. Ruby instalado en tu ordenador

**Instalación (una sola vez):**
- **Windows:** [RubyInstaller](https://rubyinstaller.org/downloads/), versión **Ruby+Devkit 3.3.x (x64)**. Al acabar, deja marcado *Run `ridk install`* y elige la opción 3. Python, desde <https://www.python.org/downloads/>.
- **macOS:** `brew install ruby@3.3 python`. Después sigue las indicaciones de Homebrew para añadir Ruby al `PATH`.
- **Linux:** usa `rbenv` o `ruby-install` para tener Ruby 3.3; Python ya suele estar instalado.

**Después, una sola vez, en la carpeta del proyecto:**
```
gem install bundler
bundle install
python -m pip install pyyaml
```

**Cada vez que quieras ver la web:**
```
bundle exec jekyll serve --livereload --config _config.yml,_config.staging.yml
```
Abre <http://localhost:4000/>. La página se recarga sola al guardar. Si cambias `_config.yml` o algo de `_plugins/`, para con Ctrl+C y vuelve a arrancar.

**Antes de subir los cambios** (son las mismas comprobaciones que hace GitHub):
```
python scripts/comprobar_datos.py
python scripts/contraste.py
bundle exec jekyll build --config _config.yml,_config.staging.yml
python scripts/verificar_sitio.py _site
```

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| `Could not find gem …` | Ejecuta `bundle install` |
| En Windows, los cambios no se detectan | Añade `--force_polling` al comando `serve` |
| Puerto 4000 ocupado | Añade `--port 4001` y abre <http://localhost:4001/> |
| La web sale sin estilos | Ábrela desde `http://localhost:…`, nunca con doble clic en el `.html` |
| Las fuentes no son las del manual | Falta `assets/fonts/*.woff2`: ejecuta `python scripts/descargar_fuentes.py` |
