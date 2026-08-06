# Myte — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `Myte`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 2 (`Hive`, act index 1)
- **Encounter:** `MytesNormal` — a two-slot encounter (`first`, `second`) that always spawns exactly **two** Mytes, never more, never fewer. Both bodies are the same model; the only thing that distinguishes them is which slot they occupy.
- **Proposed fight class:** `mixed`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Myte runs a three-state move machine with **zero randomness**. Every transition is a hard-wired follow-up and the cycle closes on itself, so once you have seen one full rotation you can predict the rest of the fight exactly.

The three moves:

1. **Toxic (cast)** — shows a *status* intent for 2. Adds **2 Toxic status cards** directly to the target's hand, previewed as they arrive.
2. **Bite (attack)** — shows a *single-attack* intent. One heavy hit.
3. **Suck (attack + buff)** — shows a *single-attack* intent **and** a *buff* intent together. A small hit, then the Myte permanently buffs **itself** with Strength.

Wiring is a closed loop: Toxic → Bite → Suck → Toxic → … forever. There is no exit, no HP-threshold branch, and no enrage. Both Mytes ride the same loop; the only branch in the whole machine is **where each one enters it**, and that is decided by slot name:

- The **`first`-slot Myte enters on Toxic.**
- The **`second`-slot Myte enters on Suck.**

That one-step offset is the entire encounter design. The two bodies are permanently 120 degrees out of phase, so the player never gets a turn where both are doing the same thing, and never gets a turn that is purely harmless.

| Turn | `first` Myte | `second` Myte | What the turn asks of you |
| --- | --- | --- | --- |
| 1 | Toxic (2 cards) | Suck (small hit, self +Str) | Absorb chip + take 2 Toxic |
| 2 | Bite (big hit) | Toxic (2 cards) | Block the big hit + take 2 more Toxic |
| 3 | Suck (small hit, self +Str) | Bite (big hit, now buffed) | Block the big hit + chip |
| 4 | Toxic | Suck (self +Str again) | repeats turn 1, one Strength step higher |

Steady state from turn 2 onward: **every single turn contains exactly one Bite, one other move, and — on two turns out of three — a fresh pair of Toxic cards.** Toxic arrives on turns 1, 2, 4, 5, 7, 8, … (both bodies cast it, offset), so the player takes 2 Toxic on two consecutive turns, gets one turn of relief, then repeats.

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll (per body) | 61–67 | 64–69 (*Tough Enemies* tier) |
| Bite damage | 13 | 15 (*Deadly Enemies* tier) |
| Suck damage | 4 | 6 (*Deadly Enemies* tier) |
| Suck Strength gain (to itself) | +2 | +3 (*Deadly Enemies* tier) |
| Toxic cards added per cast | 2 | 2 (no ascension scaling) |
| Toxic end-of-turn self-damage | 5 per card | 5 (no ascension scaling) |

Combined health pool for the encounter: **122–134** base, **128–138** at the Tough-Enemies tier. That is a modest bar for Act 2 — the fight's difficulty is not in the HP.

**The Strength ramp is the real clock.** Each Myte gains Strength on its own Suck turn, which comes around once every three turns, and the buff is permanent and uncapped. It boosts both of that body's attacks. Effective damage per body (base / Deadly-Enemies tier), before any player modifiers:

| Suck casts by that body | Its Strength | Its Bite | Its Suck |
| --- | --- | --- | --- |
| 0 | 0 | 13 / 15 | 4 / 6 |
| 1 | +2 / +3 | 15 / 18 | 6 / 9 |
| 2 | +4 / +6 | 17 / 21 | 8 / 12 |
| 3 | +6 / +9 | 19 / 24 | 10 / 15 |

Because the bodies are out of phase, incoming damage per *turn* (one Bite + one Suck, from different bodies, at slightly different ramp steps) starts around **17** and climbs by roughly **+4 every three turns** (+6 at the Deadly tier) — before counting Toxic.

**Toxic is the other half of the damage.** Toxic is a 1-cost Status card with Exhaust that deals **5 damage to its holder at end of turn if it is still in hand**. So each cast presents the player a straight trade: spend 2 energy to play both copies away (they exhaust, so they do not clog the draw pile long-term), or eat **10 damage**. Partial payment is allowed — 1 energy for 5 damage. On the two-out-of-three turns where both Mytes have cast, the standing bill is 2 energy or 10 HP *per turn*, on top of blocking a ~15–20 point Bite.

Worked mid-fight turn (base numbers, one ramp step in): Bite 15 + Suck 6 + 2 unpaid Toxic 10 = **31 damage** on a turn where the player also wanted to be attacking. That is elite-shaped pressure coming out of a 130-HP normal fight.

## Gimmicks

- **The phase offset is the gimmick.** Both bodies share one deterministic loop; spawning them one step apart guarantees a Bite lands every turn and staggers the Toxic deliveries so they never fully overlap into a single skippable turn. Killing one Myte does not just halve the damage — it deletes an entire beat from the rhythm and leaves the survivor with a fully readable, one-move-per-turn pattern. **Focus-firing is strongly correct here**, and which one you kill matters: the body you leave alive keeps whatever Strength it has already banked.
- **Self-buff, not party-buff.** Strength goes on the caster only. The two Mytes ramp independently, so their damage diverges over the fight; the one that has cast Suck more times is the more urgent kill.
- **Energy tax disguised as a status card.** Toxic competes for the exact resource the player needs to end the fight. The fight's core tension is that paying the tax slows the kill, and skipping the tax pays 10 HP a turn into a health bar the ramping Bites are already eating.
- **Toxic exhausts.** It is a turn tax, not deck pollution — no post-combat cleanup, no permanent deck damage, no interaction with card-removal economy. Relief mechanics that discard or exhaust from hand answer it for free; artifact/negate-style effects do not, because nothing is being *applied* as a debuff.
- **Toxic is not blockable.** It resolves as end-of-turn self-damage on the holder, so Block spent for the Bite does nothing about it. The player must budget two separate resources in the same turn.
- No summons, no revives, no allies, no minion spawning, no HP-threshold behavior. Everything above is the whole kit.

## Scaling by act / ascension

- **Act:** none. Myte is Act 2 (`Hive`) content only and appears in that act's general encounter pool as a normal (non-weak, non-elite) fight. Its numbers do not read the act index; the only act-derived factor that touches it is the multiplayer scaler below.
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP band 61–67 → **64–69** per body. Note the band **narrows** as it rises — the floor moves +3 but the ceiling only +2, so high-ascension Mytes are more uniform, not just tougher. Total pool gain across both bodies is only about +6.
  - *Deadly Enemies* tier: Bite 13 → 15, Suck 4 → 6, Suck Strength +2 → **+3**.
  - The Strength bump is by far the most significant ascension change in the kit: it steepens the ramp by 50%, so a long fight at that tier diverges hard from the base-tier damage table. The Toxic count (2) and Toxic damage (5) do **not** scale, so at high ascension the fight's mix shifts away from the status tax and toward raw escalating attacks.

## Multiplayer / seat-count adjustments

- **HP scales hard.** On combat entry, enemy max HP is multiplied by (player count × act factor); for Act 2 that factor is **1.2** at every room type. A 2-player Myte sits at roughly 146–161 HP and a 3-player Myte at roughly 220–241. Across both bodies a 3-player fight carries a pool of roughly **440–483**.
- **Enemy block scales the same way**, but Myte never gains Block, so this is a no-op for this encounter — a rare case where the multiplayer scaler is purely an HP tax.
- **Attack damage does not scale with seats.** Bite and Suck remain 13/4 (15/6) per hit at any seat count.
- **Toxic scales per seat — and this is the seat-count story.** The status move resolves against **all** player creatures, so *every* player receives 2 Toxic per cast. Per-seat the tax is unchanged (2 energy or 10 HP each), but the party-wide bill on a both-cast turn is 4 energy / 20 HP at two seats, 6 energy / 30 HP at three. Meanwhile the Bites still only hit one target at a time and the HP pool has ballooned, so the fight runs *much* longer with the status tax billing every seat on every one of those turns.
- **Strength gain is seat-count independent** — the ramp table above is unchanged at any seat count, but a 3-player fight lasts long enough to reach ramp steps a solo player would never see.
- Net effect: co-op turns Myte from a tempo puzzle into a genuine grind. The HP multiplier stretches the fight, the unscaled attacks make it feel safe per-turn, and the per-seat Toxic plus the uncapped Strength quietly makes the back half of a long fight the dangerous part. **This is the encounter where taking too long is actively lethal**, and the seat-count math pushes directly toward taking too long.

## Fight-class reasoning — `mixed`

Per turn, this fight asks the player for two different things at once and refuses to let one answer cover both: Block or dodge a Bite that starts at 13–15 and climbs forever, *and* pay a 2-energy / 10-HP status bill that Block cannot touch. Neither demand alone would justify a label — the attacks are too small for `spike` (there is no burst turn, only a slow uncapped ramp, and the ramp is fully telegraphed by a deterministic loop), and the 130-HP pool is far too thin for `attrition` in solo play. `swarm` is wrong on count: two bodies with no summoning is a duo, not a crowd, and the correct play is focus-fire, not sweeping. `gimmick` over-indexes on the Toxic cards, which are only two of the three moves' worth of pressure. The honest read is `mixed`: a status/energy-tax gimmick layered on a self-buffing damage race, where the player must split resources between clearing hand-clog and racing an escalating clock — and where the multiplayer HP multiplier flips the same kit into an attrition fight without changing a single number in the moveset.
