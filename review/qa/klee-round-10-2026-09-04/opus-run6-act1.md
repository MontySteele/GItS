# Blind seat — KLEEMOD-KLEE, lane 2, Klee round 10 run 6, act 1

## Identity

- **Model / seat:** Claude Opus 5 (1M), blind TESTER seat, lane 2.
- **Run seed:** not printed on any screen I saw; the bridge never showed one.
- **Character:** Klee (inferred from the printed relic *Pounding Surprise*, the Bomb/Spark/Set off vocabulary, and card titles like *Jumpy Dumpty*, *Dodoco Cover*, *Ka-pow!*). No screen ever printed the character's name.
- **Act:** 1. **Boss named on the map:** Ceremonial Beast (252 HP).
- **Actions accepted:** 213 `act` calls (cap 250). Counted in a scratch file after every batch.
- **Termination reason:** the coordinator's stop condition, not a budget. Act-1 boss killed, its reward screen handled, lane now sitting on the act-2 map (first node offered: `Ancient (path 1)`). I did not enter act 2. Budget left over: 37 actions, well inside the wall clock.
- **HP trajectory:** 62 → 62 (f1) → 62 (f2) → 49 (f3) → 45 (f4) → 35 (f5) → 29 (f6) → 26 (f7) → 21 (f8) → 39 (event heal) → 34 (event fight) → 34 (rest site: Smith, not Rest) → 52 (rest before boss) → **36/62 at the end**.
- **Gold at end:** 144.
- **Potions held at end:** Poison Potion (1 of 3 slots). Spent during the run: Duplicator ×2, Explosive Ampoule, Beetle Juice.
- **Relics at end:** Pounding Surprise; Silver Crucible (spent).
- **Deck at end (21 cards):** Strike ×4, Defend ×4, Ka-pow!, Jumpy Dumpty+, Mine Toss+, Big Badda Boom+, Quick Fuse+, Ammo Scavenging, Dodoco Cover+, Sparks 'n' Splash, Dig In ×3, Diona — Signature Mix, Alice's Recipe.
- **Neow pick:** Silver Crucible ("The first 3 card rewards you see are Upgraded. The first Treasure Chest you open is empty."). Reason: blind, I wanted the strongest early cards and upgraded faces read more of the kit's text back to me; the chest cost looked cheap on a 16-floor act with only one Treasure row. It paid — Mine Toss+, Big Badda Boom+ and Quick Fuse+ all came in upgraded and were the run's three best cards.

---

## Fight 1 — Fuzzy Wurm Crawler 55/55

**Turn 1 (62 HP, 3 energy).** Hand: Defend ×2, Strike ×2, Ka-pow!. Played Ka-pow! → Strike → Strike → Defend. *Rejected:* holding Ka-pow! for its Retain. Ka-pow! prints "Retain. **Set off.** Deal 4 damage" and there were no Bombs anywhere, so its Set off clause was inert and it was simply 4 free damage; retaining a card whose headline clause does nothing is not a decision. The one live choice was the third energy: Defend (5) vs nothing, and with a 4-damage intent printed the Defend was strictly free.

**Turn 2.** Drew Jumpy Dumpty ("Place a Bomb 8. When it goes off, place a Mine 3 on ALL enemies"). Intent read "Empower (Buff)" — no incoming damage. Played Jumpy Dumpty → Strike → Strike. *Rejected:* Defend, because the intent line said the turn had no attack in it. This was the first turn with a real shape to it: spend a card now that does zero damage this turn for a charge that grows 4 a turn.

**Turn 3.** Screen: `Bomb 12`, enemy 27 HP, Strength 7, attacking for 11. Played Ka-pow! (Set off 12, then its own 4) → Strike → Strike. Enemy to 5. *Rejected:* letting the Bomb keep growing another turn — the arithmetic on screen (12 + 4 + 6 + 6 = 28 vs 27 HP) said the fight ended this turn, and it did, one Strike later.

Ended 62/62. Reward: Mine Toss+ over Quick Fuse+/Dig In+/Gorou. Reasoning I could form from the printed text: I had exactly one Bomb source, so a second placer that hits ALL enemies looked worth more than a second detonator with nothing to detonate.

## Fight 2 — Shrinker Beetle 40/40

**Turn 1.** Intent "Strategic (DebuffStrong)". Played Mine Toss+ → Jumpy Dumpty → Strike. *Rejected:* Defends, again on the printed intent.

**Turn 2.** The debuff landed: `Shrink -1 — While Shrinker Beetle is alive, your Attacks deal 30% less damage`. Strike's face changed from "Deal 6 damage" to "Deal 4 damage" and Ka-pow! from 4 to 2 — the card text itself re-rendered, which is the clearest thing the bridge did all run. Meanwhile the Bomb keyword prints "**Not an Attack:** only their Vulnerable and a cap move it", and `Bomb 23` was indeed untouched by Shrink. **This was the best decision of the act:** the enemy had printed a debuff that specifically devalues half my hand and specifically does not touch the other half. Played Ka-pow! (Set off 23, then 2) → Strike → Strike → Defend. *Rejected:* playing around Shrink by holding Ka-pow! and just blocking — rejected because the bombs were immune to the debuff, so the debuff argued for detonating *now*, not later.

Predicted 1 HP left and a `Bomb 3` Mine sitting on it; the screen showed exactly that, and the Mine killed it on its own attack. Ended 62/62.

Rewards: took the Duplicator potion; card pick Big Badda Boom+ ("Set off. Deal 16 damage. Then deal damage equal to what the Bombs dealt") over Careful Now+/Chain Fuse+/Fiery Rain+. That "then deal damage equal to what the Bombs dealt" clause is the loudest number in the kit and I read it as a doubler.

## Fight 3 — Nibbit 45/45

**Turn 1.** Ka-pow! → Strike ×2 → Defend. *Rejected:* two Defends (10 block) instead of one Defend plus a Strike — 5 HP against 6 damage at full health, and I chose the damage. Weak turn: no Bombs in hand, so the whole Bomb layer was absent and the turn was basic-card arithmetic.

**Turn 2.** Big Badda Boom+ with **no Bombs on the target** = "16 damage for 2 energy", plus a Strike. *Rejected:* holding Big Badda Boom+ for a Bomb turn — but I had no placer in hand and the card would be discarded, so the choice was 16-now vs a coin flip on redrawing it. This is the kit's sharpest tension and it recurred all act: the payoff cards and the setup cards are separate draws, and the payoff card played bare is worth maybe a third of itself.

**Turn 3.** Enemy 7 HP behind 5 Block; Big Badda Boom+ (16) killed through it. *Rejected:* the Mine Toss+/Ka-pow line (7 through 5 Block = 2) — not enough, and the screen let me check that before committing.

Reward: Quick Fuse+ (1 Spark, no energy: "Each Bomb on the enemy grows by 6. Set off.") over a second Big Badda Boom/Chain Fuse/Ammo Scavenging. Reasoning: the Spark keyword block said "Start each combat with 1. Pounding Surprise grants more", and Pounding Surprise says "Whenever a Bomb goes off, gain 1 Spark" — so a card that spends 1 Spark to set off a Bomb refunds its own price. That read was correct.

## Fight 4 — Shrinker Beetle 39/39 + Fuzzy Wurm Crawler 55/55

**Turn 1.** Shrink had not landed yet, so my Attacks were still at full value — a printed reason to front-load. Ka-pow! → Big Badda Boom+ → Strike, all onto Shrinker Beetle (26 damage). *Rejected:* splitting damage across both, and *rejected:* blocking the Crawler's 4 — killing the Shrink source fast was worth more than 4 HP.

**Turn 2.** The three-card combo the kit is clearly built around, and the first turn that felt genuinely good: Mine Toss+ (Mine 7 on ALL) → Jumpy Dumpty (Bomb 8) → Quick Fuse+ (grow each by 6 → 13 + 14 = 27, Set off) for **two energy and one Spark**, killing the 13-HP Shrinker outright, refunding the Spark, and leaving Mines on the Crawler. *Rejected:* Ka-pow!/Big Badda Boom+ as the detonator — Quick Fuse+ costs no energy, so using it left a full 3 energy for the placers.

**Turn 3.** `Bomb 29`. Quick Fuse+ again (+12, Set off = 41) → Strike ×2 → Defend. Crawler to 2, killed by its own Mine on its attack. *Rejected:* letting the bombs grow one more turn; the Crawler's Strength 7 made every extra turn cost 11 HP.

**Where the screen and the outcome disagreed:** after turn 2's Set off the Crawler's badge read `Bomb 21 … Bombs here: 2, including 1 Mine`. From the printed faces I could only reconstruct 10 (Mine Toss's Mine 7 plus Jumpy Dumpty's rider Mine 3) or, if Quick Fuse+ grows bombs on every enemy, 16. I could not get to 21 from anything printed. See (c).

## Fight 5 — Twig Slime 11 + Twig Slime 9 + Slithering Strangler 55

**Turn 1.** Ammo Scavenging (Bomb 4) on the 9-HP slime → Quick Fuse+ (grew to 10, Set off) killed it → Strike ×2 killed the 11-HP slime. Both attackers gone on turn 1 for 3 energy and 1 Spark. *Rejected:* putting the Bomb 4 on the Strangler and Striking the slimes — the arithmetic on the printed HPs (10 ≥ 9, 12 ≥ 11) made the split exact, and finding that is the kind of thing the Bomb layer is good for. Also *rejected*, and worth noting: Ammo Scavenging's "Draw 1 card for each of your Bombs that went off this turn" was worth zero here, because the only way to make Bombs go off was to play it first. The card's two halves fight each other.

**Turn 2.** `Constrict 3 — While the Slithering Strangler is alive, at the end of your turn, take 3 damage`. Spent a Duplicator on Jumpy Dumpty (two Bomb 8s) after Mine Toss+, then Ka-pow! (Set off 23) and Defend. *Rejected:* saving the Duplicator for the boss — Constrict prices every extra turn at 3 HP, which is exactly the argument for spending a burst resource in a chip-damage fight.

**Turn 3.** Big Badda Boom+ (16, no bombs left) + Strike = exactly 22 for the kill.

Reward: Dodoco Cover ("Place a Bomb 4. Gain 5 Block") over Witches' Circle/Rapid Fire/Bennett. It is a Defend that also feeds the engine, and my four Defends were the deadest cards in the deck.

## Fight 6 — Nibbit 46 + Nibbit 44

**Turn 1.** Mine Toss+ → Jumpy Dumpty → Ammo Scavenging, all concentrated on Nibbit (1). *Rejected:* spreading the Bombs — one huge stack detonated by Big Badda Boom+ scales quadratically ("damage equal to what the Bombs dealt"), two small stacks do not.

**Turn 2 — the turn with no decision in it.** Hand was Strike/Defend/Defend/Strike/Dodoco Cover with `Bomb 20` on the board and no detonator drawn. Played Dodoco Cover + Defend + Defend for 15 block against a 14-damage intent, dealing zero damage. *Rejected:* Strike instead of a Defend, which is a 4-HP swing and not a decision worth the name. This is the failure mode: the deck's whole output is gated on drawing one of three detonators, and the turn you miss is a blank.

**Turn 3.** Quick Fuse+ on Nibbit (1) (`Bomb 28` +12 = 40) killed it outright at 39 HP. *Rejected:* Big Badda Boom+ on it — 28+16+28 = 72 into a 39-HP body is 33 wasted, and the free-energy card did the job. Choosing *which* detonator to spend on *which* body was a real, satisfying choice.

**Turn 4.** Ka-pow! (Set off 14) → Strike → Defend ×2. **Turn 5.** Big Badda Boom+ finished it through 5 Block.

Reward: Sparks 'n' Splash ("At the end of your turn, deal Pyro damage to a random enemy equal to its largest Bomb") over Run Away!/Explosives Workshop/Shinobu. Read: recurring damage that does *not* consume the Bomb — the card does not say the Bomb goes off, and it turned out not to.

## Fight 7 — Fogmog 74 (summoner) + Eye with Teeth 6

**Turn 1.** Three Strikes, and I **held Ka-pow!** deliberately against a Summon intent, wanting a detonator in hand when the adds arrived. *Rejected:* playing Ka-pow! for 4 free damage. This is the only turn all run where Retain was the decision.

**Turn 2.** Played Sparks 'n' Splash (2) + Dodoco Cover (Bomb 4, 5 block). *Rejected:* the safe line of Dodoco + Defend + Strike. Against a 74-HP body I wanted the recurring engine online even at 3 HP cost. At end of turn Sparks 'n' Splash dealt 4 and the Bomb was still there next turn at 8 — confirming it reads the Bomb without spending it.

**Turn 3 — the best turn of the act.** `Bomb 8`, Fogmog 52, a 15-damage intent, me at 26. Mine Toss+ (Bomb → 15) → Duplicator → Big Badda Boom+ played twice: first copy 15 + 16 + 15 = 46, second copy 16 into the remaining 6. Fogmog died on my own turn; the Eye's badge said `Minion 1 — Minions abandon combat without their leader`, so the fight ended and I took **zero** of the 15. *Rejected:* Mine Toss+ / Jumpy Dumpty / Defend and killing over two turns, which the arithmetic said cost ~15 HP. Every input to that decision was printed on the screen — the Minion keyword, the Bomb total, the doubling clause and the potion text. That is the kit reading well.

Reward: Dig In ("Gain 8 Block" for 1 Spark, no energy), chosen because my Spark had hit **7 unspent** by the end of fight 6 and Dig In is the only sink I had been offered.

## Fight 8 — Assassin Raider 20 + Axe Raider 22 + Crossbow Raider 19

**Turn 1.** Dodoco Cover (Bomb 4, 5 block) on the Assassin → Big Badda Boom+ (4 + 16 + 4 = 24) killed the 10-damage attacker, and the 5 block ate the Axe's 5. *Rejected:* Mine Toss+ instead of Dodoco Cover — same kill, but trading 5 block for a 7-damage Mine on the Axe, and at 26 HP I took the block.

**Turn 2.** 19 incoming against a hand with a 5-block ceiling. Explosive Ampoule (10 to ALL) → Strike ×2 killed the Crossbow Raider exactly, then Jumpy Dumpty banked a Bomb 8. *Rejected:* eating the 14 and saving the potion for the boss — at 21 HP the potion was worth more here.

**Turn 3.** Quick Fuse+ (`Bomb 12` +6 = 18, Set off) plus Ka-pow! finished the Axe Raider.

Reward: a second Dig In. Then Treasure (empty, as Silver Crucible promised), Shop (bought Beetle Juice 102 and Diona — Signature Mix 76 of 207 gold; skipped Card Removal at 75 because a single cut of one Strike out of 18 cards looked worth less than a boss-grade defensive potion).

## Fight 9 — Dense Vegetation event fight: Wriggler 17 + 19 + 21 + 18

Took **Rest** ("Heal 18 HP. Fight some enemies") over "Trudge On" (88 gold, lose 8 HP) at 21/62 — 13 HP with an Elite floor ahead was not a real option.

**Turn 1.** Jumpy Dumpty + Dodoco Cover onto one Wriggler, Defend, **Dig In** (my only Spark) → 18 block against 12 incoming. Took 0.

**Turn 2 — a genuine, and genuinely painful, resource decision surfacing after the fact.** Both Dig In and Quick Fuse+ print "cost 1 Spark", and I had spent the combat's single starting Spark on block. The screen said, in as many words: `Quick Fuse+ … CANNOT BE PLAYED: you have no Spark, and this costs 1`. A `Bomb 20` sat on the board with no way to touch it. I played Diona — Signature Mix (2 Weak to ALL) + Defend ×2. *Rejected:* Strike over a Defend. **The lesson the kit taught me here is real and I did not see it coming: block and detonation are priced in the same currency, and the currency only refills when you detonate.** Spending Spark on Dig In on turn 1 disarmed my own bombs for two turns.

**Turn 3.** Defend + Strike ×2 into the weakest Wriggler; still no Spark, still no detonator. Second blank turn.

**Turn 4.** Drew the whole kit at once. Mine Toss+ (Mine 7 on ALL) → Ka-pow! on the `Bomb 36` body: 43 damage killed it and the Jumpy Dumpty rider seeded Mines on everything → Big Badda Boom+ on the next Wriggler (13 + 16 + 13) killed that one → the third Wriggler's own Mines (`Bomb 20`, 4 Mines) went off on its attack and killed **it** before its hit landed, so I took 0 from a 20-damage board. *Rejected:* Strike-ing the 5-HP Wriggler for a guaranteed kill instead of Big Badda Boom+, which the arithmetic said cost 10 HP.

**Turn 5.** Strike killed the last 5-HP body, deliberately *before* ending the turn so the two `Infection` status cards in hand ("if this is in your Hand, take 3 damage") never resolved.

Reward: a third Dig In. Then Rest site → **Smith**, upgrading Jumpy Dumpty (Bomb 8 → Bomb 11, Mine 3 → Mine 4); then an "Aroma of Chaos" event → Maintain Control, upgrading Dodoco Cover (Bomb 4/5 Block → Bomb 6/7 Block); second shop (44 gold, nothing affordable worth buying — skipped); then Rest to 52/62.

## Fight 10 — BOSS: Ceremonial Beast 252/252

The boss badge printed the whole plan for me: `Plow 150 — The first time Ceremonial Beast's HP reaches 150 or below, it becomes Stunned and loses all its Strength`. That converts the kit's one-big-burst shape into the correct line: hoard, then break 150 in a single hit.

**Turn 1** (Empower intent, no damage). Ammo Scavenging (Bomb 4) + Strike ×2, holding Ka-pow!. *Rejected:* Defend against a Buff intent.

**Turn 2.** Sparks 'n' Splash (2) + Jumpy Dumpty+ (Bomb 11) + Beetle Juice potion (30% less enemy damage, 4 turns). *Rejected:* Diona + Jumpy Dumpty+ + Defend, the ~8-HP-cheaper turn — with 240 HP left, the recurring engine had to come online before the defence did, and Beetle Juice covered exactly the four build-up turns. Took 12 instead of 18.

**Turn 3.** Dig In (8) + Defend (5) = 13 block against a 14 intent; Strike ×2. Sparks 'n' Splash paid 15 at end of turn without spending the Bomb. Took 1.

**Turn 4.** Spark was **0** again — the hoarding line starves the Spark economy exactly as in fight 9, and both Dig Ins printed `CANNOT BE PLAYED`. The fix, which is a nice piece of design once found: Mine Toss+ places a *Mine*, and a Mine "goes off when its enemy attacks you", so it detonates on the boss's own turn — 7 damage **and** a Spark from Pounding Surprise, without touching the hoarded stack. Played Dodoco Cover+ (Bomb 6, 7 block) + Mine Toss+ + Defend, 12 block into 15.

**Turn 5 — the payoff.** `Bomb 53`, boss at 176. Big Badda Boom+ = 53 + 16 + 53 = **122**, boss to 54, straight through Plow 150 → `Intent: Stunned`, Strength wiped, and three Bombs going off handed back 3 Spark. Then Mine Toss+ to re-seed. *Rejected:* Quick Fuse+ (+6 per Bomb then Set off = 71) — Big Badda Boom+'s doubling clause is worth more the bigger the stack, and 122 vs 71 is exactly the difference between clearing Plow in one hit and giving the boss another turn.

**Turn 6.** Jumpy Dumpty+ (stack to 30) → Ka-pow! (Set off 30, +4) → Strike ×2, leaving the boss on **1 HP** by design, because Sparks 'n' Splash was going to resolve at end of turn against a freshly-seeded Mine 4. It did. Boss dead, 36/62, without taking a hit that turn.

Boss reward: 100 gold and Alice's Recipe ("Your Bombs grow twice each turn"), taken over Sugar Rush/Introduction Magic/Clorinde. No relic was offered on the reward screen — only gold and a card — which I note because I expected one from a boss.

---

## The kit, after 10 fights

**(a) Which decisions felt like real choices, and what they traded off.**

1. **Which detonator to spend on which body.** Three set-off cards with genuinely different prices — Ka-pow! (0 energy, Retain, tiny rider), Quick Fuse+ (0 energy, 1 Spark, grows first), Big Badda Boom+ (2 energy, doubles the payload) — and the right answer changed every turn with the size of the stack and the size of the target. Fight 6 turn 3 (Quick Fuse+ to kill a 39-HP body, saving Big Badda Boom+) and boss turn 5 (Big Badda Boom+ over Quick Fuse+, 122 vs 71) were the two best decisions I made, and both were readable off the printed numbers.
2. **Detonate now or let it grow.** Bombs grow 4 a turn and the enemy is also getting stronger; every turn is an explicit "is one more tick worth one more of its attacks". `Constrict 3` in fight 5 and Strength 7 in fight 4 both priced that question in HP, and differently.
3. **Spark: block or boom.** Dig In and Quick Fuse+ both cost 1 Spark, combat starts with exactly 1, and the only refill is detonating. Spending Spark on block *disarms your bombs*. That is a sharp, legible, painful trade and it cost me two blank turns in fight 9. It is the most interesting thing in the kit.
4. **Concentrate or spread.** Because Big Badda Boom+ pays "damage equal to what the Bombs dealt", one stack of 53 is worth far more than two of 26. Against multiple enemies that argues against Mine Toss+'s AoE, which is a nice internal tension.
5. **Shrink in fights 2 and 4.** An enemy debuff that hits Attacks and explicitly cannot touch Bombs ("Not an Attack") re-priced my whole hand mid-fight. Excellent.

**(b) What felt automatic, and what never seemed worth playing.**

- **Strike and Defend.** Eight of my twenty-one cards, and by fight 6 the only question they posed was "5 block or 6 damage", which is not a question. Every turn where I drew a hand of basics was a blank turn.
- **Ka-pow! with no Bomb on the board.** "Retain. Set off. Deal 4 damage" is, three or four times a fight, just "deal 4 damage", and then Retain is meaningless too. It was near-automatic to play.
- **Ammo Scavenging.** "Place a Bomb 4. Draw 1 card for each of your Bombs that went off this turn." The two halves are mutually exclusive in practice: you play it to *create* Bombs, which means you play it *before* the detonation, which means the draw is always 0. I never once drew a card off it. It is the one card in the deck whose second line I would call dead text.
- **Sparks 'n' Splash in multi-enemy fights.** "deal Pyro damage to a **random** enemy equal to its largest Bomb" is fine against a boss and a coin-flip-to-nothing against four Wrigglers, three of which carry no Bomb.
- **Everything conditional on Elemental Reactions.** I triggered **zero** Elemental Reactions in the entire act. Every card I own is Pyro, the only auras on the board were Pyro auras I put there myself, and a Pyro hit on a Pyro aura just refreshes it. Fire Safety, Sizzle, Catalytic Converter and Careful Now's reaction riders were all visibly dead to me, and the huge Elemental Reaction / Melt / Vaporize / Overloaded / Superconduct / Electro-Charged / Frozen glossary reprinted on **every single screen** described a subsystem I never once touched. That glossary is the single largest block of text in the game and it was pure noise for this deck.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **Bomb totals I could not reconstruct.** Fight 4, after a Set off on Shrinker Beetle, Fuzzy Wurm Crawler's badge read `Bomb 21 … Bombs here: 2, including 1 Mine`. From printed faces the Crawler should have held Mine Toss+'s Mine 7 plus Jumpy Dumpty's rider Mine 3 = 10, or 16 if Quick Fuse+ grows bombs on all enemies. 21 is not reachable from anything printed. Similarly fight 9 turn 4: `Bomb 20 … Bombs here: 4, including 4 Mines` on a body that should have held Mine 7 + Mine 4. The badge line tells me the total and the count but never the individual sizes or their provenance, so a wrong total is undetectable and an unexpected one is unexplainable.
2. **Jumpy Dumpty's rider fires more than once.** Its text is "When it goes off, place a Mine 3 on ALL enemies" — singular. After a Set off that popped two Bombs I repeatedly saw **two** fresh Mines appear per enemy, and Mines that were themselves rider-spawned appeared to re-spawn on later detonations. Something propagates that the card face does not describe. It worked in my favour every time, so I am not complaining about the effect — but I could not have predicted the board from the card.
3. **Which of the many Bombs Sparks 'n' Splash and Careful Now mean by "largest".** Since the badge never lists individual Bombs, "equal to its largest Bomb" is a number I can never compute in advance. On boss turn 3 I guessed 15 and was right, but only because I had been tracking each placement by hand across five turns.
4. **Whether Bombs are stopped by enemy Block.** The Bomb keyword says "Not an Attack: only their Vulnerable and a cap move it", which reads like it ignores Block, but I never got a clean read — every time a bombed enemy had Block the total was lethal either way.
5. **"a cap"** in the Bomb keyword. Referenced twice on every screen; never explained, never shown, and I never saw a Bomb stop growing.
6. **Retain and hand size.** Retaining Ka-pow! gave me a six-card hand the next turn rather than a five-card one. Whether that is intended I cannot tell from any printed text.
7. **Duplicator + Big Badda Boom+.** The duplicate copy resolved with the Bombs already spent, so it paid 16 + 0. That is the correct reading of the text and it worked out, but I was guessing.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** Strike. In a deck whose real damage is 40–120 per detonation, "Deal 6 damage" is a card that exists to make my hand worse, and Shrink cut it to 4. Ammo Scavenging is the close runner-up for the reason in (b).
- **Happiest to draw:** Big Badda Boom+. "Then deal damage equal to what the Bombs dealt" is the one line in the kit that turns three turns of quiet setup into a number that visibly breaks the fight — 122 into the boss's Plow threshold in a single card. Quick Fuse+ was the most *satisfying* card (free energy-wise, refunds its own Spark, grows-then-pops), but Big Badda Boom+ was the one I wanted to see.

**(e) Did the first turn of the first fight already present a decision?**

**No.** Hand was Defend, Strike, Ka-pow!, Defend, Strike against a single enemy with a 4-damage intent. Ka-pow! costs 0, so it is free; two Strikes and a Defend spend exactly three energy; there were no Bombs, so Ka-pow!'s Set off and Retain clauses were both inert, and there was nothing to choose between. The kit's actual identity — Bombs, Spark, Set off — did not appear on the board until **turn 2 of fight 1**, when Jumpy Dumpty was drawn, and the first turn that presented a real choice was fight 1 turn 2 (spend a card on a charge that deals zero damage this turn). The first turn that felt like *Klee* rather than like a starter deck was fight 2 turn 2, when Shrink re-priced Attacks and left Bombs alone.

---

## Non-blindness declaration

**Repo files read: none.**

- Game commands used: only `GITS_LANE=2 python -m understudy.blindplay observe` and `GITS_LANE=2 python -m understudy.blindplay act "<command>"`, all via the Bash tool, all prefixed with `cd C:/Users/Monty/Documents/GitHub/GItS &&`. No `harness state`, `scenario`, `staged_turn`, `soak`, or any other understudy subcommand was run.
- Other shell commands, all scratch bookkeeping: `mkdir -p` and `echo N > …/scratchpad/actcount.txt` to keep the running accepted-`act` count (and one `cat` of that file), and `sed -n 'A,Bp'` piped off `observe` output to re-read part of a screen without reprinting the whole thing. Several `act` calls were chained with `&&` and had their JSON echo sent to `/dev/null` to keep the transcript readable; the following `observe` was always shown to me in full or in a named line range, and no game output was hidden from my own view.
- **Caveat from my own tooling, declared:** at the start of fight 8 I read the enemy list through `sed -n '1,50p'` and the window cut off at line 50, so I did not see the third enemy (Crossbow Raider) until after my first two cards. That was my truncation, not the bridge's — the game had printed it.
- Tools used: Bash (as above) and Write (once, for this file). No Read, Grep, Glob, Agent, or web tool was used at any point.
- No refusals were returned by `act` at any point in the run; no `TOOL-BLOCKED` and no `REFUSED: …leak…` line was ever printed. Three cards printed in-hand `CANNOT BE PLAYED:` explanations (`no enemy is holding a Bomb`; `you have no Spark, and this costs 1`; `has unplayable keyword`), which are screen text rather than refusals, and I never attempted those plays.
