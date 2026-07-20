# Furina — Character Kickoff Doc v0.1

**Date:** 2026-07-20. **Status:** kickoff declarations per template §3 —
statline and systems ratified this session; card sheet not yet begun.
**Inputs:** principles v1.9, furina-predesign-notes.md (Part 2 resource
design SUPERSEDED where noted below by the v1.6 amendment and this doc),
Appendix A (Columbina staircase context).

**One line:** the Regina of All Waters directs the stage — her numbers are
modest, her cast is not.

**Strategic purpose (why Furina before anyone else):** she beta-tests
Columbina's driver machinery one character early. Every Spotlight system in
this doc is deliberately the scoped-down version of Appendix A's
requirements: character designation, character-tagged cards, cross-player
designation passing, empower-beyond-printed-stats. If it works for Furina,
Columbina inherits proven parts.

---

## 1. Identity declarations (template §3.1)

- **Element:** Hydro. **Cadence: Skill-grade** — only Skill/Burst-tagged
  cards apply Hydro; higher base numbers than catalyst-grade *within her
  low-statline identity*. Salon members are her repeatable application
  engine (see §5).
- **Companion appetite: Standard.** Spotlight is draft-gated high-ceiling,
  not her only plan; the self-Spotlight fallback means companion-poor runs
  are dimmer, never bricked (Pillar 4).
- **Burst:** kit-Burst per v1.9 (granted on meter fill, Retain, re-grant on
  refill; never in pool). Meter size and card design deferred to the sheet
  pass; her particle economy leans on Salon application and Encore spend.

## 2. Statline declaration (7-axis, declared before any card is written)

| Axis | Target | Rationale |
|---|---|---|
| A1 Frontload | **1.0–1.5** | The load-bearing weakness. Dreadful, by design. |
| A2 Scaling | ~3.0 | Fanfare gives her a curve; her scaling *identity* routes through others. Declared on starter+median per acceptance law — companion-dense decks measuring higher is the design working, not a violation. |
| A3 Block economy | ~2.5 | Encore is not Block; see harness note. |
| A4 Sustain | **4.3** | The healing metric's protagonist. Encore absorption + rare-tier true heals. |
| A5 Velocity | 3.7 | Encore-spend tempo, selector cadence. Strong, deliberately sub-elite (heuristic: exactly two elite axes). |
| A6 Utility | **4.2** | Hydro aura uptime (Klee's dream co-op partner), party buffs, debuff texture. |
| A7 Setup tax | ~2.0 | Second declared weakness. Punisher fights should genuinely hurt. |

**Harness note (Tier 0, binding):** Encore absorption credits **A4**
(chip-reduction), never A3. Without this accounting rule she grows a
phantom third elite axis and the declaration is unfalsifiable.

## 3. Signature subsystem: Spotlight (the one Ghostflames-scale system, §3.2)

**Subsystem budget ruling:** Spotlight is THE subsystem. Encore and Fanfare
are resource counters (cheap). Salon rides existing summon machinery
pending the check-if-solved audit (§5). Pneuma/Ousia is **pure flavor,
zero mechanics** (ratified). Nothing else novel ships in her v1.

### 3.1 Designation (character-level)

- Every card gains a **`character:` schema field** (shared schema change,
  not Furina-private — Columbina inherits it). Companion cards carry their
  character implicitly; Klee's cards tag Klee; Furina's tag Furina. Cards
  with no tag are **invalid Spotlight targets** (selector greys them out).
- **Delivery:** her starting relic adds an **Ethereal Spotlight selector**
  card to hand each turn. Applying it to a card in your hand reads that
  card's character tag and designates that character. In co-op, the
  selector may instead be passed to a teammate, who applies it to one of
  their own cards (first cross-player designation — Appendix A.4's
  engineering, arriving early).
- **Movable freely; persists until moved.** Designation lasts until
  re-aimed; moving costs only the (free) selector play. Commitment is
  rewarded through Fanfare throughput (§4), never enforced through rules —
  drafting a second companion or a 5-star splash must never feel like a
  pre-nerfed pick.
- **Global registry:** one Spotlighted character per Furina player at a
  time, tracked globally; duplicate selector cards are inert. Registry is
  per-player in co-op (two Furinas = two independent Spotlights).

### 3.2 Empowerment

- **Baseline (v1, boring on purpose):** Spotlighted character's cards get
  **+50% printed numbers** — damage, Block, element-application counts.
  Flat rate is the knob; texture lives in cards, not the baseline.
- **§2.2a guard (goes into principles verbatim):** Spotlight empowerment
  applies to numbers only — **never turn-economy effects**. Character-level
  designation touches a companion's entire kit; if any companion ever ships
  a soft-control card, Spotlight must not be the thing that upgrades it
  into stun economics.
- **Self-Spotlight = the solo fallback, at reduced rate** (Appendix A.4
  mandate, satisfied structurally): full rate on a companion character or
  co-op teammate; reduced rate (number TBD at sheet pass; sweep it) on
  Furina herself. The asymmetry is the primary anti-self-buff-dominance
  lever and is legible on card text.
- **Held in reserve, schematized but OFF:** per-turn Spotlighted-card cap
  (raiseable via powers as design space). Turns on only if Tier 0 shows
  asymmetry alone fails the §6 acceptance criterion.
- **Texture design space (ratified, uncommon/power tier):** "first
  Spotlighted card each turn costs 1 less," "first Spotlighted card each
  turn draws 1," etc. — cheap riders on top of the flat baseline.

## 4. Resources: Encore & Fanfare

**Supersedes furina-predesign-notes Part 2 where they conflict** (that doc
predates the v1.6 amendment).

- **Encore** (per v1.6): **unbounded per-combat** buffer pool (Osty/
  Regent-star house style — governed by opportunity cost, made safe by
  per-combat reset). Her "healing" effects grant Encore; it absorbs damage
  before HP; potent cards carry "Spend N Encore:" cost lines; **Salon
  overdraw drains true HP when Encore is empty** — greed is legal and
  priced. **True healing is Rare-tier AND Exhausts** (Pneuma/Singer
  identity; tightened from v1.5's disjunctive form by user ruling — see
  m7-rulings R8).
- **Fanfare:** **capped at %maxHP** (Rare uncappers at nasty setup cost);
  stacks grant flat power bonuses. **Generation is activity-based, never
  passive:** HP lost, Encore gained, Encore spent, and — the Ovation merge
  — **each Spotlighted card played grants Fanfare**. No per-turn passive
  accrual, ever (passive accrual = stall payoff; the healing policy exists
  to kill exactly that).
- **Fanfare is a global pool on Furina** — it survives Spotlight moves.
  Commitment texture comes from throughput (a deep single-partner kit
  plays more Spotlighted cards per turn), not from reset punishment. The
  formerly-proposed "move Ovation" uncommon is unnecessary and cut.
- **Co-op:** partner HP/Encore flux counts toward Fanfare (her Genshin
  identity; first ally-coupled mechanic). **Audit at sheet pass:**
  exclude or discount self-inflicted partner damage (Klee's Hot Hands)
  or Fanfare farms itself.

## 5. Salon Members

Off-field Hydro application engine (her repeatable aura source under
Skill-grade cadence) with HP-drain overdraw per §4.

**Engineering directive — check-if-solved FIRST:** audit Necrobinder/Osty
and BaseLib summon machinery before building anything. Salon ships on
existing rails or it ships smaller. (House norm; 3-for-3 last time.)

## 6. Keyword budget (guardrail 5 amendment — RATIFIED by user)

Census: **Spotlight, Encore, Fanfare = 3 named keywords** vs guardrail 5's
≤2 (Klee: Bombs, Sparks = 2). Ratified as a deliberate, logged exception:
support-protagonists carry structurally more machinery, and Furina pays
for the third keyword with flavor-only stances, zero new reaction content,
and Salon riding existing rails.

**Proposed principles amendment text:** guardrail 5 becomes "≤2 new
keywords per character; support-protagonists (§4.4 High-appetite or
Appendix A lineage) may carry one additional keyword via logged amendment
with compensating cuts." Note for the record: Columbina will pressure even
the amended budget (she touches every Nod-Krai mechanic); the amendment
sanctions *one* extra, not open season — her kickoff fights that fight.

## 7. Archetypes (template §3.3)

1. **Salon** — default plan; off-field Hydro engine + modest personal
   damage; the solo floor.
2. **Spotlight** — draft-gated high-ceiling; commit to companion depth
   (or your co-op partner) and direct the stage. Allowed to be luck-gated;
   that is what the slot means.
3. **Fanfare** — tempo/velocity plan; the drain→refill→spend flux cycle.

Card-slot competition separates them: Salon wants member cards and Encore
generation; Spotlight wants companion depth and selector payoffs; Fanfare
wants flux accelerants and spend payoffs.

## 8. Acceptance criteria (pre-registered, sim-enforceable)

1. **Self-carry is not the median-best plan:** at median draft quality,
   Salon and Spotlight archetype winrates must beat the self-carry
   (Encore/Fanfare-pumping-own-kit) package. Self-carry may own the
   ceiling when the draft hands it cracked Rares — lean-in reward, not
   default plan.
2. **The delete-test applies to her unmodified:** deleting Furina's cards
   from a winning Spotlight deck must gut it (her cards are the mult). If
   companions win anyway, that is SUPPORT_CARRY — real failure, even for
   the support character. **No detector carve-outs.**
3. **Standard floors:** strict relevance ≥35%/archetype; winrate bands at
   ≥1000 fights; identity heuristic on starter+median, never monoculture.

**Pre-registered achievability experiment (blocks Spotlight card tuning,
not sheet drafting):** P(≥N same-character companion cards by act 2)
under nation-weighted rewards, swept over 2-card vs 3-card Fontaine kits,
with and without Encore Performance (§9) in the drafted deck, and with
and without Guest Star generators (§9) — three arms: duplication lifts the
committed archetype's ceiling; generation lifts its floor; the bet is that
neither substitutes for drafted depth.
**Registered prediction:** 3-card kits alone put one-character depth 4+ at
"reachable but luck-gated" (correct for the slot); duplication separates
the archetype's median from its ceiling. Null results binding as usual.

## 9. Personal-pool design space (pre-sheet notes)

- **Encore Performance** (duplication): "add a copy of a Spotlighted card
  to your deck/hand" — the archetype's kit-deepener and Columbina's replay
  grammar on schedule. **Watchlist notes:** duplicating a 5-star Rare is
  copies-of-one-support (does not break banner scarcity); duplicating an
  amp-booster (Durin-analogue) goes on the **amp-cap watchlist** —
  bounded in principle by the iron rule, confirm in provenance logs.
- **Guest Star suite** (generation — user design, ratified this session):
  personal-pool cards that create companion cards for this combat only,
  Discovery-class machinery. Four binding guardrails: this-combat-only;
  generators Exhaust; equal-rarity clause (sub-Rare generators cannot
  create 5-star Rares — banner untouched); pulls from the shared companion
  pool + a purpose-built Guest Star set, NEVER from playable characters'
  pools (cadence rules live on the character dial — generated playable
  cards would have undefined element behavior). Guest Star set v0.1: 2–3
  Neuvillette cards at common/uncommon, support-shaped, explicit
  applies_element flags, personal-scoped and banner-exempt (temporary
  cameos). Generated cards are legal Spotlight targets — this is
  Spotlight's bricking mitigation, the soft form of Appendix A.3.
  Tea-party flavor is the identity: she invites guests; the Iudex always
  comes.
- Selector-payoff cards ("if you moved the Spotlight this turn…" /
  "…if it hasn't moved this combat"), Fanfare spenders, Encore-cost
  potent cards, rare-tier true heals.
- Naming sources per §3.6: constellations for rares, talent names for
  relics, voice lines for flavor. Her material is theatrical; it will
  write itself.

## 10. Fontaine companion pool (scope added to roadmap by this kickoff)

- Nation-weighting (50% same-nation) requires a **Fontaine 4-star set
  v0.1** to exist. **Authored at 3-card kits** (per character: ~common
  enabler + common attack-ish + uncommon payoff) — §4.2 permits it, and
  Spotlight's depth commitment justifies deeper wells. Distribution shape
  changes, power grade does not; Klee players see no power warp.
- **Roster RATIFIED: all four Fontaine 4-stars — Lynette (Anemo), Freminet
  (Cryo), Charlotte (Cryo), Chevreuse (Pyro).** That is the complete
  Fontaine 4-star bench (user ruling; nation rosters are uneven in the
  source material — Mondstadt/Liyue are unusually deep, everyone else is
  thin, and this recurs for every later nation including Nod-Krai).
- **Narrow-deep is pro-Spotlight by structure:** Mondstadt spreads the 50%
  nation slot across ~10 characters at 2-card kits; Fontaine concentrates
  it on 4 at 3-card kits. Same-character depth achievability (§8) should
  read materially better than any Mondstadt equivalent — expected, by
  construction, and inherited by Columbina (Nod-Krai's bench is similarly
  small). If §8 comes back friendly, that is geometry, not generosity.
- **Cryo-convergence management moves to kit design** (roster exclusion is
  off the table). Three levers, all authored-in from day one:
  1. **Application budget:** Charlotte and Freminet each get exactly ONE
     Cryo-applying card; their remaining cards do non-aura work. Half the
     nation pool being Cryo characters must not mean half the offered
     cards are freeze fuel.
  2. **Chevreuse is the counterweight by design:** her kit is authored as
     the attractive Overload/Vaporize route per the watch-item's standing
     fix ("buff other routes, never nerf freeze") — built in, not patched
     in.
  3. **Registered structural fact:** Fontaine has zero 4-star Electro;
     Furina's Electro-Charged access is confined to the uniform half of
     the reward slot and co-op. Scarce BY CONSTRUCTION — the sim and
     future reviewers should not "fix" it.
- **Freminet re-shape directive:** his source kit is a selfish Cryo carry —
  the exact shape guardrail 3 flattens. Author him around Pers and the
  diving identity instead: one applier, one defensive/trigger card, one
  enabler-shaped uncommon payoff. No fake-support re-flavor of a DPS kit.
- Kits at 3 cards each (~common enabler + common attack-ish + uncommon
  payoff), per the depth ruling above: 12 Fontaine companion cards total
  for v0.1 of the set.
- Fontaine 5-star Rares: later scope; Neuvillette flagged as the obvious
  first banner headliner. Lore audit per v1.7 checklist before anything
  ships.

## 11. Engineering asks (accumulating for the next Code handoff)

1. `character:` schema field, shared schema (all sheets).
2. Spotlight registry + selector delivery + empowerment hook (numbers-only
   enforcement at the engine level, not per-card discipline).
3. Salon summon-machinery audit (check-if-solved, report before building).
4. Tier 0 Encore accounting (A4 credit rule, §2).
5. Cross-player selector passing: C4-adjacent; solo path first.
6. Achievability experiment (§8) once the Fontaine sheet v0.1 exists.

## 12. Principles-doc amendments queued (for the next version bump)

- Spotlight system + `character:` tag (new §, or §3 extension).
- §2.2a extension: Spotlight/empowerment effects boost numbers only, never
  turn-economy.
- Guardrail 5 amendment (§6 above, ratified text pending user red-pen).
- Guardrail 2 ruling: generated companion cards retain their element
  application — stochastic, exhausting, drafted off-element access via a
  personal pool is consistent with "scarce and drafted" (explicit ruling,
  not silent precedent).
- Fanfare/Encore final definitions (supersede pre-design notes; add
  supersession header to furina-predesign-notes.md Part 2).
- Roadmap: Fontaine 4-star set v0.1 added to Furina's release scope.

## Open items (in order)

1. ~~Fontaine 4-star roster~~ — ratified (§10): all four, with kit-design
   levers for Cryo convergence. Next: sketch the four 3-card kits.
2. ~~Personal-pool signature~~ — resolved: the Guest Star generation
   suite (§9; full spec in fontaine-companions.yaml open items).
3. Self-Spotlight reduced rate (sweep at sheet pass).
3. Burst design + meter size (sheet pass).
4. Salon audit results gate Salon card grammar.
5. Statline sign-off: **user red-pen pending on this doc.**
