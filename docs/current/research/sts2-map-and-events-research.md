# StS2 map generation + event research (wiki harvest)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

> # MIXED WORLD — DO NOT QUOTE UNLABELLED
>
> **This doc accreted across three run-layer worlds and its sections do not
> agree with each other.** Current world: **RUNTEMPLATE 7 / CONSTANTS 4 /
> DRAFTER 13** (DRAFTER 13 accepted 2026-07-29, R87). Section by section:
>
> | section | world | how to read it |
> |---|---|---|
> | §1–§2 (map generation, event catalogue) | world-neutral wiki research | Live, with one caveat: the §2 catalogue was **re-harvested** during the §3.7 work (namespace-prefix bug) — trust §2 as re-harvested, and `sts2-events-harvest.txt` as the raw source. |
> | §3–§3.3 (what we can code today) | pre-build, RUNTEMPLATE 5 era | Historical. Its "needs a new op" triage was largely resolved by §3.4/§3.7. |
> | §3.4–§3.6 (the map goes live) | **RUNTEMPLATE 6** | Superseded by §3.7. Its numbers were declared uncomparable by the very next bump. |
> | §3.7 (acts 2–3 event pools) | **RUNTEMPLATE 7** — current | The only section whose stamp matches today's world. Numbers still predate DRAFTER 11/12/13, so run-layer figures need re-measurement before quoting. |
> | §4–§5 (design, open numbers) | written pre-build | Proposals. §4.3 discusses "RUNTEMPLATE_VERSION goes to 6" as *future*; it has gone to 7. |
>
> Both bumps declared **every archived run-layer number uncomparable across
> the boundary** (§3.4, §3.7), so no winrate or act-clear figure below §3.7
> describes a world that exists.
> Banner added 2026-07-29 by the doc de-drift pass (`docs/backlog-2026-07-29.md` §2).

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
  (upgrade a card)** — one per site. ~~Same as ours.~~
  **Correction, 2026-08-13 (EB-110):** "Same as ours" was false when
  published. Ours rounded — `round(0.3 * max_hp)` — where the authority
  truncates through `SetCurrentHpInternal`
  (`CurrentHp = (int)Math.Min(amount, MaxHp)`). 36 of the 80 max-HP values
  in 40..119 diverged; Klee (62 max HP) healed 19 against the game's 18.
  The sim now floors, so the struck claim reads true from this date forward.
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

> **STALE IN PLACES — see §3.7.** This section was written from the 2026-07-24
> harvest, which queried the wiki without the `Slay the Spire 2:` namespace
> prefix and so pulled partial pages. §2.3 and §2.4 are the worst affected:
> The Trial and Tinker Time appear here with no options because the harvest
> returned none, and Ranwid, Relic Trader, Potion Courier and Stone of All
> Time are mangled. The count below (46) is also short: the real category has
> **57** StS2 events, the extra 11 being Underdocks. `docs/sts2-events-harvest.txt`
> was re-harvested on 2026-07-25 and is the authority where the two disagree.

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

## 3.7 SHIPPED (§11.2, 2026-07-25) — acts 2-3 have event pools

`RUNTEMPLATE_VERSION 7`. The Hive and Glory pools are populated, and two
valuation bugs found while populating them move act-1 numbers as well, so v6
event numbers do not carry across.

**The catalogue in §2 was re-harvested first, and it needed to be.** The
original harvest hit `slaythespire.wiki.gg` without the `Slay the Spire 2:`
namespace prefix, so it was template-stripped from partial pages: The Trial
and Tinker Time came back with **no options at all**, and Ranwid, Relic
Trader, Potion Courier and Stone of All Time came back mangled. §2.3/§2.4 were
written from that. The re-harvest (58 pages, options + effects for every named
card and relic) is what made the classification below trustworthy — and it
turned The Trial, which the old harvest showed as empty, into the best event
in act 3.

### 3.7.1 What shipped

| act | own events | reachable pool |
|---|---|---|
| 1 (Overgrowth) | 11 | 14 |
| 2 (Hive) | 3 + 2 shared | 8 |
| 3 (Glory) | 2 | 5 |

New act-2 content: **Colossal Flower** (the gold ladder, bottoming out in
Pollinous Core), **Infested Automaton** (two filtered forced draws),
**Bugslayer** (two authored colorless cards). New act-3 content: **The Trial**
(one event, three randomly-selected sub-trials, six verdicts, three new
curses) and **Reflections snoitcelfeR** (downgrade-then-upgrade, or double the
deck and eat Bad Luck).

Brain Leech and Room Full of Cheese now correctly appear in act 2 as well
(`also_acts`) — the wiki lists both as Overgrowth + Underdocks + Hive.

New grammar: `also_acts`, `variants`, `add_card`, `random_card` (type/cost
filtered, and the option LOCKS when nothing matches), `downgrade_random`,
`duplicate_deck`, `card_screens`, `relic: N`, `relic_id`.

### 3.7.2 The no-substitution rule, and what it cost

The §11 pool contains one flagged substitution (Room Full of Cheese grants a
generic relic where the real event grants The Chosen Cheese). Acts 2-3 would
have needed **six more** of those, at which point a flagged exception becomes
an unflagged norm. So the rule is now explicit: **an event that pays out a
named relic we cannot express exactly does not ship.** An event relic is
admitted only when its published effect maps onto a hook the engine already
honors — no new hooks, no approximations.

Exactly one relic clears that bar: **Pollinous Core** ("every 4 turns, draw 2
additional cards" → `every_n_turns_draw {n: 4, amount: 2}`, exact).

The cost is Glory. Five of act 3's eight events pay out in a named relic, so
act 3 ships two events rather than six. `content/events.yaml`'s skip list now
carries the **specific missing mechanic per event** rather than a category, so
it reads as a backlog with per-item prices. The cheapest four:

| event | what it needs |
|---|---|
| Hungry for Mushrooms | a reduced OPENING hand (`combat_start_draw` ignores negatives, and a negative draw is not a discard) |
| Room Full of Cheese | `post_fight` returning max_hp — this retires the one existing substitution |
| The Lost Wisp | an on-card-played combat hook (8 AoE per Power played) |
| Doll Room | three hooks, plus a "choose 1 of N relics" op — `ancient_pick` is already the valuation it would use |

Two more are blocked on **published numbers**, not on engineering: Royal
Poison's effect text is simply absent from the wiki (its Interactions section
proves it causes HP loss; the magnitude and trigger appear nowhere), and
Ultimate Strike / Ultimate Defend carry their numbers only in a card infobox
the API does not render. Guessing either would be inventing content.

**One stale skip reason was caught and corrected.** `juzu_bracelet` was
skipped with "no ?-room / non-combat events exist in the run model" — true
when written, false the moment §11 shipped Unknown rooms. The real gap is
narrower: held relics have no channel into `maps.resolve_unknown`. A stale
skip reason is precisely the quiet lie the skip list exists to prevent.

### 3.7.3 Two valuation bugs, both found by act-2 content

**1. Escalating ladders were unreachable content.** `option_value` scored each
option in isolation, so Colossal Flower's "Reach Deeper" (lose 5 HP, gain
nothing, open the next rung) scored as a pure −5 and the policy could never
climb. Levels 2 and 3 were dead. Options are now valued **through** the
escalation — the immediate effect plus the best reachable value of the next
stage, which is what a player reading the next screen computes and has no free
parameter. Tablet of Truth carried the same latent bug in act 1; with
lookahead it climbs one rung and stops, which is where the max-HP price
overtakes the upgrade.

**2. `GOLD_PER_HP` contradicted its own derivation by ~2×.** It shipped at
`4.0` with the comment "a shop card is 60 gold; ~15 HP of value" — a card
worth 15 HP, four lines above `CARD_HP = 8.0`. The shop is the game's own
published exchange rate and two of its three prices agree exactly:
`SHOP_CARD_PRICE 60 / CARD_HP 8 = 7.5` and `SHOP_RELIC_PRICE 150 / RELIC_HP
20 = 7.5`. (Removal implies 12.5, but 75 is a base that rises 25 per use, so
it is not a clean read — recorded, not averaged in.) Corrected to **7.5**, the
derivation, not a target. Every "pay HP for gold" option in the pool was
mispriced in the same direction; Jungle Maze Adventure now declines 18 HP for
150 gold, which is the marginal trade it should be.

`test_events_acts23.py::test_gold_rate_matches_the_shops_own_prices` pins the
derivation so the file cannot silently contradict itself again.

### 3.7.4 Roster under v7

400 runs, seed 11, realistic, `hunter`:

| | v6 | v7 |
|---|---|---|
| ref_ironclad | 5.0% | **6.8%** |
| klee | 6.5% | 5.5% |
| furina | 12.2% | **16.8%** |
| kokomi | 4.5% | 5.2% |

Moves in both directions, which is the point: this was not a blanket buff.
Klee falls because the corrected gold rate makes her HP-for-gold events a
worse deal, and act-2 events are a net cost as often as a gift.

Event coverage, 600 runs: **2.79 events per run**, every act represented, and
the whole pool reachable (the rarest, `reflections`, fires 47 times).

### 3.7.5 The finding: relics are underpriced, now from two directions

The §11 route A/B said elite relics are underpriced because ducking elites
wins more. Under v7 that gap **widened**, and a second, independent instrument
now says the same thing.

| | hunter | cautious |
|---|---|---|
| winrate (v6) | 5.0% | 6.8% |
| winrate (v7) | 6.8% | **9.5%** |
| elites/act | 2.38 total, 1.35/act | 0.45 total, 0.19/act |

And in the event layer: the Colossal Flower ladder is climbed to level 3 in
81 of 82 visits — and then takes the **135 gold over Pollinous Core, 81 times
out of 81**. The relic is authored, exact, and reachable, and the policy
declines it every single time.

These are genuinely independent. The route A/B is an *outcome* measurement
that never consults `RELIC_HP`; the Colossal Flower split is a *valuation*
measurement that consults nothing else. They agree.

Two readings, and this pass does not distinguish them:

- **The pilot is worse than a real player**, so elites cost more HP than they
  should, and relics cannot pay that back. This is the user's reading and it
  fits: the old single-path spine forced ~2 elites per act on every run, which
  under this hypothesis was making every deck look worse than it is.
- **Our relics are genuinely weaker than StS2's.** The pool is common-tier
  only — no boss relics — and the skip list holds real ones.

The discriminating experiment is a *relic-value* A/B rather than a route one:
hold routing fixed and vary what a relic is worth. `tools/archive/roster_scale_gap.py`
and `tools/encounter_audit.py` are the instruments for the first reading;
the second wants the relic pool audited against the wiki the way the events
just were. **Neither is a licence to raise `RELIC_HP` until the numbers
look better** — that constant is derived from the shop price and moving it
would break the derivation the test now pins.

### 3.7.6 Limitations, stated

- **The event policy is one-sided in 17 of 21 events.** Only Unrest Site,
  Luminous Choir, Whispering Hollow, The Future of Potions and The Trial's
  variants show a real split; everywhere else the greedy valuation picks the
  same option every time. Many real events do have a dominant option, so this
  is not automatically wrong — but it means the event layer contributes less
  decision variance than its size suggests.
- **Bugslayer's choice is near-arbitrary.** Both options add a named card
  valued at a flat `CARD_HP`, and the drafter tiebreak's static-power term
  saturates for both Exterminate and Squash. The cards are exact; the pick
  between them is not modelled.
- **Exterminate and Squash have no upgrade paths**, so no rest site or Tablet
  of Truth improves them. That is a penalty versus the real game — the safe
  direction — and it is one upgrade-sheet entry from being exact.
- **Shame and Doubt ship as plain clogs.** Both list a second keyword (Frail /
  Weak) in their infobox with no rules text anywhere saying when it applies.
  Both are therefore SOFTER than real, the same direction as Decay. Regret has
  no rider and is exact.
- **Brain Leech's card reward should be colorless.** We have no colorless loot
  pool, so it draws from the character pool: shape right, colour wrong.

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
