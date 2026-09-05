# Blind seat record — KLEEMOD-KOKOMI, lane 2, round 16

## Identity

- Model and seat: Claude Opus, blind Opus seat, round 16
- Lane: 2
- Run seed: `31AYS93P0SNJ`
- Ascension: 3 (run opened at 64/80 HP after the Neow screen)
- Character: the Bake-Kurage / Plan kit (Kokomi). Starting relic **Tamakushi Casket** —
  "Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it
  deals 2 Hydro damage to that enemy."
- Act: 1. The map named the act's boss: **Soul Fysh**. I never reached it.
- Actions accepted: **120 of 120**
- Termination reason: **action budget**. The elite died on action 120 — the second of my
  last two acts — so the round ends on a won fight with the reward screen up and its
  33 gold / Dexterity Potion / Joss Paper / card unclaimed. Not a finding.
- HP trajectory: 64 (start) → 58 → 55 → 53 → 46 (event heal) → 72 → 66 → 66 (three fights
  and a rest with no further loss) → 55 → 46. **Final 46/80.**
- Gold: 99 after Neow, 112 after fight 1, 15 after the shop (spent 97), 41 at the elite.
  The elite's 33 gold was never claimed.
- Potions held at the end: **Energy Potion**, **Power Potion** (2 of 3 slots). Speed Potion
  spent on the elite.
- Relics at the end: **Tamakushi Casket**, **Lost Coffer**.
- Deck at the end (17 cards): Strike ×4, Defend ×4, Kurage's Oath, Slack Water,
  Cleansing Wave, Deep Current+ *(upgraded)*, Vanguard, War Council, Exposed Flank,
  Amber — Explosive Puppet, Kaeya — Glacial Waltz.

**Neow pick: Lost Coffer** ("Gain 1 card reward and procure 1 random Potion"). I took it
because a card reward is the only screen that shows me three of the kit's faces at once
and I had seen nothing but a relic line; Precise Scissors would have thinned a deck I
could not yet read, and Neow's Bones' curse is a cost I could not price blind.

Floors played: Neow → Monster (Seapunk) → Shop → Monster (Toadpoles ×2) → Unknown
(Spiraling Whirlpool) → Monster (Corpse Slugs ×2) → RestSite → Monster (Sewer Clam) →
Elite (Terror Eel). **Five fights, five won, zero deaths.**

---

## Fight 1 — Seapunk, HP 46/46

Opening screen: 3 energy, hand Kurage's Oath / Cleansing Wave / Strike / Defend / Strike.
Enemy intent 11.

**Turn 1.** Played `Kurage's Oath` **on Bake-Kurage** (writing its Plan: "Deal 7 damage to
ALL enemies"), then `Strike` on Seapunk, then `Defend`.
*Rejected:* playing Kurage's Oath now for 3 instead of planning it for 7 — a 4-damage gain
for a one-turn delay, which the screen states plainly ("Plan: Deal 7 damage to ALL
enemies"). Also rejected Strike + Strike + Defend (12 now, no Plan) — over two turns the
planned line is 13 and teaches me the mechanic.
The plan registered as its own status line: `Plan 1 (buff) — Carries out 1 Plan at the
start of your next turn, in order.` Took 6 (11 − 5 Block). This was a real decision, and
the arithmetic was fully readable off the printed faces.

**Turn 2.** Hand came up **Strike ×2, Defend ×3 — not one Plan card in it.** The signature
mechanic was simply unavailable, so the only question was how much to block.

Before playing it I probed the boundary: I asked `play "Strike (1)" on "Bake-Kurage"`.
The tool answered `"ok": true, "refusal": "", Took: Strike (1). ok Playing 'Strike'
targeting Bake-Kurage` and **charged me an action** — and nothing happened. Energy stayed
3/3, the discard pile stayed at 5, the hand still held both Strikes, and the Bake-Kurage
block still read "Nothing is planned. The morning is empty." A non-Plan card aimed at the
jellyfish is a silent no-op reported as a success. See the kit answers, (c).

Then `Strike`, `Strike`, `Defend`. *Rejected:* a third Defend (2 damage saved against
2×4 is not worth 6 damage). Seapunk 33 → 21; I took 3.

**Turn 3.** Enemy showed Empower + Defensive. Hand: Slack Water, Strike ×4.
Played `Slack Water` on Seapunk, then `Strike`, `Strike`.
*Rejected:* three Strikes, which is the same 18 damage — Slack Water's line is 4 damage
plus 1 Weak, and the Weak sets off Tamakushi Casket for 2 more, so 6 either way, with a
free debuff attached. Seapunk 21 → 3, exactly as the two printed numbers predict.
*Rejected:* planning Slack Water (Weak to ALL next turn) against a single enemy that was
about to block.

**Turn 4.** Seapunk at 3 HP behind **7 Block**, Strength 1, intent 12. Hand: Cleansing
Wave, Kurage's Oath, Defend ×3.
Played `Kurage's Oath` **on Bake-Kurage**, `Defend`, `Defend`, end turn.
*Rejected:* playing Kurage's Oath now — its 3 damage would vanish entirely into 7 Block,
whereas the planned 7 lands at the start of my next turn, after the block is gone.
*Rejected:* a third Defend (15 block against a 12 attack is 3 wasted, and it forfeits the
kill). This was the best turn of the fight: the block wall made "now vs next turn" a real
question with a right answer I could compute.

The plan killed it. The tool printed a dedicated block for this, which I thought was well
judged: *"The fight is over. This is the last thing the Bake-Kurage carried out in it —
printed here because a Plan whose kill ends a fight never reaches a battle screen."*
`Bake-Kurage: Kurage's Oath, 7 — the 7 is damage. Seapunk lost 3 HP, and died.`

Rewards: 13 gold, Energy Potion, card. Card choice was Stolen Chapter / Moon's Reflection /
Chain of Command / **Amber — Explosive Puppet**. Took Amber: 8 Pyro to ALL plus 3
mitigation for 1 energy, and it is the only thing on the screen that puts a *second*
element into the run — every glossary block up to that point had said "NO REACTION IS
REACHABLE HERE: Hydro is the only element this screen can supply."
*Rejected:* Moon's Reflection (my exhaust pile is empty, so it is a blank card), Chain of
Command (0 Companions in deck = 0 damage), Stolen Chapter (draw with nothing to draw into).

### Shop, floor 2 (112 gold)

Bought **Deep Current** (49) and **Vanguard** (48), leaving 15.
*Rejected:* Chain of Command at 72 with one Companion in deck (3 damage); Kamisato Ayaka
at 146 (unaffordable); Card Removal at 75 (most of my gold for one Strike); Song of Pearls
at 37 (3 Block per carry-out, and my Plan density was one or two a fight).

One shop line I could not read: **Undertow — "Deal 7 damage, already including 3 if the
enemy has a debuff."** On a screen with no enemy on it, I cannot tell whether that card
deals 4 or 7, and "already including" implies a conditional that has already been folded
into a number I am being shown out of context. I did not buy it, partly for that reason.

## Fight 2 — Toadpole (1) HP 23/23, Toadpole (2) HP 22/22

**Turn 1.** Intents: Empower on (1), 7 on (2). Hand: Strike ×2, Deep Current, Defend,
Cleansing Wave.
Played `Deep Current` (6 to ALL), then `Strike` and `Strike` both into **Toadpole (1)**.
*Rejected:* focusing Toadpole (2), which had 1 less HP and was the one actually attacking —
I took the buffer instead because an Empower that resolves twice compounds and a 7-damage
hit does not. *Rejected:* Defend over the second Strike (7 damage at 53 HP is cheap).
Toadpole (1) 23 → 5, Toadpole (2) 22 → 16, both wearing Hydro Aura 2. Took 7.

**Turn 2.** Toadpole (1) had bought **Thorns 2** off its Empower and was attacking 3×3;
Toadpole (2) was buffing. Hand: Defend ×2, Strike, **Amber — Explosive Puppet**,
Kurage's Oath.
Played `Amber — Explosive Puppet`, then `Kurage's Oath` **on Bake-Kurage**, then `Defend`.
*Rejected:* Striking Toadpole (1) — Thorns 2 charges me for the privilege, and Amber's
pending 8 AoE was already lethal to a 5-HP body for free. *Rejected:* a second Defend
over the planned Oath — Amber's 3 mitigation plus one Defend already covered the 9
incoming exactly.

This was the best turn the kit produced all round: three cards, three different reasons,
and the ordering mattered.

The fight ended inside the enemy turn and I never saw the numbers. From the arithmetic:
Amber's 8 Pyro killed Toadpole (1) at 5 HP, and Toadpole (2) went from 16 to 4 — **12
damage from a printed 8**, because both wore a Hydro aura. The screen never named the
reaction, never printed a multiplier, and never showed me an intermediate state; I
reconstructed ×1.5 from HP subtraction alone. The next fight confirmed it by printing
*"Reaction preview: Vaporize — Pyro meets Hydro: this hit deals 1.5x damage and consumes
the aura"* on the card face. **The preview exists; it just is not reachable on the turn
where the reaction is set up, only on turns where a card in hand can cause one.** So the
first Vaporize of my run was invisible and the second was well signposted.

The kill line also printed **"Toadpole lost 4 HP, and died"** — unnumbered, with two
Toadpoles in the fight. Everywhere else the screen is scrupulous about `(1)` / `(2)`.

Rewards: 11 gold, card. Took **Kaeya — Glacial Waltz** (6 Cryo to a random enemy at end of
turn for 3 turns, Exhaust) over Ripple, Cleansing Wave and Rally: 18 damage for 1 energy
is the best rate on the screen and it puts a third element in the deck.
*Rejected:* Ripple (0-cost, Plan gives 1 Energy + 4 Block — a genuine engine piece I would
take in a deck that had damage already).

### Event, floor 4 — Spiraling Whirlpool (HP 46/80)

Offered: **Observe** (enchant a basic Strike or Defend with Spiral → Replay 1, i.e. a
12-damage Strike) or **Drink** (heal 26). Took **Drink**.
*Rejected:* Observe. A Replay Strike is the stronger card, but at that point nothing in
the kit — not one card, relic, event or shop shelf — had shown me a single point of
healing, and 26 HP is a third of my bar. I would take Observe at high HP.

## Fight 3 — Corpse Slug (1) HP 27/27, Corpse Slug (2) HP 25/25

Both carried `Ravenous 4 — When an enemy dies, Corpse Slug immediately eats it, becoming
Stunned and gaining 4 Strength.` That one line turned kill *order* into the whole fight.

**Turn 1.** Played `Amber`, `Strike` into Slug (2), `Defend`.
*Rejected:* holding Amber for a turn when a Hydro aura would be up — no Hydro card was in
hand, so Amber could only be a flat 8-to-all, and 8-to-all now beats 12-to-all later
against a pair. Took 6.

**Turn 2.** Both slugs wore **Pyro Aura 1** from Amber, and every Hydro card in my hand
now printed *"Reaction preview: Vaporize."* Slug (1) 19 HP / 8 incoming; Slug (2) 11 HP /
debuff intent. Hand: Slack Water, Deep Current, Vanguard (0), Kurage's Oath, Strike.

I played it in an order chosen for the reactions, and the screen let me compute every
number in advance:
1. `Deep Current` — 6 to ALL, ×1.5 Vaporize = 9 each. **Predicted 10 and 2; screen showed
   10 and 2.** Auras consumed, both bare.
2. `Vanguard` on Slug (1) — 0 cost, applies Vulnerable; the Vulnerable then makes
   Tamakushi Casket's 2 Hydro land as 3. **Predicted 8; screen showed 7** — because the
   Vulnerable applies before the relic's own hit, so it was 2 × 1.5 = 3, not 2. My error,
   and the screen was right.
3. `Strike` on Slug (1) — 6 × 1.5 = 9 into 7 HP. Dead. Slug (2) ate it: Stunned, Strength 4,
   still 2 HP.
4. `Kurage's Oath` — 3 to ALL, kills the 2-HP body. Fight over on turn 2, no damage taken.

*Rejected, and this was the actual decision:* killing Slug (2) first. That is the obvious
line — it was at 2 HP after Deep Current — but it hands the 10-HP slug a Stun **and** 4
Strength and leaves it alive. Killing the healthy one first means the survivor is the
2-HP one, which the AoE mops up in the same turn. Ravenous made a two-slug fight into a
sequencing puzzle with a clean right answer. Best-designed enemy interaction I met.

One refusal here: `play "Kurage's Oath" on "Corpse Slug"` →
`error Card 'Kurage's Oath' cannot be played on 'Corpse Slug'`. Correct (it is an ALL
card), but the same output line first said **`Took: Kurage's Oath.`** and then errored, and
it consumed an action. Untargeted `play "Kurage's Oath"` worked.

Rewards: 7 gold, card. Took **War Council** (Weak to ALL; Plan: 5 damage and Weak to ALL)
over a second Vanguard, The Clouds Like Waves Rippling and Diona — Icy Paws: Weak to ALL
fires Tamakushi Casket once per enemy, so it is AoE damage and AoE defence on one card.

### Rest site, floor 6 (HP 66/80)

Took **Smith** over **Rest** — Rest heals 24 into a 14-point hole, so a third of it is
thrown away, and I was not under HP pressure. Upgraded **Deep Current** (6 to ALL → 9 to
ALL, my main attack and my Vaporize carrier).

**The upgrade screen prints only the card's current face.** Thirteen cards listed, not one
of them showing what upgrading would do. I picked Deep Current on a guess about what "+"
means and only learned it was 6 → 9 when I next drew it in combat. That is a choice made
blind by construction, not by my blindness rule.

## Fight 4 — Sewer Clam, HP 56/56, Block 8

`Plating 8 — At the end of your turn, gain 8 Block. Plating is reduced by 1 at the start
of your turn.` A regenerating wall that decays: the fight is explicitly a question of
whether your burst beats the block clock.

**Turn 1.** Played `War Council` (Weak to ALL; intent visibly fell 10 → 7, and the relic's
2 Hydro ate 2 block), `Kaeya — Glacial Waltz`, `Defend`.
*Rejected:* Strike + Strike — 12 damage into 8 block is 4 real damage, and against a 56-HP
body that regenerates 8 a turn, chip damage is the losing plan. Weak plus a 3-turn engine
was worth more than four points of HP.

**Turn 2.** The clam showed **Empower**, i.e. no attack — my burst window. Played
`Vanguard` (0, Vulnerable), then `Deep Current+` (9 × 1.5 = 13), `Strike` (9), `Kurage's
Oath` (4). 54 → 46 → 37 → 33, every step matching the printed numbers.
*Rejected:* any Defend (nothing incoming); *rejected:* planning Kurage's Oath, because the
Plan would arrive next turn against a fresh 8-block Plating layer, whereas played now it
rode the same Vulnerable and the same already-broken block pool.

This turn caught a contradiction in the printed text. The status line reads
**`Vulnerable 1 (debuff) — Receive 50% more damage from Attacks`**, but the glossary block
on the same screen reads **`Vulnerable — The wearer takes 50% more damage from every
hit.`** Kurage's Oath is a *skill*, and it dealt 4 (3 × 1.5), so the glossary is right and
the status line is wrong. I would have mis-sequenced if I had trusted the status line.

**Turn 3.** Clam 21 HP / 7 Block / Strength 4 / intent 14. Played `Slack Water` (Weak, so
14 → ~10) and two Defends (10 block). Took 0.
*Rejected:* Strike over Slack Water — 6 damage that dies in block versus a Weak that turns
a 14 into a 10 against exactly 10 block.

**Turn 4.** Clam buffing again. Three `Strike`s, 18 into 6 block → 12 through, clam to 2.
*Rejected:* Amber — the clam was not attacking, so Amber's trigger would idle a whole turn;
I banked it for the elite. *Rejected:* Defend (nothing incoming).

**Turn 5.** `Deep Current+` for 9 into 5 block and 2 HP. Dead.
**Fight taken at 66/80 → 66/80: zero HP lost across five turns.**

Rewards: 8 gold, Power Potion, card. Took **Exposed Flank** (1 Vulnerable; Plan: 2
Vulnerable to ALL) over Change of Plans, Moon's Reflection and Thoma — Blazing Barrier: a
*non-exhausting* Vulnerable that also fires the relic, where my Vanguard exhausts.

## Fight 5 (Elite) — Terror Eel, HP 140/140

`Shriek 70 (debuff) — The first time Terror Eel's HP reaches 70 or below, it becomes
Stunned.` A printed, readable threshold; it changed how I counted for three turns.

**Turn 1.** `Amber`, `Strike`, `Defend`. Took 8 (16 − 3 − 5).
*Rejected:* Amber + double Defend (take 3) — against 140 HP I could not afford a turn that
deals 6 total, and Amber's Pyro was worth more as an aura for my Hydro cards than as
mitigation.

**Turn 2.** Eel wearing Pyro Aura 1. Played in reaction order: `Deep Current+` first
(9 × 1.5 Vaporize = 13, consuming the aura), then `War Council` (Weak + relic 2, which
re-applies Hydro), then `Kaeya — Glacial Waltz`.
*Rejected:* Defend — 9 incoming at 58 HP is cheap and Kaeya's 18-over-3-turns was the best
damage rate on the board. 126 → 103.

**Turn 3.** Eel 103, intent 22. Played `Vanguard` (0) for Vulnerable, then `Slack Water`,
`Strike`, `Strike`. Predicted 3 + 6 + 3 + 9 + 9 = 30 → **73**. Screen: 73. Exactly.
*Rejected:* swapping a Strike for Cleansing Wave (5 block against 22 is a rounding error;
I wanted the Shriek threshold). I missed the 70 line by **3 damage** and could not find
the last 3 anywhere in hand — a genuinely tense turn, and the tension was legible.

**Turn 4.** Kaeya's end-of-turn Cryo pushed it to 61 *after* my turn, so **Shriek fired
anyway and the eel was Stunned** — its 22 never landed. Honest note: that was luck, not
read. The end-of-turn Cryo is not shown as a pending number anywhere, so I could not have
counted on it. Then, into a debuff intent: `Exposed Flank`, `Strike`, and `Kurage's Oath`
**planned**. *Rejected:* playing Oath now for 4 — Vulnerable falls off at the end of the
enemy's turn, so the Plan's 7 next turn still beats 3 × 1.5 now. *Rejected:* both Defends
(no attack incoming). 61 → 30 (relic 3 + Strike 9 + Cryo 12 + planned Oath 7 = 31).

**Turn 5.** Eel 30 HP, intent **33**, and nothing in hand could kill it. Used
`Speed Potion` (5 Dexterity), then `Defend`, `Defend`, `Cleansing Wave` — 5 + 5 + 5
becomes **30 Block** exactly.
*Rejected:* Energy Potion + Slack Water to add Weak and take 0 instead of 3 — two more
actions off a budget I could see running out, for three points of HP. This was the single
best-signposted decision of the run: the Dexterity glossary, the three block faces and
the intent number let me compute 30 before spending anything.

**Turn 6.** `Deep Current+`, `Strike`, `Strike` → eel to 9. *Rejected:* the Energy Potion
line (potion + 4 plays + end turn = exactly my last 6 actions, leaving the eel at 7 and
me unable to act again). Taking 9 damage instead bought me two spare actions on the
following turn.

**Turn 7, actions 119 and 120.** Eel at 9. `Strike` (6) + `Kurage's Oath` (3) = 9 exactly.
**The elite died on the last action of the budget.**

---

## The kit, after 5 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The Plan mechanic is the kit, and it is a good one, because it prices a card twice on the
same screen and the two prices are visibly different. "Kurage's Oath: 3 to ALL now / 7 to
ALL next turn" is a clean tempo-versus-total question, and the game keeps producing board
states where the answer flips. Fight 1 turn 4 — 3 HP behind 7 Block — was the moment it
clicked: playing the card *now* deals literally zero, and the Plan lands after the block
is gone. Fight 4 turn 2 was the mirror image: a Vulnerable window and a broken block pool
meant playing it now beat planning it, because the Plan would arrive against a fresh
Plating layer. Same card, opposite answers, both readable off the screen.

The second real axis is elemental ordering, and it is sharper than the Plan. Once Amber
put Pyro on the board, "which of my Hydro cards eats the aura" became a genuine
optimisation, because the aura is consumed by the first different-element hit and there is
exactly one 1.5× to allocate. Fight 3 turn 2 — Deep Current first to Vaporize both slugs,
*then* Vanguard so its Vulnerable is up before the relic's own hit, then kill the healthy
slug rather than the dying one so Ravenous eats the corpse I want it to — was four
decisions chained, and I predicted the numbers in advance and got them.

Third: the relic makes debuff cards into damage cards, which is a quiet, good trade. War
Council's "Weak to ALL" is 2 damage per enemy plus a defensive debuff for one energy, and
that reframing is what made me take it over three other cards.

**(b) What felt automatic, and what never seemed worth playing.**

Every turn where the hand was Strikes and Defends. Fight 1 turn 2 came up
Strike/Strike/Defend/Defend/Defend — **not one card in it interacted with the Bake-Kurage,
the auras or the relic.** With 8 of my 17 cards basic, roughly one turn in three is played
by a character with no kit at all. That is the biggest gap between how good this kit is at
its best and how it feels on average.

Defend specifically. I played it nine times and never once with a rejected alternative
worth writing down; the only question is how many.

Never worth playing, from the screens I saw: **Chain of Command** (offered three times,
including at 72 gold in the shop — "3 damage for each Companion you played this turn" is a
0-damage card until a deck has three or four Companions, and card rewards hand out
Companions one at a time). **Moon's Reflection**, offered twice, was a blank both times —
it reads the Exhaust pile, and in a deck with two exhaust cards it is dead on turn 1 by
construction.

**(c) What you could not understand, or that seemed to contradict its own printed text.**

1. **A non-Plan card played on the Bake-Kurage is a silent no-op that reports success.**
   `play "Strike (1)" on "Bake-Kurage"` returned `"ok": true, "refusal": ""` and
   `Took: Strike (1)`, cost me an action, and did nothing: energy 3/3 unchanged, discard
   pile unchanged, card still in hand, "Nothing is planned. The morning is empty." A
   refusal here would have been correct and cheap.

2. **Vulnerable's two printed definitions disagree.** Status line: "Receive 50% more damage
   **from Attacks**." Glossary on the same screen: "The wearer takes 50% more damage from
   **every hit**." Kurage's Oath is a skill and dealt 3 × 1.5 = 4, so the glossary is right
   and the status line is wrong. A player who trusts the status line will sequence badly.

3. **A Cryo hit landed on a Hydro aura three separate times and the aura never visibly went
   away.** The reaction plainly *happened* — 6 printed Cryo removed 12 HP each time — but
   the aura line only ever decremented by its natural 1 per turn, never showed as consumed.
   The glossary anticipates exactly this ("no screen ever shows it gone and the reaction
   looks as though it did not happen... the reaction did happen — its effect is on the
   body"), which is unusually honest documentation, and it is the only reason I did not
   file this as a bug. But an explanation in a tooltip is not the same as a screen I can
   read: I still cannot tell, at the moment of choosing, whether my next Hydro card has an
   aura to eat.

4. **Printed intent numbers overstated what landed, three times, and always in my favour.**
   F1T2: intent 7 against 5 Block, HP unchanged (expected −2). F4T1: intent 7 against 5
   Block, HP unchanged (expected −2). F5T5: intent 33 against 30 Block, HP unchanged
   (expected −3). Each time the shortfall was small and each time it was exactly the amount
   I had failed to cover. I could not find a printed rule that explains it, and I do not
   know whether the intent number, the block application or my reading is wrong.

5. **Reaction damage is only previewable on turns where you cannot use it.** The
   "Reaction preview: Vaporize — 1.5x damage" line appears on cards *in hand* when the aura
   is already on the enemy. It cannot appear on the turn you play the card that *creates*
   the aura, which is the turn the decision is actually made. My first Vaporize of the run
   was a 50% damage swing I learned about by subtracting HP totals after the fight ended.

6. **The upgrade screen shows the current face, never the upgraded one.** Thirteen cards,
   no previews. I upgraded Deep Current on a guess and found out it was 6 → 9 two fights
   later.

7. **"Deal 7 damage, already including 3 if the enemy has a debuff"** (Undertow, shop). On
   a screen with no enemy, I could not determine whether that card deals 4 or 7.

8. Minor: the kill line printed "**Toadpole** lost 4 HP, and died" with two numbered
   Toadpoles in the fight; and a refused targeting printed `Took: Kurage's Oath.` on the
   same line as `error ... cannot be played on`, which reads as a success followed by a
   failure.

**(d) The card you never wanted to play, and the one you were happiest to draw.**

Never wanted: **Defend**. Four copies, no decision attached to any of them, and it is
strictly worse than Cleansing Wave at the same cost — same 5 Block, but Cleansing Wave also
strips a debuff and carries a 10-Block Plan line. Runner-up is **Chain of Command**, which
I declined three times and would decline again.

Happiest to draw: **Deep Current+**. 9 to ALL for 1 energy is already the best rate in the
deck, and it is the card that decides where the Vaporize goes — it was the opener of the
best turn in fight 3, the burst in fight 4, and it dealt the killing blow twice. **Vanguard**
is the honourable mention: a 0-cost card that applies Vulnerable, sets off the relic, and
makes the relic's own hit 50% bigger in the same beat is a lot of texture for no energy.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a good one.** The opening hand held Kurage's Oath and Cleansing Wave, both
printing two prices — "3 to ALL now / 7 to ALL next turn" and "5 Block now / 10 Block next
turn" — against an 11-damage intent and 3 energy. The question "do I take less now to get
more next turn, and can I afford the turn where the plan is still in the air" was live on
action one, before I understood anything about the character. That is the strongest thing
I can say about this kit: the mechanic that makes it interesting is legible and load-bearing
on the very first screen. The weakest thing is that four Defends and four Strikes are also
in that deck, and roughly every third turn they are all you get.

---

## Non-blindness declaration

Commands run outside `blindplay observe` / `blindplay act`, all through the Bash tool:

- `mkdir -p` twice: once for the scratchpad notes directory, once for the record directory
  `review/qa/kokomi-round-16-2026-09-04`.
- `echo > notes.md` and `echo >> notes.md`, three times, appending my own action count and
  two one-line observations to a scratch file in the session scratchpad.
- `sed -n` on the output of `observe`, to re-read one block of a screen without reprinting
  the whole page. All ranges non-overlapping.
- `grep -m1` / `grep -E` on the output of `observe`, to pull the enemy HP line or the card
  titles out of a screen I had already read in full.
- `head -40`, `tail -2`, `tail -3`, `tail -5` on command output, and `>/dev/null` to
  suppress the JSON echo of `act` calls whose result I read with the following `observe`.
- One `for i in 1 2 3; do ... done` shell loop wrapping three identical `act` calls
  (three Strikes, fight 4 turn 4).

Tools used: **Bash** (all of the above) and **Write** (once, this file).

I did not run `harness state`, `scenario`, `staged_turn`, `soak`, or any understudy command
other than `blindplay observe` and `blindplay act`.

**Repo files read: none.**
