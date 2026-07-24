# Furina Legibility Sprint — Execution Log ("Read the Stage")

**Opened:** 2026-07-24. Governing doc: the "Furina Legibility — Sprint Plan"
(playtest workshop 2026-07-24). This log is the required no-chat-side-only
record. Zero gameplay/sim/sheet changes remain the rule.

**License / method note (re-recorded per standing rule):** Downfall
(`lamali292/Downfall`) and the base game are read **reference-only** — patterns
mirrored, never files copied. The game ships no source; both `sts2.dll` and
`Downfall.dll` were decompiled locally with `ilspycmd` 8.2 for reading only:
- game: `…/Slay the Spire 2/data_sts2_windows_x86_64/sts2.dll`
- Downfall: `…/steamapps/workshop/content/2868840/3747508091/Downfall.dll`

---

## Pre-flight reframing (READ FIRST)

The sprint doc's leading hypothesis — *"if Furina's cards ship static localized
strings, that alone explains the playtest report"* — **is false.** Every Furina
card already ships on DynamicVars with `:diff()` green formatting. **L-B
(static→DynamicVar conversion) is therefore essentially already done and is not
the fix.** The real defect is a **split value path**, and it lands the sprint on
the **L-A4 branch (preview/modifier hook)** — the [USER]-gated one — from the
start. Evidence below.

---

## Track L-A1 — DynamicVar contract audit (decompile-cited)

### The base-game contract (from `sts2.dll`)

`DynamicVar` carries three values (decompiled `DynamicVar`):
- **`BaseValue`** — the number used for *actual state-changing calculations*.
- **`EnchantedValue`** — base + card-intrinsic enchantment; "part of the card,"
  rendered **uncolored**.
- **`PreviewValue`** — **display only**, "the final value after all
  modifications" (its own doc-comment). Set via `UpdateCardPreview(...)` /
  `CardModel.UpdateDynamicVarPreview(...)`.

**Q1 — what makes a number render green (`:diff()`)?** *Internal, driven by
`PreviewValue`.* `:diff` resolves to `Formatters.HighlightDifferencesFormatter`
(`Name => "diff"`), whose `TryEvaluateFormat` writes
`dynamicVar.ToHighlightedString(inverse:false)`. `ToHighlightedString` compares
**`PreviewValue` vs `EnchantedValue`**: Preview > Enchanted → green, < → red,
= → default. So a number greens **iff something raised its `PreviewValue`.**

**How powers legitimately reach `PreviewValue`:** the base
`DynamicVar.UpdateCardPreview` is a **no-op**. `DamageVar.UpdateCardPreview`
sets `PreviewValue = Hook.ModifyDamage(runState, combatState, target, dealer,
BaseValue, Props, card, ModifyDamageHookType.All, previewMode, …)`. **`Hook.
ModifyDamage` is the one and only channel** by which a power/relic contributes
to a displayed damage number. (`ModifyDamageAdditive` / `ModifyDamageMultiplicative`
power overrides feed this hook.)

**Q2 — does the enemy-hover preview share that path?** Yes — hover/intent
previews render `PreviewValue` (same field, populated by the same
`UpdateDynamicVarPreview` → `Hook.ModifyDamage`, with the hovered enemy passed
as `target`). *Value-path confirmed from source; the on-screen behavior is the
L-A3 eyes-on gate, still owed.*

**Q3 — `.WithTooltip()` loc-key resolution?** Partially answered. Downfall
carries a number-owns-its-tooltip idiom via `DynamicVarExtension` /
`AbstractTooltipSource` (`PowerTooltipSource`, `RelicTooltipSource`). Exact
loc-key resolution to be pinned at L-C (tooltip re-homing) — it is not on the
L-A3 gate's critical path, so it is deferred, not skipped. DECISIONS 23
prefixing law applies when it lands.

### Why Furina's numbers lie (the split path)

Furina cards declare `new DamageVar(n, ValueProp.Move)` and print
`{Damage:diff()}` (e.g. `WarmupAct.cs:44,50`). So the **card face + hover** show
`PreviewValue` = `Hook.ModifyDamage(BaseValue)`. But Furina's signature
modifiers **never enter that hook**:

- **Spotlight mult/flat** live in `SpotlightSystem.PrintedDamage`
  (`SpotlightSystem.cs:146-157`, reading `SpotlightMultBonusPower` etc. at
  `131-144`). Those powers (`SpotlightSystem.cs:317/329/351/362`) are plain
  `Counter` powers whose amount `PrintedDamage` reads by hand — they do **not**
  override `ModifyDamage*` (confirmed: no such override in the file, and a
  hook + a manual read would double-count).
- **Card-local riders** are baked straight into the `PrintedDamage(...)`
  argument inside each `OnPlay`: `Crescendo.cs:64` `+ Fanfare/2`,
  `StandingRoomOnly.cs:72` `+ Fanfare/5`, `UniversalRevelry.cs:63`,
  `TorrentialTurn.cs:63` `+ (aura?4:0)`, `GentilhommeUsher.cs:67` Block ×3 on
  salon replacement.

`PrintedDamage`/`PrintedBlock` are called **only from `OnPlay`** (verified: every
caller is a resolution site; no display/preview/Harmony patch routes through
them). Net result:

| Number | Card face + hover (`PreviewValue`) | Resolved hit (`OnPlay`) |
|---|---|---|
| No modifier live | base | base (agree) |
| Spotlight/Fanfare/Salon live | **base (wrong, un-greened)** | `PrintedDamage(base)+riders` (larger) |

They diverge **exactly when a modifier is live** — precisely the playtest report
("even the hover-over-an-enemy preview numbers are off"). This is
static/decompile-proven; L-A3 turns it into an on-screen capture.

### The fix already exists in-repo (proof of pattern)

`FurinaResources.cs:635` — `FanfareAttackPer10Power.ModifyDamageAdditive` adds
`Amount*(Fanfare/10)` to attacks **through the hook**. Because it is a
`ModifyDamage*` override, its bonus *already* shows on the face and greens
correctly. The same idiom is used correctly by `AuraPower.cs:100`,
`BombPower.cs:148`, `FrozenPower.cs:45`, `CompanionPowers.cs:308`. The Spotlight/
Salon/per-card-Fanfare modifiers are the outliers that bypass it.

### Two fix shapes (this is the L-A4 surface — [USER]-gated)

1. **Migrate Spotlight/Salon modifiers into `ModifyDamage*` power hooks**
   (mult → `ModifyDamageMultiplicative`, flat → `ModifyDamageAdditive`),
   deleting the manual reads from `PrintedDamage`. Display + resolution then
   share the game's one path; `{Damage:diff()}` greens for free. Pattern proven
   by `FanfareAttackPer10Power` above.
2. **Card-local Fanfare/aura riders → `CalculatedDamageVar`** (the game's own
   "6 + 2×N" mechanism; `WithMultiplier(static Func<CardModel,Creature?,decimal>)`).
   Its `UpdateCardPreview` runs `Calculate(target)` **then** `Hook.ModifyDamage`
   on top, so the rider shows on the face *and* powers still stack. Constraint:
   the multiplier func must be static (reads `card`/`CombatState`, captures no
   model) — fine for `Fanfare(owner)` / aura lookups.

**Why this is [USER]-gated, not executor discretion:** it changes how every
Furina damage number is *computed*, moving magnitude onto the shared
`Hook.ModifyDamage` hot path — the doc's own L-A4 clause ("touches every
character's hot path; does not ship on executor discretion"). It is also more
than the doc's L-B "conversion pass" scoped for — closer to a modifier-hook
migration.

---

## L-A2 — Proof card (BUILT, awaiting live gate)

**Card chosen: `Crescendo`, not the doc-suggested `WarmupAct`.** Correction from
the audit: Spotlight flat/mult only touch **GuestCast (companion)** cards, and
`GuestCastBaseMultiplier = 1.5m` (`SpotlightSystem.cs:59`) is an *intrinsic*
companion multiplier — so a clean companion proof would mean migrating the whole
GuestCast transform (1.5× + mult + flat + Block) at once, not one modifier.
`WarmupAct` is a Furina own-card (CenterStage → `OutwardMultiplier == 1`) and
shows **no** Spotlight change at all, so it cannot prove anything here.

Crescendo is a Furina own-card whose only modifier is the inline `+1 per 2
Fanfare` rider — zero Spotlight entanglement — and it exercises
`CalculatedDamageVar`, which **nothing in the mod uses yet** (the genuinely
unproven path). Best single de-risking proof.

**Change (proof spike, `Crescendo.cs`, hand-edited generated file — NOT
committed, generator owns it post-L-A3):** replaced `DamageVar(8)` +
`PrintedDamage(base + Fanfare/2)` with the game's own PerfectedStrike idiom —
`CalculationBaseVar(8)` + `ExtraDamageVar(1)` + `CalculatedDamageVar(Move)
.WithMultiplier(static (card,_) => Fanfare(card.Owner.Creature)/2)`; description
token `{Damage:diff()}` → `{CalculatedDamage:diff()}`; `OnPlay` now
`DamageCmd.Attack(DynamicVars.CalculatedDamage)`.

**Result: `dotnet build` green, 0 errors** (klee.dll). By construction the var
now behaves: `EnchantedValue = CalculationBase = 8`; `PreviewValue =
Calculate = 8 + Fanfare/2`; `:diff()` greens iff Preview > 8.

### L-A3 — eyes-on gate — ✅ PASSED (live, 2026-07-24)

[USER] confirmed in live combat: Crescendo's face number is green and scales up
as Fanfare is gained. This is the load-bearing confirmation — BaseLib's
`CustomCardModel` DOES participate in the game's `UpdateDynamicVarPreview` refresh,
the `CalculatedDamageVar` renders + greens, and the fanfare slice works end to end.
The static BaseLib finding (`UpdateModifierPreview`) is now empirically confirmed.
Deploy note: full `deploy.ps1` binds fine interactively but errored in the
non-interactive shell; shipped via a targeted `mods/klee/klee.dll` refresh from the
Release build (manifest/pck/art unchanged; validate's suite gate already green).

Original recipe (for regression): static analysis proves the *var* math, but only a
live run proves BaseLib's `CustomCardModel` actually participates in the game's
`UpdateDynamicVarPreview` refresh (i.e. the pipeline includes our cards at all).
**Repro recipe** (please screenshot both states into this log):
1. Deploy the built `klee.dll`, start a run as Furina, get **Crescendo** in hand.
2. **Fanfare = 0:** card face reads **8**, default color (unmodified baseline).
3. Build **Fanfare ≥ 10** (Center-Stage plays grant +2 each). Face should read
   **13 in green** (8 + 10/2); hover over an enemy → preview **13**; the actual
   hit deals **13**, then spends 10 Fanfare. Face + hover + resolution all agree.
4. If the face does **not** update/green live → the preview pipeline does *not*
   include our custom cards, and the sprint shape changes (we'd hook the preview
   refresh). That is exactly what this gate exists to catch.

## Precondition CONFIRMED from BaseLib (the load-bearing risk, resolved statically)

The one thing static analysis of the game alone couldn't prove — that the preview
refresh runs for our *custom* cards — is settled by decompiling `BaseLib.dll`:

- `BaseLib.Abstracts.UpdateModifierPreview` is a Harmony **transpiler on
  `CardModel.UpdateDynamicVarPreview`** (the base method the game runs on cards in
  hand). It augments, not replaces — so each var's `UpdateCardPreview` (→
  `Hook.ModifyDamage` for `DamageVar`, → `Calculate` for `CalculatedVar`) fires
  for Furina/Klee cards as base-game behaviour. **The fix will preview.**
- BaseLib ships the blessed helper `CustomCardModel.MakeCalculatedDamage(baseVal,
  Func<CardModel,Creature?,decimal> bonus, int mult=1, …)`. We emit the explicit
  PerfectedStrike three-var form (identical result, and it's what the base game's
  own cards use).

Consequence for the Klee worry (2026-07-24): the refresh is a base-`CardModel`
patch, not per-character — whatever previews Furina previews Klee. A laggy Klee
*detonation* number is the bomb fuse, not a preview bug (bomb damage lives on
`BombPower`, not a card-face var). Klee card-face riders are a fast-follow, not a
threat to this fix.

## L-B (fanfare slice) — SHIPPED via the generator ([USER] approved "safe half globally")

`tools/gen_klee_cards.py` now converts every Furina own-card `N_per_M_fanfare`
damage rider to `CalculatedDamageVar` (`fanfare_calc_rider` predicate → four emit
sites: vars / OnPlay / description token `{CalculatedDamage:diff()}` / upgrade →
`CalculationBase`). Regen changed exactly the 3 generated fanfare cards:
**Crescendo, Standing Room Only, Universal Revelry.** Each now renders base +
N·(Fanfare/M) live and green, matching the resolved hit.

Scope guards (why only these 3): the predicate excludes salon-deploy cards (the
×3 replacement is the deferred entangled modifier) and only fires on the fanfare
formula (Furina-only by mechanic, so Klee's shared codegen is untouched). Dropping
the old `PrintedDamage` wrap changes no resolved number — it is identity for
Furina's own cards (Center Stage doesn't scale her numbers).

**Gates: `dotnet build` green (0 errors); full repo suite `python -m pytest -q`
635 passed** (updated the one pin in `test_roster_codegen.py` that asserted
Crescendo's old inline form).

## Status / remaining gates

- **L-A1 / precondition:** contract + custom-card refresh — **DONE, decompile-cited.**
- **L-A2/L-A3:** **✅ PASSED live** (green scaling confirmed on Crescendo, 2026-07-24).
- **L-B fanfare slice:** **SHIPPED + live-verified** (3 cards, build + suite green).
- **Fanfare slice committed:** `a1bca0d` (generator + 3 cards + test + this log).
- **`LetThePeopleRejoice` (hand-written kit Burst): CONVERTED** — same
  CalculatedDamageVar form by hand (base 8 + 1·(Fanfare/4)), description token
  `{Damage}` → `{CalculatedDamage:diff()}`. Build + full suite green (635; updated
  the `test_handwritten_furina_burst` pin). Deployed and **live-verified**: cast at
  Fanfare 28–31, the face read **15** and the AoE hit for 15 — i.e. `8 + 28/4`, both
  paths scaling off one value. (First read was "unmodified": 15 was mistaken for the
  printed base, which is 8.) One cosmetic item stays open — the 15 was reported as
  **not green**, though `DynamicVar.ToHighlightedString` compares `PreviewValue` (15)
  against `EnchantedValue` (8, pinned by `CalculatedVar.UpdateValues` →
  `GetBaseVar().BaseValue`) and should highlight. Crescendo greens on the identical
  token, so the asymmetry is unexplained; next sighting, confirm the colour before
  chasing it. Value correctness is not in question either way.
- **Follow-ups (queued, not this slice):**
  - `bonus_vs_aura` riders — `torrential_turn` (single-target, clean but shares
    Klee codegen → needs a Furina gate) and `crashing_waves` (**AoE / per-target**,
    genuinely harder to preview). Deferred within the safe half.
  - **L-A4 entangled half** — Spotlight/Salon `1.5×` GuestCast + flat + Block hook
    migration (companion cards). The bigger, separately-verified step.
- **L-C:** text re-homing — unstarted (ordering).

_Note: `tools/lint_strict_domination.py` shows modified in the tree — that is the
concurrent Kokomi v0.2 session (Sly riders), NOT this sprint. Keep it out of any
Furina commit._

### Open [USER] items
1. **L-A4 approval:** adopt the hook-migration fix (shapes 1+2) as the sprint's
   real spine, replacing the L-B "conversion" framing? This is the load-bearing
   ruling.
2. **L-A3:** run the proof card in live combat and capture both states.
3. **DECISIONS entry:** the doc's title "DynamicVar card layer" no longer
   describes the work; propose retitling to "Furina legibility: modifier-hook
   migration (PrintedDamage → Hook.ModifyDamage)". Entry deferred until commit
   (DECISIONS.md is mid-Kokomi-edit; keeping streams separate).
