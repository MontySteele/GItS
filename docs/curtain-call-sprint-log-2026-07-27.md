# "Curtain Call" — Furina distinctness / register / structure sweep — SPRINT LOG

Date: 2026-07-27. Status: EXECUTING (this file opens before any measuring
cell runs and closes with the graded predictions; sections are appended in
execution order, never rewritten). Pre-registration: the sprint doc ratified
in chat 2026-07-27 ([USER]: "if there are no open questions, please
proceed", plus the three AskUserQuestion ratifications recorded in §1
below). Ruling number: R85 (DECISIONS entry lands with the close-out).

Baseline world: seed 11, runs 600, RT7/D12/P3/C4 (`python -m
tier05.exp_roster_anchors`), drafter D12 FROZEN — no scorer changes in this
sprint. Gate: R81 (uniq ≥70, maxclu ≤5, neardup ≤0.40/card; vocab/top%
report-only). Furina baseline: uniq 62, neardup 0.94/card, vocab 26
(re-read this morning, matches the pre-registration).

## 1. Open questions surfaced and ratified BEFORE execution

The pre-registration's counting check (§7 note) was run first and FAILED as
written — three §7 move-column entries contradict the sheet of record:

- `warmup_act` and `dramatic_entrance` are marked skill→attack but are
  ALREADY attacks (and §4's "current: 13 attacks" includes them, so the
  listed moves cannot reach Attack 17);
- `pit_orchestra` is marked C→U but is already uncommon.

Landing §7 as written gives A14/S49/P15 and C29/U28/R17 against §4's
17/46/15 and 22/32/19. Surfaced to [USER] with options; RATIFIED 2026-07-27:

1. **"I author extra moves to hit §4"** — the session red-pens the
   additional moves needed to land §4 exactly; all such moves are marked
   (authored) in §2 and get [USER] eyes at PR review.
2. **5th power = `quick_change`** (florid_cadenza's threshold design is
   ratified F-B1 work and fanfare-load-bearing; quick_change is generic
   Bright Idea parity — exactly the padding this sweep removes).
3. **4th rare = `showstopper` U→R** (its rewrite is a big-moment payoff;
   universal_revelry is the in-pool precedent for a rare gate; crescendo
   stays the draftable uncommon model card per its own §7 row).

## 2. The reconciled move set (the red-pen of record)

Verified by script to land EXACTLY on §4: **Attack 17 / Skill 46 / Power 15;
C 22 / U 32 / R 19** (5 basics untouched, pool size 78 frozen).

| move | cards | provenance |
|---|---|---|
| skill→attack (4) | standing_room_only; flood_of_emotion (authored); matinee_performance (authored); usher_the_waves (authored) | all from the damage-clone families; retype deletes hydro application (skill_tag dropped). undercurrent deliberately KEPT as the AoE hand-cast applier and usher's loss is the smallest single-target one — the §6 uptime rider is the check, and Track B's shrink clause fires on breach |
| skill→power (5) | fortissimo_guard; pit_orchestra; courtroom_drama; crowd_work; quick_change (ratified) | all activity-triggered, never per-turn (sheet header law) |
| C→U (10) | standing_room_only, crowd_work, audience_participation, witness_stand (listed); torrential_turn, dramatic_entrance, matinee_performance, tempo_change, poised_riposte, curtain_up (authored) | authored picks are payoffs moving to where payoffs are legal (§2 grammar) plus rewritten glue whose new shapes are uncommon-grade; curtain_up's rewrite gives the 0-cost slot a decide point |
| C→R (1) | thunderous_ovation (authored) | the archon defensive payoff — the steep fanfare-read block, high_tide's survival-axis mirror at rare |
| U→R (3) | flood_of_emotion (listed); showstopper (ratified); rapturous_applause (authored) | "Rare 19 — Fanfare payoff slots" (§4 derivation): all three are fanfare payoffs; rapturous_applause additionally earns the rare-Power floor grant, which is the structure-enables story cell 2 measures |

Register deviations forced by the ratified §3 grammar (the doc's own
lint clause governs its prose column): dramatic_entrance and high_tide
carry Fanfare reads → archon (§7 column said salon). Two Track-A-state
registers flip WITH their Track C rewrites: audience_participation
private→archon, many_waters_melody private→salon (the rewritten bodies
justify the voice; the Track-A bodies did not).

## 3. Cell 0 — re-baseline (PASS, with one environment caveat)

`python -m tier05.exp_roster_anchors` unchanged. All ten arms that can run
on a fresh clone reproduced the D12 §7 table EXACTLY (same-seed
determinism): klee 7.5/6.8/11.7, furina 17.2/4.2/2.8, kokomi 2.8/2.5/0.0,
ref_ironclad 10.2. The two real-anchor arms (real_ironclad 7.8,
real_silent 2.0) CANNOT run here: game_ref/ is gitignored and built
locally from the game DLL (loader.py:31 documents the fresh-clone
KeyError). Logged as an environment limitation, not instrument drift —
the STOP condition is not tripped. Consequence for all cells: the
roster table in this sprint is the 10-arm subset; the real-anchor
"rows must not move" tripwire is carried by ref_ironclad plus the house
rows, and the full 12-arm table should be re-run once on a machine with
game_ref/ before the next consolidation sprint quotes it.

## 4. Registered instrument definitions (fixed before any measuring cell)

- **hydro-application uptime**: fraction of player turns during which at
  least one enemy carried a LIVE hydro aura at any point in the turn,
  reconstructed read-only from the combat log (aura_applied element=hydro
  opens an interval on its target; the interval closes at a reaction event
  consuming that target's aura, an aura_wasted expiry on it, or fight end;
  enemy death mid-aura is not separately tracked — the small overcount is
  identical across cells, which is what the ±10% bound compares).
  Companion/relic/potion hydro counts: the metric is pool-level uptime,
  not per-card credit, matching kickoff §1's "primary application engine"
  language. Implemented in tier05/aura_telemetry.py, collected the same
  way the fanfare traces are.
- **fanfare payoffs drafted per deck**: `draft._reads_fanfare` count per
  final deck — the ghost check's own metric (exp_furina_ghostcheck), the
  null result's denominator, unchanged.
- **per-card take-when-offered**: taken / offered per card id over each
  cell's furina arms, from the draft telemetry.
- Cells 2 and 3 quote the same 10-arm roster invocation as cells 0/1 plus
  `python -m tier05.exp_curtain_call` (new, this sprint) for the riders.

## 5. Prediction grading rubric (written before cell 2/3 results were read)

Each §8 prediction grades PASS / FAIL / SUPERSEDED with the number beside
it; "within noise" for roster rows means within the paired-seed spread
observed between cell 0 and the published D12 table (which reproduced
exactly, so any house/anchor-row motion in cells 1–3 beyond ±1.5pp win /
±3pp act-1 is a defect finding, not noise):

1. cell 1 byte-identical → PASS iff all ten rows byte-identical.
2. gate → PASS iff uniq ≥70 AND neardup ≤0.40 at cell 3 (tool `--pool furina`).
3. vocab → PASS iff ≥32 at cell 3.
4. fanfare → PASS iff full-run win ≥5.0% at cell 3 AND payoffs/deck ≥2× cell-0
   fanfare-arm value; if payoffs ≥2× but win <5%, the compositional
   diagnosis is SUPERSEDED in writing (that null is itself a finding).
5. salon → PASS iff 12.0–15.0% at cell 3; ≥16% routes the trim experiment
   as its own pre-registered pass (clean denominator).
6. spotlight → PASS iff 2.2–6.2% at cell 3.
7. uptime → PASS iff cell-3 furina-arm uptime within ±10% relative of cell 0;
   breach shrinks the retype list (Track B constraint) and re-runs.
8. house/anchor rows unmoved (klee ×3, kokomi ×3, ref_ironclad) → PASS per
   the noise band above.
9. cell 2 fanfare delta < half of cell 3's total fanfare delta → graded on
   the win column.

## 6. Cell results

### Cell 1 — Track A only (renames + registers): PASS, byte-identical

All ten runnable rows byte-identical to cell 0 (diff of the row blocks is
empty). Prediction 1 PASSES as registered: the engine reads no card name
and no register field anywhere. The register census lands at salon 42 /
archon 23 / private 13 with 0 lint violations (tools/lint_furina_registers,
wired into test_sheet_lints).

### Cell 2 — Tracks A+B (structure only)

Track B landed: 4 skill→attack retypes (application deleted with the
skill_tag, per the cadence law), 5 skill→power conversions on new
activity-triggered powers (salon_deploy_block / salon_bow_block+encore /
encore_spend_draw / first_attack_draw / cross_examination — engine hooks at
the deploy, bow, spend, first-attack and first-reaction sites, each pinned
in tier0/tests/test_curtain_call.py), 14 rarity moves, upgrade-sheet deltas
re-keyed for the conversions, and the C# codegen ledger updated (six cards
join FURINA_DEFERRED_TO_CONSOLIDATION — §9 defers C# parity; blocked_reason
refuses each by name; manifest 71 generated / 7 blocked).

Two transients recorded, both by-design and resolved in Track C's commit:
- poised_riposte's rewrite landed EARLY (with B): its C→U promotion made
  the old flat body strictly dominated by house_call at common, and the
  domination lint is a commit gate. Cell 2 therefore carries exactly ONE
  Track-C-style body; cell-3 attribution notes it.
- ("furina", "maxclu") joins the gate test's KNOWN_FAILING with a pointer
  here: the four retypes join the plain-damage family (maxclu 5→6) before
  Track C breaks the family apart. The staleness test forces the entry's
  removal the moment it clears.

Cell 2 results (roster rows + riders; riders' cell-0 baseline taken
retroactively in a worktree at the Track A commit — content-identical to
cell 0 by the cell-1 proof — with the instrument copied in):

```
arm         win     act-1   uptime  apps/f  payoffs  deck   (cell 0 -> cell 2)
salon       17.2 -> 15.0    62.8 -> 63.5    59.6% -> 55.5%   3.36 -> 3.39   1.22 -> 0.62   23.8 -> 23.5
spotlight    4.2 ->  4.3    68.5 -> 63.7    40.0% -> 34.0%   2.43 -> 2.16   0.88 -> 0.46   23.6 -> 22.9
fanfare      2.8 ->  1.5    57.5 -> 46.2    39.8% -> 28.8%   2.23 -> 1.74   2.12 -> 1.26   21.0 ->  9.9f/19.6d
```

klee ×3, kokomi ×3 and ref_ironclad rows: BYTE-IDENTICAL to cell 0 (the
tripwire holds; the aura-telemetry instrument provably changed nothing).
Structure alone moved salon DOWN 2.2pp (padding removal, prediction 5's
direction), left spotlight flat, and HURT fanfare (payoff reach fell 2.12
→ 1.26/deck: rarity promotion cuts offer frequency under RARITY_ODDS
before the rewrites pay it back). Prediction 9's "structure enables,
rewrites deliver" now has a signed version: structure alone is negative.
The five new powers draft at 12–17% deck presence.

## 7. Gate re-read at cell 3 content (the tool, `--pool furina`)

| metric | cell 0 | cell 3 | gate | official band |
|---|---|---|---|---|
| uniq% | 62 | **76** | ≥70 PASS | 72–86 — INSIDE |
| neardup/card | 0.94 | **0.15** | ≤0.40 PASS | 0.24–0.36 — BELOW (better) |
| maxclu | 5 | **3** | ≤5 PASS | 4–5 — BELOW (better) |
| vocab | 26 | **34** | report-only | R81 guidance "mid-30s" — MET |

R81's named defect (the 12-card stat-only core + the clone families) is
paid. The furina KNOWN_FAILING entries are removed; the gate's red test
now bites Furina regressions at full strength.

## 9. Consequentials

- **furina-upgrades.yaml**: delta rows re-keyed for the five power
  conversions (power_amount) and re-commented for every rewritten body;
  showstopper's dead conditional_bonus key replaced ({damage: +3});
  lint_upgrade_coverage green. No inline upgrade: fields anywhere (R20).
- **Reserved-names lint**: all nine new display names pass
  lint_unique_names (266 card + 6 relic names unique, reserved list
  honored).
- **Art rehunt list** (renamed cards; verify plan.tsv col-10 wiki_title
  fit against the NEW name before locking any source — per art-pass law,
  file slugs stay mechanical so rows key on ids and nothing broke):
  | id | new name | current pick (col-10) | verdict to confirm |
  |---|---|---|---|
  | warmup_act | Stage Combat | Icon Emoji Paimon's Paintings 28 Furina 2.png | REHUNT — playful emoji vs combat choreography |
  | standing_room_only | The House Rises | Item Theater Tickets.png | plausible keep — full-house iconography |
  | graceful_retreat | Slip Backstage | Furina Expression 2.png | plausible keep — verify the expression reads "escape" |
  | curtain_up | In the Wings | Opera Epiclese - After The Forgotten Thief.png | plausible keep — house interior |
  | crowd_work | The Gallery Stirs | Astra Carnival Cat's Tail Gathering 2024 S5 Artwork.png | REHUNT — carnival ≠ courtroom gallery (archon voice) |
  | swelling_overture | Compose Herself | Chanson of Many Waters 2024-06-25 - Furina Shorts.png | plausible keep — solitary Furina |
  | tempo_change | Double Time | Icon Emoji Paimon's Paintings 29 Furina 1.png | REHUNT — emoji vs music direction |
  | pit_orchestra | Stagehands | Opera Epiclese Support Card Golden.png | plausible keep — house machinery |
  | audience_participation | The Crowd Answers | A Commemorative Photo Aether 1.png | REHUNT — Aether photo vs nation-audience (archon voice) |
- **C# / klee-mod**: Furina generated set regenerated twice (B, C);
  twelve cards in FURINA_DEFERRED_TO_CONSOLIDATION (each refused by name
  in blocked_reason; manifest 65/13). §9 stands: parity work ships in the
  consolidation sprint, and the two renderer-fixture tests note their
  deferred fixtures explicitly.
- **Schema note (REQUIRED, §10)**: `register: Optional[str]` is on the
  SHARED Card schema in tier0/engine/state.py. Columbina and all future
  characters inherit the column. The value vocabulary is per-character;
  Furina's is {salon, archon, private} enforced by
  tools/lint_furina_registers.py, and the third-instance rule generalizes
  the lint when a second character adopts registers. Nothing in the
  engine or drafter may ever read the field (cell 1 is the pin).

### Cell 3 — Tracks A+B+C, first read (seed 11, 600): the shrink clause FIRES

```
arm         win               act-1            uptime           payoffs/deck
salon       17.2 -> 14.5      62.8 -> 62.2     59.6 -> 54.9%    1.22 -> 0.60
spotlight    4.2 ->  2.8      68.5 -> 63.2     40.0 -> 34.0%    0.88 -> 0.43
fanfare      2.8 ->  2.0      57.5 -> 48.2     39.8 -> 29.3%    2.12 -> 1.23
```

House/anchor rows byte-identical to cell 0 for the third time. Salon and
spotlight land inside their predicted bands. Fanfare recovers half of cell
2's drop (1.5 → 2.0) but stays under baseline — and the hydro-uptime bound
BREACHES outside salon (fanfare −26% rel., spotlight −15%, salon −7.9%,
pooled −15%). The pre-registered Track B contingency fires exactly as
written: **the retype list shrinks.** The two AUTHORED retypes carrying
the most deleted application revert to damaging skills with their rewrites
and rarity moves intact — flood_of_emotion (both threshold strikes apply
again) and matinee_performance (every member-scaled hit applies: the
matinée seeds the stage it reads). The LISTED retype (standing_room_only)
and usher_the_waves stay attacks. Final type shape: **Attack 15 / Skill 48
/ Power 15** — a logged deviation from §4's Attack 17, on the authority of
§4's own shrink clause. Rarity shape unchanged (22/32/19); gate metrics
unchanged (76 / 0.15 / 3 / 34).

(§6 cell 3′ — the post-shrink re-run + seed-12 rider — and §8 graded
predictions are appended when the run completes.)
