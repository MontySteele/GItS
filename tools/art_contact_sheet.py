#!/usr/bin/env python3
"""Emit an art contact sheet — shortlist candidates, click to select.

"Export picks" downloads art/picks.tsv; apply with:
    python tools/art_process.py --apply-picks art/picks.tsv

Roster/character-aware (furina-art-pass-requirements.md 9.4). The Klee sprint
put every shortlist on one page, which was fine at Klee's scale and is not at
Furina's: 101 outputs in one scroll is the "102-card wall" requirements sec.10
explicitly forbids. Batches come from that section.

    python tools/art_contact_sheet.py                    # everything (Klee default)
    python tools/art_contact_sheet.py --batch identity   # basics + generic + rares
    python tools/art_contact_sheet.py --list             # batch sizes, review nothing

Batch membership is computed from the canonical sheets, not hand-listed, and
assignment is FIRST MATCH WINS because `archetypes` is a list -- a third of
Furina's rows carry two, so "salon or fanfare" and "spotlight" genuinely
overlap. Every shortlisted asset lands in exactly one batch, and anything the
sheets do not classify goes to `unsorted` rather than being dropped: a review
tool that silently omits a card reads as "reviewed" when it was never seen.

Stdlib only. Images referenced relative to art/ (candidates/..., gitignored).
"""
import argparse
import html
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from art_fetch import read_plan  # noqa: E402

DOCS = ROOT / "docs"
SHEETS = ("furina-cards.yaml", "klee-cards.yaml",
          "mondstadt-companions.yaml", "fontaine-companions.yaml")

BATCH_TITLES = {
    "identity": "Furina identity — basics, generic/courtroom, and all 15 rares",
    "salon-fanfare": "Furina Salon + Fanfare — Member readability, applause vs generic blue",
    "spotlight": "Furina Spotlight — invitations, billing, selector, shared cast",
    "companions": "Companions — Guest Stars, normals, and 5-star rares by character",
    "klee": "Klee — the original sprint's card slice",
    "assets": "UI / powers / relics / model — reviewed at native size",
    "unsorted": "Unsorted — no canonical sheet row and no known output path",
    "all": "All shortlists",
}

# The salon/fanfare/spotlight split is FURINA's review structure, not a global
# taxonomy -- it comes from her archetypes. Routing on the output path first
# keeps another character's cards out of it: Klee rows fell into `unsorted`
# when archetype was checked first, which reads as a classification failure
# rather than "these belong to a different character's batch".
BATCH_ORDER = ["identity", "salon-fanfare", "spotlight", "companions",
               "klee", "assets", "unsorted"]


def card_meta():
    """id -> {rarity, archetypes} from the canonical sheets. Empty if no yaml."""
    try:
        import yaml
    except ImportError:                      # stdlib-only fallback
        return {}
    meta = {}
    for name in SHEETS:
        path = DOCS / name
        if not path.exists():
            continue
        for row in yaml.safe_load(path.read_text(encoding="utf-8")) or []:
            if isinstance(row, dict) and "id" in row:
                meta[row["id"]] = {
                    "rarity": row.get("rarity"),
                    "archetypes": set(row.get("archetypes") or ()),
                }
    return meta


def batch_of(asset_id, out_path, meta):
    """Which review batch an asset belongs to. First match wins -- see docstring."""
    out = out_path.replace("\\", "/")
    if "/cards/companions/" in out:
        return "companions"
    if "/cards/klee/" in out:
        return "klee"
    if "/cards/furina/" not in out:
        # ui/, powers/, relics/, model/ -- requirements sec.10: "UI/model/power/
        # relic assets receive their own small native-size sheet."
        return "assets"

    m = meta.get(asset_id)
    if m is None:
        return "unsorted"
    arch = m["archetypes"]
    # sec.10 batch 1 is the identity read: the cards that establish who she is.
    if m["rarity"] in {"basic", "rare", "token"} or arch == {"generic"}:
        return "identity"
    if arch & {"salon", "fanfare"}:
        return "salon-fanfare"
    if "spotlight" in arch:
        return "spotlight"
    return "unsorted"


def render(assets, title, subtitle):
    blocks = []
    for aid, cands in assets.items():
        cells = []
        for r in sorted(cands, key=lambda x: x["rank"]):
            img = f"candidates/{aid}/r{r['rank']}.png"
            label = r["title"] + (f" @{r['frame']}%" if r["frame"] is not None else "")
            if not (ROOT / "art" / img).exists():
                cells.append(f'<div class="cand missing">r{r["rank"]}: missing<br>'
                             f'<small>{html.escape(label)}</small></div>')
                continue
            checked = " checked" if r["rank"] == 1 else ""
            cells.append(
                f'<label class="cand"><input type="radio" name="{aid}" value="{r["rank"]}"{checked}>'
                f'<img src="{img}" loading="lazy"><small>r{r["rank"]} · {html.escape(label)}</small></label>')
        blocks.append(f'<section><h2>{aid}</h2><div class="row">{"".join(cells)}</div></section>')

    return f"""<!doctype html><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
 body{{font:14px/1.4 -apple-system,sans-serif;margin:2em;background:#1b1b1f;color:#eee}}
 h2{{margin:1.2em 0 .3em;font-size:15px;color:#f8c471}}
 .row{{display:flex;gap:12px;flex-wrap:wrap}}
 .cand{{width:260px;cursor:pointer;text-align:center;color:#aaa}}
 .cand img{{width:250px;height:190px;object-fit:contain;background:#111;border:3px solid #333;border-radius:6px;display:block;margin:0 auto 4px}}
 .cand input{{display:none}}
 .cand:has(input:checked) img{{border-color:#e74c3c}}
 .cand.missing{{border:1px dashed #555;padding:8px;border-radius:6px}}
 #bar{{position:fixed;top:0;left:0;right:0;background:#111;padding:8px 2em;border-bottom:1px solid #333;z-index:9}}
 button{{background:#e74c3c;color:#fff;border:0;padding:6px 16px;border-radius:4px;font-size:14px;cursor:pointer}}
 main{{margin-top:3.6em}}
</style>
<div id="bar"><b>{html.escape(subtitle)}</b> — {len(assets)} cards ·
<button onclick="exportPicks()">Export picks.tsv</button>
<span style="color:#888">then: python tools/art_process.py --apply-picks art/picks.tsv</span></div>
<main>{"".join(blocks)}</main>
<script>
function exportPicks(){{
  let out="";
  document.querySelectorAll("section").forEach(s=>{{
    const id=s.querySelector("h2").textContent;
    const c=s.querySelector("input:checked");
    if(c) out+=id+"\\t"+c.value+"\\n";
  }});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(new Blob([out],{{type:"text/tab-separated-values"}}));
  a.download="picks.tsv"; a.click();
}}
</script>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", default="all", choices=sorted(BATCH_TITLES))
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--list", action="store_true",
                    help="print batch sizes and exit; review nothing")
    args = ap.parse_args()

    meta = card_meta()
    rows = [r for r in read_plan() if r["pick"] == "shortlist"]

    tally = OrderedDict((b, 0) for b in BATCH_ORDER)
    assets = OrderedDict()
    for r in rows:
        b = batch_of(r["asset_id"], r["out"], meta)
        if r["asset_id"] not in assets:
            tally[b] += 1
        if args.batch in (b, "all"):
            assets.setdefault(r["asset_id"], []).append(r)

    if args.list or not assets:
        for b, n in tally.items():
            print(f"  {b:14s} {n:3d}")
        print(f"  {'TOTAL':14s} {sum(tally.values()):3d} shortlist assets")
        if not args.list:
            print(f"\nnothing to render for batch '{args.batch}'")
        return 0

    if tally["unsorted"]:
        print(f"NOTE: {tally['unsorted']} shortlist asset(s) unclassified by the "
              f"canonical sheets -- see the 'unsorted' batch, they are not dropped")

    title = f"Teyvat Spire art picks — {BATCH_TITLES[args.batch]}"
    out = args.out or ROOT / "art" / (
        "contact_sheet.html" if args.batch == "all"
        else f"contact_sheet_{args.batch}.html")
    out.write_text(render(assets, title, BATCH_TITLES[args.batch]), encoding="utf-8")
    print(f"wrote {out} ({len(assets)} shortlist assets, batch '{args.batch}')")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
