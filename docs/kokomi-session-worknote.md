# Worknote — Kokomi kickoff session (Code workstream)

**Date:** 2026-07-23. This is the CROSS-SESSION NOTE required by the
standing rule (DECISIONS ~431 / R20 lineage: changes to shared loaders and
shared schema land only after this note exists). Written BEFORE the changes
land. Owner: Kokomi kickoff session. Governing doc:
docs/kokomi-kickoff-v1.md; response doc: docs/kokomi-roster-v0.1-report.md.

## Shared-schema / shared-loader changes this session lands

1. **`Card` dataclass (tier0/engine/state.py) gains two fields**, both
   inert-by-default so every existing sheet row and every constructed test
   card is byte-identical in behavior:
   - `conscripted: bool = False` — combat-local provenance stamped by the
     new `conscript` op (mirrors `generated_by_guest_star`). Read by the
     SUPPORT_CARRY / control-provenance path (kickoff ask §6.7,
     implemented as PROPOSED).
   - `sly: list[dict] = []` — effects that fire when the card is discarded
     BY A CARD EFFECT (StS2 Silent keyword, Kokomi Assist lane). End-of-turn
     hand flush does NOT trigger Sly; draw-pile discards (scry) do NOT
     trigger Sly. Both scopings are loud comments at the trigger site.
2. **`Player` gains `charge: int = 0`** — Kokomi's uncapped meter. Reset in
   `run_fight` alongside encore/fanfare. Dead field for everyone else.
3. **`DOCS_CARD_SHEETS` (tier0/content/loader.py) grows two sheets**:
   `kokomi-cards.yaml`, `inazuma-companions.yaml`. Nation derives from the
   companion filename (existing rule); `character` derives from id prefix /
   filename (existing rule). New loader helper `companion_pool(nation)` for
   the conscript op's generation pool.
4. **New ops (tier0/engine/effects.py)**: `gain_charge`, `conscript`
   (transform-in-hand → random same-nation companion, cost −1, gains
   Exhaust; `mode: create` variant creates instead of transforming —
   Uncommon+ only per the Kokomi deck-size law). `_bonus_formula` learns
   `N_per_M_charge`. `_op_discard` now resolves `sly` effect lists after a
   card-effect discard (no existing card carries one → dead branch).
5. **New power semantics**: `ceremonial_garment` added to `powers.DECAYING`
   (stacks = turns remaining). `prevent_exhaust_ward` read by a new guarded
   branch in `combat._enemy_turn` (first unblocked hit per player-turn:
   prevent up to stacks, exhaust a random draw-pile card through the
   `refpowers.exhaust_card` funnel). `powers.apply_power` converts positive
   player Strength to Charge when the player carries the
   `tamakushi_casket` relic hook (Flawless Strategy). All guarded:
   ref/Klee/Furina paths are dead branches — the frozen anchor is
   untouched.
6. **`refpowers.after_card_exhausted`** gains the Charge-accrual branch,
   guarded on the `tamakushi_casket` relic hook (the ONE exhaust funnel:
   played-exhaust, mid-card exhausts, ethereal, autoplay sweep, prevention
   procs all pass through it).
7. **Pilot (tier0/pilot/policy.py)** gains a `charge` scoring term,
   `w.get("charge", 0.0)` — inert for every existing pilot yaml.
   `content/pilots/archetypes.yaml` gains `commander` / `priest` / `assist`
   pilot rows.
8. **Metrics (tier0/harness/metrics.py)**: `FightStats` gains
   `prevented: int = 0` (damage prevented by the ward) and
   `charge_gained: int = 0`. NOT folded into any axis: A4-credit for
   prevention is a metric-redefinition and therefore red-pen (ruling ask in
   the report). `engine_closure` diagnostic (report-only flag, R14) counts
   turns where cards created ≥ cards consumed.
9. **Constants**: new Kokomi section (CHARGE_PER_EXHAUST etc., all
   PROPOSED); `NATION_WEIGHTS` gains `"inazuma": 1.0`.

## v0.2 sheet pass additions (2026-07-24, same session lineage)

Written BEFORE landing, per the standing rule. Trigger: R51/R52 closed
every kickoff gate; the sheet pass + act-sim readiness work lands now.

10. **`UPGRADE_SHEETS` (tier0/content/upgrades.py) grows one sheet**:
    `kokomi-upgrades.yaml` (full coverage: kokomi-cards +
    inazuma-companions; ceremonial_garment excluded — kit, v1.9). No new
    delta keys: every Kokomi upgrade is expressible in the existing
    dispatch (the resource-curve law forbids gain_charge/conscript deltas,
    which is exactly the set that would have needed new keys). Known gap
    flagged in the sheet header: no sly-delta key exists, so Sly branches
    never move on upgrade.
11. **DRAFTER_VERSION 6 → 7 (tier0/constants.py + tier05/draft.py)**:
    `_static_power` learns three conservative structural proxies —
    `conscript` (STATIC_CONSCRIPT_VALUE 1.5/transform), `gain_charge`
    (STATIC_CHARGE_VALUE 0.5/point), and Sly rider lists priced at
    STATIC_SLY_SHARE 0.5 of printed face. Klee/Furina/Ironclad cards carry
    none of these ops — their draft scores are bit-identical; only Kokomi
    reads differently. Any v6 Kokomi act number would be a different world
    (none were ever produced, so nothing is orphaned).
12. **tier05/runner.py `CHARACTER_PLANS`** gains `kokomi`
    (generic/commander/priest/assist; default plan priest).
13. **Sheet-side (not loader-shared, listed for completeness)**:
    sango_prayer heal → Weak-2-all rework (R52 ask 1); new uncommons
    `exposing_current` / `tidal_lure` (R51 texture pair); Raiden authored
    as opposed-lore 5★ Rare (R52 ask 9); packages gain the two texture
    cards (priest/assist) — v0.2 battery is a NEW labeled world.

## Collision watch

- No existing card ids collide with the new sheets (lint_unique_names runs
  in-suite; verified before landing).
- No changes to Klee/Furina sheets, upgrades, or any ratified band.
- klee-mod C# parity is deliberately NOT touched (sim leads the mod;
  Kokomi has no mod presence yet).
