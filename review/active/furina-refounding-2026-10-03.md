Status: RULED, draft 4 amended (third reviews taken 2026-10-04, sec.8); the sim slice is specified in sec.9

# Furina: re-founding the Stage (paper, draft 4)

**Where it comes from.** [USER], after the co-op run, 2026-10-03: "Furina
'technically works' in the sense that no individual component is broken,
but they do not play well with one another, and getting this any cleaner
requires fundamental design work."

**What is ruled.**
- **2026-10-04, "Let's go with 1a) and the rest of your defaults":**
  - Fanfare is a currency on Furina;
  - stage scaling is a separate drafted stat;
  - directing is a card family;
  - the 2026-09-07 "not a Defect with Fanfare for Focus" line is reopened,
    only for a stat that is not Fanfare;
  - guests keep their seat against Salon summons;
  - stars pay their acts from Fanfare;
  - the front shield is retired;
  - the starter pair is decided together.
- **2026-10-04, on draft 3** ("in general I'm opposed to arbitrary caps ...
  Guest Stars can't just be 'damage and element' ... the opportunity cost
  of directing the Stage becomes larger than the payoff"), then "Yep, this
  sounds good to me!":
  - **no caps:** a card that reads Fanfare without spending it reads this
    turn's flow;
  - **guests bend rules, the trio carries the numbers.**

**Draft history.**
- Draft 1 merged scaling and currency; holding always won.
- Drafts 2 and 3 took Fable's and GPT's reviews.
- Draft 4 takes [USER]'s two rulings above. Sec.7 lists what each draft
  took.

## 1. The rules

1. **Three seats, performers with no bars.** Performers take no hits and
   cannot be emptied. At the end of Furina's turn they act **front to
   back**. Combat opens with Usher on stage (Salon Solitaire).
2. **Two kinds of performer, two jobs.**
   - The **Salon trio** (Usher, Chevalmarin, Crabaletta) is the numbers
     engine: Block, damage to ALL, single-target damage. It is cheap and
     cloneable, and it cycles. This is the Defect-like half, and it is
     plain on purpose.
   - A **Guest Star** changes how Furina's turn plays. Each one has a
     "while on stage" line, a utility act, or both (sec.2). A guest is
     worth its seat even when nobody Cues it. One of each; a second copy
     Bows it and returns it.
3. **The Bow.** A performer that leaves acts once more, and that last act
   is **free**: a star does not pay. **Every Bow then gives 1 Fanfare, after
   its act**, including Grand Finale's Bows, which do not remove anyone.
4. **Overflow: Salon summons never evict guests.**
   - A summon onto a full stage Bows your front-most Salon member.
   - A Salon summon when every seat holds a guest is a **walk-on**: that
     member acts once and Bows at once, without taking a seat.
   - A guest summon when every seat holds a guest Bows the front guest.
5. **Fanfare is one number on Furina.** It has no cap and no fade, and
   hits never touch it.
   - **Filled by:** her Raise cards, Charlotte, reactions, and Bows.
   - **Drained by:** Spend N on her cards, and the stars' acts. A star that
     cannot pay skips the act and stays; nothing is spent.
   - **Read by flow, not stock.** A card that reads Fanfare without
     spending it counts what you **gained** or **spent this turn**, never
     what you hold. So holding is never paid for, and nothing needs a cap
     (sec.3).
   - Acting front to back makes **seat order matter**: Charlotte in front
     of Neuvillette funds him the same turn, and behind him she does not.
6. **Rehearsal** is the stage's scaling, from drafted cards and one relic.
   Every performer's damage and Block act deals 1 more per stack, guests
   included. Since guests are mostly not numbers, it is mostly the trio's
   stat. Energy, draw and Fanfare never scale (`LAW.md`: "empowerment
   boosts numbers only, never turn-economy effects"). It shows as a Power
   badge with its total.
7. **Cue.** "Cue a performer" makes it act now, as it would at the end of
   the turn; a star pays as usual. A short star skips the act, and the
   card's other effects still happen. **The player chooses the performer**
   if the game can target one; otherwise the prototype falls back to "your
   front performer". **Every Cue card carries a plain effect as well**, so
   directing never spends a whole card on nothing.
8. **Retired:**
   - performer bars, absorption and the front shield;
   - the shield and bank seats;
   - the fade;
   - Wriothesley's "always front";
   - the leaver's Fanfare passing to the newcomer;
   - every reader of Fanfare held.

## 2. The cast (opening values; the sim sets them)

**The trio:**
- **Usher:** 4 Block.
- **Chevalmarin:** 2 damage to ALL.
- **Crabaletta:** 5 damage to a random enemy.

**The guests.** Stars are Rare and pay for their acts; supports are
Uncommon and free.

| Guest | Kind | While on stage | Act |
|---|---|---|---|
| Neuvillette | Star | Your Hydro cards deal 3 more damage | pay 2: 7 Hydro to ALL |
| Clorinde | Star | Whenever you Spend, deal 4 Electro to a random enemy | pay 1: 8 Electro to a random enemy |
| Lyney | Star | The first Cue card you play each turn costs 0 | pay 1: add a Trick to your hand |
| Escoffier | Star | The first Salon summon card you play each turn costs 0 | pay 2: your Salon members act |
| Navia | Star | (none) | free: Geo to a random enemy, twice the Fanfare you spent this turn |
| Charlotte | Support | At the start of your turn, draw 1 more card | gain 1 Fanfare |
| Lynette | Support | The first time each turn you Cue a performer, it moves to the front | 3 Anemo to an enemy with an aura if any |
| Chevreuse | Support | (none) | the first time each turn: pay 2, next turn gain 1 Energy |
| Sigewinne | Support | (none) | 3 Block, plus 2 for each time you lost HP since her last act |
| Wriothesley | Support | (none) | 4 Cryo to a random enemy, plus 1 per damage your Block stopped since his last act |

- **Trick** is a token card: 0 Energy, "Deal 4 Pyro damage. Retain. Exhaust."
- **What each guest does to the turn:**
  - Neuvillette makes Hydro cards the plan.
  - Clorinde turns every Spend into a hit, so spending small and often
    pays.
  - Lyney makes directing cheap.
  - Escoffier makes the trio churn, and every Bow gives Fanfare.
  - Navia is the spender's payoff.
  - Charlotte is a draw engine with a seat cost.
  - Lynette is the stage's rearranger, the job GPT wanted kept.
  - Chevreuse is Energy.
  - Sigewinne and Wriothesley are defence.
- **Guest cards give Fanfare on arrival.** "Neuvillette joins with 6"
  becomes "Summon Neuvillette. Gain 4 Fanfare."
- **Critics' Darling** ([USER]'s "whenever Fanfare changes") stays distinct
  from Clorinde: hers fires per Spend for a flat 4, and it scales by count,
  not size.

## 3. The pool: what moves

The pool stays 78. About 30 rows change:

- **In: Gentilhomme Usher** (Common, 1): "Summon Usher. Gain 4 Block."
  **Out: Leading Lady**, which on one pool is Ousia Surge.
- **Directing (Cue Commons, from the seat-arranging rows; each carries a
  plain effect):**
  - Plot Twist becomes **Encore!** (Attack, 1): "Deal 7 damage. Cue a
    performer."
  - Stage Whisper becomes **Stage Whisper** (Skill, 1): "Cue a performer.
    Draw 2 cards."
  - A third (Skill, 1): "Gain 5 Block. Cue a performer."
  - Revolving Stage becomes an Uncommon Power: "At the start of your turn,
    Cue your front performer."
  - Step Forward goes, since Lynette and the chosen Cue do its job. Bis!,
    Tutti! and Oratrice's Verdict stay.
- **Raise.** "Your back performer gains N" becomes "Gain N Fanfare" on Warm
  Reception, Hold Your Places, Cheered On, Opening Number, Season Tickets,
  Groundswell and Singer of Many Waters.
- **Readers, by flow:**
  - **Ousia Surge:** "+N damage per Fanfare you gained this turn". It pays
    for building.
  - **Pneuma Refrain:** "+N Block per Fanfare you spent this turn". It pays
    for cashing out.
  - **Navia** reads Fanfare spent this turn.
  - **Bravura and Bring the House Down** spend what they read, and their
    per-point rates are reset down from the starved-bar values.
- **Bow cards need new designs:** Final Bow, Intermission and A
  Five-Century Act read a single performer's bar today. Grand Finale, Da
  Capo and Thunderous Applause carry over.
- **Rehearsal:** two Uncommon Powers and a Rare, replacing rows whose
  premise is gone (Counterclaim, Interposition, Guest of Honor's shield
  half), plus a relic.
- **Defence:** Usher at 4, Sigewinne, Gentilhomme Usher, and Regal Bearing
  plus two Block rows raised once the sim reads damage.
- **Critics' Darling:** "Whenever your Fanfare changes, deal that much
  damage to a random enemy."
- **Co-op:** Share the Spotlight and The Crowd Roars are rewritten on the
  one number.

## 4. The starter pair

- **Curtain Rise** (Basic Attack, 1): "Deal 7 damage. Spend 3: deal 17
  instead." Unchanged.
- **Rising Applause** (Basic Skill, 1): "Gain 3 Fanfare." (upgraded: Gain
  4). Ruled (sec.6, pick 1); the Cue Commons teach directing.

## 5. How it gets proven

1. **The sim slice:** the rules, the starter pair, the trio, Gentilhomme
   Usher, Take the Stage, the three Cue Commons, Neuvillette, Clorinde,
   Escoffier, Charlotte, Navia, Sigewinne, Bravura, Ousia Surge, Pneuma
   Refrain, and an Uncommon Rehearsal Power. Its questions:
   - one Salon seat against three guests;
   - **does a guest earn its seat uncued?** Compare Clorinde or Charlotte
     on stage with a third Salon member;
   - **does a Cue card beat its plain twin?** Compare "Gain 5 Block. Cue a
     performer." with a 1-cost 8 Block;
   - a Spend-small Clorinde deck against a Bravura finale deck;
   - a draft that finds no Rehearsal;
   - Escoffier's churn: free summons, Bows and Fanfare. It is the likeliest
     loop.

   The bar is that banking, spending and directing all make real
   decisions.
2. **Then the C#**, including whether the game can target a performer,
   and the rest of the ~30 rows.
3. **A rule change,** so [USER] plays it and a two-seat round reads it.
   Draft 4 goes back to Fable and GPT first.

## 6. Ruled picks

[USER], 2026-10-04: "Agreed on all 3 of those default picks."

1. **Rising Applause is "Gain 3 Fanfare."** (upgraded: Gain 4). The Cue
   Commons teach directing.
2. **The scaling stat is named Rehearsal**, shown as a Power badge with
   its total.
3. **The walk-on** (rule 4): a Salon summon onto a stage of three guests
   acts once and Bows, never evicting a guest.

## 7. What each draft took

- **Draft 2** (Fable, GPT): currency only; guests keep their seat; star
  upkeep; directing.
- **Draft 3** (Fable, GPT):
  - Usher's card and a second Block act;
  - free Bows defined;
  - overflow fixed;
  - front-to-back acts;
  - a chosen Cue;
  - Chevreuse once a turn;
  - three or four Rehearsal sources;
  - Leading Lady cut.
- **Draft 4** ([USER]):
  - the caps are gone, and readers count flow;
  - guests bend rules, with "while on stage" lines and utility acts;
  - every Cue card has a plain effect;
  - Step Forward goes in favour of Lynette.

## 8. Amended after the third reviews (2026-10-04)

Fable and GPT both said draft 4 was ready for the sim slice, after a set of
rule definitions and one hand-closed loop. These are card and rule details
inside the ruled direction, so they are decided here; where the two
reviews differ, the choice and its reason are given.

**Rule definitions:**
- **"Spent this turn" counts only a card's Spend.** A star's payment is
  not a Spend: it does not feed Pneuma Refrain or Navia, and it does not
  trigger Clorinde. Otherwise Navia behind Neuvillette is free damage, and
  seat order becomes a puzzle (Fable).
- **The flow counts** (gained this turn, spent this turn) reset at the start
  of Furina's turn, so they hold through the whole end-of-turn sequence
  (GPT). Both counts show on the Fanfare badge (Fable).
- **The walk-on is one act:** the member Bows at once without taking a
  seat. That is its free Bow act plus 1 Fanfare, not an act and then a Bow
  (GPT).
- **Chevreuse's once a turn covers every act she makes,** her free Bow
  included (GPT).
- **The chosen Cue is part of the design, not an option** (GPT). If
  clicking a performer is awkward, the C# uses a small selection panel. The
  front-performer fallback is withdrawn.

**Cards:**
- **Escoffier:** "The first Salon summon card you play each turn costs 0."
  The free-summon, Bow and draw loop needs no pilot to find. Fable's
  once-a-turn closes it in one line; GPT preferred pricing, but a loop is
  not a price question.
- **Take the Stage:** "Summon a random Salon member. Draw 1 card." (1
  Energy; 0 upgraded). No Fanfare, so the upgrade is not a free Rising
  Applause.
- **Gala Premiere:** "Summon Usher, Chevalmarin and Crabaletta." (1, Exhaust;
  0 upgraded). On a full stage its Bows pay the Fanfare.
- **Thunderous Applause:** "Whenever a performer Bows, draw 1 card." (Innate
  upgraded). The Fanfare half is now the base Bow rule.
- **Lyney's Trick has Retain:** "Deal 4 Pyro damage. Retain. Exhaust." His
  end-of-turn act makes it after the hand is played, so without Retain it
  would be discarded unused (GPT).
- **Lynette no longer moves anyone at the end of the turn**, which undid
  arrangements (the 2026-09-26 Lyney complaint, GPT). New line: "The first
  time each turn you Cue a performer, it moves to the front." Her act is 3
  Anemo to an enemy with an aura. The player drives the rearranging.
- **Step Forward returns** as the plain rearranger (GPT): "Move a
  performer to the front. Gain 3 Block." (0 Energy).
- **Stage Whisper** draws 1 (2 upgraded): "Cue a performer. Draw 1 card."
  At 2 it was above rate (Fable).
- **Bring the House Down** stops being the second spend-all finale. Let
  the People Rejoice keeps that job: "Spend all your Fanfare. Deal 2 damage
  to ALL enemies per point. Your performers Bow and return." New Bring the
  House Down (Rare, 2): "Deal damage to ALL enemies equal to 3 times the
  Fanfare you spent this turn." It is the flow finisher after a run of
  Spends.
- **Endless Waltz:** "Deal 18 damage. Each guest acts."
- **Grand Deluge:** "Deal 12 damage and apply Hydro to ALL enemies. On an
  Elemental Reaction, gain 4 Fanfare."
- **Arkhe Alignment's Pneuma mode:** "Gain 2 Fanfare." Ousia stays the
  damage mode.
- **Relics:**
  - Grand Theater Program ("Your performers no longer fade") becomes
    "Start each combat with 3 Fanfare."
  - The Curtain Never Falls, her Ancient, becomes "Combat opens with Usher
    on stage. Start each combat with 1 Rehearsal." This is the relic
    source of Rehearsal.

**Watched in the slice, not changed:**
- Charlotte's draw on a guest who cannot be knocked out (Fable, GPT).
- Whether three guests is simply the best stage (both reviews).

## 9. The sim slice, exact rows

The slice is built in the tier0 sim as a separate arm. Today's Furina keeps
working in both engines until the C# build. The rules are sec.1 as amended
in sec.8. Opening values:

**Starter:** Strike x4, Defend x4, Curtain Rise, Rising Applause.
- **Curtain Rise:** "Deal 7 damage. Spend 3: deal 17 instead." Upgraded as
  today.
- **Rising Applause:** "Gain 3 Fanfare." (4 upgraded).
- **Relic:** Salon Solitaire, which opens combat with Usher.

**The trio:** Usher, 4 Block; Chevalmarin, 2 to ALL; Crabaletta, 5 to a
random enemy.

**Common:**
- **Take the Stage** (1; 0 upgraded): "Summon a random Salon member. Draw
  1 card."
- **Gentilhomme Usher** (1): "Summon Usher. Gain 4 Block." (6 upgraded).
- **Surintendante Chevalmarin** (1): "Apply Hydro to ALL enemies. Summon
  Chevalmarin."
- **Mademoiselle Crabaletta** (1): "Summon Crabaletta. Deal 4 damage." (6
  upgraded).
- **Encore!** (1, Attack): "Deal 7 damage. Cue a performer." (10 upgraded).
- **Places, Everyone!** (1): "Gain 5 Block. Cue a performer." (8 upgraded).
- **Stage Whisper** (1): "Cue a performer. Draw 1 card." (draw 2 upgraded).
- **Step Forward** (0): "Move a performer to the front. Gain 3 Block." (5
  upgraded).

**Uncommon:**
- **Ousia Surge** (1, Attack): "Deal 4 damage, plus 2 per Fanfare you gained
  this turn." (3 per Fanfare upgraded).
- **Pneuma Refrain** (1): "Gain 4 Block, plus 2 per Fanfare you spent this
  turn." (3 per Fanfare upgraded).
- **Bravura** (1, Attack): "Spend all your Fanfare. Deal 4 damage, plus 2
  per point." (3 per point upgraded).
- **Thunderous Applause** (1, Power): "Whenever a performer Bows, draw 1
  card." (Innate upgraded).
- **Dress Rehearsal** (1, Power): "Gain 1 Rehearsal." (2 upgraded).
- **Guest Star: Charlotte** (1): summon. Her line and act are in sec.2.
- **Guest Star: Sigewinne** (1): summon. Her act is in sec.2.

**Rare:**
- **Guest Star: Neuvillette** (2): "Summon Neuvillette. Gain 4 Fanfare."
- **Guest Star: Clorinde** (1): "... Gain 2 Fanfare."
- **Guest Star: Escoffier** (2): "... Gain 3 Fanfare."
- **Guest Star: Navia** (1): "... Gain 2 Fanfare."

**Probe decks.** These are the slice's questions:
1. Mixed cast (Usher, Chevalmarin and one guest) against three guests
   with walk-ons.
2. Clorinde Spend-small against a Bravura finale.
3. Charlotte against a third Salon member in the same seat.
4. "Places, Everyone!" against a plain 1-cost 8 Block.
5. A draft with no Dress Rehearsal.
6. Escoffier with Take the Stage and Thunderous Applause. Count the cards
   played per turn and flag any turn over 12.

**What to report:** act-1 wins, plus per fight:
- Fanfare gained, spent and paid;
- star acts skipped for want of Fanfare;
- Cues played, and on whom;
- walk-ons;
- turns over 12 cards.
