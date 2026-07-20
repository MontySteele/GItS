# Principles amendment batch — Furina kickoff (PROPOSED, awaiting user red-pen)

**Status: DRAFT. Nothing here is applied to
teyvat-spire-design-principles.md until ratified** (house rule: version
bumps are user calls; once red-penned this lands as the next dated entry
in the §10 amendment log). Sources: furina-kickoff-v0.1.md §12,
m7-rulings R8. Engineering for items 1, 2 and 5 already exists behind
tests (sprint 1) — the amendments codify what the kickoff ratified; the
text below is what needs your pen.

## 1. New section: the Spotlight system + `character:` schema field

Every card carries an optional `character:` field (shared schema — all
sheets; companion rows derive it from their id prefix, personal sheets
from the filename, explicit field wins). Cards with no character tag are
invalid Spotlight targets. One Spotlighted character per Furina player
at a time (per-player in co-op); designation is movable freely and
persists until moved; duplicate selectors are inert. Baseline
empowerment: +50% printed numbers (flat rate is the knob; texture lives
in cards). Self-Spotlight at a reduced rate is the solo fallback and the
primary anti-self-buff lever. A per-turn Spotlighted-card cap exists in
schema but ships OFF.

## 2. §2.2a extension (verbatim from kickoff §3.2)

"Spotlight empowerment applies to numbers only — **never turn-economy
effects**. Character-level designation touches a companion's entire kit;
if any companion ever ships a soft-control card, Spotlight must not be
the thing that upgrades it into stun economics."
*(Engine note: enforced structurally — the multiplier is plumbed into
damage, Block, and element-application counts only.)*

## 3. Guardrail 5 amendment (ratified as exception in kickoff §6; text
pending red-pen)

"≤2 new keywords per character; support-protagonists (§4.4
High-appetite or Appendix A lineage) may carry one additional keyword
via logged amendment with compensating cuts."
For the record: Columbina will pressure even the amended budget; the
amendment sanctions *one* extra, not open season — her kickoff fights
that fight.

## 4. Guardrail 2 ruling (generated companion cards)

Generated companion cards retain their element application. Stochastic,
exhausting, drafted off-element access via a personal pool is consistent
with "scarce and drafted" — explicit ruling, not silent precedent.
(Guest Star guardrails: this-combat-only; generators Exhaust;
equal-rarity clause; pulls from shared companion pool + purpose-built
Guest Star sets, never from playable characters' pools.)

## 5. Encore & Fanfare final definitions (supersede pre-design notes)

Encore: unbounded per-combat buffer (v1.6 house style), absorbs damage
after Block and before HP; potent cards carry "Spend N Encore:" cost
lines; overdraw drains true HP. **Tier 0 accounting (binding): Encore
absorption credits A4, never A3.** Fanfare: capped at %maxHP; generation
strictly activity-based (HP lost, Encore gained, Encore spent,
Spotlighted card played); **no passive per-turn accrual, ever**; a
global pool that survives Spotlight moves.
*(The supersession header on furina-predesign-notes.md Part 2 is
applied — sprint 1.)*

## 6. R8 conjunctive healing law (already enforced in code/tests)

True in-combat healing is Rare-tier AND Exhausts; below Rare, sustain
routes through Block or character-specific buffer pools; no 4-star
companion may true-heal. (Ships with this batch per m7-rulings R8.)

## 7. Roadmap addition

Fontaine 4-star companion set v0.1 (Lynette, Freminet, Charlotte,
Chevreuse at 3-card kits — the complete Fontaine 4-star bench) is in
Furina's release scope. Loaded and simming as of sprint 1.

---

### Open questions attached to this batch (not amendments; need rulings)

a. **Selector cadence vs A5:** the Ethereal Spotlight selector arriving
   each turn currently emits its own event and does NOT count toward A5
   velocity. Kickoff §2 lists "selector cadence" in the A5 rationale —
   rule whether it should count (and how) before the statline pass reads
   A5 off the sim.
b. **test_m5 fragility-shape lock** relaxed 0.6 → 0.5 majority-clustering
   after the Fontaine world change (measured 0.588 at n=40, binomial sd
   ~0.12). Bless or revert with a better lock.
c. **Fanfare cap fraction** (0.5 × maxHP) and **self-Spotlight rate**
   (1.25×) ship as flagged placeholders; both are sheet-pass sweeps and
   user picks.
