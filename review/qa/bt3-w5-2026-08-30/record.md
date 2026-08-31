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

## `KLEESPARK-BT3` — RUN, and the grade

Full results at packet §25.5. In one line each: **`G1` UNREACHED** (both
deciding Codex forms REFUSED `intent_insensitive` — the slot's own rule),
**`G2` UNREACHED** (its declared subset), **`G3` PREDICTED 2 of 2** (both forms
carried the forecast; `EB-239`'s repair holds on its second round), **`G4`
UNREACHED** (`EB-209`). Both boards staged clean on the re-drafted relics.

The refusals are not the graders'. Both boards declared *"one enemy
telegraphing an attack for 16"*; live, `t01` drew a **Debuff** intent and `t02`
an attack for **12**. `EB-240`'s `expects:` has no `intent` leg → **`EB-244`**.

Codex: 2 calls of a cap of 6. The pair read was not taken (§25.5.4).

## `KLEESPARK-W5` — RUN, and the grade

Sealed session `20260831-022129`, seed `UVPVUS1BVEQ0`, 40 actions, 19 combat
pages, forecast channel ON and answered on all 19. Full results at §25.6.

| slot | grade |
|---|---|
| `B1` R230's collapse condition | **UNREACHED** — 1 opportunity page against a floor of 4. **The collapse did not fire and could not have.** |
| `B2` the one-Spark trade NAMED | **PREDICTED** (threshold 1, observed 6) |
| `B3` the up-front liquidity BINDS | **PREDICTED** (threshold 1, observed 3 of 5 pages the card reached hand) |
| `B4` the delayed refund at fight scale | **MISSED** on its registered falsifier, denominator one take |
| `B5` | recorded: peak bank 2 / 2 / 4, priced takes 1, free takes 0, preserved-Spark reasons 6 of 19 |

Preconditions all checked: soak gate `fights=3 defects=0`, pck contract diff
empty, printed-Spark-price stop rule checked page by page (Ka-pow! 1, the
sheet's, no disagreement), Neow's only deck-neutral boon (*Silken Tress*) taken
by the operator per `W4` §19.5.

Minted here: **`EB-245`** (a `card_select` overlay triggers a phantom fight
record — the sealed record carries FOUR for THREE fights) and **`EB-246`**
(BBCode leaks into a printed option name). Neither touched a graded slot.

| meter | reading |
|---|---|
| before BT3 | 5h 0% (rolled over) / week 28% |
| after BT3's second deciding read | 5h 0% / week 35% |
| before W5 | 5h 0% / week 35% |
| after W5 | 5h 1% / week 0% (rolled over, resets Sep 06 22:26) |

## `KURAGECAD-W1` — RUN, and the grade

**NOT blocked.** The deployed world was proven to carry what §15.8 assumes
before the session, read-only and five ways (§15.9.0): the manifest reads
`0.2.1786+proto.dirty`; `embark --arm proto_kurages_oath_memory` was accepted,
which `--arm` refuses on a non-`+proto` build; `Kokomi.StartingDeck` slot eleven
is `#if PROTOTYPE_CARDS → KurageMemory.StarterSlotEleven()`; `KurageMemory` and
`KurageMemoryCard` are both in the deployed `klee.dll` with
`KurageMemoryLaw.AlwaysOn = true`; and every one of the 22 wire snapshots
carries a populated `kurage_memory` block with `base_kit: true`.

Sealed session `20260831-023544`, seed `0EEMNL2RE8UY`, 40 actions, 22 combat
pages, all three forecast questions answered on all 22. Full results §15.9.

| slot | grade |
|---|---|
| `K1` readability | **half (a) PASS 6 of 6**; **half (b) UNREACHED** (`run_out_index` −1 on every page) |
| `K2` the live cadence | **SPLIT** — 3 fires ÷ 22 pages = 13.6%, inside the 10%–<25% band |
| `K3` the tail | **UNREACHED** — peak queue 3, no page reached 4 |
| `K4` is it hers? | **SPLIT** — 3 STEERs on the first 10 pages, none naming a Muster door |
| `K5` the block | **UNREACHED** — zero blocked pages |
| `K6` | recorded: 2 of 3 fires at price 0, 6 exhaust / 1 muster, 0 blocked, peak 3 and 2, fires 2 and 1, all five granted rows reached play |

**One cause, three UNREACHEDs: the Charge was never scarce.** The enriched
stress deck over-samples enrolment and under-samples scarcity, and scarcity is
what `K1`(b), `K3` and `K5` were about. `EB-198` is half discharged and stays
OPEN. Minted: **`EB-247`** (the jellyfish's text disagrees with its pulse) and
**`EB-248`** (a discounted entry's price is not derivable from the printed
face). No number, threshold or constant moved; no [USER] row opens.

Meter: **5h 1% / week 0%** before, **5h 8% / week 1%** after.
