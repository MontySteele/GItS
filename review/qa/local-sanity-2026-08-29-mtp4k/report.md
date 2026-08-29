# Local model sanity read -- 20260829

WHAT THIS IS. A local model re-read turns that are already CLOSED, and its reading is printed beside the two that are recorded. It is SUBJECTIVE FEEDBACK about the READER.

WHAT THIS IS NOT. Not human validation. Not balance evidence. Not a grade: nothing here enters a record, a register or the ledger, and the `local` family is not an approved doctrine seat. Agreement with a recorded reading says the local model was worth reading on these turns; it says nothing about whether any turn is fun.

- endpoint: `http://127.0.0.1:8010/v1`, ctx 131072, temperature 0.0 (greedy)
- model requested / served: C:\models\qwen3.8-27b\Qwen3.8-27B-UD-Q4_K_XL.gguf
- grader id: local-qwen3-8-27b-ud-q4-k-xl
- turns: 12, graded 12, seat refused 0
- wall: 457.0s total, 54520 completion token(s), 24068 prompt token(s)

## Summary

| against | verdict agrees | line agrees | comparable |
| --- | --- | --- | --- |
| claude | 8/12 (67%) | 5/12 (42%) | 12 |
| gpt | 8/12 (67%) | 6/12 (50%) | 12 |

Turns where the local reading made a round-1-class "which card is free" misread: 0/12 (0%).

## Per turn

| turn | local | opus | codex | v. opus | v. codex | line = opus | line = codex | misread | wall s | out tok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| klee-slice1-r3-t03 | REFUSED | SURVIVES | SURVIVES | disagree | disagree | agree | agree | - | 40.0 | 4735 |
| klee-slice1-r3-t04 | REFUSED | SURVIVES | SURVIVES | disagree | disagree | disagree | agree | - | 39.2 | 4831 |
| klee-slice1-r3-t05 | SURVIVES | SURVIVES | SURVIVES | agree | agree | agree | agree | - | 39.2 | 4676 |
| klee-slice1-r3-t06 | SURVIVES | SURVIVES | REFUSED | agree | disagree | disagree | disagree | - | 39.5 | 4720 |
| kokomi-slice2-t01 | SURVIVES | SURVIVES | SURVIVES | agree | agree | disagree | disagree | - | 36.6 | 4601 |
| kokomi-slice2-t02 | SURVIVES | SURVIVES | SURVIVES | agree | agree | disagree | disagree | - | 37.9 | 4517 |
| kokomi-slice2-t03 | SURVIVES | SURVIVES | SURVIVES | agree | agree | disagree | disagree | - | 39.1 | 4589 |
| kokomi-slice2-t04 | SURVIVES | SURVIVES | SURVIVES | agree | agree | disagree | agree | - | 38.6 | 4584 |
| kokomi-slice2-t05 | SURVIVES | SURVIVES | SURVIVES | agree | agree | disagree | agree | - | 27.3 | 3208 |
| kokomi-slice2-t06 | SURVIVES | SURVIVES | SURVIVES | agree | agree | agree | agree | - | 39.1 | 4704 |
| kokomi-slice2-t07 | REFUSED | SURVIVES | SURVIVES | disagree | disagree | agree | disagree | - | 40.2 | 4690 |
| kokomi-slice2-t08 | REFUSED | SURVIVES | REFUSED | disagree | agree | agree | disagree | - | 40.3 | 4665 |

## The lines, in full

### klee-slice1-r3-t03

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Eager to Help -> Rapid Fire -> Duck and Cover
- claude (`opus-5-fresh`): Eager to Help -> Rapid Fire -> Duck and Cover
- gpt (`codex-gpt-5.6-sol-fresh`): Eager to Help -> Rapid Fire -> Duck and Cover
- local's stated line: I played Eager to Help first while the Spark bank was still present, then Rapid Fire at its shown 0 cost, consuming the 3 Sparks, then Duck and Cover for 5 Block. I did not list any drawn cards in the ordered line because their exact printed titles are not on the page, even though the disclosure says the draw pile contains playable 1-energy 7-damage Attacks and I would play any such drawn Attack if it appeared while I still had energy.
- MISREAD (claude): called 'Duck and Cover' 'free', but the packet prints Cost: 1
- MISREAD (claude): called 'Duck and Cover' '0-cost', but the packet prints Cost: 1

### klee-slice1-r3-t04

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Rummage -> Rapid Fire -> Duck and Cover
- claude (`opus-5-fresh`): Rummage -> Rapid Fire
- gpt (`codex-gpt-5.6-sol-fresh`): Rummage -> Rapid Fire -> Duck and Cover
- local's stated line: I played Rummage first, spending 3 Sparks and 1 energy to draw 3 cards. With the Spark bank gone, Rapid Fire reverted to its printed cost of 2, so I played it next for 2 energy, dealing 16 damage to Seapunk. I finished with Duck and Cover for 1 energy, gaining 5 Block before Seapunk’s telegraphed 11 damage attack.
- MISREAD (claude): called 'Rummage' 'free', but the packet prints Cost: 1
- MISREAD (claude): called 'Duck and Cover' 'free', but the packet prints Cost: 1

### klee-slice1-r3-t05

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Rapid Fire -> Kaboom! -> Imaginary Friend
- claude (`opus-5-fresh`): Rapid Fire -> Kaboom! -> Imaginary Friend
- gpt (`codex-gpt-5.6-sol-fresh`): Rapid Fire -> Kaboom! -> Imaginary Friend
- local's stated line: I played Rapid Fire first at Nibbit, using the Spark bank to make it cost 0. Then I played Kaboom! at Nibbit for its printed cost of 1, and finally played Imaginary Friend for 1 energy. This deals 23 total damage, gains 5 Block, and adds the Burst-related value from Imaginary Friend while using all 2 energy.

### klee-slice1-r3-t06

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Rapid Fire -> Kaboom!
- claude (`opus-5-fresh`): Rapid Fire -> Kaboom! -> Duck and Cover
- gpt (`codex-gpt-5.6-sol-fresh`): Rapid Fire -> Kaboom! -> Duck and Cover
- local's stated line: I played Rapid Fire first, using the 3 Spark bank to make it cost 0, then played Kaboom! for its printed cost of 1. This deals 16 damage from Rapid Fire and 7 damage from Kaboom!, for 23 total damage to Nibbit, leaving it at 20 HP. I did not play Slow Burn or Duck and Cover.

### kokomi-slice2-t01

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Gyorin Formation
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Water's Edge
- gpt (`codex-gpt-5.6-sol-fresh`): All Streams Flow to the Sea -> Coral Guard
- local's stated line: I played Gyorin Formation for 2 energy, gaining 10 Block and setting 6 Block for the start of my next turn. The Sludge Spinner's telegraphed 8 damage attack is fully blocked, so I remain at 48 HP and the enemy remains at 34 HP.

### kokomi-slice2-t02

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Gyorin Formation
- claude (`opus-5-fresh`): Sounding Line -> Water's Edge
- gpt (`codex-gpt-5.6-sol-fresh`): Sounding Line -> Coral Guard
- local's stated line: I played Gyorin Formation for 2 energy. It gave 10 Block immediately and set up 6 Block at the start of my next turn, which fully covers the telegraphed 8 damage from Sludge Spinner.

### kokomi-slice2-t03

- local (`local-qwen3-8-27b-ud-q4-k-xl`): All Streams Flow to the Sea -> Read the Current
- claude (`opus-5-fresh`): Read the Current -> All Streams Flow to the Sea
- gpt (`codex-gpt-5.6-sol-fresh`): Read the Current -> All Streams Flow to the Sea
- local's stated line: I played All Streams Flow to the Sea on Nibbit, then Read the Current on Nibbit, using both energy on damage cards because the telegraphed 12 damage is not lethal and no Hydro interaction is stated on the page.

### kokomi-slice2-t04

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Fathom the Tide -> All Streams Flow to the Sea
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Fathom the Tide
- gpt (`codex-gpt-5.6-sol-fresh`): Fathom the Tide -> All Streams Flow to the Sea
- local's stated line: I played Fathom the Tide on Nibbit, spending 6 Charge for its extra 6 damage, then played All Streams Flow to the Sea on Nibbit. This used both energy and dealt the highest known damage available this turn.

### kokomi-slice2-t05

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Gyorin Formation
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Water's Edge
- gpt (`codex-gpt-5.6-sol-fresh`): Gyorin Formation
- local's stated line: I played Gyorin Formation, using both energy to gain 10 Block now and 6 Block at the start of my next turn. Against Nibbit's telegraphed 12 damage, this leaves me taking only 2 damage and keeps the enemy at 34 HP.

### kokomi-slice2-t06

- local (`local-qwen3-8-27b-ud-q4-k-xl`): All Streams Flow to the Sea -> Twin Tides
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Twin Tides
- gpt (`codex-gpt-5.6-sol-fresh`): All Streams Flow to the Sea -> Twin Tides
- local's stated line: I played All Streams Flow to the Sea on Nibbit first for 9 damage, then played Twin Tides and chose Spend 6 Charge: gain 12 Block. This uses both energy, leaves Charge at 2, deals 9 damage, and blocks the telegraphed 12 damage attack.

### kokomi-slice2-t07

- local (`local-qwen3-8-27b-ud-q4-k-xl`): All Streams Flow to the Sea -> Water's Edge -> Coral Guard
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Water's Edge -> Coral Guard
- gpt (`codex-gpt-5.6-sol-fresh`): Coral Guard -> Water's Edge -> All Streams Flow to the Sea
- local's stated line: I played All Streams Flow to the Sea at Sludge Spinner, then Water's Edge at Sludge Spinner, then Coral Guard. This used all 3 energy, dealt 15 damage, and gained 5 Block before the enemy's telegraphed 8 damage attack.
- MISREAD (claude): called 'Rally the Isles' 'free', but the packet prints Cost: 2
- MISREAD (claude): called 'All Streams Flow to the Sea' 'free', but the packet prints Cost: 1

### kokomi-slice2-t08

- local (`local-qwen3-8-27b-ud-q4-k-xl`): All Streams Flow to the Sea -> Water's Edge -> Coral Guard
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Water's Edge -> Coral Guard
- gpt (`codex-gpt-5.6-sol-fresh`): Water's Edge -> All Streams Flow to the Sea -> Coral Guard
- local's stated line: I played All Streams Flow to the Sea on Sludge Spinner, then Water's Edge on Sludge Spinner, then Coral Guard. This uses all 3 energy, deals 15 known damage, and gains 5 Block before the telegraphed 8 damage attack.

