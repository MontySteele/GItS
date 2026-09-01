# klee-upgrades.yaml - comment provenance

Long comment blocks that used to sit in `docs/klee-upgrades.yaml`. They
moved here on 2026-09-01 so an agent reading the sheet loads rows,
not prose. Blocks are verbatim and in sheet order.

A heading names the row the block was attached to. `before <id>`
means a column-0 section note that sat above that row. `header` is
the file header. Blocks of three lines or fewer stayed in the sheet.

## before big_badda_boom

```
# EB-118 Phase 2 (packet §4.3): the base card now prints Ethereal, and the upgrade
# BUYS THE DOWNSIDE OFF instead of bumping the number. `{damage: +4}` (16->20) is
# GONE, not kept beside it -- row 6 of the mined grammar is one upgrade axis per card,
# and a card whose base story is "strong, but it dies in your hand" upgrades by
# ending that story. Canon shape verbatim: Apparition, EchoForm and VoidForm each
# print Ethereal and each remove it on upgrade, changing nothing else.
# CONVENTION DIVERGENCE, DECLARED: row 4 puts keyword upgrades in "mid/rare
# territory" and our derived Commons rule says "exactly one number bump". This is a
# COMMON taking a keyword upgrade. It is ruled, not drifted -- the packet names the
# card, the phase and the shape -- and it is the same kind of exception R148 ruled
# for shared_billing's common cost reduction rather than grandfathering it.
```

## prune_witch_hunt

```
                                       # EB-219: WAS `{spark: +1}`, bumping the unconditional
                                       # `gain_spark` on her face. That op is gone (LAW:145 --
                                       # a Companion may not grant a signature resource), so the
                                       # delta has nowhere on the FACE to land and would raise in
                                       # upgrades.apply. `kit_spark` is the same +1 declared where
                                       # the grant now lives: Klee's kit reads the Companion's
                                       # upgraded flag and mints
                                       # KLEE_COMPANION_SPARK_UPGRADED_BONUS more. Expressed at
                                       # play time in BOTH engines, the `condition` key's shape --
                                       # the number is pinned to the constant by test, so the
                                       # sheet and the engine cannot drift. Swirl/fallback Block
                                       # stay fixed (personal pool).
```

## nicole_celestial_gift

```
                                        # The upgrade is COST, not magnitude, because the card's power is
                                        # already a ratchet: +1 Strength per turn compounds on its own, and
                                        # buying it a turn earlier is worth more than buying it bigger.
                                        # SUPERSEDES the interim G-C2 delta {buff: +2}, which existed only
                                        # to make the card upgradable at all after {block_per_turn: +2}
                                        # turned out to be unexpressible in both the sim and the codegen.
                                         # WAS {block_per_turn: +2} (4->6 block; lint-ok: 4->6 is the
                                         # superseded delta's arithmetic, not this row's), which was
                                         # UNEXPRESSIBLE in both layers: CELESTIAL_GIFT_BLOCK is a
                                         # tier0 constant and CompanionConstants.CelestialGiftBlock is
                                         # a C# const, so neither the sim nor the codegen could apply
                                         # it. The card was a dead campfire choice in the live build --
                                         # named by the 2026-07-25 playtest, and the reason
                                         # tools/lint_upgrade_coverage.py exists.
                                         # This moves the delta onto the half of the card that IS a
                                         # per-card field, which the `buff` grammar already binds to
                                         # the first top-level apply_power. Same upgrade budget, same
                                         # card identity (a buffer), zero new plumbing.
                                         # The higher-fidelity alternative -- make the block a card
                                         # field and thread it through effects.py, the upgrade
                                         # grammar, the generator and CelestialGiftPower -- is a real
                                         # four-layer change and is NOT conventional-delta work; it is
                                         # listed for [USER] at red-pen rather than taken here.
```
