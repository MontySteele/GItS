# Atlas — klee-mod-runtime

> **Lifecycle: LIVING** — expected to change; read it to work on the project.

Scope: `klee-mod/KleeCode/` — `Powers/`, `Elements/`, `Vfx/`, `Patches/`,
`Relics/`, `Diagnostics/`, plus the root entry files (`KleeMod.cs`,
`KleePatchBootstrap.cs`, `KleePck.cs`, `KleeAssetPathFallback.cs`).

## 1. Purpose

The in-game runtime: a net9.0 Harmony/BaseLib mod DLL (`klee.dll`) that makes the
Teyvat Spire roster (Klee, Furina, Kokomi) playable inside Slay the Spire 2. It is
a **port, not a design surface** — every balance number mirrors tier0, and
re-deriving one C#-side is the defect this layer exists to avoid
(`Elements/ReactionTable.cs:22-27`, `Powers/BurstResource.cs:14-18`). It is
explicitly **not a simulator and not a test bed**: there is no C# test project and
this DLL only executes inside Godot, so nothing here can be run against the sim
(`Diagnostics/FurinaParityVectors.cs:10-13`). Its second job is **not losing
runs** — several patches exist only to stop base-game code from soft-locking on a
pool it never anticipated (`KleeMod.cs:243-269,318-344`). Card *content* is
generated elsewhere (`tools/gen_roster_cards.py` → `Cards/Generated/`); this
module owns the systems those cards call into.

## 2. Entry points

The DLL cannot be built or run on this host — it needs a Steam install of the game
plus Workshop BaseLib (`klee-mod/local.props.example`). The gates that DO run here
are Python:

```sh
# source-text contract tests over KleeCode/ (the only automated C# gate)
PYTHONPATH=. python3 -m pytest \
  tier0/tests/test_roster_runtime_contracts.py \
  tier0/tests/test_card_play_hook_guards.py \
  tier0/tests/test_canonical_model_misuse.py \
  tier0/tests/test_reaction_phase_parity.py \
  tier0/tests/test_creature_facing_contract.py \
  tier0/tests/test_harmony_bootstrap_contract.py -q

PYTHONPATH=. python3 tools/lint_constant_parity.py   # C# consts vs tier0, by value
PYTHONPATH=. python3 tools/lint_pool_membership.py   # every card class in a pool
PYTHONPATH=. python3 -m pytest tier0/tests -q        # full suite
```

Windows/macOS dev box only: `klee-mod/build/deploy.ps1` (build → stage →
`validate.ps1` → copy into `mods/`), `tools/build_pck.ps1` (art/scene pack), and
the manual Harmony gate `klee-mod/build/bitecheck/` (`dotnet build;
./bin/Debug/harmony-bitecheck.exe`) which must print `17 patch class(es) armed.`

In-game there is no CLI: `KleeMod.Initialize` is the only entry
(`KleeMod.cs:24-29`); diagnostics land in `godot.log` — grep `SELFCHECK`,
`harmony:`, `convention scene`.

## 3. Key invariants

- **One aura per enemy.** Application is skipped when an aura exists; `AuraCmd.Find`
  is the single accessor — `Powers/ElementalApplication.cs:201,214-216`.
- **Auras apply in `BeforeDamageReceived`, are consumed in `AfterDamageReceived`.**
  The phase split makes "after a reaction nothing sticks" true without ordering
  assumptions — `Powers/ElementalApplication.cs:30-37,183`.
- **Amplifiers (Vaporize/Melt) multiply exactly one hit and are consumed with the
  aura — never persist.** They live only in `AuraPower.ModifyDamageMultiplicative`
  and are deliberately absent from `ReactionEffects` —
  `Elements/ReactionTable.cs:89-93`, `Powers/ReactionEffects.cs:20-23`.
- **Element travels on the CARD, not the damage instance** (`IElementalCard`);
  card-less damage (bombs, the Burst volley, DoT ticks) routes through
  `ElementalHit` — `Elements/Element.cs:20-34`, `Powers/ElementalHit.cs:10-23`.
- **The element a card applies is a GEM on the face, never a sentence in the
  rules box.** [USER], 2026-09-01: *"instead of saying 'applies pyro' - maybe
  make it a card indicator as well to remove text overhead? That would be a
  universal shift."* The four `KleeKeywords.Applies*` fields carry
  `AutoKeywordPosition.None`; `After` is what fed BaseLib's
  `AdditionalAfterKeywords` and made `CardModel.BuildDescription` append the
  line, so that one attribute is the whole of the removal — 114 faces across
  every sheet and both quarantined arms at once. **The TIP is untouched:**
  `CardModel.HoverTips` walks `Keywords` and never the printed text, which is
  why `Bomb` and the eight reaction previews have always hovered at `None`.
  `Vfx/ElementBadge.cs` reads the SAME keyword to hang the aura's own icon on
  `%TypePlaque` — ANCHORED to the plaque, never positioned from its rect,
  because `NCard.UpdateTypePlaqueSizeAndPosition` is deferred — so the gem, the
  tip and the sheet's cadence are one declaration. Pinned at
  `KleeTests/ElementBadgeTests.cs` and `tier0/tests/test_element_badge.py`.
- **Unpowered mirror hits re-apply Strength/Weak/Vulnerable by hand** (native
  powers gate on `IsPoweredAttack()`, which these deliberately fail) and truncate
  exactly ONCE — `Powers/SimDamagePipeline.cs:12-28`, `Powers/ElementalHit.cs:16-23`.
- **Balance constants are MIRRORED, never re-derived**; `lint_constant_parity` fails
  any numeric `const` in neither `MIRRORED` nor `UNMIRRORED` —
  `tools/lint_constant_parity.py:83,196,348-355`.
- **Per-type Harmony patching, never `PatchAll`.** One dead lookup disarms one
  patch; a class arming ZERO methods is a failure even if nothing threw; the
  `SoftlockGuards` set is `nameof` only, never literals (a literal survives a rename
  and guards nothing) — `KleeMod.cs:33-38`, `KleePatchBootstrap.cs:53-62,106-166`.
- **Exactly one `ModHelper.SubscribeForCombatStateHooks` call**, every character's
  hooks concatenated behind it (duplicate ids are silently rejected) —
  `KleeMod.cs:55-61`; pinned at `tier0/tests/test_roster_runtime_contracts.py:160`.
- **Telemetry patches read and never answer.** EB-14's selection hook
  (`Diagnostics/SelectionTelemetry.cs`) is three Prefix/Postfix pairs on the
  selection surfaces — the six grid screens share one inherited
  `CardsSelected()`, the choose-a-card screen is its own class, and hand
  selection opens no screen at all. `CardSelectCmd.PushSelector`/`UseSelector`
  is the game's automation seam and installing one would pick FOR the player,
  so it is banned mod-wide by
  `tier0/tests/test_eb14_selection_hook.py`. `PlayTelemetry.cs` itself stays
  Harmony-free by design (`test_track_b_curves.py`).
- **Once-per-play means `cardPlay.IsFirstInSeries`** — card hooks fire once per
  replay, the sim grants once per `play_card` — `Powers/ElementalApplication.cs:74-95`.
- **Never `new()` an `AbstractModel`, never hand a CANONICAL model to a mutating
  command.** ModelDb builds canonicals itself; resolve lazily via `ModelDb.GetById`
  — `Powers/ElementalApplication.cs:44-58`.
- **Mutable power fields must be deep-cloned** — `MutableClone` is a
  `MemberwiseClone`, so every bombed enemy would share one list
  (`Powers/BombPower.cs:88-96,121-124`).
- **Loc keys are `Id.Entry`, BaseLib-prefixed** (`KABOOM` → `KLEEMOD-KABOOM`). Plain
  `CardModel` stubs declare loc in `KleeMod.InjectLocStrings`; `CustomCardModel`
  subclasses use an `ILocalizationProvider.Localization` override —
  `KleeMod.cs:74-93`, `Diagnostics/KleeSelfCheck.cs:490-496`.
- **Loc encoding: SmartFormat uses SINGLE braces, square brackets are BBCode.**
  `{{Damage}}` renders literally; `[Block]` throws "Found end tag center" —
  `KleeMod.cs:76-89`, enforced at `Diagnostics/KleeSelfCheck.cs:544-563`.
- **Every pck lookup funnels through `KleePck.Path`, which returns null on a miss**
  so callers degrade to base behaviour — `KleePck.cs:20-24,30-45`.
- **Visuals read state, never own it**; cached node values are display-only, and
  bridges must be inert (not throw) when a node is absent — `Vfx/GaugeBridge.cs:34-38`.
- **A preview reads the resolution's own accessor, never its own arithmetic.**
  The three creature-tracked bridges (`Vfx/GaugeBridge.cs`,
  `Vfx/SalonVisualsBridge.cs`, `Vfx/TurnEndPreviewBridge.cs`) all share
  `Vfx/TrackedDisplayBridge.cs` and all print numbers computed by the code that
  resolves them — `SalonMemberPower.TickValue`, `KurageSummonPower.PulseDamage`.
  The end-of-turn docket goes one step further: the four sources it names ARE
  `Powers/TurnEndAttribution.cs`'s `Order`, the same list `TurnEndSequencer`
  walks, so the display cannot name them in an order they are not fired in
  (EB-53/N1; pinned by `test_the_turn_end_sequence_is_the_sims_order` and
  `test_the_sequencer_walks_the_table`).

## 4. Rulings that shaped it

- **R13** (`klee-mod/DECISIONS.md:1905`) — every concrete `PowerModel` here
  resolves to an icon that EXISTS in the merged pck, or is listed in
  `KleePowerIcons.IconExempt` with a reason; reflection check at boot
  (`Diagnostics/KleeSelfCheck.cs:397-436`).
- **R52** (`tier0/DECISIONS.md:1314`) — Kokomi heals no HP, ever; her sustain is
  prevention. Binds every Kokomi power that would otherwise grant healing.
- **R59 / R60 / R61** (`tier0/DECISIONS.md:1777`, `:1796`, `:1813`) — the shop's two
  colorless slots carry companions: BOTH slots are Uncommon-or-Rare at renormalized
  odds (`SlotOneUncommonOdds` / `SlotTwoUncommonOdds`, both mirroring
  `SHOP_COMPANION_RARITY_ODDS`) and differ by nation only; the patch REDIRECTS only,
  so `ColorlessCardPool` stays populated for its six non-shop consumers; and pricing
  must match tier 0.5's model of the same channel —
  `Patches/MerchantCompanionSlots.cs`. **[USER] 2026-08-10** restored slot 2's floor
  (R116/NC-10 had removed it, `CONSTANTS_VERSION` 9) and deleted the base-colorless
  last rung: an unfillable slot is now OMITTED, matching `tier05/shop.py`.
- **R69** (`tier0/DECISIONS.md:2164`) — the Orobas upgrade DISPLAYS as "Dodoco
  Tales"; the C# type stays `ExplosiveFrags`, because renaming it moves the runtime
  relic id and that is a co-op desync
  (`Relics/UpgradedStarterRelics.cs:99-118,148`).
- **R71** (`tier0/DECISIONS.md:2267`) — `SPOTLIGHT_BASE_MULT = 1.5` ratified;
  mirrored as `SpotlightSystem.GuestCastBaseMultiplier`.
- **R72** (`tier0/DECISIONS.md:2313`) — Kaboom Beetle Swarm snapshots bombed-state
  **at cast**, clears it in a `finally`, and falls back to a live read outside a
  play so previews stay honest.
- **R80** (`klee-mod/DECISIONS.md:2161`) — Charge is never spent;
  `ChargeResource.Spend` is a documented no-op, not an oversight
  (`Powers/KokomiResources.cs:124,154`).
- **R85 / R86** (`tier0/DECISIONS.md:2699`, `:2757`) — Curtain Call's six powers are
  ACTIVITY-triggered, never per-turn, and their per-turn windows reset in
  `BeforeSideTurnStart` (Salon upkeep spends Encore in `AfterPlayerTurnStart`) —
  `Powers/CurtainCallPowers.cs:8-21,61-70`.

## 5. Traps

- **Three R-namespaces collide.** `KleeSelfCheck` has its own rule labels R1-R13/R19
  (`Diagnostics/KleeSelfCheck.cs:110-117`), `validate.ps1` uses S1-S7, DECISIONS
  rulings are R1-R97. "R3a" in a log line is a self-check rule, not a ruling; `R4`/`R5`
  come from a `rule` parameter, so grepping `Fail("R` misses them.
- **`KleeAssetPathFallback.cs` looks like dead placeholder scaffolding and is
  load-bearing** — renamed from `KleePlaceholderArt` precisely because a name
  predicting its own deletion invites deletion; 9 asset paths have no other source
  (`KleeAssetPathFallback.cs:11-40`).
- **`ProgressSaveManager_EpochCheck_Patch` is a CANARY, not the fix.** If its warn
  line appears, BaseLib's `ICustomModel` guard stopped applying; deleting it removes
  the detector — `KleeMod.cs:396-414`.
- **The self-check must never throw** (`Diagnostics/KleeSelfCheck.cs:29-31`) and runs
  as a `Priority.Last` postfix on `ModelDb.Init` so it sees BaseLib's loc injection
  (`:568-583`).
- **Phase, not magnitude, is the usual divergence.** `lint_constant_parity` stays
  green on `ShatterDamage`/`VulnerableTakenMult` while a hook move re-opens a 30-50%
  gap; the phase ledger is `tier0/tests/test_reaction_phase_parity.py:1-16`.
- **`cardPlay.Card.Owner` is null on real paths** (autoplay, token plays); the NRE
  lands in an async continuation → black screen, no crash dialog. Guard every
  card-played hook — `tier0/tests/test_card_play_hook_guards.py:1-16`,
  `Powers/ElementalApplication.cs:78-83,113-114`.
- **`Cards/Generated/` is machine-written: DO NOT EDIT** — change the sheet and regen
  (`Cards/Generated/BarbaraShiningIdol.cs:1-7`). Same for
  `Diagnostics/FurinaParityVectors.cs:14-29`, whose tables the Python suite parses.
- **Bridges are inert when their scene node is missing, which is undebuggable.**
  `KleeSceneTelemetry` makes that loud at boot; `%Facing` is the live example —
  `Diagnostics/KleeSceneTelemetry.cs:56-75`.
- **Mirror `%Facing`, never `%Rig` (animated) and never `Visuals.Scale`** — the latter
  inverts the hitbox `UpdateBounds` reads back — `Vfx/CreatureFacing.cs:32-42`.
- **The bomb-suppression latch lives on the Creature via `SpireField`**, not in
  combat-keyed statics, which reload or a second live combat silently reset —
  `Powers/BombPower.cs:98-108`.

## 6. Reading order

1. `klee-mod/KleeCode/KleeMod.cs` — init order, the loc contract, and the three
   softlock patches with their findings written out.
2. `klee-mod/KleeCode/KleePatchBootstrap.cs` — how patches arm and how failure reports.
3. `klee-mod/KleeCode/Diagnostics/KleeSelfCheck.cs` — the boot invariants, each one a
   bug that shipped.
4. `klee-mod/KleeCode/Elements/ReactionTable.cs` + `Powers/ElementalApplication.cs` —
   the reaction system and its tier0 mirror discipline.
5. `klee-mod/KleeCode/Powers/ElementalHit.cs` + `Powers/SimDamagePipeline.cs` — the one
   damage pipeline every card-less hit must use.
6. `tier0/tests/test_roster_runtime_contracts.py` + `tools/lint_constant_parity.py` —
   what the suite holds shut on this module's behalf.
