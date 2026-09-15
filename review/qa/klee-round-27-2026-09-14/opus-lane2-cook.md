# Klee round 27 — blind seat, lane 2 (opus-lane2-cook)

## Identity

- Model and seat: Claude Opus 5 (1M context), blind TESTER seat, lane 2 (`GITS_LANE=2`).
- Run seed: **never printed on any screen I saw.** No screen in this run named a seed.
- Character: KLEEMOD-KLEE (never named on screen either; I know it from my brief, not from the game).
- Ascension the run opened at: **never printed.** No screen named an ascension level.
- Act and boss: act 1. The map named the act's boss: **Soul Fysh**. I never reached it.
- Actions accepted: **119 of 120**.
- Termination reason: **action budget**. I stopped one act short of the cap, on the
  floor-11 rest site, rather than start a turn I could not finish. Wall clock was
  nowhere near 5400 s. No refusals at all this round (0 refused commands), no stalls,
  no `TOOL-BLOCKED`.
- Floors reached: floor 11 of act 1 (six combats, one of them an elite, all won).
- HP trajectory: 62/62 start → 60 (fight 1) → 52 (Trash Heap, −8 by choice) → 44
  (fight 2) → 36 (fight 3) → 18 (fight 4) → 36 (rest) → 19 (elite, fight 5) → 14
  (fight 6) → **32/62** after the floor-11 rest.
- Gold: 245.
- Potions held: Flex Potion, Strength Potion, Skill Potion (3/3, none used — see (b)).
- Relics at the end: Pounding Surprise, Precise Scissors, The Boot, Gorget, Blood Vial.
- Deck at the end — **reconstructed from hands, never read off a deck screen** (no
  screen this run printed my whole deck after the Neow removal): Strike ×3, Defend ×4,
  Jumpy Dumpty, Ka-pow!, Grounded, Return to Sender, Sparks 'n' Splash, Bombs Away!,
  Perfect Timing, Razor — Claw and Thunder, Explosives Workshop, Ammo Scavenging,
  Dig In. Status cards (Dazed) arrived in fight 6 and I assume they were combat-only;
  I never saw a screen that would tell me.

Neow pick: **Precise Scissors** (remove 1 card from your deck), and I removed a
**Strike**. Why: it was the only option that did not put a card into a deck I had not
yet read — Neow's Torment adds Neow's Fury and Neow's Sacrifice adds an unplayable
Guilty — and choosing it also opened the removal chooser, which was the only way this
screen would show me my whole starting deck before I had to commit to anything. That
second reason mattered more than the thinning: it is how I learned Klee's five
non-basic starters (Jumpy Dumpty, Ka-pow!, Grounded, Return to Sender, Sparks 'n'
Splash) before turn one.

---

## Fight 1 — Toadpole (1) [A] 21/21 and Toadpole (2) [B] 24/24

**Turn 1.** Played Jumpy Dumpty on A, then Grounded, then Defend.

The decision was Grounded against Ka-pow!, and it is a genuinely sharp one because the
two cards are written to hate each other. Grounded: *"At the start of your turn, if you
played no Set off card last turn, gain 4 Block and 1 Spark."* Ka-pow!: *"Retain. Set
off. Deal 4 damage."* So the turn splits: detonate Jumpy Dumpty's Bomb 8 now for 8+4
plus a Mine 3 on both bodies, or stay quiet, let the bomb grow (the Bomb line says
"grows 4 a turn"), and collect Grounded's block and spark. I rejected the immediate
Ka-pow! because Ka-pow! prints **Retain** — it costs nothing to wait, the bomb gets
strictly bigger, and Grounded pays only on a quiet turn. This is the first turn of the
first fight and it already had a real fork. Ka-pow! was still in my hand afterwards,
exactly as Retain says.

**Turn 2.** Bomb 12 on A; A had picked up Thorns 2 from its turn-1 Empower. Played
Ka-pow! on A (12 Pyro + 4 = A to 5), then Strike on A (dead), then Strike ×2 into B.

Rejected: Sparks 'n' Splash for 2 energy, which would have banked the power while the
Bomb 12 was still on the field. I rejected it because a power that pays "at the end of
your turn, damage equal to its largest Bomb" pays nothing worth having once I set the
bomb off in the same turn — the largest bomb would have been a Mine 3. Also rejected:
holding Ka-pow! another turn for a Bomb 16, rejected because A's Thorns and 3×3 intent
made killing it now the better trade.

The plan from turn 1 paid here and it paid visibly: A died with two Mine 3s on the
board, and the screen behaved exactly as the Mine gloss says — *"If the enemy dies with
it on, it moves to a survivor"* — B ended the turn wearing **two** Mine 3s.

**Turn 3.** B at 12/24, wearing Mine 14 (7/7) and Thorns 2, intent 3×3. I played
nothing and ended the turn.

This is the fight's nothing turn and I want to be honest about it: it was not a turn
with no decision so much as a turn where the decision had already been made two turns
earlier. Mine says it *"also goes off just before its enemy's hit"*; 14 > 12; so ending
the turn was lethal and every card in my hand was worse than free. I checked whether
Strike was better and it was not — Thorns 2 would have cost me 2 HP to do damage the
mines were already going to do. It played out as printed: B died before its hit, I took
0, and the fight ended.

Judged across the fight: two real decisions (the turn-1 Grounded/Ka-pow! fork, the
turn-2 kill order) and one turn that was a plan landing. Won at 60/62.

Card reward: took **Bombs Away!** over Tinder Toss, Long Fuse and the Sucrose
companion. Reasoning on the screen alone: I had two Set off cards' worth of detonation
(Ka-pow!) and exactly **one** bomb placer (Jumpy Dumpty, and it is Innate so it is the
same one every fight). Set off does nothing without bombs. Long Fuse and Tinder Toss
are more detonators for a board that has nothing to detonate.

---

## Fight 2 — Sludge Spinner [A] 39/39

**Turn 1.** Jumpy Dumpty on A, Strike, Strike. Took its 8 and a Weak.

Rejected: Defend instead of the second Strike, and rejected letting the bomb ride with
Grounded (Grounded was not in hand). At 52/62 against a single 39-HP body I judged the
race worth 8 HP. Rejected also: Ka-pow! now — same reasoning as fight 1, Retain makes
waiting free.

**Turn 2.** Ka-pow! on A (0 cost, set off Bomb 12), Bombs Away!, Strike. Exactly lethal.

Rejected: Sparks 'n' Splash, again, for the same reason — it wants an undetonated bomb
and I was cashing the bomb.

**Here is where the screen and the outcome disagreed, and it is the clearest legibility
defect I found.** I was Weak 1. Ka-pow! printed *"Deal 3 damage"* and Strike printed
*"Deal 4 damage"* — the faces had already been re-costed downward for Weak, which is
good. But I also held **The Boot** — *"Whenever you would deal 4 or less unblocked
attack damage, increase it to 5."* So the three numbers I could read (12 bomb + 3 + 4 =
19) did not add to the 27 the enemy actually had left, and yet it died. The real
arithmetic was 12 + 5 + 5 + 5 (Bombs Away!'s 2 also bumped) = 27. **Every card face on
that screen was re-printed for the debuff and none of them was re-printed for the
relic.** A blind reader who trusts the printed numbers under-counts his own damage by
up to 3 per hit, on the exact turn where being off by 3 decides whether he takes another
8 to the face. I got the kill by luck of over-committing, not by reading.

Card reward: took **Perfect Timing** (*"Set off. Deal 8 damage."*) over Stoke the Fuse,
Tinder Toss and Amber. A second detonator, and twice Ka-pow!'s attached hit.

Also on that reward screen, in the "Words on this screen" glossary, a definition that
belongs to a different character entirely: **"Spend — Chosen on play, never automatic.
Pays the lead performer, fires in full even if the bar is short, and an emptied
performer takes a Bow. On an empty stage the Spend mode is not offered at all."**
Nothing on that screen, nothing in my deck, and nothing I saw in the whole run has a
lead performer, a bar, a stage or a Bow. I spent real reading time trying to work out
what of Klee's I had missed. It is glossary leakage from another kit.

---

## Fight 3 — Corpse Slug (1) [A] 27/27 and Corpse Slug (2) [B] 25/25, both Ravenous 4

**Turn 1.** Jumpy Dumpty on A, then Sparks 'n' Splash (2 energy). Took 8 and a Frail.

This was the real decision of the fight and it was a gamble on printed text I could not
resolve: Sparks 'n' Splash says *"deal Pyro damage to a **random** enemy equal to its
largest Bomb."* With a Bomb 8 on A and nothing on B, "random enemy" could mean 8
damage or could mean 0. I rejected the safe line (Jumpy + two Strikes into A, 12
guaranteed) specifically to find out. It picked the bombed body: A went 27 → 19 at end
of turn. One sample, so I cannot tell you whether it is weighted, whether it prefers a
bombed target, or whether I was lucky — and the card's own text does not say. That is a
card whose value I still cannot price after playing it.

**Turn 2.** Perfect Timing on A (Bomb 12 + 8 = 20, A dead at 19), then Bombs Away! on
both, then ended with 1 energy unspent.

Rejected: killing B first. Ravenous 4 says *"When an enemy dies, Corpse Slug immediately
eats it, becoming Stunned and gaining 4 Strength."* I read that as a genuine trade —
the survivor skips a turn but hits 4 harder forever — and picked the body whose death
handed the survivor the shorter remaining fight. It resolved exactly as printed: B
became Stunned with Strength 4, and the two Mine 3s from Jumpy Dumpty's trigger plus
Bombs Away!'s Bomb 2 all stacked on it. Rejected spending the last energy on Defend,
because B was Stunned and 3 block against nothing is worth less than nothing.

**Turn 3.** B at 17/25 wearing **Bomb 20** (7/7/6). Ka-pow!, 0 cost, dead.

An obvious lethal — but it is the two-turn plan landing, not a dead turn. I will say
plainly that the interesting part had happened on turn 2.

Card reward: took **Razor — Claw and Thunder** (Electro) over Dig In, Countdown and
Coven Errand. The whole run so far had printed, on every single combat screen, *"NO
REACTION IS REACHABLE HERE: Pyro is the only element this screen can supply."* Razor
was the first card offered that could make that sentence go away. I drafted it to see
the other half of the kit. Coven Errand was the card I most wanted on pure deck logic
(a second bomb placer) and I passed it for curiosity — a draft decision I would defend
but which cost me later.

---

## Fight 4 — Punch Construct [A] 55/55, Artifact 1, intent Defend

**Turn 1.** Jumpy Dumpty on A, Grounded, Ka-pow! on A, Strike. 55 → 36.

The decision here was made *by the enemy's intent line*, and it is the best-designed
moment in the run. The Bomb gloss says **"Block stops it."** The construct's intent was
Defend. So every turn I let a bomb ride is a turn its block eats the payoff — the whole
"grow the bomb" instinct the kit teaches in fights 1–3 is exactly wrong here. I
detonated on turn one, into 0 block, and rejected the grow-the-bomb line for that
reason. I did also play Grounded knowing it would not pay next turn (I was about to Set
off), purely to bank the power with an energy I had nothing else to do with — a small,
real call.

**Turn 2.** Razor on A — first reaction of the run, Overloaded.

The reaction preview printed on the card in hand before I played it
(*"Reaction preview: Overloaded — Pyro meets Electro: 6 damage to ALL enemies and 1
Weak on the reacted enemy"*), which is excellent: I could price the play before
committing. Two things then disagreed with what I expected, one of them fine and one
not:

- **The Weak never landed, and the screen told me why in advance**: Artifact 1,
  *"Negates 1 debuff."* After Razor the Artifact was gone from its line. That is the
  screen being honest; I just had not thought it through.
- **The Overloaded 6 appears to have ignored block.** Razor's 8 hit Block 10, leaving
  Block 2. Then the reaction's 6 should have met that Block 2 and put 4 on the body:
  36 → 32. The screen showed **HP 30, Block 2** — the full 6 on the body, block
  untouched. Either reaction damage bypasses block or something else is adding up; the
  Overloaded line says only "6 damage to ALL enemies" and does not say which.

Then Bombs Away! (to strip the last 2 block and add a Bomb 2), then Perfect Timing to
set off Mine 7 + Bomb 2 + its own 8. Rejected: holding the mine so it would fire before
the construct's hit. I rejected it because block would have been back up by then — the
same "Block stops it" rule that shaped turn 1.

**Turns 3 and 4.** Drew Strike + four Defends at 26 HP against a 14-damage intent —
the deck's low point. Played Strike and two Defends (rejected three Defends: 9 block
saves 5 HP where Strike takes the body from 8 to 2, and I wanted it dead before it
defended again). Killed it turn 4 with a Strike. Won at 18/62.

The honest read of this fight: the kit's engine was switched off by one enemy keyword
and I had to win it with Strikes and Defends. That is a fine design (a real counter to
the archetype, telegraphed on the intent line) but the fallback it forces you into is
the most boring thing in the deck.

Card reward: took **Explosives Workshop** over Witches' Circle, Fish Blasting and
Fischl. Reasoning: Witches' Circle keys off Hexerei and I owned exactly one Hexerei
card. I will say below that I think this pick was wrong.

Rest site: rested 18 → 36. Rejected Smith. With an Elite next and 18 HP, upgrading a
card I might not draw loses to not dying.

---

## Fight 5 (Elite) — Skulking Colony [A] 75/75, Hardened Shell 20/turn, intent 14

This is the fight of the round and the one that taught me what the kit actually is.

The Hardened Shell line — *"cannot lose more than 20 HP each turn"* — plus the Bomb
gloss's *"Only Vulnerable and the HP cap move it"* means the kit's signature play
(stack one enormous bomb, cash it in a single glorious detonation) is **the worst
available line here.** By turn 6 that body was wearing **Bomb 65** (30/22/13), 65 Pyro
of stored damage, and setting it off would have dealt 20. The counter-play the fight
demands is the exact inverse of the habit fights 1–3 teach, and finding that inversion
was the most interesting thinking I did all round.

**Turn 1.** Jumpy Dumpty, Strike, Defend. Rejected the second Strike for the Defend:
against a 14 that will repeat every turn for five turns, 5 block compounds and 6 damage
into a 20-cap does not.

**Turn 2.** Grounded, Defend, Defend. Rejected Bombs Away! here. This is where I worked
it out: the bombs are going to deal my damage *for free*, capped at 20 either way, so
every point of energy I spend on attacks is energy the cap eats. Energy belongs on
block; the bomb belongs on the board, growing. Took 4.

**Turn 3.** Sparks 'n' Splash, then Return to Sender. The best turn of the run.

Sparks 'n' Splash is the answer to Hardened Shell: it pays *"damage equal to its largest
Bomb"* at the end of every turn **without consuming the bomb**. It turns a 20-HP cap
from a wall into a metronome — 20 a turn, forever, for zero energy after the first two.
69 → 53 that turn, then 53 → 33, then 33 → 13, all of it free.

And Return to Sender did exactly what its face promises, which I had doubted: *"Gain 8
Block. This turn, damage this Block absorbs is placed on the attacker as a Bomb."* Its 9
hit landed on my block, I took 0 HP, and a **Bomb 12** appeared on its line. A defensive
card that feeds the offensive engine — the single most satisfying card interaction I
met. Rejected: Defend (5 block, no bomb) for the same energy.

**Turn 4.** Defend, Defend, Explosives Workshop. The third energy was dead — Strike's 6
and Ka-pow!'s set off would both have been eaten by the cap that Sparks 'n' Splash was
already filling — so I banked a power I did not need rather than waste it. Took 4.

**Turn 5.** Razor for the Overloaded, then Return to Sender, then Defend. Rejected
attacking further: capped. I played Razor **specifically for the Weak**, not the damage
— reducing a 16-damage intent was the only thing left on the screen worth buying. It did
not work: the next screen showed intent 16 unchanged and no Weak on its line. Whether
the Weak landed and expired at the end of its own turn before I could read it, or never
landed, the screen does not let me tell. Blocked 17 against 16, took 0.

**Turn 6.** Ka-pow!, 0 cost, into Bomb 65 on a 13-HP body. Dead.

Judged across the fight: this is the round's best fight and its decisions were real and
sequenced — the turn-3 realisation that Sparks 'n' Splash beats a damage cap, the
standing choice each turn of energy-into-block versus energy-into-attack that the cap
makes non-obvious, and Return to Sender turning damage taken into damage stored. Won at
19/62 with zero HP lost across the last three turns.

Elite rewards: Gorget, Skill Potion, 39 gold, and **Ammo Scavenging** (*"Place a Bomb 4.
Draw 1 card for each of your Bombs that went off this turn"*) over Blazing Delight,
Pocket Fireworks and Mika. A bomb placer, which I had wanted since fight 1.

---

## Fight 6 — Haunted Ship [A] 63/63

**Turn 1.** Jumpy Dumpty, Sparks 'n' Splash. Straight to the elite's lesson: no
detonator, bomb on the board, engine on. Rejected Strike and Razor, because the ship's
intent was Debuff + 5 Status cards and nothing I did this turn changed what it did.

**Turn 2.** Defend, Defend, Explosives Workshop. Blocked its 13 to 0; Sparks 'n' Splash
paid 12 for free. Rejected Perfect Timing — detonating would have reset the meter I
was living off.

**Turn 3.** Defend, Ammo Scavenging (Bomb 4), Bombs Away! (Bomb 2). Deliberately
feeding bombs to Sparks 'n' Splash rather than cashing them. Took 5.

**Turn 4.** Ship at 29/63 wearing Bomb 38 (22/9/7), no HP cap in sight. Ka-pow!, 0 cost,
dead.

The whole fight was one decision made once — "do not detonate, let the power meter run"
— and then executed. That is the elite's lesson transferring, which I count as the draft
and the earlier fight paying off rather than four empty turns, but I will not pretend
turns 2 and 3 were exciting on their own.

Reward: **Dig In** (*"cost 1 Spark, Gain 8 Block"*) over Big Badda Boom, Bombs Away!
and Kaeya. I ended the run holding 3 potions and 7 Sparks I had no card to spend on;
Dig In is the first card I was offered that turns the spark surplus into the thing that
was actually killing me.

Floor 10 Treasure: Blood Vial. Floor 11 rest: 14 → 32. Budget reached.

---

## The kit, after 6 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Four, and three of them are structural rather than incidental:

1. **Detonate now or let the bomb grow — made on the turn, every turn.** This is the
   kit's spine and it is well built, because the pressure runs both ways: the bomb
   grows 4 a turn so waiting is strictly more damage, but the enemy is hitting you
   while you wait, and "Block stops it" means a defending enemy can eat the whole
   stored payoff. Fight 4's Punch Construct (intent: Defend) and fight 1's Toadpoles
   pull in opposite directions and both are legible from the intent line before you
   commit.
2. **Grounded against the whole set-off half of the deck — made on the turn.**
   *"if you played no Set off card last turn"* is a real cost on a real card. It made
   turn 1 of fight 1 a decision, which is more than most starters manage.
3. **Energy into block versus energy into attacks — made across the elite fight, once
   Hardened Shell made the cap visible.** Discovering that bombs pay for free and
   therefore energy belongs on block was the best thinking the round asked of me.
4. **Whether to draft the second element — made at the draft, fight 3.** Taking Razor
   over Coven Errand traded a bomb placer I needed for a mechanic I had only read
   about. Real, and I am still not sure I was right.

**(b) What felt automatic, and what never seemed worth playing.**

Automatic: the kill turn. Six fights, and five of them ended with Ka-pow! or Perfect
Timing into an oversized bomb for a lethal I could see two turns out. That is the
plan paying off, not a defect — but it does mean the last turn of most fights is
bookkeeping.

Never worth playing: **Strike and Defend**, which is not news, except that fight 4
forced me to win a fight on them and it was the dullest stretch of the run.
**Explosives Workshop** (*"your Bombs grow by 1 more"*) I drafted and played twice and
could not once point at a moment it changed an outcome — bombs already grow 4 a turn
and the fights that matter cap the damage anyway; I played it both times as a place to
dump an energy the damage cap had made worthless. And I finished the run with three
unused potions, which I should flag against myself: I never found a turn where Flex or
Strength beat the bomb, because Strength does not touch bomb damage and the two fights
that were close were both capped.

**(c) What I could not understand, or that contradicted its own printed text.**

- **The Boot versus the printed card face** (fight 2). Card faces are re-printed for
  Weak but not for the relic, so on a Weak turn the numbers on the screen are wrong in
  a direction that makes you under-play. This is the one I would fix first.
- **Overloaded's 6 seems to ignore block** (fight 4, turn 2): 8 into Block 10 left
  Block 2, then the reaction's 6 took the body 36 → 30 with Block 2 still standing.
  Nothing printed says reaction damage bypasses block.
- **Overloaded's Weak, twice, invisible.** Once correctly (Artifact 1 ate it, and the
  screen showed the Artifact gone). Once inexplicably (elite turn 5: no Artifact, no
  Weak on its line, intent unchanged at 16). The screen's own long Elemental Reaction
  gloss warns that a reaction can happen where "no screen ever shows it" — which reads
  less like a rule and more like a confession, and it means I cannot audit my own
  reaction plays from the screen.
- **Sparks 'n' Splash's "random enemy."** Played it once with two bodies and one bomb,
  and it hit the bombed one. I cannot tell from the text or one sample whether that was
  weighted or lucky, and the card is a 2-energy power whose whole value hangs on it.
- **The "Spend / lead performer / Bow / empty stage" glossary entry** on the fight-2
  card reward. It has nothing to do with anything on that screen or in this kit.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Explosives Workshop**. Happiest: **Return to Sender** — in a kit where
every other card asks you to spend a turn setting something up, it blocks a hit and
converts the hit into the setup, in one card, at the moment you most want block. The
elite turn where it took a 9 to the face and printed a Bomb 12 on the attacker was the
one time this round the screen did something better than I had predicted.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a sharp one.** Jumpy Dumpty is Innate, so it is in hand turn one of every
fight; Ka-pow! is 0-cost and Retain; Grounded pays only after a turn with no Set off.
Three cards, in the opening hand, that make "detonate now or bank it" a live question
before I had seen a single reward screen. That is the strongest thing I can say about
this kit's legibility.

---

## Three lines

MOST WANTED TURN: fight 5 turn 3 -- Sparks 'n' Splash turned a 20-HP-per-turn cap into a free metronome and Return to Sender paid a 9-damage hit back as a Bomb 12.
NOTHING TURN: fight 6 turn 2 -- two Defends and a power I did not need, while the engine ran itself.
NEVER AGAIN: Explosives Workshop -- +1 bomb growth never once changed an outcome, and the fights that matter cap the damage anyway.

---

## Non-blindness declaration

**Repo files read: none.**

Every game command was one of the two allowed forms, all via the Bash tool, all with
`GITS_LANE=2` and the absolute venv python path:
`...\.venv\Scripts\python.exe -m understudy.blindplay observe` and
`... -m understudy.blindplay act "<command>"`. I ran no `harness state`, no `scenario`,
no `staged_turn`, no `soak`, and no other understudy subcommand.

Commands and tools outside those two:

- `mkdir -p` on the session scratchpad directory, once, and one `echo` writing a
  one-line scratch file (`notes.md`) into it. I never read that file back and it played
  no part in the round.
- `cd` into the repo working directory as the prefix of most Bash calls, and shell `for`
  loops to issue several `act` calls in one Bash call.
- `sed -n` and `head` piping the output of `observe` to re-read one block of the screen
  I had just been shown. Nothing was filtered out that I did not read elsewhere; on a
  few calls overlapping `sed` ranges printed some blocks twice, which is my pipe and not
  the game.
- The Write tool, once, for this record.

No other tool was used. No repo file, YAML sheet, C# source, doc, packet, review
material or other seat's record was opened at any point.
