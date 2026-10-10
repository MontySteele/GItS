# Varka forced-Amber round, 2026-10-10

This round grades the Pyro payoffs on Pyro starts. Its predecessor is `review/records/varka-payoff-round-2026-10-10.md` (PR #1017).

**What ran**
- Solo Varka at A0 on staging 0.2.4704+next, which includes #1018: Stoke switches element first, Wolfpack shuffles in an exhausting copy, the Banner text fix, and seat-page fixes.
- Every lane's starting Knight was forced to Amber with `--varka-knight pyro`. The seed's own roll was drawn and discarded.
- Same five seeds. Per-act Sonnet seats, embark `20261010-0400xx`.
- The current element is logged at play for the first time.
- The fact packet and seat records are in the session scratchpad (`varka-amber-r1/`), which is gitignored.
- The review is by a Fable reviewer. The main session accepted it with one correction: `hp_after_return` is missing from this round's rows because the build was deployed before #1022 merged. It is not a defect.

## Result

| Seed | Amber start | Payoff round (own Knight) | Base character |
|---|---|---|---|
| 30KMHAVG9SMQ | floor 44, Slimed Berserker | floor 33 | floor 48 |
| CYHZM9S0VPW6 | floor 38, Frog Knight | won | floor 48 |
| DJCAV76ZKAUN | floor 48, Test Subject at 16 HP | won | floor 48 |
| YEWA0B7AVE45 | floor 33, Knowledge Demon | floor 33 | floor 46 |
| R41TX5Q0ZQYN | **won** | won | floor 48 |

1 win in 5, against 3 in 5 on the seeds' own Knights.

The four deaths:
- Lane 2: a text misread. Shatter's 6 damage read as a bonus.
- Lanes 1 and 3: attrition.
- Lane 4: the same death as last round.

**By act against the base window:**

| | This round | Payoff round | Base |
|---|---|---|---|
| Damage a turn (ratio to base) | 1.15 / 1.03 / 0.79 | 1.05 / 0.91 / 0.69 | — |
| HP lost (ratio to base) | 0.39 / 0.90 / 1.08 | 0.36 / 0.60 / 0.72 | — |
| Block a turn | 3.8 / 6.5 / 9.8 | — | 2.2 / 2.9 / 7.5 |

A Pyro start kills faster and blocks less. 1 in 5 against 3 in 5 is inside seat and seed noise, so no strength number moves.

**Offers and play**
- **Pyro take rate:** 35%, up from 13% (Varka-owned cards).
- **Paid for by other elements:** Anemo fell from 37% to 22%, Cryo from 19% to 7%, Electro from 23% to 15%.
- **Overall take rate unchanged:** 21% against 23%.

Seats draft their starting element, which confirms the last record's element-lock diagnosis.

- 72.6% of Four Winds' Ascension plays had Pyro current. Two lanes were effectively mono-Pyro (96% and 100%). Three ran a second element, the Switch archetype.
- The payoff paper's three grading lines are all met.

**Pyro cards, taken / offered:**

| Card | Taken / offered |
|---|---|
| Stoke | 4/7 |
| Kindled Edge | 3/6 |
| Ember Cleave | 3/9 |
| Sharpshooter | 2/6 |
| Wildfire | 2/3 |
| Baron Bunny | 1/7 |
| Pyre Oath | 1/9 (0 of 4 from rewards) |

**How the payoffs played:**
- Stoke: 33 plays.
- Wildfire Oath: the engine of the one win.
- Wolfpack: decided fights in the deck that played it. It sat dead in the deck with 2-to-3-turn fights.
- Pyre Oath: failed again.

## What changes (Claude ships)

1. **Pyre Oath becomes Ashen Oath.**
   - Text: "Exhaust a card. Whenever you Exhaust a card, gain 2 Pyro Oath."
   - This is the fallback promised by the last record.
   - The rename fixes a legibility defect: "Pyre Oath 1" sat beside "Pyro Oath 12" on the status list, and a seat lost track of its Pyro Oath.
2. **Wildfire Oath:** numbers held.
   - The seat page shows its bonus on any card that applies Pyro while it is up ("Wildfire: +19 a hit").
   - It fires on every Pyro application he makes, but not on a Swirl's spread.
3. **Frost Ward** gets a floor. It was taken 1 of 14 and called NEVER AGAIN twice.
   - Text: "Gain 3 [4] Block. For each enemy with an aura, apply 1 Weak and gain 3 [4] more Block."
4. **Oath Unto Death:** cost 3 to 2, Innate upgrade kept. It was NEVER AGAIN in all three of its acts, and played only on 7-Energy turns.
5. **Frozen's badge text:** "Its next action deals 50% less damage. Attacking it ends the freeze and deals 6 unblockable damage."
   - The same text goes on the preview and glossary.
   - Element text is shared by all four kits, so this goes on `klee-next`.
6. **The seat page's hand row** prints "Knight" on Knight cards, if it does not already.
7. **Held:**
   - Wolfpack, and Boreas's Fang's once-per-combat Ascension. This is the paper's intended weakness, and the real card is retained, not exhausted.
   - Unwavering Banner.

**Seat error or by design:**
- Mika is a Knight, so it switches the element.
- Itto is a Companion, not a Knight.
- Stoke auto-selects when the hand holds one other card, as True Grit+ does.
- "Four Winds was exhausted" was a misread: it was in the discard pile.

**For [USER]'s queued Hydro pick:** Hydro was taken 8% of the time under a Pyro start too, even as act-3 HP lost crossed 1.0. Seats skip the Block element even when Block is what kills them.

## Next round

Unforced Knights on the same five seeds, with the changes above.

**Grading lines:**
- Ashen Oath is taken from a reward once and played.
- Frost Ward is taken at or above about 21% and played when held.
- Oath Unto Death is taken and played at cost 2.
- No record reads Shatter's damage as a bonus.
- Wolfpack's copy is drawn and played in at least half the 4-turn-plus fights of a run that holds it.

**Then strength:** wins, and act-3 HP lost against 0.72 and 1.08, with the Block multiple beside it, using `hp_after_return`.
