#!/usr/bin/env python3
"""Refresh plane data/images from foldnfly.com into site/."""
import html as H
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ASSETS = SITE / "assets" / "planes"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
DIFF_CN = {"Easy": "简单", "Medium": "中等", "Hard": "困难", "Expert": "专家"}
TAG_CN = {
    "distance": "远距",
    "time_aloft": "滞空",
    "acrobatic": "特技",
    "decorative": "装饰",
}


def curl(url, out=None, timeout=25):
    if out is None:
        return subprocess.check_output(
            ["curl", "-sL", "-A", UA, "--compressed", "--max-time", str(timeout), "--fail", url]
        ).decode("utf-8", "replace")
    code = subprocess.check_output(
        [
            "curl",
            "-sL",
            "-A",
            UA,
            "--compressed",
            "--max-time",
            str(timeout),
            "-o",
            str(out),
            "-w",
            "%{http_code}",
            url,
        ]
    ).decode().strip()
    return code == "200" or (out.exists() and out.stat().st_size > 200)


def strip_tags(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return H.unescape(s).strip()


def load_meta(hangar_html):
    planes_meta = []
    for m in re.finditer(
        r'<div class="filterable col p-0 ([^"]*)" data-m="(\d+)" data-r="(\d+)" '
        r'data-h="(\d+)" data-d="(\d+)" data-t="(\d+)" id="p(\d+)">(.*?)</a>\s*</div>\s*</div>',
        hangar_html,
        re.S,
    ):
        classes, block = m.group(1), m.group(8)
        href = re.search(r'href="([^"]+)"', block)
        title = re.search(r'title="([^"]*)"', block)
        name = re.search(r"<b>([^<]+)</b>", block)
        diff = re.search(r'class="diff">([^<]+)', block)
        super_ = re.search(r'class="super"><span>([^<]+)', block)
        tag_map = {
            "distance": "distance",
            "duration": "time_aloft",
            "acrobatic": "acrobatic",
            "decorative": "decorative",
        }
        tags = [tag_map.get(t, t) for t in re.findall(r"tag_(\w+)", classes)]
        planes_meta.append(
            {
                "id": int(m.group(7)),
                "name": name.group(1) if name else "",
                "slug": href.group(1).split("#")[-1] if href else "",
                "blurb": H.unescape(title.group(1)) if title else "",
                "difficulty": diff.group(1) if diff else "",
                "difficultyLevel": int(m.group(4)),
                "tags": tags,
                "scissors": "cut1" in classes,
                "popularity": int(m.group(3)),
                "distanceScore": int(m.group(5)),
                "timeScore": int(m.group(6)),
                "badge": super_.group(1) if super_ else None,
            }
        )
    return planes_meta


def fetch_plane(meta):
    pid = meta["id"]
    html = curl(f"https://www.foldnfly.com/{pid}.html")
    desc_m = re.search(
        r'<div class="details[\s\S]*?<p class="left[^"]*">([\s\S]*?)</p>', html
    )
    description = strip_tags(desc_m.group(1)) if desc_m else meta["blurb"]
    steps = []
    for sm in re.finditer(
        r'<div class="step s(\d+)">\s*<picture>[\s\S]*?<p><b>\d+\.</b>\s*([\s\S]*?)</p>\s*</div>',
        html,
    ):
        n = int(sm.group(1))
        steps.append(
            {
                "n": n,
                "text": strip_tags(sm.group(2)),
                "image": f"assets/planes/{pid}/{n}.webp",
            }
        )

    pdir = ASSETS / str(pid)
    pdir.mkdir(parents=True, exist_ok=True)
    for fname, remote in [
        ("thumb.webp", f"https://www.foldnfly.com/data/{pid}/rect_s.webp"),
        ("thumb.jpg", f"https://www.foldnfly.com/data/{pid}/rect.jpg"),
        ("square.webp", f"https://www.foldnfly.com/data/{pid}/square_s.webp"),
    ]:
        curl(remote, pdir / fname)

    for st in steps:
        n = st["n"]
        webp = pdir / f"{n}.webp"
        jpg = pdir / f"{n}.jpg"
        if curl(f"https://www.foldnfly.com/data/{pid}/{n}_s.webp", webp) and webp.stat().st_size > 500:
            st["image"] = f"assets/planes/{pid}/{n}.webp"
        elif curl(f"https://www.foldnfly.com/data/{pid}/{n}.jpg", jpg) and jpg.stat().st_size > 500:
            st["image"] = f"assets/planes/{pid}/{n}.jpg"
        else:
            st["image"] = f"https://www.foldnfly.com/data/{pid}/{n}.jpg"

    return {
        **meta,
        "difficultyCn": DIFF_CN.get(meta["difficulty"], meta["difficulty"]),
        "tagsCn": [TAG_CN.get(t, t) for t in meta["tags"]],
        "description": description,
        "paper": "Letter & A4",
        "steps": steps,
        "thumb": f"assets/planes/{pid}/thumb.webp",
        "square": f"assets/planes/{pid}/square.webp",
        "source": f"https://www.foldnfly.com/{pid}.html",
    }


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    hangar = curl("https://www.foldnfly.com/")
    meta = load_meta(hangar)
    print(f"found {len(meta)} planes", flush=True)
    planes = []
    for i, m in enumerate(meta, 1):
        print(f"[{i}/{len(meta)}] {m['id']} {m['name']}", flush=True)
        planes.append(fetch_plane(m))
    out = SITE / "data" / "planes.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(planes, ensure_ascii=False, indent=2), "utf-8")
    print("wrote", out, "steps", sum(len(p["steps"]) for p in planes), flush=True)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print("curl failed", e, file=sys.stderr)
        sys.exit(1)
