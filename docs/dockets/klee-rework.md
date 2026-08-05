# Docket — the Klee rework

**Status:** DOCKET. Routed, not decided, not scheduled. Zero design authority:
nothing here proposes a card, a number or a fix. Opened 2026-08-06 (Track R)
against the sitting of 2026-08-06
(`docs/sitting-record-predraft-2026-08-06.md`); rulings R109 and R111.

Source for every item: `review/redteam/exploit-ledger.md` (S13 — 71 lines,
71/71 replay-verified, 14 mechanism families). Pins:
`tier0/tests/test_s13_exploit_pins.py`.

---

## 1. X1 — the companion cost-delta accumulator (NOTE, R111)

**Verdict, verbatim:** *"Let's make a note of this for the Klee rework."*

The note, so the session does not have to re-derive it:
`state.companion_cost_delta_this_turn` is additive and uncapped
(`tier0/engine/effects.py:961-962`) and `card_cost` floors every companion at 0
(`tier0/engine/combat.py:159-160`). One play of Klee's **`friendly_visit`** — a
common that draws its own replacement — makes every companion in hand free for
the turn; any self-replacing companion then loops until the engine's 25-play
detector fires. Ten S13 lines across four independent slices ride this one
accumulator.

### FLAG-1 — HELD, and this docket does not answer it

The accumulator has **two** run-plausible enablers riding the same shared
uncapped state: Klee's `friendly_visit` (common) **and Kokomi's `honor_guard`
(printed 0-cost)**. A Klee-rework-only note leaves the Kokomi leg live.

Two questions were put and neither has an answer:

1. Should the note also ride the Kokomi pool-rework docket
   (`docs/dockets/kokomi-workshop.md`)?
2. Should the accumulator **itself** — shared machinery, uncapped, floored at
   0 — take a structural disposition at a systems session, rather than being
   handled once per character kit?

**Held means held.** Until one-line verdicts land, this docket carries the Klee
leg only, and the Kokomi leg is live and unrouted by design rather than by
oversight.

---

## 2. X7 — the Klee spark economy (NEW LAW + AUDIT, R109)

**Verdict, verbatim:** *"Gate repeatable spark generation behind Uncommon or
make sure no card below Rare is both 'sparks + draw enabler'"*

### 2a. The law

**EITHER** repeatable spark generation sits at **Uncommon or higher**, **OR**
no card below **Rare** is simultaneously a spark source and a draw enabler.

The disjunction is load-bearing and is recorded as stated. Two ways to satisfy
it; the law is not collapsed to one here, and a session that collapses it is
making a design decision that this docket has not been given.

Mechanism the law is aimed at, from the ledger: the spark printer's only bound
is Exhaust, and the shipped upgrade is exactly `{remove: exhaust}`.

### 2b. Audit findings — filled by Track T, 2026-08-06

Sweep methodology and full tables: `docs/track-t-audits-2026-08-06.md` §T-2.
Findings only; no card was changed.

**Limb (a) — repeatable spark generation below Uncommon.** The count depends
on a reading the auditor did not pick:

- **Broad reading** (any non-exhaust repeatable generation): **6 Common
  violations** — `crackle`, `skip_and_hop`, `sparkly_treasure`, `snap`,
  `spark_collection`, `warm_glow`. No basics violate. All power-based
  generation (`spark_per_turn`, `bomb_and_spark_per_turn`,
  `reaction_bonus_spark_energy`, `sparks_n_splash`) is Uncommon+ and compliant.
- **Strict reading** ("repeatable" = loops / multi-fires per play): **0
  violations** — the only loop is `sugar_rush+`/`bright_idea`, both Uncommon.

Which reading the law means is a design call; both counts are on the page.

**Limb (b) — no card below Rare that is both spark source and draw enabler:**
**1 violation** index-wide — `cant_catch_me` (uncommon: gain_spark 1 + draw 1).
Borderline, no verdict taken: `crackle` (discard-enabler, not draw) and
`eager_to_help` (spark-keyed draw that mints nothing).

One non-Klee spark card exists index-wide: `prune_witch_hunt` (uncommon
companion), compliant on both limbs.

---

## 3. X8 — bomb damage, two uncapped terms (AUDIT, R111)

**Verdict, verbatim:** *"Not a problem at higher rarity — need to check these
cards."*

The verdict prices the mechanism as acceptable **at higher rarity** and asks
for the rarity fact, which nobody has. Mechanism, from the ledger:
`_op_modify_bombs` adds a bonus to every bomb on every enemy with no per-card,
per-bomb or per-turn limit, and bomb damage is the product of two uncapped
terms.

### Findings — filled by Track T, 2026-08-06

Sweep methodology and full tables: `docs/track-t-audits-2026-08-06.md` §T-3.
Findings only; no card was changed.

**Term 1 — the additive per-bomb damage bonus** (`tier0/engine/effects.py:443`).
Four uncapped writers:

| card | rarity | note |
|---|---|---|
| `chain_fuse` | **common** | +3→+5, board-wide scope, non-exhaust |
| `careful_arrangement` | **common** | +2→+4, non-exhaust |
| `remote_detonator` | uncommon | +2→+4 |
| `explosives_workshop` | uncommon | `bomb_damage_up` +2/copy |

**Term 2 — `detonations_total`** (`tier0/engine/effects.py:444`, monotonic,
never decays). Single uncapped **reader**: `grand_finale` ("The Big One"),
**rare** — the only consumer of `N_per_detonation_this_combat` in 298 rows.
But the counter's **growth** is ungated: producers run from 3 detonators
(`quick_fuse` common / `remote_detonator` uncommon / `chained_reactions` rare)
down through 15 bomb placers at **basic** rarity, and bombs auto-detonate at
turn start (`tier0/engine/combat.py:452-454`) with no card in the loop at all.

**Against the verdict's pricing:** "not a problem at higher rarity" holds for
term 2's read (one Rare) but **not** for term 1's writers (two non-exhaust
Commons) nor for term 2's growth.

**Adjacent defect surfaced by the sweep** (finding, not a fix):
`docs/klee-character-design.md:50` records a ratified `bomb_damage_up ≤ 4` cap
that is **not implemented** — `max_stacks` only ever arrives from a card row
and no Klee row carries one, so every Klee scaling power is uncapped for the
same reason.

---

## 4. What this docket is not

It is not the Klee rework plan, and it is not a list of things to fix. Three
items arrived from one red-team sweep; the rework session owns everything else
about Klee, including whether these three are even the interesting ones.
