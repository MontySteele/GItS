# Varka: the Four Winds (paper kit)

**Ask ([USER], 2026-09-28):** paper kits for Nahida, Zhongli and Varka that
assume the element changes. [USER] ranks Varka at the top with Yae. His kit
facts come from a research packet built from secondary sources (Fandom and
official pages were not reachable): the Skill "Windbound Execution" puts him
in **Stormward Charge**, where his attacks take an ally's element, and
**Four Winds' Ascension** deals Anemo plus that element together. His passives
reward Swirl.

**Stage:** Paper. A concept, not yet a brief. Card numbers are placeholders
for the sim.

## 1. The promise

The Grand Master fights with every wind in Mondstadt. Varka takes the elements
others leave on the field and makes them his own.

## 2. His element: Anemo, with the new Swirl

Anemo leaves no aura. Under the element review
(`review/ruled/element-home-review-2026-09-28.md`), an Anemo hit on a fresh
aura **Swirls** it:
- the aura spreads to every enemy that lacks it;
- the enemy that was hit keeps it;
- every enemy takes a flat 2;
- the aura is spent for triggers.

`LAW.md` §Economy already imagines him: "a hypothetical swirl-fisher", an
archetype where fishing for companions may be the dominant plan.

**Element changes he needs:** the shared rule and change A, both ruled. One
new hook, the Absorb in §3. The engine already has a Swirl event that
remembers its element (`tier0/constants.py`, the Mondstadt workshop's hooks).
The spread reacting where it lands is **not** needed. It stays the separate,
later candidate.

## 3. The signature: the Four Winds

- **Absorb:** some of Varka's own cards say **Absorb**. An Absorb Swirl works
  like any Swirl, except that it **takes the aura off the enemy it hit**
  instead of leaving it spent there. The copies it spread to the others still
  arrive spent. This is a card effect, not a change to the shared rule, and it
  is canon: an Anemo absorption removes the element it took. The first time
  each fight he absorbs Pyro, Hydro, Electro or Cryo, he gains that element's
  **Wind** for the rest of the fight. Each Wind is small, flat and of its own
  kind (placeholders):
  - **Pyro Wind:** your Attacks deal +2.
  - **Hydro Wind:** gain 2 Block whenever you Swirl.
  - **Electro Wind:** your first Swirl each turn draws a card.
  - **Cryo Wind:** each Swirl applies 1 Weak to the enemy it hit.
- **Four Winds' Ascension** (his signature Attack): 6 damage, plus 6 per Wind
  you hold. Exhaust.

**The tension is now or later.** Ascension with two Winds today, or another
turn to catch a third? That is Klee's "detonate or wait" shape, fed by variety
instead of stockpiling. Which aura to Swirl first matters too, because each
Wind comes once.

**Why Absorb takes the aura (GPT's audit).** If the aura only went spent, the
next Knight would react with it: Hydro on a spent Pyro Vaporizes both away,
and he needs another application before he can absorb Hydro. Taking the aura
leaves the enemy clean for the next colour.

**A worked solo sequence against a boss,** with the starter plus one drafted
Knight (Barbara) and one Windbound Execution:
1. **Turn 1:** Knights' Muster, choosing Amber, paints Pyro. A Strike, Absorbing
   through the starting relic, takes it off: Pyro Wind. The boss is clean.
2. **Turn 2:** Barbara paints Hydro. Windbound Execution Absorbs it: Hydro
   Wind. Then Ascension now for 18, or hold it for a third Wind at 24.

With the bare starter it is slower: Muster comes back once per shuffle. That
is the intended weakness. The first round has to read whether it feels
deliberate or starved.

**Against a pack it is a targeting puzzle.** The spread copies land spent on
the other enemies, so a new Knight aimed at one of them reacts instead of
painting. You aim the next colour at the enemy you absorbed from, the one left
clean.

**In co-op the choice is sharper.** His partner's auras are his Winds, but an
Absorb takes them away. A plain Swirl leaves Klee's Pyro for her Vaporize and
gets no Wind; an Absorb gets the Wind and costs her the aura. Deciding between
them is the co-op decision, and it is Genshin's Stormward Charge with a price.

## 4. His first colour: the Knights of Favonius

Varka *is* reaction-centred, so he needs a dependable second element (the
element review, §1). Mondstadt's Knights supply it, which is lore-true: the
Grand Master commands them.
- **Personal-pool companions** (`LAW.md`: they "are the character's kit, and
  may carry"): Amber (Pyro), Barbara (Hydro), Lisa (Electro), Kaeya (Cryo).
  Each is a Varka-only card that paints its element.
- **In the starter: Knights' Muster**, a companion card. Choose a Knight: deal
  4 of their element.

The draft then decides how fast he reaches four Winds. His deck wants
**variety**, which no current kit wants: Klee, Kokomi and Furina all paint one
colour.

## 5. The three archetypes

1. **Four Winds (default, the simple path).** One element at a time: paint,
   Absorb, collect, finish with Ascension. Signposts: cheap Knights, and a
   Common that Swirls **every** enemy carrying a fresh aura (one aura cannot be
   Swirled twice).
2. **Gale (the ceiling: payoff for handling complexity).** Many Swirls instead
   of many Winds, and multi-element boards. This is where the element review's
   later candidate lives, **as a card and not a shared rule**: *Converging
   Winds (Rare, Power): your Swirls react where they land.* The unbounded
   three-Overload case is then something you draft, pay for, and aim. It also
   reuses the Mondstadt companion **Sturm und Drang** (a Swirl makes your next
   Attack deal +6 of the swirled element). This follows [USER]'s framing:
   make Swirl useful on its own, and make multi-reaction Swirls "an archetype
   or payoff for handling complexity vs a simpler 'just do one-element swirls'
   main path".
3. **Grand Master (provisional).** Command the Knights: companions cost 0 this
   turn, replay the last companion. GPT's audit is right that discounts and
   replays so far support both plans rather than making a third. It stays
   provisional until it shows a turn the other two would not play.

**Bridges:** every Knight feeds both Winds and Gale. A Grand Master replay
turns one Knight into two colours.

**Flavour for the relic and potion pass:** Dandelion Wine (a potion), and
**The Untitled Question** (a Rare that sets three tasks for the fight: Varka's
witch's homework, from his Hexerei quest).

## 6. Starter (sketch)

Strike ×4, Defend ×4, and two of his own:
- **Knights' Muster** (1, companion): choose a Knight; deal 4 of their
  element.
- **Four Winds' Ascension** (2): the payoff, in the starter so it is reached
  from fight one. Exhaust, so the "now or wait" decision is one per fight.

**Starting relic: Boreas's Fang.** Your first Attack each fight Absorbs. It
teaches the Absorb verb on turn one, so the starter needs no third card of
his. Windbound Execution (deal 6 Anemo, Absorb) is a Common in the pool.

The first draft discounted Ascension with its relic but left Ascension out of
the starter (GPT's audit). Now the payoff is in the deck, and the relic teaches
the verb that feeds it.

## 7. Intended weakness and failure modes

- **Weakness:** a slow start. Turn one has no Winds, and a draw without a
  Knight is a Strike deck.
- **Failure mode, companions carry:** the delete-test in `LAW.md` deletes his
  personal Knights along with his other cards, because they are his kit (GPT's
  correction). The real check is universal companions: if Sturm und Drang
  and other Mondstadt universals win without any Varka card, that is
  `SUPPORT_CARRY`.
- **Failure mode, the same fight every time:** collect four, fire, every fight.
  Winds reset each fight, Ascension exhausts, and which Knight you draw varies
  the order. The first round should read whether the order felt chosen.
- **Failure mode, the Gale wall:** the flat 2 to every enemy on every Swirl
  against packs. The once-per-aura rule bounds it to one Swirl per fresh aura.

## 8. What it costs to build

Medium, mostly in cards. The element review's change A, one Absorb hook (a
Swirl that removes its source aura), the Wind powers, four personal-pool
Knights, and Converging Winds as a card-scoped switch. He is the character that tests
the new Swirl hardest.

## Picks

1. **Winds.** (1) *Four different flat effects, one per element* [default].
   (2) One generic stack per distinct element (simpler, less flavour).
2. **His first colour.** (1) *Knights' Muster in the starter* [default].
   (2) An optional run-start offer of one Knight (`LAW.md`'s R160 route).
   (3) No starter source; the Knights come through the draft.
3. **Grand Master.** (1) *Provisional third archetype, until it shows a
   distinct turn* [default]. (2) Drop it now; a third archetype comes from his
   Hexerei homework instead.
