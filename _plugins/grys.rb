# frozen_string_literal: true

# =====================================================================
#  GRyS · rutas bilingües, fichas de detalle y redirecciones
# ---------------------------------------------------------------------
#  · Filtros Liquid:
#      {{ 'team' | route_url }}            URL de una página de _data/routes.yml
#      {{ 'team' | route_url: 'en' }}      … en otro idioma
#      {{ '/ruta/' | url_lang }}           añade baseurl y prefijo de idioma
#      {{ doc | detail_url: 'projects' }}  URL de la ficha de un elemento
#      {{ page | alt_url: 'en' }}          URL equivalente en otro idioma
#      {{ campo | l10n }}                  elige {es:…, en:…} según el idioma
#  · Generador: crea, en cada pasada de idioma de polyglot, las fichas de
#    detalle de las colecciones declaradas en routes.yml > details, y (solo
#    en la pasada del idioma por defecto) las páginas de redirección.
# =====================================================================

module GRyS
  # Utilidades compartidas por filtros y generador
  module Util
    module_function

    def default_lang(site)
      (site.config["default_lang"] || "es").to_s
    end

    def active_lang(site)
      lang = site.respond_to?(:active_lang) ? site.active_lang : nil
      (lang || default_lang(site)).to_s
    end

    def languages(site)
      Array(site.config["languages"] || [default_lang(site)]).map(&:to_s)
    end

    def routes(site)
      site.data["routes"] || {}
    end

    def route(site, id)
      Array(routes(site)["pages"]).find { |r| r["id"].to_s == id.to_s }
    end

    # Ruta de la pasada (sin baseurl ni /en) -> ruta pública completa
    def full_path(site, lang, path)
      return nil if path.nil?

      base = site.config["baseurl"].to_s.chomp("/")
      prefix = lang.to_s == default_lang(site) ? "" : "/#{lang}"
      "#{base}#{prefix}#{path}"
    end

    def route_path(site, id, lang)
      r = route(site, id)
      r && r[lang.to_s]
    end

    def date_str(doc)
      d = doc.data["date"]
      d.respond_to?(:strftime) ? d.strftime("%Y-%m-%d") : d.to_s[0, 10]
    end

    def base_slug(doc)
      doc.basename_without_ext.sub(/\A\d{4}-\d{2}-\d{2}-/, "")
    end

    def detail_slug(doc, lang)
      (doc.data["slug_#{lang}"] || doc.data["slug"] || base_slug(doc)).to_s
    end

    def detail_path(site, coll, doc, lang)
      cfg = (routes(site)["details"] || {})[coll.to_s]
      return nil unless cfg && cfg[lang.to_s]

      cfg[lang.to_s].gsub(":date", date_str(doc)).gsub(":slug", detail_slug(doc, lang))
    end

    # Un elemento sin «lang» (o con lang: both) se publica en todos los idiomas
    def doc_in_lang?(doc, lang)
      l = doc.data["lang"]
      return true if l.nil? || l.to_s.empty? || l.to_s == "both"

      Array(l).map(&:to_s).include?(lang.to_s)
    end

    def find_doc(site, drop, coll)
      return drop if drop.is_a?(Jekyll::Document)
      return nil unless drop.respond_to?(:[])

      name = (coll || drop["collection"]).to_s
      collection = site.collections[name]
      return nil unless collection

      rel = drop["relative_path"].to_s
      collection.docs.find { |d| d.relative_path == rel }
    end

    # Ojo: Jekyll rellena data["title"] con el nombre del fichero si falta,
    # por eso los campos propios (nombre, acrónimo) van antes.
    def title_for(doc, lang)
      d = doc.data
      return [d["given"], d["family"]].compact.join(" ").strip if d["given"]

      d["acronym"] || d["title_#{lang}"] || d["title"]
    end

    # Entradilla bajo el <h1>: en proyectos, el título largo
    def lead_for(doc, lang)
      d = doc.data
      d["lead_#{lang}"] || (d["acronym"] ? d["title_#{lang}"] : nil)
    end
  end

  # ---------------------------------------------------------------------
  module Filters
    def route_url(id, lang = nil)
      site = @context.registers[:site]
      lang = (lang || Util.active_lang(site)).to_s
      path = Util.route_path(site, id, lang)
      Jekyll.logger.warn("GRyS:", "route_url: página '#{id}' desconocida") if path.nil?
      Util.full_path(site, lang, path)
    end

    def url_lang(path, lang = nil)
      site = @context.registers[:site]
      Util.full_path(site, (lang || Util.active_lang(site)).to_s, path.to_s)
    end

    def detail_url(drop, coll = nil, lang = nil)
      site = @context.registers[:site]
      lang = (lang || Util.active_lang(site)).to_s
      doc = Util.find_doc(site, drop, coll)
      return nil unless doc && Util.doc_in_lang?(doc, lang)

      Util.full_path(site, lang, Util.detail_path(site, doc.collection.label, doc, lang))
    end

    def alt_url(page, lang)
      site = @context.registers[:site]
      return nil unless page.respond_to?(:[])

      alt = page["alt_paths"]
      return alt[lang.to_s] if alt.respond_to?(:[])

      path = Util.route_path(site, page["page_id"], lang)
      Util.full_path(site, lang.to_s, path)
    end

    def l10n(value, lang = nil)
      return value unless value.is_a?(Hash)

      site = @context.registers[:site]
      lang = (lang || Util.active_lang(site)).to_s
      value[lang] || value[Util.default_lang(site)] || value.values.first
    end
  end

  # ---------------------------------------------------------------------
  class Generator < Jekyll::Generator
    safe true
    priority :low

    SKIP_KEYS = %w[layout permalink excerpt output collection draft].freeze

    def generate(site)
      lang = Util.active_lang(site)
      generate_details(site, lang)
      generate_redirects(site) if lang == Util.default_lang(site)
    end

    private

    def generate_details(site, lang)
      (Util.routes(site)["details"] || {}).each do |coll, cfg|
        collection = site.collections[coll]
        next unless collection

        collection.docs.each do |doc|
          next if doc.data["published"] == false
          next unless Util.doc_in_lang?(doc, lang)

          path = Util.detail_path(site, coll, doc, lang)
          site.pages << build_detail(site, doc, coll, cfg, lang, path) if path
        end
      end
    end

    def build_detail(site, doc, coll, cfg, lang, path)
      page = Jekyll::PageWithoutAFile.new(site, site.source, path, "index.md")
      doc.data.each { |k, v| page.data[k] = v unless SKIP_KEYS.include?(k) }

      alt = {}
      Util.languages(site).each do |l|
        next unless Util.doc_in_lang?(doc, l)

        alt[l] = Util.full_path(site, l, Util.detail_path(site, coll, doc, l))
      end

      page.data.merge!(
        "layout" => cfg["layout"] || "detail",
        "lang" => lang,
        "page_id" => "#{coll}/#{Util.detail_slug(doc, Util.default_lang(site))}",
        "permalink" => path,
        "title" => Util.title_for(doc, lang),
        "lead" => Util.lead_for(doc, lang),
        "kind" => coll,
        "parent" => cfg["parent"],
        "source_path" => doc.relative_path,
        "alt_paths" => alt
      )
      page.content = doc.content
      page
    end

    def generate_redirects(site)
      list = Array(site.data["redirects"]).map(&:dup)
      list.concat(redirects_from_collections(site))

      list.each do |r|
        from = r["from"].to_s
        next if from.empty?

        to = r["to_path"] || resolve_target(site, r)
        next unless to

        site.pages << build_redirect(site, from, to)
      end
    end

    def redirects_from_collections(site)
      out = []
      (Util.routes(site)["details"] || {}).each_key do |coll|
        collection = site.collections[coll]
        next unless collection

        collection.docs.each do |doc|
          lang = (doc.data["old_urls_lang"] || "en").to_s
          lang = Util.default_lang(site) unless Util.doc_in_lang?(doc, lang)
          target = Util.full_path(site, lang, Util.detail_path(site, coll, doc, lang))
          Array(doc.data["old_urls"]).each { |from| out << { "from" => from, "to_path" => target } }
        end
      end
      out
    end

    def resolve_target(site, r)
      lang = (r["lang"] || Util.default_lang(site)).to_s
      path = Util.route_path(site, r["to"], lang)
      if path.nil?
        Jekyll.logger.warn("GRyS:", "redirección #{r['from']}: página '#{r['to']}' desconocida")
        return nil
      end
      "#{Util.full_path(site, lang, path)}#{r['anchor']}"
    end

    def build_redirect(site, from, to)
      folder = from.end_with?("/") || File.extname(from).empty?
      dir = folder ? from : File.dirname(from)
      name = folder ? "index.html" : File.basename(from)
      page = Jekyll::PageWithoutAFile.new(site, site.source, dir, name)
      dl = Util.default_lang(site)
      page.data.merge!(
        "layout" => "redirect",
        "redirect_to" => to,
        "lang" => dl,
        "lang-exclusive" => [dl],
        "page_id" => "redirect#{from}",
        "sitemap" => false
      )
      page.content = ""
      page
    end
  end
end

Liquid::Template.register_filter(GRyS::Filters)
