#!/usr/bin/env python3
"""Generate SEO plane pages, sitemap, and update hangar meta helpers."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PLANES_DIR = SITE / "planes"
DATA = SITE / "data" / "planes.json"

TAG_CN = {
    "distance": "远距",
    "time_aloft": "滞空",
    "acrobatic": "特技",
    "decorative": "装饰",
}

SITE_NAME = "纸飞机机库"
# Relative site root for local static hosting; change when deploying to a domain.
BASE_URL = "https://paperplanesworld.wiki"


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def abs_url(path: str) -> str:
    path = path.lstrip("/")
    if BASE_URL:
        return f"{BASE_URL.rstrip('/')}/{path}"
    return f"/{path}" if path else "/"


def meta_desc(plane: dict) -> str:
    text = (plane.get("description") or plane.get("blurb") or "").strip()
    text = " ".join(text.split())
    if len(text) > 150:
        text = text[:147].rstrip() + "…"
    tags = "、".join(TAG_CN.get(t, t) for t in plane.get("tags") or [])
    diff = plane.get("difficultyCn") or plane.get("difficulty") or ""
    extra = f"{diff}难度" + (f"，适合{tags}" if tags else "")
    if not text:
        return f"学习如何折叠纸飞机「{plane['name']}」。{extra}，共 {len(plane.get('steps') or [])} 步图解。"
    return f"{text} {extra}，共 {len(plane.get('steps') or [])} 步。"


def page_title(plane: dict) -> str:
    return f"{plane['name']} 纸飞机叠法 · {SITE_NAME}"


def keywords(plane: dict) -> str:
    parts = [
        plane["name"],
        "纸飞机",
        "叠法",
        "折纸飞机",
        plane.get("difficultyCn") or plane.get("difficulty") or "",
        *[TAG_CN.get(t, t) for t in plane.get("tags") or []],
    ]
    return "，".join(p for p in parts if p)


def render_steps(plane: dict) -> str:
    blocks = []
    for s in plane.get("steps") or []:
        cn = s.get("textCn") or ""
        en = s.get("text") or ""
        body = ""
        if cn and cn != en:
            body = f"<p>{esc(cn)}</p><p class=\"step-en\">{esc(en)}</p>"
        else:
            body = f"<p>{esc(en)}</p>"
        img = esc("../" + s["image"])
        blocks.append(
            f"""
      <article class="step" id="step-{s['n']}">
        <div class="step-media">
          <img src="{img}" alt="{esc(plane['name'])} 第 {s['n']} 步" loading="lazy" width="300" height="390" data-full="{img}" />
        </div>
        <div class="step-copy">
          <h3><span class="n">{s['n']}</span>步骤 {s['n']}</h3>
          {body}
        </div>
      </article>"""
        )
    return "\n".join(blocks)


def howto_jsonld(plane: dict) -> dict:
    steps = []
    for s in plane.get("steps") or []:
        text = s.get("textCn") if s.get("textCn") and s.get("textCn") != s.get("text") else s.get("text")
        steps.append(
            {
                "@type": "HowToStep",
                "position": s["n"],
                "name": f"步骤 {s['n']}",
                "text": text,
                "image": abs_url(s["image"]),
            }
        )
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"如何折叠纸飞机 {plane['name']}",
        "description": plane.get("description") or plane.get("blurb") or "",
        "image": abs_url(plane.get("square") or plane.get("thumb") or ""),
        "totalTime": f"PT{max(5, len(steps) * 2)}M",
        "tool": [{"@type": "HowToTool", "name": "A4 或 Letter 纸"}],
        "step": steps,
    }


def render_plane_page(plane: dict) -> str:
    title = page_title(plane)
    desc = meta_desc(plane)
    kw = keywords(plane)
    slug = plane["slug"]
    path = f"planes/{slug}.html"
    og_image = abs_url(plane.get("square") or plane.get("thumb") or "")
    tags = "".join(
        f'<span class="chip">{esc(TAG_CN.get(t, t))}</span>' for t in plane.get("tags") or []
    )
    cut = (
        '<span class="chip cut">需要剪刀</span>'
        if plane.get("scissors")
        else '<span class="chip">不用剪刀</span>'
    )
    diff = plane.get("difficultyCn") or plane.get("difficulty") or ""
    ld = howto_jsonld(plane)
    web_page = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": abs_url(path),
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": abs_url("")},
        "primaryImageOfPage": abs_url(plane.get("square") or plane.get("thumb") or ""),
    }

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <meta name="keywords" content="{esc(kw)}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{esc(abs_url(path))}" />

  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="{esc(SITE_NAME)}" />
  <meta property="og:locale" content="zh_CN" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{esc(abs_url(path))}" />
  <meta property="og:image" content="{esc(og_image)}" />
  <meta property="og:image:alt" content="{esc(plane['name'])} 纸飞机" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="twitter:image" content="{esc(og_image)}" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Noto+Sans+SC:wght@400;500;700&family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="../styles.css" />
  <script type="application/ld+json">{json.dumps(web_page, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body class="is-detail">
  <div class="sky" aria-hidden="true">
    <div class="cloud c1"></div>
    <div class="cloud c2"></div>
    <div class="cloud c3"></div>
    <div class="vapor"></div>
  </div>

  <header class="topbar">
    <a class="brand" href="../index.html">
      <span class="brand-mark" aria-hidden="true">✈</span>
      <span class="brand-text">
        <strong>纸飞机机库</strong>
        <small>Folding Hangar</small>
      </span>
    </a>
    <div class="topbar-meta">
      <span>{esc(plane['name'])}</span>
    </div>
  </header>

  <main>
    <section class="view detail">
      <a class="btn back" href="../index.html">← 返回机库</a>
      <div class="detail-layout">
        <aside class="detail-aside">
          <img class="square" src="{esc('../' + (plane.get('square') or plane.get('thumb') or ''))}" alt="{esc(plane['name'])}" width="250" height="250" />
          <h1>{esc(plane['name'])}</h1>
          <p class="blurb">{esc(plane.get('description') or plane.get('blurb') or '')}</p>
          <div class="detail-stats">
            <span class="chip diff-{esc(plane.get('difficulty') or '')}">{esc(diff)}</span>
            <span class="chip">{esc(plane.get('paper') or 'Letter & A4')}</span>
            <span class="chip">{len(plane.get('steps') or [])} 步</span>
            {tags}{cut}
          </div>
        </aside>
        <div class="steps">
          <h2 class="steps-title">叠法步骤</h2>
          {render_steps(plane)}
        </div>
      </div>
    </section>
  </main>

  <footer class="site-foot">
    <p>纸飞机机库 · 纯静态叠法图解</p>
  </footer>
  <script src="../plane.js"></script>
</body>
</html>
"""


def hangar_jsonld(planes: list[dict]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"{SITE_NAME} · 58 种纸飞机叠法",
        "description": "58 种经典纸飞机叠法，按远距、滞空、特技与难度筛选，逐步图解。",
        "url": abs_url(""),
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": abs_url("")},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(planes),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "url": abs_url(f"planes/{p['slug']}.html"),
                    "name": p["name"],
                }
                for i, p in enumerate(planes)
            ],
        },
    }


def write_sitemap(planes: list[dict]) -> None:
    urls = [""] + [f"planes/{p['slug']}.html" for p in planes]
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        loc = abs_url(u) if BASE_URL else f"/{u}" if u else "/"
        # For file:// or relative deploys without domain, still emit path-style locs
        if not BASE_URL:
            loc = f"https://example.com/{u}" if u else "https://example.com/"
        body.append("  <url>")
        body.append(f"    <loc>{esc(loc)}</loc>")
        body.append("    <changefreq>monthly</changefreq>")
        body.append(f"    <priority>{'1.0' if not u else '0.8'}</priority>")
        body.append("  </url>")
    body.append("</urlset>")
    # Prefer placeholder note when BASE_URL empty — write relative-friendly sitemap with paths
    if not BASE_URL:
        body = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            "<!-- 部署时请把 BASE_URL 设成正式域名后重新运行 scripts/build_seo_pages.py -->",
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        ]
        for u in urls:
            loc = f"/{u}" if u else "/"
            body += [
                "  <url>",
                f"    <loc>{esc(loc)}</loc>",
                "    <changefreq>monthly</changefreq>",
                f"    <priority>{'1.0' if not u else '0.8'}</priority>",
                "  </url>",
            ]
        body.append("</urlset>")
    (SITE / "sitemap.xml").write_text("\n".join(body) + "\n", encoding="utf-8")


def write_robots() -> None:
    (SITE / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n",
        encoding="utf-8",
    )


def patch_index(planes: list[dict]) -> None:
    index = SITE / "index.html"
    text = index.read_text(encoding="utf-8")
    title = f"{SITE_NAME} · 58 种纸飞机叠法图解"
    desc = "58 种经典纸飞机叠法：远距、滞空、特技与装饰机型，按难度筛选，逐步图解，打开就能折。"
    keywords = "纸飞机,叠法,折纸飞机,纸飞机教程,远距纸飞机,滞空纸飞机,特技纸飞机"
    og = abs_url("assets/planes/1/square.webp")
    ld = hangar_jsonld(planes)
    head = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
  <meta name="keywords" content="{esc(keywords)}" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="{esc(abs_url(''))}" />

  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="{esc(SITE_NAME)}" />
  <meta property="og:locale" content="zh_CN" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{esc(abs_url(''))}" />
  <meta property="og:image" content="{esc(og)}" />
  <meta property="og:image:alt" content="纸飞机机库" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="twitter:image" content="{esc(og)}" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Noto+Sans+SC:wght@400;500;700&family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>"""
    # Replace from start through </head>
    end = text.find("</head>")
    if end == -1:
        raise SystemExit("index.html missing </head>")
    rest = text[end + len("</head>") :]
    # Ensure brand links to index without hash-only
    rest = rest.replace('href="#/"', 'href="index.html"', 1)
    index.write_text(head + rest, encoding="utf-8")


def main() -> None:
    planes = json.loads(DATA.read_text(encoding="utf-8"))
    PLANES_DIR.mkdir(parents=True, exist_ok=True)
    for old in PLANES_DIR.glob("*.html"):
        old.unlink()
    for p in planes:
        out = PLANES_DIR / f"{p['slug']}.html"
        out.write_text(render_plane_page(p), encoding="utf-8")
    write_sitemap(planes)
    write_robots()
    patch_index(planes)
    print(f"generated {len(planes)} plane pages + sitemap/robots")


if __name__ == "__main__":
    main()
