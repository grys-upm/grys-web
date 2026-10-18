#!/usr/bin/env bash
# Publica o borra vistas previas de PR en el repositorio de vistas previas
# (por defecto grys-upm/grys-web-previews), ya clonado en el directorio actual.
# Lo usan .github/workflows/pr.yml y vista-previa-borrar.yml.
#
#   vista_previa.sh publicar pr-12 RUTA/_site    copia el sitio en pr-12/
#   vista_previa.sh borrar pr-12                 borra pr-12/
#   vista_previa.sh borrar-salvo "pr-3 pr-7"     borra todas las pr-N salvo esas
#
# El repositorio de vistas previas guarda UN solo commit, sin historial, para
# que no crezca con cada compilación. --force-with-lease evita pisar a otra PR
# que publique a la vez; si ocurre, se reintenta hasta 5 veces.
set -euo pipefail

modo="${1:?modo: publicar | borrar | borrar-salvo}"
arg="${2:-}"
sitio="${3:-}"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
rama=$(git rev-parse --abbrev-ref HEAD)

for intento in 1 2 3 4 5; do
  git fetch -q --depth 1 origin "+refs/heads/$rama:refs/remotes/origin/$rama"
  git reset -q --hard "origin/$rama"
  base=$(git rev-parse HEAD)
  cambios=""
  case "$modo" in
    publicar)
      [[ "$arg" =~ ^pr-[0-9]+$ ]] || { echo "nombre no válido: $arg"; exit 2; }
      rm -rf "$arg"; mkdir -p "$arg"; cp -R "$sitio"/. "$arg"/
      touch .nojekyll
      cambios="$arg" ;;
    borrar)
      if [ -d "$arg" ]; then rm -rf "$arg"; cambios="$arg"; fi ;;
    borrar-salvo)
      for d in pr-*; do
        [ -d "$d" ] || continue
        case " $arg " in *" $d "*) continue ;; esac
        rm -rf "$d"; cambios="$cambios $d"
      done ;;
    *) echo "modo desconocido: $modo"; exit 2 ;;
  esac
  if [ -z "$cambios" ]; then echo "vista_previa: nada que hacer"; exit 0; fi
  git checkout -q --orphan nueva
  git add -A
  git commit -qm "Vistas previas ($modo):$cambios"
  if git push -q --force-with-lease="$rama:$base" origin "nueva:$rama"; then
    echo "vista_previa: $modo$cambios"
    exit 0
  fi
  git checkout -q -f "$rama"
  git branch -q -D nueva
  sleep $((RANDOM % 10 + 5))
done
echo "::error::vista_previa: no se pudo publicar tras 5 intentos"
exit 1
