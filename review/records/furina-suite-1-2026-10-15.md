# Furina Balance suite 1, 2026-10-15

Build: `main` f89d29e34 (0.2.5630), the build Furina moved to Balance on
(#1343); no `furina-next` change set yet, so this suite is her baseline.
Prediction graded: [USER]'s read of his finish-line run, written before the
suite: "Act 1 was pretty easy ... act 2 was very touch and I nearly died
several times - act 3 was pretty easy again as all of my power scaling caught
up."
Seeds, seats and grading: A0, one Sonnet 5.5 seat per lane for the whole run,
normal fights against the base five's counted runs on the same seeds
(`review/records/base-five-baseline-2026-10-05.md`).

| Seed (base character) | End floor (cause) | Suite 0 | Base | Act 1 dmg / HP | Act 2 dmg / HP | Act 3 dmg / HP |
|---|---|---|---|---|---|---|
| 30KMHAVG9SMQ (Ironclad) | 39 (Globe Head, act 3) | -- | 48 | 25.0 / 12.8 | 39.5 / 14.1 | 31.9 / 23.7 |
| CYHZM9S0VPW6 (Silent) | 44 (Mecha Knight, act 3 elite) | -- | 48 | 24.7 / 5.1 | 30.0 / 17.3 | 46.2 / 6.4 |
| DJCAV76ZKAUN (Defect) | 17 (The Kin, act 1 boss) | -- | 48 | 13.3 / 7.7 | -- | -- |
| YEWA0B7AVE45 (Necrobinder) | 48 (Test Subject, act 3 boss) | -- | 46 | 22.0 / 7.7 | 21.8 / 10.3 | 40.5 / 22.9 |
| R41TX5Q0ZQYN (Regent) | 33 (Kaiser Crab, act 2 boss) | -- | 48 | 20.5 / 8.3 | 26.9 / 15.3 | -- |
| **All** (fights per act) | 36.2 | -- | 47.6 | dmg 1.05, HP 1.65 (36) | dmg 0.98, HP 1.05 (18) | dmg 0.72, HP 1.48 (17) |

Cells are median damage a turn / median HP lost per fight as % of max HP,
normal fights. Furina's HP column is `net%` (after her end-of-combat return of
drained HP); the base five's records predate that key, so their `hp%` stands
in (the base five have no such return; Burning Blood is the one heal). Her
gross `hp%` ratios are 2.47 / 1.55 / 2.12. Command:
`tools/telemetry_report.py --character Furina --since 2026-10-15T21:00
--until 2026-10-16T06:00 --baseline-since 2026-10-05 --baseline-until
2026-10-06` with the five `--baseline-run-instance` tokens. No run won, and the
base five won none either; all five of theirs reached act 3, three of hers
did.

## The prediction, graded

"Act 1 easy, act 2 dangerous, act 3 easy": **MISS** on act 3, the clause the
seats contradict most. Act 3 is her worst act: damage 0.72 of base (33.7
against 47.0 a turn), HP 1.48x. Act 2's normal fights are on the bar (0.98,
1.05), but its boss ended one run and act 1's boss another, so "dangerous" holds
for the bosses only. Act 1's normal fights deal base damage (1.05) at 1.65x
the HP.

What the seats said (records: scratch `seats/archive/furina-suite1-l1..l5`):
banking Fanfare off a hit, then spending it on Rising Applause or All the
World's a Stage, decided most fights; reactions with the guests (Vaporize,
Frozen, Overloaded) were the best turns. Three found no damage to ALL enemies
until Let the People Rejoice. At low HP her Drain cards lock ("Not enough
HP"), so the fights that bring her low remove her outs. Weakest cards named:
Endless Waltz (no Repay engine), Hymn of Many Waters, Verdict of the Oratrice,
The Masquerade, Kirara, The Show's Not Over. Lane 1's run turned on the
Whispering Earring, which plays her first turn (a relic, not her kit).

## Picks

1. **What suite 1 feeds.**
   - **(a) Default:** a `furina-next` change paper aimed at act 3 damage and
     area damage, with the weak cards above as the candidates, and the screen
     lines in `BACKLOG.md` fixed on main; then suite 2 on these seeds.
   - (b) Treat the act-3 gap as seat skill (your run says it caught up) and
     hold her as she is.

Raw transcripts: `review/qa/blindplay/` (local, gitignored).
