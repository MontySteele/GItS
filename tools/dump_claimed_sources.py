#!/usr/bin/env python3
"""Dump the art source claim map -> docs/art-claimed-sources.tsv.

Round 3 proposed ten "locked" sources and seven were already the effective
pick of a shipped card, because the hunt had no way to see what was taken.
This is that way. Hunt collision-verified: diff every candidate against the
CLAIMED block before proposing it, and round 3's failure mode becomes
impossible rather than merely discouraged.

Regenerate after any plan.tsv change (it is a derived file, never hand-edit):

    python tools/dump_claimed_sources.py

Blocks:
  CLAIMED  effective card picks (auto, or shortlist rank 1, out under
           /cards/) as `wiki_title <TAB> card_id`. A title here is TAKEN;
           proposing it for a second card needs a red-pen ruling that
           displaces the incumbent.
  FREE     titles already fetched into art/raw but claimed by no card --
           dead shortlist ranks and non-card registers. Cheap candidates:
           the file is on disk already. `[non-card]` marks a title that IS
           an effective pick somewhere outside card space (a power icon, a
           splash); reusing those on a card is legal by construction
           (register-crossing) but worth naming out loud.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from art_fetch import read_plan          # noqa: E402

OUT = ROOT / "docs" / "art-claimed-sources.tsv"


def main() -> int:
    rows = read_plan()

    def effective(r):
        return r["pick"] == "auto" or r["rank"] == 1

    claimed = sorted(
        {(r["title"], r["asset_id"]) for r in rows
         if "/cards/" in r["out"] and effective(r)})
    claimed_titles = {t for t, _ in claimed}
    noncard = {r["title"] for r in rows
               if "/cards/" not in r["out"] and effective(r)}
    free = sorted({r["title"] for r in rows} - claimed_titles)

    lines = [
        "# DERIVED FILE -- regenerate with tools/dump_claimed_sources.py.",
        "# Diff every art candidate against the CLAIMED block before "
        "proposing it.",
        "# See the tool's docstring for what each block means.",
        f"# CLAIMED: {len(claimed)} effective card picks",
    ]
    lines += [f"{t}\t{cid}" for t, cid in claimed]
    lines += ["#",
              f"# FREE: {len(free)} fetched titles no card claims"]
    lines += [f"# {t}" + ("\t[non-card]" if t in noncard else "")
              for t in free]

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    dupes = len(claimed) - len(claimed_titles)
    print(f"{OUT}: {len(claimed)} claimed, {len(free)} free"
          + (f", {dupes} title(s) claimed twice (see art_lint L1)"
             if dupes else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
