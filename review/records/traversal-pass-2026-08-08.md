Status: RECORD

# Understudy traversal pass — 2026-08-08

> **NO MEASUREMENT WAS PUBLISHED FROM THIS PASS.** It is a defect pass, not a
> stats pass: no Cell, no stamp, no registration. The two live runs below are
> reproduction and verification of one filed defect, and their fight curves,
> HP ledgers and damage tables are **not quotable** — Guardrail-7 applies to
> them as it applies to every bot number, and nothing here was designed to be
> compared to anything.

Branch `traversal-2026-08-08`, worktree `../GItS-traversal`, off `main`
@ `986da95`.

**Build.** `git diff --stat 6d352d7..986da95 -- klee-mod` is empty, so the
deployed package `0.2-612` (built from `6d352d7`) is current for `986da95` and
**no rebuild was done**. The soak deploys only the vendored MCP bridge
(pin `55e0648`), which is a file copy and reverted at teardown.

The four rows this pass was opened for: `EB-11`, `EB-12`, `EB-13`, `EB-15`.

---

## EB-11 — understudy defect 13, `no_action` on a state with no `state_type`

**FIXED.** Row leaves HEAD.

**The gap.** `RunDriver._settle_transient` (`understudy/soak.py`) rides out
`state_type: "unknown"` — the bridge's own name for "unrecognized room or null
state", which is what the instant after embarking is. It tested
`str(state.get("state_type")) != "unknown"`. A state with **no `state_type` key
at all** renders through `str()` as the string `"None"`, which is not
`"unknown"` and is not any screen name either, so the missing key fell straight
past the settle, past every `_mechanical_action` arm, into `policy_v1.decide`
declining (`'None' is a mechanical screen with no sim decision behind it`) and
`_last_resort` returning `None` — and the run ended as `Defect("no_action")`.
The defect kind named the policy for a state that was never a screen.

**The fix.** Both faces are the same MOMENT and now get the same answer: the
settle rides out `unknown` **or** an absent `state_type`, and emits a
`transient_settled` record when it lands. The asymmetry on failure is
deliberate and stated in the docstring:

- a stuck `unknown` is still **handed back** to the no-progress watchdog, which
  can post against it and therefore builds a fingerprint history — a better
  record than an instant refusal, which is the whole reason the settle exists;
- a `state_type` that never arrives is **filed here**, under the new kind
  `state_type_missing`, because nothing downstream can post an action against a
  state with no screen, so the watchdog would never see a second sample. It is
  classified, logged, and skipped loudly — not disguised as `no_action`.

`state_type_missing` joins `_HARNESS_SIDE`, so two of them halt a soak. Same
seat as `bridge_unreachable`: not the harness's fault, but a soak that keeps
arriving somewhere it cannot name is producing nothing.

**Reproduce-or-argue: ARGUED, not reproduced.** The state is a sub-second
transition on the bridge's side and there is no verb that makes it appear; it
did not occur in either live run tonight (`grep` over both run logs: zero
records with a null `state_type`, zero `transient_settled`). The handler is
therefore unit-tested against the **recorded state shape** from the original
filing — run/player present, screen name absent — in five tests in
`tier0/tests/test_understudy_soak.py`, covering: the transition is ridden out;
`unknown` still is; a never-arriving `state_type` files its own kind; a stuck
`unknown` is still handed to the watchdog; and the halt classification.

---

## EB-13 — understudy defect 15, the map↔rest_site "bounce" (seed `43MLG7MG9L`)

**REPRODUCED, DIAGNOSED, FIXED.** Row leaves HEAD.

### Reproduction

`python -m understudy.soak --runs 1 --seed 43MLG7MG9L --commit salon`
(soak `20260808-145030`) filed, at 86 actions:

```
no_progress  1/7  rest_site
2 distinct state fingerprint(s) across 12 posted actions (cycle):
map|None|1|6|None|57|None|0|-|0  <->  rest_site|None|1|7|None|57|None|0|-|0
```

Byte-for-byte the shape of the original filing, at the same act/floor, on the
same seed, in a different build. (HP reads 57 rather than 59; the bot's earlier
play differed, the dead end did not.)

### Diagnosis — and the first thing to correct is the row's own words

The row calls this a rest site "entered at full HP, **left**, and re-entered
without the floor advancing". **It never left.** The `map|floor 6` fingerprint
is the single preceding action still inside the twelve-action window; every one
of actions 77–86 is `rest_site|floor 7`. `NO_PROGRESS_CYCLE = 2` counts
*distinct* fingerprints, so a frozen screen whose window straddles the
transition into it reports as two — and reads as a bounce. It is a **frozen
screen**, not a cycle. Nothing was bouncing.

The cause is **understudy-side and mechanical**, and the run log states it
outright. At floor 7 the wire carried:

```json
"rest_site": {"can_proceed": false, "options": [
  {"index": 0, "id": "HEAL",  "name": "Rest",  "is_enabled": true},
  {"index": 1, "id": "SMITH", "name": "Smith", "is_enabled": true}]}
```

and `policy_v1._rest` decided:

```json
"sim_choice": "remove", "sim_target": "soloists_solicitation",
"option_matched": false, "action": {"action": "proceed"},
"status": "error", "message": "No proceed button available or enabled"
```

The chain, in four steps:

1. `tier05.model.rest_action` returned **`remove`** — a card removal — for a
   6-card salon deck at 57/66 HP with no elite ahead.
2. An act-1 rest site sells `HEAL` and `SMITH`. It does not sell removal, so
   `policy_v0._match_rest_option` matched nothing and returned `None`.
3. `_rest`'s no-match fallback was an unconditional `{"action": "proceed"}`.
4. The screen reports `can_proceed: false` and the bridge refuses the verb in
   as many words. **A refused verb is not a fallback; it is a loop with a
   rationale attached.** The bot spent every remaining action of the run
   posting it until the watchdog stopped the run.

`soak._last_resort` mapped `rest_site` to the same `proceed`, so the escape
hatch was the identical dead end. This is the third instance of a shape the
module has already learned twice — defect 4 (removal grid), defect 6 (Enchant),
defect 12 (bundle preview), and the `card_select` comment that says it best:
**a screen that cannot be cancelled must be answered.**

### Fix

Two edits, on the two halves, and `policy_v0.py` is untouched — it is FROZEN,
one arm of a published measurement.

- **`policy_v1._rest` declines** instead of emitting a refused verb, carrying
  its diagnosis keys (`sim_choice`, `sim_target`, `next_fight`,
  `next_node_kinds`) through the decline, because those keys are what made this
  defect readable at all. Declining routes the screen to `_last_resort`, which
  **counts every use as a `forced_default`** — the old shape spent the same
  action while reporting itself as a decision, so the telemetry claimed the
  sim had chosen when it had not.
- **`soak._last_resort` answers the rest site**: first **enabled** option in
  offered order, falling back to `proceed` only when nothing is left to spend.
  Deterministic and declared — the same always-heads coin `_mechanical_action`
  already spends on events, not a new policy.

A latent twin was closed on the way past: `_match_rest_option` matches on
`id`/`name` and never reads `is_enabled`, because that wire key did not exist
when it was written. It cannot be changed (frozen), so `policy_v1` screens the
match instead — a greyed-out option is not an option. Untriggered on this seed;
it would have produced the same freeze against a spent option.

Five regression tests in `tier0/tests/test_understudy_soak.py` are built from
the verbatim recorded state.

### Verification — live, same seed, same arm

Re-run after the fix (soak `20260808-145537`). The rest site at act 1 floor 7
is now answered, and **both** branches of the new `_last_resort` fired in the
same visit:

```json
{"record":"forced_default","state_type":"rest_site",
 "why":"tier05.model.rest_action chose 'remove' (soloists_solicitation), which
        this rest site does not offer as an enabled option (offered: ['HEAL','SMITH'])",
 "action":{"action":"choose_rest_option","index":0}}
{"record":"forced_default","state_type":"rest_site",
 "why":"... (offered: [])",
 "action":{"action":"proceed"}}
```

First the enabled option, then — the option spent and the list empty — the exit
the screen has by then enabled. The run walked past floor 7 and on to **floor
12**, where it died in a fight: **184 actions against 86**, and the report reads

> **None.** No crash, no soft-lock, no unhandled overlay, no stalled state
> across every run in this soak.

with the answer visible where it belongs: *"3 forced defaults — every one is a
decision nobody made: `rest_site` x2, `rewards` x1."* Before the fix the same
two actions were reported as decisions the sim had made. It had not.

---

## EB-12 — `bridge_unreachable` by timeout with the process alive

**NO NEW EVIDENCE. Row unchanged.** Not chased, per the pass's terms.

Both of tonight's runs were swept at the end of the pass: `bridge_unreachable`
appears **0** times across every log this session wrote, and neither run lost
the wire at any point. The single observation stands alone; the row stays filed
with one, and says so now.

---

## EB-15 — the `lobby` seed route

**DIAGNOSED. Row rewritten, not closed** — the route did **not** fire, and this
pass can now say why it never will on this arm.

The attempt was made deliberately and once, at the only moment that can work:
character chosen, embark not yet fired. To make it diagnostic rather than
another tally mark, the driver now reads `GET /api/v1/gits/seed` **before** the
POST as well as taking the POST's own report, and logs both halves of the
endpoint's guard onto the `seed_chosen` record (adding keys to a log record is
free; these are read, never driven on).

Observation four, from soak `20260808-145030`:

```json
{"record": "seed_chosen", "requested": "43MLG7MG9L", "seed": "43MLG7MG9L",
 "route": "debug_override", "on_char_select": true,
 "lobby_seed": "43MLG7MG9L", "debug_override": "43MLG7MG9L",
 "before_on_char_select": true, "before_lobby_seed": null}
```

Read against `GitsSeedApply` (`vendor/STS2_MCP/gits/GitsSeed.cs`) this is
already conclusive, and it rules out the standing hypothesis. `on_char_select`
is **true** on both reads, so the screen was found and visible; and
`lobby_seed` reads back the seed **afterwards**, which is only reachable if
`charSelect.Lobby` was non-null, `SetSeed` assigned `Seed`, and then **threw**,
sending control to the catch and on to the debug override. The lobby is not
null. It never was.

`godot.log` names the throw:

```
[STS2 MCP][GItS] seed: lobby route failed
    (Seed should not be changed in standard mode!); falling back to the debug override
```

**`StartRunLobby.SetSeed` refuses on the GameMode, not on `NetService.Type`**,
and `NCharacterSelectScreen.InitializeSingleplayer` builds its lobby with
`GameMode.Standard`. So the lobby route is **unreachable by construction** on
every standard singleplayer run — which is all four observations, and every
future one. `debug_override` is not the fallback on this arm; it is the route.

Three consequences, all recorded:

- The file's own header comment was **wrong about which guard fires**. It cites
  the `NetService.Type` check and concludes "the upstream guard is defensive,
  not descriptive" — upstream refuses for a real reason, just not the reason
  upstream states. The comment is corrected in place (comment-only; the
  deployed dll is unaffected and no rebuild is owed).
- The stranded `Lobby.Seed` left behind by the half-completed `SetSeed` is
  harmless: `DebugSeedOverride` outranks it at `BeginRunForAllPlayersIfAllReady`,
  and `Clear` empties both channels. Teardown does call it.
- The arm is **kept**. It is the route a Custom-run or a hosted lobby would
  take and it reports itself accurately either way. Nobody should read "two
  routes work" out of it — which is what the row said, and the row was right.

**For [USER], if it is ever worth a ruling:** deleting the lobby arm would be a
taste call, not a defect fix, so nothing was deleted. The honest position is
that the endpoint has one working route on the arm the soak flies and a second
that is correct code for a screen the soak never uses.

---

## Live runs

Two, both on seed `43MLG7MG9L` with `--commit salon`, the arm the original
filing came from. Not a measurement; a before and an after.

| soak | code | outcome | act/floor | actions | wall s |
|---|---|---|---|---|---|
| `20260808-145030` | before the fix | **`no_progress` at the rest site** | 1/7 | 86 | 67.1 |
| `20260808-145537` | after the fix | `died` — **no defects**, 3 forced defaults | 1/12 | 184 | 141.8 |

Both runs took `route: "debug_override"` with `on_char_select: true`, so EB-15's
tally is now four observations and one diagnosis, not five tally marks.

Logs are `understudy/logs/soak/soak-*-run001.jsonl` — gitignored per-machine
output, quoted here because that is the only way they leave the machine.

## Teardown

Reversibility ledger walked clean on both runs (`steam_appid.txt` removed —
it did not pre-exist; bridge undeployed; process terminated; speed restored;
**both seed channels cleared**, which matters because `DebugSeedOverride` is
global and sticky). No `steam_appid.txt` remains at the game root.
