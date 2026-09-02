# `funnel-bench-1` -- the throughput bench, INSTRUMENT ONLY

Six boards, byte-for-byte copies of `KLEESPARK-R2`'s (`understudy/turns/klee-sparks-r2/`)
under new ids, with R2's `slots.yaml` beside them so the plan and the stopping
rule are the same shape. It exists to put a number on `--lanes 2 --read-workers 2`
(EB-206, EB-210, `serve.ps1 -Parallel 2`) against R2's single-lane 372 s, and
for nothing else: the seat reads in the SHADOW chair (R222 B), no deciding form
is taken, no replay runs, no Codex spot-check is taken (`--seat-spot-check 0`),
and no verdict here is a reading about any card. `review/qa/funnel-bench-1-record.md`
and the round's rows in `review/qa/ledger.tsv` are the evidence in HEAD; the
per-turn directories left HEAD at `EB-189` (2026-09-02) and read at
`git show e85d1309:review/qa/funnel-bench-1-t01/observed.json`. `OPERATIONS.md`
(*Local tester seat*) carries the number.
