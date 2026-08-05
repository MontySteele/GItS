# Atlas — klee-mod-runtime

Scope: `klee-mod/KleeCode/` — `Powers/`, `Elements/`, `Vfx/`, `Patches/`,
`Relics/`, `Diagnostics/`, plus the four entry-point files at the root
(`KleeMod.cs`, `KleePatchBootstrap.cs`, `KleePck.cs`, `KleeAssetPathFallback.cs`).

## 1. Purpose

The in-game runtime: a net9.0 Harmony/BaseLib mod DLL (`klee.dll`) that makes the
Teyvat Spire roster (Klee, Furina, Kokomi) actually playable inside Slay the Spire
2. It is a **port, not a design surface** — every balance number here mirrors
tier0, which is the single source of truth, and re-deriving one C#-side is the
defect this layer exists to avoid (`Elements/ReactionTable.cs:22-27`,
`Powers/BurstResource.cs:14-18`, `Powers/KokomiResources.cs` transcription table).
It is explicitly **not a simulator and not a test bed**: there is no C# test
project and this DLL only executes inside Godot, so nothing here can be run
against the sim (`Diagnostics/FurinaParityVectors.cs:10-13`). Its second job is
**not losing runs**: several of its patches exist solely to stop base-game code
from soft-locking on a pool it never anticipated (`KleeMod.cs:243-269,318-344`).
Card *content* is generated elsewhere (`tools/gen_roster_cards.py` →
`Cards/Generated/`); this module owns the systems those cards call into.

## 2. Entry points

The DLL cannot be built or run on this host (it needs a Steam install of the game
plus Workshop BaseLib — see `klee-mod/local.props.example`). The gates that DO run
here are Python:

```sh
# the C#-facing contract tests (source-text lints over KleeCode/)
PYTHONPATH=. python3 -m pytest \
  tier0/tests/test_roster_runtime_contracts.py \
  tier0/tests/test_card_play_hook_guards.py \
  tier0/tests/test_canonical_model_misuse.py \
  tier0/tests/test_reaction_phase_parity.py \
  tier0/tests/test_creature_facing_contract.py \
  tier0/tests/test_harmony_bootstrap_contract.py -q

PYTHONPATH=. python3 tools/lint_constant_parity.py    # C# consts vs tier0, by value
PYTHONPATH=. python3 tools/lint_pool_membership.py    # every card class in a pool
PYTHONPATH=. python3 -m pytest tier0/tests -q         # full suite
```

On a Windows/macOS dev box only: `klee-mod/build/deploy.ps1` (builds, stages,
runs `validate.ps1`, copies into `mods/`), `klee-mod/build/validate.ps1`
(static S-rules), `tools/build_pck.ps1` (the art/scene pack), and the manual
Harmony gate `klee-mod/build/bitecheck/` — `dotnet build; ./bin/Debug/harmony-bitecheck.exe`,
which must print `14 patch class(es) armed.`

In-game there is no CLI: `KleeMod.Initialize` is the only entry
(`KleeMod.cs:24-29`), and diagnostics land in `godot.log` — grep `SELFCHECK`,
`harmony:`, `convention scene`.

## 3. Key invariants

- **One aura per enemy.** Application is skipped when an aura already exists;
  `AuraCmd.Find` is the single accessor — `Powers/ElementalApplication.cs:201`,
  `:214-216`.
- **Auras apply in `BeforeDamageReceived`, are consumed in `AfterDamageReceived`.**
  The phase split is what makes "after a reaction nothing sticks" true without
  ordering assumptions — `Powers/ElementalApplication.cs:30-37,183`.
- **Amplifiers (Vaporize/Melt) multiply exactly one hit and are consumed with the
  aura — never persist.** They live only in `AuraPower.ModifyDamageMultiplicative`
  and are deliberately absent from `ReactionEffects` —
  `Elements/ReactionTable.cs:89-93`, `Powers/ReactionEffects.cs:20-23`.
- **Element travels on the CARD, not the damage instance** (`IElementalCard`);
  card-less damage (bombs, the Burst volley, DoT ticks) routes through
  `ElementalHit` — `Elements/Element.cs:20-34`, `Powers/ElementalHit.cs:10-23`.
- **Unpowered mirror hits must re-apply Strength/Weak/Vulnerable by hand** (the
  native powers gate on `IsPoweredAttack()`, which these deliberately fail), and
  truncate exactly ONCE at the end — `Powers/SimDamagePipeline.cs:12-28`,
  `Powers/ElementalHit.cs:16-23`.
- **Balance constants are MIRRORED, never re-derived**, and `lint_constant_parity`
  fails any numeric `const` that is in neither `MIRRORED` nor `UNMIRRORED` —
  `tools/lint_constant_parity.py:83,196,348-355`.
- **Per-type Harmony patching, never `PatchAll`.** One dead lookup must disarm one
  patch, not the rest of the walk; a class that arms ZERO methods is a failure even
  if nothing threw — `KleeMod.cs:33-38`, `KleePatchBootstrap.cs:106-166,141-147`.
- **Exactly one `ModHelper.SubscribeForCombatStateHooks` call**, with every
  character's hooks concatenated behind it (duplicate ids are silently rejected) —
  `KleeMod.cs:55-61`, pinned by `tier0/tests/test_roster_runtime_contracts.py:160`.
- **Once-per-play means `cardPlay.IsFirstInSeries`.** Card hooks fire once per
  replay; the sim grants once per `play_card` —
  `Powers/ElementalApplication.cs:74-95`.
- **Never `new()` an `AbstractModel`, never hand a CANONICAL model to a mutating
  command.** ModelDb constructs canonicals itself; resolve lazily via
  `ModelDb.GetById` — `Powers/ElementalApplication.cs:44-58`.
- **Mutable power fields must be deep-cloned** — `MutableClone` is a
  `MemberwiseClone`, so every bombed enemy would share one list
  (`Powers/BombPower.cs:88-96,121-124`).
- **Loc keys are `Id.Entry`, which BaseLib prefixes** (`KABOOM` → `KLEEMOD-KABOOM`).
  Plain `CardModel` stubs declare loc in `KleeMod.InjectLocStrings`; anything
  deriving from `CustomCardModel` declares an `ILocalizationProvider.Localization`
  override instead — `KleeMod.cs:74-93`, `Diagnostics/KleeSelfCheck.cs:490-496`.
- **Loc encoding: SmartFormat uses SINGLE braces; square brackets are BBCode.**
  `{{Damage}}` renders literally and `[Block]` throws "Found end tag center" —
  `KleeMod.cs:76-89`, enforced `Diagnostics/KleeSelfCheck.cs:544-563`.
- **Every pck lookup funnels through `KleePck.Path`, which returns null on a
  miss** so callers degrade to base behaviour instead of handing Godot a dead
  path — `KleePck.cs:20-24,30-45`.
- **Visuals read state, never own it.** Gauges re-read the authoritative resource
  on refresh; cached values are display-only — `Vfx/GaugeBridge.cs:34-38`.

## 4. Rulings that shaped it

- **R13** (`klee-mod/DECISIONS.md:1905`) — every concrete `PowerModel` in this
  assembly must resolve to an icon that EXISTS in the merged pck, or be listed in
  `KleePowerIcons.IconExempt` with a reason. Enforced by reflection at boot
  (`Diagnostics/KleeSelfCheck.cs:397-436`).
- **R52** (`tier0/DECISIONS.md:1314`) — Kokomi heals no HP, ever; her sustain is
  prevention. Constrains every Kokomi power that would otherwise grant healing.
- **R59** (`tier0/DECISIONS.md:1777`) — shop colorless slot 2 is Uncommon-or-Rare
  at renormalized odds; the C# mirror is `SlotTwoUncommonOdds`
  (`Patches/MerchantCompanionSlots.cs:59,132`).
- **R60** (`tier0/DECISIONS.md:1796`) — phase 1 REDIRECTS the shop only;
  `ColorlessCardPool` must stay populated for its six non-shop consumers
  (`Patches/MerchantCompanionSlots.cs:37-41`).
- **R61** (`tier0/DECISIONS.md:1813`) — tier 0.5 models the shop channel, so C#
  and sim must price it the same way.
- **R69** (`tier0/DECISIONS.md:2164`) — the Orobas upgrade DISPLAYS as "Dodoco
  Tales"; the C# type stays `ExplosiveFrags` because renaming it moves the runtime
  relic id and that is a co-op desync (`Relics/UpgradedStarterRelics.cs:99-118,148`).
- **R70** (`tier0/DECISIONS.md:2209`) — manifest version is MAJOR-AUTO (commit
  count); `deploy.ps1` refuses to overwrite an existing zip, `validate.ps1` S3
  fails on a stale manifest.
- **R71** (`tier0/DECISIONS.md:2267`) — `SPOTLIGHT_BASE_MULT = 1.5` ratified;
  mirrored as `SpotlightSystem.GuestCastBaseMultiplier`.
- **R72** (`tier0/DECISIONS.md:2313`) — Kaboom Beetle Swarm snapshots bombed-state
  **at cast** into `_bombedAtCast`, clears it in a `finally`, and falls back to a
  live read outside a play so previews stay honest.
- **R80** (`klee-mod/DECISIONS.md:2161`) — Charge is never spent;
  `ChargeResource.Spend` is a documented no-op, not an oversight
  (`Powers/KokomiResources.cs:124,154`).
- **R85 / R86** (`tier0/DECISIONS.md:2699`, `:2757`) — Curtain Call's six powers
  are ACTIVITY-triggered, never per-turn, and their per-turn windows reset in
  `BeforeSideTurnStart` (Salon upkeep spends Encore in `AfterPlayerTurnStart`) —
  `Powers/CurtainCallPowers.cs:8-21,61-70`.

## 5. Traps

- **Three different R-namespaces collide.** `KleeSelfCheck` has its own rule labels
  R1-R13/R19 (`Diagnostics/KleeSelfCheck.cs:110-117`), `validate.ps1` uses S1-S7,
  and DECISIONS rulings are R1-R97. A "R3a" in a log line is a self-check rule, not
  a ruling. `R4`/`R5` come from a `rule` parameter, so grepping `Fail("R` misses
  them (`Diagnostics/KleeSelfCheck.cs:113-116`).
- **`KleeAssetPathFallback.cs` looks like dead placeholder scaffolding and is
  load-bearing.** It was renamed from `KleePlaceholderArt` precisely because a name
  predicting its own deletion invites deletion; 9 asset paths have no other source
  — `KleeAssetPathFallback.cs:11-40`.
- **`ProgressSaveManager_EpochCheck_Patch` is a CANARY, not the fix.** If its
  warn line ever appears, BaseLib's `ICustomModel` guard stopped applying. Deleting
  it removes the detector — `KleeMod.cs:396-414`.
- **The `SoftlockGuards` set must use `nameof`, never string literals** — a literal
  survives a rename and guards nothing — `KleePatchBootstrap.cs:53-62`.
- **The self-check must never throw.** A validator that bricks boot is the failure
  mode it exists to prevent — `Diagnostics/KleeSelfCheck.cs:29-31`. It runs as a
  `Priority.Last` postfix on `ModelDb.Init` so it observes BaseLib's loc injection
  — `:568-583`.
- **Phase, not magnitude, is the usual divergence.** `lint_constant_parity` is
  green on `ShatterDamage`/`VulnerableTakenMult` while a hook move re-opens a
  30-50% gap; the phase ledger is `tier0/tests/test_reaction_phase_parity.py:1-16`.
- **`cardPlay.Card.Owner` is null on real paths** (autoplay, token plays) and the
  NRE lands in an async continuation → black screen, not a crash dialog. Guard
  every card-played hook — `tier0/tests/test_card_play_hook_guards.py:1-16`,
  `Powers/ElementalApplication.cs:78-83,113-114`.
- **`Cards/Generated/` is machine-written: DO NOT EDIT** — change the sheet and
  regen (`Cards/Generated/BarbaraShiningIdol.cs:1-7`). Same for
  `Diagnostics/FurinaParityVectors.cs`'s tables, which the Python suite parses
  (`Diagnostics/FurinaParityVectors.cs:14-29`).
- **Bridges are inert when their scene node is missing, which is undebuggable.**
  `KleeSceneTelemetry` exists to make that loud at boot; `%Facing` is the live
  example — `Diagnostics/KleeSceneTelemetry.cs:56-75`.
- **Mirror `%Facing`, never `%Rig` (animated) and never `Visuals.Scale`** — the
  latter inverts the hitbox `UpdateBounds` reads back, a gameplay bug wearing a
  visual bug's clothes — `Vfx/CreatureFacing.cs:32-42`.
- **The bomb-suppression latch lives on the Creature via `SpireField`**, not in
  combat-keyed statics — reload or a second live combat silently reset those —
  `Powers/BombPower.cs:98-108`.

## 6. Reading order

1. `klee-mod/KleeCode/KleeMod.cs` — initialization order, the loc contract, and
   the three softlock patches with their findings written out.
2. `klee-mod/KleeCode/KleePatchBootstrap.cs` — how patches arm and how a failure
   is reported.
3. `klee-mod/KleeCode/Diagnostics/KleeSelfCheck.cs` — the boot invariants, each
   one a bug that shipped.
4. `klee-mod/KleeCode/Elements/ReactionTable.cs` + `Powers/ElementalApplication.cs`
   — the reaction system and its tier0 mirror discipline.
5. `klee-mod/KleeCode/Powers/ElementalHit.cs` + `Powers/SimDamagePipeline.cs` —
   the one damage pipeline every card-less hit must use.
6. `tier0/tests/test_roster_runtime_contracts.py` and `tools/lint_constant_parity.py`
   — what the suite actually holds shut on this module's behalf.
