# Surplus-dispatch-3 — BLOCKERS

Charter §6: appended by the research integrator from the agents' returned
messages. Nothing here is a decision. Three sections: (1) stop-work /
data-loss class, (2) runner and environment facts that **bound** tonight's
non-findings, (3) the outputs that were deferred and what a re-run needs.

Compiled 2026-08-27 by the research integrator. No git command was run and no
file outside `review/dispatch3/BLOCKERS.md` and `review/dispatch3/MORNING-READ.md`
was written.

---

## 1. Stop-work / security / data-loss class

Three items. Each names the file that reports it and what it blocks.

### 1.1 Twenty-five of the twenty-seven contact sheets in `art/` are dead — the R212(1) veto route is closed

**Reported by:** the S17 Klee, Furina, and icons/UI/models/VFX agents
(`review/dispatch3/s17-art/s17-klee.md`, `s17-furina.md`,
`s17-icons-ui-models-vfx.md`).

**What is gone:** the `art/candidates/` directories the sheets reference are
missing from disk. The HTML contact sheets survive; the images they point at do
not. Named casualties:

- `contact_sheet_eb88_energy_orb.html` (M19) — 21 images, none resolvable.
- `contact_sheet_eb54_s4g12.html` (S4-G12).
- The EB-65 sheet.
- **Every Klee sheet — 60 of 60 candidate directories missing.**

**What it blocks.** R212(1) delegates art picks to Claude *on the condition
that [USER] can veto on the sheet*. A sheet that cannot be walked is not a
veto route. So: M19, S4-G12, EB-65 and every open Klee art pick cannot be
progressed as written — not by Claude under the ladder, and not by [USER] on
review — until the candidate directories are re-materialised. This is a
data-loss finding, not a defect in the sheets.

**What it is not.** Nobody established *why* the directories are absent
(gitignored-and-never-committed, cleaned, or lost). No agent attempted a
recovery and none was authorised to.

### 1.2 The deployed version string `0.2-1159` is not valid semver — a dependent mod would be refused

**Reported by:** `review/dispatch3/s20-release-readiness/s20-packaging-metadata-credits.md`.

**The mechanism, as the agent cited it:** `SemanticVersion.cs:102-107` throws on
a `-` inside the Minor field. Our version string puts one there. The mod still
**loads** — the parse failure is swallowed — but its parsed version is `null`.
`ModManager.cs:810-812` then refuses any future mod that declares a dependency
on us with a `min_version`.

**What it blocks.** Nothing today: no third-party mod depends on us. It blocks
the day one does, and it blocks any public-release posture that assumes other
mods can pin us. The remedy shapes the agent sketched all **amend LAW R70**
(the version-stamp law), so this is not a hygiene fix — it returns to [USER].

### 1.3 EB-65 cannot be closed mechanically — no rank-1 row exists for the seven Furina sigils

**Reported by:** `review/dispatch3/s17-art/s17-furina.md`.

R212(1) authorises Claude to apply *shortlist rank 1* without asking. For the
seven Furina sigils there is **no rank-1 row to apply**. The delegation ladder
has nothing to act on, so EB-65 stops at the gate rather than closing. Compounded
by 1.1: the sheet route that would let [USER] settle it by eye is also down.

---

## 2. Runner and environment facts that bound tonight's non-findings

None of these is stop-work. Each one **narrows** a claim that would otherwise
read as absence-of-evidence. Read this section before quoting any NON-FINDING.

### 2.1 The Windows `python` / `py` App Execution Aliases broke mid-run

Symptom: under Bash, `Permission denied`; under PowerShell, a hang. It broke
partway through the night, so early and late runs used different invocations.
Every affected agent routed around it by calling the real interpreter by
absolute path (the primary checkout's `.venv/Scripts/python.exe`, or the
machine Python at `C:\Users\Monty\AppData\Local\Python\bin\python.exe`).
Reported by the lane handoffs and by the S18 act agents. **Consequence:** any
command in a handoff written as bare `python` needs the absolute-path form on
this machine until the alias is repaired.

### 2.2 GitHub REST rate limits and the code-search auth wall bound every S12 "no released mod does X"

`s12-public-patterns/s12-00-joined-read.md` §4 records it: **GitHub code search
is behind an auth wall for this runner**, so no agent could enumerate mods that
*consume* a given BaseLib API. The REST core API also rate-limited two agents
(S12a, S12c) partway; both fell back to `raw.githubusercontent.com` and source
tarballs. `nexusmods.com` returned HTTP 403.

**So "no released mod consumes X" is a limit of the search, not a proof of
absence.** Named in search results and deliberately **not opened** (recorded so
a later pass does not re-search them): `spencerqfox/sts2-custom-mods`,
`jiegec/STS2FirstMod`, `lamali292/sts2_example_mod`, `lamali292/WatcherMod`,
and the longer list in that file's §4.

### 2.3 No live capture was possible all night

[USER] was playtesting on mod `0.2-1155` and the charter forbade launching,
deploying to, or writing to the game installation. Consequences, all recorded
by their own files:

- **Every S16 capture slot is "capture pending."** The charter asked for three
  annotated captures per body; there are none.
- **Lane A rendered nothing** — its strongest evidence is "the scene loads in
  the headless editor and carries the nodes, animations and states claimed for
  it." Whether any motion *reads* as an attack or a tell is unmeasured.
- **Lane C's contact-sheet assembler is proven on five generated fixture PNGs
  only.** The capture half does not exist in that lane.
- **Lane D rendered nothing** — its `proof_prism.tscn` has never been parsed by
  Godot. Its evidence is strings and method dispatch, offline.
- **S20 carries six "needs the game" rows**, and two S20 performance
  measurements are barred outright: the mod's share of boot time, and the
  resident-texture ceiling.

### 2.4 Spine clip durations and bone/slot counts were not readable

They live in binary `.skel` files and no parser was written tonight. Reported by
all four S16 body files. Everything S16 says about clip *duration* is therefore
inferred or absent, not measured.

### 2.5 One S20 agent's PCK v3 index parse returned zero files

Consequence: the `kreon_regular.ttf` cmap (which glyphs the shipped font
actually covers) and the character-select sizing stay **UNKNOWN** in
`s20-controller-resolution-text.md` / `s20-localization-seams.md`. Note that
lane A independently *did* write a working MegaDot format-3 pack reader
(`tools/animation_bakeoff/pck.py`), so this is a gap in one agent's night, not
a repo-wide capability gap.

### 2.6 Two S18 agents collided on a scratch directory

The Act-1 and Act-2 agents used the same scratch path. **No data was lost** and
both files completed; recorded because the next dispatch should namespace
scratch per agent. Also from S18: one PowerShell extraction timed out. Routed
here rather than to the sitting by `CURATION.md` §S18.

### 2.7 Two test-harness traps that are **not** repo red

- `tools/run_lints.py --lane local` exits **2** on `card-distinctness` in any
  worktree without `game_ref/` — it prints *"no game_ref/ pools found."*
  `game_ref/` is gitignored local reference data. Observed in lane C.
- Run from a shell with no valid stdin handle, **~74 repo tests that shell out**
  fail with `OSError: [WinError 6] The handle is invalid` inside
  `subprocess.Popen` (lane C saw ~74; lane D saw the same class narrowed to the
  four `test_art_coverage.py` tests). They pass from a normal console, or with
  `--capture=sys` / `-s`. Lane C's own CLI test pins `stdin=subprocess.DEVNULL`
  and is immune; the repo's existing subprocess tests do not.

### 2.8 The primary checkout moved three times during the dispatch

`PREFLIGHT.md` recorded `main` at `223a4ff`. Lane B observed it reach `c09b6b6`
(PR #108, Kokomi's relic and power icons) with a pck rebuild at 20:39, and then
`98fb3a0`. Lane D branched from `c09b6b6`, not the preflight SHA. **Any number
in this dispatch that was measured against the primary checkout carries the SHA
it was measured at, and should be re-taken before it is quoted.**

---

## 3. Deferred outputs

Six research outputs were **not produced**. The cause is one event, not six:
the account usage limit was hit at ~02:10; the resumed runs were then throttled
to roughly **one tool call per two minutes for eight hours** and produced no
file; the orchestrator stopped them at **10:25**.

**No substitute content was written for any of them.** A gap is recorded as a
gap.

| # | Deferred output | Charter home | What a re-run needs |
|---|---|---|---|
| 1 | **S17 — companions art family** | §4 S17 | The same prompt, unmodified. ~1–3 h unthrottled. |
| 2 | **S17 — joined ledger proposal + disjoint batches** | §4 S17 | The same prompt. Depends on #1 (it is one of the five families it joins), so run #1 first. ~1–3 h. |
| 3 | **S19 — audio / VFX grammar and free-tool census (the entire stream)** | §4 S19 | The same prompt. Nothing of S19 exists on disk. ~1–3 h. |
| 4 | **S20 — save / update / removal family** | §4 S20 | The same prompt. ~1–3 h. |
| 5 | **S20 — joined readiness matrix** | §4 S20 | The same prompt. Depends on #4; five of the six families are on disk. ~1–3 h. |
| 6 | **S16 — joined capability matrix** | §4 S16 | **See the note below — this one is different.** |

### 3.1 The S16 matrix is on disk but was never confirmed by its author

`review/dispatch3/s16-animation/s16-joined-capability-matrix.md` **exists and is
complete on disk** (712 lines, written 00:41). Its agent's *return* then failed
on the usage limit, so the file was never confirmed by the agent that wrote it,
and `CURATION.md` (written 02:40) lists S16 under "pending curation" believing a
rewrite was in flight.

**How to treat it:** as a real output whose author never signed off. Quote it,
but say so — every citation of it in `MORNING-READ.md` carries that flag. A
re-run would be a *confirmation* pass, not a fresh write.

### 3.2 Curation status of the deferred streams

`CURATION.md` records one completed touchpoint each for **S15, S12+S13, S18 and
S14**. It records **S16, S17, S19 and S20 as pending**. Charter §8 requires
"Fable curation recorded once per completed research stream" — for the four
curated streams that bullet is met; for S16/S17/S20 the streams are partial and
uncurated, and S19 does not exist.

---

## 4. What is NOT a blocker

Recorded so nobody re-raises it. Lanes A, B, C and D all completed, all pushed
to their own branches, all green on their targeted tests, and none merged or
deployed anything. No governing doc, sheet, constant, production asset,
registered experiment, live game installation, or [USER]-owned checkout was
altered by any agent or lane. `M45`, `M46`, enemy mappings, taste, rights,
money and ship scope remain unruled.
