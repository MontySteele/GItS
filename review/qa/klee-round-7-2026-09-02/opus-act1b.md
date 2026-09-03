# Klee round 7 — blind seat record — Act 1, second seat

## Identity

- **Model / seat:** Opus (Claude), blind TESTER seat, continuing the run the previous seat handed off. Lane 2 (`GITS_LANE=2`), mod `KLEEMOD-KLEE`.
- **Character:** Klee. **Act:** 1. **Act boss named on the map:** Waterfall Giant (never reached — it was 9 floors ahead when I died).
- **Picked up at:** map screen after floor 6, **2/62 HP**, 76 gold, no potions, 16-card deck, relics Pounding Surprise and Arcane Scroll.
- **Stopped at:** **dead.** Combat screen, Fight 6, round 2, killed by the enemy turn. The bridge returned `TOOL-BLOCKED: game_over` and printed **"The run ended on floor 9."**
- **Actions accepted:** **16** accepted `act` calls. **Zero refused** — every command I typed was accepted on the first form.
- **Termination reason:** the run ended in **death**. Not a budget stop. I used 16 of 140 permitted act calls and 15 of 300 tool calls.
- **HP trajectory:** 2 → 2 (event, no damage) → 2 (Fight 6 turn 1: blocked 11 to zero) → **0 (dead, Fight 6 turn 2)**.
- **Gold at death:** 76. Never spent a coin the whole run — no shop was ever on a reachable node, for either seat.
- **Potions at death:** none. Glowwater Potion gained at the Drowning Beacon event and spent in Fight 6 turn 1.

**Where the run stands: over.** Died on the floor the bridge calls 9 (the `go` call for that node printed `Traveling to Monster at (3,8)` — the two numbers disagree by one, see the kit notes), against **Calcified Cultist 40/40 + Seapunk 23/44**, on the second turn of the first fight after the hand-off.

**Relics, as printed (unchanged):**

- **Pounding Surprise** — Whenever a Bomb goes off, gain 1 Spark. Card rewards after a fight offer a fourth Companion choice.
- **Arcane Scroll** — Upon pickup, obtain a random Rare Card to add to your Deck.

**Deck at the end (16 cards, unchanged from the hand-off).** No card was added or removed: the one Unknown node was an event that paid in a potion, and I won no fight, so no card-reward screen ever appeared. Like the previous seat, **I never saw a deck screen** — the bridge printed no such view — but this round I did see 11 of the 16 faces in hand, and the pile arithmetic closed exactly (5 hand + 6 draw + 5 exhausted = 16), which independently confirms their reconstruction. Quoting the faces as printed to me this round:

- **Strike** ×4 — cost 1, attack. "Deal 6 damage."
- **Defend** ×4 — cost 1, skill. "Gain 5 Block." (*Block* — Until next turn, prevents damage.)
- **Jumpy Dumpty** ×1 — cost 1, skill. "Place a Bomb 8. When it goes off, place a Mine 3 on ALL enemies."
- **Ka-pow!** ×1 [Pyro] — cost 0, attack. "Retain. Set off. Deal 4 damage."
- **Alice's Recipe** (Swift 2) ×1 — cost 2, power. "Your Bombs grow twice each turn. Draw 2 cards the first time this is played."
- **Pocket Fireworks** ×2 [Pyro] — cost 1, attack. "Deal 9 damage."
- **Big Badda Boom** ×1 [Pyro] — cost 2, attack. "Set off. Deal 12 damage. Then deal damage equal to what the Bombs dealt."
- **Powder Charge** ×1 — cost 1 Spark, skill. "Place a Bomb 6."
- **Diona — Icy Paws (proto)** ×1 — cost 1, skill. "Gain 6 Block. When this Block absorbs damage, apply Cryo to the attacker."

---

## The two map screens, and the fact that there were no decisions on either

Both map screens between the hand-off and the fight offered **exactly one reachable node**. Floor 7: `Unknown (path 1)`, leading on to Monster. Floor 8: `Monster (path 1)`, leading on to Treasure. The map's forecast rows printed a RestSite one floor ahead on both screens, and on neither was it reachable.

So at 2/62 HP I had no route that avoided a two-enemy combat, and no route to a rest. **The hand-off state was not survivable and the map is what made it unsurvivable** — not a kit fact, but the reason this round is two screens and one fight long, and the reason the previous seat's decision to stop rather than walk into a fight was the correct read of the position they were in. There was simply nothing else on the board.

---

## The Drowning Beacon (floor 7 Unknown)

Printed in full, and this is the entire screen:

```
# Drowning Beacon

- **Bottle**
    Procure Glowwater Potion.
- **Climb**
    Obtain Fresnel Lens. Lose 13 Max HP.
```

**Chose Bottle.**
*Rejected:* Climb. At 2/62 HP, losing 13 Max HP costs nothing today but cuts what any rest site could ever give back, and the thing I would be buying — a **Fresnel Lens** — has **no printed text anywhere on this screen**. I would have been paying max HP for an object I could not read.

**But so was the thing I took.** "Procure Glowwater Potion" is the whole description. The reward screen that followed printed only the words `**Glowwater Potion**`. The potion's actual text — **"Exhaust your Hand. Draw 10 cards."** — appeared for the first time on the combat screen one floor later, when I already owned it. **This event asked me to choose between two objects and described neither.** It is the third instance of this exact shape in this run: the previous seat bought a `Swift 2` enchantment with no printed definition and a Neow "random Rare Card" whose result was never named. Three for three means it is a pattern, not an accident.

As it happens the choice was correct and by more than I knew: my Fight 6 opening hand contained **zero block cards** against an 11-damage attacker at 2 HP, so without the potion I would have died on turn 1 instead of turn 2. I got a life out of a coin-flip between two blanks.

---

## Fight 6: Calcified Cultist — HP 40/40, and Seapunk — HP 44/44

I came in at **2/62** with 3 energy and 1 Spark.

### Turn 1

Opening hand: **Big Badda Boom, Strike, Strike, Strike, Alice's Recipe (Swift 2)**. Incoming: Calcified Cultist `Empower (Buff)`, Seapunk `Aggressive (Attack) — the number on its icon is 11`.

**Not one block card.** Eleven damage into two hit points.

**Played: Glowwater Potion → Powder Charge on Seapunk → Diona — Icy Paws → Defend → Defend.** 16 block. Took nothing.

*The potion was the real decision of the fight, and a good one.* "Exhaust your Hand. Draw 10 cards" is not free: it permanently exhausted **Big Badda Boom and Alice's Recipe** — the archetype's two payoff cards — for the rest of the combat, along with three Strikes, in exchange for drawing 10 of the 11 cards left in my pile. I took it because 11 damage kills me and nothing in my hand blocks; the trade was my engine for my life. It drew all four Defends and Diona.

*Rejected: Alice's Recipe + a Strike (build the engine, take 11, die).* Rejected on the arithmetic.
*Rejected: three Strikes for 18 into the Seapunk, and die.* Same.

*Then the sub-decisions, which were real:*

- **Powder Charge first, because it costs 1 Spark and no energy.** A Bomb 6 for free is the best-value card in this deck and the previous seat was right to flag it. *Rejected:* putting the bomb on the Calcified Cultist. I put it on **Seapunk specifically because Diona's Cryo would land on whoever hit me, and Seapunk was the only attacker** — so the bomb and the aura would end up on the same body. That was a two-card, two-turn plan built entirely out of printed text, and it is the best thing this kit did for me.
- **Diona over a third Defend for the last energy**: 6 block instead of 5, plus the Cryo rider. *Rejected:* Defend ×3 + Diona would have been 21 block but I only had 3 energy.
- **Blocking to 16 against an 11 rather than 11 exactly + Pocket Fireworks for 9 damage.** *Rejected the damage line* because the Calcified Cultist's intent was `Empower (Buff)` with no printed target, and I could not tell from the screen whether that buff would land on itself or on the Seapunk before the Seapunk swung. At 2 HP an unknown +Strength is fatal. **I paid 9 damage for that uncertainty and it turned out the Empower was self-directed (the Cultist came back with `Ritual 2` on itself).** The screen would not tell me, so I bought insurance. I would buy it again, and it did not change the outcome.

**The Diona rider worked exactly as printed.** Round 2 opened with `Cryo Aura 1 (aura)` on Seapunk. My block had absorbed damage; the attacker got Cryo.

### Turn 2 — and the finding this whole round exists for

Round 2 screen. And the moment the Cryo existed, **my Pyro cards grew a line they had never printed before**:

> **Ka-pow!** [Pyro] — cost 0, attack
> Retain. Set off. Deal 4 damage.
> ***Reaction preview: Melt*** — *This card supplies Pyro or Cryo while an enemy has the other aura. The triggering hit deals 1.75x damage and consumes the aura.*

The same line appeared on **Pocket Fireworks**. The board printed the other half:

> **Cryo Aura 1 (aura)** — Cryo clings to this enemy for 1 more turn. A hit of a different element consumes the aura and triggers an Elemental Reaction; a Cryo hit refreshes its duration.

**Played: Ka-pow! on Seapunk, then Defend, Defend, Defend** (15 block, 0 energy left, Pocket Fireworks stranded in hand).

**Ka-pow! took Seapunk from 44 to 23 — twenty-one damage from a card that costs nothing.** The Bomb 10 went off as a Pyro hit into the Cryo aura: 10 × 1.75 = 17, plus Ka-pow!'s own 4 = 21. Spark went 0 → 1 (Pounding Surprise, one bomb). The consumed Cryo was replaced by `Pyro Aura 2` from Ka-pow!'s own applies-Pyro clause. **Every number on those two screens multiplied out correctly.** This is the first time in seven fights across two seats that anyone has seen the Reaction layer fire, and it was legible, previewed, and enormous.

*The one alternative I rejected, and it lost either way.* **Third Defend (5 block) over Pocket Fireworks (9 damage).** Incoming was `9` from the Cultist plus `2x4` from the Seapunk = **17**. My entire remaining deck could produce **15** block. I took the block anyway, on the reasoning that if any part of my model of the incoming was two points pessimistic — an intent number that included Strength I'd double-counted, a hit the block ordering ate — 15 saves the run and 10 does not. It was not pessimistic. **17 into 15 block leaked exactly 2, and I had exactly 2 HP.** The run ended by the width of one Defend minus three.

*There was no decision to reject on the defensive side, because there was no defensive option left to reject.* Zero energy after three Defends, one Pocket Fireworks I could not cast, one Spark and no Spark card in hand (Powder Charge was in the draw pile). The turn was arithmetic, not a choice.

---

## Companions and offers

**None.** I won no combat, so no card-reward screen appeared and Pounding Surprise's fourth-slot Companion rider was never exercised this round. The event paid in a potion.

The one companion card in the deck, **Diona — Icy Paws (proto)** — *"cost 1, skill. Gain 6 Block. When this Block absorbs damage, apply Cryo to the attacker."* — was played once and **did more for this kit than any Klee card in the deck**. Its text made sense next to the kit in a way none of the four companions the previous seat declined would have: it is the only key to the Reaction riders that six Klee cards print. It also still prints **"(proto)"** in the title the player reads, one round later.

---

## The kit, after 6 fights

### (a) Which decisions felt like real choices, and what they traded off

Only one turn in this round had genuine choice in it, and it had three:

1. **Spend the potion, and with it the engine.** "Exhaust your Hand. Draw 10 cards" meant burning Big Badda Boom and Alice's Recipe out of the fight to find block. Engine for survival is exactly the trade a low-HP run should be asked to make, and both halves were printed clearly enough to price it.
2. **Where to put the free bomb.** Powder Charge costs a Spark and no energy, so it never competes with anything — but *which enemy* is a real question, and this turn the answer came from a different card's rider (Diona's Cryo lands on whoever attacks me, so put the Pyro payload on the attacker). Two cards, two turns, one plan, assembled from printed text. That is the kit at its best and it is the same shape as the previous seat's bank-or-cash finding: the good decisions in this kit are all about **where and when the bomb cashes**, never about which card is bigger.
3. **Insurance against an unreadable intent.** `Empower (Buff)` with no named target, at 2 HP, is worth 9 damage of hedging. That the screen refuses to say who a buff lands on is what made it a decision at all — an arguably accidental source of tension.

### (b) What felt automatic, and what never seemed worth playing

**Turn 2 was almost entirely automatic.** Ka-pow! costs 0, so it is never a decision — a free card is played, always. The remaining three energy had one job. The only sub-choice on the board was the third Defend versus Pocket Fireworks, and both branches died, which means it was a choice in form only.

Never worth playing, confirming the previous seat: **Defend.** Five block is the wrong denomination for this game. The numbers I was asked to answer were 11, then 9 and 2x4 — and I lost by **2**, holding a deck whose entire block output is 5, 5, 5, 5 and 6. A defensive card that cannot reach a round number of the incoming damage is not a defensive option.

### (c) What I could not understand, or that contradicted its own printed text

1. **The Bomb badge does not know about the Reaction, and the Reaction preview does not know about the Bomb.** The badge printed `Bomb 10 (buff) — Set off here deals 10 Pyro damage.` My card printed `Reaction preview: Melt — the triggering hit deals 1.75x damage`. **The hit actually dealt 17.** Neither screen printed 17, and neither is wrong on its own. This is the same defect the previous seat found (the badge showing a conditional post-Weak figure under a raw-looking title), now reproduced through a completely different modifier: **the badge number is the bomb's size, never the bomb's damage, and the screen never anywhere prints the product.** I happened to do the multiplication; a player who read the badge would have expected 10 and got 17.
2. **The Drowning Beacon described neither of the two objects it sold** (above). Third instance of purchase-sight-unseen in this run.
3. **The floor number disagrees with itself.** `go "Monster (path 1)"` printed `ok Traveling to Monster at (3,8)`; the game-over line printed `The run ended on floor 9`. One of those two is off by one.
4. **`Empower (Buff)` names no target.** At full HP that is flavour; at 2 HP it is the difference between a correct and a fatal turn, and it cost me nine damage of hedging.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted: Defend**, and harder than the previous seat put it. They finished the act at 2/62 holding four of them; I *died* holding a deck whose maximum possible block was two short of the incoming. Four copies of a 5-block card is not a defensive plan, it is four cards that are not the kit.

**Happiest to draw: Ka-pow!**, without competition, and now for a sharper reason than last time. It is the only card in this deck whose value comes from what other cards did — a 0-cost that dealt **21 damage, nearly half a 44-HP enemy's bar**, because a Spark had placed a bomb and a companion had painted an aura. Every good moment either seat has had in this kit is Ka-pow! cashing something. The runner-up remains **Powder Charge** for costing no energy at all.

### (e) Did the previous seat's findings hold up in my fight

- **"The Elemental Reaction layer is printed everywhere and reachable nowhere" — REFUTED, decisively, by the one card they drafted to test it.** Diona's Cryo turned on a `Reaction preview: Melt` line on every Pyro card in my hand, and the detonation paid 1.75x exactly as previewed. The layer works and the UI announces it the instant it becomes reachable.
- **…but their finding survives in a worse form: the layer is un-self-servable.** Every Klee card is [Pyro] and none can apply another element. **Six Klee cards print Reaction riders and zero Klee cards can switch one on.** The whole layer is gated behind drafting a companion of a foreign element, and my single Cryo card, played once, doubled the output of my best card. That is a large amount of printed text that a Klee deck cannot reach on its own.
- **"The bomb badge number changes meaning between turns" — HELD, and generalised.** Badge 10, actual hit 17. The badge reports charge, not damage, and no screen prints the product (see (c)1).
- **"Two Mines from one rider" — NOT TESTED.** Jumpy Dumpty stayed in my draw pile both turns; I never played it.
- **"Bomb cards and detonator cards are separate draws, and when they separate half your hand is inert" — HELD, and the game made a joke of it.** The Glowwater Potion drew **10 of the 11** cards in my pile. The single card it left behind was **Ka-pow!**, the only detonator in the deck — Big Badda Boom having just been exhausted by the same potion. I placed a bomb on turn 1 that I had, at that instant, no card anywhere in hand able to set off.
- **"(proto) leaks onto the card face" — HELD.** `Diona — Icy Paws (proto)` still prints it.
- **"Their first-turn-of-first-fight decision was sharp" — my first turn was sharper, for a bad reason.** A 2-HP opening hand with no block card is tense, but it is tense the way a coin flip is; the previous seat's turn 1 was tense because of a choice about the kit.

---

## Non-blindness declaration

**Other repo files read: none.**

- **The one record I read:** `C:\Users\Monty\Documents\GitHub\GItS\review\qa\klee-round-7-2026-09-02\opus-act1.md`, read once, first, before any game command, and declared at the time.
- **Tools used:** `Read` (once, for that record), `Bash` (15 calls, all of them wrappers around the two allowed commands), `Write` (once, for this file).
- **Every command run outside the two allowed ones:** three shell utilities, all on my own output and none touching the repo —
  - `cd "C:\Users\Monty\Documents\GitHub\GItS"` prefixed to every Bash call, to set the working directory;
  - `sed -n '...p'` on four `observe` outputs, to print only the ranges of the screen I needed and keep the transcript small — this discards text, it never adds any;
  - `>/dev/null` on two `act 'end turn'` calls, so the chained `observe` output was the only thing printed.
- **Game commands:** all 16 accepted actions were `GITS_LANE=2 python -m understudy.blindplay act "<command>"`, and all 9 reads were `GITS_LANE=2 python -m understudy.blindplay observe`. **Zero refusals.**
- I chained `act` calls with `&&` inside single Bash calls to conserve tool budget, but — taking the previous seat's lesson — **I never chained an `end turn` behind a play I was unsure of.** Both `end turn` calls were issued alone.
- I did **not** run `harness state`, `scenario`, `staged_turn`, `soak`, or any other understudy command.
- I did **not** use the offered scratchpad notes file; all notes were held in context.
- I read no YAML sheet, no C# source, no doc, no packet, no review material, and no other seat's record.
- I did not tear the lane down.
