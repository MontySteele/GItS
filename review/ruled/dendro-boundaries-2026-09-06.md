Status: RULED R264 2026-09-06

# Dendro: the boundaries, drawn now, built later

Written 2026-09-06 under R263 pick 1: the implementation is deferred out of
the immediate rebuild milestone, the design is drawn now, and Sumeru is no
longer a prerequisite. This paper fixes the edges a later build has to stay
inside, so that when the build comes it is a build and not a second design
argument. Two pages. Every claim names the file it is checked against.

## 1. Where Dendro comes from, without Sumeru

The old packet said "the cost of Dendro is a nation" because no character
and no companion was Dendro. That was true of the three nation sheets and
false of the prototype surface, which already carries two canonically Dendro
characters with the Dendro part left off:

| row | who | nation | what the row does today | why it has no element |
|---|---|---|---|---|
| `proto_mi_kirara_surprise_dispatch` | Kirara | Inazuma | 8 Block; next turn 10 damage to a random enemy | "this engine has six elements and no Dendro aura" (`docs/notes/prototype-surface-provenance.md` item 14) |
| `proto_mc_yaoyao_yuegui_throwing_mode` | Yaoyao | Liyue, Klee's personal pool | for 3 turns, end of turn, a Bomb 3 on a random enemy | "Dendro, which this mod does not have" (`review/active/klee-brief-2026-09-01.md` §7) |

Both are on `docs/prototype-surface.yaml`. So the Dendro source is the
companion slot in nations that exist, under the law as written (off-element
comes only from companions, `LAW.md` §Combat): Kirara for Inazuma, and a
Fontaine 5-star for Fontaine, where Emilie is canonically Dendro and the
5-star roster "may grow without limit" (`LAW.md` §Companions, rarity
grades). Mondstadt has no canonically Dendro character, so Klee reaches
Dendro the way she reaches anything off-nation: the reward channel's
roughly half off-nation weighting and the shop's wildcard slot (`LAW.md`
§Companions), plus Yaoyao if her row is given the element (pick 1).

**One rule of this paper: no row carries `element: dendro` until the
resolver knows Dendro.** Today an element the resolver does not know, hitting
an enemy with an aura, clears the aura and fires nothing
(`tier0/engine/reactions.py`, `resolve_hit` clears `enemy.aura` before
`_react`, and `_react` leaves `name` unset for an unknown pair). A tag
landed early would make Kirara's hit eat auras silently, which is a defect
wearing a schema field. The provenance note's reason for leaving her blank
stands until the build.

## 2. What Dendro is here

A **fifth aura element**, and nothing else changes about auras: one per
enemy, two player turns, refreshed by a same-element hit, Anemo and Geo
still trigger only (`LAW.md` §Combat; `AURA_ELEMENTS` in
`tier0/engine/reactions.py` gains one entry). The three reactions, in the
order they are built, and the decision each asks:

| pair | reaction | what it does | the decision it asks |
|---|---|---|---|
| Dendro + Hydro | **Bloom** | a **Dendro Core** sits on that enemy | where to put it, and whether to wait or spend a hit to pop it |
| Dendro + Electro | **Quicken** | that enemy is *Quickened* for two turns: a flat bonus on hits (§4) | which deck wants it: many small hits, not one large one |
| Dendro + Pyro | **Burning** | a damage-over-time that holds a Pyro aura up while it lasts | let it tick, or end it by cashing the standing Pyro into Vaporize or Melt |

The Core comes first (R263 kept the old packet's default), because it is the
only one that is a new object and it is the one a Hydro character reaches
with a single companion. Then Quicken, then Burning.

**The pairs that do not react.** Dendro with Cryo, and Anemo or Geo on a
Dendro aura, react with nothing in the source game (Dendro is neither
swirled nor crystallised). This engine has never had a non-reacting pair of
distinct elements, so the rule is new and is pick 2. The default: the hit
is plain, the standing aura stands, and the preview says "no reaction:
Dendro stands", so a seat is never surprised by a vanished aura.

## 3. The Core

- **What it is.** A neutral field object attached to one enemy, the first of
  its kind: the engine has enemy-side charges that belong to Klee (Bombs), a
  player-side pet (the Bake-Kurage) and a player-side stage (the Salon). Any
  Hydro-plus-Dendro pair makes one, whoever supplied which half.
- **When it bursts.** On its own at the end of your next turn, for
  `CORE_BURST` Dendro damage to the enemy it sits on. Early, if a **Pyro**
  hit lands on that enemy: *Burgeon*, `CORE_BURST` to every enemy. Early, if
  an **Electro** hit lands: *Hyperbloom*, `CORE_BURST × HYPERBLOOM_MULT` to
  that enemy alone. The three outcomes are the decision: free and late,
  wide, or deep.
- **What its damage is.** Flat and pipeline-free like Overload's splash
  (`LAW.md` §Combat, damage-pipeline-free), so no Strength or Vulnerable
  recursion and no compounding; it applies no aura; it is not an Attack hit,
  so it wakes no Thorns and no Skittish. Unlike Overload it does not pass
  Block: a Core is a thing that explodes, not a shock.
- **How many.** At most `CORE_CAP` Cores on one enemy; a Bloom past the cap
  **bursts the oldest** (a plain burst, to that enemy) and adds the new one,
  so repeating the central interaction never postpones its reward; the
  repeat-trigger this allows is part of what a round tests. A Core outlives
  the aura that made it. A killing Pyro or Electro hit still takes its
  Burgeon or Hyperbloom, the rule `EB-515` already set for reactions on a
  killing hit; a Core on a body that dies any other way is lost with it.
- **Plain Bloom stands alone.** Hydro plus one Dendro companion has to be
  worth the draft by itself: the timer burst is the ordinary payoff, and
  Burgeon and Hyperbloom reward a second element rather than rescue the
  first. `CORE_BURST` is priced for that, not for the popped case.
- **Cores and Bombs** (pick 4). Default: a Core is not a Bomb. Klee's Set off
  ignores it, the Bomb counter does not count it, the Splash reads nothing
  from it. But a Bomb's explosion is a Pyro hit, so it Burgeons a Core
  sitting under it, which is the one cross the two objects should have and
  the reason a Hydro companion in Klee's deck would want a Dendro one.

The Core is why Dendro waits on `EB-410`: a reaction the page cannot name
would put a Core on the field that a seat finds only in the HP arithmetic,
which is exactly the failure the old packet's §2 recorded for Overload and
Superconduct. `EB-428` (the glossary sized to the deck) is BUILT; `EB-410`
(a fired reaction named on the page, a bridge build) is the open half.

## 4. Quicken, additive, and not Superconduct

R263 pick 3: no amendment to the iron rule, an additive bonus. Superconduct
applies Vulnerable 2 (`SUPERCONDUCT_VULN`, `tier0/constants.py`), which
scales every hit by its size for two turns: it pays a deck that lands one
large hit. Quicken must pay the other deck. **Quickened: for two turns, every
hit on this enemy deals `+QUICKEN_BONUS`.** A flat bonus per hit is worth a
third of a 6-damage hit and a tenth of a 20-damage Bomb, so Klee's Spray
deck wants Quicken and her Cook deck wants Superconduct, and Kokomi's
carry-outs, which are several small hits, want Quicken. It is flat, timed,
and applied once as a power, which is the reading of the iron rule R263 took:
Superconduct's shape with a different sign. Quickened and Vulnerable can both
sit on an enemy; Quicken consumes the aura like every other reaction, so the
one-aura rule is untouched.

Canon gates the bonus to Electro hits (*Aggravate*) and Dendro hits
(*Spread*), and **that gating is the default**, revised on GPT's review of
2026-09-06. The first draft paid every hit, on the argument that only
companion hits would otherwise collect it. Two things outweigh that. An
all-hit Quicken is a generic multi-hit damage package that every future
character inherits, which blurs the reaction's identity into Superconduct's
neighbourhood again; and the companions that supply Electro in this mod hit
repeatedly on their own (Oz's tick, Shinobu's ring, Sara's rider), so a
gated bonus is collected several times per fight without making any
companion the carry. The all-hit shape stays as pick 3's option 2. The
honest limit holds either way: Quicken is Electro plus Dendro, and no
character is either, so it is a **two-companion reaction for every current
character**, Superconduct's access exactly. The reading
(`review/records/reaction-sequences-2026-09-06.md` §1, §5 item 6) shows
two-companion reactions do get planned where the sheets sell the pair, so
that access is a price, not a wall; Klee has Burning at one companion and
the Hydro characters have Bloom, and neither needs every Dendro payoff to be
one draft away.

## 5. Burning

Dendro with Pyro: `BURNING_DOT` a turn for `BURNING_TURNS`, and while it
burns the enemy holds a Pyro aura that refreshes each turn. Any Pyro or
Dendro hit re-lights it; any other reaction on that enemy ends it, because
that reaction consumed the aura Burning was holding. The decision is the
second half: a burning enemy is a lit Pyro aura, so a Hydro or Cryo hit
cashes it into Vaporize or Melt now and gives up the ticks. Electro-Charged
is a decaying Poison-shaped stack through Block that grows on a repeat
(`LAW.md` §Combat, stacking DoT); Burning is a fixed tick, stopped by Block,
that **never stacks**: a Pyro or Dendro hit on a burning enemy resets the
duration and leaves the tick where it was, so repeated application cannot
escalate it and the only way it ends early is another reaction. That is
what makes it a different thing rather than the same number twice. For Klee every hit is Pyro, so a
Dendro companion makes everything she touches burn: that is her one-companion
Dendro loop, the way Bloom is the Hydro characters'.

## 6. What Dendro does not do

No Dendro character; no change to the eight shipped reactions, the aura
duration or the one-aura rule; no LAW line moves; no Sumeru sheet is
required; nothing here enters the rebuild milestone or a `CONSTANTS_VERSION`
bump. The engine cost, for the record and not as rows: one entry in
`AURA_ELEMENTS`, three pairs and one non-reacting rule in `_react`, the Core
as an object the size of Mines in both engines, the C# mirror in
`klee-mod/KleeCode/Powers/ReactionEffects.cs`, and the previews. The seams
are already named: the C# badge documents Kirara's `Element.None` as the
Dendro gap (`ElementBadge.cs`), the icon lint handles a `DendroAuraPower`
in its own fixture (`tier0/tests/test_eb153_power_icons_lint.py`), and the
understudy's aura reader already matches the word `dendro` off the wire
(`understudy/adapter.py`). Rows are minted when the build is scheduled, after the reading and
after `EB-410`.

Every number here is a D pick the sim decides at build time, disclosed now
at its default: `CORE_BURST` 6, `HYPERBLOOM_MULT` 2, `CORE_CAP` 2,
`QUICKEN_BONUS` 3 under the gated default (2 under the all-hit shape),
`QUICKEN_TURNS` 2, `BURNING_DOT` 3, `BURNING_TURNS` 3.

## 7. Picks

1. **Dendro's first sources.** (1) *Kirara's row gains Dendro at the build,
   and Emilie enters Fontaine as a 5-star Rare applier; Yaoyao stays
   element-less, her radishes being Klee's Bombs* [default]. (2) Kirara
   only; Fontaine and Mondstadt reach Dendro off-nation. (3) As (1), and
   Yaoyao's Yuegui applies Dendro with each Bomb it plants, so Klee's
   personal pool carries her own Burning.
2. **The non-reacting pairs** (Dendro with Cryo; Anemo or Geo on Dendro).
   (1) *The hit is plain and the standing aura stands, previewed as "no
   reaction"* [default]. (2) The new element overwrites the aura, no
   reaction. (3) Dendro and Cryo coexist on one enemy, which breaks the
   one-aura rule and needs a LAW line.
3. **Quicken's shape.** (1) *Canon gating: Electro hits and Dendro hits on
   the Quickened enemy deal +3 for two turns* [default, moved here on the
   2026-09-06 GPT review; the first draft's default was (2)]. (2) Every hit
   deals +2 for two turns. (3) Count-capped: the next four hits deal +2,
   however long they take.
4. **Cores and Bombs.** (1) *A Core is not a Bomb; Set off ignores it; a
   Bomb's explosion, being Pyro, Burgeons it* [default]. (2) A Core counts as
   a Bomb for Klee: Set off pops it as Burgeon and the counter includes it.

## 8. The ruling (R264, 2026-09-06)

[USER] took all four picks at their defaults, in one line ("let's take
defaults and proceed"), after the reconciliation on GPT's review moved
pick 3's default to canon gating. So: (1) Kirara gains Dendro at the build
and Emilie enters Fontaine as a 5-star Rare applier, Yaoyao stays
element-less; (2) Dendro with Cryo, and Anemo or Geo on Dendro, are plain
hits that leave the standing aura, previewed as "no reaction"; (3) Quicken
pays +3 on Electro and Dendro hits for two turns and nothing on other hits;
(4) a Core is not a Bomb, and a Bomb's explosion Burgeons it. The numbers in
§6 stay D picks for the sim at build time. Nothing builds from this ruling:
the build waits, as §3 says, on `EB-410` and on the sweep's reading-ordered
work, and rows are minted when it is scheduled. No LAW line moves.
