# Informe de la migración desde al-folio

Generado por `migrar_desde_alfolio.py` el 2026-10-16.

## Datos contradictorios en el origen (2)

- `_projects/swarms.md`: fecha end: front matter 2018-06-30 y tabla 2018-07-31; se usa la del front matter
- `_projects/woo.md`: fecha end: front matter 2013-01-12 y tabla 2013-12-31; se usa la del front matter

## Correcciones aplicadas (6)

- `_projects/accus.md`: errata «European Comission» → «European Commission»
- `_projects/demanes.md`: errata «European Comission» → «European Commission»
- `_projects/swarms.md`: errata «European Comission» → «European Commission»
- `_projects/woo.md`: errata «European Comission» → «European Commission»
- `_projects/afaredge.md`: referencia europea 101252360-2 → 101252360 (CORDIS)
- `_opportunities/2026-07-22-humami-job.md`: plazo 2026-08-05 23:00:00 +0200 → 2026-08-06 23:00:00 +0200 (confirmado: 6 de agosto de 2026)

## Decisiones que conviene revisar (22)

- `_members/mario-san-emeterio-de-la-parte.md`: enlace interno /projects/afarcloud/ → ficha projects/afarcloud
- `_members/mario-san-emeterio-de-la-parte.md`: enlace interno /projects/demeter/ → ficha projects/demeter
- `_members/vicente-hernandez-diaz.md`: enlace interno /projects/demeter/ → ficha projects/demeter
- `_members/vicente-hernandez-diaz.md`: enlace interno /projects/afarcloud/ → ficha projects/afarcloud
- `_members/vicente-hernandez-diaz.md`: enlace interno /projects/swarms/ → ficha projects/swarms
- `_projects/afarcloud.md`: se han corregido erratas del texto original («recived», «th European»)
- `_projects/nextarc.md`: rol «partner» deducido de «Coordinated by: Mälardalen University»
- `_projects/nextarc.md`: web oficial https://nextarc.eu tomada de la noticia del 24-04-2026
- `_projects/simgeosev.md`: el responsable en la UPM («María Castro Malpica (Group of Highway Engineering R&D - ICID-UPM)») no es del grupo: ¿GRyS participa como equipo de trabajo de otro grupo? Rol sin asignar
- `_events/2025-11-05-tech-hub-6g-madrid-2025.md`: tipo «tech_hub» → «fair» (lista cerrada del esquema)
- `_events/2025-11-20-car-csic-industry-day-2025.md`: tipo «industry_day» → «fair» (lista cerrada del esquema)
- `_events/2025-11-20-car-csic-industry-day-2025.md`: enlazado con la noticia del mismo día (2025-11-27-car-csic-industry-day-2025)
- `_events/2026-01-12-nextarc-workshop-2026-madrid.md`: el enlace del evento apunta a una página de la web anterior que no existe: https://grys.etsist.upm.es/events/nextarc-workshop-madrid-2026; se quita
- `_events/2026-01-12-nextarc-workshop-2026-madrid.md`: enlazado con la noticia del mismo día (2026-01-27-nextarc-workshop)
- `_events/2026-03-18-upm-investiga-2026.md`: tipo «upm_investiga» → «fair» (lista cerrada del esquema)
- `_events/2026-03-18-upm-investiga-2026.md`: enlazado con la noticia del mismo día (2026-03-18-upm-investiga)
- `_events/2026-04-04-coitt-awards-2025.md`: tipo «award_ceremony» → «award» (lista cerrada del esquema)
- `_events/2026-04-04-coitt-awards-2025.md`: participación «honored_guest» → «guest»
- `_events/2026-04-04-coitt-awards-2025.md`: enlazado con la noticia del mismo día (2026-04-24-estela-professional-association-awards)
- `_opportunities/2025-05-20-ai-edge-agriculture-scholarship.md`: el título decía «June 1, 2025 at 12:00 PM (CEST)» y el campo deadline «2025-06-01 12:00:00 +0200»; se mantiene el campo
- `_opportunities/2025-09-22-nextarc-job-offer.md`: el título decía «October 21, 2025 at 11:00 PM (CEST)» y el campo deadline «2025-10-21 11:00:00 +0200»; se mantiene el campo
- `_opportunities/2026-07-22-afaredge-job.md`: el título decía «August 6, 2026 at 11:00 PM (CEST)» y el campo deadline «2026-08-05 23:00:00 +0200»; se mantiene el campo

## Contenido de demostración eliminado (1)

- `_projects/afarcloud.md`: eliminada la plantilla de ejemplo de al-folio (texto «Every project has a beautiful feature showcase page», imágenes 1.jpg…11.jpg y cita einstein1950meaning)

## Datos que faltan (6)

- `_projects/afaredge.md`: creado desde la convocatoria; falta la descripción
- `_projects/humami.md`: falta el nombre del responsable en la UPM (pi_name; no es del grupo)
- `_projects/humami.md`: creado desde la convocatoria; falta la descripción
- `_data/repos.yml`: Data-Access-Manager_Data-Query: sin lenguaje ni descripción (no estaba en el mockup)
- `_data/repos.yml`: DEMETER-enabler-Data-Query-Interoperability-enabler: sin lenguaje ni descripción (no estaba en el mockup)
- `_data/repos.yml`: STS_DataModel_IoT: sin lenguaje ni descripción (no estaba en el mockup)

## Traducciones que faltan (6)

- `_news/2024-02-20-ice-diploma-award-ceremony.md`: sin título en español
- `_news/2024-09-19-mario-phd-thesis.md`: sin título en español
- `_news/2025-05-05-mario-assistant-professor.md`: sin título en español
- `_news/2025-05-13-nestor-associate-profesor-ppl.md`: sin título en español
- `_news/2025-09-04-nextarc-kickoff.md`: sin título en español
- `_news/2025-11-03-estela-research-support-nextarc.md`: sin título en español

## Imágenes sin texto alternativo (8)

- `_news/2024-02-20-ice-diploma-award-ceremony.md`: galería de 5 fotos sin texto alternativo por foto (parámetro alts)
- `_news/2025-09-04-nextarc-kickoff.md`: galería de 3 fotos sin texto alternativo por foto (parámetro alts)
- `_news/2025-09-04-nextarc-kickoff.md`: imagen sin texto alternativo: /assets/img/noticias/2025-09-04-nextarc-kickoff/nextarc-kickoff-group.webp
- `_news/2025-09-04-nextarc-kickoff.md`: imagen sin texto alternativo: /assets/img/noticias/2025-09-04-nextarc-kickoff/img-2330.webp
- `_news/2025-11-27-car-csic-industry-day-2025.md`: galería de 4 fotos sin texto alternativo por foto (parámetro alts)
- `_news/2026-01-27-nextarc-workshop.md`: galería de 4 fotos sin texto alternativo por foto (parámetro alts)
- `_news/2026-03-18-upm-investiga.md`: galería de 4 fotos sin texto alternativo por foto (parámetro alts)
- `_news/2026-04-24-estela-professional-association-awards.md`: galería de 6 fotos sin texto alternativo por foto (parámetro alts)

## Imágenes que no existen en el origen (4)

- `_projects/accus.md`: no existe en el repositorio antiguo: assets/img/projects/accus/ACCUSFunding.png
- `_projects/swarms.md`: no existe en el repositorio antiguo: assets/img/projects/accus/SWARMsFunding.png
- `_opportunities/2025-05-20-ai-edge-agriculture-scholarship.md`: no existe en el repositorio antiguo: assets/opportunities/2025-05-20-grys-scholarship.pdf
- `_opportunities/2025-09-22-nextarc-job-offer.md`: no existe en el repositorio antiguo: assets/opportunities/2025-10-05-nextarc-job.pdf

## Enlaces rotos en el origen (2)

- `_opportunities/2025-05-20-ai-edge-agriculture-scholarship.md`: el PDF de la oferta no existe en el repositorio antiguo: /assets/opportunities/2025-05-20-grys-scholarship.pdf
- `_opportunities/2025-09-22-nextarc-job-offer.md`: el PDF de la oferta no existe en el repositorio antiguo: /assets/opportunities/2025-10-05-nextarc-job.pdf

## Bibliografía (27)

- `theses.bib`: rodriguez-molina_distribution_2015: tipo @phdthesis en master_theses.bib → @mastersthesis
- `theses.bib`: botas_barcena_intelligent_2026: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: mora_barba_device_2025: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: lópezlópezConcienciaSituacionalTiempo2025: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: picotarizmendiArtificialIntelligenceApplied2025: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: bravoacedoSistemaDiagnosticoPrecoz2025: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: delgado_marquez_sistema_2025: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: mora_barba_smart_2025: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: sanzbarrioDisenoAplicacionMovil2024: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: garcia_moreno_diseno_2024: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: garcia_moreno_sistema_2024: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: garcíaserranoSimulacionPlanificacionAcciones2019: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: garcíaparedesAnticipativeSystemPlanner2018: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: duanRosNodeProcessing2018: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: morenobelinchónIntegracionIndustria402018: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: perez_sechi_arquitectura_2016: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: zuoPerceptionNetworkedRobot2016: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: martínezabascalOpenTechnologiesPrototyping2013: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: lucas-martínezVirtualizacionDispositivosPara2013: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: herradormuñozSistemaAparcamientoInteligente2013: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: cuervagarcíaRedesServiciosUbicuos2012: tipo @phdthesis en bachelor_theses.bib → @thesis
- `theses.bib`: rodríguezmolinaSemanticMiddlewareDevelopment2012: tipo @phdthesis en bachelor_theses.bib → @thesis
- `_projects/demanes.md`: cita a clave inexistente en el BibTeX: LucasMartinezECSA2015 (se marca)
- `_projects/demanes.md`: cita a clave inexistente en el BibTeX: HernandezDiaz2015, LucasMartinez2016 (se marca)
- `_projects/demanes.md`: cita a clave inexistente en el BibTeX: LucasMartinezMScThesis2016 (se marca)
- `_projects/woo.md`: cita a clave inexistente en el BibTeX: lucas_martinez_virtualization_2014-1 (se marca)
- `_projects/woo.md`: cita a clave inexistente en el BibTeX: lucas_martinez_virtualization_2014 (se marca)

## Imágenes y PDF que se migran (119)

Ver `mapa_imagenes.yml`.
