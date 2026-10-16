# Spiral Abyss round 2, 2026-10-14

The second seat round on the Spiral Abyss mode: five solo seats (one per
character), a base-game Ironclad control and two co-op pairs, all blind Sonnet seats at A0 on build
0.2.5414. Asked by [USER]: "a few co-op seats on Spiral Abyss, time
permitting ... Partly to see how co-op goes, partly to see how the new
modifiers affect balance." Raw transcripts are not kept; the seat records are
in the session scratchpad (`seats/archive/`).

## Results

| Seat | End | Blessings taken (act 1 / 2 / 3) |
|---|---|---|
| Kokomi solo | **Won**, floor 48, 14/85 | Wavering Moon / Resonance / First Strike |
| Varka solo | **Won**, floor 48, 48/80 | Battle Rhythm / Overflow / Vigor of the Abyss |
| Furina solo | Lost to the final boss (Queen), floor 48 | Battle Rhythm / Vigor / First Strike |
| Klee solo | Lost to the act-1 boss (Waterfall Giant), floor 17 | Battle Rhythm |
| Yae solo | Lost in act 1, floor 11 | Vigor of the Abyss |
| Ironclad (base control) | Lost to the final boss (Test Subject), floor 48 | First Strike / Vigor / Resonance |
| Co-op Klee + Varka | Lost to the final boss (Aeonglass), floor 45 | Vigor / Overflow / Moonlit Spring |
| Co-op Furina + Kokomi | Lost to the act-2 boss (The Insatiable), floor 31 | Battle Rhythm / Moonlit Spring |

Three of five solo seats reached the final fight and two won; the base
Ironclad control also reached it, so the mode does not weigh on the modded
kits more than on a base character. That is above
tonight's plain-mode Kokomi round (1 in 5) and in line with the 2026-10-12
Abyss solo (floor 48). The Blessings roughly pay for the Shadows; nothing
here says the mode is much harder or easier than a plain run.

## What played well

- **Passing a Shadow is a real choice once it is understood.** Seats chose
  around Riptide and The Clock.
- **Overflow and First Strike are the big Blessings.** Overflow doubled
  Melt, Overloaded and Vaporize, giving Klee's biggest turns (45 on Infested
  Prism). First Strike doubled a planned Masterstroke to 84 on the final
  boss's first turn (Kokomi) and a Cleansing Torrent that wiped three Scrolls
  of Biting (Furina).
- **Co-op elements work together.** Klee's Pyro auras turned Varka's Swirls
  and Cryo flips into Melt and Overloaded; Fischl's Electro on Furina's Hydro
  gave Electro-Charged.
- No crash in eight runs. The 2026-10-12 round's vote and chest fixes held.

## What did not

- **Every seat read the Shadow printed beside a Blessing as the one it would
  get.** By design the enemies take one from the passed options; all eight
  runs met this, and two seats guessed wrong. **Fixed** (#1274): the page
  says it in its top line and names the Shadow taken after the pick; your
  "SHADOW" band is kept.
- **Fatui Skirmishers' icon showed on every enemy** though its Plated Armor is
  elites and bosses only, and **Abyss Mage Shield** likewise; display only.
  **Fixed** (#1274).
- **Riptide snowballs in act 2** (Insatiable to Strength 14, Hunter Killer 8)
  and ended the Furina + Kokomi pair. Watch, no change yet.
- **Moonlit Spring** read as weak solo ("8 HP per fight barely mattered") but
  strong in co-op. No change.
- **The Clock and Abyss Herald stack** across acts on a Whole-run choice
  (Varka saw both in act 3). As built; worth a line on the page.
- **Two refusal stops** ended a co-op seat when the partner's Bombs ended a
  fight mid-batch. **Fixed** (#1268): a command refused because the fight
  ended under it no longer counts.
- **Death Blow read as "you would take 0"** after killing the Waterfall
  Giant (two seats). **Fixed** (#1278).
- The co-op page said "Klee's vote did not reach this game" when the vote had
  synced. **Fixed** (#1268); the mod was right.

## What to change

1. Deploy #1268, #1274 and #1278 with the morning build.
2. Watch Riptide and The Clock in the next Abyss round; no number moves on
   one round.
3. The page names a stacked Whole-run Shadow ("still in force from act 1").
