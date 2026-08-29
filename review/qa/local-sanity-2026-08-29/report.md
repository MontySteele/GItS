# Local model sanity read -- 20260829

WHAT THIS IS. A local model re-read turns that are already CLOSED, and its reading is printed beside the two that are recorded. It is SUBJECTIVE FEEDBACK about the READER.

WHAT THIS IS NOT. Not human validation. Not balance evidence. Not a grade: nothing here enters a record, a register or the ledger, and the `local` family is not an approved doctrine seat. Agreement with a recorded reading says the local model was worth reading on these turns; it says nothing about whether any turn is fun.

- endpoint: `http://127.0.0.1:8010/v1`, ctx 131072, temperature 0.0 (greedy)
- model requested / served: C:\models\qwen3.8-27b\Qwen3.8-27B-UD-Q4_K_XL.gguf
- grader id: local-qwen3-8-27b-ud-q4-k-xl
- turns: 4, graded 4, seat refused 0
- wall: 377.2s total, 23149 completion token(s), 7789 prompt token(s)

## Summary

| against | verdict agrees | line agrees | comparable |
| --- | --- | --- | --- |
| claude | 2/4 (50%) | 2/4 (50%) | 4 |
| gpt | 3/4 (75%) | 1/4 (25%) | 4 |

Turns where the local reading made a round-1-class "which card is free" misread: 0/4 (0%).

## Per turn

| turn | local | opus | codex | v. opus | v. codex | line = opus | line = codex | misread | wall s | out tok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| kokomi-slice2-t05 | SURVIVES | SURVIVES | SURVIVES | agree | agree | disagree | agree | - | 99.0 | 6795 |
| kokomi-slice2-t06 | SURVIVES | SURVIVES | SURVIVES | agree | agree | disagree | disagree | - | 110.0 | 6644 |
| kokomi-slice2-t07 | REFUSED | SURVIVES | SURVIVES | disagree | disagree | agree | disagree | - | 84.6 | 4631 |
| kokomi-slice2-t08 | REFUSED | SURVIVES | REFUSED | disagree | agree | agree | disagree | - | 83.6 | 5079 |

## The lines, in full

### kokomi-slice2-t05

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Gyorin Formation
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Water's Edge
- gpt (`codex-gpt-5.6-sol-fresh`): Gyorin Formation
- local's stated line: I played Gyorin Formation for 2 energy. It gave me 10 Block and set up 6 Block at the start of my next turn. Against Nibbit's telegraphed 12 damage Attack, that leaves me taking 2 damage and ending the turn at 46 HP.

### kokomi-slice2-t06

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Twin Tides -> All Streams Flow to the Sea
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Twin Tides
- gpt (`codex-gpt-5.6-sol-fresh`): All Streams Flow to the Sea -> Twin Tides
- local's stated line: I played Twin Tides, choosing Spend 6 Charge: gain 12 Block, then played All Streams Flow to the Sea on Nibbit. This used both energy, left 2 Charge, gave 12 Block against the telegraphed 12 Attack, and dealt 9 damage.

### kokomi-slice2-t07

- local (`local-qwen3-8-27b-ud-q4-k-xl`): All Streams Flow to the Sea -> Water's Edge -> Coral Guard
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Water's Edge -> Coral Guard
- gpt (`codex-gpt-5.6-sol-fresh`): Coral Guard -> Water's Edge -> All Streams Flow to the Sea
- local's stated line: I played All Streams Flow to the Sea and Water's Edge on Sludge Spinner, then Coral Guard, using all 3 energy for 15 damage and 5 Block.
- MISREAD (claude): called 'Rally the Isles' 'free', but the packet prints Cost: 2
- MISREAD (claude): called 'All Streams Flow to the Sea' 'free', but the packet prints Cost: 1

### kokomi-slice2-t08

- local (`local-qwen3-8-27b-ud-q4-k-xl`): All Streams Flow to the Sea -> Water's Edge -> Coral Guard
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Water's Edge -> Coral Guard
- gpt (`codex-gpt-5.6-sol-fresh`): Water's Edge -> All Streams Flow to the Sea -> Coral Guard
- local's stated line: I played All Streams Flow to the Sea on Sludge Spinner, then Water's Edge on Sludge Spinner, then Coral Guard. This used all 3 energy, dealt 15 damage, applied Hydro with each damage card, and gained 5 Block.

