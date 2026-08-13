# KleeTests — the mod's C# test suite

`dotnet test` against the **real** `klee.dll` and the **real** `sts2.dll`, with
no Godot, no scene tree and no game launch. Registered as `EB-105`.

Before this existed the repo had no C# test project at all, and the register
said so in three places (`BombPower.cs:399`, `CompanionPowers.cs:46`,
`TurnEndSequencer.cs`): tier 0.5 models one seat, so **every co-op defect ever
found was found by playing**. This is a partial backstop for that — see
"Co-op coverage" below for exactly which part.

## Running it

```
cd klee-mod/KleeTests
dotnet test                       # 38 tests, ~0.3s after build
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
| `ModelDb` lookups (`GetById`, `ToMutable`) | `ModelNotFoundException` — the registry is populated only by the game's boot | card models are constructed directly; `IsMutable` is set through its own setter, which is the flag `ToMutable` would have set. A canonical `CardModel`'s Owner **getter** throws too, which is `EB-94`'s root cause met from the test side. |
| Anything touching a Godot object | `Texture2D`, `StringName`, scene nodes — **process death** | no test may touch art, VFX, hover-tip rendering or `KleePck`. |
| A live `CombatState` / a real card PLAY | needs a combat the harness cannot build | card `OnPlay` bodies, damage resolution, `await CardPileCmd.*`, turn sequencing and the Salon's `Deploy`/`Bow` are **not reachable**. Ordering facts about them are pinned structurally (IL call sets) and labelled as such. |
| A second peer | no transport, no lockstep | multiplayer **transport** — lockstep RNG agreement, remote-seat selection round trips, desync — remains play-only. |

Nothing here is faked past. Where a fact could not be reached directly it is
either pinned structurally and labelled, or left out.

## Suites

| File | Tests | What it holds |
|---|---|---|
| `ConstantPinTests.cs` | 5 | `SalonConstants` (M24's six summon-damage values, signed 2026-08-13 by R187, plus the stage dials); `PearlOfInsightRelic` = 2× the base exhaust accrual (the EB-74 invariant), and the base values against tier0's constants. |
| `DerivationPinTests.cs` | 14 | Fanfare cap against live max HP (audit **H3**, authority pin), cap clamp on gain, identity gating, the `?? 0` fallback; salon tick = printed base + Focus term, and the dry three-quarters truncation. |
| `InterpolationPinTests.cs` | 5 | The tooltip text `lint_constant_parity` structurally cannot see: `SalonMemberPower` and both Pearl relics interpolate their constants rather than restating them (EB-86's shape; M24's "signing is a one-file edit"). |
| `CoopSeamTests.cs` | 8 | Per-seat ownership and attribution — see below. |
| `ParityAuthorityPinTests.cs` | 6 | Audit findings **M1** and **M2** pinned as the C# authority record, plus H3's cross-reference. |

**38 tests, all green.**

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
  keys), pinned as both fields and emitted key literals.

What is **still play-only** — this is a partial backstop, not a full one:

- multiplayer transport: lockstep RNG agreement between peers, remote-seat
  selection round trips, desync and disconnect;
- anything that needs a live `CombatState`: the off-seat burst attribution
  `TurnEndAttribution` exists for, corpse detonations, co-op ownership of a
  card actually being played, `Deploy`/`Bow` resolution;
- everything visual.

## A note on what these tests are for

The six tests in `ParityAuthorityPinTests.cs` and the `H3_authority_*` ones in
`DerivationPinTests.cs` carry the audit findings **H3**, **M1** and **M2**. Those are *divergences
between the mod and tier0*, and in all three the 2026-08-13 audit places the
repair on the **sim** side (`BACKLOG` `EB-97`, `EB-100`, `EB-101`, gated behind
the window-2 batch `EB-104`).

They are **pins, not assertions of correctness**. Do not "fix" them. If a
window-2 change moves one, the *mod's* behaviour moved, and that is a finding.
