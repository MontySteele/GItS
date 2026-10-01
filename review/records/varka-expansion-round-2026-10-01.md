# Varka seat round: the 78-card pool (2026-10-01)

Build 0.2.4094: the expansion (#788, 37 cards and the Knight pass) on his own
relics and potions (#787). Two Sonnet seats, one act per seat with a handoff
note, ascension 0, game-rolled seeds. Raw records are gitignored (session
scratchpad `vk7-lane1/`, `vk7-lane2/`).

## Results

| Lane | Act 1 | Act 2 | Act 3 |
|---|---|---|---|
| 1 | Lagavulin Matriarch beaten, 54/87 | Kaiser Crab beaten, 4/87 (a display filter of the seat's own hid two attack intents: 41 HP) | died floor 48 to Test Subject's third phase, boss at 42 HP |
| 2 | Lagavulin Matriarch beaten, 73/80 | Kaiser Crab beaten, 17/80 | died floor 48 to Aeonglass, boss at 233/512 |

Both lanes reached the act-3 boss; neither won. The last round (41 cards)
went one win, one loss.

## What played well

- **Aura ordering is still the puzzle.** An applier, then the Anemo card, then
  Four Winds' Ascension made every good turn (lane 2: Barbara, then Four Winds
  for 37; Blazing Charge then Pressure Front Overloaded twice, two
  Decimillipedes dead before they revived).
- **Swirl AoE against groups** (Windbound Execution+ killed three Gardeners;
  Gale Sweep+ hit 6 to 12 times against 2 or 3 enemies).
- **Kaiser Crab's rule made a real decision** (lane 2 took Updraft so one
  potion hit both crabs and dodged Crab Rage).

## What did not

- **Late Oath outgrows the kit.** Lane 1 at Oath 35 to 50: Azure Devour 84
  to 140, Tidal Bulwark+ 60 to 129 Block, Four Winds 60 to 100; "everything
  else is filler". The sim agrees: the default drafter takes the Hydro Block
  Knights 95% of the time.
- **Losing the element is silent,** four times this round (Baron Bunny, Mika,
  Blazing Charge, Favonius Drill, Diluc): "I only noticed when Azure Devour
  printed 'Deals 1 damage'".
- **Turns with no aura source have no decision** (both lanes, most first
  turns).
- **Status clog has no answer.** Lane 1 died with three Wounds, a Burn and a
  Dazed in a five-card hand; nothing in the kit exhausts, discards or draws
  through them. Aeonglass's Withers killed lane 2 the same way.
- **Faces that mislead:** Cavalry Charge is tagged Anemo but hits as the
  current element; whether a Swirl's damage passes Block was read two ways;
  "spent" auras read as live.

## What to change

1. The element-identities paper
   (`review/active/varka-element-identities-2026-10-01.md`, ruled): Electro
   gets discard (Short Circuit and Violet Storm discard Wounds and Burns,
   the first answer to status clog), Unbroken Tide goes, the element-switch
   warnings land.
2. Cavalry Charge's tag reads "your current element", not Anemo; the Swirl
   tip says plainly what passes Block.
3. Watch: Azure Devour and Tidal Bulwark's ceiling at Oath 30+, and Dawn
   Patrol (gains Exhaust under the paper).

Smaller, for the backlog: a ? room printed a shop with no shelves and `buy`
was refused (bridge); `play` asked for a target while the only enemy was dead
with its revive pending.
