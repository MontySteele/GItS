# Blind seat record — KLEEMOD-KOKOMI, lane 1, Act 1

## Identity

- **Model / seat:** Opus (Claude Fable 5.1), blind TESTER seat, lane 1.
- **Run seed:** AB45JR68YMH1. **Character:** KLEEMOD-KOKOMI. **Ascension:** 2.
- **Act:** 1. **Boss named at the top of the map:** *Vantom* (never reached).
- **Actions accepted:** 118 of 120.
- **Termination:** action budget. At 118/120 the only node open was `Treasure`,
  which needs `go` + a claim + `proceed` — three acts I did not have. I stopped
  rather than half-enter a room.
- **HP trajectory:** 64/80 (start) → 57 (f1) → 55 (f2) → 44 (f3) → 33 (f4) →
  38/85 after Morphic Grove (+5 Max HP, +5 current) → 63/85 after Rest →
  46/85 after the Elite → **43/85** at the stop.
- **Gold:** 213. **Potions held:** Attack Potion (1 of 3 slots).
- **Relics:** Tamakushi Casket (start each combat with the Bake-Kurage; whenever
  you apply a debuff to an enemy it deals 2 Hydro damage to that enemy);
  Fishing Rod (every 3 normal combats, upgrade a random card); Regal Pillow
  (Rest heals an additional 15).
- **Deck at the end,** as far as the bridge ever printed it to me. The opening
  fight showed 16 cards (11 draw + 5 hand). Seen by name across the run:
  Strike ×3+ , Defend ×3+ (one of them upgraded to **Defend+**, 8 Block, by
  Fishing Rod), **Ambush**, **Flank**, **Feigned Retreat**, **Read the Field**,
  **Slack Water**, **Battle Plan**, **Kurage's Oath ×2**. Added in the run:
  **Freminet — Pers, Deploy!** (Cryo), **Vanguard**, **Fischl — Nightrider**
  (Electro), **Undertow ×3**. I never saw a full deck screen, and I never once
  saw a Status card printed in a hand even though Leaf Slime announced giving me
  five of them across two turns — the pile counts grew, the cards never showed.
- **Neow pick:** Fishing Rod. I took it because a free upgrade every three
  combats is the only one of the three that pays for the whole act — New Leaf's
  transform is one random card, and Cursed Pearl's 333 gold buys an Eternal
  unplayable into a 16-card deck I could not yet read.

---

## Fight 1 — Fuzzy Wurm Crawler [A] 57/57

**What the screen said about the jellyfish before I had played anything (turn 1):**
`Bake Kurage 1 (buff) — Enemies cannot target it. Lasts all combat. Play a Plan
card on it: it carries out the Plan at the start of your next turn.` and, in its
own block, `Nothing is planned. The morning is empty.` The block also printed
the three targeting rules (front non-Minion; ALL means every living enemy;
every planned HIT is a Hydro hit).

**Turn 1** — Plans written: **1 (Ambush)**. Ambush → Bake-Kurage, then Strike,
Strike (12 now).
*Rejected:* playing Ambush face-up for 5. Its own line reads `Deal 5 damage` and
its Plan line reads `Deal 12 damage` on the same face — with the enemy
telegraphing `Attack for 4`, block was worthless and there was no reason not to
take the bigger number one turn late. A real decision, but an easy one: the card
tells you the answer.

**Turn 2** — Plans: **none**. Morning: `Ambush, 12 — the 12 is damage. Fuzzy Wurm
Crawler lost 12 HP`. Played Flank (8), Strike, Strike = 20.
*Rejected:* planning Feigned Retreat. The enemy's intent was `Empower (Buff)`, so
it would deal no damage this turn; block and delayed damage both bought nothing
and immediate damage was strictly best.

**Turn 3** — Plans: **none**. Enemy at 13 with `Strength 7` and `Attack for 11`.
Played Slack Water (4 + 1 Weak; the relic added 2 = 6), Kurage's Oath (3), Read
the Field (5 Block). Enemy → 4.
*Rejected:* Slack Water + both Oaths — 12 damage, leaving it on 1 HP and me
eating 8. Blocking instead cost 3 points of damage and saved 6 HP, and neither
line was lethal, so the cheaper one won. **This was the first turn of the run
with a genuine cost on both sides.**

**Turn 4** — Plans: **none**. Enemy at 4; Strike (6) killed it. No alternative
existed: one card, one outcome. A dead turn, and I am saying so.

*Refusal (1 of 1 in the run):* `play "Kurage's Oath (1)" on "A"` →
`"Kurage's Oath (1)" does its own aiming, so it takes no "on \"A\"". The form
that resolves: play "Kurage's Oath (1)"`. Fair, and it handed me the working
form; but the card's face says `Deal 3 damage to ALL enemies` with no marker
that it refuses a target, so the refusal was the first place I learned it.

HP 64 → 57.

---

## Fight 2 — Shrinker Beetle [A] 38/38

**Jellyfish, turn 1, before I played anything:** `Nothing is planned. The morning
is empty.` — same block as fight 1, no memory of the previous fight's Plans.

**Turn 1** — Plans: **1 (Battle Plan)**. Flank (8, Hydro), Freminet — Pers,
Deploy! (6, Cryo onto the Hydro aura → **Frozen**), Battle Plan → Bake-Kurage.
*Rejected:* Defend — the intent was `Strategic (DebuffStrong)`, no damage.
**My own misplay, recorded:** I spent the reaction with nothing behind it.
Frozen reads `Its next action deals 50% less damage. Until it acts, an Attack
Shatters it for 6` — the beetle's next action was a debuff (halving it does
nothing) and I had no energy left for the Shatter. The reaction was free value I
threw away because I applied it last instead of first.
*What the screen showed after, and why it looked wrong:* the beetle printed
**Frozen 1 (debuff)** *and* **Hydro Aura 2** — after a Cryo hit that should have
consumed the Hydro. The long `Elemental Reaction` paragraph had already told me
why: Frozen is a debuff, the debuff fires Tamakushi Casket, the Casket's hit is
Hydro, so the aura is consumed and re-applied inside the same beat. The
arithmetic confirmed it: 38 → 22 is 16, i.e. 8 + 6 + the relic's 2.

**Turn 2 — the best decision in the run, and it was printed on the card.**
I was wearing `Shrink -1 (debuff) — While Shrinker Beetle is alive, your Attacks
deal 30% less damage`. Every face rewrote itself: Strike `Deal 4 damage`
(was 6), Ambush `Deal 3 damage` (was 5), Kurage's Oath `Deal 2 damage to ALL`
(was 3). **Every Plan line stayed at its full number** — Oath still read
`Plan: Deal 7 damage to ALL enemies`, Ambush still `Plan: Deal 12 damage`. The
Plan glossary says why: *"no damage term of yours does"* count on a carry-out.
Plans written: **2 (Kurage's Oath, Kurage's Oath)**. Then Read the Field (5
Block) and Strike (4).
*Rejected:* playing both Oaths face-up for 2 apiece. Under Shrink the same card
is worth 2 played and 7 planned, and I could read that off one face without
doing any arithmetic. That is the kit working.

**Turn 3 — morning with two carry-outs.** Printed order, front first:
`Kurage's Oath, 7 — the 7 is damage` / `Shrinker Beetle lost 7 HP`, then the
identical line again. **Order in which they resolved:** as written, first Oath
then second Oath. **Did the order matter to the outcome?** No — two identical
cards on one target; 22 − 4 − 14 = 4, and any order gives 4. Killed with Strike
(4, exactly lethal). Plans: **none**.
Shrink's own text says `your Attacks deal 30% less damage`, but Kurage's Oath is
printed `cost 1, **skill**` and it still fell 3 → 2. **Weak's glossary on the
same screen goes out of its way to say "a Skill's damage too"; Shrink's does
not, and Shrink hits Skills anyway.** That is a contradiction between a debuff's
text and its behaviour.

HP 57 → 55.

---

## Fight 3 — Nibbit [A] 42/42

**Jellyfish, turn 1:** `Nothing is planned. The morning is empty.`

**Turn 1** — Plans: **1 (Battle Plan)**. Battle Plan → Bake-Kurage, Freminet
(6, laying a Cryo aura), Defend (5). Took 7.
*Rejected:* Battle Plan + Defend + Defend (10 block, take 2). I paid 5 HP for 6
damage **and** for a Cryo aura sitting on the enemy that my all-Hydro hand could
react off next turn. A real trade made a turn early — the fight's shape was
decided here.

**Turn 2** — 4 energy (the carry-out printed `Battle Plan, 1 — the 1 is Energy`
and drew me 2). Every Hydro card in hand now printed
`*Reaction preview: Frozen* — Hydro meets Cryo: its next action deals half
damage, and until it acts the first Attack to hit it Shatters for 6 damage`.
Ambush printed **no** preview, correctly, because its face says its own hit
applies no aura. Plans: **1 (Ambush)**.
Order: Flank (8, triggers Frozen; relic adds 2 = 10) → Strike (6 + **Shatter 6**
= 12) → Slack Water (4 + Weak; relic 2 = 6) → Ambush → Bake-Kurage. 36 → 14 on
the first two, exactly as the preview implied.
*Rejected:* Strike as the third card instead of Slack Water — the same 6 damage,
but Slack Water's Weak both procs the relic and cuts the incoming 6 to 4.
*Rejected:* Ambush face-up for 5 — the Plan is 12 and the enemy was about to sit
behind Block, and 12 beats 5 even through block.

**Turn 3** — Morning: `Ambush, 12 — the 12 is damage.` /
**`Nibbit lost 7 HP, and 5 more absorbed by Block`**. That line is the single
most useful thing the bridge printed all run: enemy Block is otherwise invisible
and it told me the exact number after the fact. Plans: **none**.
Killed the 1-HP Nibbit with **Vanguard**, cost 0: it applies Vulnerable, the
Vulnerable is a debuff, the relic's 2 Hydro killed it. *Rejected:* Kurage's Oath
for 3 — Vanguard did it for free and left me the energy I did not need. A small
decision, but it was mine and the screen supported it.

HP 55 → 44.

---

## Fight 4 — Leaf Slime (M) [A] 34/34 and Flyconid [B] 49/49

**Jellyfish, turn 1:** `Nothing is planned. The morning is empty.` The block's
targeting rule mattered for the first time here — `A Plan with one target hits
the front enemy and never a Minion`, and the Slime is printed `(M)`.

**Turn 1** — Plans: **none**. Vanguard (0) on B → `Vulnerable 1`; Flyconid went
49 → 46, i.e. the relic's 2 Hydro **was itself multiplied by the Vulnerable it
had just caused** (2 × 1.5 = 3). Then Fischl — Nightrider (Electro onto the
Hydro the relic had left → `Reaction preview: Electro-Charged`), then Strike,
then Defend. 46 → 24 = 22, which is Fischl 7×1.5 = 10, plus a second relic proc
3 (Electro-Charged applies a debuff), plus Strike 6×1.5 = 9.
*Rejected:* opening on the Leaf Slime. It has 34 HP and its intent was
`StatusCard`, no damage; Flyconid was the body doing 8 a turn and it was the one
Vulnerable could be spent on.

**Turn 2** — I was wearing `Frail 2`. Defend's face read `Gain 3 Block` and
Defend+ read `Gain 6 Block`, so **faces do carry Frail** (they carried Shrink in
fight 2 too). Plans: **none**. Flank + Strike + Strike = exactly 20 = Flyconid's
remaining HP; it died.
*Rejected:* blocking with Defend+ and killing next turn. Poison 3 was already on
Flyconid and would have finished it, but a turn of 11 damage is worth more than
6 block, and removing the attacker left only the harmless Slime.

**Turn 3** — Plans: **1 (Battle Plan)**. Slack Water (4 + Weak; relic 2 = 6),
Freminet (6 + Frozen; relic 2 = 8), Battle Plan → Bake-Kurage. Slime 34 → 20,
matching to the point.
*Rejected:* Defend — the Slime's intent was `StatusCard`, no damage to block.
Note the targeting rule resolved cleanly: with only a Minion left, the printed
exception (*"unless every enemy is a Minion, when it takes the front one
anyway"*) meant Plans could still be written.

**Turn 4** — 4 energy. Plans: **none**. Slack Water + Strike ×3 = 24 ≥ 20, kill.
*Rejected:* planning an Oath for next morning — lethal on the board beats a
bigger number a turn later.

HP 44 → 33.

---

## Fight 5 (Elite) — Byrdonis [A] 82/82, `Territorial 1` (+1 Strength at the end of its turn)

**Jellyfish, turn 1:** `Nothing is planned. The morning is empty.`

**Turn 1** — the hand was three Defends, Feigned Retreat and Undertow: one
damage card against an 82-HP body telegraphing `Attack for 17`. Plans:
**1 (Feigned Retreat)**. FR → Bake-Kurage, Undertow (7 — no debuff on it yet, so
the face read 7, not 10), Defend.
*Rejected:* Undertow + Defend + Defend (10 block, take 7) against
FR-plan + Undertow + Defend (5 block, take 12). Feigned Retreat's Plan line is
`Gain 4 Block **and** deal 6 damage` against its own `Gain 4 Block` — the same
block, plus 6, for the cost of arriving a turn late. Against a body that gains
Strength every turn, buying 6 damage for 5 HP was the right side.

**Turn 2** — Morning printed `Feigned Retreat, 4 — the 4 is Block` with
`Byrdonis lost 6 HP` underneath. **A carry-out whose headline figure and whose
HP line are different quantities** — the page's own note explains it (*"The
figure on the Plan's own line is what its first clause produced"*), and without
that note I would have read the 4 as the damage. Plans: **none**.
Fire Potion (20) + Slack Water (6 with the relic) + Flank (8) + Strike (6) = 40;
82-relevant total 69 → 29.
*Rejected:* holding the potion for a worse spot. `Territorial` means every extra
turn of this fight is strictly more expensive than the last, so a potion spent
to delete a turn is worth more now than later. That is a decision the enemy's
buff text made for me, and it was a good one.

**Turn 3 — the turn the kit earned.** 29 HP left, `Attack for 19` incoming, and
**not one block card in hand**. Plans: **none**.
Freminet (6; Frozen; relic 2 = 8) → Fischl (7 + **Shatter 6** + relic 2 = 15) →
Strike (6). **29 exactly. Lethal, and I took nothing.**
*Rejected, and it was close:* the safe line, Freminet then Ambush and Kurage's
Oath — both are printed `skill`, so they deal damage **without** triggering
Shatter, which keeps Frozen alive to halve the 19 to 9. That line ends the turn
with Byrdonis on 13 and me on ~37. I chose the exact-lethal line because I could
count every term off the faces: 6, +2 relic, 7, +6 Shatter, +2 relic, 6. The
distinction that made the choice possible — *Shatter fires on an Attack, and
Ambush and Oath are Skills* — is printed on both the Shatter glossary and the
card type line, and nowhere is it called out as a combo. I had to notice it.

HP 63 → 46. Rewards: 43 gold, Poison Potion, Regal Pillow, a card.

---

## Fight 6 — Fogmog [A] 74/74, then Eye with Teeth [B] 6/6 (`Illusion`, `Minion`)

**Jellyfish, turn 1:** `Nothing is planned. The morning is empty.`

**Turn 1** — Fogmog's intent was `Summon`, no damage. Plans: **1 (Ambush)**.
Fischl (7, laying Electro on a bare body) → Undertow (7 + Electro-Charged →
`Poison 4` → relic 2). *Rejected:* Strike (6 now) in place of the Ambush plan
(12 next morning) — with no incoming damage there was no reason to want the
smaller number sooner.

**Turn 2 — the mirror of fight 2, and the reason the Plan mechanic is a
decision and not a rule.** Vanguard (0) → Vulnerable, relic hit for 3. Undertow's
face then read **`Deal 10 damage, already including 3 if the enemy has a
debuff`** — and it delivered **15** (42 → 24 across Vanguard's 3 and Undertow's
15). Plans: **none**. Then Kurage's Oath (ALL) and Defend.
*Rejected:* planning the Oath for 7 instead of playing it for 3. In fight 2 the
Plan line won because Shrink could not touch it. Here the played line won,
because `Vulnerable 1` falls off at the end of the enemy's turn and the carry-out
arrives after that — the Plan glossary's *"Enemy Vulnerable counts"* is true but
useless when the Vulnerable will not survive the night. **Two fights, the same
card, opposite answers, both readable off the screen.** That is the kit's best
idea.

**Turn 3** — Fogmog 17, `Attack for 15`. Plans: **none**.
Poison Potion (`Apply 6 Poison` → `Poison 8`; the application is a debuff, so the
relic hit for 2) → Flank (8) → Kurage's Oath (3 to ALL, which also killed the
3-HP Eye). Fogmog finished my turn on **4 HP with Poison 8**, and Poison is
printed `At the start of its turn, loses 8 HP` — so it died at the start of its
own turn, **before its 15 landed**. I played a Defend anyway as insurance and it
was never needed.
*Rejected:* Flank + Oath + Defend with the potion held. That leaves Fogmog alive
on 4, me eating 10, and the Eye reviving (`Illusion 1 — When this dies, it
revives next turn at full HP`). Reading Poison's tick timing off its own text
turned a 10-damage turn into a 0-damage win. The Eye's `Minion 1 — Minions
abandon combat without their leader` also told me not to waste damage on a body
that revives.

HP 46 → 43. Won.

---

## Between fights

- **Morphic Grove** (Unknown, floor 5): `Group` — lose ALL gold, Transform 2
  cards; `Loner` — gain 5 Max HP. Took Loner. Transform is `a random card of any
  rarity`, which in a 16-card kit deck is as likely to delete a Plan card as to
  improve one, and there was a Shop two floors on. Real choice, took the small
  certain one.
- **Rest site** (floor 6): Rest (heal 25) over Smith (upgrade one card), at
  38/85 with an Elite one node away. Not close.
- **Draft picks:** Freminet — Pers, Deploy! (the only card on the sheet that
  reaches a second element, into an all-Hydro deck); Vanguard (0-cost debuff
  that turns the relic into damage and buffs everything after it); Fischl —
  Nightrider (a third element); Undertow ×3 (10 against a debuffed body, and
  after the relic almost everything is debuffed). **Skipped:** Song of Pearls,
  Coral Bulwark, Cleansing Wave, Shell Guard, Pincer, Feint, Moon's Reflection,
  Lynette, Kujou Sara, Charlotte, The Clouds Like Waves Rippling.

---

## The kit, after 6 fights

**(a) Which decisions felt like real choices, and what they traded off.**

1. **Play the line or write the Plan — decided on the turn, off two numbers on
   one face.** Every kit card prints its own effect and its Plan effect side by
   side, and the Plan is always bigger and always a turn late. That is a clean,
   legible tempo trade, and it is genuinely two-sided: under `Shrink` (fight 2)
   the Plan line was untouched while my played lines lost 30%, so planning won
   by 5 damage a card; under `Vulnerable` (fight 6 turn 2) the played line got
   ×1.5 and the carry-out would have arrived after the Vulnerable expired, so
   playing won. **The same card gave opposite answers in two fights and the
   screen let me see why both times.** This is the kit's real content.
2. **Which reaction to set up, and when to spend it — decided a turn earlier in
   the fight.** Freminet's Cryo aura laid in fight 3 turn 1 was worth 6 HP and
   became a 12-damage Shatter turn later. Fight 2 turn 1 was the same setup
   played in the wrong order and it produced nothing.
3. **Shatter or keep the freeze — decided on the turn (elite, turn 3).** Attacks
   Shatter for 6 and end the freeze; Skills deal damage and leave it up. 6 extra
   damage against halving a 19. Both readable, neither obvious.
4. **The Elite's potion timing — decided by reading `Territorial`.** An enemy
   that gains Strength every turn prices its own tempo, and that made the potion
   a "now" card.
5. **At the draft:** Freminet, and then Fischl, were bets that a second and third
   element would pay. They paid — Frozen/Shatter carried the Elite and
   Electro-Charged's poison carried fight 6. Taking Undertow over Pincer/Feint
   was a bet that the relic keeps a debuff on everything, which it does.

**(b) What felt automatic, and what never seemed worth playing.**

- **Strike and Defend.** Nine of my ~15 turns ended with a Strike or a Defend
  filling the last energy because nothing else was there. They carry no Plan
  line at all, which in this kit reads as a blank half-card.
- **Every kill turn was automatic.** Fight 1 turn 4 (4 HP left, Strike 6), fight
  2 turn 3, fight 4 turn 4. This is normal for the genre, but note that four of
  my six fights ended on a turn with no decision in it.
- **Read the Field** never felt worth an energy except as filler. `Gain 5 Block`
  / `Plan: Gain 10 Block` is the one Plan whose delayed version I never once
  wanted, because block I do not need until the enemy swings and I always know
  the intent before I choose.
- **Battle Plan's own line** (`Draw 1 card`) is never playable — the hand is
  discarded at end of turn, so drawing with your last energy draws a card you
  cannot use. Its Plan line (`Gain 1 Energy and draw 2 cards`) is excellent and I
  planned it three times out of three. A card with a dead half.
- **Kurage's Oath played face-up** is 3 damage to all for an energy. It only ever
  earned its slot as a Plan or as an AoE finisher.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **`Shrink` says "your **Attacks** deal 30% less damage" and it reduced
   Kurage's Oath, which is printed `cost 1, skill`, from 3 to 2.** The Weak
   glossary on the same screen explicitly says "a Skill's damage too"; Shrink's
   does not, and behaves as if it did. Either the text or the behaviour is wrong.
2. **A card's face does not show Vulnerable.** Undertow read `Deal 10 damage`
   against a Vulnerable, Poisoned Fogmog and delivered 15. The face *does*
   recompute for Shrink, for Frail, and for its own debuff clause (7 → 10), so
   the one multiplier it silently omits is the one the player just applied
   himself. I only caught it by differencing HP.
3. **`Electro-Charged` is never called Poison, and Poison is what it applies.**
   The preview says "the reacted enemy loses 4 HP at the start of its turn, 1
   less each turn"; the body then wears `Poison 4`. Two names, one thing.
4. **The reaction that looks like it did not happen.** A Cryo hit onto a Hydro
   aura left the enemy showing `Frozen 1` *and* `Hydro Aura 2`, because Frozen is
   a debuff, the debuff fires Tamakushi Casket, and the Casket's hit is Hydro.
   The `Elemental Reaction` glossary predicts exactly this in a 200-word
   paragraph shouting in capitals. **It is right, it saved me, and the fact that
   it needs 200 words is itself the finding.**
5. **Leaf Slime announced five Status cards and I never saw one.** The pile
   counts rose; no Status card was ever printed in a hand I read.
6. **Kurage's Oath refuses `on "A"`** with no marker on its face that it aims
   itself.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** `Read the Field`. Both halves are block, block is the one
  resource I can size exactly from the intent line, and its Plan half asks me to
  guess a turn early for no upside.
- **Happiest to draw:** `Undertow`, once the relic was running — the face just
  told me it was a 10 and it was frequently a 15. But the card I was happiest to
  *have*, which is different, is **Vanguard**: 0 cost, applies Vulnerable, the
  relic turns that into damage, the Vulnerable then multiplies the relic's own
  hit, and it once killed a body outright at 0 energy.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a small one.** The opening hand held Ambush, printed
`Deal 5 damage. Plan: Deal 12 damage.`, against a 57-HP body telegraphing
`Attack for 4`. Play-now against plan-for-12 with block worthless is a real
question that the card answers on its own face without arithmetic. It is the
right first lesson. It is also not a *hard* question — the enemy's 4-damage
intent removes the only reason to want the smaller number sooner — so turn one
teaches the mechanic rather than testing it.

---

## Extra logging asks

**(1) Plans written per turn.** F1: T1 **Ambush**; T2 none; T3 none; T4 none.
F2: T1 **Battle Plan**; T2 **Kurage's Oath, Kurage's Oath**; T3 none.
F3: T1 **Battle Plan**; T2 **Ambush**; T3 none.
F4: T1 none; T2 none; T3 **Battle Plan**; T4 none.
F5 (Elite): T1 **Feigned Retreat**; T2 none; T3 none.
F6: T1 **Ambush**; T2 none; T3 none.
Total: 8 Plans across 20 turns, in 6 fights. Only **one** morning ever held more
than one.

**(2) Mornings with two or more carry-outs.** Exactly one: **fight 2, turn 3** —
`Kurage's Oath, 7` then `Kurage's Oath, 7`, resolved in the order written, front
first, 7 HP lost under each. **The order did not matter**: identical cards,
identical target, and the sum (14) was the same either way. I never reached a
morning where order could have mattered, so the "front first" rule went
untested by me. Worth saying: with 3 energy and Plans costing full price, two
Plans in a morning takes either a 4-energy turn or a turn spent doing nothing
else — I only managed it once in six fights.

**(3) A face showing different numbers on its own line and its Plan line after
an enchantment or buff.** Yes, and it is the run's headline.
Under `Shrink -1` (fight 2, turn 2) — **Kurage's Oath** read
`Deal 2 damage to ALL enemies. Plan: Deal 7 damage to ALL enemies.` (unshrunk
base was 3). **Ambush** read `Deal 3 damage. Plan: Deal 12 damage.` (base 5).
**Strike**, which has no Plan line, read `Deal 4 damage` (base 6).
*What each delivered:* the played Oath dealt **2**; the two planned Oaths dealt
**7 each**, confirmed by `Shrinker Beetle lost 7 HP` twice. The played Strike
dealt **4**. So the shrunk number and the unshrunk Plan number on one face were
both true, and the Plan glossary's *"no damage term of yours does"* is the line
that explains it.
A second, different mismatch, and this one is **not** self-explaining:
**Undertow** (fight 6, turn 2) showed `Deal 10 damage` on a Vulnerable enemy and
**delivered 15**. The face recomputes for its own debuff clause and for Shrink
and Frail, but not for Vulnerable.
Under `Frail 2` (fight 4, turn 2): **Defend** read `Gain 3 Block` (base 5) and
**Defend+** read `Gain 6 Block` (base 8) — both delivered what they printed.

**(4) First turn of every fight — what the screen said about the jellyfish
before I had played anything.** Identically, all six times: the buff line
`Bake Kurage 1 (buff) — Enemies cannot target it. Lasts all combat. Play a Plan
card on it: it carries out the Plan at the start of your next turn.`, the three
targeting rules, and **`Nothing is planned. The morning is empty.`** It never
carried anything over from the previous fight and it never varied by enemy, by
act, or by what was in my hand. Six identical readings: the block is correct and
it is also, after the second fight, furniture — I stopped reading it, and the one
line on it I did keep re-reading (*"A Plan with one target hits the front enemy
and never a Minion"*) only mattered once, in fight 4.

---

## Non-blindness declaration

Commands run outside the two allowed ones, all through the Bash tool, all for
scratch or for trimming output:

- `mkdir -p "…/review/qa/kokomi-round-22-2026-09-06"` — once, to create the
  directory for this file.
- `… blindplay observe 2>&1 | sed -n '<range>p'` and
  `… | sed -n '/<marker>/,/<marker>/p'` — many times, to re-read one block of an
  `observe` I had just run (hand, enemies, the Bake-Kurage block) instead of
  reprinting the whole screen.
- `… blindplay observe 2>&1 | grep -A5 "^- \*\*Nibbit"` and
  `… | grep -E "^- \*\*|^    [A-Z]"` — same purpose, filtering an `observe`.
- `echo "=== … ==="` between piped `observe` calls, as separators only.
- `cd "C:/Users/Monty/Documents/GitHub/GItS"` as the prefix of every call.

Tools used: **Bash** (as above, plus every `observe` / `act`), **Read** (once,
for my own brief at
`…\scratchpad\brief-kokomi-l1.md`, which the brief designates as the
instrument), **Write** (once, for this file).

I ran no `harness state`, no `scenario`, no `staged_turn`, no `soak`, and no
other understudy subcommand.

**Repo files read: none.**
