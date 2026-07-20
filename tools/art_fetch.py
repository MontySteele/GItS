#!/usr/bin/env python3
"""Fetch wiki-hosted official art per art/plan.tsv (docs/art-sprint-spec.md §2).

Resolves File: titles via the Genshin Fandom MediaWiki API, downloads originals
into art/raw/ (gitignored — Tier F never ships), and writes art/SOURCES.tsv
(filename → source_url → tier → replace_priority) as it goes.

Usage: python3 tools/art_fetch.py            # stdlib only, no deps
"""
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "art" / "raw"
PLAN = ROOT / "art" / "plan.tsv"
SOURCES = ROOT / "art" / "SOURCES.tsv"
API = "https://genshin-impact.fandom.com/api.php"
HEADERS = {"User-Agent": "TeyvatSpire-art-sprint/0.1 (private fan build; Tier F sourcing)"}

# replace_priority by output area: how visible the asset is if the project ever
# goes public (= how urgently it needs a Tier O replacement).
def priority(out: str) -> str:
    if "/cards/" in out or "selection_splash" in out or "/model/" in out:
        return "high"
    if "/powers/" in out or "/relics/" in out:
        return "medium"
    return "low"


def read_plan():
    rows = []
    with open(PLAN, newline="") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 10:
                sys.exit(f"bad plan row: {line!r}")
            rows.append({
                "asset_id": parts[0], "out": parts[1], "w": int(parts[2]), "h": int(parts[3]),
                "mode": parts[4], "focus": parts[5], "pick": parts[6], "rank": int(parts[7]),
                "source": parts[8], "title": parts[9],
                "frame": int(parts[10]) if len(parts) > 10 and parts[10] else None,
            })
    return rows


def api_get(params):
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def resolve(titles):
    """title (no File: prefix) -> (url, WxH). Batches of 50."""
    out = {}
    titles = sorted(set(titles))
    for i in range(0, len(titles), 50):
        batch = ["File:" + t for t in titles[i:i + 50]]
        d = api_get({"action": "query", "prop": "imageinfo", "iiprop": "url|size",
                     "titles": "|".join(batch)})
        q = d.get("query", {})
        # normalized: from-title -> canonical title
        norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        canon_to_orig = {}
        for t in batch:
            canon_to_orig[norm.get(t, t)] = t[len("File:"):]
        for p in q.get("pages", {}).values():
            orig = canon_to_orig.get(p.get("title"))
            if orig is None:
                continue
            ii = p.get("imageinfo")
            if ii:
                out[orig] = (ii[0]["url"], f"{ii[0].get('width')}x{ii[0].get('height')}")
        time.sleep(0.3)
    return out


def rawname(title: str) -> str:
    return title.replace("/", "_").replace(" ", "_")


def main():
    rows = read_plan()
    resolved = resolve([r["title"] for r in rows])

    # SVG element icons: also fetch the same-name .png as a raster fallback
    svg_fallbacks = sorted({r["title"][:-4] + ".png" for r in rows if r["source"] == "svg"})
    resolved.update(resolve([t for t in svg_fallbacks if t not in resolved]))

    missing = sorted({r["title"] for r in rows if r["title"] not in resolved})
    RAW.mkdir(parents=True, exist_ok=True)

    downloaded, srcrows = 0, []
    for title, (url, dims) in sorted(resolved.items()):
        dest = RAW / rawname(title)
        if not dest.exists():
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
                f.write(r.read())
            downloaded += 1
            time.sleep(0.4)  # be polite to the wiki CDN
        print(f"  {title}  ({dims})")

    # SOURCES.tsv: one row per plan row (final target or candidate), per spec §0
    with open(SOURCES, "w", newline="") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["filename", "source_url", "tier", "replace_priority"])
        seen = set()
        for r in rows:
            if r["title"] not in resolved:
                continue
            if r["pick"] == "shortlist":
                fn = f"art/candidates/{r['asset_id']}/r{r['rank']}.png"
            else:
                fn = r["out"]
            key = (fn, r["title"])
            if key in seen:
                continue
            seen.add(key)
            w.writerow([fn, resolved[r["title"]][0], "F", priority(r["out"])])

    print(f"\n{len(resolved)} titles resolved, {downloaded} new downloads -> {RAW}")
    print(f"SOURCES.tsv: {len(seen)} rows")
    if missing:
        print("\nMISSING on wiki (gap-list / fix plan.tsv):")
        for t in missing:
            print("  " + t)
        sys.exit(2)


if __name__ == "__main__":
    main()
