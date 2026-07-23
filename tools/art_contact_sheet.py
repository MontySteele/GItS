#!/usr/bin/env python3
"""Emit art/contact_sheet.html — one page, all shortlist cards, 3 candidates
each, click to select (spec §2 step 5). "Export picks" downloads art/picks.tsv;
apply with:  python3 tools/art_process.py --apply-picks art/picks.tsv
Stdlib only. Images referenced relative to art/ (candidates/... , gitignored).
"""
import html
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from art_fetch import read_plan  # noqa: E402

OUT = ROOT / "art" / "contact_sheet.html"

rows = [r for r in read_plan() if r["pick"] == "shortlist"]
assets = OrderedDict()
for r in rows:
    assets.setdefault(r["asset_id"], []).append(r)

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

page = f"""<!doctype html><meta charset="utf-8"><title>Klee slice — art taste picks</title>
<style>
 body{{font:14px/1.4 -apple-system,sans-serif;margin:2em;background:#1b1b1f;color:#eee}}
 h2{{margin:1.2em 0 .3em;font-size:15px;color:#f8c471}}
 .row{{display:flex;gap:12px;flex-wrap:wrap}}
 .cand{{width:260px;cursor:pointer;text-align:center;color:#aaa}}
 .cand img{{width:250px;height:190px;object-fit:contain;background:#111;border:3px solid #333;border-radius:6px;display:block;margin:0 auto 4px}}
 .cand input{{display:none}}
 .cand:has(input:checked) img{{border-color:#e74c3c}}
 .cand.missing{{border:1px dashed #555;padding:8px;border-radius:6px}}
 #bar{{position:fixed;top:0;left:0;right:0;background:#111;padding:8px 2em;border-bottom:1px solid #333}}
 button{{background:#e74c3c;color:#fff;border:0;padding:6px 16px;border-radius:4px;font-size:14px;cursor:pointer}}
 main{{margin-top:3em}}
</style>
<div id="bar"><b>Klee slice taste picks</b> — {len(assets)} cards ·
<button onclick="exportPicks()">Export picks.tsv</button>
<span style="color:#888">then: python3 tools/art_process.py --apply-picks art/picks.tsv</span></div>
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
OUT.write_text(page)
print(f"wrote {OUT} ({len(assets)} shortlist assets)")
