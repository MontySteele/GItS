# Furina Balance suite 4, 2026-10-16

Build: `furina-next` 6620b776d (0.2.5751+next). The change set under test is
paper 3 (`review/active/furina-next-3-2026-10-16.md`, both picks (a)):
- a Repay that cannot return HP gains 1 Block per HP instead;
- Pneuma Refrain Repays 4 [6];
- Endless Waltz Repays 2 first;
- Fontaine Teardrop doubles that floor;
- Salon Solitaire gains 1 Block a turn when nothing is drained.

`main` was merged in first (#1379). Seeds, seats and grading are the same as
suites 1 to 3: A0, one Sonnet 5.5 seat per lane for the whole run, and normal
fights compared with the base five's counted runs
(`review/records/base-five-baseline-2026-10-05.md`).

| Seed (base character) | Suite 4 end floor (cause) | Suite 3 | Suite 2 | Suite 1 | Base |
|---|---|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | 33 (The Insatiable, act 2 boss) | 39 | 24 | 39 | 48 |
| CYHZM9S0VPW6 (Silent) | **48, WON** | 48 | 48 | 44 | 48 |
| DJCAV76ZKAUN (Defect) | 40 (Soul Nexus, act 3 elite) | 31 | 24 | 17 | 48 |
| YEWA0B7AVE45 (Necrobinder) | 33 (Knowledge Demon, act 2 boss) | 48 | 33 | 48 | 46 |
| R41TX5Q0ZQYN (Regent) | **48, WON** | 48 | 33 | 33 | 48 |
| **Mean** | **40.4** | 42.8 | 32.4 | 36.2 | 47.6 |

**These are the first two won runs in four suites;** the base five won none
on these seeds. There was no crash or refusal stop. Both act 2 deaths were
to forced status cards:
- The Insatiable put six Frantic Escape into a 26-card deck.
- Knowledge Demon's second pick, Sloth, capped her at 3 cards a turn while
  the boss was at 87 of 379.

Normal fights compared with base. The report command is the one from suite
3, with `--since 2026-10-16T17:45`. Medians, as in suite 3:

| Act | n | dmg/t (base) | ratio | HP % lost (base) | ratio | Suite 3 ratios |
|---|---|---|---|---|---|---|
| 1 | 35 | 18.7 (19.6) | 0.95 | 9.0 (4.7) | 1.92 | 1.01 / 2.00 |
| 2 | 25 | 26.7 (33.0) | 0.81 | 20.5 (12.8) | 1.60 | 0.82 / 1.30 |
| 3 | 14 | 39.5 (47.0) | 0.84 | 24.4 (12.1) | 2.01 | 0.95 / 1.06 |

Means per normal fight, from scratch `furina-gap/s4.py`, with suite 3 in
brackets:

| Act | Block a turn | Damage taken a turn | HP lost a fight |
|---|---|---|---|
| 1 | 4.15 (3.13) | 3.79 (4.23) | 8.9 (9.7) |
| 2 | 8.77 (6.59) | 5.61 (6.55) | 14.6 (16.9) |
| 3 | 13.97 (9.80) | 6.69 (6.78) | 17.5 (16.1) |

Base is 2.69 / 1.77 / 5.6 in act 1, on the same incoming (8.3 against 8.2).

## The predictions, graded

1. **Net HP lost per normal fight: act 1 at most 1.60 of base, act 2 at most
   1.15: MISS.** The medians give act 1 at 1.92 and act 2 at 1.60. The means
   are better, act 1 at 1.58 and act 2 at 1.35, but they still miss act 2.
   Act 2's median got worse than suite 3 (1.30), yet the mean HP lost per
   fight fell from 16.9 to 14.6. Five runs cannot separate those two
   readings.
2. **Act 1 damage taken a turn at most 3.5, with the record naming the
   Block the Repay floor gave: MISS** (3.79, from 4.23 in suite 3 and 4.4
   over suites 1 to 3). The floor's Block shows up in the seats' own turns:
   - Hymn "Repay 0 gave 3 Block" helped make 14 Block, which exactly blocked
     a Bowlbug and stunned it (lane 3).
   - Pneuma "Repay 0, only block" (lane 5).
   - Waltz printed "Repay 0: gain 2 Block" (lane 2).

   No telemetry key separates floor Block from other Block.
3. **Act 1 Block a turn up by at least a quarter from 3.2: PREDICTED**
   (4.15, +30%). Block rose in every act, by 33% in act 2 and 43% in act 3.

## What the seats said

The records are in scratch `seats/archive/furina-s4/l1..l5`.

- **The loop works, and both wins were cash-outs.** Lane 5 hit Aeonglass
  for 277 from 17 HP with Let the People Rejoice at 91 Fanfare. Lane 2 won
  the Knowledge Demon fight at 24 HP through Soloist's Solicitation+.
- **The floor is legible.** The seats read "Repay 0: gain N Block" as
  printed. Lane 3's "Usher Drain + Clean Slate: Block 19 for 0 net HP" was
  "the neatest thing in the kit".
- **The Repay cards are still rated low when nothing is drained.** The
  NEVER AGAIN cards were Endless Waltz ("one Repay a turn makes it a
  Strike"), Crowd Favorite, Critics' Darling, Verdict of the Oratrice and
  Façade. Waltz is the only Repay card among them; Hymn and Pneuma Refrain
  were the suite 3 complaints and no seat named them this time.
- **The Drain buffer lines are still dense.** Three seats had to watch HP
  climb after combat to learn that the buffer returns.
- **Page lines worth a fix (BACKLOG):**
  - Ebb and Flow's "Repay 0: gain 2 Block" never showed as live Block
    (lane 4).
  - Archaic Tooth's All the World's a Stage+ loses Rising Applause+'s
    Retain (lane 5).
  - Clorinde's Night Vigil reads as if it covers her own hit (lane 5).
  - After Ousia flips, "Pneuma" cannot be played by name that turn
    (lane 3).
  - Tender showed "Tender 0" while stacking (lane 1).

## Reading

Paper 3 did what it was built to do to Block: up by a third in every act,
with damage taken down in acts 1 and 2. It did not bring her HP loss near
base. Act 1 is still about 1.6 to 1.9 times base, depending on mean or
median, so both HP predictions miss.

The end floor mean fell 2.4. That drop is two act 2 deaths to forced status
cards (Frantic Escape, Sloth) on seeds that reached 39 and 48 in suite 3.
Meanwhile two runs won outright and the Defect seed went from 31 to 40. With
five runs, the floor mean cannot tell paper 3 from suite 3, and the per-fight
numbers lean slightly better.

## Picks

1. **What to do with furina-next.**
   - **(a) Default:** promote paper 3 to main. Block is up in every act,
     damage taken is down in acts 1 and 2, and two runs won. The HP gap goes
     to a later paper, which looks at Drain's own cost: the seats call Drain
     "free but dangerous", and HP lost is what still misses.
   - (b) Do not promote; run paper 3 again on fresh seeds first.

Raw transcripts: `review/qa/blindplay/` (local, gitignored).

**Ruled 2026-10-16.** [USER]: "Awesome! Agreed on promoting the build". Pick 1 (a).
