# S17 — joined ledger proposal

> **This document decides nothing.** It proposes a **column set** and reconciles
> five family censuses and one merged tool against each other. Every "rights
> tier" is a **category read off an existing declaration**, never a rights
> verdict. Every schema recommendation is `PROPOSED` — technical, not a scope
> call. It mints no id, edits no family file, and changes no tool.

**Date:** 2026-08-27. Re-run of the output deferred by the 2026-08-26 usage
limit (`review/dispatch3/BLOCKERS.md` §3 row 2, which required row 1 — the
companions family — to be run first; it now exists).

**Inputs, read and not edited:**

| input | what it contributes |
|---|---|
| `review/dispatch3/s17-art/baseline-run-2026-08-26.txt` | the only live tool numbers anyone may quote for cards (`art_coverage.py` exit 0, `art_lint.py` exit 0, at `main 223a4ff`) |
| `s17-klee.md` (597 lines) | Klee family census; the `source_key` proposal |
| `s17-furina.md` (576) | Furina family census; the card/non-card split argument |
| `s17-kokomi.md` (478) | Kokomi family census; the provenance-gap finding |
| `s17-icons-ui-models-vfx.md` (713) | everything non-card and non-companion; the gate-scope table |
| `s17-companions.md` (this re-run) | the companions family |
| `tools/art_ledger.py` + `review/dispatch3/tooling-laneb-handoff.md` | lane B's **merged** machine-readable ledger (`art-ledger-v1`), 16 emitted columns |

**Standing correction carried into every section:** `art/candidates/` was
re-materialised on 2026-08-27 (297 directories) and **all 27 contact sheets
resolve again**. `BLOCKERS.md` §1.1 ("25 of 27 sheets are dead, the R212(1) veto
route is closed") is **CLOSED**. Where a family file's review-state column says
a sheet cannot be walked, read it as walkable today.

---

## 1. The one thing to settle before any column: what a "row" is

All five family files agree in substance and disagree in denominator, which is
why their totals cannot be added. Lane B already resolved this and its answer is
the right one; restating it because the joined view depends on it:

> **A row is one *expected visual surface* — something the shipped mod will try
> to load at runtime — and expectations are DERIVED, never listed.**
> (`tooling-laneb-handoff.md` §1.)

Two consequences the family files hit independently:

- **`art_coverage.py`'s 294 is a card number and always was.** Every family file
  says so in its own words. The repo-wide "24 missing" is a card bill; the
  non-card bill is separate and larger in *kinds* if not in count.
- **A surface with no path written anywhere is invisible to every string-reading
  instrument, including lane B's.** Kokomi found it as missing `SOURCES.tsv`
  rows; Klee found it as an unwritten provenance hole; the icons family found it
  as three unregistered generators; companions found it as **five powers with no
  path, no plan row and no source at all** (`s17-companions.md` §3d). Four
  families, one shape.

---

## 2. PROPOSED column set — 25 columns, with the reason for each

Lane B's `Row` dataclass (`tools/art_ledger.py:320-337`) emits **16** of these
already. The table marks each column `HAS` (lane B emits it, keep the name),
`LACKS` (proposed addition), or `REDUNDANT` (something a family file asked for
that should **not** be added, with the reason).

### Identity — who is asking for this surface

| # | column | state | reason |
|---|---|---|---|
| 1 | `surface_id` | **HAS** | one stable key across cards and non-cards. `card:klee:kaboom`, `power:companions:metallicize`. Without it the five families cannot be joined at all. |
| 2 | `kind` | **HAS** | card / ui / power / relic / model / salon / summon / material / scene / vfx. The charter's acceptance line — "card art is not mistaken for total visual coverage" — is enforced by this column, not by prose. |
| 3 | `owner_family` | **HAS** (`owner`) | klee / furina / kokomi / companions / shared. It is what makes a batch have exactly one owner. Note it is **not** derivable from the packed path: seven companion badges pack under `res://klee/powers/` (`s17-companions.md` §3c). |
| 4 | `expected_by` | **HAS** | `file:line` of the thing that asks. This is the citation-discipline column: a row with no `expected_by` is an assertion, not a finding. |
| 5 | `expectation_class` | **LACKS** | **The most important proposed addition.** Three values: `declared` (a path literal exists), `computed` (a concatenated prefix — lane B `F5`), `undeclared` (the surface is *needed* and no path was ever written). Today lane B reports `power 58 expected / 51 covered / 0 missing / 7 defect`; the five iconless companion powers are not in the 58, because there is no string to find. Without this column the ledger's "0 missing" on powers reads as "nothing is owed", which is exactly the wrong reading. Populating `undeclared` needs a curated list — the "structurally invisible defect" house pattern — which is a build, not a report. |

### Source and provenance

| # | column | state | reason |
|---|---|---|---|
| 6 | `source` | **HAS** | the plate or generator. Lane B falls back to `plan.tsv` when `SOURCES.tsv` is silent (`art_ledger.py:666-680`), which is right — the source is known even when the URL is not. |
| 7 | `source_evidence` | **HAS** | `file:line` for the above. |
| 8 | `source_key` | **LACKS** | a normalised source identity joined across **all** registers, not just cards. `s17-klee.md` §8 proposes it and gives 12 instances; `art_lint`'s L1 enters `/cards/` rows only (`tools/art_lint.py:320-323`), so every card↔badge collision in the repo is *structurally invisible*. Companions add two more (`s17-companions.md` §6c). Whether any is a defect is taste; the column only makes them **reportable**. |
| 9 | `provenance_shape` | **LACKS** | **The concrete gap the companions family exposes.** `art_fetch.py` writes a `SOURCES.tsv` row keyed on `art/candidates/<id>/r<n>.png` for a `shortlist` pick and on the rendered out-path for an `auto` pick (`tools/art_fetch.py:183-216`). `art_ledger._rights_for` (`:655-664`) looks up **the rendered out-path only**. Arithmetic proof: `SOURCES.tsv` holds exactly 24 rows under `ImageGen/images/cards`, and lane B's rights block reports exactly `card 24/24` private-placeholder and `card 246/270` unclassified. So **every shortlist-provenanced card in the repo — including all 46 shortlist companion cards, which do have tier-`F` rows — reads `unclassified`.** Values: `out-path` / `candidate:r<n>` / `generator` / `derived` / `none`. |
| 10 | `source_group` | **LACKS** | `plan.tsv` column 13 (`art_fetch.py:66-74`). It is the field that decides whether shared-source siblings are legal (L7) or a violation (L1) — and it was **invented for companions**. Three families now carry a group (`companions` per-Genshin-character, `furina_pool`, `kokomi_pool`) under three different unwritten regimes; surfacing the column is what makes that visible without re-litigating it. |
| 11 | `register` | **LACKS** | `plan.tsv` column 12: `tcg` / `splash` / `icon` / `sticker` / `item` / `vfx`. `art_lint` already uses it for class-appropriateness. It is also the cheapest explanation of a family's crop grammar — companions are 22 `tcg` + 27 `splash` + 2 hand-set. |
| 12 | `crop` | **LACKS** | `mode@focus` as one string. It is the field that distinguishes a legal L7 sibling from an illegal one, and it is what a reviewer actually needs beside a shared source. |

### Rendered output and shipping

| # | column | state | reason |
|---|---|---|---|
| 13 | `rendered_output` | **HAS** | repo-relative `ImageGen/` path. |
| 14 | `rendered_present` | **HAS** | `is_file()`. Lane B's debt `D2` is honest: a 0-byte PNG counts as covered. See `REDUNDANT` below. |
| 15 | `packed_path` | **HAS** | `res://…` or `images/cards/<id>.png`. |
| 16 | `packed_present` | **HAS** | from the pck contract. |
| 17 | `ship_route` | **LACKS** | two values, `loose-png` and `pck`, and they are *completely different mechanisms* with no shared tooling — `s17-icons-ui-models-vfx.md` §1 makes this its headline, and every family file re-derives it. It is one column and it saves every future reader that derivation. |
| 18 | `fallback` | **HAS** | `none` / `active:<from>` / `unintended:<from>`. Lane B's three-shape discrimination is the strongest single thing in the tool and should not be touched. |

### Rights — categories only, never summed

| # | column | state | reason |
|---|---|---|---|
| 19 | `rights_tier` | **HAS** | one of `private-placeholder` / `public-safe` / `unclassified`. |
| 20 | `rights_evidence` | **HAS** | the declaration it was read from, or "no declaration found". |
| 21 | `rights_derivation` | **LACKS** | **The five family files do not agree on where a derived asset goes, and the disagreement is invisible without this column.** `s17-klee.md` §2 puts `char_icon_outline` and `select_portrait_locked` in **private-placeholder** ("derived from a tier-F file"); `s17-icons-ui-models-vfx.md` §7 puts the same two files in **UNKNOWN** ("the derivation is ours but the pixels are not"). Both readings are defensible and neither is a verdict. A `rights_derivation` column (`original` / `derived-from:<surface_id>` / `procedural`) records the *fact* and lets [USER] decide which category the fact implies — instead of forcing a category and hiding the choice. Lane B already has the machinery: its `RIGHTS-INHERITANCE` check knows which generator reads which input. |

### Review

| # | column | state | reason |
|---|---|---|---|
| 22 | `review_state` | **HAS** | lane B populates it from `art_lint`'s curated registries (`art_ledger.py:642-653`) — undersize, banned-family, identical, red-pen. That is the *lint* half of review state. |
| 23 | `review_route` | **LACKS** | the *human* half, and the one R212(1) turns on. Three facts decide whether a pick can move: is there a **contact sheet** for this id, does it **resolve** on disk, and is there a **rank 1** to apply? `EB-65` stops precisely because the third is false (`BLOCKERS.md` §1.3), and the whole dispatch stopped on the second until this morning. Values: `no-sheet` / `sheet-broken` / `sheet-walkable` × `rank1` / `no-rank1` / `applied`. **This is the column that would have made `BLOCKERS.md` §1.1 a one-line report instead of a three-agent rediscovery.** |

### Status

| # | column | state | reason |
|---|---|---|---|
| 24 | `status` | **HAS** | covered / missing / fallback / defect. |
| 25 | `notes` | **HAS** | free list. The place a `[known]` stale reason or an allowlist rationale lands without becoming a category. |

### REDUNDANT — proposed by a family file, and should **not** be added

| candidate column | why not |
|---|---|
| `dimensions` / `mode` / `decodable` | `art_lint` already measures these and lane B deliberately did not duplicate them (`tooling-laneb-handoff.md` D2). Two tools measuring one thing is how the `art_coverage`-vs-prose defect happened in the first place (`tools/art_coverage.py:15-38`). Fix `D2` by having `art_lint` be the authority, not by copying it. |
| `family` (separate from `owner`) | duplicates column 3. |
| a **summed** rights total | actively harmful. Both lane B and every family file already refuse to sum private-placeholder with public-safe, for the stated reason: a build 100% covered by private placeholders is 0% ready to ship publicly. |
| `nation` (mondstadt/fontaine/inazuma) | interesting only for companions, and derivable from the sheet file the row came from. Not worth a roster-wide column. |
| `rarity` | tempting — the Furina source rule is rarity-scoped — but rarity is a *sheet* fact and belongs to the sheet. If the source rule ever needs it, join it; do not copy it. |

**16 of 25 already emitted. 9 proposed additions. 5 explicitly declined.**

---

## 3. Reconciled totals

### 3a. Cards — the one surface where a live tool is authoritative

Every number in this table is the baseline's or is arithmetic on the baseline.
The five family files agree with it and with each other.

| owner family | expected | covered | missing |
|---|---:|---:|---:|
| Klee (personal sheet) | 79 | 76 | 3 |
| Furina (personal sheet) | 84 | 81 | 3 |
| Furina (token) | 1 | 1 | 0 |
| Kokomi (personal sheet) | 76 | 61 | **15** |
| **Companions (Inazuma / Mondstadt / Fontaine)** | **51** | **51** | **0** |
| Shipped in C# with no sheet row | 3 | 0 | 3 |
| **TOTAL** | **294** | **270** | **24** |

`baseline-run-2026-08-26.txt:98-100`. Lane B's ledger reports the same three
numbers and pins the two id sets equal by test
(`test_card_universe_matches_art_coverage_on_this_repo`), so the two instruments
cannot silently diverge.

**Kokomi is 15 of the 24 and companions are 0 of the 24.** Companions are the
only family with a complete card bill.

### 3b. Non-card — the totals that must NOT be added

| source | non-card denominator | why it differs |
|---|---|---|
| lane B `art_ledger.py` | **131** (425 total − 294 card) | counts surfaces with a **declared path**: power 58, ui 24, scene 21, model 12, relic 3, salon 6, material 3, summon 1, vfx 3 |
| `s17-furina.md` §1 | 58 expected / 45 present / 13 absent, **Furina only** | includes 5 energy-orb layers that *no scene asks for* — a bill against a scene that does not exist |
| `s17-kokomi.md` §1 | 24 further surfaces, **Kokomi only** | includes 6 build-authored `.tscn`/`.tres` that are written as text at pack time |
| `s17-icons-ui-models-vfx.md` §10 | 113 non-card **outputs** | counts files on disk, not expectations |
| `s17-companions.md` §2 | 7 badges present + **5 with no declared path at all** | the 5 are in **nobody's** denominator, including lane B's |

**PROPOSED (technical):** publish one non-card total, lane B's, and treat the
family numbers as *views* of it rather than as rival totals. The `kind` and
`expectation_class` columns are what make that possible: the Furina orb layers
become `kind=ui, expectation_class=undeclared`, the Kokomi authored resources
`kind=scene`, and the five companion powers `kind=power,
expectation_class=undeclared` instead of vanishing.

**What this does NOT establish:** it does not establish that 131 is the right
non-card number. It establishes that it is the only one derived from a single
stated rule, and that the four family numbers measure four different things.

### 3c. Rights — three categories, never summed

Lane B's run at primary `c09b6b6` (`tooling-laneb-handoff.md` §3):

| category | covered / expected |
|---|---|
| `private-placeholder` | 90 / 90 |
| `public-safe` | 5 / 5 |
| `unclassified` | 297 / 330 |

**This split is understated on the private side and overstated on the
unclassified side, and column 9 is the whole reason.** `_rights_for` reads
out-path-keyed `SOURCES.tsv` rows only, so:

| family | what the family census found | what lane B reports |
|---|---|---|
| **companions** | **58 of 58 private-placeholder, 0 public-safe, 0 UNKNOWN** — every one of the 51 card ids and 7 badges carries a tier-`F` row (46 via `art/candidates/<id>/r1-3.png`, 5 via out-path) | 5 classified, **46 unclassified** |
| Klee | all 76 cards + 29 badges + relic + UI + model private-placeholder; **1** public-safe (`ui/transition_wipe.png`); 0 UNKNOWN | most cards unclassified |
| Furina | all 83 outputs joined to a rank-1 plan row, "zero provenance holes"; 3 salon glyphs public-safe (Tier O declared) | ″ |
| Kokomi | 99 of 100 private-placeholder, 1 public-safe, **22 asset ids with no `SOURCES.tsv` row at any rank** | ″ |
| icons/UI/models/VFX | **37 of 113 non-card outputs have no `SOURCES.tsv` row** (three kinds; only the third is a live gap) | ″ |

**Reconciled reading, stated carefully:**

- **`public-safe` is small and the families agree on which files they are:**
  the three transition wipes, the three Furina salon glyphs, and the EB-88 orb
  candidate layers — all procedural, all declaring Tier O in their generator's
  docstring. **No companion asset is public-safe.** Every other rendered pixel
  in the repo is Tier F.
- **`UNKNOWN` / `unclassified` is not one thing.** Fixing column 9 moves the 46
  companion cards (and the equivalent shortlist rows in the other three
  families) out of it immediately, because the evidence exists and is simply
  keyed elsewhere. What remains after that fix is the genuine `EB-163`
  population: the 22 Kokomi ids and the icons family's 37, which have **no row
  at any key**.
- **The two figures cannot be summed with `private-placeholder`** and this file
  does not sum them.
- **`art/SOURCES.tsv` has exactly one distinct value in its tier column: `F`.**
  Measured independently by the Klee and icons families over all 872 rows. So
  every `private-placeholder` category in S17 traces to one column with one
  value, and `public-safe` traces only to generator docstrings.

**No rights verdict is offered or implied anywhere in this document.** The
category is a transcription. Whether any Tier F asset may ship, and whether the
Tier O generators' output is genuinely clear, are [USER]'s and are not asked
here.

---

## 4. Every collision and duplicate, across all five families

Four questions, kept apart because the answers differ.

### 4a. Byte-identical rendered files

| pair | families | state |
|---|---|---|
| `kaboom` ≡ `spark_knight_style` | Klee / Klee | allowlisted `L12 KNOWN IDENTICAL` (`baseline-run-2026-08-26.txt:83`) |
| `catalytic_conversion` ≡ `spark_collection` | Klee / Klee | allowlisted `L12` (`:82`) |
| `crowd_work` ≡ `standing_ovation` | Furina / Furina | allowlisted `L12` (`:81`) |

**Cross-family byte-identical files: ZERO.** Independently established from both
sides — `s17-klee.md` §8 hashed the Klee family against all others,
`s17-kokomi.md` §5a hashed Kokomi's 79 outputs, `s17-companions.md` §6a hashed
all 51 companion cards. **This is the NON-FINDING that matters most for lane C**:
the unintended-cross-character-fallback risk it is chartered to detect **does not
currently exist in the source tree**.

### 4b. One file serving two ids — sanctioned, three times, one pattern

| file | ids | family |
|---|---|---|
| `klee/relics/pounding_surprise.png` | `PoundingSurprise` + `ExplosiveFrags` | Klee |
| `furina/relics/ethereal_spotlight.png` | `EtherealSpotlightRelic` + `CurtainNeverFalls` | Furina |
| `kokomi/relics/pearl_of_wisdom.png` | `PearlOfWisdom` + `PearlOfInsight` | Kokomi |

An upgraded starter wears its base relic's icon
(`s17-icons-ui-models-vfx.md` §3). Only the Klee instance is filed —
**`EB-162`** (`docs/current/BACKLOG.md:117`) — because `Dodoco Tales` and
`Pounding Surprise` are two *different* relics rather than a base/upgrade pair.
**Companions have no relic and are not in this table.**

Also: `klee/powers/bomb.png` is a status badge *and* Klee's Burst-gauge cap
icon; `kokomi/powers/bake_kurage.png` and `kokomi/summon/bake_kurage.png` are
**two different files on purpose** (`KleePowerIcons.cs:120-124`). Both are
deliberate and flagged in code.

### 4c. Effective-pick source collisions **across families** — exactly ONE

| source | ids | families | seen by a gate? |
|---|---|---|---|
| `Element Hydro.svg` | `power_aura_hydro` (`art/plan.tsv:229`, out-path `ImageGen/images/powers/`) and `furina_energy_icon_large` / `furina_energy_icon_small` (`:681-682`) | shared/Klee ↔ Furina | **no** — no `/cards/` row is involved, so L1 never looks |

Nothing else crosses a family at rank 1. `Element Pyro.svg` is the same shape
one family in (`power_aura_pyro` + Klee's two energy icons, `:228`, `:278-279`).
Both are element-sigil vocabulary and both are almost certainly deliberate;
recorded because **no instrument can see either one**.

**Companions cross nothing.** All 51 rank-1 sources are distinct, and no source
a companion row uses at *any* rank is used by any non-companion row at any rank
(`s17-companions.md` §6b).

### 4d. Within-family shared sources — the long tail, by family

| family | count | shape | live today? |
|---|---:|---|---|
| Klee | 12 groups (`s17-klee.md` §8) | card ↔ badge / UI / model, one motif each | all effective; none flagged; L1 blind to all 12 |
| Furina | 10 groups C1–C10 (`s17-furina.md` §8) | 1 pixel-identical pair (allowlisted), 1 latent sigil collision **already on [USER]'s plate** (`QUEUE.md:53` pick 1), 4 card↔card different-crop, 4 cross-register | one latent |
| Kokomi | 5 groups (`s17-kokomi.md` §5b) + the `kokomi_pool` concentration | card ↔ icon; L1 out of scope for the icon rows | all effective |
| icons/UI/models/VFX | 4 within-family + 19 card↔non-card (`s17-icons-ui-models-vfx.md` §9) | includes the **new** `Namecard BG …The Deep` backdrop-vs-badge pair from the EB-67 run | one new |
| **companions** | **29 groups** (`s17-companions.md` §6c) | **27 are a Genshin character's own plate shared between that character's own cards at r2/r3** — the `source_group` mechanism working exactly as designed and documented (`tools/art_fetch.py:66-74`); **2 cross-register and both latent** (`Durin.png`/`Durin Item.png` with ranks swapped between card and badge; `Nicole Icon.png` at card r3 and badge r1) | **zero effective** |

**Roster total: 80 shared-source groups touch S17's five families; exactly one
crosses a family boundary; exactly three produce byte-identical files and all
three are allowlisted; and the collisions that could bite are all latent, all
sit on an r2/r3, and three of them are already registered or on [USER]'s plate.**

The single structural fact behind the whole table: `art_lint`'s L1 and L7 enter
`/cards/` out-paths only (`tools/art_lint.py:320-323`, `:44-49`), and L12 hashes
`ImageGen/images/cards/**` only. **Every non-card and every cross-register
collision above is unchecked by any tool**, which is column 8's entire
justification.

---

## 5. What this document does **NOT** establish

It does not establish that any asset is good, on-model, or shippable — no image
was opened by this file or by any family file, and no eyes-on was taken. It does
not establish any rights verdict: every tier is a transcription of a declaration
that already exists in the repo, `unclassified` means "no declaration found"
rather than unsafe or safe, and the public/private call is [USER]'s. It does not
establish that the proposed 25 columns are the right 25 — they are proposed, and
9 of them are additions to a tool that is already merged and already passing 26
tests. It does not establish that any collision in §4 is a defect; it establishes
which ones are effective, which are latent, and which no instrument can see. It
does not establish that 131 is the correct non-card denominator, only that it is
the only one derived from a single stated rule. It does not price, schedule, or
rank anything — that is the batches file, and the batches file recommends
nothing either. It mints no id, and every finding lands on an existing row
(`EB-153`, `EB-162`, `EB-163`, `EB-65`, QUEUE Art debt, `M19`, `S4-G17`) or on a
numbered question.
