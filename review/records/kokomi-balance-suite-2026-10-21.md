# Kokomi Balance suite, 2026-10-21

Build: main 24c3bd45c (0.2.6111), the balance audit (#1512,
`review/active/kokomi-next-2026-10-19.md`, [USER]: "Agreed all around"):
Princess of Watatsumi's Plan 5 [8] x3 (was 3 [5] x5), War Banner's upgrade
Block only, Sea Glass Harvest reads the Hand only. Also new since the finish
round (2026-10-19): the Casket pays only for Planning (#1506), Treatise costs 1
and Shoal of Spears counts Stings and Wards (#1508). Five Sonnet 5.5 seats,
whole runs, A0, the five suite seeds, all drafting freely. Lane 3's first seat
was refused its lane wrapper by the permission classifier and never played; a
second seat played the lane with the two direct commands.

| Seed (base character) | End floor (cause) | Finish round (10-19) | Base |
|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | 17 (Soul Fysh, act 1 boss) | 48 | 48 |
| CYHZM9S0VPW6 (Silent) | 33 (Knowledge Demon, act 2 boss) | won | 48 |
| DJCAV76ZKAUN (Defect) | 48 (Test Subject, form 2) | 48 | 48 |
| YEWA0B7AVE45 (Necrobinder) | 45 (Globe Head) | won | 46 |
| R41TX5Q0ZQYN (Regent) | 39 (Owl Magistrate) | 39 | 48 |
| **All** | 36.4, 0 wins | 46.2, 2 wins | 47.6, 0 wins |

## Against the base five (normal fights)

`tools/telemetry_report.py --character Kokomi --character base5 --since
2026-10-21T01:30` with the five baseline run instances and
`--baseline-since 2026-10-05 --baseline-until 2026-10-06`:

| Act | dmg/turn (base) | ratio | HP lost % (base) | ratio | Finish round ratios |
|---|---|---|---|---|---|
| 1 | 18.5 (19.6) | 0.94 | 7.5 (4.7) | 1.61 | 0.95 / 0.80 |
| 2 | 29.0 (33.0) | 0.88 | 15.0 (12.8) | 1.17 | 0.96 / 0.90 |
| 3 | 35.7 (47.0) | 0.76 | 17.3 (12.1) | 1.43 | 0.68 / 0.89 |

Every act is outside the 15% bar, low on damage and high on HP lost. Her Block
a turn is above base in every act (3.0 / 7.5 / 12.3 against 2.2 / 2.9 / 7.5);
her fights run a turn longer (3 / 4 / 4 turns against 3 / 3 / 3).

## The predictions

- **Princess's damage share falls:** not testable against the finish round,
  where no seat took Archaic Tooth. Here 13 plays, 4.4% of her damage, 57 a
  play in act 2. In [USER]'s run (before the change) it was 17%.
- **War Banner's Strength per play halves when upgraded:** built; 39 plays, no
  seat reported Strength scaling from it.
- **Sea Glass Harvest's Energy from Statuses falls:** no seat built around it.

The three changes fired rarely, so they explain little of the drop from the
finish round. Act 1 HP lost doubled (3.8% to 7.5%), which is where the
Casket's change (no Block for a Plan card played face-up) lands first; the
rest is within what two rounds on the same seeds have differed by before.

## What the seats said

- Real decisions: Plan or play one card (Oath, Stings), planned AoE Stings
  slipping under Exoskeleton's per-hit cap, Grand Design with Change of Plans
  as a draw engine, Kelp Wall and Brine Sting set up two turns out.
- Losses: late hands with no Block card against multi-hit enemies (lanes 4, 5),
  Knowledge Demon's curses (lane 2), a Plan written into Soul Fysh's
  Intangible turn (lane 1).
- Never again: Tidal Surge (lane 1 read it as Ethereal), Kurage Bloom,
  Treatise, Slack Water.
- To check: Grand Design's chooser closed after one pick on some turns
  (lane 5); lane 1 saw Bubble Ward twice in a few turns with one copy.

## [USER]'s run (2026-10-20, before the change)

Won at A0 with 18 relics; normal fights 1.1 / 5.5 / 1.1% HP lost against base
4.7 / 12.8 / 12.1, damage a turn 16.7 / 29.8 / 48.0. The seats and [USER] read
her in opposite directions: for a strong player she is easy, for a seat she is
under base.
