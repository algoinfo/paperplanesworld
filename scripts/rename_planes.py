#!/usr/bin/env python3
"""Rename foldnfly-origin plane names to original hangar names; rewrite asset paths."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = SITE / "data" / "planes.json"
ASSETS = SITE / "assets" / "planes"
PLANES_HTML = SITE / "planes"

# old slug → (new name EN, new name CN, new slug)
RENAME: dict[str, tuple[str, str, str]] = {
    "The-Bird": ("Wingtip Dart", "翼尖飞镖", "Wingtip-Dart"),
    "Sky-OmniWing": ("Wide-Wing Cruiser", "宽翼巡航机", "Wide-Wing-Cruiser"),
    "Basic-Dart": ("Classic Dart", "经典飞镖", "Classic-Dart"),
    "Heavy-Nosed-Plane": ("Weighted-Nose Glider", "重头滑翔机", "Weighted-Nose-Glider"),
    "Fast-Hawk": ("Streamline Ranger", "流线远航机", "Streamline-Ranger"),
    "Lock-Bottom": ("Locked-Keel Flyer", "锁底飞航机", "Locked-Keel-Flyer"),
    "Horizon": ("Far-Horizon Dart", "地平线飞镖", "Far-Horizon-Dart"),
    "Hunting-Flight": ("Hard-Throw Ranger", "劲投远航机", "Hard-Throw-Ranger"),
    "Tail-Spin": ("Opposite-Flap Spinner", "反襟翼旋转机", "Opposite-Flap-Spinner"),
    "Lift-Off": ("Rocket-Launch Dart", "火箭投射机", "Rocket-Launch-Dart"),
    "V-Wing": ("Quiet V-Glider", "静音V翼机", "Quiet-V-Glider"),
    "Sonic-Jet": ("Cockpit Jet", "座舱喷气机", "Cockpit-Jet"),
    "The-Arrow": ("Needle Dart", "细针飞镖", "Needle-Dart"),
    "Raven": ("Wide-Wing Circler", "宽翼盘旋机", "Wide-Wing-Circler"),
    "The-UFO": ("Disc Floater", "圆盘浮空机", "Disc-Floater"),
    "Spinner-Plane": ("Aerial Spinner", "空中旋转机", "Aerial-Spinner"),
    "Soaring-Eagle": ("Circling Soarer", "盘旋滑翔机", "Circling-Soarer"),
    "Navy-Plane": ("Deck-Speed Jet", "甲板速度机", "Deck-Speed-Jet"),
    "Stealth-Glider": ("Silent High Glider", "静音高抛滑翔机", "Silent-High-Glider"),
    "Fast-Glider": ("Split-Tail Glider", "分尾滑翔机", "Split-Tail-Glider"),
    "Trooper": ("Midrange Straight Dart", "中距直线镖", "Midrange-Straight-Dart"),
    "Space-Fighter": ("Evasive Dart", "机动飞镖", "Evasive-Dart"),
    "Arrowhead": ("Pointed Classic Dart", "尖头经典镖", "Pointed-Classic-Dart"),
    "Condor": ("Lock-Fold Glider", "锁折滑翔机", "Lock-Fold-Glider"),
    "Canard": ("Forward-Wing Dart", "前翼飞镖", "Forward-Wing-Dart"),
    "Mosquito": ("Blunt-Nose Cruiser", "钝头巡航机", "Blunt-Nose-Cruiser"),
    "Flying-Shovel": ("Wedge Floater", "楔形浮空机", "Wedge-Floater"),
    "The-Stable": ("Wide-Loop Floater", "大环浮空机", "Wide-Loop-Floater"),
    "Spin-Plane": ("Aerial Dancer", "空中舞动机", "Aerial-Dancer"),
    "Origami-Plane": ("Expert Origami Glider", "大师折纸滑翔机", "Expert-Origami-Glider"),
    "Zip-Dart": ("Slim Zip Dart", "细身疾镖", "Slim-Zip-Dart"),
    "Fast-Swallow": ("Tail-Wing Soarer", "尾翼翱翔机", "Tail-Wing-Soarer"),
    "Vulture": ("Compact Speed Dart", "紧凑速度镖", "Compact-Speed-Dart"),
    "Loop-Plane": ("Vertical Loop Flyer", "垂直环飞机", "Vertical-Loop-Flyer"),
    "Wilson": ("Flared-Wing Dart", "外扩翼飞镖", "Flared-Wing-Dart"),
    "Tailed-Plane": ("Twin-Piece Tailer", "双件尾翼机", "Twin-Piece-Tailer"),
    "Stunt-Plane": ("Tip-Tune Stunter", "翼尖特技机", "Tip-Tune-Stunter"),
    "Underside-Plane": ("Underflap Glider", "下襟翼滑翔机", "Underflap-Glider"),
    "Sailor-Wing": ("Soft-Push Cruiser", "轻推巡航机", "Soft-Push-Cruiser"),
    "Uppercat": ("Ear-Wing Glider", "耳翼滑翔机", "Ear-Wing-Glider"),
    "The-Buzz": ("Trim-Tab Cruiser", "可调尾翼巡航机", "Trim-Tab-Cruiser"),
    "Gliding-Plane": ("Quick Floater", "快折浮空机", "Quick-Floater"),
    "Eagle-Eye": ("Display Fold Sculpture", "展示折纸雕塑", "Display-Fold-Sculpture"),
    "King-Bee": ("Wiggle-Throw Stunter", "摆动特技机", "Wiggle-Throw-Stunter"),
    "Boomerang": ("Return-Curve Flyer", "回旋曲线机", "Return-Curve-Flyer"),
    "The-Square": ("Stiff-Wing Wind Flyer", "硬翼抗风机", "Stiff-Wing-Wind-Flyer"),
    "White-Dove": ("Dove Display Fold", "白鸽展示折", "Dove-Display-Fold"),
    "Light-Spinner": ("Wide Spiral Flyer", "大螺旋飞机", "Wide-Spiral-Flyer"),
    "Fun-Flyer": ("Catch-It Toss Plane", "抛接飞机", "Catch-It-Toss-Plane"),
    "Wedge-Plane": ("Inside-Out Dart", "内翻飞镖", "Inside-Out-Dart"),
    "Jet-Fighter": ("Long-Glide Jet", "长滑喷气机", "Long-Glide-Jet"),
    "The-Basic": ("Simple Floater", "简易浮空机", "Simple-Floater"),
    "Sea-Glider": ("Bend-Wing Experiment", "可弯翼实验机", "Bend-Wing-Experiment"),
    "Cross-Wing": ("Heavy-Nose Crosser", "重头十字翼", "Heavy-Nose-Crosser"),
    "Royal-Wing": ("Slow-Drift Glider", "慢漂滑翔机", "Slow-Drift-Glider"),
    "Star-Wing": ("Star Display Fold", "星形展示折", "Star-Display-Fold"),
    "The-Sprinter": ("Flapping-Wing Sprinter", "扑翼冲刺机", "Flapping-Wing-Sprinter"),
    "Water-Plane": ("Smooth Water Glide", "水面滑翔机", "Smooth-Water-Glide"),
}


def rewrite_text(text: str, old_name: str, new_name: str) -> str:
    if not text:
        return text
    out = text.replace(old_name, new_name)
    out = re.sub(
        r"This design is an improved version of the original Proto OmniWing,[^.]*\.\s*",
        "",
        out,
        flags=re.I,
    )
    out = re.sub(r"\bdesigned by M[a-zA-Z .]*?\.\s*", "", out)
    out = re.sub(r"Don't let the name fool you,\s*", "", out, flags=re.I)
    out = re.sub(
        r"This designs looks like a superhero cat with cute little ears\.\s*",
        "Tall ear-like folds give this glider a distinctive silhouette. ",
        out,
        flags=re.I,
    )
    return out


def rewrite_paths(obj, old_slug: str, new_slug: str):
    if isinstance(obj, dict):
        return {k: rewrite_paths(v, old_slug, new_slug) for k, v in obj.items()}
    if isinstance(obj, list):
        return [rewrite_paths(v, old_slug, new_slug) for v in obj]
    if isinstance(obj, str):
        return obj.replace(f"assets/planes/{old_slug}/", f"assets/planes/{new_slug}/")
    return obj


def main() -> None:
    planes = json.loads(DATA.read_text(encoding="utf-8"))
    missing = [p["slug"] for p in planes if p["slug"] not in RENAME]
    if missing:
        raise SystemExit(f"rename map missing slugs: {missing}")

    tmp_root = ASSETS / "_rename_tmp"
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True)

    updated = []
    redirects = []
    for plane in planes:
        old_slug = plane["slug"]
        new_name, new_cn, new_slug = RENAME[old_slug]
        old_name = plane["name"]

        src = ASSETS / old_slug
        mid = tmp_root / new_slug
        if not src.exists():
            raise SystemExit(f"missing assets for {old_slug}")
        if mid.exists():
            shutil.rmtree(mid)
        shutil.move(str(src), str(mid))

        plane["name"] = new_name
        plane["nameCn"] = new_cn
        plane["slug"] = new_slug
        for key in ("description", "descriptionCn", "blurb", "blurbCn"):
            if key in plane and isinstance(plane[key], str):
                plane[key] = rewrite_text(plane[key], old_name, new_name)
        for step in plane.get("steps") or []:
            for key in ("text", "textCn"):
                if key in step and isinstance(step[key], str):
                    step[key] = rewrite_text(step[key], old_name, new_name)
        plane = rewrite_paths(plane, old_slug, new_slug)
        updated.append(plane)
        redirects.append((old_slug, new_slug))

    for _, _, new_slug in RENAME.values():
        mid = tmp_root / new_slug
        dest = ASSETS / new_slug
        if not mid.exists():
            continue
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(mid), str(dest))
    shutil.rmtree(tmp_root, ignore_errors=True)

    DATA.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if PLANES_HTML.is_dir():
        for old in PLANES_HTML.glob("*.html"):
            old.unlink()

    lines = ["# Old foldnfly-era slugs → hangar names"]
    for old_slug, new_slug in redirects:
        if old_slug == new_slug:
            continue
        lines.append(f"/planes/{old_slug} /planes/{new_slug} 301")
        lines.append(f"/planes/{old_slug}.html /planes/{new_slug} 301")
    (SITE / "_redirects").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"renamed {len(updated)} planes; wrote _redirects ({len(lines) - 1} rules)")


if __name__ == "__main__":
    main()
