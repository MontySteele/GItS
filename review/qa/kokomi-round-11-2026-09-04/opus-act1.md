# Kokomi — blind seat, round 11, act 1

## Identity

- **Model / seat:** Opus (Claude), blind TESTER seat, lane 1 (`KLEEMOD-KOKOMI`)
- **Run seed:** 7BEKR9871311
- **Character:** Kokomi
- **Ascension the run opened at:** 2
- **Act:** 1. The map named the act boss at the top: **Ceremonial Beast**. I did
  not reach it — 16 floors to the boss, and the action budget ran out on floor
  10.
- **Actions accepted:** 119 of the 120 given. I stopped one short because the
  only remaining action was opening a card-reward selection I would then have
  had no action left to resolve.
- **Termination reason:** action budget. Wall clock was nowhere near its cap
  (roughly 45 minutes of the 5400 s). No refusals, no stalls, no
  `TOOL-BLOCKED`.
- **HP trajectory:** opened combat at **64/80** (the run began at 80% of max —
  the Neow screen never printed HP, so the first number I saw was on the first
  battle screen) → 55 (end F1) → 44 (F2) → 36 (F3) → **23** (F4, the low point)
  → rest → 47 → 32 (F5) → rest → 56 → **44/80** (F6, final).
- **Gold at stop:** 78.
- **Potions held at stop:** Energy Potion, Speed Potion, Weak Potion (4 slots,
  3 full). Spent during the run: Explosive Ampoule (F4), Fire Potion (F6).
- **Relics at stop:** Tamakushi Casket (starting), Phial Holster (Neow),
  Miniature Cannon (act-1 chest).
- **Deck at stop (18 cards).** Starter ten: 4× Strike, 4× Defend, Slack Water,
  Kurage's Oath. Added: Ambush ×2 (fight rewards), Cleansing Wave (reward),
  Kaeya — Frostgnaw (reward), Tide Wall (reward), Exposed Flank / Undertow /
  Sea-Salt Prayer (shop). Nothing upgraded — I took Rest over Smith both times,
  which made the Miniature Cannon I found ("Upgraded Attacks deal 3 additional
  damage") a dead relic for the whole run.

**Neow pick: Phial Holster** — "Gain 1 potion slot and procure 2 random
Potions." Blind and at ascension 2 I wanted resources I could read the text of
and spend on a turn that went wrong, rather than Neow's Bones' curse or Fishing
Rod's slow upgrade drip. It paid: the Explosive Ampoule was what let me kill the
Snapping Jaxfruit a turn early in fight 4, which is the turn I would otherwise
have died on.

**Tool note the coordinator asked for.** The first single-target card I played
bare was `play "Strike"` on turn 1 of fight 1, against the only enemy on screen.
It was **accepted without a refusal** and auto-targeted: the result printed
`"target": "FUZZY_WURM_CRAWLER_0"` and `Playing 'Strike' targeting Fuzzy Wurm
Crawler`. I never saw the refusal-with-working-forms path, because I used
explicit `on "<enemy>"` from fight 3 onward wherever more than one enemy stood.

---

## Fight 1 — Fuzzy Wurm Crawler, HP 57/57

Opened at 64/80, 3 energy. Hand: Defend ×2, Slack Water, Kurage's Oath, Strike.

**Turn 1.** Played Strike (6), then Slack Water (4 + 1 Weak), then planned
Kurage's Oath onto the Bake-Kurage.

*Rejected:* playing Kurage's Oath now for its printed "Deal 3 damage to ALL
enemies" instead of its "Plan: Deal 7 damage to ALL enemies". Against a 57 HP
enemy telegraphing only 4 damage, buying 7 next turn for 3 now is free — there
was no pressure to make me want the damage immediately. That is a genuine
decision and it is the one the whole kit is built on, and it was legible on the
first turn because both numbers are printed on the same card face.

The screen and the outcome agreed exactly. 57 → 45 is 12: Strike 6 + Slack Water
4 + 2 from **Tamakushi Casket** ("Whenever you apply a debuff to an enemy, it
deals 2 Hydro damage to that enemy") firing off the Weak. The enemy's intent
number dropped 4 → 3 on the same beat, which is Weak's 25% shown rather than
described.

**Turn 2.** Drew 3× Strike, 2× Defend. Enemy was Empowering (a buff, no damage).
Played three Strikes, ended.

*Rejected: nothing.* **This turn presented no decision at all.** Every Kokomi
card was out of hand, the enemy threatened nothing, and the hand was five
vanilla starter cards. The correct line was "play all three Strikes" and there
was no second option worth a sentence. Recording that as the finding it is.

The plan carried out at the start of this turn for exactly 7, printed as its own
block:
`Bake-Kurage: Kurage's Oath, 7 / Fuzzy Wurm Crawler lost 7 HP`.

**Turn 3.** Enemy at 20, now Strength 7 and swinging for 11. Played Strike,
planned Kurage's Oath, played one Defend.

*Rejected:* two Defends plus a planned Oath (10 block, take 1, but the enemy
stays at 20 and I bank only 7). I chose to eat 6 through 5 block because putting
the enemy at 14-then-7 kills it a full turn sooner, and a turn saved against a
Strength-stacking enemy is worth more than 5 HP. Also rejected: dumping
Explosive Ampoule — 6 + 3 + 10 = 19 against 20 HP is one point short of a kill,
which is exactly the kind of thing the printed numbers let me check before
wasting the potion.

**Turn 4.** Plan hit for 7 (enemy at 7), two Strikes finished it. No decision.

Cleared in 4 turns at 55/80. Reward: 19 gold, and I took **Ambush** ("Deal 5
damage. Plan: Deal 12 damage") over Treatise, Salt Line and Kazuha Slash — 12
damage for 1 energy on a one-turn delay is the best rate on the screen, and with
only two Plan cards in the deck, Treatise's "when the Bake-Kurage carries out a
Plan, draw 1" would rarely have fired.

---

## Fight 2 — Nibbit, HP 43/43

**Turn 1.** Enemy telegraphed 12. Planned Ambush, planned Kurage's Oath, played
one Defend.

*Rejected:* the safe line, planned Ambush plus two Defends (10 block, take 2).
I chose to take 7 to bank 19 damage instead of 12. I also genuinely did not know
whether a second Plan would queue or overwrite the first — nothing I had been
shown said. It queued, and the screen said so clearly:

```
- Planned, and carried out at the start of your next turn in this order (2):
  1. **Ambush**
  2. **Kurage's Oath**
```

That "in this order" line is the single most useful sentence on the battle
screen, and it is what made the fight-5 combo below thinkable.

**Turn 2.** The carry-out printed 12 then 7; enemy 43 → 24. Played Strike,
Strike, Slack Water (18 total with the relic ping), ended.

*Rejected:* holding a Defend. The enemy was Blocking-and-attacking for 6, and
Slack Water's Weak dropped that to 4 — so the Weak *was* my defense, and it came
attached to damage. Outcome matched: I took 4, not 6.

**Turn 3.** Enemy at 6 behind 5 Block; two Strikes. No decision.

Cleared at 44/80. Took a second **Ambush** over Treatise, Read the Field and
Sayu — Yoohoo Art.

---

## Fight 3 — Leaf Slime (S) 15/15, Twig Slime (M) 26/26, Twig Slime (S) 10/10

First fight where "ALL enemies" meant something. 51 enemy HP, 7 incoming.

**Turn 1.** Planned Ambush, planned Kurage's Oath, Struck Twig Slime (S) down to
4.

*Rejected:* killing Twig Slime (S) outright with two Strikes and planning only
the Oath — safer (take 3 instead of 7) but it leaves both other slimes healthy.
I gambled that Ambush's Plan would hit the *front* enemy as printed ("front
non-Minion, or ALL, Minions too") and that the Oath's 7-to-all would clean up
behind it.

It resolved precisely, and the log is the best thing in the kit:

```
  - Bake-Kurage: Ambush, 12
    - Leaf Slime S lost 12 HP
  - Bake-Kurage: Kurage's Oath, 7
    - Leaf Slime S lost 3 HP, and died
    - Twig Slime (M) lost 7 HP
    - Twig Slime S lost 4 HP, and died
```

Two of three enemies died before I acted on turn 2. That is the kit's best
moment in this run.

**Turn 2.** One slime left at 19, swinging 11. Planned Ambush, played two
Defends (10 block).

*Rejected:* Striking. This is the turn that showed me what the Plan mechanic
actually buys: because next turn's 12 damage was already paid for, I could spend
*this entire turn* on block and lose no tempo. I took 1 damage. That is a real,
specific, kit-shaped decision that a normal Spire deck cannot make.

**Turn 3.** Plan hit for 12 (enemy at 7), Strike + Slack Water finished it.

Cleared at 36/80. Took **Cleansing Wave** ("Gain 5 Block. Remove one of your
debuffs. Plan: Gain 10 Block") over Song of Pearls, Stolen Chapter and Heizou —
at 36 HP I wanted block density, and I explicitly rejected Song of Pearls (3
block per carry-out) because a power that does nothing on the turn it is cast is
a bad buy when you are the one under pressure.

**One thing I could not resolve.** Twig Slime (M)'s turn-1 intent printed
*"Strategic (StatusCard) — this enemy intends to give you 1 Status card."* I
never saw a status card. At the start of turn 3 the piles read 8 in draw + 5 in
hand = 13, which is exactly my deck size at that point (10 starter + 2 Ambush +
Cleansing Wave was not yet added, so 12 — and I count 13). I could not open a
deck view to settle it, so I am recording it as unresolved rather than as a
defect: either the status card never arrived, or my card count is off by one.

---

## Fight 4 — Snapping Jaxfruit 31/31, Flyconid 49/49

The dangerous one: 80 enemy HP, 11 incoming, me at 36.

**Turn 1.** Slack Water into Flyconid (Weak, dropping its 8 to 6), one Defend,
planned Cleansing Wave.

*Rejected:* two Defends plus Slack Water, which blocks all 9 and takes zero.
I gave up 4 HP to start the block engine, on the reasoning that a 10-block plan
arriving free next turn is worth more than 5 block now. **This was the wrong
call and the screen told me so afterwards.**

**Turn 2 — the one legibility complaint I have.** The carry-out printed:

```
  - Bake-Kurage: Cleansing Wave, 10  →  actually printed: Cleansing Wave, 7
    - no enemy lost HP
```

It gave me **7 block, not the 10 the card promised**, because the Flyconid's
debuff intent had landed **Frail 2** ("Gain 25% less Block from cards") in
between planning and carry-out — 10 × 0.75 = 7. That is almost certainly
correct, but the carry-out log's format is `<card name>, <number>` followed by
HP-loss lines, and for a block Plan it prints a bare number in the slot where
every other line prints damage, then says "no enemy lost HP". I had to work out
what the 7 was. (The screen does carry a footnote for this — *"The figure on the
Plan's own line is what its first clause produced, which is a different quantity
whenever that clause is not damage"* — but that footnote only appeared on some
screens, and not on the one where I first hit the problem.)

The compensating thing, which is genuinely excellent: my **Defend card face
changed to "Gain 3 Block"** under Frail. The card tells you its real current
number rather than its printed base. I trusted that immediately.

Played Explosive Ampoule (10 to all), planned Ambush, two Strikes into the
Jaxfruit.

*Rejected:* focusing the Flyconid. The Jaxfruit was Empowering itself (+2
Strength a turn), so it was the growing problem even though it was the smaller
one; the Flyconid's 11 was at least static. Killing the Jaxfruit first was the
right read.

**Turn 3.** `Bake-Kurage: Ambush, 12 / Snapping Jaxfruit lost 9 HP, and died`.
Flyconid alone at 33, intent **Debuff only — no damage**. Planned Ambush,
Ambush, Kurage's Oath. All three, nothing else.

*Rejected:* playing them for 5 + 5 + 3 = 13 now. The enemy had announced it
would not hit me, so the delay cost literally nothing and the same three cards
were worth 31 instead of 13. **This is the sharpest decision the kit produced
all run**, and it was only available because enemy intent and the Plan numbers
are both printed plainly enough to compare.

**Turn 4.** 12 + 12 + 7 landed; Flyconid at 2. But its debuff turn had given me
**Vulnerable 2**, and it was now telegraphing 16 — which is 24 against
Vulnerable, into my 23 HP. One Strike killed it. Had I banked one card less, I
would have died to a number I could see coming and could not have blocked.

Cleared at 23/80. Took **Kaeya — Frostgnaw** [Cryo] over War Council, Feint and
Rally — my first non-Hydro card, and the only thing that made the enormous
Elemental Reaction glossary on every screen reachable at all.

---

## Shop (floor 5) and rests

169 gold. **Lee's Waffle — "raise your Max HP by 7 and heal all of your HP" —
cost 170.** At 23/80, one gold short of a full heal. I want that in the record
because it was the most memorable moment of the run and it was pure arithmetic
cruelty, not a defect.

Bought Exposed Flank (52), Undertow (50), Sea-Salt Prayer (25); left 42. I
skipped Card Removal (75) and I think that was wrong — I finished on 18 cards
with 8 starter Strikes and Defends still in there, and I saw hands with no
Kokomi card in them twice.

Rested twice (23 → 47, 32 → 56) and took Rest over Smith both times, which is
why nothing is upgraded.

---

## Fight 5 — Inklet 14/14, Inklet 13/13, Inklet 16/16

All three carried **Slippery 1** — "The next time Inklet loses HP, it only loses
1 HP instead."

**Turn 1.** Hand was Defend ×3, Kaeya — Frostgnaw, Strike. Played two Defends
and Kaeya into the middle Inklet (13 block against 12 incoming, take 0).

*Rejected:* Striking. Slippery caps every hit at 1 HP, so damage this turn was
worth almost nothing and block was worth full price — the enemy's own buff
turned "attack or defend" into a real question with an unambiguous answer. Kaeya
went in as the cheapest way to strip one Slippery *and* leave a Cryo aura.

Also worth saying: **this hand contained zero Plan cards.** Five cards, no
Kokomi mechanic, on turn 1 of a fight. That happened twice in the run.

**Turn 2.** Planned Exposed Flank **first**, then Ambush, then Cleansing Wave.

*Rejected:* any ordering with Ambush before Exposed Flank. The Plan glossary
says "Enemy Vulnerable counts; your Weak and Strength do not", and the queue is
explicitly ordered, so Vulnerable applied first should multiply the Ambush
behind it. Also rejected: playing Cleansing Wave now for 5 block instead of
planning it for 10 — I chose to eat the full 15 and bank the bigger block.

**Turn 3 — the best screen of the run.** The carry-out:

```
  - Bake-Kurage: Exposed Flank, 2
    - Inklet lost 1 HP
    - Inklet (1) lost 3 HP
    - Inklet (2) lost 1 HP
  - Bake-Kurage: Ambush, 18
    - Inklet lost 13 HP, and died
  - Bake-Kurage: Cleansing Wave, 10
    - no enemy lost HP
```

Everything in that block is checkable and every number is right:

- Ambush hit for **18**, not 12 — Vulnerable applied first, 12 × 1.5. The
  ordering rule works exactly as printed.
- Exposed Flank's line reads "2" (the Vulnerable stacks), and the HP losses
  under it are my **relic** firing: Tamakushi Casket's 2 Hydro damage per debuff
  applied. Two of them read "lost 1 HP" — those are the two Inklets still
  holding Slippery, capping the relic ping at 1. The third read "lost 3 HP" —
  2 × 1.5, because its Slippery was already stripped and Vulnerable was already
  on. Three different numbers from one card, all derivable.
- And the Inklet whose Slippery Kaeya stripped came out of that beat wearing
  **Frozen 1**, with its intent halved from 2×3 to 1×3. Nothing I played was
  Cryo that turn. What happened is the chain the glossary explicitly warns
  about: Exposed Flank applied a debuff → the relic dealt **Hydro** damage →
  that Hydro met the **Cryo aura Kaeya had left last turn** → Frozen. A
  three-step reaction I did not plan, that the log let me reconstruct
  afterwards. I would not have found it without the per-Plan HP breakdown.

Finished with Undertow into one (7 → 10 for the debuff → 15 with Vulnerable,
exactly lethal on 15 HP) and Strike into the Frozen one (9 + the 6 Shatter).

Cleared at 32/80 having taken **zero** damage on the last two turns. Took **Tide
Wall** over Tide Chart, Stolen Chapter and Mizuki.

---

## Fight 6 — Vine Shambler, HP 61/61

**Turn 1.** Planned Kurage's Oath, planned Cleansing Wave, played Strike.

*Rejected:* Undertow + Strike + Strike for 19 immediate. Against 61 HP and 12
incoming a turn I judged the fight long enough that banked block would matter
more than 6 extra front-loaded damage. Took 12.

**Turn 2.** Held 10 block against a telegraphed 8, so the block was already
paid for. Planned Ambush, Ambush, Tide Wall.

*Rejected:* playing the Ambushes now for 5 each. Same call as fight 4 turn 3,
and it is becoming the kit's default rather than a decision — see (b).

**Turn 3.** The carry-out: 12, 12, and `Bake-Kurage: Tide Wall, 9`. Tide Wall
reads "Plan: Gain 3 Block for each Plan the Bake-Kurage carries out this
morning" — three Plans carried out, 9 block, exactly as printed, and it counts
*itself*. Enemy 48 → 24.

The enemy's affliction intent landed **Tangled 1** — "Attacks cost an additional
[Energy] this turn" — and every Attack in my hand immediately reprinted at cost
2 while my Skills stayed at 1. Again the card faces carried the live number.

And Kaeya — Frostgnaw grew a line I had not seen before:

```
*Reaction preview: Frozen* — Hydro meets Cryo: its next action deals half
damage, and the first Attack to hit it Shatters for 6 damage.
```

The card told me, unprompted, which reaction it would cause against the aura
currently on the board. That is the single best piece of design on the screen
and it is what made the reaction system feel usable rather than decorative.

Killed it with Fire Potion (20) + Kaeya (8) rather than grinding two more turns
against a 16-damage swing.

Cleared at 44/80. Budget reached during the reward screen.

---

## The kit, after 6 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The kit has exactly one central decision and it is a good one: *every Plan card
prints two numbers, and you choose between them.* Kurage's Oath is 3 now or 7
next turn; Ambush is 5 now or 12; Cleansing Wave is 5 block now or 10 next turn.
The trade is always tempo for rate, and what makes it a decision rather than a
sum is that the enemy's intent is printed on the same screen — so "can I afford
to do nothing this turn?" is answerable rather than a guess.

The three turns that felt genuinely good all came from that:

1. **Fight 3, turn 2** — because next turn's 12 damage was already bought, I
   could spend a whole turn on block and lose nothing. The Plan mechanic
   converts a defensive turn from a tempo loss into a free action. Nothing else
   in Spire does that.
2. **Fight 4, turn 3** — the Flyconid announced a damage-free turn, so the delay
   cost zero and three cards were worth 31 instead of 13. Reading the intent
   *changed which half of the card I used*. That is the mechanic working.
3. **Fight 5, turn 2** — planning Exposed Flank *before* Ambush so the
   Vulnerable multiplies it. The queue is ordered and printed, so sequencing
   within a single turn's plans is a real skill with a real payoff (12 → 18).

Below that, Slippery in fight 5 and Frail/Tangled in fights 4 and 6 all produced
honest "attack or defend" turns, because they made one of the two obviously
worth less.

**(b) What felt automatic, and what never seemed worth playing.**

**The Plan choice collapses once you own two Ambushes.** By fight 4 I was
planning every Plan card I drew, nearly every turn, without thinking — 12 vs 5
and 10-block vs 5-block are not close enough to be decisions. The only turns
where "play it now" won were turns where I needed lethal *this* turn, and there
were two of those in six fights. A choice you make the same way 90% of the time
has stopped being a choice, and by fight 6 my turns were "put everything on the
jellyfish, end turn" — which is the same automatic feeling as a turn with no
mechanic at all, just with an extra step.

The delay also has a hidden floor: **turn 1 of every fight is spent, not
played.** You plan, you end turn, and the fight actually starts on turn 2. Six
times out of six.

Never worth playing: **Strike and Defend.** They have no Plan line, so in a kit
whose entire decision surface is "which half of this card", the starter cards
are inert filler — and I finished with eight of them in eighteen cards. Twice I
opened a fight with a five-card hand containing **zero Plan cards** (fight 5
turn 1; fight 1 turn 2), and those turns had no decision in them whatsoever. I
should have bought the Card Removal.

Also never worth it in practice: the reaction glossary. Six reactions are
printed on every single battle screen — Melt, Vaporize, Overloaded,
Superconduct, Electro-Charged, Frozen — and for the first four fights I could
not trigger a single one, because everything I owned was Hydro and Hydro on
Hydro just refreshes. The glossary is about 40% of the screen text and 0% of the
gameplay until a Cryo card happens to show up in a reward.

**(c) What I could not understand, or that contradicted its own printed text.**

- **The block-Plan carry-out line.** `Bake-Kurage: Cleansing Wave, 7` printed a
  bare 7 in the slot where every other carry-out prints damage, followed by "no
  enemy lost HP". The 7 was block, reduced from 10 by Frail. Correct, but the
  log format is damage-shaped and I had to derive it. (Fight 4.)
- **Copy numbering.** `Inklet (1)` in fight 5 turn 3 was a *different* Inklet
  than `Inklet (1)` had been the turn before, because the front one had died and
  the list re-counts. The screen does warn about this for cards, and I still
  nearly targeted the wrong body. It is a real hazard when a fight kills things
  out of order.
- **Twig Slime (M)'s StatusCard intent** (fight 3) — telegraphed, and I never
  saw a status card appear. Unresolved; I had no way to view my deck.
- The Bake-Kurage buff line reads "carries out **1** Plan at the start of your
  next turn" while holding three. It is a stack counter, not a limit, but the
  sentence reads like a limit.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Defend.** 5 block, no Plan line, and by the midgame it was
literally worse than the cards I planned for block (Cleansing Wave 10, Tide Wall
9). It is a card that exists to be a blank.

Happiest to draw: **Ambush.** 12 damage for 1 energy is the best rate in the
deck by a distance, and drawing two of them meant a turn where I put 24 damage
on the board for 2 energy. Runner-up, and the more *interesting* card:
**Exposed Flank**, because it is the only card that made the ordering of my own
plans matter, and its Vulnerable turned Ambush from 12 into 18.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and cleanly.** Turn 1, fight 1, I held Kurage's Oath with "Deal 3 damage
to ALL enemies. Plan: Deal 7 damage to ALL enemies" printed on one face, against
an enemy telegraphing 4 damage into my 64 HP. Both numbers, the cost, and the
enemy's intent were all on the same screen, so the trade was checkable before I
committed. I planned it, took 4, and it paid 7.

That is a better opening than most characters manage. The problem is not the
first turn — it is that the same decision returns every turn afterwards with the
same answer.

---

## Non-blindness declaration

**My model family is Opus (Claude). The kit under test was authored by a
different Claude model.**

**Repo files read: none.**

Commands run outside the two allowed `blindplay observe` / `blindplay act`
forms, all through the Bash tool:

1. `python -m understudy.embark --character KLEEMOD-KOKOMI --lane 1` — the
   embark the coordinator instructed me to run.
2. `mkdir -p` twice — created
   `review/qa/kokomi-round-11-2026-09-04/` and the scratchpad directory.
3. Shell text filters applied to the output of `observe`, to keep the repeated
   static glossary out of my context: `sed` (deleting the "Words on this
   screen" block, the italic footnote lines, the relic block and the potion
   block), `head`, `tail` (trimming `act` JSON to its last lines), and `grep -E`
   (pulling just the HP/Block/Energy lines once). These only ever removed text
   the bridge had already printed to me; they never added anything.
4. One `for i in 1 2 3; do ... done` shell loop, fight 1 turn 2, to issue three
   identical `play "Strike (1)"` calls, as the coordinator's notes permitted.

**One self-inflicted error, declared because it briefly misled me.** In fight 4
turn 4 my own `sed` pipeline swallowed the enemy block and printed "## The other
side" with nothing under it. I thought the Flyconid had died. It had not — it
was at 2 HP and telegraphing a lethal 16 into my Vulnerable. I re-ran a plain
`observe` to check before acting. That was my filtering, not the game's screen.

Tools used: **Bash** (all of the above) and **Write**, once, for this file. No
`harness state`, `scenario`, `staged_turn`, `soak`, or any other understudy
command was run. I did not tear the lane down.
