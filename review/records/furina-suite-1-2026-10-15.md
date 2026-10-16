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
| **All** (fights per act) | 36.2 | -- | 47.6 | dmg 1.05, HP 1.65 (36) | dmg 0.98, HP 1.05 (18) | dmg 0.75, HP 1.53 (14) |

Cells are median damage a turn / median HP lost per fight as % of max HP,
normal fights. Furina's HP column is `net%` (after her end-of-combat return of
drained HP); the base five's records predate that key, so their `hp%` stands
in (the base five have no such return; Burning Blood is the one heal). Her
gross `hp%` ratios are 2.47 / 1.55 / 2.25. Command:
`tools/telemetry_report.py --character Furina --since 2026-10-15T21:00
--until 2026-10-16T06:00 --feed bot --baseline-since 2026-10-05 --baseline-until
2026-10-06` with the five `--baseline-run-instance` tokens. No run won, and the
base five won none either; all five of theirs reached act 3, three of hers
did.

## The prediction, graded

"Act 1 easy, act 2 dangerous, act 3 easy": **MISS** on act 3, the clause the
seats contradict most. Act 3 is her worst act: damage 0.75 of base (35.0
against 47.0 a turn), HP 1.53x. Act 2's normal fights are on the bar (0.98,
1.05), but its boss ended one run and act 1's boss another, so "dangerous" holds
for the bosses only. Act 1's normal fights deal base damage (1.05) at 1.65x
the HP.

What the seats said (records: scratch `seats/archive/furina-suite1-l1..l5`):
banking Fanfare off a hit, then spending it on Rising Applause or All the
World's a Stage, decided most fights; reactions with the guests (Vaporize,
Frozen, Overloaded) were the best turns. Three said they lacked damage to ALL enemies,
but the numbers do not bear it out: her damage a turn in fights with two or
more enemies is at base (26.9 against 28.0), and the gap is single-target
(26.0 against 31.8; scratch `furina-gap/packet.md` table 6). At low HP her Drain cards lock ("Not enough
HP"), so the fights that bring her low remove her outs. Weakest cards named:
Endless Waltz (no Repay engine), Hymn of Many Waters, Verdict of the Oratrice,
The Masquerade, Kirara, The Show's Not Over. Lane 1's run turned on the
Whispering Earring, which plays her first turn (a relic, not her kit).

## The gap

[USER] asked, 2026-10-15: "Compared to base game characters, are her powers
weaker? Or do her combo pieces provide less value? What's that actual gap we're
making up for as opposed to bad play". From scratch `furina-gap/packet.md`,
with tonight's Varka seats (same seat type, same seeds) as the control for play:

- **Not the play.** Unspent Energy (0.12 against Varka's 0.13 a turn), turns
  without Block (23% each) and turns under-blocked (77.5% each) match Varka's.
  Her seats declared more mistakes (about 11 to 7), which fits a harder kit.
- **Not Power count or area damage.** She plays as many Powers as base (1.02 a
  fight against 0.95), one turn later. What the Powers add cannot be read from
  telemetry for any character. Her most-played Power, The Masquerade (28
  plays), was called a dead card by two seats.
- **The payoffs stop growing.** Her act 3 payoff cards deal 20 to 29 a play,
  about what they dealt in act 2; base act 3 finishers deal 54 to 68 (The
  Scythe, Conflagration, Finisher) and Varka's 35 to 46. Her Fanfare bank
  peaks at 23 in act 2 and 21 in act 3, so the bank that feeds them is flat.
  In long elite and boss fights her damage on turn 5 and turn 7+ is 26 and 39
  a turn, against Varka's 49 and 56.
- **She pays more HP.** 15.3 HP a fight after the return of drained HP,
  against Varka's 12.4, highest in elites.
- **Noise is large.** Her act 3 damage a turn was 28.6, 41.7 and 35.0 over
  the last three rounds, and she won 4 of 10 on 10-14.

## Picks

1. **What suite 1 feeds.**
   - **(a) Default:** a `furina-next` change paper aimed at act 3 damage and
     how her payoffs scale (sec. "The gap" below), with the weak cards above
     as the candidates, and the screen
     lines in `BACKLOG.md` fixed on main; then suite 2 on these seeds.
   - (b) Treat the act-3 gap as seat skill (your run says it caught up) and
     hold her as she is.

Raw transcripts: `review/qa/blindplay/` (local, gitignored).
