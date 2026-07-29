# Sprint log — the Fanfare rework (2026-07-28)

Brief: `docs/sprint-fanfare-rework-2026-07-28.md`. The first BALANCE pass
since playtest 3. Four tracks, all RULED; every number below marked PROPOSED
returns at review.

World: **RT7/D12/P3/C4**, seed 11, 600 runs/arm, hunter route, assigned
policy, relics + potions. Batteries: `python -m tier05.exp_pilot_gap` and
`python -m tier05.exp_roster_anchors --runs 600 --jobs 0`, each run BEFORE
(from a clean worktree at HEAD) and AFTER.

---

## The headline: the stacked nerf is roughly a third of her winrate

Every row under the STOKER pilot, per the brief's ruling, with greedy beside
it and both labelled.

| arm | before | after | Δ |
|---|---|---|---|
| **stoker** win | 24.3% | **14.5%** | **−9.8 pts (−40%)** |
| stoker act-1 | 82.2% | 76.8% | −5.4 |
| greedy win | 11.5% | 7.7% | −3.8 pts (−33%) |
| greedy act-1 | 58.5% | 51.7% | −6.8 |

The stoker loses nearly twice what greedy loses, in points — which is the
expected shape and worth saying out loud: **the better the loop was played,
the more of it was the double-count.** The pilot-gap sprint measured exactly
that (47% of generation under greedy, 62% under the stoker), and this is that
measurement paid out as winrate.

Fanfare generation itself fell **34%** under the stoker (352,876 → 232,049
points across the arm) and the meter at read fell 19.5 → 11.5.

### The roster table, and whether this is a playable band

Both runs are complete 12-arm tables, so the anchors travel with the Furina
rows.

| character | plan | before | after |
|---|---|---|---|
| furina | salon | 11.5% | **7.7%** |
| furina | spotlight | 2.8% | **2.8%** |
| furina | fanfare | 1.0% | **0.5%** |
| klee | reaction | 11.7% | 11.7% |
| klee | demolition | 7.5% | 7.5% |
| ref_ironclad | generic | 10.2% | 10.2% |
| real_ironclad | generic | 7.8% | 7.8% |
| real_silent | generic | 2.0% | 2.0% |

**Every non-Furina row is byte-identical across the change.** That is the
cleanest available evidence that the rework is Furina-only: nine arms of
shared engine, drafter, route and pilot code moved by exactly zero.

**Salon lands at 7.7%, against real_ironclad's 7.8%.** On the headline metric
that is squarely in band — she is now where the real base-game reference
character is, having been above him. The brief's stop condition (winrate
collapses, or barely moves) is not met: it moved a third, and landed on an
anchor.

**Two things are NOT in band, and both are reported rather than fixed.**

1. **The `fanfare` archetype is at 0.5%** — below real_silent (2.0%), which
   is the roster floor. The plan named after the stat took the deepest cut
   from the stat's rework, because it is the plan that held the Powers whose
   invisible floor grants Track B deleted. It was already the weakest arm on
   the sheet (1.0%) and is now half of that.
2. **Her act-1 clear is 51.7%**, against 68% for both Ironclads and 79–86%
   for Klee. This was already her outlier before the sprint (58.5%) and the
   rework widened it. Act-1 is the metric with room to move, so it is the one
   worth watching at the next playtest.

**No compensating buff ships from this brief** — that is a [USER] ruling and
explicitly out of scope. The gap is reported; the response is not proposed.

## Track A — single-leg Fanfare

`encore_gained` is DELETED in both engines. `encore_absorbed` is NEW in both.
The design invariant is pinned as a test in the sim
(`test_every_point_past_block_prints_exactly_one_fanfare`) and, on the C#
side, by the constant-parity assertions plus a new absence gate.

The source shares moved exactly as the ruling intended (stoker arm):

| source | before | after |
|---|---|---|
| encore_gained | 45.3% | **deleted** |
| hp_lost | 31.0% | 45.4% |
| encore_spent | 16.3% | 24.1% |
| encore_absorbed | — | **20.8%** |
| center_stage | 7.4% | 9.7% |

Absorption arrived at a fifth of her generation immediately, which is the
asymmetry the track was about: that damage was always happening and always
paying nothing.

**Measured price: ~44% of stoker-arm generation was predicted; the realised
number is a 34% fall in total generation.** Lower than predicted because the
two surviving reduction legs both grew — spending and absorbing are now the
only routes, so each point of Encore that leaves still pays once.

## Track B — the keywords, and the floor rule becomes visible

`FANFARE_FLOOR_PER_POWER` / `_RARE` are deleted from both engines together
with the play-hook branch that read them. Floors per combat fell **7.9 → 0.3**
— the automatic was almost the entire floor economy, and what remains is only
what cards print.

**The keyword allocation (PROPOSED).** All carriers are archon-register,
which is not a coincidence and is the reason no lint amendment was needed:
register lint R2 already claims every Fanfare-touching card for the archon
voice, and the cap only ever binds for a deck pushing the meter high — which
is the fanfare plan, which is that voice. Convention and mechanic point the
same way.

| card | rarity/type | keyword | X |
|---|---|---|---|
| the_sea_is_my_stage | rare POWER | Fanfare +X | 15 (unchanged) |
| rapturous_applause | rare POWER | Fanfare +X | **8** |
| unheard_confession | rare POWER | Fanfare +X | **8** |
| courtroom_drama | uncommon POWER | Fanfare Cap +X | 5 |
| crowd_work | uncommon POWER | Fanfare Cap +X | 5 |
| lasting_impression | common Exhaust skill | Fanfare Cap +X | 5 (was Fanfare +5) |
| reginas_mercy | rare Exhaust skill | Fanfare Cap +X | 5 (was Fanfare +5) |

The two rare Powers granting 8 are **not a buff**: a rare Power received
exactly 8 silently before. Twelve other Powers now grant nothing.

**STATED PLAINLY, because it changes how these cards should be read: the
"Fanfare Cap +X" keyword is close to INERT at current constants.** The cap
has been a non-binding safety rail since F-A5 and read-at-cap measured 0.3%
in the stoker arm after the change. A card printing only Fanfare Cap is
paying almost nothing today. `lasting_impression` is the sharpest case — it
went from +5 permanent baseline to +5 headroom on a ceiling nothing reaches,
which at current constants is close to a deletion of its scaling line. That
is a measurement, not an argument against the pair; the keywords exist so the
two grants can be priced apart, and the cap half becomes live the moment
floors stack or decay softens.

**L12, the transient-grant blocker, is in and it is a BLOCKER on two
surfaces**: a banned op on a sheet row, and a banned op existing in
`effects.OPS` at all. The second half is the one that matters, and it caught
its own bug — see judgment call 6.

**R6** is new alongside it: `gain_fanfare_floor` may only appear on a rare
POWER. It is what mechanically enforces "Fanfare +X is a rare Power payoff".

## Track C — three redesigns and the rename

1. **Slip Backstage** — "Convert 5 Encore into 10 Block. Retain." Priced
   knowing the spend itself prints 5 Fanfare under Track A, so the card is a
   Block card, an Encore sink and a Fanfare source at once. Uses the OVERDRAW
   primitive rather than an `encore_cost` gate deliberately: playing it dry
   costs 5 true HP (which itself prints 5 Fanfare) instead of making it
   unplayable, and an unplayable Retain card is a dead card in hand every
   turn. Rate and Retain PROPOSED. Upgrade buys the rate (10 → 14), not a
   cheaper spend.
2. **The Final Verdict** — the Hyperbeam. "Deal damage equal to your Fanfare.
   Fanfare falls to its baseline, and that baseline falls by 30." Moved
   `generic` → `fanfare` archetype and gained the `scaling` solve, or the
   drafter would never offer it to the plan that can use it — leaving it on
   generic would have kept a 0%-fire-rate card dead for a second, subtler
   reason. X PROPOSED at 30: her meter sits ~11.5 at read after Track A, so
   one cast reliably buries the floor and a second in the same combat is a
   genuinely bad idea. Upgrade cuts the PRICE (30 → 20), because the damage
   has no printed number to grow.
3. **Blocking Notes** — "Gain 5 Block. +2 (+3 upgraded) Block per Companion
   card played this turn." Counts Guest Star token plays, per the ruling; the
   B2 printed-cost lesson is about discounts and this is a payoff. New slope
   rail on the existing B1 block-op rider machinery, marker on the face, rate
   and live count in the hover tip. Upgrade buys the slope.
4. **`box_seats` → `casting_call`** ("Casting Call"). id, C# class, power
   title, loc row and art out-path all moved; the sheet-projections sweep was
   re-run. Art is owed under the new name only — not a second debt.

### The negative floor

RULED, and implemented as ruled: the floor may go below zero, decay clamps to
it, generation climbs out of the hole.

**PROPOSED semantics, flagged for review as the brief asks:** readers CLAMP
at `max(0, fanfare)` via `resources.readable` / `FurinaResources.ReadableFanfare`,
so a negative meter shuts effects OFF rather than inverting them. All four
sim readers and all thirteen C# read sites route through the clamp, and the
clamp is one function on each side precisely so the harsher StS-style
inversion is a one-line flip if [USER] wants it. Negative member ticks
chipping her own stage would read as a bug rather than as a cost, which is
why the conservative reading was taken by default.

## Track D — the D6 probe

**Take Your Bow** (uncommon, cost 0, salon register): "The leftmost member of
your Salon takes their bow." ONE card, not a family; the next playtest is its
measurement. Leftmost is the same end of the FIFO queue a deploy into a full
stage displaces, so the card teaches no new targeting rule.

It enters now because Track A changed what it is worth: the Encore a bow
grants no longer mints Fanfare on arrival, so the card is worth what the BOW
is worth rather than what the buffer is worth — which is the quantity the
probe wants to read. Cost 0 and the absence of any rider are both PROPOSED
and both deliberate: a rider would make a null result unattributable between
the bow and the rider.

## Gates

- **Full-repo pytest from root**: green before (**1359**) and after
  (**1385**, +26 new). Both from repo root, both full.
- **Regen clean.** `tools/gen_roster_cards.py` — furina 77 generated, 2
  blocked, and **`blocked` held at 2 through the whole sprint**. Four new
  codegen surfaces appeared (base-card `retain`, the `crash_fanfare` and
  `salon_bow` ops, and a Companion-tempo `bonus_formula`) and every one was
  IMPLEMENTED rather than deferred. Each surfaced first as a loud block —
  "card field(s) ['retain'] not understood", "op 'crash_fanfare'" — which is
  the DSL-gap law working exactly as written.
- **Structural lint**: CLEAN, 205 generated cards. **Three new L3 rows** per
  the brief's clause — `retain`, `fanfare_keywords`, `crash_fanfare`. Each
  was seen to fail against a planted defect.
- **Constant parity**: OK (71 mirrored, 16 declared unmirrored). Three
  constants RE-CLASSIFIED: `FanfarePerEncoreGained` and both
  `FanfareFloorPerPower*` left the map because they left both engines;
  `FanfarePerEncoreAbsorbed` joined.
- **Register lint**: 0 violations, 79 cards. R2 extended, R6 and L12 added.
- **art_lint**: plan OK (2 pre-existing L6 warnings, unrelated).
- **art_coverage**: 267/269 — 2 owed, `casting_call` (the renamed pre-existing
  debt) and `take_your_bow` (new).
- **Build + validate + bite-check**: `dotnet build` 0 errors, `validate: OK`,
  deployed, bite-check **14 patch classes armed**.
- **Every new gate seen to fail against its defect.** Fourteen mutations run
  and reverted: absorption pays nothing; the gain leg returns; the invisible
  power grant returns (sim); the C# constant returns; Fanfare Cap secretly
  raises the floor; the old subtractive cap rewind; readers stop clamping;
  the bow takes the rightmost member; the companion counter never increments;
  the floor is clamped at zero; a card grants transient Fanfare; the engine
  exposes a transient grant op; a common skill prints the rare-only grant;
  the `resources` import is removed from the pilot. Each failed the intended
  test and only that test.

## Judgment calls made without red-pen

1. **Every X is PROPOSED and picked by hand.** Fanfare Cap 5, Fanfare 8, the
   Hyperbeam's 30, Slip Backstage's 5→10, Blocking Notes' 5 and +2/+3, Take
   Your Bow's cost 0. None was swept; a sweep would have to run through
   `tier05/sweeps.py` under the R33/R67 dead-knob law.
2. **The Fanfare Cap short list is four cards, all archon.** The brief said
   "goes on powers generally … PROPOSE a short list, do not scatter it", and
   those two clauses pull against each other. Resolved toward the short list,
   using register lint R2 as the selector, because that keeps the keyword
   where the cap can ever bind. Twelve Powers therefore grant nothing.
3. **`lasting_impression` and `reginas_mercy` were CONVERTED, not left.**
   Both printed `gain_fanfare_floor` and neither is a rare Power, so R6 as
   ruled makes them illegal. Converting them to the cap keyword was the only
   move that honoured the ruling; deleting their line outright was the
   alternative and would have been a bigger nerf without being asked for.
4. **The grant is written FIRST in `unheard_confession`'s effects list.**
   That card pays Block whenever Fanfare changes, so a grant resolving after
   the power installs would open with 8 free Block nobody printed. This is a
   sheet-ORDERING fact, not an engine guarantee.
5. **`Player.fanfare_cap_base` replaced the subtractive cap rewind.**
   `run_fight` rewound with `fanfare_cap -= fanfare_floor`, exact only while
   `gain_fanfare_floor` was the sole writer of both fields. This sprint broke
   that twice — `raise_fanfare_cap` moves the cap alone, `crash_fanfare` moves
   the floor alone and DOWNWARD (which under the old line ADDED ceiling on
   the way out of every fight). A snapshot cannot drift. The old arithmetic
   passed the entire Furina test file under mutation, so a gate was written.
6. **L12's engine half had the exact bug it exists to prevent, and the
   mutation test caught it.** It was written as `try: import … except
   ImportError: pass`, "so the lint keeps working standalone". Run as `python
   tools/lint_furina_registers.py`, `sys.path` starts at `tools/`, the import
   failed, and the except branch silently disabled half the gate in the way
   the lint is normally invoked — a planted `gain_fanfare` op passed clean.
   Now the repo root is pushed onto `sys.path` and an ImportError RAISES.
7. **`bonus_slope` is an alias for `bonus_per_detonation`, not a rename.**
   The existing key is generic despite its name; renaming it would have
   churned every Klee upgrade row for cosmetics.
8. **Deck packages in `furina.yaml` were NOT re-curated.** Four of them list
   `graceful_retreat` as a card "a human obviously takes", and it is now a
   different card. Re-curating is a design call and would move every
   seven-axis scorecard, so the packages were left comparable and this is the
   flag instead.
9. **Three pre-existing cwd-dependence defects were fixed** because they
   blocked this sprint's own validate gate, and none was caused by it (each
   confirmed by reproducing at HEAD): a relative `Path(...)` in
   `test_roster_codegen`, an inherited-cwd subprocess in
   `test_local_reference_mode`, and a missing `PYTHONPATH` in
   `validate.ps1`'s `Invoke-RepoPython` — the last of which was reporting
   "No module named 'tools'" as "complete local game_ref failed
   verification", a much more alarming thing than what had happened.
10. **`exp_pilot_gap`'s P4 cell was rewritten rather than left printing
    `+0.0%`.** Its counterfactual priced the leg Track A deleted, so it now
    says so and points at the archive numbers. A price tag for a change
    already made is not a price tag, and printing a no-op would invite
    someone to quote it as evidence the nerf was cheap.

## Still owed / routed onward

- **The `fanfare` archetype at 0.5%**, below the roster floor. Reported, not
  fixed; compensation is [USER]'s.
- **Her act-1 clear at 51.7%**, the widest gap to the rest of the roster.
- **Every X above is unswept.**
- **The negative-floor reader semantics are PROPOSED** — clamp today, one
  line from inversion.
- **Art**: `casting_call` and `take_your_bow`.
- **The saturation divergence remains unexplained** (pilot-gap's open half);
  dry rate is 47.9% under the stoker after this change, essentially unmoved.

## What must be said when quoting any of this

Every table above is stamped and names its pilot. Track A and Track B were
measured TOGETHER and are not separable from these runs — no ablation arm was
flown between them, so no row here licenses a claim about either one alone.
