# Tech debt review (2026-10-08, revised)

Read from `origin/main` (`e4255693`), `origin/klee-next` (`063e1b40`) and `origin/klee-measure` (`0fefc6be`). Nothing was edited, built or deployed. This is the second draft. A fact-check found real errors in the first, and the log at the end says what changed. Line numbers are on `origin/main` unless a branch is named.

## Summary

The biggest debt is a ruling that never reached `main`. Klee's measurement paper was ruled on 2026-10-05, with all five picks at their defaults. It says Balance is measured on the real game (seat suites plus fight telemetry), not in the sim, and it freezes a Balance kit on `main` between suite runs. The ruled paper and its edits to `EXPERIMENTS.md`, `stage-gate.md`, `STATE.md` and `QUEUE.md` sit only on the unmerged branch `origin/klee-measure`. Three files on `main` cite the missing paper. Because the PR amends `EXPERIMENTS.md`, it is yours to merge.

Second: the sim and the game disagree on Swirl. It pays in the game and not in the sim. The rest is clutter. STATE.md is 387 lines against a two-page norm. BACKLOG has 123 items, and three live bugs are filed under "Parked". There is unreachable shipped-kit code in the sim, a handful of dead tools, and 24 unmerged remote branches. Most of this is hygiene. Five picks remain. One is a one-way door (remote branches). Two delete code that could still serve as a design tool (the stand-in seam, the Furina v2 sim slice). One covers docs for the paused frame. One is eyes-on (Furina's motion look).

## 0. The stranded measurement ruling

| fact | evidence |
|---|---|
| Ruled paper exists only on a branch | `git show origin/klee-measure:review/active/klee-balance-measurement-2026-10-05.md`, line 3: "RULED 2026-10-05, all five picks at their defaults". Not in `git ls-tree origin/main review/active/` (47 files) or on klee-next. |
| Its commit also edits the law | `git show --stat 0fefc6be`: `EXPERIMENTS.md` +12, `stage-gate.md`, `STATE.md`, `QUEUE.md`, the paper; 170 insertions in all. |
| `main` cites the missing path | `review/records/klee-suite-1-2026-10-05.md:4`, `review/records/kokomi-review-round-2026-10-05.md:32`, `tier0/tests/test_telemetry_report.py:3` (`git grep klee-balance-measurement origin/main`). |
| `main` still describes the old law | `STATE.md:45` "measurement plan being drafted"; `STATE.md:372-375` "nothing is there today, so `EXPERIMENTS.md` is dormant ... bands retired until Balance"; `STATE.md:28` and `simulate.md:16-17` "retired until a kit reaches Balance". Klee has been at Balance since 2026-10-03. |

**Action (needs your merge, not a ruling):** rebase `klee-measure` on `main`, fix the STATE lines above in the same PR, and open it. It amends `EXPERIMENTS.md` text, so by CLAUDE.md it is your PR. Every other STATE edit below should wait for it, or ride in it, to avoid two rewrites of the same lines.

Its pick 3(a) already says to "delete the unreachable shipped-kit code (`BACKLOG.md`, legacy cleanup...)" and park `EB-195`, `EB-255`, `EB-810` and the Aeonglass port. So the sim sweep in 2.1 is already authorized. My first draft's pick 5 (sweep the engine before a baseline is pre-registered) is moot. The baseline is Klee suite 1 on the real game, and the sim is not the Balance gate.

## 1. STATE, QUEUE, BACKLOG

**Size.** STATE.md 387 lines, 4,330 words. QUEUE.md 53 lines. BACKLOG.md 147 lines, 123 items (Kits 50, Harness 50, Sim 13, Parked 10). The longest item is 675 characters. CLAUDE.md asks for "about two pages" for anything you read. STATE is about six.

**STATE.md, stale or wrong lines:**

| lines | says | truth | action |
|---|---|---|---|
| 14 | Installed `0.2.4456` | Later deploys exist (0.2.4516+next on klee-next). Not checked against the game dir: the lanes are live. | **drop** the number; `deploy_round.py` prints the real one |
| 28, 45, 372-375 | measurement plan drafting; law dormant; bands retired "until Balance" | ruled 2026-10-05 (sec. 0) | **fix in the klee-measure PR** |
| 108-115 | Kokomi "Next build ... Pool stays 39" | Kokomi's pool is 78 (line 46) | **delete**: a stale plan at the top of a finished history |
| 184 | Kokomi "Next: [USER] plays" | superseded by line 221, which is the current one | **delete 184 only**; keep 221 |
| 252 | Varka "Next: [USER] plays" | superseded by line 316 | **delete** |
| 318-326 | relics "built behind their arms ... Arm off" and "Next: a seat round with the relics given at embark" (325) | arm switches deleted at cleanup stage 5 (`Directory.Build.props:43-48`) | **rewrite** as two sentences on the current state |
| 348-349 | "`-p:SwirlPays=false` ... sim twin `C.SWIRL_PAYS`, off until its retest" | true, but it is the defect in sec. 3 | **fix** with sec. 3 |
| 354 | "All three prototypes" | four kits, one at Balance | **fix** wording |

**What reads STATE**, so a rewrite keeps these intact: the pin block (`tier0/tests/test_eb157_baselib_pin.py:44,92`), the `## Live cell` stamp table (`tools/lint_stamp_rows.py:39-40`), and the "Mod build environment" heading (named in a message at `tools/lint_game_assemblies_backup.py:101`). `test_agent_rituals.py:163` only mentions STATE in a comment; it reads `Directory.Build.props`.

**Shape fix (hygiene, after the klee-measure PR):** cut each kit to its current rules, pool and open next step. Move the pass-by-pass history out; git holds it. Target under 150 lines, keeping the three sections above.

**Pool counts.** Line 50 says "Every kit's pool target is 78". Furina's row says 34. That is not a contradiction: 34 is her current size, and `PoolCountTests.cs:18` still names 78 as every kit's target while pinning her at 34 (`:77-84`). No ruling moves her target. Leave line 50 alone. STATE should give each current pool once, in the roster table, citing `PoolCountTests.cs`, and drop the counts from the prose history.

**QUEUE.md.** Lines 11-12 ("All fifteen picks ... were ruled") are a dead sentence: **delete**. Line 26, "Klee to Balance: ruled yes", is a ruled item: **delete** it (the klee-measure commit already removes one QUEUE line; do both there). The Zhongli and Nahida picks are open: **keep**. Furina's motion look (AS2-B5) is pick 5.

**BACKLOG.md.**
- **Misfiled.** The last three "Parked" items (lines 145-147) are live seat-page bugs from Klee suites 3 and 4 with no trigger. **Move** them to Harness.
- **"Sim and measurement" section (lines 120-134).** It still ties `EB-195`, `EB-255`, `EB-810` and the Aeonglass port to "when a kit reaches Balance". The measurement ruling parked them (pick 3). **Move** them under Parked with the ruling as trigger, or delete them. The cleanup leftovers in the same section (lines 131-134) become the sweep in sec. 2.
- **`EB-193`** (regenerate `game_ref/role_tempo_canon.json`): its gate lint is gone, but `tier0/tests/test_role_tempo_coverage.py` and `tools/canon_role_tempo.py` still read the file. **Keep**, low priority.
- **Unchecked.** The packet counts 19 items dated before 2026-10-01 and 27 single-observation seat-page notes. I did not sweep them against the bridge code (about an hour, hygiene). One spot check: no commit since 2026-09-25 fixes the enchant chooser (line 69), so it stays.
- **Item length.** Trim items to the defect and its file; reasoning goes in the commit that closes it.

## 2. Deprecated sim and card machinery

### 2.1 What the legacy cleanup left

| leftover | where | action |
|---|---|---|
| Shipped-kit sim machinery: Charge, Burst, Salon, Encore, Spotlight, Garment, Muster, Kurage pulse, `burst_max` | `tier0/engine/*`, `tier0/constants.py` (`BURST_*`, `SPOTLIGHT_*`, `SALON_*`, `GARMENT_*`, `KURAGE_*`, `CONSCRIPT_COST_DELTA`); `burst_max` in the character yamls | **delete** (authorized by measurement pick 3(a), sec. 0). One PR, with a sim-number diff in the description. |
| `tier05.draft.ROSTER_ARCHETYPES` dead terms (salon, spotlight...) | `tier05/draft.py` | **delete** in the same PR |
| Generated-card header "Upgrade deltas come from docs/<character>-upgrades.yaml" and the Spotlight print fold (`SpotlightSystem.Printed*`, `SpotlitBlockVar`) | `tools/gen_klee_cards.py`; 55 generated card files (`git grep -c` over `klee-mod/KleeCode/Cards`) | **wait**: see below |
| `card_connectivity_report.py` (1,950 lines) and its `xfail(strict)` row test | imported by `tier0/tests/test_eb118_connectivity.py:37` and `test_eb83_timed_block.py:41`. `lint_effect_branch_scans.py:148` only names it in a string. | **keep for now**. Either teach it the current ops or delete it with those two tests. Low priority. |
| Seat-page Kurage and Salon bridge files | removed 2026-10-04 (`vendor/STS2_MCP/PROVENANCE.md:82`) | **fix** `review/active/legacy-cleanup-2026-10-01.md:158`, which still lists them as owed |

**The codegen regen is not a quick fix.** BACKLOG line 131 records why the stage left it: dropping the Spotlight fold "changes the emitted C# of current rows, which the stage ruled byte-identical". The regen touches 55 card files, Klee's among them. Klee is under the freeze ("A Balance kit's cards and rules on `main` ... do not change between suite runs", measurement paper line 127), and klee-next has 13 commits not on `main`. So the regen rides Klee's next promotion PR (built on klee-next), or waits until it lands. It does not ship with an ordinary deploy.

### 2.2 Found here, not on any list

| item | evidence | action |
|---|---|---|
| **Furina v2 re-founding sim slice**, 2,289 lines (engine 732, probe 559, pilot 454, test 544) | Four engine hooks in `combat.py:376,852,990,1145` and two in `effects.py:747,5993`. Each is a no-op for any player but `furina_v2` (`furina_v2.py:11,542`). Of the 2,289 lines, 1,557 are probe, pilot and test, which never run in a combat turn. The ruling discards "the overnight v2 build. That covers PRs #889 to #897 and #900's Furina rows" (`furina-research-proposal-2026-10-05.md:913-914`), but the same paper reads `ref:v2` as a comparison column (`:458`, `:929`). The sim slice is not named for discard. Other dependents: `furina_tide_probe.py:263-266`, allowlist keys in `test_eb495_kit_verb_triggers.py:82-85`, and the template note in `furina_tide_pilot.py:4`. | **pick 2** |
| Companion stand-in seam: the map is empty, the code is compiled | `grep -c "replaces:" docs/prototype-surface.yaml` = 0 on main and klee-next. Code: `companion_standins.py`, `CompanionStandIns.cs`, call sites in `tier05/rewards.py`, `tier05/shop.py`, `CompanionSlot.cs:131`, `MerchantCompanionSlots.cs:277`, `KleeExpansion.cs:176`, `gen_klee_cards.py`, and three C# test files. The docstring names a flag that is gone. | **pick 1**: a design tool (Klee brief pick 6), not only dead code |
| tier05 experiment scripts with no importer | `rework_sim.py`, `exp_furina_strength.py`, `exp_x9read_s1.py`, plus `charge_telemetry.py` (used only by `exp_x9read_s1`). Each is referenced only by its own test (`git grep -l`). | **delete** with their tests |
| 16 `test_furina_*.py` files, 3,365 lines, named for rounds | e.g. `test_furina_stage_retires_burst.py` still sets `burst_max=70` | **audit** in the sweep. Keep tests that pin Tab rules. Needs a read, not a grep. |
| Stale vocabulary | 379 "QUARANTINED" hits across tier0, tier05, tools and KleeCode (`git grep -c`) | **fix** comments and docstrings. Keep file and class names (`furina_stage.py`, `FurinaStage*.cs`); ids, art paths and tests cite them. |
| klee-next leftovers | `GroundedPower`, `SitTightPower`, `PatienceKleePower`, sim twins (klee-next BACKLOG line 20) | **delete after suite 5**, as already planned |

Not debt, kept: `tier0/harness/furina_loop_probe.py`. It was carried over to the Tab ("kept for the Salon's Tab, 2026-10-05", lines 7-8). The ruled proposal requires it before seats (`:625`). It ran today in `review/records/furina-tab-sim-sweep-2026-10-08.md:16`. The orphan constants `POTION_BELT_BONUS_SLOTS` and `MAP_MAX_EDGES` are test oracles, not frozen pins (`tier05/tests/test_potion_runlayer.py:199-389`, `tier05/tests/test_maps_and_routing.py:48`). Keep both.

## 3. The real defect: Swirl in the sim is not Swirl in the game

- `klee-mod/Directory.Build.props:49`: `SwirlPays` defaults to **true**. Every build Swirls for damage.
- `tier0/constants.py:66`: `SWIRL_PAYS = False`, "the arm convention". The arm convention ended at cleanup stage 5 (same props file, lines 43-48).
- `test_element_port.py:49` pins the sim default to False. `tools/varka_expansion_sim.py:242` and all six Varka test files set it True for themselves (`git grep -l "C.SWIRL_PAYS = True"`).

So Varka's own sims are already right. The gap is elsewhere: any sim of Klee, Kokomi or Furina that drafts an Anemo card reads a world where Swirl deals nothing. 19 non-Varka sheet rows mention Anemo (prefixes `mc` 10, `mi` 6, `mf` 3, by a Python pass over the 373 rows of `prototype-surface.yaml`; `vk` has 14 more). The reaction review reads game telemetry, so it is not affected.

**Fix (hygiene, with one caveat):** set the sim default True. Flip the pin to assert parity with the C# default. Add the switch to `lint_constant_parity` (today it compares only `SwirlDamage`, `tools/lint_constant_parity.py:127`). Put a before/after table in the PR for the sim figures that ruled papers quote (the Kokomi expansion sim, the Furina Tab probe). I have not run that diff. The caveat: CLAUDE.md makes a PR yours when it "moves a ... balance constant". This flip moves no shipped number; it brings the sim to what the game already does. I read it as hygiene. If you read sim defaults as balance constants, it becomes your PR.

## 4. Dead tools

113 top-level scripts in `tools/`. `git grep -l` over `.py/.yml/.ps1/.md/.json` for each name:

| script | lines | referenced by | action |
|---|---|---|---|
| `probe_e_sim.py` | 79 | nothing | **delete** |
| `pilot_error_audit.py` | 123 | `tools/README.md` only | **delete** |
| `encounter_audit.py` | 112 | README, one research doc | **delete** |
| `measure_realistic_act1.py` | 62 | README, one 2026-07-29 calibration log | **delete** |
| `probe_b2_table.py` | 215 | `understudy/README.md` only | **delete**, and its README line |
| `burst_defense.py` | 169 | `tier05/tests/test_calibration_tools.py`, docs | **delete** with its test cases |
| `klee_survival_sprint.py` | 346 | `tier0/tests/test_measurement_world_digest.py`, docs | **delete** only if the digest test just lists it; check first |
| `dump_claimed_sources.py` | 92 | atlas, one ruled art doc | **keep** if it still makes `docs/art-claimed-sources.tsv` |
| `varka_expansion_sim.py` (1,380) / `kokomi_expansion_sim.py` (696) | | three Varka tests import the first (`test_varka_defence.py:183`, `test_varka_element_identities.py:450,470`, `test_varka_rebalance.py:22`); both edited 2026-10-04 | **keep**: live Prototype design sims, kept by name in the measurement paper sec. 4 |

`tools/README.md` names `gen_roster_cards.py` (deleted at stage 5a), cites an absent `docs/tech-debt-audit-2026-07-26.md`, and lists 56 of 113 scripts. **Fix**: generate a one-line-per-script table from module docstrings. Caveat: a grep cannot see a script someone types by hand.

## 5. Tests and CI

- **Count:** 7,706 tests collected (`pytest --collect-only`; the main checkout is 33 commits behind `origin/main`, so the true count may differ slightly). Up from 3,195 on 2026-08-24 (`operations/test.md`). Plus 1,727 C# test attributes that CI does not run.
- **CI wall time:** the one run I have, 37724617413, is on klee-next, not main. Jobs took 56, 110, 107 and 52 s (`gh run view`), so CI is about 110 s. The pytest steps took 39, 94, 92 and 37 s. `.github/test-durations.json` was last refreshed 2026-09-28. **Fix**: rerun `ci_shards.py --update-durations`. Balanced, the steps would be about 66 s each; with roughly 15 s of setup per job, CI lands near 80 s. One run only.
- **Big single costs:** `test_axes.py` 64.8 s and `test_silent.py` 20.8 s run the twelve-arm battery. The ruling retires that battery as a Balance instrument. They may still earn their keep as engine regression tests; decide that in the sweep. `test_furina_loop_probe.py` (about 25 s locally, 41.9 s in that CI run) stays: see 2.2.
- **Pins that freeze numbers.** 347 test names say pinned / frozen / still_exact / baseline (packet count, not re-run). Not audited one by one. `test_element_port.py:49` is the clearest bad case: it freezes a default the game abandoned (sec. 3).
- **`test_prototype_surface.py:116-145`** asserts some file in `review/active/` names `prototype-surface.yaml`, under the premise "AN EMPTY FILE IS THE HEALTHY STATE". The sheet is now the release pool (373 rows). The premise is wrong, but the guard needs only one citing file and 12 exist, so it does not block anything. **Fix** its docstring with the yaml header (sec. 6); the assertion can stay.

## 6. Docs that drifted from code

| doc | stale text | action |
|---|---|---|
| `docs/prototype-surface.yaml:1-12` | "QUARANTINED ... in no reward pool, no release build ... AN EMPTY FILE IS THE HEALTHY STATE" | **fix**: it says the opposite of the truth |
| `docs/current/operations/simulate.md` | lines 12-17 name kit arms that do not exist; the example commands at 7-9 and 22-24 use shipped-kit decks and archetypes (`reaction_weighted`, `demolition_weighted`, `--archetype salon/demolition`); 16-17 says bands wait for Balance | **fix** all three, after the klee-measure PR |
| `docs/current/atlas/` | live: 35 commits since 2026-09-01, the last on 2026-10-04; read by `test_eb495_kit_verb_triggers.py`, `test_lane_d_enemy_seam.py`, `tools/ci_changed_paths.py`. The first draft found some citations to deleted lints and sheets (`tools.md`, `tier0-pilot-roster.md:63`). | **fix the dead citations in place**. Do not move it. |
| `docs/current/art/{furina,kokomi}-art-pass-requirements.md` | dead sheet paths (packet count 35 and 14, not re-run). Live art tools cite them as their spec: `art_coverage.py:2`, `art_fetch.py:79`, `art_hunt.py:2`, `art_lint.py:30,354`, `art_contact_sheet.py:7`, `art_source_census.py:8`, `gen_energy_orb_layers.py:14`, `test_art_source_census.py:4`. | **fix the paths in place**. Do not archive. |
| `review/active/legacy-cleanup-2026-10-01.md:158` | bridge files "owed" | **fix**, add a done banner |
| `tools/README.md` | see sec. 4 | **fix** |

**Filing closed papers.** `review/active/` holds 47 files. Many are live: the kit briefs CLAUDE.md routes to (`klee-brief`, `kokomi-brief`, `furina-stage-brief`, `varka-paper-kit`, `reaction-brief`), the Furina research proposal (her current rules), the Zhongli and Nahida papers (open QUEUE picks), and this week's Klee papers. File only a paper whose picks are all ruled and that STATE does not route to. Check each against QUEUE and STATE; do not move "about 40" in one pass.

**Frame docs.** The four largest operations docs are `codegen.md` 549, `understudy-seats.md` 425, `act-assets.md` 370 and `media.md` 328 (`wc -l`). `act-assets.md`, `media.md` and the Teyvat half of `codegen.md` serve the paused frame. That is pick 4.

## 7. Repo hygiene

- `understudy/logs/phase0-unseeded.jsonl` is tracked, and every unseeded run appends to it (`understudy/harness.py:234,281`). It is the `+dirty` on version stamps. **Untrack and ignore** that one file.
- 1,501 stray `*.pyc.<pid>` files under `__pycache__`, ignored by git: **delete**.
- The main checkout is at `5f9d0628`, 33 commits behind `origin/main`. **Fast-forward** it when the suite ends, so local tools run on current code.
- Worktrees: 23 in all. 10 sit on unmerged branches (`coop-notes-paper`, `klee-art-picks-2026-10-08`, `klee-measure`, `klee-next-art-known-missing`, `klee-review-build`, `klee-turn-one-paper-2026-10-08`, `klee-tempo-build`, `nahida-paper-sim`, `reaction-gate-debug`, `zhongli-paper-sim`). Keep those. **Purge** the merged ones with `purge_worktree` after the suite. Prune merged local branches (recoverable).
- Unmerged remote branches: 24. Two carry small doc diffs that never landed: `coop-notes-paper` (2026-10-02, 1 file, +4/-3) and `varka-expansion-paper` (2026-10-01, 2 files, +3/-5). **Read each diff**, then land it by PR if still true, or note it as dropped. `klee-measure` is sec. 0.

## Hygiene Claude can just do

Touch nothing while suite 5 runs. Order: the klee-measure PR first (yours to merge), then the rest.

1. Rebase and open the klee-measure PR, with the STATE lines in sec. 0.
2. STATE: delete 108-115, 184, 252 and the installed version; rewrite 318-326; fix 354. Keep the pin block, the Live cell table and the build-environment heading. Target under 150 lines.
3. QUEUE: delete lines 11-12 and line 26.
4. BACKLOG: move the three seat-page bugs to Harness; move the parked sim items under Parked; trim items to one line; sweep the 27 seat-page notes and 19 pre-October items.
5. Swirl parity (sec. 3), with the before/after table.
6. Sim sweep: shipped-kit machinery, `ROSTER_ARCHETYPES` dead terms, tier05 experiment scripts, the 16 Furina round tests (read first), QUARANTINED wording.
7. Delete the seven dead tools (sec. 4, after the digest check) and regenerate `tools/README.md`.
8. Fix the docs in sec. 6 in place; file closed papers one by one.
9. Refresh `.github/test-durations.json`.
10. Untrack `phase0-unseeded.jsonl`, clear `.pyc` debris, fast-forward the main checkout, purge merged worktrees, prune merged local branches, read the two small unlanded doc branches.
11. With Klee's next promotion: the codegen regen (header line and Spotlight fold).
12. After suite 5: the klee-next Grounded / Sit Tight / Patience leftovers.

## Picks

1. **Companion stand-in seam** (about 525 lines plus C# tests; no row uses it). (a) Delete it; git keeps it if a kit wants "a Klee-only version of a Universal" again. (b) Keep it as an empty, tested capability. **Default: (a).** It touches C#, so it ships with a round's deploy.
2. **Furina v2 sim slice** (2,289 lines; hooks are no-ops for other players). The overnight v2 build was discarded; the sim slice was used as `ref:v2` in the Tab proposal and was not named. (a) Delete it with its hooks, the tide probe's v2 arm and the `test_eb495` allowlist keys; tag the last commit that has it. (b) Keep it as a comparison baseline. **Default: (a).** The Tab is built and its kill questions are answered.
3. **Merged remote branches** (220 of 242 at the first count; every commit stays reachable through `main`'s merges). Deleting them is a one-way door. (a) Delete the merged ones. (b) Leave them. **Default: (a).**
4. **Teyvat frame docs** (`act-assets.md`, `media.md`, Teyvat parts of `codegen.md`; about 1,000 lines). You ruled "nothing deleted" for the frame. (a) Leave them. (b) Keep the code; fold the docs into a 20-line pointer to the last commit that has them. **Default: (b).** Say (a) if "nothing deleted" covered the docs.
5. **Furina's motion look** (QUEUE, AS2-B5). The plan predates two rebuilds of her kit. (a) Drop it from QUEUE; re-ask at her finish line. (b) Keep it open. **Default: (a).**

Thin evidence, stated plainly: CI timing is one run, on klee-next. Tool liveness is grep only. The 19 and 27 BACKLOG counts, the 347 pin names, the art-doc path counts and the `run_lints --list` result come from the packet and were not re-run. The Swirl sim-number diff has not been run.

## Fact-check log

Accepted and fixed (each re-checked on `origin/main` unless noted):
- **Stranded measurement ruling.** Confirmed: `0fefc6be` on `origin/klee-measure` holds the ruled paper and its law edits; not on main or klee-next. Added as sec. 0. Pick 5 removed as moot, and the "clean engine before pre-registration" rationale removed. The shipped-kit deletion now cites the paper's pick 3(a). One correction to the check: the third citer on main is `tier0/tests/test_telemetry_report.py:3`, not `klee-scaling-pass-2026-10-05.md:26` (`git grep` finds no hit in that file).
- **Furina loop probe.** Confirmed kept for the Tab (`furina_loop_probe.py:7-8`), required by the proposal (`:625`), run today (sweep record `:16`). Deletion withdrawn.
- **Furina v2.** Confirmed: the hooks are no-ops for other players, 1,557 of the 2,289 lines never run in combat, and the ruling names the build, not the sim slice. Softened, and moved from hygiene to pick 2. Added the `test_eb495` and pilot dependents.
- **Atlas.** Confirmed 35 commits since 2026-09-01 (last 2026-10-04), plus two tests and a CI tool reading it. Archive withdrawn; fix in place.
- **Art-pass docs.** Confirmed nine tool and test citations. Archive withdrawn; fix in place.
- **Expansion sims.** Confirmed three Varka tests import `varka_expansion_sim`, and both files were edited 2026-10-04. The "one-shot record" header was withdrawn.
- **`card_connectivity_report`.** Confirmed: the lint only names it in a string (`:148`); two tests import it.
- **STATE "Next:" lines.** Confirmed line 223 has none and 221 is Kokomi's current line. Following the first draft would have deleted it. Now: delete 184 only. Added Varka 252 and relic 325.
- **STATE readers.** Confirmed `test_agent_rituals.py:163` is a comment. Added `lint_stamp_rows.py` and `lint_game_assemblies_backup.py`.
- **review/active.** Confirmed 47 files and 12 citing the sheet. The guard does not block filing. The bulk move was withdrawn; file one by one.
- **Codegen regen.** Confirmed BACKLOG:131 and 55 card files; klee-next is 13 ahead. Moved to ride Klee's promotion.
- **Swirl.** Confirmed six Varka test files, props line 49, and that the reaction review reads telemetry. Softened. Added the Anemo-row count, the before/after diff and the balance-constant caveat.
- **test_axes / test_silent.** The reason was changed to "engine regression, decide in the sweep".
- **Pool target 78.** Confirmed `PoolCountTests.cs:18` still says 78 is every kit's target. The "except Furina" rewrite was withdrawn as an unruled design statement. I did not make it a pick either: nothing is open, and her finish-line paper can raise it.
- **Ops doc sizes, summary pick count, timings, orphan constants, minor line numbers.** All confirmed and fixed. CI is now about 110 s on a klee-next run, the balanced estimate is about 80 s, and the constants are kept as oracles. Kokomi's 78 is at line 46, SwirlPays at 348-349, "three prototypes" at 354, and QUEUE's dead sentence at 11-12.
- **Gaps added:** STATE Live cell and "until Balance" lines, the BACKLOG sim section, unmerged branches and worktrees, the stale main checkout, and the broken simulate.md example commands.

Rejected or corrected:
- **"Third Kokomi Next: is line 115."** `grep -n "Next:"` on STATE finds 184, 221, 224, 252, 316, 325 and 351, but not 115. Lines 108-115 say "Next build:", which is still deleted as a stale plan. So Kokomi's bullet has two "Next:" lines, not three.
- **"22 remote branches unmerged."** Today's count after `git fetch` is 24 (`git branch -r --no-merged origin/main`). New branches from today, such as `klee-art-picks-2026-10-08`, likely explain the difference. I used 24.
