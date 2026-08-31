# Live game window, phase 2 — 2026-08-30

`KLEESPARK-BT3`, `KLEESPARK-W5` and `KURAGECAD-W1`, run on the art-bearing main
checkout. Phase 1 of tonight's window is `review/qa/live-acceptance-2026-08-30/`;
this window re-establishes its run legs and does **not** rebuild the pack.

## Build — REUSED, and the reuse is proven

`git diff --stat cc6f323c HEAD -- klee-mod/ ImageGen/ tools/build_pck.ps1
docs/prototype-surface.yaml docs/klee-cards.yaml docs/kokomi-cards.yaml
docs/furina-cards.yaml` is **empty**: nothing under the mod or pck source paths
differs from what `0.2.1786+proto.dirty` was built from, so the installed pack
is reused rather than rebuilt.

| fact | value | read from |
|---|---|---|
| package | `0.2.1786+proto.dirty` (dev, `-p:PrototypeCards=true`) | `mods\klee\manifest.json` |
| game | v0.111.0, `public-beta`, appid 2868840 | the pin |
| branch | `bt3-w5-run`, cut from `wave-2026-08-30-night` `df952bb1` | |

## Codex meter, unsmoothed

| when | reading |
|---|---|
| before the window | **5h 0% (rolled over) / week 28%** (resets Sep 05 17:58) |

## `EB-243` — the gift read off the wire, and the re-draft

Both BT3 boards registered the run-start gift as *Fishing Rod*. Each board was
staged **AS COMMITTED** and its refusal taken as the reading — no board was
edited before the wire was read:

| board | seed | the wire's relics | the declared pair |
|---|---|---|---|
| `klee-sparks-bt3-t01` | `YX7PB48WR7R4` | *Pounding Surprise*, **Stone Humidifier** | *Pounding Surprise*, *Fishing Rod* |
| `klee-sparks-bt3-t02` | `R805DJ56LZHM` | *Pounding Surprise*, **Scroll Boxes** | *Pounding Surprise*, *Fishing Rod* |

**A DIFFERENT gift on each seed.** The registered single name assumed the gift
was a constant of the staging path; it is seed-derived. Both `expects.relics`
blocks are re-drafted to what is true now, disclosed in each board and in the
MANIFEST, and committed **before** the round ran (`98392747`). R212: a moved
world means re-draft and disclose, never re-sign — the R231 countersign stands,
the slate `G1`–`G4` is untouched and no threshold moves. Both `hp.first` legs
(40 and 46) matched the wire unchanged. `EB-243` leaves `BACKLOG.md` and
`OPEN_IDS` on its acceptance word for word, *"both BT3 boards stage"*.

## `KLEESPARK-BT3` — the schedule, committed before the round

```
round of 2 board(s) in R221 B's pre-registered order; seat spot-check every 1; first set = 2; lanes = 1
   1  FIRST  SEAT  lane0  klee-sparks-bt3-t01   slots=C1  closeness=0.135
   2  FIRST  SEAT  lane0  klee-sparks-bt3-t02   slots=C1  closeness=0.135
preflights: every board passes face-defect and assumption checks
SLOT OK   C1: threshold 2, ceiling 2 of 2 board(s)  [klee-sparks-bt3-t01, klee-sparks-bt3-t02]
board design: every board forces a trade, and every declared exclusive pair is exclusive
```

Identical to the plan §25.2 printed before the round was registered, with the
spot-check rate at 1 as §25.2 directs (the Codex seat decides every board — a
DESIGN round under `M64`(1) / R224; fresh-Opus is not seated, the row being
`authored_by: [claude]`; the local seat sits SHADOW).
