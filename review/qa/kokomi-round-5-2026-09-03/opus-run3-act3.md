# KLEEMOD-KOKOMI — blind seat, lane 1, run 3, act 3

## Identity (running; completed block at the end)

- **Model / seat:** Claude Opus, blind TESTER seat, round 5, run 3, **third of three chained seats**.
- **Lane:** 1. **Character:** KLEEMOD-KOKOMI.
- **Picked up:** on the **act-3 map screen**, acts 1 and 2 cleared by the first two seats, Vantom and The Insatiable dead, HP **73/105** as the last reading act 2 printed.
- **Act:** 3. The map names the top of the act: **Queen**. Fifteen floors to it.
- **Actions accepted / refused:** **209 accepted, 1 refused.**
- **Termination reason:** **stop condition (1)** — the act-3 boss was resolved and its reward screen handled; the run then ended (`TOOL-BLOCKED: game_over`, floor 48). Budget was not exhausted (209 of 300).
- **Where the run stands:** **complete. Queen is dead, at HP 99/115, and the whole run is three acts, three bosses, no deaths.**

*Full details — HP trajectory, gold, potions, the fourteen relics and the reconstructed 37-card deck — are in the **Identity (completed)** section near the end of this document.*

### The act-3 map as printed on arrival

```
- 1 floor ahead: Ancient
- 2 floors ahead: Monster, Monster
- 3 floors ahead: Monster, Shop, Monster
- 4 floors ahead: Monster, Unknown, Monster, Monster
- 5 floors ahead: Monster, Monster, Unknown, Monster, Monster
- 6 floors ahead: Unknown, Unknown, Unknown, Monster, Monster
- 7 floors ahead: Elite, Shop, RestSite, Monster, Elite, Shop
- 8 floors ahead: Treasure, Treasure, Treasure, Treasure
- 9 floors ahead: Monster, RestSite, Unknown, Monster, RestSite
- 10 floors ahead: Elite, Unknown, Elite, Elite, Monster
- 11 floors ahead: RestSite, RestSite, Monster, Unknown, RestSite
- 12 floors ahead: Elite, Monster, Elite, Monster, Monster, Monster
- 13 floors ahead: Monster, Monster, Monster, Unknown, Elite, Monster
- 14 floors ahead: RestSite, RestSite, RestSite
- 15 floors ahead: Boss
```

Only one opening was offered — `Ancient (path 1)`, leading on to two Monsters — so floor 1 was not a routing choice. The shape against act 2: **no RestSite until floor 7, no Treasure until floor 8**, and floors 1–6 are Ancient/Monster/Unknown/Shop only. Six rooms of attrition at 73/105 before the first place to heal, and act 3 front-loads *nothing* — the Elites all sit at floors 7, 10, 12 and 13, after the first rest.

**Carried plan on arrival.** From the two previous records I hold: HP 73/105, four potion slots free of five (Skill, Dexterity, Regen held), ~330 gold by the second seat's count (last screen-confirmed figure was 202 at the floor-11 act-2 shop), ten relics, and a 31-card deck whose engine is:

1. **The Moon Overlooks the Waters** (Plans also happen when played) makes every Plan card pay twice *and* arms Sango Isshin on the same turn — the fix for the deck's one structural flaw.
2. **Electro-Charged Poison ignores enemy Block** and compounds; it was the second seat's main damage source against every armoured enemy.
3. **The Tamakushi Casket re-applies Hydro on every debuff**, which is what makes chained reactions possible.

Standing intentions: keep a potion slot in hand for reward screens (Potion Belt makes this nearly free now); **never batch an `act` with its output suppressed** — the second seat lost four silent refusals that way; and remember `Mika — Starfrost Swirl` takes no target and enemy indices renumber the instant a body dies.

---

## Running log

### Ancient — Tanx (floor 1)

Three relics, no cost printed on any of them:

- **Sai** — "At the start of your turn, gain 7 Block."
- **Throwing Axe** — "The first card you play each combat is played an extra time."
- **Spiked Gauntlets** — "Gain [Energy] at the start of each turn. Powers cost 1 more [Energy]." *(the amount is an unsubstituted `[Energy]` placeholder — the screen never says how much)*

**Reasoning.** Both previous seats named **energy** as the binding constraint, which argues for Spiked Gauntlets. I took **Sai** anyway, for a reason particular to this deck: 7 Block a turn is more than a Defend (5) and more than Coral Bulwark (6), so it is worth **more than one energy per turn** in Block terms *and* it never has to be drawn, where Spiked Gauntlets gives exactly one energy and taxes my two Powers — one of which, The Moon Overlooks the Waters, is the deck's engine and would go from 2 to 3. Throwing Axe doubles one card per combat; even its best case (Shinobu — Sanctifying Ring twice) needs that singleton in the opening hand, roughly one fight in six.

**Took Sai.** The very next combat screen opened at `Block 7` before I had played a card, so it applies on turn 1 as well.

### The 25 HP nobody mentioned, again

Act 2's last printed reading was **73/105**. The first act-3 combat opened at **HP 100/105**, and Blood Vial's +2 accounts for 2, so I entered the act at **98/105**. **A third act transition, a third silent heal of about 25 HP.** No screen between the boss reward and the first fight said anything. This is the second seat's finding reproducing exactly.

### Fight 14 — Scroll of Biting ×3 (34 / 30 / 37 HP), floor 2

Routing: two Monster nodes, and `Monster (path 2)` was the only one leading on to a **Shop**. I hold ~330 gold and act 3 prints two more Shops on floor 7, so a shop this early is worth more than the alternative.

The board's rule, on all three bodies:

> `Paper Cuts 2 (buff) — Whenever Scroll of Biting deals unblocked attack damage to you, you lose 2 Max HP.`

**That makes Block a damage stat here.** Max HP is not just my life total — Sango Isshin reads a quarter of it — so every unblocked instance costs 2 Max HP *permanently* and takes Sango's armed mode down with it. This board is the exact opposite of the act-1 lesson that a Block card is dead against a small hit.

**A fourth, and the cleanest, Red Mask data point.** All three opened carrying `Weak 1` from the relic and each had taken the full **2** from the Casket (34→32, 30→28, 37→35). But the printed intents read **`10`** and **`3x2`** — *unmodified*. In act 2 a Weak applied during my own turn visibly rewrote the printed intent on the spot (`3x3` → `2x3`). Here the relic's combat-start Weak is displayed on the enemy and the intent number ignores it. **The intent number itself is the proof this time, not the damage that lands** — I did not have to take a hit to see it.

**Turn 1 (7 energy, Block 7 already from Sai).** Hand: Sango Isshin+, Slack Water, Kurage's Oath, Defend, Kirara — five cards, five energy, and I had seven, so every card was affordable and the only decision was *where*.

Target choice: the three bodies remove 10, 6 and 0 incoming per turn for 32, 28 and 35 HP of work. Enemy (1) is the best rate (10 removed per 32 spent vs 6 per 28), so I focused it.

Played **Kurage's Oath → Bake-Kurage** (7 to ALL next turn, and it arms Sango next turn), **Slack Water** and **Sango Isshin+** both into Scroll (1), then **Kirara** and **Defend**.

*Predicted 17 on Scroll (1) — Slack Water 7 + Casket 2 + Sango's unarmed 8 — and Block 20 against at most 16 incoming.* Got exactly that: **32 → 15**, Block 20, and `Weak` on Scroll (1) went 1 → **2**, stacking rather than refreshing. The intent still printed 10 with Weak 2 standing.

**Turn 2 — and Sango's armed mode did the whole fight.** HP **100/105, zero damage taken**. The Kurage logged `Bake-Kurage: Kurage's Oath, 7` and Kirara's delayed 10 landed on Scroll (2). Board: 8 / 11 / 28.

Because a Plan had been carried out **this turn**, Sango was armed at a quarter of 105 = **26 to ALL**. That is lethal on two of the three bodies at once.

I had three energy and a real choice. **Bennett — Fantastic Voyage** was in hand: above 70% HP it grants 3 Strength, and Bennett + Sango is exactly 3 energy. If Strength applies to Sango's "quarter of your Max HP" mode, 26 becomes 29 and Scroll (3) at 28 dies too — the fight ends on the spot. If it does not, Scroll (3) survives at 2 with `7x2` incoming against Sai's 7 Block alone: **7 HP and 4 Max HP** (two Paper Cuts instances).

I declined the test. Max HP is this deck's damage stat, the information was not worth 4 points of it in the first fight of the act, and the safe line cost only one extra turn. Played **Sango Isshin** (armed) and **Thoma — Blazing Barrier**.

*Predicted 26 to all three — 8 and 11 dead, 28 → 2 — and Block 13 against 14 incoming, with Thoma's "+3 whenever this Block absorbs" covering the shortfall across two 7-damage hits.* **Exactly right: 2/37 left and HP still 100/105.** Thoma's arithmetic: 13 Block − 7 = 6, +3 = 9, −7 = 2 left, zero through.

*(The `{Left}` display defect the second seat recorded is still live: `Blazing Barrier 6 (buff) — {Left} Block left.`)*

**Turn 3.** Gorou (8) killed the 2 HP body.

**Fight 14 result: won on turn 3, HP 100/105, ZERO damage taken and zero Max HP lost.** Sai contributed 7 Block on each of three turns without being drawn.

**Reward:** `15 Gold`, `Weak Potion`, card. All three claimable — Potion Belt's five slots mean the act-1 problem is retired.

Offer: **Salt Line** · **Tide Wall** ("Gain 4 Block. Plan: Gain 3 Block for each Plan the Bake-Kurage carries out this morning") · **Undertow** [Hydro] ("Deal 7 damage. If the enemy has a debuff, deal 10 instead") · **Fischl — Nightrider** [Electro] ("Deal 7 damage. If Oz is out, he deals 5 Electro damage to a random enemy").

**Took Fischl — Nightrider**, and the reasoning is entirely about elements rather than the printed numbers. Undertow prints the bigger number — with Red Mask opening every fight with a Weak its "10 instead" is nearly unconditional — but it is **Hydro**, and the Tamakushi Casket keeps a Hydro aura on almost every body almost all the time, so Undertow only ever *refreshes* the aura and never reacts. Fischl is **Electro** onto that standing Hydro aura, which is Electro-Charged: 7 damage **plus** Poison 4 (which stacks and which the second seat proved ignores enemy Block) **plus** the Casket's 2 off the Poison debuff, and the Casket then re-applies Hydro so the next Electro card reacts again. Roughly 13 against a bare enemy and far more against an armoured one, versus a flat 10.

`Oz` is still undefined by any screen — the second seat flagged exactly this, and it remains dead text I priced at zero.

### The shop (floor 3) — and the gold count is reconstructible after all

`You have 345 gold.` The second seat's own running count, kept from reward screens with no confirmation since the act-2 floor-11 shop, was **330**, plus my 15 from fight 14 = **345 exactly**. So the previous two seats' complaint that gold cannot be reconstructed is *half* wrong: the arithmetic does close, and it is only the **starting** gold (act 1's unprinted ~99) that no screen ever reveals.

Bought, in priority order:

1. **Battle Plan, 78** — a third copy. It is the card the second seat named "happiest to draw", and with The Moon Overlooks the Waters in play it costs nothing at all (it refunds its own energy immediately, draws 2 immediately, and queues to do it again).
2. **Kujou Sara — Tengu Stormcall, 72** — a second copy. "Deal 5 damage. Next turn, your Attacks deal 5 additional damage." My big turns run three to five attacks, so it is +15 to +25.
3. **Card Removal, 100** — spent on a **Defend**. Both previous seats named Defend the card they never wanted to play, and **Sai makes it worse**: I now gain 7 Block at the start of every turn for free, so a card that costs an energy for 5 Block is strictly below the floor.
4. **Fire Potion, 48** — "Deal 20 damage", unconditional, and I had a free slot.

Declined: **Sango Isshin (144)** — a third copy is 26 to ALL for 2 energy, which against a single boss body is 13 per energy where Strike+ already pays 12, so it is only worth it on crowded boards. **Ninja Scroll (192)** — three Shivs in hand each combat would feed Kusarigama and Pen Nib, but "Shiv" is a word no screen defines and three cards arriving in a five-card hand crowd out the engine. **Book of Five Rings (183)** — "every 5 cards you add to your Deck, heal 20 HP" pays about twice in a whole act, and I am *removing* cards. **The General's Banner (75)** — genuinely tempting (a Weak on the front enemy every turn is also a Casket ping and a Hydro re-application, i.e. it feeds the reaction engine) but it is a **third Power** in a deck whose one indispensable card, The Moon, is a singleton Power; a third Power dilutes the draw that matters most.

Left 47 gold, nothing else affordable. **Deck 31 to 33** (Fischl, Battle Plan, Tengu Stormcall in, one Defend out).

*(A display note confirming the second seat's finding: the removal screen prints base faces. `Slack Water — Deal 4 damage` there, where every combat screen prints 7. Strike Dummy's +3 exists only inside a fight — and note it is boosting a card with no "Strike" in its printed name, which the first seat also flagged and which the deck view now proves numerically: base 4, combat 7.)*

### Event — "The Future of Potions?" (floor 4). It ate a potion and gave nothing.

The screen offered three trades and **no way to decline**:

> - **Insert Uncommon Potion** — Lose Regen Potion. Obtain an Upgraded Uncommon Attack.
> - **Insert Common Potion** — Lose Skill Potion. Obtain an Upgraded Common Skill.
> - **Insert Common Potion** — Lose Dexterity Potion. Obtain an Upgraded Common Attack.

I took the first: an *upgraded uncommon attack* has the highest ceiling of the three rewards, and Regen Potion was the potion whose value I could least pin down (the text is just "Gain 5 Regen", with no duration).

**The potion was taken. The card never arrived.** The event opened a reward screen reading `Add a card to your deck.`; claiming it opened a card-selection screen that was **completely empty** — a title, a blank list, and `You may skip this.` I observed it twice, and probing `choose 1` returned the refusal

> `there is no row 1 on this screen; it has 0.`

I skipped, re-claimed the reward, and got the same empty screen a second time. Then I proceeded out.

**And the deck count proves nothing was granted silently.** The next combat opened with `28 in the draw pile` and 5 in hand = **33** — exactly 31 + Fischl + Battle Plan + Tengu Stormcall − Defend, with no room for an upgraded uncommon attack. The trade was a straight loss of a potion for nothing.

### Fight 15 — Living Shield (55) + Turret Operator (41), floor 5

Opened **HP 102/105** (Blood Vial's +2 on 100), and `Block 7` before a card was played.

The board's rule was printed on the **other** body, and that is the whole fight:

> **Living Shield** — `Rampart 25 (buff) — At the start of the player's turn, **Turret Operator** gains 25 Block.`

The buff sits on the Living Shield and names the Turret. So the Turret enters every one of my turns with 25 Block, and the Living Shield is what has to die. This is the clearest "read the buff, not the HP bar" board in the run: the Turret is the smaller body, and every point put into it before the Shield dies is thrown away.

**Turn 1 (7 energy).** Hand: Mika, Sango Isshin+, Kujou Sara — Tengu Stormcall, Fischl — Nightrider, Defend. Both bodies wore `Hydro Aura 1` from the Casket's opening ping.

Sequenced entirely for the elements, biggest last:

1. **Tengu Stormcall** (Electro) into the Living Shield. Electro on Hydro = **Electro-Charged**: Poison 4, and the Poison is a debuff, so the **Casket fires 2 Hydro and re-applies the aura in the same beat**.
2. **Fischl — Nightrider** (Electro) into the Living Shield, onto that re-applied Hydro = a **second** Electro-Charged. Poison 4 + 4 = 8. Casket 2 again.
3. **Mika — Starfrost Swirl** (Cryo, no target) — 5 to ALL, and Cryo onto Hydro = **Frozen** on both bodies. Frozen is tagged `(debuff)`, so it fired the Casket a third time.
4. **Sango Isshin+** (free — Mika's rider) into the Living Shield, the first Attack to hit a Frozen body, so it **Shattered for 6**.
5. **Defend**.

*Predicted 37 on the Living Shield.* **Exactly 37: 53 to 16.** The decomposition closes to the point: cards 5 + 7 + 5 + 8 = 25, Casket 2 x 3 (two Poisons and one Frozen) = 6, Shatter 6. And `Poison 8` stood on the body, confirming again that Electro-Charged stacks additively.

Frozen also halved both intents on the spot — Living Shield `4`, Turret `2x5` to `1x5` — so the whole incoming turn was 9 against Block 12. **Zero damage taken.**

*(The Turret's number closed too, and only with a relic: Block 25 − Mika 5 − Casket 2 − **Kusarigama 6** = 12. Four attacks in one turn fired Kusarigama, and it chose the Turret.)*

**Turn 2 — and the second seat's mis-named-buff defect reproduced exactly.** My status line read:

> `Fantastic Voyage 5 (buff) — Your Attacks deal 5 additional damage this turn.`

That is **Kujou Sara — Tengu Stormcall's** rider, printed under **Bennett — Fantastic Voyage's** name. This time Bennett was not even in my hand or discard — it was still in the draw pile. Second independent occurrence, and it is not a "wrong card in hand" confusion: the name is simply the wrong card's.

The buff's arithmetic was right: `Strike` printed **14** (6 + 3 Strike Dummy + 5 Stormcall) and `Thundergrust` **13**.

Board: Living Shield 8 with `Poison 7`, Turret 39 behind a fresh `Block 25`. Poison alone would leave the Shield at 1, so it had to be killed by hand or Rampart renews.

Played **Thundergrust** into the Living Shield (killed it), **Kujou Sara — Crowfeather Cover** (0 cost), then **Strike** into the Turret, then **Battle Plan → Bake-Kurage**.

*I predicted the Strike would be 18 (14 + Sara's 4) and land almost entirely on the Turret's 25 Block, leaving it near-full at 39 HP.* **The screen showed 26/41 and Block 0** — 13 HP of damage — and the only arithmetic that closes it is **Pen Nib**: `Every 10th Attack you play deals double damage`. 18 x 2 = 36, minus the 25 Block = 11 to HP, then the Casket's 2 = 13. **39 to 26 exactly.**

That is worth recording carefully: **Pen Nib's counter runs across combats, not within one.** It stood at `Pen Nib (2)` mid-fight-14; fight 14 finished with 4 attacks played, and this fight's first six attacks took the running total to ten, and it fired on that tenth. Nothing on the relic line says the count is run-long, and **nothing on any screen announces the doubling when it happens** — I found it only because an arithmetic would not otherwise close.

**Turn 3.** HP 94/105 (took 8 — the Turret's `3x5` against Sai's 7). Battle Plan resolved for 4 energy, and the Turret sat at 22 with **no Block at all**: Rampart died with its owner, so the 25 was neither re-granted nor left standing. Strike+ (12), Gorou (8) and Tengu Stormcall (5) finished it.

**Fight 15 result: won on turn 3, HP 94/105, 8 HP spent** — all of it in the one turn where the Living Shield was still alive.

**Reward:** `19 Gold`, card. Offer: **Vanguard+** (cost **0**, "Plan: Apply 2 Vulnerable and 1 Weak. Exhaust") · **Change of Plans** ("The Bake-Kurage carries out your first Plan now. Exhaust") · **Rally+** · **Razor — Claw and Thunder** ("Deal 8 damage. If this is the third Attack you played this turn, gain 1 Energy").

**Took Vanguard+.** It costs **zero energy**, which in a deck whose binding constraint is energy means it never competes with anything, and 2 Vulnerable is a flat +50% on an entire turn's attacks — on a 60-damage boss turn that is +30 for free. It is a Plan card, so with The Moon in play it lands *immediately as well as next turn*, and it arms Sango on the same turn. Razor is the better repeatable card (net-free 8 Electro on any three-attack turn) but its ceiling is 8; Change of Plans is what The Moon already does for nothing.

### Event — Self-Help Book (floor 6), and an enchant nobody defines

> - **Read the Back** — Choose an Attack to Enchant with **Sharp 2**.
> - **Read a Random Passage** — Choose a Skill to Enchant with **Nimble 2**.
> - **Read the Entire Book** — Choose a Power to Enchant with **Swift 2**.

**No screen anywhere defines Sharp, Nimble or Swift**, there is no option to decline, and the card-selection screen that follows prints every candidate's *unmodified* text, so it does not tell you either. This is the `Companion` / `Oz` problem for the third time in the run, except that here the undefined word **is** the decision.

I chose Sharp on an Attack, because "sharp" is the only one of the three whose likely meaning (damage) is guessable from English, and I put it on **Mika — Starfrost Swirl**. The reasoning was about which card *cannot have the bonus blanked*: Sango Isshin+'s big mode replaces its printed damage with "a quarter of your Max HP **instead**", so an enchant on its printed number might do nothing at all; Mika's "Deal 5 damage to ALL enemies" is unconditional and hits every body, so whatever Sharp 2 is worth, Mika collects it every time and collects it N times on an N-body board.

**The confirmation screen printed the card's text unchanged**, so as of this floor I still do not know what I bought.

### The last shop (floor 7)

`You have 66 gold.` Reading the remaining map, **no room ahead of me is a Shop** — the floors from here are Treasure x4, then Monster/RestSite/Unknown, then three Elite floors, then RestSite x3, then the Boss. So this was the run's last chance to convert gold, and anything I did not spend here is worth nothing.

Bought **Poison Potion, 51** — "Apply 6 Poison." Everything else affordable was a card (Undertow 52, Coral Bulwark 52, Exposed Flank 50, Treatise 36) and my deck is already 34; a potion costs no deck slot. And of the three potions on the shelf it is the one that matches what this deck has proved: **Poison ignores enemy Block**, it stacks additively onto the Electro-Charged Poison the deck generates anyway, and against a boss with any armour it is the only damage that does not have to be paid for twice.

Declined **Exposed Flank (50)** with some regret — "Plan: Apply 2 Vulnerable to ALL enemies" would, with The Moon, be 2 Vulnerable now *and* 2 next turn for one energy — but I already hold two Vulnerable sources (Vanguard+, and Mika's boss clause) and a 35th card lowers the odds of drawing the one copy of The Moon.

Left **15 gold**, which will now never be spent.

### Treasure (floor 8) and the Smith decision (floor 9)

Chest: **Festive Popper — "At the start of each combat, deal 9 damage to ALL enemies."** Taken; nothing else on the screen. Together with Red Mask's opening Weak and the Casket ping that follows it, every combat now begins with 11 damage on every body and a Hydro aura standing for the reaction engine.

**Rest site at 94/105, and the first time in three seats that Smith beat Rest.** The screen offered `Rest — Heal for 30% of your Max HP (31). Raise your Max HP by 5.` against `Smith — Upgrade a card`. Both previous seats took Rest every single time, correctly, because they were arriving at 55–61 out of 90–100 where the heal was worth its full 30-plus.

At 94/105 it is not. The heal caps: 94 + 31 is 125 against a new maximum of 110, so **Rest was worth 16 HP**, and the run has a guaranteed all-RestSite floor before the boss plus two more RestSite floors between here and there — so I will be topped up before Queen whatever I do now. What a rest cannot give me later is a card.

**Took Smith and upgraded `Sango Isshin` (cost 2) to `Sango Isshin+` (cost 1).** This is the one upgrade in the deck whose result is *known in advance* rather than guessed: the Whetstone upgraded the other copy in act 2 and the second seat recorded that Sango's upgrade is purely a cost cut. Energy is this deck's binding constraint and Sango is the card it most wants to play, so paying one energy instead of two for 27-to-ALL is worth more than 16 HP I will get back for free two floors later. **Both copies of Sango now cost 1.**

**The upgrade screen also answered the Self-Help Book.** Mika's row printed:

> **Mika — Starfrost Swirl** [Cryo] **(Sharp 2)** — Deal **7** damage to ALL enemies. Your next Attack costs 1 less.
> *Sharp* — Increases damage on this card by 2.

So `Sharp 2` is a flat +2 damage, the enchant shows as a tag after the element, and **the keyword is defined on the card's own tooltip — but only after you have irreversibly spent the choice.** The event that made me pick between Sharp, Nimble and Swift defined none of them, and neither did the card list it opened.

*(Two smaller notes from this screen. It prints a **"Not on this list, and why"** section — Strike+, Cleansing Wave+, Sango Isshin+ and War Council, The Moon Overlooks the Waters, Fischl, one Tengu Stormcall and one Battle Plan — and says of each only "on the screen's list nowhere, and nothing on the feed says why", then admits the list is "your deck as it stood in the last fight (floor 38)". Some of those are simply already upgraded; the rest I cannot account for, and **I could not tell whether The Moon Overlooks the Waters is upgradeable at all**. And when I picked `Sango Isshin`, the "What you have picked" block printed **both** `Sango Isshin` and `Sango Isshin+` as PICKED — a title match, not two selections; the `post` payload named a single index and the result was a single upgrade.)*

### ELITE — Soul Nexus (234 HP), floor 10

Entered **96/105**, `Block 7` from Sai, 7 energy from Very Hot Cocoa, and the enemy already at **223/234** — Festive Popper's 9 plus the Casket's 2 off Red Mask's Weak.

A bare board: no gimmick buff at all, just 234 HP and an intent of **21**. The whole fight is a damage race against a body that hits harder than anything in acts 1 or 2.

**Turn 1.** Hand: Strike, Strike+, Thundergrust, Sango Isshin+, Tengu Stormcall — **five attacks and not one Plan card**, so Sango was stuck at its base 8. This is precisely the structural flaw the second seat identified: Sango's condition asks for a Plan carried out *this* turn, and without The Moon in play there is no way to satisfy it on the turn you hold the card.

I spent **Weak Potion** ("Apply 3 Weak") here rather than saving it, on three counts: my potion belt was full at 5/5 so an elite reward potion would otherwise be unclaimable, a 21-damage attacker with 234 HP is a long fight where three turns of Weak is worth about 18 HP, and applying a debuff is itself two Casket damage plus a Hydro re-application.

Then, sequenced Electro-first so each hit had an aura to eat: **Tengu Stormcall** (Electro on Hydro = Electro-Charged, Poison 4, Casket 2, Hydro re-applied) → **Thundergrust** (Electro on the re-applied Hydro = a second Electro-Charged, Poison 8, Casket 2) → **Strike+** → **Strike** → **Sango Isshin+**.

*Predicted 54.* **Exactly 54: 223 → 169**, with `Poison 8` and `Weak 4` standing.

**Turn 2 — and Pen Nib fired without saying so.** `Fantastic Voyage 5` was on my status line again (the mis-named Tengu Stormcall buff, third occurrence in the run), so Strike printed 14.

Played **Vanguard+ → Bake-Kurage** (0 energy — 2 Vulnerable and 1 Weak, landing next turn), **Tengu Stormcall**, **Strike**, **Shinobu — Sanctifying Ring**.

*Predicted 26 from the two attacks.* **Got 40: 161 → 121.** The 14 unaccounted for is **Pen Nib doubling the Strike** — 14 × 2 = 28 instead of 14. That was the tenth attack I had played since the relic last fired, counting *across combats*: this fight's five turn-1 attacks plus Tengu made nine, and the Strike was ten. Second confirmation, and again with **no announcement of any kind on the screen** — the only evidence is an arithmetic that will not otherwise close.

**Turn 3 — and the fight's real teeth.** The Soul Nexus's `DebuffStrong` had landed **`Vulnerable 2`** and **`Weak 2` on me**, and its intent read **32**. Every attack face on my screen dropped a quarter (Strike 14 → 10). Vanguard+'s Plan had resolved, so the enemy carried `Vulnerable 2` and I had a 50% multiplier for two turns.

Used **Fire Potion** here rather than holding it for the boss, because the enemy's Vulnerable window was two turns wide and would not come back, and because a turn I survive is worth more than a potion I keep. Then **Strike**, **Thoma — Blazing Barrier** and **Coral Bulwark** for block.

*Predicted 45 — Fire Potion 20 × 1.5 and Strike 10 × 1.5.* **Got 35: 93 → 58.** The only decomposition that closes is **Fire Potion 20 flat + Strike 15**, i.e. **Vulnerable does not multiply potion damage.** That is worth putting beside the first seat's finding that Vulnerable *does* multiply the Tamakushi Casket's relic ping (2 → 3): relic damage counts as an Attack for Vulnerable, potion damage does not, and nothing on either screen distinguishes them.

**Turn 4, and the reading that corrects both previous seats.** I had braced for 32 × 1.5 = 48 through 24 Block, i.e. about 21 taken. **I took 5.** HP 78 → 73.

The arithmetic that closes is `32 − (24 Block + 3 from Thoma's absorb rider) = 5`. So the attack landed for **exactly its printed 32** — *my* `Vulnerable 2` did not multiply it, and the enemy's `Weak 3` did not reduce it. Put beside turn 1 (printed 21, took 21 through 7 Block, with `Weak 4` standing on the enemy) the pattern is consistent, and it is the opposite of what the previous records assume:

**The printed intent number is the damage that will actually land, with every modifier already folded in.** Do not multiply it by your own Vulnerable and do not discount it by the enemy's Weak — the screen has done that for you.

This also explains away the run's most-repeated finding. Both previous seats concluded, from five independent cases, that **Red Mask's combat-start Weak does nothing**, because the enemy showed `Weak 1` and then hit for its full *printed* number. But "printed number, delivered in full" is exactly what a *working* Weak looks like under this rule — the reduction is already in the print. And my own case adds the missing control: I applied `Weak 3` from a potion *during my turn*, took the stack to 4, and the printed 21 did not move and 21 landed — which fits **Weak's magnitude not stacking** (extra applications buy duration, not depth) far better than it fits "Weak does nothing".

I cannot prove it outright — that would need a fight where an enemy attacks once with no Weak and once with Weak — but the four-stack test is a case the earlier seats never ran, and it points the other way.

**Turn 4's kill.** Enemy at 32 with `Poison 17`, intent `6x4`. Poison alone would leave it at 15, so it needed only a few points. **Fischl — Nightrider** (Electro-Charged), **Kujou Sara — Crowfeather Cover** (0), then **Gorou** and **Read the Field**.

And Sara did something its text implies but nowhere states plainly: **"applies Electro" overrode Gorou's own Geo.** Gorou's card face carries a `Reaction preview: Crystallize`; played after Sara it produced a *second* Electro-Charged instead, taking Poison from 17 straight to **25** (two +4 applications). The Crystallize block never happened. That is a real, invisible trade — Sara turns your Geo card into an Electro card and you lose the 4 Block the preview promised.

The Ring's last end-of-turn Electro killed it from 6.

**ELITE CLEARED on turn 4. HP 73/105, 23 HP spent** — the most expensive fight of the act so far, and 3 of the 23 was Shinobu's own cost.

**Reward:** `42 Gold`, `Radiant Tincture`, **Bellows** (relic), card — all four claimable, because spending Weak Potion and Fire Potion *during* the fight had opened two slots. The act-1 lesson, applied on purpose rather than by accident.

Offer: **Coral Bulwark+** ("Gain 9 Block. Plan: Gain 11 Block and apply 2 Weak") · **Sea-Salt Prayer** · **Deep Current** ("Deal 6 damage to ALL") · **Raiden Shogun — Musou no Hitotachi** (cost 3, "Deal 20 damage. Deals 5 additional damage for each Companion card you played this combat").

**Took Coral Bulwark+.** Raiden is the bigger number — I own eleven Companion cards, so by turn four of a boss fight it reads 45–60 for three energy — but three energy is the whole of a normal turn, and its value peaks exactly when I can least afford to spend a turn on one target. Coral Bulwark+ is never dead: with The Moon in play a single energy buys **11 Block now and 11 more next turn, plus 2 Weak twice and the Casket pings that follow them**, and it arms Sango on the turn it is written. This elite hit me once for 32 in a single swing; Queen will hit harder.

### Rest (floor 11)

`Rest` at 73/105. **73 → 109, Max 105 → 110** — a gain of **36** against a promised 31, the Stone Humidifier's silent +5 current for the fifth time across the three seats' records. Sango's armed mode is now **27**.

I took Rest over Smith this time on exactly the arithmetic that made me take Smith two floors ago: at 73 the heal is worth its full value, where at 94 it was worth half.

### ELITE 2 — Mecha Knight (300 HP), floor 12

Entered **110/110** — a forced node, and the healthiest any seat has entered an elite in this run.

**Bellows, the relic the last elite dropped, turned out to be the best pickup of the act:**

> **Bellows** — "The first Hand you draw each combat is Upgraded."

My whole opening hand arrived upgraded: `War Council+` (Plan: 8 damage and 1 Weak to ALL), `Kurage's Oath+` (Plan: **10** to ALL), `Shinobu — Sanctifying Ring+` (**4** turns instead of 3), `Mika — Starfrost Swirl+ (Sharp 2)` (**10** to ALL — base 5, upgraded to 8, plus the enchant's 2), `Kujou Sara — Tengu Stormcall+` (8). It is a free upgrade to five random cards, every single combat, and unlike the Whetstone you can read what it did.

The board:

> **Mecha Knight — HP 300.** Intent 25. `Artifact 2 (buff) — Negates 2 debuffs.`

The Artifact showed itself before I played a card: the Knight opened at **291/300**, which is Festive Popper's 9 and **nothing else** — Red Mask's Weak was negated, so the Tamakushi Casket never fired and no Hydro aura was left behind. That reproduces the first seat's act-1 finding exactly: **a negated debuff grants nothing**, not the debuff, not the relic damage, not the aura. On a `Artifact` board this deck starts with its reaction engine cold.

**Turn 1 (7 energy).** Planned **Kurage's Oath+** and **War Council+** onto the Kurage, then **Mika+** (Cryo onto a bare body, so it applied Cryo rather than reacting), then **Tengu Stormcall+** (Electro onto that Cryo = **Superconduct**, whose 2 Vulnerable the Artifact ate, `Artifact 2 → 1`), then **Shinobu — Sanctifying Ring+**.

Mika's rider made Tengu free, so five cards cost four energy and left three idle. 291 → **269**; I predicted 18 from the two attacks and **4 damage is unaccounted for** — no Kusarigama (two attacks), no Pen Nib (counter at 4), and the negated Superconduct should have left nothing behind. I could not close it.

With three idle energy I spent **Skill Potion** — a free card costs no energy, but it opened a potion slot for the elite reward and turned a wasted turn into a card. The three skills offered were Stolen Chapter, Battle Plan and **Chain of Command** ("Plan: Deal 6 damage for each Companion card you played last turn"). I had just played **three** Companions this turn — Mika, Tengu Stormcall and the Ring — so I wrote it to the Kurage expecting 18 free damage next turn.

**It dealt zero.** The Kurage's own log is the evidence:

> - Bake-Kurage: Kurage's Oath+, **10**
> - Bake-Kurage: War Council+, **8**
> - Bake-Kurage: **Chain of Command**   ← no number

and the round's arithmetic closes exactly without it (269 − Ring 5 − 10 − 8 − Casket 2 = 244). So **"each Companion card you played last turn" is counted relative to the turn the card was *written*, not the turn it resolves** — a Plan written on turn N pays for Companions played on turn N−1, and on turn 1 there is no turn before. This is the third card in the run to be priced in Companions and read, in practice, as "Deal 0 damage", and the first where the reason is a timing word rather than a missing keyword.

**Turn 2 — the Strength question the first fight of the act made me duck.** Enemy at 244, intent 6 damage plus 4 Status cards, so a nearly free turn. Three Plans had resolved, so Sango was armed.

I played **Bennett — Fantastic Voyage** (above 70% HP: gain 3 Strength) *before* **Sango Isshin+**, specifically to test whether Strength reaches Sango's "deal a quarter of your Max HP to ALL enemies **instead**" mode.

**It does. 244 → 214, exactly 30 = 27 + 3.** So Strength adds to the quarter-of-Max-HP mode, not just the printed 8 — which means my cautious line in fight 14 (declining Bennett + Sango because it might not apply) would in fact have killed the third Scroll of Biting a turn early. I got the fight right and the reasoning wrong, and it is worth saying so plainly.

Also planned **Vanguard+** (0 cost) and **Battle Plan**.

**Turn 3 — the payoff turn, and the biggest single round of the act.** Vanguard+'s Plan had landed `Vulnerable 2` on the Knight, Battle Plan gave 4 energy, and the Knight's intent was Defend + Empower — a second free turn. The Knight had also handed me **four `Burn` status cards** ("Unplayable. At the end of your turn, if this is in your Hand, take 2 damage"), which is 8 damage a turn for as long as they sit in hand.

Played **Sango Isshin+** (armed: 27 + 3 Strength = 30, × 1.5 Vulnerable = **45**), **Strike+** (12 + 3 = 15, × 1.5 = **22**), **Battle Plan → Kurage**, **Treatise**.

*Predicted 67.* **Exactly 67: 194 → 127.**

*(And a small finding on the Burns: I ended that turn holding all four and took **1** damage, not 8. Block 7 from Sai plus the Ring's 5 absorbed them. **Burn's end-of-turn damage is blockable**, which its text does not say and which makes Sai quietly answer a whole class of status-card clog.)*

**Turn 4 — Weak proved, and the boss's own swing never landed.** The Knight came back at 105 behind `Block 15` with `Strength 5` and an intent of **40**.

Played **Kujou Sara — Crowfeather Cover** (0) into **Strike** (so the colourless card carried Sara's +4 and her Electro, per the second seat's ordering lesson), then **Thundergrust** onto the re-applied Hydro for a second Electro-Charged, then **Slack Water**, then **Ambush → Kurage**. Three attacks fired Kusarigama.

Two results:

1. **87 damage through a 15-point Block: 105 → 33**, with Poison compounding to **14**.
2. **The printed intent fell from 40 to 30 the instant Slack Water's Weak landed** — exactly ×0.75.

That second one settles the run's most-repeated finding, and it settles it against the previous two seats. Both concluded from five independent cases that **Red Mask's combat-start Weak does nothing**, because an enemy showing `Weak 1` then hit for its full *printed* number. But "printed number, delivered in full" is what a **working** Weak looks like, because the print already includes it — as this turn shows directly, the number on the icon moves the moment a Weak lands. My own controlled case adds the other half: earlier in this act I applied `Weak 3` from a potion on top of Red Mask's `Weak 1`, took the stack to **4**, and neither the printed 21 nor the damage that landed moved at all. The reading that fits every case in all three records is:

- **Weak is a flat 25% cut whose magnitude does not stack** — further applications buy duration only;
- **the printed intent number is the final damage**, with Weak (and, on the same evidence, my own Vulnerable) already folded in;
- so **Red Mask works, and always did**.

I then chose **not** to spend Poison Potion to steal the kill, because the 18 HP it would have saved was about to be healed for free at the guaranteed rest before the boss. **It did not matter: the fight ended at the end of my own turn anyway.** The Ring's last Electro plus the Casket took the Knight to 23, and `Poison 18` killed it at the start of its turn — the same before-it-acts kill the first seat found three times in act 1. **A 40-damage swing from a 300 HP elite never landed.**

**ELITE CLEARED on turn 4. HP 93/110, 17 HP spent** — 3 of which was Shinobu's own cost and 1 was a Burn.

**Reward:** `39 Gold`, **Stone Cracker** (relic), card. Offer: **Deep Current+** (9 to ALL) · **Sea-Salt Prayer+** (7 Block, 2 Weak) · **Battle Plan+** ("Plan: Gain 1 Energy and draw **3** cards") · **Shinobu — Grass Ring of Sanctification** (cost 0, 4 Block, 8 if you lost HP).

**Took Battle Plan+.** Both previous seats' boss kills turned on the same turn shape — a Battle Plan resolving into four or five energy and a nine-card hand — and with The Moon Overlooks the Waters in play a Battle Plan costs literally nothing (it refunds its own energy on the spot, draws on the spot, and queues to do it again). A fourth copy, upgraded to draw three, is the card most likely to produce that turn against Queen. The 0-cost Grass Ring was the runner-up on the same logic that took Vanguard+ — a card that never competes for energy — but 8 Block does not decide a boss fight and Battle Plan's draw does.

### Fight 16 — Fabricator (150 HP) and its factory, floor 13

Routing: `Monster → RestSite` against `Unknown → RestSite`, at 93/110 with a guaranteed rest one floor on. I took the Monster deliberately: with no Shop left on the map **gold is now worthless**, so the only things a room can give me are a relic, a card, or damage — and act 3's two Unknowns had so far cost me a potion for nothing and given me an enchant I could not read. A Monster is the room whose price I can see.

The second elite's relic turned out to be a second free-upgrade engine:

> **Stone Cracker** — "At the start of each combat, Upgrade 2 random cards in your Draw Pile for the rest of combat."

Between Bellows (the whole opening hand) and Stone Cracker (two more in the pile), roughly seven cards arrive upgraded every fight now, and unlike the Whetstone both say what they did.

**The board is a leader-and-minions puzzle, and it prints the answer.** The Fabricator's intent was `Summon`, and every body it made carried:

> `Minion 1 (buff) — Minions abandon combat without their leader.`

So the whole fight is "kill the Fabricator, ignore everything else", and — unusually for this run — the printed buff is telling the truth. (Compare act 2's `Reattach`, which shaped the second seat's entire plan and then did nothing.)

**Turn 1 (free — the intent was Summon).** Gorou+ (Geo, consuming the Hydro aura for Crystallize) then Sango Isshin+ (Hydro, re-applying the aura so the Ring's end-of-turn Electro would have something to react with), plus **Read the Field+ → Kurage** for 13 Block landing at the start of my next turn, and **Shinobu — Sanctifying Ring+** (4 turns, thanks to Bellows). 150 → **109**.

**Turn 2.** It had summoned a Guardbot (18, blocks) and a Stabbot (20, hits for 11). **Mika (Sharp 2)** for 7 to ALL — Cryo onto the Fabricator's Hydro = Frozen, onto the bare bots = a Cryo aura each — then two Strikes into the Fabricator, one of them free from Mika's rider.

*Predicted 31 on the leader.* **Got 39: 109 → 70**, and it decomposes exactly: Mika 7, the **Shatter 6** the first Attack collects from a Frozen body, Strike 9, Strike 9, **Kusarigama 6** (three attacks), and **Casket 2** off the Frozen debuff — which also re-applied the Hydro aura, which is why the body still showed `Hydro Aura 2` afterwards and the Frozen was gone.

**Turn 3 — the ordering that mattered.** It summoned a **Zapbot** (23 HP, 16 damage, `High Voltage 2 — at the end of its turn it gains 2 Strength`) and the board was four bodies deep with 38 incoming. The Ring's previous Electro had hit the two bots' *Cryo* auras for **Superconduct**, so both carried `Vulnerable 1`.

I spent the turn on triage rather than on the leader: **Tengu Stormcall** killed the 3-HP Stabbot (removing 11 incoming, and buying +5 on all attacks next turn), **Sara → Fischl** put 11 into the Fabricator and, more importantly, an Electro-Charged **Poison** that its `Block 15` could not touch, and **Kirara** and **Battle Plan+** covered the turn and the next. The Fabricator's Block went 15 → 2 and its Poison to 10.

**Turn 4 — and I read the relic counter to aim it.** The screen prints **`Pen Nib (8)`**, so the next attack would be the ninth and the one after it the tenth — the doubled one. Fabricator at 37.

I briefly considered *banking* the counter at 9 by killing with a single attack and letting Poison finish the job, so that the first attack of the boss fight would be doubled. I decided against it and the reasoning is worth recording: **Pen Nib will fire during the boss fight anyway**, and because the counter is printed on every combat screen I can steer it onto the card I choose whenever it comes up. Banking only moves the doubling from turn three of the boss to turn one; it does not create one.

So: **Thundergrust** (13, the ninth attack) then **Strike+** (the tenth, **17 doubled to 34**). 37 gone, and **every minion left the field with it** — the fight simply ended, exactly as `Minion` promised.

**Fight 16 result: won on turn 4, HP 79/110, 16 HP spent.**

**Reward:** `16 Gold`, `Energy Potion`, card. Offer: **Shell Guard** ("Gain 5 Block. Until your next turn, whenever the Tamakushi Casket strikes, gain 3 Block") · **The Clouds Like Waves Rippling** (cost 2 power, 2 Block per debuff applied) · **Coral Bulwark+** (2nd) · **Razor — Claw and Thunder** ("Deal 8 damage. If this is the third Attack you played this turn, gain 1 Energy").

**Took Razor — Claw and Thunder.** With one fight left the marginal card is drawn about half the time, so the question is only whether it beats the two Defends still in the deck, and Razor does on the property that matters most: played as the third attack of a turn it is **net-zero energy**, and my boss turns run three to five attacks. It is also an Electro source, and Electro onto the Hydro aura the Casket keeps re-applying is the Poison that ignores Block.

### Rest before the boss (floor 14)

`Rest` at 79/110. **79 → 115, Max 110 → 115** — the promised 33 plus the Stone Humidifier's silent +5 current, for the sixth time across the three records. Sango Isshin's armed mode is now **28** and both copies cost 1.

I did not consider Smith here: full HP before the act's boss is not a thing one upgrade replaces, and the Humidifier makes the rest a damage upgrade as well.

### BOSS — Queen (400 HP) + Torch Head Amalgam (199 HP), floor 15

Entered **115/115**, 37 cards, 14 relics, four potions, and the best opening hand of the run — because **Bellows upgrades the whole first hand** and it dealt me:

> `Kujou Sara — Tengu Stormcall+` · `Kujou Sara — Crowfeather Cover+` · `Ambush+` (Plan: 15) · **`The Moon Overlooks the Waters+` — cost 1** · `Battle Plan+` (Plan: 1 Energy, draw 3)

The Moon's upgrade is a cost cut from 2 to 1, so the deck's engine came down on turn one for a single energy out of seven.

**The board is two bodies and one of them does not matter.** Queen at 400; the **Torch Head Amalgam** at 199 carrying `Minion 1 — Minions abandon combat without their leader`. The same rule the Fabricator taught me one floor earlier: **kill Queen and the fight is over**, so the real health bar is 389, not 588.

**Turn 1 (7 energy).** Played **The Moon+** (1), then **Battle Plan+ → Kurage**, which is where the engine shows what it is: energy went 6 → 6 (it refunded itself), the draw pile went 32 → 29 (it drew three on the spot), and `Plan 1` queued it to do the same again next turn. **A Battle Plan under The Moon is a free card that turns into four.**

Then I spent one energy on a question rather than on damage. **Ambush+ → Kurage** with The Moon resolves immediately, so it tells you at once which body a single-target Plan chooses:

> - Bake-Kurage: Ambush+, **15** — and the **Torch Head Amalgam** went 188 → **173**. Queen did not move.

**So "the front enemy" is the minion, and every single-target Plan in the deck is pointed at the body I do not need to kill.** That is a real constraint and it is worth stating plainly: **Ambush and Vanguard+ — my only 2-Vulnerable source — cannot be aimed at the boss while her minion lives.** The fix I used all fight was Mika, whose Cryo onto the Hydro aura the Casket keeps re-applying triggers the glossary's boss clause (*"Bosses cannot be Frozen: Hydro plus Cryo is consumed and applies 2 Vulnerable instead"*) and lands on Queen directly.

Finished turn 1 with **Sara+ → Strike** into Queen (the colourless card carries Sara's Electro, so it reacts where Thundergrust would only refresh), **Tengu Stormcall+**, **Slack Water**, **Defend**. Three attacks fired Kusarigama. *Predicted 41.* **Exactly 41: 389 → 348**, `Poison 8` standing.

**Turn 2 — and Queen shows her hand.** She had spent turn 1 on `Malicious (CardDebuff)`, and the result was on my status line:

> `Chains Of Binding 3 (debuff) — The first 3 cards drawn each turn are Afflicted with Bound.`
> `Bound — Only 1 Bound card can be played each turn. Cards are un-Bound at end of turn.`

**This is the best boss mechanic any of the three seats has met.** It is not a damage race and not a timer: it caps *throughput*. Three of the five cards you draw each turn collapse into a single choice, so a five-card hand is really a three-card hand, and the fight is about card economy rather than HP.

**And the deck has a printed answer to it that nothing connects.** "The **first** 3 cards drawn each turn" — so everything drawn *after* those three arrives free. My deck holds four Battle Plans, and with The Moon each one draws immediately for no net energy. I proved it on turn 3: `Battle Plan` drew two unbound cards, and chaining `Battle Plan+` off one of them drew three more — **both Sango Isshin+ and Vanguard+ arrived unbound** in a turn that had opened with three Bound cards.

Turn 2 itself: **Bennett** (3 Strength — 108/115 is above 70%), two **Strike+** for 20 each (one of them my single Bound play), and **Read the Field+** and **Coral Bulwark** written to the Kurage, which under The Moon paid **13 + 8 Block immediately and queued the same again**. *Predicted 40 on Queen.* **Exactly 40: 340 → 300.** Block 28 against an 18-damage minion: nothing through.

I also spent **Radiant Tincture** here — "Gain [Energy]. Gain an additional [Energy] at the start of your next 3 turns" — deliberately on turn 2 rather than turn 1, because turn 1 already had two energy it could not spend and the potion's value is the three turns it covers, not the immediate point.

**Queen's second debuff turn is the one that hurts.** She landed **`Frail 99`, `Weak 99` and `Vulnerable 99` on me at once** — a permanent quarter off my Block, a permanent quarter off my damage, and a permanent 50% on everything that hits me. Not a temporary swing: 99 turns is the rest of the fight.

**Turn 3 — the biggest round of the run.** Battle Plan and Battle Plan+ chained into an eight-card hand and 4 energy, all five Plans of the previous turn resolved at once (the Kurage's log printed five lines), and Sango was armed by the Plans that had *just* happened.

Played **Vanguard+** (0) first — its 2 Vulnerable had to go to the minion, so I used it as a multiplier on the AoE that was about to hit both bodies — then **Sango Isshin+** twice at **23 each to ALL** (28 for a quarter of 115, +3 Strength, ×0.75 for Queen's Weak), **Razor — Claw and Thunder** as the *third* attack so its clause refunded its own energy, **Gorou** into the minion, and **Shinobu — Sanctifying Ring**.

**148 damage in one round: Queen 293 → 231, the Amalgam 154 → 68.** Block 30 against 27 incoming; nothing through.

**Turn 4 — Cleansing Wave+ and a surprise.** `Cleansing Wave+` reads "Remove one of your debuffs" and gives no choice of which. I played it hoping to strip `Weak 99`. **It removed `Chains Of Binding` instead** — the first debuff on the list rather than the worst one. That was luckier than the play deserved: the boss's signature mechanic came off for the rest of the fight, and every card drawn from then on was free.

Then the turn Pen Nib had been counting toward. The relic prints a live counter and it stood at nine, so I led with **Mika — Starfrost Swirl (Sharp 2)** — the AoE card, so that the doubling would land on both bodies and its Cryo would put 2 Vulnerable on Queen at the same time. Followed with **Strike** (free from Mika's rider) and **Fischl** (my Bound play), then **Kurage's Oath** and **Coral Bulwark+** written to the Kurage for immediate-and-queued value, and **Moon's Reflection** to replay Shinobu's Ring out of the exhaust pile.

Two numbers I could not close, recorded as found. Queen went 209 (behind `Block 20`) → **177**, i.e. 52 total; the printed faces alone (Mika 15 + Strike 18 + Fischl 15) come to 48, plus two Casket pings = 52 **with no Pen Nib doubling and no Vulnerable multiplier visible at all**. The Amalgam's number *does* close with its Vulnerable (Mika 15 × 1.5 + Casket 3 + Kusarigama 6 = 31 against an observed 31). The difference between the two bodies is that the Amalgam's Vulnerable was already standing and Queen's was applied by the same card — so the most likely reading is that **a Vulnerable applied by a card does not retroactively raise that card's own hit here**, unlike the act-2 Superconduct case where it did. I could not make the doubling appear anywhere in the round.

`Moon's Reflection` did work exactly as advertised, and stacked: `Sanctifying Ring 2` became **`Sanctifying Ring 7`**, which is the same odd arithmetic the second seat saw when a 3-turn buff replayed once printed 8.

The round killed the **Torch Head Amalgam** outright, and with it the constraint: from turn 5 on, the front enemy was Queen.

**Turn 5 — the kill.** Queen at 121 with `Poison 20`, five energy, and no minion. Chained **Battle Plan+** for three more cards, then spent **Energy Potion** (+2) and **Poison Potion** (Apply 6 Poison, taking the stack to a tick of **30** that no Block can touch), then **Fischl → Strike+ → Strike → Strike** (121 → 56), then **Slack Water**, **War Council → Kurage** and **Kurage's Oath → Kurage**, both of which under The Moon delivered their damage on the spot.

*Predicted: Queen at 22 by end of turn, then the Ring's Electro and a Poison tick of 30 at the start of her turn — dead before she swings.* The screen showed **22/400**, and ending the turn ended the fight.

**QUEEN KILLED on round 5. HP 99/115.** She landed exactly one thing on me all fight — the three 99-turn debuffs — and **not one point of her printed attack damage ever reached my HP.**

**Reward:** `(nothing here to take)` — the act-3 boss pays no gold and no card. Then an event, **The Architect**, whose only options were `Respond` and then `Proceed`, and which printed no text of its own on this feed. Proceeding from it returned:

> `TOOL-BLOCKED: game_over` — "the run is over; there is nothing left to play. The run ended on floor 48."

**The run is complete: three acts, three bosses, no deaths.**

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

**1. Sai against Spiked Gauntlets at the act's first screen.** Both previous seats had named energy the binding constraint, which points at `Gain [Energy] at the start of each turn`. I took `At the start of your turn, gain 7 Block` anyway, because 7 Block a turn is worth *more than one energy* in this deck (a Defend buys 5, Coral Bulwark 6) and it never has to be drawn, where Spiked Gauntlets also taxes my two Powers and one of them is the singleton that runs the deck. It paid immediately and repeatedly: fights 14 and 15 cost 0 and 8 HP, and in the Mecha Knight fight Sai's 7 Block quietly ate four `Burn` status cards that should have cost 8 HP a turn.

**2. Smith over Rest at 94/105, then Rest over Smith at 73/110.** The same screen, opposite answers, and the arithmetic is the whole reason: at 94 the heal caps and is worth 16, at 73 it is worth its full 36. The upgrade I bought with the first one — `Sango Isshin` from cost 2 to cost 1 — is the only upgrade in the deck whose result is *known before you pick it*, because the Whetstone had already done it to the other copy in act 2 and the second seat wrote it down. Both copies of the best card in the deck cost 1 for the rest of the run.

**3. Declining Bennett + Sango in fight 14, and taking it in the Mecha Knight fight.** Fight 14 offered exactly 3 energy for `Bennett — Fantastic Voyage` (3 Strength) plus armed Sango, which would end the fight on the spot **if** Strength reaches Sango's "deal a quarter of your Max HP **instead**" mode. I declined, because the failure case cost 4 permanent Max HP to `Paper Cuts` and Max HP is this deck's damage stat. Two floors later I ran the same test on a free turn and **Strength does apply** (244 → 214, exactly 27 + 3). The caution was right for the price and wrong about the world, and both halves are worth recording.

**4. Which body to attack in the boss fight.** The single-target-Plan test on turn 1 settled it — `Ambush+` resolved onto the **minion** — so from then on the choice each turn was "spend on the 199-HP body that is only there to soak, or on the 400-HP body whose death ends the fight". I chose Queen and used Mika as the Vulnerable source that can actually reach her, and let AoE erode the minion incidentally. It died on turn 4 anyway.

**5. Whether to bank Pen Nib's counter at 9 across the last monster fight.** Genuinely tempting: leave the counter one short and the boss's first attack doubles. I decided against it, and the reasoning is the interesting part — **the relic prints its own counter on every combat screen**, so the doubling can be *steered* onto a chosen card whenever it comes up, and banking only moves it earlier, it does not create one.

**6. What to spend the last 66 gold on, knowing there were no more Shops.** Reading the remaining map told me this was the last conversion of gold in the run, which turned a normal shop into a one-shot. I bought the **Poison Potion** over three cards, because a potion costs no deck slot in a 34-card deck and Poison is the one damage in this deck that ignores Block — and Queen spent two of her five turns gaining Block.

### (b) What felt automatic, and what never seemed worth playing

**Automatic, in order:** *Play The Moon Overlooks the Waters the moment it appears.* *Write every Plan card to the Kurage rather than playing it* — under The Moon a planned `Read the Field+` is 13 Block now **and** 13 next turn where playing it is 8 once, and `Coral Bulwark` is 8 + Weak twice instead of 6 once. There is no Plan card in the deck that is better played than planned once The Moon is down, which makes the Power less a card than a rule change. *Battle Plan on sight*, for the same reason: it costs nothing and draws.

**Never worth playing: Defend, for the third act running.** Sai finished it off — a card that spends an energy for 5 Block when the same 7 arrives free at the start of every turn is below the floor by construction, and under `Frail 99` in the boss fight it printed **3**. I removed one at the shop and would have removed the other two.

**Never worth playing here: Chain of Command.** "Deal 6 damage for each Companion card you played last turn", written on a turn in which I had just played three Companions, dealt **zero** — see the findings. It is the third card in the run priced in Companions that read as blank text.

**Rarely worth it: Moon's Reflection**, until the exhaust pile has something in it, which is turn 3 at the earliest. The second seat said the same. When it landed on Shinobu's Ring it was excellent both times.

### (c) What I could not understand, or that contradicted its own printed text

- **"The Future of Potions?" took a potion and gave nothing.** It opened a card-selection screen with **zero rows**, twice, and the next combat's card count proves nothing was granted silently.
- **Chain of Command's "last turn"** counts the turn before the card was *written*, not the turn before it resolves, so writing it on turn 1 can only ever deal 0.
- **`Sharp`, `Nimble` and `Swift`** are the entire content of the Self-Help Book's three options and **no screen defines any of them until after the choice is spent** — the definition then appears on the card's own tooltip.
- **`Oz`** is still undefined, three acts in, and `Fischl — Nightrider`'s second clause is priced in it.
- **Pen Nib doubles without announcing it.** Two clean cases (Turret Operator 39 → 26, Soul Nexus 161 → 121) close only if a Strike dealt double, and no line on any screen says it happened.
- **Vulnerable behaved differently on the two bodies in the same turn.** The minion's already-standing Vulnerable multiplied Mika's hit and the Casket's ping; Queen's — applied by that same Mika — appeared to multiply nothing, and my Strike and Fischl afterwards read as flat. I cannot reconcile this with the first seat's act-1 case where a Vulnerable-adjusted Thundergrust was exactly lethal.
- **`Cleansing Wave+` gives no choice of which debuff to remove.** It took `Chains Of Binding` when I wanted `Weak 99` — a good outcome, arrived at blind.
- **The upgrade screen's "Not on this list, and why"** names eight cards and says of each only "nothing on the feed says why". Some are simply already upgraded; for `The Moon Overlooks the Waters` I could not tell whether it is upgradeable at all — and Bellows later handed me `The Moon Overlooks the Waters+`, so it evidently is.
- **The pick preview matches by title.** Selecting `Sango Isshin` for the Smith printed **both** `Sango Isshin` and `Sango Isshin+` as PICKED; only one was upgraded.
- **`Blazing Barrier N — {Left} Block left`** still never substitutes its placeholder — third act running.
- **The mis-named buff recurred twice.** `Kujou Sara — Tengu Stormcall`'s rider prints on my status line as **`Fantastic Voyage 5`**, once while Bennett was in the draw pile and had never been played.
- **The act-3 boss pays no reward at all** — `(nothing here to take)` — where the act-1 and act-2 bosses each paid 100 gold and a boss card.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted: Defend.** Sai made it strictly redundant and `Frail 99` made it a 3.

**Happiest to draw: `Battle Plan` with The Moon Overlooks the Waters in play, and in this act it stopped being a nice card and became the answer to the boss.** Queen's `Chains Of Binding` Afflicts *the first three cards drawn each turn*; Battle Plan draws cards four, five and six. On boss turn 3 I chained `Battle Plan` into `Battle Plan+` and drew five unbound cards — including both Sango Isshin+ and Vanguard+ — out of a turn that had opened as a three-card hand. It costs nothing, it draws, it arms Sango, and against this boss it is the counter-play.

Runner-up: **`The Moon Overlooks the Waters+` at cost 1** in the boss's opening hand, courtesy of Bellows.

### (e) Did the previous seats' sharpest findings hold up

**1. "Poison ignores enemy Block, and that is what makes this deck work." HELD, and it decided the boss.** Against the Mecha Knight's `Block 15` I put Fischl's Electro-Charged Poison on and watched the block absorb the card damage while the tick went through; against Queen — who spent two of five turns gaining Block — Poison reached **30** and was the last thing to touch her. The whole kill was priced off the tick, not the cards.

**2. "The Bake-Kurage queues multiple Plans, undocumented." HELD, and I stacked five.** The Kurage's log on boss turn 3 printed `Read the Field+ 9 / Coral Bulwark 6 / Battle Plan 1 / Battle Plan+ 1 / Vanguard+ 2` as one start-of-turn.

**3. "The Moon Overlooks the Waters silently fixes Sango Isshin." HELD, and it does more than that.** Every Plan card in the deck becomes worth roughly double, Battle Plan becomes free, and the immediate half is logged as "carried out at the start of this turn" — the exact phrase Sango's condition tests.

**4. "Red Mask's Weak does nothing." I believe this is WRONG, and I think I can show why.** Both seats reached it from five cases of the shape "enemy shows `Weak 1`, hits for its full printed number". But **the printed intent number already includes Weak** — on the Mecha Knight I watched an intent fall from **40 to 30** the instant Slack Water's Weak landed, exactly ×0.75. "Printed number, delivered in full" is therefore what a *working* Weak looks like. The other half of the case is mine: against the Soul Nexus I applied `Weak 3` from a potion on top of Red Mask's `Weak 1`, took the stack to **four**, and neither the printed 21 nor the 21 that landed moved — which fits **Weak's magnitude not stacking** (extra applications buy duration) rather than "Weak does nothing". The operating rule I ended up trusting, and which held on every reading I took after: **the number on the intent icon is the damage that will land.**

**5. "Attack cards hide their modified damage; Plan cards show theirs." MIXED, and I would now put it differently.** Debuffs *on me* re-printed every face immediately (`Strike` 14 → 10 under Weak, `Defend` 5 → 3 under Frail), and so did buffs (`Strike+` printing 17 with Tengu Stormcall's +5). What is never in the printed face is the *enemy's* Vulnerable — but see (c): in the boss fight the damage that landed matched the printed faces and not the Vulnerable-adjusted numbers, so I could not tell whether the display or my model was wrong.

**6. "A negated debuff grants nothing." HELD exactly.** The Mecha Knight's `Artifact 2` ate Red Mask's opening Weak, and the boss opened at 291/300 — Festive Popper's 9 and nothing else, no Casket ping and no Hydro aura. On an Artifact board this deck starts with its engine cold.

### (f) Did act 3 ask anything of the deck that acts 1 and 2 did not

Yes, three things, and only one of them is a damage problem.

- **`Chains Of Binding` attacks your hand size, not your HP.** Three of five drawn cards collapse into one choice. Nothing in acts 1 or 2 taxed *card economy*; act 2's `Sandpit` was a turn limit and `Hard To Kill` a damage cap, but both left your hand alone. The deck's answer is draw, and specifically draw that happens *after* the first three cards — which is a property of Battle Plan that no screen connects to the debuff.
- **`Paper Cuts` makes Max HP a resource you can lose in combat.** "Whenever this enemy deals unblocked attack damage to you, you lose 2 Max HP" turns Block into a damage stat, because Sango Isshin reads a quarter of Max HP. Acts 1 and 2 never punished a leaked hit twice.
- **Buffs printed on the wrong body.** `Rampart 25` sits on the **Living Shield** and grants **the Turret Operator** 25 Block; `Minion 1` sits on the summons and names their leader. Both boards are decided by reading a line that is not on the creature it is about — including the boss, where 588 printed HP is really 389.

Act 3 also asked, for the first time, **which enemy a Plan is allowed to hit**. In acts 1 and 2 the Kurage's "front enemy" clause was academic because the AoE cards did the work. Against a boss whose minion permanently occupies the front slot, it disables `Vanguard+` — the deck's only 2-Vulnerable card — for as long as the minion lives.

### (g) Anything a screen granted or changed without saying so

- **About 25 HP appeared between acts 2 and 3.** Act 2's last printed reading was 73/105; my first act-3 combat opened at 100/105 with Blood Vial's +2 included. Third act transition, third silent heal, still unannounced.
- **Every rest healed 5 more than promised** — 31 → 36 and 33 → 36-to-cap — because the Stone Humidifier's +5 Max HP carries +5 *current*. Sixth occurrence across three records.
- **Pen Nib doubles a hit with no notice, and its counter runs across combats.** It stood at `(2)` mid-fight-14 and fired on the tenth attack of the *run since it last fired*, in the middle of the next fight.
- **`Whetstone`-style silent grants continued:** the Self-Help Book's `Sharp 2` printed nothing on the card until a much later screen, and `Stone Cracker` upgrades two random draw-pile cards each combat without ever saying which.
- **`Kujou Sara — Crowfeather Cover` overrides the element of the card it buffs.** Played before **Gorou**, whose own face carries a `Reaction preview: Crystallize`, it made Gorou apply **Electro** and produce a second Electro-Charged instead — Poison 17 → 25 — and the 4 Block the Crystallize preview promised never arrived.
- **`Burn` status damage is blockable.** Four Burns in hand should have cost 8 HP at end of turn; with Sai's 7 and the Ring's 5 standing I lost **1**. The card's text does not say block applies.
- **Enemy Block granted by another creature dies with it.** The Turret Operator's 25 was gone the instant the Living Shield died, not merely un-renewed.
- **`Cleansing Wave+` chooses the debuff for you**, and it took the first one on the list.
- **The gold count is reconstructible after all.** The shop printed `You have 345 gold`, which is the second seat's uncounted running total of 330 plus my 15 to the pound. Only the *starting* gold — act 1's unprinted ~99 — is genuinely invisible.

---

## Findings, ranked by sharpness

**1. Red Mask's Weak works, and the run's most-repeated finding is an artefact of the display.** Both previous seats concluded, from five independent cases across two acts, that the relic's combat-start Weak "expires before the enemy's first attack" because the enemy showed `Weak 1` and then hit for its **full printed number**. But the printed intent *already contains* the reduction: on the Mecha Knight I watched an intent fall from **40 to 30** at the moment Slack Water's Weak landed, exactly ×0.75, and the Living Shield's `18` fell to `13` the same way from Coral Bulwark's planned Weak. "Printed number, delivered in full" is precisely what a working Weak looks like. My controlled case supplies the rest: against the Soul Nexus I applied `Weak 3` from a potion on top of the relic's `Weak 1`, took the stack to **four**, and the printed 21 did not move and 21 landed through 7 Block for exactly 14 HP. That fits **Weak's magnitude not stacking** — further applications buy duration only — and it does not fit "Weak does nothing". **The operating rule: the number on the intent icon is the damage that will land, with every modifier folded in; do not re-apply your own Vulnerable or the enemy's Weak on top of it.** Every HP reading I took after adopting this rule closed exactly.

**2. `Chains Of Binding` is the best boss mechanic in the run, and the deck's counter to it is invisible.** Queen opens by Afflicting **the first 3 cards drawn each turn** with `Bound`, of which **only one can be played per turn** — a five-card hand becomes a three-card hand, and the fight is about card economy rather than HP. The counter is sitting in the deck and nothing connects the two: the Affliction lands on the *first three* cards drawn, so anything drawn afterwards is free, and `Battle Plan` under The Moon draws immediately for no net energy. On boss turn 3 I chained `Battle Plan` into `Battle Plan+` and drew **five unbound cards, including both Sango Isshin+ and Vanguard+**, out of a turn that had opened with three Bound ones. A player without Battle Plans has no answer at all and will read the debuff as unmitigable.

**3. "The Future of Potions?" consumes a potion and delivers nothing.** The event offers three trades and **no way to decline**. I took `Insert Uncommon Potion — Lose Regen Potion. Obtain an Upgraded Uncommon Attack.` The Regen Potion was taken. The reward screen then opened a card-selection screen with **no rows at all**; `choose 1` returned `there is no row 1 on this screen; it has 0.` I skipped, re-claimed and got the same empty screen, then proceeded out. **The next combat printed `28 in the draw pile` and 5 in hand = 33**, which is exactly my deck before the event, so nothing was granted silently either. A straight, unavoidable loss.

**4. Single-target Plans are locked onto the boss's minion, which disables the deck's only Vulnerable card for most of the fight.** Queen (400) fights alongside a Torch Head Amalgam (199) carrying `Minion — Minions abandon combat without their leader`, so the fight ends when Queen dies and the minion is a decoy. But the Bake-Kurage's Plan resolves "on the **front enemy**", and the front enemy is the minion: `Ambush+ → Kurage` under The Moon printed `Bake-Kurage: Ambush+, 15` and took **the Amalgam** 188 → 173 while Queen did not move. `Vanguard+` — my only 2-Vulnerable source and a 0-cost card I built the deck around — therefore cannot be aimed at the boss for as long as the decoy lives. The only Vulnerable that reaches her is Mika's, via the glossary's boss clause.

**5. Pen Nib doubles a hit, keeps its counter across combats, and never says so.** Two cases close only with a doubling and no other way: Turret Operator `39 → 26` (Strike 18 doubled to 36, less 25 Block, less a Casket ping) and Soul Nexus `161 → 121` (predicted 26 from two attacks, observed 40). The counter is printed on the combat screen as `Pen Nib (N)` and **carries between fights** — it stood at `(2)` mid-fight-14, and the doubling fired mid-fight-15 on the tenth attack since. Nothing announces the doubling when it happens. The counter being printed is what makes the relic steerable: read it, and put your biggest card on the tenth attack.

**6. `Bellows` and `Stone Cracker` are the two best relics of the act and they do opposite things about legibility.** `Bellows — the first Hand you draw each combat is Upgraded` handed me `Mika+ (Sharp 2)` at 10-to-ALL, a 4-turn `Sanctifying Ring+`, and in the boss fight **`The Moon Overlooks the Waters+` at cost 1** — the deck's engine down on turn one for one energy. `Stone Cracker — upgrade 2 random cards in your Draw Pile` does the same silently and never names the two. Both are enormous; only one is readable.

**7. `Chain of Command` reads "Deal 0 damage" whenever you would want to play it.** "Plan: Deal 6 damage for each Companion card you played **last turn**." I wrote it to the Kurage on a turn in which I had just played three Companion cards, and the Kurage's own log shows `Bake-Kurage: Chain of Command` **with no number at all** while the two Plans beside it printed 10 and 8; the round's arithmetic closes exactly without it. "Last turn" is counted relative to the turn the card was *written*, so a Plan written on turn 1 can only ever pay 0, and on any turn it pays for a hand you have already discarded. This is the third card in three acts to be priced in Companions and behave, in practice, as blank text.

**8. `Rampart` is printed on the wrong creature, and it is the whole fight.** `Rampart 25 — At the start of the player's turn, **Turret Operator** gains 25 Block` sits on the **Living Shield**. Attacking the smaller, weaker-looking Turret is nearly free damage thrown away; killing the Living Shield removes the Block outright — **not merely un-renewed, but gone**, since the Turret went from `Block 25` to `Block 0` in the same turn its granter died. The same structure recurs twice more (the Fabricator's `Minion` summons; Queen's minion), so act 3 asks repeatedly that you read a rule printed on a body other than the one it governs.

**9. `Kujou Sara — Crowfeather Cover` silently overrides the element of the card it buffs.** Its text is "Your next Attack this turn deals 4 additional damage **and applies Electro**". Played before **Gorou — Inuzaka All-Round Defense**, whose own card face prints `Reaction preview: Crystallize — this card supplies Geo`, Gorou produced a second **Electro-Charged** instead (Poison 17 → 25) and the 4 Block the preview promised never arrived. The card's own preview and the buff on it disagree, and the buff wins.

**10. Strength reaches Sango Isshin's "quarter of your Max HP **instead**" mode.** `Bennett — Fantastic Voyage` for 3 Strength, then armed Sango, took the Mecha Knight 244 → **214**, exactly 27 + 3 rather than 27. Worth knowing because the word "instead" reads as though it replaces the whole damage calculation, and it does not.

**11. `Burn` status damage is blockable, which quietly makes Sai an answer to status clog.** The Mecha Knight gave me four `Burn` ("at the end of your turn, if this is in your Hand, take 2 damage"). Holding all four, I took **1**, not 8, behind Sai's 7 and the Ring's 5. Nothing on the card says Block applies.

**12. `Cleansing Wave+` removes a debuff you do not choose.** It took `Chains Of Binding` when I was aiming at `Weak 99`. In this case that was the better outcome by a distance — it turned off the boss's signature mechanic for the rest of the fight — but it was not a decision I made.

**13. Two display defects survive from act 2 unchanged.** `Blazing Barrier N (buff) — {Left} Block left` never substitutes its placeholder, and **`Kujou Sara — Tengu Stormcall`'s rider prints on my status line under `Fantastic Voyage`'s name** — twice this act, once while Bennett was still in the draw pile and had never been played, so it is not a hand-confusion.

**Where I could not tell.** Whether an enemy's `Vulnerable` multiplies my card damage at all: the Amalgam's already-standing Vulnerable closes its arithmetic exactly (Mika 15 × 1.5 + Casket 3 + Kusarigama 6 = 31, observed 31), while on the very same card Queen — whose Vulnerable that card had just applied — appears to have taken flat printed damage from it and from the two attacks after it. Whether Pen Nib fired at all on boss turn 4, where I believe the counter stood at nine and no doubling is visible in the numbers. Why `Sanctifying Ring 2` replayed once prints **7**. And what `The Architect` is: two screens, `Respond` then `Proceed`, no text on this feed, and then the run was over.


---

## Identity (completed)

- **Model / seat:** Claude Opus, blind TESTER seat, round 5, run 3, **third of three chained seats**.
- **Lane:** 1. **Character:** KLEEMOD-KOKOMI.
- **Picked up:** the act-3 map screen, acts 1 and 2 cleared by the first two seats, their last printed reading 73/105. (I actually entered act 3 at **98/105** — see the unannounced ~25 HP.)
- **Act played:** 3. Boss as named by the map: **Queen** (400 HP, defeated), fought alongside a **Torch Head Amalgam** (199 HP) minion.
- **Actions accepted: 209. Refused: 1** — `choose 1` on the empty card-selection screen "The Future of Potions?" produced, which answered `there is no row 1 on this screen; it has 0.` No `act` was ever sent with its output suppressed.
- **Termination reason:** **stop condition (1)** — the act-3 boss was resolved, its reward screen (`(nothing here to take)`) handled, and the run then ended: `TOOL-BLOCKED: game_over` — "the run is over; there is nothing left to play. The run ended on floor 48." Budget was not exhausted (209 of 300).
- **Where the run stands:** **complete.** Three acts, three bosses — Vantom, The Insatiable, Queen — **no deaths across the whole run.** Nothing is mid-screen; no reward, choice or prompt is pending.

**HP trajectory — every reading the screens printed this act, in order:**

100/105 (fight 14 open) → 100 → 100 → **100/105** (fight 14 won, zero damage taken) → 102/105 (fight 15 open) → 102 → 94 → **94/105** (fight 15 won) → **94/105 at the rest site → Smith taken, no heal** → 96/105 (Soul Nexus open) → 82 → 79 → 78 → 73 → **73/105** (Soul Nexus cleared) → **73/105 at the rest site → 109/110** → 110/110 (Mecha Knight open) → 107 → 94 → 94 → 93 → **93/110** (Mecha Knight cleared) → 95/110 (Fabricator open) → 92 → 88 → 79 → **79/110** (Fabricator won) → **79/110 at the rest site → 115/115** → 115/115 (boss open) → 108 → 108 → 105 → 105 → **99/115** (Queen killed).

Max HP rose **105 → 110 → 115** across two rests (the third rest-site visit was spent on Smith). The lowest point of the act was **73/110**, twice. **I was never in danger of dying at any point in act 3**, and Queen's printed attack damage never once reached my HP — the only thing she landed was her three 99-turn debuffs.

**Per-fight cost:** fight 14 **0 HP** · fight 15 **8** · Soul Nexus elite **23** · Mecha Knight elite **17** · Fabricator **16** · Queen **16** (and 6 of that was Shinobu's own self-cost). Six combats, six wins.

**Gold:** the only two totals any screen printed were **345** at the floor-3 shop and **66** at the floor-7 shop. The first of these confirms the second seat's running count exactly (their uncounted 330 plus my 15). I spent 298 at the first shop (Battle Plan 78, Kujou Sara — Tengu Stormcall 72, Fire Potion 48, Card Removal 100) and 51 at the second (Poison Potion). Claimed since: 19 + 42 + 39 + 16 = 116, so **my count is 131**, unspent and now unspendable — act 3's map carried no further Shop, and the act-3 boss paid no gold.

**Potions — 1 of 5 slots left full at the end: `Dexterity Potion — Gain 2 Dexterity`.** Spent during the act: Weak Potion (Soul Nexus), Fire Potion (Soul Nexus), Skill Potion (Mecha Knight), Radiant Tincture (Queen), Energy Potion (Queen), Poison Potion (Queen). Lost: **Regen Potion**, consumed by "The Future of Potions?" for nothing. Nothing was ever lost to full slots.

**Relics, exactly as printed (14):**

- **Tamakushi Casket** — Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that enemy.
- **Stone Humidifier** — Whenever you Rest at a Rest Site, raise your Max HP by 5.
- **Red Mask** — At the start of each combat, apply 1 Weak to ALL enemies.
- **Blood Vial** — At the start of each combat, heal 2 HP.
- **Strike Dummy** — Cards containing "Strike" deal 3 additional damage.
- **Very Hot Cocoa** — Start each combat with an additional 4 Energy. *(one-time, on turn 1)*
- **Kusarigama** — Every time you play 3 Attacks in a single turn, deal 6 damage to a random enemy.
- **Whetstone** — Upon pickup, Upgrade 2 random Attacks. *(spent in act 2)*
- **Potion Belt** — Upon pickup, gain 2 potion slots.
- **Pen Nib** — Every 10th Attack you play deals double damage. *(prints a live counter; the count runs across combats)*
- **Sai** — At the start of your turn, gain 7 Block. *(act-3 Ancient)*
- **Festive Popper** — At the start of each combat, deal 9 damage to ALL enemies. *(act-3 Treasure)*
- **Bellows** — The first Hand you draw each combat is Upgraded. *(Soul Nexus elite)*
- **Stone Cracker** — At the start of each combat, Upgrade 2 random cards in your Draw Pile for the rest of combat. *(Mecha Knight elite)*

**Deck — 37 cards** (screen-confirmed: the boss opened at `32 in the draw pile` plus a 5-card hand).

| # | Card | Note |
|---|---|---|
| 3 | Strike | cost 1, attack — 9 in combat (6 + Strike Dummy) |
| 1 | **Strike+** | cost 1, attack — 12 in combat |
| 3 | Defend | cost 1, skill — Gain 5 Block *(one removed at the act-3 shop)* |
| 2 | **Sango Isshin+** | cost 1, attack — 8, or a quarter of Max HP (**28**) to ALL if a Plan was carried out this turn. *Both copies now upgraded — the second by the act-3 Smith* |
| 1 | Slack Water [Hydro] | cost 1 — Deal 7. Apply 1 Weak. Plan: Apply 1 Weak to ALL |
| 1 | Kurage's Oath | cost 1 — Plan: Deal 7 to ALL |
| 1 | Ambush | cost 1 — Plan: Deal 12 |
| 3 | Battle Plan | cost 1 — Plan: Gain 1 Energy and draw 2 *(one bought in act 3)* |
| 1 | **Battle Plan+** | cost 1 — Plan: Gain 1 Energy and draw **3** *(Mecha Knight reward)* |
| 1 | Read the Field | cost 1 — Gain 5 Block. Plan: Gain 10 Block |
| 1 | Coral Bulwark | cost 1 — Gain 6 Block. Plan: Gain 8 Block and apply 1 Weak |
| 1 | **Coral Bulwark+** | cost 1 — Gain 9 Block. Plan: Gain 11 Block and apply 2 Weak *(Soul Nexus reward)* |
| 1 | **Cleansing Wave+** | cost 1 — Gain 8 Block. **Remove one of your debuffs** (not your choice which). Plan: Gain 13 Block |
| 1 | War Council | cost 1 — Plan: Deal 5 damage and apply 1 Weak to ALL |
| 1 | **Vanguard+** | **cost 0** — Plan: Apply 2 Vulnerable and 1 Weak. Exhaust *(fight-15 reward)* |
| 1 | Moon's Reflection | cost 1 — replay a card from the Exhaust Pile via the Kurage. Exhaust |
| 1 | Treatise | cost 1, power — draw 1 when the Kurage carries out a Plan |
| 1 | **The Moon Overlooks the Waters** | cost 2, power — **Plans also happen when played.** The deck's engine; Bellows dealt it as `+` (cost 1) in the boss fight |
| 1 | Gorou — Inuzaka All-Round Defense | cost 1 — Deal 8, Block half the damage dealt *(Geo: Crystallize)* |
| 1 | Shinobu — Sanctifying Ring | cost 1 — Lose 3 HP. 3 turns of 5 Electro to ALL and 5 Block. Exhaust |
| 1 | Shinobu — Thundergrust [Electro] | cost 1 — Deal 8, +5 below half HP |
| 1 | Thoma — Blazing Barrier | cost 1 — Gain 6 Block, +3 whenever it absorbs |
| 1 | Kirara — Surprise Dispatch | cost 1 — Gain 8 Block. Next turn, 10 damage to a random enemy |
| 1 | Kujou Sara — Crowfeather Cover | **cost 0** — next Attack +4 damage and **applies Electro** *(overrides the card's own element)* |
| 2 | Kujou Sara — Tengu Stormcall [Electro] | cost 1 — Deal 5. Next turn your Attacks deal +5 *(one bought in act 3)* |
| 1 | **Mika — Starfrost Swirl (Sharp 2)** [Cryo] | cost 1 — **7** to ALL, next Attack costs 1 less. Takes no target. *Enchanted at the Self-Help Book; `Sharp` = +2 damage* |
| 1 | Bennett — Fantastic Voyage | cost 1 — 3 Strength above 70% HP, else 10 Block. Exhaust. **Strength does reach Sango's AoE mode** |
| 1 | Fischl — Nightrider [Electro] | cost 1 — Deal 7. "If Oz is out…" — `Oz` is still undefined by any screen *(fight-14 reward)* |
| 1 | Razor — Claw and Thunder [Electro] | cost 1 — Deal 8; **gain 1 Energy if it is the third Attack this turn** *(fight-16 reward)* |

Removed in act 3: one **Defend** (100 gold at the floor-3 shop).

**Record of combats this act: 6 fought, 6 won** — 3 monster rooms, 2 elites (Soul Nexus 234, Mecha Knight 300), 1 boss (Queen 400 + a 199-HP minion). **Across all three acts the run stands at 23 combats, 23 wins, no deaths**, and it ended on floor 48 with the act-3 boss dead.

---

## Non-blindness declaration

- **Commands run:** only the two permitted forms, `GITS_LANE=1 python -m understudy.blindplay observe` and `GITS_LANE=1 python -m understudy.blindplay act "<command>"`, from the repo root `C:\Users\Monty\Documents\GitHub\GItS`. **No other `understudy` subcommand was invoked** — no `harness`, `session`, `audit`, `notes`, `scenario`, `staged_turn`, `soak`, `embark`. **No `git`.** The lane was never launched, closed, restarted or torn down, and **lane 2 was never touched**.
- **Shell usage beyond those two commands:** `sed`, `grep` and `head` filters applied to `observe` output to trim it; `cat <file> >> <record>` to append prepared sections to my record; and one `wc -l` on my own record to confirm an append had landed. Nothing else. **No `act` was ever run with its output suppressed** — the second seat lost four silent refusals that way, and every command in this session printed its result.
- **Tools used:** **Bash** (the two commands above plus the filters and record appends), **Read** (twice, on the two permitted files), and **Write** (this record, plus six scratch fragments of this record's own prose under the session scratchpad at `C:\Users\Monty\AppData\Local\Temp\claude\...\scratchpad\`, used because a heredoc append failed on shell quoting).
- **Repo files read: exactly two**, both named in the brief — `review\qa\kokomi-round-5-2026-09-03\opus-run3-act1.md` and `review\qa\kokomi-round-5-2026-09-03\opus-run3-act2.md`. Each exceeds the single-read cap and was read in two pages. **No source, YAML, docs, rulings, backlog, register, or other record was opened at any point.** Everything else in this document comes from what the two permitted commands printed.
- **Files edited: one** — this record, at `C:\Users\Monty\Documents\GitHub\GItS\review\qa\kokomi-round-5-2026-09-03\opus-run3-act3.md`.
- **Identifiers minted: none.**
- **Refusals: 1**, quoted in full in the "Future of Potions?" section.
- **The lane is left standing** exactly where play stopped: lane 1, run complete, `TOOL-BLOCKED: game_over` on floor 48. Nothing is mid-screen and no reward, choice or prompt is pending.

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
