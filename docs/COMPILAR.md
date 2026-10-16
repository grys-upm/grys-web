# Compilar, probar y publicar

## 1. Crear el repositorio de pruebas (una sola vez)

1. **Crear el repositorio.** En la organización `grys-upm`, crea un repositorio **público** y vacío. Este documento supone que se llama `web-grys`. Si eliges otro nombre, cámbialo también en `repository:` de `_config.staging.yml`.
2. **Subir los ficheros.** Sube el contenido del zip de la fase, con la carpeta `.github` incluida.
   - Sin Git: *Add file → Upload files*, arrastrando las carpetas.
   - Con Git: `git init`, `git add .`, `git commit -m "Fase 1"` y `git push`.
3. **Activar Pages.** En *Settings → Pages → Build and deployment → Source*, elige **GitHub Actions**.
4. **Descargar las fuentes** (una vez, en un ordenador con Internet) y subirlas:
   ```bash
   python3 scripts/descargar_fuentes.py
   ```
   Se añaden 8 ficheros `assets/fonts/*.woff2`.
5. **Ver la compilación.** Cada *push* lanza *Actions → Compilar y publicar*.
   - **Dónde se publica.** Como la organización ya tiene dominio propio, el sitio de pruebas debería quedar en `https://grys.etsist.upm.es/web-grys/`. Si no fuera así, estará en `https://grys-upm.github.io/web-grys/`.
   - **Fuera de buscadores.** Lleva `noindex`.
   - **No toca la web actual.** La web publicada no cambia.
6. **Fijar las versiones de las gemas.** Descarga el artefacto **Gemfile.lock** de la primera ejecución correcta y súbelo a la raíz del repositorio. Así las versiones quedan fijadas.

## 2. Compilar en local (opcional)

Necesitas Ruby 3.3 y Python 3.

```bash
gem install bundler
bundle install
python3 -m pip install pyyaml

python3 scripts/comprobar_datos.py
python3 scripts/contraste.py
bundle exec jekyll serve --config _config.yml,_config.staging.yml
# → http://localhost:4000/        (español)
# → http://localhost:4000/en/     (inglés)

bundle exec jekyll build --config _config.yml,_config.staging.yml
python3 scripts/verificar_sitio.py _site
```

En Windows, Ruby se instala con [RubyInstaller](https://rubyinstaller.org/), eligiendo la versión *with Devkit*.

## 3. Qué comprueba cada paso

| Paso | Detiene la publicación si… |
|---|---|
| `comprobar_datos.py` | hay YAML mal formado, rutas incoherentes con `_pages/`, claves de idioma descuadradas, redirecciones a páginas que no existen, bloques Liquid sin cerrar o filtros inexistentes |
| `contraste.py` | algún par de colores de los tokens baja de 4,5:1, en cualquiera de los dos temas |
| `jekyll build` | hay errores, o aparecen `Liquid Warning`, `Build Warning`, `Conflict:` o avisos `GRyS:` en el registro |
| `verificar_sitio.py` | falta alguna página ES/EN o alguna redirección, alguna página no tiene exactamente un `<h1>`, falta «Saltar al contenido», el tema por defecto no es el oscuro, el *script* del tema no va antes del CSS, queda Liquid sin procesar o contenido de demostración, o hay enlaces internos rotos |

## 4. Si algo falla

En *Actions*, abre la ejecución fallida, despliega el paso en rojo y copia el texto completo del error. Para el paso *Compilar*, copia el registro entero.

## 5. Migración a producción (cuando el sitio nuevo esté validado)

1. **Copia de seguridad.** En `grys-upm/grys-upm.github.io`, crea la rama `archivo-al-folio` desde `main`.
2. **Sustituir el contenido.** Sustituye el contenido de `main` por el de `web-grys`. Conserva el historial y no hace falta copiar `_config.staging.yml`.
3. **Añadir el dominio.** Añade el fichero `CNAME` con una sola línea: `grys.etsist.upm.es`.
4. **Activar el despliegue nuevo.** En *Settings → Pages*, pon *Source: GitHub Actions*. El dominio personalizado se mantiene. Desactiva el despliegue antiguo a `gh-pages` y borra esa rama.
5. **Retirar las pruebas.** Desactiva Pages en `web-grys` o archiva ese repositorio.
6. **Revisar las redirecciones.** Comprueba que las URL antiguas redirigen, por ejemplo `/team/` → `/en/group/team/`.
