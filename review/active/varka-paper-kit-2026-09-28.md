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

- **Absorb:** when Varka Swirls an aura, he **absorbs** its element. The first
  time each fight he absorbs Pyro, Hydro, Electro or Cryo, he gains that
  element's **Wind** for the rest of the fight. Each Wind is small, flat and
  of its own kind (placeholders):
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

**Bosses:** a lone boss is not a dead fight. Absorbing does not need other
enemies, so he still collects Winds; only the spread is wasted.

**In co-op:** his partner's auras are his Winds. Klee paints Pyro, and Varka
Swirls it into his Pyro Wind without taking it from her, because the aura is
only spent for triggers and she can still Vaporize it. That is Genshin's
Stormward Charge.

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

1. **Four Winds (default).** Collect distinct Winds and finish with Ascension.
   Signposts: cheap Knights, and a Common that Swirls twice.
2. **Gale (the ceiling, the swirl-fisher).** Many Swirls instead of many Winds:
   Swirl-count payoffs, with the flat 2 hitting every enemy each time. It
   reuses the Mondstadt companion **Sturm und Drang** (a Swirl makes your next
   Attack deal +6 of the swirled element), now in his hands.
3. **Grand Master (tempo).** Command the Knights: a card that makes your
   companion cards cost 0 this turn, and one that replays the last companion
   you played. Its risk is `SUPPORT_CARRY` (§6).

**Bridges:** every Knight feeds both Winds and Gale. Grand Master's replays
turn one Knight into two Swirls.

**Flavour for the relic and potion pass:** Dandelion Wine (a potion), and
**The Untitled Question** (a Rare that sets three tasks for the fight: Varka's
witch's homework, from his Hexerei quest).

## 6. Starter (sketch)

Strike ×4, Defend ×4, and two of his own:
- **Knights' Muster** (1, companion).
- **Windbound Execution** (1): deal 6 Anemo to one enemy; if it Swirls, gain 4
  Block.

**Starting relic: Boreas's Fang.** Once per fight, your first Ascension costs
0. It points at the payoff from fight one.

## 7. Intended weakness and failure modes

- **Weakness:** a slow start. Turn one has no Winds, and a draw without a
  Knight is a Strike deck.
- **Failure mode, companions carry:** the delete-test in `LAW.md`. Deleting
  Varka's own cards must gut the deck. If Knights plus Sturm und Drang win
  without him, that is `SUPPORT_CARRY`. The Winds and Ascension have to be
  where the power is.
- **Failure mode, the same fight every time:** collect four, fire, every fight.
  Winds reset each fight, Ascension exhausts, and which Knight you draw varies
  the order. The first round should read whether the order felt chosen.
- **Failure mode, the Gale wall:** the flat 2 to every enemy on every Swirl
  against packs. The once-per-aura rule bounds it to one Swirl per fresh aura.

## 8. What it costs to build

Medium, mostly in cards. The element review's change A, one Absorb hook, the
Wind powers, and four personal-pool Knights. He is the character that tests
the new Swirl hardest.

## Picks

1. **Winds.** (1) *Four different flat effects, one per element* [default].
   (2) One generic stack per distinct element (simpler, less flavour).
2. **His first colour.** (1) *Knights' Muster in the starter* [default].
   (2) An optional run-start offer of one Knight (`LAW.md`'s R160 route).
   (3) No starter source; the Knights come through the draft.
3. **Grand Master.** (1) *The third archetype* [default]. (2) Drop it; a
   third archetype comes from his Hexerei homework instead.
