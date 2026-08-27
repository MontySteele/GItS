# Lane B handoff — art / provenance ledger (charter label `EB-148`)

**Branch:** `dispatch3-laneB-art-ledger` (worktree `../GItS-laneB`, cut from `main` `223a4ff`)
**Decides nothing.** Everything below is a mechanism, a measurement, or a numbered
question for [USER]. No art was selected, produced, retouched, or deleted; no
governing doc, sheet, constant or production asset was edited; the game was never
launched, deployed to, or written to.

---

## 1. What was built

Two new files, and nothing else changed:

| file | what it is |
|---|---|
| `tools/art_ledger.py` | the ledger: schema, join, checks, text report, JSON output |
| `tier0/tests/test_art_ledger.py` | 26 tests, all on synthetic fixtures under `tmp_path` |

### The ledger in one paragraph

A **row** is one *expected visual surface* — something the shipped mod will try
to load at runtime. Expectations are **derived, never listed**, from four
readers, and each row then joins to source, rendered output, packed path,
fallback, rights tier and review state:

| reader | what it finds | why it is needed |
|---|---|---|
| canonical YAML sheets + `Art.CardPortrait("id")` literals | card portraits | the same two universes `art_coverage.py` bills, so the two tools reconcile by construction |
| `"<char>/<sub>/<name>.<ext>"` literals in `klee-mod/KleeCode/**` | pck resources | a **superset** of the `KleePck.Path(...)` call sites — the salon-member bridge and the Bake-Kurage docket sprite hold their paths in constants and dictionaries, so a `KleePck.Path`-only regex under-bills them |
| `res://` refs inside packed **text** resources (`klee-mod/pck-src/**`, and the here-strings `tools/build_pck.ps1` authors) | scenes, materials, and the textures only a scene names | `select_bg.png`, `selection_splash.png` and `transition_wipe.png` are named by **no C# at all**. Without this reader the ledger calls three shipped surfaces stale and misses the combat layer sprites entirely. |
| concatenation prefixes, e.g. `"klee/powers/aura_" + element + ".png"` | the six aura badges | the set is **not enumerable by reading strings**, so the ledger attributes what is already on disk and says out loud that the universe is unknown, instead of reporting six working files as stale |

**Rights tiers are read, never assigned.** `docs/art-asset-manifest.md:79-81`
already defines the tiers the repo uses; the tool maps them onto the charter's
categories (`F` → `private-placeholder`, `O` → `public-safe`, anything else →
`unclassified`) and prints the evidence string beside every row. Evidence comes
from, in order: (1) the `tier` column of `art/SOURCES.tsv`, (2) a `Tier X`
declaration in the docstring of the generator that owns the out-path
(`art_lint.GENERATOR_OWNED`), (3) nothing — in which case the row is
`unclassified` **and says why**. Unclassified is a question for [USER], never a
default of either category. The two coverages are printed separately and are
**never summed**: a build that is 100% covered by private placeholders is 0%
ready to ship publicly, and one number cannot say both.

**Everything is rooted.** `--root` is *required*. Every read — sheets, mod
source, build script, curated registries, `SOURCES.tsv`, the pck contract, the
art tree — is relative to it. This worktree has no art at all (`ImageGen/` and
`art/raw/` are gitignored), which is exactly why a tool that could only read its
own checkout could be neither run nor tested here. The curated registries
(`art_lint.GENERATOR_OWNED` and friends, `art_coverage.KNOWN_STALE`) are read
out of `<root>/tools/*.py` by **AST literal evaluation, not import** — they are
per-checkout data, and importing would bind their module-level paths to the
wrong root.

### The checks

| check | fires when | class |
|---|---|---|
| `MISSING-PACKED` | the mod asks for a pck resource the build contract does not contain | defect |
| `STALE-ROW` | an `art/SOURCES.tsv` provenance row points at a rendered output that no longer exists | defect |
| `STALE-OUTPUT` | a rendered file no expected surface claims, with no `KNOWN_STALE` reason | defect |
| `UNINTENDED-FALLBACK` | another character's bytes reach a path nobody declared a fallback for (three shapes, below) | defect |
| `RIGHTS-INHERITANCE` | a generator declares Tier O for an out-path while reading a Tier F input | defect |
| `ACTIVE-FALLBACK` | a character has no art for a path `build_pck.ps1` *does* declare a fallback for, so the build will ship another character's bytes there | **reported, not a defect** — it is the sanctioned mechanism |
| `MISSING-RENDER` | an expected surface has no rendered output on disk | the art bill |

`UNINTENDED-FALLBACK` has three shapes, and only the first needs a build log:

1. a build-log line `X fallback: <rel> <- Klee` for a path `build_pck.ps1` does
   not declare (script drift);
2. a build-log line that fired **even though the character has its own art** —
   the C4 `-Exclude` defect, where the copy block silently staged zero files and
   both characters dropped back onto Klee's face with every gate green;
3. **statically, with no log at all:** two characters' rendered outputs are
   byte-identical. A declared fallback does *not* excuse this — an *active*
   fallback means the character has no rendered file, so reaching this check
   means it has one and that one is another character's bytes.

---

## 2. Exact commands

Run from the lane worktree. The lane has no `.venv`; the primary checkout's
interpreter was used read-only.

```
# the report, read-only against the art-bearing primary checkout
python tools/art_ledger.py --root C:\Users\Monty\Documents\GitHub\GItS

# machine-readable ledger + a build log to reconcile fallbacks against
python tools/art_ledger.py --root <checkout> --json ledger.json --build-log deploy.log

# gate form
python tools/art_ledger.py --root <checkout> --strict     # defect-class findings => exit 1

# tests (targeted)
python -m pytest tier0/tests/test_art_ledger.py -q
python -m pytest tier0/tests/test_art_ledger.py tier0/tests/test_art_coverage.py \
                 tier0/tests/test_art_lint_full_set.py -q

# lane gate
python tools/run_lints.py --lane ci
```

Results, all from this worktree:

| command | result |
|---|---|
| `pytest tier0/tests/test_art_ledger.py -q` | **26 passed** in 1.4s |
| `pytest` the three art test files | **46 passed, 4 skipped** in 3.4s |
| `pytest tier0/tests -q -n 2 -m "not battery"` | **2956 passed, 46 skipped, 12 xfailed** in 31s |
| `python tools/run_lints.py --lane ci` | **OK: 22 lints passed** |

No unrelated existing red appeared.

---

## 3. The proving run against the primary checkout (read-only)

**Read this caveat first.** The primary checkout **moved during this lane's
work**. `PREFLIGHT.md` recorded `main` `223a4ff`; part-way through, PR #108
(`EB-67`: Kokomi's relic and power icons) merged and the primary reached
`c09b6b6`, and the pck was rebuilt at 20:39. The output below is the **later**
state. Both states are reported in §4 because the difference is itself the
lane's best demonstration.

It moved a **third** time before this branch was pushed (`c09b6b6` → `98fb3a0`,
still clean). No run was re-taken against `98fb3a0`, so the numbers below are
stamped `c09b6b6` and should be re-taken before anyone quotes them. Re-taking
them is one command (§2) and needs no state.

```
git -C C:\Users\Monty\Documents\GitHub\GItS rev-parse --short HEAD   ->  c09b6b6
git -C C:\Users\Monty\Documents\GitHub\GItS status --short           ->  (clean)
klee-mod\assets\klee.pck.contract.txt  mtime 2026-08-26 20:39:15  (gitignored, machine-local)
```

```
========================================================================
ART LEDGER  (art-ledger-v1)
root: C:\Users\Monty\Documents\GitHub\GItS
========================================================================

EXPECTED SURFACES BY KIND
  kind       expected  covered  missing  fallback  defect
  card            294      270       24         0       0
  material          3        3        0         0       0
  model            12       12        0         0       0
  power            58       51        0         0       7
  relic             3        3        0         0       0
  salon             6        6        0         0       0
  scene            21       20        0         0       1
  summon            1        1        0         0       0
  ui               24       23        0         1       0
  vfx               3        3        0         0       0
  TOTAL           425      392       24         1       8

------------------------------------------------------------------------
RIGHTS COVERAGE -- REPORTED SEPARATELY, NEVER SUMMED
  Tier categories are read from declared evidence (docs/art-asset-manifest.md:79-81).
  This tool assigns no rights tier to anything.
------------------------------------------------------------------------

  private-placeholder: 90 covered of 90 expected
    card         24 /   24
    model        12 /   12
    power        33 /   33
    relic         1 /    1
    salon         3 /    3
    ui           17 /   17

  public-safe: 5 covered of 5 expected
    salon         3 /    3
    ui            2 /    2

  unclassified: 297 covered of 330 expected
    card        246 /  270
    material      3 /    3
    power        18 /   25
    relic         2 /    2
    scene        20 /   21
    summon        1 /    1
    ui            4 /    5
    vfx           3 /    3

  UNCLASSIFIED is a question for [USER], not a default of either
  category: these surfaces carry no SOURCES.tsv tier and no
  generator tier declaration.

------------------------------------------------------------------------
COMPUTED PATHS -- THE LEDGER CANNOT ENUMERATE THESE
------------------------------------------------------------------------
  These call sites build a resource path by concatenation, so the
  set they demand is not readable from the source. Every file
  already sitting under the prefix is billed to the site; a member
  of the set with NO file is invisible to this tool and to every
  other string-reading gate in the repo.

  klee/powers/aura_*  (klee-mod/KleeCode/Powers/KleePowerIcons.cs:143)
    6 file(s) attributed: aura_anemo.png, aura_cryo.png, aura_electro.png, aura_geo.png, aura_hydro.png, aura_pyro.png

------------------------------------------------------------------------
FALLBACKS DECLARED IN tools/build_pck.ps1
------------------------------------------------------------------------
  furina: 9 path(s) fall back to klee
  kokomi: 9 path(s) fall back to klee

  ACTIVE right now: 1
    pck:furina/ui/transition_wipe.png: furina falls back to klee for ui/transition_wipe.png

------------------------------------------------------------------------
FINDINGS
------------------------------------------------------------------------

MISSING-PACKED -- 8
  pck:furina/powers/courtroom_drama.png: asked for at klee-mod/KleeCode/Powers/KleePowerIcons.cs:102; not in klee-mod/assets/klee.pck.contract.txt
  pck:furina/powers/fortissimo_guard.png: asked for at klee-mod/KleeCode/Powers/KleePowerIcons.cs:99; not in klee-mod/assets/klee.pck.contract.txt
  pck:furina/powers/quick_change.png: asked for at klee-mod/KleeCode/Powers/KleePowerIcons.cs:104; not in klee-mod/assets/klee.pck.contract.txt
  pck:furina/powers/stagehands.png: asked for at klee-mod/KleeCode/Powers/KleePowerIcons.cs:100; not in klee-mod/assets/klee.pck.contract.txt
  pck:furina/powers/stagehands_encore.png: asked for at klee-mod/KleeCode/Powers/KleePowerIcons.cs:101; not in klee-mod/assets/klee.pck.contract.txt
  pck:furina/powers/the_gallery_stirs.png: asked for at klee-mod/KleeCode/Powers/KleePowerIcons.cs:103; not in klee-mod/assets/klee.pck.contract.txt
  pck:furina/powers/unheard_confession.png: asked for at klee-mod/KleeCode/Powers/KleePowerIcons.cs:110; not in klee-mod/assets/klee.pck.contract.txt
  pck:kokomi/model/combat.tscn: asked for at klee-mod/KleeCode/Diagnostics/KleeSceneTelemetry.cs:44; not in klee-mod/assets/klee.pck.contract.txt [requested only by the diagnostics probe list]

UNINTENDED-FALLBACK -- 0

RIGHTS-INHERITANCE -- 0

STALE-ROW -- 0

STALE-OUTPUT -- 6
  file:ImageGen/images/furina/ui/energy_icon_22.png: no expected surface claims this file and it carries no KNOWN_STALE reason
  file:ImageGen/images/furina/ui/energy_icon_74.png: no expected surface claims this file and it carries no KNOWN_STALE reason
  file:ImageGen/images/model/character_klee_full_wish.png: no expected surface claims this file and it carries no KNOWN_STALE reason
  file:ImageGen/images/model/klee_character_card.png: no expected surface claims this file and it carries no KNOWN_STALE reason
  file:ImageGen/images/ui/energy_icon_22.png: no expected surface claims this file and it carries no KNOWN_STALE reason
  file:ImageGen/images/ui/energy_icon_74.png: no expected surface claims this file and it carries no KNOWN_STALE reason

MISSING-RENDER -- 24
  card:klee:powder_charge / hold_the_line / smoke_and_sparks
  card:furina:change_the_bill / take_it_from_the_top / grand_gala
  card:kokomi:  (15 rows -- the Kokomi art bill)
  card:shared:confiscated / spotlight_center_stage / spotlight_guest_cast

KNOWN-STALE files (recorded reason, NOT coverage) -- 4
  ImageGen/images/cards/furina/rising_tide.png            (A4 red-pen, 2026-07-28)
  ImageGen/images/cards/kokomi/swift_currents.png         (G8, Neap Tide v2.1)
  ImageGen/images/furina/model/furina_wikipedia_cutout.png   working file: $pckExclude
  ImageGen/images/kokomi/model/kokomi_portrait_cutout.png    working file: $pckExclude

PACKED BUT NOT EXPECTED -- 6
  res://furina/ui/energy_icon_22.png      res://furina/ui/energy_icon_74.png
  res://klee/model/character_klee_full_wish.png
  res://klee/model/klee_character_card.png
  res://klee/ui/energy_icon_22.png        res://klee/ui/energy_icon_74.png

========================================================================
RECONCILIATION to tools/art_coverage.py
  card-sized outputs expected: 294   covered: 270   missing: 24
========================================================================
exit=0
```

(The `MISSING-RENDER` block is abbreviated above for readability; the tool
prints all 24 rows in full, and `--json` carries every one.)

### Reconciliation to the S17 baseline

`review/dispatch3/s17-art/baseline-run-2026-08-26.txt` (recorded at `223a4ff`)
reports **294 expected / 270 covered / 24 missing** card-sized outputs. The
ledger reports **exactly the same three numbers**, and
`test_card_universe_matches_art_coverage_on_this_repo` pins the two id sets
equal so they cannot silently diverge. The baseline's two `[known]` stale card
files (`rising_tide`, `swift_currents`) also appear, carrying the same recorded
reasons, read out of `art_coverage.KNOWN_STALE` rather than restated.

**No difference to explain on the card surface.** The ledger's *totals* differ
because it bills **425 surfaces, not 294** — the extra 131 are the power,
relic, UI, model, salon, summon, material, scene and VFX surfaces that
`art_coverage.py` was never written to see. That is the whole point of the
lane, and it is why the report keeps the card reconciliation in its own block.

---

## 4. Findings

### F1 — the ledger caught a live gap mid-run, and then watched it close

At `223a4ff` (the preflight SHA) the ledger reported **16** `MISSING-PACKED`
rows. Eight of them were Kokomi's power and relic icons: the C# asked for
`kokomi/powers/*.png` and `kokomi/relics/pearl_of_wisdom.png`, the PNGs existed
on disk under `ImageGen/images/kokomi/`, and the deployed pack — built
19:36:02, the one behind mod `0.2-1155` [USER] is playtesting on — did not
contain them. Art present, art paid for, art not shipping.

After PR #108 merged and the pck was rebuilt at 20:39, those eight rows went
green on the next run with no change to the tool.

**What this establishes:** the join is the instrument. Neither half is a
finding on its own — `art_coverage.py` bills only cards and cannot see a power
badge at all; the pck contract is derived and correct about its own contents;
the C# is correct about what it wants. Only *source × rendered × packed* says
"the art exists and is not in the pack."

### F2 — seven Furina power badges have no art at all (open)

`courtroom_drama`, `fortissimo_guard`, `quick_change`, `stagehands`,
`stagehands_encore`, `the_gallery_stirs`, `unheard_confession`. Verified by eye
against the primary: `ImageGen/images/furina/powers/` holds 15 files and none of
these seven. They fall to the base-game placeholder icon at runtime. This is a
**real art bill that no existing instrument prints**, because every existing
coverage number is a card number.

### F3 — six rendered files nothing asks for

`ui/energy_icon_22.png` and `ui/energy_icon_74.png` (for both Klee and Furina),
plus `model/character_klee_full_wish.png` and `model/klee_character_card.png`.
The energy icons are *packed* and unreferenced: all three characters point
`CustomEnergyCounterPath` at the base game's
`res://scenes/combat/energy_counters/ironclad_energy_counter.tscn`
(`klee-mod/KleeCode/Klee.cs:176`, `Furina.cs:100`, `Kokomi.cs:155`), so the
mod's own energy art was produced and then routed around. The two `model/`
files look like source plates that ship because the `model` copy block is a
blanket `*.png`. All six are candidates for a `KNOWN_STALE`-style recorded
reason **or** for deletion — both are calls, not defects.

### F4 — one active fallback, and it is the documented one

`furina/ui/transition_wipe.png` falls back to Klee's wipe. That is deliberate
and written down: `tools/gen_transition_wipe.py`'s docstring says "Furina
deliberately has no wipe of her own and keeps Klee's via build_pck's
`Copy-FurinaFallback` (art-sprint-spec sec.8 sanctions the shared fallback)."
The ledger found it from the build script alone and classified it `active`,
not `unintended` — which is the discrimination the charter asked for.

### F5 — one path the repo *cannot* bill, now named

`klee-mod/KleeCode/Powers/KleePowerIcons.cs:143` builds its resource path by
concatenation: `"klee/powers/aura_" + aura.Element.ToString().ToLowerInvariant() + ".png"`.
No string-reading gate in this repo — this one included — can enumerate what
that demands. The ledger attributes the six files already under the prefix and
prints the prefix under a heading that says the set is unknown. **A seventh
element added to the enum with no icon would be invisible to every gate we
have.** That is a structurally invisible defect in the sense the house rule
means, and the honest fix is a curated list plus a lint — which is a build, not
a report, and is not this lane's to make.

### F6 — rights evidence is thin, and the thinness is the finding

Only **95 of 425** surfaces carry declared rights evidence (90
private-placeholder, 5 public-safe). **330 are `unclassified`** — including
**270 of the 294 card portraits**, because `art/SOURCES.tsv` rows exist for
candidates and for a handful of UI/model outputs but not for most shipped card
outputs. `RIGHTS-INHERITANCE` found nothing, which is a genuine null: the two
generators that declare Tier O (`gen_transition_wipe.py`, `gen_salon_glyphs.py`)
are both purely procedural, and the two that derive from wiki plates
(`gen_furina_stills.py`, `gen_kokomi_stills.py`) both declare Tier F correctly.

**What this does NOT establish:** it does **not** mean 330 surfaces are
un-clearable, or that any of them is or is not public-safe. It means the repo
has no machine-readable answer for them today. Every one of those rows is a
question, and none of them was answered here.

---

## 5. What this does NOT establish

- **Nothing about how anything looks.** The ledger reads names, paths, sizes of
  set, and bytes-for-identity. It has never opened an image and cannot tell you
  whether a portrait is good, on-model, or the right character.
- **No rights verdict on any asset.** Tiers are transcribed from declarations
  that already exist in the repo. `unclassified` means "no declaration found",
  not "unsafe" and not "safe".
- **No claim about the running game.** Everything is read from the checkout and
  from the pck *contract*. The pack itself was not opened, the game was not
  launched, and mod `0.2-1155` was not touched.
- **The pck contract is gitignored and machine-local.** On a fresh clone or in
  CI, `MISSING-PACKED` reports every pck surface. That is honest (there is no
  pack) but useless as a gate — see debt D1.
- **The primary checkout is a moving target.** Both runs in §3/§4 are stamped
  with the SHA and the contract mtime for exactly that reason.

---

## 6. Known debt

| id | debt |
|---|---|
| D1 | `MISSING-PACKED` is meaningless where no pck has been built (fresh clone, CI). The tool reports it plainly rather than guessing; a gate form needs a "contract absent → skip this check" mode, which is a policy call, not a code call. |
| D2 | Rendered-output presence is `is_file()` only. Size, dimensions and decodability are `art_lint`'s job and were deliberately not duplicated — but that means a 0-byte PNG counts as covered here. |
| D3 | `PCK_SOURCE_RULES` (res:// → ImageGen) is curated from `build_pck.ps1`'s copy blocks. Four non-obvious rules are pinned by `test_pck_source_map_rules_are_still_in_the_build_script`; the twelve generic ones are not, because they come from two `foreach` loops whose literal text is `'ui', 'powers', 'relics', 'model'`. A new copy block with a new layout would need a new rule. |
| D4 | The three fallback shapes cover the mechanism `build_pck.ps1` actually implements. A future third character, or a fallback source other than Klee, is parsed correctly, but a fallback implemented some *other* way would not be seen. |
| D5 | Byte-identity across characters is the static unintended-fallback proof. Two characters wearing *visually* identical art that differs by one byte is invisible to it. Perceptual hashing was not attempted. |
| D6 | The tool is not wired into `tools/run_lints.py` — see the patch note in §7. |
| D7 | The `[computed]` attribution (F5) closes a false-positive hole but does not close the real one: an unenumerable set with a *missing* member is still invisible. |

---

## 7. Patch note — a shared-file change I did NOT make

`tools/run_lints.py` is a shared file and Lane C may also want it, so per
charter §5 this lane wrote a note instead of racing the edit.

**Proposed (technical, not a scope call):** add to the `local` lane, *not* the
`ci` lane —

```python
    Lint("art-ledger", "local", ("tools/art_ledger.py", "--root", ".", "--strict")),
```

**Why `local` and not `ci`:** the `ci` lane is the pre-push gate and runs on
machines with no `ImageGen/` and no pck contract, where `--strict` would fail on
every pck surface for a reason that is not a defect (D1). Even on an
art-bearing machine it would fail today on F2 and F3, which are open art bills
and open recorded-reason calls — a gate that is red for known, accepted reasons
teaches people to ignore it. **Wiring it into any lane at all is [USER]'s call,
and it should follow the D1 skip mode and the F2/F3 dispositions, not precede
them.**

---

## 8. Merge risks

1. **Two new files only.** `tools/art_ledger.py` and
   `tier0/tests/test_art_ledger.py`. Nothing existing was edited, so there is no
   textual conflict surface with lanes A, C or D, or with the research rail.
2. **Lane C reads Lane B's schema.** The charter has Lane C consume this schema
   "through a fixture or adapter". The stable contract is `SCHEMA_VERSION =
   "art-ledger-v1"` and the `Row` dataclass field names, both asserted by
   `test_json_ledger_is_machine_readable_and_carries_the_schema`. If Lane C
   copied fields before this branch settled, re-check against that test.
3. **Test-time behaviour depends on the checkout.** Two tests read the real repo
   (`test_pck_source_map_rules_are_still_in_the_build_script`,
   `test_card_universe_matches_art_coverage_on_this_repo`). The first skips when
   `build_pck.ps1` is absent; the second imports `art_coverage` and compares id
   sets only, so it passes with no art present. Both are green in this worktree,
   which has no art.
4. **`art_coverage.py` is imported by one test.** If a concurrent branch changes
   its `SHEETS` / `TOKENS` / `mod_art_keys` shape, that test fails — by design.
   It is the tripwire that keeps the two tools billing one card universe.
5. **No dependency added.** `yaml` only, which the repo already requires.
6. **The proving run used the primary checkout's interpreter** (this worktree
   has no `.venv`). Nothing was written to the primary; `__pycache__` landed
   only under `../GItS-laneB`.

---

## 9. Numbered questions for [USER]

Each is a pick list, and each is where this lane stopped.

**Q1 — the seven Furina power badges (F2).** `courtroom_drama`,
`fortissimo_guard`, `quick_change`, `stagehands`, `stagehands_encore`,
`the_gallery_stirs`, `unheard_confession` have no art and render the base-game
placeholder.
 (a) commission/hunt art for all seven as one batch;
 (b) art for a named subset, placeholder accepted for the rest;
 (c) accept the base-game placeholder for all seven and record the acceptance so
     the ledger stops billing them;
 (d) defer — leave them on the bill as an open art debt.

**Q2 — the two energy icons (F3).** `energy_icon_22.png` / `energy_icon_74.png`
exist, are packed, and are unreachable because all three characters use the base
game's energy counter scene.
 (a) delete the four files and let them leave the pack;
 (b) keep them and add a recorded reason so they read as deliberate, not stale;
 (c) point the characters' `CustomEnergyCounterPath` at our own counter (a real
     feature, not a cleanup).

**Q3 — the two Klee `model/` plates (F3).** `character_klee_full_wish.png` and
`klee_character_card.png` are source plates that ship because the `model` copy
block is a blanket `*.png`.
 (a) delete them;
 (b) rename them to match `$pckExclude` (i.e. treat them as working files) so
     the build stops packing them;
 (c) keep as-is with a recorded reason.

**Q4 — the unenumerable aura prefix (F5).** A seventh element added to the enum
with no icon is invisible to every gate in the repo.
 (a) build a curated element→icon list plus a lint that pins it against the C#
     enum (the "structurally invisible defect" house pattern);
 (b) leave it, accepting the blind spot, now that it is named;
 (c) change the call site to enumerate literals instead of concatenating.

**Q5 — rights classification (F6).** 330 of 425 surfaces have no
machine-readable rights evidence, including 270 shipped card portraits.
 (a) backfill `art/SOURCES.tsv` rows for every shipped output so the tier column
     answers for all of them;
 (b) add a separate rights declaration file the ledger reads, leaving
     `SOURCES.tsv` as the fetch ledger;
 (c) leave them unclassified until a public release is actually on the table.

**Q6 — wiring (D6, §7).**
 (a) `local` lane with the D1 skip mode, after Q1–Q3 are dispositioned;
 (b) `ci` lane (needs D1 *and* Q1–Q3 resolved first, or it is red on day one);
 (c) no lane — run it by hand when the art question comes up.

**Q7 — ownership of the shared-file edit.** `tools/run_lints.py` is shared with
Lane C. If Q6 is (a) or (b), which lane owns that one-line edit?
 (a) Lane B; (b) Lane C; (c) a named integrator at merge time.
