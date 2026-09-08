Status: OPEN (four picks, §8)

# Furina, the Tide, second pass: nothing heals by the turn, so nothing is gained by waiting

Written 2026-09-07, night; second pass the same night after GPT's read of
the first (PR #443). The first pass bounded healing with an entry line, a
meter cap and an exclusion clause, and GPT showed each one leaking: the entry
line still pays for stalling inside a fight, it locks Spend for a fight
entered below half, the two Powers rebuilt the automatic loop, and the
worked fight skipped Regal Bearing's Weak and assumed an unplayed card would
be there next turn. All four are taken. The answer is not another boundary;
it is to remove the thing the boundaries were guarding. **In this pass no
card heals by the turn.** Recovery comes from kills and from the Burst, both
of which end fights rather than prolong them. Numbers are illustrative
unless a file is cited.

## 1. Why the Kokomi precedent does not disqualify this

`docs/current/characters/kokomi-kickoff-v1.md` records the standing axis
"Furina = HP volatility, Kokomi = HP stability", and Kokomi's first binding
law is no self-damage anywhere, because "the moment a Kokomi card costs HP,
the Furina boundary blurs." A partition, not a balance failure: the HP engine
was reserved for Furina and never built. The lesson to carry is the one
`docs/current/research/ironclad-brief-calibration-2026-09-01.md` §4 draws
from Burning Blood: "the relic makes a whole verb affordable before its cards
appear," and self-damage reads as a deal because the relic pays it back at
the end. That is the shape used here.

## 2. The character in three sentences

Furina's party is the show, and the show is HP moving. Her Attacks hit harder
when she **Spends** her own HP, allowed only while she is above half; her
Salon members are Powers that Spend for her every turn. Every point of HP an
ally loses, to a hit or to a Spend, fills her Burst, and being low fills it
faster; the Burst and the end of each performance are how HP comes back.

The screen shows the HP bar with the half-line marked and the Burst meter
every character already has. Nothing else is counted.

## 3. The rules, five, each with its job

- **Spend N.** A rider on Attacks: pay N HP before the hit for the larger
  number ("Deal 7. Spend 4: deal 12 instead."). Allowed only above half HP.
  Job: the wager, and the half-line as the thing you play around.
- **Fanfare** is her Burst meter, not a separate counter. It rises by 1 per
  HP any ally loses, to damage or to Spend, and by 2 per HP while Furina is
  below half. Nothing that heals fills it. Job: the payoff timer, and the
  comeback: the lower the show runs, the sooner the Burst.
- **Let the People Rejoice**, the kit-Burst (granted on fill, never in the
  pool): Restore 8 to each ally and deal 12 to all enemies; the meter
  empties. Job: the one big heal and the one big hit, earned by what the
  party has taken.
- **Standing Ovation**, her starting relic: whenever an enemy dies, Furina
  Restores 4. Job: recovery bound to ending fights, the Burning Blood shape;
  relic-scale trickles are already exempt from the healing law
  (`docs/current/LAW.md` line 200).
- **The Salon** is Powers, one per member, each "at the end of your turn, if
  above half HP, Spend N:" and then its act: Crabaletta Spend 2 for 8 damage
  to a random enemy; Usher Spend 1 for 4 Block to each ally; Chevalmarin
  Spend 1 for Hydro on all enemies. Job: the cast you manage, the support the
  party feels, and a drain you chose to run. No Singer: nothing in the Salon
  heals.

Gone from the first pass: the entry line, the meter cap, the Burst exclusion
clause, Restore Skills and the Singer Power. Rare true heals stay as the law
has them, Rare and Exhaust.

## 4. GPT's four problems, each answered by the same rule

1. **Stalling.** Nothing heals by the turn. Delaying a kill gains no HP,
   costs the hits you keep taking, and only fills the meter with the damage
   you chose to eat. The Burst heals 8 and needs roughly 25 HP of losses
   above half; eating hits to reach it is a losing trade by construction.
   The only heal that scales with time is none. Enemy escalation is not
   needed as an argument.
2. **A fight entered below half.** Spend and the Salon are closed. That is
   the weakness, and it is deliberate: below half she is a plain character
   with modest numbers, which the identity record already declares her to
   be. The three ways back are all fast: every kill Restores 4 (a hallway
   fight with three bodies is 12), the meter fills at double rate so the
   Burst is close, and the Burst Restores 8. The half-line's height is a
   constant the sim tunes (§8, D).
3. **The Powers.** No Salon member heals, so the cast is a drain, not a
   loop: three members out is 4 HP a turn for 8 damage, 4 Block to each
   ally and Hydro on everything. It stops itself at the half-line. Whether
   assembling three members is the intended payoff is a yes: it is the
   Salon-management loop [USER] asked to keep, and the drain is its price.
4. **The examples** are redone in §5 and §6 with Weak counted, no card
   assumed to be in hand next turn, and no Spend made for the meter's sake.

## 5. One fight, with the starter

Starter, illustrative: four Soloist's Solicitation (6), four Stage Presence
(Block 6), Regal Bearing (Block 3, Weak 1), two Curtain Rise ("Deal 7.
Spend 4: deal 12 instead."). Furina 78 of 78, half-line 39, meter fills at
25. Enemy 42 HP; intents 11, then 7 and 5 Block on its turn, then 11. Weak
takes a quarter off, rounded down.

| Turn | Hand and play | Rejected, and why | HP after enemy | Meter |
|---|---|---|---|---|
| 1 | Curtain Rise, Solicitation ×2, Presence, Bearing. Curtain Rise with Spend (78 to 74) for 12, Solicitation 6, Bearing: Weak makes the 11 an 8, Block 3, 5 through | Presence instead of Bearing: Block 6 against 11, also 5 through, and no Weak next turn; or Curtain Rise unspent for 7, enemy at 29 not 24 | 69 | 9 |
| 2 | Solicitation ×2, Presence ×2, Curtain Rise. Curtain Rise with Spend (69 to 65) for 12, Solicitation 6, enemy at 6 before it Blocks; Presence 6 against 7, 1 through | No Spend: enemy at 11 and 5 Block behind it, 16 to find on turn 3 against a hand of 6s | 64 | 14 |
| 3 | Solicitation ×2, Presence, Bearing, Curtain Rise. Solicitation ×2 for 12 on 6 HP and 5 Block: dead. Standing Ovation Restores 4 | Curtain Rise with Spend first: 4 HP for 4 meter with the kill already in hand. Not taken; the meter fills from hits anyway and the wager is for when the number is needed | 68 | 14 |

The fight cost 10 HP, 8 of it by choice, and put 14 on a 25 meter. The next
fight opens at 68, above the line, with the Burst two fights away or one bad
one.

**The contested turn**, redone: 44 of 78, an intent of 15, hand Curtain
Rise, Solicitation, Presence, Bearing, Solicitation. With Weak the 15 is an
11. Bearing and Presence hold 9 of it: 2 through, 42, still above the line,
Spend open next turn, and one Solicitation for 6. Or Curtain Rise with
Spend (to 40) for 12 and Solicitation 6, Bearing alone: 8 through, 32,
under the line, Spend closed until a kill or the Burst, meter +4 +8. Eighteen
damage now against six and an open engine tomorrow. That is the turn, and
it is the seat's to find.

## 6. The two cases GPT asked for

**A fight entered below half.** 30 of 78 against a 45-HP enemy hitting 8 a
turn. Spend closed; the hand is 6s and Block. Turn 1: two Solicitations and
a Presence, 2 through, 28, meter +4 (double). Turn 2: two Presences and a
Solicitation, nothing through. Turn 3: three Solicitations to leave it at 9,
8 through, 20, meter +16, at 20 of 25. Turn 4: two Solicitations kill it,
Standing Ovation to 24. She leaves at 24, the meter at 20: the next hit she
takes anywhere fires the Burst, Restore 8 and 12 to all. Four turns of a
plain character, then the comeback. Whether that is felt as a weakness or a
dead mode is the sim's fraction of fights entered below half, and [USER]'s
play.

**A prolonged easy fight.** An enemy hitting 3 a turn that she could kill
on turn 2. Killing on turn 2: Standing Ovation 4, meter +3 from one hit.
Delaying five turns: no card heals, so she is 15 HP lower and the meter is
15 higher, and the Burst, when it comes, gives back 8. Waiting is strictly
worse, and no rule had to say so.

## 7. Her plans, three, separated by card slots

- **The Salon (default, solo floor):** Curtain Rise and its Uncommon
  siblings, the three member Powers, Block cards that guard the half-line.
  Wants HP above half and a Presence in hand.
- **The Fanfare deck (velocity):** cards that take or Spend HP fast to reach
  the Burst twice a fight, and the Rare true heals, Exhaust as the law has
  them. Wants to be hit and to answer it.
- **The Guest Cast (draft-gated ceiling):** Chevalmarin's Hydro and the
  Companions who react off it; in co-op the party's losses fill her meter
  and Usher's Block reaches them. Wants Companions.

The statline moves as in the first pass: the weakness is the half-line, not
the frontload. On the healing law: no card below Rare heals in this pass.
Standing Ovation is a relic trickle, exempt; the Rare heals are as written.
The one open question is whether the kit-Burst, which is not in a rarity
tier, may Restore, and that is asked below as narrowly as it can be.

## 8. What is asked

1. **The Burst may heal (C, `LAW.md` line 200).** Default: yes, the
   kit-Burst is out of the pool and outside the tiers, and its 8 is the one
   card-scale heal in the kit. 2: no, the Burst deals damage only and
   Standing Ovation is her whole recovery.
2. **The half-line's height (D, applied).** Default: 50 percent of max HP,
   a constant, the sim tunes it on the fraction of fights entered below it.
3. **Usher's Block reaches allies in co-op.** Default: yes, "each ally" is
   the printed target and in solo that is Furina. 2: Furina only, a co-op
   card later.
4. **Next step.** Default: the one-page brief revision from this pass, then
   a `+proto` build and a seat round on the two questions in the concepts
   packet. 2: a third sketch pass first.
