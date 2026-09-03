# KLEEMOD-KOKOMI — blind seat, lane 1, run 3, act 2

## Identity (running; completed block at the end)

- **Model / seat:** Claude Opus, blind TESTER seat, round 5, run 3, **second of three chained seats**.
- **Lane:** 1. **Character:** KLEEMOD-KOKOMI.
- **Picked up:** on the **act-2 map screen**, act 1 cleared by the first seat, Vantom dead, HP **39/90** as the last reading act 1 printed.
- **Act:** 2. The map names the top of the act: **The Insatiable**. Sixteen floors to it.
- **Actions accepted / refused:** *(running count in the completed block at the end)*
- **Termination reason:** *(at the end)*

### The act-2 map as printed on arrival

```
- 1 floor ahead: Ancient
- 2 floors ahead: Monster, Monster, Monster, Monster
- 3 floors ahead: Monster, Monster, Monster, Unknown, Monster
- 4 floors ahead: Monster, Unknown, Monster, Monster, Unknown, Shop
- 5 floors ahead: Unknown, Monster, Unknown, Monster, Unknown
- 6 floors ahead: Unknown, Unknown, Monster, Monster, Shop
- 7 floors ahead: Elite, Monster, RestSite, Monster, Monster
- 8 floors ahead: Monster, Elite, Monster, RestSite
- 9 floors ahead: Treasure, Treasure, Treasure
- 10 floors ahead: Monster, Elite, Elite, Unknown
- 11 floors ahead: Shop, RestSite, Unknown, RestSite
- 12 floors ahead: RestSite, Monster, Elite, RestSite, Elite
- 13 floors ahead: Monster, Unknown, Monster, Monster
- 14 floors ahead: Monster, Monster, Monster, Elite, Elite, Monster
- 15 floors ahead: RestSite, RestSite, RestSite, RestSite, RestSite
- 16 floors ahead: Boss
```

Only one opening was offered — `Ancient (path 1)`, leading on to four Monsters — so floor 1 was not a routing choice. Note the shape of this act against act 1: **no Treasure until floor 9, no RestSite until floor 7**, and floors 1–6 are Monster/Unknown/Shop only. At 39/90 that is six rooms of attrition before the first place to heal.

**Carried plan on arrival.** From the previous seat's record I hold: HP 39/90, potions **full at 3/3** (Gambler's Brew, Skill Potion, Explosive Ampoule), ~316 gold by the first seat's own count (no screen has ever confirmed it), six relics, and a 22-card deck. Two standing intentions: (1) **spend a potion during a fight** so a slot is open when its reward screen appears — the previous seat lost two potions to full slots and proved a reward screen has no `use potion` form; (2) at 39/90, route toward the floor-4 or floor-6 Shop and then the floor-7/8 RestSite.

---

## Running log

### Ancient — Tezcatara (floor 1)

Three relics offered, no cost printed on any of them:

- **Very Hot Cocoa** — "Start each combat with an additional 4[Energy]."
- **Toasty Mittens** — "At the start of your turn, Exhaust 1 card from your Hand and gain 1 Strength."
- **Toy Box** — "Obtain 5 Wax Relics. Every 3 combats, your left-most Wax Relic will melt away."

**Reasoning.** The previous seat's conclusion was that *energy, not cards, is the binding constraint* of this deck, and Very Hot Cocoa buys exactly that, deterministically, in every combat. Toasty Mittens exhausts a card from hand **every** turn in a 22-card deck whose power is concentrated in singletons (Sango Isshin, Shinobu — Sanctifying Ring, Battle Plan): over a 4-turn fight that is four cards gone, and the text does not say whether I choose which. Toy Box is five unknown relics that decay — blind, five unnamed items with an expiry is the one option whose value I could not price at all from the screen.

**Took Very Hot Cocoa.** It was confirmed on the very next screen: the first combat opened at **Energy 7/3**. The relic is a one-shot +4 on the opening turn, not a permanent +4 — round 2 read `Energy 3/3`.

### The 40 HP nobody mentioned

The act-1 record's last printed HP reading was **39/90** (boss round 6). The first act-2 combat opened at **HP 81/90**, and Blood Vial's "+2 at the start of each combat" accounts for 2 of that, so I entered the fight at **79/90**.

**Between the act-1 boss's death and the first act-2 fight, ~40 HP appeared, and no screen I saw said anything about it.** The Ancient event printed only three relic names; the boss reward screen is in the previous seat's record and printed only gold and a card. Whatever heals on an act transition, it is not announced.

### Fight 8 — Exoskeleton ×3 (28 / 24 / 27 HP), floor 2

The routing choice was between four Monster nodes; `Monster (path 3)` was the only one leading on to an **Unknown** rather than another Monster, and at what I believed was low HP the cheapest room is the one that is not a fight. (It turned out I was at 79, not 39 — see above.)

The board's whole character was one buff, on all three:

> `Hard To Kill 9 (buff) — Reduce all damage taken and HP lost by Exoskeleton to 9.`

**Read as a per-instance damage cap of 9, and that read was confirmed twice.** Red Mask's opening Weak fired the Tamakushi Casket for the full **2** on each of the three (28→26, 24→22, 27→25) — under the cap, so unreduced. Then Explosive Ampoule's printed "Deal 10 damage to ALL enemies" landed as **exactly 9 on each** (26→17, 22→13, 25→16). A 10 became a 9; a 2 stayed a 2.

*(This is also a clean second data point on the previous seat's unexplained Casket variance: three enemies on the board, and each took the **full 2**, where three Inklets in act 1 each took only 1. Board size is not the variable.)*

**This buff inverts the deck.** Sango Isshin's big mode — "a quarter of your Max HP to ALL", i.e. 22 — is worth 27 total here instead of 66, while a plain **Strike deals 9, exactly the cap**, and the Casket's 2-damage pings are untouched. Many small instances beat few big ones, which is the reverse of every fight in the previous seat's record.

**Turn 1 (7 energy).** Intents: `0 damage 3 times`, `6 damage`, `Empower` — about 6 incoming, so Block was nearly dead and the energy was free. My hand was four Block cards and Sango, with **no Plan card**, so the Bake-Kurage could not be armed and Sango's conditional could not be turned on.

I spent **Explosive Ampoule** here deliberately, on the standing intention carried from act 1: three enemies is the potion's maximum-value board (27 damage against a 73-HP field), Hard To Kill cost it only 1 damage, and spending it *during* the fight is the only way to have a free slot when the reward screen appears. Then Sango for its base 8 into the lowest body (13→5), and Kirara, Thoma and both Defends with the free energy — 28 Block against 6 incoming, deliberately wasteful, but the alternative was to waste the energy instead.

Predicted 27 + 8 = 35 damage and 0 taken. **Got exactly that.**

A display defect on this screen: `Blazing Barrier 6 (buff) — {Left} Block left. When it absorbs damage, gain 3 Block.` — the `{Left}` placeholder is never substituted.

**Turn 2 (3 energy)** — and the run's one refusal so far. Kirara's delayed hit had landed for 9 (17→8). I sent three cards as one chain: Strike on Exoskeleton (1), Slack Water on Exoskeleton (3), Coral Bulwark.

**The Strike killed Exoskeleton (1), and the survivors immediately renumbered** — the 5-HP one became `(1)` and the 16-HP one became `(2)`. There was no longer an `Exoskeleton (3)`, so the second command was refused and the chain aborted before Coral Bulwark. **Enemy indices are positions in a list that is re-counted the instant a body dies, so a multi-card plan written against the pre-turn numbering breaks the moment it works.**

Re-sent against the new numbering. Slack Water into the 16-HP body: 7 damage plus the Casket's 2 off the Weak = **16 → 7**, exactly 9, and the Weak visibly cut the printed intent from `3x3` to `2x3`. Coral Bulwark's 7 Block covered the 6 that came in. **0 damage taken.**

(Contrast with act 1's Red Mask finding: a Weak I apply *during my own turn* changes the printed intent number on the spot. Red Mask's combat-start Weak never did.)

**Turn 3.** Two bodies at 5 and 7, both intending 10 — 20 incoming, which is the first genuinely dangerous turn of the act. Strike (9) killed the 7, Gorou (8) killed the 5. Fight over on two cards.

**Fight 8 result: won on turn 3, HP 81/90, ZERO damage taken.** One potion spent (Explosive Ampoule), by design.

**Reward:** `13 Gold`, card. Offer was **Rally** · **Coral Bulwark** (2nd) · **Battle Plan** (2nd) · **Gorou — General's War Banner** (cost 1, "Gain 2 Dexterity for 2 turns").

**Took Battle Plan.** It is the one card that pays its own energy back and draws two, it is itself a Plan card so it arms Sango on the turn it resolves, and a second copy raises the odds of the turn the previous seat's record calls the run's biggest (Battle Plan resolving into 4 energy and a 9-card hand). Rally is finally playable now that `Companion` has been defined and I own five of them, but it is a conditional discount; War Banner is Block-shaped in a deck that took 0 damage this fight.

### Event — The Lantern Key (floor 3), and Fight 9 — Mysterious Knight (101 HP)

The event printed exactly two lines and nothing else:

> - **Return the Key** — Gain 100 Gold.
> - **Keep the Key** — Fight to obtain the Key.

**Nothing on the screen says what the Key is, what it does, or how hard the fight is.** I took the fight, on the reasoning that at 81/90 HP was the resource I had most of, a rest site was five floors away, and an extra fight also pays gold and a card.

That reasoning was half right and half lucky. The fight was **elite-grade**:

> **Mysterious Knight — HP 101, Block 6**
> `Strength 6 (buff)`, `Plating 6 (buff) — At the end of your turn, gain 6 Block. Plating is reduced by 1 at the start of your turn.`
> Intent: Attack for **15**.

It cost me **27 HP** (83 → 56) and four turns. The event offered no way to price that against the 100 gold.

**Turn 1 (7 energy from Very Hot Cocoa).** Hand again had no Plan card, so Sango's big mode was off. I sequenced for the elements rather than for the damage: **Gorou first** (Geo consumes the Hydro aura for Crystallize Block), **Thundergrust** second (Electro onto a now-bare body, so it *applies* Electro instead of reacting), **Sango** third (Hydro onto the Electro aura → **Electro-Charged**, whose Poison is a debuff, so the Casket fires 2 Hydro and re-applies Hydro), then Strike and Defend. The alternative ordering (Gorou last) deals the identical 29 damage but ends with the enemy bare; this one ends with a Hydro aura standing for next turn's Electro.

Predicted 29 damage. **Got exactly 29 (99 → 70)**, with `Poison 4` and `Hydro Aura 2` on the body afterwards.

**But my Block came to 12, where I had predicted 15 — and the shortfall is a real rule.** Gorou reads "Gain Block equal to half **the damage dealt**". The enemy's 6 Block absorbed 6 of Gorou's 8, so only 2 reached HP, and Gorou paid **1** Block (+1 Dexterity = 2) rather than 4 (+1 = 5). Add Crystallize's 4 and Defend's 6 and you get exactly 12. In act 1 Gorou always hit unblocked bodies, so the two readings were indistinguishable; here they separate. **Gorou's Block scales with post-Block damage, so the card is worth least against a blocking enemy — which is exactly the enemy you want Block against.**

**The third Red Mask data point, and it is negative again.** Block 12 against a printed intent of 15 with `Weak 1` visibly on the enemy. If the Weak had applied, 15 × 0.75 = 11 and I take 0. **I took 3** (83 → 80). Red Mask's combat-start Weak did nothing to the first attack, for the third time in this run.

**Turn 2.** Intent escalated to `15x2` = 30. Played **Ambush → Plan**, **Kirara** (9 Block, 10 next turn), **Strike**. Took 21 (30 − 9). HP 80 → 59.

**Turn 3 — the free turn, spent entirely on setup.** Intent was `Empower (Buff)`, so Block was dead. Played **Shinobu — Sanctifying Ring** and **both Battle Plans onto the Bake-Kurage**. The Kurage printed:

> Planned, and carried out at the start of your next turn in this order **(2)**:
> 1. **Battle Plan**
> 2. **Battle Plan**

confirming the previous seat's undocumented finding that Plans stack, and this time with two copies of the same card.

**Two mechanical facts fell out of this turn's arithmetic.** The enemy went 43 → 30, which decomposes as Shinobu's Electro **5** + the Casket's **2** + a Poison tick of **6**. Two things follow:

1. **Poison ignores enemy Block.** The Knight went into its turn holding Plating Block and still lost the full Poison tick; the Block was untouched and was still standing on my next turn. Against a Plating enemy this is the only damage that does not have to be paid for twice.
2. **Electro-Charged stacks onto an existing Poison count** — Poison was at 2, the reaction added 4, and the tick that landed was **6**, leaving `Poison 5`. This confirms the previous seat's stacking finding on a fresh case.
3. **Plating grants one less Block than the number it prints.** During my turn 2 it printed `Plating 6` and granted 5 (the arithmetic of the next turn's damage only closes at 5); during turn 3 it printed `Plating 5` and granted 4. I could not find a reading of "reduced by 1 at the start of your turn" that matches what the screen shows *during* the turn.

**Turn 4 — the payoff.** Both Battle Plans resolved: **Energy 5/3 and a nine-card hand**, and a Plan had been carried out, so Sango was live at a quarter of 90 = **22**.

Enemy: 30 HP, Block 4, intending **18x2 = 36** into my 56 HP — a turn I could not afford to end without killing it. Needed 34 (30 HP + 4 Block); had 22 + 9 + 9 = 40 in three cards for four energy.

Sango 22 − 4 Block = 18 net (30 → 12), Strike 9 (→ 3), Strike 9 — **dead**, exactly as predicted, before the 36 landed.

**Fight 9 result: won on turn 4, HP 56/90, 27 HP spent.**

**Reward:** `15 Gold`, `Dexterity Potion`, **`Add Lantern Key to your deck.`**, card.

**The Key is a card, not a relic, and no screen ever printed its text** — not the event, not the reward line, which reads only "Add Lantern Key to your deck." I claimed it blind. (The Dexterity Potion was claimable because I had spent Explosive Ampoule in fight 8 — the act-1 lesson working as intended.)

Card offer: **Moon's Reflection** · **Feint** · **Rally+** (upgraded: "Apply 2 Weak") · **Sayu — Naptime** (cost 0, "Gain 4 Block. Next turn, draw 2 cards if you play no Attacks this turn").

**Took Moon's Reflection** — "Choose a card in your Exhaust Pile. Next turn, the Bake-Kurage carries out its Plan line, or plays it if it has none. Exhaust." My deck contains **exactly one** card that exhausts, Shinobu — Sanctifying Ring, and this fight proved that the Ring's Electro is what drives the Poison that bypasses enemy Block. Moon's Reflection is a second activation of the deck's only engine. Feint (6) is now strictly worse than my Strike (9); Sayu is a 0-cost 5 Block whose draw clause my Attack-heavy deck almost never satisfies.

### Fight 10 — Bowlbug (Rock) 45 + Bowlbug (Egg) 22, floor 4

**What the Lantern Key turned out to be.** It appeared in my opening hand:

> **Lantern Key** — cost 0, **quest**. "Unplayable. Unlocks a special event in the next Act."
> *CANNOT BE PLAYED: has unplayable keyword*

So the reward for a 101-HP elite that cost me 27 HP is a **permanent unplayable card in the deck** — a guaranteed brick in every hand for the rest of the run — in exchange for an event in act 3 that I will not reach in this seat. The event screen said only "Fight to obtain the Key"; nothing on it, on the reward screen, or anywhere else priced that against "Gain 100 Gold". **This is the one decision this act where I think the screen withheld what a player needed to decide.**

*(A useful side-observation from this screen: draw pile 20 + hand 5 = 25 cards, which is exactly my 22 from act 1 plus Battle Plan, Moon's Reflection and Lantern Key. **The two `Wound` status cards Vantom added in the act-1 boss fight did not persist** — they were combat-only.)*

**Turn 1 — and the best use Gambler's Brew will ever get.** Very Hot Cocoa gave 7 energy but the hand held only 4 energy of playable cards, two of which were dead: Lantern Key (unplayable) and Moon's Reflection (its exhaust pile was empty). Three energy would have been thrown away.

`use potion "Gambler's Brew"` opened a **card-selection screen** — "Choose any number of cards to replace", pick by title, then `confirm`. It carries an honest disclaimer: *"This screen's data feed did not answer which card is picked, so nothing in the list above can be marked as the one you chose. The `Confirm is` line below is the only thing that moves when a pick lands."* Replaced Lantern Key, Moon's Reflection and a Defend; drew Strike, Kirara and Sango's partner cards — a hand where all five were live.

**The board's rule was a printed invitation.** `Imbalanced 1 (debuff) — If Bowlbug (Rock)'s attacks are fully blocked, it becomes Stunned.` Rock intended 11, Egg 5 and a Defend: 16 incoming against the 15 Block I could buy (Kirara 9 + Defend 6). One short — unless I killed the Egg, which removes 5 from the total.

So: Slack Water (7 + 2 Casket = 9), Strike (9), Sango's base 8 all into the **Egg** — 26 into 20, dead — then Kirara and Defend for 15 Block against the Rock's lone 11.

**Predicted: 0 damage taken and the Rock Stunned. Both happened.** HP stayed 58/90 and the Rock's next screen read `Intent: Stunned (Stun) — This enemy can't act on its next turn.` Kirara's delayed 10 landed in the same beat (43 → 33).

**Turn 2 (free, because Stunned).** Strike, Strike, Gorou = 26 → Rock at **7/45**. Zero incoming.

**Turn 3 — the awkward one, and it decided itself on timing.** The Rock sat at 7 HP intending **15**, and my hand held **no attack card at all**: Kurage's Oath, Coral Bulwark, Thoma, Read the Field, Shinobu's Ring. Three energy.

The line I took was to kill it *without* an attack: **Kurage's Oath → Plan** (7 damage, exactly lethal, landing at the start of my next turn) plus **Thoma** (7) and **Coral Bulwark** (7) for 14 Block against 15. The alternative — three Block cards for 20 Block, fully blocking to Stun it again — takes 0 instead of 1 damage but adds a whole turn.

The fight ended before my turn 4 screen ever rendered, so the Plan killed it on schedule.

**Fight 10 result: won, HP 58/90, ZERO damage taken** (Thoma's "whenever this Block absorbs damage, gain 3 Block" appears to have covered the 1-point shortfall, but the fight ended before a screen could confirm it).

**Reward:** `10 Gold`, `Power Potion` (claimable — Gambler's Brew had opened the slot), card.

Offer: **Chain of Command** · **Moon's Reflection** (2nd) · **Tide Wall** ("Gain 4 Block. Plan: Gain 3 Block for each Plan the Bake-Kurage carries out this morning") · **Kujou Sara — Crowfeather Cover** (cost 0, "Your next Attack this turn deals 4 additional damage and applies Electro").

**Took Kujou Sara.** It costs **0**, so it never competes for energy, and its second clause is the piece the deck was missing: an on-demand **Electro applicator**. The Knight fight established that Electro-Charged Poison is the only damage in this deck that ignores enemy Block; Sara lets an ordinary colourless Strike trigger that reaction instead of waiting on Thundergrust or Shinobu's Ring. Tide Wall's "each Plan carried out this morning" never says whether "this morning" means the turn or the combat, and I could not price a card I could not read.

### Event — Ranwid the Elder (floor 5), the empty Shop (floor 6), Rest (floor 7)

Ranwid offered three trades, each for random relics:

> - **Give Power Potion** — Obtain a random Relic.
> - **Give 100 Gold** — Obtain a random Relic.
> - **Give Oddly Smooth Stone** — Obtain 2 random Relics.

**Gave Oddly Smooth Stone**, on the reasoning that two permanents beat one, and that "Start each combat with 1 Dexterity" was the weakest of my six relics — worth about +1 Block per Block card, where the Casket, Stone Humidifier and Strike Dummy are all load-bearing.

**The event never printed what I received.** It went straight to a `Proceed` screen. I did not learn the two relics' names until the next combat screen listed them:

- **Kusarigama** — "Every time you play 3 Attacks in a single turn, deal 6 damage to a random enemy."
- **Whetstone** — "Upon pickup, Upgrade 2 random Attacks."

Whetstone's effect was already spent by the time I could read it, and I never saw which two attacks it chose — I discovered them one at a time as they were drawn (**Strike+**, "Deal 12 damage", and later **Sango Isshin+**, whose upgrade turns out to be a cost cut from 2 to 1). The trade also silently removed my `Dexterity 1`: every Block face dropped by one (Defend 6 to 5, Coral Bulwark 7 to 6), which is the only way the screen told me the trade had gone through.

**The Shop was empty.** An `Unknown` node resolved into:

> # The shop
> You have 400 gold.
> On the shelves:
>
> *(nothing)*

I observed it twice to be sure. **A Shop node with 400 gold in hand and zero items on the shelves** — the only thing to do was `proceed`. This is also the first screen in either act to confirm a gold total: **400**, against the previous seat's uncounted estimate of 316 plus my 38 in act-2 rewards = 354. The running gold total is still not something a player can reconstruct from reward screens.

**Rest site (floor 7).** `Rest — Heal for 30% of your Max HP (27). Raise your Max HP by 5.` versus `Smith`. Took Rest at 58/90.

**HP 58/90 to 90/95: a gain of 32 where the screen promised 27.** This is the act-1 finding reproducing exactly — Stone Humidifier's +5 Max HP silently carries +5 *current* HP too. Sango Isshin's "quarter of your Max HP" went 22 to **23** in the same beat.

I chose Rest over Smith because Stone Humidifier makes a rest partly a *damage* upgrade (Max HP feeds Sango), and because a guaranteed all-RestSite floor still sits between me and the boss.

### ELITE — Decimillipede x3 (46 / 42 / 40 HP), floor 8

Routed here deliberately at 90/95: an Elite immediately after a rest is the cheapest an Elite ever gets.

The board's rule, on all three segments:

> `Reattach 25 (buff) — If other segments are still alive, revives in 2 turns with 25 HP.`

Read as: killing a segment piecemeal is a treadmill, so the deck's answer must be even damage across all three followed by one AoE that wipes them together. That shaped every turn — and **the rule turned out not to matter at all**, see below.

**Turn 1 (7 energy).** I spent **Power Potion** here — a long fight with spare energy is where a "free to play this turn" card is worth most, and it opened the potion slot. The three Powers offered were The General's Banner, Song of Pearls and:

> **The Moon Overlooks the Waters** — cost 2, power. "Plans also happen when played."

Free from the potion, so its 2 cost was irrelevant. **This card rewrites the deck**, and I come back to it below.

*(A display note: immediately after playing it, my status block listed only `Bake Kurage`. The `The Moon Overlooks The Waters 1 (buff) — Plans also happen when played.` line did not appear until the round-2 screen. For one whole turn a rule-changing Power was in play with nothing on screen saying so.)*

Then four Strikes spread deliberately to level the bodies: Strike+ (12) on the 42, two Strikes (18) on the 46, one Strike (9) on the 40 — chosen over the obvious "12+9 into the biggest" because it leaves 26/28/29 instead of 23/31/29, and levelling is what lets one AoE finish them. **Kusarigama fired once** for 6 (four Attacks played), landing on the 46. Result: 20 / 28 / 29, plus Defend for 5.

Took 11 (HP 92 to 81), and picked up `Weak 1` on **myself** from the Strategic intent. Worth recording: **my own attack cards visibly re-printed their reduced numbers** — Gorou 8 to "Deal 6 damage", Thundergrust 8 to "Deal 6 damage", Slack Water 7 to "Deal 5 damage". That is the mirror image of the previous seat's act-1 finding that attack cards hide their modified damage: a Weak *on me* is shown on the faces, while a Vulnerable *on the enemy* was not.

**Turn 2 — the interaction that decided the fight.** I played `Battle Plan` onto the Bake-Kurage and the panel answered:

> The Bake-Kurage carried these out **at the start of this turn**, front first:
>   - Bake-Kurage: Battle Plan, 1
> Planned, and carried out at the start of your next turn in this order (1):
>   1. **Battle Plan**
> **Plans also happen NOW as you write them.**

Three things fell out at once, none of them stated on the Power's one-line text:

1. **Every Plan card pays twice** — once immediately, once next turn. Battle Plan refunded its own energy and drew 2 on the spot (Energy stayed 3/3, draw pile 16 to 14) *and* stayed queued.
2. **The immediate half is logged as "carried out at the start of this turn"**, which is the exact phrase Sango Isshin's condition tests. **So a Plan written this turn arms Sango this turn.** That is a two-card combo the game never advertises.
3. Block Plans double as well: `Read the Field` planned gave **10 Block now and 10 more next turn** for one energy, and `Coral Bulwark` gave 8 Block + 1 Weak now and again next turn.

So turn 2 was: Battle Plan to the Kurage (free, +2 cards), **Sango Isshin+ for 23-to-ALL** — reduced by my own `Weak` to **17** — then Coral Bulwark and Read the Field to the Kurage for **18 Block immediately**, three energy in total.

Predicted 17 to each plus a 2-damage Casket ping on the front. Got exactly that: **20 to 1, 28 to 11, 29 to 12**, Block 18 against 26 incoming, HP 81 to 73. Sango's AoE mode also applied `Hydro Aura 2` to **all three** bodies.

**Turn 3 opened with three Plans resolving at once** (Energy 4/3, +2 cards, 18 Block already standing), and Coral Bulwark's queued Weak fired the Casket for 2, which **killed the 1-HP segment before I acted**.

Then the kill: **Kujou Sara** (0 cost) then **Slack Water** into the 11-HP segment = 5 (weakened) + 4 (Sara) + 2 (Casket, off the Weak) = **exactly 11**, dead. That left one body at 12, and `Ambush` written onto the Kurage delivered its immediate 12 through The Moon — **exactly lethal**.

**And here is the finding that mattered most: the fight ended instantly.** Two segments had died with other segments alive, so by the printed text two `Reattach` revives at 25 HP each were owed within two turns. **Neither arrived. Combat simply ended when the board emptied.** The buff that shaped my entire plan for this fight never did anything: killing the last body wins outright, and all the care about levelling damage for a simultaneous AoE was wasted effort. I cannot tell from any screen whether the revive is checked at revive-time or whether combat-end pre-empts it — only that the printed threat is empty.

**ELITE CLEARED in 3 turns, HP 73/95, 19 HP spent.**

**Reward:** `41 Gold`, **Potion Belt** (relic), card. Offer: Vanguard+ · Moon's Reflection+ · Shell Guard · **Mika — Starfrost Swirl** [Cryo] (cost 1, "Deal 5 damage to ALL enemies. Your next Attack costs 1 less").

**Took Mika.** It is close to net-zero energy, it is a third AoE card in a deck whose AoE was two cards, and by the glossary's own Frozen line — *"Bosses cannot be Frozen: Hydro plus Cryo is consumed and applies 2 Vulnerable instead"* — a Cryo hit onto the Hydro aura the Tamakushi Casket keeps re-applying is a **repeatable 2-Vulnerable source against the boss**. Vanguard+ delivers the same 2 Vulnerable for 0 energy but exhausts, so it is one use; Mika is every draw.

### Treasure (floor 9)

`Pen Nib — Every 10th Attack you play deals double damage.` Taken; nothing else on the screen. Later screens print it as **`Pen Nib (4)`**, i.e. the relic carries a live counter — the only relic in my list that shows its own progress.

### Fight 11 — Louse Progenitor (134 HP), floor 10

Routing: the choice was `Monster to Shop` or `Elite to RestSite`. I took the Monster line for the **Shop**, because I was holding 441 gold, the act's only other Shop had been empty, and a Card Removal would delete the Lantern Key. A guaranteed all-RestSite floor still sat before the boss, so the rest was not urgent.

`Potion Belt — Upon pickup, gain 2 potion slots.` — five slots now, which retires the act-1 problem of losing potions at reward screens.

The board's rule: `Curl Up 14 (buff) — Gains 14 Block upon first being hit.`

**Tested the trigger directly.** Red Mask's opening Weak had already fired the Casket for 2 (134 → 132) and Curl Up had **not** triggered. Then Slack Water: **132 → 123**, i.e. the card's 7 *and* the Casket's 2 both landed, and only then did `Block 14` appear and the `Curl Up` line vanish. So Curl Up triggers after the whole card resolves, and the relic ping that precedes the fight does not count as "being hit".

**Turn 1** also gave the fight's shape: Treatise, Shinobu — Sanctifying Ring, Thoma, Defend. The Ring's end-of-turn 5 Electro hit the Hydro aura for Electro-Charged, and **the entire 5 plus the Casket's 2 was eaten by Curl Up's Block — but the Poison it applied was not.** The enemy went 123 → 119, which is exactly the Poison tick of 4 and nothing else. **Poison bypassing Block is what makes this deck work against armoured enemies**, and this fight is the cleanest demonstration of it.

I also picked up `Frail 2 — Gain 25% less Block from cards`, and again **my own card faces re-printed the reduced numbers** (Defend 5 → 3, Thoma 6 → 4, Coral Bulwark 6 → 4).

**Turn 2 — the sequencing decision of the act.** A free turn (`Defensive` + `Empower`), hand of Kujou Sara (0), Strike, Thundergrust, Kirara.

Sara reads "Your next Attack this turn deals 4 additional damage **and applies Electro**". The obvious play is Sara onto Thundergrust, the big attack. **The correct play is Sara onto the ordinary Strike**, because Thundergrust already carries Electro:

- Sara → **Strike**: 9 + 4 = 13, applying Electro onto the Hydro aura → Electro-Charged → Poison, and the Poison is a debuff, so the Casket fires 2 Hydro **and re-applies the Hydro aura in the same beat**.
- **Thundergrust** then hits that freshly re-applied Hydro aura → a **second** Electro-Charged in the same turn.

Two reactions instead of one. Predicted 25 damage and Poison up by 8; the round delivered **119 → 72, 47 damage**, with Poison reaching **15**. Sara onto Thundergrust would have produced one reaction and roughly 23.

**Turn 3.** 72 HP, 19 incoming. Played Ambush → Plan, **Moon's Reflection**, and Coral Bulwark for a Frail-reduced 4 Block. Moon's Reflection needed no selection screen — the exhaust pile held exactly one card — and at the start of turn 4 the Kurage panel read:

> The Bake-Kurage carried these out at the start of this turn, front first:
>   - Bake-Kurage: Ambush, 12
>   - **Bake-Kurage: Shinobu — Sanctifying Ring**

**`Sanctifying Ring 3` was back on my status line — a full second activation of the deck's engine for one energy.** It did charge the Ring's own 3 HP cost again (HP arithmetic: 19 incoming − 9 Block = 10, plus 3 = the 13 I actually lost).

**Turn 4** was the Mika audition. Enemy at 39 with `Poison 17`. Mika (Cryo) into the Hydro aura triggered **Frozen** — "Its next action deals half damage; attacking it Shatters for 6 damage" — and its rider "your next Attack costs 1 less" made the follow-up Strike free: 5 + 9 + 6 Shatter = 20 for one energy total.

**Turn 5.** The enemy sat at **2/134** with `Poison 20`, intending only to Defend and Buff. One Strike+ (12) finished it.

**Fight 11 result: won on turn 5, HP 55/95, 20 HP spent** — and the great majority of the 134 was removed by Poison, not by cards.

**Reward:** `17 Gold`, card. Offer: Battle Plan (3rd) · Feint · Sango Isshin (3rd) · **Bennett — Fantastic Voyage** (cost 1, "If you are above 70% HP, gain 3 Strength. Otherwise, gain 10 Block. Exhaust").

**Took Bennett.** It is the rare card whose two branches are both worth a card slot: above 70% (which a pre-boss rest guarantees) it is 3 Strength for the whole fight, which in a five-turn boss fight with three or four attacks a turn is worth more than any single card I own; below 70% it is 10 Block, still double a Defend. A third Sango would have been 23 for 2 energy against a single boss body — 11.5 per energy, which Strike+ already beats at 12.

### The Shop (floor 11) — 500 gold, and this one had shelves

Fourteen items. The purchases, in priority order:

1. **Card Removal, 75** — spent on the **Lantern Key**. A 28-card deck with a guaranteed unplayable card in it is the single worst thing about my deck, and this undoes the whole Lantern Key event at a quarter of the 100 gold I turned down to get it.
2. **Gigantification Potion, 99** — "The next Attack you play deals triple damage." Sango's armed mode is 23 to ALL; tripled that is **69**. This is the largest single number available to me anywhere.
3. **Kujou Sara — Tengu Stormcall, 72** — "Deal 5 damage. Next turn, your Attacks deal 5 additional damage." My boss turns run three to five attacks, so this is +15 to +25 for one energy, and unlike Vanguard+ it does not exhaust.
4. **Explosive Ampoule, 52** — 10 to ALL, cheap, and I now have the slots to hold it.

**Declined, with reasons:** **Lantern, 197** ("Start each combat with an additional [Energy]") — Very Hot Cocoa already gives +4 on turn 1 and I have wasted 2–3 of it in almost every fight this act, so a fifth turn-1 energy is worth close to nothing to this deck. **Cauldron, 187** (5 random potions) — I had only three free slots, so two of the five would have been discarded, and known potions beat random ones. **Sparkling Rouge, 199** (1 Strength and 1 Dexterity at the start of turn 3) — my fights end on turn 3–5, so it pays for one or two turns. **Undertow, 50** (10 damage with any debuff up) beats a Strike by 1 but would be a 29th card.

Left **202 gold** standing for the act-3 seat.

**A display note from the removal screen:** out of combat the deck view prints **base** faces — `Strike — Deal 6 damage`, `Strike+ — Deal 9 damage` — where the same cards read 9 and 12 in every combat screen, because Strike Dummy's +3 is only applied in the fight. A player choosing what to remove is shown different numbers than the ones the card actually deals.

### Rest (floor 12)

`Rest — Heal for 30% of your Max HP (28). Raise your Max HP by 5.` versus `Smith`, at 55/95.

I took **Rest** over the Smith even though the upgrade on offer would have been Sango Isshin (cost 2 to 1, which the Whetstone had already proved is that card's upgrade). The arithmetic: two more fights at roughly 15–20 HP each would have put me into the pre-boss rest at about 20, and 20 + 30 is a much worse boss entry than 88 + 30. **HP 55/95 to 88/100 — a gain of 33 against a promised 28**, the Stone Humidifier's silent +5 current for the third time this act. Sango's quarter-of-Max went 23 to **25**.

### Fight 12 — Spiny Toad (116 HP), floor 13

The fight that taught the most about what this deck *cannot* do.

**Turn 1 (7 energy, free turn — `Empower`).** Both Sango Isshin and Sango Isshin+ were in my opening hand, and **there was no way to arm either of them.** Sango's condition is "if the Bake-Kurage carried out a Plan **this turn**", and without The Moon Overlooks the Waters a Plan written now resolves *next* turn. Cards left in hand are discarded, so holding a Sango for the armed turn is impossible. **Both copies of my best card were worth their base 8 instead of 25**, and there was nothing I could do about it.

I played them anyway (8 each), planned Kurage's Oath and Coral Bulwark, and slotted **Mika** between the two Sangos so that its Cryo would react with the Hydro aura for Frozen and its "your next Attack costs 1 less" would make Sango+ free.

**And here is the one arithmetic I could not close all act.** Predicted turn-1 damage: Sango 8 + Mika 5 + Sango+ 8 + Frozen's Shatter 6 = 27, then Oath's Plan 7 and the Casket's 2 off Coral Bulwark's planned Weak at the start of turn 2 = 36 total. The screen showed **114 → 89, exactly 25**, which decomposes cleanly and only as `Sango 8 + Sango+ 8 + Oath 7 + Casket 2`. Mika's 5 and the Shatter's 6 are both missing, and Mika was certainly played — it is in the discard count, and its cost rider did make Sango+ free. **I cannot account for 11 damage**, and no screen in the fight explains it. The nearest hypothesis I can form from the printed rules is that a Frozen reaction consumes the triggering hit's damage rather than adding to it (unlike Vaporize and Melt, which the glossary says *multiply* the hit) — but nothing says so, and the Shatter's absence does not fit that either.

**Turn 2 — Thorns, and the answer to it.** The Toad's Empower produced `Thorns 5 (buff) — When hit by an attack, deal 5 damage back`, alongside a 17-damage intent.

My deck plays three to four Attacks a turn, so Thorns was a 15–20 HP tax per turn. **The counter is that almost none of this deck's damage is an "Attack":** Plan damage is not (the act-1 Shrink test proved Plan damage ignores attack-modifying debuffs), the Tamakushi Casket's pings are a relic, and Electro-Charged Poison is neither. So I spent the whole turn writing Plans — **Ambush, Battle Plan and Slack Water all onto the Bake-Kurage** — dealt 14 damage at the start of the next turn and took **zero** Thorns damage.

**Thorns lasted exactly one turn** and was gone by turn 3, which no text said.

**Turn 3 — the deck's best round of the act.** Energy 4/3 and seven cards from Battle Plan. Sequenced for the reaction chain and for Kusarigama:

**Kujou Sara** (0) → **Strike** (9 + 4 = 13, applying Electro onto the Hydro aura → Electro-Charged → Poison, whose debuff fires the Casket for 2 and **re-applies Hydro**) → **Gorou** (Geo consuming that re-applied aura for Crystallize Block) → **Strike** (the third Attack, so **Kusarigama** fired for 6) → **Shinobu — Sanctifying Ring**.

**75 → 20: 55 damage in one round**, and every point of the incoming 12 was blocked. The only HP I lost was Shinobu's own 3.

**Turn 4.** 20 HP left, `Empower` intent, Strike+ (12) and Strike (9) finished it.

**Fight 12 result: won on turn 4, HP 78/100, 12 HP spent** — and 3 of that was Shinobu's self-cost, so 9 came from the enemy across a 116 HP fight.

**Reward:** `18 Gold`, card. Offer: Moon's Reflection (2nd) · Sea-Salt Prayer · **Cleansing Wave+** ("Gain 8 Block. **Remove one of your debuffs.** Plan: Gain 13 Block") · Fischl — Nightrider.

**Took Cleansing Wave+.** Thirteen Block from a Plan is the best Block rate in my deck by three points, and the debuff-removal clause answers the specific thing that has cost me most this act: `Frail` and `Weak` landing on *me* and cutting every Block face and attack face by a quarter. Fischl's second clause is priced in "Oz", a word no card I own and no glossary on the screen defines — the same dead-text problem the previous seat hit with `Companion`, now recurring with a new keyword.

### Fight 13 — Bowlbug (Rock) 45 + (Egg) 22 + (Silk) 43, floor 14

Three bodies, 110 HP, and the act's only forced route — one node.

**Turn 1 (7 energy).** Spent **Explosive Ampoule** here rather than saving it: three enemies is 30 damage, where against the single-body boss ahead it is 10. Then Kujou Sara — Tengu Stormcall into the Rock (5 + Electro-Charged + Casket), Strike into the Egg, and **Battle Plan, Ambush and Treatise** all written onto the Kurage. Took 16.

**A clear display defect.** On the next screen my status line read:

> `Fantastic Voyage 5 (buff) — Your Attacks deal 5 additional damage this turn.`

That is **Kujou Sara — Tengu Stormcall's** effect ("Next turn, your Attacks deal 5 additional damage"), printed under the name of **Bennett — Fantastic Voyage**, a completely different card which was at that moment still sitting unplayed in my hand. The number and the effect were right; the name on the buff was another card's.

*(The buff itself checked out arithmetically: Strike printed **10**, which is 6 base + 3 Strike Dummy + 5 Stormcall = 14, times 0.75 for the `Weak` I was carrying = 10.5 → 10.)*

**Turn 2 — the debuff-removal turn.** I was carrying `Weak 1`, so every attack face was down a quarter. Playing **Cleansing Wave+ first** removed it and lifted Strike from 10 to 14 and Thundergrust from 9 to 13 before either was played — the card paid for itself twice over in one turn. Strike killed the Rock; Thundergrust's 13 went through the Egg's 7 Block to kill it; Shinobu's Ring went down. All incoming was blocked.

**Turn 3 — Superconduct, and my own worst mistake of the act.** The Silk sat at 26 with an `Electro Aura` and a harmless Debuff intent.

I sent `play "Mika — Starfrost Swirl" on "Bowlbug (Silk)"` and the screen came back **completely unchanged** — same HP, same aura, same energy, same pile counts. I initially wrote this down as a defect, because I had seen the identical non-effect in fight 12 and had already recorded 11 unaccounted-for damage there.

It was **my error, not the game's.** Re-sending the command with output visible produced:

> `'Mika — Starfrost Swirl' does its own aiming, so it takes no `on "Bowlbug (Silk)"`. The form that resolves: play "Mika — Starfrost Swirl"`

Mika is an AoE card and takes no target. I had been batching `act` calls with their output piped to `/dev/null` inside a `for` loop, so **a refusal was completely silent to me** — the loop carried on, the card stayed in hand, and only the arithmetic of the enemy's HP said anything was wrong. **This retroactively explains the missing 11 damage in fight 12: Mika was refused there too, for the same reason, and I never saw it.** Two of my four refusals this act were invisible at the time I made them.

Played correctly, Mika is excellent and did exactly what the glossary promised: **26 → 16**, which is 5 base × 1.5 + the Casket's 2 × 1.5 = 7 + 3 = 10, because **Superconduct's 2 Vulnerable landed before Mika's own damage resolved**, and Vulnerable scales the relic ping as well as the card. `Vulnerable 2` and a fresh `Hydro Aura 2` (Casket re-application) were both on the body afterwards. Slack Water (free, from Mika's rider) and Sango+ finished it at 1.5x.

**Fight 13 result: won on turn 3, HP 61/100, 19 HP spent.**

**Reward:** `10 Gold`, `Power Potion`, card. Offer: **War Council** ("Plan: Deal 5 damage and apply 1 Weak to ALL enemies") · Salt Line · Song of Pearls+ · Gorou (2nd).

**Took War Council.** Against a single boss the Weak is worth more than Song of Pearls+'s 4 Block a turn — a 30-damage boss swing weakened is 8 HP saved, against 4 blocked — and it comes with 5 damage, a Casket ping off the Weak, and Plan-card status, so it arms Sango on the turn it resolves.

### Rest before the boss (floor 15)

`Rest` at 61/100. **61 → 96, Max 100 → 105**, a gain of 35 against a promised 30 — the Humidifier's silent +5 for the fourth time. Sango's armed mode is now **26**.

I took Rest over Smith again for the same reason as before: Max HP is this deck's damage stat as well as its life total.

### BOSS — The Insatiable (321 HP), floor 16

Entered at **98/105**, four potions held (Gigantification, Skill, Dexterity, Power), five relics' worth of openers and a 30-card deck.

Two lines defined the whole fight, and the second one is the best thing in this act:

> Intent: `Empower (Buff)` **and also** `Strategic (StatusCard) — the number on its icon is 6 — This enemy intends to give you 6 Status cards.`
> `Sandpit 4 (buff) — In 4 turns, you will be eaten and die.`

**Sandpit is a hard kill-clock, not a damage threat.** Four turns to remove 321 HP is roughly 80 a turn, which is more than I had ever produced. I played the first three turns believing I was in a race I would probably lose.

**Turn 1 (free).** Spent **Power Potion**, and it offered **The Moon Overlooks the Waters** again — the same 2-cost Power the Decimillipede elite had handed me, free to play from the potion. Took it instantly. Then **Shinobu — Sanctifying Ring**, and **Moon's Reflection** targeting it in the exhaust pile, which produced a result I still cannot fully explain: the status line read **`Sanctifying Ring 8`**, not 3 or 6. The Ring's duration stacked rather than refreshed, and the engine was then guaranteed for longer than the Sandpit would allow me to live.

**Turn 2.** The boss opened with `8x2` and `Sandpit 3`. Battle Plan onto the Kurage — with The Moon it **refunded its own energy and drew 2 immediately**, so it is a free card that thins nothing and gains two. Thundergrust (Electro-Charged), Gorou, Kirara: 40 damage, all 16 incoming blocked.

**Turn 3 — the turn that won the fight.** Boss at 259, `Vulnerable` not yet up, four energy from the queued Battle Plan, and Sango Isshin in hand.

1. **War Council → Bake-Kurage.** With The Moon this resolved *immediately*: 5 to ALL plus 1 Weak, and the Weak fired the Casket for 2 Hydro, which reacted with the standing Electro aura for Electro-Charged and then left a Hydro aura behind. **And it armed Sango on the same turn**, which without The Moon is impossible.
2. **Mika — Starfrost Swirl** (no target — the lesson from fight 13). Cryo onto that fresh Hydro aura. The glossary's boss clause fired exactly as printed: *"Bosses cannot be Frozen: Hydro plus Cryo is consumed and applies 2 Vulnerable instead."* `Vulnerable 2` landed, and 259 → **240**.
3. **Gigantification Potion**, then **Sango Isshin**, armed, at a quarter of 105 = 26.

**And here the potion did not do what it says.** "The next Attack you play deals triple damage." Sango's armed mode took the boss 240 → **201**, exactly **39 = 26 × 1.5**. The Vulnerable multiplier applied; the triple did not.

**But it was not consumed either.** The very next card, an ordinary Strike, took 201 → **155**: **46 damage**, which decomposes as 9 × 3 (Gigantification) × 1.5 (Vulnerable) = 40, plus **Kusarigama's 6** for the third Attack of the turn. So Gigantification skipped over Sango's "quarter of your Max HP to ALL" mode entirely and waited for the next ordinary attack. I got lucky — had Sango consumed the potion for no benefit, I would have lost roughly 40 damage on a turn I could not spare.

**Turn 4 — the Status cards turn out to be the answer to the clock.** The boss was at 121 with `Sandpit 2`, and one of the six Status cards it had given me was finally in hand:

> **Frantic Escape** — cost 1, status. "Get farther away. **Increase Sandpit by 1.** Increase the cost of this card by 1."

**The boss's own clog is the escape valve for its own kill-timer.** Six copies were shuffled into my deck on turn 1, each buying a turn, each costing one more energy than the last. That reframes the whole fight: The Insatiable is not a damage race, it is a question of how much of your deck's throughput you are willing to spend on the clock.

I spent one. Boss at 121 with two turns left is a coin-flip on one draw from a 36-card deck holding six statuses; the downside of losing that flip is the run, and I am the middle seat of three. So: Kujou Sara → Strike+ (24 with Vulnerable) → Tengu Stormcall → **Frantic Escape**, taking Sandpit back to 3. Damage that round plus a Poison that had compounded to **24** took the boss 121 → **49**.

**Turn 5 — the kill.** Ambush onto the Kurage (immediate 12 through The Moon, and Sango armed again), **Sango Isshin+** for 26, and Slack Water — printing **12** rather than 7, because Tengu Stormcall's +5 was live — for the last 11.

**THE INSATIABLE KILLED on round 5. HP 73/105, and my HP never once dropped below 73 in the entire fight.** The Sandpit never got below 2.

**Reward:** `100 Gold`, `Regen Potion` (claimable — Potion Belt's extra slots meant no reward was ever lost again after floor 10), boss card.

Offer: Sango Isshin (3rd) · The Clouds Like Waves Rippling · **The Moon Overlooks the Waters** · Albedo — Solar Isotoma ("At the end of your turn, if any enemy has an aura, deal 8 damage to that enemy and gain 4 Block").

**Took The Moon Overlooks the Waters**, as a permanent card this time. Albedo is the more efficient single card — with the Casket keeping an aura up almost permanently it is 8 damage and 4 Block every turn for one energy — but The Moon is the card that fixes this deck's one structural flaw. Sango Isshin's condition asks for a Plan **carried out this turn**, and without The Moon there is no way to satisfy it on the turn you actually hold Sango; fight 12 cost me both copies of my best card for exactly that reason. The Moon also doubles eight other cards in the deck and makes Battle Plan free.

**Act 2 complete. The lane stands on the act-3 map screen. Act 3's boss is named `Queen`.**

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

**1. The Lantern Key: 100 gold, or a fight for an item with no description.** The event printed `Return the Key — Gain 100 Gold` against `Keep the Key — Fight to obtain the Key`, and nothing else. I took the fight because at 81/90 HP was my most abundant resource. It cost **27 HP** against a 101-HP elite with Plating, and the Key turned out to be an **unplayable card permanently in my deck**. I then paid 75 gold at a shop to undo it. Net: −27 HP, −75 gold, and I turned down 100. It was a real choice and I got it wrong, but I could not have got it right from what the screen showed.

**2. Ranwid's trade: one known relic for two unknown ones.** Giving up Oddly Smooth Stone (`Dexterity 1`) for two random relics. It paid — Potion Belt alone retired the act-1 potion problem — but the cost was visible for the rest of the act in every Block face dropping by one, and I could not see what I was buying until the next combat screen.

**3. Rest versus Smith, three times, and I chose Rest every time.** The tempting Smith was Sango Isshin's cost cut, which the Whetstone had already shown me is that card's upgrade. Rest won each time for a reason particular to this character: **Stone Humidifier makes a rest a damage upgrade as well as a heal**, because Sango reads a quarter of Max HP. Over three rests Sango went 22 → 23 → 25 → 26 and I gained 100 HP.

**4. Frantic Escape on boss turn 4: one energy for one turn of life.** Boss at 121, Sandpit at 2, roughly 60 damage a turn available. Spending the energy meant not killing on the next turn; not spending it meant betting the run on a single draw from a deck holding six dead cards. I bought the turn and killed it with a turn to spare.

**5. Sara onto the Strike instead of onto Thundergrust** (fight 11, turn 2). Kujou Sara — Crowfeather Cover reads "Your next Attack this turn deals 4 additional damage **and applies Electro**". The obvious target is the biggest attack; the correct one is the *colourless* Strike, because Thundergrust already carries Electro. Putting Sara on Strike buys a reaction, whose Poison fires the Casket, whose Hydro re-applies the aura, so Thundergrust then reacts a **second** time. That single ordering choice was worth 24 damage and 4 extra Poison in one turn.

**6. Levelling the Decimillipede segments instead of focusing.** Strike+ into the 42 and two Strikes into the 46, so the three ended at 26/28/29 rather than 23/31/29. It was the right shape of play for the printed rule — and the printed rule turned out to be a lie (see findings).

### (b) What felt automatic, and what never seemed worth playing

**Automatic:** the free first turn. Eight of this act's nine combats opened with an intent that printed no damage number (`Empower`, `StatusCard`, `Defensive`, `Strategic`), so turn one wrote itself every time — never Block, spend the 7 energy from Very Hot Cocoa on damage and Plans. Also automatic: **Shinobu — Sanctifying Ring on sight**, and **any Battle Plan while The Moon was in play**, since it costs nothing and draws two.

**Never worth playing: Defend, still.** I played it perhaps six times all act, always as the last energy of a turn with nothing better, and after the Oddly Smooth Stone trade it printed **5**, dropping to **3** under Frail. Coral Bulwark, Read the Field, Thoma, Kirara, Cleansing Wave+ and Gorou all beat it, several of them while also dealing damage. Four Defends are a quarter of my starting deck and they contributed almost nothing across sixteen floors.

**Never worth playing: Moon's Reflection, until it suddenly was.** For most of the act it is a dead card — its exhaust pile is empty until Shinobu's Ring has been played, which is usually turn 2 or 3. I discarded it unplayed twice and fed it to Gambler's Brew once. In the two fights where it landed after the Ring it was one of the best cards in the deck.

### (c) What I could not understand, or that contradicted its own printed text

- **`Reattach 25 — If other segments are still alive, revives in 2 turns with 25 HP.`** Two Decimillipede segments died with others alive. **Neither revive ever happened**; killing the last body ended the combat outright. The buff shaped my entire plan for that fight and did nothing.
- **`Gigantification Potion — The next Attack you play deals triple damage`** did not triple Sango Isshin's armed mode (26 × 1.5 = 39 exactly), but did not spend itself on it either — it applied to the next ordinary Strike instead.
- **`Sanctifying Ring 8`.** A 3-turn buff, replayed once by Moon's Reflection, printed 8. Neither 3 nor 6.
- **`Plating 6` granted 5 Block, and `Plating 5` granted 4.** The number printed during my turn is consistently one higher than what the enemy actually gains at the end of it. I could find no reading of "reduced by 1 at the start of your turn" that matches the screen.
- **A buff printed under the wrong card's name.** Kujou Sara — Tengu Stormcall's effect appeared on my status line as `Fantastic Voyage 5 (buff) — Your Attacks deal 5 additional damage this turn`, while Bennett — Fantastic Voyage was still sitting unplayed in my hand.
- **`{Left}` unsubstituted.** `Blazing Barrier 6 (buff) — {Left} Block left.`
- **A Shop with 400 gold in hand and no shelves at all.** Observed twice.
- **`Oz`.** Fischl — Nightrider is priced in a keyword — "If Oz is out" — that no card I own and no glossary on any screen defines. This is exactly the `Companion` problem the previous seat hit in act 1, recurring with a new word.
- **Whether Red Mask's Weak ever works.** A third negative data point this act (Block 12 against a printed 15 with `Weak 1` standing; took 3).
- **The Moon Overlooks the Waters left no marker on my status line for a full turn** after being played, then appeared normally from the next round on.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted: Defend** — for the second act running, and now worse, because the relic that gave it a sixth point of Block was traded away and Frail cut it to 3. **Lantern Key** is technically worse (it cannot be played at all) but I paid to delete it; Defend I am stuck with.

**Happiest to draw: Battle Plan while The Moon Overlooks the Waters was in play.** It costs one energy, immediately refunds it, immediately draws two cards, queues itself to do the same again next turn, and satisfies Sango Isshin's condition on the spot. It is a free card that turns into three cards and arms the best card in the deck. Outside The Moon, **Sango Isshin+** — 26 to ALL for one energy.

### (e) Did the previous seat's three sharpest findings hold up

**1. "The Bake-Kurage queues multiple Plans, which nothing documents."** **Held, and extended.** I stacked two copies of the *same* card (`in this order (2): 1. Battle Plan 2. Battle Plan`) against the Mysterious Knight, and three Plans at once against the Decimillipedes (`Plan 3`), which resolved as 18 Block, +1 energy, +2 cards and a Casket kill in a single start-of-turn. Still nothing on any screen says Plans stack.

**2. "Electro-Charged is printed as `Poison`, stacks additively, and was my main damage source."** **Held, emphatically, and I can now add the reason it matters most.** Poison reached **20** on the Louse Progenitor and **24** on the boss. Against the Mysterious Knight I proved the mechanism the previous seat only suspected: **Poison ignores enemy Block.** The Knight entered its turn holding Plating Block and lost the full tick with the Block untouched and still standing on my next turn. Against the Louse's `Curl Up 14` the same thing happened — Shinobu's 5 Electro and the Casket's 2 were both eaten by the Block, and only the Poison landed (123 → 119, exactly the tick). Against every armoured enemy in this act, Poison was the only damage that could not be paid for twice.

**3. "Red Mask's Weak expires before the enemy's first attack, so half the relic does nothing."** **Held.** The Mysterious Knight showed `Weak 1` at combat start and hit for its full printed 15 into my 12 Block, so I took 3 where a working Weak would have made it 11 and I would have taken 0. That is a third independent negative case after Byrdonis and Vantom. The contrast is sharp because a Weak I apply *during* my turn visibly rewrites the printed intent — Slack Water took an Exoskeleton's `3x3` down to `2x3` on the spot, and War Council's Weak took the boss from 28 to 21.

I will add a fourth that also held: **"Attack cards hide their modified damage; Plan cards show theirs."** It held for enemy debuffs — Thundergrust never showed its Vulnerable-adjusted number — but **inverted for debuffs on me**: `Weak` and `Frail` on my own character *did* re-print every affected face (Gorou 8 → 6, Defend 5 → 3, Strike 14 → 10). So the display shows what is done *to* me and hides what I am doing *to* the enemy.

### (f) Did act 2 ask anything of the deck that act 1 did not

Yes — four things, and three of them are the same question asked differently: **"your damage is fine, now get it past this."**

- **`Hard To Kill 9`** (a 9-per-instance damage cap) inverts card value: Sango's 26 becomes 9, while a Strike at 9 is exactly efficient and the Casket's 2-damage pings are untouched. **Many small instances beat few big ones**, which is the reverse of everything act 1 rewarded.
- **`Plating`** (Block re-granted every turn) and **`Curl Up 14`** (Block on first hit) both tax raw damage and both fold instantly to Poison.
- **`Thorns 5`** taxes *Attacks specifically*, and the deck's answer is that most of its damage is not an Attack — Plan damage, relic pings and Poison all ignore Thorns. I took a whole turn writing three Plans and paid zero.
- **`Sandpit`** is new in kind: not a damage threat but a **hard turn limit**, answered by cards the boss itself puts in your deck.

Act 2 also asked a question act 1 never did about **Sango Isshin's condition**. Act 1's record treats Sango as reliably live; in act 2 I twice held Sango on a turn where no Plan had resolved and could do nothing about it, because a Plan written now lands *next* turn and cards do not survive to next turn. The card is only as good as your ability to have it in hand one turn after a Plan — which is why The Moon Overlooks the Waters is not a nice extra but the fix for a structural flaw.

### (g) Anything a screen granted or changed without saying so

- **About 40 HP appeared between the acts.** The act-1 record's last printed reading was 39/90; my first act-2 combat opened at 81/90 with Blood Vial's +2 included, so I entered at 79. No screen said anything.
- **Every rest healed 5 more than it promised** — 27 → 32, 28 → 33, 30 → 35 — because Stone Humidifier's +5 Max HP silently carries +5 current. Four occurrences now across two acts.
- **Ranwid's trade never printed what it gave.** I learned that Kusarigama and Whetstone were mine from the next combat's relic list, and Whetstone's "Upgrade 2 random Attacks" had already resolved — I discovered which two by drawing them, one at a time, several fights apart.
- **The Bake-Kurage logs a Plan written mid-turn as "carried out at the start of this turn"**, which is the exact phrase Sango's condition tests. Nothing on The Moon Overlooks the Waters' one line of text says it arms Sango.
- **The deck view prints different numbers than combat.** At the shop's removal screen, Strike reads "Deal 6 damage" and Strike+ "Deal 9"; in every fight they are 9 and 12, because Strike Dummy's +3 only exists inside a combat.
- **Curl Up triggers after the whole card resolves.** Slack Water's 7 *and* the Casket's 2 both landed before the 14 Block appeared.
- **Enemy Block expires; it does not accumulate forever.** Curl Up's 14 survived my end-of-turn triggers and the enemy's own turn, then was gone by my next turn.
- **Superconduct's 2 Vulnerable applies before the triggering card's own damage** — Mika's 5 landed as 7, and the Casket's 2 as 3.
- **Enemy list indices renumber the instant a body dies**, mid-turn, so a multi-card plan written against the pre-turn numbering breaks the moment its first card works.
- **`Wound` status cards do not persist between combats** — act 1 ended uncertain whether the deck was 22 or 24; the first act-2 combat printed 20 draw + 5 hand = 25, which is 22 plus my three act-2 additions exactly.

---

## Findings, ranked by sharpness

**1. `Reattach` is an empty threat, and it is the buff that most changes how you play.** All three Decimillipede segments printed `Reattach 25 — If other segments are still alive, revives in 2 turns with 25 HP`. I spent the fight levelling damage across the three bodies specifically so one AoE could wipe them together, because piecemeal killing looked like a treadmill. In the event **two segments died with others alive and neither revive ever arrived** — the combat ended the instant the board emptied. The correct play against this elite is to ignore the buff entirely and focus-fire, which is the opposite of what its text tells you to do.

**2. `Sandpit` is answered by the boss's own Status cards, and nothing connects the two.** The Insatiable opens by giving you 6 Status cards and by printing `Sandpit 4 — In 4 turns, you will be eaten and die`. The Status card is `Frantic Escape — Get farther away. Increase Sandpit by 1. Increase the cost of this card by 1.` This is a genuinely good boss: the clog *is* the clock's antidote, and the fight becomes "how much throughput will you spend staying alive". But the Sandpit line says nothing about escaping, and I did not see a Frantic Escape until turn 4 of 4 — I spent three turns playing a race I believed I was losing, on a plan I would not have chosen had the connection been visible.

**3. Poison ignores enemy Block, and that is what makes this deck work.** Two clean cases. Against the Mysterious Knight's `Plating`, the boss entered its turn holding Block and lost the full Poison tick with the Block untouched and still standing on my next turn (72 → 66, exactly 6). Against the Louse Progenitor's `Curl Up 14`, Shinobu's 5 Electro and the Casket's 2 were both absorbed and **only** the Poison landed (123 → 119, exactly the tick of 4). Poison reached **20** on the Louse and **24** on the boss. Against every armoured enemy in the act, this was the only damage that did not have to be paid for twice — and no screen anywhere says Poison bypasses Block.

**4. `The Moon Overlooks the Waters` silently fixes Sango Isshin, and the connection is invisible.** Its whole text is "Plans also happen when played." What that actually does: the Bake-Kurage logs the immediate half as **"carried out at the start of this turn"**, which is the exact phrase `Sango Isshin`'s condition tests — so writing any Plan arms Sango *on the same turn*. Without it, Sango's armed mode is unreachable on the turn you hold the card, because Plans land next turn and hands do not survive. Fight 12 cost me **both** copies of Sango at their base 8 instead of 25 for precisely this reason, with no play available to avoid it. Two cards, no shared keyword, no hint on either.

**5. `Gigantification Potion` skips Sango's armed mode entirely.** "The next Attack you play deals triple damage" produced 240 → 201, exactly `26 × 1.5` — the Vulnerable multiplier but no triple. It then applied to the following ordinary Strike (201 → 155 = `9 × 3 × 1.5` + Kusarigama's 6). Buying that potion specifically to triple Sango was my plan for the whole boss fight; it silently did something else, and only the fact that it was not consumed saved the turn.

**6. `Hard To Kill 9` inverts the deck, and it is the most interesting board in the act.** A flat 9-damage cap per instance: Explosive Ampoule's 10 landed as exactly 9 on each of three bodies, while the Casket's 2-damage pings passed untouched. Sango's 26-to-ALL is worth 9 to each; a plain Strike at 9 is perfectly efficient. **Many small instances beat few big ones**, which reverses every lesson the deck teaches elsewhere, and it does it with one clearly-worded line.

**7. Element ordering is the deepest decision this deck has, and it is entirely undocumented.** Three distinct orderings mattered this act: Gorou (Geo) must come *after* the Electro hit or its Crystallize eats the aura the reaction needs; Kujou Sara's "applies Electro" belongs on the *colourless* Strike, not on Thundergrust, because that buys a second reaction after the Casket re-applies Hydro; and Mika's Cryo must land on a Hydro aura for the boss-Vulnerable clause. The reaction previews on individual cards are good, but nothing ever explains that **the Tamakushi Casket re-applies Hydro on every debuff**, which is the fact that makes chained reactions possible at all.

**8. Enemy indices renumber mid-turn, which breaks any multi-card plan the moment its first card works.** I sent `Strike on Exoskeleton (1)`, `Slack Water on Exoskeleton (3)`, `Coral Bulwark` as one chain. The Strike killed (1), the survivors renumbered, `Exoskeleton (3)` ceased to exist, and the rest of the turn was refused. The screen's own note says the numbering "is re-counted on every screen" for *cards in hand*; the same is true of enemies and is not stated.

**9. `Plating` prints one more than it grants.** `Plating 6` during my turn granted 5 Block at the end of it; `Plating 5` granted 4. Confirmed twice by closing the damage arithmetic of the following turn. There is no reading of "reduced by 1 at the start of your turn" under which the number shown during the turn is the number that is used.

**10. Two display defects and an empty shop.** `Blazing Barrier 6 (buff) — {Left} Block left.` never substitutes its placeholder. **Kujou Sara — Tengu Stormcall's buff is printed under Bennett — Fantastic Voyage's name** while Bennett sits unplayed in hand. And an `Unknown` node resolved into a **Shop with 400 gold in hand and zero items on the shelves**, confirmed by two observes.

**11. The Lantern Key event cannot be priced from what it prints.** `Return the Key — Gain 100 Gold` versus `Keep the Key — Fight to obtain the Key`. The fight is a **101 HP elite** with `Plating` and `Strength 6` that cost me 27 HP; the Key is an **unplayable card permanently added to the deck**, whose text ("Unlocks a special event in the next Act") appears for the first time when you draw it in the next combat. Nothing on the event, and nothing on the reward line that says only "Add Lantern Key to your deck.", tells you either fact. I paid 75 gold at a shop to undo a choice I had spent 27 HP to make.

**12. The Whetstone problem: a relic whose effect is already over before you can read it.** "Upon pickup, Upgrade 2 random Attacks." Ranwid's event never printed which relics it gave, so I first read Whetstone's text on the next combat screen, by which time the upgrades had resolved. I discovered the two cards it had chosen (a Strike and a Sango Isshin) by drawing them, several fights apart. Sango+'s upgrade is a cost cut from 2 to 1, which is the single largest change to my deck this act and which I learned about by accident.

**Where I could not tell:** why `Sanctifying Ring` printed **8** after one replay of a 3-turn buff; whether the Sandpit counter ticks on my turn or the enemy's; whether the Casket fires once per enemy or once per application (three Exoskeletons each took the full 2 here, where act 1 saw three Inklets each take 1, so board size is not the variable and I still cannot name what is); and whether Gigantification would have been consumed by Sango's *unarmed* 8.

**My own error, recorded because it distorted two fights.** `Mika — Starfrost Swirl` takes no target, and I sent it with `on "<enemy>"` four times. I was batching `act` calls with output piped to `/dev/null`, so **the refusals were completely silent** — the loop continued, the card stayed in hand, and only the enemy's HP arithmetic showed anything was wrong. I initially wrote up 11 unaccounted-for damage in fight 12 as a possible engine defect; it was my refused command. The tool behaved correctly and its refusal text named the working form precisely; the failure was mine, and it is worth recording that a seat batching commands can lose a card a turn without noticing.

---

## Identity (completed)

- **Model / seat:** Claude Opus, blind TESTER seat, round 5, run 3, **second of three chained seats**.
- **Lane:** 1. **Character:** KLEEMOD-KOKOMI.
- **Picked up:** the act-2 map screen, act 1 cleared by the first seat, its last printed HP reading 39/90. (I actually entered act 2 at **79/90** — see the unannounced ~40 HP in the findings.)
- **Act played:** 2. Boss as named by the map: **The Insatiable** (321 HP, defeated). Act 3's boss is named **Queen**.
- **Actions accepted: 222. Refused: 5.** One was a stale enemy index after a mid-turn renumber; the other four were all `Mika — Starfrost Swirl` sent with a target it does not take, and four of the five were **silent to me at the time** because I was batching `act` calls with output suppressed.
- **Termination reason:** **stop condition (1)** — the act-2 boss was resolved and its reward screen handled; the lane stands on the act-3 map screen. Budget was not exhausted (222 of 250).
- **Where the run stands:** act-3 map screen, one node offered (`Ancient (path 1)`), 15 floors to `Queen`. Nothing is mid-screen; no reward, choice or prompt is pending.

**HP trajectory — every reading the screens printed this act, in order:**

81/90 (fight 8 open) → 81 → 81 → **81/90** (fight 8 won) → 83/90 (Knight open) → 80 → 59 → 56 → 56 → **56/90** (Knight won) → 58/90 (fight 10 open) → 58 → 58 → **58/90** (fight 10 won) → **58/90 at the rest site → 90/95** → 92/95 (elite open) → 81 → 73 → **73/95** (elite cleared) → 75/95 (Louse open) → 72 → 72 → 59 → 55 → **55/95** (Louse won) → **55/95 at the rest site → 88/100** → 90/100 (Toad open) → 81 → 78 → **78/100** (Toad won) → 80/100 (fight 13 open) → 64 → 61 → **61/100** (fight 13 won) → **61/100 at the rest site → 96/105** → 98/105 (boss open) → 89 → 89 → 73 → 73 → **73/105** (The Insatiable killed).

Max HP rose **90 → 95 → 100 → 105** across three rests (Stone Humidifier). The lowest point of the act was **55/90**, after the Mysterious Knight. **I was never in danger of dying at any point in act 2**, and the boss never took me below 73.

**Gold:** the only totals any screen printed were **400** at the empty shop (floor 6) and **500** at the stocked shop (floor 11). I spent 298 there (Card Removal 75, Gigantification Potion 99, Kujou Sara — Tengu Stormcall 72, Explosive Ampoule 52) leaving a printed **202**, and have claimed 18 + 10 + 100 since. **My count is 330**, unconfirmed by any screen.

**Potions (3 of 5 slots — Potion Belt added two):**
`Skill Potion — Choose 1 of 3 random Skill cards to add into your Hand. It's free to play this turn.` · `Dexterity Potion — Gain 2 Dexterity.` · `Regen Potion`
Spent during the act: Explosive Ampoule ×2 (fight 8, fight 13), Gambler's Brew (fight 10), Power Potion ×2 (Decimillipede elite, boss), Gigantification Potion (boss). **Nothing was lost to full slots this act** — the act-1 lesson (spend one mid-fight) worked at floors 2 and 10, and Potion Belt retired the problem entirely from floor 10 on.

**Relics, exactly as printed (10):**

- **Tamakushi Casket** — Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that enemy.
- **Stone Humidifier** — Whenever you Rest at a Rest Site, raise your Max HP by 5.
- **Red Mask** — At the start of each combat, apply 1 Weak to ALL enemies.
- **Blood Vial** — At the start of each combat, heal 2 HP.
- **Strike Dummy** — Cards containing "Strike" deal 3 additional damage.
- **Very Hot Cocoa** — Start each combat with an additional 4 Energy. *(one-time, on turn 1)*
- **Kusarigama** — Every time you play 3 Attacks in a single turn, deal 6 damage to a random enemy.
- **Whetstone** — Upon pickup, Upgrade 2 random Attacks. *(already spent: one Strike and one Sango Isshin)*
- **Potion Belt** — Upon pickup, gain 2 potion slots.
- **Pen Nib** — Every 10th Attack you play deals double damage. *(prints a live counter, e.g. `Pen Nib (4)`)*

**Traded away at Ranwid the Elder:** Oddly Smooth Stone (Start each combat with 1 Dexterity).

**Deck as reconstructed — 31 cards.** (Verified against the boss screen: 0 draw + 29 discard + 2 exhaust + hand = 36, of which 6 were the boss's Status cards, so 30 before the boss reward.)

| # | Card | Note |
|---|---|---|
| 3 | Strike | cost 1, attack — 9 in combat (6 + Strike Dummy), 6 in the deck view |
| 1 | **Strike+** | cost 1, attack — 12 in combat (Whetstone upgrade) |
| 4 | Defend | cost 1, skill — Gain 5 Block *(was 6 before the Dexterity relic was traded)* |
| 1 | Sango Isshin | cost 2, attack — 8, or a quarter of Max HP (**26**) to ALL if a Plan was carried out this turn |
| 1 | **Sango Isshin+** | as above at **cost 1** (Whetstone upgrade) |
| 1 | Slack Water [Hydro] | cost 1 — Deal 7. Apply 1 Weak. Plan: Apply 1 Weak to ALL |
| 1 | Kurage's Oath | cost 1 — Plan: Deal 7 to ALL |
| 1 | Ambush | cost 1 — Plan: Deal 12 |
| 2 | Battle Plan | cost 1 — Plan: Gain 1 Energy and draw 2 |
| 1 | Read the Field | cost 1 — Gain 5 Block. Plan: Gain 10 Block |
| 1 | Coral Bulwark | cost 1 — Gain 6 Block. Plan: Gain 8 Block and apply 1 Weak |
| 1 | **Cleansing Wave+** | cost 1 — Gain 8 Block. **Remove one of your debuffs.** Plan: Gain 13 Block |
| 1 | War Council | cost 1 — Plan: Deal 5 damage and apply 1 Weak to ALL |
| 1 | Moon's Reflection | cost 1 — replay a card from the Exhaust Pile via the Kurage. Exhaust |
| 1 | Treatise | cost 1, power — draw 1 when the Kurage carries out a Plan |
| 1 | **The Moon Overlooks the Waters** | cost 2, power — **Plans also happen when played** *(boss reward)* |
| 1 | Gorou — Inuzaka All-Round Defense | cost 1 — Deal 8, Block half the damage **dealt** *(Geo: Crystallize)* |
| 1 | Shinobu — Sanctifying Ring | cost 1 — Lose 3 HP. 3 turns of 5 Electro to ALL and 5 Block. Exhaust |
| 1 | Shinobu — Thundergrust [Electro] | cost 1 — Deal 8, +5 below half HP |
| 1 | Thoma — Blazing Barrier | cost 1 — Gain 6 Block, +3 whenever it absorbs |
| 1 | Kirara — Surprise Dispatch | cost 1 — Gain 8 Block. Next turn, 10 damage to a random enemy |
| 1 | Kujou Sara — Crowfeather Cover | **cost 0** — next Attack +4 damage and applies Electro |
| 1 | Kujou Sara — Tengu Stormcall [Electro] | cost 1 — Deal 5. Next turn your Attacks deal +5 |
| 1 | Mika — Starfrost Swirl [Cryo] | cost 1 — 5 to ALL, next Attack costs 1 less. **Takes no target** |
| 1 | Bennett — Fantastic Voyage | cost 1 — 3 Strength above 70% HP, else 10 Block. Exhaust. **Never drawn in a fight where I could use it** |

Removed at the shop: **Lantern Key** (unplayable quest card).

**Record of combats this act: 6 fought, 6 won** — 4 monster rooms, 1 elite (Decimillipede), 1 event-fight elite (Mysterious Knight), 1 boss. Plus the act-1 total, the run stands at 17 combats and no deaths. The most expensive fight of the act was the **optional** Mysterious Knight at 27 HP; the cheapest were fights 8 and 10 at **zero**.

---

## Non-blindness declaration

- **Commands run:** only the two permitted forms, `GITS_LANE=1 python -m understudy.blindplay observe` and `GITS_LANE=1 python -m understudy.blindplay act "<command>"`, from the repo root `C:\Users\Monty\Documents\GitHub\GItS`. **No other `understudy` subcommand was invoked** — no `harness`, `session`, `audit`, `notes`, `scenario`, `staged_turn`, `soak`, `embark`. **No `git`.** The lane was never launched, closed, restarted or torn down, and **lane 2 was never touched**.
- **Shell usage beyond those two commands:** one `mkdir -p` for the record's directory; `cat >>` and `cat <file> >>` to append to the record; `wc -l`, `tail` and `head` on my own record file to check an append had landed; and `sed`/`grep`/`head` filters applied to `observe` output to trim it. Nothing else.
- **Tools used:** **Bash** (the two commands above plus the record appends and filters) and **Write** (to create this record, and eight scratch fragments of this record's own prose under the session scratchpad at `C:\Users\Monty\AppData\Local\Temp\claude\...\scratchpad\`, used only because a heredoc append failed on shell quoting). **Read** was used exactly once, on the one file the brief permits.
- **Repo files read: exactly one** — `C:\Users\Monty\Documents\GitHub\GItS\review\qa\kokomi-round-5-2026-09-03\opus-run3-act1.md`, the previous seat's record, read in two pages because it exceeds the single-read cap. **No source, YAML, docs, rulings, backlog, register or other record was opened at any point.** Everything else in this document comes from what the two permitted commands printed.
- **Files edited: one** — this record, at `C:\Users\Monty\Documents\GitHub\GItS\review\qa\kokomi-round-5-2026-09-03\opus-run3-act2.md`.
- **Identifiers minted: none.**
- **Refusals: 5**, all quoted or described in the log and itemised in the Identity block.
- **The lane is left standing** exactly where play stopped: lane 1, **act-3 map screen**, one node available (`Ancient (path 1)`), 15 floors to the boss `Queen`, HP 73/105, no pending reward, choice or prompt.

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
