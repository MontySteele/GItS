> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/playtest2-triage-2026-07-28.md` — new path: `docs/archive/playtest2-triage-2026-07-28.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Playtest 2 triage — Furina co-op feedback + deck review (2026-07-28)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Source: co-op playtest 2 (Monty = Kokomi, guest pilot = Furina) plus Monty's own
sweep of the Furina deck. Items are triaged into three groups per the red-pen
note of 2026-07-28. Groups 1 and 2 are sprint-ready for delegation; Group 3
stays with the design table.

Where a Group 1/2 item cites file:line, the diagnosis was verified in code on
branch `take-a-bow-consolidation` before triage — these are not guesses.

---

## Group 1 — BUG-FIX SPRINT (delegate)

### B1. Thunderous Ovation ignores Fanfare — CONFIRMED, root cause found
Report: "just gave 6 block." Sheet says `block 6, bonus_formula: 1_per_2_fanfare`
(docs/furina-cards.yaml:438). Generated C# is a flat `BlockVar(6)` with no rider
(klee-mod/KleeCode/Cards/Furina/Generated/ThunderousOvation.cs:44,62).

Root cause: every calc-rider predicate in tools/gen_klee_cards.py gates on
`eff.get("op") != "damage"` (fanfare_calc_rider ~:1298, likewise charge/encore).
Thunderous Ovation is the first card to hang a fanfare rider on a **block** op
(Curtain Call C, R85 C→R promotion), so the generator dropped it silently.

Fix: extend the fanfare rider to block ops through the same calculated-var path
block already uses elsewhere (gentilhomme_usher renders `{CalculatedBlock:diff()}`,
so the rail exists). AND close the silent-drop class: the generator must treat an
unexpressed `bonus_formula` as a named BLOCKER, never emit the base number alone
(structurally-invisible-defects rule: this escaped because no lint owned it).
Sim side already implements the rider — C# regen + parity check after.

### B2. Leading Role never discounts — CONFIRMED, both user hypotheses correct
`SpotlightDiscountPower.TryModifyEnergyCostInCombat` skips cards with
`originalCost <= 0`, but `SpotlightSystem.NotePlay` increments the
plays-this-turn counter for EVERY Spotlighted play (SpotlightSystem.cs:441-454,
:319-327). And `EtherealSpotlight` is an `ICharacterCard` with
`CharacterId: "furina"` (Cards/Furina/SpotlightCards.cs:16), so under Center
Stage the free token the relic adds every turn IS a Spotlighted Furina card.
Net: the 0-cost token (or any 0-cost play) consumes the "first Spotlighted
card" flag while being ineligible for the discount. The power reads as dead.

Proposed fix (default, small semantic call — flag in sprint log): the discount
attaches to the first Spotlighted card **with printed cost ≥ 1**; cost-≤0 plays
neither benefit nor consume. Keep the Fanfare-minting side of NotePlay
unchanged. Mirror the semantics in tier0's spotlight_discount so sim and mod
agree, and update the card/power text if the final wording warrants it.

### B3. Lasting Impression exhaust — verify render, likely text-only
Sheet has `exhaust: true` (furina-cards.yaml:78); C# emits
`CanonicalKeywords => CardKeyword.Exhaust` (LastingImpression.cs:40), same
pattern as all 30 exhaust cards, so behavior should be the base game's.
The description string does NOT contain the word "Exhaust"
(LastingImpression.cs:47). Verify in-game whether CanonicalKeywords renders a
keyword banner; if the face genuinely doesn't say Exhaust, fix the generator's
description emission for all exhaust cards at once, not just this one.
(User ruling: "if it exhausts, it's fine" — so this is a legibility fix.)

### B4. Grand Salon scope — verify "damage only" against the v2 intent
Playtest read: only member damage scaled. The salon-rework plan says
`salon_damage_up` becomes "+N to member NUMERIC effects"
(docs/archive/furina-salon-rework-plan.md:41), and tier0 applies it generally
(tier0/engine/effects.py:672,677 — both tick paths). Check whether C#'s
`SalonDamageUpPower` (Powers/SalonPowers.cs:325) reaches Usher's block ticks
and Chevalmarin's hydro application, or only damage. If C# is damage-only,
that's a sim/mod parity bug — fix C#, and rename/retext the power so it says
what it does. (The NUMBER change is A10 in Group 2.)

### B5. Salon deploy cards must say WHO (card text + tooltip, not new UI)
Six deploy cards render the same boilerplate "Add 1 typed Salon Member(s).
Maximum 3; a full stage bows its OLDEST member out…" with no member name.
Defect grammar ruling: the card face names WHO it summons; the member's
abilities (tick + bow payoff) live in a tooltip keyword; the face drops the
cap-mechanics paragraph. Affects: salon_debut, gentilhomme_usher,
surintendante_chevalmarin, mademoiselle_crabaletta, overflowing_hospitality,
dress_rehearsal, endless_waltz, an_invitation (all `member:` effects).
Generator text-template + localization/tooltip work; the on-screen member
display rework is Group 3 (D1).

Sprint gate: full repo pytest from root, regen + build validate, harmony
bite-check where co-op behavior is touched (no sim backstop for co-op), sweep
the four hand-maintained sheet projections (sheet-projections-drift).

---

## Group 2 — CARD-ADJUSTMENT SPRINT (delegate; numbers below are the
2026-07-28 red-pen and may be implemented as ruled)

| # | Card | Ruling |
|---|------|--------|
| A1 | Curtain Cue | Rarity common → **uncommon** (equivalent Official effects live at U). |
| A2 | Limelight | Rarity common → **uncommon**, add **Exhaust** (self-replacing Velocity piece). |
| A3 | Macaron Break | Upgrade also raises Block to **3** (furina-upgrades.yaml delta). |
| A4 | Rising Tide | **CUT** from the pool. (Pool count / distinctness projections must be re-swept.) |
| A5 | Undercurrent | Rework (ruled 2026-07-28): retype skill → **ATTACK**, 2 energy, "Deal 2 damage to ALL enemies **3 (5) times**" — Furina is short on multi-hit attacks. Drop `skill_tag`. Note: this removes a member of the hydro mass-application WATCHLIST cell (redpen flag 8: undercurrent / rain_of_roses / guest_neuvillette_judgment) — re-scope that cell's measurement to the remaining two. |
| A6 | Singer of Many Waters | Heal 14 → **6 (8)**. Stays Rare + Exhaust. |
| A7 | Unheard Confession | Rework: lose the heal; becomes cost **2 (1) POWER**: "Gain 1 Block whenever Fanfare changes amount." New power + DSL trigger (fanfare-delta hook) in tier0 AND C#; the biggest item in this sprint. |
| A8 | Crashing Waves | Cost 2 → **1**. |
| A9 | Hearts Swelling | Add **Innate**. |
| A10 | Grand Salon | Amount **3 (4) → 1 (2)** (Defect parity), and per B4 it must apply to ALL member numbers, not just damage. |
| A11 | Salon Début vs Surintendante Chevalmarin | De-dupe: the **starter adds a RANDOM member**; Chevalmarin stays the specific-Chevalmarin card. Needs `member: random` support in DSL + generator + tier0. |
| A12 | NEW: salon cap-raise power (ruled 2026-07-28, ex-D2) | Capacitor parity: **1-cost COMMON power, salon cap +1 (+2 upgraded)**. Needs cap promoted from constant to per-player stat in tier0 + C#. Name "Box Seats" RATIFIED at red-pen 2026-07-28. PRE-REGISTERED: mild anti-synergy with bow payoffs (fuller stage = fewer bows) is INTENDED, Capacitor-style; if playtests read it as a trap, that's the pre-registered reason to revisit. |
| A13 | Dinner Service (ruled 2026-07-28, ex-D3; **BLOCK, not Encore** — deck is over-supplied on Encore grants) | Rework to per-member scaling payoff: "Gain 2 **Block**, plus **2 per Salon member**" (2/4/6/8 at 0-3). Shape ruled; the 2+2 numbers PROPOSED — red-pen at sprint review. Drops the fanfare archetype tag (no Encore flux anymore); solve moves sustain → block. |
| A14 | House Call (ruled 2026-07-28, ex-D3) | Rework to per-member scaling payoff: "Deal **6** damage, plus **2 per Salon member**" (6/8/10/12 at 0-3; A12 opens 14). Base 6 is RULED. Retires red-pen flag 9 (the old conditional was its subject). |
| A15 | Soloist's Solicitation (basic strike) | Damage **4 → 6** (ruled 2026-07-28): the dreadful-on-purpose strike is vestigial of a reverted design space. Sprint must rewrite the sheet comment (currently claims A1 is load-bearing per kickoff §2) and expect the A1 frontload axis to move at the next scorecard — label it as this ruling, not drift. Upgrade delta unchanged unless red-penned. |

House note for the sprint: these rulings change PROPOSED numbers that the
salon-assigned tables were measured on — re-run the quotable roster table after
landing, version-stamp, and never quote old rows against new unlabeled.

---

## Group 3 — DESIGN WORK (stays here; needs discussion or measurement first)

- **D1. Salon on-screen UI** (ruled 2026-07-28: YES, Defect-style): design
  sweep produces mockups first — small persistent member icons near Furina
  showing WHO is active, oldest (next to bow) marked. Constraint from the
  decompile: StS2 owns the band below a creature for its state display, so
  the strip lives above/beside her. RULED 2026-07-28 on the mockup
  (docs/mockups/salon-stage-d1-mockup-2026-07-28.html): LIVE tick numbers
  (not identity-only), accent hue per member (Crabaletta rose / Usher gold /
  Chevalmarin aqua), members displayed in SUMMON ORDER left→right so the
  leftmost is always next to bow. Note: summon-order display is already true
  in code — company is append-ordered and bow pops index 0
  (SalonPowers.cs:221-226), and the bridge renders company[i] at slot i — so
  the ruling ratifies existing behavior. RULED 2026-07-28: NO dedicated
  bow marker — with the order guarantee ratified, position IS the signal
  (leftmost = next to bow); the marker is redundant chrome. Teach it in the
  Salon Member keyword text instead ("the leftmost member bows first").
  Sequencing: after B4 (chip values read the post-parity scaled constants),
  alongside A12 (slot count from the per-player cap).
- **D7. Encore ribbon has a false max** (noted 2026-07-28): the bar's fill
  denominator is `RibbonVisualSpan = 20` (SalonVisualsBridge.cs:82) — a
  display-only constant chosen for looks; Encore itself is uncapped, so
  "full" is a lie at 20+ and noise below. PROPOSAL for red-pen: reframe the
  ribbon as RUNWAY — segment the fill into "turns of upkeep at the current
  stage" (1 Encore × member count per turn), render ~5 turn-segments with a
  5+ overflow, keep the raw number label. Answers "how long does my stage
  run" with a denominator that means something. RULED 2026-07-28: approved,
  rides the D1 sprint.
- **D8. Encore economy is too loose** (ruled direction 2026-07-28, playtest
  read): members spend too little Encore to matter — the bar refills faster
  than the stage drains it while the player does other things, so Encore
  trends toward a passively-full "free block" gauge rather than a resource
  under tension. Ruled direction, pick via sim: EITHER add more Encore
  SPENDING options (new sinks — pairs with the D6 deliberate-bow space,
  which is a natural Encore-cost candidate) OR make the stage drain faster
  per tick in exchange for a power bump. Before authoring: instrument Encore
  saturation in tier0 (fraction of turns dry vs full, Encore level at combat
  end — same shape as the Fanfare saturation telemetry from sheet pass 4)
  to establish the baseline the lever is judged against. Balance numbers
  need red-pen; the D7 runway ribbon makes whatever drain rate ships
  legible.
- **D2** — MOVED to Group 2 as **A12** (statline ruled: Capacitor parity).
- **D3** — MOVED to Group 2 as **A13/A14** (lane ruled: per-member scaling;
  numbers PROPOSED pending red-pen).
- **D6. Deliberate-bow design space** (noted 2026-07-28): no card today bows
  a member ON DEMAND — the bow payoffs only fire via cap overflow. Defect's
  evoke-on-demand family (Recursion et al.) has no analogue here. Open design
  space, pairs naturally with A13/A14's big-stage payoffs; no card authored
  yet, needs design + red-pen.
- **D4. Slip Backstage**: `hp_lost_this_turn` on a block card is near-dead
  (block resolves before enemy turn). Instrument first — measure how often the
  rider actually fires in tier0 before re-authoring the condition.
- **D5. Endless Waltz vs Grand Gala** (ruling recovered 2026-07-28): the two
  rare multi-summon payoffs (waltz: Crabaletta+Usher+standing salon_damage_up;
  gala: 4 deploys+Encore, Exhaust) are similar enough to WATCH — no change now,
  but they share a distinctness cell going forward. If one gets cut or merged
  later, this is the pre-registered reason.
- General co-op legibility: guest pilot found Furina's UI "extremely
  confusing" overall; B5 + D1 are the concrete halves of that.
