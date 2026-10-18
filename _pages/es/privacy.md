---
layout: page
lang: es
page_id: privacy
permalink: /privacidad/
privacidad_revision: 2026-10-18
lead: "Este sitio no usa cookies de seguimiento."
---
{%- comment -%}
  Política de privacidad. scripts/verificar_sitio.py comprueba que aquí se
  mencionan todas las claves de localStorage que usa el sitio y todos los
  servicios externos que se cargan en iframes o scripts. Si añades uno, explícalo aquí.
{%- endcomment -%}
{%- assign g = site.data.grupo -%}
**Este sitio no usa cookies ni herramientas de analítica o seguimiento.** Las fuentes tipográficas y todos los recursos propios se sirven desde el mismo sitio.

## Qué se guarda en tu navegador

Solo dos preferencias, en el almacenamiento local del navegador (`localStorage`). No se envían a ningún servidor y puedes borrarlas cuando quieras desde la configuración del navegador:

| Clave | Para qué | Cuándo se guarda |
|---|---|---|
| `grys-theme` | Recordar el tema (claro u oscuro) | Al pulsar el botón de cambio de tema |
| `grys-metrics` | Recordar si quieres ver las métricas de impacto | Al pulsar «Mostrar métricas de impacto» en Publicaciones |

El idioma no se guarda: va en la dirección de la página (`/en/` para el inglés).

El **buscador** funciona dentro de tu navegador: descarga un índice del propio sitio y lo que escribes no se envía a ningún servidor.

## Alojamiento

El sitio es estático y está alojado en **GitHub Pages**. Como cualquier servidor web, GitHub puede registrar la dirección IP de los visitantes por motivos de seguridad y funcionamiento, según su [declaración de privacidad](https://docs.github.com/es/site-policy/privacy-policies/github-general-privacy-statement).

## Contenidos de terceros

Algunas páginas incluyen contenidos de otros servicios. Al cargarlos, tu navegador se conecta con ellos, que tratan los datos según sus propias políticas:

- **Vídeos de YouTube** (noticias, proyectos y OpenTech Lab), en el modo de privacidad mejorada (`youtube-nocookie.com`). Al reproducir un vídeo se aplica la [política de privacidad de Google](https://policies.google.com/privacy?hl=es).
- **Mapa de OpenStreetMap** (Contacto). Se aplica la [política de privacidad de la Fundación OpenStreetMap](https://osmfoundation.org/wiki/Privacy_Policy).
- **Insignias de Altmetric y Dimensions** (Publicaciones). **Solo se cargan si pulsas «Mostrar métricas de impacto»**. Se aplican las políticas de [Altmetric](https://www.altmetric.com/privacy-policy/) y [Dimensions](https://www.dimensions.ai/privacy/).

Los enlaces a otros sitios (DOI, Portal Científico, Google Scholar, GitHub, etc.) solo te llevan allí si los pulsas.

## Si nos escribes

Si nos escribes a <a href="mailto:{{ g.email }}">{{ g.email }}</a>, usaremos tus datos solo para responderte. El responsable del tratamiento es la **Universidad Politécnica de Madrid** (C. Ramiro de Maeztu, 7, 28040 Madrid). Puedes contactar con su Delegado de Protección de Datos en <a href="mailto:proteccion.datos@upm.es">proteccion.datos@upm.es</a> y ejercer tus derechos de acceso, rectificación, supresión, oposición, limitación y portabilidad como se indica en la [sede electrónica de la UPM](https://sede.upm.es/proteccion-datos). Si no quedas satisfecho, puedes reclamar ante la [Agencia Española de Protección de Datos](https://www.aepd.es/).
