// Cloudflare Pages SEO: publish this host as canonical; keep GitHub Pages noindex.
const SITE = "https://banned21records.pages.dev";
const SOURCE = "https://olivermend.github.io/Banned21records-web";
const PAGES = ["/", "/auxkalo/es/", "/auxkalo/eu/", "/auxkalo/en/"];

function indexable(path) {
  return path === "/" || path === "/index.html" ||
    /^\/auxkalo\/(?:es|eu|en)\/(?:index\.html)?$/.test(path);
}

function sitemapXml() {
  const links = PAGES.map((path) => {
    const alternatives = path.startsWith("/auxkalo/")
      ? ["es", "eu", "en"].map((lang) =>
          '    <xhtml:link rel="alternate" hreflang="' + lang +
          '" href="' + SITE + "/auxkalo/" + lang + '/"/>'
        ).join("\n")
      : "";
    return "  <url>\n    <loc>" + SITE + path + "</loc>\n" +
      (alternatives ? alternatives + "\n" : "") + "  </url>";
  }).join("\n");
  return '<?xml version="1.0" encoding="UTF-8"?>\n' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" ' +
    'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + links + '\n</urlset>\n';
}

export async function onRequest(context) {
  const url = new URL(context.request.url);
  if (url.hostname !== "banned21records.pages.dev" || context.request.method !== "GET") {
    return context.next();
  }

  if (url.pathname === "/robots.txt") {
    return new Response(
      "User-agent: *\nAllow: /\n\nSitemap: " + SITE + "/sitemap.xml\n",
      { headers: { "content-type": "text/plain; charset=utf-8" } }
    );
  }
  if (url.pathname === "/sitemap.xml") {
    return new Response(sitemapXml(), {
      headers: { "content-type": "application/xml; charset=utf-8" }
    });
  }

  const response = await context.next();
  if (response.status !== 200 ||
      !(response.headers.get("content-type") || "").toLowerCase().includes("text/html")) {
    return response;
  }

  let html = await response.text();
  // All visible canonical, hreflang, OpenGraph, and schema.org URL hints
  // should refer to the official Cloudflare publication, never personal GitHub.
  html = html.split(SOURCE).join(SITE);

  if (indexable(url.pathname)) {
    const robots = '<meta name="robots" content="index, follow, max-image-preview:large">';
    const existingRobots = /<meta\s+name=["']robots["']\s+content=["'][^"']*["']\s*\/?>/i;
    html = existingRobots.test(html)
      ? html.replace(existingRobots, robots)
      : html.replace(/<head[^>]*>/i, (head) => head + "\n" + robots);
  }

  const headers = new Headers(response.headers);
  headers.delete("content-length");
  headers.delete("content-encoding");
  headers.delete("etag");
  return new Response(html, {
    status: response.status,
    statusText: response.statusText,
    headers
  });
}
