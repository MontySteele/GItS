# Varka wave, 2026-10-13: five seats on the last-pass build

Five Sonnet seats at A0 on build 0.2.5194, the first play of the last pass
(`review/active/varka-last-pass-2026-10-12.md`). Raw seat records and the
packet stay in the session scratchpad (gitignored by rule). Base yardstick:
the base-five Sonnet baseline went 0/5 at A0, all dying in act 3
(`review/records/base-five-baseline-2026-10-05.md`).

## Results

| Seat | Result | Killer | Deck shape |
|---|---|---|---|
| 1 | lost, floor 33 | Knowledge Demon (act 2 boss) | Pyro-led, Cryo/Hydro partners, swap passives (Cycle of Seasons, Windborne Resolve, Navia) |
| 2 | lost, floor 48 | Queen + Torch Head (act 3 boss) | Swirl chain, Pyro + Electro, the most Anemo (about a third) |
| 3 | lost, floor 31 | Infested Prism (act 2 elite) | Anemo-dominant, little Block |
| 4 | **won**, 48/80 HP | | Pyro-led, Demon Form + Juggernaut, Charge of the Knights, Wolfpack |
| 5 | lost, floor 48 | Test Subject (act 3 boss, form 3, 2 Block short) | Block into damage: Tidal Bulwark, Noelle: Sweeping Time x2 |

One win, three runs to the act 3 boss, none died in act 1. That is at or a
little above the base five's 0/5, which is where a Prototype kit should sit.

## The open questions

**1. The Pyro core.** Pyro carried the damage in three of five decks.
Kindled Edge, Blazing Charge and Ashen Oath were taken in four lanes each and
never skipped; Ashen Oath's Strength-plus-Oath was the scaling pick seat 4
named. No seat used an Exhaust synergy, and seat 5's two Dazed-clogged turns
show the "tactical Exhaust against status enemies" tool was never drafted.
Reading: the Strength half works; the Exhaust half is invisible but is not
needed to carry the element. No change.

**2. Anemo as half a deck.** No deck went mono-element; Anemo was a fifth to
a third of every deck. The most Anemo-heavy deck (seat 3) died earliest, to a
Block check; the next heaviest (seat 2) reached the act 3 boss. Anemo works as
the glue (Converging Winds, Wall of Gales, Twin Gales were praised) but a
half-Anemo deck needs its Block from somewhere else. Not yet tested on
purpose; a forced half-Anemo seat is the next probe if this stays open.

**3. Switch versus mono-element power.** The switch payoffs (Cycle of Seasons,
Windborne Resolve, Navia, Change of Guard, Charge of the Knights) each made a
deck, none dominated. The power that does hide is **Four Winds' Ascension**:
all five seats named it the card they most wanted to draw, and it landed the
kill in every boss fight seat 2 won (30 to 81 damage per cast at Oath 10 to
14). It is a relic-given Retain card, so every Varka deck has it. With one win
in five that is the engine working, not a runaway; it is the first number to
watch at Balance. Weathervane and Oathbound Aegis were never seen.

**4. Block.** Block into damage is a real archetype: seat 5's Sweeping Time on
64 Block cleared a room, seat 4's Juggernaut turned every Block card into
damage. The two losses that were Block failures (seat 3 under Tainted, seat 2
under Chains of Binding and Frail) were decks that drafted no scaling Block.
No change. **Caveat (found after the wave, fixed in #1200):** Tidal Bulwark counted its own Block twice, so every Tidal Bulwark hit in this wave dealt about its Block more than printed. Noelle: Sweeping Time and Juggernaut were not affected. Seat 5's engine was partly this bug; re-read it next wave.

Also from #1200: of the defects below, Static Field, Rising Gale, Change of Guard, the stale current element, Terror Eel and the Cultist turn were seat misreads (checked against lane telemetry); Ravenous "x2" was a double subscription, fixed; Kaiser Crab's missing 99 Block is unexplained (BACKLOG).

## What played well

- Ordering by current element (Swirl before Four Winds' Ascension, Ascension
  before the card that changes element) was the most frequent real decision.
- Exact-Block puzzles: fully blocking Bowlbug Rock to Stun it, Wall of Gales
  plus Navia for exactly enough.
- Swap passives turned "change element" into damage and Block (seat 1).

## What did not

- **A hitless element application wastes the aura.** Barbara and Rippling
  Guard apply Hydro to a Pyro aura, Vaporize on 0 damage, and the aura is gone
  with nothing paid (seat 3, twice). This is the zero-damage amplifier case
  [USER] raised for Stoke. A rule pick, below.
- The first turn of the first fight was no decision in three of five runs.
- Never again: Lynette's Bogglecat Box (4 Block for 1 Energy), Static Field+
  (never drew in 23 fights), Enlightenment (a base card).

## To change (built without a pick: defects and missing text)

1. Lisa: Violet Arc changed the current element to Electro with no printed
   switch. Print it or stop it, whichever the rule says.
2. Windbound Execution and Crosswind do not say a Swirl also deals 2 to ALL.
3. Static Field+ never drew; Rising Gale drew on one Swirl and not another.
4. Change of Guard never offered Cryo at Cryo Oath 1.
5. Stoke the Flames: show whether Four Winds' Ascension's element hit takes the
   +5 (seat 5 could not tell).
6. The Oath page showed "Current element: Pyro" after a Cryo card; a turn-1
   "Hydro Oath 0" line explains nothing.
7. Charge of the Knights counts Knights played earlier in the fight; say so.
8. Check against the base game: Terror Eel's Stun not stopping its action,
   Lagavulin waking through Plating on Tidal Bulwark, Kaiser Crab's 99 Block,
   a Cultist turn with no visible damage, Ravenous "fired x2" on one death.

## Pick for [USER]

**Varka wave, pick 1: an element applied without a hit.**
(a) **default:** an application with no hit never sets off Melt or Vaporize;
it leaves the old aura in place. Overload, Superconduct, Electro-Charged,
Frozen and Swirl still react, since they do not multiply a hit. This touches
every kit (Kokomi's jellyfish and Barbara's kind of card).
(b) Keep the rule; print a warning on cards that only apply.
(c) Varka only: his "apply your current element" cards skip an aura they
would amplify.

**Ruled 2026-10-13: keep today's rule; no code change.** [USER]: "In Genshin,
it's totally normal to just ruin a reaction by applying a super-low-damage Pyro
setup skill to an enemy with Cryo before you get your big Pyro burst hit in
(E.g. Bennet / Mavuika / Citlali teams) and managing that is just a skill
issue. So I wonder if this change is overly generous or feels like an un-needed
carve out." Then, on keeping the rule: "Sounds good!" The warning in (b)
already exists: a card with no hit shows "This card deals no damage. Pyro plus
Hydro is still consumed, and there is no hit here for the 1.5x to multiply."
(KleeCardTooltips.NoHitBody, EB-338). Seat 3 wasted the aura with it on screen.
