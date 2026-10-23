# furina-next paper 3, 2026-10-16: blank Repays and act 1 bleeding

Furina is a Balance kit. These changes go on a fresh `furina-next` (cut from
`main` after the suite 3 promotion, #1369) and reach `main` only through a
promotion PR with a suite 4 record graded against the predictions below.

**Why.** Suite 3 (`review/records/furina-suite-3-2026-10-16.md`), ruled
"Let's promote as-is ... In the meantime we can do a paper round on the
findings." Her mean end floor rose to 42.8 and the act 3 bank is now spent.
Two findings are left.

## 1. What the numbers say

Suites 1 to 3, 15 runs (scratch `furina-gap/p3.py`):

- **She takes about 2.4 times the base five's damage in acts 1 and 2, on
  the same pressure.** Normal fights, per turn: incoming 8.5 against 8.2 in
  act 1 and 12.8 against 12.4 in act 2; fights last the same 3 to 3.6 turns;
  damage taken 4.4 against 1.8 in act 1 and 6.9 against 3.3 in act 2. Her
  HP lost is enemy damage, not her own Drains: in act 1 she takes 12.7
  damage a fight and ends 11.6 HP down. Suite 3's net HP ratios were
  2.00 and 1.30 of base.
- **Some of that is the design.** Fanfare comes from HP lost, and seats say
  so: "banking Fanfare by taking damage (not blocking)" (suite 3, lane 4);
  "knowingly underblocked for Fanfare" (suite 2, lane 1). Her printed Block
  pool is the smallest of any kit (12 cards, 41 Block; wave record
  2026-10-13).
- **Four of five suite 3 NEVER AGAIN cards are Repay cards**: Endless
  Waltz (two seats), Hymn of Many Waters, Pneuma Refrain. A Repay returns
  only drained HP, so with nothing drained the face reads "Repays 0". They
  are not all blank, though (corrected after GPT's review):
  - **Hymn of Many Waters** already gives 9 Block with nothing drained (6
    printed, 3 from its fallback). Its complaint is the preview, which
    leads with "Repays 0" and not the Block.
  - **Pneuma Refrain** still draws 2; its Repay part is what goes blank.
  - **Endless Waltz** is truly blank: its bonus counts only Repays that
    returned HP.
  - Charlotte, Sigewinne and Grand Entrance already turn an unreturned
    Repay into Block, like Hymn.

  These cards are played a lot: over the three suites Pneuma Refrain 67
  times, Hymn 39, Clean Slate 27, Endless Waltz 26.

So there are two problems in act 1: she takes more damage than her Block can
cover, and the Repay cards undersell or lose their value when nothing is
drained.

## 2. The change

**One rule: a Repay that cannot return all its HP gains 1 Block for each HP
it could not return, unless the card says otherwise.** Hymn of Many
Waters and Grand Entrance already print this (the code's `StageFloor.Block`);
the rule makes it every Repay's default. With nothing drained a Repay card
is a Block card; with drained HP it returns that HP first. (It reads off
drained HP, not her HP: at 30 HP with nothing drained she gets Block, not
healing.)

- **Keeps its own floor:** Cleansing Torrent, which prints damage for an
  unreturned Repay, keeps the damage instead of Block.
- **"Repay all"** (Singer of Many Waters, Grand Absolution) has no number,
  so it has no floor: all of nothing is nothing.
- **Newly covered:** Pneuma Refrain, Clean Slate, Ebb and Flow, Fountain of
  Lucine, Coup de Théâtre's kill Repay, Ousia / Pneuma's Pneuma face,
  Endless Waltz, and **Salon Solitaire, her starter relic**: its "Repay 1"
  each turn end now gives 1 Block when nothing is drained. That is a small
  baseline gain on every run, named here so it is not missed.
- **Already covered, applied once:** Hymn of Many Waters, Grand Entrance,
  Charlotte and Sigewinne keep the Block they give today; the rule never
  adds a second floor. Hymn and Grand Entrance drop the clause they print.
- **Fontaine Teardrop** (relic) prints exactly this rule today ("Whenever
  you Repay more than you have drained, gain the rest as Block"), so it
  would go blank. It becomes: "An unreturned Repay gains 2 Block for each
  HP instead of 1." (pick 1).
- **No Vigor floor is left on a card.** The code's Vigor floor names two
  cards that no longer exist; nothing changes there.
- **The preview leads with the Block.** A Repay with nothing to return
  reads "Repay 0: gain 3 Block", not "Repays 0" (GPT's point: some of the
  complaint is how the cards say what they do).
- The rule is one keyword tip line: "Any HP a Repay cannot return becomes
  Block." 

| Card | Today | furina-next |
|---|---|---|
| **Pneuma Refrain** (Uncommon Skill, 1) | Repay 5. Draw 2 cards. | Repay 4 [6]. Draw 2 cards. (One less, because it now always pays 4 Block when healthy.) |
| **Endless Waltz** (Uncommon Attack, 1; upgrade adds to Y) | Deal X damage, plus Y for each time you Repaid this turn. | Repay 2. Deal X damage, plus Y for each time you Repaid this turn. |

Endless Waltz keeps today's counting: only a Repay that returned HP counts.
So its own Repay 2 counts only when there is drained HP to return. With
nothing earlier this turn: nothing drained, 6 damage and 2 Block; 1
drained, 9 damage, 1 HP back and 1 Block; 2 or more, 9 damage and 2 HP
back. Its guaranteed gain is the 2 Block; the bonus stays a reward for
Draining first. (The first draft said it "starts its own count"; GPT
showed it does not when nothing is drained.)

Universal Revelry and Critics' Darling ("whenever you Repay, that much")
keep reading the HP actually returned, not the Block.

## 3. Predictions (written before suite 4)

Same five seeds, one Sonnet seat per lane, on the `furina-next` staging
build.

1. Net HP lost per normal fight in act 1 falls from 2.00 to at most 1.60 of
   base, and act 2 from 1.30 to at most 1.15.
2. Damage taken a turn in act 1 normal fights falls from 4.4 to at most
   3.5, and the record names the Block the Repay floor gave (per act, and
   two concrete turns).
3. Block gained a turn in act 1 normal fights rises at least a quarter
   (suites 1 to 3: 3.2).

A seat still calling a Repay card situational is not by itself a miss.
4. Act 3 damage stays at least 0.85 of base, and at least four of five runs
   reach act 3 (suite 3: 0.95, four).

## Picks (ruled 2026-10-16)

[USER]: "Overall I agree with the paper, but as per usual with Furina, I'd
like to sanity check that we don't turn any of her cards into overly-verbose
Yugioh cards. Agreed on both counts, but let's also ask that the agent scan
the modified cars and make sure that the relevant text and tooltips are
clear and concise."

1. **The rule: (a)**, as amended: an unreturned Repay gains Block, the two
   card rows, the Fontaine Teardrop change and the Block-first preview.
2. **Act 1 Block beyond the rule: (a).** Nothing more until suite 4.

**Build condition.** Every card, relic and tooltip the change touches is
read back for length and clarity in the build: base-game templates, one
keyword tip for the rule, no card gaining a clause it does not need.

## Upgrade census (2026-10-23)

**The count.** Seventeen of Furina's 78 pool cards upgraded by cost alone
(cost -1), against 6 for the base Ironclad and 9 for the Silent (`BACKLOG.md`:
"You do have a habit of making too many powers just decrease their cost by 1
on upgrade"). After this pass she has 8, inside the base range.

**The ruling.** [USER], 2026-10-23: "Otherwise I agreed on all the cards!"
Every cost stays; the upgrade is now the bracketed part.

| Card | Base [upgraded] | Expected effect, graded by the next suite |
|---|---|---|
| Let the People Rejoice (Rare Attack, 2) | Spend all your Fanfare. Deal 2 [3] damage to ALL enemies per point. | A bank of 10 hits ALL for 30, not 20; upgraded copies end act 2 and 3 fights a turn sooner. |
| The Show Must Go On (Rare Skill, 2) | Gain Block equal to your Fanfare. [Retain.] | Held for the big enemy turn; Block from it per play rises, its play count does not fall. |
| Tutti! (Common Skill, 1) | Each guest acts. Draw 1 [2] card(s). | One more card a play; no change to how often guests act. |
| Rainfall Overture (Uncommon Skill, 1) | Apply Hydro to ALL enemies. Your next Attack this turn hits ALL enemies. [Draw 1 card.] | Finds the Attack it widens more often; fewer turns it is played with no Attack after it. |
| The Masquerade (Uncommon Power, 1) | Whenever you Drain, gain that much Block [plus 2]. | About 2 Block more a Drain, 4 to 6 a turn in a Drain deck; act 1 HP lost per fight down slightly. |
| Critics' Darling (Rare Power, 2) | Whenever you Drain or Repay, deal that much damage [plus 1] to a random enemy. | About 1 damage more a Drain or Repay, 3 to 5 a turn in a loop deck; small. |
| Showstopper (Rare Power, 2) | At the end of your turn, Spend 5 [3]: your guests act again. | The second round fires on banks of 3 and 4; more rounds a fight, a smaller bank held. |
| Ensemble Cast (Rare Power, 2) | You have 4 guest seats. Summon a random guest [2 random guests]. | A full extra guest on the turn it is played; more guest acts in fights where it is drawn early. |

Kept as cost cuts: Singer of Many Waters, Universal Revelry, A Five-Century
Act, Regina of All Waters, Grand Absolution, Encore Performance, Verdict of
the Oratrice, Plot Twist.

**Bring the House Down, reflavoured (its own commit; [USER] may still change
it).** It no longer repeats Let the People Rejoice's spend-for-damage.

| Card | Was | Now | Expected effect, graded by the next suite |
|---|---|---|---|
| Bring the House Down (Rare Attack, 2) | Spend up to 10 for each guest on stage, all you can. Deal that much damage. Each guest acts. [cost -1] | Deal 8 [11] damage. Spend 5 for each guest on stage: each guest acts twice. | Less burst (8, not up to 30 with three guests) and more guest acts; played later in a fight, with a full stage and 10 to 15 banked. Take rate may fall. |

With no guest on stage, or a bank short of 5 a guest, it is only the hit, as
Showstopper's "Spend 5: ..." does nothing when she cannot pay. It is no
longer a "Spend up to", so Extended Run does not raise it.

**How it is built.** The three Powers keep one badge for both versions, as
Prima Donna does (`UpgradeTwinPower`): the copy an upgraded card installs
adds its 2 Block, its 1 damage or its cheaper Spend, and Showstopper pays its
cheaper rounds first. Text: "plus 2" and "plus 1" follow Endless Waltz's
"plus Y" wording; Tutti! uses the base game's "Draw N card(s)" template. No
lint asked for another wording.
