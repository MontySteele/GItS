Status: OPEN, draft 2 (direction ruled 2026-10-04; four picks at the end)

# Furina: re-founding the Stage (paper, draft 2)

**Where it comes from.** [USER], after the co-op run, 2026-10-03: "Furina
'technically works' in the sense that no individual component is broken,
but they do not play well with one another, and getting this any cleaner
requires fundamental design work." Draft 1 went to Fable and GPT for review.

**What is ruled.** [USER], 2026-10-04: "Let's go with 1a) and the rest of
your defaults, then draft a new paper for review." That rules:

- **1a.** Fable's split: Fanfare is a currency only, stage scaling is a
  separate drafted stat, and GPT's directing family is added.
- **Reopened.** The 2026-09-07 line ("must not be a Defect with Fanfare for
  Focus", `review/ruled/furina-identity-concepts-2026-09-07.md`) is
  reopened for a drafted scaling stat that is not Fanfare.
- **Guests keep their seat** against Salon summons.
- **Star guests pay their acts** from Furina's Fanfare, and skip the act
  when short.
- **The front shield is retired.** Her defence is Usher plus Block cards,
  raised in the same batch.
- **The starter pair** (Curtain Rise and Rising Applause) is decided
  together, here.

## 1. What draft 1 got wrong, from the reviews

- **Merging scaling and currency.** With Fanfare as both, one held point
  was worth about 3 every turn (Usher 3, Chevalmarin 2, Crabaletta 5), while
  Curtain Rise's Spend was worth about 3.3 once. Holding always won (Fable
  and GPT).
- **It did not fix the trio-against-guests clash.** With one queue,
  Crabaletta onto a full stage still Bowed a Rare guest (Fable).
- **"Nothing scales" was overstated.** Full House, Arkhe Alignment and
  Sold Out scale the stage. What is missing is steady growth in each act's
  number (GPT).

Kept from draft 1: the diagnosis (one bar, four jobs, plus the fade), and
the cut to performers with no bars.

## 2. The rules

1. **Three seats, performers with no bars.** Performers take no hits and
   cannot be emptied. Each performer acts at the end of Furina's turn,
   from any seat. A performer that leaves takes a Bow: it acts once more.
   Combat opens with Usher on stage (Salon Solitaire, her starting relic).
2. **Two kinds of performer, two jobs.**
   - The **Salon trio** (Usher, Chevalmarin, Crabaletta) is the cycling
     floor: cheap summons, cloneable, made to Bow.
   - A **Guest Star** is the cast you keep. One of each; a second copy
     Bows it and returns it.
3. **The overflow rule.** A summon onto a full stage Bows your front-most
   Salon member. With no Salon member on stage, the front performer Bows.
   So a guest leaves only to another guest, to a card that says so, or
   when it stands with no Salon member in front of it.
4. **Fanfare is one number on Furina.** It has no cap and no fade, and
   hits never touch it.
   - **Filled by:** her Raise cards ("Gain N Fanfare"), the support guests'
     acts, reactions (Tide of Applause), and **1 per Bow** (pick 1). That
     last one joins the halves: the trio's churn feeds the guests' upkeep.
   - **Drained by:** Spend N, a mode on her cards (unchanged from rule 8,
     paid from the one number), and the star guests' acts. A star that
     cannot pay skips its act and stays on stage.
   - **Read by:** Bravura, Ousia Surge, Leading Lady, Let the People
     Rejoice and Navia. Banking for a finale works every fight; that is the
     19-Fanfare, 81-damage Bravura turn of the 2026-10-01 round
     (`review/records/furina-pool-round-2026-10-01.md`).
5. **Rehearsal** (working name, pick 2) is the stage's scaling. It comes
   from drafted Powers: "Your performers' acts deal and give 1 more."
   Per `LAW.md` ("empowerment boosts numbers only, never turn-economy
   effects") it raises damage and Block only, never Energy, draw or Fanfare.
   It needs no new display: the act numbers on the performers go up. Full
   House, Arkhe Alignment and Sold Out stay as the multipliers.
6. **Cue.** A new verb: "Cue your front performer" means it acts now, as
   at the end of the turn, and a star pays as usual. This is the directing
   family (sec.4). A Cue with no one in that seat does the card's plain
   effect instead.
7. **Retired:** per-performer bars, damage absorption, the front shield,
   the shield and bank seats, the fade, Wriothesley's "always front", and
   the newcomer inheriting the leaver's Fanfare.

The Solo path (no one on stage: Solo Verse, Soliloquy, One-Woman Show)
stays a side route. Genshin's drain lives on Sigewinne and on a Power
("whenever you lose HP, gain 1 Fanfare"), not as a base rule.

## 3. The cast

| Performer | Kind | Act (end of turn; Bow = once more) |
|---|---|---|
| Usher | Salon | 4 Block (was 3: the shield's job moves here) |
| Chevalmarin | Salon | 2 damage to ALL |
| Crabaletta | Salon | 5 damage to a random enemy |
| Neuvillette | Star | pay 2: 7 Hydro to ALL |
| Clorinde | Star | pay 1: 8 Electro to a random enemy |
| Lyney | Star | pay 1: 5 Pyro to a random enemy, twice |
| Escoffier | Star | pay 2: 3 Cryo to ALL, then your Salon members act |
| Navia | Star | Geo damage to a random enemy equal to half your Fanfare (reads, never pays) |
| Chevreuse | Support | pay 2: next turn, gain 1 Energy |
| Charlotte | Support | gain 2 Fanfare |
| Sigewinne | Support | gain 1 Fanfare, plus 1 for each time you lost HP since her last act |
| Wriothesley | Support | 4 Cryo to a random enemy, plus 1 per damage your Block stopped since his last act |
| Lynette | Support | 3 Anemo to a random enemy, one with an aura if any |

Arrival Fanfare goes: a guest's card gives Furina its Fanfare on arrival
(Neuvillette's "joins with 6" becomes "Summon Neuvillette. Gain 4
Fanfare."). The sim sets every number above. These are opening values.

## 4. The pool: what moves

The pool stays 78. About 30 rows change, by family:

- **Directing (new Commons, from the seat-arranging rows).** Step Forward,
  Plot Twist, Revolving Stage and Stage Whisper lose their job and become
  Cue cards. Examples: "Cue your front performer. Gain 4 Block."; "Deal 6
  damage. Cue your back performer." Bis!, Tutti! and Oratrice's Verdict
  already belong here.
- **Raise.** "Your back performer gains N" becomes "Gain N Fanfare":
  Warm Reception, Hold Your Places, Cheered On, Opening Number, Season
  Tickets, Groundswell, Singer of Many Waters.
- **Readers** read the one number: Ousia Surge, Leading Lady, Pneuma
  Refrain, Bravura, Bring the House Down ("Spend all your Fanfare: deal N
  per point to ALL").
- **Bow cards** keep their job (the trio is made to Bow): Final Bow,
  Intermission, Grand Finale, Da Capo, Thunderous Applause and A
  Five-Century Act.
- **Rehearsal Powers:** one Uncommon (+1, upgraded +2) and one Rare,
  replacing two rows whose premise is gone (Counterclaim, Interposition).
- **Defence:** Usher's act rises to 4, and Regal Bearing and two other Block
  rows are raised once the sim reads the new damage.
- **Critics' Darling** takes [USER]'s idea: "Whenever your Fanfare
  changes, deal that much damage to a random enemy."
- **Co-op:** Guest of Honor, Share the Spotlight and The Crowd Roars are
  rewritten on the one number.

## 5. The starter pair (decided here)

- **Curtain Rise** (Basic Attack, 1): "Deal 7 damage. Spend 3: deal 17
  instead." Unchanged. It teaches the currency.
- **Rising Applause** (Basic Skill, 1): "Gain 3 Fanfare. Cue your front
  performer." (upgraded: Gain 4.) It teaches the other two verbs, filling
  the bank and directing the stage. On turn one it is Usher's 4 Block now
  plus 3 Fanfare toward Curtain Rise's Spend.

Both start at these values. Strike and Defend do not change.

## 6. How it gets proven

1. **Sim first.** Build the rules and about a dozen rows in the tier0 twin:
   the starter pair, the trio, Take the Stage, three Cue Commons,
   Neuvillette, Charlotte, Navia, Bravura and the Uncommon Rehearsal Power.
   It sets the opening numbers and answers the main risk Fable named: a
   bank with no fade can be hoarded for free. The test is whether star
   upkeep and strong Spends drain it enough.
2. **Then the C#** and the rest of the ~30 rows.
3. **A rule change**, so [USER] plays it and a two-seat round reads it.
   GPT's questions are the checklist:
   - Does keeping a favourite cast produce interesting turns?
   - Are trio summons still wanted after guests arrive?
   - Can an ordinary draft defend while developing?

Already built and kept: Tutti! at 1 and Gala Premiere at 1. The
start-of-turn fade (#881) becomes moot when the fade is retired.

## Picks

1. **A Bow gives 1 Fanfare**, as a base rule joining the trio's churn to the
   guests' upkeep. Default: yes. (Or Bows give nothing and Thunderous
   Applause stays the only Bow payoff.)
2. **The scaling stat is called Rehearsal.** Default: yes. (A taste call;
   anything that does not collide with an existing keyword works.)
3. **The overflow rule** (sec.2, rule 3): a full-stage summon Bows the
   front-most Salon member, or the front performer if there is none.
   Default: yes. (Or a summon onto a stage of three guests is refused.)
4. **The starter pair** as in sec.5. Default: yes.
