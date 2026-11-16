#!/usr/bin/env python3
"""Generate SEO plane pages, sitemap, and update hangar meta helpers."""
from __future__ import annotations

import hashlib
import html
import json
import subprocess
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PLANES_DIR = SITE / "planes"
DATA = SITE / "data" / "planes.json"
LASTMOD_STORE = SITE / "data" / "sitemap_lastmod.json"

TAG_CN = {
    "distance": "飞得远",
    "time_aloft": "停得久",
    "acrobatic": "玩特技",
    "decorative": "好看摆设",
}

TAG_EN = {
    "distance": "Far throws",
    "time_aloft": "Long floats",
    "acrobatic": "Tricks",
    "decorative": "Display",
}

DIFF_EN = {
    "Easy": "Beginner",
    "Medium": "Intermediate",
    "Hard": "Advanced",
    "Expert": "Master",
}

DIFF_CN = {
    "Easy": "入门",
    "Medium": "进阶",
    "Hard": "挑战",
    "Expert": "大师",
}

GOAL_BLURB_EN = {
    "distance": "far, straight throws",
    "time_aloft": "long floating glides",
    "acrobatic": "tricks and loops",
    "decorative": "looking great on a shelf",
    "glider": "balanced range and hang time",
}

GOAL_BLURB_CN = {
    "distance": "远距直线飞行",
    "time_aloft": "长时间滑翔滞空",
    "acrobatic": "特技与翻转",
    "decorative": "好看的摆设展示",
    "glider": "兼顾航程与滞空",
}

SITE_NAME = "Paper Planes World"
OG_IMAGE = "assets/og-cover.jpg"
BRAND_TITLE = "Paper Planes World"
BRAND_SUB = ""
# Relative site root for local static hosting; change when deploying to a domain.
BASE_URL = "https://paperairplaneworld.wiki"


def esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def i18n_text(en: str, zh: str, tag: str = "p", cls: str = "") -> str:
    """English in the DOM; Chinese only in data-zh for the language switcher.

    Keeps the crawlable document language unambiguously English.
    """
    class_attr = f' class="{cls} i18n-text"' if cls else ' class="i18n-text"'
    if zh and zh.strip() and zh.strip() != en.strip():
        return f"<{tag}{class_attr} data-zh=\"{esc(zh)}\">{esc(en)}</{tag}>"
    if cls:
        return f'<{tag} class="{cls}">{esc(en)}</{tag}>'
    return f"<{tag}>{esc(en)}</{tag}>"


def pretty_path(path: str) -> str:
    """Strip .html so URLs match Cloudflare's extensionless canonical form."""
    path = (path or "").lstrip("/")
    if path.endswith("/index.html"):
        path = path[: -len("index.html")]
    elif path == "index.html":
        path = ""
    elif path.endswith(".html"):
        path = path[: -len(".html")]
    return path


def abs_url(path: str) -> str:
    path = pretty_path(path)
    if BASE_URL:
        return f"{BASE_URL.rstrip('/')}/{path}" if path else f"{BASE_URL.rstrip('/')}/"
    return f"/{path}" if path else "/"


def site_href(path: str) -> str:
    """Root-absolute href used in templates (no .html)."""
    path = pretty_path(path)
    return f"/{path}" if path else "/"


def primary_goal(plane: dict) -> str:
    """Single clearest flying goal for chips and copy."""
    tags = plane.get("tags") or []
    if "distance" in tags and "time_aloft" in tags:
        return "time_aloft"
    for key in ("distance", "time_aloft", "acrobatic", "decorative"):
        if key in tags:
            return key
    return "distance"


def skill_label(plane: dict, lang: str = "en") -> str:
    raw = plane.get("difficulty") or ""
    return (DIFF_CN if lang == "zh" else DIFF_EN).get(raw, raw)


def meta_desc(plane: dict) -> str:
    goal = primary_goal(plane)
    skill = skill_label(plane, "en")
    n = len(plane.get("steps") or [])
    prep = "needs a cut" if plane.get("scissors") else "hands-only fold"
    return (
        f"Fold the {plane['name']} paper airplane — best for {GOAL_BLURB_EN[goal]}, "
        f"{skill.lower()} skill, {n}-step {prep}."
    )


def page_title(plane: dict) -> str:
    return f"{plane['name']} Paper Airplane · Step-by-Step Folding Guide"


def flight_lead(plane: dict, ranks: dict) -> tuple[str, str]:
    """Main-body flight summary — ranks and ranges, not buried in a side card."""
    vals = perf_values(plane)
    name = plane["name"]
    rank_dist = ranks["rank"]["distanceScore"].get(plane["slug"])
    rank_time = ranks["rank"]["timeScore"].get(plane["slug"])
    total_dist = ranks["total"]["distanceScore"]
    total_time = ranks["total"]["timeScore"]
    bits_en, bits_zh = [], []
    if vals["distance"]:
        lo, hi = vals["distance"]
        en = f"about {lo}–{hi} m ({round(lo * 3.28)}–{round(hi * 3.28)} ft)"
        zh = f"大约 {lo}–{hi} 米"
        if rank_dist:
            en += f", ranking #{rank_dist} of {total_dist} for distance"
            zh += f"，远距在站内 {total_dist} 款中排第 {rank_dist}"
        bits_en.append(en)
        bits_zh.append(zh)
    if vals["time"]:
        lo, hi = vals["time"]
        en = f"roughly {lo}–{hi} s of hang time"
        zh = f"滞空大约 {lo}–{hi} 秒"
        if rank_time:
            en += f" (#{rank_time} of {total_time})"
            zh += f"（第 {rank_time}/{total_time}）"
        bits_en.append(en)
        bits_zh.append(zh)
    if not bits_en:
        return (
            f"The {name} is built more for shape and handling than for raw range or hang time.",
            f"{name} 更偏造型与手感，不以远距或滞空见长。",
        )
    return (
        f"In calm air with a level throw, expect {'; '.join(bits_en)}. "
        "Treat the numbers as a trim target: if your fold lands short, check symmetry and crease sharpness first.",
        f"无风、水平投掷时，{bits_zh[0]}"
        + (f"；{bits_zh[1]}" if len(bits_zh) > 1 else "")
        + "。把这些数字当微调目标：飞不到就先查左右对称和折痕是否压实。",
    )


def render_steps(plane: dict) -> str:
    blocks = []
    for s in plane.get("steps") or []:
        cn = s.get("textCn") or ""
        en = s.get("text") or ""
        body = i18n_text(en, cn, tag="p")
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
    """Throw-tip key (keeps glider when both distance + time)."""
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
    skill_en = skill_label(plane, "en")
    skill_zh = skill_label(plane, "zh")
    goal = primary_goal(plane)
    tip_key = primary_tag(plane)
    paper = plane.get("paper") or "Letter or A4 paper"
    n = len(plane.get("steps") or [])
    rank_dist = ranks["rank"]["distanceScore"].get(plane["slug"])
    rank_time = ranks["rank"]["timeScore"].get(plane["slug"])
    total_dist = ranks["total"]["distanceScore"]
    total_time = ranks["total"]["timeScore"]
    tip_en = THROW_TIPS[tip_key]
    tip_zh = THROW_TIPS_ZH[tip_key]
    prep_en = "needs a cut" if plane.get("scissors") else "hands only"
    prep_zh = "需要剪一刀" if plane.get("scissors") else "只用手折"

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
            f"What is the {name} best for?",
            f"It is best for {GOAL_BLURB_EN[goal]}. Folding skill is {skill_en.lower()}. "
            f"Use {paper}, {n} steps, {prep_en}.",
            f"{name} 最适合做什么？",
            f"它最适合{GOAL_BLURB_CN[goal]}。折纸难度为{skill_zh}，"
            f"用{paper}折 {n} 步，{prep_zh}。",
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
    goal = primary_goal(plane)
    skill_en = skill_label(plane, "en")
    skill_zh = skill_label(plane, "zh")
    paper = plane.get("paper") or "Letter or A4 paper"
    n = len(plane.get("steps") or [])
    rank_dist = ranks["rank"]["distanceScore"].get(plane["slug"])
    rank_time = ranks["rank"]["timeScore"].get(plane["slug"])
    prep_en = "Needs a cut" if plane.get("scissors") else "Hands only"
    prep_zh = "需要剪一刀" if plane.get("scissors") else "只用手折"

    if vals["distance"]:
        d_lo, d_hi = vals["distance"]
        dist_en = f"{d_lo}–{d_hi} m" + (f" · rank #{rank_dist}" if rank_dist else "")
        dist_zh = f"{d_lo}–{d_hi} 米" + (f" · 第 {rank_dist} 名" if rank_dist else "")
        dist_cell = i18n_text(dist_en, dist_zh, tag="span")
    else:
        dist_cell = i18n_text("Short glides", "短距离滑翔", tag="span")

    if vals["time"]:
        t_lo, t_hi = vals["time"]
        time_en = f"{t_lo}–{t_hi} s" + (f" · rank #{rank_time}" if rank_time else "")
        time_zh = f"{t_lo}–{t_hi} 秒" + (f" · 第 {rank_time} 名" if rank_time else "")
        time_cell = i18n_text(time_en, time_zh, tag="span")
    else:
        time_cell = i18n_text("Brief flight", "极短滞空", tag="span")

    goal_cell = i18n_text(
        f"{TAG_EN[goal]} — {GOAL_BLURB_EN[goal]}",
        f"{TAG_CN[goal]} — {GOAL_BLURB_CN[goal]}",
        tag="span",
    )
    skill_cell = i18n_text(skill_en, skill_zh, tag="span")
    paper_cell = i18n_text(
        f"{paper} · {n} folds · {prep_en}",
        f"{paper} · {n} 步 · {prep_zh}",
        tag="span",
    )
    tip_key = primary_tag(plane)
    throw_cell = i18n_text(THROW_TIPS[tip_key], THROW_TIPS_ZH[tip_key], tag="span")

    return f"""
          <div class="perf-card">
            <h2 class="perf-title" data-i18n="perfTitle">Flight notes</h2>
            <dl class="perf-list">
              <div><dt data-i18n="perfType">Best for</dt><dd>
                {goal_cell}
              </dd></div>
              <div><dt data-i18n="perfDistance">Estimated distance</dt><dd>{dist_cell}</dd></div>
              <div><dt data-i18n="perfTime">Estimated hang time</dt><dd>{time_cell}</dd></div>
              <div><dt data-i18n="perfDifficulty">Folding skill</dt><dd>
                {skill_cell}
              </dd></div>
              <div><dt data-i18n="perfPaper">Paper &amp; folds</dt><dd>
                {paper_cell}
              </dd></div>
              <div><dt data-i18n="perfThrow">How to throw</dt><dd>
                {throw_cell}
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
            {i18n_text(q_en, q_zh, tag="summary")}
            {i18n_text(a_en, a_zh, tag="p")}
          </details>"""
        )
    return "\n".join(items)


def render_plane_page(plane: dict, ranks: dict) -> str:
    title = page_title(plane)
    desc = meta_desc(plane)
    slug = plane["slug"]
    path = f"planes/{slug}"
    og_image = abs_url(plane.get("square") or plane.get("thumb") or "")
    goal = primary_goal(plane)
    goal_chip = (
        f'<span class="chip goal goal-{esc(goal)}" data-tag="{esc(goal)}">'
        f'{esc(TAG_EN[goal])}</span>'
    )
    cut_flag = "1" if plane.get("scissors") else "0"
    cut = (
        f'<span class="chip{" cut" if plane.get("scissors") else ""}" data-cut="{cut_flag}">'
        f'{"Needs a cut" if plane.get("scissors") else "Hands only"}</span>'
    )
    diff_en = plane.get("difficulty") or ""
    skill_en = skill_label(plane, "en")
    ld = howto_jsonld(plane)
    ld_faq = faq_jsonld(plane, ranks)
    n_steps = len(plane.get("steps") or [])
    tags = goal_chip
    h1 = f"{plane['name']} Paper Airplane"
    blurb_en = plane.get("description") or plane.get("blurb") or ""
    blurb_zh = plane.get("descriptionCn") or plane.get("blurbCn") or ""
    lead_en, lead_zh = flight_lead(plane, ranks)
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
    <a class="brand" href="{site_href('')}">
      <span class="brand-mark" aria-hidden="true">✈</span>
      <span class="brand-text">
        <strong data-i18n="brandTitle">{esc(BRAND_TITLE)}</strong>
        <small data-i18n="brandSub">{esc(BRAND_SUB)}</small>
      </span>
    </a>
    <nav class="topnav" aria-label="Main navigation">
      <a class="topnav-link" href="{site_href('')}" data-i18n="navHangar">Hangar</a>
      <a class="topnav-link" href="{site_href('learn')}" data-i18n="navLearn">Learn</a>
      <a class="topnav-link" href="{site_href('3d-learn')}" data-i18n="nav3dLearn">3D Learn</a>
      <a class="topnav-link" href="{site_href('read')}" data-i18n="navRead">Read &amp; Learn</a>
      <a class="topnav-link" href="{site_href('guides')}" data-i18n="navGuides">Guides</a>
      <a class="topnav-link" href="{site_href('video')}" data-i18n="navVideo">Video Guide</a>
      <a class="topnav-link" href="{site_href('fly')}" data-i18n="navFly">Fly</a>
      <details class="topnav-dd">
        <summary class="topnav-link topnav-more">More crafts</summary>
        <div class="topnav-sub" role="group" aria-label="More crafts">
          <a class="topnav-sub-link" href="{site_href('paper-mache/')}">Paper Mache</a>
        </div>
      </details>
    </nav>
    <div class="topbar-meta">
      <span>{esc(plane['name'])}</span>
    </div>
  </header>

  <main>
    <section class="view detail">
      <a class="btn back" href="{site_href('')}" data-i18n="back">← Back to hangar</a>
      <div class="detail-layout">
        <aside class="detail-aside">
          <img class="square" src="{esc('../' + (plane.get('square') or plane.get('thumb') or ''))}" alt="{esc(h1)}" width="250" height="250" />
          <h1>{esc(h1)}</h1>
          {i18n_text(blurb_en, blurb_zh, tag="p", cls="blurb")}
          {i18n_text(lead_en, lead_zh, tag="p", cls="flight-lead")}
          <div class="detail-stats">
            {tags}
            <span class="chip diff-{esc(diff_en)}" data-diff="{esc(diff_en)}">{esc(skill_en)}</span>
            <span class="chip" data-steps="{n_steps}">{n_steps} steps</span>
            {cut}
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
        goal = primary_goal(plane)
        goal_chip = (
            f'<span class="chip goal goal-{esc(goal)}">{esc(TAG_EN[goal])}</span>'
        )
        badge = (
            f'<span class="badge">{esc(plane["badge"])}</span>'
            if plane.get("badge")
            else ""
        )
        cut = (
            '<span class="chip cut">Needs cut</span>' if plane.get("scissors") else ""
        )
        skill = skill_label(plane, "en")
        thumb = plane["thumb"]
        fallback = thumb.replace(".webp", ".jpg")
        delay = min(i, 12) * 0.03
        cards.append(
            f"""
          <a class="plane-card" href="{site_href('planes/' + plane['slug'])}" style="animation-delay:{delay}s">
            {badge}
            <img class="thumb" src="{esc(thumb)}" alt="{esc(plane['name'])} paper airplane" loading="lazy" width="300" height="250" onerror="this.onerror=null;this.src='{esc(fallback)}'" />
            <div class="body">
              <h3>{esc(plane['name'])}</h3>
              <div class="meta-row">
                {goal_chip}
                <span class="chip diff-{esc(plane['difficulty'])}">{esc(skill)}</span>
                {cut}
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
        "name": f"Paper Airplane Designs — {count} Folding Guides",
        "description": (
            f"Browse {count} paper airplane designs with illustrated folding steps, "
            "flight estimates, and filters for far throws, long floats, tricks, and display."
        ),
        "url": abs_url(""),
        "isPartOf": {"@type": "WebSite", "name": SITE_NAME, "url": abs_url("")},
        "mainEntity": {
            "@type": "ItemList",
            "name": "Paper airplane designs",
            "numberOfItems": count,
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "url": abs_url(f"planes/{p['slug']}"),
                    "name": p["name"],
                }
                for i, p in enumerate(planes)
            ],
        },
    }


def sitemap_page_file(path: str) -> Path | None:
    """Resolve a sitemap path to its on-disk HTML source."""
    rel = pretty_path(path).rstrip("/")
    candidates = []
    if not rel:
        candidates.append(SITE / "index.html")
    else:
        candidates.extend(
            [
                SITE / f"{rel}.html",
                SITE / rel / "index.html",
                SITE / f"{rel}/index.html",
            ]
        )
    for cand in candidates:
        if cand.is_file():
            return cand
    return None


def plane_content_fingerprint(plane: dict) -> str:
    """Hash only fields that appear on the public plane page."""
    payload = {
        "slug": plane.get("slug"),
        "name": plane.get("name"),
        "nameCn": plane.get("nameCn"),
        "description": plane.get("description"),
        "descriptionCn": plane.get("descriptionCn"),
        "difficulty": plane.get("difficulty"),
        "scissors": plane.get("scissors"),
        "tags": plane.get("tags"),
        "distance": plane.get("distance"),
        "time": plane.get("time"),
        "steps": plane.get("steps"),
        "images": plane.get("images"),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def page_content_fingerprint(path: str, planes_by_slug: dict[str, dict]) -> str:
    """Stable content hash for a sitemap URL (not filesystem mtime)."""
    key = pretty_path(path).rstrip("/")
    if key.startswith("planes/"):
        slug = key.split("/", 1)[1]
        plane = planes_by_slug.get(slug)
        if plane:
            return f"plane:{plane_content_fingerprint(plane)}"
    page = sitemap_page_file(path)
    if page is not None:
        digest = hashlib.sha256(page.read_bytes()).hexdigest()[:20]
        return f"file:{digest}"
    return f"missing:{key}"


def git_source_date(path: str) -> str | None:
    """Best-effort last substantive git date for bootstrap only."""
    key = pretty_path(path).rstrip("/")
    if key.startswith("planes/"):
        sources = [DATA]
    else:
        page = sitemap_page_file(path)
        sources = [page] if page is not None else []
    for src in sources:
        if src is None or not src.is_file():
            continue
        try:
            out = subprocess.check_output(
                ["git", "log", "-1", "--format=%cs", "--", str(src)],
                cwd=ROOT,
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        if out:
            return out
    return None


def load_lastmod_store() -> dict:
    if not LASTMOD_STORE.is_file():
        return {}
    try:
        data = json.loads(LASTMOD_STORE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def save_lastmod_store(store: dict) -> None:
    LASTMOD_STORE.parent.mkdir(parents=True, exist_ok=True)
    LASTMOD_STORE.write_text(
        json.dumps(store, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def sitemap_lastmod(
    path: str,
    planes_by_slug: dict[str, dict],
    store: dict,
) -> str:
    """Per-page lastmod from content fingerprint, not build-day mtime.

    Unchanged content keeps the previous date. New/changed content gets today
    (or a git source date on first bootstrap so a mass rebuild does not invent
    fake staggered dates).
    """
    key = pretty_path(path).rstrip("/")
    fingerprint = page_content_fingerprint(path, planes_by_slug)
    prev = store.get(key) if isinstance(store.get(key), dict) else None
    if prev and prev.get("hash") == fingerprint and prev.get("lastmod"):
        return str(prev["lastmod"])

    lastmod = date.today().isoformat()
    if not prev:
        seeded = git_source_date(path)
        if seeded:
            lastmod = seeded
    store[key] = {"hash": fingerprint, "lastmod": lastmod}
    return lastmod


def write_sitemap(planes: list[dict]) -> None:
    high = {
        "fly",
        "learn",
        "3d-learn",
        "read",
        "guides",
        "fix-flight",
        "how-to-throw",
        "dart-or-glider",
        "choose-paper",
        "how-planes-fly",
        "video",
    }
    urls = [
        "",
        "learn",
        "3d-learn",
        "read",
        "guides",
        "fix-flight",
        "how-to-throw",
        "dart-or-glider",
        "choose-paper",
        "how-planes-fly",
        "video",
        "fly",
        "paper-mache/",
        "paper-mache-recipe/",
        "paper-mache-volcano/",
    ] + [f"planes/{p['slug']}" for p in planes]
    planes_by_slug = {p["slug"]: p for p in planes}
    store = load_lastmod_store()
    body = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for u in urls:
        loc = abs_url(u)
        key = pretty_path(u).rstrip("/")
        priority = "1.0" if not key else "0.9" if key in high else "0.8"
        body.append("  <url>")
        body.append(f"    <loc>{esc(loc)}</loc>")
        body.append(f"    <lastmod>{sitemap_lastmod(u, planes_by_slug, store)}</lastmod>")
        body.append("    <changefreq>monthly</changefreq>")
        body.append(f"    <priority>{priority}</priority>")
        body.append("  </url>")
    body.append("</urlset>")
    # Drop stale keys so deleted pages do not linger.
    keep = {pretty_path(u).rstrip("/") for u in urls}
    for stale in [k for k in store if k not in keep]:
        del store[stale]
    save_lastmod_store(store)
    (SITE / "sitemap.xml").write_text("\n".join(body) + "\n", encoding="utf-8")


def write_robots() -> None:
    (SITE / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {abs_url('sitemap.xml')}\n",
        encoding="utf-8",
    )


HOME_FAQ = [
    (
        "How many paper airplane designs are on this site?",
        "This hangar lists 58 paper airplane designs with illustrated folding steps. Filter by far throws, long floats, tricks, or display, then open any card for a full guide. If you need help choosing, see the best paper airplane design guide.",
        "站内有多少款纸飞机设计？",
        "机库目前有 58 款纸飞机设计，每款都有图解折法。可按飞得远、停得久、特技或摆设筛选，点开卡片即可看完整教程。若不知道怎么选，先看「最好的纸飞机怎么选」指南。",
    ),
    (
        "What paper should I use for paper airplanes?",
        "Standard A4 or US Letter printer paper around 70–80 gsm works for almost every design on this site. Lighter paper folds easily and glides well indoors, while slightly heavier paper holds sharper creases in outdoor air. Avoid thick card stock: it makes dense planes that stall almost immediately.",
        "折纸飞机应该用什么纸？",
        "普通的 A4 或 Letter 打印纸（约 70–80g/m²）几乎可以完成站内所有机型。较轻的纸更容易折叠，室内滑翔效果好；稍重一点的纸折痕更挺，适合在户外有风时使用。尽量不要用厚卡纸，那会让机身过重、很快就失速。",
    ),
    (
        "Are there 3D folding tutorials on this site?",
        "Yes. Every plane is cut into short illustrated folds, and the guides are built for 3D inspection — check each step from the side, top, and front so you can see exactly how the wings and nose line up before continuing. That makes unusual designs such as the Silent High Glider much easier to copy than a flat diagram.",
        "站内有 3D 折法教程吗？",
        "有。每款纸飞机都拆成了简短的图解步骤，教程按 3D 视角组织：可以从侧面、顶部和正面检查每一步，先看清机翼和机头的位置关系再继续折。像「静音高抛滑翔机」这类造型特别的机型，跟着 3D 视角比看平面图容易得多。",
    ),
    (
        "Can I test-fly a plane before folding it?",
        "Each guide lists an estimated flight distance and hang time, and the test-flight preview shows how the finished design should glide once it leaves your hand. Fold your own version, then compare it with the preview: if it dives, veers, or stalls, adjust the wings and try again.",
        "可以先试飞再动手折吗？",
        "每个详情页都给出估算的飞行距离和滞空时间，试飞预览会展示这架飞机脱手后应有的滑翔状态。折好后对照预览检查：如果出现下坠、跑偏或失速，调整机翼再试一次即可。",
    ),
    (
        "How far can a paper airplane fly?",
        "In normal indoor conditions the designs in this collection travel roughly 10–26 metres (33–85 feet) with a level throw. Distance designs such as the Rocket-Launch Dart and Classic Dart sit at the top of that range. Wind, paper weight, and small fold errors can easily change the result by several metres.",
        "纸飞机能飞多远？",
        "在正常的室内环境下，站内机型以水平投掷大约能飞 10–26 米。火箭投射机、经典飞镖这类远距机型处于这个区间的上限。风力、纸张克重和细微的折叠误差，都可能让结果相差好几米。",
    ),
    (
        "How long can a paper airplane stay in the air?",
        "Hang time ranges from a couple of seconds for heavy darts to roughly 10–13 seconds for well-trimmed gliders such as the Silent High Glider. Long flights come from light paper, a gentle upward launch, and a high release point — more than from throwing harder.",
        "纸飞机能滞空多久？",
        "偏重的机型可能只有两三秒，而「静音高抛滑翔机」这类调整得当的滑翔机可以达到 10–13 秒左右。想要长时间滞空，关键在轻薄纸张、略向上扬的轻投和更高的出手位置，而不是用力猛抛。",
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
        "Only some designs need a cut, usually to open a small slit or shape the tail. Cards marked Needs cut are optional — pick Hands only in the filter to keep planes you can fold with just a sheet of paper.",
        "这些纸飞机需要剪刀吗？",
        "只有部分机型需要剪一刀，通常用来开一个小口或修整机尾。卡片上会标“需剪”，左侧筛选也可选“只用手折”，只看徒手就能完成的机型。",
    ),
    (
        "A4 or Letter paper — does the size matter?",
        "Both work. A4 is slightly narrower and taller than US Letter, which changes the wing proportions by a few millimetres. Fold along the paper's own edges and the plane will fly correctly either way; compare the estimated numbers instead of forcing a size.",
        "A4 和 Letter 纸有区别吗？",
        "两种都可以。A4 比 Letter 略窄略长，机翼比例会相差几毫米。只要始终对齐纸张自身的边线来折，两种尺寸都能正常飞行；与其强行换纸，不如直接参考页面上的估算数据。",
    ),
    (
        "Are these paper airplanes suitable for kids?",
        "Yes. Start with beginner designs such as the Classic Dart — straight folds, hands only. Intermediate and advanced models add squash folds and sharp creases that younger folders may need help with; master designs work best as a shared project.",
        "这些纸飞机适合小朋友折吗？",
        "适合。建议从「经典飞镖」这类入门机型开始：直线折法、只用手折。进阶和挑战机型会用到压折、对齐尖角，年纪较小的孩子可能需要协助；大师难度更适合当作亲子合作项目。",
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
            {i18n_text(q_en, q_zh, tag="summary")}
            {i18n_text(a_en, a_zh, tag="p")}
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
    title = f"Paper Airplane Designs — {count} Folding Guides · {SITE_NAME}"
    desc = (
        f"Browse {count} paper airplane designs with 3D step-by-step folds, estimated distance "
        "and hang time, and a test-flight preview. Filter by far throws, long floats, tricks, or display."
    )
    og = abs_url(OG_IMAGE)
    ld = hangar_jsonld(planes)
    ld_faq = home_faq_jsonld()
    head = f"""<!DOCTYPE html>
<html lang="en" data-lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}" />
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
    rest = rest.replace('href="#/"', 'href="/"', 1)
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
    write_robots()
    patch_index(planes)
    # Sitemap after pages so static HTML fingerprints match the shipped files.
    write_sitemap(planes)
    print(f"generated {len(planes)} plane pages + sitemap/robots")


if __name__ == "__main__":
    main()
