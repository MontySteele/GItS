# Kokomi round 9, run 2, act 2 — blind seat record

## Identity

- **Model / seat:** Opus, blind TESTER seat (KLEEMOD-KOKOMI), lane 1.
- **Run seed:** not printed on any screen I saw; the bridge never showed a seed.
- **Character:** Kokomi (Bake-Kurage / Plan kit).
- **Act:** 2. **Boss:** Knowledge Demon (named on the act-2 map from the first
  `observe`), 379 max HP. **Killed.**
- **Actions accepted:** 219 `act` calls. **Refusals: 0.** No `TOOL-BLOCKED`,
  no `REFUSED: ...leak...`, no stall.
- **Termination reason:** the coordinator's stop condition, not a budget — the
  act-2 boss died and its reward screen was handled, and the lane now sits on
  the act-3 map (first node: an Ancient). Under both caps at stop (219 of 250
  actions).
- **HP trajectory:** 72/80 entering the first fight → 45 (after fight 1) → 33
  (after fight 2) → **15** (after fight 3, the low point) → rest 39 → 17 (after
  the Entomancer elite) → rest 41 → 41 (Mytes, no damage taken) → rest 65 → 59
  (Exoskeletons) → 40 (paid 14 HP to an event) → rest 64 → **24** at the end of
  the boss fight. Three rests taken, all "Rest", never "Smith".
- **HP at stop:** 24/80 as last printed (boss round 9). The Chosen Cheese grants
  +1 Max HP at end of combat, so max is likely 81; I did not spend an action to
  re-verify and the map screen does not print HP.
- **Gold at stop:** ~172 (154 at the shop, 149 spent there, then +38 +18 +11
  +100). Reconstructed from the printed reward lines, not from a wallet screen.
- **Potions held:** 1 of 3 — **Orobic Acid**. Spent during the act: Energy
  Potion (fight 3), Block Potion (elite), Swift Potion (Exoskeletons), Radiant
  Tincture (boss).
- **Relics at end:** Tamakushi Casket, Silver Crucible, Vajra, Radiant Pearl,
  Whetstone, Red Mask, The Chosen Cheese.
- **Deck at end** — reconstructed from cards the bridge printed to me in hand or
  at a reward, *not* from a deck screen (I never saw one): Luminesce (added each
  combat by Radiant Pearl, exhausts), 2x Sango Isshin (one +), 2x Feint,
  3x Undertow (one +), 2x Kurage's Oath+, 2x Exposed Flank+, Coral Bulwark+,
  Slack Water, War Council, Read the Field, Vanguard+, Stolen Chapter,
  Song of Pearls, The Moon Overlooks the Waters, 2x Nereid's Ascension,
  Expose+, Predator+, Amber — Fiery Rain, Kamisato Ayato — Kyouka,
  Kirara — Surprise Dispatch+, Lynette — Bogglecat Box, several Strikes (some +)
  and Defends, plus the two boss statuses **Mind Rot** and **Sloth**. Roughly 32
  cards.
- **Neow pick: none, inherited.** This was the second of chained seats; the
  previous seat cleared act 1 and left the lane on the act-2 map, so I inherited
  its deck, relics and potions and made no Neow choice.

The one choice that stood in for it, on the act-2 Ancient (Orobas), was
**Radiant Pearl** ("At the start of each combat, add 1 Luminesce into your
Hand"). I took it because a per-combat effect is checkable and the other two
options were not: Glass Eye would have put 5 unseen cards into a synergy deck,
and Touch of Orobas offered to swap "Tamakushi Casket" for "Circlet" while
printing the text of *neither*. Radiant Pearl also taught me a kit card by
giving me one. It turned out to be the right call for a different reason: this
deck is energy-starved and Luminesce is a free +2.

---

## Fight 1 — Bowlbug (Rock) 45 HP, Bowlbug (Egg) 22 HP

Opening state: HP 72/80, Strength 1, Bake-Kurage already on the field.

**Turn 1.** Played Luminesce (0, +2 energy, 5 total) → Exposed Flank+ **on the
Bake-Kurage** (Plan: 3 Vulnerable to ALL next turn) → Sango Isshin on the Rock →
Strike on the Rock → Coral Bulwark+ (9 block).

*Rejected:* playing Exposed Flank+ normally for 2 Vulnerable now, which would
have made this turn's Sango+Strike hit for ~25 instead of 17. I took the Plan
line because the whole question I was here to answer is what the Bake-Kurage
does, and because Vulnerable on the Plan is spread across both bodies.
*Also rejected:* Kurage's Oath+ (5 to all) in place of Strike (8 to the Rock) —
the Egg's intent included Defend, so damage on it was going to be partly eaten.

**A number that did not add up.** The screen printed Sango Isshin as "Deal 8
damage" and Strike as "Deal 7 damage", with Strength 1 showing in my status
block. The Rock went 45 → 29, i.e. **16**, where the printed numbers plus
Strength suggest 17. I could not make the two agree from anything on screen.
This recurred (see fight 3) and I never resolved it.

**Turn 2.** Drew four Defends and a Strike — no Plan card, no Sango. The Plan
fired correctly at turn start: 3 Vulnerable to both, and the Tamakushi Casket's
2 Hydro was properly amplified to 3 by the Vulnerable it had just applied.
Played three Defends for exactly 15 block, chasing the Rock's printed
**Imbalanced 1** ("If Bowlbug (Rock)'s attacks are fully blocked, it becomes
Stunned").

*Rejected:* Strike + two Defends (12 damage, 10 block). I gambled on the stun
even though I could not tell from the screen whether the Egg's 7 would land
first and spoil the "fully blocked" condition. **It worked** — the Rock came up
Stunned. That is the one turn in the act where an enemy's printed keyword gave
me a real, legible thing to play toward.

**Turn 3.** Drew **The Moon Overlooks the Waters** — "Plans also happen when
played." Played it (2) and wrote Feint onto the Kurage (1).

*Rejected:* Feint + 2 Strikes, which would have killed the Rock outright this
turn. I spent a free turn (the Rock was stunned) testing the kit's centrepiece
instead. Moon does what it says: Feint's Plan resolved immediately.

**The reading error I made here, and the correction.** Feint's Plan resolved for
**exactly 15** and I wrote down that it had ignored both Strength and
Vulnerable, contradicting the Plan reminder's "Vulnerable counts". **I was
wrong.** Three fights later I worked out that the number printed on a Plan line
is a *live preview already including Vulnerable against the current front
enemy*: Feint printed 15 with Vulnerable up and 10 without; Kurage's Oath+
printed 15 vs 10; War Council printed 7 vs 5 — all exactly ×1.5. The rule is
honest. What is missing is any indication that the printed number is a
projection rather than the card's face value, and I spent most of the act
believing the kit had a text/outcome bug.

**Turn 4.** The Plan killed the Rock at the start of the turn, which meant a
Plan had been "carried out this turn", so Sango Isshin+ converted to a quarter of
Max HP (20) to ALL and killed the Egg through its 7 block.

**Reward:** took Stolen Chapter ("Draw 2. Plan: Draw 4"). *Rejected:* Noelle —
Sweeping Time and Shell Guard. I picked draw because the failure I had just
suffered was a hand with no Plan card in it.

---

## Fight 2 — Exoskeleton x3, 28/24/25 HP, each **Hard To Kill 9**

"Reduce all damage taken and HP lost by Exoskeleton to 9." A clean, legible
counter to everything the kit had just taught me.

**Turn 1.** Luminesce → Moon → Slack Water on the Kurage → Feint on the Kurage →
Strike. With Moon out, both Plans fired immediately: Weak on all three (dropping
incoming from 11 to 6) plus a Casket trigger on each, and 9 on the front body.

*Rejected:* holding Moon and just attacking. With three bodies and a per-hit cap,
the doubling was worth more than any single card.

**Turn 2.** Undertow killed the first Exoskeleton; Exposed Flank+ onto the
Kurage; Strike. *Rejected: **Predator+**.* This is the sharpest thing the fight
said: Predator+ prints "Deal 21 damage" and the cap turns it into 9, for 2
energy, while 1-cost Undertow also does 9. The cap does not just shrink my
damage, it **flattens the entire cost curve** — and it does so silently, since
no card text mentions it.

**Turn 3.** Undertow (9) + Sango Isshin (20-to-all, capped to 9) finished the
last one. Sango's signature payoff and a 1-cost common were worth exactly the
same number.

**Reward:** War Council. *Rejected:* Gorou — Crystal Collapse (needs a Companion
density I did not have), Vanguard, Sea-Salt Prayer.

The event before this fight (Colorful Philosophers) had **no skip option** — I
had to take a colour. It turned out to be three card *choices*, not three forced
cards, which the screen did not say in advance; I picked Green expecting three
forced Silent cards. Took Predator+ and Expose+, skipped the third.

---

## Fight 3 — Chomper 62 HP, Chomper 63 HP, each **Artifact 2**

The dangerous one. I entered at 33/80 against 125 enemy HP and 16 damage a turn.

**Turn 1.** Luminesce → Lynette (draw 2) → Feint onto the Kurage → Coral
Bulwark+ → Defend → Strike. *Rejected:* the all-in damage line (Sango + both
Strikes for ~24), which would have put me at 17 HP on the first turn of a fight
I could not yet see the end of.

Second instance of the arithmetic gap: printed Strike 7 + Plan 10 = 17, observed
**16**.

**Turn 2.** A hand with **zero attack cards**. Played Expose+ (0 cost, strips
Artifact, 3 Vulnerable) on the front Chomper, Kirara+ and Defend for exactly 16
block against exactly 16 incoming, and Exposed Flank+ onto the Kurage. Took 0
damage but dealt almost none.

**Turn 3.** The good turn. War Council first (Weak to all; the Casket chipped 3
through the Vulnerable, and the second Chomper's Artifact ate the Weak but was
consumed doing it), then Undertow, then Kurage's Oath+ — killing the attacking
Chomper outright so that **I took zero damage that turn**. *Rejected:* saving
Oath's Plan for 15-to-all next turn; removing the 16-damage attacker was worth
more than the bigger number later.

**Turn 4.** Spent the Energy Potion to get Moon down (2) *and* write Stolen
Chapter onto the Kurage (1) in the same turn — Moon drew the 4 immediately.
*Rejected:* Defend + Block Potion, i.e. surviving without solving anything. The
refilled hand held Sango Isshin+, and because Stolen Chapter's Plan counted as
"carried out this turn", Sango converted for 21. **A Moon-triggered Plan does
satisfy Sango's condition** — worth recording, because the card says "the
Bake-Kurage carried out a Plan this turn" and Moon's carry-out happens mid-turn
rather than at turn start.

Then Amber's Pyro onto the Hydro Sango had just applied, for a Vaporize.

**Turn 5.** HP 15/80. Chomper at 21 with a Pyro aura; Sango Isshin+ previewed
"*Reaction preview: Vaporize*" and killed it. The reaction preview on the card
in hand is the single clearest piece of UI in the whole kit.

**Reward:** a second Exposed Flank+. *Rejected:* Song of Pearls (3 block a turn
read as below the act's damage tempo).

---

## Fight 4 (Elite) — Entomancer, 145 HP, **Personal Hive**

"Whenever this enemy is hit by an Attack, add 1 Dazed into your Draw Pile"
(later 2). The exact inverse of the Exoskeletons: there I wanted many small
hits, here I want few large ones. Two fights in a row that invert the same axis
is the best thing this act did.

**Turn 1.** Luminesce → War Council → Exposed Flank+ onto the Kurage → Defend →
Sango Isshin+ → Strike. *Rejected:* skipping Strike to avoid a Dazed — Dazed is
Ethereal, so the clog is self-clearing, which made the small attacks worth it.

**Turn 2.** Lynette to dig; drew a Dazed and a Defend. Played Slack Water (Weak,
cutting the 18 to 13) and Defend. *Rejected:* Slack Water + Undertow for 25
damage, which would have left me at 17 HP.

**Turn 3.** The best turn of the run, and it was an elemental one, not a Plan
one. The Entomancer was buffing (no damage), so: **Amber** (Pyro) vaporized its
Hydro aura and left Pyro behind; **Undertow** (Hydro) then vaporized *that*.
114 → 65, **49 damage in one turn**. Then Feint onto the Kurage.

The chain is legible once you have read the Elemental Reaction block, and the
"leaves the enemy bare" clause was exactly right — after Undertow the aura line
vanished entirely.

**Turn 4.** Incoming 28 against 22 HP. Kirara+ (11) + Block Potion (12) = 23
block, then Predator+ for 33 into the Vulnerable → 19 HP. *Rejected:* Nereid's
Ascension, which resolves next turn and would have been useless if I died first.

**Turn 5.** At 4 HP with 19 incoming and 17 HP, I killed it with **no attack
card at all**: Expose+ (0) and Exposed Flank+ each applied a debuff, each of
which fired the Tamakushi Casket for 2 Hydro amplified to 3 by the Vulnerable
being applied in the same beat — 8 → 2 — and Kurage's Oath+ (4 × 1.5 = 6)
finished it. Winning an elite off relic triggers rather than damage cards is the
most surprising thing the kit did, and it is *entirely* legible from the
Casket's printed text once you notice it.

**Reward:** Whetstone, Red Mask (later), Vanguard+. *Rejected:* Coral Bulwark
(unupgraded duplicate), Diona, Rally.

---

## Fight 5 — Myte 65 HP, Myte 67 HP

Red Mask ("apply 1 Weak to ALL enemies" at combat start) now combined with the
Casket to open every fight with free Weak *and* free damage — both Mytes were
already at 63/65 and 65/67 before I played a card. Whetstone had silently
upgraded Undertow and a Strike.

**Turn 1.** Incoming was 3, so: Luminesce → Coral Bulwark+ **onto the Kurage**
(Plan: 11 block + 2 Weak) → Undertow+ → Strike+ → Strike → Defend. *Rejected:*
Coral Bulwark+ played now for 9 block — with 3 incoming, block this turn was
nearly worthless, and as a Plan it arrived exactly when the Mytes finished
buffing.

**Turn 2.** Two **Toxic** status cards ("At the end of your turn, if this is in
your Hand, take 5 damage"). Played both off for 1 energy each — the same rate as
Defend, so not a trap — plus Exposed Flank+ onto the Kurage. My 11 block from
the Plan already covered the incoming 9, so I took 0.

**Turn 3.** The kit firing exactly as designed: the Flank Plan landed 3
Vulnerable on both at turn start, so Sango Isshin+ converted to 20-to-all at
×1.5 = 30, killing one Myte and taking the other to 6; Amber vaporized; Kurage's
Oath+ at ×1.5 = 6 finished it to the point. No damage taken.

**Reward:** Read the Field. *Rejected:* Deep Current, a third Undertow, Kujou
Sara. Chosen because my two documented failure modes were "hand with no Plan
card" and "no block", and it is both.

---

## Fight 6 — Exoskeleton x4, **Hard To Kill 9** again

**Turn 1.** A hand that was almost entirely debuff-appliers and no attacks —
which against this enemy is *good*, because the Casket's 2 Hydro per debuff is
under the cap and War Council applies to all four bodies at once. Luminesce →
Expose+ → Vanguard+ onto the Kurage → War Council → Exposed Flank+ onto the
Kurage → Swift Potion (draw 3, converting leftover energy into cards) →
Kurage's Oath+ **onto the Kurage** → Slack Water → Song of Pearls.

*Rejected again:* Predator+. Third time the cap made a 2-cost 21-damage card
identical to a 1-cost card.

**Turn 2.** One Exoskeleton had died to the plan volley. With the rest at
10/11/8 and all Vulnerable, I killed **both attackers** — Undertow+ on the third
(killing the later-listed body first so the numbering would not shift under me),
then Undertow + Feint on the second — leaving only a body that intended to buff,
so I took 0. *Rejected:* Coral Bulwark+ for block; killing the attackers is
strictly better than blocking them.

**Turns 3–4.** Anticlimax and a genuine dead turn: one 10 HP enemy left and a
hand of Moon, Stolen Chapter, Nereid's, Lynette, Read the Field — **not one
card that could deal damage**. Lynette found a Strike, which hit the 9 cap and
left it on 1 HP. Killed it the following turn.

**Reward:** Kamisato Ayato — Kyouka, chosen for the single-target boss.
*Rejected:* The Clouds Like Waves Rippling (scales with enemy count; a boss is
one body), Shell Guard, a duplicate Read the Field.

**Event (Room Full of Cheese).** No skip. Chose "Search — Lose 14 HP. Obtain the
Chosen Cheese" over "Gorge — add 2 of 8 random Commons", on the grounds that
dilution had already cost me two dead turns this act and I would rather pay HP
than cards. **The screen never printed what the Chosen Cheese does.** I paid 14
HP for an unnamed effect and only learned in the boss fight's relic list that it
is "At the end of combat, gain 1 Max HP". That is a bad trade I could not have
evaluated from anything on screen, and it is the second time this act an option
asked me to trade for an item whose text was withheld (the first was Orobas).

---

## Fight 7 (Boss) — Knowledge Demon, 379 HP

Entered at 64/80. Red Mask + Casket opened it at 377.

**Turn 1** (its intent was a debuff, so a free turn). Luminesce → Radiant
Tincture (+1 energy now and for 3 turns — banked early deliberately) → Lynette →
**Nereid's Ascension onto the Kurage** → Coral Bulwark+ onto the Kurage → Song
of Pearls → Undertow+. *Rejected:* spending the free turn on Strikes; against
379 HP, chip damage is noise and the fight would be decided by whether the
doubling engine came online.

I wrote Nereid's *first* so it would sit at the front of the Plan queue, on the
guess that "front first" ordering would make it double the Plans written after
it. **That guess was right and the screen confirmed it explicitly**, printing
Coral Bulwark+ twice in the carry-out log for 11 block each. This is the best
piece of feedback in the whole kit: the Bake-Kurage panel prints exactly what it
carried out, in order, with the HP lost under each line.

**The boss's debuff choices.** Twice it made me add a status card with no skip:
first Disintegration (6 damage at end of turn) vs **Mind Rot** (draw 1 fewer),
then Disintegration (7) vs **Sloth** (cannot play more than 3 cards a turn). I
took the tempo costs both times, reasoning that per-turn damage compounds
lethally in a fight this long. Neither card states whether it works from hand or
from anywhere in the deck, which is the information I most needed to choose.

**Turn 2.** Expose+ (3 Vulnerable) → **Moon** → Read the Field onto the Kurage →
Ayato. Getting Moon down *inside* Nereid's 2-turn window was the whole plan.

**Ayato did not do what I read it as doing.** "For 2 turns, your Attacks apply
Hydro and deal 4 additional damage. **Then** deal 12 Hydro damage to a random
enemy." I read "then" as "on play, after the buff"; the boss lost 3 HP that turn
(the Expose+ Casket trigger alone), so the 12 never landed on play. I assume it
fires when the 2 turns expire, but I never saw it resolve and no screen told me.

**Turns 3–5, the engine at full tilt.** With Moon out, every Plan I wrote fired
immediately *and* again next turn; with Nereid's up it fired twice on carry-out.
Turn 3: War Council onto the Kurage + Strike+ + Sango Isshin = **62 damage**.
Turn 4: Stolen Chapter onto the Kurage (drew 4 instantly), Feint onto the
Kurage, Amber's vaporize, Vanguard+ onto the Kurage, then Sango Isshin+ with
Vulnerable *and* a Vaporize on top = **78 damage** (265 → 187). Turn 5 was
another free turn (debuff intent): Predator+ for 33 and Exposed Flank+ onto the
Kurage.

These three turns are what the kit is for, and they were genuinely exciting to
play — each one was a small ordering puzzle (which element to lay first, whether
to write a card as a Plan or spend it now) with a visibly enormous payoff.

**Turns 6–9, the grind.** Then Sloth bit, Mind Rot bit, and the fight became
much duller: hands of three Defends with a 3-card cap. The boss healed twice
(196 from 187, then **4 back up to 34** after I had it one card from dead).
Turn 8 I got it to 4 HP and could not finish — 0 energy and the 3-card cap
reached. Killed it on turn 9 with Undertow+ (21) + Predator+ (33).

*Rejected on the last turn:* Sango Isshin+ — no Plan was carried out that turn,
so it was an 8-damage card. That is the tension the kit is built on, and it was
live right to the final turn.

**Reward:** 100 gold and a **second Nereid's Ascension**. *Rejected:* a second
Moon — Moon is a persistent power, so a duplicate does nothing once one is down,
whereas Nereid's exhausts and a second copy is a second doubling window.

---

## The kit, after 7 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The kit's core decision is genuinely good and it is live on almost every turn:
**spend this card now, or write it onto the Bake-Kurage and get its bigger Plan
line a turn late.** Feint is 7 now or 10 (15 into Vulnerable) next turn; Coral
Bulwark+ is 9 block now or 11 block plus 2 Weak next turn. Because the Plan
arrives at the *start* of your next turn, writing it is also a bet on what the
enemy will do, and I made that bet both ways for good reasons — Coral Bulwark+
went onto the Kurage in fight 5 precisely because incoming was 3 that turn and
would be 9 the next.

The second real choice is **ordering elements within a turn**. Amber (Pyro) then
Undertow (Hydro) chains two Vaporizes for 49 damage; the reverse order is worth
far less. Sango-then-Amber vs Amber-then-Sango mattered in three separate
fights. This is a genuine skill axis and the reaction preview on the card makes
it learnable rather than guesswork.

Third, and best, the **enemies invert the axes on you**. Hard To Kill 9 makes
big hits worthless and rewards wide chip and debuff-relic triggers; Personal
Hive makes many small hits actively harmful and rewards one huge one. Playing
those two fights back to back was the most interesting sequence of the act,
because the *same hand* wants opposite play patterns.

Fourth, Nereid's + Moon creates a real construction problem: Nereid's doubles
carry-outs for 2 turns, Moon makes writes resolve immediately, so there is a
narrow window where you want both down and a fat Plan card in hand. Building
toward that on boss turn 1 and cashing it on turns 3–5 was the most satisfying
thing I did.

**(b) What felt automatic, and what never seemed worth playing.**

Defend and Strike. They are pure filler in a deck whose whole identity is the
Plan line, and by the end I had drawn hands of *four Defends* (fight 1 turn 2),
*three Defends and no damage* (boss turn 6), and *five cards with no attack at
all* (fight 6 turn 3). Those turns presented no decision worth the name.

**Predator+ was never worth playing against a capped enemy** and I rejected it
three separate times — 21 printed damage for 2 energy collapsing to the same 9 a
1-cost Undertow does. Whether that is the cap's fault or the card's, the effect
is that the enemy's buff silently deletes the cost curve.

Song of Pearls (3 block once per turn) never mattered; I took it once and
declined it once. Kirara+ and Lynette were fine but unexciting.

More broadly: **deck dilution is the kit's real enemy.** I ended around 32 cards
with two forced boss statuses in it, and my dead turns were all dilution, not
bad decisions. I declined cards repeatedly for this reason and still ended up
with too many. Two events this act (Colorful Philosophers, Room Full of Cheese)
offered **no skip at all**.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **The Plan number on a card is a live preview, and nothing says so.** Feint
   printed "Plan: Deal 15 damage" in one fight and "Plan: Deal 10 damage" in the
   next, identical card, no upgrade marker, no enchantment. I recorded it as a
   text/outcome contradiction and carried that belief for three fights before
   working out it was Vulnerable being folded into the display. The rule is
   correct; the *presentation* actively misled me, because the number moves
   without any indication that it is a projection against the current front
   enemy. This is my single biggest legibility finding.

2. **Damage arithmetic came in 1 low, twice.** Fight 1: Sango (printed 8) +
   Strike (printed 7) with Strength 1 → observed 16. Fight 3: Strike (printed 7)
   + Plan 10 → observed 16 vs 17 expected. Meanwhile Predator+ *did* show
   Strength baked into its face ("Deal 20" at the reward, "Deal 21" in hand)
   while Strike showed "Deal 7" with Strength 1 up. So Strength is displayed on
   some cards and not others, and I could not reconcile the totals from any
   screen.

3. **Kamisato Ayato — Kyouka's "Then deal 12 Hydro damage"** never visibly
   resolved on play. I read "then" as immediate; the boss lost only the 3 from a
   separate Casket trigger that turn. I never saw the 12 land.

4. **Hard To Kill 9 is invisible on the cards it neuters.** Nothing on Predator+
   hints that its 21 will be 9.

5. **Two screens asked me to trade for items whose text they did not print** —
   Orobas offering to swap Tamakushi Casket for "Circlet", and the Cheese event
   charging 14 HP for "the Chosen Cheese". I paid the 14 HP and got +1 Max HP per
   combat.

6. **The boss's status cards** (Mind Rot, Sloth, Disintegration) never say
   whether they act from hand or from anywhere, which is exactly what you need to
   choose between them.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Defend.** It is 5 block in a deck that generates 11 and 20 block
off Plan lines, and every copy I drew was a turn I could not use. Predator+ is a
close second, for the specific reason that against two of this act's five enemy
types it is a strictly worse Strike.

Happiest to draw: **The Moon Overlooks the Waters.** It converts the kit's
central cost — the one-turn delay on every Plan — into no cost at all, and it
does it while *keeping* the delayed copy, so a written Plan pays twice. Drawing
it turns a slow deck into a fast one in a single card. Honourable mention to
**Sango Isshin+**, which is the payoff the whole Plan structure exists to set
up, and which produced the two biggest single hits of the act.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a good one.** Turn 1 of fight 1 I had 5 energy and 6 energy worth of
cards, so something had to be cut, and the real question was structural rather
than arithmetic: write Exposed Flank+ onto the Bake-Kurage for 3 Vulnerable to
both bodies next turn, or play it now to make this turn's attacks hit ~50%
harder. That is exactly the kit's signature tension, available on the very first
turn, and the Bake-Kurage was already on the field with its rules printed. I
also had a live secondary read — the Rock's Imbalanced keyword offering a stun
if I could fully block 15.

The one caveat is that the *reason* the choice is interesting only became clear
on turn 2, when I learned the hard way that nothing retains: Sango Isshin will be
discarded whether or not I play it, so "hold the payoff card for the turn the
Plan lands" is not actually an option. The combo requires drawing the enabler and
the payoff in the right order with no way to store either, which is why several
of my turns collapsed into Defends.

---

## Non-blindness declaration

**Repo files read: none.**

Commands run outside the two allowed ones (`blindplay observe` / `blindplay act`):

- `mkdir -p ".../scratchpad/kokomi-r9-run2"` and one `echo` appending a single
  scratch line ("act2 start: map, boss Knowledge Demon, path Ancient") to
  `notes.md` in that scratchpad directory — run once, at the start.
- `sed -n` filters applied to the output of `observe` on many calls, purely to
  re-read selected blocks (hand, enemies, status) of screens the bridge had
  already printed to me. No new information came from these.
- `head -N` / `tail` on `observe` output, same purpose.

Tools used: **Bash** (for the above and for every `observe`/`act`), and **Write**
once, to create this record file at the path the coordinator gave.

I did not run `harness state`, `scenario`, `staged_turn`, `soak`, or any other
understudy subcommand. I did not open any file under `review/`, including the
other files in this round's directory. I did not read any YAML sheet, C# source,
doc, packet or other seat's record. Everything above comes from what the bridge
printed to this seat during the run.
