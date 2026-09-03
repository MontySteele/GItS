# KLEEMOD-KLEE — blind seat, lane 2, run 2, act 1

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, round 8, run 2, **first seat of three** (act 1 only).
- **Lane:** 2.
- **Character:** KLEEMOD-KLEE.
- **Run seed:** never printed on any screen I saw.
- **Act:** 1. Map printed 16 floors and, at the top of the act: **Ceremonial Beast**.
- **Actions:** **197 accepted, 1 refused.** The single refusal was a `confirm`
  after the "Brain Leech" card pick, which had already auto-confirmed — the screen
  said so and I moved on. No refusal was ever repeated, and no tool error occurred
  at any point.
- **Termination reason:** **stop condition (1)** — the act-1 boss was resolved and
  its reward screen handled, so the lane stands on the act-2 map screen. Budget
  was not a factor (197 of 250).
- **Where the run stands:** **ACT 1 CLEARED.** Lane 2 is on the **act-2 map**,
  first node `Ancient (path 1)`, nothing selected. **HP 31/62. Gold 163.
  Potions 3/3.** Nothing is mid-screen and no choice is half-made.

### HP trajectory (every reading the screens printed, in order)

`62/62` → `58/62` `58/62` `58/62` (fight 1) → `58/62` `58/62` `53/62` `53/62`
`51/62` `51/62` (fight 2) → `51/62` `51/62` (fight 3) → `51/62` `51/62` `43/62`
`35/62` `35/62` (fight 4) → **rest 35 → 53** → `53/62` `45/62` `45/62` `45/62`
(fight 5) → `45/62` `45/62` `34/62` (fight 6) → `34/62` `22/62` `22/62`
(fight 7) → **rest 22 → 40** → `40/62` `40/62` `34/62` `31/62` `31/62`
(**boss**) → final **31/62**.

Total damage taken across seven fights and a boss: **65**, of which 36 came in the
two fights (4 and 7) where the opening hand held no Block card.

### Gold / potions / relics (exactly as printed)

- **Gold: 163.** Traced: the five gold rewards printed *before* the shop were
  `15 + 20 + 16 + 10 + 13 = 74`, yet the shop opened saying **`You have 223
  gold`** (finding 4). Spent 187 there (38 + 74 + 75), leaving 36; then `14`
  (fight 6) + `13` (fight 7) + `100` (boss) = **163**.
- **Potions: 3 of 3 slots full**, none ever used:
  - **Block Potion** — Gain 12 Block.
  - **Weak Potion** — Apply 3 Weak.
  - **Strength Potion** — Gain 2 Strength.
  - (`Stable Serum` and the boss's `Gambler's Brew` went unclaimed — slots full.)
- **Relics**, exactly as the battle screen's "Your relics" block prints them:
  - **Pounding Surprise** — Whenever a Bomb goes off, gain 1 Spark.
  - **Large Capsule** — Upon pickup, obtain 2 random Relics. Add an additional Strike and Defend to your Deck.
  - **White Star** — Elites drop an additional Rare card reward.
  - **Oddly Smooth Stone** — Start each combat with 1 Dexterity.
  - **Festive Popper** — At the start of each combat, deal 9 damage to ALL enemies.
  - **Vambrace** — The first time you gain Block from a card each combat, double the amount gained.

  White Star never paid: no Elite was reachable on any fork the map offered me.

### Final deck (24 cards)

Strike ×4 · Defend ×4 · Kaboom! · Jumpy Dumpty · Ka-pow! · Duck and Cover ·
Powder Charge · **Pop! ×3** · Nicole — Revelation, Uncreated Light ·
**Sparks 'n' Splash+** (upgraded, cost 1) · Sparks 'n' Splash (cost 2) ·
Explosives Workshop · Barbara — Melody Loop · The Big One · Chain Fuse ·
**Spoils Map** (unplayable quest card). Clumsy was removed at the shop.

### Starting deck, reconstructed from faces printed in hand

Starting deck was 12 cards (5 in hand + 7 in draw, round 1). Fully determined by
round 4:

- **Strike** ×4 — cost 1, attack, "Deal 6 damage."
- **Defend** ×4 — cost 1, skill, "Gain 6 Block."
- **Kaboom!** [Pyro] — cost 1, attack, "Deal 7 damage." (Applies Pyro)
- **Jumpy Dumpty** — cost 1, skill, "Place a Bomb 8. When it goes off, place a Mine 3 on ALL enemies."
- **Ka-pow!** [Pyro] — cost 0, attack, "Retain. Set off. Deal 4 damage."
- **Duck and Cover** — cost 1, skill, "Gain 6 Block."

Two of those (1 Strike, 1 Defend) were added by Large Capsule, so Klee's own
starter is 3 Strike / 3 Defend / Kaboom! / Jumpy Dumpty / Ka-pow! / Duck and Cover.

Added in act 1:

- **Powder Charge** — cost **1 Spark**, skill, "Place a Bomb 6." (fight 1 reward)

---

## Screen by screen

### Neow

```
- Neow's Torment      Add 1 Neow's Fury to your Deck.
- Neow's Talisman     Upgrade 1 of your Strikes and 1 of your Defends.
- Large Capsule       Obtain 2 random Relics. Add an additional Strike and Defend to your Deck.
```

**Chose Large Capsule.** Reasoning: blind to the character, two relics is the
largest unknown-upside swing on offer, and one upgraded Strike + one upgraded
Defend is the smallest. The screen never said which two relics it gave — the
first battle screen was the only place I learned them. Reading the four relics
back against the deck, the two randoms were **White Star** and **Oddly Smooth
Stone**; **Pounding Surprise** is Klee's own starter (it is a pure Bomb relic)
and **Large Capsule** is the Neow relic itself.

*Granted without saying so:* the relics were never named at the moment of the
choice. I picked "2 random Relics" and only found out what they were one screen
into a fight.

### Map (act 1)

Two openings, both Monster. Path 1 led on to "Unknown, Monster", path 2 to
"Monster, Monster". Took path 1 for the Unknown. The map prints no HP anywhere,
as briefed. Boss named at the top of the act: **Ceremonial Beast**. Floors 9 =
four Treasures; floors 10, 13, 14 carry the Elites; floor 15 is four RestSites.

### Fight 1 — Fuzzy Wurm Crawler (HP 55)

Opening state: HP 62/62, Energy 3/3, **Dexterity 1** (Oddly Smooth Stone),
**Spark 1**. Enemy badge: `Intent: Aggressive (Attack) — the number on its icon
is 4`.

The glossary on this screen is where the whole character is explained:

```
Bomb    — A charge on an enemy: each grows 4 a turn, goes off only when Set off,
          all at once. Its hit takes the enemy's debuffs, not yours.
Set off — Every Bomb on the target goes off first, one at a time, each a Pyro hit
          for its size.
Spark   — Some cards cost Sparks instead of Energy, with no cap. Gone after combat.
Mine    — A Bomb that also goes off when its enemy attacks you, before the hit lands.
```

**Round 1.** Hand: Kaboom!, Strike ×3, Jumpy Dumpty. Played Jumpy Dumpty
(Bomb 8), Kaboom! (7), Strike (6). **Predicted 13 damage. Enemy 55 → 42.**
Exact. Screen then printed `Bomb 8 (buff) — Set off here deals 8 Pyro damage`
and `Pyro Aura 2 (aura)`.

Note I had no way to detonate on round 1 — nothing in the opening hand said
"Set off". I played the bomb anyway on the reading that a bomb loses nothing by
waiting, because it grows 4 a turn whether or not it is cashed out.

**Round 2.** Took 4 (HP 62 → 58). Bomb 8 → 12, Pyro Aura 2 → 1. Drew **Ka-pow!**
— `cost 0, Retain, Set off, Deal 4 damage` — the detonator. Enemy intent was
`Empower (Buff)`, so no block needed.

Played Ka-pow! then Strike. **Predicted 12 (bomb) + 4 + 6 = 22. Enemy 42 → 20.**
Exact. Three things happened that the card did not itself print:
- Spark went **1 → 2** (Pounding Surprise, on the Bomb going off).
- **Mine 3** landed — Jumpy Dumpty's rider, paid a full round after the card left my hand.
- The Pyro Aura was **refreshed 1 → 2** by the Pyro bomb hit, exactly as the aura line said it would be.

Two energy went unspent because the rest of my hand was three block cards and
nothing was incoming.

**Round 3.** Enemy printed `Strength 7 (buff)` and `Intent: Aggressive — the
number on its icon is 11`. Two Empowers had bought +7 Strength; base 4 + 7 = 11,
and the icon number already had the Strength folded in. Mine 3 → **Mine 7**.

Hand: Defend ×2, Jumpy Dumpty, Duck and Cover, Strike — **no detonator**. So the
only cash-out available was the Mine's own trigger. Played Strike + Defend +
Defend. **Predicted:** 20 − 6 = 14, then the Mine goes off for 7 when it attacks
→ 7 HP, and 2 × (6 Block + 1 Dexterity) = 14 block ≥ 11 damage, so 0 taken.

**All three landed exactly:** enemy at **7/55**, HP still **58/62**, Spark 2 → 3.

I passed on Jumpy Dumpty here on purpose: a second Bomb 8 needing a detonator I
did not hold was worth less than the 4 HP that the third block card saved.

**Round 4.** Ka-pow! (set off — but the Mine had already gone off, so 4 only) +
Strike (6) = 10 into 7 HP. Dead.

**Result: fight 1 won at 58/62, 0 damage taken after round 1.** I finished the
fight holding **3 Spark, all of them unspendable** — nothing in the 12-card
starter prints a Spark price.

### Fight 1 reward

`15 Gold`, `Block Potion`, and a card choice — all three taken.

```
- Sizzle [Pyro] — cost 1, attack
    Set off. Deal 6 damage. If a Bomb triggered an Elemental Reaction this turn,
    deal 6 additional damage.
- Powder Charge — cost 1 Spark, skill
    Place a Bomb 6.
    Its 1 Spark is a price, not an Energy cost: an effect that makes a card free
    to play, or cuts its cost to 0, covers Energy only, and the 1 Spark is still spent.
- Catalytic Converter — cost 1, power
    Whenever one of your Bombs triggers an Elemental Reaction, gain 1 additional Spark.
- Barbara — Let the Show Begin♪ [Hydro] — cost 1, skill
    Gain 6 Block. Apply Hydro.
```

**Chose Powder Charge.** The fight had just shown me the exact hole it fills: I
banked 3 Spark and spent none, and my turns ran out of *energy*, not cards
(round 2 ended with 2 unspent energy and a hand of blocks). Powder Charge costs
no energy at all, and Pounding Surprise refunds its Spark every time a bomb
cashes out. Its own glossary box names the relic — `Pounding Surprise grants
more` — which is the game telling you the two are built together.

Passed on Sizzle (a strictly-better Strike and a second detonator, the safe
pick), Catalytic Converter (dead: my bombs are Pyro and I own no non-Pyro aura
source, so my bombs cannot trigger a reaction at all), and Barbara (the only
non-Pyro aura on offer, and therefore the only card that would have switched
Catalytic Converter and Sizzle's bonus clause on — but on its own it is a Defend
with a rider).

### Fight 2 — Twig Slime (S) 8 / Twig Slime (M) 27 / Leaf Slime (S) 14

Entered at 58/62.

**Round 1.** Incoming 4 (Twig S) + 3 (Leaf S); Twig M's badge read
`Intent: Strategic (StatusCard) — the number on its icon is 1`. Hand was three
Defends, a Strike and Ka-pow! with no bomb on the board, so Ka-pow! was just a
0-cost 4-damage attack. Killed Twig Slime (S) with Ka-pow! (4) + Strike (6) = 10
into 8 HP, removing 4 incoming, and one Defend covered the Leaf Slime's 3.
**Took 0.**

**Round 2.** Drew **Powder Charge**. Twig M now `Attack 11`. Played, in order,
Powder Charge (Bomb 6, **zero energy**, 1 Spark), Jumpy Dumpty (Bomb 8),
Kaboom! (7 damage), Defend — **all four cards on three energy**, because Powder
Charge takes none. That is the pick paying off immediately.

Predicted: Twig M 27 → 20, bombs 6+8 = 14 on it, block 7 vs 11 → 4 taken → 54 HP.

Observed: Twig M **20/27** ✓, `Bomb 22 (buff) — Set off here deals 22 Pyro
damage. Bombs here: 2` ✓ (each of the two grew 4), and **HP 53/62 — 5 taken, not
4.** The block was 6, not 7. See finding 1.

Also: with Spark spent, the `Spark` line **disappeared from the status block
entirely** rather than printing `Spark 0`.

**Round 3.** Twig M `Attack 11` + Leaf S `Attack 3` = 14 incoming, and no
detonator in hand. Played Duck and Cover + Defend, then read the status block
before ending the turn:

```
- HP 53/62
- Block 12
- Energy 1/3
- Dexterity 1 (buff) — Increases Block gained from cards by 1.
```

**Two 6-Block cards, Dexterity 1 active, Block 12.** Then Strike into Leaf Slime
(14 → 8). Predicted 14 − 12 = 2 taken → **HP 51/62** ✓.

**Round 4.** `Bomb 30` on Twig M, both slimes on `Strategic (StatusCard)`, so no
damage was coming and no block was worth playing. Struck the Leaf Slime to 2 and
ended. I could count the draw pile exactly here — 5 left, and by elimination
those five were Strike, Defend, Kaboom!, **Ka-pow!**, Slimed — so I knew the
detonator was guaranteed next turn.

**Round 5.** Drew all five as predicted, Ka-pow! among them. `Bomb 38` on a 20 HP
slime. Ka-pow! set it off — 38 into 20, **18 damage thrown away** — then Strike
finished the Leaf Slime.

**Result: fight 2 won at 51/62.** The slimes put **2 Slimed** into the deck
(`cost 1, status — Draw 1 card. Exhaust.`), which is a much gentler Slimed than
its name suggests: it replaces itself and removes itself for 1 energy.

The shape of this fight is the clearest thing act 1 showed me: **the bomb sat at
22, then 30, then 38 for three straight rounds** because the deck holds exactly
one card that says "Set off".

### Fight 2 reward

`20 Gold`, `Weak Potion`, and:

```
- Run Away! — cost 0, skill
    Gain 3 Block. If a Bomb went off this turn, gain 4 additional Block.
- Bang Bang! [Pyro] — cost 2 Sparks, attack
    Set off. Deal 8 damage. Place a Bomb 4.
- Explosives Workshop — cost 1, power
    At the start of your turn, your Bombs grow by 1 more.
- Nicole — Revelation, Uncreated Light — cost 2, power
    At the start of your turn, gain 5 Block, and 2 Strength if you ended last turn with Block.
```

**Chose Nicole.** Two fights of evidence pointed at defence: my whole block suite
is 6-a-card, and the one relic that was supposed to improve it (Oddly Smooth
Stone → Dexterity 1) demonstrably does not. Nicole is 5 Block every turn with no
card and no condition, and the Strength half compounds. I also had the energy for
a 2-cost power specifically because Klee's key cards are free — Ka-pow! is 0 and
Powder Charge costs Spark, not Energy.

Against it: **Strength does not touch bomb damage.** The Bomb glossary says the
hit "takes the enemy's debuffs, not yours", and I read that as bomb damage being
computed off the enemy's side of the ledger, not my Strength. So Nicole boosts
only Strike / Kaboom! / Ka-pow!, which is the small half of my damage.

Passed on Bang Bang! reluctantly — it is the second detonator I had just spent a
whole fight wishing for, and it costs zero energy — but 2 Sparks is a price I can
only pay *after* a detonation, which is the very thing I could not reliably do.
Explosives Workshop makes an already-idle bomb bigger, which is not the problem.

### Fight 3 — Shrinker Beetle (HP 39)

Entered at 51/62 with a 9-card draw pile and 14-card deck — which confirmed the
two **Slimed do not persist after combat**.

**Round 1.** Opening hand held both placers *and* the detonator: Powder Charge,
Jumpy Dumpty, Ka-pow!, Strike, Defend. Beetle's intent was
`Strategic (DebuffStrong)`. Because **Ka-pow! has Retain**, holding it costs
nothing, so I placed Bomb 6 + Bomb 8 and struck for 6 rather than cashing 14
immediately. 39 → 33 ✓.

**Round 2** is the sharpest single screen of the act. The debuff landed:

```
- Shrink -1 (debuff) — While Shrinker Beetle is alive, your Attacks deal 30% less damage.
```

and every card face in my hand **rewrote itself**: `Strike — Deal 4 damage`
(6 × 0.7), `Ka-pow! — Deal 2 damage` (4 × 0.7). But the enemy badge still read
`Bomb 22 (buff) — Set off here deals 22 Pyro damage`.

Predicted: the bomb is not my Attack, so Shrink should not touch it — 22 + 2 = 24.

Observed: **33 → 9, exactly 24.** Spark 0 → 2, Mine 3 placed.

**Shrink cut my cards by 30% and did not touch the bomb at all.** That is the
Bomb glossary's "takes the enemy's debuffs, not yours" doing real work, and it is
the best moment the character had: the enemy's whole gimmick is a 30% damage tax
and Klee's main damage route simply does not pay it.

**Round 3.** Beetle at 9 with `Attack 7` and a Mine 3. Two shrunken Strikes
(4 + 4 = 8) took it to **1**, one Defend covered most of the 7. Predicted the
**Mine would kill it on its own turn before its hit landed** — 3 into 1 HP.

It did. The fight ended on the enemy's turn and **I took 0**. Won at **51/62**.

### Fight 3 reward

`16 Gold`, `Strength Potion`, and:

```
- Sorry, Jean... — cost 0, skill — Remove one of your Bombs. Gain Block equal to its size.
- Sparks 'n' Splash — cost 2, power — At the end of your turn, deal Pyro damage to a random enemy equal to the Bombs on it.
- Dig In — cost 1 Spark, skill — Gain 8 Block.
- Fischl — Nightrider [Electro] — cost 1, attack — Deal 7 damage. If Oz is out, he deals 5 Electro damage to a random enemy.
```

**Chose Sparks 'n' Splash**, reading its wording against Ka-pow!'s: Ka-pow! says
"**Set off.** Deal 4 damage"; Sparks 'n' Splash says only "deal Pyro damage …
equal to the Bombs on it" — no *Set off*. If that reading held, it was not a
second detonator but something much better: the bomb stack cashed **every turn
without being spent**. Fight 4 confirmed it (below).

Passed on Fischl specifically because Electro is the *wrong* element to pair with
bombs: `Overloaded — Pyro on an Electro aura … 6 damage to ALL enemies and 1
Weak` is the only reaction on the glossary with **no damage multiplier**, whereas
`Melt` is 1.75x and `Vaporize` 1.5x. Fischl would have made a Bomb 30 deal 6
extra; Barbara's Hydro would have made it deal 45.

### Event — "This or That?"

```
- This — Lose 6 HP. Gain 51 Gold.
- That — Add Clumsy to your Deck. Obtain a random Relic.
```

**Chose That.** A relic beats 51 gold and costs no HP at 51/62 with elites ahead.
As at Neow, **the screen never named the relic it gave me.** I learned it one
screen later, in the next battle: **Festive Popper — At the start of each combat,
deal 9 damage to ALL enemies.** Both Nibbits opened that fight already at 35/44
and 34/43.

Clumsy also stayed unprinted until it appeared in hand: `cost 0, curse —
Unplayable. Ethereal.` It exhausted itself the turn it arrived (`1 exhausted`),
so the curse cost me one dead card in one hand, once.

### Fight 4 — Nibbit 44 / Nibbit 43 (both opened at −9 from Festive Popper)

**Round 1.** Nibbit (1) `Attack 6` + `Defensive (Defend)`; Nibbit (2) `Empower`.
I had Nicole in hand and passed on her, playing Jumpy Dumpty + Defend + Defend
instead: same bomb tempo, 0 damage taken, and Nicole only slips one turn.
`Block 12` again from two 6-Block cards — the third clean reading of the
Dexterity failure. Took **0**.

**Round 2.** Nibbit (2) came out of Empower with `Strength 2` and `Attack 14`.
Powder Charge (free) put a second bomb on it, two Strikes took it 34 → 22, one
Defend ate 6 of the 14. Predicted 8 taken → **43/62** ✓, `Bomb 26` ✓.

**Round 3 — 22 incoming (14 + 8).** Ka-pow! set off Bomb 26 into 22 HP and
killed Nibbit (2) outright, removing 8 of that. Spark → 2.

Here the survivor printed something I cannot account for:

```
- Nibbit — HP 35/44
    Bomb 6 (buff) — Set off here deals 6 Pyro damage. Bombs here: 2, including 2 Mines.
```

**Two Mine 3s on one enemy from one Jumpy Dumpty.** In fight 3 the identical
setup — Jumpy Dumpty + Powder Charge, two bombs, one enemy — produced exactly
`Bombs here: 1, including 1 Mine`. The difference here is that a *second enemy
died* in the same Set off. See finding 3.

Then I tested the Sparks 'n' Splash reading. Played it + Duck and Cover (6 block
vs 14).

Predicted, if Splash does **not** consume: Splash 6 at end of my turn, then the
Nibbit attacks and its 2 Mines (6) go off before the hit, so 12 total, and Spark
should rise by exactly 2 (the two Mines), not 3.

Observed: Nibbit **35 → 23 = 12 exactly**; **Spark 2 → 4**; the Bomb line then
gone (the Mines were spent by the *attack*, not by the Splash); HP 43 → 35.

**So Sparks 'n' Splash pays the whole bomb stack every turn and spends nothing,
and it does not count as "a Bomb going off" for Pounding Surprise.** It is a
free, repeating Ka-pow! that never needs to be drawn again.

It also printed as a **stacking** power: `Sparks 'n' Splash 1 (buff)`.

**Round 4.** Powder Charge (free) put Bomb 6 back on. Strike 6 → 17; end of turn
Splash 6 → **11** ✓, 0 taken behind 12 block, and **Spark 4 → 3** — spent 1 on
Powder Charge and gained none, a second confirmation that the Splash is not a
detonation.

**Round 5.** Nibbit at 11 behind `Block 5`. Ka-pow! (Bomb 10 through the block,
then 4) plus a Strike finished it.

**Result: fight 4 won at 35/62.**

### Fight 4 reward

`10 Gold` and:

```
- Fish-Flavored Bait [Pyro] — cost 1, attack — Deal 4 damage. Place a Bomb 4.
- Pop! — cost 0, skill — Place a Bomb 5.
- Witches' Circle — cost 1, power — Whenever you play a Hexerei card, place a Bomb 3 on a random enemy.
- Prune — Ring-A-Ding-Ding! Hexhunter Chime — cost 1, attack — Deal 8 damage. Swirl. …
```

**Chose Pop!** — with Sparks 'n' Splash down, a bomb is no longer a thing you
have to spend a card to cash; it is a permanent per-turn damage rate. Pop! adds
to that rate for **zero energy and zero Spark**, so it competes with nothing.
Witches' Circle was near-dead (I own one Companion card and its face does not
print the Hexerei tag, so I could not tell whether it would even trigger), and
Prune's Swirl needs a non-Pyro aura I have no way to make.

### RestSite (floor 9) — Rest

`HP 35/62`, `Rest — Heal for 30% of your Max HP (18)` vs `Smith`. Rested to
**53/62**. Run 1 of this round died routing into an Elite at 2 HP, and the map
put `Elite, RestSite, Unknown, Elite` five floors up, so the heal was the pick.

### Fight 5 — Snapping Jaxfruit 31 / Flyconid 48 (both opened at −9)

**Round 1.** Bad hand: Clumsy (unplayable), Strike, Nicole, Defend ×2, against 14
incoming. Nicole had now sat unplayed in three separate hands, so I paid the 8
damage to finally land her: Nicole + one Defend, HP 53 → **45** ✓.

**Round 2.** Nicole delivered, and delivered more than I read:

```
- Block 5
- Revelation, Uncreated Light 1 (buff)
- Strength 2 (buff) — Increases attack damage by 2.
```

Every attack face rewrote upward — `Strike — Deal 8 damage`, `Kaboom! — Deal 9`.

Note the condition. Nicole says "2 Strength **if you ended last turn with
Block**". I ended round 1 having taken 8 through a 6-Block Defend, i.e. with **0
Block left after the enemy hit** — and still got the Strength. So the condition
is checked when **my** turn ends, before the enemy attacks, not on what survives
the enemy's turn. That is a defensible reading of the words, but it is the
generous one and the screen does not say which it means.

Block 5 already covered the only incoming attack (5), so all three energy went to
killing the **Empowering** Jaxfruit: Kaboom! 9 + Strike 8 + Strike 8 = 25 into 22.
Dead, and its Empower never resolved. Took **0**, ended with 5 Block → Strength
went **2 → 4**.

**Round 3.** The Flyconid's debuff landed: `Vulnerable 2 — Receive 50% more
damage from Attacks for 2 turns`. Then the best turn of the act:

- **Pop!** (0 energy) → Bomb 5
- **Powder Charge** (0 energy, 1 Spark) → Bomb 6
- **Jumpy Dumpty** (1 energy) → Bomb 8
- **Defend** + **Duck and Cover** (1 each) → Block 17 with Nicole's 5

**All five cards played on three energy**, `Bomb 19` stacked, `Block 17`. That is
the character working: two of the three bomb placers cost no energy at all, so
the bomb turn and the block turn are the same turn.

Result: **HP stayed 45** against a printed `Attack 12` while I held Vulnerable 2
— so the hit was ≤17, not 12 × 1.5 = 18. Either the printed intent already
includes my Vulnerable or Vulnerable did not apply; I could not tell which. And
`Strength 4 → 6` confirms I ended with Block left over (17 − 12 = 5).

Also landed: `Frail 2 — Gain 25% less Block **from cards** for 2 turns`. Next
turn Nicole still granted the full `Block 5`, so Frail spared power-granted Block
— the "from cards" wording is load-bearing and it is honoured.

**Round 4.** `Strength 6` (Strike 12, Ka-pow! 10), `Bomb 31`, Flyconid at 39.
Ka-pow! alone: 31 (bomb, unaffected by my Strength) + 10 (card, +6 Strength) = 41
into 39. Dead for **zero energy**.

**Result: fight 5 won at 45/62.**

### Fight 5 reward — chose the second **Pop!**

Over `Coven Errand` (Bomb 5 for 1 energy — strictly worse than Pop!),
`Careful Arrangement`, and `Lisa — Lightning Rose` (3 turns of 5 Electro + 1
Vulnerable, Exhaust). Lisa was the tempting one: bombs "take the enemy's debuffs",
so Vulnerable on the target should multiply the whole bomb stack. I passed
because I could not verify that blind, and because the second Pop! is a
zero-cost, zero-Spark card that raises the *rate* Sparks 'n' Splash pays every
single turn.

### Event — "The Legends Were True"

`Nab the Map — Receive the Spoils Map` vs `Slowly Find an Exit — Lose 8 HP.
Procure 1 random Potion`. I was at **3 of 3 potion slots full**, so the second
option was 8 HP for a potion I could not hold. Took the map.

### Treasure (floor 12)

`Vambrace — The first time you gain Block from a card each combat, double the
amount gained.` Taken.

### RestSite (floor 13) — Smith, and the act's best catch

Chose Smith at 45/62 with another RestSite still on the map. **The upgrade screen
prints different numbers from the battle screen for the same cards:**

```
- Defend — cost 1, skill        Gain 5 Block.
- Duck and Cover — cost 1, skill  Gain 5 Block.
```

Every battle screen this act printed `Defend — Gain 6 Block`.

This resolves what I had been recording as a Dexterity bug. Base Defend is **5**;
`Oddly Smooth Stone` grants `Dexterity 1`; the **battle screen prints 6, the
already-adjusted number**. Two Defends therefore give 12, which is 2 × (5+1) and
not 2 × (6+1). Dexterity works exactly as written — but because the in-combat
face silently folds the buff in with no marker, I mispredicted my own HP on
fight 2 round 2 (predicted 54, screen said 53) and only found out four fights
later, at a screen I was under no obligation to open. See finding 1.

Upgraded **Sparks 'n' Splash**, and the screen previewed it honestly:

```
- Sparks 'n' Splash+ (upgraded) — cost 1, power — PICKED
    At the end of your turn, deal Pyro damage to a random enemy equal to the Bombs on it.
    The cost printed on this card is 2; it is showing 1 here, because this copy is upgraded
```

**Cost 2 → 1, text unchanged.** That is the exact fix for the one thing that had
gone wrong all act — 2-cost powers losing the energy contest turn after turn.

The same screen also flagged its own blind spot, which I record because it is
the tool being honest rather than a defect: `Clumsy — on the screen's list
nowhere, and nothing on the feed says why`, and a note that the list was the deck
"as it stood in the last fight (floor 8)".

### Shop (floor 14)

Screen opened with **`You have 223 gold`**. My own tally of every gold reward the
game printed was 15 + 20 + 16 + 10 + 13 = **74**. Roughly 149 gold arrived
without any screen saying so. See finding 4.

Bought, from 223:

- **Explosives Workshop** (38) — "your Bombs grow by 1 more" each turn. With
  Sparks 'n' Splash+ paying the whole stack every turn, growth is paid repeatedly,
  so +1 per bomb per turn compounds rather than accruing once.
- **Barbara — Melody Loop** (74) — "Gain 4 Block. For 3 turns, at the start of
  your turn apply Hydro to the enemy. Exhaust." Bought as a **multiplier on the
  Splash**: Hydro applied at the *start* of my turn, then the Splash's single
  Pyro hit at the *end* of it should Vaporize for `1.5x`. Barbara's start-of-turn
  timing is what made her better than Kaeya (75, Cryo, Melt 1.75x) — Kaeya
  applies at the *end* of the turn, colliding with the Splash's own timing.
- **Card Removal** (75) — removed **Clumsy**.

Left with 36 gold and nothing on the shelf under 36. Deliberately did **not** buy
`Tinder Toss` (51) or `Rapid Fire` (78), both detonators, because Sparks 'n'
Splash+ had changed what a detonator is worth: setting bombs off **spends the
stack**, and the stack is now what pays me every turn. Detonation went from being
my engine to being a finisher only.

### Event — "Brain Leech"

Took `Share Knowledge` (free, 1 of 5) over `Rip the Leech Off` (lose 5 HP).
Offered Powder Charge, Careful Arrangement, Explosives Workshop, Ammo Scavenging,
and **The Big One — cost 3, attack: "Set off for quadruple damage."**

Took **The Big One**. Rejected `Careful Arrangement` ("Move all your Bombs onto
the enemy as one Bomb. It grows by 5") on a number I had measured: the badge
tracks bombs individually and the stack grows **4 per bomb** (`Bomb 19` → `Bomb 31`
with `Bombs here: 3` is +12), so merging three bombs into one would cut my growth
rate from 12 a turn to 4. That card would have quietly halved my engine.

*(One refusal here: the pick auto-confirmed, and my follow-up `confirm` was
rejected because there was nothing left to confirm.)*

### Fight 6 — Twig Slime M 28 / Leaf Slime M 35 / Twig Slime S 11 / Leaf Slime S 12

**Round 1.** Every `Defend` in hand printed **"Gain 12 Block"** — Vambrace.
Vambrace only doubles the *first* Block card each combat, so I paid one energy to
measure it. Played Duck-and-Cover-equivalent order: Defend, then Defend.

**Result: `Block 18` = 12 + 6, and the third Defend still in hand had rewritten
itself to "Gain 6 Block".** So the faces are honest at the instant you read them,
but a hand showing "12 / 12 / 12" is really worth 24, not 36. See finding 2.

Struck the 2 HP Twig Slime (S) dead, Pop! placed a bomb, took **0**.

**Round 2.** Here the run learned what the Spoils Map actually is:

```
- Spoils Map — cost 0, quest
    Unplayable. Marks a site of 600 extra Gold in the next Act.
    CANNOT BE PLAYED: has unplayable keyword
```

It is a **card in my deck**, not a relic — permanently unplayable and, unlike
Clumsy, **not Ethereal**, so it does not exhaust itself and clogs every shuffle
for the rest of the run. The event said "Receive the Spoils Map" and nothing else.

19 incoming with no block card in hand. Fired **The Big One** at the Leaf Slime
(M): `Bomb 9` × 4 = **36 into 26 HP**, dead — quadruple exactly as printed. Took
11 → **34/62**.

**Round 3.** Pop! (0) + Jumpy Dumpty (1) stacked the Twig Slime (M) to `Bomb 23`
against its 19 HP; Ka-pow! (0) set it off and killed it, and Jumpy Dumpty's rider
put a Mine 3 on the last Leaf Slime (3 HP), which then **killed itself by
attacking me**. Predicted the whole sequence; it landed. Took **0**.

**Result: fight 6 won at 34/62.** Reward card: third **Pop!**.

Note the tool being careful, not the game: `Your potion slots are full: 3 of 3. A
potion claimed now has nowhere to go, and the game says nothing when one is
dropped -- so this page will not claim it until a slot is free.` I left
`Stable Serum` unclaimed.

### Fight 7 — three Inklets (15 / 14 / 16), reached through an "Unknown"

**Festive Popper is supposed to "deal 9 damage to ALL enemies" at combat start.
The Inklets opened at 14/15, 13/14 and 15/16 — one damage each, not nine.** And
it was not general damage resistance: the very next Pyro hit, a `Bomb 5` Splash,
took one of them 14 → 9 for the full 5. See finding 5.

**Round 1.** No block card in hand against 12 incoming, so I spent the whole turn
on engines instead: Pop! (0) + **Sparks 'n' Splash+** (1) + **Nicole** (2).
HP 34 → **22**. Splash paid 5 at end of turn.

**Round 2.** Incoming spiked to **23** at 22 HP — the tightest moment of the run.
`Bomb 9` sat on an Inklet at exactly **9 HP**, so **Ka-pow! killed it for zero
energy** and took 10 off the incoming. Nicole's 5 + a Vambrace-doubled Duck and
Cover (12) then covered the remaining 13. Took **0**.

**Round 3.** Two Strikes at 8 (Strength 2) killed one Inklet; Pop! + Jumpy Dumpty
stacked the last one to `Bomb 22` against its 10 HP, and the **end-of-turn Splash
killed it without my spending a card on the kill**. Took **0**.

**Result: fight 7 won at 22/62.** Reward: **Chain Fuse** — "Each Bomb on the
enemy grows by 6" — taken because with the Splash paying the stack every turn,
+6 per bomb is not a one-off, it is a permanent raise to my per-turn damage.

### RestSite (floor 16) — Rest

22/62 with the Boss on the next floor. Rested to **40/62**.

---

## BOSS — Ceremonial Beast (HP 252), entered at 40/62

Festive Popper opened it at **243/252** — the full 9, which is what makes the
Inklet reading in finding 5 an anomaly rather than a misreading of the relic.

**Round 1 — `Intent: Empower (Buff)`.** A free setup turn. Pop! (0) + Jumpy
Dumpty (1) → `Bomb 13`. Deliberately did **not** play Duck and Cover: Vambrace
doubles only the first Block card of a combat, and spending that doubling against
an Empower would have thrown it away. Two energy went unused, which was correct
and still felt wrong.

**Round 2.** The boss printed its clock:

```
- Plow 150 (debuff) — The first time Ceremonial Beast's HP reaches 150 or below,
  it becomes Stunned and loses all its Strength.
- Strength 2 (buff)
- Intent: Aggressive — the number on its icon is 18 — and also: Empower (Buff)
```

So the beast Empowers *every* round while attacking, and there is exactly one
brake: **93 damage away**, and the brake fires the *first* time it crosses. That
is the whole fight — get 93 damage into one beat rather than dribbling across it.

Powder Charge (0 energy) → `Bomb 27`; Nicole (2); Defend (1, Vambrace-doubled to
12). Took 6 → **34/62**.

**Round 3.** `Bomb 39`, boss `Attack 20`, `Strength 4`. Played Pop! **before**
Chain Fuse on purpose — Chain Fuse reads "Each Bomb on the enemy grows by 6", so
the order decides whether it pays on 3 bombs or 4.

Predicted `39 + 5 = 44`, then `+6 x 4 = +24` → **68**. Screen: `Bomb 68 (buff) …
Bombs here: 4` correct. Two Defends (6+6, Vambrace spent) plus Nicole's 5 = 17
against 20; took 3 → **31/62**.

**Round 4 — the turn the fight was won.** `Bomb 84`, boss `Attack 22`,
`Strength 4`, me at 31 HP.

The reasoning: **Sparks 'n' Splash resolves at the end of *my* turn, before the
boss acts.** So if the Splash is what crosses 150, the stun lands before the
attack does and the 22 never arrives. I needed 93; the Splash would carry 84 plus
a Pop! = 89, four short — so a Strike (10, with Strength 4) had to go in first.

Played Pop! (0) → `Bomb 89`; Strike (1) → boss `233`; Sparks 'n' Splash+ (1);
**Barbara — Melody Loop** (1) for `Melody Loop 3` on the enemy.

Predicted: end-of-turn Splash 89 → 144, under 150, stun, zero damage taken.

**Observed: boss at `140/252`, its Strength line gone, `Plow 150` gone, intent
flipped to `Strategic (Debuff)`, and HP still 31/62 — it never swung.**

But the arithmetic was off by 4 in my favour: 233 − 140 = **93**, not 89. The
missing 4 is exactly my `Strength 4`. See finding 6 — the Splash takes my
Strength even though a Bomb set off by Ka-pow! demonstrably ignored my Shrink.

**Round 5.** `Bomb 109`, boss at 140, intent `Strategic (Debuff)` — stunned out
of attacking. Ka-pow! (0 energy) set off 109, plus its own 10 → predicted **21**;
screen said `HP 21/252`. Kaboom! (13) → 8, Strike (12) → dead.

**BOSS KILLED at 31/62, having taken 0 damage in its last two rounds.**

Boss reward: `100 Gold` and a card. Took the **second Sparks 'n' Splash** over
`The Big One` #2, `Alice's Recipe` ("Your Bombs grow twice each turn") and
`Yumemizuki Mizuki`. The reason is the failure I had just lived through: the
engine card did not arrive until **round 4 of a 5-round boss fight**, and until
it did, an 84-point bomb stack sat on the board doing nothing. A second copy
halves the wait, and the power stacks (it prints as `Sparks 'n' Splash 1 (buff)`),
so drawing both is pure upside. Alice's Recipe doubles a stack I might again have
no way to spend.

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

**Whether to detonate at all.** This is the character's one genuine tension and it
is excellent. A bomb is worth more every turn you leave it (`Bomb 8` → `Bomb 12` →
`Bomb 22` → `Bomb 31`), and every card that cashes it destroys it. So every
Ka-pow! is a question: bank the growth, or take the damage now. Fight 1 round 2 I
cashed 12 early for tempo; fight 3 round 1 I held with the detonator *in hand*
because `Ka-pow! — Retain` meant holding cost nothing; boss round 5 I cashed 109
because it was lethal. Three different answers, all forced by the board.

**The turn Sparks 'n' Splash+ arrived, that tension inverted.** From then on
detonating was *wrong* — the Splash pays the stack every turn and spends nothing,
so setting bombs off deletes my income. That single card silently rewrote what
every other card in the deck is for, and it changed my shopping: I passed on both
detonators on the shelf (`Tinder Toss` 51, `Rapid Fire` 78) for that reason.

**Where to point the bombs, and in what order.** Fight 4 round 2, Powder Charge
and two Strikes went into the 14-damage Nibbit rather than the one holding 5
Block. Boss round 3, playing Pop! before Chain Fuse was worth +6.

**The Plow-150 turn.** Reading that the Splash resolves before the enemy acts, and
therefore that 93 damage bought a *free round* rather than just 93 damage, was the
single decision the whole boss fight turned on.

**Rest vs Smith,** twice, with opposite answers (35/62 with Elites ahead → rest;
45/62 with another rest site on the map → smith).

### (b) What felt automatic, and what never seemed worth playing

**Strike and Defend are automatic and almost always the worst card in hand.** A
6-damage Strike next to a `Bomb 31` badge is not a decision. Across the whole act
I never once had to think about whether to play a Defend — it was "do I need
block, yes or no".

**Pop! is automatic in the good way** — cost 0, always correct, never a decision.
So is Powder Charge for most of a fight: it costs no Energy, so it never competes.

**Never worth playing:** the third and fourth block card in a hand (I hit the
incoming number and the rest was dead weight); **Kaboom!** was only ever "a Strike
that hits for 1 more" because I never owned a non-Pyro aura, so its `Applies Pyro`
clause did nothing all act; and **Duck and Cover is a strict duplicate of Defend**
— same cost, same 5 base Block, same text, different name. I could not find one
board state where knowing which of the two I held would have changed a play.

**Nicole nearly joined that list for the wrong reason.** She sat unplayed in
three separate hands because a 2-cost power kept losing the energy contest against
"place a bomb and block". When I finally paid 8 HP to force her down in fight 5,
she was excellent immediately (5 Block a turn, `Strength 2 → 4 → 6`). The card is
strong; its cost is what kept it off the table.

### (c) What I could not understand, or that contradicted its own printed text

- **`Festive Popper` dealt 1 damage instead of 9** to three Inklets. Nothing on
  the screen offered a reason, and it was not damage resistance (finding 5).
- **A single Jumpy Dumpty rider put two Mine 3s on one enemy** in fight 4, where
  the same card in fight 3 put exactly one (finding 3).
- **`Vulnerable 2` on me did not turn a printed `Attack 12` into 18.** I held 17
  Block and took nothing. Either the printed intent already folds Vulnerable in,
  or it did not apply. Two screens later a printed `16` with `Vulnerable 1` was
  also consistent with either. **I could not tell which, and no screen says.**
- **Barbara's Hydro never appeared on the boss.** `Melody Loop 3` sat on the
  enemy and counted down to 2, but the round-5 board printed `Pyro Aura 2` and no
  Hydro. My best reading — and it is a reading, not a measurement — is that my own
  Splash leaves a Pyro aura, and Melody Loop's Hydro then reacts with it and is
  consumed, so a Pyro deck cannot easily hold a Hydro aura for its own Vaporize.
  If that is right, the 74 gold bought nothing, and the screen never said so.
- **`Sparks 'n' Splash` takes my Strength; a Bomb set off does not take my
  Shrink.** Both are "the bomb number", and they follow opposite rules (finding 6).

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted: `Spoils Map`.** `cost 0, quest — Unplayable.` It is a permanent
dead card that, unlike Clumsy, is **not Ethereal**, so it does not remove itself —
it clogs every shuffle for the rest of the run. The event that gave it said only
"Receive the Spoils Map", which reads like a relic.

**Happiest to draw: `Ka-pow!`** — for most of the act. `cost 0, Retain, Set off`
is a card that is never wrong to hold and never costs a turn to use, and in fight
7 it killed an Inklet whose HP was exactly the bomb sitting on it, for zero
energy, at the moment 23 damage was pointed at my 22 HP. **After the upgrade,
`Sparks 'n' Splash+`** replaced it — the boss fight was decided by it resolving
before the enemy's turn.

### (e) Did the first turn of the first fight already present a decision

**Yes, and a good one.** Opening hand: Kaboom!, Strike x3, **Jumpy Dumpty** —
"Place a Bomb 8" — against a 55 HP enemy, with **nothing in hand that could set it
off**. The screen told me bombs "go off only when Set off" and that they grow 4 a
turn. So the first decision of the run was: spend a card on a charge I had no way
to detonate, betting the game would hand me a detonator later. I played it,
reasoning a bomb loses nothing by waiting. Ka-pow! turned up on round 2. That is a
real opening decision made entirely out of printed text, which is more than most
first turns manage.

The counterpoint is that the *second* decision was not: with 3 energy and a hand
of Strikes, "play the two biggest numbers" needed no thought.

### (f) Anything a screen granted or changed without saying so

- **Neow's "Obtain 2 random Relics" never named the relics.** I learned they were
  White Star and Oddly Smooth Stone one screen later, from the battle screen.
- **"This or That?" → "Obtain a random Relic" never named it either.** Festive
  Popper only surfaced in the next fight's relic block.
- **About 149 gold appeared with no screen printing it** (finding 4).
- **Card faces silently rewrite themselves to include buffs and relics.** Defend
  prints 5 out of combat, 6 in combat under Dexterity 1, and 12 while Vambrace is
  unspent; Strike printed 6, then 8, 10, 12 as Nicole's Strength climbed; Strike
  printed **4** under Shrink. There is no marker distinguishing a printed base
  number from a printed adjusted one (finding 1).
- **Jumpy Dumpty's Mine lands a full round after the card leaves your hand**, on
  a target chosen by a rule ("ALL enemies") that resolved differently in two
  fights (finding 3).
- **`Spark 0` is not printed — the Spark line simply vanishes** from the status
  block when the bank empties, which reads as "this character has no Spark
  mechanic" rather than "you have none".

---

## Findings, ranked by sharpness

**1. The same card prints different numbers on different screens, with no marker
saying which number is adjusted — and it made me mispredict my own HP.**
The upgrade screen prints `Defend — cost 1, skill / Gain 5 Block`. Every battle
screen this act printed `Defend — Gain 6 Block`. The difference is `Oddly Smooth
Stone`'s `Dexterity 1`, folded into the face. Because I read the combat face as
the base and added Dexterity on top, I predicted 54 HP on fight 2 round 2 and the
screen said **53** (11 damage against 6 Block, not 7). I carried that as a
suspected Dexterity bug through four fights and only resolved it at a Smith screen
I had no obligation to open. The same silent folding covers Strength (`Strike`
printing 6 → 8 → 10 → 12), Shrink (`Strike` printing 4), and Vambrace (`Defend`
printing 12). **Nothing is wrong with the game here; the numbers are all correct.
What is missing is any way to tell an adjusted number from a base one.**

**2. Vambrace makes every Block card in hand print its doubled value, though only
one of them can pay it.** Fight 6 round 1, all three Defends printed `Gain 12
Block`. I played two and the screen showed **`Block 18`** — 12 + 6 — and the third
card in hand had by then rewritten itself to `Gain 6 Block`. Each face is true at
the instant you read it, but a hand reading "12 / 12 / 12" is worth 24, not 36,
and the only way to find that out is to spend the energy. This is the same defect
as finding 1 with a sharper edge, because here it misprices a *whole turn's*
defence, which is exactly the number you must get right when you are at 22 HP
against 23 incoming.

**3. One Jumpy Dumpty put two Mine 3s on one enemy.** Fight 4 round 3: two bombs
on Nibbit (2) (one from Jumpy Dumpty, one from Powder Charge), two enemies alive,
Ka-pow! set them off, Nibbit (2) died, and the survivor printed `Bomb 6 (buff) …
Bombs here: 2, including 2 Mines`. In fight 3 the *identical* card pair — Jumpy
Dumpty + Powder Charge, two bombs, one Set off — produced `Bombs here: 1,
including 1 Mine`. The only difference is that a second enemy died inside the same
Set off. Either the rider fired twice, or the dead enemy's Mine migrated to the
survivor. **I could not tell which**, and it is worth 3 extra damage plus a
Pounding Surprise Spark, so it is not cosmetic.

**4. About 149 gold arrived that no screen announced.** Every gold reward printed
before the shop totalled **74** (15 + 20 + 16 + 10 + 13). The shop opened with
**`You have 223 gold`**. The two candidates in between are the `Treasure` chest
(which listed only `Vambrace`) and the `Nab the Map` event (which named only the
Spoils Map, and the Spoils Map turns out to promise its gold *in the next Act*).
This is a large, silent grant: it is more than the price of the `Card Removal`
plus `Explosives Workshop` I bought with it.

**5. Festive Popper dealt 1 damage instead of 9, once.** It reads `At the start
of each combat, deal 9 damage to ALL enemies`. Against the Ceremonial Beast it did
exactly 9 (`HP 243/252`). Against three Inklets it produced `14/15`, `13/14`,
`15/16` — **one damage each**. And it was not blanket resistance on that enemy
type: the next Pyro damage to land on one of them, a `Bomb 5` Splash, took it
14 → 9 for the full 5. Something reduced that one relic's hit to 1 and no screen
said what.

**6. Sparks 'n' Splash takes my Strength; a Bomb set off ignores my debuffs.**
Boss round 4: bomb total `89`, `Strength 4`, boss went 233 → **140**, i.e. the
Splash dealt **93 = 89 + 4**. But fight 3 round 2 measured the opposite rule for a
detonation: `Shrink -1 … your Attacks deal 30% less damage` cut `Strike` from 6 to
4 and `Ka-pow!` from 4 to 2 on their printed faces, and the Set off still dealt
its full `22` (33 → 9 = 22 + 2). So the *same number* — the bomb stack — is
treated as "not your attack" when Ka-pow! sets it off and as "your attack" when
the Splash pays it. Both behaviours are defensible on their own text (the Bomb
glossary says a bomb's hit "takes the enemy's debuffs, not yours"; the Splash
never claims to be a bomb hit). **Together they are a trap**, because the player's
whole plan is built on treating the bomb number as one quantity.

**7. Sparks 'n' Splash pays the bomb stack every turn and spends nothing, which
silently makes every detonator in the game worse.** Measured twice. Fight 4
round 3: Splash 6 + Mines 6 = **12** damage (35 → 23) with `Spark 2 → 4` — a rise
of exactly 2, the two Mines, so the Splash itself did not count as "a Bomb going
off" for Pounding Surprise. Fight 4 round 4: Splash 6 with `Spark 4 → 3` — spent
one on Powder Charge, gained none. This is the strongest thing in the character
and it is genuinely exciting to discover, but it inverts the deckbuilding rules
mid-run: after it lands, Ka-pow!, Tinder Toss, Rapid Fire and Big Badda Boom all
go from "engine" to "thing that deletes my engine", and the game never says so.
`Careful Arrangement` ("Move all your Bombs onto the enemy as one Bomb") is the
sharpest version — the badge proves growth is **4 per bomb** (`Bomb 19` → `31`
with `Bombs here: 3`), so that card would have cut my growth from 12 a turn to 4
while reading like an upgrade.

**8. The boss's one brake is readable, and the fight is better for it.**
`Plow 150 — The first time Ceremonial Beast's HP reaches 150 or below, it becomes
Stunned and loses all its Strength`, on an enemy that Empowers every single round
while attacking (`18` → `20` → `22`). Because Sparks 'n' Splash resolves at the
end of *my* turn, crossing 150 with the Splash rather than with a card means the
stun lands before the swing. I needed 93, had 89, and added a Strike for it. It
worked exactly as read: boss to 140, Strength gone, intent flipped to a Debuff,
**0 damage taken**. This is the best-designed screen I saw all act — a printed
threshold, a printed reward for hitting it, and a timing subtlety that rewards
reading rather than luck.

**9. Two starter cards are indistinguishable.** `Duck and Cover` and `Defend` have
the same cost, the same 5 base Block, and the same rules text. Across seven fights
I never found a state where knowing which I held changed anything.

**10. Klee's own cards mostly cost no Energy, and that is the best thing about the
turn-to-turn feel.** Fight 5 round 3 I played **five cards on three energy** —
Pop! (0), Powder Charge (0 Energy, 1 Spark), Jumpy Dumpty (1), Defend (1), Duck
and Cover (1) — placing `Bomb 19` and holding `Block 17` in the same turn. The
character does not make you choose between building and surviving, which is
unusual and good. The counterweight is that the two most powerful cards I owned
were 2-cost powers (Nicole, Sparks 'n' Splash), and both spent most of the act
stuck in hand because of it; the `Sparks 'n' Splash+` upgrade being **cost 2 → 1**
was worth more than any number on any card I saw.

**Where I could not tell:** whether Vulnerable on me was applied at all (the
printed intent may already include it); whether Barbara's Hydro ever landed on the
boss; which of the two explanations produced the double Mine; and what reduced
Festive Popper to 1 damage. I did not have a way to test any of these without
spending turns I needed.

---

## Non-blindness declaration

- **Commands run:** only the two permitted forms,
  `GITS_LANE=2 python -m understudy.blindplay observe` and
  `GITS_LANE=2 python -m understudy.blindplay act "<command>"`, from the repo
  root. No other `understudy` subcommand was run at any point — no `harness`,
  `session`, `audit`, `notes`, `scenario`, `staged_turn`, `soak`, or `embark`.
  No `git`. Some `observe` output was piped through `sed`, `grep` and `head` to
  trim it, and one `mkdir -p` created this record's directory.
- **Tools used:** `Bash` (for the two commands above and this record's appends),
  `Write` and `Edit` (this record file, plus one scratch file under the session
  scratchpad used only to assemble this record's closing sections).
- **Repo files read: none.** No source, YAML, docs, rulings, backlog, or any
  earlier record was opened. Everything above comes from screens the tool
  printed. Where I state a rule, it is either quoted from a screen or marked as
  my inference.
- **Files written:** this record only —
  `review/qa/klee-round-8-2026-09-03/opus-run2-act1.md`. No identifiers were
  minted.
- **Lane:** lane 1 was never touched. The game was never launched, closed,
  restarted or torn down.
- **The lane is left standing** on the **act-2 map screen**, first node
  `Ancient (path 1)`, with no node selected and no screen half-resolved, at
  **HP 31/62, 163 gold, 3/3 potions**, ready for the next seat.

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
