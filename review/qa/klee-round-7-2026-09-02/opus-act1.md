# Klee round 7 — blind seat record — Act 1

## Identity

- **Model / seat:** Opus (Claude), blind TESTER seat. Lane 2 (`GITS_LANE=2`), mod `KLEEMOD-KLEE`.
- **Run seed:** never printed. No screen the bridge showed me carried a seed, and I did not go looking for one.
- **Character:** Klee. **Act:** 1. **Act boss named on the map:** Waterfall Giant (never reached).
- **Actions accepted:** 99 accepted `act` calls, plus 1 refused (see Fight 5, turn 1). 100 `act` invocations total.
- **Termination reason:** the act-call budget. 99 of 110 accepted with 11 remaining. My five fights cost an average of ~14 accepted acts each, so 11 was not enough to finish another combat, and at 2/62 HP the only reachable node was an `Unknown` that could have been one. I stopped on the map screen rather than walk a 2-HP run into a fight I could not have finished inside budget. **Not** the act-2 hand-off: the boss was still 10 floors ahead.
- **Where the run stands:** the map screen after floor 6, one reachable node (`Unknown (path 1)`, leads on to Monster). A RestSite is 2 floors ahead. Alive.
- **HP trajectory:** 62 → (F1) 54 → 48 → (F2) 37 → 34 → (F3) 25 → (F4) 21 → 18 → (F5) 17 → **2/62**.
- **Gold:** 76 (18 + 12 + 11 + 20 + 15; never spent, no shop visited).
- **Potions held:** none. Weak Potion spent in Fight 4, Attack Potion spent in Fight 5.

**Relics, as printed:**

- **Pounding Surprise** — Whenever a Bomb goes off, gain 1 Spark. Card rewards after a fight offer a fourth Companion choice.
- **Arcane Scroll** — Upon pickup, obtain a random Rare Card to add to your Deck.

**Deck at the end (16 cards).** Caveat for the next seat: *the bridge never showed me a deck screen*, so this is reconstructed from cards I drew plus every card I added. It reconciles with the pile counts (Fight 5 round 1 printed 10 in draw + 5 in hand = 15, before Diona was added).

- **Strike** ×4 — cost 1, attack. "Deal 6 damage."
- **Defend** ×4 — cost 1, skill. "Gain 5 Block."
- **Jumpy Dumpty** ×1 — cost 1, skill. "Place a Bomb 8. When it goes off, place a Mine 3 on ALL enemies."
- **Ka-pow!** ×1 [Pyro] — cost 0, attack. "Retain. Set off. Deal 4 damage."
- **Alice's Recipe (Swift 2)** ×1 — cost 2, power. "Your Bombs grow twice each turn. Draw 2 cards the first time this is played."
- **Pocket Fireworks** ×2 [Pyro] — cost 1, attack. "Deal 9 damage."
- **Big Badda Boom** ×1 [Pyro] — cost 2, attack. "Set off. Deal 12 damage. Then deal damage equal to what the Bombs dealt."
- **Powder Charge** ×1 — cost 1 Spark, skill. "Place a Bomb 6."
- **Diona — Icy Paws (proto)** ×1 — cost 1, skill. "Gain 6 Block. When this Block absorbs damage, apply Cryo to the attacker."

I believe **Alice's Recipe** is the random Rare that Arcane Scroll granted — it was never in a card-reward screen, and the card count only works if it arrived at Neow. The screen never told me what the Scroll gave me, which is itself a small gap: I picked a Neow option whose result was never printed.

**Neow pick: Arcane Scroll** ("Obtain a random Rare Card"), over Lava Rock (2 boss relics) and Dowsing Rod (add 1 Dowsing).
*Why:* I am here to read the kit, and a rare card puts a piece of the kit in my hand on floor 1, where a boss-relic voucher 16 floors away would have taught me nothing. Rejected Dowsing Rod because "Dowsing" was a word with no printed definition anywhere on the screen — I would have been adding a card I could not read.

---

## Fight 1: Sludge Spinner — HP 39/39

**Turn 1** (3 energy, hand: Defend ×2, Strike, Jumpy Dumpty, Alice's Recipe). Played **Alice's Recipe** (2) then **Jumpy Dumpty** (1) on the Spinner.
*Rejected:* Strike + Defend + Defend (6 damage, 10 block, take nothing). I took the whole 8 to the face instead, because the two setup cards read as an engine and I wanted to see whether it paid: "Grows by 4 at the start of your turn. **Never goes off by itself**" plus "Your Bombs grow twice each turn". That "never goes off by itself" is the scariest line on the card — I had just spent my whole turn on a resource with **no card in hand that could ever cash it**, and nothing on the screen told me a detonator existed. That is a real decision and a genuinely tense one.

**Turn 2** (HP 54, Weak 1 on me). Played **Strike ×3** for 12.
*Rejected:* Defend ×2 + Strike (8 damage, 5 block). Chose damage because the Spinner only hit for 6 and I was at 54/62. Almost no decision content — my hand was three Strikes and two Defends with no bomb interaction at all.

*Screen-vs-screen note, and I got this wrong first:* Strike printed **"Deal 4 damage"** this turn instead of 6, and the bomb badge printed **"Bomb 12 ... Set off here deals 12 Pyro damage after Weak"**. I initially read 8 → 12 as +4 and concluded Alice's Recipe had **not** doubled anything. It had: the true charge was 16, and both numbers on the screen were post-Weak displays. The screen is honest — it says "after Weak" — but the headline number in the buff title (`Bomb 12`) is a *conditional* value while the same title on other turns is the raw one. I could not read the bomb's actual size off that screen, only its size-if-set-off-right-now.

**Turn 3.** Drew **Ka-pow!** — "cost 0, Retain, Set off, Deal 4 damage" — the detonator, which the game had not told me existed until it appeared. Bomb had grown 8 → 16 → 24 (+8/turn, doubling confirmed). Enemy at 27. Played **Ka-pow!** for 24 + 4 = 28. Kill.
*Rejected:* nothing. This turn had no decision — a free retained card that exactly killed. It was, however, the most satisfying moment of the run: the setup turn that looked like a mistake paid out at 4× a Strike.

---

## Fight 2: Seapunk — HP 46/46

**Turn 1** (3 energy). Played **Alice's Recipe (Swift 2)**, which drew Pocket Fireworks and a Strike, then **Pocket Fireworks** (9 damage) with the last energy.
*Rejected:* Strike ×2 + Defend (12 damage, 5 block). The Swift enchantment turned a 2-cost do-nothing power into a 2-cost draw-2, which changes the card's whole character — with a bomb-less board the Recipe would otherwise have been a dead turn against an 11-damage attacker.
*Note:* the Recipe buff was live with **zero bombs on the board** for the whole turn. The kit lets you play its scaling power into an empty board where it does literally nothing, and the screen does not warn you.

**Turn 2** (HP 37; Pyro Aura 1 now on Seapunk). Played **Jumpy Dumpty** (Bomb 8), **Strike** (6), **Defend** (5).
*Rejected:* Jumpy + **Ka-pow! immediately** — detonate the Bomb 8 at once for 8+4=12 and place the two Mines a turn early. I banked instead, because +8/turn doubling means one turn of patience turns 8 into 16, and Ka-pow! is **Retain**, so waiting costs me nothing but the tempo. This is the kit's best decision and it recurred all run: *detonate small now for the Mine rider, or bank for the doubling?*
*Also rejected:* Defend ×2 (10 block, take 0) over Strike + Defend (take 3). Traded 3 HP for 6 damage.

**Turn 3** (Bomb 16; enemy intent **Empower**, so nothing incoming). Played **Jumpy Dumpty** again (second Bomb 8, stack now 24), then **Ka-pow!**: 16 + 8 = 24 Pyro, then Ka-pow's own 4 = **28**, exactly as the text predicted. Enemy 31 → 3. Then **Strike** for the kill.
*Rejected:* banking one more turn for a ~48-damage detonation. Pure overkill on a 31-HP enemy, and it would have let the Empower resolve. The three Defends in hand were dead cards because the intent line told me no attack was coming — the intent display is doing real work here.
*Spark check:* 1 → 3, exactly +1 per bomb that went off. Pounding Surprise is legible.

---

## Fight 3: Corpse Slug ×2 — HP 26/26 and 27/27

Both printed **Ravenous 4** — "When an enemy dies, Corpse Slug immediately eats it, becoming Stunned and gaining 4 Strength."

**Turn 1** (HP 34, 3 energy). Played **Jumpy Dumpty** → **Ka-pow!** → **Pocket Fireworks**, all on Slug (2), then **Defend**.
*Rejected:* banking the bomb again. With two enemies the calculus **inverts** — Jumpy's rider only fires "when it goes off", so early detonation is the only way to get the Mine onto the *other* slug. Banking would have been strictly worse. That the same card wants opposite play patterns against one enemy vs two is the best thing in this kit.
*Also rejected:* Defend ×2 (take 4 instead of 9). Took 5 more damage to deal 9 more; at 34/62 that was probably too aggressive in hindsight, and it is where the run's HP problem started.
*Outcome matched the text exactly:* both Mines went off before their owners' hits (26→23, 6→3), Spark 1 → 4 (+1 bomb, +2 mines).

**Turn 2.** Killed the 3-HP slug with one **Strike** to test Ravenous.
*Rejected:* leaving it alive and focusing the big one, to deny the survivor its +4 Strength. I killed it because the debuff intent was worse than the Strength. The screen then printed **"Intent: Stunned (Stun) — This enemy can't act on its next turn"** — which is exactly the confirmation I needed, and it arrived *before* I had to commit my remaining energy. I had planned to hedge with a Defend; seeing the stun, I played **Strike ×2** instead for 12.
*This is the screen doing its job well:* the keyword was undefined when I chose, and defined the instant it mattered.

**Turn 3.** Slug at 11, hitting for 12. Killed with **Pocket Fireworks** + **Strike**.
*Rejected:* Big Badda Boom, also lethal at 12 damage — but with no bombs on the target BBB is a **2-cost 12** against my **1-cost 9**. Worth writing down: the archetype's payoff card is strictly worse than a common when the engine is offline.

---

## Fight 4: Calcified Cultist 40/40 + Damp Cultist 53/53

**Turn 1** (HP 25, both intents Empower). Played **Pocket Fireworks ×2 + Strike**, all into Calcified.
*Rejected:* nothing meaningful. Both enemies were buffing, so every Defend was dead and I had no bomb card in hand. **This turn presented no decision at all beyond which of two enemies to point at.** Saying so is the finding.

**Turn 2.** Damp revealed **Ritual 5** (+5 Strength every turn) — a hard clock against my 25 HP. Played **Jumpy Dumpty** → **Ka-pow!** on Calcified (12) → **Strike** to kill it, then **Defend**.
*Rejected:* Alice's Recipe + Jumpy (draw 2, bank the bomb). Refused because Ritual 5 meant a long fight was an automatic loss; the bomb had to cash immediately. The scaling enemy is what forces the bank-or-cash question to resolve, and that felt good.

**A discrepancy I could not resolve from the screen.** After that detonation, Damp Cultist's badge read: **"Bomb 6 — Set off here deals 6 Pyro damage. Bombs here: 2, including 2 Mines."** Two Mines, from one Jumpy Dumpty whose rider reads "place a Mine **3** on ALL enemies" — singular, one per enemy. And Spark went only **1 → 2**, i.e. exactly **one** bomb went off. So one bomb going off placed two Mines on one of the two enemies. Either the rider fires per-enemy-in-the-room rather than once, or a Mine placed onto the dying Calcified migrated. Nothing on the screen distinguishes those, and I could not make the printed rider text produce the printed board state.

**Turn 3.** Damp at 47, Strength 10 and climbing. Used **Weak Potion** on it, then **Big Badda Boom** (12, no bombs) + **Strike**.
*Rejected:* saving the potion for the bigger hits later. Weak lasts 3 turns and the fight had ~3 turns left, so front-loading covered the whole thing.
*Rejected:* Defend-heavy turtling — against Ritual 5 that loses by construction.

**Turn 4.** **Strike ×2 + Ka-pow! + Defend** for 16.
*Rejected:* Alice's Recipe for 2 energy to draw 2 — max 9 damage from the follow-up vs 16 from just attacking. Recipe was uncastable value with no bomb in the deck's reach.

**Turn 5.** Damp at 13. **Pocket Fireworks ×2** = 18. Kill. No decision.

---

## Fight 5: Fossil Stalker — HP 52/52

Printed **Suck 3** — "Whenever Fossil Stalker deals unblocked attack damage, it gains 3 Strength."

**Turn 1** (HP 18, incoming 12, hand: Defend ×3, Strike, Alice's Recipe). Used **Attack Potion**, took **Rapid Fire** from the three offered, then **Defend ×3** for 15 block.
*Rejected:* Defend ×2 + Strike. Suck punishes *partial* blocking specifically — leaking 2 damage would have handed it 3 permanent Strength. Blocking to zero denied it the buff, and the screen confirmed it: no Strength appeared. This is a good, legible interaction and the enemy that most changed how I played the kit.

**REFUSAL (the one refused command).** `play "Rapid Fire" on "Fossil Stalker"` returned **`error Card 'Rapid Fire' cannot be played on 'Fossil Stalker'`**. Rapid Fire reads "Deal 3 damage to a **random** enemy 4 times", so it takes no target — but the refusal did not say so, and did not list the working form the way the brief said ambiguous names do. Because I had chained the call, the turn ended and the free potion card was discarded unplayed: **12 free damage lost to a refusal message that did not tell me what to type instead.** My error for chaining, but the message had the information and withheld it.

**Turn 2** (Stalker 52, incoming 3×2 = 6; only one Defend in hand, so full blocking was *impossible* — 5 block against 3+3 still leaks 1 and still feeds Suck). Played **Ka-pow!** (4) + **Pocket Fireworks** (9) + **Strike** (6) + **Defend**.
*Rejected:* Pocket Fireworks + Big Badda Boom + Ka-pow! for 25 damage and zero block, leaving me at 12. Chose 19 damage and 5 block to stay alive a turn longer against a snowballing enemy.
*Also genuinely rejected:* **holding Ka-pow!**. It is Retain, so it survives the turn — spending it as a 4-damage cantrip meant not having a guaranteed detonator when Powder Charge or Jumpy Dumpty finally showed up. I spent it to race, and one turn later that was exactly the wrong call.

**Turn 3** (HP 17, incoming 15, **no Defend in the hand at all**). Played **Powder Charge** (1 Spark, Bomb 6) + **Pocket Fireworks** + **Strike ×2** for 21. Stalker 33 → 12. Took the full 15 → **2 HP**.
*Rejected:* Jumpy Dumpty instead of a Strike, to stack a second bomb. Refused because **I had no detonator in hand and none in the draw pile — the pile was empty**. Two bombs I could not set off would have been 14 damage of pure decoration. This is the kit's failure mode in one turn: the bomb cards and the detonator cards are separate draws, and when they separate, half your hand is inert.
*There was no defensive option to reject.* Zero block cards in hand. The turn was forced.

**Turn 4** (2 HP, Stalker 12 with a Bomb 10 on it). Played **Big Badda Boom**: set off 10, deal 12, then 10 again = 32. Kill, and the first time all run I saw its doubler clause fire.
*Rejected:* Pocket Fireworks ×2 (18, also lethal). Took BBB to finally see the third clause resolve.

---

## Companions and offers

Every companion I was offered, quoted as printed. All five arrived as the **fourth** card-reward slot, which Pounding Surprise's text explicitly promises — that rider worked every single time.

1. **Noelle — Sweeping Time** — cost 2, attack. "Deal damage equal to your Block to ALL enemies."
   Makes sense *as a card*, but next to this kit it is aspirational: my only block source was a 5-Block Defend, so it reads as 5 AoE damage for 2 energy. It pairs with the **Sorry, Jean...** card offered on the same screen ("Remove one of your Bombs. Gain Block equal to its size") — bomb → block → AoE damage is a real and attractive line, but it needs two specific cards I did not have.
2. **Charlotte — First-Person Shutter** — cost 1, skill. "Gain 4 Block. At the start of your next turn, gain 4 Block."
   Perfectly legible, entirely kit-neutral. Nothing about it is Klee; it would read identically in any deck.
3. **Bennett — Fantastic Voyage (proto)** — cost 1, skill. "If you are above 70% HP, gain 3 Strength. Otherwise, gain 10 Block. Exhaust."
   Legible and it has a real decision baked into it. But note the **"(proto)" in the player-facing title.**
4. **Freminet — Pressurized Floe: Backstroke** — cost 2, attack. "Deal 10 damage. Gain 6 Block."
   Clean, and the block half is what I actually needed. Kit-neutral again.
5. **Diona — Icy Paws (proto)** — cost 1, skill. "Gain 6 Block. When this Block absorbs damage, apply Cryo to the attacker." — **DRAFTED.**
   This is the only card in the entire run — companion or Klee card — that applies a **non-Pyro** element, and therefore the only key I was ever offered to the Elemental Reaction layer that six of my cards print clauses about. I drafted it over the strictly better survival card (**Dig In**, "cost 1 Spark, Gain 8 Block", which would also have used the Spark I keep wasting) specifically so the next seat can test whether Reactions work at all.

**Two companions of five print "(proto)" in the title the player reads.** That is development state leaking onto a shipped card face.

---

## The kit, after 5 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The central one is genuinely good: **bank the bomb or cash it now.** Bombs grow +4/turn (+8 with Alice's Recipe), never go off by themselves, and Ka-pow! is a 0-cost Retain detonator — so waiting is nearly free in energy and costs only the damage you take meanwhile. Fight 2 turn 2 I banked and got 28 damage out of one Ka-pow!; Fight 3 turn 1 I cashed immediately and was *right to*, because Jumpy Dumpty's Mine rider only fires when the bomb goes off, so with two enemies early detonation is the only way to spread. **The same card wanting opposite lines against one enemy versus two is the best design in this kit.**

Second real choice: Fight 5's **Suck 3** made partial blocking actively poisonous, which inverted the kit's whole "dump everything into damage" instinct. Third: spending Ka-pow! as a 4-damage cantrip versus holding the Retain as insurance that my next bomb is cashable — I got that one wrong and it nearly killed me, which means it was a real decision.

**(b) What felt automatic, and what never seemed worth playing.**

Automatic: every turn where the enemy's intent was **Empower/Buff**, my Defends became visibly dead and the turn collapsed into "point damage at something" (Fight 4 turn 1, Fight 2 turn 3). Also automatic: every lethal turn, and every turn where my hand was Strikes and Defends with no bomb piece — which was **roughly half my turns**. The deck is 8 vanilla starter cards out of 16, and when you draw the vanilla half there is no kit on the screen at all.

Never worth playing: **Big Badda Boom with no bomb on the target** — a 2-cost 12 next to my 1-cost 9. **Alice's Recipe played into an empty board**, which the game happily let me do twice. And **Ka-pow!'s 4 damage** in isolation is filler; the card is a detonator wearing an attack's clothes.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **The Elemental Reaction layer is printed everywhere and reachable nowhere.** "A different aura is consumed to trigger a Reaction instead" appears on Ka-pow!, Pocket Fireworks, Big Badda Boom, Sizzle, Perfect Timing, Flame Dance. But every Klee card is **[Pyro]**, my own hits *refresh* Pyro rather than consume it, and enemies never arrived carrying an aura of their own — the only auras I ever saw were Pyro ones **I** had applied. So **Perfect Timing** ("If a Bomb triggered an Elemental Reaction this turn, play this again") and **Sizzle** ("...deal 6 additional damage") have riders I had no way to switch on, and **Flame Dance** ("Set off each enemy whose aura is not Pyro") is *actively disabled by my own deck* — playing any other Klee card first turns its set-off clause off. I was offered six cards keyed to a mechanic I could not access, and exactly one card in five fights (Diona) that could unlock it.
2. **The two-Mines-from-one-rider board state in Fight 4**, above. "Place a Mine 3 on ALL enemies" produced two Mines on one enemy from a single detonation (Spark +1 confirms one bomb). I cannot derive that from the text.
3. **The bomb badge number changes meaning between turns.** `Bomb 12 ... deals 12 Pyro damage after Weak` versus `Bomb 24 ... deals 24 Pyro damage`. Same field, sometimes the raw charge and sometimes a conditional post-Weak figure. It cost me a wrong read on whether Alice's Recipe was working at all.
4. **The Self-Help Book event sold me an enchantment sight-unseen.** "Choose a Power to Enchant with **Swift 2**" — nothing on that screen said what Swift does, no selection overlay ever appeared, and I learned only in the next combat that it means "the first time you play this card, draw 2 cards". It turned out excellent. I had no way to know that when I paid for it.
5. **Neow's Arcane Scroll never told me what rare it gave me.** I inferred Alice's Recipe from a card count.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Defend**. Five block against enemies hitting for 12 and 15 is not a defensive option, it is a rounding error — and against **Suck 3** a partial block is worse than none, so the card that is supposed to keep me alive was the card that fed the enemy. I finished the act at 2/62 HP holding four of them. Runner-up: **Alice's Recipe** in any fight where no bomb-placer showed up.

Happiest to draw: **Ka-pow!**, without hesitation. Cost 0, Retain, and it converts a number that has been quietly doubling on the enemy's portrait into a single enormous hit. Drawing it in Fight 1 turn 3 and cashing 24+4 for exact lethal is the moment the kit explained itself. **Powder Charge** is the honourable mention — 1 Spark and *no energy* for a Bomb 6, spending a resource I had otherwise been throwing away at the end of every fight.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a sharp one.** Three energy, and the choice was Strike + Defend + Defend for immediate, safe, boring value, or Alice's Recipe + Jumpy Dumpty — spending the entire turn on a charge that the card itself warns "**never goes off by itself**", with **no card in my opening hand able to set it off** and nothing on screen promising such a card existed. Choosing to take 8 damage for a resource I might never be able to spend is a real decision with real dread in it, and the payoff two turns later was the best moment in five fights. That is a strong opening turn.

The caveat: that decision exists because of the *starter* cards. Roughly half my turns afterwards drew the Strike/Defend half of the deck and presented nothing at all.

---

## Non-blindness declaration

**Repo files read: none.**

- **Tools used:** `Bash` (for the two allowed commands and one `mkdir`), and `Write` **once**, for this record.
- **Every command run outside the two allowed ones:** exactly one —
  `mkdir -p "C:/Users/Monty/Documents/GitHub/GItS/review/qa/klee-round-7-2026-09-02" && echo created`, to create the directory this file lives in.
- All game commands were `GITS_LANE=2 python -m understudy.blindplay observe` and `GITS_LANE=2 python -m understudy.blindplay act "<command>"`, each prefixed with `cd "C:\Users\Monty\Documents\GitHub\GItS" &&` to set the working directory, and several chained together with `&&` in a single Bash call to conserve tool budget. That chaining is what cost me the Rapid Fire card in Fight 5: the refused call did not stop the queued `end turn`.
- I did **not** run `harness state`, `scenario`, `staged_turn`, `soak`, or any other understudy command.
- I did **not** open the scratchpad notes file that was offered to me; all notes were held in context.
- I read no YAML sheet, no C# source, no doc, no packet, no review material, and no other seat's record.
