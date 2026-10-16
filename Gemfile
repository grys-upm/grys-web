# Gemas del sitio GRyS. Versiones fijadas con "~>" (admite parches y menores
# compatibles). Dependabot propone las actualizaciones; Gemfile.lock fija la
# versión exacta y debe estar en el repositorio.
source "https://rubygems.org"

gem "jekyll", "~> 4.4.1"

group :jekyll_plugins do
  gem "jekyll-polyglot", "~> 1.14"   # bilingüe ES (/) y EN (/en/)
  gem "jekyll-scholar", "~> 7.2"     # publicaciones y tesis desde BibTeX
end

# Necesarias con Ruby >= 3.3 (ya no vienen por defecto)
gem "observer", "~> 0.1"   # la usa jekyll-scholar
gem "webrick", "~> 1.9"    # solo para "jekyll serve" en local
