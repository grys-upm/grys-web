---
layout: page
lang: en
page_id: privacy
permalink: /privacy/
privacidad_revision: 2026-10-18
lead: "This site does not use tracking cookies."
---
{%- comment -%}
  Privacy policy. scripts/verificar_sitio.py checks that every localStorage key
  used by the site and every external service loaded in iframes or scripts is
  mentioned here. If you add one, explain it here.
{%- endcomment -%}
{%- assign g = site.data.grupo -%}
**This site does not use cookies or any analytics or tracking tools.** Fonts and all our own resources are served from this same site.

## What is stored in your browser

Only two preferences, in your browser's local storage (`localStorage`). They are never sent to any server, and you can delete them at any time from your browser settings:

| Key | Purpose | When it is stored |
|---|---|---|
| `grys-theme` | Remember the theme (light or dark) | When you press the theme button |
| `grys-metrics` | Remember whether you want to see impact metrics | When you press “Show impact metrics” in Publications |

The language is not stored: it is part of the page address (`/en/` for English).

## Hosting

This is a static site hosted on **GitHub Pages**. Like any web server, GitHub may log visitors' IP addresses for security and operational purposes, as described in its [privacy statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).

## Third-party content

Some pages include content from other services. When it loads, your browser connects to them, and they process data under their own policies:

- **YouTube videos** (news, projects and OpenTech Lab), in privacy-enhanced mode (`youtube-nocookie.com`). When you play a video, [Google's privacy policy](https://policies.google.com/privacy?hl=en) applies.
- **OpenStreetMap map** (Contact). The [OpenStreetMap Foundation privacy policy](https://osmfoundation.org/wiki/Privacy_Policy) applies.
- **Altmetric and Dimensions badges** (Publications). **They are only loaded if you press “Show impact metrics”**. The [Altmetric](https://www.altmetric.com/privacy-policy/) and [Dimensions](https://www.dimensions.ai/privacy/) policies apply.

Links to other sites (DOI, Scientific Portal, Google Scholar, GitHub, etc.) only take you there if you click them.

## If you write to us

If you write to <a href="mailto:{{ g.email }}">{{ g.email }}</a>, we will use your data only to reply to you. The data controller is **Universidad Politécnica de Madrid** (C. Ramiro de Maeztu, 7, 28040 Madrid, Spain). You can contact its Data Protection Officer at <a href="mailto:proteccion.datos@upm.es">proteccion.datos@upm.es</a> and exercise your rights of access, rectification, erasure, objection, restriction and portability as explained on the [UPM e-office](https://sede.upm.es/proteccion-datos) (in Spanish). If you are not satisfied, you can lodge a complaint with the [Spanish Data Protection Agency (AEPD)](https://www.aepd.es/).
