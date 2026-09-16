# proofs-10, lane 1 — the two frames

Material for a person to look at, captured by pid from **lane 1's disposable profile** on the
`0.2.3581+proto.dirty` deploy. Read them with
`review/records/teyvat-proofs-10-lane1-2026-09-16.md`, which is where every claim made off them
lives.

**Nothing here is a measurement.** Both boards were written by hand (`set_hp`, `set_power`,
`give_card`), and the record's honesty preamble counts every write. A frame proves a pixel, not
a judgement: nothing a bot or an LLM derives from one is a claim about look, legibility or fun
(Guardrail-7).

| frame | what it is for | what to look at |
|---|---|---|
| `frame-20260916-164937-eb159-modded-player-death.png` | `EB-159` | the header reads `0/62` and the wire already said `game_over`, yet the client is still on the combat board: Klee's body drawn under the death vignette with her bar replaced by **`Dead`**, the Sludge Spinner still at 33/33, the killing `8` still floating. |
| `frame-20260916-165245-eb791-eb780-curtain-rise-mode-chooser.png` | `EB-791`, `EB-780` | the two option cards' **titles** carry no `[gold]` bracket (`EB-791`), and their **bodies** read `Deal 7 damage` / `Spend 3: deal 12 instead` — the hand's Weak-folded pair (`EB-780`). The titles' `13` against the body's `12` is off-list defect 1. |

`frames-manifest.jsonl` carries both rows. Both say `"complete": true` —
*the frame covers the whole client area*, `3842 2160` client against `3842 2160` drawn at
`render_scale [1.0, 1.0]`, route `printwindow` — which is `EB-788`'s fix (#589) reporting on
itself. Both rows say `"instance": "lane0"`, which is wrong and is off-list defect 4; the `pid`
field (7716, 13032) is the one that is right.
