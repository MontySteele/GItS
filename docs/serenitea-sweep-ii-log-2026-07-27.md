# Serenitea Sweep II — quick clearance (2026-07-27)

One session. Every track landed. Suite green on a bare clone after each.

**Standing discipline this sprint ran under:** R68 stamps, module-alias
imports, bite-check every new pin, grades before review — plus **D4**, recorded
first, which then caught its own first live case before the sprint ended.

---

## Landing order, as executed

| # | Item | Commit |
|---|---|---|
| 0 | D4 ledger entry + B1 CI adopted (pulled forward) | `602383c` |
| 1 | Kokomi `neap-tide-v2.1` merge | `4810f3a` |
| 2 | Track A — F2 Harmony bootstrap | `2dfd97c` |
| 3 | B3 + B4 + E | `5f49387` |
| 4 | Track C — C1–C4 | `0e21d43` |
| 5 | D1 — art-queue registration | `2043fec` |
| 6 | B2 doc + the C6 twins | `8c3374e` |

Gate run after every track (`GITS_REFERENCE_MODE=committed-only`, the bare-clone
path a GitHub runner takes on its own): pytest + 7 lints + ledger = **9/9
green**, every time.

---

## D4 — recorded first, and it bit the same day

> A pre-registered prediction must name its instrument, and registration must
> confirm the instrument models the changed object. C#-only changes get
> C#-side verification, never sim predictions. Any quantitative claim used as
> rationale carries a measurement or is marked UNMEASURED.

Origin was two Sweep-I failures with one root: Track D registered three
predictions against the canonical tier-0.5 cell, two of which were C#-only and
therefore unmeasurable by it (one graded FAILED, one graded VACUOUSLY MET,
neither grade carrying information); and C6, where an unmeasured claim served
as R70 design rationale for a file's whole life.

**Clause 3 fired within the sprint.** See "The C6 claim had two twins" below.

---

## Pre-flight — the Kokomi merge

**CI first.** `serenitea-g3-ci.yml` → `.github/workflows/repo.yml` before the
merge, deliberately: the branch was developed in parallel and had never met
Sweep I's gates, so its merge should be the first thing CI checks.

**The merge was CLEAN — zero conflicts**, against an expectation of "messy".
Topology explains it and the expectation was simply wrong: PR #7 merged this
branch at `b539860`, `main` added nothing but that merge commit, and the six
new commits sit directly on `b539860`. There was nothing on `main` to conflict
with.

Gates on the merged tree: **1043 passed, 20 skipped** (984 at Sweep I), 7/7
lints, 0 ledger duplicates. **No findings.** The good outcome rather than the
suspicious one — the branch carries its own tests, and the +59 net is mostly
those.

The merge did, however, invalidate a prepared artifact. See B3.

---

## Track A — F2, the headline

`harmony.PatchAll(assembly)` walks patch classes in reflection order and
abandons the walk at the first one that throws. Every patch after that never
armed, and the single try/catch logged one line naming the patch that threw —
never the ones that consequently went missing. Two of this assembly's patches
are softlock guards, and reflection order is neither source order nor stable.

Replaced with per-type patching: each class through its own
`CreateClassProcessor` in its own try/catch, then a report.

- **armed** — patched ≥1 method, every lookup resolved
- **DEGRADED** (warn) — patched ≥1 method but named lookups died
- **FAILED** (error) — patched *nothing*, whether it threw or silently matched
  nothing

A failure prints a banner, one line per casualty naming the class **and its
declared target**, and the consequence. Harmony's own message for a dead
class-level target is `Patching exception in method null` — it cannot name what
it failed to find — so the target is read back off the `[HarmonyPatch]`
attribute. If a casualty is one of the four softlock guards, the report says so
and tells the operator not to playtest that build.

Same visit, per the pinned `CreatureFacing` pattern: both `TargetMethods`
bodies resolve through the bootstrap (dead lookups recorded by name);
`MerchantCompanionSlots.cs:61`'s `AccessTools.FieldRefAccess` moved out of a
static field initializer — it *throws*, so a renamed private field became a
`TypeInitializationException` at first use, and first use was a player walking
into a shop; `SoftlockGuards` entries are all `nameof`, so an entry cannot
outlive the class it guards.

### The bite-check, and what it caught

`klee-mod/build/bitecheck/` loads the built `klee.dll` **outside Godot** and
runs the real bootstrap. This works because `sts2.dll` is a plain `net9.0`
assembly — Harmony patches its methods with no scene tree and no native Godot
runtime. All 14 classes arm there exactly as in game. The harness redirects the
game's `Log` to stdout using the very mechanism under test.

| Break | Expected | Observed |
|---|---|---|
| baseline | 14 armed, silent | as expected |
| class-level target renamed | 13 armed, 1 FAILED named + guard escalation | as expected |
| 1 of 2 `TargetMethods` renamed | 14 armed, 1 DEGRADED naming the dead lookup | as expected |
| both `TargetMethods` renamed | 13 armed, 1 FAILED listing both + escalation | as expected |

**It earned its place on first use.** The failure report originally carried the
class name by string-splitting its own rendered line on `:`. Adding the patch
target to that line silently broke softlock-guard escalation — the escalation
line just vanished. The pins could not have caught that; the harness did, on
the first run after the change. Fixed by keeping the name and the rendered line
as separate fields.

**Automated half:** `tier0/tests/test_harmony_bootstrap_contract.py`, 6 rules,
each bite-checked by reintroducing its defect.

**Still owed:** an in-game boot. The harness proves the bootstrap arms and
reports correctly against the real assembly; only a play session proves the log
lands where an operator reads it.

---

## Track B

### B1 — CI adopted

All three jobs, ledger check included. The file's "DRAFTED, NOT ENABLED" banner
would have been false the moment it moved, so it now records the adoption and
points at the NOT-doing list.

**Owed by [USER]:** set the three jobs as required checks on `main`. That is
branch protection, a GitHub setting, not a file here — and B2 rule 3 depends
on it.

### B3 — the sheet pass, regenerated, and why that mattered

The prepared patch was verified against the **pre-merge** tree. The merge
rewrote `kokomi-cards.yaml`, so it was re-checked rather than trusted: 5 of 6
files still applied unchanged; kokomi's hunks were regenerated. 9 of 11 kokomi
hunks still applied (by offset, context matching exactly — no fuzz); 2 rejects
were re-derived, along with **11 further findings** on rows the branch had
added or rewritten that had never seen the pass.

**The finding, and the argument for the freshness rule.**
`scattering_spray`'s comment reads *"less than surging_shoal's 7"*. R77 moved
`surging_shoal` 7 → 6 on the merged branch. The prepared patch would have
appended `(lint-ok: sibling card's number)` to that line — stamping "this
number is correct and belongs to another row" onto a number that is no longer
either. **A marker on a stale number is worse than no marker**, because it
certifies the staleness and closes the lint that would have caught it.

Corrected to 6 (the argument survives: the card is 5, the shoal is 6), then
marked. **This is a second number correction beyond the countersigned patch**,
which covered only `depths_judgment` — flagged for red pen. It is the same
operation the countersign already approved once, and the Kokomi branch itself
performed exactly this correction on `vow_of_tides` two rows earlier, but the
countersign predates it.

The other 12 were markers with per-line reasons: supersession records, upgrade
values, worked arithmetic at a superseded value, sibling numbers, a
quoted-and-corrected note, a quoted dead justification, and twice the literal
"LAW 5" read as the number 5.

All six sheets CLEAN, 11 tests. Patch deleted rather than archived — it no
longer describes what landed, and git history holds the original.

### B4 — the always-firing gate now says why

Sweep-I E2 measured all three Furina A2 bands low in the same direction (salon
9.04 vs 7.6, fanfare 5.69 vs 4.2, spotlight 4.90 vs 4.3). Under D3 those are
reportable but not load-bearing, so **no band moved**. What was fixed is the
flag, which fired on every Furina run:

```
BAND EXCEEDED: A2_scaling 9.4 > 7.6 for salon_weighted
               (known-stale band; re-ratify at axis-validity session)
```

Verified end-to-end via `score_config`, not by reading the code. A new
`stale_bands` key carries the reason beside the band; band values are
byte-identical. `test_stale_band_annotations` fails if an annotation outlives
the band it names, both rules bite-checked.

### B2 — worktree policy

`docs/worktree-workflow.md` is the operating doc. Five rules: one worktree per
workstream; branch naming; PR-to-`main` with `repo` as a required check; stage
explicitly, never `git add -A`; never link a gitignored asset dir into a
worktree.

Rule 4 was **promoted, not copied**: G4 proposed explicit staging as the
fallback for *not* adopting worktrees, but the art-bearing main checkout stays
more convenient for `build_pck`, `deploy` and art passes, so the shared tree
keeps being used and rule 4 is what makes that survivable.

**The transition is NOT executed.** It requires every session closed and the
tree clean, and this session is a session; running it from inside the tree
being split is the exact risk the protocol exists to avoid. Left for [USER] to
run once, quietly, per the doc.

---

## Track C

- **C1** `ReplaceFirst<TBasic>` matches exactly. `is` matches any subclass; the
  contract is "find the authored basic". No subclasses exist today — the shape
  was wrong, not the behaviour.
- **C2** the reward-draw clamp gates on our roster. It was self-limiting *by
  argument* — a claim about six pools this mod does not own. Added
  `CompanionPool.IsRosterCharacter` as the general name, with
  `HostsCompanions` delegating: a gate named for one of its two callers is how
  a reader concludes the other caller is a mistake.
- **C3** `SpotlightSystem.PendingDraws` no longer outlives its combat.
  Deliberately **not** BombPower's idiom verbatim: that keeps one shared
  `ICombatState` token, and the state reachable here is `PlayerCombatState`,
  which is *per player* — a single token would make each co-op partner's play
  clear the other's pending draw, trading a leak for a dropped card. Generation
  is recorded and checked per entry instead.
- **C4** `KleePlaceholderArt` → `KleeAssetPathFallback`. Reconciled, not
  deleted.

### C4's reconciliation

The header said the file would be deleted when the art pass landed a real pck.
The art pass landed, `has_pck` is **true**, and the file is still load-bearing
two ways, both verified:

1. Klee, Furina and Kokomi override the **same 13** `Custom*Path` properties.
   The four arm textures and five FMOD events are overridden by nobody. For
   Klee this postfix is their only source of a valid path.
2. `KleePck.Path` returns **null** for a missing resource and BaseLib then
   falls back to the id-derived base getter — the path that does not exist. So
   a stale pck lands back on this postfix instead of on the select-screen
   crash O6 records.

**The count is 9, not 8.** The 2026-07-26 audit and this sprint's brief both
say "8 asset paths"; counted at the source it is 4 arms + 5 sfx. Corrected in
the header rather than repeated (D4 clause 3).

**Open asymmetry, registered not acted on.** The gap in (1) is roster-wide and
the rewrite is gated on `is Klee`, so **Furina and Kokomi have no fallback for
those 9 paths.** Not extended: redirecting a shipped character's arm textures
and combat SFX to Ironclad's is an audible, visible change to two characters,
and it would mask the stale-pck warning `KleePck.Path` already logs. Whether
the gap manifests in play is **UNMEASURED**. [USER] to rule.

Renamed because "PlaceholderArt" predicts its own deletion, and that is how a
live safety net gets removed by someone tidying up.

---

## Track D1 — two registries, two different facts

[USER] ruled kaboom keeps "Klee Character Card"; `spark_knight_style` re-hunts.
Its plan row is commented out with the ruling, following the `pop` precedent.

- **`PENDING_RED_PEN` — removed.** It recorded a *plan* collision: two rows
  wanting one source. With the row commented, exactly one card claims it, so
  the collision is gone and a surviving entry would suppress a finding that can
  no longer occur. Confirmed by running the lint: that L1 line is gone.
- **`KNOWN_IDENTICAL` — kept, cross-referenced.** It records *shipped pixels*,
  still byte-identical until someone re-crops.

Removal is **automatic, not remembered**: when new art lands,
`test_every_allowlisted_identical_pair_is_still_identical` fails on the pair
and the entry has to come out. An exemption outliving its reason is the B6
lesson, and the answer is a test that breaks, not a note asking someone to
check.

**One claim corrected before it shipped.** The first draft of the plan note
said `spark_knight_style` would now show under MISSING ART, by analogy with
`pop`. Measured instead: it does **not**. `pop` never had a shipped file;
this one's PNG is already on disk, so `art_coverage` still counts it covered
(263/267 before and after). The card keeps rendering the old crop until the
rehunt; the debt stays visible through L12 rather than the coverage bill.

---

## Track E — `aria_of_recompense`: RULED (a), keep as shipped

5→8 **and** innate; the encore delta is not traded for the Innate. The upgrade
sheet's "no equivalent ruling ever made here" flag is closed — the equivalent
ruling is this one, and it went the other way from `kurages_oath` deliberately
(a basic is in every deck, so it is a campfire decision; the Oath is a draft
lottery, where innate-only is the conservative read).

The registered-but-not-scheduled revisit and its candidate two-card shape are
recorded on the row, so a later reader can tell "considered and kept" from
"never looked at".

---

## The C6 claim had two twins — D4 clause 3's first live case

Sweep-I C6 deleted an unmeasured claim from `validate.ps1`: that the gate
"cannot be run quickly (S7's `game_ref` verification takes minutes)", when that
verification is **0.17s of an 84.0s run** and the cost is the pytest suite.

The same sentence was still alive in two other files, found by *running* the
gate rather than reading about it:

- **`klee-mod/build/version.ps1`** — the file the extraction C6 was correcting
  actually produced, still giving the false claim as the reason for its own
  existence.
- **`tier0/tests/test_manifest_version_gate.py`** — same sentence, module
  docstring.

C6 corrected the claim where it was found and pinned it where it was found.
`test_the_false_stall_claim_is_gone` reads `validate.ps1` **and only
`validate.ps1`**, so the copies the extraction had already spawned were never
in scope — a corrected claim sat one directory from its uncorrected twins for a
month.

Both corrected. The pin now follows the **claim**, not the file someone first
noticed it in: it checks all three carriers and treats "sentence present with
no correction in the file" as the failure, so a correcting note can still quote
the sentence in order to strike it. Bite-checked.

---

## State at close

- **Build:** Debug and Release, 0 errors, 15 warnings (unchanged from before
  the sprint). Bootstrap arms 14/14 against both DLLs.
- **Suite:** 1043 passed / 20 skipped on a bare clone, plus this sprint's new
  pins.
- **Lints:** 7/7. `art_lint` exit 0. `validate.ps1` and `version.ps1` parse
  clean and are pure ASCII (S8).
- **Tree is deploy-ready.** Deploying is [USER]'s, and the fresh deploy should
  follow promptly — the per-owner detonation fix and the conscript soft-lock
  fix are both waiting in it.

### Owed, explicitly

1. **Push + PRs.** `gh` is not installed on this machine, so no PR could be
   opened and no GitHub run observed. The work sits on local branch
   `serenitea-sweep-ii`. The three CI jobs were emulated locally on the exact
   bare-clone path a runner takes, green after every track — but "green on
   GitHub" is unverified by construction.
2. **Branch protection** — required checks on `main` (B1/B2 rule 3).
3. **The B2 worktree transition** — sessions closed, tree clean, then split.
4. **An in-game boot** for F2's log surface.
5. **Red pen** on B3's second number correction (`scattering_spray` 7 → 6).
6. **A ruling** on C4's Furina/Kokomi 9-path asymmetry.

### Not touched, by instruction

F3 (codegen driver unification) and F4 (engine chokepoint extraction) remain
rolled forward, in that order. No band or axis number moved. `_static_power`
untouched. The Kokomi pool sweep and the actual Spark Knight Style re-crop are
both out of scope.

One thing noticed in passing, not acted on: `art_coverage` bills **4 missing**
card portraits, all Kokomi's, all arriving with the merge — `ebb_tide`,
`salt_line`, `before_sun_and_moon`, `undertow`. That is the Track D art debt
the Neap Tide sprint already recorded, not a new finding.

---

## Addendum — D5, added at merge (2026-07-27)

Recorded after the sprint body was written, on [USER] amendment, and merged to
`main` with it: **D5 — Kokomi stability band: provenance and schedule.**

E1 (Sweep I) built `stability_profile` dark, under a blind-declaration gate:
the acceptance band on record *before* any playtest HP data was reviewed. HP
data was reviewed during the Kokomi playtest sprint on the feature branch, so
that gate is no longer satisfiable. D5 rules the recovery rather than pretending
otherwise — the observed playtest is **EXPLORATORY** and grades nothing; the
band is declared from **design intent**, informed by those observations and
recorded as such; declaration comes **before** the post-rework confirmatory
playtest, which grades it; and **the band may not be revised against the
playtest that grades it.**

That last clause is the part of the original gate that survives intact: the
band stays blind with respect to the measurement that judges it. It is also a
D4 instrument statement — the confirmatory playtest is the named instrument,
and the exploratory one is named as explicitly not it.

Amended in the two places the blind wording is read (`tier05/run_metrics.py`,
`tier0/tests/test_stability_band.py`); the Sweep-I log's account is left as
written, because it was true on its date. `band is None` stays pinned.

**This adds a seventh owed item:** the band declaration itself, which is a
[USER] design ruling and is now on the critical path for the Kokomi
confirmatory playtest — nothing can grade until it exists.
