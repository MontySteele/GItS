Status: RECORD

# Roster HP: Furina and Kokomi are HP-scalers — 2026-08-29

Branch `roster-hp-scalers`. Staged, not deployed, not re-baselined.

## 1. The ruling

[USER], verbatim:

> "I think we forgot that Furina and Kokomi are canonically HP-scalers, so it's
> weird to give them lower HP pools than the average of the canonical
> characters. Klee being low makes total sense, but Furina should probably be
> medium-high and Kokomi be high, relative to the base cast."

Ruling id is not minted here — it lands as part of the sitting slate for
2026-08-29. Every comment this branch writes says "sitting slate 2026-08-29"
rather than a number.

## 2. The base cast, with sources

These are the shipped Slay the Spire 2 characters, read out of the reference
layer this repo already keeps:

| character | starting HP | source |
|---|---|---|
| Ironclad | 80 | `game_ref/ironclad_char_facts.yaml:7`, `game_ref/char_real_ironclad.yaml:8` |
| Defect | 75 | `game_ref/defect_char_facts.yaml:20` |
| Regent | 75 | `game_ref/regent_char_facts.yaml:20` |
| Silent | 70 | `game_ref/silent_char_facts.yaml:28`, `game_ref/char_real_silent.yaml:8` |
| Necrobinder | 66 | `game_ref/necrobinder_char_facts.yaml:21` |

Median **75**. Mean **73.2**. Top **80**. Bottom **66**.

`game_ref/` is gitignored and absent on a fresh clone, so those line numbers
read against the local tree, not against HEAD.

Where our three sat before this change: Klee 62, Furina 60, Kokomi 70. All
three were at or below the cast's median, and two of them were below its
bottom. That is the thing [USER] caught.

## 3. The derivation (derived, not picked — R212)

The ruling gives three ordered constraints and no numbers:

1. Klee low — already true at 62, below Necrobinder's 66. Unchanged.
2. Kokomi **high** relative to the base cast. The cast's top is Ironclad's
   80, so "high" reads as the top of the range → **Kokomi 80**.
3. Furina **medium-high**, and by the sentence's own ordering below Kokomi.
   That puts her strictly between the median (75) and Kokomi (80) →
   **Furina 78**.

Error direction, stated once: both moves are **upward**, and both make the two
characters **more survivable**. If the derivation is wrong it is wrong in the
direction of the roster being slightly too forgiving, never too punishing —
which is the recoverable direction, because a starting-HP number is a pure
knob with no card text hanging off it.

Klee is untouched at 62, and stays the compatibility baseline.

## 4. Alternatives — a numbered pick for [USER]

Shipped on this branch is option **1**. The others are listed, not built.

| # | Furina | Kokomi | the reading it encodes |
|---|---|---|---|
| **1 (shipped)** | **78** | **80** | "High" = the cast's top; "medium-high" = above the median, below Kokomi. |
| 2 | 78 | 82 | Kokomi *above* the whole cast — she is the healer and the stability fantasy wants headroom past Ironclad's. |
| 3 | 75 | 80 | "Medium-high" read as exactly the median. Cheapest move; leaves Furina level with Defect/Regent. |
| 4 | 80 | 82 | Both above the median with Furina tied to Ironclad; widest departure from the pre-change roster. |
| 5 | 78 | 78 | Both medium-high, no separation between them — rejects the "Kokomi higher than Furina" half of the sentence. |

Changing the pick is two constants and two YAML lines; the expensive part is
the re-baseline in §7, and that cost is the same for every row.

## 5. Files changed

| file | change |
|---|---|
| `tier0/content/characters/furina.yaml` | `hp: 60` → `hp: 78`; R17's citation kept, this ruling appended |
| `tier0/content/characters/kokomi.yaml` | `hp: 70` → `hp: 80`; R52's citation kept, this ruling appended |
| `klee-mod/KleeCode/Furina.cs` | `StartingHp => 60` → `78`, with a doc comment mirroring the sheet |
| `klee-mod/KleeCode/Kokomi.cs` | `StartingHp => 70` → `80`, existing R52 rationale kept |
| `docs/current/characters/furina-kickoff-v0.1.md` | §2 gains an explicit **Starting HP: 78** line — the kickoff had never stated her HP at all |
| `docs/current/characters/kokomi-kickoff-v1.md` | §6 ask 8 statline constants: hp 70 → 80 |
| `docs/current/STATE.md` | roster table gains an HP column (62 / 78 / 80) plus a paragraph on the base-cast comparison and the R68 staleness |
| `tier0/tests/test_stability_band.py` | docstring said "Kokomi ... Klee (62)"; now names Kokomi's 80 |
| `tier05/tests/test_stability_trajectory.py` | docstring "Kokomi (70)" → "Kokomi (80)" |

**Test pins: there are none to update.** The sweep looked for `hp == 60`,
`hp == 70`, `StartingHp`, `max_hp` fixtures and every numeric literal near
`furina`/`kokomi` across `tier0/tests`, `tier05/tests` and `klee-mod`. Every
hit is one of three things and none is a pin on the sheet:

- **Arbitrary fixture HP.** `Player(hp=200, max_hp=200)`, `Player(hp=60,
  max_hp=60)` in `test_furina_fanfare_parity.py:136`,
  `Player(character_id="kokomi", hp=70, max_hp=70)` in
  `test_noncard_parity_vectors.py:154`. These are harness numbers chosen for
  arithmetic convenience; the assertions are all relative (`p.hp ==
  p.max_hp - 6`). Changing them would change nothing and lose the round
  numbers, so they stand.
- **Docstrings quoting the roster.** The two fixed above.
- **Captured observations.** `review/qa/kokomi-first-turn-example/*.json`
  records a live Kokomi at `62/70`. That is a published measurement record and
  is left exactly as captured (R101b) — it is evidence of what the game did on
  the day, not a statement about what the sheet says now.

No golden fixture needed regenerating; nothing had to be hand-edited inside
one.

## 6. What reads max HP, and what moves

Nothing in either character's card sheet reads max HP directly — `grep -i
"max_hp\|maxhp"` over `docs/kokomi-cards.yaml` returns nothing, and Furina's
sheet references it only through the Fanfare cap. What moves is engine
machinery that scales off the pool:

**Furina-specific**

- **Fanfare cap = `FANFARE_CAP_FRACTION` × maxHP** (0.5;
  `tier0/constants.py:166`, `tier0/engine/state.py:465-505`, mirrored in
  `klee-mod/KleeCode/Powers/FurinaResources.cs:376`). Her ceiling goes
  **30 → 39**, a 30% wider rail. LAW:195 calls this "a high safety rail, not
  a first-order dial" and nothing on her sheet carries `raise_fanfare_cap`, so
  no card text changes — but the four `fanfare_at_least_N` gates on her sheet
  (N = 12, 15, 20 in `docs/furina-cards.yaml`) now sit lower in the reachable
  range. **The sheet's own comment that `fanfare_at_least_12` "reads true on
  22.4% of ATTACK plays" is a measured rate and is now stale.** It is a
  comment, not a lint input, so nothing goes red; it wants a re-measure at the
  same time as the tables in §7.
  *Note:* `review/ruled/furina-e4-2026-08-29.md` §5 proposes retiring
  `FANFARE_CAP_FRACTION` and the whole cap/floor/decay machinery. That packet
  is **proposed and unratified** — the cap is live today. If E4 lands, this
  entire bullet stops applying and the HP change becomes invisible to Fanfare.
- **Salon overdraw drains true HP** (LAW:193, kickoff §5). This is a **flat**
  drain, so a bigger pool makes greed straightforwardly cheaper: the same
  overdraw costs 1.7 percentage points less of her bar at 78 than at 60. This
  is the largest real balance consequence of the change, and it is the reason
  the change is not free even though it touches no card.
- **Encore absorbs before HP** — unchanged; Encore is uncapped and does not
  read max HP.

**Kokomi-specific**

- Nothing. Her ward, Charge, Kurage queue and heals are all flat amounts; the
  grep for max-HP readers in her kit is empty. Her change is pure pool size,
  which is exactly what the stability band is denominated in.

**Roster-wide, and so hitting both**

Every one of these is a fraction of max HP, so all of them get larger in
absolute terms:

| reader | constant | Furina 60 → 78 | Kokomi 70 → 80 |
|---|---|---|---|
| rest-site heal (`REST_HEAL_FRACTION`) | 0.30 | 18 → 23 | 21 → 24 |
| rest policy threshold (`REST_HEAL_THRESHOLD`) | 0.65 | 39 → 50 | 45 → 52 |
| blood potion (`POTION_BLOOD_HEAL_FRACTION`) | 0.20 | 12 → 15 | 14 → 16 |
| fairy revive (`POTION_FAIRY_REVIVE_FRACTION`) | 0.30 | 18 → 23 | 21 → 24 |
| "big hit" potion trigger (`POTION_BIG_HIT_FRACTION`) | 0.35 | 21 → 27 | 24 → 28 |
| relic `hp_below` conditionals (`tier0/engine/relics.py:357`) | 0.5 default | 30 → 39 | 35 → 40 |
| stability / trajectory metrics (`run_metrics`) | — | denominator only: every reading is already a fraction of max HP, so bands stay comparable without rescaling |

The metrics row is the reassuring one: the stability and trajectory profiles
were built to divide by max HP precisely so a band declared for one character
reads against another, which is why no band constant needs re-ruling here.

## 7. What this invalidates (R68)

Levels are not comparable across world stamps, and starting HP is a
world-moving number. **Every measured table quoting a Furina or Kokomi row is
stale the moment this merges.** Named:

- **The standing twelve-arm baseline**,
  `review/records/sitting-reads-2026-08-26-c20-d18-p11.md` at `RT12/D18/P11/C20`
  — the six Furina and Kokomi arms (salon / spotlight / fanfare; priest /
  commander / assist), on **both** the winrate and act-1 columns. The four
  anchor arms (`ref_ironclad`, `real_ironclad`, `ref_silent`, `real_silent`)
  and the three Klee arms are **unaffected** — nothing about them moved — but
  the table as a whole cannot be quoted as a single read until it is re-run in
  one pass, which is the house rule that produced it in the first place.
- **The act-1 clear rates in the richness / sitting reads** —
  `review/records/sitting-reads-2026-08-08.md` (salon 54.33%; priest 42.20%,
  commander 51.83%, assist 35.37%) and the same three Kokomi rates quoted in
  `review/active/eb74-lever2-options-2026-08-13.md:119`. Act-1 clear is the
  most HP-sensitive column on the board, so these move most.
- **Furina's Fanfare-gate open rate** (the 22.4% comment in
  `docs/furina-cards.yaml`), per §6.
- **Kokomi's stability-band readings**, which are the acceptance instrument
  for her healer fantasy. They are fractions of max HP so they stay
  *comparable*, but the underlying runs were taken on a 70 HP body.

Published records are not rewritten. Under R101b they stand as published; this
packet is the disclosure that they no longer describe the live world.

**Cost of the re-baseline:** `review/ruled/eb81-furina-remedy-options-2026-08-12.md`
§4 measured `tier05.exp_roster_anchors` at 500 runs across ten arms as **41
seconds**, and extrapolated the published cell — 3000 runs, twelve arms — at
**roughly four to five minutes**. That packet's own conclusion applies here
too: *"The compute is not the cost."* The re-baseline is a stamp move, so its
timing is [USER]'s, not this branch's.

## 8. Merge timing

Merging this **moves the world stamp**. Two consequences worth stating before
anyone clicks the button:

- The twelve-arm table should be re-run in one pass **after** the merge, not
  before, and the re-run is what makes the new numbers quotable. Until then
  the roster's measured levels are disclosed-stale, not replaced.
- Because the C# side changes too, the mod package on disk is behind until the
  next deploy. Best landed **with** the next deploy rather than between
  deploys, so live play and the sheets agree on the same two numbers. That is
  [USER]'s call, not this branch's — nothing here was deployed, no game was
  launched, and no re-baseline was run.

## 9. Verification run on this branch

All green, final state of the branch:

- `python tools/lint_constant_parity.py` →
  `constant parity: OK (75 mirrored, 18 declared unmirrored, 2 ratified invariants held)`
- `python -m tools.run_lints --lane ci` → `OK: 28 lint(s) passed`
- `python -m pytest tier0/tests -q` →
  `3639 passed, 46 skipped, 12 xfailed, 3 warnings in 239.41s (0:03:59)`
- `python -m pytest tier05/tests -q` → `794 passed, 9 warnings in 37.61s`
- `dotnet build klee-mod/KleeCode/KleeCode.csproj -p:UsePinnedAssemblies=true`
  → `12 Warning(s)` / `0 Error(s)`

**One pre-existing red had to be cleared to push, in its own commit.** On the
first run, `prototype-authorship` and `prototype-codegen` were red and
`tier0/tests/test_prototype_authorship.py` failed twice — all of it the same
defect, and all of it confirmed red on `origin/main` (`48a2273`) with this
branch's changes stashed. `proto_kurages_oath_memory` had shipped without the
`authored_by:` field EB-190 requires; the row's comment block justified the
omission by saying the surface has no such field and `Card.from_dict` refuses
one, which is false — seventeen rows above it carry the field and load. The
follow-up commit adds `authored_by: [claude]` (the value the same comment
block's own words give: numbers and rule [USER], implementation and wording
Claude, nothing designed by the doctrine seat, nothing graded) and corrects the
comment. No card behaviour, face, number or generated file moves, and the
codegen check reports the surface already up to date. It is hygiene, disclosed
here because it rode in on this branch and belongs to the Kurage workstream,
not to the HP change.
