# Compilar, probar y publicar

## 1. Crear el repositorio de pruebas (una sola vez)

1. **Crear el repositorio.** En la organización `grys-upm`, crea un repositorio **público** y vacío. Este documento supone que se llama `grys-web`. Si eliges otro nombre, cámbialo también en `repository:` de `_config.staging.yml`.
2. **Subir los ficheros.** Sube el contenido del zip de la fase, con la carpeta `.github` incluida.
   - Sin Git: *Add file → Upload files*, arrastrando las carpetas.
   - Con Git: `git init`, `git add .`, `git commit -m "Fase 1"` y `git push`.
3. **Activar Pages.** En *Settings → Pages → Build and deployment → Source*, elige **GitHub Actions**.
4. **Fuentes: no hay que hacer nada.** Si `assets/fonts/` no tiene los `.woff2`, GitHub Actions los descarga en cada compilación con `scripts/descargar_fuentes.py`. Se sirven desde el propio sitio, no desde Google Fonts.
   *Opcional, para no depender de la descarga:* ejecuta en tu ordenador, dentro de la carpeta del proyecto, `python3 scripts/descargar_fuentes.py`. Después sube los 8 ficheros que aparecen en `assets/fonts/` a esa misma carpeta del repositorio: entra en ella en GitHub y usa *Add file → Upload files*.
5. **Ver la compilación.** Cada *push* lanza *Actions → Compilar y publicar*.
   - **Dónde se publica.** Como la organización ya tiene dominio propio, el sitio de pruebas debería quedar en `https://grys.etsist.upm.es/grys-web/`. Si no fuera así, estará en `https://grys-upm.github.io/grys-web/`.
   - **Fuera de buscadores.** Lleva `noindex`.
   - **No toca la web actual.** La web publicada no cambia.
6. **Fijar las versiones de las gemas.** Descarga el artefacto **Gemfile.lock** de la primera ejecución correcta y súbelo a la raíz del repositorio. Así las versiones quedan fijadas.
7. **Imágenes y PDF (una sola vez, fase 2).** El repositorio nuevo solo lleva las imágenes que usa la web, en WebP. La lista está en `scripts/migracion/mapa_imagenes.yml`. En un ordenador con Python y con una copia del repositorio antiguo:
   ```
   python -m pip install pillow pyyaml
   python scripts/migrar_imagenes.py RUTA/A/grys-upm.github.io
   ```
   Se crean `assets/img/{equipo,noticias,proyectos}/…` y `assets/convocatorias/…`. Súbelas: en GitHub, entra en `assets/` y usa *Add file → Upload files*, arrastrando las carpetas `img` y `convocatorias`. Mientras no estén, la web se ve igual pero sin fotos (avatares con iniciales), y las comprobaciones lo indican con un aviso, no con un error.

## 2. Compilar en local (opcional)

Las cuatro formas de ver la web antes de publicar (artefacto de la PR, Codespaces, Docker o Ruby) están explicadas paso a paso en [PROBAR_EN_LOCAL.md](PROBAR_EN_LOCAL.md). Resumen con Ruby:

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

### Comprobaciones informativas (no impiden fusionar)

La protección de `main` solo exige el job `build` («Comprobar PR»). Estas otras salen en la PR con ✅ o ❌, pero no bloquean la fusión:

| Comprobación | Cuándo | Qué hace | Si sale ❌ |
|---|---|---|---|
| **Enlaces nuevos** | cada PR | Comprueba con lychee solo las URL externas que **añade** la PR. La configuración y las exclusiones están en `lychee.toml` | Abre el resumen de la ejecución, corrige la URL y vuelve a subir. Si la URL funciona en el navegador, el sitio bloquea robots: añádelo a `exclude` en `lychee.toml` |
| **Lighthouse** | cada PR que compila | Rendimiento, accesibilidad, buenas prácticas y SEO de 8 páginas representativas (mediana de 3 ejecuciones, móvil simulado). Las páginas están en `lighthouserc.json` | Error si accesibilidad < 95 o SEO < 90. Rendimiento < 80 y buenas prácticas < 90 solo dan aviso. Los informes completos están en el artefacto `informe-lighthouse` |
| **Enlaces externos** | cada lunes y a mano | Comprueba todos los enlaces externos del sitio | Abre o actualiza la issue «Enlaces rotos» con la lista, y la cierra cuando ya no quedan |

## 4. Si algo falla

En *Actions*, abre la ejecución fallida, despliega el paso en rojo y copia el texto completo del error. Para el paso *Compilar*, copia el registro entero.

## 5. Vista previa de cada PR (una sola vez)

Cada PR (también las que creen el gestor de contenidos y los formularios de *issue* de la fase 5) se publica en una dirección propia, por ejemplo `https://grys-upm.github.io/grys-web-previews/pr-12/`. El enlace aparece en un comentario de la propia PR, y la página lleva una franja que indica que es una vista previa. Se borra sola al cerrar la PR.

GitHub Pages solo permite una web por repositorio, así que las vistas previas van en un **repositorio aparte**. Para que GitHub Actions pueda escribir en él se usa una **clave de despliegue**, que solo da acceso a ese repositorio.

1. **Crear el repositorio.** En `grys-upm`, crea el repositorio **público** `grys-web-previews` y marca *Add a README file*.
2. **Activar Pages en él.** En *Settings → Pages → Source*, elige **Deploy from a branch**, rama `main` y carpeta `/ (root)`.
3. **Crear la pareja de claves.** En tu ordenador (Linux, macOS o PowerShell de Windows 10/11):
   ```
   ssh-keygen -t ed25519 -N "" -C "grys-web vista previa" -f vista-previa
   ```
   Se crean dos ficheros: `vista-previa` (privada) y `vista-previa.pub` (pública).
4. **Clave pública → repositorio de vistas previas.** En `grys-web-previews`, *Settings → Deploy keys → Add deploy key*:
   - título: `grys-web`;
   - contenido: el de `vista-previa.pub`;
   - ✅ marca **Allow write access**.
5. **Clave privada → repositorio de la web.** En `grys-web`, *Settings → Secrets and variables → Actions → New repository secret*:
   - nombre: `PREVIEW_DEPLOY_KEY`;
   - valor: el contenido completo de `vista-previa`, incluidas las líneas `-----BEGIN…` y `-----END…`.
6. **Borrar las claves de tu ordenador.** Ya no hacen falta; si algún día se pierden, se crean otras.
7. *(Solo si el repositorio de vistas previas tiene otro nombre.)* En `grys-web`, *Settings → Secrets and variables → Actions → Variables*, crea `PREVIEW_REPO` con el valor `organización/nombre`.

Mientras no esté configurado, las PR funcionan igual: el paso «Vista previa» solo deja un aviso. Sigue existiendo el artefacto `sitio-compilado` para descargar. Las PR de Dependabot y las de *forks* no tienen vista previa, porque GitHub no les da acceso a la clave.

**Limpieza:** si alguna vista previa se queda sin borrar, lanza *Actions → Borrar vista previa → Run workflow*. Borra las de todas las PR que ya no están abiertas.

## 6. Dependabot

`.github/dependabot.yml` revisa una vez al mes las acciones de GitHub, las gemas de Ruby y los paquetes de la auditoría de accesibilidad, y propone una PR por tipo. Las PR de Dependabot pasan «Comprobar PR» como cualquier otra:
- **si todo sale en verde**, se pueden fusionar;
- **si algo falla**, no se fusionan: se deja un comentario y quien mantenga el sitio lo revisa.

Las versiones mayores de las gemas (Jekyll 5…) no se proponen; se actualizan a mano. Para recibir también las **alertas de seguridad**, activa en `grys-web` *Settings → Code security → Dependabot alerts* y *Dependabot security updates*.

Para Dependabot con las gemas hace falta que **`Gemfile.lock` esté en el repositorio**. Si aún no lo subiste, mira el paso 6 del apartado 1.

## 7. Migración a producción (cuando el sitio nuevo esté validado)

1. **Copia de seguridad.** En `grys-upm/grys-upm.github.io`, crea la rama `archivo-al-folio` desde `main`.
2. **Sustituir el contenido.** Sustituye el contenido de `main` por el de `grys-web`. Conserva el historial y no hace falta copiar `_config.staging.yml`.
3. **Añadir el dominio.** Añade el fichero `CNAME` con una sola línea: `grys.etsist.upm.es`.
4. **Activar el despliegue nuevo.** En *Settings → Pages*, pon *Source: GitHub Actions*. El dominio personalizado se mantiene. Desactiva el despliegue antiguo a `gh-pages` y borra esa rama.
5. **Retirar las pruebas.** Desactiva Pages en `grys-web` o archiva ese repositorio, y archiva también `grys-web-previews` si la web de producción no va a usar vistas previas. Si las va a usar, mueve el secreto `PREVIEW_DEPLOY_KEY` al repositorio de producción.
6. **Revisar las redirecciones.** Comprueba que las URL antiguas redirigen, por ejemplo `/team/` → `/en/group/team/`.
