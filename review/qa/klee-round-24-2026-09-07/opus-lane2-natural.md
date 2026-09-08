# Klee round 24 — blind seat, lane 2, natural draft

## Identity

- **Model and seat:** Opus, blind tester seat, lane 2 (`GITS_LANE=2 python -m understudy.blindplay`).
- **Run seed:** not printed on any screen I was shown. The bridge never printed a seed, so I cannot report one.
- **Character:** Klee (the screens never printed a character name either; the kit is the Bomb/Spark/Pyro one and the Neow relic **Pounding Surprise** and the Hexerei glossary both name Klee, so I am naming her from those lines).
- **Ascension:** never printed on any screen I saw. I cannot report it.
- **Act:** act 1. Reached floor 11. **Boss named at the top of the act: Waterfall Giant** (printed on the floor-1 map).
- **Actions accepted:** 120 of 120.
- **Termination reason:** the **action budget**. My 120th accepted act was the `end turn` that closed round 3 of fight 6; I was mid-fight, round 4, when I stopped. No refusal streak, no stall, and the wall clock was nowhere near 5400 s.
- **HP trajectory:** 62 (start) → 54 → 52 → 50 → 46 → 40 → 36 → 32 → 24 → **14** (after the elite) → 32 (Rest) → 34 (Blood Vial at combat start) → 29 → **15 at the stop**.
- **Gold:** 215.
- **Potions held:** none. I started with 4 slots (Phial Holster) and spent all four — Powdered Demise and Skill Potion on the elite's turn 1, Dexterity Potion and Energy Potion on the elite's lethal turn.
- **Relics at the end:** Pounding Surprise, Phial Holster, Blood Vial, Red Mask.
- **Deck at the end** (I could not run a deck command, so this is the ten I opened with plus every card I saw myself add): 4× Strike, 4× Defend, Jumpy Dumpty, Ka-pow!; added — Rapid Fire (fight 1 reward), Razor — Claw and Thunder (fight 2 reward), Razor — Lightning Fang (fight 3 reward), Big Badda Boom (fight 4 reward), Grounded (shop, 72g), Stoke the Fuse (shop, 37g), Lisa — Violet Arc (elite reward), Rip and Tear (Trash Heap "random forgotten card"). 18 cards. Nothing upgraded, nothing removed.

**Neow pick: Phial Holster** — "Gain 1 potion slot and procure 2 random Potions." I took it because I had never seen this kit and two unknown potions plus a spare slot is the cheapest insurance a blind seat can buy; the other two both charged a real price (New Leaf gambles a card away, Silken Tress takes *all* my gold to Glam a card reward I would only keep one card from).

**What I was offered and what I took, reward by reward** (natural draft — nothing was pre-added):

| After | Offered | Took |
|---|---|---|
| Fight 1 | Dig In / **Rapid Fire** / Witches' Circle / Freminet — Shattering Pressure | Rapid Fire |
| Fight 2 | Pocket Match / Careful Arrangement / Perfect Timing / **Razor — Claw and Thunder** | Razor — Claw and Thunder |
| Fight 3 | Witches' Circle / Flash Point / Coven Errand / **Razor — Lightning Fang** | Razor — Lightning Fang |
| Fight 4 | **Big Badda Boom** / Pop! / Grounded / Amber — Explosive Puppet | Big Badda Boom |
| Shop | (7 cards, 3 relics, 3 potions, removal 75g) | **Grounded** 72g, **Stoke the Fuse** 37g |
| Elite | Chain Fuse / Chained Reactions / Sugar Rush / **Lisa — Violet Arc** | Lisa — Violet Arc |
| Trash Heap | (random) | Rip and Tear |

---

## Fight 1 — Sludge Spinner (37 HP)

Opening hand: Jumpy Dumpty (Innate), Ka-pow!, Strike ×2, Defend. Spark 1, Energy 3.

**Turn 1.** Jumpy Dumpty on A (Bomb 8), then both Strikes (6+6). **Rejected:** Ka-pow! immediately — it prints *Set off*, and setting off a Bomb 8 the turn it lands throws away the "grows 4 a turn" line the Bomb keyword prints. Ka-pow! is Retain, so waiting costs nothing. That is a real turn-1 decision and the kit hands it to you on the first hand: the bomb is a bank account, and the detonator retains, so the only question is when to cash it. Also rejected: Defend, because 8 incoming out of 62 is not worth a card. Took 8 and Weak 1.

**Turn 2.** Bomb had grown 8→12. Ka-pow! (0) set it off: 25 → 10, so **15**, which is Bomb 12 landing in full plus Ka-pow!'s own 3. Ka-pow!'s printed damage had dropped 4→3 under Weak, but **the Bomb's 12 was not reduced** — exactly what the Bomb keyword promises ("Not an Attack... only Vulnerable and a cap on the enemy's HP loss move it"), and the screen and the outcome agreed to the point. Spark 1→2 on the detonation (Pounding Surprise). Then Strike, Strike (4 each under Weak) → 2 HP, and one Defend. **Rejected:** a third attack — the Mine 3 that Jumpy Dumpty's rider had dropped kills a 2 HP body before its own hit, so the last energy was better spent on Block than on a kill I was already owed.

**Outcome:** it died on its own turn to the Mine. I never saw a round 3. That is the plan-payoff case, not a dead turn: the decision was made on turn 1 (bank the bomb) and turn 2 (stop attacking).

---

## Fight 2 — Toadpole (1) 24 HP, Toadpole (2) 25 HP

**Turn 1.** Jumpy Dumpty on **A** (the one Empowering, not the one attacking), Strike A, Defend. **Rejected:** bombing B, the attacker. The reason was the rider — Jumpy Dumpty's Bomb drops **Mine 3 on ALL enemies** when it goes off, so the bomb's host only decides where the big number lands; the small numbers spray either way. I put it on the buffer so the buff would not get to mature.

**Turn 2.** A now had Bomb 12 **and Thorns 2** ("Every card hit is one, a Skill's too"). Ka-pow! on A: 18 → 2, mines on both. Then I stopped hitting A: **rejected** Strike-to-finish, because A was at 2 with a Mine 3 on it and the Mine keyword says it goes off before its enemy's hit — so A was going to kill itself for free, and every card I pointed at it would have cost me 2 Thorns. Two Strikes into B instead, plus a Defend. **Also rejected:** Rapid Fire, whose four random hits would have been split onto a body already dying, and would have paid Thorns four times.

That was the sharpest decision of the run and Thorns is why: the kit's *stop attacking* button (Mine) and the enemy's *punish attacking* button (Thorns) pointed the same way.

**Turn 3.** A had duly died to its Mine. B was at 13 with **Mine 7** (grown 3→7) and had inherited **Thorns 2** — the "moves to a survivor" clause, visible on the board. Ka-pow! (11) then Strike (6) killed it, paying Thorns twice instead of the three times three Strikes would have cost.

---

## Fight 3 — Seapunk (44 HP)

**Turn 1.** Jumpy Dumpty, Strike, Defend. **Rejected:** double Strike; 11 incoming at 46 HP was worth 5 Block, and the Bomb grows whether or not I spend the turn attacking — which is the single nicest thing about this kit's clock. Blocking does not cost tempo.

**Turn 2.** This is where the round's real question opened. Bomb 12 on a bare Seapunk, and I now held Razor — Claw and Thunder, printed `[Electro]`, in an otherwise all-Pyro deck.

Sequence: **Ka-pow! first** (set off Bomb 12 + its own 4 = 16, 38 → 22) *specifically so that its `Applies Pyro` line would leave a Pyro Aura 2 on the body*, then Razor into that aura. Razor is printed for 8; it took the Seapunk 22 → 8, i.e. **14**, and dropped **Weak 1** on it (its intent visibly fell 2×4 → 1×4). Spark went 2 → 4. **Rejected:** Rapid Fire, which is 21 damage for 2 energy on that board but leaves no energy for Razor and, being Pyro, could not react with anything.

Then Rapid Fire (2) finished it. **A refusal here, and it is a finding:** `play "Rapid Fire" on "A"` was refused with *"'Rapid Fire' is played on you, not on an enemy, so it takes no `on \"A\"`."* The card's own face reads "4 times: Set off a random enemy and deal 3 damage to it" — so the refusal is correct and the message named the working form, but the card reads as targeted and is not. That is the only refusal of the run, and one refusal is not a stop.

The decision here was made **on the turn**, in the ordering: Pyro before Electro. Nothing about the two cards' faces tells you to sequence them that way — you have to read `Applies Pyro` on one and `Applies Electro` on the other and put them together yourself. That is a good puzzle and I enjoyed solving it.

---

## Fight 4 — Gremlin Merc (47 HP), which split into Sneaky Gremlin (12) and Fat Gremlin (15)

The Merc printed **Surprise 1 — "Something is off about this creature..."**, **Thievery 20** and a 7×2 intent.

**Turn 1.** Jumpy Dumpty, Defend, Defend. **Rejected:** any attack at all. 14 incoming at 40 HP against a 47 HP body is a race I could not win on turn 1, and (again) the Bomb grows for free while I block. 10 Block ate 14; I took 4.

**Turn 2.** The best turn of the run, and it was a genuine sequencing puzzle. Razor's face has a second clause: *"If this is the third Attack you played this turn, gain 1 Energy."* So:

1. Ka-pow! (0 energy, attack #1) — Bomb 12 + 4 = 16, and the Pyro aura goes on.
2. Strike (attack #2) — 6. **Chosen over playing Razor here**, purely to make Razor third.
3. Razor (attack #3) — reacted off the Pyro aura for 14 and Weak, **and refunded 1 energy**, which the screen confirmed (Energy read 2 after spending 1+1 out of 3).
4. Rapid Fire with the refunded energy — 15 more, and lethal.

Without the ordering that is a 3-energy turn; with it, it is a 4-energy turn that kills. The alternative I rejected — Ka-pow!, Razor, Strike, in the "obvious" order — deals the same card damage and does not refund, and would have left the Merc alive at ~7 HP with a 14-damage swing coming at my 36 HP.

**Then the screen surprised me, honestly.** The Merc died and *split* into two fresh gremlins — that is what "Surprise 1 — Something is off about this creature..." meant, and I could not have read it off that line. I do not call it a defect: it is a base-game body, the line is deliberately coy, and the intent screen updated immediately. But it is the one moment in six fights where the printed text did not let me plan.

**Turn 3.** Fat Gremlin carried **Heist 20 — "When killed, returns all the stolen Gold"** and intended to **Escape**, and it wore a Pyro Aura 2 that Rapid Fire had left on it. Razor into that aura: Overloaded killed the Fat Gremlin (14 on a 12 HP body) *and* the reaction's "6 damage to ALL enemies" clipped the Sneaky Gremlin 12 → 6 in the same beat. One card, one kill, one softened survivor, +2 Spark. **Rejected:** hitting the Sneaky Gremlin, which was the one actually attacking me — the Fat one was leaving with my gold, and the aura was on the Fat one. Chasing the aura over chasing the attacker is a decision the reaction rules create and I liked making it.

Then Jumpy Dumpty on the survivor + Defend. **Turn 4:** the survivor sat at 6 HP under a Bomb 12, and I killed it with a plain Strike, deliberately wasting the bomb — **rejected** Rapid Fire, because spending a 2-cost payoff to overkill a 6 HP body is worse than spending a Strike. A bomb you throw away is a legitimate outcome and the kit does not punish you for it.

**Screen vs outcome, small:** Heist says the gold "returns" when the Fat Gremlin is killed, but the 20 gold arrived as a line in the post-fight reward pile (`20 Gold (stolen back)`) that I had to claim, not as an immediate refund. The gold came back, so nothing was lost — but the card's wording and the delivery mechanism do not match.

---

## Fight 5 — ELITE: Terror Eel (140 HP)

Entered at **32/62**, which was my own fault for the shop spend, and it printed a 16-damage intent and **Shriek 70 — "The first time Terror Eel's HP reaches 70 or below, it becomes Stunned."**

**Turn 1.** Powdered Demise on it (9 HP a turn, free, and 140 HP is a lot of turns), Jumpy Dumpty (Bomb 8), Grounded, then Skill Potion.

The Skill Potion offered Fireworks Show (2 Sparks), **Dig In** (1 Spark), Sugar Rush (2 Sparks) — *all three priced in Sparks*, and I had exactly 1 Spark. Dig In's own face pre-empted the trap I was about to walk into: *"Its 1 Spark is a price, not an Energy cost: an effect that makes a card free to play, or cuts its cost to 0, covers Energy only, and the 1 Spark is still spent."* So the potion's "free to play" covered the Energy and I still paid the Spark. **That sentence is on the card, and I read it before I acted, and it was right.** 8 Block for a resource I was about to regenerate anyway.

Then Razor (8) — **chosen not for the damage but to leave an Electro Aura 2 on the Eel for next turn's bomb to react against.** Ka-pow! and Big Badda Boom are Pyro; the aura had to go on first, and Razor's Hexerei line refunded the Spark I had just spent on Dig In. Took 16 through 8 Block → 24 HP.

**Turn 2.** Bomb 16 (8→12 grown, and the screen said 12). **Big Badda Boom**: *"Set off. Deal 12 damage. Then deal damage equal to what the Bombs dealt."* Against Bomb 12 on an Electro aura that is Bomb 12 + Overloaded 6 + card 12 + echo 12 = **42, and the board went 123 → 81 exactly.** I predicted the number before I played it and the screen matched it to the point. That is the moment the kit clicked.

Then Ka-pow! (free, set off the fresh Mine 3, +4) and Strike → **68 HP, crossing Shriek's 70**, and the intent flipped to Stunned *immediately*, in my own turn. I took **zero** damage that round. **Rejected:** Defend, and it was close — I was at 24 with 6 incoming — but reaching 70 *this* turn instead of next was worth more than 5 Block, and the Demise tick would have got me there anyway a turn later at the cost of a full enemy turn.

**Turn 3.** Free turn (stunned), no attack incoming, and — a real cost of the previous turn — **no Bomb on the field, so Grounded printed "No Bomb on the field this turn, so nothing was paid"** and Stoke the Fuse in my hand was a blank card. Razor — Lightning Fang (*"For 2 turns, your Attacks apply Electro and deal 3 additional damage"*) then Rapid Fire: 4 hits at 3+3, the first Overloading off the Pyro aura for 6 → **59 → 29, exactly the 30 I predicted.**

**Turn 4.** Eel at 20 with a **24-damage** intent, me at 24 HP. Two Strikes at 9 (Lightning Fang's +3) is 18 — one short of lethal. But the Eel's own **Demise 9** would finish anything at 9 or below at the end of its turn, so the win condition was *survive one hit*, not *kill*. Dexterity Potion (+2 Dex) then Energy Potion (+2 Energy), Strike, Strike (→ 2 HP), Defend, Defend at 7 each = **14 Block**. Took 10, ended at 14, and Demise killed it. **Rejected:** hoarding the potions — a potion you die holding is worth nothing, and the arithmetic said HP 5 without them and HP 14 with.

This fight is the whole kit working: bank a bomb, dress the body in the wrong element, detonate into it, and let a status line (Shriek, Demise) do the last of the work.

---

## Fight 6 — Corpse Slug ×3 (27 / 25 / 26), stopped mid-fight on the budget

All three printed **Ravenous 4 — "When an enemy dies, Corpse Slug immediately eats it, becoming Stunned and gaining 4 Strength."** Red Mask had put Weak 1 on all three at the bell.

**Turn 1.** Jumpy Dumpty on A, Razor on A (Electro aura), Defend. **Rejected:** spreading damage — with Ravenous on the board, killing anything early feeds a survivor 4 Strength, so the plan was to build one big bomb and cash it when the AoE would be worth the feeding.

**Turn 2.** Drew no detonator — Lightning Fang, 2 Defend, 2 Strike, and a Bomb 12 sitting on A that I could not touch. **This is the kit's real failure mode and it is worth writing down plainly:** the Bomb is the whole engine, and when the detonator is in the draw pile the Bomb is furniture. I played Lightning Fang + two 9-damage Strikes into A (19 → 1) and took 14 to the face. **Rejected:** two Defends under Frail (3 Block each — a quarter of my hand for 6 Block) which is the sort of hand where blocking is simply not on offer.

**Turn 3, and the best single card of the run.** A sat at **1 HP under a Bomb 16 with an Electro aura**. **Ka-pow!, at 0 energy**, did all of this at once: set off Bomb 16, which killed A; Overloaded off the Electro aura for 6 to ALL; dropped Mine 3 on both survivors; and, because A died, **both** remaining slugs ate it — going to Strength 4 **and Stunned**. One free card removed a body, chunked two, and bought a turn with nothing incoming.

**Where the screen and the outcome disagree:** Ravenous reads *"When an enemy dies, Corpse Slug immediately eats **it**"* — one corpse. Two slugs each ate the same corpse and each gained 4 Strength. Both readings are defensible from that sentence, but I did not expect it, and by the time I stopped, the survivor was at **Strength 8** off two feedings from what had been one body. If a slug eating a slug is meant to be a resource the enemies compete over, the current behaviour hands it to all of them at once.

Then Rip and Tear (the Trash Heap card: 10 damage to a random enemy twice, 13 each under Lightning Fang) took them to 9 and 10, and a Strike killed B — feeding C again.

**Stopped here on 120/120.** Final board: Corpse Slug (3) at 10/26, **Strength 8**, and carrying **Mine 14**, both mines having moved onto it as the transfer rule promises. Me at 15/62.

One printed line on that last screen I could not fully parse: *"Mine 14 (buff) — Set off here deals 14 Pyro damage, **in 2 hits for 2 Sparks**."* Nothing else all run had priced a *set-off* in Sparks, and there was no card in my hand that would have charged me. I take it to mean "if you set these off with a Spark-priced card, that costs 2 Sparks (one per charge)", but the sentence reads as though the Mine itself has a Spark price, and I never got to test it.

---

## The kit, after 5 completed fights and one in progress

**(a) Which decisions felt like real choices, and where each was made.**

- *When to detonate* — **on the turn**, every single fight. The Bomb grows 4 a turn and Ka-pow! is Retain, so the kit asks "cash now or bank a turn?" and the answer genuinely moves. Fight 1's turn 1 was already this question.
- *Which element goes on first* — **on the turn**, fights 3, 4 and 5. Pyro then Electro, or Electro then Pyro, are different turns, and nothing on either card tells you; you deduce it from `Applies Pyro`/`Applies Electro` and the Elemental Reaction paragraph.
- *Whether to attack a dying body at all* — **on the turn**, fight 2. Mine kills it for free; Thorns charges you for touching it. Two keywords pulling opposite ways is the cleanest decision the kit produced.
- *Razor's third-attack ordering* — **on the turn**, fight 4. A one-energy refund that is invisible unless you count attacks. Genuinely the most satisfying single turn.
- *Chase the aura or chase the attacker* — **on the turn**, fight 4 turn 3.
- *The draft that shaped everything* — Razor — Claw and Thunder, taken at fight 2, is the decision that made fights 3, 4, 5 and 6 interesting, because it is the only card in a mono-Pyro deck that supplies a second element. Fight 5's whole shape was that pick paying off. **Big Badda Boom + a banked Bomb is the same story:** a 42-damage turn that was decided one reward screen earlier.
- *Shop* — Grounded + Stoke the Fuse over Bag of Marbles. Ironically the two I bought were the two weakest cards I played (see (b)).

**(b) What felt automatic, and what never seemed worth playing.**

- **Defend is a non-decision.** Five of my Defends were "the number on the intent is bigger than 5, play a Defend"; under Frail it printed 3 and was not worth the card slot.
- **Strike is filler.** It became interesting only under Lightning Fang (+3) and only because Lightning Fang was in play.
- **Stoke the Fuse never once did anything.** It came up twice; both times there was no Bomb on the field and the card was blank. Its floor is "dead card", its ceiling needs a bomb *and* spare Sparks *and* a detonator in the same hand — three conditions, and I never met all three in 120 acts. The 37 gold was wasted.
- **Grounded paid twice in three turns of the elite and then stopped**, because the way you win with this kit is to set off your bombs, and setting them off is exactly what turns Grounded off. A Power that punishes you for using your engine is a strange piece of design and I noticed it as a wrong feeling before I could say why.
- **Jumpy Dumpty is automatic but not boring** — it is Innate, it is always turn 1, and there is no decision beyond target. That is fine for an opener.

**(c) What I could not understand, or that seemed to contradict its own printed text.**

- **Ravenous fed two slugs off one corpse** (fight 6). The card says "eats **it**". Strength 8 off a single death.
- **Heist's gold "returns" as a reward-pile line**, not a return (fight 4).
- **"Mine 14 ... in 2 hits for 2 Sparks"** — a Spark price attached to a *Mine's* set-off, with no card on my side that would charge it. I could not resolve what pays.
- **Rapid Fire reads targeted and is not** — it prints "Set off a random enemy", is refused with `on "A"`, and the refusal message was clear and correct, but the face invites the mistake.
- The **Elemental Reaction** glossary paragraph is very long and warns at length about an aura being consumed and re-applied inside one beat so the reaction "looks as though it did not happen". I hit exactly that in fight 5 (Big Badda Boom left a Pyro Aura 2 after Overloading off Electro) and the paragraph is the only reason I did not file it as a bug. Long, but it earned its length.
- Everything else I read did what it said, to the point, including two damage numbers (42 and 30) I computed in advance from the printed faces and matched exactly.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** Stoke the Fuse. Twice drawn, twice blank, never played. (Defend is worse on average but at least it does something.)
- **Happiest to draw:** **Ka-pow!** — 0 energy, Retain, and it is the key to the whole engine. In fight 6 turn 3 a single free Ka-pow! killed a body, dealt 6 to everything, mined both survivors and stunned them both. Big Badda Boom is the bigger number but Ka-pow! is the card that makes the bombs mean anything, and its Retain is what makes "bank it a turn" safe.

**(e) Did the first turn of the first fight already present a decision?**

**Yes.** Opening hand was Jumpy Dumpty, Ka-pow!, Strike, Strike, Defend against a 37 HP body telegraphing 8. Jumpy Dumpty is forced (Innate, obvious), but the very next question is real: Ka-pow! costs 0 and would set off the Bomb 8 for 12 total right now, or it Retains and the Bomb becomes 12 and it sets off for 15 next turn. I chose to bank, and the fight ended a turn earlier than it would have otherwise because the Mine rider then killed the body on its own turn. That is a decision, on turn 1, with a consequence I could trace — from cards whose faces gave me everything I needed to make it.

---

## The word on the Companion cards

**Hexerei.** As I understood it from the screens: **Hexerei is a word printed on some Companion cards, and playing one pays Klee in Spark.** The glossary line is *"Hexerei — A Companion card whose face prints the word. Playing one gives Klee 1 Spark, up to 3 a play."* The rider printed on the Razor cards themselves breaks the number down: *"Sparks from your Companion — Playing a Hexerei card makes 1 Spark, 1 more if it triggered an Elemental Reaction and 1 more if it is upgraded."* So: **Klee is paid, not charged** — it is income, not a cost; the amount is **1 base, +1 if that play triggered an Elemental Reaction, +1 if the card is upgraded**; and the cap of **3 caps the payout of a single play**, not a total. Nothing caps the Spark pool itself — the Spark keyword says "with no cap".

**Where I read it.** First on the **fight-1 card-reward screen** (floor 2), in the glossary under Witches' Circle, alongside the definition of **Companion** — *"A card titled with a character's name, a dash, then its own. Card rewards after a fight offer a fourth, Companion, choice."* The three-part breakdown I only got later, printed as a rider **on Razor — Claw and Thunder's own face** in hand.

**Two things I learned that the word does not say.** (1) **Not every Companion is Hexerei.** Freminet — Shattering Pressure, Amber — Explosive Puppet and Lisa — Violet Arc are all Companions by the naming rule and **none of them prints Hexerei**; Razor — Claw and Thunder and Razor — Lightning Fang do. So Hexerei is a subset, and the fourth reward slot is not a Spark guarantee. (2) The payout is not flat — I watched it be 1 and I watched it be 2, and the difference was whether the play reacted.

**The turn it changed what I did — fight 4, turn 2, against the Gremlin Merc (47 HP).** Hand: Strike ×2, Ka-pow!, Razor — Claw and Thunder, Rapid Fire. Energy 3, Spark 1, Bomb 12 on the body.

Razor's face carries two things at once: the Hexerei rider, and *"If this is the third Attack you played this turn, gain 1 Energy."* Knowing Hexerei meant Razor pays me rather than costing me is what made me willing to spend a *Strike* — a card that was doing nothing else that turn — purely as a counter, to make Razor the third attack. I played **Ka-pow! (attack 1, 0 energy, sets off Bomb 12 and lays the Pyro aura) → Strike (attack 2, pure counter) → Razor (attack 3)**. Razor reacted off the Pyro aura for 14 and Weak, **paid 2 Spark** (1 base + 1 for the reaction — the counter went 2 → 4 on that single play, which is the "up to 3" rule visibly not maxing out), **and refunded the energy**, which let Rapid Fire follow for the kill. Without reading Hexerei I would have played Ka-pow! → Razor → Strike, dealt the same card damage, banked no Spark bonus, got no refund, and left the Merc alive at roughly 7 HP with a 14-damage swing coming at my 36 HP.

---

## Non-blindness declaration

**Repo files read: none.**

- Every game action was one of the two allowed commands, `GITS_LANE=2 python -m understudy.blindplay observe` and `GITS_LANE=2 python -m understudy.blindplay act "<command>"`. I ran no other `understudy` subcommand — no `harness state`, no `scenario`, no `staged_turn`, no `soak`.
- **Tools used:** the **Read** tool once, on my brief at `C:\Users\Monty\AppData\Local\Temp\claude\...\scratchpad\k24-seat-lane2.md`; the **Bash** tool for every game command; the **Write** tool once, for this record.
- **Shell work outside the two commands:** none that touched the repo. I piped `observe` output through `sed -n '<ranges>p'` and once through `grep -E '^- \*\*'` to re-read one block of a screen without re-printing the whole page. Both are filters on the bridge's own output and read no file. Note for the coordinator: on one such call my two `sed` ranges overlapped and printed the enemy block twice — that duplication was my filter, **not** the game, and I mention it so nobody reads it as a rendering defect.
- I chained several `act` calls in one Bash invocation with `;` or `&&`. Each was still one `act`, and the bridge's own counter (which reached exactly 120) is the authority.
- No repository file, YAML sheet, C# source, doc, packet, review material or other seat's record was opened at any point.
