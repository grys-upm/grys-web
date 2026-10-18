# Revisión manual de accesibilidad (WCAG 2.2 AA)

Lo que las comprobaciones automáticas de cada PR **no** pueden decidir. Se hace sobre la vista previa o el sitio publicado, **en español y en inglés**, al menos:
- antes de la puesta en producción;
- una vez al año (el RD 1112/2018 pide revisar la declaración anualmente);
- cuando cambie una plantilla o un componente.

Al terminar, actualiza `a11y_revision` en `_pages/es/accessibility.md` y `_pages/en/accessibility.md`. Si algo no se cumple y no se puede corregir enseguida, añádelo a «Falta de conformidad» en las dos declaraciones.

**Cómo usar esta lista:** copia la tabla de resultados del final en una *issue* titulada «Revisión de accesibilidad AAAA-MM-DD» y marca cada punto. Basta con unos 60–90 minutos.

## Páginas de muestra

Una de cada plantilla, en los dos idiomas:

| Plantilla | Español | Inglés |
|---|---|---|
| Portada | `/` | `/en/` |
| Pestañas | `/grupo/equipo/` · `/investigacion/tesis/` | `/en/group/team/` · `/en/research/theses/` |
| Filtros y tabla | `/investigacion/proyectos/` · `/investigacion/publicaciones/` | `/en/research/projects/` · `/en/research/publications/` |
| Ficha con vídeo y galería | `/investigacion/proyectos/woo/` · una noticia con galería | ídem en `/en/` |
| Ficha de miembro | `/grupo/equipo/nestor-lucas-martinez/` | ídem en `/en/` |
| Contacto con mapa | `/grupo/contacto/` | `/en/group/contact/` |
| Buscador | cualquier página, tecla `/` | ídem |

## Herramientas (gratuitas)

- **Teclado:** el del ordenador, sin ratón.
- **Lector de pantalla:** NVDA + Firefox o Chrome (Windows), o VoiceOver + Safari (macOS: `Cmd+F5`). En el móvil, TalkBack (Android) o VoiceOver (iOS).
- **Zoom:** el del navegador (`Ctrl/Cmd` y `+`), hasta el 200 % y el 400 %.
- **Colores forzados:** en Windows, Configuración → Accesibilidad → Temas de contraste. Como alternativa, en Chrome: DevTools → Rendering → «Emulate CSS media feature forced-colors».
- **Espaciado de texto (1.4.12):** el *bookmarklet* «Text spacing» de Steve Faulkner.

## 1. Teclado (2.1.1, 2.1.2, 2.4.3, 2.4.7, 2.4.11)

| # | Prueba | Resultado esperado |
|---|---|---|
| T1 | Carga la página y pulsa `Tab` una vez | Aparece «Saltar al contenido»; con `Intro`, el foco pasa al contenido principal |
| T2 | Recorre toda la página con `Tab` y `Mayús+Tab` | El orden sigue el visual: cabecera, menú, contenido y pie. El indicador de foco se ve siempre y la cabecera fija no lo tapa |
| T3 | Menú principal: `Intro` o `Espacio` en un apartado | Se abre el submenú y el foco va al primer enlace. `Esc` lo cierra y el foco vuelve al botón. Al salir con `Tab`, el submenú se cierra |
| T4 | Pestañas (Equipo, Tesis) | `←` y `→` cambian de pestaña, e `Inicio` y `Fin` van a la primera y a la última. `Tab` entra en el panel |
| T5 | Filtros (Proyectos, Publicaciones) | Se pueden usar todos con el teclado. El recuento de resultados se anuncia y la URL cambia |
| T6 | Buscador: tecla `/` y luego `Esc` | Se abre con el foco en el campo y las flechas recorren los resultados. `Esc` lo cierra y el foco vuelve a donde estaba |
| T7 | Vídeo y mapa incrustados | Se puede entrar y salir con `Tab` (no hay trampa) y el enlace al servicio original es accesible |
| T8 | Cambio de tema e idioma | Funcionan con `Intro`. El cambio de idioma lleva a la página equivalente |

## 2. Lector de pantalla (1.1.1, 1.3.1, 2.4.2, 2.4.6, 3.1.1, 3.1.2, 4.1.2, 4.1.3)

| # | Prueba | Resultado esperado |
|---|---|---|
| L1 | Lista de encabezados (NVDA `Ins+F7`; VoiceOver: rotor) | Hay un solo H1, que coincide con el título de la página, y los niveles no se saltan |
| L2 | Lista de regiones | Hay cabecera, navegación, principal y pie, y las navegaciones tienen nombres distintos |
| L3 | Lista de enlaces | Cada enlace se entiende fuera de contexto: no hay varios «aquí» o «más» sin más información |
| L4 | Imágenes de fichas y galerías | El texto alternativo describe la imagen. Las decorativas no se anuncian |
| L5 | Página en español con un texto original en inglés (o al revés) | Se lee con la pronunciación del idioma correcto y se anuncia el aviso de idioma o de traducción provisional |
| L6 | Pestañas, menús y botones de filtro | Se anuncian el rol y el estado: «pestaña, seleccionada, 1 de 3», «contraído/expandido», «pulsado» |
| L7 | Filtrar y buscar | El número de resultados se anuncia sin mover el foco (4.1.3) |
| L8 | Título de la pestaña del navegador | Es único y descriptivo en cada página e idioma |

## 3. Zoom, adaptación y visualización (1.4.4, 1.4.10, 1.4.11, 1.4.12, 1.4.13)

| # | Prueba | Resultado esperado |
|---|---|---|
| Z1 | Zoom al 200 % | No se pierde ni se corta contenido ni funcionalidad |
| Z2 | Zoom al 400 % (equivale a 320 px de ancho) | No hay desplazamiento horizontal (salvo en tablas de datos), el menú pasa a un botón y la cabecera no tapa el contenido |
| Z3 | Espaciado de texto (*bookmarklet*) | No se solapan ni se cortan textos |
| Z4 | Colores forzados (alto contraste de Windows) | Se ven los bordes de botones y campos y el indicador de foco. Los estados de proyecto se distinguen por la forma y el texto |
| Z5 | Contenido que aparece al pasar el ratón o al enfocar (submenús) | Se puede cerrar con `Esc`, se puede pasar el ratón por encima sin que desaparezca y no se oculta solo |
| Z6 | Contraste de elementos no textuales (bordes de campos, iconos con significado, foco) | Tienen al menos 3:1 en los dos temas |

## 4. Criterios nuevos de WCAG 2.2

| # | Criterio | Prueba | Resultado esperado |
|---|---|---|---|
| N1 | 2.4.11 Foco no tapado | Con `Mayús+Tab` desde el pie hacia arriba y con zoom al 200 % | El elemento con el foco nunca queda debajo de la cabecera fija. Esto también lo comprueba la auditoría automática |
| N2 | 2.5.7 Movimientos de arrastre | Busca cualquier función que requiera arrastrar | No hay ninguna. En el mapa de OpenStreetMap, de terceros, los botones `+`/`−` sirven como alternativa |
| N3 | 2.5.8 Tamaño del objetivo | En móvil, pulsa los enlaces del pie, los botones de idioma y tema y los filtros | Todos miden al menos 24×24 px o están bien separados. axe lo comprueba en cada PR |
| N4 | 3.2.6 Ayuda coherente | Compara varias páginas | El correo y el enlace a Contacto están en el pie, en el mismo sitio, en todas las páginas |
| N5 | 3.3.7 Entrada redundante | Formularios con varios pasos | No hay ninguno (no aplica) |
| N6 | 3.3.8 Autenticación accesible | Inicio de sesión | No hay (no aplica). El gestor de contenidos de la fase 5 usa la cuenta de GitHub, fuera del sitio público |

## 5. Contenido (lo que no ve ninguna herramienta)

| # | Prueba | Resultado esperado |
|---|---|---|
| C1 | Vídeos con voz | Tienen subtítulos, aunque sean los automáticos de YouTube revisados, o una transcripción enlazada (1.2.2) |
| C2 | PDF enlazados posteriores a 2018 | Están etiquetados (accesibles) o tienen una alternativa en HTML |
| C3 | Textos de enlaces en el contenido (noticias, fichas) | No hay «aquí» ni URL desnudas largas como texto del enlace |
| C4 | Traducciones provisionales | Quedan pocas, o al menos ninguna en las páginas principales |

## Plantilla de resultados (copiar en la *issue*)

```
Revisión de accesibilidad · fecha: AAAA-MM-DD · quién: …
Navegadores / lectores usados: …

Teclado:     T1 [ ] T2 [ ] T3 [ ] T4 [ ] T5 [ ] T6 [ ] T7 [ ] T8 [ ]
Lector:      L1 [ ] L2 [ ] L3 [ ] L4 [ ] L5 [ ] L6 [ ] L7 [ ] L8 [ ]
Zoom/vista:  Z1 [ ] Z2 [ ] Z3 [ ] Z4 [ ] Z5 [ ] Z6 [ ]
WCAG 2.2:    N1 [ ] N2 [ ] N3 [ ] N4 [ ] N5 n/a N6 n/a
Contenido:   C1 [ ] C2 [ ] C3 [ ] C4 [ ]

Problemas encontrados (página · prueba · qué pasa):
- …
```
