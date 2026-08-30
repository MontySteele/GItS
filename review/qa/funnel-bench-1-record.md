# `funnel-bench-1` — the first two-lane, two-worker round, timed

**Instrument only.** Six boards, byte-for-byte copies of `KLEESPARK-R2`'s under
bench ids (`understudy/turns/funnel-bench-1/`), run 2026-08-30 with
`--lanes 2 --read-workers 2 --first 0 --seat-spot-check 0` in the SHADOW chair
(R222 B). No deciding form was taken, no replay ran, no Codex call was spent, and
no verdict here is a reading about any card. The question was one number: what
does the pipeline built after `KLEESPARK-R2` (§13.5 of the Klee Sparks packet:
372 s, single lane, one reader) buy on the same six boards?

| | `KLEESPARK-R2` (2026-08-30, one lane, one reader) | `funnel-bench-1` (two lanes, two readers) |
|---|---|---|
| build | `0.2.1517+proto.dirty` | `0.2.1543+proto.dirty` |
| launches | 7 (one per lane per board, plus the first) | 8 (4 per lane: 1 launch + 3 relaunches each) |
| stage, all six boards | 89 s (14.8 s / board, one lane) | **93 s** wall (22:19:20 → 22:20:53): each stage took ~30 s with two games up, so two lanes bought nothing here |
| read + grade | 295 s (49.2 s / board, back to back for 313 s) | **219 s** wall (22:19:51 → 22:23:30): reads paired at 68–80 s each, **~37 s / board effective** |
| replay | 124 s over three surviving lines | none — shadow chair, no deciding form, all six OWED |
| launch → teardown | ~313 s to the last read; 372 s with replays | **251 s** (22:19:20 → 22:23:31) |
| Codex calls | 3 | **0** |
| seeds honoured | 6 of 6 (single lane) | **6 of 6, no crossing** (`EB-210`'s fix, first time in a full round) |

**What the number says.** The model half is where the round is, and two server
slots shorten it: six reads in 219 s against 295 s, a **1.35×** throughput gain
on the read phase, below the 1.76× two raw generations measured on the server
(`OPERATIONS.md`, *Local tester seat*) because each funnel read also carries a
~10–15k-token prompt whose processing competes for the same GPU. A paired read
took ~74 s where a solo read took 49 s. The game half did NOT gain: with two
processes up, each stage stretched from ~15 s to ~30 s, so six stages on two
lanes took the 93 s that six stages on one lane took. Two lanes are worth
having for what they proved (`EB-206`/`EB-210`: seeds route to the right
process under load), not for time — on this machine the second game competes
with the first for the same CPU/GPU, and the honest stage figure is a wash.

**Stage + read wall clock: 251 s against R2's ~313 s, 1.25× — with replays
excluded on both sides.** A graded round adds its replays (R2: 124 s over three
lines) and its deciding forms, which are produced outside the funnel, so a
graded two-lane, two-worker round should expect roughly 250 s + replays.

**The shadow seat refused 6 of 6.** On the identical boards `KLEESPARK-R2`'s
shadow read refused 4 of 6 (`t02`, `t06` SURVIVED there and were refused here,
`intent_insensitive` and `no_second_line`). That is a fact about the local seat's
run-to-run consistency on the same packet, recorded here because it was seen;
it decides nothing (the seat is in shadow, R222 B) and it is not a defect in the
funnel. It belongs to the requalification battery's evidence (R223), not to any
arm.

**Evidence.** `review/qa/funnel-bench-1-t0{1..6}/` (packet, shadow form, verdict,
`observed.json`), `review/qa/funnel-bench-1-round-summary.json`
(`read_workers: 2`, `read_completion_order`), the round's timestamped stdout at
`understudy/logs/funnel-bench-1-round.log` (gitignored; the timestamps above are
read off it), and the ledger rows (`role: shadow`, `instance: lane0/lane1`).
