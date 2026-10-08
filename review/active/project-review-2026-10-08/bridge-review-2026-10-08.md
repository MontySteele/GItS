# Testing bridge review (2026-10-08, revised after fact-check)

**Summary.** The bridge works. Seats finish acts. In 43 Sonnet seat-acts from the night of 2026-10-06/07 (23:28 to 07:47 UTC), 146 of 5,189 tool calls were refused (2.8%, median 2 a seat). None of the 38 embark logs from 2026-10-05 to 10-08 shows a failed embark. The biggest fault tonight is not in the bridge. **Suite 5's act-1 seats ran the page's Python from the main checkout while the game ran the `klee-next` build.** Where no Bomb tip was on screen, the page said a Bomb grows 4 and a fight opens with 1 Spark. The build says 2 and 3. The coordinator moved the act-2 briefs to the `klee-next` worktree at 00:24. That fixed the numbers but split every per-lane state file: **since about 00:24 the act-2 seats have run with no action cap, a reset words store, and no build identity in their sealed records** (section 1a). That needs a fix before act 3 starts. After it come cheap harness fixes: lane scripts baked by `seat.py`, a brief that matches the lane's cap, page trims the seats' own filter scripts already describe, and a few co-op lines. Page trims save more than I first said. Cache writes are about 29% of the bill and grow with page size (section 3). Co-op evidence is two pair-runs on one seed in the 2026-10-07 round, plus earlier rounds on 09-27 and 09-30.

## 0. Tonight's incident: the python kill

Another agent ran `taskkill /F /IM python.exe` and killed PIDs 44888 and 60936 without identifying them. I checked the lanes from disk only. I did not touch any game or port.
- **No lane stalled.** Each main-checkout counter (`understudy/logs/_blindplay-budget-laneN.json`) was rewritten between 00:19:14 and 00:19:23. The five games were up, started 23:55:30 to 23:56:02.
- **No counter was truncated.** The counter is written in place (`understudy/blindplay_shape.py:170-175`). A kill mid-write would leave a file that reads as cap 0, meaning no cap. None did.
- **Keep-awake does not matter tonight.** AC standby is 0, meaning never (`powercfg /query`).
- **Two stray Store-alias pythons were up** at the time (PIDs 62932 and 16292, `WindowsApps\python.exe -`), from other fan-out agents. Kill such strays by PID after reading the command line. Never kill by image name while lanes run.

## 1. Solo page and harness

**1a. Page and game come from different builds, and the fix split the lane state (urgent).**

*The skew.* The act-1 wrappers `cd` to the main checkout, on `main` at `5f9d0628`. The game runs `klee-next` at `063e1b40`, checked out at `GItS-klee-review-build`.
- `BOMB_GROWTH` is 4 on main and 2 on klee-next (`blindplay_shape.py:36`). The page reads growth off the screen's own Bomb tip when one is shown; klee-next's tip prints 2 (`ArmKeywordTips.cs:167` on klee-next; `blindplay_notes.py:1432-1434`). It falls back to the stale 4 elsewhere, including `observe --define` (`blindplay_notes.py:3017`). With the once-per-lane words store, that fallback can be the only definition a seat sees. Lane 3 wrote "Bomb grew +2/turn seen (8,10,12), not 4 as defined?" Lane 1 wrote "8->10 shown; thought 4". Lane 2 wrote "14->18 (+4/bomb/turn)" with two Bombs on the target: the total fits 2 a Bomb, the label fits the stale 4.
- `OPENING_SPARK` is 1 on main and 3 on klee-next (`blindplay_shape.py:59`). It feeds the Spark glossary rule (`blindplay_notes.py:204`).
- The skew is older than tonight. In suite 4 the shop shelf printed Explosive Spark at "cost 0", because the Spark-price index is read off the checkout's own `klee-mod` (comment in `blindplay_faces.py` near line 497, both branches).
- **Separately, the main checkout is 33 commits behind `origin/main`** (`git rev-list --count main..origin/main`). That includes #958, the shop Spark-price fallback (`card_spark_price`, `origin/main:understudy/blindplay_faces.py:513-514`). Suite 5's act-1 page did not have it.

*The live side effect.* At 00:24 the coordinator pointed the act-2 briefs at the worktree (`S\suite5\brief-next-lane1.md:14-15`, `cd ".../GItS-klee-review-build" && ...`). But blindplay keeps per-lane state in its own checkout's `understudy/logs` (`blindplay_shape.py:127`, `_BUDGET_STORE_DIR = Path(__file__).resolve().parent / "logs"`). I listed both folders at 00:45:
- The worktree has new `arm`, `deck`, `events`, `fight`, `run` and `words` files for lanes 1-5, and **no budget file for lanes 1-5**. So `read_budget` returns cap 0, which means no cap. The main-checkout counters stopped at 00:22-00:28 (lane 3 at 247 of 1500).
- The words store restarted, so definitions print again in act 2. "Since last page" and fight state also restarted.
- The worktree has no `embark-*.json` sidecar, so the arm cannot be matched by seed, and no `klee-mod/local.props`, so `build_version()` (`blindplay_record.py:55-81`) cannot find the game and sealed records read "(not read)".

Fixes, in order:
- **Before act 3 starts:** copy each lane's `_blindplay-budget-laneN.json` (and the `embark-*-laneN.json` sidecar) from the main checkout into the worktree's `understudy/logs`, and copy `klee-mod/local.props` (a single config file, not an asset directory). Or put `GITS_MAX_ACTIONS=1500` in the act-3 brief command, which `budget_cap` reads first (`blindplay_shape.py`, `budget_cap`). The act-2 cap overrun is already spent and cannot be undone. Note it in the suite 5 record.
- **Then:** key the state folder to an environment variable or a fixed path, not to the checkout, so one lane's state survives a checkout change.
- **Then:** make the page prefer live game values everywhere, as `card_spark_price` and the Bomb tip already do. The bridge can emit `KleeOverhaulLaw.BombGrowth` and the opening Spark, so the Python mirrors become a fallback only.
- **Then:** a build check. `build_version()` already reads the deployed `mods\klee\manifest.json` version (for example `0.2.4516+next`) into each sealed record. Have `blindplay` print one warning when that version does not match its checkout's branch. A sidecar-based check would break whenever blindplay runs from another checkout than embark, as tonight.
- **Always:** pull the seat checkout to `origin/main` before a round.

**1b. Seats wander out of the repo and their commands fail.** `ModuleNotFoundError` shows in 21 of 43 transcripts (`S\fanout\bridge_refusals.py`). These are failed commands, not crashes. The brief's command works from the default working directory, which is the repo root. The fact-check traced every failure to the seat first changing directory (`cd /tmp`, `cd /c`, a scratch folder). Wrappers that hard-code a `cd` are the seats' own answer: 30 of 32 suite 2-4 records (packet section 5a) and 5 of 5 suite 5 seats. **Fix:** `seat.py --opus-brief --scratch` writes `o` and `a` scripts into the seat's folder, with lane, interpreter, `--brief` and repo root baked in, and the brief names them. This also removes the cross-lane risk the brief warns about ("a shared wrapper once drove another seat's lane").

**1c. The brief contradicts the lane.**
- `seat-brief.md:93` says "120 accepted `act` calls for an act". The lane prints "budget: 1500 actions". Three suite 3 seats noted it (`suite3\seat-lane3\record-act1.md:5`: "the 120 cap in the brief was not enforced").
- The doc's header calls the seat "an Opus tester" (lines 1 and 3). Seats never see it: nothing above the `---` is sent (`seat-brief.md:9-10`), and the emitted brief has no "Opus". Rename it for accuracy only.
- The coordinator's brief files are cp1252 with CRLF. Each em dash becomes byte 0x97.
- At 00:45, lanes 4 and 5 still had no `notes.md` in act 2 (`S\suite5\seat-lane4`, `seat-lane5`). Notes are the only handoff if a seat dies mid-act.

**1d. Seats trim the page themselves.** Suite 4 lane 1's `s.sh` drops `Its .* is a price`, `***Vigor`, `Written:`, `(the line above` and `## Words`. It also prints only lines 1-10 plus the hand-to-Words span, so it drops the whole relic block and "What reacted this turn". That is a free spec for `--brief`. On one saved page (`S\suite4\seat-lane1\o.txt`, 3,978 bytes) the relic block was 1,072 bytes (27%) and the Spark-price sentence 332 bytes (8%). The words store (`blindplay_brief.py:28`) can carry relic texts and the price sentence: relic name plus counter after a fight's first page, price sentence once per lane. One page is one example; measure page bytes before and after.

**1e. Refusals: few, mostly one kind.**

| Refusal | Count | Fix |
|---|---|---|
| "you are not in a battle" (`blindplay_grammar.py:1336`) | 30 | A chained play after the fight ended. Say "the fight is over" and print the next page |
| "you are not in a shop" | 8 | Same pattern |
| "nothing here is called 'Strike (3)'" and similar | 7 | Copies renumber after a play (`BACKLOG.md:73`). Name copies stably, or say "renumbered" |
| "a card chooser is open" | 6 | Fine as is |
| reward screen still holds an item | 15 or more | Working as designed (held once) |

Refusals are not charged against the budget. The cost is a wasted page.

**1f. Page facts the seats asked for.**
- **A set-off receipt per Bomb or Mine:** which Bomb went off, on whom, for how much. 4 seat reports. It is open on `origin/main:docs/current/BACKLOG.md:147`, which says it "Needs a detonation log in the mod like ReactionLog, a bridge read and a page line". `ResolutionLedger` files card plays only (`BACKLOG.md:101`), so it cannot supply this.
- **Enemy rules:** Reattach and its countdown is open (`BACKLOG.md:100`). Surrounded, Flutter against Bomb damage, Enrage and curse growth drew reports but have **no** BACKLOG line yet. Adding lines is hygiene.
- **Effect draws in "Since last page"** (`BACKLOG.md:34`) and **enemy act order** (`BACKLOG.md:117`).
- **Mine timing** drew reports from 4 seat lanes (packet 5b). The glossary row is pinned word for word to the mod's tooltip by a test (`blindplay_notes.py:1424-1426`, `1489-1491`), and the tip already says "goes off just before its enemy attacks". Adding a clause means changing Klee's in-game text against the ruled short-text pass, on a build under review. I do not propose it here.

The Klee number lines (`BACKLOG.md:83-89`) belong to the Klee review. The "HP after this turn's hits if you play no Block" line has shipped ("You would be at 0/68 HP").

## 2. Co-op (`--fastmp`)

The 2026-10-07 round had two pair-runs on seed 30KMHAVG9SMQ, Klee + Varka and the Ironclad + Silent control, plus an abandoned first try (`review/records/coop-reaction-round-2026-10-07.md:9-16`). Earlier rounds: `coop-seat-round-2026-09-27.md` and the 09-30 Varka + Kokomi round.
- **Fixed during the 10-07 round:** the potion-discard desync (#948) and the Crystal Sphere under the map (#949).
- **Map votes.** A split vote sent the control pair to the elite that killed them. Claude's call: the brief tells the client seat to match the host's vote when it shows under "Choices so far". That removes routing noise from strength readings.
- **Fight ended under the seat.** "You are not in a battle" when the partner finishes the fight (three Klee screens). The 1e fix covers it.
- **Six page items logged 2026-09-27** (`BACKLOG.md:42`): partner's cards credited to you, players named "Test Host" and "Test Client 1" (from the game; no such string in our code), the reaction glossary ignores the partner's element, contested chest picks unannounced, `wait` silent while a reward is up, silent retargeting. Not re-tested.
- **One pair per machine.** The host binds UDP 33771 (`embark_coop.py:58`). Claude's call: run pairs one after another. Patch the port only if co-op rounds become routine.
- **Dev grants.** `give_card` is refused in co-op (`BACKLOG.md:47`).

## 3. Cost per floor and per-act handoff

- **Size of a seat-act.** From `S\fanout\census.out` (41 Klee and Varka seat-acts since 2026-10-05): median 115 model calls, 9.6M cache-read tokens, context peak 130k to 230k. A median act-1 seat makes 203 accepted acts, about 7 calls and 12 actions a floor. Memory puts that at $0.1-0.2 a floor; I did not reprice it.
- **Where the cost goes.** The base-five record's own table (`base-five-baseline-2026-10-05.md:36-42`) gives 175M cache reads at 1/20 = 8.75M and 2.89M cache writes at 1.25 = 3.61M, for 12.4M. **Reads are about 71% and writes about 29%.** The record's prose line "about 95%" (line 44) disagrees with its own table; fix it. Writes grow with each new page, so page trims cut both terms.
- **How much a trim saves.** Tool output is a median 219 KB per seat-act, about 55k tokens (`bridge_refusals.out`). I cannot split the rest of the 130k-230k peak between reasoning and system prompt: logged output tokens are only 500 to 2,500 per seat, and the records say transcripts under-log them. So I give no percentage. Measure it with the before-and-after page bytes from 1d.
- **The handoff is cheap.** Act 2 and 3 seats read an 8 KB brief plus the prior record (7 to 15 KB), about 5k tokens against a 150k+ context. Per-act splitting is already the shape.

## 4. Telemetry

`load_fights(default_dirs())` now holds 5,390 rows (4,650 bot, 740 human). Rows since 2026-10-05 local: 1,328, all bot.
- **"Base characters lack `enemy_hp_by_turn`" is a date window, not a gap.** Base five has it on 0/220 fights on 10-05 and 62/62 on 10-07. Furina (0/42) and Kokomi (0/37) were last seated on 10-05.
- **`reactions_by_type` is always written from 10-07 on**, empty when nothing fired. "Cannot tell zero from not logged" holds for older rows only.
- **No per-set-off record.** Only per-fight `detonations`, `mine_detonations`, `corpse_detonations`.
- **No build stamp on a row.** Rows can still be told apart: klee-next rows carry `homework_bomb_size` on every fight (799 rows: Klee 573, Varka 164, Silent 56, Ironclad 6; first at 2026-10-06 00:09), and `run_id` joins to the sealed record's build version. A mod version on each row would make this direct.
- **`homework_bomb_size`** exists only on klee-next (`origin/klee-next:klee-mod/KleeCode/Diagnostics/PlayTelemetry.cs:1524`); main's `PlayTelemetry.cs` does not write it. `BACKLOG.md:90` stays open on main until that lands.
- `meters_by_turn` is already marked retired (`understudy/README.md:862`); older rows carry it. `intent` is a declared-archetype field, empty by design (`README.md:947`; filled on 137 rows in August). Neither is dead.

## 5. Lane robustness

- **Embarks are solid.** No failed embark in 38 logs. The slow-boot warning raises the menu wait from 180 s to 180-210 s, so 0 to 30 s added (`grep "menu-ready wait"` over `embark-2026100[5-8]*-lane*.log`).
- **Non-atomic state writes.** Counter and refusal mark are written in place (`blindplay_shape.py:170-175`, about line 228). Use a temp file and `os.replace`.
- **Open stall classes in `BACKLOG.md`:** Kifuda chooser (69), `EB-489` (104), `EB-391` rest (105), `scenario run` on a profile with a saved run (114). None hit a seat this week.

## 6. Dead weight around the bridge

- **Dormant doc sections.** `understudy-seats.md:315-377` (63 of 425 lines) documents the Codex seat, the local Qwen seat and the staged-turn funnel. No seat since 2026-09-28 used them. Cut to one paragraph.
- **The code is not safe to retire.** Counting indirect and lazy imports, the live path reaches most of it. `embark` imports `soak` (`embark.py:114`), which imports `policy_v1` (`soak.py:112-113`), which imports `policy_v0` (`policy_v1.py:120`). `soak_driver.py:117` lazily imports `p2capture`. `blindplay_session.py:18` imports `seat`, which lazily imports `staged_turn` (`seat.py:1202`) and `codex_usage` (`seat.py:1222`). `staged_turn.py:130` imports `scenario`, and the CI lint `face-defects` (`run_lints.py:126`) reaches `scenario` through `face_defects.py:57`. Any retirement needs a real import-graph check first.
- **Untracked agent files.** `.claude/agents/*seat*.md` are untracked (`git status`), so the seat's model and effort settings are in no commit.

## Hygiene and Claude's calls (no ruling needed)

1. **Now, before act 3:** restore cap and identity in the worktree (1a, first bullet). Record the act-2 cap overrun and the restarted words store in the suite 5 record.
2. Key blindplay's per-lane state to an env var or fixed path. Have the bridge emit Bomb growth and opening Spark. Warn when the deployed manifest version does not match the checkout. Pull the seat checkout before a round.
3. `seat.py --opus-brief --scratch` writes `o` and `a` lane scripts, and prints the brief as UTF-8 with LF.
4. `seat-brief.md`: budget line says "the lane's cap, printed on every page"; header says "blind seat"; ask for a `notes.md` line after each fight.
5. `--brief` page: relic name plus counter after a fight's first page; Spark-price sentence once per lane. Measure bytes before and after.
6. "The fight is over" plus the next page instead of "you are not in a battle" (covers co-op too).
7. Stable copy names or a "renumbered" line (`BACKLOG.md:73`).
8. Add BACKLOG lines for Surrounded, Flutter, Enrage and curse growth on the page.
9. Atomic writes for budget and refusal-mark files.
10. Fix the "about 95%" line in `base-five-baseline-2026-10-05.md:44` to match its table.
11. Cut `understudy-seats.md:315-377` to one paragraph. Keep the code.
12. Track `.claude/agents/*seat*.md` in git.
13. Co-op: client matches the host's map vote; pairs run one after another.
14. Base control: a base-character control seat each round is already ruled. Run act-1 base seats on the current page after suite 5 ends, from tonight's spare budget, so kit comparisons do not mix page versions (the 10-05 baseline predates `enemy_hp_by_turn`, pages 5-6 and #945).
15. Coordinators: never `taskkill /IM python.exe`.

## Picks for [USER]

None. Everything above is engineering, instrument procedure or a reversible deletion, which CLAUDE.md gives to Claude. The base control seat was already ruled yes.

## Fact-check log

**Accepted and changed:**
- BACKLOG citations corrected: renumbering 73, Homework II size 90, Reattach 100, EB-489 104, EB-391 105, scenario run 114, enemy act order 117, Kifuda 69, give_card 47. I checked each line with `sed -n`.
- "Safe to retire" withdrawn. I confirmed the import chain. One nuance: `lint_face_defects.py` imports `face_defects`, and `face_defects.py:57` imports `scenario`; the lint does not import `scenario` directly at its line 57.
- Cost share: reads 71%, writes 29%, recomputed from the record's table. The "95%" came from the record's own prose, which is wrong; added as hygiene.
- homework_bomb_size: on klee-next only (confirmed with `git grep`); BACKLOG:90 stays open on main.
- Receipt source: `ResolutionLedger` cannot supply it; cited the origin/main BACKLOG:147 note.
- Skew predates tonight (suite 4 "cost 0"); Spark-price fallback is on origin/main too (#958); main checkout 33 commits behind. All confirmed.
- "Opus tester" header: seats never see it (confirmed: no "Opus" in `brief-lane1.md`). Downgraded to accuracy only.
- ModuleNotFoundError: reworded as failed commands after the seat changed directory. I did not re-scan the transcripts for the `cd`; this rests on the fact-check's scan.
- Telemetry: build can be told apart by `homework_bomb_size` presence and `run_id`. Row counts re-run now (5,390; 1,328 since 10-05), slightly above the fact-check's because rows keep landing.
- `meters_by_turn` and `intent` are not dead; dropped that hygiene line.
- Slow boot: 0 to 30 s (my grep of 38 logs: 180 to 210 s).
- Mine timing: no BACKLOG line; tip text is test-pinned to the mod; withdrawn as hygiene. Surrounded, Flutter, Enrage, curse growth: not in BACKLOG; now a hygiene item to add them.
- Picks 1 to 4 moved to Claude's calls (pick 1 was already ruled; 2 to 4 are reversible engineering).
- Co-op evidence: two pair-runs plus earlier rounds.
- Bomb "grows 4": mechanism stated (tip first, stale fallback otherwise).
- Live gap added: act-2 seats run from the worktree with no cap, restarted state, no sidecar and no `local.props`. Confirmed by listing both `understudy/logs` folders at 00:45: the worktree has no `_blindplay-budget-lane1..5.json`, while main's lane counters stopped at 00:22-00:28 (lane 3 at 247).
- Refusal scan window stated as 10-06 23:28 to 10-07 07:47 UTC (confirmed in `bridge_refusals.out`), including two co-op control seats. Reward-screen count raised to "15 or more".

**Rejected or qualified:**
- "Since about 00:34 all five act-2 seats run with... a fresh counter": qualified. The briefs changed at 00:24, and the worktree has no budget file at all for lanes 1-5, so there is no counter, not a fresh one. The start time per lane varies (main counters stopped 00:22 to 00:28).
- "Lane 2's notes adopt '+4/bomb/turn'": qualified. With two Bombs on the target, 14 to 18 is consistent with 2 a Bomb; only the label carries the stale 4.
- The CI-lint evidence path: corrected as above (indirect through `face_defects`), but the conclusion stands.
