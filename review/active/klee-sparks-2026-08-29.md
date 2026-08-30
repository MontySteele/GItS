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
   `review/active/burst-retirement-2026-08-29.md`. Klee's Burst meter is still
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
`review/active/klee-sparks-r1-sim-2026-08-29.txt`. Flag OFF the shipped economy
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
276 = 88.0%** (`review/active/klee-sparks-r1-sim-2026-08-29.txt`). The review's
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
2. **The shipped automatic Spark rule is still live in the build.** The
   re-author retires it only on acceptance (§6.1), so the fight is played on a
   build where the granted priced rows sit BESIDE the shipped threshold
   discount. That is a contaminant and it runs one way: it makes Sparks *more*
   valuable to hold than the re-authored economy alone would, so a thin
   spend-versus-hold reading here is a floor, not a ceiling.

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
seed, one pilot, a granted deck the generators did not produce, and the shipped
automatic Spark rule still live beside the priced rows (§12.1 item 2).
Guardrail-7: these are floors.

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
selector step"*, `review/active/kokomi-kurage-memory-2026-08-29.md:46`, and the
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
| f1 | Second Pocket adds a discard selector — the run-length UX cost rejected for Kokomi | **PARTLY RIGHT** | `.../sprint-sim-hygiene-log-2026-07-29.md:130`; `review/active/kokomi-kurage-memory-2026-08-29.md:46,127-129,478-481` |
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
