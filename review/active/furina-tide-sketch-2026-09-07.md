Status: OPEN (five picks, §8)

# Furina, the Tide, third pass: the curtain never falls, it turns

Written 2026-09-07, night; third pass after GPT's read of the second
(PR #443). The second pass removed every heal by the turn, and GPT showed
what that cost: the below-half example demonstrated a shutdown, not a
comeback (she still could not use Spend or the Salon after the Burst); the
"nothing is gained by waiting" claim was false at a nearly full meter; three
Powers that drain until a line are an engine you install, not a cast you
manage, and their resolution order could switch Usher off mid-performance;
and Usher leaving when she is hurt reads as "strong while healthy,
diminished while hurt", which is a character, but not the one the Tide was
picked for. All four are taken. The principle this pass is built to is
GPT's: **when Furina is injured her opportunities change, and she still has
something distinctly hers to do.** The healing sources of the second pass
stay (no heal by the turn; kills and the Burst). What changes is what the
half-line does: it turns the show instead of stopping it. Numbers are
illustrative unless a file is cited.

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

Furina's party is the show, and the show has two acts. Above half HP the
cast attacks and Spends her HP to do it; below half the same cast turns to
the audience: they protect the party and raise the applause that brings the
Burst. The Burst heals, hits, and raises the curtain for one more act at full
strength, whatever her HP.

The screen shows the HP bar with the half-line marked and the Burst meter
every character already has. Nothing else is counted.

## 3. The rules, five, each with its job

- **Spend N.** A rider on Attacks: pay N HP before the hit for the larger
  number ("Deal 7. Spend 4: deal 12 instead."). Allowed only above half HP.
  Job: the wager, and the half-line as the thing you play around.
- **Fanfare** is her Burst meter, not a separate counter. It rises by 1 per
  HP any ally loses, to damage or to Spend, and by 2 per HP while Furina is
  below half. Nothing that heals fills it. Job: the payoff timer.
- **Let the People Rejoice**, the kit-Burst (granted on fill, never in the
  pool): Restore 8 to each ally, deal 12 to all enemies, and **the curtain is
  up until the end of your next turn: Furina counts as above half.** The
  meter empties. Job: the one heal, the one big hit, and a recovery window
  you can use: one turn of Spend and the full Salon, whatever the bar says.
- **Standing Ovation**, her starting relic: whenever an enemy dies, Furina
  Restores 4. Job: recovery bound to ending fights, the Burning Blood shape;
  relic-scale trickles are already exempt from the healing law
  (`docs/current/LAW.md` line 200).
- **The Salon** is Powers, one per member, and each member has two lines,
  performed at the end of your turn. **Above half:** Crabaletta Spend 2, deal
  8 to a random enemy; Chevalmarin Spend 1, Hydro on all enemies; Usher
  Block 4 to each ally. **Below half:** Crabaletta raises 2 Fanfare;
  Chevalmarin Hydro on one random enemy, free; Usher Block 4 to each ally,
  the same. Usher never leaves. The half-check is made **once, when the
  performance begins**: if she is above the line then, every member performs
  the upper line this turn even if a Spend crosses the line mid-way, and the
  members perform in the order they were played. Job: the cast on stage in
  both acts, and a drain that stops itself.

Gone since the first pass: the entry line, the meter cap, the Burst
exclusion clause, Restore Skills and the Singer Power. Rare true heals stay
as the law has them, Rare and Exhaust. Nothing heals by the turn.

## 4. GPT's four problems, and what each changed

1. **The below-half example showed a shutdown.** Now the below-half act is
   a mode with its own job: the cast protects and applauds, the meter fills
   at double rate, and the Burst, when it comes, gives one turn of the
   whole engine plus 8 HP plus 12 damage. §6 redoes the example and it now
   ends with a Burst turn, a kill and an open engine, not four plain turns.
   With no member on stage she is still a plain character below half; that
   is a pool question (the Fanfare deck in §7 is the below-half plan), not
   a rule.
2. **"Strictly worse" was false at a nearly full meter.** Withdrawn. §6 now
   shows the 23-of-25 case as the trade it is, and names the number the sim
   reports and the question the seat answers. Occasionally taking a hit to
   reach the payoff is the appeal; the risk is that it becomes a chore, and
   that is measured, not argued.
3. **The Salon is an engine you install.** Agreed, and the packet no longer
   says otherwise. What is managed is the bar around it: which members go
   out and in what order, how far to Spend toward the line before the show
   turns, and when to fire the Burst so its open turn lands on a hand that
   can use it. The mid-performance ordering problem is closed by the
   once-per-performance check.
4. **Usher left when she was hurt.** Usher's line is the same above and
   below. The duality is now in the cast's two lines, not in whether the
   cast works.

## 5. One fight, with the starter

Starter, illustrative: four Soloist's Solicitation (6), four Stage Presence
(Block 6), Regal Bearing (Block 3, Weak 1), two Curtain Rise ("Deal 7.
Spend 4: deal 12 instead."). Furina 78 of 78, half-line 39, meter fills at
25. Enemy 42 HP; intents 11, then 7 and 5 Block on its turn, then 11. Weak
takes a quarter off, rounded down. No member is on stage: the starter has
none, and this fight is the character without the Salon.

| Turn | Hand and play | Rejected, and why | HP after enemy | Meter |
|---|---|---|---|---|
| 1 | Curtain Rise, Solicitation ×2, Presence, Bearing. Curtain Rise with Spend (78 to 74) for 12, Solicitation 6, Bearing: Weak makes the 11 an 8, Block 3, 5 through | Presence instead of Bearing: Block 6 against 11, also 5 through, and no Weak next turn; or Curtain Rise unspent for 7, enemy at 29 not 24 | 69 | 9 |
| 2 | Solicitation ×2, Presence ×2, Curtain Rise. Curtain Rise with Spend (69 to 65) for 12, Solicitation 6, enemy at 6 before it Blocks; Presence 6 against 7, 1 through | No Spend: enemy at 11 and 5 Block behind it, 16 to find on turn 3 against a hand of 6s | 64 | 14 |
| 3 | Solicitation ×2, Presence, Bearing, Curtain Rise. Solicitation ×2 for 12 on 6 HP and 5 Block: dead. Standing Ovation Restores 4 | Curtain Rise with Spend first: 4 HP for 4 meter with the kill already in hand. Not taken; the wager is for when the number is needed | 68 | 14 |

The fight cost 10 HP, 8 of it by choice, and put 14 on a 25 meter.

**The contested turn**: 44 of 78, an intent of 15, hand Curtain Rise,
Solicitation, Presence, Bearing, Solicitation. With Weak the 15 is an 11.
Bearing and Presence hold 9 of it: 2 through, 42, above the line, Spend open
next turn, one Solicitation for 6. Or Curtain Rise with Spend (to 40) for 12
and Solicitation 6, Bearing alone: 8 through, 32, under the line, meter +4
+8, and from here the show turns: no Spend, but double meter and, with
members out, the applause. Eighteen damage now against six and the upper
act tomorrow. That is the turn, and it is the seat's to find.

## 6. The two cases GPT asked for, redone, and the third

**A fight entered below half.** 30 of 78 against a 45-HP enemy hitting 8 a
turn, Usher and Crabaletta on stage from the fight before, meter 14 carried
in (the second pass assumed the meter carries between fights; if it empties,
the meter numbers below start from 0 and the Burst comes a turn later).
Turn 1: Curtain Rise unspent 7, Solicitation 6, Bearing; the performance
gives Block 4 and 2 Fanfare; the Weakened 6 meets Block 7, nothing through.
Enemy 32, meter 16. Rejected: Presence for Bearing, Block 10 for the same
nothing and no Weak next turn. Turn 2: two Solicitations and Curtain Rise,
enemy 13; the performance Block 4 and 2 Fanfare; 8 against 4, 4 through at
double rate. HP 26, meter 26: the Burst is granted. Rejected: two Presences
and a Solicitation, nothing through, meter 18, and two more turns of 8.
Taking 4 to bring the Burst is the choice. Turn 3: Let the People Rejoice,
Restore 8 to 34, 12 to the enemy leaving 1, curtain up; a Solicitation
kills, Standing Ovation to 38. She leaves at 38 of 78, one below the line,
meter 0, having had one turn with the whole engine open. The next hallway
fight with three bodies is 12 HP and the upper act. Whether the below-half
act is felt as weakness or as a mode is still the sim's fraction of fights
entered below half and [USER]'s play; what the example now shows is that
she did Furina things on every turn of it.

**A prolonged easy fight, empty meter.** An enemy hitting 3 a turn that she
could kill on turn 2. Killing on turn 2: Standing Ovation 4, meter +3 from
one hit. Waiting five turns: no card heals, so she is 15 lower and the meter
15 higher. Waiting loses here.

**A prolonged easy fight, nearly full meter.** Meter 23 of 25, the same
enemy, lethal in hand. Kill now: Restore 4, the 23 carries to the next fight,
where the first 2 HP lost fires it. Wait a turn: take 3, the Burst is
granted, next turn Restore 8 and 12 damage onto a nearly dead enemy, then the
kill for 4: she exits 5 HP higher than killing now, and has spent the Burst's
12 damage and the carried meter on nothing. A trade, not a dominated line,
and sometimes the right one. The sim reports, per fight, the count of turns
where lethal was in hand and not taken, split by meter band; the seat round
asks "did you ever take a hit on purpose, and did it feel like a play or a
chore." If the deferred-lethal count is a habit rather than an occasion,
the lever is the Burst's heal, not a new rule.

## 7. Her plans, three, separated by card slots

- **The Salon (default, solo floor):** Curtain Rise and its Uncommon
  siblings, the three member Powers, Block cards that guard the half-line.
  Wants HP above half and a Presence in hand; below half, wants the members
  already out.
- **The Fanfare deck (the below-half plan):** cards whose lower line is the
  applause: Skills that raise Fanfare while she is below half, Attacks that
  hit harder during the curtain-up turn, and the Rare true heals, Exhaust as
  the law has them. Wants to cross the line on purpose and time the Burst.
- **The Guest Cast (draft-gated ceiling):** Chevalmarin's Hydro and the
  Companions who react off it; in co-op the party's losses fill her meter
  and Usher's Block reaches them. Wants Companions.

The statline moves as in the first pass: the weakness is the half-line, not
the frontload. On the healing law: no card below Rare heals in this pass.
Standing Ovation is a relic trickle, exempt; the Rare heals are as written.
The one open question is whether the kit-Burst, which is not in a rarity
tier, may Restore, and that is asked below as narrowly as it can be.

## 8. What is asked

1. **The identity, confirmed (A).** Default: an active offense/support
   relationship, as this pass builds it: above the line the cast spends her
   HP to hit, below it the same cast protects and applauds, and Usher never
   leaves. 2: HP expenditure with occasional recovery, the second pass as
   written, with the Salon off below the line.
2. **The Burst may heal (C, `LAW.md` line 200).** Default: yes, the
   kit-Burst is out of the pool and outside the tiers, and its 8 is the one
   card-scale heal in the kit. 2: no, the Burst deals damage and raises the
   curtain, and Standing Ovation is her whole recovery.
3. **The half-line's height (D, applied).** Default: 50 percent of max HP,
   a constant, the sim tunes it on the fraction of fights entered below it.
4. **Usher's Block reaches allies in co-op.** Default: yes, "each ally" is
   the printed target and in solo that is Furina. 2: Furina only, a co-op
   card later.
5. **Next step.** Default: the one-page brief revision from this pass, then
   a `+proto` build and a seat round on the two questions in the concepts
   packet plus §6's hit-on-purpose question. 2: a fourth sketch pass first.
