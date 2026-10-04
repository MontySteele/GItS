Status: FOR REVIEW. [USER], Fable and GPT, before [USER]'s playtest of build 0.2.4376.

# Furina v2, the re-founded Stage: review packet

**What this is.** Furina's Stage kit was rebuilt from the ground up
between 2026-10-03 and 2026-10-04. It went from a ruled paper, to two sim
passes, to a full build in the mod, to a blind two-seat round. This packet
covers what was built, why, and what the evidence says, and ends in
questions for the reviewers.
- **Every claim names its source.** The ruled paper is
  `review/active/furina-refounding-2026-10-03.md` (sec.10 is the full sheet).
  The seat record is `review/records/furina-v2-round-2026-10-04.md`. The
  built rows are in `docs/prototype-surface.yaml`.
- **The old build is kept** at git tag `furina-stage-frozen-2026-10-04`.

## 1. Why it was rebuilt

[USER], after the co-op run: "Furina 'technically works' in the sense
that no individual component is broken, but they do not play well with one
another." Two problems:
- **Four mechanics were juggled at once:** performer bars, Fanfare stored
  on each performer, a fade, and seat shields.
- **Nothing made the stage scale.**

The re-founding keeps the stage and the guests and drops the rest.
[USER]'s rulings shaped it:
- "I'm opposed to arbitrary caps."
- "Guest Stars can't just be 'damage and element'."
- 1a, the directing family, with "the rest of your defaults".

## 2. The rules as built

1. **Three seats. Performers have no bars**, take no hits and cannot be
   knocked out. Combat opens with Usher on stage (Salon Solitaire). At the
   end of Furina's turn every performer acts, **front to back**.
2. **Two kinds of performer:**
   - The **Salon trio** carries the numbers: Usher 4 Block, Chevalmarin 2
     damage to ALL, Crabaletta 5 damage to a random enemy.
   - **Guest Stars** bend the rules, with a "while on stage" line, a
     utility act, or both. One copy of each guest; a second copy makes it
     Bow and stay.
3. **The Bow.** A performer that leaves acts once more for free, and then
   Furina gains 1 Fanfare.
4. **Overflow:**
   - A Salon summon onto a full stage Bows the front-most Salon member.
     Salon summons never evict guests.
   - A Salon summon onto three guests is a **walk-on**: it acts once and
     Bows, and takes no seat.
   - A guest onto three guests Bows the front guest.
   - Since #895, the summon card in hand names who will Bow.
5. **Fanfare is one number on Furina.** It has no cap and does not fade.
   - **Raised by:** her cards, Bows, reactions and some guests.
   - **Spent by:** a card's "Spend N" mode.
   - **Paid by:** a star's act. A star that can't pay skips its act and
     stays on stage.
6. **Readers count flow, never stock.** A card that reads Fanfare without
   spending it counts what was gained or spent *this turn*. Only a card's
   Spend counts as spent; a star's payment does not.
7. **Rehearsal** is the stage's scaling stat, a Power with stacks. Each
   stack adds +1 to every performer's damage or Block act. It never adds
   to Energy, draw or Fanfare.
8. **Cue a performer** makes it act now; a star pays as usual. The player
   picks the performer on a small panel, one face per seat. Every Cue card
   also has a plain effect.

## 3. The cast

| Guest | Kind | While on stage | Act |
|---|---|---|---|
| Neuvillette | Star (Rare, 2) | Your Hydro damage deals 2 more | pay 2: 7 Hydro to ALL |
| Clorinde | Star (Rare, 1) | Whenever you Spend, deal 4 Electro to a random enemy | pay 1: 6 Electro to a random enemy |
| Lyney | Star (Rare, 1) | The first Cue card you play each turn costs 0 | pay 1: add a Trick to your hand (0: deal 4 Pyro, Retain, Exhaust) |
| Escoffier | Star (Rare, 2) | The first Salon summon card you play each turn costs 0 | pay 2: your Salon members act |
| Navia | Star (Rare, 1) | none | free: Geo damage equal to twice the Fanfare you spent this turn |
| Charlotte | Support (Unc., 1) | At the start of your turn, draw 1 more card | gain 1 Fanfare |
| Lynette | Support (Unc., 1) | The first time each turn you Cue a performer, it moves to the front | 3 Anemo to an enemy with an aura |
| Chevreuse | Support (Unc., 1) | none | once a turn: pay 2, gain 1 Energy next turn |
| Sigewinne | Support (Unc., 1) | none | 3 Block, plus 2 per time you lost HP since her last act |
| Wriothesley | Support (Unc., 1) | none | 4 Cryo to a random enemy, plus 1 per damage your Block stopped since his last act |

Star cards also give Fanfare on arrival: Neuvillette 4, Escoffier 3, and
Clorinde, Lyney and Navia 2 each.

## 4. The starter and the pool

**Starter:** Strike x4, Defend x4, and:
- Curtain Rise: "Deal 7 damage. Spend 3: deal 17 instead."
- Rising Applause: "Gain 3 Fanfare."

**The pool, by family.** The full card texts are in the appendix.
- **Summons:**
  - Take the Stage;
  - Gentilhomme Usher;
  - Surintendante Chevalmarin;
  - Mademoiselle Crabaletta;
  - Gala Premiere, which summons all three;
  - the ten Guest Star cards.
- **Directing:**
  - Cue cards: Encore!, Places, Everyone!, Stage Whisper, Bis!, Guest of
    Honor;
  - acting outside a Cue: Revolving Stage, Tutti!, Endless Waltz;
  - moving performers: Step Forward.
- **Bows:**
  - Final Bow and Intermission (a performer Bows and leaves);
  - Grand Finale (everyone Bows and stays);
  - Thunderous Applause, Da Capo, A Five-Century Act.
- **Fanfare in:** Warm Reception, Hold Your Places, Cheered On, Opening
  Number, Groundswell, Season Tickets, Tide of Applause, Singer of Many
  Waters, Grand Deluge.
- **Fanfare out:**
  - Spend modes: Curtain Rise, Quick Flourish, Tidal Flourish, Spirited
    Aria, Grand Entrance, Interval Bell;
  - spend-all: Bravura and Let the People Rejoice;
  - flow readers: Ousia Surge, Pneuma Refrain, Bring the House Down,
    Critics' Darling.
- **Rehearsal:**
  - Dress Rehearsal (Uncommon Power, +1);
  - Premiere Season (Rare Power, +1 each turn);
  - The Curtain Never Falls (Ancient relic, +1);
  - Curtain Water (potion, +1).
- **Solo family (kept, watched):** Solo Verse, Between Acts, Aria for One,
  Soliloquy, One-Woman Show, The Last Act. Since performers can't be
  knocked out, a solo deck must pay a Bow card to clear Usher.

## 5. The evidence

**The sim** (`tier0/harness/furina_v2_probe.py`; 2000 runs per probe;
fixed decks on the act-1 route; read only the differences, since no
starter deck clears it, Ironclad's included):

| Question | Result |
|---|---|
| Does the stage scale? | Dress Rehearsal 84.0% against 57.9% on the same deck |
| Does a Cue card beat its plain twin? | Places, Everyone! 34.5% against a plain 8 Block's 27.9% |
| Does Escoffier loop? | No: no turn over 5 cards, no card cap reached |
| Do drafted decks work? | 10-card drafts win 79.6%; with ≥2 guests 81.5%, fewer 77.7% |
| Guests against the trio, equal card counts | three guests 98.9% against the mixed cast's 79.0% (see question 1) |
| Bravura finale | 0% with a greedy or a banking pilot; its rate was raised to 6 + 3 per point afterwards |

**The seats.** Build 0.2.4370, ascension 0, one blind Sonnet seat per act.
- **Lane 1** cleared acts 1 and 2. It lost to the final boss, one Block
  short, with the boss on 123 HP.
- **Lane 2** cleared acts 1 and 2. It lost to an act-3 elite after an
  Artifact cancelled a planned Freeze.
- Nothing crashed, and no rule misbehaved.
- **The best turns were guest turns:**
  - Navia hit three times in one turn after a Spend and Tutti!, taking an
    elite from 258 to 147.
  - Wriothesley hit for 32 off stored Block with Full House, taking a boss
    from 94 to 3.

## 6. Known weaknesses

1. **Directing was not felt early.** Both seats passed every Cue card and
   support guest in act 1. One said "nothing told me why seat order
   mattered." Seat order matters only through Charlotte in front of a star
   and Lynette's move.
2. **Fanfare sat idle at 5 or 6** in early decks with one Spend outlet
   (Curtain Rise). Rising Applause and Season Tickets were called filler.
3. **Guest pairs overpower the trio** in built decks (question 1).
4. **The stage sometimes plays the turn for you.** Lane 1: "most fights
   had one or two dead turns where the end-of-turn stage acts did the
   work."
5. **Weak cards so far:**
   - Tide of Applause ("too few reactions to earn a power slot");
   - Arkhe Alignment (2 Energy, never played);
   - Charlotte ("the draw bonus never mattered").
6. **Untested by anyone:** Ousia Surge, Pneuma Refrain, Escoffier,
   Neuvillette, Lyney, Sigewinne, Premiere Season, Sold Out, Star Turn, and
   the solo family.

**Readings the builder made** where the paper was silent (25 in all; these
are the ones a player will meet):
- Critics' Darling fires on every Fanfare change, including a star's
  payment.
- Lynette moves the first performer Cued each turn to the front before it
  acts.
- Navia's act adds Rehearsal.
- Rehearsal applies to a Bow's free act.
- Final Bow keeps Exhaust; its upgrade is +3 Block.

## 7. Questions for the reviewers

1. **Trio against guests.** The paper says the trio carries the numbers.
   The sim says a guest pair funded by Charlotte beats it by about 20
   points in a built deck, but drafted decks show no gap (81.5 against
   77.7). Is this a structural flaw, or a tuning item for after play?
2. **Directing early.** Should a Cue card or a seat-order reason reach
   the player in act 1 (for example a Cue card in the starter, or a common
   whose payoff depends on the front seat), or is a mid-run discovery
   fine?
3. **Fanfare outlets.** Is one Spend card in the starter enough? Or should
   an early common Spend appear more often, or Rising Applause carry a
   small Spend of its own?
4. **The solo family.** Do these cards still earn their slots, now that
   the stage only empties through a Bow card?
5. **Anything that reads as a loop or a degenerate line** that the sim
   could not find, given that its decks were energy-bound at 3 to 5 cards
   a turn.

**For [USER]:** if neither review finds an obvious issue, the next step is
your playtest on the installed build, 0.2.4376.

## Appendix: the built card texts

Format: cost, card text, then the upgrade in brackets.

**Basic:**
- Curtain Rise (1, Attack): Deal 7 damage. Spend 3: deal 17 instead. [10 /
  Spend 3: 21]
- Rising Applause (1, Skill): Gain 3 Fanfare. [4]

**Common:**
- Take the Stage (1): Summon a random Salon member. Draw 1 card. [cost 0]
- Gentilhomme Usher (1): Summon Usher. Gain 4 Block. [6]
- Surintendante Chevalmarin (1): Apply Hydro to ALL enemies. Summon
  Chevalmarin. [cost 0]
- Mademoiselle Crabaletta (1): Summon Crabaletta. Deal 4 Hydro damage. [6]
- Encore! (1, Attack): Deal 7 damage. Cue a performer. [10]
- Places, Everyone! (1): Gain 5 Block. Cue a performer. [8]
- Stage Whisper (1): Cue a performer. Draw 1 card. [2]
- Step Forward (0): Move a performer to the front. Gain 3 Block. [5]
- Warm Reception (1): Gain 3 Fanfare. Draw 1 card. [2]
- Hold Your Places (1): Gain 5 Block. Gain 2 Fanfare. [7, 3]
- Cheered On (1, Attack): Deal 7 damage. Gain 2 Fanfare. [10]
- Opening Number (1, Attack): Deal 9 damage. If this is the first card you
  played this turn, gain 2 Fanfare. [12]
- Quick Flourish (0, Attack): Deal 3 damage. Spend 3: deal 11 and apply
  Hydro instead. [4 / 13]
- Tidal Flourish (1, Attack): Deal 5 damage to ALL enemies. Spend 3: deal
  13 and apply Hydro to ALL instead. [8 / 16]
- Spirited Aria (1, Attack): Deal 8 damage. Spend 3: deal 14 and draw 2
  cards instead. [11 / 17]
- Regal Bearing (1): Gain 5 Block. Apply 1 Weak. [6, 2]
- Ensemble Piece (1, Attack): Deal 5 damage for each performer on stage.
  [7]
- Improvised Number (1, Attack): Deal 8 damage. If no one is on stage,
  summon a random performer. [11]
- Between Acts (1): Gain 5 Block. If no one is on stage, draw 2 cards. [8]
- Solo Verse (1, Attack): Deal 6 damage. If no one is on stage, deal 12
  instead. [8 / 16]
- Bubble Aria (1, Attack): Deal 4 damage twice. Apply Hydro. [5]
- Stage Combat (0, Attack): Deal 3 damage. If an enemy intends to attack,
  gain 3 Block. [5]
- Commanding Gaze (1): Gain 2 Block. Apply 1 Weak to ALL enemies. [2 Weak]
- Undercurrent (1, Attack): Deal 3 damage 3 times. [5 times]

**Uncommon:**
- Ousia Surge (1, Attack): Deal 4 damage, plus 2 per Fanfare you gained
  this turn. [3 per]
- Pneuma Refrain (1): Gain 4 Block, plus 2 per Fanfare you spent this
  turn. [3 per]
- Bravura (1, Attack): Spend all your Fanfare. Deal 6 damage, plus 3 per
  point. [4 per]
- Bis! (1): Cue a performer twice. [cost 0]
- Tutti! (1): All your performers act now. [Retain]
- Final Bow (1): A performer Bows and leaves. Gain 8 Block. Exhaust. [11]
- Intermission (1): A performer Bows and leaves. Draw 2 cards. [3]
- Dress Rehearsal (1, Power): Gain 1 Rehearsal. [2]
- Revolving Stage (1, Power): At the start of your turn, Cue your front
  performer. [Innate]
- Thunderous Applause (1, Power): Whenever a performer Bows, draw 1 card.
  [Innate]
- Season Tickets (1, Power): At the start of your turn, gain 1 Fanfare. [2]
- Tide of Applause (1, Power): Whenever you trigger an Elemental Reaction,
  gain 2 Fanfare. [3]
- Star Billing (1, Power): Whenever a Guest Star joins the stage, draw 2
  cards.
- Full House (3, Power): If every seat is filled at the end of your turn,
  your performers act twice. [cost 2]
- Groundswell (1, Attack): Deal 9 damage. If the enemy has an aura, gain 3
  Fanfare. [12]
- Grand Entrance (2, Attack): Deal 12 damage. Spend 7: deal 40 instead.
  [16 / 45]
- Interval Bell (0): Draw 1 card. Spend 3: draw 1 card and gain 1 Energy
  instead. [Spend 2]
- Da Capo (1, Attack): Deal 5 damage, plus 2 for each Bow this combat. [8,
  3 per]
- Oratrice's Verdict (0): This turn, your performers' random hits target
  this enemy. Draw 1 card. [2]
- Dual Nature (1): Choose Ousia or Pneuma for this turn. Draw 1 card. [2]
- Casting Agent (1): Exhaust. Choose 1 of 3 random Guest Star cards and
  add it to your hand. It costs 0 this turn. [and is upgraded]
- Crashing Waves (1, Attack): Deal 8 damage to ALL enemies; enemies with
  an aura take 5 more. [10]
- Aria for One (1, Attack): Deal 5 damage twice. If no one is on stage,
  deal it three times. [7]
- Soliloquy (1, Power): While no one is on stage, your Attacks deal 3 more
  damage.
- Courtroom Drama, Quick Change, Duet, The Witness Stand: shared rows,
  unchanged.
- The five support Guest Star cards (1): "Summon X." [cost 0]

**Rare:**
- Neuvillette (2): Summon Neuvillette. Gain 4 Fanfare. [cost 1]
- Escoffier (2): Summon Escoffier. Gain 3 Fanfare. [cost 1]
- Clorinde, Lyney and Navia (1): Summon X. Gain 2 Fanfare. [4]
- Let the People Rejoice (2, Attack): Spend all your Fanfare. Deal 2
  damage to ALL enemies per point. Your performers Bow and return. [cost 1]
- Bring the House Down (2, Attack): Deal damage to ALL enemies equal to 3
  times the Fanfare you spent this turn. [4 times]
- Critics' Darling (1, Power): Whenever your Fanfare changes, deal that
  much damage to a random enemy. [Innate]
- Premiere Season (3, Power): At the start of your turn, gain 1 Rehearsal.
  [cost 2]
- A Five-Century Act (3, Power): The first time each turn a performer Bows
  and leaves, it returns at the back if a seat is free. [cost 2]
- Grand Finale (1): All your performers Bow without leaving. [cost 0]
- Gala Premiere (1): Summon Usher, Chevalmarin and Crabaletta. Exhaust.
  [cost 0]
- Endless Waltz (2, Attack): Deal 18 damage. Each guest acts. [22]
- Grand Deluge (2, Attack): Deal 12 damage to ALL enemies and apply Hydro
  to them. On an Elemental Reaction, gain 4 Fanfare. [16]
- Singer of Many Waters (1): Gain 6 Fanfare. [9]
- Arkhe Alignment (2, Power): At the start of your turn, choose Ousia
  (damage) or Pneuma (gain 2 Fanfare). [cost 1]
- Regina of All Waters (1, Power): At the start of your turn, apply Hydro
  to ALL enemies. [Innate]
- Sold Out (2, Power): Your stage has a fourth seat. [cost 1]
- Star Turn (2, Power): Whenever a Guest Star joins the stage, it acts at
  once. [cost 1]
- One-Woman Show (3, Power): At the start of your turn, if no one is on
  stage, gain 1 Energy and draw 2 cards. [cost 2]
- The Last Act (3, Attack): Costs 1 less for each empty seat. Deal 24
  damage. [30]

**Co-op:**
- Guest of Honor (1): Another player gains 7 Block. Cue a performer. [10]
- Share the Spotlight (1): Spend all your Fanfare. Another player gains 2
  Block per point. [3 per]
- Raise a Toast (1): Draw 1 card. Spend 4: another player gains 4
  temporary Strength. [6]
- The People of Fontaine (1, Power): Whenever another player plays an
  Attack, gain 1 Fanfare.
- The Crowd Roars (1, Power): Whenever another player loses HP, gain 1
  Fanfare.

**Relics:**
- Salon Solitaire (starter): combat opens with Usher on stage.
- Opera Glasses: start each combat with 3 Fanfare.
- Grand Theater Program: at the start of your turn, gain 1 Fanfare.
- Guest Book: the first time you summon a Guest Star each combat, gain 3
  Fanfare.
- The Curtain Never Falls (Ancient): Usher on stage, and 1 Rehearsal.
- Stagehand's Gloves: whenever a performer Bows, gain 3 Block.
- Curtain Call Bouquet: a performer that Bows acts twice as it leaves.
- Palais Ledger: your Spends cost 1 less Fanfare.
- Opening Night: start of combat, summon a random performer behind Usher.

**Potions:**
- Bottled Applause: gain 6 Fanfare.
- Curtain Water: gain 1 Rehearsal.
- Encore Elixir: each of your performers acts twice.
