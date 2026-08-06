> **MOVED 2026-08-06 — Clear the Stage, Track R-B resumption (R121 `Q20`, MOVE-WITH-RESOLVER; charter R119, rail 1).**
> Old path: `docs/sprint-understudy-p1-log-2026-08-04.md` — new path: `docs/archive/sprint-understudy-p1-log-2026-08-04.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Live citers repointed in the move commit; ledger and other
> frozen citations keep the old path on purpose (rail 1: ledger bytes are
> never rewritten) and resolve through the moved-path resolver table,
> `docs/registry/identifiers.md` §17. Per-file map:
> `review/stage-clear/rb-move-manifest.tsv`.

# Sprint log — Understudy P1: policy_v1 and the soak harness (2026-08-04)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Sprint: Understudy (bot playtest apparatus). Phase: **P1**. Worktree G4.
Brief: `docs/understudy-kickoff-brief.md`. Phase-0 measurement:
`docs/understudy-phase0-report.md`. The signed package this pass executes:
`docs/understudy-countersign-2026-08-04.md`. Rulings: `tier0/DECISIONS.md`
**R93–R97**.

Status: **policy_v1 SHIPPED, soak harness SHIPPED and P1 VALIDATED** — a clean
N=3 on current code, 2026-08-04 evening (R98; see "P1 VALIDATED" below).
Every number produced by either is a bot-limited floor and none of it is
balance evidence — see the Guardrail-7 section at the bottom, which is not a
formality here.

---

## What landed

| item | where |
|---|---|
| The signed package, verbatim | `docs/understudy-countersign-2026-08-04.md` |
| R93–R97 | `tier0/DECISIONS.md` |
| policy_v1, all seven revisions | `understudy/policy_v1.py`, `understudy/naming.py` |
| P1 soak harness | `understudy/soak.py` |
| Morning report generator | `understudy/report.py` |
| Telemetry schema (shared-surface-to-be) | `understudy/README.md` |
| Tests | `tier0/tests/test_understudy_policy_v1.py` (41), `tier0/tests/test_understudy_soak.py` (28) |

`understudy/policy_v0.py` was **not touched**. It is one arm of a published
measurement; editing it would retroactively move a quoted number, so policy_v1
is a new module and a test pins the counterfactual arm's Phase-0 behaviour.

Nothing in `tier0/`, `tier05/`, the drafter or any sheet was modified. The two
numbers policy_v1 needed (`BLOCK_MATTERS_FRACTION`,
`COMPANION_SHARE_FOR_GUEST_CAST`) live in `understudy/policy_v1.py`, are named
as bot-policy dials, are recorded per run in the log, and a test asserts the
first has not migrated into `tier0/constants.py`.

## policy_v1, revision by revision

| # | revision | status | the observation it closes |
|---|---|---|---|
| 1 | free expiring cards first | **DONE** — `_free_expiring` | the largest share of Phase-0's 34-of-47 turn-opener gap |
| 2 | block-panic gate + kill-vs-block | **DONE** — `_gated_ladder` | the floor-7 board: 4 Block bought against 39 incoming, five times running |
| 3 | map one ply deeper via `leads_to` | **DONE** — `_map` | all three path differences |
| 4 | the potion arm | **DONE** — `_potion_arm` | 26 unscored rows become scored |
| 5 | `next_fight` into the rest arm | **DONE** — `_rest` | the rest-vs-smith difference |
| 6 | in-combat choice overlay arm | **DONE** — `_choice_overlay` | Center Stage / Guest Cast, previously invisible to the whole measurement |
| 7 | resolved card NAMES per action | **DONE** — `understudy/naming.py` | **the P1 blocker.** A soak cannot be categorised by hand |

Three implementation notes worth keeping:

**#2 calls the sim's own scorer rather than re-typing it.** The revision is one
gate inserted between two rungs of `make_pilot`'s ladder; every valuation
around it (`_incoming_damage`, `_expected_damage`, `_block_value`,
`_raw_block`, `_score`, `_lethal_card`, and `potions._intent_damage` for "how
much incoming does this body own") is the sim's function, called. A re-typed
scorer would have made every future divergence unreadable, which is exactly
the failure M2 was written to rule out.

**#3's arithmetic is `tier05.route._plan`'s, not a new one.** `_plan` sums room
values along a path UNDISCOUNTED and re-plans from live state at every floor
with one value closure for the whole DAG. So the faithful truncation at depth
2 is `value(node) + max(value(child))` with the same closure. No discount
factor was invented, because inventing one would make this a different policy
rather than a shallower one. It is still a reduction and still says so: two
plies, not the act.

**#4 asks the sim's potion policy instead of running it.** `try_use_potions`
MUTATES a CombatState — it drinks, and the effect lands. Over the wire we need
the decision, not the effect, so the policy is run against the reconstruction
and the drink is read back out of the `player.potions` diff, with the aim
recovered from the same target-choosing helpers the sim just used. The ladder
stays the sim's; only the observation is ours.

**#5 needed a memo, and the memo is named.** policy_v0 is a pure function of
one wire state because a counterfactual has to be. policy_v1 drives, and two
revisions need something the wire does not carry when it is needed: the potion
arm fires once per combat ROUND, and the rest arm needs the kind of the node
after this one, which lives on the map screen and is gone by the time the rest
site loads. Both ride in an explicit `policy_v1.Memo` the driver owns, so the
hidden state is inspectable rather than living in module globals.

## The soak harness

`python -m understudy.soak --runs N [--report]`.

- **Seeds: read-back (R95).** The game generates, we record from
  `GET /api/v1/compendium` after embarking. No `seed` parameter is passed
  anywhere on the embark path. The chosen-seed Custom arm is **not built** —
  it is P1.5, gated at the first cross-build comparison. **UPDATE 2026-08-05
  (R104): P1.5 is no longer gated — it is NEXT in the Understudy queue.** Three
  independent demands land on the same bridge fork: chosen seeds (cross-build
  comparison), resource/meter visibility on the wire (R100/6b, before any
  Furina-meter claim is graded from the bot feed), and selector recording (the
  S7 C2 probe, R103(b)). One work item, three payoffs; the scope is unchanged.
- **Readiness: the `options` key on a menu state, never `GET /` (R97/5a).** A
  test asserts `bridge.health(` appears nowhere in the module.
- **Watchdog:** process liveness, `state_type: "overlay"`, a state FINGERPRINT
  (screen + floor + round + hp + energy + hand size + enemy HP pool + option
  count) unchanged across 12 consecutive posted actions, an action ceiling and
  a wall-clock ceiling. Every trip files a defect record with the seed, the
  floor, a trimmed state dump and the last twelve fingerprints.
- **Stop-and-surface:** two defects of the same **harness-side** shape halt the
  soak. `process_died`, `overlay_softlock` and `no_progress` are deliberately
  NOT on that list — those are the soak working, and halting on them would
  make the instrument stop on the very thing it exists to find.
- **Reversibility:** `steam_appid.txt`, the bridge deploy, the launch and the
  speed setting, each recorded in a ledger **before** the change lands and
  walked in reverse at teardown. Appendix A of the Phase-0 report is the
  checklist; the ledger for this pass is in "Reversibility" below.
- **The leftover run is abandoned, not negotiated with (R97/5b).**

Telemetry (damage by source, HP trajectory, incoming per turn, cards played,
turn count) goes to gitignored JSONL under `understudy/logs/soak/`. The schema
is documented in `understudy/README.md` and **flagged as a shared surface to
be**: Track B wants the same per-fight numbers out of the sim, and the moment
it reads this, renaming a key becomes a cross-session change.

## H4 — the validation soak

See "Validation soak (H4)" at the end of this document: 6 soaks, 10 harness
defects found and fixed, zero defects attributable to the GItS build.

---

## Routed findings

R93's routing note and R96's three observations. **No code in any of these
streams was touched.** Each note is filed in the consolidated backlog register
(`docs/backlog-2026-07-29.md`), which is where this repo's pilot, drafter and
ruling queues actually live — there is no separate per-stream queue file, and
grepping `docs/` for one confirms it. This section names the target stream for
each so the routing is legible from the sprint log too.

| # | finding | target stream | filed at |
|---|---|---|---|
| A | block-panic rung never asks whether the Block can matter, or whether a kill removes more | **pilot-improvement backlog** (`tier0/pilot/policy.py`) | `docs/backlog-2026-07-29.md` §1, "Python sim — P1 measurement defects" |
| B | `score_offer` returns exactly 0.0 for The Gallery Stirs | **DRAFTER 13** | `docs/backlog-2026-07-29.md` §1 (beside the 42-of-56 entry) and §3 item 6 |
| C | `score_offer` prices Vulnerable as a flat debuff | **`_static_power` repricing session** | `docs/backlog-2026-07-29.md` §1 |
| D | `_reaction_value` has no defensive term (Frozen priced as damage only) | **reactions-promotion session** | `docs/backlog-2026-07-29.md` §1 |

B carries an acceptance form, per R96: **DRAFTER 13 is not done while The
Gallery Stirs scores 0.0 at offer.** That is a regression fixture, not an
opinion, and it is written that way in the backlog.

---

## Guardrail-7, restated where the numbers are

Nothing this sprint produced is a balance finding. A soak number is a
**bot-limited floor**, and it stacks three limits, not one:

1. policy_v1 is a heuristic with declared reductions of its own — the map arm
   sees two plies of an act, and the draft arm is the sim's with three known
   scoring gaps that R96 routed rather than fixed.
2. The seeds are read-back, not chosen (R95). **No soak number is comparable
   to another build's soak number** until the Custom-screen arm exists.
3. A JSON-state agent cannot see the screen. No fun, legibility or readability
   claim can ever come from here.

Completion counts, floors reached, HP curves and damage tables from this
harness are defect-hunting instruments and telemetry. They do not grade a
character, they may not be quoted against a floor, and the report generator
prints no winrate at all — which is enforced by a test, not by discipline.

---

## Validation soak (H4)

This is harness validation, **not measurement**. Nothing in it is a balance
reading and the completion counts below are bot-limited floors in the sense
the Guardrail-7 section above defines. What the soak was run to answer is one
question: does the instrument work on real runs.

**It does, and it proved it the only way that counts — by catching its own
defects.** Six soaks were run over the pass; the harness filed a defect record
every time it failed, the stop-and-surface rule halted two of them, and the
game directory came back clean from every one, including the two that were
killed mid-run and the one where the game itself died.

## The final soak: 3 runs, 861 decisions, 19 fights

`understudy/logs/soak/soak-20260804-212539-*` (gitignored).

| run | seed | outcome | reached | fights | actions | wall |
|---|---|---|---|---|---|---|
| 1 | `JFH79C0S4U` | died | act 1, floor 14 | 5 | 218 | 166 s |
| 2 | `MXD9PKUWQ6` | defect | act 1, floor 17 (the boss) | 8 | 379 | 287 s |
| 3 | `HDGAR3K4ZL` | defect | act 1, floor 15 | 6 | 264 | 200 s |

All three seeds are **read-back** (R95): the game generated them, the harness
recorded them, and no policy stream ever saw one.

**Every one of the seven revisions fired in live play**, which is the check
that the offline tests cannot make:

| revision | decisions | |
|---|---|---|
| v1.2 gated ladder | 406 | plus 16 `v1.2-panic` (gate held) and **2 `v1.2-kill`** |
| v1.6 choice overlay | 127 | the screen policy_v0 could not answer at all |
| v1.1 free expiring first | 112 | |
| v1.3 map, two plies | 43 | |
| v1.5 rest with `next_fight` | 20 | |
| v1.4 potion arm | 1 | |
| v0 (draft / shop, delegated) | 29 | |
| mechanical (no decision) | 105 | |

The **kill-vs-block line fired twice in real fights** — the revision that
needed a live board to exercise at all, since the Phase-0 case that motivated
it was a single floor-7 observation.

Telemetry came out complete. An earlier soak's Act 1 boss fight recorded an
11-turn HP trajectory `[[1,22,0],[2,22,0],[3,14,3],[4,2,6],...,[11,1,12]]`
against an incoming curve peaking at 26, with damage attributed across six
named sources. That is the per-fight surface the brief asked for, from
policy-driven play rather than from AutoSlay.

## Defects filed, and what each was

Every defect this pass found was in **the harness**, not in the GItS build.
That is worth saying plainly: **three soaks' worth of policy-driven play
through a live GItS build produced no crash, no NRE and no unhandled overlay
attributable to the mod.\*** The instrument is what was broken, repeatedly, and
each break is now a red test.

> **\* Asterisk added 2026-08-04 (R99/2).** The headline held for the three
> soaks it describes and does not hold as a general claim. A later soak died
> inside a **Punch Off** event with `Signal
> '_internal_spine_objects_invalidated' is already connected` and our
> animation-router patch on the stack; [USER] ruled it **SUSPECTED-OURS** and
> routed it to the animation stream, seed `8B97LMCL2F` as the regression case
> (`docs/animation-sprint-2-log.md` § "ROUTED IN — the Punch Off crash";
> `docs/backlog-2026-07-29.md` §1). It is the apparatus's **first suspected
> mod-side catch** — which is the soak working, not the soak failing. The
> asterisk stays until the item is closed either way.

| # | shape | what it actually was | fixed |
|---|---|---|---|
| 1 | `embark_loop` | `menu_select KLEEMOD-FURINA` is idempotent; preferring the character over the confirm re-selects her forever | yes |
| 2 | `no_embark` | `confirm` returns "Embarking on run" and the next GET still reads `character_select` — a run generates over several frames | yes |
| 3 | `no_action` | a run opens on `state_type: "unknown"` at floor 0, which is a moment and not a screen | yes |
| 4 | `no_progress` (cycle) | grid screens TOGGLE on `select_card` and need a confirm; the shop's removal screen says `screen_type: "select"` and only its PROMPT says "Remove" | yes |
| 5 | `no_progress` (cycle) | the shop arm bought an untyped card-removal service it could not follow through on — and narrowing the shelf needed the index remapped | yes |
| 6 | `no_progress` (cycle) | the Enchant screen reports `can_confirm` with `preview_showing` false; multi-select screens need a DIFFERENT card each visit | yes |
| 7 | `no_progress` (cycle) | screen selection state outlived the visit, so the Spotlight overlay — which reopens every turn — exhausted its own options | yes |
| 8 | crash + skipped teardown | `ConnectionResetError` is an OSError, not a `URLError`, so it escaped `bridge._request` and aborted `teardown` at its first step | yes |
| 9 | `no_progress` (cycle) | the wire's `can_play` was never read, so a card the GAME blocked was chosen, rejected and chosen again | yes |
| 10 | `no_progress` (cycle) | with a full potion belt `claim_reward` returns ok and does nothing, and the mechanical walker re-claimed the same Fire Potion | yes |

Defects 9 and 10 are the two in the final soak's table. They are fixed and
carry regression tests, but they landed **after** that soak, so the next soak
is the first that runs without them.

## What the validation actually establishes

- **The watchdog works, and it was wrong once in a way worth keeping.** Its
  first form only caught a frozen frame; a real run bounced between two
  screens forever and never tripped it. A stall is a small CYCLE, and the bar
  is now at most two distinct fingerprints across a twelve-action window.
- **The stop-and-surface rule works and fires on the right things.** It halted
  two soaks on repeated harness-side failures. `process_died`,
  `overlay_softlock` and `no_progress` are deliberately excluded — those are
  the soak working, and halting on them would stop the instrument on exactly
  what it exists to find.
- **The morning report reads correctly on real data**: defects first with seed
  and floor, then outlier runs, then HP-by-floor, damage-by-source and
  cards-per-turn. It prints no winrate, and a test enforces that.
- **Reversibility held through every failure mode**, including two mid-run
  kills and one game crash. The final soak's ledger reads **REVERTED on all
  six entries**, and the captured `fast_mode` read `Fast` on every relaunch —
  proof that no killed session leaked `Instant` into `settings.save`.

## P1 VALIDATED — the clean N=3, 2026-08-04 evening

**Debt #2 is DISCHARGED and struck from the list below.** Recorded as **R98**
(`tier0/DECISIONS.md`). Log:
`understudy/logs/soak/soak-20260804-222105-*` (gitignored).

| run | seed | outcome | reached | fights | actions | wall |
|---|---|---|---|---|---|---|
| 1 | `8YD62HHZKP` | died | act 1, floor 14 | 7 | 232 | 175 s |
| 2 | `ERPW0H5LPZ` | died | act 1, floor 8 | 4 | 185 | 139 s |
| 3 | `WTG4G9B4GB` | died | act 1, floor 14 | 7 | 239 | 180 s |

**Three runs, 18 fights, 656 actions, ZERO defects filed.** The morning report
prints "None. No crash, no soft-lock, no unhandled overlay, no stalled state
across every run in this soak." The reversibility ledger reads **REVERTED on
all four entries**, and `_speed_on` captured `fast_mode: "Fast"` at setup —
which is the leak check, and it passed: the previous soak's speed entry died
NOT REVERTED (the bridge was gone), and `Instant` still did not reach
`settings.save`.

**It took two attempts, and the first one is the finding.** The first N=3 ran
clean for two runs and then filed `bridge_unreachable` at act 1 floor 6 — a
HARNESS-side kind, which is the instrument blaming its own wire. It was not
the wire.

### Defect 11 — a crashing process is not yet an exited process

`run()` already asked `session.alive()` before choosing between `process_died`
and `bridge_unreachable`. It asked in the same millisecond the socket reset,
and `Popen.poll()` had not yet reaped a process that was in the middle of
dying — so a build-side failure was filed under a harness-side kind. Two of
those halt a soak, which means this defect's real cost is a night that stops
on the very thing the soak exists to catch.

Fixed in `understudy/soak.py`: `Session.died(grace)` is the slow twin of
`alive()`, called only where a failure has already happened and the question is
who to blame; `alive()` stays instantaneous because the per-action watchdog is
on a hot path. Every defect record now also carries `proc_exit_code`. Two red
tests in `tier0/tests/test_understudy_soak.py` — one that a still-crashing
process reads as dead, one that a live game with a dead socket still reads as
the wire, because a grace period that swallowed the second would be a worse
bug than the first.

**Class: the traversal/wire layer**, the same family as the other ten and as
Phase-0's five adapter defects — a wrong assumption about how the wire behaves,
not a logic slip. It is expected-class, not new information.

### What the first attempt found in the BUILD, and did not fix

`godot.log` (`%APPDATA%/SlayTheSpire2/logs/`) ends mid-backtrace on a **Punch
Off event**: `PunchOff.PunchEachOther` → `CreatureCmd.TriggerAnim` →
`NCreature.SetAnimationTrigger` (our animation-router patch is on the stack) →
`CreatureAnimator.SetNextState`, and the Godot error is `Signal
'_internal_spine_objects_invalidated' is already connected to given callable`.
The event builds an `NCombatRoom` in `VisualOnly` mode against Furina's
convention `combat.tscn`.

**Filed, not diagnosed and not fixed.** It is one observation; the seed
(`8B97LMCL2F`) reproduces the floor, nothing in this pass's scope touches Vfx,
and it belongs to the animation stream. It is in the gate package and in the
backlog. What it is NOT is evidence against the harness — the soak caught a
game-side death, which is the instrument working.

The human feed (`PlayTelemetry.cs`) declines to open a fight record for any
room that is not a `CombatRoom`, so a Punch Off animation cannot enter Track
B's demand curve as a zero-incoming "fight" — that is the same event paying
for itself twice.

## Stop-and-surface

1. **The harness needed ten fixes to survive three runs, and all ten were
   wrong assumptions about the wire rather than logic slips.** Phase-0's
   five adapter defects were the same class (R97/5d: "any future adapter
   against this wire meets the same five"). This pass adds ten more to that
   map. The honest reading is that **the wire's screen protocol is the
   expensive half of this apparatus**, and a P1.5 or Phase-3 estimate that
   assumes the traversal layer is done will be wrong.
2. ~~**No soak has yet completed a clean N=3 with the current code.**~~
   **DISCHARGED 2026-08-04 evening — R98.** Deleted rather than rewritten,
   per the hand-back note; the evidence is "P1 VALIDATED" above. Kept as a
   struck line because a debt list that quietly loses rows is a debt list
   nobody trusts.
2b. **Two more traversal defects were filed the same evening and NOT fixed**
   (13: the bridge answering with no `state_type` mid-transition; 14: the wire
   timing out while the process stayed alive). Both are recorded in
   `docs/sprint-track-b-curves-log-2026-08-04.md`; both are the expected class.
   Note that the FINAL soak of that session was a second clean N=3 at HEAD, so
   R98's validation holds for the code as landed and not only for the commit
   that earned it.
   **ROUTING ACCEPTED 2026-08-04 (R99/3): the next traversal pass owns both.**
   Filed in the consolidated backlog register (`docs/backlog-2026-07-29.md` §1,
   "Understudy harness — traversal layer") with what reproduction exists — 13
   has a shape, 14 has one observation and none. They stay open and stay
   unfixed by design; this line is the accepted routing, not a promise to close
   them here.
3. **Runs die in Act 1.** Deepest reach across every soak was the Act 1 boss,
   beaten once. This is a **bot-limited floor and says nothing about
   difficulty** — but it does mean the current policy will not produce Act 2
   or Act 3 telemetry, so any Track B surface expecting late-act curves is not
   served by this harness yet.
