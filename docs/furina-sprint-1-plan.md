# Furina — Sprint 1 Plan ("Foundation Wave")

**Date:** 2026-07-20. **Inputs:** furina-kickoff-v0.1.md (governing),
fontaine-companions.yaml v0.1 (ratified draft), principles v1.9,
m7-rulings (R8 conjunctive healing law), Klee pass 1–3 process precedent.
**Baseline environment:** CONSTANTS_VERSION 2, DRAFTER_VERSION 2,
RUNTEMPLATE_VERSION 2, post-R8 pool.

**Sprint goal:** ship the engineering foundation from kickoff §11 so that
Furina's sheet pass 1 (next sprint) starts on working rails: schema,
Spotlight, Encore/Fanfare, skill-grade cadence, Fontaine pool loaded,
nation weighting real, achievability experiment run, Salon audit
delivered. No Furina personal-pool cards are authored this sprint (sheet
pass is gated — see "Gates" below).

---

## Track A — Schema & content plumbing

- **A1. `character:` schema field** (kickoff §11.1). Add to the `Card`
  dataclass (tier0/engine/state.py); shared schema — tag all three ship
  sheets (klee-cards, mondstadt-companions, fontaine-companions).
  Companion character derivable from id prefix; explicit field wins.
  Untagged cards are invalid Spotlight targets (enforced in Track B).
- **A2. `guest_star:` field.** Used by fontaine-companions.yaml rows but
  not yet in the dataclass — rows would throw on load. Add field; exclude
  `guest_star` cards from all reward/banner rolls (tier05/rewards.py) —
  they are personal-pool-generated cameos, never drafted.
- **A3. Load fontaine-companions.yaml**: add to `DOCS_CARD_SHEETS`
  (tier0/content/loader.py:23); nation derives from filename (existing
  mechanism). Healing-law conjunctive test must pass over the new sheet
  (expected: it contains no true heals, by construction — R8-shaped).
- **A4. Fontaine DSL asks** (flagged inline in the yaml):
  `reaction_triggered_this_turn` predicate, `block_next_turn` op,
  `shatter_bonus` power. All three are small; implement fully with unit
  tests rather than stubbing (house convention permits stubs for pass 1;
  full implementation is cheaper than the stub here and unblocks sim).

## Track B — Furina engine systems (kickoff §11.2, §11.4)

- **B1. Character spec** `tier0/content/characters/furina.yaml` (mirrors
  klee.yaml): Hydro, **cadence: skill** (new grade — engine support in
  `effects._element_for`: only Skill/Burst-tagged cards apply element),
  declared 7-axis targets from kickoff §2 recorded in the spec, burst
  meter size placeholder (sheet-pass scope).
- **B2. Encore** (v1.6 house style): `Player.encore`, unbounded
  per-combat, absorbs damage before HP, per-combat reset; `gain_encore`
  op; "Spend N Encore:" cost-line support; Salon overdraw drains true HP
  when empty. **Tier 0 binding accounting rule (kickoff §2 harness
  note):** Encore absorption emits a distinct event credited to **A4**,
  never A3 — implemented in metrics.extract + axes.raw_axes with a
  regression test, so the rule is engine-enforced, not discipline.
- **B3. Fanfare:** capped at %maxHP (constant; Rare uncappers are
  sheet-pass scope), flat power bonus per stack. Generation strictly
  activity-based: HP lost, Encore gained, Encore spent, Spotlighted card
  played (Ovation merge). **No passive accrual path exists in code** —
  the anti-stall policy is structural. Global pool; survives Spotlight
  moves.
- **B4. Spotlight:** per-player registry (one designated character;
  duplicate selectors inert); Ethereal Spotlight selector delivered to
  hand each turn via relic hook; designation reads the target card's
  `character:` tag (untagged ⇒ invalid target); **+50% printed numbers**
  empowerment applied at card resolution. **Numbers-only enforcement at
  the engine level** (§2.2a extension): the multiplier touches damage,
  block, element-application counts — draw/energy/turn-economy ops are
  structurally unreachable by it. Self-Spotlight reduced rate ships as a
  sweepable constant (placeholder value, flagged — final number is a
  user call at sheet pass). Per-turn Spotlighted-card cap: schematized
  but **OFF** (turns on only if Tier 0 shows asymmetry alone fails §6).
  Cross-player selector passing (kickoff §11.5): **deferred** — solo
  path first, per the kickoff's own ordering.

## Track C — Draft layer & experiments

- **C1. Nation weighting made real** (kickoff §10 prerequisite):
  `NATION_WEIGHTS` currently a single-nation uniform stub; implement the
  actual 50% same-nation / 50% uniform split keyed on the run
  character's nation, add Fontaine. Version-stamp discipline applies if
  constants semantics change.
- **C2. Achievability experiment (§8, pre-registered).** P(≥N
  same-character companion cards by act 2), three arms: 2-card vs 3-card
  kits; ± Encore Performance; ± Guest Star generator. The ± arms need
  **prototype cards** — these are experiment scaffolding with explicit
  PROTOTYPE flags, not ratified designs; real versions arrive at sheet
  pass under red-pen. Registered prediction (kickoff §8) checked
  verbatim; **null results binding**. Blocks Spotlight card *tuning*
  only, not sheet drafting.
- **C3. Salon audit (check-if-solved FIRST, kickoff §11.3).** Audit
  oz_summon / witchs_flame / solar_isotoma end-of-turn-tick machinery
  against Salon requirements (off-field repeating Hydro applicator +
  Encore/HP overdraw coupling). Report before building anything; result
  gates Salon card grammar at sheet pass.

## Track D — Governance & docs

- **D1. Supersession header** on furina-predesign-notes.md Part 2
  (already ruled — kickoff §12; mechanical application).
- **D2. Principles amendment batch drafted for red-pen** as a proposal
  doc (Spotlight/`character:` §, §2.2a numbers-only extension, guardrail
  5 amendment, guardrail 2 generated-cards ruling, Encore/Fanfare final
  definitions, roadmap addition, R8 conjunctive law). **Not applied** to
  teyvat-spire-design-principles.md until user ratifies.
- **D3. Sprint report** in house decision-ready format: findings, honest
  gaps (UNAPPLIABLE/deferred), asks for chat/user rulings.

---

## Gates & ratification flags (things that need YOU)

1. **Statline red-pen (kickoff open item 5).** Systems are ratified;
   the statline sign-off on the kickoff doc is still pending. This
   sprint's engineering doesn't tune numbers against it, so work
   proceeds — but **sheet pass 1 must not start** until you red-pen §2.
2. **Principles amendment batch (D2)** — drafted this sprint, lands only
   on your ratification (next version bump).
3. **Self-Spotlight reduced rate** — ships as a constant with a
   placeholder; the sweep and your pick happen at sheet pass.
4. **Burst design + meter size** — sheet-pass scope, needs a design
   session; not touched this sprint beyond the spec placeholder.
5. **Experiment prototype cards (C2)** — Encore Performance and one
   Guest Star generator exist only as flagged scaffolding; treat any
   numbers on them as throwaway. Real cards come to red-pen with the
   sheet.
6. **Fontaine kit sim findings** — the 12 cards are ratified v0.1; if
   first sim contact surfaces parity/band issues they come back as
   findings + candidate knobs, never silent changes.

## Out of scope this sprint (next waves)

- Furina 75-card personal sheet + upgrades (sheet pass 1) — gated on
  flags 1, 3, 4 and the C3 audit result.
- Spotlight card tuning — gated on C2 results.
- Cross-player selector passing (co-op) — C4-adjacent, solo path first.
- Fontaine 5-star Rares (Neuvillette et al.) — later scope, v1.7 lore
  audit first.
- C# (klee-mod) work — accumulating on the §11 handoff list.

## Definition of done

Both test suites green (tier0 ~70+, tier05), Fontaine pool loading and
drafted under real nation weights, Spotlight/Encore/Fanfare functional
with engine-enforced policy rules (numbers-only, A4 crediting, no
passive Fanfare), achievability report delivered with prediction
verdicts, Salon audit delivered, amendment batch awaiting red-pen.
