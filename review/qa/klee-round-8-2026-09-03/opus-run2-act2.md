# KLEEMOD-KLEE — blind seat, lane 2, run 2, act 2

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, round 8, run 2, **second seat
  of three** (act 2 only).
- **Lane:** 2.
- **Character:** KLEEMOD-KLEE.
- **Picked up:** on the **act-2 map screen**, exactly where the first seat left it
  — HP 31/62, 163 gold, 3/3 potions, one node offered (`Ancient (path 1)`).
- **Act:** 2. Map printed 16 floors; at the top of the act: **Knowledge Demon**.
- **Actions:** **196 accepted, 0 refused.** No command was ever rejected and no
  tool error occurred at any point. (One Bash call returned no output, because a
  `sed` filter of mine matched nothing on an unexpected "Choose a card" screen;
  the actions in it had all been accepted, as the next `observe` confirmed.)
- **Termination reason:** **stop condition (1)** — the act-2 boss was resolved
  and its reward screen handled, so the lane stands on the act-3 map screen.
  Budget was never close (196 of 250).
- **Where the run stands:** **ACT 2 CLEARED.** Lane 2 is on the **act-3 map**,
  which names its boss **Aeonglass** and offers one node, `Ancient (path 1)`.
  Nothing is selected and no screen is half-resolved.
  **HP 15/69** as last printed (boss round 7) — but see finding 1: **act 2 opened
  with an unannounced full heal**, so the next seat should re-read HP from its
  first battle screen rather than trusting this number. **Gold 242. Potions 1 of
  3.**

### HP trajectory (every reading the screens printed, in order)

Max HP was **62** until `Strawberry` raised it to **69** on floor 28.

`62/62` `62/62` `49/62` `49/62` `49/62` (**fight 8**) → `39/62` `34/62` `34/62`
(**fight 9**) → `34/62` `34/62` `29/62` (**fight 10**) → **rest 29 → 47** →
**rest 47 → 62** → `62/62` `51/62` `42/62` `42/62` `33/62` `33/62` `23/62`
(**ELITE**) → **rest 23 → 41** → **Strawberry 41/62 → 48/69** → `48/69` `48/69`
`48/69` `41/69` `35/69` (**fight 11**) → **rest 35 → 55** → `55/69` `55/69`
`38/69` `26/69` `26/69` `18/69` `18/69` `15/69` (**BOSS**) → final **15/69**.

Entered act 2 at 62/62 (after the silent heal from 31) and left at 15/69.
Damage taken across four fights, one Elite and a boss: **123**, of which **39**
came from the Elite alone and **40** from the boss.

### Gold / potions / relics (exactly as printed)

- **Gold: 242.** Fully traced, with no unexplained arrivals this act (unlike act
  1's finding 4): started **163**, `+15` (fight 8) = 178, **−79 −49** at the shop
  = 50, `+20` (fight 9) = 70, `+15` (fight 10) = 85, `+45` (Elite) = 130, `+12`
  (fight 11) = 142, `+100` (boss) = **242**. The `Spoils Map`'s promised 600
  never appeared (finding 13).
- **Potions: 1 of 3.** `Droplet of Precognition` — **no screen has ever said what
  it does.** I began the act at 3/3 and cleared the jam deliberately: traded the
  **Strength Potion** at a forced event, spent the **Block Potion** in fight 11
  and the **Weak Potion** at the boss. They were the first potions used in the
  run. `Explosive Ampoule` (fight 8) was still lost to full slots.
- **Relics**, exactly as the battle screen's "Your relics" block prints them:
  - **Pounding Surprise** — Whenever a Bomb goes off, gain 1 Spark.
  - **Large Capsule** — Upon pickup, obtain 2 random Relics. Add an additional Strike and Defend to your Deck.
  - **White Star** — Elites drop an additional Rare card reward.
  - **Oddly Smooth Stone** — Start each combat with 1 Dexterity.
  - **Festive Popper** — At the start of each combat, deal 9 damage to ALL enemies.
  - **Vambrace** — The first time you gain Block from a card each combat, double the amount gained.
  - **Pael's Blood** — At the start of your turn, draw 1 additional card.
  - **Strike Dummy** — Cards containing “Strike” deal 3 additional damage.
  - **Razor Tooth** — Every time you play an Attack or Skill, Upgrade it for the remainder of combat.
  - **Strawberry** — Upon pickup, raise your Max HP by 7.

  **White Star finally paid, once, on floor 26** — the only Elite I fought, which
  gave two card rewards. `Festive Popper` dealt its full 9 in all five combats
  this act, so act 1's "1 damage to three Inklets" anomaly did not recur.

### Deck as I reconstruct it (33 cards, plus 2 in question)

Carried in from act 1 (24): Strike ×4 · Defend ×4 · Kaboom! · Jumpy Dumpty ·
Ka-pow! · Duck and Cover · Powder Charge · Pop! ×3 · Nicole · Sparks 'n' Splash+ ·
Sparks 'n' Splash · Explosives Workshop · Barbara — Melody Loop · The Big One ·
Chain Fuse · Spoils Map.

Changed in act 2:

- **Upgraded:** `Sparks 'n' Splash` → **`Sparks 'n' Splash+`** (cost 2 → 1) at
  the Spirit Grafter. **Both copies are now cost 1.**
- **Added:** `Run Away!+` · `Explosives Workshop` (2nd, shop) · `Dig In` (shop) ·
  `Mine Toss+` · `Fish-Flavored Bait+` · `Sorry, Jean...` ·
  `Yumemizuki Mizuki — Anraku Secret Spring Therapy` ·
  `Rosaria — Ravaging Confession` · `Nicole` (2nd, boss reward).
- **Removed:** nothing. I bought no Card Removal (it was 100 gold here, up from
  75 in act 1), so **`Spoils Map` is still in the deck and still unplayable**.

**In question:** the Knowledge Demon added **`Mind Rot`** and **`Sloth`** as
status cards mid-fight. I could not tell from any screen whether they persist
after combat; the next seat will see it on its first battle screen's pile counts.

**One card of the deck is unidentified**: fight 9's Thieving Hopper stole a card
and the reward screen returned it, and **no screen named it either time**
(finding 5). The deck count came back to where it was, so nothing is missing —
but I cannot swear which card made the round trip.

### Act-2 map as printed on arrival

```
- 1 floor ahead: Ancient
- 2 floors ahead: Monster, Monster
- 3 floors ahead: Monster, Monster, Shop, Unknown
- 4 floors ahead: Unknown, Monster, Unknown, Monster
- 5 floors ahead: Monster, Monster, Monster, Monster
- 6 floors ahead: Monster, Shop, Unknown
- 7 floors ahead: Monster, Monster, Unknown
- 8 floors ahead: RestSite
- 9 floors ahead: Treasure
- 10 floors ahead: Monster, RestSite, Unknown
- 11 floors ahead: Unknown, Elite, Shop, Unknown
- 12 floors ahead: Elite, RestSite, RestSite, Elite
- 13 floors ahead: Unknown, Unknown, Elite, Monster
- 14 floors ahead: Elite, Monster, Unknown, Monster
- 15 floors ahead: RestSite, RestSite
- 16 floors ahead: Boss
```

Routing note taken on arrival: I am at **31/62** with seven Monster floors before
the first RestSite (8 floors ahead), and the Elites do not start until floor 11.
`White Star` (Elites drop an additional Rare card reward) has still never paid.
The plan is to take the free floors to the rest site, then decide about Elites on
the HP I actually have.

---

## Screen by screen

### Act-2 opening — an unannounced full heal

The first seat left the lane at **31/62** and its record says so twice. The Pael
event printed three options and a `Proceed`, and nothing else. The very next
screen carrying an HP line — round 1 of fight 8 — printed **`HP 62/62`**.

**31 HP arrived between the act-1 boss reward and the first act-2 fight, and no
screen I saw announced it.** Between those two points I opened only the map, the
Pael event, and its `Proceed`. This is the largest silent grant of either act
(finding 1).

### Ancient (floor 1) — Pael

```
- Pael's Tears   If you end your turn with unspent [Energy], gain an additional [Energy][Energy] next turn.
- Pael's Wing    You may sacrifice card rewards to Pael. Every 2 sacrifices, obtain a Relic.
- Pael's Blood   At the start of your turn, draw 1 additional card.
```

**Chose Pael's Blood**, on the first seat's record rather than on taste: both of
its structural complaints are draw problems, not power problems. Its engine card
`Sparks 'n' Splash+` "did not arrive until round 4 of a 5-round boss fight", and
**36 of the 65 damage it took all act came in the two fights whose opening hand
held no Block card**. `Pael's Blood` is unconditional and pays on turn 1 of every
fight, which is exactly where both failures live.

Against `Pael's Tears`: the bigger number (3 energy → 5), but conditional on
deliberately wasting energy, and Klee's turns are already energy-loose because
Pop! costs 0 and Powder Charge costs Spark, not Energy. Against `Pael's Wing`: my
deck is 24 cards including a permanently dead `Spoils Map`, and trading certain
card rewards for random relics is a bet, not a fix.

**It paid immediately and visibly.** Every hand this act was **6 cards**, and
`Pael's Blood` prints in the relic block. It is the only one of the three whose
effect I could have confirmed from a screen at all.

### Fight 8 — Tunneler (HP 87), entered at 62/62

`Festive Popper` opened it at **`HP 78/87`** — the full 9, so the act-1 anomaly
(1 damage to three Inklets) did not repeat here.

Opening state: `Energy 3/3`, `Dexterity 1`, `Spark 1`, **`18 in the draw pile`**
against a 6-card hand = the 24-card deck intact, and the 6 confirms Pael's Blood.

**Round 1.** Hand: Pop! x2, Strike x3, Explosives Workshop. Enemy
`Intent: Aggressive — the number on its icon is 13`. No Block card in hand and 13
incoming at full HP, so I bought the engine instead of the mitigation: Pop! (0),
Pop! (0), **Explosives Workshop** (1), Strike (1), Strike (1) — five cards on
three energy, one Strike left over.

Predicted 12 damage. **Enemy `78 → 66`, exact.** Badge: `Bomb 10 … Bombs here: 2`.

**The Explosives Workshop measurement.** Its text is `At the start of your turn,
your Bombs grow by 1 more`. Two bombs, 10 total. Per **bomb**, next turn is
10 + (4x2) + (1x2) = **20**; per **stack**, 19.

Screen, round 2: **`Bomb 20`**. **Per bomb.** Took 13 → `HP 49/62`.

**Round 2 — a free turn, spent on a clean Vaporize test.** Enemy intent was
`Empower (Buff)` *and also* `Defensive (Defend)`: no damage coming, so every
Block card in hand was worth nothing this turn.

The hand printed **four Defends all reading `Gain 12 Block`** — the act-1 seat's
finding 2 reproducing exactly, since `Vambrace` was unspent and only one of the
four could ever pay 12.

Played **Barbara — Melody Loop** (`Gain 10 Block. For 3 turns, at the start of
your turn apply Hydro to the enemy. Exhaust.`) and a Strike (`66 → 60`), leaving
1 energy. The reasoning: the Tunneler carried **no aura at all** at that moment —
nothing had painted Pyro on it yet, and `Festive Popper` leaves no aura — so this
was the one clean window in the fight to land Hydro on a bare body and Vaporize a
large bomb. The price was spending Vambrace's doubling on 10 Block that did
nothing, which I paid knowingly.

**Round 3 — the best screen of the act.** The Hydro landed:

```
- Hydro Aura 1 (aura) — Hydro clings to this enemy for 1 more turn.
```

and both my Pyro cards rewrote themselves with a line that had never appeared
before: `*Reaction preview: Vaporize* — This card supplies Pyro or Hydro while an
enemy has the other aura. The triggering hit deals 1.5x damage and consumes the
aura.`

But the enemy had printed a wall, and the key to it:

```
- Tunneler — HP 60/87, Block 32
    Intent: Aggressive — the number on its icon is 23
    Burrowed 1 (buff) — Block is not removed at the start of Tunneler's turn.
                        Stunned if all Block is removed.
```

`Burrowed` is what makes this fight a puzzle rather than a race: **its Block
persists between turns**, so chipping is worthless and the wall only accumulates
— but strip all 32 in a single beat and it is **Stunned**. Effective HP 32 + 60
= 92.

Played **Jumpy Dumpty** (1) → predicted `Bomb 38`; then **Chain Fuse** (1, "Each
Bomb on the enemy grows by 6") → predicted 38 + 6x3 = **56**. Screen:
**`Bomb 56 … Bombs here: 3`**, exact. The three bombs were individually
**21 / 21 / 14** (two Pop! bombs placed at 5 and grown +5 twice, then +6; the
Jumpy Dumpty bomb placed at 8, then +6).

Then **Ka-pow!** (0 energy) to Set off. I deliberately held `Kaboom!` back: it is
also Pyro and also printed the Vaporize preview, and playing it first would have
spent the Hydro aura on a 7-damage card instead of on a 21-point bomb.

**Predicted 70:** one 21-bomb Vaporized to 31 (21 x 1.5 = 31.5), the other two
plain at 21 and 14, plus Ka-pow!'s own 4 = 31 + 21 + 14 + 4 = **70**. Into
`Block 32` first, so 38 into HP → `HP 22`, `Block 0`, **Stunned**.

**Observed, exactly:**

```
- Tunneler — HP 22/87
    Intent: Stunned (Stun) — This enemy can't act on its next turn.
    Pyro Aura 2 (aura)
    Bomb 3 … Bombs here: 1, including 1 Mine.
```

with `Spark 1 → 4`.

Three rules confirmed on one screen: **Vaporize multiplies exactly one bomb hit,
not the badge's 56** (finding 3); **Pounding Surprise pays once per bomb, not
once per Set off** (Spark +3 for three bombs); and the last Pyro bomb hit left
`Pyro Aura 2` behind once the Hydro was consumed, exactly as the Elemental
Reaction glossary says it should.

Spent the last energy on `Kaboom!` (7) → `HP 15`, and ended. **Took 0** — the
stun held and the printed `Attack 23` never arrived.

**Round 4 — Barbara's Hydro dies to my own fire, and the screen shows it.**
`Melody Loop` applied its second Hydro at the start of my turn, onto an enemy now
wearing `Pyro Aura 2` from my own Set off. The result:

```
- Tunneler — HP 15/87
    Melody Loop 1 (buff)
    Bomb 8 …
```

**No aura line at all**, and `HP 15` unchanged. The Hydro was consumed to
Vaporize a hit that carried no damage, the Pyro went with it, and the enemy was
left bare for nothing. **This is the act-1 seat's unverified hypothesis about why
its 74-gold Barbara purchase never paid, now confirmed on a screen** (finding 2).

Killed it cleanly: Pop! (0) → Bomb 13, **Powder Charge** (0 energy, 1 Spark) →
Bomb 19, **Sparks 'n' Splash+** (1) → predicted the end-of-turn Splash pays the
whole 19 into a 15 HP enemy, killing it **before** its printed `Attack 13` lands.
It did.

**Result: fight 8 won at 49/62** — 13 damage across four rounds, all of it in the
one round whose opening hand held no Block card.

### Fight 8 reward

`15 Gold` (→ **178**), `Explosive Ampoule` (**unclaimable, 3/3 potion slots**),
and a card. All four offers were upgraded:

```
- Run Away!+   — cost 0, skill — Gain 6 Block. If a Bomb went off this turn, gain 4 additional Block.
- Fwoosh!+     — cost 1 Spark, attack — Set off. Deal 9 damage.
- Sizzle+      — cost 1, attack — Set off. Deal 9 damage. If a Bomb triggered an Elemental Reaction this turn, deal 6 additional.
- Barbara — Let the Show Begin♪ — cost 1, skill — Gain 6 Block. Apply Hydro.
```

**Chose Run Away!+**, on three measurements rather than taste:

1. **Barbara — Let the Show Begin♪ is a trap in this deck, and I had just watched
   why.** Its own glossary says `Applies Hydro — If the target has no aura, this
   applies Hydro for 2 turns. A different aura is consumed to trigger a Reaction
   instead.` My deck paints Pyro on everything it touches, so on any turn after
   the first the Hydro is consumed for nothing — exactly what Melody Loop had
   done one round earlier.
2. **Both detonators fight my own engine.** I hold two `Sparks 'n' Splash`, which
   pay the bomb stack every turn and spend nothing; `Set off` deletes the stack.
   `Ka-pow!` (0 energy) and `The Big One` already cover the burst case.
3. **A 0-cost Block card competes with nothing.** Klee's bombs are free, so the
   deck's whole shape is "spend the energy on defence", and the only damage I
   took this fight came from a turn with no Block card in hand.

### Shop (floor 20) — 178 gold

```
- Bang Bang!          cost 2 Sparks, attack   78
- Fwoosh!             cost 1 Spark, attack    25
- Careful Arrangement cost 1, skill           74
- Dig In              cost 1 Spark, skill     49
- Explosives Workshop cost 1, power           79
- Bennett — Fantastic Voyage  cost 1, skill   77
- Razor — Lightning Fang      cost 1, skill   72
- Potion Belt         relic  (2 potion slots) 160
- Snecko Skull        relic                   192
- Screaming Flagon    relic                   219
- Power Potion 52 · Regen Potion 77 · Cure All 79 · Card Removal 100
```

**Bought `Explosives Workshop` (79) and `Dig In` (49), leaving 50.**

- A **second Explosives Workshop** because I had measured the first one that
  morning: `Bomb 10 → Bomb 20` on two bombs is **+1 per bomb**, and with a
  `Sparks 'n' Splash` paying the whole stack every turn, growth is collected
  repeatedly instead of once. It is the only card on the shelf that compounds.
- **`Dig In`** (`cost 1 Spark, Gain 8 Block`) as a second **zero-Energy** block
  card, for the same reason I took Run Away!+.

**`Careful Arrangement` (74) is a trap, and my own Workshop measurement is the
proof.** It reads `Move all your Bombs onto the enemy as one Bomb. It grows by
5.` Growth is **per bomb**: my three bombs grow 4+4+4 = 12 a turn before
Workshop and 15 with it. Merged into one bomb they would grow **4, or 5 with
Workshop**. The card reads like consolidation and is a two-thirds cut to the
engine. The act-1 seat refused it at an event on the same reasoning; I refused it
again at a price.

**`Razor — Lightning Fang` (72)** would make my Attacks apply **Electro**, and
`Overloaded` is the one reaction on the glossary with no damage multiplier — the
worst element to pair with a Pyro deck. **`Card Removal` was 100 here** (it was
75 in act 1), and I judged one card out of 24 a worse buy than two cards in.

### Unknown (floor 21) — Spirit Grafter

```
- Let It In   Heal 25 HP. Add Metamorphosis to your Deck.
- Rejection   Lose 10 HP. Upgrade a card.
```

**Chose Rejection** at 49/62. The heal is **capped and wastes 12 of its 25** — at
79% HP the game was offering me its worst rate — and `Metamorphosis` is an
unnamed permanent addition to a deck already at 25 cards with one dead card in
it. Against that, the map showed a **RestSite as the only room on its floor five
floors ahead**, so a rest was guaranteed, not hoped for. HP is replenishable
here; a card is not.

Upgraded the **second `Sparks 'n' Splash`, cost 2 → 1.** The two copies stack
(the buff prints as `Sparks 'n' Splash 1`), so with both at cost 1 a double-Splash
turn costs 2 energy instead of 3, and — more to the point — **whichever copy I
draw first is now always the cheap one.** Act 1's single biggest complaint was
this exact card losing the energy contest turn after turn.

The upgrade screen previewed it honestly before I confirmed:
`Sparks 'n' Splash+ (upgraded) — cost 1, power — PICKED`.

*Two tool notes from this screen, recorded because they are the page being
honest rather than defects:* it listed the deck "as it stood in the last fight
(floor 19)", flagged `Sparks 'n' Splash+` and `Spoils Map` as absent with
"nothing on the feed says why" — and **did not mention `Run Away!+` at all**,
which I had picked up one floor earlier and which was in neither list nor
exception.

### Fight 9 — Thieving Hopper (HP 79), entered at 39/62

Opened at `HP 70/79` (Festive Popper's full 9 again). Hand: Duck and Cover,
Defend x2, Strike, Kaboom!, **Spoils Map** — one of six cards permanently dead.

```
- Thieving Hopper — HP 70/79
    Intent: Aggressive — the number on its icon is 17
      and also: Malicious (CardDebuff) — This enemy intends to apply Afflictions on your cards.
    Escape Artist 5 (buff) — Tries to escape the combat after 5 turns.
```

**`Escape Artist` is a damage clock** — 79 HP in five turns — and it is the first
thing act 2 asked of the deck that act 1 never did (question (f)).

**Round 1.** Duck and Cover (Vambrace-doubled to 12) + Kaboom! (7) + Strike (6).
Predicted `70 → 57` and `39 → 34` behind 12 Block against 17. **Both exact.**

**Round 2 — what the CardDebuff actually was.** The enemy printed a new line:

```
- Swipe 1 (buff) — Upon killing this enemy, the stolen card is returned.
```

and my pile counts had gone from a 27-card deck to **26** (6 hand + 14 draw + 6
discard). **It had stolen a card out of my deck, and no screen ever named which
one** — not when it was taken, and not when it came back (finding 5).

Its intent was `Empower (Buff)`, so this was a free turn. Spent it entirely on
the engine: Pop! (0), Pop! (0), **Powder Charge** (0 Energy, 1 Spark),
**Sparks 'n' Splash+** (1), Strike (1) — five cards, three bombs, two energy.

The **Spark decision** here is the sharpest small choice of the act. I held
exactly **1 Spark**, and `Powder Charge` and `Dig In` both cost 1 Spark. Because
I run the Splash, my bombs never *go off*, so `Pounding Surprise` never refunds
me — **in Splash mode the Spark bank is one per combat, full stop.** I spent it
on Powder Charge: a Bomb 6 adds 6 to *every* future Splash and grows, where Dig
In is 9 Block once, and nothing was incoming.

Predicted `57 → 51` (Strike) then the end-of-turn Splash for the full 16
→ **35**. Screen: `HP 35/79`, `Bomb 28 … Bombs here: 3` (16 + 4x3). Exact.

**Round 3 — two enemy buffs that both point at the same question.**

```
- Escape Artist 3 (buff)
- Flutter 5 (buff) — Receives 50% less damage from Attacks. Deal attack damage 5 times to Stun it.
```

and my hand held **no Block card at all** against a printed `Attack 21`, at
34 HP.

`Flutter` is a direct question about the bomb rule: **is a Bomb's hit an
Attack?** If it is, my Set off is halved but its four separate hits plus a card
would Stun the Hopper; if it is not, the Set off lands in full. I could not tell
from any printed text — the Bomb glossary says only that a bomb's hit "takes the
enemy's debuffs, not yours", and `Flutter` is a buff.

So I picked the line that wins **in both branches**: Pop! (0) → `Bomb 33` across
four bombs, then **The Big One** (3) — `Set off for quadruple damage`. 33 x 4 =
**132**, or **66** if Flutter halves it. The enemy had 35 HP. Lethal either way.

It died on the spot, at **34/62, taking 0 damage in the round**, which also
cancelled the escape clock and returned the stolen card.

**I therefore still do not know whether Flutter halves bomb damage** — I bought
the guaranteed kill instead of the measurement, at 34 HP with elites ahead, and
I would make the same trade again.

### Fight 9 reward

`20 Gold` (→ **70**), `Take your stolen card back.`, and a card:

```
- Quick Fuse      — cost 1 Spark, skill — Each Bomb on the enemy grows by 3. Set off.
- Mine Toss+      — cost 1, skill — Place a Mine 7 on ALL enemies.
- Catalytic Converter — cost 1, power — Whenever one of your Bombs triggers an Elemental Reaction, gain 1 additional Spark.
- Prune — Ring-A-Ding-Ding! Hexhunter Chime — cost 1, attack — Deal 8 damage. Swirl. …
```

**Chose Mine Toss+.** It is the only offer that **feeds** the Splash instead of
spending it, and it is my first multi-target bomb placer — everything else in the
deck places on one enemy (Jumpy Dumpty's Mine rider excepted, and that pays a
round late). A Mine also cashes itself when the enemy attacks, before the hit
lands, so it is damage that does not cost me the stack.

`Quick Fuse` ends in `Set off`, which deletes the stack the Splash lives on.
`Catalytic Converter` needs my Bombs to trigger Elemental Reactions, and I had
just watched my only Hydro source get eaten by my own Pyro aura. `Prune` needs a
non-Pyro aura I have no reliable way to make.

### Unknown (floor 22) — "The Future of Potions?"

```
1. Insert Common Potion   Lose Block Potion. Obtain an Upgraded Common Attack.
2. Insert Common Potion   Lose Weak Potion. Obtain an Upgraded Common Attack.
3. Insert Common Potion   Lose Strength Potion. Obtain an Upgraded Common Attack.
```

**There was no way to decline.** Three rows, all of them a forced trade, and no
"leave" option printed. That is worth recording on its own: every other event
this run offered a way out.

**Traded the Strength Potion**, on the act-1 seat's own measurement. Its boss
round 4 measured the Splash paying **`bombs + Strength`** — 89 bombs + 4 Strength
= 93 — a **flat** add, not a multiplier. So `Gain 2 Strength` is worth about
+2 damage per turn to my main damage source, while `Gain 12 Block` and
`Apply 3 Weak` are both worth more than that against a boss. It also freed a
potion slot: I had been at **3 of 3 for the whole run**, and had already had to
leave `Stable Serum` (act 1) and `Explosive Ampoule` (fight 8) on the floor.

Offered `Fish-Flavored Bait+`, `Sizzle+`, `Fwoosh!+`. **Took Fish-Flavored
Bait+** (`cost 1 — Deal 7 damage. Place a Bomb 6.`): the only one of the three
that **adds** to the stack. Both others begin `Set off`.

### Fight 10 — Hunter Killer (HP 121), entered at 34/62

Reached through an **Unknown**, which turned out to be a fight. Opened at
`112/121`. First intent `Strategic (Debuff)` — a second free setup turn, which I
spent entirely on the engine: Pop! (0), Powder Charge (0 Energy, 1 Spark),
**Mine Toss+** (1), **Explosives Workshop** (1), Kaboom! (1). Five cards, three
energy, three bombs.

Predicted `Bomb 18 → 33` (18 + 3 bombs x 5) and `112 → 105`. **Both exact.**

**Round 2 — the debuff that is aimed at Klee specifically.**

```
- Tender 0 (debuff) — Whenever you play a card, lose 1 Strength and 1 Dexterity this turn.
```

This is the first thing in either act that **punishes the character's own
shape**. Klee's whole feel is "five cards on three energy" — the act-1 seat named
that its best quality — and `Tender` taxes exactly that. It also makes **play
order load-bearing in a way nothing else has**: Block cards want to be played
while Dexterity is still positive, attacks while Strength still is, and the two
compete for the same early slots.

I ordered for it: **Defend first** (Dexterity still 1, Vambrace doubling →
`Block 12`), **Fish-Flavored Bait+** second, **Sparks 'n' Splash+** third.

Screen after two cards: `Block 12`, `Strength -2`, `Dexterity -1`, `Tender 2`,
enemy `105 → 99`. So the Bait dealt **6, not 7** — it resolved at `Strength -1`,
one card's worth of Tender. Every number exact, and **`Tender N` turns out to be
a counter of cards played this turn**, not a stack size; it printed `Tender 0`
at the start of both turns.

Predicted the end of turn precisely: bombs `39` (33 + the Bait's 6), Splash pays
`39 + Strength(-3)` = **36**, then the enemy attacks and the **Mine (12) goes off
before its hit lands**, so 36 + 12 = **48**, and I take `17 - 12` = 5.

**Observed: `HP 99 → 51` (48 exactly) and `34 → 29` (5 exactly).**

**Round 3.** `Bomb 42` across 3 bombs (the Mine had spent itself), enemy at 51,
intent `the number on its icon is 7x3` — 21 incoming at 29 HP, with Vambrace
already spent so every Block card in hand printed 6 or 7.

Two lines. **Block it out and keep the engine:** four block cards, but Tender
would shave each one after the first (7 + 5 + 4 + 3 = 19 against 21), and the
Splash would pay 38, leaving the enemy at 13. **Or kill it now.**

Killed it: Strike (1) at full Strength for 6, Jumpy Dumpty (1) for `Bomb 50`,
**Ka-pow!** (0) to Set off. 6 + 50 + Ka-pow!'s own 4 at `Strength -2` = **54
into 51**, and it dies before a single one of the three 7s lands. This is the one
time all act that spending the stack was right, and the reason is that
**detonation is a finisher, not an engine** — the exact conclusion the act-1 seat
reached at the shop.

**Result: fight 10 won at 29/62**, 5 damage taken across three rounds.

### Fight 10 reward

`15 Gold` (→ **85**) and a card:

```
- Careful Arrangement+ (upgraded) — cost 1 — Move all your Bombs onto the enemy as one Bomb. It grows by 8.
- Fwoosh!            — cost 1 Spark, attack — Set off. Deal 6 damage.
- Sorry, Jean...     — cost 0, skill — Remove one of your Bombs. Gain Block equal to its size.
- Bennett — Passion Overload — cost 0, skill — Your next Attack this turn deals 4 additional damage and applies Pyro.
```

**Chose Sorry, Jean...** — **0 energy Block that scales with the engine**, and my
binding constraint all act has been HP, not damage. Late in a fight a single bomb
is worth 15–20, so this is a Defend that pays three times as much and costs
nothing, and if it is the first Block card of a combat, Vambrace doubles it.

**`Careful Arrangement+` is the same trap at a better price and I refused it a
third time.** Even upgraded ("grows by 8" instead of 5), it converts N bombs into
one. This fight had **four bombs growing 5 each = 20 a turn**; merged, that
becomes **5 a turn plus 8 once**. The card reads like an upgrade and is a
three-quarters cut to the engine.

### RestSite (floor 24) — Rest

`HP 29/62` — 47%. `Rest — Heal for 30% of your Max HP (18)` vs `Smith`. **Rested
to 47/62.** Three more RestSites were on the map (floors 3, 5 and 8 ahead) so
this was not the last one, but the Elites start four floors on, and the briefing
notes run 1 of this round died routing into an Elite at 2 HP.

### Treasure (floor 25) — Strike Dummy

`Strike Dummy — Cards containing "Strike" deal 3 additional damage.` Taken; there
was nothing else in the chest. See finding 6 — **it does not do what it says.**

### Map decision — routing deliberately *into* an Elite

Three ways on: `Monster → Unknown, Elite`, `RestSite → Elite`, and
`Unknown → Elite, Shop, Unknown`. **Took the RestSite**, rested `47 → 62/62`, and
walked into the Elite at full HP.

This was the act's biggest routing call and I made it on two printed facts:
`White Star — Elites drop an additional Rare card reward` **had never once paid
in 25 floors**, and my damage had been overshooting all act (fight 8 delivered 70
into 92 effective HP; fight 10 killed a 121 HP enemy in three rounds for 5
damage). The map also put **two RestSites on the next floor**, so the Elite was
bracketed by rests on both sides.

### ELITE — Infested Prism (HP 161), entered at 62/62

Opened at `152/161`. The Elite's gimmick is aimed straight at this character:

```
- Vital Spark 2 (buff) — ALL Skills are Tainted 2.
```

and every Skill in my hand rewrote itself with `Gain 2 Tainted`. **Klee's deck is
overwhelmingly Skills** — Pop!, Powder Charge, Chain Fuse, Jumpy Dumpty, Mine
Toss+, Dig In, Run Away!+, Sorry Jean, and every Defend. This is the second enemy
in a row built against the character's own shape, after `Tender`.

**What Tainted does was not readable before I paid for it.** The card face said
`Gain 2 Tainted` and the glossary entry said, in full, `*Tainted* — Gain 2
Tainted when played.` Neither says what Tainted *is*. I spent a free card (Pop!,
0 energy) purely to read the status block, and only then got:

```
- Tainted 2 (debuff) — Take 2 additional damage from Attacks this turn.
```

(finding 4).

**Round 1.** Pop!, Powder Charge, Chain Fuse, Duck and Cover (Vambrace → 12
Block), Strike. Four Skills = `Tainted 8`. Predicted `152 → 143` (Strike at 9)
and `15 + 8 - 12` = 11 taken → **51/62**. Both exact. `Bomb 23`.

**Round 2.** Predicted `Bomb 31` and took the same arithmetic again: intent 11,
two Skills = `Tainted 4`, Block 6 → `11 + 4 - 6` = 9 taken → **42/62**, enemy
`143 - 19` = **124**. All exact.

**Round 3 — Powers are not Skills.** The enemy went to `Block 11` with a
three-hit intent. I built the turn to pay almost no Tainted: **Ka-pow!** (0, an
Attack) to Set off `Bomb 48`, **Run Away!+** (0), **Explosives Workshop** (1) and
**Nicole** (2) — and the last two are **Powers, which `Vital Spark` does not
tax at all.** Only one Skill, so `Tainted 2`.

Predicted the Set off exactly: 48 bomb + 4 = 52, of which `Block 11` absorbs 11,
so **41 into HP → `124 → 83`**, and `Spark +3` for three bombs. Both exact.

Two things did *not* match:

- **`Run Away!+` paid 12 Block, not the 11 its face prints.** It reads
  `Gain 7 Block. If a Bomb went off this turn, gain 4 additional Block` — 7 + 4 =
  11 — and the screen showed `Block 12`. The conditional clause picked up
  Dexterity that the printed face did not show (finding 7).
- **`Tainted 2` did not appear in the damage.** Intent `7x3` = 21, Block 12, and
  I took **exactly 9** — i.e. `21 - 12`, with the +2 nowhere. The identical
  arithmetic had held to the point in rounds 1 and 2, both of which were
  **single-hit** intents. I could not tell why (finding 8).

**Round 4 — the character's best turn of the act, and the reason I bought
`Dig In`.** Nicole delivered `Block 5` and `Strength 2`, and the Splash finally
arrived. Played **five cards on three energy**: `Sparks 'n' Splash+` (1, Power),
`Pop!` (0), `Fish-Flavored Bait+` (1), `Strike` (1), and **`Dig In` — which costs
1 Spark and no Energy at all**.

Predicted: 9 + 11 = 20 from cards → 63, then the end-of-turn Splash pays
`bombs 11 + Strength 2` = 13 → **50**; and `Block 5 + 9 = 14` against
`8 + Tainted 4 = 12` → **take 0**.

**Observed: `83 → 50` (33 exactly) and `HP 33` unchanged.** Ending with Block
left over then took `Strength 2 → 4` off Nicole.

The Elite answered by Empowering: **`Vital Spark 2 → 4`** — every Skill now cost
4 Tainted, which made `Defend` (`Gain 6 Block. Gain 4 Tainted.`) very nearly
self-cancelling — and it went behind `Block 20`.

**Round 5 — the double-Splash measurement.** Two Strikes at 13 (6 base + 3 Strike
Dummy + 4 Strength) stripped the `Block 20` and put 6 through, `50 → 44`, exactly
as predicted. I also played the **second `Sparks 'n' Splash+`**.

**The buff counter did not move: it still read `Sparks 'n' Splash 1` after the
second copy resolved**, and the end-of-turn payout was **25 — a single
`bombs 21 + Strength 4`**, not two. The counter only incremented to
`Sparks 'n' Splash 2` at the **start of the following turn** (finding 9).

Took `15 - 5` = 10 → **23/62**.

**Round 6.** `Bomb 31`, enemy at 19, me at 23. **Ka-pow!** (0 energy, an Attack,
so no Tainted) set off 31 plus its own 4 + 6 Strength = **41 into 19**. Dead on
the spot, taking nothing.

**Result: Elite killed at 23/62**, 39 damage taken over six rounds.

### Elite reward — White Star pays, once, in 27 floors

`45 Gold` (→ **130**), the relic **`Razor Tooth`** (the screen named it and never
said what it does — I learned that from the next battle's relic block), and
**two** card rewards, which is `White Star` finally earning its slot.

**Skipped the first** (`Sugar Rush`, `Sizzle`, `Fish-Flavored Bait`,
`Amber — Explosive Puppet`) — none beat a card already in the deck, and at 30
cards with 4 Strikes, 4 Defends and a dead `Spoils Map` in it, thinning was worth
more than a marginal add.

**Took `Yumemizuki Mizuki — Anraku Secret Spring Therapy`** from the second
(over `The Big One` #2, `Alice's Introduction Magic` and `Sugar Rush`):
`cost 2, skill — Swirl ALL enemies. If you are above 70% HP, deal 18 damage to
ALL enemies. Otherwise, Mend 10. Exhaust.`

The reason is the measurement, not the taste: **damage has overshot in every
fight of the act and HP has been the binding constraint in all of them.** This is
the only card offered in either act that **restores HP inside a fight**, and its
healthy-side mode is 18 to ALL enemies, which covers the multi-enemy case my
single-target bomb placers handle worst. `Alice's Introduction Magic` is dead — I
own no card that pays for Hexerei.

### RestSite (floor 27) — Rest

`23/62` → **41/62**.

### Map decision — refusing the second Elite

Next floor offered `Unknown → Monster, Unknown` or **`Elite → Unknown, Monster`**.
Another Elite meant another relic and another White Star rare, but **the first
Elite cost 39 HP starting from a full 62**, and I was at 41 with only one
RestSite left before the boss. Took the Unknown.

### Unknown (floor 28) — a chest

`Strawberry — Upon pickup, raise your Max HP by 7.` Taken. It raised the cap
**and healed the same 7**: `41/62` became **`48/69`**.

### Fight 11 — Ovicopter (HP 124) + 3 summons, entered at 48/69

The first battle screen was also where I learned what the Elite's relic does,
since the reward screen only named it:

```
- Razor Tooth — Every time you play an Attack or Skill, Upgrade it for the remainder of combat.
```

That is a genuinely good relic for this deck and it changes how a turn is played:
spare energy is never wasted, because a "useless" Defend still banks a permanent
upgrade for the rest of the fight. Later in this same combat `Run Away!+` printed
`Gain 14 Block` and `Dig In` printed **`Gain 18 Block`** — Vambrace doubling a
Razor-Tooth-upgraded card, for **zero Energy**.

**Round 1** — intent `Summon`, so a free turn: Explosives Workshop (1),
Kaboom! (10), Strike (9), Ka-pow! (4, played only to bank its Razor Tooth
upgrade, since no bomb existed to set off). Predicted `115 → 92`. Exact.

**Round 2** — three `Tough Egg`s appeared, each `Hatch 1` and, decisively:

```
- Minion 1 (buff) — Minions abandon combat without their leader.
```

so the whole fight is "kill the Ovicopter". `Dig In` (18 Block, **0 Energy**),
Fish-Flavored Bait+, Strike, Duck and Cover. Predicted `92 → 76`, `Bomb 11`, and
**0 damage taken**. All exact.

Also useful tool behaviour, not a defect: `The Big One` printed
`CANNOT BE PLAYED: no enemy is holding a Bomb`, and `Powder Charge` later printed
`CANNOT BE PLAYED: you have no Spark, and this costs 1`.

**Round 3 — the act-1 Vulnerable question, answered.** The eggs hatched into
three Hatchlings printing `the number on its icon is 4`, and the Ovicopter's
Debuff landed `Vulnerable 2` on me. **The next screen printed those same
Hatchlings at `the number on its icon is 6`** — and 4 x 1.5 = 6.

**The printed intent number already folds in my own Vulnerable.** The act-1 seat
recorded this as one of the things it "could not tell", with two readings and no
way to separate them. Here the same three enemies printed 4 and then 6 across the
debuff landing, which separates them (finding 10).

Spent the **Block Potion** here — 12 Block against 19 incoming with no Block card
in hand — the first potion used in either act. Jumpy Dumpty and Chain Fuse took
the stack to `Bomb 31`, Strike took the leader to 67. Predicted 7 taken → **41**.
Exact.

**Round 4 — the Splash's targeting rule.** `Bomb 41`, four enemies, and the
Splash reads `deal Pyro damage to a **random enemy** equal to the Bombs on it`.
Only the Ovicopter carried bombs, so I deliberately put **both Pop!s on the
Ovicopter as well** rather than spreading them: if "random" ranges over all four
enemies, spreading raises the average, but if it ranges only over enemies that
*have* bombs, spreading would cut the chance of the big hit from certain to one
in three.

Predicted `Bomb 51`, `Block 12`, 6 taken → **35**, and the Splash for 51.
**Observed: the Splash hit the Ovicopter for exactly 51 (`67 → 16`)**, and every
other number exact. **The Splash goes to the bombed enemy** — at least when only
one is bombed, which is the only case I tested.

**Round 5 — the tightest turn of the act.** The Ovicopter Empowered to
`Strength 3` and a **28** intent; with the three Hatchlings that is **46 incoming
at 35 HP**, and my hand held **no attack and no detonator** — Pop!, Explosives
Workshop, Mine Toss+, Sparks 'n' Splash+, Defend, Sorry Jean.

Two readings decided it:

1. **Do not play `Mine Toss+`.** It places a Mine on *ALL* enemies, which would
   have given the Hatchlings bombs and so pulled the Splash off the 16 HP leader
   — the exact opposite of what round 4 had just taught me.
2. **`Sorry, Jean...` is the block card.** It removed the **largest** bomb —
   `Bomb 71 → 44` — and paid **`Block 27`** for **zero energy**. Nothing else in
   the deck comes close.

Added Defend (6 → `Block 33`) and a Pop! back onto the Ovicopter, keeping bombs
exclusive to it. Predicted: the end-of-turn Splash pays 49 into a 16 HP leader,
kills it, and **the minions abandon before anything swings**; and if the Splash
somehow missed, 46 − 33 = 13 taken, leaving me alive at 22.

**The leader died and the whole fight ended at 35/69, taking 0 that round.**

### Fight 11 reward

`12 Gold` (→ **142**) and a card. **Took `Rosaria — Ravaging Confession`**
(`cost 1, attack [Cryo] — Deal 9 damage. If the enemy has an aura, apply 1
Vulnerable.`) over `Flame Dance+`, `Ammo Scavenging` and a plain
`Fish-Flavored Bait`.

The reason is a mechanism the screens have already proved, and it is the sharpest
piece of deckbuilding I did all act:

- Fight 8 measured that a **Set off is separate hits** — `Bomb 56` across three
  bombs delivered 70, because Vaporize multiplied **one** 21-point bomb and not
  the badge total.
- But the **Splash pays the whole stack as a single Pyro hit** — 51 in one number
  this fight.
- So an Elemental Reaction on the *Splash* multiplies **everything**, where the
  same reaction on a *Set off* multiplies about a third of it.

Rosaria applies **Cryo**, and `Melt — Pyro on a Cryo aura … deals 1.75x damage`
is the largest multiplier on the glossary. Her Vulnerable also lands on the
**enemy**, and the Bomb glossary is explicit that a bomb's hit "takes the enemy's
debuffs, not yours". The act-1 seat passed on Lisa for exactly this idea because
it could not verify it blind; I now have the two measurements that make it
checkable.

### RestSite (floor 30) — Rest

`35/69` → **55/69**, which is also above the 70% line (48.3) that switches
`Yumemizuki Mizuki` from `Mend 10` to `18 damage to ALL enemies`.

---

## BOSS — Knowledge Demon (HP 379), entered at 55/69

Opened at `370/379` — Festive Popper's full 9 for the third boss in a row.

**379 HP is more than twice the act-1 boss's 252**, and unlike the Ceremonial
Beast it prints **no threshold**: no `Plow 150`, no brake, nothing to aim a burst
turn at. Its shape is instead a grinder — it **Heals**, it **Empowers**, and
twice in the fight it hands you a **choice of two status cards**, both of which
attack something Klee specifically does.

**Round 1** — intent `Strategic (Debuff)`, a free setup turn: Explosives
Workshop (1), Mine Toss+ (1) for a `Mine 7`, `Sparks 'n' Splash+` (1). I did not
play a Block card, because both of mine (`Run Away!+`, `Dig In`) are **0 Energy**
and playing one on a null turn would have spent Vambrace's doubling for nothing.

**The first debuff — and the Ancient choice paying off in an unplanned way.**

```
- Disintegration — cost 0, status — At the end of your turn, take 6 damage.
- Mind Rot       — cost 0, status — Draw 1 fewer card each turn.
```

**Took Mind Rot.** Against a 370 HP boss this fight was always going to be long,
and 6 a turn compounds without bound where one card of draw does not — and
**`Pael's Blood` from the first floor of the act cancels Mind Rot exactly.** My
hands went from 6 cards back to 5, i.e. to the number everyone else plays with.
I did not pick Pael's Blood for this, but it is the single luckiest interaction
of the act.

**Round 2.** Boss `363`, intent 17, and a hand with **no bomb placer and no Block
card**. Played Kaboom! (10) and two Strikes (9 each) and, deliberately, **did not
Set off** — `Ka-pow!` has Retain, so banking it costs nothing, and the Mine was
worth strictly more left alone: the Splash pays it *and* it self-triggers on the
boss's attack.

Predicted `28 (cards) + 12 (Splash) + 12 (the Mine going off before the hit)` =
**52**. Screen: `363 → 311`, and `Spark +1` for the Mine. Exact.

The cost of that is worth recording: **`Mine Toss+` is anti-synergy with the
Splash against an attacking boss**, because the Mine spends itself every time the
enemy swings and so never joins the growing stack.

**Round 3.** `Powder Charge` (0 Energy, 1 Spark) and `Jumpy Dumpty` for two
bombs, `Chain Fuse` for +6 on each, `Defend` for 12. Predicted `Bomb 26`, Splash
26, 12 taken. All exact — `311 → 285`, `38 → 26`.

**Round 4 — the turn the whole act's reading paid off.** The boss printed
`Attack 11 · Heal · Empower`, I was at 26 HP, and the hand held `The Big One`
(Set off for **quadruple**) next to a `Bomb 36`. Quadrupling 36 is **144 damage
in one card**, which is the obvious play and, I think, the wrong one.

I passed on it for a reason the screens had already given me: **`Ka-pow!` is
retained in my hand permanently and sets off the entire stack for 0 Energy.** I
already owned a free finisher, so the stack was worth far more growing than
cashed — and The Big One costs all 3 Energy, which would have meant no blocking
and no building on the turn I played it.

Instead: `Fish-Flavored Bait+` (7 damage, `Bomb 42`), **`Rosaria`**, the second
`Explosives Workshop`, and the **Weak Potion** — unused since act 1.

Rosaria's card face had rewritten itself with
`*Reaction preview: Melt* — … 1.75x damage and consumes the aura`, because she
supplies **Cryo** into the boss's Pyro aura. Predicted `Bait 7 + Rosaria 9 x 1.75
(= 15)` = **22**. Screen: `285 → 263`, exact.

Three things landed on that one screen:

```
- Explosives Workshop 2 (buff) — At the start of your turn, your Bombs grow by 2 more.
- Bomb 62 (buff) — Set off here deals 62 Pyro damage after Vulnerable. Bombs here: 3.
- Weak 3 (debuff) — Attacks deal 25% less damage for 3 turns.
```

- **Explosives Workshop stacks**: two copies, `grow by 2 more`.
- **`after Vulnerable`.** The bombs totalled 42; the badge printed **62**, which
  is 42 x 1.5. **Vulnerable on the enemy multiplies bomb damage, and the badge
  says so in words.** This is the act-1 seat's open question — it passed on Lisa
  for exactly this idea and wrote "I could not verify that blind" — answered on a
  screen (finding 11).
- The Weak Potion cut the printed intent from 11 to **8** (11 x 0.75 = 8.25).

End of turn: `263 → 230`, a net −33 across a Splash of ~62 and the boss's Heal.
Took 8 → **18/69**.

**Round 5.** Intent `Debuff` only — a second free turn, spent entirely on the
engine: `Pop!` (`Bomb 65`, 4 bombs), the **second `Sparks 'n' Splash+`**, and
`Nicole`. Predicted the Splash for 65: `230 → 165`. Exact.

**The second debuff.**

```
- Disintegration — At the end of your turn, take 7 damage.   (it was 6 last time)
- Sloth         — You cannot play more than 3 cards each turn.
```

**Took Sloth.** At 18 HP, 7 a turn kills me in three rounds and nothing in my
deck heals. But note what the pair is doing: `Mind Rot` taxes **draw** and
`Sloth` caps **cards played per turn**, and "more cards than you have energy for"
is the whole feel of this character. Both of this boss's debuffs are aimed at the
same place `Tender` and `Vital Spark` were.

**Round 6.** `Bomb 89` across 4 bombs, `Sparks 'n' Splash 2`, and Sloth allowing
three cards: two `Pop!`s to `Bomb 99` and a `Defend`.

**The double-Splash measurement, finally clean.** The buff read
`Sparks 'n' Splash 2` at the start of the turn, the stack was 99, and the payout
was **99 — `165 → 66`, paid once.** A second copy of the power **does not double
the payment** (finding 9). Took 3 → **15/69**.

**Round 7.** `Bomb 135` across 6 bombs against 66 HP, with `10x3` = 30 pointed at
my 15. **`Ka-pow!`, 0 Energy, set off 135 into 66.**

**KNOWLEDGE DEMON KILLED at 15/69**, on turn 7, with the free retained detonator
I had been holding since round 2 — which is the whole argument for having passed
on The Big One three rounds earlier.

### Boss reward

`100 Gold` (→ **242**), the potion **`Droplet of Precognition`** (claimable at
last: I had spent two potions this act, so a slot was free — and **no screen ever
said what it does**), and a card.

**Took the second `Nicole — Revelation, Uncreated Light`** over `Sugar Rush`,
`Chained Reactions` and `Alice's Introduction Magic`. In both long fights of the
act Nicole was the best card I drew and in both she arrived late — round 3 of 6
in the Elite, round 5 of 7 in the boss. A second copy halves that wait, and her
`5 Block` a turn is the most block-per-energy in the deck while her Strength adds
flatly to every Splash. `Chained Reactions` pays only when Bombs **go off**,
which in Splash mode is almost never; `Alice's` is dead because I own no card
that pays for Hexerei.

Proceeding put the lane on the **act-3 map**, boss **Aeonglass**.

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

**Passing on `The Big One` at the boss.** `Bomb 36`, "Set off for quadruple
damage", 144 in one card, at 26 HP against a boss that heals. The reason to
refuse it is that **`Ka-pow!` has Retain and sets off the whole stack for 0
Energy**, so the finisher was already in hand for free and the stack was worth
more growing. The stack went 36 → 42 → 65 → 89 → 99 → **135**, and Ka-pow! cashed
it for nothing four rounds later. That is the single best decision I made, and
it is made entirely out of the word "Retain" on a card face.

**Whether to detonate at all** is still the character's central tension, and act 2
gave it a sharper edge than act 1 did, because it produced the **one board state
where detonating early was clearly right**: the Tunneler's
`Burrowed — Stunned if all Block is removed` behind `Block 32`. Growth is worth
more than tempo *unless* there is a threshold, and then it is worth much less.
Fight 10 was the same shape — 51 HP with a `7x3` intent, so cashing 50 to end the
fight beat banking it.

**The Spark contest.** `Powder Charge` and `Dig In` both cost 1 Spark, and
because the Splash means bombs never go off, `Pounding Surprise` never refunds
me: **in Splash mode the bank is one Spark per combat.** Fight 9 round 2 was
literally "a Bomb 6 that pays into every future Splash, or 9 Block right now".

**Routing into the Elite, and then refusing the second one.** Rest to 62, take
the Elite, come out at 23; then at 41 with one RestSite left, decline the next.
The same map screen, opposite answers, both driven by a number the map never
prints.

**`Rejection` over `Let It In`** — paying 10 HP for an upgrade rather than taking
a heal that **caps and wastes 12 of its 25**, because a RestSite was the only
room on its floor five floors on.

**The Splash's targeting.** Fight 11 round 4: four enemies, bombs on one. Putting
the two Pop!s on the *same* enemy rather than spreading them was a bet on what
"a random enemy" means, and round 5 turned that bet into the win condition —
**not** playing `Mine Toss+` so the Splash could not be pulled off the 16 HP
leader.

### (b) What felt automatic, and what never seemed worth playing

**`Pop!` is still automatic in the good way** — 0 cost, always right, never a
decision. `Powder Charge` likewise for most of a fight.

**Strike and Defend remain the worst cards in the deck**, and act 2 made that
worse rather than better: `Strike Dummy` and Nicole's Strength pushed Strike to
9, then 11, then 13 — and it was still a rounding error next to a `Bomb 89`.
Across the whole act I never once had to think about whether to play a Defend.

**Never worth playing:** `Barbara — Melody Loop`, which I now know why (below);
`Alice's Introduction Magic` and `Catalytic Converter` and `Prune`, all of which
need a mechanic this deck cannot make; and **`Spoils Map`, which is not merely
weak but a permanently dead card** — I drew it in fights 9 and 10 and it printed
`CANNOT BE PLAYED: has unplayable keyword` both times. Its promised 600 gold
**never appeared anywhere in act 2**, and the act named as "the next Act" is now
over.

**`Mine Toss+` turned out to be a mistake against bosses**, though a good card
against summons. The Mine cashes itself the moment the enemy attacks, so it is
the one bomb that can never join the growing stack.

### (c) What I could not understand, or that contradicted its own printed text

- **`Strike Dummy` boosted `Kaboom!`.** It reads `Cards containing "Strike" deal
  3 additional damage.` Kaboom! contains no "Strike" anywhere on its face and
  went from `Deal 7 damage` to `Deal 10 damage` the floor I picked the relic up.
  `Ka-pow!` stayed at 4 (finding 6).
- **`Tainted 2` did not appear in the damage once**, on the one turn the intent
  was multi-hit, where the identical arithmetic had held exactly twice before
  (finding 8).
- **`Run Away!+` paid 12 Block where its own two printed numbers add to 11**
  (finding 7).
- **The 31 HP that arrived between the acts** (finding 1).
- **`Droplet of Precognition`, `Razor Tooth` and `Strawberry` were all named and
  never described** at the moment I took them; two of the three I learned from a
  later battle screen, and the potion I still cannot describe.
- **Whether `Flutter` halves bomb damage.** Fight 9 round 3 was the clean test
  and I deliberately did not run it, buying a guaranteed kill instead at 34 HP.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted: `Spoils Map`, again, and now with the receipt.** Act 1's seat
called it a permanent dead card; act 2 is the act its text promised to pay in,
and no marked site appeared on any of the 31 floors I saw.

**Happiest to draw: `Sorry, Jean...`** — `cost 0, skill — Remove one of your
Bombs. Gain Block equal to its size.` It removed the **largest** bomb and paid
**27 Block for zero energy** at the exact moment three Hatchlings and an
Empowered Ovicopter had 46 damage pointed at my 35 HP. It is the only card in the
deck that converts the engine directly into survival, and it scales with the
engine, which is precisely the shape a bomb deck needs and otherwise lacks.

Runner-up is `Ka-pow!`, for the boss.

### (e) Did the previous seat's three sharpest findings hold up

**Its finding 1 — printed numbers silently fold in buffs, with no marker.**
**Held, repeatedly, and it is worse than act 1 recorded.** `Dig In` printed
`Gain 8 Block` on the shop shelf, `Gain 9` in combat (Dexterity), and
**`Gain 18`** with Vambrace unspent and Razor Tooth applied. `Strike` printed 6,
9, 11 and 13 across the act. `Kaboom!` printed 7 and then 10. Nothing anywhere
distinguishes a base number from an adjusted one.

**Its finding 2 — Vambrace makes every Block card in hand print its doubled
value though only one can pay it.** **Held exactly.** Fight 8 round 2 my hand
showed **four Defends all reading `Gain 12 Block`**; only the first would have
paid 12.

**Its finding 7 — the Splash pays the stack every turn and spends nothing, which
silently makes every detonator worse.** **Held, and it governed my whole act** —
it is why I refused `Fwoosh!+`, `Sizzle+`, `Quick Fuse`, and `Careful
Arrangement` three separate times. But act 2 **qualifies** it in two places the
act-1 seat could not have seen: detonation is right against a **threshold**
(`Burrowed`) and as a **finisher** (Ka-pow! for 135), and `Careful Arrangement`
is even worse than act 1 argued, because my Workshop measurement proves growth is
**per bomb** — merging four bombs cuts growth from 24 a turn to 6.

**One of its conclusions did not hold.** Act 1 took a second `Sparks 'n' Splash`
as its boss reward reasoning "the power stacks … so drawing both is pure upside".
The stacking is cosmetic: `Sparks 'n' Splash 2` paid **99 once**, not twice
(finding 9).

**And two of its open questions are now answered:** Vulnerable does apply, and
the printed intent already includes it (findings 10 and 11); and Barbara's Hydro
really is eaten by my own Pyro aura (finding 2).

### (f) Did act 2 ask anything of the deck that act 1 did not

**Yes — four things, and three of them are aimed at this character specifically.**

1. **Clocks.** `Escape Artist 5` (kill 79 HP in five turns or it leaves) is a
   damage floor act 1 never set. A bomb deck that banks growth is exactly the
   deck that fails a clock, and it forced the one turn I spent The Big One.
2. **Card-count taxes.** `Tender` (lose 1 Strength and 1 Dexterity per card
   played), `Vital Spark` (**ALL Skills** are Tainted 2, then 4), and the boss's
   `Sloth` (no more than 3 cards a turn). Klee's signature is five cards on three
   energy; **three separate act-2 enemies charge for exactly that**, and
   `Vital Spark` charges for it hardest because almost every Klee card is a Skill.
   The counter-play is real and readable — Powers are not Skills, so
   `Explosives Workshop` and `Nicole` walk past `Vital Spark` untaxed.
3. **Walls and persistence.** `Burrowed` (Block is not removed at the start of
   its turn) and enemies routinely holding `Block 11`–`32`. Act 1 had no block to
   punch through at all.
4. **Multiple bodies with one leader.** Three Tough Eggs plus `Minion — Minions
   abandon combat without their leader`, against a deck whose placers are
   single-target and whose Splash hits **one** enemy a turn.

### (g) Anything a screen granted or changed without saying so

- **31 HP between the acts** (finding 1) — much the largest.
- **`Strawberry` healed 7 as well as raising the cap** (41/62 → 48/69). Its text
  says only "raise your Max HP by 7".
- **The stolen card came back unnamed.** `Swipe 1 — Upon killing this enemy, the
  stolen card is returned`; my deck count went 27 → 26 → 27 and **no screen ever
  said which card left or returned**.
- **`Razor Tooth` and `Droplet of Precognition` were named but never described**
  on the screen that gave them.
- **Card faces silently rewrite themselves**, still, and now from five different
  sources at once (Dexterity, Strength, Vambrace, Strike Dummy, Razor Tooth).
- **`Sparks 'n' Splash 1 → 2` incremented a full turn after the second copy was
  played**, so the screen and the effect disagreed for one turn.

---

## Findings, ranked by sharpness

**1. 31 HP arrived between the acts and no screen announced it.** The act-1
record closes the run at **31/62** and says so twice. I then opened the map, the
Pael event, and a `Proceed`. The next screen with an HP line, round 1 of fight 8,
printed **`HP 62/62`**. This is a full heal — half the character's maximum —
delivered silently across an act boundary, and it invalidates any HP plan a seat
makes at the end of an act. It is also the reason I cannot state the lane's HP
for the next seat with confidence: **the same thing may happen again on the way
into act 3.**

**2. Barbara's Hydro is consumed by my own Pyro aura, and the screen shows it.**
Act 1 spent **74 gold** on `Barbara — Melody Loop` to Vaporize its Splash, never
saw a Hydro land on the boss, and recorded the explanation as a reading it could
not check. Fight 8 checks it. Round 3 the Hydro landed clean on a **bare**
Tunneler (`Hydro Aura 1`) and Vaporized a 21-point bomb to 31, exactly as
designed. Round 4, Melody Loop applied its second Hydro to the *same* enemy now
wearing `Pyro Aura 2` from my own Set off, and the screen printed **no aura line
at all** with the enemy's HP unchanged: the Hydro was consumed to Vaporize a hit
carrying no damage, and took the Pyro with it. **A Pyro deck cannot hold a Hydro
aura for its own use except on the first hit of a fight**, which makes every
Hydro companion card in the game close to dead in this deck, and the card's own
text says nothing about it.

**3. An Elemental Reaction is worth ~3x more on the Splash than on a Set off, and
nothing says so.** Fight 8: `Bomb 56` across three bombs (21/21/14) with a Hydro
aura up, Set off by Ka-pow!, delivered exactly **70** — one 21-bomb Vaporized to
31, the other two paid flat, plus Ka-pow!'s 4. **Vaporize multiplied one hit of
three.** But the Splash pays the whole stack as a **single** Pyro hit — 51 in one
number in fight 11 — so the same reaction on a Splash multiplies **everything**.
This is the deepest thing I found, it is what made `Rosaria` the right pick over
an AoE card, and **it is invisible**: the badge prints one number, `Bomb 56`, for
something that is three separate hits when detonated and one hit when Splashed.

**4. `Vital Spark` charges for a mechanic whose cost is unreadable until you have
paid it.** The Elite prints `ALL Skills are Tainted 2`; every Skill in hand then
prints `Gain 2 Tainted`; and the glossary's entry for Tainted reads, in full,
`*Tainted* — Gain 2 Tainted when played.` **Nothing on the screen says what
Tainted does.** I had to spend a card — I chose a 0-cost Pop! specifically to pay
as little as possible — and read the status block afterwards to learn
`Take 2 additional damage from Attacks this turn`. That is a debuff on a boss-tier
enemy whose price you cannot price before committing to it.

**5. A card was taken out of my deck and returned, and no screen ever named it.**
Fight 9's Thieving Hopper printed `Malicious (CardDebuff)`; my pile counts went
from a 27-card deck to **26** (6 + 14 + 6); the enemy then printed `Swipe 1 —
Upon killing this enemy, the stolen card is returned`; and the reward screen
offered `Take your stolen card back.` **At no point was the card named.** If it
had escaped with the card — which is what `Escape Artist 5` was counting down to
— I would have finished the act not knowing what I had lost.

**6. `Strike Dummy` does not do what it says.** It reads
`Cards containing "Strike" deal 3 additional damage.` On the floor I took it,
`Strike` went 6 → 9 (correct) and **`Kaboom!` went 7 → 10**, while `Ka-pow!`
stayed at 4. Kaboom! contains no "Strike" on any part of its printed face. Either
the relic's rule is not the printed one, or it is matching something the player
cannot see.

**7. `Run Away!+` pays 12 Block where its own two printed numbers add to 11.**
Its face: `Gain 7 Block. If a Bomb went off this turn, gain 4 additional Block.`
Played immediately after a Set off, the status block read **`Block 12`**. The
conditional half picked up Dexterity that the printed `4` did not show — so the
card's own arithmetic does not reconcile against its own face even after you
account for the buff folded into the first number.

**8. Tainted's arithmetic held twice and then failed by 2 against a multi-hit
intent.** Elite round 1: intent 15, `Tainted 8`, Block 12, took **11** =
15 + 8 − 12. Round 2: intent 11, `Tainted 4`, Block 6, took **9** = 11 + 4 − 6.
Round 3: intent **`7x3`** = 21, `Tainted 2`, Block 12, took **9** — which is
21 − 12 with the +2 nowhere, and there is no split of three hits against a
12-point Block pool that yields 9 with the Tainted included. **I could not tell
why**, and the only structural difference is that this was the one multi-hit
intent.

**9. A second copy of `Sparks 'n' Splash` adds nothing to the payment.** Measured
twice. In the Elite, playing the second copy left the buff reading
`Sparks 'n' Splash 1` for the rest of that turn and the payout was a single 25.
At the boss, with the buff reading **`Sparks 'n' Splash 2`** at the start of the
turn and `Bomb 99` on the board, the payment was **99 — `165 → 66`**, once. The
counter increments; the damage does not. **Act 1 took its boss reward on the
opposite belief** ("the power stacks … drawing both is pure upside"). The second
copy is still worth having, but only for draw consistency, and the screen's
`2` actively suggests otherwise.

**10. The printed intent number already includes my Vulnerable.** Act 1 recorded
this as untestable: "Either the printed intent already folds Vulnerable in, or it
did not apply. I could not tell which, and no screen says." Fight 11 separates
them cleanly, because the debuff landed between two readings of **the same three
enemies**: three Hatchlings printing `the number on its icon is 4`, then
`Vulnerable 2` on me, then those same three printing **`6`**. 4 x 1.5 = 6.

**11. Vulnerable on the *enemy* multiplies bomb damage, and the bomb badge says
so in words.** Boss round 4, after Rosaria applied `Vulnerable 1`, the badge read
**`Bomb 62 (buff) — Set off here deals 62 Pyro damage after Vulnerable`** on a
stack of 42 (42 x 1.5 = 63). This is the act-1 seat's Lisa question — it passed
on a card because "bombs take the enemy's debuffs … I could not verify that
blind" — settled, and settled by the game volunteering the phrase `after
Vulnerable`. It is also the best single line of UI I saw in either act: a derived
number that names its own modifier.

**12. Growth is per bomb, which makes one shop card and one event card
three-quarters cuts to the engine that read like upgrades.** `Explosives Workshop`
says `your Bombs grow by 1 more`; two bombs at `Bomb 10` became **`Bomb 20`** next
turn (10 + 4x2 + 1x2), so the +1 is per bomb, and two copies stack to
`grow by 2 more`. At the boss I had six bombs growing **36 a turn**.
`Careful Arrangement` (74 gold in the shop, and offered again upgraded as a
reward) says `Move all your Bombs onto the enemy as one Bomb. It grows by 5` —
which against that same board would have cut 36 a turn to 6. I refused it three
times; a player who reads it as consolidation buys it.

**13. `Spoils Map`'s promised gold never arrived.** `Unplayable. Marks a site of
600 extra Gold in the next Act.` Act 2 **is** the next Act. I saw all 16 floors
of the act-2 map on every map screen and no site was ever marked, no screen
mentioned it, and my gold is fully accounted for by printed rewards
(163 + 15 + 20 + 15 + 45 + 12 + 100 − 128 spent = **242**). Meanwhile the card is
not Ethereal, so unlike Clumsy it never removes itself: I drew it dead in fights 9
and 10. **I could not tell** whether the site exists and I failed to route to it,
whether "next Act" means act 3, or whether it does not pay at all — but nothing on
any screen would let a player tell either.

**14. Klee's own defensive cards are the best thing that happened to the deck,
and they are all zero-Energy.** `Run Away!+` (0 Energy), `Dig In` (1 Spark, **no
Energy**) and `Sorry, Jean...` (0 Energy) turned the act around: fight 8's only
damage came from the one round with no Block card in hand, and by the Elite I was
playing **five cards on three energy** — `Sparks 'n' Splash+`, `Pop!`,
`Fish-Flavored Bait+`, `Strike` and `Dig In` — for 33 damage and **zero taken**.
`Sorry, Jean...` is the standout because it is the only card that converts the
engine into survival and **scales with it**: 27 Block off a single bomb.

**15. This boss is a grinder where act 1's was a puzzle, and I think act 1's was
better.** The Ceremonial Beast printed `Plow 150` — a threshold, a stated reward
for crossing it, and a timing subtlety about *when* you cross. The Knowledge
Demon prints no threshold at all: 379 HP, a Heal, an Empower, and two forced
status cards. It is a longer and harder fight and it was decided by arithmetic
(hold the stack, cash 135 with a free card) rather than by reading anything. The
one genuinely good thing it does is that **both of its debuff pairs make you
choose which part of your own character to give up** — draw, or HP; cards per
turn, or HP.

**Where I could not tell:** whether `Flutter` halves bomb damage (I bought the
guaranteed kill instead); why `Tainted` failed once against a multi-hit intent;
whether the Splash's "random enemy" ranges over all enemies or only bombed ones
(every case I saw had exactly one bombed enemy); how much the Knowledge Demon
healed on the one turn it healed; what `Droplet of Precognition` does; and
whether `Mind Rot` and `Sloth` are still in the deck now that the fight is over.

---

## Non-blindness declaration

- **Commands run:** only the two permitted forms,
  `GITS_LANE=2 python -m understudy.blindplay observe` and
  `GITS_LANE=2 python -m understudy.blindplay act "<command>"`, from the repo
  root `C:\Users\Monty\Documents\GitHub\GItS`. **No other `understudy`
  subcommand was run at any point** — no `harness`, `session`, `audit`, `notes`,
  `scenario`, `staged_turn`, `soak`, or `embark`. **No `git`.** Some `observe`
  output was piped through `sed` and `grep` to trim it; one such pipe used
  overlapping `sed` ranges and printed a status block twice, which is a display
  artefact of my own command and not of the game.
- **Tools used:** `Bash` (the two commands above), `Read` (once), and `Write` /
  `Edit` (this record only).
- **Repo files read: exactly one** —
  `review/qa/klee-round-8-2026-09-03/opus-run2-act1.md`, the previous seat's
  record, as instructed. No source, YAML, docs, rulings, backlog, register, or
  any other record was opened. No scratch file was created. Everything above
  comes from screens the tool printed; where I state a rule it is either quoted
  from a screen or explicitly marked as my inference.
- **Files written:** this record only —
  `review/qa/klee-round-8-2026-09-03/opus-run2-act2.md`. **No identifiers were
  minted.**
- **Lane:** lane 1 was never touched. The game was never launched, closed,
  restarted or torn down.
- **The lane is left standing** on the **act-3 map screen**, boss **Aeonglass**,
  with the single node `Ancient (path 1)` offered, **nothing selected and no
  screen half-resolved.**

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
