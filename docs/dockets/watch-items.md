# Watch-item register

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

**Status:** REGISTER. Zero design authority. Opened 2026-08-06 (Track R)
against the sitting of 2026-08-06
(`docs/archive/sitting-record-predraft-2026-08-06.md`); ruling R111.

**What a watch item is** (R111, recorded once for reuse): not a deferral and
not a queue entry. It is a **blessing of the mechanism** plus a **named
quantity** and a **named trigger**. The item does not come back until the
trigger fires, and when it comes back it comes back **with a reading, not with
an argument**.

**What a watch item is not:** a licence to tune. Nothing on this register may
be changed on the strength of being watched.

| # | Family | Blessed | Watched quantity | Revisit trigger | Instrument |
|---|---|---|---|---|---|
| W1 | X4 — Guest Cast unfiltered ×1.5 | the power, as a damage booster | **block-side** Guest Cast scaling | the block scaling getting absurd | block-side Guest Cast telemetry readings |
| W2 | X6 — salon displacement double-pay | the strategy | the **power level** | power level out of band | salon power-level telemetry |
| W3 | X12 — cross-element reaction splashes | the mechanism ("half the fun of co-op") | actual reaction potency in co-op | potency readings from real co-op play | Track H reactions corpus — **blocked, see W3 note** |
| W4 | X5 — decay-proof fanfare floor stacking | the mechanism, **explicitly by design** (a strength-style scaling effect) | the **power level**, against two verified magnitudes | either magnitude being reproduced in a real run, or exceeded | the S13 replay lines themselves + Furina fanfare telemetry |

---

## W1 — X4, Guest Cast multiplies anything tagged companion

**Verdict, verbatim:** *"Seems totally fine as a damage-boosting power… may
need to limit to 'damage only' if the block scaling gets absurd."*

The verdict blesses the **damage** side outright and names the **block** side
as the thing that could turn. The trigger is therefore asymmetric on purpose: a
large damage reading is not a trigger, and a large block reading is.

The named limit, if the trigger ever fires, is already in the verdict — restrict
the multiplier to **damage only**. It is recorded so that whoever reads the
trigger does not invent a different remedy, and it is **not** pre-authorised:
the trigger firing produces a sitting, not an edit.

Mechanism (`review/redteam/exploit-ledger.md` X4): the outward Spotlight 1.5×
applies to any `is_companion` card with no nation, rarity or magnitude filter.

## W2 — X6, salon displacement pays on the way in and the way out

**Verdict, verbatim:** *"As a strategy, totally fine (Defect does the exact
same thing) — it's the power level we need to watch."*

The distinction is the whole entry: **the strategy is blessed and the power
level is watched.** A future reading that says "players are doing this a lot"
is not a trigger. A reading that says the power level is out of band is.

Mechanism (X6): FIFO salon displacement prices nothing — overfilling the stage
pays a free Focus-scaled final bow per displaced member.

## W3 — X12, cross-element reaction splashes

**Verdict, verbatim:** *"Seems probably fine; half the fun of co-op. Check
actual potency in co-op playthroughs."*

**The instrument is not currently usable, and that is part of the entry.** The
Track H reactions corpus is the natural reading, and it carries **O-1** (R112):
`run_battery` merges the gauntlet's two stages into one `FightStats` while
rates divide by records, so every published per-fight reaction rate overstates
— all-row aura applications per fight **7.70 → 6.60, an overstatement of
16.7%**. Until O-1 is repaired and the corpus re-read, a Track H potency number
cannot answer this watch item.

Recording the dependency in both directions is deliberate: R112 names X12, and
this entry names O-1, so neither can be closed while thinking the other is
someone else's problem.

Mechanism (X12): a cross-element splash makes every attack a guaranteed
reaction, and `amp_reaction_up` is a raw uncapped percentage.

## W4 — X5, the fanfare floor is decay-proof on purpose

**Added 2026-08-06 (R114), on W2's pattern.** FLAG-3 asked whether the
family's verdict covered the decay-proof floor stacking or only the cantrip
leg. It covers both, and it arrived with its intent stated.

**Verdict, verbatim:** *"We deliberately allowed for powers to raise the
fanfare floor (without decaying) as a sort of strength-style scaling effect. I
think this is fine."*

**What is blessed is the mechanism, and unusually it is blessed with a design
rationale attached** — the floor is meant to behave like Strength: a permanent
raise rather than a temporary one, and its immunity to the 20%/turn decay is
the *point* of it rather than a hole in it. That is why this entry blesses more
confidently than W1 or W2 do, and it is also why the watched quantity has to be
stated precisely.

**The watched quantity is the power level, and it is anchored to two numbers
this repo actually verified** rather than to a feeling:

| line | magnitude |
|---|---|
| `furina_fanfare_2` | **240 damage from one card** |
| `furina_fanfare_3` | **turn-2 boss kill** |

Both are replay-verified in `review/redteam/exploit-ledger.md` and both are
**run-stretch**, not run-plausible — they need multiple copies of
`the_sea_is_my_stage+`. **The trigger is therefore: either magnitude showing up
in a real run, or being exceeded.** A reading that says "players like stacking
the floor" is not a trigger. A reading that says a run reached those numbers
is.

**No remedy is pre-authorised**, per W1's precedent: the trigger firing
produces a sitting, not an edit. Recorded because the intent statement makes it
easy to assume the opposite — "deliberately allowed" blesses the mechanism, and
says nothing about the magnitude.

Mechanism (`review/redteam/exploit-ledger.md` X5): `gain_fanfare_floor` raises
floor, cap and current together with no ceiling on repetition, and decay
returns 0 at or below the floor.

---

## Pins

W1, W2 and W3 keep their S13 pins in
`tier0/tests/test_s13_exploit_pins.py`, still `xfail(strict=True)`. A watch item
is not a fix, so nothing flips. If one of these pins ever goes red without a
ruling behind it, the mechanism changed by accident — which is exactly the
event the pins exist to catch.

**W4's pin is the exception, and it is inverted.** Because X5 was ruled
*intended*, its pin converted from `xfail(strict=True)` to a
documented-behaviour test that asserts the mechanism **reproduces**
(`test_x5_fanfare_floor_stacking_is_documented_behaviour`, R114). For W4 the
sentence above runs backwards: if that pin goes red without a ruling behind it,
a blessed mechanism stopped working. Same alarm, opposite meaning, and the
docstring says so at the site.
