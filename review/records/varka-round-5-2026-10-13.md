# Varka round 5, 2026-10-13: five seats on the Balance build

Five Sonnet seats at A0 on build 0.2.5344. This is the first play of the new
starter (Four Winds' Ascension plus a rolled Knight; Boreas's Fang makes the
Knight's element current) and of the pool audit (#1242, #1243). Raw seat
records stay in the session scratchpad (gitignored by rule). Base yardstick:
the base-five Sonnet baseline went 0/5 at A0, all dying in act 3
(`review/records/base-five-baseline-2026-10-05.md`).

## Results

| Lane | Knight | Result | Killer |
|---|---|---|---|
| 1 | Lisa | **won**, 13/87 HP | |
| 2 | Barbara | lost, floor 40, 3 HP | Flail, Spectral and Magi Knight (act 3 elite) |
| 3 | Kaeya | **won**, 34/121 HP | |
| 4 | Barbara | lost, floor 48, turn 5 | Queen + Torch Head (act 3 boss) |
| 5 | Lisa | lost, floor 40 | Mecha Knight (act 3 elite) |

Two wins, every run reached act 3, and both act 1 and act 2 bosses fell in
every lane. That is above the base five's 0/5. Three lanes hit refusal stops
from their own batched commands after a fight-ending play and were continued
by a fresh seat. Each run took 75 to 95 minutes, slower than the usual 50 to
60 because build agents were running full test suites at the same time.

## What played well

- **The new starter teaches itself.** Knight aura, then Four Winds' Ascension
  Swirl, by turn 2 in every lane. The Retain made holding Ascension for an
  aura a real choice (lanes 3, 4, 5).
- **Ascension+ is the carry.** 99 on the final boss (lane 3), 106 in a turn on
  the Mecha Knight (lane 4).
- **Audit cards:** Chain Lightning (0 cost) was good in all four lanes that met
  it. Downburst and Kindled Edge+ were strong in three. Eula played well
  (lanes 1, 3).
- **Reactions:** Electro-Charged poison carried three elites in lane 4 and
  finished fights in lanes 2 and 3. Frozen halved attacks (lane 2). Reaction
  preview lines were legible (lane 1).
- **Knights as an engine:** Knights' Roll Call+ and The Order Answers (lane 1).

## What did not

- **Block is thin in act 3** (lanes 2, 4, 5). Block cards give 5 to 8. Act 3
  elites hit for 25 to 43, and the Queen's permanent Frail held lane 4 to
  about 17 Block a turn. This applies to the base cast too, but three of five
  lanes named it.
- **Hidden element changes** (lanes 3, 4, 5). Kaeya, Barbara and Short Circuit
  switch the current element and silently lower Ascension's Oath. A
  reaction that uses up an aura leaves a later Swirl card with nothing to
  Swirl, and the screen does not say the aura is gone.
- **Twin Gales** pays nothing extra when the Swirled element is the current
  one (lanes 1, 2). It was lane 2's worst card twice.
- **Dead cards:** Weathervane, Windborne Resolve (lane 3). Blazing Charge and
  Kindled Edge with no Pyro Oath (lanes 3, 4).
- **Ascension at 0 Oath** is 10 damage for 2 Energy until about fight 3
  (lanes 1, 3).
- **Chain Lightning's discard** comes before its damage, does not print what it
  discarded, and picks itself when two cards remain (lanes 2, 4).

## What to change

1. **Show element changes on the card** (main, UI only). A card that switches
   the current element shows the damage change on Ascension and other
   Oath-reading cards in hand. Swirl cards whose target has lost its aura read
   "No aura".
2. **Chain Lightning prints what it discarded** (main, log only).
3. **Eula: Icetide Vortex is a damage card printed as a Skill** (lane 1). The
   other damage Knights are Attacks. This changes Strength scaling, so it goes
   to `varka-next`.
4. **Twin Gales: a matched element pays twice** (`varka-next`).
5. **Act 3 Block** is a pick for [USER], not a change. The defence paper
   (#1126) settled his Block, and the base cast dies to the same act 3 checks.

Not changing: Ascension's 0-Oath opening (the starter is meant to be weak and
Retain is the answer), Weathervane and Windborne Resolve (one lane each).
