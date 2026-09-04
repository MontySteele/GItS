# Blind seat — KLEEMOD-KOKOMI, lane 1, act 1

## Identity

- **Model / seat:** Opus (Claude), blind TESTER seat. Lane 1, stamp 20260903-223411.
- **Run seed:** `1BPLAQEG976D`
- **Character:** Kokomi. **Ascension 2.**
- **Act:** 1. Act-1 boss named by the map: **The Kin** (never reached).
- **Actions accepted:** 65 `act` calls. Cap was 70.
- **Termination reason:** action budget. I stopped standing on the rest site at
  floor 6 (map coordinate 4,6) with 4 acts left and an **Elite** as the next
  node — not enough budget to open a fight, let alone finish one. No refusal
  streak, no stall, no wall-clock issue, nothing TOOL-BLOCKED.
- **Floors cleared:** Neow → Monster → Shop → Monster → Monster → Unknown (event)
  → RestSite. Three fights, all won.
- **HP trajectory:** 80 max at start; Neow took it to 91. Entered fight 1 at
  **75/91** → 71 → 60 → **54** (fight 1 done) → 54 through the whole of fight 2
  (took zero) → 47 → **45** (fight 3 done) → **38** (event, paid 7 HP) →
  **65/91** after resting.
- **Gold:** 144.
- **Potions held:** none. I was never offered one as a reward and never bought
  one.
- **Deck at the end (14 cards):** Strike ×4, Defend ×4, Slack Water,
  Kurage's Oath, Feint ×2 (one from a card reward, one bought), Ripple (bought),
  Amber — Fiery Rain.
- **Relics:** Tamakushi Casket (starting) — *"Start each combat with the
  Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage
  to that enemy."* — and Nutritious Oyster.

**Neow pick: Nutritious Oyster (+11 Max HP).** Blind, with no idea whether this
kit blocks well or races, the flat HP is the one option whose value I could
compute; Cursed Pearl's 333 gold was tempting but "Receive Greed" is a card I
have never seen and could not price, and Winged Boots buys map freedom I had no
plan for yet.

---

## Fight 1 — Fuzzy Wurm Crawler, 57/57

Opened at 75/91, 3 energy, hand Strike ×3 / Defend / Kurage's Oath. The screen
also handed me the whole Bake-Kurage rulebook up front: the jellyfish is on the
field all fight, cannot be targeted, and *"Play a card on it to write its **Plan**
line instead of playing the card now."*

**Turn 1.** Planned **Kurage's Oath** on the Bake-Kurage, then two Strikes.
*Rejected:* three Strikes for a flat 18. The Oath prints *"Deal 3 damage to ALL
enemies. Plan: Deal 7 damage to ALL enemies."* — against one enemy, played
face-up it is a Strike that deals half as much, so face-up Oath was never on the
table. The real question was Oath-plan + 2 Strikes (12 now, 7 later, and the
carry-out costs no energy next turn) versus 3 Strikes (18 now). I took the plan
because the delayed 7 is free tempo next turn and, per *"the Bake-Kurage carries
out the Plan as a Hydro hit, which does [apply an aura]"*, it seeds an aura I
might get to react with. **This was a real decision and it was the first one of
the run.**

**Turn 2.** The carry-out printed cleanly: `Bake-Kurage: Kurage's Oath, 7 /
Fuzzy Wurm Crawler lost 7 HP`. Enemy 38/57 wearing `Hydro Aura 1`, intent
Empower. Hand was four blanks and a Slack Water. I played **Slack Water** and a
**Strike** and skipped the third energy entirely.
*Rejected:* a Defend, because the printed intent said Buff — block would expire
unused. Also rejected planning Slack Water (`Plan: Apply 1 Weak to ALL enemies`)
because there was one enemy and no damage in that line.

**The screen and the outcome disagreed here, and this is my first finding.**
Slack Water prints *"Deal 4 damage. Apply 1 Weak"*, and the Casket adds 2 Hydro
on any debuff applied — so I expected 6 from it and 6 from the Strike, 12 total,
leaving the enemy at 26. The enemy went 38 → **32**. Exactly 6 landed. The
difference between the two cards: the tool echoed
`ok Playing 'Strike' targeting Fuzzy Wurm Crawler` but only
`ok Playing 'Slack Water'` — **no target**. I had typed `play "Slack Water"` with
no `on` clause. The command was *accepted*, reported `ok`, `"refusal": ""`, and
then did nothing at all: no damage, and no Weak on the enemy the following
screen. Every later single-target card I played with an explicit `on "<enemy>"`
resolved correctly, and the AoE **Kurage's Oath** played with *no* target on turn
4 resolved correctly (14 → 5 alongside a Strike, i.e. its 3 landed). So the
failure is specific to a single-target attack played without a named target: it
silently fizzles while reporting success. I burned a card and an energy on
nothing and did not know until I read the HP bar two screens later.

**Turn 3.** Enemy 32/57, now `Strength 7`, telegraphing 11. Hand was four
Strikes and a Defend. Played **three Strikes**.
*Rejected:* 2 Strikes + Defend. That is 12 damage and 5 block, taking 6 instead
of 11 — but it puts the enemy at 20 and needs a third turn, so it eats the 11
anyway a turn later. Racing was cheaper. Damage landed exactly as printed (32 →
14), which is what let me convict turn 2's Slack Water.

**Turn 4.** Enemy 14/57 still swinging 11. Played **Strike**, **Kurage's Oath**
face-up, **Defend**.
*Rejected:* two Defends + Strike, which takes only 1 damage but leaves the enemy
at 8. I checked the deck: 4 Strike, 4 Defend, Slack Water, Oath — a five-card
hand from ten cards cannot be five Defends, so leaving the enemy at **5** made
next turn's kill arithmetically certain (even Slack Water's 4+2 clears 5), while
leaving it at 8 did not. I paid 6 HP for certainty. *Also rejected:* planning the
Oath for 7 — it would have left the enemy on 1 HP at the start of turn 5 for a
whole extra round of 11-damage attacks, which is the trap the Plan's one-turn
delay sets.

**Turn 5.** One Strike, dead. Rewards: 10 gold, and a card.

**Card reward.** Offered Coral Bulwark, Song of Pearls, **Feint**, and
Yae Miko — Sesshou Sakura. Took **Feint** (*"Deal 6 damage. Plan: Deal 10
damage."*) — a strictly-better Strike whose Plan line is the best rate on the
screen. Yae was the tempting one (Electro, three stacking Sakura, and the
keyword table told me Electro on my Hydro is Electro-Charged) but it is three
energy of setup before it pays and my deck could not afford the tempo.

---

## Interlude — Shop (floor 3)

109 gold. Bought **Ripple** (48) and a second **Feint** (52), ending on 9.
*Rejected:* Card Removal at 75, which in an 11-card deck is real, but fight 1
had just cost me 21 HP against a basic monster over five turns — the deck's
problem was output, not consistency. Ripple prints *"cost 0 — Gain 2 Block.
Plan: Gain 1 Energy and 4 Block."* A zero-cost card that plans into a full extra
energy is the strongest thing on the shelf and I bought it on sight.

Also on the shelf and worth recording, because they name the kit's intended
shape: **Sango Isshin** (*"Deal 8 damage. If the Bake-Kurage carried out a Plan
this turn, deal a quarter of your Max HP to ALL enemies instead"*) and
**Tide Chart** (*"Draw 1 card for each Plan the Bake-Kurage holds"*) — both read
as payoffs for planning heavily every turn, which the starter deck cannot do.

---

## Fight 2 — Shrinker Beetle, 39/39

**Turn 1.** Hand Strike ×3 / Defend / Ripple, enemy telegraphing DebuffStrong.
**Planned Ripple** (cost 0 — free), then three **Strikes** for 18.
*Rejected:* playing Ripple face-up for 2 Block, which is strictly worse than
planning it in every state I can imagine — planning costs the same zero energy
and returns 1 Energy and 4 Block instead of 2 Block. Also rejected holding a
Defend against an announced debuff, which block does not stop.

**Turn 2 — the best turn of the run.** The beetle had landed
`Shrink -1 (debuff) — While Shrinker Beetle is alive, your Attacks deal 30% less
damage.` **The card faces re-printed themselves to match**: Strike now read
"Deal 4 damage", Feint "Deal 4 damage", Slack Water "Deal 2 damage". That is
excellent — I did not have to do the multiplication.

But **the Plan line did not shrink.** Feint still printed *"Deal 4 damage. Plan:
Deal 10 damage."* on the same card face, which lines up with the Plan keyword's
*"Enemy Vulnerable counts; your Weak and Strength do not"* — the carry-out is the
jellyfish's hit, not mine, so my debuff does not travel with it. So I **planned
Feint** (10 next turn) rather than playing it (4 now), then played **Slack
Water** *on the beetle* (this time with a target), **Strike**, and **Defend**,
spending the 4 energy Ripple had given me.
*Rejected:* playing Feint face-up. Choosing between the same card's two halves
because an enemy debuff hits one half and not the other is the most interesting
thing this kit did all act, and the screen printed everything I needed to see it.

Outcome matched: the carry-out logged `Bake-Kurage: Feint, 10 / Shrinker Beetle
lost 10 HP` — full value through a 30% attack debuff. Weak-plus-Casket held the
beetle's 7 to 5, my 9 block ate it, and I took **zero damage this fight**.

**Turn 3.** Beetle on 3, killed with Feint face-up (4 was plenty).
*Rejected:* nothing — this was not a decision.

Rewards: 20 gold, then a card screen offering Moon's Reflection, Tide Chart,
The General's Banner, and **Gorou — General's War Banner**. **I skipped.**
*Rejected:* Tide Chart, the only one with a case (0-cost cycling given I plan
every turn), but at 13 cards I wanted the deck lean more than I wanted one draw.

**A printed contradiction, on that screen.** Gorou — General's War Banner prints
*"Gain 2 Dexterity for 2 turns."* The Dexterity gloss printed directly beneath it
on the same screen prints *"Adds its amount to every Block the wearer gains.
**It does not decay.**"* Those two sentences cannot both be true of the same
card. I could not tell from the screen whether I would be buying 2 turns of
Dexterity or permanent Dexterity, and that ambiguity is the whole price of the
card.

---

## Fight 3 — Nibbit, 44/44

**Turn 1.** Telegraphing 12. **Planned Ripple** (free), **planned Kurage's
Oath**, played **Strike** and **Defend**.
*Rejected:* a second Defend instead of the Strike — 10 block would have taken the
hit to 2 instead of 7, but against a 44 HP body I could not afford to spend a
turn dealing 0. *Also rejected:* Oath face-up for 3 instead of planned for 7,
same reasoning as fight 1 turn 1, and here it was clearly right because nothing
was going to die soon. Two Plans stacked on the jellyfish resolved in printed
order at the start of the next turn, front first — the log showed both.

**Turn 2 — the block/timing decision.** Nibbit dropped to 31 and telegraphed a
**double** intent: `Aggressive (Attack) 6` *and also* `Defensive (Defend)`. I had
4 energy (Ripple's) and a hand of Feint ×2 / Strike ×2 / Defend. I played
**all four attacks face-up for 24** and took the 6 on the chin.
*Rejected:* planning a Feint for 10 instead of playing it for 6. This is the
mirror of fight 2's turn and it is why that decision has teeth: the enemy had
announced it would gain block **on its turn**, i.e. *after* mine — so a planned
hit lands at the start of my next turn into a fresh wall of enemy block, while a
face-up hit lands now into nothing. Planning is worth +4 raw and costs an unknown
amount of block. I chose the certain 6. The wall turned out to be 5, so playing
face-up was right by exactly 1. *Also rejected:* holding a Defend, which would
have saved 6 HP and cost 6 damage against a body I wanted dead in two turns.

**Turn 3.** Nibbit on 7 behind 5 Block, buffing. Played **Strike** (6, of which 5
ate the block and 1 landed), then **Slack Water** *on* it: 4 damage, then the Weak
fired the Tamakushi Casket for 2 more Hydro. 6 exactly, dead.
*Rejected:* leading with Slack Water — the Casket's 2 would have been spent
against block. The ordering mattered and the screens gave me enough to compute
it, which I liked.

Rewards: 14 gold and a card screen offering Treatise, Salt Line, Moon's
Reflection, and **Amber — Fiery Rain** (*"Deal 4 damage to ALL enemies 3 times"*,
Pyro). Took **Amber**: 12 AoE for 1 energy is the biggest number I had been
shown all act, and it is the first off-element source I have owned, which is the
only way anything in the nine-entry reaction table can ever fire.
*Rejected:* Treatise (*"Once per turn, when the Bake-Kurage carries out a Plan,
draw 1 card"*), which is the correct engine card for a deck built around planning
every turn and which I would take in a longer run.

---

## Floor 6 — The Sunken Statue (event) and the rest site

Offered **Grab the Sword** (obtain the Sword of Stone) or **Dive into the Water**
(101 gold, lose 7 HP). Took the gold: at 45/91 the 7 HP was affordable, the map
had shops at 11 and 14 floors ahead, and "Sword of Stone" is a name the screen
gave me no text for at all — I could not price it. *Rejected the Sword purely
because the screen would not tell me what it was.*

Rest site at 38/91 with an Elite as the only onward node: **Rest** for 27, to
65/91. *Rejected Smith*, because 27 HP in front of an Elite beats one upgrade,
and I had no budget left to spend the upgrade in anyway.

---

## The kit, after 3 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The Plan mechanic is the kit, and when it works it works. Three genuinely
different decisions came out of it in three fights:

1. **Plan-now-or-hit-now, priced by tempo.** Kurage's Oath is 3 face-up or 7
   planned; Feint is 6 or 10. The Plan is always the bigger number and always a
   turn late, so the trade is raw damage against the delay — and the delay has a
   real cost, because a Plan that leaves an enemy on 1 HP hands it a whole extra
   attack. I turned down a plan on fight 1 turn 4 for exactly that reason.
2. **The Plan routes around my own debuffs.** Shrink cut my attacks 30% and the
   card faces honestly re-printed — but the Plan line kept its full 10, because
   *"your Weak and Strength do not"* count on the carry-out. Planning Feint for
   10 while face-up Feint read 4 is the sharpest choice the kit offered, and the
   screen printed every fact I needed to find it.
3. **Enemy block inverts the same choice.** On fight 3 turn 2 the Nibbit
   announced attack-*and*-block, which meant a planned hit would land into a
   fresh wall and a face-up hit would not. Same two halves of the same card, and
   the right answer flipped. That the same mechanic reads differently against a
   debuffer and against a blocker is the best thing I can say about it.

Beyond the Plan: Slack Water plus the Tamakushi Casket makes ordering matter
(debuff last, so its free 2 Hydro does not get eaten by block), and that is a
small, satisfying, entirely legible decision.

**(b) What felt automatic, and what never seemed worth playing.**

- **Ripple is a free roll, not a decision.** *"cost 0. Gain 2 Block. Plan: Gain 1
  Energy and 4 Block."* Planning it costs the same zero and returns strictly more
  in both currencies. I planned it every single time it appeared and I cannot
  construct the board where I would not. It is a very good card that never asks
  me anything.
- **Kurage's Oath was never played face-up by choice** for the first four turns
  of the act — against a single enemy its face-up 3 is half a Strike. Its face-up
  half is a card for a fight I have not had yet.
- **Roughly half of every turn was Strikes and Defends.** The starter deck is 8
  vanilla cards out of 10, so the Plan machinery had two cards to work with and
  most turns reduced to "spend the leftover energy on the biggest number." Fight
  1 in particular — five turns, 21 HP, against a basic monster — was mostly
  arithmetic.
- **Defend against an announced Buff intent** is the recurring non-decision: the
  screen tells me block will be wasted, so the "choice" is already made.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **Gorou — General's War Banner** prints *"Gain 2 Dexterity for 2 turns"* while
   the Dexterity gloss on the same screen prints *"It does not decay."* Flat
   contradiction, and it is the card's entire selling point.
2. **The nine-line elemental reaction table is on every screen and never once
   fired.** Melt, Vaporize, Overloaded, Superconduct, Electro-Charged, Frozen,
   Swirl — all glossed at length, including a hundred-word paragraph about a
   reaction that is invisible because a relic re-applies the aura inside the same
   beat. In three fights I owned exactly one element. Every Hydro hit I landed on
   a Hydro aura just "refreshed" it. I read that table five or six times looking
   for the thing I was supposed to be doing with it, and the answer was nothing —
   the starter deck cannot produce a reaction at all. That is a lot of screen
   asking to be understood in exchange for nothing happening.
3. **The Casket's "2 Hydro damage" and aura interaction is genuinely opaque.**
   The keyword text warns me at length that a reaction can be hidden because the
   relic re-applies the aura in the same beat. I could not verify anything about
   this from the screens; I just watched HP numbers.
4. **The Plan carry-out log is very good and I want to say so.** `Bake-Kurage:
   Feint, 10 / Shrinker Beetle lost 10 HP`, with a note explaining that the
   figure under the Plan is the whole beat and the figure on the Plan's line is
   only its first clause. That is the one place the kit shows its working, and it
   is the reason I could convict the Slack Water bug at all.
5. **A defect, not a comprehension failure:** a single-target attack played with
   no `on "<enemy>"` is accepted with `ok` and `"refusal": ""` and then does
   nothing — no damage, no debuff. See fight 1 turn 2. An AoE card with no target
   resolves fine, so the silent no-op is specific to targeted cards, and it looks
   identical to success in the echo.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted: Defend.** Not the kit's fault in principle, but concretely: a
  quarter of my deck was 5 Block, and the Plan mechanic runs on energy the
  Defends were competing for. Every turn I played one it was because I had a spare
  energy and no better sink. **Runner-up: Kurage's Oath face-up**, which in three
  single-enemy fights was a Strike that dealt 3.
- **Happiest to draw: Feint**, and specifically happiest on the Shrink turn. It
  is the card that made the Bake-Kurage feel like a mechanic rather than a delay
  — 10 planned versus 4 face-up, with the reason printed on the card. **Honourable
  mention to Ripple**, which is the card I was most pleased to *own* even though
  it never made me think.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a decent one.** Turn 1 of fight 1 offered three real lines with three
Strikes, a Defend and Kurage's Oath in hand: 18 damage now off three Strikes; or
plan the Oath (7 next turn, free carry-out, Hydro aura seeded) and Strike twice
for 12; or hold a Defend against the telegraphed 4. The Oath's two halves are
printed side by side on the same card face, so the trade is visible on turn one
without any prior knowledge of the kit — I did not have to learn anything to
have the choice. That is a good opening. What is less good is that turns 3 and 5
of the same fight were "play the Strikes."

---

## Non-blindness declaration

**Repo files read: none.**

Every command I ran through the Bash tool:

- `mkdir -p review/qa/kokomi-round-10-2026-09-04` (once, to create the record
  directory the coordinator named), and `mkdir -p` once on a scratchpad
  directory under the session scratchpad, which I then never wrote to.
- `python -m understudy.embark --character KLEEMOD-KOKOMI --lane 1` — exactly
  once, exactly as the coordinator specified.
- `GITS_LANE=1 python -m understudy.blindplay observe` — many times, several
  piped through `tail` or `sed -n '<range>p'` purely to trim the repeated
  keyword tables out of my own reading. `sed`/`tail` were used only on the
  output of `observe` and `act`.
- `GITS_LANE=1 python -m understudy.blindplay act "<command>"` — 65 accepted
  calls, several issued inside a `for` loop over identical repeated plays
  (e.g. three Strikes) to save round-trips. No refused calls that I noticed;
  no refusal streak.

I ran no `harness state`, no `scenario`, no `staged_turn`, no `soak`, and no
other understudy subcommand of any kind. I did not tear the lane down.

Other tools used: the **Write** tool, once, to create this file. Nothing else —
no Read, no Grep, no Glob, no Agent, no web tool.

**Model provenance, as the coordinator required:** I am an **Opus** model
(Claude). The kit under test was authored by a **different Claude model**. We
share a family and a vendor but not a context: I was given no repo access, no
design doc, no sheet, and no prior seat's record for this kit, and everything
above is derived from the bridge's printed screens alone. I had never seen this
kit before this session.
