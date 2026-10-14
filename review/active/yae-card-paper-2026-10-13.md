# Yae Miko: the card paper (first batch)

**Stage: Paper.** The proposal (`review/active/yae-proposal-2026-10-12.md`)
was ruled on 2026-10-12: the Shrine and the Publishing House, Annotations
that last the combat unless Published, Sakura that last 3 turns with Tenko
refreshing them. Stellar-Conduct is parked and nothing here leans on it.
[USER]'s open question: "how we keep the Sakura interesting / scaling beyond
just 'get some free Electro damage each turn'." Section 4 answers it three
ways and marks a default.

What this paper carries: the rules as readings (sec.2), the starter and relic
(sec.3), the scaling answers (sec.4), a 30-card first batch (sec.5 and the
appendix), the census against the base game (sec.6), what the sim showed
(sec.7) and the picks (sec.8). Rows: `docs/yae-staging.yaml`, a sim-only
sheet. Rules twin: `tier0/engine/yae_shrine.py`. Harness:
`tools/yae_expansion_sim.py`. No C# until the picks are ruled.

## 1. The promise, restated

Yae runs a shrine and a publishing house. The shrine is up to three Sesshou
Sakura beside her that strike a random enemy with Electro at the end of every
turn and grow stronger as she tends them. The publishing house is her deck:
she Edits cards in hand, and at a rest she Publishes the one edit worth
keeping. The two meet in Sakura Seal, an Annotation that plants a Sakura
whenever its card is played. The Defect itch is scratched by the shrine (a
board that pays every turn, a cash-in to time, a number that grows, several
ways to build it); nothing of Defect's signature is copied (no queue, no
Evoke, no orb types, no Focus).

**Element and cadence.** Electro, catalyst-grade: her Attack cards deal
Electro damage, as Klee's deal Pyro. Base Strike and Defend apply nothing.
HP 72 (between Klee's 70 and Kokomi's 80: she is a catalyst who ends fights
through her shrine, not a tank).

## 2. The rules, as readings

Every reading a builder would otherwise choose. The sim takes exactly these.

**Sakura.**
- Up to **3** Sakura stand beside her. Each has a **Level** (1 to 3) and a
  timer of **3 strikes**.
- **Plant** adds one at Level 1 with 3 strikes left. Planting while others
  stand raises every standing Sakura's Level by 1 (max 3). Planting while
  three stand levels the three and adds none. (Pick 1 (a); (b) replaces the
  oldest instead and has no Levels.)
- **Strike:** at the end of her turn each Sakura, oldest first, deals **2 +
  its Level** Electro damage (3 / 4 / 5) to one random living enemy. It is a
  pet's hit: her Strength and Weak do not apply; the enemy's Vulnerable and
  Block do; it applies Electro and reacts with whatever aura it lands on,
  credited to Yae. A mature shrine is 15 a turn.
- After the strikes every timer ticks; a Sakura at 0 withers. So a Sakura
  planted on turn N strikes on turns N, N+1 and N+2 and is gone on N+3.
- **Tenko:** every Sakura strikes now (the same strikes, oldest first), then
  every timer is set back to 3. Tenko with no Sakura does nothing. Tenko
  keeps the board (Genshin 6.7); nothing is consumed.
- Targeting is random unless a card aims it (Foxfire Lure: "this turn, your
  Sakura strike it" holds for the end-of-turn strikes and any Tenko this
  turn, while that enemy lives).
- "Standing" counts Sakura now, not planted this combat. "Each Sakura lasts
  1 more turn" adds 1 strike to every timer. "Each Sakura gains a Level" is
  +1 each, capped.
- In co-op every Sakura is hers; a strike that reacts with a partner's aura
  is her reaction (LAW: credited to the player who triggered it).

**Edit and Annotations.**
- **Edit a card in your hand:** the card gains one Annotation for the rest
  of the combat, overwriting any it had. Never the Edit card itself, never a
  Status or Curse, never a kit card. When nothing qualifies the Edit does
  nothing (and still paid its cost).
- The five Annotations (her Enchantments, one per card, saved on the card
  as the engine's `CardCmd.Enchant` already does):
  - **Red Ink:** this card deals 3 more damage (per hit) and gives 3 more
    Block (per gain).
  - **Footnote:** when played, draw 1, after its own effects.
  - **Deadline Extension:** Retain.
  - **Fox Fire:** when played, deal 4 Electro damage to a random enemy,
    after its own effects, a pet's hit.
  - **Sakura Seal:** when played, plant a Sakura, after its own effects.
- **Annotated** means carrying any Annotation, a Published one included.
  "For each Annotated card in your hand" counts the card being played too
  (Bestseller counts itself when it is Annotated).
- Annotations ride copies made in combat only if the copy is of the
  instance (a card that copies "this card" copies its Annotation; a card
  that adds a fresh copy by id does not).
- An Annotation ends with the combat unless Published.

**Publish.**
- A Published Annotation lasts the rest of the run. A Published card can be
  Edited again in combat (the Edit wins for that combat; the Published one
  returns next fight) and Published again later (the new one replaces it).
- **In combat** (The Seven Glamours): choose an Annotated card in hand; its
  Annotation is Published.
- **At a rest site** (the relic, sec.3): see pick 2. Default: the card keeps
  the Annotation it last carried in a combat this run (its *draft*; the
  game remembers one draft per card), so Publishing is a choice among edits
  she has already played with, not a menu.

**Keywords.** Two of her own beyond the element system: **Sakura** (its tip
explains plant, Level, the timer and Tenko) and **Edit** (its tip lists the
five Annotations; Publish is the relic's word). Pick 6.

## 3. The starter

Strike x4, Defend x4 (base game), and:
- **Yakan Evocation** (Skill, 1): Plant a Sakura. Upgrade: cost 0. Her E;
  the shrine's teaching card.
- **Proofread** (Skill, 1 [0]): Edit a card in your hand: Red Ink. Ruled
  2026-10-13 (pick 3): no Block, and the upgrade makes it cost 0, like a
  Defect starter. The sim's plain-Proofread battery read 15.2 HP lost a fight
  (sec.7); that gap is read again once the pool is built.
- **Meditations of a Yako** (starting relic, her utility passive's name):
  "At a rest site you may Publish: a card you Edited this run keeps its last
  Annotation for the rest of the run." In place of Rest or Smith, the way
  Shovel adds Dig. Its upgrade, **Enlightened Blessing** (her A4): "You may
  Publish and then Rest or Smith." No free setup: fight one opens with an
  empty shrine and an unedited deck.

The upgraded starter cards need distinct names (LAW): proposed "Yakan
Evocation: Sesshou Sakura" and "Line Edit".

## 4. How the Sakura scale: three answers

The placeholder was "2 each with one out, 3 each with two, 4 each with
three", which caps at 12 a turn after three plants and then only asks to be
kept alive. The three answers below each add a decision; the first is the
default and is what the batch and the sim are built on.

**(a) Levels, by planting (default).** A Sakura is planted at Level 1 and
every plant while others stand levels the standing ones. Three plants give
Levels 3/2/1 (12 a turn); the fourth and fifth plants level the rest to
15 a turn. The 3-turn timer is the cost: without a Tenko the oldest, highest
Sakura withers first, so the rhythm is plant, plant, plant, Tenko, plant.
What it adds: a visible per-Sakura number the player raises by choosing to
plant into a full shrine instead of spending the energy elsewhere; Tenko
becomes both the cash-in and the way to keep the elders; Fox's Mooncall (C2
in Genshin: start at 2, cap 4) is a real Rare. What it costs: two numbers
per Sakura on the display (Level and turns left), and a slower start than
(b) (sec.7, both measured).

**(b) Count, plus a Tenko bonus.** The placeholder table (lifted to 3/4/5
so the ceiling matches (a)); a fourth plant replaces the oldest; each Tenko
adds 1 to every later strike this combat. One number per Sakura (turns
left) and one shrine number. Scaling lives entirely in Tenko timing, so a
deck without Tenko cards has a flat 15. Closest to the proposal.

**(c) The shrine reads the board.** The count table, and a strike that
reacts (lands on Pyro, Hydro or Cryo) deals 4 more. Scaling comes from
partners and Companions, which is her Genshin role, but solo it is a flat
turret, which LAW's pillar 3 ("every character clears solo") argues
against. Not simmed; Edict of Cleansing carries this idea as an Uncommon
Power under (a) instead.

Beyond the base rule, the pool scales the shrine in (a) and (b) alike:
Sakura Grove (+1 [2] a strike), Fox's Mooncall (Level 4), Yakan Offering (a
free plant every turn), Sakura Channeling (Block per strike), Editor-in-Chief
(a strike per Annotated play) and Sakura Seal (plants from any card). A
later batch owns the C6 nod (Forbidden Art: Daisesshou, strikes ignore
Block) and the Stellar-Conduct nod once an Inazuma Cryo partner exists.

## 5. The batch (32 rows: 2 starter, 9 / 13 / 8)

Three archetypes compete for the slots, as the template asks:
1. **The Shrine:** plant, keep three alive, time the Tenko. Twin Sakura,
   Thunder Rite, Shrine Offering, Shrine Maiden's Guard; Sakura Grove,
   Kitsune Rite, Thunderbolt Tithe, Rooted Shrine, Edict of Cleansing; Tenko
   Kenshin, Fox's Mooncall, Yakan Offering, Sakura Channeling.
2. **The Publishing House:** Edit, play the Annotated card, read the
   Annotated hand, Publish. Kitsune Flash, Deadline, Fox Fire Draft;
   Bestseller, Print Run, Footnote, Sakura Seal, Serialization, Manuscript
   Pile; The Seven Glamours, Reborn as Guuji Yae, Editor-in-Chief.
3. **Kitsune Mischief:** Weak, draw, aim. Sly Strike, Fox Trick; Kitsune
   Guile, Foxfire Lure; Mischievous Teasing.

Bridges: Sakura Seal (house to shrine), Editor-in-Chief (house to shrine),
Foxfire Lure (mischief to shrine), Manuscript Pile (mischief to house),
Kitsune Flash (a Common that asks to be Edited). Her defence is six Block
cards in 30 (Shrine Offering, Deadline, Shrine Maiden's Guard, Rooted Shrine,
Print Run, Sakura Channeling) plus Proofread; the shrine itself guards
nothing, which is the intended weakness beside random targeting and the slow
first two turns.

**Not in this batch, said so:** the Companion card "Yae Miko: Sesshou
Sakura" (pick 5), the two Ancients (Tome and Tooth, next batch), the co-op
five (Editor's Note: Edit a card in an ally's hand, is the first), the C6
Power, and the second half of the pool to 78 (the audit after the user's
first play says what it is short of; the kit-checklist's "audit before
adding" rule).

Every card, with cost, text, upgrade and its one-line why, is the appendix.

## 6. Census: not Defect, by archetype

- **The Shrine against Defect's orbs.** Defect channels orbs into an ordered
  queue of up to 3 (10 with slots), each a type with its own passive and
  Evoke; Focus raises all of them; the decisions are which orb to push out
  and when to Evoke. The Shrine is one object, Sakura, capped at three, each
  with its own Level and timer; nothing is pushed out and nothing is
  consumed; the scaling number is earned per Sakura by planting; the
  cash-in keeps the board. Against our own Klee (Bombs sit on enemies, grow
  on their own, go off only when set off) and Kokomi (one jellyfish that
  carries out Plans) it is the only pet that fires by itself and expires.
- **The Publishing House against the base game.** The packet's census
  (proposal sec.2) found one base card that gives a card an Enchantment
  (Silent's Blade of Ink), and in-combat upgrades that reset every fight
  (about 30 cards). No base character edits cards as an identity, none
  reads "for each enchanted card", and none keeps an edit across the run by
  choice. The nearest shape is the base rest site's Smith, which Publish
  competes with.
- **Kitsune Mischief against the Silent.** Weak and draw are the Silent's
  (Neutralize, Leg Sweep, Malaise, Acrobatics); hers are five cards of 30,
  and the one new verb is aiming the shrine (Foxfire Lure), which the Silent
  has no turret to aim.

## 7. What the sim showed (smoke checks, not balance claims)

`tools/yae_expansion_sim.py` on the staging rows, 100 seeds, stylised act 1
(`N N N N E R N N E R B`, then an act-2 boss), the stock pilot, four
drafters. The Varka harness on the same template and seeds is the
calibration: his default drafter wins act 1 **20.6% ±6.3** (160 runs, four
starts). Read the gaps, not the levels.

1. **The starter battery** (every act-1 easy and hard encounter, full HP,
   600 fights): with the plain Proofread and strikes of 1 + Level she wins
   every fight in 6.0 turns at 10.8 damage a turn (2.0 of it Sakura) and
   loses **15.2 HP** a fight on 3.1 Block a turn. Varka's starters on the
   same fights lose 10.3 (Hydro) and 7.9 (Pyro) at 12.6 and 15.7 damage a
   turn. She bleeds, and arrives at the first elite at about 12 HP: **0 of
   100 runs** cleared act 1 under every pilot and every rule variant tried.
   With the paper's defaults (item 2) the battery reads 5.4 turns, 11.8
   damage a turn (2.6 Sakura), **12.0 HP** lost on 4.1 Block a turn; the
   first elite then falls in 26 of 400 runs, and no run passes the act-1
   boss. The second half of the pool and a tuned drafter are what Varka had
   and she does not yet; the gap to his starter is the number to watch.
2. **The levers, paired on the battery** (300 fights each): Proofread with
   4 Block, 13.5 lost; strikes of 2 + Level, 13.9; both, **11.9**; both and
   Sakura planted at Level 2, 10.5; both and 4-turn timers, 11.2; Proofread
   plain and Yakan Evocation with 3 Block, 13.1. The paper's defaults are
   "both" (pick 3); the rest are the alternatives.
3. **The shrine does not mature off the starter.** Sakura standing per turn
   on the drafted decks: 0.3 on turn 1, 1.1 on turn 3, 1.4 to 2.0 by turn 5
   (the shrine drafter highest). Mean Level 1.3 to 1.6. With one plant card
   in ten and a 3-turn timer, three Sakura need a plant every turn or a
   Tenko every third; the batch holds four plant sources and three Tenko.
   That is the new fact behind pick 4.
4. **(a) against (b), paired** (the same seeds and drafts, the paper's
   defaults): the shrine drafter's Sakura deal 4.0 a turn under Levels and
   4.8 under the count table (all damage 11.2 against 12.0), because (b)
   pays the full 3/4/5 from the first plant while (a) ramps. Neither shrine
   reaches three (1.7 standing by turn 5, mean Level 1.5 under (a)). The
   difference the user would feel is the display and the plant decision;
   the number gap is one Level's worth.
5. **Plays per fight held** (default drafter): Thunder Rite 1.8, Shrine
   Offering 1.5, Kitsune Flash 1.5, Twin Sakura 1.4, Bestseller 1.3, Print
   Run 1.2; Kitsune Rite 0.3 (Exhaust, held for a full shrine that rarely
   comes). The stock drafter never takes Sakura Seal, Footnote or Fox Fire
   Draft (it prices an Edit at nothing), so the publishing archetype is read
   only through its forced drafter: 1.6 to 2.8 Edits a fight (1.9 for
   every drafter once Proofread carries Block, since it is then played), one
   Publish in a hundred runs. Of the 26 runs that reached the rest every one
   rested: no Sakura Seal or Footnote draft was waiting, because the stock
   drafter never takes those cards. The rest-site Publish is built and
   unread; it needs a drafter that values an Edit, which is the next harness
   step.

Raw files: the PR body carries the two run tables; the harness reproduces
them (`--seeds 100 --seed 7 --scaling level|count`).

## 8. Picks for [USER]

1. **How the Sakura scale.**
   - **(a) Default:** Levels by planting (sec.4). Two numbers per Sakura on
     the display; the plant decision is the scaling decision.
   - (b) Count, plus 1 a strike per Tenko. One shrine number; scaling is
     Tenko timing alone.
   - (c) Count, plus 4 on a strike that reacts. Partner-keyed; flat solo.
2. **What the rest-site Publish keeps.**
   - **(a) Default:** the card's last Annotation from a combat this run
     (a draft per card). You Publish what you played with.
   - (b) Any of the five, chosen at the rest. A menu; the combat Edits and
     the run arc come apart.
3. **The starter's second card.**
   - **(a) Default:** Proofread, "Gain 4 Block. Edit a card in your hand:
     Red Ink." (11.9 HP a fight with 2 + Level strikes.)
   - (b) Proofread plain, "Edit a card in your hand: Red Ink." (15.2.)
   - (c) Proofread plain, and Yakan Evocation "Plant a Sakura. Gain 3
     Block." (13.1; the shrine card carries the defence.)
4. **The Sakura timer, reopened by sec.7 item 3.**
   - **(a) Default:** 3 turns, as ruled; the pool supplies plants and Tenko.
   - (b) 4 turns (11.2 against 11.9 on the battery; one more strike a plant).
5. **The universal Companion "Yae Miko: Sesshou Sakura".**
   - **(a) Default:** it stays in the Inazuma roster for the other
     characters and is hidden from Yae's own offers (her Sakura are her
     kit's, by the character-only ruling of 2026-10-12).
   - (b) It leaves the roster and becomes her Uncommon "Sesshou Sakura:
     Plant 2 Sakura" (Twin Sakura's slot, which then goes).
6. **Keyword budget.**
   - **(a) Default:** two tips, Sakura and Edit; Tenko lives in the Sakura
     tip and the five Annotation names in the Edit tip.
   - (b) Four tips (Sakura, Tenko, Edit, Publish), as Klee carries four.

With the picks ruled, the C# build follows the staging rows unchanged in
grammar: the `yae` op, the shrine power, the five Enchantments, the relic's
rest-site option, and the rows move onto `docs/prototype-surface.yaml`.

## Appendix: the cards

Numbers in brackets are the upgrade. "Electro" on an Attack is her cadence.

**Starter**
- **Yakan Evocation** (Skill, 1 [0]): Plant a Sakura. The shrine, from fight one.
- **Proofread** (Skill, 1 [0]): Edit a card in your hand: Red Ink. The house, from fight one; ruled pick 3 (no Block, the upgrade costs 0).

**Common (9)**
- **Kitsune Flash** (Attack, 1): Deal 6 [8] Electro damage. If this card is Annotated, deal 3 [4] more. The Common that asks to be Edited.
- **Thunder Rite** (Attack, 2): Deal 8 [11] Electro damage. Tenko. The Common Tenko, priced at 2 so a full shrine is the reason to play it.
- **Shrine Offering** (Skill, 1): Gain 6 [9] Block. Each Sakura lasts 1 more turn. Block that keeps the elders; the binding price is a Defend's rate.
- **Twin Sakura** (Skill, 2 [1]): Plant 2 Sakura. The count builder; two Levels for the standing on one play.
- **Deadline** (Skill, 1): Gain 4 [6] Block. Edit a card in your hand: Deadline Extension. Retain on the card you are saving for the Tenko turn.
- **Fox Fire Draft** (Skill, 0): Edit a card in your hand: Fox Fire. Exhaust. [Edit 2 cards.] A free 4 Electro on a card you play often; 0-cost because it draws nothing.
- **Sly Strike** (Attack, 1): Deal 5 [7] Electro damage. Apply 1 [2] Weak. Mischief's Strike.
- **Fox Trick** (Skill, 1): Apply 2 [3] Weak to an enemy. Draw 1 card. Neutralize's cousin at 1 energy, so not a cantrip.
- **Shrine Maiden's Guard** (Skill, 1): Gain 4 [6] Block, plus 2 [3] for each Sakura standing. The shrine's Block reader; 4 with none, 10 with three.

**Uncommon (13)**
- **Sakura Grove** (Power, 1): Your Sakura strike for 1 [2] more. The bounded Focus; +3 a turn at three.
- **Kitsune Rite** (Skill, 1 [0]): Tenko. Exhaust. The pure cash-in, once.
- **Thunderbolt Tithe** (Attack, 1): Deal 4 [6] Electro damage for each Sakura standing. Barrage's rate (4 an orb).
- **Rooted Shrine** (Skill, 1): Each Sakura gains a Level. Gain 3 [5] Block. Levels without a plant.
- **Edict of Cleansing** (Power, 1): Your Sakura strikes deal 4 [6] more to an enemy with a Pyro, Hydro or Cryo aura. The reaction nod from the proposal; partner and Companion value, dead solo.
- **Bestseller** (Attack, 1): Deal 5 [7] Electro damage, plus 3 [4] for each Annotated card in your hand. The house's reader, itself included.
- **Print Run** (Skill, 1): Gain 4 [5] Block, plus 2 [3] for each Annotated card in your hand. The house's Block.
- **Footnote** (Skill, 0): Edit a card in your hand: Footnote. Exhaust. [Edit 2 cards.] The draw engine, Uncommon as the cycling rule asks.
- **Sakura Seal** (Skill, 1 [0]): Edit a card in your hand: Sakura Seal. The bridge: the card you play most plants.
- **Serialization** (Power, 1): Whenever you Edit a card, gain 3 [4] Block. Edits become Defends.
- **Manuscript Pile** (Skill, 1): Draw 2 [3] cards. Edit a card in your hand: Deadline Extension. Mischief's draw with the house's rider.
- **Kitsune Guile** (Skill, 1): Apply 2 [3] Weak to ALL enemies. Leg Sweep's Weak without its Block.
- **Foxfire Lure** (Skill, 1): Apply 1 [2] Weak to an enemy. This turn, your Sakura strike it. Aim for the shrine (kit-checklist 2: targeting the player can steer).

**Rare (8)** (constellation names where one fits)
- **Great Secret Art: Tenko Kenshin** (Attack, 2): Deal 12 [16] Electro damage to ALL enemies. Tenko. Her burst.
- **Fox's Mooncall** (Power, 2 [1]): Your Sakura are planted at Level 2 and can reach Level 4. C2; the shrine's ceiling rises to 18.
- **Yakan Offering** (Power, 2 [1]): At the start of your turn, plant a Sakura. C1; the upkeep solved, every turn a Level.
- **The Seven Glamours** (Skill, 1 [0]): Publish an Annotated card in your hand: its Annotation lasts the rest of the run. Exhaust. C3; the in-combat Publish.
- **Sakura Channeling** (Power, 2): Whenever a Sakura strikes, gain 2 [3] Block. C4; the shrine finally guards her, 6 a turn at three.
- **Mischievous Teasing** (Skill, 0): Apply 2 Weak to ALL enemies. Draw 2 [3] cards. Exhaust. C5.
- **Reborn as Guuji Yae** (Skill, 1 [0]): Choose an Annotation. Edit every other card in your hand with it. Exhaust. The contest; a hand of Sakura Seals is a shrine in one turn.
- **Editor-in-Chief** (Power, 2 [1]): Whenever you play an Annotated card, a Sakura strikes (the highest Level). The house drives the shrine.

Held back, named: Lightning Lash (5 Electro to ALL, 1), Forbidden Art:
Daisesshou (strikes ignore Block, C6), Tengu Taunt (Weak and Vulnerable), a
Common "Sakura Bloom" (0-cost plant, Exhaust) if pick 4 keeps 3 turns and the
shrine still starves.

## Ruled 2026-10-13

[USER]: "1) ideas b and c are actually quite interesting (we'll probably want
multiple Tenko effects, and building scaling into them makes a lot of sense to
me) but we can leave that for a pool expansion. A is fine. 2) agreed on a 3) I
lean towards proofread by itself and having the upgrade make the effect 0 cost,
like a Defect starter. 4, 5, 6) agreed on your picks, a) We might decide that
we need more that 2 keywords as we go, the way Furina ended up with a billion
of them, but let's start simple and see what design space these two enable."

- Pick 1 (a): Levels by planting. (b) and (c) (Tenko-built scaling, reaction
  bonus) return in the pool expansion as Tenko cards (BACKLOG).
- Pick 2 (a). Pick 4 (a): 3 turns. Pick 5 (a). Pick 6 (a): two tips to start.
- Pick 3: **Proofread** (Skill, 1 [0]): "Edit a card in your hand: Red Ink."
  No Block; the upgrade makes it cost 0. The starter battery's HP-loss gap is
  read again once the pool is built.
