/* GRyS · comportamiento mínimo (el contenido es estático; esto es mejora progresiva)
   - Menús desplegables: <button aria-expanded>, Esc, clic fuera
   - Cajón móvil
   - Cambio de tema claro/oscuro con memoria en localStorage
   - Pestañas accesibles (Equipo, Tesis) con ancla en la URL
   - Filtros de Proyectos y Publicaciones, con su estado en la URL
   - Insignias de Altmetric y Dimensions bajo demanda
   - Buscador del sitio (índice JSON generado al compilar)
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
  /* ---------- Filtros (Proyectos, Publicaciones) ----------
     Marcado: form.filters[data-filter=P] (oculto con «hidden» hasta que este
     script lo muestra), con controles que tienen name (input/select) o grupos
     .seg[data-name] de botones aria-pressed. Elementos asociados por id:
     P-table (filas <tr> con data-<name>) o P-list (elementos .pubdata con
     data-<name>; se oculta su <li> y, si un <ul> se queda vacío, también el
     <ul> y su encabezado de año), P-count (recuento, data-one/data-many) y
     P-empty (aviso sin resultados). Los <select data-prune> pierden las
     opciones que no tiene ningún elemento; si no queda ninguna, no se muestran. Un valor de filtro coincide si está entre los
     valores de data-<name>, separados por espacios; «q» busca en data-q sin
     tener en cuenta mayúsculas ni tildes. El estado se guarda en la URL (?tipo=…). */
  function norm(s) {
    return String(s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }
  Array.prototype.slice.call(document.querySelectorAll("form.filters[data-filter]")).forEach(function (form) {
    var p = form.getAttribute("data-filter");
    var table = document.getElementById(p + "-table") || document.getElementById(p + "-list");
    if (!table) return;
    var isTable = table.tagName === "TABLE";
    var rows = isTable ? Array.prototype.slice.call(table.tBodies[0].rows)
      : Array.prototype.slice.call(table.querySelectorAll(".pubdata"));
    function box(r) { return isTable ? r : (r.closest("li") || r); }
    var count = document.getElementById(p + "-count");
    var empty = document.getElementById(p + "-empty");
    var fields = Array.prototype.slice.call(form.querySelectorAll("input[name], select[name]"));
    var segs = Array.prototype.slice.call(form.querySelectorAll(".seg[data-name]"));
    // Quitar opciones sin elementos (y el desplegable entero si queda vacío)
    fields.forEach(function (f) {
      if (f.tagName !== "SELECT" || !f.hasAttribute("data-prune")) return;
      var have = {};
      rows.forEach(function (r) {
        (r.getAttribute("data-" + f.name) || "").split(/\s+/).forEach(function (v) { if (v) have[v] = true; });
      });
      Array.prototype.slice.call(f.options).forEach(function (o) {
        if (o.value && !have[o.value]) f.removeChild(o);
      });
      if (f.options.length <= 1) {
        f.hidden = true;
        var lb = form.querySelector('label[for="' + f.id + '"]');
        if (lb) lb.hidden = true;
      }
    });

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
        box(r).hidden = !ok;
        if (ok) n++;
      });
      if (!isTable) {
        Array.prototype.slice.call(table.querySelectorAll("ul")).forEach(function (ul) {
          var any = Array.prototype.slice.call(ul.children).some(function (li) { return !li.hidden; });
          ul.hidden = !any;
          var h = ul.previousElementSibling;
          if (h && /^H[1-6]$/.test(h.tagName)) h.hidden = !any;
        });
      }
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
  /* ---------- Insignias de Altmetric y Dimensions (bajo demanda) ----------
     Las insignias (<span class="badges" hidden>) están en el HTML, pero los
     scripts externos solo se cargan cuando el visitante pulsa el botón
     [data-metrics] button (privacidad y rendimiento). La elección se guarda en
     localStorage («grys-metrics») y se aplica en las visitas siguientes. */
  var mbar = document.querySelector("[data-metrics]");
  var METRIC_SCRIPTS = [
    "https://embed.altmetric.com/assets/embed.js",
    "https://integration-badge.dimensions.ai/static/ai/badge.js"
  ];
  var metricsLoaded = false;
  function showMetrics(on) {
    Array.prototype.slice.call(document.querySelectorAll(".badges")).forEach(function (b) { b.hidden = !on; });
    if (on && !metricsLoaded) {
      metricsLoaded = true;
      METRIC_SCRIPTS.forEach(function (src) {
        var s = document.createElement("script");
        s.src = src; s.async = true; s.charset = "utf-8";
        document.body.appendChild(s);
      });
    }
    if (mbar) {
      var b = mbar.querySelector("button");
      b.setAttribute("aria-pressed", String(on));
      b.textContent = b.getAttribute(on ? "data-on" : "data-off");
    }
  }
  if (mbar && document.querySelector(".badges")) {
    var mpref = null;
    try { mpref = localStorage.getItem("grys-metrics"); } catch (e) { /* modo privado */ }
    mbar.hidden = false;
    mbar.querySelector("button").addEventListener("click", function () {
      var on = this.getAttribute("aria-pressed") !== "true";
      try { localStorage.setItem("grys-metrics", on ? "1" : "0"); } catch (e) { /* modo privado */ }
      showMetrics(on);
    });
    if (mpref === "1") showMetrics(true);
  }
  /* ---------- Buscador ----------
     Botón #searchbtn (cabecera) o tecla «/» → diálogo #search. El índice
     (data-index, generado al compilar: _includes/indice-busqueda.json) se
     descarga la primera vez y se busca aquí, sin enviar nada a ningún servidor.
     Búsqueda: sin mayúsculas ni tildes; todas las palabras deben aparecer.
     Orden: título que empieza por la consulta > título que la contiene >
     todas las palabras en el título > el resto; después, por tipo.
     Teclado: Esc cierra; ↓/↑ recorren los resultados; Tab queda dentro del
     diálogo; al cerrar, el foco vuelve a donde estaba. */
  var sdlg = document.getElementById("search");
  var sbtn = document.getElementById("searchbtn");
  if (sdlg && sbtn) {
    var sq = document.getElementById("q");
    var sout = document.getElementById("results");
    var sstatus = document.getElementById("searchstatus");
    var sclose = document.getElementById("searchclose");
    var KIND_ORDER = ["page", "project", "member", "line", "domain", "demo", "news", "event", "repo", "pub"];
    var MAX = 20;
    var sindex = null, sloading = null, slast = null, skinds = {};
    try { skinds = JSON.parse(sdlg.getAttribute("data-kinds") || "{}"); } catch (e) { skinds = {}; }
    sbtn.hidden = false;

    function loadIndex() {
      if (sindex) return Promise.resolve(sindex);
      if (sloading) return sloading;
      sloading = fetch(sdlg.getAttribute("data-index"), { credentials: "same-origin" })
        .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
        .then(function (data) {
          sindex = data.filter(function (i) { return i.k !== "meta"; }).map(function (i, n) {
            i._t = norm(i.t);
            i._h = norm([i.t, i.s, i.x].join(" "));
            i._k = KIND_ORDER.indexOf(i.k);
            i._n = n;
            return i;
          });
          return sindex;
        });
      return sloading;
    }
    function esc(s) {
      return String(s || "").replace(/[&<>"']/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
      });
    }
    function rank(i, q, terms) {
      if (i._t.indexOf(q) === 0) return 0;
      if (i._t.indexOf(q) > 0) return 1;
      if (terms.every(function (w) { return i._t.indexOf(w) >= 0; })) return 2;
      return 3;
    }
    function render() {
      var q = norm(sq.value.trim().replace(/\s+/g, " "));
      if (q.length < 2) { sout.innerHTML = ""; sstatus.textContent = ""; return; }
      if (!sindex) {
        sstatus.textContent = sdlg.getAttribute("data-loading");
        loadIndex().then(render, function () {
          sout.innerHTML = '<li class="datos noresult">' + esc(sdlg.getAttribute("data-error")) + "</li>";
          sstatus.textContent = sdlg.getAttribute("data-error");
          sloading = null;
        });
        return;
      }
      var terms = q.split(" ");
      var hits = sindex.filter(function (i) {
        return terms.every(function (w) { return i._h.indexOf(w) >= 0; });
      }).map(function (i) { return { i: i, r: rank(i, q, terms) }; });
      hits.sort(function (a, b) { return a.r - b.r || a.i._k - b.i._k || a.i._n - b.i._n; });
      var n = hits.length;
      if (!n) {
        sout.innerHTML = '<li class="datos noresult">' + esc(sdlg.getAttribute("data-none")) + "</li>";
      } else {
        sout.innerHTML = hits.slice(0, MAX).map(function (h) {
          var i = h.i;
          return '<li><a href="' + esc(i.u) + '"><span class="kind">' + esc(skinds[i.k] || "") + "</span>" +
            esc(i.t) + (i.s ? "<small>" + esc(i.s) + "</small>" : "") + "</a></li>";
        }).join("") + (n > MAX ? '<li class="datos noresult">' + esc(sdlg.getAttribute("data-more").replace("%n", MAX)) + "</li>" : "");
      }
      sstatus.textContent = n + " " + sdlg.getAttribute(n === 1 ? "data-one" : "data-many");
    }
    function links() { return Array.prototype.slice.call(sout.querySelectorAll("a")); }
    function openSearch() {
      slast = document.activeElement;
      sdlg.hidden = false;
      document.body.classList.add("search-open");
      sq.focus();
      sq.select();
      loadIndex().then(function () { if (sq.value) render(); }, function () {});
    }
    function closeSearch() {
      sdlg.hidden = true;
      document.body.classList.remove("search-open");
      if (slast && slast.focus) slast.focus();
    }
    sbtn.addEventListener("click", openSearch);
    sclose.addEventListener("click", closeSearch);
    sdlg.addEventListener("click", function (e) { if (e.target === sdlg) closeSearch(); });
    sq.addEventListener("input", render);
    sout.addEventListener("click", function (e) { if (e.target.closest("a")) closeSearch(); });
    sdlg.addEventListener("keydown", function (e) {
      var ls = links(), idx = ls.indexOf(document.activeElement);
      if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); closeSearch(); }
      else if (e.key === "ArrowDown" && ls.length) { e.preventDefault(); (ls[idx + 1] || ls[0]).focus(); }
      else if (e.key === "ArrowUp" && ls.length) { e.preventDefault(); if (idx <= 0) sq.focus(); else ls[idx - 1].focus(); }
      else if (e.key === "Tab") {
        // Foco atrapado en el diálogo (aria-modal)
        var f = [sclose, sq].concat(ls), first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key !== "/" || !sdlg.hidden || e.ctrlKey || e.metaKey || e.altKey) return;
      var tg = e.target, tn = tg && tg.tagName;
      if (tn === "INPUT" || tn === "TEXTAREA" || tn === "SELECT" || (tg && tg.isContentEditable)) return;
      e.preventDefault();
      openSearch();
    });
  }
})();
