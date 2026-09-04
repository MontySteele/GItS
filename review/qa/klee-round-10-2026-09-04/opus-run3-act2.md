# Klee round 10, run 3, act 2 — blind seat record

## Identity

- **Model / seat:** Claude Opus 5 (`claude-opus-5[1m]`), blind TESTER seat, KLEEMOD-KLEE.
- **Lane:** 1.
- **Run seed:** not printed on any screen I was shown; I cannot state it.
- **Character:** Klee (the mod character; the bridge never printed a character name
  header, but every card in the deck and the relic `Pounding Surprise` are hers).
- **Act:** 2. The map printed **"At the top of this act: Knowledge Demon"** as the boss.
  I never reached it.
- **Actions accepted:** **62** accepted `act` calls (cap was 250).
- **Termination reason:** **not a budget.** On floor (2,5) — an Unknown node that
  turned out to be the **Crystal Sphere** event — I chose `Uncover Future`, and the
  bridge answered:

  ```
  TOOL-BLOCKED: crystal_sphere

  a minigame with a click-a-cell interface; the command grammar has no shape for it
  ```

  A second bare `observe` returned the identical two lines. The blindness brief says
  a `TOOL-BLOCKED` screen is a stop, so I stopped. The act-2 boss is alive, the run
  is not dead, and **the lane is NOT on the act-3 map** — it is parked inside the
  Crystal Sphere minigame at (2,5), roughly 9 floors short of the boss.
- **HP trajectory:** 77/77 at the first battle screen → 74 (end of Exoskeleton turn 1)
  → 66 (end of Exoskeleton fight) → 53 (Tunneler turn 1's 13-damage hit) → **53/77 at
  the stop.** Never dropped below 53; Lizard Tail was never triggered.
  - **Discrepancy with the handover:** the coordinator told me I was inheriting the
    lane at "17 of 77". The first battle screen printed **HP 77/77**. I have no way,
    blind, to tell whether act 1 ended at 77, or whether something between the acts
    healed. Recording it because it changed how I played: I tanked hits I would not
    have tanked at 17.
- **Gold:** 357 on entering the shop (I had never been shown a gold figure before
  that screen); 185 after three purchases; 113 after Explosives Workshop; **15** after
  paying 98 for `Uncover Future`.
- **Potions held at the stop:** Colorless Potion, Attack Potion, Strength Potion
  (3 of 3). Duplicator was won and spent in fight 2.
- **Relics at the stop:** Pounding Surprise, Stone Humidifier, Kusarigama, Lizard Tail,
  Prayer Wheel, **Toasty Mittens** (taken this act).
- **Deck at the stop.** The shop's removal screen printed the whole deck — 26 entries:
  Strike ×4, Defend ×4, Jumpy Dumpty+, Ka-pow! (Sharp 2), Big Badda Boom ×2,
  Dodoco Cover, Fwoosh!, Mine Toss, Bang Bang!, Razor — Claw and Thunder, Run Away!,
  Powder Charge ×2, Perfect Timing, Careful Now, The Big One ×2, Fish-Flavored Bait.
  Then: −1 Strike (removed, 75 gold), +Explosives Workshop (bought), and the two cards
  I had already taken as rewards but which **did not appear on that removal list** —
  Chained Reactions and Quick Fuse (see the kit answers, (c)) — plus one unnamed Power
  from the Infested Automaton event. So ~29 cards, one of which I have never seen.
- **Neow pick:** **none, inherited.** This is the second of chained seats; the deck,
  relics and both starting potions came from the seat that cleared act 1, and I made
  no Neow choice.

### The one non-combat pick I did make, and why

- **Tezcatara (Ancient node), took `Toasty Mittens`** — "At the start of your turn,
  Exhaust 1 card from your Hand and gain 1 Strength." I took it because it was the
  only one of the three options whose printed text I could fully evaluate blind:
  `Nutritious Soup` enchants "all Strikes in your Deck with Tezcatara's Ember" and I
  had no idea how many Strikes I had or what an Ember does, and `Toy Box`'s "Wax
  Relics" is a word the screen never defines. I also reasoned that Exhaust is a
  within-combat cost, not deck destruction, so the price is card economy in long
  fights and the payoff is compounding Strength. It paid: Strength 1 → 2 → 3 inside
  three turns of the first fight.

---

## Fight 1 — Exoskeleton ×3 (25/25, 24/24, 26/26), each with `Hard To Kill 9`

The board-defining line was on all three: **"Hard To Kill 9 — Reduce all damage taken
and HP lost by Exoskeleton to 9."** Read against the Bomb keyword — **"Not an Attack:
only their Vulnerable and a cap move it"** — this told me, before I played anything,
that my whole big-bomb plan was the *wrong* plan here and that many small hits beat one
large one. That is the most legible thing the kit did all round.

**Turn 0 (Toasty Mittens prompt) — exhausted `Defend`.** Rejected: Ka-pow! (0-cost,
Retain, my only free set-off), Powder Charge (Spark-priced, so it costs no Energy),
Jumpy Dumpty+ (Bomb 11 + Mines on ALL), Big Badda Boom (the payoff). Defend's 5 Block
was the only card that did nothing for either the charge or the detonation.
**Note: this prompt fires before the board is shown.** I chose which card to burn
without ever having seen that there were three enemies with a damage cap. That is a
decision the screen actively prevents you from making well.

**Turn 1 — Jumpy Dumpty+ → Exoskeleton (2); Powder Charge → Exoskeleton (2);
Ka-pow! → Exoskeleton (2); Big Badda Boom → Exoskeleton (3).**
This was the round's best turn and it had two live rejections.

- *Rejected: charging the bombs a turn.* Standard bomb play is to let them grow 4/turn
  and detonate later. The cap said no — a Bomb 11 is already wasting 2 points against a
  9 cap, and next turn it would waste 6. So: detonate immediately, every turn.
- *Rejected: Big Badda Boom on Exoskeleton (2) to finish it.* Jumpy Dumpty+'s bomb going
  off placed a **Mine 4 on ALL enemies**, and a Mine "goes off when its enemy attacks
  you, **before the hit lands**." Exoskeleton (2) was at 2 HP with intent "Attack for 8"
  and a Mine on it. So I deliberately left it alive: its own attack would kill it before
  it connected. I spent Big Badda Boom on Exoskeleton (3) instead, whose intent was
  Empower — a Mine on a non-attacker is a Mine that never fires, so that was the one
  worth cashing by hand.
  **It worked exactly as printed.** Next turn Exoskeleton (2) was gone, I had taken 3
  damage (the 1×3 attacker), and Exoskeleton (3) was at 8/26.

**Turn 2 (exhausted `Defend (3)`, of three in hand) — Strike → the 8 HP one;
Big Badda Boom → the 21 HP one.**
*Rejected: Big Badda Boom on the 8 HP enemy.* Big Badda Boom's 14 would have been
capped to 9 and thrown 6 away on an 8 HP target. Strike (8, after Strength 2) killed it
exactly and left the 2-Energy card for a full-health body. This is the cap doing real
work: it turns "which card on which enemy" into arithmetic rather than reflex.

**Turn 3 (exhausted `Careful Now`) — Razor — Claw and Thunder → the last Exoskeleton
(12/25, wearing Pyro Aura 1).**
*Rejected: Strike ×2 + Ka-pow.* The card printed its own answer: **"Reaction preview:
Overloaded — Pyro meets Electro: 6 damage to ALL enemies and 1 Weak on the reacted
enemy."* 10 (+3 Strength) capped to 9, plus the 6 from Overloaded, cleared 12 in one
card. The reaction preview on the card face is the single clearest piece of teaching in
the whole kit — it did the elemental arithmetic for me.
*Why I exhausted Careful Now:* "Gain Block equal to your largest Bomb, up to 10" with
zero Bombs on the board is a 1-cost card that gains 0 Block. Genuinely dead that turn.

**Result:** win, 66/77, three turns. Rewards: 12 Gold, Duplicator (a **potion**, though
the reward line printed only the bare name "Duplicator" with no text — I could not tell
it was a potion until the claim line said `Claiming reward: potion`), and two card
choices (Prayer Wheel's extra).
Took **Fish-Flavored Bait** over Witches' Circle (its Hexerei payoff needs Companion
cards I could not confirm I owned), Grounded+ (it rewards *not* setting off bombs, which
is the opposite of the line the caps had just taught me), and Sucrose.
Took **The Big One** over a second Fish, Witches' Circle and Sucrose — explicitly as
insurance for a *capless* enemy, since it was worthless against the fight I had just had.

## Fight 2 — Tunneler (87/87), no cap

**Turn 0 — exhausted `Defend`.** Again chosen blind, before the enemy was on screen.
Again the obviously worst card in hand. Two fights in, this prompt has never once been
a decision.

**Turn 1 — Perfect Timing; Fish-Flavored Bait; Mine Toss.**
*Rejected: leading with the bomb-placers.* Perfect Timing reads "Set off. Deal 8 damage",
and there were no Bombs yet — so playing it **first** wasted nothing and playing it last
would have thrown away the Bomb 4 I was about to place. Sequencing a set-off card to the
front of the turn to *avoid* its own set-off is a genuinely nice little decision, and
the screen gives you everything you need to find it.
*Rejected: holding the third Energy.* Nothing else in hand was a non-set-off play.
*Rejected: skipping Mine Toss.* Tunneler's intent was "Attack for 13", so a Mine was
guaranteed to fire for free damage plus a Spark from Pounding Surprise. It did.
Took the 13. 66 → 53.

**Turn 2 (exhausted `Strike (2)`, second of two) — Duplicator potion → Jumpy Dumpty+
(played twice) → Strike.**
Tunneler had switched to **Empower + Defend** and had no attack intent, and it already
carried a Bomb 8 (my Bomb 4, grown).
*Rejected: detonating now.* It was about to gain Block, and it prints
`Burrowed 1 — Block is not removed at the start of Tunneler's turn`, so anything I
detonated into that Block was going to be eaten. Charging instead was clearly right.
*Rejected: saving Duplicator for The Big One.* The Big One quadruples the set-off, so
duplicating it is pure overkill; duplicating the *charge* (two Bomb 11s) is what
actually scales. This was the most satisfying decision of the round.

**Turn 3 (exhausted the spare `The Big One`) — The Big One → Tunneler.**
The board read **HP 61/87, Block 32, Bomb 42 (Bombs here: 3)**. Quadruple set-off on
42 points of Bombs was 93+ through 32 Block and 61 HP. It was lethal and I knew it was
lethal from the printed numbers alone.
*Rejected: Big Badda Boom + Razor for 2 Energy.* That was ~25 through 32 Block — i.e.
nothing — and would have burned the charge. There was one right card and the screen
told me which.
*Why I exhausted the second The Big One:* one copy was already lethal; a second was
strictly dead weight, so it was the correct Strength donation.

**Result:** win, 53/77, three turns, no damage taken after turn 1. Rewards: 15 Gold,
Strength Potion, two card picks.
Took **Powder Charge** (Spark-priced, so it places a Bomb 6 without competing for
Energy — with Pounding Surprise refunding a Spark per bomb, that is the engine) over
Witches' Circle, Run Away! and Shinobu.
Took **Chained Reactions** ("Whenever one of your Bombs goes off, place a Bomb 3 on a
random enemy") over Coven Errand, Quick Fuse and Bennett, because it is the only card
offered that makes a set-off turn *feed the next* set-off turn.

## Between fights — Shop (357 gold), Infested Automaton, Crystal Sphere

- **Shop.** Bought Quick Fuse (25), Powder Charge (72), Card Removal (75, removed a
  Strike), Explosives Workshop (72). Rejected: Blood Vial 155 (2 HP a combat against a
  deck that was killing things in three turns), The Abacus 228, Tiny Mailbox 257, and
  — the one that was close — **Mona — Stellaris Phantasm 145**, "apply 1 Vulnerable to
  ALL enemies", because the Bomb keyword says Vulnerable is one of only two things that
  moves a Bomb, so Mona is the kit's only printed *bomb multiplier*. I passed to keep
  113 gold for the second Shop's card removal, and then the Crystal Sphere took 98 of it.
  In hindsight that was my worst call of the round.
- **Infested Automaton.** Took `Study — Obtain a random Power` over
  `Touch the Core — Obtain a random 0 cost card`, on the reasoning that every Power I
  had been shown (Chained Reactions, Explosives Workshop, Grounded+, Witches' Circle)
  was playable. **The screen never told me which Power I got.** It went straight to
  "Proceed". I still do not know what is in my deck.
- **Crystal Sphere.** Two options, no exit: `Uncover Future — Pay 98 Gold. Divine 3
  times.` and `Payment Plan — Gain a Debt. Divine 6 times.` **Neither "Divine" nor
  "Debt" is defined anywhere on the screen.** I paid the 98 rather than take an undefined
  permanent, and got the TOOL-BLOCKED wall. See (c).

---

## The kit, after 2 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Three, and all three were good.

1. **Charge or detonate.** Bombs grow 4 a turn and only move when something Sets off, so
   every turn asks "cash now or bank a turn". Fight 1 answered *cash every turn* (the 9
   cap makes a big bomb literally wasted); fight 2 answered *bank two turns and win with
   one card*. Same deck, opposite correct answer, decided entirely by a line printed on
   the enemy. That is the kit working.
2. **Which body to detonate on.** Jumpy Dumpty+ puts Mines on **ALL** enemies but a Mine
   only fires on an attacker, so "spend the Mine by hand on the enemy that is buffing,
   and let the attacker kill itself on its own Mine" is a real read of the intent line.
   I got a free kill out of it in fight 1.
3. **Sequencing inside a turn.** Perfect Timing and Ka-pow! both Set off, so where they
   sit in the turn changes what they do. Playing a set-off card *before* your bomb
   placers, precisely so it sets off nothing, is a nice non-obvious line the printed text
   fully supports.

The two currencies also stay pleasantly separate: Spark-priced cards (Powder Charge,
Fwoosh!, Bang Bang!, Quick Fuse) don't compete for Energy, and Pounding Surprise refunds
a Spark per bomb, so a detonation turn pays for the next turn's placements. I ended
fight 1 with 5 Sparks and no Spark card in hand, which was the only time that economy
felt like it was leaking.

**(b) What felt automatic, and what never seemed worth playing.**

- **The Toasty Mittens exhaust prompt was automatic five times out of five.** Four times
  the answer was "the Defend", once "the dead card". Worse, it fires *before the enemy
  board is drawn*, so on the first turn of a fight you are picking blind. It is a
  relic, not the kit — but it interacted with the kit's basic cards to produce five
  non-decisions in a row.
- **Strike and Defend.** 4 and 4 in a 26-card deck. Defend was exhaust fodder every
  single time. Strike was played twice and only ever because it was exactly lethal
  against a damage cap. Everything Klee-shaped is better than both.
- **Careful Now** — "Block equal to your largest Bomb, up to 10" — never once had a Bomb
  to read when I drew it, because I was detonating on the turn I placed. It seems to
  want the charge-two-turns plan, which is only one of the kit's two modes.
- **Grounded+** (offered, refused) rewards *not* setting bombs off, which is the same
  problem pointed the other way: the deck's own reward screen keeps offering me cards
  that want the mode I am not in.

**(c) What I could not understand, or that contradicted its own printed text.**

- **The kit's own text was very good.** I never had to guess at Bomb, Mine, Set off,
  Spark, or a reaction; the "Reaction preview: Overloaded" line on Razor's face was
  outright excellent teaching. Bomb's "only their **Vulnerable** and a **cap** move it"
  is the single sentence that made both fights legible.
- **The deck list I was shown does not match the deck I own.** The shop's removal screen
  listed 26 cards and **neither Chained Reactions nor Quick Fuse was on it**, though I
  had taken Chained Reactions as a reward and bought Quick Fuse minutes earlier. Either
  the removal screen filters (bought-this-visit? Powers?) or it is stale. Two Powder
  Charges *did* show, one of which I had just bought — so it is not simply "purchases
  don't appear". I cannot resolve this blind; flagging it.
- **`Study — Obtain a random Power` never printed what I obtained.** The event went
  straight to Proceed. I finished the round not knowing one card in my own deck.
- **The Crystal Sphere's "Divine" and "Debt" are undefined.** The event asks you to
  spend 98 gold or take a permanent penalty for a word that appears nowhere on the
  screen and in no glossary block.
- **The glossary printed the wrong keyword.** On that same Crystal Sphere screen, the
  "Words on this screen" block contained exactly one entry: **"Plan — On the
  Bake-Kurage, paid now; next turn: front enemy, or ALL if it says so; never a Minion.
  Vulnerable counts; your Weak does not."** Nothing on that screen says Plan,
  Bake-Kurage, or Minion — that is a Kokomi keyword surfacing in a Klee run, while the
  two words the screen actually needed defined were absent.
- **Reward names arrive without text.** "Duplicator" was listed as a bare name among
  gold and card rewards; only the acceptance line revealed it was a potion.
- **The blocker itself:** `TOOL-BLOCKED: crystal_sphere — a minigame with a click-a-cell
  interface; the command grammar has no shape for it`. An Unknown node can therefore
  end a seat's round at any point, and it charged me 98 gold on the way in.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** `Defend`. Five Toasty Mittens prompts, and it was the answer to four
  of them. `Careful Now` is the near-miss — I drew it twice and it was worth 0 Block
  both times.
- **Happiest to draw:** `Jumpy Dumpty+`. Bomb 11 that pays out a **Mine 4 on ALL
  enemies** when it goes off is two cards' worth of effect, it scales in both directions
  (it's the biggest charge for The Big One *and* the widest spread against capped
  enemies), and the Mines turn the enemy's own intent into damage. Duplicating it was the
  turn I enjoyed most. `The Big One` is the more spectacular card but it only asks one
  question; Jumpy Dumpty+ asks several.

**(e) Did the first turn of the first fight already present a decision?**

**Yes — and a sharp one.** The three Exoskeletons printed `Hard To Kill 9` before I
played a card, which inverted the plan my hand was built for (Jumpy Dumpty+'s Bomb 11
was already 2 points of waste), and the Mine-on-attacker rule meant I had to read three
intent lines to decide which enemy to hand-detonate and which to let kill itself. I
finished turn 1 having made two decisions I could defend and one enemy effectively dead.

The caveat: that decision was handed to me by the *enemy's* text, not by Klee's. Against
the single capless Tunneler, turn 1 was much closer to automatic — place what you can,
sequence the set-off card first, take the hit.

---

## Non-blindness declaration

**Repo files read: none.**

Every game action was one of the two allowed forms,
`GITS_LANE=1 python -m understudy.blindplay observe` and
`GITS_LANE=1 python -m understudy.blindplay act "<command>"`, run through the Bash tool
from `C:\Users\Monty\Documents\GitHub\GItS`. I ran no other understudy subcommand — no
`harness state`, `scenario`, `staged_turn`, or `soak`.

Commands and tools used outside those two:

- **Bash**, for scratch bookkeeping only, all inside the session scratchpad at
  `...\scratchpad\klee-r10-run3\`: one `mkdir -p`, one `echo > count.txt`, one `cat` of
  that file, and repeated `echo "<n>" >> log.txt` appended to the same Bash lines as my
  `act` calls, to keep the running count of accepted actions.
- **Bash**, for shaping the bridge's own output only: `sed -n '<range>p'` and `head`/
  `tail` piped from `observe` and from `act`, to re-read one block of a screen I had
  already been shown. No file was ever read this way.
- **Bash**, one `for` loop over a list of `act` commands, to issue several accepted
  commands in one call.
- **Write**, once, for this record.

No repo file, YAML sheet, C# source, doc, packet, or other seat's record was opened at
any point.
