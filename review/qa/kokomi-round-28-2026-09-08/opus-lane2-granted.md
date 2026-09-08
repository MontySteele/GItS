# Kokomi round 28 — blind seat, lane 2 (granted arm)

## Identity

- **Model and seat:** Opus 5 (claude-opus-5[1m]), blind TESTER seat, lane 2, "granted" arm
  (starting deck carried two extra cards for this round: **Read the Field** and **Scout Ahead**).
- **Run seed:** not printed on any screen the bridge showed me. The map page, the Neow page
  and the run-over page all print floor, act, gold and relics; none of them printed a seed,
  so I cannot report one.
- **Character:** Kokomi (Bake-Kurage / Plan kit, Hydro).
- **Ascension the run opened at:** not printed either. The first battle screen opened at
  **HP 64/80**, i.e. already below full at floor 2 before anything hit me, so the run opened
  on an ascension that starts you under max HP; the bridge never named the number.
- **Act and boss:** Act 1, and the map named the act's boss on the very first map screen:
  **Waterfall Giant**.
- **Actions accepted:** **210 of 240**.
- **Termination reason:** not a budget. **The run ended — I died** on floor 17 to the
  Waterfall Giant's phase-two Death Blow. The bridge answered my `end turn` with
  `TOOL-BLOCKED: game_over` / "the run is over; there is nothing left to play". I had 30
  accepted acts and most of the wall clock still in hand.
- **HP trajectory:** 64/80 (start of fight 1) → 49 → 37 → 31 → 27 (floor 5) → **rest 51** →
  43 → 38 → 32 (floor 9) → **rest 56** → 47 → 43 → 38 → 29 (floor 13) → **rest 53** →
  boss: 53 → 43 → 30 → 29 → 28 → 25 → **0/80**.
- **Gold at the end:** 177.
- **Potions held at the end:** Vulnerable Potion. (Spent during the run: Powdered Demise on
  the Fossil Stalker, Blessing of the Forge on the boss's last turn.)
- **Relics at the end:** Tamakushi Casket (starting), Booming Conch (Neow), Lantern (floor-10
  chest).
- **Deck at the end** (reconstructed from hands and piles; no screen prints a deck list —
  the map page says so in as many words, "This page cannot say what is in your deck yet"):
  Strike ×4, Defend ×4, Kurage's Oath, Slack Water, **Read the Field** (granted),
  **Scout Ahead** (granted), Undertow, Riptide, Exposed Flank, Coral Bulwark, Ambush ×2,
  Vanguard, Ripple ×2, Gorou — Inuzaka All-Round Defense, Spoils Map (unplayable). 23 cards.
  Counts check out against the boss fight's own piles (18 draw + 5 hand at round 1).

**Neow pick: Booming Conch** ("At the start of Elite combats, draw 2 additional cards and gain
Energy"). I took it because the other two both cost me something I could not price blind —
Winged Boots is map freedom I had no map knowledge to spend, and Neow's Sacrifice buys a heal
by putting a Guilty in a deck I had not yet seen a single card of. The Conch is the only one
that is pure upside. In the event it never paid a single time: **the run reached no Elite**,
because every path the map offered me from floor 11 on ran Monster/Unknown/RestSite into the
boss. That is a real finding about the pick and not about the relic.

---

## Fight 1 — Corpse Slug (1) 27 HP / Corpse Slug (2) 26 HP

Both wore `Ravenous 4` — "When an enemy dies, Corpse Slug immediately eats it, becoming
Stunned and gaining 4 Strength." That line is the whole fight, and it is legible: it tells you
that a kill is a tempo purchase, +4 Strength for a skipped enemy turn.

**Turn 1** (HP 64, 3 energy). Played **Read the Field** first, then wrote **Kurage's Oath**
on the Bake-Kurage, then Defend.
Rejected: playing Oath face-up for "3 damage to ALL" now. The card prints
"Plan: Deal 7 damage to ALL enemies" against a face-up 3, so writing it more than doubles it
for the same energy and the slugs' 14 incoming was survivable behind one Defend. That is a
real decision and it is made entirely off the printed face.

**Turn 2** (HP 55; the Plan had resolved for 7 apiece, both slugs at 20/19 and both wearing a
Hydro Aura). Played Slack Water on A, then two Strikes on A.
Rejected: two Defends for 10 Block, which would have fully eaten A's 8. I turned it down
because I wanted A dead next turn specifically to *hand B the Stun* — the Ravenous line means
the kill buys me a free enemy turn, which is worth more than the 6 HP the Defends save.
That is the fight's one interesting choice and the enemy's own text set it up.

**Turn 3.** Played Oath face-up for 3-to-ALL to kill A at exactly 2 HP, then two Strikes into B.
Rejected: writing Oath as a Plan again for 7. Turned down because the 3 face-up killed A *now*,
and the Stun that bought was worth more than 4 extra damage a turn later. The screen then
printed exactly what it had promised: B at 4 HP, `Intent: Stunned`, `Strength 4`.

**Turn 4.** One Strike, lethal. No rejected alternative — but this was the Turn-3 plan paying
off, not a dead turn.

**Verdict on the fight:** three of four turns carried a real decision, and each one was a
timing question the printed text posed (now vs. next turn; kill vs. block).

---

## Fight 2 — Sludge Spinner 37 HP

**Turn 1.** Slack Water on A, Strike on A, wrote **Kurage's Oath** as a Plan.
Rejected: a second Strike instead of writing the Plan. The Plan's 7 beats a Strike's 6 for the
same energy; I paid a turn of delay for one damage and for the Hydro aura, and against a single
37 HP body the delay was cheap.

**Turn 2 — a refusal, and it cost me the turn.** I asked for `play "Riptide" on "A"`. The
bridge refused:

> `'Riptide' does its own aiming, so it takes no on "A". The form that resolves: play "Riptide"`

I had batched the turn's commands, so the refusal ate the Riptide and I ended the turn having
played only a Defend. **This is a finding twice over.** Once against me: a batched turn is a
bad idea against a parser that refuses on aiming grammar. And once against the surface: Riptide
prints "Deal 9 damage to ALL enemies" and *every other* damage card in the kit takes `on "<enemy>"`,
so the one card that refuses a target is the one whose text does not say it aims itself. The
refusal message is excellent — it names the working form — but the card face gives no warning.

Also this turn: my Strikes printed **4** and Riptide printed **6** rather than 6 and 9, because
I was carrying Weak 1. The screen folding my own Weak into the printed card numbers is genuinely
good and I trusted it immediately.

**Turn 3.** Exposed Flank on A, then Undertow on A — dead.
The arithmetic was fully readable off the face: Exposed Flank applies 1 Vulnerable, which sets
off `Tamakushi Casket` for 2 Hydro damage, and that 2 is itself boosted by the Vulnerable it
just applied → 3. Then Undertow, "Deal 7 damage. If the enemy has a debuff, deal 10 instead",
at 10 × 1.5 = 15. 3 + 15 = 18 on a body at exactly 18. **The screen and the outcome agreed to
the point.**
Rejected: two Defends. Turned down because the Vulnerable/Undertow line was exactly lethal and
I could count it before committing.

---

## Fight 3 — Seapunk 45 HP

**Turn 1.** Exposed Flank on A, Strike on A, Defend.
Rejected: writing **Coral Bulwark** as a Plan (8 Block and 1 Weak) instead. Turned down because
Vulnerable falls off at the end of *its* turn — "One stack falls off at the end of each of its
turns" — so a Vulnerable applied on my turn only multiplies cards I play *that* turn. That
printed clause is what decided the turn: it makes Exposed Flank a *now* card and rules out
saving it. 12 damage dealt, exactly as computed (3 + 9).

**Turn 2.** Slack Water, Undertow, Strike — all into A. 22 damage.
Rejected: swapping the Strike for a Defend. Turned down because Slack Water's Weak had already
cut the incoming 2×4 to ~4, so the Defend was buying almost nothing.

**Turn 3.** Two Strikes for lethal at 11 HP. No alternative — the payoff of turn 2.

---

## Fight 4 — Living Fog 80 HP (+ Gas Bomb 7 HP, summoned)

The best fight of the run, and the one where the Plan system actually sang.

**Turn 1.** Wrote **two Ambushes** on the Bake-Kurage, then played Undertow face-up.
Rejected: playing both Ambushes face-up for 5 each. Ambush prints "Deal 5 damage.
Plan: Deal 12 damage" — writing them is 24 against a face-up 10 for the same 2 energy. Against
an 80 HP body with nothing but a chip attack telegraphed, taking one turn of 8 to bank 24 was
not close. The Bake-Kurage's own page had already told me the jellyfish "holds any number of
Plans", so I knew stacking two was legal before I tried it.

**Turn 2.** The Fog had put `Smoggy 1` on me — "You can only play 1 Skill per turn" — which is
a direct attack on this kit, since Plans are *written by playing the card* and most of my
writers are Skills. That is a good, legible counter and it changed the turn: I spent my one
Skill on **Vanguard** (0 cost, Apply 1 Vulnerable, Exhaust), then poured three Attacks through
the Vulnerable: Slack Water, Strike, Strike. 49 → 19, exactly the 30 I had counted (3 + 9 + 9 + 9).
Rejected: spending the Skill slot on writing another Plan. Turned down because Vulnerable is a
*this turn only* multiplier and I had three Attacks in hand to push through it.

**Turn 3.** Riptide (auto-aimed, this time I knew) killed the Gas Bomb before its Death Blow
could land and left A at 10; Strike took it to 4.
Rejected: writing Kurage's Oath as a Plan. Turned down because killing the Gas Bomb *now* is
what cancels its "attack you for 8 damage before being destroyed" — a fact I only learned by
doing it, and which mattered enormously ten fights later.

**Turn 4.** Strike for lethal.

---

## Fight 5 — Two-Tailed Rat ×3 (17 / 21 / 18 HP)

**Turn 1** (4 energy, Lantern now in play). Vanguard on A → Strike on A → Ambush face-up on A,
which killed A for exactly its 17 (3 + 9 + 7 through the Vulnerable); then wrote
**Exposed Flank** as a Plan and played a Defend.
Rejected: Exposed Flank face-up on B. Turned down for the same Vulnerable-decays reason — B was
not going to be attacked by me this turn, so a face-up Vulnerable on it was 3 damage and nothing
else, whereas the Plan line reads "Apply 2 Vulnerable to ALL enemies" and lands them *at the
start of my next turn*, where they do multiply everything. This is the sharpest thing the Plan
system does: it moves a debuff from the wrong side of the turn boundary to the right side.

**Turn 2.** Wrote **Kurage's Oath** as a Plan, then wrote **Scout Ahead** as a Plan, then Strike
into C.
Rejected: Coral Bulwark for 4 Block instead of writing Scout Ahead. I paid 4 HP for two cards,
and the order mattered — see the Debrief.

**Turn 3.** The Plan killed C outright (7 × 1.5 through the Vulnerable = 10). B at 8; Undertow
finished it.

---

## Fight 6 — Haunted Ship 63 HP

**Turn 1.** Wrote **Vanguard** as a Plan *first*, then **Ambush** as a Plan, then Strike face-up.
Rejected: playing all three face-up for 3 + 7 + 9 = 19. Turned down because the enemy's
telegraph was "apply a Debuff" and "give you 5 Status cards" — *no damage at all* — so a turn
spent banking cost nothing. Writing Vanguard before Ambush means the Vulnerable lands before
the 12 does. The next screen showed 63 → 33: **30 damage in one carry-out beat**, off 2 energy.
That is the kit's ceiling and it felt like a genuine payoff for two turns of setup.

**Turn 2.** Riptide face-up (15 through the Vulnerable), Strike, and wrote **Ripple** as a Plan.
Rejected: Ripple face-up for 2 Block. Its Plan line is "Gain 1 Energy and 4 Block" for a 0-cost
card — more block *and* an energy, one turn later. It duly showed up next turn as Block 4 and
Energy 4/3.

**Turn 3 — the only Elemental Reaction of the run.** Gorou — Inuzaka All-Round Defense carried
a line I had not seen before:

> *Reaction preview: Crystallize* — Geo meets an aura: the aura is consumed and you gain 4 Block.

I played it into the Ship's Hydro Aura and my Block went 4 → 11 (6 damage dealt → 3 Block, plus
4 Crystallize). Preview, rule and outcome all matched. Then Exposed Flank + Undertow for lethal.

---

## Fight 7 — Fossil Stalker 51 HP

`Suck 3` — "Whenever Fossil Stalker deals unblocked attack damage, it gains 3 Strength." Another
enemy whose text names the whole problem.

**Turn 1.** Slack Water on A (its Weak drops the telegraphed 12 to 9), Strike, then two Defends
for 10 Block — 10 ≥ 9, so **zero unblocked damage and no Strength gained**. The decision here
was made purely by reading two numbers off two screens and noticing they crossed.
Rejected: a third attack. Turned down because the whole fight is "never let it connect."

**Turn 2.** Used **Powdered Demise** ("Enemy loses 9 HP at the end of each of its turns"), then
Riptide, then Undertow. The Demise counts as a debuff, which turned Riptide's "and 4 more to
each enemy with a debuff" and Undertow's "if the enemy has a debuff, deal 10 instead" both on
at once. 39 → 5 in a single turn, and the arithmetic (2 Casket + 13 + 10 + 9) matched exactly.
Rejected: blocking instead. Turned down because the Suck escalation means a long fight is a
lost fight; I ate 9 to end it two turns early.

**Turn 3.** Strike, lethal.

---

## Fight 8 — Waterfall Giant, 240 HP (act 1 boss) — the fight that killed me

Thirteen rounds. I will not narrate all of them; the shape is what matters.

`Steam Eruption 15 (buff) — When killed, deals 15 damage at the end of your next turn.` It grew
**+3 every single round** — 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 — printed plainly on the
screen the whole time. That is the fight's real clock, and it is beautifully legible: the boss
tells you, from round two, exactly how much the kill is going to cost and exactly how fast that
price is rising. My problem was that nothing in my deck could pay it.

- **R1** (boss telegraphs a Buff, no damage): wrote Exposed Flank then Ambush as Plans, played
  Undertow and Strike face-up. Rejected the all-face-up line (36 now) in favour of 13 now + 21
  next, because a turn with no incoming damage is free banking time. 240 → 206.
- **R2:** Gorou (12 damage, 10 Block via half-damage + Crystallize), Coral Bulwark for 6 more —
  16 Block against a telegraphed 15, so **0 taken** — and wrote Kurage's Oath as a Plan.
  Rejected: Defend + Oath face-up. Turned down because Gorou's Crystallize was free block that
  only existed while the aura was up.
- **R3:** Vanguard face-up (Vulnerable 2), Riptide (15), and **wrote Read the Field for its 10
  Block** rather than taking the look. Here the screen and the outcome **disagreed by one**:
  Vanguard 3 + Riptide 15 should have read 184 → 166, and the next screen said **167**. One
  point. I could not tell from any printed text whether Weak is applied before or after the
  Vulnerable multiply, and the page itself warns it cannot break a number down
  ("the feed carries no base, no modifier list and no breakdown"). It is one point, but it is
  the only time in eight fights my arithmetic missed.
- **R4:** the boss **healed 10** (167 → 157 → shown as 159 after my 18). A 240 HP boss that
  heals and escalates its own death-explosion is a damage-race check the kit failed.
- **R5–R8:** I ran the block engine — Ripple ×2 as Plans for +2 energy and 8 Block, Read the
  Field as a Plan for 10 Block, Coral Bulwark as a Plan for 8 Block and a Weak — and took 0, 0,
  1 and 1 damage across four rounds while grinding 133 → 76. **The Plan system as a defensive
  engine works well**, and the +1-energy Ripple Plan is the best card I drafted all run.
- **R9 (boss healing again):** all-in — Undertow face-up, Ambush and Oath as Plans. 76 → 43.
- **R10–R11:** Slack Water's Weak cut a telegraphed 25 to 18 and a 13 to 10, both fully blocked.
  22 → 4.
- **R12:** Strike for what I thought was lethal. Instead the screen printed
  **`Waterfall Giant [A] — changing phase (its HP is not a number this turn)`**, `Intent: Stunned`.
  A second phase I had no way to know about. I spent the free stunned turn writing Exposed Flank
  and Kurage's Oath as Plans.
- **R13, the kill turn.** The phase body telegraphed `Death Blow — 45`. I had 25 HP, 3 energy
  and no healing anywhere in the deck. I played **Scout Ahead face-up first** (so the card it
  drew would be caught by the potion), then used **Blessing of the Forge** to upgrade the whole
  hand, then **Gorou+** — 16 damage, 8 Block from half-damage, 4 Block from Crystallize, Block 12.
  The last energy was the run's real decision: **Defend+ for 8 more Block (total 20, taking
  45 − 20 = 25 into exactly 25 HP — arithmetically certain death), or Undertow+ for 19 damage on
  the chance the phase body's hidden HP was low enough to die first**, which I had *seen* work
  when Riptide killed the Gas Bomb before its Death Blow in fight 4. I took the gamble, because
  the safe line was provably lethal and the gamble was not. It was not enough. 45 − 12 = 33 into
  25 HP.

**Where the screen and the outcome disagreed, plainly:** nowhere fatal, but twice worth writing
down. (1) The one-point Riptide discrepancy in R3. (2) `changing phase (its HP is not a number
this turn)` — I do not blame the bridge, which says exactly what it knows, but it means the
last two rounds of the act-1 boss are played with the single most important number hidden, and
the choice I lost on was precisely a bet about that number.

---

## The kit, after 8 fights

**(a) Which decisions felt like real choices, and what they traded off.**

- **Face-up or Plan, every single turn, on almost every card** — made *on the turn*. This is the
  kit's whole identity and it is a good one. Ambush is 5 now or 12 next; Kurage's Oath is 3-to-all
  now or 7-to-all next; Read the Field is a look now or 10 Block next; Ripple is 2 Block now or
  4 Block *and an energy* next. The trade is always the same shape — roughly double, one turn
  late — which makes it learnable, and the thing that keeps it from being automatic is that the
  enemy's telegraph decides which side is right. On a turn the boss telegraphed a Buff, writing
  was free. On a turn a Corpse Slug was at 2 HP, writing was a mistake.
- **Ordering the Plans within a turn** — made *on the turn*, and this is the subtlest good thing
  in the kit. "The jellyfish holds any number of Plans and carries them out in the order written"
  means Vanguard-then-Ambush is 18 damage and Ambush-then-Vanguard is 12. Same cards, same
  energy, different sequence. I used it deliberately three times (fight 6 R1, fight 5 R2, boss R7)
  and it paid every time.
- **Whether to buy a kill for its consequence** — made *on the turn*. Fight 1's Ravenous
  (kill = the other slug is Stunned) and fight 4's Gas Bomb (kill = its Death Blow never lands)
  are both decisions the enemy's own printed text creates.
- **Debuff timing against the Vulnerable decay rule** — made *on the turn*, but it is really a
  rule you learn once and then apply forever: Vulnerable applied face-up only helps this turn,
  Vulnerable written as a Plan helps next turn. Exposed Flank is two different cards depending
  on which you need.
- **At the draft:** taking Coral Bulwark over Razor's Electro at floor 4, and taking Ripple twice
  over bigger cards. The Ripple picks shaped every good turn of the boss fight; the Coral Bulwark
  pick I would make again and it still was not enough block.

**(b) What felt automatic, and what never seemed worth playing.**

- **Defend.** In a kit where Read the Field's Plan is 10 Block and Coral Bulwark's is 8-and-a-Weak
  for the same 1 energy, a flat 5 is what you play when you have a spare energy and nothing to
  spend it on. I never once *chose* a Defend over something; I filled with it.
- **Strike.** Same. Undertow is 7-or-10 for the same cost and Gorou is 8-plus-block. By floor 12
  the four Strikes were the worst cards in a 23-card deck and I had no removal.
- **Slack Water face-up** became automatic in the good way — it is nearly always right, because
  the Weak is mitigation *and* the Casket turns the debuff into free damage. "Automatic" here
  means "reliably correct", which is less of a problem than a card that is reliably ignorable.
- **Riptide face-up** was rarely worth 2 energy; its Plan (13-to-ALL) is where it lives.
- **Spoils Map.** Not the kit's fault — I took it at an event — but a 23-card deck with a dead
  0-cost in it draws it about once a fight and it never did anything.

**(c) What I could not understand, or that seemed to contradict its own printed text.**

- **The printed card numbers fold in some modifiers and not others, on the same screen.** With
  the boss at Vulnerable 2, Undertow printed "Deal 10 damage. If the enemy has a debuff, deal 15
  instead" (its 7/10 scaled by 1.5) and Gorou printed 12 (its 8 scaled) — but **Strike on the very
  same screen still printed 6, not 9, and Ambush printed 5, not 7**. My own Weak *is* folded into
  every card (Strikes printed 4). So: my debuffs are shown in the numbers, the enemy's Vulnerable
  is shown on some cards and not others. That is the one thing in eight fights I could not read
  off the screen and had to hold in my head, and it is exactly the kind of inconsistency that
  makes a player stop trusting the numbers.
- **The one-point gap in boss R3** (expected 166, screen said 167). Weak and Vulnerable interact
  in some order the page cannot show me.
- **`changing phase (its HP is not a number this turn)`.** Honest, and unplayable. I lost the run
  to a bet on a hidden number.
- **The Elemental Reaction block is enormous and, for seven of eight fights, entirely inert.**
  Every combat screen prints a ~150-word explanation of reactions ending in "NO REACTION IS
  REACHABLE HERE: Hydro is the only element this screen can supply." It is honest and it is a lot
  of text to read past. When a reaction *was* reachable, the *Reaction preview* line on the card
  did the whole job in one sentence. The preview line is excellent; the standing essay is not
  earning its space.
- **Riptide refusing `on "A"`** (see fight 2). Nothing on the card face says it aims itself.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** Defend. Not because 5 Block is bad, but because in this kit every other
  1-cost skill has a Plan line that makes it two cards, and Defend has none — it is the only
  card in the deck that cannot be pointed at the jellyfish, so it is the only card that never
  poses the kit's question. (Spoils Map was more useless, but I chose it and it is not kit.)
- **Happiest to draw: Ripple.** A 0-cost whose Plan reads "Gain 1 Energy and 4 Block". Writing
  it costs literally nothing and pays an energy — it is the card that made my 4- and 5-energy
  boss turns exist, and it is the clearest expression of what the Bake-Kurage is *for*.
  Honourable mention to Ambush (5 or 12 for one energy is the starkest version of the choice)
  and to Gorou, whose Crystallize preview was the one moment the elemental layer felt real.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a good one, twice over.** With three energy and Kurage's Oath, Read the Field, Strike
and two Defends in hand, the first turn asks (i) whether Oath is 3-to-both now or 7-to-both next
turn, against two slugs telegraphing 14 between them, and (ii) whether Read the Field is a look
or 10 Block. Neither has an obvious answer and both are answerable from the printed faces alone.
I never felt lost on turn one — the Bake-Kurage's own block of text explains the whole mechanism
before you spend anything, which is the right place for it.

---

## Debrief

**Turns I held Read the Field:** fight 1 R1 (played); fight 2 R3 (held, unplayed); fight 4 R3
(held, unplayed); fight 5 R3 (held, unplayed); fight 6 R2 (held, unplayed); boss R3 (written);
boss R6 (written); boss R11 (played).

**Read the Field, face-up — two occasions.**

1. **Fight 1, turn 1.** The three cards shown were **Strike (1)**, **Scout Ahead**, **Strike (2)**.
   I took **Scout Ahead**. Energy left after playing it: **2 of 3**. The take was **not** played
   that turn — I spent the remaining 2 on writing Kurage's Oath and a Defend, and Scout Ahead was
   discarded unplayed at end of turn. I took it over a guaranteed Strike deliberately: I wanted a
   second Plan card in hand to write alongside Oath, and taking a Strike I had no energy to play
   would have been the same nothing with less optionality. In hindsight it *was* the same nothing,
   because unplayed cards are discarded and I never got to pair them.
2. **Boss, round 11.** The three cards shown were **Ambush**, **Strike**, **Slack Water**. I took
   **Slack Water**. Energy left after playing it: **3 of 4**. The take **was** played that turn,
   immediately — and it was the right take for a reason the other two could not match: Slack Water
   applies Weak, which cut the Giant's telegraphed 13 down to 10, and 10 was exactly what my
   remaining Defend + Ripple + carried Block could absorb. I took **0 damage** that round. Ambush
   or Strike would each have dealt a couple more damage and cost me ~3 HP I did not have.

**Read the Field, written as a Plan — two occasions, both in the boss fight (R3 and R6). Why the
10 Block over the look:**

Because by then the fight had become a pure attrition problem and the look had nothing to find.
Concretely: at boss R3 I had 3 energy, and my third card was a choice between a face-up Defend
(5 Block) and Read the Field's Plan (**10 Block**) — same cost, double the block, one turn late,
against a boss that telegraphs its damage a full turn ahead so the delay is free information-wise.
At R6 the same reasoning applied and harder: I was at 30/80 against a 133 HP body whose
Steam Eruption was already at 30, and I was assembling a whole turn out of Plans (Riptide 13,
Read the Field 10 Block, Ripple +1 energy and 4 Block) so that the following turn would open with
14 Block and 4 energy. The look, by contrast, would have shown me three cards out of a 23-card
deck whose best contents I already knew — there was no card in that deck worth 10 Block to find,
because *Read the Field's own Plan was the best block card in the deck*. That is the honest
answer: I stopped using the granted look card as a look because its Plan line outclassed anything
it could have dug up.

**Scout Ahead.**

**Did I write it? Yes, twice** (fight 5 R2, boss R7), and I played it face-up once more (boss R13).

- **Fight 5, round 2.** Plans the Bake-Kurage carried out that morning, by my own count and
  **including Scout Ahead itself: 2** — Kurage's Oath, then Scout Ahead. **It drew 2 cards.**
  I counted it off the screen: the next turn's hand held seven cards (Slack Water, Defend ×2,
  Strike ×2, Read the Field, Undertow) where five is the normal draw.
- **Boss, round 7.** Plans carried out that morning, itself included: **3** — Kurage's Oath,
  Ripple, then Scout Ahead. **It drew 3 cards** — the following hand was eight cards deep
  (Ambush, Strike, Coral Bulwark, Defend ×2, Exposed Flank, Spoils Map, Riptide) against a normal
  five. The card scales exactly as printed and the count is easy to verify off the piles line.
- **Boss, round 13** (face-up, "Draw 1 card"): played *first*, deliberately ahead of the
  Blessing of the Forge potion, so that the card it drew would be inside the hand the potion
  upgraded. It drew a Strike, which the potion turned into Strike+. The sequencing worked.

**Every turn I held Scout Ahead alongside another Plan card, and which I wrote first:**

- **Fight 2, R2** — held with Riptide. **Wrote neither** (this was the turn Riptide's aiming
  refusal ate my actions and I ended up playing only a Defend). No ordering decision was made.
- **Fight 4, R2** — held with Vanguard and Slack Water, both Plan cards. **Wrote none of them**:
  `Smoggy 1` limited me to one Skill per turn, and I spent that one Skill on Vanguard *face-up*
  to get the Vulnerable multiplier onto three Attacks in the same turn. Scout Ahead lost the slot
  to a multiplier that was worth ~15 damage.
- **Fight 5, R2** — held with Kurage's Oath. **Wrote Kurage's Oath first, Scout Ahead second.**
  Reason: Scout Ahead's Plan reads "Draw 1 card for each Plan carried out **this turn**", and the
  Bake-Kurage "carries them out in the order written". Writing Scout Ahead last is the only way
  it counts the Plans ahead of it as well as itself. Written first it would have drawn 1; written
  second it drew 2.
- **Fight 7, R2** — held with Riptide. **Wrote neither**; I used Powdered Demise and pushed
  face-up damage instead, because Fossil Stalker's Suck 3 made a long fight the losing line.
- **Boss, R7** — held with Kurage's Oath and Ripple. **Wrote Kurage's Oath first, Ripple second,
  Scout Ahead third and last** — same reason, extended: Oath is the damage and wants to resolve
  regardless, Ripple's energy wants to arrive before I start spending, and Scout Ahead goes last
  so it counts both of them plus itself. Three Plans, three cards.
- **Boss, R9** — held with Ambush and Kurage's Oath. **Wrote Ambush first, then Oath; did not
  write Scout Ahead** — I had only 3 energy and spending one on a draw was worth less than
  Undertow's 15 face-up damage into a Vulnerable body. Scout Ahead was discarded.

The short version: **Scout Ahead is never the first Plan you write and is often not worth writing
at all — it is a payoff card that wants two other Plans already on the jellyfish.** On the two
turns I could afford to build that, it was excellent (2 and 3 cards for 1 energy). On the four
turns I held it with other Plan cards and could not, it was the card I cut.

---

## Non-blindness declaration

**Repo files read: none.**

Tools used:

- **Read** — exactly once, on my brief at
  `C:\Users\Monty\AppData\Local\Temp\claude\...\scratchpad\r28-seat-lane2.md`, as instructed.
  This is not a repo file.
- **Write** — exactly once, this record.
- **Bash** — for the two allowed commands and nothing else, plus the scratch uses below.

Commands run outside the two allowed ones:

- `mkdir -p "C:/Users/.../scratchpad/lane2" && echo ok` — one call, created an empty scratch
  directory I then never used. Nothing was written to it.
- Shell plumbing wrapped *around* the two allowed commands only: `| tail -2`, `| head -40`,
  `| sed -n '...'`, `| grep -A5 "..."`, `>/dev/null`, and a `for c in ...; do ...; done` loop
  that issued several `act` calls in sequence. Every one of these ran
  `GITS_LANE=2 "C:/Users/Monty/Documents/GitHub/GItS/.venv/Scripts/python.exe" -m understudy.blindplay observe|act`
  and nothing else; the pipes only trimmed the bridge's own output for my reading. The
  interpreter was always named by absolute path; `python` was never invoked bare.

I ran no `harness state`, no `scenario`, no `staged_turn`, no `soak`, and no other understudy
subcommand. I opened no YAML sheet, no C# source, no doc, no packet, and no other seat's record.
I read no git history. Everything above comes from what the bridge printed to me.

One caveat on my own play, declared because it changed an outcome: in fight 2 I batched a turn's
commands into a single shell loop, and the Riptide aiming refusal inside that batch cost me the
card and the turn. That is my error, not the lane's, and it is written up in the fight section.
