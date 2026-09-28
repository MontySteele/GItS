# Nahida: the Seeds of Skandha (paper kit)

**Ask ([USER], 2026-09-28):** paper kits for Nahida, Zhongli and Varka that
assume the element changes. "Dendro is probably overdue for proper support",
and Nahida "seems like a decent test case for 'first Dendro.'"

**Stage:** Paper. A concept, not yet a brief. Card numbers are placeholders
for the sim.

## 1. The promise

Nahida learns the room. Plant Seeds in your enemies' minds, and when anything
reacts on one of them, all of them feel it.

## 2. Her element: Dendro, the first new aura

Dendro is an aura element, and its rules are already ruled
(`review/ruled/dendro-boundaries-2026-09-06.md`):
- **Bloom** (Dendro and Hydro) leaves a **Core** that bursts for 6. A Pyro hit
  on it makes Burgeon, to every enemy; an Electro hit makes Hyperbloom, 12 to
  one enemy.
- **Quicken** (Dendro and Electro): for two turns, Electro and Dendro hits deal
  +3.
- **Burning** (Dendro and Pyro): a tick that holds a Pyro aura up.
- **No reaction:** Anemo, Geo and Cryo do not react with Dendro.

**She is a catalyst:** every one of her Attacks paints Dendro, at low numbers
(`LAW.md` §Combat, application cadence).

**She meshes with every kit we have:** Bloom with Kokomi and Furina, Burning
with Klee. In co-op she is the partner who makes the others' reactions spread.

**Element changes she needs:** the whole Dendro engine (the aura, Bloom and its
Core, Quicken, Burning, previews), built as that paper describes. The Swirl and
Crystallize changes do not touch her, because Dendro is never swirled or
crystallized.

## 3. The signature: Seeds and Purification

- **Seed:** a counter on an enemy, up to 3 on one enemy.
- **Purification:** every seeded enemy takes **2 Dendro per Seed** on it. It
  fires two ways:
  1. **A card that says Purify.** These are her own cards, like Klee's Set off.
  2. **The first reaction on a seeded enemy during each card you play.**
     Genshin's Tri-Karma has a cooldown; "once per card" is ours.
- **The bound:** a reaction that Purification itself sets off never fires
  Purification again.

**The tension is where the Seeds go:**
- **Spread** them across a pack to hit everything.
- **Stack** them on a boss to hit it hard.
- **Or place them on the attacker** that the Foresight archetype defends
  against (§5).

A lone boss is not a dead fight: three Seeds on one body is a 6-damage
Purification.

Purification is a Dendro hit, so it paints Dendro on every seeded enemy. The
whole room is then ready for the next colour, whoever brings it.

## 4. Solo, and her first colour

A reaction-centred character needs a dependable second element (the element
review, §1). Nahida's engine works without one: Seeds plus Purify cards are a
multi-target damage engine in a mono-Dendro deck. Reactions make it free and
frequent, and they are the ceiling rather than the floor. So by default her
starter holds **no companion**, and she drafts her second colour like Klee.

**Where her companions come from is the real cost.** `LAW.md` says a character
from a nation with no sheet "sits in their nation of operation until their
home sheet ships". Nahida's nation, Sumeru, has no companion sheet. Pick 2.

## 5. The three archetypes

1. **The Seedbed (default, mono-Dendro).** Seed cards and Purify cards. The
   decision is placement: wide or deep.
2. **Tri-Karma (the ceiling, draft-gated).** A second element makes reactions
   fire Purification for free, and each colour plays differently:
   - **Hydro** grows Cores on seeded enemies. A Core bursting counts as a
     reaction, which is canon.
   - **Pyro** sets the room Burning.
   - **Electro** Quickens it for many small hits.
3. **Foresight.** Seeds as sensors: a seeded enemy's attacks deal 1 less per
   Seed, and a Common draws a card when a seeded enemy attacks you. This is
   her mind-reading. It makes placing a Seed on the biggest attacker a
   defensive choice that competes with the offensive ones.

**Bridges:** Foresight Seeds are also Purification targets, so defence is also
damage. A Seedbed deck that drafts one Hydro companion is already halfway to
Tri-Karma.

## 6. Starter (sketch)

Strike ×4, Defend ×4, and two of her own:
- **All Schemes to Know** (1): Seed an enemy twice, and deal 3 Dendro to it.
- **Tri-Karma Purification** (1): Purify.

**Starting relic: Akasha Terminal.** At the start of each fight, every enemy
gains one Seed. It teaches the Seed on turn one and makes the first Purify
land everywhere.

## 7. Intended weakness and failure modes

- **Weakness:** slow single-target damage until the Seeds are stacked, and she
  is fragile.
- **Overlap with Klee:** both put things on enemies and trigger them. The
  difference is that Bombs are spent when they go off, while Seeds stay and
  fire again and again. If seats read her as "Klee with green Bombs", that
  difference is not landing.
- **Failure mode, autopilot:** if the Akasha Terminal plus a Purify every turn
  is the whole game, placement stopped mattering. Seed caps and a per-enemy
  choice have to bind.
- **Failure mode, a reaction storm:** Purification on three Hydro-marked
  enemies makes three Cores. The once-per-card rule and the no-refire rule are
  the bound, and the first round tests it.

## 8. What it costs to build

The largest of the three. The whole Dendro engine (the Core alone is a build
the size of Mines, in both engines), Seeds, the Purification trigger, and the
companion question in pick 2.

## Picks

1. **Purification's element.** (1) *A Dendro hit that paints and can react,
   under the no-refire bound* [default]. (2) Element-less damage, like
   Overload's splash: safer, but it loses the "room is ready" loop.
2. **Her companions.** (1) *Until a Sumeru sheet exists she has no home
   nation, and both companion channels treat every nation as off-nation*
   [default]. (2) A Sumeru companion workshop is part of her build.
   (3) She operates from a nation we have (Inazuma, where Kirara is Dendro).
3. **Foresight.** (1) *The third archetype* [default]. (2) Drop it and give
   the slot to a Dendro Core archetype.
