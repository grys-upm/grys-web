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

### Protección de `main`

La regla que exige pasar «Comprobar PR» para fusionar está en `.github/rulesets/main.json`. Cómo activarla y qué hace: [MANTENIMIENTO.md](MANTENIMIENTO.md) §2.

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
6. **Protección de `main`.** Importa `.github/rulesets/main.json` también en el repositorio de producción (MANTENIMIENTO §2).
7. **Gestor de contenidos.** En la aplicación OAuth (§8.3), cambia *Homepage URL* si hace falta. `cms.repo` toma el valor de `repository:`, así que el gestor pasa a guardar en el repositorio de producción. Repite los ajustes de §8.1 y §8.2 en ese repositorio.
8. **Revisar las redirecciones.** Comprueba que las URL antiguas redirigen, por ejemplo `/team/` → `/en/group/team/`.

## 8. Gestor de contenidos (una sola vez)

El gestor (Sveltia CMS) está en `/admin/` y permite editar Noticias, Eventos, Convocatorias, Miembros y Proyectos sin Git. La guía para editores está en [EDITAR.md](EDITAR.md).

**Cómo funciona.** Cada cambio guardado se convierte en una PR (rama `cms/…`): pasa «Comprobar PR» y tiene vista previa. «Publicar» la fusiona. Si las comprobaciones aún no han terminado, deja programada la fusión automática. La configuración está en `admin/config.yml`, una plantilla que Jekyll rellena con los puestos, roles, líneas, ámbitos y repositorios de `_data/` y de las colecciones.

`comprobar_datos.py` da error si al gestor le falta algún campo de los esquemas, porque lo borraría al guardar una ficha, o si ofrece una opción que el esquema no admite. Al añadir un campo a un esquema, añádelo también en `admin/config.yml`.

### 8.1 Quién puede editar

1. **Crear el equipo.** En la organización `grys-upm`, *Teams → New team*: nombre `web`, visibilidad *Visible*. Añade a los miembros del grupo que vayan a editar.
2. **Dar permiso al equipo.** En `grys-web`, *Settings → Collaborators and teams → Add teams*: equipo `web`, rol **Write**.
3. **Revisar el permiso base.** En la organización, *Settings → Member privileges → Base permissions*: mejor **Read**, para que solo el equipo `web` (y los administradores) puedan guardar.

### 8.2 Ajustes del repositorio

1. **Fusión automática.** En `grys-web`, *Settings → General → Pull Requests*: activa **Allow auto-merge**. Así «Publicar» funciona aunque las comprobaciones sigan en marcha.
2. **Fusión con *squash*.** En el mismo apartado, deja activado **Allow squash merging**. El gestor fusiona así: un commit por cambio.
3. **Borrar las ramas fusionadas.** Activa también **Automatically delete head branches**.
4. **Tokens de la organización.** Si se va a entrar con token: en la organización, *Settings → Personal access tokens*, permite los *fine-grained tokens*. Puedes exigir aprobación de cada token.

### 8.3 Inicio de sesión con GitHub (recomendado)

Sin este paso solo se puede entrar con un token personal, que funciona pero es incómodo. Con él aparece el botón «Iniciar sesión con GitHub». Hace falta un pequeño servicio gratuito en Cloudflare que intercambia el código de GitHub por la sesión:

1. **Desplegar el autenticador.** Crea una cuenta gratuita en Cloudflare. Abre [sveltia-cms-auth](https://github.com/sveltia/sveltia-cms-auth) y pulsa **Deploy to Cloudflare Workers**. Al terminar, copia la dirección del *worker* (algo como `sveltia-cms-auth.NOMBRE.workers.dev`, con `https://` delante).
2. **Registrar la aplicación OAuth en la organización.** *grys-upm → Settings → Developer settings → OAuth Apps → New OAuth App*:
   - *Application name*: `GRyS · gestor de contenidos`;
   - *Homepage URL*: `https://grys.etsist.upm.es/`;
   - *Authorization callback URL*: `<dirección del worker>/callback`.

   Después pulsa *Generate a new client secret*.
3. **Configurar el worker.** En Cloudflare, *Workers → sveltia-cms-auth → Settings → Variables*, añade:
   - `GITHUB_CLIENT_ID`;
   - `GITHUB_CLIENT_SECRET` (márcala como cifrada);
   - `ALLOWED_DOMAINS` = `grys-upm.github.io, grys.etsist.upm.es`.
4. **Activarlo en la web.** En `_config.yml`, pon la dirección del worker en `cms: oauth_url:`. Súbelo por PR como cualquier otro cambio.

### 8.4 Comprobar que funciona

1. **Entrar.** Abre `/admin/` en la web de pruebas y entra.
2. **Guardar un cambio de prueba.** Edita una noticia, cambia una coma y guarda. ✅ En `grys-web` aparece una PR de la rama `cms/news/…`, con «Comprobar PR» y el comentario de la vista previa.
3. **Ver la vista previa.** ✅ En el gestor aparece «Ver vista previa». Usa el estado `vista-previa` que pone el job «Vista previa».
4. **Publicar.** Pon la noticia en «Listo» y pulsa «Publicar». ✅ La PR se fusiona cuando «Comprobar PR» termina, y la rama se borra.

**Versión del gestor.** `admin/index.html` carga siempre la última versión publicada de Sveltia CMS. Está en beta y recibe correcciones casi a diario. Si una versión nueva diera problemas, se puede fijar una concreta cambiando la dirección del *script* (por ejemplo `@sveltia/cms@0.235.1`).

## 9. Formularios de issue (opcional)

Los formularios de `.github/ISSUE_TEMPLATE/` (Noticia, Evento, Convocatoria, Miembro, Proyecto) crean una PR con el fichero ya hecho. El flujo `issue-a-pr.yml` usa `scripts/issue_a_contenido.py`:
- **Quién puede usarlos:** solo generan la PR si quien abre la issue tiene permiso de escritura, o si alguien con permiso le añade la etiqueta `generar-pr`.
- **Qué se comprueba:** los datos se validan con `comprobar_datos.py` antes de abrir la PR, y los errores se contestan en la propia issue.
- **Las etiquetas** se crean solas.

**Listas de opciones.** Los puestos, líneas y ámbitos de los formularios se generan desde los datos. Si añades uno, `comprobar_datos.py` avisa de que hay que regenerarlos: `python scripts/issue_a_contenido.py --plantillas`.

**Comprobaciones de las PR generadas.** GitHub no lanza otros flujos cuando la PR la crea el token normal de Actions. Sin más configuración, la PR lleva un comentario que pide **cerrarla y reabrirla** una vez para lanzar las comprobaciones. Para que se lancen solas, crea una aplicación de GitHub (una sola vez, unos 10 minutos):

1. **Crear la aplicación.** En `grys-upm` → *Settings → Developer settings → GitHub Apps → New GitHub App*:
   - nombre `grys-web-contenido`;
   - *Homepage URL*: la del repositorio;
   - desmarca *Webhook → Active*;
   - permisos de repositorio: **Contents: Read and write** y **Pull requests: Read and write**;
   - *Where can this GitHub App be installed?*: *Only on this account*.
2. **Clave privada.** En la página de la aplicación, anota el **App ID** y pulsa *Generate a private key* (se descarga un `.pem`).
3. **Instalarla.** *Install App* → `grys-upm` → *Only select repositories* → `grys-web`.
4. **Guardar sus datos en el repositorio.** En `grys-web` → *Settings → Secrets and variables → Actions*:
   - variable `CONTENIDO_APP_ID` = el App ID;
   - secreto `CONTENIDO_APP_KEY` = el contenido completo del `.pem`.

   Después borra el `.pem` de tu ordenador.

**En la migración a producción:** cambia en `.github/ISSUE_TEMPLATE/config.yml` la dirección del gestor por `https://grys.etsist.upm.es/admin/` e instala la aplicación también en el repositorio de producción.

## 10. Sincronización con Zotero

Las publicaciones (`_bibliography/papers.bib`) salen de la biblioteca de grupo de Zotero (grupo 5287048). Las tesis (`theses.bib`) no se sincronizan: se editan a mano.

**Cuándo se sincroniza.** Cada lunes a las 05:45 UTC, y cuando se quiera desde *Actions → Sincronizar con Zotero → Run workflow*. Si hay cambios, se abre o actualiza la PR **«Publicaciones: sincronización con Zotero»** con un informe:
- publicaciones nuevas, con cambios y borradas;
- las clasificadas con etiquetas;
- las nuevas que aún no tienen proyecto o línea.

Se revisa en la vista previa y se fusiona. Si ya no hay diferencias, la PR se cierra sola.

**Qué hace `scripts/sincronizar_zotero.py`:**
- **Conserva las claves BibTeX** (de ellas dependen `etiquetas.yml`, las citas y las anclas): empareja cada ítem por su identificador de Zotero (guardado en `_bibliography/zotero-claves.yml`), por DOI o por título y año.
- **Quita los campos internos** (`urldate`, `copyright`…) y las etiquetas de servicio de `keywords` (`⛔ No DOI found`…).
- **Etiquetas `proyecto:<slug>` y `linea:<id>` en Zotero:** clasifican la publicación y mandan sobre `etiquetas.yml`. Es la forma más cómoda de etiquetar: se hace en Zotero y llega a la web en la siguiente sincronización.
- **Fusiones en Zotero:** si se fusionan dos ítems duplicados, los campos propios de la entrada que desaparece (`portal_upm`…) pasan a la que queda.
- **Seguridad:** no borra más del 10 % de las publicaciones (ni ninguna si Zotero no devuelve nada). En ese caso la ejecución falla y GitHub avisa por correo; si el borrado es intencionado, se repite con *Permitir borrados*.

**Configuración (una vez):**
1. **Clave de la API.** Si el grupo de Zotero es **público**, no hace falta. Si es privado: en zotero.org, *Settings → Security → Create new private key*, con acceso **solo de lectura** al grupo 5287048 y sin acceso a la biblioteca personal. Guárdala en `grys-web` → *Settings → Secrets and variables → Actions* como secreto **`ZOTERO_API_KEY`**.
2. *(Opcional)* Variables `ZOTERO_GRUPO` (otro grupo), `ZOTERO_COLECCION` (clave de una colección, si solo una parte de la biblioteca son publicaciones del grupo) y `ZOTERO_EXCLUIR_TIPOS` (tipos de Zotero que no van a Publicaciones; por defecto `computerProgram,patent,thesis`: los registros de software y las patentes se listan en el informe para llevarlos a Transferencia).
3. **Permitir que Actions abra PR.** En `grys-web` → *Settings → Actions → General → Workflow permissions*, marca **Allow GitHub Actions to create and approve pull requests** y pulsa *Save*. Si la casilla sale en gris, la organización lo tiene bloqueado: actívala antes en `grys-upm` → *Settings → Actions → General* (misma casilla). Lo necesitan también los formularios de §9.
4. **Primera ejecución.** Lánzala a mano y revisa la PR. Lo normal es que aparezcan:
   - limpiezas de `keywords`;
   - pequeñas diferencias de formato en algunas entradas, porque el `.bib` actual viene de una exportación anterior;
   - lo que se haya cambiado en Zotero desde la migración.

Las comprobaciones de la PR se lanzan solas si está configurada la aplicación de §9; si no, hay que cerrarla y reabrirla una vez.
