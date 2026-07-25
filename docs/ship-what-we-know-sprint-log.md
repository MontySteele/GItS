# Implementation Sprint — "Ship What We Know" — execution log

Sprint doc: **docs/ship-what-we-know-sprint-plan.md**, recorded verbatim there
per the house rule that no artifact lives only in chat (the `*-plan.md` /
`*-log.md` pairing follows the animation-sprint and sheet-pass precedents).
Opened 2026-07-25 on branch `furina/ship-what-we-know`.
DECISIONS entry: klee-mod/DECISIONS.md, "Implementation sprint: C# parity,
co-op ownership, upgrade lint, known-card fixes — no new design".

Governing intent, verbatim from the user: *"Let's take everything we already
know about and implement it so we don't stack a giant backlog of design ideas
on top of one another."* Direction RATIFIED; **every number PROPOSED** pending
one red-pen session (see §Gates in the sprint doc).

**Ordering law in force:** G-A first among Furina-touching items. G-B
independent. G-C / G-E / G-F parallel. G-D's numbers land any time; its
red-pen happens once, late, over the whole set. **Hard gate: G-D4 is not
decided before G-A lands.**

---

## Sprint-start state (2026-07-25)

Branched from `kokomi/playtest-build-sprint` @ `4ce3b87` ("Track P: pin the
Oath's hidden coupling, and watch act 3 by construction"), which is one commit
ahead of `origin/main` @ `7260590`.

**The animation stream is live in the same working tree.** Uncommitted at
sprint start: `klee-mod/KleeCode/Vfx/SalonVisualsBridge.cs`,
`klee-mod/KleeCode/Diagnostics/KleeSceneTelemetry.cs`,
`klee-mod/KleeCode/Vfx/CreatureFacing.cs` (new),
`klee-mod/pck-src/{furina/model/combat.tscn, furina/ui/salon_stage.tscn,
klee/model/combat.tscn}`, `tools/build_pck.ps1`, `klee-mod/DECISIONS.md`,
`docs/animation-sprint-2-log.md`.

`Powers/FurinaResources.cs` — G-A's main surface — is **clean** at sprint
start, so the G-A4 collision risk is live but not yet realised. This sprint
does not stage or commit any file in the list above except `DECISIONS.md`
(append-only, at the end of the file, where the animation stream's own edits
are not).

---

## G-A — C# parity: the orphaned F-D

### The decoder fact, restated because it governs the whole track

The playtest note *"Furina fanfare still capped"* is not a bug report. It is
an accurate description of a build that predates the read-only rework. The
fanfare sprint ratified, tested and shipped read-only Fanfare to the **sim**
and the **sheet**, then hard-gated the C# port (F-D) behind an F-C that the
close-out declares will never run. So the live C# layer still implements the
**retired** design: a capped, spendable meter with no decay and no floor.

Every live playtest until this track lands generates feedback against a kit
that does not exist in the design of record. That is why G-A is blocking and
why G-D4 is gated behind it.

### G-A1 — what the port has to match

Source of truth is the sim, read at `4ce3b87`:

| Behaviour | Sim site | Rule |
|---|---|---|
| Decay | `resources.decay_fanfare`, called from `combat._player_turn` | At the **true top** of the player turn, before block-clear / draw / Salon upkeep. Skipped while `state.turn < 2`. Proportional: `max(1, round(fanfare * FANFARE_DECAY_FRACTION))` while above the floor, else `0`. Then `fanfare = max(floor, fanfare - decay)`. |
| Floor grant | `resources.gain_fanfare_floor` | `floor += n`, `cap += n`, `current = min(cap, current + n)` — all three together. Raising the cap alongside the floor is load-bearing, not bookkeeping: a floor that pushed current toward an unmoved ceiling would just re-pin the meter. |
| Power grant | `combat.play_card`, after the replay loop | Playing a Power grants a floor by rarity: rare `FANFARE_FLOOR_PER_POWER_RARE` (8), else `FANFARE_FLOOR_PER_POWER` (5). **Once per card, not once per replay** — a doubled Power is still one performance. Fires **after** resolution so a Power that also grants a floor outright does not double-count against its own read. |
| Per-combat reset | `combat.run_fight` | `fanfare = 0`; `cap -= floor`; `floor = 0`. The cap rewind is the real bug fix: `player` is one object reused across every fight, so without it the ceiling ratchets upward all run. |
| Spend | — | **Gone.** `fanfare_cost` was retired by F-A4 and has no meaning in the design of record. |

Rounding note recorded deliberately: Python's `round()` is banker's rounding
(half-to-even), and C#'s `Math.Round(double)` default is *also*
`MidpointRounding.ToEven`. The two agree without a flag. This is exactly the
kind of silent per-language default that a trace-parity acceptance exists to
catch, so it is written down rather than trusted.

### G-A1 — what landed

`klee-mod/KleeCode/Powers/FurinaResources.cs`:

- **`FanfareFloorResource`** (new) and **`FanfareCapBonusResource`** (kept) are
  the floor and cap halves of a constellation grant, mirroring the sim's two
  independent `fanfare_floor` / `fanfare_cap` fields.
- **`GainFanfareFloor`** raises floor, then cap, then clamps current — *in that
  order*. Getting the order wrong truncates the grant at the old ceiling and is
  invisible in play; it has its own regression test.
- **`DecayFanfare`** takes `max(1, round(current * 0.20))` while above the
  floor, then clamps. Rounded with an explicit `MidpointRounding.ToEven`.
- **`SpendFanfare` is deleted**, along with the `AfterCardPlayed` settle that
  called it and the `CustomResources<FanfareResource>.Cost(...)` read that fed
  it. A test asserts the absence, because a reintroduced spend would fail
  nothing — it would just quietly drain a meter that 11 cards read.
- **`RaiseFanfareCap` is kept and annotated as retired grammar.** No sheet
  carries `raise_fanfare_cap` (verified), but the cap is still a real quantity
  and this is its only writer.

**Two constants were free.** The cap-rewind — the sim bug worth porting — turns
out to be structurally impossible on this side: BaseLib's
`BasicCustomResource.PrepForCombat()` sets `Amount = 0`, and it runs per
`PlayerCombatState`, so floor and cap bonus both rewind by construction. The
sim needed an explicit `cap -= floor` only because its `Player` object is
reused across every fight. Recorded with the decompile citation rather than
asserted, since it is a BaseLib default this file does not control.

**The decay site.** `BeforeSideTurnStart(Player)`, guarded on
`PlayerCombatState.TurnNumber <= 1`. Chosen from the decompile, not guessed:

- `TurnNumber` is **per-player and 1-based** (`"This starts at 1, so it should
  never be 0"`), which is exactly the sim's `state.turn` — and exactly what
  co-op needs, since Furina must decay on *her* second turn, not the table's.
  `RoundNumber` would have been wrong here for that reason.
- `CombatManager` awaits `BeforeSideTurnStart` to completion, *then*
  `AfterBlockCleared`, *then* `AfterSideTurnStart`. So decay is guaranteed
  ahead of the block clear, the draw, the aura tick, and Salon upkeep
  (`AfterPlayerTurnStart`) with no intra-broadcast ordering assumption.
- A dozen vanilla powers use exactly this hook plus a `TurnNumber <= 1` guard
  to mean "not on the first turn", so the idiom is the game's, not ours.

**One residual ordering caveat, recorded rather than hidden.** Bomb detonation
also rides `BeforeSideTurnStart`, and order *between models* within a single
broadcast is not guaranteed. A bomb that damages Furina mints Fanfare from HP
loss, so in the Klee-bombs-Furina co-op case decay may or may not see that
income; the sim always decays strictly first. Not fixable from inside a hook,
too narrow to justify a Harmony patch, and it is written down so the next
person meets it as a known limit rather than a mystery.

### G-A3 — call-site census

Every C# site that reads or writes Fanfare. `Powers/FurinaResources.cs` unless
noted.

| Site | Kind | Status |
|---|---|---|
| `FanfareResource` | storage | **kept**, spend path deleted, `Spend` left as a defensive no-op |
| `FanfareCapBonusResource` | storage | **kept** — cap half of a grant |
| `FanfareFloorResource` | storage | **NEW** — floor half |
| `Fanfare()` / `FanfareCap()` | read | unchanged |
| `FanfareFloor()` | read | **NEW** |
| `GainFanfare()` | write | unchanged (generation) |
| `SpendFanfare()` | write | **DELETED** |
| `GainFanfareFloor()` | write | **NEW** |
| `DecayFanfare()` | write | **NEW** |
| `RaiseFanfareCap()` | write | kept, annotated retired |
| `GainEncore()` → `GainFanfare` | write | unchanged |
| `SpendEncore()` → `GainFanfare` | write | unchanged |
| `AfterCurrentHpChanged` → `GainFanfare` | write | unchanged |
| `AfterCardPlayed` — Fanfare cost settle | write | **DELETED** |
| `AfterCardPlayed` — Power rarity grant | write | **NEW** |
| `BeforeSideTurnStart` — decay | write | **NEW** |
| `SyncMeters` → `SyncMeter<FanfareMeterPower>` | display-only | unchanged |
| `FanfareMeterPower` localization | display-only | **text updated** — now states decay and baseline, and deliberately stops naming the cap |
| `FanfareAttackPer10Power.ModifyDamageAdditive` | read | unchanged (Rising Ovation) |
| `SpotlightSystem.cs:228` `GainFanfare` | write | unchanged (Center Stage) |
| `SalonPowers.cs:112` `Fanfare()/FocusPerFanfare` | read | unchanged (the Focus analogue) |
| `Cards/FurinaRiderTips.cs:72` | display-only | unchanged |
| `Powers/KleePowerIcons.cs:68` | display-only | unchanged |
| `KleeMod.cs:165` (loc key) | display-only | unchanged |
| 11 generated readers (Crescendo, Dramatic Entrance, Flood of Emotion, High Tide, Standing Room Only, Universal Revelry, Florid Cadenza, Showstopper, Rapturous Applause, Let the People Rejoice) | read | unchanged — every one reads a live meter now instead of a pinned one |
| `TheSeaIsMyStage`, `LastingImpression` (generated) | write | **NEW** — via `GainFanfareFloor` |

No site was left stale. The count that matters: **zero** remaining spend sites,
**three** new write sites, **eleven** readers whose inputs now move.

### G-A4 — Funnel Contract check

Fanfare is not one of the contract's three points (Salon slots, Encore absorb
funnels, Spotlight designation), so this track was free to move it. **No Encore
funnel identity changed** — `GainEncore`, `SpendEncore`, `SpendEncoreOrHp` and
`AbsorbDamage` keep their signatures, their call order and their
`GaugeBridge.Refresh` / `SalonVisualsBridge.Refresh` calls, which are
display-only and own no state. No cross-session stop-work note was required.

The one visual consequence worth flagging to the animation stream: the Fanfare
badge now *changes every turn on its own*, where before it sat still. The badge
was kept in the E1 diet precisely because the redesign was going to make it a
live number, so this is the intended outcome — but it is the first Furina badge
that animates without a card being played.

### G-A2 — the two deferred cards

`gain_fanfare_floor` got its C# home, so `the_sea_is_my_stage` and
`lasting_impression` now generate. Wiring took six generator sites (op set,
validation, DynamicVar, emission, description text, category bucket) plus two
more that only showed up on the second run: `EXPRESSIBLE_DELTAS` and the `has`
table in `upgrade_plan`, without which both cards generated *with no upgrade
path* — a silent downgrade from "deferred" to "dead campfire choice".

`FURINA_DEFERRED_TO_FD` is now empty and kept, per the `florid_cadenza`
precedent. Coverage moved **75 generated / 3 blocked → 77 / 1**; the one
remaining block is `let_the_people_rejoice`, the hand-written kit Burst.

Card text: *"Permanently raise your Fanfare baseline by N this combat."*
"Baseline", not "floor" or "minimum" — the meter's own rule text says it fades
"never below the baseline your Powers have built", and one concept gets one
word.

Worth noting for the red-pen: `the_sea_is_my_stage` grants **twice** — 15 from
its own effect and 8 from being a rare Power — landing a floor of 23. That is
what the sheet comment says it should do, and the trace below confirms it, but
it is a large number and it is PROPOSED.

### G-A5 — acceptance

**(a) Trace parity.** There is no C# test project; the DLL only executes inside
the game. So "run both and diff" was never available, and parity is assembled
from two halves that are each machine-checked:

- `docs/furina-fanfare-parity-vectors.json` — 16 decay vectors and 6 floor-grant
  vectors, **derived from the sim**. Cases chosen to hit branches, not to look
  plausible: the `>= 1` anti-stall rule (2 → 1), the exact-fall case (5 → 4),
  the clamp binding (10 on floor 9 → 9), resting *on* the floor (9/9 → 9, which
  catches a meter that grinds through its own baseline), and the 38/40/+5 row
  that fails if the cap is raised after the clamp instead of before.
- `klee-mod/KleeCode/Diagnostics/FurinaParityVectors.cs` carries the same table
  as C# literals and runs the C# arithmetic against it **at boot**, via a new
  `KleeSelfCheck` rule R19. Findings log as `SELFCHECK` errors; it never throws.
- `tier0/tests/test_furina_fanfare_parity.py` parses that C# file and asserts
  its table *is* the sim's, asserts the three ported constants match
  `tier0/constants.py` by reading the C# literals, and asserts the spend path
  stays deleted.

So the Python suite guarantees the two question sheets are identical, and the
in-game check guarantees this side's answers match its sheet. Neither half is
load-bearing alone.

One thing the vectors cannot do, stated because it looks like an omission:
**no vector can force the banker's-rounding tie.** A tie needs a meter value
that is a multiple of 2.5, which an integer never is, so at
`FANFARE_DECAY_FRACTION = 0.20` the Python/C# shared half-to-even default is
belt-and-braces rather than load-bearing. It stops being unreachable the moment
the fraction changes — 0.10 makes every odd multiple of 5 a tie — which is why
the C# pins `MidpointRounding.ToEven` explicitly instead of trusting a default
to survive a constant change.

**Sequencing** is what no automated check on either side can reach, so
`tier05/exp_furina_parity_trace.py` prints the sim's answer turn by turn for a
deterministic scripted fight:

```
  turn  event                   amt  fanfare  floor   cap   note
     1  play an_invitation
     2  fanfare_decay             0        0      0         resting on floor
     2  play lasting_impression
     2  fanfare_floor_granted     3        3      3    33   source=card:lasting_impression
     2  gain_fanfare              4        7                source=encore_gained
     3  fanfare_decay             1        6      3
     4  fanfare_decay             1        5      3
     4  play the_sea_is_my_stage
     4  fanfare_floor_granted    15       20     18    48   source=card:the_sea_is_my_stage
     4  fanfare_floor_granted     8       28     26    56   source=power:the_sea_is_my_stage
     5  fanfare_decay             2       26     26         resting on floor
     6  fanfare_decay             0       26     26         resting on floor
```

Every ported rule is legible in eleven lines: no decay on turn 1; decay lands
*before* the turn's plays; the rare Power grants twice (card effect, then
rarity) and grants *after* it resolves; and the fall stops dead on the new
floor at turn 5 and stays stopped at turn 6.

**(b) [USER] live capture — OUTSTANDING.** The deck above cannot be forced
in-game, so this is qualitative rather than a diff. Four shapes to look for,
printed by the script itself: turn 1 shows no decay; the meter falls every
later turn; a Power play raises the floor and the fall then stops on it; no
card ever spends Fanfare.

**(c) Suite + codegen green.** `python -m pytest -q` → **753 passed** (was 747
at sprint start; +6 from this track). `dotnet build` → **0 errors, 9 warnings**,
all pre-existing patterns (8 × CS1998 async-without-await in generated cards,
1 × CS8765 in `KokomiResources.cs`). One `CS0162` introduced and removed: a
rarity-ordering check on two `const` operands, which the compiler proved
unreachable — a runtime check on compile-time constants is theatre, and the
real guard is the Python-side constant comparison.

**No winrate bar, by design.** This track ships behaviour, not balance.

## G-B — Co-op correctness

### G-B1 — Best Friends Forever

Root cause was worse than "the result is never filtered by `Owner`".
`CompanionPlays` stored a bare `List<ModelId>`, so ownership was not merely
unfiltered — it was **unrecoverable**. No amount of filtering at the call site
could have fixed it.

Fixed at the tracker: entries are now `(Player Owner, ModelId Id)`,
`PlayedThisCombat` takes the owner and filters on it, and the generator emits
`PlayedThisCombat(CombatState!, Owner)`.

Uniqueness is now **per owner**, deliberately. If both players play Oz, both
should get an Oz back; deduplicating across owners would have fixed the leak by
creating a subtler one — the second player's copy silently vanishing. Sheet
text unchanged, because `copy_companions_played_this_combat` always meant the
owner's.

### G-B2 — the bug class

Every C# consumer of a combat-wide tracker that feeds a card effect.

| Tracker | Consumers | Verdict |
|---|---|---|
| `CompanionPlays.PlayedThisCombat` | Best Friends Forever | **was needs-fix → FIXED (G-B1)** |
| `BombPower.DetonationsThisCombat` | The Big One (`grand_finale`) bonus formula | **NEEDS FIX — blocked, see below** |
| `ReactionEffects.TotalResolved` (delta pattern) | Boom Goes the Dynamite, Perfect Timing, Prune (Witch Hunt), The Final Verdict | **NEEDS RULING** |
| `ReactionEffects.ReactionTriggeredThisTurn` | Chevreuse (Vanguard's Valor) | **NEEDS RULING** |
| `DemolitionPowers._procsThisTurn` | detonation splash cap | correctly scoped — instance field on a Power, and a Power has an owner |
| `SpotlightSystem.MovedThisTurn` / `PlaysThisTurn` | selector payoffs, Standing Ovation | correctly scoped — keyed per `Creature` |
| `CompanionCostThisTurnPower` | Friendly Visit | correctly scoped — already tests `card.Owner?.Creature != Owner` |

**Why the detonation counter is not fixed here.** `BombCharge` is
`record struct BombCharge(int Damage, int RoundPlaced)` — it does not carry who
placed it, and bombs live on *enemies*, so the detonating `BombPower`'s owner is
the enemy, not a player. Attributing a detonation to a player needs a schema
change to the charge plus a placer identity threaded through
`BombPower.ModifyAll` / `MoveAllTo`. That is a real change with real blast
radius, and this sprint's mandate is explicitly not to do design work inside a
census. Flagged, not started. **Impact is Klee-plus-Klee only** — a Furina
partner places no bombs — so it is narrower than G-B1 was.

**Why the reaction counters need a ruling rather than a fix.** `TotalResolved`
is a single global monotonic counter, and `MarkTurnStart` fires on a *shared*
broadcast. So in co-op, your partner's Overload satisfies your Chevreuse, and
their reaction landing inside your card's resolution window can satisfy your
Boom Goes the Dynamite. Whether that is a bug depends on a design question this
sprint may not answer: **is a reaction a team event or a personal one?** There
is a defensible reading in which Chevreuse's *"if a Reaction triggered this
turn"* is a co-op payoff working as intended, and a defensible reading in which
it is the same leak as G-B1. [USER] ruling; then it is a fix or a comment.

### G-B3 — the regression, and what it cannot be

The sprint asked for a co-op-shaped unit test with two owners and interleaved
plays. **That test cannot be written**, and the reason is the finding the
sprint asked to be recorded explicitly:

> **Co-op has no sim backstop.** The logic is C#, there is no C# test project,
> and tier 0.5 models exactly one seat. There is no runtime, on either side of
> the language boundary, in which two owners can play cards at all. G-B1 was
> found by two people playing the game, and nothing in this repository could
> have found it.

So `tier0/tests/test_coop_ownership.py` is a **structural** tripwire, not an
execution test: it asserts the tracker records an owner, that the query cannot
be asked without one, that uniqueness is per-owner, and — the one that actually
earns its keep — that **no call site anywhere asks the combat-wide question**.
That catches how this bug would come back: a new consumer copying the old
one-argument shape, or a generator branch nobody updated. It does not catch a
filter that is present and wrong.

Building a second seat into tier 0.5 is a design-stage question and is named in
the sprint's non-goals. It is not started.

<!-- G-C findings appended below. -->
