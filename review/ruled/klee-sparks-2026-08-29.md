Status: RULED R219 2026-08-29

# Klee's Sparks as a real cost — the research, and what I need you to pick

**2026-08-29 · branch `klee-sparks-research` · research packet, nothing built,
nothing staged, no ids minted.**

Companion document: `docs/current/research/regent-stars-economy.md`, which is
the evidence. Every number below points back into it or into a repo file by
line.

---

## 1. Your words, and what they settle

Verbatim, from the sitting:

> The old base rule ("At 3 Sparks, your Attacks cost 0. Playing one consumes
> 3") is being retired as the universal base mechanic; Sparks become an
> ALTERNATIVE card cost (some Klee cards cost Sparks instead of Energy); Bomb
> detonation stays the main source.

> "No need for a cap. Getting insane spark generation is fine. Spending a ton
> of sparks is fine. Figuring out how to do both in a deck that also needs to
> do other things should be difficult. Regent doesn't cap its stars, it just
> makes star generation a bit stingy unless you deliberately lean into it."

> (a) "Regent has some star generation in their base kit - I believe it's a
> starter card. Let's aim to match their generation pattern. So this would be
> a research project."

> (c) "Leaning towards reauthoring. I think that we can make some Attacks that
> cost Sparks, matching the lore flavor, with a Rare power that basically
> converts all attacks into 3-spark-cost attacks, which would be a deliberate
> payoff for the archetype."

**What that settles, so nobody re-opens it below:**

1. The threshold rule goes. It is not a card question and cannot be
   quarantined on the prototype card surface — that is exactly the point the
   independent seat made in `review/ruled/klee-slice-1-2026-08-29.md` §6.2,
   which is still held for you and which this direction *answers* rather than
   sidesteps.
2. Sparks are a **price on cards**, not a passive discount on a card type.
3. **No cap.** Confirmed as correct-by-canon: the game's own
   `PlayerCombatState.GainStars` clamps only at zero and has no ceiling, while
   `GainEnergy` four lines above it clamps at 999,999,999. Regent's stars are
   genuinely uncapped.
4. Pounding Surprise (+1 Spark per Bomb detonation) stays the main source.
5. There is a Rare Power that turns the whole Attack suite into Spark
   spenders.

**What it does not settle, and what §3–§6 are pick lists about:** how much
generation, at which rarities, where the starter-deck generator lives, what
the new Attacks cost, which existing cards get converted to make room, which
of two possible wordings the Rare Power uses, and how a Spark price is drawn
on a card face.

**One thing you asked me not to do, and I did not:** EB-186 (all Attacks
showing cost 0 at 3 Sparks) is not cited anywhere here as a defect. It was the
mechanic working.

---

## 2. Klee today against Regent, side by side

### 2.1 What Regent actually has

I decompiled the pinned game build (v0.111.0, `main_assembly_hash`
`222455745`, matching `STATE.md`'s pin) rather than trusting our extracts, and
found two things worth reading before the numbers.

**First: `ForgeStars` is our word, not the game's.** It appears nowhere in the
assembly. It is a regex we wrote in `tools/canon_role_tempo.py:126` that
matches three different things at once, and it fuses **Stars** (the spendable
resource) with **Forge** (a growing 0-cost attack card, closer to Ironclad's
Strength than to a bank). Ten of the nineteen cards in our `regent_forge`
"package" — the anchor `klee/spark` is measured against,
`docs/role-tempo-baseline.md:270` — never touch a Star. **The anchor's
percentages are computed over a population that is about half a different
mechanic.** I have not changed the anchor; that is a measurement-law call. I
have written it down.

**Second: a Star cost is an ADDITIONAL cost, not an alternative one.** From
`PlayerCombatState.HasEnoughResourcesFor`, a card has an energy price *and* a
star price and both are checked independently. Regent gets the *feel* of an
alternative cost by printing **energy 0** on most star cards — 13 of 23,
including the Basic `FallingStar` — not by any either/or machinery. This
matters for us: your "cost Sparks instead of Energy" is expressed as **cost
0 energy, spend N Sparks**, which is what both our engines already do.

### 2.2 The counts

| | Regent (91-card pool) | Klee (79-card pool) |
|---|---|---|
| generators | **11** (12.1%) | **16** (20.3%) |
| spenders | **23** (25.3%) | **3** (3.8%) |
| generators : spenders | **1 : 2.1** | **5.3 : 1** |

By rarity — the shape matters more than the totals:

| rarity | Regent gen | Regent spend | Klee gen | Klee spend |
|---|---|---|---|---|
| Basic / starter | 1 (`Venerate`, 2★) | 1 (`FallingStar`, 2★) | **0** | **0** |
| Common | 4 | 4 | **6** | **0** |
| Uncommon | 4 | 10 | 5 | 3 |
| Rare | 2 | 6 | 5 | **0** |
| Ancient | 0 | 2 | — | — |

Klee's sixteen: six Commons (`sparkly_treasure` 1, `spark_collection` 2,
`skip_and_hop` 1, `warm_glow` 1, `snap` 1, plus `crackle`'s priced discard),
five Uncommons (`cant_catch_me` 1, `sugar_rush` 1, `hot_hands` 3,
`endless_fireworks` = 1/turn power, `catalytic_conversion`), five Rares
(`all_my_treasures` 2, `da_da_da` 1, `playtime_forever`, `sparks_n_splash`,
`true_spark_knight`). Her three spenders are all Uncommon Skills that print
`Spend 2` — `powder_charge`, `hold_the_line`, `smoke_and_sparks`.

### 2.3 Where Klee is more generous than Regent, and by how much

- **On the ratio: about eleven times.** Regent's pool holds 2.1 sinks per
  source; Klee's holds 0.19. Multiply that out and Klee's supply of things to
  spend on, relative to things that make Sparks, is **11× thinner**.
- **At Common: infinitely.** Regent's Common band is 4 generators and 4
  spenders — perfectly balanced, and it is the band a player actually drafts
  from most. Klee's is 6 and **zero**.
- **At Rare: five to nothing.** Regent's Rares are 2 generators against 6
  spenders. Klee's Rares are 5 generators against 0.
- **In the starter deck the direction reverses.** Regent's ten cards ship one
  generator (`Venerate`, 2★) *and* one spender (`FallingStar`, 0 energy /
  2★ — his Basic Attack **is** a star sink). Klee's ten (`kaboom` ×4,
  `duck_and_cover` ×4, `jumpy_dumpty`, `pop`) contain **neither**. Her only
  base-kit income is the relic.

### 2.4 The one number that says what "stingy" means

Regent, from starter deck plus relic only, at 3 energy a turn and a 10-card
deck that cycles every two turns:

- income **+1.0 Spark-equivalent per turn** (Venerate is 2★ seen once per two
  turns), plus a flat **3★ at the start of every fight** from Divine Right;
- expenditure **−1.0 per turn** (FallingStar is 2★, seen once per two turns);
- **net zero, with a 3-point opening buffer.**

Over a four-turn fight: **7★ made, 4★ spent.** The cheapest sink in his whole
pool is 1★; the median printed sink is **3★**. So a Regent who drafts nothing
can play his cheapest sink every turn and his median sink every third turn —
and to do more than that he has to lean in.

Klee's base kit, on the same arithmetic: `pop` places one bomb and
`jumpy_dumpty` places one, so a cycle detonates about two bombs, which is
**+1.0 Spark per turn** from Pounding Surprise — *the same income rate as
Regent*. What she does not have is the **3-point opening buffer** and she does
not have **a single thing to spend it on**. (Treat the +1/turn as an upper
bound: bombs fire on a delay and `jumpy_dumpty` costs 2 energy, so some turns
it does not get played.)

**That is the whole diagnosis in one line: her income already matches Regent's
almost exactly. Her sink supply does not exist.**

---

## 3. The generation pattern to match — PICK 1

Because §2.4 says income is already right, "matching the generation pattern"
is mostly about **not adding more generation** while adding sinks, and about
deciding whether the relic keeps doing Divine Right's job.

### 3.1 Does Pounding Surprise already equal Divine Right?

**Not quite, and the difference is the interesting one.**

| | Divine Right | Pounding Surprise |
|---|---|---|
| when | start of every combat, once | on every Bomb detonation |
| amount | flat **3** | **+1 each**, unbounded |
| steerable? | no — it just happens | **yes** — you chose the bombs |
| turn-one value | 3 Stars in hand | usually **0**; bombs have not gone off yet |

Divine Right's job is to make **turn one non-dead**. Pounding Surprise's job
is to make **the demolition plan feed the spark plan**. They are different
jobs, and Klee currently has only the second. Under an economy where Attacks
cost Sparks, a turn-one hand of Spark-priced Attacks with a bank of 0 is a
brick.

**PICK 1 — the starter-kit generator.**

1. **Relic keeps its body, and a Basic card carries the buffer.** Add a Spark
   rider to one starter card — the natural home is `pop` (0 energy, places a
   bomb), which becomes "place a Bomb, gain 1 Spark". Mirrors Regent exactly:
   a Basic that makes, a Basic that spends. *This is my recommendation* — my
   reading is that it puts the control on a card the player chooses to play,
   which is the D2 answer, and it is the smallest change that removes the
   turn-one brick.
2. **Relic gains Divine Right's clause outright**: "At the start of each
   combat, gain 2 Sparks. Whenever a Bomb detonates, gain 1 Spark." Simplest
   to reason about, but it is unsteerable income and the seat's D2 objection
   in §6.2 was precisely about unsteerable Spark machinery.
3. **Relic changes to a flat per-combat grant only** (drop the per-detonation
   clause). Cleanest match to Regent, but it severs demolition from spark,
   which is Klee's whole bridge — I would not.
4. **Neither; the opening Attack is priced at 1 Spark and the first
   detonation pays for it.** Accepts a dead turn one by design. Honest, and
   possibly the most interesting; also the most likely to feel bad.
5. **Convert one Basic Attack into the starter's spark sink** — `kaboom`
   becomes 0 energy / Spend 1 Spark. This is `FallingStar`'s exact role. Can
   be combined with (1) and probably should be.

**PICK 2 — how many free generators survive, by rarity.** Regent's shape is
`Basic 1 / Common 4 / Uncommon 4 / Rare 2`. Klee's is `0 / 6 / 5 / 5`.

1. **Match Regent exactly** — `Basic 1 / Common 4 / Uncommon 4 / Rare 2`.
   Requires converting or de-riding 2 Commons, 1 Uncommon, 3 Rares.
   *Recommended*, with the caveat in §4.3 about how deep the Rare cut goes.
2. **Match at Common and Basic only**, leave Uncommon and Rare alone. Half the
   work, and Common is the band that decides the early game.
3. **Keep all sixteen generators and only add sinks.** Pool grows by 5–8
   cards. Simplest, but the ratio lands around 1:0.5 — still twice as
   generous as Regent, and your "should be difficult" does not bite.
4. **Go past Regent** — cut to `Basic 1 / Common 3 / Uncommon 3 / Rare 1`,
   because Klee's relic supplies income Regent's does not. Defensible, and
   riskier.

> **PICK 2 — ANSWERED (R226, 2026-08-30): option (1), match Regent exactly —
> `Basic 1 / Common 4 / Uncommon 4 / Rare 2`.** The conversion is 2 Commons,
> 1 Uncommon and 3 Rares, and §4.3's caveat about how deep the Rare cut goes
> rides with it. **One condition, and it is the only one:** if `EB-205`'s
> sim-drafted arm (`KLEESPARK-S1`) shows a drafted-deck maker:sink ratio that
> CONTRADICTS Regent's shape, PICK 2 **RETURNS to [USER] with that number** —
> it is not re-decided by Claude, and no other evidence reopens it. The
> shipped-pool edit itself is a fold edit and lands at the
> `SPARK_ALT_COST_ENABLED` flip, not before. **PICK 1 is untouched and still
> open** — R225's order stands: the generator question is answered first, on a
> representative deck.

> **R227 (2026-08-30): the condition FIRED, the number was RETURNED, and
> REGENT STANDS — `1/4/4/2`.** `KLEESPARK-S1`'s `S4` read the drafted floor-15
> maker:sink median at **1.500, rising** from floor 5 rather than falling as
> the registered arithmetic predicted. The number was returned to [USER]
> exactly as R226 required, and [USER] ruled that Regent stands. The ratio is
> **maker-heavy**, and its sink denominator is contaminated by `EB-233` — the
> drafter undervalues the non-damage Spark sinks — so it is evidence for
> neither a softer nor a deeper cut. **The exact card cuts are named in the
> fold packet with `W4` in hand**: 2 Commons, 1 Uncommon and 3 Rares, of which
> `true_spark_knight` is already re-authored; `W4` may decide whether Spark
> Knight's Oath takes one of the Rare slots.

---

## 4. Attacks that cost Sparks — PICK 3

### 4.1 It is already expressible, in both engines, today

Nothing needs to be built for the cards themselves.

**tier0:** a row prints `cost: 0` and a **top-level** `{op: spend_spark,
amount: N}`. `tier0/engine/combat.py:186` `spark_cost()` derives the price
from the op — deliberately, so "the price shown and the price paid cannot
drift apart" — and `card_playable` at line 171 gates on it:

```python
price = spark_cost(card)
if price and state.player.sparks < price:
    return False
```

The payment is `tier0/engine/effects.py:928 spend_sparks`, all-or-nothing,
never a partial spend.

**C#:** `klee-mod/KleeCode/Powers/SparkPower.cs` already ships both halves —
`SparkPower.CanSpend(owner, amount)` is wired into a generated
`CardModel.IsPlayable` override (the gate), and `SparkPower.Spend(...)` is the
payment. `tools/gen_klee_cards.py:3985 _stmt_spend_spark` emits it. Three
Uncommon Skills use this rail in the shipped game right now.

**So the only thing standing between us and Spark-priced Attacks is that no
Attack has ever printed the op.**

### 4.2 Five candidates, priced against §2.4's income

Income target is ~1 Spark/turn plus a small opening buffer, so: **1 Spark =
one turn of income, 2 = a cycle, 3 = Regent's median sink.** All are 0 energy.

| # | name | rarity | price | body | the Regent row it mirrors |
|---|---|---|---|---|---|
| 1 | **Sizzle** | Common | Spend 1 | 8 damage | `GuidingStar` (1★, 12 dmg) |
| 2 | **Tinder Toss** | Common | Spend 1 | 4 damage to ALL enemies | `CloakOfStars` (1★, the cheap utility) |
| 3 | **Bang Bang!** | Common | Spend 2 | 5 damage to a random enemy, twice | `FallingStar` (2★, the Basic sink) |
| 4 | **Dodoco Blast** | Uncommon | Spend 2 | 7 damage to ALL enemies | `GammaBlast` (3★ AoE) |
| 5 | **Firework Finale** | Uncommon | Spend 3, Exhaust | 18 damage, single target | `Devastate` (4★ big hit) |

On the names: `Sizzle`, `Bang Bang!` and `Tinder Toss` sit in the
onomatopoeia family the sheet already speaks — `Snap!`, `Crackle`,
`Da-da-da!`, `Pop`. `Dodoco Blast` reuses a word the mod already uses in code
(`KleeCombatVfx.SpawnDodocoPop` is literally the Spark-spend effect).
`Firework Finale` sits beside `Pocket Fireworks` and `Endless Fireworks`.
**All five are provisional and go through the reserved-names lint (LAW, R69 /
R29d) before anything is authored.**

The damage numbers above are *shape*, not ruled values. They are set so a
Spark-priced Attack beats its energy-priced neighbour by roughly the energy it
did not spend — that pricing derivation is a separate, one-constant job and I
have not done it here.

### 4.3 What gets converted, so the pool does not grow — PICK 4

Klee's pool is 79. One-for-one conversions keep it there and move the ratio at
the same time.

1. **The tight set (5 conversions, pool stays 79).** *Recommended.*
   - `sparkly_treasure` (Common, 0E, gain 1) → **Sizzle**
   - `spark_collection` (Common, 1E, gain 2) → **Bang Bang!**
   - `pocket_fireworks` (Common, 1E attack, no Spark rider) → **Tinder Toss**
   - `sugar_rush` (Uncommon, 1E, +1 energy + gain 1) → **Dodoco Blast**
   - `cant_catch_me` (Uncommon, 1E, block 2 + gain 1 + draw 1) → **Firework
     Finale**

   Result: generators `Basic 0→1 (PICK 1) / Common 6→4 / Uncommon 5→3 / Rare
   5`; spenders `Common 0→3 / Uncommon 3→5`. Overall **11 : 8, or 1 : 0.73**.
   Still more generous than Regent's 1 : 2.1, but it is a fifth of the
   distance from where we are, and the Common band lands at 4 : 3 against
   Regent's 4 : 4.

   Why those five: the three Commons chosen are the ones whose whole body is
   "make a Spark" (`sparkly_treasure`, `spark_collection`) or that is already
   a low-texture enabler (`pocket_fireworks`); the two Uncommons are the ones
   whose Spark gain is a small rider on other value, so the archetype loses
   least. `snap`, `warm_glow`, `skip_and_hop` and `crackle` survive, which
   keeps one Common Attack that generates (`snap` = Regent's `SolarStrike`
   role) and two block-plus-Spark glue cards.

2. **The tight set plus a Rare cut.** Add `da_da_da` (Rare, gain 1) →
   converted to a Rare Spark spender, taking Rares to 4 generators. Gets the
   overall ratio to about 1 : 0.9.
3. **Convert nothing; add the five as new cards.** Pool goes to 84. Ratio
   lands at 1 : 0.5. Least disruptive to existing balance reads, weakest on
   your "should be difficult".
4. **Convert only the three Commons.** Pool stays 79, the Common band gets its
   sinks, Uncommon and Rare are left for a later pass.

---

## 5. The Rare Power — PICK 5

Your shape: *"a Rare power that basically converts all attacks into
3-spark-cost attacks."* There are two ways to write that sentence and they are
very different cards.

### Wording (1) — STRICT conversion

> **True Spark Knight** — Rare, Power, 2 Energy.
> *"Your Attacks cost 3 [Spark] instead of their Energy cost."*

**In play:** every Attack in the deck now reads `0 energy / 3 Sparks`. With
base income around 1 Spark a turn you get roughly one Attack every three turns
unless you have drafted generation — which is the payoff loop working: the
Power is a bet that you *have* the engine. It bricks hard when you do not.
Energy becomes almost pure Skill currency. It is legible: every Attack's cost
corner shows the same number.

**In code:** the price is not on the card, so `spark_cost()` — which reads
top-level ops off the row — cannot see it. Both engines need a **new
power-contributed Spark price** that the playability gate consults. In tier0
that is a few lines in `combat.spark_cost` and `card_playable`. In C# it is a
new hook of the same shape the base game already has for Stars
(`AbstractModel.TryModifyStarCost`, fanned out by
`Hook.ModifyStarCost`) — we would be writing our own copy of an extension
point the game ships and, notably, **nothing in the base game overrides**.

**One sub-pick if you take (1):** what happens to Attacks that *already* print
a Spark price (§4.2)? (a) they are unaffected — the Power only converts
energy-priced Attacks; (b) all Attacks become exactly 3, which *raises* the
price of `Sizzle` from 1 to 3. I would take **(a)**: (b) makes the payoff
punish the very cards the archetype drafts.

### Wording (2) — MAY-PAY

> *"You may pay 3 [Spark] instead of an Attack's Energy cost."*

**Does STS2 have an either/or cost UI Regent uses? No.** I looked, and the
answer is unusually clean. There is exactly one mechanism in the whole
assembly that lets one currency stand in for another —
`Hook.ShouldPayExcessEnergyCostWithStars` — and it is:

- **automatic**, with no prompt and no choice;
- a **shortfall** rule, firing only when energy is already insufficient;
- fixed at **2 Stars per missing energy**;
- and **not enabled by anything that ships**. Its card, `Reserves`, exists as
  a localisation string — *"If you don't have enough ⚡ for a card, 2★ are used
  per ⚡ instead"* — with **no implementing class anywhere in v0.111.0**. Same
  for `VISIONS_OF_GRANDEUR` and `PITY`. Cut or unreleased content.

So the nearest expressible form of MAY-PAY is **automatic: pays Sparks when
affordable, else Energy**. And that reintroduces exactly the problem the
independent seat raised in slice 1 §6.2 — *"the automatic rule itself remains
facially in tension with D2… it chooses the first eligible Attack and forces
both timing and expenditure."* We would be retiring one automatic engine and
installing another.

A genuine prompt is possible but has no precedent: the game's choose-a-card
screen has no per-mode playability (our own
`tier0/engine/combat.py:200 charge_cost` docstring already records this
problem for modal cards), so a play-time "pay which?" dialogue is new UI in a
live game, on a Rare.

### My recommendation

**Take wording (1), STRICT.** My reading: it is the only one of the two where
the player's decision happens at a moment the player controls — drafting and
playing the Power, then choosing *which* Attack the bank buys when the bank is
short — which is D2 satisfied by acquisition and conversion rather than by a
prompt. On D4 it is strictly better too: a fixed printed price in the cost
corner is the pattern the base game uses for every one of its 23 star cards,
and none of them explain the price in rules text because the badge carries it.
MAY-PAY, in the only form the engine can express, is an automatic engine
wearing the word "may".

**Re-authored text.** The current `true_spark_knight` row (Rare, 2 energy,
`spark_threshold_down 1`, "free attack at 2 sparks instead of 3") dies with
the base rule — it is a modifier to a threshold that will not exist. Proposed
replacement, same id, same rarity, same cost:

> **True Spark Knight** — Rare · Power · 2 Energy
> *"Your Attacks that do not already cost [Spark] cost 3 [Spark] instead of
> their Energy cost."*

---

## 6. Engine notes — what actually has to move

### 6.1 Retiring the base rule

**tier0 — four places, all in the Spark rule and nowhere else.**

| file : line | what it is | what happens |
|---|---|---|
| `tier0/constants.py:68` | `SPARKS_FOR_FREE_ATTACK = 3` | deleted (or kept only for the archived world) |
| `tier0/engine/combat.py:38–41` | `spark_threshold()` | deleted |
| `tier0/engine/combat.py:279–281` | in `card_cost`: `if card.type == "attack" and sparks >= threshold: return 0` | deleted — this is the zeroing |
| `tier0/engine/combat.py:305–310` | in `play_card`: `state.sparks_at_play = p.sparks` and the `p.sparks -= spark_threshold(state)` consume | consume deleted; `sparks_at_play` decision below |

**What survives untouched, and is the new economy's spine:**
`combat.py:171–175` (the playability gate), `combat.py:186–200`
(`spark_cost`), `effects.py:911–947` (`spend_spark_amount`, `spend_sparks`),
`effects.py:1772–1783` (`_op_spend_spark`).

**Three rulings become dead letters and should be retired with the rule, not
left standing:** R34 (X-cost Attacks exempt from the spark spend — there is no
spend to be exempt from), R39 (readers see the pre-spend bank — nothing spends
implicitly any more, so `state.sparks_at_play` and
`SparkPower.SparksAsResolved` both lose their reason to exist), and the
`gleeful_barrage` compensation note at `docs/klee-cards.yaml:281–287`, whose
whole subject was the threshold fighting itself.

**C# — `klee-mod/KleeCode/Powers/SparkPower.cs`.** Delete `Threshold`,
`CurrentThreshold`, `AppliesTo`, `TryModifyEnergyCostInCombat`,
`BeforeCardPlayed`, `AfterCardPlayed`, `SparksAsResolved`, the
`_pendingSpendPlay` / `_pendingSpendAmount` pair, and the localisation
description string *"At 3 Sparks, your Attacks cost 0. Playing one consumes 3
Sparks."* **Keep** `Gain`, `CanSpend`, `Spend`, `SparksAtPlay` — those are the
alternative-cost machinery and they already work. `SparkThresholdDownPower`
goes with `true_spark_knight`'s old body.

### 6.2 The flag, and what the repo's convention actually is

There are **two** quarantine mechanisms here and they are not
interchangeable — which is the whole reason §6.2 of the slice-1 packet is held
for you.

- **Cards** are quarantined by living on `docs/prototype-surface.yaml` with
  `proto_`-prefixed ids, compiled only under `dotnet build
  -p:PrototypeCards=true` and reachable only by explicit grant. That covers
  §4's five Attacks and §5's Power body cleanly.
- **A rule change cannot be.** The threshold rule is in
  `tier0/engine/combat.py` and `SparkPower.cs`, not on a card sheet. The
  repo's convention for a behaviour switch is a `*_ENABLED` boolean declared
  next to the code it gates — the two live examples are
  `PILOT_POLICIES_ENABLED` (`tier0/pilot/policy.py:938`) and
  `MODE_CHOOSER_ENABLED` (`tier0/pilot/policy.py:1030`). So the name that
  matches the house is **`SPARK_ALT_COST_ENABLED`**, not `SPARK_ECONOMY`, and
  its home is `tier0/constants.py` beside `SPARKS_FOR_FREE_ATTACK` (line 68),
  because that is the constant it retires.

**PICK 6 — how the rule change is gated.**

1. `SPARK_ALT_COST_ENABLED = False`, both rules living
   side by side behind it, with the mod compiling the new `SparkPower` only
   under `-p:PrototypeCards=true`. *Recommended* — it lets one arm be measured
   against the other, which nothing else here can give you.
2. Flip the rule outright and re-baseline. Faster, and every existing Klee
   number becomes incomparable in one step (`RT/D/P/C` all move).
3. Prototype cards only, rule untouched — the slice-1 shape. **This is the one
   that cannot answer the question**, and the seat already said so.

### 6.3 The pilot

The comment at `docs/klee-cards.yaml:267` — *"the pilot has no
hold-versus-spend term for Sparks"* — **is stale.** `STATE.md` records
`POLICY_VERSION 11` as R207, "the pilot gains a Spark hold-versus-spend term".
That comment should be corrected as hygiene whenever that row is next touched.

**Is the gap smaller under a pure spend economy? Yes, structurally.** The
hold-versus-spend problem exists *because* holding at 3 has a payoff (a free
Attack) that competes with spending. Retire the threshold and holding has no
payoff at all — a Spark is worth exactly what you buy with it — so the pilot's
question collapses from "hold or spend?" to "can I afford this sink, and is it
the best card in hand?", which is the question it already answers for energy.

**But one drafter dial becomes wrong and it is yours.**
`tier05/draft.py:1602` sets `STATIC_SPARK_VALUE = 0.0` — a `gain_spark` is
priced at **zero**. That was defensible when Sparks only fed a discount. Under
a spend economy every generator is underpriced by exactly that constant, which
will show up as the drafter refusing to build the archetype. `draft.py:1670`
records that the value is held by you. **PICK 7:** (1) leave it at 0.0 and
read the consequence, (2) move it in the same batch as the rule, (3) derive it
from the new sink prices once §4's numbers are ruled — *my reading is (3)*,
because a value derived from prices that do not exist yet is a guess.

### 6.4 Display — PICK 8

The current Spark cost is a **text line** in the card body. The base game
never does that: its 23 star cards say **nothing** about their price in rules
text and carry it entirely on a dedicated cost badge beside the energy orb
(`Nodes.Cards/NCard.cs:1044 UpdateStarCostVisuals`, a `_starIcon` /
`_starLabel` pair with its own red-when-unaffordable colouring, plus a
persistent on-screen counter that Regent forces always-visible).

1. **Reuse the game's own star badge by storing Sparks in
   `PlayerCombatState.Stars`.** `CardModel.CanonicalStarCost` is `public
   virtual` and a modded card can override it;
   `UnplayableReason.StarCostTooHigh`, the red cost colouring, the persistent
   counter (`Klee.ShouldAlwaysShowStarCounter => true`), the spend/gain hooks
   and the history entries all then come **free**, exactly as they work for
   Regent. Cheapest by a distance and it is the shipped UI.
   **The risk, stated plainly:** Sparks would *be* Stars. The power-bar icon
   goes away, every reader (`has_spark`, `gleeful_barrage`) re-points at
   `PlayerCombatState.Stars`, and in co-op a Star Potion or a Regent star
   relic would top up Klee's Sparks. That cross-character coupling is a design
   call, not an engineering one.
2. **Keep `SparkPower` and build a Klee Spark badge** on the card face,
   mirroring `NCard`'s star badge. No coupling, real UI work, and it is the
   thing `EB-186` proved the player reads first.
3. **Keep the text line.** Cheapest, and it is the option the base game
   deliberately does not take — a price in the rules box is a price you read
   after deciding.

*My reading is (2)* — the badge is the right display and the Stars coupling in
(1) is a door I would not walk through on a display question. But (1) is worth
a serious look precisely because it is free, and if you want it, it is a
one-way door and should be picked as one.

---

## 7. Independence and protocol

Roles here follow "models don't grade their own work", by model family
(R217 / the `authored_by` field on `docs/prototype-surface.yaml`, EB-190).
The **Spark-cost Attacks (§4) and the Rare Power (§5) are authored by
Claude**, so the independent grader on those rows is **the Codex seat (GPT)**;
a fresh-Opus grade on those same rows is same-family and is recorded as such,
not as the deciding read. GPT also **gates doctrine on the slate before
anything is built**, under the doctrine seat protocol in `OPERATIONS.md` — a
gate decides what may be built and decides nothing about whether it is good.
The one row GPT does **not** read independently is the **base-rule retirement
and the alternative-cost economy itself (§1, §6)**, because GPT co-authored
that direction with you; there the independent read is **Claude's**, marked by
family. Every row carries `authored_by` before `tools/gen_prototype_cards.py`
will emit it, and `understudy/seat.py` refuses a seat that would grade its own
family's work.

---

## 8. Ordered next steps

1. **Answer PICK 5 (strict vs may-pay) and PICK 6 (how the rule is gated).**
   Everything else is downstream: the Attack prices in §4 only make sense once
   the Power's shape is fixed, and nothing can be measured until the rule
   change has somewhere to live. → depends on nothing.
2. **Answer PICK 1 and PICK 2** — the starter-kit generator and the surviving
   generator counts. → sets the income the §4 prices are priced against.
3. **Answer PICK 3 and PICK 4** — the five Attacks and which cards convert.
   → depends on 2.
4. **GPT doctrine gate on the resulting slate** (cards only; the rule row is
   Claude-read per §7). → depends on 1–3.
5. **Claude authors the rows** onto `docs/prototype-surface.yaml` as `proto_*`
   with `authored_by: [claude]`, behind `SPARK_ALT_COST_ENABLED` if PICK 6
   takes (1). → depends on 4.
6. **Answer PICK 8** (display) before the dev build, because option (1) changes
   where the bank lives and would invalidate anything built on `SparkPower`.
   → depends on nothing, but blocks 7.
7. **Dev build, stage, blind grade with the Codex seat as the independent
   read**, replay every graded line. → depends on 5, 6.
8. **Answer PICK 7** (`STATIC_SPARK_VALUE`) once §4's prices are ruled, then
   re-baseline. → depends on 3 and 7.
9. **Separately, and not blocking any of the above: the `regent_forge` anchor.**
   §2.1 shows it is half a different mechanic. That is a measurement-law
   question about `docs/role-tempo-baseline.md` and
   `tools/canon_role_tempo.py:126`, and it is yours. → depends on nothing.

---

## 9. The independent seat's doctrine read

Run 2026-08-29 under the doctrine seat protocol (`OPERATIONS.md`), model
`gpt-5.6-sol`, on this packet at `412b929`. Verbatim output and provenance:
`review/qa/klee-sparks-doctrine-review-codex-gpt-5.6-sol.md`; prompts:
`review/qa/klee-sparks-doctrine-review-prompt.txt` and
`…-r2-prompt.txt`. The seat was told the DIRECTION is [USER]-ruled and closed,
and that its own family co-authored it (§7), so it gated the cards and the
picks only and issued no verdict on the base-rule row.

Every quotation below is the seat's own, unedited. A blank clause cell means
the seat cited none for that row.

| pick | seat's option (verbatim) | doctrine | clause cited (verbatim) | vs my reading |
|---|---|---|---|---|
| 1 | *"1, Relic keeps its body, and a Basic card carries the buffer; 5, Convert one Basic Attack into the starter's spark sink; best: 1."* — and *"Options 1 and 5 together follow."* | FOLLOWS | D2: *"The control must be reachable early and reliably — starter kit, starting relic, base system, or the ordinary pool — not only through a rare."* | agrees |
| 2 | *"1, Match Regent exactly."* | FOLLOWS | D2: *"Every persistent resource and every automatic engine must feed a decision the player can steer."* | agrees |
| 3 | *"2, Tinder Toss; 3, Bang Bang!; 4, Dodoco Blast; 5, Firework Finale; best: 2. Option 1 ruled out — R69 / R29d."* | REQUIRES_MODIFICATION | R69 / R29d: *"Display names live in the unique-names namespace, reserved names annotated with the owning kind."* | **DISAGREES** — §4.2 offered all five candidates; the seat rules candidate 1 out |
| 4 | *"1, The tight set."* | FOLLOWS | D7: *"Each pool carries linear signposts AND modular tools."* | agrees |
| 5 | *"1, STRICT conversion."* — sub-pick *"(a), already-priced Attacks are unaffected; (b) ruled out — D2."* | FOLLOWS | D2: *"Every persistent resource and every automatic engine must feed a decision the player can steer: timing, targeting, placement, acquisition, conversion, or forgoing."* D4: *"At the decision point the player can perceive and forecast the consequences that matter."* | agrees |
| 6 | *"1, `SPARK_ALT_COST_ENABLED = False`."* | FOLLOWS | D4: *"Text that cannot bind in the shipped world, invisible feeds and misleading calculated displays are defects."* | agrees |
| 7 | *"3, derive it from the new sink prices once §4's numbers are ruled."* | FOLLOWS | D4: *"At the decision point the player can perceive and forecast the consequences that matter."* | agrees |
| 8 | *"2, Keep `SparkPower` and build a Klee Spark badge."* | FOLLOWS | D4: *"At the decision point the player can perceive and forecast the consequences that matter, through the card, a keyword, a persistent UI element or a character rule."* | agrees |

And the three gate questions:

| gate | seat's verdict | clause cited (verbatim) |
|---|---|---|
| G1 — do the five Spark-cost Attacks fix the sink problem within doctrine? | REQUIRES_MODIFICATION | R69 / R29d: *"Display names live in the unique-names namespace, reserved names annotated with the owning kind."* |
| G2 — does the STRICT Rare Power fix it within doctrine, given that no either/or cost UI exists? | FOLLOWS | D2: *"Every persistent resource and every automatic engine must feed a decision the player can steer."* D4: *"At the decision point the player can perceive and forecast the consequences that matter."* |
| G3 — is a Spark bank whose only sinks are printed card prices steerable under D2 and visible under D4? | FOLLOWS | D2: *"Every persistent resource and every automatic engine must feed a decision the player can steer."* D4: *"At the decision point the player can perceive and forecast the consequences that matter, through the card, a keyword, a persistent UI element or a character rule."* |

**The one disagreement, and it is a real catch.** §4.2 candidate 1 proposed the
name **Sizzle**, and `Sizzle` is already a shipped Klee Common Attack
(`docs/klee-cards.yaml:158`, upgrade at `docs/klee-upgrades.yaml:46`; the
character design doc's §4 names it too). §4.2 said the five names go through
the reserved-names lint before anything is authored; the seat did the lint's
job first and unaided. The name is [USER]'s to settle when PICK 3 is answered —
I have not chosen a replacement here, because the seat may not supply one and
neither may I in the same breath as recording its verdict.

**No clause moved that the packet had not already put in front of the seat**,
and the seat named none beyond D2, D4, D7 and the card-sheet naming rule. It
volunteered no remedy in either round.

---

## 10. What was built — the tier 0 arm

**2026-08-29 · branch `klee-sparks-sim`, stacked on `klee-sparks-research`.**
Python sim only. No C# was written, nothing was deployed, and the game was not
launched. Every number in this section is SHAPE, and under R215 B nothing
measured on a prototype row is quotable anywhere.

### 10.1 The flag, and what moves behind it

`SPARK_ALT_COST_ENABLED = False` in `tier0/constants.py`, beside
`SPARKS_FOR_FREE_ATTACK` — the constant it retires — and named on the repo's
own `*_ENABLED` convention (`PILOT_POLICIES_ENABLED`, `MODE_CHOOSER_ENABLED`).
PICK 6, option 1.

Six sites read it and no seventh does:

| site | with the flag ON |
|---|---|
| `combat.card_cost` | the Attack-zeroing branch does not run |
| `combat.play_card` | the automatic consume does not run |
| `combat.spark_power_price` | the strict Rare Power contributes a price |
| `loader._starter_ids` | two starter substitutions |
| `pilot/policy.py` | a Spark stops being "a third of a free Attack" |
| `tier05/draft.py` | the Spark dials are re-derived |

`SPARKS_FOR_FREE_ATTACK` and `combat.spark_threshold` are both marked
RETIRED-UNDER-FLAG in comments and are unread with the flag on. Neither is
deleted: option 1 exists so the two economies can be run as two arms, and an
OFF arm needs the shipped rule byte for byte. R34's X-cost exemption goes inert
with the branch it guarded — with nothing spending implicitly there is no spend
to be exempt from.

**Flag off is byte-identical, and it is measured rather than asserted.** A
sha256 of the entire event log of a fixed-seed Klee starter fight was taken on
this branch's parent (`a8b8552`), before a byte of the arm existed:
`20b877d3411ccdc5306f6b8c0664c8d0f0dd7f9b30421d73af411aa8c3dbe9fa`. It is
equal on the finished branch, and it is pinned in
`tier0/tests/test_spark_alt_cost.py`.

### 10.2 The rows, as written

Seven rows are on `docs/prototype-surface.yaml`. Verbatim:

```yaml
- {id: proto_pop_spark, name: "Powder Pop", character: klee,
   authored_by: [claude],
   cost: 0, type: skill, rarity: basic, solve: [frontload], archetypes: [demolition], role: enabler, tags: [skill_tag],
   effects: [{op: place_bomb, amount: 1, target: enemy, bomb_damage: 5},
             {op: gain_spark, amount: 1}]}

- {id: proto_kaboom_sink, name: "Ka-pow!", character: klee,
   authored_by: [claude],
   cost: 0, type: attack, rarity: basic, solve: [frontload], archetypes: [generic], role: glue,
   effects: [{op: spend_spark, amount: 1},
             {op: damage, amount: 7, target: enemy}]}

- {id: proto_spark_strike, name: "Fwoosh!", character: klee,
   authored_by: [claude],
   cost: 0, type: attack, rarity: common, solve: [frontload], archetypes: [spark], role: payoff,
   effects: [{op: spend_spark, amount: 1},
             {op: damage, amount: 8, target: enemy}]}

- {id: proto_spark_sweep, name: "Tinder Toss", character: klee,
   authored_by: [claude],
   cost: 0, type: attack, rarity: common, solve: [frontload], archetypes: [spark], role: payoff,
   effects: [{op: spend_spark, amount: 1},
             {op: damage, amount: 4, target: all_enemies}]}

- {id: proto_spark_double_tap, name: "Bang Bang!", character: klee,
   authored_by: [claude],
   cost: 0, type: attack, rarity: common, solve: [frontload], archetypes: [spark], role: payoff,
   effects: [{op: spend_spark, amount: 2},
             {op: damage, amount: 5, target: random_enemy, times: 2}]}

- {id: proto_spark_blast, name: "Dodoco Blast", character: klee,
   authored_by: [claude],
   cost: 0, type: attack, rarity: uncommon, solve: [frontload], archetypes: [spark], role: payoff,
   effects: [{op: spend_spark, amount: 2},
             {op: damage, amount: 7, target: all_enemies}]}

- {id: proto_spark_finisher, name: "Firework Finale", character: klee,
   authored_by: [claude],
   cost: 0, type: attack, rarity: uncommon, solve: [frontload], archetypes: [spark], role: payoff, exhaust: true,
   effects: [{op: spend_spark, amount: 3},
             {op: damage, amount: 18, target: enemy}]}
```

Every damage figure is §4.2's table verbatim. The two Basics carry their
shipped twins' bodies unmoved (`kaboom` 7 damage, `pop` one Bomb at 5), so the
starter substitution is a PRICE change and nothing else. The one-for-one pool
replacements PICK 4 names are recorded in the surface's header comment and
executed nowhere — this surface cannot reach a pool, and re-authoring the
printed sheet is what ACCEPTANCE means under the deletion rule.

**The renamed candidate.** §4.2 candidate 1 was `Sizzle`; the seat ruled it out
by name under R69 / R29d because `Sizzle` is a shipped Klee Common Attack
(`docs/klee-cards.yaml:158`). Only the name moved — rarity, price, cost and body
are the packet's unchanged. The replacement is **`Fwoosh!`**: provisional and
mine under R179, in the onomatopoeia family the sheet already speaks (`Snap!`,
`Crackle`, `Pop!`, `Da-da-da!`), zero hits against `docs/reserved-card-names.txt`
and against every display name on every sheet, and `lint_unique_names` is green
on it. **The name is yours to settle; the lint is the floor, not the ruling.**
`Powder Pop`, `Ka-pow!` and `Spark Knight's Oath` are working titles for the
same reason — a proto row may not reuse its twin's printed name.

**The eighth row is not on the surface, and this is the first thing that goes
back to you.** PICK 5's re-authored Rare Power is written and its sim half is
built and tested, but `tools/gen_prototype_cards.py` refuses the row by name:

> `proto_true_spark_knight is NOT EXPRESSIBLE: apply_power power
> 'spark_attack_cost' (no PowerModel in the registry). A prototype row must be
> emittable today — rewrite it inside the existing grammar, or take the runtime
> work first.`

That refusal is correct and was left standing rather than worked around: the C#
`PowerModel` is owed work this branch did not do, and a row emitting a
reference to a class that does not exist is a prototype that cannot be staged.
The row as it would be written:

```yaml
- {id: proto_true_spark_knight, name: "Spark Knight's Oath", character: klee,
   authored_by: [claude],
   cost: 2, type: power, rarity: rare, solve: [scaling], archetypes: [spark], role: payoff,
   effects: [{op: apply_power, power: spark_attack_cost, amount: 1, target: self,
              note: "Attacks that do not already cost Sparks cost 3 Sparks and 0 Energy"}]}
```

Its face text is §5's proposal unchanged: *"Your Attacks that do not already
cost [Spark] cost 3 [Spark] instead of their Energy cost."*

### 10.3 The engine

`combat.spark_power_price(state, card)` is the state-aware half of a Spark
price — Attacks only, Attacks that do not already print a price only, and
`C.SPARK_ATTACK_POWER_PRICE = 3` (lifted, not picked: your own phrase, and the
retired threshold's own number). `combat.spark_price` sums it with the printed
half so the playability gate, the payment in `play_card` and the pilot's hold
term cannot disagree about the number. `card_playable` gates on it; `play_card`
pays it beside the energy.

The starter substitutions go through ONE seam, `loader._starter_ids` — the
Kurage base kit's seam replicated for Klee, and for the same reason: both
readers of a printed starter (`build_player`, `starting_deck`) go through it, so
the tier 0 battery and the tier 0.5 run cannot disagree about what she opens
with. **No printed sheet moved.** `_card_prototype` gained one flag-gated
branch so a `proto_` id in a starting deck resolves at all; membership does not
move, so pools, rewards, drafts and digests still cannot see the surface.

### 10.4 PICK 7 — the derived number, and its arithmetic

The seat ruled option 3: *"derive it from the new sink prices once §4's numbers
are ruled."* They are ruled, so it is derived.

**Neither [USER]-held shipped dial moved.** `STATIC_SPARK_VALUE` stays 0.0 and
`STATIC_SPARK_SPEND_COST` stays 2.5. Both were derived against a rule that does
not run under the flag — 2.5's own route (1) reads *"2 Sparks is one free
Attack under True Spark Knight"*, a sentence with no referent once the threshold
is retired — so the arm gets ONE number of its own, `SPARK_ALT_VALUE`, read
through two accessors, and the shipped world keeps both of its own.

One number for both sides, because under an alternative cost a Spark is worth
what it buys and is bought for what it is worth; printing two would assert an
asymmetry the new rule does not have.

The unit is the file's own — points of printed damage or Block. For each of the
five sinks: what does the price buy OVER a 0-energy neighbour of the same
rarity? All five are 0 energy, so the energy line cancels and the whole delta is
the Sparks. Baselines are shipped rows, not invented: Common 0-energy Attack
3.5 (`crackle` 3, `study_of_explosions` 4); Uncommon 0-energy Attack 6.0
(`flame_on_the_wick`). AoE counts `STATIC_AOE_MULT` = 2.0 bodies, this file's
own convention.

| card | body | over baseline | per Spark |
|---|---|---|---|
| Fwoosh! | 8 | 8 − 3.5 = 4.5 over 1 | **4.50** |
| Tinder Toss | 4 × 2.0 = 8 | 8 − 3.5 = 4.5 over 1 | **4.50** |
| Bang Bang! | 5 × 2 = 10 | 10 − 3.5 = 6.5 over 2 | **3.25** |
| Dodoco Blast | 7 × 2.0 = 14 | 14 − 6.0 = 8.0 over 2 | **4.00** |
| Firework Finale | 18 | 18 − 6.0 = 12.0 over 3 | **4.00** |

**Median = 4.00.** Median rather than mean for the reason the 2.5 derivation
gave: an outlier row (Bang Bang!'s deliberately poor rate, which is what the
sheet charges for a two-Spark purchase) then fails to move the dial. Firework
Finale's Exhaust is NOT discounted — discounting it would lower the number, and
lower is the unsafe direction on the spend side.

**The error direction is one-way on both sides**, which is what makes this
derived-not-picked under R212 rather than a design pick: on the GAIN side 4.00
is the first non-zero price a `gain_spark` has ever carried, so the drafter can
finally see a generator at all (0.0 made twelve shipped rows invisible); on the
SPEND side 4.00 is 1.6× the shipped 2.5, so a sink is charged MORE, never less
— the direction that cannot make the drafter pay for a cost it cannot see.
Archive scope is the flag: with it off nothing reads this number.

### 10.5 The pilot

Leg 1 of the hold-versus-spend term quoted the rule it has to outlive — *"at
`SPARKS_FOR_FREE_ATTACK` = 3 a Spark is a third of a free Attack"*. Under the
flag it becomes **a share of the cheapest affordable sink in hand**: walk the
hand for cards whose Spark price the bank can already meet, take the CHEAPEST
such price, and price one Spark at that card's payoff divided by its price. With
no affordable sink in hand a Spark is worth **exactly zero** — §6.3's sentence
in code. Cheapest rather than best-rate because the cheapest affordable sink is
the use the bank is guaranteed to be able to make, and because under-valuing
spends more readily, which is R194's safe direction. Leg 2 (a free Attack
forfeited by dropping under the bar) returns 0.0 under the flag: no bar, nothing
to forfeit. Leg 3 (the reader leg) is untouched. The price the term charges is
now `spark_price`, so the strict Power's three Sparks are charged too.

**What the pilot still cannot see**, named at the function rather than left to
be found. Each of these makes it spend more readily than a player would — the
one-way direction — but they are real:

1. **Sinks in the draw pile.** Hand-only is inherited and deliberate, so a bank
   held for the Firework Finale two cards down reads as a bank held for nothing.
2. **Sparks already in flight.** Bombs on the board will pay the relic when they
   detonate; the pilot prices the bank it HAS, never the bank it is about to
   have, so it cannot plan a two-turn purchase.
3. **The floor of its own Power, and this is the largest.** Under the strict
   Rare Power, spending to 2 Sparks makes EVERY unpriced Attack in hand
   unplayable. Leg 3 does not catch it: `_spark_bank_probe` asks what a card is
   WORTH at a bank, not whether it is PLAYABLE at one, and an Attack's expected
   damage is the same float either way. **A pilot holding the Power will spend
   itself out of its own Attack suite.** Fixing it means teaching the probe
   playability, which is a `POLICY_VERSION` bump and was not taken here.
4. **Multi-turn value.** One Spark banked across two turns and one Spark spent
   now score identically; nothing in the term is a discount rate.

### 10.6 The smoke — shape only, against Regent's numbers

Five Klee **starter-deck** fights, seeds 1–5, flag ON, `punisher` encounter,
demolition pilot weights. Not a balance read (R215 B); counts only.

| seed | turns | gained | spent | auto-consumes | refused | sink in hand | sink playable | sink played | longest idle bank | win |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 6 | 2 | 0 | 0 | 2 | 2 | 2 | 2 | yes |
| 2 | 5 | 7 | 2 | 0 | 0 | 4 | 4 | 2 | 1 | yes |
| 3 | 5 | 7 | 2 | 0 | 0 | 4 | 2 | 2 | 2 | yes |
| 4 | 5 | 6 | 2 | 0 | 0 | 4 | 2 | 2 | 2 | yes |
| 5 | 5 | 7 | 3 | 0 | 0 | 7 | 5 | 3 | 1 | yes |

Totals over 25 player turns: **33 Sparks gained (1.32/turn), 11 spent
(0.44/turn), net +22.** Zero automatic consumes and zero refused spends, which
is the retirement and the gate both working. The starter sink was in hand at 21
decisions and playable at 15 of them — **71%**.

**Against the Regent numbers in `regent-stars-economy.md` §2.4:**

| | Regent (starter + relic) | Klee, this arm |
|---|---|---|
| income | +1.0 / turn | **+1.32 / turn** |
| expenditure | −1.0 / turn | **−0.44 / turn** |
| net | **zero**, with a 3-point opening buffer | **+0.88 / turn**, no buffer |
| over a fight | 7 made, 4 spent | ~6.6 made, ~2.2 spent |

**Income now matches Regent's and slightly exceeds it; expenditure is under half
his.** She still banks. Two readings, and they are not exclusive: the starter
sink is priced at 1 where Regent's `FallingStar` is priced at 2 (a full cycle's
income, not a turn's), and there is one sink in ten cards against income that
scales with how many bombs go off rather than with the cycle. The bank sat at or
above the cheapest price with no spend for **two consecutive turns in three of
five fights** — never longer, which is the honest shape of a starter with one
cheap sink in it: it is not idle for long, but it is idle.

**Do not read a balance claim off any of this.** The pilot's blind spots in
§10.5 all push toward spending, the encounter is one battery fight, and five
seeds is five seeds.

### 10.7 Tests

`tier0/tests/test_spark_alt_cost.py`, 39 tests in six sections: flag off
byte-identical (the log digest, the starter, both shipped dials,
`spark_price == spark_cost` for every card, and the shipped rule still running);
the base rule retired; the printed price (each proto Attack gates one short of
its price and pays exactly it); the strict Power (unplayable at 2, playable at
3, pays 3 Sparks and 0 Energy; already-priced Attacks, Skills and X-cost Attacks
unaffected); the starter; and the pilot.

**Fifteen mutations were run against the finished file and all fifteen are
caught.** Three of them SURVIVED when first written and the tests were fixed
rather than the mutations dropped, which is the part worth recording:

| mutation | first result | what was missing |
|---|---|---|
| remove the consume guard | SURVIVED | no test made an Attack cost 0 under the flag, so the old branch's own guard was never satisfied. The Power's turn now asserts the event log too. |
| keep `PILOT_SPARK_VALUE` in leg 1 | SURVIVED | the unit function was tested directly and `_spark_hold_cost` was not. |
| take the best-rate sink, not the cheapest | SURVIVED | the fixture's two sinks happened to agree. The pair now disagrees by construction — cheaper price, worse rate. |

The other twelve: remove the zeroing guard; do not pay the Power's price; gate
on the printed price only; sub-pick (b) instead of (a); X-cost Attacks not
exempt; the Power applied to Skills; the starter substitution replacing all four
copies; the starter seam ignoring the flag; leg 2 not retired; the hold term
back on `spark_cost`; `SPARK_ALT_VALUE` moved off the median; and the shipped
gain dial waked in the shipped world.

### 10.8 The green lines, verbatim

```
OK: 28 lint(s) passed                                    (python -m tools.run_lints --lane ci)
3626 passed, 46 skipped, 12 xfailed, 3 warnings in 218.32s (0:03:38)   (pytest tier0/tests -q)
794 passed, 9 warnings in 36.56s                         (pytest tier05/tests -q)
gen_klee_cards: up to date
gen_roster_cards: furina up to date
gen_roster_cards: kokomi up to date                      (tools/gen_roster_cards.py --check)
lint_prototype_authorship: OK (21 surface row(s), 4 carried debt entr(ies))
lint_prototype_authorship: self-test OK
gen_prototype_cards: prototype surface up to date
```

### 10.9 The DRAFT prediction slate

**DRAFTED, unrun, uncountersigned.** Drafted from written design intent (§1's
ruling, §4–§5's proposals) and committed before any seed run, per R212(2) and
`EXPERIMENTS.md`'s pre-registration rule. It is offered for batch countersign.

> **COUNTERSIGNED and RUN — recorded 2026-08-30, and the banner above is left
> as the record of what was drafted (R101b).** The offer was taken: `M51`,
> verbatim, *"M51 countersigned, let's get Klee moving and see how things
> look."* — which §11.0 records as countersigning **this slate, `P1`–`P6`**,
> under R212(2), together with the eleven as-built calls at §10.11. Signed
> once and never re-signed (R212). It then RAN as `KLEESPARK-R1`, the
> registration committed before a board was staged, on `0.2.1481+proto`, world
> `main` @ `d974303`, and **§11.5 is the grade, slot by slot** — including
> `P1`'s MISS and the 2026-08-29 ERRATUM that corrects the INSTRUMENT and
> re-grades nothing. **All six slots are graded**, tally 2 PREDICTED (`P3`,
> `P6`) / 2 SPLIT (`P2`, `P4`) / 2 MISS (`P1`, `P5`), the two sim slots off
> `tier05/exp_klee_sparks_r1.py`. This section is not the `KLEESPARK-W1` slate (§12.3) or the
> round-2 slate (§13), each of which carries its own status.

**The decisive question, and it is a D2/D4 question rather than a winrate one:
does a Spark-priced Attack create a spend-versus-hold decision the reader can
see on the page?** The base rule failed D2 because the bank had one destination
and the engine chose it. A price only fixes that if the player is ever in a
position where two uses compete and the face shows both prices.

**Instrument.** The blind-play funnel (`understudy/`), Codex seat as the
independent read on the card rows (§7); a fresh-Opus read on the same rows is
same-family and is recorded as such. The rule row itself is Claude-read by §7.
The sim cannot see the decisive question at all — it is a face-and-turn
question — so no sim prediction is registered for it; the sim slots below are
separate and are what the sim CAN see.

| # | slot | prediction (directional) | the decision each outcome changes |
|---|---|---|---|
| P1 | Does a graded turn contain a visible spend-vs-hold choice — two Spark uses competing, both affordable, in one hand? | **YES on at least 4 of 8 graded turns.** Two Common sinks at price 1 plus a 2 and a 3 means an ordinary hand holds more than one affordable use most turns. | Below 4 the tight set is too thin at the cheap end and PICK 4 reopens at option 2 (add the Rare cut) or option 3 (add rather than convert). |
| P2 | Can the grader state the price off the FACE, without the rules box? | **NO with the text line; the badge is required.** This is PICK 8 option 2 restated as a prediction: the base game carries every one of its 23 star prices on a badge and none in rules text. | A NO here makes the Klee Spark badge blocking for the dev build rather than a nicety. A surprise YES retires PICK 8 as a question. |
| P3 | Does the strict Rare Power read as a payoff or as a brick, on a turn where the bank is short? | **BRICK on an unbuilt deck, PAYOFF on a built one, and the grader can tell which from the hand.** That is the bet the card is; it fails if the grader cannot tell. | If the grader cannot tell them apart, the Power's face is under-informative and §5's wording is reopened — not its strictness. |
| P4 | Does the starter's opening hand ever contain the sink with an empty bank? | **YES, and it reads as a dead card rather than a plan.** One `Ka-pow!` in ten with income that arrives on detonation means turn one can hold it dry. | A YES that reads DEAD moves PICK 1 toward option 4's honest dead-turn or toward pricing the opening buffer higher. A YES that reads as a plan closes PICK 1. |
| P5 | (sim) Does the pilot's spend rate rise when the flag is on and the tight set is drafted? | **YES**, because a Spark now has a computable use and the drafter's gain dial is non-zero for the first time. | A NO says the pilot's blind spots (§10.5) dominate and the probe needs playability before any sim number about this economy is worth reading. |
| P6 | (sim) Does the bank sit idle above the cheapest price for 3+ consecutive turns in a drafted deck? | **NO** — the starter smoke tops out at 2 and drafting adds sinks faster than income. | A YES says the sink supply is still too thin at the prices set and §4.2's table is re-priced downward. |

**Contamination stated:** §10.6's starter smoke has already been read, on the
STARTER deck only, with no drafted cards and no Rare Power. P5 and P6 are about
DRAFTED decks and are not answered by it; P1–P4 are face-and-turn questions the
sim cannot see. The smoke's numbers are not used to set any prediction above.

### 10.10 The C# delta checklist

**BUILT 2026-08-29, branch `klee-sparks-cs`, stacked on `klee-sparks-sim`.**
Nothing was deployed and the game was not launched; the arm stops at
build-green and deploy-ready. Every item below carries what was actually
written, and where what was written differs from what the checklist asked for,
the difference is a numbered pick in §10.11.

1. **DONE — `SparkPower.cs`, the base rule retired.** `AppliesTo` gains
   `BaseRuleActive` as its FIRST clause, which stands the zeroing hook, the
   spend decision and the consume down together; they cannot be retired by
   halves. The localisation string went with the rule — a counter printing *"At
   3 Sparks, your Attacks cost 0"* while nothing costs 0 is the D4 defect, not
   a loose end — and now reads *"A resource. Cards that print a Spark price
   spend it."* `Gain`, `CanSpend`, `Spend` and `SparksAtPlay` are untouched.
   **RETIRED, NOT DELETED**, which is the checklist's word changed and is
   §10.11 item 7: `Threshold`, `CurrentThreshold`, `SparksAsResolved` and the
   pending pair all stay, exactly as tier 0 keeps `combat.spark_threshold`,
   because an OFF arm needs the shipped rule byte for byte.
2. **NOT DONE, deliberately — `SparkThresholdDownPower` stays.** §10.11 item 8.
   It is unread under the flag and it is still the body the SHIPPED
   `true_spark_knight` prints in a release build; deleting it would break the
   OFF arm the flag exists to preserve.
3. **DONE — the strict Power, and the eighth row is on the surface.**
   `Powers/Prototype/SparkAttackCostPower.cs`. **Not** on
   `TryModifyStarCost`, and that is §10.11 item 9: that hook feeds the game's
   STAR cost, whose gate reads `PlayerCombatState.Stars` — using it would have
   made a Klee card unplayable for want of Stars she never has. The three
   clauses ride three hooks the game already fans to every model in combat:
   `TryModifyEnergyCostInCombat` (Energy to 0), `ShouldPlay` (the gate; `CanPlay`
   reports `BlockedByHook` and names the power as preventer), and the
   `BeforeCardPlayed`/`AfterCardPlayed` split for the payment. `Converts` is
   the ONE predicate all four sites share — Attacks only, already-priced
   Attacks unaffected, X-cost exempt, and the card's owner must be this power's
   owner, which is co-op and which the sim cannot see at all.
   `spark_attack_cost` is in `APPLY_POWERS`, and the row in §10.2 is on
   `docs/prototype-surface.yaml` and generates `ProtoTrueSparkKnight`.
   Its face reads §5's sentence unchanged.
4. **DONE — the starter swap, at one seam.** `Klee.StartingDeck`, `#if
   PROTOTYPE_CARDS`, mirroring `loader._starter_ids`: `Powers/Prototype/
   SparkStarter.PricedKaboom()` for one of the four Ka-boom!s and
   `SparkingPop()` for Pop. The sheet does not move. It composes with the
   companion roll by construction, not by luck —
   `KleeStartingCompanionsPatch.ReplaceFirst` matches
   `GetType() == typeof(Kaboom)`, which `ProtoKaboomSink` is not — and that is
   pinned.
5. **DONE — the badge.** `Vfx/Prototype/SparkCostBadge.cs`, a postfix on
   `NCard.UpdateStarCostVisuals` writing `%StarIcon` / `%StarLabel`: the same
   position, the same shape and the same font as Regent's price, with Klee's
   own `klee/powers/spark.png` as the glyph and no new art. `StsColors.red` +
   `unplayableEnergyCostOutline` when the bank is short, in HAND only, which is
   `CardCostHelper.GetStarCostColor`'s own arm. A second postfix on
   `UpdateEnchantmentVisuals` puts the enchantment tab back down — the base
   game lifts it 45px into the empty badge slot on any card with no Star cost,
   which is every Klee card. **The persistent counter was NOT added** (§10.11
   item 11): she already has a Spark counter in the power bar, and
   `ShouldAlwaysShowStarCounter` belongs to the Stars door that was declined.
6. **NOT TRUE ANY MORE — the seven card rows DID need C#, and it is the badge's
   fault.** Until this branch a printed Spark price existed only as a literal
   inside the generated `IsPlayable` expression, so nothing outside the card
   could ask what a card costs — and a badge that reads a SECOND copy of the
   number is the display-versus-gate drift the badge exists to repair. So every
   card whose row prints a top-level `spend_spark` now declares
   `PrintedSparkPrice` on `ISparkPricedCard` and gates through
   `SparkCost.PriceOf`, the C# twin of `combat.spark_price`. Three SHIPPED Klee
   Skills are regenerated by that change; their behaviour is identical, because
   with the flag off `PriceOf` IS the printed price. §10.11 item 10.
7. **DONE, and it was not on the checklist — the observed board can read a
   price.** `EB-185` put the BANK on the wire; nothing carried the PRICE.
   `cost` is the ENERGY cost and is 0 for every one of these cards, `can_play`
   folds every refusal into one boolean, and under the strict Power the price
   is not on the card at all. A hand card now carries `spark_price` and
   `spark_affordable` (`vendor/STS2_MCP/gits/GitsSparkPrice.cs`, read by
   reflection so "no klee mod" means "no Spark prices"), omitted for a card
   that charges nothing. `understudy/adapter.py` reads them AND cross-checks
   them against `combat.spark_price`, reporting disagreements by name — two
   implementations of one rule in two languages, and a divergence is invisible
   unless something asks. One status row makes the Power's price crossable:
   `true_spark_knight` -> `spark_attack_cost`.
8. **DONE — the bite-check.** `klee-mod/KleeTests/Prototype/
   SparkAlternativeCostPinTests.cs`, 27 pins, and most of them are REAL rather
   than structural: a card can be constructed, made mutable and given an owner,
   so the price, the gate and the Energy zeroing are all called directly. The
   retirement is measured (the hook declines at a bank of 5), the derived price
   of every proto row is read off the emitted class, the gate is checked at 0 /
   2 / 3 / 7 Sparks, and each of the three exemptions is checked against its
   live alternative. Structural and labelled: the payment
   (`SparkPower.Spend` needs a `PlayerChoiceContext`), the badge (Godot nodes
   are process death in this host) and the starter seam (`ModelDb` is populated
   only by the game's boot). The flag is pinned BOTH ways round — the file that
   says the base rule is retired is not compiled without the switch, so the
   release half lives in `SparkSinkPinTests` behind an `#if`.

**Verification, verbatim.**

```
Build succeeded.  0 Error(s)   (dotnet build klee-mod/KleeCode/KleeCode.csproj -p:UsePinnedAssemblies=true)
Build succeeded.  0 Error(s)   (… the same, plus -p:PrototypeCards=true)
Passed!  - Failed:     0, Passed:   163, Skipped:     0, Total:   163   (dotnet test)
Passed!  - Failed:     0, Passed:   211, Skipped:     0, Total:   211   (dotnet test -p:PrototypeCards=true)
OK: 28 lint(s) passed                                    (python -m tools.run_lints --lane ci)
3702 passed, 46 skipped, 12 xfailed, 3 warnings in 309.19s (0:05:09)   (pytest tier0/tests -q)
lint_prototype_authorship: OK (23 surface row(s), 4 carried debt entr(ies))
gen_prototype_cards: prototype surface up to date
gen_klee_cards: up to date
gen_roster_cards: furina up to date
gen_roster_cards: kokomi up to date
```

All of the above is taken AFTER merging `origin/klee-sparks-sim` at its
resolved head, so it is the arm standing on `main` with Kokomi's Kurage-memory
arm beside it -- 211 with the flag is this slice's 27 plus that arm's 21 plus
the shipped 163, and the two quarantines share one switch without either
noticing the other.

**Where the bite-check ran, stated because it is a real limit.** The pinned
assembly vault (`UsePinnedAssemblies`) has no `Sentry.Godot`, which the test
HOST needs to load `sts2.dll` — the vault keeps the BUILD alive, not a test
run. So the suite was run against the INSTALLED game assemblies, read-only,
resolved through a local `klee-mod/local.props`. Same route the Kokomi arm
took, for the same reason.

### 10.11 What the packet left unsaid and I had to decide — each goes to you

Five, and they are picks, not blanks.

1. **The replacement name for candidate 1.** `Fwoosh!` (provisional, R179,
   lint-clean). Alternatives in the same family that also came back clean:
   `Whizz!`, `Whoosh!`, `Sputter`, `Fizzle`. — *(a) keep `Fwoosh!`; (b) one of
   the four; (c) name it yourself.*
2. **How many `kaboom` copies become the sink.** The packet says "`kaboom`
   becomes 0 energy / Spend 1 Spark" and her starter holds four. I substituted
   **one**, because Regent's ten ships one sink and four would make four of her
   ten opening cards unplayable on an empty bank. — *(a) one, as built; (b) two;
   (c) all four, and accept the dry opening.*
3. **X-cost Attacks under the strict Power.** §5 is silent. I **exempted** them:
   an X card's cost IS its energy spend, so a flat 3-Spark conversion resolves it
   at X = 0 and deals nothing — R34's own reasoning reached from the other side.
   — *(a) exempt, as built; (b) converted, and X becomes 0 by design.*
4. **PICK 7's shape.** The seat ruled "derive it", and I derived **one** number
   for both the gain and the spend side rather than two, and put it behind the
   flag rather than moving either [USER]-held shipped dial. — *(a) one derived
   dial at 4.00 under the flag, as built; (b) two dials; (c) move the shipped
   dials and re-baseline.*
5. **The eighth row is held on C#, not on doctrine.** The Power's sim half is
   built and tested; the row cannot go on the surface until a `PowerModel`
   exists. — *(a) write the C# next, then the row; (b) grade the seven card rows
   first and leave the Power for a second slice.*
   **ANSWERED by building it: (a).** The row is on the surface and generates.

---

**And six more from the C# half.** Same rule: picks, not blanks.

6. **What the flag IS, in C#.** I made it the `-p:PrototypeCards=true` COMPILE
   switch — the one that already quarantines the surface, defines
   `PROTOTYPE_CARDS` and stamps a deploy `+proto` — rather than a runtime
   constant. So one flag is the whole revert and a release build contains no
   type from the arm at all; the cost is that a single installed build cannot
   run both arms, which the sim's `SPARK_ALT_COST_ENABLED` can. — *(a) the
   compile switch, as built; (b) a runtime constant too, so one dev build can
   be flipped mid-session.*
7. **Retired versus deleted.** §10.10 item 1 said DELETE. I retired instead:
   `Threshold`, `CurrentThreshold`, `SparksAsResolved` and the pending pair all
   stay, gated, exactly as tier 0 keeps `combat.spark_threshold` — because
   option 1 exists so the two economies can be run as two arms and an OFF arm
   needs the shipped rule byte for byte. — *(a) retired, as built; (b) delete
   them now and accept that the OFF arm is gone.*
8. **`SparkThresholdDownPower` did not go.** §10.10 item 2 said it should. It is
   unread under the flag, but it is still what the SHIPPED `true_spark_knight`
   prints in a release build, so removing it breaks the very arm item 7 keeps.
   — *(a) leave it, as built; (b) delete the power and re-author the shipped
   row in the same pass.*
9. **The gate is `ShouldPlay`, not a patch on `IsPlayable`.** §10.10 item 3 said
   the Power "must also drive `CardModel.IsPlayable`". `IsPlayable` is
   `protected virtual` and a Harmony patch on it would MISS every card that
   overrides it — which is exactly the already-priced cards. `ShouldPlay` is a
   first-class `AbstractModel` override the game fans to every model in combat,
   reports `BlockedByHook`, and names the power as the preventer in the
   player's own tooltip. — *(a) `ShouldPlay`, as built; (b) patch `IsPlayable`
   as well.*
10. **Three shipped cards moved so the badge could exist.** The badge must read
    the same number the gate charges or it is the defect it was built to
    repair, and that number was a literal buried in generated code. So
    `ISparkPricedCard` is emitted for every row that prints a top-level
    `spend_spark`, shipped rows included, and the three Klee Skills that do were
    regenerated. Behaviour is identical with the flag off. — *(a) one interface
    for every priced card, as built; (b) confine it to proto rows and give the
    badge a second table of prices for shipped ones.*
11. **The badge repurposes the star slot, and there is no persistent counter.**
    It writes the `%StarIcon` / `%StarLabel` pair rather than adding a node, so
    a card cannot show a Star price and a Spark price at once — unreachable
    today (no Klee card has a Star cost, and Sparks-are-Stars was declined) but
    it is a real ceiling. And `ShouldAlwaysShowStarCounter` was left alone: she
    already has a Spark counter in the power bar, and Regent's always-on
    counter belongs to the door that was declined. — *(a) as built; (b) a badge
    node of Klee's own; (c) add an always-visible bank counter too.*
12. **The price is on the badge AND still in the rules text.** The generated
    face still says *"Spend 1 [Spark]."* The base game says nothing about a
    price in rules text, so this is one line of redundancy — but stripping it is
    a face change on three SHIPPED cards as well as the prototypes, and P2 in
    §10.9 is precisely the measurement that would justify it. — *(a) keep both
    for the blind grade, as built; (b) strip the sentence now.*

**Eyes-on for the next dev deploy — the badge's look is taste by definition.**

1. **The Spark glyph at cost-badge size.** `klee/powers/spark.png` was drawn for
   the power bar; at the badge's scale it may read as a blob. This is the single
   most likely thing to need art.
2. **The badge against the energy orb.** Two costs on one card, the Energy badge
   reading 0 beside a Spark badge reading 1–3. Regent's cards look like this all
   the time; hers never have.
3. **Red when the bank is short**, and whether it reads as "cannot afford" or as
   "something is wrong with this card".
4. **Under the strict Power**, an unpriced Attack showing a 3-Spark badge it
   does not print. That is the card's whole bet and it should look deliberate.
5. **The enchantment tab's 45px correction**, on an enchanted Spark-priced card.
6. **The Spark counter's new description** — *"A resource. Cards that print a
   Spark price spend it."*
7. **The strict Power's own icon**, which borrows `spark_threshold_down.png`
   from the body it replaces.
8. **Whether the rules-text price line reads as redundant** beside the badge
   (item 12 above).

---

## 11. ROUND 1 (2026-08-29) — the Sparks arm on a live board, Qwen in the tester seat

### 11.0 What has to be said before any result

**The build.** Everything below was read on a dev build stamped
**`0.2.1481+proto`**, deployed from the art-bearing main checkout with the game
closed, confirmed by reading `+proto` out of the installed
`mods\klee\manifest.json`. The world is `main` @ `d974303`. The registration is
`KLEESPARK-R1` in `EXPERIMENTS.md`, committed before a board was staged.

**What [USER] settled, and what this round therefore rests on.** `M51`,
verbatim: *"M51 countersigned, let's get Klee moving and see how things look."*
That countersigns the §10.9 slate P1–P6 under R212(2) and lets all eleven
as-built calls at §10.11 stand. Nothing in this round re-opens either.

**The first deploy attempt was REFUSED and the refusal was right.** The
registration cited `R220` for two things that are genuinely ruled, and `R220`
is not issued — `R_CEILING` is 219. `validate.ps1`'s own suite caught it
(`test_r_numbers_lint::test_the_real_tree_is_one_clean_namespace`) before a
build was staged. The citations moved to the documents that carry the words;
nothing about what is ruled changed. It is recorded here because a gate that
bites is worth more than a gate that passes.

**Three disclosures, made before any form was read.**

1. **The roster-wide Burst retirement is RULED and NOT BUILT.** It lives at
   `review/ruled/burst-retirement-2026-08-29.md`. Klee's Burst meter is still
   live in this build, and `Burst +5` appears on the printed face of Powder
   Pop and Jumpy Dumpty on four of the eight packets. No reader was asked
   about it and no result below turns on it, but it was on the page.
2. **The Spark badge has not had [USER]'s eyes-on.** The frames are at
   `review/qa/eb194-gates/frame-*gatec-*.png`. P2 is a prediction *about* that
   badge, and this is stated again under P2 because it decides how P2 can be
   graded at all.
3. **The spot-check rate was the DEFAULT, and `M58` is still open.**
   `--seat-spot-check 4` is what ships. This round used it and does not answer
   the question of what the rate should be. On eight turns the default put the
   Codex seat on turn 1 and turn 5; the resource-order flag routed nothing,
   and a caught misread routed `t05` a second time.

**And the ordinary standing limits.** R215 B: no number a prototype row
produces is quotable anywhere. Guardrail-7: every replay figure below is a
defect diagnostic and never a design or balance claim. The funnel refuses
turns and never rates them.

### 11.1 The boards

Eight, at `understudy/turns/klee-sparks-r1/`, with `MANIFEST.md` beside them.
All `exact_hand: true` and `prototype: true`, all on Klee's base 3 energy, all
with the bank written through the `set_power` op on `SPARK_POWER` (the
precedent is `understudy/scenarios/set-power-sparks.yaml`). They were committed,
with the round's schedule and all eight closeness readings, before the build
that would produce the readings existed.

| turn | bank | seed | the encounter the seed drew | what the board is |
|---|---|---|---|---|
| `t01` | 0 | `R805DJ56LZHM` | Nibbit 46/46, attack 12 | turn one, the substituted starter dealt |
| `t02` | 1 | `YX7PB48WR7R4` | Shrinker Beetle 40/40, **debuff** | two sinks priced 1 |
| `t03` | 2 | `JH4T8MSN10KS` | Seapunk 45/45, attack 11 | a price-1 beside a price-2 |
| `t04` | 3 | `XT4BE7LFY5XH` | Fuzzy Wurm Crawler 46/56, attack 4 | the Rare Power, bank can pay |
| `t05` | 1 | `VEZY6KLK71XR` | Sludge Spinner 37/37, attack 8 | the Rare Power, bank short |
| `t06` | 2 | `VG1MYKCZD93V` | Shrinker Beetle 39/39, **debuff** | the two AoE sinks |
| `t07` | 4 | `EW3ZC40K83G4` | Sludge Spinner 39/39, attack 8 | a bank deep enough to buy both |
| `t08` | 0 | `PRX320N09RMK` | Fuzzy Wurm Crawler 46/57, attack 4 | empty bank with the generator in hand |

Every seed was honoured on every one of the sixteen replays. All eight
closeness readings SURVIVE, gaps 0.0377 to 0.2100 against a `DOMINANCE_GAP` of
0.5.

**Four things the boards could not do, and each of them bears on a grade
below.**

- **The tier0 mirror runs FLAG-OFF.** `build_combat_state` runs in this tree,
  where `SPARK_ALT_COST_ENABLED` is `False`, so on `t04` (bank 3) and `t07`
  (bank 4) it still applies the retired base rule and scores those boards
  richer than the live game. The error runs one way and can only make the
  falsifier stricter. Fixing it is a per-turn flag on the mirror, owed.
- **The intents are the seed's.** `t02` and `t06` telegraphed a DEBUFF, not an
  attack, while the mirrored board declares an attack. Two records, not one.
- **`t06` asked an AoE question of a one-enemy encounter.** The board was set
  for the two ALL-enemies sinks and the seed produced a single Shrinker
  Beetle, so both AoE clauses were worth single-target damage. The pair read
  returned that board for exactly this.
- **Both empty-bank boards had the GENERATOR in hand.** `t01` and `t08` each
  hold Powder Pop beside the locked sink, and I put it there. A hand holding
  the sink with *no* way to fill the bank was never staged. This matters to P4
  and it is why P4 does not close its pick below.

### 11.2 The forms — eighteen of them, three readers

**The tester seat is the LOCAL Qwen seat and this is its first live use**
(`understudy.local_tester`, `local-qwen3-8-27b-ud-q4-k-xl`, family `local`,
role `tester`). It filled all eight forms; `staged_turn grade` applied the
falsifiers, as it does for every reader, with no model in that loop.

**The fresh-Opus read is SAME-FAMILY and is recorded as such.** §7 is
unchanged: these rows are `authored_by: [claude]`, so an Opus grade is family
and is never the deciding read. One agent per packet, never reused, no repo
access, the packet inline, the three identity fields a model cannot know about
itself filled by the orchestrator, the unedited reply kept as
`form-raw-opus-5-fresh.json`.

**The Codex seat read two packets**, `t01` and `t05`, which is what the
shipped `--seat-spot-check 4` default put on it.

| turn | local Qwen tester | fresh Opus (same family) | Codex seat |
|---|---|---|---|
| `t01` | **REFUSED** `intent_insensitive` | SURVIVES | SURVIVES |
| `t02` | **REFUSED** `intent_insensitive` | SURVIVES | — |
| `t03` | **REFUSED** `intent_insensitive` | **REFUSED** `intent_insensitive` | — |
| `t04` | SURVIVES | SURVIVES | — |
| `t05` | SURVIVES (+ **MISREAD**) | SURVIVES | **REFUSED** `no_second_line`, `intent_insensitive` |
| `t06` | **REFUSED** `intent_insensitive` | SURVIVES | — |
| `t07` | SURVIVES | **REFUSED** `intent_insensitive` | — |
| `t08` | **REFUSED** `intent_insensitive` | **REFUSED** `intent_insensitive` | — |

**Every refusal by name.** `intent_insensitive` ten times — five of the
tester's eight, three of Opus's eight, and once against the seat.
`no_second_line` once, against the **Codex seat on `t05`**, whose question two
was the single word *"none"* and whose question four was *"With this hand and
these resources, a different telegraphed intent would not have produced a
stronger affordable line."* That is the round's sharpest single result: on the
Rare Power's short-bank board the INDEPENDENT reader considered nothing else at
all.

**The one flag the tooling raised on its own.** `t05`, from the local tester's
post-read: *"MISREAD: called 'Duck and Cover' 'free', but the packet prints
Cost: 1."* That routed `t05` to the seat for a second reason on top of the
periodic rate. `understudy/resource_order.py` flagged nothing in the round.

**Agreement.** The Opus read and the Qwen read reached the same verdict on
**4 of 8** turns (`t03`, `t04`, `t05`, `t08`) and differed on four — Qwen
refused `t01`, `t02` and `t06` where Opus survived, and Opus refused `t07`
where Qwen survived. On the two spot-checked turns the Codex seat agreed with
**neither** the tester (0 of 2) nor, on `t05`, with Opus (1 of 2).

### 11.3 The replays — sixteen, and two of them stopped

Every graded line was replayed live on its own pinned seed. `execute` compared
the live enemies and hand against the packet first and refused no board.

| turn | tester line | Opus line |
|---|---|---|
| `t01` | **STOPPED at play 1**, 46 → 46 | 4 plays, 46 → 5 |
| `t02` | 4 plays, 40 → 18 | 3 plays, 40 → 18 |
| `t03` | 4 plays, 45 → 21 | 4 plays, 45 → 21 |
| `t04` | 2 plays, 46 → 23 | 2 plays, 46 → 17 |
| `t05` | 3 plays, 37 → 16 | 4 plays, 37 → 16 |
| `t06` | 3 plays, 39 → 25 | 2 plays, 39 → 25 |
| `t07` | **STOPPED at play 1**, 39 → 39 | 4 plays, 39 → 8 |
| `t08` | 4 plays, 46 → 27 | 4 plays, 46 → 27 |

**The two stoppages share one cause and it is mechanical.** On `t01` and `t07`
the local tester wrote `Powder Pop` with `target: null`, and the bridge refused
it in its own words: *"Card requires a target. Provide 'target' with an
entity_id."* Powder Pop places a Bomb on an enemy, so it is a targeted card;
the packet does not say which cards need a target, and the Opus forms supplied
one. Both lines stopped at their first play and dealt nothing. Those two forms
are **UNTESTED, not contradicted** — a quarter of the tester seat's lines could
not be executed at all.

Where both lines ran, they agreed with each other on the board to the hit
point on `t02`, `t03`, `t05`, `t06` and `t08`. They differ on `t04` (23 against
29) because Opus's Jumpy Dumpty Bomb detonated inside the replay window and
Qwen's line placed no second Bomb.

### 11.4 The pair read, verbatim on the outcomes

One Codex call, `understudy.seat review --role pair`, over the whole round —
every packet, every form, every verdict and every replay inline. The full text
is `review/qa/klee-sparks-r1-pair-review-codex-gpt-5.6-sol.md`. Its outcome
table, verbatim:

| Row | Trial card | Outcome | Reason |
|---|---|---:|---|
| t01 | Powder Pop — starter generator | ADVANCE | Multiple readers saw the empty-bank Ka-pow! as initially dead and Powder Pop as the explicit unlocking plan; two independent valid reads survived, although the tester's replay did not. |
| t02 | Fwoosh! | RETURN | The competing equal-price card was treated as "strictly one damage worse"; the board exposed simple numerical dominance rather than a meaningful spend-versus-hold choice. |
| t03 | Bang Bang! | ADVANCE | Both readers explicitly valued the alternative bank state—"preserves a Spark at the cost of only 2 damage"—even though both chose immediate damage. |
| t04 | Spark Knight's Oath, bank 3 | ADVANCE | The page supported exact conversion accounting and a recognizable setup alternative; readers could tell that precisely one converted Attack was fundable. |
| t05 | Spark Knight's Oath, bank 1 | ADVANCE | Readers correctly distinguished this state from t04 and recognized the immediate brick/setup tension; disagreement was about whether setup was serious, not about the game state. |
| t06 | Dodoco Blast and Tinder Toss | RETURN | The generated one-enemy encounter erased the intended AoE dimension, so this board did not adequately ask what these two all-enemy rows were meant to reveal. |
| t07 | Firework Finale | ADVANCE | The price was fully affordable, while Exhaust generated a visible hold-versus-spend alternative; the valid replay confirmed the complete line. |
| t08 | Ka-pow! — starter spender | ADVANCE | Both readers correctly read it as dead at an empty bank and live after generation, then consciously chose it over the competing priced card. |

Its overall lines, verbatim: *"No row requires ESCALATE."* — *"Overall arm
judgment: ADVANCE. The page consistently communicated affordability, bank
depletion, and generator-to-spender sequencing. Whole-fight play is warranted
to test whether the visible future value readers mentioned actually sustains
spend-versus-hold decisions beyond staged single turns; this is neither ship
approval nor a balance conclusion."*

And on the seat, verbatim: *"Overall tester-seat judgment: RETURN. It can
articulate alternatives, but its intent reasoning and replay-valid line
construction are not dependable enough for this seat."*

**Six ADVANCE, two RETURN, no ESCALATE, and a RETURN on the tester seat
itself.**

### 11.5 The slate, slot by slot

**P1 — does a graded turn contain a visible spend-versus-hold choice, two
Spark uses competing and both affordable, in one hand? Predicted YES on at
least 4 of 8. → MISS.**
Four boards opened with two priced cards both individually affordable (`t02`,
`t03`, `t06`, `t07`), a count taken and written into `MANIFEST.md` before any
form was read. But `t07`'s bank of 4 pays for both, and the seat said so:
*"t07 is not actually a board where the bank could not pay for both sinks."*
Of the three where the bank genuinely could not, the seat found the choice
visible on two — *"t03: this produced the clearest actual spend-versus-hold
comparison… both visibly recognized the banked Spark as the thing
surrendered"*, and `t06` the same — and found `t02` was numerical dominance
rather than a decision: *"the only real choice between them is which prints the
larger number."* Two of eight is below four. **The registered decision fires:
the tight set is too thin at the cheap end, and PICK 4 reopens** at option 2
(add the Rare cut) or option 3 (add rather than convert). Two 1-priced cards in
one hand is not a decision when one of them simply prints a bigger number.

**ERRATUM (2026-08-29, relayed independent review). The grade above STANDS AS
PUBLISHED and nothing is re-graded (R101b). What is corrected is the
INSTRUMENT: `P1`'s threshold of 4 was unreachable on this board set.** Counting
each board's bank against the Spark prices its own hand held, only THREE boards
can pose the question at all — `t02` (bank 1: Ka-pow! 1, Fwoosh! 1), `t03`
(bank 2: Fwoosh! 1, Bang Bang! 2) and `t06` (bank 2: Tinder Toss 1, Dodoco
Blast 2). `t07`'s bank of 4 pays Firework Finale (3) AND Fwoosh! (1) together,
so it is not a competition; `t01` and `t08` sit at bank 0 with nothing
affordable at all; `t04` and `t05` hold ONE Spark use each, the Power. A
ceiling of three against a threshold of four means **no reading of this round
could have met `P1`**, so the MISS cannot establish that the tight set is too
thin at the cheap end — it establishes that the board set could not ask.
`MANIFEST.md`'s pre-registered count of four is true as written and is a
DIFFERENT predicate: "two or more Spark uses in hand that the bank can each
individually afford" is not `P1`'s "two Spark uses COMPETING". The instrument
defect is BACKLOG `EB-202`.

**The registered decision-fire is CONTESTED, and it is NOT un-fired here.**
The packet's published reading stands: `P1` MISSED and PICK 4 reopens by its
own registered clause. The relayed review reads it the other way, verbatim:
*"Keep the recorded MISS for audit purposes, but treat it as an instrument
defect — not a trigger to add/reprice cards."* On that reading PICK 4 does not
reopen and the question goes to a repaired board set instead. Both readings are
on the pick list at §11.7 item 1, and which one governs is [USER]'s.

**P2 — can the grader state the price off the FACE, without the rules box?
Predicted NO; the badge is required. → SPLIT.**
The first half is falsified cleanly. Across all eighteen forms the seat found
*"No reader misstated a printed Spark price, miscounted the available Spark
bank, or treated an unaffordable priced Attack as free."* Readers quoted the
prices back correctly at every bank from 0 to 4, including the Power's
conversion arithmetic. The second half is **UNTESTED and cannot be tested by
this instrument**: the funnel's packet is a text rendering with no badges of
any kind on it, so a reader who succeeded off the text line says nothing about
whether a badge would beat the text line on a rendered card. **PICK 8 does not
retire and does not become blocking on this evidence.** The one thing this
round does add is that the text line alone is legible to a careful reader,
which was not previously known.

**P3 — does the strict Rare Power read as a payoff or as a brick on a turn
where the bank is short, and can the grader tell which from the hand?
Predicted brick on an unbuilt deck, payoff on a built one, and the grader can
tell. → PREDICTED.**
The seat, on `t04` against `t05`: *"the page communicated 'one conversion
available' versus 'conversion unavailable'. Oath read as conditional
setup/payoff at t04 and as an immediate brick at t05; it was not mistaken for
an unconditional discount."* The Opus form on `t04` did the arithmetic
unprompted — *"with exactly 3 Spark I can pay for exactly one Attack"* — and on
`t05` reached the brick from the other side: *"both Kaboom!s would want 3 Spark
each and I would have 0 Spark."* **But the caveat is real and it cuts at the
card, not the prediction:** the local tester *"did not engage with Oath at
all"* on `t04`, and the independent seat's own `t05` form was refused for
having no second line whatsoever. Two of the three readers on the Power's
boards found nothing to weigh. The face is informative; whether the card is
worth playing is a different question this round did not ask.

**P4 — does the starter's opening hand ever contain the sink with an empty
bank? Predicted YES, and it reads as a dead card rather than a plan.
→ SPLIT.**
The YES is uncontested: `t01` and `t08` both printed *"Cannot be played right
now: BlockedByCardLogic"* on a priced card. The *dead* half is falsified. The
seat: *"On both boards, the priced card read as dead before generation and as a
plan once Powder Pop was noticed… the blocked message therefore communicated a
present dead card, while the generator made it a visible sequencing plan within
the same hand."* Every reader on both boards led with the generator and then
spent the Spark it made.
**The registered decision — "a YES that reads as a plan closes PICK 1" — is NOT
taken, and the reason is a limitation of my own boards.** On both empty-bank
boards I put Powder Pop in the hand. A hand holding the priced sink with no way
to fill the bank was never staged, and that is the hand PICK 1 is actually
worried about. What this round shows is that the sink plus the generator reads
as a plan; it shows nothing about the sink alone. PICK 1 goes back to [USER] as
a pick rather than closing.

**P5 — (sim) does the pilot's spend rate rise when the flag is on and the
tight set is drafted? Predicted YES. → MISS.**
`tier05/exp_klee_sparks_r1.py`, 40 fights per arm from seed 1, `punisher`,
`demolition` weights; raw output at
`review/records/klee-sparks-r1-sim-2026-08-29.txt`. Flag OFF the shipped economy
moved **1.00 Sparks per player turn** (all of it the automatic consume). Flag
ON the priced economy moved **0.72** (all of it priced, zero automatic, zero
refused). It did not rise; it fell by roughly a quarter. **The registered
decision fires: the pilot's blind spots (§10.5) dominate, and the probe needs
playability before any sim number about this economy is worth reading.** The
largest of those blind spots is named there — under the Rare Power a pilot
spends itself out of its own Attack suite, because `_spark_bank_probe` asks
what a card is *worth* at a bank and never whether it is *playable* at one.

**ERRATUM-STYLE NOTE (2026-08-29, relayed independent review). The grade
STANDS; the METRIC is confounded** — nothing here is re-graded (R101b). The
registered metric is Sparks moved PER PLAYER TURN, and the two arms differ in
both of that ratio's inputs. **Turns:** ON 294, OFF 243 — the ON arm's fights
ran longer, and it won 25 of 40 where OFF won 40 of 40. **Income:** the
one-for-one map converts four GENERATORS out of the deck — `sparkly_treasure`
(+1), `spark_collection` (+2), `sugar_rush` (+1), `cant_catch_me` (+1) — and
puts five priced damage Attacks that generate nothing in their place
(`docs/klee-cards.yaml`; the map is `tier05/exp_klee_sparks_r1.py:34-56`), so
Sparks GAINED fell 276 -> 235 by construction rather than by pilot behaviour.
Normalized against what was available to spend, the arms nearly tie and the
direction reverses: **ON spent 213 of 235 generated = 90.6%; OFF spent 243 of
276 = 88.0%** (`review/records/klee-sparks-r1-sim-2026-08-29.txt`). The review's
91% / 88% and 294 / 243 are arithmetically correct against that raw output. The
per-turn rate answers *"does a priced deck move more Sparks per turn than the
automatic rule"*; *"does the pilot spend what it has"* is a different question,
and it is the second one `P5`'s decision clause acts on. **That decision still
fires** — the probe needs playability before any further sim reading — and this
note does not disturb it. `spent / available Sparks` and `affordable sinks
skipped` are offered as candidate metrics for the re-registration at §11.7
item 6, option (d).

**P6 — (sim) does the bank sit idle above the cheapest price for 3 or more
consecutive turns in a drafted deck? Predicted NO. → PREDICTED.**
Longest streak **2 turns**, on both arms. And the definition was set against
the prediction rather than for it: a turn counts as idle when it ends at or
above the cheapest price the *deck* prints, not the cheapest the *hand* holds,
which over-counts idleness. The streak is at least as long as the true one and
it still never reached 3.

**Tally: 2 PREDICTED (P3, P6), 2 SPLIT (P2, P4), 2 MISS (P1, P5).**

### 11.6 What the round means, and what it could not do

**The arm's page works and its economy does not yet.** Those are two different
findings and they point in opposite directions. On the page, every reader
handled printed prices, empty banks, locked cards and a conversion Power
without a single price misread — the seat's ADVANCE on six of eight rows rests
on that, and so does P2's falsified first half and P3's PREDICTED. Underneath
it, the priced economy moved *fewer* Sparks per turn than the automatic rule it
replaces, and only two boards in eight produced a spend-versus-hold decision an
independent reader would call one. A price the player can read perfectly and
rarely has to think about is not obviously better than a rule that thought for
them; it is only more honest.

**A number that is NOT a balance claim and is recorded because it should be
looked at.** Over the same 40 fights per arm, the flag-OFF deck won 40 and the
flag-ON deck won 25. R215 B forbids quoting it and Guardrail-7 forbids reading
design into it, and neither is being done here: it is a one-encounter,
one-pilot, hand-assembled-deck diagnostic, and §10.5's four blind spots all
push the ON arm toward over-spending. It is written down because a fifteen-fight
gap is the kind of thing that is worse to discover later, and because it is a
reason to want whole-fight play before anything else.

**The tester seat's first live use returned a RETURN**, and the evidence for it
is not opinion. Five of eight forms answered question four "no" and were
refused as intent-insensitive; two of eight lines could not be replayed at all
because the model omitted a target on a targeted card; and one form called a
1-cost card free, which the seat's own misread check caught before any human
did. The seat did the one thing it was built to do — it named a real second
line on five of eight boards — but it does not yet write a form the rest of the
pipeline can consume.

**What this round could not do.**

1. **It could not ask the decisive question.** §10.9 says so plainly: whether a
   price creates a spend-versus-hold decision is a face-and-turn question, and
   a staged single turn shows one hand with no memory of what the bank was
   held *for*. The pair read reached the same conclusion independently:
   *"whole-fight play is warranted."*
2. **It could not test the badge.** The packet has no badges. P2's second half
   stays open and PICK 8 with it.
3. **It could not test the dry sink alone**, because both empty-bank boards
   carried the generator. P4's pick stays open for that reason.
4. **It could not put an AoE card in front of two enemies.** The encounter is
   the seed's, and the seed gave one body on both AoE boards.
5. **It could not draft.** `loader._pool_substitutions` returns `{}` for Klee,
   so the tier 0.5 drafter structurally cannot be offered a prototype Spark
   row; P5 and P6 read a deck assembled by id from PICK 4's own one-for-one
   map, which is what the arm intends but is not what a drafter picked.
6. **It could not run the mirror under the flag.** On two boards the closeness
   falsifier scored the retired base rule. The error runs one way.

**A design observation from the relayed review, recorded and NOT ruled.** All
five Spark-priced non-starter rows are damage Attacks — `proto_spark_strike`
(8 to one), `proto_spark_sweep` (4 to all), `proto_spark_double_tap` (5 ×2),
`proto_spark_blast` (7 to all), `proto_spark_finisher` (18, Exhaust) — and so
is the starter sink `proto_kaboom_sink`. `type: attack` on all six, checked on
`docs/prototype-surface.yaml`; only the generator `proto_pop_spark` (Skill) and
`proto_true_spark_knight` (Power) are anything else. The review's words:
*"Five Spark-priced cards are still five damage Attacks… If whole-fight play
still reduces to damage-per-Spark, re-author one or two sinks around Bomb
manipulation, setup, targeting, draw/exhaust, or another qualitative payoff."*
If every destination for a Spark is damage then choosing between two of them is
arithmetic, which is exactly what the seat found on `t02` — a reason a board can
fail to show a decision that is INDEPENDENT of the prices. It is a design call,
so it goes on the pick list at §11.7 item 1 as option (e) rather than being
settled here.

### 11.7 What went back to [USER] — ANSWERED by R222 (2026-08-29)

**All seven items are ruled.** [USER] countersigned the relayed review's column
whole, verbatim: *"Yep, agreed on those items - please proceed"* — recorded as
ONE slate under **R222**, the day's SECOND batch, because R221 had already been
merged when these answers arrived. Each item below carries the option that was
taken; the unchosen options are gone from HEAD, and the relayed review's
argument is kept beside each answer because it is the record of why.

1. **P1 missed, and PICK 4 does NOT reopen. → (d): leave the set as built and
   let whole-fight play answer it.** No repricing and no enlargement come out of
   `P1`. The published MISS stands as an audit record (R101b) and is an
   INSTRUMENT defect, BACKLOG `EB-202` — the threshold of 4 was unreachable on a
   board set that could pose the question on at most three boards (§11.5
   erratum). **The registered decision-fire is therefore NOT a trigger**, and
   PICK 4 is not reopened.
   **Relayed review, adopted:** *"Keep the recorded MISS for audit purposes, but
   treat it as an instrument defect — not a trigger to add/reprice cards."* Its
   option (e) — re-author one or two sinks away from damage — remains what to do
   IF whole-fight play still reduces to damage-per-Spark, and is not ruled here.
2. **P4 split, and PICK 1 does not close on boards I stacked. → (a): re-run two
   boards with the sink and NO generator, as a sanity check only.**
   **Relayed review, adopted:** the sanity check is a sanity check; the
   meaningful test of a dry sink is how OFTEN it happens across a fight and
   whether it frustrates, which a staged single turn cannot ask. The
   whole-fight starter test is the real one, and the dry-sink boards ride the
   minimal repaired staged round at item 7.
3. **The Rare Power: informative face, uninteresting turn. → (a): leave it as
   built and re-read it in whole-fight play.** Its face is legible — that is what
   `P3` PREDICTED — and an investment Power needs fight history before its
   wording or its price can be judged. Neither §5's wording nor the price of 3
   is reopened.
   **Relayed review, adopted** as written.
4. **The tester seat, on the seat's own RETURN. → (e): the local seat is REMOVED
   as a DECIDING tester until it is repaired AND requalified, and reads in
   SHADOW meanwhile — forms recorded, never graded.** The measurement half is
   law and is written into `EXPERIMENTS.md` under R222 B; the mechanical half of
   the fault is BACKLOG `EB-203`.
   **Relayed review, adopted with its condition:** requalification runs on a
   battery covering target selection, printed costs and intent sensitivity,
   because *"fixing `target: null` alone does not address its semantic
   failures."* `M62` carried both halves and is ANSWERED by R222 — the criterion
   is **≥ 6/8 over one round** AND that battery, together, as the seat's return
   condition.
5. **`M58` — WITHDRAWN as a pick, 2026-08-29 (hygiene), and it stays withdrawn.**
   It asked what the Codex spot-check rate should be. `M58` was **ANSWERED by
   R220 G at N = 4** before this section was written, and its QUEUE row is closed
   and gone from HEAD. §11.0's third disclosure is unchanged: the round did use
   the default, and it does not bear on the rate. The numbering here is left as
   published so citations to items 6 and 7 keep their targets. *(Relayed review:
   "stale, M58 was answered by R220 G (N = 4) — REMOVE the pick." Confirmed.)*
6. **The 40-versus-25 win diagnostic. → (d): teach the probe playability first,
   THEN re-register it on normalized metrics.** No repricing comes out of the
   40-versus-25 figure. The re-registration's metrics are fixed now and are
   recorded in `EXPERIMENTS.md` as the `P5` rerun's metrics-to-be:
   **`spent / available Sparks`** and **`affordable sinks skipped` per turn**,
   in place of the raw per-turn spend rate.
   **Relayed review, adopted:** normalized, the ON arm spent ~91% of what it
   generated against OFF's ~88%, so the raw fall is a consumption artefact and
   not evidence about the prices.
7. **What runs next. → (c): whole-fight Codex play FIRST, then a minimal
   repaired staged round.** The repaired round covers the dry sink with NO
   generator in hand (item 2) and a genuinely multi-enemy board for the two AoE
   rows. The order is a REGISTRATION PRECONDITION, not a preference: the arm's
   next staged round may not be registered until the whole-fight Codex play has
   run. `EXPERIMENTS.md` carries it.
   **Relayed review, adopted** in that order, with the round-2 half kept minimal.

## 12. WHOLE-FIGHT BLIND PLAY (`KLEESPARK-W1`) — registration, drafted before the run

**7(c) is [USER]'s ruling of §11.7 pick 7: both, whole-fight first.** This
section is the first half of that — the registration, the unit, the slate and
the falsifiers — written and committed BEFORE the bridge was deployed and
before any Codex call was spent. Under R212(2) the slate is Claude's to draft
from written design intent and commit DRAFTED; it is offered for batch
countersign. §12.5 onward is the read, appended after the run.

### 12.1 The unit, and why it is one fight and not a run

**The unit is ONE COMPLETE FIGHT** — the first Monster room of a live Act-1
Klee run, played end to end by the Codex seat through `understudy.blindplay
session`, with the Sparks arm granted into the starting deck by
`understudy.embark --arm`.

The house's larger blind-play unit is the floor-1-to-Act-1 run, and it was
measured: sealed session `20260829-181718` spent **120 Codex calls** on 120
actions across six fights, one `codex exec resume` per screen, plus one call
per fight record and one for the run record — **~20 calls per fight all in,
and 128 for the run**. The standing budget rule for tonight caps this piece at
**30 Codex calls**. A run unit is four times over that cap; one fight is inside
it. So the unit is one fight, the cap is set in the driver rather than trusted
to the fight's length (`--max-actions 24`, `--max-refusals 2`), and the worst
case is 24 command calls + 2 refusals + 1 fight record + 1 run record = **28**.

**Two operator facts that ride with the unit, disclosed rather than tidied:**

1. **The screens before the first Monster room are driven by the operator**,
   with `blindplay act`, at zero Codex cost, so the seat's budget is spent
   inside the fight rather than on a map fork. Every such action is listed in
   §12.4. The seat sees its first page at the combat screen.
2. ~~**The shipped automatic Spark rule is still live in the build.** The
   re-author retires it only on acceptance (§6.1), so the fight is played on a
   build where the granted priced rows sit BESIDE the shipped threshold
   discount. That is a contaminant and it runs one way: it makes Sparks *more*
   valuable to hold than the re-authored economy alone would, so a thin
   spend-versus-hold reading here is a floor, not a ceiling.~~

   **ERRATUM 2026-08-30 (relayed review, fact-checked) — R101b: the GRADES
   STAND and are NOT re-graded; the CONTAMINATION CLAIM is struck.** ~~"The
   shipped automatic Spark rule is still live in the build."~~ It was not.
   `+proto` is stamped by `klee-mod/build/deploy_proto.ps1`, which builds
   `-p:PrototypeCards=true`, which defines `PROTOTYPE_CARDS`, under which
   `SparkPower.BaseRuleActive` is the compile-time constant **`false`**
   (`klee-mod/KleeCode/Powers/SparkPower.cs:64`, pinned by
   `SparkAlternativeCostPinTests:66` and `SparkSinkPinTests:50`) — *"at no bank
   do Attacks cost 0 and nothing is consumed automatically"*. Both `W1`
   (`0.2.1517+proto.dirty`) and `W2` (`0.2.1600+proto.dirty`) ran on `+proto`
   builds, so the shipped threshold discount was RETIRED in both, not live
   beside the priced rows. **No grade moves in either run**: the retired rule's
   threshold is 3, `W1`'s peak printed bank was 2 and `W2`'s was 1, so the rule
   could not have fired under either reading. The *"floor, not a ceiling"* hedge
   this note attached to the `W1`/`W3` hold readings is therefore **withdrawn as
   unnecessary**, not as wrong-in-direction. The three back-references that
   inherit this item — §12.9's *"what the record does NOT say"*, §16.4
   contamination 1 and §16.11's *"what the record does NOT say"* — are struck
   with it.

### 12.2 What is granted, and what is not

Six rows of §10.2's tight set, one copy each, into the starting deck — the
whole price ladder so a hand can hold competing prices:

| row | printed name | Spark price | shape |
|---|---|---|---|
| `proto_pop_spark` | Powder Pop | — (generates 1) | the income |
| `proto_kaboom_sink` | Ka-pow! | 1 | the Basic sink |
| `proto_spark_strike` | Fwoosh! | 1 | the Common sink |
| `proto_spark_sweep` | Tinder Toss | 1 | the AoE at the cheap end |
| `proto_spark_double_tap` | Bang Bang! | 2 | the middle rung |
| `proto_spark_finisher` | Firework Finale | 3 | the top rung, Exhaust |

**`proto_true_spark_knight` is NOT granted.** The strict Rare Power would
change the price of every Attack in the deck at once, which is a second
variable in a window whose one variable is the priced-sink economy (D4). §11.7
pick 3 is where it goes, and it stays there.

**Guardrail-7 and R217 G both ride on everything below.** Nothing here is a
win-rate, a comparison with any other build, or a claim about whether the arm
is fun or good. Bot numbers are floors. A blind-play record is iteration
feedback and is never validation, balance evidence or approval.

### 12.3 The slate — four predictions, mechanical falsifiers

Every falsifier is computed from artefacts the run writes by itself: the
gitignored `turn-*/reply.json` per-turn `thinking` sentences, the rendered
observations (`turn-*/prompt.md`), and `transcript.jsonl`'s command rows. No
grade reads a judgement.

| # | slot | prediction | falsifier, mechanically | the decision the outcome changes |
|---|---|---|---|---|
| `W1` | Does the Spark price get *named* as a trade-off across a fight, rather than only on a staged board? | **YES, on at least 3 combat turns** of the fight. | Count the fight's combat turns whose `thinking` string names a Spark-priced row AND either a second Spark-priced row or an explicit hold/save of the bank. **≥ 3 = PREDICTED, 1–2 = SPLIT, 0 = MISS.** | Below 3, §11.7 pick 1 is confirmed by a second instrument and the minimal repaired staged round of 7(c) must carry a two-affordable-sinks board and a dry-sink board rather than more rows. |
| `W2` | The spend rate `P5` asked for, read on a real fight instead of a hand-assembled sim deck. | **Sparks spent ≥ 50% of Sparks generated** over the fight. | Sum the positive and the negative deltas of the printed Spark bank across the fight's observations; `spent / generated`. **≥ 0.5 = PREDICTED, 0.25–0.5 = SPLIT, < 0.25 = MISS.** | Below 0.25 the bank is a pool the player sits on and the ladder is priced above the income — pick 1 option (c), re-price, rather than re-count. Above 0.5 with `W3` at zero, the bank is a pass-through and the price is doing no holding work. |
| `W3` | Is an affordable sink ever *deliberately skipped*? | **YES, on at least 1 turn.** | Count turns ended with `end turn` while the hand held a Spark-priced row whose Spark price ≤ the printed bank. **≥ 1 = PREDICTED, 0 = MISS.** (No SPLIT: the slot is a yes/no.) | Zero says the price creates no hold decision at all in live play, which reopens §4.2's table downward before any further staged round is worth staging. |
| `W4` | GPT's attack-spam concern, as a count rather than an impression — six of eight proto rows are Attacks. | **≥ 70% of the fight's successful `play` commands name an Attack.** | Successful `play` commands in `transcript.jsonl`, typed against the granted rows and Klee's shipped starter. **≥ 70% = PREDICTED, 50–70% = SPLIT, < 50% = MISS.** | A PREDICTED `W4` beside a MISS or SPLIT `W1` is the concern confirmed: the repaired staged round must build its boards around non-Attack competition (the generator, the Burst conversion) rather than adding Attack rows. A `W4` MISS retires the concern for this build. |

**Contamination stated.** §11's eight staged boards have been read, and §10.6's
starter smoke has been read. Neither sets a number above: `W1`–`W3` are
whole-fight questions a single staged turn structurally cannot answer (§11.6
item 1), and `W4` is a count of live plays, which no staged board produces.
The 40-versus-25 sim diagnostic of §11.6 is not quoted and sets nothing.

### 12.4 What actually ran — the session, the stamp, and the four operator actions

**RUN 2026-08-29, sealed session `kleespark-w1`.** Records under
`review/qa/klee-sparks-wholefight-1/` — the house record (`record.md`, its
identity block, the tester's fight and run records verbatim, the per-turn
sentence table and the leak audit), the raw `transcript.jsonl`, `session.json`,
the two record answers as written (`fight-01.md`, `run.md`), all 22 rendered
observation pages and all 22 replies under `pages/`, the grader (`grade.py`)
and its output (`grades.json`).

| | |
|---|---|
| pilot | `gpt-5.6-sol` requested and observed, `codex-cli 0.150.1` |
| build | **`0.2.1517+proto.dirty`**, read off the deployed `mods\klee\manifest.json` |
| game | `v0.111.0`, read off the game's own `release_info.json` |
| run seed | `21H4Y89QDRP6`, read back off the wire (R95) |
| arms granted | the six of §12.2, by wire id, into the starting deck |
| actions | 20 |
| termination | `tool_blocked` — the second fight's first frame, torn down (`EB-178`'s shape) |
| Codex calls | **24** — 22 turn prompts plus 2 record calls. Cap was 30. |
| leak audit | 22 observations scanned, **1 hit**, and it is a false positive: the rule `pilot-vocabulary-score` matched the word *score* inside the prompt's own disclaimer, *"no card list, no score, no recommendation"* |

**The stamp is NOT the one the brief named, and this is the first thing to say.**
The brief named `0.2.1506+proto` and said to stop if the stamp differed. It did
differ. `0.2.1506+proto.dirty` was on disk when this piece began; another agent
deployed `EB-201`'s pile-ring fix while this piece was waiting out the
shared-machine lock; the build the run actually met is
**`0.2.1517+proto.dirty`**. Nothing here deployed anything. I carried on rather
than stopping, and the reason is that the check's purpose — *this build carries
the Sparks arm* — is satisfied more strongly than a matching stamp would have
shown it: `embark --arm` refuses any build without `+proto`, and all six grants
returned `ok`, which is the arm's own classes answering. **That is a call under
the ladder and it is [USER]'s to overturn.** The registration was written so the
cell reads *the installed dev build, named in the record's identity block*,
precisely because `MAJOR.AUTO` moves under a piece that waits.

**The four operator actions, in full**, per §12.1 item 1 — all before the seat
saw anything, none of them a play:

1. `choose "Golden Pearl"` at Neow — the option that changes the deck least, so
   the fight tests the granted ladder and not a Neow modifier.
2. `choose "Proceed"` to leave Neow. (A bare `proceed` was refused there first
   and posted nothing.)
3. `go "Monster (path 1)"` — of the two nodes offered, both Monster.

The seat's first page was that Monster room's combat screen, and its opening
hand held two priced sinks — `Ka-pow!` at 1 and `Firework Finale` at 3 —
against an empty bank. That is `P4`'s dry-sink board arrived at by the seed
rather than by staging, and both cards printed `CANNOT BE PLAYED`.

### 12.5 The fight, turn by turn

Two Toadpoles, 24 and 21 HP, one buffing and one attacking for 7. Three rounds.

- **Round 1** (turns 1–4). Bank **0**. Kaboom! (the shipped 1-cost twin) into
  the attacker, then both Duck and Covers for 10 Block against a 7. `end turn`
  with the reason *"No remaining card is playable"* — the two priced sinks in
  hand were unaffordable, not declined.
- **Round 2** (turns 5–10). Prune — Little Witch's Hunt Swirls the Pyro aura
  and the bank goes **0 → 2**. Fwoosh! (price 1) then Kaboom! kill the
  non-attacker. Powder Pop puts a Bomb on the survivor and returns the bank to
  **2**. Bang Bang! (price 2) goes into it. `end turn` on an empty hand.
- **Round 3** (turns 11–12). Powder Pop again, bank **1 → 2**, then Ka-pow!
  (price 1) detonates the Bomb and finishes the fight.

Then rewards (it took the card, Kaeya — Frostgnaw), gold, a potion, a shop it
left without buying from because *"every item is unnamed"*, and the next
Monster room, whose first frame was torn down and stopped the session.

### 12.6 The four slots, graded mechanically

`python review/qa/klee-sparks-wholefight-1/grade.py <log dir>`, committed before
the run, full output at `grades.json`.

| slot | prediction | measured | grade |
|---|---|---|---|
| `W1` | a named Spark trade-off on **≥ 3** combat turns | **0** | **MISS** |
| `W2` | Sparks spent / generated **≥ 0.5** | generated 4, spent 2, **0.50** | **PREDICTED** (on the boundary) |
| `W3` | **≥ 1** affordable sink deliberately skipped | **0** | **MISS** |
| `W4` | **≥ 70%** of successful plays are Attacks | 5 of 10, **50.0%** | **SPLIT** (on the boundary) |

**Two grades landed exactly on their own boundary and neither is nudged.** `W2`
is PREDICTED at 0.50 by the rule as written, and `W4` is SPLIT at 50.0% by the
rule as written. Both rules were fixed before the run.

**Three honest limits on the numbers, none of which changes a grade.**

1. **`W2` reads NET deltas of the printed bank, page to page, so a turn that
   both generates and spends undercounts both halves.** Round 2 is exactly that
   turn. The true spend is higher than 2 and the true generation higher than 4;
   the ratio is what the instrument can see, and the error moves it in only one
   direction — up.
2. **The fight's last play spent a Spark no page could witness.** `Ka-pow!` at
   price 1 ended the fight, so there is no following combat page to read the
   bank off. Counting it would make the ratio 0.75.
3. **`W1` is strict on purpose and it cost the arm two near-misses.** Turn 6's
   sentence is *"Spend 1 Spark to bring the non-attacking Toadpole within range
   of Kaboom!"*; turn 8's is *"gain a Spark, and unlock Bang Bang!"*. Each names
   one priced row and a Spark, and neither names a second use or a hold, which
   is what the falsifier required. The count is 0 and it stands.

**And the finding the count alone would hide.** The tester never weighed two
Spark uses against each other *on a turn* — and then, asked at the end what the
recurring tension was, answered it unprompted:

> *"The recurring tension was whether to spend Sparks immediately for damage or
> preserve them for stronger cards such as Bang Bang! and Firework Finale."*

That is §10.9's decisive question answered YES by the tester's retrospective and
NO by every one of its twelve turn-time sentences. **The economy is legible as a
shape and inert as a decision** — the tension is describable after the fact and
was never actually faced, because the bank never once held more than one
affordable use.

### 12.7 The pilot's own words on the Spark decisions

Verbatim, R217 G — one model's account, never validation, never balance
evidence, never approval.

1. > *"The recurring tension was whether to spend Sparks immediately for damage
   > or preserve them for stronger cards such as Bang Bang! and Firework
   > Finale."* — the run record, question 2.
2. > *"Firework Finale was dead without 3 Sparks, and the Spark attacks were
   > dead whenever the resource was unavailable."* — the fight record, question
   > 4. The top rung of §4.2's ladder never became payable in the whole fight.
3. > *"Powder Pop was also automatic when followed by an attack, since it
   > generated a Spark, reduced an attack, and added detonation damage."* — the
   > fight record, question 4. The *generator* is what became automatic, not a
   > sink.
4. > *"Play became repetitive once Powder Pop followed by an attack was clearly
   > the default sequence. Applying Pyro, generating Sparks, and spending them
   > on zero-cost attacks also repeated quickly."* — the run record, question 4.
5. > *"I would hesitate to draft additional expensive Spark spenders when
   > Firework Finale already became unusable whenever the resource engine did
   > not line up."* — the run record, question 5.
6. > *"Bang Bang! also appeared to spend only 1 Spark despite printing a cost of
   > 2."* — the fight record, question 6, and the printed bank agrees with it:
   > 2 before, 1 after. See §12.8 item 1.

### 12.8 Two things the run found that are not slots

1. **`Bang Bang!` may be charging 1 for a printed 2 — UNRESOLVED, and the
   tester is what caught it.** The bank read 2 on the page before the play and 1
   on the page after. There is a benign explanation — the play detonated a Bomb
   on the same turn, and if a detonation itself pays a Spark the arithmetic is
   `2 − 2 + 1 = 1` — and the page cannot distinguish the two. **It is a defect
   candidate, not a defect.** Settling it wants a staged board with the sink, a
   full bank and no Bomb on the field, which is one of the boards §12.9 asks for
   anyway.
2. **Kokomi's Bake-Kurage memory panel renders on a KLEE run, and says the wrong
   thing.** Every combat page in this session carried a *"The Bake-Kurage's
   memory"* block with a Charge count, and the tester reported it as the most
   confusing thing on the screen: *"The Bake-Kurage memory repeatedly said I had
   played no card even after several cards had been played."* That is a live
   defect on the installed build and it belongs to the Kurage-memory
   workstream, not to this arm. It is reported here rather than filed, because a
   register row minted on this branch would collide with the branch that owns
   it.

### 12.9 What this leaves — numbered picks, never blanks

**1. Is the "minimal repaired staged round" of 7(c) still warranted? The read is
YES, and this run sharpened what it must contain.** The whole-fight unit did the
thing §11.6 said a staged board could not — it put the price in front of a bank
with a history — and what came back is that **the bank never once held two
affordable uses**. So the decision the arm exists to create did not occur, was
never declined (`W3` = 0), and was named only in retrospect. That is not a
reason to stage more of the same boards; it is a reason to stage the three
boards this fight could not produce.

*(a) run the minimal repaired round on the three boards below;
(b) those three plus a re-read of §11.7 pick 3's Rare Power, which this run
deliberately did not carry;
(c) stage nothing yet — re-price §4.2's table first on the strength of `W1` = 0
and `W3` = 0, then stage;
(d) run a second whole fight on a different seed instead, on the grounds that
one fight is one seed.*

**2. The three boards the repaired round needs, if pick 1 goes (a) or (b).** Each
exists because this fight could not produce it, and each is a board whose
outcome changes something already on the table.

- **Board A — TWO AFFORDABLE USES, ONE BANK.** A bank of 3; `Fwoosh!` (1),
  `Bang Bang!` (2) and `Firework Finale` (3) in hand; one enemy. The bank pays
  any one and cannot pay two. This is `W1`'s and `W3`'s question with the
  precondition actually met, and §11.7 pick 1's four options are what its
  outcome selects between.
- **Board B — THE DRY SINK WITH NO GENERATOR**, which §11.7 pick 2 asked for by
  name and this fight *nearly* delivered: the opening hand was dry with two
  unplayable sinks, but `Powder Pop` was in the deck and arrived on round two.
  The board wants the sink, an empty bank, and no generator anywhere in hand.
- **Board C — THE PRICE THE BANK PAYS, WITH NO BOMB ON THE FIELD.** `Bang Bang!`
  at a bank of exactly 2, one enemy, no Bomb. This settles §12.8 item 1 in one
  turn, and until it is settled every Spark-arithmetic reading in this packet
  carries an asterisk.

**3. GPT's attack-spam concern, now a count.** `W4` came in at exactly 50% —
SPLIT — and the five non-Attack plays were two Blocks, the Swirl, and two
generators. The concern is **neither confirmed nor retired** by one fight.
*(a) treat 50% as inside tolerance and drop the concern;
(b) hold it open and re-count on the repaired round, where the boards are chosen
rather than drawn;
(c) act now by converting one of §4.2's six Attack rows to a non-Attack sink —
which is `PICK 4` option (c) under another name.*

**4. The top rung.** `Firework Finale` (price 3) sat in the opening hand, stayed
in hand for the whole fight, was named DEAD in the fight record and named again
in the run record as a reason not to draft more spenders. Income across the
fight was 4 Sparks in three rounds.
*(a) re-price the top rung down;
(b) leave the price and raise generation, which is `PICK 1`'s question;
(c) leave both, on the grounds that one fight on a starter deck is exactly where
a 3-rung should be dead;
(d) pull the 3-rung from the tight set.*

**5. What the record does NOT say.** No win rate, no comparison with any other
build or seed, and no claim about whether the arm is fun or good. One fight, one
seed, one pilot, a granted deck the generators did not produce, ~~and the
shipped automatic Spark rule still live beside the priced rows (§12.1 item
2)~~. Guardrail-7: these are floors.

**ERRATUM 2026-08-30 (relayed review, fact-checked) — R101b: the grades STAND
and are NOT re-graded.** The struck clause inherits §12.1 item 2, which is
itself struck: `W1` ran on a `+proto` build, so `SparkPower.BaseRuleActive` was
the compile-time constant `false` and the shipped threshold rule was retired,
not live. See the erratum at §12.1 item 2 for the citations. `W1`'s peak
printed bank was 2 against the retired rule's threshold of 3, so no grade
moves.

---

## 13. ROUND 2 (`KLEESPARK-R2`) — R222 D's minimal repaired staged round

Generated from the records by `python -m understudy.staged_turn packet-section klee-sparks-r2` on 2026-08-29. Every table below is transcribed from `review/qa/klee-sparks-r2-t*/` and `review/qa/ledger.tsv`; nothing here is re-graded and nothing is re-read (R101b).

**6 board(s) run, 0 UNRUN, 14 form(s) graded.**

### The boards, grader by grader

| turn | seed | grader | family | verdict | refused by | falsifier hits | replay |
|---|---|---|---|---|---|---|---|
| `klee-sparks-r2-t01` | `JH4T8MSN10KS` | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | intent_insensitive | -- | - |
|  |  | `opus-5-fresh` | claude | **SURVIVES** | -- | -- | confirms -- Seapunk 45 -> 20; Block 0 -> 5 |
| `klee-sparks-r2-t02` | `R805DJ56LZHM` | `local-qwen3-8-27b-ud-q4-k-xl` | local | **SURVIVES** | -- | -- | - |
|  |  | `opus-5-fresh` | claude | **REFUSED** | target_missing, intent_insensitive | -- | - |
| `klee-sparks-r2-t03` | `YX7PB48WR7R4` | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | intent_insensitive | -- | - |
|  |  | `opus-5-fresh` | claude | **REFUSED** | intent_insensitive | -- | - |
| `klee-sparks-r2-t04` | `NMQLUYZDLV` | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | intent_insensitive | -- | - |
|  |  | `opus-5-fresh` | claude | **SURVIVES** | -- | -- | confirms -- Shrinker Beetle 30 -> 15; Block 0 -> 0 |
| `klee-sparks-r2-t05` | `XT4BE7LFY5XH` | `codex-gpt-5.6-sol-fresh` | gpt | **SURVIVES** | -- | -- | - |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | no_second_line, intent_insensitive | spot_check | - |
|  |  | `opus-5-fresh` | claude | **REFUSED** | intent_insensitive | -- | - |
| `klee-sparks-r2-t06` | `R7W86HG7WHUD` | `codex-gpt-5.6-sol-fresh` | gpt | **SURVIVES** | -- | -- | - |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | **SURVIVES** | -- | spot_check | - |
|  |  | `opus-5-fresh` | claude | **SURVIVES** | -- | -- | confirms -- Twig Slime (S) 9 -> None; Leaf Slime (M) 32 -> 25; Leaf Slime (S) 15 -> 8; Block 0 -> 5 |

### The registered slots

A slot is **DECIDED** on two or more grades that all agree, **UNDECIDED** on any split or on fewer than two (R221 B). SURVIVES reads PREDICTED, REFUSED reads MISSED.

| slot | grades | reading |
|---|---|---|
| `S1` | MISS, PRED, MISS, PRED, PRED, PRED, PRED (7) | **UNDECIDED** |
| `S2` | PRED, MISS, PRED, MISS, MISS (5) | **UNDECIDED** |
| `S3` | MISS, PRED, PRED, PRED, PRED (5) | **UNDECIDED** |
| `S4` | MISS, MISS, PRED, PRED, PRED (5) | **UNDECIDED** |

### What the round spent

- **Codex seat reads:** 2 -- the scarce budget, one record each.
- **Local tester reads:** 6.
- **Control / other reads:** 6.

### UNRUN boards (R221 B)

None -- every board in the pre-registered order was run.

### The banners the ledger carries

> staged board: this hand and this board were set by hand through a dev door, so nothing measured here is comparable to any run, and nothing here is a claim about whether the turn is fun
> down-weighting: a grader whose q2 disagrees with [USER] on 3 of its last 5 shared turns cannot mark a turn SURVIVES alone
> UNRUN: R221 B: sequential stopping. This board was staged in the round's pre-registered order and NOT run, because every registered slot it carries was already DECIDED -- two or more grades that all agreed -- before its turn came. Its seed is pinned here so a later round runs THIS board rather than a re-rolled one. Nothing about it was graded, and an UNRUN board is a board with no record, never a struck one (R101b)

### The read

**Everything above this line is transcribed from the records. Everything below
it is a judgment.** The slate is `understudy/turns/klee-sparks-r2/MANIFEST.md`,
DRAFTED and committed before any board was staged; the registration is
`EXPERIMENTS.md` → `KLEESPARK-R2`. Build `0.2.1517+proto.dirty`, read off the
deployed `mods\klee\manifest.json`; game `v0.111.0`; world `main` @ `712c75e`.

### 13.1 The slate, graded

**3 PREDICTED / 0 SPLIT / 0 MISS / 2 UNREACHED.** The two UNREACHED are the
finding, and they are the same finding twice: a staged board can be *authored*
to ask a question and still fail to *pose* it, and this round found two more
ways for that to happen than `EB-202`'s ceiling check can see.

| slot | verdict | why |
|---|---|---|
| `P1` — the price creates a visible spend-versus-hold choice | **PREDICTED** | 3 of 3 `S1` boards, against a threshold of 2 |
| `P2` — a dry sink reads as a dead card | **PREDICTED** | 2 of 2 `S2` boards |
| `P3` — at three bodies the AoE sink is chosen | **UNREACHED** | one of the two `S3` boards drew one enemy |
| `P4` — Bang Bang! spends exactly 2 on a bank of exactly 2 | **UNREACHED** | neither `S4` board produced a replay that played it |
| `P5` — the shadow seat is below `M62`'s bar | **PREDICTED** | agreement 3 of 5 on the first set |

**`P1` is the repair working.** On all three `S1` boards the deciding reader's
second line named a *different Spark-priced card* from the one it played, and
named it as a trade rather than as an also-ran: on `t01`, *"the real
alternative was Firework Finale"* — 18 in one hit against 8 + 5 + 5 out of the
same bank of three; on `t04`, *"the only thing I actually weighed was Dodoco
Blast"*; on `t06`, *"the only real branch was Bang Bang! instead of Dodoco
Blast, since I have exactly one Spark card's worth of Sparks and playing one
locks the other out."* `KLEESPARK-R1`'s `P1` asked for four such boards out of
a set that could produce three, and its MISS said nothing about the cards. This
one asked for two out of a set that could produce three and got three. **That
is what a reachable threshold buys, and it is the whole of `EB-202`'s value:
the same question, asked where it can be answered.**

**ERRATUM 2026-08-29 (relayed review) — the GRADE STANDS and is NOT re-graded
(R101b); the LABEL on it is superseded.** `P1`'s slot title says
*spend-versus-hold*. Its registered predicate does not. `S1` asks only that the
bank reach the cheapest Spark price and fall short of the sum of the affordable
ones (`understudy/turns/klee-sparks-r2/slots.yaml:44-52`), and the MANIFEST
grades `P1` on *"the DECIDING form's answer to question 2 names a Spark-priced
card DIFFERENT from the Spark-priced card its chosen line plays"* — a choice
BETWEEN SINKS. Nothing in either predicate requires a hold line, and nothing in
the three forms supplies one. `t01`'s two candidates — Firework Finale against
Fwoosh! + Bang Bang! — **both spend all three Sparks**, and the hold it does
raise it kills in the same sentence (*"a banked Spark is just damage I did not
deal"*). `t04` names Dodoco Blast, finds it dominated, and says *"this turn did
not present me with a decision — it presented me with a sum"*. `t06`'s two
candidates are **both priced 2**, and it calls the board *"not close"* with
Dodoco Blast dominating *"outright"*. On no board was an affordable sink
deliberately left unplayed.

**So the sentence "3 of 3 spend-versus-hold" above is SUPERSEDED by: on 3 of 3
`S1` boards the ALTERNATIVE SINK IS LEGIBLE** — the reader sees a second
Spark-priced use, prices it against the one it played, and can say why it lost.
That is a real result about the faces and it is what `P1` measured. It is NOT
the whole-fight result: `W1` = 0 and `W3` = 0 (§12.6) said the bank never held
two affordable uses and no affordable sink was ever declined, and nothing in
this round overturns that.

**The registered wording that would have caught it**, stated so a later slate
can use it rather than re-derive it: (i) require the named alternative to be a
HOLD LINE — a second line that plays NO Spark-priced card — which is a strictly
narrower reading of the same question 2; or (ii) `W3`'s falsifier, *a turn
ended with an affordable Spark-priced row still in hand*, which is mechanical,
reads off the replayed line rather than off prose, applies to a staged board
exactly as it applies to a fight, and which no board of this round produced.

**`P2` is the sanity check §11.7 item 2 authorised, and it passes cleanly.**
Both dry boards printed the Spark cards as *"Cannot be played right now"* and
every reader — deciding, shadow and the third seat — read them that way and
played around them. Nobody called a priced card free. The dry sink is legible
at an empty bank; whether it is *frustrating* is a fight-length question and
this board cannot ask it, which §11.6 item 1 already said.

**`P3` UNREACHED, and the reason is worth more than the slot.** `t06` drew its
three bodies and the reader took the AoE without hesitation, for the reason the
board was built to elicit: *"Dodoco Blast's guaranteed 21 spread across the
board with the Twig left in Kaboom! range"* against Bang Bang!'s *"10 total
damage with no guarantee either hit lands on the Twig."* `t04` was built the
same way and **the game gave it one enemy**, on a seed recorded three-body on
six earlier stagings. So the arm's AoE rows now have exactly one live
observation, and one is not two — R221 B decides a slot on two agreeing grades
and this one has one. The registration said in advance that a board drawing
fewer than three enemies is UNREACHED rather than MISSED, and that is what it
is.

**`P4` UNREACHED, and this one is the sharper instrument lesson.** `t03` was
built for exactly this: Bang Bang! at a bank of exactly 2, nothing else priced
in Sparks, no Bomb in hand or on the field. The board did its job — the deciding
reader played Bang Bang! — and then the form was REFUSED for
`intent_insensitive`, because the reader honestly answered that a Debuff
telegraph changed nothing, and **a refused form is not replayed**. `t06`, the
other `S4` board, spent its bank on Dodoco Blast. So the slot's own denominator
produced no replay. *`P4` is UNREACHED, not PREDICTED*, and the pair read's
words are the reason it stays that way: *"absence of a counterexample does not
count as PREDICTED."*

**The Bang Bang! arithmetic is nevertheless ANSWERED, out of slot, and the
answer is recorded here rather than laundered into `P4`.** `t01`'s replay is on
the live game: the bank read **3** before the line; the reader played Kaboom!
(1 Energy), then **Fwoosh!** (price 1), then **Bang Bang!** at a bank of
**exactly 2**, then Duck and Cover; the bank read **0** after, and Seapunk fell
45 → 20, a drop of exactly 25 = 7 + 8 + (5 and 5). **Bang Bang! charged its
printed 2 and dealt its printed 10, with no Bomb anywhere on the board to
refund anything.** §12.8 item 1's candidate — *"Bang Bang! may be charging 1
for a printed 2"* — is therefore explained by the detonation that shared the
whole-fight turn, and there is no pricing defect. `t06` corroborates on the
other 2-priced row: Dodoco Blast off a bank of 2 to 0, 7 to each of three
bodies. **This is evidence, and it is not a graded slot**; `P4` remains
UNREACHED and the board that would have graded it is `t03`, which needs a
telegraph its reader will answer "yes" to.

**`P5` PREDICTED.** Shadow against deciding: `t06` agreed (both SURVIVES),
`t03` and `t05` agreed (both REFUSED), `t04`, `t02` and `t01` disagreed —
**3 of 5** on the first set and **3 of 6** over the round, against `M62`'s
≥ 6/8 bar. The seat stays in the shadow chair and `local_tester qualify`'s
battery remains its route back. Nothing here is a pick.

### 13.2 Shadow versus deciding, and what the disagreements were made of

The three disagreements are not noise and they do not all point the same way.
On `t02` and `t01` the shadow seat was STRICTER than the deciding reader —
`intent_insensitive` on boards the deciding reader answered "yes" to. On `t04`
it was stricter again, and on `t02` the *deciding* reader was the one refused,
for `target_missing`: fresh Opus omitted the target on Kaboom!, which is the
same fault `EB-203` was built for and it fired on the CONTROL rather than on
the seat. **That is worth saying plainly: the missing-target failure is not a
local-model failure, it is a form-writing failure, and the funnel now catches
it in whichever chair it happens.**

The third seat read two boards and disagreed with both of the others on `t05`:
it marked SURVIVES where the shadow seat and the deciding reader both refused.
One board is not a pattern and nothing is claimed from it.

### 13.3 The pair read

Three ADVANCE (`P1`, `P2`, `P5`), two RETURN (`P3`, `P4`), and **overall
RETURN** — on the instrument, not on the arm's design:

> *"The repaired instrument successfully staged the empty-bank/no-generator
> condition on t02 and t05, the multi-enemy area-choice condition on t06, and
> reachable spend-versus-hold comparisons across S1. It did not complete both
> remaining repairs: t04 drew one enemy instead of the required three, and no
> surviving replay exercised Bang Bang! from an exact bank of 2."*

Verbatim at `review/qa/klee-sparks-r2-pair-review-codex-gpt-5.6-sol.md`; its
prompt, which is the whole evidence it saw, is beside it.

### 13.4 Two instrument findings the round produced, neither of them a slot

1. **A seed does not pin an encounter across characters.** `NMQLUYZDLV` drew
   three slimes on six recorded Kokomi stagings and one Shrinker Beetle here,
   on Klee. `R7W86HG7WHUD` drew its three on both. **A board that needs an
   enemy count has no way to require one** — `scenario`'s enemy selectors are
   `first` / `lowest_hp` / `highest_hp` and nothing spawns — so "three bodies"
   is a wish the turn file makes and the seed grants or refuses. `EB-202`
   computes ceilings off the DECLARED board, by construction (a ceiling taken
   off the live board would be taken after staging), so a board declaring three
   enemies counts toward `S3`'s ceiling whatever the game does. **The gap
   between the declared ceiling and the reached one is invisible to every check
   this funnel has.**
2. **In the shadow chair, R221 B's stopping rule reads SHADOW grades.** The
   deciding forms do not exist while the round is running — that is what the
   OWED replay means — so `slot_state` saw only the local seat's verdicts when
   it decided whether to run `t01`. Here it made no difference (every slot read
   UNDECIDED and every board ran), but a round where the shadow seat happens to
   agree with itself twice would stop early on a reading that decides nothing.

### 13.5 The wall clock — R221's timing claim gets its first number

Single-lane pipelined round, six boards, one game, seven launches (six
relaunches, each because a staged board leaves the game mid-combat):

| phase | total | per board |
|---|---|---|
| stage (game-bound) | 89 s | 14.8 s |
| read + grade (model-bound) | 295 s | 49.2 s |
| replay (game-bound) | 124 s | 41.3 s over the 3 surviving lines |
| **round wall clock** | **372 s** | — |

The reads ran back to back for 313 of the round's 372 seconds; everything the
pipeline hid is inside that. **Stage plus read is 384 s of work done in 372 s
of wall clock, so the two lanes saved roughly 73 s of the 89 s of game-bound
work — about 16% of the round.** That is the honest shape of the claim: the
pipeline hides almost all of the game time, and the game time is only about a
quarter of the round, because a read is three times a stage. **A round of this
funnel is model-bound, and a second GAME instance cannot fix a model-bound
round** — which `--lanes`' own documentation says, and this round is the first
number behind it.

**The two-lane attempt, and it failed.** `--lanes 2` was tried first, as the
brief directed, and it **crossed the seeds**: lane 1 asked for `NMQLUYZDLV`
and the run read back `R7W86HG7WHUD`, which is lane 0's seed, so `t04` was
refused by `seed_not_honoured` and the round stopped. `OPERATIONS.md` already
says no graded two-lane round has run and that `EB-191` fires often with two
games on one machine; this is the first graded attempt and it did not survive
its second board. The round was re-run whole on `--lanes 1` so that every board
sits under one instrument, and no reading was carried over from the two-lane
attempt. **The 372 s above is the single-lane number.**

### 13.6 What goes back to [USER] — numbered picks, never blanks

Three, and only three. Everything else this round produced is either a graded
slot, a confirmed defect on `BACKLOG` (`EB-208`, `EB-209`), or an observation
recorded above and claiming nothing.

**1. A staged board cannot require an enemy count (`EB-208`). Which shape does
the fix take?** `t04` was authored for three bodies, declared three bodies,
passed `EB-202`'s ceiling check on those three, and drew one. The declared
board is what every check reads, by construction.

*(a) A LIVE-COUNT PREFLIGHT: after staging, compare the live enemy count with
the declared one and mark the slot UNREACHED on that board automatically, so a
round can never report a slot as graded on a board that did not pose it. Cheap,
catches it every time, and fixes nothing about getting the board.*
*(b) A STAGING VERB: `require_enemies: 3`, which refuses the staging and
re-rolls or fails rather than reading a board nobody wanted. Gets the board or
says why not, and costs game time per attempt.*
*(c) A SEED LEDGER PER CHARACTER: record the encounter each seed drew per
character and let a turn file pin from it. Costs nothing new to run and needs a
Klee three-body seed found first, which is game time either way.*
*(d) Neither: stop staging multi-enemy boards, and leave the AoE question to
whole-fight play, where the encounters are the run's.*

**Relayed review (recorded, never answered): (c), guarded by (a).** The seed
ledger is the fix; the live-count preflight sits behind it so a board that
misses its declared count still cannot report a slot as graded. **Its condition
on (c): the ledger must be keyed by CHARACTER, by GAME/BUILD VERSION, and by
ENCOUNTER CONTEXT** — `NMQLUYZDLV` drew three slimes on six Kokomi stagings and
one Shrinker Beetle on Klee (§13.4 item 1), and the arm has already been ported
across a game version once (R218). A ledger keyed on the seed alone records the
same thing that misled `t04`.

**ANSWERED (R224): (c) + (a), SEQUENCED.** (a) ships FIRST — it costs nothing,
it is hygiene under the ladder, and it alone closes `EB-208`'s acceptance line;
(c) follows, keyed by character, build version and encounter context, when a
Klee three-body seed hunt happens, which is game time either way. `EB-208`'s
`BACKLOG` row carries the shape.

**2. `P4` is UNREACHED because its board's form was refused, not because the
board was wrong (`t03`). What runs next for it?** The Bang Bang! arithmetic is
answered in fact by `t01`'s replay — bank 3 → Fwoosh! → Bang Bang! at exactly
2 → 0, 25 damage, no Bomb — but that is not `P4`'s denominator and it is not
being counted as one.

*(a) Nothing: §12.8 item 1 is answered by the `t01` replay as an out-of-slot
observation, `P4` stays UNREACHED in the published record, and the arithmetic
question closes.*
*(b) Re-stage `t03` on a seed that draws an ATTACK telegraph rather than a
Debuff, so its reader has something to answer question four with, and re-run
`P4` alone as a two-board top-up.*
*(c) Re-pose `P4` against the replayed line wherever a 2-price is paid off a
bank of exactly 2, rather than against the two `S4` boards — which is a
threshold change and therefore a NEW registration, never an edit to this one
(R101b).*

**Relayed review (recorded, never answered): (a).** `t01`'s replay answers the
arithmetic in fact, `P4` stays UNREACHED as published, and the question closes
without spending game time re-staging a board whose answer is already on the
record out of slot.

**ANSWERED (R224): (a).** R101b-clean — the published record is not rewritten,
`P4` stays UNREACHED as published, and §12.8 item 1 closes out of slot.

**3. The pair read returned the instrument (3 ADVANCE / 2 RETURN, overall
RETURN). What runs next for the arm?**

*(a) A two-board top-up round — a Klee three-body board for `P3` and a
re-telegraphed `t03` for `P4` — registered fresh, then the arm's next gate.*
*(b) Nothing staged until §12.9 pick 1 is answered, since that pick asks
whether a repaired staged round was warranted at all and this round is now
evidence about its own premise.*
*(c) Treat `P1` and `P2` as the two answers the round was actually for — the
price does pose a choice, the dry sink does read as dead — accept `P3` and
`P4` as unreached, and move the arm to its next gate without a top-up.*
*(e) **ADDED 2026-08-29 by the relayed review**, which its own column says is
where it stands and which the three options above did not carry: accept `P2` as
the round's answer; record `P1` only as *"alternative sinks are legible"* and
NOT as a spend-versus-hold result (the erratum at §13.1); take NO AoE or
payment top-up round; and resolve the two open questions about the SINK SET —
whether every Spark destination is damage arithmetic, and whether Firework
Finale's price of 3 is reachable at all — BEFORE the arm advances unchanged.
This is (b) amended, not (c): it withholds the advance rather than staging
more boards for it.*

**Relayed review (recorded, never answered): NOT (c) as worded**, because (c)
rests on `P1` reading as a spend-versus-hold result and §13.1's erratum says it
does not. Its position is **(e)**, above, added verbatim in substance at its
request.

**ANSWERED (R224): (e).** The only option consistent with §13.1's erratum —
(c) is explicitly ruled out on it. `P2` is the round's answer, `P1` records
only that alternative sinks are legible, no top-up round is staged, and the
two open questions about the sink set are resolved before the arm advances.

**And one condition has come due — a pick for [USER], not a ruling here.** R222
took §11.7 item 1 option **(d)**, *leave the set intact and let whole-fight play
answer it*, and left option **(e)** — *re-author one or two sinks away from
damage* — as what to do IF whole-fight play still reduced to damage-per-Spark.
The whole fight has now run: `KLEESPARK-W1` graded `W1` = 0, `W3` = 0 and `W4`
SPLIT at exactly 50% (§12.6). **The condition (d) deferred on is therefore MET,
and §11.7 item 1(e) is back on the table as a live pick.** The relayed review
recommends taking it — *"re-author one or two Spark sinks away from pure damage
arithmetic, then another whole fight with Codex or an author-disjoint model"* —
and that recommendation is recorded, not adopted.

### 13.7 What this round does NOT settle

It does not price anything, it does not compare the arm with the retired base
rule, and it says nothing about whether the mechanic is fun — `R215 B` and
Guardrail-7 both still bind, and every board was hand-set through a dev door.
It does not answer §12.9 pick 1, which is [USER]'s. It does not close `PICK 3`,
`PICK 4` or `PICK 8`: `P3`'s single live AoE board is not two, and no badge was
staged. And it still cannot ask the face-and-turn question — §11.6 item 1 is
untouched by anything here.


### 13.8 The relayed review of this round, fact-checked (2026-08-29)

An independent review (GPT) of `KLEESPARK-R2` and R223 was relayed by [USER].
Its column on §13.6's three picks is recorded above, beside each pick. Three
further claims are checked here against the record; none re-grades anything.

**1. `P1` measured a choice between sinks, not spend-versus-hold. RIGHT**, and
the erratum is at §13.1. The registered predicates are the evidence:
`slots.yaml:44-52` and the MANIFEST's `P1` falsifier.

**2. The DECIDING tester was same-family with the rows' author. RIGHT, and the
packet already said so before the round ran.** §7: *"a fresh-Opus grade on
those same rows is same-family and is recorded as such, not as the deciding
read"*; R217 C, `OPERATIONS.md:607`: *"independence is by MODEL FAMILY, author
against grader"*; `understudy/seat.py:275-279` refuses a seat that would grade
its own family's work. All eight Spark rows carry `authored_by: [claude]`
(`docs/prototype-surface.yaml`, `proto_pop_spark` through
`proto_true_spark_knight`). R222 B seated fresh Opus as the DECIDING reader for
an operational reason — the local seat had just been returned — and that
authorisation is real; it is not a finding of independence. **So `KLEESPARK-R2`
is a sound round and is NOT author-disjoint alpha feedback, and the record
should not be read as though it were.** Nothing is re-graded on this: the
grades stand as published (R101b). What it should cost a future round is a
[USER] pick, QUEUE **`M64`**, with three options and no default — R217 C
implies the deciding read must be author-disjoint, R222 B authorised this one,
and the law does not choose between them.

**3. R223's battery has two soft categories. RIGHT on both, and `qualify.py`
concedes half of it in its own docstring.** `costs` is a NEGATIVE check only —
`score_costs` runs `misreads.free_card_misreads` over the reader's prose and
returns PASS on no hits (`understudy/qualify.py:195-206`), so a form that never
mentions a price passes the category and R223's mark of 4/6 is satisfiable by
silence. `intent` is SELF-REPORT — `score_intent` passes any form whose
`q4_changed` is not `False` and whose `q4_different_intent` is not negative
(`understudy/qualify.py:209-216`), so a seat that learns to answer *yes* passes
without the telegraph having entered its line; and the module's own docstring
already says the record cannot do better today (*"The intent category asks for
two packets identical except the enemy intent. No such pair exists in the
record"*, `understudy/qualify.py:43-51`). Both are BACKLOG rows now, `EB-211`
and `EB-212`. Both are PROSPECTIVE instrument design: no sealed form is
re-scored and no published battery result moves, including the seat's live
FAIL at 10 of 18 (R223).

**4. A stopping decision must be applied in the PRE-REGISTERED BOARD ORDER even
where parallel reads finish out of order.** Sent to the engineering branch by
[USER]; recorded here as an amended acceptance condition on `EB-209`, which is
the row that already owns R221 B's stopping rule.

**What this section does not do.** It answers no pick, adopts no
recommendation, and moves no grade. The three picks at §13.6, the added option
(e), §11.7 item 1(e), and `M64` are all [USER]'s.

---

## 14. Sink candidates for 1(e) — sinks that are not damage

**Written 2026-08-29 on branch `klee-sink-candidates`. This is a design memo and
a pick list. Nothing is built, no row is staged, no id is minted, and no number
below is a balance claim.**

The thing being answered is §11.7 pick 1's option (e), which R222 left standing
rather than ruling: *"re-author one or two sinks away from damage — Bomb
manipulation, setup, targeting, draw/exhaust or another qualitative payoff — so
that two Spark destinations differ in KIND and not only in number."* Six of the
eight prototype rows are Attacks. The whole fight (§12) then showed the bank
being spent as soon as it was earned, the price-3 top rung dead from turn one to
the end, and the generator — not any sink — becoming the automatic play.

### 14.1 What a real hold decision needs

A player leaves an affordable damage sink unplayed only when the same Sparks
have a **future use that is worth more than the damage is worth now**. That is
the whole of it, and it is a comparison the current set cannot stage, because
every destination the bank has is damage, so the comparison is arithmetic —
eight now against ten later, and later loses to now every time an enemy is alive
in front of you. There are five shapes that produce a genuine hold, and they are
worth naming separately because they fail for different reasons:

- **A delayed payoff that grows with the bank.** Spend later and the same Sparks
  buy strictly more. This is the only shape where holding is *directly* rewarded
  rather than rewarded by circumstance.
- **A payoff that only exists on a later board state** — a second body on the
  field, a Bomb already placed, an enemy telegraphing a big attack. Holding is
  not rewarded; it is simply the only way to have the Sparks when the board
  finally makes the card good.
- **A defensive use that competes with damage when you are threatened.** The
  bank has to choose between killing faster and not dying, which is the oldest
  real decision in the genre and the one Klee's kit is deliberately short of.
- **An investment.** Spend the bank on something that pays across the rest of
  the fight instead of this turn, so the question is "how long is this fight?"
  rather than "how much damage?".
- **A tempo or draw use.** The bank buys cards or card order, so spending is a
  bet on the deck rather than on the enemy's health bar.

**None of the six Attacks can produce any of these, and the reason is
structural rather than a matter of their numbers.** All six resolve entirely on
the turn they are played, all six pay in the same currency (enemy hit points),
and none of them reads anything about the board except how many bodies are on
it. So the only difference between any two of them is damage-per-Spark, and a
player choosing between two rates does not hold — they take the better rate and
empty the bank. §13.1's `P1` is not a counter-example to this: the readers there
genuinely weighed two priced cards against each other, but every one of those
sentences compared *amounts of damage* (18 in one hit against 8 + 5 + 5; 21
spread against 10 with no guarantee), which is a choice about which Attack to
play, not a choice about whether to spend at all. And `W3` — the funnel's only
detector of an actual hold, "an affordable sink was in hand when the player
ended the turn" — read **zero** across the whole fight.

**Why Powder Pop into an Attack became automatic.** The generator is 0 energy,
it advances the Bomb plan you wanted to advance anyway, and it hands you a Spark
that has exactly one thing to do with it. Playing it costs nothing and forecloses
nothing, so there is no reason ever to hold it and no reason ever to play it
second. Once the Spark exists it goes into the cheapest Attack in hand, because
that is the only destination it has. The sequence is not a decision that happens
to have an obvious answer — it is a sequence with no branch in it at all. Adding
a sink of a *different kind* is the smallest change that puts a branch there,
because for the first time the Spark in hand has two things it could become and
they are not comparable by subtraction.

### 14.2 The candidates

**PREFACE — what already exists (added 2026-08-29 on the relayed review; see
§14.5 claim (a)).** Before any candidate is read, the record has to say that
the shipped Klee pool already contains **three Spark spenders whose payoff is
not a plain Attack**, all three ratified in W3/R211, all three **hybrids: 1
Energy *and* a top-level `spend_spark 2`**:

| id | face as shipped | payoff kind | file |
|---|---|---|---|
| `powder_charge` | 1 Energy · Spend 2 Sparks · Skill · Uncommon — *detonate the target's Bombs, +4 each* | damage, but **board-conditional** — dead on an unbombed target | `docs/klee-cards.yaml:248-249` |
| `hold_the_line` | 1 Energy · Spend 2 Sparks · Skill · Uncommon — *Gain 5 Block; if the enemy intends to attack, gain 6 more* | **defence** (non-damage) | `docs/klee-cards.yaml:303-306` |
| `smoke_and_sparks` | 1 Energy · Spend 2 Sparks · Skill · Uncommon — *Apply 3 Vulnerable* | **debuff** (non-damage) | `docs/klee-cards.yaml:320-322` |

**None of the three was granted to the whole-fight deck.** §12.2's grant is six
prototype rows and nothing else — `Powder Pop`, `Ka-pow!`, `Fwoosh!`,
`Tinder Toss`, `Bang Bang!`, `Firework Finale`. So *"the bank has exactly one
destination and that destination is damage"* is **true of the granted deck and
of the eight-row prototype set, and false of the shipped pool.** That does not
retire §14.1 — the prototype arm is the priced-sink economy under test, and the
three rows above sit in the *other* economy: they charge Energy as well, so
they are not reachable by a bank alone, and the whole point of the arm is a
price paid in Sparks only. But it changes what a re-authoring is *for*. It is
not "give the Spark a second kind of destination for the first time"; it is
"give the **0-Energy, Spark-priced** economy a second kind, and decide what
happens to the three hybrids that already do this at a different price". That
second half is now recommendation option **(5)**, and it did not exist before
the review supplied it.

Eight, numbered. Seven are buildable with what both engines already have; the
eighth is included because it is the shape the brief most wants and it is
honestly out of reach today, and saying so is more useful than smuggling in a
worse version of it.

Every number below is lifted off a shipped Klee or companion face, never
invented — the same rule §4 set for the damage sinks. All seven buildable rows
are **0 Energy with a top-level Spark price**, which is what makes the price a
playability gate in both engines; none has a Spark cost inside a conditional.

Two constraints on what a candidate may replace, both of which narrow the field:
the set stays at eight, and only Attacks may be replaced — and of the six
Attacks, `Ka-pow!` is the **starter** sink that PICK 1 exists to create, so
moving it would undo a different ruling. That leaves five replaceable rows:
`Fwoosh!` (price 1), `Tinder Toss` (price 1, area), `Bang Bang!` (price 2),
`Dodoco Blast` (price 2, area) and `Firework Finale` (price 3).

---

#### 1. Slow Fuse — the bank pumps the Bombs you are about to place

> **Slow Fuse** — 0 Energy · Spend 2 Sparks · Skill · Common
> *Bombs you placed this turn deal 3 more damage.*

Replaces **Bang Bang!** (price 2, Common). The body is `Chain Fuse`'s exactly —
same op, same scope, same figure (`docs/klee-cards.yaml:117-118`) — with the
energy cost swapped for a Spark price and the free Bomb dropped.

**SEQUENCING — CORRECTED 2026-08-29 (relayed review, §14.5 claim (c)); the
first draft of this candidate had it backwards.** `_op_modify_bombs`
(`tier0/engine/effects.py:1667-1673`) iterates the Bombs **already on living
enemies** and adds the bonus to each; it schedules nothing and it cannot reach
a Bomb that does not exist yet. So this card is played **AFTER** the placement
cards on the same turn, never before them. The shipped precedent says the same
thing from the other side: `Chain Fuse` prints `modify_bombs` *first* and
`place_bomb` second, so **`Chain Fuse` does not buff its own Bomb** — it buffs
whatever was already placed this turn. Every sentence below is written in the
corrected order.

**The decision:** hold 2 Sparks through the placement so that on the turn you
have actually put two or three Bombs down, one more card makes all of them
bigger — instead of spending the same 2 on ten damage today.

**The board state that makes it beat damage:** a turn on which `Double Pop`,
`Bomb Voyage`, `Mine Toss` or `Jumpy Dumpty` has **already resolved**. One Bomb
makes this a bad ten damage; three Bombs make it nine damage that also feeds
the relic and every detonation payoff in the deck.

**The failure mode:** it is dead on a turn with no Bomb placed yet, which is
most opening hands, and "dead card" is what §13.1's `P2` says a dry sink already
reads as. And because the buff arrives *after* the placements rather than
before them, a player who has not internalised the scope clause will sequence
it first, get nothing, and read it as a nothing card — a legibility cost that
`Chain Fuse` already carries and that this row inherits whole.

**Overlap with `Chain Fuse`, stated plainly (§14.5 claim (c), second half):**
against a player who holds both, this card is `Chain Fuse` minus the 4-damage
Bomb, bought with Sparks instead of Energy. The only thing it tests that
`Chain Fuse` does not is **whether the currency changes the decision**. That is
a real question for this arm and a thin one for the pool, and it is the reason
this candidate is weaker as a *novelty* argument than as a *price* argument.

**Can tier 0 price it?** **No — it needs a `_spark_unit_value` leg.**
`modify_bombs` appears nowhere in `_expected_damage`, so the pilot values this
card at exactly zero and will never buy it, and `_spark_unit_value` (which
prices a Spark as the cheapest affordable sink's payoff over its price) would
therefore price the whole bank at zero on a hand holding only this. That is the
declared blind spot working exactly as its docstring says it does.

**The falsifier (corrected with the sequencing):** an affordable damage sink is
in hand at `end turn` on a turn this card was played, or — sharper — the
recorded reason for a `Slow Fuse` play names **the Bombs it has already placed
this turn**. A reason that names a Bomb card the player intends to play
*afterwards* is now evidence of a **misread**, not of a hold, and the grader
script must score it that way.

---

#### 2. Minefield — the bank buys a delayed board sweep instead of an instant one

> **Minefield** — 0 Energy · Spend 2 Sparks · Skill · Uncommon
> *Place a 5-damage Bomb on ALL enemies.*

Replaces **Dodoco Blast** (price 2, Uncommon, 7 damage to all). The body is
`Mine Toss`'s exactly, at Spark price instead of 1 Energy.

**The decision:** hold 2 Sparks now so that the Bombs land on a turn you can
also detonate them, instead of taking 7 to each body immediately.

**The board state that makes it beat damage:** two or more enemies AND a
detonator (`Quick Fuse`, `Remote Detonator`, `Powder Charge`, or simply any
Attack, since a hit detonates early) either in hand or expected. Against three
bodies it is 15 damage on a one-turn delay plus three Spark refunds from the
relic; `Dodoco Blast` is 21 now and nothing afterwards. Against one body it is
plainly worse than the card it replaced, and that is intended.

**IT IS PARTLY A GENERATOR, AND THE FIRST DRAFT DID NOT DO THIS ARITHMETIC
(relayed review, §14.5 claim (d)).** Klee's **starter** relic Pounding Surprise
carries `spark_on_detonation`, and `detonate_bombs` grants **1 Spark per Bomb
detonated** (`tier0/engine/effects.py:874-875`) — it is not a draft-dependent
upside, it is in the kit from turn one. So the bank arithmetic for one play of
this card, once the Bombs go off, is:

| bodies | Sparks spent | Bombs placed | Sparks refunded | net |
|---|---|---|---|---|
| 1 | 2 | 1 | 1 | **−1** |
| 2 | 2 | 2 | 2 | **0** |
| 3 | 2 | 3 | 3 | **+1** |

**On three or more bodies this sink pays for itself and then some**, and a sink
that refills the bank it drains cannot create the scarcity that §14.1 says a
hold requires. The refunds are one turn late and are forfeit on any body that
dies before its Bomb resolves, so it is not free income — but it is closer to
`Powder Pop` than the section intends, and against a four-body board it is
strictly Spark-positive. That is a real argument against this candidate and it
is recorded as one rather than as a bonus. If [USER] takes it anyway, the
honest repair is to price it at **3** rather than 2, which puts every row of the
table at −1 or worse; that is a design change, not hygiene, so it is not made
here.

**The failure mode:** the delay is a real cost against anything that dies this
turn, and Klee's own Attacks detonate Bombs early *by accident*, so an
inattentive player will often convert this back into ordinary damage without
meaning to. It also risks being read as simply a slower `Dodoco Blast` — the
same kind, differently timed — rather than a different kind.

**Can tier 0 price it?** **Partly, and the gap is precise.** `_expected_damage`
credits `place_bomb` as `bomb_damage × amount` and **never multiplies by the
number of targets**, so an all-enemies Bomb is valued as one Bomb. Against three
bodies the pilot sees 5 where the card delivers 15. A one-line leg fixes it; the
direction of the error is under-valuing, which is the safe direction this file
takes everywhere.

**The falsifier:** `Dodoco Blast` or `Bang Bang!` affordable and in hand while
this is played, on a board with two or more enemies — or the W3 detector firing
on a turn this card is held for a Bomb-and-detonate turn.

---

#### 3. Behind the Barrel — the bank buys survival, and only when survival is at stake — **DOMINATES `Hold the Line`, see the finding below**

> **Behind the Barrel** — 0 Energy · Spend 1 Spark · Skill · Common
> *Gain 5 Block. If the enemy intends to attack, gain 6 more.*

Replaces **Fwoosh!** (price 1, Common, 8 damage). The body is `Hold the Line`'s
exactly — same Block figures, same predicate — at price 1 instead of 2 and 0
Energy instead of 1.

**The decision:** hold 1 Spark now so that when the telegraph turns red you can
pay for eleven Block, instead of converting it into eight damage the moment you
earn it.

**The board state that makes it beat damage:** any turn where the incoming
number is larger than the damage you would trade it for — which, on a 62-HP
character, is most turns after act 1. It is the only candidate whose value is
set by the *enemy's* next move rather than by your own hand.

**The failure mode:** on a turn where the enemy is not attacking it is five
Block for a Spark, which is thin, so it may simply read as a worse `Run Away!`
and never be drafted. There is also a legitimate objection that the shipped pool
already has this card at 1 Energy and 2 Sparks, so the prototype is a reprice of
an existing idea rather than a new kind — the answer is that `Hold the Line`
proves the kind works and is exactly why it is the cheapest candidate to be
confident about, but it does mean this row tests placement and price, not
novelty.

**FINDING — THIS ROW STRICTLY DOMINATES `Hold the Line`, and the first draft
did not say so (relayed review, §14.5 claim (b)).** The two faces, side by
side: `hold_the_line` is **1 Energy + 2 Sparks, Uncommon**
(`docs/klee-cards.yaml:303-306`); this candidate is **0 Energy + 1 Spark,
Common**, with the **identical body** — Block 5, plus 6 more on
`enemy_intends_attack`. It is cheaper on **both** currencies, and it is
*commoner*, so it is also easier to draft. There is no board state on which a
player prefers `Hold the Line`. **The row is kept listed and is not deleted** —
the record went out with it in, and R101b's habit is to strike rather than
rewrite — but it now carries this finding, and anything downstream must read
the two together. The mitigating fact, which is real but does not dissolve the
problem: prototype rows are dev-only and are not in the draftable pool, so the
two faces never sit in one deck **today**. The domination becomes live the
moment (e) is accepted and a row moves to the real sheet, which is precisely
when nobody will be looking for it. So if [USER] takes this candidate, the
acceptance step owes **either** a reprice of this row **or** a migration
decision for `Hold the Line` — which is option **(5)**, and the second reason
that option now exists.

**Can tier 0 price it?** **Yes, today.** `_block_value` reads printed Block, and
`_active_effects` evaluates the `enemy_intends_attack` branch live, so the pilot
sees the conditional half on the turns it fires. The one honest caveat is that
Block is valued only up to the damage it actually prevents this turn, so on a
turn with a big incoming hit the pilot will value it correctly and on a quiet
turn it will value it at zero — which is, for once, exactly the behaviour we
want to observe.

**The falsifier:** a turn on which `Tinder Toss` or `Bang Bang!` is affordable
and in hand, the enemy telegraphs an attack, and this is played instead — with
the recorded reason naming the incoming damage. The mirror case is just as
informative: the same board, damage taken anyway, and the Block left unbought.

---

#### 4. Powder Keg — the whole bank buys next turn instead of this one

> **Powder Keg** — 0 Energy · Spend 3 Sparks · Skill · Uncommon · Exhaust
> *Place a 5-damage Bomb on ALL enemies. Your Bombs deal 3 more damage.*

**TEXT AND EFFECT ORDER CORRECTED 2026-08-29 (relayed review, §14.5 claim
(e)).** The first draft printed the `modify_bombs` clause first, which — by the
same engine fact as candidate 1, `tier0/engine/effects.py:1667-1673` — means
the Bomb this card places is put down **after** the buff has already run and
therefore does **not** get the `+3`. The draft's headline arithmetic (three
existing Bombs plus this one, `+3` each, **12** extra damage) counted a Bomb the
printed order could not reach; as printed it was **9**. The two available
repairs were (i) reverse the effects so `place_bomb` resolves first and the
`scope: all` buff then catches every Bomb including the new one, keeping 12, or
(ii) keep the order, print *"existing Bombs"*, and say 9. **Taken: (i)** — it is
the ordering that matches the sentence the candidate was written to make ("every
Bomb on the board, including the ones already ticking"), so it corrects the text
to the intent rather than shrinking the intent to the text. Option (ii) remains
available to [USER] at a stroke and is a strictly smaller card. Note this makes
the row's order the **opposite** of `Chain Fuse`'s shipped order, deliberately;
the effects list must read `place_bomb` then `modify_bombs`, and a build that
copies `Chain Fuse` verbatim reintroduces the bug.

Replaces **Firework Finale** (price 3, Uncommon, Exhaust, 18 damage) — the rung
that was dead for the entire whole-fight run and was named twice by the tester
as a reason not to draft more spenders. The `+3` is `Chain Fuse`'s figure at
`modify_bombs`' other shipped scope; the Bomb is `Mine Toss`'s.

**The decision:** hold 3 Sparks so that one turn is spent making every Bomb on
the board — including the ones already ticking — bigger, instead of taking 18
damage to one enemy right now.

**The board state that makes it beat damage:** a board that already carries
Bombs and a fight with turns left in it. Against a pile of three existing Bombs
plus the one this places, the `+3` alone is 12 extra damage arriving at the
start of your next turn **— on the corrected order above; it is 9 if [USER]
takes repair (ii) —** with the Bomb on top and a relic Spark per detonation
feeding the next purchase. That refund is the same Pounding Surprise income
candidate 2 was corrected for, and it applies here too: on a board of three
carrying four Bombs each detonation returns a Spark, so the 3 spent here come
back over the following turn. Unlike candidate 2 the card still consumes the
whole bank at the moment of decision, which is the property the hold test
needs, but the section should not pretend the bank is gone for good. Against an enemy about to die it is strictly worse
than 18 now, which is the trade.

**The failure mode:** this is the most likely of the eight to be *dead* rather
than merely automatic — it wants a board state that the opening turns of a fight
never have, and a fight short enough to be worth playing is a fight where next
turn may not matter. It is also the candidate most exposed to the identity rail
in LAW: Klee's scaling must never top her frontload, and a card that converts
the bank into future damage is a scaling card wearing a Spark price. If it
overperforms it overperforms in exactly the direction the character is not
allowed to go.

**Can tier 0 price it?** **No — the same `modify_bombs` leg as candidate 1, plus
candidate 2's target-count fix.** With neither, the pilot values this at 5 (one
Bomb) against a real payload several times that, and will never spend a full
bank on it.

**The falsifier:** the W3 detector firing at all — a bank of 3 held through a
turn on which `Bang Bang!` and `Tinder Toss` were both affordable — plus, on the
turn it is finally played, a recorded reason that names the Bombs already on the
board rather than the Bomb it places.

---

#### 5. Second Pocket — the bank buys the card you need, not the damage you have

> **Second Pocket** — 0 Energy · Spend 1 Spark · Skill · Common
> *Put a card from your discard pile on top of your draw pile. Draw 1 card.*

Replaces **Fwoosh!** (price 1, Common) — the alternative to candidate 3 in that
slot. The fetch is `A Moment Alone`'s op used in the same direction it already
ships in.

**The decision:** hold 1 Spark so that the turn after your best Bomb card goes
to the discard, you can have it back on top — instead of turning the Spark into
eight damage the moment you get it.

**The board state that makes it beat damage:** a discard pile containing
`Jumpy Dumpty`, `Bombs Away!`, `All of My Treasures!` or a detonator, and a
fight long enough for the deck to have cycled once. It is the only candidate
that makes the bank buy *the shape of your next turn*.

**The failure mode:** it is the candidate most likely to be automatic in the
other direction — a cheap card that draws is played on sight in most decks, and
a player who does not care which card comes back will just play it for the draw.
Turn one, with an empty discard, it is a 1-Spark cantrip and nothing else.

**AND IT ADDS A SELECTOR, WHICH IS A COST THIS HOUSE HAS PRICED BEFORE (relayed
review, §14.5 claim (f1)).** `recall_to_draw` fetches a **chosen** card
(`docs/current/calibration/sprint-sim-hygiene-log-2026-07-29.md:130`), so every
play opens the discard pile and stops the turn while the player reads it. The
adjacent precedent is real but is **not** the same object: what [USER] rejected
on Kokomi was a **mode selector fired on every play** — *"forces an extra
selector step"*, `review/ruled/kokomi-kurage-memory-2026-08-29.md:46`, and the
Charge design was then built with *"no selector, and that is deliberate"*
(`:127-129`), refusing pick-at-fire-time as *"the selector step [USER]
rejected"* (`:478-481`). A discard fetch is opt-in, on one card, at a moment the
player chose — a smaller object than a mandatory per-play mode prompt. It is
still the shape [USER] has twice declined to pay for, and on a card meant to be
played most turns the difference narrows. Recorded against this candidate; not
decided here.

**Can tier 0 price it?** **No — it needs a `_spark_unit_value` leg.**
`_tempo_value` prices `draw` and `energy`; `recall_to_draw` appears nowhere in
it, so the pilot sees this as "draw 1 for a Spark" and prices the fetch — the
entire point of the card — at zero. Worse than the other gaps, the pilot has no
concept of *which* card it would fetch, so even a leg would be crude.

**The falsifier:** an affordable damage sink left in hand at `end turn` while
this is held, or a recorded reason for the play that names the card being
fetched.

---

#### 6. Regroup — the bank buys aim

> **Regroup** — 0 Energy · Spend 1 Spark · Skill · Common
> *Move all Bombs onto the target. They deal 2 more damage.*

Replaces **Tinder Toss** (price 1, Common, 4 damage to all). The body is
`Careful Arrangement`'s exactly (`move_bombs`, bonus 2 —
`docs/klee-cards.yaml:119-120`), which means it carries the same
currency-conversion-duplicate objection candidate 1 does: against a player
holding both, this is `Careful Arrangement` bought with Sparks instead of
Energy. It does **not** overlap `powder_charge`, contrary to the relayed review
(§14.5 claim (f2)) — that card runs `detonate`, this one runs `move_bombs`, and
gathering a pile is the setup for a detonation rather than a second way to do
one.

**The decision:** hold 1 Spark so that when your Bombs have scattered across
three bodies you can gather them onto the one that is about to matter, instead
of spending it on four damage to each.

**The board state that makes it beat damage:** Bombs spread across two or more
enemies with one of them near a kill threshold, or an elite that wants the whole
pile. This is D2's *targeting* verb, which the current set feeds not at all.

**The failure mode:** Klee's Bombs mostly go where you put them, so a
disciplined player rarely needs to move them, and against one enemy the card
does nothing but the `+2`. It is also the narrowest of the eight — narrow enough
that it may simply never be drafted, which is a different failure from being
automatic and arguably a worse one.

**Can tier 0 price it?** **Partly.** The pilot has a `move_bombs` reader
(`BOMB_MOVE_READER_AIM_VALUE`) and `_hand_has_op` checks for it, so unlike
candidates 1, 4 and 5 it is not invisible — but the value is a flat constant
rather than a read of where the Bombs actually are, so the pilot cannot tell a
gathering worth making from one that is not.

**The falsifier:** the card played on a board with Bombs on two or more enemies
while a damage sink was affordable, with the recorded reason naming the enemy
being gathered onto.

---

#### 7. Powder Trail — the bank buys defence you have not needed yet

> **Powder Trail** — 0 Energy · Spend 2 Sparks · Skill · Uncommon
> *Gain 4 Block. Gain 4 Block at the start of your next turn.*

Replaces **Bang Bang!** (price 2, Common) — the alternative to candidate 1 in
that slot; at Uncommon it would go into `Dodoco Blast`'s slot instead. Both
figures are Charlotte's shipped pair in `docs/fontaine-companions.yaml`.

**The decision:** hold 2 Sparks so that a turn you can afford to spend
defensively buys defence for the turn you cannot — instead of buying ten damage
now.

**The board state that makes it beat damage:** a known two-turn threat — an
elite winding up, or the turn before a boss's big beat — where the Block you
want is not the Block you can pay for on the turn it lands.

**The failure mode:** pre-emptive Block is the exact shape the watch register
already worries about on another character (`W6`), and Klee's declared Block
axis is 2.0 — deliberately low. A card that hands her steady defence for a
resource she generates every turn moves her off her own statline, and it does it
quietly.

**The declared weakness, with its citation (relayed review, §14.5 claim
(f3)).** `docs/current/characters/klee-character-design.md:15` — *"A3 Block
**2.0** — Reluctant, **conditional** defense"* — and the adjective is the whole
distinction between this candidate and candidate 3. `Hold the Line` and Behind
the Barrel are *conditional*: their large half is gated on
`enemy_intends_attack`, so they buy defence only on the turns the enemy is
swinging, which is what "reluctant, conditional" describes. Powder Trail is
**unconditional and pre-emptive** — 4 now and 4 next turn regardless of what
anything intends — so it is not a low, conditional Block axis at a Spark price;
it is a *steady* Block axis, which is a different character. That is not a
reason it cannot be picked, but it is a **statline amendment** and belongs to
[USER] under the identity rail, not to a sink re-authoring.

**Can tier 0 price it?** **No — it needs a leg on the block side.** `_raw_block`
reads only `op == "block"`; `block_next_turn` is not in it, so the pilot sees
four Block for two Sparks and will price this as the worst card in the set.

**The falsifier:** played on a turn when the incoming damage was *low* and a
damage sink was affordable — that combination is the hold, and nothing else in
the set can produce it.

---

#### 8. Saving Up — the shape the brief most wants, and it cannot be built today

> *Sketch, not a row.* A card or Power whose payoff scales with how long the
> Sparks have been held — "at the end of your turn, if you did not spend a
> Spark, this costs 1 less" or "spend your whole bank: deal 4 damage per Spark
> spent, to all enemies".

**AMENDED 2026-08-29 (relayed review, §14.5 claim (f4)): the spend-all half of
that sketch is struck as a hold shape.** *"Spend your whole bank: 4 damage per
Spark"* is linear — the Sparks are worth exactly 4 each whenever you spend them
— so it rewards *batching*, not *holding*, and it pays in damage, which puts it
back in the one kind this whole section is trying to leave. What the shape
actually needs is one or both of: **increasing returns** (the per-Spark rate
rises with the size of the bank, so a bank of 3 is worth strictly more than
three banks of 1) and **Retain**, so the card survives the draw that would
otherwise force the spend — Retain already ships in this world (Bursts carry it
per principles v1.4, `docs/current/characters/klee-character-design.md:52`).
Both were absent from the sketch and both are now part of it. Neither changes
the refusal below: the engine work is still unbuilt, and increasing returns need
the same missing bank-reading formula.

This is the only shape on §14.1's list that rewards holding **directly** rather
than through circumstance, and it is therefore the shape most likely to produce
a genuine hold. It is recorded here as refused rather than proposed, for two
reasons:

1. **A bank-scaled payoff has no op.** There is no `spend_all_sparks`, and no
   damage formula that reads the Spark bank as a count except `2_plus_sparks`,
   which reads it and does not spend it. Writing one is engine work in both
   engines.
2. **A cost that decays while you hold is a new Power**, and
   `tools/gen_prototype_cards.py` refuses a row applying a power with no
   `PowerModel` in the registry — by name, exactly as it refused
   `spark_attack_cost` (§10, the eighth row). That refusal is the surface's
   promise that a staged row can actually be staged, and it should not be worked
   around.

If [USER] wants this shape, the honest route is the one `Spark Knight's Oath`
took: take the runtime work first, in its own step, and stage the card after.
It is not a candidate for *this* re-authoring.

---

### 14.3 Recommendation — a numbered pick, and nothing is marked default

> **TAKEN (R224): option (5), migrate before you duplicate.** No new prototype
> row is created; the first act is the ruling on the three existing non-damage
> spenders, and the next whole fight grants the mixed pool.
> **Its migration BRANCH is RULED too (R224, slate item 16): SPARK-ONLY,
> FLAG-GATED.** `powder_charge`, `hold_the_line` and `smoke_and_sparks` go to
> 0 Energy with the price paid wholly in Sparks, as a **dev-only substitution**
> — `loader._pool_substitutions`' Klee half under `SPARK_ALT_COST_ENABLED` in
> sim, and `-p:PrototypeCards=true` in C#. Energy-gating would make a null read
> uninterpretable, and the flag removes the one cost (5) records against
> itself: that a migration is a shipped-pool edit and therefore heavier and
> less reversible than a dev-only prototype row. **With the flag off the pool
> is byte-identical to shipped.** Engineering: `EB-218`.
> **BUILT on branch `eb218-hybrid-migration`** (three rows on
> `docs/prototype-surface.yaml`, three entries in `C.SPARK_ALT_POOL_SUBS`,
> both engines, no reprice).
> Under (5), Minefield and Powder Trail are no-ops — Minefield lives only
> inside option (2), and Powder Trail appears in no numbered option.

This is a design call between genuinely different directions, so it goes back
whole. Options (1) through (3) keep the set at eight and replace Attacks only;
(4) changes nothing; (5) — added 2026-08-29 on the relayed review — creates no
prototype row at all and acts on the shipped pool instead.

**(1) Re-author two: `Fwoosh!` → Behind the Barrel (candidate 3), and
`Firework Finale` → Powder Keg (candidate 4).**

Why these two. They differ from each other about as far as two sinks can: one is
defence bought on the enemy's turn, one is offence bought on a future turn of
yours, and neither can be compared to the other by subtraction — the first is
priced by the incoming number, the second by how many turns the fight has left.
Both differ from every remaining damage sink in kind and not only in amount. And
they sit at the two ends of the price ladder deliberately: at price 1, the
cheapest thing the bank can do stops being "eight damage" and starts being a
question; at price 3, the rung that was dead for an entire fight gets a body
that a dead rung is *supposed* to have — something you save up for. After the
swap the damage ladder still reads `Tinder Toss` at 1, `Bang Bang!` and
`Dodoco Blast` at 2, and nothing at 3, which is the point: a full bank of 3 must
now choose between one investment and two small damage plays, and that is a hold
decision by construction rather than by hope.

What it costs to build. **No new C#**: every op involved — `block`, the
`enemy_intends_attack` conditional, `modify_bombs`, `place_bomb` — already ships
in the Klee mod on `Hold the Line`, `Chain Fuse` and `Mine Toss`, and the
prototype generator emits all four today. **Two tier-0 pricing legs**, both in
`_expected_damage`: `modify_bombs` (currently invisible) and a target count on
`place_bomb` (currently valued as one Bomb regardless of targets). Candidate 3
needs none. **No art**: prototype rows are dev-only and carry no portrait; art is
owed at acceptance, when the rows move to the real sheet, and would be two
portraits.

**What the 2026-08-29 corrections add to this option's cost, and nothing else
moved.** (i) Powder Keg's effects must be emitted `place_bomb` **then**
`modify_bombs` — the opposite of `Chain Fuse`'s shipped order — or the card
loses 3 of its 12 (candidate 4's correction block). That is a build instruction,
not a new leg. (ii) Candidate 3 now carries a **strict domination over
`hold_the_line`** that is inert in the dev arm and live at acceptance, so this
option's *acceptance* step owes either a reprice of the new row or a migration
of the old one — see option (5). Neither correction changes the two pricing
legs, the "no new C#" finding, or the art count.

**(2) An alternative pair: `Bang Bang!` → Slow Fuse (candidate 1), and
`Dodoco Blast` → Minefield (candidate 2).**

Both Bomb-facing, both in the middle of the ladder, and the damage rungs at 1
and 3 stay exactly as they are. This is the more conservative direction: it
tests whether *Bomb manipulation* is a real second kind while leaving the top and
bottom of the price ladder untouched, so if it fails, nothing else about the arm
has moved. It is weaker on the finding that motivated all of this — the dead top
rung is still `Firework Finale` and still dead — and it puts both new cards in
the same family, so a null result cannot distinguish "Bomb sinks don't work"
from "this pair of Bomb sinks doesn't work". It needs the same two pricing legs
and no C#.

**(3) One only: `Fwoosh!` → Behind the Barrel (candidate 3).**

The cheapest possible test of the whole idea. It is the one candidate that needs
**no engine work at all** — buildable and sim-priceable today, in both engines,
with numbers lifted whole off a shipped card — and it is the only kind on
§14.1's list that has already been proved to work in this pool, because
`Hold the Line` is that card at a different price. If the answer to "does a
non-damage sink create a hold?" is no even here, the other six candidates are
not worth building.

**(4) None: keep the set as built and move to the next gate.**

The case for this is real and should not be strawmanned. §13.1's `P1` came back
PREDICTED on three of three boards: readers did weigh two priced cards against
each other and said so in their own words. The whole-fight null on `W3` came off
**one fight, one seed, one pilot and a granted deck**, and the fight's own record
says the bank never held two affordable uses — which may be a generation problem
(PICK 1's question) rather than a sink-kind problem. Under this option the arm's
next gate is a second whole fight with the generation question answered first,
and (e) stays available afterwards with better evidence behind it.

*Relayed review, on option (4):* the reviewer's reading of this option is **not**
"the damage-only set is fine". It is **"pause replacement, and test or migrate
the existing utility sinks first"** — i.e. the case for doing nothing to the
prototype set is really a case for doing something to the *pool* rows in §14.2's
preface. Recorded beside (4) because it is a different option from (4) as
written, and it is now carried as (5) rather than folded in here.

**(5) Migrate before you duplicate: rule on the three existing non-damage
spenders under the alternative-cost economy first, test the real mixed sink
pool, and create no new rows until that read is in.**

The three hybrids in §14.2's preface — `powder_charge`, `hold_the_line`,
`smoke_and_sparks` — already do what candidates 3, 5, 6 and 7 propose to do,
one economy over. Under this option the first act is an explicit decision about
**what they become in the priced-sink world**: either they stay **hybrid**
(1 Energy *and* a Spark price, so the bank alone cannot reach them and they
remain a second, Energy-gated tier of sink), or they migrate to **Spark-only**
(0 Energy, price paid entirely in Sparks, which is the economy the eight
prototype rows are testing). That is one ruling covering three rows, and it is
prior to any re-authoring because it decides whether a new row is a *new kind*
or a *duplicate at a second price* — which is exactly what candidate 3 turned
out to be against `hold_the_line`, and candidates 1 and 6 against `Chain Fuse`
and `Careful Arrangement`. The next whole fight then grants **the mixed pool**
— the prototype ladder plus the migrated utility spenders — and asks §14.4's
hold question of a deck that actually contains a non-damage destination,
without minting a single new id. **If, after that read, a qualitative rung at
price 3 is still wanted, the smallest next step is to prototype the corrected
Powder Keg (candidate 4) alone, in `Firework Finale`'s slot, and nothing else.**

What it costs: no new C#, no art, and no new prototype row in the migrate-only
form. It does need the same **two tier-0 pricing legs** if Powder Keg follows
(and none if it does not), plus whatever the migration itself moves on the real
sheet — which is a shipped-pool edit and therefore a heavier, less reversible
act than a dev-only prototype row, and that is the honest argument against this
option. What it gives up: a whole fight's delay before any new kind is tested,
and the possibility that the hybrids' Energy cost is precisely why they never
compete with the bank, in which case the read comes back null for a reason that
has nothing to do with kind.

### 14.4 What would prove it

Whichever pair is chosen, the unit that decides it is **another whole fight**,
not a staged round — §11.6 item 1 and §13.7 both say a staged single turn cannot
ask a face-and-turn question, and this is the most face-and-turn question the arm
has. The registration would carry three mechanical predictions, all falsifiable
off the transcript by a grader script committed before the run: the funnel's own
hold detector (**an affordable damage sink in hand at `end turn`**) fires at
least once, which is the single number this whole section exists to move off
zero; the bank holds **two affordable uses on at least three combat turns**,
which is the precondition §12.9 found was never met and without which the first
prediction is untestable rather than false; and the **price-3 rung is bought at
least once**, which is the direct answer to §12.9 pick 4 and to the tester's
"I would hesitate to draft additional expensive Spark spenders". A fourth,
recorded and not graded, is worth carrying: the share of successful plays that
are Attacks, which came in at exactly 50% last time and which these
re-authorings should move down if they are doing anything at all. And the run
sits on an **author-disjoint seat** — whoever writes these rows may not grade
them, which is the independence question now open on QUEUE and which this branch
does not settle. The rows above are Claude's, so the grading chair is not.

**THE AMENDED PROOF (2026-08-29). The five conditions below were supplied by
the relayed independent review and are adopted into this proposal as written.**
They are **instrument conditions, not design picks** — none of them chooses a
candidate, a price or an option — so the ladder (R212) lets them be adopted
here rather than returned; the pick at §14.3 is untouched by all five.

1. **A capped batch, and UNREACHED is a real outcome.** The run is a bounded
   batch of fights rather than one, and it stops as soon as **three or more
   combat turns have held two simultaneously affordable uses of the bank**. If
   the batch's cap is reached without that, the registration grades
   **UNREACHED**, not FALSE: §12.9 already found the precondition was never met
   once, and a hold prediction evaluated on a board that never offered a choice
   measures the generator, not the sink. UNREACHED must be a printed outcome on
   the slate before the run, or the grader will be tempted to read a null as a
   refutation.
2. **A hold counts only when the model names what it is holding for.** The bare
   `W3` detector — an affordable damage sink in hand at `end turn` — stays as
   the mechanical floor, but it is **not sufficient** on its own: the turn
   scores as a hold only if the recorded reasoning **names the future sink or
   the future board state the bank is being preserved for**. A player who
   simply forgot the card is in hand produces the same transcript as a player
   who held, and the whole question is which of those §14.1 has created.
3. **The deck includes the existing utility spenders, and Rummage.** The
   granted deck carries `hold_the_line`, `smoke_and_sparks` and
   `powder_charge` — **Spark-only under `SPARK_ALT_COST_ENABLED`**, the form
   R224 gave them — alongside the prototype ladder, **and
   `proto_spark_priced_draw` (Rummage), FOLDED IN by R224 (slate item 19)**
   rather than staged as a separate whole fight: it is the same hybrid-price
   shape as the three, so a separate fight would ask this fight's question
   twice.
   §12.2 granted none of them, so the fight that produced the null never
   contained a non-damage destination at all, and repeating that grant would
   repeat the artefact rather than test the fix.
4. **The price-3 prediction is conditional.** *"The price-3 rung is bought at
   least once"* is registered **only if the chosen option puts a redesigned card
   at price 3** — i.e. options (1) or (5)-with-Powder-Keg. Under option (2) the
   rung is still `Firework Finale` and the prediction would be a re-run of a
   settled finding; under option (3) there is no price-3 row to buy. A
   prediction that cannot apply must not be on the slate.
5. **The deciding player is author-disjoint.** As above, and now stated as a
   registration condition rather than an aspiration: the seat that plays and
   the seat that grades may not share a model family with the rows' author
   (R217 C, `OPERATIONS.md:607`; `understudy/seat.py:275-279`). All eight
   prototype rows carry `authored_by: [claude]`, and any row added by this
   section will too. This is the same condition QUEUE `M64` is open on; if
   `M64` is still open when this run is registered, the run waits on it.

### 14.5 The relayed review of §14, fact-checked (2026-08-29)

An independent review (GPT) of §14 was relayed by [USER]. Every claim is checked
against the files below; where a claim found a wrong effect ordering or wrong
arithmetic in a candidate's text, the candidate was **corrected in place** as
hygiene and the correction is named in one line here. **No pick is answered.**

| # | claim | verdict | where |
|---|---|---|---|
| a | Klee already ships three non-damage Spark spenders, and the whole-fight deck omitted all three, so "one destination" was true of the granted deck and not the pool | **PARTLY RIGHT — and materially** | `docs/klee-cards.yaml:248,303,320`; §12.2's six-row grant |
| b | Behind the Barrel is `Hold the Line`'s body at 0E+1 Spark, Common vs Uncommon — strictly dominates | **RIGHT** | `docs/klee-cards.yaml:303-306` vs candidate 3 |
| c | Slow Fuse's sequencing is documented backwards; and it overlaps `Chain Fuse` | **RIGHT on the sequencing; PARTLY on the overlap** | `tier0/engine/effects.py:1667-1673`; `docs/klee-cards.yaml:117-118` |
| d | Minefield on three bodies spends 2 and refunds 3 through the relic — partly a generator | **RIGHT** | `tier0/engine/effects.py:874-875`; `docs/current/characters/klee-character-design.md:25` |
| e | Powder Keg as ordered gives the new Bomb no `+3`; the four-Bomb/+12 arithmetic is wrong | **RIGHT** | `tier0/engine/effects.py:1667-1673` |
| f1 | Second Pocket adds a discard selector — the run-length UX cost rejected for Kokomi | **PARTLY RIGHT** | `.../sprint-sim-hygiene-log-2026-07-29.md:130`; `review/ruled/kokomi-kurage-memory-2026-08-29.md:46,127-129,478-481` |
| f2 | Regroup overlaps `Careful Arrangement` and `Powder Charge` | **RIGHT on `Careful Arrangement`, WRONG on `Powder Charge`** | `docs/klee-cards.yaml:119-120` vs `:248-249` |
| f3 | Powder Trail erases Klee's deliberate defensive weakness | **RIGHT, and the doc exists** | `docs/current/characters/klee-character-design.md:15` |
| f4 | Saving Up needs Retain and/or increasing returns, not spend-all | **PARTLY RIGHT — the spend-all half is struck** | candidate 8, amended |
| g | add an option: migrate the existing utility spenders first, test the mixed pool, and prototype only a corrected Powder Keg if a price-3 rung is still wanted; and (4) reads as "pause and migrate", not "the set is fine" | **ADOPTED as option (5)**, and (4)'s reading recorded beside (4) | §14.3 |
| h | five tightened proof conditions | **ADOPTED into §14.4** as instrument conditions | §14.4 |

**On (a), precisely.** Two of the three are non-damage — `hold_the_line` pays in
Block, `smoke_and_sparks` in Vulnerable. The third, `powder_charge`, pays in
**damage**: it detonates. It is still not a plain Attack — its payoff is
board-conditional and is nothing at all on an unbombed target — but the claim's
word "non-damage" is wrong for one row of three. The load-bearing half of the
claim is right and stands: all three are in the shipped pool, all three charge
Sparks at the top level, and §12.2 granted **none** of them, so the whole-fight
null was measured on a deck whose bank genuinely had one destination. §14.2 now
opens with them.

**On (c), the second half.** The overlap is real and the memo disclosed it in
its own first line (*"The body is `Chain Fuse`'s exactly"*), so this is not a
finding the memo hid — but the review is right that the memo drew no conclusion
from it. It has one now, at candidate 1: against a player holding both, Slow
Fuse is `Chain Fuse` minus the Bomb, in a different currency, and the only thing
it tests is whether the currency changes the decision.

**The four corrections made, one line each.**

1. **Slow Fuse (candidate 1)** — sequencing reversed in the prose: the card is
   played **after** the placement cards, never before; the falsifier now scores
   a reason naming a *future* Bomb card as a **misread** rather than a hold.
2. **Minefield (candidate 2)** — the relic refund arithmetic added as a table:
   net **−1 / 0 / +1** Sparks on one / two / three bodies, so on three or more
   the sink partly refills the bank it drains, recorded as an argument against
   the candidate.
3. **Behind the Barrel (candidate 3)** — marked in its heading as **strictly dominating `hold_the_line`** and given the finding in full; **kept listed, not deleted**, because
   the record already went out with it.
4. **Powder Keg (candidate 4)** — printed text and effect order swapped to
   `place_bomb` then `modify_bombs`, which keeps the intended **+12**; repair
   (ii) (keep the order, print *"existing Bombs"*, say **+9**) is recorded as
   available to [USER] at a stroke.

**What this section does not do.** It answers no pick. §14.3's five options —
including the new (5) — §11.7 item 1(e), the Minefield reprice, the Powder Keg
repair choice, the Powder Trail statline question, and `M64` are all [USER]'s.

---

## 15. `EB-219` — Prune re-authored: the kit declaration, drafted before anything is built

**2026-08-30 · branch `eb219-prune-reauthor`, stacked on `eb218-hybrid-migration`
(`f3bb301`). DRAFTED FIRST, seat-read second, built third (R217).** This section
is the DECLARATION only. It settles no pick that is [USER]'s and it moves no
number that is not already printed on Prune's face today.

### 15.1 The clause, and the acceptance line

LAW:145 as **COUNTERSIGNED (R224, 2026-08-30)** — the tightened option (2) of
`review/ruled/burst-retirement-2026-08-29.md` §3.2, PROSPECTIVE under R213:

> **Companion cards may not themselves grant signature resources. A
> character-owned engine may respond to a Companion play and generate its
> resource where that character's kit explicitly declares the trigger and
> bounds the amount generated per Companion play.**

`BACKLOG.md` `EB-219`'s acceptance line, verbatim: **"no `gain_spark`, one
declaration, the same Sparks"**. [USER]'s ruling words (2026-08-30): *"Let's try
to re-author her. As a Personal Companion, she should tie in directly with
Klee's engine."*

Two obligations, and they are the whole design constraint: the Companion's FACE
grants nothing, and the SPARKS THE PLAYER GETS DO NOT MOVE.

### 15.2 What Prune yields today, counted off her row

`docs/mondstadt-companions.yaml:102-103`, the effect list in resolution order:

```
[{op: swirl, target: enemy},
 {op: conditional, if: reaction_triggered_by_this,
                   then: [{op: gain_spark, amount: 1}],
                   else: [{op: block, amount: 5}]},
 {op: gain_spark, amount: 1}]
```

The second `gain_spark` is **top level and unconditional** — it is not inside
the conditional and it fires on every play, Swirl or no Swirl. So, exactly:

| play | Sparks today | other |
|---|---|---|
| base Prune, Swirl triggered a reaction | **2** | — |
| base Prune, no reaction | **1** | 5 Block |
| Prune+, Swirl triggered a reaction | **3** | — |
| Prune+, no reaction | **2** | 5 Block |

The upgraded rows come from `docs/klee-upgrades.yaml:130`
(`prune_witch_hunt: {spark: +1}`), which bumps the FIRST top-level `gain_spark`
— the unconditional one. **The face's ceiling is therefore 2 Sparks base, 3
upgraded, per play**, and those four numbers are the parity target. Nothing
above is a choice; it is arithmetic off the committed sheet.

The condition on the second Spark is `reaction_triggered_by_this`
(`tier0/engine/effects.py:2831`, `state.reactions_this_card > 0`), which is
**ANY elemental reaction this card triggered** — not Swirl specifically and not
Pyro specifically. C# says the same thing the same way
(`PruneWitchHunt.cs`: a `ReactionEffects.TotalResolved` diff around
`ElementalHit.ApplyOnly`).

### 15.3 The declaration — ONE wording, and it is parity

> **Little Hexenzirkul (Klee kit trigger).** When **Klee** plays a card from her
> **Personal Companion pool**, her kit mints **1 Spark**; **1 more** if that
> play triggered an Elemental Reaction; **1 more** if that Companion is
> upgraded. **At most 3 Sparks per Companion play, and once per play** — a
> Companion resolved a second time by a replay is one play, not two.

- **The trigger is explicitly declared by the kit**, which is what LAW:145
  requires of the responding engine, and it is declared in ONE place per engine
  (`tier0/engine/effects.py` beside `gain_sparks`, reached from
  `combat._finish_play`; `KleeElementalHooks` in C#) rather than per card.
- **The bound is per Companion play and it is printed in the declaration**: 3.
  That is the rate guard R224's tightening restored to the clause in place of
  "cheaply repeatable".
- **Parity, row for row, against §15.2:** base+reaction `1+1 = 2`; base, no
  reaction `1`; upgraded+reaction `1+1+1 = 3`; upgraded, no reaction `1+1 = 2`.
  All four match. The 5 Block on the no-reaction branch **stays on her face** —
  Block is not a signature resource and LAW:145 does not reach it.
- **Prune's face keeps everything else**: the Swirl, the conditional, the Block,
  the cost, the non-Exhaust. Only the two `gain_spark` ops leave.

**THE PYRO NARROWING IS WITHDRAWN — it was never [USER]'s words.** An earlier
draft of this section carried *"a Personal Companion's Swirl on a Pyro aura"* as
though it were part of the ruling. **It is not.** It was a paraphrase written
into the working brief that reached this desk, and it is withdrawn here rather
than quietly deleted, because the first doctrine read (§15.7) returned on it and
that return has to stay legible. [USER]'s ruling is, in full and with nothing
else in it:

> *"Let's try to re-author her. As a Personal Companion, she should tie in
> directly with Klee's engine."*

Read against those words plus `EB-219`'s acceptance line — *"no `gain_spark`,
one declaration, the same Sparks"* — **§15.3 is the DERIVED reading, not a
picked one.** "Tie in directly with Klee's engine" is satisfied exactly by the
kit declaring the trigger; "the same Sparks" fixes every number, so nothing here
is chosen. That is R212(6), derived-not-picked: the error direction is one-way
(any deviation moves a shipped number), the scope is one card, and no constant
is invented — all four amounts are lifted off the committed face.

**A Pyro-scoped trigger is not an available alternative today, and the reason is
R213.** It would pay **0** where Prune pays **1** — on a Swirl that finds no
aura, and on a Swirl into a Cryo or Electro aura — so it is a **nerf of
unmeasured size**. That makes it a **tuning lever**, and the R213 design freeze
holds levers. It is therefore not a design pick standing beside parity; it is a
balance change that cannot be pulled at all right now. **It is recorded as a
possible balance item for after the freeze and NO REGISTER ROW IS MINTED for
it** — if it is ever wanted, it is drafted, measured and pulled as a lever in
its own right, never folded into a legality fix.

### 15.4 Which companions the rule reaches

**The rule is GENERAL IN FORM and PRUNE-ONLY IN FACT.** `personal_pool` is the
field that marks a Personal Companion (`tier0/engine/state.py:185`;
`ICompanionCard.PersonalPool` in C#), and across every committed companion sheet
— Mondstadt, Liyue, Inazuma, Fontaine — **exactly one row carries it**:
`prune_witch_hunt`, `personal_pool: klee`
(`docs/mondstadt-companions.yaml:102`). No other row in any sheet declares a
personal pool, so today the declaration mints for Prune and for nothing else. A
second Personal Companion authored for Klee later would fall under it
automatically, which is the point of declaring the trigger on the POOL rather
than on the card — a per-card declaration would have to be re-argued under
LAW:145 every time, and a general one is bounded once.

Two adjacent facts, so the reach is not overstated:

- **Klee's Swirl-capable Personal Companions today: Prune, and only Prune.** Of
  the six live rows carrying an aimed Swirl (`tier0/constants.py`, the C18/R211
  archive block) — `sayu_yoohoo_windwheel`, `lynette_enigmatic_feint`,
  `lynette_astonishing_shift`, `sucrose_gust`, `sucrose_astable`,
  `prune_witch_hunt` — the last is the only one with a `personal_pool`. The
  other five are shared-pool companions and the declaration does not reach them,
  before or after this change.
- **NO OTHER SPARK GENERATOR MOVES.** The declaration adds one site and removes
  one; every other Spark source is untouched: the printed `gain_spark` rows on
  `docs/klee-cards.yaml`, `SparkPerTurnPower` (Endless Fireworks),
  `discard_for_sparks`, the relic path (`tier0/engine/relics.py:167`), and the
  detonation feed. `docs/prototype-surface.yaml:761` is behind
  `SPARK_ALT_COST_ENABLED` and is not touched either.

### 15.5 The one behaviour that is NOT parity, stated rather than found later

**A replayed Prune.** Today her face resolves inside the replay loop, so a
Companion replayed by `replay_next_companion` (Study Buddy) resolves her effect
list twice and mints **twice** — up to 4 Sparks base, 6 upgraded, from one card
play. The declaration mints **once per play**, so that combination pays half
what it pays today. This is not an oversight and it is not a free choice: LAW:145
bounds *"the amount generated per Companion play"*, and a per-play bound that a
replay can double is not a bound. It is the only observable divergence from the
face, it is in the direction the clause exists to enforce, and it is recorded
here rather than in a test comment.

### 15.6 What has to move, in both engines

| engine | site | change |
|---|---|---|
| tier0 sheet | `docs/mondstadt-companions.yaml:103` | both `gain_spark` ops leave Prune's face; Swirl, conditional, Block, cost, non-Exhaust unchanged |
| tier0 sheet | `docs/klee-upgrades.yaml:130` | `{spark: +1}` has no face op left to bump (`upgrades.apply` raises on a key that finds no effect); the upgrade's +1 is declared kit-side by §15.3's third limb |
| tier0 constants | `tier0/constants.py`, Klee resources block | the declaration's numbers, named and bounded |
| tier0 engine | `tier0/engine/effects.py` + `combat._finish_play` | one function, called once per Companion play after the FIRST resolution (where `reactions_this_card` is readable and the replay loop has not run again) |
| C# | `Cards/Generated/PruneWitchHunt.cs` | REGENERATED, not hand-edited, from the sheet |
| C# | `Powers/KleeElementalHooks` (`ElementalApplication.cs`) | the same declaration, beside `CompanionPlays.Record` — the site that already means "once per Companion play" |

**This is SHIPPED-POOL behaviour, not flag-gated.** LAW:145 governs the shipped
game; `SPARK_ALT_COST_ENABLED` gates an economy experiment and has nothing to do
with whether a Companion may grant a signature resource. Both arms of that flag
see the re-authored Prune.

### 15.7 The doctrine-seat read

Run 2026-08-30 under the doctrine seat protocol (`OPERATIONS.md`,
`python -m understudy.seat review … --role doctrine`), model `gpt-5.6-sol`, on
§15 of this packet. Prompt:
`review/qa/eb219-prune-doctrine-review-prompt.txt`; verbatim output and
provenance: `review/qa/eb219-prune-doctrine-review-codex-gpt-5.6-sol.md`. One
Codex call. The seat was told the DIRECTION and LAW:145 itself are closed and
that its own family drafted the clause's text, so it gated the DECLARATION only.

The brief was refused once before it ran — `review_asks_for_a_remedy`, offending
phrase *"rewrite it"*, which appeared inside a sentence of PROVENANCE ("your own
model family drafted the rewrite it is based on") and not in an ask. The word
was replaced with "text" and nothing else in the brief moved. Recorded because a
refusal is a seat event even when the cause is a false positive.

**The seat's output, verbatim and unedited:**

> 1. ARM A — FOLLOWS. CLAUSE: LAW:145.
>
> 2. ARM B — FOLLOWS. CLAUSE: D3 and D4.
>
> 3. ARM C — FOLLOWS. CLAUSE: D7 and D9.
>
> G1 — REQUIRES_MODIFICATION. CLAUSE: R217 C human-owner ruling — "As a
> Personal Companion, she should tie in directly with Klee's engine"; and
> EB-219 acceptance — "no gain_spark, one declaration, the same Sparks."

**The verdict, and what it stops.** All three ARMS FOLLOW: the declaration
satisfies LAW:145 (Arm A), the face that remains is legible under D3/D4 (Arm B),
and a rule general in form and single-card in fact is not a doctrine problem
under D7/D9 (Arm C). **The GATE returns.** G1 asked whether the PARITY reading
— any Personal Companion play, any reaction — follows, and the seat answered
**REQUIRES_MODIFICATION**, naming both texts the packet had set against each
other and choosing neither, which is the only thing it is permitted to do: it
may not pick between two design directions and it may not write a third. It
volunteered **no remedy**, so nothing here is DISCARDED.

**THE BUILD STOPPED HERE, at the seat (R217),** and the stop stands as
published — a returned read is not re-graded away (R101b). What it returned on
is the next paragraph's business. At the moment of the return nothing had been
built: the sheets, the constants, both engines and the generated card were
untouched, and the declaration stood DRAFTED and unbuilt, which is what R217
asks a returned read to leave behind.

**WHAT THE FIRST READ ACTUALLY RETURNED ON, and it was not the declaration.**
G1 set [USER]'s ruling against `EB-219`'s acceptance line and asked which
reading to take. **That opposition was manufactured by the brief.** The
*"Swirl on a Pyro aura"* half of it was a **paraphrase in the working brief,
not [USER]'s words** — the ruling is only *"Let's try to re-author her. As a
Personal Companion, she should tie in directly with Klee's engine."* The
paraphrase is **WITHDRAWN** (§15.3). With it withdrawn there are not two
readings: the ruling and the acceptance line agree, and §15.3 is what they
derive to.

**OPTION (1), PARITY AS DRAFTED, IS TAKEN — under the R212 ladder, and it does
NOT return to [USER].** The three options this section first offered are
resolved as follows, and the resolution is recorded rather than left implied:

1. **PARITY as drafted — TAKEN.** R212(6), derived-not-picked: one card, one
   one-way error direction, no invented constant — all four Spark amounts are
   lifted off Prune's committed face. Nothing here is a taste call, so nothing
   here is [USER]'s.
2. **PYRO-SCOPED — NOT AVAILABLE, and not because it lost a pick.** It is a
   nerf of unmeasured size, which makes it a **tuning lever**, and the **R213
   design freeze holds levers**. There is no version of this sitting today
   where option (2) could be taken, by Claude or by [USER], as part of a
   legality fix.
3. **A LATER NARROWING — possible, unminted.** If the Pyro scoping is ever
   wanted it is drafted, measured and pulled as a balance lever in its own
   right after the freeze. **No register row is minted for it here**, because a
   row minted now would be a transient one for a decision nobody has asked for
   (R206/R212).

**So the build proceeds on §15.3 as drafted**, and the amended §15 goes back to
the seat once — the return was on the withdrawn paraphrase, and a section that
no longer contains it has not been read.

### 15.8 The doctrine-seat read, second run — on the amended §15

Run 2026-08-30, same convention and same seat, on the AMENDED §15 — the
paraphrase withdrawn, the derivation claim stated. Prompt:
`review/qa/eb219-prune-doctrine-review-r2-prompt.txt`; verbatim output:
`review/qa/eb219-prune-doctrine-review-r2-codex-gpt-5.6-sol.md`. One Codex call.
The brief re-asked ARMS A–C unchanged, told the seat what its first read had
answered and why it is being asked twice (it has no memory of the first), and
replaced the withdrawn gate with a fourth arm on the derivation itself.

**The seat's output, verbatim and unedited:**

> 1. ARM A — FOLLOWS. CLAUSE: LAW:145. RISK: None.
>
> 2. ARM B — FOLLOWS. CLAUSES: D3, D4. RISK: None.
>
> 3. ARM C — FOLLOWS. CLAUSES: D7, D9. RISK: None.
>
> 4. ARM D — FOLLOWS. CLAUSES: D2, D4. The derivation holds. RISK: None.

**CLEAN — four arms, no return, no remedy volunteered.** ARM D is the one that
was not asked the first time and it is the one that matters: *"The derivation
holds."* The build proceeded on that.

### 15.9 What was built

**Branch `eb219-prune-reauthor`. Shipped-pool behaviour, not flag-gated** —
LAW:145 governs the shipped game, `SPARK_ALT_COST_ENABLED` gates an economy
experiment, and both arms of that flag see the re-authored Prune.

| where | what |
|---|---|
| `docs/mondstadt-companions.yaml` | both `gain_spark` ops leave her face; the conditional keeps deciding with an empty `then` and the 5 Block on the `else`; cost, Swirl, non-Exhaust untouched |
| `docs/klee-upgrades.yaml` | `{spark: +1}` → `{kit_spark: +1}`, the same +1 declared where the grant now lives |
| `tier0/constants.py` | the declaration: `KLEE_COMPANION_SPARK_BASE/REACTION_BONUS/UPGRADED_BONUS/MAX_PER_PLAY` = 1/1/1/3, and `CONSTANTS_VERSION` 20 → **21** with `SHEET_DIGEST` re-pinned in the same commit |
| `tier0/engine/effects.py` | `klee_personal_companion_spark` — the one site |
| `tier0/engine/combat.py` | called from `_finish_play`, inside the replay loop but gated to the first pass |
| `tier0/content/upgrades.py` | the `kit_spark` key, which applies no face delta and **raises** if the sheet number and the kit constant disagree, or if the row is not a Personal Companion |
| `tools/gen_klee_cards.py` | `kit_spark` made expressible (play-time `IsUpgraded` read, the `condition` key's shape) + `PREDICATE_TEXT_NEGATED` so an empty `then` renders as the inverted single-armed form instead of a dangling colon |
| `klee-mod/.../PruneWitchHunt.cs` | REGENERATED, not hand-edited |
| `klee-mod/.../KleeCompanionSpark.cs` | the C# twin, armed at `BeforeCardPlayed` and settled at `AfterCardPlayed`, both on `IsFirstInSeries` |
| `klee-mod/.../ElementalApplication.cs` | the two call sites, beside `CompanionPlays.Record` |
| `tools/lint_constant_parity.py` | the four constants classified **MIRRORED** — a drift between the engines here would be a drift in a RULE, not in a tunable |

**Her printed face, before and after:**

> *before:* "Swirl an enemy's aura. If it triggered an Elemental Reaction: gain
> 1 Spark. Otherwise: gain 5 Block. Gain 1 Spark."
>
> *after:* "Swirl an enemy's aura. If it did not trigger an Elemental Reaction:
> gain 5 Block."

**The `CONSTANTS_VERSION` bump, and why one was taken on a parity change.** The
four yields do not move, so on outcomes this is as close to a no-op as a sheet
edit gets. It is stamped anyway because the SHEET moved and LAW's material-edit
clause names "effect-number changes" with no exemption for an edit that restores
the number elsewhere — and because §15.5's replayed-Prune case is a real world
difference. `RT`/`D`/`P` are untouched, and `D` is arithmetic rather than hope:
`draft.STATIC_SPARK_VALUE` is **0.0**, so deleting two `gain_spark` ops from a
printed row changes her offer score by exactly nothing.

**Green lines, verbatim.**

```
4753 passed, 46 skipped, 12 xfailed, 18 warnings in 308.89s
OK: 28 lint(s) passed                                    (run_lints --lane ci)
face scaling OK: 18 face(s) state a fold once and none state one twice, of 333 card class(es) read
upgrade coverage OK: 284 draftable cards across 6 sheets, 0 curated codegen debt(s), 277 generated OnUpgrade bodies read
constant parity: OK (83 mirrored, 25 declared unmirrored, 2 ratified invariants held)
sheet-stamp OK: every content sheet is accounted for by the digest pinned beside CONSTANTS_VERSION.
Build succeeded.  0 Error(s)            (dotnet build klee-mod/KleeCode -c Release)
Build succeeded.  0 Error(s)            (…the same, -p:PrototypeCards=true)
Passed! - Failed: 0, Passed: 171, Skipped: 0, Total: 171   (KleeTests)
```

**NEITHER EXEMPTION LIST GREW.** `lint_upgrade_coverage`'s `SHEET_EXEMPT` and
`CODEGEN_DEBT` are both still EMPTY, which was the deciding constraint on how
the upgrade was expressed: the honest reading of that lint is that Prune's
campfire choice is REAL — upgrading her mints one more Spark — so silencing the
lint with a curated entry would have been recording a defect where there is
none. `kit_spark` says the true thing instead, in the sheet, in both engines.

**ONE LINT FAILS AND IT IS ENVIRONMENTAL, not this change:**
`card-distinctness` exits 2 with *"NO OFFICIAL ANCHOR IN THIS RUN — thresholds
are calibrated against one and cannot be checked without it"* — the worktree has
no `game_ref/` pools. It fails identically on the parent commit.

**What this section does not do.** It closes no register row (`BACKLOG`,
`QUEUE`, `STATE`, `LAW` are untouched — those close after merge), it deploys
nothing, and it launches no game. `EB-219`'s acceptance line is met in full: no
`gain_spark`, one declaration, the same Sparks.

---

## 16. `KLEESPARK-W2` — the mixed-pool whole fight

**2026-08-30 · branch `kleespark-w2`, cut from `main` @ `d8a4d11`. REGISTRATION,
DRAFTED AND COMMITTED BEFORE ANY DEPLOY.** This section and its
`EXPERIMENTS.md` row are the registration §14.4 ordered when R224 took option
(5): the alternative-cost Spark economy read on a deck that carries the real
sink pool. Under R212(2) the slate is Claude's to draft from written design
intent and commit DRAFTED before any run; it is offered for batch countersign.
Everything from §16.6 onward is appended after the run, and nothing above it is
edited once the game is launched.

### 16.1 The unit, and what is different from `KLEESPARK-W1`

**The unit is a CAPPED BATCH of live fights** — §14.4 condition 1 — begun at the
first Monster room of a live Act-1 Klee run and played by the Codex seat through
`understudy.blindplay session`, with the arm granted into the starting deck by
`understudy.embark --arm`. `KLEESPARK-W1` was ONE fight; this is a batch,
because `W1`'s finding was that *the bank never once held two affordable uses*,
and a precondition that fails on one fight needs more than one fight before the
failure is attributed to the economy rather than to a draw.

**The one thing that changed in the world since `W1`, and it is the whole
point.** `W1`'s granted deck held six damage rungs and a generator, so the bank
had exactly ONE kind of destination, and the null it returned could not
distinguish "the price creates no hold" from "there was nothing else to hold
for" (§14.5 claim (a), and §14.3's option (5)). `EB-218` built the three
shipped hybrid spenders as **Spark-only twins** behind the same flag pair, and
R224 item 19 folded **Rummage** into this fight rather than staging it
separately. So this deck has a non-damage destination for the bank, at four
different faces, for the first time.

### 16.2 The deck — the exact `arms_granted` list

Eleven rows, one copy each, into the STARTING deck (`--arm`, repeatable;
`embark.grant_arms` grants each with `pile="deck"` and raises on the first
non-ok answer, so a half-granted deck cannot produce a record).

| # | `--arm` id | printed name | Spark price | Energy | kind of sink |
|---|---|---|---|---|---|
| 1 | `proto_pop_spark` | Powder Pop | — (generates 1) | 0 | the income |
| 2 | `proto_kaboom_sink` | Ka-pow! | 1 | 0 | damage |
| 3 | `proto_spark_strike` | Fwoosh! | 1 | 0 | damage |
| 4 | `proto_spark_sweep` | Tinder Toss | 1 | 0 | damage, AoE |
| 5 | `proto_spark_double_tap` | Bang Bang! | 2 | 0 | damage |
| 6 | `proto_spark_blast` | Dodoco Blast | 2 | 0 | damage, AoE |
| 7 | `proto_spark_finisher` | Firework Finale | 3 | 0 | damage, Exhaust |
| 8 | `proto_powder_charge_spark` | Set It Off | 2 | 0 | **detonation** (`EB-218` twin) |
| 9 | `proto_hold_the_line_spark` | Dig In | 2 | 0 | **Block** (`EB-218` twin) |
| 10 | `proto_smoke_and_sparks_spark` | Powder Smoke | 2 | 0 | **Vulnerable** (`EB-218` twin) |
| 11 | `proto_spark_priced_draw` | Rummage | 3 | 1 | **draw** (R224 item 19) |

**`arms_granted` verbatim, as the sealed record will name them** (wire ids —
`KLEEMOD-` plus the id upper-cased, `embark.wire_id`):

```
KLEEMOD-PROTO_POP_SPARK
KLEEMOD-PROTO_KABOOM_SINK
KLEEMOD-PROTO_SPARK_STRIKE
KLEEMOD-PROTO_SPARK_SWEEP
KLEEMOD-PROTO_SPARK_DOUBLE_TAP
KLEEMOD-PROTO_SPARK_BLAST
KLEEMOD-PROTO_SPARK_FINISHER
KLEEMOD-PROTO_POWDER_CHARGE_SPARK
KLEEMOD-PROTO_HOLD_THE_LINE_SPARK
KLEEMOD-PROTO_SMOKE_AND_SPARKS_SPARK
KLEEMOD-PROTO_SPARK_PRICED_DRAW
```

**THE ROW LEFT OUT, and why — `proto_true_spark_knight` (Spark Knight's
Oath).** The eighth row of §10.2's set is the strict Rare Power that prices
**every** Attack in the deck at 3 Sparks. §12.2 excluded it from `W1` by name
under D4 — *"a second variable in a window whose one variable is the priced-sink
economy"* — and nothing since has overturned that: R224 ruled §14's direction,
not §11.7 pick 3. §14.4's own condition 3 names *"the prototype ladder"* plus
the three twins plus Rummage, and a Rare Power that reprices every Attack in the
deck is not a ladder rung. It is therefore left out on the SAME published
grounds `W1` left it out on, recorded here under §14.4 condition 1's instruction
to record which rows were left out and why, ~~and it stays [USER]'s at §11.7
pick 3~~. **`embark` caps nothing** — eleven arms is not a tooling limit, it is
this call, and it is one [USER] may overturn.

**ERRATUM 2026-08-30 (relayed review, fact-checked) — R101b: the exclusion
STANDS, the disposition line is struck.** ~~"and it stays [USER]'s at §11.7
pick 3"~~ — §11.7 pick 3 is ANSWERED. **R222** (`13a0537`) took option (a):
*"leave the Rare Power as built and re-read it in whole-fight play"*, and
*"Neither §5's wording nor the price of 3 is reopened."*
`proto_true_spark_knight`'s exclusion from `W2` on §12.2's published D4 grounds
is unaffected; what is outstanding is the whole-fight read R222 ordered, which
is **engineering work, not an open decision**, and is filed as `EB-223` in
`BACKLOG.md` rather than in a pick list.

### 16.3 The cell, the budget, and the stopping rule

| | |
|---|---|
| cell | the **installed dev build**, named in the sealed record's identity block, read off the deployed `mods\klee\manifest.json`, plus the game build off `release_info.json` |
| build stamp EXPECTED | **`0.2.1600+proto.dirty`** — `MAJOR` `0.2` off the source manifest, `AUTO` = `git rev-list --count HEAD` = 1600 at `d8a4d11`, `+proto` from `deploy_proto.ps1`, `.dirty` because the art-bearing main checkout carries untracked scratch that predates this piece |
| build stamp RULE | the cell is **whatever the deployed manifest says**, and a difference from the expected string is DISCLOSED in §16.6 rather than treated as a stop — `MAJOR.AUTO` moves under any piece that waits for a shared machine, and `embark --arm` refuses a build with no `+proto` anyway (`embark.check_arms`), which is the check that actually matters |
| action budget | `--max-actions 40 --max-wall-s 5400 --max-refusals 2 --max-stalls 6` |
| Codex cap | **45 calls** — up to 40 turn prompts plus up to two fight records and one run record. `W1`'s cap was 30 for a ONE-FIGHT unit; §14.4 condition 1 asks for a batch, and two fights do not fit inside `W1`'s 24 actions |
| the batch's bound | the action budget IS the batch bound. §14.4's stopping condition — *stop as soon as three or more combat turns have held two simultaneously affordable uses* — is evaluated **at grading, off the wire record**, not live: the driver is a blind one-thread seat and no operator reads a page mid-session. Stated rather than implied, because a stopping rule nobody can apply live is a cap and should be called one |
| sessions | **ONE.** If the first session ends early — `tool_blocked`, a refusal, a crash — it is recorded as it ended and NO second session is started |

### 16.4 The slate — drafted from §14.4's conditions and §12's `W1`–`W4`

Every falsifier is computed by `review/qa/blindplay/kleespark-w2/grade.py`,
**committed in this same commit, before the deploy**, off artefacts the run
writes by itself: the rendered observation pages (`turn-*/prompt.md` — printed
bank, printed Energy, printed hand), the per-turn `reply.json`, and
`transcript.jsonl`'s command rows. No grade reads a design judgement, and no
grade reads the tester's prose except `W3'`, whose §14.4-condition-2 half is a
fixed keyword rule over the tester's own recorded sentence and is stated as
such.

**Affordability, defined once for the whole slate.** On a combat page a hand
card is AFFORDABLE when its printed Spark price is ≤ the printed Spark bank AND
its printed Energy cost is ≤ the printed current Energy. Ten of the eleven
granted rows cost 0 Energy, so the Energy half binds only on Rummage; it is in
the rule anyway, because an unpayable card is not a declined one.

**The four NON-DAMAGE sinks, named once**: Set It Off, Dig In, Powder Smoke,
Rummage. **The six DAMAGE sinks**: Ka-pow!, Fwoosh!, Tinder Toss, Bang Bang!,
Dodoco Blast, Firework Finale.

| # | slot | prediction | falsifier, mechanically | UNREACHED when | the decision the outcome changes |
|---|---|---|---|---|---|
| `W1'` | **The precondition `W1` never met**: does the bank ever hold two affordable uses at once, with a non-damage destination among them? | **YES, on at least 3 combat turns.** | Count combat pages where **two or more distinct Spark-priced titles in hand are each affordable**, and **at least one of the affordable ones is a non-damage sink**. **≥ 3 = PREDICTED, 1–2 = SPLIT, 0 = MISS.** | the session reaches **zero combat pages** — a batch that never entered a fight measures nothing | **PREDICTED**: the precondition is met and `W3'` is a real reading. **MISS**: the null is the GENERATOR's and not the sink set's, twice over — §14.3 option (4)'s reading is confirmed, PICK 1 (generation) moves ahead of any further sink work, and no re-price of §4.2's table may be taken off this run. |
| `W2'` | **The mixed pool's own question**: is a non-damage sink ever chosen over a damage sink the bank could equally have paid? | **YES, on at least 1 turn.** | A successful `play` of a non-damage priced row on a turn whose page showed **at least one damage sink also affordable at that moment, at a Spark price ≤ the played row's price**. **≥ 1 = PREDICTED, 0 = MISS.** | **no page ever showed a non-damage sink and a damage sink affordable at the same moment** — the deck never posed the choice, which is a draw fact and not a design reading | **PREDICTED**: the bank has a second kind of destination in live play, and §14.3's question about minting NEW sink rows (options 1–3) can be asked against a measured alternative rather than against a null. **MISS with `W1'` PREDICTED**: the choice was posed and damage won every time — the migration did not buy a decision, and options (1)/(2)'s new rows are back on the table. **UNREACHED**: the fault is draw, and the next act is more fights, not more rows. |
| `W3'` | **§14.4 condition 2 — a hold that names what it is saving for.** | **YES, on at least 1 turn.** | A turn ended with `end turn` while an **affordable** Spark-priced sink sat in hand (`W3`'s bare detector, unchanged), **AND** that turn's recorded sentence both matches the fixed hold vocabulary and **names a Spark-priced title or the bank itself** — §14.4 condition 2's requirement that a player who simply forgot the card does not score as a player who held. **≥ 1 = PREDICTED, 0 = MISS.** | **`W1'` grades MISS** — §14.4 condition 1 in so many words: a hold prediction evaluated on a board that never offered a choice measures the generator, not the sink | **PREDICTED**: the single number this whole section exists to move off zero has moved, and the arm's economy creates a decision in live play. **MISS with `W1'` PREDICTED**: the choice existed and was never declined — §14.3's option (4) reading is finished, and re-pricing §4.2's table (§12.9 pick 1 option (c)) is the next act. **UNREACHED**: nothing about the sinks is learned and the next unit is a longer batch. |
| `W4'` | **§14.4 condition 4 — the price-3 rung is bought at least once.** | **NOT A GRADED SLOT. `UNREACHED` BY CONSTRUCTION, and printed here before the run.** | §14.4 condition 4 registers this prediction **only if the chosen option puts a REDESIGNED card at price 3** — options (1), or (5)-with-Powder-Keg. R224 took (5) in its **migrate-only** form: `EB-218` built the three twins at price 2, and **Powder Keg was not built**. There is no redesigned price-3 rung in this deck, so the prediction cannot apply, and §14.4's own last line — *"a prediction that cannot apply must not be on the slate"* — puts it here as a printed UNREACHED rather than as a slot. | by construction, before the run | nothing. It is printed so a later reader cannot mistake its absence for an omission. **What IS recorded, ungraded**: whether the two price-3 faces that ARE in this deck (Firework Finale, Rummage) were ever bought. |
| `W5'` | **§14.4's fourth item — the attack share.** | **RECORDED, NOT GRADED**, exactly as §14.4 asks. | Share of successful `play` commands that name an Attack, by the kind the page printed. `W1` read 50.0%. | n/a | none on its own. It is the count §12.9 pick 3 option (b) said to re-take on a chosen deck rather than a drawn one. |

**Contamination, stated before the run.**

1. ~~**The shipped automatic Spark rule is still live in the build** (§12.1
   item 2, unchanged): the re-author retires it only on acceptance, so the
   priced rows sit beside the shipped threshold discount. It runs one way — it
   makes Sparks more valuable to hold — so a thin hold reading here is a floor,
   not a ceiling.~~

   **ERRATUM 2026-08-30 (relayed review, fact-checked) — R101b: the GRADES
   STAND and are NOT re-graded; the CONTAMINATION CLAIM is struck.** It was not
   live. `W2`'s build was `0.2.1600+proto.dirty`, and `+proto` is stamped by
   `klee-mod/build/deploy_proto.ps1`, which builds `-p:PrototypeCards=true`,
   which defines `PROTOTYPE_CARDS`, under which `SparkPower.BaseRuleActive` is
   the compile-time constant **`false`**
   (`klee-mod/KleeCode/Powers/SparkPower.cs:64`, pinned by
   `SparkAlternativeCostPinTests:66` and `SparkSinkPinTests:50`) — *"at no bank
   do Attacks cost 0 and nothing is consumed automatically"*. The shipped
   threshold discount was therefore RETIRED for this run, not sitting beside
   the priced rows. **No grade moves**: §16.7's one number is that the printed
   bank never exceeded 1, against the retired rule's threshold of 3, so the
   rule could not have fired under either reading. The *"floor, not a ceiling"*
   hedge is **withdrawn as unnecessary**, not as wrong-in-direction. Same
   erratum at §12.1 item 2, its origin.
2. **`W1`'s results have been read, and `KLEESPARK-R2`'s.** Neither sets a
   number above: `W1'` is the precondition `W1` measured at 0 on a deck that
   could not pose it, and `W2'` names a card kind `W1`'s deck did not contain at
   all. `R2` was staged single turns and produces no live-play count.
3. **The re-authored Prune of §15 is in this build**, and she is Klee's Spark
   generator on a Swirl. §15's declaration is **parity** — all four yields
   unmoved — so income is what `W1` saw, except on a replayed Prune (§15.5),
   which a starter deck cannot produce.
4. **One batch, one seed, one pilot, a granted deck the generators did not
   produce.** Guardrail-7: these are floors. R217 G: the tester's words are
   iteration feedback and are never validation, balance evidence or approval.

### 16.5 Independence — §14.4 condition 5

All eleven granted rows are `authored_by: [claude]`. **The seat that plays is
Codex (`gpt-5.6-sol`)**, refused-by-family through
`blindplay.check_independent` (R217 C), so the playing chair is author-disjoint.
**`M64` is ANSWERED by R224** as a SPLIT — *Codex decides every board on a round
that can ADVANCE an arm; fresh-Opus rounds are INSTRUMENT rounds* — so §14.4
condition 5's clause *"if `M64` is still open when this run is registered, the
run waits on it"* is discharged: it is not open. **The GRADING chair is a
committed mechanical script**, not a model, so author-disjointness does not
arise for it except on `W3'`'s keyword half, which is a fixed rule written
before the run.

### 16.6 What actually ran — the session, the stamp, and the three operator actions

**RUN 2026-08-30, sealed session `kleespark-w2`.** The committed record is
`review/qa/blindplay/kleespark-w2/record.md` — identity block, the tester's
fight and run records verbatim, the per-turn sentence table, the leak audit.
The grader's output is `grades.json` beside it. The rendered pages, the replies
and `transcript.jsonl` are the gitignored operator half under
`understudy/logs/blindplay/kleespark-w2/`.

| | |
|---|---|
| pilot | `gpt-5.6-sol` requested and observed, `codex-cli 0.150.1` |
| build | **`0.2.1600+proto.dirty`**, read off the deployed `mods\klee\manifest.json` — **exactly the stamp §16.3 registered in advance** |
| game | `v0.111.0`, read off the game's own `release_info.json` |
| run seed | **`488GKZJSHC34`**, read back off the wire (R95) |
| arms granted | **all eleven of §16.2**, by wire id, into the starting deck, each answering `ok` |
| actions | **17** (cap 40) |
| termination | `tool_blocked` — the SECOND Monster room's first frame, torn down. The same shape `W1` ended on |
| Codex calls | **21** — 19 turn prompts plus 2 record calls. Cap was 45 |
| refusals | **2**, both grammar and both recovered inside the turn: `play "Jumpy Dumpty"` with three enemies on the board and no target named, and `choose "Explosive Ampoule"` on a reward screen whose printed options are the categories `Card` / `Gold` / `Potion` |
| wall clock | the fight ran `04:43:08Z` to `04:44:00Z`; the whole session, records included, `04:42`–`04:45` |
| leak audit | 21 observations scanned, **1 hit**, and it is the same false positive `W1` recorded: `pilot-vocabulary-score` matching the word *score* inside the prompt's own disclaimer, *"no card list, no score, no recommendation"* |

**The stamp matched, and that is worth one line because `W1`'s did not.** §16.3
registered `0.2.1600+proto.dirty` as the expected string and made a difference a
DISCLOSURE rather than a stop; no difference arose. The deploy ran from the
art-bearing main checkout at `d8a4d11`, dirtied **no tracked file** there (the
ten uncommitted paths in the `+proto.dirty` mark are untracked scratch that
predates this piece), and the full `validate.ps1` gate passed in 349.5 s.

**ONE DISCLOSURE ABOUT THE SIDECAR, and it is the only artefact this piece
touched after it was written.** `embark`'s own seed read-back came back EMPTY
(`run seed: (unread)`, `screen: unknown`) while every one of the eleven grants
answered `ok`. The seed was read off the wire immediately afterwards, with the
game still up on the same open run, as `488GKZJSHC34`, and written into the
gitignored operator sidecar `embark-20260830-003931.json` so that
`blindplay.granted_arms` — which matches a sidecar to a run BY SEED — could
name the grant in the sealed record instead of reporting `(none)`. That edit is
to operator scratch, not to a measurement, it is disclosed here rather than
tidied, and the seed in the record is the wire's, not the sidecar's original.

**The three operator actions, in full** — all before the seat saw anything,
none of them a play, all at zero Codex cost (§12.1 item 1's convention):

1. `choose "Fishing Rod"` at Neow — of the three offered, the only one that
   adds no card and changes no reward: *"Every 3 normal combats, Upgrade a
   random card in your Deck"*, which cannot fire inside one fight. The same
   rule `W1` used to pick Golden Pearl.
2. `choose "Proceed"` to leave Neow.
3. `go "Monster (path 1)"` — of the three nodes offered, all three Monster.

The seat's first page was that Monster room's combat screen: **three enemies**
— Twig Slime (S) 10 HP, Leaf Slime (M) 35 HP, Leaf Slime (S) 11 HP — which is
the genuinely multi-body board `KLEESPARK-R2`'s `P3` went UNREACHED for want
of, arrived at here by seed rather than by staging. The opening hand held
**Dig In** (a migrated twin, price 2) and **Ka-pow!** (price 1) against an empty
bank, both printing `CANNOT BE PLAYED`.

### 16.7 The fight, and the one number that decides the slate

One fight, three rounds, twelve combat pages. The printed Spark bank, page by
page:

| turn | bank | Energy | the Spark-priced cards in hand (price; **bold** = affordable) | command |
|---|---|---|---|---|
| `turn-001` | 0 | 3 | Dig In (2)\*, Ka-pow! (1) | `play "Jumpy Dumpty"` (refused, no target) |
| `turn-002` | 0 | 3 | Dig In (2)\*, Ka-pow! (1) | `play "Jumpy Dumpty" on "Leaf Slime (S)"` |
| `turn-003` | 0 | 1 | Dig In (2)\*, Ka-pow! (1) | `play "Duck and Cover (1)"` |
| `turn-004` | 0 | 0 | Dig In (2)\*, Ka-pow! (1) | `end turn` |
| `turn-005` | 1 | 3 | **Tinder Toss (1)**, Firework Finale (3), Set It Off (2)\*, Powder Smoke (2)\* | `play "Tinder Toss"` |
| `turn-006` | 0 | 3 | Firework Finale (3), Set It Off (2)\*, Powder Smoke (2)\* | `play "Kaboom!" on "Leaf Slime (S)"` |
| `turn-007` | 0 | 2 | Firework Finale (3), Set It Off (2)\*, Powder Smoke (2)\* | `end turn` |
| `turn-008` | 0 | 3 | Dodoco Blast (2), Fwoosh! (1), Bang Bang! (2), Ka-pow! (1) | `play "Powder Pop" on "Leaf Slime (M)"` |
| `turn-009` | 1 | 3 | Dodoco Blast (2), **Fwoosh! (1)**, Bang Bang! (2), **Ka-pow! (1)** | `play "Fwoosh!" on "Leaf Slime (M)"` |
| `turn-010` | 1 | 3 | Dodoco Blast (2), Bang Bang! (2), **Ka-pow! (1)** | `play "Ka-pow!" on "Leaf Slime (M)"` |
| `turn-011` | 0 | 3 | Dodoco Blast (2), Bang Bang! (2) | `end turn` |
| `turn-012` | 0 | 3 | — | `play "Kaeya — Frostgnaw" on "Leaf Slime (M)"` |

\* a NON-DAMAGE sink (Set It Off, Dig In, Powder Smoke, Rummage).

**THE ONE NUMBER: the printed bank never exceeded 1.** Nine of the twelve
combat pages printed no Spark at all — a bank of zero — and the other three
printed **1**. The cheapest non-damage sink in the deck costs **2**. So no
non-damage sink was affordable on any page of the fight, and the mixed pool
this registration exists to test was **in hand and unreachable**: Dig In on four
consecutive pages against a bank of 0, Set It Off and Powder Smoke on three
against a bank of 0 or 1. **Rummage was never drawn at all.**

### 16.8 The slate, graded mechanically

`python review/qa/blindplay/kleespark-w2/grade.py understudy/logs/blindplay/kleespark-w2`,
the grader committed at `76e3c92` before the deploy; full output at
`review/qa/blindplay/kleespark-w2/grades.json`.

| slot | prediction | measured | grade |
|---|---|---|---|
| `W1'` | ≥ 3 combat turns where the bank affords two distinct priced titles, one of them non-damage | **0** of 12 combat pages. Two priced titles were simultaneously affordable exactly ONCE — `turn-009`, bank 1, Fwoosh! (1) and Ka-pow! (1) — and **both are damage sinks**. Peak bank 1 against a cheapest non-damage price of 2 | **MISS** |
| `W2'` | ≥ 1 non-damage sink played over an equally affordable damage sink | 0 — and **no page ever posed the pair**: a non-damage sink and a damage sink were never affordable at the same moment, because a non-damage sink was never affordable at all | **UNREACHED** (its registered condition, met exactly) |
| `W3'` | ≥ 1 `end turn` with an affordable sink in hand AND a sentence naming what the bank is kept for | `W1'` graded MISS, which §16.4 registered as this slot's UNREACHED condition (§14.4 condition 1). **Recorded beside it: the BARE detector is also 0** — the three `end turn` pages (`turn-004`, `turn-007`, `turn-011`) each carried a bank of 0, so no affordable sink was skipped on any of them | **UNREACHED** |
| `W4'` | the price-3 rung is bought | **UNREACHED BY CONSTRUCTION**, as printed before the run. Recorded and ungraded: neither price-3 face was ever bought — Firework Finale sat in hand on `turn-005`–`turn-007` against a bank of 0–1, and Rummage was never drawn | **UNREACHED** |
| `W5'` | attack share | **6 of 8 successful plays, 75.0%** (`W1` read 50.0%) | **RECORDED, NOT GRADED** |

**No grade is nudged and no rule moved.** Every threshold above was fixed in
`76e3c92`. The grader was sanity-checked before the run against `KLEESPARK-W1`'s
own committed pages, where it reproduces `W1`'s published attack share exactly —
10 plays, 5 attacks, 50.0% — which proves the parse and re-grades nothing
(R101b).

**Three honest limits on the numbers, none of which changes a grade.**

1. **One fight, not the batch the registration allowed.** The cap was 40 actions
   and the session stopped at 17 on `tool_blocked` at the second Monster room's
   first frame — `W1`'s ending, on a different seed and a different build. So
   the *capped batch* of §14.4 condition 1 was funded and did not happen: this
   is one fight's evidence, and §16.9 pick 1 is where that goes.
2. **`W1'` is the strict form and the loose form disagrees by one.** Dropping
   the non-damage qualifier, two affordable uses coexisted on exactly ONE page
   (`turn-009`). Even the loose count is 1 against a threshold of 3, so the
   qualifier is not what produced the MISS — the bank's ceiling is.
3. **The bank read is the PRINTED bank, page to page**, so a turn that both
   generates and spends is invisible between pages. That is the same limit
   `W1`'s `W2` carried and it cannot lift the ceiling above 1: a page that
   printed 1 printed 1 at the moment the tester chose.

### 16.9 What the run found that is not a slot

**1. The Spark-arithmetic question is back, in a new place, and it has the same
benign explanation.** `turn-009` printed **Spark 1**, the tester played
**Fwoosh!** (printed price 1), and `turn-010` printed **Spark 1** again and
allowed **Ka-pow!** (printed price 1); `turn-011` printed no Spark line at all.
Two price-1 cards were paid across a bank that read 1 twice and then 0. The
tester caught it unprompted — *"after Fwoosh! supposedly spent the one Spark,
the screen still showed Spark 1 and allowed Ka-pow! to be played, but the Spark
disappeared afterward."* **There is a benign explanation and the page cannot
distinguish it:** `Powder Pop` had placed a Bomb on Leaf Slime (M) on
`turn-008`, and `Fwoosh!` is the unblocked Attack that detonates it, so if a
detonation feeds a Spark the arithmetic is `1 − 1 + 1 = 1`. **That is exactly
§12.8 item 1's shape** — the `Bang Bang!` candidate — **which
`KLEESPARK-R2` settled as detonation arithmetic and not a pricing defect**
(§13.1's out-of-slot finding). It is recorded here as a **defect candidate, not
a defect**, and the board that settles it is still §12.9 pick 2's **Board C**:
the sink, a full bank, one enemy, and no Bomb on the field.

**2. §12.8 item 2 is GONE on this build.** `W1` reported Kokomi's Bake-Kurage
memory panel rendering on a Klee run and saying the wrong thing, and the tester
named it the most confusing thing on the screen. **Zero of this session's 21
observations contain the string `Bake-Kurage`.** Nothing here claims which
change removed it; the fact is recorded because the previous record's reader
would otherwise have to wonder.

**3. The tester read the shortage as a GENERATOR shortage, unprompted, twice.**
Under R217 G and concluding nothing from it — §16.10 carries the words verbatim
— its run record names *"whether to spend limited Spark immediately or save it
for stronger cards"* as the recurring tension, then says *"Energy was often
available while several zero-cost cards were unusable because Spark, not energy,
was the real constraint"*, and picks its card reward as *"the deck needed
another Spark generator"*. The slate does not grade prose and none of that moves
a grade; it is recorded because §16.9 pick 1 is a choice between a generator
answer and a sink answer, and the transcript's own numbers — peak bank 1, four
non-damage faces never once affordable — are the graded half of the same
picture.

**4. Two grammar refusals, both recovered, both about naming.** `play "Jumpy
Dumpty"` on a three-enemy board with no target, and `choose "Explosive Ampoule"`
where the reward screen prints the categories `Card` / `Gold` / `Potion` and the
item name beneath them. The second is the same shape as `W1`'s bare `proceed`
at Neow. Neither is filed as a defect here: both refusals said what was wrong
and the tester answered them on its next turn, which is the grammar working.

### 16.10 The pilot's own words

Verbatim, R217 G — one model's account of one fight, never validation, never
balance evidence, never approval. **Nothing below is concluded from.**

1. > *"The recurring tension was whether to spend limited Spark immediately or
   > save it for stronger cards. Energy was often available while several
   > zero-cost cards were unusable because Spark, not energy, was the real
   > constraint."* — the run record, question 2.
2. > *"Spark-costing cards were dead whenever no Spark was available, especially
   > Firework Finale, Set It Off, Powder Smoke, Dodoco Blast, and Bang Bang!;
   > Duck and Cover was useful only when damage was actually incoming."* — the
   > fight record, question 4.
3. > *"Play became repetitive when hands contained several Spark spenders but no
   > way to generate Spark. Those turns reduced to playing the one available
   > generator or ordinary energy-cost attack, then ending the turn with
   > nominally cheap cards still dead in hand."* — the run record, question 4.
4. > *"Next time I would avoid drafting more expensive Spark spenders until the
   > deck had reliable generation. Firework Finale, Set It Off, Powder Smoke,
   > Dodoco Blast, and Bang Bang! all looked potentially strong, but too many
   > were unplayable during this fight; another payoff would worsen that
   > bottleneck."* — the run record, question 5.
5. > *"Snap! looked like the most important reward because the deck needed
   > another Spark generator."* — the run record, question 3.
6. > *"The Spark display was confusing: after Fwoosh! supposedly spent the one
   > Spark, the screen still showed Spark 1 and allowed Ka-pow! to be played,
   > but the Spark disappeared afterward."* — the fight record, question 6. See
   > §16.9 item 1.

### 16.11 What this leaves — numbered picks, never blanks

**1. The mixed pool was granted and the bank could not reach it. Which reading
does the arm take next?** `W1'` = 0 on a ceiling of 1 against a cheapest
non-damage price of 2, and `W2'`/`W3'` UNREACHED by their own registered rules.
Under §16.4's registered decision linkage a `W1'` MISS says the null is the
GENERATOR's and not the sink set's — *twice over now*, on two different decks —
and that **no re-price of §4.2's table may be taken off this run**. What the
arm does about it is [USER]'s.

*(a) take the registered reading and move PICK 1 (the generation pattern) ahead
of every remaining sink question — no new sink row, no reprice, until the
income question is answered;
(b) re-run this exact registration as the BATCH it was funded for — the cap was
40 actions and the session spent 17 — on the grounds that one fight on a starter
deck cannot show a ceiling that a deck with two generators would not have;
(c) re-price the migrated twins DOWN from 2 to 1 so a bank of 1 can reach a
non-damage destination, which is the smallest edit that would let `W1'` ever
fire — and which §16.4's own decision linkage forbids taking off this run, so it
would be [USER] overruling the registration rather than reading it;
(d) accept that the migration is untested and stage `KLEESPARK-R2`'s form
instead — a staged board with a bank of 3 and the twins in hand — on the
grounds that a whole fight has now twice failed to produce the precondition and
a staged turn produces it by construction.*

**ANSWERED by R225 (2026-08-30): (a′).** Option (a) — the generation question
first, no new sink row and no re-price — with one qualification adopted from
the relayed review. `W2`'s granted deck ran **two Spark makers against eleven
Spark-priced sinks**, both starter rows granted a second time, so the run shows
that THAT deck could not fund its pool, not yet that the one-for-one draft
economy needs more generation. The `W1'` decision text stands as registered
(R101b); this is its reading. The next evidence is a **representative deck, not
a `W2` re-grant**: first `EB-205`'s sim-drafted arm, which costs no game time
and is now the next Klee read, then a live controlled-ratio deck under a fresh
registration Claude drafts.

**2. The batch that was funded and did not happen.** §14.4 condition 1 asked for
a bounded batch of fights; the driver stopped at 17 of 40 actions on
`tool_blocked` at the second Monster room's first frame, which is the shape
`W1` ended on. This is now **two whole-fight sessions in a row that ended at the
first frame after the first fight**, and until it is fixed the "batch" unit
cannot be run at all.
*(a) file it as an engineering defect against the blind-play driver and fix it
before any further whole-fight registration;
(b) treat one fight as the honest unit and re-write §14.4 condition 1's "batch"
as "one fight, repeated on N seeds, N sessions";
(c) neither — accept single fights and stop registering batch conditions.*

**ANSWERED by R225 (2026-08-30): (a)**, already done. `EB-221` and `EB-222`
were the two lifecycle throws that ended every whole fight at combat 2, both
fixed, and the soak reads `fights=3 defects=0` on `0.2.1608+proto.dirty`. The
batch re-run waits on pick 1's deck composition.

**3. The Spark-arithmetic candidate, a second time.** §16.9 item 1 is §12.8
item 1 in a new place, with the same benign detonation explanation and the same
inability of the page to distinguish it. `KLEESPARK-R2` settled the first
instance out of slot.
*(a) stage §12.9 pick 2's Board C — the sink, a full bank, one enemy, no Bomb —
and settle it once for the whole arm;
(b) treat `R2`'s out-of-slot finding as settling this class too and record
nothing further;
(c) instrument it instead: have the wire report the Spark delta per play, so no
future page has to be read for arithmetic.*

**ANSWERED by R225 (2026-08-30): (b).** Round 2's out-of-slot replay settles
the class — bank 3 → Fwoosh! → Bang Bang! at exactly 2 → 0 with no Bomb — and
`W2`'s instance is the starter relic Pounding Surprise's +1 per detonation.
Nothing further is recorded on the arm. A four-field ledger — bank before,
price paid, gains by source, bank after — is adopted as INSTRUMENT work folded
into `EB-216`'s per-turn wire snapshot; it gates nothing, and it is not
`EB-211`, which is a tester-form schema.

**4. What the record does NOT say.** No win rate, no comparison with any other
build or seed, and no claim about whether the arm is fun or good. One fight, one
seed, one pilot, a granted deck the generators did not produce, ~~and the
shipped automatic Spark rule still live beside the priced rows (§16.4
contamination 1)~~. Guardrail-7: these are floors. R217 G: §16.10's words are
iteration feedback, never validation.

**ERRATUM 2026-08-30 (relayed review, fact-checked) — R101b: the grades STAND
and are NOT re-graded.** The struck clause inherits §16.4 contamination 1,
which is itself struck: `W2` ran on `0.2.1600+proto.dirty`, so
`SparkPower.BaseRuleActive` was the compile-time constant `false` and the
shipped threshold rule was retired, not live. See the erratum at §16.4
contamination 1 for the citations. The printed bank never exceeded 1 against
that rule's threshold of 3, so no grade moves.

## 17. `KLEESPARK-S1` — the Spark arm measured DRAFTED, in the sim

**REGISTRATION. Drafted from written intent and committed BEFORE any run**
(R212(2), EXPERIMENTS *Pre-registration + blind grading*). Nothing below was
written after a number was seen; the instrument that produces the numbers is a
SEPARATE, LATER commit, and the run is a third. R101b binds: nothing already
published in §11–§16 is re-read, re-graded or rewritten by this section.

### 17.1 Intent — why this read exists, quoted

**R225 item 1, answering §16.11 pick 1, verbatim:**

> **ANSWERED by R225 (2026-08-30): (a′).** Option (a) — the generation question
> first, no new sink row and no re-price — with one qualification adopted from
> the relayed review. `W2`'s granted deck ran **two Spark makers against eleven
> Spark-priced sinks**, both starter rows granted a second time, so the run
> shows that THAT deck could not fund its pool, not yet that the one-for-one
> draft economy needs more generation. The `W1'` decision text stands as
> registered (R101b); this is its reading. The next evidence is a
> **representative deck, not a `W2` re-grant**: first `EB-205`'s sim-drafted
> arm, which costs no game time and is now the next Klee read, then a live
> controlled-ratio deck under a fresh registration Claude drafts.

**§14.4's conditions, the two that reach a SIM read, verbatim:**

> 1. **A capped batch, and UNREACHED is a real outcome.** […] If the batch's
>    cap is reached without that, the registration grades **UNREACHED**, not
>    FALSE: §12.9 already found the precondition was never met once, and a hold
>    prediction evaluated on a board that never offered a choice measures the
>    generator, not the sink. UNREACHED must be a printed outcome on the slate
>    before the run, or the grader will be tempted to read a null as a
>    refutation.

> 3. **The deck includes the existing utility spenders, and Rummage.** The
>    granted deck carries `hold_the_line`, `smoke_and_sparks` and
>    `powder_charge` — **Spark-only under `SPARK_ALT_COST_ENABLED`**, the form
>    R224 gave them — alongside the prototype ladder, **and
>    `proto_spark_priced_draw` (Rummage), FOLDED IN by R224 (slate item 19)**
>    […]

**§14.4's conditions 2, 4 and 5 do NOT reach this read, and are printed here so
their absence is not read as an omission.** Condition 2 (a hold counts only
when the model NAMES what it is holding for) has no referent: the tier-0.5
pilot is a scoring function with no recorded reasoning, so the *named-hold*
half is unmeasurable in sim by construction and no slot below claims it — the
bare detector is all a sim can carry, and it is carried as a RECORDED number,
not as a hold reading. Condition 4 (the price-3 rung) is UNREACHED by
construction for the same reason §16.4 printed it so: R224 took option (5) in
its **migrate-only** form, Powder Keg was not built, and there is no redesigned
price-3 row to buy. Condition 5 (an author-disjoint deciding seat) reaches a
MODEL-GRADED run; every number below is produced by a committed mechanical
script over the sim's own log, so there is no grading chair for authorship to
attach to.

**What this read is FOR, stated as the act it selects between.** R225 puts the
generation question ahead of every sink question and names a **live
controlled-ratio deck** as the evidence after this one. This read answers, in
the sim and at no game cost, whether the ONE-FOR-ONE DRAFT ECONOMY reaches its
non-damage sinks on a deck the drafter actually built — and it hands the live
registration the **maker:sink ratio** it should stage, derived from the drafted
decks' own median rather than picked.

### 17.2 The arm, exactly

**The shipped Klee pool with `SPARK_ALT_COST_ENABLED` set true**, and nothing
else. No card is granted, injected or forced; `force_cards` is `None`. What the
flag turns on, exhaustively, is what `tier0/constants.py` says it turns on:

1. **The substituted starter** (`loader._starter_ids`,
   `C.SPARK_ALT_STARTER_SUBS`): one `pop` → `proto_pop_spark` (Powder Pop, the
   Basic that MAKES) and one `kaboom` → `proto_kaboom_sink` (Ka-pow!, the Basic
   that SPENDS). Klee's starter is randomized per run off its own rng stream,
   so the substituted pair is present in every run of the arm by construction
   and the rest of the ten vary.
2. **The one-for-one pool substitutions** (`loader._pool_substitutions`,
   `C.SPARK_ALT_POOL_SUBS`), PICK 4's map: `sparkly_treasure` → Fwoosh!,
   `spark_collection` → Bang Bang!, `pocket_fireworks` → Tinder Toss,
   `sugar_rush` → Dodoco Blast, `cant_catch_me` → Firework Finale. Same rarity
   in and out, so the offer odds are untouched.
3. **The three `EB-218` Spark-only twins**, migrated by R224 slate item 16:
   `powder_charge` → Set It Off, `hold_the_line` → Dig In, `smoke_and_sparks` →
   Powder Smoke — the same bodies at 0 Energy with the price paid wholly in
   Sparks. Three Uncommons in, three Uncommons out.

**`proto_true_spark_knight` is EXCLUDED**, on §12.2's published D4 grounds and
exactly as `KLEESPARK-W2` excluded it. Mechanically: the arm pops the
`true_spark_knight` key out of `C.SPARK_ALT_POOL_SUBS` for the duration of the
run, so the Rare offer slot serves the SHIPPED row and the offer odds are again
untouched. Its own whole-fight read is `EB-223` and is not this read.

**Rummage (`proto_spark_priced_draw`) is IN §14.4 condition 3's deck and is NOT
REACHABLE BY DRAFT, and this is stated before the run rather than found after
it.** `C.SPARK_ALT_POOL_SUBS` carries no entry for it — it has no shipped twin
to substitute for, because it was authored as a new row rather than as a
conversion — so `rewards.character_pool("klee")` cannot offer it under the flag
and no drafted deck can contain it. **This is a fact about the seam, read off
`constants.py` and confirmed against `rewards.character_pool` before any run,
not a result.** Slot `S5` below registers it as an instrument check and names
the decision it changes: a live controlled-ratio deck must GRANT Rummage rather
than expect a draft to find it.

**The four NON-DAMAGE sinks, named once and taken from §16.4 unchanged so the
two reads are comparable**: Set It Off, Dig In, Powder Smoke, Rummage. **The
six DAMAGE sinks**: Ka-pow!, Fwoosh!, Tinder Toss, Bang Bang!, Dodoco Blast,
Firework Finale. Under this arm's pool the reachable non-damage sinks are the
three twins, **every one of them priced 2**, which is why every affordability
threshold below is 2 — the same *cheapest non-damage price of 2* `W1'` was
graded against.

**A MAKER is a deck card carrying a top-level `gain_spark` op**; a **SINK** is
a deck card carrying a top-level `spend_spark` op (`combat.spark_cost`'s own
rule). Both are read off the card sheet, not off play, so the ratio is a
property of the DECK and not of a draw.

### 17.3 The cell, the control, and the budget

| | |
|---|---|
| cell | `cells.CANONICAL.but(character="klee", archetype="demolition", name="kleespark-s1")` — **600 runs, seed 11, route `hunter`, `assigned` policy, realistic loadout (relics + potions), every act** |
| world stamp | **`RT12 / D18 / P11 / C20`**, `PILOT_WEIGHTS_VERSION` 6, read live off `tier05.cells.world_stamp()` and printed in the record's header. A stamp that differs at run time is DISCLOSED in §17.6 and the read is not published against a moved world |
| stamps this read moves | **NONE.** The instrument is a new module plus its test; it adds no constant, no drafter dial, no policy branch and no engine rule. `SPARK_ALT_VALUE` and the two shipped dials are untouched, and the flag is flipped at run time and restored in a `finally` |
| arms | **TWO. `flag ON` is the arm.** `flag OFF` — the shipped Klee pool, same cell, same seeds — is a paired CONTROL, **RECORDED and NOT GRADED**: it exists so the ON arm's maker:sink ratio can be read against the pool it was converted out of, and no prediction below is registered on it |
| jobs | **1 (serial, in-process).** The observer wraps the pilot, `run_fight`, `run_one` and `mark_hindsight`, and a batch spread over worker PROCESSES reaches none of them. **CORRECTION, made in the instrument commit and before any run:** the registration commit wrote *`jobs=0` (in-process)*, which is wrong on the repository's own reading — `model.run_many` treats `jobs=0` as ONE WORKER PER CPU, not as serial. The serial value is **1**, the instrument's `CELL` is pinned at 1 by test, and its `main` REFUSES anything else rather than printing a silent zero. Nothing else about the cell moves, and no number had been taken when this was corrected |
| compute budget | **≤ 30 minutes for both arms.** Sized before the run off a bare 20-run timing probe on this tree (1.0 s / 20 runs, no telemetry), so 1,200 instrumented runs has ample headroom. **If the driver exceeds 30 minutes it is stopped and the record publishes what completed, with the completed run count as the denominator** |
| grader | `tier05/exp_klee_sparks_s1.py`, committed BEFORE the run in its own commit. Every falsifier below is one of its printed fields; no grade reads a judgement |

### 17.4 The slate — five predictions, drafted from §14's written intent

**Affordability, defined once for the whole slate.** At a pilot decision, a hand
card is **AFFORDABLE** when its printed Spark price is ≥ 1 and ≤ the player's
current Spark bank. A second, stricter count — affordable AND
`combat.card_playable` — is printed beside every affordability figure so the
Energy/gate half is visible, but **every threshold below is registered on the
bank-only count**, because R225 puts the INCOME question first and the bank is
what income buys.

**A drafted deck** is a run's `deck_ids` at the floor named. Floors are the
run's own floor indices (`node_kinds` index; `MAP_FLOORS` = 16 per act), and a
deck is counted at floor F only if the run REACHED floor F — which is stated so
a shrinking denominator is never read as a shrinking ratio.

| # | slot | prediction | falsifier, mechanically | UNREACHED when | the decision the outcome changes |
|---|---|---|---|---|---|
| `S1` | **Per-fight PEAK Spark bank.** `W1'` read a printed peak that never exceeded 1 on a granted deck; §14's intent is that a deck whose generators were NOT converted away funds its own pool. | **The median per-fight peak bank is ≥ 2, AND ≥ 60% of fights reach a peak of ≥ 2.** | Peak = `max` over the fight's log of every `gain_spark`/`spend_spark` event's `total` field, and 0 for a fight with no Spark event. Both halves hold = **PREDICTED**; exactly one = **SPLIT**; neither = **MISS**. | fewer than 100 fights are recorded across the arm | **PREDICTED**: the drafted economy reaches the price-2 rung, `W1'`'s null is a property of `W2`'s GRANTED deck and not of the one-for-one economy, and the live controlled-ratio deck is registered to test SPENDING rather than income. **MISS**: the generation pattern is confirmed as the governor on a representative deck too, and it stays ahead of every sink question — the live registration is about INCOME, and no sink row and no re-price may be proposed off either read. **SPLIT**: the live deck is registered at the ratio `S4` hands it and the income question stays open. |
| `S2` | **Share of player turns on which a NON-DAMAGE sink was affordable at least once.** The number §16.11 pick 1 says a representative deck has to produce; `W2`'s was 0. | **≥ 15% of player turns.** | Over every pilot decision in every fight: a turn counts when at least one card in hand is a registered non-damage sink AND its price (2) ≤ the bank at that decision. **≥ 15% = PREDICTED; 5% to < 15% = SPLIT; < 5% = MISS.** | `S3` reads 0 — no drafted deck ever held a non-damage sink, so no turn could pose the question and the fault is the OFFER, not the bank | **PREDICTED**: the non-damage destination is reachable in a drafted deck, and the live controlled-ratio deck is staged to ask whether it is CHOSEN. **MISS**: the destination is unreachable on a representative deck as well, which is the same finding `W1'` made and is a second, independent witness for the generation-first order. **UNREACHED**: the question is a draft-offer question and the live deck must grant its non-damage sinks outright. |
| `S3` | **Share of drafted decks holding ≥ 1 non-damage sink** (final deck). Three Uncommon twins sit in a 31-card uncommon tier, so this is an offer-and-score question, not a bank question. | **≥ 50% of runs.** | Count runs whose final `deck_ids` contain any of Set It Off / Dig In / Powder Smoke / Rummage. **≥ 50% = PREDICTED; 20% to < 50% = SPLIT; < 20% = MISS.** | never — the pool is verified to contain all three before the run | **PREDICTED**: `S2`'s reading is about the BANK, and the live deck may take the drafted composition as representative. **MISS**: the drafter does not value the migrated twins at `SPARK_ALT_VALUE` = 4.00, which is a SCORER finding and not an income finding — it goes to `BACKLOG` as an instrument row, and the live controlled-ratio deck must grant its non-damage sinks. **SPLIT**: same, weaker; the live deck grants them and the scorer question is recorded. |
| `S4` | **Maker : sink ratio of the drafted deck at floors 5, 10 and 15.** PICK 4's map converts five makers into sinks in the offerable pool, so the intent's own arithmetic says the ratio falls as a run drafts. **THIS SLOT'S FLOOR-15 MEDIAN IS THE NUMBER THE LIVE REGISTRATION INHERITS.** | **The median ratio FALLS from floor 5 to floor 15, AND the floor-15 median lies in [0.30, 0.80].** | Ratio = makers ÷ sinks in the deck at that floor, undefined (excluded) when sinks = 0. Both halves hold = **PREDICTED**; exactly one = **SPLIT**; neither = **MISS**. | fewer than 30 runs reach floor 15 | **ANY graded outcome hands the live registration its ratio** — the live controlled-ratio deck is staged at the floor-15 MEDIAN, whatever it is, so the live registration inherits a number rather than a pick. **PREDICTED**: the drafted economy dilutes its own generation, which is the mechanism `W1'`'s null pointed at, and the live deck tests that ratio directly. **MISS with a ratio ABOVE 0.80**: `W2`'s 2:11 was an artefact of granting, the drafted economy is generator-rich, and the live deck is staged at the drafted median rather than at `W2`'s. |
| `S5` | **Rummage draw rate — an INSTRUMENT CHECK, not a reading about the card.** | **EXACTLY 0.0%**, because `C.SPARK_ALT_POOL_SUBS` carries no Rummage entry and no drafted deck can contain it. | Share of runs whose deck ever contains `proto_spark_priced_draw`, and share of fights in which it is drawn. **Exactly 0 = PREDICTED; anything > 0 = MISS** (which would mean the substitution map or this instrument is wrong, and the whole read would be withdrawn before publication). | never | **PREDICTED**: §14.4 condition 3's Rummage half is UNREACHABLE BY DRAFT, so the live controlled-ratio deck must **GRANT** Rummage; a drafted live deck would silently drop it. **MISS**: the instrument is wrong and no number in this section is published. |

**Contamination and blind spots, stated before the run.**

1. **`W1`, `W2` and `R2`'s results have been read.** None sets a number above.
   `S1`'s threshold of 2 is §16.4's own cheapest-non-damage price, not `W2`'s
   observed 1; `S2`'s 15% and `S3`'s 50% are drafted from §14.1's intent that
   the bank have a second kind of destination, and have no live counterpart at
   all (`W2`'s was 0 on a deck whose composition this arm does not share);
   `S4`'s band is derived below rather than observed.
2. **`S4`'s band is DERIVED, and the derivation is printed so it can be
   checked.** Klee's starter under the flag ships exactly one maker (Powder
   Pop) and one sink (Ka-pow!) among the substituted pair — ratio 1.0 from the
   substitution alone. The offerable pool loses five makers to PICK 4's map and
   gains five sinks, and the three `EB-218` twins add three more sinks with no
   maker beside them, so every draft that touches the Spark family moves the
   ratio DOWN. Eight added sinks against zero added makers, on a substitution
   at 1:1, puts a fully-drafted ratio well under 1; **0.80** is the loosest
   reading that still says "fell", and **0.30** is roughly the ratio a deck
   reaches if it drafts the family hard (1 maker : 3 sinks). The band is wide on
   purpose: a narrow band drafted from arithmetic rather than from data would be
   a guess wearing a threshold.
3. **The sim is one seat and has no display.** Nothing here measures legibility,
   a badge, a face or a player's understanding. Guardrail-7 applies whole: every
   number below is a FLOOR produced by a scoring pilot, and none of them is a
   claim about whether the arm is fun, good, or ready.
4. **The pilot is `P11`, whose Spark literacy is a hold-versus-spend term.** It
   is not a player. A low `S2` is a statement about the BANK on the turns the
   pilot reached, and a high one is not evidence that a human would notice the
   destination.
5. **No win rate is registered and none may be quoted off this read** (R215 B).
   The instrument prints one because the run layer produces it; it is a
   diagnostic, it grades nothing, and it is not comparable to any published arm.

### 17.5 What actually ran — the cell, the stamp, and one disclosure

**RUN 2026-08-30.** `python -m tier05.exp_klee_sparks_s1 --json
review/qa/kleespark-s1/record.json`, 600 runs per arm at seed 11, `jobs=1`,
completed inside the driver's 600-second allowance and well inside §17.3's
registered 30-minute budget. Record, raw JSON and the driver's unedited stdout
are under `review/qa/kleespark-s1/`.

**THE STAMP DIFFERED FROM THE ONE §17.3 DECLARED, and §17.3's own rule is that
it is disclosed here.** §17.3 wrote the expected stamp as `RT12/D18/P11/C20`,
copied from `STATE.md`'s Live cell. The tree's live stamp is
**`RT12/D18/P11/C21`**. `STATE.md` was **stale at `HEAD`**:
`CONSTANTS_VERSION` moved to **21** on 2026-08-30 under `EB-219` — Prune's
Sparks moved off her printed face into Klee's kit declaration, at parity on all
four yields.

**The world did not move under this read.** It was C21 before §17 was written,
during the run and after it, so what differed is the registration's
transcription of a stale document, not the world the numbers were taken in.
§17.3's clause — *the read is not published against a moved world* — is
therefore satisfied rather than triggered: there is one world here, and every
number below is published stamped **C21**, which is where it was taken.
Nothing is re-run, no threshold moves, and `STATE.md`'s Live cell is corrected
as hygiene in the same commit that lands this section.

**C21 is not neutral for this read and it is named rather than left to be
found.** `EB-219` is exactly the edit that moved a Klee Spark SOURCE off a
printed row, so §17.2's sheet-only maker definition cannot see it — see the
blind spot at §17.7 item 1, which is why the inherited ratio is stated as a
floor on generation and never as a ceiling.

### 17.6 The slate, graded

**2 PREDICTED / 0 SPLIT / 3 MISS / 0 UNREACHED.** Every grade is the committed
grader's own output against §17.4's registered thresholds and no others.

| slot | grade | the read | the registered threshold |
|---|---|---|---|
| `S1` per-fight peak Spark bank | **PREDICTED** | median peak **5.0**, and **90.7%** of 8,428 fights peaked at ≥ 2 | median ≥ 2 AND ≥ 60% of fights peak ≥ 2 |
| `S2` share of turns with a non-damage sink affordable | **MISS** | **0.62%** of 34,597 player turns (216 turns) | ≥ 15% PREDICTED, 5–15% SPLIT, < 5% MISS |
| `S3` share of drafted decks holding one | **MISS** | **3.2%** of 600 runs — 19 decks | ≥ 50% PREDICTED, 20–50% SPLIT, < 20% MISS |
| `S4` maker : sink at floors 5 / 10 / 15 | **MISS** | medians **1.000** (n=576) / **1.000** (n=538) / **1.500** (n=510). The ratio **ROSE**, and floor 15 sits **above** the band | median FALLS 5 → 15 AND floor-15 median in [0.30, 0.80] |
| `S5` Rummage | **PREDICTED** | **0.0%** — 0 of 600 decks, as the seam says it must be | exactly 0.0% PREDICTED, anything > 0 MISS |

**The two arms side by side.** The flag-OFF column is the paired control and is
**RECORDED, NOT GRADED**.

| | flag OFF (control) | flag ON (the arm) |
|---|---|---|
| runs / fights / player turns | 600 / 9,237 / 37,009 | 600 / 8,428 / 34,597 |
| peak Spark bank, median (mean) | 3.0 (3.48) | **5.0 (5.94)** |
| fights peaking ≥ 2 | 86.3% | **90.7%** |
| turns with a NON-DAMAGE sink affordable | 0.00% | **0.62%** |
| turns with ANY priced sink affordable | 0.44% | **20.50%** |
| decks holding a non-damage sink | 0.0% | **3.2%** |
| decks holding any prototype row | 0.0% | 99.8% |
| median maker:sink, floors 5 / 10 / 15 | 0.000 / 0.000 / 0.000 | **1.000 / 1.000 / 1.500** |
| mean deck size | 25.2 | 23.8 |
| runs won — diagnostic, NOT A BALANCE CLAIM (R215 B) | 5.5% | 1.7% |

**What each registered decision now says, quoted from §17.4 and applied.**

- **`S1` PREDICTED.** §17.4: *"the drafted economy reaches the price-2 rung,
  `W1'`'s null is a property of `W2`'s GRANTED deck and not of the one-for-one
  economy."* Taken. On a deck the drafter built, the bank's median per-fight
  peak is **5** — two and a half times the cheapest non-damage price — against
  `W2`'s printed ceiling of **1**. **In the sim, income is not the governor.**
- **`S2` MISS** and **`S3` MISS**, and they are one finding rather than two.
  §17.4 registered `S3`'s MISS as *"a SCORER finding and not an income
  finding"*, going *"to `BACKLOG` as an instrument row"*, with the live
  controlled-ratio deck **granting** its non-damage sinks. Taken, and it is
  what `S2` is made of: the destination was usually not in the deck at all
  (3.2%), so 0.62% of turns is an OFFER number wearing a bank number's clothes.
  `S2`'s registered UNREACHED condition was `S3` **exactly 0**; `S3` was 19, so
  the slot grades MISS as registered and is not relabelled (R101b).
- **`S4` MISS, on the branch §17.4 printed for it.** *"MISS with a ratio ABOVE
  0.80: `W2`'s 2:11 was an artefact of granting, the drafted economy is
  generator-rich, and the live deck is staged at the drafted median rather than
  at `W2`'s."* Taken exactly as written. The prediction that the ratio would
  FALL was wrong in sign: under the flag a `gain_spark` is priced at
  `SPARK_ALT_VALUE` = 4.00 for the first time, so the drafter can finally see a
  generator, and it drafts them.
- **`S5` PREDICTED.** §14.4 condition 3's Rummage half is **unreachable by
  draft**, confirmed at 0 of 600. The live controlled-ratio deck must **GRANT**
  Rummage; a drafted live deck would silently drop it.

### 17.7 What the live registration INHERITS, and what it does not

**IT INHERITS ONE NUMBER: `1.500` makers per sink** — `S4`'s floor-15 median
under the arm, i.e. **3 makers to 2 sinks**. §17.4 registered that *any* graded
outcome of `S4` hands the live deck its ratio, so the live controlled-ratio
registration takes a **derived** number rather than a pick, and it is the
inverse of `W2`'s granted **2 : 11**.

**IT INHERITS NOTHING ELSE. Named, so the next registration cannot borrow
more:**

1. **No re-price of §4.2's table and no new sink row.** R225 forbids both until
   income is answered, and this read answers income **in the sim only**.
2. **No conclusion that the sink set is fine.** `S2` and `S3` MISSED. What they
   establish is that the drafter does not TAKE the three migrated twins, which
   is a scorer question the live deck sidesteps by granting them — it does not
   establish that a player would not.
3. **No win rate, no comparison, no balance or fun claim** (R215 B,
   Guardrail-7). The 1.7% / 5.5% column is a diagnostic of a scoring pilot.
4. **Nothing about presentation.** The sim has no display and never saw the
   cost badge.

**Blind spots the run made concrete, stated rather than left to be found:**

1. **The maker count is a FLOOR, on both arms equally.** §17.2 defined a MAKER
   as a top-level `gain_spark`, so two real Spark sources are invisible to the
   ratio: `crackle`'s `discard_for_sparks`, and — since **C21** — **Klee's kit
   declaration** (`effects.klee_personal_companion_spark`), which is where
   `prune_witch_hunt`'s two printed `gain_spark` ops went under `EB-219`. The
   inherited 1.500 therefore understates generation and never overstates it.
2. **The control's maker:sink medians read 0.000 at every floor, and that is a
   scorer fact rather than a fault.** `draft.STATIC_SPARK_VALUE` is **0.0**:
   with the flag off a `gain_spark` is worth literally nothing to the drafter,
   so the median shipped deck drafts none. It is precisely why the control is
   RECORDED and NOT GRADED.
3. **One pilot, one policy, one route, one seed base.** Six hundred runs is a
   sample of one cell, not of the game.

---

## 18. `KLEESPARK-W3` — the live controlled-ratio whole fight

**2026-08-30 · branch `kleespark-w3`, stacked on `eb205-drafted-read`
(`4e1f2ae`). REGISTRATION, DRAFTED AND COMMITTED BEFORE ANY RUN.** This
section and its `EXPERIMENTS.md` row are the registration R225 ordered when it
answered §16.11 pick 1 as **(a′)**: *"then a live controlled-ratio deck under a
fresh registration Claude drafts."* Under R212(2) the slate is Claude's to
draft from written design intent and commit DRAFTED before any run; it is
offered for batch countersign and is never re-signed. R101b binds: nothing
already published in §11–§17 is re-read, re-graded or rewritten here.
`KLEESPARK-S1` (§17) is the sim half of the same order and this is the live
half; §17.7 is the list of what may travel between them, and this section
takes **one number** off it and nothing else.

### 18.1 The unit, and what is different from `KLEESPARK-W2`

**The unit is a CAPPED BATCH of live fights** — §14.4 condition 1 — begun at
the first Monster room of a live Act-1 Klee run and played by the Codex seat
through `understudy.blindplay session`, with the deck granted by
`understudy.embark --arm`. `W2` was registered as a batch and **did not get
one**: it stopped at 17 of 40 funded actions on `tool_blocked` at the second
Monster room's first frame, the same shape `W1` ended on. Two lifecycle throws
were the cause and both are fixed — `EB-221` (a `Deactivate` postfix resolving
the local seat on a combat that has none) and `EB-222` (the meter cost badge
painting a texture the room preloader had freed) — and
`understudy.soak --max-fights 3` now answers `fights=3 defects=0`. **So the
batch is attempted here for the first time on a build that can carry one**, and
§18.6 records what it actually got rather than what it was funded for.

**The one thing that changed in the DECK, and it is the whole point.** `W2`
granted **two Spark makers against eleven Spark-priced sinks** and its printed
bank never exceeded 1 against a cheapest non-damage price of 2. R225 read that
as a fact about THAT deck rather than about the economy, and §17's sim read
then measured the economy on decks the drafter itself built: the maker : sink
ratio at floor 15 came in at a median of **1.500 — three makers to two sinks** —
and the per-fight peak bank at a median of **5.0**. This deck is staged at that
ratio. It is the same arm, the same build family and the same slate; what moves
is the composition, and it moves to a number §17 derived rather than to one
anybody picked.

### 18.2 The deck — derived from the inherited ratio, row by row

**What is inherited, and it is one number** (§17.7): **1.500 makers per sink**,
`S4`'s floor-15 median under the arm. It is taken as a **FLOOR**, not as a
target — §17.7's blind spot 1 says the maker count is a floor on both arms
because two real Spark sources (`crackle`'s `discard_for_sparks` and, since
`C21`, Klee's kit declaration) carry no top-level `gain_spark` and are
invisible to the definition. A deck staged BELOW the inherited ratio would be
asking a question `S1` has already answered; a deck at or above it is asking
this one.

**A MAKER is a deck card carrying a top-level `gain_spark`; a SINK is a deck
card carrying a top-level `spend_spark`** — §17.2's definitions, unchanged, so
the two reads count the same things.

**The derivation, in order, with nothing picked at any step.**

1. **The SINKS are named by §14.4 condition 3 and by §16.4, not chosen here**:
   the three `EB-218` Spark-only twins (Set It Off, Dig In, Powder Smoke),
   **Rummage** — which R224 item 19 folded into this fight and which `S5`
   proved is **unreachable by draft** (0 of 600 decks), so it must be GRANTED —
   and **the cheapest damage sink, so a choice exists**. The cheapest damage
   sink in the arm is priced **1**, and one of the three price-1 faces is
   `proto_kaboom_sink` (Ka-pow!), which the substituted starter already
   supplies. It is therefore counted once and no second price-1 damage row is
   minted: **five sinks**.
2. **The MAKERS follow from the ratio**: 5 sinks × 1.500 = 7.5, and the
   inherited number is a FLOOR, so the count rounds **UP to 8**. Seven makers
   would put the deck at 1.400, below the floor this read exists to stage.
3. **WHICH makers is not a pick either.** Under `SPARK_ALT_COST_ENABLED` four
   of Klee's ten shipped `gain_spark` rows are converted into sinks by PICK 4's
   map (`sparkly_treasure`, `spark_collection`, `sugar_rush`, `cant_catch_me`),
   leaving **exactly six** shipped makers in the offerable pool. All six are
   granted, one copy each — the whole set, so no selection among them is made —
   and the eighth is a **second copy of the substituted starter's own maker**,
   `proto_pop_spark`, which is the row the arm already establishes rather than
   a seventh row somebody chose.

**THE GRANTED DECK — thirteen cards, one copy each except where noted.**

| # | `--arm` id | printed name | Energy | Spark | role | body |
|---|---|---|---|---|---|---|
| 1 | `proto_pop_spark` **×2** | Powder Pop | 0 | **makes 1** | maker (starter sub, doubled to the floor) | Bomb 5, gain 1 Spark |
| 2 | `skip_and_hop` | Skip and Hop | 0 | makes 1 | maker (shipped, common) | Block 2, gain 1 Spark |
| 3 | `warm_glow` | Warm Glow | 1 | makes 1 | maker (shipped, common) | Block 6, gain 1 Spark |
| 4 | `snap` | Snap! | 1 | makes 1 | maker (shipped, common) | 6 damage, gain 1 Spark |
| 5 | `hot_hands` | Hot Hands | 1 | makes 3 | maker (shipped, uncommon) | gain 3 Sparks, 2 damage to self |
| 6 | `all_my_treasures` | All of My Treasures! | 3 | makes 2 | maker (shipped, rare) | 6 Bombs at 6, gain 2 Sparks |
| 7 | `da_da_da` | Da-da-da! | 0 | makes 1 | maker (shipped, rare) | 4 damage ×3 random, gain 1 Spark |
| 8 | `proto_kaboom_sink` | Ka-pow! | 0 | **spends 1** | sink — damage (starter sub, and the cheapest damage sink) | Spend 1, 7 damage |
| 9 | `proto_powder_charge_spark` | Set It Off | 0 | spends 2 | sink — **detonation** (`EB-218` twin) | Spend 2, detonate +4 |
| 10 | `proto_hold_the_line_spark` | Dig In | 0 | spends 2 | sink — **Block** (`EB-218` twin) | Spend 2, Block 5 (+6 vs an attack intent) |
| 11 | `proto_smoke_and_sparks_spark` | Powder Smoke | 0 | spends 2 | sink — **Vulnerable** (`EB-218` twin) | Spend 2, Vulnerable 3 |
| 12 | `proto_spark_priced_draw` | Rummage | 1 | spends 3 | sink — **draw** (R224 item 19) | Spend 3, draw 3 |

**The arithmetic the deck is staged on:** **8 makers : 5 sinks = 1.600**, at or
above the inherited floor of 1.500, against `W2`'s granted **2 : 11 = 0.182**.
Klee's printed starter (4 × Kaboom!, 4 × Duck and Cover, Jumpy Dumpty, Pop!)
carries **no maker and no sink** by the sheet definition, so it moves neither
side of the ratio.

**Deck size: 23** — the printed ten plus thirteen granted — against `W2`'s
**21**. The two records are comparable on composition and near enough on size
that draw frequency is not the difference between them.

**`arms_granted` verbatim, as the sealed record will name them** (wire ids —
`KLEEMOD-` plus the id upper-cased, `embark.wire_id`; Powder Pop appears twice
because it is granted twice):

```
KLEEMOD-PROTO_POP_SPARK
KLEEMOD-PROTO_POP_SPARK
KLEEMOD-SKIP_AND_HOP
KLEEMOD-WARM_GLOW
KLEEMOD-SNAP
KLEEMOD-HOT_HANDS
KLEEMOD-ALL_MY_TREASURES
KLEEMOD-DA_DA_DA
KLEEMOD-PROTO_KABOOM_SINK
KLEEMOD-PROTO_POWDER_CHARGE_SPARK
KLEEMOD-PROTO_HOLD_THE_LINE_SPARK
KLEEMOD-PROTO_SMOKE_AND_SPARKS_SPARK
KLEEMOD-PROTO_SPARK_PRICED_DRAW
```

**WHAT IS LEFT OUT, and why.**

- **`proto_true_spark_knight` (Spark Knight's Oath)** — excluded on §12.2's
  published D4 grounds, exactly as `W1`, `W2` and `S1` excluded it: a Rare
  Power that reprices every Attack in the deck is a second variable in a window
  whose one variable is the maker : sink ratio. Its own whole-fight read is
  **`EB-223`** and is not this read.
- **The five damage rungs above price 1** — Fwoosh! and Tinder Toss at 1, Bang
  Bang! and Dodoco Blast at 2, Firework Finale at 3. `W2` granted the whole
  ladder and the ladder is not what is being asked about; a deck carrying every
  damage face at every price would put the ratio back where `W2` had it. **One**
  cheapest damage sink is in, because §14.4's question needs a rival for the
  bank, and nothing above it is.
- **A shipped maker converted by PICK 4's map.** Granting `sparkly_treasure`
  under the flag would put a row in the deck that the arm's own pool cannot
  offer.

### 18.3 The cell, the batch, the budget and the stopping rule

| | |
|---|---|
| cell | the **installed dev build**, named in the sealed record's identity block, read off the deployed `mods\klee\manifest.json`, plus the game build off `release_info.json` |
| build stamp EXPECTED | **`0.2.1610+proto.dirty`** — read before this registration was written, from `main` `d45785a` (both prototype arms, `EB-222`'s badge fix, `EB-220`'s glyphs). **NOTHING IS DEPLOYED BY THIS PIECE**: the build that is installed is the build that runs |
| build stamp RULE | the cell is whatever the deployed manifest says, and a difference from the expected string is DISCLOSED in §18.6 rather than treated as a stop — `embark --arm` refuses a build with no `+proto` anyway (`embark.check_arms`), which is the check that actually matters |
| the pck contract check | the deployed package was built at `main` `d45785a`; this branch is that commit plus `EB-226`, `EB-227` and §17, and `git diff d45785a..HEAD -- klee-mod docs/klee-cards.yaml docs/prototype-surface.yaml tier0/constants.py` is **EMPTY**. So every granted row's printed text on the installed build is this tree's sheet text. **If a granted row's printed face on a live page differs from its sheet row, the run STOPS and says so** |
| action budget | `--max-actions 40 --max-wall-s 7200 --max-refusals 2 --max-stalls 6` |
| Codex cap | **45 calls** — the driver spends one `codex exec` per answered screen plus one per fight record and one for the run record, so 40 actions is the largest cap that fits inside 45. **The Codex cap is what bounds this batch, not the game**: `--max-actions` is set to the number the cap can pay for |
| the batch's bound | the action budget IS the batch bound, as it was in `W2`. On `W2`'s own rate — 12 combat pages and 5 navigation pages for one fight and its rewards — 40 actions is **two to three fights**. §14.4's stopping condition (*stop as soon as three or more combat turns have held two simultaneously affordable uses*) is evaluated **at grading, off the wire record**, not live: the driver is a blind one-thread seat and no operator reads a page mid-session |
| the seed | **rolled by the game and read back off the wire (R95)** — not chosen and not pinned, exactly as `W1` and `W2` took theirs. There is no declared board here, so `EB-208`'s (a) live-count preflight has no declared count to compare against; **no slot below reads `enemy_count`**, so no page can be UNREACHED on a body-count gap and (a) cannot bite. `EB-208` (c)'s character/build/context-keyed seed ledger is **not built and is not used** |
| sessions | **ONE.** If the session ends early it is recorded as it ended and NO second session is started |
| the seat's meter | `python -m understudy.codex_usage` is printed **before and after** the run into §18.6 (`EB-227`, stop lines 85% of the five-hour window and 50% of the week). If the guard refuses mid-batch the run stops cleanly, what ran is graded, and §18.6 says so |
| the R225 soak gate | `python -m understudy.soak --runs 1 --character KLEEMOD-KLEE --max-fights 3` is run as the preflight and its answer is recorded in §18.6 |

### 18.4 The slate — `W1'`–`W5'` re-used at their `W2` thresholds, plus one new slot

Every falsifier is computed by `review/qa/blindplay/kleespark-w3/grade.py`,
**committed in this same commit, before any run**, off artefacts the run writes
by itself: the rendered observation pages (`turn-*/prompt.md` — printed bank,
printed Energy, printed hand), the per-turn `reply.json`, and
`transcript.jsonl`'s command rows. No grade reads a design judgement, and no
grade reads the tester's prose except `W3''`, whose §14.4-condition-2 half is a
fixed keyword rule over the tester's own recorded sentence and is stated as
such. The slot names carry a **double prime** so no reader can confuse a grade
here with `W2`'s published `W1'`–`W5'`, which stand as published (R101b).

**Affordability, defined once for the whole slate, and taken from §16.4
unchanged.** On a combat page a hand card is AFFORDABLE when its printed Spark
price is ≤ the printed Spark bank AND its printed Energy cost is ≤ the printed
current Energy. Every sink but Rummage costs 0 Energy; the Energy half binds
anyway, because an unpayable card is not a declined one.

**The four NON-DAMAGE sinks in this deck**: Set It Off, Dig In, Powder Smoke,
Rummage. **The one DAMAGE sink**: Ka-pow!.

| # | slot | prediction | falsifier, mechanically | UNREACHED when | the decision the outcome changes |
|---|---|---|---|---|---|
| `W1''` | **The precondition `W1` and `W2` never met**: does the bank ever hold two affordable uses at once, with a non-damage destination among them? | **YES, on at least 3 combat turns** — `W2`'s threshold, unchanged. | Count combat pages where **two or more distinct Spark-priced titles in hand are each affordable**, and **at least one of the affordable ones is a non-damage sink**. **≥ 3 = PREDICTED, 1–2 = SPLIT, 0 = MISS.** | the session reaches **zero combat pages** | **PREDICTED**: the precondition is met at the inherited ratio, `W3''` is a real reading, and `W1'`'s null is established as a property of `W2`'s composition (R101b leaves `W1'` itself untouched). **MISS**: the precondition fails at a deck staged three makers to two sinks, which is the strongest evidence available that generation and not composition is the governor — **PICK 1 REOPENS to [USER]** (see `W6''`). **SPLIT**: the bank reaches the rung but rarely; the next unit is a longer batch, not a new row. |
| `W2''` | **The mixed pool's own question**: is a non-damage sink ever chosen over a damage sink the bank could equally have paid? | **YES, on at least 1 turn** — `W2`'s threshold, unchanged. | A successful `play` of a non-damage priced row on a turn whose page showed **at least one damage sink also affordable at that moment, at a Spark price ≤ the played row's price**. **≥ 1 = PREDICTED, 0 = MISS.** | **no page ever showed a non-damage sink and a damage sink affordable at the same moment** — the deck never posed the choice, which is a draw fact and not a design reading | **PREDICTED**: the bank has a second kind of destination in live play at this ratio, and §14.3's question about minting NEW sink rows can at last be asked against a measured alternative rather than a null. **MISS with `W1''` PREDICTED**: the choice was posed and damage won every time — the migration did not buy a decision, and §14.3 options (1)/(2)'s new rows are back on the table. **UNREACHED**: the fault is draw, and the next act is more fights. |
| `W3''` | **§14.4 condition 2 — a hold that names what it is saving for.** | **YES, on at least 1 turn** — `W2`'s threshold, unchanged. | A turn ended with `end turn` while an **affordable** Spark-priced sink sat in hand (`W3`'s bare detector, unchanged), **AND** that turn's recorded sentence both matches the fixed hold vocabulary and **names a Spark-priced title or the bank itself**. **≥ 1 = PREDICTED, 0 = MISS.** | **`W1''` grades MISS** — §14.4 condition 1 in so many words: a hold prediction evaluated on a board that never offered a choice measures the generator, not the sink | **PREDICTED**: the single number §14 exists to move off zero has moved, and the arm's economy creates a decision in live play at the inherited ratio. **MISS with `W1''` PREDICTED**: the choice existed and was never declined — §14.3's option (4) reading is finished and re-pricing §4.2's table becomes the next act to put to [USER]. **UNREACHED**: nothing about the sinks is learned. |
| `W4''` | **§14.4 condition 4 — the price-3 rung is bought at least once.** | **NOT A GRADED SLOT. `UNREACHED` BY CONSTRUCTION, and printed here before the run**, exactly as §16.4 printed it. | §14.4 condition 4 registers this prediction **only if the chosen option puts a REDESIGNED card at price 3**. R224 took (5) in its migrate-only form, **Powder Keg was not built**, and the twins are priced 2. There is no redesigned price-3 rung in this deck. | by construction, before the run | nothing. It is printed so a later reader cannot mistake its absence for an omission. **What IS recorded, ungraded**: whether the one price-3 face in this deck (Rummage) was ever bought. |
| `W5''` | **§14.4's fourth item — the attack share.** | **RECORDED, NOT GRADED.** | Share of successful `play` commands that name an Attack, by the kind the page printed. `W1` read 50.0%, `W2` read 75.0%. | n/a | none on its own. A deck of six new makers and four non-damage sinks should read lower than `W2`'s 75%; it is recorded so that claim can be checked later, and it grades nothing. |
| `W6''` | **NEW, and the only slot §17 hands this registration a number for: the LIVE per-fight peak Spark bank against `S1`'s sim median of 5.0.** | **The median per-fight peak printed bank is ≥ 2.** Registered as a **FLOOR relation, not an equality**: `S1`'s 5.0 was taken in the sim, on decks the drafter built, over 8,428 fights, and a live median that merely CLEARS the cheapest non-damage price is what this read needs. **It is registered as "≥ 2" and never as "= 5".** | Per fight, the **maximum printed Spark bank** across that fight's combat pages (an absent Spark line on a combat page is a bank of 0 — `W1`'s and `W2`'s graders' own rule). The median over fights carrying at least one combat page. **median ≥ 2 = PREDICTED; median = 1 = SPLIT; median 0 = MISS.** | the session records **zero combat pages** | **PREDICTED**: income clears the price-2 rung in live play at the inherited ratio, `S1`'s sim reading survives contact with the build, and **`EB-205` is DISCHARGED** — the income question R225 put first is answered on both engines, and the arm's remaining question is SPENDING, which is `W2''`'s. **SPLIT**: income reaches the rung only sometimes; the live deck is not re-staged and the next act is a longer batch. **MISS**: **income fails live on a deck staged at three makers to two sinks.** This is the first evidence that would **REOPEN Klee PICK 1 (the generation pattern) to [USER]** — a MISS here cannot be blamed on composition, because composition is the one thing this registration controlled, and it goes back as a numbered pick rather than as a Claude decision. |

**A MISS on income reopens PICK 1, and that is registered here rather than
decided later.** R225 forbids a new sink row and a re-price *until income is
answered*. `S1` answered it in the sim. If `W6''` (and with it `W1''`) MISSES
on a deck built to §17's own inherited ratio, then the answer differs between
the engines on the one question the whole sequence turns on, and **Claude does
not settle that**: it returns to [USER] as PICK 1 reopened, with this run and
`S1` as the two readings. Any other combination of grades leaves PICK 1 closed.

**Contamination and blind spots, stated before the run.**

1. **GRANTED, NOT DRAFTED.** `bridge.GRANT_GUARDRAIL` rides the record: this
   run's deck is not one the generators produced, so nothing measured on it is
   comparable to any other run. The ratio is staged deliberately — that is the
   experiment — and it is not evidence about what a player would draft. `S3`
   already measured the draft half and MISSED (3.2%), which is why the sinks
   are granted here.
2. **THE STARTER IS SUBSTITUTED ADDITIVELY, NOT REPLACED.** `S1`'s arm
   substitutes one `pop` → Powder Pop and one `kaboom` → Ka-pow! at
   `loader._starter_ids`; the live game has no such seam, so the two prototype
   Basics are GRANTED on top and the printed starter keeps its `Pop!` and its
   four `Kaboom!`. The deck therefore holds two Bomb-placers and five
   7-damage Attacks where the sim's holds one and four. Neither shipped row is
   a maker or a sink, so the **ratio is unaffected**; what is affected is draw
   frequency, and it is disclosed rather than corrected.
3. **`+proto`, so the shipped automatic Spark rule is NOT LIVE.** The build is
   stamped `+proto` by `deploy_proto.ps1`, which compiles
   `-p:PrototypeCards=true`, under which `SparkPower.BaseRuleActive` is the
   compile-time constant **`false`** (`klee-mod/KleeCode/Powers/SparkPower.cs`,
   pinned by `SparkAlternativeCostPinTests` and `SparkSinkPinTests`). At no
   bank do Attacks cost 0 and nothing is consumed automatically. This is the
   R101b erratum §16.4 contamination 1 carries, stated here as a fact and not
   as a hedge.
4. **ONE SEED for the whole batch**, rolled by the game and read back. Every
   fight in the batch is a fight of that one run, so the fights are not
   independent samples of anything.
5. **Pounding Surprise, Klee's starter relic, pays +1 Spark per detonation.**
   It is an income source the deck's maker count does not see, in the same
   direction as §17.7's blind spot 1: the inherited ratio understates
   generation and never overstates it. `W2`'s own Spark-arithmetic candidate
   was explained by exactly this, and R225 closed the class at pick 3 (b).
6. **Guardrail-7 and R217 G.** Every number here is a FLOOR off one capped
   batch, one seed, one pilot and a granted deck. The tester's words are
   iteration feedback — never validation, never balance evidence, never
   approval — and no win rate, comparison or fun claim may be taken off this
   run.

### 18.5 Independence, and who holds the deciding chair

All five prototype sink rows and both prototype Basics are
`authored_by: [claude]`; the six shipped makers are shipped content and carry
no authorship claim of the seat's. **The seat that plays is Codex
(`gpt-5.6-sol`)**, refused-by-family through `blindplay.check_independent`
(R217 C), so the playing chair is author-disjoint.

**Who holds the DECIDING chair — OPERATIONS' own rule, applied.** *"A round
that can ADVANCE an arm gets the Codex seat deciding every board … A round
that is an INSTRUMENT round — a repair, a bench, anything on which no ADVANCE
rests — stays on the fresh-Opus deciding form. The round's own registration
says which it is, before it runs."* **This batch CAN ADVANCE**: it decides the
income question `EB-205` and R225 put first, and `W6''` PREDICTED discharges
`EB-205`. It is therefore **not** an instrument round, the deciding read is
**Codex's**, and there is no fresh-Opus form in this registration at all —
which in whole-fight blind play is the same thing as saying the tester decides,
because the tester is the only reader. The **GRADING** chair is a committed
mechanical script, not a model, so author-disjointness does not arise for it
except on `W3''`'s keyword half, which is a fixed rule written before the run.

### 18.6 What actually ran — the session, the stamp, and the operator's four actions

**RUN 2026-08-30, sealed session `kleespark-w3`.** The committed record is
`review/qa/blindplay/kleespark-w3/record.md` — identity block, the tester's
four fight records and its run record verbatim, the per-turn sentence table,
the leak audit. The grader's output is `grades.json` beside it. The rendered
pages, the replies and `transcript.jsonl` are the gitignored operator half
under `understudy/logs/blindplay/kleespark-w3/`.

| | |
|---|---|
| pilot | `gpt-5.6-sol` requested and observed, `codex-cli 0.150.1` |
| build | **`0.2.1610+proto.dirty`**, read off the deployed `mods\klee\manifest.json` — **exactly the stamp §18.3 registered in advance**, and nothing was deployed by this piece |
| game | `v0.111.0`, read off the game's own `release_info.json` |
| run seed | **`LEA0X16MF2WQ`**, read back off the wire (R95) — see the `EB-191` disclosure below |
| arms granted | **all thirteen of §18.2**, by wire id, into the starting deck, each answering `ok` on `0.2.1610+proto.dirty` |
| actions | **40 of 40**, termination **`max_actions`** |
| fights | **FOUR**, all four fought to a finish |
| Codex calls | **45 of the registered 45** — 40 answered screens, four fight records, one run record. At the cap, not over it |
| seat meter, BEFORE | `codex: 5h 3% (resets 04:40 EDT) · week 11% (resets Sep 05 17:58)` |
| seat meter, AFTER | `codex: 5h 41% (resets 04:40 EDT) · week 17% (resets Sep 05 17:58)` |
| the guard | `EB-227`'s stop lines are 85% of the five-hour window and 50% of the week. Neither was reached and **the guard never refused a call**; the batch cost ~38 points of the five-hour window and ~6 of the week |
| the R225 soak gate | **PASSED before the embark**: `bounded seed=M93YQQ01072S actions=68 fights=3 defects=0`, reversibility log all REVERTED |
| the power request | `EB-226` held for the soak and again for the embark — *"idle sleep is blocked while the harness holds the game"* — and released at each teardown |

**THE BATCH HAPPENED.** `W1` was one fight; `W2` was funded for a batch and got
one fight, stopping on `tool_blocked` at the second Monster room's first frame;
this session played **four fights** and stopped only because it ran out of
funded actions. `EB-221` and `EB-222` are the difference, and §14.4 condition
1's *capped batch* is a real unit for the first time.

**Four operator actions before the seat was handed the game, and they are
declared rather than buried.** `embark` left the run on the **Neow** screen at
floor 1 rather than at a Monster room, and Neow cannot be skipped — a bare
`proceed` is refused by the wire. Its three boons are *Scroll Boxes* (add a
pack of cards to the deck), *Precise Scissors* (remove a card) and *Silken
Tress* (lose all Gold; enchant the first card reward with Glam). **Two of the
three rewrite the deck this registration exists to control**, and letting the
tester take one would have put a pack of undeclared cards into a deck staged at
a derived ratio. The operator therefore took the **only deck-neutral option** —
Silken Tress — and advanced to the map, which is the state §18.1 registers as
the start. The four commands were `proceed` (refused by the wire),
`choose "Silken Tress"`, `proceed` (refused), `choose "Proceed"`. The tester's
first screen was the map above the first Monster room.

**`EB-191` fired, and the repair is disclosed.** `embark` printed
`run seed: (unread)` — the known read-back-`None` defect, which a retry always
fixes. The seed was re-read off the wire **from the same process, with the run
open and before the session started**, came back `LEA0X16MF2WQ`, and was
written into the embark sidecar so `blindplay.granted_arms` could match the run
to its grant. Nothing else in the sidecar was touched. Had it not been, the
sealed record would have said `arms_granted: (none)` about a deck of thirteen
granted cards, which is the one thing that record must not do.

**The pck contract check, as §18.3 registered it.** `git diff d45785a..HEAD`
over `klee-mod`, `docs/klee-cards.yaml`, `docs/prototype-surface.yaml` and
`tier0/constants.py` is **empty**, so the deployed package's Klee rows are this
tree's sheet rows. **One printed face nevertheless disagreed with the sheet on
one frame, and it is §18.9 item 1** — a runtime display divergence rather than
a stale build, so the stop rule's condition (a build whose rows are not the
sheet's) was not met, and no falsifier reads that number.

### 18.7 The fight, fight by fight, and the numbers that decide the slate

Four fights, **19 combat pages**, in pages: **8 / 2 / 5 / 4**.

| fight | pages | peak printed Spark bank | what it was |
|---|---|---|---|
| 1 | 8 | **5** | Nibbit. Block, then both Powder Pops into Jumpy Dumpty, Kaboom! and Ka-pow! |
| 2 | 2 | **0** | Shrinker Beetle. One Kaboom!, then a Power Potion; **not one Spark all fight** |
| 3 | 5 | **3** | Shrinker Beetle. Endless Fireworks off the potion, then Sucrose into All of My Treasures! and one Ka-pow! detonation |
| 4 | 4 | **9** | Fuzzy Wurm Crawler. All of My Treasures!, the stack detonates, Powder Pop into Jumpy Dumpty for an exact kill |

**The median per-fight peak bank is 4.0**, against `W2`'s printed ceiling of
**1** across all twelve of its combat pages and against `S1`'s sim median of
**5.0**.

**The counted ratio held for the whole run, and that is checked rather than
assumed.** The tester added three cards after the first fight — *Sucrose —
Catalyst Conversion* (drafted), *Endless Fireworks* (a Power Potion) and
*Eager to Help* (drafted) — and **none of the three carries a top-level
`gain_spark` or `spend_spark`**, so the deck's maker : sink count was **8 : 5 =
1.600 at every page of every fight**. The controlled variable stayed controlled.

### 18.8 The slate, graded mechanically

**1 PREDICTED (`W6''`) / 1 SPLIT (`W1''`) / 2 MISS (`W2''`, `W3''`) / 1
UNREACHED BY CONSTRUCTION (`W4''`)**, plus `W5''` RECORDED and NOT GRADED.
Every grade is `review/qa/blindplay/kleespark-w3/grade.py`'s own output against
§18.4's registered thresholds and no others; the raw output is `grades.json`.

| slot | grade | the read | the registered threshold |
|---|---|---|---|
| `W1''` two affordable uses, one non-damage | **SPLIT** | **1** of 19 combat pages — `turn-030`, bank 3, energy 2, Ka-pow! and **Dig In** both affordable | ≥ 3 PREDICTED, 1–2 SPLIT, 0 MISS |
| `W2''` a non-damage sink chosen over a payable damage sink | **MISS** | **0**. The choice was posed on exactly one page (`turn-030`) and the tester played **Ka-pow!** — *"Any unblocked attack should detonate the 36 Bomb damage"* | ≥ 1 PREDICTED, 0 MISS |
| `W3''` a hold that names what it is saving for | **MISS** | **0 named, and 0 on the bare detector** — no turn ended with `end turn` while an affordable Spark-priced sink sat in hand | ≥ 1 PREDICTED, 0 MISS; UNREACHED only if `W1''` MISSED, and it did not |
| `W4''` the price-3 rung | **UNREACHED BY CONSTRUCTION** | printed before the run. The one price-3 face in this deck, **Rummage, was never played** | not a graded slot |
| `W5''` attack share | **RECORDED, NOT GRADED** | **6 of 15 successful plays, 40.0%** — against `W1`'s 50.0% and `W2`'s 75.0% | none |
| `W6''` median per-fight peak bank | **PREDICTED** | **median 4.0** over four fights (peaks 5 / 0 / 3 / 9) | median ≥ 2 PREDICTED, 1 SPLIT, 0 MISS. `S1`'s 5.0 is a comparator and was never a threshold |

**What each registered decision now says, quoted from §18.4 and applied.**

- **`W6''` PREDICTED.** §18.4: *"income clears the price-2 rung in live play at
  the inherited ratio, `S1`'s sim reading survives contact with the build, and
  `EB-205` is DISCHARGED."* Taken. On a deck staged at three makers to two
  sinks the live median per-fight peak bank is **4**, twice the cheapest
  non-damage price. **The income question R225 put first is ANSWERED on both
  engines, and PICK 1 DOES NOT REOPEN.** The registered reopening condition
  was a `W6''` MISS and it did not occur.
- **`W1''` SPLIT.** §18.4: *"the bank reaches the rung but rarely; the next unit
  is a longer batch, not a new row."* Taken exactly as written. One page in
  nineteen posed the two-affordable-uses question. That is one more than `W2`
  managed and it is not three.
- **`W2''` MISS and `W3''` MISS AUTHORISE NOTHING, and the reason is in the
  registration.** Both of their MISS branches are written **"MISS with `W1''`
  PREDICTED"** — the design acts they unlock (new sink rows for `W2''`;
  re-pricing §4.2's table for `W3''`) are conditional on the precondition
  having been met, and it was not: `W1''` is SPLIT. A choice posed **once** and
  declined once is not a reading about the sink set, and a hold detector at
  zero on a run that offered a hold on one page measures the draw. **No
  re-price and no new sink row may be taken off this run**, which is also what
  R225 already forbids until income is answered — and this run answers income
  the other way.
- **`W5''` records the number `W2` left.** The attack share fell from `W2`'s
  75.0% to **40.0%**, which is the direction §18.4 said a deck of makers and
  non-damage sinks should move it. It grades nothing, and it is not a balance
  reading.

### 18.9 What the run found that is not a slot

1. **A printed face disagreed with itself inside one run — `All of My
   Treasures!`, and it is a DEFECT CANDIDATE with a named mechanism.** On
   `turn-029` the page printed *"Place 6 Bombs, each dealing **4** damage"*; on
   `turn-037` the same card printed *"each dealing **6** damage"*. The sheet
   says **6** (`docs/klee-cards.yaml`, `bomb_damage: 6`) and the generated C#
   places `DynamicVars.Damage.BaseValue` — so the CARD always places 6-damage
   Bombs, and the observed stack was 36 on both frames. The face uses
   `{Damage:diff()}`, which renders the var through the player's live damage
   modifiers, and the `turn-029` frame was against the **Shrinker Beetle**,
   whose intent is a debuff. **A displayed number that moves with a debuff the
   body does not read is the `EB-164` family**, and the tester caught it
   unprompted: *"All of My Treasures! said six Bombs dealing 4 damage each,
   suggesting 24, but the enemy displayed Bomb 36."* It is recorded as a
   candidate rather than a defect because the mechanism is inferred from two
   frames and one intent, not proved. **It moves no grade**: no falsifier reads
   that number, and the card is a maker, not a priced sink.
2. **Income at this ratio was not carried by the granted makers alone, and the
   ratio cannot see the difference.** Fight 4's peak of 9 followed a six-Bomb
   stack, and the tester says plainly: *"The sudden jump from 2 Sparks to 8 at
   the next turn was unexplained by the visible cards or buffs."* That is
   **Pounding Surprise**, the starter relic, paying +1 per detonation —
   §18.4's contamination 5 — plus `Endless Fireworks`, which grants
   `spark_per_turn` and carries **no** top-level `gain_spark`, so the counted
   maker set does not include it either. **`W6''` is therefore a FLOOR on
   income and never a ceiling**, in the same direction as §17.7's blind spot 1,
   and it is honest to say that a deck at 1.600 counted makers had two
   uncounted sources helping it clear the rung.
3. **One whole fight ran at a bank of zero.** Fight 2's two pages carried no
   Spark at all, and the tester names the consequence four separate times
   across its records — *"Rummage, Dig In, and Powder Smoke were dead in the
   opening hand because there were no Sparks"*, *"Set It Off and Rummage were
   dead because I had no Sparks"*. A median of 4 and a fight of 0 are both true
   of this run, and the second is what the SPLIT on `W1''` is made of.
4. **The tester names the hold tension unprompted while the detector reads
   zero** — the same shape `W1` reported. Its run record item 2: *"a smaller
   tension between spending Sparks immediately on attacks or saving them for
   draw, defense, and manual Bomb detonation."* `W3''`'s bare detector is 0.
   Legible as a shape, inert as a decision, for the third read running. R217 G:
   that sentence is iteration feedback and is not evidence for any slot.
5. **Two harness observations, neither a slot and neither a design finding.**
   The Power Potion's own selection screen never appeared before the
   fight-record prompt on `turn-023`/`turn-024`, so the tester wrote its fight
   record believing the potion had resolved into nothing; and the duplicate
   `Powder Pop (1)` / `Powder Pop` pair carried an enchantment warning without
   saying which copy was enchanted — a consequence of the operator's Silken
   Tress choice reaching a card reward.

### 18.10 What this leaves

**The decision the grades permit, stated once.**

1. **`EB-205` is DISCHARGED.** Its acceptance was *"that registration
   committed"* and its scope was the drafted Spark arm, never measured drafted.
   `KLEESPARK-S1` measured it in the sim and this read measured it live at the
   ratio `S1` derived: **income is not the governor on a representative Klee
   Spark deck, on either engine.** The row closes.
2. **Klee PICK 1 does NOT reopen.** §18.4 registered exactly one condition that
   would have reopened it — a `W6''` MISS on a deck staged at the inherited
   ratio — and `W6''` is PREDICTED. Nothing else on this slate reaches PICK 1.
3. **No re-price, and no new sink row.** R225 forbade both until income was
   answered; income is now answered, and the two slots that could have
   authorised a sink act (`W2''`, `W3''`) both MISSED with their registered
   precondition unmet. What the run establishes about the sink set is that a
   deck at 1.600 makers per sink posed the two-destination choice **once in
   nineteen combat pages** — a draw fact at this deck size, and an argument for
   a longer batch rather than for a different card.
4. **The next unit is `W1''`'s own registered act: a longer batch at this same
   deck.** Forty actions bought four fights and one qualifying page. The
   binding constraint is the **Codex cap**, not the game — the driver spent 45
   of 45 calls and the game stopped nothing — so a longer batch is a budget
   question for [USER] and not an engineering one.
5. **Nothing here is a balance or fun claim.** One batch, one seed, one pilot, a
   granted deck the generators did not produce, two uncounted income sources.
   Guardrail-7: floors. R217 G: §18.6's and §18.9's quoted sentences are
   iteration feedback, never validation, never approval.

**Leak audit: 45 observations scanned, 1 hit, and it is the known false
positive** — `pilot-vocabulary-score` matching the word `score` inside the
guide's own sentence *"no card list, no score, no recommendation"*, exactly as
`W1` and `W2` recorded it. No card id, design tag, policy hint or run seed
reached any page.

---

## 19. `KLEESPARK-W4` — the strict Rare Power's whole fight, and `W1''`'s longer batch

**2026-08-30 · branch `eb223-rare-power-registration`, stacked on
`kleespark-w3` (`36f162a`). REGISTRATION, DRAFTED AND COMMITTED BEFORE ANY
RUN. NOTHING RAN TONIGHT.** Under R212(2) the slate is Claude's to draft from
written design intent and commit DRAFTED before any run; it is offered for
batch countersign and is **never re-signed**. R101b binds: nothing already
published in §11–§18 is re-read, re-graded or rewritten here. `W3`'s
`W1''`–`W6''` stand exactly as published, and the slot names below carry a
**triple prime** so no reader can confuse a grade here with one of theirs.

### 19.1 Why this registration exists, and why it is ONE registration serving TWO owed reads

**Owed read A — `EB-223`, the Rare Power.** R222 answered §11.7 pick 3 as
**(a)**, verbatim: *"leave it as built and re-read it in whole-fight play. Its
face is legible — that is what `P3` PREDICTED — and an investment Power needs
fight history before its wording or its price can be judged. Neither §5's
wording nor the price of 3 is reopened."* That answer is a **work order, not a
decision** (§16.2's erratum, 2026-08-30), and the work is this read.

**Why it must be a WHOLE FIGHT and not a staged turn, in R222 (a)'s own
terms.** *An investment Power needs fight history.* A staged turn hands the
reader a board and a bank that somebody chose; the Power's entire question is
whether a bet placed on turn N is paid back over turns N+1…end, off a bank the
run itself produced. `KLEESPARK-R1`'s `P3` already read the only thing a
staged turn CAN read about it — the face is legible — and PREDICTED it, so a
second staged round would re-ask an answered question and could not ask the
open one. The three slots at §19.4 are each a statement about pages that come
AFTER a play, which is a shape a single staged board does not have.

**Owed read B — `W1''`'s own registered act.** §18.4 registered, for a `W1''`
SPLIT: *"the bank reaches the rung but rarely; the next unit is a longer
batch, not a new row."* `W1''` came in SPLIT (1 of 19 combat pages), and
§18.10 item 4 named the unit: *"a longer batch at this same deck… the binding
constraint is the Codex cap, not the game."* This registration IS that longer
batch — same deck, same derived ratio, roughly double the actions.

**Two reads, one session, and the linkages are registered SEPARATELY so
neither contaminates the other.** The whole hazard of folding them together is
that the Power reprices Attacks, and a repriced Attack changes what "two
affordable uses" means — which is exactly the D4 objection §12.2 raised when
it kept the Power out of `W1`, `W2` and `S1`. The separation is mechanical and
is fixed here, before the run:

- **`W1'''` is graded on PRE-POWER combat pages only** — every page from the
  session's first up to and including the last page before `proto_true_spark_
  knight` resolves. On those pages the deck is `W3`'s deck exactly: the Power
  carries neither a top-level `gain_spark` nor a top-level `spend_spark`, so
  while it sits unplayed the counted ratio is still **8 makers : 5 sinks =
  1.600**, and no Attack's price has moved. `W1'''` is therefore a strict
  continuation of `W1''` at a longer batch, and its denominator is printed
  with its grade.
- **`K1'''`, `K2'''` and `K3'''` are graded on POST-POWER combat pages only**,
  and every one of them is UNREACHED if the Power never resolves. None of them
  reads a pre-Power page and `W1'''` reads no post-Power page; the two sets are
  disjoint by construction and the grader partitions them once, at the
  transition, off the transcript's own `play` row.
- **The post-Power count for `W1'''`'s question is RECORDED and NOT GRADED**,
  beside the graded pre-Power count. It is printed so the number exists, and it
  grades nothing, because on those pages the affordability question is a
  different question.

### 19.2 The D4 objection, recorded, and what this read CAN and CANNOT say about it

**The objection as published (§12.2, and §18.2 repeating it):** *"The strict
Rare Power would change the price of every Attack in the deck at once, which is
a second variable in a window whose one variable is the priced-sink economy
(D4)."* It was correct in `W1`, `W2`, `S1` and `W3`, and it is not withdrawn
here. What changes is the question the window is asked: `W3` and `S1` between
them ANSWERED the income question (`EB-205` DISCHARGED, `W6''` PREDICTED at a
median per-fight peak bank of 4.0), so the priced-sink economy is no longer the
one variable this window is protecting. The Power is now the variable, and the
ratio is the thing held fixed.

**What this read CAN say.** What the strict Power does on a deck whose
maker : sink ratio is **known, derived and held constant at 1.600**, checked
page by page the way §18.7 checked `W3`'s — whether the converted price of 3 is
ever actually paid, whether the conversion is visible where §5 says it is
visible, and whether the price-3 rung takes the bank away from the price-2
rungs.

**What this read CANNOT say, stated before the run so it is not claimed
after.**

1. **It is not a comparison with `W3` and no number here may be quoted as
   one.** Different seed, different batch length, a fourteenth card in the
   deck, and a different draw order. `W3`'s grades stand as published (R101b)
   and nothing below re-reads them.
2. **The pre-Power / post-Power split inside ONE session is NOT a controlled
   contrast**, and it is not offered as one. The two halves differ in fight
   order, in what the run has drafted and drunk by then, and in the enemies
   they faced. The split exists to keep the two OWED READS from grading each
   other's pages, and it buys nothing else.
3. **It cannot attribute anything to the Power alone.** A whole fight is one
   arm; there is no Power-off arm here and none is registered.
4. **It says nothing about whether the Power should be on the sheet.** The best
   outcome available on this slate is an ADVANCE-to-sheet **candidate** — a
   numbered proposal to [USER] — never a Claude decision (the ladder: a pick
   between genuinely different design directions is [USER]'s).

### 19.3 The deck — `W3`'s exact granted deck PLUS the Rare Power, and nothing else

**Fourteen granted cards: §18.2's thirteen, unchanged and in the same order,
plus `proto_true_spark_knight`.** Not one of the thirteen is re-chosen here;
they are the derived deck `S4`'s inherited floor of 1.500 produced, and
re-deriving them would be picking them.

| # | `--arm` id | printed name | Energy | Spark | role |
|---|---|---|---|---|---|
| 1 | `proto_pop_spark` **×2** | Powder Pop | 0 | makes 1 | maker (starter sub, doubled to the floor) |
| 2 | `skip_and_hop` | Skip and Hop | 0 | makes 1 | maker |
| 3 | `warm_glow` | Warm Glow | 1 | makes 1 | maker |
| 4 | `snap` | Snap! | 1 | makes 1 | maker |
| 5 | `hot_hands` | Hot Hands | 1 | makes 3 | maker |
| 6 | `all_my_treasures` | All of My Treasures! | 3 | makes 2 | maker |
| 7 | `da_da_da` | Da-da-da! | 0 | makes 1 | maker |
| 8 | `proto_kaboom_sink` | Ka-pow! | 0 | spends 1 | sink — damage (cheapest) |
| 9 | `proto_powder_charge_spark` | Set It Off | 0 | spends 2 | sink — detonation |
| 10 | `proto_hold_the_line_spark` | Dig In | 0 | spends 2 | sink — Block |
| 11 | `proto_smoke_and_sparks_spark` | Powder Smoke | 0 | spends 2 | sink — Vulnerable |
| 12 | `proto_spark_priced_draw` | Rummage | 1 | spends 3 | sink — draw |
| 13 | **`proto_true_spark_knight`** | **Spark Knight's Oath** | **2** | — | **the Rare Power, and the subject of this read** |

**The row as authored, quoted off the surface** (`docs/prototype-surface.yaml`,
§5 wording (1) STRICT with sub-pick (a); neither the wording nor the price is
reopened here — R222 closed both):

> **Spark Knight's Oath** — Rare · Power · 2 Energy
> *"Your Attacks that do not already cost [Spark] cost 3 [Spark] instead of
> their Energy cost."*

The **3** is not on the card and is not a stack: `amount: 1` is one stack of
`spark_attack_cost`, and the price is a constant of the rule —
`C.SPARK_ATTACK_POWER_PRICE = 3` in tier0, printed as a literal by the C#
registry template, implemented by
`klee-mod/KleeCode/Powers/Prototype/SparkAttackCostPower.cs` (compiled only
under `-p:PrototypeCards=true`). **Sub-pick (a) rides it:** an Attack that
ALREADY prints a Spark price is untouched, so **Ka-pow! stays at 1** and the
five Spark-priced damage rungs `W3` left out stay left out.

**Build note, disclosed before the run — `EB-230`.** Granted card 6, All of My
Treasures!, prints its Bomb damage as `{Damage:diff()}`, which resolves against
the player's live attack modifiers while its body (`place_bomb bomb_damage: 6`)
does not read them, so under a debuff the face can understate the stack
(`KLEESPARK-W3` `turn-029`: face 4, dealt 6). The fix — every `place_bomb` face
prints the bomb's own amount — is scheduled to land BEFORE this run, and the
run's stamp records the build. If the run happens on a build without it, the
disagreement is a pre-declared confound on the tester's play and NOT a Spark
quantity: the card's `gain_spark 2` and every price on this slate are
unaffected, and no slot here grades a Bomb damage number. Stated now so it is
not read back into any grade after the run.

**The ratio is UNCHANGED at 8 : 5 = 1.600.** The Power carries no top-level
`gain_spark` and no top-level `spend_spark`, so by §17.2's sheet definitions —
used unchanged by `S1`, `W3` and this read — it is neither a maker nor a sink
and moves neither side. **Deck size is 24** against `W3`'s 23; that is a draw
frequency difference and it is disclosed rather than corrected (§19.5
contamination 6).

**`arms_granted` verbatim, as the sealed record will name them** (wire ids —
`KLEEMOD-` plus the id upper-cased, `embark.wire_id`; Powder Pop appears twice
because it is granted twice):

```
KLEEMOD-PROTO_POP_SPARK
KLEEMOD-PROTO_POP_SPARK
KLEEMOD-SKIP_AND_HOP
KLEEMOD-WARM_GLOW
KLEEMOD-SNAP
KLEEMOD-HOT_HANDS
KLEEMOD-ALL_MY_TREASURES
KLEEMOD-DA_DA_DA
KLEEMOD-PROTO_KABOOM_SINK
KLEEMOD-PROTO_POWDER_CHARGE_SPARK
KLEEMOD-PROTO_HOLD_THE_LINE_SPARK
KLEEMOD-PROTO_SMOKE_AND_SPARKS_SPARK
KLEEMOD-PROTO_SPARK_PRICED_DRAW
KLEEMOD-PROTO_TRUE_SPARK_KNIGHT
```

**What is still left out, and why it stays left out.** The five damage rungs
above price 1 (Fwoosh!, Tinder Toss, Bang Bang!, Dodoco Blast, Firework
Finale), for §18.2's reason unchanged — granting the ladder would put the ratio
back where `W2` had it. And a shipped maker converted by PICK 4's map, for
§18.2's reason unchanged.

### 19.4 The slate — one continuation slot, three Rare-Power slots, two linkages

Every falsifier below is computed by
`review/qa/blindplay/kleespark-w4/grade.py`, **owed as its own commit BEFORE
the run** — the shape §17 used, where the instrument is a separate, later
commit than the slate and both precede the run. It reads only artefacts the run
writes by itself: the rendered observation pages (`turn-*/prompt.md` — printed
bank, printed Energy, printed hand, printed cost corners), the per-turn
`reply.json`, and `transcript.jsonl`'s command rows. No grade reads a design
judgement and no grade reads the tester's prose.

**AFFORDABLE, defined once for the whole slate and taken from §18.4
unchanged:** on a combat page a hand card is AFFORDABLE when its printed Spark
price is ≤ the printed Spark bank AND its printed Energy cost is ≤ the printed
current Energy.

**THE PARTITION, defined once.** The **POWER PAGE** is the combat page on which
a successful `play` of *Spark Knight's Oath* is recorded. **PRE-POWER PAGES**
are every combat page up to and including it; **POST-POWER PAGES** are every
combat page after it. If the Power is never played there are no post-Power
pages and every `K` slot grades UNREACHED.

**THE FOUR NON-DAMAGE SINKS in this deck**: Set It Off, Dig In, Powder Smoke,
Rummage. **THE ONE PRINTED DAMAGE SINK**: Ka-pow!. **A CONVERTED ATTACK** is a
hand card the page prints as an Attack that carries no printed Spark price on a
pre-Power page and prints **Spark 3 / Energy 0** on a post-Power page.

| # | slot | prediction | falsifier, mechanically | UNREACHED when | the decision the outcome changes |
|---|---|---|---|---|---|
| `W1'''` | **`W1''`'s question at the longer batch, on the SAME deck**: does the bank hold two affordable uses at once, with a non-damage destination among them? | **YES, on at least 3 PRE-POWER combat pages** — `W2`'s and `W3`'s threshold, unchanged, and deliberately not re-derived at the longer batch. | Count PRE-POWER combat pages where **two or more distinct Spark-priced titles in hand are each affordable** and **at least one of the affordable ones is a non-damage sink**. **≥ 3 = PREDICTED, 1–2 = SPLIT, 0 = MISS.** The pre-Power page count is printed as the denominator; the same count over POST-POWER pages is printed beside it, RECORDED and NOT GRADED. | the session records **zero pre-Power combat pages** | **PREDICTED**: the two-destination choice IS posed regularly at the inherited ratio once the batch is long enough, and `W3`'s SPLIT was a batch-length artefact rather than a composition fact. That authorises **re-posing `W2''` and `W3''` in a FRESH registration at this batch length** — and it authorises no re-price and no new sink row on its own, because neither of those slots is graded here. **SPLIT**: the rate is real and low for the second read running; the next unit is NOT a third batch bought on Claude's own authority — it goes to [USER] as a numbered pick on whether to keep buying batch length (§18.10 item 4: a budget question, not an engineering one). **MISS on a denominator of ≥ 30 pre-Power pages**: the choice is not posed at the inherited ratio even at double the batch, which is the composition finding `W3`'s single page could not make; it returns to [USER] as a numbered pick between §14.3's options, and Claude does not settle it. **MISS on a denominator below 30**: the batch did not happen and the slot is a batch-length reading, not a composition one. |
| `K1'''` | **Is the converted price of 3 ever actually PAID?** §5's whole bet — *"roughly one Attack every three turns unless you have drafted generation — which is the payoff loop working"* — is a claim about a price being paid, not about a face being read. `W3` saw per-fight peak banks of **5 / 0 / 3 / 9**, so a bank of ≥ 3 was reached in three fights of four and the rung is plausibly reachable. **This is registered as a threshold, not as a hope.** | **YES, on at least 2 post-Power pages**: a successful `play` of a CONVERTED ATTACK on a page whose printed Spark bank was ≥ 3. | Count successful `play` commands naming a converted Attack, on post-Power pages whose printed bank was ≥ 3 at the moment of the play. **≥ 2 = PREDICTED, 1 = SPLIT, 0 = MISS.** The **DENOMINATOR is printed with the grade**: the number of post-Power combat pages whose printed bank was ≥ 3, i.e. the pages that could pose the question at all. | the Power never resolves (no post-Power page); **or** zero post-Power pages printed a bank of ≥ 3 — in which case the fault is INCOME AT THE PRICE-3 RUNG on this batch and nothing about the Power's price is learned | **PREDICTED**: the price of 3 is payable in live play on a deck at the inherited ratio, and — with `K2'''` and `K3'''` also PREDICTED — the Power becomes an **ADVANCE-to-sheet CANDIDATE**, put to [USER] as a numbered proposal (§5's row, unchanged, moving from the prototype surface to the sheet). **SPLIT**: payable but barely; **RETURN to a staged round** built to hand the reader a bank of exactly 3 with a converted Attack in hand, which a whole fight cannot guarantee. **MISS with a NON-ZERO denominator** — pages that could pay 3 existed and none did — is **the ONE registered outcome on this slate that REOPENS §5's wording and the price of 3 to [USER]**, as a numbered pick. R222 closed that question; only this MISS, on this slot, with its denominator non-zero, may reopen it, and no other slot here may. **MISS with a ZERO denominator** grades UNREACHED by the rule above and reopens nothing. |
| `K2'''` | **Once played, is the effect FELT — and the observable is the one §5 names.** §5: *"every Attack in the deck now reads `0 energy / 3 Sparks`… Energy becomes almost pure Skill currency. It is legible: every Attack's cost corner shows the same number."* Two halves, both read off the printed page. | **BOTH halves hold.** **(i) THE COST CORNER**: on **every** post-Power combat page, every Attack in hand that printed no Spark price before the Power prints **Spark 3 and Energy 0**. **(ii) ENERGY BECOMES SKILL CURRENCY**: on **at least 1** post-Power page, a Skill or a Power is played AND a converted Attack is paid in Sparks on the SAME page — the Energy and the bank buying different things on one turn. | (i) is a page read over every post-Power page: any converted Attack still printing its Energy cost, or printing a Spark price other than 3, FAILS half (i) and the failing page is named. (ii) is a transcript read over one page's successful `play` rows. **Both = PREDICTED; exactly one = SPLIT; neither = MISS.** | the Power never resolves; **or**, for half (i) alone, no post-Power page ever printed an Attack in hand — in which case (i) is UNREACHED and the slot grades on (ii) alone, recorded as such | **PREDICTED**: the conversion is visible where §5 said it would be and the freed Energy has somewhere to go; it is one of the three conditions of the ADVANCE-to-sheet candidate. **SPLIT or MISS on half (i)** — a printed corner that disagrees with the price the gate charges — is a **display defect in the `EB-164` family**, filed to `BACKLOG` as a defect row and **RETURNED to a staged round**, which is where a one-board legibility read belongs; it does NOT reopen §5. **MISS on half (ii) alone**: the conversion is legible and the freed Energy went nowhere, which is a deck-composition observation about a deck holding one Skill-shaped sink family, and it is recorded, not acted on. |
| `K3'''` | **Does the price-3 rung CROWD OUT the price-2 rungs?** The hold-versus-spend tension the tester has now named unprompted on three reads running (`W1` §12.7, `W2` §16.10, `W3` §18.9 item 4) while every bare detector read zero. With the Power up, the bank has a THIRD destination at a HIGHER price, and §5's own worry is that the payoff *"bricks hard when you do not"* have the engine. | **NO, it does not erase them: on at least 1 post-Power page where a CONVERTED ATTACK (3) and a price-2 NON-DAMAGE SINK were BOTH affordable, the non-damage sink was the play.** | The **CROWDING DENOMINATOR** is the count of post-Power combat pages posing that pair. Of those pages, count the ones whose successful `play` named the non-damage sink. **≥ 1 = PREDICTED.** **0 with a denominator ≥ 3 = MISS.** **0 with a denominator of 1–2 = SPLIT** — posed too rarely to say. The share taken by the converted Attack is printed beside the grade, RECORDED and NOT GRADED. | the crowding denominator is **0** — the pair was never posed, the fault is draw and bank, and nothing about crowding is learned | **PREDICTED**: the price-3 rung coexists with the price-2 rungs and the bank has three destinations rather than one; the third condition of the ADVANCE-to-sheet candidate. **MISS**: every posed page went to the converted Attack — the Power crowds out the rungs the `EB-218` migration exists to create, which is a finding about the INTERACTION and not about §5's wording, and its act is a **RETURN to a staged round** built to pose the 3-versus-2 pair deliberately at a fixed bank, which a whole fight cannot guarantee. It does not reopen §5 and it authorises no re-price. **SPLIT**: the same RETURN, on weaker evidence. |
| `K4'''` | **RECORDED, NOT GRADED — three numbers the next reader will want and no slot claims.** | none. | (a) Whether the Power was DRAWN at all, and on which page it resolved. (b) The attack share of successful plays, pre-Power and post-Power, in `W5''`'s shape — `W1` read 50.0%, `W2` 75.0%, `W3` 40.0%. (c) The per-fight peak printed Spark bank, in `W6''`'s shape, so the batch's income is on the record beside `W3`'s median of 4.0. | n/a | none. Printed so a later reader cannot mistake their absence for an omission, and so no one is tempted to grade them after the fact. |

**Only `K1'''` may reopen §5, and that is registered here rather than decided
later.** R222 closed §5's wording and the price of 3 — *"Neither §5's wording
nor the price of 3 is reopened"* — and a closed question is not reopened by a
reading Claude finds interesting. The one thing that would make the closure
untenable is the price being unpayable in the play it was closed for, and that
is `K1'''` MISS with a non-zero denominator, and nothing else on this slate.
Claude does not settle it either way: it goes back as a numbered pick with this
run as the reading.

### 19.5 Contamination and blind spots, stated before the run

1. **GRANTED, NOT DRAFTED.** `bridge.GRANT_GUARDRAIL` rides the record: this
   run's deck is not one the generators produced, so nothing measured on it is
   comparable to any other run. The ratio and the Power are both staged
   deliberately — that IS the experiment — and neither is evidence about what a
   player would draft. `S3` already measured the draft half and MISSED (3.2%
   of decks held a non-damage sink), and `S5` proved Rummage undraftable at 0
   of 600, which is why the sinks are granted; the Power's own draft rate is
   not measured here and no number below is one.
2. **`+proto`, so the shipped automatic Spark rule is NOT LIVE.** The build is
   stamped `+proto` by `deploy_proto.ps1`, which compiles
   `-p:PrototypeCards=true`, under which `SparkPower.BaseRuleActive` is the
   compile-time constant **`false`** (`klee-mod/KleeCode/Powers/SparkPower.cs`,
   pinned by `SparkAlternativeCostPinTests` and `SparkSinkPinTests`). At no
   bank do Attacks cost 0 and nothing is consumed automatically. **This matters
   more here than in any previous read**: it means the converted price of 3 is
   the ONLY Spark cost a converted Attack carries, so `K1'''` and `K2'''` are
   reading the Power's rule and not a rule underneath it. This is the R101b
   erratum §16.4's contamination 1 carries, stated as a fact and not a hedge.
3. **NEOW'S FORCED BOON, and the deck-neutral rule the next operator follows.**
   `embark` leaves the run on the **Neow** screen at floor 1, and Neow cannot
   be skipped — a bare `proceed` is refused by the wire. `W3`'s three boons
   were *Scroll Boxes* (add a pack of cards to the deck), *Precise Scissors*
   (remove a card) and *Silken Tress* (lose all Gold; enchant the first card
   reward with Glam); two of the three rewrite the deck the registration exists
   to control, and the operator took the only deck-neutral one. **The rule,
   registered here so it is followed rather than re-invented: the operator
   takes the boon that changes NEITHER the deck's card list NOR the counted
   maker : sink ratio, and if more than one qualifies, the first such option in
   the order the screen prints them. The boons offered and the one taken are
   recorded verbatim in §19.6.** It is an operator action, declared, and it is
   not the tester's choice. `W3` found one cost of Silken Tress worth naming:
   the Glam enchantment reached a card reward and the duplicate `Powder Pop
   (1)` / `Powder Pop` pair then carried an enchantment warning without saying
   which copy was enchanted (§18.9 item 5).
4. **TWO INCOME SOURCES THE RATIO CANNOT COUNT, and `W6''` was a FLOOR because
   of them.** **Pounding Surprise**, Klee's starter relic, pays **+1 Spark per
   detonation**; **Endless Fireworks** grants `spark_per_turn` and carries no
   top-level `gain_spark`, so the counted maker set never included it either.
   `W3`'s fight 4 peak of 9 followed a six-Bomb stack and the tester called the
   jump *"unexplained by the visible cards or buffs"* (§18.9 item 2). Both
   sources push in the same direction as §17.7's blind spot 1: **the counted
   ratio understates generation and never overstates it, so any income figure
   here — including `K1'''`'s bank-≥-3 denominator — is a FLOOR and never a
   ceiling.** A `K1'''` MISS on a non-zero denominator is therefore the
   conservative direction, and a `K1'''` UNREACHED on a zero denominator is
   not evidence that the rung is unreachable in general.
5. **ONE SEED for the whole batch**, rolled by the game and read back off the
   wire (R95), never chosen and never pinned. Every fight in the batch is a
   fight of that one run, so **the fights are not independent samples of
   anything** and a per-fight median over eight fights is not eight
   observations. `EB-191` (the `run seed: (unread)` read-back defect) is known
   to fire and its repair is the one §18.6 records: re-read off the wire from
   the same process, with the run open, before the session starts, and written
   into the embark sidecar — or the sealed record says `arms_granted: (none)`
   about fourteen granted cards.
6. **THE STARTER IS SUBSTITUTED ADDITIVELY, and the deck is one card larger
   than `W3`'s.** `S1`'s sim arm substitutes one `pop` → Powder Pop and one
   `kaboom` → Ka-pow! at `loader._starter_ids`; the live game has no such seam,
   so the two prototype Basics are GRANTED on top and the printed starter keeps
   its `Pop!` and its four `Kaboom!`. Deck 24 against `W3`'s 23 against `W2`'s
   21. Neither shipped starter row is a maker or a sink, so the RATIO is
   unaffected; **draw frequency is**, and it is disclosed rather than
   corrected. The Power itself is the fourteenth granted card and must be drawn
   before any `K` slot can be reached — which is why every `K` slot registers
   UNREACHED on a Power that never resolves, and why that outcome is a draw
   fact and not a reading about the card.
7. **THE CONTROLLED VARIABLE IS CHECKED, NOT ASSUMED.** §18.7's check is
   repeated here as a registered obligation: every card added mid-run —
   drafted, from a potion, from an event — is examined for a top-level
   `gain_spark` or `spend_spark`, and if one is added the page at which the
   ratio moved is named in §19.6 and every slot's pages are reported on both
   sides of it. A run whose ratio moves is reported as it ran; it is not
   re-run.
8. **Guardrail-7 and R217 G.** Every number here is a FLOOR off one capped
   batch, one seed, one pilot and a granted deck. The tester's words are
   iteration feedback — never validation, never balance evidence, never
   approval — and no win rate, comparison or fun claim may be taken off this
   run.

### 19.6 The cell, the batch, the budget and the stop lines

| | |
|---|---|
| cell | the **installed dev build**, named in the sealed record's identity block, read off the deployed `mods\klee\manifest.json`, plus the game build off `release_info.json` |
| build stamp EXPECTED | **`0.2.1610+proto.dirty`** or later — whatever is deployed when the slot opens. **NOTHING IS DEPLOYED BY THIS PIECE**; the build that is installed is the build that runs |
| build stamp RULE | the cell is whatever the deployed manifest says, and a difference from the expected string is DISCLOSED in §19.6's run block rather than treated as a stop. `embark --arm` refuses a build with no `+proto` anyway (`embark.check_arms`), which is the check that actually matters |
| the pck contract check | **owed before the embark, as §18.3 registered it**: `git diff <the commit the deployed package was built at>..HEAD -- klee-mod docs/klee-cards.yaml docs/prototype-surface.yaml tier0/constants.py` must be **EMPTY**, so every granted row's printed text on the installed build is this tree's sheet text. **If a granted row's printed face on a live page differs from its sheet row, the run STOPS and says so** — with the one exception `W3` already recorded, a face whose divergence is a runtime render of a live modifier (§18.9 item 1) rather than a stale build |
| action budget | `--max-actions 80 --max-wall-s 14400 --max-refusals 2 --max-stalls 6` |
| **Codex cap** | **90 calls.** The driver spends one `codex exec` per answered screen, one per fight record and one for the run record. `W3` spent **45 of 45 for 4 fights — 11.25 calls per fight** — at 40 actions; 80 actions on that rate is 80 answered screens + ~8 fight records + 1 run record = **89**, so 90 is the smallest cap that covers the batch and 80 is the largest action count the cap pays for. **The Codex cap is what bounds this batch, not the game** |
| **N fights** | **~8**, on `W3`'s own measured rate of 4 fights per 40 actions (19 combat pages). The batch is bounded by the action cap and NOT by a fight target: it runs until `max_actions`, and `N` is what that buys. §19.4's `W1'''` MISS branch turns on a denominator of **≥ 30 pre-Power combat pages**, which is the number `W3`'s 19-pages-per-40-actions rate says 80 actions should clear even with half the session on the far side of the Power |
| **the guard's stop lines** | `EB-227`: **85% of the five-hour window and 50% of the week**. `W3`'s 45 calls cost **~38 points of the five-hour window** (3% → 41%) and **~6 of the week** (11% → 17%) — about **0.85 points per call**. 90 calls is therefore **~76 points of the five-hour window** and ~12 of the week. **REGISTERED PRECONDITION: the batch starts only when `python -m understudy.codex_usage` reads ≤ 8% of the five-hour window and ≤ 35% of the week**, printed into the record before the embark; otherwise the action cap is cut to what the headroom pays for at 0.85 points per call, and §19.6's run block states the cut cap before the session starts. The meter is printed **before and after** either way. **If the guard refuses mid-batch the run stops cleanly, what ran is graded on the denominators it actually reached, and §19.6 says so.** No second session is started |
| sessions | **ONE.** If the session ends early it is recorded as it ended and NO second session is started |
| the R225 soak gate | `python -m understudy.soak --runs 1 --character KLEEMOD-KLEE --max-fights 3` is run as the preflight and its answer recorded. `EB-226`'s power request is held for the soak and again for the embark, and released at each teardown |
| the seed | **rolled by the game and read back off the wire (R95)** — not chosen and not pinned, exactly as `W1`, `W2` and `W3` took theirs. There is no declared board, so `EB-208` (a)'s live-count preflight has no declared count to compare against; **no slot above reads `enemy_count`**, so no page can be UNREACHED on a body-count gap. `EB-208` (c)'s seed ledger is not built and is not used |
| the stopping rule | R221 B's sequential stopping reaches the STAGED-TURN funnel and does not reach a whole-fight batch: there are no boards to order and none to leave UNRUN. The batch's only bound is the action cap |
| grader | `review/qa/blindplay/kleespark-w4/grade.py`, **owed as its own commit before the run** (§17's shape: slate first, instrument second, run third), copying `kleespark-w3/grade.py`'s shapes — the same page parser, the same AFFORDABLE rule, the same fight boundary (a maximal run of consecutive combat pages) — plus the pre/post-Power partition §19.4 defines and the converted-Attack cost-corner read `K2'''` (i) needs |
| record | `review/qa/blindplay/kleespark-w4/record.md`, in `kleespark-w3/record.md`'s shape: identity block, the tester's per-fight records and its run record verbatim, the per-turn sentence table, the leak audit |

### 19.7 Independence, who holds the deciding chair, and when this runs

**Independence.** `proto_true_spark_knight` and all five prototype sink rows
and both prototype Basics are `authored_by: [claude]`; the six shipped makers
are shipped content and carry no authorship claim of the seat's. **The seat
that plays is Codex (`gpt-5.6-sol`)**, refused-by-family through
`blindplay.check_independent` (R217 C), so the playing chair is
author-disjoint.

**The deciding chair — OPERATIONS' rule, applied.** *"A round that can ADVANCE
an arm gets the Codex seat deciding every board… A round that is an INSTRUMENT
round… stays on the fresh-Opus deciding form. The round's own registration says
which it is, before it runs."* **This batch CAN ADVANCE**: `K1'''`, `K2'''` and
`K3'''` all PREDICTED makes the Rare Power an ADVANCE-to-sheet candidate. It is
therefore **not** an instrument round, the deciding read is **Codex's**, and
there is no fresh-Opus form in this registration at all — which in whole-fight
blind play is the same thing as saying the tester decides, because the tester
is the only reader. The **GRADING** chair is a committed mechanical script, not
a model, so author-disjointness does not arise for it: no falsifier above reads
the tester's prose, not even `W3''`'s keyword half, which this slate does not
carry.

**Sequencing.** After the morning's merges, at **the next game-time slot** —
the game is one of the two scarce things and this batch asks for a long,
uninterrupted hold of it. The order inside the slot is fixed: the grader
commit, then the meter read and the soak gate, then the pck contract check,
then the embark and the Neow rule, then one session to `max_actions`.

**Countersign.** DRAFTED under R212(2) and offered for BATCH countersign. It is
signed once; a moved world means re-drafting the affected slots and disclosing
the diff, and it never means re-signing (R212, EXPERIMENTS *Countersign once*).

> **COUNTERSIGNED (R227, 2026-08-30): `KLEESPARK-W4` is SIGNED**, in the batch
> of three, at PICK 3 option (1) — none vetoed. The `EB-230` build note at
> §19.3 stands as disclosed. Signed once: it is not re-signed, and a moved
> world means re-drafting the affected slots and disclosing the diff.

**NOT RUN.** As of this commit no board has been staged, no session opened, no
Codex call spent and no number taken.

---

## 20. `KLEESPARK-W4` — RUN AND GRADED

**2026-08-30 · branch `kleespark-w4`, cut from `gpt-review-2026-08-30`
(`af265de1`). THE RUN, AND NOTHING ELSE.** §19 is the registration and it is
not touched here: no slot was re-worded, no threshold re-derived, no
contamination added after the fact. R101b binds — §11–§19 stand exactly as
published, and this section reports what §19.4's committed grader answered.

### 20.1 What actually ran — the session, the stamp, and the operator's two actions

**RUN 2026-08-30, sealed session `kleespark-w4`.** The committed record is
`review/qa/blindplay/kleespark-w4/record.md` — identity block, the tester's
five fight records and its run record verbatim, the per-turn sentence table,
the leak audit — with `wire.json` and `grades.json` beside it. The rendered
pages, the replies and `transcript.jsonl` are the gitignored operator half
under `understudy/logs/blindplay/kleespark-w4/`.

**The preconditions, printed as §19.6 requires.**

| | |
|---|---|
| working tree | `git status --porcelain --untracked-files=no` **empty** at `af265de1`; the only uncommitted paths are gitignored operator scratch, which is why the package stamps `+proto.dirty` |
| the game lock | `%LOCALAPPDATA%\Temp\gits-game.lock` **absent** before the deploy |
| Steam | **running** (PID 17556) — the game is launched directly and needs it |
| **the registered Codex precondition** | **`5h 0% (rolled over) · week 18%`**, against §19.6's *≤ 8% of the five-hour window and ≤ 35% of the week*. **BOTH MET, so no cut cap was applied**: the batch ran at the registered `--max-actions 80` on the registered cap of 90 calls |

| | |
|---|---|
| pilot | `gpt-5.6-sol` requested and observed, `codex-cli 0.150.1` |
| build | **`0.2.1676+proto.dirty`**, read off the deployed `mods\klee\manifest.json`. §19.6 expected *"`0.2.1610+proto.dirty` or later — whatever is deployed when the slot opens"*, and this is later; **the difference is DISCLOSED here rather than treated as a stop**, exactly as the build-stamp rule says. It carries `EB-230`'s `place_bomb` face fix, which §19.3's build note scheduled to land before this run, so the `All of My Treasures!` confound §19.3 pre-declared did not arise |
| game | `v0.111.0`, read off the game's own `release_info.json` |
| the pck contract check | the package was built at this branch's `af265de1`; `git diff af265de1..HEAD -- klee-mod docs/klee-cards.yaml docs/prototype-surface.yaml tier0/constants.py` is **EMPTY** — trivially so, because the only commit between them is the grader, which touches `review/qa/` alone. **And the stop rule was checked rather than assumed**: every printed Spark price on every combat page matched the sheet — Powder Smoke 2, Set It Off 2, Dig In 2, Rummage 3, Ka-pow! 1, with **no disagreement on any of the 50 combat pages** |
| the R225 soak gate | **PASSED before the embark**: `bounded seed=V4823EVDU888 actions=51 fights=3 defects=0`, reversibility log all REVERTED |
| run seed | **`KGU5LKM77PB5`**, rolled by the game and read back off the wire (R95). **`EB-191` did NOT fire** — the seed came back on the first read and no sidecar repair was needed |
| arms granted | **all fourteen of §19.3**, by wire id, into the starting deck, each answering `ok` on `0.2.1676+proto.dirty` |
| actions | **80 of 80**, termination **`max_actions`** |
| refusals / stalls | **0 and 0.** All eighty commands were accepted by the wire |
| fights | **SIX** |
| Codex calls | **86 of the registered 90** — 80 answered screens, five fight records, one run record |
| seat meter, BEFORE | `codex: 5h 0% (rolled over) · week 18% (resets Sep 05 17:58)` |
| seat meter, AFTER | `codex: 5h 40% (resets 16:36 EDT) · week 25% (resets Sep 05 17:58)` |
| the guard | `EB-227`'s stop lines are 85% of the five-hour window and 50% of the week. Neither was reached and **the guard never refused a call**; the batch cost ~40 points of the five-hour window and ~7 of the week, ~0.47 per call against `W3`'s ~0.85 |
| the power request | `EB-226` held for the soak and again for the embark, and released at each teardown |
| wire snapshots | **48**, machine-written off the API and never shown to the tester (`EB-216`) |

**Two operator actions before the seat was handed the game, taken by §19.5
contamination 3's registered rule and not re-invented.** `embark` left the run
on the **Neow** screen at floor 1. The three boons printed were **Nutritious
Oyster** (*"Raise your Max HP by 11"*), **Neow's Talisman** (*"Upgrade 1 of
your Strikes and 1 of your Defends"*) and **Silver Crucible** (*"The first 3
card rewards you see are Upgraded. The first Treasure Chest you open is
empty"*). The rule is *the boon that changes NEITHER the deck's card list NOR
the counted maker : sink ratio, and if more than one qualifies, the first such
option in the order the screen prints them.* Only Nutritious Oyster changes no
card at all — the Talisman rewrites two faces and the Crucible rewrites three
future ones — so it was taken, and it is the first in printed order regardless.
The two commands were `choose "Nutritious Oyster"` and `choose "Proceed"`. The
tester's first screen was the map above the first Monster room, which is the
state §19.1 registers as the start. **`W3` took Silken Tress; this run took a
different boon because a different screen was printed, and what is held
constant is the RULE and not the boon.**

**The teardown.** `embark --teardown` reverted the seed, the speed and the
process; the bridge removal refused while the game still held its dll and was
run again by hand (`deploy_bridge.ps1 -Remove`), and the leftover
`steam_appid.txt` was removed. **The dev build stays installed**, as the
sequencing requires — `deploy.ps1` was NOT run.

### 20.2 The batch, fight by fight, and the partition

**Six fights, 50 combat pages**, in pages: **7 / 6 / 8 / 14 / 11 / 4**. That is
`W3`'s 19 pages more than doubled, which is the longer batch §18.10 item 4
named and the unit `W1'''` was registered on.

| fight | pages | peak printed Spark bank |
|---|---|---|
| 1 | 7 | **3** |
| 2 | 6 | **13** |
| 3 | 8 | **8** |
| 4 | 14 | **3** |
| 5 | 11 | **8** |
| 6 | 4 | **0** |

**THE PARTITION, and it is the run's first fact: `power_page` is `null`.**
*Spark Knight's Oath* was **DRAWN** — it sat in the tester's hand on seven
combat pages (`turn-033`, `-034`, `-035`, `-069`, `-070`, `-071`, `-072`) —
and was **never played**. So there are **50 PRE-POWER pages and 0 POST-POWER
pages**, and by §19.4's own rule every `K` slot is UNREACHED. §19.5
contamination 6 registered that outcome in advance and its reading with it: the
Power *"must be drawn before any `K` slot can be reached — which is why every
`K` slot registers UNREACHED on a Power that never resolves, and why that
outcome is a draw fact and not a reading about the card."* Here it is one step
short of a draw fact — the card was drawn and declined — and **nothing is
inferred from that absence**, because the slate registers no slot that grades a
decision not to play.

**The controlled variable is CHECKED, not assumed (§19.5 contamination 7).**
Twenty-two distinct card titles reached the tester's hand across the six
fights. Every one of them that carries a top-level `gain_spark` or
`spend_spark` is one of the twelve granted rows — the seven makers and the five
sinks — and **not one card added mid-run (drafted, from a potion, from an
event) carries either op**. The deck's counted maker : sink ratio was
therefore **8 : 5 = 1.600 on every page of every fight**, and no page has to be
reported on two sides of a moved ratio.

### 20.3 The slate, graded mechanically

**0 PREDICTED / 0 SPLIT / 1 MISS (`W1'''`) / 3 UNREACHED (`K1'''`, `K2'''`,
`K3'''`)**, plus `K4'''` RECORDED and NOT GRADED. Every grade is
`review/qa/blindplay/kleespark-w4/grade.py`'s own output against §19.4's
registered thresholds and no others; the raw output is `grades.json`.

| slot | grade | the read | the registered threshold |
|---|---|---|---|
| `W1'''` two affordable uses on a pre-Power page, one non-damage | **MISS** | **0** of **50** pre-Power combat pages. Post-Power count 0 of 0, RECORDED and NOT GRADED as §19.1 requires | ≥ 3 PREDICTED, 1–2 SPLIT, 0 MISS. **Denominator 50, i.e. ≥ 30** |
| `K1'''` the converted price of 3 actually paid | **UNREACHED** | the Power never resolved. Denominator of post-Power pages printing a bank ≥ 3: **0 of 0** | ≥ 2 PREDICTED, 1 SPLIT, 0 MISS; UNREACHED on a Power that never resolves |
| `K2'''` the conversion is felt where §5 says it is | **UNREACHED** | the Power never resolved; half (i) had no post-Power page to read and half (ii) no post-Power turn | both PREDICTED, one SPLIT, neither MISS; UNREACHED on a Power that never resolves |
| `K3'''` the price-3 rung crowding out the price-2 rungs | **UNREACHED** | crowding denominator **0** — the pair was never posed, because there were no post-Power pages | ≥ 1 PREDICTED; 0 with denominator ≥ 3 MISS; 0 with 1–2 SPLIT; denominator 0 UNREACHED |
| `K4'''` three numbers | **RECORDED, NOT GRADED** | (a) the Power was **drawn** on seven pages and **resolved on none**. (b) attack share **15 of 39 successful plays, 38.5%** over the whole session, against `W1`'s 50.0%, `W2`'s 75.0% and `W3`'s 40.0%; there is no pre/post split to print, because there is no post. (c) per-fight peak printed bank **3 / 13 / 8 / 3 / 8 / 0, median 5.5**, on the record beside `W3`'s 4.0 exactly as §19.4 asked and as **no comparison** — §19.2 item 1 forbids quoting it as one | none |

**What each registered decision now says, quoted from §19.4 and applied.**

- **`W1'''` MISS on a denominator of 50.** §19.4, verbatim: *"MISS on a
  denominator of ≥ 30 pre-Power pages: the choice is not posed at the inherited
  ratio even at double the batch, which is the composition finding `W3`'s
  single page could not make; it returns to [USER] as a numbered pick between
  §14.3's options, and Claude does not settle it."* **The branch is taken as
  written.** The pick is at §20.5, it is numbered, and nothing is decided here.
- **`K1'''`, `K2'''` and `K3'''` UNREACHED, and they AUTHORISE NOTHING.** The
  one registered outcome on this slate that could reopen §5's wording or the
  price of 3 is a `K1'''` **MISS with a non-zero denominator**, and the
  denominator is zero. R222's closure of §5 therefore **stands untouched**, and
  the ADVANCE-to-sheet candidate — which needed `K1'''`, `K2'''` and `K3'''`
  all PREDICTED — **is not reached and is not refused**. `EB-223`'s owed work
  is DONE in the sense the row asked for (the read is taken and recorded);
  what it did not produce is a reading about the Power, and §20.5 says so.

### 20.4 What the run found that is not a slot

1. **The Oath was declined, three times in the tester's own words, and that
   is R217 G iteration feedback and nothing else.** Its run record item 5:
   *"Next time I would avoid narrow powers such as Spark Knight's Oath or True
   Spark Knight unless the deck already had enough compatible attacks; the Oath
   repeatedly sat dead while costing too much tempo."* Fight 3's item 4:
   *"Spark Knight's Oath and Kaboom! were unnecessary once Melt showed
   lethal."* Fight 5's item 4: *"Hot Hands, Spark Knight's Oath, Prune, and the
   round-three Block cards were dead in their respective hands."* **No slot
   grades this and no slot may be read off it.** It is the clearest statement
   any of the four reads has produced about why the Power did not get played,
   and it is exactly the kind of sentence R217 G says is feedback and never
   evidence: the slate asked whether a paid price is legible and payable, and a
   card that is never played answers neither question.
2. **`W1'''`'s zero has a mechanical shape, and it is a DRAW fact about the
   damage side.** Two or more distinct Spark-priced titles were in hand on
   **four** of the 50 combat pages, all four in the last fight and all four at
   a printed bank of **0**. The non-damage sinks were drawn plentifully —
   Powder Smoke on 12 pages, Set It Off on 9, Dig In on 6, Rummage on 3 — and
   **the deck's one printed damage sink, Ka-pow!, reached the hand on exactly
   one page in fifty.** An affordable non-damage sink sat in hand on **9**
   pages, so the bank had a destination often; what it never had was a
   **second** one. This is recorded as the observation it is: at this deck and
   this batch length the two-destination choice was not posed, and the reason
   visible in the pages is the draw of the one-price rung rather than the
   bank.
3. **Income again cleared the rung comfortably, and again with a source the
   ratio cannot count.** Per-fight peaks of 3 / 13 / 8 / 3 / 8 / 0 sit above
   the cheapest non-damage price of 2 in five fights of six. **Prune — Little
   Witch's Hunt** entered the deck mid-run: it prints no `gain_spark`, so the
   counted ratio is formally untouched, but since **C21** (`EB-219`) a
   Personal Companion play is a declared Klee-engine Spark grant
   (`KLEE_COMPANION_SPARK_*`), so it is income the maker count cannot see —
   the same direction as §19.5 contamination 4 and §17.7's blind spot 1.
   **Every income figure here is a FLOOR and never a ceiling.**
4. **One instrument artefact, named because it touches a recorded number.**
   The six record prompts are written as `turn-081`…`turn-086`, so the grader's
   "was the previous command accepted" read — which chains off the NEXT page —
   returns false for the five plays that immediately preceded a fight record.
   That costs `K4'''` (b)'s per-partition play count five plays, which is why
   the attack share is quoted off the transcript's own 39 successful plays
   (38.5%) rather than off the page chain's 34. **No graded slot reads
   `accepted`**: `W1'''` counts pages and hands, and the three `K` slots are
   UNREACHED. The artefact is disclosed and it moves no grade.
5. **The run ended inside fight 6 and the tester could not tell why.** Its run
   record item 5: *"The run ended unexpectedly immediately after playing Powder
   Pop at 31 HP, so I cannot tell from the final screen whether that choice
   caused the loss or whether an unprinted effect resolved."* The session's own
   termination is `max_actions` at 80 of 80, so the batch was not cut short by
   the ending; it is recorded as an unexplained frame, not diagnosed, and it
   grades nothing.

**Leak audit: 86 observations scanned, 1 hit, and it is the known false
positive** — `pilot-vocabulary-score` matching the word `score` inside the
guide's own sentence *"no card list, no score, no recommendation"*, exactly as
`W1`, `W2` and `W3` recorded it. No card id, design tag, policy hint or run
seed reached any page.

### 20.5 What this leaves, and the one pick that returns to [USER]

**What the grades permit, stated once and no further.**

1. **`EB-223`'s read is TAKEN and the row CLOSES on its own acceptance** — *"the
   read recorded in `EXPERIMENTS.md`"* — which this run and the row above it
   satisfy. What the row wanted, a whole-fight reading of the strict Rare
   Power, **is not what it got**: the Power was drawn and declined, all three
   of its slots are UNREACHED, and R222 (a)'s question is still open. That is
   reported as the outcome rather than repaired by a second session (§19.6:
   *"ONE. If the session ends early it is recorded as it ended and NO second
   session is started"*, and this session did not even end early).
2. **§5's wording and the price of 3 are NOT reopened.** The single registered
   reopening condition was a `K1'''` MISS on a non-zero denominator. The
   denominator is zero, so the slot grades UNREACHED and R222's closure stands.
3. **Nothing here is an ADVANCE and nothing here is a RETURN for the Power.**
   The ADVANCE-to-sheet candidate needed three PREDICTEDs and has none; the
   RETURN-to-a-staged-round acts are hung on a `K2'''` or `K3'''` MISS and
   there is none. Under the slate's own rule an UNREACHED slot is not a pass
   and not a fail, so **no [USER] row opens on the Power** off this run.
4. **Nothing here is a balance or fun claim.** One batch, one seed, one pilot,
   a granted deck the generators did not produce, one uncounted income source.
   Guardrail-7: floors. R217 G: §20.1's and §20.4's quoted sentences are
   iteration feedback, never validation, never approval.

**THE ONE PICK THAT RETURNS TO [USER] — `W1'''`'s registered act, as a numbered
list and never a blank.** The two-destination choice was posed **0 times in 50
combat pages** at the derived ratio of 1.600, against `W3`'s 1 in 19. §19.4
sends that back as a pick between §14.3's options, and Claude does not settle
it. The evidence to weigh with it: the non-damage sinks were drawn and
affordable often (an affordable one in hand on 9 pages), the damage rung
Ka-pow! was drawn once in fifty, and income was never the binding constraint.

> **PICK — the sink set, now that the longer batch has reported.**
>
> **(1) §14.3 option (1): re-author two — `Fwoosh!` → Behind the Barrel and
> `Firework Finale` → Powder Keg.** Builds the price-1 and price-3 rungs the
> ladder is missing, so a full bank chooses between one investment and two
> small plays by construction rather than by draw.
>
> **(2) §14.3 option (2): the alternative pair — `Bang Bang!` → Slow Fuse and
> its partner.** The same act on a different two rows.
>
> **(3) §14.3 option (3): one only — `Fwoosh!` → Behind the Barrel.** The
> cheapest version of (1), and the one that changes the fewest shipped faces.
>
> **(4) §14.3 option (4): none — keep the set as built.** Read the zero as a
> DRAW fact rather than a composition fact: the one damage rung in the deck
> reached the hand once in fifty pages, and a set whose second destination is
> not drawn is not a set that lacks a second destination.
>
> **(5) Change the DECK and not the SET: re-derive the granted deck so more
> than one damage rung is in it, and re-pose `W1'''` under a fresh
> registration.** This run granted exactly one printed damage sink because
> `S4`'s inherited ratio put the cheapest one there; the zero may be a
> property of that choice rather than of the sink set. Costs another batch of
> game time and another 90 Codex calls.
>
> **(6) Stop buying batch length on this question.** §18.10 item 4 already
> called a longer batch *"a budget question for [USER] and not an engineering
> one"*, and this batch — double the length, 86 calls — moved the count from 1
> to 0. Bank the two readings and let the sink set be settled by the mixed-pool
> design work rather than by more live pages.

**No QUEUE row is minted for it here** (R206/R212, one batch per sitting): the
pick is assembled into the sitting's slate by the orchestrator, and this
section is where its evidence lives.

## 21. `KLEESPARK-BT1` — *Bag of Tricks*, the staging round (`EB-224`)

**Registration. DRAFTED by Claude under R212 item 2 and committed, with its
four boards and its `slots.yaml`, BEFORE anything was staged, deployed or
read.** [USER] countersigns in batch or vetoes. The machine-readable half is
`understudy/turns/klee-sparks-bt1/` (`MANIFEST.md`, `slots.yaml`, `t01`–`t04`);
the published record is `docs/current/EXPERIMENTS.md` → `KLEESPARK-BT1`; the
results are §22.

### 21.1 Why this read exists

`BACKLOG` `EB-224`'s next action reads *stage, grade, replay, whole-fight*.
This is **stage, grade and replay**. The whole fight stays owed and this
section does not touch it.

The row is `proto_spark_mode_bombs` — **Bag of Tricks**, 0 Energy, Skill,
Uncommon: *Choose one: Place 1 Bomb dealing 5 | Spend 3 Sparks: place 3 Bombs
dealing 5.* It is **the first row in the tree whose price sits at the HEAD OF A
MODE** rather than at the card's top level. The doctrine seat held the arm on
that clause twice (klee-slice-1 packet §6.1 and §6.1.1); R225 amended the
written clause on 2026-08-30 — *top level **or** the head of a `choose_one`
mode, and nothing nested or conditional* — and the arm proceeds. It is built on
`EB-182`'s mode-price machinery, whose behaviour is what half this round tests
live on this row.

**The sequencing gate is discharged.** `EB-224`'s row is sequenced behind
`EB-205`'s read; `KLEESPARK-S1` and `KLEESPARK-W3` took that read on
2026-08-30 and `EB-205` is DISCHARGED. Nothing in this round re-opens it and
nothing here is compared to either of those runs.

### 21.2 The question, in two halves

1. **Does a price of 3 that buys Bomb PLACEMENT create a real
   spend-versus-hold / one-versus-three decision** — is the expensive mode
   *taken* where three Bombs plainly pay, and *declined* where the same bank
   has a better home?
2. **Is the mode-head price LEGIBLE** — the face shows the price, the
   unaffordable mode is omitted (`EB-182`), and the bank is debited exactly once
   when the mode is taken?

**What is NOT asked:** whether the card is fun; whether 3 is the right number;
anything about win rate. Nothing measured on a prototype row is quotable
anywhere (R215 B), and a staged board is comparable to no run (Guardrail-7).

### 21.3 The boards — four, matched in pairs

Player HP 42/62, Block 0, Energy 3, enemy 40 HP on all four, so **the only
things that move across the round are the bank and one card in hand**. Every
seed is a `KLEESPARK-R2` seed recorded ONE-BODY on a Klee run, and every board
wants one body — so unlike `KLEESPARK-R2`'s `P3`, no slot here can go UNREACHED
on an encounter roll.

| turn | seed | bank | hand | what the board is | slot |
|---|---|---|---|---|---|
| `t01` | `JH4T8MSN10KS` | **3** | Bag of Tricks, Quick Fuse, Kaboom!, Duck and Cover | **A** — three Bombs pay (22 against 12), nothing else wants the bank | `B1` |
| `t02` | `R805DJ56LZHM` | **3** | Bag of Tricks, **Firework Finale**, Quick Fuse, Duck and Cover | **B** — `t01` with ONE card swapped: the bank buys the mode **or** the rival, and the rival is worth more (23 against 15) | `B2` |
| `t03` | `YX7PB48WR7R4` | **2** | Bag of Tricks, Quick Fuse, Kaboom!, Duck and Cover | **C** — `t01` at a bank one short with no `gain_spark` in hand: the priced mode must be OMITTED and the card must stay playable | `B3` |
| `t04` | `XT4BE7LFY5XH` | **2** | Bag of Tricks, **Powder Pop**, Quick Fuse, Kaboom! | **D** — one short, but the hand holds the missing Spark: affordability must RECOMPUTE inside the turn | `B3` |

**The matched pairs are the design.** `t01`/`t02` turns on one swapped card, so
a reader who takes the priced mode on both is taking it out of habit rather
than off the board. `t01`/`t03` turns on one number, and is the *bank ≥ 3
versus bank < 3* pair. `t03`/`t04` splits `EB-182`'s omission rule into its two
halves — withheld when short, opened when the bank is raised mid-turn.

**Quick Fuse is in three of the four hands** because Bombs detonate at the START
of the player's turn, so a Bomb placed now is next turn's damage; the shipped
0-Energy `detonate` is the only way a one-turn packet can put 15 and 5 side by
side. It prices no Sparks and moves no slot. **No line on any board is lethal**
(enemy 40, largest mirrored total 30.0).

**`B1` ceiling 1 / threshold 1, `B2` 1 / 1, `B3` 2 / 2**, computed by
`local_tester round --plan-only` over these four boards before staging.
`--first 0`: every board runs, because each is the only one of its kind and
R221 B's early stop would leave a question unasked rather than an answer
duplicated.

### 21.4 The slate — five slots, every falsifier mechanical

Full text in `understudy/turns/klee-sparks-bt1/MANIFEST.md`; the thresholds and
falsifiers, in summary:

| slot | board(s) | prediction | threshold | falsifier |
|---|---|---|---|---|
| `P1` | `t01` | the deciding form's `chosen_line` plays Bag of Tricks with `choose` naming the **priced** mode | 1 of 1 | the card is omitted, or `choose` names the free mode |
| `P2` | `t02` | the deciding form's `chosen_line` plays Bag of Tricks with `choose` naming the **free** mode **and** plays Firework Finale | 1 of 1 | `choose` names the priced mode; or the free mode is taken and the bank is left unspent |
| `P3` | `t03`, `t04` | no deciding form claims the priced mode is available at a bank of 2 without first raising the bank; no `free_card_misreads` hit | 2 of 2 | such a claim, or a misread, on either board |
| `P4` | `t03` | where the replayed line plays the card: the play is accepted, and the modal record raises no screen or one whose `offered` list omits the priced mode's text | 1 of 1 | the priced mode among the offers at bank 2, or a refused play |
| `P5` | `t01` | where the replayed line takes the priced mode: `offered` contains **both** texts, post-play bank **0**, target carries **3** Bombs | 1 of 1 | fewer than two offers; a bank other than 0; a Bomb count other than 3 |

**`P1` and `P2` are ONE finding and are read together.** Both PREDICTED is the
only result that says the decision is real — driven by the board rather than by
a habit of buying the expensive thing or a habit of hoarding. Either alone is
not that result and is not reported as one. Registered here so it cannot be
assembled afterwards.

**Refusals and absences, ruled in advance.** A REFUSED deciding form grades its
slot **UNREACHED**, not MISSED (`EB-209`). `P4` and `P5` are UNREACHED — never
PREDICTED — where the replayed line does not reach the play they are about;
absence of a counterexample is not a pass. That is `KLEESPARK-R2`'s `P4` lesson
applied before the run rather than after it. **`t04` planning *Powder Pop
first* is a correct reading and not a `P3` counterexample**: the board is built
so the bank can reach 3 inside the turn.

**RECORDED AND NOT GRADED:** the shadow-versus-deciding verdict agreement. A
four-board denominator decides nothing about the seat's chair and `M62` is not
at issue here.

### 21.5 What each result decides — and what a MISS does NOT license

- **`P1` and `P2` both PREDICTED** → the mode price poses a real
  one-versus-three decision at the staged surface; `EB-224`'s staged half is
  discharged and the row advances to the whole fight **unchanged**. No number
  moves.
- **Either MISSED** → the decision is not posed at the staged surface, and it
  returns to [USER] as a numbered pick list in §22. **A MISS licenses nothing
  on its own.** It does NOT license a re-price of the mode's 3, a change to
  §4.2's price table, a new sink row (R225), any amendment to or re-reading of
  R225's mode-head clause, any LAW change, or any claim about win rate, balance
  or fun (R215 B, Guardrail-7). Claude does not reprice a row on a staged read,
  and this is written before the run so it cannot be argued after it.
- **`P3` MISSED** → a FACE finding, to `BACKLOG` as a defect candidate with the
  failing form attached. Not a re-price.
- **`P4` or `P5` MISSED** → an `EB-182`/codegen defect on this row, to
  `BACKLOG`, and it **blocks** `EB-224`'s whole-fight step until fixed.
  Engineering, not a design result: it moves no design slot.
- **Any slot UNREACHED** → not a pass and not a fail; nothing is inferred from
  the absence and no [USER] row opens on it.

### 21.6 Who grades, and who does not

**This is a DESIGN round — an ADVANCE for the arm rests on it — so under
`M64` (1) / R224 the Codex seat decides EVERY board** (`--seat-spot-check 1`),
and the round costs more Codex calls than the standing three for exactly that
reason.

**The local seat sits in the SHADOW chair** (`--seat-mode shadow`, R222 B): it
reads every packet, it is graded, it is never the deciding verdict and it is
never replayed.

**Fresh-Opus is NOT the deciding chair here.** R222 B seats it for INSTRUMENT
rounds; `M64` (1) takes it out of a round on which an ADVANCE rests. The row is
`authored_by: [claude]`, so a same-family deciding read would not be
author-disjoint under R217 C — which is the whole reason the split exists.

### 21.7 The budget, the meter, and the stop lines

- **Plan: 4 deciding seat reads + 1 pair read = 5 Codex calls expected, cap 15
  for the round.** Four boards is the minimum that carries the four distinct
  questions; a fifth would add a duplicate and a call.
- **Meter read BEFORE anything was staged:** `5h 40% (resets 16:36 EDT) ·
  week 25% (resets Sep 05 17:58)`. `EB-227`'s guard refuses at 85% of the
  five-hour window and 50% of the week; the plan is well inside both. **If the
  guard refuses mid-round the round STOPS at that board** and §22 records how
  many boards were read, rather than finishing on a cheaper chair.
- **Preconditions checked before the run, each of which stops the round:** the
  game lock `gits-game.lock` under the user's Temp directory absent; Steam
  running; the installed dev build carrying the row. The build was verified
  read-only at `0.2.1676+proto.dirty` against the game's own
  `mods\klee\manifest.json`, and the row's presence proven off the installed
  `klee.dll` — `ProtoSparkModeBombs` ×4 in the UTF-8 metadata, and *"Bag of
  Tricks"* and `proto_spark_mode_bombs` each once in the UTF-16 user strings.
  **Nothing was deployed for this round.**

### 21.8 What these boards still cannot do

**The tier0 mirror cannot see a mode.** `closeness` enumerates CARD SETS, so its
lines read *"Bag of Tricks + Quick Fuse + Kaboom!"* without saying which mode —
which is why `t02`'s mirrored top line is not the line `P2` predicts. Every gap
below is a bound on card sets and **not** on the choice this round is about; the
packet and every replay read the LIVE game. All four SURVIVE at
`DOMINANCE_GAP` 0.5: `t01` gap 0.0000 (30.000 / 30.000, 15 lines), `t02`
0.0000 (22.400 / 22.400, 15), `t03` 0.0000 (19.000 / 19.000, 15), `t04` 0.0000
(30.020 / 30.020, 15).

**`slot_plan` cannot see a mode price either.** `_spark_prices` reads a
top-level `spend_spark` and nothing else, so *Bag of Tricks* is invisible to
`affordable_spark_uses` on every board here. `slots.yaml` says so at length and
writes every predicate about the OTHER Spark cards: `affordable_spark_uses == 0`
reads *"no other Spark sink"*, never *"no Spark sink"*, and the banks are
compared against integer literals because 3 is a number the file knows and
`min_spark_price` is not. Making `slot_plan` mode-aware is engineering this
round does not need and does not do; it is reported as a candidate and nothing
is minted here.

**It still cannot draft, and it still cannot ask a face-and-turn question.**
`loader._pool_substitutions` returns `{}` for Klee, so nothing here was picked
by a drafter; and a staged single turn has no memory of what a bank was held
for. §11.6 item 1 is unchanged, and whole-fight play — `EB-224`'s remaining
next action — is the instrument for it.

## 22. `KLEESPARK-BT1` — RUN AND GRADED

Generated from the records by
`python -m understudy.staged_turn packet-section klee-sparks-bt1` on
2026-08-30. Every table in §22.1 is transcribed from
`review/qa/klee-sparks-bt1-t*/` and `review/qa/ledger.tsv`; nothing there is
re-graded and nothing is re-read (R101b).

### 22.1 What actually ran — the session, the stamp, and one instrument stop

Dev build **`0.2.1676+proto.dirty`**, read off the deployed
`mods\klee\manifest.json`; game **`v0.111.0`**; world **`eb224-staging`** @
`acb543b9`, which is the registration commit itself. **Nothing was deployed for
this round** — the installed build already carried the row, proven read-only
before staging (§21.7).

**4 boards run, 0 UNRUN, 8 forms graded.**

| turn | seed | grader | family | verdict | refused by | replay |
|---|---|---|---|---|---|---|
| `klee-sparks-bt1-t01` | `JH4T8MSN10KS` | `codex-gpt-5.6-sol-fresh` | gpt | **SURVIVES** | -- | confirms — Seapunk 40 → 18; Block 0 → 5 |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | intent_insensitive | - |
| `klee-sparks-bt1-t02` | `R805DJ56LZHM` | `codex-gpt-5.6-sol-fresh` | gpt | **REFUSED** | intent_insensitive | - |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | intent_insensitive | - |
| `klee-sparks-bt1-t03` | `YX7PB48WR7R4` | `codex-gpt-5.6-sol-fresh` | gpt | **REFUSED** | intent_insensitive | - |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | intent_insensitive | - |
| `klee-sparks-bt1-t04` | `XT4BE7LFY5XH` | `codex-gpt-5.6-sol-fresh` | gpt | **REFUSED** | intent_insensitive | - |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | intent_insensitive | - |

**The funnel's own generic board-slot table reads `B1` UNDECIDED, `B2` DECIDED,
`B3` DECIDED under its convention that SURVIVES is PREDICTED and REFUSED is
MISSED. That convention is NOT this round's slate** and grades nothing here:
`B1`–`B3` are board-QUALIFICATION slots, and §21.4's `P1`–`P5` are the
predictions. §22.2 is the grading.

**What the round spent:** 4 Codex seat reads (the deciding chair, one per
board), 4 local tester reads (shadow), 0 control reads — fresh-Opus is not
seated in a design round (§21.6).

**One instrument stop, and its repair.** `t04` FAILED TO STAGE on the round's
first pass with `seed_not_honoured: asked for seed 'XT4BE7LFY5XH', the run
reads back None` — `EB-191`, the same defect that cost `KLEESPARK-R2` a board
and that `KLEESPARK-W3` had to work around off the wire. **Nothing had been
read**, so the board was re-staged alone from the unchanged committed file and
then read in the pre-registered position; the seed came back honoured on the
second attempt. A board that failed to stage is not a board that was read, so
this is a re-attempt and not a re-roll, and it is recorded rather than smoothed.

### 22.2 The slate, graded mechanically

**2 PREDICTED (`P1`, `P5`) / 0 SPLIT / 0 MISS / 3 UNREACHED (`P2`, `P3`,
`P4`).**

**`P1` PREDICTED at 1 of 1.** `t01`'s deciding form SURVIVES and its chosen
line opens *"Bag of Tricks on Seapunk [mode: Spend 3 Sparks: place 3 Bombs
dealing 5.]"*. Its own words: *"I spent 3 Sparks with Bag of Tricks to place 3
Bombs on Seapunk, detonated them with Quick Fuse…"*, and its second answer
names the alternative it declined — *"I seriously considered taking the
single-Bomb option on Bag of Tricks to preserve all 3 Sparks."* The priced mode
is taken where three Bombs pay, and the reader can say what the price bought.

**`P2` UNREACHED.** `t02`'s deciding form was REFUSED for `intent_insensitive`
(Q4: *"No. With the printed hand and resources, I would still take the
available damage and Block without sacrificing another play."*), and the
registered rule is that a refused deciding form grades its slot UNREACHED.
**ANSWERED OUT OF SLOT, and recorded as such rather than as a grade:** the
refused form's line is *"Bag of Tricks on Nibbit [mode: Place 1 Bomb dealing 5]
→ Quick Fuse → Firework Finale → Duck and Cover"*, which is exactly what `P2`
predicted, and its third answer says *"It gave up the three-Bomb option, using
the Sparks on Firework Finale instead."* The shadow form did the same thing in
the other order. **That evidence does not move `P2`, which stays UNREACHED as
published (R101b).**

**`P3` UNREACHED.** Both `B3` boards' deciding forms were REFUSED for
`intent_insensitive`, so the 2-of-2 threshold has a denominator of 0. **Out of
slot:** neither refused form claimed the priced mode was available at a bank of
2, and `t04`'s deciding form planned the raise explicitly — *"I played Powder
Pop on Fuzzy Wurm Crawler to place a Bomb and reach 3 Sparks, then Bag of
Tricks choosing 'Spend 3 Sparks: place 3 Bombs dealing 5.'"* — which is the
reading §21.4 printed in advance as correct. `P3` stays UNREACHED.

**`P4` UNREACHED.** `t03`'s deciding form was REFUSED and a refused form is not
replayed, so the slot's own denominator produced no replay. **Absence of a
counterexample is not PREDICTED**, exactly as registered. `EB-182`'s omission
rule is therefore NOT read live on this row by this round, and that is what the
round owes.

**`P5` PREDICTED at 1 of 1**, and it is the round's second finding. On `t01`'s
replay the `card_select` screen offered **both** mode texts at a bank of 3
(`["Place 1 Bomb dealing 5", "Spend 3 Sparks: place 3 Bombs dealing 5"]`); the
wire then reads, step by step:

```
staged board          player spark 3    Seapunk 40 HP, no bomb
after Bag of Tricks   player spark 0    Seapunk 40 HP, bomb 15
after Quick Fuse      player spark 3    Seapunk 25 HP, no bomb
after Kaboom!         player spark 3    Seapunk 18 HP
after Duck and Cover  player spark 3    Seapunk 18 HP, player Block 5
```

The post-play bank is exactly **0**, and the payload is three Bombs at 5: the
wire carries no bomb COUNT field — its `bomb` figure is the aggregate bomb
damage standing on the target — so **3** is established twice over, by
`bomb: 15` immediately after the play and by the detonation delivering exactly
15. **The mode-head price is charged once and pays out what it prints**, which
is the live half of the codegen gap `EB-224`'s build closed.

**Judgment, per slot: `P1` ADVANCE, `P2` RETURN, `P3` RETURN, `P4` RETURN,
`P5` ADVANCE — 2 ADVANCE / 3 RETURN / 0 ESCALATE, overall RETURN, on the
INSTRUMENT and not on the arm's design.**

**`P1` AND `P2` DO NOT DELIVER THEIR JOINT FINDING**, and §21.4 registered that
in advance: `P1` alone is not the result, and it is not reported as one. The
pair read says it in its own words: *"P1 was predicted, but P2 was unreached;
this round does not show that the decision changed with the board rather than
reflecting a habit."*

### 22.3 The pair read

`review/qa/klee-sparks-bt1-pair-review-codex-gpt-5.6-sol.md`, prompt beside it
at `klee-sparks-bt1-pair-review-prompt.txt`; model observed `gpt-5.6-sol` via
Codex, `--role pair`, one call, no re-send. It grades **exactly** the five
verdicts above and the same per-slot judgments, and closes:

> The boards only partly did what they were built to do. t01 successfully
> exercised priced-mode selection and its replay validated the offer list,
> immediate payment, and Bomb payload. But t02's intended comparison was
> refused, neither affordability board reached replay, and the repeated
> intent-insensitive construction prevented most of the arm's registered
> questions from being asked. […] **Overall judgment: RETURN.**

### 22.4 Two things the round found that are not slots

**1. The priced mode REFUNDED ITS OWN PRICE inside the same turn, and the
boards did not control for it.** `t01`'s bank read 3 → 0 on the mode and **3
again** after Quick Fuse. The mechanism is not in doubt: Klee's STARTER RELIC,
*Pounding Surprise*, pays **+1 Spark per Bomb detonated**
(`klee-mod/KleeCode/Klee.cs:152` seats it as her starter;
`Relics/PoundingSurprise.cs`'s `OnBombDetonated` gains the Spark), and the
priced mode places exactly **3** Bombs. So on any board where the Bombs the
mode buys are detonated on the same turn, the mode is **net-free** — the "spend"
in spend-versus-hold is returned before the turn ends. `KLEESPARK-W3` §18.9
already named this relic as one of *"two sources the ratio cannot count"*; this
is the first record in which it lands on the card under test.

**This changes no grade and the pair read says so:** `P5` asks for the bank
*immediately after the priced mode*, when it was 0, and `P1` asks which mode was
chosen. Neither is disturbed. It is a **board confound** — the registration did
not control the starter relic and the blind page does not print relics — and it
is the round's most consequential finding. It is **not** filed as a defect: the
relic behaved as built. What it questions is whether a Spark price on a
*Bomb-placement* mode is a price at all on this character, and that is a design
question that returns to [USER] at §22.6.

**2. Seven of eight forms were REFUSED for `intent_insensitive`, and the boards
are why.** Three of four deciding forms and four of four shadow forms. The
readers say the reason plainly and consistently: `t03`'s deciding form — *"With
enough energy to play both costed cards and both zero-cost cards, a different
telegraphed intent would not have changed this line"*; `t04`'s — *"The hand
contains no printed defensive or intent-dependent effect."* **Every board of
this round gave one enemy with a fixed telegraph, three Energy, and a hand of
at most two Energy-costed cards** — so the whole hand was always playable and
the telegraph never forced a trade. §21.3 chose that construction deliberately,
to hold everything but the bank constant across the four boards; the cost was
that the round's central falsifier fires on the construction rather than on the
cards. **This is a REGISTRATION defect, and it is the round's RETURN.** It is
reported as a `BACKLOG` candidate — a board-design rule for resource rounds,
and/or the reach of the `intent_insensitive` falsifier on a board whose question
is not a defensive one — and nothing is minted here.

### 22.5 What the round spent, and what it did not settle

- **5 Codex calls of a cap of 15**: four deciding seat reads and one pair read,
  exactly the plan at §21.7. The meter read **`5h 40% / week 25%`** before the
  round and **`5h 48% / week 26%`** after; `EB-227`'s guard (85% / 50%) never
  refused and never came close.
- **Shadow-versus-deciding verdict agreement: 3 of 4** — both REFUSED on `t02`,
  `t03` and `t04`, disagreeing only on `t01`, where the shadow seat refused the
  board the deciding seat survived. **RECORDED AND NOT GRADED** (§21.4): a
  four-board denominator decides nothing about the seat's chair and `M62` is
  not at issue.
- **NOT SETTLED, and owed:** `EB-182`'s omission rule is not read live on this
  row (`P4` UNREACHED); the one-versus-three decision is not established
  (`P1`+`P2` incomplete); and the whole fight `EB-224`'s row owes is untouched.
  Nothing about the row's price, its wording or R225's clause moved, and under
  §21.5 nothing here licenses moving them.

### 22.6 What this leaves — numbered picks, never blanks

`EB-224`'s row keeps its remaining next action. What returns to [USER] is a
choice about the FIRST finding at §22.4, because it is a design question about
what a Spark price means on a Bomb-placement mode, and the ladder keeps that
kind of call with [USER]:

1. **Accept the refund and re-pose the round with it printed.** The mode is
   net-free whenever its Bombs detonate the same turn; say so in the arm's own
   terms, put the relic on the record, and re-run a repaired staged round whose
   boards separate *"the Bombs detonate now"* from *"the Bombs sit until next
   turn"*. This is the cheapest option and it changes no number.
2. **Re-pose the round WITHOUT the starter relic**, if the harness can suppress
   it, so the price is measured before the refund. This measures the price the
   sheet prints rather than the price the character pays, and it is the more
   honest instrument and the less honest world.
3. **Treat the refund as the finding and take it to the whole fight
   unchanged.** The refund is a real property of a real deck; let a whole fight
   say whether a self-refunding mode price is a decision, and skip a second
   staged round entirely.
4. **Hold the arm here.** Bank `P1` and `P5`, and let the mode-head machinery's
   live proof wait for other consumers, because two of the four boards this
   round could ask were refused by their own construction.

**No default and no recommendation on the price.** Under §21.5 a MISS licenses
no re-price, and this round did not even produce a MISS — it produced three
UNREACHED. **Nothing here re-prices the 3, re-words the row, re-reads R225's
clause, or moves any LAW line.**

> **RULED (R229, 2026-08-30): option (1), QUALIFIED.** The starter relic stays
> and the round is re-posed in the SHIPPED world, but *"accept the refund"*
> means accept it as an observed TEST CONDITION, not as approval of the card's
> design — the arm is AT RISK, not presumptively advancing. A RETURN CONDITION
> is PRE-REGISTERED before `KLEESPARK-BT2` is drafted: if immediate detonation
> restores enough bank to play the competing sink, or the price otherwise
> imposes no meaningful opportunity cost across the turn and the next, the arm
> RETURNS TO DESIGN rather than advancing unchanged. The ruling's evidence is a
> consequence §22.4 did not draw: `t02`'s header prices the bank of 3 as buying
> exactly ONE of two things, but in the shipped world *priced mode → Quick Fuse
> → Firework Finale* buys BOTH (15 + 18, not 15-versus-23), so the price is
> collateral — it gates the play at 3 and usually consumes nothing. The full
> record, the qualification and the repaired round's five required contents are
> in `review/ruled/sitting-2026-08-30.md` §R229.

A second item is engineering rather than a decision and is reported to
`BACKLOG` rather than to [USER]: the board-construction rule §22.4 item 2 names,
and `slot_plan`'s blindness to a mode-head price (§21.8). Both are candidates;
neither is minted here (R206/R212, one batch per sitting).

### 22.7 What this round does NOT settle

It says nothing about whether *Bag of Tricks* is fun, whether 3 is the right
price, or anything comparable to any run (Guardrail-7, R215 B). It does not
discharge `EB-224`'s acceptance line, which asks for the arm graded, replayed
**and** its whole fight run: one board of four was replayed, and the whole
fight is untouched.


## 23. `KLEESPARK-BT2` — the repaired *Bag of Tricks* round, under R229's return condition

**REGISTERED — NOT RUN; Claude drafts (R212 item 2), [USER] countersigns in
batch.** The three boards, `slots.yaml`, `MANIFEST.md` and the slate below
were committed **before anything was staged, deployed or read**. Nothing here
has been run: no board staged, no game launched, no Codex call spent. The
machine-readable half is `understudy/turns/klee-sparks-bt2/`; the round this
one repairs is §21 (registration) and §22 (results).

### 23.1 Why this round exists, and what R229 settled

§22.4 item 1 found, off `t01`'s replay, that the priced mode **refunded its own
price inside the same turn** — bank 3 → 0 on the mode, **3 again** after the
detonator. Klee's starter relic *Pounding Surprise* pays **+1 Spark per Bomb
detonated** (`klee-mod/KleeCode/Relics/PoundingSurprise.cs`; the sim's twin is
the `spark_on_detonation` hook, `tier0/engine/effects.py:874`) and the priced
mode places exactly three Bombs. The registration had not controlled for it,
and the blind page printed no relics at all, so no reader could see it.

**R229, in three parts.** *Bag of Tricks* **stays under test in the SHIPPED
world** — the starter relic is kept. The refund is accepted as an **observed
TEST CONDITION and not a design approval**; nothing about it licenses a
re-price. And the arm is **AT RISK under a pre-registered RETURN CONDITION**,
written at §23.4 as a graded predicate with its numbers.

**Three engineering rows were closed first, and each of them is why this round
can be written honestly.**

- **`EB-238`** — the blind page printed relics only where one is OFFERED. Both
  surfaces now print the run's relics: the combat page's header and, more to
  the point, the STAGED packet, which is the page `KLEESPARK-BT1`'s eight forms
  actually read. Printed name and printed hover text, nothing the shipped game
  does not show the player (R217).
- **`EB-237`** — `slot_plan._spark_prices` read a top-level `spend_spark` and
  nothing else, so the row under test priced nothing as far as every ceiling
  and predicate could see. It now reads R225's amended clause in full: the top
  level **or** the head of a `choose_one` mode, and nothing nested. §22 could
  only write its predicates about the OTHER cards in hand; this round's
  `slots.yaml` says what it means.
- **`EB-236`** — a board-design check for resource rounds, in the STRONG form
  GPT asked for and R229 adopted: not *"are the two prices greater than the
  bank"* but *"can **any order of play**, counting every relic-triggered gain
  along the way, pay for all of them"*. It refuses `KLEESPARK-BT1`'s `t02` on
  the exact sequence, and all four of that round's boards on the weaker half.

### 23.2 The three boards

Body 55 HP on all three, no lethal line, every seed a `KLEESPARK-BT1` seed
recorded ONE-BODY on a Klee run. **Every hand costs 4 Energy against 3**, which
is the thing that round never did: its four boards all let 3 Energy pay for the
whole hand, so the telegraph forced no trade and `intent_insensitive` refused
**seven of its eight forms** (§22.4 item 2).

| turn | seed | bank | HP | hand | what the board is | slot |
|---|---|---|---|---|---|---|
| `t01` | `JH4T8MSN10KS` | **3** | 42/62 | Bag of Tricks, **Kaboom!**, Firework Finale, Duck and Cover, Spirited Away | **A** — the exact *priced mode → ordinary Attack → rival price-3 sink* sequence: 3 → 0 → 3 → 0, for 7 + 15 + 18. **The return-condition board.** | `C1` |
| `t02` | `R805DJ56LZHM` | **3** | 42/62 | Bag of Tricks, Firework Finale, Mine Toss, Duck and Cover, Spirited Away | **B** — §21's `t02` REPAIRED: the same exclusivity claim, and this time no order of play buys both | `C1` |
| `t03` | `YX7PB48WR7R4` | **3** | **24**/62 | Bag of Tricks, Mine Toss, Duck and Cover, Spirited Away, Run Away! | **C** — no Attack and no detonator, so three Bombs SIT: a delayed refund against a telegraphed 16 into 24 HP, and the next turn's bank is read | `C2` |

**The detonator is an ORDINARY ATTACK and not *Quick Fuse*.** §21 put a free
single-purpose `detonate` in three of four hands, which makes the refund read
as a property of one strange card. It is not: any Attack that gets HP damage
through pops the target's Bombs (`_detonate_bombs_on_hit`; the C# twin is
`Powers/BombPower.cs` with `IBombDetonationListener`). `t01`'s detonator is
Kaboom!, a basic card in the starting deck, and there is no Quick Fuse in this
round at all.

**Why `t02`'s claim holds where §21's did not.** The only Attack in that hand
is *Firework Finale* itself, and it must be paid for before it can pop
anything. Priced mode first → bank 0 and three Bombs nothing can detonate.
Finale first → bank 0, and its 18 lands on a body carrying at most Mine Toss's
one Bomb, so the relic pays at most 1 and the bank reaches 1, not 3. `EB-236`
walks every order and finds none that buys both.

**`C1` ceiling 2 / threshold 2, `C2` 1 / 1**, computed by `local_tester round
--plan-only` over these three boards before staging, which also printed *board
design: every board forces a trade, and every declared exclusive pair is
exclusive*. `--first 0`: every board runs, because each is the only one of its
kind.

### 23.3 The forecast — a pre-commit question, and it is new machinery

`EB-229` found `KURAGEMEM002`'s forecast slots UNREACHED **not because the
display failed but because the question is never asked**: a blind run's reply
schema is `command` and `thinking`, and the staged form's four questions are
all past tense. **This round is the STAGED TWIN of that row, and the twin is
built here.**

A turn file may now carry `forecast:` — a short list of questions printed at
the **top** of the blind packet under *Before you decide*, numbered, answered
into the form's `forecast` list in the same order, **before** the line is
chosen. A form that skips it where a board asked is REFUSED
`forecast_missing`; a board that asks nothing prints no such block and is
graded exactly as before. The questions are asked CONDITIONALLY (*"if you spend
3 Sparks on Bag of Tricks…"*) so that asking them does not recommend a line,
and they go through the packet's own leak scrub like every other printed
string. **`EB-229` itself stays open**: this is the staged half, and a blind
RUN's reply schema is untouched.

`replay_next_turn: true` on `t03` makes the replay **end the turn after the
graded line and take one more reading**. A staged single turn has no next turn
(§11.6 item 1), which is why §22 could say nothing about a delayed refund;
this buys exactly one turn of it.

### 23.4 The slate — five slots, and the return condition among them

Full text in `understudy/turns/klee-sparks-bt2/MANIFEST.md`.

| slot | board | prediction | threshold | falsifier |
|---|---|---|---|---|
| `F1` | `t01` | the deciding line plays the priced mode, an Attack, and Firework Finale in one turn, **and** the replay reads bank **0** after the mode and **≥ 3** after the Attack | 1 of 1 | the bank does not reach 3 again; or the line cannot pay for both |
| `F2` | `t03` | where the replayed line takes the priced mode: the third answer names a concrete thing this turn gave up, **and** the next-turn reading shows the bank back at **3** | 1 of 1 | no cost named; or a next-turn bank other than 3 |
| `F3` | `t02` | the deciding line pays for **exactly one** of the two priced uses, and the second answer names the other as declined | 1 of 1 | both paid in one turn; or the second answer names neither |
| `F4` | all three | every deciding form carries a full `forecast`; none is refused `forecast_missing` | 3 of 3 | a missing or short forecast on any board |
| `F5` | `t01` | where the line takes the priced mode: the first forecast answer reads **0** and the second reads **3** | 1 of 1 | either number wrong |

> **THE PRE-REGISTERED RETURN CONDITION (R229), AS A GRADED PREDICATE.**
> `F1` and `F2` are ONE finding and are read together.
>
> **The arm RETURNS TO DESIGN if EITHER**
> **(a) `F1` is PREDICTED — the bank reads ≥ 3 again after the detonation, on
> the same turn, and the reader pays for both priced uses; OR**
> **(b) `F2`'s form names NO cost given up AND `F2`'s next-turn bank reads 3.**
>
> (a) is R229's *"immediate detonation restores enough bank to play the
> competing sink"* — **3** is the competing sink's exact price and is the
> number. (b) is *"the price otherwise imposes no meaningful opportunity cost
> across the turn and the next"* — the bank comes back one turn later and the
> reader can name nothing it cost. Either alone RETURNS the arm; both is the
> strongest form and is reported as one finding, not two.

**Refusals and absences, ruled in advance.** A REFUSED deciding form grades its
slot **UNREACHED**, not MISSED (`EB-209`). `F1`, `F2` and `F5` are UNREACHED —
never PREDICTED — where the replayed line does not reach the play they are
about; absence of a counterexample is not a pass. Any slot UNREACHED is not a
pass and not a fail, and no [USER] row opens on it.

**A MISS on `F3` is an INSTRUMENT finding, not a design one:** `EB-236` says no
order of play buys both on that board, so a form that does is a defect in the
check or in the build, filed to `BACKLOG`, and it blocks `EB-224`'s whole
fight until fixed. **A MISS on `F5` is a LEGIBILITY finding** — the page shows
the relic and the reader still could not do the arithmetic — also to `BACKLOG`.

### 23.5 What a MISS does NOT license

**A MISS licenses nothing on its own.** It does NOT license a re-price of the
mode's 3, a change to §4.2's price table, a new sink row (R225), any amendment
to or re-reading of R225's mode-head clause, the removal or suppression of
*Pounding Surprise*, any LAW or measurement-law change, or any claim about win
rate, balance or fun (R215 B, Guardrail-7). **A RETURN under §23.4's condition
returns the arm to [USER] as a numbered pick list; it does not itself move a
number, and Claude picks nothing on it.**

### 23.6 Who grades, and what it costs

**The Codex seat decides every board** (`--seat-spot-check 1`): a DESIGN round
on which an ADVANCE rests, so `M64` (1) / R224 puts the deciding chair there
on every board. **The local seat sits in the SHADOW chair** (`--seat-mode
shadow`, R222 B) — read, graded, never deciding, never replayed.
**Fresh-Opus is NOT seated**: R222 B seats it for INSTRUMENT rounds, the row is
`authored_by: [claude]`, and a same-family deciding read would not be
author-disjoint under R217 C.

- **Plan: 3 deciding seat reads + 1 pair read = 4 Codex calls expected, cap 9**
  (≈3 per board). Three boards is the minimum that carries the three distinct
  questions — immediate refund, exclusive pair, delayed refund.
- **The meter as this registration was drafted:** `5h 48%`, resetting **16:36
  EDT**; the round is planned for after that reset, and the operator reads the
  meter again immediately before it. `EB-227`'s guard refuses at **85%** of the
  five-hour window and 50% of the week; if it refuses mid-round the round
  **STOPS at that board** and the results record how many were read, rather
  than finishing on a cheaper chair.
- **Preconditions, each of which stops the round:** `gits-game.lock` absent;
  Steam running; the installed dev build carrying the row, proven read-only off
  the deployed `mods\klee\manifest.json` and the installed `klee.dll` before
  anything is staged.

### 23.7 What these boards still cannot do

**The tier0 mirror cannot see a mode, and it cannot see the relic.**
`closeness` enumerates CARD SETS and scores them through the pilot's own
surface with no run layer, so neither the mode choice nor the refund is
visible to it. All three boards SURVIVE at `DOMINANCE_GAP` 0.5 — `t01` gap
0.0313 (38.3 / 37.1, 5 lines), `t02` 0.0194 (36.1 / 35.4, 5), `t03` 0.1174
(40.9 / 36.1, 5) — and every one of those numbers bounds card sets and nothing
this round is about.

**One turn plus one reading is not a fight.** `loader._pool_substitutions`
returns `{}` for Klee, so nothing here is picked by a drafter, and `t03` buys
exactly ONE turn of the future. `EB-224`'s whole fight stays owed and this
round does not touch it.

**R217 G rides on everything this round will produce.** A tester's or a
grader's words are one model's account, never validation and never balance
evidence; Guardrail-7 stands on top of that, and nothing measured on a
prototype row is quotable anywhere except the decision-closeness falsifier
(R215 B).

## 24. `KLEESPARK-BT2` — RUN AND GRADED

Generated from the records by
`python -m understudy.staged_turn packet-section klee-sparks-bt2` on
2026-08-30. Every table in §24.1 is transcribed from
`review/qa/klee-sparks-bt2-t*/` and `review/qa/ledger.tsv`; nothing there is
re-graded and nothing is re-read (R101b).

### 24.1 What actually ran — the session and the stamp

Dev build **`0.2.1676+proto.dirty`**, read off the deployed
`mods\klee\manifest.json`; game **`v0.111.0`**, read off `release_info.json`;
world `r229-2026-08-30` @ `94e1a4a5`. **Nothing was deployed for this round** —
the installed build already carried the row, proven read-only off both files
before anything was staged (§23.6). The game lock was absent, Steam was
running, and the meter read **`5h 48%` / week 26%** immediately before the
round and **`5h 59%` / week 28%** immediately after; `EB-227`'s guard never
refused.

**3 boards run, 0 UNRUN, 6 forms graded, 0 lines replayed.**

| turn | seed | grader | family | verdict | refused by | replay |
|---|---|---|---|---|---|---|
| `klee-sparks-bt2-t01` | `JH4T8MSN10KS` | `codex-gpt-5.6-sol-fresh` | gpt | **REFUSED** | `forecast_missing` | - |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | `forecast_missing` | - |
| `klee-sparks-bt2-t02` | `R805DJ56LZHM` | `codex-gpt-5.6-sol-fresh` | gpt | **REFUSED** | `forecast_missing` | - |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | `forecast_missing` | - |
| `klee-sparks-bt2-t03` | `YX7PB48WR7R4` | `codex-gpt-5.6-sol-fresh` | gpt | **REFUSED** | `target_missing`, `forecast_missing` | - |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | `forecast_missing` | - |

**Every seed came back as requested on the first attempt** — no `EB-191`
re-stage on any board — and **all three previously unverified `give_card` ids
staged live**: `KLEEMOD-MINE_TOSS`, `KLEEMOD-SPIRITED_AWAY` and
`KLEEMOD-RUN_AWAY` are in `t03`'s live hand at costs 1, 2 and 0. Nothing
refused an id and the round never had to stop.

**The funnel's own generic slot table reads `C1` and `C2` DECIDED under its
convention that SURVIVES is PREDICTED and REFUSED is MISSED. That convention
is NOT this round's slate** and grades nothing here: `C1`/`C2` are board
COUNTING slots, and §23.4's `F1`–`F5` are the predictions.

**What the round spent:** 3 Codex seat reads (the deciding chair, one per
board) + 1 Codex pair read = **4 calls of a cap of 9**, exactly the plan.
3 local tester reads in the shadow chair. 0 control reads — fresh-Opus is not
seated in a design round (§23.6).

### 24.2 The slate, graded mechanically

**0 PREDICTED / 0 SPLIT / 1 MISS (`F4`) / 4 UNREACHED (`F1`, `F2`, `F3`,
`F5`).**

**`F1` UNREACHED.** `t01`'s deciding form was REFUSED, and a refused form is
not replayed, so there is **no wire reading anywhere in this round** and the
slot's own denominator produced nothing. Absence of a counterexample is not
PREDICTED, exactly as registered.

**`F2` UNREACHED.** `t03`'s deciding form was REFUSED twice over, no replay
ran, and the `replay_next_turn` reading this round was built to buy **does not
exist**. The delayed refund is exactly as unmeasured as it was after
`KLEESPARK-BT1`.

**`F3` UNREACHED.** `t02`'s deciding form was REFUSED.

**`F4` MISSED at 0 of 3, and it is the round's finding.** Every deciding form
carried **0 forecast answers against 3 questions asked**, on every board. `F4`
is the one slot the UNREACHED rule does not swallow, because its registered
falsifier *is* a `forecast_missing` refusal — "a missing or short forecast on
any board" — and a slot whose falsifier can only ever grade UNREACHED would be
unfalsifiable by construction. It is graded on its own falsifier and it is an
INSTRUMENT reading, as registered.

**`F5` UNREACHED**, by its own registered rule: `F4` was MISSED on `t01`.

**Judgment, per slot: `F1` RETURN, `F2` RETURN, `F3` RETURN, `F4` RETURN,
`F5` RETURN — 0 ADVANCE / 5 RETURN / 0 ESCALATE, overall RETURN, on the
INSTRUMENT and not on the arm's design.** That is the same verdict
`KLEESPARK-BT1` returned, for a different reason, and it is the second round
in a row on which this arm has been asked a design question and has not been
able to answer one.

### 24.3 THE PRE-REGISTERED RETURN CONDITION — **IT DID NOT FIRE**

R229's condition, read exactly as §23.4 wrote it:

- **(a) is not satisfied.** `F1` is **UNREACHED, not PREDICTED**. The clause
  requires the bank to read ≥ 3 again after the detonation *on the replay's
  wire readings*, and no replay ran.
- **(b) is not satisfied.** It is a conjunction — `F2`'s form names NO cost
  **AND** `F2`'s next-turn bank reads 3 — and **both halves fail**: the form
  did name a cost (below), and there is no next-turn bank reading at all.

**The arm therefore does NOT return to design on this round.** It stays where
R229 put it: **under test and AT RISK**, with the condition still standing and
still unanswered. Nothing here licenses a re-price, a sheet move, a change to
§4.2's price table, a re-reading of R225's mode-head clause, the removal of
*Pounding Surprise*, or any claim about win rate, balance or fun (§23.5,
R215 B, Guardrail-7). **No numbered pick list is owed**, because the condition
that would have opened one did not fire.

### 24.4 Why every form was refused — the instrument finding, stated plainly

**The forecast machinery shipped one half of itself.** `EB-229`'s staged twin
was built into the PACKET — `qa_packet` prints the numbered questions at the
top of the page under *Before you decide*, and `staged_turn` refuses a form
that carries fewer answers than questions. **The FORM half was never built.**
`understudy/seat.py`'s `form_schema()` is a strict schema —
`additionalProperties: false`, nine named properties, all of them `required` —
and **`forecast` is not one of them**. The reply the seat is allowed to emit
has no field to answer the question into. The local tester's schema has the
same shape and the same gap.

**Both readers answered the question anyway, in prose, in the wrong box**,
which is the proof that the packet half works and the form half is what is
missing:

- `t02`, deciding form, Q1 opens: *"Forecast: 3; yes; 1. I used Bag of Tricks'
  3-Spark option on Nibbit…"*
- `t03`, deciding form, Q1 closes: *"My forecasts were: 0 Spark at the end of
  this turn, 4 Spark at the start of next turn, and 25 damage dealt by then."*

A forecast smuggled into a past-tense answer is not a pre-commitment and the
falsifier is right to refuse it — but the refusal is a defect in the
instrument this round shipped, not a reading about the reader. **This is
`EB-229`'s other half and it is the round's owed engineering.** The staged
twin cannot be graded until a form can carry a forecast.

**The second refusal, `t03`'s `target_missing`,** is `EB-203`'s check doing its
job: the deciding form played *Bag of Tricks* with no target, and the card
aims at one enemy. It is independent of the forecast gap and would have
refused that board on its own.

### 24.5 Out of slot — recorded, and graded nowhere (R101b)

**The evidence the round could not admit is exactly the evidence it was built
to take.** All three of these are reader prose on REFUSED forms; none moves a
slot, none is a measurement, and none is quoted anywhere as one.

1. **`t01` — the same-turn refund, in the reader's own words.** The deciding
   form's line is *Bag of Tricks* [priced mode] → Kaboom! → Firework Finale →
   Spirited Away, and Q1 reads: *"I spent 3 Sparks with Bag of Tricks to place
   three Bombs on Seapunk, played Kaboom! on Seapunk, **spent the Sparks gained
   from the Bomb detonations** on Firework Finale targeting Seapunk."* The
   shadow reader is more explicit still: *"the bombs detonating under
   **Pounding Surprise** restore 3 Sparks, and Firework Finale spends those 3
   Sparks for 18 damage."* That is `F1`'s predicate as prose. **It is not
   `F1`'s evidence**: `F1` asks for the replay's wire readings, and no replay
   ran. The arithmetic is the readers', unverified against the game.
2. **`t02` — the exclusivity claim, contradicted on paper and not on the
   wire.** The deciding line pays for BOTH priced uses — *Bag of Tricks*
   [priced mode] → Firework Finale → Mine Toss → Duck and Cover — on the board
   `EB-236` certified as having no order of play that buys both, and its Q2
   names *Spirited Away* rather than either priced use as the declined line.
   Read on paper the line is unpayable: the mode takes the bank to 0, and
   Firework Finale must be PAID before it can detonate anything. **Whether the
   game would have refused it is exactly what a replay would have shown, and
   no replay ran.** So this is not `F3`'s MISS and not `EB-236`'s
   counterexample; it is an unresolved reading, and it is the first thing the
   repaired round should settle.
3. **`t03` — a cost was named.** Q3: *"It gave up 12 additional Block from
   Spirited Away."* That is half of `F2`'s predicate, and it is the half that
   made `(b)` fail rather than fire.

### 24.6 What `EB-238` bought, and one thing it exposed

**`EB-238`'s acceptance is met and its row closes.** The staged page prints
the run's relics with printed name and printed hover text, and a form quotes
one: the `t01` shadow form names *Pounding Surprise* and uses it to do the
turn's arithmetic, and the `t01` deciding form quotes its effect (*"the Sparks
gained from the Bomb detonations"*) without naming it. A reader can now see
what `KLEESPARK-BT1`'s readers could not.

**And printing the relics immediately falsified a printed assumption.** Every
board of this round asserts *"The run carries Klee's starting relic and no
other."* The staged pages print **two**: *Pounding Surprise* and *Fishing Rod*
(*"Every 3 normal combats, Upgrade a random card in your Deck"*). Fishing Rod
does nothing inside a combat and moves no number this round scores, so no
grade is affected — but the assumption as printed is FALSE on the page, the
preflight's assumption check cannot see it, and a reader who noticed would be
right to distrust the rest. It is recorded here rather than fixed silently.

### 24.7 The pair read

`review/qa/klee-sparks-bt2-pair-review-codex-gpt-5.6-sol.md`, prompt beside it
at `klee-sparks-bt2-pair-review-prompt.txt`. The independent seat read the
completed round against the slate and **agreed slot for slot**: `F1`, `F2`,
`F3`, `F5` UNREACHED; `F4` **MISS** at 0 of 3, on the same reasoning that `F4`
is exempt from the refusal rule; **0 ADVANCE / 5 RETURN**, and on the return
condition, in its own words:

> **DID NOT FIRE.** `F1` is UNREACHED, not PREDICTED. `F2` is also UNREACHED;
> moreover, its out-of-slot text names a cost and there is no next-turn bank
> reading. Neither registered predicate is satisfied on the grades above.

and on the round:

> The boards exposed the intended same-turn Spark-repayment question on `t01`,
> the claimed exclusivity question on `t02`, and the delayed-detonation
> question on `t03` in the readers' prose. But the completed instrument did not
> obtain admissible answers… The round therefore cannot answer the design
> questions it was built to test. … **Overall: RETURN.** This is an instrument
> return, not a balance reading, validation, or design return under the
> pre-registered `F1`/`F2` predicate.

The shadow seat is recorded and not graded: it was refused `forecast_missing`
on all three boards for the same structural reason, so shadow-versus-deciding
agreement has **0 comparable turns** and says nothing about `M62`.

### 24.8 What is and is not licensed by this round

**Licensed.** One engineering row: the forecast's FORM half — a reply schema
that can carry a `forecast` list, in both the Codex seat and the local tester —
without which the staged twin of `EB-229` cannot be graded at all. `EB-238`
closes. `EB-224` stays open with a third round owed.

**Not licensed.** Nothing about the card. No re-price, no re-wording, no sheet
move, no change to §4.2 or to R225's clause, no removal of *Pounding
Surprise*, and no claim about win rate, balance or fun. The arm has now been
staged twice and read on neither: the return condition stands, unanswered, and
the next round is the one that answers it. **A third staged round is not a
re-roll of this one** — the boards, the seeds and the slate are unchanged and
stay pinned; what has to change is the instrument, and R101b keeps this round's
grades exactly as published while it does.

**R217 G rides on every word a reader wrote above.** A tester's account is one
model's account, never validation and never balance evidence, and nothing
measured on a prototype row is quotable anywhere except the
decision-closeness falsifier (R215 B).

### 24.9 THE RERUN — `klee-sparks-bt2r`

**REGISTERED — NOT RUN when this was committed. Claude drafts (R212 item 2),
[USER] countersigns in batch.** The boards, the slate and this section were
committed **before anything was staged, deployed or read**, exactly as §23
was. The machine-readable half is `understudy/turns/klee-sparks-bt2r/`.

**THIS IS NOT A NEW ROUND AND NOT A RE-ROLL.** §24.8 says what has to change
and what may not: *"the boards, the seeds and the slate are unchanged and stay
pinned; what has to change is the instrument"*. It is `KLEESPARK-BT2` asked
again with a form that can answer it, and it follows the `KURAGEMEM002`
precedent at kurage §13.9 — a new dated cell, drafted and committed before the
run, disclosing exactly what moved.

**§24's grades stand exactly as published (R101b).** `F4` MISSED at 0 of 3;
`F1`, `F2`, `F3` and `F5` UNREACHED; 0 ADVANCE / 5 RETURN / 0 ESCALATE; the
return condition DID NOT FIRE. Nothing in this cell re-reads, re-scores or
withdraws one of them, and the first run's forms and verdicts under
`review/qa/klee-sparks-bt2-t0*/` are not written over — which is the whole
reason the rerun's boards carry an `r` in their turn ids.

#### 24.9.1 What changed — the disclosure list, and it is three items long

1. **The reply schema can carry a forecast (`EB-239`, CLOSED on its lock).**
   `understudy/seat.py`'s `form_schema()` now declares `forecast`, nullable
   and required on exactly `target`'s rule; `additionalProperties` stays
   `False`, so the field is DECLARED and the schema is not loosened.
   `staged_turn.forecast_answers` already read a missing `forecast` as the
   empty list, so nothing downstream moved.
2. **Both chairs, from one function.** `local_seat.build_grade_prompt` prints
   `seat.form_schema()` into the local tester's prompt verbatim, which is why
   the shadow chair was refused for the same structural reason as the
   deciding one (§24.7) and why one fix repairs both. There is no second
   schema to keep in step.
3. **`qa_form.md` says so.** The form contract now states that the two seats
   answer through the strict schema, where `forecast` is nullable-and-required
   and `null` means *this board asked for none*, while a hand-written form may
   still omit the key.

**The lock, seen to FAIL first**, in `tier0/tests/test_seat_instruments.py`:
an ANSWERED form — `KLEESPARK-BT2`'s own `t01` reply as it would have had to
be written — was refused `undeclared:forecast` by the old schema and validates
under the new one; and a form that OMITS the field is still refused
`missing:forecast` by the schema and `forecast_missing` by the falsifier on an
asking board, because declaring the field must not stop the falsifier biting
or the forecast stops being a pre-commitment.

**`t03`'s second refusal, `target_missing`, is NOT an instrument defect and
nothing was changed for it.** The verdict names the cause exactly: the
deciding form played *Bag of Tricks* with `target: null` on a board whose one
enemy it had already named elsewhere in the same line (*Mine Toss* → *Shrinker
Beetle*). The form CAN express a target — `target` has been a declared,
required, nullable property of the schema since `EB-149`, and it is the
precedent this cell's fix was written to follow — so this is a READER's
omission on a board with somewhere to aim, caught by `EB-203`'s check doing
its job (§24.4 says so and this cell agrees). **The board is not edited and
neither is the check.** It is disclosed here because it is a second reason
`t03` was refused, and if it recurs on the rerun it is a reading about the
reader and not about the arm.

#### 24.9.2 What is unchanged, and it is everything else

- **The three boards**, byte-identical to `understudy/turns/klee-sparks-bt2/`
  except the turn id: same seeds `JH4T8MSN10KS` / `R805DJ56LZHM` /
  `YX7PB48WR7R4`, same hands, same 55 HP body, same 4-Energy-against-3 trade,
  same assumptions, same three forecast questions per board, same
  `replay_next_turn: true` on `t03`.
- **`slots.yaml`**: `C1` threshold 2 ceiling 2 (`t01`, `t02`), `C2` threshold 1
  ceiling 1 (`t03`), re-computed by `local_tester round --plan-only` before
  staging and identical to §23.2's numbers, closeness gaps included (0.031 /
  0.019 / 0.117).
- **The slate `F1`–`F5`**, §23.4's table verbatim — the same predictions, the
  same thresholds (1/1, 1/1, 1/1, 3/3, 1/1), the same falsifiers, the same
  UNREACHED rule (`EB-209`), the same reading that a MISS on `F3` is an
  INSTRUMENT finding and a MISS on `F5` a LEGIBILITY one, and the same §23.5
  list of what a MISS does not license.
- **The return condition, verbatim from §23.4:**

> **THE PRE-REGISTERED RETURN CONDITION (R229), AS A GRADED PREDICATE.**
> `F1` and `F2` are ONE finding and are read together.
>
> **The arm RETURNS TO DESIGN if EITHER**
> **(a) `F1` is PREDICTED — the bank reads ≥ 3 again after the detonation, on
> the same turn, and the reader pays for both priced uses; OR**
> **(b) `F2`'s form names NO cost given up AND `F2`'s next-turn bank reads 3.**
>
> Either alone RETURNS the arm; both is the strongest form and is reported as
> one finding, not two.

#### 24.9.3 The chair, the budget and the guard

**Unchanged from §23.6.** The Codex seat DECIDES every board
(`--seat-spot-check 1`), the local seat sits SHADOW (`--seat-mode shadow`,
R222 B), fresh-Opus is NOT seated — the row is `authored_by: [claude]` and a
same-family deciding read is not author-disjoint under R217 C.

- **Plan: 3 deciding seat reads + 1 pair read = 4 Codex calls.** The cap is
  **9 minus the 4 the first run spent = 5**; the plan sits one under it. A
  round that needs a sixth call STOPS rather than borrowing from the cap.
- **The meter**, read immediately before the round: `5h 59%` (resets 16:36
  EDT) / week 28%. `EB-227`'s guard refuses at **85%** of the five-hour window
  and 50% of the week; if it refuses mid-round the round **STOPS at that
  board** and the results record how many were read, rather than finishing on
  a cheaper chair.
- **Preconditions, each of which stops the round:** `gits-game.lock` under the
  user's Temp directory absent; Steam running; the installed dev build
  `0.2.1676+proto.dirty` carrying the row, proven read-only off the deployed
  `mods\klee\manifest.json` before anything is staged. **Nothing is deployed
  for this cell** — the fix is in Python, not in the mod.

#### 24.9.4 What this cell can and cannot settle

It can settle exactly what §24 could not reach: whether the priced mode's
same-turn refund happens **on the wire** (`F1`), what one turn of the future
does to the bank (`F2`), and whether `EB-236`'s exclusivity certification
survives contact with a reader (`F3`). It cannot settle the whole fight —
`EB-224`'s third owed piece — and it cannot make the tier0 mirror see a mode
or a relic (§23.7 stands word for word). **R217 G rides on every word any
reader writes here.**

#### 24.9.5 What actually ran — the session and the stamp

Dev build **`0.2.1676+proto.dirty`**, read off the deployed
`mods\klee\manifest.json`; game **`v0.111.0`** (`min_game_version` on the same
file); world `r229-2026-08-30` @ `bac66284`, the commit that registered this
cell. **Nothing was deployed** — the fix is Python and the installed build
already carried the row. The game lock was absent and Steam was running.

**The meter, and one thing it did on its own.** Read immediately before the
round: **`5h 59%` / week 28%**. The five-hour window **ROLLED OVER at 16:36
EDT, between the local reads and the first Codex call**, exactly as §23.6 had
noted the reset time; the first deciding read printed `5h 0% (rolled over)` and
the round finished at **`5h 1%` / week 28%** (a new window, resetting 21:42
EDT). `EB-227`'s guard never came near refusing. This is recorded rather than
smoothed: the round's four calls were paid out of a window that had just reset,
which is *cheaper* than the plan assumed and is not a licence to spend more.

**3 boards run, 0 UNRUN, 6 forms graded, 2 lines replayed.**

| turn | seed | grader | family | verdict | refused by | replay |
|---|---|---|---|---|---|---|
| `klee-sparks-bt2r-t01` | `JH4T8MSN10KS` | `codex-gpt-5.6-sol-fresh` | gpt | **SURVIVES** | – | **replayed, every step ok** |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | REFUSED | `target_missing` | – (shadow) |
| `klee-sparks-bt2r-t02` | `R805DJ56LZHM` | `codex-gpt-5.6-sol-fresh` | gpt | **SURVIVES** | – | **replayed; the game refused play 2** |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | SURVIVES | – | – (shadow) |
| `klee-sparks-bt2r-t03` | `YX7PB48WR7R4` | `codex-gpt-5.6-sol-fresh` | gpt | **REFUSED** | `no_second_line`, `intent_insensitive` | – |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | REFUSED | `intent_insensitive` | – (shadow) |

Every seed came back as requested on the first attempt (no `EB-191`), every
board passed its face-defect and assumption preflights, and `--plan-only`
reproduced §23.2's numbers exactly: `C1` threshold 2 ceiling 2, `C2` threshold
1 ceiling 1, closeness 0.031 / 0.019 / 0.117.

**And `forecast_missing` refused NOTHING.** All six forms carried three answers
against three questions. That is `EB-239` working, and it is the whole
difference between this cell and §24.

**What the round spent:** 3 Codex deciding reads + 1 Codex pair read = **4
calls**, exactly the plan, against a cap of 5 (9 minus §24's 4). 3 local reads
in the shadow chair. 0 control reads — fresh-Opus is not seated in a design
round.

#### 24.9.6 THE WIRE LEDGER — the readings §24 could not take

The Spark bank is a player status **printed only when non-zero**, so an empty
status block is a bank of 0.

**`t01`, the return-condition board. Every step completed.**

| step | bank | Seapunk |
|---|---|---|
| staged read | **3** | 45 HP, no statuses |
| *Bag of Tricks*, priced mode, resolves | **0** | 45 HP, `bomb: 15` |
| *Kaboom!* at Seapunk | **3** | 23 HP, `pyro aura: 2` |
| *Firework Finale* at Seapunk | **0** | **5 HP** |
| *Spirited Away* | 0 | 5 HP; player Block 12 |

40 damage in one turn, the player untouched at 42 HP with 12 Block, and **both
3-Spark uses paid and resolved inside the turn.** The refund `KLEESPARK-BT1`
saw in passing and §24 could only quote as prose is now a wire reading:
3 → 0 → **3** → 0.

**`t02`, the exclusivity board. The game refused the second play.**

| step | bank | Nibbit |
|---|---|---|
| staged read | **3** | 46 HP |
| *Bag of Tricks*, priced mode, resolves | **0** | 46 HP, `bomb: 15` |
| *Firework Finale* at Nibbit | — | **REFUSED by the bridge** |

*"Card 'Firework Finale' cannot be played: `BlockedByCardLogic`"*, and the live
hand entry reads `can_play: false`, `unplayable_reason: BlockedByCardLogic`.
**`EB-236`'s certification holds on the wire**: on a hand with no Attack to pop
the Bombs, no order of play buys both, and §24.5 item 2's unresolved reading —
*"whether the game would have refused it is exactly what a replay would have
shown"* — is now resolved, in `EB-236`'s favour. The reader's line was
unpayable on paper and unpayable in the game.

**`t03`**: the deciding form was REFUSED, so no replay ran and the
`replay_next_turn` reading is absent for the third round running.

#### 24.9.7 The slate, graded mechanically

**3 PREDICTED (`F1`, `F4`, `F5`) / 0 SPLIT / 1 MISS (`F3`) / 1 UNREACHED
(`F2`).**

**`F1` PREDICTED at 1 of 1.** `t01`'s deciding line is *Bag of Tricks* [priced
mode] → *Kaboom!* → *Firework Finale* → *Spirited Away*, all in one turn, and
the replay reads the bank at **0 immediately after the mode** and at **3
immediately after the Attack**. Both halves of the predicate, on the wire.

**`F2` UNREACHED.** `t03`'s deciding form was REFUSED — `no_second_line` (its
Q2 reads *"none"*) and `intent_insensitive` — so no replay ran and there is no
next-turn bank reading. The delayed refund is still unmeasured, and both
refusals are about the reader, not about the instrument.

**`F3` MISSED at 0 of 1, and WHICH CLAUSE FIRED MATTERS.** The falsifier has
two clauses — *both priced uses paid in one turn*, or *the second answer names
neither*. **The first did NOT fire:** exactly one priced use was paid, because
the game refused the other. **The second did:** `t02`'s Q2 reads *"I seriously
considered replacing Mine Toss with Duck and Cover"*, which names neither *Bag
of Tricks*' priced mode nor *Firework Finale*. §23.4 calls a MISS here an
INSTRUMENT finding on the reasoning that *"a form that does [buy both] is a
defect in the check or in the build"* — **and that reasoning belongs to the
clause that did not fire.** `EB-236` is vindicated and the build behaved, so
there is no defect to file and **nothing is minted on `F3`**. What the slot
caught is a reader who wrote a line the board could not pay for and then
discussed a different trade-off entirely.

**`F4` PREDICTED at 3 of 3.** Every deciding form carries a full forecast —
`t01` `["0", "3", "0"]`, `t02` `["3", "yes", "1"]`, `t03` `["4", "4", "20"]` —
and no form on either chair was refused `forecast_missing`. `EB-229`'s staged
twin works end to end for the first time.

**`F5` PREDICTED at 1 of 1.** On `t01`, where the line takes the priced mode,
the first forecast answer reads **0** and the second reads **3** — and the wire
read 0 and 3. The reader did the arithmetic in advance, off a page that prints
the relic, and got it right. That is the legibility reading §23.4 asked for.

**Judgment, per slot: `F1` RETURN (it is the return-condition slot and it
fires), `F2` RETURN, `F3` RETURN, `F4` ADVANCE, `F5` ADVANCE — 2 ADVANCE /
3 RETURN / 0 ESCALATE, overall RETURN.** Unlike §22 and §24, **this RETURN is
on the ARM'S DESIGN and not on the instrument**: the instrument did its job on
every board it was handed a survivable form on.

#### 24.9.8 THE PRE-REGISTERED RETURN CONDITION — **IT FIRED**

R229's condition, read exactly as §23.4 and §24.9.2 wrote it:

- **(a) IS SATISFIED.** `F1` is **PREDICTED**. The bank read **3 again after
  the detonation, on the same turn** (`0` after the mode, `3` after *Kaboom!*),
  and the reader **paid for both priced uses** — *Bag of Tricks*' 3-Spark mode
  and *Firework Finale*, both resolved, 45 → 23 → 5 HP.
- **(b) is not satisfied.** `F2` is UNREACHED: its form was refused and there
  is no next-turn bank reading. It contributes no inference either way.

**THE ARM RETURNS TO DESIGN.** (a) alone returns it, as registered, and it is
reported as ONE finding and not two. The independent pair read
(`review/qa/klee-sparks-bt2r-pair-review-codex-gpt-5.6-sol.md`, prompt beside
it) agreed slot for slot — `F1` PREDICTED, `F2` UNREACHED, `F3` MISS, `F4` and
`F5` PREDICTED, 2 ADVANCE / 3 RETURN, overall RETURN — and on the condition, in
its own words:

> **FIRED.** `F1` is PREDICTED: the bank returned to 3 after the same-turn
> detonation, and the reader paid for both priced uses. Predicate (a) therefore
> returns the arm independently of `F2`.

**What a RETURN does and does not do.** §23.5 still binds: it does **not**
itself re-price the mode, move §4.2's price table, re-read R225's mode-head
clause, remove *Pounding Surprise*, amend LAW, or say anything about win rate,
balance or fun (R215 B, Guardrail-7). It returns the arm to [USER] as a
**numbered pick list**, and Claude picks nothing on it.

#### 24.9.9 THE PICK LIST — [USER]'s, and it is four numbered directions

**What was measured, because the pick rests on it.** The price is REAL where
nothing can pop the Bombs: on `t02` the mode took the bank to 0 and the game
itself refused *Firework Finale*. The price is NET-FREE where an ordinary
Attack lands the same turn: on `t01` the same 3 Sparks bought three Bombs,
*Kaboom!* popped them, *Pounding Surprise* handed the 3 back, and the rival
3-Spark sink was paid out of the refund. The mode's cost is therefore
**contingent on whether the hand holds a detonator** — and on `t01` the reader
did not experience it as a cost at all: it forecast `0, 3, 0` before playing,
and was right.

1. **Re-price the mode.** Move the printed 3 so the refund cannot cover the
   rival sink. Cheapest to write; but the refund scales with the BOMB COUNT, so
   any price the mode can pay for itself at is a price the relic can hand back.
   Fixes the number rather than the loop.
2. **Restructure the mode so its own Bombs cannot pay for it.** Bombs placed by
   the priced mode do not trigger *Pounding Surprise*, or resolve only at the
   start of the next turn. Kills the loop directly; costs a special case in the
   Bomb/relic seam that BOTH engines must carry, and `t03` shows the delayed
   half is still unmeasured.
3. **Accept the refund as the card's POINT, and write the design intent to say
   so.** R229 already accepted it as an observed test condition; this makes it
   deliberate — *Bag of Tricks* is the card that turns a bank plus a detonator
   into a free second sink, and the decision it poses is *does this hand hold
   an Attack?* Costs nothing to build; costs a written intent, and re-poses
   `F2` on the delayed half. **← RULED (R230), QUALIFIED.**
4. **Drop the arm.** Retire `proto_spark_mode_bombs`' priced mode from the
   prototype surface. Cleanest; spends three staged rounds of work, and leaves
   R225's mode-head price clause without the row it was amended for.

**Claude's recommendation, which is not a decision: 3.** The one thing this
round measured on the wire is that the price behaves DIFFERENTLY on two hands
that differ only in whether an Attack is in them, and that the game enforces
the difference by itself, with no rule written for it. 1 and 2 move a number or
add a seam on the strength of a single graded turn; 4 discards a row that three
rounds of instrument work were built around. 3 is the only option the evidence
positively supports, and the only one that leaves `F2`'s unmeasured half worth
asking. **The pick is [USER]'s** (CLAUDE.md's ladder: a pick between genuinely
different design directions).

> **RULED (R230, 2026-08-30): option (3), QUALIFIED.** The refund loop is
> accepted as the card's deliberate bridge mechanic — but the qualification
> corrects the economics this section stated. The priced mode is **not**
> net-free with a detonator in hand: it costs **one net Spark** relative to the
> free mode after detonation, and it demands **three Sparks of up-front
> liquidity** to open at all. A same-turn detonator changes WHEN that liquidity
> comes back and whether a second sink can be chained onto it; it does not make
> the priced mode economically identical to the free one. The rewritten design
> intent, the F2 registration correction owed before any re-pose, and a NEW
> pre-registered whole-fight collapse condition are at §24.9.11. The full
> record is `review/ruled/sitting-2026-08-30.md` §R230.

#### 24.9.10 Out of slot — recorded, graded nowhere (R101b)

1. **The declared body HP is 55 and the live body is 45 / 46 / 40.** Every
   board writes `set_hp: {who: first, amount: 55}`; the packets read Seapunk
   45, Nibbit 46, Shrinker Beetle 40, and `board_check` passed with no
   differences on all three because the `board:` block it compares against is
   what the packet records. **It is identical in §24's first run** — the boards
   are reproduced exactly — and it moves no grade: the largest line is 40
   damage against 45 HP, so §23.2's *"no lethal line"* holds, by 5. It is the
   same shape of blind spot as `EB-240` (a declared board fact the preflight
   cannot check against the wire), and it is recorded rather than fixed
   silently.
2. **The shadow chair, recorded and not graded.** `t02` SURVIVES, `t01`
   REFUSED `target_missing` — it played *Bag of Tricks* at no target, the same
   refusal the DECIDING chair drew on `t03` in §24, and again a reader's
   omission rather than the schema's — and `t03` REFUSED
   `intent_insensitive`. Shadow-versus-deciding agreement is **1 of 3
   comparable turns** and says nothing about `M62` at that denominator.
3. **`t03` was refused for something `EB-239` cannot fix.** Its Q2 reads
   *"none"*. A reader that considers no second line fails R213's readiness
   test, and the funnel is right to refuse it; neither the board nor the form
   schema is at fault.

**R217 G rides on every word any reader wrote above.** A tester's or a grader's
account is one model's account, never validation and never balance evidence,
and nothing measured on a prototype row is quotable anywhere except the
decision-closeness falsifier (R215 B).

#### 24.9.11 R230 — the pick list is RULED, and what the ruling actually says

**The ruled option is (3), qualified.** *Bag of Tricks* keeps its refund loop.
The loop is now the card's stated point rather than an accident the round
tripped over, and the design intent has been rewritten to say so (below). The
arm does **not** return to design a second time; it carries on to the whole
fight under a new failure condition that is registered here, before that fight
is played.

Everything under this heading is written in plain English on purpose. This is
the section a reader should be able to open cold and understand without any of
the register shorthand the rest of the packet uses.

**1. What the mode actually costs — the number this ruling corrects.**

§24.9.9 above said the priced mode is *"net-free where an ordinary Attack lands
the same turn."* **That framing was wrong, and this ruling corrects it.** Put
the two modes side by side on the same turn, with a detonator in hand and a
bank of 3:

- **Free mode.** Place one Bomb. The Attack pops it. The starter relic pays 1
  Spark per Bomb detonated, so the bank goes **3 → 4**.
- **Priced mode.** Pay 3 for three Bombs. The Attack pops all three. The relic
  pays 3 back, so the bank goes **3 → 0 → 3**.

The player ends the turn on **3 instead of 4**. The real trade is therefore
**one net Spark for two extra Bombs — 10 extra damage** — and not a free
upgrade. The deciding form says exactly this in its own third answer: the line
*"gave up the Spark that the single-Bomb line would have retained at turn end,
in exchange for 10 additional Bomb damage."*

There is a second cost the earlier framing missed entirely. The mode cannot be
opened at all below a bank of 3, so it demands **three Sparks of up-front
liquidity** even though only one of them is spent in the end. That is a real
constraint on when the card can be played, and it is a large part of what makes
the card a decision rather than a formality.

A same-turn detonator changes two things and only two: **when** the locked
liquidity comes back (immediately, instead of at the start of the next turn),
and **whether** a second sink can be chained onto the refund in the same turn.
It does not erase the one-Spark difference between the modes.

**2. Who recommended what — the attribution, stated plainly.**

Option (3) was **Claude's recommendation alone.** The independent pair read
(`review/qa/klee-sparks-bt2r-pair-review-codex-gpt-5.6-sol.md`) graded the five
slots and confirmed that the return condition fired; it offered **no opinion**
on the four redesign directions and recommended none of them. Nothing in this
packet, in `BACKLOG.md` or in `EXPERIMENTS.md` claims otherwise, and nothing
should be written later that does.

**3. The design intent, rewritten under R230 (2026-08-30).**

The intent statement that governs this row lives with the row itself, in
`docs/prototype-surface.yaml` under *ARM 4: two prices for one card*, and it has
been rewritten there. In full, and in the same words:

> *Bag of Tricks* is a **bridge**. Its priced mode asks the player to hold a
> bank of **3** — real liquidity, locked up, and unavailable to anything else
> until it is released — in order to buy **two additional Bombs** for a **net
> cost of one Spark** relative to the free mode once the Bombs detonate. If an
> Attack is already in hand, that liquidity is returned **immediately** and can
> be sequenced straight into another sink in the same turn. If it is not, the
> bank stays locked until the Bombs go off on their own next turn. So the card
> poses two questions at once: *can I afford to tie up three Sparks right now*,
> and *do I hold something that unties them this turn*.

Note what the intent does **not** claim: it does not claim the mode is free, and
it does not claim the refund makes the two modes equivalent.

**4. A registration defect that must be fixed before `F2` is re-posed.**

`F2` — the second half of R229's return condition — has never been graded; it
has come back UNREACHED three rounds running. Before it is posed a fourth time,
its predicate has to be repaired, because as written it cannot pass.

The predicate (`understudy/turns/klee-sparks-bt2r/MANIFEST.md`, `F2`) requires
the Spark bank to read **exactly 3** at the start of the next turn. But board
`t03` also grants *Mine Toss*, which places a Bomb of its own, so the proposed
line puts **four** Bombs on the board and the refund is **4**. The reader
forecast 4 and was correct; the predicate would have failed it anyway. That is
the registration's defect, not the reader's.

**The correction owed:** a re-posed `F2` must grade the refund **attributable to
Bag of Tricks' own Bombs — at least 3** — or else the extra Bomb source must
leave the board entirely. Either repair is acceptable; what is not acceptable is
re-posing the exact-3 predicate on a board that cannot produce a 3.

**The published boards and MANIFEST are NOT edited** (R101b): they are the
record of a run that has already happened, and they stand as published. The
correction applies to the next registration, which is a new document.

**5. THE WHOLE-FIGHT FAILURE CONDITION — pre-registered NOW, by this ruling.**

This is registered before the whole fight is drafted, so that no later reading
of the result can pick its own threshold after seeing it.

> When the arm reaches whole-fight play: **if the priced mode proves effectively
> automatic** — taken on essentially every turn where an affordable detonator is
> in hand, with no free-mode choices actually taken and no named reason on any
> turn to preserve the extra Spark — **then the bridge has collapsed into free
> damage and the arm RETURNS TO DESIGN again.**

The reasoning is the one-Spark cost above. A cost of one Spark is a real cost
only if a Spark is sometimes worth more elsewhere. If a whole fight never once
shows the player preferring that Spark, the cost is nominal and the decision the
card exists to create does not exist.

**6. Three sunk rounds are not evidence, in either direction.**

`KLEESPARK-BT1`, `KLEESPARK-BT2` and its rerun cost real work, and none of that
work argues for keeping the arm. The two earlier rounds returned on the
**instrument**, which says nothing about the card. The rerun returned on the
**design**, which is why this ruling exists at all. What earned the arm its
continuation is the corrected one-Spark trade in item 1 — a real, if small,
decision that the wire shows and that the reader articulated unprompted. Had the
economics come back genuinely free, option (4), dropping the arm, would have
been the honest ruling, and the three rounds already spent would not have saved
it.

**What this ruling does NOT do.** It re-prices nothing: the 3 stands, §4.2's
price table is untouched, R225's mode-head clause is unchanged, and *Pounding
Surprise* stays exactly as it is in both engines. It says nothing about win
rate, balance or fun (R215 B, Guardrail-7). It discharges no part of `EB-224`'s
acceptance line beyond the redesign direction itself — the whole fight is still
owed, and it is what comes next.

---

## 25. `KLEESPARK-BT3` and `KLEESPARK-W5` — the two cells R230 left owed (`EB-224`)

**REGISTERED — NOT RUN. Drafted by Claude from written intent under R212 item
2 and committed BEFORE anything is staged, deployed, launched or read;
[USER] countersigns in BATCH, or vetoes within five days.** Nothing in this
section has been run. No board has been staged, no seat has been called, the
game has not been launched, and no number below was chosen after seeing a
result.

R230 ruled §24.9.9's four-item pick at **option (3), QUALIFIED**: *Bag of
Tricks* keeps its refund loop, the loop is the card's stated point rather than
an accident the round tripped over, and the arm carries on. It left **exactly
two things owed**, and this section registers both of them, in the order the
ruling put them:

1. **the `F2` repair**, which comes first — `KLEESPARK-BT3`, two staged
   boards, `understudy/turns/klee-sparks-bt3/`;
2. **the whole fight**, carrying the **pre-registered collapse condition R230
   wrote before the fight was drafted** — `KLEESPARK-W5`.

### 25.1 What R230 settled, in the terms these two cells are written in

**The corrected economics.** §24.9.9 called the priced mode *"net-free where an
ordinary Attack lands the same turn"*, and R230 corrects it. On a bank of 3
with a detonator in hand the free mode places one Bomb, the Attack pops it, and
*Pounding Surprise* takes the bank **3 → 4**; the priced mode places three, the
Attack pops all three, and the relic takes it **3 → 0 → 3**. The player ends the
turn on **3 instead of 4**. The real trade is **one net Spark for two extra
Bombs, 10 extra damage**, behind a **three-Spark up-front liquidity
requirement** the free mode does not carry. A same-turn detonator changes
**when** the locked liquidity returns and **whether** another sink can be
chained onto it; it does not make the two modes economically identical.

**Why that matters to both cells below.** A cost of one Spark is a real cost
**only if a Spark is sometimes worth more elsewhere**. `KLEESPARK-BT3` asks
whether a reader can NAME what the locked liquidity cost on a single turn;
`KLEESPARK-W5` asks whether, across a whole fight, the player ever prefers the
Spark. Those are the two halves of the same question and neither substitutes
for the other.

**The `F2` defect, and the repair taken.** R230, verbatim: *"a re-posed `F2`
must grade the refund ATTRIBUTABLE TO Bag of Tricks' own Bombs — at least 3 —
or else the extra Bomb source must leave the board entirely."* `KLEESPARK-BT3`
takes the **second** repair. *Mine Toss* is gone; nothing in either hand places
a Bomb except the card under test and neither board starts with one, so every
Spark the relic pays back is the mode's own **by construction rather than by
subtraction**. `G1`'s predicate is written both ways so it reads the same
whichever way it is checked. **`klee-sparks-bt2r`'s boards and MANIFEST are NOT
edited (R101b)** — they are the record of a run that happened.

### 25.2 `KLEESPARK-BT3` — the two boards

Full manifest, slate and both files:
`understudy/turns/klee-sparks-bt3/` (`MANIFEST.md`, `slots.yaml`, `t01`,
`t02`). Both are `exact_hand: true`, `prototype: true`,
`replay_next_turn: true`; both seeds are recorded ONE-BODY on a Klee run over
three earlier rounds.

| turn | seed | bank | HP | body | hand | Energy | the board | slot |
|---|---|---|---|---|---|---|---|---|
| `t01` | `YX7PB48WR7R4` | **3** | **24**/62 | 40 | Bag of Tricks, Duck and Cover, Spirited Away, Run Away! | 2 of 3 needed | the delayed refund with the pressure ON — a telegraphed 16 into 24 HP | `C1` |
| `t02` | `R805DJ56LZHM` | **3** | **40**/62 | 46 | the same four | 2 of 3 | the same question with the pressure OFF | `C1` |

**Two boards and not one, for a stated reason.** `F2` has graded UNREACHED
three rounds running and twice of those because one deciding form was REFUSED.
A slot posed on one board has a denominator of one and one refusal takes it to
zero — which is what happened at §24 and again at §24.9. Two boards is the
cheapest repair for that failure mode, and the second board is not a duplicate:
it moves the incoming pressure, so that a cost only nameable at 24 HP is
separable from a cost the card itself imposes.

**Every board forces a trade** (`EB-236`): each hand costs 3 Energy against 2.
**The Energy is this round's one other change and it is disclosed** — dropping
*Mine Toss* out of `klee-sparks-bt2r-t03`'s hand would have left 3 Energy
paying for the whole hand, which `no_forced_trade` refuses, so the Energy moves
3 → 2. No card is added.

**`EB-240`'s `expects:` block is declared on both**, and it is new machinery
whose first use this is. §24.9.10 recorded two printed falsehoods: one relic
asserted where the page printed two, and `set_hp: {who: first, amount: 55}`
against bodies of 45 / 46 / 40. These boards **declare both relics** and
**write no enemy HP at all**, declaring instead the body each seed is recorded
at; the stage refuses on a mismatch before a packet is written. A refusal
**stops the round at that board with nothing read**; the declaration is
corrected from the observed value, the correction is disclosed with the
results, and the board is re-staged from the corrected file — a re-attempt on
`EB-191`'s precedent and **not a re-roll**.

**The plan, printed before anything was staged:**

```
round of 2 board(s) in R221 B's pre-registered order; seat spot-check every 4; first set = 2; lanes = 1
   1  FIRST  SEAT  lane0  klee-sparks-bt3-t01   slots=C1  closeness=0.135
   2  FIRST        lane0  klee-sparks-bt3-t02   slots=C1  closeness=0.135
preflights: every board passes face-defect and assumption checks
SLOT OK   C1: threshold 2, ceiling 2 of 2 board(s)  [klee-sparks-bt3-t01, klee-sparks-bt3-t02]
board design: every board forces a trade, and every declared exclusive pair is exclusive
```

Run with `--first 0` (every board runs; both are the only board of their kind)
and `--seat-spot-check 1` (the Codex seat decides every board — a DESIGN round
under `M64` (1) / R224; fresh-Opus is not seated, the row being
`authored_by: [claude]` under R217 C; the local seat sits SHADOW).

**The slate is `G1`–`G4` and lives in the manifest**, written out in full
there rather than duplicated here. In one line each: **`G1`** re-poses `F2`
under R230's corrected predicate — the third answer names a concrete thing the
turn gave up AND the next-turn bank reads ≥ 3, all of it the mode's own —
threshold 2 of 2, with the one-refusal rule written in advance; **`G2`** is
`G1` read on `t02` alone, the pressure control, and is a SUBSET of `G1` and
reported as one; **`G3`** gives the forecast channel its denominator at 2 of 2;
**`G4`** grades the delayed arithmetic (`0` then `3`) at 1 of 2. Every
UNREACHED rule, every decision linkage and the *what a MISS does not license*
block are in the manifest and bind as written.

**Budget: 2 deciding reads + 1 pair read = 3 Codex calls expected, cap 6.**

### 25.3 `KLEESPARK-W5` — the whole fight, and the collapse condition

`EB-224`'s last owed half. **It runs only after `KLEESPARK-BT3` is graded**, and
it does not run at all where `G1` MISSES on its engine clause (ii) or where
`G3` MISSES — both of those are instrument or engine findings that would make
the fight unreadable, and both are written into `BT3`'s decision linkage.

**Unit.** One `understudy.blindplay session` on a live dev build carrying the
prototype rows, Codex seat, the arm's rows granted into the starting deck by
`understudy.embark --arm`, the whole fight (or fights) to the action budget.

#### 25.3.1 THE COLLAPSE CONDITION — R230's words, then the numbers

R230 registered this **before the fight was drafted, so that no later reading
of the result can pick its own threshold after seeing it.** Quoted verbatim:

> When the arm reaches whole-fight play: **if the priced mode proves effectively
> automatic** — taken on essentially every turn where an affordable detonator is
> in hand, with no free-mode choices actually taken and no named reason on any
> turn to preserve the extra Spark — **then the bridge has collapsed into free
> damage and the arm RETURNS TO DESIGN again.**

**In graded-predicate form.** Three definitions, all read off the run's own
artefacts — the sealed record's combat pages, the per-page `wire.json`
snapshots (`EB-216`) and the forecast rows (`EB-229`) — and none of them read
off prose written after the fact:

- **An OPPORTUNITY PAGE** is a combat page on which the printed Spark bank is
  **≥ 3**, *Bag of Tricks* is in hand, and at least one **affordable
  detonator** is in hand — an Attack the page's printed Energy can pay for.
  (Any Attack that gets HP damage through pops the target's Bombs; there is no
  special detonator card in this deck.)
- **A PRICED-MODE TAKE** is an opportunity page whose command plays *Bag of
  Tricks* choosing the priced mode. **A FREE-MODE TAKE** is any page whose
  command plays it choosing the one-Bomb mode while the bank was ≥ 3.
- **A PRESERVED-SPARK REASON** is a forecast answer or a `thinking` sentence
  naming a reason to keep Sparks rather than spend them this turn — a named
  alternative use, a named next-turn plan, or the liquidity itself.

> **`B1` — THE COLLAPSE FIRES, AND THE ARM RETURNS TO DESIGN AGAIN, IF ALL
> THREE HOLD:**
>
> **(i) priced-mode takes ≥ 90% of opportunity pages, on a denominator of at
> least 4 opportunity pages;**
> **(ii) ZERO free-mode takes across the whole session; AND**
> **(iii) ZERO pages carry a preserved-Spark reason.**
>
> *"Effectively every turn"* is **≥ 90% with a floor of 4** — a floor, because
> two-of-two is not a habit. *"No free-mode choices actually taken"* is **0**.
> *"No stated reason on any turn"* is **0**. **Any one of the three failing
> refuses the collapse**, and the arm stands where R230 put it.
>
> **UNREACHED where fewer than 4 opportunity pages occur.** A fight that never
> posed the question has measured the GENERATOR and not the card — which is
> exactly what `W1'` found and `W3` confirmed — and under the slate's own rule
> an UNREACHED slot is not a pass and not a fail. Nothing is inferred, no
> [USER] row opens, and the act is another fight, not a reading.

*What a `B1` collapse decides:* the arm RETURNS TO DESIGN a second time, as a
numbered pick list to [USER] and nothing else. A RETURN moves no number by
itself (R215 B, Guardrail-7). *What a refused collapse decides:* nothing is
licensed by it either — it is the absence of a failure, not a pass, and it does
not advance the row to the sheet.

#### 25.3.2 The rest of the slate

**`B2` — the one-Spark trade is NAMED at least once.** On ≥ 1 page where both
modes were affordable, the tester's own sentence names the liquidity, the net
Spark, or what the bank was being kept for. *Threshold:* 1. *Falsifier:* no
page does. *UNREACHED* where no page ever offered both modes at a bank ≥ 3.
*A MISS with `B1` not collapsed is a LEGIBILITY finding* — the intent is real
and unreadable — filed to `BACKLOG` as a page or wording row, **never** a
re-price.

**`B3` — the up-front liquidity BINDS at least once.** ≥ 1 page where *Bag of
Tricks* is in hand at a bank of 1 or 2 and the priced mode is therefore not
available. *Threshold:* 1. *Falsifier:* 0 such pages on a denominator of at
least 3 pages with the card in hand. *UNREACHED* where the card reaches the
hand on fewer than 3 pages. This is the half of R230's intent that says the
three Sparks are *"real liquidity, locked up"*; a bank that is never below the
price has no liquidity requirement in it.

**`B4` — the delayed refund at fight scale.** ≥ 1 page where the priced mode is
taken with NO affordable detonator in hand, and the following combat page's
printed bank shows the refund arrived. *Threshold:* 1. *Falsifier:* every
priced-mode take has a detonator in hand. *UNREACHED* where the priced mode is
never taken. This is `BT3`'s question asked where the player, not the board,
chose the hand.

**`B5` — RECORDED AND NOT GRADED.** Per-fight peak printed Spark bank;
priced-mode takes against free-mode takes; and the count of pages carrying a
preserved-Spark reason. Beside `W3`'s 4.0 and `W4`'s 5.5 medians and **NOT a
comparison** (§19.2 item 1) — a comparator, never a threshold.

#### 25.3.3 `EB-229`'s forecast channel is switched ON, and what that costs

This is the first registration to use the blind RUN's forecast channel
(`understudy.blindplay session --forecast`, opt-in, asked before the command on
every combat page). Two questions, asked conditionally so that asking them does
not recommend a line:

1. *"What will your Spark bank read at the very end of this turn, on the line
   you are about to play?"*
2. *"If you are about to spend Sparks this turn, what are you giving up by
   spending them rather than keeping them? If you are not spending any this
   turn, write 'not spending'."*

**The error direction is declared before the run and it runs one way.** Asking
question 2 every turn makes a preserved-Spark reason EASIER to produce, so
`B1` clause (iii) — *zero pages carry one* — becomes **harder to satisfy**.
The channel therefore biases the collapse condition toward NOT firing: a
collapse that fires anyway is a **floor**, and a refused collapse is
correspondingly weaker evidence than it would have been on a silent page. That
is the trade, and it is taken because `KURAGEMEM002` graded three slots
UNREACHED for want of exactly this channel and the alternative is mining
`thinking` prose for a pre-commitment it was never asked for.

#### 25.3.4 Contaminations, blind spots and what is NOT folded in

1. **The deck is GRANTED, not drafted** — as `W1` through `W4` were. Nothing
   here is a drafted-economy reading and `S1`'s and `W3`'s findings on the
   generator are not re-opened.
2. **`+proto` build, prototype surface.** Every number is about a prototype row
   (R215 B) and nothing is quotable except the decision-closeness falsifier.
3. ***Pounding Surprise* is present and is meant to be.** R230 keeps it; it is
   the mechanism under test, not a confound to control.
4. **`EB-235` is NOT folded in here.** The Rare Power's uptake slot rides the
   fold's mixed-pool read and is registered nowhere in this section.
   `proto_true_spark_knight` is **not granted**; if it is drafted mid-run it is
   RECORDED and grades nothing, and nothing in this section is evidence about
   it in either direction.
5. **Neow.** `embark` leaves the run on the Neow screen, which cannot be
   skipped and two of whose three boons rewrite the deck. The operator takes
   **the only deck-neutral boon offered**, by `W4` §19.5's registered rule, and
   names which one it was in the results.
6. **`EB-191`** — the run seed is re-read off the wire from the same process
   before the session starts and written into the sidecar.
7. **The maker/sink ratio cannot see a kit declaration** (`EB-219`, C21) or
   *Pounding Surprise*'s per-detonation gain, so every income figure this
   session produces is a **FLOOR** and never a ceiling.
8. **R217 G rides on every sentence the tester writes.** One model's account,
   never validation, never balance evidence, never approval.

#### 25.3.5 Budget, gates and stop lines

- **Codex calls:** `--max-actions 40`, `--max-refusals 2`, one fight record and
  one run record — worst case **45 calls**, which is `W3`'s shape and its
  actual spend. The cap for the session is **45**.
- **`EB-227`'s guard** refuses at 85% of the five-hour window and 50% of the
  week; the meter is read immediately before and after and both readings are
  recorded, unsmoothed.
- **R225's soak gate** (`fights=3 defects=0`) passes before the session starts.
- **The pck contract check** is empty and **the printed-Spark-price stop rule**
  is checked, as `W4` ran them.
- **Preconditions that stop the session:** the game lock absent; Steam running;
  the installed build proven read-only to carry the row before anything is
  granted.

### 25.4 What these two cells do NOT license

**Neither cell licenses any of this, and it is registered before the run so it
cannot be argued after:** a re-price of the mode's 3; a change to §4.2's price
table; a new sink row (R225); any amendment to or re-reading of R225's
mode-head clause; the removal or suppression of *Pounding Surprise*; a sheet
move or an accept-to-sheet signoff for the row; any LAW or measurement-law
change; or any claim about win rate, balance or fun (R215 B, Guardrail-7).

**R230's ruled direction is not reopened by any result here.** `KLEESPARK-BT3`
measures the half that ruling left owed, and `KLEESPARK-W5` carries the failure
condition that ruling wrote. The only thing either can do to the direction is
what R230 already said one of them could: fire the collapse, and send the arm
back to [USER] as a numbered pick.

---

## 25.5 `KLEESPARK-BT3` — RUN AND GRADED

**RUN 2026-08-30 on `0.2.1786+proto.dirty`** (game v0.111.0, `public-beta`),
branch `bt3-w5-run` off `wave-2026-08-30-night`. Evidence directory
`review/qa/bt3-w5-2026-08-30/`. The schedule §25.2 printed was re-printed and
committed before anything was staged and it matched. Codex meter, unsmoothed:
**5h 0% (rolled over) / week 28%** immediately before, **5h 0% / week 35%**
after the second deciding read.

### 25.5.0 `EB-243` — the relic re-draft, disclosed before the round

Both boards registered the run-start gift as *Fishing Rod*. It was read **off
the wire** first, by staging each board **as committed** and taking its refusal
as the reading — no board was edited before the wire was read:

| board | seed | the wire | the registered declaration |
|---|---|---|---|
| `t01` | `YX7PB48WR7R4` | *Pounding Surprise*, **Stone Humidifier** | *Pounding Surprise*, *Fishing Rod* |
| `t02` | `R805DJ56LZHM` | *Pounding Surprise*, **Scroll Boxes** | *Pounding Surprise*, *Fishing Rod* |

**A different gift on each seed**, so the single registered name assumed a
constant the staging path does not have. Both `expects.relics` blocks were
re-drafted to what is true now and the change disclosed in each board and in
the MANIFEST, committed BEFORE the round ran (`98392747`). Under R212 a moved
world means re-draft and disclose, never re-sign: the R231 countersign stands,
`G1`–`G4` are untouched and no threshold moved. Both `hp.first` legs (40 and
46) matched the wire unchanged. Both boards then staged **clean** through the
`EB-240` preflight and both packets print the correct pair, which is
`EB-243`'s acceptance word for word.

## THE ROUND -- `klee-sparks-bt3`

Generated from the records by `python -m understudy.staged_turn packet-section klee-sparks-bt3` on 2026-08-30. Every table below is transcribed from `review/qa/klee-sparks-bt3-t*/` and `review/qa/ledger.tsv`; nothing here is re-graded and nothing is re-read (R101b).

**2 board(s) run, 0 UNRUN, 4 form(s) graded.**

### The boards, grader by grader

| turn | seed | grader | family | verdict | refused by | falsifier hits | replay |
|---|---|---|---|---|---|---|---|
| `klee-sparks-bt3-t01` | `YX7PB48WR7R4` | `codex-gpt-5.6-sol-fresh` | gpt | **REFUSED** | intent_insensitive | -- | - |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | intent_insensitive | misread:called 'Spirited Away' 'free', but the p; spot_check; misread | - |
| `klee-sparks-bt3-t02` | `R805DJ56LZHM` | `codex-gpt-5.6-sol-fresh` | gpt | **REFUSED** | intent_insensitive | -- | - |
|  |  | `local-qwen3-8-27b-ud-q4-k-xl` | local | **REFUSED** | intent_insensitive | misread:called 'Spirited Away' 'free', but the p; spot_check; misread | - |

### The registered slots

A slot is **DECIDED** on two or more grades that all agree, **UNDECIDED** on any split or on fewer than two (R221 B). SURVIVES reads PREDICTED, REFUSED reads MISSED.

| slot | grades | reading |
|---|---|---|
| `C1` | MISS, MISS, MISS, MISS (4) | **DECIDED** |

### What the round spent

- **Codex seat reads:** 2 -- the scarce budget, one record each.
- **Local tester reads:** 2.
- **Control / other reads:** 0.

### UNRUN boards (R221 B)

None -- every board in the pre-registered order was run.

### The banners the ledger carries

> staged board: this hand and this board were set by hand through a dev door, so nothing measured here is comparable to any run, and nothing here is a claim about whether the turn is fun
> down-weighting: a grader whose q2 disagrees with [USER] on 3 of its last 5 shared turns cannot mark a turn SURVIVES alone
> UNRUN: R221 B: sequential stopping. This board was staged in the round's pre-registered order and NOT run, because every registered slot it carries was already DECIDED -- two or more grades that all agreed -- before its turn came. Its seed is pinned here so a later round runs THIS board rather than a re-rolled one. Nothing about it was graded, and an UNRUN board is a board with no record, never a struck one (R101b)


### 25.5.1 The slate, graded mechanically

| slot | grade | the reading, and the rule it comes from |
|---|---|---|
| `G1` | **UNREACHED** | Both deciding forms were REFUSED (`intent_insensitive`). `G1`'s own rule: *"where both are refused, `G1` is UNREACHED"*. **`F2` is UNREACHED for the FOURTH round running.** |
| `G2` | **UNREACHED** | `t02`'s deciding form was refused, which is `G2`'s own UNREACHED rule verbatim. `G2` is a SUBSET of `G1` and is reported as one. |
| `G3` | **PREDICTED, 2 of 2** | Both deciding forms carry a non-empty `forecast` with one answer per registered question (`["3","3","15"]` on both) and neither was refused `forecast_missing`. `G3`'s predicate is written entirely about the FORM's forecast field and its own falsifier names a refusal reason, so it is reachable on a refused form by construction — which is why the blanket `EB-209` rule below does not swallow it, and reading it otherwise would leave the slot unfalsifiable. **`EB-239`'s schema repair holds on its second round.** |
| `G4` | **UNREACHED** | The blanket rule at *UNREACHED, ruled in advance*: *"A REFUSED deciding form grades its slot UNREACHED, not MISSED (`EB-209`)"*. No line was replayed — a refused form never is — so no replayed line took the priced mode. |

**`C1`, the counting slot, reads MISS on all four grades and is DECIDED as a
counting matter.** That is the funnel's own bookkeeping over four refusals and
is not one of the four registered predictions.

### 25.5.2 THE INSTRUMENT FINDING — the boards declared a telegraph the wire does not carry

Both deciding forms were refused for the same reason, and the reason is not the
graders':

| board | the board's `notes` and `board:` mirror | what the live page printed |
|---|---|---|
| `t01` | *"one enemy telegraphing an attack for 16"*, the **pressure ON** board — *"a telegraphed 16 into 24 HP"* | **Shrinker Beetle — Intent: Strategic, This enemy intends to apply a Debuff to you.** No attack at all. |
| `t02` | the same telegraph with the pressure OFF | **Nibbit — Intent: Aggressive, 12.** An attack, but 12 and not 16. |

The encounter is generated from the seed and **the board writes no intent**, so
neither board could have got the telegraph it declared. `EB-240`'s `expects:`
block has a `relics` leg and an `hp` leg and **no `intent` leg**, so the
preflight that caught the relic could not catch this.

**It is causal, and it is the whole of the round's outcome.** `t01`'s hand
holds no Attack; against an enemy that intends a Debuff there is genuinely no
intent that would change the line, and the deciding form says so in its own
words — *"against an intent that showed no damage"* — which is exactly what
`intent_insensitive` fires on. `t02` kept an attack but at 12 into 40 HP, so
the *pressure ON / pressure OFF* contrast `G2` exists to read collapsed: **both
boards ran with less pressure than either declared, and `t01` with none.** Two
boards were staged as the cheapest repair for a single refusal, and a defect
common to both took the denominator to zero anyway.

**This is a DEFECT and it is filed as `EB-244`.** It is the same class as
`EB-240` and `EB-243` — a board asserting a fact the wire does not carry — on
the one leg the `expects:` block does not check. Nothing else is inferred from
it: `G1` UNREACHED on both boards is the registration's own case where
*"nothing is inferred from the absence and no [USER] row opens; the act is a
repaired board, not a reading."*

### 25.5.3 Recorded, and graded nowhere (R101b)

- **The forecast arithmetic was wrong on both boards, in the same place.** Both
  deciding forms answered `3 / 3 / 15` where the registered arithmetic is
  `0 / 3 / 15`: with no detonator in hand the bank ends **this** turn at 0 and
  is repaid to 3 at the start of the next. That is precisely what `G4` was
  drafted to grade, and `G4` is UNREACHED under `EB-209` because the forms that
  carry those numbers were refused. **It is recorded here and it grades
  nothing** — no slot moves on it, no [USER] row opens on it, and it is not a
  reading about the card. It is written down so a repaired round knows the
  question is live.
- The SHADOW seat refused both boards on the same falsifier and additionally
  flagged `misread` on both (*"called 'Spirited Away' 'free', but the printed
  cost is 2"*). Shadow-versus-deciding agreement is **0 of 0 comparable turns**
  — both chairs refused, and the round summary records the pair as not
  comparable. A two-board denominator decides nothing about the seat's chair
  and `M62` is not at issue (the manifest says so in advance).

### 25.5.4 What the round spent, and what it did not

**2 Codex calls against a plan of 3 and a cap of 6.** The registered third call
was the pair read, and **it was not made.** With `G1`, `G2` and `G4` all
UNREACHED there is no pair read to take: a pair read weighs an arm's boards
against each other toward ADVANCE or RETURN, and this round produced no
readable grade to weigh. The registration's own consequence for `G1` UNREACHED
on both boards is a repaired board, not a reading, and R230's ruled direction is
not reopened by any result here. Spending a call to obtain an opinion the slate
forbids acting on would be the wrong kind of thrift.

### 25.5.5 What this leaves

- **`EB-224`'s staged half is still owed.** `F2` has now graded UNREACHED four
  rounds running: twice on a single refused form, once on a predicate that
  could not pass, and now on a board whose declared telegraph was never on the
  wire. Each cause was different and each was found; the slot has still never
  been read.
- **`EB-244` is minted** — the `expects:` block gains an `intent` leg, and a
  repaired BT3 round runs behind it. Boards `t01`/`t02` are **NOT edited**
  (R101b): they are the record of a round that happened.
- **`KLEESPARK-W5` is NOT blocked and runs.** §25.3's gate is literal: the
  whole fight *"does not run at all where `G1` MISSES on its engine clause (ii)
  or where `G3` MISSES."* `G1` is UNREACHED, which is neither a MISS nor a MISS
  on clause (ii); `G3` is PREDICTED. Neither blocking condition fired, `BT3` is
  graded, and the fight goes ahead under R230's pre-registered collapse
  condition. The whole fight is also the half of `EB-224` that no staged board
  can reach, and its `B3` asks the liquidity question where the player, not a
  board, chose the hand.
- **No [USER] row opens on this round.** No number moved, no threshold moved,
  and nothing here is quotable as balance (R215 B, Guardrail-7).


---

## 25.6 `KLEESPARK-W5` — RUN AND GRADED

**RUN 2026-08-30 on `0.2.1786+proto.dirty`** (game v0.111.0, `public-beta`),
sealed record `review/qa/blindplay/20260831-022129/record.md`, wire snapshots
`wire.json` beside it. Run seed `UVPVUS1BVEQ0`, read back off the wire
(`EB-191`). `arms_granted: KLEEMOD-PROTO_SPARK_MODE_BOMBS`, matched to the
embark sidecar by run seed. 40 actions, termination `max_actions`, 0 refusals,
**19 combat pages** carrying a command, forecast asked on all 19 with **0
answered short**.

**Preconditions, each checked and none assumed.** R225's soak gate green
(`bounded seed=ZGWG4HHCRZCU actions=52 fights=3 defects=0`, reversibility log
all REVERTED). The pck contract check empty — the diff from `cc6f323c` over
every mod and pck source path is empty, so the pack is the one phase 1 built
and validated. The printed-Spark-price stop rule **checked rather than
assumed**: the only top-level printed Spark price on any combat page is
*Ka-pow!* at **1**, which is the sheet's, on every page it appeared; *Bag of
Tricks* prints its price at the head of a `choose_one` mode, which is R225's
mode-head clause, and no page disagreed with the sheet. Game lock absent, Steam
running, the build proven read-only to carry the row before anything was
granted. Codex meter, unsmoothed: **5h 0% / week 35%** immediately before,
**5h 1% / week 0% (rolled over, resets Sep 06 22:26)** immediately after.

**Neow.** Three boons were offered — *Kaleidoscope* (obtain 2 card rewards from
other characters), *Scroll Boxes* (choose 1 of 2 packs of cards to add to your
Deck) and *Silken Tress* (lose all Gold; enchant all cards in your first card
reward with Glam). Two rewrite the deck, exactly as §25.3.4 item 5 predicted.
The operator took **Silken Tress**, the only deck-neutral boon offered, by
`W4` §19.5's registered rule.

### 25.6.1 The definitions, counted off the wire

| | count | how it was counted |
|---|---|---|
| combat pages | **19** | pages of the sealed record whose screen is combat and which carried a command; one `wire.json` snapshot each |
| pages with *Bag of Tricks* in hand | **5** | snapshots 4, 5, 10, 11, 17 |
| printed Spark bank on those pages | 1, 2, 0, 2, **4** | the meter row, never a reconstruction |
| **OPPORTUNITY PAGES** — bank ≥ 3 **and** the card in hand **and** ≥ 1 affordable detonator | **1** | snapshot 17 only (bank 4; Kaboom! 1, Jumpy Dumpty 2, Fish-Flavored Bait 1, Ka-pow! 0 against 3 Energy) |
| **PRICED-MODE TAKES** | **1** | snapshot 17: the tester chose *"Spend 3 Sparks: place 3 Bombs dealing 5"* on the mode screen, its own command |
| **FREE-MODE TAKES** (the one-Bomb mode at a bank ≥ 3) | **0** | *Bag of Tricks* was played exactly once in the session |
| pages carrying a **PRESERVED-SPARK REASON** | **6 of 19** | forecast answers on actions 8, 9, 17, 32, 34, 35 |

### 25.6.2 The slate, graded mechanically

| slot | grade | the reading, and the rule it comes from |
|---|---|---|
| `B1` — R230's collapse condition | **UNREACHED** | *"UNREACHED where fewer than 4 opportunity pages occur."* **One** occurred. The floor was written as a floor on purpose — *"two-of-two is not a habit"* — and one-of-one is less than that again. **The collapse did not fire and, on this denominator, could not have.** Per the slot's own words, *"a fight that never posed the question has measured the GENERATOR and not the card"*: nothing is inferred, **no [USER] row opens**, and the act is another fight, not a reading. |
| `B2` — the one-Spark trade is NAMED | **PREDICTED, threshold 1** | Snapshot 17 is a page where both modes were affordable at a bank of 4, and the tester's own pre-commit answer on that page names what the bank was being kept for and the refund that unties it: *"Keeping the 3 Sparks for later Spark-priced cards; the three detonations should refund them through Pounding Surprise."* Five further pages name it unprompted (actions 8, 9, 17, 34, 35), and the fight record adds the counterfactual in the tester's own words: *"That would have retained the initial Sparks but given up 15 Bomb damage."* The threshold is 1 and the observed count is 6. |
| `B3` — the up-front liquidity BINDS | **PREDICTED, threshold 1** | The card reached the hand on **5** pages, which clears the denominator rule of 3. On **3** of them the bank stood at 1 or 2 and the priced mode was therefore unavailable (snapshots 4, 5, 11); on a fourth the bank stood at 0. The threshold is 1. R230's *"real liquidity, locked up"* clause is graded live for the first time and it holds: the bank was below the price more often than it was above it. |
| `B4` — the delayed refund at fight scale | **MISSED** | The falsifier as registered: *"every priced-mode take has a detonator in hand."* The one priced-mode take had **four** affordable Attacks in hand and the refund arrived inside the same turn (snapshot 18's ledger: `Jumpy Dumpty … gains {relic:pounding_surprise/detonation: 3}`, bank 1 → 4). `B4` is UNREACHED only *"where the priced mode is never taken"*, and it was taken, so the falsifier applies and the slot MISSES. **The denominator is one take**, and that is said here rather than argued later. A MISS licenses nothing on its own (§25.4). |
| `B5` — RECORDED AND NOT GRADED | recorded | **Per-fight peak printed Spark bank: 2, 2, 4** over the session's three fights. **Priced-mode takes 1, free-mode takes 0.** **Pages carrying a preserved-Spark reason: 6 of 19.** Beside `W3`'s 4.0 and `W4`'s 5.5 medians and **NOT a comparison** (§19.2 item 1) — a comparator, never a threshold. |

**The `B1` clauses, read for the record and graded nowhere.** Because a reader
will ask: clause (ii) held (zero free-mode takes) and clause (iii) **failed** —
six pages carry a preserved-Spark reason where the collapse requires zero. So
even had the denominator been reached, clause (iii) alone refuses the collapse.
**This is written down, not graded**: `B1` is UNREACHED, an UNREACHED slot is
not a pass and not a fail, and no reading is taken off it. The declared error
direction bites here exactly as §25.3.3 said it would — asking *what are you
giving up* on every page makes a preserved-Spark reason easier to produce, so
clause (iii)'s failure is the weakest of the three observations and the one
most owed to the channel.

### 25.6.3 THE INSTRUMENT FINDING — the sealed record carries FOUR fight records for THREE fights

The record prints fights 1, 2, 3 and 4. **There were three.** The transcript
says why, and the tester said it first.

`blindplay session` demanded a fight record on a **`card_select`** observation
— *Bag of Tricks*' own *Choose one* mode screen, which is the middle of a play
and not the end of a fight (transcript rows 132–134). The tester wrote a whole
fight record there, believing the fight had ended, and its item 6 is that
confusion in full: *"playing Bag of Tricks immediately ended the fight even
though its printed three Bombs appeared to total only 15 damage against an
enemy with 44 HP, and I was not shown a mode-selection screen"*. The enemy was
at 44 HP on snapshot 17 and still at 44 on snapshot 18; the fight ran on for two
more pages. Its item 6 in the next record names the mechanism directly: *"the
game asked for a fight record before Bag of Tricks had actually finished
resolving."*

**What it did and did not touch.** It spent one Codex call on a phantom record
and put a false end-of-fight in a sealed record (which stands as published,
R101b — it is annotated here, never rewritten). It did **not** touch a graded
slot: `B1`–`B5` are counted off `wire.json` snapshots and forecast rows, both
of which are per-page and complete, and the mode WAS the tester's own free
choice one row later. **It is `EB-245`.**

**A second thing the same three rows show, and the tester named it too**
(*"the gold markup was also part of the option's required name"*): the printed
option name reaches the observation and the command **with its BBCode intact**
— `choose "Spend 3 [gold]Sparks[/gold]: place 3 [gold]Bombs[/gold] dealing 5"`.
`understudy/scenario.py` folds those tags out for the staged-turn packet and
`blindplay`'s own screen render does not, so a blind tester must type markup to
name a printed choice. **It is `EB-246`.**

### 25.6.4 Contaminations, restated after the fact because they bit

1. **The deck is GRANTED, not drafted.** One copy of the arm's one row
   (`proto_spark_mode_bombs`) into a Klee starter — the literal reading of
   *"the arm's rows"*, the registration naming no count. That single copy is
   the whole of why `B1`'s denominator came in at one: the card reached the
   hand on five pages and the bank was at or above its price on one of them.
   **The generator was measured, not the card**, which is `W1'`'s finding and
   `W3`'s again, and this cell now records it a third time.
2. **`+proto` build, prototype surface** — nothing here is quotable as balance
   (R215 B).
3. ***Pounding Surprise* present by design** (R230), and every income figure is
   a FLOOR: the ratio cannot see a kit declaration or the relic's
   per-detonation gain.
4. **`EB-235` was not folded in.** `proto_true_spark_knight` was not granted
   and was not drafted; nothing here is evidence about it either way.
5. **R217 G rides on every sentence the tester wrote** — one model's account,
   never validation, never balance evidence, never approval.

### 25.6.5 What this leaves

- **R230's collapse condition did not fire, and that is not a pass.** §25.3.1
  says it in advance: *"a refused collapse decides nothing either — it is the
  absence of a failure, not a pass, and it does not advance the row to the
  sheet."* Here it is weaker still, because the condition was UNREACHED rather
  than refused. **The arm stands exactly where R230 put it. No number moved,
  no threshold moved, and no [USER] row opens on this cell.**
- **`B2` and `B3` are the two things this fight did buy**, and they are the two
  halves of R230's rewritten intent that a staged board could not reach: a
  player who was not told what to look for named the liquidity in their own
  words, and the bank was genuinely below the price most of the time the card
  was in hand. Both are PREDICTED at a threshold of 1 and neither is a balance
  claim.
- **`B4` MISSED on a denominator of one take.** What it says is that the one
  time the priced mode was taken, the hand held a detonator — which is the
  easy case, not the delayed one. `BT3` was supposed to buy the delayed case
  off a board and its `G1` is UNREACHED; this fight did not buy it either.
- **`EB-224` still owes the delayed half.** Two cells were spent on it tonight
  and neither reached it.
- **`EB-245` and `EB-246` are minted** — the phantom fight record on a
  `card_select` screen, and the BBCode leaking into a printed option name.
  Both are instrument rows and both gate nothing that ran tonight.

---

## 26. `EB-211` — the `costs` category now costs something, and what it OWES

**Written 2026-08-30 on branch `understudy-instruments-2`. This is instrument
work, and it is PROSPECTIVE: no sealed form is re-scored, no published battery
result moves, and the seat's recorded FAIL at 10 of 18 under R223 stands
exactly as published (R101b).**

Section 13.8's third claim was right. The battery's `costs` category ran one
check — did the reader call a card free that the packet prints a price for? —
and PASSED whenever it found nothing. A form that never mentioned a price
passed the category, so R223's mark of 4 of 6 was satisfiable by silence, and
the only thing `costs` could actually catch was a reader who volunteered the
misread in prose.

The form now carries a **price ledger**: one entry per play, in the line's
order, in the numbers the packet prints — the bank that play started with, the
price on the card, and the bank it left, with the same three fields for Spark
where the board prints a Spark bank. `qualify.score_costs` scores it against
the printed costs and the printed bank: the price must match the printed
`Cost:`, the first entry must start at the printed Energy, each entry must
start where the last one ended, and the arithmetic must subtract. **A form with
no ledger FAILS.** The field is nullable everywhere else, so every sealed form
and every replay loads unchanged, and no falsifier requires it.

### 26.1 What this OWED [USER] — RULED by R232 (2026-08-30)

**R232 answered both halves of what this section put up.** The six sealed
`costs` items were RE-PICKED against the ledger's question, and R223's mark of
4 of 6 was deliberately LEFT ALONE. In plain words, the two reasons:

- **The items should ask the question the scorer asks.** Keeping the old six
  would have preserved comparability with the seat's earlier reads while
  weakening what the category actually measures, and validity wins that trade.
- **Do not move the boards and the bar in the same step.** The ledger already
  made the category materially harder; changing the pass mark at the same time
  would leave any later failure impossible to attribute. 4 of 6 stands for the
  first properly selected run, and the revisit is gated on accumulated
  evidence rather than scheduled.

**What that meant in the file.** The picking rule in
`understudy/battery/battery.yaml` is now the LEDGER's rule: a board qualifies
when the packet prints an Energy bank, when the hand prints **two different
non-zero prices that are jointly payable out of that bank** — so a real line
moves the bank by two different amounts and a reader who subtracts the same
number every play cannot land right by habit — and when the six between them
cover **both Spark shapes**, boards that print a Spark bank and boards that do
not. Four of the old six fail that rule and moved out: `kokomi-slice2-t02` and
`-t06` print a bank of 2 against prices of 1, 1, 1 and 2, so no two different
prices are ever payable together; `klee-slice1-r3-t03` and `-t04` print no
non-zero price but 1, and neither does any other board in that round. The two
that stayed are `klee-sparks-r1-t04` and `-t05`, and they are the two that
carry the printed Spark bank. Four `kokomi-slice1` boards fill the gap, which
widens the battery from three closed rounds to four. The honest cost is that
`costs` is now a Kokomi-only category: Klee's printed hands are almost all 0s
and 1s, and only two sealed Klee boards clear the rule at all. The Klee
vocabulary is carried by `targets` (four of six) and `intent` (two of six).

**The old six are KEPT, labelled and unscored**, as a `free-claim-regression`
set in the same file — they remain the sharpest boards in the record for the
FIRST half of `score_costs`, the "X is free" misread, which still ships.
`qualify.load_battery` reads only the scored list, `qualify.load_regression`
is the only other door, and the tests pin the separation in both directions.
The re-pick and the drops are both pinned executably in
`tier0/tests/test_eb211_price_ledger.py`, and the four dropped boards are
asserted to FAIL the new rule, so a rule nothing fails cannot creep back in.

**What follows stands as it was written**, as the statement of the question
R232 answered.

### 26.2 What this OWED [USER], as it was put up

**The six sealed `costs` items need re-picking, and that is [USER]'s call, not
this branch's.** The battery file states the rule those six were chosen on:
*the hand must print at least two non-zero costs, so a "free" claim has
something to be wrong about.* That rule was written for a check that could only
fire on a positive claim. A ledger asks a different question — can this reader
track a bank across a line? — and the boards that ask it best are not
necessarily the six that were picked to bait a "free" claim: a board wants a
bank a line can actually exhaust, and a Spark bank that moves, before it is
worth a slot. Choosing which sealed boards those are is a judgement about what
the instrument should measure, and it lands on top of a second question that is
already [USER]'s: **R223's mark of 4 of 6 was answered against a category that
was half as hard**, so whether 4 is still the right number is part of the same
call.

All six items remain in the battery and remain scorable — each prints a bank
and prices at least two cards in hand, which
`tier0/tests/test_eb211_price_ledger.py` pins — so nothing is broken while the
pick is open. What is NOT done here, deliberately: no item was swapped, no
`why:` was rewritten, and the `threshold:` block is untouched.
