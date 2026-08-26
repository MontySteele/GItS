<!-- Verbatim charter text supplied by [USER] in chat, 2026-08-26. Not edited by the orchestrator. Preflight facts and version skew are in PREFLIGHT.md. -->

# Surplus-dispatch-3 synthesized charter — 2026-08-26

> **Lifecycle:** research rail ACTIVE until the morning read, then HISTORICAL;
> tooling rail ACTIVE until its branch handoffs are accepted or closed.
>
> **Purpose:** let [USER] playtest while Claude Code (a) builds the shared art,
> animation, enemy, and visual-QA tooling that later production needs and (b)
> spends overnight capacity on citation-bound research and sitting preparation.
> This charter decides no design, taste, lore, behavior, rights, money, or ship
> call.

## 0. Preflight — live checkout wins

Before dispatching anything:

1. Read `CLAUDE.md`, then `docs/current/STATE.md`; read LAW / QUEUE / BACKLOG /
   OPERATIONS as the task reaches them.
2. Record `git rev-parse --short HEAD` and `git status --short`. Treat every
   existing modification and untracked file as [USER]-owned. Do not reset,
   overwrite, stage, or "clean up" the live checkout.
3. The source charter claimed HEAD `f38cd90`. That object does not resolve in
   the checkout used for this synthesis (live HEAD was `e2af89f`). If it is
   also unavailable to the runner, write `DRAFT-SHA-UNAVAILABLE`; do not use
   the claimed SHA as evidence and do not stop useful work merely to recover
   it.
4. Check for
   `review/active/full-mod-roadmap-2026-08-26.md`, BACKLOG `EB-147`–`EB-155`,
   and QUEUE `M46`. They may be present as uncommitted [USER]-owned work. If
   absent, use the roadmap attached to this charter as planning context and
   report the version skew; **do not mint replacement IDs**.
5. `S11` is already issued: it produced `docs/current/atlas/README.md` and the
   architecture atlas in surplus-dispatch-2. This dispatch therefore begins
   at **S12**, not S11.

## 1. Reconciliation result

The two planning passes agree that the existing world-side canon galleries
should not be repeated and that implementation sockets are the immediate
unknown. Each also found work the other did not.

| Source | Distinct contribution | Synthesized route |
|---|---|---|
| Chat charter | Public-mod pattern mining and base-engine socket trace | `S12` + `S13`, feeding `EB-149`, `EB-152`, and `EB-154` |
| Chat charter | Elemental Resonance pre-read | `S14`, retained as surplus-only and non-critical-path |
| Chat charter | One world-track ruling agenda from finished galleries | `S15`, first research artifact in the morning read |
| Full-mod roadmap | Native-animation grammar and no-paid-tools bake-off | `S16` research + Tool lane A, feeding `EB-147` |
| Full-mod roadmap | Art coverage/provenance ledger and visual QA gates | `S17` research + Tool lanes B/C, feeding `EB-148`/`EB-151` |
| Full-mod roadmap | Implementation-aware enemy map, not another canon atlas | `S18`, feeding `EB-150`; neutral runtime proof is Tool lane D |
| Full-mod roadmap | Audio/VFX and public-release/accessibility gaps | `S19` + `S20`, feeding `EB-153`–`EB-155` |

The chat charter's "these four and nothing else" clause is retired. It omitted
the explicitly requested art/animation pass and the tooling foundation that
makes later enemy production economical. Its useful no-verdict research rules
remain in force on the research rail.

## 2. Two rails, different mutation authority

### Research rail — S12 through S20

- Outputs only under `review/dispatch3/` on a dedicated dispatch integration
  branch. No `docs/current/`, sheet, constant, runtime, test, manifest, PCK, or
  production-asset edit.
- Agents may commit their one assigned output in their own sibling worktree.
  The research integrator may collect only those `review/dispatch3/` commits
  onto the dispatch branch. Nothing merges to `main` before [USER]'s morning
  read.
- No suite run is required for prose-only research. Citation/link and output-
  shape checks are required.

### Tooling rail — lanes A through D

- Real code, tests, and synthetic proof assets are allowed **only** in one
  sibling worktree and branch per lane.
- Each lane runs its targeted tests/lints and returns a commit SHA, commands,
  findings, known debt, and merge risks. No lane merges, deploys, alters live
  game files, or edits governing docs.
- Production art, enemy mappings, and shared PCK/build-script edits remain
  single-owner. When two lanes need one shared file, one owns the edit and the
  other supplies a patch note or fixture rather than racing it.

This split resolves the source charter's conflict between "Claude works on
tooling" and "no code/no suite/no landings." Research remains non-mutating;
tool implementations exist as reviewable branch handoffs, not surprise
landings.

## 3. Standing constraints — all streams and lanes

1. **Zero design authority.** Outputs describe, catalog, test, and order. A
   technical recommendation is `PROPOSED`; a mapping, mechanic, taste, lore,
   public-rights, spend, scope, or ship choice is [USER]'s.
2. **Dormant rows are prohibited targets (R183).** `DORMANT / NO-SPEND` rows,
   including `SKIP-10.9`, may appear in a cited pattern table but are never
   built, prototyped, or promoted because capacity exists.
3. **One sibling worktree per workstream.** No agent edits from the live
   checkout. Never link or copy `game_ref/` or another gitignored asset tree
   into a worktree.
4. **Local ignored sources are read-only.** A local-only agent may read the
   primary checkout's `game_ref/` or decompile by absolute path while writing
   only in its sibling worktree. If the runner lacks them, file a deferral;
   never approximate from memory.
5. **Citation discipline.** Every factual research claim carries repo
   `file:line`, public-source URL pinned to a commit/tag where possible, or
   commit SHA. Unpinned claims are `UNVERIFIED` inline. A non-finding is a
   valid result.
6. **Primary technical sources only.** For public-mod/tool research, use the
   source repository, release, documentation, or license—not summaries. For
   mutable canon, pin the retrieval date and source.
7. **No copying.** LAW permits Downfall and other mods as reference-reading:
   abstractions/patterns may inform questions; code, scenes, art, audio, and
   text are never copied verbatim.
8. **No registered measurements.** Do not open a balance window, move a stamp,
   run an uncountersigned experiment, or interpret [USER]'s playtest.
9. **Fable curation.** One curation touchpoint per research stream before the
   morning read. Curation may select, dedupe, and order; it may not rewrite
   factual claims into stronger ones or turn candidates into verdicts.

## 4. Research rail

### S12 — public StS2 subsystem pattern mining

**Correction to the source charter.** Do not begin from "Downfall solved every
subsystem." At `lamali292/Downfall@32e61132052ae58e32cd33342d24136ffe18be12`,
the official README and repository tree prove a released StS2 mod, build/PCK
pipeline, character scenes, localization, relic/potion implementations, and
some custom creature models. The tree does **not by itself prove** custom
encounter pools, acts/maps, or world-event models. Downfall is the first
source where it has evidence; a subsystem with no implementation there becomes
a source hunt and may end as a NON-FINDING.

Primary starting points:

- `https://github.com/lamali292/Downfall/tree/32e61132052ae58e32cd33342d24136ffe18be12`
- `https://github.com/lamali292/Downfall/blob/32e61132052ae58e32cd33342d24136ffe18be12/README.md`

**One agent per subsystem:**

| ID | Subsystem | Question |
|---|---|---|
| S12a | Enemy registration, AI, intents | Which public StS2 source, if any, proves a hostile enemy lifecycle rather than a player-owned summon/model? |
| S12b | Boss and encounter integration | How are encounters/pools and boss-specific lifecycle registered, or is there no public implementation? |
| S12c | Act and map hooks | Which public source proves act/map/node mutation while retaining base flow? |
| S12d | World-event runtime | Distinguish an actual event model/choice tree from a project-local "Events" hook namespace |
| S12e | Relic and potion hooks | Registration, trigger, rarity, pool, reward, and shop patterns; Downfall is expected to be useful here |
| S12f | Save/version compatibility | Evidence for stable IDs, migrations, modded-save separation, update/removal behavior; absence stays absence |
| S12g | Packaging/localization/distribution | Build outputs, PCK/DLL/manifest, dependency pins, release workflow, install route, and localization topology |

**Output:** `review/dispatch3/s12-public-patterns/s12{a-g}-*.md`.
Each file: overview ≤15 lines; pattern table (pattern / purpose / pinned
source / base type); gotchas; transfer questions against our BaseLib/Harmony
abstractions; explicit NON-FINDINGS and search boundary.

**Acceptance:** seven files; no row treats a filename match as proof; every
pattern cited; no code/design proposed; curation complete.

### S13 — StS2 engine socket probe (LOCAL READ-ONLY)

Read the base decompile and BaseLib directly. This is authoritative where S12
finds public-mod gaps.

**Output:** `review/dispatch3/s13-engine-sockets.md`:

1. Type inventory for hostile monsters, encounters/bosses, acts/maps, world
   events, relics, potions, saves/IDs, and asset lifecycle.
2. Instantiation-to-death call trace for one hostile enemy and entry-to-exit
   trace for one world event, with `file:line` at each load-bearing step.
3. Socket table keyed to S12a–g.
4. Animation coupling: what is required at declaration/load time versus lazy
   resolution, and which missing resource shapes fail hard or fall back.
5. NON-FINDINGS and remaining questions.

**Gate:** local runner can read the primary checkout's ignored sources. If it
cannot, write `review/dispatch3/s13-DEFERRED.md` with the missing paths and no
substitute claims.

**Acceptance:** joins to S12; hostile enemy and world-event meanings are not
confused with player hooks; animation coupling exists; curation complete.

### S14 — Elemental Resonance pre-read (SURPLUS-ONLY)

Retained from the chat charter because it is independent and potentially
useful, but it is **not evidence that Resonance belongs in public v1** and it
does not outrank presentation, world, or release foundations.

**Output:** `review/dispatch3/s14-resonance-preread.md`:

1. Dated canon census of current resonance effects, including single-element
   and special/event variants, with exact-source citations.
2. Structural read: what composition/state each effect keys from and whether
   it is fixed or dynamic.
3. Primary-source prior-art scan for composition passives in relevant
   deckbuilders/co-op mods; NON-FINDING allowed.
4. Questions-only interaction surface against reactions, co-op seats,
   companion nations, banner limits, UI, and save identity, each with the
   governing repo pointer.

**Acceptance:** no proposed numbers, recommendation, or declarative design in
section 4; every mutable canon claim dated; curation complete.

### S15 — world-track ruling agenda

Compile the already-finished enemy, boss, Ancient, event, and potion/relic
galleries into one walking order. Do not commission another candidate deck.

**First action:** dedupe against QUEUE, the 2026-08-08 sitting agenda, current
sitting reads, and `M46`. Already ruled/agendized questions are linked, not
re-listed.

**Output:** `review/dispatch3/s15-world-sitting-agenda.md`:

1. Decides-nothing banner; QUEUE remains canonical.
2. One-word calls first, then short calls, then discussions.
3. Every item gives one inline context sentence, exact source pointer, and
   answer shape (pick-one / yes-no / open), with no recommendation.
4. Gap appendix for gallery questions with no QUEUE row; the agenda mints none.
5. Dedupe log at top.

**Acceptance:** a cold read suffices to walk the sitting; every item resolves
to a source; no existing ranking is silently changed; curation complete.

### S16 — native-animation grammar and corpus

Define the common evidence schema once, then fan out across four bodies:

- a base/simple player character;
- a base/complex player character;
- a normal enemy;
- an elite or boss.

For each: scene/resource topology, node/layer/bone count, animation/state
names, durations/transitions, intent/attack/hit/death tells, VFX/audio hooks,
fallback behavior, authoring dependency, runtime/performance observables, and
three annotated captures where available.

Include a public-mod sidecar comparing native layered/cutout approaches. Base
Spine assets may be inspected to understand the runtime contract; no Spine
purchase or proprietary-authoring dependency may be proposed as the answer.

**Output:** `review/dispatch3/s16-animation/` plus one joined capability matrix
for layered sprites, cutout/skeletal 2D, mesh deformation, and particles/
tweens. Recommendations are technical and labeled PROPOSED.

**Acceptance:** common schema, four corpus files, joined matrix, source/license
citations, explicit unknowns, curation complete.

### S17 — art coverage, provenance, and batch plan

Start from the live tools, not prose. Re-run `tools/art_coverage.py` and
`tools/art_lint.py`; record tool, date, checkout, and exit status. The synthesis
baseline was 39 / 294 card-sized outputs covered and 255 missing, but the live
run wins.

Fan out by non-overlapping owner/family: Klee; Furina; Kokomi; companions;
icons/UI/models/VFX. Populate a draft ledger with expected id, source,
rendered output, packed path, fallback, private/public rights tier, review
state, collision/duplicate state, and blocking unknown.

**Output:** `review/dispatch3/s17-art/` with a joined ledger proposal and
disjoint production/tooling batches. No mass image generation and no rights or
taste verdict.

**Acceptance:** card art is not mistaken for total visual coverage; private
placeholder and public-safe coverage stay separate; every batch has one owner;
curation complete.

### S18 — implementation-aware enemy feasibility

Use the existing remap atlas and reskin gallery. Do not repeat Genshin canon or
invent a second ranking.

One agent per act plus one boss/elite integrator annotates: asset/rig family,
required tells/states, variants/reuse, VFX/audio surface, estimated complexity,
RESKIN/REDESIGN evidence, and socket uncertainty. Use provisional columns until
S13 completes; the integrator joins S13's final socket keys afterward.

**Output:** `review/dispatch3/s18-enemy-feasibility/` and one joined matrix.

**Acceptance:** every mapped encounter has a row or explicit exclusion;
unknowns stay unknown; no mapping verdict; no `SKIP-10.9` prototype; curation
complete.

### S19 — audio/VFX grammar and free-tool census

Census cues/surfaces for characters, reactions, companions, enemies, UI,
rooms, and transitions: hook, format, layering, timing/readability constraint,
fallback, packed path, rights tier, and capture/test seam. Research free tools
and licenses from their primary documentation. Do not settle sonic identity or
generate a production library.

**Output:** `review/dispatch3/s19-audio-vfx.md` with cue matrix, missing/
fallback report, tool/license table, and fanout-ready asset-family briefs.

**Acceptance:** audio and VFX are distinct but join on event/cue IDs; no taste,
purchase, or public-rights verdict; curation complete.

### S20 — release, accessibility, and localization surface census

Split among: save/update/removal; 1/2/3-player; packaging/metadata/credits;
performance/size/load; controller/resolution/text; color/effect/reduced-motion;
localization seams. This is an inventory, not a promise of support.

**Output:** `review/dispatch3/s20-release-readiness/` and one joined matrix of
case / reproduction / current status / evidence / automation candidate /
[USER] scope call.

**Acceptance:** UNKNOWN is legal; defects and scope calls are distinct; no
language/player-count/accessibility/ship promise is invented; curation
complete.

## 5. Tooling rail

### Lane A — native animation bake-off (`EB-147`)

Use one original synthetic rig and one required-motion suite across layered-
sprite, cutout/skeletal-2D, mesh, and particle/tween approaches. Pass each
through source → export → PCK → live capture where the runner permits. Measure
repeatability, source burden, package/runtime cost, and failure modes.

**Owns:** its synthetic sample directory and lane-specific automation only.
**Does not own:** production character scenes or the shared PCK script unless
the orchestrator assigns that single file here.

**Handoff:** branch/commit, exact commands, captures, targeted checks, and a
PROPOSED production grammar.

### Lane B — art/provenance ledger (`EB-148`)

Implement one machine-readable ledger and report joining expected surfaces to
source/output/packed path/fallback/rights/review state. It must report private
placeholder coverage separately from public-safe coverage and carry tests for
missing packed paths, stale rows, and unintended fallback.

**Owns:** ledger schema/tool/tests. **Does not own:** visual QA build gates or
production asset selection.

### Lane C — visual QA gates (`EB-151`)

Implement independent checks for export-log errors, resource/animation
dependencies, unintended cross-character fallback, package contents, and
deterministic capture/contact-sheet assembly. Consume Lane B's proposed schema
through a fixture or adapter; do not co-edit its core files.

**Owns:** QA gates/fixtures/capture tool. Shared build-script changes belong to
exactly one named integrator.

### Lane D — neutral enemy seam (`EB-149`)

Begin only after S13 identifies a credible socket, or stop with a documented
blocker. Replace one ordinary enemy's presentation with original geometric
proof art, preserving mechanics and avoiding global base-resource overwrite.
Capture reachable idle/intent/attack/hit/death and co-op surfaces; test clean
load/combat/save/uninstall where possible.

**Owns:** neutral proof model and seam spike. **Does not own:** Genshin mapping,
enemy mechanics, act pools, or production art.

## 6. Orchestration

### Priority

1. **Critical tooling:** lanes A, B, C.
2. **Critical research:** S13 engine sockets, S15 world agenda, S16 animation,
   S17 art ledger, S18 enemy feasibility.
3. **Foundation research:** S12 public patterns, S19 audio/VFX, S20 release.
4. **True surplus:** S14 Resonance.
5. **Conditional:** lane D after S13; never brute-force the seam blind.

### Parallelism and joins

- S12a–g are independent; their integrator joins the seven files.
- S13 is local-only and independent while running; it joins S12 and supplies
  final socket columns to S18 and the go/no-go evidence for lane D.
- S16 corpus bodies, S17 asset families, S18 acts, and S20 readiness families
  are internally disjoint.
- Lanes A–C run independently in separate worktrees. Lane D is conditional.
- No two agents edit the same output file. One integrator per joined matrix.

### Output/branch map

- Research: `review/dispatch3/` on a dedicated dispatch branch.
- Tooling: four separate branches/worktrees; no automatic integration branch.
- Blockers: `review/dispatch3/BLOCKERS.md`, appended by the research integrator
  from agent messages; agents do not race the file.
- Morning summary: `review/dispatch3/MORNING-READ.md`, written last from actual
  outputs, never pre-filled with expected conclusions.

### Morning read order

1. Stop-work/security/data-loss blockers.
2. Tool lanes A–C handoffs; lane D result or exact blocker.
3. S15 world sitting agenda.
4. S12 + S13 joined socket read.
5. S16 animation + S17 art + S18 enemy feasibility.
6. S19 audio/VFX + S20 release readiness.
7. S14 Resonance last.

## 7. Failure rules

- Cannot cite it: mark UNVERIFIED or NON-FINDING; do not launder confidence.
- Cloud clone lacks decompile/`game_ref/`: defer S13; do not approximate.
- Public mod lacks a named subsystem: widen the primary-source search once,
  record the boundary, then NON-FINDING. Do not read a hook namespace as a
  player-facing world event.
- Existing output/branch/path already owned: stop that worker and reassign a
  disjoint row; do not merge concurrent drafts by hand.
- Tool lane needs a design/taste/rights/money/ship call: build the neutral
  mechanism or fixture, record a numbered question, and stop at the gate.
- Tool tests expose unrelated existing red: report it with command/output and
  prove the lane's targeted tests separately; do not fix outside scope.
- Time/capacity ends: preserve partial cited rows and blockers. Coverage is
  valuable; invented completeness is not.

## 8. Final dispatch acceptance

The dispatch is ready for [USER]'s morning read when:

- every started research stream has its required output, explicit deferral, or
  cited partial plus blocker;
- Fable curation is recorded once per completed research stream;
- lanes A–C return isolated, tested branch handoffs; lane D returns a handoff
  or S13-grounded blocker;
- no governing doc, production sheet/asset, registered experiment, live game
  installation, or [USER]-owned checkout change was altered;
- `M45`, `M46`, enemy mappings, taste, rights, money, and ship scope remain
  unruled;
- the morning summary distinguishes facts, non-findings, defects, technical
  proposals, and [USER] questions.

*Synthesized from the chat-authored surplus-dispatch-3 draft and
`review/active/full-mod-roadmap-2026-08-26.md`; corrected against the live
checkout and the pinned public Downfall repository on 2026-08-26.*
