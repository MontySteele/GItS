# Klee whole-run round after the card passes, 2026-10-11

This round grades the three passes ruled tonight:
- **The Commons** (`review/active/klee-commons-pass-2026-10-11.md`, #1082);
- **The Uncommons and Rares** (`review/active/klee-upper-pass-2026-10-11.md`, #1085);
- **The Companion numbers** (`review/active/companion-pass-2026-10-11.md`, pick 2, #1084).

Five whole-run Sonnet seats played on the base-five seeds, A0, build 0.2.4866+next. The packet (`klee-pass-packet.md`), the records and the scripts are in the session scratchpad, which is gitignored. A Fable reviewer reviewed the round (`klee-pass-review-fable.md`), and the main session accepted the review as written.

## Result: 0 of 5; every act-1 boss beaten

| Seed | Floor | Killer |
|---|---|---|
| CYHZM9S0VPW6 | 48 | the Queen (act-3 boss) |
| DJCAV76ZKAUN | 33 | Kaiser Crab (act-2 boss) |
| 30KMHAVG9SMQ | 33 | The Insatiable (act-2 boss) |
| YEWA0B7AVE45 | 39 | Axebots (act 3) |
| R41TX5Q0ZQYN | 48 | Aeonglass (act-3 boss) |

The mean death floor is 40.2. No earlier Klee whole-run exists on these seeds. Her per-act suites averaged floors 28 to 41.

**The four lines:**

| Line | Measured | Result |
|---|---|---|
| Changed cards taken in at least 20% of offers | 17 of 86 = 19.8% (Commons 25%, Uncommons/Rares 14%; before 11.6%) | Miss by one take; the 95% interval is 13% to 29% |
| No act-1 boss deaths in five | 0 of 5; seats entered at 57 to 70 HP | Pass |
| Act-1 normal fights no more than 10% shorter than base | 2.94 turns against 3.06 (3.7% shorter); 5.6 HP lost against 5.9 | Pass |
| Companions taken in at least 15% of offers, and 2 or more per deck at the act-1 boss | 6 of 109 = 5.5% (before 9.9%); 1.0 per deck | Fail |

**Boss damage is now above base:** 34.1 a turn against 28.5 at the act-1 boss, and 58.3 against 39.4 at the act-2 boss.

## What played well

- **The Commons pass made her engine.**
  - Chain Fuse was taken 5 of 10 times, up from 14%, and appeared in 4 of 5 decks.
  - Sizzle was taken 3 of 5, up from 16%.
  - Three of the five MOST WANTED turns were Bomb stacks cashed by a Set off. Booby Trap plus Chain Fuse grew seven Bombs to 163, and Sizzle killed the act-2 boss with them.
- **The opening turn is a real decision.** A seat chooses between setting off now and letting the Bomb grow, from the first fight's first turn.
- **The Companion Commons did their job.** Seats drafted them for their elements, and every one of the 28 fights with a reaction had a Companion played.

## What did not

- **Rare Companions lose every time.** No Rare Companion was taken in 20 offers. At all 8 boss reward screens, the native Rare beat the Rare Companion, including Durin, Albedo, Jean, Navia, Varka, Venti, Clorinde, Arlecchino and Mizuki. Your bar for Uncommon and Rare Companions ("Colorless-tier") is the one that fails.
- **Act-3 normal fights cost 16.7 HP against base's 10.9.**
  - This is tempo, not Block. She deals 40.1 damage a turn against base's 47.8, but blocks 9.6 a turn against base's 8.5.
  - Ten of those 16 fights are from the two lanes without the growth engine.
- **Four changed cards were never taken:** Exquisite Compound 0 of 8, Taste Test 0 of 6, Tag Along 0 of 6, Lizard-Tail Gunpowder 0 of 6.
  - Each alone fits sample noise at these counts; together they don't.
  - Exquisite Compound is still weak by shape. Its "each grows 4" sits under Chain Fuse's 9 at Common.
  - Taste Test reads as a trap: it carries two drawbacks.
  - Tag Along follows the Companion pool, not its own number.
- **NEVER AGAIN picks, all judged fine on the evidence:**
  - Shockwave is a base card.
  - Lisa's Treats was one blind take.
  - Mine Toss was played in 19 of the 22 fights it was held.
  - Sparkling Burst was played in 48% of fights held, up from 25%.
  - Hair Trigger is niche by design.

## Being built, with no approval needed

These are display and text fixes:
- **"Nothing to amplify"** now prints only when an element is applied without a hit. It no longer appears on a real Melt.
- **The seat page prints a card's steps in play order.** Fire! Fire! showed its Bomb after the explosion.
- **The Mine tip** says a Mine waits if its enemy doesn't attack. Three of five seats missed this.
- **Stoke the Fuse and similar cards** say "your largest Bomb, on any enemy". Lane 1 grew the minion's Bomb instead of the Queen's.
- **The seat page names the power** that changed a printed number.

**Checked and not a bug:**
- Vulnerable does scale Bomb damage.
- Weak alone prints Ka-pow! at 3. The 2 a seat saw came from Shrink.

## For [USER]

Klee is ready for your playtest sweep. Things to watch:
- your HP leaving the act-1 boss (seats left it at 31 to 46 of 70);
- whether Chain Fuse plus Sizzle make every deck the same;
- HP lost per act-3 fight.

The picks below are all decided after the sweep, except the Companion one.

1. **Companions.** The next Companion paper starts with the Uncommon and Rare Companions, priced card by card against the native Rares they lost to. The nation sweep and the dead cards are its second half.
   - **(a) Default:** yes.
   - (b) Do the nation sweep first.
2. **Act-3 tempo.**
   - **(a) Default:** hold, and watch act 3 in your sweep.
   - (b) Bombs grow 3 a turn, up from 2. You ruled 4 to 2 on 2026-10-08.
3. **Stoke the Fuse targets an enemy.** It would grow the largest Bomb on the chosen enemy.
   - **(a) Default:** the text fix only for now.
   - (b) Targeted.
4. **Exquisite Compound and Taste Test.**
   - **(a) Default:** hold for the sweep.
   - (b) Taste Test drops its 2 Confiscated, and "they don't go off" becomes its one drawback. Exquisite Compound goes to a design question: does an Uncommon "gather" card have a job that Chain Fuse doesn't already do?
