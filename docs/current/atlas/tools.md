# Atlas — tools

> **Lifecycle: LIVING** — expected to change; read it to work on the project.

Scope: `tools/` — the roster codegen entry points (`gen_*`), the art pipeline
(`art_*`, `cut_*`, `*_stills`), every `lint_*`, the canon extractors
(`extract_base_game_pool.py`, `canon_role_tempo.py`, `role_tempo.py`), and
`tools/combat_layer_fences/`. `tools/build_pck.ps1` lives here but is documented
in `docs/current/atlas/klee-mod-build-pck.md`; the generator's card contract is
`docs/current/atlas/klee-mod-cards.md`.

## 1. Purpose

The **instrument shed**: nothing here ships to a player, and everything here
either derives a committed artifact from a canonical source or refuses a commit
that broke one. Its unifying discipline is the house "structurally invisible
defect" rule — when a defect can exist without changing anything a human reads
(same card text, same rendered picture, same green suite), a curated list plus a
lint is the only catcher, and the curated list is itself checked for rot
(`art_lint.py:349-353`, `lint_generated_structure.py:20-24`). Tools are **not**
design authorities: the coverage lint counts and names no card
(`lint_role_tempo_coverage.py:6-12`), the register lint claims no semantic
judgment (`lint_furina_registers.py:15-19`), and the sheet is the source of
truth a tool reads, never one it edits — with exactly two ruled exceptions
(`suggest_role_tempo_tags.py --land`, and the codegen writing C#). Nothing here
may become a simulator or a balance author.

## 2. Entry points

Run from the repo root. `tools/` is an implicit namespace package (no
`__init__.py`), so both `python3 tools/x.py` and `from tools import x` work;
scripts that import siblings insert the root themselves
(`lint_role_tempo_coverage.py:70-77`).

```sh
# CI's exact list (.github/workflows/repo.yml:42-96) — the softlock gates
# CI's exact list, in order (S-numbers are validate.ps1's deploy gates)
python3 tools/lint_handwritten_parity.py   # S6      | lint_pool_membership.py  S6b
python3 tools/lint_constant_parity.py      # S6e     | lint_ancient_coverage.py S6d
python3 tools/lint_op_parity.py            # engine OPS vs drafter pricing
python3 tools/gen_roster_cards.py --check  # S6a codegen staleness
python3 tools/suggest_role_tempo_tags.py --check   # [--land] writes the 3 sheets
python3 tools/lint_role_tempo_coverage.py --gate   # [--write-debt]
python3 tools/lint_roster_registry.py
python3 tools/lint_vendor_pin.py           # [--write] regenerates manifests
python3 tools/art_coverage.py              # CI runs it WITHOUT --strict on purpose

# not in CI
python3 tools/lint_text_encoding.py [path.py]      # scans tier0/ tier05/ tools/
python3 tools/lint_generated_structure.py          # L1/L2/L3 on emitted .cs
python3 tools/art_lint.py                          # also run by art_process
python3 tools/dump_claimed_sources.py ; python3 tools/card_distinctness_report.py --gate
python3 tools/canon_role_tempo.py [--from-json]    # needs game + ilspycmd
python3 tools/extract_base_game_pool.py --characters Ironclad,Silent [--emit-sheet]
python3 tools/art_fetch.py && python3 tools/art_process.py [--apply-picks art/picks.tsv]
python3 tools/art_hunt.py Furina ; python3 tools/art_contact_sheet.py --list
python3 tools/art_source_census.py --character kokomi [--reuse-cap N] [--tsv OUT]
.venv/Scripts/python tools/cut_combat_layers.py klee [--check]
.venv/Scripts/python tools/gen_furina_stills.py    # and gen_kokomi_stills.py
.venv/Scripts/python tools/gen_char_icon_outlines.py [--check]

python3 -m pytest tier0/tests/test_sheet_lints.py tier0/tests/test_art_lint_full_set.py \
    tier0/tests/test_encoding_gate.py tier0/tests/test_char_stills.py -q
```

`tools/README.md:9-42` is the authoritative map of which tool is gated by
`validate.ps1`, which by pytest only, and which is a manual instrument.

## 3. Key invariants

- **Every text read/write declares `encoding=`.** Structural, not behavioural —
  the platform that fails (Windows cp1252) is not the platform that tests
  (`lint_text_encoding.py:4-16`, `:33-36`); binary I/O and `PIL.Image.open` are
  the only exemptions (`:38-41`, `:52`). Per-file bare-`open` counts are a debt
  ledger that may only shrink (`tier0/tests/test_encoding_gate.py:30-57`).
- **`art/plan.tsv` is UTF-8 and CRLF**: read with `encoding="utf-8"`,
  `newline=""`, and `rstrip("\r\n")` on the whole line, or the last column
  (`register`) carries a `\r` and L3/L4 silently stop matching
  (`art_fetch.py:38-58`).
- **The three duplicate rules PARTITION on `proto_`, they do not exempt it**
  (`art_lint.is_prototype`). A prototype placeholder wears a shipped card's
  source, crop and pixels on purpose, so L1, L7 and L12 compare prototypes with
  prototypes and shipped with shipped and never across — while **two prototype
  cards on one picture is still a finding**, because that is the defect the
  rules exist for. `dump_claimed_sources` splits the same way, into CLAIMED and
  PLACEHOLDER, so a hunt still sees a borrowed title without it counting as a
  claim; `art_contact_sheet --batch prototype` is the one page the whole set is
  vetoed on.
- **art_lint scopes to EFFECTIVE picks only** — auto rows and shortlist rank 1;
  dead ranks may share sources freely (`art_lint.py:4-5`). `source_group`
  defaults to BLANK and blank means strict L1 (`:35-46`).
- **An art pool is priced in (source, anchor) SLOTS, never in sources**
  (`art_source_census.py`). `cover` clamps its crop inside the image, so a
  source's slot count is `min(reuse_cap, floor(range / 0.085) + 1)` over the
  valid centre range `[f/2, 1 - f/2]` its own geometry allows — a big splash
  backs six faces, a transparent icon exactly one. **`reuse_cap` is a TASTE
  call, not a geometric one**, and Kokomi's 2026-08-23 "6-slot deficit" was
  entirely an artifact of a stale one (`EB-121`; the doc's 70 reconciles at
  `--reuse-cap 4`, the shipped plan is at 6).
- **A worktree reaches the main checkout's art by `--art-root`, never by a
  link.** `art/raw/` and `art/candidates/` are gitignored Tier F and exist only
  on the art-bearing checkout; `art_process.py` and `art_contact_sheet.py` both
  take an absolute `--art-root` so a branch's `plan.tsv` renders against those
  pixels without a junction `git worktree remove` could follow
  (`operations/worktrees.md`). `art_process --assets` renders candidates
  ONLY — nothing is placed and the manifest is untouched, so a gate review
  cannot promote an unreviewed rank 1 into the shipping tree.
- **No plan row may claim an out-path a generator owns (L11)**, and the curated
  `GENERATOR_OWNED` map is itself verified — named script must exist and must
  contain the filename (`art_lint.py:354-411`).
- **art_coverage reports three disjoint sets** — COVERED / MISSING / STALE — off
  the canonical sheets, never a prose bill (`art_coverage.py:9-16`, `:65`). Its
  universe is the sheets **plus** every portrait key the shipped mod requests
  (`RosterArt.CardPortrait("id")`, scanned — `:90-91`, `:155`): billing the sheets alone
  hid three cards that ship with no sheet row (D4 / EB-36). Still
  surfaces frame off the ALPHA BBOX, never the image frame, and that rule lives
  once, in `char_stills.py:9-13`, because two copies drift.
- **Layer cuts are a hard partition, asserted**: at-rest recomposition is
  pixel-exact by construction (`cut_combat_layers.py:23-25`, `:259`);
  `--check` re-cuts to a temp dir and diffs (`:329`, `:368-369`).
  `dilate_priority` is deliberately NOT z-order — it decides who keeps the
  shared outline pixels, and the object in FRONT wins
  (`combat_layer_fences/klee.yaml:26-29`).
- **Decompiled game material never enters the repo.** The scripts are safe to
  commit; everything they write goes to gitignored `game_ref/`, and the ILSpy
  tree is deleted after each run (`extract_base_game_pool.py:20-25`,
  `canon_role_tempo.py:5-15`). Machine paths come from `klee-mod/local.props`
  only (`extract_base_game_pool.py:96`, `:145-150`).
- **The canon baseline is read STRUCTURALLY (Cmds, DynamicVars, TargetType,
  reached models), never off card text** — that keeps card text out of the
  process and makes the tag-through real (`canon_role_tempo.py:14-33`). **One
  exception, declared:** the `regent_stars` package's membership is a curated
  list cited to `docs/current/research/regent-stars-economy.md`, because a
  Star price is a cost FIELD on the model and leaves no mark in a card body a
  structural read could find (EB-192 / R231, `canon_role_tempo.py`
  `REGENT_STARS`). It is locked to that census by test, and the committed
  baseline stays percentages-only either way.
- **Parity lints are total by construction**: an unclassified `public const int`
  or an unpriced `OPS` key is a FINDING, not a skip
  (`lint_constant_parity.py:19-27`, `lint_op_parity.py:26-40`). `lint_vendor_pin`
  runs in BOTH directions, because a one-directional manifest never notices an
  ADDED file (`lint_vendor_pin.py:8-14`, rules 1-7 at `:16-33`).
- **`tools/` is deliberately excluded from the register-isolation scan**: art
  selection is a legitimate reader of `register` (`lint_register_isolation.py:25-31`).

## 4. Rulings that shaped it

- **R67 / R68** — dead knobs deleted rather than marked, and the Furina
  experiment scripts moved to `tools/archive/` keeping their hand-rolled seeds:
  an archived one-shot is the record of a measurement, not a thing to re-run
  (`tier0/DECISIONS.md:2065-2078`, `:2122-2160`; `tools/README.md:44-58`).
- **R69** — `lint_unique_names` extends to relic display names read out of the
  emitted C#, not a manifest; both sides of the settled clash are reserved
  (`tier0/DECISIONS.md:2190-2205`).
- **R70** — "latest is not a version": unpinned build identity is what
  `vendor/`'s sha pin and `lint_vendor_pin` rule 1 refuse
  (`tier0/DECISIONS.md:2209-2247`; `vendor/README.md:26-28`).
- **R81** — distinctness thresholds ratified (uniq ≥ 70, maxclu ≤ 5, neardup
  ≤ 0.40/card); `top%`/`vocab` carry no gate permanently, and the curated
  known-failing list may only shrink (`tier0/DECISIONS.md:2563-2591`).
- **R85** — the register convention lands, which is what `lint_furina_registers`
  formalizes mechanically while leaving the semantic half to [USER]
  (`tier0/DECISIONS.md:2699-2745`; `lint_furina_registers.py:5-20`).
- **R90/1a, 1c** — the coverage lint stays a COUNTING tool with no magnitude
  gate; floors are re-derived from canon PACKAGES, and an anchored package must
  clear its own floor with equality (`tier0/DECISIONS.md:3024-3060`;
  `canon_role_tempo.py:290`, `:351`, `:435`, `:506`).
- **R91** — closing A-G1 is what let `--land` exist at all and flipped the
  suggester from proposal to parity artifact (`suggest_role_tempo_tags.py:12-27`);
  2b gives every meter a bounded/unbounded property with the cap READ from
  `tier0/constants.py` (`role_tempo.py:295`, `:329`), 2c makes meter-reading
  damage `scaling` and `frontload` only if it pays at zero, 2d puts `sustain` on
  the never-linted list (`tier0/DECISIONS.md:3084-3136`; `role_tempo.py:107`).
- **R92/3b** — a sheet-schema field has TWO readers (`Card.from_dict` and
  `gen_klee_cards.CARD_FIELDS`), so the cross-session note is filed BEFORE the
  field lands (`tier0/DECISIONS.md:3145-3165`).
- **D4** — a prediction must name an instrument that can SEE the changed object;
  the sim is one-seat, which is why `support` is never linted
  (`tier0/DECISIONS.md:2446-2466`; `lint_role_tempo_coverage.py:45-48`).

## 5. Traps

- **`--gate` fails on a VANISHED pinned finding too.** A stale pin means a cell
  moved and nobody said so; and no floor may ever be adjusted to make the gate
  pass (`lint_role_tempo_coverage.py:56-63`).
- **The "R87" cited inside `lint_generated_structure.py:9-13` is a defect id
  from the playtest-2 batch review, NOT `tier0/DECISIONS.md`'s R87** (which is
  the sweep backlog, `:2834`). Tool docstrings carry local label schemes.
- **`docs/art-claimed-sources.tsv` is derived and nothing enforces its
  freshness** — regenerate after any `plan.tsv` change (`tools/README.md:40-42`).
- **`art_lint`'s L12 pixel gate reads the CANDIDATES directory**, so a stale
  leftover candidate can manufacture a finding about a card whose out-path was
  never written (`art_lint.py:604-621`); it is dead on clean checkouts, and
  `lint_sheet_comments.py` is gated on `furina-cards.yaml` ONLY — 35 open
  findings elsewhere are unlinted, not absent (`tools/README.md:22-28`).
- **Fence coordinates are pinned to one artwork revision.** If the source image
  changes, re-digitize; `--check` exists to prove the generalization never moved
  Klee's shipped bytes (`cut_combat_layers.py:11-16`, `:31-34`;
  `combat_layer_fences/klee.yaml:1-12`).
- **`gen_kokomi_stills.py` has NO byte-pin twin** the way Furina's does, and
  Kokomi's source arrives on a WHITE plate — fed to the same code it degrades
  every framing rule to frame-centring, silently reintroducing the B4 defect
  (`tools/README.md:37`; `gen_kokomi_stills.py:16-22`).
- **`tools/archive/` scripts using `parent.parent` compute the repo root as
  `tools/` and will not import until that line is fixed** (`tools/README.md:60-65`).
  `GITS_ILSPY_TREE` is opt-in and env-only for the same class of reason: a
  persistent tree is decompiled game source outside `game_ref/`
  (`extract_base_game_pool.py:47-52`).
- **Native stderr kills a PowerShell deploy even at exit 0** — `lint_constant_parity`
  printing "OK" once took the deploy down; every native call goes through the EAP
  helper (`tier0/tests/test_repo_python_convention.py:1-26`).
- **`art_coverage` in CI asserts nothing about art**: `ImageGen/` is gitignored
  Tier F and absent on a runner, so the bill is empty by construction — the job
  proves the tool still runs (`.github/workflows/repo.yml:91-96`).

## 6. Reading order

1. `tools/README.md` — which tool is gated by what; orphan status is otherwise
   undiscoverable.
2. `.github/workflows/repo.yml:24-96` — the fresh-clone contract every session
   inherits, plus the recorded NOT-doing list.
3. `tools/lint_text_encoding.py:1-41` — read before touching any file I/O here.
4. `tools/art_lint.py:1-56` then `:349-411` — the rules as a defect history, and
   the curated-list-that-checks-itself pattern.
5. `tools/role_tempo.py:1-107` — the taxonomy spine the three role/tempo tools
   are thin over, including what it deliberately does not measure.
6. `tools/canon_role_tempo.py:1-55` — structural-not-textual extraction, and
   which of its three outputs is committed versus gitignored.
