# Mantener la web (administradores)

Para quien administra el repositorio `grys-web`. Las tareas de los editores están en [EDITAR.md](EDITAR.md); la puesta en marcha de cada pieza, en [COMPILAR.md](COMPILAR.md).

## 1. Qué llega solo y qué hay que hacer

| Cuándo | Qué llega | Qué hacer |
|---|---|---|
| Cada vez que un editor guarda en el gestor o envía un formulario | Una PR (`cms/…` o `contenido/issue-N`) | Normalmente nada: el editor la publica. Si las comprobaciones fallan y no sabe resolverlo, ayúdale. Si la PR viene de un formulario y no está la aplicación de COMPILAR §9, ciérrala y reábrela para lanzar las comprobaciones |
| Lunes, 05:45 UTC | PR «Publicaciones: sincronización con Zotero» (solo si hay cambios) | Leer el informe: nuevas, con cambios, borradas, «no son publicaciones». Cerrar y reabrir para lanzar las comprobaciones (si no está la aplicación), mirar la vista previa y fusionar |
| Lunes, 06:30 UTC | Issue «Enlaces rotos» (solo si hay) | Corregir las URL en el contenido, cambiarlas por una copia de archive.org o, si el sitio bloquea robots, añadirlo a `exclude` en `lychee.toml`. La issue se cierra sola |
| Cada día, 05:15 UTC | Nueva compilación (sin PR) | Nada. Reclasifica eventos (próximos/pasados) y retira convocatorias vencidas. Las métricas de citas se actualizan cada 7 días |
| Una vez al mes | Hasta 3 PR de Dependabot (acciones, gemas, auditoría) | Si «Comprobar PR» está en verde, fusionar. Si falla, no fusionar: suele ser un cambio de versión que hay que adaptar |
| Cuando lleguen | Alertas de seguridad de Dependabot | Revisarlas en *Security*. La mayoría se resuelven fusionando la PR que el propio Dependabot abre |
| Una vez al año (y al cambiar una plantilla) | — | Revisión manual de accesibilidad (`docs/REVISION_ACCESIBILIDAD.md`) y fecha `a11y_revision` en las dos declaraciones |
| Una vez al año | — | Repasar `_data/metrics.yml` (cifras de Scopus y tesis) y `PENDIENTES.md` |

Si una ejecución programada falla, GitHub envía un correo a quien la configuró. El detalle está en *Actions*, en la ejecución en rojo.

## 2. Protección de la rama `main`

Nadie (ni el gestor, ni los formularios, ni las personas) escribe directamente en `main`: todo entra por una PR que tiene que pasar «Comprobar PR» (job `build`).

Las reglas están en `.github/rulesets/main.json`:

| Regla | Para qué |
|---|---|
| No se puede borrar `main` | Evita perder la web por error |
| No se puede reescribir el historial (*force push*) | El historial es la copia de seguridad: todo cambio se puede deshacer |
| Todo cambio entra por PR, sin aprobación obligatoria | Las comprobaciones y la vista previa se ejecutan siempre; no hace falta una segunda persona para publicar una noticia |
| La comprobación `build` tiene que estar en verde | Ningún dato roto, enlace interno roto ni fallo de accesibilidad llega a la web |
| Los administradores pueden saltárselo **solo en una PR** | Para una urgencia (p. ej. si una comprobación falla por un servicio externo caído): en la PR aparece *Merge without waiting for requirements to be met*. Nunca permite escribir directamente en `main` |

**Activarla (una vez):** en `grys-web` → *Settings → Rules → Rulesets → New ruleset → Import a ruleset*, elige `.github/rulesets/main.json` (descárgalo antes del repositorio) y pulsa *Create*.

- Si ya creaste antes una regla a mano para `main`, bórrala o compárala con esta: dos reglas a la vez se suman.
- Si la importación da error, créala a mano con los valores de la tabla. En *Require status checks to pass* añade `build` y elige como origen **GitHub Actions**.

**Comprobarla:** intenta `git push` directamente a `main` con un cambio cualquiera. ✅ Debe rechazarlo con «Changes must be made through a pull request».

`comprobar_datos.py` avisa si la comprobación que exige el fichero ya no existe en `pr.yml` (por ejemplo, si alguien renombra el job): en ese caso ninguna PR se podría fusionar.

## 3. Personas y permisos

| Quién | Cómo | Puede |
|---|---|---|
| **Editores** | Equipo `web` de la organización, rol *Write* en `grys-web` | Usar el gestor, generar PR desde formularios, fusionar PR en verde |
| **Administradores** | Rol *Admin* en `grys-web` | Todo lo anterior, cambiar la configuración, secretos y reglas, fusionar en urgencias |
| Resto de miembros de la organización | Permiso base *Read* | Ver el repositorio y proponer contenido con un formulario (alguien del equipo `web` añade la etiqueta `generar-pr`) |

**Alta de un editor:** añádelo al equipo `web` (*grys-upm → Teams → web → Add a member*) y envíale [EDITAR.md](EDITAR.md).

**Baja:** quítalo del equipo. Si entraba al gestor con token, el token deja de servir al perder el permiso; pídele que lo borre en GitHub (*Settings → Developer settings → Personal access tokens*).

## 4. Secretos y variables

En `grys-web` → *Settings → Secrets and variables → Actions*. Ninguno es imprescindible para publicar: sin ellos, la pieza correspondiente se salta con un aviso.

| Nombre | Tipo | Para qué | Dónde se explica |
|---|---|---|---|
| `PREVIEW_DEPLOY_KEY` | secreto | Publicar la vista previa de cada PR en `grys-web-previews` | COMPILAR §5 |
| `PREVIEW_REPO` | variable | Otro repositorio de vistas previas (opcional) | COMPILAR §5 |
| `CONTENIDO_APP_ID` / `CONTENIDO_APP_KEY` | variable / secreto | Que las PR de formularios y Zotero lancen solas las comprobaciones | COMPILAR §9 |
| `ZOTERO_API_KEY` | secreto | Leer la biblioteca de Zotero si es privada | COMPILAR §10 |
| `ZOTERO_GRUPO`, `ZOTERO_COLECCION`, `ZOTERO_EXCLUIR_TIPOS` | variables | Ajustes de la sincronización (opcionales) | COMPILAR §10 |

Fuera de GitHub: el autenticador del gestor (Cloudflare Workers y aplicación OAuth de la organización, COMPILAR §8.3) y la dirección `cms.oauth_url` de `_config.yml`.

**Si se filtra una clave:** bórrala en su origen (clave de despliegue, clave privada de la aplicación, clave de Zotero), crea otra y sustituye el secreto. Los secretos nunca aparecen en los registros de Actions.

## 5. Deshacer un cambio

Todo lo publicado está en el historial y se puede deshacer:

1. **Localiza el cambio.** Abre la PR fusionada (*Pull requests → Closed*).
2. **Deshazlo.** Pulsa **Revert**: se crea una PR nueva que deshace el cambio. Fusiónala cuando pase las comprobaciones.
3. **Si hace falta urgencia**, un administrador puede fusionarla sin esperar (§2).

Para recuperar un fichero borrado sin deshacer nada más: en GitHub, abre el historial de la carpeta (*History*), busca el commit anterior al borrado y copia su contenido en una PR nueva (o pide al editor que lo vuelva a crear en el gestor).

## 6. Si algo deja de funcionar

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Ninguna PR se puede fusionar: «Expected — Waiting for status to be reported» | Se ha renombrado el job `build` de `pr.yml` o se ha desactivado el flujo | Restaurar el nombre o cambiar la regla (§2) |
| El gestor muestra un error de configuración | `admin/config.yml` mal generado | Mirar «Comprobar PR» de la última PR fusionada; `verificar_sitio.py` lo detecta |
| El gestor no deja entrar con GitHub | El autenticador de Cloudflare o la aplicación OAuth | COMPILAR §8.3; mientras tanto, entrar con token |
| «GitHub Actions is not permitted to create pull requests» | Permiso de Actions desactivado | COMPILAR §10, punto 3 |
| La web no se actualiza tras fusionar | Falló «Compilar y publicar» | *Actions* → la ejecución en rojo; si es un fallo temporal, *Re-run jobs* |
| La sincronización con Zotero falla | Zotero caído, clave caducada o se detuvo por seguridad | El informe de la ejecución lo dice. Si borraría muchas publicaciones, revisar Zotero antes de usar «Permitir borrados» |
