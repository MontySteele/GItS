# Surplus Week — landing manifest

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

Nothing in this section is scheduled. Each is a decision waiting on the table.

1. **S2 gallery sitting.** 47 events / 130 kept variants, awaiting a sitting.
2. **S4 audit sitting.** 17 hygiene findings, all resolutions PROPOSED and
   NOT EXECUTED. Per Ruling 6, the **ledger-repair pre-drafts are gated on
   this sitting** and were deliberately not authored by the train.
3. **S13 exploit ledger sitting.** 71 verified lines, 14 mechanism families.
   No fixes authored, by design.
4. **S14 non-card parity triage sitting.** 174 findings across 173 entities.
   No fixes authored, by design.
5. **C2 escrow release (R102).** Four fanfare conclusions remain PROVISIONAL
   pending probe (b).
6. **Build 0.2-296 distribution + telemetry notice** to the table.
7. **R105 fact-sheet item** — carried in tonight's Track E.
8. **S7 §4 probes.** The two family-C candidates (+2 block offset, Fanfare
   accounting residual) are [USER]-gated candidates, not scheduled work.
9. **S8's 8 flagged items** and **S10's reskin candidates** — candidates, not
   verdicts; RESKIN/REDESIGN remains [USER]'s call per north-star.

**Parked deliberately by the train:** ledger-repair pre-drafts and any
S2/S4-derived amendment; any S13/S14 finding resolution; the escrowed numbers.
The artifacts merge; the derived work waits.
