# frozen_string_literal: true

# =====================================================================
#  GRyS · cifras calculadas desde el BibTeX (fuente principal de recuentos)
# ---------------------------------------------------------------------
#  Deja en site.data["bib_stats"]:
#    papers: { total, journal, conference, chapter, book, other, first_year, last_year,
#              with_doi, with_portal, with_archivo }
#    theses: { total, phd, master, bachelor, awards }
#  Uso en Liquid: {{ site.data.bib_stats.papers.total }}
#  Las cifras de Scopus (citas, índice h) no salen del BibTeX: _data/metrics.yml
# =====================================================================

require "bibtex"

module GRyS
  class BibStats < Jekyll::Generator
    safe true
    priority :highest

    KIND = {
      "article" => "journal",
      "inproceedings" => "conference", "conference" => "conference",
      "incollection" => "chapter", "inbook" => "chapter",
      "book" => "book"
    }.freeze

    def generate(site)
      dir = File.join(site.source, "_bibliography")
      site.data["bib_stats"] = {
        "papers" => papers(File.join(dir, "papers.bib")),
        "theses" => theses(File.join(dir, "theses.bib"))
      }
    end

    private

    def load(path)
      return [] unless File.exist?(path)

      BibTeX.open(path, parse_comments: false).data.select { |e| e.is_a?(BibTeX::Entry) }
    rescue StandardError => e
      Jekyll.logger.warn("GRyS:", "no se pudo leer #{File.basename(path)}: #{e.message}")
      []
    end

    def field(entry, name)
      value = entry[name.to_sym]
      value.nil? ? "" : value.to_s.strip
    end

    def papers(path)
      entries = load(path)
      stats = Hash.new(0)
      years = []
      entries.each do |e|
        stats[KIND.fetch(e.type.to_s.downcase, "other")] += 1
        stats["with_doi"] += 1 unless field(e, "doi").empty?
        stats["with_portal"] += 1 unless field(e, "portal_upm").empty?
        stats["with_archivo"] += 1 unless field(e, "archivo_upm").empty?
        y = field(e, "year").to_i
        years << y if y.positive?
      end
      stats["total"] = entries.size
      stats["first_year"] = years.min
      stats["last_year"] = years.max
      %w[journal conference chapter book other].each { |k| stats[k] += 0 }
      stats.to_h
    end

    def theses(path)
      entries = load(path)
      stats = Hash.new(0)
      entries.each do |e|
        level = field(e, "level")
        stats[level.empty? ? "other" : level] += 1
        stats["awards"] += 1 unless field(e, "award").empty?
      end
      stats["total"] = entries.size
      %w[phd master bachelor].each { |k| stats[k] += 0 }
      stats.to_h
    end
  end
end
