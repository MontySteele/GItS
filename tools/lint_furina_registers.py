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
  R2  RETIRED 2026-10-19 with the shipped Fanfare meter it read. It said a
      card that READS Fanfare (a `N_per_M_fanfare` rider, a
      `fanfare_at_least_*` gate or the `gain_fanfare_floor` grant) is
      register: archon; none of those spellings exists in the engine now.
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
  R6, R7 and L12 RETIRED: R7 on 2026-08-24 (EB-118 sec.5.2), R6 (the
      "Fanfare +X" grant is a rare Power) and L12 (no direct transient
      Fanfare grant) on 2026-10-19, with the shipped meter they guarded.
      The Stage's own `furina` kind `gain_fanfare` is a different Fanfare.

Third-instance rule stands: if a second character adopts registers, this
generalizes into a shared lint with a per-character vocabulary table.

Exit 0 clean; exit 1 with one line per violation.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools.effect_walk import iter_effects as _leaf_ops  # noqa: E402

# Her own rows on the prototype surface (`proto_fs_`) since legacy cleanup
# stage 6 deleted `docs/furina-cards.yaml`; the Fontaine companion rows that
# name her as owner are Universals, not her personal pool.
SHEET = REPO / "docs" / "prototype-surface.yaml"
OWN_PREFIX = "proto_fs_"
REGISTERS = ("salon", "archon", "private")


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
    cards = [c for c in yaml.safe_load(SHEET.read_text(encoding="utf-8"))
             if isinstance(c, dict) and str(c.get("id", "")).startswith(OWN_PREFIX)]
    errors: list[str] = []
    focalors: list[dict] = []
    census = {r: 0 for r in REGISTERS}

    for c in cards:
        cid, reg = c["id"], c.get("register")
        if reg not in REGISTERS:
            errors.append(f"R1 {cid}: register {reg!r} not in {REGISTERS}")
            continue
        census[reg] += 1
        if _applies_member(c) and reg != "salon":
            errors.append(f"R3 {cid}: deploys salon_member but register={reg}")
        if (_pure_encore(c) and reg != "private"
                and "focalors" not in (c.get("tags") or ())):
            errors.append(f"R4 {cid}: pure-Encore card but register={reg}")
        if "focalors" in (c.get("tags") or ()):
            focalors.append(c)

    # R5 was "exactly 2" on the shipped sheet, whose two Focalors rares were
    # ruled; the Stage's rows tag none yet (legacy cleanup stage 6), so the
    # cap is enforced as a ceiling until a pass places the flavor again.
    if len(focalors) > 2:
        errors.append(f"R5 focalors cap: {len(focalors)} tagged, at most 2"
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
