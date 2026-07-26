# "Serenitea Sweep" — tech-debt clearance, landing log (opened 2026-07-26)

Running record for the sprint doc of the same name. Governing inputs:
`docs/tech-debt-audit-2026-07-26.md`, `docs/missed-requirements.md`,
`tier0/DECISIONS.md` R66–R72 + D3, `docs/epoch-1-log-2026-07-26.md`.

Standing discipline, every track: R68 stamp lines on any cited run;
KNOB_READS gate on any sweep; module-alias constant imports only; no sheet
edits outside Track G; predictions graded in writing before any other output
of the same landing is reviewed.

**Epoch numbering.** This sprint's stamped landing is EPOCH 2 (Track D). The
deferred `_static_power` repricing (DRAFTER 11) takes the next integer when
its design session rules — epoch integers are assigned at landing time, never
reserved.

---

## Track A — Fresh-clone green — LANDED

Standalone commit, ahead of every other track, because it is the gate the
later tracks are verified against.

### A1 — `test_stale_file_is_not_counted_as_coverage`

Seeded a COVERED probe alongside the stale probe. The test's negative
assertions ("the covered list does not name the stale probe") were being
evaluated against a list that is empty on any tree without art — a vacuous
assertion wearing a real one's clothes, which is why the module went red on a
bare clone at `assert covered_lines, "report printed no covered list"`.

The covered probe's id is **read from a canonical companion sheet**, not
written as a literal — a literal here would reproduce
`test_bill_is_derived_from_canonical_sheets`'s own failure mode one level up.
It is written only if that path is currently unoccupied and removed only if
this test wrote it, so on a machine that holds the real portrait an
eyes-on-approved file is never overwritten.

Verified in both directions on a real `git clone --depth 1`:

- **pre-fix, no art:** `FAILED ... assert [] :: report printed no covered list`
- **post-fix, no art:** passes
- **post-fix, stale counted as coverage** (mutated `art_coverage.py` to print
  every present stem as `have:`): `FAILED ... assert all(stale.stem not in ln ...)`

### A2 — Sibling audit, bounded — **0 further instances; the third-instance rule does NOT fire**

Nine suite modules reference a gitignored path. Classification:

| Count | Class | Modules |
|---|---|---|
| 1 | Unguarded, fails on a bare clone | `test_art_coverage` — the A1 subject |
| **0** | **Further unguarded siblings** | — |
| 5 | Correctly guarded (`skipif` on the artifact, or monkeypatched onto `tmp_path`) | `test_char_stills`, `test_ironclad_upgrades`, `test_real_ironclad`, `test_measurement_world_digest`, `test_anchor_lock` |
| 1 | Path strings are synthetic fixture data; no filesystem read | `test_art_lint_source_group` |
| 2 | Prose/docstring mention only | `test_manifest_version_gate`, `test_art_coverage` header |

`test_anchor_lock` deserves naming as the *correct* pattern rather than as a
finding: it monkeypatches the absence of `game_ref/` and asserts on it, so a
bare clone is the case under test rather than the case that breaks it.

**Noted, not fixed, out of A2's bounded scope** (a weaker class, recorded so
it is not re-discovered as new): `test_local_reference_mode` asserts that
committed-only mode does *not* see `game_ref/`. Its pass/fail is
machine-independent — it never goes red on a bare clone — but on a tree
without `game_ref/` it is vacuously true and carries no evidence. That is
"the assertion is empty here", not "the test reports the machine". If a
third instance of the *A1* class ever appears, the fix is the lint the sprint
doc specifies (a fixture running collection against a simulated bare clone),
not a third spot repair.

### A3 — archived-tool importability — 2 files, not 1

`tools/archive/banner_variance_cells.py` computed repo root as
`Path(__file__).resolve().parent.parent`. That was correct in `tools/`; after
the audit moved it into `tools/archive/` it lands on `tools/` and the module
is unimportable.

The bounded sweep found the **same defect in `render_card_gallery.py`**,
archived in the same commit, with an extra hop: its second `sys.path.insert`
pointed at the script's own directory to reach `art_fetch`, which stayed in
`tools/`. Both fixed to `parents[2]`; the gallery's second insert now points
at `ROOT / "tools"`. Both verified to import.

This is instance 2 of the *archiving* class (distinct from A2's
"reports the machine" class); at instance 3 it should become a lint that
imports every module under `tools/archive/`.

### A4 — orphan comment fragment

`tier0/constants.py` carried a dangling trailing-comment continuation
(`# fraction, otherwise remove a card`) on its own line under
`REST_PREFIGHT_HEAL_THRESHOLD`, left behind when its owning constant was
deleted. Deleted. (The audit cites it at `:563`; R67/R71 have since moved it
to `:579`.)

### Exit gate — MET

`git clone --depth 1` of the working branch, no art, no `.venv` in the tree:

```
871 passed, 21 skipped in 77.35s
```

Same tree on the art-present development machine: `892 passed`. The 21-test
delta is exactly the artifact-gated set, which is the guarded class behaving
as designed.

---

## Track B — Pin batch — LANDED

Tests only. The one behavioural edit in this commit is C5's helper, landed
early and flagged below, because B4's lint has nothing to enforce without it.

Suite: 892 -> 973 (+81). Every pin below was verified to BITE by mutating the
source it guards and confirming red, then reverting — a pin that has never
been seen to fail is a pin nobody has tested.

### B1 — reaction phase parity x3 (`test_reaction_phase_parity.py`, 10 tests)

Taken as the **curated step-to-hook ledger**, the implementer's-choice option,
rather than three bespoke pins: each row is a phase decision with the measured
divergence that paid for it recorded beside it, so adding a row means a new
decision was made and deleting one means it was reversed.

| decision | receipt |
|---|---|
| Superconduct's Vulnerable multiplier rides `ModifyDamageMultiplicative` | card-triggered Superconduct dealt 10 where the sim dealt 15, while the same reaction off a bomb dealt 15 — one reaction, two payouts |
| Shatter is dealt from `AfterDamageReceived`, Unblockable + Unpowered, no dealer, no card source | as `ModifyDamageAdditive` it scaled with Vulnerable AND was absorbed by Block. Frozen + Vulnerable 2 on a 10-damage attack: sim 21, game 24. Into 12 Block: sim 6, game 4 |
| aura tick on `AfterSideTurnStart(Player)` | ticking in `AfterSideTurnEnd(Enemy)` expired the aura before the start-of-turn detonation could react with it — a Hydro aura + a bomb lost its Vaporize |

The second half of each row is the one that matters: **the token must appear in
no sibling hook**. A revert that moves code to the adjacent override keeps
every S6e constant green, so "must appear here" alone is half a pin.

*Bite check:* renaming `AfterSideTurnStart` to `AfterSideTurnEnd` turned 3 red.

### B2 — NextAttackUpPower series consumption (`test_next_attack_up_series.py`, 8)

Both engines. The tier0 half is **executable** — a real OneTwoPunch series is
played through `combat.play_card` and the payout counted — because the pop
happens in `resolve_card` and there is something to run. The C# half is
source-text: `CardPlay.IsFirstInSeries` lives in a compiled Godot run.

The line both engines draw, now stated in one place: a SERIES is the replay
loop (bonus pays once); a TAIL is `repeat_this` (bonus rides every repetition,
because `current_attack_bonus` is already snapshotted). Both directions pinned.

Also pinned: the `.get()` siblings (`attack_up_this_turn`,
`zero_cost_attacks_up`) survive the same play. That is what makes the pop
load-bearing rather than incidental, and it is what a future "tidy the
summation" edit would break.

*Bite check:* `pop` to `get` in `effects.py` turned 4 red.

### B3 — CreatureFacing (`test_creature_facing_contract.py`, 9)

Promoted from a single `Log.Warn`. Four decisions, all taken against a
decompile of a game that has **no facing concept at all**, so there is no
upstream signal to check against and nothing to execute.

`%Facing` not `Visuals.Scale` (NCreature owns that one; `UpdateBounds` reads it
back to place the hitbox — a gameplay bug wearing a visual bug's clothes);
`%Facing` not `%Rig` (the rig carries the lunge in its own position track, so
mirroring it moonwalks); prefix `AttackCommand.Execute` not the damage funnel
(which flips at impact, after the lunge); aim at the MEAN of the targets, since
a fully-centered encounter is exactly where an AoE spans both sides.

*Bite check found a hole in my own pin.* Mutating the mirror to
`Visuals.Scale` fired only 1 of the 2 tests that should have caught it: the
realistic revert writes through the **local** (`visuals.Scale = ...`), which a
check spelled against the property name misses. Restated as "the only `.Scale`
assignment in the file is the facing node's". Both tests now fire.

### B4 — Invoke-RepoPython convention (`test_repo_python_convention.py`, 15)

Scoped to all four shipped `.ps1` files, not the two with call sites today —
`deploy.ps1` and `version.ps1` are in scope precisely so the first native call
added to them has to answer to this.

Four assertions: no `& $exe` outside a helper body; no `2>&1` outside a helper
body; no bare `python`/`python3` invocation (string bodies exempt — the S7
failure message legitimately *tells an operator* to run
`python -m tools.extract_base_game_pool`, and instructing a human is not
invoking an interpreter); and the helper actually lowers EAP and restores it in
a `finally`.

That last one is the anti-vacuum guard, and it earned its keep immediately: it
rejected build_pck's thin `Invoke-RepoPython` wrapper until the check learned
that a helper may either do the swap itself **or** delegate to a sibling that
does — but never redirect without swapping, which would look like the
convention while re-arming the trap.

Also B4: the comment at `validate.ps1:573` (audit cites `:555`) read
"No 2>&1 (same PS 5.1 NativeCommandError reason as S6)" directly above a
helper call that does exactly that. It was written for the bare call site the
helper replaced. Corrected, with the reason it was wrong.

**C5 landed here** (Track C item, out of order by necessity): `build_pck.ps1`'s
three call sites — the Pillow re-encode and both MegaDot invocations — onto
`Invoke-NativeCaptured` / `Invoke-RepoPython`. Both scripts still parse clean
under PS 5.1 and both are still pure ASCII (build_pck's own header requires it).

*Bite check:* restoring the bare `& $MegaDot ... 2>&1` turned 2 red.

### B5 — Crackle+ printed text (`test_roster_codegen.py`, +1, joins its 24 siblings)

The card's semantics are pinned twice and its **sentence** never — and the
sentence is the only place a player learns that an empty hand pays nothing,
which is the whole R10 replacement design.

Pinning the sentence alone would have been the shallow version. The `1` in
"gain 1 Spark per card discarded" is a **literal** where every other number on
the face is a bound `{Var:diff()}` token, and it is correct for exactly one
reason: R36 moved `Discards` and `Sparks` by the same delta, so
`Math.Min(Sparks, picked.Count)` always equals the cards actually discarded.
So the pin asserts the sentence AND the two invariants holding it up — both
`UpgradeValueBy(1m)` calls, and the `Min` clamp. Bump one var without the
other and the text starts lying with every lint green; now it fails instead.

### B6 — two visual contracts (`test_visual_contract_gaps.py`, 7)

Both are missed-requirements items whose fix is design/asset work, not a test,
so these are **curated known-gap ledgers**: the settled arithmetic is pinned
hard, and the gap is listed with its receipt in a form that fails in BOTH
directions.

- **sec.4.2, outline != fill icon.** All three characters return the fill
  `char_icon.png` for `CustomIconOutlineTexturePath`; the manifest billed two
  assets and one was made. The ledger flips to ENFORCING per character the day
  its entry is deleted, and fails if an entry outlives its own fix.
- **sec.4.3, salon member sprite scale.** Pinned what is settled: the stage
  geometry is uniform across all three slots, the ghost is 34x36 and the pitch
  62px (the figures the write-up quotes, so scene and doc cannot drift apart
  silently), and `TARGET_H = 144` is exactly 2x the 72px beam — that ratio IS
  the intended runtime scale of 0.5, and it is stated nowhere else but a
  sentence in the cut tool. The bridge sets Texture/Visible/Modulate and no
  `Scale`; the test asserts that and **is written to fail the day a `Scale`
  appears**, with the arithmetic that should replace it in the failure message.

`TARGET_H` is read from the tool source, not from `members.json` — that file is
gitignored Tier F output, and Track A's lesson is that an assertion anchored on
an ungenerable artifact reports the machine.

### B7 — content-boundary allowlists (`test_content_boundaries.py`, 18)

The audit's inversion, closed: the two smallest content files validated loudly
while the two largest read every key through `.get()`.

- **Sheet `op:` / `if:` validated at LOAD.** Both raises already existed in
  `_resolve_effects` and `_predicate`; this moves them from play time to load
  time. Valid content is unaffected — all 367 cards pass — and the only thing
  that moves is *when* a typo is reported. For a rare card, play time means in
  front of a player, and on the co-op seat there is no sim backstop at all.
  Validation recurses into `then`/`else`, since an unreachable-today branch is
  where a typo survives longest.
- The predicate vocabulary needed to be **enumerable** for that, and
  `_predicate` is an if-chain whose per-branch prose is worth keeping. So the
  chain stays and `PREDICATE_NAMES` / `PREDICATE_PREFIXES` mirror it — with a
  test that parses the chain and compares both directions, so the mirror
  cannot rot into rejecting legitimate cards.
- Parameterised predicates now check their argument: `fanfare_at_least_ten`
  used to pass a name check and die in `int()` mid-combat.
- **events.yaml and the three act pools** get allowlists on the `potions.py`
  pattern. The audit's own example is now loud: `is_bos: true` raises instead
  of silently making a non-boss boss.
- Every allowlist is checked in the rot direction too — a key the allowlist
  carries that the reader never consumes IS the silent no-op being guarded
  against. (`card_screens` is the one sanctioned spare: documented grammar the
  reader honours, used by no shipped event yet.)

### B8 — sec.2.2 mechanical repairs ONLY (`test_axes_honesty.py`, 13)

**The scorecard invariants stay PULLED per D3**, and the test file says so at
the top and carries a scope guard at the bottom, so reinstating them requires
deleting a test — which requires reading why it is there.

Three repairs, each removing a number the instrument had not measured:

1. **Zero-baseline anchor.** `max(eps, b)` with eps = 1e-9 was not a guard, it
   was a silent substitution: a zero baseline turned any nonzero raw into
   ~1e9, which `SCORE_CAP` clamped to a clean-looking **10.0**. "Best possible"
   and "unmeasurable" were the same output. Now raises. Applied to A7's
   inversion too, where the divisor is the RAW value — otherwise exactly one
   axis could still print a free 10.0. A6's application term stays exempt by
   construction: its baseline IS zero, which is why R18 anchored it additively.
2. **Named encounter pools.** `.get("attrition", pooled)` made a missing or
   renamed id a whole-battery average — the axis printed a number for a
   different quantity, while `runner.score_config` two files over indexes
   `stats["attrition"]` and raises. Now both raise. An *empty* named pool
   counts as missing, which the old `.get()` never caught at all: the key
   existed, so the fallback never fired and the axis averaged `[]` to 0.0.
   `battery=False` exists for genuinely synthetic single-encounter callers and
   must be written at the call site (one test updated to declare it).
3. **The `or 1.0` turn-10 default.** Zero turn-10 samples became A2 = 1.0,
   which against a baseline that also read 1.0 printed exactly **3.0**:
   average scaling, from nothing on either side. Now zero samples read 0.0 and
   `A2_samples` rides in the raw dict so every report can see the denominator.

Repairs 1 and 3 compose, which is where the old silence lived: a baseline with
no turn-10 fight now raises rather than printing 3.0.

**Zero movement on real numbers, by construction.** `x or 1.0 == x` for every
nonzero `x`, the real battery has both named pools, and every baseline axis is
nonzero — confirmed end to end: `klee/starter/generic, 40 fights, seed 11`
scores A1 4.74 / A2 3.34 / A3 2.35 / A4 0.50 / A5 3.00 / A6 3.44 / A7 3.09
with `A2_samples = 33` and no guard firing.

---

## Track C — Gate repairs — LANDED

Verified END TO END, not just by pin: the pck was rebuilt with MegaDot and the
full `validate.ps1` was run against the real staged package and the real game
directory. **`validate: OK`, 84.0s.** C5 landed with Track B.

Suite: 973 → 995. Bare clone: 971 passed, 24 skipped.

> **Working-directory collision, recorded.** Between the Track B and Track C
> commits, another workstream wrote `tier0/tests/test_card_scope.py` and edited
> `KleeCode/Powers/KokomiConscript.cs` into this same working directory (a
> Kokomi conscript soft-lock fix from a 2026-07-26 playtest). A `git add -A`
> swept both into the Track C commit; the commit was split and both were
> returned to the working tree untouched, exactly as found. Nothing was lost
> and nothing of theirs is in this sprint's history. This is precisely the
> pre-commit collision class **G4** exists to address, and it happened *during
> the sprint that drafts G4* — noted there as evidence rather than hypothesis.

Every rule repaired here had the same shape: it ran, it reported nothing, and
reporting nothing read as passing.

### C1 — S8 scanned a directory with no `.ps1` files in it

It walked `$SourceDir` (= `KleeCode`). All three PowerShell files live in
`klee-mod\build\` and `tools\`. The loop found nothing every run since the day
it was written, so the mojibake class it exists for — `build_pck.ps1`'s heredoc
strings, the only place this repo writes game-visible text from PowerShell —
was never checked at all.

Now scans from the repo root, because a *list* of directories is the same
defect one level up. `.venv` and build trees are excluded — `Activate.ps1` is
not this repo's to keep ASCII. And **an empty sweep is now itself a failure**,
which is the direct lesson: a rule that iterates zero files reports exactly
what a rule that iterates a clean set reports.

### C2 — S9's precondition was the defect it existed to catch

Two repairs.

The guard was `Test-Path $stagedArt`, and `deploy.ps1` creates that directory
only when it finds sources — so "art missing entirely", the one case the rule
was written for, made the missing-art gate silent. Now that case is the
finding.

And the `break` is gone. Probing one portrait per character proved a directory
was wired and nothing else; no gate anywhere asserted per-card completeness,
because `art_coverage.py` bills against the *sheets* rather than against the
*package*. A partial copy, a name collision in the flat stage, or a per-file
filter all ship blank cards and all looked identical to the old check.

Dry-run against the real stage before landing: **264 of 264 portraits present**
across companions/furina/klee/kokomi, so the stricter rule costs nothing today
and now actually gates completeness.

### C3 — the pixel-dedupe gate was dark, and turning it on found something

L12 was off for three independent reasons, all fixed: it hashed
`art/candidates/**` (gitignored, absent on any clean checkout → `[]` in
silence); that directory is the *shortlist*, so auto-picks — which never get a
candidates directory — were never hashed at all; and it was called only from
`main()`, so `art_process`, the tool that WRITES the crops, imported `lint()`
and never pixel-checked its own output.

Now it hashes `ImageGen/images/cards/**`, and `lint()` calls it.

**It immediately found a real duplicate: `klee/kaboom.png` and
`klee/spark_knight_style.png` are byte-identical** (sha256 `5649882009…`). Both
are auto-picks off "Klee Character Card", which is exactly why the old
candidates-only hash could never have seen them.

It was already half-recorded — the pair sits in `PENDING_RED_PEN` as a *source*
collision — but unlike its two siblings it was in no pixel ledger, which is the
gap `missed-requirements.md` §4.6 names by hand. Added to `KNOWN_IDENTICAL`
with its reason. **Not resolved**: re-cropping is an art pass and the ruling it
needs ("which card keeps the Character Card") is [USER]'s. Listed so the gate
runs green while the debt stays visible.

Wired as **validate rule S10** and as a full-set pytest — closing the L11
"verified by negative test" claim, which referred to a test that did not exist.
The new test file carries both directions, with the negative half synthetic so
it runs on a bare clone too.

### C4 — the pck contract now measures instead of asserting

It was a hand-written list of ~45 `resource=` lines appended after the export,
asserting that set regardless of which copy blocks ran. Every copy block skips
on a missing source, so the contract named `res://furina/salon/member_usher.png`
whether or not that file existed. S2 checked the contract *belonged to* the pck
(sha256) and S6c checked C# references against the contract *text*, so nothing
in the loop ever touched the actual pack contents.

Now derived by enumerating the work directory — which is exactly what the
exporter packs (`export_filter="all_resources"`). **`roster-pck-v3`**, and S2
requires it: a v2 contract is a hand-written one, so reading it as current
would be reading an assertion as a measurement. An empty derived contract
throws, since a zero-length measurement is the failure mode a derived list
introduces.

Copy-block skips are now announced individually and summarised at the end.

**Rebuilt and verified: 114 derived resources, and 2 real gaps surfaced
immediately** — `kokomi\powers` and `kokomi\relics` have no source art at all.
Five C# sites reference them (`kokomi/relics/pearl_of_wisdom.png` ×4,
`kokomi/powers/pearl.png` ×1). Not a crash: `KleePck.Path` checks
`ResourceLoader.Exists` and returns null, so `?? base.PackedIconPath` falls
back to a base-game icon with a `Log.Warn`. So it is a missing-art bill that
was previously visible only in `godot.log`, and is now printed by the build.
**Recorded, not fixed** — it is an art pass, and Kokomi's art is a tracked
open item.

Two existing pins in `test_roster_runtime_contracts.py` went red, correctly:
they asserted against the static list in the builder's *source* — an assertion
checking an assertion. They now check the mechanism (derived, throws when
empty, no resource literal may reappear) plus the built **artifact**, skipped
where the pck has not been built since `*.pck.contract.txt` is gitignored.
That artifact check is the half that can actually fail when a copy block skips.

### C6 — there is no S7 stall; the premise was never measured

The diagnosis is the deliverable. `validate.ps1` carried, as the stated
rationale for an R70 design decision, the claim that *"validate.ps1 as a whole
cannot be run quickly (S7's game_ref verification takes minutes)"*.

Measured:

| | |
|---|---|
| `tools.build_ironclad_sheet --verify` | **0.17s** |
| pytest collection from the repo root | 0.40s, 984 tests |
| the pytest suite S7 runs | **78.4s** |
| every other rule in `validate.ps1`, together | **5.5s** |
| full `validate.ps1` | **84.0s** |

The game_ref verification is 0.2% of the gate. There is no stall to bound or
cache: the cost is the suite, and the suite is the point — caching a "suite
green" verdict would trade 80 seconds for a class of false green far worse than
the wait.

So, three things instead:

1. **The false claim is deleted**, with the measured numbers in its place. The
   unit-testable `Test-VersionPolicy` design stands on its own merits; only its
   stated rationale was wrong.
2. **The gate prints its own timing breakdown every run**
   (`timing: total 84.0s (S7 suite 78.4s, all other rules 5.5s)`). This cost
   was attributed to the wrong rule for the file's whole life because nobody
   printed it — a number nobody prints is a number somebody will guess.
3. **`-StaticOnly`** runs every rule except the suite invocation: **5.5s**,
   measured. It announces itself with a banner where the suite would have run
   AND in the verdict line (`validate: OK (STATIC ONLY -- the suite did not
   run)`), and `deploy.ps1` never passes it — pinned. A fast mode that could be
   mistaken for a full pass is R70's failure class wearing the opposite coat.

### Two defects the bare-clone gate caught in this sprint's own work

Track A exists so later tracks are verified against it, and it earned that
twice in one run:

- `test_content_boundaries` (Track B) asserted `len(index) > 300`. The card
  index is 367 with `game_ref/` and **291** on a bare clone, because
  real_ironclad's pool is a gitignored local artifact. A magic total was a test
  reporting the machine — the exact class Track A closed. Re-anchored on the
  committed roster (each of the three shipped characters ≥ 50 cards) plus a
  non-vacuity check that a conditional actually exercised the predicate branch.
- `test_art_lint_full_set`'s skipif used `SHIPPED.is_dir()`, and an **empty**
  `ImageGen/images/cards/companions/` is a real state on a bare clone — left
  behind by Track A's own probe test, which created directories and removed
  only the files it wrote. So the skipif read "art is present" on a clone with
  no art. Fixed on both sides: the skipif requires an actual PNG, and the probe
  test now removes the directories it created (deepest first, via `rmdir`,
  which refuses a non-empty directory — so a machine that really holds art is
  safe by construction rather than by a check).

Verified after: bare clone leaves no `ImageGen` behind at all.

---

## Track D — EPOCH 2 — predictions REGISTERED (pre-measurement)

Written and committed BEFORE any post-fix number was produced or reviewed, per
the standing discipline. Transcribed from the sprint doc so the record does not
depend on a document that can be edited later.

| # | Fix | Registered prediction | Grading rule |
|---|---|---|---|
| D1 | Pearl of Insight funnel + relic-pool membership + R7 lint extension | kokomi assigned-plan winrate moves **UP** on the canonical Cell | Direction committed, **magnitude unbounded** |
| D2 | `BombPower.DetonationsThisCombat` per-owner | solo canonical-Cell numbers move **0.0pt** — the fix is co-op-scoped | **Any** solo movement is a FINDING, not a pass |
| D3 | Furina Q3 innate Encore ships | furina/salon winrate moves **UP** from the 16.8% EPOCH-1 baseline | If it moves **DOWN**: HALT and report before landing anything else in the epoch |

Epoch stamp for this landing is assigned at landing time. Klee is untouched
this epoch.
