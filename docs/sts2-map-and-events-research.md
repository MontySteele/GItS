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

### 1.1 The comparison that matters

Expected composition of one act, real vs ours:

| | real (17 floors, expected) | ours (`NNNRETN$ERB`) |
|---|---|---|
| normal fights | **~7.9** | 4 |
| **elites** | **~1.0** | **2** |
| rest sites | ~2.6 | 2 |
| unknowns (event/shop/treasure/monster) | **~2.9** | **0** |
| merchants | ~0.7 | 1 |
| treasure | 1 | 1 |
| boss | 1 | 1 |
| **total floors** | **17** | **11** |
| **player choice** | **yes** | **none** |

Read against §1.3.2's HP ledger, where an elite costs the anchor 34 HP and a
normal costs 6:

- We run **twice the elites** of an average real path, and the elite is the
  single most expensive node in the game for us.
- We run **half the normal fights**, which are nearly free (6 HP) and are
  where card rewards and gold come from. So our runs are not merely harsher —
  they are harsher *and* poorer.
- We run **zero unknowns**, i.e. none of the healing, gold, relic and
  card-quality swings that real runs use to recover.
- And the player never chooses, so none of the above can be steered.

This is a straightforward, quantified explanation for §1.3.2 that requires
weakening no enemy.

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

## 4. PROPOSED design (not built — see §6)

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

**Recommendation: (A).** The whole finding is that our *authored* composition
is off (2 elites where the real game averages 1, no unknowns). (B) fixes the
agency half and leaves the composition half authored, so we would be tuning
the fork weights by hand — the same trap as the difficulty dial. (A) costs
more up front and then stops being a source of authored numbers.

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
3. **Elite frequency.** At A0 the real number is 8%/room ⇒ ~1 per act. Ours is
   2, hard-coded. Under (A) this stops being a decision and becomes an
   outcome — worth saying out loud, because it will look like a difficulty
   nerf in the numbers when it is actually a fidelity fix. Guard against
   self-deception here: check elites-faced-per-run against ~1.0, not against
   the winrate.
4. **Gold and shop stock** are both below the real numbers (§1). Fixing them
   is in scope for a map pass or explicitly out; either is fine, deciding by
   accident is not.
