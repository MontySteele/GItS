# Varka Hydro check, 2026-10-10

This round checks the Hydro paper (`review/active/varka-hydro-payoffs-2026-10-10.md`) and the new Converging Winds (#1048).
- Two whole-run Sonnet seats, each forced to a Barbara start (`--varka-knight hydro`).
- Build 0.2.4779+next. Embark `20261010-175608`.
- The packet and records are in the session scratchpad (`varka-hydro-r1/`), which is gitignored.

## Result

| Seed | This round | varka-r3 (per-act, own Knight) |
|---|---|---|
| CYHZM9S0VPW6 | floor 48, the Queen (died by 1 HP) | won |
| R41TX5Q0ZQYN | **won** | won |

## The paper's three lines

All three are **ungraded.**
- **Drafting:** Tidal Bulwark and Whisper of Water were each offered once and passed. Neither appeared in a shop.
- **Bulwark's damage:** no deck held it, so its 15+ hit can't be checked.
- **Whisper's retention:** no seat mentioned Whisper or Blur, so a misread can't be checked.
- Two seats over two runs is too few offers to grade. The Hydro take rate was 2 of 10 (20%): the starting bundle's Gleeful Songs, and Rippling Guard.

**Converging Winds (6 [8] to ALL per Swirl) landed.**
- Lane 1 took it at the act-1 boss and played it in 12 fights.
- That lane's best turn of the run was Converging Winds+ with Gale Sweep: 39 damage in one turn, killing the three-part Decimillipede elite in two cards.
- Its damage is credited inside `(Swirl)` in telemetry, not on its own line.

**Block and HP**, on the same two seeds as varka-r3:
- Block a turn rose in all three acts: 8.3 / 11.1 / 10.6, against 3.8 / 4.0 / 9.0.
- Total HP lost fell: 96 / 154 / 207, against 156 / 211 / 228.
- Neither new Hydro card was drafted, and the seat format also changed, so these numbers are not evidence for the paper.

## Defects and legibility (Claude checks and fixes the real ones)

- Four Winds' Ascension: the board number disagrees with the written text (lane 1). **By design:** the board folds Oath, Strength and Weak into the number, and the page prints a `Written:` line with a note saying the board's number is the one that lands (`understudy/blindplay_render.py`, `_render_card`). The seat read it correctly.
- An Amber switch turns off Hydro Oath scaling, and it shows only after the play as "Hydro Oath (left)" (lane 2). **Already covered:** the hand row reads "Knight, Pyro." (#1032) and the Knight note says playing one makes its element your current element (`understudy/blindplay_notes.py`). No change.
- Wolfpack's exhausting copy is told apart from the original only by "(1)" and "(2)" (lane 2). **Fixed:** where copies of one name differ, the one that Exhausts reads "(exhausts)" beside its number.
- The Four Winds' card added by the relic is missing from the deck list (lane 1). **By design:** Boreas's Fang makes it inside the fight (`Relics/BoreasFang.cs`, `AddGeneratedCardToCombat`). The note under it now adds "It is not in your deck."
- Short Circuit discards without asking (lane 2). **Base game:** it uses the same discard chooser as Concentrate. With 2 or fewer other cards in hand there is no choice to make, so it discards them all (fight 22, a hand of 2).
- **Checked as base game:**
  - The Gambling Chip prompt at the start of each fight.
  - Crab Rage's Block duration.
  - Shrink in lethal math.
  - Windborne Resolve called dead by one seat. The r3 seats called it a Block engine.

## Next

**No further Varka seat round.** The Hydro cards go to [USER]'s run, which is a better reader than two more seats that may never see them. In that run, watch two things:
- Is Tidal Bulwark offered and worth taking?
- Does Whisper's one-turn Block read clearly?
