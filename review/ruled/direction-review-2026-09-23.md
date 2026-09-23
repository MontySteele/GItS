Status: RULED R276 2026-09-23

# Direction: what "the Genshin experience" needs, and the Teyvat frame

Written 2026-09-23 by Claude (Opus 5.5). It covers the two halves you named:
the character kits, and the run frame (backgrounds, events, enemy art and
music). The per-character reviews are separate documents
(`klee-review-2026-09-23.md`, `kokomi-review-2026-09-23.md`,
`furina-review-2026-09-23.md`).

## 1. What makes Genshin feel like Genshin

Four things, in the order I think they matter for this mod:

1. **Characters whose kits feel like them.** Klee throws bombs and runs
   away, Kokomi sends a jellyfish, Furina conducts a cast. This is the
   kits' job, and it is the half that is working. Your Klee runs said so
   twice.
2. **A team whose elements meet.** Most of Genshin's combat fun is two
   characters' elements reacting: Vaporize, Melt, Overload, Freeze.
   Slay the Spire has one character per run. The mod's answer is the
   companion cards plus the shared reaction layer, and it works in
   principle. It is the thing a seat can least see on the screen (`EB-410`,
   the reaction display, is still open).
3. **Enemies that ask for the right element.** Abyss Mage shields,
   Fatui shields, Cryo slimes you cannot Freeze. Genshin's combat puzzles
   are mostly "bring the element that breaks this". The mod has none of
   that: every enemy is a base-game enemy with base-game rules.
4. **Places.** Nations, music and scenery. This is what the frame
   dressed.

## 2. Why the frame did not land, and I agree

The frame changed item 4 and nothing else. Every fight is still decided by
the same intents, the same numbers and the same answers. So the dressing
reads as a facelift over a game you already know, and the base game's art
direction is more coherent than a generated one. Your read ("the StS2 devs
know what they're doing") is the right one. The enemy art swap was the part
you liked. It is the part that sits nearest to item 3, because an enemy
that looks like an Abyss Mage invites a player to expect Abyss Mage rules.

**What I would keep switched on:** nothing by default. The frame already
ships behind `TeyvatFrame`, off in every release package. Leaving it there
costs nothing. Deleting it is a one-way door, and it isn't needed.

## 3. The lift that would make the frame matter

If the frame comes back, it should come back as item 3, not item 4: a small
number of **elemental enemies**. Genshin's signature shape is an
**elemental shield**, a second health bar that only one element damages
well. An Abyss Mage's Hydro shield breaks quickly to Cryo or Electro and
barely moves for anything else.

In this mod that would mean:

- A handful of elites and one boss per face carry a shield of one element,
  shown as a coloured bar above their health.
- Reactions against the shield do extra damage, using the existing
  reaction table. Nothing new for a player to learn.
- The companion reward slot then has a reason to be read: "I am heading
  into Inazuma, and the elites there carry Electro shields, so I want Pyro
  or Hydro help."

This touches enemy rules, which R272 froze, so it is a direction pick, not
a default. Its cost is real. It needs a new enemy power in both engines, a
bar on the enemy, and a sim pass, because it moves the difficulty of every
elite it touches. It is also the one change I can see that turns the
nation dressing into gameplay. It would come after the kits, not beside
them.

## 4. Picks

**Pick 1: the frame.**
1. **(default)** On hold. Behind its switch, off in every release package,
   nothing deleted, no further work.
2. On hold, but keep only the enemy art swap on by default in dev builds.
3. Remove the frame from the tree (a one-way door, under a git tag).

**Pick 2: elemental enemies.**
1. **(default)** Record it as the frame's re-entry condition. When the
   three kits are done, a short brief on elemental shields comes to you
   before any build.
2. Brief it now, beside the kits.
3. No. Enemies stay base-game.

**Pick 3: the team.** One fact first: under their prototypes, Klee and
Kokomi start with no companion card, while Furina starts with two. Her
patch still runs by accident. The shipped kits each started with one or
two. A starting companion is the cheapest way to put the team on the table
from fight one.
1. **(default)** The team stays the companion layer. For now all three
   prototypes start with no companion, so they match, and whether each
   kit starts with one comes back as part of the post-kit work. That work
   also makes reactions legible on screen (`EB-410`) and makes the
   companion slot a real draft choice.
2. Open a bigger structural brief now: a run as a lead character plus a
   drafted party, with companions central instead of a side slot.
3. No change to the companion layer's scope.

## Ruled (R276, 2026-09-23)

All three picks at their defaults.
