# Klee — blind seat, round 12, act 1

## Identity

- **Model / seat:** Opus (Claude), blind TESTER seat. The kit's author is a
  different Claude model; I have never seen this kit and read no repo file.
- **Lane:** 1 (port 15527), stamp 20260904-145703.
- **Run seed:** JNPWLQR7U532 (read back off the wire).
- **Character:** Klee (KLEEMOD-KLEE). **Ascension:** 0.
- **Act:** 1. The map named the act boss: **Ceremonial Beast**. I did not reach
  it — the act is 16 floors and I stopped on floor 10.
- **Actions accepted:** 120 (the cap). One further command was **refused**
  (`play "Spoils Map"` — see Fight 5, turn 3); refusals do not count.
- **Termination reason:** the action budget, exactly. The 120th accepted act
  was opening the post-fight card reward on floor 10. Wall clock was not close
  to 5400 s. No act-2 record is owed, because the act-1 boss was never reached.
- **HP trajectory:** 62/62 → 55 (fight 1) → 53 → 48 (fight 3) → **18** (elite,
  low point) → rest to 36 → 54 (event heal) → **39/62** at the stop.
- **Gold:** 111 (I declined the last 14).
- **Potions held:** none. I held Gigantification Potion from floor 4 and spent
  it on floor 10; the Fire Potion on the final reward screen was never claimed.
- **Relics at the end:** Pounding Surprise (starter — *whenever a Bomb goes
  off, gain 1 Spark*), Silver Crucible (all three charges spent), Lantern (elite
  drop — it printed no text I ever saw, but combat opened at **Energy 4/3**
  after I took it, so I inferred +1 energy on turn one), Spoils Map (event).
- **Deck at the end (16 cards + 1 quest card):** Strike ×4, Defend ×4,
  Ka-pow!, Jumpy Dumpty+, Tinder Toss+, Mine Toss, Ammo Scavenging,
  Perfect Timing+ ×2, Barbara — Front Row Seat; plus Spoils Map (quest,
  unplayable, sits in hand).

**Neow pick: Silver Crucible** ("The first 3 card rewards you see are Upgraded.
The first Treasure Chest you open is empty.") — I took it because as a blind
seat I wanted to read the kit's cards at their strongest printing, and three
upgraded rewards is the largest early swing on offer; the empty chest is a cost
paid ten floors later, which it duly was (floor 9's chest printed "nothing here
to take", exactly as advertised).

---

## Fight 1 — Shrinker Beetle, HP 38/38 (floor 1)

Opening hand: Strike, Defend ×3, Ka-pow!. Spark 1. Energy 3.

**Turn 1.** Intent was "Strategic (DebuffStrong) — intends to apply a Debuff",
i.e. no damage. Played **Strike** (6), then **Ka-pow!** (cost 0, *Retain. Set
off. Deal 4 damage.*). *Rejected:* all three Defends — with a pure-debuff intent
printed, 5 Block is provably zero value, so the "decision" collapsed to "spend
the two cards that do anything". I ordered Strike before Ka-pow! deliberately so
the Pyro aura Ka-pow! applies would still be standing at end of turn; that was
the only real choice on the turn and it was worth ~0.

The debuff landed as **Shrink -1 — "While Shrinker Beetle is alive, your Attacks
deal 30% less damage."** This is the single best legibility moment of the run:
on the next screen Strike's own text read **"Deal 4 damage"** and Ka-pow!'s read
**"Deal 2 damage"**. The card printed the number I was actually going to get.

**Turn 2.** Bomb-less. Played **Jumpy Dumpty** (*Place a Bomb 8. When it goes
off, place a Mine 3 on ALL enemies.*) then Strike ×2 (8 damage after Shrink).
*Rejected:* three Strikes for 12 now. I took the bomb because the draw pile was
empty and the five discarded cards included Ka-pow!, so a Set off next turn was
guaranteed, and a Bomb 8 becomes a Bomb 12 by then — 12 beats 4. That is a real
decision and the screens gave me everything I needed to make it (pile counts
printed, bomb growth printed on the keyword).

**Turn 3.** Bomb read **"Bomb 12 — Set off here deals 12 Pyro damage."** Played
**Ka-pow!** (12 + 2 = 14), then Strike ×2 to finish. *Rejected:* holding
Ka-pow! another turn for a Bomb 16 — the enemy's printed intent was 13 damage,
so another turn cost more HP than the bomb gained. Kill. The screen and the
outcome agreed exactly.

Reward: **Tinder Toss+** over Explosives Workshop+, Catalytic Converter+ and
Bennett — Fantastic Voyage+. I picked it because it is a *second* Set off and
its price is 1 Spark rather than Energy, and my only Spark source is a relic
that pays out **when a bomb goes off** — so a card that sets off bombs partly
refunds its own price. That reasoning turned out to be exactly right and it is
the most elegant thing in the kit.

## Fight 2 — Nibbit, HP 45/45 (floor 3, after the shop)

Shop on floor 2: bought **Mine Toss** (24g) and **Ammo Scavenging** (51g) of
112 gold. I bought both because after fight 1 my deck had three Set off effects
and exactly **one** bomb source; the shelf priced bomb sources cheaply and
detonators dearly, which reads as the designer knowing which half is scarce.
*Rejected:* Flame Dance (76g, "Set off each enemy whose aura is not Pyro") —
my own bombs are Pyro hits that leave Pyro auras, so the card disables itself
after one detonation. I could not tell from the shelf whether that was a
drawback or a trap, and would not pay 76 gold to find out.

**Turn 1.** Played **Jumpy Dumpty** (Bomb 8) + **Defend ×2**. *Rejected:*
Jumpy + Strike ×2 for 12 damage while eating the printed 12. 10 Block against a
printed 12 was worth more than 12 damage against 45 HP, because the bomb was
going to do the damage instead. Took 2.

**Turn 2 — the turn the kit is for.** Bomb 12 on the board, hand held Mine Toss
and Tinder Toss+. Sequenced:
1. **Mine Toss** (Mine 4 on ALL) — placed *before* the detonator, so it would
   be caught in the same Set off.
2. **Tinder Toss+** (1 Spark) — *Set off and deal 6 damage to a random enemy
   twice.* First half set off Bomb 12 **and** Mine 4; Jumpy Dumpty's rider then
   dropped a fresh **Mine 3**, which the *second* half of the same card set off.
3. Strike, Defend with the leftover energy.

45 → 8 with 5 Block up, and **Spark went 1 → 3**: I spent one and the relic
paid three back, one per bomb. *Rejected:* holding a turn to let the bomb grow
to 16 — the four-detonation chain was worth more than 4 extra bomb size, and I
could see it would be because every number was printed. This was the best turn
of the run and it was entirely my construction: place, then chain, then let the
relic refill the resource I spent.

**Turn 3.** Ka-pow! + Strike ×2 through 5 Block. *Rejected:* nothing —
lethal was arithmetic.

Reward: **Perfect Timing+** over Bang Bang!+, Quick Fuse+ and Freminet. Bang
Bang!+ (2 Sparks, Set off, 11 damage, *place a Bomb 6*) is the better card in a
built deck; I took Perfect Timing+ because at that point my Spark income was one
relic trigger and a 2-Spark card is uncastable on turn one, whereas 1 Energy for
"Set off, deal 11" is never dead. That is a genuine resource-curve decision and
I enjoyed having to make it.

## Fight 3 — Fuzzy Wurm Crawler, HP 57/57 (floor 4)

**Turn 1.** Ammo Scavenging (Bomb 4) + Strike ×2. **Retained Ka-pow!.**
*Rejected:* playing Ka-pow! for 4 free damage. Retain is what makes that a
choice: Ka-pow! is the only card in the deck that can be *saved*, so every turn
asks "4 damage now, or a guaranteed detonator on the turn the bombs are big".
That question came up in every fight and I never answered it the same way twice.

**Turn 2.** Enemy intent was Buff — no incoming. Played **Jumpy Dumpty** (second
Bomb 8) and one Strike, and deliberately **left one energy unspent** because the
only cards left were Defends and Block against a Buff intent is nothing.
*Rejected:* Defending anyway. Worth flagging: with 6 cards in hand and 3 energy
I had a turn where the correct play used two cards and burned a third of my
energy on purpose, because Klee's basic Defends have no bomb interaction at all.

**Turn 3.** Two bombs, 24 total. **Mine Toss** first (three bombs, 28), then
**Perfect Timing+** — Set off 28 + 11 = 39, exactly the enemy's remaining 39.
*Rejected:* Ka-pow! as the detonator to save the energy — Perfect Timing+'s 11
was the margin, and I could read that it was, off the printed bomb total and the
printed HP.

Reward: second **Perfect Timing+** over Explosives Workshop+, Careful
Arrangement+ (*Move all your Bombs onto the enemy as one Bomb. It grows by 8.*)
and Bennett. Bennett's 3 Strength is a trap in this kit and the screen tells you
why if you read two keywords together: Strength "adds its amount to every Attack
hit", and Bomb is "**Not an Attack**". I was pleased that the answer was
derivable from printed text alone, and slightly worried that it requires the
player to cross-reference two glossary entries to see that a card in their
reward pool is nearly blank for them.

Floor 5, event **Aroma of Chaos**: took **Maintain Control** (upgrade a card)
over Let Go (transform a random card) and upgraded **Jumpy Dumpty → Jumpy
Dumpty+** (Bomb 8 → Bomb 11, Mine 3 → Mine 4). The upgrade-selection screen
previewed the upgraded text before I confirmed, which is good. It also printed
a "Not on this list, and why" block naming Tinder Toss+ and Perfect Timing+ with
"**nothing on the feed says why**" — the answer is obviously "already upgraded",
but the screen would not say so.

## Fight 4 (ELITE) — Phrog Parasite, HP 64/64, *Infested 4 — "Upon dying, summons... something."* (floor 6)

This fight is the whole round in one place: the best thing the kit did and the
worst thing that happened to me.

**Turn 1.** My hand was **Tinder Toss+, Ka-pow!, Perfect Timing+**, Defend,
Strike — *three Set off cards and not one bomb on the board*. All three
degraded to plain attacks. I played Perfect Timing+ (11), Tinder Toss+ (12),
Strike (6) for 29 and **retained Ka-pow!**. *Rejected:* holding Tinder Toss+ for
a bomb turn — I couldn't; only Ka-pow! Retains, everything else is discarded, so
"save the detonator" is not a legal move for two of my three detonators. That is
a real structural constraint and I think it is the kit's sharpest tension.

The enemy's printed intent was "give you 3 Status cards". It did. **I never saw
them arrive** — they were not in my hand, and the screen's pile counts moved
without ever naming what went in. They surfaced two turns later as
**Infection ×2** ("Unplayable. At the end of your turn, if this is in your Hand,
take 3 damage").

**Turn 2.** Ordering decision, and a good one: I played **Perfect Timing+
first** (nothing to set off, 11 damage) and **Mine Toss second**, so the Mine 4
would still be armed when the enemy attacked. *Rejected:* Mine Toss first, which
would have had Perfect Timing+ immediately blow up my own mine for 4. **Set off
is not optional**, so card order is a genuine puzzle every turn. The mine did
fire on the enemy's 4×4 attack for 4 free damage and 1 Spark.

**Turn 3.** Enemy at 20, doing statuses, so no defence needed: **Jumpy Dumpty+**
(Bomb 11) + **Ammo Scavenging** (Bomb 4) + Strike, retaining Ka-pow!.
*Rejected:* trying to kill through 20 with 16 of printed damage — it doesn't
reach, and killing was *not* obviously what I wanted anyway with "Upon dying,
summons... something" on the board.

**Turn 4 — the best moment in the run.** Bomb 23 across two bombs, enemy at 14.
Played **Ka-pow!** (0 cost). The bombs went off one at a time; the first killed
the Phrog; **Infested** summoned four Wrigglers (21/19/20/17); the *unspent*
second bomb obeyed "**A kill moves them to a survivor**" and landed on
Wriggler (2); and Jumpy Dumpty+'s rider then dropped a **Mine 4 on ALL** — onto
enemies that had not existed when I placed the bomb. One 0-cost card resolved
five different printed rules in the right order and every one of them was
readable on the next screen. I did not plan the summon interaction and it still
worked out coherently, which is the strongest thing I can say about a rules set.

**Turn 5.** All four stunned. Stacked **Jumpy Dumpty+** onto Wriggler (2) to
make a Bomb 23 on a 19 HP body, planning the kill to shunt the remainder along.
*Rejected:* spreading the bomb — stacking is better precisely *because* of the
"kills move it on" rule, so the rule creates the tactic.

**Turn 6.** **Mine Toss** (all four bombs on everything), then **Perfect
Timing+** on Wriggler (2) — Bomb 35 across four bombs killed a 19 HP enemy and
pushed the leftovers onward, ending with **Bomb 31 (4 bombs, 3 Mines)** on
Wriggler (1). Then, with one energy, I played Ammo Scavenging and **ended the
turn deliberately leaving three armed Mines on three enemies**, reasoning they
would fire for free when the enemies attacked.

**This is where the screen and the outcome disagreed, and it nearly killed me.**
I read *"A Mine ... also goes off when its enemy attacks you, **before the hit
lands**"* as meaning the mine is a pre-emptive interrupt — and, since a mine can
kill its host, that the hit might not land. It does not work that way. Five
bombs went off (Spark 4 → 9), the hosts survived, **and all of them hit me
anyway**; with two Infections also ticking I went **36 → 18 in one enemy
turn**, the worst swing of the run, on a turn I had planned as a free one. The
words "before the hit lands" are literally true and completely misleading about
what they buy you: they buy chip damage and Spark, not mitigation. If one line
in this kit should be rewritten, it is that one.

**Turn 7.** At 18 HP I stopped building and blocked: Strike to kill the 5 HP
Wriggler (moving its Bomb 19 along), Defend ×2. *Rejected:* the Gigantification
Potion for a 3× Strike to kill the 17 HP attacker — I chose to trust the block
maths, and it held exactly (0 damage taken). **Turn 8:** one Perfect Timing+ set
off Bomb 35 on the last 8 HP body. Elite cleared at 18/62.

Rewards: 42 gold, **Lantern**, and I took **Barbara — Front Row Seat**
(*Gain 5 Block. Apply Hydro twice. Whenever a Bomb goes off this turn, gain 3
Block.*) over Powder Charge, Chained Reactions and a downgraded Tinder Toss.
Two reasons: the elite had just shown me that this deck has no defensive floor
at all, and Barbara plants a **Hydro** aura that my own Pyro bombs can Vaporize
off. That was the only card all run that offered defence and offence in the same
sentence.

Floor 7 rest (18 → 36). Floor 8 event: took the Spoils Map for free. Floor 9
treasure: empty, as Silver Crucible promised. Floor 10 event **Dense
Vegetation**: chose "Rest — Heal 18 HP. Fight some enemies" over "75 Gold, lose
8 HP", because with ~20 actions left a fight was worth more to this record than
gold was.

## Fight 5 — four Wrigglers, HP 17/19/18/21 (floor 10)

Opened at **Energy 4/3** (Lantern).

**Turn 1 — the reaction test.** Played **Barbara — Front Row Seat** on
Wriggler (1): 5 Block, and the target came back reading **"Hydro Aura 2"**.
Then **Perfect Timing+** into it: **17 → 1**, i.e. 16 damage where the card
prints 11 — Vaporize's 1.5× exactly (11 × 1.5 = 16.5). The aura vanished and,
as the glossary warns, **no Pyro aura replaced it**. Everything the long
Elemental Reaction blurb promised, happened, and was checkable to the point.
Barbara also silently paid **+1 Spark** ("Sparks from your Companion"), which I
only noticed because I was watching the counter. *Rejected:* Perfect Timing+ on
the 21 HP body for raw tempo — setting up my own aura to eat it was worth 5
extra damage and taught me the mechanic in one turn.

**Turn 2.** **Mine Toss** (mines on all three survivors) then **Perfect Timing+**
on the 12 HP one: its Mine 4 went off first, then 11, for the kill. *Rejected:*
Tinder Toss+ despite having 2 Spark spare — its targeting is **random**, and
with mines armed on the two attackers a random Set off would have disarmed the
free damage I wanted the enemy turn to deliver. Random targeting turning a
strictly-positive card into a "maybe don't" is a nice piece of friction.

**Turn 3.** No detonator drawn. Tried **`play "Spoils Map"`** and was
**refused**: *"'Spoils Map' cannot be played right now: has unplayable keyword"*
— fair, and my mistake for not reading its type, though a 0-cost quest card
sitting in an already-cramped hand with no explanation of what it is *for* is
the one card all run whose purpose I never learned. Played Ammo Scavenging
(Bomb 8) and a Strike. *Rejected:* Defending against a printed Buff intent.

**Turn 4.** Both survivors printed 10 damage. Spent **Gigantification Potion**
then **Ka-pow!**: Set off 8 + a tripled 4 = 20, killing the 17 HP body outright.
Then Defend ×2 to eat the last attacker's 10. *Rejected:* saving the potion for
the boss — I was two floors from my action cap and a potion that dies unspent is
worth nothing. Note that the potion tripled only the card's own 4 damage, not
the 8 from the bomb: "the next **Attack** you play" and "a Bomb is **not an
Attack**" are consistent here, and I could predict it.

**Turn 5.** Strike ×2 into the last 9 HP Wriggler. No decision; three Strikes
and a Defend was the whole hand. Cleared at **39/62**.

I spent my 120th accepted action opening the reward screen (Mine Toss / Run
Away! / Pop! / Jean — Gale Blade) and stopped there without picking.

---

## The kit, after 5 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Four, and they recurred every fight:

1. **Detonate now, or let the bomb grow.** Bombs grow 4 a turn and only go off
   when Set off, so every turn prices "N damage now" against "N+4 next turn,
   minus one more enemy attack". Because both the bomb size and the enemy's
   intent number are printed, this is arithmetic I could actually do — which is
   what makes it a choice rather than a guess.
2. **Card ordering within the turn**, because *Set off is not optional*. Mine
   Toss before a detonator means the mine is caught in the blast; Mine Toss
   after means it stays armed. I made that call, in one direction or the other,
   on at least six turns. This is the best thing in the design.
3. **Retain Ka-pow!, or take the 4 damage.** Ka-pow! is the only card that can
   be banked, so it is the only guaranteed detonator for a turn you are still
   building toward. Every "free" 0-cost play was a real cost.
4. **Which resource to spend.** Energy, Spark and HP are genuinely separate
   pools, and Spark's only real income is *bombs going off* — so Spark cards
   are cheap exactly when the deck is working and uncastable when it isn't.
   Tinder Toss+ refunding its own price out of Pounding Surprise is the single
   most satisfying loop I found.

**(b) What felt automatic, and what never seemed worth playing.**

**Strike and Defend.** Four of each, one third of the deck, and they interact
with nothing — no bomb, no Spark, no aura, no Set off. Whenever they were the
answer, the turn had no content: Fight 5 turn 5 was "play the two Strikes",
Fight 3 turn 2 was "play the good card and waste the third energy because the
only cards left are Defends". They are also the reason the elite hurt: Defend's
5 Block is the deck's *entire* defensive floor and it scales with nothing, so
the honest defensive plan at 18 HP was "hold two Defends and hope". Barbara —
Front Row Seat was the first card in ten floors that gave Block a reason to
belong to this character, and it arrived as an elite reward.

Also automatic: reward screens where one option is arithmetically blank for the
character. **Bennett — Fantastic Voyage+**'s 3 Strength is nearly dead in a deck
whose damage is mostly Bombs, and Bombs are printed "Not an Attack". It appeared
twice.

**(c) What I could not understand, or that contradicted its own printed text.**

- **"A Mine ... goes off when its enemy attacks you, before the hit lands."**
  I read this as mitigation. It is not — the mine fires, the host survives, and
  the hit lands in full. It cost me 18 HP in one turn. Nothing on the screen
  says the trigger does not interrupt the attack, and "before the hit lands" is
  actively suggestive that it might.
- **Status cards I never saw arrive.** The elite printed "intends to give you 3
  Status cards", the pile counts changed, and no screen ever named them. They
  turned up as Infection ×2 in a later hand. I could not tell how many I had or
  where they were.
- **"Apply Hydro twice"** produced `Hydro Aura 2`. I still do not know whether
  that is two applications (the second refreshing the first) or a duration-2
  aura, and whether a second Pyro hit in the same turn would find anything left.
  With reaction damage at 1.5×, that ambiguity is worth real damage.
- **Perfect Timing+'s "If a Bomb triggered an Elemental Reaction this turn,
  play this again."** I ran two copies for six floors and never once saw the
  replay, because Klee's own bombs are Pyro and they mostly land on bare or
  Pyro-aura'd enemies. The clause is not wrong; it is conditional on an aura
  source my deck did not have until floor 6. A new player reads "play this
  again" and buys a card whose upside is invisible.
- **Bomb totals are printed as a sum.** `Bomb 35 (buff) — Bombs here: 3` never
  tells you the individual sizes, and Set off resolves them **one at a time**,
  so whether a 19 HP enemy dies to the first, second or third bomb — and how
  much of the total is therefore wasted or shunted to a survivor — is not
  computable from the screen. It matters, because "kills move it on" makes the
  leftovers a real asset.
- **Spoils Map.** A 0-cost unplayable quest card that occupies a hand slot,
  with nothing on the screen saying what it is for.
- **Lantern** never printed its effect anywhere I saw; I inferred +1 first-turn
  energy from the combat header reading `Energy 4/3`.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Defend**. Not because Block is bad — because in this deck Block
is the one thing that is never part of a plan, and drawing three of them is a
turn the kit has nothing to say about. (Strike is close behind, but Strike at
least finishes things.)

Happiest to draw: **Ka-pow!** — 0 cost, Retain, Set off. It is the card that
makes the bomb plan safe to commit to, it is the only card I could bank, and on
elite turn 4 it resolved a bomb chain, a kill, a summon, a bomb transfer and a
mine placement for free. **Jumpy Dumpty+** is the other one: Bomb 11 plus a
rider that seeds Mines onto enemies that do not exist yet.

**(e) Did the first turn of the first fight already present a decision?**

**No.** Hand was Strike, Defend ×3, Ka-pow! against a printed pure-debuff
intent. Three of the five cards were provably worthless that turn, and the other
two were both strictly worth playing, so the turn played itself; the only
judgement available was the *order* of Strike and Ka-pow!, worth nothing. The
kit's first genuine decision was **fight 1 turn 2** — Jumpy Dumpty's Bomb 8
against three Strikes' 12 damage — and its first exciting one was fight 2
turn 2. Two turns of runway is not bad, but the opening hand contains no bomb,
and the character's whole identity is bombs.

---

## Non-blindness declaration

- **Model family:** Opus (Claude). The kit's author is a **different Claude
  model**. This seat had no prior exposure to the kit.
- **Game commands:** only the two allowed forms —
  `GITS_LANE=1 python -m understudy.blindplay observe` and
  `GITS_LANE=1 python -m understudy.blindplay act "<command>"`. No
  `harness state`, `scenario`, `staged_turn`, `soak`, or any other understudy
  subcommand was run.
- **The one exception, as instructed by the coordinator:** the embark, run
  exactly once as given —
  `python -m understudy.embark --character KLEEMOD-KLEE --lane 1`.
- **Other shell usage (Bash tool):** `mkdir -p review/qa/klee-round-12-2026-09-04`;
  `for` loops chaining several `act` calls in one shell invocation; and `sed`,
  `grep`, `head` and `tail` used **only** to trim the output of my own `observe`
  and `act` calls so the long shared glossary did not repeat. No other program
  was run.
- **Other tools:** the Write tool, once, for this file. Nothing else.
- **Repo files read: none.**
