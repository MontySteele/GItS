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
Oath's hidden coupling, and watch act 3 by construction"), one commit ahead of
`origin/main` @ `7260590`.

> **CORRECTION, at close.** The parallel streams committed *during* this sprint,
> and this sprint's four commits sit on top of them, not on `4ce3b87`. The real
> base is **`a879ffe`**, reached via `7c53c31` (animation sprint 2, "Playtest 1:
> the ribbon number was covered…"), `40b0884` and `a879ffe` ("Track A: the Pearl
> of Wisdom, and Kokomi's hooks go live"). Verified: **no commit in this sprint
> touches any animation-stream file** — `git diff --name-only a879ffe HEAD`
> returns 45 files and none of them are under `Vfx/`, `pck-src/`,
> `KleeSceneTelemetry.cs`, `animation-sprint-2-log.md` or `build_pck.ps1`. The
> DECISIONS bookkeeping note about carrying along uncommitted edits to that file
> is therefore moot: the animation stream committed its own work.
>
> One consequence worth naming: **Kokomi's starter relic went live mid-sprint**
> in `a879ffe`. G-C3(b)'s condition — "Kokomi's rides along only if her starter
> relic already exists in-tree" — was satisfied more firmly than it looked when
> the call was made.

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

## G-C — Upgrade coverage

### G-C1 — the lint, and why it has two layers

`tools/lint_upgrade_coverage.py`, wired into the suite at
`test_sheet_lints.py::test_every_draftable_card_can_be_upgraded`.

The sprint asked for one check: every draftable card has an entry in its
`*-upgrades.yaml`. **That check would have reported all-clear on the card the
playtest named.** `nicole_celestial_gift` has `{block_per_turn: +2}` in
`klee-upgrades.yaml` — a perfectly good entry. The defect was one layer down:
the delta was not expressible, so `OnUpgrade()` in the generated C# was an
empty method with a comment in it. The sim upgraded the card; the live game did
not.

So the lint checks both:

- **L1 (sheet)** — the delta exists and is *applicable* (non-empty, not
  `_unexpressible`, not in `upgrades.UNAPPLIABLE`).
- **L2 (codegen)** — the generated card actually emits an upgrade, read from
  each profile's `manifest.json` rather than re-derived, so it cannot drift
  from the emitted C#.

The two get separate exemption lists deliberately: "no delta authored yet" and
"delta exists but the generator cannot say it" are different debts with
different fixes, and collapsing them hides the second behind the first.

Whole classes are exempted by predicate, not by listing ids — kit cards, guest
stars, non-generatable tokens/statuses/curses — because a list would need
editing every time a card is added, which is how a lint becomes stale and
untrusted. A stale-curation sweep runs over both exemption lists.

**Result: the feared companion gap does not exist.** 232 draftable cards across
6 sheets, and exactly **one** finding in the entire roster:
`nicole_celestial_gift`. The playtest's guess that "mondstadt-companions.yaml
carries no upgrade entries at all" was wrong — the companion upgrades live in
`klee-upgrades.yaml`, which is why they looked absent. Good news, and it is why
the lint was worth building before the fills rather than after.

### G-C2 — the one fill

`nicole_celestial_gift`: `{block_per_turn: +2}` → **`{buff: +2}`** (attack
bonus 2→4; block stays 4). **PROPOSED.**

The old delta was unexpressible in *both* layers for the same root cause:
`CELESTIAL_GIFT_BLOCK` is a tier0 constant and `CelestialGiftBlock` is a C#
const, so the block is not a per-card field and neither the sim nor the
generator could touch it. The new delta moves the upgrade onto the half of the
card that *is* a per-card field, which the existing `buff` grammar already
binds to the first top-level `apply_power`. Same upgrade budget, same card
identity (a buffer), zero new plumbing.

The higher-fidelity alternative — make the block a card field and thread it
through `effects.py`, the upgrade grammar, the generator and
`CelestialGiftPower` — is a real four-layer change, is not conventional-delta
work, and is listed for [USER] at red-pen rather than taken here.

Consequently `upgrades.UNAPPLIABLE` is now **empty**. That tripped
`test_m7.py::test_unappliable_upgrades_never_chosen_at_rest`, which asserts the
set is non-empty and says *"retire this test with a ruling, not a skip"* — so
the ruling is on the record there. The test itself is kept, not retired: its
rest-smithing rule is merely vacuous while the set is empty and re-arms the
moment anything becomes unappliable, and the thing the non-empty assertion was
really protecting is now carried far more broadly by the new lint.

### G-C3 — Touch of Orobas

**(a) Decompile first, and it paid.** Vanilla resolves the swap through
`TouchOfOrobas.GetUpgradedStarterRelic`, which is a **hardcoded dictionary of
five base-game pairs** (Burning Blood → Black Blood, Ring of the Snake → Ring
of the Drake, Divine Right → Divine Destiny, Bound Phylactery → Phylactery
Unbound, Cracked Core → Infused Core) with a fallback of
`ModelDb.Relic<Circlet>()` — the no-effect filler. Confirmed exactly as
reported: a strict downgrade dressed as a reward, silent, no error, no log.

Vanilla is **not** extensible there — the dictionary is a private static
property. But **BaseLib already patches that exact method**:

```csharp
[HarmonyPatch(typeof(TouchOfOrobas), "GetUpgradedStarterRelic")]
private static bool CustomStarterUpgrade(RelicModel starterRelic,
                                         ref RelicModel? __result)
{
    if (starterRelic is CustomRelicModel customRelicModel)
    {
        __result = customRelicModel.GetUpgradeReplacement();
        return __result == null;
    }
    return true;
}
```

So the registration surface is `CustomRelicModel.GetUpgradeReplacement()`,
which defaults to `null`. All three of our starters are `CustomRelicModel`s and
**none of them overrode it** — the bug was a virtual method nobody implemented.
No Harmony patch of our own was needed or written. This is precisely what the
decompile-before-asserting norm is for: the naive fix would have been to patch
a method BaseLib is already patching.

**(b) Registered.** `Relics/UpgradedStarterRelics.cs`:

| Character | Starter | Upgraded form | Delta (PROPOSED) |
|---|---|---|---|
| Klee | Pounding Surprise | **Explosive Frags** | 1 → **2** Sparks per detonation |
| Kokomi | Pearl of Wisdom | **Pearl of Insight** | Charge and Burst per exhaust **doubled** |
| Furina | Ethereal Spotlight | **none — curated gap** | see below |

Distinct names rather than a `+` suffix, following the base game's own
convention. Both upgraded forms are **Ancient** rarity, not Starter — that is
load-bearing, not cosmetic: `GetStarterRelic` finds its target with
`r.Rarity == RelicRarity.Starter`, so a Starter-rarity replacement could be
found and "upgraded" again by a second Orobas, and the second pass would fall
through to the Circlet. The bug would come back through the fix. There is a
test for it.

Klee's companion reward slot rides along unchanged on the upgraded form.
Dropping it would have been a second instance of the same bug.

**The magnitude precedent is the base game's own**: Burning Blood heals 6,
Black Blood heals 12 — an exact doubling. Klee's is nonetheless the most
aggressive number in this sprint and is flagged as such: Sparks are her core
economy (three make the next Attack free), so doubling detonation income
roughly halves the time to every free attack. That the base-game starter it
copies is a flat post-combat heal rather than an *engine input* is the argument
against. Red-pen decides.

**Kokomi is included, against the "Kokomi anything" non-goal**, because
G-C3(b) explicitly says hers rides along if her starter relic exists in-tree —
and `PearlOfWisdomRelic` does. Specific instruction beats general non-goal, and
leaving her starter to degrade into a Circlet while fixing exactly that bug for
Klee would have been knowingly shipping a known defect. Flagged for the user to
reverse if that reading is wrong; reverting is deleting one class and one
override.

**Furina has no upgraded form, and that is a finding rather than an omission.**
Ethereal Spotlight adds a one-use Spotlight selector to hand each turn. **There
is no number in it to scale**: the selector is a Token card with no upgrade,
and the effect is binary. Every candidate tune-up is out of bounds *by this
sprint's own rules* —

- a second designation, or changing when the selector arrives, is new
  **behaviour**, which G-C3(b) forbids in a starter upgrade ("an upgraded
  starter that changes behavior is pool-sweep material");
- a per-turn Encore or Fanfare trickle is banned outright by her sheet's
  no-passive-accrual law (kickoff §4), which explicitly names "a per-turn
  Encore power would launder passive Fanfare through the gain hook".

So inventing one here would have broken a ratified law to close a lint. It is
curated in `NO_UPGRADED_FORM` with its reason and its gate. **Consequence,
stated plainly: Touch of Orobas still hands Furina a Circlet — and she is the
character the playtest was played on.** [USER] ruling at red-pen: accept a
behaviour change as a deliberate exception, or send it to the pool sweep.

**(c) Sim parity — recorded divergence, which G-C3(c) permits.** tier 0.5 models
act-2 ancients, but **nothing in the sim models a starter-relic upgrade at
all**: `relics.yaml` has the Orobas *event's* Sand Castle, not Touch of Orobas,
and starter hooks are bare names (`spark_on_detonation`) with their amounts
hardcoded at the call site (`gain_sparks(state, 1)` in `effects.py`). Modelling
it means parameterising the hook and adding a relic that rewrites it — real
plumbing, and the sprint's own risk section warns against exactly this kind of
creep inside a census-and-fill track.

**The cost of that choice, so it is not silent: Klee's doubling goes to red-pen
with no sim evidence behind it.** It is the most aggressive number in the
sprint and it is the one least measured. If the user wants it measured before
ratifying, the work is: make the spark amount a constant, add a
`starter_upgraded` relic hook, and add `touch_of_orobas` to the ancient pool.

**(d) Curated-invariant test.** `tier0/tests/test_starter_relic_upgrades.py`.
Source-level for the same reason as G-B3. Four checks: every starter is either
upgraded or curated (the one that catches a *fourth* roster character being
added), the override exists and names its form, the form exists and is not
Starter rarity, and curated absences still apply.

## G-D — the named cards

All numbers **PROPOSED**, applied to the sheets per house practice (land, then
red-pen once over the whole set). Each carries its alternative, so red-pen is a
choice rather than an approval.

| Card | Change | Rationale |
|---|---|---|
| `rain_of_roses` | cost **2 → 1** | The v2 reprice lesson applied: rares were overpriced as a *tier*. Effect untouched, so identity and convergence-cell membership cannot drift. **Alt:** hold cost 2, raise the Encore rider. |
| `star_of_the_show` | printed **3 → 5** per copy | Bounded to magnitude on purpose. Spotlight's 2.3% is not a number a rare power fixes; the structural question is the pool sweep's. |
| `controlled_demolition` | `X_plus_1` → **`X_plus_2`** | The "base rider so X=0..1 isn't dead" fix, in the grammar the sheet already speaks. **Alt:** `bomb_damage` 5 → 7, which scales every X proportionally and leaves the bomb *count* (and the splash proc cap) alone. |

`rain_of_roses` is a **WATCHLIST convergence-cell member** (with `undercurrent`
and `guest_neuvillette_judgment`); a cost cut moves the whole mass-application
cell, so that measurement should be retaken *after* ratification.

Three tests needed updating, and the way they broke is worth recording: two of
them asserted `star_of_the_show`'s printed value **twice, in the test name and
in the assertion**, so a ratified reprice read as a regression. They now read
the printed amount off the sheet — what they exist to protect is the pass-2
`max_stacks` errata and the linearity of a second copy, neither of which is a
claim about the number 3.

### G-D4 — the `ebb_and_flow` ruling

Hard-gated behind G-A by the ordering law. G-A landed, so the gate is open.

**In the build played** the churn fed a pinned meter and did nothing. The
playtest's *"???"* was correct about the card in front of it. **In the design of
record** the same play mints **4 Fanfare** (1 for the Encore spent, 3 for the
Encore gained) into a meter that fades 20% a turn and therefore always has
room, and nets +2 Encore and a card besides.

**RULING: legibility branch, not redesign.** The card justifies itself; it does
not *say* so. No pool-sweep slot.

Scope, so the ruling is not mistaken for the fix: the text change is a
**generator** change (a generation tip on Encore-churn cards) touching every
card with `encore_cost` or `gain_encore` — more than the "cheap" budgeted for
one card, so it is named and not done here. G-A already shipped partial
mitigation: the meter's own tooltip now states the generation rule and the
decay.

## G-E — instruments, and what they found

### G-E1 — `core_complete("fanfare")` (DRAFTER_VERSION 9 → 10)

The predicate asked for generation coverage and floor coverage. Both are
**inputs**. Neither is a payoff. So it reported the archetype online while the
average deck held ~1.87 cards that could read the meter. It now requires at
least one reader.

**Not bookkeeping**, which is why the version moved: `core_complete` and
`_core_progress` both feed `score_offer`, so a fanfare deck now advances its
core — and takes the +3.0 core-advance bonus — on a reader it previously
ignored.

Re-measured (600 runs, seed 11, route `hunter`, v7):

| arm | win | act-1 | payoffs/deck | reach | online |
|---|---|---|---|---|---|
| fanfare | **2.2%** | 55.5% | **2.03** / 20.2 | 10.0% | **75.5%** (was 85.7–86.0%) |
| salon | 18.5% | 62.2% | 1.14 / 23.4 | 4.9% | 68.2% |
| spotlight | 2.3% | 64.5% | 0.83 / 22.8 | 3.6% | 90.2% |

**The instrument fix moved the archetype**, which is worth stating plainly:
fanfare went **1.3% → 2.2%** and payoff reach 1.87 → 2.03. That is the drafter
reaching for payoffs it used to ignore, not noise. So the close-out's headline —
*"1.3% in all three worlds"* — is now an archived number, and the fanfare null
should be restated as **"below the 3% bar in four consecutive worlds"** rather
than "unmoved". It is still below the bar. It moved.

### G-E2 — roster anchors, same world (600 runs, seed 11, route `hunter`)

Every row from one invocation; nothing quoted across a version bump.

| character | plan | win | act-1 | acts | deck | fights |
|---|---|---|---|---|---|---|
| klee | demolition | 4.7% | 83.8% | 1.14 | 24.8 | 15.3 |
| klee | spark | 5.3% | 77.7% | 1.01 | 23.7 | 14.1 |
| klee | reaction | 9.2% | 86.8% | 1.25 | 21.8 | 16.2 |
| ref_ironclad | generic | 7.7% | 62.7% | 1.01 | 22.9 | 13.7 |
| **furina** | **salon** | **18.5%** | 62.2% | 1.18 | 23.4 | 14.3 |
| furina | spotlight | 2.3% | 64.5% | 0.83 | 22.8 | 12.3 |
| furina | fanfare | 2.2% | 55.5% | 0.69 | 20.2 | 11.0 |

**Salon's 18.5% finally has a denominator, and it is damning: salon is double
the best arm on the roster** (Klee reaction, 9.2%) and more than double the
reference Ironclad. Meanwhile Furina's *other* two arms sit below every Klee
arm. She is bimodal — one dominant plan and two dead ones — which is a sharper
statement of the problem than either half was alone.

The salon ruling itself stays out of scope, as the sprint requires. It now has
its evidence.

### G-E3 — free drafting (POLICY_VERSION 2), one cell

**The instrument had a hole that had to be fixed before the question could be
asked.** `adaptive_policy` was already the non-committed scorer G-E3 describes —
printed power plus synergy weighted by what the deck accumulated, no assigned
label anywhere. But `adaptive_score`'s archetype term begins `if a not in
ARCHETYPES: continue`, and `ARCHETYPES` was hardcoded to **Klee's three**.
Running "free draft" on Furina before the fix would have measured *a scorer
blind to salon, spotlight and fanfare alike* — every Furina card scored as
printed power plus the universal block quota — and the number would have looked
like evidence about drafting behaviour.

POLICY_VERSION 2 makes the archetype set character-aware, read off the deck's
cards rather than passed in (a character label down the same channel would be
the first step back toward a plan label). **Klee's numbers do not move** — her
tuple is unchanged and no other character had a synergy term to lose — which is
why this is a policy bump and not a drafter bump.

The cell — salon, 600 runs, seed 11, v7:

| policy | win | act-1 | deck | fights | salon share |
|---|---|---|---|---|---|
| assigned (plan-committed) | **18.3%** | 62.2% | 23.4 | 14.3 | 28.9% |
| adaptive (free-drafting) | **4.0%** | 59.0% | 23.2 | 12.0 | 23.5% |
| **delta** | **−14.3pt** | −3.2pt | — | — | **−5.4pt** |

Free-draft emergent shape: **spotlight 41.3%**, salon 31.7%, fanfare 25.7%,
goodstuff 1.3%.

**This is the playtest's headline finding, quantified, and it is large.** A
drafter picking on card quality rather than a plan drifts to **spotlight — the
worst arm on the roster at 2.3%** — more often than to salon, and loses 14.3
points of winrate doing it. Note the asymmetry: salon *density* only falls 5.4
points while winrate falls 14.3. So this is not merely "fewer salon cards"; the
free drafter is actively picking spotlight cards that do not work.

**Null discipline, as registered in advance:** the result does **not** weaken
the sim-artifact hypothesis — it strongly supports it. Salon "sims dominant"
only when the drafter is *told* to build salon. The pool-sweep pass opens
knowing that.

This track ends at the measurement, as the sprint requires. No design response.

### G-E4 — the calibration note

Added as guardrail 7 in `docs/teyvat-spire-design-principles.md`: absolute
winrates are pilot-limited floors, the instrument's authority is relative deltas
and structural findings, and it is on the record so it stops being re-litigated
per pass. It carries the corollary G-E3 produced the same day — a plan-committed
drafter is *also* better than a human at staying on plan, so an archetype's
measured winrate can equally be an **over**-estimate of what a real drafter
reaches.

## G-F — doc hygiene

- **G-F1.** Kickoff §4's uncapper parenthetical annotated as retired grammar
  with a pointer to the DECISIONS entry. Explicitly an annotation, not an
  amendment: the no-passive-accrual law in the same sentence is untouched and
  F-B4's non-opening reasoning stands.
- **G-F2.** Bookkeeping note in the fanfare sprint log confirming the decay
  ruling took **20% — the conservative alternative — deliberately, over the
  10% proposed in the same cell**. The note exists because the ruling appears
  *earlier* in that append-only file than the sweep that produced it, so a
  top-to-bottom reader would meet the decision before the data. Physical order
  is not causal order, and where they disagree the log should say so.
- **G-F3.** `docs/playtest-2026-07-25-coop-a0.md` — the notes, the build
  decoder, a triage table mapping all ten observations to tracks, the
  `ebb_and_flow` ruling, and the two observations deliberately not acted on.
  It states honestly that the notes are recorded *as quoted in the sprint doc*
  and that fuller raw notes, if they exist, should replace that section.

---

# RED-PEN OUTCOME — 2026-07-26

**The sprint's gate has been run.** Full record:
**docs/red-pen-2026-07-26.md**. This section is the delta against the close-out
below, which is otherwise left as written.

**Ratified as proposed (2 of 7):** `rain_of_roses` cost 1 — *interim*, with a
pool-sweep direction recorded (five rares grant Encore; drop the rider and lean
into the mass-aura identity); `star_of_the_show` +5.

**Ratified as the alternative (1):** `controlled_demolition` took
`bomb_damage` 5→7 with the count reverted to `X+1` — the option this log
recorded as the alternative, chosen for exactly the reason recorded (raising the
count also raises the ceiling and pulls on the splash proc cap).

**Superseded by user redesign (2):** `nicole_celestial_gift` becomes *"Gain 1
Strength and 4 Block each turn"* at cost 2; Explosive Frags' **doubling was
rejected** — *"way too good"* — for *"Gain 3 additional Sparks at the start of
combat"*. Both are implementation-pending.

**Rulings that close open items in this log:**

- **The reaction-counter question (G-B2) is answered: Reactions are TEAM events
  in co-op, working as intended.** The census listed it as NEEDS RULING; it is
  now ruled, and needs only a sealing comment.
- **Furina's starter gap (G-C3) is answered, by overriding this sprint's own
  rule.** R2 grants both Spotlight selector effects at once — new behaviour in a
  starter upgrade, accepted as a deliberate exception by user authority. G-C3
  declined to invent this precisely because it broke the rule; the rule was
  overridden rather than reinterpreted. Still pending implementation, so **Touch
  of Orobas continues to hand Furina a Circlet.**
- **G-A5(b) is clarified as eyes-on, not telemetry** — and remains **OPEN**.

**Two corrections to this log's own claims, on the evidence of the red-pen:**

1. **G-C3(c)'s recorded divergence cost more than it said.** This log noted that
   Klee's relic number would go to red-pen without sim evidence. It did not:
   the red-pen built a throwaway `starter_upgraded` hook and measured it —
   +7.1pt on demolition, +5.0 on reaction, CIs disjoint. Those deltas are what
   rejected the doubling. The lesson inverts: the divergence was not merely a
   cost, it was load-bearing, and the harness the session had to improvise is
   now queue item 2.
2. **G-D's "numbers land whenever" reading held, but the landing did not.** The
   record states its patch had already applied `controlled_demolition` and
   `lasting_impression`; a clean tree at `329c1a7` had neither. Both were applied
   by hand on 2026-07-26. See the Discrepancy section of the record.

**Sprint status: CLOSED at the red-pen.** What remains is a ratified
implementation queue, not sprint work — it is listed in the record, in order.

---

# Sprint close-out — 2026-07-25

## Definition of done, item by item

| DoD clause | Status |
|---|---|
| Live build implements the design of record: Fanfare decays, floors, cannot be spent | **DONE**, verified by vector parity + boot self-check + trace. Live capture **outstanding ([USER])**. |
| Verified by trace parity | **DONE** — and reshaped, because there is no C# test project. See G-A5. |
| BFF copies its owner's companions | **DONE** |
| The bug class has a census and a tripwire test | **DONE** — census found 2 more; neither fixed, both with stated reasons |
| No draftable card lacks an upgrade path without a curated reason | **DONE** — lint + suite gate; 232 cards, 0 uncurated gaps |
| The playtest's named cards have red-penned numbers | **PROPOSED, not red-penned** — red-pen is [USER]'s and is the sprint's own gate |
| `ebb_and_flow` has its ruling | **DONE** — legibility, not redesign |
| Truthful `core_complete` | **DONE**, and it moved the arm |
| v7 anchors | **DONE** — salon is 2× the roster's best |
| Free-drafting scorer with its first measurement | **DONE** — −14.3pt |
| Playtest in the repo with its build-decoder | **DONE** |
| Pool-sweep backlog written down in one place | **DONE** — below |

## What is NOT done, and why

1. **[USER] live capture (G-A5b).** The only acceptance this sprint cannot
   self-serve.
2. **The single red-pen session.** Every number here is PROPOSED: G-D's three
   cards, G-C2's Nicole delta, G-C3(b)'s two relic tune-ups. The sprint's own
   gate says this happens once, late, over the whole set.
3. **Furina's starter has no upgraded form.** Touch of Orobas still hands her a
   Circlet — and she is the character the playtest was played on. Not an
   implementation gap: every available tune-up breaks either the sprint's
   no-new-behaviour rule or her sheet's no-passive-accrual law. Needs a ruling,
   not code.
4. **Two co-op findings from the G-B2 census.** The Big One's detonation count
   cannot be attributed to a player without a schema change to `BombCharge`;
   the reaction counters are a design question (is a Reaction a team event?).
5. **Orobas is not modelled in the sim.** Permitted by G-C3(c) as a recorded
   divergence. **Cost: Klee's doubling is the most aggressive number in this
   sprint and the one with no sim evidence behind it.**
6. **`ebb_and_flow`'s text.** The ruling is made; the fix is a generator change
   across every Encore card, which is more than one card's worth of "cheap".
7. **`lasting_impression` lore audit** — still outstanding from the fanfare
   sprint, rides along with red-pen.

## Measurement status

**G-E2's anchors and G-E3's cell were taken BEFORE G-D's card changes landed.**
They are the pre-G-D baseline, which is the right thing to red-pen *against* —
but after ratification both should be re-run, along with the `rain_of_roses`
convergence cell. One command each.

Version stamps at close: `RUNTEMPLATE 7`, `CONSTANTS 3`, `DRAFTER 10` (G-E1),
`POLICY 2` (G-E3). The last two moved in this sprint, so **every pre-2026-07-25
Furina drafting number is archive.**

## Standing lessons

- **A lint that checks one layer can report all-clear on the exact defect it
  was built for.** The upgrade lint needed the sheet *and* the codegen; the
  card the playtest named passed the first cleanly.
- **Decompile before asserting, still.** The naive Orobas fix was to Harmony
  patch `GetUpgradedStarterRelic`. BaseLib already patches it, and the real
  surface was a virtual method nobody had implemented.
- **An instrument can be blind in a way that looks like data.** The free-draft
  scorer would have produced a confident number for Furina while unable to see
  any of her archetypes. Check what a scorer *can* see before quoting what it
  says.
- **Fixing an instrument can move what it measures.** `core_complete` feeds
  `score_offer`, so making the predicate truthful also made the drafter better.
  A "re-print under the fixed definition" was never going to be just a re-print.
- **Physical order in an append-only log is not causal order.** Where a ruling
  lands above its evidence, say so (G-F2).
- **Co-op has no sim backstop.** Both co-op defects this sprint touched were
  found by people playing the game, and nothing here could have found either.

## The pool-sweep backlog — one place, as promised

The next pass opens with: G-E1's fixed `core_complete`, G-E2's same-world
anchors, and G-E3's −14.3pt free-draft measurement. It inherits:

1. **Salon felt weak, sims 2× the roster.** G-E3 says why: it only dominates
   when the drafter is told to build it.
2. **Free drafting converges on spotlight (41.3%) — the worst arm (2.3%).**
   The sharpest single finding here.
3. **Furina is bimodal**: one dominant plan, two arms below every Klee arm.
4. **The fanfare reach null** — now "below the bar in four worlds", not
   "unmoved": 1.3% → 2.2% under DRAFTER 10.
5. **Spotlight's structural collapse.** G-D2 raised a number and explicitly did
   not try to rescue the archetype.
6. **Per-archetype own-payoff reach**, measured for fanfare (2.03/20.2) and
   nobody else.
7. **Pool dilution** — 78 Furina cards against ~3-card reward screens.
8. **Drafter valuation** — `FANFARE_READER_VALUE` is still 1.0.
9. **Any `ebb_and_flow` follow-on** — the ruling says legibility, so this is a
   text job, not a redesign slot.
10. **Co-op sim modelling** — the standing gap behind every co-op finding.
