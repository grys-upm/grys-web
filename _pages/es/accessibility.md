---
layout: page
lang: es
page_id: accessibility
permalink: /accesibilidad/
a11y_preparacion: 2026-10-18
a11y_revision: 2026-10-18
lead: "Queremos que cualquier persona pueda usar este sitio."
---
{%- comment -%}
  Declaración de accesibilidad (RD 1112/2018). Al cambiar el estado de
  cumplimiento o tras una revisión, actualiza «a11y_revision» en el front matter.
{%- endcomment -%}
{%- assign g = site.data.grupo -%}
El Grupo de Redes y Servicios de Próxima Generación (GRyS) de la Universidad Politécnica de Madrid se ha comprometido a hacer accesible este sitio web de conformidad con el [Real Decreto 1112/2018, de 7 de septiembre](https://www.boe.es/buscar/act.php?id=BOE-A-2018-12699), sobre accesibilidad de los sitios web y aplicaciones para dispositivos móviles del sector público.

Esta declaración se aplica al sitio web **{{ site.url | remove: "https://" }}**.

## Situación de cumplimiento

Este sitio web es **parcialmente conforme** con el RD 1112/2018 (requisitos de la norma UNE-EN 301549:2022, equivalentes a las WCAG 2.1 nivel AA), debido a las excepciones y la falta de conformidad que se indican a continuación. El objetivo del sitio es cumplir las **WCAG 2.2 nivel AA**.

## Contenido no accesible

**Falta de conformidad:**

- Algunas imágenes heredadas del sitio anterior todavía no tienen un texto alternativo descriptivo.

**Contenido que no entra en el ámbito de la legislación aplicable:**

- Vídeos de YouTube y mapas de OpenStreetMap incrustados, e insignias de Altmetric y Dimensions: son contenidos de terceros que el grupo no controla. Junto a cada uno se ofrece el enlace al servicio original y, en el caso del mapa, la dirección en texto.
- Documentos PDF publicados antes del 20 de septiembre de 2018.

## Qué hemos hecho

- Contraste de texto mínimo de 4,5:1 en modo claro y en modo oscuro, comprobado automáticamente en cada compilación del sitio.
- Modo oscuro por defecto y modo claro a un clic; la elección se recuerda.
- Tipografía Atkinson Hyperlegible, diseñada para personas con baja visión.
- Navegación completa con teclado, foco visible y enlace para saltar al contenido. Los menús, las pestañas y los filtros siguen los patrones de WAI-ARIA.
- La información nunca depende solo del color: los estados de los proyectos usan forma y texto.
- La cabecera fija no tapa el elemento que tiene el foco, y deja de ser fija cuando la pantalla tiene poca altura útil (por ejemplo, con un zoom del 400 %).
- Todo el contenido está en español y en inglés. Algunas traducciones de biografías, proyectos y noticias son provisionales hasta que el grupo las revise; se indica con un aviso, y el texto original se marca con su idioma para que los lectores de pantalla lo pronuncien bien.
- Se respeta la preferencia de movimiento reducido del sistema.
- El sitio funciona sin JavaScript: sin él, las pestañas se muestran como bloques seguidos y los filtros no aparecen.

## Preparación de esta declaración

Esta declaración se preparó el **{{ page.a11y_preparacion | date: "%d/%m/%Y" }}** mediante una **autoevaluación** del propio grupo. Cada cambio en el sitio se audita automáticamente antes de publicarse: reglas WCAG 2.2 A y AA con axe-core en modo claro y oscuro, adaptación a 320 px de ancho, recorrido completo con el teclado (foco visible y no tapado, sin trampas), contraste, estructura de encabezados, idioma, enlaces y texto alternativo. Además, se ha hecho una revisión manual con teclado, lector de pantalla y zoom siguiendo la lista de `docs/REVISION_ACCESIBILIDAD.md` del repositorio. Última revisión: **{{ page.a11y_revision | date: "%d/%m/%Y" }}**.

## Observaciones y datos de contacto

Puedes comunicarnos cualquier posible incumplimiento, dificultad de acceso al contenido o sugerencia de mejora escribiendo a <a href="mailto:{{ g.email }}">{{ g.email }}</a>. También puedes pedirnos cualquier contenido en un formato accesible.

## Procedimiento de aplicación

Si tu solicitud o queja no recibe respuesta, o no estás de acuerdo con ella, puedes presentar una reclamación ante la **Unidad Responsable de Accesibilidad de la Universidad Politécnica de Madrid**, como se explica en la [declaración de accesibilidad de la UPM](https://www.upm.es/UPM/WebUPM/Accesibilidad).
