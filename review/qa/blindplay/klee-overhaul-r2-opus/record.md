# Blind play session `klee-overhaul-r2-opus`

**R217 G, and same model family as the author: subjective feedback from a Claude Opus subagent playing the real game through the blind render. Useful for iteration; not human validation, not balance evidence, not approval, and not an author-disjoint read.**

## Identity
- model: claude-opus (this agent)
- build_version: not printed to the tester
- run_seed: not read back at embark; the operator will fill it from the sidecar
- actions: 94
- termination: action budget (alive at 3/62 HP, 4 fights won, act-one boss not reached)

Opening boon: **Silver Crucible** (first 3 card rewards upgraded, first chest empty).
Starting relic: **Pounding Surprise** (a Spark whenever a Bomb goes off; a fourth Companion
option on card rewards).

---

## Fight 1 — two Toadpoles (21 and 24 HP)

**1. What I did, turn by turn.**
Opening hand was four `Duck and Cover` and one `Kaboom!`, which told me most of what I needed:
this deck blocks in fives and hits in sixes. Turn 1 I put `Kaboom!` into the lower-HP Toadpole
(it was buffing, and the other was telegraphing 7) and spent the rest on two blocks for 10, which
ate the 7 whole. Turn 2 was the turn the character actually explained itself: `Pop!` cost 0 and
placed a Bomb 5, `Kaboom!` said "Set off" and I guessed correctly that it meant "detonate what's
on this enemy first" — 5 + 6 = 11, and Pounding Surprise handed me a Spark, which turned the
greyed-out `Ka-pow!` into a live 0-cost 7 that finished the first Toadpole. I ended the turn
planting `Jumpy Dumpty` on the survivor. Turn 3 the bomb had grown 8 → 10 on its own; `Kaboom!`
cashed it for 16, Jumpy Dumpty's rider dropped a Mine 3, and a second `Kaboom!` set off the mine
for the kill. 56/62 out of the fight.

**2. The line I did not take.**
On turn 2 I could have led `Kaboom!` before `Pop!` and just taken 6+6 across two bodies. That is
12 damage spread thin instead of 11 concentrated plus a Spark, and it would not have unlocked
`Ka-pow!` — I would have finished the turn with a Toadpole at 4 HP still swinging.

**3. What would have changed my line.**
If the buffing Toadpole had shown an attack intent instead of Empower, I would have blocked more
and skipped the bomb-planting entirely. And if `Kaboom!` had not said "Set off" I would have
played `Pop!` as a dead card for two more turns waiting for something to explain it.

**4. Automatic and dead cards.**
`Pop!` into `Kaboom!` became automatic by turn 2 and stayed automatic for the whole run. `Ka-pow!`
was dead until the first bomb went off and then was never dead again. Nothing was truly dead here;
the fourth `Duck and Cover` was just surplus.

**5. How my plan changed.**
It went from "block and chip" to "the deck is a fuse, not a weapon" the moment the Bomb 5 line
read *Grows at the start of your turn; never goes off by itself*. Everything after that was about
when to cash a bomb, not whether.

**6. What was confusing.**
Nothing badly. The one thing I had to infer was whether `Kaboom!`'s "Set off" hit only its target
or every enemy — the card never says, and I only learned it was target-local by watching the
numbers.

---

## Fight 2 — Sludge Spinner (37 HP)

**1. What I did, turn by turn.**
Turn 1 I committed to the accumulate plan: `Pop!` (Bomb 5) plus `Jumpy Dumpty` (Bomb 8) for 13
banked, one `Duck and Cover` for 5, and I ate 3. Turn 2 the bomb had grown to 17 — and the enemy's
turn-1 hit had left me Weak, which quietly cut the detonation to 12. I detonated anyway (16 total
with the Kaboom) and used the rest on two blocks. Turn 3 I deliberately left the Mine 3 alone so
it would trigger on the Spinner's own attack (it did, for 2, and paid me a Spark). Turn 4 the kill
was a clean three-card chain: `Jumpy Dumpty` → `Kaboom!` (8+6=14) → `Ka-pow!` cashing the fresh
Mine 3 for 10. Out at 50/62.

**2. The line I did not take.**
I nearly held the 17-stack one more turn to shed Weak and grow to 21. I dropped it when I worked
out the Spinner re-applies Weak on every hit, so waiting buys the growth but never buys back the
25%. That call gave up ~6 points of detonation.

**3. What would have changed my line.**
Any turn where the Spinner showed a non-attack intent, I would have banked instead of cashed —
which is exactly what I did later against the Corpse Slug.

**4. Automatic and dead cards.**
`Duck and Cover` was automatic filler for leftover energy all fight. `Quick Fuse+`, freshly drafted,
was dead every single turn it appeared: it wants a Spark *and* a live bomb, and by the time I have
a Spark the bomb it would have set off is the one that produced the Spark.

**5. How my plan changed.**
From "grow a big one" to "cash on schedule". The Weak tax and the +2/turn growth rate together mean
banking is only worth it on a turn the enemy is not attacking.

**6. What was confusing.**
The bomb readout. It printed **`Bomb 17 (buff) — Set off deals 12 total Pyro damage here`**. Two
different numbers on one line, and it took me a beat to realise 17 is the raw stack and 12 is what
*I* would deal through my own Weak. The name says one thing and the sentence says another.

---

## Fight 3 — two Corpse Slugs (26 and 27 HP), Ravenous 4

**1. What I did, turn by turn.**
The buff read *When an enemy dies, Corpse Slug immediately eats it, becoming Stunned and gaining 4
Strength*, so I picked my kill order to minimise what Strength was worth: the 3x2 attacker, because
+4 on a multi-hit is +8 a turn. Turn 1: `Pop!` + `Kaboom!` for 11, then `Powder Charge+` (paid with
the Spark that detonation just produced) to leave a Bomb 6 on the same body, and two blocks. Turn 2
the Bomb 6 had grown to 8; `Kaboom!` cashed it for 14 and a second `Kaboom!` took the last point.
The survivor ate it, went to Strength 4, and — the important half — was **Stunned**, so the whole
round was free. I spent my Energy Potion there to squeeze `Jumpy Dumpty` in, because a stunned
enemy is exactly the turn you want to be banking. Turn 3 the bomb was at 10, I stacked `Powder
Charge+` on top for 16, `Kaboom!` cashed 22, and `Ka-pow!` cleaned up the last 5. Zero damage taken
after turn 1.

**2. The line I did not take.**
Leaving the 1 HP Slug alive and killing the *other* one first, so the Strength never landed on a
healthy body. It gives up 8 damage a turn for two or three turns to deny 4 Strength; the arithmetic
never got close.

**3. What would have changed my line.**
If Stunned had not been printed as an intent I would have blocked instead of spending the potion.
The intent line saying *This enemy can't act on its next turn* is what made the potion safe.

**4. Automatic and dead cards.**
`Powder Charge+` became automatic the moment I understood Spark is nearly free — it is a 0-cost
Bomb 6 in a deck where bombs are the damage. `Quick Fuse+` was dead again, all fight, every copy.

**5. How my plan changed.**
This is the fight where the loop clicked: place on a safe turn, stack a second bomb on top of the
first, cash the whole pile with one `Kaboom!`, then use the returned Sparks on `Ka-pow!` for the
overkill. 22 damage from one card is a genuinely good feeling.

**6. What was confusing.**
`Jumpy Dumpty` says *Place a Bomb 8 on a random enemy* with no target prompt, so I had to sequence
around it — kill the low body first, or risk 8 points of bomb landing on something with 1 HP. That
is a real decision, but the card gives you no way to see the roll coming.

---

## Fight 4 — Living Fog (80 HP) with Gas Bomb minions

**1. What I did, turn by turn.**
Long fight, so I opened with the power: `Sparks 'n' Splash (proto)+` (end of turn, set off a random
enemy's Bombs) plus a block. The Fog answered by putting **Smoggy** on me — *You can only play 1
Skill per turn* — which is a precision strike on this deck, because `Pop!`, `Powder Charge+`,
`Jumpy Dumpty`, `Quick Fuse+` and `Duck and Cover` are *all* skills. From there every turn was the
same question: which one skill. Turn 2 I spent it on `Jumpy Dumpty` and let the power detonate it
at end of turn (8, plus a Mine that took 3 more off the Fog's own attack). Turn 3 a Gas Bomb
appeared with *Death Blow, 8* and I chose to ignore it and race the leader — 12 into the Fog, ate
11. Turns 4 and 6 were my ceiling turns: `Powder Charge+` → `Kaboom!` → `Ka-pow!` for 19 apiece,
one energy spent, two wasted because every remaining card in hand was a skill. Turn 5 I did stop to
kill a Gas Bomb with two Kabooms. Turn 7 I drew five cards, all five skills, played exactly one, and
went from 14 to 3. Turn 8 I had to choose between killing and surviving and chose to survive at 3 HP
with the Fog on 7. Turn 9 two Kabooms killed the Fog and the Gas Bomb abandoned combat exactly as
its `Minion` line promised — the difference between a win and a death was one word on an enemy buff.

**2. The line I did not take.**
Turn 3, killing the first Gas Bomb with both Kabooms instead of racing. It denies 8 damage and costs
12 of output; I priced it as roughly break-even and took the race because minion spawns punish long
fights. I still think that was right, and it still nearly killed me.

**3. What would have changed my line.**
Smoggy. Without it I block for 10-15 a turn and this is a comfortable fight. With it, my whole
defensive suite is rationed to one card a turn while my attacks are unrestricted — so the debuff
did not slow my damage at all, it only removed my ability to survive. If `Duck and Cover` were an
attack-adjacent card, or if I had drafted `Diona` or `Run Away!` earlier, turn 7 does not happen.

**4. Automatic and dead cards.**
Automatic: `Powder Charge+` → `Kaboom!` → `Ka-pow!`, in that exact order, on every turn I drew it.
Dead: `Quick Fuse+` again — it never once fired in four fights. Also dead: `Sparks 'n' Splash` on
any turn I had no bomb, which was most of them, and worse, it is *actively anti-synergistic* with
the growth mechanic, because it force-detonates at end of turn and so no bomb I place can ever grow.
I drafted it as an engine and it turned out to be a tax on the thing that makes bombs good.

**5. How my plan changed.**
Three times. Bank-and-grow → cash-every-turn (because the power detonates for me) → then, from
turn 5, pure damage race with block only when the hand forced it. By turn 7 there was no plan, only
"play the one skill I am allowed and hope".

**6. What was confusing.**
- The debuff is called **Smoggy** in my status list; the keyword the cards print is **Smog** —
  and the keyword text only appeared on the cards *after* I had already spent my skill, i.e. the
  explanation shows up once it is too late to use it.
- A blocked card printed **`CANNOT BE PLAYED: something else on the board is stopping you right
  now`**, which is vaguer than everything else the screen tells you.
- I could not predict which turn a Gas Bomb would spawn; they arrived on 3, 5, 7 and 9 and nothing
  on screen forecast them.

---

## The run, in the tester's own words

**1. What the character seems to be about, from the cards alone.**
Delayed damage you schedule. You do not hit things; you leave something on them and decide, later,
when to collect. Bombs stack into one pile, grow +2 a turn on their own, and one "Set off" card
cashes the whole pile at once — so the character's real currency is *timing*, and the best turns
are the ones where the enemy is buffing or stunned and you get to bank instead of spend. Spark is a
second, softer currency that the relic prints for you every time a bomb goes off, which makes the
0-cost cards feel like they are free because someone else paid.

**2. The recurring tension.**
Cash now or grow. It is a good tension and it is legible: +2 a turn versus the damage you take
waiting. It was sharpest against enemies with an Empower or Stunned turn, where the game hands you
a free round and you can feel it. It got blunted whenever I could not afford to look away from my
own health bar.

**3. Which cards carried the run and which never mattered.**
Carried: `Kaboom!` (the universal cash-out), `Powder Charge+` (0-cost Bomb 6 is absurd value once
Sparks flow), `Ka-pow!` (0-cost 7 to finish), `Jumpy Dumpty` (the Mine rider is a second detonation
you get for free on the enemy's turn, and it is the most elegant card I drew).
Never mattered: **`Quick Fuse+` did nothing across four fights** — every time it was in hand it
printed either *no enemy is holding a Bomb* or *you have no Spark*, and its whole job is duplicated
by `Kaboom!`, which also deals 6. `Sparks 'n' Splash (proto)+` was a mistake I paid 2 energy for.
`Duck and Cover` mattered but only ever as change for leftover energy — 5 block never once felt
like a decision.

**4. When play became repetitive.**
By fight 3 the turn had a fixed shape: place the biggest bomb I could, cash it with `Kaboom!`,
spend the returned Spark on `Ka-pow!`, dump leftover energy into `Duck and Cover`. Fight 4 reduced
it further, to "which of my five skills am I allowed to play". The bomb engine is satisfying the
first two times you fire it and then it is a rotation.

**5. What I would draft differently.**
I would take `Noelle — Breastplate+` or `Diona` over `Quick Fuse+`, because I ended the run at 3 HP
and never once wanted a second set-off card. I would skip `Sparks 'n' Splash` outright — it deletes
the growth mechanic that is the character's best idea. And I would take `Ammo Scavenging+` over
`Powder Charge+` if I saw them again, because in four fights I ran out of *cards* far more often
than I ran out of Sparks, and a 12-card deck that draws five means the engine is idle every second
turn.

---

## Defects and oddities

- **The Dexterity Potion cannot be used. Three attempts, three failures, on two different screens.**
  Each returned `{"ok": true, "verb": "use potion", "post": {"action": "use_potion", "slot": 0},
  "printed": {"potion": "Dexterity Potion"}, "refusal": ""}` followed by the single word `error`,
  and the potion was still in my Potions list afterwards with no Dexterity gained. The `Energy
  Potion` used from the same slot 0 earlier in the run worked normally. This mattered: I was
  making block decisions at 22 and then 14 HP that assumed a potion I could not spend.
- **A power's name and its effect print different numbers with no explanation.**
  `Bomb 17 (buff) — Set off deals 12 total Pyro damage here (2 Bombs, 0 of them Mines).` I worked
  out that 17 is the stack and 12 is the post-Weak figure, but nothing on screen says so, and the
  bold number a player reads first is the wrong one.
- **`Quick Fuse+` never fired in four fights.** Its two gates (needs a Spark, needs a live enemy
  Bomb) are almost mutually exclusive in practice, because the ordinary way to get a Spark is to
  set off the bomb it wants to set off. Not a crash — but a card that did nothing, all run.
- **The `Smog` keyword text only appears after you have spent your skill.** Before I played a skill,
  `Duck and Cover` printed just its own rules; after, the same card printed
  `*Smog* — You cannot play additional Skills this turn. Clears at the end of the turn.` The status
  line calls the debuff `Smoggy 1` and the keyword calls it `Smog`; two names for one thing.
- **A vague refusal string.** `CANNOT BE PLAYED: something else on the board is stopping you right
  now` — every other refusal on this screen names its reason (`you have no Spark; and this costs 1`,
  `no enemy is holding a Bomb`, `you do not have enough energy`). This one does not.
- **Numbered card names go stale within a turn.** After playing one of two identically named cards,
  `play "Duck and Cover (1)"` was refused with `nothing here is called 'Duck and Cover (1)'. What is
  on the screen: Duck and Cover, Kaboom!, Quick Fuse+` — the suffix silently disappears when the
  duplicate is gone. Recoverable in one retry, but it cost me an action.
- **`Jumpy Dumpty` targets randomly with no way to see or influence the roll**, which forces you to
  sequence kills around it. Called out as an oddity rather than a bug — it may well be intended.
- No screen was ever unescapable, and every printed command that I could legally use worked apart
  from the potion above.
