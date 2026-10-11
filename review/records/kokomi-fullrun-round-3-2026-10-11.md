# Kokomi whole-run round 3, 2026-10-11

This round grades the fixes that followed [USER]'s 2026-10-10 run ("energy-starved", "the one turn penalty is currently too punishing"):
- **The Casket:** Open the Casket costs 0, then 1 more each play that fight (#1067); Grand Design fetches it each turn (#1064).
- **Plan pricing:** nine Plan cards pay 1.3 times the base on-turn median (`review/active/kokomi-plan-pricing-2026-10-11.md`, #1069).

How the round ran:
- Five whole-run Sonnet seats on the base-five seeds, A0, build 0.2.4844+next.
- The packet, records and scripts are in the session scratchpad (`kokomi-fullrun-r3/`, `kokomi-r3-packet.md`), which is gitignored.
- A Fable reviewer reviewed the round (`kokomi-r3-review-fable.md`). The main session accepted the review with one rejection, listed at the end.

## Result: 0 of 5, as deep as the base seats

| Seed | Round 3 | Round 2 | Base, whole-run (10-10) |
|---|---|---|---|
| CYHZM9S0VPW6 | floor 48, the Queen (act-3 boss) | floor 39 | floor 33 |
| DJCAV76ZKAUN | floor 31, Entomancer (act-2 elite) | floor 8 | floor 24 |
| 30KMHAVG9SMQ | floor 48, the Queen | floor 33 | floor 33 |
| YEWA0B7AVE45 | floor 48, Test Subject (act-3 boss) | floor 40 | floor 33 |
| R41TX5Q0ZQYN | floor 33, Kaiser Crab (act-2 boss) | floor 33 | floor 33 |

The mean death floor is 41.6, against 30.6 in round 2 and about 39 for the pooled base seats. All five beat the act-1 boss.

**The three lines:**

| Line | Measured | Result |
|---|---|---|---|
| Act-1 normal fights: 9.0 HP lost or less | 8.4 (n=36; round 2 11.0; base 5.6) | Pass |
| Act-2 boss: median damage a turn, 40 or more | 37.9 (n=4; round 2 38.4; base 39.4) | Miss, within noise |
| Act-1 normal fights not more than 10% shorter than base | 3.3 turns against 3.0 to 3.1 | Pass |

## What played well

- **The decisions.** Every record names the same four:
  - Plan or now;
  - the order of the queue (Opening Gambit before Oath turned 12 into 36);
  - when to Open the Casket;
  - writing Plans after the Strength comes in.
- **The repriced cards.** Taken in 51% of offers, up from 43%. Jellyfish Drift went 7 of 11, Nip 4 of 6, and Bubble Ward 3 of 5 (0 of 5 before).
- **The Casket hold.** It reached Strength 30 once in 102 fights; the median top Strength is 2.
  - The one big hold cost three potions and a whole fight's defence, and still came in under the boss line.
  - It is the kit's Limit Break. No change.

## What did not

- **Act-2 normal fights** cost 15.6 HP against base's 10.9, at the same length, so she blocks less of what comes in. Three causes:
  - Act-2 enemies blunt her shape. Artifact eats her Weak and Frozen Plans; Toxic and Dazed clog her hand. Her status answers were offered 23 times and taken 0 (Tidecleanse, Kelp Wall, Turning Tide, Abyssal Salvage).
  - Block from a Plan lands next turn, against a swing you cannot see yet, and the seats could not tell when it arrives.
  - Drafted decks were thin on Block.
- **The debuff and reaction cards** were offered 25 times and taken 0: Drowning Pressure, Undercurrent Snare, Salt in the Wound, Sea's Reproach, Suffocating Deep, Tidal Resonance and At Water's Edge.
- **Gorou — Inuzaka All-Round Defense** says "half the damage dealt", but the code gives half of the damage that gets past Block. Lane 3 counted on 11 Block, got about 1 against the Queen's 20 Block, and died.

## What changes

**Built, with no approval needed:**
- Gorou's face now says "half the unblocked damage".
- Undertide Lance's Plan line names "the front enemy".
- The Plan tip says when Plan Block lands.
- Kelp Wall shows its live Block in combat.
- Drowning Pressure deals 5 [7] per debuff.

**Act-2 boss line.** It is kept at 40 with no lever. Round 4's bosses pool with these (n=8) before any number moves. If it still misses, the lever is Depths' Judgment, 3 to 4 per Casket point.

**Rejected from the review: Change of Plans dropping Exhaust.**
- A free card that carries out a Plan now and draws, with no Exhaust, lets a deck cash every Plan on the turn it is written. That removes the delay the kit is built on.
- [USER] said the tension "works"; the problem was the price, which the pricing pass fixed.
- The card stays as it is.

**Unverified checks** (BACKLOG): Thieving Hopper's Flutter halving Opening Gambit, a Skill; Iron Club never visibly drawing.

## Is she near her finish line?

Yes:
- the pool is 78;
- five whole-run seats have played this build;
- she reaches act 3 as the base seats do, and her bosses are at base.

What remains is [USER]'s full run, after the text fixes deploy. Things to watch in it:
- the act-2 hallways;
- the free first Casket against the hold;
- whether Change of Plans or Tidecleanse ever looks worth a pick.

## Round 4, pooled (2026-10-11, 05:57)

The review asked for one more round before any lever on the act-2 boss line. Five seats played the same seeds on build 0.2.4870+next, with the text fixes above in. The packet is `kokomi-r4-packet.md` in the scratchpad.

| Seed | Round 4 |
|---|---|
| CYHZM9S0VPW6 | floor 48, the Queen |
| DJCAV76ZKAUN | floor 22, Louse Progenitor (entered at 6 HP) |
| 30KMHAVG9SMQ | floor 39, Slimed Berserker (at 2 HP, after a Regret curse) |
| YEWA0B7AVE45 | floor 43, Soul Nexus elite |
| R41TX5Q0ZQYN | floor 33, Kaiser Crab |

The three lines, rounds 3 and 4 pooled:

| Line | Pooled | Result |
|---|---|---|
| Act-1 normal fights, 9.0 HP lost or less | 8.8 (n=69; round 4 alone 9.2) | Pass |
| Act-2 boss, median damage a turn, 40 or more | 40.5 (n=8; base 39.4) | Pass |
| Act-1 normal fights not more than 10% shorter than base | 3.25 turns against 3.06 | Pass |

Other findings:
- **Act-2 normal fights** cost 11.6 HP in round 4, against base's 10.9 to 12.1. In round 3 they cost 15.6. Block a turn rose from 5.9 to 8.0. One lane (24 HP over 3 fights) carries most of the pooled 13.9.
- **The debuff and reaction cards** have now had 39 reward offers and 0 takes over two rounds.
- **Flagged items:**
  - A Plan "hitting a Minion" was an ALL Plan, which is correct.
  - Tide Wall+ reads only the front enemy's intent. Its text now says "front enemy".
  - The rest are consistent with the rules, or the data can't tell.

What this changes for the picks below: pick 1's case (Block Plans at 1.5) is weaker, because act 2 came back to base without it. The default stays hold.

## For [USER]

These are decided after your run, not before.

1. **The rate on Block Plans.**
   - **(a) Default:** hold.
   - (b) 1.5 times base on Block Plans only (Bubble Ward 6, Kelp Wall 8), because Block from a Plan can't be aimed at a swing you can see. This reopens the ruled 1.3 ratio on one new fact: act 2 did not improve while act 1 did.
2. **Kurage's Oath (starter).** Every lane wrote it as a Plan and almost never played it for Block.
   - **(a) Default:** leave it.
   - (b) Reprice it at the 1.3 ratio (9 to ALL).
3. **The debuff and reaction cards** (seven cards, 0 of 25 offers). Blind seats draft printed numbers, so this needs your eyes.
   - **(a) Default:** keep them and watch in your run.
   - (b) A pass on them next.
