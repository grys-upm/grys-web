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
 *   · errores de JavaScript en la consola.
 * Solo se cargan recursos del propio sitio (YouTube, OpenStreetMap,
 * Altmetric… se bloquean): se audita nuestro contenido, de forma repetible.
 * Escribe reports/a11y/axe.json y reports/a11y/axe.md. Sale con 1 solo con
 * --estricto si hay incumplimientos WCAG, problemas de reflow o errores JS.
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
        let url = "/" + path.relative(site, p).split(path.sep).join("/");
        url = url.replace(/index\.html$/, "");
        out.push(url);
      }
    }
  })(site);
  return out.sort();
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
    await page.setViewport({ width: reflow ? 320 : 1280, height: reflow ? 640 : 900 });
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

// ------------------------------------------------------------------ informe
export function agregar(resultados) {
  const reglas = new Map(), incompletos = new Map(), reflow = [], js = [], fallos = [];
  for (const { url, modo, r } of resultados) {
    if (r.fallo) { fallos.push({ url, modo, fallo: r.fallo }); continue; }
    for (const e of r.errores || []) js.push({ url, modo, error: e });
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
  return { reglas: [...reglas.values()], incompletos, reflow, js, fallos };
}

const IMPACTO = { critical: "crítico", serious: "grave", moderate: "moderado", minor: "leve" };
const ORDEN = { critical: 0, serious: 1, moderate: 2, minor: 3 };
const md = s => String(s).replace(/\|/g, "\\|").replace(/</g, "&lt;").replace(/`/g, "'").replace(/\n/g, " ");

export function informe(ag, n, extra = {}) {
  const wcag = ag.reglas.filter(g => !g.bp)
    .sort((a, b) => (ORDEN[a.impact] ?? 9) - (ORDEN[b.impact] ?? 9) || b.paginas.size - a.paginas.size);
  const bp = ag.reglas.filter(g => g.bp).sort((a, b) => b.paginas.size - a.paginas.size);
  const L = [];
  L.push("## Accesibilidad · auditoría con navegador (axe-core)", "");
  L.push(`${n} páginas × 3 pasadas (tema oscuro, tema claro, 320 px) · axe-core ${extra.axe || ""}`, "");
  L.push(`- **Incumplimientos WCAG 2.2 A/AA: ${wcag.length} reglas** en ${new Set(wcag.flatMap(g => [...g.paginas])).size} páginas`);
  L.push(`- Reflow a 320 px (1.4.10): **${ag.reflow.length}** páginas con desplazamiento horizontal`);
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
  await browser.close();
  srv.close();
  const ag = agregar(resultados);
  const { texto, wcag } = informe(ag, paginas.length, { axe: AXE_VERSION });
  fs.mkdirSync(OUTDIR, { recursive: true });
  fs.writeFileSync(path.join(OUTDIR, "axe.md"), texto);
  fs.writeFileSync(path.join(OUTDIR, "axe.json"), JSON.stringify(resultados, null, 1));
  console.log(`auditar: ${paginas.length} páginas en ${Math.round((Date.now() - t0) / 1000)} s · ` +
    `${wcag} reglas WCAG incumplidas · reflow ${ag.reflow.length} · errores JS ${ag.js.length} · ` +
    `no completadas ${ag.fallos.length} → reports/a11y/axe.md`);
  if (ESTRICTO && (wcag || ag.reflow.length || ag.js.length || ag.fallos.length)) process.exit(1);
}

if (!process.env.GRYS_A11Y_SIN_MAIN) {
  main().catch(e => { console.error(e); process.exit(2); });
}
