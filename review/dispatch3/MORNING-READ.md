# Surplus-dispatch-3 — MORNING READ

Written last, 2026-08-27, from the outputs that are actually on disk. Nothing
here was pre-filled. This file decides nothing: it orders, points, and lists.
Every ranking reproduced below is its source file's own.

**Read in this order** (charter §6). Sections 1–7 are the walk; section 8 is the
five separated lists (facts / non-findings / defects / proposals / questions);
section 9 is the honest acceptance status against charter §8.

**Two rails ran.** The research rail (S12–S20) wrote prose under
`review/dispatch3/` on branch `dispatch3-2026-08-26`. The tooling rail (lanes
A–D) wrote real code and tests, each on its own branch in its own worktree.
**Nothing merged. Nothing deployed. The game was never launched** — you were
playtesting mod `0.2-1155` all night, and the charter forbade touching the
installation.

---

# 1. Stop-work blockers

Full detail, with sources and what each one blocks, is in
**`review/dispatch3/BLOCKERS.md`**. Three items, one line each:

1. **25 of the 27 contact sheets in `art/` are dead.** The `art/candidates/`
   directories they point at are missing — M19's 21-image energy-orb sheet,
   S4-G12, EB-65, and **all 60 Klee candidate directories** — so R212(1)'s
   "veto on the sheet" route is closed until they are re-materialised
   (`s17-art/s17-klee.md` §7.1, `s17-furina.md` F3, `s17-icons-ui-models-vfx.md` §11(1)).
2. **`0.2-1159` is not a legal semantic version**, so the game parses our
   version as `null` and would refuse any future mod that pins us with
   `min_version`; every clean remedy amends LAW R70
   (`s20-release-readiness/s20-packaging-metadata-credits.md` P1).
3. **EB-65 cannot close mechanically** — the seven Furina sigils have no
   rank-1 row, so R212(1) has nothing to apply
   (`s17-art/s17-furina.md` F1 / §11 Q1).

`BLOCKERS.md` also carries §2, the runner facts that **bound** tonight's
non-findings (read it before quoting any "we found nothing"), and §3, the six
deferred outputs.

---

# 2. The tool lanes

All four lanes finished, pushed, and returned a handoff. **None merged, none
deployed, none opened a PR.** Read the handoff on each branch as written.

## Lane A — native animation bake-off

- **Branch** `dispatch3-laneA-animation-bakeoff`, commit **`09864c2`**, cut from
  `main` `223a4ff`. Handoff:
  `../GItS-laneA/review/dispatch3/tooling-lanea-handoff.md`; matrix at
  `review/dispatch3/lane-a/bakeoff-matrix.md`.
- **What was built.** One original synthetic rig ("Sprig" — eight parts drawn
  at run time from four primitives, no fetched or licensed art anywhere) plus
  one six-motion suite (`idle`/`intent`/`attack`/`hurt`/`death` + a derived
  `RESET`), authored once as **264 shared hand-authored numbers** and compiled
  four ways: layered sprites, cutout/skeletal 2D, mesh deformation, and
  particles/tweens. Each was exported to a `.pck` through the same headless
  MegaDot editor `tools/build_pck.ps1` drives. New package
  `tools/animation_bakeoff/` (including `pck.py`, the repo's only reader for
  MegaDot pack files) plus `tier0/tests/test_animation_bakeoff.py`.
- **What its tests prove.** 56 tests in the lane file; 3757 passed / 46 skipped
  / 12 xfailed on the full `tier0`+`tier05` suite; `run_lints.py --lane ci`
  22/22 — and 22/22 on the branch *before* the lane's files existed, so nothing
  is masking pre-existing red. **All twelve exports are byte-identical within
  their approach**, warm, warm-again, and cold (import cache deleted): the
  MegaDot headless export is reproducible on this machine.
- **The fidelity result.** Of 27 tracks: layered carries **27 as written, 0
  relocated, 0 dropped**; cutout relocates 7 (a `Bone2D` has no `modulate`);
  mesh relocates 6 and **drops 1** (a skinned `Polygon2D` ignores its own
  `scale`); particles **drops 18 of 27** and needs 12 extra hand-authored
  numbers.
- **Known debt, one line:** no live capture, no runtime frame cost, `intent` is
  unreachable, mesh drops one track, cross-machine export reproducibility
  untested, `tools/README.md` and `test_repo_python_convention.py` both need a
  row the lane deliberately did not race.
- **Its numbered questions (verbatim shape):**
  - **Q1 — how should an enemy's intent tell be driven?** (a) leave it, tells
    stay in the intent UI and rigs ship four states; (b) add a fifth state
    driven from our own C# when an intent is set; (c) reassign `PowerUp` to
    `intent` instead of `attack`; (d) defer until lane D / S18 has a real
    subject.
  - **Q2 — which technique is the default for the next rig built?**
    (a) layered, escalating to cutout only when a body demands limb hierarchy
    *(what the measurements support; still your call)*; (b) cutout everywhere;
    (c) decide per body, no default.
  - **Q3 — the missing-asset gap in `tools/build_pck.ps1` (F2).** (a) scan the
    **export** log for `ERROR` the way the import log is scanned; (b) extend the
    derived contract check to `.tscn`-referenced resources, not just
    C#-referenced ones; (c) both; (d) neither, accept the gap.
  - **Q4 — the two dead router rows (F5).** (a) leave them; (b) Harmony postfix
    on `NCreature.ImmediatelySetIdle`; (c) delete the unreachable `["Revive"]`
    row and write the reason next to it.
  - **Q5 — does the lane's tooling become a repo fixture or stay one-shot?**
    (a) keep the whole package; (b) keep `pck.py` and the tests only; (c) keep
    nothing, archive the branch unmerged.
  - **Q6 — does the lane worktree get its own virtualenv?** (a) yes; (b) no,
    borrowing the primary checkout's interpreter is fine.

## Lane B — art / provenance ledger

- **Branch** `dispatch3-laneB-art-ledger`, commit **`800062b`**. Handoff:
  `../GItS-laneB/review/dispatch3/tooling-laneb-handoff.md`.
- **What was built.** `tools/art_ledger.py` + `tier0/tests/test_art_ledger.py`
  (26 tests, all on synthetic fixtures). A row is one **expected visual
  surface**, derived — never listed — from four readers: the YAML sheets and
  `Art.CardPortrait` literals; `"<char>/<sub>/<name>.<ext>"` literals in
  `KleeCode/**`; `res://` refs inside packed **text** resources (which is the
  only way `select_bg.png`, `selection_splash.png` and `transition_wipe.png`
  are named at all); and concatenation prefixes such as the six aura badges.
  Rights tiers are **read, never assigned**, from `art/SOURCES.tsv` and
  generator docstrings; private-placeholder and public-safe coverage are printed
  separately and **never summed**.
- **What its tests prove.** 26 passed; 46 passed / 4 skipped across the three
  art test files; 2956 passed on `tier0`; `--lane ci` 22/22. No unrelated red.
  `test_card_universe_matches_art_coverage_on_this_repo` pins the ledger's card
  universe equal to `art_coverage.py`'s so the two cannot silently diverge.
- **The proving run (read-only against the primary, stamped `c09b6b6`):**
  **425 expected surfaces** — 294 card, 58 power, 24 UI, 21 scene, 12 model, 3
  each material/relic/vfx, 6 salon, 1 summon — **392 covered, 24 missing, 1
  active fallback, 8 defect-class**. Card reconciliation to the S17 baseline is
  exact: **294 / 270 / 24**.
- **Known debt, one line:** `MISSING-PACKED` is meaningless where no pck exists
  (fresh clone, CI); presence is `is_file()` only so a 0-byte PNG counts as
  covered; the `res://`→`ImageGen` rule table is curated; byte-identity is the
  only static unintended-fallback proof; the tool is not wired into
  `run_lints.py`.
- **Its numbered questions:**
  - **Q1 — the seven Furina power badges** (`courtroom_drama`,
    `fortissimo_guard`, `quick_change`, `stagehands`, `stagehands_encore`,
    `the_gallery_stirs`, `unheard_confession`) have no art and render the
    base-game placeholder. (a) commission/hunt all seven as one batch; (b) a
    named subset, placeholder for the rest; (c) accept the placeholder for all
    seven and record it so the ledger stops billing them; (d) defer.
  - **Q2 — the two energy icons.** They exist, are packed, and are unreachable
    because all three characters use the base game's energy counter scene.
    (a) delete the four files; (b) keep and record a reason; (c) point
    `CustomEnergyCounterPath` at our own counter (a feature, not a cleanup).
  - **Q3 — the two Klee `model/` plates** that ship because the `model` copy
    block is a blanket `*.png`. (a) delete; (b) rename to match `$pckExclude`;
    (c) keep with a recorded reason.
  - **Q4 — the unenumerable aura prefix.** A seventh element with no icon is
    invisible to every gate in the repo. (a) curated element→icon list plus a
    lint pinned against the C# enum; (b) leave it, blind spot now named;
    (c) change the call site to enumerate literals.
  - **Q5 — rights classification.** 330 of 425 surfaces have no machine-readable
    rights evidence, including 270 shipped card portraits. (a) backfill
    `SOURCES.tsv` for every shipped output; (b) a separate rights declaration
    file the ledger reads; (c) leave unclassified until public release is on the
    table.
  - **Q6 — wiring.** (a) `local` lane with a "contract absent → skip" mode,
    after Q1–Q3 are dispositioned; (b) `ci` lane (needs D1 *and* Q1–Q3 first,
    or it is red on day one); (c) no lane, run by hand.
  - **Q7 — ownership of the shared `tools/run_lints.py` edit,** shared with
    lane C. (a) lane B; (b) lane C; (c) a named integrator at merge time.

## Lane C — visual QA gates

- **Branch** `dispatch3-laneC-visual-qa`, commit **`0c08fdf`**. Handoff:
  `../GItS-laneC/review/dispatch3/tooling-lanec-handoff.md`.
- **What was built.** Five independent gates under `tools/visual_qa/`, all of
  which read the *leftovers* of a build and none of which needs the game, the
  editor, or a deploy: `export-log` (did import **or export** log an error),
  `scene-deps` (does every reference inside a `.tscn`/`.tres` resolve),
  `fallback` (did a character silently ship another character's art),
  `contract` (does the package match its contract), `contact-sheet` (build a
  byte-reproducible review sheet). CLI is `python -m tools.visual_qa` —
  deliberately **not** `tools/lint_*.py`, to avoid forcing an edit to the shared
  `run_lints.py`.
- **What its tests prove.** 63 passed across six new test files; `--lane ci`
  22/22; full suite 3758 passed after one self-inflicted encoding-gate failure
  was fixed. `scene_deps.CREATURE_STATES` is asserted equal to
  `CreatureAnimationRouter.TriggerToState` so the state list cannot go stale.
  All eight committed scenes carry **zero** error-severity findings.
- **Known debt, one line:** no live capture (contact sheet proven on five
  fixture PNGs only); the fallback policy is a sample, not a policy;
  `scene-deps` needs a resource universe (gitignored) to check texture
  existence; the C# animation-name association is a heuristic; two advisory
  `load_steps` warnings mean `--strict scene-deps` exits 1 today.
- **Its numbered questions:**
  - **Q1 — the fallback policy.** (1) one curated policy file with a reason and
    an expected-until note per row, plus a deploy rule that fails on anything
    undeclared; (2) same file, report-only until the art plan settles; (3) no
    policy file — drive the gate off lane B's ledger `fallback_from` (the code
    already exists); (4) leave the gate uninvoked for now.
  - **Q2 — should any of these block a deploy?** (1) all three proposed
    `validate.ps1` rules as blocking; (2) export-log only; (3) all three as
    warnings that never throw; (4) none yet.
  - **Q3 — the `load_steps` drift** in two Furina scenes. (1) correct both now;
    (2) leave them and keep the warning; (3) drop the rule.
  - **Q4 — `lint_text_encoding.py`'s `Path.open("rb")` blind spot.** (1) widen
    `_is_binary_open`; (2) leave it — over-reports, never under-reports.
  - **Q5 — captures.** (1) next session wire the sheet to the existing
    understudy/bot capture path; (2) fixture-only until a specific review needs
    a sheet; (3) something else you have in mind.

## Lane D — neutral enemy seam (ran because S13 returned a credible socket)

- **Branch** `dispatch3-laneD-enemy-seam`, commit **`bd5b28d`**, branched from
  `main` at **`c09b6b6`** (not the preflight SHA — `main` had moved). Handoff:
  `../GItS-laneD/review/dispatch3/tooling-laned-handoff.md`.
- **The result, in one line: the seam works, and it was proved offline only.**
  A Harmony prefix on `MonsterModel.get_VisualsPath` plus a second on
  `CreateVisuals`, armed against the real `sts2.dll` in a bare .NET process,
  then swept across **all 120 concrete base monsters: 1 claimed, 119 base path
  intact, 0 unexpected values.** BaseLib's own prefix arms first and the two
  compose — which is exactly the composition question S13 left open.
- **The proof art** is a "prism sentinel" whose every shape is a `Polygon2D`
  with vertices written out in the scene file: no texture, no image import, no
  external resource, nothing traced from anywhere. Deliberately abstract; it is
  proof geometry, not a design proposal.
- **What its tests prove.** 20 tests in `tier0/tests/test_lane_d_enemy_seam.py`
  (no game install needed); the mod's four existing C#-contract gates still
  pass; `--lane ci` green; 2950 passed on `tier0` with `--capture=sys`. One test
  exists solely to make "ship the base path inside our pck" fail — that mistake
  would swap the enemy's art **globally** and look identical in play to doing it
  right. A deliberate mutation removing the id guard was run: exit 1, all 119
  casualties named, then reverted.
- **The honest cost.** A non-Spine body **keeps** spawning, HP bar, intents,
  targeting, hitbox, damage, powers, death, removal, rewards, and a looping
  idle; it **loses** attack, hurt and death tells, and death is instant. The
  proof enemy will bob in place, take hits without flinching, and vanish.
- **Six base monsters cannot be reached this way** — `BigDummy` and five
  `Mock*` types declare their own `VisualsPath` override. None is an ordinary
  encounter enemy. **Nobody would have found this by reading source; the sweep
  found it.**
- **Known debt, one line:** nothing rendered, the `.tscn` has never been parsed
  by Godot, the spike is loaded by nothing, co-op untouched, Phobia mode a
  silent no-op for the proof scene, `NodeFactory::ConvertScene`'s body unread.
- **§7 of its handoff is a step-by-step live test procedure for the morning**,
  each step falsifiable on its own, starting with "re-run the offline gates; if
  the harness does not print 120 / 1 / 119 / 0, stop."
- **Its numbered questions:**
  1. **Does the proof art go into the shipped pack at all?** (a) yes, move it
     into `klee-mod/pck-src/`; (b) yes, behind a build flag / debug-only path;
     (c) no — keep it in the spike directory. *Nothing is packed until this is
     answered.*
  2. **If it runs in game, how does it load?** (a) move the two `.cs` files into
     `KleeCode/Patches/` (smallest change; the spike then enters four linted
     trees and the bite-check should read 19, not 17); (b) a separate assembly
     with its own mod id, manifest and pack; (c) neither yet.
  3. **Is a motion-less enemy acceptable for a proof?** (a) acceptable —
     idle-only is enough to judge the seam; (b) not acceptable — price the
     `NCreature` work first; (c) only judge after seeing step 6 live.
  4. **Which enemy is the subject, if any?** (a) keep the current one as
     disposable proof; (b) name a different one now; (c) do not name any base
     enemy — re-target at a mod-declared monster. *The current subject was
     picked only because it is the simplest and earliest base enemy.*
  5. **Do the six override-declaring monsters matter?** (a) no, note and move
     on; (b) yes, the seam should handle a per-type override before it is
     trusted.

---

# 3. S15 — the world-track sitting agenda

**File:** `review/dispatch3/s15-world-sitting-agenda.md` (570 lines). It decides
nothing; QUEUE stays canonical; it mints no id.

**How to walk it** (this order is `CURATION.md`'s, and it is the file's own):
open **§0, the dedupe log**, then **§A**. Then §A (items 1–12) → §B (13–47) →
§C (48–58) → §D.

**Item counts by section:**

| Section | Items | Shape |
|---|---|---|
| §A one-word calls | **12** (1–12) | each a yes/no or a choice between two named words; 7 Ancients-side, 3 boss-side, 2 enemy-atlas-side |
| §B short calls | **35** (13–47) | picks from lists the galleries already wrote. B1 = the eight Ancients (13–20) + 5 register calls (21–25); B2 = the six act-boss slots (26–31) + 2 register calls (32–33); B3 = the thirteen live event FLAGs (34–46) + item 47, which is **41 open per-event checkboxes** in one row; B4 = S8+S10, linked to their QUEUE row, not re-listed |
| §C discussions | **11** (48–58) | no crisp pick; several gate items above and say which |
| §D gap appendix | — | D1 (register coverage), D2 (four citation problems), D3 (what it does not establish) |

**Total: 58 numbered walking items.** Item 48 is the one the gallery itself says
outranks the rest of §B2 — "do the act-boss slots take weekly-boss bodies at
all", since the enemy atlas already carries curated picks for the same six base
bodies and argues three of them beat every weekly-boss draft on the merits.

**The dedupe result:** exactly **one** overlap with QUEUE (`S8 + S10 galleries`,
§3), which is linked rather than re-listed. **All 58 items are without a
register row of their own.** `M46` is absent in this checkout and the file says
so.

**CURATION.md's routing of S15's four hygiene findings — from curation, not from
me.** The four items in §D2 are dead-reference hygiene under
`docs/current/dossiers/`, and they are **routed off the sitting** to the
orchestrator's morning hygiene list, as normal commits on a hygiene branch and
**not** on this dispatch branch (charter §2 forbids `docs/current/` edits here).
They are:

1. Two stale line pointers, boss gallery → enemy atlas (`candidates.md:139`,
   `:148`, `:719` cite `reskin-gallery.md:117`, now `:122-124`; `:792` cites
   `:100`, now `:98`).
2. A file renamed without its citers updated — the Ancients gallery cites the
   event gallery as bare `gallery.md` at `:325`, `:598`, `:827`; **the line
   numbers are all still correct**, only the filename is wrong.
3. A cited path not in HEAD — `ancients-gallery.md:243` cites
   `docs/sitting-prep-2026-08-05.md:215`; retrieve via
   `git show pre-simplification-2026-08-06:…`.
4. One research correction nobody booked — `ancients-gallery.md:876-880` records
   that the wiki attributes three boons to Tanx which
   `research/act2-act3-roster-research.md:215-224` lists as unattributed. No
   QUEUE row, no BACKLOG row; not a [USER] decision.

Curation also notes that item 11 ("does the tier0 calibration battery stay
unthemed") touches measurement law, but is **an ask, not a finding**, and stays
where it is.

---

# 4. S12 + S13 — the joined socket read

**Open first** (curation's order): `s12-public-patterns/s12-00-joined-read.md`
**§1**, then `s13-engine-sockets.md` **§3**, then S13 **§4.4–4.5**, then S13
**§5** (the open socket questions), then S12 **§3** transfer questions — and
within §3, **group A (dependency pin) first**, because our manifest pins BaseLib
`≥3.3.6`, every pattern was read at **3.4.5**, and S20's packaging census found
the same three-number skew independently. It gates every other transfer
question. Then group F (registration route), C (save/identity/removal), then the
rest.

**The one-sentence headline:** the charter's suspicion was right — Downfall
answers relics, potions, packaging and localization end to end and almost
nothing else; every other subsystem's proof came from widening to **BaseLib**
(which we already depend on) and to two or three small mods nobody had opened.

## 4.1 Per-subsystem verdict, with S13's agreement or silence

| S12 | Subsystem | S12 verdict | S13 |
|---|---|---|---|
| **a** | Enemy registration, AI, intents | **PROVEN — not by Downfall.** Downfall ships **zero** hostile enemies: all 24 `CustomMonsterModel` classes are player-owned pets and all 3 move-machine overrides are the same `NOTHING_MOVE` self-loop. The proof is `BaseLib@2275793:Monsters/MoveBuilder.cs:16-304` | **AGREES and extends** — `S13-a1…a7` give the whole seam set, including the four presentation seams BaseLib already patches |
| **b** | Boss and encounter integration | **PROVEN.** Registration is a postfix on every act's `GenerateAllEncounters` (`BaseLib:Patches/Content/ContentPatches.cs:352-393`); `Act4FinalAscent@05c251a` ships a four-phase boss with **raw Harmony and zero library dependency**; Downfall has 0 `EncounterModel` subclasses repo-wide | **AGREES** — `S13-b2` confirms BaseLib enumerates base *and* modded acts. **NARROW on the boss half** (`S13-b3`): `BossDiscoveryOrder` is a plain virtual getter on the act, so changing a base act's boss order needs a patch on that act type, and BaseLib does not exercise it |
| **c** | Act and map hooks | **PARTIALLY PROVEN** — yes for acts, map generation and node behaviour (four public mods add or rewrite maps); **NON-FINDING for new node *kinds*** — none mints a new `MapPointType`/`RoomType`, all re-type existing nodes | **AGREES** on the sockets; **SILENT** on `MapPointType`/`RoomType` *membership*, so S12c's flag on `(MapPointType)7`/`8` stays UNVERIFIED. `S13-c4` (`GenerateRooms`) is file-level only |
| **d** | World-event runtime | **PROVEN (library) / NON-FINDING (released mod).** `CustomEventModel` exists and self-registers; Downfall's 72 `*Code/Events/` files are **combat hooks, not world events** — exactly the false positive charter §7 warned about, and it defines zero "?" events | **AGREES emphatically** — `S13 §5.1.5` names `MegaCrit.Sts2.Core.Hooks` as the combat/run callback bus and calls reading it as world events the charter's error |
| **e** | Relic and potion hooks | **PROVEN end to end.** A one-line pool class plus one inherited `[Pool(…)]` attribute is the entire registration for 15 relics. **Rarity is the only dial** for pool, shop and reward eligibility; no pricing, no shop slot, no shop screen anywhere in Downfall | **ANSWERS an S12 open item** — `RelicModel::MerchantCost` and `IsAllowedInShops` are both **`virtual`** (`S13-e2`). A pricing seam exists; no mod uses it. **SILENT** on whether `RelicRarity.Boss` exists |
| **f** | Save / version compatibility | **PARTIALLY PROVEN.** MegaCrit's own patch note `PN-0.107.1`: "The base game no longer deletes progress from mods that are removed or errored." Mod content is keyed by a `ModelId` derived from the **C# class name** — a rename is a save break — and no mod declares an explicit stable id anywhere | **AGREES and narrows.** `SaveUtil.XOrDeprecated` × 11 turns an unresolvable id into a `Deprecated*` tombstone (`S13-f3`) — S13 calls that "the entire modded-content-removal story". S13 also **narrows S12f NF1**: the base game *does* have `ISaveSchema.schema_version` and a migration registry; what stays true is that **nothing lets a mod register its own migration** |
| **g** | Packaging / localization / distribution | **PROVEN end to end, n = 1.** Bundling many characters in one package costs a Harmony postfix because only one `Mod` entry registers. Localization is a committed source tree with a supply chain — nine hosted translation projects and a nightly bot — not a string table filled in at the end | **AGREES** — a missing loc line warns and falls back (`S13-g5`). **`S13-g4` adds a TRAP S12 did not have:** Godot's pack loader replaces colliding `res://` paths, so a mod pck containing a base path overwrites the base scene globally |

**Counted across the seven S12 files:** 217 cited pattern rows, 70 gotchas, 65
raw transfer questions (**57 after dedupe**), 47 explicit NON-FINDINGS.

**Four claims appear in both S12 §2.3 and S13 §5, and S13 is the authority
(engine decompile) with S12 corroborating from mod source** — this is curation's
dedupe, not mine: no `BossModel`; no declarative data format for
enemies/encounters/acts/events; `Hooks` is a callback bus; the class name is the
save id.

**One S13 finding no S12 file could reach, because it changes the art question:**
BaseLib's `NCreatureVisualsFactory` will build a complete `NCreatureVisuals`
**from a bare `Texture2D`**, generating the missing required children with
defaults and warning rather than throwing for the one it cannot invent. **The
practical minimum presentation for a monster under BaseLib is one image, not a
rig.** S13 states plainly that whether the resulting trade is acceptable is a
taste call and yours.

## 4.2 The three open socket questions (S13 → lane D and S18)

S18 states these once and binds all 60 of its rows to them
(`s18-joined-matrix.md` §1):

- **S1 ✓ OPEN — register a hostile `MonsterModel` + `EncounterModel` into an
  act's pool.** `S13-b2` **dissolves the "`GenerateAllEncounters` returns a fixed
  array" objection all three S18 act files raised**: BaseLib enumerates every
  `ActModel` subtype, base and modded, and postfixes it. S13 also settles
  hostile-vs-summon — it is the **side**, not the type.
- **S2 ◐ SPLIT — ship a mod `creature_visuals` scene + Spine rig.** *Scene half
  OPEN* (`S13-a4` `VisualsPath` is the recommended seam because the preloader
  reads it too; `S13-g6` binds a mod `.tscn` to the game's C# node type).
  *Spine half still UNKNOWN* — S13 read no Spine import path. **⚠ trap
  `S13-g4`.**
- **S3 ◐ HALF — supply the FMOD events the id-derived SFX paths demand.**
  Overriding the **string** is proven (`S13-a7` OPEN). **Supplying bank content
  is not**: S13's own note is "replacing one needs an FMOD bank, not a file", it
  found no bank-adding mechanism, and it could not even enumerate the base
  game's event inventory (`Master.strings.bank` yields no plaintext). **This is
  the least-answered key and it touches all 60 S18 rows.**

**Still UNVERIFIED after the join — 16 items**, listed at
`s12-00-joined-read.md` §5, including `MapPointType`/`RoomType` membership,
whether `RelicRarity.Boss` exists, the per-key language fallback rule, the
BaseLib pin (four numbers), the creature-visuals scene *root* type, BaseLib's
reward/shop patches (file-level only), and **the whole of
`[STS2]Multiplayer\`, which S13 left unread**.

---

# 5. S16 animation + S17 art + S18 enemy feasibility

## 5.1 S16 — native-animation grammar and corpus

**Author-unconfirmed flag.** `s16-animation/s16-joined-capability-matrix.md` was
written to disk at 00:41 and is complete (712 lines), **but its agent's return
failed on the usage limit, so the file was never confirmed by its author**, and
`CURATION.md` still lists S16 as pending curation. Every claim I take from the
matrix below carries that flag. The schema, four body files and the public-mod
sidecar are all complete and unaffected.

**The four PROPOSED body picks** (`s16-00-schema.md` §5 — technical picks,
chosen to be *disjoint in what they teach* and reachable in default Act 1 or the
base roster):

| Slot | Pick | Why, in its own words |
|---|---|---|
| Player — simple | **Ironclad** | The smallest complete *player* body that still carries one VFX affordance (a `SpineSlotNode` on slot `slash_mesh` with a shader material + one driver). Seven nodes, 2,701 B. Canonical seven-state player shape with exactly one bespoke trigger (`heavyAttack`) — "the player grammar's floor-plus-one". It is also the house measurement anchor. `silent.tscn` is named as the strict floor contrast, not written up separately |
| Player — complex | **Regent** | "By a wide margin the most structurally complex shipped player body": 75,694 B, **three** `SpineSprite`s, a second skeleton resource, **six** `GPUParticles2D` (five hung off four `SpineBoneNode`s). The only base body proving skeleton-inside-skeleton composition and bone-anchored particles at once — **the two capabilities our layered-sprite rig has no answer for.** Its animator is still the same seven-state shape: "on the player side, complexity lives in the scene, not in the state machine" |
| Normal enemy | **Mawler** | "The most ordinary enemy the game ships, and the most capturable." *(Note: curation flags that S13 §5.4 #5 picks **Nibbit** for the same enemy slot, and lane D took Nibbit. Two PROPOSED picks for one slot; not resolved by curation, and flagged here.)* |
| Elite or boss | **Ceremonial Beast** | Section M of its file records three places where its evidence **corrects** the schema |

**What the matrix says per approach** (§1, one row each; **no approach is ranked
there** — ranking is partly lane A's evidence and finally yours):

- **A. Layered sprites.** Authoring dependency: **a raster editor and nothing
  else** — no importer, no rig format, no licence. Runtime: `%Visuals` must be
  `Node2D`-derived and must **not** be a `SpineSprite`; `HasSpineAnimation`
  false ⇒ **no `CreatureAnimator` is ever built**, `SetAnimationTrigger` is a
  no-op, **so something external must route triggers**. Fallback: the base
  game's *own* fallback body is this approach (`fallback.tscn` is a plain
  `Sprite2D`) — but **player bodies have no fallback at all**, since
  `CharacterModel::CreateVisuals` has no try/catch. Measured: Klee body 14,109 B
  source / 14 nodes / 5 layers, **108,919 B packed**; Furina 15,359 B / 13 nodes
  / 4 layers. Unknown: whether it reads at combat distance (no frame was seen),
  and what a `Travel()` to a missing state does.
- **B1. Cutout/skeletal 2D, Godot-native (`Skeleton2D`/`Bone2D`/`Polygon2D`).**
  **NON-FINDING, and a strong one** — zero occurrences across all 171 Downfall
  scene/script files, the widened 11-repo set, our own `pck-src/`, and **all 126
  base creature scenes**. An absence inside a stated boundary, not proof the
  engine lacks it. *(Lane A independently built and measured exactly this shape;
  the two results are complementary, not contradictory.)*
- **B2. Cutout/skeletal as the ecosystem actually does it: Spine.** Authoring
  dependency is **the commercial Spine editor** — the licence, retrieved
  2026-08-26, says "each user of the Products must obtain their own Spine Editor
  license", and **charter §4/S16 forbids proposing this as our answer.** Failure
  behaviour is the important half: skeleton data that fails to load is a
  **silent downgrade** to a static pose with **no death SFX and death length
  `0f`**; a **missing animation name is a silent freeze**. Packed body totals:
  Ironclad 364 KB, Mawler 367 KB, Ceremonial Beast 774 KB, Regent ≈703 KB; the
  shape is stable at roughly texture 71 % / skeleton 28 % / scene 0.33 %.
- **C. Mesh deformation — two different things wear this name.** (a) shader-on-a-
  quad: no licence, no special contract, and the base game's analogue is
  stronger (Ironclad's slash draws *inside* the skeleton's z-order). (b) true
  vertex deformation: needs a 3D DCC and glTF, is **a single unreplicated
  instance whose shipped status could not be confirmed**, and how a `Skeleton3D`
  hosts under the 2D body contract is UNKNOWN. The matrix newly names that
  **nothing in the corpus establishes Spine *mesh* attachments are used by any
  base body** — `slash_mesh` is a name, and a filename match is not proof.
- **D. Particles / tweens.** No dependency beyond one texture per emitter —
  except baked emission data, where Regent inlines a 977-point image as **79.3 %
  of its whole scene** and the Beast 1,732 points as **87 %**. Two shipped uses
  raise it above decoration: `AnimTempRevive` is **a pure `Tween` used as the
  revive animation on a player body**, and `IDeathDelayer` gates the Beast's
  death on a particle `Finished` signal. Failure mode is "**valid, loads, and
  wrong**": delete the Beast's driver and 1,500 particles fire at spawn instead
  of at death, with the death gate silently gone.

**S16's five PROPOSED reads (§5)**, all technical: **P1** the four rows are the
wrong decision axis — every shipped body *composes* rows, and the real
difference is a five-item capability list; **P2** the required-motion floor is
evidence-derived, not invented; **P3** three cheap gates fall out and are lane
C's to accept or refuse; **P4** three UNKNOWNs are cheap and unblock
disproportionately much; **P5** **the death seam is the single highest-value
thing to settle and it is one observation** — one attended death capture with
audio settles four independent questions.

## 5.2 S17 — art coverage, provenance, and batch plan

**Live baseline first, not prose** (`s17-art/baseline-run-2026-08-26.txt`, run
against the art-bearing primary at `223a4ff`, clean):

| Sheet | expected | covered | missing |
|---|---:|---:|---:|
| Klee personal | 79 | 76 | 3 (`hold_the_line`, `powder_charge`, `smoke_and_sparks`) |
| Furina personal | 84 | 81 | 3 (`change_the_bill`, `take_it_from_the_top`, `grand_gala`) |
| Furina token | 1 | 1 | 0 |
| Kokomi personal | 76 | 61 | **15** |
| Companions (Inazuma / Mondstadt-shared / Fontaine) | 15 / 17 / 19 | all | 0 |
| C#-only keys with no sheet row | 3 | 0 | 3 |

**Card-sized total: 294 expected / 270 covered / 24 missing** — which lane B's
ledger reproduces exactly, from a different derivation.

**What the four family files establish:**

- **`s17-klee.md`.** Card art is **76 of the 124 Klee-family images that ship**;
  the other 48 are badges, icons, model textures and layer cuts, and **five more
  surfaces have never been built at all**. 29 power badges all present at
  256×256. **One relic icon serves two relics** (`Dodoco Tales` wears Pounding
  Surprise's icon). Klee renders *someone else's* art in two places: two shipped
  card portraits are byte-identical to two others by design, and four co-op arm
  textures plus five combat SFX resolve to **Ironclad's**. Defects: §7.1 the
  dead sheets (blocker 1); §7.2 **1.18 MB of the 9.14 MB pack — 12.3 % — is two
  source masters nothing loads**; §7.3 two packed UI textures with no consumer.
- **`s17-furina.md`.** The headline is that **card art is a minority of her
  visual surface**: card-sized bill 87 expected / 82 present / 5 absent, but the
  **non-card bill is 58 expected / 45 present / 13 absent** — 7 power sigils
  (EB-65), 1 UI wipe present in the pck *as Klee's file*, and 5 energy-orb
  layers that exist nowhere because **no energy-counter scene exists for any
  character**. F1 confirms EB-65 cannot execute as written (blocker 3). F5:
  provenance is complete but keyed two ways. F7: the `§8` icon bill in the
  requirements doc no longer names the shipped paths.
- **`s17-kokomi.md`.** 76 expected / 61 present / **15 missing** — the largest
  single card bill in the repo. Power icons 7/7, relic icon 1 file for 2 relics,
  Bake-Kurage summon present. **Provenance gap: 22 Kokomi asset ids have no
  `SOURCES.tsv` row at any rank.** No byte-identical Kokomi outputs (a genuine
  null). **All 77 Kokomi card rows carry `source_group = kokomi_pool`** — she
  has no rarity-scoped source-uniqueness rule where Furina has a ratified one,
  so all 5 basics sit on one source and 12 of 19 identity cards on shared
  sources. One source is over its computed budget.
- **`s17-icons-ui-models-vfx.md`.** The cross-character family. Klee 29/29
  complete; Furina 15 packed against 22 expected (the 7 absent are the
  registered EB-65 deferral); **Kokomi 7/7 complete as of 20:34 tonight** — that
  is PR #108 landing mid-dispatch. **Seven powers have no icon mapping at all**,
  reported and not filed. **37 of 113 non-card outputs have no `SOURCES.tsv`
  row.** It also documents the cross-**game** fallbacks as first-class rows, and
  a **NON-FINDING on fonts**: the mod packs no font at all — zero
  `.ttf`/`.otf`/`.fnt` in the 132-resource contract; all text rides the base
  game's fonts.

**The two deferred S17 pieces** (see `BLOCKERS.md` §3): the **companions
family** and the **joined ledger proposal + disjoint batches**. Consequence: S17
has **no joined ledger**, so the charter's "joined ledger proposal" bullet is
unmet. What partly stands in for it is **lane B's `art_ledger.py`**, which is a
running tool billing 425 surfaces with rights read separately — but that is a
mechanism on a branch, not S17's ledger proposal, and it does not carry the
companions family.

## 5.3 S18 — implementation-aware enemy feasibility

**Open first** (curation's order): `s18-enemy-feasibility/s18-joined-matrix.md`
**§1** (socket resolution) and **§3a** (complexity), then **§3c** — *the boss
surcharge is invisible in the complexity letter*, the one methodological caveat
to hold while reading any row — then **§5**. Within §5, questions **1–4 are
SCOPE** and come before 5–12, which presuppose a scope.

**Socket resolution** is §4.2 above: S1 ✓, S2 ◐, S3 ◐, plus row-specific keys —
**S1b ⚠ NARROW** binds all 12 boss rows; **S4 ✓ OPEN** (17 rows); **S6 ◐
PARTIAL** is *the most load-bearing partially-answered key in S18* at **28
rows**; **S5, S7, S8, B1–B6 are all ○ — S13 has no key for them.**

**The complexity spread** (§3a), an engineering count of asset contracts, **not
a schedule and not hours**:

| Set | S | M | L | rows | share L |
|---|---|---|---|---|---|
| All normals | 6 | 7 | 17 | 30 | 57 % |
| Elites + bosses | 3 | 1 | 18 | 22 | **82 %** |
| Whole costed set | 9 | 8 | 35 | **52** | 67 % |

The cause is not creature size: **the bespoke-`N…Vfx`-driven-by-named-Spine-
events pattern is the house style at elite and boss tier** — 17 of 22 elite/boss
rows carry one, against 11 of 30 normals. Only **nine S rows exist in the whole
mapped set**, only three sit above normal tier, and one of those three
(Aeonglass) is S **because it has no rig at all**. Coverage: 61 gallery rows →
**60 matrix rows** (one deliberate merge, A3-5); nothing mapped is dropped;
**eight Underdocks rows covering twelve bodies are present but not costed**,
because no S18 agent owned that block — S18 records that as its one coverage gap
rather than papering over it.

**Its 14 questions, compactly** (§5, numbered for citation, **not ranked**):
**scope** — (1) do the ten unmapped base Overgrowth encounters come into scope?
(2) do Act 1's four research bosses? (3) does the Underdocks block get costed at
all? (4) does the gallery's five-body Underdocks leftovers row get split?
**structural** — (5) the atlas-vs-weekly-boss fork, globally or per slot;
(6) boss art-surface scope — creature only / creature + map node / everything;
(7) family coherence on `bowlbug_pod`, `construct_gang`, `shield_and_turret`;
(8) phobia-mode coverage — reproduce / drop / per-body, across **two
incompatible filename conventions**. **Empty or blocked rows** — (9) Soul Fysh
and Queen + Torch Head Amalgam have **no candidate from either gallery**;
(10) three more redesign-pressure rows with shipped content and no cover
(Decimillipede, Spiny Toad, Entomancer/Knowledge Demon); (11) Aeonglass has no
base animation to reskin against — (a) static-body reskin, (b) the row that gets
an original rig, (c) out of scope until MegaCrit finishes it; (12) Globe Head's
silhouette flag is now partly answerable — re-order or leave. **Register
hygiene** — (13) `TunnelerNormal` exists as a class and is in no `ActModel`
encounter list; (14) `ScrollsOfBitingNormal` is neither modelled nor on the
dropped list, so a sim encounter count is one short.

**Questions 5, 7 and 12 are the same decisions as S15 items 48, 56 and the
Globe Head flag** — S18 restates them with implementation evidence attached.
Walk them once, from S15's ordering.

---

# 6. S19 + S20

## 6.1 S19 — audio / VFX grammar and free-tool census: **DEFERRED, entirely**

Nothing of S19 exists on disk. Cause and re-run instructions are in
`BLOCKERS.md` §3 (row 3): the same prompt, ~1–3 h unthrottled. **Do not read any
audio claim elsewhere in this dispatch as S19's answer** — S13's `S13-a7` and
S18's key S3 both stop at "overriding the SFX string is proven; supplying bank
content is not", and S17 kokomi Q4 ("does Kokomi's kit want a `vfx/` scene?")
explicitly routes to S19.

## 6.2 S20 — release, accessibility, and localization surface census

**Five of seven families landed.** The save/update/removal family and the joined
matrix are deferred (`BLOCKERS.md` §3, rows 4–5), so **there is no joined S20
matrix** and the charter's S20 output bullet is unmet.

### Packaging / metadata / credits — `s20-packaging-metadata-credits.md`

The six things worth knowing, in the file's own order:

1. **`0.2-1159` is not a legal semver and the game says so on every boot.**
   Blocker 1.2. The remedies are a numbered pick list because they amend LAW
   R68/R70: (1) `MAJOR.AUTO` → `0.2.1159`; (2) `MAJOR.0-AUTO` → `0.2.0-1159`,
   keeping the dash but sorting *below* a plain `0.2.0`; (3) `MAJOR.AUTO+dirty`
   for dirty trees; (4) change nothing and record the dependency consequence.
   The automation seam already exists: `Test-VersionPolicy` in
   `klee-mod/build/version.ps1:168-236`, already unit-tested from Python.
2. **The manifest is the entire metadata surface, and it has nine fields.** No
   URL, no licence, no credits, no tags, no icon path.
3. **There is a real in-game credits surface and we use none of it.** BaseLib —
   which we already depend on — patches the base credits screen and takes
   registrations. Downfall uses it for team, art, sound and nine localization
   teams. We register nothing and ship no `credits` loc table.
4. **The packaged mod is 100 % Tier F art.** All 872 rows of `art/SOURCES.tsv`
   are tier `F`. Deploy's own handoff text says the zip must be handed off
   privately. **A public release cannot ship today's package as-is** — a rights
   call, not an engineering one.
5. **The install route is manual-only and private.** No Workshop item, no
   release workflow, no first-publish step; the base game exposes no in-game
   upload API by design.
6. **The BaseLib pin is three numbers in three places and nothing joins them** —
   manifest `>= 3.3.6`, `STATE.md` `3.3.7.0`, machine compiles and runs against
   `3.4.5.0`. **Whether we already use a 3.4-only API is UNKNOWN tonight.**

Also: **P2** `klee.dll` ships `AssemblyVersion 1.0.0.0`, never stamped; **P5**
no `mod_image.png`, so the Mods screen shows an empty slot; **P10** one shipped
card PNG has no live plan row (owner: S17 / lane B); **P11** the UTF-8 BOM is
tolerated — verified, not assumed.

### Performance / size / load — `s20-performance-size-load.md`

**The single dominant fact: the loose card-art directory is 7.4× the size of
the PCK and 88 % of the whole package.** Measured: `klee.pck` 9,586,076 B;
`klee.dll` 877,056 B; `images/cards/*.png` **71,368,915 B across 272 files**;
deployed total ~82.7 M (**79 MiB**). All 272 cards are 500×380, 8-bit,
**colour type 6 = RGBA**, mean 262 KiB. **The alpha carries nothing** —
`tools/art_process.py:296-301` forces the image fully opaque and then writes an
alpha channel anyway, confirmed on 20 of 20 sampled files. Separately, decoded
card portraits are **cached forever, uncompressed, with no eviction**
(`KleeArt.cs`), and the "9.6 MB PCK" is imported lossless, not VRAM-compressed.
`godot.log` has **no timestamps**, so no phase inside boot can be timed. Two
measurements were **barred outright** by the no-launch rule: the mod's share of
boot time, and the resident-texture ceiling.

### Player count (1 / 2 / 3) — `s20-player-count.md`

The file opens by correcting its own family name: **the base game's lobby
reports `max_players: 4`**, and nothing in `klee-mod/` or `tier0/` caps,
asserts, or branches on a seat count of any size — so "1/2/3" is the dispatch's
framing. Seventeen cases. What **works**: per-seat ownership and attribution in
C# (8 `[Fact]`s in `CoopSeamTests`), shared-RNG discipline, id freezing (R69),
handoff/zip hygiene, and the damage-preview purity sweep that closed the
2026-07-27 desync. What is **UNKNOWN and play-only**: transport, anything
needing a live two-seat `CombatState`, and whether `Player.PlayerRng.Seed` is
genuinely distinct per seat (the Featured Banner's per-player LAW claim rests on
it and **nothing checks it**).

**The one asymmetry worth your eye (§2).** `LAW.md:272-275` (R144) says co-op
depth arrives as **multiplayer-only cards**. **We ship zero. No sheet field, no
codegen path, no sim.** The mechanism is proven in the wild: at
`Downfall@32e6113`, seven characters each ship exactly five multiplayer-only
cards in a dedicated `Cards/Multiplayer/` folder — 35 files. The file does not
recommend adding them, propose a count, or price it.

**And one defect:** reaction counters in the per-seat fight telemetry row are
**team-wide**, so a co-op seat's `reactions_by_turn` silently includes the
partner's (`PlayTelemetry.cs:259-263`). The row's own shape implies per-seat and
the value is not. The repair shape is already pinned next door — the corpse
counter is a `Dictionary<Player,int>`.

### Controller / resolution / text — `s20-controller-resolution-text.md`

Three facts everything hangs on: **(a) controller mode warps the mouse cursor to
(-1000,-1000)** and hands navigation to the focus graph, so **a Control whose
only reveal path is `MouseEntered` is unreachable — not harder, unreachable**;
**(b) the base game's own creature hover is wired to all four signals**
(`FocusEntered`/`Exited` *and* `MouseEntered`/`Exited`) and that is its published
shape for a controller-reachable informational hover; **(c) resolution is
decoupled from layout by a fixed logical canvas** chosen by the aspect-ratio
setting, while the resolution dropdown whitelists 26 entries from 1024×768 to
7680×4320 — so monitor pixels change *upscaling* and the aspect setting changes
the *logical box*, which are two different risks. Left **UNKNOWN** by the failed
PCK index parse: whether the shipped `kreon_regular.ttf` covers U+266A (the
eighth note in the two Barbara titles), and character-select sizing.

### Colour / effect / reduced motion — `s20-color-effect-reduced-motion.md`

**The base game has no colour-blind mode and no reduced-motion mode** — neither
string nor any synonym appears in the decompile. It has four adjacent switches
(Screenshake with a true zero, Phobia Mode, Text Effects, Fast Mode) and **our
mod touches none of them**, because it never shakes the screen, never animates
text, and never registers a phobia-toggleable animation player. The real
exposure is **colour-only encoding**, in two halves: one inherited (the base
game's green/red "this number changed" convention, which **246 of our 309 card
files opt into** by writing `{X:diff()}`), and one we created — **Furina and
Kokomi ship near-identical cyan seat colours at 1.44:1, which in co-op are the
only channel identifying who drew a map line and who is aiming at what**.
Everything else we encode by colour also carries a shape, icon, number or hover
tip. Eight mod animations, all one-shot or slow loops, none a strobe; the only
continuous motion is two idle sway loops (3–3.5 s, ±1.4 px) that **no player
setting can stop**.

### Localization seams — `s20-localization-seams.md`

Our strings live in **six** places: 319 C# `Localization =>` overrides (368
titles / 294 descriptions) which are injected into the *active* table at boot
and so **can have no per-language file**; 37 PCK loc rows generated **inside the
PowerShell build script**; 53 rows injected from the DLL at runtime; 13
`new HoverTip(...)` sites whose **bodies are raw C# text and cannot be
translated at all**; 2 scene-baked strings; and the 3 manifest fields, which the
base type has no loc field for. **L4 is the sharp one, predicted and
UNVERIFIED:** switching language in-game rebuilds the tables while our
injections ran once and nothing subscribes to locale change — predicted result
is a `LocException` on custom card/power/relic text and ~20 keyword titles
rendering as raw keys. **It is a defect either way, because the dropdown is
reachable by any player who installs the mod.** L3 records a repeat failure mode
with no coverage (two live builds shipped a raw `card_keywords` key). L7 is a
latent gate gap: `lint_prose_constants.py` checks C# only, so the build script's
hand-typed balance numbers in the loc JSON are ungated — **checked tonight, all
eight match, no drift today.**

---

# 7. S14 — Elemental Resonance pre-read (SURPLUS, read last)

`s14-resonance-preread.md`, 392 lines. Curation is explicit that **all of it is
"not for the sitting"** — the charter keeps this stream surplus-only and
non-critical-path, and no item is promoted. Read **§1.4 first**, before citing
any number from §1.2: the census found the official page is **behind** the
community wiki on wording (the community rows name Stellar-Conduct,
Lunar-Charged, Lunar-Bloom, Lunar-Crystallize and Moondrifts; none of those
terms appear in the official source, whose page stamp is 2025-08-13 against a
2026-07-13 revision — a consistent direction, but an inference, not a citation),
and a widely-mirrored third-party summary contradicts **both**, rendering
Soothing Water as "+30 % incoming healing" where both real sources say "+25 %
Max HP". Then §1.2 (the composition table in official wording), §2.2 (where
fixed and dynamic payoff separate), §3.1 (**NON-FINDING — no composition passive
exists in Downfall**), and §4, which is questions only against reactions, co-op
seats, companion nations, banner limits, UI and save identity. §1.5 is the one
place HoYoverse has already re-expressed Resonance *as a card game* — fourteen
Genius Invokation TCG cards where the composition check moved from party slots
to **deck contents** and the payoff from a passive aura to a playable Event
Card. Nothing in S14 proposes a number, a mechanic, or that Resonance belongs in
v1.

---

# 8. The five separated lists

## 8.1 FACTS established tonight

Each with the file that establishes it. All are source-reads, offline runs, or
static measurements; **nothing was observed in the running game.**

**Engine and modding sockets**
1. A hostile `MonsterModel`/`EncounterModel` can be registered into a base act's
   pool: BaseLib enumerates every `ActModel` subtype, base and modded, and
   postfixes `GenerateAllEncounters` — `s13-engine-sockets.md` §3 `S13-b2`.
2. There is **no `BossModel`**; a boss is an `EncounterModel` with
   `RoomType.Boss` in an act's `BossDiscoveryOrder` — S13 §5.1.1.
3. There is **no declarative data format** for enemies, encounters, acts or
   events; content is C# classes and loc strings are the only externalized part
   — S13 §5.1.2.
4. **The class name is the save id** (`ModelDb::GetEntry` = `Slugify(type.Name)`)
   — S13 `S13-f1`; corroborates the repo's own R69.
5. Removing a mod turns its content into `Deprecated*` tombstones rather than
   corrupting the save (`SaveUtil.XOrDeprecated` × 11) — S13 `S13-f3`.
6. **A non-Spine body is a fully supported engine state end to end** — it keeps
   spawning, HP bar, intents, targeting, hitbox, damage, powers, death,
   hitbox-based fade, removal and rewards; it loses the animator, animation
   triggers, the death clip and skeleton-accurate fade bounds — S13 §4.4.
7. **The practical minimum presentation for a monster under BaseLib is one
   image, not a rig** — `NCreatureVisualsFactory` builds a complete
   `NCreatureVisuals` from a bare `Texture2D` — S13 §4.5.
8. `MerchantCost` and `IsAllowedInShops` are both `virtual` on `RelicModel` — a
   shop-pricing seam exists and no public mod uses it — S13 `S13-e2`.
9. Downfall ships **zero hostile enemies**: all 24 `CustomMonsterModel` classes
   are player-owned pets — `s12-public-patterns/s12a-enemy-lifecycle.md`, joined
   at `s12-00-joined-read.md` §1.
10. `Act4FinalAscent@05c251a` proves an encounter and a four-phase boss with
    **raw Harmony and zero library dependency** — `s12b-boss-encounter.md`.
11. `MegaCrit.Sts2.Core.Hooks` is the combat/run callback bus, **not** a
    world-event system — S13 §5.1.5, confirming `s12d-world-event.md`.
12. `Collector` and `Gremlins` are in Downfall's tree but excluded from its
    default build — **a class in the tree is not shipped content** —
    `s12-00-joined-read.md` §2.1.
13. **The seam composes with BaseLib at runtime.** Two prefixes on
    `MonsterModel.get_VisualsPath` both arm and the mod's value wins, proven
    against the real assembly outside Godot — lane D §4.2.
14. **Sweeping all 120 concrete base monsters: 1 claimed, 119 base path intact,
    0 unexpected** — lane D §4.1.
15. **Six base monsters (`BigDummy` + five `Mock*`) declare their own
    `VisualsPath` override** and are unreachable by that seam — lane D §4.3.

**Animation and the build pipeline**
16. **The MegaDot 4.5.1 headless export is byte-reproducible** — twelve exports,
    warm/warm/cold, all identical within their approach — lane A §4.
17. **Layered sprites carry the whole 27-track motion suite with nothing moved
    and nothing lost**; cutout relocates 7; mesh relocates 6 and drops 1;
    particles drops 18 and needs 12 extra numbers — lane A §3.
18. **No Spine or paid dependency is needed** for any of the four approaches;
    `NCreature.SetAnimationTrigger` is `_spineAnimator?.SetTrigger`, a guaranteed
    no-op without a spine animator — lane A F7.
19. **Godot-native `Skeleton2D`/`Bone2D` cutout has zero occurrences** across
    Downfall, the widened 11-repo set, our `pck-src/`, and all 126 base creature
    scenes — S16 matrix row B1 *(author-unconfirmed)*.
20. The base game's **own** fallback body is a plain `Sprite2D` with no
    skeleton; **player bodies have no fallback at all** —
    `CharacterModel::CreateVisuals` has no try/catch — S16 matrix row A
    *(author-unconfirmed)*.
21. Baked emission point clouds are **79 % of Regent's scene and 87 % of the
    Ceremonial Beast's** — S16 matrix row D *(author-unconfirmed)*.
22. All eight committed `pck-src` scenes carry **zero** error-severity scene
    findings; all six C# `Play`/`Queue` animation names resolve; both combat
    scenes carry the full `idle`/`attack`/`hurt`/`death` set — lane C F7.

**Art and package**
23. **294 card-sized outputs expected / 270 covered / 24 missing** — the S17
    baseline and lane B's ledger agree exactly, from two different derivations.
24. **425 expected visual surfaces exist, not 294** — the extra 131 are power,
    relic, UI, model, salon, summon, material, scene and VFX surfaces
    `art_coverage.py` was never written to see — lane B §3.
25. **Only 95 of 425 surfaces carry declared rights evidence**; 330 are
    unclassified, including 270 of 294 shipped card portraits — lane B F6.
26. **All 872 rows of `art/SOURCES.tsv` are tier `F`** — the packaged mod is
    100 % Tier F art — `s20-packaging-metadata-credits.md` P8.
27. **The deployed package is 79 MiB, of which 272 loose 500×380 RGBA card PNGs
    are 71.4 MB — 88 %** — `s20-performance-size-load.md` §1.
28. The mod **packs no font at all** — zero `.ttf`/`.otf`/`.fnt` in the
    132-resource contract — `s17-icons-ui-models-vfx.md` §12.
29. Kokomi's power and relic icons were **art present, art paid for, art not
    shipping** at `223a4ff`, and went green after PR #108 rebuilt the pck at
    20:39 — lane B F1. **Only source × rendered × packed can say that.**

**Enemy feasibility**
30. **82 % of elite/boss rows are complexity L against 57 % of normals**, and the
    cause is that the bespoke-`N…Vfx`-driven-by-named-Spine-events pattern is the
    house style at that tier (17 of 22 vs 11 of 30) — `s18-joined-matrix.md` §3a.
31. **Every boss row carries a map node, a custom background, and `CustomBgm` +
    a music parameter; no elite row does — and none of the three moves the
    complexity letter** — S18 §3c.
32. **Exactly one mapped encounter shares its bodies across acts** (A3-5, the
    construct gang); **no elite or boss body is shared across acts at all** —
    S18 §3e.
33. Aeonglass is the base game shipping a **spine-less boss**: a 5-node scene
    whose `%Visuals` is a plain `Sprite2D` on `hourglass_placeholder.png`, root
    node still named `Doormaker` — S18 E21.

**Release surface**
34. Controller mode warps the cursor off-screen, so a `MouseEntered`-only reveal
    path is **unreachable** by controller — `s20-controller-resolution-text.md`
    §0(a).
35. **The base game has no colour-blind mode and no reduced-motion mode** —
    `s20-color-effect-reduced-motion.md` §1.
36. **246 of our 309 card files opt into the base game's green/red colour-only
    "changed from printed" convention** by writing `{X:diff()}` — same file, C2.
37. The base game's lobby reports **`max_players: 4`** — `s20-player-count.md`
    §0.
38. Our PCK loc files **do** merge into the base tables under `eng`, and the
    card/character/power self-check passes at boot — `s20-localization-seams.md`
    L1, L2.

## 8.2 NON-FINDINGS

Each of these is a result, not a gap in effort — but read `BLOCKERS.md` §2 for
the boundaries that bound them.

1. **No `BossModel` type exists** — S13 §5.1.1.
2. **No declarative monster/event data format exists in `sts2.dll`** — S13
   §5.1.2.
3. **No mod-registered save migration exists.** BaseLib's answer is additive
   extra fields, not migrations. *Absence stays absence — S13 did not
   exhaustively read the registry* — S13 §5.1.3.
4. **No public API to replace a base monster's art.** The seam is a Harmony
   patch on an engine member, not a supported extension point — S13 §5.1.4.
5. **Zero Godot-native `Skeleton2D`/`Bone2D` cutout rigs** in any corpus read —
   S16 matrix B1 *(author-unconfirmed)*.
6. **Nothing in the corpus establishes that Spine *mesh* attachments are used by
   any base body** — `slash_mesh` is a name, and a filename match is not proof —
   S16 matrix row C *(author-unconfirmed)*.
7. **Does any of lane A's work require Spine? It does not** — lane A F7.
8. **No byte-identical Kokomi outputs** — a genuine null — `s17-kokomi.md` §5a.
9. **`RIGHTS-INHERITANCE` found nothing** — a genuine null: the two Tier-O
   generators are purely procedural and the two wiki-derived ones both declare
   Tier F correctly — lane B F6.
10. **The mod packs no font** — `s17-icons-ui-models-vfx.md` §12.
11. **No composition passive exists in Downfall** — S14 §3.1.
12. **No seat-count-conditional gameplay branch exists in `klee-mod/KleeCode/`.**
    Searching returned per-seat *keying* and unbounded `Players` enumerations,
    but no code that behaves differently at 1 vs 2 vs 3 seats —
    `s20-player-count.md` §5.
13. **No co-op-specific QUEUE row exists** anywhere in the register today —
    same file.
14. **No `MultiplayerConstraint` card in any of our three pools**; we only ever
    *read* the flag — same file, row 15.
15. **The manifest's UTF-8 BOM is tolerated** — verified, not assumed —
    `s20-packaging-metadata-credits.md` P11.
16. **No loc drift today:** all eight hand-typed balance numbers in the build
    script's generated loc JSON match the C# constants, checked 2026-08-26 —
    `s20-localization-seams.md` L7.
17. **"No released mod consumes API X" was not establishable** — GitHub code
    search is behind an auth wall for this runner, and four named repositories
    were deliberately not opened. This is a **bounded** non-finding, not a proof
    of absence — `s12-00-joined-read.md` §4, `BLOCKERS.md` §2.2.

## 8.3 DEFECTS (technical, with `file:line` where the source gave one)

Reported, **not fixed**, unless the row says otherwise.

| # | Defect | Where | Source |
|---|---|---|---|
| D1 | The pck producer greps the **import** log for `ERROR` and throws, but checks **only the exit code** for the export — so a referenced texture can vanish from the pack with exit 0 and zero error lines | `tools/build_pck.ps1:773-774` vs `:777-778` | lane A F2, lane C F1 (both, independently) |
| D2 | That `ERROR` sweep both over- and under-matches: `Select-String 'ERROR'` is case-insensitive and unanchored, while Godot reports `Unrecognized dependency:`, `Failed loading resource`, `Cannot open file` with no `ERROR:` prefix at all | `tools/build_pck.ps1:771-778` | lane C F2 |
| D3 | On MegaDot 4.5.1 a `Polygon2D` `bones/N/path` line is **silently discarded by the scene parser** — import 0, export 0, scene loads and animates, `get_bone_count()` returns 0 | — | lane A F1 — **fixed in-lane with a regression test** |
| D4 | `NCreature::ImmediatelySetIdle` calls `_spineAnimator?.SetTrigger("Idle")` **directly**, bypassing the `SetAnimationTrigger` our Harmony postfix patches | decompile `:983-985` vs `CreatureAnimationRouter.cs:82-88` | lane A F5 |
| D5 | `NCreature::StartReviveAnim` only emits `"Revive"` when `_spineAnimator != null`, so the router's `["Revive"] = "idle"` row is unreachable for every modded (spine-less) character | decompile `:957-963`, `:503-514` | lane A F5 |
| D6 | `NCreature::StartDeathAnim` gates the death SFX and the death-anim length read inside `if (_spineAnimator != null)`, so **spine-less bodies play no death sound** and combat may not wait for the death | — | S16 schema / matrix Q3 *(author-unconfirmed)*; corroborated by S13 §4.4 |
| D7 | `lint_text_encoding.py` cannot see `Path.open("rb")` — `_is_binary_open` reads the mode from keyword or positional index **1**, but the bound-method shape puts it at index **0**, so a binary read counts as an undeclared text read | `tools/lint_text_encoding.py:60-70` | lane C F5 — worked around locally, not fixed |
| D8 | Two committed Furina scenes carry a stale `load_steps` (`combat.tscn` declares 26, has 25; `salon_stage.tscn` declares 11, has 9). Cosmetic in Godot 4 | `klee-mod/pck-src/furina/…` | lane C F6 — advisory warning only |
| D9 | **`0.2-1159` is not a valid semantic version**; the parser throws on `-` in Minor, our parsed version is `null`, and a future dependent mod with `min_version` is refused | `SemanticVersion.cs:102-107`; `ModManager.cs:810-812` | S20 packaging P1 — **STOP-WORK class** |
| D10 | `klee.dll` ships `AssemblyVersion 1.0.0.0` — never stamped | — | S20 packaging P2 |
| D11 | No `res://<id>/mod_image.png`, so the Mods screen shows an empty image slot (soft-failing; the texture is set to `null`) | — | S20 packaging P5 |
| D12 | The BaseLib pin joins nothing: manifest `>= 3.3.6`, `STATE.md` `3.3.7.0`, machine `3.4.5.0`; **whether we already use a 3.4-only API is UNKNOWN** | three files | S20 packaging P6; also S12 §3 Q1 and S16 Q15 |
| D13 | One shipped card PNG has no live row in the art plan (1 of 272) | — | S20 packaging P10 (owner: S17 / lane B) |
| D14 | Card portraits are forced fully opaque and then written **with an alpha channel anyway** — ≈0.87× size for nothing, confirmed 20/20 sampled | `tools/art_process.py:296-301` (the brief's `:297`/`:301`) | S20 performance P1a |
| D15 | Decoded card textures are cached forever, uncompressed, with no eviction | `KleeArt.cs:30` (cache) / `:60` (hardcoded `.png`) | S20 performance P2 |
| D16 | Reaction counters in the per-seat fight telemetry row are **team-wide**, so a co-op seat's row silently includes the partner's reactions | `PlayTelemetry.cs:259-263`; schema `understudy/README.md:711` | S20 player-count §3 |
| D17 | Custom-keyword / hover-tip **title** rows are covered by no check — it has shipped raw keys to live builds twice (`KLEEMOD-COMPANION_RIDER` in 0.2-589, `KLEEMOD-MUSTER` in 0.2-634) | `KleeMod.cs:206-215`; `KleeSelfCheck.cs:500-524` | S20 l10n L3 |
| D18 | Switching language in-game rebuilds the tables while our injections ran once and nothing subscribes to locale change — **predicted** `LocException` on custom text plus ~20 raw keys. **UNVERIFIED at runtime**, and a defect either way because the dropdown is reachable | `LocManager.cs:332-341` vs `KleeMod.cs:293-299` | S20 l10n L4 |
| D19 | `lint_prose_constants.py` is scoped to `klee-mod/KleeCode/**/*.cs`, so the build script's hand-typed balance numbers in the generated loc JSON are ungated (latent — no drift today) | `tools/lint_prose_constants.py:29-32`; `tools/build_pck.ps1:585-620` | S20 l10n L7 |
| D20 | Scene-baked `"END OF TURN"` has no loc key and is never reassigned | `klee-mod/pck-src/shared/turn_end_docket.tscn:141` | S20 l10n L8 |
| D21 | Seven Furina power badges have no art and render the base-game placeholder — a real art bill no existing instrument prints, because every existing coverage number is a card number | `KleePowerIcons.cs:99-110` | lane B F2; S17 furina §4b |
| D22 | 1.18 MB of the 9.14 MB Klee pack (12.3 %) is two `mode=raw` source masters that **no C#, no `.tscn` and no generated scene references** | `res://klee/model/character_klee_full_wish.png`, `klee_character_card.png` | `s17-klee.md` §7.2 |
| D23 | Two Klee relics share one icon — `Dodoco Tales` wears Pounding Surprise's | — | `s17-klee.md` §5 |
| D24 | 22 Kokomi asset ids have no `SOURCES.tsv` row at any rank; **37 of 113 non-card outputs** across the icons family likewise | — | `s17-kokomi.md` §4; `s17-icons-ui-models-vfx.md` §10 |
| D25 | Seven powers have no icon mapping at all | — | `s17-icons-ui-models-vfx.md` §2d — reported, not filed |
| D26 | **25 of 27 contact sheets are unrenderable** (60/60 Klee candidate dirs missing) | `art/contact_sheet_*.html` | `s17-klee.md` §7.1 — **STOP-WORK class** |

**Structurally invisible, named but not closed:**
`KleePowerIcons.cs:143` builds its path by concatenation
(`"klee/powers/aura_" + element + ".png"`), so **a seventh element with no icon
is invisible to every gate in this repo, this ledger included** — lane B F5. The
honest fix is a curated list plus a lint, which is a build, not a report.

## 8.4 TECHNICAL PROPOSALS — all labelled `PROPOSED`

None of these is adopted, scheduled, or recommended by this file.

**Lane A §7 — a PROPOSED production grammar (8 items):** layered sprites stay
the default for a player character or a normal enemy; cutout/skeletal is the
escalation for a body needing limb hierarchy; **mesh deformation is a per-part
decision, not a per-character one**; particles are an addition to a rig, never a
substitute; every scene declares the same `%Visuals`/`Bounds`/`%CenterPos`/
`%IntentPos`/`%AnimationPlayer`/`%AnimationTree` contract regardless of
technique; **`RESET` is derived, never hand-written**; motion is authored once
in semantic channels and compiled; a generated scene is checked for node-path
validity before it ships.

**Lane A P1 (patch note, not applied)** — a `tools/README.md` entry for
`tools/animation_bakeoff/`.

**Lane B §7 (patch note, not applied)** — add
`Lint("art-ledger", "local", (…, "--strict"))` to the **`local`** lane, not
`ci`, because `ci` runs where there is no `ImageGen/` and no pck contract. The
lane argues explicitly that **wiring it into any lane at all is yours, and
should follow the D1 skip mode and the F2/F3 dispositions, not precede them.**

**Lane C §8 (patch notes, none written)** — `run_lints.py` gains one `ci` row
for `scene-deps` (needing either a two-line shim or teaching `Lint.command()` to
accept `-m`); and three `validate.ps1` rules: **S17** pipe both MegaDot logs
through `export-log`, **S18** run `contract --package $StageDir` beside S2,
**S19** run `fallback` against a real policy (blocked — no policy exists).

**Lane D** — `BUILD-PCK-PATCH-NOTE.md` §2 describes what a shared-file change
would be *if* you ever want one; nothing was applied.

**S13 §6** — prefer socket **`S13-a4`** (`VisualsPath`) over `S13-a5`
(`CreateVisuals`), because a4 is read by the preloader too so the replacement
scene is warmed with the rest of the combat set. "A technical preference,
`PROPOSED`, not a decision."

**S16 §5 (five reads, author-unconfirmed)** — P1 the four approaches are the
wrong decision axis and the five free-with-Spine capabilities are the right one;
P2 the required-motion suite has an evidence-derived floor; P3 three cheap gates
fall straight out and are lane C's to accept or refuse; P4 three UNKNOWNs are
cheap and unblock disproportionately much; **P5 the death seam is the single
highest-value thing to settle and it is one observation.**

**S17 klee §11** — five disjoint PROPOSED batches, one owner each: **K-1** sheet
revival (owner: the art-bearing primary's owner, since it writes
`art/candidates/`); **K-2** ledger rows to lane B; **K-3** pack-leak patch note
to the single named `build_pck.ps1` integrator; **K-4** a Klee art-pass doc
note; **K-5** the card bill, blocked on your pick 3.

**S20 packaging P1** — four PROPOSED version-string shapes (see §6.2). **S20
performance** — four PROPOSED delivery/topology options for card art. **S20
player-count §3** — key the reaction counter as a `Dictionary<Player,int>`, the
pattern already pinned next door. **S20 l10n Q2** — three PROPOSED storage
options for card/power/relic strings, all of which need a LAW read because
`LAW.md:410-413` currently mandates the C# override.

## 8.5 [USER] QUESTIONS

**213 questions after dedupe.** 98 are listed individually below or in sections
2–6; **115 live in two register blocks that are pointed at rather than
re-listed** — S15's 58 walking items (re-listing them would duplicate the agenda
and risk changing an ordering curation told me to keep) and S12 §3's 57 transfer
questions. Grouped by the decision each belongs to; **no option is recommended
and nothing is ranked.**

**Group 1 — the world sitting (58 questions, plus the fork).** All of S15,
walked in its own order (§3 above). **S18 questions 5, 7 and 12 are the same
decisions as S15 items 48, 56 and the Globe Head flag**, with implementation
evidence attached — answer them once, from S15.

**Group 2 — dependency pin and game version (curation says read this first).**
S12 §3 Q1: *what is our true BaseLib floor, and who signs off raising it?* Four
numbers are in play (manifest `≥3.3.6`, `STATE.md` `3.3.7.0`, installed Workshop
`v3.4.5`, Downfall `3.4.5`) and **every pattern in the seven S12 files was read
at 3.4.5**. S20 packaging P6 and S16 Q15's hygiene half are the same question
from two other directions. Q2–Q4 of S12 group A follow it: is a dll inside a
Steam Workshop folder a reproducible dependency at all; what do we run against
the installed binary to prove a named API is there; and do we have a
game-version compatibility posture beyond one hand-written canary.

**Group 3 — the enemy seam and whether it ships** (lane D 1–5, plus S13 §5.4
1–4). Does the proof art go into the shipped pack (a/b/c)? If it runs, how does
it load (a/b/c)? Is a motion-less enemy acceptable for a proof (a/b/c)? Which
enemy is the subject, if any (a/b/c) — **this dedupes S13 §5.4 #5, which picked
Nibbit for the trace and said the choice is yours.** Do the six
override-declaring monsters matter (a/b)? S13's remaining four: does `AssetCache`
ever unload a mod-namespaced path mid-run (untested); does a presentation
replacement present on one seat only desync anything (**play-derived only —
co-op has no sim backstop**); is a missing `%PhobiaModeVisuals` acceptable for a
spike vs production (a scope call).

**Group 4 — animation grammar and the rig pipeline** (lane A Q1, Q2, Q4, Q5,
Q6; S16 Q1–Q15). Lane A Q1 (how an intent tell is driven) and S16 Q5 (bespoke
tells: does the router grow rows, does the scene contract grow an override
table, or do modded bodies not have bespoke tells) are adjacent and should be
answered together — **note S16's joined cost: any bespoke trigger wins the
animation and loses the character-derived SFX.** S16's fifteen, in its own
order: Q1 the death-state name (`death` vs `die` vs alias vs defer); Q2 who owns
the trigger seam; Q3 is a modded character's death currently silent and is
combat not waiting for it (yes-no ×2, settled by **one capture**); Q4 revive;
Q5 bespoke tells; Q6 conditional state selection; Q7 where sub-clip VFX timing
lives; Q8 attachment points; Q9 idle desync; Q10 the script-less scene rule;
Q11 visual-QA gates (pick-many, lane C owns the build); Q12 baked data in
scenes; Q13 variant economy ("one rig, many skins" as the target shape?);
Q14 the blend convention (**partly taste; the eyes-on half is yours by
definition**); Q15 four capability scope declarations plus the pin.

**Group 5 — the build and QA gates** (lane A Q3 **merged with** lane C Q2, plus
lane C Q1, Q3, Q4, Q5). The merged one: *the export-log gap in
`tools/build_pck.ps1`* — lane A offers scan-the-export-log / extend the derived
contract to `.tscn` refs / both / neither; lane C offers all-three-rules /
export-log-only / all-three-as-warnings / none-yet. **One defect, two option
sets, one owner needed.** Then: the fallback policy's shape (four options,
including driving it off lane B's ledger instead); the `load_steps` drift; the
`Path.open("rb")` blind spot; and how captures get taken.

**Group 6 — the art ledger, the art bill, and shared-file ownership** (lane B
Q1–Q7; S17 klee 1–3, furina 1–6, kokomi 1–4, icons 1–5). The bill: the seven
Furina power badges (lane B Q1 ≡ S17 furina EB-65 territory); the three unhunted
Klee cards with **zero unclaimed Klee faces in the local pool**; Furina's
`change_the_bill` / `take_it_from_the_top`; the two energy icons and the two
Klee `model/` plates. The register: rights classification for 330 unclassified
surfaces (backfill `SOURCES.tsv` / a separate declaration file / leave until
public release is on the table); Kokomi's never-written source-uniqueness rule
(ratify pooling / adopt Furina's rarity split / something between); the
unenumerable aura prefix; `swift_currents`; the two relic-icon collisions; the
new Kokomi source collision; the seven unmapped powers; the 9-path
arm-texture/FMOD asymmetry. The wiring: which lane (`local`/`ci`/none) and
**which lane owns the one-line `tools/run_lints.py` edit** (lane B Q7 — lane C
deliberately left the same file untouched).
**Blocked until blocker 1 clears:** S17 furina Q3 (re-materialise the candidate
directories, or review from sources, or treat the sheets as historical) and
anything downstream of a sheet — including **M19**, where S17 furina Q4 and S17
icons pick (1) are the same question and the standing R212(1) default is
**set A — Fontaine Hydro**.

**Group 7 — enemy feasibility scope** (S18 1–4, 6, 8–11, 13–14; 5/7/12 folded
into group 1). Scope first, per curation: the ten unmapped Overgrowth
encounters; Act 1's four research bosses; whether the Underdocks block is costed
at all; whether the five-body leftovers row is split. Then: boss art-surface
scope (creature only / + map node / everything); **phobia-mode coverage —
reproduce / drop / per-body, across two incompatible filename conventions, and
it is simultaneously an accessibility surface**; the two bosses with no
candidate from either gallery (Soul Fysh, Queen + Torch Head Amalgam); the three
redesign-pressure rows with shipped content and no cover; Aeonglass, which has
no base animation to reskin against and is also the row the gallery calls its
strongest single boss argument; and the two register-hygiene items
(`TunnelerNormal`, `ScrollsOfBitingNormal`).

**Group 8 — release, rights, and ship scope** (S20 packaging's blocking six +
the version pick; performance 1–4; player-count 1–6; controller Q1–Q6; colour
Q1–Q5; localization Q1–Q4). The blocking ones, in the packaging file's own
order: **public release, yes or no** — everything else is downstream; **art
rights** (original / cleared / art-free package); a **licence** for our code and
an explicit statement of what it excludes; **credits content**; **distribution
channel and the account that owns it**; and **the version-format pick, because
it amends LAW**. Then: card-art delivery format (RGBA PNG 68 MiB / RGB ≈59 MiB /
WebP ≈9.5 MiB / JPEG ≈12.5 MiB — the last two need a code change and an eyes-on)
and topology (loose / atlas in the pck / loose with eviction); whether package
size matters for v1 at all; boot-cost self-reporting. Co-op: **does the public
target include co-op at all** (yes/no/later); what seat ceiling (2/3/4/whatever
the base game does); **does R144's multiplayer-only-card route stay LAW as
written, or become "co-op is base-kit-identical and we ship no co-op cards"**;
should `KleeTests` become a deploy or CI gate; is a live-`CombatState` harness
worth building; is a two-instance co-op understudy arm worth building on the
already-existing `/api/v1/multiplayer` endpoint. Accessibility and text:
controller support for mod-owned hover surfaces (support / declare mouse-only /
defer); the eighth note in the two Barbara titles (five options, one of which is
"settle nothing until the glyph question is closed by a capture"); authoring
resolution for mod UI icons (1× / 2× / 4× / defer); which aspect-ratio settings
the mod promises to look right on; the Furina/Kokomi seat colour; the buffed-
number green; idle sway and Phobia Mode; whether a mod-owned options screen is
in scope at all; and which of the offline automation candidates to build.
**Localization posture is one question asked three times** — S20 l10n Q1, S20
controller Q5, and S12 §3 Q44 — English-only-and-documented / English-only-but-
must-not-break / English plus community translations via
`res://klee/localization/<lang>/` / not decided tonight.

**Group 9 — the 57 S12 transfer questions**, in `s12-00-joined-read.md` §3,
already deduped there from 65 raw and grouped A–I (dependency pin · two engines
· save/identity/removal · co-op · testability · registration route ·
content-shape · localization · art/PCK/packaging). Read group A first (that is
group 2 above), then F, then C, then the rest — curation's order.

**Group 10 — S14 (surplus).** `s14-resonance-preread.md` §4 is questions only,
against reactions, co-op seats, companion nations, banner limits, UI and save
identity. Curation routes **all of S14 away from the sitting**; it is carried so
the material exists, not because anything is ripe.

---

# 9. Acceptance status against charter §8 — honestly

| §8 bullet | Status |
|---|---|
| Every started research stream has its required output, explicit deferral, or cited partial plus blocker | **PARTLY MET.** S12, S13, S14, S15, S18 are complete. S16 has its schema, four bodies, sidecar and matrix — but **the matrix was never confirmed by its author**. S17 has four of five families and **no joined ledger**. S20 has five of seven families and **no joined matrix**. **S19 does not exist at all.** All six gaps are recorded as explicit deferrals with re-run instructions in `BLOCKERS.md` §3, so the *deferral* half of this bullet is met; the *output* half is not, for S17, S19 and S20 |
| Fable curation recorded once per completed research stream | **PARTLY MET.** `CURATION.md` records touchpoints for **S15, S12+S13, S18 and S14**. **S16, S17, S19 and S20 are recorded as pending** — for three of them because the stream is partial, and for S19 because there is nothing to curate |
| Lanes A–C return isolated, tested branch handoffs; lane D returns a handoff or an S13-grounded blocker | **MET.** Four branches, four commits (`09864c2`, `800062b`, `0c08fdf`, `bd5b28d`), four handoffs, all targeted tests green, `--lane ci` 22/22 on every lane. Lane D returned a **handoff**, not a blocker, because S13 §6 returned a credible socket and the offline harness proved it |
| No governing doc, production sheet/asset, registered experiment, live game installation, or [USER]-owned checkout was altered | **MET**, on every agent's and lane's own statement. Lane A, B, C and D each modified **no existing file** — additions only. The primary checkout was read-only throughout; it moved three times, but under your own PRs (#108 and one more), not under any agent |
| `M45`, `M46`, enemy mappings, taste, rights, money and ship scope remain unruled | **MET.** `M46` is absent from this checkout and S15 records that rather than minting it. No id — `M-`, `EB-`, `R-` — was minted anywhere in this dispatch, by any stream or lane |
| The morning summary distinguishes facts, non-findings, defects, technical proposals, and [USER] questions | **MET** — §8.1 through §8.5 above |

**One extra thing the charter did not ask for but you should know:** three of
the four lanes independently found the *same* export-log gap in
`tools/build_pck.ps1`, from three different directions (lane A measured it by
deleting a texture; lane C read the source; lane D's whole safety argument
depends on the pack loader's collision behaviour next door). That is the
strongest signal in the dispatch that D1 is real.
