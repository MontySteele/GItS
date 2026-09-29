Status: RULED 2026-09-28 (§6). Step 4, phase one (§3, §4, §7.1, §7.3) built
2026-09-28 in PR #745; phase two (§7.2, §7.4) is in `BACKLOG.md`.

# The elements as a home: what a character built on each element wants

**Ask ([USER], 2026-09-28):** "review the elemental system from a lens of
'what would a character centered around this element want to get out of it'
and do a design / balance pass over the elements first, since it seems like a
design gate for Varka or Nahida." Enemies are in view to keep it broad, but
"we are only implementing the character kits in this phase"; elemental enemies
are their own workstream after Kokomi.

**What stays fixed:** the September sweep protected Vaporize and Melt, the
iron rule, one aura per enemy and the two-turn aura
(`review/ruled/elements-reaction-sweep-2026-09-05.md` §4). This paper touches
none of them.

## 1. What an element does for its own character today

Pyro, Hydro, Electro and Cryo leave an **aura**. Anemo and Geo leave none:
they only react with an aura that is already there. No character card applies
an off-element aura. The second colour comes from companions, a co-op partner
or a Furina guest (`LAW.md` §Combat).

**A character's own element does nothing by itself, and that is fine.**
Klee's Pyro is a colour for somebody else to react with, and her Bombs carry
her solo game. A trigger element can live the same way: a Zhongli or a Varka
can have a subsystem that carries him. The first draft of this paper said
Anemo and Geo "cannot be a home". That went too far (GPT review, 2026-09-28).

**The real requirement is narrower.** A character *built around reactions*
needs a dependable second element, whatever his own element is.

**What the seats show is the weakness of the trigger reactions themselves:**
- **Swirl is passed at the draft.** A Klee seat said "copying Pyro onto
  everything looked close to a no-op"
  (`review/records/reaction-sequences-2026-09-06.md` §2).
- **Crystallize is sequenced around as a cost:** it eats the aura for 4 Block.
- **Both are worse than they look.** Today Swirl needs **three** elements to
  pay: Anemo, the aura it spreads, and a third element to react with the
  spread ([USER], 2026-09-28). Crystallize is a cost to every reaction deck.

## 2. Element by element

| element | the deck it rewards | what it has today | the gap |
|---|---|---|---|
| Pyro | one big hit | Vaporize, Melt, Overload | none |
| Hydro | paint often; be the aura others cash in | Vaporize, Frozen, Electro-Charged | none |
| Electro | many small hits | Overload, Electro-Charged, Superconduct; Quicken is drawn | none once Quicken lands |
| Cryo | control: which enemy, and when | Frozen, Melt, Superconduct | no Cryo character on any list |
| Dendro | set up now, pay later | Bloom's Core, Quicken, Burning, ruled (`review/ruled/dendro-boundaries-2026-09-06.md`), none built | the engine |
| Anemo | one card touching every enemy | Swirl spreads the aura, no damage | pays only with a third element |
| Geo | things that stay | Crystallize: 4 Block, and the aura is eaten | a cost to any reaction deck |

## 3. The shared rule: a trigger element uses an aura once

Anemo and Geo **no longer consume** the aura they act on. Instead the aura is
**spent for triggers**: a second Anemo or Geo hit on it does nothing extra
until it is refreshed by a hit of its own element or replaced by another
reaction. Aura elements react with a spent aura exactly as before.

This is the bound for both reactions below. A trigger element's output is
capped by how often fresh auras arrive, and that is capped by the
second-element source. Repeated hits (Navia acting twice, a multi-hit Varka)
cannot loop.

## 4. The two changes

**A. Swirl pays for itself.** An Anemo hit on a fresh aura:
- spreads that aura to every enemy that lacks it;
- keeps it on the enemy that was hit, so a Swirl on a lone boss does not
  throw away the setup;
- deals a flat 2 to every enemy.

The 2 is element-less and outside the damage pipeline, like Overload's
splash, so it reacts with nothing. The spread copies arrive spent, so they
cannot be Swirled again. Anemo plus one aura element is now a two-element
reaction.

*Later, a separate candidate:* the spread reacts where it lands (a Hydro
Swirl onto a Pyro-marked enemy Vaporizes there). It is left out because it is
not bounded. A Pyro Swirl across three Electro-marked enemies makes three
Overloads, which is 18 damage to every enemy.

**B. Crystallize keeps the aura.** A Geo hit on a fresh aura gives its 4 Block
and leaves the aura standing, now spent.
- **Used incidentally** (Furina with Navia on stage), it is a free bonus that
  never costs the real reaction.
- **As your main element**, it is capped by fresh auras.

Shards and constructs you spend down belong in a Geo character's kit, the way
Bombs are Klee's and not Pyro's. The round has to test Navia with Tide of
Applause: Block, Fanfare and a kept aura all at once.

## 5. Enemies (to keep the view broad; not this phase)

Two shapes, both after Kokomi as their own workstream:

1. **Enemies that wear a standing aura.** This gives every one-element
   character a solo reaction. It pulls against "reactions are earned, not
   given".
2. **Elemental shields** (`review/ruled/direction-review-2026-09-23.md` §3).

The shared rule and A and B leave both shapes open.

## 6. The ruling (2026-09-28)

After GPT's review, [USER] took the revised picks ("That makes sense"):

1. **Swirl:** it pays for itself with a flat 2. Reactions where the spread
   lands stay a separate, later candidate.
2. **Crystallize:** it keeps the aura; an aura crystallizes once. Tested with
   repeated hits and reaction rewards.
3. **A trigger character's first colour:** decided per character, in its own
   paper, with a named source.
4. **Timing:** [USER]'s order.
   1. Paper kits for Nahida, Zhongli and Varka that assume these changes.
   2. [USER] playtests Kokomi and Furina.
   3. Kokomi and Furina changes as needed, with agent retests.
   4. The element changes ported under a flag, Swirl and Crystallize tested
      separately, with agent retests.
   5. Character four decided.
5. **Character four:** decided after the changes are played.

[USER] on Geo: "making sure that Geo doesn't just become a source of infinity
block if we don't consume the aura, while also making sure it's useful whether
you trigger it incidentally ... but not broken if it's your primary element."
The once-per-aura rule is the answer in §3. On Swirl: "it now requires three
elements to effectively function". Change A answers that.

## 7. Shared rules the kit papers expose, for the port

GPT's audit of the three paper kits (2026-09-28) listed what the port in step 4
has to settle, whichever character comes fourth. Seeds, Winds and the Tab stay
character work and add nothing to the shared system.

1. **Fresh and spent auras must be visible.** Swirl and Crystallize share one
   budget: a Swirl spends the aura, so a Crystallize after it gets nothing
   until the aura is refreshed. Spread copies arrive spent, so this reaches
   across the room. The aura badge shows "spent", and the preview says why a
   trigger pays nothing.
2. **Burning and the trigger elements.** The Dendro paper ends Burning when
   another reaction consumes its aura. Swirl and Crystallize no longer
   consume, so they do not end Burning: a Swirl or Crystallize on a burning
   enemy spends the held Pyro, and Burning keeps ticking.
3. **One reaction event for every listener.** Every reaction reports what
   fired, on whom, and from what source: a card, a companion, a co-op partner,
   or an automatic effect such as a Core on its timer. It is shaped so that a
   later listener (Nahida's Purification, Varka's Winds) needs no new hook.
4. **Dendro is ported as ruled.** The non-reacting pairs, the Core rules and
   their previews, tested on the ruled first sources (Kirara, Emilie) without
   committing to Nahida.
