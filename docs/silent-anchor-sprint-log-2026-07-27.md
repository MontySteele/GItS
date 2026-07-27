# Silent Anchor — sprint log, 2026-07-27

Executor: Opus. Plan: `docs/silent-anchor-sprint-plan.md`. Design:
`docs/silent-anchor-kickoff-v1.md`. Commits `e6b57dc` (A), `18e24f3`
(B + C-1/2/3), `8bf6435` (C-7 + D).

Gate at every landing: `python -m pytest -q` from repo ROOT.
**1121 passed / 1 skipped** (baseline was 1077/1).

Fresh-clone behaviour was verified by RUNNING it, twice, rather than asserted:

- `GITS_REFERENCE_MODE=committed-only python -m pytest -q` → **1088 passed /
  34 skipped**;
- and then for real — a genuine `git clone` of this branch into a scratch
  directory, with no `game_ref/` present at all, which is exactly the
  environment the CI runner starts from → **1084 passed / 38 skipped**,
  nothing red.

The two differ by four tests because committed-only mode redirects the
game_ref path while a true clone has no directory, and four guards
distinguish those cases. That is the reason both were run.

CI itself has NOT run on this branch: `.github/workflows` triggers on
`pull_request` and on pushes to `main` only, and opening the PR is a [USER]
action (no `gh` on this machine). The clone above is the same check the
runner would perform.

---

## 1. Headline numbers

| | Ironclad | Silent |
|---|---|---|
| DLL pool | 87 | **88** |
| first structural pass | 35 (40%) | **10 (11%)** |
| after this sprint's dial + translator work | 35 | 17 (19%) |
| assembled pool (`*_pool.yaml`) | 76 (87%) | **22 (25%)** |
| passes behind that | 3, over earlier sprints | 1 |

**The 89-vs-91 question is settled: 88.** Both wiki sources were wrong.

**The kickoff's size claim was wrong too, and in an instructive way.** §3 said
Silent is "~15% larger than Ironclad's 76". 76 is Ironclad's *assembled sheet*;
his *pool* is 87. The two characters are the same size to within one card. The
comparison had crossed a measurement of the DSL with a fact about the game —
the same hyphen-vs-underscore confusion that produced the `ironclad-cards.yaml`
snapshot incident, wearing different clothes.

Pool shape (extractor summary, local run):

```
Silent: 88 cards
  rarity  Rare 26  Uncommon 36  Common 20  Basic 4  Ancient 2
  type    Power 19  Skill 42  Attack 27
  defensive 12/88 = 14%    (Ironclad 15%, Klee 17%)
  P(offer is defensive) 19.9%   P(3-card screen has none) 51%
  block per energy: floor 3.0  median 5.0  ceiling 8.0
  effect vocabulary 17 distinct Cmd calls; 40 distinct powers referenced
```

**A replication.** Ironclad's first extraction settled "low defensive density
is normal StS2, not a Klee defect" at 51% chance of a defence-free reward
screen. Silent posts **51%**. Two anchors, same number. That finding is now
replicated rather than single-sourced.

**A new one.** Silent's Rare tier is **0/26 defensive**. Not low — zero.

---

## 2. Track A — tooling generalisation

**A-1.** `ID_PREFIX = "ic_"` was a module constant read at four sites. The
danger was not a loud collision: every character's pool has a Strike and a
Defend, so a shared prefix would have had the second extraction silently
*overwrite* the first in the loader's card index. Now derived per character
(first two letters → `si_`), with `ic_` PINNED because artifacts this tool
cannot rewrite already depend on it. A derived prefix colliding with a pinned
one is an error.

**A-2.** `build_ironclad_sheet.py` → `build_official_sheet.py --character
{ironclad,silent}`, carrying fail-closed / disjointness / ordered `--verify`
unchanged. Required supplement layers are listed **explicitly per character,
never globbed**: "required" is exactly what makes a missing layer an error
instead of a quietly smaller pool, and this directory has been destroyed twice.

*Deviation from plan.* The plan said Ironclad tests stay "untouched". The four
tooling tests in `test_extract_base_game_pool.py` were migrated from
monkeypatching module globals to constructing a `CharacterSpec` — a call-site
migration the plan explicitly permits, with every assertion preserved and three
added. `test_real_ironclad.py` and `test_ironclad_upgrades.py` are untouched.
`build_ironclad_sheet.py` survives as a thin entry point because
`klee-mod/build/validate.ps1` invokes it and because every generated header in
the existing gitignored artifacts names it as the rebuild command.

**Ironclad proven unchanged across every extractor change in this sprint:**
`ironclad-upgrades.yaml` and `ironclad.json` byte-identical, `ironclad-cards.yaml`
doc 1 and `excluded:` semantically identical, `--verify` 76/76.

---

## 3. The defect this sprint found

The first Silent sheet emitted 15/88 — **and 7 of those 15 rows had silently
dropped a printed rule.**

`CanonicalKeywords` was read by a regex looking for exactly one keyword,
`Exhaust`. ilspy renders a one-element keyword list as a compiler-generated
type rather than a `{ ... }` initialiser, and *only* the Exhaust spelling was
ever searched for. Five **Sly** cards and two **Innate** cards were emitted as
vanilla rows: a wrong card wearing the right name, which is the one thing this
extractor exists not to produce.

**Ironclad never exposed it.** Exhaust is the only keyword his pool declares
(census: 11× Exhaust, nothing else). A whole class of silent approximation sat
behind a single-character pool for a month — the second anchor earned its keep
before it was even wired.

Fixed structurally: the declaration is parsed, `Exhaust`/`Innate`/`Retain` map
onto the tier0 `Card` fields that exist for them, and **any other keyword
excludes the card**. An *unreadable* declaration excludes too — an unparsed
keyword line is indistinguishable from an empty one, and guessing empty is how
this happened. Pinned by three data-free tests.

The honest first-pass number after the fix is **10/88 (11%)**, against the
pre-registered expectation that Silent would land below Ironclad's 40%. She
does, by a lot.

---

## 4. Track C — exclusion histogram and what moved

First histogram, measured against the dial in force (the number the plan
required be captured *before* any dial change):

```
  29x  behaviour branches on runtime state
   7x  damage/block scales off runtime state
   5x  CardKeyword.Sly has no tier0 Card field
   3x  PoisonPower not on the dial
   2x  DexterityPower not on the dial
   2x  no tier0 op for CardCmd.Discard
   1x  each of ~30 further powers
   1x  Hand.GetPile / out-of-play hook / hit count / combat history / unrecognised
```

**The structural finding of the histogram**: 40 distinct powers referenced, and
roughly thirty of them gate exactly ONE card each. Poison (3) and Dexterity (2)
are the only powers gating more than one. The Silent is a long tail of bespoke
powers where the Ironclad was a smaller set of reused ones — so C-6's
"implement only if the histogram shows a material card count" resolves to
"implement none of them", and every one is an UNIMPLEMENTED entry with a stated
reason, on the stampede/hellraiser precedent.

### C-1 chosen discard
`select: chosen` on the discard op, through the same `_worst_card` pilot
surface `exhaust_from` already uses — so it is not a second heuristic to keep
honest. Random stays the DEFAULT; flipping it would silently re-price every
existing discard card.

### C-2 poison — verified, and deliberately not `dot`
From `PoisonPower`, not from memory: current stack as damage, `Unblockable |
Unpowered` (bypasses block; neither the poisoner's Strength nor the victim's
Vulnerable scales it), then `PowerCmd.Decrement` by exactly one, **alive-gated**
(a poison that kills does not decrement). `TriggerCount = min(Amount, 1 +
Accelerant)` is transcribed even though Accelerant is unimplemented, so the day
it lands this function is already the thing it modifies.

It is NOT the generic `dot`: `dot` ticks at StS2 site A (before the draw),
poison at site F (after it). Klee and Kokomi are balanced around `dot`'s clock
and the parity work has no claim on it. Two mechanics, same shape, different
clocks, neither pretending to be the other.

### C-3 dexterity — **the sprint plan was wrong about where this goes**
The plan said to hang Dexterity off `refpowers.gain_block`. `DexterityPower`
guards its additive hook with `props.IsPoweredCardOrMonsterMoveBlock()` — the
*same* predicate `FrailPower`'s multiplicative hook uses — and `gain_block`
carries the Unpowered power-block that Frail is correctly not allowed to touch
(no caller passes `card_sourced=True`). Hanging it there would have applied
Dexterity to the block it must NOT scale and missed every block it must.

It lives in `powers.modify_block_gained`, **additive before Frail's
multiplicative**, matching `ModifyBlockAdditive` → `ModifyBlockMultiplicative`:
`(base + dex) * 0.75`. On 5 block the two orderings agree; on 11 they do not.
`AllowNegative` is honoured, floored at 0 before Frail.

Both powers joined `SUPPORTED_POWERS` only after that verification.

### C-4 Sly — held, correctly
Blocked on ask A4. The 5 Sly cards stay excluded, which is now *enforced* by
the keyword fix rather than left to discipline. The naming hazard is real and
is documented at both touchpoints: `state.Card.sly` is **Kokomi's Assist lane**
(resolve an authored effect list when discarded by a card effect);
`CardKeyword.Sly` is **"if discarded before end of turn, play it for free"**.
Different mechanics, one word.

### C-5 Thorns / Weak / Frail audit
Weak, Frail and Vulnerable are present and correct; Frail's 0.75 multiplicative
and its enemy-turn-end tick-down match the source. **Thorns is absent** and
gates exactly one Silent card (`si_abrasive`) — below the bar for
implementation, logged. It is also the stated reason `bronze_scales` is a SKIP
relic, which remains accurate.

### C-7 pass-1 supplement (5 cards)
Every row is a card tier0 expresses EXACTLY. Four were held back by a null-guard
around a discard (`if (cardModel != null)` — an empty-hand check the discard op
already handles by doing nothing) and one by a `foreach` over hittable enemies
that is precisely `target: all_enemies`. All five upgrade deltas were recovered
mechanically from the DLL; none unexpressible.

**What was left out, and why that matters more than what came in.** `Prepared`
is the sharp case: one DynamicVar feeds *both* its draw count and its discard
count, and the upgrade grammar can bump only one. An "obvious" row would have
under-modelled its upgrade silently, forever. It stays excluded with its reason.
`Expertise` needs `max(0, N − hand)`, which the formula grammar cannot clamp.
Every shiv generator needs the Shiv token, which is not in the pool and so has
no DLL source for the supplement pass to recover an upgrade from.

### Also fixed: three cards excluded over an animation timer
`si_neutralize` (**a starter**), `si_slice` and `si_suppress` read
`Character.AttackAnimDelay` into a local and branch on the player's Fast Mode
*preference*. Cosmetic-ness now propagates from a cosmetic declaration to the
statements that only feed it, leaving the `if` empty. Guarded by a test that a
real branch still excludes the card: this must not become a general if-eraser.

---

## 5. Track D — wiring and measurement

Wired exactly as `real_ironclad`: loader sheets + required layers, upgrade
sheet, `roster.REFERENCE_IDS`, `NO_COMPANION_CHARACTERS`,
`CHARACTER_PLANS`/`DEFAULT_PLAN`, and a `silent` pilot with every weight
flagged PLACEHOLDER pending A3.

`test_real_silent.py` (14 tests, skip-guarded) mirrors the Ironclad module and
adds the cross-anchor id-disjointness pin that motivated A-1. `test_anchor_lock`
gets its OWN silent clauses rather than riding the Ironclad ones — a change
stranding only Silent would pass every existing assertion — plus a clause that
the COMMITTED six-card `ref_silent` construct survives a fresh clone. The two
now share a character's name and must not share a fate.

The layer lists in `loader.EXTERNAL_CARD_LAYERS` and
`build_official_sheet.CHARACTERS` are pinned to agree: each side fails closed
only against its OWN list, so a layer in one and not the other is a pool that
loads at the wrong size, silently.

### D-5 axis run

One labeled window: commit `18e24f3`, `game_ref=651847d42009`, 200 fights,
seed 7, baseline `ref_ironclad/starter` = 3.0 by construction.

| config | A1 front | A2 scale | A3 block | A4 sust | A5 veloc | A6 util | A7 tax |
|---|---|---|---|---|---|---|---|
| ref_ironclad/starter | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 | 3.0 |
| ref_silent/shiv_package | 2.9 | 4.7 | 4.2 | 0.5 | 3.6 | 2.6 | 1.6 |
| real_ironclad/starter | 3.5 | 3.3 | 2.5 | 3.3 | 3.0 | 3.1 | 2.9 |
| **real_silent/starter** | **2.7** | **3.1** | **4.6** | **0.5** | **3.0** | **2.5** | **3.9** |

`ref_silent.yaml`'s header predicts A1 ≈ 2, A5 ≈ 4.5, A2 superlinear. The
construct itself posts A1 2.9 / A5 3.6 / A2 4.7 — it matches its own prediction
on A2 and misses on A5.

**The divergence is real but the comparison the header invites cannot be made
yet, and saying so is the finding.** `ref_silent`'s "deck" is its
`shiv_package`; `real_silent`'s is the 12-card starter. A starter deck has no
scaling by construction, so A2 3.1 vs 4.7 is apples-to-oranges. A
package-equivalent Silent deck does not exist at 25% coverage — every shiv
generator is excluded.

**Also on the record: the `silent` and `generic` pilots produce IDENTICAL
statlines on the starter.** Four distinct cards in a twelve-card deck leave the
weights almost nothing to choose between. Ask A3 cannot be evaluated against
these numbers either.

tier 0.5, 300 runs, seed 11: `real_silent` act1 cleared **49%** (real_ironclad
26%), act2 **0%** for both, median act HP 11% of 70, near-death in 33% of runs.

---

## 6. Track E — the two-anchor table, and why it does not ratify the gate

```
pool                  cards vocab hapax  top%  uniq% maxclu rider% neardup decide%
furina                   78    26    10   31%    62%      5    37%      73     26%
klee                     76    34    22   36%    61%      5    25%      26     20%
kokomi                   61    21    13   33%    56%      7    34%      23     30%
OFFICIAL:ironclad        76    40    33   57%    86%      4    26%      18     20%
OFFICIAL:silent          22     9     3   50%    59%      3    50%       7     14%
```

Coverage fraction beside her row, as the kickoff required: **22/88 = 25%**.

### 6.1 The second anchor fails the gate the first one set

PROPOSED gate: uniq ≥ 75 / maxclu ≤ 4 / neardup ≤ 0.33·cards. Silent posts
uniq **59%** — a clear fail. maxclu 3 and neardup 7 pass.

**And she is invisible to the gate while failing it.** `--gate` skips any pool
under `GATE_MIN_POOL = 30`, an exemption written for companion sheets. At 22
cards the anchor added to ratify the gate is never evaluated by it. The
exemption is doing something it was not designed to do, silently.

### 6.2 The obvious defence does not survive its control

The kickoff pre-registered the caveat: the emitted/excluded split biases an
anchor toward simple cards, which should depress uniq%. That predicts
Ironclad's *structurally-simple subset* should look worse than his full pool.
Control, run on this machine:

| subset | cards | vocab | top% | uniq% | maxclu | neardup |
|---|---|---|---|---|---|---|
| ironclad assembled | 76 (87%) | 40 | 57% | **86%** | 4 | 18 |
| ironclad doc-1 only | 35 (40%) | 18 | 66% | **89%** | 2 | 6 |
| silent assembled | 22 (25%) | 9 | 50% | **59%** | 3 | 7 |
| silent doc-1 only | 17 (19%) | 8 | 53% | **47%** | 3 | 6 |

**Restricting Ironclad to his simple cards RAISES uniq% (86 → 89).** The bias
the caveat predicted does not reproduce. At comparable thinness the two anchors
sit 42 points apart. Silent's simple cards genuinely repeat — 3× (weak+damage),
2× (poison), 2× (block), 2× (damage) clones — where Ironclad's simple cards are
each a different idea.

Held honestly: this is evidence, not proof. 22 cards is a small sample, and
"what the DSL expresses" is not a random selector — it may correlate with
distinctness differently for the two characters. But the defence that would
have let us dismiss Silent's row has been tested and did not hold.

### 6.3 What the table actually says

Our pools post 56–62%. Silent posts 59%. **Ironclad posts 86% and is the
outlier.** A gate calibrated on him condemns our pools for matching the other
official anchor. Two live readings, and the sprint does not get to choose:

- **(a)** uniq ≥ 75 is an *Ironclad* property, not an *official-pool* property.
  The gate is mis-set and should be lowered, or scoped to "no pool may be worse
  than the worst official anchor" (which would put the line near 59%).
- **(b)** Both officials are real and the spread between them (86 vs 59) is
  larger than the spread between us and either — in which case uniq% is not
  measuring "official-ness" at all and is the wrong gate metric.

### 6.4 The concentration question is NOT answered, and coverage is why

Kickoff §7.2 asked whether Silent — the most archetype-concentrated official
pool — posts top% near our 31–36% or Ironclad-like 57%. She posts **50%**,
which reads as "officials concentrate, we do not".

**That reading is not safe.** Her vocabulary is **9 ideas** against Ironclad's
40 and our 21–34. With nine words the top word covers a large share
mechanically. Unlike uniq%, top% *does* move with coverage in the control
(Ironclad 57% → 66% when thinned). This sub-question needs a materially larger
Silent pool and cannot be closed here.

### 6.5 Draft ruling for ask A2 — PROPOSED, not self-ratified

1. **Do not ratify uniq ≥ 75.** The second anchor fails it, and the coverage
   defence failed its control. Ratifying now would freeze an Ironclad-specific
   number into a project-wide law.
2. **Do not lower it on this data either.** Reading (a) and reading (b) imply
   different lines, and 22 cards cannot separate them.
3. **Recommended:** hold uniq at PROPOSED and mark it explicitly
   *single-anchor-derived* in the module docstring, so no future reader mistakes
   it for ratified. maxclu ≤ 4 and neardup ≤ 0.33·cards are cleared by BOTH
   anchors and may move to ratified now.
4. **Fix the invisibility regardless of the ruling:** `GATE_MIN_POOL = 30`
   silently exempts the anchor. Either exempt by *kind* (companion sheets) or
   report skipped-by-size rows explicitly so an exemption is never mistaken for
   a pass.
5. **Re-open A2 when Silent's coverage clears ~70%**, or when the excluded set
   stops being systematically the distinctive cards — whichever comes first.

---

## 7. Open asks — all [USER], none self-ratified

- **A1 Ring of the Snake.** Verified semantics, which are narrower than the
  kickoff's description: `ModifyHandDraw` returns `count + 2` **on turn 1 only**
  (`if (TurnNumber > 1) return count`). A first-turn hand-size bonus, not a
  per-turn draw. tier05 already has the shape (`combat_start_draw`), so this is
  purely a ruling. Recommendation unchanged: **(b) wire it** — omitting it
  understates exactly the resource her discard plan spends.
  `char_real_silent.yaml` carries `relic_hooks: []` and `test_real_silent` pins
  it, so the ruling changes one line and one assertion.
- **A2 gate ratification.** §6.5. Delivered as a decision, not applied.
- **A3 pilot heuristics.** Weights ship PLACEHOLDER-flagged. Note §5: they are
  currently unmeasurable — pilot and generic tie on the starter.
- **A4 Sly.** Recommendation now firmer than the kickoff's: **refuse the
  restricted form.** `CardKeyword.Sly` is "play it for free", and the restricted
  reading (resolve its effects on discard) is not a smaller version of that — it
  skips the card-played events that the Silent's own payoffs read. 5 cards, all
  currently excluded and enforced by the keyword check.
- **A5 reserved-card-names bulk pass.** NOT APPLIED — the file is untouched.
  The block is ready and is IP-clean (card names are public wiki material), but
  ~88 lines added to a 27-line curated file changes that file's nature, which is
  what the ask is about. Say the word and it lands as one commit.

---

## 8. Deviations from the plan

1. **A-2 test migration** (§2) — four tooling tests moved to a spec-based API.
2. **C-3 placement corrected** (§4) — the plan's `refpowers.gain_block` was the
   wrong chokepoint; the source says otherwise.
3. **An unplanned P0 was found and fixed first** (§3) — the keyword defect
   preceded everything, because every emitted row was suspect until it did.
4. **`oddly_smooth_stone`'s skip reason was corrected** — it said "Dexterity is
   absent from tier0", which C-3 made false. Reason updated on the
   `juzu_bracelet` precedent; the relic stays SKIPPED, since un-skipping arms a
   knob and moves the tier 0.5 world. That is a [USER] call, not a side effect
   of a parity pass.
5. **C-6 resolved to "implement none"** — the histogram says ~30 powers gate one
   card each. That is the histogram doing its job.
