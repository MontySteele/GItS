# Wriggler — behavior dossier

- **Class:** `Wriggler`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 1 (`Overgrowth`, act index 0 — the alternate Act 1 alongside `Underdocks`)
- **Encounters:**
  - `DenseVegetationEventEncounter` — **four** Wrigglers, all starting *unstunned*. This is not a map combat: it is entered from the middle of the **Dense Vegetation** event (the "Rest" option, which heals you first and then hisses at you), and it awards **no combat rewards at all**.
  - `PhrogParasiteElite` — the Wrigglers are not placed at encounter start. The Phrog Parasite enters combat carrying an *Infested* power; when the Phrog dies, that power **blocks combat from ending** and spawns **four Wrigglers**, all flagged *start stunned*, into the four wriggler slots. Effectively an elite second phase (the game even swaps the music).
- **Bestiary:** only the Wriggle move is listed. Nasty Bite and the spawn-stun state are explicitly hidden from the bestiary entry.
- **Proposed fight class:** `swarm`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

A Wriggler has two real moves and one do-nothing state, and **no randomness anywhere**. There is no RNG branch in its state machine at all: given the slot it occupies, its entire fight is readable from turn one.

The moves:

1. **Nasty Bite** — *single-attack* intent. One hit.
2. **Wriggle** — a combined *buff* + *status* intent (the intent icon shows both: a buff arrow and a "1 status card" marker). Deals no damage. It adds **one Infection status card** to each opponent's discard pile and gives **itself +2 Strength, permanently**.
3. **Spawned** — a *stun* intent that does literally nothing. Used only for the elite's second phase.

Wiring: Bite → Wriggle → Bite → Wriggle → … forever. Spawned → (slot branch) → the cycle.

**The pack is de-synchronised by slot, not by seed.** The opening move is chosen by a conditional branch on which of the four wriggler slots the body occupies:

| Slot | Opening move |
| --- | --- |
| `wriggler1` | Nasty Bite |
| `wriggler2` | Wriggle |
| `wriggler3` | Nasty Bite |
| `wriggler4` | Wriggle |

So a full pack is permanently split **two biters / two wrigglers**, and because both bodies strictly alternate, that split holds every single turn — the *identities* swap each turn but the turn's composition never does. While all four live, every turn is **two bites + two Wriggles** (2 Infection cards per player, +2 Strength on each of the two wriggling bodies). Unlike Corpse Slug's rotation, this is not a random offset; it is fixed by the encounter layout, so the pattern is identical every run.

The state machine performs its initial state before it is allowed to transition, so the first turn is always the slot-assigned move (or, for elite-spawned bodies, always the free stun turn).

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll (per body) | 17–21 | 18–22 (*Tough Enemies* tier) |
| Nasty Bite damage | 6 | 7 (*Deadly Enemies* tier) |
| Wriggle self-Strength | +2 permanent | +2 — **not** ascension-scaled |
| Wriggle Infection cards | 1 per opponent | 1 — **not** ascension-scaled |
| Infection end-of-turn damage | 3 | 3 — **not** ascension-scaled |

Four-body pool: **68–84** base, **72–88** at the Tough-Enemies tier. These are the softest bodies in the act — a single body dies to one mid-sized card.

The Wriggler has **no block move**, no heal, no defensive power and no escape. Every point of its HP is raw pool.

**The escalation table.** Each body gains +2 Strength on every Wriggle, i.e. every other turn, and that Strength is added to its own Bite. With a full four-pack the two alternating pairs stagger, so party-facing damage grows about **+2 per turn on average** (base numbers; add +1 per bite at the Deadly-Enemies tier):

| Turn | Biting pair | Bite each | Party takes | Also |
| --- | --- | --- | --- | --- |
| 1 | slots 1+3 | 6 | **12** | 2 Infection |
| 2 | slots 2+4 | 8 | **16** | 2 Infection |
| 3 | slots 1+3 | 8 | **16** | 2 Infection |
| 4 | slots 2+4 | 10 | **20** | 2 Infection |
| 5 | slots 1+3 | 10 | **20** | 2 Infection |
| 6 | slots 2+4 | 12 | **24** | 2 Infection |
| 8 | slots 2+4 | 14 | **28** | 2 Infection |

There is no cap and no reset. Strength is applied to the creature itself, so it dies with the body — killing a Wriggler permanently deletes its accumulated Strength as well as its share of the output. Kills here are unambiguously good; there is no Ravenous-style punish for picking bodies off.

**Infection.** An unplayable Status card, cost -1, **no upgrade, no exhaust**. It enters the **discard** pile (so it does nothing the turn it is created — it bites once it cycles into hand), and at the **end of any turn it is still in hand** it deals **3 damage to its owner**. That damage is ordinary blockable damage, which means in practice it eats the block you just bought for the enemy turn rather than being free. Because it never exhausts, every copy is a permanent deck clog for the rest of the combat: at 2 copies per player per turn, a four-turn fight has already put ~8 dead cards into a starter deck.

## Gimmicks

- **Self-buff, not a party buff.** Wriggle's Strength goes on the wriggling body only. There is no aura, no leader, no shared scaling — four Wrigglers escalate as four independent clocks. This is what makes focus-firing correct.
- **The Infection loop is the real cost.** Wriggle contributes zero damage on the turn it fires but converts into damage twice over: 3 HP whenever the card sits in hand at end of turn, and a lost card slot every draw thereafter. The pack's per-turn *nominal* damage understates its real pressure by roughly the number of Infections currently live in your draw.
- **Spawn stun is a genuine free turn — once.** Elite-spawned Wrigglers telegraph a stun intent on their first turn and do nothing at all: no damage, no status, no Strength. That turn is a full-pack free turn for the party, and it is the only reprieve the fight offers. After it, they fall into the same slot-keyed branch (bite / wriggle / bite / wriggle) as the event pack.
- **The elite refuses to end.** The Phrog's Infested power explicitly prevents combat from ending on the Phrog's death, so there is no way to skip phase two by bursting the Phrog down — you are always paying for the second phase in full.
- **The event fight pays nothing.** The Dense Vegetation encounter grants an empty reward list. You get the event's rest-heal, and then you pay for it with ~80 HP of bodies, an escalating clock and a permanently clogged deck for zero cards, gold or relics.
- No summons (the Wrigglers *are* the summons), no revives, no HP thresholds, no enrage, no block. The above is the entire kit.

## Scaling by act / ascension

- **Act:** none. Wriggler is Act 1 (`Overgrowth`) content only, in one event encounter and one elite's second phase. Nothing in its numbers reads the act index; the only act-derived factor is the multiplayer scaler below (act index 0 → ×1.1).
- **Ascension:** exactly two tier-keyed bumps, and one of them is tiny.
  - *Tough Enemies* tier: HP band 17–21 → **18–22** per body (+4 across the four-pack).
  - *Deadly Enemies* tier: Nasty Bite 6 → **7**. Applied to two biters per turn, that is +2 party damage per turn *on top of* the Strength ramp — so at turn 8 the pack is at 32 rather than 28.
  - Strength per Wriggle, Infection count, Infection damage and pack size (always 4) are **not** ascension-scaled. Notably the escalation *rate* is fixed; ascension moves only the starting height of the curve.

## Multiplayer / seat-count adjustments

- **HP scales by seats.** Enemy max HP is multiplied by (player count × act factor), and for a non-boss **Act 1** room that factor is **1.1**. A 2-player Wriggler sits at roughly 37–46 HP and a 3-player Wriggler at roughly 56–69. A 3-player four-pack is a ~250 HP pool — but crucially the bodies stop being one-card kills, which is the whole difference in co-op (see below).
- **The block scaler is inert here.** The multiplayer system also inflates enemy block from monster moves by the same factor; Wriggler has no block move, so this does nothing.
- **Damage does not scale, but everything is applied per seat.** Monster attacks target *all* opposing player creatures. Every Nasty Bite hits **every** player for its full amount, and every Wriggle puts **one Infection into every player's discard**. Per-seat incoming damage and per-seat deck clog are therefore identical to solo — a three-seat party takes 2 Infections *each* per turn, i.e. six cards of clog per turn across the table.
- **The Strength ramp is seat-count independent.** The escalation table above holds at any seat count, while the HP pool triples — so the ramp gets more turns to run and the fight's back half is materially nastier in co-op.
- **Net effect: co-op stretches the clock, and the clock is the danger.** Inflated bodies mean fewer kills per turn, more turns, more Strength, and more Infections in every deck at once. Parties want overlapping AoE and coordinated focus-fire on one body at a time rather than four players each chipping a different Wriggler.

## Fight-class reasoning — `swarm`

Per turn, this fight demands one thing: **delete bodies, and delete them now.** Four ~20 HP bodies with no block, no heal and no defensive tricks make AoE and cheap repeatable damage the dominant answer, and every body removed permanently deletes both its share of the two-bites-per-turn output and the Strength it had banked — there is no kill-order puzzle and no reason to hold damage. The escalation is what makes the demand urgent rather than trivial: a fixed +2 Strength per Wriggle with no cap, plus two never-exhausting Infection cards per player per turn that make your deck worse exactly as the enemy gets better, so the same fight taken three turns slower is a strictly different fight. `attrition` is the near-miss — the fight does grind and it does tax your deck — but attrition implies the enemy statline is stable while you outlast it, and here the statline outruns you if you stall; `gimmick` overstates Infection, which is a compounding tax on tempo rather than a rule you must solve.
