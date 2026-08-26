# KleeTests — the mod's C# test suite

`dotnet test` against the **real** `klee.dll` and the **real** `sts2.dll`, with
no Godot, no scene tree and no game launch. Built as `EB-105`, whose BACKLOG
row closed on 2026-08-26 (R212) — **this file is the record now**: the headless
boundary, what co-op coverage exists and what is still play-only, and the three
audit findings pinned as the C# authority record all live below.

Two things that were only ever in the row, kept here because nothing else says
them. **The next leg**, if anyone takes one, is a live-`CombatState` harness:
it would move `Deploy`/`Bow`, card `OnPlay` bodies and off-seat attribution
from the play-only list into the boundary. And **tier 0.5 models ONE seat**, so
no sim run can ever disagree with the mod about a two-seat board — that is why
a partial C# backstop is worth having at all.

Before this existed the repo had no C# test project at all, and the shipped
source said so in nine places: tier 0.5 models one seat, so **every co-op
defect ever found was found by playing**. This is a partial backstop for that
— see "Co-op coverage" below for exactly which part. None of those nine
comments says it any more: `EB-130` rewrote `BombPower.cs` and `EB-105`'s
comment leg swept the other eight (`CeremonialGarment.cs`, `CompanionPool.cs`,
`CompanionPowers.cs`, `FurinaParityVectors.cs`, `KleeSelfCheck.cs`,
`KleeOffPoolCards.cs`, `NonCardParityVectors.cs`, `KuragePowers.cs`). Each now
names this project AND the boundary that still applies to it, because "there
is a C# suite" and "this particular fact is reachable" are different claims
and only the second one is worth anything to a reader.

## Running it

```
cd klee-mod/KleeTests
dotnet test                       # 162 tests, ~0.7s after build
dotnet test --filter CoopSeamTests
dotnet test --filter "FullyQualifiedName~H3_authority"
```

From `validate.ps1`, opt-in:

```
klee-mod\build\validate.ps1 -StageDir … -SourceDir … -GameDir … -RunCsharpTests
```

Requires the same two machine-local things as the build: `GameDir` and
`BaseLibDll` in `klee-mod/local.props`. `Directory.Build.props` resolves them,
so nothing here hardcodes a Steam path (spec §0.3).

### Not a deploy gate yet

`deploy.ps1` does **not** run this, and `validate.ps1` only runs it when asked.
That is deliberate and it is a **[USER] call**, not a hygiene decision:
promoting it to mandatory puts the game install and the Workshop BaseLib on
every deploy's critical path, which is the same objection that keeps
`validate.ps1` out of CI (`docs/pending/serenitea-g3-ci-proposal.md`). Whoever
raises that with [USER] should raise the CI question with it.

## Why it works at all

Identical to the F2 bite-check's finding: `sts2.dll` is a plain `net9.0`
assembly, so its logic types load and run outside the engine.

One extra thing was needed, and it is the whole reason the interesting tests
exist. The first call into `MegaCrit.Sts2.Core.Logging.Logger` runs a static
constructor that asks `Godot.OS.GetCmdlineArgs()` whether it is in the editor.
In a test host that is not an exception you can catch — it is a `0xC0000005`
that kills the process mid-run. BaseLib reaches that logger on the **first read
of any `CustomResources<T>`**, which is every Fanfare, Encore, Charge and Burst
accessor in the mod.

`Harness/HeadlessGame.cs` Harmony-patches `GetIsRunningFromGodotEditor` to
return false from a `[ModuleInitializer]`, before anything can touch it — the
bite-check's own idiom of using the mechanism to observe the mechanism. The
patch is confined to the game's **logger**. Nothing in the mod is patched,
stubbed or mocked.

## The headless boundary

These are **hard** limits, established by running into them, not guessed. Most
of them kill the process rather than throwing, so a test that crosses one takes
the whole run with it and reports as `Test Run Aborted`.

| Boundary | What happens | Consequence |
|---|---|---|
| `Player`'s real constructor | reaches `SaveManager.Instance` → Godot Dictionary → **process death** | seats are allocated with `GetUninitializedObject` and the three fields the tested code reads (`Character`, `_relics`, `PlayerCombatState`) are seeded directly. A test needing a fourth Player field has left the boundary. |
| `PlayTelemetry.ToJson()` | `Intent()` → `Root()` → `Godot.ProjectSettings.GlobalizePath` → **process death** | the telemetry schema is pinned by reading the serializer's field set and its `ldstr` key literals (`Harness/Il.cs`), not by running it. |
| `ModelDb` lookups (`GetById`, `ToMutable`) | `ModelNotFoundException` — the registry is populated only by the game's boot | card models are constructed directly; `IsMutable` is set through its own setter, which is the flag `ToMutable` would have set. A canonical `CardModel`'s Owner **getter** throws too — that was `EB-94`'s root cause met from the test side, and now that the tips no longer read it, `CanonicalHoverTipTests` pins the throw as the game's behaviour rather than as a limit on what can be tested. |
| A `HoverTip`'s TEXT | every `HoverTip` ctor formats its `LocString` through `LocManager.Instance`, which is `null` until `LocManager.Initialize` reaches `SaveManager.Instance` — `NullReferenceException` | `ExtraHoverTips` cannot be enumerated end to end. The tip BODIES are plain strings and are tested directly; that a card's tip set arrives intact is wire-only (`EB-94`'s acceptance). |
| Anything touching a Godot object | `Texture2D`, `StringName`, scene nodes — **process death** | no test may touch art, VFX, hover-tip rendering or `KleePck`. |
| A live `CombatState` / a real card PLAY | needs a combat the harness cannot build | card `OnPlay` bodies, damage resolution, `await CardPileCmd.*`, turn sequencing and the Salon's `Deploy`/`Bow`/`PerformMember` are **not reachable**. Ordering facts about them are pinned structurally (IL call sets) and labelled as such. |
| A second peer | no transport, no lockstep | multiplayer **transport** — lockstep RNG agreement, remote-seat selection round trips, desync — remains play-only. |

Nothing here is faked past. Where a fact could not be reached directly it is
either pinned structurally and labelled, or left out.

## Suites

| File | Tests | What it holds |
|---|---|---|
| `ConstantPinTests.cs` | 5 | `SalonConstants` (M24's six summon-damage values, signed 2026-08-13 by R187, plus the stage dials); `PearlOfInsightRelic` = 2× the base exhaust accrual (the EB-74 invariant), and the base values against tier0's constants. |
| `DerivationPinTests.cs` | 16 | Fanfare cap against live max HP (audit **H3**, authority pin), cap clamp on gain, identity gating, the `?? 0` fallback; salon tick = printed base + Focus term, and the dry three-quarters truncation. Plus `EB-122`'s `DiscardsThisTurn`: the two null routes a CalculatedVar preview actually takes, and a labelled structural pin that the per-turn and per-seat clauses are the base game's MementoMori ones. |
| `InterpolationPinTests.cs` | 6 | The tooltip text `lint_constant_parity` structurally cannot see: `SalonMemberPower` and both Pearl relics interpolate their constants rather than restating them (EB-86's shape; M24's "signing is a one-file edit"). Plus `EB-122`'s Charge-rider NOUN — `gyorin_formation` is the first Charge rider on a Block op, and this tip is the only surface carrying the rate, so a hardcoded "damage" would be the single place a player can read it and would read it wrong (SYS-7, one meter over). |
| `CoopSeamTests.cs` | 8 | Per-seat ownership and attribution — see below. |
| `SparkSinkPinTests.cs` | 14 | EB-118 §4.5's Spark sink: the `CanSpend` gate a generated sink hangs `IsPlayable` on (whole price or nothing), True Spark Knight's live threshold and its floor of 1, and two structural pins on `Spend` (it refuses through the same predicate the gate uses, and moves the bank through the same `PowerCmd.ModifyAmount` the threshold consume uses). No card prints the op. |
| `ParityAuthorityPinTests.cs` | 6 | Audit findings **M1** and **M2** pinned as the C# authority record, plus H3's cross-reference. |
| `SalonVerbTests.cs` | 12 | `EB-118` §5.5's Salon verbs: the structural pin that the turn-start upkeep and perform-now resolve through the SAME `PerformMember` (the packet's no-duplicate-implementation requirement), and the behavioural pins for `RotateLeftmost` and the leftmost reads. |
| `RecallFromExhaustTests.cs` | 10 | EB-118's exhaust-pile retrieval: the pool filter RUNS (kit, junk and retriever exclusions), the move is pinned structurally (`FromCombatPile` -> `Add` at `CardPilePosition.Top` -> `AddKeyword`) because it needs a live `CombatState`. |
| `ExhaustSelectionTests.cs` | 15 | `EB-118`'s Exhaust identity context: the six printed descriptors, the derived reads, and above all the SCOPING — another card reads nothing, a second `Open` replaces, the seat is part of the key. Sim twin: `tier0/tests/test_exhaust_context.py`; the emitted column names are pinned across the two engines by `tier0/tests/test_exhaust_context_parity.py`. The codegen's wiring into a generated `OnPlay` is a labelled structural pin — a card PLAY is outside the boundary. |
| `RecallFromDiscardTests.cs` | 11 | `EB-122`'s other half of the same verb: `recall_to_draw` reading its DEFAULT source. The file is about an ASYMMETRY that is deliberate on both sides — the discard branch filters nothing and grants nothing, because [USER] ruled the unfiltered branch (and the self-recall it allows) DELIBERATE at `EB-69`/D3, R198. Sim spec: `tier0/tests/test_eb69_tokoyo_returns_selfrecall.py`. Structural where a live `CombatState` is needed, including the two faces routing through one call. |
| `SlyGrantTests.cs` | 9 | `EB-122`'s turn-scoped Sly grant. The pool predicate RUNS (Skills only, never a kit card, never one already Sly this turn — the clause that makes a second grant pick a different card); the grant is structural, and pins that the expiry is the GAME's `CardCmd.ApplySingleTurnSly` rather than a mod-side timer. Both carriers route through the one home. |
| `ModalChoicePinTests.cs` | 5 | `EB-118` sec.5.4's modal surface: `ModalChoice` delegates to the base game's OWN card-level choice rather than reimplementing one (`CardSelectCmd.FromChooseACardScreen` + `PlayerChoiceContext`, co-op-synced as `PlayerChoiceType.Index`), the three-option ceiling the screen itself enforces, and the `mode_chosen` telemetry row pinned to its tier0 twin. Structural: making a choice needs a live `CombatState`. No sheet row is modal. |
| `BombDeathTeardownTests.cs` | 10 | `EB-138` / R211's compensation for the death teardown `BombInstancingTests` pins on the base game. The turn-start TAKE is pure, so it is all real: one instance's work reaches every pile, each keeps its own placer and payload, every pile is spent before anything that can kill runs, and a second slot finds nothing. Then the game's own kill steps are reproduced (dead + `RemoveAllPowersAfterDeath`) and the later placer's snapshot is shown to survive them, still crediting its own Big One counter and still ringing its own listeners. The MUTATION CHECK is `The_turn_start_hook_resolves_every_pile_not_only_its_own`: put `await Detonate(choiceContext)` back in the hook and it fails. Structural where a live `CombatState` is needed — the detach, the damage, and the fizzle itself. |
| `ConditionalUpgradePinTests.cs` | 6 | `EB-140`'s two branch-moving upgrade delta keys. `hold_the_line`'s `{conditional_block: +3}` and `take_it_from_the_top`'s `{conditional_damage: +4}` shipped at `W3` with an empty `OnUpgrade`; the top-level half is now pinned BEHAVIOURALLY through the game's own `CardModel.UpgradeInternal` (Block 5 -> 8, and the Furina card's printed Block held at 5 because the delta is a damage one), the branch half by the face it prints (`{IfUpgraded:show:9|6}` / `{IfUpgraded:show:14|10}`), and the play-time read structurally -- resolving a branch needs a live `CombatState`. Codegen twin: `tier0/tests/test_roster_codegen.py`. |
| `CardTargetTypePinTests.cs` | 2 | `EB-142`, the 0.2-1028 attended-playtest defect, pinned on the one value that was wrong. `take_it_from_the_top` shipped `TargetType.Self` because the generator derived TargetType from a card's TOP-LEVEL ops only and its 10 damage sits behind a `spotlight_moved_this_turn` conditional -- so the branch's own `ThrowIfNull(cardPlay.Target)` threw on every play with the Spotlight moved, was swallowed by `TaskHelper.LogTaskExceptions`, and the card silently paid Block and nothing else. Real, not structural: the constructor runs headlessly. Class-wide gate beside it: `tools/lint_generated_structure` law L4. |
| `CanonicalHoverTipTests.cs` | 9 | `EB-94`: the hover tips a CANONICAL card could not be asked for. `CardModel.Owner`'s getter asserts mutability, so every tip body that read it threw on the models the compendium hands out (`NCardLibraryGrid._Ready` -> `ModelDb.AllCards` -> `NCard.Create` -> `NCardHolder.CreateHoverTips`) and took the card's WHOLE tip set with it. Real, not structural: the models, the throw and the bodies all run headlessly. The three wire-measured cards (Endless Waltz, Dress Rehearsal, Dinner Service) are pinned by name, the owned-card case is the mutation guard, and one class-wide IL gate bans `CardModel.get_Owner` from the tip classes. |
| `BombInstancingTests.cs` | 18 | `EB-130` / R205's per-placer bomb piles. The instance type itself; the base game's OWN `PowerCmd.FindExistingInstanceForStacking` answering that two placers get two piles, one placer still gets one, and a gather does not land in another placer's pile on the destination; the SUPPRESSION ARBITER (two piles fold to one 0.75, never 0.5625 — the preview and the hit elect the same pile, and the creature-keyed latch is spent once); and `ModifyAll` reaching every pile with the solo total unmoved. Structural where a live `CombatState` is needed: the `DetonateOn`/`MoveAllTo` loops, and the DEATH-TEARDOWN finding pinned on the game's own kill and hook-broadcast machinery. |

**162 tests, all green.**

## Co-op coverage

What this converts from play-only to testable:

- two seats hold **independent Fanfare meters**;
- a seat's **Fanfare ceiling is its own max HP**, not the table's;
- **identity gating** on a mixed table — a Furina resource hook does not fire
  for the Klee seat;
- **relic ownership is per-seat** — Pearl of Insight doubles the accrual for
  the seat holding it and not for the other Kokomi;
- **`BothModes` is a per-seat relic query** — R2's upgrade does not leak across
  the table;
- **salon tick scaling reads the acting seat's meter**, not the other's;
- the **salon company is keyed per Creature**, and two seats resolve to two
  distinct entries;
- the telemetry **fight row carries `seats` and `seat_index`** (EB-18's join
  keys), pinned as both fields and emitted key literals;
- **two placers own two separate bomb piles** on one enemy, and the enemy's
  first attack is still reduced ONCE across both of them (`EB-130`).

What is **still play-only** — this is a partial backstop, not a full one:

- multiplayer transport: lockstep RNG agreement between peers, remote-seat
  selection round trips, desync and disconnect;
- anything that needs a live `CombatState`: the off-seat burst attribution
  `TurnEndAttribution` exists for, corpse detonations, co-op ownership of a
  card actually being played, `Deploy`/`Bow` resolution, and **two seats
  DETONATING on one enemy** — `EB-130` pins the placing half and `EB-138`
  pins everything the turn-start TAKE decides, but the damage itself, and
  with it the fizzle of a hit that lands on a corpse, is still play-derived;
- everything visual.

## A note on what these tests are for

The six tests in `ParityAuthorityPinTests.cs` and the `H3_authority_*` ones in
`DerivationPinTests.cs` carry the audit findings **H3**, **M1** and **M2**. Those are *divergences
between the mod and tier0*, and in all three the 2026-08-13 audit places the
repair on the **sim** side (`BACKLOG` `EB-97`, `EB-100`, `EB-101`, gated behind
the window-2 batch `EB-104`).

They are **pins, not assertions of correctness**. Do not "fix" them. If a
window-2 change moves one, the *mod's* behaviour moved, and that is a finding.
