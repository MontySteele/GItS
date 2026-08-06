# Probe B2 (S7 probe (a)) — the +2 block offset

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Date: 2026-08-05. Authority: R103, probe order (c) → **(a)** → (b). Input: the
S7 audit's C1 cluster (`docs/s7-fidelity-audit.md` §4.1,
`docs/s7-classification.md` family C). This is a **live measurement**: the game
was launched, two scripted fights were driven through the P1.5 bridge, and the
numbers below came off the wire.

**Zero design authority was exercised.** No constant, card, sheet or rule was
touched. No mod behaviour was changed; the P1.5 wire was frozen for this pass.
Nothing here re-grades any ratified result, and no number below is a balance
finding (Guardrail 7 unchanged).

---

## The pre-registered question, verbatim

> "Does the +2 block offset (C1 candidate) reproduce in a minimal fight with
> relics stripped and a fixed script?"

## The answer

**YES — it reproduces, and it is not a +2 and not a rule.**

The offset is **Frail**: a player debuff that reduces gained Block by 25%,
floored (`FRAIL_BLOCK_MULT = 0.75`, and the engine's own
`Math.Truncate`-shaped equivalent). It is on the wire in `player.status`, it is
**not** in the fight record `understudy/replay.py` reconstructs from, and so
the replay resolved every Block card at its printed value while the engine
resolved it at three-quarters. On Furina's Block cards — printed 3, 4 and 6 —
25% truncates to 1, 1 and 2, which is why the corpus looked like a clustered
`+2` with a `+1` skirt rather than like a multiplier.

**C1 is therefore a family-B reconstruction gap, not a family-C tier0
infidelity.** tier0 already models Frail exactly; what the replay never had was
the reading. With the recorded status strip loaded, **33 of 38 measured plays
agree exactly**, up from 7 of 38, and **every one of the 26 positive
divergences closes to zero**.

The two candidate layers the probe was sent to separate:

| layer | verdict |
|---|---|
| play-resolution (engine increments Block differently) | **NO.** Engine per-play Block equals `trunc(printed x spotlight x frail)` on every play measured, with no residual. |
| turn-open sampling / decay-expiry timing | **NO.** The divergence is present per PLAY, inside a turn, with block read either side of each action. |
| the wire (reading position) | **NO.** Both instruments read the same number; one of them was reconstructed from a record that omits a modifier. |
| reconstruction INPUT (the modifier is absent from the record) | **YES.** |

---

## Design

One fight, floor 1→2, Furina, chosen seed `TRACKB2`, driven by
`understudy/probe_block.py` — a fixed script with no policy in it:

1. play the granted **Ethereal Spotlight** first, so the designation is
   standing before any Companion card resolves;
2. answer its Center Stage / Guest Cast selector with the **declared arm**
   (`--spotlight center` / `--spotlight guest`), not with a policy;
3. play every card whose **wire text** prints "Block", in hand order — no
   scoring, no ladder. (Recognised from the game's own description string and
   never from a tier0 sheet: a probe that read tier0 to decide what to play
   would have tier0 on both sides of its own comparison.)
4. end the turn.

`player.block` is read at **every decision point**, so consecutive readings
bracket exactly one card — the same bracketing S7's L1 uses on `target_hp`,
applied to Block. The sim side is asked the identical question through tier0's
own entry point (`effects.resolve_card` on a fresh state) under the same
declared designation. No rule is retyped on either side.

Two arms were run on the same seed so the same Companion card could be read
under both Spotlight answers.

### "Relics stripped"

**The game offers no relic-less start, so the probe took the KNOWN-relic
allowance instead.** Relics were read off the wire on every reading. Exactly
two were held, all fight, both arms:

| relic | can it touch Block? |
|---|---|
| **Ethereal Spotlight** (Furina's starter) | No. It grants a card each turn. The granted card's *selector* changes Block through the Spotlight multiplier, and that is why the arm is a declared input rather than a confounder. |
| **Golden Pearl** | No. One effect, `{hook: gold_on_pickup, amount: 150}`; `gold_on_pickup` is in `tier0/engine/relics.py` `RUN_HOOKS`, so it never enters the combat engine's `relic_effects` at all. Zero combat behaviour. |

### Confounders present, and what happened to them

| confounder | status |
|---|---|
| **Frail on the player** | PRESENT from round 2, 2–4 stacks. **This is the finding**, not a nuisance: it was logged, then reconstructed, and the divergence closed. |
| enemy block | absent — `Corpse Slug blk=0` on every reading. |
| enemy powers | `Ravenous 4`, `Weak 1` on the enemy. Neither touches the player's Block. |
| player Strength / Dexterity | absent from the status strip on every reading. |
| a second enemy | absent — one enemy, all eight rounds. |
| `Aria of Recompense` | a scaling card the isolated per-card reconstruction cannot feed (its sim value is 0 against engine 0–4). It is the ONLY residual after Frail is loaded, it runs the OTHER way (sim under), and it is called out below rather than folded into the C1 answer. |

---

## The raw per-play table

Every reading, both arms. `engine` is `block_after − block_before` off the
wire; `sim_blind` is tier0 with the selector known and the status strip NOT
loaded (S7's position); `sim_status` is the same with the recorded Frail
loaded. Rounds 1–8; the script hands combat back to `policy_v1` after round 8
so the fight can end.

| arm | rnd | card | frail | engine | sim_blind | sim_status |
|---|---|---|---|---|---|---|
| center | 1 | Stage Presence | 0 | 6 | 6 | 6 |
| center | 1 | Stage Presence | 0 | 6 | 6 | 6 |
| center | 1 | Aria of Recompense | 0 | 1 | 0 | 0 |
| center | 2 | Regal Bearing | 2 | 2 | 3 | 2 |
| center | 3 | Stage Presence | 3 | 4 | 6 | 4 |
| center | 3 | Aria of Recompense | 3 | 3 | 0 | 0 |
| center | 4 | Regal Bearing | 2 | 2 | 3 | 2 |
| center | 4 | Charlotte — Enduring Frosthelm | 2 | 3 | 4 | 3 |
| center | 4 | Stage Presence | 2 | 4 | 6 | 4 |
| center | 5 | Stage Presence | 3 | 4 | 6 | 4 |
| center | 5 | Regal Bearing | 3 | 2 | 3 | 2 |
| center | 5 | Charlotte — Enduring Frosthelm | 3 | 3 | 4 | 3 |
| center | 6 | Stage Presence | 4 | 4 | 6 | 4 |
| center | 6 | Aria of Recompense | 4 | 4 | 0 | 0 |
| center | 7 | Aria of Recompense | 3 | 4 | 0 | 0 |
| center | 7 | Regal Bearing | 3 | 2 | 3 | 2 |
| center | 7 | Stage Presence | 3 | 4 | 6 | 4 |
| center | 8 | Stage Presence | 4 | 4 | 6 | 4 |
| center | 8 | Charlotte — Enduring Frosthelm | 4 | 3 | 4 | 3 |
| guest | 1 | Stage Presence | 0 | 6 | 6 | 6 |
| guest | 1 | Stage Presence | 0 | 6 | 6 | 6 |
| guest | 1 | Aria of Recompense | 0 | 0 | 0 | 0 |
| guest | 2 | Regal Bearing | 2 | 2 | 3 | 2 |
| guest | 3 | Stage Presence | 3 | 4 | 6 | 4 |
| guest | 3 | Aria of Recompense | 3 | 0 | 0 | 0 |
| guest | 4 | Regal Bearing | 2 | 2 | 3 | 2 |
| guest | 4 | **Charlotte — Enduring Frosthelm** | 2 | **4** | 6 | **4** |
| guest | 4 | Stage Presence | 2 | 4 | 6 | 4 |
| guest | 5 | Stage Presence | 3 | 4 | 6 | 4 |
| guest | 5 | Regal Bearing | 3 | 2 | 3 | 2 |
| guest | 5 | **Charlotte — Enduring Frosthelm** | 3 | **4** | 6 | **4** |
| guest | 6 | Stage Presence | 4 | 4 | 6 | 4 |
| guest | 6 | Aria of Recompense | 4 | 0 | 0 | 0 |
| guest | 7 | Aria of Recompense | 3 | 1 | 0 | 0 |
| guest | 7 | Regal Bearing | 3 | 2 | 3 | 2 |
| guest | 7 | Stage Presence | 3 | 4 | 6 | 4 |
| guest | 8 | Stage Presence | 4 | 4 | 6 | 4 |
| guest | 8 | **Charlotte — Enduring Frosthelm** | 4 | **4** | 6 | **4** |

### Distribution of `sim − engine`

| reconstruction | −4 | −3 | −1 | 0 | +1 | +2 | agree |
|---|---|---|---|---|---|---|---|
| selector known, status **BLIND** (S7's position) | 2 | 1 | 2 | **7** | 11 | 15 | **7 / 38** |
| selector known, status **LOADED** | 2 | 1 | 2 | **33** | 0 | 0 | **33 / 38** |

Every `+1` and every `+2` closes. The five that remain are all
`Aria of Recompense`, all negative, and all the same unrelated gap.

---

## Localization, stated as arithmetic

The engine's Block on a play is exactly

```
trunc( printed  x  spotlight_multiplier  x  frail_multiplier )
```

and every cell above is that number:

| card | printed | Guest Cast x1.5 | Frail x0.75 | engine read |
|---|---|---|---|---|
| Regal Bearing | 3 | — (not a Companion) | 2.25 | **2** |
| Stage Presence | 6 | — (not a Companion) | 4.5 | **4** |
| Stage Presence, round 1 (no Frail yet) | 6 | — | — | **6** |
| Charlotte — Enduring Frosthelm, Center Stage | 4 | — (Center Stage) | 3.0 | **3** |
| Charlotte — Enduring Frosthelm, Guest Cast | 4 | 6 | 4.5 | **4** |

Two parity facts fall out of the same table and are worth recording because
they were open questions a moment ago:

1. **The Spotlight Block multiplier is at parity.** Charlotte's printed 4
   reads 6 under Guest Cast on the engine side (`Block Next Turn 6` in the
   status strip confirms it independently), which is
   `SPOTLIGHT_BASE_MULT = 1.5` — the same number `effects._spotlight_scale`
   applies. Under Center Stage it reads its printed 4. Both languages agree in
   both arms.
2. **Frail is at parity too** — 0.75, truncated, on both sides. The gap was
   never in the law; it was in whether the replay knew the law applied.

### Why the corpus looked like a constant `+2`

S7's `l2.block_at_turn_end` compares TURN TOTALS. A Furina turn under Frail
loses `trunc(0.25 x printed)` per card, which on her Block cards is 1 or 2, and
the commonest single-Block-card turns lose exactly 2 (Stage Presence 6→4,
Lynette 7→5). S7's four commonest pairs — 7/5, 13/11, 6/4, 10/8 — are all
consistent with that and none of them requires a flat term. **A per-card
multiplicative loss read as a per-turn constant offset because the audit
could only see per-turn sums.**

---

## What is NOT explained, and is not C1

`Aria of Recompense` reads 0 in the isolated sim against engine readings of 0,
1, 3 and 4 — a card whose Block scales with state the per-card reconstruction
does not carry. It is the mirror image of C1 (sim UNDER, not over), it is
present in both arms, and it is **not adjudicated here**: the probe was sent
for the +2 and the +2 is answered.

---

## Exact repro

```
# from the branch, with klee-mod/local.props pointing at the game dir
python -m understudy.probe_block --spotlight center --seed TRACKB2 --max-fights 1 --turns 8
python -m understudy.probe_block --spotlight guest  --seed TRACKB2 --max-fights 1 --turns 8
python -m tools.probe_b2_table "understudy/logs/soak/probe-b2-*.jsonl"
```

Readings land in `understudy/logs/soak/probe-b2-<arm>-<stamp>.jsonl`
(gitignored — per-machine run output). Stamps of record:
`20260805-125753` (center), `20260805-125933` (guest), `20260805-132001`
(center, re-run with `player.resources` recorded for probe B3). All three:
seed `TRACKB2` honoured, **0 defects**, `outcome: bounded`.

**One harness fact learned the expensive way and recorded rather than
smoothed over.** The first attempt had no turn bound. A Block-only script
never kills anything and Furina never dies behind the Block it is measuring:
the run reached **round 140 of one floor-2 fight** and was still going. Hence
`--turns` (default 8), after which combat is handed back to `policy_v1` so the
fight can end — and hence the readings are flushed to disk as they are taken
rather than at the end of a run that may not have one. Both are pinned by
tests in `tier0/tests/test_understudy_replay_selectors.py`.

## What this probe does NOT license

No balance change, no constant edit, no re-grading of anything. It says one
thing: **C1 is a reconstruction gap in `understudy/replay.py`'s input, not a
tier0 infidelity**, and the S7 `l2.block_at_turn_end` column should be read
that way. Whether the replay should carry the status strip — and whether the
fight record should record it — is a call for the ruling session, not for this
probe. `hp_trajectory` carries `[round, hp, block]` and no status; adding a
column is a telemetry change with a cross-session note attached, and it was
not made here.
