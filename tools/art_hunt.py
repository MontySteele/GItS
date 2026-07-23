#!/usr/bin/env python3
"""Discover REAL wiki file titles for an art hunt (furina-art-pass-requirements 9.2).

Shortlist rows in art/plan.tsv name a `wiki_title`. Inventing those titles from
memory does not work -- a wrong guess is not caught until art_fetch reports it
MISSING, one round-trip per mistake, and a *plausible* wrong guess is worse
because it silently resolves to some other character's art. This enumerates
what the wiki actually has so shortlists are built from a real inventory.

    python tools/art_hunt.py Furina                    # search File: namespace
    python tools/art_hunt.py Furina --category         # Category:Furina members
    python tools/art_hunt.py Neuvillette --limit 100

Read-only against the same MediaWiki API and User-Agent as art_fetch.py.
Prints titles one per line; nothing is downloaded and nothing is written.
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

API = "https://genshin-impact.fandom.com/api.php"
HEADERS = {"User-Agent": "TeyvatSpire-art-sprint/0.1 (private fan build; Tier F sourcing)"}

# File: search returns every uploaded asset, and for a voiced character most of
# them are .ogg voice lines. Filtering here keeps the signal readable.
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp")

# Wiki titles carry characters cp1252 cannot encode, and this prints to a
# Windows console. Replacing them keeps the tool usable; the exact bytes come
# from the API at fetch time, not from this listing.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def api_get(params):
    params = dict(params, format="json")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def search_files(term, limit):
    """Full-text search restricted to the File: namespace (6)."""
    out, offset = [], 0
    while len(out) < limit:
        data = api_get({
            "action": "query", "list": "search", "srsearch": term,
            "srnamespace": 6, "srlimit": min(50, limit - len(out)),
            "sroffset": offset,
        })
        hits = data.get("query", {}).get("search", [])
        if not hits:
            break
        out.extend(h["title"] for h in hits)
        if "continue" not in data:
            break
        offset = data["continue"]["sroffset"]
        time.sleep(0.4)          # be a polite API citizen
    return out


def category_files(term, limit):
    out, cont = [], None
    while len(out) < limit:
        params = {
            "action": "query", "list": "categorymembers",
            "cmtitle": f"Category:{term}", "cmnamespace": 6,
            "cmlimit": min(50, limit - len(out)),
        }
        if cont:
            params["cmcontinue"] = cont
        data = api_get(params)
        members = data.get("query", {}).get("categorymembers", [])
        if not members:
            break
        out.extend(m["title"] for m in members)
        cont = data.get("continue", {}).get("cmcontinue")
        if not cont:
            break
        time.sleep(0.4)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("term")
    ap.add_argument("--category", action="store_true",
                    help="list Category:<term> members instead of searching")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--all-types", action="store_true",
                    help="do not filter to image extensions")
    args = ap.parse_args()

    try:
        titles = (category_files if args.category else search_files)(args.term, args.limit)
    except Exception as exc:                       # noqa: BLE001 - CLI surface
        print(f"wiki API error: {exc}", file=sys.stderr)
        return 1

    kept = titles if args.all_types else [
        t for t in titles if t.lower().endswith(IMAGE_EXT)]
    for t in kept:
        print(t)
    dropped = len(titles) - len(kept)
    note = f" ({dropped} non-image dropped)" if dropped else ""
    print(f"\n{len(kept)} title(s){note}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
