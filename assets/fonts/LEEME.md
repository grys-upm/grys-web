# Fuentes alojadas en el sitio

Aquí van los `.woff2` de Urbanist, Atkinson Hyperlegible y Atkinson Hyperlegible Mono (licencia SIL OFL 1.1).

Se descargan una vez con `python3 scripts/descargar_fuentes.py` y se suben al repositorio. Los nombres deben coincidir con los `@font-face` de `assets/css/grys.css`.

Si faltan, el sitio usa las fuentes de respaldo del manual (Segoe UI/Calibri y Verdana/Tahoma), pero `scripts/verificar_sitio.py` dará error por enlaces rotos en los `preload`.
