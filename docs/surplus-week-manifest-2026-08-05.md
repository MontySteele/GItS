# Surplus Week — landing manifest

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

> ## RETIRED AS A REGISTER 2026-08-06 — status lives in the queue now
>
> As of 2026-08-06 (docs diet, Track Z / Z-3) this manifest is **the landing
> record of surplus week**, not a live open-item register. Nothing was deleted
> or reworded. §4's "Open [USER] items", the Last Call addendum and the Second
> Wind batch's one-liners are all reconciled in `docs/registry/user-queue.md`
> — §1 (`Q4` came from here), §5, §7 and §8 — and where the two disagree the
> queue is the later reconciliation.

**Status:** INDEX. This file is a pointer table, not a finding. It says what
landed, where it lives, and what is still owed. It resolves nothing, grades
nothing, and carries zero design authority.

**Landed by:** the R106 merge train ("Last Call", Track A), 2026-08-05.
Merge order was fixed by Ruling 6: the cloud dispatch as one unit, then S12,
then S3 (with a path repair), then S5, then S7 last.

**Read this first.** Every stream below produced a *review artifact* — a
verdict sheet, a gallery, an atlas, a ledger. Almost none of them authored a
fix, and the ones that changed code say so explicitly. If you are looking for
"what did surplus week *do* to the game", the honest answer for thirteen of
the fifteen streams is: nothing yet. It looked.

---

## 1. The streams

Fifteen streams. S3, S5, S7 and S12 ran locally; the other eleven ran on the
cloud branch `claude/surplus-week-dispatch-lg7k0c` and arrived interleaved,
which is why that branch merged as a single 24-commit unit rather than as
eleven cherry-picks.

Numbers below are the documents' own claims, quoted, not re-derived.

| Stream | What it was | Tip commit | Artifact(s) |
|---|---|---|---|
| S1 | Card parity sweep: 219/219 cards verdicted (76 Klee / 82 Furina / 61 Kokomi) — CLEAN 147, with-findings 72, 111 raw findings; "NO FIXES anywhere — verdicts only." Fable triage deduped those to **41 distinct defects** + 5 not-a-defect rows, ranked as systemic families SYS-1…SYS-8+. | `3b81d81` (ledger `812c28a`) | `review/parity-sweep/findings-ledger.md`, `review/parity-sweep/triage-memo.md` |
| S2 | Teyvat **event** conversion gallery: 47 events, 141 drafted variants → 130 kept / 11 cut, 4 demotions. "Curation here is selection and ordering only" — no draft text rewritten, flags are questions not changes. | `c0d01cd` | `review/event-gallery/gallery.md` |
| S3 *(local)* | Enemy bestiary: **111 dossiers** written one-agent-per-enemy, then a Fable synthesis into five fight classes (spike / attrition / swarm / gimmick / mixed). Gimmick = 27 of 111, ~30% of Act 1 encounters; slope rule ≲ +3 damage/turn. "Zero design authority: no RESKIN/REDESIGN verdicts anywhere." | `ec15028`, path-repaired by `28759f0` | `docs/enemy-dossiers/` (112 files: 111 dossiers + `fight-class-labels.yaml`), `docs/fight-class-taxonomy.md` |
| S4 | Ledger consistency audit over DECISIONS entries 1–93, R39–R97, D2–D5: **17 findings** F1–F17 (2 HIGH / 8 MEDIUM / 7 LOW) plus 20 double-cited [USER]-gate queue entries. "STRICTLY READ-ONLY — nothing was amended; every resolution below is PROPOSED, NOT EXECUTED." | `c4427a1` | `review/ledger-audit/hygiene-report.md` |
| S5 *(local)* | Animation-tech peek at `SlayTheSpire2.pck` v0.107.1. The answer is one word: **Spine** (`spine-godot` GDExtension, skeleton format 4.2.43). 101 folders, 101 of them Spine, zero exceptions; 163 `.spskel`, 169 `.spatlas`; 126 creature scenes, 118 with SpineSprite; 0 AnimationPlayer, 0 AnimatedSprite2D, 0 Skeleton2D. Read-only; nothing extracted into the repo. | `09585fa` | `docs/s5-animation-tech-note.md` |
| S6 | Mutation audit: **114 mutants across 17 modules — 68 killed, 46 SURVIVED, 0 not run**, survivors ranked (31 HIGH). "Non-goal honored: zero tests were written"; all mutations reverted, clean tree verified. | `c613f91` | `review/mutation-audit/blind-spot-report.md` |
| S7 *(local)* | Understudy fidelity audit, in two passes. The worker pass built `understudy/replay.py` and inventoried **39 soak run logs, 5,704 `decision` rows, 139 closed `fight` records, 18 `defect` rows, 97 `forced_default` rows** (2,738 `play_card` actions), filing 1,635 divergence rows. The Fable pass sorted those into four families — A instrument defects, B replay reconstruction gaps, **C two candidate genuine infidelities (+2 block offset; Fanfare accounting residual)**, D uninformable — and states: "of 1,635 rows, none is yet a confirmed tier0 infidelity." Status REVIEW. | `a828e45` (worker `ac40e18`) | `understudy/replay.py`, `docs/s7-fidelity-audit.md`, `docs/s7-classification.md`, `docs/s7-divergences.tsv` (1,636 lines) |
| S8 | Teyvat **potion + relic** conversion gallery: 51 items curated, 126 draft mappings → 79 kept / 47 cut (14 canon errors, 32 cross-gallery redundancies, 1 reserved-naming collision). Hard gate: "0 set-shaped mappings found." Mechanics FROZEN — names, flavor and lore only. 8 items flagged for [USER]. | `49b2283` | `review/potion-relic-gallery/gallery.md` |
| S9 | Weekly-boss dossiers: **11 bosses** (Dvalin, Andrius, Childe, Azhdaha, La Signora, Raiden, Shouki no Kami, Guardian of Apep, All-Devouring Narwhal, The Knave, Lord of Eroded Primal Fire), one agent each, plus a cross-boss pattern memo. Pool splits roughly half HP-gated, half counter/gauge/event-gated. "ZERO design authority … no card designs, no proposed numbers, no verdicts." | `d6fe4e1` | `review/boss-dossiers/dossiers.md`, `review/boss-dossiers/pattern-memo.md` |
| S10 | Enemy-family atlas: **16 Genshin enemy families** (variants, silhouettes, elemental identity, family structure), plus a Fable dedupe pass against the committed base roster into a reskin-candidate gallery. "Candidates only, never verdicts: RESKIN/REDESIGN is [USER]'s call per north-star." | `ce4f85a` | `review/enemy-atlas/atlas.md`, `review/enemy-atlas/reskin-gallery.md` |
| S11 | Architecture atlas: **12 module docs + index**, one agent per module, "every invariant and trap carrying a file:line or DECISIONS.md cite". "These are maps, not reviews — no design opinions, no proposals." | `ae3ec39` | `docs/atlas/` (13 files incl. README) |
| S12 *(local)* | `tools/patch_sentinel.py` — a tripwire that re-extracts from the installed DLL and diffs 4 surfaces (cards / characters / relics / dll) against `game_ref/` + `.sentinel/` baselines. 14 tests; an **advisory** CI job. Documents its own blind spots: card/relic TEXT (IP rule), method-body behaviour, and every surface with no baseline (potions, events, encounters, monsters, acts, enchantments, badges, map generation). | `e38ce08` | `tools/patch_sentinel.py`, `docs/patch-sentinel.md`, `tier0/tests/test_patch_sentinel.py`, `.github/workflows/repo.yml` (advisory job) |
| S13 | Verified exploit ledger: **71 candidate lines returned, 71/71 verified on central replay** (18 infinite, 13 stall, 40 metric threshold), each re-executable per seed, across **14 mechanism families**. "Review artifact — zero design authority: no nerfs, no fixes, no costing opinions." Carries a standing caveat, *sim-verified-with-known-infidelity-list-pending*, because S7 was not final when it ran. | `c1b5227` | `review/redteam/exploit-ledger.md`, `review/redteam/exploit-lines.json`, `review/redteam/harness.py`, `review/redteam/replay-results.json` |
| S14 | Non-card parity sweep: **173 entities** (powers 25, relics 42, potions 9, events 24, companions 51, constants 22) → **75 CLEAN, 98 with findings, 174 findings** (83 low / 65 medium / 26 high). All 174 passed a mechanical citation audit. Triage memo ranks NC-1…NC-6+ and cross-references S1's SYS-numbers and the S13 exploits whose enabler is a parity defect. "Zero design authority: no fixes, no suggestions — verification only." | `0d0f463` | `review/parity-sweep/noncard-findings-ledger.md`, `review/parity-sweep/noncard-triage-memo.md` |
| S15 | Suite-hardening sweep — the one stream that shipped executable work: **111 pin-test functions across 22 new test files** (17 module + 5 card-batch), pinning **46/46 S6 surviving mutants** and all **64 clean-but-untested S1 cards** (25 Klee / 12 Furina / 27 Kokomi). "Zero should-be findings were filed." Claims **1629 passed / 61 skipped** on its own history (see §3 — the post-merge count differs). The S7 arm is absent by circumstance. | `6171428` | `review/suite-hardening/summary.md`, `tier0/tests/test_pin_*.py` (17), `tier05/tests/test_pin_*.py` (5) |

### Rider: Playtest 4

`95a88ac` ("Playtest 4 enters the record") is **not** a surplus-week stream —
it predates the week and was sitting unmerged on the S3 branch as `ec15028`'s
parent. It rode in with S3 and is flagged here so nobody hunts for the stream
that produced it. It adds `docs/playtest4-notes-2026-08-04.md` and
`docs/playtest4-triage-2026-08-04.md` and edits `docs/backlog-2026-07-29.md`
and `docs/kokomi-playtest-protocol.md`.

---

## 2. The S3 path repair

`ec15028` committed its 113 files under
`.claude/worktrees/s3-enemy-dossiers/docs/…` — the worktree-relative path the
authoring session was standing in, not the repo-root path the tree needs. The
files were therefore invisible to everything: `docs/enemy-dossiers/` was empty
on main, and `.claude/` is session scaffolding, not tracked content.

`28759f0` is a pure rename of all 113 files into the repo-root `docs/` tree.
No content was edited; no target path existed beforehand, so nothing was
overwritten. The tracked tree now has zero files under `.claude/`.

**Stale pointer, do not trust it:** the branch `review/enemy-dossiers` points
at `e07fb4c`. The dossier content did *not* land from that branch — it landed
via `ec15028` plus the repair above.

---

## 3. Suite

Baseline on main before the train: **1605 passed / 6 skipped** (auto mode),
**1570 passed / 41 skipped** (`GITS_REFERENCE_MODE=committed-only`).

After the full train: **1752 passed / 6 skipped** (auto), **1717 passed / 41
skipped** (committed-only). All eight CI lint jobs exit 0.

S15's own summary claims 1629/61 on its own history. That number is not
comparable to the ones above — it predates the merge with main's later work
and was measured in a different reference mode. Both are recorded; neither is
wrong.

One inconsistency worth knowing before you cite S15: its per-module pin-count
table lists 0 pins for engine-effects, engine-reactions, tier0-pilot and
tier05-economy even though all four files exist and carry tests. The table's
column does not sum to its own headline of 111. Not repaired here — that is
the stream's paperwork, not the train's.

---

## 4. Open [USER] items

> **QUEUE POINTER** (Track X, 2026-08-06; compressed by Track Z, Z-6). Status for everything below lives in `docs/registry/user-queue.md`; short codes resolve at `docs/registry/identifiers.md`. Full rule: `docs/registry/identifiers.md` §16.


Nothing in this section is scheduled. Each is a decision waiting on the table.

1. **S2 gallery sitting.** 47 events / 130 kept variants, awaiting a sitting.
2. **S4 audit sitting.** 17 hygiene findings, all resolutions PROPOSED and
   NOT EXECUTED. Per Ruling 6, the **ledger-repair pre-drafts are gated on
   this sitting** and were deliberately not authored by the train.
3. **S13 exploit ledger sitting.** 71 verified lines, 14 mechanism families.
   No fixes authored, by design.
4. **S14 non-card parity triage sitting.** 174 findings across 173 entities.
   No fixes authored, by design.
5. ~~**C2 escrow release (R102).** Four fanfare conclusions remain PROVISIONAL
   pending probe (b).~~ **DISCHARGED 2026-08-06 by R113** — [USER]: *"agreed -
   signed."* Probe (b) reported, C2 was written off, and all four PROVISIONAL
   marks are struck as instrument-vindicated. The grades stand exactly as
   ratified; no number moved.
6. **Build 0.2-296 distribution + telemetry notice** to the table.
7. **R105 fact-sheet item** — carried in tonight's Track E.
8. **S7 §4 probes.** The two family-C candidates (+2 block offset, Fanfare
   accounting residual) are [USER]-gated candidates, not scheduled work.
9. **S8's 8 flagged items** and **S10's reskin candidates** — candidates, not
   verdicts; RESKIN/REDESIGN remains [USER]'s call per north-star.

**Parked deliberately by the train:** ledger-repair pre-drafts and any
S2/S4-derived amendment; any S13/S14 finding resolution; the escrowed numbers.
The artifacts merge; the derived work waits.

---

## Addendum (Last Call / House Lights, 2026-08-05 late)

- **G12 eyes-on materials are ready:** `docs/g12-review-2026-08-05.md` — contact
  sheets verified + all 24 in-game captures; the five-minute look the gate wanted.
- **Optional sitting material (no review obligation):** `review/ancients-gallery/gallery.md`
  and `review/boss-pool-gallery/gallery.md` — curated best-first, checkbox-per-entity.
- The batch's own asks live in `docs/sitting-prep-2026-08-05.md` §10.
- **House Lights ledgers:** `docs/lore-fidelity-audit-2026-08-05.md` (Track N),
  `docs/instrument-redteam-2026-08-05.md` (Track O, +87 pins),
  `docs/mutation-round-2026-08-05.md` (Track K, +32 pins),
  `docs/probe-a-block-offset.md` / `docs/probe-b-fanfare-residual.md` (Track B),
  `docs/probe-d-registration-draft.md` (Track P, DRAFT),
  `docs/roster-anchor-v14-2026-08-05.md` (Track G, PROPOSED),
  `docs/reactions-corpus-2026-08-05.md` (Track H — see sitting pack §10.14 caveat),
  `docs/zhongli-dossier-2026-08-05.md` + `docs/slot5-candidates-2026-08-05.md` (Track J),
  `docs/animation-downfall-investigation-2026-08-05.md` (Track M),
  `docs/sitting-prep-2026-08-05.md` (Track L — the sitting's single entry point).

---

## Second Wind batch (2026-08-06)

**What changed about this file's premise.** §4 above lists nine open [USER]
items and says of surplus week that "the honest answer for thirteen of the
fifteen streams is: nothing yet. It looked." The sitting of **2026-08-06**
ruled on two of those nine — the **S4 audit** (item 2) and the **S13 exploit
ledger** (item 3). They are no longer open, and the derived work §4's closing
line calls "parked deliberately by the train" is unparked for those two.

**Authority document:** `docs/sitting-record-predraft-2026-08-06.md` — [USER]'s
verdicts, transcribed and committed verbatim before anything was executed from
them.

### Track R — the sitting lands

| what | where | note |
|---|---|---|
| The sitting record | `docs/sitting-record-predraft-2026-08-06.md` | Verbatim. The source every ruling below is drawn from. |
| Six rulings | `tier0/DECISIONS.md` **R107–R112** | R107 S4 (F1–F17 approved; DRAFTER 13 entry, which discharges G8) · R108 G1 countersigned, Zhongli slot 4 · R109 two new rarity laws (X2, X7) · R110 three ratified changes (X3, X11, X14b) · R111 the nine families that are not changing · R112 O-1 and N-1 docketed. |
| S4 repair batch | `docs/backlog-2026-07-29.md`, `docs/README.md`, `tier0/DECISIONS.md` (R84/R87/R96 banners), `docs/teyvat-spire-design-principles.md`, `docs/furina-kickoff-v0.1.md`, `docs/klee-character-design.md`, `docs/kokomi-playtest-protocol.md`, `docs/missed-requirements.md`, `docs/open-playtest-items.md`, `docs/axis-validity-session-charter.md`, `docs/role-tempo-floors.yaml`, `tools/canon_role_tempo.py` | **16 of 17 executed. F6 BLOCKED** — its proposal requires stating whether the 2026-08-01/02 session is the G5 fork's trigger, and no such fact was supplied. Strikes are strikethrough + dated banner; no measured value was rewritten (R101b). |
| S13 ledger dispositions | `review/redteam/exploit-ledger.md`, `tier0/tests/test_s13_exploit_pins.py` | All 14 families annotated per-family with the verbatim verdict and its routing; each pin carries a one-line disposition. **No pin flipped** — a disposition is not a fix. |
| Dockets | `docs/dockets/` (`README.md`, `klee-rework.md`, `kokomi-workshop.md`, `companion-pricing.md`, `watch-items.md`) | New directory. Routed, not decided. X7's audit slot is **empty and owned by Track T**. |

**Four HELD flags, carried out of the sitting unresolved and not to be built
against:** FLAG-1 (X1's second enabler / a structural disposition for the
shared accumulator), FLAG-2 (X3's two adjacent closures), FLAG-3 (what X5's
verdict actually covers), FLAG-4 (X14's legs (a) and (c)). Each is recorded
with its question in R110/R111 and mirrored into the ledger and the dockets.

**One item surfaced, not resolved:** X2's approved mechanical audit (R109) was
given a law but no docket. Recorded as unrouted in
`docs/dockets/companion-pricing.md` §2.

### Track S — the three ratified errata (R110), both engines

The batch's only behavior changes.

| change | where | note |
|---|---|---|
| S-1 (X3): Encore Performance loses the energy refund and becomes 0-cost | `docs/furina-cards.yaml`, regenerated `klee-mod/.../EncorePerformance.cs`, new cost pin in `tier0/tests/test_furina_sheet.py` | "The energy rider" read as the `{op: energy}` refund (keeping a refund on a 0-cost card would be energy-positive, contradicting FLAG-2's premise). **The upgrade's `copy_cost_override: 0` deletion is STOPPED** — it is the upgrade's only content, and deleting it makes `lint_upgrade_coverage` fail L1; the remedy (replacement delta or curated exemption) is a design call. `docs/furina-upgrades.yaml` untouched, one-liner owed. |
| S-2 (X11): `replay_next_companion` scoped to the writing turn | `tier0/engine/combat.py` (clear moved from next turn's open to this turn's close), new test in `tier0/tests/test_furina.py` | Write-side scoping chosen because spend-side needs per-stack metadata the C# `Counter` power cannot carry; C# already expired at `AfterSideTurnEnd`, so tier0 was the divergent half. One boundary covers both twins (Study Buddy, Duet). In tier0 the change is behaviorally **inert** — a parity/legibility fix, not a nerf. |
| S-3 (X14 leg b): ethereal-spotlight hand-full fallback (random discard first) | `tier0/engine/effects.py`, `klee-mod/.../EtherealSpotlightRelic.cs`, three tests | New stochastic surface → dedicated RNG stream (tier0 `selector_rng` at seed+4e9; C# `furina_spotlight_hand_full` per the banner idiom); `understudy/rng.py` now carries an actual stream registry. Victim pool follows `_op_discard`'s kit-cards-never-fodder rule; a kit-only hand keeps the old skip. |

**No S13 pin flipped, and correctly so** — each of the three families is
pinned by a leg the errata do not touch (X3's pin caps on self-copies alone;
X11's line stacks and spends inside one turn; X14's pin is leg (a), which is
HELD). The pins' docstrings record this. Post-errata harness re-run on 9
affected lines: all 9 still verified, byte-identical observed fields.
Line-quality finding: `stall_softlock_4`, the
ledger's own leg-(b) line, never actually starves the selector — its stall
claim holds for a different reason than its mechanism.

C# build clean, bite-check 14 patch classes armed, nothing deployed. Parity
lints (constant/op/handwritten/upgrade-coverage) all OK; fanfare parity
vectors unaffected (verified, not assumed).

### Track T — the three sweeps (R109/R111 audits)

`docs/track-t-audits-2026-08-06.md`. One ratified conditional action taken:
**`sucrose_gust` Common → Uncommon** (rarity field only, per R109's "if this
is Common, it needs a bump"; `sayu_naptime` was already Uncommon). Findings
wired into `docs/dockets/klee-rework.md` §2b/§3 (X7 spark law: 6-or-0 limb-(a)
violations depending on a reading left open, 1 limb-(b) violation
`cant_catch_me`; X8: two Common term-1 writers undercut "fine at higher
rarity"; the ratified `bomb_damage_up ≤ 4` cap was never implemented) and
`docs/dockets/companion-pricing.md` §2 (X2 results + the C# `Star` parity
question). Population caveat: no `game_ref/` in the audit worktree, so
base-game pools were not swept.

### Track U — O-1 repaired, corpus republished with erratum (R112)

`run_battery`'s stage-merge keeps one record per encounter *attempt* but now
carries its stages, and every reaction/aura/payoff rate denominates
**per combat** (`tier0/harness/metrics.py`; 10-test pin
`tier0/tests/test_pin_o1_combat_denominators.py`). The corpus re-read moved
**zero pooled counts across all 91 rows** — pure denominator defect, the
predicted 16.7% overstatement exact. Erratum atop
`docs/reactions-corpus-2026-08-05.md` (originals preserved in Appendix E;
corrected TSV alongside, original byte-untouched). Stated, not re-graded:
the gauntlet aura-ranking inversion O predicted occurred in every arm; starved
combats reappear; the per-fight mean *share* moves up. Cohort surface
untouched — tier 0.5 never merges stages. No other O finding addressed.

### Open one-liners this batch generated for [USER]

1. **F6** (Track R, blocked): is the 2026-08-01/02 session the G5 fork's
   trigger? The S4 proposal needs that fact stated to execute.
2. **Encore Performance's upgrade** (Track S, stopped): deleting
   `copy_cost_override: 0` empties the upgrade entry and fails L1 — replacement
   delta, or curated exemption?
3. **CONSTANTS_VERSION 4→5?** (Track S, surfaced): S-1 moves a Furina rare's
   cost + deletes an energy op; under the constant's own comparability
   criterion, prior Furina tier-0.5 numbers are no longer strictly comparable.
   DRAFTER_VERSION and RUNTEMPLATE correctly do not bump.
4. **X7 limb-(a) reading** (Track T): broad = 6 Common violations, strict = 0.
   Which does the law mean?
5. **X2 audit venue** (Track R/T): does `docs/dockets/companion-pricing.md`
   own X2 rarity work going forward?
6. **F14's siblings** (Track R): four further `R91/1c` misattributions in
   `tools/canon_role_tempo.py` sit outside F14's cited scope.

#### Replies of 2026-08-06, and what executed against them (Track W)

Three of the six are answered. **The other three are still AWAITED and nothing
was executed against them.**

| # | reply | executed |
|---|---|---|
| 1 · F6 | **AWAITED** | nothing. Both answer forms are DRAFTED and parked at `docs/awaiting-user-slots-2026-08-06.md`; a one-word reply lands one. |
| 2 · Encore Performance | *"CURATED EXEMPTION now; the replacement delta is deferred behind FLAG-2."* | Register entry in `tools/lint_upgrade_coverage.py::SHEET_EXEMPT`, carrying the citation and the FLAG-2 removal gate. **`docs/furina-upgrades.yaml` is still untouched** — S-1's stopped deletion is a sheet change and Track W did not take it, so the exemption is pre-positioned rather than load-bearing today. |
| 3 · CONSTANTS_VERSION 4→5 | **APPROVED** | `tier0/constants.py` `CONSTANTS_VERSION = 5` with its changelog note citing S-1 (R110/X3) as the comparability break; archive banners appended to six documents publishing Furina tier-0.5 numbers. No number rewritten (R101b). |
| 4 · X7 limb (a) | *"infinite sparks must not be achievable at Common"* — some Common spark generation is fine. | Dated [USER] annotation on R109; re-read of all six candidates against the unboundedness criterion — **3 VIOLATION / 3 CLEARED**, `docs/dockets/klee-rework.md` §2c, lines in `review/redteam/exploit-lines-x7a.json`. |
| 5 · X2 venue | **AWAITED** | nothing. One-line venue assignment DRAFTED at `docs/awaiting-user-slots-2026-08-06.md`. |
| 6 · F14's siblings | **AWAITED** | nothing on `main`'s line. The repair + a new attribution lint are **STAGED, never merged**, on branch `staged/f14-siblings`. |

**Owed by the C5 bump, and it is a COMPUTE decision, not a debt this batch
pays: the Furina tier-0.5 re-baseline belongs to the next measurement
sprint.** Nothing was re-measured for the bump; the banners label the archive
and stop there. Until that sprint runs there is **no post-C5 Furina row
anywhere**, so every Furina winrate in circulation is quotable only with its
pre-C5 label attached.

### Suite and lints at the batch tip

Full suite (auto mode, game_ref present):
`python -m pytest tier0/tests tier05/tests -q` — **1975 passed / 6 skipped /
14 xfailed** after all four tracks. Committed-only mode green at every track's
own tip. Lints incl. duplicate-R/D-number check exit 0.
