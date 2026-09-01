#!/usr/bin/env python3
"""EB-127: one id, one row, once ever. The uniqueness gate the registers never had.

WHY THIS EXISTS. `tools/lint_r_numbers.py` covers R- and D-numbers and nothing
else. The `M`-series in `QUEUE.md`, the `EB`-series in `BACKLOG.md` and every
other series were unchecked: nothing read them and nothing asserted
uniqueness. Two collisions reached review inside two weeks — `EB-119`/`EB-120`,
and `M38` minted twice on 2026-08-24 off the same base — and both were caught
by a human, neither by the suite. A collision that reaches `main` is worse than
a duplicate row: the two branches' provenance chains, rulings and
cross-references silently point at each other's item.

WHAT IS CHECKED, AND WHY EXACTLY THIS.

  1. within `QUEUE.md`, no two rows define the same id;
  2. within `BACKLOG.md`, no two rows define the same id;
  3. no id is defined as a row in BOTH registers at once;
  4. every defined id sits at or below its series' frozen CEILING — a number
     above it is a mint whose ceiling bump never landed;
  5. every defined id at or below the ceiling is a live entry in the manifest
     below — anything else is a RETIRED number being re-minted;
  6. every manifest entry still defines a row — an entry that outlives its row
     is STALE and fails, which is what keeps the manifest from rotting into
     cover for the next real collision;
  7. no row defines an id in a series another lint owns (`R`, `D`), which
     would land it outside both guards.

A row DEFINES an id when the id sits in the table's first column. Everything
else — a citation in another row's prose, a pointer from `STATE.md`, a
provenance chain naming a closed item — is a REFERENCE and is deliberately out
of scope AS A DEFINITION. References are how these documents work: `EB-136`
cites `R208`, `QUEUE` rows point at `BACKLOG` rows by id, and a lint that
treated any mention as a definition would fire on every healthy
cross-reference in the tree. The row's own words: *citations are fine*.

WHERE THE MANIFEST LIVES, AND WHY HERE. `EB-127` named three candidate homes
for the record of every id ever ISSUED — a committed ledger under `docs/`, a
derivation from git tags, or a per-series high-water mark — and refused to
settle it. The answer taken is the third, **as constants in this file**:

  * **Git derivation is not available.** CI checks out a depth-1 clone with no
    tags fetched (CLAUDE.md's history-retrieval section exists precisely
    because history is NOT in HEAD). A lint that needs `git log` to decide
    whether a number was ever issued cannot run in the lane that matters.
  * **`lint_r_numbers.py` set the precedent and it has held.** `R_CEILING` and
    `D_CEILING` are hand-bumped integers in the tool that reads them, for the
    same reason, and two branches taking "the next number" collide on that
    constant instead of silently sharing it. A second mechanism for a second
    pair of series would be a second thing to keep true.
  * **A `docs/` ledger would be a fourth register to maintain by hand** with
    nothing enforcing it, and CLAUDE.md's read-order budget is the thing this
    repo defends hardest. The manifest is machine data, not prose; it belongs
    next to the code that reads it.
  * **Rule 6 makes the whole thing self-enforcing.** Close a row, drop its id
    from `OPEN_IDS` in the same commit, and that number is permanently
    un-re-mintable — the retirement is recorded by the act of retiring. No
    separate discipline to remember, because forgetting fails the lint.

HOW THE CEILINGS WERE FIRST SET. Not from the highest LIVE row — closed items
leave HEAD, so that number understates the truth by exactly the ids this rule
exists to protect. Each ceiling is the highest id of its series **defined or
cited anywhere under `docs/current/`**, scanned on 2026-08-25: a retired id
survives in HEAD as a citation long after its row is gone (`EB-131` and
`EB-133` are cited by live rows and define none). That is a floor on "ever
issued", not a proof of one — but it only ever moves forward, and every mint
above it must record itself here, so the floor becomes exact from this commit
on.

Usage:
    python tools/lint_register_ids.py
    python tools/lint_register_ids.py --self-test   # prove it bites

Exit 1 with findings on stdout.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# The two ROW registers. Deliberately not every markdown table in the tree:
# `STATE.md`'s tables are stamps and roster rows, `EXPERIMENTS.md`'s are
# registrations — neither mints ids into these series, and scanning them would
# turn a stamp label into a "duplicate id".
REGISTERS = ("docs/current/QUEUE.md", "docs/current/BACKLOG.md")

# One id as the registers spell it: an uppercase series, then hyphen-joined
# parts. Covers `EB-71`, `M14`, `S4-G6`, `CC-G1`, `OT-1` and `SKIP-10.9`.
ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9.]+)*$")

# The compound spelling one row uses for a merged item: `EB-33/34/35` is three
# ids in one cell, not an id containing slashes. Expanded rather than special-
# cased, so a second merged row cannot quietly hide a duplicate inside itself.
COMPOUND = re.compile(r"^(?P<head>.*?)(?P<num>[0-9.]+)(?P<rest>(?:/[0-9.]+)+)$")

# A cell may carry several ids joined by ` / ` (QUEUE's S4-G12 / CC-G1 / CC-G2
# row). Each is a definition; the row is shared, the ids are not.
BACKTICKED = re.compile(r"`([^`]+)`")

# An INTEGER id: a series prefix and a number, hyphen optional (`EB-137`,
# `M26`). `S4-G6`, `CC-G1` and `SKIP-10.9` deliberately do not match — their
# tails are not integers, so they get the explicit-set treatment below.
SERIES_NUM = re.compile(r"^(?P<series>[A-Z][A-Z0-9]*?)-?(?P<num>\d+)$")


# --- THE ISSUED-ID MANIFEST ------------------------------------------------
# Hand-maintained, deliberately. Nothing derives these at runtime: a constant
# that recomputes itself from the thing it is checking guards nothing.

# Highest id ever issued in each integer series minted by these registers.
# Bump in the SAME commit as the row that mints past it. R and D are NOT here
# — `tools/lint_r_numbers.py` owns those two series and one namespace must not
# have two ceilings; rule 7 below refuses a row that tries to define one.
CEILINGS: dict[str, int] = {
    # EB-199/EB-200 minted 2026-08-29 by the R220 slate: the roster-wide Burst
    # retirement, in two rows. 199 is the retirement itself -- engine fields,
    # ops, the requires gate, eight constants, three sheets' burst_max and the
    # ~30 test files, gated on all three folds landing. 200 is its C# arm --
    # the three pools, the keyword loc id and its consumer sweep, the
    # retired-display registry and the GaugeBridge re-point. The Burst packet
    # reserved 198/199 for these two; 198 was taken by the blind run first, so
    # both shifted up one and the packet carries a pointer saying so.
    # EB-198 minted 2026-08-29 by the KURAGEMEM001 blind run: the tester read
    # the memory strip as inconsistent twice, undiagnosed on purpose.
    # EB-202/EB-203 minted 2026-08-29 by the KLEESPARK-R1 relayed review:
    # a slot whose threshold the board set could not reach, and a form
    # whose play line is never checked for a target before it is graded.
    # EB-210 minted 2026-08-29 by the two-lane repair, and CLOSED in the
    # minting commit: `bridge.current_seed` is a FILE read on the mod's
    # side, and the path resolved through
    # `Environment.GetFolderPath(ApplicationData)`, which ignores the
    # `APPDATA` that separates two lanes' user trees -- so both lanes read
    # lane 0's `current_run.save` and a round filed `seed_not_honoured`
    # against a game that had honoured its seed. Fixed in
    # `McpMod.Compendium.cs` (globalize `user://`; the env var first) with
    # `bridge.LaneCrossed` as the harness-side refusal. Five locks, each
    # seen to FAIL first.
    # EB-209 CLOSED 2026-08-29 in the same commit: the stopping rule reads
    # DECIDING grades in the shadow chair, and a refused deciding form is
    # no grade. It LEFT OPEN_IDS there. EB-208 stays open (its fix is a
    # pick).
    # EB-208/EB-209 minted 2026-08-29 by KLEESPARK-R2: a staged board
    # cannot REQUIRE an enemy count, so a slot that needs one can pass
    # every check and still not be posed; and in the shadow chair R221 B's
    # stopping rule reads shadow grades, which decide nothing.
    # EB-211/EB-212 minted 2026-08-29 by the KLEESPARK-R2 relayed review:
    # R223's battery has two soft categories -- `costs` only FAILS a positive
    # misread, so silence passes it, and `intent` is scored on self-report.
    # EB-213..EB-219 minted 2026-08-30 by R224, the sitting slate landed whole
    # -- the engineering the countersign creates, seven rows, all OPEN:
    # 213 the prototype surface has no upgrade channel, so the substituted
    # Kurage's Oath cannot be upgraded at a campfire; 214 print Rule 1 as the
    # Muster keyword and re-run the memory gate on KURAGEMEM002 (M54);
    # 215 the prototype surface's per-row `description:` channel, emitted by
    # gen_prototype_cards.py, and the loc merge deleted (M57); 216 a per-turn
    # wire snapshot in every future blind-run record (M56, published grades
    # standing under R101b); 217 delete KURAGE_MEMORY_KEYWORD_NEEDS_SUMMON
    # and its branch (M50 pick 4); 218 the three hybrid spenders migrated to
    # Spark-only behind SPARK_ALT_COST_ENABLED (slate item 16); 219 Prune
    # re-authored under the countersigned LAW:145, her Spark grant becoming a
    # declared Klee-engine response (slate item 31, which R224's own LAW text
    # opened). The Bake-Kurage retirement and the five K1/K2/KO1/KO1a/KO2
    # shapes were NOT minted -- they attach to the existing Burst-fold rows
    # EB-199/EB-200, and EB-208 gained its ruled fix shape in place, its (a)
    # half BUILT and merged as #197. M55's pile-view line folds into EB-214
    # rather than minting. M47/M49/M50/M52/M54/M55/M56/M57/M59/M60/M64 LEFT
    # OPEN_IDS in the same commit as their rows.
    # EB-220 minted 2026-08-30 by [USER]'s word on EB-182's build: Encore- and
    # Charge-priced modes and cards get the cost badge the Spark price has.
    # EB-224/EB-225 minted 2026-08-30 by R225, the open-items slate: 224 is
    # Bag of Tricks, admitted now that the top-level-cost clause reads top
    # level OR mode head, built on EB-182's mode-price machinery and
    # sequenced after EB-205's read; 225 is the prototype-patch scope lint
    # that buys the single PROTOTYPE_CARDS switch its guard -- every
    # prototype Harmony patch character-scoped and seat-guarded. M65 and M66
    # LEFT OPEN_IDS in the same commit as their rows.
    # EB-221/EB-222 minted 2026-08-30 by the first whole-fight soak of the
    # `+proto` package, and both CLOSED in the minting commit -- two
    # lifecycle throws, each of which ended every whole fight at the second
    # combat since `0.2.1353+proto`. 221: `KurageMemoryCard`'s `Deactivate`
    # postfix called `LocalContext.GetMe` on a combat with no local seat --
    # the next room's, still being built -- and that API throws rather than
    # answering null, so the room never finished readying and the fight was
    # never set up. Fixed in d217b4f (#207): a `TryGetMe` guard for all three
    # callers and a `TrackedDisplayBridge.Spawn` degrade, locked by
    # `KurageMemorySeatGuardTests`. 222: `MeterCostBadge` (EB-220) held the
    # glyph in a process-lifetime static cache; the room preloader freed
    # combat 1's `CompressedTexture2D` with the room, combat 2's first
    # `UpdateStarCostVisuals` handed the freed object to
    # `TextureRect.SetTexture`, and the `ObjectDisposedException` escaped
    # `Paint` into `CardPileCmd.Draw` and killed the turn loop. Fixed in
    # fa1fffe: the glyph is resolved from `ResourceLoader` per paint, checked
    # with `GodotObject.IsInstanceValid`, and a freed resource degrades to no
    # glyph with one `Log.Warn`; three structural locks in
    # `MeterCostBadgeTests`. PROOF, on `0.2.1608+proto.dirty`:
    # `python -m understudy.soak --runs 1 --character KLEEMOD-KLEE
    # --max-fights 3` -> `bounded  seed=None  actions=46  fights=3
    # defects=0`. The same command returned `fights=1` before 221 and
    # `fights=2 defects=1` on 221 alone.
    # EB-223 minted 2026-08-30 by the relayed open-items review, fact-checked:
    # R222 (a)'s whole-fight read of the strict Rare Power
    # `proto_true_spark_knight` is owed WORK, not an open decision -- the
    # packet's "stays [USER]'s at 11.7 pick 3" is struck as erratum 2 and the
    # read is filed in BACKLOG behind 16.11 pick 1.
    # EB-226 minted 2026-08-30 by the overnight-harness sitting and CLOSED in
    # the minting commit. Two overnight runs died to the power plan rather
    # than to anything this repo owns: the System log records `Kernel-Power
    # 42 -- "entering sleep -- Sleep Reason: System Idle"` at 2026-08-29
    # 07:05:40, resumed 11:21:48 on a mouse movement -- a 4 h 16 m hole
    # through the middle of a live funnel, the game suspended mid-fight --
    # and again at 2026-08-30 00:56:17. The AC standby timeout was five
    # hours and [USER] has since set it to never, but a power plan is machine
    # state nothing in this tree can see, survives no reinstall and no plan
    # reset, so the harness now asks for what it needs itself.
    # `understudy/keepawake.py` holds `ES_CONTINUOUS | ES_SYSTEM_REQUIRED`
    # for exactly as long as a `soak.Session` holds the game (`setup` ->
    # `teardown`), refcounted so two lanes share one hold, and deliberately
    # WITHOUT `ES_DISPLAY_REQUIRED` -- the run needs the CPU, not the
    # monitor. The flags are per-THREAD, and `Session.setup` and `teardown`
    # are reached from different lane workers under a two-lane round, so the
    # request lives on its own thread whose only job is to stay alive; set
    # inline it would have been released by the OS when the worker exited,
    # which looks correct in a diff and holds nothing. Non-Windows or a
    # missing kernel32 is one logged line and a no-op.
    # `tier0/tests/test_understudy_keepawake.py` asserts the flag sequence a
    # fake setter records, that both calls land on one non-caller thread,
    # that the context manager releases when its body raises, and the
    # two-holder case. Confirm live with `powercfg /requests` (elevated):
    # the harness's `python.exe` under `SYSTEM:`.
    # EB-227 minted 2026-08-30 by the same sitting and CLOSED in its minting
    # commit: the Codex seat judged its own budget by hand. The standing rule
    # -- three calls per graded turn (R217, `M64`'s split) -- is written in
    # OPERATIONS and obeyed by a person, which is fine for a sitting somebody
    # is watching and useless overnight, where the failure mode is the seat
    # burning the week's window at 02:00 and every round after it returning
    # `codex_failed exit 1` with no explanation. `understudy/codex_usage.py`
    # reads the meter out of the rate-limit line Codex itself writes into its
    # newest session rollout (`$CODEX_HOME/sessions/YYYY/MM/DD/rollout-*.jsonl`,
    # `payload.rate_limits`, primary = 5 h, secondary = the week); nothing
    # here asks OpenAI anything, so THE READ IS AS-OF THE LAST CALL, and a
    # window whose `resets_at` has passed is counted 0% used rather than
    # billed for a window that no longer exists. `python -m
    # understudy.codex_usage` prints one line. `seat grade` and `seat review`
    # both probe before every `codex exec` and refuse -- in each role's own
    # refusal shape, never an exception that would kill a round -- at or past
    # `CODEX_PRIMARY_STOP_PERCENT` (85) or `CODEX_WEEKLY_STOP_PERCENT` (50),
    # env-overridable via `GITS_CODEX_PRIMARY_STOP` / `GITS_CODEX_WEEKLY_STOP`;
    # the two lines are asymmetric because the five-hour window refills in
    # five hours and the week does not. The percentages land in the call's own
    # record (`seat.json`, `<out>.usage.json`) so per-call cost is learnable
    # overnight. A missing rollout logs and PROCEEDS -- a file that is not
    # there must not be able to stop a round. Live read at the time of the
    # commit: `codex: 5h 3% (resets 04:40 EDT) - week 11% (resets Sep 05
    # 17:58)`. Locked by `tier0/tests/test_understudy_codex_usage.py`
    # (fresh / rolled-over / missing fixtures, both stop lines, both roles'
    # refusal branches with `seat._run` monkeypatched, and the under-the-line
    # case that must still reach codex). The three-calls rule is UNTOUCHED.
    # EB-228 minted 2026-08-30 by the Kokomi slice-2 round-2 job, which was
    # scheduled to RUN and stopped at the door instead: the packet's own §9
    # PICK 2 held round-2 staging on the Charge accrual rule, that pick had
    # never been minted, and so STATE -- which reads the register -- said no
    # prototype-slice row was open. The row is the lint that would have caught
    # it: a hold verb in a `review/active/` packet naming no OPEN QUEUE id.
    # The pick itself is M67, minted in the same commit.
    # EB-230/231/232 minted 2026-08-30 by the night's runs, three defects that
    # each surfaced where nothing was looking for them. 230 the `KLEESPARK-W3`
    # record's §18.9 item 1, promoted from defect CANDIDATE to a row now that
    # the mechanism is read off the generated file: a face rendering a live
    # modifier its body ignores. 231 the same session's teardown, which wrote
    # REVERTED over a process it had not killed and then failed the bridge
    # removal on the live PID twice. 232 the lane test, whose flake this
    # integration reproduced and then diagnosed off the quoted save path --
    # it is a cross-SESSION leak, and the standing "rerun the file alone"
    # workaround is the reason nobody had looked.
    # EB-241 minted 2026-08-30 by R231 A3: `Card.is_junk` is rarity-only,
    # and the fix is scheduled AT the Kokomi fold because it moves shipped
    # numbers and rides the fold's already-required re-baseline.
    # EB-242 minted 2026-08-30 by the X9READ-S1 graded read: the
    # reads-per-turn instrument tallies the pilot's valuation calls as reads
    # (packet §9.4), which §2 declares it does not do.
    # EB-243 minted 2026-08-30 by the live-acceptance window: BT3's staged
    # boards declare a relic the wire does not carry on their pinned seed
    # (renumbered from EB-242 at the fold: two parallel windows both took
    # the next free id; X9READ-S1's mint keeps 242).
    # EB-244 minted 2026-08-30 by the KLEESPARK-BT3 round: a staged board can
    # declare an enemy INTENT the wire does not carry, because EB-240 expects:
    # has a relics leg and an hp leg and no intent leg. Both BT3 boards
    # declared a telegraphed attack for 16 and the wire carried a Debuff on
    # t01 and an attack for 12 on t02.
    # EB-245/246 minted 2026-08-30 by the KLEESPARK-W5 whole fight: the
    # phantom fight record a card_select overlay triggers mid-play, and
    # the BBCode a printed option name carries into the blind render.
    # EB-247/248 minted 2026-08-30 by KURAGECAD-W1: the jellyfish's own
    # text disagrees with the pulse it delivers, and the memory's price
    # cannot be derived from the printed face on a discounted entry.
    # EB-249/250/251 minted 2026-08-30 by the register-reconcile pass, which
    # is where R234 section 5.3 and the companion packet's section 2.6 both
    # said their engineering would mint -- neither document filed a row, on
    # purpose, because the id space is not theirs to spend: the two-halved
    # companion-distinctness gap, the downward-only rarity fallback the
    # colorless anchor made reachable, and the two Klee Personal Companion
    # card drafts the ruling owes.
    # EB-252 minted 2026-08-30 by the role-tempo staleness find: the
    # baseline docs predate the 0.111.0 port, and a clean regen moves
    # floors onto Klee -- so the re-baseline ships disclosed, filed here.
    # EB-253 minted 2026-08-31 by the EB-242 fix: note_fanfare_read has
    # the same valuation exposure, left for its own disclosed commit.
    # EB-254..EB-258 minted 2026-08-31 by the triage of [USER]'s manual solo
    # Kokomi playtest (`review/ruled/kokomi-playtest-triage-2026-08-31.md`),
    # five rows: 254 the Muster keyword printed its -1 with no
    # duration while four sibling faces print `this turn` (CLOSED
    # 2026-08-31); 255 the unlinted
    # "every starter card is basic" invariant, false on `an_invitation`
    # (SHIPPED) and `to_the_front` (flagged), contaminating `_committed_share`;
    # 256 an unwinnable-and-unloseable stall is reachable and no instrument
    # can see it; 257 a dev `+proto` package survives a window teardown into
    # an unattended manual session with no signal; 258 a second un-golded
    # resource keyword on a face (SYS-9), plus the comment saying there was
    # only one (CLOSED 2026-08-31 -- it was the twenty-fourth, not the
    # second). (253 was minted in parallel by the EB-242 fix the same day;
    # both landed at the fold, so the numbering closes with no gap.)
    "EB": 258,   # EB-239/240 minted 2026-08-30 by KLEESPARK-BT2 (Klee Sparks
                 # packet section 24). 239 is the forecast's FORM half --
                 # `EB-236` item (d) shipped the packet and the falsifier and
                 # not the field, so the reply schema both seats answer
                 # through had nowhere to put a forecast and all six of BT2's
                 # forms were refused `forecast_missing`. It was CLOSED in
                 # the commit that minted it and never entered OPEN_IDS.
                 # 240 is the staged board's blind spot for the run's relics:
                 # every BT2 board asserted "the run carries Klee's starting
                 # relic and no other" while the page printed two.
                 # EB-236/237/238 minted 2026-08-30 by KLEESPARK-BT1 (Klee
                 # Sparks packet section 22): the board-design trap that drew
                 # `intent_insensitive` refusals from 7 of 8 forms, slot_plan's
                 # blindness to a mode-head Spark price, and the blind page
                 # printing no relics -- which is why the priced mode's
                 # self-refund off Pounding Surprise was invisible to every
                 # form and uncontrolled by the registration.
                 # EB-235 minted 2026-08-30 by R228 pick 1: the successor to
                 # the closed EB-223, carrying R222 (a)'s whole-fight read of
                 # the strict Rare Power, which KLEESPARK-W4 left UNREACHED
                 # because the Power was drawn on seven pages and played on
                 # none. Its unit is an uptake slot, not W4 repeated.
                 # EB-233/EB-234 minted 2026-08-30 by the post-merge review,
                 # fact-checked against main 21a078c4. 233 is KLEESPARK-S1's
                 # S3 miss, which both the registration and the result route
                 # to BACKLOG as an instrument row and which reached none:
                 # the drafter does not TAKE the migrated non-damage twins,
                 # so the bank number S2 quotes is an OFFER number. 234 is
                 # the memory's cadence over a DEVELOPED deck, deferred in
                 # the kurage packet at :2225 and registered nowhere.
                 # EB-229 minted 2026-08-30 by the `KURAGEMEM002` rerun: the
                 # blind-play reply schema collects no forecast, so three
                 # display slots graded UNREACHED on a display that was
                 # demonstrably on the page and correct.
                 # EB-207 minted 2026-08-29 by the Klee Sparks whole-fight run
                 # (klee-sparks-2026-08-29.md 12.8 item 2): the blind page
                 # printed Kokomi's Bake-Kurage memory block on a KLEE run and
                 # told the tester it had played no card.
                 # EB-206 minted 2026-08-29 by the two-instance funnel build:
                 # two game processes from one install, per-process APPDATA
                 # and a per-process bridge port.
                 # EB-205 minted 2026-08-29 by R222 pick 6(d): the Klee Spark
                 # arm became DRAFTABLE (the pool seam) and has never been
                 # measured drafted. 202-204 are other branches of the same
                 # sitting; this branch took the next free number above them.
                 # EB-201 minted 2026-08-29 by EB-198's live acceptance: the
                 # pile view's affordability rings never paint, on a hook that
                 # binds without error and a pile that demonstrably opens.
                 # EB-196/197 minted 2026-08-29 by the Gate B diagnosis. 196:
                 # the C# memory could never hold an entry -- the per-fight
                 # clear sat in the subscription delegate, which the combat
                 # re-invokes on EVERY hook broadcast, so both entry rules
                 # filed and were wiped between hooks (and the same line wiped
                 # the pulse key, which is the strip's second wrong sentence).
                 # 197: the Bake-Kurage buff printed "Lasts 1 more turn" under
                 # a flag that never ticks it down. Both FIXED and CLOSED in
                 # the minting commit, locks seen to FAIL first.
                 # EB-195 minted 2026-08-29: the twelve-arm re-baseline of
                 # the Furina and Kokomi arms at RT12/D18/P11/C20 is OWED
                 # after R219 F moved their HP (Kokomi 80, Furina 78, #156).
                 # Under R68 every measured table quoting their rows is
                 # STALE until it runs. OPEN.
                 # EB-194 minted 2026-08-29 by the +proto deploy that was
                 # meant to run the Kurage-memory pre-tester gates: the dev
                 # build could not start a run for ANY character. sec.12.6
                 # item 14's loc merge called PrototypeCards.For from a
                 # Harmony postfix on LocManager.Initialize, forcing the
                 # eager PrototypeRoster initializer while ModelDb was still
                 # empty; the throwing static ctor poisoned the type for the
                 # process and every later caller rethrew. FIXED and CLOSED
                 # in the minting commit -- both locks were seen to FAIL
                 # against the pre-fix build first.
                 # EB-192/193 minted 2026-08-29 by the Klee Sparks research
                 # pass, both confirmed defects found decompiling the pinned
                 # 0.111.0 build. EB-192: the `regent_forge` canon package
                 # was a regex artifact fusing Regent's Stars with the
                 # unrelated Forge card, so the anchor `klee/spark` was
                 # measured against about half a different mechanic. CLOSED
                 # 2026-08-30 by R231 A8 -- rebuilt as `regent_stars` from
                 # the census, both anchors re-baselined. EB-193: the base-game pool
                 # extractor requires a decimal `...m` literal and so drops
                 # every int-typed var, leaving `game_ref/regent.json` with
                 # no Star amounts at all. OPEN.
                 # EB-188/189/190 minted 2026-08-29 by the process-review
                 # pass (EB-188: the prototype-arm door for whole-fight
                 # blind play -- BUILT, and CLOSED 2026-08-29 on its live
                 # acceptance: sealed session 20260829-181718 on
                 # 0.2.1353+proto, seed 71D8JS1VSKRN, 120 actions, the
                 # record naming arms_granted, and the granted arm drawn
                 # and played in fights 4 and 6. RETIRED; EB-189: the QA
                 # pilot's ~59k lines under `review/qa/` want compacting;
                 # EB-190: recorded authorship on the prototype surface,
                 # CLOSED the same day). EB-191 minted by the Klee slice 1
                 # round-2 funnel run: a replay's run seed reads back None
                 # on 7 of 12 launches (`seed_not_honoured`); an identical
                 # retry always works. OPEN. (It was minted as EB-188 in
                 # parallel and renumbered at integration.)
                 # EB-185/186/187 minted 2026-08-29 by the Klee slice 1
                 # funnel run. EB-186 was NOT A DEFECT and its row is gone:
                 # [USER] ruled 2026-08-29 that every Attack rendering
                 # cost 0 at a bank of 3 is the intended mechanic -- at the
                 # moment the hand is read every Attack IS free, whichever
                 # is played first takes the discount, and the rest snap
                 # back to printed cost. Round 1's ten refused lines were
                 # readers failing to chain the keyword's second sentence,
                 # not a display or D4 fault. A false positive goes
                 # nowhere permanent (CLAUDE.md audit triage), so the id is
                 # retired here and stays un-re-mintable.
                 # EB-185: the observed closeness board maps no Spark, so
                 # every observed reading of a Klee turn scores a bank of
                 # zero. CLOSED 2026-08-29 -- the Spark status now crosses
                 # onto `Player.sparks` and declared and observed agree on
                 # all six slice 1 boards. RETIRED.
                 # EB-187: the Burst assumption line double-counts the
                 # Skill tag against the rider the face already prints,
                 # and it corrupted a grade. CLOSED 2026-08-29 -- both
                 # halves reworded and `staged_turn check` now refuses an
                 # assumption claiming a gain the face prints. RETIRED.
                 # EB-184 minted 2026-08-29 by Kokomi slice 1 round 4: a
                 # `choose_one` card typed as an Attack demands a target
                 # even on a mode that attacks nothing, so a blind
                 # grader's Block-mode line cannot be replayed. OPEN.
                 # EB-182/183 minted 2026-08-29 by the Kokomi slice 2 funnel run.
                 # 182 LEFT OPEN_IDS 2026-08-30: built and merged (#200);
                 # the seat's re-ask of Bag of Tricks is EB-220's sibling, not a row.
                 # EB-182: the choose-a-card screen has no per-option
                 # playability, proven off the 0.111.0 decompile, so a
                 # priced "Choose one" mode is offered on a short bank
                 # and simply does nothing. OPEN.
                 # EB-183: R216 D's per-companion half -- recruits from a
                 # paid order paying no Charge on Exhaust -- is a funnel
                 # property, not an effect list, and is owed as its own
                 # matched pair. OPEN.
                 # EB-178/179/180 minted 2026-08-29 from run B6 and the module-size note
                 # EB-181 minted 2026-08-29 by EB-179's close: the
                 # vendored bridge reports no enchantment on a card
                 # face and no maximum on a resource meter, and the
                 # game's own screen shows both. OPEN.
                 # EB-179 CLOSED 2026-08-29: powers now print the
                 # `type` the wire always carried, and the page states
                 # out loud what the feed does not carry -- no power
                 # expiry, no meter maximum or spend rule, and no
                 # enchantment behind two cards printing one name.
                 # EB-178 CLOSED 2026-08-29: the frame after a kill is a
                 # combat screen with NO `battle` block at all, read live
                 # across a victory (+0 ms `monster` and no battle key,
                 # +250 ms `rewards`). `blindplay.transient` names it and
                 # rides it out; it is never drawn as `round 0`.   # EB-177 minted 2026-08-29 by run B6: two cards with the
                 # same printed title that differ by anything but upgrade
                 # state are BOTH unplayable -- a Sharp-enchanted copy of
                 # `Water's Edge` beside a plain one, where the bare title
                 # is ambiguous and neither `(upgraded)` nor
                 # `(not upgraded)` separates them. The session died on the
                 # refusal limit and the tester named it unprompted.
                 # CLOSED 2026-08-29: repeats are numbered in printed
                 # order, the way the map numbers a fork's paths.
                 # EB-176 minted AND CLOSED 2026-08-29 by the same acceptance:
                 # a live `hand_select` renders as `card_select`, only the
                 # WIRE's screen name was exempt from the snake_case rule, and
                 # the tool's own name for the screen -- in the tool's own
                 # observation -- tripped the blindness assertion and stopped
                 # a session that had leaked nothing. Fixed in the same
                 # commit, so the row never existed.
                 # EB-175 minted 2026-08-29 by the same acceptance and CLOSED
                 # 2026-08-29: `end turn` had to be said twice, four times in
                 # one session. The wire read either side of the post settled
                 # it -- the bridge's `end_turn` is asynchronous, and a GET
                 # 55 ms later reads the round unchanged, the hand discarded
                 # to zero and `is_play_phase` FALSE. `blindplay.transient`
                 # now names that frame a transition and rides it out.
                 # EB-174 minted 2026-08-29 and CLOSED 2026-08-29: the sealed
                 # blind-play record could not name the build it was taken on
                 # -- the bridge's health payload carries the VENDORED
                 # bridge's version and never ours, and `build_version`
                 # correctly refused to invent one. Both builds are now read
                 # OFF DISK and labelled: the deployed
                 # `mods\klee\manifest.json` and the game's own
                 # `release_info.json`.
                 # EB-173 minted AND CLOSED 2026-08-29 by the EB-167 live
                 # acceptance: `_fold` erased the `+` the game prints on an
                 # upgraded title, so a hand holding a base and an upgraded
                 # copy made BOTH unplayable, and the `(upgraded)` escape the
                 # refusal advertised was implemented nowhere. Run B died on
                 # it at the refusal limit. Fixed in the same commit, so the
                 # row never existed; the ceiling stays at the issued number.
                 # EB-172 minted 2026-08-28 by R218 C: a gitignored backup of
                 # the four PINNED managed assemblies in the OneDrive vault
                 # beside game_ref, plus a local.props switch that builds
                 # against it. A Steam update may stop a live run; it must not
                 # be able to stop the build.
                 # EB-171 minted 2026-08-28 by the EB-167/168 live acceptance,
                 # which could not run: the machine's game moved to v0.111.0
                 # on the `public-beta` branch and neither the vendored bridge
                 # nor the roster mod compiles against it any more. The PORT is
                 # engineering; whether to port at all is M46.
                 # EB-169/170 minted 2026-08-28 by the Kokomi slice-1 round-3
                 # sitting, both under R213/R216 authority and neither a
                 # design call: a funnel preflight that refuses a packet
                 # holding a card with an OPEN face/runtime defect (round 2
                 # staged one on all eleven boards), and the replayer's
                 # inability to answer a modal prompt, which left three of
                 # round 3's eleven replays untested.
                 # EB-166/167/168 minted by R217 (2026-08-28): the automation
                 # the design course-correction authorized, in order -- the
                 # independent-model seat (Codex CLI on [USER]'s subscription),
                 # the design-blind any-screen render over the existing
                 # bridge, and the orchestrated Act-1 tester. A4 and A6 are
                 # deliberately NOT minted; A1-extended and A5 are DEFERRED.
                 # EB-164/165 minted by R216 (2026-08-27): the two engineering
                 # findings the first end-to-end blind-QA run turned up -- a
                 # generated face that double-states a scaling its printed
                 # number already includes, and the missing bridge dev door
                 # that would let a staged turn post an EXACT hand.
                 # EB-147..163 minted at the morning sitting 2026-08-27. The
                 # block the dispatch-3 charter had reserved was RELEASED by
                 # [USER] — "is this just procedural (what id to use)? If so
                 # then whichever is fine." — so R213's authorized engineering
                 # (the quarantined prototype surface, the Companion audit, the
                 # blind QA-agent funnel, the three playtest defects) and the
                 # dispatch-3 confirmed defects mint CONSECUTIVELY from 147.
                 # No M id was minted with them: nothing there registers a
                 # measurement, so the M ceiling deliberately does not move.
                 # EB-146 minted 2026-08-26 (scenario harness first run + set_power); EB-143/144/145 minted 2026-08-26 for the three Phase-4
                 # pilot/scorer repairs the C19/D17/P10 standing read named as
                 # its diagnostic caveats, and CLOSED the same day in the one
                 # P11 window (with EB-129); the ceiling stays at the issued
                 # number.
                 # EB-142 minted AND CLOSED for the 0.2-1028 attended-playtest
                 # defect (a branch-nested aiming op deriving TargetType.Self);
                 # the ceiling stays at the issued number, ceilings never come
                 # down. EB-141 minted 2026-08-25 for the unstamped
                 # exp_shop_companion_channel instrument (R68); EB-140 minted
                 # at the R211 W3 build (the codegen upgrade-delta gap);
                 # EB-138/EB-139 minted by R211; EB-131/EB-133 retired
    # M63 minted 2026-08-29 by the KLEESPARK-R1 relayed review: whether the
    # funnel may repair a filed form is measurement law, not engineering.
    # M64 minted 2026-08-29 by the KLEESPARK-R2 relayed review: R222 B seats
    # fresh Opus as the DECIDING reader on rows `authored_by: [claude]`, which
    # R217 C calls same-family. How a round buys an author-disjoint deciding
    # read while the local seat is in shadow is [USER]'s, and has no default.
    # M65 minted 2026-08-30 by the Bag of Tricks re-ask (R224 item 17 = (3)):
    # the one clause the doctrine seat left, the top-level-cost rule.
    # M66 minted 2026-08-30 by the relayed open-items review, fact-checked:
    # per-fold C# feature gates versus the single PROTOTYPE_CARDS switch. It
    # is a design call and it revises the Furina reframe's countersigned
    # section 6.1 plan, which keys FURINA_REFRAME to the same compile symbol.
    # M67 minted 2026-08-30 out of Kokomi slice 2 §9 PICK 2, which had been
    # holding round-2 staging since 2026-08-29 without ever reaching this
    # register: the Charge accrual rule. It is a pick between design
    # directions and option (1) amends LAW R80, so it is [USER]'s twice over.
    # M69 minted 2026-08-30 by the X9READ-S1 graded read: `W9` fired on
    # Limb A (repeatable readers 58.91% of completed-turn reads, and 51.68%
    # with `EB-242`'s pilot-estimate reads removed), and a firing's whole act
    # is to return X9 to [USER] as a numbered pick.
    "M": 69,     # M62 minted 2026-08-29 by R221 A: the criterion that
                 # retires the fresh-Opus control form from every packet of
                 # a blind-QA round to the spot-check rate. The threshold is
                 # a number, so it is [USER]'s.
                 # M61 ANSWERED 2026-08-29: build option 3, and the element
                 # is local-seat only. The row left QUEUE the same day.
                 # M59/M60 minted 2026-08-29 by the R220 slate, one row per
                 # packet under one ruling (R206 as amended by R212): M59 the
                 # Furina reframe's sixteen design picks F1-F16, M60 the Burst
                 # retirement's four, K1/K2/KO1/KO2. Both packets reserved ids
                 # that had since collided -- the reframe reserved M54 and the
                 # retirement M52, and M54-M58 were minted by the blind run
                 # and the tester seat in between -- so both moved up and each
                 # packet's owed section carries a pointer to where it landed.
                 # M51 and M53 LEFT OPEN_IDS in this same commit, answered by
                 # R220 F (the Sparks countersign given, with LAW:481's
                 # bounded-spark line amended with it) and R220 E (the local
                 # tester seat, the Codex seat's ADVANCE being the condition
                 # [USER] set). Ceilings never come down.
                 # M58 minted 2026-08-29 by the local tester seat: the Codex
                 # seat's ADVANCE requires "periodic review by this seat" and
                 # names no rate, so the rate is [USER]'s. The mechanism ships
                 # on the default and takes any N.
                 # M58 ANSWERED 2026-08-29 by R220 G: N = 4, the shipped
                 # default -- it LEFT OPEN_IDS in that commit.
                 # M54-M57 minted 2026-08-29 by the KURAGEMEM001 blind run:
                 # Rule 1 is not taught (P3 0 of 10), P4's half (b) failed so
                 # the acceleration keyword stops being optional, the sealed
                 # record cannot carry P2/P6's objective side, and the
                 # prototype description channel is a generator contract.
                 # M53 minted 2026-08-29 by the same slate: whether a local
                 # model may hold a grading chair, i.e. whether the "no third
                 # family" paragraph is about authorship only. The branch that
                 # assumed it is unmerged and stays unmerged until the row is
                 # answered.
                 # M51/M52 minted 2026-08-29 by the sitting slate (R219): the
                 # Klee Sparks re-author's countersign -- its DRAFT prediction
                 # slate and its eleven as-built calls -- and Furina E4's
                 # C1/C2/C3, the ruling text, the prospective LAW text and the
                 # P7 triage plan, which no seat and no ladder clause can sign.
                 # M48 LEFT OPEN_IDS in the same commit, answered by R219 B:
                 # the automatic free-Attack rule is retired by the re-author
                 # rather than amended, and EB-186 was never a defect.
                 # M47..M50 minted 2026-08-29 by the process-review pass: the
                 # four decisions the two prototype-slice packets carry that
                 # are genuinely [USER]'s, moved out of the packets and into
                 # the register the read order points at. M47 Bag of Tricks
                 # (the held Klee arm), M48 the automatic free-Attack rule
                 # against D2, M49 the pilot's frozen Charge term, M50 the
                 # Charge accrual rule itself.
                 # M46 minted 2026-08-28 beside EB-171: the pinned build
                 # environment stopped describing the machine mid-sitting, and
                 # which way that is repaired -- back to the `public` branch,
                 # forward to 0.111.0, or a kept copy of the old tree -- is a
                 # one-way-ish call with every measurement label riding on it.
                 # M45 minted 2026-08-26: the post-playtest richness slate, ONE
                 # row under ONE ruling (R206), gated on the three-character
                 # playtest. M43/M44 minted by R206 (4ff9f90) and settled by
                 # R207 with no surviving HEAD citation — the exact blind spot
                 # this constant covers. A HEAD scan reads 40; the ceiling is
                 # the ISSUED high-water, so history outranks the scan here.
}

# Every id AT OR BELOW its ceiling that legitimately defines a row. Frozen by
# a scan of the two registers on 2026-08-25 (the grandfather census) and
# maintained by hand since: a fresh mint joins it in the same commit as the
# ceiling bump, and a closed row's id LEAVES it in the same commit as the row.
# That second half is the whole mechanism — see rule 6 in the docstring.
OPEN_IDS: dict[str, frozenset[int]] = {
    "EB": frozenset({
        # 40 LEFT OPEN_IDS 2026-08-30 with its row, on its acceptance word for
        # word -- "the five `GetNode`s resolve LIVE". On `0.2.1786+proto.dirty`
        # the boot log reads `convention scene ok:
        # res://furina/ui/energy_counter.tscn root=Control` with no
        # `has no node named` warning for any of the five, and a live Furina
        # combat (seed `07G8YGNTQHKX`, 42 actions, 1 fight, 0 defects) logs
        # `[BaseLib] Auto-converted 'res://furina/ui/energy_counter.tscn' from
        # Control to NEnergyCounter` and then plays on. That line IS the hard
        # cast: `NEnergyCounter._Ready` GetNodes all five and throws on a null,
        # so a run that continues past it is the five resolving. `godot.log`
        # carries no exception on the session.
        12, 15, 32, 33, 34, 35, 38, 41, 53, 65, 70, 71,
        # 78 LEFT OPEN_IDS 2026-08-30 with its row, on its acceptance word
        # for word -- "it runs, slate first". `X9READ-S1` was countersigned
        # (R233), the grader landed with its tests before the run, the run
        # took 1,800 runs in 53 s of a 1-hour ceiling, and the seven slots
        # came back 4 PREDICTED / 1 SPLIT / 2 MISS. `W9` fired on Limb A, and
        # a firing lives in QUEUE (`M69`), not in this row.
        74, 80, 83, 84, 116, 128,
        154, 158, 159, 160, 161, 163,
        # 184 LEFT OPEN_IDS 2026-08-30 with its row, on its acceptance word for
        # word -- "the Block mode replays with no target". Live on
        # `0.2.1786+proto.dirty`, `understudy/scenarios/eb184-modal-block-no-
        # target.yaml`: `{"action": "play_card", "card_index": 5, "mode":
        # "Gain 3 Block, applying no element"}` with NO `target` key answers
        # `status: ok` and the bridge's own message says the chosen mode "aims
        # at nobody"; player Block 0 -> 3, both expects held. The other half is
        # its twin `eb184-modal-damage-needs-target.yaml`, SEEN TO FAIL by
        # construction: the same card, the same absent target, the DAMAGE mode
        # named, is still refused "Card requires a target ... The chosen mode
        # aims at one enemy". A fix that switched aiming off would pass the
        # first file and fail the second, which is why there are two.
        180, 181, 183,
        189, 191, 193, 194, 195, 196, 197, 198,
        # 192 was minted 2026-08-29 and CLOSED 2026-08-30 by R231 A8: the
        # `regent_forge` canon package -- a regex union of Regent's Stars
        # with the unrelated Forge card -- was rebuilt as `regent_stars`
        # from the Star-touching cards only, membership taken from
        # `docs/current/research/regent-stars-economy.md` sec.2/3.5/3.6 and
        # locked to it by test, and the klee/spark and kokomi/commander
        # anchors were re-baselined on it. It leaves OPEN_IDS with its row.
        # 202/203 were minted 2026-08-29 by the KLEESPARK-R1 relayed review
        # and LEFT OPEN_IDS with their rows the same day, both BUILT under
        # R222: the slot-reachability check (`understudy/slot_plan.py`, a
        # round's `slots.yaml`, refused by `round --plan-only` and
        # `staged_turn check`) and the pre-grade target refusal
        # (`understudy/targeting.py`, falsifier `target_missing`). The repair
        # half stayed out of both and is QUEUE `M63`. Ceilings never come
        # down.
        # 205 was minted 2026-08-29 by R222 pick 6(d) -- a drafted arm for
        # the Klee Spark economy, now that the drafter can be offered the
        # rows -- and CLOSED 2026-08-30 by both of its halves landing:
        # KLEESPARK-S1 in the sim and KLEESPARK-W3 live. It leaves OPEN_IDS
        # with its row, which is what makes the number un-re-mintable; the
        # ceiling above still holds it.
        # 208/209 minted 2026-08-29 by KLEESPARK-R2 (packet section 13.4): the
        # declared-versus-reached enemy count, which no check can see, and the
        # stopping rule reading shadow grades in the shadow chair. 209 LEFT
        # OPEN_IDS the same day, FIXED and CLOSED with its row: the rule reads
        # DECIDING grades in the shadow chair and a refused deciding form is
        # no grade. 208's fix is a pick, so 208 stays.
        # 210 was minted AND CLOSED on 2026-08-29 by the same commit -- the
        # two-lane seed crossing, which was a save-file resolution in the mod
        # and never the harness's ports. It left OPEN_IDS in the commit that
        # closed it, with the ceiling above holding the number.
        208,
        # 211/212 minted 2026-08-29 by the KLEESPARK-R2 relayed review (packet
        # section 13.8): the battery's costs category passes on silence, and its
        # intent category is self-report.
        # 211 CLOSED 2026-08-30 by R232 and left OPEN_IDS with its row: the
        # ledger shipped on 2026-08-30, and the re-pick of the six sealed
        # `costs` boards -- the only thing its acceptance was still waiting on
        # -- is R232's. The ceiling above holds the number.
        212,
        # 206 was minted AND CLOSED on 2026-08-29 by the two-instance funnel
        # build -- it left OPEN_IDS in the same commit that closed it, with
        # the ceiling above holding the number so nothing re-takes it.
        # 207 was minted 2026-08-29 by the Klee Sparks whole-fight run (the
        # blind page printed the Bake-Kurage memory block on a Klee run) and
        # LEFT OPEN_IDS in the same branch on its live acceptance: an empty
        # wire map is an absent memory in the reader, the element's Refresh
        # asks the character test its Setup already asked, and the two frames
        # are in kokomi-kurage-memory-2026-08-29.md 14.12.
        # 199/200 minted 2026-08-29 by R220 B: the shared Burst retirement and
        # its C# arm, both gated on the three character folds landing first.
        199, 200,
        # 213-219 minted 2026-08-30 by R224: the engineering the sitting
        # slate creates, now that every item on it is ruled. See the ceiling
        # comment above for what each one is, and for why the Bake-Kurage
        # retirement, the five burst-fold shapes and M55's pile-view line
        # minted nothing.
        # 218 LEFT OPEN_IDS 2026-08-30: built and merged (#199).
        # 219 LEFT OPEN_IDS 2026-08-30: Prune re-authored, merged.
        # 217 LEFT OPEN_IDS 2026-08-30: the accelerator keyword's summon dial
        # is deleted in both engines and both doors ask the one question.
        # 213 LEFT OPEN_IDS 2026-08-30: the prototype surface has an upgrade
        # channel on the row, emitted through the shipped upgrade path.
        # 215 LEFT OPEN_IDS 2026-08-30: the face is on the row and the
        # boot-time loc merge is deleted -- one channel per card.
        # 216 LEFT OPEN_IDS 2026-08-30: every blind run writes a per-turn wire
        # snapshot and a per-play meter ledger the tester never sees.
        # 214 LEFT OPEN_IDS 2026-08-30: the KURAGEMEM002 rerun ran and P3 came
        # in at 5 of 10 with two Musters against a threshold of 3-with-1, which
        # is the row's acceptance word for word. Only 214 was removed.
        # 229 minted 2026-08-30 by that same rerun: P1, P2 and P4 all read
        # UNREACHED because a blind run's reply schema is `command` and
        # `thinking` and never a forecast, so a slate slot that grades one has
        # no per-turn field to count. EB-216's other half.
        #
        # 229 LEFT OPEN_IDS 2026-08-30 on its acceptance word for word -- "a
        # forecast slot has a field to count". `blindplay.command_schema()`
        # takes a forecast count: at zero (the default, and every run already
        # registered) it returns the object it always returned, and above zero
        # it declares `forecast` as the FIRST property and the FIRST required
        # key, `additionalProperties` still False. `--forecast QUESTION`,
        # repeatable, is the switch a registration throws; the block prints
        # above the board on combat pages only, the answers are sealed on the
        # COMMITTED half of the record with an asked/answered count, and a
        # short answer is counted short rather than stopping a live run. The
        # lock was seen to FAIL first, on all three halves -- the OFF schema,
        # the field's order in the reply, and the block's position on the
        # page. Staged twin: EB-239.
        # 220 minted 2026-08-30 -- the meter cost badge (Encore, Charge).
        220,
        # 223 minted 2026-08-30 by the relayed open-items review, fact-checked:
        # R222 (a)'s whole-fight read of the strict Rare Power, owed work and
        # not a pick, gated on section 16.11 pick 1's deck composition.
        #
        # 223 LEFT OPEN_IDS 2026-08-30 with its row, on its own acceptance
        # word for word -- "the read recorded in EXPERIMENTS.md". KLEESPARK-W4
        # ran and is graded (packet section 20; 0 PREDICTED / 1 MISS / 3
        # UNREACHED). The read is TAKEN and it is not the reading the row
        # wanted: `proto_true_spark_knight` was drawn on seven combat pages and
        # never played, so every K slot is UNREACHED by the slate's own rule
        # and R222 (a)'s question is still open. That is an outcome, not an
        # unfinished row, and no second session is started (section 19.6).
        # 224/225 minted 2026-08-30 by R225: Bag of Tricks on EB-182's
        # mode-price machinery, gated on EB-205's read; and the
        # prototype-patch scope lint that keeps one PROTOTYPE_CARDS switch
        # honest.
        #
        # 225 LEFT OPEN_IDS 2026-08-30 with its row: the lint is written
        # (`tools/lint_prototype_patch_scope.py`, `ci` lane), it was seen to
        # FAIL on three real prototype patches first, and all three were
        # fixed. The ceiling stays at 225 -- ceilings never come down.
        224,
        # 228 minted 2026-08-30 by the Kokomi slice-2 round-2 job: the lint
        # for a packet that HOLDS live work on an unminted pick.
        228,
        # 230/231/232 minted 2026-08-30 by the overnight integration, from the
        # night's two live runs and from the integration's own suite: the
        # `place_bomb` face, the teardown that reports a kill it did not make,
        # and the lane test leaking across pytest sessions.
        #
        # 230 LEFT OPEN_IDS 2026-08-30 with its row: every `place_bomb` face
        # prints the Bomb's own amount, carried by a plain "BombDamage" var
        # instead of the attack-var family, and the lock was seen to FAIL on
        # all seventeen shipped faces first.
        #
        # 232 LEFT OPEN_IDS 2026-08-30 with its row, on its acceptance word
        # for word -- "two concurrent sessions stay green". The row's
        # diagnosis was half right and the fix is the other half: `tmp_path`
        # is ALREADY session-unique (`pytest-2295` and `pytest-2296` are two
        # base directories), so nothing shared a save tree -- a path out of
        # 2295 reached 2296's assertion over the WIRE, because the lane tests
        # bound the FIXED loopback port 15599 and on Windows a second process
        # binds it too, silently, with the FIRST binder answering everybody.
        # Every server in that file now binds port 0 and reads its port back,
        # `_LaneServer` refuses `allow_reuse_address` so a future constant
        # fails at the bind rather than quietly, and `_lane_bridge` no longer
        # TAKES a port. Seen to FAIL: with a squatter holding 15599, the old
        # file's named test fails `DID NOT RAISE LaneCrossed` where the new
        # one passes; two concurrent sessions of the old file give 1 failed /
        # 13 passed against 14 passed, and of the new file 91 passed twice.
        #
        # 231 LEFT OPEN_IDS 2026-08-30 with its row, on its acceptance word
        # for word -- "teardown proves the PID gone before the marker, lock
        # seen to FAIL". `embark --teardown` rebuilds the session from the
        # ledger on disk and so holds no `Popen`; `_kill` found `proc is
        # None`, did nothing, and `_stop_game` returned "process terminated"
        # anyway. Two halves: `_launch` writes the pid onto the launch entry
        # (the only copy that outlives the process that made it), and
        # `_kill_and_prove` polls the process table for up to
        # `PID_EXIT_TIMEOUT_S` and RAISES on a survivor, so `_step` records
        # NOT REVERTED naming the image still holding the number. An
        # unanswerable probe counts as ALIVE, and a pre-change ledger with no
        # pid refuses rather than assumes. `halt_spin`'s marker goes through
        # the same proof. SEEN TO FAIL against a live pid (this python
        # process, `taskkill` stubbed, real `tasklist`): old soak.py wrote
        # REVERTED / "process terminated", new soak.py writes NOT REVERTED /
        # "pid N (python.exe) is STILL ALIVE".
        # 233/234 minted 2026-08-30 by the post-merge review: the scorer/pool
        # half of KLEESPARK-S1's S3 miss, and the memory-cadence read on a
        # developed deck the kurage packet defers.
        #
        # 233 LEFT OPEN_IDS 2026-08-30 with its row. `SPARK_ALT_VALUE` = 4.00
        # is a median over five rows that ALL print `damage`, so charging it
        # to a sink that prints no Attack body drove every such row NEGATIVE
        # and the drafter could take one at no bank, on no seed. `spend_spark`
        # now routes a non-damage sink to `STATIC_SPARK_SPEND_COST` -- this
        # repository's other, damage-free, already-derived per-Spark price,
        # used whole, so no number is minted. The acceptance re-run moved the
        # drafted non-damage-sink share 3.2% -> 3.8% at the registered
        # 600 runs / seed 11, and the three twins moved from LAST in the
        # uncommon tier to 0.00 / 1.00 / 2.00 inside it. What remains is
        # composition, which the row itself sends to the fold, as does
        # Rummage's missing pool seam.
        234,
        # 235 minted 2026-08-30 by R228 pick 1, successor to the CLOSED
        # EB-223: KLEESPARK-W4 drew the strict Rare Power on seven pages and
        # the tester played it on none, so R222 (a)'s owed whole-fight read
        # is UNREACHED and a new registration -- an uptake slot, not W4
        # repeated -- carries it.
        235,
        # 236/237/238 minted 2026-08-30 by KLEESPARK-BT1, all three out of
        # what the round found that was not a slot: the resource-round board
        # trap (holding everything but the bank constant leaves the whole hand
        # playable, so the `intent_insensitive` falsifier fires on the
        # construction -- 7 of 8 forms), `slot_plan._spark_prices` reading a
        # TOP-LEVEL `spend_spark` only, so the row under test is invisible to
        # its ceilings, and the blind page printing no relics, which is why
        # Pounding Surprise refunding the mode's own price inside the turn was
        # invisible to every form and uncontrolled by the registration.
        #
        # 237 LEFT OPEN_IDS 2026-08-30 with its row: `slot_plan._spark_prices`
        # now reads R225's clause in full -- a top-level `spend_spark` or the
        # head of a `choose_one` mode, and nothing nested -- the lock was seen
        # to FAIL first, and BT1's `t01` plan lists the three prices with
        # `affordable_spark_uses` 1. DISCLOSURE (R101b): BT1's `B1` predicate
        # was written under the OLD reading; re-planning that CLOSED round
        # reports ceiling 0 against threshold 1, and `slots.yaml` is NOT
        # edited -- a published measurement stands as published.
        # 157 LEFT OPEN_IDS 2026-08-30 with its row: one pin. The manifest's
        # BaseLib `min_version` was 3.3.6, a floor nothing compared to
        # anything; it is now 3.4.5, the release this machine compiles against,
        # the assembly vault's `PIN.json` records and the installed Workshop
        # item reports -- the same number STATE.md's pin block carries.
        # `tier0/tests/test_eb157_baselib_pin.py` is the gate: manifest vs
        # STATE.md, plus a curated enumeration of the BaseLib types we call so
        # a reach for a new API meets the pin. RESIDUAL UNKNOWN, disclosed
        # rather than closed: the 3.3.6 SURFACE could not be obtained (Steam
        # serves only a Workshop item's current version and no older copy
        # exists here or in the vault), so the enumeration was taken against
        # 3.4.5 and whether those symbols exist in 3.3.6 is still unknown.
        # Raising the floor to the verified number is what makes it harmless.
        # 156 LEFT OPEN_IDS 2026-08-30 with its row: the per-fight telemetry
        # row now reads `ReactionEffects.ResolvedThisCombat(combat, player)`,
        # a per-seat counter keyed exactly like `BombPower`'s detonation
        # totals next door. `TotalResolved` is UNCHANGED and still global --
        # that scope is a sealed ruling (red-pen R1) about GAMEPLAY, and the
        # defect was sampling it into a per-seat ROW. A dealer-less reaction
        # belongs to no seat, so the seats sum to at most the team-wide count;
        # that asymmetry is pinned, not hidden. `understudy/README.md`'s schema
        # line is corrected. Tests: `KleeTests/ReactionSeatCountTests.cs`.
        # 155 LEFT OPEN_IDS 2026-08-30 with its row: KleeSelfCheck rule R20
        # sweeps this assembly's `KLEEMOD-` keyword CONSTANTS -- found by
        # reflection, never a curated list, because the failure being fixed IS
        # the commit that adds a key and forgets its row -- for a `.title` row
        # in `card_keywords`. The three salon-member keys were hoisted out of a
        # switch body in the same commit, since a key that is only a literal
        # inside a method is one reflection cannot see. Seen to fail in
        # `klee-mod/KleeTests/KeywordTitleRowTests.cs`.
        # 153 LEFT OPEN_IDS 2026-08-30 with its row: `tools/lint_power_icons.py`
        # (ci lane) bites on both shapes the row named -- a concrete
        # `PowerModel` with no `PathFor` case, no `IconExempt` entry and no
        # `ICON_DEBT` row, and an aura element whose icon path `PathFor` builds
        # by CONCATENATION with nothing behind it. Both are exercised against
        # synthetic input in `tier0/tests/test_eb153_power_icons_lint.py`. The
        # seven powers the row names ship as named debt rather than a silent
        # pass: no icon was invented for any of them.
        # 236 LEFT OPEN_IDS 2026-08-30 with its row: `board_design_findings`
        # in `--plan-only` walks EVERY order of play with relic gains counted
        # (`both_buyable`, R229's strong form) and refuses a hand the Energy
        # pays for whole (`no_forced_trade`). BT1's four boards fail it --
        # `t02` on four both-buyable orders -- and BT2's three pass. It is
        # deliberately NOT a `ci` lint: a tree-wide sweep would refuse a
        # closed round's published boards. The lint count is 31 since conflict-markers (2026-08-30), 30 since
        # EB-153 added `power-icons` (2026-08-30).
        # 238 LEFT OPEN_IDS 2026-08-30 with its row, on its acceptance word for
        # word -- "a staged page shows the relic line and a form quotes it".
        # KLEESPARK-BT2's pages printed the run's relics and `t01`'s shadow form
        # quoted one by name, doing the turn's arithmetic with it: "the bombs
        # detonating under Pounding Surprise restore 3 Sparks". The deciding
        # form on the same board quoted the effect without the name. Both
        # halves met; that the forms were later REFUSED for an unrelated
        # falsifier (`forecast_missing`) does not bear on whether the relic
        # reached the reader, which is all this row asked.
        #
        # 239 NEVER ENTERED OPEN_IDS: minted and CLOSED in the same commit,
        # on its lock. `seat.form_schema()` now declares `forecast` --
        # nullable-and-required on `target`'s rule, `additionalProperties`
        # still `False`, and the local tester prints the same schema, so one
        # fix repairs both chairs. Seen to FAIL first: an answered form was
        # refused `undeclared:forecast` by the old schema, and a form that
        # OMITS the field is still refused `forecast_missing` on an asking
        # board after the fix.
        # 240 minted 2026-08-30 by KLEESPARK-BT2 §24.6: printing the relics
        # immediately falsified a printed assumption, and the preflight's
        # assumption check cannot see the wire's relic list.
        # 240 LEFT OPEN_IDS 2026-08-30 with its row, on its acceptance word for
        # word -- "one board's refusal seen live". All THREE committed
        # `klee-sparks-bt2r` boards were staged as they stand (R101b: read,
        # never edited) against `0.2.1786+proto.dirty`, and all three were
        # refused before a packet was written, each naming the mismatch:
        # "hp: the board declares 'first' at 55 and the wire reads 45" (t01),
        # 46 (t02), 40 (t03) -- exactly the three live bodies the row names.
        # The CONTROL half holds too: a correct current-world board (a scratch
        # copy of `klee-sparks-bt3/t01`, relic leg corrected) stages clean,
        # packet sha256 be932c77, so the preflight refuses a false assumption
        # and not a board. The control's first attempt refused on the RELIC
        # leg and that is a real find -- BACKLOG `EB-243`.
        # 241 minted 2026-08-30 by R231 A3, gated on the Kokomi fold.
        241,
        # 242 minted 2026-08-30 by the X9READ-S1 graded read (packet §9.4):
        # the reads-per-turn instrument counts the PILOT's estimates as
        # reads. `pilot/policy.py:439` and `:555` call
        # `effects._bonus_formula` with no card, and its `_per_charge` branch
        # ticks `note_charge_read` unconditionally -- so 9,893 of the 13,198
        # pooled `bonus_formula` reads (74.96%) are deliberation, which §2 of
        # the packet declares deliberately NOT counted. It is the whole of
        # `X3`'s MISS (a 15-read turn, 14 of them estimates) and it moves
        # `X5` and `X1`; the published grades stand as graded (R101b).
        #
        # 242 LEFT OPEN_IDS 2026-08-31 with its row, on its acceptance word
        # for word -- "a valuation call tallies nothing, on a test seen to
        # FAIL". `tier0/tests/test_eb242_valuation_is_not_a_read.py` was seen
        # to fail 5 of 6 before the fix (the pilot's damage estimate alone
        # tallied `{'bonus_formula': 1}`) and passes 6 of 6 after.
        # `_bonus_formula` grew a keyword-only `valuation` flag, DEFAULTING
        # to the resolve path so a new resolve site cannot opt out by
        # forgetting, and the two pilot sites (`policy.py` `_expected_damage`
        # and `_raw_block`) pass `valuation=True`. What a RESOLVED play
        # tallies is untouched and is pinned by its own case in the same
        # file, as is the untouched fanfare leg of the same helper -- that
        # instrument has its own registration and is not in this row's scope.
        # The published X9READ-S1 grades stand as graded (R101b); the re-read
        # M69 pick (2) waits on is DRAFTED in the same branch, unrun.
        # 243 minted 2026-08-30 by EB-240's live control: BT3's boards declare
        # a relic pair the wire does not carry on their pinned seed, so the
        # round cannot stage until they are re-drafted (renumbered from
        # EB-242 at the fold; X9READ-S1's mint keeps 242).
        #
        # 243 LEFT OPEN_IDS 2026-08-30 with its row, on its acceptance word
        # for word -- "both BT3 boards stage". The gift was read OFF THE WIRE
        # at both pinned seeds before anything was re-drafted, by staging each
        # board AS COMMITTED and taking its refusal as the reading: `t01`
        # (`YX7PB48WR7R4`) carries *Stone Humidifier* and `t02`
        # (`R805DJ56LZHM`) carries *Scroll Boxes* -- a DIFFERENT gift on each,
        # so the registered single name assumed a constant the staging path
        # does not have. Both `expects.relics` blocks were re-drafted to what
        # is true now with a disclosure line in each board and in the MANIFEST
        # (R212: a moved world means re-draft and disclose, never re-sign; the
        # R231 countersign stands and the slate G1-G4 is untouched), the
        # re-draft was committed BEFORE the round ran, and both boards then
        # staged clean through the EB-240 preflight. Both `hp.first` legs
        # (40 and 46) matched the wire unchanged.
        # 244 minted 2026-08-30 by the KLEESPARK-BT3 round (packet section
        # 25.5.2): the third leg of the same class as EB-240 and EB-243 -- a
        # board asserting a fact the wire does not carry -- on the one leg the
        # expects: block does not check. The encounter is generated from the
        # seed and the board writes no intent, so both boards notes and
        # board: mirror printed "one enemy telegraphing an attack for 16"
        # while t01 drew a Debuff intent and t02 an attack for 12. It is
        # causal, not cosmetic: t01 holds no Attack in hand, so against a
        # Debuff no intent could change the line, both deciding forms were
        # refused `intent_insensitive`, and G1/G2/G4 all graded UNREACHED --
        # F2 UNREACHED for the fourth round running.
        #
        # 244 LEFT OPEN_IDS 2026-08-31 with its row, on its acceptance word
        # for word -- "a board declaring an intent the wire lacks is refused
        # at stage". `expects:` grew an optional `intent` leg in the style of
        # the two it had: `{who: {kind: attack, amount: 16}}`, `kind`
        # required and the numbers optional, refused rather than coerced,
        # compared through `adapter._intent` so a board is checked against
        # the parse the pilot and the falsifier already act on, and quoted
        # back beside the telegraph the page actually printed. Nine cases in
        # `tier0/tests/test_staged_turn.py`, 7 of them seen to FAIL first --
        # including BT3's own two committed boards, read and never edited
        # (R101b), whose mirrored `attack 16` is refused against the Debuff
        # and the attack for 12 they drew. The two that pass red are the
        # untouched-behaviour guards: a board declaring no intent is asked
        # nothing, which is where every board written before this row is.
        # The row's GATE -- a repaired BT3 round -- is a RUN and is not
        # discharged here; the leg it was waiting for exists.
        # 245/246 minted 2026-08-30 by KLEESPARK-W5 (packet section 25.6.3).
        # 245: blindplay session asked for a FIGHT RECORD on a card_select
        # observation -- Bag of Tricks' own Choose one mode screen, which is
        # the middle of a play. The sealed record carries FOUR fight records
        # for THREE fights and the phantom one reports the fight over while
        # the enemy stood at 44/44; it cost a Codex call and put a falsehood
        # in a sealed record. It touched no graded slot: B1-B5 are counted off
        # per-page wire snapshots and forecast rows, and the mode was still the
        # tester's own free choice one transcript row later.
        # 246: the printed option name reaches the blind observation AND the
        # command with its markup intact -- choose "Spend 3 [gold]Sparks[/gold]
        # : place 3 [gold]Bombs[/gold] dealing 5". scenario.py folds those tags
        # out for the staged packet and the blind render does not, so one
        # choice has two printed names. The W5 tester named it unprompted.
        245,
        246,
        # 247/248 minted 2026-08-30 by KURAGECAD-W1 (kurage packet section
        # 15.9.5). Both are DISPLAY and WORDING rows, which is the destination
        # K1's and K4's decision columns name; neither is a re-price, a dose
        # change or a move to any constant (R231 A2).
        # 247: the Bake-Kurage's persistent buff promises damage scaling with
        # Charge while the pulse it actually delivers is 4 damage or 5 Block
        # depending on the last card played. The blind tester named it in BOTH
        # fight records, unprompted, and the wire's pulse_kind agrees with the
        # tester rather than with the text.
        # 248: a Muster-discounted Thoma prints cost 2 on the sheet and enrols
        # at cost 1 / price 3. The 3x rule is applied correctly to the card's
        # EFFECTIVE cost; what the player cannot do is get from the printed 2
        # to the queued 3, and the tester said so in those words.
        247,
        248,
        # 249/250/251 minted 2026-08-30 by the register-reconcile pass, all
        # three named in writing before the pass and filed nowhere.
        # 249: `tools/card_distinctness_report.py` is two-halved. Its `SHEETS`
        # list (`:195-198`) globs `docs/*-cards.yaml` and then appends
        # `mondstadt-companions.yaml` and nothing else, so Fontaine's and
        # Inazuma's companion sheets are ABSENT from the instrument's input --
        # a different failure from the size exemption at `GATE_MIN_POOL = 30`
        # (`:263`), which is what the packet was reading when it found this.
        # And there is no taxonomy filter, so adding the sheets alone would
        # count Personal and `guest_star` rows inside a metric that measures
        # the DRAFTABLE Universal pool -- Fontaine proves it, three of its
        # nineteen rows being cameos no player can draft. Neither half bites
        # today (17/19/15, all exempt); both bite the moment a pool reaches 30,
        # which is what P4 is for. Companion packet section 2.6; R234 5.3.
        #
        # 249 LEFT OPEN_IDS 2026-08-31 with its row, on its acceptance word
        # for word -- "three sheets read, Personal and guest-star out". Both
        # halves seen to FAIL first, together, in
        # `tier0/tests/test_eb249_distinctness_input.py`: 6 of its 8 cases
        # failed before the change and all 8 pass after. (a) `SHEETS` globs
        # `docs/*-companions.yaml` instead of naming one file, so a fourth
        # nation's sheet arrives on its own. (b) `universal_rows` drops any
        # row carrying `personal_pool` or `guest_star` -- the loader's own
        # predicate, stated here because this tool reads sheets and not the
        # index -- applied after the read, so an unparseable sheet is still
        # the hard failure it was. Mondstadt reads 16 rather than 17 (Prune),
        # Fontaine 16 rather than 19 (three cameos), Inazuma 15 whole. All
        # three are under GATE_MIN_POOL and are skipped by size exactly as
        # Mondstadt already was; the three character pools are unmoved at
        # 84/79/76 and the ratified debt is unmoved at klee/uniq,
        # kokomi/uniq and kokomi/maxclu, each pinned by its own case.
        # 250: `tier05/rewards.py:220` `_RARITY_FALLBACK` is
        # `{"rare": "uncommon", "uncommon": "common"}` -- a ladder with no rung
        # under `common`, walked by `while rarity not in pool` at `:251-252`
        # and `:260-261`. Every pool this repository ships has commons, so the
        # ladder has always terminated; a colorless-SHAPED pool does not, and
        # the anchor read off the assembly says why -- 0 commons of 65, and the
        # base game's own `CardFactory.RollForRarity` falls FORWARD rather than
        # back precisely because a pool can lack a tier. The row exists because
        # the anchor made a latent crash reachable, not because anything has
        # crashed. `docs/current/research/colorless-anchor-2026-08-30.md`.
        #
        # 250 LEFT OPEN_IDS 2026-08-31 with its row, on its acceptance word
        # for word -- "a commonless pool rolls its offers, on a test seen to
        # FAIL". `tier05/tests/test_eb250_commonless_pool_rolls.py` was seen
        # to fail 4 of 6 first, on the row's own `KeyError` raised at
        # `rewards.py:252`, and passes 6 of 6 after. The ladder now offers a
        # roll its own tier, then the tiers BELOW in the order they have
        # always been tried, then the tiers above -- the base game's
        # fall-forward for the end the downward walk used to run off, and
        # byte-identical for every pool that already resolved. Down is still
        # first deliberately: the wrapping walk taken whole would re-point
        # the reference pools' rare rolls from uncommon to common and move
        # every archived number taken on them, and two of the six cases pin
        # exactly that. The `distinct=True` ladder keeps its downward-only
        # step -- a different question -- with a `seen` set so a resolvable
        # step forward cannot spin.
        # 251: the two Klee Personal Companion card drafts R234 owes at its
        # section 5.3 (P2 and P5), 4-star, against P5a's standing bar for a
        # Rare. Design DRAFTING, which the R212 ladder makes Claude's; the pick
        # between genuinely different directions, and P5a itself, stay
        # [USER]'s. It is a row and not a QUEUE line because nothing here asks
        # him anything yet. Sheet rows are gated on the Burst fold (P3).
        251,
        # 252 minted 2026-08-30: the role-tempo baseline predates 0.111.0; a
        # full regen moves floors and reads two NEW coverage findings on
        # Klee, so the re-baseline is a disclosed act, not a silent regen
        # (three canon states preserved as dated vault files).
        #
        # 252 LEFT OPEN_IDS 2026-08-31 with its row, on its acceptance word
        # for word -- "the coverage gate green on the 0.111.0 canon". The
        # re-baseline branch regenerated the canon from the 0.111.0 `sts2.dll`
        # and re-pinned the two NEW Klee findings the regen reads, each with
        # its arithmetic said out loud in the debt list's header; the gate
        # runs 20 findings against 20 pins. The ceiling stays where it is.
        # 253 minted 2026-08-31 by the EB-242 fix: the pilot's fanfare
        # valuations tick note_fanfare_read through the same helper --
        # fixed separately because it moves a published measurement's
        # source; the EB-242 test file pins the exposure.
        253,
        # 254-258 minted 2026-08-31 by the triage of [USER]'s manual solo
        # Kokomi playtest. The world it was played on is the reason four of
        # them exist: `0.2.1786+proto.dirty` was still installed, so a manual
        # session ran on a dev build carrying both prototype arms. 254 the
        # Muster keyword printed "costs 1 less" with no duration, against four
        # sibling faces that print `this turn` -- the build is
        # `AddThisCombat` and the ruled memory price depends on that, so the
        # face was what moved, not the number: CLOSED 2026-08-31, the tip
        # reads "costs 1 less this combat" and both pins moved with it.
        # 255 `draft.py`'s
        # "every starter card is basic" is an unchecked comment, false on
        # SHIPPED `an_invitation` and on flagged `to_the_front`, and
        # `_committed_share` excludes by RARITY, so a starter reads back as a
        # draft. 256 the Gorou/Metallicize stall against the Lagavulin
        # Matriarch -- unwinnable AND unloseable, and no engine has a
        # no-progress detector to notice. 257 R217 D restores the release
        # package before a measured run or a handoff, and a manual playtest
        # is neither. 258 a second un-golded resource keyword on a face,
        # which also falsified the generator comment claiming there was one:
        # CLOSED 2026-08-31, twenty-four faces golded at their emission sites
        # and `tools/lint_keyword_meters.py` grew the lock, seen to FAIL on
        # all of them first.
        255,
        256,
        257,
    }),
    # M46 left OPEN_IDS with its row when R218 answered it (2026-08-28); the
    # ceiling stays at 46, because ceilings never come down.
    # M54-M57 minted 2026-08-29 by the KURAGEMEM001 blind run: Rule 1 is not
    # taught, P4's half (b) failed, the record cannot carry P2/P6's objective
    # side, and the prototype description channel is a generator contract.
    # M51 and M53 left OPEN_IDS with their rows when R220 answered them
    # (2026-08-29): F countersigned the Sparks re-author, E handed the local
    # model a TESTER seat and no grading chair. M59/M60 join with the two
    # slate rows R220 mints.
    # M61 left 2026-08-29, answered the day it was minted: the build is
    # option 3 and the element is local-seat only.
    # M62 and M63 closed 2026-08-29 by R222 B and R222 C -- the seat's
    # return condition (>= 6/8 over one round AND the requalification
    # battery) and "refuse only, never repair". Both rows left HEAD in
    # that commit, so both numbers leave this manifest with them.
    # M64 minted 2026-08-29 by the KLEESPARK-R2 relayed review: the
    # author-disjoint deciding read while the local seat is in shadow.
    # M47, M49, M50, M52, M54, M55, M56, M57, M59, M60 and M64 LEFT OPEN_IDS
    # on 2026-08-30 with their rows: R224 landed the sitting slate WHOLE, so
    # every row it covered closed. M47 took option (3), build per-mode
    # playability (EB-182) first then re-ask, and EB-182 now names its two
    # consumers; M55 took (5) re-scoped to the pile view and folds into
    # EB-214; M64 took the SPLIT -- Codex decides any round that can read PLAYABLE
    # an arm, fresh-Opus rounds are INSTRUMENT rounds -- written into
    # OPERATIONS' Local tester seat section. The rest:
    # the pilot's obsolete Charge term closed, the Kurage-memory redesign's
    # four unruled rows ruled, the Furina reframe and its sixteen picks
    # countersigned PROSPECTIVE, the blind run's Rule-1, instrument-gap and
    # description-channel picks taken, and the Burst retirement's five shapes
    # ruled. No slate row survives, and the five rowless items (16, 19, 20,
    # 28 and 31) minted no M row either -- the slate packet was their pick
    # list and their engineering is EB-214/218/219. Ceilings never come down.
    # M65 and M66 LEFT OPEN_IDS 2026-08-30 (R225), with their rows: the
    # top-level-cost clause is amended to admit a mode-head price, so Bag of
    # Tricks proceeds as EB-224; and the single PROTOTYPE_CARDS switch stands
    # with a scope lint (EB-225) plus a three-fight soak on every dev deploy.
    # M67 minted 2026-08-30: Kokomi's Charge accrual rule, out of slice 2 §9
    # PICK 2, where it had been holding round-2 staging unregistered since
    # 2026-08-29. It was re-scoped the same day to the CONSEQUENCE of that
    # rule once R226 answered accrual one branch over, and it LEFT OPEN_IDS
    # 2026-08-30 with its row, closed by R227 at option (1): slice 2 retires,
    # its four Charge-priced arms and their round-2 boards delete, the spend
    # plumbing stays, and the Charge question moves whole to the memory
    # program (EB-229, then whole fights). Ceilings never come down.
    # M68 minted 2026-08-30 under R227 pick 4: the Furina Spotlight pick R226
    # owed, drafted as an options packet the same day. It LEFT OPEN_IDS the
    # same day with its row, closed by R228 at option (1) -- one mode, priced:
    # Center Stage retires, Guest Cast and SPOTLIGHT_BASE_MULT = 1.5 stay, and
    # the selector aims a Companion and costs Encore. M45(4) is answered with
    # it; M45 itself stays until its other six calls are answered. Ceilings
    # never come down.
    # M10, M14, M16 and M19 LEFT OPEN_IDS 2026-08-30 with their rows,
    # closed by R231: the Fontaine Rares close APPROVED with Neuvillette
    # shipping as-is; the companion-channel trigger closed as NOISE, the
    # published grade standing as graded (R101b); SceneSlots stays at 4 as
    # harmless headroom; and the energy orb takes A Fontaine Hydro, which
    # lifts EB-40's gate. Ceilings never come down.
    # M69 minted 2026-08-30 by the X9READ-S1 graded read and OPEN with its
    # row: R188's watch trigger fired, so X9 returns as a numbered pick.
    "M": frozenset({13, 26, 45, 69}),
}

# The series whose ids are not a prefix plus an integer: sprint-gate families
# (`S4-G*`, `CC-G*`), one-off tags, and `SKIP-10.9`. No arithmetic is possible
# on these, so there is no ceiling — the set IS the manifest, with the same
# rot semantics as OPEN_IDS. A retired `S4-G7` is therefore refused the same
# way a retired `EB-53` would be: it is simply not in here.
# S4-G11 left this manifest 2026-08-30 with its row, ruled in all three parts
# by R231: Backstroke KEPT, Tengu Flurry KEPT with `chinowa_ward` renamed
# `chinju_ward`, and the EB-82 Grave conversion taking the Liyue / Nameless
# Cairn labels. S4-G6 STAYS -- R231 answered only its MECHANISM.
OPEN_IRREGULAR: frozenset[str] = frozenset({
    "CC-G1", "CC-G2",
    "S4-G6", "S4-G12", "S4-G14", "S4-G17",
    "SKIP-10.9",
})

# Series another lint already owns. A register row defining one of these would
# sit outside both guards: `lint_r_numbers` checks `## R<n>` HEADINGS in
# docs/current/, never table cells, so a `| `R209` |` row would be namespaced
# by neither tool.
FOREIGN_SERIES: dict[str, str] = {
    "R": "tools/lint_r_numbers.py",
    "D": "tools/lint_r_numbers.py",
}


def parse(cid: str) -> tuple[str | None, int | None]:
    """`'EB-137'` -> `('EB', 137)`; `'S4-G6'` -> `(None, None)`."""
    m = SERIES_NUM.match(cid)
    if not m:
        return None, None
    return m.group("series"), int(m.group("num"))


def expand(token: str) -> list[str]:
    """One first-column token -> the ids it defines, or [] if it is not one."""
    token = token.strip()
    m = COMPOUND.match(token)
    if m:
        head, num, rest = m.group("head"), m.group("num"), m.group("rest")
        ids = [head + num] + [head + part
                              for part in rest.split("/") if part]
        return ids if all(ID.match(i) for i in ids) else []
    return [token] if ID.match(token) else []


def row_ids(text: str) -> list[tuple[str, int]]:
    """Every (id, line number) a table row DEFINES in this register text.

    Takes TEXT rather than a path so the self-test below exercises this
    function itself. A second copy of the parse living in the test is exactly
    the drift a self-test is supposed to catch.

    The id cell is the first column. A cell that is not entirely backticked
    id tokens is not a definition — that is what keeps `Art debt` and the
    `S8 + S10 galleries` row out, and it is a deliberate REFUSAL rather than
    an oversight: a row without a machine-readable id cannot be checked for
    uniqueness and should not pretend to be.
    """
    out: list[tuple[str, int]] = []
    for n, line in enumerate(text.split("\n"), 1):
        stripped = line.strip().lstrip("> ").strip()
        if not stripped.startswith("|"):
            continue
        cell = stripped.split("|")[1].strip()
        tokens = BACKTICKED.findall(cell)
        if not tokens:
            continue
        # The cell must be ONLY those backticked tokens and the ` / ` between
        # them, or it is prose that happens to open with a code span.
        residue = BACKTICKED.sub("", cell).replace("/", "").strip()
        if residue:
            continue
        for token in tokens:
            out.extend((cid, n) for cid in expand(token))
    return out


def manifest_findings(where: dict[str, list[tuple[str, int]]],
                      ceilings: dict[str, int],
                      open_ids: dict[str, frozenset[int] | set[int]],
                      open_irregular: frozenset[str] | set[str]) -> list[str]:
    """Rules 4–7: every defined id is a live entry, every entry a live row.

    Takes the manifest as arguments rather than reading the module constants,
    so the self-test can manufacture a retirement without editing the real one.
    """
    out: list[str] = []
    seen_int: dict[str, set[int]] = collections.defaultdict(set)
    seen_irregular: set[str] = set()

    for cid, sites in sorted(where.items()):
        placed = ", ".join(f"{rel}:{line}" for rel, line in sites)
        series, num = parse(cid)

        if series in FOREIGN_SERIES:
            out.append(
                f"FOREIGN SERIES: {cid!r} defines a row ({placed}), but the "
                f"{series}-series is owned by {FOREIGN_SERIES[series]}, which "
                f"reads `## {series}<n>` headings and never table cells. A row "
                f"wearing that number is namespaced by neither tool.")
            continue

        if series is not None and series in ceilings:
            seen_int[series].add(num)
            ceiling = ceilings[series]
            if num > ceiling:
                also = ("" if num in open_ids.get(series, frozenset())
                        else f", and add {num} to OPEN_IDS[{series!r}]")
                out.append(
                    f"UNRECORDED MINT: {cid!r} defines a row ({placed}) above "
                    f"the frozen {series} ceiling of {ceiling}. Bump "
                    f"CEILINGS[{series!r}] to {num}{also} in the minting "
                    f"commit — two branches each taking 'the next free number' "
                    f"then collide on this constant instead of on main.")
            elif num not in open_ids.get(series, frozenset()):
                out.append(
                    f"RE-MINT: {cid!r} defines a row ({placed}), but {num} is "
                    f"at or below the frozen {series} ceiling of {ceiling} and "
                    f"is not in OPEN_IDS[{series!r}]. That number was issued "
                    f"and has retired — its row left HEAD (CLAUDE.md §Norms), "
                    f"so the collision is with HISTORY, not with a row. Take "
                    f"{ceiling + 1} instead and bump the ceiling with it.")
            continue

        seen_irregular.add(cid)
        if cid not in open_irregular:
            hint = ("" if series is None else
                    f" (if {series!r} is a new INTEGER series, give it a "
                    f"CEILINGS entry rather than listing ids one by one)")
            out.append(
                f"UNRECORDED ID: {cid!r} defines a row ({placed}) and is not "
                f"in OPEN_IRREGULAR. Either it is a fresh id that was minted "
                f"without recording itself, or it re-mints a retired one — "
                f"these series carry no ceiling, so the set cannot tell them "
                f"apart, which is exactly why it is explicit. Add it in the "
                f"minting commit{hint}.")

    for series in sorted(open_ids):
        for num in sorted(set(open_ids[series]) - seen_int.get(series, set())):
            out.append(
                f"STALE MANIFEST ENTRY: OPEN_IDS[{series!r}] lists {num}, but "
                f"no row in {' or '.join(REGISTERS)} defines {series}-{num} "
                f"any more. Delete it here in the same commit as the row: that "
                f"deletion is what makes the number permanently un-re-mintable, "
                f"and an entry that outlives its row is cover for the next "
                f"branch that re-takes it.")
    for cid in sorted(set(open_irregular) - seen_irregular):
        out.append(
            f"STALE MANIFEST ENTRY: OPEN_IRREGULAR lists {cid!r}, but no row "
            f"defines it any more. Delete it here in the same commit as the "
            f"row — that deletion is what retires the id.")
    return out


def findings(sources: dict[str, str] | None = None,
             ceilings: dict[str, int] | None = None,
             open_ids: dict[str, frozenset[int] | set[int]] | None = None,
             open_irregular: frozenset[str] | set[str] | None = None,
             ) -> tuple[list[str], dict[str, list[tuple[str, int]]]]:
    """Findings, plus the id -> [(register, line)] map for the denominator.

    `sources` overrides the on-disk registers with `{relative path: text}`.
    The self-test feeds it manufactured collisions, so the REPORTING half is
    exercised by the same code path the real run takes — not by a second
    implementation that agrees with this one by coincidence. The three
    manifest arguments override the frozen constants the same way.
    """
    out: list[str] = []
    where: dict[str, list[tuple[str, int]]] = collections.defaultdict(list)
    for rel in (sources or {rel: None for rel in REGISTERS}):
        if sources is not None:
            text = sources[rel]
        else:
            page = REPO / rel
            if not page.exists():
                out.append(f"MISSING REGISTER: {rel} does not exist -- this "
                           f"lint cannot answer the question it claims to "
                           f"answer.")
                continue
            text = page.read_text(encoding="utf-8")
        for cid, line in row_ids(text):
            where[cid].append((rel, line))

    for cid, sites in sorted(where.items()):
        if len(sites) == 1:
            continue
        registers = {rel for rel, _ in sites}
        placed = ", ".join(f"{rel}:{line}" for rel, line in sites)
        if len(registers) > 1:
            out.append(
                f"CROSS-REGISTER: {cid!r} defines a row in {len(registers)} "
                f"registers at once ({placed}). One id, one home: a QUEUE row "
                f"and a BACKLOG row wearing the same id make every "
                f"cross-reference to it ambiguous.")
        else:
            out.append(
                f"DUPLICATE: {cid!r} defines {len(sites)} rows in the same "
                f"register ({placed}). This is the EB-119/EB-120 and M38 "
                f"collision shape — two branches each took 'the next free "
                f"integer' against a HEAD showing neither the other's row.")

    out.extend(manifest_findings(
        where,
        CEILINGS if ceilings is None else ceilings,
        OPEN_IDS if open_ids is None else open_ids,
        OPEN_IRREGULAR if open_irregular is None else open_irregular))
    return out, where


def _fitted(sources: dict[str, str]) -> tuple[dict, dict, set]:
    """A manifest that exactly fits `sources`. SELF-TEST SCAFFOLDING ONLY.

    NOT a source of truth, and never called by the real run: it derives each
    ceiling from the highest id that still DEFINES a row, which is precisely
    the understatement the frozen constants exist to correct — a retired id's
    number survives in HEAD only as a citation. It is here so the uniqueness
    cases below see uniqueness findings and nothing else.
    """
    ceilings: dict[str, int] = {}
    open_ids: dict[str, set[int]] = collections.defaultdict(set)
    irregular: set[str] = set()
    for text in sources.values():
        for cid, _ in row_ids(text):
            series, num = parse(cid)
            if series is None or series in FOREIGN_SERIES:
                irregular.add(cid)
                continue
            ceilings[series] = max(ceilings.get(series, 0), num)
            open_ids[series].add(num)
    return ceilings, dict(open_ids), irregular


def _run(sources: dict[str, str], ceilings=None, open_ids=None,
         open_irregular=None) -> list[str]:
    """`findings` over synthetic registers, defaulting to a fitted manifest."""
    fit_c, fit_o, fit_i = _fitted(sources)
    bad, _ = findings(sources,
                      fit_c if ceilings is None else ceilings,
                      fit_o if open_ids is None else open_ids,
                      fit_i if open_irregular is None else open_irregular)
    return bad


def self_test() -> list[str]:
    """Prove the check BITES, on synthetic text rather than on the registers.

    A uniqueness lint that has never seen a duplicate is indistinguishable
    from one that cannot see duplicates, and the registers are (correctly)
    clean — so the only honest evidence is a manufactured collision. Each
    case below is one of the rules, plus the shapes that must NOT fire.
    """
    bad: list[str] = []

    def ids(text: str) -> list[str]:
        return [cid for cid, _ in row_ids(text)]

    dup = ids("| `EB-9` | a |\n| `EB-9` | b |")
    if dup != ["EB-9", "EB-9"]:
        bad.append(f"self-test: a duplicate id cell did not parse: {dup}")

    compound = ids("| `EB-33/34/35` | x |")
    if compound != ["EB-33", "EB-34", "EB-35"]:
        bad.append(f"self-test: compound expansion is wrong: {compound}")

    shared = ids("| `S4-G12` / `CC-G1` / `CC-G2` | x |")
    if shared != ["S4-G12", "CC-G1", "CC-G2"]:
        bad.append(f"self-test: a shared-row cell is wrong: {shared}")

    prose = ids("| Art debt | x |\n| S8 + S10 galleries | y |\n"
                "| see `EB-71` for why | z |")
    if prose:
        bad.append(f"self-test: a prose cell was read as a definition: {prose}")

    if ids("| ID | Item |\n|---|---|"):
        bad.append("self-test: a header row was read as a definition")

    # --- and the three UNIQUENESS rules, through `findings` itself ---------
    Q, B = REGISTERS

    same = _run({Q: "| `M38` | a |\n| `M38` | b |", B: ""})
    if not any(f.startswith("DUPLICATE:") and "M38" in f for f in same):
        bad.append(f"self-test: rule 1 (same-register duplicate) did not "
                   f"fire: {same}")

    both = _run({Q: "", B: "| `EB-119` | a |\n| `EB-119` | b |"})
    if not any(f.startswith("DUPLICATE:") and "EB-119" in f for f in both):
        bad.append(f"self-test: rule 2 (same-register duplicate) did not "
                   f"fire: {both}")

    cross = _run({Q: "| `EB-9` | a |", B: "| `EB-9` | b |"})
    if not any(f.startswith("CROSS-REGISTER:") for f in cross):
        bad.append(f"self-test: rule 3 (cross-register) did not fire: {cross}")

    clean, seen = findings({Q: "| `M38` | a |", B: "| `EB-119` | b |"},
                           *_fitted({Q: "| `M38` | a |",
                                     B: "| `EB-119` | b |"}))
    if clean or sorted(seen) != ["EB-119", "M38"]:
        bad.append(f"self-test: a CLEAN pair produced findings {clean} / "
                   f"{sorted(seen)} -- the check fires on healthy registers")

    # A compound row must not collide with itself, and MUST collide with a
    # sibling that re-mints one of its members. Both halves, because the
    # expansion is the one place a merged row can hide a duplicate.
    merged = _run({Q: "", B: "| `EB-33/34/35` | a |"})
    if merged:
        bad.append(f"self-test: a merged row collided with itself: {merged}")
    reminted = _run({Q: "", B: "| `EB-33/34/35` | a |\n| `EB-34` | b |"})
    if not any("EB-34" in f for f in reminted):
        bad.append(f"self-test: a re-minted member of a merged row was "
                   f"missed: {reminted}")

    # --- and the MANIFEST rules, each against a manufactured retirement ----
    # The shape that motivated the row: EB-53's row has closed and left HEAD,
    # so a branch re-taking 53 sees no collision anywhere in the tree.
    retired = _run({Q: "", B: "| `EB-53` | re-taken |"},
                   ceilings={"EB": 137}, open_ids={"EB": set()},
                   open_irregular=set())
    if not any(f.startswith("RE-MINT:") and "EB-53" in f for f in retired):
        bad.append(f"self-test: rule 5 (re-minted RETIRED id) did not fire — "
                   f"this is the failure EB-127 was filed about: {retired}")

    unbumped = _run({Q: "", B: "| `EB-138` | fresh |"},
                    ceilings={"EB": 137}, open_ids={"EB": {138}},
                    open_irregular=set())
    if not any(f.startswith("UNRECORDED MINT:") for f in unbumped):
        bad.append(f"self-test: rule 4 (mint above an un-bumped ceiling) did "
                   f"not fire: {unbumped}")

    bumped = _run({Q: "", B: "| `EB-138` | fresh |"},
                  ceilings={"EB": 138}, open_ids={"EB": {138}},
                  open_irregular=set())
    if bumped:
        bad.append(f"self-test: a fresh mint WITH its ceiling bump and its "
                   f"manifest entry was refused: {bumped}")

    stale = _run({Q: "", B: "| `EB-138` | fresh |"},
                 ceilings={"EB": 138}, open_ids={"EB": {99, 138}},
                 open_irregular=set())
    if not any(f.startswith("STALE MANIFEST ENTRY:") and "99" in f
               for f in stale):
        bad.append(f"self-test: rule 6 (a manifest entry that outlived its "
                   f"row) did not fire: {stale}")

    irregular = _run({Q: "| `S4-G6` | live |\n| `S4-G7` | re-taken |", B: ""},
                     ceilings={}, open_ids={}, open_irregular={"S4-G6"})
    if not any(f.startswith("UNRECORDED ID:") and "S4-G7" in f
               for f in irregular):
        bad.append(f"self-test: an unrecorded irregular id was accepted: "
                   f"{irregular}")

    irregular_stale = _run({Q: "| `S4-G6` | live |", B: ""},
                           ceilings={}, open_ids={},
                           open_irregular={"S4-G6", "S4-G7"})
    if not any(f.startswith("STALE MANIFEST ENTRY:") and "S4-G7" in f
               for f in irregular_stale):
        bad.append(f"self-test: a stale irregular entry was accepted: "
                   f"{irregular_stale}")

    foreign = _run({Q: "", B: "| `R209` | a ruling as a row |"},
                   ceilings={}, open_ids={}, open_irregular=set())
    if not any(f.startswith("FOREIGN SERIES:") for f in foreign):
        bad.append(f"self-test: a row defining an R-number — guarded by "
                   f"neither this lint nor lint_r_numbers — was accepted: "
                   f"{foreign}")

    fitting = _run({Q: "| `M10` | a |",
                    B: "| `EB-1` | b |\n| `S4-G6` | c |"})
    if fitting:
        bad.append(f"self-test: a manifest that exactly fits its registers "
                   f"produced findings: {fitting}")
    return bad


SELF_TEST_CASES = 19


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        bad = self_test()
        for line in bad:
            print(line)
        print(f"self-test: {SELF_TEST_CASES} case(s), {len(bad)} failure(s)")
        return 1 if bad else 0

    bad, where = findings()
    for line in bad:
        print(line)
    per_register = collections.Counter(
        rel for sites in where.values() for rel, _ in sites)
    scope = ", ".join(f"{rel} {per_register[rel]}" for rel in REGISTERS)
    print(f"scope: {len(where)} distinct id(s) defined across "
          f"{len(REGISTERS)} register(s) -- {scope}")
    manifest = "; ".join(
        f"{series} ceiling {CEILINGS[series]}, "
        f"{len(OPEN_IDS.get(series, ()))} open"
        for series in sorted(CEILINGS))
    print(f"manifest: {manifest}; {len(OPEN_IRREGULAR)} irregular id(s)")
    if not where:
        # lint_strict_domination's rule: a sweep that compared nothing must
        # not read like a clean one.
        print("VACUOUS: no row ids were found at all. The registers moved, or "
              "the row shape did; this lint is reporting nothing, not health.")
        return 1
    if bad:
        print(f"\n{len(bad)} finding(s). One id defines one row, once ever: "
              f"a number at or below its ceiling that is not in the manifest "
              f"has RETIRED, and closed rows leave HEAD, so nothing else in "
              f"the tree would have caught you re-taking it.")
        return 1
    print("register-ids OK: every row id defines exactly one row, no id is "
          "defined in both registers, and every defined id is a live entry in "
          "the issued-id manifest — no retired number re-minted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
