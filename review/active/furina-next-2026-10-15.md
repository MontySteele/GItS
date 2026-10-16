# furina-next, 2026-10-15: her Fanfare engines

Furina is a Balance kit, so her cards on `main` are frozen. These changes go
on `furina-next` and reach `main` only through a promotion PR that carries a
suite record graded against the predictions below
(`docs/current/operations/stage-gate.md`).

**Why.** Suite 1 (`review/records/furina-suite-1-2026-10-15.md`): no seat won
and two of five died before act 3. Normal-fight damage was at base in acts 1
and 2 (1.05, 0.98) and 0.75 of base in act 3. [USER] asked: "Compared to base
game characters, are her powers weaker? Or do her combo pieces provide less
value? What's that actual gap we're making up for as opposed to bad play".
Then: "On Furina - yes, let's do a paper on this". The numbers are in that
record's "The gap" and in scratch `furina-gap/packet.md`.

## 1. What the gap is

- **Not the play.** Her seats used Energy and Block exactly as well as
  tonight's Varka seats on the same seeds (0.12 against 0.13 unspent Energy a
  turn; 23% of turns without Block for both).
- **Her payoffs do not grow.** Fanfare comes from HP lost or repaid, and her
  bank peaks at about the same size in act 3 as in act 2 (21 against 23). Her
  payoffs turn it into damage at a fixed rate, so her act 3 payoffs deal 20
  to 29 a play, as in act 2. Base finishers grow with the deck (The Scythe,
  Conflagration, Finisher: 54 to 68 a play in act 3). In long elite and boss
  fights she deals 26 a turn on turn 5 against Varka's 49.
- **The cards that should grow them go untaken.** Since the sweep build,
  her four Powers that act on Spend or Fanfare were taken 4 times in 56
  offers: Standing Room Only 0 of 17, Crescendo 2 of 23, Prima Donna 2 of 6,
  Showstopper 0 of 10 (`tools/telemetry_report.py --offers --character Furina
  --since 2026-10-14`). The seats said why: Prima Donna "never fired in
  practice because I spend Fanfare quickly"; Crescendo "never drew a Spend
  turn where it paid"; Standing Room Only was passed over as "+1 Strength per
  full Spend". Her Powers that were taken are not engines (The Masquerade, 9
  of 22, called a dead card by two seats; Leading Lady, 12 of 22).

So her Powers are the gap: the three meant to grow a long fight each wait
on a condition her play avoids (a full bank at turn start, spending
everything, the first Spend of a turn).

## 2. The changes

Three Powers, same names, rarities and roles; each loses the condition that
kept it from firing. No payoff card and no starter changes.

| Card | Today | furina-next |
|---|---|---|
| **Crescendo** (Uncommon Power, 1; upg: Innate) | The first time each turn you Spend, draw 1 card. | At the start of your turn, gain 1 Fanfare for each turn this combat. (upg: Innate) |
| **Standing Room Only** (Rare Power) | 2 [1]. Whenever you Spend all your Fanfare and it is at least 1, gain 1 Strength. | 1. Whenever you Spend, gain 1 Strength. (upg: Innate) |
| **Prima Donna** (Rare Power) | 2 [1]. At the start of your turn, if you have 10 or more Fanfare, gain [E]. | 2. At the start of your turn, if you Spent last turn, gain [E]. (upg: Innate) |

- **Crescendo** is the long-fight engine her bank lacks: 1, 2, 3 ... Fanfare a
  turn, 15 by turn 5 and 28 by turn 7, fed to the payoffs she already has.
  It is an Uncommon because it does nothing on its own; a short fight gives
  3 to 6 Fanfare.
- **Standing Room Only** pays on every Spend (she makes 2.6 a fight in act 3,
  more in boss fights), so the Strength grows with fight length like Demon
  Form's, but only as fast as she spends. Strength adds to every hit of
  Soloist's Solicitation.
- **Prima Donna** rewards spending instead of hoarding, so it no longer fights
  her own play. "Last turn" keeps a 0-cost Spend (Quick Flourish) from
  refunding itself on the same turn.
- The two Rares drop the "costs 1 less when upgraded" pattern ([USER], on Yae:
  "a lot of powers have the formulaic "cost 2 - upgrade reduces to 1"
  pattern"); each upgrade gives Innate.

Not changed, and why: Showstopper and Full House are guest Powers, outside
this question; The Masquerade and the weak cards suite 1 named (Endless
Waltz, Hymn of Many Waters, Verdict of the Oratrice, Kirara, The Show's Not
Over) wait for suite 2, so this suite tests one idea.

## 3. Predictions (written before the suite)

Suite 2: the same five seeds, one Sonnet seat per lane for the whole run, on
a `furina-next` staging build.

1. Crescendo, Standing Room Only and Prima Donna together are taken in at
   least a quarter of their offers (today 4 of 56).
2. Normal-fight damage a turn in act 3 rises to at least 0.85 of base (today
   0.75); acts 1 and 2 stay within 15% of base.
3. In elite and boss fights, damage a turn on turns 5 and later rises by at
   least a quarter (today 26 on turn 5, 39 on turns 7 and later).
4. Net HP lost per fight does not rise in any act (today 1.65 / 1.05 / 1.53
   of base).
5. At least three of five runs reach act 3 (today three).

If 1 holds and 2 or 3 does not, the engines are taken but too small; if 1
fails, they are still read as weak, and the next paper looks at their text.

## Picks

1. **The change set.**
   - **(a) Default:** the three Powers as in sec.2, built on `furina-next`,
     then suite 2.
   - (b) Crescendo only, so the suite isolates one engine.
   - (c) You name a different direction (for example her payoff cards
     instead of her Powers).
