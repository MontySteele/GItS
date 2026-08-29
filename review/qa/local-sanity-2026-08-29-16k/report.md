# Local model sanity read -- 20260829

WHAT THIS IS. A local model re-read turns that are already CLOSED, and its reading is printed beside the two that are recorded. It is SUBJECTIVE FEEDBACK about the READER.

WHAT THIS IS NOT. Not human validation. Not balance evidence. Not a grade: nothing here enters a record, a register or the ledger, and the `local` family is not an approved doctrine seat. Agreement with a recorded reading says the local model was worth reading on these turns; it says nothing about whether any turn is fun.

- endpoint: `http://127.0.0.1:8010/v1`, ctx 131072, temperature 0.0 (greedy)
- model requested / served: C:\models\qwen3.8-27b\Qwen3.8-27B-UD-Q4_K_XL.gguf
- grader id: local-qwen3-8-27b-ud-q4-k-xl
- turns: 7, graded 5, seat refused 2
- wall: 1508.7s total, 98675 completion token(s), 14347 prompt token(s)

## Summary

| against | verdict agrees | line agrees | comparable |
| --- | --- | --- | --- |
| claude | 4/5 (80%) | 4/5 (80%) | 5 |
| gpt | 5/5 (100%) | 1/5 (20%) | 5 |

Turns where the local reading made a round-1-class "which card is free" misread: 0/5 (0%).

## Per turn

| turn | local | opus | codex | v. opus | v. codex | line = opus | line = codex | misread | wall s | out tok |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| klee-slice1-r3-t03 | REFUSED-SEAT (answer_truncated) | SURVIVES | SURVIVES | n/a | n/a | n/a | n/a | - | 256.3 | 16384 |
| klee-slice1-r3-t04 | REFUSED-SEAT (answer_truncated) | SURVIVES | SURVIVES | n/a | n/a | n/a | n/a | - | 276.4 | 16384 |
| klee-slice1-r3-t05 | SURVIVES | SURVIVES | SURVIVES | agree | agree | agree | agree | - | 252.1 | 15902 |
| klee-slice1-r3-t06 | REFUSED | SURVIVES | REFUSED | disagree | agree | disagree | disagree | - | 193.4 | 13293 |
| kokomi-slice2-t01 | SURVIVES | SURVIVES | SURVIVES | agree | agree | agree | disagree | - | 148.4 | 10208 |
| kokomi-slice2-t02 | SURVIVES | SURVIVES | SURVIVES | agree | agree | agree | disagree | - | 171.9 | 11975 |
| kokomi-slice2-t04 | SURVIVES | SURVIVES | SURVIVES | agree | agree | agree | disagree | - | 210.2 | 14529 |

## The lines, in full

### klee-slice1-r3-t03

- local: SEAT REFUSED `answer_truncated` -- the answer stopped at the token ceiling, so the form is incomplete and is not a partial grade
- claude (`opus-5-fresh`): Eager to Help -> Rapid Fire -> Duck and Cover
- gpt (`codex-gpt-5.6-sol-fresh`): Eager to Help -> Rapid Fire -> Duck and Cover

### klee-slice1-r3-t04

- local: SEAT REFUSED `answer_truncated` -- the answer stopped at the token ceiling, so the form is incomplete and is not a partial grade
- claude (`opus-5-fresh`): Rummage -> Rapid Fire
- gpt (`codex-gpt-5.6-sol-fresh`): Rummage -> Rapid Fire -> Duck and Cover

### klee-slice1-r3-t05

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Rapid Fire -> Kaboom! -> Imaginary Friend
- claude (`opus-5-fresh`): Rapid Fire -> Kaboom! -> Imaginary Friend
- gpt (`codex-gpt-5.6-sol-fresh`): Rapid Fire -> Kaboom! -> Imaginary Friend
- local's stated line: I played Rapid Fire first at its shown 0 cost, consuming the 3 Spark bank; with one enemy, its random hits land on Nibbit. Then I played Kaboom! at Nibbit for 1 energy, and finally Imaginary Friend for 1 energy. This deals 23 damage, leaving Nibbit at 20 HP, gives 5 Block, and gains the printed Burst effects.

### klee-slice1-r3-t06

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Rapid Fire -> Duck and Cover -> Kaboom!
- claude (`opus-5-fresh`): Rapid Fire -> Kaboom! -> Duck and Cover
- gpt (`codex-gpt-5.6-sol-fresh`): Rapid Fire -> Kaboom! -> Duck and Cover
- local's stated line: I played Rapid Fire at Nibbit for its shown 0 cost, consuming all 3 Sparks, then Duck and Cover for 1 energy, then Kaboom! at Nibbit for its printed 1 cost. This dealt 16 damage from Rapid Fire and 7 damage from Kaboom!, for 23 total, and gained 5 Block.

### kokomi-slice2-t01

- local (`local-qwen3-8-27b-ud-q4-k-xl`): All Streams Flow to the Sea -> Water's Edge
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Water's Edge
- gpt (`codex-gpt-5.6-sol-fresh`): All Streams Flow to the Sea -> Coral Guard
- local's stated line: I played All Streams Flow to the Sea on Sludge Spinner, then Water's Edge on Sludge Spinner, using both energy. This deals 9 damage then 6 damage, for 15 total, and applies Hydro with each card as printed.

### kokomi-slice2-t02

- local (`local-qwen3-8-27b-ud-q4-k-xl`): Sounding Line -> Water's Edge
- claude (`opus-5-fresh`): Sounding Line -> Water's Edge
- gpt (`codex-gpt-5.6-sol-fresh`): Sounding Line -> Coral Guard
- local's stated line: I played Sounding Line at Sludge Spinner, spending 6 Charge for 12 damage and Hydro, then played Water's Edge at Sludge Spinner for 6 damage and Hydro. This used both energy, left the enemy at 16 HP, and I would take the telegraphed 8 damage, ending at 40 HP.

### kokomi-slice2-t04

- local (`local-qwen3-8-27b-ud-q4-k-xl`): All Streams Flow to the Sea -> Fathom the Tide
- claude (`opus-5-fresh`): All Streams Flow to the Sea -> Fathom the Tide
- gpt (`codex-gpt-5.6-sol-fresh`): Fathom the Tide -> All Streams Flow to the Sea
- local's stated line: I played All Streams Flow to the Sea on Nibbit first, then Fathom the Tide on Nibbit. All Streams is played before Fathom because the disclosure says it reads Charge at one point per two Charge, so it deals 11 at Charge 12. Fathom then spends 6 Charge for 13 damage. Total is 24 damage and two Hydro applications, leaving Charge 6.

