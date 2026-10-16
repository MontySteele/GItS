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

- **Probably not mostly the play.** Her seats used Energy and Block as well
  as tonight's Varka seats on the same seeds (0.12 against 0.13 unspent Energy
  a turn; 23% of turns without Block for both). That does not show equal play:
  drafting, sequencing and Drain choices are not measured, and her seats
  declared more mistakes (about 11 to 7).
- **Her payoffs do not grow.** Fanfare comes from HP lost or repaid. Her
  production in normal fights is 5.2 Fanfare a turn in act 1, 8.2 in act 2
  and 8.3 in act 3 (spent plus left at the end, over turns; 68 fights), while
  base damage needed rises by about 40% from act 2 to act 3. Her
  payoffs turn it into damage at a fixed rate, so her act 3 payoffs deal 20
  to 29 a play, as in act 2. Base finishers grow with the deck (The Scythe,
  Conflagration, Finisher: 54 to 68 a play in act 3). In long elite and boss
  fights she deals 26 a turn on turn 5 against Varka's 49.
- **The cards that should grow them go untaken.** Since the sweep build,
  the three Powers this paper changes were taken 4 times in 46 offers:
  Standing Room Only 0 of 17, Crescendo 2 of 23, Prima Donna 2 of 6
  (Showstopper, unchanged, 0 of 10) (`tools/telemetry_report.py --offers --character Furina
  --since 2026-10-14`). The seats said why: Prima Donna "never fired in
  practice because I spend Fanfare quickly"; Crescendo "never drew a Spend
  turn where it paid"; Standing Room Only was passed over as "+1 Strength per
  full Spend". Her Powers that were taken are not engines (The Masquerade, 9
  of 22, called a dead card by two seats; Leading Lady, 12 of 22).

So her Powers are the likeliest single cause, though not proven to be the
whole gap: the three meant to grow a long fight each wait on a condition her
play avoids (a full bank at turn start, spending everything, the first Spend
of a turn). The findings justify testing these engines.

## 2. The changes

Three Powers, same names, rarities and roles; each loses the condition that
kept it from firing. No payoff card and no starter changes.

| Card | Today | furina-next |
|---|---|---|
| **Crescendo** (Uncommon Power, 1) | The first time each turn you Spend, draw 1 card. (upg: Innate) | At the start of your turn, gain 2 [3] Fanfare, then 2 [3] more each turn after. |
| **Standing Room Only** (Rare Power) | 2 [1]. Whenever you Spend all your Fanfare and it is at least 1, gain 1 Strength. | 1. Whenever you Spend, gain 1 Strength. (upg: Innate) A Spend of 0 Fanfare does not count. |
| **Prima Donna** (Rare Power) | 2 [1]. At the start of your turn, if you have 10 or more Fanfare, gain [E]. | 2. At the start of your turn, if you Spent last turn, gain [E] [and draw 1 card]. |

- **Crescendo** is the long-fight engine her bank lacks. It counts from the
  turn it is played, not the combat's turn number: played on turn 1, it pays
  2, 4, 6, 8 on turns 2 to 5 (20 Fanfare) and 42 by turn 7; upgraded, 3, 6,
  9, 12. Played late it starts small, so when to play it is a choice, as with
  Demon Form. It gives up the old card's draw (taken 2 of 23, so the draw was
  rarely in a deck); prediction 6 watches her draw.
- **Standing Room Only** pays on every Spend that spends at least 1 Fanfare.
  Her own cards make 2.6 Spends a fight in act 3, but guests can Spend too:
  Full House Spends once for each damaging guest act, and Showstopper and
  Navia add more. Three damaging guests under Full House give 3 Strength a
  turn while the bank lasts, more with Showstopper. That makes it a bridge
  from her guests to her multi-hit Attacks, and its ceiling is set by those
  builds, not by 2.6. The bank limits it (each Spend needs Fanfare), and the
  build takes three Rares or Uncommons plus guests, so it is not a trivial
  loop; it is tested on purpose (sec.3).
- **Prima Donna** rewards spending instead of hoarding. "Last turn" keeps a
  0-cost Spend (Quick Flourish) from refunding itself on the same turn. At
  cost 2, Innate would only make the setup earlier, so the upgrade improves
  the return instead: it also draws a card, which gives back some of the draw
  Crescendo gives up.
- **Upgrades.** The two Rares drop "costs 1 less when upgraded" ([USER], on
  Yae: "a lot of powers have the formulaic "cost 2 - upgrade reduces to 1"
  pattern"), and the three upgrades differ: a number (Crescendo), Innate
  (Standing Room Only), a card (Prima Donna).

Not changed, and why: Showstopper and Full House are guest Powers, outside
this question; The Masquerade and the weak cards suite 1 named (Endless
Waltz, Hymn of Many Waters, Verdict of the Oratrice, Kirara, The Show's Not
Over) wait for suite 2, so this suite tests one idea.

## 3. Predictions (written before the suite)

Suite 2: the same five seeds, one Sonnet seat per lane for the whole run, on
a `furina-next` staging build.

1. Crescendo, Standing Room Only and Prima Donna together are taken in at
   least a quarter of their offers (today 4 of 46), reported card by card.
2. Normal-fight damage a turn in act 3 rises to at least 0.85 of base (today
   0.75); acts 1 and 2 stay within 15% of base.
3. In elite and boss fights, damage a turn on turns 5 and later rises by at
   least a quarter (today 26 on turn 5, 39 on turns 7 and later).
4. Net HP lost per fight does not rise in any act (today 1.65 / 1.05 / 1.53
   of base).
5. At least three of five runs reach act 3 (today three).
6. Cards drawn a turn do not fall (today 5.74), and Fanfare produced a turn in
   act 3 rises above act 2's (today 8.3 against 8.2).

Before the suite, a C# test plays Standing Room Only with Full House,
Showstopper and three damaging guests, and the record states the most
Strength one turn gave, so a runaway shows up before the seats do.

If 1 holds and 2 or 3 does not, the engines are taken but too small; if 1
fails, they are still read as weak, and the next paper looks at their text.

## Picks

1. **The change set.**
   - **(a) Default:** the three Powers as in sec.2, built on `furina-next`,
     then suite 2.
   - (b) Crescendo only, so the suite isolates one engine.
   - (c) You name a different direction (for example her payoff cards
     instead of her Powers).

## Revised 2026-10-16 after GPT's review (relayed by [USER])

[USER]: "I had some concerns on how Spend would scale, so I asked GPT for a
look ... I'm not set any particular way on this one". Taken from it:
Crescendo's timing is settled (it counts from when it is played) and its
examples corrected; Standing Room Only's guest Spends (Full House,
Showstopper, Navia) are named and tested; Prima Donna's upgrade improves its
return instead of adding Innate; the three upgrades no longer repeat; the
diagnosis is softened; 4 of 46, not 56. Added: her Fanfare production a turn
by act, which shows production, not only the peak, stops growing after act 2.

## Ruled 2026-10-16

[USER]: "On Furina's powers - I'm good with this now, ship it!" Pick 1 (a),
as revised.
