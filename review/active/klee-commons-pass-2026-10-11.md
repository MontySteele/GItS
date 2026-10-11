# Klee's Commons: an underperformer pass, 2026-10-11

After two Klee runs that both died to the act-1 boss, [USER] said:
- "I found enough weak-looking cards in the Klee pool that I think it's worth a balance audit for underperformers."
- "I think that Klee's Commons in particular felt bad, such that I expect they need the most review - and since we see so many of them, that would be a sizeable shift in power."

## The evidence

The census is in the session scratchpad (`klee-pool-census.md`). It covers:
- every Klee card's rate against the base five;
- take and play rates from 63 Klee runs since 2026-10-03 (58 seat runs and 5 of [USER]'s), read from the run files and telemetry;
- [USER]'s two runs from tonight.

The average card is taken about 25% of the times it is offered.

**Tonight's runs.** Both died to Waterfall Giant on turn 7, entering the fight at 32 of 70 and 30 of 58 HP. Each dealt more than the boss's 240 HP (273 and 270), so each was about one turn short. Block was not the gap: the rewards [USER] skipped held Bombs Away!, Windtrace, Booby Trap and Mine Toss, but the Block cards he did hold were Defends.

**How the rate is read.** Klee's damage is split between placing charges and cashing them:
- a Bomb deals its number when a Set off card cashes it, and grows by 2 a turn;
- a Mine also goes off when its enemy attacks;
- every Bomb that goes off pays back 1 Spark.

So a placer is worth its Bomb's number, a turn or more late, plus a Spark. A Set off card is worth a Ka-pow!, the free starter that sets off the enemy and deals 4. A Spark is priced at about 1.2 Energy (Explosive Spark deals 12 for 1 Spark; a base 1-Energy attack deals about 10).

## Her 25 Commons, sorted by what seats did with them

**Working (taken 40% or more, or played in 70% or more of fights held). No change:**
- Bombs Away! 50%
- Dig In 53%
- Windtrace 55%
- Quick Fuse 48%
- Countdown 40%
- Booby Trap 34% taken, 72% played
- Explosive Spark 33% taken, 76% played
- Forbidden Fun 77% played
- Coven Errand 73% played
- Blast Shield
- Boom Badge
- Bottomless Bag

**Already changed tonight (#1079):** Fish Blasting and Tinder Toss.

**Low, but doing a job. No change:**
- **Up in Smoke!** 17%. Two Weak on ALL for 0 Energy is above the base rate; it is a utility pick.
- **Hair Trigger** 18%. A 0-cost cycle card for Mine decks.
- **Run Away!** 24%. Seven Block for 0 Energy after a Bomb goes off. Klee is fast and fragile by ruling, so her free Block stays small.
- **Fire! Fire!** 23%. Bomb 7 placed and set off at once is 7 damage now plus a Spark back, about the base rate.

**Underperformers: below rate AND rarely taken. These are the proposals.**

| Card (cost) | Today | Taken | Why it's weak | New |
|---|---|---|---|---|
| Pocket Match (0, Retain) | Set off only your largest Bomb. Deal 3 [5]. | 9% of 85 | It does less than the free Ka-pow! you already hold | Deal 6 [9] |
| Simmer (1) | Deal 4 [6] plus half your largest Bomb; it doesn't go off. Add a Dazed. | 0% of 16 | About 9 damage for 1 Energy with a Bomb 10, and a Dazed | Deal 6 [9] plus half your largest Bomb. No Dazed |
| Sizzle (1) | Set off. Deal 6, +6 if a Bomb reacted this turn. No upgrade. | 16% of 56 | A Ka-pow! plus 2 for 1 Energy; Flash Point does more at Uncommon | Deal 8 [11], +6 on a reaction |
| Chain Fuse (1) | Each Bomb on the enemy grows by 6 [9] | 14% of 73 | Six late damage for 1 Energy with one Bomb out; Quick Fuse grows 3 and sets off for a Spark | Grows by 9 [12] |
| Lizard-Tail Gunpowder (1) | Place a Bomb 6 [9]. Draw 1 for each Bomb that went off this turn. | 13% of 82 | Its Bomb is under Mine Toss's, and the draw needs a Set off first | Bomb 8 [11] |
| Mine Toss (1) | Place a Mine 9 [12] | 14% of 69 | Tonight's Alice's Mine is a free Mine 10 every turn; the paid Common should be bigger | Mine 11 [14] |
| Blasting Spree (1) | Place a Bomb 4 [6] on ALL. Add a Dazed. | 8% of 12 | Bomb 4 on ALL is under a base AoE attack's 7, and it carries a Dazed | Bomb 6 [8] on ALL, Dazed kept |

- These are seven of her 25 Commons. Each moves by about 2 to 3, the size of one upgrade.
- No card gains a new effect, and none loses its core decision. Simmer's Dazed is the only drawback removed. It was the reason a 0%-taken card stayed dead, and Simmer is the cook loop's payoff.

## How it is checked

A whole-run Klee seat round on the five base-five seeds, after these and the #1079 changes. Lines:
- the seven cards are taken in at least 20% of offers, pooled;
- act-1 boss deaths: none in five (tonight [USER]'s were 2 of 2);
- act-1 normal fights are no shorter than 10% below base, so the act is not trivialised.

[USER]'s "playtest sweep" decision follows the round.

## For [USER]

Klee is at Balance, so these are your picks.

1. **The seven Commons above.**
   - **(a) Default:** all seven as listed.
   - (b) Only the five below 15% taken: Pocket Match, Simmer, Chain Fuse, Lizard-Tail Gunpowder, Blasting Spree.
   - (c) None. Read the #1079 changes on their own first.
2. **Simmer's Dazed.**
   - **(a) Default:** remove it.
   - (b) Keep it and deal the full largest Bomb instead of half, the Wild Strike shape: a drawback that buys a bigger number.
