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

## 2. Less Block: five generic Block cards leave

The 2026-10-03 rebalance gave Block to Hydro as its identity. The generic
Block that any deck drafts stayed, and that is the wall: Gale Mantle and
Oath of the Knights turn whatever Oath you built into Block, every turn.
Five cards that are Block for any element leave, and their five slots fund §3
and §4:

| Leaves | Rarity | Why |
|---|---|---|
| Gale Mantle | C | Block plus half your total Oath: generic Oath-to-Block |
| West Wind Shield | C | Block per aura: a second generic Block common |
| Jean — Wind Companion | C | Block and a Swirl; seats' weakest card on 2026-10-03 |
| Tailwind Guard | U | Block per element (your friend's note) |
| Oath of the Knights | U | Block equal to Oath every turn: the wall's engine |

Hydro keeps its Block (Barbara, Rippling Guard, Tidal Bulwark, Retaliating
Tide), and Anemo keeps Eye Wall and Wall of Gales. The pool stays 78.

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

1. **§2: the five generic Block cards leave.** Default: yes.
2. **§3: Pyro's Exhaust engine (Stoke the Flames, Ember Cleave, Pyre Oath).**
   Default: yes.
3. **Four Winds' Ascension's upgrade becomes cost 2 to 1** (in place of +3
   damage and +1 per Oath). This touches his starter. Default: yes.
4. **§4: Shatter, Deep Freeze and the reworded Unwavering Banner.** Default:
   yes.

§1's other rows are card fixes and ship with the build.
