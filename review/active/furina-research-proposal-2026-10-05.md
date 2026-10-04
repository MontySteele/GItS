Status: RULED 2026-10-05: the defaults (picks 1 to 6), with sec.16's two changes. The overnight v2 build is discarded. The reference is the frozen tag `furina-stage-frozen-2026-10-04`. See the ruling note at the picks.

# Furina: the Salon's Tab (a research proposal)

**Where it comes from.** [USER] played the re-founded Stage on 2026-10-05:
"Honestly, not very engaging." The design-layer paper
(`review/active/furina-design-layer-2026-10-05.md`) reached a verdict:
"square pegs". The Stage is three base-game engines bolted together (orbs,
a pet and Stars), and each has lost its tension. [USER] then asked for this
pass: "move all of these pieces around until they have a build they think is
worth trying." This paper is one build, not a menu.

**The short version.**
- Furina lends her own HP to the Salon to hit harder.
- The Singer pays it back.
- Every swing of her HP, down or up, makes the crowd cheer.
- She cashes the cheering in for the show-stoppers.
- The stage stays, but only guests use it.

A sim slice of this build exists (sec.10). On act one it beats today's
Furina starter. Its biggest open risk is one the sim cannot see.

## 1. The promise and the ordinary turn

**Promise.** Furina is the actress who spends herself on the show. Her Salon
takes HP for bigger numbers, the Singer gives it back, and the audience
cheers every swing. She is strong while she gambles with her HP above the
line, and she wins by turning the fight's ups and downs into a finale.

**The core decision of an ordinary turn has two parts:**
- **How much of my HP do I lend the Salon this turn?** The HP is spent now
  and repaid slowly, and it is lost for good if the fight ends first.
- **Do I cash the Fanfare now or let it build for a finale?**

Behind both sits the usual StS question, Block or hit. Here it carries extra
weight, because a hit eats the HP she would otherwise lend.

## 2. The rules

1. **Drain N.** This is a choice on some of her cards: lose N HP for the
   bigger effect ("Deal 7. Drain 3: deal 14 instead."). It cannot take her
   below half the HP she started this combat with. HP lost to a Drain is
   *drained*.
2. **Restore N.** She gets back up to N of her drained HP. It never returns
   more than she drained, and never HP an enemy took. Drained HP still
   missing when the fight ends is gone.
3. **Fanfare** is one number on Furina, with no cap and no fade. She gains 1
   for every HP she loses or Restores, whatever the cause: a Drain, an
   enemy, or the Singer. It is paid by Spend N on cards and by the
   spend-all finales.
4. **Salon Solitaire**, her starting relic: "At the end of your turn,
   Restore 2." (Upgraded: 3.) This is the Singer.
5. **Guest Stars** are kept from v2, without the trio:
   - Up to three guests stand on stage.
   - Each has a line that bends a rule, and most act at the end of her turn.
   - A fourth guest makes the oldest one leave. It acts once more as it
     goes.

Those five rules are the whole kit. Gone from v2:
- the Salon trio as performers;
- Usher opening every fight;
- Rehearsal;
- the Cue family;
- seat order;
- the Bow's Fanfare;
- the solo family.

The two new mechanics are rules 1 and 2 (the HP loan) and rule 3 (Fanfare
from HP). The relic is one Restore, and the guests are machinery we already
built.

## 3. The two mechanics

### 3.1 The HP loan (Drain and Restore)

**What it is.** HP above the line is a budget. Drains spend it for bigger
cards. Restores and the Singer refill it, but only up to what was drained.
Enemy damage takes from the same pool and never comes back.

**The tension: what she gives up.**
- **Real HP when the fight ends early.** The Singer repays 2 a turn, so
  Draining on turn 1 is nearly free. Draining on the killing turn is a
  permanent cost.
- **Buffer against the next hit.** HP lent out cannot absorb a big intent.
- **Room for the big Drain.** At 43 of 78, after starting at full, the
  line is 39. Solicitation's Drain 2 still works and Crabaletta's Drain 5
  does not, unless a Restore comes first.
- **Block now against Drain room later.** Unblocked damage shrinks the room
  for good.

**How it shows on screen.**
- The HP bar gets a tick at the line (half her HP at the start of the
  fight).
- Drained HP shows as a pale, hatched segment above her current HP: the
  part that can come back.
- A Drain card in hand greys its Drain mode when the line would be crossed.
- The two-mode chooser is the one Spend uses today.

**Which base engine it is not.**
- **Not Ironclad's Bleed.** His HP payments are permanent, and Burning Blood
  heals after a won fight, so he bleeds late. Her Drain is a loan inside the
  fight: the Singer repays it over turns, so she drains early. Repaying it
  is itself fuel (rule 3).
- **Not the Watcher's stances.** The round trip ("dip, hit, come back")
  rhymes with Calm, Wrath, Calm. But it runs on her HP across turns and
  multiplies nothing. The Watcher is not in StS2 either.

### 3.2 Fanfare from HP

**What it is.** This is Genshin's rule with no translation: every point of
HP change makes a point of applause. It also restores the line the original
identity record carried: "every point of damage past Block prints exactly 1
Fanfare" (`docs/current/characters/furina-identity-record.md`).

**The tension: what she gives up.**
- The spend-or-bank choice is kept from v2, where both seats called it the
  kit's steady decision (`review/records/furina-v2-round-2026-10-04.md`).
- Small Spend modes pay about 2 per point now. Let the People Rejoice pays
  2 per point to every enemy, later.
- Fanfare at the curtain is wasted, like Block.

**How it shows.** The Fanfare gauge beside the energy orb (#897) stays as it
is. Its hover adds where this turn's Fanfare came from.

**Which base engine it is not.**
- **Not the Regent's Stars.** Stars come from cards that do nothing else
  (Venerate) and from a relic. Fanfare comes as a side effect of HP moving,
  which every turn produces, so no card is a dead "gain N" turn. The v2
  seats called those cards filler.
- **Not Focus.** Fanfare boosts nothing passively. It is only spent.

## 4. Three archetypes

The guests are not a fourth archetype. Each archetype owns three guests, so
a guest is a payoff inside a plan rather than a plan of its own. The
design-layer paper counted seven thin archetypes in v2. This build has
three.

| | **Ousia: the Salon's Tab** | **Pneuma: the Singer** | **The Crowd: Let the People Rejoice** |
|---|---|---|---|
| Plan | Drain every turn for big frontload | Drain a little, Restore a lot; every repaid HP pays twice | Bank Fanfare from every swing, hits included, and cash it in a finale |
| Scales by | Drain readers (Salon's Encore, Ousia Surge), so every Drain is also AoE and draws more | Restore readers (Endless Waltz, Clorinde, Sigewinne), so each HP repaid becomes damage or Block | Fanfare multipliers (Universal Revelry) and spend-all AoE (Let the People Rejoice) |
| Key cards | Mademoiselle Crabaletta, Surintendante Chevalmarin, Gentilhomme Usher, Soloist's Solicitation, Salon's Tab, Grand Deluge, A Five-Century Act | Surging Waters, Hymn of Many Waters, Pneuma Refrain, Endless Waltz, Singer of Many Waters | Rising Applause, Standing Ovation, Tidal Flourish, Bravura, Spirited Aria, Universal Revelry, Critics' Darling |
| Guests | Wriothesley, Lyney, Neuvillette (they drain too) | Charlotte, Sigewinne, Clorinde (they heal) | Chevreuse, Lynette, Navia (they read Spends and hits) |
| Weakness | HP: about 6 unrepaid HP a fight in the slice | Slow; needs some Drain to have anything to Restore | Few outlets early means Fanfare idles; weak while the bank is small |

**The bridges:**
- every Pneuma deck needs a few Drains;
- every Ousia deck feeds the Crowd's bank;
- Hydro (Chevalmarin, Tidal Flourish, Grand Deluge) gives every plan the
  guests' reactions.

## 5. The act curve

StS2's challenge, as [USER] framed it: act 1 needs cards better than Strike
and Defend; act 3 needs rapid scaling; act 2 is the bridge.

**Act 1: frontload.** Drain modes are better than Strike from the first
fight:
- Curtain Rise deals 14 for 3 lent HP;
- Crabaletta deals 26 for 2 Energy and 5 HP;
- Solicitation deals 9 for 0 Energy and 2 HP.

Rising Applause turns the hits she has already taken into damage. In the
slice, the starter wins 4.29 act-one fights on average, against 3.72 for
today's v2 starter, and takes the first elite 67% of the time against 39%
(sec.10, K1).

**Act 2: AoE and ramp.**
- **AoE:**
  - Surintendante Chevalmarin (4 to ALL, or 8 with Drain 3);
  - Tidal Flourish (Spend 6: 12 to ALL);
  - Standing Ovation (spend all as damage to ALL; Common);
  - Salon's Encore (every Drain also deals 3 to ALL);
  - Grand Deluge.
- **Ramp:** the bank grows with the fight. Bigger hallways hit harder, so
  they print more Fanfare, so the AoE finale is bigger. The scaling tracks
  the danger without any card asking for it.

**Act 3: multiplication.** Damage here is (HP swung per turn) times (the
payoffs on each swing). Example: Universal Revelry doubles every gain,
Critics' Darling turns every gain into damage, and Endless Waltz turns every
Restore into damage. A turn that drains 8 and Restores 8 then makes:
- 32 Fanfare with Revelry;
- 32 damage from Critics' Darling;
- 8 more damage from Endless Waltz;
- and, the next turn, 64 to ALL from Let the People Rejoice.

Singer of Many Waters (Restore all drained) with Clorinde on stage turns 30
drained HP into 60 Electro. A Five-Century Act doubles the room by letting
her Drain to 1 HP.

The slice's evidence is partial. A finale deck matches v2's best built deck
on the act-2 boss (26% against 23%). Neither does much against the act-3
boss with an unupgraded 18-card deck (K6).

## 6. Fight one: Nibbit, turns 1 to 3

**The fight.**
- Nibbit has 44 HP (`tier05/content/act1_pool.yaml`: Butt 12, Hesitant
  Slice 6 with 5 Block, Hiss +2 Strength). Its order is the Stage brief's:
  Butt, Hiss, Slice.
- Furina has 78 of 78 HP, so the line is 39.
- **Starter:** Strike x4 (6), Defend x4 (5), Curtain Rise and Rising
  Applause (sec.7), and Salon Solitaire (Restore 2 at the end of her
  turn).

**Turn 1.** She has 3 Energy and 0 Fanfare. Her hand is Curtain Rise,
Rising Applause, Strike, Strike and Defend. Nibbit intends Butt 12.

| Line | Play | Nibbit after | Furina after the enemy turn | Fanfare |
|---|---|---|---|---|
| **A: lend and swing** | Curtain Rise with Drain 3 (78 to 75; 14 dmg), Strike 6, Rising Applause (5 Block, spends the 3 Fanfare for 3 dmg). Singer Restores 2 (to 77). Butt 12 against 5 Block: 7 through | 21 | 70, 1 HP still drained | 0 + 3 − 3 + 2 + 7 = **9** |
| **B: lend and guard** | Curtain Rise with Drain 3 (14), Defend 5, Rising Applause (5 Block, 3 dmg). Singer +2. Butt 12 against 10 Block: 2 through | 27 | 75, 1 still drained | **4** |
| **C: keep the HP** | Curtain Rise plain (7), Strike 6, Defend 5. Nothing to Restore. 7 through | 31 | 71 | **7** |

**The choice.**
- A against C: A does 10 more damage for 1 more HP, and 2 more Fanfare.
  The Singer has already repaid most of the loan.
- A against B: 6 damage now against 5 HP. That is the real wager.
- The rejected lines each lose something. C leaves Nibbit at 31, a fourth
  turn against a buffed Butt. B is the safe line and leaves Nibbit 6 higher
  at the Hiss turn.

**Turn 2: Hiss, no attack.** Her hand is Strike, Strike, Defend, Defend,
Defend.
- After line A: two Strikes put Nibbit at 9. The Singer repays the last
  drained HP (71, Fanfare 10).
- Nobody hits her this turn, so this is where the Singer catches up. An
  early Drain is the cheap Drain.

**Turn 3: Slice 8 with 5 Block.** Nibbit has 9 HP and Furina has 10
Fanfare. Her hand is Curtain Rise, Rising Applause, Strike, Defend, Defend.
There are three kills:
- **Curtain Rise with Drain 3 (14).** This costs 3 HP for good, because the
  fight ends before the Singer can repay it.
- **Curtain Rise plain plus Strike (13).** This costs 2 Energy.
- **Rising Applause.** It spends all 10 for 10 damage, with 5 Block that
  will not matter, and it costs 1 Energy. Fanfare left at the curtain is
  wasted anyway.

She plays Rising Applause. This turn teaches the kit's second lesson: lend
early, cash in before the curtain. She leaves at 71 of 78.

## 7. The starter, and a pool sketch

**[USER] pick (the starter).** The base Strike x4 and Defend x4 stay. Two
kit cards change.

| Card | Today (v2) | Proposed |
|---|---|---|
| Curtain Rise (Basic Attack, 1) | Deal 7. Spend 3: deal 17 instead. | **Deal 7. Drain 3: deal 14 instead.** [10 / Drain 3: 18] |
| Rising Applause (Basic Skill, 1) | Gain 3 Fanfare. | **Gain 5 Block. Spend all your Fanfare and deal that much damage.** [7 Block] |
| Salon Solitaire (starting relic) | Combat opens with Usher on stage. | **At the end of your turn, Restore 2.** [3] |

Both names are kept, as [USER] asked on 2026-09-28. Between them, the pair
and the relic teach all four verbs: Drain, Restore, Fanfare and Spend.

**The pool sketch, 36 key cards.** Format: name (type, cost, rarity): text
[upgrade]. Rows marked * are in the sim slice at these numbers.

*Common, Ousia*
- Mademoiselle Crabaletta* (Attack, 2): Deal 12 damage. Drain 5: deal 26
  instead. [16 / 32]
- Surintendante Chevalmarin* (Attack, 1): Deal 4 damage to ALL enemies and
  apply Hydro. Drain 3: deal 8 to ALL instead. [6 / 11]
- Gentilhomme Usher* (Skill, 1): Gain 7 Block. Drain 3: gain 14 instead.
  [9 / 18]
- Soloist's Solicitation* (Attack, 0): Deal 4 damage. Drain 2: deal 9
  instead. [6 / 12]

*Common, Pneuma*
- Surging Waters* (Attack, 1): Deal 6 damage. Restore 3. [9, Restore 4]
- Hymn of Many Waters* (Skill, 1): Gain 8 Block. Restore 3. [11, Restore 4]

*Common, the Crowd*
- Standing Ovation* (Attack, 1): Spend all your Fanfare. Deal that much
  damage to ALL enemies. [Retain]
- Tidal Flourish* (Attack, 1): Deal 5 damage to ALL enemies. Spend 6: deal
  12 to ALL and apply Hydro instead. [8 / 16]
- Spirited Aria* (Attack, 1): Deal 8 damage. Spend 5: deal 13 and draw 2
  instead. [11 / 17]
- Quick Flourish* (Attack, 0): Deal 3 damage. Spend 4: deal 11 and apply
  Hydro instead. [4 / 13]
- Interval Bell* (Skill, 0): Draw 1 card. Spend 4: also gain 1 Energy.
  [Spend 3]

*Common, guests (so a guest can arrive in act 1)*
- Guest Star: Charlotte* (Skill, 1): Line: the first time you Restore each
  turn, draw 1 card. Act: Restore 2. [cost 0]
- Guest Star: Chevreuse (Skill, 1): Line: your first Spend each turn costs 2
  less. Act: deal 3 Pyro damage to a random enemy. [cost 0]
- Casting Call (Skill, 1): Choose 1 of 3 random Common or Uncommon Guest
  Stars. It costs 0 this turn. Exhaust. [Choose 1 of 4]

*Uncommon*
- Ousia Surge* (Attack, 1): Deal 4 damage, plus 1 per Fanfare you gained
  this turn. [plus 2]
- Salon's Encore* (Power, 1): Whenever you Drain, deal 3 damage to ALL
  enemies. [4]
- Salon's Tab (Skill, 0): Draw 1 card. Drain 4: also gain 1 Energy. [Draw
  2]
- Pneuma Refrain* (Skill, 1): Restore 5. Gain 6 Block. [Restore 7, 8
  Block]
- Endless Waltz* (Power, 1): Whenever you Restore, deal that much damage to
  a random enemy. [Innate]
- Bravura* (Attack, 1): Spend all your Fanfare. Deal 6 damage, plus 2 per
  point. [3 per]
- Tutti! (Skill, 1): Each guest acts now. [Retain]
- Guest Star: Wriothesley* (Skill, 1): Line: whenever you Drain, deal that
  much Cryo damage to a random enemy. Act: deal 4 Cryo damage to a random
  enemy. [cost 0]
- Guest Star: Sigewinne* (Skill, 1): Line: whenever you Restore, gain that
  much Block. Act: Restore 3. [cost 0]
- Guest Star: Lynette (Skill, 1): Line: the first time each turn an enemy
  makes you lose HP, gain that much Fanfare again. Act: deal 3 Anemo damage
  to an enemy with an aura. [cost 0]

*Rare (each bends a rule and keeps the decision)*
- Let the People Rejoice* (Attack, 2): Spend all your Fanfare. Deal 2
  damage to ALL enemies per point. [cost 1]
- Universal Revelry* (Power, 2): Whenever you gain Fanfare, gain that much
  again. [cost 1]
- Critics' Darling* (Power, 1): Whenever you gain Fanfare, deal that much
  damage to a random enemy. [Innate]
- A Five-Century Act (Power, 2): You can Drain down to 1 HP. [cost 1]
- Singer of Many Waters (Skill, 1): Restore all your drained HP. Exhaust.
  [cost 0]
- Grand Deluge (Attack, 2): Deal 10 damage to ALL enemies and apply Hydro.
  Drain 6: deal 22 to ALL instead. [14 / 28]
- Guest Star: Neuvillette* (Skill, 2): Line: your Hydro damage deals 2
  more. Act: Drain 4 if you can, then deal 8 Hydro damage to ALL enemies (3
  if he could not). [cost 1]
- Guest Star: Clorinde* (Skill, 1): Line: whenever you Restore, deal twice
  that much Electro damage to a random enemy. Act: deal 6 Electro damage to
  a random enemy. [cost 0]
- Guest Star: Navia* (Skill, 1): Act: deal Geo damage to a random enemy
  equal to twice the Fanfare you spent this turn. [cost 0]
- Guest Star: Lyney (Skill, 1): Line: whenever you Drain, add a Trick to
  your hand (0: deal 4 Pyro damage, Exhaust). [cost 0]

**How the 78 divide, roughly:**

| Group | Cards |
|---|---|
| Ousia | 20 |
| Pneuma | 18 |
| The Crowd | 20 |
| Guests and stage | 12 (9 guests, Casting Call, Tutti!, one leave card such as Final Bow) |
| Plain and bridges | 8 (Regal Bearing, Commanding Gaze, Stage Combat, Undercurrent, Bubble Aria, Crashing Waves and two Hydro bridges) |

By rarity it is about 30 Common, 32 Uncommon and 16 Rare.

## 8. Reuse, cuts and cost

**Kept from the current pool and the C#:**
- the Spend chooser and every Spend-mode row (Tidal Flourish, Spirited Aria,
  Quick Flourish, Interval Bell, Grand Entrance);
- Bravura, Let the People Rejoice, Bring the House Down, and Ousia Surge
  with its flow reader;
- the Fanfare gauge (#897);
- the stage's seats, guest summons and the leave-and-act-once-more Bow;
- the summon card's "who will leave" preview (#895);
- nine guests, with new lines;
- Tutti!, Final Bow, Star Billing, Star Turn and Sold Out;
- Grand Deluge, Crashing Waves, Bubble Aria, Regina of All Waters, and the
  plain Commons.

**Kept and rewritten:**
- Critics' Darling, Endless Waltz, Singer of Many Waters and A Five-Century
  Act;
- the three Salon names, which become Drain cards;
- Casting Agent, which becomes Casting Call;
- the relics, as follows:
  - Opera Glasses stays;
  - Palais Ledger stays;
  - Guest Book stays;
  - The Curtain Never Falls (Ancient) becomes "Your Drain line is a quarter
    of your starting HP";
  - Opening Night becomes "Start each combat with a random Common Guest
    Star on stage".

**Cut:**
- the trio as performers and their summon cards (Take the Stage, Gala
  Premiere and the summon halves);
- Rehearsal (Dress Rehearsal, Premiere Season, Curtain Water);
- the Cue family (Encore!, Places, Everyone!, Stage Whisper, Bis!,
  Revolving Stage, Step Forward, Oratrice's Verdict);
- the pure gainers (Warm Reception, Hold Your Places, Cheered On, Opening
  Number, Season Tickets, Tide of Applause);
- the solo family;
- Full House, Ensemble Piece, Escoffier, Da Capo, Grand Finale and
  Thunderous Applause.

**Cost.**
- **Engine:** a drained-HP count, the Restore op, the line taken from entry
  HP, and Fanfare hooks on HP loss and gain. This is small.
- **The two-mode Drain chooser** reuses Spend's.
- **The HP-bar overlay** (the line tick and the drained segment) is the one
  piece of new UI, and the riskiest.
- **The stage** is mostly deletion: the trio, Rehearsal and the Cue panel.
- **About 45 rows** are written or rewritten.
- **The sim arm** already exists (sec.10).

Overall it is about the size of the v2 rebuild (paper to build in two days,
2026-10-03 to 10-04), with the HP-bar UI as the item most likely to run
long.

## 9. Law check

| Rule | This proposal |
|---|---|
| **Healing law** (`LAW.md`: true in-combat healing is Rare and Exhausts) | **Reopening proposed, narrowly.** Restore at Common needs a sentence: "Restore returns only HP your own cards drained this combat. It can never return HP an enemy took, so it is a refund, not healing." Over a fight her HP with Drains can never end above her HP without them, so it cannot be a stall payoff, which is what the law exists to stop. **If refused:** Salon Solitaire stays legal (relic trickles are exempt), and Pneuma shrinks to the relic plus Rare Restores |
| Pet clause | Not used |
| Starter basics never change | Strike x4 and Defend x4 kept. The two kit cards and the relic change, as a [USER] pick (sec.7) |
| "Must not be a Defect with Fanfare for Focus" (2026-09-07) | Kept. No slot scales, there is no Focus-like stat, and Rehearsal is cut. Guests have no evoke |
| "Opposed to arbitrary caps" | Kept. Fanfare is uncapped. The line is the Salon's own rule from Genshin ("drains only above half"), and A Five-Century Act bends it. Three guest seats are unchanged from today |
| "Guest Stars can't just be damage and element" | Kept. Every guest has a rule-bending line, and Navia's act reads Spends |
| Rares bend, never remove the decision | Kept. A Five-Century Act still costs HP; Revelry and Let the People Rejoice still ask when |
| Player text short, base templates | "Drain 3: deal 14 instead." mirrors "Spend 3: deal 17 instead." Restore is one verb |
| Empowerment boosts numbers only | Neuvillette's +2 is a number |
| Reactions are earned | Her own cards apply only Hydro; off-element comes only from guests (the guest clause) |
| ≤2 new keywords | Drain and Restore are added; Cue, Rehearsal and the trio's Summon are removed. A net cut |
| Kokomi owns "HP stability" | Kept apart. Kokomi never costs HP. Furina's Restore only undoes her own Drain and never protects against enemies |
| Infinite cycling gates to Uncommon+ | Lyney's Trick per Drain is bounded by Drain room. Salon's Tab is Uncommon |

## 10. Kill questions and the sim slice

**The slice.** It is built and runnable. It uses `tier0/engine/furina_tide.py`
with the pilot `tier0/pilot/furina_tide_pilot.py`, and runs as:

    .venv/Scripts/python.exe -m tier0.harness.furina_tide_probe --runs 1000 --jobs 0

It holds the starter and 26 pool rows, six of them guests. One row, The
Crowd Gasps, is a probe-only Power, which Lynette's line replaced on paper.
Two readings differ from this paper's text:
- the slice lets the pilot choose whether Rising Applause spends;
- Lynette, Lyney, Chevreuse, Casting Call, Salon's Tab, Tutti!, Grand
  Deluge, A Five-Century Act and Singer of Many Waters are not in it.

It uses `furina_v2_probe`'s act-one spine:
- fixed decks;
- no potions, relics or upgrades;
- HP carries between fights;
- a rest heals 30%.

No starter clears that spine, Ironclad's included, so read only the
differences.

**The pilots:**
- **judged:** values HP by how close she is to the line, and charges a
  Drain for the share the Singer cannot repay in time;
- **always:** Drains whenever it can;
- **never:** never Drains.

The **gauntlet** fights the act-2 boss and then the act-3 boss, each at full
HP. The references run the same seeds:
- `ref:v2` is today's v2 starter under its own pilot;
- `ref:ironclad` is the reference Ironclad starter under the generic pilot,
  so the cross-pilot comparison is loose.

These numbers are an instrument reading, not sheet numbers (`EXPERIMENTS.md`).

| # | Question, and what kills it | Result (1000 runs) | Read |
|---|---|---|---|
| K1 | **Frontload.** Killed if the starter does no better than v2's on act one | Fights won: 4.29 (v2 3.72, Ironclad 3.56). First elite won: 67% (v2 39%, Ironclad 32%) | **Pass.** Watch the overshoot: the lever is Rising Applause's Block or Curtain Rise's 14 |
| K2 | **Drain matters.** Killed if never-Drain loses under 0.3 fights a run | Draft deck 5.52 vs 4.57; balanced deck 5.97 vs 4.93; starter 4.29 vs 4.08 | **Pass** (the starter's margin is small) |
| K3 | **Drain is a decision, not a reflex.** Killed if seats report they never declined a Drain and never sequenced a Restore before one | The sim cannot answer it. The judged pilot takes 97 to 100% of legal Drains, and always-Drain plays the same | **Open: the biggest risk.** Seat question. Levers: Singer 2 to 1 (draft 5.52 to 5.43), higher Drain prices, or the line back to half of Max HP |
| K4 | **A hurt Furina still has her kit.** Killed if fights started below half Max HP are dead | Line at half of entry HP: those fights won 53%, Drain blocked 28%. Genshin's half-of-Max-HP line: 38% won, Drain blocked 100% by construction | **Pass with the entry line.** This is why rule 1 measures from entry HP |
| K5 | **Fanfare gets spent.** Killed if a deck with three outlets spends under 40% of what it gains | Balanced deck: 54% spent (47% of gains from hits, 31% Drain, 22% Restore). Random draft: 21% spent, about 23 left at the curtain | **Pass for a built deck, fail for the draft model.** The pool needs Spend outlets at Common (sec.7 has 7). Seats ask "did Fanfare sit idle?" |
| K6 | **Late scaling.** Killed if her best built deck falls well short of v2's best on the bosses | Finale deck: act-2 boss 26% (v2 three-guest deck 23%), act-3 boss 0% (v2 6%) | **Partial.** Act 2 matches; act 3 is unread with unupgraded 18-card decks. Seats in act 3 decide |

**Also measured:**
- **Guests may be the strongest plan.** The guest deck wins 6.12 fights
  against the balanced deck's 5.97, and reaches the boss 64% of the time.
  This is a watch item, as v2's guests were.
- **Hits matter late.** Without Fanfare from enemy hits (the `nohit`
  variants, run under the half-of-Max-HP line), the finale deck took 0% of
  act-2 bosses against 25% with hits. That is why rule 3 counts every HP
  change.
- **The loan's real cost** is 2.5 HP a fight unrepaid in a drafted deck,
  and 5.8 in a heavy Ousia deck.

**Next, if the direction is taken:**
1. a two-seat round on a `+proto` build, with K3, K5 and K6 as its
   questions;
2. [USER] plays one run, since this is a rule change.

## 11. The lore map

| Genshin fact | Here |
|---|---|
| Salon members drain the HP of party members above 50% to hit harder (Salon Solitaire, Ousia) | Drain, and the line at half |
| The Singer of Many Waters heals the party at intervals (Pneuma) | Salon Solitaire's Restore 2 a turn; the Pneuma archetype |
| Fanfare: 1 point per 1% of any party member's HP change, up or down, during Let the People Rejoice; it raises damage and healing | Rule 3, word for word in spirit; Let the People Rejoice as the spend-all finale |
| Universal Revelry, the Burst's buff; constellation 2 makes Fanfare gain 3.5 times faster | Universal Revelry doubles every gain |
| Passive "Endless Waltz": overhealing makes Furina heal the party | Endless Waltz: every Restore also hits |
| Constellation 6, "Center of Attention": attacks heal in Ousia and drain the team in Pneuma | The round trip as the kit itself |
| The 500-year performance: the human half of Focalors played a god until the trial | A Five-Century Act: she can give the Salon everything, to 1 HP |
| Neuvillette's charged attack drains his own HP above half | Neuvillette Drains 4 at the end of each turn for 8 Hydro to ALL |
| Wriothesley's Chilling Penalty spends his HP above half | Wriothesley: every Drain also hits in Cryo |
| Lyney's Prop Arrow spends HP above 60% to make a Grin-Malkin hat | Lyney: every Drain adds a Trick |
| Clorinde's kit runs on a Bond of Life that healing pays off | Clorinde: every Restore deals twice that in Electro |
| Sigewinne is the Fortress of Meropide's nurse; Charlotte and Chevreuse both heal | Sigewinne and Charlotte read and make Restores |
| Lynette is the assistant in the box, who takes the trick's risk | Lynette: the first hit each turn pays its Fanfare twice |
| Navia's shotgun fires the Crystal Shrapnel she gathers | Navia: an act sized by what was spent this turn |
| Fontaine's court is a theatre, and the audience's mood is the verdict | Fanfare as the crowd, and the finale as the verdict |

## 12. Alternatives rejected

- **Keep the Stage and tune it.** The design-layer paper's diagnosis is
  structural (sec.6 there), not numeric.
- **The Arkhe face-flip** (concept B, 2026-09-07). Every card would carry
  two texts, against [USER]'s short-text rule. It also has no scaling story
  for act 3.
- **The Flood** (Hydro stacks on enemies). It depends on companions, and
  Varka already owns element juggling.
- **The pure Tide**, with Genshin's half-of-Max-HP line and Restore only at
  Rare:
  - the slice shows a fight started below the line is locked out of Drain
    entirely (K4);
  - without Common Restore, the Singer half has no cards;
  - that is the "nothing to do while injured" failure GPT found in the 2026-09-07 sketch.
- **Guests as pets with HP bars, healed under the pet clause.** This
  brings back the bars [USER] removed in v2 to cut juggling.
- **Fanfare from Drain and Restore only, not from hits.** This makes
  Fanfare purely player-driven, but late scaling vanished in the slice
  (sec.10).
- **A spend-all starter at 2 per point.** It was swingier in the slice. It
  reached the boss 13% of the time against 2% at 1 per point, but took the
  first elite only 55% of the time against 67%.
- **A fixed "Spend 6: deal 12" starter.** It left 23 Fanfare idle a fight
  (K5).

## 13. Sources

**Repo:**
- the design-layer paper (PR #899);
- `review/ruled/furina-identity-concepts-2026-09-07.md`;
- the Tide sketch at `19ace889^`;
- `review/active/furina-stage-brief-2026-09-08.md`;
- `review/active/furina-refounding-2026-10-03.md`;
- `review/active/furina-v2-review-packet-2026-10-05.md`;
- `review/records/furina-v2-round-2026-10-04.md`;
- `docs/current/research/ironclad-brief-calibration-2026-09-01.md` (the
  Burning Blood lesson);
- `docs/current/research/regent-stars-economy.md` (Venerate, Divine Right);
- the Klee, Kokomi and Varka briefs.

**Base-game facts:** the local decompile extract `game_ref/*.json`, which is
gitignored. Necrobinder's starter is Bodyguard (Summon 5) and Unleash,
and her HP is 66. Web guides disagree: one says 68 HP, with "Bone Toss" and
"Raise Hand" (slaythespiretwo.com). I trust the decompile. Treat
web StS2 claims as uncertain.

**Web:**
- [KQM, Furina quick guide](https://keqingmains.com/q/furina-quickguide/):
  Salon drain above 50%, the Singer, Fanfare per 1% HP change (300 max),
  passives, constellations.
- [Icy Veins, Furina guide](https://www.icy-veins.com/genshin-impact/furina-guide-best-builds).
- [Wikipedia, Furina](https://en.wikipedia.org/wiki/Furina_(Genshin_Impact)):
  the 500 years, the prophecy, the trial, Focalors, life after.
- [PC Gamer, "Everything is bigger" in Slay the Spire 2](https://www.pcgamer.com/gaming-industry/events-conferences/everything-is-bigger-in-slay-the-spire-2-which-has-been-crowned-our-most-wanted-game/):
  the Regent as "a character with two resources", Osty growing with HP.
- [The Necrobinder guide, slaythespiretwo.com](https://slaythespiretwo.com/articles/the-necrobinder-complete-guide-osty-doom-and-souls-explained):
  Osty soaks hits; Doom's end-of-turn check (uncertain, see above).
- [Game Developer, Slay the Spire's metrics-driven balance (GDC 2019)](https://www.gamedeveloper.com/design/how-i-slay-the-spire-i-s-devs-use-data-to-balance-their-roguelike-deck-builder)
  and [Justin Gary's interview with Anthony Giovannetti](https://justingarydesign.substack.com/p/anthony-giovannetti-crafting-slay):
  "The core design of Slay the Spire is risk versus reward."
- [Game Developer, Sid Meier at GDC 2012](https://www.gamedeveloper.com/design/gdc-2012-sid-meier-on-how-to-see-games-as-sets-of-interesting-decisions):
  an interesting decision has tradeoffs and is situational, personal and
  persistent. A choice that is always the same is not one, which is K3.
- [Unsolicited Design, the Watcher](https://mfq-games.digital.conncoll.edu/news/unsolicited-design/unsolicited-design-sunday-universes-beyond-slay-the-spire-part-4-the-watcher/)
  and [PC Gamer on the Watcher](https://www.pcgamer.com/slay-the-spire-the-watcher-4th-character/):
  Wrath doubles damage dealt and taken; the stance dance is Calm, Wrath,
  Calm. This is the round trip sec.3.1 says this kit rhymes with but is
  not.

## 14. Main session review (2026-10-05)

**Verdict: worth a build.** This is the first Furina direction whose
mechanics are her Genshin kit rather than base-game engines renamed. It
restores what the design-layer paper named as the dropped core: HP volatility
as fuel. It answers [USER]'s guest-slot question by giving guests the stage
alone. It also cuts seven thin archetypes to three, each with a bridge.

**The K3 risk is real, and no rules switch fixed it.** A Drain the Singer
fully repays costs nothing and earns Fanfare twice. Four switches were run
at 1000 runs on the same seeds (`--k3`, commit 948080ed):

| Variant | Drains taken (balanced) | Always minus judged | Balanced fights | Finale vs act-2 boss |
|---|---|---|---|---|
| Today's rules | 98% | +0.01 | 5.97 | 26% |
| Singer repays only on a turn with no Drain | 90% | −0.08 | 5.66 | 20% |
| Restore gives no Fanfare | 98% | +0.01 | 5.76 | 20% |
| Both | 94% | −0.05 | 5.43 | 17% |
| Singer repays 1 | 97% | −0.04 | 5.75 | 19% |

- The double Fanfare is not the cause: the judged pilot never priced it.
- Only the Singer-rests switch makes declining a Drain pay at all, and the
  effect is small for the power it costs.
- **Read:** at these prices a Drain is close to a well-priced cost, like
  Ironclad's HP cards. The decision lives in three places:
  - the draft;
  - the line;
  - the killing turn, where HP isn't repaid.
  It does not live on every turn.
- That may be acceptable, since StS asks the same of Offering. The sim
  pilot cannot settle it. The seats and [USER]'s run settle it, with K3
  asked as written.
- **No switch is recommended now.** Keep the paper's rules. If the seats
  call Drain a reflex, the first lever is the price: Drain 3 for +7 on
  Curtain Rise is cheap. The Singer-rests rule is the second lever, because
  it is the one that made judging pay.

**Two things the paper must carry into the build:**
1. **Loops carried over from v2.** The v2 loop audit (`furina_loop_probe`,
   PR #900) found 37 open loops. The proposal cuts most of their parts: the
   Cue family with Oratrice's Verdict, Thunderous Applause, and Bis!. It
   keeps two:
   - **Star Billing**, with 0-cost upgraded guests: a repeat play makes the
     oldest guest leave, act and draw. Ten loops in v2.
   - **Lyney's Trick per Drain**, bounded only by Drain room. A Five-Century
     Act widens that room to 1 HP.
   The build must run the loop probe on the new pool before seats.
2. **Neuvillette and the Singer.** Under Singer-rests, does his act's Drain
   count? Moot while the switch is off. Rule it if it comes on.

**Smaller notes:**
- The starter may overshoot: first elite won 67%, against 32% for the
  reference Ironclad. A strong starter is the act-1 job [USER] asked for,
  so this goes to the seats with the paper's lever.
- ~~The Restore refund sentence keeps the law's purpose intact.~~
  Withdrawn in sec.15: GPT showed it rewards stalling a kill.

## 15. Reviews folded in (Fable and GPT, 2026-10-05)

Both reviewers would build it. GPT wants a small playable slice before a
full sheet. These are the paper's changes. The design calls are the main
session's.

**1. Multipliers read Drain and Restore, never hits (Fable).**
- A hit still pays 1 Fanfare per HP. That's the recovery mechanism, and the
  `nohit` variant showed late scaling needs it.
- **The problem:** with Universal Revelry and Critics' Darling, a 30-damage
  hit was worth about 6 damage per HP lost, so Blocking worked against her
  own plan.
- **New texts:**
  - Universal Revelry: "Whenever you Drain or Restore, gain that much
    additional Fanfare."
  - Critics' Darling: "Whenever you Drain or Restore, deal that much damage
    to a random enemy."
- Neither triggers itself. A second copy adds again (two copies give +2x,
  not 4x).
- **Lynette keeps her hit line.** It is her identity, it fires once a turn,
  and it is flat.

**2. The Crowd gets an Uncommon scaling Power (Fable).**
- Thunderous Applause (Power, 1, Uncommon): "Whenever you Spend, deal 3
  damage to ALL enemies." [4]
- A spend-all counts as one Spend.
- Each archetype now has an Uncommon Power reading its own verb:
  - Salon's Encore reads Drain;
  - Endless Waltz reads Restore;
  - Thunderous Applause reads Spend.
- It also attacks the idle-Fanfare result (K5): it pays for spending often
  rather than banking.

**3. Stalling: the refund argument is withdrawn (GPT).**
- Restoring only self-drained HP caps the reward for delaying a kill. It
  doesn't remove it.
- **The cap:** outstanding drain, at most half her entry HP, repaid at 2 a
  turn. Every stalled turn must also Block the enemy fully.
- That is the same order as base-game stalls, but it is a real one.
- **Seats get the question:** "Did you ever keep a beaten enemy alive to
  collect repayment?"
- **Lever if yes:** the curtain call repays everything (all drained HP
  returns when the fight ends). Stalling then gains nothing. The price is
  the killing-turn tradeoff, so Drain's only cost becomes the risk of being
  low when hit.
- Pick 3 below now asks for a prototype exception, not a law change.

**4. Neuvillette spends no HP on his own (GPT).**
- New act: "Deal Hydro damage to ALL enemies equal to the HP you drained
  this turn."
- The player's own Drains feed him, and a guest never takes permanent HP
  unasked.
- This also settles the Singer-rests question in sec.14.

**5. Fewer choosers (both).**
- **Two-mode cards** where the plain mode is a real line:
  - Curtain Rise, which teaches;
  - Chevalmarin;
  - Usher;
  - Tidal Flourish;
  - Spirited Aria.
- **Fixed-cost cards** where the answer would be yes:
  - Crabaletta: "Drain 5. Deal 26."
  - Solicitation: "Drain 2. Deal 9."
  - Quick Flourish: "Spend 4. Deal 11 and apply Hydro."
- A fixed-cost card can't be played if its price can't be paid. That's
  Hemokinesis's shape.
- This puts the Drain-or-not choice into the draft and the play-or-hold
  decision, where GPT says it honestly lives. The Singer funds a modest
  steady pace, and the big Drain cards overdraw it.

**6. Pneuma is about timing and conversion (GPT).**
- "Drain a little, Restore a lot" was wrong, since Restore can't exceed what
  was drained.
- **What Pneuma Restores are for:**
  - reopening Drain room this turn;
  - getting healthy before a big intent;
  - feeding converters: Endless Waltz, Clorinde, Sigewinne, Charlotte.
- A plain Restore that only speeds up a refund the Singer would make
  anyway is filler, so Pneuma Commons each carry a body: damage or Block.
- Draft question for seats: "did a Restore card change your turn?"

**7. Rising Applause always spends.**
- The face says "Spend all your Fanfare". The slice let the pilot skip it
  (sec.10), and the build will match the face.
- The bank-or-spend choice is whether to play it now. The slice reruns K1
  under that rule before the seats.

**8. Loops.**
- **Salon's Tab:** its Energy now arrives next turn, the Interval Bell fix
  from #900.
- **Before seats, the loop probe covers:**
  - Salon's Tab with Interval Bell;
  - Star Billing with 0-cost guests;
  - Lyney with A Five-Century Act.

**9. Seats.** They play into act 2. On top of K3, they're asked:
- ever declined a Spend;
- ever stalled a kill;
- did a Restore change a turn.

## 16. [USER]'s two changes, and the slice spec (2026-10-05)

[USER]: "we now have 3 keywords (Heal, Mend and Restore) that might be worth
unifying. Do we need to separate Restore from Mend?" And: "I lean towards
making 'restore drain at the end of the fight' a default anyway so it can't
brick you".

**Restore becomes Repay. It is not merged into Mend.**
- **Different rules:**
  - Mend (Kokomi, `text-conventions.md`) heals any HP lost this combat, up
    to the HP she started it with. Enemy damage included.
  - Furina's verb returns only HP she drained herself.
- **Why not merge them:**
  - If Furina Mended, she would heal hits at Common. That is the healing law
    and Kokomi's "HP stability" lane.
  - If Kokomi's Mend shrank to drained HP, it would do nothing for her.
- **What was wrong was the word, not the split.** "Restore" reads as a third
  synonym for heal. "Repay" carries the loan and says it is not healing:
  "Repay 3."
- **Player-facing count:** Heal (base), Mend (Kokomi) and Repay (Furina),
  each owned by one kit.
- `text-conventions.md` gains Drain and Repay rows. Its stale "Drain your
  Fanfare" row, from a retired kit and with no live card, goes.

**The curtain call repays everything (the default rule).**
- **New rule:** when a combat ends, all HP she drained returns.
- **What it removes:**
  - the stall incentive (sec.15 point 3);
  - the run-long attrition risk (sec.14);
  - the "brick" [USER] named.
- **What it costs:** the killing-turn tradeoff. Drain's price becomes being
  lower when the next hit lands and nearer the line, inside the fight.
- **Balance read:**
  - The slice measured unrepaid HP of 2.5 a fight on a drafted deck, 2.8 on
    a balanced deck and 5.8 on a heavy Drain deck.
  - The rule is worth that much each fight. That is the same order as
    Ironclad's Burning Blood (heal 6 after each fight) and below it for
    most decks.
  - For a character with no other out-of-combat healing, it is not out of
    line.
  - It does stack on a starter that already overshoots act one (K1), and it
    makes Drain more of a yes (K3).
  - **Price check:** Crabaletta goes 26 → 24 in the slice. The slice reruns
    K1 and K3 with the rule on, against without, before seats.
- The Singer keeps its job: refilling Drain room and making Fanfare *inside*
  the fight.

**The slice (pick 1).** It's the starter plus 24 cards. Texts are final for
the slice, and the numbers are the instrument's.

*Rules:* sec.2's rules, with Restore renamed Repay, plus the curtain call.
The line is half the HP she started the combat with. There are three guest
seats, and nothing else uses the stage.

*Starter:*
- Strike x4 and Defend x4 (base).
- Curtain Rise (Basic Attack, 1): "Deal 7 damage. Drain 3: deal 14
  instead." [10 / 18]
- Rising Applause (Basic Skill, 1): "Gain 5 Block. Spend all your Fanfare
  and deal that much damage." [7 Block]
- Salon Solitaire (relic): "At the end of your turn, Repay 2." [3]

*Drain (5):*
- Mademoiselle Crabaletta (Attack, 2, Common): "Drain 5. Deal 24 damage."
  [30]
- Soloist's Solicitation (Attack, 0, Common): "Drain 2. Deal 8 damage." [11]
- Surintendante Chevalmarin (Attack, 1, Common): "Deal 4 Hydro damage to
  ALL enemies. Drain 3: deal 8 instead." [6 / 11]
- Gentilhomme Usher (Skill, 1, Common): "Gain 7 Block. Drain 3: gain 13
  instead." [9 / 17]
- Salon's Tab (Skill, 0, Uncommon): "Draw 1 card. Drain 4: also gain 1
  Energy next turn." [Draw 2]

*Repay (4):*
- Surging Waters (Attack, 1, Common): "Deal 6 damage. Repay 3." [9, Repay
  4]
- Hymn of Many Waters (Skill, 1, Common): "Gain 8 Block. Repay 3." [11,
  Repay 4]
- Pneuma Refrain (Skill, 1, Uncommon): "Repay 5. Draw 2 cards." [Repay 7]
- Singer of Many Waters (Skill, 1, Rare): "Repay all your drained HP.
  Exhaust." [cost 0]

*Fanfare outlets (6):*
- Tidal Flourish (Attack, 1, Common): "Deal 5 damage to ALL enemies. Spend
  6: deal 12 Hydro damage to ALL enemies instead." [8 / 16]
- Spirited Aria (Attack, 1, Common): "Deal 8 damage. Spend 5: deal 13 and
  draw 2 instead." [11 / 17]
- Quick Flourish (Attack, 0, Common): "Spend 4. Deal 11 Hydro damage." [14]
- Standing Ovation (Attack, 1, Common): "Spend all your Fanfare. Deal that
  much damage to ALL enemies." [Retain]
- Interval Bell (Skill, 0, Common): v2 text after #900, unchanged.
- Bravura (Attack, 1, Uncommon): "Spend all your Fanfare. Deal 6 damage,
  plus 2 per point." [3 per]

*Powers (3, Uncommon):*
- Salon's Encore (1): "Whenever you Drain, deal 3 damage to ALL enemies."
  [4]
- Endless Waltz (1): "Whenever you Repay, deal that much damage to a
  random enemy." [Innate]
- Thunderous Applause (1): "Whenever you Spend, deal 3 damage to ALL
  enemies." [4]

*Guests (4, cost 1, upgraded 0):*
- Charlotte (Common). Line: "The first time you Repay each turn, draw 1
  card." Act: "Repay 2."
- Wriothesley (Uncommon). Line: "Whenever you Drain, deal that much Cryo
  damage to a random enemy." Act: "Deal 4 Cryo damage to a random enemy."
- Lynette (Uncommon). Line: "The first time each turn an enemy makes you
  lose HP, gain that much Fanfare again." Act: "Deal 3 Anemo damage to an
  enemy with an aura."
- Clorinde (Rare). Line: "Whenever you Repay, deal twice that much Electro
  damage to a random enemy." Act: "Deal 6 Electro damage to a random enemy."

*Rares (2 more):*
- Universal Revelry (Power, 2): "Whenever you Drain or Repay, gain that
  much additional Fanfare." [cost 1]
- Let the People Rejoice (Attack, 2): "Spend all your Fanfare. Deal 2
  damage to ALL enemies per point." [cost 1]

*Relics and potions:*
- **Kept:** Opera Glasses, Grand Theater Program and Bottled Applause.
- **Out of the slice's pools:** every other Furina relic and potion. They
  name the trio or Rehearsal.

*Screen:*
- The Fanfare gauge stays.
- **Drain room** must be readable before any play: the line, and how much
  is drained. The cheapest honest reading is a second counter beside
  Fanfare: "Drained N", whose hover says "You can Drain down to M HP". A
  tick on the HP bar is better, if the HP bar can take one safely.
- A Drain mode or card that would cross the line greys out.

## Picks for [USER]

1. **The direction, as a slice.** Build a small `+proto` slice, not the
   full 78. It has:
   - the starter;
   - about 6 Drain cards, 4 Restore cards and 6 Fanfare outlets, mostly
     Common;
   - the three Uncommon Powers;
   - four guests (Wriothesley, Charlotte, Clorinde and Lynette);
   - three Rares (Universal Revelry, Let the People Rejoice and Singer of
     Many Waters).
   You play it, and a two-seat round plays it into act 2. The full sheet
   waits on that. Default: yes. 2: the full sheet now, as Fable suggests.
2. **The starter** (sec.7): Curtain Rise becomes "Drain 3: deal 14",
   Rising Applause becomes "Gain 5 Block. Spend all your Fanfare and deal
   that much damage", and Salon Solitaire becomes "Restore 2 at the end of
   your turn". Default: yes. 2: keep today's Curtain Rise (Spend), add the
   Drain card as a Common.
3. **Restore at Common, for the prototype only.** It's a prototype exception
   to the healing law (`LAW.md`, R8), not a law change. The law text is
   amended only if it survives play and the stall question. Default: yes.
   2: no, and Pneuma shrinks to the relic plus Rare cards.
4. **The line.** Half the HP she started the combat with. Default: yes,
   because of K4. 2: Genshin's half of Max HP, which reads more cleanly on
   the HP bar but locks Drain in fights started below it.
5. **The current build** stays installed as the reference until this is
   ruled. Default: yes. *Ruled differently:* the frozen tag is the
   reference, and v2 is discarded (see the ruling note below).
6. **If seats call Drain a reflex.** The first lever is the Singer resting
   on a turn with a Drain (Fable), not higher prices. Default: hold until
   the seats report.

**Ruling (2026-10-05).**
- [USER] on the paper: "Overall this makes sense".
- [USER] on the two changes in sec.16: "Sounds good".
- [USER] on the builds: "let's leave yesterday's already-frozen reference
  build for now, but the current one built overnight can be discarded."

What that means:
- **Picks 1 to 4 and 6:** the defaults, with Repay and the curtain call
  from sec.16.
- **The reference:** the tag `furina-stage-frozen-2026-10-04` (main at
  #888), kept as is.
- **The overnight v2 build is discarded.** That covers PRs #889 to #897 and
  #900's Furina rows. The slice replaces it in place, as the release
  Furina, not as a `+proto` arm beside it.
- **What the slice keeps from v2's machinery:** what sec.8 names as reused.
  - the Spend chooser;
  - the Fanfare gauge;
  - guest seats;
  - the leave-and-act-once-more exit;
  - the summon preview.
