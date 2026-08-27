# S20 — release readiness: performance, size, load

> **This decides nothing.** It is an inventory of what the shipped package
> costs today and how each cost could be measured. It is not a promise that any
> of it will be supported, optimised, or shipped. Every number below is a
> measurement or a citation; where a number would need the game launched, the
> row says so, because [USER] is playtesting tonight and no agent may launch,
> deploy, or touch the game installation.

Family: **performance / size / load**. Six sibling families (save/update/removal,
player count, packaging/metadata/credits, controller/resolution/text,
colour/reduced-motion, localization seams) run concurrently; where a row touches
theirs there is a one-line pointer and nothing more.

Retrieval date for everything below: **2026-08-26**. Checkout read: the primary
`C:\Users\Monty\Documents\GitHub\GItS` (read-only). Deployed mod read from the
live install: `manifest.json` version **0.2-1159**, matching the dispatch note.

---

## 1. The headline numbers, measured tonight

Measured with `ls`/`du` against the staged package
`klee-mod/dist/klee/` and the deployed copy
`<GameDir>/mods/klee/`; both are byte-identical in the four top-level files.

| Artifact | Bytes | Human | How counted |
|---|---:|---|---|
| `klee.pck` | 9,586,076 | 9.1 MiB | file size; also `klee-mod/assets/klee.pck` |
| `klee.pck.contract.txt` | 6,385 | 6 KiB | 132 `resource=` lines |
| `klee.dll` | 877,056 | 857 KiB | file size |
| `manifest.json` | 576 | — | |
| `images/cards/*.png` | **71,368,915** | **68.1 MiB** | **272 files** |
| **Deployed total** | **~82.7 M** | **79 MiB** (`du -sh`) | |
| Handoff zip (last built, `klee-v0.2-826.zip`) | 80,592,322 | 76.9 MiB | `klee-mod/dist/` |

**The single dominant fact of this family: the loose card-art directory is
7.4× the size of the PCK and 88% of the whole package.** The charter's framing
("9.6 MB now, 132 resources") describes the PCK only; the PCK is the small half.

Card PNG shape, measured across all 272 files (PNG IHDR bytes 24–25):

| Property | Value |
|---|---|
| Dimensions | 500 × 380, **all 272 identical** |
| Bit depth / colour type | 8-bit, type **6 = RGBA** for all 272 |
| Mean file size | 262 KiB |
| Largest | `thunderous_ovation.png` 488,905 B |
| Smallest | `flame_on_the_wick.png` 32,175 B |

---

## 2. Case inventory

Columns per the charter: case / reproduction / status / evidence / automation
candidate / **defect vs. [USER] scope call** (kept distinct — a defect is
something the code does not do what its own comments say; a scope call is a
trade [USER] owns).

### P1 — card art ships as opaque RGBA PNG; the alpha channel carries no information

- **Case.** `tools/art_process.py:296-297` composites every card portrait onto
  an opaque background (`Image.alpha_composite(Image.new("RGBA", out.size,
  CARD_BG), out)`) *because* alpha holes read as missing art, then saves at
  `art_process.py:301` (`out.save(dest)`) in RGBA. Every shipped card therefore
  carries a fourth channel that is constant 255.
- **Reproduction (run tonight, no game needed).** Seeded 20-file sample
  (`random.seed(7)`) re-encoded in memory with Pillow:

  | Encoding | Sample bytes | Ratio vs. shipped |
  |---|---:|---:|
  | shipped RGBA PNG | 5,729,949 | 1.00 |
  | RGB PNG, `optimize=True` | 4,963,255 | 0.87 |
  | JPEG q90 | 1,051,636 | 0.184 |
  | WebP q90 | 795,342 | **0.139** |

  Alpha extrema were `(255,255)` on **20 of 20** — no sampled card uses
  transparency at all.
- **Status.** **DEFECT (small, size-only)** for the RGBA-vs-RGB half: the file
  format contradicts the pipeline's own stated intent two lines above the save.
  Extrapolated at the 0.87 ratio that is ≈8.9 MiB of the 68.1 MiB.
- **Status.** **[USER] SCOPE CALL** for the lossy half: WebP/JPEG would take the
  art directory from 68.1 MiB to roughly 9.5 / 12.5 MiB (≈70 MiB off the
  download), and that is a taste-and-quality trade nobody but [USER] may make.
  Godot's `Image.Load` accepts `.webp` and `.jpg`, but `KleeArt.cs:60` hardcodes
  `cardId + ".png"`, so a format change is a code change, not a pipeline-only
  change.
- **Automation candidate: yes.** Seam: a size/format lint next to
  `tools/art_lint.py` asserting card outputs are opaque and in the ruled format.
- **What this does not establish.** Nothing about *visual* acceptability at any
  quality setting. That is eyes-on and [USER]'s.

### P2 — decoded card portraits are cached forever, uncompressed, with no eviction

- **Case.** `KleeCode/KleeArt.cs:30` — `private static readonly
  Dictionary<string, Texture2D?> Cache = new();`. `CardPortrait`
  (`KleeArt.cs:56-83`) loads a loose PNG with `Image.Load` and
  `ImageTexture.CreateFromImage`, then stores the texture (or the null) forever.
  The comment states the cache exists to avoid a per-frame decode, which it does;
  nothing ever removes an entry.
- **Arithmetic.** `ImageTexture.CreateFromImage` on a PNG-loaded `Image` yields
  an uncompressed RGBA8 texture: 500 × 380 × 4 = **760,000 B ≈ 0.72 MiB per
  card**. All 272 resident at once is **≈197 MiB** of texture memory that is
  never released for the rest of the session. For scale, the game's own
  first-party line reads `VRAM=338.3MB` at "main menu loaded (essential)" and
  `VRAM=820.6MB` at "complete"
  (`%APPDATA%/SlayTheSpire2/logs/godot2026-08-26T20.56.20.log:801,857`).
- **Reproduction.** **Not reproducible tonight — needs the game.** The shape
  would be: boot, note the `[Startup] Resource stats` VRAM line, open the card
  compendium so every card model renders a portrait, and read VRAM again. Note
  that `Resource stats` is only emitted at the two startup checkpoints in the
  logs read tonight, so a mid-session reading needs another source.
- **Status.** **UNKNOWN whether it is a defect.** The arithmetic is certain; the
  *ceiling in practice* is not, because whether the compendium instantiates all
  272 portraits at once was not observable tonight. If it does not, resident
  cost is bounded by cards actually seen in a run (tens, not hundreds).
- **Compare — Downfall.** Downfall does not do this for card portraits. Its
  cards resolve to an **atlas region inside the PCK**:
  `DownfallCode/Abstract/DownfallCardModel.cs:50-51` returns
  `"<id>.tres".CardImageAtlasPath<T>()`, and
  `DownfallCode/Extensions/StringExtensions.cs:13-19` resolves that to
  `atlases/card_atlas.sprites` under the mod's `images/` tree
  (Downfall@32e6113). Runtime `Image.Load` + `ImageTexture.CreateFromImage` does
  exist in Downfall, but at
  `DownfallCode/Voting/NVoteCard.cs:221` and
  `DownfallCode/Voting/NArtVotingCardContainer.cs:67,99` — the **art-voting**
  surface, not the shipped card path. The KleeArt header comment
  (`KleeArt.cs:11-14`) cites Downfall as proving the technique loads; that
  remains true, but it is not what Downfall ships card portraits on. The
  base game itself uses atlases too: the same log shows
  `AtlasManager: Loaded card_atlas with 875 sprites` (log line 806).
- **Automation candidate: partial.** The C# headless suite
  (`klee-mod/KleeTests/README.md:1-8`, "no Godot, no scene tree and no game
  launch") cannot exercise `Image.Load`. A capture-based check belongs to the
  visual-QA lane (Lane C), not here.
- **Defect vs. scope.** Whether to move card art into the PCK as an atlas is a
  **[USER] scope call** with real cost (it is the packaging topology, and
  `tools/build_pck.ps1` owns it); the missing eviction is at most a small defect
  and only matters if P2's ceiling is real.

### P3 — the "9.6 MB PCK" is imported lossless, not VRAM-compressed

- **Case.** `tools/build_pck.ps1` builds a throwaway Godot project whose only
  job is to import textures and export a pack (`build_pck.ps1:76-83`,
  `:771-774`), with no import-preset override for compression anywhere in the
  file (`grep -n "compress\|vram\|lossless"` returns only the header comment at
  `:4-10` and the import invocation).
- **Status.** **WORKS AS BUILT / UNKNOWN as a cost.** 132 resources in 9.1 MiB
  is small; whether any of them is a VRAM problem was not measured.
- **Automation candidate: yes** — a headless MegaDot import step already exists
  in the pipeline, so a contract-line report of per-resource decoded size is a
  script, not a new dependency.
- **Defect vs. scope:** neither yet. It is an UNKNOWN.

### P4 — startup work the mod does, itemised from the live log

Read from `%APPDATA%/SlayTheSpire2/logs/godot2026-08-26T20.56.20.log`, the
session that ran deployed **0.2-1159**. 62 `[klee]` lines total.

| Step | Evidence | Cost |
|---|---|---|
| DLL + PCK load by ModManager | log `:141-142` | UNKNOWN (no timestamps) |
| Harmony: 17 patch classes, applied one-by-one | log `:145`; `KleeMod.cs:38`, `KleePatchBootstrap.ApplyAll` | UNKNOWN |
| PCK merge proof read | log `:146`; `KleePck.LogStatus()` (`KleeMod.cs:42`) | 1 resource load |
| Scene telemetry | log `:147-171`; `Diagnostics/KleeSceneTelemetry.cs:82-140` | **26 `ResourceLoader.Load<PackedScene>` calls**, plus 7 re-reads for required-node checks (`RequiredNodes`, `:69-80`) |
| Loc injection (2 tables, ~60 rows + 10 merged pck tables) | log `:200-210`; `KleeMod.cs:78-…` | UNKNOWN |
| BaseLib custom-enum generation for **2,234 modded types** | log `:211` | UNKNOWN; this is BaseLib's work, driven by our model count |
| `KleeSelfCheck` — 19 rule families over 3 characters + every power in the assembly, with two compiled regexes | log `:223`; `Diagnostics/KleeSelfCheck.cs:52-…`, invoked as a `ModelDb.Init` postfix (`:589-593`) | UNKNOWN |
| `ModelIdSerializationCache` | log `:226` — Categories 26, **Entries 2,005**, Epochs 57 | UNKNOWN |

- **Whole-boot figure, first-party:** `[Startup] Time to main menu:
  16,896ms` / `(Godot ticks): 16818ms` (log `:786,800`). Across the five logs on
  this machine: 13,328 / 13,333 / 13,481 / 13,497 / 16,818 ms.
- **NON-FINDING: the mod's share of that is UNKNOWN and cannot be inferred.**
  All five logs on disk have `[klee] Initializing`, so there is **no unmodded
  baseline in the corpus**. Two other mods are also installed
  (`STS2AutoSlayMod`, `quick_fingers`), and one of them throws a manifest error
  every boot (log `:18-21`) — that is a packaging-family observation, pointer
  only.
- **Reproduction.** Not reproducible tonight — needs the game, and would need
  the install mutated (mod folder moved aside) which is forbidden. The clean
  shape is: three boots with `mods/klee` present, three with it absent, compare
  the `Time to main menu` medians.
- **Status.** **UNKNOWN.** Automation candidate: **yes** — the game prints the
  number itself, so a log-scraper over `logs/*.log` is the whole instrument.
  Seam: `understudy/` already parses game logs and already records wall-clock
  per run (`understudy/soak.py:1438`, `"wall_s"`).

### P5 — `godot.log` has no timestamps, so no phase inside boot can be timed

- **Case.** Every line in the log corpus read tonight is `[LEVEL] text` with no
  clock (`head -20` of the same file). The only time value in the file is the
  game's own two `[Startup]` lines.
- **Status.** **DEFECT-ADJACENT / NOT-SUPPORTED-BY-DESIGN** — it is the base
  game's log format, not ours, so it is not our defect; but it is the reason
  every row above says UNKNOWN.
- **Mitigation available to us, PROPOSED, not built:** the mod's own boot lines
  could carry an elapsed-milliseconds stamp from a `Stopwatch` started at the
  top of `KleeMod.Initialize` (`KleeMod.cs:29-31`) and read at the end
  (`:73`), which would make the mod's own share of boot self-reporting without
  a baseline run. That is a code change and belongs to a lane, not to this file.
- **Automation candidate: yes**, seam as above.

### P6 — per-combat and per-turn allocations visible in code

Read across `klee-mod/KleeCode/` (384 `.cs` files, 44,531 lines).

| Finding | Evidence | Read |
|---|---|---|
| **No per-frame mod code.** `grep -rn "override void _Process\|_PhysicsProcess"` over `KleeCode/` returns **zero** hits. | (empty grep) | WORKS. The mod does no per-frame work of its own; the seven `Vfx/*` bridges attach to game nodes. |
| One combat-hook subscription per combat, built with `IEnumerable.Concat` over 6 hook sets | `KleeMod.cs:52-71` | WORKS. One allocation per combat start, not per turn. |
| Defensive `participants.ToList()` twice per turn-end | `Powers/TurnEndSequencer.cs:83,145` | WORKS — a deliberate copy against mutation-during-iteration; two small lists per turn. |
| Two compiled regexes, static | `Diagnostics/PlayTelemetry.cs:98-101` | WORKS. Compiled once; `RegexOptions.Compiled` is the right call for a per-fight path. |
| `static Dictionary<Player, FightRecord> Open` | `Diagnostics/PlayTelemetry.cs:107` | WORKS — cleared in `FlushAll` (`:608-609`), with an interrupted-flush path at `:177`. A static map keyed on a game entity is a retention shape worth knowing about, but it is drained. |
| Timer allocation in VFX | `Vfx/KleeCombatVfx.cs:175` (`CreateTimer(4.0)`) | WORKS — one-shot, per effect. |

- **NON-FINDING:** no allocation hot spot was found in the mod's combat path by
  reading. That is a *reading*, not a profile; nothing here has been measured
  under load.
- **Automation candidate: partial** — `klee-mod/KleeTests` runs against the real
  `klee.dll` and real `sts2.dll` with no Godot
  (`KleeTests/README.md:1-8`), so allocation counting on the pure-C# half is
  reachable; anything needing a live `CombatState` is play-only, and that
  boundary is stated in the same file (`:9-15`).

### P7 — telemetry files accumulate with no pruning

- **Case.** `Diagnostics/PlayTelemetry.cs:660-671` — one JSONL per session at
  `user://gits_telemetry/play-<session>.jsonl`, written with
  `File.AppendAllText` on the calling thread once per fight per player
  (`:629-648`). Nothing deletes, rotates, or caps: `grep -n
  "prune\|Delete\|rotate\|MaxFiles"` over `PlayTelemetry.cs` and
  `SelectionTelemetry.cs` returns **zero** hits.
- **Measured tonight:** `%APPDATA%/SlayTheSpire2/gits_telemetry/` holds **76
  files, 1.1 MiB total**. That is small, and the directory is outside the mod
  directory by design so a redeploy does not delete it (`PlayTelemetry.cs:52-57`).
- **Status.** **WORKS** at current volume. Growth is linear in sessions and
  bounded by fights; at the observed ~15 KiB/session it is not a size problem.
- **Defect vs. scope.** Not a defect. Whether an unpruned player-visible
  directory is acceptable for a *public* release is a **[USER] scope call**
  (it is one of the things a released mod leaves behind on uninstall — pointer
  to the save/update/removal family, which owns that question).
- **Automation candidate: yes**, trivially — a size assertion in the same place
  the schema is already tested.

### P8 — 24 cards render with no art and warn once each

- **Case.** log `:812-835` — 24 `[klee] No card art at …` warnings in one
  session (`KleeArt.cs:76-79`). They fire after the atlas load block, i.e. when
  something first asks for those portraits, and the null result is cached
  (`KleeArt.cs:27-30`, "Null is cached too, so a missing file is not retried
  forever"), so it is once per id per session, not a loop.
- **Status.** **WORKS as designed** for the performance question — no repeated
  disk hit. The *coverage* question (which 24, and why) is S17's, pointer only.
- **Defect vs. scope:** neither, here.

---

## 3. What a headless measurement would look like

Nothing in this section was run. It is the shape of the instrument, so the
question is cheap next time.

| Question | Instrument | Needs the game? | Existing seam |
|---|---|---|---|
| Package/download size, by family | `du` + a size report keyed off `klee.pck.contract.txt` and `images/cards/` | no | new script; sits beside `tools/art_coverage.py` |
| Format savings (P1) | Pillow re-encode in a scratch dir, ratio table | no | run tonight, above |
| Mod's share of boot (P4) | scrape `[Startup] Time to main menu` across `logs/*.log`, n≥3 with and without `mods/klee` | **yes** — and needs the install mutated | `understudy/` already parses logs |
| Mod's own init cost (P5) | `Stopwatch` around `KleeMod.Initialize`, one log line | **yes**, but self-reporting — no baseline run needed | `KleeMod.cs:29` |
| Resident texture cost (P2) | `[Startup] Resource stats` VRAM before/after opening the compendium | **yes** | first-party log line, log `:801,857` |
| Per-combat allocation (P6) | allocation-counting test against real `klee.dll` | no | `klee-mod/KleeTests` |
| PCK import cost (P3) | per-resource decoded-size report from the existing headless MegaDot import | no | `tools/build_pck.ps1:771` |

The two rows that need the game are also the two that cannot be honoured while
[USER] is playing on 0.2-1159.

---

## 4. UNKNOWN and NON-FINDING, collected

- **UNKNOWN:** the mod's contribution to the 13.3–16.8 s boot. No unmodded log
  exists in the corpus; five of five logs on this machine have the mod loaded.
- **UNKNOWN:** whether P2's ~197 MiB texture ceiling is ever reached in play.
- **UNKNOWN:** any frame-time, memory-over-time, or long-session figure. None
  was measurable without launching.
- **UNKNOWN:** whether the PCK's 132 imported resources are lossless-decoded to
  anything expensive at runtime.
- **NON-FINDING:** no per-frame mod code exists (`_Process`/`_PhysicsProcess`
  grep is empty), so the usual "mod costs frames" suspicion has no code to hang
  on.
- **NON-FINDING:** no allocation hot spot found by reading the combat path.
- **NON-FINDING (attribution):** the shutdown RID/resource-leak block at the end
  of every log (e.g. `1080 RIDs of type "CanvasItem" were leaked`) is
  **not attributable** to this mod without an unmodded baseline; Godot emits
  that class of message on exit routinely. Recorded, not charged.

---

## 5. Defects vs. [USER] scope calls, kept apart

**Defects (something contradicts its own stated intent; hygiene-class):**

1. **P1a** — card portraits are forced fully opaque and then written with an
   alpha channel anyway (`tools/art_process.py:296-301`). ≈0.87× size for
   nothing. Confirmed on 20/20 sampled files.

**Scope calls that are [USER]'s alone — offered as numbered picks, not blanks:**

1. **Card-art delivery format.** Pick one: (a) leave shipped RGBA PNG,
   68.1 MiB; (b) RGB PNG, ≈59 MiB, visually identical, no code change beyond
   the pipeline; (c) WebP q90, ≈9.5 MiB, needs `KleeArt.cs:60` to stop
   hardcoding `.png`, quality is eyes-on; (d) JPEG q90, ≈12.5 MiB, same code
   change, same eyes-on.
2. **Card-art topology.** Pick one: (a) keep loose PNGs next to the DLL as
   today; (b) move card art into `klee.pck` as an atlas, the way Downfall
   (`DownfallCardModel.cs:50`) and the base game (`card_atlas`, 875 sprites) do
   — this is a `tools/build_pck.ps1` and `KleeArt.cs` change and a real chunk of
   work; (c) keep loose PNGs but add cache eviction.
3. **Does package size matter for v1 at all?** Pick one: (a) yes, set a target
   number; (b) no, size is not a v1 constraint, and P1/P2 become notes.
4. **Boot-cost self-reporting.** Pick one: (a) add the `Stopwatch` line to
   `KleeMod.Initialize` so the number exists from the next deploy onward;
   (b) don't, and leave P4 UNKNOWN.

None of these is answered here.

---

## 6. What this does NOT establish

It does not establish that the mod is slow, fast, heavy, or light — no timing
attributable to the mod was measured, because that requires launching the game.
It does not establish that any size figure is too big: there is no target, and
setting one is [USER]'s. It does not establish that P2's texture ceiling is
reached in practice. It does not interpret [USER]'s playtest, open any balance
window, or propose a design change. And the Downfall comparisons are
reference-reading only: they show what one released mod chose, not what we
should copy.
