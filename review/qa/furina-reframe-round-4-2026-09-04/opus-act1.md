# Blind seat — KLEEMOD-FURINA, lane 2, act 1

## Identity

- **Model / seat:** Opus (Claude), blind TESTER seat. The kit's author is a
  different Claude model; I had not seen this kit before this round and read no
  repo file during it.
- **Lane:** 2 (port 15528). Embark stamp `20260903-223432`.
- **Run seed:** `2JDS8K04D5UU`
- **Character:** Furina. **Ascension 2.** Act 1; the map named the act's top as
  **Ceremonial Beast**.
- **Actions accepted:** 70 of 70 (the cap). Every `act` call was accepted; there
  were **no refusals** and no `TOOL-BLOCKED` screen.
- **Termination reason:** the action budget, mid-turn-3 of fight 4 on floor 4.
  Wall clock was not close to its cap. Because the budget ran out inside act 1,
  there is **no `opus-act2.md`** — I never reached the act-1 boss.
- **HP trajectory:** 62/78 at the first fight (the run opens below max on A2) →
  60 → 59 → 58 → 55 → 53 (three fights won) → 41 → **31/78** at the stop, mid
  fight 4.
- **Gold:** 44 (18 + 10 + 16). Nothing spent; I never reached the shop.
- **Potions held:** none. No potion was ever offered as a reward and no potion
  slot was ever printed on any screen, so I cannot say whether this run has
  potion slots at all.
- **Relics:** `Ethereal Spotlight` ("At the start of your turn, add an Ethereal
  Spotlight to your Hand") and `Scroll Boxes` (the Neow pick).
- **Deck at the stop.** The two allowed commands never print a deck list, so
  this is assembled from what I saw drawn. Pile arithmetic gives the sizes:
  14 cards entering fight 1, 15 entering fight 2, 16 entering fight 3, 17
  entering fight 4 — i.e. **11 starter cards + 3 from the Neow bundle + 3 card
  rewards**. Cards I positively saw in my own draw pile: `Soloist's
  Solicitation` (at least two copies, seen together in one hand), `Aria of
  Recompense`, `An Invitation`, `Stage Presence`, `Regal Bearing`, `Salon
  Début`, `Lynette — Enigmatic Feint`, `Freminet — Pers, Deploy!` [Cryo];
  from Neow, `Suffering for Art`, `Undercurrent`, `The Guest List`; from
  rewards, `Chevreuse — Interdiction Fire` [Pyro], `Lynette — Magic Trick:
  Astonishing Shift`, `Charlotte — Framing: Freezing Point Composition` [Cryo].
  Cards that appeared in hand but were generated in-combat and are **not** deck
  cards: `Sayu — Yoohoo Art: Fuuin Dash`, `Kujou Sara — Tengu Stormcall`
  [Electro], `Lynette — Bogglecat Box`, and the per-turn `Ethereal Spotlight`.

**Neow pick: `Scroll Boxes`** (choose 1 of 2 packs of cards). I took it over
`Silver Crucible` because a blind seat learns more from six new printed faces
than from three upgraded ones, and `Winged Boots`'s path-ignoring is worth
nothing to a seat that cannot see what it is routing toward.

Inside Scroll Boxes I took **bundle 2 — `Suffering for Art` / `Undercurrent` /
`The Guest List`** over bundle 1. Bundle 1's cards both *read* Encore
(`Compose Herself`: "If you have at least 8 Encore") without telling me what
Encore is; bundle 2 contained the only card on the screen that would let me
*make* Encore cheaply and find out (`Suffering for Art`, 0 cost, "Lose 1 HP.
Gain 3 Encore"), plus the only real AoE on offer.

**Legibility note taken at Neow, before any fight:** the bundle screen printed
a "Words on this screen" glossary for *Companion*, *Weak* and *Exhaust*, but
**not for Encore**, which two of the six cards named. I made that pick without
knowing what the kit's headline resource does.

---

## Fight 1 — Nibbit, HP 44/44

Opening hand: `Ethereal Spotlight`, `Soloist's Solicitation` ×2, `Aria of
Recompense`, `An Invitation`, `Lynette — Enigmatic Feint`. 3 energy. Nibbit
intended Attack 12.

### Round 1

Played `An Invitation` (0) → `Aria of Recompense` (1) → `Ethereal Spotlight`
(0, "Costs 2 Encore") → `Lynette — Enigmatic Feint` (1) → `Soloist's
Solicitation` (1).

`Ethereal Spotlight` had printed, in my opening hand, **`CANNOT BE PLAYED: you
have no Encore, and this costs 2`**. That refusal line is what told me the
turn-1 sequencing problem existed at all: the free card in my hand is locked
behind a resource I have none of, and the only unlock on the board costs an
energy. So I paid the energy for `Aria` first and then the Spotlight went
through, and the world opened up:

> `Encore: 3 — a buffer and not a bank: after Block it absorbs incoming damage
> before HP. Cards spend it, and a Salon member spends 1 each time it performs`
> `Guest Cast 1 (buff) — Companion cards are Spotlighted: 50% stronger printed
> damage and Block, no Fanfare. Lasts until the Spotlight moves.`

and `Lynette` re-printed from "Gain 5 Block" to **"Gain 7 Block"**, `Sayu` from
"Deal 4" to **"Deal 6"**. The buff rewrites the card faces. That is the single
best legibility thing in the kit and I want to say so plainly.

**Alternative rejected:** the pure-tempo line, `Soloist` + `Soloist` + `Sayu` =
16 damage and no block. I rejected it because the Spotlight is stated to last
"until the Spotlight moves" — i.e. it is a one-off purchase, not a per-turn
tax — so paying for it on the turn the enemy is weakest is strictly better than
paying for it later. That was a genuine decision and it hinged on one clause of
printed text.
**Second alternative rejected:** `Lynette` for block over `Sayu` for damage. 12
incoming, 7 block, 3 Encore buffer — the arithmetic said I would eat 2. I ate
exactly 2 (62 → 60). Encore behaved exactly as printed.

### Round 2

Enemy dropped to Attack 6 + Defend. Played `The Guest List` (1, refunds 1) →
`Freminet — Pers, Deploy!` (1) → `Kujou Sara — Tengu Stormcall` (1) →
[the Spotlight test, below] → `Stage Presence` (1).

`Freminet` applied Cryo; `Sara` hit Electro into it and **Superconduct** fired
for Vulnerable 2. Nibbit 38 → 20.

**Alternative rejected:** `Undercurrent` (2 energy, 6 AoE at the time) into a
single 38-HP target. Two 1-cost companions of different elements paid better
than the AoE card *and* set off a reaction, which is the interesting shape of
this kit — a real, elemental decision, and the first one the run offered.

**The disagreement between screen and outcome (round 2).** With **0 Encore** —
the Encore line had vanished from the status block entirely after round 1's
absorption — `Ethereal Spotlight` printed **no `CANNOT BE PLAYED` line at all**,
unlike round 1 on the same zero. I played it to see what would happen. It was
**accepted**, it **Exhausted** (exhaust pile 3 → 4), and **nothing changed**:
`Guest Cast` stayed at 1, no Encore moved, no number on any card face moved. A
card that prints "Costs 2 Encore" was spent for free and did nothing, silently.
The refusal that had been correct on turn 1 was simply gone.

### Round 3

Enemy on Empower, no damage incoming — a free setup turn. Played `Salon Début`
(1) → `Aria` (1) → `Suffering for Art` (0) → `Soloist` (1).

`Salon Début` is where the kit finally explains itself, and it explains all of
it at once — Salon, three named members with their perform/Evoke numbers,
Fanfare, and a 70-point **Burst Energy** meter. `Surintendante Chevalmarin`
joined and performed immediately for 4 into the enemy's 5 Block.

**Alternative rejected:** attacking with all three energy. I took the setup line
*because* the intent said Empower — the enemy's own intent is what made a
tempo-negative turn correct. That is the best-designed decision I met all round,
and it came from base-game intent legibility rather than the kit.

**Ordering mistake I made, and it was mine, not the kit's:** I played `Salon
Début` *before* `Aria`, so Chevalmarin performed on 0 Encore and, per its own
text, "a member with no Encore to spend performs at three-quarters." The screen
told me the rule; I read it after I had already paid for it.

### Round 4

Enemy 9 HP, intending 14. Played `Freminet — Pers, Deploy!` (1, previewing
**"Reaction preview: Frozen"** on the enemy's Hydro aura) and it ended the
fight.

The **reaction preview** printed on the card face is excellent — it names the
reaction, the element pair, and the effect, on the card, before you commit.

**Alternative rejected:** `Sayu` (8 + swirl). Freminet's 11 was lethal on its
own and Sayu's swirl had nothing worth moving.

**Reward:** 18 gold; card choice offered four, the fourth a Companion exactly as
the glossary promised. Took `Chevreuse — Interdiction Fire` [Pyro] over
`Compose Herself` (draw 2), because a fourth element opens Melt/Vaporize/
Overloaded and because a Companion card is also a lever on the Salon.

---

## Fight 2 — Shrinker Beetle, HP 38/38

### Round 1

Enemy on `DebuffStrong`, no damage incoming. Played `Aria` (1) → `Ethereal
Spotlight` (0) → `Chevreuse` (1, 7 → **10** spotlighted) → `Soloist` (1).
38 → 22.

**Alternative rejected:** `Stage Presence` for 6 block. The intent said Debuff,
not Attack, so block was dead. Same shape of decision as fight 1 round 3.

Note taken here: with `Guest Cast` up, no Fanfare appeared at all, matching the
buff's own "no Fanfare" clause. The Spotlight's price is legible and real.

### Round 2

The debuff landed: `Shrink -1 (debuff) — While Shrinker Beetle is alive, your
Attacks deal 30% less damage.` **Every attack face in my hand re-printed
downward in the same beat** — `Freminet` 9 → 6, `Soloist` 6 → 4. I could read
my whole turn off the cards without doing arithmetic. That is the second thing
the kit does very well.

Played `An Invitation` (0, gave a second `Freminet`) → `Freminet` (1,
**"Reaction preview: Melt"**, 1.75× into the Pyro aura Chevreuse left) for 11.
22 → 11. Then `Lynette — Enigmatic Feint` (1, 7 block) → `Freminet` (1) →
end turn.

**Alternative rejected:** `Freminet` + `Soloist` = 10 damage, leaving the Beetle
on 1 HP and eating its 7. I could not kill it either way (11 HP, 10 available),
so the block line strictly dominated: same "it lives", 7 damage less taken. Took
**0 damage this fight**.

This was the round the kit's engine actually sang: Chevreuse's leftover Pyro
aura turned a 6-damage card into an 11-damage card, and the card told me it
would before I played it.

### Round 3

Beetle 5 HP, intending 13. My hand had **no attack in it** — `Ethereal
Spotlight`, `Suffering for Art`, `Regal Bearing`, `The Guest List`, `Salon
Début`, `Stage Presence`.

Played `Salon Début` (1). The deployed member performed on arrival and killed
the Beetle outright.

**Alternative rejected:** `The Guest List` → play the generated Companion for
damage, then `Stage Presence` for block. I picked `Salon Début` because Deploy
performs *immediately* and I could not know what `The Guest List` would hand me.
This was a real choice with a real read behind it — "a member joins and performs
at once" is the clause that made it.

**Reward:** 10 gold; took `Lynette — Magic Trick: Astonishing Shift` (1: swirl +
4 AoE) over `House Call` and `Stage Combat`, because it is a Companion (so it
also performs the front Salon member), it is AoE, and swirl spreads an aura for
later reactions — three jobs on one 1-cost card.

---

## Fight 3 — Leaf Slime (S) 12, Leaf Slime (M) 35, Twig Slime (S) 8

### Round 1

Played `Suffering for Art` (0) → `Ethereal Spotlight` (0) → `An Invitation` (0)
→ `Lynette — Bogglecat Box` (1, draw 2) → `Chevreuse` (1, 10) on Leaf Slime (S)
→ `Soloist` (1, 6) on Twig Slime (S).

**Alternative rejected (Encore source):** `Aria of Recompense` (1 energy, 5
Encore) versus `Suffering for Art` (0 energy, 1 HP, 3 Encore). Energy was the
binding constraint and 3 Encore is one Spotlight; the HP was the cheap currency.
A genuine, if small, decision, and it exists only because the kit gives Encore
two prices.

**Alternative rejected (targeting):** the obvious line was 16 damage into Leaf
Slime (S) to kill it and stop its status cards. I instead **chipped both small
slimes to exactly 2 HP** and left them alive, planning a 6-damage AoE sweep the
next turn. That is a real, satisfying decision, and it worked.

### Round 2

Played `Lynette — Magic Trick` (1, spotlighted to **6 damage to ALL**, swirling
the Pyro aura first) — killed both 2-HP slimes and left Leaf Slime (M) wearing
Pyro. Then `Freminet` (1, **Melt**) for 15 and `Stage Presence` (1).

**Alternative rejected:** `Undercurrent` (2 for 4×3 AoE) instead of Magic Trick
+ Freminet. Magic Trick swirled the aura *onto* the survivor, which is what made
Freminet's Melt possible. The two-card line was worth more than the one-card
line by exactly the amount the swirl set up — a genuinely good puzzle.

### Round 3

Leaf Slime (M) at 14, giving status cards. Played `Salon Début` (1, Crabaletta
joined and performed for 4 + Hydro) → `Soloist` (1) → `Soloist` (1). Kill.

**Alternative rejected:** none worth naming. Three energy, one target, twelve
damage of attacks in hand and a 14-HP enemy — this turn presented no decision
and I want that on the record.

**Reward:** 16 gold; took `Charlotte — Framing: Freezing Point Composition`
(1: 4 damage, draw 1, Cryo) over `Compose Herself`, because a Companion that
cycles is also a free Salon performance every time it is drawn.

---

## Fight 4 — Inklet 14, Inklet 17, Inklet 13 (all `Slippery 1`) — **unfinished**

`Slippery 1 (buff) — The next time Inklet loses HP, it only loses 1 HP
instead.` A clean, printed puzzle: three enemies each with a one-shot damage
sponge, so multi-hit and AoE strip it for free.

### Round 1

Played `Salon Début` (1, Crabaletta joined, performed) → `Freminet` (1) →
`Charlotte` (1). Each Companion play performed Crabaletta again; Fanfare climbed
2 per performance to 6. Inklets ended at 14 / 2 / 8.

**Alternative rejected:** open with `An Invitation` + `The Guest List` to stack
Companions before deploying. I had 3 energy and Deploy performs on arrival, so
front-loading the member paid immediately. Correct read: three performances came
out of one `Salon Début`.

**What I could not see:** Crabaletta's performances chose their own targets and
I was never told which enemy they would hit. Inklet (3) took 5 and came out
wearing Hydro; nothing on any screen said that was going to happen or let me
aim it.

Ended turn and took 12 — HP 53 → 41.

### Round 2

Played `Undercurrent` (2, 2 damage ×3 to ALL) — the Slippery-stripper — then
`Stage Presence` (1, 6 block), then ended turn. Undercurrent killed the 2-HP
Inklet and stripped Slippery off the rest.

**Alternative rejected:** `Lynette — Enigmatic Feint` (5 block + swirl) instead
of `Stage Presence` (6 block). Unspotlighted this fight, Lynette's block had
fallen from 7 to 5 and there was no aura worth moving, so the plain block card
won. Worth saying: the Spotlight's absence changed which of two block cards was
correct, which is the *right* kind of consequence.

Took 10 through the 6 block. **HP 31/78, budget spent, stopped.**

---

## The kit, after 3 completed fights and 2½ rounds of a 4th

### (a) Which decisions felt like real choices, and what they traded off

Four kinds, and three of them are good.

1. **Spend the turn on the Spotlight, or on the enemy.** `Ethereal Spotlight`
   arrives free every turn but is gated behind Encore you must buy, so the real
   cost is the `Aria` (1 energy) or `Suffering for Art` (1 HP) in front of it,
   plus the "no Fanfare" clause it turns on. Because it lasts "until the
   Spotlight moves", the decision is *when*, not *whether* — and the answer is
   "on the turn the enemy's intent is harmless", which makes it read off the
   board. Good.
2. **Which element into which aura.** Freminet/Chevreuse/Sara/Charlotte and the
   Hydro the Salon leaks give you a genuine ordering puzzle, and the
   `Reaction preview:` line on the card face means you can *see* the payoff
   without memorising the reaction table. Fight 2 round 2 (Chevreuse's leftover
   Pyro turning Freminet from 6 into 11) and fight 3 round 2 (swirl the aura onto
   the survivor, then Melt it) were the two most enjoyable turns of the round,
   and both were pure kit.
3. **Kill now, or chip both and sweep.** Fight 3 round 1. This is base-game
   shaped, but the kit's cheap AoE Companions are what make it available.
4. **Encore: buffer or currency.** The status line says it outright — "a buffer
   and not a bank". Every point you spend on a Spotlight is a point of HP you
   don't get back. Real, but small: across four fights it only ever mattered
   once, on 3 points.

### (b) What felt automatic, and what never seemed worth playing

- **`Soloist's Solicitation` is the automatic card.** "Deal 6 damage" for 1, no
  element, no tag, no interaction with Salon, Encore, Fanfare or Spotlight. It
  is what I played with leftover energy and I never once thought about it.
  Fight 3 round 3 is a turn that presented no decision at all, and it was two
  Soloists and a `Salon Début`.
- **`Regal Bearing` I never played once** in four fights, and it was in my hand
  five separate times. 3 block + 1 Weak for 1 next to `Stage Presence`'s flat 6
  block for 1 — the Weak was never worth 3 block against A2 act-1 numbers.
- **`Ethereal Spotlight` after the first one each fight** is dead: the relic
  hands you a new one every turn, but the buff it grants "lasts until the
  Spotlight moves", so copies 2..N do nothing. It is Ethereal, so it disappears
  on its own — but it still occupies a hand slot and a read every single turn
  for the rest of the combat, and (see (c)) the second one is playable and
  silently wasted.
- **Fanfare did nothing.** It climbed to 6, decayed 20% a turn, and its own text
  says "Cards read it and none spends it" and "Member numbers gain +1 per 10
  Fanfare you hold" — I never held 10, so it was a number I watched and never
  used.

### (c) What I could not understand, or that contradicted its own printed text

1. **`Ethereal Spotlight` at 0 Encore is refused on one turn and free on the
   next.** Fight 1 round 1: `CANNOT BE PLAYED: you have no Encore, and this
   costs 2`. Fight 1 round 2, same 0 Encore: no refusal line, the play accepted,
   the card exhausted, and **nothing happened** — no Encore moved (I had none),
   `Guest Cast` stayed 1, no card face changed. Either the cost is not being
   checked once a Spotlight is already out, or the "already spotlighted" case is
   swallowing the card silently. Whichever it is, the screen and the outcome
   disagree, and a card that prints a price got spent for free and for nothing.
2. **`Freminet — Pers, Deploy!` never deployed anything.** The title says
   Deploy; the screen glossed **Deploy — "A member joins and performs at once"**
   on the very screen the card sat on; the card's own body says only "Deal 6
   damage". I played it six times across four fights and no member named Pers,
   or any member, ever joined the Salon from it — the `Salon Member` buff only
   ever appeared from `Salon Début`. Either the card lost its Deploy, or the
   glossary is keying off the word in the title. Both readings are a defect in
   what the player is told.
3. **Burst Energy is invisible and I never saw it move.** The gloss inside
   `Salon Début` says an Elemental Skill grants 5 and "every Elemental Reaction
   grants 5", and that at 70 the Burst card enters your hand. It read **"You
   hold 0 of 70 Burst Energy"** in fight 3 round 3 — *after* I had set off
   Melt and Swirl in that same fight — and there is **no Burst line anywhere on
   the combat screen**. Encore and Fanfare both get their own status rows the
   moment they are nonzero; Burst never does. So a 70-point meter that gates the
   character's signature card is only readable by holding one specific card, and
   on the one occasion I could read it, it said zero when by its own rule it
   should have said ten. At 70-per-fight against ~10 a fight, I would not expect
   to ever see a Burst.
4. **Salon members' targets are not shown.** Crabaletta chose its own enemy in
   fight 4 and left a Hydro aura on a body I had not picked. In a kit whose best
   decisions are "which element lands on which aura", an untargetable source of
   Hydro is actively working against the part of the kit that is good.
5. **Encore's dual role is stated but never reconciled.** "A buffer and not a
   bank … Cards spend it, and a Salon member spends 1 each time it performs."
   Nothing tells you which happens first when an attack lands on the same turn a
   member performs, and nothing shows the buffer's size in the damage preview.
6. **Small arithmetic I could not close:** fight 1 round 2, Freminet 9 +
   Sara 6 into an enemy with no Vulnerable at the time of the first hit took
   Nibbit 38 → 20, i.e. 18, not 15 or 17. I could not make the printed numbers
   and the printed Strength reach 18 from anything on screen.

### (d) The card I never wanted to play, and the one I was happiest to draw

- **Never wanted:** `Regal Bearing` — 3 block and 1 Weak for 1 energy, sitting
  in the same deck as `Stage Presence`'s 6 block for 1. Five appearances, zero
  plays. (`Soloist's Solicitation` I played constantly and never *wanted* to;
  it is the card I would cut first.)
- **Happiest to draw:** `Freminet — Pers, Deploy!`. Not for the 6 damage — for
  the **`Reaction preview: Melt` / `Frozen`** line that appears on its face the
  moment an aura is up. It is the one card that made me look at the board before
  looking at my hand. (Runner-up: `Lynette — Magic Trick: Astonishing Shift`,
  which does three jobs for one energy and made fight 3 round 2 a puzzle.)

### (e) Did the first turn of the first fight already present a decision?

**Yes, and a good one — but only because of a refusal message.** The opening
hand held a free card I could not play, and `CANNOT BE PLAYED: you have no
Encore, and this costs 2` is what told me the turn's real question: pay one of
my three energy for `Aria of Recompense` to unlock the free card and buy a
combat-long 50% buff on my Companions, or dump 16 damage into a 44-HP enemy and
buy nothing. I chose the setup, ate 2 HP for it, and it paid off two fights
running.

The caveat: I made that choice **without being told what Encore was**. The
Neow screen and the opening hand both used the word; neither defined it. The
definition — the good, sharp one-liner "a buffer and not a bank" — only appears
in the status block *after* you already have some. The first real decision of
the run is made blind, and it does not need to be.

---

## Non-blindness declaration

**Repo files read: none.**

I am an Opus (Claude) model. The kit under test was authored by a different
Claude model; I had no prior exposure to it, and nothing in this round came from
anywhere but the bridge's printed screens.

Commands run outside the two allowed forms:

1. `python -m understudy.embark --character KLEEMOD-FURINA --lane 2` — once, the
   embark the coordinator's notes instruct. It printed the seed, the stamp, the
   lane/port and the screen type, and nothing about the kit.
2. `mkdir -p review/qa/furina-reframe-round-4-2026-09-04` — once, in the same
   Bash call as my first `observe`, to create the record directory.

Every other game command was `GITS_LANE=2 python -m understudy.blindplay
observe` or `GITS_LANE=2 python -m understudy.blindplay act "<command>"`.
Several of those were piped through `sed -n '<range>p'`, `grep -A/-B`, `tail`
and `echo ---` **purely to trim the output I re-read**; the piping never
requested anything the raw command would not have printed. I ran no `harness
state`, no `scenario`, no `staged_turn`, no `soak`, and no other understudy
subcommand.

Tools used: **Bash** (all of the above) and **Write** (once, for this file).
No Read, no Grep, no Glob, no Agent, no web access.

Budget accounting: 70 `act` calls, all accepted; 0 refusals; 0 stalls; no
`TOOL-BLOCKED` screen. `observe` calls are not counted against the action cap
per the brief.
