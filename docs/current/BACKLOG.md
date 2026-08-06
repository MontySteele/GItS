# BACKLOG

> **Only OPEN executable engineering work** — confirmed defects, mechanical /
> parity fixes, measurement instruments, refactors, and test-writing that need
> **no [USER] design call to start**. One of six governing files, no overlap:
> [USER] design / taste / behavior / money calls live in **QUEUE.md**, settled
> rules in **LAW.md**, shipped facts in **STATE.md**, commands in
> **OPERATIONS.md**. Identifiers are preserved from their source registers;
> closed items are in git history (tag `pre-simplification-2026-08-06`).

---

## tier0 — engine, pilot, constants

| ID | Item | Provenance |
|---|---|---|
| `EB-5` | The combat pilot's scoring weights are unstamped inline literals (`tier0/pilot/policy.py:426-504`) — move to constants + version-stamp, no behavior change | eng-backlog §1 |
| `EB-17` | Klee played-when-drawn / dead-in-hand / force-first-copy telemetry — zero matches across `tier0/`,`tier05/`,`tools/`; a **live gate** (bodyless draw/resource engines may not be buffed without it) | eng-backlog §3; missed-requirements §2.2 |
| `X8-cap` | Ratified `bomb_damage_up ≤ 4` cap (`docs/current/characters/klee-character-design.md` §9) is **not implemented** — `max_stacks` only ever arrives from a card row and no Klee row carries one, so every Klee scaling power is uncapped | dockets/klee-rework §3 |
| `S13→S7` | Sim-infidelity cross-checks owed before any design session reads them as game facts: swirl aura self-refresh (`reactions.py:96-99`), detonation-order Vulnerable self-amp (`effects.py:474-476`), conscript nation hard-default `'inazuma'` (`effects.py:2018`), Kurage direct `p.block +=` bypass (`effects.py:2549`), per-effect-dict relic no-dedupe (`relics.py:133-136`) | exploit-ledger "Routed to S7" |

## tier0.5 — draft / run layer / measurement

| ID | Item | Provenance |
|---|---|---|
| `EB-10` | `tier05/route.py:13` docstring advertises `route_regret` as existing — stop advertising an unbuilt instrument | eng-backlog §1 |
| `EB-16` | `route_regret` — advertised in code, never written; `run_metrics.py` defines no such function. §3.7.5's "relics underpriced" finding rests on this comparison | eng-backlog §3; missed-requirements §2.1 |
| `EB-20` | Instrumentation for D8 (Encore economy census: 19/78 grant, 1 spends, absorption automatic) — measurement open though the lever is ruled-direction, unpicked | eng-backlog §3 |
| `EB-25` | Lagavulin Matriarch's Soul Siphon player-stat-drain half — no stat-drain op anywhere in `tier05/` or `tier0/engine/`; silently biases the Act-1 boss split. "single highest-leverage backlog item for boss identity" | eng-backlog §4; missed-requirements §3.1; run-model §10.9 |
| `EB-27` | Two tier0.5 spec features never built: `choose3` standalone slot mode (`model.py:246-250` raises `ValueError`) and the Prune signature event (`events.py` offers none) | eng-backlog §4; missed-requirements §3.5 |
| `EB-28` | The drafter's salon-deploy blindness — `tier05/draft.py:_static_power` has no `salon_member` term, so cross-plan the members are invisible | eng-backlog §4; missed-requirements §3.6 |
| `EB-29` | Out-of-scale boss audit (`test_subject`, `knowledge_demon`, `kaiser_crab`) — `test_subject`'s sheet inflates HP to stand in for a skipped mechanic (`act3_pool.yaml:217-222`), the fake-it-quietly pattern the house rules forbid | eng-backlog §4; missed-requirements §3.9; tier05-perf §1.5.2(1) |
| `EB-30` | The Ancient card's 3 Charge/turn is unmeasurable — lives in a layer the run sim does not model; the least-defended value in Kokomi's build | eng-backlog §4; open-playtest-items §6.3 |
| `EB-31` | Orobas not modelled in the sim — Klee's variant now is; still unmodelled: Furina's R2 upgraded form and Kokomi's variant | eng-backlog §4; open-playtest-items §6.3 |
| `EB-43` | **D15 (spotlight-limb payoff-presence) — STAGED, HELD.** Drafter behaviour change (`DRAFTER 15`) + re-baseline sweep; `Q18` countersigned, pinned DRAFTER 14. **Lands as step (5) of a fixed six-step order** — must not land before blind-first grading (4) or it invalidates the registration | eng-backlog §6; R121 |
| `EB-46` | Diagnose why tag-visible scoring moved the `ref_ironclad` anchor: separate the tag effect from the v6 (C5→C6) effect on this arm. No deadline, no design authority | eng-backlog §6; Q19; `review/r121-shield/` (at tag `pre-simplification-2026-08-06`) |
| `O-1` | `run_battery` merges the gauntlet's two stages into one `FightStats` while rates divide by records, so every published per-fight reaction rate overstates (7.70 → 6.60, +16.7%); blocks the X12 co-op potency reading | watch-items W3; R112 |
| `perf-1.5.2(3)` | Re-instrument on `real_ironclad`, not `ref_ironclad`, before reading any "can an average player clear this" claim — needs `game_ref/` rebuilt | tier05-perf §1.5.2(3) |
| `SKIP-10.9` | Living skip-backlog of un-modelled enemy mechanics to promote when a pass needs them: Back Attack (Kaiser Crab), untargetable Burrow (Tunneler), Ethereal/Hex auras (Knight Gang), Intangible (Test Subject P3), damage caps (Hard to Kill / Plating / Hardened Shell), and the two Ancient relic hooks — Blessed Antler and Philosopher's Stone | run-model-rework-plan §10.9 |

## klee-mod — C# implementation & parity

| ID | Item | Provenance |
|---|---|---|
| `EB-1` | **Punch Off crash** (reclassified GAME-SIDE/SPINE-SIDE) — the animation stream keeps the watch; not done while seed `8B97LMCL2F` crashes in Punch Off | eng-backlog §1 |
| `EB-2` | Salon upkeep vs All the World's a Stage income race — two powers in the same `AfterPlayerTurnStart` broadcast with no guaranteed order (`SalonPowers.cs:352` vs `FurinaResources.cs:1122`); nondeterministic tick rate | eng-backlog §1; `NC-9` seam |
| `EB-18` | The mod's per-fight telemetry (C2) was never built — JSON-lines per fight; `tier1/analyze.py` reads per-**run** granularity. Answers the corpse-detonation count for free | eng-backlog §3; missed-requirements §2.3 |
| `EB-19` | The sim-pipeline-step → C#-hook sweep is still owed — Superconduct, Shatter, aura-tick ordering all reduce to PRE/POST hook misplacement; no pass has systematically mapped each sim step to its C# hook | eng-backlog §3; missed-requirements §2.4 |
| `BFF-copy` | `best_friends_forever` replays companions un-upgraded and dedupes differently than the sim — `combat.py:269` records instance ids (`foo+` distinct from `foo`, both can copy; upgrade travels), while C# `CompanionPlays` records base ids and `ModelDb.GetById` rebuilds pristine. Same root R114/FLAG-2(i) settled for the other copy ops; the dedupe half may need a ruling | parity-sys-cluster sprint follow-on |
| `NC-parity` | The C# side reads companion rarity from `Star`, not the sheet's `rarity` field — whether the cycling-rarity gate (X2 law) is enforceable in C# at all is open | dockets/companion-pricing §2 |
| `EB-14` | `selectors` is bot-feed only — a mod-side hook into the selection screens is the open item | eng-backlog §2 |

## tools — codegen, lint, scripts, refactors

| ID | Item | Provenance |
|---|---|---|
| `EB-3` | Two unlintable hand-written kit cards: `LetThePeopleRejoice.cs:57-82` and `AllTheWorldsAStage.cs:49,68` (+5 Encore/turn, outside the sheets) — extend the parity gate or add sheet rows | eng-backlog §1 |
| `EB-4` | Two p90s that disagree (`run_metrics._percentile` interpolates, `elite_blitz._percentile` nearest-rank while claiming to match) + two `wilson` impls with different return shapes — unify each; verify which convention the ratified bands used first | eng-backlog §1 |
| `EB-6` | Error-laundering fixes (five bare-except sites): `refpowers.py:1130`, `render_card_gallery.py:215`, `card_distinctness_report.py:435`, `extract_base_game_pool.py:528`, `exp_furina_strength.py:771` | eng-backlog §2 |
| `EB-7` | Waiver-set staleness tests — add the `KNOWN_IDENTICAL`-style guard to `PENDING_UNDERSIZE`/`PENDING_BANNED_FAMILY`/`PENDING_RED_PEN` in `art_lint.py`; also stop the two image checks `continue`-ing past unreadable files (:483,:532) | eng-backlog §2 |
| `EB-8` | Cross-sheet strict-domination check — the gate sweeps within-sheet only and prints `CLEAN` for two of six sheets; the Clorinde/Raiden pair was caught by hand | eng-backlog §2 |
| `EB-21` | `char_facts` baselines for Defect, Necrobinder and Regent — the patch sentinel reports three of five characters "not watched" for lack of `<char>_char_facts.yaml`; cheap, no design content | eng-backlog §3 |
| `EB-41` | Refactors, only if budget remains (big, safe, boring): `run_one` 518-line split; codegen driver unification (F3); telemetry-module template dedupe; `exp_*` script archive move; `apply_upgrade` op-coverage guard | eng-backlog §7 |
| `SYS-11` | Ratified changes not swept through prose (19 findings): stale before/after annotations in `kokomi-upgrades.yaml`, uncap-all stale cap comments, Fanfare-rework/v0.4 stale prose | triage-memo SYS-11 |
| `SYS-12` | Stale doc comments in code (9 findings): kaboom/sizzle/flame_dance sheet-number comments, catalytic_conversion "NO UPGRADE PATH", sparks_n_splash pool-membership | triage-memo SYS-12 |
| `L4`/`L7` | Remaining lint candidates from the S1 sweep: flat effect-list scans (L4 — shared `iter_effects()` recursing then/else; sparkly_explosion, pearl_barrage, `rider_tip_args` charge gap) and comment-arithmetic on upgrade sheets (L7 — recompute `# a->b` annotations, flags SYS-11a/b). L5/L6 landed only for their swept instances (replacement multiplier; draw/exhaust/discard plurals) — a general pass is still open | triage-memo Lint L1–L8 |

## tests — pins & filed-not-fixed

| ID | Item | Provenance |
|---|---|---|
| `EB-9` | `test_art_coverage.py::test_stale_file_is_not_counted_as_coverage` fails on any checkout without the gitignored `ImageGen/images/` tree — a machine-dependent test its own docstring warns against | eng-backlog §1 |
| `EB-11` | Understudy Defect 13 — `no_action` on a state with no `state_type`; **FILED, NOT FIXED** (next traversal pass) | eng-backlog §2 |
| `EB-12` | Understudy Defect 14 — `bridge_unreachable` by timeout with the process alive; one observation, no reproduction; **FILED, NOT FIXED** | eng-backlog §2 |
| `EB-13` | Understudy Defect 15 — `no_progress`, the map↔rest_site bounce (seed `43MLG7MG9L`); **FILED, NOT FIXED** | eng-backlog §2 |
| `EB-15` | The seed's `lobby` route never fired in three live runs; the lobby arm is retained and reports itself — nobody should read "two routes work" out of it | eng-backlog §2 |

## art — production work (the *picks* are [USER]'s in QUEUE; these are not)

| ID | Item | Provenance |
|---|---|---|
| `EB-36` | Three shipped cards render the BETA placeholder and are invisible to the coverage tool (`spotlight_center_stage`, `spotlight_guest_cast`, `confiscated`) — zero `art/plan.tsv` rows; structural blind spot in `tools/art_coverage.py` | eng-backlog §6; missed-requirements §4.1 |
| `EB-37` | The character-icon `_outline` asset was never produced — `Klee.cs:146`,`Furina.cs:84`,`Kokomi.cs:134` all return the fill `char_icon.png`; no outline row in plan/SOURCES | eng-backlog §6; missed-requirements §4.2 |
| `EB-38` | Animation Track F3 + the sprint-1 polish deferral — rest/merchant gentle idles both characters; in-combat layer approved and frozen but no polish sprint opened | eng-backlog §6; missed-requirements §4.5 |
| `EB-39` | `no_holding_back` still uses the `Klee Multi Wish` source L6 flagged as trimming 76% of the image | eng-backlog §6; missed-requirements §4.6 |
| `EB-40` | Furina's energy counter: `Furina.cs:97` still points at `ironclad_energy_counter.tscn`; `energy_icon_74/22` have no plan rows | eng-backlog §6; furina-art-pass-requirements §8 |
| `EB-42` | Path B (Skeleton2D) animation spike — a normal Code sprint, ruled FREE-SPIKE (Kokomi pilot); Path C layered remains the shipped fallback. (The spike→Spine-licence $379 reconsider is a QUEUE money call) | eng-backlog §6; R118 |
