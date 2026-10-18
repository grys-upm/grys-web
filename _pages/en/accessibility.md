---
layout: page
lang: en
page_id: accessibility
permalink: /accessibility/
a11y_preparacion: 2026-10-18
a11y_revision: 2026-10-18
lead: "We want everyone to be able to use this site."
---
{%- comment -%}
  Accessibility statement (Spanish Royal Decree 1112/2018). After a review or
  a change in compliance status, update «a11y_revision» in the front matter.
{%- endcomment -%}
{%- assign g = site.data.grupo -%}
The Next-Generation Networks and Services Group (GRyS) at Universidad Politécnica de Madrid is committed to making this website accessible in accordance with Spanish [Royal Decree 1112/2018 of 7 September](https://www.boe.es/buscar/act.php?id=BOE-A-2018-12699) on the accessibility of public-sector websites and mobile applications, which transposes Directive (EU) 2016/2102.

This statement applies to the website **{{ site.url | remove: "https://" }}**.

## Compliance status

This website is **partially compliant** with Royal Decree 1112/2018 (requirements of standard EN 301 549, equivalent to WCAG 2.1 level AA) due to the exceptions and non-conformities listed below. The site aims to meet **WCAG 2.2 level AA**.

## Non-accessible content

**Non-conformities:**

- Some images inherited from the previous site do not yet have a descriptive text alternative.

**Content outside the scope of the applicable legislation:**

- Embedded YouTube videos and OpenStreetMap maps, and Altmetric and Dimensions badges: third-party content not controlled by the group. A link to the original service is provided next to each one and, for the map, the address is also given as text.
- PDF documents published before 20 September 2018.

## What we have done

- Minimum 4.5:1 text contrast in both light and dark mode, checked automatically every time the site is built.
- Dark mode by default and light mode one click away; your choice is remembered.
- Atkinson Hyperlegible typeface, designed for people with low vision.
- Full keyboard navigation, visible focus and a skip link. Menus, tabs and filters follow WAI-ARIA patterns.
- Information never relies on colour alone: project status uses shape and text.
- The sticky header never hides the element with keyboard focus, and it stops being sticky when the screen has little height available (for example, at 400% zoom).
- All content is available in Spanish and English. Some Spanish translations of biographies, projects and news are provisional until the group reviews them; this is indicated with a notice, and the original text is marked with its language so that screen readers pronounce it correctly.
- Your system's reduced-motion preference is respected.
- The site works without JavaScript: tabs are shown as consecutive blocks and filters are hidden.

## Preparation of this statement

This statement was prepared on **{{ page.a11y_preparacion | date: "%d/%m/%Y" }}** through a **self-assessment** by the group. Every change to the site is audited automatically before publication: WCAG 2.2 A and AA rules with axe-core in light and dark mode, reflow at 320 px width, a full keyboard walk-through (visible, unobscured focus and no keyboard traps), contrast, heading structure, language, links and text alternatives. A manual review with keyboard, screen reader and zoom has also been carried out, following the checklist in `docs/REVISION_ACCESIBILIDAD.md` in the repository. Last reviewed: **{{ page.a11y_revision | date: "%d/%m/%Y" }}**.

## Feedback and contact details

You can report any possible non-compliance, difficulty accessing content or suggestion for improvement by writing to <a href="mailto:{{ g.email }}">{{ g.email }}</a>. You can also ask us for any content in an accessible format.

## Enforcement procedure

If your request or complaint receives no answer, or you disagree with it, you can file a complaint with the **Accessibility Unit of Universidad Politécnica de Madrid**, as explained in the [UPM accessibility statement](https://www.upm.es/UPM/WebUPM/Accesibilidad) (in Spanish).
