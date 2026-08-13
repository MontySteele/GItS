#!/usr/bin/env python3
"""Parity lint: ONE Sly grammar, on both sides of the C# wall (EB-71, R174).

WHY THIS EXISTS. Sly was two near-identical mechanics wearing one word --
Kokomi's authored discard riders (`sly:`, an effect list) and the base game's
auto-play keyword (`sly_keyword:`, a boolean, plus Hand Trick's one-turn twin
`sly_this_turn:`). R174 unified them: `sly:` is the one field, and the keyword
is the RESERVED rider `{op: sly_autoplay}` inside it. The sim leg landed
2026-08-12 and `state.RETIRED_CARD_FIELDS` makes a stale sheet row fail by
name -- but only for rows the tier0 loader ever sees.

The codegen path does not go through that loader. `tools/gen_klee_cards.py`
reads the yaml sheet DIRECTLY, and until the C# leg it read a row's `sly:`
list verbatim as an effect list. Under the new grammar that is a live hazard
in two directions:

  * a sheet row printing the reserved marker would have handed
    `{op: sly_autoplay}` to the effect emitter, which prices it as an unknown
    op and blocks -- or, on the day somebody widens the op set, emits a body
    for a keyword the GAME already implements, resolving it twice.
  * a row keeping the retired spelling would be read as inert metadata by
    everything on this side of the wall and silently drop the mechanic from
    the mod while the sim still refuses the row. Divergence, not a crash.

So: the retired spellings must not reappear anywhere, and the reserved marker
must be handled as a KEYWORD by every sheet-side reader rather than as an
effect. This lint is the standing guard for both, in the shape
`lint_op_parity` / `lint_enchant_parity` use -- findings on stdout, exit 1.

Run: python tools/lint_sly_grammar.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools import effect_walk                          # noqa: E402
from tools import gen_klee_cards as gen                # noqa: E402

# The spellings R174 retired, as a card FIELD. `sly_this_turn` needs the
# lookbehind because the live op `grant_sly_this_turn` -- Hand Trick's verb,
# still registered and still priced -- contains it as a substring; the op
# kept its name because the name is what the card does, and only the storage
# changed.
RETIRED_PATTERNS = {
    "sly_keyword": re.compile(r"\bsly_keyword\b"),
    "sly_this_turn": re.compile(r"(?<!grant_)\bsly_this_turn\b"),
}

# A PROSE citation of a dead spelling is how this repo routes the next
# author -- "`until: turn_end`, not a separate `sly_this_turn` boolean" is
# the comment that stops the mistake, and a lint that deleted it would be
# eating its own documentation. Backticks are the tell: source code never
# wraps an identifier in them, so a backticked mention is a comment about the
# migration and an un-backticked one is a live read.
BACKTICKED = re.compile(r"`[^`\n]*`")

# Files permitted to NAME a retired spelling UN-backticked, each because
# naming it is the point. Anything else that mentions one is either a
# consumer that never migrated or a new author copying a dead example --
# both are findings.
ALLOWED_TO_NAME = {
    # The retirement registry itself, plus the field comments that route an
    # author from the dead spelling to the live one.
    "tier0/engine/state.py",
    # The migration's own pins.
    "tier0/tests/test_eb71_sly_unification.py",
    "tier0/tests/test_extract_base_game_pool.py",
    "tier0/tests/test_eb71_cs_parity.py",
    # The extractor's comment explaining what CardKeyword.Sly used to map to.
    "tools/extract_base_game_pool.py",
    # This lint.
    "tools/lint_sly_grammar.py",
}

# Where a retired spelling would still do damage: executable surface only.
# Register prose and archived logs describe the migration and are not scanned
# -- a lint that fought the history would be asking the docs to lie.
SCAN_ROOTS = (
    ("tier0", "*.py"),
    ("tier05", "*.py"),
    ("tools", "*.py"),
    ("understudy", "*.py"),
    ("klee-mod", "*.cs"),
)

# Sheets the codegen path reads directly.
SHEETS = tuple(sorted((REPO / "docs").glob("*-cards.yaml"))) + tuple(
    sorted((REPO / "docs").glob("*-companions.yaml")))


def _rows(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if isinstance(data, dict):
        data = data.get("cards", data.get("companions", []))
    return [r for r in (data or []) if isinstance(r, dict)]


def _retired_spellings() -> list[str]:
    """No executable file may name a retired Sly field again."""
    out: list[str] = []
    for root, glob in SCAN_ROOTS:
        base = REPO / root
        if not base.is_dir():
            continue
        for path in sorted(base.rglob(glob)):
            rel = path.relative_to(REPO).as_posix()
            if rel in ALLOWED_TO_NAME:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            lines = [BACKTICKED.sub("``", ln) for ln in text.splitlines()]
            for name, pattern in RETIRED_PATTERNS.items():
                hit = next((i for i, ln in enumerate(lines, 1)
                            if pattern.search(ln)), 0)
                if hit:
                    line = hit
                    out.append(
                        f"RETIRED SLY FIELD: {rel}:{line} names {name!r}. "
                        f"EB-71 (R174) unified the two Sly mechanics on the "
                        f"one `sly:` effect list; the base-game keyword is "
                        f"the reserved rider [{{op: "
                        f"{effect_walk.SLY_AUTOPLAY_OP}}}]. Reading or "
                        f"emitting the old spelling puts the mod and the sim "
                        f"on different mechanics.")
    return out


def _sheet_shapes() -> list[str]:
    """Every committed sheet row speaks the unified grammar."""
    out: list[str] = []
    for sheet in SHEETS:
        rel = sheet.relative_to(REPO).as_posix()
        for row in _rows(sheet):
            cid = row.get("id", "<unnamed>")
            for name in RETIRED_PATTERNS:
                if name in row:
                    out.append(
                        f"RETIRED SLY FIELD: {rel} row {cid!r} prints "
                        f"{name!r}. Rewrite as `sly: [{{op: "
                        f"{effect_walk.SLY_AUTOPLAY_OP}}}]`; an EXTRACTED "
                        f"sheet is re-emitted by "
                        f"tools/extract_base_game_pool.py instead.")
            if "sly" not in row:
                continue
            sly = row.get("sly")
            if not isinstance(sly, list):
                out.append(
                    f"SLY SHAPE: {rel} row {cid!r} has `sly: {sly!r}`. Since "
                    f"R174 `sly:` is an EFFECT LIST, never a boolean.")
                continue
            reason = gen._sly_marker_reason(row)
            if reason:
                out.append(f"SLY SHAPE: {rel} row {cid!r}: {reason}")
    return out


def _codegen_handles_the_marker() -> list[str]:
    """The generator treats the reserved marker as a KEYWORD, not an effect.

    Proven by construction rather than by reading the source: a synthetic row
    carrying the marker is pushed through `gen.emit` and the output must put
    `CardKeyword.Sly` on the CanonicalKeywords rail and emit no discard hook
    for it. That is the check that would have caught the pre-EB-71 generator,
    which had no opinion about the marker at all.

    NOT vacuous even though no committed sheet prints the marker today --
    that is exactly the state this guard exists to survive.
    """
    out: list[str] = []
    base = {"id": "lint_sly_probe", "name": "Lint Sly Probe", "cost": 1,
            "type": "skill", "rarity": "common",
            "effects": [{"op": "block", "amount": 5}]}

    marker = {**base, "sly": [{"op": effect_walk.SLY_AUTOPLAY_OP}]}
    reason = gen.blocked_reason(marker, gen.KOKOMI_PROFILE)
    if reason:
        out.append(
            f"CODEGEN: a card printing the reserved "
            f"{effect_walk.SLY_AUTOPLAY_OP} rider BLOCKS ({reason}). The "
            f"marker is the base-game keyword and has a rail: "
            f"CanonicalKeywords, beside Exhaust/Innate/Retain.")
    else:
        cs = gen.emit(marker, gen.KOKOMI_PROFILE)
        if "CardKeyword.Sly" not in cs:
            out.append(
                "CODEGEN: the reserved rider did not emit CardKeyword.Sly. "
                "The mod would ship a card the sim auto-plays on discard and "
                "the game does not.")
        if "AfterCardDiscarded" in cs:
            out.append(
                "CODEGEN: the reserved rider emitted an AfterCardDiscarded "
                "hook. The GAME owns the auto-play once the keyword is on "
                "the card; a hook beside it resolves the discard twice.")
        if effect_walk.SLY_AUTOPLAY_OP in cs:
            out.append(
                f"CODEGEN: {effect_walk.SLY_AUTOPLAY_OP!r} reached the "
                f"emitted C#. It is a marker for the keyword, never a name "
                f"the mod should see.")

    # And the riders beside it still emit, or Kokomi's Assist lane would
    # quietly vanish from any card that also printed the keyword.
    both = {**base, "sly": [{"op": effect_walk.SLY_AUTOPLAY_OP},
                            {"op": "draw", "amount": 1}]}
    if not gen.blocked_reason(both, gen.KOKOMI_PROFILE):
        cs = gen.emit(both, gen.KOKOMI_PROFILE)
        if "AfterCardDiscarded" not in cs or "CardKeyword.Sly" not in cs:
            out.append(
                "CODEGEN: a card carrying BOTH the keyword and an authored "
                "rider must emit both the keyword and the discard hook.")
    return out


def _generated_csharp() -> list[str]:
    """No emitted C# names a sim-side marker or a retired field."""
    out: list[str] = []
    for path in sorted((REPO / "klee-mod").rglob("*.cs")):
        rel = path.relative_to(REPO).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if effect_walk.SLY_AUTOPLAY_OP in text:
            out.append(
                f"EMITTED MARKER: {rel} contains "
                f"{effect_walk.SLY_AUTOPLAY_OP!r}. The reserved rider is a "
                f"tier0 marker for the base-game keyword; the mod expresses "
                f"it as CardKeyword.Sly and nothing else.")
    return out


def findings() -> list[str]:
    return (_retired_spellings() + _sheet_shapes()
            + _codegen_handles_the_marker() + _generated_csharp())


def main() -> int:
    bad = findings()
    for line in bad:
        print(line)
    if bad:
        print(f"\n{len(bad)} finding(s). One Sly, one field, one word "
              f"(EB-71, R174) -- on both sides of the C# wall.")
        return 1
    print(f"sly grammar OK: {len(SHEETS)} sheets speak the unified list, "
          f"no retired spelling in executable source, and the generator "
          f"emits the reserved rider as CardKeyword.Sly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
