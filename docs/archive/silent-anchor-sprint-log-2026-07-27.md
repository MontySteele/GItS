> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/silent-anchor-sprint-log-2026-07-27.md` — new path: `docs/archive/silent-anchor-sprint-log-2026-07-27.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Silent Anchor — sprint log, 2026-07-27

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

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

> **SUPERSEDED 2026-07-27 by `docs/a2-gate-ratification-2026-07-27.md`
> (R81), written against the COMPLETE pool.** Point 3's certifications did
> not survive coverage: Silent completed at maxclu 5 and neardup 0.36, so
> ratifying "cleared by both anchors" from a 22-card partial would have
> shipped thresholds an official character fails. Points 1, 4, and 5 held.
> Kept as written — the record shows what a partial anchor licensed.

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

---

## 9. The rulings landed (2026-07-27, same day)

[USER] red-pen on all five asks, verbatim: *"A1) yes, please implement. A2)
gate ratification waits til the card pool completes. A3) Should also wait.
A4) We should implement the Silent's Sly accurate to the game, and also pass
a note to the next tech debt sweep to unify that behavior to Kokomi. A5)
Agreed, let's add them."*

### A1 — Ring of the Snake: WIRED

`starting_relic_effects` is a new character-yaml field, read by the loader on
**both** paths (`build_player` for the battery, `build_player_from_ids` for
the run layer), because `relic_hooks` is a list of bare strings and cannot
carry the `2`. Her entry is one hook: `{combat_start_draw, amount: 2}` —
tier0's `combat_start_draw` is already TURN-1-ONLY, which is exactly
`ModifyHandDraw`'s shape, so nothing was approximated to fit.

The battery is no longer categorically relic-free, and that is a deliberate,
scoped change: only a character whose yaml declares the field gets one, and
no roster character does. A relic on the roster is a DRAFTED relic and stays
the run layer's job.

Pinned by a fight, not by the yaml: `test_ring_of_the_snake_fires_on_turn_one_and_only_turn_one`
runs a real combat and asserts the opening hand is `CARDS_DRAWN_PER_TURN + 2`
and the next one is not.

### A4 — Sly: IMPLEMENTED AS THE GAME HAS IT

**My pre-ruling recommendation was to refuse, and it was wrong on the
evidence.** The argument for refusing was that the restricted reading
("resolve its effects on discard") skips the card-played events the Silent's
payoffs read. That is true of the RESTRICTED reading and is not an argument
against the real one — which the ruling asked for and which does fire those
events. Re-read from the DLL rather than from the earlier note:

- `CardCmd.DiscardAndDraw` collects Sly cards while discarding the batch,
  moves the whole batch to the discard pile (each firing `AfterCardDiscarded`),
  and only then calls `CardCmd.AutoPlay(..., AutoPlayType.SlyDiscard)` on each.
- `AutoPlay` builds a `ResourceInfo` with **`EnergySpent = 0`** and hands the
  card to `CardModel.OnPlayWrapper` — **the same wrapper a manual play uses**.
  So `Hook.BeforeCardPlayed`, `History.CardPlayStarted/Finished` and normal
  result-pile routing all happen. An auto-play is a real card play that
  nobody paid for.
- `IsSlyThisTurn` is keyword-or-granted; `GiveSingleTurnSly` (Hand Trick)
  is the granted half and is not implemented (no card needing it is emitted).

What that required in tier0:

1. **`combat.resolve_free_play(state, card, force_exhaust=False)` now
   exists.** It did not before: `effects._free_play` raised UNIMPLEMENTED
   with a six-point contract docstring naming exactly what the function had
   to do. That contract is now satisfied rather than reinterpreted. The
   Havoc / Cascade / HowlFromBeyond exclusions on the IRONCLAD anchor are
   **unchanged** — they are excluded because the extractor cannot read their
   shapes, not because the primitive was missing — and `--verify` confirms
   his pool is still 76 cards, byte-identical.
2. **`play_card`'s tail became `_finish_play`**, shared by the paid and free
   paths, so the two cannot drift. `OnPlayWrapper` is entered identically by
   both in the source; this is that fact in our code.
3. **`Card.sly_keyword`** joins `Card.sly`, and the extractor's
   `CARD_KEYWORDS` maps `CardKeyword.Sly` onto the new field. Mapping it onto
   Kokomi's would have printed a keyword that resolved an empty list — the
   dropped-rule defect in a new costume, and a test now pins against it.

**Verified scoping, not assumed:** `CombatManager.FlushPlayerHand` moves the
end-of-turn hand with `CardPileCmd.Add`, never through `CardCmd.Discard`. The
end-of-turn flush is therefore NOT a Sly trigger in the base game either — the
pre-existing comment claiming so on the activity-gating law turns out to be
right about the game as well as about us.

**Known ordering divergence, recorded not papered over:** the game draws
BETWEEN the batch discard and the auto-plays (that is what `DiscardAndDraw`
is for). tier0 spells "discard N, draw M" as two ops, so a following draw op
lands after the auto-plays. Fixing it needs a combined op; no emitted Silent
row needs one yet.

**Result: the pool grew 22 → 27 (25% → 31%).** The five Sly cards left the
excluded list. Nine new data-free tests in `test_si_effects.py`.

### A4b — the unification note is filed

`docs/tech-debt-audit-2026-07-26.md` §5, with the touchpoints, the failure
mode (a card that reads as one mechanic and behaves as the other), and the
one direction the unification must NOT take.

### A5 — reserved names: 87 added

The Silent's 88 card names are in `docs/reserved-card-names.txt` as kind-1
external collisions. **Zero collided** with the mod's 266 existing names, so
the list is a fence for the future rather than a record of a fire.

One entry was already there: `Grand Finale`, hand-flagged by [USER] on
2026-07-21 as "base game / Downfall Silent". It IS in the StS2 Silent's own
pool — the hand-flag was right twice over, and its line now says so instead
of being duplicated.

**Ironclad's 87 names are NOT in the file.** The same exposure exists for
him; this pass was scoped to the Silent. A green lint currently means "no
collision with the SILENT", and the file's header says exactly that.

### A2 / A3 — deferred, and recorded where they will be seen

Both wait for the pool to complete. The deferral is written into
`card_distinctness_report.py`'s docstring and its `--gate` output (**all
three** thresholds stay PROPOSED — ratifying the two both anchors clear
would freeze the easy half and make the contested half look like the only
open question) and into the `silent` pilot block in `archetypes.yaml`.

A3's deferral is additionally the *right* call on evidence rather than a
postponement: the weights are currently unmeasurable, because the `silent`
and `generic` pilots tie on a twelve-card starter holding four distinct
cards.

### Re-measurement after the world moved

`git=6bc4609+`, `game_ref=790c7ee0c8ff`. Both rulings landed together, so
attribution is stated per surface rather than claimed globally:

| surface | before | after | attributable to |
|---|---|---|---|
| distinctness | 22 cards, uniq 59%, top 50%, neardup 7 | **27 cards, uniq 63%, top 48%, neardup 12** | A4 only (A1 is not a card) |
| battery A1/A3/A5/A7 | 2.7 / 4.6 / 3.0 / 3.9 | **2.8 / 4.7 / 3.1 / 4.7** | A1 only — no Sly card is in the starter deck |
| tier 0.5 act 1 (300 runs, seed 11) | 49% | **46%** | BOTH; and the delta is inside sampling noise (se ≈ 2.9%), so it is reported, not read |

The distinctness verdict did not change, and that is the useful part: +23
percentage points of coverage moved `uniq` by four points. The gate's
failure is not a coverage artifact.

---

## 10. The overnight coverage pass (2026-07-27, same day)

[USER]: *"please proceed with the sprint plan, including implementation of as
many cards as possible that do not require a ruling from me."* Everything
below is implementation and measurement; no ask was answered on the user's
behalf.

**Coverage: 27 -> 46 -> 56 of 88 (31% -> 64%).**

### 10.1 Nineteen powers (46 cards)

Each read off its own decompiled PowerModel and implemented in
`refpowers`/`powers`: accelerant, afterimage, anticipate, block_next_turn,
blur, burst, corrosive_wave, draw_cards_next_turn, envenom, free_skill,
intangible, master_planner, noxious_fumes, outbreak, serpent_form,
shadowmeld, speedster, strangle, thorns, tools_of_the_trade,
well_laid_plans. Three new hook sites: `AfterCardDrawn` (inside
`CombatState.draw`, per CARD), `ModifyHandDraw` (site D), `BeforeFlushLate`.

Three of them are worth naming individually:

- **Accelerant needed no behaviour at all.** `poison_tick` already
  transcribed `TriggerCount = min(Amount, 1 + Accelerant)` against a
  hardcoded zero, with a comment saying it was transcribed so that the day
  the power landed this function would already be the thing it modifies.
  That day was today and the comment was right: one line changed, no logic.
- **Shadowmeld had to go in BOTH block funnels.** Its multiplicative hook
  carries no `IsPoweredCardOrMonsterMoveBlock` guard, so unlike Frail it
  doubles power block too -- and tier0's two block paths are disjoint
  (`_op_block` for card block, `refpowers.gain_block` for power block). One
  site would have been half a power.
- **The Silent's four per-play powers sit ABOVE `after_card_played`'s
  attacks-only early return.** Afterimage on a Skill is most of what that
  card is for; below the return it paid out on nothing.

**Two powers are REFUSED, not implemented, and that is a finding.** Sneaky
pays out only when an ALLY plays an Attack; Flanking multiplies only for a
dealer other than the applier. In single-player neither trigger is
reachable, so they go in `refpowers.MULTIPLAYER_ONLY_POWERS` and the
extractor now reports a THIRD category -- `CO-OP ONLY` -- beside
"unimplemented" and "not on the dial". Implementing either would have
produced a card that reads as a buff and measurably does nothing, which is
the same class of defect as the dropped keyword, only louder.

`bronze_scales`' skip reason was corrected on the `oddly_smooth_stone`
precedent (Thorns exists now). The relic stays SKIPPED -- arming it is a
[USER] ruling.

### 10.2 A hand-translated layer, `silent_pool_pass2.yaml` (56 cards)

Ten cards the strict structural translator refuses to invent but whose
behaviour tier0 expresses exactly: Haze and Piercing Wail (a `foreach` over
HittableEnemies is `target: all_enemies`; PiercingWailPower IS the class
Mangle uses), Bubble Bubble (a real `if`, on the predicate
`target_has_power_poison` that already existed), and seven
calculated-damage cards behind six new `_runtime_count` tokens --
`attacks_played_this_turn`, `skills_in_hand`, `other_cards_in_hand`,
`discards_this_turn`, `cards_drawn_this_combat`, `enemy_poison_total`, plus
`X` for Skewer's hit count.

Two supporting fixes, both of which the tooling FOUND rather than my
noticing: `CalculationBase` and `ExtraDamage` are the two halves of one
grammar and collided on a single upgrade key (Memento Mori upgrades both),
and the `power_amount` upgrade key searched only top-level effects, so
Bubble Bubble's nested apply was invisible to it. The builder refused both
rows until they were fixed, which is the fail-closed design working.

**What is still excluded, and why it is not laziness:** the SHIV cards (12
of them) need a token card that is not in the 88-card pool at all, so the
extractor cannot even find its source; Grand Finale needs a playability
gate ("only while the draw pile is empty"); Nightmare, Hidden Daggers and
Well Laid Plans' card-selection prompts need a chooser; Blade of Ink needs
enchantments. Each stays excluded with its reason.

### 10.3 The gate reading moved four times in one day

```
  22/88 (25%)  uniq 59%  FAIL        46/88 (52%)  uniq 78%  pass
  27/88 (31%)  uniq 63%  FAIL        56/88 (64%)  uniq 73%  FAIL
```

**I published two conclusions off this anchor and coverage overturned both.**
At 22-27 cards: "Ironclad is the outlier and the gate condemns us for
matching the other anchor." At 46: "the anchors agree with each other and
disagree with us." At 56 she is four points under the line and neither
statement survives. The E-2 control that licensed the first one -- thinning
Ironclad RAISES his uniq -- was a good experiment with a misleading answer:
coverage bias is a property of the SLICE, not of thinness, and a control run
on the other anchor cannot see it.

`maxclu` and `neardup` never breached on either anchor across all four
readings. That is the only part of the gate the data has held still on, and
it is still not ratified, because ask A2 deferred all three and the ruling
looks better every time this number moves.

### 10.4 tier 0.5, and a number that went the wrong way

300 runs, seed 11, `game_ref=b6998b1285f8`:

| pool | act 1 clear | near-death |
|---|---|---|
| 27 cards | 46% | 36% |
| 46 cards | 31% | 30% |
| 56 cards | 39% | 35% |

**Act-1 clear FELL as coverage rose, and I cannot attribute it yet.** The
starter battery is unchanged across all three (2.8 / 3.2 / 4.7 / 0.5 / 3.1 /
2.6 / 4.7), which is consistent with a DRAFT-side cause rather than a combat
one: nineteen powers' worth of new cards entered her reward pool, the pilot
weights are ask-A3 placeholders, and the scorer still has no poison term at
all. The most likely reading is that the anchor is now drafting cards it
cannot pilot. That is a hypothesis, not a finding, and it is exactly the
measurement A3's deferral leaves open.

Suite at the end of the pass: **1168 passed / 1 skipped** from repo ROOT.

### 10.5 The Shiv, and one more gate reading (59 of 88)

The twelve shiv cards were excluded for a reason that turned out to be about
the TOOL, not the DSL: `Shiv` is created in hand and is not one of the 88
draftable cards, so `decompile_character` never loaded its source and no
supplement could reference it. The extractor now finds token types
**structurally** -- it scans the pool's own sources for the two create-call
shapes (`X.CreateInHand(`, `CreateCard<X>`) and loads what it finds, which
on this pool is exactly `Shiv`. No card-name table entered the committed
tool.

`silent_pool_pass3.yaml` carries the token plus the three creators whose only
untranslatable part was that it did not exist (Blade Dance, Cloak And Dagger,
Leading Strike). The `for` loop those three use is a COUNT, which `add_card`
already takes as an amount; a new `cards` upgrade key bumps it, kept distinct
from `draw` because creating a card and drawing one are different resources.

**The Shiv's single-target damage is EXACT only conditionally, and the
condition is recorded where it will be hit.** The real Shiv targets one enemy
unless the owner has FanOfKnivesPower, which rewrites its TargetType to
AllEnemies. That power is now in `refpowers.UNIMPLEMENTED` -- a third kind of
entry there, since it is not a mechanic tier0 cannot run but a mechanic that
would silently invalidate an already-translated row -- and its reason names
the Shiv row explicitly. A test pins that the reason still says "Shiv".

The remaining nine shiv cards stay out on their own merits: Fan Of Knives
(the power above), Storm Of Steel and Hidden Daggers (a discard whose size is
the hand, and an upgrade that upgrades created cards), Knife Trap (auto-play
every shiv in the exhaust pile), Blade Of Ink (enchantments), Up My Sleeve (a
permanent self-cost reduction), Accuracy / Infinite Blades / Phantom Blades
(three more powers).

**Fifth gate reading, and it did not settle anything:** 60 pool rows (59 of
the 88 plus the token), `uniq 72%` -- three points under, `maxclu 4`,
`neardup 23`. tier 0.5 act-1 clear 35% (300 runs, seed 11,
`game_ref=4cba51f68f68`), still below the 46% it posted at 27 cards and
still unattributed.

Suite: **1170 passed / 1 skipped** from repo ROOT.

---

## 11. Where this leaves the morning

Landed overnight, all green, all pushed: the five rulings, nineteen parity
powers, two hand-translated card layers, the Shiv token, and 29 new
data-free tests. Coverage 22 -> 59 of 88.

**Two things want [USER] eyes, neither actioned:**

1. **The gate number will not hold still.** Five readings, two published
   conclusions of mine overturned, and the only stable parts (`maxclu`,
   `neardup`) are the ones nobody doubted. Ask A2's deferral is holding up
   well; the question worth asking when the pool completes is whether
   `uniq` is measuring anything a designer should be gated on.
2. **tier 0.5 act-1 clear fell as coverage rose** (46% -> 31% -> 39% ->
   35%) while the starter battery stayed flat. The hypothesis is the
   A3-placeholder pilot drafting cards it cannot fly, and the scorer having
   no poison term at all. Testing it is a measurement task, not a ruling --
   but it is the measurement that would make ask A3 answerable.

---

## 12. The pilot review, the denominator, and what the last cards need

### 12.1 Ruling recorded: review the pilot when the pool completes

[USER], 2026-07-27: *"let's make a note to review the pilot after all of the
cards land."* Written where it will actually be read -- at the top of the
`silent` entry in `tier0/content/pilots/archetypes.yaml`, beside the
PLACEHOLDER numbers themselves, not only here. The note names three questions
in order, because doing them out of order would corrupt the answer:

  a. Re-read the placeholders against the complete pool (ask A3).
  b. **Explain the act-1 clear regression FIRST.** Tuning weights before that
     is explained would tune them to hide it.
  c. Decide whether the SCORER needs a poison term -- a change no value in
     the weights block can express.

### 12.2 The denominator was wrong, and it was wrong for both anchors

Triaging the gap turned up a fact that is not about the Silent at all. Two of
her 88 printed pool cards -- Flanking and Sneaky -- carry
`CardMultiplayerConstraint.MultiplayerOnly`, which is the game declaring that
a single-player run never offers them. Ironclad has two of his own (Demonic
Shield, Tank). Every coverage number this sprint has published measured
against a universe containing four cards that cannot appear in the world we
simulate.

The extractor now reads that constraint structurally (`MP_ONLY`), and those
cards go to a new `unavailable:` block in document 2 -- recorded, not dropped,
so nobody re-derives them from the pool listing and reports the sheet as
missing cards it deliberately does not want. They are OUT of the denominator:

    Silent    41 emitted / 45 excluded of 86     (was: of 88)
    Ironclad  35 emitted / 50 excluded of 85     (was: of 87)

Live coverage is therefore **59 of 86 (69%)**, and the remaining debt is
**27 cards, not 29**. Note what this is not: it is not a coverage improvement.
Nothing was implemented; a wrong measuring stick was replaced.

Two checks, both clean. No card already emitted or hand-translated into
EITHER anchor's live pool is multiplayer-only -- the shortfall was in the
denominator only, never in the pool. And the inverse flag exists
(`SingleplayerOnly`, on Well Laid Plans) and is deliberately NOT filtered: it
is in the game we measure.

This also retires the CO-OP ONLY reasons written earlier today, which argued
from `SneakyPower`/`FlankingPower` guard clauses. The argument was right and
the evidence was second-hand: the game says it at the card level. Both
categories now coexist, because a power can be co-op-only on a card that is
not, and only the card-level flag may touch the denominator.

The gate did not move: `uniq` is computed over the pool, so the sixth reading
is the fifth reading. That is worth saying out loud after a day in which this
number moved five times -- **this change moves the coverage story and nothing
about the measurement.**

### 12.3 Triage of the 27: what each one is actually waiting on

Read from the DLL, not from the exclusion strings, which are the translator's
generic complaints and understate what is possible now that passes 1-3 have
landed. Two things surprised me, both in the direction of less work:

**Bucket A -- translation plus at most one new amount token (9).** Prepared
and Calculated Gamble need no new mechanic at all; the extractor simply does
not map `CardCmd.Discard` + `CardSelectCmd.FromHandForDiscard`, and the ops
have existed since Kokomi. Expertise wants a hand-size stop condition on
`draw_while`, which today stops on card TYPE. Dodge And Roll needs the block
it ACTUALLY gained (`block_gains_this_card` is already tracked). Escape Plan
needs a condition on the drawn card's type; Malaise is X-cost arithmetic we
already do; Bouncing Flask needs a repeat that re-rolls its random target;
Echoing Slash a repeat-while-it-killed; Expose an enemy block-strip.

  Expose carries one thing that must be stated on the row rather than
  silently skipped: it also removes ArtifactPower. tier0 models no Artifact,
  so in this world that clause is VACUOUS, and skipping a clause that could
  never fire is exact. Skipping it quietly is how a row starts lying.

**Bucket B -- one genuinely new engine concept each, no ruling (16).**
Accuracy, Infinite Blades, Phantom Blades, Tracking and Wraith Form are five
more powers of exactly the kind pass 1 did nineteen times. Shadow Step needs a
damage-doubling power; Bullet Time a free-hand-this-turn plus NoDraw; Up My
Sleeve and Pinpoint two shapes of self-cost reduction (Pinpoint's is
retroactive, via `AfterCardEnteredCombat`); Hidden Daggers and Storm Of Steel
need created tokens that arrive upgraded; Nightmare needs a power that
remembers a chosen card and clones it next turn; Knife Trap auto-plays every
Shiv in the exhaust pile -- which `resolve_free_play` made possible only
today.

  **Grand Finale is in this bucket, not the ruling bucket, and I expected
  otherwise.** It is unplayable unless the draw pile is empty, and I assumed
  conditional playability would be a DSL question for [USER]. It is not:
  `Card.requires` already exists with exactly this shape (`burst_energy_full`)
  and `pilot/policy.py` already filters on `card_playable`. It needs one more
  `requires` value and no new concept.

  **Fan Of Knives stays last on purpose.** It makes every Shiv hit all
  enemies, so it cannot land without changing the already-translated Shiv row
  in the same pass -- which is precisely what its `UNIMPLEMENTED` entry says.

**Bucket C -- genuinely needs a ruling (2).**

  1. **The Hunt.** On a fatal kill it grants an extra CARD REWARD. That is a
     combat effect reaching into the run layer, which the tier0/tier0.5 split
     forbids by design. Either the split gets a documented exception or the
     card stays out; both are defensible and neither is mine to choose.
  2. **Blade Of Ink.** It creates Shivs enchanted with `Inky`. Enchantments
     are a subsystem tier0 does not have in any form. This is a SCOPE
     question -- does the anchor want an enchantment layer at all? -- not a
     translation one, and it is much larger than one card.

So the honest answer to "what do you need": for 25 of the 27, nothing. For
The Hunt and Blade Of Ink, one ruling each.

---

## 13. ADDENDUM: enchantments want a design pass ([USER], 2026-07-27)

> **CLOSED 2026-07-27 (R82).** The pass ran and was ratified same day:
> docs/enchantments-design-2026-07-27.md. Blade Of Ink ships as
> per-instance riders on its tokens (silent_pool_pass7.yaml), the
> subsystem refusal is recorded in the extractor, the design space is
> ratified OPEN for house characters, and THE POOL IS COMPLETE at 86 of
> 86. Gate re-read at 87 rows: PASS.

Ruling: *"we should do a design pass on enchantments."* Blade Of Ink stays out
of the pool until that pass happens, and this addendum exists so the pass
starts from the question rather than from the card.

**Why this is not a translation problem.** Blade Of Ink creates Shivs and then
enchants each of them (`CardCmd.Enchant<Inky>`). An enchantment is state
attached to a CARD INSTANCE, carrying its own stack amount. Every modifier
tier0 has -- powers, auras, statuses -- attaches to a CREATURE. The Card
dataclass has flags (`exhaust`, `innate`, `retain`, `sly_keyword`) but no
concept of a per-instance modifier with a value, and no concept of two copies
of the same card differing in what they do. That is the gap, and it is a
data-model gap, not a missing op.

**What the pass has to decide, in the order the answers constrain each other:**

1. **Does tier0 model enchantments at all?** A legitimate answer is no --
   and if it is no, that answer belongs in `refpowers.UNIMPLEMENTED`'s spirit:
   written down once, with its reason, so the question stops being reopened
   one card at a time. Note the honest price of yes: among the Silent's 27
   remaining cards exactly ONE needs it. A subsystem for one card is a bad
   trade unless the answer to (2) is that we want enchantments for OUR
   characters too.

2. **Is this a base-game parity feature or a Teyvat Spire feature?** These
   pull in opposite directions. Parity says model it because the anchor pool
   contains it, and the anchor exists to measure our pools against a real
   one. Design says our characters have never wanted per-card state, and
   adding a mechanic to the DSL that only the reference pool uses grows the
   engine for a measurement rather than for a game. If the answer is
   parity-only, consider whether the anchor can be honest WITHOUT it -- an
   `unavailable:`-style category for "expressible only with a subsystem we
   chose not to build" would say so out loud, the way the MultiplayerOnly
   cards now do.

3. **If yes: where does the state live, and what copies it?** A card in
   tier0 moves hand -> discard -> draw and is cloned by several effects
   (`copy_companion_in_hand`, `copy_spotlighted_in_hand`, Nightmare's clones
   when it lands). Every one of those sites has to answer whether the
   enchantment travels. Getting this wrong is invisible in a card sheet and
   very visible in a sim result.

4. **What does an enchantment DO, mechanically, in a world with no
   enchantment payoffs?** `Inky` on a Shiv is only worth modelling if
   something reads it. If nothing in either pool reads it, then implementing
   it faithfully produces a card that is exactly as inert as Sneaky was --
   which is the trap the CO-OP ONLY category was created to stop us walking
   into twice.

5. **Interaction with the two things it touches today.** The Shiv is a TOKEN,
   created at runtime rather than drafted, so enchanting one means the
   enchantment attaches to a card that never existed in the deck. And
   upgrades are recovered MECHANICALLY from `OnUpgrade`; an enchantment that
   scales on upgrade needs an upgrade key, or it silently does not scale.

**Not in scope for this addendum, deliberately:** what Inky itself is worth.
That is a number, and numbers come after the model. Answering (1) and (2) may
make it moot.

---

## 14. The pool is complete (85 of 86), and the gate has its answer

Passes 5 and 6 finished the Silent. Coverage 22 -> 85 of 86 in one day; the
one card still out is Blade Of Ink, which [USER] sent to the enchantments
design pass (§13) and which no amount of DSL work closes.

### 14.1 A fourth exclusion category: PAYLOAD POWERS

Infinite Blades creates the owner's TOKEN; Phantom Blades reads the owner's
card TAG. tier0 implements both powers, but a base-game card id or tag is
decompiled game data and may not appear in committed engine code. So the row
carries it as a `payload` and `effects._op_apply_power` hands it to the
power -- the id stays in the gitignored yaml where it already lived.

The category exists because of what the alternative was. Emitting those cards
structurally would have applied a real power with nothing to work on: a card
that reads as a buff and measurably does nothing. That is the identical
failure the CO-OP ONLY category was created to prevent, arrived at from the
opposite direction, and the extractor now refuses both the same way.

### 14.2 Two numbers read off the DLL that I would have got backwards

DoubleDamagePower returns a literal `2` and its stacks count TURNS (one
decrements per owner turn end) -- two stacks is two turns of doubling, not
quadruple damage. TrackingPower is the exact opposite: `base.Amount` IS the
multiplier, so its second copy takes 2x to 3x. Assuming either would have
been a large silent difference, and they sit two lines apart in the same
hook.

### 14.3 The Shiv row changed, exactly as pass 3 said it would have to

When the token was translated single-target, `refpowers.UNIMPLEMENTED` carried
an entry that was not a refusal to model a mechanic -- it was a note that
FanOfKnivesPower rewrites the token's TargetType, that the single-target
translation was exact only while the power could not exist, and that the two
had to land in the same pass. Pass 6 is that pass: the row carries
`target_all_if_power: fan_of_knives`, the power is implemented, and the entry
is gone. That entry did its whole job -- it made a conditional exactness
claim, named the condition, and expired when the condition did.

### 14.4 The gate, seventh reading, and A2 is answerable now

    OFFICIAL:silent  85/86 (99%)  vocab 50  top 31%  uniq 72%  maxclu 5  FAIL

**`uniq` finished where it started.** 72% at 59 cards, 72% at 85, having
passed through 78% in between. Twenty-six more cards moved it by nothing.
`maxclu` went UP to 5 and `neardup` to 31 against a 28 budget -- the two
columns that had looked stable across five readings both breached on the
completed pool.

A2 deferred ratification until the pool completed. It has completed, and the
answer is not "ratify": a finished, real, shipped base-game character fails
two of three thresholds. That makes these numbers a statement about the
THRESHOLDS rather than about any pool. Three options, none of them mine:
recalibrate off the completed second anchor; keep the thresholds and accept
that they describe an aspiration no shipped pool meets; or retire `uniq` as a
gate column and keep it as a report. The tool's docstring carries all seven
readings and this paragraph.

> **A2 CLOSED 2026-07-27:** [USER] took the first option. Recalibrated on
> the two-anchor floor and RATIFIED (uniq ≥ 70 / maxclu ≤ 5 / neardup
> ≤ 0.40/card; top%/vocab permanently gate-free), enforced as a red suite
> test with a curated debt list. R81;
> `docs/a2-gate-ratification-2026-07-27.md`.

### 14.5 What was still owed -- ALL THREE PAID, 2026-07-27 (same day)

Nothing in this section is open. Each item carries its closure inline
(banner folded into the list 2026-07-29 by the doc de-drift pass).

- ~~**Blade Of Ink**, pending the enchantments design pass (§13).~~
  **PAID** -- it landed via the enchantments pass (§13 closure banner; R82).
  **The pool is 86 of 86.**
- ~~**The pilot review** ([USER], §12.1), whose trigger -- pool completion --
  has now fired. The act-1 clear regression is the first question and it is
  still unexplained; nothing in passes 4-6 was aimed at it.~~
  **PAID** -- the review ran, and the regression question is EXPLAINED as an
  estimator artifact rather than a real regression
  (`docs/silent-pilot-review-2026-07-27.md` §1a).
- ~~**A2/A3 remain unratified.** A2 now has its evidence and needs a ruling;
  A3 is unblocked for the first time, because the pilot finally has a
  complete pool to draft from.~~
  **PAID, both halves.** A2 was RATIFIED as **R81** on the recalibrated
  two-anchor floor (`docs/a2-gate-ratification-2026-07-27.md`); A3 was ruled
  to stay PLACEHOLDER (**R83**) after the weights measured as a dead lever
  (24.2% vs 24.5%, 1000 runs).

---

## 15. Post-sprint review (2026-07-27, four-reviewer pass, fixes applied)

An adversarial review of the whole branch confirmed the log's claims
essentially everywhere it checked -- and found **one P0, twice
independently, each time with a live repro**:

**The end-of-turn flush destroyed duplicate cards under Well Laid Plans.**
`Card` is a dataclass, so `c not in retained` compared by VALUE; retaining
one Strike made its equal twin fail the discard filter AND miss
`p.hand = retained` -- the twin left the combat permanently. With a starter
of 5 Strikes / 5 Defends, every run drafting WLP shed duplicates turn after
turn, invisibly. The existing test used two distinct cards and could not
see it. FIXED by identity membership, and the same value-equality idiom was
then swept out of EVERY card-pile remove (`state.remove_instance`, ten
sites across combat/effects/refpowers -- per-instance state like
`cost_delta_this_combat` means equal twins are not interchangeable). Two
twin-card tests pin the flush.

**Every tier 0.5 Silent number in this log predates that fix** and is
suspect to the degree WLP entered decks. The act-1 regression question
(§12.1.b) should be re-measured before it is explained. A narrowing fact
for that review, also found here: tier05/runner.py flies `real_silent` on
the GENERIC pilot, so the A3 placeholder weights never touched any act-1
number -- the live suspect is the draft scorer.

Also fixed on review: Intangible now caps unblockable damage and poison
ticks (it capped only the block-funnel path; Wraith Form's promise);
the loader<->builder layer-agreement pin moved out of the game_ref skip
guard so CI can see it; a token-free `CanonicalKeywords` declaration
(`=> _keywords;`) now excludes instead of reading as empty; the upgrade
lookup fallbacks catch only missing-entry shapes instead of every
exception; derived-vs-derived id-prefix collisions are pinned by test;
token discovery no longer swallows the ambiguous-match error; the
stale coverage block in archetypes.yaml was updated to the completed pool;
the gate banner and docstring were brought current (the 75-card reading is
now in the table, columns unrecorded at the time marked `--`).

**Deliberately NOT touched:** the committed `tag_damage_shiv` power name
sits on the wrong side of §14.1's own payload rule (a base-game tag in
committed code) -- or the rule overstates. Either way it is a [USER]
ruling, filed here rather than papered over.

### 15.1 The tag ruling, and what re-running Ironclad found (same day)

[USER] ruled: clear the issue. A plain rename cannot -- the committed name
must equal `tag_damage_` + the snake of the base game's own CardTag or the
real pool's Accuracy silently buffs nothing -- so the fix is the one §14.1
already prescribes: the committed dial now holds only the PREFIX
(`TAG_SCOPED_POWERS = {"AccuracyPower": "tag_damage_"}`), and
`decompile_character` completes the entry into SUPPORTED_POWERS and
UPGRADE_POWER_KEY by reading the single CardTag off the power's own
decompiled source (fail-closed: zero or two tags refuses), the same way
tokens and CanonicalTags were already recovered. Verified by re-running
both extractions: every game_ref output byte-identical. The finished name
now exists only in gitignored output. What REMAINS committed --
`tag_damage_shiv` in `tier0/content/cards/silent.yaml`, tests, and the
effects.py comment -- is REF vocabulary: ref_silent's own token tag,
authored from public StS1 knowledge in the Bomb-era commit 719219a, long
before any decompilation. §14.1 does not reach it; the coincidence of
spelling is the linkage working as designed.

The verification run also exposed a LATENT pass-5 break nobody had seen:
`Ironclad --emit-sheet` had not been re-run since NoDrawPower joined the
dial (10:54), so its 9:54 sheet predated Battle Trance graduating from the
pass-4 supplement -- and the next run refused on
`ic_battle_trance overlaps the emitted sheet`, exactly the tripwire doing
its job. The supplement row was expired (the Fan Of Knives pattern: the
hand translation's whole job was to exist until the structural one could).
Diff of the re-emitted sheet: the row moved from excluded to emitted 36/85
with byte-identical effects, metadata, and upgrade delta, so no merged
pool content and no recorded gate reading moved. The "Ironclad
byte-identical" claim in §15 above is now locally re-verified -- through
9:54; pass 5 itself had broken the RUN, not the output.
