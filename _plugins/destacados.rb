# frozen_string_literal: true

# =====================================================================
#  GRyS · proyectos destacados de la portada
# ---------------------------------------------------------------------
#  Deja en site.data["destacados"] la lista ORDENADA de slugs de proyecto
#  que muestra la portada, según _data/portada.yml → destacados:
#    numero: 3        cuántos se muestran
#    fijos: [...]     (opcional) slugs que van SIEMPRE, primero y en ese orden
#    excluir: [...]   (opcional) slugs que nunca se eligen automáticamente
#  Los huecos que quedan se rellenan AUTOMÁTICAMENTE:
#    1.º proyectos en curso (estado calculado con las fechas a la fecha de
#        compilación), del que empezó más tarde al que empezó antes;
#    2.º el resto, en orden cronológico inverso por fecha de fin (los que
#        terminaron más recientemente primero); los próximos (aún sin empezar)
#        van detrás de los en curso.
#    Empates: por acrónimo. Proyectos sin fechas, al final.
#  La regla está replicada en scripts/verificar_sitio.py para comprobar la salida.
# =====================================================================

module GRyS
  class Destacados < Jekyll::Generator
    safe true
    priority :lowest

    RANK = { "ongoing" => 0, "upcoming" => 1, "completed" => 2, "unknown" => 3 }.freeze
    FAR = Date.new(1900, 1, 1)

    def generate(site)
      cfg = (site.data["portada"] || {})["destacados"] || {}
      coll = site.collections["projects"]
      return site.data["destacados"] = [] unless coll

      today = site.time.to_date
      docs = coll.docs.to_h { |d| [Util.detail_slug(d, Util.default_lang(site)), d] }
      numero = (cfg["numero"] || 3).to_i
      fijos = Array(cfg["fijos"]).map(&:to_s).select { |s| docs.key?(s) }
      excluir = Array(cfg["excluir"]).map(&:to_s)

      auto = docs.reject { |s, _| fijos.include?(s) || excluir.include?(s) }.map do |slug, d|
        state = Util.project_status(d, today)
        start = Util.to_date(d.data["start"]) || FAR
        finish = Util.to_date(d.data["end"]) || FAR
        # En curso: por inicio (más reciente primero); el resto: por fin.
        key_date = state == "ongoing" ? start : finish
        [RANK.fetch(state, 3), -key_date.jd, d.data["acronym"].to_s.downcase, slug]
      end
      auto.sort!
      site.data["destacados"] = (fijos + auto.map(&:last)).first([numero, 0].max)
    end
  end
end
