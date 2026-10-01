# Base-game baseline: Sonnet seats on Ironclad and Silent (2026-10-01)

Installed build 0.2.4118 (the base characters are unchanged by our mod). Two
Sonnet seats, one act per seat with handoff notes, ascension 0, game-rolled
seeds: Ironclad on lane 1, Silent on lane 2. Purpose: the Sonnet counterpart
to the Opus baseline ([USER]: Opus seats win about 70% on the base
characters, dying mostly to the act-3 boss), so our kits' Sonnet rounds have
a base-game yardstick. Raw records are gitignored (session scratchpad
`base-lane1/`, `base-lane2/`).

## Results

| Character | Act 1 | Act 2 | Act 3 |
|---|---|---|---|
| Ironclad | Lagavulin Matriarch beaten, 12/80 | The Insatiable beaten, 48/80 | died on floor 48 to Queen and Torch Head Amalgam (Queen 323/400) |
| Silent | Waterfall Giant beaten, 31/85 | Kaiser Crab beaten, 10/100 | **won**: Queen beaten on floor 48, about 3 HP left |

One win, one act-3-boss death. Actions: Ironclad 596, Silent 653.

Against our kits on the same seat type today: Varka 0/2 (both reached act 3),
Furina 0/2 (one act-3 death, one stopped early), Kokomi 0/2 (both died to the
act-1 boss). Two base runs are too few for a rate; they say the act-3 boss is
the wall for a Sonnet seat on the base game too, and that Kokomi's act-1
deaths are hers, not the seat's.

## What played well (the base game's own standard)

- **Readable hard counters made the best decisions.** Skulking Colony's
  "Hardened Shell 20 of 20 left this turn", Exoskeleton's Hard To Kill 9,
  The Insatiable's printed Sandpit countdown, Terror Eel's stun threshold:
  each told the seat exactly what to spend.
- **One scaling plan carried each run.** Silent: poison (two Noxious Fumes,
  Snecko Skull, Apotheosis) killed every boss and elite in act 3. Ironclad:
  Block-into-damage (Juggernaut+ with Daughter of the Wind). Perfected Strike+
  was the first play nearly every turn. The "one-card plan" complaint about
  Varka is the base game's shape too.

## What did not

- **Counters to the deck's plan hurt most:** Infested Prism taints every
  Skill (Silent 20 HP to 4), Globe Head's Galvanic made every Power cost 6 HP,
  and the Queen's Bound plus Frail cut Ironclad's Block engine off.
- **Dead turns were draws, not choices:** five Strikes and five Defends clog
  both decks all act; status piles (Dazed, Frantic Escape) had no answer.
- **The bridge hid definitions:** brief mode never defined Tainted, Bound or
  Galvanized. Fixed in #807 (a word is defined the first time a lane meets it).
- **Bridge loose ends:** enemy action order is not shown (it decided the
  Silent win); the Drowning Beacon's "Bottle" promised a Glowwater Potion the
  seat never received (unchecked).

## What to change

1. **Read our kits' seat rounds against this:** a Sonnet seat reaching act 3
   is the base-game norm; dying at act 1 (Kokomi) is not.
2. **BACKLOG:** the Drowning Beacon potion, and showing enemy action order.
