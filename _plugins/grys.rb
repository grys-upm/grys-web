# frozen_string_literal: true

# =====================================================================
#  GRyS · rutas bilingües, fichas de detalle, estados y redirecciones
# ---------------------------------------------------------------------
#  · Filtros Liquid:
#      {{ 'team' | route_url }}            URL de una página de _data/routes.yml
#      {{ 'team' | route_url: 'en' }}      … en otro idioma
#      {{ '/ruta/' | url_lang }}           añade baseurl y prefijo de idioma
#      {{ doc | detail_url }}              URL de la ficha de un elemento (o nil)
#      {{ page | alt_url: 'en' }}          URL equivalente en otro idioma
#      {{ campo | l10n }}                  elige {es:…, en:…} según el idioma
#      {{ doc | tr: 'title' }}             campo title_<idioma> con respaldo
#      {{ 'slug' | member }}               documento de _members por su slug
#  · Generador (en cada pasada de idioma de polyglot):
#      - calcula el estado de los proyectos a partir de las fechas;
#      - crea las fichas de detalle de routes.yml > details;
#      - (solo en el idioma por defecto) crea las páginas de redirección.
#  · Idioma del contenido: el campo «lang» de un elemento indica en qué
#    idioma está escrito su texto (es/en). Los elementos se publican en
#    los dos idiomas; si el texto no está en el idioma de la página, la
#    plantilla lo marca con lang="…" y un aviso. «only_lang: es» restringe
#    la publicación a un idioma.
# =====================================================================

require "date"

module GRyS
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

    # Ruta de la pasada (sin baseurl ni prefijo) -> ruta pública completa
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

    def to_date(value)
      return nil if value.nil? || value.to_s.strip.empty?
      return value.to_date if value.respond_to?(:to_date)

      Date.parse(value.to_s)
    rescue ArgumentError
      nil
    end

    def date_str(doc)
      d = to_date(doc.data["date"])
      d ? d.strftime("%Y-%m-%d") : doc.basename_without_ext[0, 10]
    end

    def base_slug(doc)
      doc.basename_without_ext.sub(/\A\d{4}-\d{2}-\d{2}-/, "")
    end

    # Jekyll rellena data["slug"] con el nombre del fichero (en noticias puede
    # incluir la fecha), así que siempre se quita un prefijo AAAA-MM-DD-.
    def detail_slug(doc, lang)
      (doc.data["slug_#{lang}"] || doc.data["slug"] || base_slug(doc)).to_s.sub(/\A\d{4}-\d{2}-\d{2}-/, "")
    end

    def has_detail?(doc)
      doc.data["detail"] != false && doc.data["published"] != false
    end

    def detail_path(site, coll, doc, lang)
      cfg = (routes(site)["details"] || {})[coll.to_s]
      return nil unless cfg && cfg[lang.to_s] && has_detail?(doc)

      cfg[lang.to_s].gsub(":date", date_str(doc)).gsub(":slug", detail_slug(doc, lang))
    end

    def doc_in_lang?(doc, lang)
      only = doc.data["only_lang"]
      return true if only.nil? || only.to_s.empty?

      Array(only).map(&:to_s).include?(lang.to_s)
    end

    def find_doc(site, drop, coll = nil)
      return drop if drop.is_a?(Jekyll::Document)
      return nil unless drop.respond_to?(:[])

      name = (coll || drop["collection"]).to_s
      collection = site.collections[name]
      return nil unless collection

      rel = drop["relative_path"].to_s
      collection.docs.find { |d| d.relative_path == rel }
    end

    # Campo traducible: <campo>_<idioma>, si no el del otro idioma, si no <campo>
    def tr(data, field, lang, langs)
      v = data["#{field}_#{lang}"]
      return v unless v.nil? || v.to_s.strip.empty?

      (langs - [lang]).each do |l|
        v = data["#{field}_#{l}"]
        return v unless v.nil? || v.to_s.strip.empty?
      end
      data[field]
    end

    # Jekyll rellena data["title"] con el nombre del fichero si falta, por eso
    # los campos propios (nombre, acrónimo, title_xx) van antes.
    def title_for(doc, lang, langs)
      d = doc.data
      return [d["given"], d["family"]].compact.join(" ").strip if d["given"]
      return d["acronym"] if d["acronym"]

      tr(d, "title", lang, langs)
    end

    # true si el título mostrado no está en el idioma de la página
    def title_fallback?(doc, lang)
      d = doc.data
      return false if d["given"] || d["acronym"]

      v = d["title_#{lang}"]
      v.nil? || v.to_s.strip.empty?
    end

    # Entradilla bajo el <h1>: en proyectos, el título largo; en líneas, la descripción
    def lead_for(doc, lang, langs)
      d = doc.data
      return tr(d, "title", lang, langs) if d["acronym"]
      return tr(d, "desc", lang, langs) if d["desc_es"] || d["desc_en"]

      nil
    end

    # Estado de un proyecto: «status» explícito, o calculado con las fechas
    def project_status(doc, today)
      explicit = doc.data["status"].to_s
      return explicit unless explicit.empty?

      start = to_date(doc.data["start"])
      finish = to_date(doc.data["end"])
      return "unknown" if finish.nil?
      return "upcoming" if start && start > today

      finish >= today ? "ongoing" : "completed"
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

    def tr(item, field, lang = nil)
      return nil unless item.respond_to?(:[])

      site = @context.registers[:site]
      lang = (lang || Util.active_lang(site)).to_s
      Util.tr(item, field.to_s, lang, Util.languages(site))
    end

    # Texto de un campo BibTeX para mostrar: sin llaves de protección ni
    # órdenes LaTeX básicas. (En Liquid no se puede escribir "}" dentro de
    # {{ … }}: el analizador lo toma como cierre. Por eso existe este filtro.)
    def bib_text(value)
      return value if value.nil?

      value.to_s
           .gsub(/\\&/, "&").gsub(/\\%/, "%").gsub(/\\_/, "_")
           .gsub(/\\textendash\s*|--/, "–").gsub(/\\textemdash\s*|---/, "—")
           .gsub(/\\[a-zA-Z]+\s*/, "")
           .delete("{}\\")
           .gsub(/\s+/, " ").strip
    end

    # true si el fichero existe en el repositorio. Ruta desde la raíz: "/assets/…".
    # (En las plantillas, site.static_files NO expone relative_path; por eso
    # este filtro en lugar de recorrer site.static_files.)
    def asset_exists(path)
      return false if path.nil? || path.to_s.strip.empty?

      site = @context.registers[:site]
      File.file?(site.in_source_dir(path.to_s.sub(%r{\A/+}, "")))
    end

    # Texto visible de un enlace: sin «https://», «www.» ni barra final
    def url_label(value)
      return value if value.nil?

      value.to_s.sub(%r{\Ahttps?://}i, "").sub(/\Awww\./i, "").chomp("/")
    end

    # Enlace interno a una ficha desde el TEXTO de cualquier elemento, válido en
    # los dos idiomas:  [AFarCloud]({{ 'projects/afarcloud' | ref }})
    # Formato: «colección/slug» (members, projects, lines, news).
    def ref(target)
      site = @context.registers[:site]
      coll, slug = target.to_s.split("/", 2)
      collection = site.collections[coll.to_s]
      doc = collection&.docs&.find { |d| Util.detail_slug(d, Util.default_lang(site)) == slug.to_s }
      if doc.nil?
        Jekyll.logger.warn("GRyS:", "ref: «#{target}» no existe (formato: colección/slug)")
        return "#"
      end
      lang = Util.active_lang(site)
      Util.full_path(site, lang, Util.detail_path(site, coll, doc, lang))
    end

    def member(slug)
      site = @context.registers[:site]
      coll = site.collections["members"]
      return nil unless coll

      coll.docs.find { |d| Util.detail_slug(d, Util.default_lang(site)) == slug.to_s }
    end

    # Slug de un documento de colección (el de su URL en el idioma por defecto).
    # En los listados se usa esto, NO «page_id»: page_id solo existe en las
    # páginas de ficha que genera el plugin, no en los documentos de la colección.
    def slug_of(drop, coll = nil)
      site = @context.registers[:site]
      doc = Util.find_doc(site, drop, coll)
      doc && Util.detail_slug(doc, Util.default_lang(site))
    end
  end

  # ---------------------------------------------------------------------
  class Generator < Jekyll::Generator
    safe true
    priority :low

    SKIP_KEYS = %w[layout permalink excerpt output collection draft].freeze

    def generate(site)
      lang = Util.active_lang(site)
      compute_status(site)
      generate_details(site, lang)
      generate_redirects(site) if lang == Util.default_lang(site)
    end

    private

    def compute_status(site)
      coll = site.collections["projects"]
      return unless coll

      today = site.time.to_date
      coll.docs.each { |doc| doc.data["state"] = Util.project_status(doc, today) }
    end

    def generate_details(site, lang)
      langs = Util.languages(site)
      (Util.routes(site)["details"] || {}).each do |coll, cfg|
        collection = site.collections[coll]
        next unless collection

        collection.docs.each do |doc|
          next unless Util.doc_in_lang?(doc, lang)

          path = Util.detail_path(site, coll, doc, lang)
          site.pages << build_detail(site, doc, coll, cfg, lang, langs, path) if path
        end
      end
    end

    def build_detail(site, doc, coll, cfg, lang, langs, path)
      page = Jekyll::PageWithoutAFile.new(site, site.source, path, "index.md")
      doc.data.each { |k, v| page.data[k] = v unless SKIP_KEYS.include?(k) }

      alt = {}
      langs.each do |l|
        next unless Util.doc_in_lang?(doc, l)

        alt[l] = Util.full_path(site, l, Util.detail_path(site, coll, doc, l))
      end

      page.data.merge!(
        "layout" => cfg["layout"] || "detail",
        "lang" => lang,
        "content_lang" => (doc.data["lang"] || lang).to_s,
        "page_id" => "#{coll}/#{Util.detail_slug(doc, Util.default_lang(site))}",
        "permalink" => path,
        "title" => Util.title_for(doc, lang, langs),
        "title_fallback" => Util.title_fallback?(doc, lang),
        "lead" => Util.lead_for(doc, lang, langs),
        "kind" => coll,
        "parent" => cfg["parent"],
        "source_path" => doc.relative_path,
        "alt_paths" => alt
      )
      page.content = doc.content
      page
    end

    # -------------------------------------------------------------- redirecciones
    def generate_redirects(site)
      list = Array(site.data["redirects"]).map(&:dup)
      list.concat(redirects_from_collections(site))

      seen = {}
      list.each do |r|
        from = r["from"].to_s
        next if from.empty? || seen[from]

        to = r["to_path"] || resolve_target(site, r)
        next unless to

        seen[from] = true
        site.pages << build_redirect(site, from, to)
      end
    end

    # old_urls de cada elemento: a su ficha si la tiene; si no, a la página de lista
    def redirects_from_collections(site)
      out = []
      details = Util.routes(site)["details"] || {}
      lists = Util.routes(site)["lists"] || {}
      site.collections.each do |coll, collection|
        collection.docs.each do |doc|
          urls = Array(doc.data["old_urls"])
          next if urls.empty?

          lang = (doc.data["old_urls_lang"] || "en").to_s
          lang = Util.default_lang(site) unless Util.doc_in_lang?(doc, lang)
          path = details[coll] ? Util.detail_path(site, coll, doc, lang) : nil
          path ||= Util.route_path(site, lists[coll], lang) if lists[coll]
          next unless path

          target = Util.full_path(site, lang, path)
          urls.each { |from| out << { "from" => from, "to_path" => target } }
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
