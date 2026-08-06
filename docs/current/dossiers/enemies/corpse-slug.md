# Corpse Slug — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `CorpseSlug`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Underdocks`, act index 0)
- **Encounters:** `CorpseSlugsNormal` — **three** Corpse Slugs; `CorpseSlugsWeak` — **two** Corpse Slugs (flagged as a weak/early-act encounter). Both carry the `Slugs` encounter tag. There is no single-slug encounter: you always fight a pack.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Each Corpse Slug runs a **three-state cycle with zero randomness**. Every transition is a hard-wired follow-up, so once you have seen one turn you can read the rest of that slug's fight exactly.

The three moves:

1. **Whip Slap** — *multi-attack* intent, damage × 2. Two light hits played on one animation.
2. **Glomp** — *single-attack* intent. One heavy hit.
3. **Goop** — *debuff* intent. No damage; applies Frail.

Wiring: Whip Slap → Glomp → Goop → Whip Slap → … forever. No branch, no HP threshold, no re-roll. The state machine performs its initial state before it is allowed to transition, so the slug's first turn is always its assigned starting move.

**The pack is deliberately de-synchronised.** At encounter generation the game picks one random starting index in the 3-cycle and then hands each slug in the group the *next* index in sequence. Consequences:

- In the 3-slug encounter, the pack **always covers all three moves every single turn** — one Whip Slap, one Glomp, one Goop, in some rotation. Which slug is doing which rotates each turn, but the turn's total is constant.
- In the 2-slug (weak) encounter, two of the three moves are live each turn and the missing one rotates: (Whip+Glomp) → (Glomp+Goop) → (Goop+Whip) → repeat. One turn in three has no Frail, one turn in three drops the heavy hit.

Example, 3-slug pack (rotation offset depends on the seed):

| Turn | Slug A | Slug B | Slug C | Party takes |
| --- | --- | --- | --- | --- |
| 1 | Whip Slap | Glomp | Goop | 6 + 8 dmg, 2 Frail |
| 2 | Glomp | Goop | Whip Slap | 6 + 8 dmg, 2 Frail |
| 3 | Goop | Whip Slap | Glomp | 6 + 8 dmg, 2 Frail |

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll (per slug) | 25–27 | 27–29 (*Tough Enemies* tier) |
| Whip Slap damage | 3, **twice** (6 total) | 3, twice — not ascension-scaled |
| Glomp damage | 8 | 9 (*Deadly Enemies* tier) |
| Goop Frail applied | 2 | 2 — not ascension-scaled |
| Ravenous Strength per ally death | +4 | +5 (*Deadly Enemies* tier) |

HP is rolled per body inside the band, and the game prefers a **distinct** max-HP value per creature on the side where the band allows — so in a 3-pack the slugs will usually sit on three different HP totals (e.g. 25 / 26 / 27). That matters more than it looks: it means the pack cannot be cleanly cleared by a single repeated same-size hit, and the "which one dies first" decision is partly made for you by the roll.

The slugs have **no block move of any kind** and gain no defensive powers. Total pool: **75–81** base for the 3-pack (81–87 at the Tough-Enemies tier), **50–54 / 54–58** for the weak 2-pack.

Frail reduces block gained to 75% for 2 turns. In the 3-slug pack, Goop fires **every turn**, so Frail uptime is continuous from turn 1 and a re-application always arrives before the counter expires.

## Gimmicks

- **Ravenous (the headline).** Every Corpse Slug enters combat carrying a counter-style buff, initialised to 4 (5 at the Deadly-Enemies tier). When **any allied creature on its side dies**, each surviving slug: flashes, plays a "devour" animation and enters a devouring state, is **Stunned** for its next turn (its telegraphed intent is immediately replaced with a Stun intent), and gains **permanent Strength equal to the counter's amount**. The Strength is applied at the moment of the death — i.e. on the player's turn — so the *only* turn it is not felt is the stunned one.
- **The stunned turn is a delay, not a skip in the cycle.** The Stun move's follow-up is set to the slug's last logged move, so after devouring it resumes the move it had telegraphed rather than advancing past it. Killing a slug therefore costs the pack one turn of output and permanently raises the rest; the cycle order is preserved.
- **Killing is a real cost, and this is the fight's whole design.** Every kill trades *one free turn now* for *permanently bigger hits forever after*. Because Whip Slap is a two-hit move and Strength is added per hit, the multi-attack scales at **double rate** with each devour — a fed slug's "light" attack outgrows its "heavy" one.

  Effective per-slug output as the pack thins (base / Deadly-Enemies tier):

  | Deaths so far | Strength | Whip Slap (per hit ×2) | Glomp |
  | --- | --- | --- | --- |
  | 0 | 0 | 3 ×2 = **6** | **8 / 9** |
  | 1 | +4 / +5 | 7 ×2 = **14** / 8 ×2 = 16 | **12 / 14** |
  | 2 | +8 / +10 | 11 ×2 = **22** / 13 ×2 = 26 | **16 / 19** |

  Pack damage per turn, 3-slug encounter: **14** while all three live; after one death the surviving two deal **14 + 12 = 26** (two of the three moves are live, so the exact figure rotates between 26, 20 and 14+Frail depending on which pair is up — but the *worst* turn nearly doubles). Killing a slug can make the fight strictly more dangerous.
- **The devour trigger is not slug-specific.** It fires on the death of *any* allied creature on the same side, and it explicitly excludes a slug that is itself dead or is the creature that died — so a simultaneous wipe grants nothing. **This is the escape hatch:** an AoE finish that kills the last slugs in the same instant denies the buff entirely, and killing the whole pack in one turn denies it completely.
- **Goop is pure debuff.** No damage, no self-buff — its only job is to keep Frail up so the player's block cards buy 25% less while the escalation clock runs.
- No summons, no revives, no HP-threshold branch, no enrage beyond Ravenous. Everything above is the whole kit.

## Scaling by act / ascension

- **Act:** none. Corpse Slug is Act 1 (`Underdocks`) content only, appearing in both the normal and weak encounter pools of that act. Its numbers do not read the act index; the only act-derived factor that touches it is the multiplayer scaler below (act index 0 → ×1.1).
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP band 25–27 → **27–29** per slug (+6 across a 3-pack).
  - *Deadly Enemies* tier: Glomp 8 → **9**, and Ravenous Strength 4 → **5**.
  - Whip Slap damage, Whip Slap hit count, and the Frail amount are **not** ascension-scaled. The pack size is not ascension-scaled either — always 3 (normal) or 2 (weak).
  - Note the shape of the *Deadly* bump: +1 on the heavy hit is trivial, but +1 on Ravenous compounds. At two deaths the surviving slug is at +10 Strength instead of +8, which is +4 on its Whip Slap total.

## Multiplayer / seat-count adjustments

- **HP scales by seats.** On entering combat with more than one player, enemy max HP is multiplied by (player count × act factor); for a non-boss **Act 1** room that factor is **1.1**. A 2-player slug sits at roughly 55–59 HP (2 × 1.1 × a 25–27 roll) and a 3-player slug at roughly 82–89. A 3-player 3-pack is a pool of ~250 HP — which is a long time to spend under continuous Frail with an escalation clock running.
- **The block scaler is inert here.** The multiplayer system also inflates block gained by enemies from monster moves by the same factor, but Corpse Slug has no block move, so this does nothing.
- **Damage does not scale, but it is applied per seat.** Monster attacks target all opposing player creatures rather than picking one. Whip Slap hits **every** player twice, Glomp hits every player once, and Goop applies its 2 Frail to every player creature. Per-seat incoming damage is therefore identical to solo.
- **Ravenous is seat-count independent** — the escalation table above holds at any seat count.
- **Net effect: co-op makes the gimmick strictly worse.** More HP per body means it is much harder to line up a same-turn multi-kill, so parties are pushed into staggered kills — exactly the pattern Ravenous punishes — while each surviving slug's inflated attacks land on everyone. The fight's difficulty in co-op is governed by whether the party can co-ordinate a simultaneous finish, not by raw throughput.

## Fight-class reasoning — `gimmick`

The per-turn demand of the raw statline is unremarkable Act 1 chip — a fixed 14 damage and 2 Frail from a 3-pack, on a deterministic rotation you can read from turn one — so neither `spike` nor `attrition` describes what the player is actually solving. What the fight demands is a **kill-order and kill-timing decision**: Ravenous inverts the normal answer to a multi-body encounter by making "pick them off one at a time" the losing line, since each death buys one stunned turn and then permanently raises every survivor, with the two-hit Whip Slap absorbing Strength at double rate. The whole encounter is therefore a question about whether you can hold damage and finish two or three bodies in the same turn (denying the buff) or must accept the escalation and race a pack whose output nearly doubles as it thins. `swarm` is the near-miss — three low-HP bodies genuinely do reward AoE — but it under-sells the mechanic, because here AoE is not merely efficient, it is the specific counter to the special rule; the rule, not the body count, sets the demand curve.
