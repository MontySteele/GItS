# Kokomi Balance suite 3, 2026-10-21

Build: main 5582d0843 (0.2.6119), the boss ramp and Casket pass
(`review/active/kokomi-next-2026-10-19.md`, "Boss ramp and Casket"): Kurage
Vanguard deals 2 more each turn, the Casket pays 2 Block a counted play
(Watatsumi 3), on top of suites 1 and 2's changes. Five Sonnet 5.5 seats,
whole runs, A0, the five suite seeds, all drafting freely. This is the last
suite on the pre-audit cards; the taste audit
(`review/active/kokomi-taste-audit-2026-10-21.md`) changes ten cards next.

| Seed (base character) | End floor (cause) | Suite 2 | Base |
|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | 33 (The Insatiable, act 2 boss) | won | 48 |
| CYHZM9S0VPW6 (Silent) | 33 (Knowledge Demon, act 2 boss) | 33 | 48 |
| DJCAV76ZKAUN (Defect) | 30 (Hunter Killer, act 2 elite) | 33 | 48 |
| YEWA0B7AVE45 (Necrobinder) | 44 (Frog Knight, act 3) | 33 | 46 |
| R41TX5Q0ZQYN (Regent) | **won** | 33 | 48 |
| **All** | 37.6, 1 win | 36.0, 1 win | 47.6, 0 wins |

## Against the base five

`tools/telemetry_report.py --character Kokomi --character base5 --since
2026-10-21T17:00 --tempo`, the five baseline run instances, baseline window
2026-10-05.

| Act | dmg/turn (base) | ratio | HP lost % (base) | ratio | bar |
|---|---|---|---|---|---|
| 1 | 18.8 (19.6) | 0.96 | 6.2 (4.7) | 1.34 | outside (HP) |
| 2 | 29.0 (33.0) | 0.88 | 12.5 (12.8) | 0.97 | within |
| 3 | 54.0 (47.0) | 1.15 | 8.4 (12.1) | 0.69 | outside (9 fights, two lanes) |

Not promoted: act 1 HP lost is a third over base, and act 3 rests on two
lanes.

## The predictions

- **Boss damage a turn up (Kurage Vanguard ramp):** yes. Act 2 bosses 40.9 a
  turn over 8.5 turns (suite 2: 28.5 over 9; base 58.4 over 7). Kurage
  Vanguard dealt 70 to 150 a play; lane 4 called it the engine of its run.
  Still two of the four act 2 boss fights were lost.
- **Act 1 HP back toward base (Casket 2):** partly. 1.88 to 1.34 of base.

## What the seats said

- Best turns: playing a Sting now or Planning it was the fork most turns;
  Plan chains into Pearl Current and Grand Design cleared the multi-enemy
  fights; Breakwater and Press the Advantage made Plans-waiting a sequencing
  puzzle (lane 4); lane 5's win ran on Watchful Shoal, Shoal Call and
  Casket Block.
- Losses: Knowledge Demon's debuffs and healing (lane 2), Frantic Escape
  clogging a 23-card deck (lane 1, The Insatiable), Tender under 20 HP
  (lane 3), a misread lethal (lane 4).
- Weak cards: Following Current ("never again", lane 4), Treatise (lane 3),
  Resolve of Watatsumi under Tender. The last two are changed by the audit.
- To check (not yet confirmed as bugs): a Plan written before Soul Fysh's
  Intangible hit for 1 with no warning on the Plan page (lane 1); Press the
  Advantage's reaction preview said "deals no damage" and it dealt damage
  (lane 1), and lane 4 could not tell if its printed number included
  Vulnerable; the hand limit still drops Stings (lanes 2, 5); a Grand Design
  plan gave no Casket Block (lane 5).

## Next

Deploy the taste audit and its visuals, then suite 4 on the same seeds.
