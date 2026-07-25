# StS2 map generation + event research (wiki harvest)

**Status:** RESEARCH NOTES — 2026-07-24. Raw source data for the map/event
extension. Nothing here is a modeling decision; the curated codeable subset
and the plan live in §4–§6 and are marked as PROPOSALS.

Source: slaythespire.wiki.gg, `Slay the Spire 2:` namespace — `Map
Generation`, `Map Locations`, `Acts`, and the 46 individual event pages.
Ascension 0, early-access build current as of 2026-07-24. Harvested through
the MediaWiki API (`action=query&prop=revisions`); the template-stripped
options for all 46 events are committed verbatim alongside this file as
`sts2-events-harvest.txt`, so the curated subset below can be checked against
the source without a second harvest.

**Why this exists:** the act-3 diagnosis
(`tier05-perf-and-ironclad-act3-notes.md` §1.3) found that runs die to the HP
ledger across a roster that is otherwise 99–100% winnable, and that the
suspect is our node composition rather than enemy statlines. This is the
ground truth needed to check that. It **reverses** draft-sim spec §7, which
listed "map pathing/branching" and "events" as non-goals ("their design, not
ours") — user ruling 2026-07-24. That non-goal was right when the run layer
was a card-distribution instrument; it stopped being right when run fragility
became the headline metric.

---

## 1. Map generation (load-bearing)

Every act is **17 floors**, up to **6 rooms per floor** in a roughly
horizontal row. Aside from the first and last floors, each room has **1–3
paths in** from the floor below and **1–3 paths out** to the floor above. The
player picks any room on floor 1, and is thereafter restricted to the edges.

Fixed floors, every act:

| floor (act 1 / 2 / 3) | contents |
|---|---|
| 1 / 18 / 35 | all rooms are **easy-pool** monster encounters |
| 9 / 26 / 43 | all rooms are **Treasure** |
| 15 / 32 / 49 | all rooms are **Rest Sites** |
| 16 / 33 / 50 | the act **Boss** (all routes converge) |
| 17 / 34 / — | Boss Chest (not on the map; act 3 has none) |

Every other room rolls a type independently:

| room type | chance |
|---|---|
| Normal encounter | **53%** |
| Unknown | **22%** |
| Rest Site | **12%** |
| Elite | **8%** |
| Merchant | **5%** |

Ascension 1+ raises elite frequency by ~60%. **A0 is what we model.**

**Unknown rooms** resolve *on entry*, not at generation: the game picks
Monster / Merchant / Treasure / Event, then resets that type's weight to its
baseline and increments the others (a pity system). Weights reset between
acts. The wiki does not publish the baselines or increments — **UNKNOWN
NUMBER, flag it rather than invent it.**

Other structural facts:

- The same elite can repeat within an act, but **never twice in a row**.
- A Rest Site is always placed on the routes leading to the boss (floor 15 is
  all-Rest, which is how that is enforced).
- Rest Site options are **Rest (heal 30% max HP, rounded down)** or **Smith
  (upgrade a card)** — one per site. Same as ours.
- Gold: normal 10–20, elite 35–45, chest 42–53, boss 100. (Ours: 10 / 25 /
  40 treasure / 100. The elite and treasure numbers are low.)
- Elites **always** drop a relic. Elite card rewards have raised rare/uncommon
  odds.
- Merchant stock: 5 character cards, 2 colorless, 3 relics, 3 potions, one
  card removal per shop. (Ours: 3 cards, 1–2 relics, 1–2 potions, one
  removal.)
- Act 1 randomly picks **Overgrowth or Underdocks**. Our `act1_pool.yaml` is
  Overgrowth-based, so Overgrowth is the event list that matches it.

### 1.1 Per-ROOM odds are not per-PATH odds

**Correction, 2026-07-24 (user ruling).** A first pass at this section
multiplied the 8% elite rate by 13 free floors, concluded "a real act has ~1.0
elites versus our 2", and called ours double. **That is wrong**, and the error
is worth naming because it is easy to repeat: the table in §1 is the chance a
**room** rolls a type, and floors are **up to six rooms wide**. Multiplying by
floors silently assumes a one-room-wide map, so it describes a *random walk*,
not a player.

Done properly: 13 freely-typed floors at up to 6 rooms each is roughly 50–78
rooms, of which ~8% — call it **4–6 elite rooms per act** — exist somewhere on
the map. The player's path touches one room per floor, subject to edges, so
how many elites they actually *fight* is a **routing outcome, not a map
statistic**.

**Player-behaviour ground truth (user, domain authority — this is not a
published stat):** elites are where relics come from, so a competent player
hunts them. You take **2 as a matter of course, 3 if the deck can carry it,
and 1 only on a bad map or by deliberately routing around them. 1–4 is the
realistic range; the median is ~2.5.**

So our elite *count* is approximately right — 2 forced, against a realistic
median of 2.5. What we are missing is the **agency**: the real player takes
the third elite because the deck is strong, or ducks to one because they are
at 20 HP. We take exactly two at exactly the same two floors, every run,
regardless.

### 1.2 The comparison that matters, corrected

| | real | ours (`NNNRETN$ERB`) |
|---|---|---|
| walkable floors | **16** (+ a boss chest) | 11 |
| normal fights | **~7.4** | **4** |
| elites **on the map** | ~4–5 | — |
| elites **fought** | **1–4, median ~2.5** (routing) | **2, forced** |
| rest sites | ~2.4 | 2 |
| unknowns (event/shop/treasure/monster) | **~2.6** | **0** |
| merchants | ~0.6 | 1 |
| treasure | 1 | 1 |
| boss | 1 | 1 |
| **player choice** | **yes** | **none** |

Read against §1.3.2's HP ledger (an elite costs the anchor 34 HP, a normal 6),
the gap is **not** elite density — it is everything around the elites:

- We run **half the normal fights**. Those are nearly free at 6 HP and they
  are where card rewards and gold come from. Our runs are therefore not
  merely harsher, they are *poorer*: fewer picks, less gold, a thinner deck
  arriving at the same bosses.
- We run **zero unknowns** — none of the healing, gold, relic and
  card-quality swings a real run recovers with.
- Six fewer floors overall, so what economy we do get is compressed.
- And **nothing is steerable**. An elite at 38/80 HP is a decision in the real
  game and a sentence in ours.

Elite *frequency* is close to right and should be left alone. The fix is the
missing 6 floors of economy and the agency to spend them.

### 1.3 The acceptance check this hands us

The player-behaviour numbers above are a **falsifiable routing target that
touches no enemy statline**:

> median elites fought per act ≈ **2.5**, full range **1–4**, and the count
> must *respond to run state* (a healthy deck takes more, a hurt run takes
> fewer).

That last clause is the real test. A route policy that always takes 2 hits the
median and is still wrong. Report the distribution and its correlation with
arrival HP, not the mean.

Note the trap, given the history in this branch: moving from 2 forced elites
to a routed 1–4 will move the winrate, and it will *look* like the difficulty
nerf that was already vetoed. It is not one — but the way to know that is to
check elites-fought against the 2.5 median and the response-to-state clause,
**not** to check whether the winrate improved.

---

## 2. Events — the full list

46 events. Act 1 = Overgrowth (16) or Underdocks (14); Act 2 Hive (21); Act 3
Glory (14); 4 appear in all acts. Several appear in more than one act (Brain
Leech, Room Full of Cheese, Tea Master, Crystal Sphere, Potion Courier, Ranwid
the Elder, Relic Trader, Symbiote, The Merchant???).

Below: the **Overgrowth + all-acts** set (act 1, matching our pool) and the
Hive/Glory sets, with outcomes exactly as the wiki states them.

### 2.1 All acts

| event | options |
|---|---|
| Self-Help Book | Enchant a card with Sharp 2 / Nimble 2 / Swift 2; Move On (only if no valid card) |
| Slippery Bridge | **Overcome**: a specific card is removed from your deck. **Hold On**: lose 3 HP, the offered card is re-randomized |
| The Future of Potions? | Spend a potion of a named tier → an **Upgraded** card reward (rarity scales with the potion's tier) |
| This or That? | **This**: lose 6 HP, gain 57 gold. **That**: add Clumsy (curse), obtain a random relic |

### 2.2 Act 1 — Overgrowth

| event | options |
|---|---|
| Aroma of Chaos | Transform a card / Upgrade a card |
| Brain Leech | Choose 1 of 5 random cards to add / lose 5 HP + a card reward |
| Byrdonis Nest | **Eat the Egg**: +7 max HP. **Take the Egg**: quest card |
| Dense Vegetation | Trudge On (nothing) / **Rest**: heal a rest-site amount, then fight 4 Wrigglers |
| Jungle Maze Adventure | **Solo**: 135–165 gold, lose 18 HP. **Join Forces**: 35–65 gold |
| Luminous Choir | Remove 2 cards + add Spore Mind (curse) / pay 99–149 gold → random relic |
| Morphic Grove | **Group**: lose ALL gold, transform 2 cards. **Loner**: +5 max HP |
| Room Full of Cheese | **Gorge**: choose 2 of 8 random cards (no duplicates). **Search**: lose 14 HP → The Chosen Cheese (relic: +1 max HP at end of combat) |
| Sapphire Seed | Heal 9 + upgrade a card / enchant a card with Sown |
| Tablet of Truth | **Smash**: heal 20 HP. **Decipher**: lose 3 max HP, upgrade a random card — escalating stages (−6, −12, −24 max HP; stage 5 costs all but 1 max HP and upgrades the WHOLE deck). Give Up at any stage |
| Tea Master | Bone Tea (50 gold): upgrade your starting hand next combat. Ember Tea (150 gold): +2 Strength at the start of the next 5 combats. Tea of Discourtesy (free): 2 Dazed into next combat's draw pile |
| The Legends Were True | **Nab the Map**: Spoils Map quest card. **Slowly Find an Exit**: lose 8 HP, 1 random potion |
| Unrest Site | **Rest Anyways**: heal to FULL, receive Poor Sleep (curse). **Kill the Trees**: lose 8 max HP → random relic |
| Wellspring | **Bottle**: 1 random potion. **Bathe**: remove 1 card, add Guilty (curse) |
| Whispering Hollow | Lose 50 gold → 2 random potions / lose 9 HP → transform a card |
| Wood Carvings | Transform a starter into Peck / enchant with Slither / transform a starter into Toric Toughness |

### 2.3 Act 2 — Hive (selected; full list in the raw archive)

Amalgamator (2 Strikes → Ultimate Strike; 2 Defends → Ultimate Defend) ·
Bugslayer (add Exterminate or Squash) · Colorful Philosophers (3 cards of
another character's colour) · **Colossal Flower** (escalating: 35 gold / −5 HP
→ 75 gold / −6 HP → 135 gold / −7 HP → Pollinous Core) · Crystal Sphere
(Divine) · **Doll Room** (random Doll relic / −5 HP pick 1 of 2 / −15 HP pick 1
of 3) · Field of Man-Sized Holes · Infested Automaton (random Power card /
random 0-cost card) · Potion Courier · Ranwid the Elder (trade a potion or 100
gold for relics) · Relic Trader · **Spirit Grafter** (heal 25 + add
Metamorphosis / −9 HP, remove 1 card) · Stone of All Time · Symbiote · The
Lantern Key (100 gold / fight for a quest card) · **The Lost Wisp** (Decay
curse + Lost Wisp relic / 45–75 gold) · Welcome to Wongo's (relic shop at 100
/ 200 / 300 gold; Leave downgrades a random card) · **Zen Weaver** (50 gold: 2
Enlightenment / 125: remove 1 card / 250: remove 2 cards)

### 2.4 Act 3 — Glory (selected)

**Battleworn Dummy** (fight a 75 / 150 / 300 HP dummy within 3 turns for a
potion / 2 upgrades / a relic) · Grave of the Forgotten · **Hungry for
Mushrooms** (Big Mushroom relic / Fragrant Mushroom: −15 HP, upgrade 3 random
cards) · **Reflections snoitcelfeR** (downgrade 2, upgrade 4 / duplicate the
ENTIRE deck + Bad Luck curse) · **The Round Tea Party** (Royal Poison relic +
heal to full / −11 HP + random relic) · The Trial · Tinker Time · War
Historian, Repy

---

## 3. What we can code TODAY vs what needs a new op

Classified against the ops the run layer already has (HP, max HP, gold, add /
remove / upgrade a card, grant a relic, grant a potion, run an extra fight):

**Fully codeable now (7 for act 1, enough for a pool):**

| event | why it is clean |
|---|---|
| Jungle Maze Adventure | pure gold/HP tradeoff — the archetypal "do I pay HP for economy" |
| Tablet of Truth | heal 20 vs max-HP-for-upgrades ladder; the escalation is a loop over existing ops |
| Brain Leech | card add vs HP-for-a-reward-screen |
| Room Full of Cheese | 2-of-8 card pick vs HP-for-a-relic |
| Dense Vegetation | free pass vs heal-then-fight (needs one Wriggler statline) |
| The Future of Potions? | spend a held potion for an upgraded card |
| Slippery Bridge | targeted removal vs 3 HP to re-roll it |

**Needs ONE new op each — and two ops unlock most of the list:**

- **`transform`** (remove a card, add a random one of the same rarity):
  unlocks Aroma of Chaos, Morphic Grove, Whispering Hollow, Wood Carvings,
  Symbiote. Trivial given `rewards.character_pool`.
- **`curse`** (a permanent, unplayable card in the DECK): unlocks This or
  That?, Luminous Choir, Unrest Site, Wellspring, The Lost Wisp, Reflections.
  The engine already has unplayable status cards (`engine/statuses.py`); a
  curse is that machinery made deck-persistent instead of combat-scoped. It is
  also the honest way to price the "heal to full" options, which are otherwise
  free money.

**Not codeable, skip loudly (§10.9 backlog):** everything built on
**Enchant** (Self-Help Book, Sapphire Seed, Wood Carvings' snake, Field of
Man-Sized Holes, Grave of the Forgotten, Stone of All Time), **Divine**
(Crystal Sphere), **quest cards** (Byrdonis Nest, The Lantern Key, The Legends
Were True, War Historian), **Debt**, and cross-character card pools (Colorful
Philosophers).

---

## 3.4 SHIPPED (§11, 2026-07-24) — the map is live

`RUNTEMPLATE_VERSION 6`. The fixed spine is gone: every act generates a map,
a route policy walks it, Unknown rooms resolve at entry, and 55% of those are
events. **Every archived run-layer number is uncomparable across this
boundary** — total, not partial, unlike v4→v5.

New modules: `maps.py`, `route.py`, `events.py`, `content/events.yaml`,
`tier0/content/cards/curses.yaml`. New CLI: `--route`, `--route-ab`.

### 3.4.1 What moved, with no enemy touched

400 runs, seed 11, realistic, `hunter`:

| | v5 spine | v6 map |
|---|---|---|
| ref_ironclad act-1 clear | 42.8% | **61%** |
| ref_ironclad act-2 clear | 16.2% | **26%** |
| ref_ironclad win | 2.8% | **5.0%** |
| klee win | 5.0% | 6.5% |
| furina win | 14.0% | 12.2% |
| kokomi win | 1.8% | 4.5% |

The act-1 wall softened by ~18 points because the run finally has the normals,
the unknowns and the agency a real act has — not because anything got weaker.

### 3.4.2 Two findings the route A/B produced immediately

`--route-ab`, ref_ironclad, 400 runs each:

| | hunter | cautious |
|---|---|---|
| winrate | 5.0% | **6.8%** |
| elites/act (mean, median) | 1.27, 1 | 0.18, 0 |
| responds to state | 1.28 healthy → 1.00 hurt | flat (already at the floor) |

**1. Elite relics are underpriced — ducking elites wins more.** `route.py`
called this in advance: "if [cautious] wins outright that is itself the
finding". It did. Either elite relics are worth too little or elites cost too
much HP; that is a real balance question and it is now measurable.

**2. Realised elite count is 1.27, against the 2.5 target — and that gap is
the HP economy, not the policy.** On a healthy run `hunter` reaches 2.3
(pinned in `test_maps_and_routing.py`). In a live run it manages 1.27, because
the run sits around 37% HP and hunter's affordability bar correctly refuses
the third elite. **Do not "fix" this by lowering the bar.** Forcing the count
to 2.5 would manufacture the target instead of measuring it; the honest read
is that our runs cannot afford the elites a real player takes, which is the
same HP-ledger thread the act-3 diagnosis (§1.3.2) landed on — now with an
instrument attached.

### 3.5 Deliberate gaps

- **Acts 2-3 event pools are empty.** Act 1 is the pilot for the grammar; the
  Hive and Glory lists are catalogued in §2 but not authored. An Unknown in
  acts 2-3 that rolls "event" finds an empty pool and passes.
- **No `route_regret`.** The A/B ships; the road-not-taken sampler does not.
- **Events that start a fight** (Dense Vegetation, Battleworn Dummy, The
  Lantern Key) are deferred — resolving combat inside an event would hand the
  event layer the pilot, relics and the potion bag, and that coupling wants
  its own pass.
- **Enchant / Divine / quest cards / Debt** remain skip-loudly (§3).

## 3.6 Build log (§11 milestone, 2026-07-24)

`tier05/maps.py` + `tier05/route.py`, with `tier05/tests/test_maps_and_routing.py`.
**Not yet wired into `model.run_one`** — the run layer still walks the fixed
template. Events are not built.

**One finding worth keeping.** Two generator/policy designs were tried and
both failed the §1.3 target before the third worked:

| attempt | elites fought (healthy) | P(0 elites) |
|---|---|---|
| per-floor width rolls + centred edge spans, greedy next-room policy | mean 2.02 | 8.8% |
| **path-carved** map, greedy next-room policy | mean 1.38 | **23.2%** |
| path-carved map, **whole-map planning** policy | **mean 2.31** | **3.0%** |

The first design was lane-locked, and widening floors did not help — the tell
that *connectivity*, not room count, was binding. Path-carving fixed the map
and made things worse, which localised the real bug: **a next-room-only policy
cannot route toward an elite three columns away.** "Path-hunting" is exactly
the act of reading the whole map and committing to a lane several floors
early, so the policy plans the full path by backward induction over the DAG
and re-plans every floor as state changes. Both route policies got the
planner; what differs between them is what they *value*, which is what makes
the A/B about preferences rather than eyesight.

Measured path composition (400 maps, healthy run):

| | target | `hunter` | `cautious` |
|---|---|---|---|
| normals | ~7.4 | 5.8 | 6.6 |
| elites | median ~2.5 | **2.3** | 0.4 |
| rests | ~2.4 | 1.6 (→ **2.4** when hurt) | 1.4 |
| unknowns | ~2.6 | 3.3 | 4.9 |
| shops | ~0.6 | 1.0 | 0.8 |

`hunter` lands on the elite target and **responds to state** — the run that
gets hurt drops to 1.5 elites and picks up a whole extra rest, which is the
clause that makes the target meaningful. `cautious` deliberately brackets
*below* the realistic floor of 1: it is not a model of a cautious player, it
is the other end of the confounder check.

Honest gaps: `hunter` runs ~1.5 normals light against expectation (it spends
floors on elites and unknowns instead), and neither policy has `route_regret`
yet.

## 4. Design (A = RULED; §3.5 has what is built)

### 4.1 Two fidelity levels, pick one

**(A) Real map generator.** Generate the actual 17-floor DAG per act: 6-wide
floors, 1–3 edges, the fixed floors of §1, the §1 room-type table, the
no-back-to-back-elite rule, and Unknown resolved on entry. A route policy
walks it. Highest fidelity, and it makes elite frequency, rest frequency and
event exposure *emergent* rather than authored.

**(B) Choice points on the existing template** (the user's sketch): keep a
linear spine, insert 2–3 forks per act ("campfire or elite"), fire an event
after each. Much smaller change, keeps every existing metric's shape, but the
composition stays authored — which is the thing §1.3.2 says is wrong.

**RULED: (A)** (user, 2026-07-24). The finding is that our *authored*
composition is off — half the normals, no unknowns, six missing floors — and
that nothing is steerable. (B) fixes the agency half and leaves composition
authored, so we would be hand-tuning fork weights: the same trap as the
difficulty dial. Under (A) the composition is generated and the elite count
becomes an outcome of routing, which is exactly what §1.3 gives us a target
for.

### 4.2 The route policy is a new confounder — treat it like the drafter

Adding pathing adds a **second policy** whose quality is confounded with every
finding, exactly as draft-policy quality was (spec §0's pre-registered
confounder). It needs the same countermeasures from day one:

- at least two distinct route policies (e.g. *greedy-safe*: prefer rests and
  avoid elites; *greedy-value*: prefer elites and shops for relics/gold), and
- every headline finding must survive the A/B, and
- a `route_regret` instrument analogous to `draft_regret`.

Without this, "runs got better" is unfalsifiable — it could just be that the
route policy is good at ducking elites.

### 4.3 Blast radius, honestly

`RunResult.node_kinds` becomes **variable per run**. That breaks two things
that assume a shared template: `run_metrics.act_funnel` (derives act length
from `len(node_kinds) // n_acts`) and the death heatmap (indexes
`results[0].node_kinds`). Both need to move from node index to **floor
index**, which is the more meaningful axis anyway. `RUNTEMPLATE_VERSION` goes
to 6 and **every archived run-layer number becomes uncomparable** — the same
discipline as the v4→v5 boundary.

---

## 5. Open numbers to resolve before building

1. **Unknown-room resolution weights.** The wiki gives neither the baselines
   nor the pity increments. Options: pick a defensible split and stamp it as
   OPEN (the `SHOP_CARD_OFFERS` precedent), or measure from a real run log.
   Do not silently invent one.
2. **Event pool composition.** Do we ship only the 7 fully-codeable events, or
   add `transform` + `curse` first and ship ~20? The second is better content
   but it is two new ops plus a curse-card class.
3. **Rooms per floor.** The wiki says only "up to six" and publishes no
   distribution. It matters: it sets how many elites exist to route toward,
   and therefore whether the §1.3 target (median 2.5, range 1–4) is even
   reachable. Pick a width distribution, stamp it OPEN, and tune it against
   that target — that is calibrating the MAP against player behaviour, not
   calibrating enemies against a winrate.
4. **Elite frequency is NOT an open number.** 8%/room stands as generated; the
   count fought is a routing outcome with a target of median ~2.5 (§1.3). Do
   not "fix" it by changing the 8%.
5. **Gold and shop stock** are both below the real numbers (§1). Fixing them
   is in scope for a map pass or explicitly out; either is fine, deciding by
   accident is not.
