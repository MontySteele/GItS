# Blind seat — KLEEMOD-FURINA, lane 2, act 1

## Identity

- **Model / seat:** Opus (Claude), blind TESTER seat. Lane 2.
- **Run seed:** `1A3S4GK2ELEL` (read back off the wire by the embark).
- **Character:** Furina.
- **Ascension the run opened at:** 2.
- **Act:** 1. The map named the act top as **Waterfall Giant** (boss, 16 floors ahead at the first map screen).
- **Actions accepted:** 120 `act` calls, 0 refused, 0 stalls.
- **Termination reason:** the **action budget** (120/120). I stopped mid-turn on round 4 of the floor-11 elite. Wall clock was nowhere near 5400 s.
- **Floor reached:** 11 (elite, `Skulking Colony`, left alive at 7/75 while I stood at 25/84).
- **HP trajectory:** opened the first fight at **62/78**; 58 → 52 → 50 → 49 → 43 → 40 → **34/84** (max HP went 78 → 84 on the Bloody Ink event) → rested to 59 → healed to 69 → 60 → 51 → 39 → **25/84** at the cap.
- **Gold:** the bridge **never printed a running gold total** on any screen — not the map, not the shop-adjacent screens, not rewards. I can only report gains: 16 + 16 + 13 + 14 + 16 + 60 (stolen-back) = 135 collected, less an unknown amount taken by the Gremlin Merc's `Thievery 20`, less 0 spent (I never reached the shop). I could not check affordability at the `Waterlogged Scriptorium` event, which asked for 55 or 99 Gold, except by inference.
- **Potions held:** 1 — **Power Potion** (never used; I held it for a shop/elite emergency and the action budget ran out first). A second Power Potion was offered at floor 10 and I declined it to save an `act`.
- **Relics at the end:** Ethereal Spotlight (starting), Lead Paperweight (Neow), Vajra (floor-9 chest).
- **Deck at the end:** *the tool never printed a deck list on any screen and I did not go looking for one*, so this is assembled from the cards I saw in hand plus everything I added. Starter cards seen: `Soloist's Solicitation` (≥2 copies), `Stage Presence` (≥2), `Salon Début`, `Aria of Recompense`, `An Invitation`, `Regal Bearing`, `Charlotte — First-Person Shutter`, `Neuvillette — Sourcewater Droplets`. Added: `Seeker Strike` (Neow/Lead Paperweight), `Chevreuse — Ring of Bursting Grenades`, `Suffering for Art`, `Dahlia — Sacramental Shower`, `Charlotte — Framing: Freezing Point Composition`, a second `Chevreuse — Interdiction Fire` (a first copy was already in the starter deck). Plus one unplayable `Spoils Map` quest card and five `Dazed` statuses shovelled in by the Haunted Ship (Ethereal, so they self-clear).

**Neow pick: Lead Paperweight** — of the three, Kaleidoscope adds *two* off-character cards and Cursed Pearl adds a curse, so Lead Paperweight was the smallest dilution of a kit I was there to read. Off it I took **Seeker Strike** over **Restlessness**, because Restlessness's "if your Hand is empty" clause looked close to never true and Seeker Strike's "choose 1 of 3 cards in your Draw Pile" doubled as a way to *see* kit cards I had not met yet.

---

## Fight 1 — Corpse Slug (1) 25/25 and Corpse Slug (2) 27/27

Both wore `Ravenous 4 — When an enemy dies, Corpse Slug immediately eats it, becoming Stunned and gaining 4 Strength.`

**Round 1** (3 energy, HP 62/78, Encore 0).
Opening hand: Ethereal Spotlight (marked `CANNOT BE PLAYED: you have no Encore, and this costs 2`), Soloist's Solicitation, Regal Bearing, An Invitation, Charlotte — First-Person Shutter, Salon Début.

- Played **An Invitation** (0) first, purely for information — a free look at a random Common Companion before I committed energy. It gave `Neuvillette — Sourcewater Droplets`. *Rejected:* opening with Soloist's, which would have spent energy before I knew what my hand actually was.
- Played **Salon Début** (1). The Salon glossary said "A Companion card you play performs the front member", so a member on stage turns every later Companion card into two effects; that made the deploy worth more than 6 damage. *Rejected:* Soloist's Solicitation for a flat 6 — more damage right now, no engine.
  Outcome, printed verbatim: `Crabaletta hit Corpse Slug (1) for 4 Hydro, and it is wearing a Hydro aura (dry: it could not pay its Encore, so it acted at three-quarters).` The "dry" annotation is the single best piece of text in the kit — it told me the mechanic, the reason, and the size of the penalty in one clause.
- Played **Neuvillette — Sourcewater Droplets** (1) for 4 Block, and it performed Crabaletta again for another 4.
- Played **Regal Bearing** (1) on Slug (1) for 3 Block + 1 Weak, dropping its printed intent from 8 to 6 on the screen. *Rejected:* Charlotte — First-Person Shutter (4 now + 4 next turn), because 7 total block plus the Weak made this turn exactly damage-free and the Weak was visible on the intent immediately.
- Ended turn on 7 Block against a weakened 6. Took 0.

**Round 2** (HP 62/78, Frail 2 applied, draw pile down to 1).
- Played **Aria of Recompense** (1) → `Gain 5 Encore. If you have at least 6 Fanfare, gain 5 more.` Fanfare was 3, so no bonus. This was the first card that explained where Encore comes from. *Rejected:* Stage Presence for block; Encore is both fuel and a damage layer, so it strictly dominated a one-shot block when I had a member waiting to be fed.
- Played **Chevreuse — Interdiction Fire** (1) into Slug (1)'s Hydro aura for the Vaporize. Slug (1) went 17 → 1: 10 from the vaporized 7, then `Crabaletta hit Corpse Slug (1) for 6 Hydro` off the Companion trigger — and the Hydro aura showed **2** again afterwards, exactly the case the on-screen Elemental Reaction glossary warns about ("the aura is consumed and RE-APPLIED inside the same beat, so no screen ever shows it gone"). The text predicted its own confusing case correctly; that is rare and it worked.
- Played **Seeker Strike** (1) into Slug (2) for 9. Its "choose 1 of 3 cards in your Draw Pile" **silently auto-resolved with no selection screen** (draw pile was 1) and dropped a second Stage Presence into hand. *Rejected:* killing Slug (1) here, because Ravenous would hand the survivor +4 Strength and I wanted the 1-HP slug parked as a corpse-on-demand.
- Played **Ethereal Spotlight** (0, −2 Encore) to test whether the buff persisted. It did: `Guest Cast 1 — Companion cards are Spotlighted: 50% stronger printed damage and Block. Lasts until the Spotlight moves.` Cost: 2 fewer points of damage absorption, so 4 HP instead of 2 at end of turn. *Rejected:* holding the Encore as a shield — I traded 2 HP for the read, and would make the same trade again.

**Round 3** (HP 58/78).
- Played **Soloist's Solicitation** on Slug (1) to kill it deliberately. This is the turn's real decision: killing it hands Slug (2) `Strength 4` forever but Stuns it for a full turn, and removes a 3×2 attacker permanently. I judged the stun plus the removed attacker worth +4 Strength on a body already at 18 HP. *Rejected:* leaving Slug (1) at 1 HP and grinding Slug (2) down first, which avoids the Strength but eats 6 damage a turn from the corpse-to-be.
- Played **Salon Début** (1) to field a second member. The status line moved to `Salon Member 2`. **Here the screen and the outcome disagreed:** `Guest Cast 1` was active and claims Companions are "50% stronger", yet the log printed `Crabaletta hit Corpse Slug for 4 Hydro ... (dry ...)` — 6 × 0.75, with no 1.5× anywhere. Reading the Spotlight card again, it says "Spotlight every **Companion card**", and a Salon member is not a card; but the relic that hands you the card says "It does nothing once your **Companions** are lit", and the salon members are the things the game calls Companions everywhere else. I could not tell from the screens whether that was a bug or my misreading, and that is the point.
- One energy left and a Stunned enemy: block was worthless, Weak was worthless. **No rejected alternative — this turn presented no decision at the end.** Ended turn.

**Round 4** — Seeker Strike (9) + Soloist's Solicitation (6) into a 14-HP Slug. Lethal arithmetic, nothing to weigh. *Rejected:* the Neuvillette/Charlotte defensive line, which is only correct if you cannot kill.

Won at 58/78. Rewards: 16 Gold, and I took **Chevreuse — Ring of Bursting Grenades** (2, `Deal 10 damage to ALL enemies`, Pyro) over Duet, Double Time and a second An Invitation — a Companion card that is *also* AoE *also* a Pyro trigger for my own Hydro auras is three of the kit's four systems on one card.

---

## Fight 2 — Toadpole (1) 23/23, Toadpole (2) 22/22

**Round 1.** Noted first: `Guest Cast` and Encore had both **reset between fights**. Nothing on the previous screens said they were combat-scoped, and nothing on this screen said it either; I inferred it from their absence.

- **An Invitation** (0) → `Chevreuse — Vanguard's Valor` (0, next Attack +3, +3 more if a Reaction triggered this turn).
- **Aria of Recompense** (1) → 5 Encore, *then* **Salon Début** (1). Order was the whole decision: deploying after Aria meant `Crabaletta hit Toadpole (2) for 6 Hydro` at full strength instead of the 4 it does dry. *Rejected:* Salon Début first, which is the natural reading order of the hand and is 2 damage worse.
- **Chevreuse — Vanguard's Valor** (0) for +3 on the next attack, and it performed Crabaletta a second time — *which hit **Toadpole (1)**, not the target I was building toward*. **Member targeting is not controllable, not previewed, and not mentioned on any card.** That is the sharpest edge in the kit: the whole "Companion card performs a member" engine has a randomised output the cards never disclose.
- **Seeker Strike** (1) on Toadpole (2) for 9+3 = 12. This time the "choose 1 of 3" **did** open a selection screen, and it was excellent — each option carried `*Reaction preview: Vaporize* — Pyro meets Hydro: this hit deals 1.5x damage and consumes the aura`. I took `Chevreuse — Interdiction Fire`. *Rejected:* `Stage Presence` (which the screen now printed as `Gain 6 Block`, revealing that the "4" I had been reading in fight 1 was 6 with Frail already folded in).
- **Ethereal Spotlight** (0, −2 Encore) again, for 2 HP, to have Ring of Bursting Grenades lit next turn. *Rejected:* banking the Encore, worth 2 HP; the Spotlight was worth 5 damage.

**Round 2.** The payoff and the best legibility moment of the run: `Chevreuse — Ring of Bursting Grenades — Deal **15** damage to ALL enemies` — **the card rewrote its own printed number** under Spotlight. 15 Pyro onto two Hydro auras = Vaporize on both, and the fight ended in one card. *Rejected:* Stage Presence/Regal Bearing/Charlotte, all block, all irrelevant against a board I could clear.

Won at 52/78, round 2. Took **Suffering for Art** (0, `Lose 1 HP. Gain 3 Encore.`) over Stagehands, Commanding Gaze and a Charlotte. Encore had been the binding constraint in both fights — every member performance so far had gone off "dry" at three-quarters at least once.

*On the reward screen:* `Stagehands — Whenever a Salon Member takes its final bow, gain 5 Block. Whenever a Salon Member takes its final bow, gain 2 Encore.` The same trigger clause is printed twice instead of once with two effects, and **"takes its final bow" appears nowhere else in the kit's vocabulary** — Evoke is the word every other screen uses. I skipped it partly because I could not be sure the two clauses were one trigger or two.

---

## Fight 3 — Seapunk 44/44 (attacks for 11)

**Round 1 — the turn the kit is actually about.** Four cards, one order, 32 of the enemy's 44 HP:

- **Suffering for Art** (0) → Encore 3.
- **Ethereal Spotlight** (0) → −2 Encore, Guest Cast up.
- **Salon Début** (1) → `Crabaletta hit Seapunk for 6 Hydro` at full price (the last Encore paid for it), **and left a Hydro aura**.
- **Chevreuse — Ring of Bursting Grenades** (2) → 15 Pyro into that fresh Hydro aura = Vaporize, then a second `Crabaletta hit Seapunk for 4 Hydro (dry ...)` off the Companion trigger.

44 → 12. I had predicted "about 32" off the printed text before playing a card, and got exactly 32. *Rejected:* the same four cards in the obvious order (Grenades before Salon Début), which is ~10 damage worse because there is no aura for the Pyro to eat; and the Aria/Stage Presence defensive line, which is ~5 damage a turn and loses the race.

**Round 2** — Soloist's Solicitation ×2 = 12 into a 12-HP body. Lethal arithmetic, no decision. *Rejected:* Seeker Strike, only because its selection screen costs an extra action and 6+6 already killed.

Won at 49/78 → the fight cost 11 HP total. Took **Dahlia — Sacramental Shower** over Grand Salon, The House Holds Its Breath and Compose Herself: another Companion card, i.e. another member trigger, and a Hydro applicator to set up the Pyro cards.

---

## Fight 4 — Haunted Ship 63/63

**Round 1** (intent: Debuff *and* "give you 5 Status cards"; no attack).

- **Suffering for Art**, **Ethereal Spotlight**, **Dahlia — Sacramental Shower** (stored 9 Hydro for the next enemy attack), **Soloist's Solicitation**, **Charlotte — First-Person Shutter**. *Rejected:* Stage Presence — against a turn with no attack in the intent, straight block is dead, whereas Charlotte's delayed half survives into a turn that does have one.
- **Screen/outcome disagreement:** Charlotte's card text under an active Spotlight read `Gain 4 Block. At the start of your next turn, gain 4 Block.` It delivered 6 Block and a `Block Next Turn 6` buff. The Spotlight rewrites the *first* number of a two-clause card but not the second, so the card under-reports itself. Compare Ring of Bursting Grenades, which rewrites cleanly — the behaviour is inconsistent between cards.
- Same class of thing on Dahlia: the buff line printed `Sacramental Shower 1 — The next time an enemy attacks you, deal **9** Hydro damage to it first`, and when it fired the ship went 38 → 32, i.e. **6**. I was carrying `Weak 2`. Card text on this kit folds Weak into the printed number reliably and well (`Seeker Strike — Deal 6 damage` while Weak, `Deal 10` later with Strength and no Weak); the *stored-buff* text does not. If you are going to fold modifiers into printed numbers — and you should, it's very good — the buff readouts have to do it too, or the one place that doesn't becomes the place you get killed.

**Round 2.** Aria (Encore 6) → Salon Début (Crabaletta 6, Hydro aura) → Chevreuse — Interdiction Fire (Vaporize ~11, plus a second Crabaletta 6). 57 → 38. *Rejected:* An Invitation, because a companion card added at 0 energy just gets discarded at end of turn — An Invitation is only worth playing at the *top* of a turn you can still pay for.

**Round 3.** Ring of Bursting Grenades into the standing Hydro aura (Vaporize) plus a member performance, 32 → 13. Then a real coin-flip: **Regal Bearing** (3 Block + 1 Weak) versus **Stage Presence** (6 Block) against a 4×3 = 12 intent. They are *arithmetically identical* — 12 × 0.75 − 3 = 6, and 12 − 6 = 6. I took Stage Presence. A pair of cards that are exactly equal against the intent on screen is a non-decision dressed as a decision.

**Round 4.** Interdiction Fire alone (Vaporize 10 + a dry Crabaletta 4) into 13 HP. Lethal, no decision.

Won at 34/84. Took **Charlotte — Framing: Freezing Point Composition** (Cryo) over Curtain Cue, Fortissimo Guard and The House Holds Its Breath — a Cryo Companion card turns my Pyro cards into Melt (1.75×) instead of Vaporize (1.5×).

*On that reward screen:* `Curtain Cue — If you moved the Spotlight this turn: gain 3 Encore and draw 1 card.` **"Moved the Spotlight" is never defined.** The Ethereal Spotlight card says "Spotlight every Companion card"; the buff says "Lasts until the Spotlight moves"; and once it is up, the card is refused with `CANNOT BE PLAYED: the Spotlight is already on your Companion cards`. So from the screens alone I could not tell whether moving it is possible more than once per fight, and I could not price Curtain Cue at all.

Floors 6–9: `The Legends Were True` (took the Spoils Map over losing 8 HP at 34/84), a **rest** (heal 25 → 59/84; rejected Smith, because at 40% HP with an elite two floors out the upgrade is the wrong currency), `Abyssal Baths` (Abstain, heal 10; rejected +2 Max HP for 3 damage — a net −1 at that HP), and a chest: **Vajra**, +1 Strength each combat.

---

## Fight 5 — Gremlin Merc 49/49 (`Surprise 1 — Something is off about this creature...`, `Thievery 20`)

**Round 1.** Vajra's Strength was folded into every printed number immediately and correctly (Soloist's 6→7, Interdiction Fire 7→8, Ring 10→11, Framing 4→5). Good.

- **Charlotte — Framing** (Cryo, 5) then **Chevreuse — Interdiction Fire** (Pyro into Cryo = **Melt**, 8 × 1.75 = 14). 49 → 30. *Rejected:* Ring of Bursting Grenades + Interdiction Fire, which is more printed damage (19 vs 13) and less real damage, because two Pyro cards in a row react with nothing. Choosing the *order of elements* is the most interesting recurring decision in this kit.
- **Aria of Recompense** with the last energy, over Stage Presence's 6 Block: 5 Encore absorbs 5 now *and* survives the turn *and* can light the Spotlight later; 6 Block is 6 Block. *Rejected:* Soloist's for 7 damage, which loses 5 HP to gain 7 damage on a body I could not kill this turn either way.

**Round 2.** An Invitation → `Shinobu — Sanctifying Ring` (Electro, 4 to all + 4 Block). Real choice: **Shinobu + Dahlia** sets up an Electro-Charged when Dahlia's stored Hydro fires on the enemy's turn, versus **Soloist's + Dahlia + Charlotte** for 16 straight damage and 4 block. I took the damage line — 30 → 13 — because Electro-Charged prints as a 4-HP-a-turn decay against a body I expected to be dead first. *Rejected, and I think correctly.*

**Round 3.** Suffering for Art → Salon Début (`Crabaletta hit Gremlin Merc for 6 Hydro`) → Seeker Strike. Arithmetic said 13 − 6 − 7 = 0. **The screen and the outcome disagreed: it lived on 1 HP.** Seeker Strike printed `Deal 7 damage` and delivered 6. I was carrying Weak 2 and Strength 1, so the printed 7 and the applied 6 are two different roundings of the same 9→10→×0.75. A one-point discrepancy is small; a one-point discrepancy *on the number the card prints* is exactly the kind that makes you misjudge a lethal.
- Stage Presence for 6 block over the 8-damage intent, because there was no attack left in hand to finish the job.

**Round 4.** Charlotte — Framing for 3 into 1 HP. The Merc's `Surprise` fired: it **split into Sneaky Gremlin 8/13 and Fat Gremlin 13/13 (`Heist 60 — When killed, returns all the stolen Gold`)**, both Stunned. One **Ring of Bursting Grenades** — 8 to all, Vaporized on the Sneaky one which still wore my Hydro aura, plus a Crabaletta performance — cleared both. *Rejected:* single-targeting the Fat Gremlin for the 60 gold first; the AoE got both anyway.

Won at 51/84. Took a second **Chevreuse — Interdiction Fire** over Stage Lights, Blocking Notes and Lasting Impression.

*On that reward screen:* `Blocking Notes — Gain 5 Block, already including Companions. *Companion scaling* — +2 Block per Companion card you have played this turn, **including Guest Stars**.` "Guest Stars" is a third undefined term, alongside "takes its final bow" and "moved the Spotlight". The kit has at least three names for things I could not attach to anything I had seen.

---

## Fight 6 (unfinished) — Skulking Colony 75/75, elite, floor 11

`Hardened Shell 20 — Skulking Colony cannot lose more than 20 HP each turn.` A cap on burst is a genuinely good foil for this kit, because the kit's whole shape is one enormous reaction turn; it forced me to *stop adding damage*, which is a decision I had not had to make once in five fights.

**Round 1.** Suffering for Art → Ring of Bursting Grenades (11 Pyro) → Dahlia — Sacramental Shower (9 stored Hydro, which would land on the *enemy's* turn into the Pyro aura I had just applied = Vaporize). 75 → 49, i.e. 26, split 11 on my turn and 15 on theirs — the cap held on each side of the turn boundary, but nothing on screen says which side of that line the cap counts, and I only learned it by watching. *Rejected:* the Spotlight line (Ring at 16), because with a 20/turn cap the Spotlight's +5 is pure waste and the 2 Encore is worth more as absorption. **This is the first time in the run the Spotlight was the wrong play, and working that out was the most interesting thirty seconds of the round.**

**Round 2.** Framing (Cryo, 5) → Interdiction Fire (**Melt**, 14) = 19, one under the cap. 49 → 30. *Rejected:* adding Soloist's Solicitation for a third attack — it would have contributed exactly 1 damage against the cap and cost an action; declining to play a playable card was the right move and the screen gave me everything I needed to see it.

**Round 3.** Aria (5 Encore) → Interdiction Fire (8) → Stage Presence (6 Block). Took 0 from the 9-damage intent. 30 → 22.

**Round 4, cut off by the action budget.** Interdiction Fire (8) + Soloist's Solicitation (7) → **7/75**. I stopped there on action 120 without ending the turn, holding 25/84, 2 Encore, 1 energy, an unused Power Potion, and a 9×2 intent on the board that had just gained `Strength 2`.

One last mismatch, on that final screen: `**Hardened Shell 5** (buff) — Skulking Colony cannot lose more than **20** HP each turn.` The badge number counts down as the remaining allowance; the sentence keeps saying 20. The number and the words on the same line describe different things.

---

## The kit, after 6 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Three, and they are good ones.

1. **Element order.** Every turn with two elemental cards in hand is a genuine ordering puzzle: Cryo-then-Pyro is Melt at 1.75×, Pyro-then-Cryo is the same two cards for 40% less. Hydro from a Salon member sets up Vaporize for free, so "deploy, then burn" beats "burn, then deploy" by about ten damage. This decision recurs, it is legible from the printed text, and the on-screen reaction glossary plus the `*Reaction preview: Vaporize*` on selection screens make it *learnable* rather than guessable. It is the best thing in the kit.
2. **Encore as two resources at once.** Encore pays members to perform at full instead of three-quarters, pays 2 to light the Spotlight, *and* sits behind Block as a damage layer. So "spend 2 to light the Spotlight" is always literally "take 2 more damage this turn for +50% Companion numbers", and the answer genuinely changes — it was right in fights 1–3, and wrong against the elite's damage cap. That is a good resource.
3. **The Ravenous kill-order decision** in fight 1 — kill the 1-HP slug to Stun the survivor and eat +4 Strength forever, or leave it parked. That one came from the enemy, not the kit, but the kit's Encore-as-shield made it a live calculation rather than a reflex.

**(b) What felt automatic, and what never seemed worth playing.**

Automatic: **`Aria of Recompense` → `Salon Début` in that order**, every single fight, because deploying dry costs 25% of the member's output and there is never a reason to prefer it. **`Suffering for Art` at 0 cost** is auto-play at any HP above about 15. And **`Ethereal Spotlight` was auto-play for five fights straight** — the relic hands you a free copy every turn, so the only question is whether you have 2 Encore, and the answer is yes as soon as you have played Aria once. It stopped being automatic exactly once, against the damage cap, and that was the only time it was interesting.

Never worth playing: **`Regal Bearing`** — I played it once, in round 1 of fight 1, and never again; against a 12-damage intent it is arithmetically *identical* to `Stage Presence`, and against anything bigger it is worse. **`Stage Presence`** itself is filler: 6 Block on a character whose Encore already absorbs damage and whose block cards mostly come stapled to Companions. And **`An Invitation`** is a trap at the bottom of a turn — the card it fetches gets discarded unplayed — but nothing on it says so.

**(c) What I could not understand, or that contradicted its own printed text.**

- **The Spotlight does not buff Salon members, but the relic implies it does.** `Ethereal Spotlight` says "Spotlight every **Companion card**"; `Guest Cast` says "**Companion cards** are Spotlighted"; the relic says "It does nothing once your **Companions** are lit." Salon members are the things the whole kit calls Companions. With Guest Cast up, `Crabaletta hit ... for 4 Hydro (dry...)` — 6 × 0.75, no 1.5× anywhere. Either it is a bug or "Companion card" and "Companion" are two different nouns that look identical. I could not resolve it from the screens.
- **Member targeting is invisible.** A Companion card performs the front member, and the member hits *something* — in fight 2 it hit the enemy I was not attacking, splitting damage across two Toadpoles when I wanted one dead. No card, keyword or glossary entry says how a member picks a target.
- **Three undefined terms**: "takes its final bow" (Stagehands), "moved the Spotlight" (Curtain Cue), "Guest Stars" (Blocking Notes). Each one sat on a card I had to price at a reward screen, and each one I declined partly because I could not price it.
- **Fanfare does nothing I could observe.** Its own buff says "Cards read it and none spends it", the status line says "no maximum, and no rule for how it is spent", it decays 20% a turn, and across six fights it sat between 1 and 6. The two things that read it — `Aria of Recompense`'s "at least 6 Fanfare" and the Salon's "+1 per 10 Fanfare" — **never once triggered**. I finished the act unable to say what Fanfare is for, and it is on every screen.
- **Modifier-folding is inconsistent.** Card text folds Weak/Frail/Strength into the printed number, which is superb. Stored-buff text does not (`Sacramental Shower ... deal 9` delivered 6 under Weak). Spotlight rewrites a card's first clause but not its second (`Charlotte — First-Person Shutter` printed 4/4, delivered 6/6). And `Seeker Strike` printed 7 and delivered 6, which cost me a lethal.
- Smaller: the two Fanfare readouts on the same screen say different things about whether a rule exists for spending it; `Hardened Shell 5` prints "20" in its own sentence; and **no screen ever showed my gold or my deck**.

**(d) The card I never wanted to draw, and the one I was happiest to see.**

Never wanted: **`Regal Bearing`**. It is `Stage Presence` with extra reading and a rider that, against every intent I actually faced, bought exactly zero net damage.

Happiest: **`Chevreuse — Ring of Bursting Grenades`**. It is a Companion card (so it performs a member), it is AoE, it is Pyro (so it eats the Hydro aura my own members leave behind), and it visibly rewrote its own printed number to 15 when the Spotlight was lit. It ended fight 2 by itself and cleared the Gremlin split by itself. Every system in the kit touches it.

**(e) Did the first turn of the first fight already present a decision?**

**Yes** — a real one, and a good one. With 3 energy against 8 incoming I had to choose between `Soloist's Solicitation` for a flat 6 and `Salon Début` for ~4 now plus a standing member that turns every later Companion card into two effects. The Salon glossary printed on that first screen gave me enough to reason about it ("A Companion card you play performs the front member"), and the "dry: it could not pay its Encore, so it acted at three-quarters" annotation on the result told me *immediately* what I had got wrong. That is a first turn that teaches. The caveat is that by fight 3 that same decision had collapsed into a fixed opening sequence — Suffering → Spotlight → Salon Début → biggest Pyro card — that I played identically three fights running.

---

## Non-blindness declaration

**Repo files read: none.**

Commands run outside `blindplay observe` / `blindplay act`:

- `python -m understudy.embark --character KLEEMOD-FURINA --lane 2` — once, as the coordinator instructed.
- `mkdir -p review/qa/furina-reframe-round-6-2026-09-04` and `mkdir -p <scratchpad>/lane2` — directory creation only. The scratchpad directory was created and never written to.
- Shell text-trimming on the output of `observe` only: `head`, `tail`, `sed -n`, `grep`, and one `for` loop that issued several `act` calls in sequence. These reshaped what the bridge printed to me; they read nothing else.

Tools used: **Bash** (all of the above), and **Write**, once, for this record. No Read, no Grep, no Glob, no Agent, no other understudy subcommand — no `harness state`, no `scenario`, no `staged_turn`, no `soak`.

My model family is **Opus (Claude)**. The kit under test was authored by a different Claude model, so this seat is not model-independent of its author, though it is blind to the author's work.
