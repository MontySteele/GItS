# Varka: elements that borrow from each other

Status: PICKS OPEN. Main session design, on [USER]'s direction (2026-10-02
and 10-03).

## 1. Why

The co-op run (2026-10-02): Varka "seemed very fun, and had a trivial time
generating massive amounts of block and card draw, but my friend never saw
any of the Electro payoffs for discarding cards." [USER]'s diagnosis: "we're
splitting his deck space 6 ways ... and each element has its own
mini-payoffs and mini-engine ... Hydro has a deeper 'pool' because you can
steal all the block cards of all 4 elements." The aim: "each element's
intended 'payoff' ... universal enough that it can steal some cards from at
least one other element," with "the tradeoff inherent between 'get reactions
going' vs 'build one Oath really high'."

The census (all 78 rows of `docs/prototype-surface.yaml`) bears it out:

| Engine | What its payoff eats | Cards that feed it | From other elements |
|---|---|---|---|
| Hydro | Block | about 23, plus the starter Knight | about 19 |
| Anemo (Gale) | fresh auras | about 23 appliers | all of them |
| Pyro | Pyro Oath, while Pyro is current | 5, plus about 6 generic Oath cards | about 2, and each switches you off Pyro |
| Electro | discards | 2 (Short Circuit, Violet Storm) | 0 |
| Cryo | Weak and Vulnerable | 3 | 0; no status payoff below Rare |

Hydro and Anemo eat what every element makes. Pyro, Electro and Cryo eat
what only they make, and two of their payoffs (Wildfire Oath, Absolute Zero)
switch off when a borrowed card changes the element.

## 2. The Oath rule

[USER]: "Anemo's gimmick might be reading the active Oath, while others just
read whatever Oath level you're at in their element whether or not it's
active ... if any cards were balanced around needing to still be in that
element to use the Oath, we downscale appropriately."

- **Element cards read their own element's Oath, current or not.** Blazing
  Charge, Tidal Bulwark, Glacial Edict, Thundering Verdict and Retaliating
  Tide already do; nothing changes for them.
- **Anemo and generic cards read the current element's Oath.** Four Winds'
  Ascension, Oathsworn Strike, Azure Devour, Northwind Avatar, Eye of the
  Storm, Oath of the Knights and the other Focus readers already do.
- **The two that need the current element lose that condition and get
  smaller:**
  - Wildfire Oath: "Your first Attack each turn deals additional damage
    equal to half your Pyro Oath." (Was the full Oath, only while Pyro is
    current.)
  - Absolute Zero: "Your Swirls apply 1 Weak to ALL enemies." (Was Weak and
    Vulnerable, only while Cryo is current.)

So borrowing a card costs you Oath growth (only Pyro cards grow Pyro Oath),
never your payoff. Staying in one element builds one Oath high. Mixing gets
reactions going.

## 3. Hydro: Block that scales, not big Block

[USER]: "the direction for Hydro should NOT be 'generic big block cards that
does Hydro' but rather flavors of scaling block ... I think that 'generic
big numbers card' is really what we want to put into Anemo."

| Card | Rarity | Today | Becomes | Scales with |
|---|---|---|---|---|
| Barbara: Gleeful Songs | C | Apply Hydro to ALL. Gain 5 [7] Block. | Apply Hydro to ALL enemies. Gain 3 [4] Block for each enemy it reacts on. | reactions (needs other appliers) |
| Rippling Guard (new; replaces Wind Wall) | C | Wind Wall: Gain 7 [10] Block, 3 more with a current element. | Apply Hydro to an enemy. Gain 2 [3] Block for each other card you played this turn. | cards played |
| Barbara: Whisper of Water | U | Hydro. Block now and next turn. | Apply Hydro to an enemy. Gain 4 [5] Block now and at the start of your next 2 turns. | delayed |
| Tidal Bulwark | U | unchanged | | Hydro Oath |
| Barbara: Wellspring Hymn | U | unchanged (cleanse, Exhaust) | | |
| Retaliating Tide | R | unchanged (Block becomes damage, capped by Hydro Oath) | | the payoff |

The flat, generic Block in Anemo stays as Jean — Wind Companion ("Gain 7
[10] Block. Swirl"), Eye Wall and Wall of Gales. Wind Wall, Favonius Drill
and Gust Ward leave (§4), so the generic Block pool shrinks by three.

## 4. Payoffs that borrow

| Element | Payoff | Card | Borrows |
|---|---|---|---|
| Pyro | a hit that grows when it reacts | **Kindled Edge** (C Attack, 1; replaces Cavalry Charge): "Deal 7 [10] Pyro damage. If it sets off an Elemental Reaction, deal 7 [10] more." | every Hydro, Cryo and Electro applier (Vaporize, Melt, Overload) |
| Electro | a big hand | **Storm Battery** (U Attack, 2; replaces Gust Ward): "Deal 2 [3] Electro damage to ALL enemies for each other card in your hand." | the twelve generic draw cards |
| Cryo | auras on enemies | **Frost Ward** (C Skill, 1; replaces Favonius Drill): "Apply 1 Weak to each enemy with an aura. Gain 3 [4] Block for each." | every applier, AoE appliers best |

Wildfire Oath stays as the stay-on-Pyro payoff and Kindled Edge is the mixing
one; Glacial Edict and Absolute Zero stay as Cryo's. The discard cards
(Short Circuit, Chain Lightning, Violet Storm) remain an Electro branch, and
Charged Lunge is unchanged.

The pool stays 78 (20 / 35 / 23): three Commons and one Uncommon replaced,
four rewritten.

## 5. The starter

[USER]: "I wonder if the rotations starter block card is actually healthy or
if it incentivizes the Block / Hydro playstyle too much ... I wonder if those
3 are actually the optimal idea here."

Today: Strike x4, Defend x4, Windbound Execution (4 [6] Anemo to ALL, his
Swirl card), one random starter Knight ("Gain 8 [11] Block. Apply its
element"), and Four Winds' Ascension from Boreas's Fang on his first Oath
(Regent's Sovereign Blade is the model).

- The starter Knight is not a Hydro card: three of the four are other
  elements, and each gives the same 8 Block. The sim gave the starters
  equal Block on purpose: with Barbara alone giving Block, Hydro won 50% of
  act-1 runs and the others 7 to 16% (`varka-paper-kit-2026-09-28.md` §5).
  The Hydro pull is the pool's 19 off-element Block cards, which §3 and §4
  cut.
- Windbound Execution is the only Swirl in the starter. Ascension arrives
  only after the first Oath, and the Knight is what makes that Oath.

So my read is that the three earn their slots. The alternative is starter
Knights that teach their element's job, at the cost of reopening the act-1
gap: Amber "Deal 8 [11] Pyro damage", Barbara "Gain 8 [11] Block. Apply
Hydro", Lisa "Apply Electro. Draw 2 [3] cards", Kaeya "Apply Cryo and 2 [3]
Weak".

## 6. Before the build

Rerun `tools/varka_expansion_sim.py` on the new pool. The bars:
- every mono deck and the mixed deck within 10 points of each other;
- each element's deck plays at least three cards of another element;
- no new card dominant or dead.

The numbers above move with the sim. Then a Varka seat round.

## Picks

1. **The Oath rule (§2):** element cards read their own Oath, Anemo and
   generic cards read the current one; Wildfire Oath and Absolute Zero lose
   the condition and shrink. Default: yes.
2. **Hydro scales (§3):** Gleeful Songs and Whisper of Water rewritten,
   Rippling Guard replaces Wind Wall. Default: yes.
3. **Borrowing payoffs (§4):** Kindled Edge, Storm Battery and Frost Ward
   replace Cavalry Charge, Gust Ward and Favonius Drill. Default: yes.
4. **The starter (§5):** (a) keep it as is (default); (b) starter Knights
   that teach their element's job.
