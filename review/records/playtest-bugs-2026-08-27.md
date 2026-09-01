Status: RECORD

# Playtest bugs, 2026-08-27 — EB-150, EB-151, EB-152

Three things [USER] reported in the Kokomi/Furina playtest of 2026-08-26. Each
one below says: what he saw, what the game actually did when the harness drove
it, what the cause turned out to be, what changed, and the exact command to
re-run the check once this branch is merged and deployed.

Everything measured here was measured against the **deployed build 0.2-1159**,
which is the build with the bugs in it. A worktree cannot deploy, so the green
half of EB-150 is owed one attended run from the primary checkout after merge.
EB-151 and EB-152 need no such run and the reasons are in their sections.

Short version:

| | report | verdict |
|---|---|---|
| EB-150 | Deep Breath soft-locks | **Real, found, fixed.** The two mode faces belonged to no card pool. |
| EB-151 | Pearl Barrage always does 5 | **Not a code defect.** The card scales correctly, live. What he saw has two other explanations, and both are questions for him. |
| EB-152 | Kokomi's Burst cards aren't labelled | **Real, found, fixed.** One line in the generator printed the label for Klee's cards only. |

---

## EB-150 — Deep Breath soft-locks the game

> "Deep Breath's 'choose one' mechanic doesn't work - softlocks the game"
> — [USER], 2026-08-26

### The red run, verbatim

`understudy/scenarios/deep-breath-modal-choice.yaml`, driven against 0.2-1159:

```
FAILED expect / resource: KLEEMOD_ENCORE is 0, expected 2
```

The steps around that failure, off the run log
(`understudy/logs/scenario/scenario-deep-breath-modal-choice-20260827-124658.jsonl`;
the log directory is gitignored, so the rows are transcribed here):

```
5  play Deep Breath                     ok  "Playing 'Deep Breath'"                        -> card_select
7  select Gain 1 Energy and 2 Encore    ok  "Choosing card: Gain 1 Energy and 2 Encore"    -> card_select
9  expect                                   KLEEMOD_ENCORE is 0, expected 2                -> card_select
```

and the run's own verdict:

```
"record": "run_end", "outcome": "defect",
"detail": "no_progress: 2 distinct state fingerprint(s) across 12 posted actions (cycle):
           card_select|None|1|2|None|48|2|7|-|0 <-> monster|None|1|2|1|48|3|6|46|0"
```

Read that as: the choice screen came up, the mode was picked, the game said it
had been picked — and then nothing happened. Encore never moved, the screen
never closed, and the run spent the rest of its actions bouncing between the
stuck screen and the combat behind it. That is the soft-lock.

The game's own log for the same play (`godot.log`, 2026-08-27 12:46):

```
[INFO] Player 1 playing card KLEEMOD-DEEP_BREATH (no target)
ERROR: System.InvalidOperationException: You monster!
   at MegaCrit.Sts2.Core.Models.CardModel.NeverEverCallThisOutsideOfTests_ClearOwner()
   at MegaCrit.Sts2.Core.Models.Cards.Mocks.MockCardModel.MockCanonical()
   at MegaCrit.Sts2.Core.Models.CardPools.MockCardPool.MockCard[T](CardRarity rarity)
   at MegaCrit.Sts2.Core.Models.CardPools.MockCardPool.GenerateAllCards()
   at MegaCrit.Sts2.Core.Models.CardPoolModel.get_AllCards()
   at MegaCrit.Sts2.Core.Models.CardPoolModel.get_AllCardIds()
   at MegaCrit.Sts2.Core.Models.CardModel.get_Pool()
   at MegaCrit.Sts2.Core.Models.CardModel.get_VisualCardPool()
   at MegaCrit.Sts2.Core.Nodes.Cards.NCard.Reload_Patch1(NCard this)
   at MegaCrit.Sts2.Core.Nodes.Cards.NCard._Ready()
```

followed, a few lines later, by the `NullReferenceException` in
`NChooseACardSelectionScreen.AfterOverlayShown()` that the 2026-08-26 playtest
log showed.

### The cause

Deep Breath's two modes are shown to the player as two little cards on the base
game's choose-a-card screen. Those two cards — `DeepBreathModeA` and
`DeepBreathModeB`, generated into
`klee-mod/KleeCode/Cards/Furina/Generated/DeepBreath.cs` — belonged to **no
card pool at all**.

That sounds harmless and is not. When the game draws a card on screen it asks
the card which pool it came from, to pick its frame and colours. A card in no
pool does not answer "none": `CardModel.Pool`
(`sts2src/MegaCrit.Sts2.Core.Models/CardModel.cs:297`) falls through to a
test-only mock pool, and building that mock pool throws
`InvalidOperationException("You monster!")` in a shipped build. The throw lands
inside the choose-a-card screen's own `_Ready()`, at the moment it builds the
first option card — which is *before* the screen has fetched its buttons. The
screen is then shown anyway, `AfterOverlayShown()` reaches for a button that
was never fetched, and that is the `NullReferenceException`. The card play is
waiting on an answer from a screen that can no longer give one, so the turn
never comes back.

This exact failure was already written down. `tools/lint_pool_membership.py` has
described it in its docstring since 2026-07-21 — "a poolless card does not fail
when it is played, it fails when it is drawn or previewed". It did not catch
this one because its class-matching pattern looked for `: CustomCardModel` and
the generated mode faces derive from the shared `ModalOptionCard` base instead.

The two hand-written selector options for Furina's Ethereal Spotlight
(`CenterStageOption`, `GuestCastOption`) were already carried in a pool for
exactly this reason — `FurinaCardPool.cs` says so in a comment. The generated
faces were simply never given the same treatment.

Blast radius: **one card**. `deep_breath` is the only `choose_one` row on any
sheet, and `ModalChoice.SelectMode` has no other caller in the mod.

### The fix

1. `tools/gen_klee_cards.py` now emits a per-character roster of the mode faces
   (`FurinaModalOptions`), the same shape as the existing Guest Star roster, so
   a modal card added tomorrow is carried without anyone remembering to.
2. `FurinaCardPool.cs` carries that roster in its off-pool list, beside the two
   hand-written Spotlight options.
3. `tools/lint_pool_membership.py` now sees `ModalOptionCard` subclasses, so
   the gate that was supposed to catch this can.
4. Three structural tests in `tier0/tests/test_eb118_modal_parity.py`: the mode
   faces exist and the scan can see them; every face is in a generated roster;
   every roster is carried by a card pool.

Both gates were seen to fail before they were made to pass. The lint, run
against the tree with the roster removed:

```
FINDING: klee-mod\KleeCode\Cards\Furina\Generated\DeepBreath.cs: DeepBreathModeA is in no card pool.
         CardModel.Pool falls through to MockCardPool and throws 'You monster!' the first time the
         card is drawn or previewed. Add it to a visible character pool (rollable or filtered as off-pool).
FINDING: ... DeepBreathModeB is in no card pool. ...
exit=1
```

and the tests, before the generator change:

```
FAILED tier0/tests/test_eb118_modal_parity.py::test_every_mode_face_is_carried_by_a_generated_modal_options_roster
FAILED tier0/tests/test_eb118_modal_parity.py::test_every_modal_options_roster_is_carried_by_a_card_pool
```

### Re-run after deploy

```
python -m understudy.scenario run understudy/scenarios/deep-breath-modal-choice.yaml \
    --why "EB-150: Deep Breath's choose-one resolves both modes"
```

Green means: the screen opens, mode 0 pays 2 Encore, mode 1 spends 3 of a bank
of 5, and combat is still live after each.

---

## EB-151 — "Pearl Barrage seems to just do 5 damage all the time"

> "what does Pearl Barrage even do? Seems to just do 5 damage all the time."
> — [USER], 2026-08-26

### What the harness found: the card is correct

Two scenarios were written and both **passed on the buggy build 0.2-1159**,
before any change was made:

```
scenario: pearl-barrage-cost-ladder  (KLEEMOD-KOKOMI)
PASS: 5 expect step(s) held
```

```
scenario: tide-of-names-cost-ladder  (KLEEMOD-KOKOMI)
PASS: 2 expect step(s) held
```

The Pearl Barrage run, step by step: it exhausted **Coral Guard (cost 1)** and
took Twig Slime (S) from 8 to 0 — a delta of **8**, which is 5 + 3×1. It then
exhausted **Gyorin Formation (cost 2)** and moved Leaf Slime (M) by **11**,
which is 5 + 3×2. The sibling, Tide of Names, exhausted Coral Guard and moved
**7**, which is 5 + 2×1.

So the ladder is exact, live, on the build he was playing. **There is no
arithmetic defect and nothing was changed in the code.**

The hypothesis recorded in the backlog — that the damage number is worked out
before the selection and never recalculated — is wrong, and the decompiled
source says why. `AttackCommand.Execute` asks the damage var for its value at
the moment the hit lands (`sts2src/MegaCrit.Sts2.Core.Commands.Builders/AttackCommand.cs:654`),
which is after the exhaust has already been recorded. Nothing is cached. A
"recalculate after the selection" fix would have been a no-op.

### So what did he see? Two candidates, both for him

**1. The number printed on the card never moves.** In hand, Pearl Barrage's
face shows **5**, always, and it will still show 5 after this branch merges.
The preview asks the same multiplier for its value, and outside an actual
resolution the multiplier honestly answers zero — there is no selection yet.
The card's text does say "Scales with the total cost of the cards you just
Exhausted", but the big number next to it, the one a player actually reads,
sits at the base and never climbs.

**2. The natural fodder is free.** The damage is priced off the *printed cost*
of whatever gets exhausted, and a live Kokomi hand fills up with conscripted
units that cost 0. Exhausting one of those pays exactly 5 — correctly, every
time. A player who feeds the card its cheapest cards will see 5 for the whole
fight and be right about what he saw.

Both are legibility/design questions, not engineering ones, so they are left
for [USER] rather than settled here. As a numbered list:

1. Leave both cards exactly as they are; the scenarios now stand as proof the
   scaling works, and the confusion was a one-off.
2. Change what the face previews, so the number on the card climbs as the hand
   changes rather than sitting at the base. (This is a real piece of work: the
   preview would need a plausible victim to price itself against, and picking
   one is a design decision, not a derivation.)
3. Change the card's text so the printed 5 reads as a floor rather than as the
   damage — e.g. lead with the scaling clause instead of trailing it.
4. Change what the card scales on, so the common fodder is not worth zero.

Option 4 moves numbers and is frozen under R213 regardless; it is listed
because it is the option that actually addresses "all the time", not because it
can be taken today.

### Re-run after deploy

Neither needs a re-run to prove the fix — there is no fix. They are kept as
standing regression proof and can be re-run any time:

```
python -m understudy.scenario run understudy/scenarios/pearl-barrage-cost-ladder.yaml \
    --why "EB-151: Pearl Barrage's cost ladder, 8 at cost-1 and 11 at cost-2"

python -m understudy.scenario run understudy/scenarios/tide-of-names-cost-ladder.yaml \
    --why "EB-151: the sibling reads the exhausted cost too, 7 at cost-1"
```

---

## EB-152 — Kokomi's Burst cards print no label

> "Klee's cards that give Burst energy are labelled, but Kokomi's are not."
> — [USER], 2026-08-26

### The cause

He is right, and it was one predicate.

Cards carrying the `skill_tag` tag grant 5 Burst Energy when played. That
payment is made by the engine for **any** character with a Burst meter — Klee,
Furina and Kokomi all have one. But the line that prints "Burst +5" on the
card's face was gated to rows on **Klee's sheet only**
(`tools/gen_klee_cards.py`, the old `_is_klee_row` predicate). The gate was
deliberate when it was written — the ruling that added the line was scoped to
Klee's fifteen cards — and its own docstring said the extension "is the same
legibility argument and is deliberately NOT taken here". EB-152 is the ruling
it was waiting for.

Fourteen faces collected a real 5 Burst Energy and said nothing about it:
thirteen of Furina's, and Kokomi's `bake_kurage`.

Worth writing down, because it is not what the backlog row assumed: there is
**no Burst keyword and no Charge keyword** anywhere in the mod, and no
op-to-keyword mapping in the generator at all. The "label" Klee's cards carry
is a printed line of card text plus the `Elemental Skill` badge, which comes
from the same `skill_tag` tag by a separate route. Kokomi's Charge-granting
cards already print "Gain N Charge" in gold; what they lack is a badge, and
minting a new named keyword for Charge would be a design decision with loc
consequences (a keyword with no title row renders its raw key on screen, which
has shipped live twice — that is EB-155). So this fix does the Burst half,
which is what was reported, and leaves the Charge badge alone.

### The red run, verbatim

The new lint, run against the generated faces as they ship in 0.2-1159:

```
FINDING: SILENT BURST: 'bake_kurage' (kokomi-cards.yaml) carries `skill_tag`, so playing it pays
         5 Burst Energy -- and BakeKurage's face never says so. Expected '[gold]Burst[/gold] +5.'
         in the description; got 'Summon [gold]Bake-Kurage[/gold] for {KurageTurns:diff()}
         turn{KurageTurns:plural:|s}. Gain 1 [gold]Charge[/gold].'.
FINDING: SILENT BURST: 'dress_rehearsal' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'flood_of_emotion' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'full_ensemble' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'gentilhomme_usher' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'grand_gala' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'high_tide' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'mademoiselle_crabaletta' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'many_waters_melody' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'matinee_performance' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'overflowing_hospitality' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'rain_of_roses' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'salon_debut' (furina-cards.yaml) ...
FINDING: SILENT BURST: 'surintendante_chevalmarin' (furina-cards.yaml) ...

14 finding(s).
exit=1
```

and after the fix:

```
burst legibility OK: 29 skill_tag card(s) print the reading, of 29 tagged sheet row(s)
and 287 card class(es) read
```

### The fix

1. `tools/gen_klee_cards.py`: the sheet gate is gone, so every card that pays
   the Burst prints that it does. The old predicate was deleted rather than
   left unreferenced.
2. Regenerated: fourteen card files gained the line. No number moved anywhere,
   so R213's freeze is untouched.
3. New lint `tools/lint_burst_legibility.py`, registered on the `ci` lane. It
   checks both directions: a tagged card that does not print the line, and a
   card that prints the line without the tag (a face promising Burst nothing
   will pay).
4. Its test in `tier0/tests/test_sheet_lints.py` forces both failures on
   synthetic data — no probe file is ever written into the live tree.

Nothing is owed in the Python sim: it renders no card text at all, so there is
no second copy of this string to keep in step.

### Re-run after deploy

The check is a lint, not a live run, so it is already gated on every push:

```
python tools/lint_burst_legibility.py
```

Eyes-on after deploy is still worth one minute: Bake-Kurage should now read
"… Gain 1 Charge. Burst +5." on its face.

---

## What is owed

- One attended run of `deep-breath-modal-choice.yaml` from the primary
  checkout, after this branch is merged and a build is deployed. That is the
  green half of EB-150 and the reason its backlog row is not closed here.
- A decision from [USER] on the EB-151 list above.
- The three backlog rows (EB-150, EB-151, EB-152) are deliberately left open.
