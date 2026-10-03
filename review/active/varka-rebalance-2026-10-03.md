# Varka: elements that borrow from each other

Status: ALL FOUR PICKS RULED 2026-10-03; Storm Battery's cost is open (pick 5).
Main session design, on [USER]'s direction (2026-10-02 and 10-03).

[USER], 2026-10-03: "Otherwise the picks in 1 make sense" (Absolute Zero
excepted, §2); "Agreed on 3"; on 2, "can we do a cross-check against
similar cards on the base game and see if these are reasonably priced?"
(§3); on 4, "My favorite answer would be '4 different but equally balanced
starter cards, one per element' If we can pull it off somehow." (§5). On the
revised picks 2 and 4: "Otherwise all picks make sense."

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
  - Absolute Zero (revised on [USER]'s note: "it used to read 'all enemies
    are always weak and vulnerable if you swirl at least once per turn' ...
    both conditions being ridiculously strong as multiplayer payoffs, that
    is a sizeable nerf to cross damage output"): it stops being a team-wide
    debuff and becomes Cryo's missing status payoff (identities paper §6).
    Rare Power, 2: "Whenever you apply [gold]Weak[/gold] or
    [gold]Vulnerable[/gold] to an enemy, deal damage equal to your Cryo
    [gold]Oath[/gold] to it." Base analogues: Necrobinder's Shroud (U, 1:
    3 [4] Block each time you apply Doom), the "pays on applying a debuff"
    shape at Uncommon; this one scales with Cryo Oath, so Rare. Fed by
    Mika, Kaeya, Glacial Edict, Frost Ward and Cryo Swirls.

So borrowing a card costs you Oath growth (only Pyro cards grow Pyro Oath),
never your payoff. Staying in one element builds one Oath high. Mixing gets
reactions going.

## 3. Hydro: Block that scales, not big Block

[USER]: "the direction for Hydro should NOT be 'generic big block cards that
does Hydro' but rather flavors of scaling block ... I think that 'generic
big numbers card' is really what we want to put into Anemo."

| Card | Rarity | Today | Becomes | Scales with |
|---|---|---|---|---|
| Barbara: Gleeful Songs | C | Apply Hydro to ALL. Gain 5 [7] Block. | Apply Hydro to ALL enemies. Gain 4 [6] Block, plus 3 [4] for each enemy it reacts on. | reactions (needs other appliers) |
| Rippling Guard (new; replaces Wind Wall) | C | Wind Wall: Gain 7 [10] Block, 3 more with a current element. | Apply Hydro to an enemy. Gain 3 Block, plus 2 [3] for each other card you played this turn. | cards played |
| Barbara: Whisper of Water | U | Hydro. Block now and next turn. | Apply Hydro to an enemy. Gain 4 [6] Block now and at the start of your next 2 turns. | delayed |

**Priced against the base game** (the base cards read from the game's own
code; full table in this session's scratchpad, `base-block-census.md`). A
cost-1 Common Skill buys about 8 [11] Block with a small rider: Shrug It Off
8 [11] and draw 1, Gather Light 8 [11] and a Star, Leap 9 [12] alone.
- **Gleeful Songs.** The first draft, 3 [4] per reacting enemy and nothing
  else, gave 3 against one enemy: far under the line. With a 4 [6] floor it
  is 7 [10] when one enemy reacts and 13 [18] when three do, plus the Hydro
  aura on all. Taunt (C, 6 [7] and Vulnerable) and Shrug It Off bracket it.
- **Rippling Guard.** The first draft, 2 [3] per other card, gave 4 to 6 on a
  normal turn. With a 3 floor it is 7 [9] as the third card and 9 [12] as the
  fourth. The base scales the same way only at Uncommon or as a 0-cost
  Skill (Rage: 3 [5] per Attack, this turn only), so a Common pays with a
  floor.
- **Whisper of Water.** 12 [18] over three turns, plus Hydro. Dodge and Roll
  (C: 4 [6] now and again next turn, 8 [12] in all) and Glitterstream (C,
  cost 2: 11 [13] now and 5 [7] next turn) bracket it; the third turn is
  what an Uncommon adds.
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
| Electro | a big hand | **Storm Battery** (U Attack, 1 proposed, was 2; replaces Gust Ward): "Deal 2 [3] Electro damage to ALL enemies for each other card in your hand." | the twelve generic draw cards |
| Cryo | auras on enemies | **Frost Ward** (C Skill, 1; replaces Favonius Drill): "Apply 1 Weak to each enemy with an aura. Gain 3 [4] Block for each." | every applier, AoE appliers best |

**Storm Battery's price (open).** [USER]: "played in a fresh hand of 5,
that's 2 energy to AoE for 8 when the going rate on commons is to aoe for 5
or 6 for 1 energy ... I'm not sure if dropping to 1 energy would be balanced
at Uncommon." The base cards (read from the game's code): Dagger Spray (C, 1:
4 [6] twice to ALL, so 8 [12]), Breakthrough (C, 1: 9 [13] to ALL),
Thunderclap (C, 1: 4 [7] and Vulnerable to ALL), Echoing Slash (U, 1: 10 [13]
to ALL). Proposed: **cost 1, numbers unchanged.** Played first from a fresh
hand it is 8 [12], Dagger Spray's number one rarity up; played third it is
4 [6]; it beats Echoing Slash only with a draw engine (7 cards in hand: 12
[18]).

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

So the three earn their slots. The change is to the Knight itself: four
different starters, one per element, each keeping some Block (the start is
decided by Block) and adding its element's job. The sim balances them.

| Starter Knight | Text (first numbers; the sim moves them) | Job |
|---|---|---|
| Amber: Precise Shot | Deal 7 [10] Pyro damage. Gain 5 [6] Block. | the hit |
| Barbara: Glorious Season | Gain 6 [8] Block. Apply Hydro. Next turn, gain 3 [4] Block. | delayed Block |
| Lisa: Induced Aftershock | Gain 6 [8] Block. Apply Electro. Draw 1 [2] card(s). | draw |
| Kaeya: Hidden Strength | Gain 5 [7] Block. Apply Cryo and 1 Weak. | statuses |

Base yardsticks: Silent's starter Survivor (8 [11] Block, discard 1),
Backflip (C, 5 [8] Block, draw 2) and Necrobinder's Defy (C, 6 [9] Block and
1 Weak, Ethereal). [USER] on the first draft: Lisa "looks weak ... the
upgrade looks weaker", so her upgrade draws 2; Kaeya "is closer to
Necrobinder's Defy ... Ethereal cards often run hot", so without Ethereal
her Weak stays 1 when upgraded. "Amber and Barbara are solid." The bar: the four starters' act-1 win
rates within 5 points of each other, tighter than the 10 points the sim
reached before only by making them identical.

**The starter ruling, 2026-10-03.** After the seat round
(`review/records/varka-rebalance-round-2026-10-03.md`: Windbound Execution
NEVER AGAIN in all four records). [USER] on Ascension: "I do think that we
should consider modifying Ascension to be 2 cost with Retain, similar to
Regent's Sovereign Blade." On Windbound: "What about making it single target
but 0 energy? It nerfs his AoE output but we already found that we print too
many AoE cards." Then: "Sounds good! Please proceed." Four Winds' Ascension
costs 2 (was 1), gains Retain, and deals 10 [13] Anemo (was 6 [9]), then
3 [4] per Oath as before. Windbound Execution costs 0 (was 1) and deals 4 [6]
Anemo to one enemy (was to ALL); it still Swirls by the element rules, the
Swirl's flat 2 to all and its spread unchanged. Wolf's Gravestone and Darv's
Dusty Tome stay as written.

## 6. Before the build

Rerun `tools/varka_expansion_sim.py` on the new pool. The bars:
- every mono deck and the mixed deck within 10 points of each other;
- each element's deck plays at least three cards of another element;
- no new card dominant or dead.

The numbers above move with the sim. Then a Varka seat round.

Sim 2026-10-03 (PR #863): at the paper's numbers the starters spread 7.6 points; Amber Block 5 and Lisa Block 6 bring it to 1.6. Element decks within 10.4 of the default drafter and 9.3 of the mixing deck.

Sim after the starter ruling (2026-10-03, 2,400 seeds paired against main): the default drafter's act 1 rises 22.9 to 29.4 (+6.5); the starters 29.0 / 29.2 / 31.0 / 28.5, a spread of 2.5 (was 1.6); element decks within 11.2 of the default drafter and of the mixing deck (were 10.4 and 9.3); the default drafter's multi-target share in fights with two or more enemies falls 40.3% to 30.2%.

## Picks

1. **The Oath rule (§2):** RULED. Open only on the revised Absolute Zero (a
   status payoff that reads Cryo Oath). Default: yes.
2. **Hydro scales (§3), at the base-game prices:** RULED. Gleeful Songs 4 [6] plus
   3 [4] per reacting enemy; Rippling Guard 3 plus 2 [3] per other card;
   Whisper of Water 4 [6] for three turns.
3. **Borrowing payoffs (§4):** RULED.
4. **The starter (§5):** four different starter Knights, one per element,
   balanced by the sim to within 5 points; Strike, Defend, Windbound
   Execution and Ascension unchanged. RULED. (Both changed by the starter
   ruling of 2026-10-03, end of §5.)
5. **Storm Battery at cost 1 (§4),** numbers unchanged. Default: yes.
