# Eye with Teeth — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `EyeWithTeeth`
- **Kind:** normal (non-elite, non-boss); in practice a **summoned minion**, never a headline body
- **Act:** Act 1 (`Overgrowth`, act index 0)
- **Encounters:** `FogmogNormal` only. The encounter *generates* just the Fogmog (slot `fogmog`); the Eye is listed in the encounter's possible-monster set and arrives mid-fight into the reserved `illusion` slot when Fogmog performs its summon move. There is no encounter in which an Eye with Teeth is placed at combat start, and none in which more than one exists.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Eye has the simplest state machine in the roster: **one move, wired to follow up into itself.** There is no branch, no random roll, no HP threshold, no opening variation.

- **Distract** — *status-card* intent (shows the status-card icon with a count of 3). Plays an attack animation and a slash effect, but deals **no damage and applies no powers**. It adds **3 Dazed** to the bottom of the target's **discard** pile.

Because the follow-up is the state itself, the telegraph is Distract on the turn it spawns and Distract on every turn thereafter, forever. Reading its intent is never a decision.

The one interruption is the revive (see Gimmicks): when killed, its next turn is replaced by a **Heal** intent instead of Distract, and the state machine is pointed back at Distract afterwards, so the cycle resumes exactly where it left off.

Full-fight cadence, solo (Fogmog's own opener is its summon; its damage numbers are listed for context only):

| Turn | Fogmog | Eye with Teeth | Player takes |
| --- | --- | --- | --- |
| 1 | Illusion (summon) | — (not yet in combat) | nothing |
| 2 | Swipe 8 + self Strength | Distract | 8 dmg, 3 Dazed |
| 3+ | branches between Swipe and Headbutt | Distract | attack + 3 Dazed |
| any turn after you kill it | (unchanged) | Heal to full | attack only |
| turn after that | (unchanged) | Distract | attack + 3 Dazed |

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP | **6**, fixed (min = max, no roll) | not ascension-scaled |
| Distract damage | **0** | — |
| Dazed added per turn, per player | **3**, to the discard pile, bottom | not ascension-scaled |
| Block gained | **none** — it has no block move | — |
| Revive heal | back to **full** (6) | — |

Dazed itself: cost-less **Status** card, **Unplayable** and **Ethereal**. Ethereal means a copy that reaches your hand exhausts at end of turn — so the cards do eventually leave the deck, but only after they have each cost you one draw. Delivery to the *discard* pile (not hand, not draw) is the meaningful detail: nothing is clogged this turn, and the whole batch enters the draw pile at the next shuffle. The pollution therefore arrives in a lump, one reshuffle behind the intent that created it.

Rate: **3 status cards per turn, indefinitely.** Against a starting deck this is roughly a card of dilution per turn of the fight; four turns of Distract is more junk than a starting deck has strikes.

## Gimmicks

- **It is an illusion: killing it does not remove it.** It enters combat already carrying the Illusion buff, which (a) prevents removal from combat on death, (b) preserves its buffs through death, and (c) on death immediately installs a one-shot **Revive** move that must be performed before the machine may transition. The practical loop: you spend damage → it plays a stun animation and sits dead for the rest of the turn → on its next turn it wakes and heals to **full 6 HP** → the turn after, Distract resumes. **Killing it buys exactly one Dazed-free turn, for 6 HP of damage, every time.** There is no kill count at which it stops coming back.
- **Debuffs are wiped by the death you cause, and cannot be applied while it is reviving.** The Illusion buff strips non-temporary debuffs on death (buffs are kept), so poison/weak invested in it is destroyed by killing it; and while it is in the reviving state it refuses incoming power application entirely. Damage-over-time and debuff plans are structurally dead against this body.
- **It is a minion, and it is not the win condition.** The Illusion buff applies a Minion tag: the Eye counts as a *secondary* enemy, and its death is explicitly non-fatal to the encounter. Combat ends when Fogmog dies; the Eye is simply removed with the fight. Its own death animation is gated on no primary enemy being alive — until Fogmog is dead, the Eye visibly stuns rather than dies.
- **Doom does not clear it.** The Eye is flagged to *not* disappear from Doom, so the player-side low-HP execution mechanic does not permanently remove it either — the standard "sweep the chaff" answer is closed.
- **Zero threat, pure tax.** No damage, no block, no buffs to Fogmog, no Strength gain of its own. Every point of pressure it exerts is deck dilution. Note the deliberate misdirection in presentation: it plays an attack animation and a slash hit effect for a move that cannot hurt you.
- **Summoned once.** Fogmog's summon is its opening move and its state machine never returns to it, so exactly one Eye exists per fight; because the Eye never leaves, there is never a second summon to punish.

## Scaling by act / ascension

- **Act:** none. Act 1 (`Overgrowth`) content only, single encounter. No number on this creature reads the act index; the only act-derived factor that touches it is the multiplayer HP scaler (act index 0 → ×1.1).
- **Ascension:** **none on the Eye.** Its HP is a fixed 6 at every ascension, and the Dazed count is a hard 3. The ascension bumps in this encounter all land on the parent: Fogmog's HP 74 → **78** at the *Tough Enemies* tier, and its Swipe 8 → **9** / Headbutt 14 → **16** at the *Deadly Enemies* tier. So on higher ascensions the Eye's relative cost *falls* — the 6 HP you spend to mute it is a smaller share of a bigger clock, while the junk it generates is unchanged.

## Multiplayer / seat-count adjustments

- **HP scales by seats; the tax does not shrink.** Enemy max HP is multiplied by (player count × act factor), 1.1 for a non-boss Act 1 room, truncated to an integer: **6 solo → 13 at two players → 19 at three.** The revive heals to that inflated maximum, so the recurring price of muting it roughly doubles and triples.
- **The status output is per seat, and that is the real co-op change.** The move targets every player creature, and the status-add helper runs the full count for each target independently. **Every player receives their own 3 Dazed, every turn** — 6 cards per turn across a duo, 9 across a trio. Party-wide dilution scales linearly with seats while the "off switch" gets 2–3× more expensive, so the cost-per-card-denied worsens on both sides at once.
- **The enemy block scaler is inert here** — the Eye has no block move.
- Dead players are skipped by the status delivery, and the revive/illusion behaviour is seat-count independent.

## Fight-class reasoning — `gimmick`

Per turn this creature demands **nothing defensively** — it deals zero damage, gains no block, and buffs nothing — so `spike` and `attrition` both mis-describe it, and at one body `swarm` is meaningless. What it demands is a repeated **resource-allocation ruling**: every turn you must decide whether to spend 6 (13 / 19 in co-op) damage that could have gone into Fogmog's ~74–78 HP clock in order to buy a single turn of clean draws, knowing the purchase never becomes permanent and that any debuff you invest in the body is destroyed by the kill you land. That "you can always answer it, you can never solve it" loop, plus the closed exits (Doom won't clear it, debuffs won't stick, its death won't end the fight), is a special rule setting the demand curve rather than a statline doing it. The near-miss is `mixed` — the encounter as a whole pairs a real attacker with this thing — but that belongs on Fogmog's dossier; the Eye's own contribution is entirely the gimmick.
