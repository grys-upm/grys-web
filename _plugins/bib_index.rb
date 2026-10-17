# frozen_string_literal: true

# =====================================================================
#  GRyS · índice de publicaciones para las fichas (proyecto, línea, miembro)
# ---------------------------------------------------------------------
#  Deja en site.data:
#    pubs      → lista de publicaciones de papers.bib, de la más reciente a la
#                más antigua: { key, kind, year, title, authors, venue, doi,
#                portal_upm, archivo_upm, projects[], lines[], members[] }
#    pub_index → el mismo contenido indexado por clave BibTeX (lo usa bib.html)
#  · projects/lines salen de los campos «project»/«lines» (etiquetas.yml).
#  · members se calcula por AUTORÍA comparando los autores del BibTeX con
#    given/family de _members/ (sin tildes ni mayúsculas):
#      - el primer apellido debe estar en los apellidos del autor (o todos los
#        apellidos del miembro en el nombre completo), y si ambos tienen
#        segundo apellido, debe coincidir;
#      - algún nombre debe coincidir entero o por la inicial.
#    Para formas que no encajan (seudónimos, erratas en Zotero), el miembro
#    puede declarar «bib_names» con los autores exactos tal como están en el BibTeX.
#  Uso: {{ site.data.pubs | where_exp: "p", "p.projects contains slug" }}
# =====================================================================

require "bibtex"

module GRyS
  class BibIndex < Jekyll::Generator
    safe true
    priority :high

    PARTICLES = %w[de la del las los y da van von e i].freeze
    MONTHS = %w[jan feb mar apr may jun jul aug sep oct nov dec].freeze
    KIND = {
      "article" => "journal",
      "inproceedings" => "conference", "conference" => "conference"
    }.freeze

    def generate(site)
      path = File.join(site.source, "_bibliography", "papers.bib")
      entries = File.exist?(path) ? load(path) : []
      people = members(site)
      pubs = entries.map { |e| to_hash(e, people) }
      pubs.sort_by! { |p| [-p["year"].to_i, -p["_month"], p["title"].to_s.downcase] }
      pubs.each { |p| p.delete("_month") }
      site.data["pubs"] = pubs
      site.data["pub_index"] = pubs.to_h { |p| [p["key"], p] }
    end

    private

    def load(path)
      BibTeX.open(path, parse_comments: false).data.select { |e| e.is_a?(BibTeX::Entry) }
    rescue StandardError => e
      Jekyll.logger.warn("GRyS:", "bib_index: no se pudo leer papers.bib: #{e.message}")
      []
    end

    def clean(value)
      value.to_s
           .gsub(/\\&/, "&").gsub(/\\%/, "%").gsub(/\\_/, "_")
           .gsub(/\\textendash\s*|--/, "–")
           .gsub(/\\[a-zA-Z]+\s*/, "")
           .delete("{}\\")
           .gsub(/\s+/, " ").strip
    end

    def tokens(text)
      clean(text).unicode_normalize(:nfd).gsub(/\p{Mn}/, "").downcase
                 .split(/[^a-z0-9]+/).reject(&:empty?)
    end

    def list(value)
      clean(value).split(/[\s,;]+/).reject(&:empty?)
    end

    def members(site)
      coll = site.collections["members"]
      return [] unless coll

      coll.docs.map do |d|
        fam = tokens(d.data["family"]) - PARTICLES
        giv = tokens(d.data["given"])
        next nil if fam.empty? || giv.empty?

        { "slug" => d.data["slug"] || d.basename_without_ext, "fam" => fam, "giv" => giv,
          "alias" => Array(d.data["bib_names"]).map { |n| tokens(n) } }
      end.compact
    end

    # Autor del BibTeX (BibTeX::Name) → [apellidos, nombres] en tokens
    def author_tokens(name)
      last = tokens([name.prefix, name.last].compact.join(" ")) - PARTICLES
      first = tokens(name.first.to_s)
      [last, first]
    end

    def same_person?(m, last, first)
      return true if m["alias"].include?(tokens("#{first.join(' ')} #{last.join(' ')}")) ||
                     m["alias"].include?(last + first)

      all = last + first
      fam = m["fam"]
      return false unless last.include?(fam[0]) || fam.all? { |w| all.include?(w) }
      # Segundo apellido distinto (Sánchez Alcón ≠ Sánchez Fernández)
      if fam.size > 1 && last.size > 1 && last[0] == fam[0] && last[1] != fam[1]
        return false
      end

      rest = first - fam
      rest.any? { |t| m["giv"].include?(t) || (t.size <= 2 && m["giv"].any? { |g| g.start_with?(t[0]) }) }
    end

    def to_hash(e, people)
      names = e[:author].respond_to?(:each) ? e[:author].to_a : []
      slugs = []
      names.each do |n|
        next unless n.respond_to?(:last)

        last, first = author_tokens(n)
        people.each { |m| slugs << m["slug"] if same_person?(m, last, first) }
      end
      month = e[:month].to_s.downcase[0, 3]
      {
        "key" => e.key.to_s,
        "kind" => KIND.fetch(e.type.to_s.downcase, "book"),
        "year" => e[:year].to_s,
        "_month" => (MONTHS.index(month) || (month.to_i - 1)).to_i + 1,
        "title" => clean(e[:title]),
        "authors" => names.map { |n| n.respond_to?(:last) ? clean("#{n.first} #{n.prefix} #{n.last}") : clean(n) }.join(", "),
        "venue" => clean(e[:journal] || e[:booktitle] || e[:publisher] || ""),
        "doi" => e[:doi].to_s.strip,
        "portal_upm" => e[:portal_upm].to_s.strip,
        "archivo_upm" => e[:archivo_upm].to_s.strip,
        "projects" => list(e[:project]),
        "lines" => list(e[:lines]),
        "members" => slugs.uniq
      }
    end
  end
end
