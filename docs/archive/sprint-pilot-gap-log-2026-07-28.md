> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/sprint-pilot-gap-log-2026-07-28.md` — new path: `docs/archive/sprint-pilot-gap-log-2026-07-28.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Sprint log — the pilot gap (2026-07-28)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Brief: `docs/sprint-pilot-gap-2026-07-28.md`. MEASURE ONLY, and it stayed
that way: no lever moved, no card changed, no balance constant changed.

World: **RT7/D12/P3/C4**, seed 11, 600 runs/arm, hunter route, assigned
policy, relics + potions. Battery: `python -m tier05.exp_pilot_gap`.

---

## The headline: R-C, and a split verdict

The pre-registered reading is **R-C** — but the two halves of the hypothesis
came apart, and that separation is the sprint's real result.

**The pilot gap is real and large.** Same character, same assigned draft, same
seed, same route: the only difference is how the cards get played.

|         arm |   win |  act-1 | acts | deck | fights/run |
|------------:|------:|-------:|-----:|-----:|-----------:|
|      greedy | 11.5% |  58.5% | 0.97 | 22.7 |       12.7 |
|  **stoker** | **24.3%** | **82.2%** | **1.55** | 26.8 | 17.2 |
|  stoke-only | 21.7% |  78.0% | 1.42 | 26.2 |       16.4 |
|   spot-only | 13.0% |  66.0% | 1.10 | 23.9 |       13.9 |

**+12.8 winrate points — but 2.1x.** The pre-registration was written in
POINTS and the base is 11.5%, so R-A's +25 bar was unreachable without
tripling her. Act-1 clear, which has room to move, went **+23.7 points**.
The registered thresholds fired R-C and R-C is what is recorded; the ratio is
context, not a re-cut, and it is not being used to argue R-A after the fact.

**The saturation divergence is NOT explained by the pilot.**

|         arm | dry | full | runway5+ | surplus | held |
|------------:|----:|-----:|---------:|--------:|-----:|
|      greedy | 49.8% | 45.0% | 12.9% | +1.5 | 3.6 |
|      stoker | 46.9% | 47.4% | 11.6% | +1.6 | 3.9 |

The stoker more than doubles her winrate **while the stage stays dry almost
half the time**. R-A required the dry rate to fall below ~25%; it fell by 2.9
points. And the new runway5+ column — the direct analogue of the bar a
playtester reads as "I am not going to run out" — sits at **11–13% under every
pilot including the best one**. The sim does not produce a saturated runway
for anybody.

So the two things the brief bundled together are separable:

- **"Furina is stronger than her sim rows say"** — SUPPORTED, and by a wide
  margin. Every Furina row on record is a floor.
- **"The saturated Encore runway is a pilot artifact"** — NOT SUPPORTED. A
  pilot that stokes hard enough to double her winrate still cannot make the
  bar look full. Whatever the playtest saw, this is not it.

The co-op seat is now the leading remaining hypothesis for the saturation
specifically — which is the destination R-B named, arrived at for one half of
the question rather than for both. That routes to a FUTURE brief, per scope.

## Where the gap actually comes from

The ablations were added because `salon_stoker` changes two things at once,
and "the stoker wins" and "her salon pilot was under-weighting the Spotlight
all along" are different findings with different levers behind them.

**Most of it is the stoke term**: stoke-only recovers 21.7 of the 24.3, and
spot-only recovers 13.0. Deploying early and keeping the stage fed is the
behaviour that matters; the Spotlight re-weight adds about +2.6 on top.

**But it adds them by a mechanism the brief did not predict — see below.**

## The Spotlight behaviour was NOT delivered, and the measurement says why

Brief behaviour 3 was "hold the stage's Spotlight… the stoker may re-weight
[the existing term], not rewrite it." Re-weighting it **moves her away from
holding it**:

| arm | center_stage share of all Fanfare |
|---|---|
| greedy (spotlight 0.4) | 18.9% |
| stoke-only (spotlight 0.4) | 17.9% |
| stoker (spotlight 1.0) | **7.4%** |
| spot-only (spotlight 1.0) | **8.6%** |

`_spotlight_value` scores designation at **20.0** when a Companion is waiting
— a deliberate sequencing priority that pushes her into **Guest Cast** mode,
where the Spotlight is on the Companion. `center_stage` pays 2 Fanfare per
card only **while SHE holds it**. So turning the weight up turns that source
off, and the +2.6 points the re-weight buys are bought by Companion
sequencing, not by stage fuel.

**Behaviour 3 as written is not reachable by a weight.** It needs the term
rewritten to distinguish the two Spotlight modes, and the brief forbids that.
Logged as a scope boundary hit rather than quietly counted as delivered.

## Track 3 — the two nerf price tags, computed, not implemented

Pure accounting over emitted events. The counterfactual drops the **smaller**
leg, which is the conservative direction: it prices the cheaper of the two
single-count rules and so cannot overstate what the nerf buys.

| arm | Encore double-count | single-count counterfactual | center_stage |
|---|---|---|---|
| greedy | 47.2% of generation | −11.7% Fanfare | 18.9% |
| stoker | 61.6% of generation | −16.3% Fanfare | 7.4% |

The double-count is the **majority** of her Fanfare under a pilot that runs
the engine, and it grows as the pilot gets better at running it — 47% → 62%.
That is the shape of a flywheel: the better the loop is played, the larger the
share of its output that comes from the loop taxing itself twice.

Neither is implemented and neither is recommended here.

## Fanfare sources, drafted decks vs the hand-built one

P3 re-runs the 38d7769 census against decks the drafter actually assembles.
The shares are **not** the ones the hand-built power-heavy deck produced:

| source | drafted (greedy) | drafted (stoker) | hand-built power deck (S8) |
|---|---|---|---|
| encore_gained | 35.5% | 45.3% | 35.0% |
| hp_lost | 33.9% | 31.0% | **8.4%** |
| center_stage | 18.9% | 7.4% | **39.8%** |
| encore_spent | 11.7% | 16.3% | 16.8% |

A drafted Furina takes four times as much of her Fanfare from **being hit**.
Both readings are correct about their own deck; the S8 table should not be
quoted as "Furina's Fanfare sources" without saying which deck it is about.

## Gates

- **Full-repo pytest from root**: green before (**1339**) and after
  (**1359 passed**, +20 new). Both from repo root, both full.
- **Anchor reproduction**: `exp_roster_anchors --runs 200 --jobs 0` captured
  before the policy edit and re-run after. **All 12 arms byte-identical**,
  including all three Furina plans and both real anchors. The standard pilots
  and their weights are untouched.
- **Every new gate seen to fail against its defect.** Ten mutations run and
  reverted: cap read as the constant instead of the per-player stat; deploy
  blind to open-vs-full slots; fuel priced as a cliff instead of a split;
  `stoke` leaked onto the reachable salon pilot; the stoker made reachable as
  an archetype; runway threshold read per-member instead of per-stage; runway
  collapsed into full rate; sources credited net of overflow; legacy
  un-instrumented events credited to a source; pilot override omitted from
  the stamp; bad pilot id not caught at construction. Each failed the
  intended test and only that test.
- **Version stamps on every table**, and every non-default pilot names itself
  in its own stamp line (below).

## Judgment calls made without red-pen

Listed because the brief requires it. None of these is a balance decision;
all of them are pilot or instrument choices.

1. **The five stoke constants were picked by hand and never swept.**
   `STOKE_DEPLOY_OPEN 6.0`, `STOKE_DEPLOY_FULL 1.5`, `STOKE_RUNWAY_TURNS 2.0`,
   `STOKE_FUEL_HUNGRY 1.2`, `STOKE_FUEL_SATED 0.15`. They were calibrated by
   eye against the scale of the existing `_charge_value` and `_spotlight_value`
   terms. **The reported gap is therefore a lower bound on what a tuned
   stoker would show**, and no number here should be read as "the ceiling".
2. **They live in `tier0/pilot/policy.py`, not `tier0/constants.py.`**
   constants.py is the surface the C# parity gate compares by value, and a
   pilot heuristic has no C# counterpart — the mod ships no bot.
3. **`spotlight: 1.0` for the stoker's re-weight** was a guess at "values
   designation without dominating". The measurement above shows it does
   something other than what was intended; see the scope-boundary section.
4. **Two ablation arms were added beyond the brief** (`salon_stoke_only`,
   `salon_spot_only`). Without them the two-change stoker could not be
   attributed, and the attribution turned out to matter.
5. **`turns_to_kill` and `hp_left` are computed over WON fights only.** A
   loss ends when she dies, so folding losses in reports "died fast" as
   "killed fast". Registered here because the brief named the metrics but not
   their denominator.
6. **`RUNWAY_SATURATED_TURNS = 5` is registered in `encore_telemetry`**, not
   passed per call, so no later cell can re-cut the threshold and quote the
   result as the same column.
7. **Per-source Fanfare is credited by REQUESTED, not by what survived the
   cap.** Crediting net of overflow would re-attribute spill to whichever
   source happened to be measured while there was room — a fact about order,
   not about sources.
8. **The isolation gate pins REACHABILITY, not a pilot-id list.** "Only
   salon_stoker declares stoke" would have to be edited every time an arm is
   added, and a gate that gets edited is not a gate. What protects the frozen
   tables is that no `resolve_plan` path reaches the stoker family.
9. **`Cell.pilot_override` names itself in `stamp()` only when set.** Naming
   the pilot unconditionally would rewrite every stamp on record and stop the
   canonical line matching the sprint docs that cite it.

## Debts retired

- **The owed post-`box_seats` salon re-measure.** P1's salon rows are taken
  after A12 made the member cap a per-player stat, in the current world, with
  a stamp. Any salon number quoted from before 2026-07-28 predates that cap.

## Still owed / routed onward

- **The saturation divergence remains unexplained** and is now the sharper
  question, since the pilot is ruled out as its cause. Co-op seat dynamics
  next, via a future brief.
- **Behaviour 3 ("hold the Spotlight")** needs `_spotlight_value` to
  distinguish Guest Cast from self-held before a stoker can encode it.
- **The stoke constants are unswept.** A sweep would have to run through
  `tier05/sweeps.py` under the R33/R67 dead-knob law.
- **The lever pick is [USER] red-pen** and nothing here recommends one.

## What must be said when quoting any of this

Never quote a stoker row against a greedy row without both labels. This is
enforced structurally rather than by discipline: `pilot_override` lands in
`Cell.stamp()`, so a table printed off a non-default pilot names it in its own
mandatory stamp line —

    cell=pilot-gap[stoker] seed=11 runs=600 pilot=salon_stoker RT7/D12/P3/C4
