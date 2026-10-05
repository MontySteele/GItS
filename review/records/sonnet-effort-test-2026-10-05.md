# Sonnet effort test: low, medium, high on one seed

2026-10-05. Three blind Sonnet 5.5 seats played the same Ironclad run (seed PPW4N6WX70LS, A0, act 1 only) on build 0.2.4441 (seat page 3, #921), with the same brief and harness. Only the agent's effort setting differed (`.claude/agents/sonnet-seat-low.md`, `sonnet-seat.md`, `sonnet-seat-high.md`). Raw records and transcripts are gitignored.

## Result

| Effort | Act 1 | HP at end | Low point | Actions | Wall time |
|---|---|---|---|---|---|
| low | Vantom killed | 46/80 | 34 | 227 | 14.0 min |
| medium | Vantom killed | 53/80 | 16 | 216 | 12.8 min |
| high | Vantom killed | 38/80 | 30 | 214 | 16.0 min |

All three cleared. Lanes 1 and 3 drafted near-identical Perfected Strike decks on the same route (White Star, act 2 boss Knowledge Demon); lane 2 took another route (Happy Flower, Juggernaut, act 2 boss The Insatiable). One run per level, so a 15-HP spread is noise.

## Tokens by type (from the subagent transcripts)

| Effort | Calls | Fresh input | Cache writes | Cache reads | Context peak | Fresh-input equivalent |
|---|---|---|---|---|---|---|
| low | 125 | 250 | 171k | 10.9M | 171k | 762k |
| medium | 111 | 222 | 132k | 7.6M | 132k | 547k |
| high | 124 | 248 | 171k | 10.3M | 171k | 728k |

Fresh-input equivalent counts cache reads at 1/20 and writes at 1.25. Output and thinking tokens are not usable from the transcripts: `output_tokens` logs about 2k per seat in total, and no thinking text is stored. The only output signal is wall time per call: 6.7 s low, 6.9 s medium, 7.8 s high, so high thinks somewhat longer per turn.

Cost is set by how many calls a seat makes and how big its context grows, because cache reads are about 95% of every seat's bill. Effort did not change either one. Medium was the cheapest here only because its route needed fewer calls.

## Play quality

The mistakes each seat listed are the same kind at every level. On most turns the seat read "Incoming this turn: N", then chose damage over Block and took the hit. Low listed 4 of these, medium listed 3 (one elite fight cost it 46 HP), and high listed 2. High's worst mistake (a Strike played instead of Defend before Dismember, which cost 26) is a mistake low and medium also made. Each level also made one sequencing slip. None of the three seats played noticeably better.

The page lines held up at every level. The enemy briefing changed the elite and boss plans in all three runs (Byrdonis tempo, the Wrigglers after Phrog, Vantom's Slippery count and Dismember), and no seat found a wrong line. Two more findings:
- **Card renumbering:** medium tried three plays in one chained command, and the third failed because the cards had been renumbered after the earlier plays.
- **Rest preview:** low's rest site showed "Heal 24" at 62/80 but healed 18. The heal is capped at max HP (80 − 62 = 18), so the preview should show the capped figure.

## Verdict

Keep medium. Going to high effort did not stop the Sonnet seats from taking unblocked hits, and it cost about the same. This one seed cannot show any difference smaller than that. Raising effort is not the way to close the gap to a human player. A better next step is a page fact that addresses the shared mistake: show the HP the seat would have after this turn's incoming damage if it plays no Block, without recommending a play.
