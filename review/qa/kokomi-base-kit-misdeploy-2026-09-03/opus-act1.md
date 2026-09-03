# KLEEMOD-KOKOMI — blind seat, lane 1, act 1

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, round 4d, first seat of three.
- **Lane:** 1.
- **Character:** KLEEMOD-KOKOMI.
- **Run seed:** never printed. No screen in this run printed a seed.
- **Act:** 1. The map header printed `At the top of this act: **Vantom**`, so the act-1 boss is **Vantom**.
- **Actions accepted:** **99.** 98 accepted and rendered normally; the 99th (`choose "Gorge"`) took effect but could not be rendered — see the termination note.
- **Actions refused:** **5.** One by the game's own grammar (`choose "Sayu — Muji-Muji Daruma"` on a Muster picker — Companions cannot be eaten); then four by the harness after the run bricked (`act 'proceed'`, `act 'skip'`, `act 'confirm'`, plus two bare `observe` calls, all returning the same `PacketLeak`).
- **Termination reason:** **stop condition (4) — refusals in a row I could not resolve.** After the Gorge pick, every command including plain `observe` fails with `PacketLeak: 1 design-vocabulary leak(s) in the packet: internal-snake-case-id: 'simple_select' in 'simple_select'`. `act` computes an observation on every call, so no verb of any kind can get through. This is a harness block, not a game state — the budget was not spent (99 of 250) and the run was not lost.
- **Where the run stands:** lane 1, **act 1, floor 8**, inside the "Room Full of Cheese" event, on the unrenderable `simple_select` "choose 2 of 8 random Common cards" picker. **The act-1 boss Vantom was never reached**; no Elite and no Treasure node was ever entered. The lane is left standing exactly there.
- **HP trajectory — every reading the screens printed, in order:** 64/80, 64/80, 64/80, 64/80, 64/80 (fight 1, rounds 1–3; won at zero cost) → 64/80, 64/80 (fight 2, rounds 1–2; won at zero cost) → 64/80, **62/80** (fight 3, rounds 1–2) → 62/80, **58/80**, 58/80 (fight 4, rounds 1–3) → 58/80, 58/80 (rest site, before and after Smith). **Final: 58/80.** Total damage taken across four fights: **6**.
- **Gold:** **77.** (Shop printed "You have 137 gold"; I spent 25 + 51 = 76, leaving 61; fight 4 then paid 16.) The 137 itself is unexplained — only 38 gold of rewards was ever printed to me, so ~99 was granted silently. See finding (f)1.
- **Potions (exactly as printed):**
  - **Blessing of the Forge** — "Upgrade all cards in your Hand for the rest of combat."
  - **Potion of Binding** — "Apply 1 Weak and 1 Vulnerable to ALL enemies."
  - Neither was ever used. No screen ever printed a potion-slot count.
- **Relics (exactly as printed):**
  - **Pearl of Wisdom** — "Whenever a card is Exhausted, gain 1 Charge and 2 Burst Energy. Card rewards after a fight offer a fourth Companion choice."
  - **Kaleidoscope** — "Upon pickup, obtain 2 card rewards from other characters."
  - No third relic was ever gained. Notably the "Spoils Map" from an event is **not** a relic (see below).
- **Deck, reconstructed from faces printed in hand and confirmed against the Smith screen (19 cards):**
  - Water's Edge ×4 — cost 1, attack, [Hydro], "Deal 6 damage."
  - Coral Guard ×4 — cost 1, skill, "Gain 5 Block."
  - Sayu — Muji-Muji Daruma ×1 — cost 1, skill, "Gain 4 Block. At the start of your next turn, gain 4 Block."
  - To the Front! ×1 — cost 0, skill, "Muster 1."
  - Gorou — Inuzaka All-Round Defense ×1 — cost 0, attack, "Deal 6 damage. Exhaust."
  - Tactical Retreat ×1 — cost 0, skill, "Draw 1 card. Discard 1 random card."
  - *(the six lines above are the 12-card starting deck)*
  - Claw ×1 — cost 0, attack, "Deal 3 damage. Increase the damage of ALL Claw cards by 2 this combat." *(Neow / Kaleidoscope)*
  - Freminet — Pressurized Floe: Backstroke ×1 — cost 2, attack, "Deal 10 damage. Gain 6 Block." *(fight 1 reward)*
  - Raiden Shogun — Musou no Hitotachi ×1 — cost 3, attack, [Electro], "Deal 40 damage. Apply 2 Vulnerable. Exhaust." *(fight 2 reward; **upgraded at the floor-7 Smith — the screen never printed what the upgrade changed**)*
  - Communion of Tides ×1 — cost 1, skill, "Exhaust 1 card from your hand. Draw 2 cards." *(fight 3 reward)*
  - Tideturn ×1 — cost 1, attack, [Hydro], "Deal 5 damage. Draw 1 card." *(shop, 25 gold)*
  - Signal Arrow ×1 — cost 1, attack, [Hydro], "Deal 5 damage. Muster 1." *(shop, 51 gold)*
  - Spoils Map ×1 — cost 0, quest, "Unplayable. Marks a site of 600 extra Gold in the next Act." *(event; **does not appear on the Smith screen**, which lists only 18)*
  - Plus **up to 2 unknown Common cards** if the Gorge pick resolved server-side before the render failed — I could never see that screen, so I cannot say.
- **Cards seen only as temporary Muster recruits (never in the deck):** Sayu — Naptime (0, "Gain 3 Block. Draw 1 card."), Shinobu — Thundergrust (0 shown / 1 printed, [Electro], "Deal 7 damage."), Kujou Sara — Crowfeather Cover (0, "Your next Attack deals 4 more damage."), Itto — Superlative Superstrength (1 shown / 2 printed, "Deal 14 damage. Gain 6 Block."), and a second Raiden Shogun (2 shown / 3 printed).
- **Fights fought:** 4, all won. Fuzzy Wurm Crawler (57 HP), Shrinker Beetle (38), Nibbit (43), and Shrinker Beetle (39) + Fuzzy Wurm Crawler (56) together.

---

## Screen 1 — Neow

Three options printed:

- **Kaleidoscope** — "Obtain 2 card rewards from other characters."
- **Phial Holster** — "Gain 1 potion slot and procure 2 random Potions."
- **Dowsing Rod** — "Add 1 Dowsing to your Deck."

**Predicted:** two card rewards is the largest raw value; I can decline either if the cards are bad.
**Took:** Kaleidoscope.
**What happened:** it resolved as two consecutive card-reward screens.

**Reward 1 offered:**
- **Expect a Fight** — cost 3, skill. "Gain 15 Block. Gains 5 additional Block for each Strength you have."
- **Claw** — cost 0, attack. "Deal 3 damage. Increase the damage of ALL Claw cards by 2 this combat."
- **Casting Call** — cost 1, power. "Your Salon has room for 1 more Salon Member(s)."

**Took Claw.** Reasoning from the screen alone: a 0-cost card is nearly free to include; "Expect a Fight" costs my whole turn's energy; "Casting Call" refers to a "Salon" that no screen of mine has ever mentioned, so I read it as belonging to another character.

**Reward 2 offered:**
- **Snap** — cost 1, attack. "Osty deals 7 damage. Add Retain to a card in your Hand."
- **Rapturous Applause** — cost 1, power. "Fanfare +8. Your Attacks deal 1 more damage per 10 Fanfare."
- **Accelerant** — cost 1, power. "Poison is triggered 1 additional time."

**Declined all three.** Every one of them keys off a resource I have no evidence of owning: "Osty" (a named creature never on any of my screens), "Fanfare", and "Poison". `Rapturous Applause` is self-defeating at pickup by its own text — "+8 Fanfare" and "1 more damage per 10 Fanfare" is 0 extra damage.

**Bridge behaviour worth recording:** on the card-selection screen, `skip` did **not** consume the reward. After `skip` the reward list still printed "Add a card to your deck.", and re-opening it printed the identical three cards. I skipped twice and the row persisted both times; only `proceed` from the reward list left it behind. So `skip` backs out of the picker rather than declining the reward.

---

## Fight 1 — Fuzzy Wurm Crawler (57 HP), floor 1, Monster (path 1)

Opening state: HP 64/80, Energy 3/3, 8 in draw pile, 0 discarded, 0 exhausted, Charge 0.

The permanent buff, quoted in full:

> **Bake Kurage 1 (buff)** — At the end of your turn, the jellyfish answers the last card you played this turn. After an Attack: it deals 4 damage and applies Hydro to a random enemy. After a Skill: it grants 5 Block. After a Power: it banks 1 Charge. If you played no card at all, it does nothing. It stays on the field for the whole fight.

A dedicated screen section, "The Bake-Kurage's memory", printed every turn:

> - The Bake-Kurage is on the field for the whole fight. Nothing summons it and nothing removes it.
> - Charge: 0
> - The memory is empty. Nothing is queued and nothing fires next turn.
> - At the end of this turn the jellyfish will do nothing, because you have played no card this turn.

### Round 1

Hand: Coral Guard (1, 5 Block); Sayu — Muji-Muji Daruma (1, 4 Block + 4 Block at start of next turn); Water's Edge ×2 (1, 6 damage, [Hydro]); Claw (0, 3 damage).
Enemy: `Intent: Aggressive (Attack) — the number on its icon is 4 — This enemy intends to Attack for 4 damage.`

**Predicted:** incoming is only 4, so Sayu (4 now + 4 next turn) exactly covers it and beats Coral Guard's 5 on total value; then all three attacks with an *Attack* last, so the jellyfish answers with 4 damage rather than 5 Block. Predicted damage 6+6+3+4 = 19, ending HP untouched.

**Played:** Sayu — Muji-Muji Daruma → Water's Edge → Water's Edge → Claw → end turn.

**Happened, exactly:** 57 → 51 after the first Water's Edge (6, checks). Hydro Aura 2 appeared on the enemy:

> Hydro Aura 2 (aura) — Hydro clings to this enemy for 2 more turns. A hit of a different element consumes the aura and triggers an Elemental Reaction; a Hydro hit refreshes its duration.

End of round the enemy stood at **38/57** = 51 − 6 − 3 − 4. **Predicted 19 damage, got exactly 19.** HP stayed 64/80: 4 Block ate the 4-damage attack exactly.

Note: the second Water's Edge on an enemy that already had Hydro Aura printed no visible effect from its "Applies Hydro" clause — the aura read `Hydro Aura 2` before my turn's attacks and `Hydro Aura 1` on the next screen, i.e. it ticked down rather than refreshing, despite the aura's own text saying "a Hydro hit refreshes its duration". I cannot tell from the screens whether the refresh happened and then the turn tick undid it.

### Round 2

Enemy `Intent: Empower (Buff)` — no damage incoming, so I spent nothing on defence.
Drew two new faces:

> - **To the Front!** — cost 0, skill. "Muster 1."
>   *Muster* — "Muster N: transform N cards in your hand into random Inazuma Companion cards. Each costs 1 less this combat and Exhausts. Kit cards and Companions you already hold are never chosen. A Muster creates a memory of the card it ate, and the recruit creates a second when it burns. A memory replays for Charge equal to 3x its Cost."
> - **Gorou — Inuzaka All-Round Defense** — cost 0, attack. "Deal 6 damage. Exhaust."

**Gorou** (38 → 32, exactly 6). Its Exhaust immediately produced three separate visible changes:
- `Charge: 1`
- `Kokomi Burst: 2/20` — a meter that had not appeared on any earlier screen at all
- a memory entry: `Next to fire: **Gorou — Inuzaka All-Round Defense** — costs nothing — it fires at the start of your next turn.`

**This is the sharpest text mismatch of the fight.** Pearl of Wisdom says "gain 1 Charge and **2 Burst Energy**". Energy did not move (still 3/3). What moved was a meter printed as **Kokomi Burst: 2/20**. "Burst Energy" and "Kokomi Burst" are not the same words, and on first read I priced my turn expecting 2 extra energy.

**To the Front! → Muster 1.** The picker printed:

> # Choose a card to Transform.
> - Coral Guard (1) / Water's Edge / Coral Guard (2)

I fed it a Coral Guard (no damage was incoming, so its Block was worthless). It became **Sayu — Naptime** — cost 0, skill, "Gain 3 Block. Draw 1 card." And the memory gained a second entry:

> 2. **Coral Guard** — 3 Charge, cost 1 x 3 — aims at random
> - Charge runs out at #2 (**Coral Guard**): that one and everything behind it are held until the bank catches up.

**Sayu — Naptime** played for 3 Block and drew Tactical Retreat, and it **Exhausted** (exhausted count 1 → 2, Charge 1 → 2, Burst 2/20 → 4/20) — even though the card's own printed text says only "Gain 3 Block. Draw 1 card." with no Exhaust line. Gorou prints "Exhaust."; Sayu — Naptime does not, and exhausts anyway.

The memory then read:

> 1. **Coral Guard** — 3 Charge, cost 1 x 3 — aims at random
> 2. **Sayu — Naptime** — free — aims at random
> - Charge runs out at #1 (**Coral Guard**): that one and everything behind it are held until the bank catches up.

**This is the head-blocking rule, printed plainly:** a *free* memory sitting behind an unpayable one never fires. My Muster paid for itself in a body (Sayu — Naptime) but jammed my own replay queue with a 3-Charge Coral Guard I could not afford, and that jam stranded a free replay behind it.

I declined Tactical Retreat this turn on the arithmetic: playing it would have meant a 1-in-3 chance of randomly discarding my only Water's Edge and losing 10 damage (6 + the jellyfish's 4), against an upside of roughly one extra card of unknown type. I played Coral Guard and Water's Edge and ended on the Attack.

### Round 3

Enemy at **16/57** — 32 − 6 (Gorou memory firing at the start of my turn) − 6 (Water's Edge) − 4 (jellyfish). **Predicted 16, got exactly 16.** The Gorou memory fired for free and left the queue, confirming memories are one-shot FIFO.

Enemy now:
> Intent: Aggressive (Attack) — the number on its icon is 11
> Strength 7 (buff) — Increases attack damage by 7.

So `Empower` was Strength 7, and the printed intent number 11 = base 4 + 7. That checks.

**Refusal (1 of 1 this run):** I tried `choose "Sayu — Muji-Muji Daruma"` on the Muster picker and got:

> nothing here is called 'Sayu — Muji-Muji Daruma'. What is on the screen: Coral Guard, Tactical Retreat, Water's Edge

That is the Muster text's "Companions you already hold are never chosen" applying to the card being **eaten**, not (as I had read it) to the Companion being **created**. Sayu — Muji-Muji Daruma is a Companion, so it cannot be fed to a Muster.

I then fed it **Tactical Retreat (cost 0)**, having worked out from the printed rule "A memory replays for Charge equal to 3x its Cost" that a 0-cost meal makes a **free** memory and a 1-cost meal makes a 3-Charge one. Confirmed on screen: `3. **Tactical Retreat** — free — aims at random`.

The recruit was:

> **Shinobu — Thundergrust** [Electro] — cost 0, attack. "Deal 7 damage."
> The cost printed on this card is 1; it is showing 0 here.
> *Reaction preview: Electro-Charged* — This card supplies Hydro or Electro while an enemy has the other aura. The reacted enemy gains a 4-damage decaying damage-over-time effect.

The enemy was carrying Hydro Aura, so this was a live reaction.

**Predicted:** Coral Guard (5) + Sayu — Muji-Muji Daruma (4) = 9 Block as insurance against the 11-hit, then Shinobu (7) → 9 HP, then Water's Edge (6) → 3 HP, then the jellyfish's 4 as the answer to an Attack = lethal at exactly 16. Total energy 1+1+0+1 = 3, exactly my pool.

**Happened:** Shinobu took it 16 → **9** (exactly 7). The Hydro aura vanished and the reaction landed as:

> Poison 4 (debuff) — At the start of its turn, loses 4 HP, then reduce Poison by 1.

**Second text mismatch:** the card's glossary calls the reaction "**Electro-Charged**" and describes "a 4-damage decaying damage-over-time effect". The enemy panel names the resulting debuff "**Poison**". Nothing on any screen connects those two words. Also, Shinobu's "Applies Electro" did **not** leave an Electro aura behind — the Hydro aura was consumed by the reaction and no aura replaced it.

Water's Edge then took it to 3 and the fight ended on the jellyfish's answer, before the enemy's 11-damage attack ever resolved. **The jellyfish fires at the end of my turn, ahead of the enemy's action** — that ordering is what made the kill exact.

**Fight 1 result: won on round 3, HP 64/80 → 64/80. Zero damage taken.**

### Fight 1 reward

`11 Gold` and a card screen with **four** options — confirming Pearl of Wisdom's "Card rewards after a fight offer a fourth Companion choice":

- **Ebb Tide** — cost 0, skill. "Discard a random card. Exhaust 1 card from your hand."
- **Pearl Barrage** [Hydro] — cost 1, attack. "Exhaust 1 card from your hand. Deal 5 damage, plus 3 per cost of the card you just Exhausted."
- **Wheel the Ranks** — cost 0, skill. "Discard 1 card. Draw 2 cards. Sly: Gain 4 Block."
- **Freminet — Pressurized Floe: Backstroke** — cost 2, attack. "Deal 10 damage. Gain 6 Block."

**Took Freminet.** The reasoning, from screens only: my turns were capping around 19 damage and my whole damage suite is 6s. Freminet is 10 damage + 6 Block for 2 energy with no conditions. Pearl Barrage is more damage per energy (8 for 1, exhausting a 1-cost) and feeds Charge/Burst, but I had *just watched* a 3-Charge memory jam my queue and strand a free replay behind it, and Pearl Barrage manufactures exactly that jam every time it eats a 1-cost card. I bought reliability over an engine I had seen misfire.

Also note `Wheel the Ranks` prints "**Sly**: Gain 4 Block" with no glossary line for "Sly" anywhere on the screen. I had no way to price that clause.

---

## Event — "The Legends Were True" (floor 2, Unknown)

> - **Nab the Map** — Receive the Spoils Map.
> - **Slowly Find an Exit** — Lose 8 HP. Procure 1 random Potion.

**Took "Nab the Map"** — a free thing beats a random potion bought with 8 HP.

**What the screen did not say, and I had to work out later:** no relic appeared. The next battle screen still listed exactly two relics (Pearl of Wisdom, Kaleidoscope), but my draw pile + hand had grown by one card. Three floors later I finally drew it:

> **Spoils Map** — cost 0, quest. "Unplayable. Marks a site of 600 extra Gold in the next Act."
> *Unplayable* — Unplayable cards cannot be played.
> CANNOT BE PLAYED: has unplayable keyword

So the "free" option was a **dead card jammed into my deck for the whole of act 1**, paying out only in an act this seat does not play. Nothing on the event screen said "card", "unplayable", or "next Act". It is also invisible to the Smith screen (see below), so it never appears in the one place that lists the deck.

---

## Fight 2 — Shrinker Beetle (38 HP), floor 3

Opened HP 64/80, 10 in draw pile (deck now 15). `Intent: Strategic (DebuffStrong)`.

**Predicted:** no damage incoming, so spend nothing on Block. Freminet 10 + Water's Edge 6 + Claw 3 = 19 for exactly 3 energy, Attack last so the jellyfish adds 4. Predicted 38 − 23 = 15.
**Got exactly 15.**

The debuff landed as:

> Shrink -1 (debuff) — While Shrinker Beetle is alive, your Attacks deal 30% less damage.

**Good behaviour worth naming:** the card faces in hand *rewrote themselves* to match. Gorou printed "Deal 4 damage" (not 6) and Water's Edge printed "Deal 4 damage" (not 6) while Shrink was up. That is the most helpful thing any screen did all act — the debuff was priced for me instead of left as arithmetic homework.

**But the rewritten face then disagreed with the outcome.** Round 2 I played Kujou Sara — Crowfeather Cover ("Your next Attack deals 4 more damage") and then Gorou, whose face read "Deal 4 damage". I predicted 4 + 4 = **8**. The enemy went 15 → 8, i.e. **7**. The engine computes (6 base + 4 bonus) × 0.7 = 7; the face computes 6 × 0.7 = 4 and then invites you to add 4 to it. Two different roundings of the same debuff, and only one of them is real. This is the clearest place in the act where a printed number and the result disagreed.

Round 2 also produced the one refusal of the run (quoted in Fight 1) and the second Muster recruit:

> **Kujou Sara — Crowfeather Cover** — cost 0, skill. "Your next Attack deals 4 more damage."

Fight ended round 2 with Water's Edge; the enemy died before its 7-damage swing landed. **HP 64/80 → 64/80, zero damage taken.**

**Rewards:** 13 Gold; **Blessing of the Forge** (the reward row printed the name only — the text "Upgrade all cards in your Hand for the rest of combat" did not appear until it showed up in a Potions panel mid-fight); and a card from four:

- Salvage the Line (1, skill) — "Draw 1 card. Choose a card from your Exhaust pile; put it on top of your draw pile. It gains Exhaust. Gain 2 Charge. Gain 4 Block. Exhaust."
- Massed Volley [Hydro] (1, attack) — "Deal 5 damage to ALL enemies. Sly: Deal 4 damage to a random enemy."
- Raise the Sashimono (0, skill) — "Give a Skill in your hand Sly this turn. Draw 1 card."
- **Raiden Shogun — Musou no Hitotachi** [Electro] (3, attack) — "Deal 40 damage. Apply 2 Vulnerable. Exhaust."

**Took Raiden Shogun.** 40 damage for 3 energy against a deck whose entire damage suite was 6s.

This screen is also where the **Charge** glossary finally printed its rules, four floors after Charge first appeared on my screen:

> *Charge* — Charge: a bank that grows by 1 whenever one of your cards Exhausts. It has no maximum. Cards that read it are stronger the more you hold; a card printing a Charge price spends it, and cannot be played below that price.

---

## Fight 3 — Nibbit (43 HP), floor 4

Enemy swung for 12.

**Predicted:** end on a *Skill* so the jellyfish gives 5 Block instead of 4 damage — Coral Guard 5 + jellyfish 5 = 10 Block against the 12, taking 2, while still dealing 21 (Water's Edge 6, Water's Edge 6, Claw 3, Gorou 6). I accepted 4 less damage to save 5 HP specifically because Gorou's Exhaust seeds a **free** memory that replays 6 damage at the start of next turn for nothing.

**Got exactly that.** 43 − 21 = 22; the Gorou memory fired at the start of round 2 for 6 → **16/43**; HP 64 → **62** (12 − 10 Block). Round 2, Freminet 10 + Water's Edge 6 = exactly 16. Dead.

**Rewards:** 14 Gold, **Potion of Binding** ("Apply 1 Weak and 1 Vulnerable to ALL enemies" — again, text not shown at the reward screen), and I took **Communion of Tides** (1, skill: "Exhaust 1 card from your hand. Draw 2 cards.") over Massed Volley, Salt Line and Charlotte — Charlotte — First-Person Shutter's face is word-for-word identical to the Sayu — Muji-Muji Daruma I already had.

---

## Shop (floor 5)

> You have 137 gold.

**This is where a silent grant showed up.** The only gold any screen had ever printed to me was 11 + 13 + 14 = 38. The shop says 137. The missing 99 was never printed anywhere — no starting-gold line, and no running gold total on any map, battle or reward screen. 99 + 38 = 137 exactly, so I infer a starting purse of 99 that no screen ever stated.

Shelves (quoted): Signal Arrow 51; Tideturn 25; Ebb Tide 51; Raise the Sashimono 74; Vigil of the Deep 144; Sayu — Naptime 75; Gorou — Forward Unto Victory 77; White Star 291; Oddly Smooth Stone 192; Bread 224; Colorless Potion 48; Skill Potion 49; Cure All 77; Card Removal 75.

**Bought Tideturn (25)** and **Signal Arrow (51)**, leaving 61. Reasoning: both are 1-cost attacks that replace themselves (Tideturn draws, Signal Arrow Musters), and Muster had already handed me a 0-cost 7-damage attack and a free +4 damage. I passed on Card Removal (75) because two efficient cards beat deleting one mediocre one, and held 61 for the second shop the map shows further up.

---

## Fight 4 — Shrinker Beetle (39 HP) + Fuzzy Wurm Crawler (56 HP), floor 6 — first multi-enemy fight

Opening hand was Coral Guard ×3, Raiden Shogun, and the unplayable Spoils Map — 15 Block and a brick.

**Predicted:** this is the ideal Raiden turn precisely *because* the rest of the hand is worthless — Raiden costs 3, my whole pool, so it can never combine with anything and there is no better turn coming. 40 damage kills the 39 HP Beetle outright, deleting the Shrink debuff **before** it is ever applied. Predicted: Beetle dead, jellyfish 4 into the Crawler (56 → 52), I eat the Crawler's 4.

**Got exactly that:** Beetle gone, Crawler 52/56, HP 62 → **58**.

**And the sharpest structural finding of the act showed up here.** Raiden's Exhaust queued this:

> - Next to fire: **Raiden Shogun — Musou no Hitotachi** — costs 9 Charge — you cannot pay it, so NOTHING in the memory fires next turn.
>   1. **Raiden Shogun — Musou no Hitotachi** — 9 Charge, cost 3 x 3 — aims at random
> - Charge runs out at #1: that one and everything behind it are held until the bank catches up.

My Charge was 1 and my Charge income is 1 per Exhaust. **Playing my best card permanently switched the Bake-Kurage's memory off for the rest of the fight** — a 9-Charge head that nothing behind it can get past. By the end of the fight the queue read Raiden (9) / Communion of Tides (3) / Water's Edge (3), all frozen.

There is a perverse consequence I then *exploited*: once the queue is bricked, the memory cost of feeding Muster an expensive card is **zero**, because nothing was going to fire anyway. So the correct play inverted between fight 1 ("always feed Muster a 0-cost card, so its memory is free") and fight 4 ("feed it whatever you like"). That is real strategic texture, but it exists only because the system had already failed.

Round 2: Crawler was Empowering, so three Water's Edge = 18 + jellyfish 4 = 22. **Predicted 52 − 22 = 30; got exactly 30.**

Round 3, the Muster chain paid out enormously:
- To the Front! ate Communion of Tides → **Itto — Superlative Superstrength** — cost 1 (printed 2), "Deal 14 damage. Gain 6 Block."
- Signal Arrow (5 damage) then force-Mustered my last Water's Edge — the only legal meal, since both other cards in hand were Companions — into a **second Raiden Shogun**, cost 2 (printed 3), 40 damage.

A 1-cost Water's Edge worth 6 damage became a 2-cost card worth 40 in a single mandatory transformation. Raiden killed the 25 HP Crawler outright. **HP 58/80; 4 damage taken all fight.**

**Rewards:** 16 Gold. Card options were Send the Runner, A Moment Alone, Mercy of the Currents ("Whenever a card is Exhausted, gain 3 Block"), Sucrose — Wind Spirit Creation ("Swirl an enemy's aura. Draw 1 card."). **Skipped all four** — my deck was already 19 cards including a brick, and I wanted density on the bombs. I priced Mercy of the Currents off my own logs: my fights had been running 1–2 Exhausts each, so 3 Block per Exhaust was ~6 Block a fight, not worth a slot.

---

## Rest site (floor 7)

> HP 58/80
> - **Rest** — Heal for 30% of your Max HP (24).
> - **Smith** — Upgrade a card in your Deck.

**Took Smith.** The reasoning is checkable off the map: the floor immediately before the boss reads `RestSite, RestSite, RestSite` — every node on it is a rest — so a heal is guaranteed later and an upgrade is not.

**The Smith screen is the only full deck listing in the game**, and it printed 18 cards: Water's Edge ×4, Coral Guard ×4, Gorou, Sayu — Muji-Muji Daruma, To the Front!, Tactical Retreat, Claw, Freminet, Raiden Shogun, Communion of Tides, Tideturn, Signal Arrow. This is what let me finally settle the starting deck at 12: **Water's Edge ×4, Coral Guard ×4, Gorou, Sayu — Muji-Muji Daruma, To the Front!, Tactical Retreat** — resolving the two faces I had never drawn.

**Spoils Map is absent from that list.** The one screen that enumerates my deck omits the one card I cannot play and would most want accounted for. Deck is 19; the Smith says 18.

**Upgraded Raiden Shogun.** The screen then returned to "this rest site has nothing left to offer" and **never printed what the upgrade changed** — no new face, no before/after. I do not know what my upgraded Raiden does and will only find out if I draw it.

---

## Event — "Room Full of Cheese" (floor 8, Unknown) — THE RUN STOPS HERE

> # Room Full of Cheese
> - **Gorge** — Choose 2 of 8 random Common cards to add to your Deck.
> - **Search** — Lose 14 HP. Obtain the Chosen Cheese.

**Predicted / chose Gorge.** My stated reasoning at the time: this event repeats the shape of "The Legends Were True", where the option that named a thing without describing it ("Receive the Spoils Map") turned out to be an unplayable brick welded into my deck for the whole act. 14 HP at 58/80, with two Elites and a boss still ahead, is a real price for a second undescribed noun. Gorge is the only option whose cost (deck dilution) and benefit (2 cards I pick from 8 I can read first) are both visible before committing.

**What happened instead — a hard tool block.** `act 'choose "Gorge"'` returned:

```
REFUSED: 1 design-vocabulary leak(s) in the packet: internal-snake-case-id: 'simple_select' in 'simple_select'
```

The choice **did land** — before it, `observe` rendered the event fine; after it, `observe` fails with the identical error. So the game advanced to the "choose 2 of 8" picker, and the bridge's own blindness guard refuses to render that screen because the screen's type name, `simple_select`, is itself an internal snake_case identifier that the guard is built to strip.

Every subsequent command fails the same way, including plain `observe`:

```
File "understudy\blindplay_grammar.py", line 641, in act
    obs = observation(state)
File "understudy\blindplay_observe.py", line 324, in observation
    qa_packet.assert_blind(obs, allow={st, obs["screen"]})
understudy.qa_packet.PacketLeak: 1 design-vocabulary leak(s) in the packet:
    internal-snake-case-id: 'simple_select' in 'simple_select'
```

I tried, in order: `observe`, `act 'proceed'`, `act 'skip'`, `act 'confirm'` — five refusals in a row, all the same `PacketLeak`, none resolvable with the two commands I am permitted to run. `act` computes the observation on every call, so no verb of any kind can get through; the lane cannot be observed or advanced from this seat.

**This is a blocking defect in the seat harness, not in the game.** The game is sitting on a perfectly ordinary card-selection screen. The blindness guard rejects the packet because it checks the screen-type token against a snake_case rule and the token for this screen type happens to be snake_case, so the guard flags its own screen name as a design-vocabulary leak. The allow-set on line 324 is `allow={st, obs["screen"]}` — the screen id is passed in as allowed, yet the string `'simple_select'` is still reported as leaking "in 'simple_select'", i.e. the leak is found in the field that is supposed to be exempt.

**Consequence for this round:** the act-1 boss **Vantom** was never reached, and seats 2 and 3 cannot be chained off this lane until the block is cleared. Any event offering "choose N of M cards" (this one, and the shop's Colorless Potion / Skill Potion, which promise "Choose 1 of 3 random ... cards") is a live tripwire that will end a seat's run on contact.

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

**The jellyfish's last-card rule was a genuine dilemma every single turn.** The buff reads "the jellyfish answers the last card you played this turn. After an Attack: it deals 4 damage... After a Skill: it grants 5 Block." That converts card *ordering* — normally free — into a priced decision, and the price is legible: 4 damage against 5 Block. In Fight 3 against Nibbit I deliberately ended on Coral Guard rather than an attack, taking 21 damage instead of 25 so that 5 Block + Coral Guard's 5 would eat 10 of a 12-damage swing. That cost me 4 damage and saved me 5 HP, and I could compute both halves before committing. This is the best-designed thing on the character.

**What to feed a Muster was a real choice with a rule you have to derive.** The printed rule is "A memory replays for Charge equal to 3x its Cost". Nothing tells you what follows: feeding a 0-cost card makes a **free** memory, feeding a 1-cost card makes a **3-Charge** one, and my Charge income is 1 per Exhaust. In Fight 1 I worked that out mid-turn and fed Tactical Retreat (cost 0) instead of Coral Guard (cost 1), and the screen confirmed it: `3. **Tactical Retreat** — free`.

**When to spend Raiden Shogun.** The answer I reached — play it on the turn your hand is *worst*, because at cost 3 it consumes the entire energy pool and can never combine with anything — is a genuinely satisfying inversion. Fight 4's opening hand of three Coral Guards plus an unplayable card was the ideal Raiden turn, and 40 damage exactly deleted a 39 HP Shrinker Beetle before its debuff ever landed.

**Smith versus Rest at floor 7.** Real, and decidable off the map: the floor before the boss is `RestSite, RestSite, RestSite`, so healing is guaranteed later and the upgrade is not.

### (b) What felt automatic, and what never seemed worth playing

**Coral Guard was almost always automatic.** "Cost 1, Gain 5 Block" with four copies in a twelve-card starting deck. On a turn with damage incoming you play it; on a turn without, it is Muster food. It never once posed a question.

**Water's Edge is automatic in a subtler and worse way.** Four copies of "cost 1, deal 6 damage" means my default turn for the first three fights was literally "play Water's Edge until the energy runs out". Its [Hydro] clause almost never mattered, because a second Water's Edge into an enemy that already has a Hydro aura does nothing visible — the aura text says a same-element hit "refreshes its duration", but the aura ticked 2 → 1 across the turn I hit it twice with Hydro.

**Tactical Retreat is the card I never wanted to play** — see (d).

**Claw was near-dead.** "Deal 3 damage. Increase the damage of ALL Claw cards by 2 this combat." I had exactly one Claw, so the scaling clause could only ever pay off if I drew and replayed the same card in one combat, which happened zero times in four fights. It was a 0-cost 3-damage filler with a rider that was structurally unreachable in my deck.

### (c) What I could not understand, or that contradicted its own printed text

1. **"Sly" is never defined anywhere.** It appears on at least five cards I was shown — `Wheel the Ranks` ("Sly: Gain 4 Block"), `Massed Volley` ("Sly: Deal 4 damage"), `Salt Line` ("Sly: Exhaust 1 card"), `A Moment Alone` ("Sly: Draw 1 card"), and `Raise the Sashimono`, whose *entire text* is "Give a Skill in your hand Sly this turn" — and no screen ever printed a glossary line for it, though these same screens print glossary lines for Block, Exhaust, Retain, Poison, Strength, Charge and Unplayable. `Raise the Sashimono` was on sale in the shop for **74 gold** and I could not price it at all.

2. **"Burst Energy" vs "Kokomi Burst".** Pearl of Wisdom promises "gain 1 Charge and **2 Burst Energy**". When it fired, Energy stayed at 3/3 and a previously-unseen meter appeared reading **Kokomi Burst: 2/20**. I initially mispriced a turn expecting 2 extra energy.

3. **Kokomi Burst does nothing I ever saw.** It is the character's name-bearing meter and its screen line openly says so: "the game's data feed carries this meter's amount and its maximum, **and no rule for how it is spent**". Across four fights it never exceeded **4/20**. I never learned what filling it does, and nothing on any screen suggests how a 20 could be reached — at 2 per Exhaust that is ten Exhausts in one combat, against the 1–2 per fight I actually managed.

4. **The Shrink arithmetic contradicts the card face.** Covered in Fight 2: the face read "Deal 4 damage", Kujou Sara added "+4 more damage", and the result was **7**, because the 30% reduction is applied to (6+4) rather than to the 4 the card printed.

5. **"Electro-Charged" is printed as "Poison".** Shinobu's own preview says the reaction "gains a 4-damage decaying damage-over-time effect" under the heading *Reaction preview: Electro-Charged*; what appeared on the enemy was `Poison 4 (debuff)`. Two names, no screen linking them. Separately, Shinobu's "Applies Electro" left **no** Electro aura — the Hydro aura was consumed and nothing replaced it.

6. **The Smith omits part of the deck.** It listed 18 cards; my deck was 19. **Spoils Map does not appear**, so the only screen in the game that enumerates your deck cannot be used to audit your deck.

7. **The upgrade result is never shown.** I upgraded Raiden Shogun and the screen went straight to "this rest site has nothing left to offer". No new face, no before/after, no way to learn what I bought.

8. **`skip` on a card-reward picker does not decline the reward** — it backs out to the reward list, which still offers the same three cards. Declining actually requires `proceed`. On the Smith screen the same word is explicitly documented as an undo ("You may say `skip` to undo this pick"), so one verb means two different things on two adjacent screens.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted: Tactical Retreat** — "cost 0, Draw 1 card. Discard 1 random card." In Fight 1 round 2 I worked out that playing it with Water's Edge, Coral Guard and one unknown in hand carried a 1-in-3 chance of randomly discarding the Water's Edge I needed, costing 10 damage (6 plus the jellyfish's 4) for the upside of seeing one extra card. I declined it, and I declined it every other time it appeared. The one thing I ever did with it was **feed it to a Muster**, where its 0 cost made it the *best* card in my hand — the only value it ever produced was being eaten.

The true zero, though, is **Spoils Map**: "Unplayable", in my deck for the entire act, paying out only in an act I do not play.

**Happiest to draw: Raiden Shogun — Musou no Hitotachi.** "Cost 3, Deal 40 damage. Apply 2 Vulnerable. Exhaust." Against a deck whose damage was otherwise 6s, drawing it meant a fight ended. It killed a 39 HP Shrinker Beetle outright *and* deleted its Shrink debuff pre-emptively, and a Muster-made copy killed a 25 HP Crawler. Honourable mention to **Itto — Superlative Superstrength** (14 damage + 6 Block for cost 1) which Muster produced out of a Communion of Tides.

### (e) Did the first turn of the first fight already present a decision?

**Yes, and a properly priced one.** The opening hand was Coral Guard (5 Block), Sayu — Muji-Muji Daruma (4 Block now + 4 next turn), Water's Edge ×2, Claw, against `Attack for 4`. Two decisions were live immediately:

- **Which blocker.** The incoming hit was exactly 4, so Coral Guard's 5 was one wasted point while Sayu's 4 covered it exactly and banked another 4 for next turn. Sayu is strictly better *only because* the intent number is 4; at 5 incoming the answer flips.
- **Card order**, because of the jellyfish. I put an Attack last for 4 damage instead of 5 Block, since Sayu had already covered the whole hit.

I predicted 19 damage and dealt exactly 19, and took 0. A first turn where the enemy's printed intent number changes which of two block cards is correct is a genuine opening decision, not a tutorial.

### (f) Anything a screen granted or changed without saying so

1. **~99 starting gold, never printed.** The first gold figure any screen ever showed me was the shop's "You have 137 gold", after exactly 38 gold of printed rewards. No map, battle or reward screen carries a running gold total.
2. **"Receive the Spoils Map" silently added an unplayable card** to my deck. No relic appeared; the deck grew by one; I learned what it was three floors later by drawing it.
3. **Companions Exhaust without printing "Exhaust".** Gorou prints "Exhaust."; **Sayu — Naptime**, **Shinobu — Thundergrust**, **Kujou Sara** and **Itto** do not, and Sayu — Naptime demonstrably exhausted (exhaust pile 1 → 2, Charge 1 → 2, Burst 2 → 4).
4. **Exhausting silently queues a memory.** Nothing on Gorou's face, or Pearl of Wisdom's, says that Exhausting a card puts it in the Bake-Kurage's replay queue. It is a large hidden upside (a free 6-damage Gorou replay) and a large hidden downside (Raiden's unpayable 9-Charge head).
5. **The Smith never printed what my upgrade did.**
6. **Potion text is withheld at the reward screen.** "Blessing of the Forge" and "Potion of Binding" were named at the reward and only described later in a battle's Potions panel — so I chose to pick them up without being able to read them.
7. **Muster's exclusion rule is stated backwards from how it behaves.** "Kit cards and Companions you already hold are never chosen" reads as a constraint on the Companion being *created*; it is in fact a constraint on the card being *eaten*, which I only learned from a refusal.

---

## Findings, ranked by sharpness

**1. A `simple_select` screen hard-bricks the seat harness, and it ended this run.** `act 'choose "Gorge"'` at "Room Full of Cheese" advanced the game to a "choose 2 of 8" picker, after which **every** command — including bare `observe` — dies with `PacketLeak: 1 design-vocabulary leak(s) in the packet: internal-snake-case-id: 'simple_select' in 'simple_select'`, raised at `blindplay_observe.py:324` via `qa_packet.assert_blind(obs, allow={st, obs["screen"]})`. The guard flags the screen's own type token as a leak even though that token is passed into the allow-set. The lane cannot be observed or advanced. This is the single highest-priority finding: it cost the round its boss fight, and it will fire again on the shop's Colorless Potion and Skill Potion, which both promise "Choose 1 of 3 random ... cards".

**2. Playing your best card permanently disables the character's signature system.** Raiden Shogun (cost 3) Exhausts, and Exhausting queues a memory priced at 3× cost, so it queues a **9 Charge** head. Charge income is **1 per Exhaust**. The screen states the consequence itself: "Next to fire: Raiden Shogun — costs 9 Charge — **you cannot pay it, so NOTHING in the memory fires next turn**", and "that one and everything behind it are held". By the end of Fight 4 the queue was Raiden (9) / Communion of Tides (3) / Water's Edge (3), permanently frozen. The best card in the deck switches off the Bake-Kurage's memory for the rest of the combat, and the queue is strictly FIFO so nothing cheap behind it can ever jump it.

**3. The same head-blocking rule silently punishes ordinary play, not just bombs.** In Fight 1 — with no bombs involved — Mustering a single 1-cost Coral Guard queued a 3-Charge memory against a bank of 2, which stranded a **free** memory (`2. Sayu — Naptime — free`) behind it that never fired. A player who does the natural thing (feed Muster the block card they do not need) is punished, and the rule that tells them so is only derivable from "A memory replays for Charge equal to 3x its Cost" plus watching it fail.

**4. Shrink's printed card face and Shrink's actual arithmetic disagree.** With `Shrink -1` up, Gorou's face read "Deal 4 damage" (6 × 0.7 → 4). With Kujou Sara's "+4 more damage" active, the enemy went **15 → 8**, i.e. **7** = (6 + 4) × 0.7. The face rounds one way and the engine another, so a player adding the printed +4 to the printed 4 predicts 8 and gets 7. I made exactly that error on-screen. The face-rewriting itself is excellent and should be kept — it is the rounding that is wrong.

**5. "Sly" is a keyword with no definition anywhere, on at least five cards, one of them sold for 74 gold.** `Wheel the Ranks`, `Massed Volley`, `Salt Line`, `A Moment Alone`, and `Raise the Sashimono` (whose whole text is "Give a Skill in your hand Sly this turn. Draw 1 card."). Every other keyword I met — Block, Exhaust, Retain, Poison, Strength, Charge, Unplayable, Muster, Applies Hydro — printed a glossary line. Sly never did. I could not price a shop item or a card reward because of it.

**6. Kokomi Burst is inert.** The character's own named meter reached **4/20** across four fights and its screen line admits there is "no rule for how it is spent". At +2 per Exhaust it needs ten Exhausts in a single combat; my fights produced 1–2. I finished the act never having seen it do anything.

**7. Kaleidoscope's second card reward was entirely unplayable for this character.** All three offers keyed off resources KLEEMOD-KOKOMI has no access to: `Snap` ("**Osty** deals 7 damage" — a creature that never appears on any of my screens), `Rapturous Applause` ("**Fanfare** +8..."), `Accelerant` ("**Poison** is triggered 1 additional time"). `Rapturous Applause` is dead on arrival by its own arithmetic: +8 Fanfare with "1 more damage per 10 Fanfare" is +0 damage. The first reward was two-thirds the same (`Casting Call` — "Your **Salon** has room for 1 more Salon Member(s)"). Of six cards offered by a Neow option, one was playable.

**8. Muster is the strongest thing in the kit by a wide margin, and it is mostly upside-random.** A 0-cost `To the Front!` turned a Coral Guard into Shinobu (7 damage, 0 cost) and a Communion of Tides into **Itto** (14 damage + 6 Block at cost 1, printed 2). A 51-gold `Signal Arrow` force-fed my last Water's Edge and returned a **second Raiden Shogun** (40 damage at cost 2, printed 3). Turning a 1-cost 6-damage card into a 40-damage one, in a mandatory transformation, is the largest single value swing I saw. I cannot tell from four fights whether that is intended, but it dwarfs every printed number in the starting deck.

**9. Two events named a reward they refused to describe, and the one I took was a brick.** "Receive the Spoils Map" gave an **Unplayable** card that occupied a deck slot for the whole act to pay out in the next one; "Obtain the Chosen Cheese" asked 14 HP for another undescribed noun. Because the first one burned me, I steered away from the second — and that avoidance is what walked me into finding 1.

**10. Where I could not tell.** I never reached an Elite, a Treasure node, or the boss **Vantom**, so I have nothing on how the kit scales against a real HP pool or a multi-attack pattern; every fight I played ended in 2–3 rounds with the enemy dying before its big swing. I never saw Kokomi Burst fire, never learned what my Raiden upgrade did, never learned what "Sly", "Swirl" or "the Chosen Cheese" mean, and could not determine whether Muster's recruits persist after combat or whether the eaten card returns to the deck.

---

## Non-blindness declaration

- **Commands run outside the two allowed ones: none.** Every game command was `GITS_LANE=1 python -m understudy.blindplay observe` or `GITS_LANE=1 python -m understudy.blindplay act "<command>"`, run from the repo root. I ran no `harness`, `session`, `audit`, `notes`, `scenario`, `staged_turn`, `soak` or `embark`, no git, and I never launched, closed, restarted or tore down the game, and never touched lane 2.
- **Repo files read: none.** I read no source, YAML, docs, rulings or backlog. The only file paths I touched were my own record at `C:\Users\Monty\Documents\GitHub\GItS\review\qa\kokomi-round-4d-2026-09-03\opus-act1.md` and two scratch fragments under `C:\Users\Monty\AppData\Local\Temp\claude\...\scratchpad\` used only to assemble that record.
  - The one qualification I must declare: the blocked screen returned a **Python traceback** rather than a rendered screen, and that traceback printed source file names, line numbers and one line of code (`qa_packet.assert_blind(obs, allow={st, obs["screen"]})`) from `understudy/blindplay.py`, `understudy/blindplay_grammar.py`, `understudy/blindplay_observe.py` and `understudy/qa_packet.py`. I did not open any of those files; the tool put that text on my screen unbidden. I have quoted it in finding 1 because it is the evidence for the defect. It concerns the harness, not the game's design, so my blindness to the kit is intact.
- **Other tools used:** Bash (to run the two allowed commands, and `cat`/`sed`/`wc` to trim output and append my record) and Write (record and scratch fragments only). No other file was edited, and no identifier was minted.
- **Lane left standing:** yes. Lane 1 is left exactly where it stopped — act 1, floor 8, inside the "Room Full of Cheese" Gorge picker, on the unrenderable `simple_select` screen. I issued no teardown of any kind.

---

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
