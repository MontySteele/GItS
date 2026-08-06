> **MOVED 2026-08-06 — Clear the Stage, Track R-B resumption (R121 `Q20`, MOVE-WITH-RESOLVER; charter R119, rail 1).**
> Old path: `docs/probe-e-corpse-detonation.md` — new path: `docs/archive/probe-e-corpse-detonation.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Live citers repointed in the move commit; ledger and other
> frozen citations keep the old path on purpose (rail 1: ledger bytes are
> never rewritten) and resolve through the moved-path resolver table,
> `docs/registry/identifiers.md` §17. Per-file map:
> `review/stage-clear/rb-move-manifest.tsv`.

# Probe (e) — corpse detonation: MEASURED, no detonation on the killing blow, sim and game agree

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

> **Run 2026-08-06, Track M (wave 8), under the COUNTERSIGNED registration
> `docs/probe-e-corpse-detonation-registration-draft.md` (Q11 / R118, [USER]
> verbatim *"Countersign."*).** Two tells, negative-control arm, nine
> confounders, cost ceiling, stop-and-re-register tripwire — all per the
> registration. **This probe grades nothing, prices nothing, and moves no
> number.** Guardrail 7 unchanged; every engine number below comes from a
> fixed script (bot-limited).

## The pre-registered question, verbatim, and the answer

> "Does a killing blow on a bombed enemy early-detonate that enemy's bombs?"

**NO — in both instruments.** The game shows no detonation on the killing
blow (no Spark, no damage anywhere but the blow itself), and tier0 — read
off the sim by executing it, not off the ledger prose — also does not
detonate on a blow that kills (`effects._detonate_bombs_on_hit` returns on
`not enemy.alive`; measured: bombs remain on the corpse, `detonations_total`
0, sparks 0). **Sim and game agree in outcome.**

Layer table (registration §"candidate layers"), one row left standing **in
outcome**:

| # | layer | outcome |
|---|---|---|
| 1 | engine suppresses the broadcast on death | **LEFT STANDING (outcome).** No detonation observed on the killing blow; sim and game agree; the missing `IsDead` guard is harmless **for this hook**. Caveat, stated so it cannot be inferred away: the registered tells cannot separate mechanism 1 from mechanism 3 (both produce no spark and no damage); the C#-side broadcast read is the registration's declared ceiling and was not taken. Both candidate mechanisms yield the same observable behaviour and the same parity verdict. |
| 2 | broadcasts and bombs resolve early | **DEAD.** The relic tell is live on this wire (fired twice in the control readings below) and stayed silent on the killing blow. |
| 3 | broadcasts but bombs cleaned up with the corpse | Not separable from layer 1 by these tells — see the layer-1 caveat. Its *stakes* clause ("the sim's unconditional detonation is then the divergence") is factually inapplicable: the sim's detonation is **not** unconditional (measured, below). Under either mechanism there is no divergence. |
| 4 | state unreachable as scripted | **DEAD.** The state was reached and read cleanly. |

**Second finding, reported as one (registration §"one adjacent fact"):** the
`klee-mod/DECISIONS.md` entry's STAKES paragraph — *"the sim detonates
unconditionally"* — states the sim's behaviour **backwards**, exactly as
S14's `NC-18` claimed. Measured off the sim (method step 4,
`tools/probe_e_sim.py`): tier0's on-hit detonation carries an alive-guard
and does **not** fire on the killing blow. Consequently the entry's
decision-tree branch *"No Spark → real divergence, opens a sim-side
correction"* was built on the inverted premise: no Spark is **agreement**.
Whether that entry's prose gets corrected is [USER]'s to rule (`NC-18`,
`docs/sitting-prep-2026-08-05.md` §4b) — nothing there is amended by this
probe.

## Apparatus and corpus

- Driver: `understudy/probe_corpse.py` (new, in the shape of
  `understudy/probe_block.py` — a fixed script with no policy in it, per the
  registration's method). Klee (`KLEEMOD-KLEE`), first fight of a fresh run,
  chosen seed `PROBEE` (echoed by the wire as `PR0BEE`), P1.5 bridge,
  deployed mod `0.2-296`. Encounter drawn: two Toadpoles (25 HP, 22 HP);
  target = the 22 HP one, pinned by id `TOADPOLE_1`.
- Sim side: `tools/probe_e_sim.py` — the identical sequence through
  `tier0/engine/effects.py`, read-only.
- Readings (gitignored per-machine run output; stamps recorded per the B2
  lesson, globs must be narrowed to them):
  - kill arm: `probe-e-kill-20260806-023623.jsonl` (18.0 s wall)
  - control arm: `probe-e-control-20260806-023252.jsonl` (20.3 s wall)
  - first kill attempt (schedule observation, below):
    `probe-e-kill-20260806-023430.jsonl`

## The readings

**Kill arm** (round 3; bomb application and killing blow are distinct
scripted actions with a reading between them):

| reading | target | player | Spark | bystander |
|---|---|---|---|---|
| before bomb | hp 1, no bombs | hp 46 | 0 | hp 25 |
| before blow | hp 1, **Bomb 5** | hp 46 | 0 | hp 25 |
| after blow (same turn) | **dead** | hp 44 (−2 = target's Thorns 2, the only damage) | **0** | hp 25 (untouched) |

No Spark; no bomb damage appeared anywhere. The 12-damage signature a
detonation stamps on the wire (see control) is absent.

**Control arm** (registration method step 3 — same seed, blow sized
non-lethal): target at 22 HP takes Bomb 5, then one Kaboom! (7): hp 22 → 10
(**12 = 7 + 5**, the stated arithmetic of confounder 4), **Spark 0 → 1**,
bomb consumed. Both tells fire on a detonation the instant one exists, on
this exact wire, this exact seed. "The bombs did not resolve early" is
therefore distinguishable from "the bombs were never applied".

**Unplanned schedule observation** (first kill-arm attempt, stamp
`023430`): a Bomb 5 left overnight on the 1-HP target detonated on the
normal start-of-player-turn sweep — Spark 0 → 1, target dead — before any
blow existed to measure. Recorded as a second live confirmation of the
relic tell and of the normal schedule; the scripted driver then gained the
same-turn bomb-then-blow gate and the arm was re-taken cleanly.

**Sim side** (`python -m tools.probe_e_sim`, verbatim output):

```
{'arm': 'kill',    'target_hp_start': 6,  'relic_hooks': ['spark_on_detonation'],
 'after_bomb': {'target_bombs': 1, 'detonations': 0, 'sparks': 0},
 'after_blow': {'target_hp': -1, 'target_alive': False, 'target_bombs': 1,
                'detonations': 0, 'sparks': 0, 'bystander_hp': 50, 'player_hp': 62}}
{'arm': 'control', 'target_hp_start': 20, 'relic_hooks': ['spark_on_detonation'],
 'after_bomb': {'target_bombs': 1, 'detonations': 0, 'sparks': 0},
 'after_blow': {'target_hp': 8, 'target_alive': True, 'target_bombs': 0,
                'detonations': 1, 'sparks': 1, 'bystander_hp': 50, 'player_hp': 62}}
```

Sim-vs-engine on one script: kill — no detonation in either; control —
one detonation in both, same 12-damage arithmetic (engine 22→10, sim
20→8), same single spark.

## Confounders, dispositions (registration order)

1. **Relic dependence of tell 1** — Pounding Surprise is Klee's starter and
   was held on every reading (`relics` recorded per row). Two-tell result,
   as registered.
2. **AoE/splash attribution** — the blow was single-target (Kaboom!); the
   only non-target damage across the blow was the player's −2 from the
   target's own Thorns 2, attributed and stated. Jumpy Dumpty (random
   targets) was never played.
3. **Death vs turn boundary** — the after-blow reading is same-turn (energy
   3 → 2 within round 3); the ordering claim is clean.
4. **Which bomb** — exactly one Pop! bomb, printed 5 damage; expected
   detonation signature 7 + 5 = 12, observed in the control, absent in the
   kill.
5. **Bot-limited (Guardrail 7)** — fixed script; nothing here is a balance
   finding.
6. **One character, one encounter, one seed** — no breadth claim.
7. **`NC-18` prose** — not used as the sim-side reading; the sim was
   executed (`tools/probe_e_sim.py`). The prose contradiction is the second
   finding above.
8. **Wire freeze** — same session family as probe (d)'s re-take, which
   reproduced B2's corpus byte-identical the same hour; deployed mod
   `0.2-296` recorded. No wire movement observed.

*(Count note: the countersign banner says "nine confounders"; the
registration's own declared list numbers eight, and eight are dispositioned
above. The banner's count is off by one; the list is the authority.)*

## What this licenses, per the registration — and what it does not

- **`S4-G15` CLOSES as "sim and game agree"** — the registration's own
  closure condition for the no-detonation outcome, met and recorded as
  paper: the killing blow does not early-detonate bombs in either engine,
  and `BombPower.AfterDamageReceived`'s missing `IsDead` guard is harmless
  **for this hook**, with this measurement as the citation the original
  panel never had. The ~10-second table settlement is superseded by an
  answered question (it was fallback-only pending an answer; the answer
  exists).
- NOT licensed, and not claimed: harmlessness of the missing guard on any
  other hook or power; any bomb balance statement; adding the guard (a code
  change nobody asked for); amending the `klee-mod/DECISIONS.md` prose
  (NC-18, [USER]'s); treating a one-encounter reading as a roster property.
