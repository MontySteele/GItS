Status: RECORD

# The card audit of 2026-09-07: six adjusted prototype rows read by GPT before a tester sees them

Written 2026-09-07. The six rows were adjusted on
`claude/card-deck-balance-review-p2oxjx` on 2026-09-06 while the local
machine was offline (`EB-507`, `EB-616`, `EB-617`, all D defaults from the
GPT balance review of that day), and the branch said in three places that
the audit door had to read them on the local machine before a deploy. It did
this morning, through `understudy.seat review --role doctrine` on the Codex
bridge, from `review/qa/card-adjustments-2026-09-06-prompt.txt`; the reply
is `review/qa/card-adjustments-2026-09-06-reply.md`, its usage read beside
it. Every row was written by Claude, so the reviewer is GPT (R217 C). The
reviewer names a clause and a line; it supplies no number and no remedy,
and none was used.

## 1. The verdicts

| # | Row | Kit | Verdict | Clause named, and the comparison |
|---|---|---|---|---|
| 1 | Long Fuse (escalation off) | Klee | **FOLLOWS** | C2, C6: loses 6 damage to Sizzle on a reaction turn; Retain trades damage for reliable access; no dominance over Pocket Match (Spark-priced) or Ka-pow! |
| 2 | Florid Cadenza (arm copy, Exhaust, bar 6 to 3 on upgrade) | Furina | **FOLLOWS** | C2, C6: draws 2 fewer than Skim below its gate; gains 2 less Energy than Adrenaline; three copies Exhaust after three plays, so the holding loop is gone |
| 3 | Shared Billing (arm copy, upgrade gains 3 Block) | Furina | **FOLLOWS** | C2, C6: 0 net Energy and one hand card per play, no cycle; draws 1 fewer than Limelight |
| 4 | Rapturous Applause (arm copy, 2 per 10 Fanfare) | Furina | **REQUIRES_MODIFICATION** | C8: the floor's removal answers the unearned-Fanfare objection, but doubling the shipped 1-per-10 payout is a payout change, and C8 permits the threshold only |
| 5 | Unheard Confession (arm copy, 2 Block per change) | Furina | **FOLLOWS** | C3, C5: 0 surviving Block on a decay-only turn; 6 usable Block on a turn the player pays for two performances and a drain |
| 6 | Let the People Rejoice (enters the offer, 2 per drained) | Furina | **FOLLOWS** | C1, C6: 25 to Universal Revelry's 20 at 10 Fanfare but 5 to its 9 at 0, and it empties the meter; neither version dominates |

## 2. What was done with row 4

The clause is the threshold clause, and the row takes the threshold mapping
the other arm copies took on 2026-09-04 (shipped 20-to-30 meter halved for
the arm's 0-to-15): **1 additional damage per 5 Fanfare**, upgrade 2 per 5.
The slope is the one the branch wanted; the granularity is what C8 fixes.
That is Claude's design call (the reviewer's remedy ban is intact: it named
the clause and nothing else), built on both engines the same morning as
`fanfare_attack_per5` beside the shipped per-10 power, and read again at the
door as a single arm; §3 records that read.

## 3. The re-read of row 4

Second call, the same morning, one arm
(`review/qa/card-adjustments-2026-09-07-arm4-prompt.txt`, reply beside it):
**FOLLOWS, C8** -- "changes the shipped threshold from 10 to 5 while
preserving the base payout of 1, answering the prior C8 objection; on a
turn at 10 Fanfare the arm adds 2 damage per Attack versus the shipped
row's 1, matching the shipped bonus at 20 Fanfare within the stated economy
mapping, while removing the shipped 'Fanfare +8, and cannot fall below 8'."

Six rows go to the testers. Nothing is withdrawn.

## 4. Provenance

- Prompts: `review/qa/card-adjustments-2026-09-06-prompt.txt` (six arms; the
  file now carries the per-5 row, the first reading of arm 4 is quoted in
  its reply) and `review/qa/card-adjustments-2026-09-07-arm4-prompt.txt`.
- Replies: `review/qa/card-adjustments-2026-09-06-reply.md` and
  `...-2026-09-07-arm4-reply.md`; Codex meter at both calls: 0% of the
  five-hour window, 0% of the week (both rolled over).
- Nothing measured here is quotable (R215 B); Prototype stage, no slate, no
  countersign, no register re-baseline.
