# Probe (d) — `Aria of Recompense`'s unreconstructed Block: MEASURED, the divergence closes

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

> **Run 2026-08-06, Track M (wave 8), under the COUNTERSIGNED registration
> `docs/probe-d-registration-draft.md` (R120 / 10.13, [USER] verbatim
> *"countersigned"*).** Results adjudicate **B2's declared residual and
> nothing else**; Guardrail 7 unchanged. No constant, card, sheet or rule was
> touched. Zero design authority exercised.

## The pre-registered question, verbatim, and the answer

> "Does `Aria of Recompense`'s Block divergence close when the recorded
> Fanfare meter is loaded into the reconstruction, the way C1's divergences
> closed when the recorded status strip was?"

**YES — all five declared divergences close to zero, and they close on the
AFTER-play meter reading.** Layer 1 (reconstruction input) is the verdict,
with the layer-2 fork resolved as a resolution-order fact: the engine's
Block for `1_per_4_fanfare` corresponds to the meter **after** the play's own
Fanfare income has landed, not before.

| layer (registration table) | outcome |
|---|---|
| 1 — reconstruction INPUT gap | **YES — left standing.** Family B, exactly like C1: the replay never had the reading. Closes all five. |
| 2 — read timing | Resolved, not left standing as a defect: **AFTER-play** is the reading the engine matches (38/38); BEFORE-play misses exactly one row (37/38). Recorded as a resolution-order fact per the registration's licence. |
| 3 — arithmetic pipeline | **Dead over this corpus.** With the meter loaded, tier0's `n * (readable // m)` + Frail truncation reproduces every engine value exactly. |
| 4 — clamp/meter-state fields | **Inert over this corpus.** Recorded meter ranged 0–30, `KLEEMOD_FANFARE_CAP_BONUS` = 0 and `KLEEMOD_FANFARE_FLOOR` = 0 on every reading; the reconstruction pinned `fanfare_cap=999`, `fanfare_floor=0` (printed in the table header), so no clamp was load-bearing. |

## Corpus

Per the registration's method step 1 and its cost-class "expected" shape:

- **center arm** — the stamped re-run with `resources` recorded already on
  the machine: `probe-b2-center-20260805-132001.jsonl` (49 readings, rounds
  1–8, `KLEEMOD_FANFARE` present on all 49).
- **guest arm** — re-taken live 2026-08-06 (the old guest stamp
  `20260805-125933` carries no `resources`, exactly as the registration
  predicted): `probe-b2-guest-20260806-023042.jsonl`, produced by the B2
  script verbatim —
  `python -m understudy.probe_block --spotlight guest --seed TRACKB2
  --max-fights 1 --turns 8` (48 readings, one fight, 58.2 s wall).
- Analysis: `python -m tools.probe_b2_table <the two logs above> --meters`
  — the registration's one new column plus its sub-fork, landed in
  `tools/probe_b2_table.py`.

**Wire-freeze check (confounder 9): PASSED.** The re-taken guest arm's
table output without `--meters` is **byte-identical** to the same table run
over B2's original guest log (`probe-b2-guest-20260805-125933.jsonl`) —
every engine Block increment, every Frail stack, every pairing reproduces.
The two corpora are the same corpus. Deployed mod at run time: `0.2-296`
(`mods/klee/manifest.json` in the game directory); the fight is floor-1 and
touches neither of v6's changed surfaces (boss-room Frozen scope, shop
odds).

## The readings

Divergence distributions over the 38 pairings (both arms, rounds 1–8; the
B2 reproduction rows are the first two lines and match B2's published
distribution exactly):

```
selector-known, status-BLIND  : {-4: 2, -3: 1, -1: 2, 0: 7, 1: 11, 2: 15}  agree=7/38
selector-known, status-LOADED : {-4: 2, -3: 1, -1: 2, 0: 33}               agree=33/38
status+meter (PRE-play)       : {-1: 1, 0: 37}                             agree=37/38
status+meter (POST-play)      : {0: 38}                                    agree=38/38
```

The five declared Aria divergences, with the recorded meter beside them:

| arm | rnd | frail | engine | `sim_status` | fanfare pre → post | `sim_m_pre` | `sim_m_post` |
|---|---|---|---|---|---|---|---|
| center | 1 | 0 | 1 | 0 | 4 → 6 | 1 | **1 = engine** |
| center | 3 | 3 | 3 | 0 | 14 → 16 | 2 | **3 = engine** |
| center | 6 | 4 | 4 | 0 | 24 → 26 | 4 | **4 = engine** |
| center | 7 | 3 | 4 | 0 | 24 → 26 | 4 | **4 = engine** |
| guest | 7 | 3 | 1 | 0 | 8 → 8 | 1 | **1 = engine** |

The single PRE-play miss is center round 3: meter 14 before the play
(`14 // 4 = 3`, Frail → 2) vs 16 after (`16 // 4 = 4`, Frail → 3 = engine).
That one row is what forks layer 2: the engine's read includes the play's
own income. Every non-Aria row is unchanged by the new columns' presence
(method step 5's instrument check).

## Confounders, dispositions (registration order)

1. **Frail** — present (stacks 0–4 across the corpus). Shown as arithmetic
   in the table above: Frail truncation composes AFTER the Fanfare division,
   identically in both instruments. Layer-3 component dead.
2. **Spotlight arm** — declared input. The guest arm's meter is low (6–8 vs
   center's 14–30) and is the natural low-meter contrast, read as such.
   **Factual note owed to B3's owner, not adjudicated here:** B3 Ledger 2
   recorded *zero* Fanfare income in the guest arm; this re-take's wire shows
   `KLEEMOD_FANFARE` reaching 8 in the guest arm. This probe reads the
   recorded meter as input and makes no claim about generation (B3 owns
   generation); the discrepancy is surfaced, not resolved.
3. **The `+2` first-Spotlight optimism (B3 term 3)** — not load-bearing
   here: the reconstruction loads the ENGINE's own recorded meter, so
   tier0's crediting rule never runs. No subtraction needed; stated so it is
   not re-discovered.
4. **Encore** — logged: Aria's `gain_encore: 5` moved `KLEEMOD_ENCORE`
   (0–3 observed). It does not feed Block; these rows are not evidence about
   Encore.
5. **Upgrade state** — the base `Aria of Recompense` (not `+`) was in the
   deck in both arms; no `innate` draw-order effect.
6. **Clamps** — layer 4 row above: inert, and determinable from the wire.
7. **Salon empty throughout** — same coverage caveat as every measurement to
   date.
8. **One character, one card, one encounter, one seed** — no breadth claim.
9. **Wire freeze** — checked and passed (byte-identical reproduction, above).

## What this licenses, per the registration — and what it does not

- The Aria residual is **reclassified family B: a reconstruction gap in
  `understudy/replay.py`'s input**, the same verdict C1 received. The S7
  ledger note is owed by whoever owns that ledger's next pass; this document
  is the citation.
- **Resolution-order fact recorded:** the engine's `1_per_4_fanfare` Block
  matches the meter **after** the play's own Fanfare income lands.
- NOT licensed, and not claimed: anything about Fanfare generation or decay
  (B3's), anything about the other `bonus_formula` readers (one card was
  measured), any change to the fight record's contents (whether the record
  *should* carry the meter is a ruling), any escrowed number.

**B2's declared residual is adjudicated: no arithmetic infidelity survives
the reconstruction.** The probe grades nothing, re-opens nothing, and moves
no escrowed number.
