# Klee balance review, 2026-09-25

What this is: a card-by-card pass over Klee's 78-card pool under the prototype arm
(`KleeOverhaulRoster.Slice`, sheet `docs/prototype-surface.yaml`). It follows
[USER]'s first co-op run on 0.2.3737+proto, cleared at ascension 0, where the
verdict was "Klee was very fun, and I think that the loop basically works! I
think we need to review the cards for overall balance". [USER] ruled pick 4a:
Claude does the review and ships the numbers.

The yardsticks:

- **Energy.** A base-game common Attack pays about 6 to 9 damage per Energy
  (Strike 6, Pommel Strike 9 plus a draw). Block pays about 5 to 8 per Energy
  (Defend 5, Shrug It Off 8 plus a draw).
- **Bombs.** A Bomb grows 4 at the start of Klee's turn, so a Bomb 4 placed now
  is worth about 8 damage when it goes off next turn. It also pays 1 Spark.
- **Sparks.** Dig In, a common, turns 1 Spark into 8 Block at 0 cost, which puts
  a Spark at about one Energy. Since PR #654, Companion cards mint no Sparks.
  Explosions are the only income, plus the 1 she starts with.

The pool has 24 Commons, 36 Uncommons and 18 Rares.

## What the evidence says

- **Two sets of notes.**
  - [USER]'s run: Pocket Match is redundant with Ka-pow!, Spark Knight is
    underpowered, Boom Badge is weak.
  - GPT's seat on 2026-09-24 (the seat-round record, "Klee, GPT's seat"): Sparks
    are sometimes short and sometimes idle.
- **Why Sparks sit idle.** When Sparks sit idle it is because the thing to buy is
  poor, not because there is too much money. Six cards charge more Sparks than
  they are worth by the Dig In yardstick. The Spark prices come down on those six
  (below). That keeps her Spark-limited, which was the point of #654: cheaper
  things worth buying raise the demand on a scarce income.

## Changes

**Already in flight from the run** (Klee playtest PR):

| Card | Was | Now | Why |
|---|---|---|---|
| Pocket Match | 0, 1 Spark: Set off, 5 dmg, Retain | 0, no Spark: Set off only your largest Bomb on the enemy, 3 dmg, Retain | It was Ka-pow! plus 1 damage for a Spark. Now it fires one charge and lets the rest keep growing. |
| Spark Knight | 2 cost, 2 dmg to a random enemy per Spark gained | 1 cost, 3 dmg to ALL enemies per Spark gained (+1 upgraded) | At about 2 Sparks a turn it paid 4 single-target damage for 2 Energy. |
| Boom Badge | 3 Sparks: next Set off card played twice | 2 Sparks (1 upgraded): next Set off, your Bombs deal double | The second play found the Bombs already gone. |

**This review:**

| Card | Was | Now | Why |
|---|---|---|---|
| Countdown (C) | 1: Set off, draw 1 | 1: Set off, draw 2 (3 upgraded) | It paid an Energy for what Ka-pow! does free, plus one card. |
| Fish Blasting (C) | 1: 5 to ALL, adds Confiscated | 1: 8 to ALL, adds Confiscated (+3 upgraded) | Cleave's number with a dead card attached was already the floor. Five was under it. |
| Where Did I Put It? (C) | 1 cost | 0 cost | A tutor for a card type Klee always has one of (Ka-pow! retains) cannot also cost Energy. |
| Stoke the Fuse (U) | +3 growth per Spark | +5 per Spark (+2 upgraded) | 3 delayed damage per Spark is well under one Energy. |
| One More Charge (U) | largest Bomb grows 5 | grows 8 (+3 upgraded); draw at 20 unchanged | It was worse than Chain Fuse, a Common (each Bomb +6). |
| Wait For It... (U) | 1 cost; upgrade cost 0 | 0 cost; upgrade draws 3 | At 1 cost the refund of 1 Energy nets zero Energy for a conditional 2 cards. |
| Party Poppers (U) | Bomb 2 per Spark card | Bomb 3 (4 upgraded) | It only fires on the Spark-priced cards. |
| Look Out! (U) | 3 Block per Mine | 4 (6 upgraded) | Mines fire more now that they answer attacks on allies (pick 1a). Still a narrow power. |
| Blast Shield (U) | 2 Sparks: 6 Block, returns | 1 Spark | 2 Sparks for 6 Block was a quarter of Dig In's rate. |
| Return to Sender (U) | 1 Energy + 2 Sparks | 1 Energy, no Sparks | It charged both currencies for 8 Block and a conditional Bomb. |
| Once More! (U) | 3 Sparks | 2 (1 upgraded) | Re-buying a Set off card is not worth 3 Energy's worth. |
| Sparkling Burst (U) | 3 Sparks | 2 (1 upgraded) | 3 Sparks for 1–2 Energy lost Energy on the trade. |
| Blazing Delight (R) | 2 Energy + 5 Sparks | 2 Energy + 3 Sparks (2 upgraded) | Five Sparks is two or three turns of income before the power does anything. |

## Left alone, and watched

- **Rapid Fire (2 cost).** Four Set offs on one enemy do nothing after the first,
  so it is only good with several enemies. That may be the right place for it.
- **The payoffs.** Pop!, Bang Bang!, Big Badda Boom, Windblume Fireworks, Sparks
  'n' Splash and The Big One are already strong. [USER]'s run and both seat reads
  found no trouble there.
- **Any Klee starter card.** Starter basics are never changed.

## What the next read should look for

- Whether Sparks now run short more often than they sit idle.
- Whether the cheaper sinks (Blast Shield, Once More!, Sparkling Burst) get
  bought, and whether Spark Knight becomes the automatic Rare.

## Follow-up, 2026-09-25 afternoon (two blind seats, Codex and Opus, on 0.2.3766)

- **The loop reads.** Both seats found the real decision on their own: set off now or
  let the Bombs grow a turn, timed against the enemy's intent.
- **Sparks still sit idle.** The Opus seat ended fights holding 2, 2, 4, 6 and 4 Sparks,
  and judged every Spark card it was offered weaker than a card that places Bombs. The
  Codex seat held Bottomless Bag dead at 1 Spark. Today's price cuts did not change the
  draft. Changed here: Bottomless Bag 2 Sparks → 1. The rest goes to [USER] as a pick.
- **Sparks 'n' Splash** fired after the Bombs were gone. It now fires at the start of
  the turn, after growth, and leaves the Bomb in place (upgrade: cost 1).
- **Favonius Escort** was the Codex seat's never-again (it spends a Bomb the deck wants
  for damage). One seat; watched, not changed.
- **Jumpy Dumpty** opened every Codex fight. It is a starter card; not changed.
