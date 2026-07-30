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
import json
import mimetypes
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tier0.content import loader          # noqa: E402
from tier0.content import upgrades        # noqa: E402
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


MOD_CARDS_DIR = ROOT / "klee-mod" / "KleeCode" / "Cards"
# C# string literal, escapes included: "...\"..." stops at the real close quote.
_CS_STR = r'"((?:[^"\\]|\\.)*)"'
_LOC_RE = re.compile(r'\(\s*"(title|description)"\s*,\s*' + _CS_STR + r'\s*\)')
_PORTRAIT_RE = re.compile(r'CardPortrait\(\s*"([a-z0-9_]+)"\s*\)')


def _unescape_cs(s: str) -> str:
    return (s.replace('\\"', '"').replace("\\n", "\n")
             .replace("\\t", "\t").replace("\\\\", "\\"))


def _pascal(cid: str) -> str:
    return "".join(w.capitalize() for w in cid.split("_"))


def ingame_index(card_ids: set[str]) -> tuple[dict[str, dict], dict[str, str]]:
    """(card_id -> shipped {title, description, src}, card_id -> blocked reason).

    This reads the SHIPPED string out of the mod's `Localization` block. That
    is the opposite of the prose renderer `effect_lines` refuses to be: it
    invents nothing, and because the ops and the shipped text come from two
    independent producers (the sheet, and the generated C#), showing them in
    one tile makes sheet-vs-mod drift *visible*. A card whose ops say "deal 9"
    while the shipped text says "deal 6" is exactly the defect no lint sees.

    Absence is information too, so it is reported rather than blanked: a card
    the generator refused shows the manifest's `blocked` reason verbatim.
    """
    shipped: dict[str, dict] = {}
    if not MOD_CARDS_DIR.exists():
        return shipped, {}
    by_pascal = {_pascal(c): c for c in card_ids}

    for path in sorted(MOD_CARDS_DIR.rglob("*.cs")):
        src = path.read_text(encoding="utf-8", errors="replace")
        loc = dict(_LOC_RE.findall(src))
        if "description" not in loc and "title" not in loc:
            continue
        # Prefer the explicit id anchor the generator emits; fall back to the
        # filename convention. Anything that resolves to no sheet row is a
        # mod-only card and is left out (main() reports the count).
        m = _PORTRAIT_RE.search(src)
        cid = m.group(1) if m else None
        if cid not in card_ids:
            cid = by_pascal.get(path.stem)
        if not cid or cid not in card_ids:
            continue
        shipped[cid] = {
            "title": _unescape_cs(loc.get("title", "")),
            "description": _unescape_cs(loc.get("description", "")),
            "src": path.relative_to(ROOT).as_posix(),
        }

    blocked: dict[str, str] = {}
    for man in sorted(MOD_CARDS_DIR.glob("*/Generated/manifest.json")):
        data = json.loads(man.read_text(encoding="utf-8"))
        for cid, reason in (data.get("blocked") or {}).items():
            blocked[cid] = reason
    return shipped, blocked


# StS markup, shown rather than stripped -- [gold]x[/gold] is colour, and
# {IfUpgraded:show:A|B} is the upgrade branch. Rendering these legibly is
# formatting the shipped string, not rewriting it.
_TAG_RE = re.compile(r"\[(/?)(gold|b|i)\]")
_IFUPG_RE = re.compile(r"\{IfUpgraded:show:([^|}]*)\|([^}]*)\}")


def ingame_html(text: str) -> str:
    # Escape ONCE up front, then apply markup to the escaped text: none of the
    # markup delimiters ([] {} | :) are touched by html.escape, so they survive
    # intact and the substitutions below can safely emit tags.
    out = html.escape(text)

    def upg(m):
        alt, base = m.group(1).strip(), m.group(2).strip()
        return (f'{base}<span class="ifupg">&#8679; {alt}</span>'
                if alt else base)

    out = _IFUPG_RE.sub(upg, out)
    out = _TAG_RE.sub(
        lambda m: "</span>" if m.group(1) else f'<span class="kw {m.group(2)}">',
        out)
    return out.replace("\n", "<br>")


def _upgrade_error(exc: BaseException) -> str:
    """The visible marker that replaces a swallowed upgrade-render failure.

    Rendered rather than raised on purpose: one malformed `+` entry must not
    take the whole gallery down (the page's job is to show the set to a human,
    and 300 good tiles beat a traceback). But it must not be INVISIBLE either
    -- a blank where an upgrade line belongs reads as "this card has no
    upgrade", which is a different and false claim.
    """
    return ('<div class="upg-err">&#9888; upgrade render failed: '
            f'{html.escape(type(exc).__name__)}: {html.escape(str(exc))}'
            '</div>')


def tile(card, row, covered: bool, inline: bool, out_dir: Path,
         shipped: dict, blocked: dict) -> str:
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
    up_html, up = "", None
    # `except Exception: pass` used to wrap this whole block, which conflated
    # two facts a REVIEW surface must never conflate: "this card has no
    # upgrade" (ordinary -- basics, unexpressible deltas, UNAPPLIABLE) and
    # "rendering its upgrade THREW" (a defect). Both printed the same blank,
    # so a broken `+` entry under-reported as an unupgradeable one on the page
    # a human reads to decide what shipped. Absence stays silent; a throw now
    # prints an explicit marker.
    try:
        up = loader.get_card(card.id + upgrades.SUFFIX)
    except KeyError:
        pass                        # no such base card / no upgraded form
    except ValueError as exc:
        # apply_upgrade raises ValueError for BOTH "there is no upgrade here"
        # and "the delta is malformed". Only the first is a non-event.
        if "no applicable upgrade" not in str(exc):
            up_html = _upgrade_error(exc)
    except Exception as exc:        # noqa: BLE001 - report, never swallow
        up_html = _upgrade_error(exc)
    if up is not None:
        try:
            base_lines = set(effect_lines(card))
            changed = [l for l in effect_lines(up) if l not in base_lines]
            if str(up.cost) != str(card.cost):
                changed.insert(0, f"cost {card.cost} -> {up.cost}")
            if changed:
                up_html = ('<div class="upg">&#8679; ' +
                           " &middot; ".join(html.escape(l) for l in changed) +
                           "</div>")
        except Exception as exc:    # noqa: BLE001 - report, never swallow
            up_html = _upgrade_error(exc)
    ship = shipped.get(card.id)
    if ship and ship["description"]:
        ig_html = (f'<div class="ig-text">{ingame_html(ship["description"])}</div>'
                   f'<div class="ig-src">{html.escape(ship["src"])}</div>')
        ig_state = "shipped"
        # A shipped title that disagrees with the sheet name is drift worth
        # seeing, so it is called out rather than silently preferred.
        if ship["title"] and ship["title"] != card.name:
            ig_html = (f'<div class="ig-warn">shipped title: '
                       f'{html.escape(ship["title"])}</div>' + ig_html)
    elif card.id in blocked:
        ig_state = "blocked"
        ig_html = ('<div class="ig-none">not generated &mdash; '
                   f'{html.escape(blocked[card.id])}</div>')
    else:
        ig_state = "absent"
        ig_html = '<div class="ig-none">no shipped card in the mod</div>'

    tags = " ".join(card.archetypes + (["exhaust"] if card.exhaust else [])
                    + [card.type, card.rarity, card.character or ""])
    title = row["title"] if row else ""
    search = (card.id + " " + card.name + " " + tags + " "
              + (ship["description"] if ship else ""))
    return f"""
<div class="card" data-rarity="{html.escape(card.rarity)}" data-art="{state}"
     data-ingame="{ig_state}"
     data-search="{html.escape(search.lower())}">
  <div class="art">{art_html}</div>
  <div class="hd">
    <span class="cost">{html.escape(str(cost))}</span>
    <span class="name">{html.escape(card.name)}</span>
  </div>
  <div class="meta">{html.escape(card.id)} &middot; {html.escape(card.type)}
       &middot; <span class="rar">{html.escape(card.rarity)}</span></div>
  <div class="ops"><ul class="eff">{effs}</ul>{up_html}</div>
  <div class="ingame">{ig_html}</div>
  <div class="tags">{html.escape(tags)}</div>
  <div class="src">{html.escape(title)}</div>
</div>"""


CSS = """
.chips{margin:6px 0}.chip{background:#23252c;color:#cfd3da;border:1px solid #3a3d46;border-radius:12px;padding:2px 10px;margin:2px;cursor:pointer;font-size:12px}.chip:hover{background:#2f323b}.upg{color:#7fc97f;font-size:12px;margin:2px 8px 6px}
.upg-err{color:#f0a0a0;background:#3a1f1f;border-left:2px solid #d05a5a;font-size:12px;margin:2px 8px 6px;padding:3px 6px}
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

/* view toggle: ops (sheet) vs in-game (shipped C# Localization) */
.ingame{display:none}
body.view-ingame .ops{display:none}
body.view-ingame .ingame{display:block}
.ig-text{padding:7px 10px 0;font-size:12.5px;line-height:1.5}
.ig-src{padding:5px 10px 0;color:#4e535c;font-size:10px;font-family:ui-monospace,Consolas,monospace}
.ig-none{padding:7px 10px 0;color:#7a6b4a;font-size:11.5px;font-style:italic}
.card[data-ingame=blocked]{border-color:#6b5a2e}
.ig-warn{margin:6px 10px 0;padding:3px 6px;background:#3a2e1a;border-left:2px solid #d8b34a;color:#e0c583;font-size:11px}
.kw.gold{color:#d8b34a;font-weight:600}
.kw.b{font-weight:700}.kw.i{font-style:italic}
.ifupg{color:#7fc97f;margin-left:5px}
.tgl{background:#23252c;color:#cfd3da;border:1px solid #3a3d46;border-radius:5px;padding:5px 12px;cursor:pointer;font-size:12px;margin-left:8px}
.tgl:hover{background:#2f323b}
body.view-ingame .tgl{background:#2e4a2e;border-color:#4a6b4a;color:#cfe6cf}
"""

JS = """
// View toggle: ops (the sheet's raw effect dicts) vs in-game (the string the
// mod actually ships). The choice sticks across re-renders, because auditing
// a 457-card set means reloading this page a lot.
const TGL = document.getElementById('tgl');
function setView(ingame){
  document.body.classList.toggle('view-ingame', ingame);
  TGL.textContent = ingame ? 'showing: in-game text' : 'showing: op text';
  try { localStorage.setItem('gallery-view', ingame ? 'ingame' : 'ops'); } catch (e) {}
}
TGL.addEventListener('click', () =>
  setView(!document.body.classList.contains('view-ingame')));
let saved = null;
try { saved = localStorage.getItem('gallery-view'); } catch (e) {}
setView(saved === 'ingame');

document.addEventListener('click',e=>{if(e.target.classList.contains('chip')){const q=document.getElementById('q');q.value=q.value===e.target.dataset.q?'':e.target.dataset.q;q.dispatchEvent(new Event('input'));}});
document.getElementById('q').addEventListener('input', e => {
  const q = e.target.value.trim().toLowerCase();
  // `!rehunt` is the dashboard view: cards the art plan covers but that have
  // no effective pick. `!noart` widens it to unplanned cards too.
  // `!notext` is the same idea for shipped text: cards the mod has no
  // description for (blocked by the generator, or absent entirely).
  document.querySelectorAll('.card').forEach(c => {
    const hit = q === '!rehunt' ? c.dataset.art === 'rehunt'
              : q === '!noart'  ? c.dataset.art !== 'ok'
              : q === '!notext' ? c.dataset.ingame !== 'shipped'
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
    all_cards = loader._card_index().values()
    shipped, blocked = ingame_index({c.id for c in all_cards})
    cards = sorted(all_cards, key=lambda c: (c.character or "zz", c.id))
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
                               args.inline, out_dir, shipped, blocked)
                          for c in grp)
                + "</div></section>")

    facet_vals = []
    for attr in ("character", "type", "rarity"):
        facet_vals += sorted({getattr(c, attr, None) or "" for c in cards} - {""})
    facet_vals += sorted({a for c in cards for a in c.archetypes})
    chips = "".join(f'<button class="chip" data-q="{html.escape(v)}">'
                    f"{html.escape(v)}</button>" for v in dict.fromkeys(facet_vals))
    n_shipped = sum(1 for c in cards
                    if shipped.get(c.id, {}).get("description"))
    doc = f"""<!doctype html>
<meta charset="utf-8"><title>Teyvat Spire -- card gallery</title>
<style>{CSS}</style>
<h1>Teyvat Spire &mdash; card gallery</h1>
<div class="sub">{len(cards)} cards &middot;
 {len(cards) - len(rehunt) - len(unplanned)} with art &middot;
 <b style="color:#c86b6b">{len(rehunt)} rehunt</b> &middot;
 {len(unplanned)} not in the art plan &middot;
 {n_shipped} with in-game text &middot;
 <b style="color:#d8b34a">{len(cards) - n_shipped} without</b>
</div>
<div class="chips">{chips}</div>
<div class="sub"> filter: <input id="q"
   placeholder="id, name, archetype, !rehunt, !noart, !notext">
  <button class="tgl" id="tgl">showing: op text</button>
</div>
{''.join(body)}
<script>{JS}</script>
"""
    out_path.write_text(doc, encoding="utf-8")
    print(f"{out_path}  ({len(cards)} cards, {len(rehunt)} rehunt, "
          f"{len(unplanned)} unplanned, {n_shipped} with in-game text)")
    mod_only = sorted(set(shipped) - {c.id for c in cards})
    if mod_only and args.character == "all":
        print(f"mod-only (shipped C#, no sheet row): {', '.join(mod_only)}")
    if rehunt:
        print("REHUNT (planned, no effective pick): "
              + ", ".join(c.id for c in rehunt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
