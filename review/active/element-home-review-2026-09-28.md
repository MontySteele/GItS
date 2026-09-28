# The elements as a home: what a character built on each element wants

**Ask ([USER], 2026-09-28):** "review the elemental system from a lens of
'what would a character centered around this element want to get out of it'
and do a design / balance pass over the elements first, since it seems like a
design gate for Varka or Nahida." Enemies are in scope to keep the view broad,
but "we are only implementing the character kits in this phase"; elemental
enemies are their own workstream after Kokomi.

**Stage:** Paper. Nothing builds until you rule. A change to the reaction
table is a rule change, so it ships under a flag and is read by two seats and
your play.

**What stays fixed:** the September sweep protected Vaporize and Melt, the
iron rule, one aura per enemy and the two-turn aura
(`review/ruled/elements-reaction-sweep-2026-09-05.md` §4). This paper touches
none of them.

## 1. What an element does for its own character today

Pyro, Hydro, Electro and Cryo leave an **aura**. Anemo and Geo leave none:
they only react with an aura that is already there. No character card applies
an off-element aura. The second colour comes from companions, a co-op partner
or a Furina guest (`LAW.md` §Combat).

So **a character's own element does nothing by itself.** Klee's Pyro is a
colour for somebody else to react with, and her solo game is her Bombs. For the
four aura elements that works: the kit carries the solo game, and the element
is half a sentence that a companion or a partner finishes.

**It fails for Anemo and Geo.** A trigger element with no second colour has
nothing to react with. A Varka whose every hit is Anemo opens every solo fight
with his element doing nothing. `LAW.md` §Roster says "every character clears
solo; co-op is amplified, never required", so his canon kit, which borrows an
ally's element, cannot be his solo loop.

The seats already show both trigger reactions failing:

- **Swirl is passed at the draft.** A Klee seat said "copying Pyro onto
  everything looked close to a no-op"
  (`review/records/reaction-sequences-2026-09-06.md` §2).
- **Crystallize is sequenced around as a cost** (it eats the aura for 4
  Block), and it is never the reason a Geo card is taken (§2, §4).
- **The fix was never built.** The reading's Swirl hypothesis, a small flat
  damage to all enemies (§5 item 8), was never built. `tier0/constants.py`
  has no Swirl number.

## 2. Element by element

| element | the deck it rewards | what it has today | the gap |
|---|---|---|---|
| Pyro | one big hit | Vaporize, Melt, Overload | none; the amplifiers are "the best thing the layer does" (sweep §2) |
| Hydro | paint often; be the aura others cash in | Vaporize, Frozen, Electro-Charged | none |
| Electro | many small hits | Overload, Electro-Charged, Superconduct; Quicken is drawn (+3 on Electro and Dendro hits) | none once Quicken lands |
| Cryo | control: which enemy, and when | Frozen, Melt, Superconduct | no Cryo character on any list |
| Dendro | set up now, pay later | Bloom's Core, Quicken, Burning, all drawn and ruled (`review/ruled/dendro-boundaries-2026-09-06.md`), none built | the engine |
| Anemo | one card touching every enemy | Swirl copies the aura to all enemies, no damage | nothing solo; nothing against one enemy |
| Geo | things that stay | Crystallize: 4 Block, and the aura is eaten | a cost to any reaction deck |

## 3. Three proposals

**A. Swirl as Genshin does it.** A Swirl deals the swirled element to every
other enemy, as a hit of that element. Where that enemy has no aura, it
spreads the aura, as today. Where it has a different aura, **it reacts
there**: a Hydro Swirl onto a Pyro-marked enemy Vaporizes on it. Every enemy
also takes a flat 2 (the reading's candidate). Each reaction is still per-hit
and eats its aura, so the iron rule holds. The one guard: a Swirl's spread
hits never Swirl again, so no chains. That gives Anemo its home: one card that
cashes a board of auras at once.

**B. Crystallize reads the aura and does not eat it.** A Geo hit on an aura
gives its Block and leaves the aura standing. Geo becomes a free rider in any
reaction deck instead of a cost. The alternative is Geo's canon
"permanence": the Block does not expire at the end of your turn, up to a cap.

**C. Trigger characters bring their own first colour.** An Anemo or Geo
character's starter holds one companion card of an aura element. `STATE.md`
already parks the question of whether characters start with a companion ("comes
back after the kits"); this answers yes for trigger elements only. It keeps the
law (companions stay the source) and moves no existing starter. For Varka, his
kit reads the aura on his target and carries it into his next Attack (canon
"absorption"). Solo, his starter companion supplies the aura; in co-op his
partner supplies it better, which is the canon fantasy, amplified and never
required. The other route is a `LAW.md` amendment that lets a trigger
character's own cards paint an element he absorbed this fight.

## 4. Enemies (to keep the view broad; not this phase)

Two shapes, both after Kokomi as their own workstream:

1. **Enemies that wear a standing aura**, such as a Hydro slime that is always
   Hydro. This gives every one-element character a solo reaction, and gives
   Swirl and Crystallize something to work on. It pulls against "reactions are
   earned, not given". My read is that the earning moves from the draft to
   the choice of target, which may be fine, but it is a question for that
   workstream.
2. **Elemental shields:** a second health bar that one element breaks fast
   (`review/ruled/direction-review-2026-09-23.md` §3).

This paper only checks that A to C do not close either shape off. A and B make
enemy auras richer. C does not depend on them.

## 5. Which character this opens (a read, not a pick)

- **Nahida** is the most ready. Dendro is designed and ruled, it is an aura
  element, and it pairs with all three kits: Bloom with Kokomi and Furina,
  Burning with Klee. Her Seeds of Skandha (a reaction on one seeded enemy
  fires on all of them) make her the most reaction-centred kit on the list.
  Her cost is the Dendro engine; the Core is a build the size of Mines.
- **Varka** needs A and C. After that his absorption loop is new ground.
- **Zhongli** is the least gated: his hook, debt, is not elemental, and B
  helps his Geo. `LAW.md` §Roster already says "Zhongli holds slot 4
  (countersigned, unscheduled)".
- **Yae**: Electro needs nothing new. Her risk (another turret character) is a
  kit question, not an element question.

## Picks

1. **Swirl.** (1) *Canon Swirl: it reacts where it lands, plus 2 to every
   enemy, with no chains* [default]. (2) The flat 2 only. (3) Leave it.
2. **Crystallize.** (1) *The Block, and the aura stays* [default].
   (2) Block that does not expire at end of turn, capped. (3) Leave it.
3. **A trigger character's first colour.** (1) *One aura-element companion
   in the starter* [default]. (2) Amend `LAW.md` so an absorbed element may be
   painted. (3) Decide in each character's brief.
4. **When A and B land.** (1) *After your Kokomi run, under a flag, before
   character four's Prototype; two seats and your play read it* [default].
   (2) With the first character that needs each. (3) With the enemy
   workstream.
5. **Character four.** (1) *Nahida: first Dendro, and the hardest test of
   this pass* [default]. (2) Zhongli, per the slot-4 line. (3) Varka.
   (4) Decide after A and B have been played.
