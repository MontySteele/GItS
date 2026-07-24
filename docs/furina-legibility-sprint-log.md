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
- **L-B pass 2 — `bonus_vs_aura` riders: DONE (single-target only).**
  - `torrential_turn` **converted**: `CalculationBaseVar(10)` + `ExtraDamageVar(4)`
    + multiplier `static (_, target) => target != null && AuraCmd.Find(target) != null ? 1 : 0`.
    This is the shape `CalculatedVar` was actually built for — `Calculate(target)`
    gets the *hovered* creature during preview and the real one at resolution, so
    the face greens exactly when you hover an aura'd enemy. No Furina gate was
    needed after all: Klee's only `bonus_vs_aura` card (`flame_dance`) is AoE, so
    the single-target predicate simply never matches it.
  - `crashing_waves` + Klee's `flame_dance` **deliberately NOT converted**, and not
    for cosmetic reasons: `AttackCommand` resolves a `CalculatedDamageVar` **once**
    with `singleTarget == null`, while these emit a per-target `foreach` that
    re-tests `AuraCmd.Find` per enemy. Converting would collapse a per-enemy
    decision into one flat board-wide value — a real gameplay change. Pinned by
    `test_aoe_aura_riders_stay_per_target`.
  - Refactor: the four emission sites (vars / OnPlay / description token / upgrade
    target) now key off one `calc_rider` predicate, so they cannot disagree about
    which shape a card is. Regen proved it neutral — the three fanfare cards came
    out **byte-identical**; only `TorrentialTurn.cs` changed.
- **Zero-gameplay-change argument, now proven rather than assumed:** the conversion
  drops the `SpotlightSystem.PrintedDamage(this, …)` wrapper the generator puts on
  every Furina card. That wrapper is *identity* for non-companion cards:
  `PrintedDamage`'s bonus path requires `Mode == GuestCast`, and under GuestCast
  `IsSpotlighted` is true only for `ICompanionCard`; under CenterStage
  `OutwardMultiplier` returns a hard `1m`. Furina's sheet has **zero** `star`
  (companion) rows — Guest Stars are generated separately — so no converted card
  can ever have been scaled by it. This retroactively covers `a1bca0d` too.
- **L-A4 damage half — DONE (11 companion cards).**
  - **The hook migration the doc called for is the WRONG fix, and the decompile
    says so.** `Hook.ModifyDamage` applies *every* additive contribution before
    *every* multiplicative one (`Hook.ModifyDamageInternal`), whereas
    `PrintedDamage` computes `Truncate(printed × mult) + flat` on the PRINTED
    number, ahead of Strength/Vulnerable. Registering Spotlight as a
    `ModifyDamageMultiplicative` participant would fold Strength into the 1.5×
    and add the flat on the wrong side of the multiply — a real change to
    resolved damage. Rejected on those grounds.
  - **What shipped instead:** the mechanism already proven live twice. Companion
    damage renders through a `CalculatedDamageVar` whose multiplier *calls*
    Spotlight: `base + 1 × (PrintedDamage(base) − base)` ≡ `PrintedDamage(base)`.
    The arithmetic is not re-derived, it is the same function, so no resolved
    number can move. New `SpotlightSystem.PrintedDamageDelta(card)` gives it one
    home. The `PrintedDamage` wrap is removed from OnPlay in the same change —
    keeping both would apply Spotlight twice.
  - Confirmed load-bearing fact: `CreatureCmd.Damage` calls
    `Hook.ModifyDamage(..., CardPreviewMode.None, ...)`, so preview and hit share
    that hook — which is exactly why a hook-based Spotlight would have hit both
    and why removing the wrap was mandatory, not optional.
  - Scope was uniform and collision-free: all 11 companion damage cards passed
    exactly `DynamicVars.Damage.BaseValue`, one wrap each, none already using an
    `ExtraDamage` var. Furina's own cards deliberately NOT converted (the wrap is
    identity there) — pinned by `test_furina_own_cards_keep_the_identity_spotlight_wrap`.
- **Follow-ups (queued):**
- **L-A4 block half — DONE (7 cards).**
  - **Correction to the note written in `6af7a71`:** the game DOES ship a block
    counterpart — `CalculatedBlockVar`, which overrides `UpdateCardPreview` to run
    `Hook.ModifyBlock` exactly as `CalculatedDamageVar` does for damage, and reads
    `CalculationBase` + `CalculationExtra`. No custom `SpotlightBlockVar` was
    needed. Found it via BaseLib's `CustomCardModel.GainsBlock`, which tests
    `value is BlockVar || value is CalculatedBlockVar` — worth remembering that
    BaseLib's overrides name game types we haven't met yet.
  - Same identity as the damage half: `base + 1 × (PrintedBlock(base) − base)`.
    Resolution uses the base game's own idiom, lifted from `Mirage`:
    `GainBlock(creature, DynamicVars.CalculatedBlock.Calculate(target),
    DynamicVars.CalculatedBlock.Props, cardPlay)` — face and gain read one var.
    New `SpotlightSystem.PrintedBlockDelta`.
  - **Excluded, deliberately: `freminet_pressurized_floe`** — the only card doing
    both damage and block. `CalculatedDamageVar` and `CalculatedBlockVar` BOTH
    take their base from the single `CalculationBase` var, so converting both
    would compute its block off the damage base. Damage conversion wins; its block
    stays inline. Pinned by `test_card_doing_both_damage_and_block_converts_only_its_damage`.
- **Known remaining gap (new, small): `prune_witch_hunt`.** Its block is a
  conditional-branch literal (`PrintedBlock(this, 5m)`), not a `Block` var, so the
  card text prints a hard "5" while the gain scales. There is no var to green;
  closing it means introducing per-branch vars for conditional effects — a
  different, larger change than this sprint's conversions. Logged, not attempted.
- **Salon replacement multiplier — DONE (6 cards), [USER]-ratified 2026-07-24.**
  The ruling asked for was granted ("proceed with both items"), so the shared
  predicate was written rather than the second expression.
  - **`SalonMemberPower.StageIsFull(companyCount)` is now the one home of the
    rule.** `Deploy`'s loop condition became a call to it (byte-identical test,
    zero behaviour change), and the face reads it through
    `WillReplace(owner, deploys)` — the closed form, with the proof in the
    doc-comment: iteration *i* of `Deploy`'s loop sees a company of
    `min(Count + i, MemberSlots)`, so `StageIsFull` first turns true at
    `i = MemberSlots − Count` and stays true; testing the LAST iteration
    therefore answers for all of them. No simulation, no second rule.
  - **`ReplacementDelta(card, deploys, multiplier)`** returns
    `base × (multiplier − 1)` when a bow is coming, so the CalculatedVar's
    `base + 1 × delta` lands exactly on `base × multiplier` — the number these
    cards already resolved. Base is read live off `CalculationBase`, so it stays
    upgrade-safe.
  - **The timing rule, which is the load-bearing part:** `WillReplace` reads
    PRE-PLAY company size, but a card's own deploys grow the company mid-
    resolution — a 4-deploy card mutates the count as it goes. So each converted
    body captures its scaled value in a local at the TOP of `OnPlay`, before the
    first `Deploy`, which is precisely the state the preview read. Spending the
    var *after* the deploys would answer a different question than the face did.
    Pinned by `test_salon_scaled_value_is_captured_before_the_cards_own_deploys`.
  - **Converted (6):** `gentilhomme_usher` (Block ×3, `CalculatedBlockVar`),
    `dress_rehearsal` (draw ×2), `grand_gala` + `overflowing_hospitality` +
    `surintendante_chevalmarin` (Encore ×2), `endless_waltz` (power amount ×2).
    The ×2 numerics use the base game's plain `CalculatedVar` — it takes a name
    in its constructor and its `UpdateCardPreview` sets `PreviewValue =
    Calculate(target)`, so any named var can green; only Damage/Block have typed
    subclasses (which additionally run their `Hook.Modify*`).
  - **Two traps found and guarded.** (a) `DynamicVar.IntValue` is `(int)BaseValue`,
    and a `CalculatedVar`'s `BaseValue` is only its *base term* — so bodies must
    call `Calculate(...)`, never `IntValue`, or the scaling silently vanishes.
    (b) The draw var is named **`DrawCards`, not `Cards`**: `DynamicVarSet.Cards`
    is a typed accessor that casts to `CardsVar`, so a `CalculatedVar` under that
    name would throw on any read through the property. `Encore`/`PowerAmount`
    have no typed accessor, so they keep their natural names.
  - **One conversion per card** (`test_only_one_salon_number_per_card_converts`):
    every calculated var — typed or plain — takes its base from the single
    `CalculationBase`, so a second would compute itself off the first one's base.
  - **Excluded, deliberately:** `mademoiselle_crabaletta` — its deploy count is
    itself an upgradeable var, so the closed form has no static deploy count to
    stand on; it stays inline rather than guessing.
  - **Known remaining gap:** `salon_debut`'s Encore is added by the `add` upgrade
    delta, not by a sheet effect, and prints inside `{IfUpgraded:show:…|}`.
    Nesting a `{Encore:diff()}` token inside that swap is not expressible, so its
    upgraded Encore still prints unscaled. Logged, not attempted.
  - Suite **646**. `dotnet build` 0 errors; parity lint OK (8 cards).
  - _Superseded analysis (kept for the record):_
    **Salon ×3 replacement multiplier — ANALYSED, needs a [USER] ruling.**
    Unlike Spotlight, this one is not a pure function of pre-play state: the
    generator scales by `salonReplacements > 0`, and `SalonPowers.Deploy`
    increments that counter only when the company is already at
    `SalonConstants.MemberSlots` *at the moment of each deploy within this card's
    own resolution*. A card deploying four members mutates the count as it goes.
    **But it is still predictable in closed form:** a replacement occurs iff
    `Count(owner) + deploysSoFar > MemberSlots`, so a preview needs only the
    current company size and how many deploys precede the scaled effect on that
    card — no simulation. The catch is that this introduces a *second*
    expression of the replacement rule, which is precisely the split-path disease
    this sprint exists to cure, unless `Deploy` is refactored to consume the same
    predicate. That refactor touches resolution order on salon cards, so it wants
    red-pen before it is written, not after.
  - **L-C text re-homing — SCOPED, costs more than the doc assumes.** Only 4
    generated cards (+ the hand-written Burst) carry a trailing rider sentence,
    so the surface is small. The blocker is the tip API: every
    `HoverTipFactory` entry point is TYPED — `FromKeyword`, `FromPower`,
    `FromPotion`, `FromOrb`, `FromEnchantment`, `FromAffliction`. There is no
    free-text constructor, and a shared `Fanfare` keyword tip cannot carry a
    per-card rate ("1 per 2" vs "1 per 4"). Re-homing therefore needs a custom
    `IHoverTip` implementation in the mod. Feasible — `KleeCardTooltips.ForCard`
    already exists as the injection point and several cards already override
    `ExtraHoverTips` — but it is a new UI type plus a card-text change on 5
    cards, i.e. design surface. Not attempted unilaterally.
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
