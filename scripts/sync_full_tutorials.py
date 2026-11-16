#!/usr/bin/env python3
"""Sync complete foldnfly tutorials into planes.json (all steps + images).

Phase 1: fetch HTML + rewrite step text (fast).
Phase 2: download missing step images in parallel.
"""
from __future__ import annotations

import argparse
import html as H
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = SITE / "data" / "planes.json"
ASSETS = SITE / "assets" / "planes"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
PRESERVE_HERO = {"Wingtip-Dart"}
SKIP_COMPLETE = {"Wingtip-Dart"}

sys.path.insert(0, str(ROOT / "scripts"))
from rewrite_step_copy import rewrite_cn, rewrite_en  # noqa: E402

_EN_ZH: dict[str, str] = {}
_zh_path = ROOT / "scripts" / "_steps_en_to_zh.json"
if _zh_path.is_file():
    try:
        _EN_ZH = json.loads(_zh_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        _EN_ZH = {}


def curl_text(url: str, timeout: int = 45) -> str | None:
    try:
        proc = subprocess.run(
            [
                "curl",
                "-sL",
                "-A",
                UA,
                "--compressed",
                "--max-time",
                str(timeout),
                "--retry",
                "2",
                "--retry-delay",
                "1",
                "--fail",
                url,
            ],
            capture_output=True,
            check=False,
        )
    except Exception:
        return None
    if proc.returncode != 0 or not proc.stdout:
        return None
    return proc.stdout.decode("utf-8", "replace")


def curl_file(url: str, out: Path, timeout: int = 45, min_size: int = 500) -> bool:
    out.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            "curl",
            "-sL",
            "-A",
            UA,
            "--compressed",
            "--max-time",
            str(timeout),
            "--retry",
            "2",
            "--retry-delay",
            "1",
            "-o",
            str(out),
            "-w",
            "%{http_code}",
            url,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    code = (proc.stdout or "").strip()
    return code == "200" and out.exists() and out.stat().st_size > min_size


def strip_tags(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return H.unescape(s).strip()


def parse_steps(html: str) -> list[dict]:
    seen: dict[int, dict] = {}
    for part in re.split(r'(?=<div class="step s\d+">)', html):
        m = re.match(r'<div class="step s(\d+)">', part)
        if not m:
            continue
        n = int(m.group(1))
        tm = re.search(r"<p><b>\d+\.</b>\s*([\s\S]*?)</p>", part)
        if not tm:
            continue
        seen[n] = {"n": n, "raw": strip_tags(tm.group(1))}
    return [seen[k] for k in sorted(seen)]


def to_webp(src: Path, dest: Path) -> bool:
    try:
        from PIL import Image

        Image.open(src).convert("RGB").save(dest, "WEBP", quality=85, method=6)
        return dest.exists() and dest.stat().st_size > 500
    except Exception:
        return False


def local_image_ok(slug: str, n: int) -> Path | None:
    pdir = ASSETS / slug
    webp = pdir / f"{n}.webp"
    jpg = pdir / f"{n}.jpg"
    if webp.exists() and webp.stat().st_size > 500:
        return webp
    if jpg.exists() and jpg.stat().st_size > 2000:
        return jpg
    return None


def download_one_image(pid: int, slug: str, n: int) -> tuple[str, bool]:
    """Returns (image_path_or_url, downloaded_ok)."""
    existing = local_image_ok(slug, n)
    if existing:
        rel = f"assets/planes/{slug}/{existing.name}"
        return rel, True

    pdir = ASSETS / slug
    pdir.mkdir(parents=True, exist_ok=True)
    webp = pdir / f"{n}.webp"
    jpg = pdir / f"{n}.jpg"

    if curl_file(f"https://www.foldnfly.com/data/{pid}/{n}_s.webp", webp, timeout=35):
        return f"assets/planes/{slug}/{n}.webp", True
    if curl_file(
        f"https://www.foldnfly.com/data/{pid}/{n}.jpg", jpg, timeout=50, min_size=2000
    ):
        if to_webp(jpg, webp):
            try:
                jpg.unlink()
            except OSError:
                pass
            return f"assets/planes/{slug}/{n}.webp", True
        return f"assets/planes/{slug}/{n}.jpg", True
    return f"https://www.foldnfly.com/data/{pid}/{n}.jpg", False


def step_cn(raw: str, en: str, old_cn: str) -> str:
    mapped = _EN_ZH.get(raw) or _EN_ZH.get(en) or ""
    if old_cn and re.search(r"[\u4e00-\u9fff]", old_cn):
        return rewrite_cn(old_cn, en)
    if mapped:
        return rewrite_cn(mapped, en)
    cn = rewrite_cn("", en)
    if re.search(r"[\u4e00-\u9fff]", cn or ""):
        return cn
    return "按图示完成本步折法。"


def sync_texts(planes: list[dict], start: int = 0, only: set[str] | None = None) -> None:
    for i, plane in enumerate(planes):
        if i < start:
            continue
        if only and plane["slug"] not in only:
            continue
        pid = plane["id"]
        slug = plane["slug"]
        old_n = len(plane.get("steps") or [])
        print(f"[text {i+1}/{len(planes)}] {slug} (id={pid})", flush=True)

        if slug in SKIP_COMPLETE and old_n >= 10:
            print(f"  skip complete ({old_n})", flush=True)
            continue

        html = None
        for attempt in range(4):
            html = curl_text(f"https://www.foldnfly.com/{pid}.html", timeout=50)
            if html:
                break
            time.sleep(1.5 * (attempt + 1))
        if not html:
            print("  FAIL fetch", flush=True)
            continue

        parsed = parse_steps(html)
        if not parsed:
            print("  FAIL parse", flush=True)
            continue

        if old_n == len(parsed) and all(
            local_image_ok(slug, s["n"]) for s in (plane.get("steps") or [])
        ):
            # Still refresh text if somehow short, else skip
            print(f"  already {old_n} steps with images", flush=True)
            # still ensure paths/text are rewritten once
            pass

        new_steps = []
        old_by_n = {s.get("n"): s for s in (plane.get("steps") or [])}
        for item in parsed:
            n = item["n"]
            raw = item["raw"]
            en = rewrite_en(raw)
            old = old_by_n.get(n) or {}
            cn = step_cn(raw, en, old.get("textCn") or "")
            existing = local_image_ok(slug, n)
            if existing:
                img = f"assets/planes/{slug}/{existing.name}"
            else:
                img = f"assets/planes/{slug}/{n}.webp"
            new_steps.append({"n": n, "text": en, "textCn": cn, "image": img})

        plane["steps"] = new_steps
        plane["source"] = f"https://www.foldnfly.com/{pid}.html"
        print(f"  steps {old_n} → {len(new_steps)}", flush=True)
        DATA.write_text(
            json.dumps(planes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        time.sleep(0.25)


def collect_image_jobs(planes: list[dict]) -> list[tuple[int, str, int]]:
    jobs = []
    for plane in planes:
        pid = plane["id"]
        slug = plane["slug"]
        for s in plane.get("steps") or []:
            n = int(s["n"])
            if local_image_ok(slug, n):
                # normalize path in json
                existing = local_image_ok(slug, n)
                s["image"] = f"assets/planes/{slug}/{existing.name}"
                continue
            jobs.append((pid, slug, n))
    return jobs


def sync_images(planes: list[dict], workers: int = 8) -> None:
    jobs = collect_image_jobs(planes)
    print(f"downloading {len(jobs)} missing step images with {workers} workers…", flush=True)
    if not jobs:
        return

    results: dict[tuple[str, int], str] = {}
    ok = fail = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {
            ex.submit(download_one_image, pid, slug, n): (slug, n)
            for pid, slug, n in jobs
        }
        for fut in as_completed(futs):
            slug, n = futs[fut]
            try:
                path, good = fut.result()
            except Exception as e:
                path, good = f"FAIL:{e}", False
            results[(slug, n)] = path
            if good:
                ok += 1
            else:
                fail += 1
            if (ok + fail) % 20 == 0:
                print(f"  images {ok+fail}/{len(jobs)} ok={ok} fail={fail}", flush=True)

    for plane in planes:
        slug = plane["slug"]
        for s in plane.get("steps") or []:
            key = (slug, int(s["n"]))
            if key in results:
                s["image"] = results[key]
            elif local_image_ok(slug, int(s["n"])):
                existing = local_image_ok(slug, int(s["n"]))
                s["image"] = f"assets/planes/{slug}/{existing.name}"

        # refresh thumbs unless protected
        if slug not in PRESERVE_HERO:
            pdir = ASSETS / slug
            pdir.mkdir(parents=True, exist_ok=True)
            curl_file(
                f"https://www.foldnfly.com/data/{plane['id']}/rect_s.webp",
                pdir / "thumb.webp",
                timeout=35,
            )
            curl_file(
                f"https://www.foldnfly.com/data/{plane['id']}/square_s.webp",
                pdir / "square.webp",
                timeout=35,
            )
            plane["thumb"] = f"assets/planes/{slug}/thumb.webp"
            plane["square"] = f"assets/planes/{slug}/square.webp"

    DATA.write_text(
        json.dumps(planes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"images done ok={ok} fail={fail}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--only", type=str, default="")
    ap.add_argument("--texts-only", action="store_true")
    ap.add_argument("--images-only", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    only = {s.strip() for s in args.only.split(",") if s.strip()} or None

    planes = json.loads(DATA.read_text(encoding="utf-8"))
    if not args.images_only:
        sync_texts(planes, start=args.start, only=only)
        planes = json.loads(DATA.read_text(encoding="utf-8"))
    if not args.texts_only:
        sync_images(planes, workers=args.workers)
    total = sum(len(p.get("steps") or []) for p in planes)
    print(f"finished. planes={len(planes)} total_steps={total}", flush=True)


if __name__ == "__main__":
    main()
