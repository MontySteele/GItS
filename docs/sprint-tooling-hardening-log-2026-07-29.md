# Tooling hardening sprint — 2026-07-29

> **Provenance note.** This sprint ran concurrently with the Kokomi instrument
> sprint in one working tree. Its file contents were swept into commit
> `4ee6881` ("The fanfare +1.0 was noise") by that sprint's broad `git add`
> before this one could commit its own; the code is identical either way, and
> this commit carries the narrative that belongs with it. Files owned by this
> sprint: `tools/{art_lint,card_distinctness_report,extract_base_game_pool,
> lint_strict_domination,lint_text_encoding,lint_unique_names,
> render_card_gallery}.py`, `tier05/exp_furina_strength.py` (S4 reporting
> only), and their tests.

Eight items from a read-only sweep of `tools/`, all one shape: **a check that
skipped its own inputs, or narrowed its own scope, and still printed the same
confident line as a full run.** The house rule this sprint enforces is already
written down — *a lint that skips its own inputs on error is worse than no
lint* — and every fix below is that rule applied to a place it had not been.

Nothing in `docs/*.yaml`, `klee-mod/`, or any shipped card changed. Item 7
surfaced seven real design findings and **none of them was fixed** — they are
enumerated below for red-pen.

Suite: **1466 passed, 0 failed** from repo root. This sprint added **28**
tests; the rest of the delta from the ~1412 baseline belongs to the concurrent
Kokomi instrument sprint, which owns `tier05/` metrics and was running in the
same tree. Nothing this sprint touched is shared with it.

---

## The pattern, stated once

Four of these eight were the *same* bug in four files:

```python
try:
    ...
except Exception:
    continue        # or: pass, or: print to stderr and continue
```

The failure mode is not that work is lost. It is that **the output shape is
identical to a successful run**, so the narrower scope is invisible at exactly
the moment it matters. A gate that gets greener the less it can read is worse
than no gate, because someone is relying on it.

The fixes divide into three dispositions, and picking the right one per site is
most of the work:

| disposition | when | example |
|---|---|---|
| **FINDING** | the input is present and unusable | item 1, corrupt image |
| **HARD FAIL** | continuing would narrow a *gate*'s scope | item 3, unreadable pool |
| **MARKER** | one bad row must not kill a whole report | items 5, 8 |

Silence stays correct in exactly one case: when absence is a fact about the
*machine* rather than about the *content* (no Pillow installed, gitignored file
not fetched yet). Every fix below keeps those and only those.

---

## Item 1 — `art_lint`: an unreadable source was the one source nothing checked

`tools/art_lint.py`. Both image rules — L8 (undersize) and the L6 clip warn —
did `except Exception: continue` around `Image.open`. So a truncated download,
a wiki HTML error page saved under a `.png` name, or a WEBP with no decoder in
this Pillow build passed **both** image checks in silence. The single input
neither rule could measure was the one input they reported nothing about.

**Fix.** New rule **L10** (`undecodable()`), called from `lint()` so every
importer gets it — including `art_process`, which is the thing that writes the
crops. The two documented skips are kept verbatim, because they are facts about
the machine and not about the pick:

* no Pillow → the plan must stay lintable without an image decoder;
* no raw file → the plan must stay lintable *before* a fetch.

"The file is here and it is not an image" is neither. The two rules now
`continue` with a comment pointing at L10 rather than at nothing.

**Red demonstration.** `test_l10_reports_a_source_it_cannot_decode` writes
`<html>404 Not Found</html>` into `art/raw/Bogus_Source.png` and asserts the
L10 line, then asserts it reaches `lint()` and not merely the helper.
`test_l10_stays_silent_on_the_two_documented_skips` pins the other direction.

Live plan: **L10 clean** over 272 effective picks.

---

## Item 2 — the three PENDING waiver sets could only grow

`PENDING_UNDERSIZE` (L8, 6 entries), `PENDING_BANNED_FAMILY` (L9, 1) and
`PENDING_RED_PEN` (L1, 1) are hand-maintained allowlists that print instead of
failing. Each carried a comment asking a future human to *"DELETE the entry so
the lint guards the resolution"*. `KNOWN_IDENTICAL` already had the real
version of that: a test that fails when the underlying defect is gone.

The request in a comment is the failure mode. A test that breaks is the fix.

**Fix.** Three staleness tests in `tier0/tests/test_art_lint_full_set.py`, all
one idiom and it is the only honest one: **empty the waiver set and re-run the
rule.** An entry that stops producing its finding with the suppression lifted is
guarding nothing.

* `test_pending_undersize_entries_are_still_undersize` — needs Pillow *and* the
  gitignored `art/raw`, so it carries a `needs_raw_images` skip with the reason
  on record. It refuses to pass vacuously: if no entry could be measured, that
  is an assertion failure, not a quiet green.
* `test_pending_banned_family_entries_still_hit_a_ban` — pure string work, runs
  wherever the plan does.
* `test_pending_red_pen_entries_are_still_colliding` — the precedent is in the
  set's own comment: `{kaboom, spark_knight_style}` was removed by hand in
  Sweep II D1 *because someone remembered*. This makes the next one mandatory.
* `test_the_staleness_idiom_detects_an_entry_that_stopped_firing` — the
  synthetic half, so the mechanism is pinned on a bare clone too.

**Stale entries removed: none.** All eight entries across the three sets still
fire, verified by running each rule with its waiver lifted. Also confirmed the
detector is not vacuous: injecting a bogus id into each set reports it stale.

---

## Item 3 — an unparseable pool turned its own breaches into a passing test

`tools/card_distinctness_report.py:435`. `build_reports()` printed
`!! <pool>: unreadable (...)` to stderr and `continue`d. Combined with
`test_distinctness_gate.test_no_new_gate_breaches` — which asserts over
*whatever pools `build_reports` happens to return* — a pool that stopped
parsing simply left the comparison, and its breaches became a **pass**.

Worse on this specific tool: `load_pool`'s own docstring already documents this
exact class from the other side ("the error goes to stderr and any run that
redirects stdout loses it entirely").

**Fix.** `raise RuntimeError` naming the pool, the path, the exception, and why
it refuses. Absence is untouched and still a legitimate no-op — the
`os.path.exists` check above it handles gitignored `game_ref` pools, which CI
genuinely does not have. **Present-but-unparseable** is the defect.

**Red demonstration.** `test_an_unreadable_pool_is_a_hard_failure` points
`cdr.SHEETS` at a broken YAML file and asserts the raise;
`test_a_pool_file_that_is_absent_is_still_a_no_op` pins the other half.

---

## Item 4 — the manifest recorded a verdict where the truth was "unknown"

`tools/extract_base_game_pool.py:528`. `_power_gap` wrapped
`from tier0.engine import refpowers` in `except Exception` and returned
`"{power} is not on the SUPPORTED_POWERS dial"` — a claim about the dial's
*contents*, made by code that had just failed to open the dial. The blocker
manifest then recorded an adjudicated verdict where the honest answer was
"unreachable". The two want opposite repairs: implement the power, versus fix
the import.

**Fix.** The import failure is its own string, carries the exception type and
message, and says the reason is UNKNOWN rather than adjudicated. The three real
categories (UNIMPLEMENTED, payload-needed, co-op-only, dial) are untouched.

**Red demonstration.** `test_an_unimportable_tier0_is_reported_as_such_not_as_a_
dial_verdict` patches `builtins.__import__` to raise for `tier0.engine`, which
is the only way to reach the branch in a repo where tier0 imports fine.
`test_a_real_dial_gap_still_reads_as_a_dial_gap` proves the separation lost
nothing.

---

## Item 5 — the review surface under-reported the thing it exists to show

`tools/render_card_gallery.py:215`. `except Exception: pass` wrapped the whole
upgrade-diff block, collapsing two facts into one identical blank:

* this card **has** no upgrade (basics, `_unexpressible` deltas, `UNAPPLIABLE`)
  — ordinary, correctly silent;
* rendering its upgrade **threw** — a defect, silently reported as the first.

The gallery's own docstring says it exists because design drift "is exactly the
class of defect no lint can see — it needs a human looking at the set as a set."
A surface built for that job may not quietly drop a line it failed to compute:
the reviewer reads the blank as a fact about the card.

**Fix.** Split the block. `KeyError` (no such card) and the specific
`ValueError("no applicable upgrade …")` stay silent; anything else renders an
explicit `upg-err` marker with the exception type and message, HTML-escaped. Not
a `raise`, on purpose — one malformed `+` entry must not take down a page whose
job is showing 300 good tiles to a human.

The `ValueError` split matters: `apply_upgrade` raises it for both "there is no
upgrade here" *and* "this delta is malformed" (`innate delta on 'x' must be
true`). Only the sentinel message is a non-event.

**Red demonstration.** `tier0/tests/test_card_gallery_reporting.py`, five tests:
a throwing `get_card`, a throwing effect-line render, the two silent-absence
cases, a malformed delta, and escaping of the exception text.

---

## Item 6 — the uniqueness lint could not see a mangled name

`tools/lint_unique_names.py:61` was `yaml.safe_load(open(path))` — no encoding,
no context manager, in violation of the repo's own ratified gate.

The sharp end: this lint's entire job is comparing display **names**, and a name
decoded through cp1252 is still perfectly unique. The defect would have landed
as a green run rather than as a failure. `Salon Debut`'s accented `e` is the
live case, and it is the same card that produced the original mojibake finding.

**Fix.** `with open(path, encoding="utf-8") as fh:`. Debt entry removed from
`test_encoding_gate.DEBT` (removed, not lowered to 0 — the staleness test forces
the deletion, and a zero entry is an allowance for the next offence).

**Pinned both ways** in `test_the_unique_name_lint_declares_its_encoding`: the
structural half (no undeclared read in the file), because the behavioural half
only shows the bug on a cp1252 machine; and the behavioural half (an accented
name survives the read), because the structural one cannot prove the value came
back right.

### Item 6b, found on the way — 20 phantom debt entries, and a live allowance

`tools/lint_text_encoding.py` keyed its `open` arm on the **attribute name**, so
every `Image.open(...)` in the repo counted as an undeclared text read. There
were 20 of them across seven files, all carried on `DEBT` as debt that could
only ever be "paid" by deleting the image pipeline.

That was not a cosmetic miscount. **The gate compares a per-file COUNT**, so
`"tools/art_lint.py": 2` was a standing allowance for two *real* bare `open()`
calls to hide behind — in the file this sprint was editing.

**Fix.** A narrow `BINARY_OPEN_RECEIVERS = {"Image", "ImageFile"}` exemption, and
the exemption is deliberately *not* "attribute-form open is exempt":
`io.open`, `codecs.open` and `gzip.open` all take `encoding=` and stay in scope.
`test_image_open_is_not_a_text_read` asserts exactly that boundary on a synthetic
file. `test_the_exemption_did_not_swallow_the_real_offences_in_those_files`
proves the four files that left the list have genuinely nothing left rather than
having merely gone quiet.

Recount: `art_process` 8→3, `cut_combat_layers` 3→2, `cut_salon_members` 2→1;
`art_lint` (2), `gen_furina_stills` (2), `gen_kokomi_stills` (2) and
`archive/autocrop_card_art` (1) left the list entirely.

---

## Item 7 — the cross-sheet strict-domination sweep

The gap: `tools/lint_strict_domination.py` compared cards only against
**siblings in the same file**, and the sheets are split by author and by nation
rather than by what competes. The gate's scope was a filesystem accident.

The precedent is on the record — `docs/fontaine-rares-banner-sprint-log.md`
item 2: the Clorinde/Raiden dominating pair "was flagged **BY HAND** because no
lint could see it."

### How comparability was decided

The within-sheet rules are applied **unchanged** cross-sheet: identical
`(cost, type, encore_cost, fanfare_cost, exhaust, tags)` group tuple, different
rarity, non-basic, benefits-superset-with-all-≥ **and** costs-subset-with-all-≤,
adjacent-rarity narrowing (R26), formula amounts incomparable. The
disposition logic is now a shared `_verdict()` so the two passes cannot drift.

The cross pass adds exactly **one** new question — *can these two cards be
drafted in one run?* — because the law protects draft decisions, and two cards
that never meet on a reward screen are not a decision. Read off the pool
assembly, not asserted:

| pair | co-draftable | why |
|---|---|---|
| companions × companions | **yes** | `rewards.companion_pool()` is every non-guest companion of *every* nation; `nation` only weights the roll in `_nation_weighted_choice` |
| personal × companions | **yes** | both fill the same reward screen |
| personal × personal | **no** | `rewards.character_pool()` requires `c.character == character_id`; Klee's cards and Kokomi's never co-occur |

One row filter was added to **both** passes (`draftable()`): `kit_card` (Bursts
— `character_pool` skips them, "kit, not loot") and `guest_star` (Furina's
generated cameos — `companion_pool` skips them, and the only door in serves
them at *exactly* its own rarity, so a rule about what rarity **buys** has
nothing to say about them). Verified not to be a scope reduction in disguise:
with both filters on, the within-sheet sweep reports exactly what it reported
before (the same three R26 informational notes, zero findings).

### The reporting defect

The old summary was `CLEAN: <sheet names>` — a verdict with no denominator. It
read as "these sheets are clean" when it meant "the subset of rows I compared
had no findings", and it had silently dropped basics, rows with no `effects`,
non-draftable rows and formula amounts.

Now every run prints a scope block first, and the verdict carries its own count:

```
scope (rows this sweep has NO opinion about are itemised):
  fontaine-companions.yaml      16/19  compared  (skipped: 0 no-effects, 0 basic, 3 non-draftable, 0 formula)
  furina-cards.yaml             76/82  compared  (skipped: 0 no-effects, 5 basic, 1 non-draftable, 0 formula)
  inazuma-companions.yaml       15/15  compared  (skipped: 0 no-effects, 0 basic, 0 non-draftable, 0 formula)
  klee-cards.yaml               70/76  compared  (skipped: 0 no-effects, 4 basic, 1 non-draftable, 1 formula)
  kokomi-cards.yaml             55/61  compared  (skipped: 0 no-effects, 5 basic, 1 non-draftable, 0 formula)
  mondstadt-companions.yaml     17/17  compared  (skipped: 0 no-effects, 0 basic, 0 non-draftable, 0 formula)
  CROSS-SHEET                 249 cards over 12 co-draftable sheet pair(s) of 6 sheets
CLEAN over 249 compared card(s) in 6 sheet(s)
```

Two further reporting rules:

* a run that compared **zero** cards prints `VACUOUS` and exits 1. A sheet of
  nothing but basics used to produce the identical `CLEAN` line as a full sweep.
* `--within-only` prints `CROSS-SHEET  NOT RUN (--within-only): a domination
  spanning two sheets is UNCHECKED`. A narrower run is fine; a narrower run that
  reads like a full one is not.

### CI stays green without hiding anything

The cross pass surfaced seven pre-existing pairs the moment it was switched on.
Editing a printed card needs red-pen, so they are enumerated in
`CROSS_KNOWN` — the same pattern, for the same reason, as
`test_distinctness_gate.KNOWN_FAILING` and `art_lint`'s PENDING sets. Notes, not
findings; exit stays 0; a **new** cross-sheet domination fails immediately.

Guarded by two tests: `test_the_cross_sheet_allowlist_is_not_stale` (lift the
allowlist, re-run, any entry that no longer dominates must be deleted) and
`test_the_cross_sheet_allowlist_is_not_a_blanket` (each entry names two ids
that are real comparable cards on a real sheet).

---

## 🔴 CROSS-SHEET DOMINATION FINDINGS — FOR [USER] RED-PEN

**Seven pairs. No card was changed.** All are pre-existing; all are notes in
`CROSS_KNOWN` today. Each needs a ruling, and the last four need *one* ruling
between them.

### 1. THE HEADLINE — a shared Uncommon beats a personal Rare

```
mondstadt-companions.yaml : sucrose_catalyst_conversion  (uncommon)
    strictly dominates
kokomi-cards.yaml         : moonlit_offering             (rare)
```

Both **0 cost, skill, self-Exhaust**.

| | benefits | costs |
|---|---|---|
| `sucrose_catalyst_conversion` (uncommon) | energy 1, draw 1 | — |
| `moonlit_offering` (**rare**) | energy 1, draw 1 | **discard 1** |

Identical benefits, and the **Rare pays a cost the Uncommon does not**. This is
exactly the Clorinde/Raiden shape, and it is worse in one respect: Sucrose is in
the *shared* pool, so she is drawable by every character including Kokomi, in
the same run, from the same reward screens.

Context worth having in front of the ruling: `moonlit_offering` is a **recent
deliberate design object** — G8 merged `swift_currents` into it precisely to
avoid printing two near-duplicates, and R79's carve-out template is "Rare AND
self-Exhaust". Sucrose is marked `v1.11a, PROPOSED: the neutral-energy FIXER the
shared pool owed every character (§4.7 audit)`. So this is two live design
decisions colliding across two sheets, which is precisely what nothing could see.
It looks like a Sucrose question rather than a Kokomi one, but that is a call,
not a finding.

### 2. `communion_of_tides` (uncommon) > `lynette_box_trick` (common)

```
kokomi-cards.yaml         : communion_of_tides  (uncommon)  1 cost skill
fontaine-companions.yaml  : lynette_box_trick   (common)    1 cost skill
```

`communion_of_tides` = `exhaust_from 1 (chosen)` + `draw 2`.
`lynette_box_trick` = `draw 2`, nothing else. The Uncommon is the Common plus a
free Exhaust trigger, at the same cost.

Worth noting the Common's own comment defends its plainness — *"Pure velocity
glue. Plain by design: the pool's honest draw common; every archetype takes it,
none warps around it."* If "plain by design" is the ruling, this pair may be an
accepted domination rather than a defect, in which case the right home for it is
`KNOWN` with a reason rather than a fix.

### 3. `sayu_naptime` (uncommon) > `moon_signal` (common)

```
inazuma-companions.yaml : sayu_naptime  (uncommon)  0 cost skill
kokomi-cards.yaml       : moon_signal   (common)    0 cost skill
```

`sayu_naptime` = `block 3` + `draw 1`. `moon_signal` = `discard 1` + `draw 1`.
The Common **pays a cost** (a random discard) and gains strictly less. Same
cross-pool asymmetry as finding 1: a shared Uncommon over a personal Common.

### 4–7. THE ELEMENT CLUSTER — one ruling, four pairs

```
inazuma-companions.yaml : shinobu_thundergrust (uncommon) 1 cost attack, 7 dmg, applies electro
    strictly dominates all four of:
mondstadt-companions.yaml : dahlia_sacramental_shower (common) 6 dmg, hydro
mondstadt-companions.yaml : fischl_nightrider         (common) 5 dmg, electro
mondstadt-companions.yaml : kaeya_frostgnaw           (common) 6 dmg, cryo
fontaine-companions.yaml  : freminet_pers_deploy      (common) 6 dmg, cryo
```

**This is one design question, and it is a question about the LINT as much as
about the cards.** All five are the same card — a 1-cost applier attack — at
different elements and different damage. The lint cannot see the element: the
effect vocabulary carries only `applies_element: true`, and `element` is a
separate card field that is not in the comparison group.

The ruling needed: **is `element` a comparability dimension?** The case for yes
is strong — a cryo applier and an electro applier enable different reactions, so
arguably they never compete for one deck slot, and the whole Fontaine set is
built on exactly that premise ("No Fontaine Electro exists; Furina's
Electro-Charged scarcity is BY CONSTRUCTION"). The case for no is that four
Commons at 5–6 damage next to one Uncommon at 7 is still a rarity ladder
statement.

Deliberately **not** pre-decided by a code change. Adding `element` to
`comparison_group()` would have made these four disappear, and it would have
changed the within-sheet lint's scope at the same time — a scope reduction
wearing a bug-fix's clothes. If the ruling is "yes, element is a dimension", the
one-line change is in `comparison_group()` and these four entries come out of
`CROSS_KNOWN` on their own.

### Informational, not a finding (R26 two-step rarity gap)

```
inazuma-companions.yaml : itto_superlative_superstrength (rare)
    dominates
fontaine-companions.yaml : freminet_pressurized_floe     (common)   2 cost
```
A rare obsoleting a common's slot is the rarity ladder working. Printed as
informational by the same R26 rule the within-sheet pass uses. No action.

### Observed and EXCLUDED, recorded so nothing is hidden

Three more pairs appeared in the prototype sweep and are excluded by
`draftable()` because the dominated card is a **Guest Star** (generated cameo,
never on a reward screen, and its generator serves it at exactly its own
rarity):

* `dahlia_favonian_favor` (uncommon) > `guest_neuvillette_droplets` (common)
* `barbara_shining_idol` (uncommon) > `guest_neuvillette_droplets` (common)
* `shinobu_thundergrust` (uncommon) > `guest_neuvillette_tears` (common)

If [USER] disagrees that generation-only cards are outside the rarity ladder,
deleting the `guest_star` clause in `draftable()` brings all three back.

---

## Item 8 — a comparison table computed over survivors

`tier05/exp_furina_strength.py:771`, cell **S4** — the roster calibration,
whose entire output is the sentence "Furina is N times the reference Ironclad".
A failing arm printed `SKIPPED` *above* the table and then dropped out of
`rows`, so the table a reader quotes was computed over the survivors with
nothing in it saying so.

The worst case is specific and silent: lose `ref_ironclad` and `ref` is `None`,
every `vs ref_IC` cell becomes `--`, and the winrate column still reads like a
finished measurement.

**Fix.** A missing arm keeps its **row** in the table, marked `MISSING` with
`<- ARM FAILED: <type>: <message>`, and a footer states how many of how many
arms are gone and that the ratio column is meaningless if `ref_ironclad` is one
of them.

**Red demonstration.** `tier0/tests/test_exp_strength_missing_arm.py` — five
tests, `model.run_many` replaced wholesale so **no sims run**: the marked row,
the footer count, the lost-reference case, a fully green run printing no marker
at all, and a guard that the arm list itself was not quietly shrunk by a change
that was supposed to be about formatting.

---

## Evidence summary

| item | file | red demonstration |
|---|---|---|
| 1 | `tools/art_lint.py` | `test_l10_reports_a_source_it_cannot_decode` + silent-skip twin |
| 2 | `tools/art_lint.py` | 3 staleness tests + synthetic idiom test |
| 3 | `tools/card_distinctness_report.py` | `test_an_unreadable_pool_is_a_hard_failure` + absence twin |
| 4 | `tools/extract_base_game_pool.py` | `test_an_unimportable_tier0_is_reported_as_such…` + dial twin |
| 5 | `tools/render_card_gallery.py` | `tier0/tests/test_card_gallery_reporting.py` (5) |
| 6 | `tools/lint_unique_names.py` | `test_the_unique_name_lint_declares_its_encoding` |
| 6b | `tools/lint_text_encoding.py` | `test_image_open_is_not_a_text_read` + no-swallow twin |
| 7 | `tools/lint_strict_domination.py` | `test_the_cross_sheet_sweep_catches_the_clorinde_raiden_shape` + 6 more |
| 8 | `tier05/exp_furina_strength.py` | `tier0/tests/test_exp_strength_missing_arm.py` (5) |

Every lint fix is exercised in **both** directions, because a rule only ever
seen passing is not a gate.

---

## Still owed

1. **The seven cross-sheet findings need rulings.** Nothing above is a fix;
   they are notes in `CROSS_KNOWN` and the staleness test will force each entry
   out the day its pair stops dominating. The element cluster (4–7) is one
   ruling for four pairs, and it decides a lint rule rather than a card.
2. **Is `element` a comparability dimension?** See findings 4–7. If yes, the
   change is one line in `comparison_group()` — but it changes the *within*-sheet
   sweep's scope too, so it needs red-pen rather than a commit.
3. **Are generation-only cards inside the rarity ladder?** The `guest_star`
   clause in `draftable()` assumes not, and three excluded pairs hang on it.
4. **`Pillow` is now installed on this dev box**, which switched on L6/L8/L10
   against the real `art/raw` for the first time locally. CI already installs
   it (`.github/workflows/repo.yml`). Worth knowing that a machine *without* it
   runs a materially smaller art gate — the skip reasons say so, but nothing
   totals them.
5. **`extract_base_game_pool.py` still carries 7 encoding-debt entries** and
   `build_official_sheet.py` 10. Those are real, unlike the 20 phantom ones this
   sprint removed, and they are unrelated to any item above.
6. **The `art_lint` L6 warn is noisy** — 27 lines on the current plan, all
   "cover trims 57–80% of the source height" on TCG-shaped portrait sources.
   The rule already excludes `tcg` for exactly this reason; the `splash`
   register may want the same treatment. Not touched: it is a WARN by design and
   changing what it points at is a taste call.
