# Furina suite 5, 2026-10-23 (the upgrade census)

Build: `furina-next` 90e1fdbec (0.2.6203+next), after #1555: eight real
upgrades and Bring the House Down reflavoured
(`review/active/furina-next-3-2026-10-16.md`, "Upgrade census
(2026-10-23)"). Seeds, seats and grading as suites 1 to 4: A0, one Sonnet
5.5 seat per lane for the whole run, drafting freely. Raw records:
scratchpad `furina-1023/seat-laneN/record.md` (local).

| Seed (base character) | Suite 5 end floor (cause) | Suite 4 | Suite 3 | Base |
|---|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | 28 (Ovicopter, act 2) | 33 | 39 | 48 |
| CYHZM9S0VPW6 (Silent) | **48, WON** | won | 48 | 48 |
| DJCAV76ZKAUN (Defect) | 48 (Test Subject, act 3 boss, phase 3 at 118) | 40 | 31 | 48 |
| YEWA0B7AVE45 (Necrobinder) | 48 (Test Subject, act 3 boss, phase 3) | 33 | 48 | 46 |
| R41TX5Q0ZQYN (Regent) | 48 (Aeonglass, act 3 boss) | won | 48 | 48 |
| **Mean** | **44.0**, 1 win | 40.4, 2 wins | 42.8 | 47.6, 0 wins |

Four of five reached the act 3 boss, the most of any Furina suite. Normal
fights against the base five since 2026-10-05
(`tools/telemetry_report.py --character Furina --since 2026-10-23T02:30`):

| Act | n | Damage a turn, ratio | HP lost a fight (base), ratio |
|---|---|---|---|
| 1 | 36 | 0.99 | 10.3% (8.8%), 1.17 |
| 2 | 24 | 0.97 | 13.5% (14.9%), 0.91 |
| 3 | 21 | 1.06 | 22.8% (10.0%), 2.28 |

Acts 1 and 2 are at base. Act 3 is where she loses HP: two seats reached
Test Subject's last phase at 23 HP and lost there.

## The changed cards (offers taken, all five runs)

| Card | Offered, taken | Seen in play |
|---|---|---|
| The Masquerade | 8, 4 | Taken and played in three seats; "free Block from Drain" |
| Let the People Rejoice | 9, 3 | 12 plays, 55 to 80 damage a play, 153 upgraded |
| Tutti! | 15, 2 | Guest acts "without triggering Thorns or Enrage" |
| The Show Must Go On | 4, 3 | 36 Block from 47 Fanfare saved lane 2's Queen fight |
| Critics' Darling | 3, 2 | 16 plays |
| Showstopper, Ensemble Cast, Bring the House Down, Rainfall Overture | 3/3/2/2, none taken | not tested |

The four cards with the paper's biggest changes were never taken, so the
reflavoured Bring the House Down has no evidence either way yet.

## What played well

- **Banking Fanfare for one big turn** was the decision in every seat:
  Rising Applause+ on 35 banked killed the Obscura leader exactly; Let the
  People Rejoice and Thunderous Applause+ cleared whole groups (four
  Exoskeletons, the Decimillipedes).
- Reactions read from the preview line (Vaporize, Frozen).

## What did not

- **Act 3 bosses.** Lanes 3 and 4 met Test Subject's 300 HP phase at 23 HP;
  lane 5 lost to Aeonglass from 4 HP. No healing, and The Show Must Go On or
  Hold the Stage not drawn on the 45 and 47 damage turns.
- **Never again:** Beckon, Tearful Monologue, Soloist's Solicitation (weak on
  a low bank), Doubt, Commanding Gaze (its Vulnerable is lost to Artifact).
- **Unclear:** Hold the Stage spends Fanfare and so shrinks Freminet's act,
  which nothing says; a Repay with nothing drained becoming Block is easy to
  miss; Rising Applause prints "(Deals 0 damage)" in hand with no Fanfare;
  Plot Twist+ on an Artifact boss was taken by the Artifact.

## What to change

1. **Nothing on the cards yet.** The paper's graded effects for Showstopper,
   Ensemble Cast, Bring the House Down and Rainfall Overture need a round
   where they are drafted; the next Furina round briefs one seat toward a
   guest deck.
2. **Act 3 HP:** the 2.28 was mostly her own Drain (below). Not a card-pass
   item; the bar's reading is a pick (`QUEUE.md`, "Yae and Furina reads").

## Correction: the HP column counts Drain (read 2026-10-23)

[USER]: "Is her block too low? Is her block not scaling to act 3? Did the
seats draft all offense?" None of the three. The table's "HP lost" is
`hp_lost`, taken before the curtain call returns drained HP, so it counts
the HP Furina Drains herself on purpose. Fight rows since 2026-10-23T02:30
against the base five since 2026-10-05, normal fights, rows that carry
`hp_after_return` (median / mean, % of max HP):

| Act | HP lost as printed | Minus the Drain returned | Base five |
|---|---|---|---|
| 1 | 10.3 / 10.1 | 5.1 / 5.9 | 9.1 / 9.7 |
| 2 | 13.5 / 16.9 | 5.1 / 9.8 | 16.2 / 16.4 |
| 3 | 22.8 / 20.2 | 6.4 / 8.5 | 5.1 / 12.4 |

Block in act 3 normal fights (means): 52.9 a fight against the base's 32.6,
13.5 on turns with an attack coming against 10.2, and 10.1 unblocked a hit
turn against 12.6. Her fights run 4.2 turns against 3.4, so more attacks
arrive (70.9 a fight against 55.2). Her Block rises from 4.7 a turn in act 1
to 9.6 in act 3 (base 2.5 to 10.0). The seats drafted Usher, The Masquerade,
The Show Must Go On, Velvet Curtain and Hymn of Many Waters.

The act 3 boss killed 3 of her 4 runs that reached it, and 13 of the base
five's 20. Her real gap is lane 1, dead on floor 28 in act 2.
