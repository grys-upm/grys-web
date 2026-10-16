/* GRyS · comportamiento mínimo (el contenido es estático; esto es mejora progresiva)
   - Menús desplegables: <button aria-expanded>, Esc, clic fuera
   - Cajón móvil
   - Cambio de tema claro/oscuro con memoria en localStorage
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
})();
