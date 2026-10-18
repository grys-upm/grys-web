#!/usr/bin/env node
/*
 * Auditoría de accesibilidad con navegador real (Chrome sin ventana + axe-core)
 * sobre el sitio YA COMPILADO.
 *
 *   cd scripts/a11y && npm install && cd ../..     (una vez)
 *   node scripts/a11y/auditar.mjs _site [--estricto] [--solo texto] [--max N]
 *
 * Para cada página HTML (salvo redirecciones), en ES y EN:
 *   · axe-core con las reglas WCAG 2.0/2.1/2.2 A y AA (+ buenas prácticas,
 *     que se informan aparte) en tema OSCURO y en tema CLARO, a 1280 px;
 *   · «reflow» (WCAG 1.4.10): a 320 px de ancho no debe haber desplazamiento
 *     horizontal;
 *   · errores de JavaScript en la consola;
 *   · TECLADO (una página de cada plantilla, a 1280×900 y a 320×256, que
 *     equivale a un zoom del 400 % en una pantalla de 1280×1024): se recorre la
 *     página con el tabulador y se comprueba que el primer Tab lleva al enlace
 *     «Saltar al contenido» (2.4.1), que el foco se ve (2.4.7), que la cabecera
 *     fija no lo tapa (2.4.11) y que no hay trampas de teclado (2.1.2).
 * Solo se cargan recursos del propio sitio (YouTube, OpenStreetMap,
 * Altmetric… se bloquean): se audita nuestro contenido, de forma repetible.
 * Escribe reports/a11y/axe.json y reports/a11y/axe.md. Sale con 1 solo con
 * --estricto si hay incumplimientos WCAG, problemas de reflow o de teclado, o errores JS.
 */
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { createRequire } from "node:module";
import puppeteer from "puppeteer";

const require = createRequire(import.meta.url);
const AXE = fs.readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");
const AXE_VERSION = JSON.parse(fs.readFileSync(require.resolve("axe-core/package.json"), "utf8")).version;
export const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];
const TAGS = WCAG_TAGS.concat(["best-practice"]);
const CONCURRENCIA = 4;
const MAX_TAB = 250;            // pulsaciones de Tab por página como máximo
const VISTAS_TECLADO = { "teclado": { width: 1280, height: 900 }, "teclado-400": { width: 320, height: 256 } };
// Fichas de detalle: se audita la más grande de cada tipo (la que tiene más componentes)
const DETALLES = [/^\/grupo\/equipo\/[^/]+\/$/, /^\/investigacion\/lineas\/[^/]+\/$/,
  /^\/investigacion\/proyectos\/[^/]+\/$/, /^\/actualidad\/noticias\/[^/]+\/$/];

// ------------------------------------------------------------------ argumentos
const args = process.argv.slice(2);
const SITE = path.resolve(args.find(a => !a.startsWith("--") && !/^\d+$/.test(a)) || "_site");
const ESTRICTO = args.includes("--estricto");
const opt = n => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : null; };
const SOLO = opt("--solo");
const MAX = opt("--max") ? parseInt(opt("--max"), 10) : Infinity;
const OUTDIR = path.resolve("reports", "a11y");

// ------------------------------------------------------------------ páginas
export function listarPaginas(site) {
  const out = [];
  (function walk(d) {
    for (const f of fs.readdirSync(d, { withFileTypes: true })) {
      const p = path.join(d, f.name);
      if (f.isDirectory()) walk(p);
      else if (f.name.endsWith(".html")) {
        const html = fs.readFileSync(p, "utf8");
        if (/http-equiv=["']?refresh/i.test(html)) continue;   // redirecciones
        if (html.includes('name="grys-herramienta"')) continue;   // gestor de contenidos (no es del sitio público)
        let url = "/" + path.relative(site, p).split(path.sep).join("/");
        url = url.replace(/index\.html$/, "");
        out.push(url);
      }
    }
  })(site);
  return out.sort();
}

// Páginas para la pasada de teclado: todas las páginas de primer y segundo
// nivel en español, la ficha más grande de cada tipo y la portada en inglés.
export function paginasTeclado(paginas, site) {
  const tam = p => { try { return fs.statSync(path.join(site, p, p.endsWith("/") ? "index.html" : "")).size; } catch (e) { return 0; } };
  const sel = [];
  for (const p of paginas) {
    if (p.startsWith("/en/") || DETALLES.some(r => r.test(p))) continue;
    if (p.split("/").filter(Boolean).length <= 2) sel.push(p);
  }
  for (const r of DETALLES) {
    const c = paginas.filter(p => r.test(p)).sort((x, y) => tam(y) - tam(x));
    if (c.length) sel.push(c[0]);
  }
  if (paginas.includes("/en/")) sel.push("/en/");
  return sel;
}

// Estado del elemento con el foco (se ejecuta en la página). Si el indicador no
// se ve, se vuelve a medir tras dos fotogramas: el estilo :focus-visible puede
// aplicarse un instante después de la pulsación.
async function estadoFoco() {
  const el = document.activeElement;
  if (!el || el === document.body || el === document.documentElement) return null;
  if (!el.dataset.a11yN) el.dataset.a11yN = String((window.__a11yN = (window.__a11yN || 0) + 1));
  const cls = typeof el.className === "string" && el.className.trim() ? "." + el.className.trim().split(/\s+/).join(".") : "";
  const txt = (el.getAttribute("aria-label") || el.textContent || el.getAttribute("title") || "").trim().replace(/\s+/g, " ").slice(0, 40);
  const desc = el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") + cls + (txt ? " «" + txt + "»" : "");
  const iframe = el.tagName === "IFRAME";
  const medir = () => {
    const b = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    const contorno = cs.outlineStyle !== "none" && parseFloat(cs.outlineWidth) > 0;
    const sombra = cs.boxShadow && cs.boxShadow !== "none";
    return { b, ok: iframe || ((contorno || sombra) && b.width > 0 && b.height > 0) };
  };
  let m = medir();
  if (!m.ok) {
    await new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
    m = medir();
  }
  const r = m.b;
  const visible = m.ok;
  let tapado = false;
  const cab = document.querySelector("header.site");
  if (cab && !cab.contains(el) && /sticky|fixed/.test(getComputedStyle(cab).position)) {
    const c = cab.getBoundingClientRect();
    tapado = r.height > 0 && r.top >= c.top - 1 && r.bottom <= c.bottom + 1;
  }
  return { clave: el.dataset.a11yN, desc, iframe, visible, tapado, salto: el.classList.contains("skip"),
    pestanaConFoco: document.hasFocus() };
}

// ------------------------------------------------------------------ servidor
const MIME = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript",
  ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".webp": "image/webp",
  ".jpg": "image/jpeg", ".ico": "image/x-icon", ".woff2": "font/woff2", ".xml": "application/xml",
  ".pdf": "application/pdf", ".txt": "text/plain" };
export function servir(site) {
  return new Promise(resolve => {
    const srv = http.createServer((req, res) => {
      const p = decodeURIComponent(req.url.split("?")[0].split("#")[0]);
      let f = path.join(site, p);
      if (!f.startsWith(site)) { res.writeHead(403); return res.end(); }
      if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, "index.html");
      if (!fs.existsSync(f)) { res.writeHead(404); return res.end("404"); }
      res.writeHead(200, { "Content-Type": MIME[path.extname(f)] || "application/octet-stream" });
      fs.createReadStream(f).pipe(res);
    });
    srv.listen(0, "127.0.0.1", () => resolve(srv));
  });
}

// ------------------------------------------------------------------ una pasada
async function pasada(browser, base, url, modo) {
  const page = await browser.newPage();
  const errores = [];
  try {
    const reflow = modo === "reflow";
    const teclado = VISTAS_TECLADO[modo];
    await page.setViewport(teclado || { width: reflow ? 320 : 1280, height: reflow ? 640 : 900 });
    const tema = modo === "claro" ? "light" : "dark";
    await page.evaluateOnNewDocument(t => { try { localStorage.setItem("grys-theme", t); } catch (e) { /* */ } }, tema);
    await page.setRequestInterception(true);
    page.on("request", r => ((r.url().startsWith(base) || r.url().startsWith("data:")) ? r.continue() : r.abort()));
    page.on("pageerror", e => errores.push(String((e && e.message) || e)));
    page.on("console", m => {
      if (m.type() === "error" && !/Failed to load resource|ERR_FAILED|ERR_BLOCKED/i.test(m.text())) errores.push(m.text());
    });
    await page.goto(base + url, { waitUntil: "load", timeout: 30000 });
    await page.evaluate(() => (document.fonts ? document.fonts.ready.then(() => true) : true));
    if (teclado) {
      if (page.bringToFront) await page.bringToFront();
      return { teclado: await recorrerConTab(page), errores };
    }
    if (reflow) {
      const r = await page.evaluate(() => {
        const w = window.innerWidth, sw = document.documentElement.scrollWidth;
        if (sw <= w + 1) return null;
        const culpables = [];
        for (const el of document.body.querySelectorAll("*")) {
          const b = el.getBoundingClientRect();
          if (b.right > w + 1 && b.width > 0 && getComputedStyle(el).position !== "fixed") {
            const cls = typeof el.className === "string" && el.className.trim() ? "." + el.className.trim().split(/\s+/).join(".") : "";
            culpables.push({ desc: el.tagName.toLowerCase() + (el.id ? "#" + el.id : "") + cls, right: Math.round(b.right) });
          }
        }
        culpables.sort((a, b) => b.right - a.right);
        return { scrollWidth: sw, culpables: culpables.slice(0, 3) };
      });
      return { reflow: r, errores };
    }
    await page.addScriptTag({ content: AXE });
    const res = await page.evaluate(async tags => {
      // eslint-disable-next-line no-undef
      const r = await axe.run(document, { runOnly: { type: "tag", values: tags }, iframes: false,
        resultTypes: ["violations", "incomplete"] });
      const corta = v => ({ id: v.id, impact: v.impact, tags: v.tags, help: v.help, helpUrl: v.helpUrl,
        nodes: v.nodes.map(n => ({ target: [].concat(n.target).join(" "), html: String(n.html).slice(0, 200),
          summary: String(n.failureSummary || "").slice(0, 300) })) });
      return { violations: r.violations.map(corta), incomplete: r.incomplete.map(v => ({ id: v.id, n: v.nodes.length })) };
    }, TAGS);
    return { ...res, errores };
  } catch (e) {
    return { fallo: String((e && e.message) || e), errores };
  } finally {
    await page.close().catch(() => {});
  }
}

// Recorre la página con el tabulador hasta que el foco sale de la página,
// vuelve a un elemento ya visitado o se llega a MAX_TAB.
export async function recorrerConTab(page) {
  const hallazgos = [];
  const vistos = new Set();
  let previo = null, repetido = 0;
  for (let n = 0; n < MAX_TAB; n++) {
    await page.keyboard.press("Tab");
    const f = await page.evaluate(estadoFoco);
    if (!f) break;
    if (n === 0 && !f.salto) hallazgos.push({ tipo: "sin-salto", desc: f.desc });
    if (f.clave === previo) {
      // El foco no se ha movido. Un iframe (vídeo) puede retenerlo unas pulsaciones mientras recorre su contenido.
      if (++repetido >= (f.iframe ? 15 : 1)) { hallazgos.push({ tipo: "trampa", desc: f.desc }); break; }
      continue;
    }
    repetido = 0;
    previo = f.clave;
    if (vistos.has(f.clave)) break;           // ha dado la vuelta
    vistos.add(f.clave);
    if (!f.visible && f.pestanaConFoco !== false) hallazgos.push({ tipo: "foco-invisible", desc: f.desc });
    if (f.tapado) hallazgos.push({ tipo: "foco-tapado", desc: f.desc });
  }
  return hallazgos;
}

// ------------------------------------------------------------------ informe
export function agregar(resultados) {
  const reglas = new Map(), incompletos = new Map(), reflow = [], js = [], fallos = [], teclado = [];
  let nTeclado = 0;
  for (const { url, modo, r } of resultados) {
    if (r.fallo) { fallos.push({ url, modo, fallo: r.fallo }); continue; }
    for (const e of r.errores || []) js.push({ url, modo, error: e });
    if (r.teclado) { nTeclado++; for (const h of r.teclado) teclado.push({ url, modo, ...h }); }
    if (r.reflow) reflow.push({ url, ...r.reflow });
    for (const v of r.violations || []) {
      const g = reglas.get(v.id) || { id: v.id, impact: v.impact, help: v.help, helpUrl: v.helpUrl,
        wcag: v.tags.filter(t => /^wcag\d{3,}$/.test(t)).map(t => t.slice(4, 5) + "." + t.slice(5, 6) + "." + t.slice(6)),
        bp: !v.tags.some(t => WCAG_TAGS.includes(t)),
        paginas: new Set(), modos: new Set(), nodos: 0, ejemplos: new Map() };
      g.paginas.add(url); g.modos.add(modo); g.nodos += v.nodes.length;
      for (const n of v.nodes) {
        const k = n.target + "|" + n.html;
        if (!g.ejemplos.has(k) && g.ejemplos.size < 6) g.ejemplos.set(k, { url, modo, ...n });
      }
      reglas.set(v.id, g);
    }
    for (const i of r.incomplete || []) incompletos.set(i.id, (incompletos.get(i.id) || 0) + i.n);
  }
  return { reglas: [...reglas.values()], incompletos, reflow, js, fallos, teclado, nTeclado };
}

const TECLADO = {
  "sin-salto": ["2.4.1", "el primer Tab no lleva a «Saltar al contenido»"],
  "foco-invisible": ["2.4.7", "el elemento con el foco no muestra indicador"],
  "foco-tapado": ["2.4.11", "la cabecera fija tapa el elemento con el foco"],
  "trampa": ["2.1.2", "el foco no sale del elemento con el tabulador"],
};
const IMPACTO = { critical: "crítico", serious: "grave", moderate: "moderado", minor: "leve" };
const ORDEN = { critical: 0, serious: 1, moderate: 2, minor: 3 };
const md = s => String(s).replace(/\|/g, "\\|").replace(/</g, "&lt;").replace(/`/g, "'").replace(/\n/g, " ");

export function informe(ag, n, extra = {}) {
  const wcag = ag.reglas.filter(g => !g.bp)
    .sort((a, b) => (ORDEN[a.impact] ?? 9) - (ORDEN[b.impact] ?? 9) || b.paginas.size - a.paginas.size);
  const bp = ag.reglas.filter(g => g.bp).sort((a, b) => b.paginas.size - a.paginas.size);
  const L = [];
  L.push("## Accesibilidad · auditoría con navegador (axe-core)", "");
  L.push(`${n} páginas × 3 pasadas (tema oscuro, tema claro, 320 px) · teclado: ${ag.nTeclado || 0} pasadas (1280×900 y 320×256) · axe-core ${extra.axe || ""}`, "");
  L.push(`- **Incumplimientos WCAG 2.2 A/AA: ${wcag.length} reglas** en ${new Set(wcag.flatMap(g => [...g.paginas])).size} páginas`);
  L.push(`- Reflow a 320 px (1.4.10): **${ag.reflow.length}** páginas con desplazamiento horizontal`);
  L.push(`- Teclado y foco (2.1.2, 2.4.1, 2.4.7, 2.4.11): **${(ag.teclado || []).length}** hallazgos`);
  L.push(`- Errores de JavaScript: **${ag.js.length}**`);
  L.push(`- Buenas prácticas (no WCAG): ${bp.length} reglas`);
  if (ag.fallos.length) L.push(`- ⚠️ Pasadas que no se pudieron completar: ${ag.fallos.length}`);
  const tabla = (lista, titulo) => {
    if (!lista.length) return;
    L.push("", `### ${titulo}`, "", "| Regla | Impacto | WCAG | Páginas | Nodos | Pasadas | Qué pide |", "|---|---|---|---|---|---|---|");
    for (const g of lista) {
      L.push(`| [\`${g.id}\`](${g.helpUrl}) | ${IMPACTO[g.impact] || g.impact || ""} | ${g.wcag.join(", ")} | ${g.paginas.size} | ${g.nodos} | ${[...g.modos].join(", ")} | ${md(g.help)} |`);
    }
    for (const g of lista) {
      L.push("", `<details><summary><code>${g.id}</code>: ejemplos</summary>`, "");
      for (const e of g.ejemplos.values()) {
        L.push(`- \`${e.url}\` (${e.modo}) · \`${md(e.target)}\``, `  - \`${md(e.html)}\``);
        if (e.summary) L.push(`  - ${md(e.summary)}`);
      }
      L.push("", "</details>");
    }
  };
  tabla(wcag, "Incumplimientos WCAG");
  if (ag.reflow.length) {
    L.push("", "### Reflow a 320 px", "");
    for (const r of ag.reflow.slice(0, 30)) {
      L.push(`- \`${r.url}\`: ancho ${r.scrollWidth} px · ${r.culpables.map(c => "`" + md(c.desc) + "` (" + c.right + ")").join(", ")}`);
    }
  }
  if ((ag.teclado || []).length) {
    L.push("", "### Teclado y foco", "", "| Página | Vista | WCAG | Problema | Elemento |", "|---|---|---|---|---|");
    for (const h of ag.teclado.slice(0, 60)) {
      const [c, q] = TECLADO[h.tipo] || ["", h.tipo];
      L.push(`| \`${h.url}\` | ${h.modo} | ${c} | ${q} | \`${md(h.desc)}\` |`);
    }
  }
  if (ag.js.length) {
    L.push("", "### Errores de JavaScript", "");
    const vistos = new Map();
    for (const e of ag.js) if (!vistos.has(e.error)) vistos.set(e.error, e);
    for (const e of [...vistos.values()].slice(0, 20)) L.push(`- \`${e.url}\` (${e.modo}): ${md(e.error.slice(0, 200))}`);
  }
  tabla(bp, "Buenas prácticas (no son requisitos WCAG)");
  if (ag.incompletos.size) {
    L.push("", "### Para revisar a mano (axe no puede decidir)", "");
    L.push([...ag.incompletos.entries()].sort((a, b) => b[1] - a[1]).map(([k, v]) => `\`${k}\` (${v})`).join(" · "));
  }
  if (ag.fallos.length) {
    L.push("", "### Pasadas no completadas", "");
    for (const f of ag.fallos.slice(0, 20)) L.push(`- \`${f.url}\` (${f.modo}): ${md(f.fallo.slice(0, 200))}`);
  }
  return { texto: L.join("\n") + "\n", wcag: wcag.length };
}

// ------------------------------------------------------------------ principal
async function main() {
  let paginas = listarPaginas(SITE);
  if (SOLO) paginas = paginas.filter(p => p.includes(SOLO));
  paginas = paginas.slice(0, MAX);
  const srv = await servir(SITE);
  const base = `http://127.0.0.1:${srv.address().port}`;
  const browser = await puppeteer.launch({ headless: true, args: ["--no-sandbox", "--disable-dev-shm-usage"] });
  const tareas = [];
  for (const url of paginas) for (const modo of ["oscuro", "claro", "reflow"]) tareas.push({ url, modo });
  // El teclado va aparte y en serie: con varias pestañas a la vez solo la que
  // está al frente tiene el foco real, y :focus-visible no es fiable en las demás.
  const tareasTeclado = [];
  for (const url of paginasTeclado(paginas, SITE)) for (const modo of Object.keys(VISTAS_TECLADO)) tareasTeclado.push({ url, modo });
  const resultados = [];
  let i = 0;
  const t0 = Date.now();
  async function trabajador() {
    while (i < tareas.length) {
      const t = tareas[i++];
      resultados.push({ ...t, r: await pasada(browser, base, t.url, t.modo) });
      if (resultados.length % 60 === 0) console.log(`auditar: ${resultados.length}/${tareas.length}`);
    }
  }
  await Promise.all(Array.from({ length: CONCURRENCIA }, trabajador));
  for (const t of tareasTeclado) resultados.push({ ...t, r: await pasada(browser, base, t.url, t.modo) });
  await browser.close();
  srv.close();
  const ag = agregar(resultados);
  const { texto, wcag } = informe(ag, paginas.length, { axe: AXE_VERSION });
  fs.mkdirSync(OUTDIR, { recursive: true });
  fs.writeFileSync(path.join(OUTDIR, "axe.md"), texto);
  fs.writeFileSync(path.join(OUTDIR, "axe.json"), JSON.stringify(resultados, null, 1));
  console.log(`auditar: ${paginas.length} páginas en ${Math.round((Date.now() - t0) / 1000)} s · ` +
    `${wcag} reglas WCAG incumplidas · reflow ${ag.reflow.length} · teclado ${ag.teclado.length} · errores JS ${ag.js.length} · ` +
    `no completadas ${ag.fallos.length} → reports/a11y/axe.md`);
  // DETALLE EN EL REGISTRO: lo imprescindible para corregir, sin tener que abrir el informe
  for (const g of ag.reglas.filter(r => !r.bp)) {
    const e = [...g.ejemplos.values()][0];
    console.log(`  WCAG ${g.id} (${g.wcag.join(", ")}): ${g.paginas.size} páginas · p. ej. ${e.url} · ${e.target}`);
  }
  for (const r of ag.reflow) {
    console.log(`  REFLOW ${r.url}: ${r.scrollWidth} px · ${r.culpables.map(c => c.desc + " (" + c.right + ")").join(", ")}`);
  }
  for (const h of ag.teclado.slice(0, 20)) {
    const [c, q] = TECLADO[h.tipo] || ["", h.tipo];
    console.log(`  TECLADO ${h.url} (${h.modo}) ${c}: ${q} · ${h.desc}`);
  }
  for (const e of ag.js.slice(0, 10)) console.log(`  JS ${e.url} (${e.modo}): ${e.error.slice(0, 160)}`);
  for (const f of ag.fallos.slice(0, 10)) console.log(`  NO COMPLETADA ${f.url} (${f.modo}): ${f.fallo.slice(0, 160)}`);
  if (ESTRICTO && (wcag || ag.reflow.length || ag.teclado.length || ag.js.length || ag.fallos.length)) process.exit(1);
}

if (!process.env.GRYS_A11Y_SIN_MAIN) {
  main().catch(e => { console.error(e); process.exit(2); });
}
