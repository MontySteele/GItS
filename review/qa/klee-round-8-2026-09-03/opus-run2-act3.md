# KLEEMOD-KLEE — blind seat, lane 2, run 2, act 3

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, round 8, run 2, **third seat of
  three** (act 3 to the end of the run).
- **Lane:** 2.
- **Character:** KLEEMOD-KLEE.
- **Picked up:** on the **act-3 map screen**, exactly where the second seat left it
  — one node offered (`Ancient (path 1)`), boss named **Aeonglass**, 15 floors.
- **Act:** 3. Boss the map named at the top of the act: **Aeonglass**, HP **512**.
- **Actions:** **189 commands issued, 188 of them visibly accepted, 0 refusals
  printed.** One command — the first `choose "Chain Fuse"` at the floor-14 Smith —
  was issued inside a chained call whose output I had piped away, and the next
  `observe` showed the Smith option still on offer, so I cannot say whether it was
  accepted and backed out or refused; I re-issued the sequence and it worked. No
  tool error occurred at any point.
- **Termination reason:** **stop condition (1) — the run ended.** The act-3 boss
  was killed, its reward screen (which held nothing) was proceeded through, the
  post-boss `The Architect` event was answered, and the next command returned
  **`TOOL-BLOCKED: game_over` / "the run is over; there is nothing left to play" /
  "The run ended on floor 48."** Budget was never a factor (189 of 300).
- **Where the run stands:** **RUN COMPLETE. Aeonglass killed at 36/69 on round 5**,
  with Klee alive. The lane stands on the game-over state; there is nothing left
  to play and no screen is half-resolved. **No screen anywhere said whether the run
  was won** — see finding 9.

### HP trajectory (every reading the screens printed, in order)

Max HP was 69 throughout.

**`69/69`** (fight 12 r1 — the act boundary healed 15 → 69 silently) `69/69`
`64/69` `62/69` (**fight 12**) → `62/69` `62/69` (**fight 13**) → `62/69`
`52/69` `52/69` `46/69` `46/69` (**fight 14**) → smith at `46/69`, no heal →
**rest 46 → 66** → `68/69` (Blood Vial) `66/69` `66/69` `66/69` `66/69`
(**ELITE**) → **rest 66 → 69** → `69/69` `54/69` `54/69` `54/69` `36/69`
(**BOSS**) → final **36/69**.

Damage taken in the whole act: **7 + 0 + 16 + 2 + 33 = 58**, across three fights,
an Elite and the boss. **33 of the 58 came from the boss**, and 16 more from the
one enemy (Frog Knight) that regenerated Block every round.

### Gold / potions / relics (exactly as printed)

- **Gold: 161.** Traced: 242 carried in, `+14` `+12` `+16` from fights 12–14 =
  **284** — and then **the first shop opened saying `You have 1028 gold`**
  (finding 2). From 1028: −503 at shop 1 (Grounded 37, Miniature Tent 185,
  Whetstone 183, Swift Potion 49, Power Potion 49), −100 Card Removal, `+42`
  (Elite) = 467, −181 `Orrery`, −125 Card Removal = **161**.
- **Potions: 3 of 3, none used at the boss.** `Energy Potion` (Gain 2 Energy),
  `Swift Potion` (Draw 3 cards), `Power Potion` (Choose 1 of 3 random Power cards
  to add into your Hand; free to play this turn). `Droplet of Precognition` was
  spent in fight 14 and is the single best card the run drew (see below). A
  `Power Potion` from the Elite went unclaimed to full slots.
- **Relics (16)**, exactly as the battle screen prints them:
  - **Pounding Surprise** — Whenever a Bomb goes off, gain 1 Spark.
  - **Large Capsule** — Upon pickup, obtain 2 random Relics. Add an additional Strike and Defend to your Deck.
  - **White Star** — Elites drop an additional Rare card reward.
  - **Oddly Smooth Stone** — Start each combat with 1 Dexterity.
  - **Festive Popper** — At the start of each combat, deal 9 damage to ALL enemies.
  - **Vambrace** — The first time you gain Block from a card each combat, double the amount gained.
  - **Pael's Blood** — At the start of your turn, draw 1 additional card.
  - **Razor Tooth** — Every time you play an Attack or Skill, Upgrade it for the remainder of combat.
  - **Strawberry** — Upon pickup, raise your Max HP by 7.
  - **Sai** — At the start of your turn, gain 7 Block.
  - **Blood Vial** — At the start of each combat, heal 2 HP.
  - **Centennial Puzzle** — The first time you lose HP each combat, draw 3 cards.
  - **Miniature Tent** — You may choose any number of options at Rest Sites.
  - **Whetstone** — Upon pickup, Upgrade 2 random Attacks.
  - **Pendulum** — Every 3 turns, draw 1 card.
  - **Orrery** — Upon pickup, gain 5 card rewards.

  **`Strike Dummy` was traded away** at the Relic Trader. `White Star` paid once,
  at the act's single Elite.

### Deck as I reconstruct it (37 cards)

Strike · **Strike+** · Defend ×3 · Duck and Cover · Kaboom! · **Ka-pow!+** ·
**Jumpy Dumpty+** · **Powder Charge+** · Pop! ×3 · **Nicole+** · Nicole ·
**Sparks 'n' Splash+ ×2** · Sparks 'n' Splash · Explosives Workshop ×2 ·
**Explosives Workshop+ ×2** · Barbara — Melody Loop · **The Big One+** ·
**Chain Fuse+ ×2** · **Spoils Map** (still unplayable, still unremovable) ·
Run Away! · Dig In · **Mine Toss+** · **Fish-Flavored Bait+** · Sorry, Jean... ×2 ·
Yumemizuki Mizuki · Rosaria · **Diona** · Grounded · **Bully**.

**The count does not reconcile with the second seat's, and the gap is theirs, not
mine.** Fight 12 opened with `26 in the draw pile` + 6 in hand = **32 cards**,
where act 2 reconstructed 33. The likeliest candidate is fight 9's stolen card,
which no screen ever named either when it left or when it came back. `Mind Rot`
and `Sloth` did **not** persist out of the act-2 boss fight.

---

## Screen by screen

### Ancient (floor 1) — "Tanx"

```
- Spiked Gauntlets   Gain [Energy] at the start of each turn. Powers cost 1 more [Energy].
- Sai                At the start of your turn, gain 7 Block.
- Claws              Transform up to 6 cards into Maul.
```

**Chose Sai.** Reasoning from the two previous records: HP has been the binding
constraint in every fight of both acts, never damage, and the deck's whole block
suite is 5–8 a card. `Sai` is 7 Block every turn, unconditional, costing no card
and no energy — and because it is a relic and not a card it should not spend
`Vambrace`'s doubling (confirmed below: round 1 opened `Block 7` with every Block
card in hand still printing its doubled face).

`Spiked Gauntlets` was the tempting one — 3 energy to 4 — but I own **six Powers**
(`Sparks 'n' Splash+` ×2, `Nicole` ×2, `Explosives Workshop` ×2) and the whole of
act 2 was spent paying to get the Splash from cost 2 down to cost 1. "Powers cost
1 more" undoes both upgrades and puts `Nicole` at 3. `Claws` transforms up to 6
cards into `Maul`, a card no screen described; blind, that is six unknown cards
for six known ones.

### Fight 12 — Devoted Sculptor (HP 162), entered at 69/69

**The act boundary healed again, and again silently.** The second seat's record
closes at **15/69**. The first screen of act 3 with an HP line printed
**`HP 69/69`** — a **54 HP** full heal, arriving across the same boundary that
granted 31 HP last act, with the intervening screens being one map, one event and
one `Proceed`. (Act-2 finding 1, reproduced.)

Two other things the first battle screen settled that no earlier screen had:

- **`Droplet of Precognition` finally has a description**: `Choose a card in your
  Draw Pile and add it into your Hand.` The second seat carried it for a whole act
  and wrote "no screen has ever said what it does" — the potion block on a
  **battle** screen is where it says so.
- **The deck is 32 cards** (`26 in the draw pile` + 6 in hand). The second seat
  reconstructed 33. Nothing on any screen accounts for the difference, and the
  candidate is fight 9's stolen-and-returned card, which no screen ever named.
  Also: **`Mind Rot` and `Sloth` are gone** — the boss's status cards did not
  persist.

Enemy opened at `153/162`: `Festive Popper` for its full 9.

**Round 1 — `Intent: Empower (Buff)`, a free turn.** Hand: Fish-Flavored Bait+,
Nicole, Yumemizuki Mizuki, Kaboom!, Chain Fuse, Sparks 'n' Splash+.

Played **Fish-Flavored Bait+** (1) → 7 damage, `Bomb 6`; **Chain Fuse** (1) →
`Bomb 12`; **Sparks 'n' Splash+** (1). I passed on `Kaboom!` (10 damage once) for
`Chain Fuse` (+6 to the stack, which the Splash then pays *every* turn) and on
`Nicole` because the engine card matters more in the first turn of a 162 HP fight
than 2 Strength a turn.

Predicted `153 → 146` and `Bomb 12`. Both exact. End of turn the Splash paid 12:
**`146 → 134`**.

**A Razor Tooth reading.** The tool's echo line said `Playing 'Chain Fuse+'` — the
relic had upgraded the card — but the bomb went to exactly **12** (6 + 6), the
base number. Same on round 2: the echo said `Playing 'Strike+'` and the damage was
**9**, the unupgraded face. **`Razor Tooth` upgrades the card *after* it resolves,
and the echo line names the post-upgrade card**, which reads as though the current
play was upgraded when it was not.

**Round 2 — the enemy prints its clock.**

```
- Ritual 9 (buff) — At the end of its turn, gains 9 Strength.
- Intent: Aggressive — the number on its icon is 12
```

That is +9 damage a round, forever: 12, 21, 30, 39, 48. There is no threshold and
no brake — the only answer is to end the fight.

Played **Pop!** (0) → 2 bombs, **Explosives Workshop** (1), **Strike** (1),
**Strike** (1). I deliberately did **not** play `Run Away!+` (0 energy, printing
`Gain 14 Block` because Vambrace was unspent): incoming was 12, `Sai` covers 7,
so the card would have spent Vambrace's doubling to save **5 HP** at full health,
where a later doubled `Dig In` or `Sorry, Jean...` saves far more.

Predicted `134 − 18 = 116`, stack `21`, Splash 21 → **95**, and 12 − 7 = 5 taken.
**All exact: `HP 95/162`, `HP 64/69`.**

The stack arithmetic also re-confirmed act-2 finding 12: `Bomb 16` on one bomb
became `Bomb 21` after adding a `Bomb 5`, then next turn `Bomb 31` — **+5 per
bomb** with one `Explosives Workshop` down, i.e. growth is per bomb, not per
stack.

**Round 3 — five cards, three energy, six bombs.** `Bomb 31`, enemy 95, incoming
21, me at 64.

Played **Pop!** (0) → 36, **Powder Charge** (0 Energy, 1 Spark) → 42,
**Jumpy Dumpty** (1) → 50, **Mine Toss+** (1) → 57, **Defend** (1) → `Block 12`,
Vambrace spent, total `Block 19`.

`Mine Toss+` was the interesting one. Against an *attacking* enemy a Mine is
**paid twice**: the Splash pays it as part of the stack at the end of my turn, and
then it goes off again on its own when the enemy attacks. The second seat recorded
`Mine Toss+` as "anti-synergy with the Splash against an attacking boss" because
the Mine leaves the stack; against a short fight it is 14 damage for 1 energy.

Predicted: `Bomb 57` (`Bombs here: 6, including 1 Mine`), Splash 57 → **38**, then
the Mine 7 before the hit → **31**, and 21 − 19 = 2 taken → **62/69**.

**Every number exact**, including `Spark 0 → 1` from `Pounding Surprise` when the
Mine went off.

**Round 4.** `Bomb 75` across 5 bombs (50 + 5×5), enemy at 31, its intent now
**30** (`Strength 18`). The end-of-turn Splash of 75 kills it before it swings, so
the turn was pure insurance: `Dig In` (1 Spark, **0 Energy**, 9 Block), `Defend`
(6), `Duck and Cover` (6) → 28 Block against 30, in case the Splash somehow did
not resolve first.

**It resolved first. Fight 12 won at 62/69 — 7 damage across four rounds** against
an enemy that would have been hitting for 39 on round 5 and 48 on round 6.

### Fight 12 reward

`14 Gold` (→ **256**), **`Energy Potion`** (claimed — 2 slots were free), and:

```
- Ammo Scavenging — cost 1, skill — Place a Bomb 4. Draw 1 card for each of your Bombs that went off this turn.
- Explosives Workshop — cost 1, power — At the start of your turn, your Bombs grow by 1 more.
- Bang Bang! [Pyro] — cost 2 Sparks, attack — Set off. Deal 8 damage. Place a Bomb 4.
- Mika — Starfrost Swirl [Cryo] — cost 1, attack — Deal 5 damage to ALL enemies. Your next Attack costs 1 less.
```

**Took the third `Explosives Workshop`.** Two copies already print
`Explosives Workshop 2 — your Bombs grow by 2 more`, and this fight measured the
first copy as **+1 per bomb per turn**; with five or six bombs on the board a third
copy is +5 or +6 a turn, collected by the Splash every single turn.

`Ammo Scavenging` and `Bang Bang!` both pay only when Bombs **go off**, which in
Splash mode is almost never — the same reason both previous seats refused every
detonator on offer. `Mika` was the real competitor: a second **Cryo** source, and
`Melt` (1.75x) on a Splash multiplies the *whole* stack (act-2 finding 3). I
passed because I already hold the two cards that combo needs —
`Barbara — Melody Loop`, whose Hydro strips my own Pyro aura at the *start* of my
turn (act-2 finding 2), and `Rosaria`, whose Cryo can then land on a bare enemy —
so Mika would be a third piece of a two-piece combo.

### Unknown (floor 3) — "Reflections snoitcelfeR"

```
- Touch a Mirror   Downgrade 2 random cards. Upgrade 4 random cards.
- Shatter          Duplicate your Deck. Receive Bad Luck.
```

**No way to decline** — two rows, both forced, no "leave". (Act 2's potion event was
the same shape; every other event in three acts offered a way out.)

**Chose Touch a Mirror**, for net +2 upgrades on a 32-card deck against
`Shatter`'s 64-card deck containing two `Spoils Map`s, eight Strikes, eight
Defends and an unnamed curse called `Bad Luck`.

**The screen never said which six cards it touched.** I had to reconstruct it from
battle screens over the next two fights:

- **Downgraded:** `Sparks 'n' Splash+` → **`Sparks 'n' Splash` (cost 2 again)`**,
  and `Run Away!+` → **`Run Away!` (`Gain 3 Block`)**. Those are the two cards the
  first and second seats spent an event and a shop trip upgrading.
- **Upgraded:** `Explosives Workshop+` (*grow by 2 more*), `Strike+` (12 damage),
  `Powder Charge+` (*Place a Bomb 9*), `Jumpy Dumpty+` (*Bomb 11, Mine 4*).

Net it was a clear win, but **the downgrade hit the single most important card in
the deck and no screen told me** — I found out when `Sparks 'n' Splash` turned up
in an opening hand two floors later printing `cost 2, power`.

### Fight 13 — three Scrolls of Biting (35 / 34 / 36), entered at 62/69

All three opened at −9 (`26/35`, `25/34`, `27/36`) — `Festive Popper` in full.

```
Paper Cuts 2 (buff) — Whenever Scroll of Biting deals unblocked attack damage
                      to you, you lose 2 Max HP.
```

**That is a permanent cost for taking a hit**, which changes the price of a bad
turn completely, and I had **no Block card in hand** against `5x2` + `14` = 24
incoming with only `Sai`'s 7.

**Round 1 — the one turn all act where killing beat building.** Ordered for
margins:

- `Pop!` (0) and `Pop!` (0) on Scroll (3) → `Bomb 10`
- **`Ka-pow!`** (0) → Set off 10 + its own 4 = 14 → Scroll (3) `27 → 13`
- **`Yumemizuki Mizuki`** (2) — at 89.9% HP it took the `18 damage to ALL enemies`
  branch → Scroll (3) **dead**, Scroll (1) `26 → 8`, Scroll (2) `25 → 7`
- `Strike` (1) → 9 into Scroll (1)'s 8 → **dead**

Predicted both kills with margin (18 vs 13, 9 vs 8) rather than taking the
tighter ordering that would have needed 9 into exactly 9. **Both landed.**
`Spark 1 → 3` — `Pounding Surprise` paying once per bomb, not once per Set off.

Also observed: **`Swirl` did something.** `Yumemizuki`'s `Swirl ALL enemies`
consumed the `Pyro Aura` my Set off had left on Scroll (3) and printed
`Pyro Aura 2` on **both survivors**. The card's own text says "No aura, no
effect", so its damage half and its Swirl half both paid.

**Round 2.** One Scroll left at 7 HP with `7x2` pointed at me. **`Rosaria`** (1) —
her face had rewritten itself with `*Reaction preview: Melt*` because she supplies
Cryo into that Swirled Pyro aura — killed it outright (9 x 1.75 ≈ 15 into 7).

**Result: fight 13 won at 62/69, two rounds, ZERO damage taken and zero Max HP
lost.** This is the fight `Yumemizuki` was bought for in act 2 and it paid exactly
as reasoned.

### Fight 13 reward

`12 Gold` (→ **268**) and:

```
- Chain Fuse+ (upgraded) — cost 1, skill — Each Bomb on the enemy grows by 9.
- Sorry, Jean... — cost 0, skill — Remove one of your Bombs. Gain Block equal to its size.
- Dig In+ (upgraded) — cost 1 Spark, skill — Gain 11 Block.
- Sayu — Muji-Muji Daruma — cost 1, skill — For 2 turns, at the end of your turn deal 6 damage to a random enemy if you are above 70% HP, otherwise gain 6 Block. Exhaust.
```

**Took `Chain Fuse+`.** Growth is **per bomb** (act-2 finding 12, re-measured this
act), so `Each Bomb grows by 9` is +9 × the number of bombs, and the Splash then
pays that total **every turn**. On the five- and six-bomb boards this deck reaches
that is +45 or +54 a turn for one energy. Fight 14 measured it at **+18 on two
bombs** — exactly 9 each.

### Fight 14 — Frog Knight (HP 191), entered at 62/69

The opening screen printed `HP 191/191, Block 6` — **and that is `Festive Popper`
firing into Block, not failing.** `Plating 15` gives the Frog Knight 15 Block, the
relic's 9 was absorbed, and `15 − 9 = 6`. **This is very likely what act 1's
finding 5 actually was** (three Inklets taking "1 damage instead of 9"): the relic
hit block, not HP, and no screen prints an enemy's starting block before the
relic resolves.

```
Plating 15 (buff) — At the end of your turn, gain 15 Block.
                    Plating is reduced by 1 at the start of your turn.
```

So the Frog Knight's effective HP is 191 **plus 15, 14, 13 … every round** — a
regenerating wall, and the second wall-enemy in two acts after the Tunneler.

**Round 1.** I opened with **`Barbara — Melody Loop`** (1) — the card act 2's
record called dead — on a deliberate reading of act-2 finding 2. Barbara's Hydro
is eaten by my own Pyro aura *when one is up*; the Frog Knight was **bare**
(Popper leaves no aura, and I had played no Pyro card). So on each of the next
three turns Barbara would apply Hydro at the **start** of my turn, and the
`Sparks 'n' Splash` fires at the **end** of it — a Pyro hit into a Hydro aura,
which is **Vaporize, 1.5x, on the whole stack**. Then plus `Strike+` (12) and
`Strike` (9) into `Block 6` → `191 → 176`, exact, and `Block 17` against 13 → 0
taken.

**Round 2.** `Frail 2` landed (`Gain 25% less Block from cards`), the Hydro was up,
and my hand held **no Splash**. Played `Pop!` (0), **`Powder Charge+`** (0 Energy,
1 Spark) → `Bomb 14`, `Nicole` (2) and a `Defend` (1, 4 Block under Frail).
Predicted 21 − 11 = 10 taken → **52/69**. Exact.

**Round 3 — the potion that fixed the deck's oldest complaint.** Free turn
(`Empower`), `Bomb 22`, Hydro up, one Melody Loop application left — and still no
Splash in hand, in a deck where both previous seats' single loudest complaint was
"the engine card arrives on round 4 or 5".

**`Droplet of Precognition`** — `Choose a card in your Draw Pile and add it into
your Hand` — fetched **`Sparks 'n' Splash+`** straight out of the 16-card draw
pile. That is a tutor for the engine card, and it is the answer to both earlier
records' complaint.

The draw-pile screen it opened is also a clean control for act-1 finding 1:
**every card there printed its BASE face** — `Defend — Gain 5 Block`,
`Strike — Deal 6 damage` — while the *same cards in hand* printed 4 and 13 the
same second, with Dexterity, Frail, Strike Dummy and Strength folded in.

Played `Chain Fuse+` (1) → `Bomb 40` (22 + 9 + 9, exact), `Sparks 'n' Splash+`
(1), `Run Away!` (0, purely to bank its `Razor Tooth` upgrade).

**Predicted the Splash at 40 x 1.5 = 60, less `Block 14` = 46.**
**Observed: `176 → 127`, i.e. 49.** The 3 I was missing is my `Strength 2`,
multiplied: **(40 bombs + 2 Strength) x 1.5 = 63, − 14 Block = 49.**

That single number settles two open questions from the earlier records at once:
the Splash adds my Strength **before** the reaction multiplier, and an Elemental
Reaction multiplies the **entire** Splash (act-2 finding 3, which was inferred
there and is measured here).

**Round 4 — the last Vaporize.** `Bomb 48`, Melody Loop expired but its final
Hydro still on the body, enemy `127` behind `Block 13`, `Strength 4` on me.

I deliberately did **not** play `Fish-Flavored Bait+` even though it adds a
`Bomb 6` and 11 damage: it is **[Pyro]**, so it would have consumed the Hydro
before the Splash could use it, trading a 1.5x on ~63 for a 1.5x on 11.

Played `Jumpy Dumpty+` (1) → `Bomb 59`, **`Strike`** (1) → exactly 13 into exactly
`Block 13`, stripping it, and `Explosives Workshop+` (1). Stripping the block was
worth 13 damage; the third Workshop would have been worth about 3.

**Predicted `(59 + 4) x 1.5 = 94`, none of it blocked → `127 → 33`.**
**Observed `HP 33/191`.** Exact. Took 18 − 12 = 6 → **46/69**.

**Round 5.** `Bomb 77` (59 + 3 bombs x 6, exact) against 33 HP behind `Block 12`.
Added a `Pop!` and ended: the end-of-turn Splash paid `(82 + 6) − 12` and the Frog
Knight died **before its printed `26` landed**.

**Result: fight 14 won at 46/69** — 16 damage across five rounds against a 191 HP
enemy that regenerated 12–15 Block every round.

### Fight 14 reward

`16 Gold` (→ **284**) and:

```
- Sorry, Jean...+ (upgraded) — cost 0, skill — Retain. Remove one of your Bombs. Gain Block equal to its size.
- Witches' Circle+ (upgraded) — cost 1, power — Whenever you play a Hexerei card, place a Bomb 5 on a random enemy.
- Fish-Flavored Bait+ (upgraded) [Pyro] — cost 1, attack — Deal 7 damage. Place a Bomb 6.
- Diona — Shaken, Not Purred [Cryo] — cost 1, skill — Gain 6 Block. Apply Cryo twice. If a Bomb goes off this turn, gain 5 Block.
```

**Took `Diona`, for one word on its face: "twice".** The whole difficulty with
reacting off the Splash is that the Splash itself repaints the enemy Pyro at the
end of every turn, so at the start of my turn the enemy always wears **my own**
element and a single Cryo card only strips it. `Apply Cryo **twice**` should strip
the Pyro with the first application and then paint Cryo with the second, leaving
the enemy wearing Cryo when the Splash lands — **`Melt`, 1.75x, on the whole
stack**, which is the largest multiplier on the glossary. Fight 14 measured a
1.5x Vaporize at +21 damage on a 63-point Splash; the same board at 1.75x is +47.
It is also a Skill, so it does not paint Pyro itself, and it pays 6–11 Block.

`Witches' Circle+` needs `Hexerei` cards, and this screen is the first that
explains what Hexerei is (`A Companion card from the witches' circle … Klee is one
too`) — but **no companion card in my deck prints the Hexerei tag on its face**,
so I still cannot tell whether my four companions would trigger it. Both earlier
seats refused it for the same unreadability.

### Unknown (floor 5) — "Relic Trader"

```
- Take the Top One      Trade Strike Dummy for Blood Vial.
- Take the Middle One   Trade Razor Tooth for Venerable Tea Set.
- Take the Bottom One   Trade Festive Popper for Gremlin Horn.
```

**Again no way to decline** — three rows, all trades. And **none of the three
relics I would receive was described**: three names and nothing else, against
three relics whose text I can read. That is a blind trade by construction.

**Traded `Strike Dummy` for `Blood Vial`.** `Strike Dummy` (+3 on cards containing
"Strike") is my cheapest relic to lose — the Splash does the damage and Strikes
are the deck's worst card — and I kept `Razor Tooth` (which upgrades every Attack
and Skill I play for the rest of a combat, and had just turned `Run Away!` into
`Run Away!+` mid-fight) and `Festive Popper`. **The consequence was immediate and
unannounced: every `Strike` in the deck silently went back from 9 damage to 6.**

### RestSite (floor 6) — Smith

`HP 46/69`. **Chose Smith over Rest**, because floor 14 ahead is `RestSite,
RestSite, RestSite, RestSite` — a *guaranteed* rest before the boss — and the next
room was a free Treasure. Upgraded **`Sparks 'n' Splash`, cost 2 → 1**, undoing
exactly the downgrade the Mirror had taken. **Both copies are cost 1 again.**

*Tool honesty note, not a defect:* the smith list flagged
`Barbara — Melody Loop+ — on the screen's list nowhere, and nothing on the feed
says why`, and its own footer explains it — the list is "your deck as it stood in
the last fight (floor 38)", and **in that fight `Razor Tooth` had upgraded Barbara
temporarily**. The snapshot carries in-combat upgrades that no longer exist.

### Treasure (floor 7)

`Centennial Puzzle — The first time you lose HP each combat, draw 3 cards.` Taken.

### Shop (floor 8) — and 744 gold that no screen ever printed

The shop opened with **`You have 1028 gold.`** My tally of every printed reward is
**284**: 242 carried from act 2, `+14` (fight 12), `+12` (fight 13), `+16`
(fight 14). **744 gold arrived without any screen saying so** — larger than act
1's ~149, and it is not the `Spoils Map`'s promised 600 either (that would make
884). See findings.

Bought, from 1028:

- **`Card Removal`** (100) — see below.
- **`Grounded`** (37) — `At the start of your turn, if none of your Bombs went off
  last turn, gain 6 Block and 1 Spark.` **In Splash mode my Bombs never go off**,
  so this is an unconditional 6 Block *and* 1 Spark every turn for one energy —
  and the Spark half fixes the constraint the second seat named exactly ("in
  Splash mode the Spark bank is one per combat, full stop"), which is what gates
  `Powder Charge+` and `Dig In`. The cheapest card on the shelf was the best one.
- **`Miniature Tent`** (185) — `You may choose any number of options at Rest
  Sites.` With four RestSites on floor 14 and more before it, this converts every
  remaining rest into a rest **and** an upgrade. It paid on the very next floor.
- **`Whetstone`** (183) — `Upon pickup, Upgrade 2 random Attacks.` A relic, so no
  deck dilution, and the roll was excellent: it produced **`Ka-pow!+`** and
  **`The Big One+`, whose cost went 3 → 2** — the two attacks I actually want.
- **`Swift Potion`** (49, draw 3) and **`Power Potion`** (49) to refill the two
  free potion slots.

**Refused `Careful Arrangement` (72) for the fourth time in three acts** — growth
is per bomb, so merging N bombs into one is a cut of (N−1)/N to the engine — and
refused all three detonators on the shelf (`Tinder Toss` 51, `Sizzle` 49,
`Quick Fuse` 50) for the reason both earlier seats did: `Set off` spends the stack
that the Splash pays out of every turn. Refused `Albedo — Solar Isotoma` (154,
8 damage + 4 Block a turn) purely on deck size — at 35 cards, dilution was costing
me more than 8 damage a turn was worth. Refused `Kaeya` (72) because his Cryo
lands at the **end** of my turn, colliding with the Splash's own timing.

**The Card Removal could not remove `Spoils Map`.** The removal screen listed
**25 cards** out of a 35-card deck and `Spoils Map` was not among them — the
screen's own footer says the list is the deck "as it stood in the last fight",
and `Spoils Map` had not been drawn in that fight. **The one card in the deck that
can never be played is the one card the removal screen would not offer me.** I
removed a `Strike` instead (worth 6 damage now that `Strike Dummy` is traded away).

### RestSite (floor 9) — Rest *and* Smith

`Miniature Tent` paid at once: **Rest 46 → 66/69, and then the Smith screen was
still on offer.**

Used the preview to shop for a cost reduction rather than a bigger number — the
screen shows the upgraded face before you confirm and lets you `skip` back — and
found **`Nicole — Revelation, Uncreated Light+`, cost 2 → 1**, same text. Both
earlier seats' complaint about Nicole was never her effect, it was that a 2-cost
power keeps losing the energy contest; this is that complaint's fix.

### ELITE (floor 10) — Flail Knight 101 / Spectral Knight 93 / Magi Knight 82, entered at 66/69

The battle screen opened at **`HP 68/69`** — **`Blood Vial` heals 2 at the start of
combat**, which is the first time any screen said what the relic the Trader gave me
does. All three knights opened at −9 (`92/101`, `84/93`, `73/82`).

**Each of the three knights taxes a different part of the character, and two of the
three taxes are only readable after you have paid them.**

```
Hex 2 (debuff)    — While Spectral Knight is alive, ALL your cards are Ethereal.
Dampen 1 (debuff) — While Magi Knight is alive, ALL your cards are Downgraded.
```

`Hex` is the harshest thing either earlier act showed: **every card you do not play
this turn is Exhausted**, in a deck built on playing five cheap cards a turn and
banking the rest. `Dampen` silently un-upgraded everything — `Sparks 'n' Splash+`
went back to cost 2, `Chain Fuse+` back to +6, `Powder Charge+` back to `Bomb 6`
— i.e. it undid every upgrade this act bought, for as long as one enemy lived.

**Round 1.** `Pop!` (0) and `Jumpy Dumpty+` (1) on the Flail Knight → `Bomb 16`,
`Sparks 'n' Splash+` (1), `Duck and Cover` (1, Vambrace → 12). Predicted 21 − 19 =
2 taken → **66/69**, and the Splash for 16 → `92 → 76`. Both exact.

**Round 2 — the combo the `Diona` pick was made for, and it worked exactly as
read.** Nine cards in hand (the 2 damage had triggered `Centennial Puzzle`'s
3-card draw), 3 energy, and everything I did not play would Exhaust. Incoming 33
at 66 HP.

Diona's own card face is what makes the line readable, and it is the single best
piece of rules text in three acts:

```
*Reaction preview: Melt* — This card deals no damage. Pyro plus Cryo is still
consumed, and there is no hit here for the 1.75x to multiply.
```

That sentence tells you the thing the glossary does not: an aura application with
no damage attached is a **stripper**, not a hit. Played in order:

- **`Rosaria`** (1) — Cryo into the Flail Knight's Pyro aura → `Melt` on her own
  9 → **15**, `76 → 61`, aura consumed, body left bare, **and `Vulnerable 1`
  applied** because it had an aura at the moment she hit.
- **`Diona`** (1) — `Apply Cryo twice` onto the now-bare body → `Cryo Aura 2`, plus
  7 Block.
- **`Pop!`** (0) → third bomb.
- **`Defend`** (1) → `Block 20` total.

The badge then printed the whole chain in one line:
**`Bomb 42 (buff) — Set off here deals 42 Pyro damage after Vulnerable. Bombs
here: 3`** on a raw stack of 29 — and 42 is not 29 x 1.5 = 43. **Vulnerable is
applied per bomb and floored per bomb**: 15→22, 9→13, 5→7 = **42**.

**Predicted: the end-of-turn Splash pays the badge's 42, Melts on the Cryo aura
for 1.75x = 73, and kills a 61 HP Flail Knight before its `9x2` lands, so I take
only the Spectral Knight's 15 into 20 Block = 0.**

**Observed: the Flail Knight dead, `HP 66/69` unchanged.** Two multipliers on one
Splash — Vulnerable on the target and a Melt off an aura I painted myself — turned
a 29-point bomb stack into a 73-point hit.

**And then the screen showed something no text anywhere describes.** The Flail
Knight had died holding three bombs. The next screen printed:

```
- Spectral Knight — HP 84/93   Bomb 32 … Bombs here: 2
- Magi Knight    — HP 73/82   Bomb 9  … Bombs here: 1
```

**The dead enemy's three bombs moved onto the two survivors**, individually
(19 + 13 = 32 on one, 9 on the other, each having grown 4). **Bombs are not lost
when their host dies; they are redistributed.** This is almost certainly what
act 1's finding 3 was — "one Jumpy Dumpty put two Mine 3s on one enemy" after a
second enemy died in the same Set off. Nothing on any card, badge or glossary
entry says this happens.

**Round 3.** Now **two** enemies carried bombs, which is the case the second seat
could not test: the Splash reads `a random enemy equal to the Bombs on it`. I
concentrated instead of spreading — `Powder Charge` (1 Spark, 0 Energy) and
`Chain Fuse` (1) both onto the Spectral Knight → `Bomb 56` there against `Bomb 13`
on the Magi Knight — and blocked to 22 with `Dig In` (1 Spark, 0 Energy) and a
`Defend`, plus played **`Grounded`** (1).

`Grounded` is the shop card of the act: `if none of your Bombs went off last turn,
gain 6 Block and 1 Spark`. **In Splash mode no Bomb ever goes off**, so it is
unconditional, and its Spark half is what pays for `Powder Charge` and `Dig In` on
later turns — the second seat's "in Splash mode the bank is one Spark per combat"
constraint, removed.

Took **0**. The Splash rolled the Spectral Knight: `84 → 28`, i.e. **56, the whole
stack, and the roll went my way**.

**Round 4.** Spectral at 28 with `Bomb 68`; Magi at 73 with `Bomb 13`. No
detonator in hand and nothing that could deal 28, so I could not choose which
enemy the Splash would pay. Pumped the Magi Knight's single bomb with `Chain Fuse`
(so the bad roll would still be worth something), blocked to 17 against 15, and
ended. **The Splash rolled the Spectral Knight again and killed it** — and its
**three bombs migrated onto the Magi Knight**, which came up the next screen at
`Bomb 103, Bombs here: 4`.

**Round 5.** `Bomb 103` on a 73 HP Magi Knight with `Block 5` and a **35** damage
intent. **`Ka-pow!` (0 Energy) set it off and ended the fight on the spot** — the
retained free detonator as finisher, which is the second seat's own conclusion.

**Result: ELITE killed at 66/69, having taken 2 damage across five rounds.**

### Elite reward — White Star pays a second time

`42 Gold` (→ **467**), the relic **`Pendulum`** (named, never described), a
`Power Potion` I could not claim (3/3 slots), and **two** card rewards.

Skipped the first list entirely (`Perfect Timing+`, `Coven Errand`, `Flame Dance`,
`Dahlia`) — two of the four begin `Set off`. From the rare list
(`Alice's Introduction Magic`, `Chained Reactions`, `Sparks 'n' Splash`, `Varka`)
I took the **third `Sparks 'n' Splash`**, knowing from act-2 finding 9 that extra
copies do **not** increase the payment: this is bought purely as draw insurance,
because the one thing that decides every fight is what turn the engine lands.

### Shop (floor 11) — `Orrery`, and the removal screen's blind spot

467 gold. Bought **`Orrery`** (181) — `Upon pickup, gain 5 card rewards` — which
is five separate three-card choices, each skippable, for one relic slot and no
deck dilution unless I accept. Twelve of the fifteen cards on offer were
detonators, `Careful Arrangement`, or duplicates; I took two:

- **`Explosives Workshop+`** (a fourth Workshop, `grow by 2 more`) — growth is per
  bomb per turn and the Splash collects it every turn, so on a six-bomb boss board
  this is +12 a turn compounding.
- **`Sorry, Jean...`** (a second copy) — `cost 0 — Remove one of your Bombs. Gain
  Block equal to its size`, the only card in the deck that converts the engine into
  survival and scales with it.

Then bought **`Card Removal` (125)** — and **the removal screen again would not
offer `Spoils Map`**. Its list is capped at **25 entries** out of a 38-card deck
both times I paid for it, and the one permanently unplayable card in the deck was
outside the cap on both occasions. I removed a second `Strike` instead.

Refused `Gorget` (186, 4 Plating) and `Bronze Scales` (200, 3 Thorns) as small
next to 18 Block a turn from `Sai` + `Grounded` + `Nicole+`, and could not buy
`Potion of Binding` (76, `Apply 1 Weak and 1 Vulnerable to ALL enemies` — which
after this Elite I know multiplies the whole bomb stack) because my potion slots
were full.

### Unknown (floor 12) — "Symbiote"

```
- Approach        Enchant an Attack with Corrupted.
- Kill with Fire  Choose a card to Transform.
```

**A third event in a row with no way to decline.** Took `Kill with Fire`
specifically to transform `Spoils Map` — **and its list, capped at 25 entries
again, did not contain `Spoils Map`.** Three separate screens in three floors
(two Card Removals and this Transform) offered to change a card in my deck and
**none of the three would show me the one card that cannot be played.**

Transformed a `Defend` instead. **The screen never said what it became**; I found
out at the next Smith that it is `Bully — cost 0, attack — Deal 4 damage. Deals 2
additional damage for each Vulnerable on the enemy.`

### RestSite (floor 14) — Rest *and* Smith again

`66/69` → **69/69**, and `Miniature Tent` left the Smith on offer as well.
Upgraded **`Chain Fuse` → `Chain Fuse+`** (each Bomb grows by 6 → **9**), which on
the four- and five-bomb boards this deck reaches is +36 to +45 to the stack for
one energy, collected by the Splash every turn thereafter.

The Smith list is where I first read `Bully`, and where the page's own
"not on this list, and why" block named **fifteen** cards as missing —
`Ka-pow!+`, `Strike+`, `Chain Fuse+`, `Sparks 'n' Splash+`, `Nicole+`, `Pop!+`,
`Duck and Cover+` and others. **`Spoils Map` was in neither the list nor the
exceptions.** It is invisible to every deck-editing screen in the game.

---

## BOSS — Aeonglass (HP 512), entered at 69/69

Opened at `503/512` — `Festive Popper`'s full 9. **512 HP is more than act 2's
379 and double act 1's 252.** Its two printed buffs are both aimed at this
character:

```
Withering Presence 6 (buff) — Every 6 cards you play, add a Wither to your Hand.
Artifact 3 (buff)           — Negates 3 debuffs.
```

`Withering Presence` is the fourth enemy in two acts to charge for Klee's
signature — five cheap cards on three energy — after act 2's `Tender`,
`Vital Spark` and `Sloth`. `Artifact 3` pre-empts the one debuff route I owned:
`Rosaria`'s Vulnerable, which the Elite had just shown multiplies the whole bomb
stack. **Auras are not debuffs** and `Artifact` never touched them, which is why
the Melt line still worked — but nothing on either screen says so, and I only
learned it by watching `Artifact 3` stay at 3 after a Cryo landed.

Aeonglass alternates **Attack + Defend** with **Attack** and **StatusCard +
Empower**, and the Defend turns are the shape of the fight: it puts up **Block 33**
on its own turn, which sits there through the whole of my next turn, so **every
Defend round taxes my one big hit by 33**.

**Round 1.** `Pop!` (0), `Pop!` (0), `Sparks 'n' Splash+` (1),
`Explosives Workshop` (1). No Block card in hand; I took the hit rather than spend
`Sorry, Jean...` (which would have removed a Bomb 5 that the Splash pays out of
*every* turn for the rest of the fight). Predicted `Bomb 10`, Splash 10 → **493**,
and 22 − 7 = 15 taken → **54/69**. Both exact, and the 15 triggered
`Centennial Puzzle` for 3 extra cards.

**Round 2 — the block tax, measured.** Aeonglass sat behind `Block 33`.
`Dig In` (1 Spark, **0 Energy**) printed **`Gain 18 Block`** — base 8, +1
Dexterity, doubled by `Vambrace` — and with `Sai`'s 7 that was 25 against a 22
intent. Then `Kaboom!` (1) for 7, `Jumpy Dumpty+` (1) for `Bomb 11`, `Defend` (1).

Predicted: Kaboom's 7 eats 7 of the boss's 33 Block; the end-of-turn Splash of 31
then meets Block 26 and puts **5** through; I take 0.
**Observed `493 → 488` and `HP 54/69` unchanged.** Exact — and it is the clearest
statement of the problem: **a 31-point engine turn delivered 5 damage to a 512 HP
boss, because the boss's Block is a flat tax on the one hit the deck makes.**

**Round 3 — the turn the fight was won, and the reason the `Diona` pick mattered.**
Aeonglass's intent was `StatusCard` + `Empower`: no damage, and — crucially —
**no Defend, so it would carry no Block into my next hit**. It was also **bare**:
my own round-2 Splash had left a Pyro aura, which had expired.

Played, on three energy:

- **`Chain Fuse+`** (1) — `Each Bomb on the enemy grows by 9` across three bombs →
  `Bomb 46` became **`Bomb 73`**, exact.
- **`Grounded`** (1) — the 37-gold shop card. `if none of your Bombs went off last
  turn, gain 6 Block and 1 Spark`, which in Splash mode is unconditional.
- **`Diona`** (1) — `Apply Cryo twice` onto a Pyro-aura'd body: the first
  application Melts the Pyro off for no damage, the second paints **`Cryo Aura 2`**.

I deliberately played only three cards, because `Withering Presence` was at 1.

**Predicted: the end-of-turn Splash is a single Pyro hit of 73 into a Cryo aura →
`Melt`, 1.75x → 127, with no Block in the way.**

**Observed: `488 → 361`. Exactly 127.** One card that deals no damage at all
turned a 73-point turn into a 127-point turn.

Also on that screen, unexplained: **`Spark 0 → 4`.** `Grounded` grants 1. The
other 3 arrived with the Melt, on a turn when **no Bomb went off** — the only
candidate is one Spark per bomb for the reaction, which is `Catalytic Converter`'s
printed effect and I do not own `Catalytic Converter`. No screen said anything.

**Round 4 — the same trick, one size larger.** Aeonglass was bare again (the Melt
consumed the Cryo), carried no Block, and had `Bomb 88` on it.

- **`Powder Charge+`** (1 Spark, **0 Energy**) → fourth bomb, `Bomb 97`
- **`Chain Fuse+`** (1) → +9 x 4 = **`Bomb 133`**
- **`Explosives Workshop+`** (1) → `Explosives Workshop 3`, i.e. bombs now grow
  **7 each per turn**
- **`Rosaria`** (1) → 9 damage, and since the body was bare she **painted Cryo**
  rather than reacting

**Predicted 9 + (133 x 1.75 = 232) = 241 with no Block in the way → `361 − 241 =
120`.**
**Observed `HP 120/512`.** Exact.

Two things I got wrong on that turn, both recorded honestly:

- **I took 18 where the screen's arithmetic says 12.** Printed intent **25**,
  `Block 13` (Sai 7 + Grounded 6), `HP 54 → 36`. That implies a hit of **31**, not
  25 — and `Strength 3` was already showing on the boss when the 25 was printed,
  so it is not a Strength fold-in either. **I could not account for 6 damage**, and
  the likeliest candidate is the Status card the boss gave me on round 3, which I
  never located in any pile and which no screen described.
- **`Rosaria`'s Vulnerable never happened**, because her clause is `If the enemy
  has an aura` and the body was bare at the instant she hit. `Artifact 3` stayed at
  3, which is how I know it was never even attempted. The card that is supposed to
  set up the 1.5x is silently mutually exclusive with the state you need it in to
  set up the 1.75x.

**Round 5.** `Bomb 161` across four bombs (133 + 4 x 7, exact) against a boss at
**120** behind `Block 33`. `Pop!` (0) took the stack to **166**, and
**`Ka-pow!+` (0 Energy) Set it off**: 166 − 33 = 133 into 120 HP.

**AEONGLASS KILLED on round 5 at 36/69, for two cards costing zero energy** — and
the whole fight was decided by the two turns the boss did not put up Block.

### Boss reward — and the end of the run

```
# What the fight left behind
- (nothing here to take)
```

**The act-3 boss dropped nothing** — no gold, no relic, no card. `Proceed` led to
an event called **`The Architect`** with a single option, `Respond`, then a single
`Proceed`, and that returned:

```
TOOL-BLOCKED: game_over
the run is over; there is nothing left to play
The run ended on floor 48.
```

**No screen ever said the run was won.** Klee was alive at 36/69 with the act's
boss dead, and the only words the game offered about it were "the run is over".

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

**Diona, and what "twice" is for.** The whole act-3 story is one interaction. The
Splash paints Pyro on the enemy at the end of every turn, so at the start of every
turn the enemy wears *my own element* and a single Cryo card can only strip it. A
card that applies Cryo **twice** strips and then repaints, and the Splash — being a
single hit of the entire stack — then Melts for 1.75x on everything. **Measured
twice, at 73 → 127 and 133 → 232.** Choosing `Diona` over `Sorry, Jean...+`,
`Witches' Circle+` and a second `Fish-Flavored Bait+` was the best call I made, and
it was made entirely off one word on a card face and one sentence of its own
reaction preview.

**Barbara, whom act 2 called dead, on a bare enemy.** The second seat proved that
`Melody Loop`'s Hydro is eaten by my own Pyro aura. That is true *after* the first
Pyro hit — so on the very first turn of a fight, before anything paints Pyro, she
lands clean and then Vaporizes three consecutive Splashes. Fight 14 round 3's
Splash paid `(40 bombs + 2 Strength) x 1.5 = 63`. The card is not dead; it is
**timing-locked to turn 1**, and nothing says so.

**Rest versus Smith versus routing, with `Miniature Tent` collapsing the choice.**
At floor 6 I took Smith over a 20 HP heal at 46/69, on the printed fact that
floor 14 was `RestSite, RestSite, RestSite, RestSite` — a guaranteed rest before
the boss. Buying `Miniature Tent` at floor 8 then removed the dilemma entirely for
the two rest sites that followed: rest **and** smith, both times.

**Routing into the Elite, and refusing one before it.** At 46/69 I skipped the
first Elite for a rest and a shop, then took the second at 66/69 and left it at
66/69. Act 2's Elite cost 39 HP from a full bar; this one cost **2**, and the
difference is `Sai` plus `Grounded` plus `Nicole+` giving 18 Block a turn for no
cards at all.

**Which enemy to point the stack at when two have bombs.** The Elite forced the
case act 2 could not test: `a random enemy equal to the Bombs on it`, with bombs
on two bodies. I concentrated everything on one and accepted a coin flip rather
than spreading and guaranteeing a small payout — it paid twice running.

**Whether to cash `The Big One+` at the boss.** `Bomb 31` x 4 = 124 into a 33-Block
boss on round 2 was 91 damage in one card, and I refused it for the same reason
the second seat did: `Ka-pow!+` retains and sets off the whole stack for **zero
energy**, so the finisher was already free and the stack was worth more growing.
It grew 31 → 46 → 73 → 133 → 166 and `Ka-pow!+` cashed it four rounds later.

### (b) What felt automatic, and what never seemed worth playing

**`Pop!` is still automatic in the good way** — 0 cost, always right. `Powder
Charge+` likewise once `Grounded` was making a Spark a turn.

**Strike and Defend are worse than in either earlier act, and the game did it to
me twice.** Trading `Strike Dummy` away silently dropped every `Strike` from 9
back to 6, and by the boss I had `Sai` 7 + `Grounded` 6 + `Nicole+` 5 = **18 Block
a turn for no cards**, which makes a 6-Block `Defend` a rounding error. I paid 225
gold across two shops to remove two Strikes and would have removed more.

**Never worth playing:** every `Set off` card except the two free ones — I refused
`Tinder Toss`, `Sizzle` x2, `Quick Fuse` x2, `Fwoosh!` x2, `Rapid Fire`,
`Perfect Timing+`, `Flame Dance` and `Bang Bang!` across three shops, five Orrery
rolls and four reward screens, all for the same reason. **`Careful Arrangement`
was offered a fourth and fifth time** and is still a three-quarters cut to the
engine dressed as consolidation. `Mine Toss+` I deliberately never played at the
boss, because a Mine going off would have switched `Grounded` off.

**`Spoils Map`, for the third act running**, and now with the full receipt: its
600 gold never appeared in the act it named or in the one after, and **no
deck-editing screen in the game will show it to you.**

### (c) What I could not understand, or that contradicted its own printed text

- **744 gold that no screen printed** (finding 2).
- **`Spark 0 → 4` on the first Melt turn**, with no Bomb going off and no
  `Catalytic Converter` in the deck.
- **31 damage from a printed `25`** at the boss, with `Block 13` and no debuff on
  me that any screen showed.
- **The card-selection screens cap at 25 entries**, and the cap is not disclosed on
  the screen — only inferable by counting.
- **`Touch a Mirror` and `Kill with Fire` never named a single card they changed.**
  Six cards were re-written by the Mirror and I reconstructed all six from combat
  screens over the following two fights; the Transform's output I learned two
  floors later at a Smith.
- **What `Corrupted` is** (the Symbiote's other option), what `Wither` does (the
  boss's own printed threat, which I triggered at least twice and never located),
  and what the boss's Status card was.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted: `Spoils Map`**, which is now a three-act joke, and — new this act —
**the third `Sparks 'n' Splash`**, which I bought knowing from act-2 finding 9 that
extra copies add nothing to the payment, purely as draw insurance, and which is a
dead 2-cost card every time it arrives after the first.

**Happiest to draw: `Ka-pow!+`.** `cost 0, Retain, Set off` ended the Elite on
round 5 (103 into a 73 HP Magi Knight) and ended the boss on round 5 (166 into a
120 HP Aeonglass behind 33 Block), both for **zero energy**, both on turns where
the alternative was another round of taking damage. The runner-up is not a card at
all: **`Droplet of Precognition`** — `Choose a card in your Draw Pile and add it
into your Hand` — which reached into a 16-card draw pile and pulled
`Sparks 'n' Splash+` on the exact turn I needed it. Both earlier seats' single
loudest complaint is that the engine card arrives on round 4 or 5; that potion is
that complaint's answer, and act 2 carried it for a whole act without any screen
telling it what the potion did.

### (e) Did the previous seats' sharpest findings hold up

- **Act-1 finding 1 (printed numbers silently fold in buffs, with no marker):
  held, and act 3 produced the clean control.** The `Droplet of Precognition`
  screen prints the **draw pile**, and there every card showed its **base** face —
  `Defend — Gain 5 Block`, `Strike — Deal 6 damage` — while the same two cards in
  hand at that same instant printed 4 and 13. Same deck, same second, two different
  numbers, and nothing distinguishes them.
- **Act-1 finding 2 (Vambrace makes every Block card print its doubled value):
  held.** And act 3 gives it a sharper edge: `Dig In` printed `Gain 8` on the
  smith list, `Gain 9` in combat, and **`Gain 18`** in the hand where Vambrace was
  unspent.
- **Act-2 finding 1 (a silent full heal at the act boundary): held, larger.**
  Act 2 closed at 15/69; act 3's first battle screen printed **69/69**. That is
  **54 HP** across a map, an event and a `Proceed`.
- **Act-2 finding 3 (a reaction is worth far more on the Splash than on a Set off):
  held, and is now measured rather than inferred.** Three Splashes:
  `(40 + 2) x 1.5 = 63`, `73 x 1.75 = 127`, `133 x 1.75 = 232`. The Splash is one
  hit, so the multiplier takes the whole stack.
- **Act-2 finding 9 (a second `Sparks 'n' Splash` adds nothing): held.** I took a
  third anyway, and only for draw odds.
- **Act-2 finding 11 (Vulnerable on the enemy multiplies bomb damage, and the badge
  says so): held, with a new detail** — it is applied **per bomb and floored per
  bomb**. `Bomb 42 … after Vulnerable` on a raw stack of 29 is not 29 x 1.5 = 43;
  it is 22 + 13 + 7 from bombs of 15, 9 and 5.
- **Act-2 finding 12 (growth is per bomb): held four times over.** One Workshop:
  `Bomb 16 → 21 → 31` (+5 per bomb). Three Workshops: `133 → 161` on four bombs
  (+7 each).
- **Act-1 finding 3 (one Jumpy Dumpty put two Mines on one enemy) — I think I
  found the mechanism**, and it is not the rider firing twice: **bombs migrate off
  a dying enemy onto the survivors** (finding 4).
- **Act-1 finding 5 (`Festive Popper` dealt 1 instead of 9) — I think that is
  explained too.** The Frog Knight opened `HP 191/191, Block 6` with
  `Plating 15`: the relic hit **Block**, not HP, and 15 − 9 = 6. An enemy that
  starts with block eats the relic and no screen ever shows the block before the
  relic resolves.

### (f) Did act 3 ask anything of the deck that acts 1 and 2 did not

**Yes — three things.**

1. **Regenerating and persistent Block, as a flat tax on a deck that makes exactly
   one big hit a turn.** The Frog Knight gained 12–15 Block *every* round
   (`Plating`), and Aeonglass put up **33** on every Defend round. A deck whose
   damage is one number per turn loses the block *once* — which sounds fine until
   the number is 31 and the block is 33 and the turn delivers **5**. This is the
   only thing all act that genuinely threatened to make the engine lose.
2. **Permanent costs for taking a hit.** `Paper Cuts 2` (lose 2 **Max** HP per
   unblocked hit) turns a sloppy turn into a run-long cost, and it arrived in the
   one fight where my opening hand held no Block card at all.
3. **Three simultaneous, stacking taxes on the character's own shape, in one Elite.**
   `Hex` (ALL your cards are Ethereal — play it this turn or lose it), `Dampen`
   (ALL your cards are Downgraded — every upgrade the act had bought, off), and a
   third body to spread damage across. Act 2 charged for "five cards on three
   energy" three separate times; act 3 charged for it **and** for having upgraded
   anything **and** for banking cards, at once, and the counter-play was readable:
   Powers dodge `Hex`'s worst case because they stay on the board once played.

The boss added a fourth, `Withering Presence` (a card added to hand every 6 played)
— which is the same tax again, and the fifth enemy in two acts to levy it.

### (g) Anything a screen granted or changed without saying so

- **54 HP at the act boundary.**
- **744 gold.**
- **Six cards re-written by `Touch a Mirror`, none named** — including the
  downgrade of `Sparks 'n' Splash+` back to cost 2, the single most important card
  in the deck.
- **One card transformed into another, and the result not named.**
- **`Blood Vial`, `Pendulum` and `Centennial Puzzle` were named and never
  described** at the moment I took them; two of the three I learned from a later
  battle screen. `Whetstone`'s "Upgrade 2 random Attacks" **never said which two**
  — I found `Ka-pow!+` and `The Big One+` (cost 3 → 2) on a removal screen.
- **Trading `Strike Dummy` away silently dropped every Strike from 9 to 6.**
- **Bombs migrate off a dead enemy onto the survivors** (finding 4) — no card,
  badge or glossary entry mentions it.
- **3 Spark on a Melt turn with no Bomb going off.**
- **The run ended without a word about whether it was won.**

---

## Findings, ranked by sharpness

**1. The Splash's Melt is the biggest number in the character, it is set up by a
card that deals no damage, and the deck cannot reach it without a card that says
"twice".** Measured three times: `(40 bombs + 2 Strength) x 1.5 = 63` (Vaporize,
fight 14), **`73 x 1.75 = 127`** and **`133 x 1.75 = 232`** (Melt, boss rounds 3
and 4). The reason it is hard to reach is structural and nothing states it: **the
Splash itself repaints the enemy Pyro at the end of every turn**, so at the start
of every turn the enemy wears your own element and one Cryo card only strips it.
`Diona — Shaken, Not Purred` says `Apply Cryo twice`, and its own reaction preview
— `This card deals no damage. Pyro plus Cryo is still consumed, and there is no hit
here for the 1.75x to multiply` — is the only text in the game that tells you an
aura application with no damage is a **stripper**. That sentence is worth more than
any number on any card I saw, and it is on one card.

**2. 744 gold arrived that no screen announced.** Every printed reward totalled
**284** (242 carried in, +14, +12, +16). The shop opened with **`You have 1028
gold`**. This is not the `Spoils Map`'s promised 600 either — 284 + 600 = 884.
Act 1 recorded ~149 unexplained; act 2 traced its gold exactly; act 3's gap is
**five times act 1's**, and it is more than the price of every relic I bought.

**3. Three separate screens offered to change a card in my deck and none of them
would show me the one card that cannot be played.** Two `Card Removal`s (100 and
125 gold) and one event Transform each listed exactly **25 cards** out of a 35- to
38-card deck, and `Spoils Map` was outside the cap all three times — it did not
even appear in the Smith screen's "not on this list, and why" block, which named
fifteen other absentees. `Spoils Map` has now survived three acts as an unplayable,
non-Ethereal, unremovable card that promised 600 gold in "the next Act" and
delivered nothing in two of them. **I paid 225 gold trying to remove it and removed
two Strikes instead.**

**4. Bombs migrate off a dying enemy onto the survivors, and nothing says so.**
Elite round 2: the Flail Knight died holding three bombs; the next screen printed
`Spectral Knight — Bomb 32, Bombs here: 2` and `Magi Knight — Bomb 9, Bombs here:
1`, i.e. the same three bombs (19 + 13 and 9, each grown by 4). It happened again
on round 4 when the Spectral Knight died holding three and the Magi Knight came up
at **`Bomb 103, Bombs here: 4`**. This is a large, load-bearing rule — it means
killing the host does **not** cost you the stack, it decides whether spreading
bombs is a mistake, and **it is almost certainly what act 1's finding 3 was**
(two Mine 3s on one enemy after a second enemy died inside the same Set off). No
card, badge or glossary entry mentions it.

**5. An enemy's Block is a flat tax on the exact shape of damage this deck makes,
and it is the only thing that ever threatened the engine.** Klee's whole output is
**one hit per turn** (the Splash). Boss round 2: bombs 31, boss `Block 33`,
**5 damage delivered**. The Frog Knight regenerated 12–15 Block every single round
via `Plating`. Against Aeonglass the fight was decided entirely by which rounds it
chose to Defend: the two rounds it did not, I did 127 and 241; the two rounds it
did, I did 5 and 0. **A player who does not notice this reads the deck as
inconsistent rather than as taxed**, and no screen frames it.

**6. `Touch a Mirror` re-wrote six cards and named none of them — including
un-upgrading the deck's key card.** `Downgrade 2 random cards. Upgrade 4 random
cards.` I reconstructed all six from combat screens over the next two fights:
**down** `Sparks 'n' Splash+ → Sparks 'n' Splash (cost 2)` and
`Run Away!+ → Run Away!`; **up** `Explosives Workshop+`, `Strike+`,
`Powder Charge+`, `Jumpy Dumpty+`. The downgrade hit the one card an event and a
shop trip in act 2 had been spent upgrading, and I found out when it turned up in
an opening hand two floors later printing `cost 2, power`. **A card-changing effect
that does not name what it changed is unpriceable at the moment you accept it**,
and act 3 has four of them in twelve floors (Mirror, Transform, Whetstone, and the
Relic Trader's three unnamed relics).

**7. Three of act 3's four events had no way to decline.** `Reflections`
(downgrade/duplicate), `The Future of Potions?` in act 2, `Relic Trader` (three
forced trades, **none of the three relics offered described**) and `Symbiote`
(enchant with an unnamed keyword, or transform). Every event in act 1 offered a way
out. **The Relic Trader is the sharpest case**: it prints the full text of the
three relics you would *lose* and only the names of the three you would *gain*.

**8. `Grounded` is the best 37 gold in the run because a whole line of enemy design
is inert against a deck that never detonates.** `At the start of your turn, if none
of your Bombs went off last turn, gain 6 Block and 1 Spark.` In Splash mode **no
Bomb ever goes off**, so the condition is never false: it is an unconditional 6
Block *and* 1 Spark a turn, and its Spark half removes the constraint the second
seat named exactly ("in Splash mode the bank is one Spark per combat"), which is
what gates `Powder Charge+` and `Dig In`. By the boss I was starting every turn
with **13 Block before playing a card** and enough Spark to play two zero-Energy
cards a turn. The same inversion makes `Ammo Scavenging`, `Chained Reactions`,
`Catalytic Converter` and `Run Away!`'s conditional half close to dead. **One
keyword decides whether about a dozen cards are strong or blank, and no screen
groups them.**

**9. The run ended with no statement of whether it was won.** The act-3 boss's
reward screen read `(nothing here to take)` — no gold, no relic, no card, where the
act-1 and act-2 bosses each paid 100 gold and a card. `Proceed` gave an event
called `The Architect` with one option, then `TOOL-BLOCKED: game_over / the run is
over; there is nothing left to play / The run ended on floor 48.` Klee was alive at
**36/69** with the boss dead. **I cannot tell from any screen whether that is a
victory, and there is no difference in what a death would have printed.**

**10. `Razor Tooth` upgrades the card *after* it resolves, but the echo line names
the upgraded card, which reads as though the current play was upgraded.** The tool
printed `Playing 'Chain Fuse+'` and the bomb grew by exactly **6** (the base
number); it printed `Playing 'Strike+'` and the damage was exactly **9** (the base
number). The relic is honest — "for the remainder of combat" — but the only feedback
you get names the *next* copy, not the one you just paid for.

**11. Two of the boss's numbers did not reconcile, and I could not find why.**
Round 4: printed intent **25**, `Block 13`, `HP 54 → 36` — a **31** damage hit, with
`Strength 3` already folded into the printed 25 on the same screen and no debuff on
me. And on round 3, `Spark 0 → 4` where `Grounded` accounts for 1 and **no Bomb went
off**, on the turn a Melt fired. The likeliest candidate for the first is the Status
card Aeonglass gave me on round 3, which no screen described and which I never
located in any pile. **The likeliest candidate for the second is a Spark per bomb
for triggering a reaction, which is `Catalytic Converter`'s printed text and I do
not own `Catalytic Converter`.**

**12. `Rosaria` cannot set up the 1.5x and the 1.75x at the same time, and her own
face hides the conflict.** `Deal 9 damage. If the enemy has an aura, apply 1
Vulnerable.` To paint Cryo for the Splash's Melt she must hit a **bare** body — and
a bare body has no aura, so the Vulnerable clause silently does not fire. At the
boss `Artifact 3` never decremented, which is how I know it was never attempted.
The two best things the card does are **mutually exclusive by construction** and
nothing on it says so.

**13. `Miniature Tent`, `Droplet of Precognition` and `Whetstone` are the three
items that most changed how the act played, and two of the three were unreadable
when acquired.** The Tent turns every remaining rest site into rest **and** smith
(it paid twice, for `Nicole+` at cost 1 and `Chain Fuse+` at +9). The Droplet is a
tutor that answers both earlier seats' single loudest structural complaint. The
Whetstone rolled `Ka-pow!+` and **`The Big One+`, cost 3 → 2**, and **never said
which two attacks it had upgraded** — I found out on a removal screen three floors
later.

**Where I could not tell:** what `Wither` and `Corrupted` do; what the boss's Status
card was; where the 6 extra damage and the 3 extra Spark came from; whether
`Sparks 'n' Splash`'s "random enemy" is uniform over bombed enemies (it went 2-for-2
my way at the Elite, which is one coin landing twice, not a measurement); and
whether the run counts as a win.

---

## Non-blindness declaration

- **Commands run:** only the two permitted forms,
  `GITS_LANE=2 python -m understudy.blindplay observe` and
  `GITS_LANE=2 python -m understudy.blindplay act "<command>"`, from the repo root
  `C:\Users\Monty\Documents\GitHub\GItS`. **No other `understudy` subcommand was
  run at any point** — no `harness`, `session`, `audit`, `notes`, `scenario`,
  `staged_turn`, `soak`, or `embark`. **No `git`.** Several `act` calls were
  chained inside one Bash invocation and some `observe` output was piped through
  `sed` and `grep` to trim it; where I piped a command's own output away I have
  said so above (the one uncertain command at the floor-14 Smith).
- **Tools used:** `Bash` (the two commands above), `Read` (twice), and `Write` /
  `Edit` (this record only). No scratch file was created.
- **Repo files read: exactly two** —
  `review/qa/klee-round-8-2026-09-03/opus-run2-act1.md` and
  `review/qa/klee-round-8-2026-09-03/opus-run2-act2.md`, the two previous seats'
  records, as instructed. No source, YAML, docs, rulings, backlog, register or any
  other file was opened. Everything above comes from screens the tool printed;
  where I state a rule it is either quoted from a screen or explicitly marked as my
  inference.
- **Files written:** this record only —
  `review/qa/klee-round-8-2026-09-03/opus-run2-act3.md`. **No identifiers were
  minted.**
- **Lane:** lane 1 was never touched. The game was never launched, closed,
  restarted or torn down.
- **The lane is left standing exactly where the run ended** — lane 2 returns
  `TOOL-BLOCKED: game_over`, "the run is over; there is nothing left to play", on
  floor 48, with **Aeonglass dead and Klee alive at 36/69**. Nothing is
  half-resolved.

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
