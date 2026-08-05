# understudy/ — the bot playtest apparatus

Opened 2026-08-04 by the Understudy sprint. Brief:
`docs/understudy-kickoff-brief.md`. P0 findings and the three ratified
rulings: `docs/understudy-p0-findings.md`. Phase-0 measurement:
`docs/understudy-phase0-report.md`.

This directory drives the **real game** through the vendored STS2MCP bridge
(`vendor/STS2_MCP/`). It is not a simulator and it must never become one.

| file | what it is |
|---|---|
| `bridge.py` | stdlib HTTP client for `localhost:15526`; the wire contract is `vendor/STS2_MCP/docs/raw-simplified.md` |
| `adapter.py` | wire JSON -> tier0 engine objects, with its fidelity losses enumerated in the module docstring |
| `policy_v0.py` | the counterfactual arm: delegates every decision to the live tier0/tier05 entry points, and returns *nothing* where it cannot delegate faithfully |
| `rng.py` | the dedicated policy stream, and the refusal that keeps a game seed out of it |
| `harness.py` | `begin` / `state` / `act` — the Phase-0 measurement loop |
| `logs/` | per-run decision JSONL; `phase0-<seed>.jsonl` |

## The two rules this directory exists under

**Guardrail-7.** Every number a bot or an LLM produces here is a
**bot-limited floor**, in exactly the sense pilot-limited already means in
tier 0.5. No winrate, no HP curve and no damage figure from this directory is
a balance conclusion, and none of them are quotable as one. The apparatus
files defects and telemetry; it authors no design.

**No fun, ever.** A JSON-state agent cannot see the screen. Legibility,
readability, feel and fun remain [USER]-only instruments and nothing in this
directory may be read as evidence about them.

## Running the Phase-0 loop

Prerequisites: the bridge installed (`klee-mod\build\deploy_bridge.ps1`),
`steam_appid.txt` in the game root, Steam running, the game launched
directly from its exe.

```
python -m understudy.harness begin           # stamp the seed and speed
python -m understudy.harness state           # read the screen + policy_v0
python -m understudy.harness act '{"action":"end_turn"}' --why "..."
```

`act` recomputes the counterfactual at the current state *before* posting, so
a log line can never pair a choice with a policy answer from a screen that has
since moved.

## What policy_v0 will not answer

Three decision classes return no counterfactual and are excluded from the M2
denominator: events, boss-relic picks, and the Crystal Sphere minigame. The
reasons are in `policy_v0.NO_COUNTERFACTUAL`, and they are all the same
reason — the sim scores those by ids the wire does not carry, so any answer
would be a guess contributing noise to a number about judgment.
