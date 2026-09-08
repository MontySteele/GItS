# Blind seat record — kokomi, lane 2, round 23

## Identity

- **Model / seat:** Opus (Claude Code subagent), blind TESTER seat, "opus-attack-act1".
- **Lane:** 2.
- **Run seed:** none printed. No screen I saw carried a seed.
- **Character:** not named on any screen I reached. I inferred a Hydro/jellyfish kit from the relic
  **Tamakushi Casket** ("Start each combat with the Bake-Kurage") and from every kit card printing
  `[Hydro]` and a `Plan` line. The character's own name was never printed to me.
- **Ascension:** not printed on any screen. The run opened at **HP 64/80** on the first combat screen
  (80 max, 64 current before a single fight), which is 80% of max — but I am reading that off the
  battle screen, not off an ascension label, because none was shown.
- **Act / boss:** act 1. The map named the act's boss: **Ceremonial Beast**. I did not reach it.
- **Actions accepted:** 106 of 120.
- **Termination reason:** action budget. At 106 accepted acts I had 14 left, which is not enough to
  finish another combat (my fights cost 10–20 acts each), so I stopped on the map at floor 10 rather
  than start a fight I could not finish. No refusal chain, no stall, no TOOL-BLOCKED screen. Wall
  clock was not close to 5400 s.
- **HP trajectory:** 64/80 (open) → 57 (fight 1) → 54 → 57 kept through fight 2 → 46 after the
  "Slowly Find an Exit" event (-8) → 44 (fight 3) → 38 (fight 4) → **62 after Rest (+24)** → 61 → 38
  (elite, took 23) → **78/80 after Ambergris** → **78/80 final**.
- **Gold:** 210.
- **Potions held at the end:** Potion of Binding (Apply 1 Weak and 1 Vulnerable to ALL enemies),
  Fruit Juice (Gain 5 Max HP). Spent during the run: Power Potion, Ambergris.
- **Relics at the end:** Tamakushi Casket; Neow's Sacrifice; Tingsha (whenever you discard a card
  during your turn, deal 3 damage to a random enemy for each card discarded); Tungsten Rod
  (whenever you would lose HP, lose 1 less).
- **Deck at the end** (reconstructed from the Enchant screen at floor 2 plus every card I added; no
  screen after floor 2 listed the whole deck, so this is my own bookkeeping, 22 cards):
  4× Strike, 4× Defend, Kurage's Oath, Slack Water, Feint, Ambush, Opening Gambit **(Sown)**,
  Opening Gambit (2nd copy, plain), Converging Tide, Scout Ahead, Pincer, Guilty (curse),
  Thoma — Crimson Ooyoroi, Thoma — Blazing Barrier, Kirara — Surprise Dispatch, Well Laid.
  Nereid's Ascension was a Power-Potion card and did not enter the deck.
- **Neow pick:** **Neow's Sacrifice** (procure 1 Ambergris, add 1 Guilty). I took it because an
  Ambergris — heal 50% max HP *and* an extra turn in combat — is the single largest thing on offer,
  and a curse that self-removes after 5 combats is a rented cost, not a permanent one. It paid: the
  extra turn is what killed the elite. Rejected: Fishing Rod (a random upgrade every 3 normal
  combats is slow), and **Lead Paperweight**, which I rejected partly on a defect — the row promised
  "Choose 1 of 2 Colorless cards" and the page itself said *"this option's own words promise a card
  and the feed carried no face for it — no rules text, no cost, no type — so this page can offer it
  by name only."* I will not blind-pick a card whose face does not exist on the screen.

---

## Fight 1 — Shrinker Beetle (40 HP)

**Turn 1** (HP 64, 3 energy). Played **Slack Water** on the beetle (4 damage, 1 Weak), then
**Strike**, then **Defend (1)**.
- Rejected: writing Slack Water as a **Plan** on the Bake-Kurage. Its Plan line is "Apply 1 Weak to
  ALL enemies" and there was exactly one enemy, so the Plan buys nothing the direct play doesn't,
  and costs a turn of delay. The Plan is a card that wants a second body on the board.
- Rejected: holding the third energy. The beetle's intent was `Strategic (DebuffStrong)`, so Block
  was worthless against it, but Defend costs nothing I had a use for.
- What I learned from the screen: the beetle went 40 → 34 on Slack Water alone. The card says 4.
  The other 2 is **Tamakushi Casket** firing off the Weak. That is the kit's first hidden line and I
  only found it by arithmetic; nothing on the play result said "Casket".

**Turn 2** (HP 64 → the beetle had applied **Shrink -1**: "While Shrinker Beetle is alive, you deal
30% less damage"). Wrote three Plans, in this order: **Scout Ahead**, **Kurage's Oath**, **Pincer**.
- This was the fight's real decision and it was made here, not on turn 3. Scout Ahead's Plan is
  "Draw 1 card for each Plan carried out **after this one**" — so writing it *first* and two more
  behind it makes it a 2-card draw, and writing it last makes it a blank. The ordering rule is
  printed and it is load-bearing. I wrote it first deliberately.
- Rejected: Kurage's Oath + Pincer + **Defend**, taking 2 damage instead of 7. I gave up 5 HP for
  the two cards, on the read that a 7-damage beetle is not the threat.
- Rejected: playing anything face-up. Under Shrink, Strike had *re-printed itself as "Deal 4
  damage"* (from 6) — the screen updates the face for the debuff, which is excellent — while the
  Plan lines still printed 7 and 3×3.

**Turn 3.** The carry-out log read: Scout Ahead 2 cards; Kurage's Oath 7; Pincer 9. **The beetle went
28 → 12, i.e. exactly 16 = 7 + 9.** Shrink took 30% off Strike and took *nothing* off the two Plans.
That is the largest thing I learned all round, and no screen says it. Then, with the printed faces
reading 4 / 4 / 4, I played **Strike (1)**, **Strike**, **Feint** for exactly 12 and the kill.
- Rejected: writing Ambush as a Plan for 12 next turn. The beetle was telegraphing 13 damage; the
  exact-lethal line was on the table and reading three shrunken 4s off the faces is what found it.
- This turn had an obvious answer, and that is the two-turn Plan setup paying off, not a dead turn.

---

## Fight 2 — Nibbit (45 HP)

**Turn 1** (HP 57). Played **Thoma — Crimson Ooyoroi** (for 2 turns, each Attack deals 5 Pyro to a
random enemy and gains 3 Block), then **Slack Water** on Nibbit, then **Strike**.
- The decision was made at the **draft**, one floor earlier: I took Thoma over **Change of Plans**
  ("The Bake-Kurage carries out your first Plan now. Exhaust."). Change of Plans is the answer to the
  kit's whole drawback — it converts the delay to zero — and I passed on it precisely because Thoma
  is the only **second element** I had seen, and the screens spend a whole paragraph on Elemental
  Reactions I had no way to reach with Hydro alone. I wanted to see whether the reaction was real.
- It was real, and the screen hid it: Nibbit went 45 → 32 on Slack Water, i.e. **13**. The parts are
  4 (card) + 2 (Casket off the Weak) + 5 (Thoma's Pyro) = 11. The extra 2 is the Pyro hit landing
  into the Hydro aura Slack Water had just applied: 5 × 1.5 = 7. **Nothing on that screen named
  Vaporize.** I worked it out from a subtraction.
- Rejected: writing Ambush as a Plan (12 next turn). Thoma is a 2-turn window, and spending both of
  its turns on Attacks is worth more than banking one Plan.

**Turn 2.** Now the screen *did* print it, on the card face:
`*Reaction preview: Vaporize* — The triggering hit deals 1.5x damage and consumes the aura. Into that
Pyro aura this card's 6 lands 9.` Played **Feint** (9) then **Strike (1)**; Nibbit 21 → 7 → dead.
- Rejected: **Opening Gambit** as a Plan to set up a doubled Plan. Nibbit was at 21 into a hand that
  could deal 36, and it was telegraphing a Block on its own turn — a Plan carries out *before* I can
  play anything and lands into whatever Block the enemy is standing in, which the Bake-Kurage panel
  says outright. Killing through 0 Block now beat killing through its Block later.
- **Where screen and outcome disagreed:** they did not, here. The reaction preview is a genuinely
  good piece of writing — it prints the *resolved* number ("this card's 6 lands 9") on the card that
  will do it. My complaint is only that it appears one turn after the reaction it describes first
  happened; on the turn the aura was applied *by my own play*, no preview existed.

---

## Fight 3 — Leaf Slime (S) 12, Leaf Slime (M) 33, Twig Slime (S) 8

**Turn 1** (HP 46). Wrote **Opening Gambit (Sown)** as a Plan, then **Pincer** as a Plan, then played
**Strike** on the Twig Slime, then **Defend**.
- This is the turn the kit finally clicked. Opening Gambit's Plan is "Apply 1 Vulnerable to ALL
  enemies. **The next Plan deals double damage.**" With **Sown** on it (from the Sapphire Seed event
  — I took "Plant and Nourish" over 9 HP + an upgrade, because energy is what caps how many Plans you
  can write in a turn), writing it cost me nothing: energy stayed at **3/3** after I wrote it. Sown
  refunds on a *Plan write*, not only on a face-up play. That is not stated anywhere; I checked it by
  observing the energy line.
- Rejected: playing Pincer face-up on the Twig Slime to kill it (3+3 = 6 into 8 HP — not even a
  kill). Rejected: Converging Tide, which was not in hand this turn.
- The three-enemy board is what made the Plan line right, and that read was the decision.

**Turn 2.** The carry-out log is worth quoting in full, because it is the best screen in the game:
```
- Bake-Kurage: Opening Gambit, 1 — the 1 is Vulnerable. Inside the same beat:
  Tamakushi Casket 3 on Leaf Slime (S), Tamakushi Casket 3 on Leaf Slime (M),
  Tamakushi Casket 3 on Twig Slime (S).
    Leaf Slime (S) lost 3 HP / Leaf Slime (M) lost 3 HP / Twig Slime (S) lost 2 HP, and died
- Bake-Kurage: Pincer, 9 — the 9 is damage; the clause asked for 3.
    Leaf Slime (S) lost 9 HP, and died
    Leaf Slime (M) lost 18 HP
```
Three things I could not have known and now do: the Casket hit for **3, not 2**, because the
Vulnerable it was answering had already landed *inside the same beat*; Pincer's 3 became **9** (×2
from Opening Gambit, ×1.5 from Vulnerable) and the log says so explicitly — *"the 9 is damage; the
clause asked for 3"*; and the surplus hits of a multi-hit Plan **carry over to the next body** when
the front one dies (Leaf Slime M ate two of Pincer's three hits). One 1-energy Plan write killed two
enemies and took a third to 12/33.

Then **Feint** (9, Vulnerable) + **Strike (1)** (9) finished Leaf Slime (M).
- Rejected: nothing meaningful — the fight was decided on turn 1, and the fact that turn 2 was
  arithmetic is the plan paying off.

---

## Fight 4 — Snapping Jaxfruit (33 HP), Flyconid (48 HP)

**Turn 1** (HP 44, no Plan card worth banking — hand was Slack Water and four basics). Played
**Slack Water** on Flyconid, **Strike** on Flyconid, **Defend**.
- Rejected: writing Slack Water's Weak-ALL Plan. Weak applied *now* cuts Flyconid's telegraphed 11
  down to 8 on the turn it lands; written as a Plan it arrives a turn late, and this hand had no
  payoff to bank it for. This is the one card in the kit where "play it or plan it" genuinely
  flipped between fights on the board state, and that is a good card.
- Rejected: two Strikes + Slack Water for 18 damage and eating 14. 81 enemy HP is not a race I win
  from 44 HP.
- Took 6. Jaxfruit spent its turn on **Strength 2** and its attack went 3 → 5. It grows.

**Turn 2.** The combo turn. Wrote **Opening Gambit** as a Plan, wrote **Feint** as a Plan, played
**Kirara — Surprise Dispatch** (8 Block, 10 damage next turn).
- I did the arithmetic on the screen before committing and it came out exact: Casket 2 × 1.5 = 3, and
  Feint's Plan 10 → ×2 (Opening Gambit) → 20 → ×1.5 (Vulnerable) = 30. 3 + 30 = **33 = Snapping
  Jaxfruit's exact HP.** The log confirmed it: `Bake-Kurage: Feint, 30 — the 30 is damage; the clause
  asked for 10. Snapping Jaxfruit lost 30 HP, and died.` This is the most satisfying thing I did all
  round, and it was legible *in advance* — every multiplier is printed on some card on the screen.
- Rejected: **Converging Tide** (4 Block, aim queued Plans at a chosen enemy). Jaxfruit was already
  the front, so the redirect was redundant; the 1 energy went to Kirara instead. Converging Tide's
  only job is aiming Plans off the front, and I never once needed it in five fights.
- Kirara's delayed 10 also landed into the Vulnerable for **15**, which I had not planned for.

**Turn 3.** Flyconid at 18, Vulnerable 1, telegraphing 12 + a debuff. Played **Opening Gambit**
face-up (5 → 7, and Sown made it free), **Strike** (9), **Ambush** (7). Dead.
- Rejected: writing Opening Gambit + Ambush as Plans for a doubled 12 → 36 next turn. I would have
  eaten 12 to set up damage I no longer needed. The kit's constant question is "is this body dying
  this turn, or next?", and it is a real question every time.

---

## Fight 5 (Elite) — Bygone Effigy (127 HP)

A different fight from the other four, and the interesting one.

`Slow 0 (debuff) — Whenever you play a card, this enemy receives 10% more damage from Attacks this
turn. It counts the cards played BEFORE this one.` **Slow resets to 0 at the start of every turn**,
and Plans are carried out *before you play anything*. So against this enemy the Plan engine is
worth its printed number and nothing more, while a face-up hand is worth up to +30%. The kit's
best line is turned off by one enemy's printed rule. That is good design and it was legible from
the intent panel on turn 1.

**Turn 1** (HP 62, the Effigy asleep). Played **Thoma — Crimson Ooyoroi** first (a Skill — spends a
card on the Slow counter without wasting an Attack on a low multiplier), then **Slack Water**, then
**Strike**. 127 → 102.
- Rejected: opening with Strike. Playing the cheapest non-Attack first and the Attacks last is the
  whole puzzle this enemy sets, and it is stated on its own debuff line.

**Turn 2.** Slow back to 0. Played **Pincer**, **Feint**, **Strike** — all Attacks, ascending Slow,
each one also firing Thoma's 5 Pyro. 102 → 63 (39 in a turn). The Hydro/Pyro alternation is a small
engine on its own: my Hydro card applies an aura, Thoma's Pyro proc Vaporizes it for ×1.5, the proc
leaves a Pyro aura, the next Hydro card Vaporizes *that*. Two of my three cards had a
`Reaction preview: Vaporize` line on them by then, so this was visible, not guessed.
- Rejected: **Kurage's Oath** (a Skill — no Thoma proc, and 3 damage on a single target).

**Turn 3.** The Effigy had taken **Strength 10** and telegraphed **23**. Played
**Thoma — Blazing Barrier** (6 Block, +3 whenever it absorbs), **Kirara** (8 Block), **Defend** (5)
= 19 Block, and used **Power Potion**.
- Rejected: Ambush for 7 damage while eating 18. At 62 HP against a 127-HP body with growing
  Strength, the fight is a stamina fight and I chose to bank tempo.
- Power Potion offered **Nereid's Ascension** (cost 2, power: *"At the start of your turn, the
  Bake-Kurage carries out every Plan twice"*), **The Clouds Like Waves Rippling**, and **The
  General's Banner**. I took Ascension without hesitating; free to play that turn, it doubles the
  engine I had spent four fights learning. I took **1** damage that turn — Blazing Barrier's regrowth
  ate the rest of 23.

**Turn 4.** Wrote **Opening Gambit** as a Plan, played the *other* **Opening Gambit (Sown)** face-up
for 5, then two **Strikes** last for the Slow bonus. 53 → 28 across the beat.
- Rejected: writing both Opening Gambits as Plans. I did write one, and the log shows the cost of
  that mistake plainly:
```
- Bake-Kurage: Opening Gambit, 1 — the 1 is Vulnerable. ... Bygone Effigy lost 3 HP
- Bake-Kurage: Opening Gambit, 1 — the 1 is Vulnerable. ... Bygone Effigy lost 3 HP
```
  Nereid's Ascension carried the one Plan **twice** exactly as printed — but "the next Plan deals
  double damage" fired twice with **no damage Plan behind it**, so both doublings evaporated. I had
  no damage Plan in hand and wrote the setup anyway. That is my error, not the kit's, and the
  doubling is silent when it is wasted: nothing warned me, and nothing in the log says a doubling
  went unused.

**Turn 5.** Effigy at 28, Vulnerable 2, hitting for 23; me at 38. Played **Kurage's Oath** (a Skill,
cheapest, first — to start the Slow counter), then **Opening Gambit**, then **Strike** last: 4 + 8 +
10 = 22, leaving it on **6** and me one card short of lethal. Then **Ambergris**: healed to 78/80 and
**took an extra turn** — the screen stayed on "round 5", energy went back to 3/3, a fresh hand
appeared, and the Effigy never acted. Played **Ambush** (5 × 1.5 = 7) for the kill.
- Rejected: Defend and surviving into turn 6. At 38 HP against 23 a turn with the enemy at 28, I was
  two turns from dying and one potion from winning. This was the sharpest decision of the run and it
  was made on a potion, not a card.
- Rewards: 28 gold, Potion of Binding, **Tingsha**, and **Well Laid** (cost 0 attack, *"Deal 2
  damage... plus 3 for each Plan the Bake-Kurage carried out at the start of this turn"*) — a card
  that finally pays the Plan count itself. Then the Treasure chest gave **Tungsten Rod**.

---

## The kit, after 5 fights

**(a) Which decisions felt like real choices, and what they traded off.**

1. **Play it now, or write it as a Plan** — *on the turn, every single turn.* This is the kit's
   spine and it is a good one, because the Plan line is not a strict upgrade: it is bigger (Feint 6
   → 10, Ambush 5 → 12, Kurage's Oath 3-ALL → 7-ALL) but it arrives a turn late, it lands into
   whatever Block the enemy is standing in, and it takes the front body rather than the one you
   want. In five fights I chose both ways and both were right at least once — Slack Water in fight 4
   turn 1 wanted to be played, and in fight 3 turn 1 the same class of card wanted to be written.
2. **The order you write Plans in** — *on the turn.* Scout Ahead ("draw 1 for each Plan carried out
   **after this one**") and Opening Gambit ("**the next** Plan deals double") both key off queue
   position. In fight 1 turn 2 I wrote Scout Ahead first on purpose and got 2 cards; written last it
   is a blank. This is a decision inside a decision and it is the best thing in the kit.
3. **Card sequencing inside a turn** — *on the turn, in the elite only.* Bygone Effigy's Slow
   inverts the kit: Plans resolve at Slow 0, face-up Attacks last resolve at +30%. One enemy that
   turns the character's main engine off, legibly, from its own printed debuff line.
4. **Aura sequencing** — *on the turn, once I had a Pyro source.* Alternating a Hydro card with
   Thoma's Pyro proc Vaporizes on both sides. This only exists if the draft handed you a second
   element, which makes it...
5. **The draft picks that shaped whole fights** — *at the draft.* Thoma over Change of Plans (fight 2
   is entirely that pick), Sown onto Opening Gambit rather than a Strike (fights 3, 4 and the elite
   all leaned on Opening Gambit being effectively free), and the second Opening Gambit over Diona.

**(b) What felt automatic, and what never seemed worth playing.**

- **Defend** was automatic every time: play it when the intent is an Attack and you have spare
  energy, never otherwise. Fine, but it is filler.
- **Converging Tide** (4 Block; queued Plans aim at this enemy instead of the front) never got
  played. In five fights the front body was always the one I wanted the Plan on, or the multi-hit
  overflow reached the second body anyway. It needs a board where the back enemy is the priority,
  and act 1 never gave me one.
- **Kurage's Oath** face-up (3 damage to ALL) is weak enough that I only ever played it as a
  Slow-counter body or wrote it as a Plan. Its Plan line (7 to ALL) is the real card.
- The end of fights 1 and 3 were automatic — but in both cases that was a Plan written two turns
  earlier arriving, which is the payoff, not a dead turn.
- **Guilty** did nothing but sit in my hand, which is what it says it does.

**(c) What I could not understand, or that contradicted its own printed text.**

- **Shrink did not touch Plan damage and nothing says so.** With `Shrink -1` on me ("you deal 30%
  less damage with every hit you land"), Strike re-printed as 4 (from 6) — good — but Kurage's Oath's
  Plan and Pincer's Plan landed for exactly their printed 7 and 9. Either "every hit you land" is
  false for a carry-out, or the Plan is not my hit. The Bake-Kurage panel does say *"Every planned
  HIT is the jellyfish's"*, so this is probably intended — but the interaction is invisible until
  you subtract, and it is a 30% swing on the character's main damage.
- **Tamakushi Casket is silent when you play a card face-up.** Slack Water printed "Deal 4 damage"
  and dealt 6, twice, in two different fights, before I worked out the Casket was answering the Weak.
  The *carry-out log* names the Casket explicitly and beautifully; the face-up play result does not
  name it at all. The two paths through the same relic have completely different legibility.
- **Reaction previews are one beat late.** The `Reaction preview: Vaporize ... this card's 6 lands 9`
  line is excellent — but it only appears once an aura is already on the body. On the turn where my
  own card applies the aura and my own Thoma proc reacts with it in the same beat, nothing previews
  it, and the extra damage arrives unexplained. The screen even warns about exactly this class of
  hidden reaction in the Elemental Reaction glossary, which suggests it is known.
- **`Gain [Energy]` is a literal unfilled placeholder.** The Sown enchantment prints
  *"The first time you play this card each combat, gain [Energy]."* — square brackets and all, on
  both the card face and the keyword line, every time. It is 1 energy. That is a text defect.
- **A wasted "next Plan deals double" is silent.** I fired two of them with no damage Plan behind
  them and no screen said anything, before or after.
- **"The 9 is damage; the clause asked for 3"** is the log doing something genuinely hard well —
  but the same log's first line, `Pincer, 3 — the 3 is damage` (fight 1), sat above `lost 9 HP`, and
  I had to read the footnote to understand the header figure is the *first clause*, not the total.
  Two adjacent numbers meaning different things is the one place the log fights itself.
- **The character is never named.** No screen I reached printed the character's name or an ascension
  level.
- **Lead Paperweight at Neow offered a reward whose card faces did not exist** (the page said so
  itself). I could not evaluate it, so I could not pick it.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** Converging Tide. Four Block and a redirect I never needed; it is a 1-energy tax
  on a turn where every energy wants to be a Plan write. (Guilty is worse but it is a curse and
  that's the point.)
- **Happiest to draw:** **Opening Gambit**, by a distance, and it is not close. "Apply 1 Vulnerable
  to ALL enemies. The next Plan deals double damage" is the card that makes every other Plan card
  interesting: it turned Pincer's 3 into 9 three times over, turned Feint's 10 into an exact 33-point
  execution on Snapping Jaxfruit, and it triggers the Casket on every body on the board as a
  side-effect. Taking a second copy was the easiest draft pick of the run. Honourable mention to
  **Scout Ahead**, which is a 1-energy cantrip whose Plan line is a puzzle piece.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, but a thin one.** The choice was Slack Water face-up versus Slack Water written as a Plan, and
the board answered it immediately: one enemy, and the Plan line is "Apply 1 Weak to **ALL**
enemies", so the Plan is strictly worse. The kit's central question was on screen on turn 1 — that is
more than most opening turns manage — but it had a forced answer. The first turn that presented a
*live* decision was turn 2 of fight 1, where the queue-order rule (Scout Ahead first or last) and the
tempo trade (5 HP for 2 cards) both had two defensible answers.

---

## Non-blindness declaration

Commands run outside `blindplay observe` / `blindplay act`:

- `mkdir -p` twice, in one Bash call, to create
  `review/qa/kokomi-round-23-2026-09-07/` and the session scratchpad directory.
- `sed -n` and `head`/`tail`/`grep` filters piped onto the output of `blindplay observe` and
  `blindplay act`, purely to re-read one block of a screen I had already been shown (the enemy
  panel, the hand, the Bake-Kurage panel, the carry-out log) without reprinting the whole page.
  Every one of these operated on the bridge's own output and on nothing else.
- `cd` into the repo root as the prefix of each Bash call.

Tools used: **Bash** (the two blindplay commands, plus the mkdir and the output filters above) and
**Write** (once, for this file).

I ran no `harness state`, no `scenario`, no `staged_turn`, no `soak`, and no other understudy
subcommand.

**Repo files read: none.**
