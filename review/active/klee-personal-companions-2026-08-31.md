# Klee's two new Personal Companions — the drafted faces

**Drafted 2026-08-31 on branch `klee-personal-drafts-2026-08-31`, based on main
`9726bea7`. This is the design drafting `EB-251` owes, which is what R234 §5.3
owes under picks `P2` and `P5`.**

**PAPER ONLY.** No card sheet is edited, no register row moves, no code is
written, and no identifier is minted here. The card ids written in §8 are
proposed strings; they mint when the rows land, and the rows land **at the Burst
retirement fold and not before** — that is `EB-251`'s stated gate and R234 `P3`'s
ruled program. The picks below are numbered `K1` to `K6` **inside this document
only**; those labels are handles for a conversation, not register ids, and they
reserve nothing.

Both faces are drafted **4-star**, common and uncommon, because R234 `P5a` leaves
the Rare Personal tier open and bars any Rare Personal design until it is
answered. Nothing here is a Rare, and nothing here assumes one will exist.

---

## 1. The contract these two faces have to satisfy

Five sentences, each one taken from something already ruled or already shipped.
Everything in §4 and §5 is built to satisfy all five at once.

1. **A Personal Companion prints the engine interaction on its own face.** That
   is the derived contract of the companion packet §1.2, and R234 `P2` is a
   Personal-only slice precisely to prove that half. A Personal card whose face
   could be dealt to any character is a Universal card that happens to be
   flagged, and it fails the slice.

2. **It may not print a Spark grant.** The countersigned clause — *"Companion
   cards may not themselves grant signature resources"* — is why Prune's two
   `gain_spark` ops left her face at `EB-219`, and it reaches these two rows the
   same way. **This forbids the most obvious card either of them could have
   been.** A Mondstadt friend who hands Klee a Spark is illegal by law, not by
   taste, and no wording gets round it.

3. **What it *may* print about the Spark economy is the other three verbs:**
   it may **read** the bank (`has_spark`, shipped on `eager_to_help` and
   `patched_dress`), it may **spend** the bank (`spend_spark` at the card's top
   level, shipped on `powder_charge`, `hold_the_line` and `smoke_and_sparks`),
   and it may **feed** the bank *indirectly* by doing something Klee's own kit
   answers — triggering a reaction, or putting Bombs on the board for
   *Pounding Surprise*. Reading and spending are on the card; every grant is on
   Klee's side of the line.

4. **Power tracks rarity, measured against Klee's own sheet.** Answer 4 of the
   verbatim intent, restated as the companion packet §3.2's test: place the card
   in `docs/klee-cards.yaml` at its rarity and ask whether it would be an
   unremarkable member of that band. The Universal tests — reaction fodder, kit
   gap, "slightly better because it is an unlikely find" — **do not apply to
   these two cards** and are not argued below. R234 `P9` says it in one line:
   Personal cards follow character identity, not nation shape.

5. **Every companion upgrades.** The sheet header's own law, standing since the
   2026-07-21 ruling; the sim's `UNAPPLIABLE` set is empty and both engines emit
   real deltas. So each face below carries an upgrade path, and each one is a
   single axis (upgrade-conventions row 6).

---

## 2. Two facts that set every number on both cards

These are properties of the shipped kit declaration, not choices made here, and
they are the reason both faces are printed **under** the Klee band they sit in
rather than level with it.

**Fact one — the kit already pays a rider neither card prints.** *Little
Hexenzirkul* mints **1 Spark on any Personal Companion play, 1 more if that play
triggered an Elemental Reaction, 1 more if the Companion is upgraded, capped at
3 per play.** The declaration is keyed on the **pool**, not on Prune
(`effects.klee_personal_companion_spark` returns early only when the card is not
a Personal Companion, or when its `personal_pool` is not the player's character),
so both cards below fall under it automatically the day their rows exist. The
four numbers are the shipped constants (`tier0/constants.py:201-204`:
`KLEE_COMPANION_SPARK_BASE = 1`, `..._REACTION_BONUS = 1`,
`..._UPGRADED_BONUS = 1`, `..._MAX_PER_PLAY = 3`).

**The reaction limb is conditional, and earlier drafting of this packet
overstated it.** A Companion applies **its own** element and never Klee's:
`_element_for` (`tier0/engine/effects.py:572`) returns `card.element` for an
effect carrying `applies_element`, and its docstring says so in as many words —
*"Cards with their own element (companions) apply that instead"*, and *"Companion
cards are exempt from cadence entirely"*. So Card 1's Electro does not meet
Klee's Pyro by being played; it meets a Pyro aura only if the target is
**already carrying one**, which in practice means Klee's own catalyst attacks put
it there on an earlier play in the same fight. Into a bare target the play
does not react.

The corrected yields, per play:

| play | Sparks |
|---|---|
| Personal Companion, no reaction | **1** |
| Personal Companion, no reaction, **upgraded** | **2** |
| Personal Companion, **reaction** | **2** |
| Personal Companion, reaction, **upgraded** | **3** (the cap) |

That is one table for **both** cards. Card 1 sits on the reaction rows only when
a Pyro aura is already standing; Card 2 (Pyro, and applying nothing) sits on the
no-reaction rows always. **Card 1 mints 1 Spark into a bare target (2 upgraded)
and 2 onto a standing Pyro aura (3 upgraded, the cap); Card 2 mints 1, and 2
upgraded.**

The rider is therefore worth **the Spark half of `snap`, not `snap`'s whole
body** — one Spark on a normal play, a second only when the board was already set
up. It is still a real free rider on every play, so the honest correction is
still to print the body one step below the Klee card it is being compared to;
what changes is the size of the discount that buys, which §4.4 and §5.4 now
argue on the corrected numbers.

**Fact two — the upgrade of any Personal Companion is worth +1 Spark before its
printed delta.** The kit reads the upgraded suffix off the card id, so the
upgraded face gets its extra Spark whether or not the upgrade row says so —
Prune's `{kit_spark: +1}` is that fact written down, not a mechanism she owns.
Consequence for these drafts: **printed upgrade deltas are modest on purpose**,
because each already rides a free Spark. `{damage: +2}` on a 5-damage common is
the right size here where `{damage: +4}` would be on a Klee card.

---

## 3. Who the two companions are — the whole field, and why it narrows

Mondstadt's committed pool already spends eleven names: Dahlia, Fischl, Barbara,
Sucrose, Bennett, Kaeya, Diona (4-star), Albedo, Durin, Nicole (5-star) and Prune
(Personal). **Prune is the only one of the eleven carrying a Klee-interacting
card**, so ten names are technically free — but authoring a Personal card for a
character who already has Universal rows would put one face of one character on
each side of the taxonomy the slice exists to prove. Both drafts therefore take
**new** Mondstadt names.

The field narrows further by element. Card 1's job requires an **off-element**
applier, because Klee prints no off-element aura (LAW: reactions are earned, not
given) and an off-element application onto her Pyro is what makes the play react
— which is the kit's +1. Electro is the pool's thinnest 4-star element (one row,
Fischl's) and Pyro–Electro **Overload** is implemented as **6 damage to every
living enemy plus Weak 1 on the reacted target** (`tier0/engine/reactions.py:154-161`
— `for other in state.living_enemies: _splash(state, other, C.OVERLOAD_SPLASH)`
then `powers.apply_power(state, enemy, "weak", C.OVERLOAD_WEAK)`, with
`OVERLOAD_SPLASH = 6` and `OVERLOAD_WEAK = 1` at `tier0/constants.py:47-48`),
which is a real body and not a flavour note. It is also the reason the aura
precondition in §2 matters: that body arrives only on the plays that find a Pyro
aura already up. Card 2's job is Bomb-facing and wants a Pyro name.

The specific names are picks `K1` and `K3`. The faces below are written on their
defaults.

---

## 4. CARD ONE — the common, reaction-shaped

### 4.1 The face, as it would print

> **Razor — Claw and Thunder**
> 4★ · Common · Companion (Klee, personal) · Electro
> **1 Energy · Attack**
> **Deal 5 damage. Deal 3 more if the target carries a Bomb.**
> *(Applies Electro.)*

### 4.2 The printed engine interaction

Two of them, and both are Klee-only reads:

- **It reads Klee's Bomb board.** `bonus_vs_bombed` is shipped grammar on
  `kaboom_beetle_swarm`, and a Bomb board exists in exactly one character's deck.
  Dealt to Kokomi or Furina the rider is dead text, which is the test the
  Personal/Universal split is for: this card would be a brick anywhere else, and
  that is *allowed* here and forbidden on a Universal card.
- **It is built to fire Klee's own kit trigger — on a board Klee has already
  touched.** Klee's attacks are catalyst-grade and apply Pyro; the Companion
  applies its **own** Electro (`effects.py:572`), so the Overload happens when
  the Electro lands on a Pyro aura Klee's earlier attack left standing. When it
  does, it splashes 6 to every living enemy, applies Weak 1, and pays the
  *Little Hexenzirkul* reaction bonus (2 Sparks, 3 upgraded). When the target is
  bare it is a plain Electro application and the play mints 1 (2 upgraded).
  **The sequencing is the card's skill expression, not a rounding error**, and
  it is why the reaction limb is not priced into the printed body. Either way
  the card's Spark contribution is **entirely on Klee's side of LAW's line**:
  the face grants nothing.

Nothing here needs a mechanic that has not landed. `damage` with
`applies_element`, and `bonus_vs_bombed`, are both emitted today by
`tools/gen_klee_cards.py`, which is the same generator that emits the companion
sheets.

### 4.3 The upgrade path

`{damage: +2}` — 5 → 7, so 8 → 10 against a bombed target. One axis, visible on
the offer screen, and it rides the free +1 Spark from fact two — which the row
writes as `kit_spark: +1` beside the damage delta (§8, note one: the key carries
no effect delta and is checked against the constant). The alternative axis is
pick `K6`.

### 4.4 At-rarity parity — argued against three named Klee commons

Klee's 1-cost common Attacks, printed:

| card | printed | notes |
|---|---|---|
| `snap` | 6 damage **+ 1 Spark** | the closest neighbour |
| `sizzle` | 8 damage, **+6** if the target holds an off-element aura | 14 ceiling |
| `fish_flavored_bait` | 5 damage **+ a Bomb at 5** | 10 across two turns |

**Card 1 is 5, ceiling 8; upgraded 7, ceiling 10.** Base 5 is the **lowest**
1-cost Attack number on Klee's common sheet and equals `fischl_nightrider`, the
Universal Electro common it will sit beside. The ceiling of 8 equals `sizzle`'s
*base* and is 6 short of `sizzle`'s ceiling.

**The full-kit accounting, on the corrected reaction rule (§2) and with
Overload's actual body counted.** Four lines, because the play is two different
cards depending on whether Klee has already put Pyro on the target:

| line | on the target | elsewhere on the board | Sparks minted |
|---|---|---|---|
| bare target, base | 5 (8 vs bombed) | — | **1** |
| bare target, upgraded | 7 (10 vs bombed) | — | **2** |
| standing Pyro aura, base | 5 + 6 splash = 11 (14 vs bombed), Weak 1 | 6 to each other living enemy | **2** |
| standing Pyro aura, upgraded | 7 + 6 splash = 13 (16 vs bombed), Weak 1 | 6 to each other living enemy | **3** (cap) |

The splash and the Weak are **Overload's** body, not the card's — any off-element
applier landing on Klee's Pyro gets the same, and the reacted rows are therefore
priced as a reward for sequencing rather than as printed power.

**Where that lands the card.** The two rows a player actually gets most of the
time are the bare-target rows, and they are **1 Spark on a 5-damage 1-cost
Attack** — strictly under `snap` (6 damage *and* a Spark), and far under
`sizzle`'s 14 ceiling. The reacted base row (11 on the target, 2 Sparks) is above
`snap` and beneath `sizzle`'s ceiling on one body; on a three-body board its
**total** damage (11 + 6 + 6 = 23) exceeds every 1-cost Klee common, which is the
one place the card is genuinely strong — and it is strong exactly on the turn the
player spent an earlier card setting up. The upgraded reacted row is the cap in
both senses. Taken across the four lines the card is an unremarkable member of
the band with a sequencing ceiling, which is what test 4 asks for.

The Bomb rider is honestly conditional on top of all four: on an empty Bomb board
this is a 5-damage 1-cost Attack, which is under every Klee common on the table.

### 4.5 What it is FOR in a run

It is the **reaction plan's missing first card**. Klee's reaction archetype has
been measured thin twice, and the structural reason is in LAW: she cannot apply
an off-element aura, so her own reaction payoffs (`sizzle`, `flame_dance`,
`perfect_timing`, `boom_goes_the_dynamite`, `vermillion_pact`) depend on
something else putting the aura up. Prune does it by consuming an aura, not
supplying one. This card supplies one every time it is played, at common, on a
body that is never dead. In a demolition deck the rider makes it a cheap
finisher on an armed target; in a reaction deck it is the enabler; in neither is
it a card you build around, which is right for a common.

---

## 5. CARD TWO — the uncommon, build-around

### 5.1 The face, as it would print

> **Amber — Explosive Puppet**
> 4★ · Uncommon · Companion (Klee, personal) · Pyro
> **1 Energy · Skill**
> **Gain 5 Block. If you have a Spark, place a Bomb dealing 5 on each enemy.**

### 5.2 The printed engine interaction

- **It reads Klee's Spark bank on its face.** `has_spark` is the shipped
  predicate (`eager_to_help`, `patched_dress`). It **reads and never grants**,
  so LAW's clause is satisfied without a kit declaration of its own.
- **It writes to Klee's Bomb board**, the other half of her kit, and the board
  is what *Pounding Surprise* pays Sparks off when those Bombs detonate. So the
  card's loop closes **through Klee's relic and kit rather than on the card**,
  which is the shape the contract wants.
- **It is the first card in the game that pays you for NOT spending Sparks.**
  Every existing destination for the bank — `powder_charge`, `hold_the_line`,
  `smoke_and_sparks`, and the whole prototype ladder — takes Sparks away. The
  written finding on the arm is that a hold decision needs the bank to be worth
  something un-spent; this card makes a bank of one a standing threshold. It does
  that **without adding a sink**, which matters for sequencing: see pick `K4` and
  §7.

### 5.3 The upgrade path

`{bomb_damage: +2}` — the Bombs go 5 → 7. The key bumps `bomb_damage` wherever it
appears, including inside a conditional, so it reaches the gated branch, and it
keeps the Spark read printed on **both** faces. The row carries `kit_spark: +1`
beside it, for the reason §8 note one gives. The alternative — upgrading the
gate away with `{condition: unconditional}` — is pick `K5`, and it is not the
default for a stated reason: an upgrade that deletes the engine interaction turns
a Personal Companion into a Universal one on its better face.

### 5.4 At-rarity parity — argued against three named Klee cards

| card | rarity | printed at 1 Energy |
|---|---|---|
| `mine_toss` | **common** | a Bomb at 5 on **each** enemy, ungated, no Block |
| `trip_wire` | uncommon | a Bomb at 7 on one enemy + Weak 1 |
| `hold_the_line` | uncommon | spend 2 Sparks → 5 Block, +6 more if the enemy attacks |

**Card 2 is `mine_toss` plus 5 Block, one rarity step up, behind a gate.** That
is the whole parity argument and it is deliberately simple: the Block is what
the rarity step buys, and the `has_spark` gate is what pays for it. Against
`trip_wire` it is worse on one body (5 against 7, no Weak) and better on two or
three (10 or 15 pending). Against `hold_the_line` it costs no Sparks but delivers
5 Block where that card delivers about 11 in practice.

**The honest failure floor, stated rather than found later — and it is a floor on
the FACE, not on the play.** On an empty bank the *printed* card is 5 Block for
1 Energy, which is `duck_and_cover` — a **Basic**. But the kit rider still fires:
`effects.klee_personal_companion_spark` is called from `_finish_play`
(`tier0/engine/combat.py:626`) **after** `effects.resolve_card` has run, so the
`has_spark` gate is evaluated on the bank as it stood *before* the play — the
card can never gate itself on its own Spark — and an empty-bank Amber still
leaves the player **1 Spark richer (2 upgraded)**. The full-kit accounting:

| board | bank at play | printed body resolves as | kit Sparks this play | bank after | later refund |
|---|---|---|---|---|---|
| 1 enemy | 0 | 5 Block | **+1** (+2 upgraded) | 1 (2) | — |
| 1 enemy | ≥1 | 5 Block + 1 Bomb at 5 (7 upgraded) | **+1** (+2 upgraded) | bank+1 (bank+2) | **+1** when that Bomb pops |
| 3 enemies | 0 | 5 Block | **+1** (+2 upgraded) | 1 (2) | — |
| 3 enemies | ≥1 | 5 Block + 3 Bombs at 5 (7 upgraded) | **+1** (+2 upgraded) | bank+1 (bank+2) | **+3** as they pop |

(The refund column is *Pounding Surprise*, Klee's starting relic: +1 Spark per
Bomb detonation. It is the loop §5.2 describes, written as numbers.)

So the true floor is **5 Block and a Spark for 1 Energy**, not a Basic — and the
empty-bank play is self-correcting, because it hands over the Spark that arms the
*next* copy. An uncommon whose printed face can read as a Basic is still a real
cost and the packet does not withdraw that; what it withdraws is the claim that
the empty-bank play gives you nothing but Block. That the floor is this soft is
also the price of the gate being this easy. Note also that the only shipped Spark predicate is `has_spark`, which
is *greater than zero*: a "two or more" gate is not expressible today and would
be engine work, so the gate is genuinely easy to satisfy in any deck that has
looked at a Spark. That is a reason the body is printed at `mine_toss`'s number
and not above it.

### 5.5 What it is FOR in a run

It is the **bridge between Klee's two plans**, from the demolition side. A
Spark-heavy deck holds a bank it was going to spend anyway; this turns holding
into board damage, and the resulting Bombs mint Sparks back through *Pounding
Surprise* when they pop. A demolition deck with no Spark engine at all still
plays it as a defensive body most turns and a board-wide Bomb whenever a Spark
happens to be around. It is a card a deck is **built around** in the sense the
taxonomy means: taking it changes what the rest of the deck wants to do with the
bank, because for the first time an un-spent Spark is worth something.

---

## 6. The picks — six, each with options and a marked default

**`K1` — which companion carries Card 1.**
1. **Razor — Claw and Thunder** *(DEFAULT)*. Electro is the pool's thinnest
   4-star element; Overload is a reaction Klee's own sheet can never produce;
   Razor is a Mondstadt child of Klee's own generation, which reads as a
   playmate rather than a chaperone.
2. **Lisa — Violet Arc.** Same element, same body; a Knights-of-Favonius adult
   rather than a peer.
3. **Mona — Mirror Reflection of Doom.** Hydro instead of Electro, so the
   reaction becomes Vaporize — which `vermillion_pact` doubles, a stronger tie to
   one Klee Rare, but Hydro is already the pool's most-covered element with four
   rows.
4. **Noelle — Breastplate.** Geo, so the reaction is Crystallize (flat Block to
   the player) and the card becomes defensive rather than offensive; it would
   want a different body from §4.1.

**`K2` — Card 1's printed hook.**
1. **`bonus_vs_bombed 3`** *(DEFAULT)* — reads the Bomb board.
2. **`has_spark` → +3 damage** — reads the bank instead. Rejected as the default
   only because Card 2 already prints that predicate and two of two cards on one
   read is thin for a set of three.
3. **`reaction_triggered_by_this` → +3 damage** — reads the reaction it just
   caused. It is Prune's own predicate, which makes it the most redundant of the
   three against the card the set already has.

**Note — `+3` re-argued against the corrected table (§2, §4.4), rather than
assumed.** The correction moved the card **down**, not up: the ordinary play is
1 Spark and no splash, where the earlier draft credited it with 2 Spark and an
Overload every time. A rider that pays only on an armed target is therefore
sitting on a *weaker* base than the one `+3` was first sized against, so `+3`
does not break — if anything the corrected floor argues it is on the low side.
The counterweight is the reacted-and-bombed line, 14 on the target at base and 16
upgraded, which is the highest single number in the packet; it is reached only by
holding a Bomb board **and** a standing Pyro aura, i.e. by playing two cards
first. The default stands at `3` and no value moved.

**`K3` — which companion carries Card 2.**
1. **Amber — Explosive Puppet** *(DEFAULT)*. Baron Bunny is a placed decoy that
   explodes, which is a Bomb in everything but name; Amber is Pyro; and
   Mondstadt's two explosives enthusiasts is a pairing the fiction writes itself.
2. **Alice — Teyvat Travel Guide.** Klee's mother and the actual source of her
   engine, which is the strongest possible fiction for a *Personal* Companion.
   Against it: Alice is unplayable in the source and has no talent name to take,
   so the card name is an item name, and a first-appearance of Alice as a
   4-star Uncommon may be a bigger call than this slice should make on its own.
3. **Jean — Guiding Breeze.** The canonical Klee tie (`sorry_jean` is already a
   printed Klee card, and the fiction is confiscation). It would want a different
   body — a status-cleanup card reading Klee's `confiscated` vocabulary — which
   is a good card but not a Spark-economy one.

**`K4` — Card 2's hook on the bank, and this is the one with a sequencing
consequence.**
1. **Read it (`has_spark`)** *(DEFAULT)*. Adds no Spark sink, so it does not
   touch the sink program at all, and it supplies the hold-side incentive that
   program keeps finding missing.
2. **Spend it (`spend_spark 2` at top level, alongside the 1 Energy).** Shipped
   grammar and the exact shape of the three hybrids. **But it makes this card a
   new sink of the "investment" kind**, which is the sink-candidate program's
   business, and that program's ruled direction is *migrate before you
   duplicate* — no new row until the mixed-pool read is in. Choosing this option
   means sequencing the card behind that read.
3. **Price it at the head of a mode (`choose_one`).** Legal under the amended
   cost clause, and machinery that exists. **Not recommended, and listed only so
   the option is visibly declined:** the one card using it is under an open
   design question whose collapse condition has not been posed, and a second card
   copying the pattern now would prejudge it. **Sequencing status, corrected:**
   that collapse condition **has** now been posed — `KLEESPARK-W5` ran
   2026-08-30 and `B1` came back **UNREACHED**, at **one** opportunity page
   against a registered floor of **four**, so R230's collapse did not fire and
   could not have. The honest wording is therefore *"unresolved after an
   under-denominator read"*, not *"has not been posed"*. The consequence for
   this pick is unchanged: an under-denominator read licenses nothing, the
   question is still open, and a second card copying the pattern would still
   prejudge it. Option 1 remains the default on exactly the reasoning it
   already had.

**`K5` — Card 2's upgrade axis.**
1. **`{bomb_damage: +2}`** *(DEFAULT)* — Bombs 5 → 7, gate kept on both faces.
2. **`{condition: unconditional}`** — the upgrade deletes the Spark gate. It is
   the most *exciting* upgrade of the three and it is shipped grammar, but the
   upgraded face then prints no engine interaction at all, which is the contract
   §1 sentence 1 exists to hold.
3. **`{block: +3}`** — 5 → 8 Block. The most visible on the offer screen and the
   least interesting; it improves the failure floor rather than the plan.

**`K6` — Card 1's upgrade axis.**
1. **`{damage: +2}`** *(DEFAULT)* — 5 → 7, ceiling 8 → 10.
2. **`{bonus_vs_bombed: +2}`** — rider 3 → 5, so the upgrade only pays in a
   demolition deck. Sharper identity, but it makes the upgrade dead in the
   reaction deck the card is otherwise for.

**Both card names are provisional and cosmetic under R179.** Neither
*Claw and Thunder* nor *Explosive Puppet* appears in
`docs/reserved-card-names.txt` or on any committed sheet; the lint is the floor,
and the names are [USER]'s to settle at any time without moving anything else.

---

## 7. What these two drafts do NOT touch

- **No Rare, and no Rare argument.** R234 `P5a` is deliberately open and bars any
  Rare Personal design until it is answered. Both faces are 4-star, where the
  acquisition chain already works, and neither depends on a third card of any
  rarity existing.
- **No Universal card, and no Universal repricing.** R234 `P2` excludes the
  Universal half from slice 1, and `P8` makes the colorless anchor a precondition
  on it. The anchor now exists as a census, but nothing here spends it: the
  parity arguments in §4.4 and §5.4 are against **Klee's own sheet**, which is
  the only comparison answer 4 licenses for a Personal card.
- **No sheet row, before the fold.** `EB-251`'s gate is the Burst retirement
  fold, per R234 `P3` and the ruled program. §8's YAML is written out so the fold
  has something to land, and it is prospective until then.
- **Nothing that assumes the Burst fold's outcome.** Neither face prints
  `burst_energy`, and neither reads the meter. The three undispositioned
  `burst_energy` companion faces travel in the fold and none of them is touched
  here.
- **Nothing that assumes the alternative-cost re-author.** Both faces work
  identically in the shipped world and in the Spark-alt-cost world. Neither
  prints a 0-Energy Spark-only price, and neither reads
  `zero_cost_attacks_up` or the retiring threshold.
- **Nothing that prejudges the open Bag-of-Tricks question**, its collapse
  condition, or the mode-head price pattern — see pick `K4` option 3, which is
  declined on exactly that ground. The condition is **unresolved after an
  under-denominator read** (`KLEESPARK-W5`, 2026-08-30: `B1` UNREACHED at one
  opportunity page against a floor of four), which is a different state from
  unposed and reaches the same conclusion here.
- **No home-nation weight change.** `SAME_NATION_REWARD_SHARE` holds at 0.5 under
  `P7`, and the re-measurement `P7` attaches is owed **after** these rows land,
  not from this packet.
- **No register row, and no id.** The engineering these faces will need at the
  fold — two portraits, and the codegen check that the companion emitter carries
  `bonus_vs_bombed` and a `has_spark` conditional as the Klee path already does
  — is named here so it is not rediscovered, and minted nowhere.

---

## 8. The prospective sheet rows — **PROSPECTIVE, and nothing writes them today**

Written out so the fold has something to land rather than something to design.
**These are not committed rows.** They land on `docs/mondstadt-companions.yaml`
under the PERSONAL POOL heading, and their upgrade rows on
`docs/klee-upgrades.yaml`, **at the Burst retirement fold and not before**. The
ids below are proposed strings and mint with the rows.

```yaml
# ---------- PERSONAL POOL (Klee) — PROSPECTIVE, lands at the Burst fold ----------
- {id: razor_claw_and_thunder, name: "Razor — Claw and Thunder", star: 4, rarity: common,
   role_c: applier, element: electro, cost: 1, type: attack, personal_pool: klee,
   effects: [{op: damage, amount: 5, target: enemy, applies_element: true, bonus_vs_bombed: 3}]}

- {id: amber_explosive_puppet, name: "Amber — Explosive Puppet", star: 4, rarity: uncommon,
   role_c: buffer, element: pyro, cost: 1, type: skill, personal_pool: klee,
   effects: [{op: block, amount: 5},
             {op: conditional, if: has_spark,
              then: [{op: place_bomb, amount: 1, target: all_enemies, bomb_damage: 5}]}]}
```

```yaml
# docs/klee-upgrades.yaml — PROSPECTIVE
razor_claw_and_thunder:    {damage: +2, kit_spark: +1}      # 5 -> 7; rider unchanged at +3
amber_explosive_puppet:    {bomb_damage: +2, kit_spark: +1} # 5 -> 7 inside the conditional
```

Four notes for whoever lands them.

**`kit_spark: +1` is not an optional garnish — it is how the sheet writes the
kit's upgraded limb.** The key is defined at `tier0/content/upgrades.py:565`, and
its comment is explicit that it applies **no effect delta** (there is nothing on
the face to bump, which is the point of LAW:145's clause) and is **not** a silent
no-op either: the engine expresses it at play time by reading the upgraded flag
in `effects.klee_personal_companion_spark`, and the codegen emits the matching
play-time comment instead of flagging a missing upgrade path. The comment is
equally explicit that **the value is checked rather than trusted** — "the row must
name a card the kit actually reaches, and must agree with the constant" — so `+1`
is not a choice here: it is `KLEE_COMPANION_SPARK_UPGRADED_BONUS`
(`tier0/constants.py:203`) written on the sheet. A row omitting the key would
under-describe the upgrade; a row saying `+2` would fail the check. Prune's
`{kit_spark: +1}` is the same fact already written down (§2, fact two).

**The parity test becomes a three-card enumeration AT THE FOLD.**
`tier0/tests/test_eb219_prune_kit_spark.py` currently enumerates the four
(upgraded × reacted) yields for the **single** Personal Companion that exists —
its `FACE_PARITY` map and `test_prune_pays_exactly_what_her_face_used_to_pay`
are written against `prune_witch_hunt` by id. When these two rows land, that
enumeration must become an enumeration over **all three** Personal Companions,
since the declaration is keyed on the pool and not on Prune (the file's own
`test_a_shared_pool_companions_swirl_mints_nothing` is the other half of that
scoping). **No test is edited today** — the sheet rows are fold-gated, so a test
enumerating cards that do not exist would be red on arrival. This is a note for
the fold, not a task.

**`role_c` on Card 2 is the weakest field on either row.** The vocabulary is
applier / buffer / trigger. Card 2 applies nothing, buffs nothing and triggers
nothing in the reaction sense — it places Bombs, which the taxonomy has no word
for because no companion has ever done it. `buffer` is the closest fit and is
written above; if the fold wants a fourth role word, this is the row that asks
for it, and that is a taxonomy question rather than a card question.

**Neither row carries art.** Two portraits are owed at the fold, on the ordinary
art path, under the R212 ladder's art clause.
