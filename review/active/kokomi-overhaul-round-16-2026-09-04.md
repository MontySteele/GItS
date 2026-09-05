Status: OPEN (no pick; the defaults in §4 are applied)

# Kokomi round sixteen: a silent no-op, Vulnerable's two texts, and a preview that arrives a turn late

Written 2026-09-05. One blind Opus seat played the Plan kit on
`0.2.2614+proto` (rows on `docs/prototype-surface.yaml`), the first build
with the redesigned Tide Chart in the pool (`EB-478`, R257) and the
round-15 rows folded (`EB-467` to `EB-469`, `EB-461` neutral). Record:
`review/qa/kokomi-round-16-2026-09-04/opus-act1.md`. Prototype stage,
Guardrail-7. No pick.

## 1. The run in one paragraph

Seed `31AYS93P0SNJ`, Ascension 3. Five fights, five won, the Terror Eel
elite dying on action 120 of 120 with its reward unclaimed; floor 8, 46 of
80 HP, a 17-card deck. No refusals, no stalls. The redesigned Tide Chart
was not offered or drawn: its ninth non-draw, the first on the new text.

## 2. What the round found

**A non-Plan card played on the Bake-Kurage is a silent no-op that
reports success.** `play "Strike" on "Bake-Kurage"` returned ok, burned an
action and changed nothing: energy, discard and hand as before, "Nothing is
planned." A refusal listing the Plan cards in hand is the fix (`EB-480`).

**Vulnerable's two texts disagree, Weak's twin.** The status line says
"from Attacks", the glossary "every hit", and Kurage's Oath (a Skill) took
the 1.5x, so the glossary is right; the same one-sentence fix as `EB-469`
(`EB-481`).

**The reaction preview arrives a turn late.** It reads the board as it
stood at the last observe, so on the turn a card creates the aura the
next card would eat there is no preview, which is the turn the decision
is made; the seat's first Vaporize was found by subtracting HP after the
fight (`EB-482`). A Cryo hit on a Hydro aura three times never showed the
aura consumed; the glossary predicts the illusion, and the seat did not
file it as a bug because of that paragraph (`EB-410`, cited).

**Two page gaps.** The Smith screen shows the current face and never the
upgraded one, so Deep Current was upgraded on a guess (`EB-483`); Undertow's
folded face on a shop screen with no enemy could not say whether it deals 4
or 7 (`EB-484`). Printed intent numbers overstated damage taken three
times, each by the amount the seat had failed to Block, which reads as the
enemy's own Block-side arithmetic rather than `EB-461`'s multi-part case;
cited, not minted.

**What read true.** The Plan priced a card twice and the right answer
flipped with the board (fight 1 turn 4 against fight 4 turn 2); fight 3
turn 2 chained four decisions with the relic and the numbers predicted in
advance; turn one of fight one presented a real decision.

**The deck is two cards deep, a seventh round.** Eight of seventeen cards
were Strike and Defend, about one turn in three with no kit interaction.
R254 and R257 stand; Tide Chart's redesign is the answer on the table and
has not been drawn.

## 3. What the round did not test

The redesigned Tide Chart, a ninth non-draw; the boss. One run. Nothing
here is a strength reading.

## 4. Defaults applied (D and E), disclosed

- **`EB-480` to `EB-484` minted; `EB-410`, `EB-461` cited.**
- **The next Kokomi round grants Tide Chart** (E): the redesign has to be
  seen before the pool pass reads it, and nine natural runs have not drawn
  it.
