# Byrdonis — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `Byrdonis`
- **Kind:** elite
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounter:** `ByrdonisElite` — a **solo** elite. Both the encounter's possible-monster pool and its generator contain exactly one entry, so the Byrdonis always fights alone: no adds, no summons, no variant roster.
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

A two-state move machine with **zero randomness**. Each state's follow-up is hard-wired to the other, so the fight is a strict alternation that plays identically on every seed:

1. **Swoop** (single-attack intent) — the **initial** state, so this is what the player sees on turn 1.
2. **Peck** (multi-attack intent, 3 hits) — follow-up of Swoop.
3. Peck's follow-up is Swoop again.

The whole fight is: **Swoop → Peck → Swoop → Peck → …** forever. There is no block move, no debuff move, no summon, no HP-threshold branch, no enrage state, and no state the machine can reach that isn't one of these two. The intent readout is fully predictable from turn one onward — a player who has seen the fight once knows every future intent.

The state machine will not transition away from its initial state until a move has actually been performed, so the opening Swoop is guaranteed to resolve before the machine advances; there is no "skips its first turn" behaviour here.

## Numbers

| Value | Base | Ascension-modified |
| --- | --- | --- |
| Initial HP band | 81–84 (rolled) | 90 flat (Tough Enemies tier and above) |
| Swoop damage (printed) | 17 | 19 (Deadly Enemies tier and above) |
| Peck damage per hit (printed) | 3 | 4 (Deadly Enemies tier and above) |
| Peck hit count | 3 | 3 (no ascension scaling) |
| Block gained | none | none |
| Debuffs applied to the player | none | none |

At base the HP is a **rolled band** (81–84); at the Tough Enemies tier the min and max collapse to the same value, so it is exactly **90** with no roll.

The printed numbers are never what the player eats past turn 1, because of the self-buff below. Effective per-turn damage, base values, assuming no Strength removal:

| Byrdonis turn | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Move | Swoop | Peck ×3 | Swoop | Peck ×3 | Swoop | Peck ×3 | Swoop | Peck ×3 |
| Strength when acting | 0 | +1 | +2 | +3 | +4 | +5 | +6 | +7 |
| Damage, base | 17 | 12 | 19 | 18 | 21 | 24 | 23 | 30 |
| Damage, Deadly Enemies | 19 | 15 | 21 | 21 | 23 | 27 | 25 | 33 |

Cumulative unblocked damage at base: 17 / 29 / 48 / 66 / 87 / 111 / 134 / 164 after turns 1–8. Against Act 1 hero HP that is roughly a **five-to-seven-turn death clock**, and the clock accelerates rather than running flat.

Two shape facts fall out of the table:

- **Turn 1 is the single biggest hit in the fight for a long while.** A 17–19 unmitigated blow on the opening turn, before any setup, is well above the Act 1 norm and is the fight's most common source of unavoidable chip.
- **Peck overtakes Swoop.** Because Strength is added *per hit*, the 3-hit move gains **+3 effective damage per turn** while Swoop gains only +1. Peck starts as the weak turn (12 vs 17) and permanently passes Swoop from turn 6 onward. A fight that goes long is lost to Pecks, not Swoops.

## Gimmicks

- **Territorial (the whole gimmick).** On entering the room the Byrdonis applies a **Territorial counter to itself, amount 1**, permanently. Territorial is a self-buff that fires at the **end of the enemy side's turn** and grants that creature **Strength equal to its counter value** — so, at 1 stack, **+1 permanent Strength every round**, forever, with no cap and no decay. The power surfaces a Strength hover-tip and flashes when it triggers, so the escalation is legible rather than hidden.
  - Practical consequence: the fight has a **built-in soft enrage** with no threshold and no announcement turn. Every round the player spends not killing it makes the next round strictly worse, and worse at an accelerating rate on the Peck turns.
- **No defensive kit at all.** No block, no thorns, no self-heal, no artifact-style buff protection, no player-facing debuff. Every hit the player lands sticks, and Weak / Vulnerable / Strength-removal all work at face value.
- **Disproportionate weakness to Strength removal and Weak.** All output routes through one Strength stat that the enemy is stacking for you. Stripping Strength does not just shave a turn — it resets the accelerator, and on a Peck turn each point removed is worth 3 damage. This is the fight's designed counterplay hook.
- **Multi-hit vs. single-hit texture.** Alternating a chunky single blow with a 3-hit spread means block-efficiency oscillates: full-block plans are fine either way, but per-hit mitigation (flat damage reduction, per-hit triggers, retaliate/thorns effects) swings wildly between the two turns. Thorns-style retaliation gets triple value on Peck turns.
- **Animator carries an unused "Angry" state.** The creature's animation graph registers a `get_angry` any-state transition and the model declares a trigger constant for it, but nothing in the shipped combat logic ever fires it. Treat "the Byrdonis visibly enrages at some point" as *designed-for but not implemented* — the escalation is numeric only, delivered through the Territorial flash.
- **Adjacent content (not part of the fight).** Act 1 carries a `ByrdonisNest` event (eat the egg for +7 max HP, or take an unplayable quest card that adds a hatch option at rest sites, feeding the Byrdpip pet relic). On a player's very first run the act deliberately front-loads both the nest event and this elite into the first slots of their respective room lists, so the Byrdonis is the intended first elite most players ever meet.

## Scaling by act / ascension

- **Act:** none. Act 1 content only; no per-act variant, and none of its combat values read the act index. (The act index does feed the *multiplayer* scaler — see below.)
- **Ascension:** two independent bumps, each keyed to a named ascension tier rather than a raw level.
  - *Tough Enemies tier:* HP band 81–84 → flat 90 (+7% against the midpoint, and it removes the low roll entirely).
  - *Deadly Enemies tier:* Swoop 17 → 19 and Peck 3 → 4 per hit. Note the asymmetry: Peck's +1 per hit is **+3 per turn**, so the Deadly bump hits the multi-hit turn nearly three times as hard as the Swoop turn, and it moves the Peck-overtakes-Swoop crossover a turn earlier.
  - The Territorial +1/turn, the hit count, and the alternation are identical at every ascension. Ascension makes the fight longer *and* raises the slope's starting point; it does not change the slope itself or the fight's shape.

## Multiplayer / seat-count adjustments

- **HP scales hard.** On entering combat with more than one player, enemy max HP is multiplied by (player count × an act factor); the Act 1 factor is **1.1**. That puts the Byrdonis at roughly **178–185 HP at 2 players** and **267–277 at 3** (198 / 297 on the Tough Enemies tier).
- **Both moves hit every seat.** Both attacks are built as monster attacks targeting *all opponents*, and with more than one live target the damage is dealt to the whole list rather than to a randomly picked seat. In co-op **each player takes the full Swoop and the full 3-hit Peck every round** — nothing is split. Team-wide incoming damage scales linearly with seat count (turn 1 = 34 at 2P, 51 at 3P) on top of an already-escalating curve.
- **Territorial does not scale with seats,** but its effect effectively does: +1 Strength is +1 damage *per seat* on Swoop turns and +3 *per seat* on Peck turns, so the ramp's real cost to the table is multiplied by the seat count even though the buff is unchanged. At 3 players a single Territorial tick is worth 9 team damage on Peck turns.
- **Block scaling is irrelevant here** — the multiplayer scaler that inflates enemy block only touches enemies that gain block, and the Byrdonis gains none.
- Net co-op read: the HP wall grows ~2.2×/3.3× while per-round table damage grows 2×/3× *and* accelerates, so the extra seats do not buy slack. Co-op teams need the Strength-removal or Weak answer far more urgently than a solo player does.

## Fight-class reasoning — `attrition`

Every turn of this fight asks the same question with a slightly bigger number attached: cover 17–19 (or a 3× spread) *per seat*, or trade HP for tempo, while grinding down an ~81–90 HP body (178+ in co-op) that never blocks, never heals, and never gives a free turn. There is no telegraphed burst turn to bank block for and no add wave — the demand curve is a rising line with no gaps, which is an attrition body with a soft enrage rather than a `spike`. The Territorial self-buff is a real mechanic, but it poses no puzzle-lock; it just steepens the race and hands the player one obvious lever (remove Strength / apply Weak), so `gimmick` overstates it. The fight is won or lost on whether the deck's sustained damage clears the wall before the accelerating clock — driven mainly by the Peck turns, not the flashier Swoop — clears the party.
