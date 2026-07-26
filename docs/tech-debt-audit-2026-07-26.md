# Architecture & tech-debt audit — 2026-07-26

Companion to `missed-requirements.md` (same recap session). Six parallel
audits over the C# mod, the build/deploy pipeline, the tier0 engine, the
tier05 run layer, `tools/`, and the defect→test ledger. Every finding below
was verified in code (file:line cited); several were verified by execution.

**Fix classes:** `SAFE` = mechanical, no behavior change; `TESTS` = needs a
pinning test with the fix; `RULING` = needs a [USER] decision first.
Items marked **[FIXED]** were applied in this session's cleanup commit;
everything else is untouched and logged.

---

## 1. Live bugs — behavior is wrong in the shipped tree today

### 1.1 Pearl of Insight (Kokomi's upgraded starter) is a no-op with a lying tooltip — HIGH / TESTS
`klee-mod/KleeCode/Relics/UpgradedStarterRelics.cs:217-218` declares
`ChargePerExhaust = 2 / BurstPerExhaust = 4`, but those constants are read
only by the relic's own description. The actual exhaust funnel
(`Powers/KokomiResources.cs:268-269`) always grants base 1/2 and never checks
the relic. **The red-pen record (Part 1 item 6, "shipped as doubled
per-exhaust") is contradicted by the code.** The relic's own doc comment
(:210-214) claims the opposite of what's wired.

### 1.2 All three upgraded starter relics are in no relic pool — HIGH / SAFE + TESTS
`ExplosiveFrags` (:95), `PearlOfInsightRelic` (:215), `CurtainNeverFalls`
(:324) are `autoAdd: false` and appear in no `GenerateAllRelics`.
`KleeRelicPool.cs:13-23` documents the invariant: a relic in no pool
**throws** at `RelicModel.Pool`. This is finding 27's crash class, one door
over. `KleeSelfCheck` R7 only sweeps `StartingRelics`, so the mid-run grant
path is unguarded; `lint_pool_membership.py` covers cards only.

### 1.3 Kokomi's archetype registry names tags that exist on zero cards — HIGH / RULING then SAFE
`tier05/draft.py:654-658`: `ROSTER_ARCHETYPES["kokomi"] = ("garment",
"ward", "conscript")` — her cards are tagged `priest/commander/assist/
generic`, and `runner.py:39-47` registers plans under those names. The two
registries disagree in the same repo. Verified consequences:
`dominant_archetype()` on any Kokomi deck returns `goodstuff`; adaptive
(free-draft) Kokomi scores plans as pure static power; shop/rest/event plans
degrade; `--ab` fires a spurious starvation alarm on every Kokomi run
(`ab.py:49-50` reads Klee's archetypes). **Every adaptive Kokomi number ever
taken was measured through this.** Needs a ruling on canonical vocabulary,
then a POLICY/DRAFTER stamp bump.

### 1.4 Tamakushi Casket "refresh" downgrades an upgraded Bake-Kurage — MED / TESTS
`tier0/engine/effects.py:597-599` hard-sets `kurage_summon = KURAGE_DURATION`
(1) while `_op_summon_kurage` (:1360) uses `max()`. Playing Garment after an
upgraded summon (`kurage_turns: +1` → 2) *removes* the turn the upgrade paid
for. R56/R57's claim that "restoring a longer duration is safe" is false as
wired. One-line fix; moves Kokomi priest numbers, so it needs a stamp.

### 1.5 Event-death runs lose their relic telemetry — HIGH / SAFE **[FIXED]**
`tier05/model.py`: fight-death and run-end paths overwrite `res.relics` with
the full held set (:583, :667); the event-death exit (:482-488) returned
without doing so, leaving only event-granted relics. Any relic-frequency
analysis silently mixed two populations. Fixed to write the same full held
set on the event-death exit; the field comment now also names events as a
source. *(No pin yet — belongs in the next test batch, §7.)*

### 1.6 "Explosive Frags" is two different game objects — HIGH / RULING
A Klee Rare Power card (`docs/klee-cards.yaml:193`, pooled) and Klee's
Orobas relic upgrade (`UpgradedStarterRelics.cs:122`) share the display name
with unrelated effects; both reachable in one run. `lint_unique_names.py`
sees card sheets only. Red-pen Part 1 item 5 is ambiguous about which object
it ratified — the relic's doc comment quotes the item-5 measurement table.
Rename one (the relic is the newer arrival) and teach the lint about relics.

### 1.7 Splash damage bypasses overkill clamping and block/kill accounting — MED / TESTS
Overload splash (`tier0/engine/reactions.py:148-152`) and detonation splash
(`effects.py:323-329`) emit unclamped damage; the canonical path clamps
(`effects.py:258-260`). Overkill against 3-HP swarm adds is credited in full
to `total_damage_dealt` → **A6 (a ratified elite axis for Kokomi) over-reads
for exactly the reaction archetypes it grades.** Any fix moves archived
A6/DPT numbers — batch behind a stamp. Related smaller: Shatter's emitted
vs returned damage disagree (`effects.py:269-275`).

---

## 2. Instruments manufacturing false evidence

### 2.1 Two live sweeps tune constants the engine never reads — HIGH / TESTS
- `SPOTLIGHT_SELF_MULT` (`tier0/constants.py:97`) has zero readers —
  `spotlight_mult()` hard-codes the 1.0 early-return. Yet
  `exp_furina_sheetpass.py:212-223` (block C2) sweeps it {1.0, 1.25, 1.5}:
  three guaranteed-identical rows that read as "self rate doesn't matter."
- `FANFARE_DECAY_PER_TURN` (`constants.py:183`) is unreachable while
  `FANFARE_DECAY_FRACTION > 0` (it is 0.20), yet `exp_furina_decay.py:73-95`
  sweeps it — five identical rows that read as a null. Its comment block
  still argues "FLAT over proportional is deliberate" for a branch that
  cannot execute; `resources.py:78` asserted the same. **[FIXED — comments
  and docstring corrected to the ruled 20% proportional world; constants
  marked DEAD-KNOB pending ruling. The sweeps themselves are untouched and
  must not be re-run until wired or deleted.]**
- Neither sweep calls `effects.reset_knob_reads()` — the KNOB_READS exercise
  counter (R33/DECISIONS-87) exists precisely for this and only
  `exp_furina_pass3.py` uses it. Add a KNOB_READS gate to the sweep harness.

### 2.2 The 7-axis scorecard can pass by coincidence — HIGH / RULING then TESTS
`tier0/harness/axes.py:168-180` `heuristic_flags`: "exactly two strong axes"
is enforced as *not 0, not >2* (1 passes silently); the 4–**5** upper band is
never checked (`SCORE_CAP` clamps runaways into "merely strong"); a
zero-baseline axis pins to 10.0 via `eps` division with no guard (only A4
got a floor). Klee's A1+A6 elite pairing currently passes by coincidence.
Also `axes.py:63,84`: missing `attrition`/`swarm` encounter ids silently
fall back to whole-pool averages (vs `runner.py:93` failing loudly), and
`a2 = _avg(ratios) or 1.0` maps "no fight reached turn 10" to exactly 3.0.

**RULED — D3 (2026-07-26), and it SPLITS this item.** The invariant half
(non-elite ≤ 4.0 cap, declared-elite-pair identity) is **pulled from the pin
batch**: encoding "the scorecard must be obeyed" is not something to assert
while it is unknown whether the scorecard is directionally correct. The
bands were ratified against a battery since recognized as unrealistic, and
designs were tuned until the axes hit them — "passing by coincidence" may be
Goodhart, not luck. The mechanical half (eps guard, loud failure on missing
encounter ids, the `or 1.0` default) **stays in the pin batch**: it makes
the instrument honest without asserting it is right. Standing until the
axis-validity session rules: seven-axis numbers are reportable but **not
load-bearing** — no new band ratified, no design accepted or rejected on
axis evidence alone.

### 2.3 A4 Sustain is anchored on a phantom heal — MED / RULING
Burning Blood emits `heal` without mutating HP (`combat.py:657-663`,
deliberate). Consequence not recorded anywhere: the A4 denominator is
6 × (baseline **won** fights), so any ref_ironclad winrate shift silently
rescales every character's A4; in GAUNTLET the phantom heal is banked
per-stage against an HP pool that never moved.

### 2.4 `survival_profile` sizes its axis off `results[0]` — HIGH / TESTS
`tier05/run_metrics.py:189-203` derives fight positions from the first run's
`node_kinds` — under RUNTEMPLATE 6+ paths differ per run and dead runs are
short. The same module's own docstring (:47-49) forbids exactly this. The
pass-4 fragility scalars (`act_median_hp_pct`, `act_share_below_30pct`)
cross-sample every run's HP at floors that were different room types.
Unit test uses a single synthetic run, so the hole is invisible to the suite.

### 2.5 `_static_power` prices 21–58% of each pool at exactly 0.0 — HIGH / RULING
`tier05/draft.py:313-430` knows four (power, target) pairs; 33 of 37 power
names are unpriced — furina 58.3% of draftable cards score 0.0 (spotlight
tag: 88.9%), klee 33.8%, kokomi 21.2%. `tideline_watch` is double-blind
(`block_next_turn` invisible to both `_static_power` and `_has_block`).
**The G-E3 free-draft finding (−14.5pt) was measured by this scorer** — the
confound is unstated in the sprint log. Any fix bumps DRAFTER to 11 and
archives current numbers; that's the discipline working, but the bump is due.

### 2.6 No canonical cell reproduction — MED / SAFE
The ratified-cell config ("600 runs, seed 11, hunter, RT7/D10/P2/C3") exists
in no code object; 12 exp scripts hand-roll seeds (11 / 20260720 / 20260724 /
20260725 / 2000), three carry byte-identical arg parsers with drifted
`_arm()` copies, exp scripts bypass `runner.resolve_plan` (two sources of
truth for plan→pilot), and `print_run_report` prints no version stamps.
One `Cell` dataclass + a `--stamp` line closes most of this.
Also: `exp_furina_achievability.py` still hardcodes `SCREENS = 10` from
RUNTEMPLATE 2 — it runs, prints numbers, and describes no world that exists;
`exp_furina_modes.py`/`exp_furina_pass3.py` self-declare archived. See §6.

---

## 3. Gates that don't gate

### 3.1 S8 (ASCII gate) scans a directory containing zero .ps1 files — HIGH / SAFE
`validate.ps1:631` walks `$SourceDir` (= `KleeCode`) for `*.ps1`; all three
PowerShell files live elsewhere. The mojibake class it was written for
(`build_pck.ps1:572` heredoc strings) is unchecked. A no-op gate since birth.

### 3.2 The pck "contract" asserts, it never measures — HIGH / TESTS
`build_pck.ps1:720-769` writes a static resource list after export; every
copy block skips silently on missing sources (:84, :96, :105, :114, :143).
S2 verifies the contract *belongs to* the pck (sha256), S6c checks C# refs
against the contract *text* — the loop never touches the actual `.pck`
contents. Missing salon art ships with all gates green.

### 3.3 S9 skips itself when no art is staged — HIGH / SAFE
`validate.ps1:593` guards on the staged-art dir existing, but `deploy.ps1`
only creates it when sources exist — the exact "art missing entirely"
case makes the missing-art gate silent. Also: S9 probes one portrait per
character (`break` on first hit); no gate anywhere asserts per-card art
completeness (`art_coverage.py`'s test deliberately doesn't).

### 3.4 The stderr trap survives in build_pck.ps1 — HIGH / SAFE
The PS 5.1 `NativeCommandError` class fixed in `validate.ps1` (7 call sites →
`Invoke-RepoPython`) is alive at `build_pck.ps1:699,704,710` (bare python +
two `2>&1` MegaDot calls under `$ErrorActionPreference='Stop'`). One Godot
deprecation warning kills the pck build. Also unenforced: nothing asserts
new validate.ps1 call sites use the helper; and `validate.ps1:555`'s comment
says "No 2>&1" directly above a helper call that does `2>&1`.

### 3.5 BaseLib/game version pins are decorative — HIGH / TESTS
S3 (`validate.ps1:116-121`) checks dependency *presence* only;
`min_version 3.3.6` and `min_game_version 0.107.1` are compared to nothing.

### 3.6 Manifest version: never bumped in 134 commits — HIGH / RULING + SAFE
`manifest.json` has one commit ever; everything since (Kokomi's shell, three
sprints) shipped as `0.2.0`, and `deploy.ps1:149` silently overwrites the
previous zip of the same name. For deterministic-lockstep co-op this is the
exact failure the version field exists for. Minimum safe change: refuse to
overwrite an existing `dist/klee-v<version>.zip`.

### 3.7 The pixel-dedupe gate (L12) is dead on every clean checkout — HIGH / TESTS
`art_lint.py:526` hashes `art/candidates/**` — gitignored and absent; returns
`[]` silently. It's also called only from `main()`, not `lint()`, so
`art_process`'s import path never pixel-checks; and it hashes the shortlist
rather than the shipped `ImageGen/images/cards/**` files (auto-picks are
never hashed at all). The one gate that caught the 28-card identical-crop
defect is currently off. Related: **`art_lint` is wired into no validate
rule and no full-set test** — the largest lint in the repo runs only by hand
(the L11 "verified by negative test" claim in the sprint log: that test does
not exist in the repo).

### 3.8 Parity lints: honest but narrower than their prose — HIGH / TESTS
- `lint_handwritten_parity.py` covers 8 of ~15 hand-written cards, Klee ops
  only, `Cards/` root only. Ungated live numbers include
  `LetThePeopleRejoice.cs:82` (`GainEncore(..., 6)` — an active red-pen
  tuning target), the `/4` fanfare divisor (three copies in one file),
  `CeremonialGarment.cs:78` (7), and the SpotlightCards description literals.
- `lint_constant_parity.py` is C#-driven with no reverse sweep: 84/144 tier0
  constants unclassified (incl. `FANFARE_CAP_FRACTION`, Weak/Frail mults —
  asymmetric with mirrored Vulnerable); regex misses `static readonly`,
  wrapped declarations, arrays, and all inline literals. It pinned the three
  reaction *numbers* while the *pipeline phases* (the actual defect axis)
  are unguarded — see §4.1.
- `lint_upgrade_coverage.py` Layer 2 reads the manifest, not the emitted C#
  (the exact one-layer-lint failure it was built after; currently consistent,
  latent).
- `lint_sheet_comments.py` gated 1 of 6 sheets. Run against the other five
  today it reports **35 findings** (klee 3, kokomi 25, fontaine 4, inazuma 3)
  — real drift the gate's scope hid. Fanning it out requires fixing those
  comments first (sheet-comment edits touch ratified sheets → do as its own
  reviewed pass).

### 3.9 No CI at all — MED / RULING
No workflows; pytest is by hand, and the five S6-family lints run only on a
Windows deploy machine. A contributor with green pytest has zero signal on
hand-written parity, codegen staleness, pool membership, or ancient coverage
— two of which prevent hard softlocks. The dual-wiring rationale written in
`test_sheet_lints.py:78-87` applies verbatim and was never extended.

---

## 4. Missing pins for known defects (defect→test ledger)

The crash/softlock class is exemplary — every one pinned, usually twice.
The gap is behavioral phase parity in C#:

1. **Superconduct / Shatter / aura-tick fixes (2026-07-21) shipped with zero
   tests** (`git show --stat 26fe7c9`: 13 files, 0 tests). Each was a 30–50%
   damage divergence; each can silently regress; S6e green on the three
   constant *names* reads as coverage of the three *phases* it doesn't cover.
   Pin: source-text phase assertions in the `test_roster_runtime_contracts`
   idiom (Superconduct in `ModifyDamageMultiplicative` not
   `AfterDamageReceived`; Shatter dealt from `AfterDamageReceived` with
   `Unblockable|Unpowered`; tick on `AfterSideTurnStart`). Or land the owed
   step→hook sweep as a curated-ledger lint (the house pattern).
2. **`NextAttackUpPower` series-consumption** — unpinned on both sides; the
   load-bearing pop-vs-get distinction is stated in no test.
3. **`CreatureFacing`'s three load-bearing decisions** (mirror `%Facing` not
   `Visuals.Scale` — "a gameplay bug wearing a visual bug's clothes"; hook
   `AttackCommand.Execute`) — only a `Log.Warn` behind them.
4. **`Invoke-RepoPython` convention unenforced** (see §3.4).
5. **Crackle+ printed text** — semantics pinned twice, the sentence (the
   actual defect) never; belongs with the 30 sibling text tests in
   `test_roster_codegen.py`.
6. **`KleeSceneTelemetry` is a diagnostic, not a gate** — every branch
   `Log.Warn`. Anything resting only on it is unpinned.

---

## 5. Structural debt (works today, taxes every future change)

- **Harmony bootstrap is all-or-nothing:** `KleeMod.cs:33-41` wraps
  `PatchAll` in one catch — one dead string-keyed reflection lookup
  (e.g. `ProgressSaveManager` rename) silently disarms every later patch,
  including the shop-softlock guards, with one log line. Patch types
  individually / null-guard `TargetMethods`. `MerchantCompanionSlots.cs:61`
  has the same string-fragility at static-ctor time.
  (`CreatureFacing.cs:65-66` shows the right pattern.)
- **Adding character #4 = ~26 scattered edit sites, 4 gated / 22 silent.**
  tier05 alone: 17 sites (enumerated in the audit; `runner.py` plans,
  `draft.py` ×7 including `ROSTER_ARCHETYPES`, `rewards.py:27`,
  `model.py` trace fields, `ab.py:49`). C# side: 6 closed lists, only 2
  gated (`KitBurst.NotKitCard`, `CompanionPool.CharacterId/HomeNation`,
  `KleeStartingCompanions` chain, `KleeSelfCheck` roster array are silent).
  Codegen: 9 `profile is X_PROFILE` ladders bypass the CharacterProfile
  dataclass; `_run_klee/_furina/_kokomi` are 590 lines of triplicated driver
  with three divergent manifest schemas; `_pool_members()` hardcodes Klee's
  sheet for all profiles (latent: only Klee uses `pool:` today).
  Build: roster lists in `deploy.ps1:87`, `build_pck.ps1:139` + two
  byte-identical `Copy-*Fallback` functions, contract lines, and
  `lint_pool_membership.MEMBERSHIP_FILES`. **One roster registry + extending
  the S6c pattern is the single highest-leverage refactor before Act-2 push.**
- **Character logic in generic engine chokepoints:** Kokomi's
  Strength→Charge law lives in `tier0/engine/powers.py:130-135` (string-keyed
  relic probe in the universal `apply_power`); Klee bomb suppression is
  duck-typed `getattr` in the damage funnel (:47-53) — silent no-op if the
  attribute renames; Kokomi's Charge accrual sits in `refpowers.py:245-257`,
  the Ironclad-parity module whose header says it contains no such thing.
  24 `# late import avoids cycle` sites; `effects.py` is 1848 lines.
- **C# triplication with visible drift:** 3 near-identical relic pools and
  character classes (16 `Custom*Path` overrides each); 3 byte-equivalent
  `GrantIfCharged` bodies where Klee gates on the concrete class while
  Furina/Kokomi use the interface pattern the code itself documents as
  correct (no `IKleeCharacter` exists); 4 copies of
  `TryModifyCardRewardOptions`.
- **`KleePlaceholderArt.cs` is stale-live:** its header says "deleted when
  the real pck lands" and `has_pck` is true; it postfixes 22 base getters for
  every character in the game; and it is the *only* fallback for 8 asset
  paths (arms/SFX) that Furina and Kokomi don't get at all.
- **Static-state residuals:** `SpotlightSystem.PendingDraws`
  (`SpotlightSystem.cs:62`) — process-global dict keyed by `CardPlay`,
  retains dead run graphs on abnormal exits; `BombPower.DetonationsThisCombat`
  still team-wide in co-op (tracked since 2026-07-25, "NEEDS FIX — blocked";
  the ownership idiom it needs exists two files over in `ExplosiveFrags`).
  Everything else checked is per-owner, ruled-global, or immutable.
- **Reward-draw clamp runs for every character in the game**
  (`KleeMod.cs:265-287`, no character gate — materializes the full pool per
  reward for base-game characters too).
- **`ReplaceFirst<TBasic>` matches by `is`** — first card-family subclass
  silently steals the starter-replacement slot
  (`KleeStartingCompanions.cs:235`).
- **Determinism is real and verified** (no global RNG; per-run
  `Random(seed+i)`; offset side-streams; sorted set-orderings; explicit
  tie-breaks) — two caveats: `test_parallel_runs.py` pins only ref_ironclad
  at 1 act across the process boundary, and `assigned_policy`'s two branches
  break score ties toward opposite ends (`draft.py:604-623`).
- **Content-boundary validation is inverted:** the two smallest content
  files (potions, relics) validate loudly; the two largest (events 340 L,
  act pools 720 L) read every key through `.get()` — a typo'd `is_bos:`
  makes a non-boss boss with no signal. A misspelled sheet `op:`/predicate
  loads fine and crashes mid-run when first played (`loader` validates
  fields, never op names against `OPS`). Both are cheap allowlist lints —
  the pattern already exists in `potions.py`.
- **`tier1/analyze.py` is Klee-only** (`CHARACTER.KLEE`, `CARD.KLEEMOD-`
  prefix): the soak instrument predates the roster and can't see
  Furina/Kokomi runs.
- **macOS is documented but unservable** (`Directory.Build.props` detects
  mac game dirs; every script assumes `\`, `.venv\Scripts`, `.exe`) — the
  failure message misleads. Plus `build_pck.ps1:23` defaults MegaDot to one
  contributor's `Downloads\` folder — the only record of the contractual
  editor build.

---

## 6. Dead code & orphans

**Moved to `tools/archive/` this session [FIXED]:** `render_card_gallery.py`
and `banner_variance_cells.py` (zero references repo-wide),
`autocrop_card_art.py` (docstring: absorbed into `art_process` as
`cover_autocrop`), `klee_dead_cards.py`, `klee_lever_sweep.py`,
`klee_rework_sim.py` (design-review one-shots, results ratified),
`roster_scale_gap.py` (superseded by `encounter_audit.py`, which says so).
A `tools/README.md` index now maps every remaining script to its gate/test/
doc status so orphan status stays discoverable.

**Dead constants (`tier0/constants.py`), comments corrected [FIXED],
deletion needs a ruling:** `PROGRESSION_GAP_COMPENSATOR` (frozen, applied by
nothing — comment claimed live application), `SPOTLIGHT_SELF_MULT`,
`FANFARE_DECAY_PER_TURN` (unreachable branch), `SPOTLIGHT_SELECTOR_VERSION`
(stamp nothing reads), `PILOT_REGRET_SAMPLE_RATE` (implies sampling;
`_log_regret` is a full census), `ATTRITION_LITE_HP`, `PUNISHER_LITE_SCALE`,
`NORMAL_POOL_WEIGHTS`, `NORMAL_ATTRITION_SCALE`.

**Sim-layer leftovers (SAFE, untouched):** `model.py:347` dead `final_act`;
`model.py:358` documented no-op `grant_treasure_relic` call;
`node_template()` exported though DEAD as of RUNTEMPLATE 6;
`acts.ELITES_PER_ACT` tombstone plus `ActDraw._e_seen` written-never-read;
`_game_ref_digest()` byte-duplicated across two tools with a test that
*pins the duplication* (belongs in `tier0/content/local_reference.py`);
`gen_roster_cards.py` can't be imported as a module (path-invoked only —
which is why no test covers the entry point validate gates on);
5 of 46 engine OPS are reachable only via the gitignored `game_ref/`
(document as such); `metrics.py` extracts `prevented`/`charge_gained`/
`engine_closure_turns`/`debuffed_intents` that no report prints — note
`prevented` is the ruled feed for the (unbuilt) stability band, see
`missed-requirements.md` §1.3.

---

## 7. Repo/policy items (need [USER], not code)

1. **Tier F art was in the public repo — REMEDIATED 2026-07-26.**
   `docs/klee-art-hunt-contactsheet.png` (21 cells of sourced Genshin art,
   GENSHIN IMPACT/Cognosphere watermarks visible) and
   `docs/animation-sprint-2-a3-intake.png` (two full HoYoverse Furina
   renders) were committed under `docs/` — the same content class
   `.gitignore` blocks by path with the comment "repo is public."
   **[USER]-ruled removal, executed this session:** both files purged from
   the entire history via `git filter-repo --invert-paths`; `main` and the
   working branch force-pushed with the rewritten history. The third PNG
   (`docs/animation-sprint-1-a4-gate.png`, an in-game screenshot of the mod
   running) was ruled distinct and retained. Residual caveats, standard for
   any history rewrite: (a) GitHub may serve the old commits by SHA until
   its garbage collection runs — a support ticket can force it if urgency
   warrants; (b) any existing local clone still holds the old objects and
   should be re-cloned, not pulled; (c) there were no forks or open PRs at
   rewrite time (verified: forks_count 0).

   **SHA translation.** The rewrite renumbered every commit after the first
   PNG landed. Docs and DECISIONS cite short SHAs extensively; those
   citations refer to the pre-rewrite history. Translation for all 41
   doc-cited commits (old → new; two early ones unchanged):

   | | | | |
   |---|---|---|---|
   | `0076b7b`→`cef61e1` | `0b33ffd`→`d0b4c1b` | `102e99a`→`7b02cb2` | `15fc78f`→`d1083cf` |
   | `1752836`→`7b7c835` | `1afee5d`→`e5c8c31` | `22b6d86`→`1442afc` | `26fe7c9`→`cdd2aff` |
   | `329c1a7`→`805ca9f` | `364acf0`→`f9dcccf` | `40b0884`→`3ba78d3` | `41cab5a`→`0514242` |
   | `477b282`→`388d838` | `4ce3b87`→`bb511d0` | `5828cd0`→`e727c25` | `5e631f0`→`88f7ec3` |
   | `68fb11b`→`e4f8e3b` | `6af7a71`→`55763ee` | `6d75d37`→`3c0cdff` | `6f1b969`→`cf9dcc1` |
   | `7260590`→`64024aa` | `7480847`→`9528214` | `750a9cc`→`a2ee535` | `7c53c31`→`a10d2e5` |
   | `81ba9d5`→`2613a44` | `90c9b58`→`1251f42` | `94c8e91`→`16599b4` | `a1bca0d`→`0ef3105` |
   | `a23d87f`→`9db3805` | `a879ffe`→`a0aa716` | `bc02b76`→`b99b689` | `bc8995f`→`61ff723` |
   | `db06d8c`→`f49aa66` | `e263577`→`37dacee` | `e307ad2`→`fe59287` | `e3852e7`→`2f3b10d` |
   | `e80f955`→`5d9477c` | `ebcf1b2`→`72fea95` | `f032cf1`→`5337995` | `587a902`, `915dd0e` unchanged |

   The doc texts themselves were left as written (they are records); read
   their SHA citations through this table. The deployed-pck stamp
   `20260725-175515+e263577` in `open-playtest-items.md` likewise refers to
   pre-rewrite `e263577` = post-rewrite `37dacee`.
2. **Manifest version policy** (§3.6) — decide the bump discipline (per
   deploy? per handoff?) and whether deploy should enforce it.
3. **35 stale sheet comments** (§3.8) — a reviewed comment-fix pass over
   klee/kokomi/fontaine/inazuma sheets, then fan `lint_sheet_comments` over
   all six sheets in `test_sheet_lints.py`.
4. **Sheet `docs/mondstadt-companions.yaml:4`** still opens with "Companion
   cards NEVER scale" — the ruling went the other way
   (`klee-mod/DECISIONS.md:1524`). One-line sheet-comment fix, listed here
   because sheets are ratified artifacts.

---

## 8. Fixed in this session (all comment/doc/organizational — zero behavior)

- `tier05/model.py` event-death relic telemetry (§1.5 — the one behavioral
  fix; unambiguous data-corruption bug).
- `tier05/route.py` header no longer advertises the unbuilt `route_regret`.
- `tier0/engine/resources.py` decay docstring now describes the ruled
  proportional world; `constants.py` decay/self-mult/compensator/
  regret-rate comments corrected and marked DEAD-KNOB where dead.
- `tier05/draft.py` header no longer claims "DRAFTER_VERSION 3" (points at
  the live stamp in `tier0/constants.py`); `tier05/maps.py` header 17→16
  floors contradiction fixed.
- Root `README.md`: `klee-mod/tools/build_pck.ps1` → `tools/build_pck.ps1`.
- `tools/lint_strict_domination.py` standalone default now covers all six
  sheets (pytest already did; the CLI default silently skipped Kokomi and
  companions).
- Seven orphan tools → `tools/archive/`; `tools/README.md` index added.

## 9. Suggested sequencing for the "big push"

1. **Rulings batch** (one red-pen sitting): Kokomi archetype vocabulary
   (§1.3), Explosive Frags rename (§1.6), dead-constant deletions (§6),
   manifest version policy, Tier F PNG remediation, `_static_power`
   repricing scope (§2.5 — this is the DRAFTER 11 bump).
2. **Pin batch** (tests only, no behavior): reaction phase parity ×3,
   NextAttackUp series, CreatureFacing placement, Invoke-RepoPython
   enforcement, outline≠fill icon assertion, salon scale arithmetic,
   Crackle+ text, op/predicate-vs-OPS lint, events/act-pool key allowlists,
   plus the §2.2 mechanical repairs (eps guard, loud missing-encounter
   failure, the `or 1.0` turn-10 default).
   **PULLED by D3 (2026-07-26): the §2.2 scorecard INVARIANTS** (non-elite
   ≤ 4.0 cap, declared-elite-pair identity). They are not deferred for cost;
   they are deferred because pinning "the scorecard must be obeyed" asserts
   the scorecard is right, and that is the open question. Reinstate only if
   the axis-validity session (below) finds the instrument directionally
   sound.
3. **Gate repairs** (small diffs, big honesty): S8 target dir, S9 inversion,
   L12 → shipped files + wire art_lint as S10, contract from staged files,
   S3 version compare, build_pck stderr helper.
4. **Behavior fixes behind stamps**: Pearl of Insight funnel (+ relic pool
   membership + R7 extension), Tamakushi refresh max(), splash clamping,
   survival_profile axis, DetonationsThisCombat per-owner.
5. **Then** the structural refactors (roster registry, codegen driver
   unification, engine chokepoint extraction) — each is mechanical once the
   gates from (2)–(3) are watching.

## 10. The horizon list (design sessions, not code)

### Axis-validity session — OPEN, opened by D3 (2026-07-26)

**Question.** Is the seven-axis scorecard directionally correct, or has the
design loop been overfitting to it? The bands were ratified against a
battery since recognized as unrealistic, and designs were then tuned until
the axes hit those bands — the same battery on both sides of the loop. A
design that "passes" may be passing by construction.

**Sequencing is part of the ruling**, both ends:

- **After EPOCH 1 lands.** A6 splash and `survival_profile` were known
  instrument errors; re-litigating the framework on contaminated readings
  would decide the wrong question. (EPOCH 1 landed 2026-07-26 — this end of
  the gate is now clear; see `docs/epoch-1-log-2026-07-26.md`.)
- **Before the Zhongli deep dive.** Slot 4 must not declare elite axes
  against a framework nobody trusts.

**Candidate agenda (non-binding).** Directional-validity tests against
holdouts the designs were never tuned on: the tier-0.5 realistic gates, and
co-op playtest outcomes, which no design loop has ever seen.

**Until it rules:** seven-axis numbers are reportable but not load-bearing.
