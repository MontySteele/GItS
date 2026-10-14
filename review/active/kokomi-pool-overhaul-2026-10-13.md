# Kokomi: the pool overhaul (2026-10-13)

**Why.** [USER]'s run on 0.2.5336: "the idea is interesting, but she still feels...
janky. A bunch of the Plan lines basically read 'get a bunch of block or a status
next turn,' and I wasn't able to come up with a satisfying combo with what I found.
I did have an interesting idea going with using Electro companions for poison
stacking, but the card drafts weren't usually very interesting. I think that her
direction is probably fine (archetypes centered around Plans vs reaction-driven
Sting effects, with Companion cards in the middle) and that this can probably be
fixed with an overhaul / clean-up of the card selection."

The direction stays: Plans on one side, reaction-driven Stings on the other,
Companions in the middle. This paper changes cards, not rules. The numbers below
come from the census (2026-10-13, 52 bot runs since the 10-12 re-founding plus
[USER]'s two runs; scratch packet, not committed).

## 1. What the census shows

- **Most Plan lines do what a card already does, a turn later.** 30 of 78 cards
  have a Plan line: 8 deal damage, 5 give Block, 5 apply a debuff, 4 draw. Five
  apply Vulnerable to ALL enemies (Feint, Brine Sting, Spearhead, Undercurrent
  Snare, Opening Gambit). Three are "Block now or draw next turn" (Riptide Guard,
  Tidal Screen, Steady Tide).
- **The Plan lines that read the future are the good ones.** Flank (hits each
  enemy that intends to attack) and Tide Wall (Block plus the biggest incoming
  attack) are the only lines a now-card cannot copy, and Tide Wall is picked 17
  of 23 offers.
- **The reaction lane has no payoff of her own.** Electro-Charged applies 4
  Poison (`ReactionEffects.cs`), so Stings on an Electro aura stack Poison:
  that is the combo [USER] found. But her pool has no card that rewards a
  reaction except Grand Strategist (Plans only; never played) and At Water's
  Edge. The Companion bridge is Watatsumi Resistance (0 plays in 17 offers) and
  Coordinated Tide (1 pick in 29).
- **Six cards are dead weight** (picked 0 to 3 times in 14 to 25 offers, and
  barely played): Watatsumi Resistance, Reserves, Brace for the Tide, Ceremonial
  Garment, Moon's Reflection, and Riptide Guard, which repeats Tidal Screen.

## 2. Three things only a Plan can do

A Plan is written on her turn and lands at the start of her next one, after the
enemies have acted and with their next intents showing. The rewritten lines use
that window. These are readings of existing timing, not new rules:

- **Counter:** reads the enemy turn the Plan sat through. "since you planned
  this" = from the moment it was written until it is carried out.
- **Intent:** reads what enemies intend when it lands (Flank and Tide Wall
  today).
- **Chain:** counts the Plans carried out this turn, itself included, so
  landing several at once is a combo.

## 3. Rewrites (same name, rarity and cost unless noted)

| Card | Today's Plan or text | New |
|---|---|---|
| Kelp Wall (C) | Or plan: Gain 12 [15] Block. | Or plan: Deal Hydro damage equal to the damage you blocked since you planned this. *(Counter)* |
| Feint (C) | Or plan: Apply 1 [2] Vulnerable. | Or plan: Deal 5 [7] Hydro damage for each Plan carried out this turn. *(Chain)* |
| Brine Sting (U) | Or plan: Apply 1 Vulnerable to ALL enemies. | Or plan: Deal 8 [11] Hydro damage to each enemy that attacked you since you planned this. *(Counter)* |
| Undercurrent Snare (U) | Or plan: Apply 1 [2] Vulnerable to ALL enemies. | Or plan: Each enemy that intends to attack loses 3 [4] Strength this turn. *(Intent)* |
| Read the Field (U) | Or plan: Gain 10 [12] Block. | Or plan: Put a card from your Draw Pile into your Hand. |
| Coordinated Tide (U Power) | Whenever the Bake-Kurage carries out an Ethereal card, deal 6 [9]. | Whenever a Companion triggers an Elemental Reaction, add a Sting to your Hand. *(the bridge)* |
| Grand Strategist (R Power) | Whenever a Plan triggers an Elemental Reaction, deal 7 [10] to ALL. | Whenever you trigger an Elemental Reaction, deal 4 [6] damage to ALL enemies. |
| All Streams Flow to the Sea (R) | 4 [8], plus 2 per Sting played this combat. | Deal 5 [7] Hydro damage, plus 5 for each Elemental Reaction you triggered this combat. |

Spearhead and Opening Gambit keep their Vulnerable lines: one is the big Rare-feel
hit, the other is the Plan-doubling combo piece.

## 4. Cuts and the six cards that replace them

Each new card takes the slot of a cut card of the same rarity, so the pool stays
at 78 (20 / 38 / 20).

| Out | In | Text |
|---|---|---|
| Riptide Guard (C) | **Turning Tide** (C Attack, 1) | Deal 7 [10] Hydro damage. Or plan: Deal 4 [5] Hydro damage to ALL enemies for each Plan carried out this turn. *(Chain)* |
| Reserves (U) | **Brine Spray** (U Attack, 1) | Deal 5 [7] Hydro damage. If it triggers an Elemental Reaction, add 2 Stings to your Hand. |
| Brace for the Tide (U) | **Jellyfish Current** (U Power, 1) | Whenever a Sting triggers an Elemental Reaction, add a Sting to your Hand. *(upg: Innate)* |
| Moon's Reflection (U) | **Prepared Retreat** (U Skill, 1) | Gain 7 [10] Block. Or plan: If an enemy attacked you since you planned this, gain 1 [2] Energy. *(Counter)* |
| Ceremonial Garment (R) | **Battle Formation** (R Power, 1) | Whenever 3 or more Plans are carried out in one turn, gain 1 Energy and draw 2 cards. *(upg: Innate)* |
| Watatsumi Resistance (R) | **Turnabout** (R Skill, 2, Exhaust) | Play on the Bake-Kurage. Plan: Deal damage equal to all the damage enemies dealt you since you planned this, blocked or not, to ALL enemies. *(Counter)* |

**Readings a builder needs:**
- "Damage you blocked" counts Block that absorbed enemy attack damage.
- "Attacked you" means an enemy Attack intent that targeted her.
- Each Chain line counts itself.
- A Sting "triggers" a reaction when its own hit reacts.
- Jellyfish Current does not loop forever, because each reaction consumes the aura. That puts it in the thin-deck loop rule's known set, not a fix list.

## 5. What a draft now offers

- **Plans:** Feint, Turning Tide, Kelp Wall, Brine Sting and Prepared Retreat
  at Common and Uncommon give the Plan deck lines worth landing together.
  Battle Formation and Turnabout are the Rare payoffs, beside Nereid's
  Ascension and Sango Isshin.
- **Stings and reactions:** Brine Spray, Jellyfish Current, the new All Streams
  and Grand Strategist make an Electro or Cryo Companion turn Stings into
  Poison or Frozen engines.
- **Companions in the middle:** Coordinated Tide pays both sides. A Companion
  written as a Plan already reacts with the Bake-Kurage's Hydro (rule 8), so it
  makes Stings.

## Picks

1. **The Plan verbs** (sec.2–3: Counter, Intent, Chain rewrites).
   **(a) Default:** build all eight rewrites. (b) Build them but keep Feint's and Kelp
   Wall's old lines. (c) Different verbs; say which.
2. **The six cuts and six new cards** (sec.4). **(a) Default:** as written.
   (b) Name any to keep or drop.
3. **What follows.** **(a) Default:** build, then a two-seat round on the new
   pool (a new card batch), then your next Kokomi run. (b) Five seats instead
   of two.

## Ruled 2026-10-13

[USER]: "On Kokomi, I'm good with default on 1 and 2. We'll want a 5 seat run on
this, but I'll likely be back after the Varka run concludes to do the Furina test
first."

Pick 1 (a), pick 2 (a), pick 3 (b): five seats on the built pool, after
[USER]'s Furina run.
