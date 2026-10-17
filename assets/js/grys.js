/* GRyS · comportamiento mínimo (el contenido es estático; esto es mejora progresiva)
   - Menús desplegables: <button aria-expanded>, Esc, clic fuera
   - Cajón móvil
   - Cambio de tema claro/oscuro con memoria en localStorage
   - Pestañas accesibles (Equipo, Tesis) con ancla en la URL
   - Filtros de la tabla de Proyectos, con su estado en la URL
   (El tema inicial lo aplica el <script> en línea del <head>, sin parpadeo.) */
(function () {
  "use strict";
  var doc = document.documentElement;

  /* ---------- Menús ---------- */
  var tops = Array.prototype.slice.call(document.querySelectorAll(".mainnav .top"));
  function closeMenus(except) {
    tops.forEach(function (b) { if (b !== except) b.setAttribute("aria-expanded", "false"); });
  }
  tops.forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = b.getAttribute("aria-expanded") === "true";
      closeMenus(b);
      b.setAttribute("aria-expanded", String(!open));
      if (!open) {
        var first = b.nextElementSibling && b.nextElementSibling.querySelector("a");
        if (first) first.focus();
      }
    });
  });
  document.addEventListener("click", function (e) {
    if (!e.target.closest || !e.target.closest(".mainnav .dd")) closeMenus();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var open = tops.filter(function (b) { return b.getAttribute("aria-expanded") === "true"; })[0];
    closeMenus();
    if (open) open.focus();
  });
  // Cerrar el menú cuando el foco sale de él con el tabulador
  document.addEventListener("focusin", function (e) {
    tops.forEach(function (b) {
      var li = b.parentNode;
      if (b.getAttribute("aria-expanded") === "true" && !li.contains(e.target)) b.setAttribute("aria-expanded", "false");
    });
  });

  /* ---------- Cajón móvil ---------- */
  var burger = document.getElementById("burger");
  var drawer = document.getElementById("drawer");
  if (burger && drawer) {
    drawer.hidden = true;
    burger.addEventListener("click", function () {
      var open = burger.getAttribute("aria-expanded") === "true";
      burger.setAttribute("aria-expanded", String(!open));
      drawer.hidden = open;
    });
  }

  /* ---------- Tema ---------- */
  var btn = document.getElementById("themebtn");
  function applyThemeUI() {
    if (!btn) return;
    var dark = doc.getAttribute("data-theme") === "dark";
    document.getElementById("themelbl").textContent = btn.getAttribute(dark ? "data-to-light" : "data-to-dark");
    btn.setAttribute("aria-label", btn.getAttribute(dark ? "data-to-light-a" : "data-to-dark-a"));
    document.getElementById("themeicon").setAttribute("href", dark ? "#i-sun" : "#i-moon");
    var m = document.querySelector('meta[name="theme-color"]');
    if (m) m.content = dark ? "#2E3440" : "#FFFFFF";
  }
  if (btn) {
    btn.addEventListener("click", function () {
      var next = doc.getAttribute("data-theme") === "dark" ? "light" : "dark";
      doc.setAttribute("data-theme", next);
      try { localStorage.setItem("grys-theme", next); } catch (e) { /* modo privado */ }
      applyThemeUI();
    });
    applyThemeUI();
  }
  /* ---------- Pestañas (patrón ARIA tablist) ----------
     Marcado: .tabs[role=tablist] > button[role=tab][aria-controls=ID] y
     div[role=tabpanel][id=ID]. Flechas izquierda/derecha, Inicio y Fin para moverse.
     El ancla de la URL (#ID del panel o de algo que esté dentro) abre esa
     pestaña, y al cambiar de pestaña se actualiza el ancla sin saltar.
     Sin JavaScript, el CSS muestra todos los paneles. */
  var tablists = Array.prototype.slice.call(document.querySelectorAll('[role="tablist"]'));
  function tabsOf(list) { return Array.prototype.slice.call(list.querySelectorAll('[role="tab"]')); }
  function selectTab(tab, focus, updateHash) {
    var list = tab.closest('[role="tablist"]');
    tabsOf(list).forEach(function (x) {
      var on = x === tab;
      x.setAttribute("aria-selected", String(on));
      x.tabIndex = on ? 0 : -1;
      var p = document.getElementById(x.getAttribute("aria-controls"));
      if (p) p.hidden = !on;
    });
    if (focus) tab.focus();
    if (updateHash && history.replaceState) history.replaceState(null, "", "#" + tab.getAttribute("aria-controls"));
  }
  tablists.forEach(function (list) {
    var tabs = tabsOf(list);
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { selectTab(tab, true, true); });
      tab.addEventListener("keydown", function (e) {
        var n = null;
        if (e.key === "ArrowRight") n = tabs[(i + 1) % tabs.length];
        else if (e.key === "ArrowLeft") n = tabs[(i - 1 + tabs.length) % tabs.length];
        else if (e.key === "Home") n = tabs[0];
        else if (e.key === "End") n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); selectTab(n, true, true); }
      });
    });
  });
  function openFromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    var el = id && document.getElementById(id);
    if (!el) return;
    var panel = el.closest('[role="tabpanel"]');
    if (!panel) return;
    var tab = document.querySelector('[role="tab"][aria-controls="' + panel.id + '"]');
    if (tab) {
      selectTab(tab, false, false);
      el.scrollIntoView();
    }
  }
  if (tablists.length) {
    openFromHash();
    window.addEventListener("hashchange", openFromHash);
  }
  /* ---------- Filtros de tabla (Proyectos) ----------
     Marcado: form.filters[data-filter=P] (oculto con «hidden» hasta que este
     script lo muestra), con controles que tienen name (input/select) o grupos
     .seg[data-name] de botones aria-pressed. Elementos asociados por id:
     P-table (filas con data-<name>), P-count (recuento, data-one/data-many) y
     P-empty (aviso sin resultados). Un valor de filtro coincide si está entre los
     valores de data-<name>, separados por espacios; «q» busca en data-q sin
     tener en cuenta mayúsculas ni tildes. El estado se guarda en la URL (?tipo=…). */
  function norm(s) {
    return String(s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }
  Array.prototype.slice.call(document.querySelectorAll("form.filters[data-filter]")).forEach(function (form) {
    var p = form.getAttribute("data-filter");
    var table = document.getElementById(p + "-table");
    if (!table) return;
    var rows = Array.prototype.slice.call(table.tBodies[0].rows);
    var count = document.getElementById(p + "-count");
    var empty = document.getElementById(p + "-empty");
    var fields = Array.prototype.slice.call(form.querySelectorAll("input[name], select[name]"));
    var segs = Array.prototype.slice.call(form.querySelectorAll(".seg[data-name]"));

    function segValue(seg) {
      var b = seg.querySelector('button[aria-pressed="true"]');
      return b ? b.getAttribute("data-value") : "";
    }
    function setSeg(seg, value) {
      var found = false;
      Array.prototype.slice.call(seg.querySelectorAll("button")).forEach(function (b) {
        var on = b.getAttribute("data-value") === value;
        if (on) found = true;
        b.setAttribute("aria-pressed", String(on));
      });
      if (!found) seg.querySelector("button").setAttribute("aria-pressed", "true");
    }
    function state() {
      var s = {};
      fields.forEach(function (f) { s[f.name] = f.value.trim(); });
      segs.forEach(function (g) { s[g.getAttribute("data-name")] = segValue(g); });
      return s;
    }
    function apply(updateUrl) {
      var s = state(), q = norm(s.q), n = 0;
      rows.forEach(function (r) {
        var ok = true;
        Object.keys(s).forEach(function (k) {
          if (!ok || !s[k] || k === "q") return;
          var vals = (r.getAttribute("data-" + k) || "").split(/\s+/);
          if (vals.indexOf(s[k]) < 0) ok = false;
        });
        if (ok && q) ok = norm(r.getAttribute("data-q")).indexOf(q) >= 0;
        r.hidden = !ok;
        if (ok) n++;
      });
      if (count) count.textContent = n + " " + count.getAttribute(n === 1 ? "data-one" : "data-many");
      if (empty) { empty.hidden = n > 0; table.hidden = n === 0; }
      if (updateUrl && history.replaceState && window.URLSearchParams) {
        var u = new URLSearchParams();
        Object.keys(s).forEach(function (k) { if (s[k]) u.set(k, s[k]); });
        var qs = u.toString();
        history.replaceState(null, "", location.pathname + (qs ? "?" + qs : "") + location.hash);
      }
    }
    // Estado inicial desde la URL (solo valores que existan en los controles)
    if (window.URLSearchParams) {
      var u = new URLSearchParams(location.search);
      fields.forEach(function (f) {
        var v = u.get(f.name);
        if (v === null) return;
        if (f.tagName === "SELECT" && !f.querySelector('option[value="' + v.replace(/"/g, "") + '"]')) return;
        f.value = v;
      });
      segs.forEach(function (g) { var v = u.get(g.getAttribute("data-name")); if (v !== null) setSeg(g, v); });
    }
    form.addEventListener("submit", function (e) { e.preventDefault(); });
    form.addEventListener("input", function () { apply(true); });
    form.addEventListener("change", function () { apply(true); });
    form.addEventListener("reset", function () {
      setTimeout(function () { segs.forEach(function (g) { setSeg(g, ""); }); apply(true); }, 0);
    });
    segs.forEach(function (g) {
      g.addEventListener("click", function (e) {
        var b = e.target.closest("button");
        if (!b) return;
        setSeg(g, b.getAttribute("data-value"));
        apply(true);
      });
    });
    form.hidden = false;
    apply(false);
  });
})();
