# Varka: the combo pass (Pyro burns, Cryo shatters, less Block)

Paper, 2026-10-04. Main session design, from [USER]'s Klee + Varka co-op run
and his friend's notes. Card rows: `docs/prototype-surface.yaml`.

[USER]: "Varka still seems to have too much Block, but the basic loop is
fun! I want to come up with something for Pyro and Cryo - they still didn't
seem impactful compared to Hydro or Electro. Perhaps Pyro cards gain an
Exhaust engine to compliment Electro's draw engine? I recall that Cryo was
supposed to have status-related payoffs, but they didn't come up this game."

## 1. The friend's notes, one by one

| Note | Answer |
|---|---|
| Swirl leaves the original target with no element | **Deliberate.** [USER]'s 2026-10-03 ruling removed "spent" auras: every reaction consumes its aura, Swirl included, and the Swirl tip says "remove it". No change. |
| Charge of the Knights: 1 cost, upgrade 6 to 8 | Agreed in shape. Now 2 cost, 5 [6] per Knight played this combat. **Becomes 1 cost, 5 [7].** A Rare that needs four Knights to reach 20 should not also cost 2. |
| Jean — Lion's Fang, Fair Protector needs a better upgrade | Agreed. Its upgrade is 8 to 9 Block. **Upgrade becomes cost 2 to 1.** (Klee's pool.) |
| Dusty Tome's Four Winds' Ascension should cost 1 | Pick 3: this is his starter card, so it is yours. |
| Unwavering Banner: does it do anything? | It stops non-Knight cards from switching your element, and nothing else: a 1-cost Power that only prevents a loss. **Gains a payoff** (§4). |
| Tailwind Guard undertuned | It is 3 [4] Block per element you have Oath in. Buffing a Block card fights your note, so **it leaves the pool** (§2). |
| Kaeya: Heart of the Abyss and Razor: Awakening look like Attacks | They deal damage and nothing else, so **both become Attacks.** Diluc and Amber: Sharpshooter already are. |
| Thundering Verdict: +1 damage or +1 hits? | Damage. **New text:** "Deal 6 [8] Electro damage, plus 1 for each Electro Oath, to ALL enemies X times." |
| Converging Winds: legacy? | Half. Its job (spread elements react) survived the spent removal, its words did not. **New text:** "The elements your Swirls spread set off Elemental Reactions." Numbers unchanged. |

## 2. Less Block: what the co-op run says

**The evidence.** The run's telemetry
(`%APPDATA%\SlayTheSpire2\gits_telemetry\play-20261004-181026.jsonl`, Varka's
21 fights, a win over the Queen) logs Block gained per turn and the cards
played that turn, not Block per card. A non-negative regression of each
turn's Block on that turn's cards (89 turns, 1,542 Block, R² 0.93) splits it
roughly as follows. These are estimates, not counts.

| Source | Plays | Block per play | Share of 1,542 |
|---|---|---|---|
| Amber: Baron Bunny (C Knight: 6 [8] Block, 6 [8] Pyro to ALL next turn) | 50 | about 6 | about 19% |
| Defend | 35 | about 6 | about 13% |
| Oath of the Knights, at the start of each turn | 22 turns | about 8 | about 11% |
| Gale Mantle (C: 5 [8], plus half your total Oath) | 12 | about 13 | about 10% |
| Lisa: Induced Aftershock (starter Knight) | 31 | about 5 | about 9% |
| Jean — Wind Companion (C: 7 [10] Block, Swirl) | 8 | about 15 | about 8% |

**Oath of the Knights is a problem child, but not the biggest.** The biggest
is volume: Baron Bunny was played 50 times, and the Knight commons with a
Block rider (Baron Bunny, Lisa, Gleeful Songs, Wellspring Hymn, Pulsating
Witch) made about 40% of all his Block. Per play, the worst is Gale Mantle,
which turns any Oath into Block. Varka took no damage in 7 of his last 10
fights, the Queen included.

**What changes:**

| Card | Rarity | Change | Why |
|---|---|---|---|
| Gale Mantle | C | leaves | generic Oath-to-Block, the most per play |
| West Wind Shield | C | leaves | a second generic Block common |
| Knightly Guard | C | leaves | a third: Block, plus Oath after a Knight |
| Tailwind Guard | U | leaves | Block per element (your friend's note) |
| Oath of the Knights | U | leaves | Block equal to Oath every turn |
| Amber: Baron Bunny | C | Block 6 [8] → 3 [4] | the volume; its job is the next-turn Pyro hit |

**Jean — Wind Companion stays** as Anemo's one generic Block common ([USER]:
"we should have one generic Anemo block card"). Eye Wall (U) and Wall of
Gales (R) stay above it. Hydro keeps its Block (Barbara, Rippling Guard,
Tidal Bulwark, Retaliating Tide). The pool stays 78. Lisa: Induced
Aftershock is a starter Knight and is left alone.

## 3. Pyro burns: an Exhaust engine for the big hit

Pyro's job is one very big hit, and it scales with Pyro Oath (Blazing
Charge, Wildfire Oath). Its problem: only Pyro cards grow Pyro Oath, and
there are few of them. Exhaust fixes both. Burning a card is how Pyro grows
its Oath, so a Pyro deck feeds its hit from cards it does not want, Defends
first. That also answers §2 from inside the deck: the Pyro player trades
Block for damage. Electro discards to draw and gain Energy; Pyro exhausts to
build one number. The two never share a payoff.

| Card | Type, cost, rarity | Text |
|---|---|---|
| Stoke the Flames | Skill, 1, C | Exhaust a card. Gain 2 [3] Pyro Oath. |
| Ember Cleave | Attack, 1, C | Deal 9 [12] Pyro damage. Exhaust a card. |
| Pyre Oath | Power, 1, U | Whenever you Exhaust a card, gain 1 Pyro Oath. [Innate] |

- **Yardsticks.** True Grit (Ironclad C, 1: 7 [9] Block, Exhaust a random
  card [chosen]) prices "exhaust as a cost" at about +2 over rate. Ember
  Cleave is 9 for 1 against Strike's 6. Stoke is Vow of the Blade (1 Oath
  and draw 1) with the draw swapped for a second Oath and a burned card.
  Pyre Oath is Feel No Pain's shape (U, 1: 3 Block per Exhaust) paying Oath.
- **The guard.** Nothing here gains Energy or draws, so the loop is limited
  by the cards you hold. The payoff is still one hit a turn.

## 4. Cryo shatters: status payoffs below Rare

The identities paper (2026-10-01, §6) left this owed: Cryo stacks Weak and
Vulnerable (Mika, Kaeya, Glacial Edict, Frost Ward) and its only payoff is
Absolute Zero, a Rare. Two cards, and Unwavering Banner:

| Card | Type, cost, rarity | Text |
|---|---|---|
| Shatter | Attack, 1, C | Deal 5 [7] Cryo damage, plus 2 [3] for each Weak and Vulnerable on the enemy. |
| Deep Freeze | Skill, 1, U | Apply Cryo to an enemy. Double its Weak and Vulnerable. [Retain] |
| Unwavering Banner (reworded) | Power, 1, U | Only Knights can change your current element. Whenever another card would, gain 1 Oath of your current element instead. [Innate] |

- **Yardsticks.** Shatter with nothing on the enemy is 5 [7], under
  Strike; against 1 Weak and 2 Vulnerable it is 11 [16] for 1, and it gets
  there only after two setup cards. Deep Freeze is Catalyst's shape (Silent
  U, 1: double Poison [triple]) on Cryo's statuses.
- The base-game yardsticks in §3 and §4 are quoted from memory of the
  StS1 cards; the build checks each against the game's own code first.
- **Banner** turns "don't lose your element" into a mono-element payoff:
  off-element cards still do their own job and now feed the Oath you are
  building.

## 5. Before the build

`tools/varka_expansion_sim.py` with the five cuts and five adds. The bars
are the identities paper's: each element deck within 10 points of the
default drafter, Pyro and Cryo up, no new card dominant or dead. Then a
two-seat round, and your next Varka run.

## Picks

1. **§2: five generic Block cards leave, Jean — Wind Companion stays, Baron Bunny's Block 6 [8] → 3 [4].** Default: yes.
2. **§3: Pyro's Exhaust engine (Stoke the Flames, Ember Cleave, Pyre Oath).**
   Default: yes.
3. **Four Winds' Ascension's upgrade becomes cost 2 to 1** (in place of +3
   damage and +1 per Oath). This touches his starter. Default: yes.
4. **§4: Shatter, Deep Freeze and the reworded Unwavering Banner.** Default:
   yes.

§1's other rows are card fixes and ship with the build.
