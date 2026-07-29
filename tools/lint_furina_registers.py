#!/usr/bin/env python3
"""Register lint for the Furina pool (Curtain Call sweep, R85 / sprint §3+§5E).

The register convention (RATIFIED 2026-07-27, binding on this and future
passes) sorts every Furina card name into one of three voices:

  salon    Furina the vision-holder: theatre director and actress-by-craft;
           her cast, stagecraft vocabulary, the post-truth professional.
  archon   Furina-as-Archon: life itself as the act -- the 500-year
           performance, the decaying mask, the audience of a nation, the
           trial as the act's public climax. Focalors lives here.
  private  the life the audience never sees: backstage reserves, sweets,
           breath, the self offstage.

What is MECHANICALLY lintable is the same-resource-same-register grammar
(the same-action-same-nation precedent applied to naming). The rules below
are the enforceable formalization ratified with the sweep; the SEMANTIC half
of the convention (does this name read in this voice?) is [USER]'s eyes-on
name audit, by house law, and no tool pretends to cover it.

  R1  every Furina card carries register: salon | archon | private.
  R2  any card that touches Fanfare (a bonus_formula reading fanfare, a
      fanfare_at_least_* gate, or either keyword op -- gain_fanfare_floor
      "Fanfare +X" / raise_fanfare_cap "Fanfare Cap +X") is register: archon.
      Fanfare IS the mask/audience stat; a stagehand name on a Fanfare read
      is the register scramble this sweep exists to remove.
      raise_fanfare_cap joined this rule with the Fanfare rework (Track B,
      2026-07-28), and it is the rule that DECIDED which cards carry the new
      keywords: the cap only ever binds for a deck pushing the meter high,
      which is the fanfare plan, which is the archon voice. The convention
      and the mechanic point the same way, so no amendment was needed.
  R3  any card that APPLIES salon_member (deploys a cast member) is
      register: salon. Reads (has_salon_members and count scalers) are not
      deploys and carry no constraint -- Dinner Service feeding the
      household offstage is correctly private.
  R4  a PURE Encore card (every leaf op is gain_encore/spend_encore) is
      register: private -- the buffer is the self rebuilt offstage --
      UNLESS the card carries the focalors flavor tag (her final mercy is
      the Archon's, ratified placement).
  R5  the Focalors cap: EXACTLY two cards carry the focalors tag, and both
      are rare (ruling 2026-07-27: the_sea_is_my_stage + reginas_mercy; no
      third Focalors reference anywhere in the pool).
  L12 NO DIRECT TRANSIENT FANFARE GRANT, on the sheet or in the engine.
      Required by the Fanfare rework brief (Track B, 2026-07-28) and the
      reason it is a BLOCKER rather than a warning: the "Fanfare +X" keyword
      can only mean the permanent grant while every generation source is
      INDIRECT (hp_lost, encore_spent, encore_absorbed, center_stage --
      things the player DOES, which then pay). The first card that hands out
      transient Fanfare outright makes the keyword mean two things, on faces
      already printed, forever. Checked on BOTH surfaces: a banned op on a
      sheet row, and a banned op existing in effects.OPS at all -- because a
      sheet lint alone would pass right up until someone wrote the card.
  R6  the "Fanfare +X" keyword (gain_fanfare_floor) is a RARE POWER payoff.
      The cheap half of the pair ("Fanfare Cap +X") is what commons,
      uncommons and Exhaust skills may print. Ruled with the rework; before
      it, every Power got a floor grant by rarity and no card said so.

Third-instance rule stands: if a second character adopts registers, this
generalizes into a shared lint with a per-character vocabulary table.

Exit 0 clean; exit 1 with one line per violation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SHEET = REPO / "docs" / "furina-cards.yaml"
REGISTERS = ("salon", "archon", "private")


def _leaf_ops(effects: list[dict]):
    for fx in effects or ():
        yield fx
        for branch in ("then", "else"):
            if fx.get(branch):
                yield from _leaf_ops(fx[branch])


# The two printed keywords (Track B). Both are Fanfare-touching for R2.
KEYWORD_OPS = ("gain_fanfare_floor", "raise_fanfare_cap")

# L12. Ops that would hand the player TRANSIENT Fanfare directly. None of
# these exists today and none may be added; the names are the plausible
# spellings someone would reach for, so the lint fires on the attempt rather
# than on the consequence three passes later.
BANNED_TRANSIENT_OPS = ("gain_fanfare", "add_fanfare", "grant_fanfare",
                        "fanfare", "give_fanfare")


def _touches_fanfare(card: dict) -> bool:
    for fx in _leaf_ops(card.get("effects")):
        if fx.get("op") in KEYWORD_OPS:
            return True
        if "fanfare" in str(fx.get("bonus_formula", "")):
            return True
        if str(fx.get("if", "")).startswith("fanfare_at_least_"):
            return True
    return False


def _grants_fanfare_floor(card: dict) -> bool:
    return any(fx.get("op") == "gain_fanfare_floor"
               for fx in _leaf_ops(card.get("effects")))


def _applies_member(card: dict) -> bool:
    return any(fx.get("op") == "apply_power"
               and fx.get("power") == "salon_member"
               for fx in _leaf_ops(card.get("effects")))


def _pure_encore(card: dict) -> bool:
    ops = [fx.get("op") for fx in _leaf_ops(card.get("effects"))
           if fx.get("op") != "conditional"]
    return bool(ops) and all(op in ("gain_encore", "spend_encore")
                             for op in ops)


def main() -> int:
    cards = yaml.safe_load(SHEET.read_text())
    errors: list[str] = []
    focalors: list[dict] = []
    census = {r: 0 for r in REGISTERS}

    for c in cards:
        cid, reg = c["id"], c.get("register")
        if reg not in REGISTERS:
            errors.append(f"R1 {cid}: register {reg!r} not in {REGISTERS}")
            continue
        census[reg] += 1
        if _touches_fanfare(c) and reg != "archon":
            errors.append(f"R2 {cid}: touches Fanfare but register={reg}")
        elif _applies_member(c) and reg != "salon":
            errors.append(f"R3 {cid}: deploys salon_member but register={reg}")
        if (_pure_encore(c) and reg != "private"
                and "focalors" not in (c.get("tags") or ())):
            errors.append(f"R4 {cid}: pure-Encore card but register={reg}")
        if "focalors" in (c.get("tags") or ()):
            focalors.append(c)
        for fx in _leaf_ops(c.get("effects")):
            if fx.get("op") in BANNED_TRANSIENT_OPS:
                errors.append(
                    f"L12 {cid}: op {fx['op']!r} would grant TRANSIENT "
                    "Fanfare directly. Every generation source must stay "
                    "indirect or the printed 'Fanfare +X' keyword becomes "
                    "ambiguous on faces already shipped")
        if _grants_fanfare_floor(c) and not (
                c.get("type") == "power" and c.get("rarity") == "rare"):
            errors.append(
                f"R6 {cid}: prints 'Fanfare +X' (gain_fanfare_floor) but is "
                f"a {c.get('rarity')} {c.get('type')}. The full grant is a "
                "RARE POWER payoff; commons, uncommons and Exhaust skills "
                "print 'Fanfare Cap +X' instead")

    # L12, the ENGINE half. The sheet half above can only catch a card that
    # was written; this catches the op being made available at all, which is
    # the step that actually opens the door.
    #
    # THE REPO ROOT IS PUSHED ONTO sys.path EXPLICITLY. This was first written
    # as a bare try/except ImportError with a `pass` fallback, "so the lint
    # keeps working as a standalone yaml checker" -- and the mutation test
    # caught what that actually did: run as `python tools/lint_...py`, sys.path
    # starts at tools/, `tier0` is not importable, and the except branch
    # silently switched off half the gate in the exact way the lint is
    # normally invoked. A planted `gain_fanfare` op passed clean.
    #
    # So: fix the path, and let an ImportError RAISE. A lint that cannot see
    # the thing it lints must fail loudly, not report zero violations. This is
    # the same class of defect the L12 rule itself exists to prevent -- a gap
    # that is invisible precisely because nothing complains.
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from tier0.engine import effects

    for op in BANNED_TRANSIENT_OPS:
        if op in effects.OPS:
            errors.append(
                f"L12 engine: effects.OPS exposes {op!r}. No op may hand "
                "out transient Fanfare directly -- generation stays "
                "indirect so 'Fanfare +X' keeps one meaning")

    if len(focalors) != 2:
        errors.append(f"R5 focalors cap: {len(focalors)} tagged, need exactly 2"
                      f" ({[c['id'] for c in focalors]})")
    for c in focalors:
        if c.get("rarity") != "rare":
            errors.append(f"R5 {c['id']}: focalors tag on rarity "
                          f"{c.get('rarity')!r}, cap slots are rare")

    total = sum(census.values())
    print(f"furina register census: {total} cards -- "
          + " ".join(f"{r} {n}" for r, n in census.items())
          + f" | focalors {len(focalors)}")
    for e in errors:
        print(f"  REGISTER LINT: {e}")
    print(f"{len(errors)} register violations")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
