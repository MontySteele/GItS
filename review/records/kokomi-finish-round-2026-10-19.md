# Kokomi finish round, 2026-10-19

Build: main 0.2.6066, the finish pass (`review/active/kokomi-cards-2026-10-18.md`
sec. 7): Battle Formation at 2 with the draw on upgrade, and Grand Design
drawing per Plan. Five Sonnet 5.5 seats, whole runs, A0, on the five suite
seeds. Lanes 1–3 drafted freely. Lane 4 started with Tidal Riposte and lane 5
with The Shape of Water. Each answered: what was the winning turn, what did
you give up for it, and did you lose a fight to running out of Block?

| Seed | End | Lost to Block? |
|---|---|---|
| 30KMHAVG9SMQ | 48, Test Subject (form 2) | yes, ~4 Block against 60 |
| CYHZM9S0VPW6 | **won** (Queen, at 3/83) | no; three close fights |
| DJCAV76ZKAUN | 48, Test Subject (form 2) | yes, 24 Block against 42 |
| YEWA0B7AVE45 (Tidal Riposte) | **won** (at 9/80) | no |
| R41TX5Q0ZQYN (Shape of Water) | 39, Frog Knight (act 3) | yes, ~10 Block against 31 |
| **All** | 46.2 mean, 2 wins | v3 round: 0 wins of 7; v2: 1 of 5 |

## The defence trigger: not met

The paper's trigger was "HP lost per normal fight more than 1.5 above the
base characters'". Normal fights against the base five (2026-10-05 window,
`tools/telemetry_report.py --character Kokomi --since 2026-10-19T21:40`,
112 fights):

| Act | Damage a turn vs base | HP lost vs base |
|---|---|---|
| 1 | 1.01 | 0.43 |
| 2 | 0.96 | 0.92 |
| 3 | 0.67 | 0.85 |

She loses less HP than base in normal fights in every act, so Ward stays a
draw. The three losses came at act-3 bosses and elites: her act-3 boss
fights lost 83% of max HP (base: every base run also ended in act 3, none
won). Act-3 normal-fight damage at 0.67 is the number to watch; v3 had it at
0.92, so 27 fights is a watch, not a finding.

## What played well

- Plan against direct play was the decision in every seat, most of all
  Opening Gambit or Nereid's Ascension doubling a Plan. Nereid's carried the
  act 2 boss in lane 2.
- **Tidal Riposte (lane 4) was the best card in its deck.** It made "block
  fully or take it" the decision of nearly every enemy turn.
- **The Shape of Water (lane 5)** did 28–50 a turn once Stings were in hand,
  and was dead without them.
- Plan damage went through Flutter, Thorns and the player's Weak, and the
  seats used that.

## What did not

- **Block at the act-3 boss.** Every seat drafted damage first. Test
  Subject's form 1 gains Strength whenever a Skill is played (planning one
  counts), which taxes her Block Skills.
- **One loop got automatic.** Everlasting Moonglow plus Tide Wall+ as the
  first Plan gave 23–99 Block a turn (lane 4). Lane 4 also wanted more cards
  that read intent; Tide Wall was the only one.
- **Rarely or never taken:**

  | Card | Offered | Taken |
  |---|---|---|
  | Battle Formation | 2 | 0 |
  | Grand Design | 5 | 1 (played 6 times, lane 5) |
  | Gorou — Crystal Collapse | 7 | 1 |

  Seats called these dead: Sea Glass Harvest, Sangonomiya's Orders, War
  Council, Crystal Collapse ("can't be played until a Companion has been
  played").

## Screen and possible bugs (to check, not yet verified)

1. Tamakushi Casket's text names "a Plan card or a Companion", yet every
   Sting gave 1 Block (lane 2).
2. The Shape of Water counts the token Sting but not Brine Sting, and its
   text does not say so (lane 5).
3. Tide Wall reads the intent when it is carried out, not when it is
   planned, and the text does not say so (lane 4).
4. Flank's Plan hit one of three bodies once after an intent changed (lane 3).
5. At Water's Edge's "first time each turn" is spent by Vanguard at the start
   of the turn, and nothing shows it spent (lane 3).
6. Planning an Attack voids Ripple Basin's Block (lane 1).
7. Red Mask and Bag of Marbles' combat-start Weak and Vulnerable did not show
   on several fights (lane 2).
8. Knowledge Demon's "choose a card" gives permanent debuffs, and the prompt
   does not say so (base game; lane 4).

## What to change

See `review/active/kokomi-next-2026-10-19.md`.
