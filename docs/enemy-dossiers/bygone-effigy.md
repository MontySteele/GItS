# Bygone Effigy — behavior dossier

- **Class:** `BygoneEffigy`
- **Kind:** elite
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounter:** `BygoneEffigyElite` — a **solo** elite. The encounter's monster pool and its generator both contain exactly one entry, so the Effigy is always alone; there is no add, no summon, and no variant roster. The encounter also pulls the camera back slightly and drops it, which is a size cue: this is one very large body, not a pack.
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

A four-state move machine with **zero randomness** — every transition is a hard-wired follow-up, so the fight plays identically on every seed:

1. **Sleep** (sleep intent) — the opening state. The Effigy does nothing at all except emit a thought-bubble line. No damage, no block, no power.
2. **Wake** (buff intent) — follow-up of Sleep. Gains a large flat Strength buff, speaks a line, and (outside test mode) kicks the music into the elite second-phase stem. Still deals no damage this turn.
3. **Slash** (single-attack intent) — follow-up of Wake, and **its own follow-up**. Once the Effigy reaches Slash it slashes every single turn for the rest of the fight.

So the whole fight is: **Sleep → Wake → Slash → Slash → Slash → …**

Two structural details worth carrying into a clone:

- The state machine will not transition away from its initial state until the monster has performed a move at least once, so the Sleep turn is genuinely consumed — the player really does get turn 1 free, not just a cosmetic sleep icon on an enemy that then acts.
- A **second sleep state exists in the machine but nothing reaches it.** It is registered, it carries a sleep intent, its follow-up points at Slash — but no other state names it, and the Effigy never force-sets it. In the shipped build it is dead content (an obvious hook for a cut "knock it back to sleep" mechanic, or for a card/relic that could re-sleep an enemy). Treat "the Effigy can be put back to sleep" as *designed-for but not implemented*.

There is no HP-threshold branch, no enrage, no block move, and no second attack. The intent readout after turn 2 is the same icon and the same number forever.

## Numbers

| Value | Base | Ascension-modified |
| --- | --- | --- |
| Max HP | 127 | 132 (Tough Enemies tier and above) |
| Slash damage (printed) | 13 | 15 (Deadly Enemies tier and above) |
| Wake Strength gain | +10 | +10 (no ascension scaling) |
| Block gained | none | none |
| Debuffs applied to the player | none | none |

HP is fixed, not rolled — the min and max initial HP are the same value, so unlike most monsters there is no per-run HP band to plan around. 127 (or 132) exactly.

Because Wake lands a flat **+10 Strength** before the first Slash, the printed 13 is never the number the player actually eats. Effective damage per Effigy turn:

| Effigy turn | 1 (Sleep) | 2 (Wake) | 3+ (Slash) |
| --- | --- | --- | --- |
| Damage dealt, base | 0 | 0 | **23** |
| Damage dealt, Deadly Enemies | 0 | 0 | **25** |

Strength here is the ordinary permanent additive buff — it does not decay and it is applied once, so 23/25 is flat for the whole fight and never climbs. Cumulative unblocked damage: 0 through turn 2, then 23 / 46 / 69 / 92 / 115 on turns 3–7. Against typical Act 1 hero HP that is roughly a **four-to-five-Slash death clock** once it wakes, i.e. the player has about six or seven total turns of fight before the Effigy wins.

Damage feedback is stone-flavored — it reads and sounds like carved rock being chipped, which is the tell that this is a statue that will eventually move.

## Gimmicks

- **Self-inflicted Slow (the whole gimmick).** On entering the room the Effigy applies a **Slow debuff to itself**, permanently, for the entire fight. Slow is a counter that starts at zero and **increments by one every time a card is played**; while it is on the Effigy, every *attack-card* hit the Effigy takes is multiplied by **1 + 0.10 × (cards played so far this turn)**. The counter **resets at the start of the enemy's turn**, so it accumulates fresh across each player turn and is spent within that turn. The UI shows the counter as a percentage (the internal count × 10).
  - Practical consequence: **card ordering is the fight's skill test.** Lead with cheap skills, draw, and powers, and land your biggest attack last. A sixth-card attack lands at +50%; the same attack played first lands at +0%.
  - The bonus is **multiplicative on attack damage only** — poison/HP-loss ticks, relic and potion damage, and power-sourced damage carry the "unpowered" flag and get nothing from Slow. A pure-DoT deck fights this elite at face value; a big-attack deck fights it at a large discount.
  - Note the sign: this debuff is *on the enemy* and helps the player. It is the design's built-in answer to the 127 HP wall, and it is why the Effigy can afford flat 23s.
- **Two free turns, front-loaded.** The Sleep and Wake turns deal nothing, so the player gets two uninterrupted setup turns. That is where powers, scaling, and a Slow-stacked opening burst are meant to go. A deck that cannot convert those two turns into a large chunk of the 127 will not beat the clock later.
- **One telegraphed escalation, then flatness.** Wake nearly doubles the attack (13 → 23) in a single step and announces itself with a line, a buff intent, and a music cue. After that, nothing about the fight ever changes again.
- **No defensive kit at all.** No block, no thorns, no debuff on the player, no self-heal, no minions, no artifact-style buff protection. Every hit the player lands sticks, and every Weak/Vulnerable-style tool works normally.
- **Weak-and-Strength-removal weakness.** All of its output routes through one Strength-boosted attack, so Weak (or anything that strips Strength) is disproportionately effective — removing the +10 takes it from 23 back to 13.

## Scaling by act / ascension

- **Act:** none. Act 1 content only; no per-act variant, and none of its values read the act index. (The act index does feed the *multiplayer* scaler — see below — but not single-player.)
- **Ascension:** two independent bumps, each keyed to a named ascension tier rather than a raw level. The "tough enemies" tier raises max HP 127 → 132 (+3.9%). The "deadly enemies" tier raises Slash 13 → 15, which after the flat +10 Strength is an effective 23 → 25 (+8.7%). The +10 Strength itself, the sleep/wake timing, and the Slow behaviour are identical at every ascension. Net: ascension makes this fight modestly longer and modestly harder-hitting, but it does not change its shape or its two free turns.

## Multiplayer / seat-count adjustments

- **HP scales hard.** On entering combat with more than one player, enemy max HP is multiplied by (player count × an act factor); in Act 1 that factor is **1.1**. So the Effigy sits at roughly **279 HP at 2 players** and **419 at 3** (290 / 436 on the Tough Enemies tier).
- **The Slash hits every seat.** The attack is built as a monster attack targeting *all opponents*, and with more than one valid target the damage is dealt to the whole list rather than to a picked target. In co-op **each player takes the full 23/25 every turn** — the intent is a "single attack" only in the sense that it is one hit per player, not one hit total. Team-wide incoming damage therefore scales linearly with seat count (46/turn at 2P, 69/turn at 3P) while the enemy's HP scales at 2.2×/3.3×. Damage-per-seat is *not* divided, so the fight gets meaningfully harsher per seat than the HP multiplier alone suggests.
- **Block scaling is irrelevant here** — the multiplayer scaler that inflates enemy block only touches enemies that gain block, and the Effigy gains none.
- **Slow counts the table's cards.** The Slow counter increments on card plays generally, so with more seats the multiplier climbs faster within a shared turn — a co-op team can stack a much larger bonus before the designated hitter swings. This is the main lever that keeps the inflated HP pool killable, and it rewards explicit turn-order coordination ("everyone cycle first, closer swings last").
- Targeting geometry: before slashing, the Effigy repositions itself toward the leftmost player creature (a visual lunge plus a radial blur). Cosmetic — it does not change who is hit.

## Fight-class reasoning — `attrition`

After its two-turn wind-up the Effigy demands exactly the same thing every single turn forever: cover 23–25 damage per seat, or trade HP for tempo, while chewing through a 127 HP (279+ in co-op) wall that never blocks and never heals. There is no burst turn to save block for, no add wave, no threshold, and no variance — the demand curve is a flat line with one telegraphed step at turn 3, which is the signature of an attrition body rather than a spike. The Slow self-debuff is a genuine mechanic but it points the other way: it is a player-facing damage discount that rewards card ordering, so it deepens the *race* rather than posing a puzzle-lock, which is why this is not labelled `gimmick`. The fight is won or lost on whether the deck's sustained damage clears the wall before the flat clock clears the party.
