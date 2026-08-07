# BACKLOG

> **Only OPEN executable engineering work** — confirmed defects, mechanical /
> parity fixes, measurement instruments, refactors, and test-writing that need
> **no [USER] design call to start**. One of six governing files, no overlap:
> [USER] design / taste / behavior / money calls live in **QUEUE.md**, settled
> rules in **LAW.md**, shipped facts in **STATE.md**, commands in
> **OPERATIONS.md**. Identifiers are preserved from their source registers;
> closed items are in git history (tag `pre-simplification-2026-08-06`).

> **Resolving a provenance identifier.** `eng-backlog`, `dockets/…`,
> `user-queue` and the retired sprint docs read at
> `git show pre-simplification-2026-08-06:<path>`. The two recap registers —
> `missed-requirements` and `open-playtest-items` — left HEAD after their
> rows migrated here; read them at
> `git show aa09b97:docs/current/backlog/missed-requirements.md` and
> `git show aa09b97:docs/current/playtest/open-playtest-items.md`
> (`git fetch --depth=1 origin aa09b97` first on a shallow clone).

---

## tier0 — engine, pilot, constants

| ID | Item | Provenance |
|---|---|---|
| `EB-17p` | Force-first-copy **paired** winrate — the register's actual phrase: two decks on the same seeds, one with a copy forced in, one without. Deck construction is barred from the tier0 kernel, so this is a tier05 experiment under EXPERIMENTS pre-registration. The fight-side half ships (`metrics.card_flow_profile`, `--card-flow`) and explicitly declines to call its within-arm split the pairing | fix-sweep-2; EB-17 residual |

## tier0.5 — draft / run layer / measurement

| ID | Item | Provenance |
|---|---|---|
| `EB-16w` | Wire `route_regret` into the live run layer: `model.run_one` walks incrementally and `RunResult` records no route decisions, so nothing calls the sampler on a real run yet (`route.walk_decisions` exists for it); promote the sample-rate default to `tier0/constants.py` and calibrate `ROUTE_REGRET_MARGIN` (the 1.0 is a literal `draft_regret` analogy, not a measured threshold). Then §3.7.5's "relics underpriced" comparison can actually be re-run | fix-sweep-2; EB-16 residual |
| `EB-27` | Two tier0.5 spec features never built: `choose3` standalone slot mode (`model.py:246-250` raises `ValueError`) and the Prune signature event (`events.py` offers none) | eng-backlog §4; missed-requirements §3.5 |
| `EB-28` | The drafter's salon-deploy blindness — `tier05/draft.py:_static_power` has no `salon_member` term, so cross-plan the members are invisible | eng-backlog §4; missed-requirements §3.6 |
| `EB-43` | **D15 (spotlight-limb payoff-presence) — STAGED, HELD.** Drafter behaviour change (`DRAFTER 15`) + re-baseline sweep; `Q18` countersigned, pinned DRAFTER 14. **Lands as step (5) of a fixed six-step order** — must not land before blind-first grading (4) or it invalidates the registration | eng-backlog §6; R121 |
| `SKIP-10.9` | Living skip-backlog of un-modelled mechanics to promote when a pass needs them. **Enemy:** Back Attack (Kaiser Crab), untargetable Burrow (Tunneler), Ethereal/Hex auras (Knight Gang), pick-your-poison curse choice (Knowledge Demon), damage caps (Hard to Kill / Plating / Hardened Shell), Artifact, Thorns, on-hit status injection, every-N-cards cadence intents, buff-all-enemies, block-an-ally, random-no-repeat AI, self-stun, Slimed self-exhaust, the minor-power list (Imbalanced / Ringing / Paper Cuts / Stock / Galvanic / Rampart), Soul Siphon stat-theft class (the Matriarch's player-half drain landed with EB-25), and the two Ancient relic hooks — Blessed Antler and Philosopher's Stone. **C#-side structures with no sim twin (EB-19):** the deferred-settle machinery (`SpotlightSystem` PendingDraws / `CurtainCallPowers` NoteEncoreSpent / `FurinaResources` PendingDeltaBlock — parity rests on every flush site being reached; a stranded draw is the failure mode) and per-dealer reaction windows (ruled co-op divergence, red-pen R1; solo is byte-identical). *Restored to the full §10.9 open list 2026-08-06 — the migration had dropped ~14 entries, making logged approximations read as unlogged fakes (EB-29c)* | run-model-rework-plan §10.9; EB-29 audit |

## klee-mod — C# implementation & parity

| ID | Item | Provenance |
|---|---|---|
| `EB-1` | **Punch Off crash** (reclassified GAME-SIDE/SPINE-SIDE) — the animation stream keeps the watch; not done while seed `8B97LMCL2F` crashes in Punch Off | eng-backlog §1 |
| `EB-14` | `selectors` is bot-feed only — a mod-side hook into the selection screens is the open item | eng-backlog §2 |

## tools — codegen, lint, scripts, refactors

| ID | Item | Provenance |
|---|---|---|
| `EB-41` | Refactors, only if budget remains (big, safe, boring): `run_one` 518-line split; codegen driver unification (F3); telemetry-module template dedupe; `exp_*` script archive move; `apply_upgrade` op-coverage guard | eng-backlog §7 |

## tests — pins & filed-not-fixed

| ID | Item | Provenance |
|---|---|---|
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
