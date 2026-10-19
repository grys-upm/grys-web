# Editar la web con el gestor de contenidos

Para miembros del grupo con cuenta de GitHub que pertenezcan al equipo **web** de la organización `grys-upm`. No hace falta saber Git ni Jekyll.

**Dirección:** `https://grys.etsist.upm.es/admin/` (mientras dure la fase de pruebas, `https://grys-upm.github.io/grys-web/admin/`).

Desde el gestor se editan **Noticias, Eventos, Convocatorias, Miembros y Proyectos**. El resto (líneas, ámbitos, textos de las páginas, publicaciones) lo mantiene quien administra la web: ver `docs/RECETAS.md`.

## ¿Qué quieres hacer?

| Quiero… | Cómo |
|---|---|
| Publicar una noticia, un evento o una convocatoria | Gestor → *Nueva* en su colección (§2), o un formulario (§5) |
| Dar de alta a una persona o un proyecto | Gestor → *Miembros* o *Proyectos* → *Nuevo* |
| Corregir algo que ya está en la web | Gestor → busca la ficha, cámbiala y publica |
| Marcar a alguien como antiguo miembro | Gestor → su ficha → *Situación: Antiguo miembro* y *En el grupo hasta* |
| Añadir o corregir una publicación | En Zotero (§6) |
| Cambiar el texto de una página fija (Quiénes somos, Contacto…), líneas, ámbitos, puestos | Pídelo al administrador (`docs/RECETAS.md`) |
| Avisar de un error en la web | *Issues → New issue → Blank issue* |

**Vocabulario:**
- **Propuesta de cambios (PR, *pull request*):** un cambio guardado que todavía no está en la web. Tiene sus comprobaciones y su vista previa.
- **Publicar:** fusionar la propuesta; la web se actualiza en 2–3 minutos.
- **Issue:** una petición o aviso en el repositorio de GitHub; los formularios crean una.
- **Comprobaciones:** revisión automática de datos, enlaces y accesibilidad. Si fallan, el cambio no se puede publicar.

## 1. Entrar

- **Con el botón «Iniciar sesión con GitHub»**, si el administrador ya ha configurado el inicio de sesión (`docs/COMPILAR.md` §8).
- **Si solo aparece «Iniciar sesión con token»:** pulsa el botón y sigue el enlace a GitHub, que ya trae marcados los permisos necesarios. Crea el token, cópialo y pégalo en el gestor. El navegador lo recuerda; no lo compartas con nadie.

Si al guardar aparece un error de permisos, pide al administrador que te añada al equipo **web**.

## 2. Cómo se publica un cambio

Ningún cambio llega a la web hasta que se **publica**, y antes pasa por las mismas comprobaciones que cualquier otro:

1. **Guardar.** El gestor crea una «propuesta de cambios» (PR) con tu cambio. Puedes guardar tantas veces como quieras.
2. **Comprobaciones y vista previa (2–5 minutos).** GitHub comprueba los datos, compila la web y revisa la accesibilidad. Después aparece en el gestor el enlace **«Ver vista previa»**, con la página tal como quedará.
3. **Publicar.** Pon el estado en **«Listo»** y pulsa **«Publicar»**.
   - Si las comprobaciones han terminado bien, el cambio se publica (la web se actualiza en 2–3 minutos).
   - Si todavía están en marcha, queda programado y se publica solo cuando terminen.
   - **Si alguna comprobación falla, no se publica.** El enlace de la PR (en «Página de Flujo editorial» → la ficha) lleva al detalle; normalmente es un dato con formato incorrecto. Corrígelo, guarda y vuelve a publicar. Si no sabes qué pasa, avisa al administrador.

En **«Flujo editorial»** ves todos los cambios guardados y aún sin publicar, en columnas (Borrador, En revisión, Listo). Desde ahí también puedes **descartar** un cambio.

## 3. Lo que conviene saber

- **Los dos idiomas.** Cada ficha tiene título en español y en inglés. El texto largo se escribe en un idioma (campo «Idioma en que está escrito el texto») y, si puedes, se añade la traducción en «Traducción al…». Si la traducción no está revisada, marca «Borrador»: la web muestra un aviso.
- **Imágenes.**
  - Se convierten solas a WebP y se reducen al subirlas.
  - **Describe siempre la imagen** en el campo de descripción: lo que verías si no pudieras verla. Solo si es decorativa, déjalo vacío.
  - En el texto, usa el botón **«Imagen con pie»**; para vídeos, **«Vídeo de YouTube»** (pide el identificador del vídeo y un título).
- **Encabezados del texto:** empieza por «Título 2» y no te saltes niveles (de Título 2 a Título 4).
- **Campos «(avanzado)»:** no los toques salvo que sepas para qué sirven. «Direcciones antiguas» mantiene funcionando los enlaces de la web anterior.
- **Convocatorias:** dejan de publicarse solas cuando pasa el plazo.
- **Eventos:** pasan de «Próximos» a «Pasados» solos, según la fecha.
- **Borrar una ficha** también crea una propuesta de cambios que hay que publicar.

## 4. Si algo va mal

- **No veo «Publicar»:** el estado tiene que estar en «Listo».
- **«No se pudo publicar»:** alguna comprobación ha fallado o aún no ha empezado. Espera un par de minutos y vuelve a intentarlo; si sigue, mira el detalle en la PR.
- **He publicado algo por error:** edita la ficha y publica la corrección, o pide al administrador que deshaga el cambio (todo queda en el historial de GitHub y se puede recuperar).

## 5. Sin entrar en el gestor: los formularios

Para **crear** una noticia, un evento, una convocatoria, un miembro o un proyecto también puedes usar un formulario de GitHub. Es útil desde el móvil, o si prefieres que otra persona lo revise.

1. **Elegir el formulario.** En el repositorio `grys-web`, abre la pestaña *Issues*, pulsa *New issue* y elige el formulario.
2. **Rellenarlo.** Las imágenes y el PDF se **arrastran** a su casilla; se descargan y se convierten solas. En las noticias, escribe una descripción por imagen, en el mismo orden.
3. **Enviar.** Pulsa *Submit new issue*. Un par de minutos después aparece un comentario:
   - ✅ con el enlace a la **propuesta de cambios** (con comprobaciones y vista previa). Al fusionarla se publica y la issue se cierra sola;
   - ❌ con lo que hay que corregir. **Edita la issue** (⋯ → *Edit*) y la propuesta se rehace.
4. **Sin permiso de edición.** Si no estás en el equipo `web`, la issue queda pendiente hasta que alguien del equipo la revise y le añada la etiqueta **generar-pr**.

Los formularios solo **crean** contenido nuevo. Para cambiar algo que ya existe, usa el gestor.

## 6. Publicaciones

Las publicaciones no se editan aquí: se añaden en la **biblioteca de Zotero del grupo**. Cada lunes se sincronizan solas, y se abre una propuesta de cambios para revisarlas. Para que una publicación salga en la ficha de un proyecto o de una línea, ponle en Zotero las etiquetas `proyecto:nextarc`, `linea:iot`…

## 7. Por qué no se puede publicar «directamente»

La rama principal del repositorio (`main`) está protegida: todo cambio entra por una propuesta que tiene que pasar las comprobaciones. Así ningún error (una fecha mal escrita, un enlace roto, una imagen sin descripción) llega a la web, y cualquier cambio se puede deshacer. Para ti no supone ningún paso más: el gestor y los formularios crean la propuesta por su cuenta.
