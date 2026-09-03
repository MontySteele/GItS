# Klee round 10, run 1, act 2 — blind seat record

## Identity

- **Model / seat:** Opus, blind TESTER seat, KLEEMOD-KLEE, lane 1.
- **Run seed:** not printed on any screen I saw. The bridge never prints a seed.
- **Character:** Klee.
- **Act:** 2. **Boss named at the top of the act map:** *The Insatiable* — I never
  reached it.
- **Actions accepted:** 98 `act` calls (cap was 250).
- **Termination reason:** **not a budget.** The run ended in death. My last
  `end turn` in fight 4 returned:

  ```
  TOOL-BLOCKED: game_over

  the run is over; there is nothing left to play

  The run ended on floor 25.
  ```

  Per the brief I stopped there. The lane is **not** on the act-3 map; the act-2
  boss was never fought.
- **HP trajectory:** 62/62 at the act-2 start → 43 after fight 1 → 29 after
  fight 2 → **3** after fight 3 → 21 after the rest site → 14 → 9 → dead in
  fight 4. I was at or under 30 HP for the entire second half of the act.
- **Gold:** **I never once saw my gold total.** No screen printed it — not the
  map, not the events, not combat, not the rest site. I gained 13 + 19 + 12 = 44
  across three fights and paid 125 at the Zen Weaver. I inferred I could afford
  the 125 only because a *third* option on that screen was flagged
  `**Locked** (not available) — Not enough Gold` and the one I wanted was not.
- **Potions held at the end:** none. I started the act with a Colorless Potion
  (inherited) and picked up a Duplicator; both were spent in fights 3 and 4.
- **Relics at the end:** Pounding Surprise, Arcane Scroll, Ripple Basin, Dolly's
  Mirror, Tingsha, Pael's Growth.
- **Deck at the end (24):** 4× Strike (one carrying `Slither`), 4× Defend,
  2× Jumpy Dumpty+, Ka-pow!, Sparks 'n' Splash+ (Clone), Fwoosh!, Perfect
  Timing, Coven Errand, Fish-Flavored Bait, Dig In, Amber — Fiery Rain,
  Noelle — I Got Your Back, Chained Reactions, Rapid Fire, Quick Fuse,
  Exterminate, Big Badda Boom. (A `Clumsy` curse was added to me mid-run and I
  paid to remove it.)

**Neow pick: none, inherited.** This was the second of two chained seats; the
previous seat cleared act 1 at 10 of 62 and made the Neow pick. I began on the
act-2 map with its deck, relics and potion.

---

## Fight 1 — Thieving Hopper, HP 79/79

Escape Artist 5 (*"Tries to escape the combat after 5 turns"*), so this was a
5-turn kill clock, not a fight. It also carried `Flutter 5 — Receives 50% less
damage from Attacks. Deal attack damage 5 times to Stun it.`

**Turn 1** — played Chained Reactions, Perfect Timing, Strike, Ka-pow!, Dig In.
My whole hand was playable: three cards at 1 energy, Ka-pow! at 0, and Dig In
priced in Sparks rather than energy. *Rejected:* nothing, and that is the
finding — there was no decision here. Every card in hand could be played, so
"which do I cut" never arose. The only judgement was that Chained Reactions and
the two Set-off cards were dead on an enemy with no Bombs, and I played them
anyway because the energy had no other home. Dealt 18 (79 → 61).

**Turn 2** — played Jumpy Dumpty+ (Bomb 11), Sparks 'n' Splash+, Fish-Flavored
Bait. *Rejected:* Defend, because the printed intent was `Empower (Buff)` and
not an attack, so 5 Block would have expired unused. *Rejected:* Strike (6 flat)
in favour of Fish-Flavored Bait (4 damage **and** a Bomb 4), because Bombs
"grow 4 a turn" and a growing 4 outruns a flat 6 over a 5-turn clock. This was a
real choice. Enemy to 46.

**Turn 3** — played Jumpy Dumpty+ (a second Bomb 11), Defend, Defend.
*Rejected:* Strike, which had been enchanted with `Slither — When you draw this
card, randomize its cost from 0 to 3` and had rolled **cost 2** that turn, for 6
damage that `Flutter` would halve to 3. Paying 2 energy for 3 damage against
21 incoming was obviously worse than 10 Block. *Rejected:* Coven Errand
(Bomb 5), because Sparks 'n' Splash+ reads only the **largest** Bomb and a
Bomb 5 would not have raised it above the existing 15. That distinction —
between cards that raise my *largest* bomb and cards that raise my *total* —
was the sharpest read of the fight.

**Turn 4** — played Amber — Fiery Rain, Noelle — I Got Your Back, Defend.
I worked out I could reach at most 28 damage against 31 HP, so the kill was
not available; *rejected:* Strike, taking 11 Block instead of 3 post-Flutter
damage, because the end-of-turn Sparks tick would finish the job next turn
regardless. Enemy to 6.

**Turn 5** — enemy at 6 HP with intent `Cowardly (Escape)` and
`Escape Artist 1 — Tries to escape the combat this turn`. Played Fwoosh!, which
costs 1 Spark and no energy. Its Set off detonated `Bomb 58` and the fight ended
instantly. *Rejected:* waiting for the end-of-turn Sparks tick, which would also
have killed it — I took the certain line because the enemy was leaving.

**Where the screen and the outcome agreed and disagreed.** Agreed, mostly, and
the Bomb badge was excellent: `Bomb 58 (buff) — Set off here deals 58 Pyro
damage. Bombs here: 3.` told me exactly what a detonation was worth. The
disagreement was structural rather than numeric: I sat on a 46-, then 58-point
Bomb for **two consecutive turns** with no Set-off card in hand. The deck holds
only three detonators (Ka-pow!, Fwoosh!, Perfect Timing) and one of those is
priced in Sparks I did not have, because `Pounding Surprise` only grants Sparks
when a Bomb goes off — which needs a detonator. That circularity is the fight's
real finding.

---

## Fight 2 — Exoskeleton ×3, HP 28/28, 25/25, 26/26

Every one carried `Hard To Kill 9 — Reduce all damage taken and HP lost by
Exoskeleton to 9`. **This was the best fight of the round.**

**Turn 1** — played Chained Reactions, Sparks 'n' Splash+, Jumpy Dumpty+ on
Exoskeleton (2), then Ka-pow! on Exoskeleton (2).

The decision: the Bomb keyword prints *"only their Vulnerable and a cap move
it"*, and here the cap was 9. My Bomb 11 was **already over the cap**, so
letting it grow — the entire premise of the archetype — was worth nothing.
Detonating immediately became correct, which is the exact inverse of the fight-1
logic. *Rejected:* holding Ka-pow! (it has `Retain`, so holding is normally
free) and banking the Bomb, which would have thrown away 6 damage to no purpose.
*Rejected also:* Fish-Flavored Bait, for want of energy.

Second read in the same turn: Set off resolves *"one at a time, each a Pyro hit
for its size"*, so three Bombs of 7 are three uncapped hits while one Bomb of 21
is a single hit capped to 9. **Bomb count beats bomb size against a cap.** That
made Chained Reactions — normally a slow engine — the best card in the deck for
this fight. Exoskeleton (2) to 12; Jumpy Dumpty's rider seeded a Mine 4 on all
three.

I want to record how well this read: after the detonation the badges printed
`Bomb 4 (buff) — Set off here deals 4 Pyro damage **capped by Hard To Kill**.
Bombs here: 1, including 1 Mine.` The screen named the interaction out loud. I
did not have to guess.

**Turn 2** — played Perfect Timing on Exoskeleton (3), Strike on Exoskeleton
(2), Defend. Exoskeleton (3) was showing `Bomb 22 … Bombs here: 3` against 26
HP; because those were three separate sub-cap hits I predicted 22 + 8 = 30 and a
kill, and got it. *Rejected:* dumping Perfect Timing into the wounded
Exoskeleton (2) at 4 HP, which a Strike could finish for a third of the cost —
and *rejected* Coven Errand, because a fourth small Bomb was worth less than 5
Block with 18 incoming.

**Turn 3** — one Exoskeleton left at 17 HP holding `Bomb 30 … Bombs here: 4`,
and I was sitting on **7 Sparks** because Pounding Surprise had been paying out
on every detonation. Played Fwoosh! for 1 Spark and 0 energy; the four
sub-cap detonations ended the fight without my spending a single point of
energy. *Rejected:* Strike/Defend, irrelevant once the kill was free.

Won on turn 3 having lost 14 HP. The Spark economy inverted completely between
fight 1 (0 Sparks, Fwoosh! uncastable) and here (7 Sparks, kills for free).

---

## Fight 3 — Chomper ×2, HP 63/63 and 60/60

123 enemy HP; I entered at 29/62. Both printed `Artifact 2 — Negates 2 debuffs`.

**Turn 1** — played Coven Errand and Fish-Flavored Bait onto Chomper (1), then
Noelle — I Got Your Back. *Rejected:* the pure-defensive line of playing only
non-Attacks to collect `Ripple Basin — If you did not play any Attacks during
your turn, gain 4 Block`. That would have been 10 Block instead of 6, but cost
me a Bomb 4 that grows every turn; over a fight this long the growing Bomb wins.
Took 10, to 19.

**Turn 2** — the pivotal turn, and the one real decision of the round.

I drew no Block card at all: Rapid Fire, Fwoosh!, Strike, Exterminate, Jumpy
Dumpty+. 16 damage was incoming onto 19 HP. I spent the Colorless Potion here
rather than hoarding it, on the reasoning that a potion used while I still had
margin beats one used at 3 HP.

It offered Rolling Boulder, Dark Shackles and Catastrophe. **Dark Shackles
(*"Enemy loses 9 Strength this turn"*) would have zeroed the entire 8×2 attack
and saved my whole turn — and it would have done nothing**, because both
Chompers print `Artifact 2 — Negates 2 debuffs` and Shackles is a debuff. That
catch came straight off the enemy panel, and it is the single best piece of
printed-text-to-decision transfer in the round. Took Rolling Boulder instead,
which the potion made free (it displayed at `cost 0` afterwards), keeping all 3
energy.

Then: Rolling Boulder, Jumpy Dumpty+ on Chomper (1), Fwoosh! on Chomper (1)
(1 Spark, no energy), Exterminate, Strike. I predicted 52 damage onto Chomper
(1) and got exactly that — 59 → 7. *Rejected:* the Ripple Basin line again
(4 Block for 52 damage), and *rejected* Rapid Fire (12 for 2 energy) in favour
of Exterminate + Strike (18 for 2). Took 16, to **3 HP**.

Recording the part that made me look stupid: I made that trade knowing it put me
at 3, on the argument that 4 extra Block would not change whether I survived the
*following* turn. That was correct as far as it went, but it left me with zero
margin for the rest of the act, and I never got the HP back.

**Turn 3** — Chomper (1) at 2 HP was the only attacker (16 damage); Chomper (2)
was on `Strategic (StatusCard)`. So killing the 2 HP body meant taking **zero**.
Played Quick Fuse on it — priced in Sparks, so the kill cost no energy at all —
then spent the full 3 energy on the survivor: Amber — Fiery Rain, Strike,
Strike. *Rejected:* leading with Amber, which would also have killed Chomper (1)
with its first 4-damage tick and dealt 6 more to Chomper (2); at 3 HP I paid 6
damage for a guaranteed single-target kill rather than trust hit-ordering. I
would make that trade again. *Rejected:* Defend, pointless once nothing could
attack.

**Turn 4** — Chomper at 5 HP, attacking for 16, me at 3. My hand held exactly 4
damage (Ka-pow!) — not enough to kill — and three Block cards. So I played
Dig In, Defend, Defend and **Chained Reactions**, deliberately playing *no*
Attacks: powers are not Attacks, so Ripple Basin still paid. 18 Block on the
panel plus the Ripple bonus, against 16. *Rejected:* Ka-pow! for 4 damage, which
would have left the Chomper at 1 HP and cost me the 4 Ripple Block — and it was
unnecessary, because Rolling Boulder was going to tick 15 at the start of my
next turn and kill it outright. It did; the fight ended on the block.

Survived at 3 HP. Rolling Boulder — a potion card, not a Klee card — did the
majority of the work in this fight.

---

## Fight 4 — Hunter Killer, HP 121/121 (the one that killed me)

Entered at 21/62 after resting. 121 HP against a deck that had never once dealt
more than ~52 in a turn.

**Turn 1** — intent was `Strategic (Debuff)`, so Block would expire unused.
Played Exterminate and Strike for 18. *Rejected:* both Defends (no incoming
damage), and *rejected* Fwoosh! — with no Bomb on the field its Set off was
dead and it would have burned my only Spark, which I wanted banked for Dig In as
an emergency 8 Block at zero energy. I left 1 energy unspent, which nothing in
hand could use.

**Turn 2** — the debuff landed: `Tender 0 (debuff) — Whenever you play a card,
lose 1 Strength and 1 Dexterity this turn.` A tax on *card count*, which cuts
directly against a deck that wants to chain four or five cheap cards a turn.
Played Noelle then Coven Errand — both skills, so Ripple Basin still paid — and
*rejected* Big Badda Boom, my new payoff card, because with only a Bomb 5 on
the field it would have been 12 damage for 2 energy and wasted the card that
doubles bomb damage. Took 7, to 14.

**Turn 3** — 21 incoming (`7 damage 3 times`) onto 14 HP. Used Duplicator
(*"This turn, your next card is played an extra time"*) on **Defend**, not on a
damage card, specifically because Tender charges per card *played* and the
duplicate appeared to be the cheaper way to buy Block. Then Defend, then Jumpy
Dumpty+. Ended on 12 Block, `Tender 4`, `Strength -4`. *Rejected:* Duplicator on
Jumpy Dumpty+ for a Bomb 31 race — I ran that line and it put me at 3 HP with
the enemy still above 100, which is not a race, it is a slower death. Took 9,
to 9.

**Turn 4** — 21 incoming onto 9 HP, and my hand held exactly one Block card
(Dig In, 8). I did the arithmetic on the screen: 8 Block plus Ripple Basin's 4
is 12, against 21, is 9 through, against 9 HP — **exactly lethal, with the best
possible line**. There was no configuration of that hand that lived. I played
Dig In alone and no Attacks, because the max-Block line was the only one with
any survival chance at all, and ended the turn. The run ended.

*Rejected:* detonating `Bomb 28` with Ka-pow! for 32 damage. It was free (0
energy) and it was the biggest number available to me, and I turned it down
because it would have cost Ripple Basin's 4 Block and the enemy would still
have been above 70. I would rather have died at maximum Block than at maximum
damage. That is the last real decision of the run, and I stand by it, but I
note it produced a turn where my most exciting card was correctly unplayable.

---

## The kit, after 4 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Three, and two of them were excellent.

1. **`Hard To Kill 9` versus the Bomb archetype (fight 2).** The cap inverted
   every instinct the kit had taught me. Bombs normally reward patience — "grows
   4 a turn" — but a Bomb already over the cap gains nothing by growing, so the
   correct play became *detonate immediately*, and *many small bombs beat one
   large one* because Set off resolves each Bomb as its own hit. That is a
   genuine, legible, text-derived reversal, and it made Chained Reactions
   (a card I had written off as a slow engine) into the best card in the deck
   for one fight. This is the kit at its best.
2. **`Artifact 2` versus Dark Shackles (fight 3).** Reading the enemy panel
   turned a tempting potion card into an obvious trap. Nothing about it was
   Klee-specific, but it was a real decision the screen fully supported.
3. **"Largest Bomb" versus "total Bomb" (fight 1, turn 3).** Sparks 'n' Splash+
   reads only the largest Bomb; Set off consumes all of them. So a small Bomb
   raises my detonation but not my per-turn tick, and detonating collapses the
   tick to near zero. Cards that grow one big Bomb and cards that add many
   small ones are genuinely different, and choosing between Coven Errand and
   Jumpy Dumpty+ meant something. This tension is good and I do not think it is
   surfaced anywhere except by working it out.

Underneath all three sat the resource that actually generated decisions: **the
Spark economy**. Spark-priced cards cost no energy, so Fwoosh!, Quick Fuse and
Dig In are free actions *if* you have Sparks — and Pounding Surprise only pays
Sparks when a Bomb goes off, which needs a detonator. In fight 1 I had 0 Sparks
and Fwoosh! sat uncastable for four turns; in fight 2 I had 7 and killed things
for free. That swing is dramatic and I liked it, but see (c).

**(b) What felt automatic, and what never seemed worth playing.**

Fight 1 turn 1 was fully automatic — see (e). More broadly, the deck's floor is
too wide: with almost everything costing 1 and 3 energy a turn, most turns were
"play three of the four things I can afford", and the cut was usually a Strike
or a Defend rather than a decision between two Klee cards.

Never worth playing: **Strike**, always, in every fight. 6 damage in a deck
whose bombs do 20–50 in a hit, halved to 3 by `Flutter`, and the copy carrying
`Slither` rolled cost 2 and cost 3 on me. Four of them survived to the end of
the run. **Defend** was necessary but never interesting — Dig In (8 Block for a
Spark and no energy) strictly outclasses it whenever Sparks exist.

Also effectively dead: the entire **Elemental Reaction** subsystem. Every
`observe` printed roughly ten lines of glossary for Melt, Vaporize, Overloaded,
Superconduct, Electro-Charged and Frozen — including a long paragraph about a
reaction that "looks as though it did not happen". **I triggered zero reactions
across four fights**, because every card in Klee's deck is Pyro and a Pyro hit
on a Pyro aura only refreshes it. Perfect Timing's *"If a Bomb triggered an
Elemental Reaction this turn, play this again"* and Sizzle+'s equivalent rider
are, in a mono-Pyro deck, unreadable text on a card that never does it. The two
cards that would have unlocked it (Razor, Fischl) were offered as card rewards
and I passed on both — correctly, I think, on raw power, which is itself the
problem.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **`Clone` — the worst legibility failure of the round.** The Ancient offered
   *"Pael's Growth — Enchant a card with Clone"*. I picked Sparks 'n' Splash+,
   and the confirm screen showed me:

   ```
   ## What you have picked
   - **Sparks 'n' Splash+ (1)** (upgraded) — cost 1, power — PICKED
   - **Sparks 'n' Splash+ (2)** (upgraded) (Clone) — cost 1, power — PICKED
   ```

   Two rows, both PICKED, one tagged Clone. I read that as "you now have two
   copies" and confirmed on that basis — that was the entire reason I chose to
   enchant a *power* rather than Jumpy Dumpty+. It was wrong. The keyword, which
   I only saw a fight later when the card reached my hand, reads
   *`Clone` — This card can be duplicated at Rest Sites.* The removal screen
   confirmed a single copy in the deck. So the enchant does not duplicate
   anything; it grants the *option* to duplicate, later, by spending a rest-site
   action. **The preview screen shows the outcome of a future choice as though
   it had already happened.**
2. **And the payoff never arrived**, which compounds it. The one rest site I
   reached offered `Rest / Smith / Clone` as mutually exclusive options while I
   was on **3 of 62 HP**. Claiming the Clone I had paid an Ancient for would
   have meant declining an 18-point heal at 3 HP. The enchant was dead on
   arrival from the moment I took chip damage.
3. **The Bugslayer event printed no card text at all.** It offered
   *"Learn Extermination Technique — Add Exterminate to your Deck"* and
   *"Learn Squash Technique — Add Squash to your Deck"*, with no rules text for
   either card, no cost, no type, and **no option to decline**. Every other
   choice screen in the game prints the full card. I picked Exterminate off the
   name alone. It turned out to be excellent (`cost 1 — Deal 3 damage to ALL
   enemies 4 times`) and I still consider the screen a defect: I had no way to
   know that, and I was forced to add *something*.
4. **Gold is never printed anywhere.** I spent 125 at the Zen Weaver without
   ever seeing a balance, inferring affordability only from which row was
   flagged `Locked`. That screen also had no leave option.
5. **Power numbers that are not stacks.** `Chained Reactions 3` is the *size of
   the Bomb it places*, not three stacks. `Sparks 'n' Splash 1` is presumably
   one copy. `Tender 0` displays a zero for a debuff that was very much active.
   The page's own footnote concedes it: *"A power's number is what the game's
   data feed reports for it… unless a power's own text says when it ends, this
   page cannot say either."* In practice I learned to ignore the numbers on
   powers entirely, which means they are noise.
6. **A redaction I could not resolve.** Claiming the fight-1 reward
   *"Take your stolen card back"* returned
   `(the game answered with something this tool will not repeat)`. I never
   learned which card came back. Four Strikes appeared in a deck that started
   with three, so I assume a Strike, but I am guessing.

Against all of that, the things that read *beautifully* and deserve saying:
Quick Fuse refusing itself with `CANNOT BE PLAYED: no enemy is holding a Bomb`;
the Bomb badge printing `capped by Hard To Kill` the moment a cap existed; and
Sparks 'n' Splash+ explaining its own discount — *"The cost printed on this card
is 2; it is showing 1 here, because this copy is upgraded — that is permanent."*
That last one answered a question before I could ask it.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Strike**, and its `Slither` copy most of all — a 6-damage card
in a deck built around 30-point detonations, whose enchanted copy randomises to
cost 3 and clogs the hand. I removed a Clumsy curse rather than a Strike at the
Zen Weaver and I am no longer sure that was right.

Happiest to draw: **Quick Fuse**, and it is worth saying why, because it is not
the flashiest card. It costs a Spark rather than energy, which means on the turn
that mattered most — fight 3, 3 HP, one attacker at 2 HP and a 39 HP enemy
behind it — it killed the thing that was about to kill me *for zero energy*, and
left my entire turn intact to spend on the survivor. Cards that are free in the
resource you are short of are the ones that make turns feel clever.

Honourable mention to **Big Badda Boom** (*"Set off. Deal 12 damage. Then deal
damage equal to what the Bombs dealt"*), which I took as the archetype's payoff
and then **never once got to play** across two fights — see (e) and the pattern
below.

**(e) Did the first turn of the first fight already present a decision?**

**No.** My opening hand was Perfect Timing, Strike, Chained Reactions, Ka-pow!
and Dig In, against 3 energy. Ka-pow! costs 0, Dig In is priced in Sparks rather
than energy, and the remaining three cost 1 each — so I played **my entire
hand** and never chose anything. There was no rejected alternative to record.
The only reasoning available was noticing that two Set-off cards and Chained
Reactions were all dead against an enemy with no Bombs, and playing them anyway
because the energy had nowhere else to go.

That is the structural note I would most want acted on. The kit's whole identity
is a delayed payoff — place Bombs, let them grow, detonate — and turn one of a
fight is the moment when that engine is emptiest, so the opening turn is
reliably the least interesting turn of the fight. It got interesting on turn 3.

**The pattern that killed the run.** In fight 1 I sat on a 46- and then
58-point Bomb for two consecutive turns with no detonator in hand. In fight 4 I
died holding `Bomb 28` and never drew Big Badda Boom. The deck carries a large
majority of Bomb-placers and Blocks against a handful of Set-off cards, and it
cannot reliably assemble the two halves of its own combo. I bought Rapid Fire
and Quick Fuse specifically to fix that, and it was still the proximate cause of
death. Meanwhile the fight I won most comfortably (fight 2) I won partly with
Rolling Boulder — a potion card from another character's list. The kit's best
turns in this round came from an enemy modifier that inverted its rules and from
a card that is not Klee's.

---

## Non-blindness declaration

Commands run outside the two allowed forms, in full:

- `mkdir -p ".../scratchpad"` — once, to create the scratch directory.
- `echo "count=N" > ".../klee-act2-count.txt"` — repeatedly, to keep the running
  count of accepted `act` calls required by the brief. Also `cat` on that file
  once, immediately after creating it.
- `GITS_LANE=1 python -m understudy.blindplay observe` piped through `sed -n`
  and `grep -n` — used throughout to re-read one block of the screen (hand,
  enemy panel, header) instead of reprinting the whole page. These are filters
  over the allowed `observe` output and revealed nothing `observe` did not
  already print. One such `sed` range matched nothing and returned empty, which
  is why a `grep` for `picked|confirm` follows it.

Tools used: **Bash** (for everything above and for both allowed commands) and
**Write** (once, for this record, as permitted).

I ran no `harness state`, no `scenario`, no `staged_turn`, no `soak`, and no
other understudy subcommand.

**Repo files read: none.**
