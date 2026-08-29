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
   independent seat made in `review/active/klee-slice-1-2026-08-29.md` §6.2,
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
