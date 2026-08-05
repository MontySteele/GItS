# Architecture Atlas

> Written by surplus-dispatch-2 stream S11 (2026-08-05), one agent per module, every
> invariant and trap carrying a file:line or DECISIONS.md cite. Purpose: stop every
> future session from re-deriving this context from scratch. These are maps, not
> reviews — no design opinions, no proposals. If a doc contradicts the code, the
> code and DECISIONS.md win; fix the atlas doc on next touch.

| doc | scope | rulings cited |
|---|---|---|
| [`tier0-engine.md`](tier0-engine.md) | The combat kernel: op interpreter, powers, statuses, reactions, resources — comparability-first, emit-only toward the run layer. | R14, R16, R20, R33, R34, R36, R37, R39, R52, R67, R72, R82, R85, R92-3b |
| [`tier0-harness-tests.md`](tier0-harness-tests.md) | The seven-axis scorecard, metrics/report/runner CLI, and what the test suite actually gates. | R18, D3, D4, D5, R67, R70, R81, R93, R97 |
| [`tier0-pilot-roster.md`](tier0-pilot-roster.md) | The content-and-decision layer feeding combat: pilot policy, roster, constants, content YAMLs. | R8, R20, R24, R33, R36, R37, R66, R67, R68, R80, R83, R92-3b, R93 |
| [`tier05-sim-core.md`](tier05-sim-core.md) | The run-level sim and drafter: model, acts, runner, draft, route/maps/cells. | R2.1, R2.2, R61, R64, R66, R68, R83, R84, R87 |
| [`tier05-economy.md`](tier05-economy.md) | Events, rewards, shop, potions, relics and the content pools — run-half only, skip-loudly. | R59, R60, R61, R63, R64, R65, R87, D4 |
| [`tier05-metrics.md`](tier05-metrics.md) | The measurement layer: run_metrics, stats, sweeps, ab, telemetry modules, exp_* convention. | R14, R33, R51, R66, R67, R68, R85, R87, D3, D4, D5 |
| [`klee-mod-cards.md`](klee-mod-cards.md) | The C# card layer and its codegen contract with the design sheets; manifests and the lints that gate them. | R20, R23, R24, R34, R36, R37, R52, R69, R85, R86, R87, R92-3b |
| [`klee-mod-runtime.md`](klee-mod-runtime.md) | Powers, Elements, Vfx, Patches, Relics, Diagnostics — the in-game runtime layer. | R13, R52, R59, R60, R61, R69, R71, R72, R80, R85, R86 |
| [`klee-mod-build-pck.md`](klee-mod-build-pck.md) | The build/ship pipeline: deploy, versioning, validate gates, bitecheck, the pck overlay. | R70, R13, D4, R66 |
| [`tools.md`](tools.md) | Codegen, art pipeline, lints, canon extractors — and which CI gates run them. | R67, R68, R69, R70, R81, R85, R90, R91, R92, D4 |
| [`understudy.md`](understudy.md) | The bot playtest apparatus driving the real game; Guardrail-7 and the no-fun rule. | R93, R94, R95, R96, R97, R87, R70, R68, D4 |
| [`vendor-sts2-mcp.md`](vendor-sts2-mcp.md) | The vendored wire contract the understudy bridge speaks. | R70, R94, R95, R97 |

