#!/usr/bin/env python3
"""Render every card -- numbers AND art -- into one self-contained HTML page.

Why: the sheets are the source of truth for numbers and art/plan.tsv is the
source of truth for pictures, and until now nothing put the two in front of
one pair of eyes at once. Design drift (a card whose art says "sleepy nap"
over an effect that says "deal 24 damage") is exactly the class of defect no
lint can see -- it needs a human looking at the set as a set. This is the
instrument for that look.

It doubles as the REHUNT DASHBOARD. A card whose art/plan.tsv row has no
effective pick (or whose rendered file is absent) shows a MISSING ART tile,
so the rehunt pile is a thing you can see rather than a list you maintain.

Read-only. Never writes into ImageGen/ or docs/; emits one .html (gitignored)
and nothing else.

  python tools/render_card_gallery.py                 # -> card_gallery.html
  python tools/render_card_gallery.py --inline        # embed art as data: URIs
  python tools/render_card_gallery.py -o /tmp/x.html

`--inline` makes the file portable at the cost of size (~90 PNGs); the
default links art by relative path, which is correct when the page is opened
from the repo root and is what you want while iterating.
"""
import argparse
import base64
import html
import mimetypes
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tier0.content import loader          # noqa: E402
from art_fetch import read_plan           # noqa: E402

RARITY_ORDER = ["basic", "common", "uncommon", "rare"]
RARITY_COLOR = {"basic": "#8a8a8a", "common": "#c9c9c9",
                "uncommon": "#6fb1d6", "rare": "#d8b34a"}


def art_index() -> tuple[dict[str, dict], set[str]]:
    """(card_id -> EFFECTIVE plan row, set of card_ids the plan covers at all).

    Joins on the `out` path, not wiki_title: `out` is what the pipeline
    actually writes, so a card whose art was re-pointed still resolves, and
    two cards sharing a source (legal across registers) don't collide here.

    The second return value is what makes the dashboard mean something. Three
    states, not two:
      HAS ART   -- effective row, file on disk
      REHUNT    -- the plan covers this card but no row is effective (which is
                   how plan.tsv spells "yielded its source", e.g. pop after
                   the 2026-07-21 Kaboom Box flip), or the file is absent
      unplanned -- no plan row at all; Furina's 91 cards are here, and calling
                   those "missing art" buries the 10-card rehunt pile in noise
    """
    eff, covered = {}, set()
    for r in read_plan():
        if "/cards/" not in r["out"]:
            continue
        covered.add(Path(r["out"]).stem)
        if r["pick"] == "auto" or r["rank"] == 1:
            eff[Path(r["out"]).stem] = r
    return eff, covered


def effect_lines(card) -> list[str]:
    """Compact one-line-per-op rendering of the raw effect dicts.

    Deliberately NOT prose. There is no effect-text renderer in the repo, and
    inventing one here would put a second, unverified description of every
    card next to the sheet -- a drift source, not a drift detector. The ops
    are shown as they are written so the page can never disagree with the
    sheet it is displaying.
    """
    lines = []
    for e in card.effects:
        op = e.get("op", "?")
        rest = " ".join(f"{k}={v}" for k, v in e.items() if k != "op")
        lines.append(f"{op} {rest}".strip())
    return lines


def tile(card, row, covered: bool, inline: bool, out_dir: Path) -> str:
    state = "rehunt" if covered else "unplanned"
    art_html = (f'<div class="noart {state}">'
                f'{"REHUNT -- NO ART" if covered else "not in art plan"}</div>')
    if row:
        src_path = ROOT / row["out"]
        if src_path.exists():
            state = "ok"
            if inline:
                mime = mimetypes.guess_type(src_path.name)[0] or "image/png"
                b64 = base64.b64encode(src_path.read_bytes()).decode()
                src = f"data:{mime};base64,{b64}"
            else:
                # relative to the HTML file, so the page works from anywhere
                # it is written as long as the repo is intact.
                src = Path(row["out"]).as_posix()
                try:
                    src = Path(
                        __import__("os").path.relpath(src_path, out_dir)
                    ).as_posix()
                except ValueError:      # different drive on Windows
                    src = src_path.as_uri()
            art_html = f'<img loading="lazy" src="{html.escape(src)}" alt="">'

    cost = "X" if card.cost == "X" else card.cost
    effs = "".join(f"<li>{html.escape(l)}</li>" for l in effect_lines(card))
    tags = " ".join(card.archetypes + (["exhaust"] if card.exhaust else []))
    title = row["title"] if row else ""
    return f"""
<div class="card" data-rarity="{html.escape(card.rarity)}" data-art="{state}"
     data-search="{html.escape((card.id + ' ' + card.name + ' ' + tags).lower())}">
  <div class="art">{art_html}</div>
  <div class="hd">
    <span class="cost">{html.escape(str(cost))}</span>
    <span class="name">{html.escape(card.name)}</span>
  </div>
  <div class="meta">{html.escape(card.id)} &middot; {html.escape(card.type)}
       &middot; <span class="rar">{html.escape(card.rarity)}</span></div>
  <ul class="eff">{effs}</ul>
  <div class="tags">{html.escape(tags)}</div>
  <div class="src">{html.escape(title)}</div>
</div>"""


CSS = """
:root{color-scheme:dark}
body{background:#15161a;color:#e6e6e6;font:13px/1.45 system-ui,sans-serif;margin:0;padding:20px}
h1{font-size:20px;margin:0 0 4px}
h2{font-size:15px;margin:26px 0 10px;border-bottom:1px solid #333;padding-bottom:4px}
.sub{color:#8b8b8b;margin-bottom:14px}
#q{background:#22242a;border:1px solid #3a3d45;color:#e6e6e6;padding:6px 10px;
   border-radius:5px;width:260px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.card{background:#1d1f25;border:1px solid #2e313a;border-radius:8px;overflow:hidden;
      display:flex;flex-direction:column}
.card[data-art=rehunt]{border-color:#7a3b3b}
.noart.rehunt{color:#c86b6b}
.noart.unplanned{color:#4e535c;letter-spacing:0;font-weight:400}
.art{aspect-ratio:500/380;background:#111;display:flex;align-items:center;justify-content:center}
.art img{width:100%;height:100%;object-fit:cover;display:block}
.noart{color:#c86b6b;font-size:11px;letter-spacing:.09em;font-weight:600}
.hd{display:flex;gap:8px;align-items:baseline;padding:8px 10px 2px}
.cost{background:#3a3d45;border-radius:4px;padding:0 6px;font-weight:700}
.name{font-weight:600}
.meta{padding:0 10px;color:#8b8b8b;font-size:11px}
.eff{margin:7px 0 0;padding:0 10px 0 24px;font-family:ui-monospace,Consolas,monospace;font-size:11px}
.eff li{margin-bottom:2px;word-break:break-word}
.tags{padding:6px 10px 0;color:#6f7580;font-size:11px}
.src{padding:2px 10px 9px;color:#4e535c;font-size:10px;margin-top:auto}
"""

JS = """
document.getElementById('q').addEventListener('input', e => {
  const q = e.target.value.trim().toLowerCase();
  // `!rehunt` is the dashboard view: cards the art plan covers but that have
  // no effective pick. `!noart` widens it to unplanned cards too.
  document.querySelectorAll('.card').forEach(c => {
    const hit = q === '!rehunt' ? c.dataset.art === 'rehunt'
              : q === '!noart'  ? c.dataset.art !== 'ok'
              : !q || c.dataset.search.includes(q);
    c.style.display = hit ? '' : 'none';
  });
  document.querySelectorAll('section').forEach(s => {
    s.style.display = s.querySelectorAll('.card:not([style*="none"])').length
                      ? '' : 'none';
  });
});
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=str(ROOT / "card_gallery.html"))
    ap.add_argument("--inline", action="store_true",
                    help="embed art as data: URIs (portable, much larger)")
    ap.add_argument("--character", default="all",
                    help="filter to one character id, or 'all' (default)")
    args = ap.parse_args()
    out_path = Path(args.out).resolve()
    out_dir = out_path.parent

    art, covered = art_index()
    cards = sorted(loader._card_index().values(),
                   key=lambda c: (c.character or "zz", c.id))
    if args.character != "all":
        cards = [c for c in cards if c.character == args.character]
        if not cards:
            sys.exit(f"no cards for character {args.character!r}")

    groups: dict[tuple, list] = {}
    for c in cards:
        groups.setdefault((c.character or "(no character)", c.rarity), []).append(c)

    def has_art(c):
        return c.id in art and (ROOT / art[c.id]["out"]).exists()

    rehunt = [c for c in cards if not has_art(c) and c.id in covered]
    unplanned = [c for c in cards if not has_art(c) and c.id not in covered]

    body = []
    for char in sorted({k[0] for k in groups}):
        for rar in RARITY_ORDER + sorted({k[1] for k in groups
                                          if k[1] not in RARITY_ORDER}):
            grp = groups.get((char, rar))
            if not grp:
                continue
            body.append(
                f'<section><h2 style="color:{RARITY_COLOR.get(rar, "#ccc")}">'
                f'{html.escape(char)} &middot; {html.escape(rar)} '
                f'<span style="color:#6f7580">({len(grp)})</span></h2>'
                '<div class="grid">'
                + "".join(tile(c, art.get(c.id), c.id in covered,
                               args.inline, out_dir) for c in grp)
                + "</div></section>")

    doc = f"""<!doctype html>
<meta charset="utf-8"><title>Teyvat Spire -- card gallery</title>
<style>{CSS}</style>
<h1>Teyvat Spire &mdash; card gallery</h1>
<div class="sub">{len(cards)} cards &middot;
 {len(cards) - len(rehunt) - len(unplanned)} with art &middot;
 <b style="color:#c86b6b">{len(rehunt)} rehunt</b> &middot;
 {len(unplanned)} not in the art plan
 &nbsp;|&nbsp; filter: <input id="q"
   placeholder="id, name, archetype, !rehunt, !noart">
</div>
{''.join(body)}
<script>{JS}</script>
"""
    out_path.write_text(doc, encoding="utf-8")
    print(f"{out_path}  ({len(cards)} cards, {len(rehunt)} rehunt, "
          f"{len(unplanned)} unplanned)")
    if rehunt:
        print("REHUNT (planned, no effective pick): "
              + ", ".join(c.id for c in rehunt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
