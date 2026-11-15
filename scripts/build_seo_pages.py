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

TAG_EN = {
    "distance": "Distance",
    "time_aloft": "Time aloft",
    "acrobatic": "Acrobatic",
    "decorative": "Decorative",
}

SITE_NAME = "Paper Planes World"
# Relative site root for local static hosting; change when deploying to a domain.
BASE_URL = "https://paperairplaneworld.wiki"


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def abs_url(path: str) -> str:
    path = path.lstrip("/")
    if BASE_URL:
        return f"{BASE_URL.rstrip('/')}/{path}"
    return f"/{path}" if path else "/"


def meta_desc(plane: dict) -> str:
    tags = ", ".join(TAG_EN.get(t, t) for t in plane.get("tags") or [])
    diff = plane.get("difficulty") or ""
    details = []
    if diff:
        details.append(f"{diff} difficulty")
    if tags:
        details.append(f"{tags} flyer")
    details.append(f"{len(plane.get('steps') or [])}-step illustrated guide")
    details.append("scissors needed" if plane.get("scissors") else "no scissors required")
    return f"Learn how to fold the {plane['name']} paper airplane: {', '.join(details)}."


def page_title(plane: dict) -> str:
    return f"{plane['name']} Paper Airplane · Step-by-Step Folding Guide"


def keywords(plane: dict) -> str:
    parts = [
        plane["name"],
        "paper airplane",
        "paper plane",
        "folding guide",
        "origami",
        plane.get("difficulty") or "",
        *[TAG_EN.get(t, t) for t in plane.get("tags") or []],
    ]
    return ", ".join(p for p in parts if p)


def render_steps(plane: dict) -> str:
    blocks = []
    for s in plane.get("steps") or []:
        cn = s.get("textCn") or ""
        en = s.get("text") or ""
        if cn and cn != en:
            body = (
                f'<p class="lang-en">{esc(en)}</p>'
                f'<p class="lang-zh">{esc(cn)}</p>'
            )
        else:
            body = f"<p>{esc(en)}</p>"
        img = esc("../" + s["image"])
        blocks.append(
            f"""
      <article class="step" id="step-{s['n']}">
        <div class="step-media">
          <img src="{img}" alt="{esc(plane['name'])} step {s['n']}" loading="lazy" width="300" height="390" data-full="{img}" />
        </div>
        <div class="step-copy">
          <h3 data-step="{s['n']}"><span class="n">{s['n']}</span>Step {s['n']}</h3>
          {body}
        </div>
      </article>"""
        )
    return "\n".join(blocks)


def howto_jsonld(plane: dict) -> dict:
    steps = []
    for s in plane.get("steps") or []:
        text = s.get("text") or s.get("textCn") or ""
        steps.append(
            {
                "@type": "HowToStep",
                "position": s["n"],
                "name": f"Step {s['n']}",
                "text": text,
                "image": abs_url(s["image"]),
            }
        )
    data = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": f"How to Fold a {plane['name']} Paper Airplane",
        "description": meta_desc(plane),
        "image": abs_url(plane.get("square") or plane.get("thumb") or ""),
        "supply": [
            {
                "@type": "HowToSupply",
                "name": plane.get("paper") or "Letter or A4 paper",
            }
        ],
        "step": steps,
    }
    if plane.get("scissors"):
        data["tool"] = [{"@type": "HowToTool", "name": "Scissors"}]
    return data


def build_ranks(planes: list[dict]) -> dict:
    def ranked(key: str) -> dict:
        pool = sorted(
            (p for p in planes if p.get(key)), key=lambda p: -p[key]
        )
        return {p["slug"]: i + 1 for i, p in enumerate(pool)}

    scored = {key: ranked(key) for key in ("distanceScore", "timeScore")}
    total = {
        key: sum(1 for p in planes if p.get(key)) for key in scored
    }
    return {"rank": scored, "total": total}


def perf_values(plane: dict) -> dict:
    """Turn the in-site 0-430 / 0-388 scores into estimated metric ranges."""
    d = plane.get("distanceScore") or 0
    t = plane.get("timeScore") or 0
    dist = None
    if d >= 40:
        base = d * 0.06
        dist = (round(base * 0.85), round(base * 1.15))
    time = None
    if t >= 40:
        base = t * 0.03
        time = (round(base * 0.85), round(base * 1.15))
    return {"distance": dist, "time": time}


def plane_kind(plane: dict) -> str:
    tags = plane.get("tags") or []
    if "time_aloft" in tags and "distance" in tags:
        return "glider"
    if "time_aloft" in tags:
        return "glider"
    if "acrobatic" in tags:
        return "stunt plane"
    if "decorative" in tags:
        return "display model"
    return "dart"


THROW_TIPS = {
    "glider": "Launch gently at a slight upward angle, ideally from a high spot, and let it settle into a glide instead of throwing it hard.",
    "distance": "Hold the plane level and throw with a smooth, firm push, aiming straight ahead rather than upward.",
    "time_aloft": "Launch softly at a slight upward angle, ideally from a high point, and let the plane glide instead of forcing it.",
    "acrobatic": "Use a quick wrist snap and a fairly firm throw so the plane has enough speed to complete its maneuver.",
    "decorative": "This design is made for display; if you fly it, use a gentle toss and expect a short, floaty descent.",
}

THROW_TIPS_ZH = {
    "glider": "以略向上扬的角度轻轻放出，最好从高处投掷，让它自然进入滑翔，不要用力硬抛。",
    "distance": "让机身保持水平，用平稳有力的推送直线投出，不要向上抛。",
    "time_aloft": "以略向上扬的角度轻轻放出，最好从高处投掷，让飞机自然滑翔，不要用力硬抛。",
    "acrobatic": "用手腕快速抖动、稍用力投出，让飞机有足够速度完成动作。",
    "decorative": "这类机型更适合摆放展示；如果要试飞，请轻投，并预期较短的飘落距离。",
}


def primary_tag(plane: dict) -> str:
    tags = plane.get("tags") or []
    if "distance" in tags and "time_aloft" in tags:
        return "glider"
    for key in ("distance", "time_aloft", "acrobatic", "decorative"):
        if key in tags:
            return key
    return "distance"


def faq_pairs(plane: dict, ranks: dict) -> list[tuple[str, str, str, str]]:
    """Return (question_en, answer_en, question_zh, answer_zh)."""
    name = plane["name"]
    vals = perf_values(plane)
    diff = plane.get("difficulty") or ""
    kind = plane_kind(plane)
    tags = " and ".join(TAG_EN.get(t, t).lower() for t in plane.get("tags") or [])
    paper = plane.get("paper") or "Letter or A4 paper"
    n = len(plane.get("steps") or [])
    rank_dist = ranks["rank"]["distanceScore"].get(plane["slug"])
    rank_time = ranks["rank"]["timeScore"].get(plane["slug"])
    total_dist = ranks["total"]["distanceScore"]
    total_time = ranks["total"]["timeScore"]
    tip_en = THROW_TIPS[primary_tag(plane)]
    tip_zh = THROW_TIPS_ZH[primary_tag(plane)]

    if vals["distance"]:
        d_lo, d_hi = vals["distance"]
        dist_en = f"roughly {d_lo}–{d_hi} metres (about {round(d_lo * 3.28)}–{round(d_hi * 3.28)} feet)"
        dist_zh = f"大约 {d_lo}–{d_hi} 米"
        dist_rank_en = (
            f" Among the {total_dist} distance-rated designs in this collection it ranks #{rank_dist}."
            if rank_dist
            else ""
        )
        dist_rank_zh = f"在站内 {total_dist} 款远距机型中排第 {rank_dist}。" if rank_dist else ""
    else:
        dist_en = "only a short distance, since this design is not built for range"
        dist_zh = "距离很短，这款机型本身并不以远距为目标"
        dist_rank_en = dist_rank_zh = ""

    if vals["time"]:
        t_lo, t_hi = vals["time"]
        time_en = f"about {t_lo}–{t_hi} seconds of hang time"
        time_zh = f"大约 {t_lo}–{t_hi} 秒"
        time_rank_en = (
            f" That places it #{rank_time} of {total_time} designs for time aloft."
            if rank_time
            else ""
        )
        time_rank_zh = f"在站内 {total_time} 款机型中滞空排第 {rank_time}。" if rank_time else ""
    else:
        time_en = "a very brief flight; the design is not aimed at hang time"
        time_zh = "滞空时间很短，这类机型并不追求滞空"
        time_rank_en = time_rank_zh = ""

    return [
        (
            f"How far can the {name} fly?",
            f"With a calm day and a level throw, expect {dist_en}.{dist_rank_en} "
            "Wind, paper weight, and small crease errors all change the result.",
            f"{name} 能飞多远？",
            f"在无风天气、水平投掷的情况下，大约能飞 {dist_zh}。{dist_rank_zh}"
            "风力、纸张克重和折痕误差都会改变实际结果。",
        ),
        (
            f"How long does the {name} stay in the air?",
            f"A well-trimmed {name} should hold {time_en}.{time_rank_en} "
            "Launching from a higher spot and keeping the wings level will extend it.",
            f"{name} 能滞空多久？",
            f"调整得当的 {name} 可以保持{time_zh}。{time_rank_zh}"
            "从更高的位置轻投、保持两翼水平，都能延长滞空时间。",
        ),
        (
            f"What type of paper airplane is the {name}?",
            f"It is a {tags} {kind} rated {diff} difficulty. Fold it from {paper} "
            f"in {n} steps{' and keep a pair of scissors handy' if plane.get('scissors') else ' with no scissors required'}.",
            f"{name} 属于什么类型的纸飞机？",
            f"它是一款{''.join(TAG_CN.get(t, t) for t in plane.get('tags') or [])}机型，"
            f"难度为{plane.get('difficultyCn') or diff}，用{paper}折 {n} 步"
            f"{'，需要准备剪刀' if plane.get('scissors') else '，全程不用剪刀'}。",
        ),
        (
            f"How should I throw the {name}?",
            tip_en,
            f"{name} 应该怎么投掷？",
            tip_zh,
        ),
    ]


def faq_jsonld(plane: dict, ranks: dict) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q_en,
                "acceptedAnswer": {"@type": "Answer", "text": a_en},
            }
            for q_en, a_en, _, _ in faq_pairs(plane, ranks)
        ],
    }


def render_perf(plane: dict, ranks: dict) -> str:
    vals = perf_values(plane)
    tags_en = " + ".join(TAG_EN.get(t, t) for t in plane.get("tags") or [])
    tags_zh = " + ".join(TAG_CN.get(t, t) for t in plane.get("tags") or [])
    kind = plane_kind(plane)
    diff = plane.get("difficulty") or ""
    diff_zh = plane.get("difficultyCn") or diff
    paper = plane.get("paper") or "Letter or A4 paper"
    n = len(plane.get("steps") or [])
    rank_dist = ranks["rank"]["distanceScore"].get(plane["slug"])
    rank_time = ranks["rank"]["timeScore"].get(plane["slug"])
    total_dist = ranks["total"]["distanceScore"]
    total_time = ranks["total"]["timeScore"]

    if vals["distance"]:
        d_lo, d_hi = vals["distance"]
        dist_cell = (
            f'<span class="lang-en">{d_lo}–{d_hi} m'
            f'{" · rank #" + str(rank_dist) if rank_dist else ""}</span>'
            f'<span class="lang-zh">{d_lo}–{d_hi} 米'
            f'{" · 第 " + str(rank_dist) + " 名" if rank_dist else ""}</span>'
        )
    else:
        dist_cell = (
            '<span class="lang-en">Short glides</span>'
            '<span class="lang-zh">短距离滑翔</span>'
        )

    if vals["time"]:
        t_lo, t_hi = vals["time"]
        time_cell = (
            f'<span class="lang-en">{t_lo}–{t_hi} s'
            f'{" · rank #" + str(rank_time) if rank_time else ""}</span>'
            f'<span class="lang-zh">{t_lo}–{t_hi} 秒'
            f'{" · 第 " + str(rank_time) + " 名" if rank_time else ""}</span>'
        )
    else:
        time_cell = (
            '<span class="lang-en">Brief flight</span>'
            '<span class="lang-zh">极短滞空</span>'
        )

    return f"""
          <div class="perf-card">
            <h2 class="perf-title" data-i18n="perfTitle">Performance</h2>
            <dl class="perf-list">
              <div><dt data-i18n="perfType">Type</dt><dd>
                <span class="lang-en">{esc(tags_en)} {kind}</span>
                <span class="lang-zh">{esc(tags_zh)}{'滑翔机' if kind == 'glider' else '机型'}</span>
              </dd></div>
              <div><dt data-i18n="perfDistance">Estimated distance</dt><dd>{dist_cell}</dd></div>
              <div><dt data-i18n="perfTime">Estimated hang time</dt><dd>{time_cell}</dd></div>
              <div><dt data-i18n="perfDifficulty">Difficulty</dt><dd>
                <span class="lang-en">{esc(diff)}</span>
                <span class="lang-zh">{esc(diff_zh)}</span>
              </dd></div>
              <div><dt data-i18n="perfPaper">Paper &amp; folds</dt><dd>
                <span class="lang-en">{esc(paper)} · {n} folds</span>
                <span class="lang-zh">{esc(paper)} · {n} 步</span>
              </dd></div>
              <div><dt data-i18n="perfThrow">How to throw</dt><dd>
                <span class="lang-en">{esc(THROW_TIPS[primary_tag(plane)])}</span>
                <span class="lang-zh">{esc(THROW_TIPS_ZH[primary_tag(plane)])}</span>
              </dd></div>
            </dl>
            <p class="perf-note" data-i18n="perfNote">Estimates assume a calm day, a level launch, and a well-trimmed plane.</p>
          </div>"""


def render_faq(plane: dict, ranks: dict) -> str:
    items = []
    for q_en, a_en, q_zh, a_zh in faq_pairs(plane, ranks):
        items.append(
            f"""
          <details class="faq-item">
            <summary><span class="lang-en">{esc(q_en)}</span><span class="lang-zh">{esc(q_zh)}</span></summary>
            <p class="lang-en">{esc(a_en)}</p>
            <p class="lang-zh">{esc(a_zh)}</p>
          </details>"""
        )
    return "\n".join(items)


def render_plane_page(plane: dict, ranks: dict) -> str:
    title = page_title(plane)
    desc = meta_desc(plane)
    kw = keywords(plane)
    slug = plane["slug"]
    path = f"planes/{slug}.html"
    og_image = abs_url(plane.get("square") or plane.get("thumb") or "")
    tags = "".join(
        f'<span class="chip" data-tag="{esc(t)}">{esc(TAG_EN.get(t, t))}</span>'
        for t in plane.get("tags") or []
    )
    cut_flag = "1" if plane.get("scissors") else "0"
    cut = (
        f'<span class="chip{" cut" if plane.get("scissors") else ""}" data-cut="{cut_flag}">'
        f'{"Scissors" if plane.get("scissors") else "No scissors"}</span>'
    )
    diff_en = plane.get("difficulty") or ""
    ld = howto_jsonld(plane)
    ld_faq = faq_jsonld(plane, ranks)
    n_steps = len(plane.get("steps") or [])
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
<html lang="en" data-lang="en">
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
  <meta property="og:locale" content="en_US" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{esc(abs_url(path))}" />
  <meta property="og:image" content="{esc(og_image)}" />
  <meta property="og:image:alt" content="{esc(plane['name'])} paper airplane" />

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
  <script type="application/ld+json">{json.dumps(ld_faq, ensure_ascii=False)}</script>
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
        <strong data-i18n="brandTitle">Paper Airplane</strong>
        <small data-i18n="brandSub">Folding Hangar</small>
      </span>
    </a>
    <nav class="topnav" aria-label="Main navigation">
      <a class="topnav-link" href="../index.html" data-i18n="navHangar">Hangar</a>
      <a class="topnav-link" href="../learn.html" data-i18n="navLearn">Learn</a>
      <a class="topnav-link" href="../3d-learn.html" data-i18n="nav3dLearn">3D Learn</a>
      <a class="topnav-link" href="../read.html" data-i18n="navRead">Read &amp; Learn</a>
      <a class="topnav-link" href="../guides.html" data-i18n="navGuides">Guides</a>
      <a class="topnav-link" href="../video.html" data-i18n="navVideo">Video Guide</a>
      <a class="topnav-link" href="../fly.html" data-i18n="navFly">Fly</a>
      <details class="topnav-dd">
        <summary class="topnav-link topnav-more">More crafts</summary>
        <div class="topnav-sub" role="group" aria-label="More crafts">
          <a class="topnav-sub-link" href="../paper-mache/">Paper Mache</a>
        </div>
      </details>
    </nav>
    <div class="topbar-meta">
      <span>{esc(plane['name'])}</span>
    </div>
  </header>

  <main>
    <section class="view detail">
      <a class="btn back" href="../index.html" data-i18n="back">← Back to hangar</a>
      <div class="detail-layout">
        <aside class="detail-aside">
          <img class="square" src="{esc('../' + (plane.get('square') or plane.get('thumb') or ''))}" alt="{esc(plane['name'])}" width="250" height="250" />
          <h1>{esc(plane['name'])}</h1>
          <p class="blurb">{esc(plane.get('description') or plane.get('blurb') or '')}</p>
          <div class="detail-stats">
            <span class="chip diff-{esc(diff_en)}" data-diff="{esc(diff_en)}">{esc(diff_en)}</span>
            <span class="chip">{esc(plane.get('paper') or 'Letter & A4')}</span>
            <span class="chip" data-steps="{n_steps}">{n_steps} steps</span>
            {tags}{cut}
          </div>{render_perf(plane, ranks)}
        </aside>
        <div class="steps">
          <h2 class="steps-title" data-i18n="stepsTitle">Folding steps</h2>
          {render_steps(plane)}
        </div>
      </div>
      <section class="detail-faq" aria-labelledby="faq-title">
        <h2 id="faq-title" class="steps-title" data-i18n="faqTitle">Frequently asked questions</h2>
        <div class="faq-list">{render_faq(plane, ranks)}
        </div>
      </section>
    </section>
  </main>

  <footer class="site-foot">
    <p data-i18n="footer">Paper Planes World · Static folding guides</p>
  </footer>
  <script src="../i18n.js"></script>
  <script src="../plane.js"></script>
</body>
</html>
"""


def render_hangar_cards(planes: list[dict]) -> str:
    cards = []
    for i, plane in enumerate(planes):
        tags = "".join(
            f'<span class="chip">{esc(TAG_EN.get(tag, tag))}</span>'
            for tag in plane.get("tags") or []
        )
        badge = (
            f'<span class="badge">{esc(plane["badge"])}</span>'
            if plane.get("badge")
            else ""
        )
        cut = (
            '<span class="chip cut">Scissors</span>' if plane.get("scissors") else ""
        )
        thumb = plane["thumb"]
        fallback = thumb.replace(".webp", ".jpg")
        delay = min(i, 12) * 0.03
        cards.append(
            f"""
          <a class="plane-card" href="planes/{esc(plane['slug'])}.html" style="animation-delay:{delay}s">
            {badge}
            <img class="thumb" src="{esc(thumb)}" alt="{esc(plane['name'])} paper airplane" loading="lazy" width="300" height="250" onerror="this.onerror=null;this.src='{esc(fallback)}'" />
            <div class="body">
              <h3>{esc(plane['name'])}</h3>
              <div class="meta-row">
                <span class="chip diff-{esc(plane['difficulty'])}">{esc(plane['difficulty'])}</span>
                {tags}{cut}
              </div>
            </div>
          </a>"""
        )
    return "\n".join(
        line.rstrip() for line in "\n".join(cards).splitlines()
    )


def hangar_jsonld(planes: list[dict]) -> dict:
    count = len(planes)
    return {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"{SITE_NAME} · {count} Paper Airplane Folding Guides",
        "description": f"{count} classic paper airplane designs with illustrated folding steps. Filter by distance, time aloft, acrobatic, and difficulty.",
        "url": abs_url(""),
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": abs_url("")},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": count,
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
    urls = [
        "",
        "learn.html",
        "3d-learn.html",
        "read.html",
        "guides.html",
        "fix-flight.html",
        "how-to-throw.html",
        "dart-or-glider.html",
        "choose-paper.html",
        "how-planes-fly.html",
        "video.html",
        "fly.html",
        "paper-mache/",
        "paper-mache-recipe/",
        "paper-mache-volcano/",
    ] + [f"planes/{p['slug']}.html" for p in planes]
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
        body.append(
            f"    <priority>{'1.0' if not u else '0.9' if u in ('fly.html', 'learn.html', '3d-learn.html', 'read.html', 'guides.html', 'fix-flight.html', 'how-to-throw.html', 'dart-or-glider.html', 'choose-paper.html', 'how-planes-fly.html', 'video.html') else '0.8'}</priority>"
        )
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
        f"User-agent: *\nAllow: /\nSitemap: {abs_url('sitemap.xml')}\n",
        encoding="utf-8",
    )


HOME_FAQ = [
    (
        "What paper should I use for paper airplanes?",
        "Standard A4 or US Letter printer paper around 70–80 gsm works for almost every design on this site. Lighter paper folds easily and glides well indoors, while slightly heavier paper holds sharper creases in outdoor air. Avoid thick card stock: it makes dense planes that stall almost immediately.",
        "折纸飞机应该用什么纸？",
        "普通的 A4 或 Letter 打印纸（约 70–80g/m²）几乎可以完成站内所有机型。较轻的纸更容易折叠，室内滑翔效果好；稍重一点的纸折痕更挺，适合在户外有风时使用。尽量不要用厚卡纸，那会让机身过重、很快就失速。",
    ),
    (
        "Are there 3D folding tutorials on this site?",
        "Yes. Every plane is cut into short illustrated folds, and the guides are built for 3D inspection — check each step from the side, top, and front so you can see exactly how the wings and nose line up before continuing. That makes unusual designs such as the Stealth Glider much easier to copy than a flat diagram.",
        "站内有 3D 折法教程吗？",
        "有。每款纸飞机都拆成了简短的图解步骤，教程按 3D 视角组织：可以从侧面、顶部和正面检查每一步，先看清机翼和机头的位置关系再继续折。像 Stealth Glider 这类造型特别的机型，跟着 3D 视角比看平面图容易得多。",
    ),
    (
        "Can I test-fly a plane before folding it?",
        "Each guide lists an estimated flight distance and hang time, and the test-flight preview shows how the finished design should glide once it leaves your hand. Fold your own version, then compare it with the preview: if it dives, veers, or stalls, adjust the wings and try again.",
        "可以先试飞再动手折吗？",
        "每个详情页都给出估算的飞行距离和滞空时间，试飞预览会展示这架飞机脱手后应有的滑翔状态。折好后对照预览检查：如果出现下坠、跑偏或失速，调整机翼再试一次即可。",
    ),
    (
        "How far can a paper airplane fly?",
        "In normal indoor conditions the designs in this collection travel roughly 10–26 metres (33–85 feet) with a level throw. Distance designs such as the Lift Off and Basic Dart sit at the top of that range. Wind, paper weight, and small fold errors can easily change the result by several metres.",
        "纸飞机能飞多远？",
        "在正常的室内环境下，站内机型以水平投掷大约能飞 10–26 米。Lift Off、Basic Dart 这类远距机型处于这个区间的上限。风力、纸张克重和细微的折叠误差，都可能让结果相差好几米。",
    ),
    (
        "How long can a paper airplane stay in the air?",
        "Hang time ranges from a couple of seconds for heavy darts to roughly 10–13 seconds for well-trimmed gliders such as the Stealth Glider. Long flights come from light paper, a gentle upward launch, and a high release point — more than from throwing harder.",
        "纸飞机能滞空多久？",
        "偏重的机型可能只有两三秒，而 Stealth Glider 这类调整得当的滑翔机可以达到 10–13 秒左右。想要长时间滞空，关键在轻薄纸张、略向上扬的轻投和更高的出手位置，而不是用力猛抛。",
    ),
    (
        "Why does my paper airplane fly in circles?",
        "A plane turns because one wing is doing more work than the other. Check that both wings are the same size and angle, that the body is folded exactly in half, and that the vertical tail is straight. A tiny upward bend on the outside wing usually corrects a gentle turn.",
        "纸飞机为什么会绕圈飞？",
        "绕圈通常是因为两侧机翼受力不一致。先检查两翼大小和角度是否相同、机身是否严格对折、垂直尾翼有没有歪。把外侧机翼的后缘轻轻向上折一点，一般就能修正轻微的偏转。",
    ),
    (
        "Why does my paper airplane nose-dive?",
        "A nose-dive usually means the centre of gravity is too far forward or the trailing edges sit too low. Start with a gentler, level throw, then bend both trailing edges up by 2–3 mm to add lift. If it still dives, a small paper clip near the tail shifts the balance backwards.",
        "纸飞机为什么总是栽头？",
        "栽头通常说明重心太靠前，或者机翼后缘位置偏低。先改用更轻、更平直的投掷，再把两侧后缘一起向上折 2–3 毫米来增加升力。如果仍然下坠，可以在机尾夹一个小回形针，把重心往后移。",
    ),
    (
        "Do I need scissors for these paper airplanes?",
        "Only some designs need scissors, usually to cut a small slit or shape the tail. Every card carries a Scissors label, and the filter rail lets you hide those models with the No scissors option, so you can start folding with just a sheet of paper.",
        "这些纸飞机需要剪刀吗？",
        "只有部分机型需要剪刀，通常用来开一个小口或修整机尾。每张卡片上都有剪刀标识，左侧筛选栏也可以勾选“不用剪刀”，只保留徒手就能折的机型。",
    ),
    (
        "A4 or Letter paper — does the size matter?",
        "Both work. A4 is slightly narrower and taller than US Letter, which changes the wing proportions by a few millimetres. Fold along the paper's own edges and the plane will fly correctly either way; compare the estimated numbers instead of forcing a size.",
        "A4 和 Letter 纸有区别吗？",
        "两种都可以。A4 比 Letter 略窄略长，机翼比例会相差几毫米。只要始终对齐纸张自身的边线来折，两种尺寸都能正常飞行；与其强行换纸，不如直接参考页面上的估算数据。",
    ),
    (
        "Are these paper airplanes suitable for kids?",
        "Yes. Start with Easy designs such as the Basic Dart, which use straight folds and need no scissors. Medium and Hard models add squash folds and sharp creases that younger folders may need help with, and Expert designs are best treated as a shared project.",
        "这些纸飞机适合小朋友折吗？",
        "适合。建议从 Basic Dart 这类“简单”难度开始，都是直线折法，也不需要剪刀。中等和困难机型会用到压折、对齐尖角等技巧，年纪较小的孩子可能需要协助；专家难度更适合当作亲子合作项目。",
    ),
    (
        "How can I make my paper airplane fly farther?",
        "Launch level and firmly instead of throwing upward, keep both wings symmetrical, and avoid heavy paper. A clean, sharp crease along the centre line matters more than brute force, and you should test small adjustments one at a time so you know which change helped.",
        "怎么让纸飞机飞得更远？",
        "投掷时保持水平、用力平稳，不要向上抛；同时保证两翼对称，并避免使用过厚的纸。中缝折痕干净笔直，比单纯用力更重要。每次只调整一处，再对比上一次的飞行结果。",
    ),
    (
        "How do I use the flight estimates in each guide?",
        "The distance and hang-time figures are ranges, not guarantees. They assume a calm day, a level launch, and a properly trimmed plane, so treat them as a benchmark: if your plane lands well short, check symmetry, crease sharpness, and paper weight before changing the design.",
        "详情页里的飞行估算怎么用？",
        "这些距离和滞空数据是区间参考，不是保证值，前提是无风天气、水平出手和调整到位的飞机。可以把它们当作基准：如果你的飞机明显飞不到，先检查左右对称、折痕是否压实、纸张是否过厚，再考虑改动设计。",
    ),
]


def render_home_faq() -> str:
    items = []
    for q_en, a_en, q_zh, a_zh in HOME_FAQ:
        items.append(
            f"""
          <details class="faq-item">
            <summary><span class="lang-en">{esc(q_en)}</span><span class="lang-zh">{esc(q_zh)}</span></summary>
            <p class="lang-en">{esc(a_en)}</p>
            <p class="lang-zh">{esc(a_zh)}</p>
          </details>"""
        )
    return "\n".join(items)


def home_faq_jsonld() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q_en,
                "acceptedAnswer": {"@type": "Answer", "text": a_en},
            }
            for q_en, a_en, _, _ in HOME_FAQ
        ],
    }


def patch_index(planes: list[dict]) -> None:
    index = SITE / "index.html"
    text = index.read_text(encoding="utf-8")
    count = len(planes)
    title = f"{SITE_NAME} · {count} Paper Airplane Designs with 3D Folding Guides"
    desc = (
        f"Fold {count} classic paper airplanes with 3D step-by-step guides, estimated flight "
        "distance and hang time, and a test-flight preview. Filter by distance, difficulty, and scissors."
    )
    keywords = (
        "paper airplane,paper plane,3d paper airplane tutorial,paper airplane folding guide,"
        "paper airplane test flight,paper airplane simulator,how far can a paper airplane fly,"
        "paper airplane template,dart,glider,origami airplane"
    )
    og = abs_url("assets/planes/1/square.webp")
    ld = hangar_jsonld(planes)
    ld_faq = home_faq_jsonld()
    head = f"""<!DOCTYPE html>
<html lang="en" data-lang="en">
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
  <meta property="og:locale" content="en_US" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(desc)}" />
  <meta property="og:url" content="{esc(abs_url(''))}" />
  <meta property="og:image" content="{esc(og)}" />
  <meta property="og:image:alt" content="{esc(SITE_NAME)}" />

  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{esc(title)}" />
  <meta name="twitter:description" content="{esc(desc)}" />
  <meta name="twitter:image" content="{esc(og)}" />

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Noto+Sans+SC:wght@400;500;700&family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="styles.css" />
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(ld_faq, ensure_ascii=False)}</script>
</head>"""
    # Replace from start through </head>
    end = text.find("</head>")
    if end == -1:
        raise SystemExit("index.html missing </head>")
    rest = text[end + len("</head>") :]
    # Ensure brand links to index without hash-only
    rest = rest.replace('href="#/"', 'href="index.html"', 1)
    start_marker = "<!-- PLANE_GRID_START -->"
    end_marker = "<!-- PLANE_GRID_END -->"
    start = rest.find(start_marker)
    end = rest.find(end_marker)
    if start == -1 or end == -1 or end < start:
        raise SystemExit("index.html missing plane grid markers")
    end += len(end_marker)
    grid = f"{start_marker}\n{render_hangar_cards(planes)}\n          {end_marker}"
    rest = rest[:start] + grid + rest[end:]

    faq_start = "<!-- HOME_FAQ_START -->"
    faq_end = "<!-- HOME_FAQ_END -->"
    start = rest.find(faq_start)
    end = rest.find(faq_end)
    if start == -1 or end == -1 or end < start:
        raise SystemExit("index.html missing home FAQ markers")
    end += len(faq_end)
    faq = f"{faq_start}{render_home_faq()}\n        {faq_end}"
    rest = rest[:start] + faq + rest[end:]
    index.write_text(head + rest, encoding="utf-8")


def main() -> None:
    planes = json.loads(DATA.read_text(encoding="utf-8"))
    ranks = build_ranks(planes)
    PLANES_DIR.mkdir(parents=True, exist_ok=True)
    for old in PLANES_DIR.glob("*.html"):
        old.unlink()
    for p in planes:
        out = PLANES_DIR / f"{p['slug']}.html"
        out.write_text(render_plane_page(p, ranks), encoding="utf-8")
    write_sitemap(planes)
    write_robots()
    patch_index(planes)
    print(f"generated {len(planes)} plane pages + sitemap/robots")


if __name__ == "__main__":
    main()
