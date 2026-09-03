# KLEEMOD-KOKOMI — blind seat, lane 1, act 1 boss + act 2

## Identity

- **Model / seat:** Claude Opus 5 (1M), blind TESTER seat, lane 1. Second seat of
  this kind on this run; I picked up where `opus-act1.md` stopped.
- **Character:** the Bake-Kurage / Plan kit. Same as the previous seat: no screen
  I saw printed a character name. The only place a name appears is the status
  line `Kokomi Burst: N/20`. The one new name-bearing thing I found is a card,
  **Princess of Watatsumi+**, obtained from an event — and it turns out to have
  nothing to do with that meter (see below).
- **Picked up at:** act 1, five floors below the boss, HP 44/80, 71 gold, on the
  map screen offering `Unknown (path 1)` / `Shop (path 2)`.
- **Stopped at:** act 2, on the map screen after the fifth room of the act
  (`Unknown (path 1)` the only node), HP 37/80. The act-2 boss, **The
  Insatiable**, printed as 16 floors above the act's first map, so the hand-off
  point in my brief was never reachable inside the budget.
- **Actions accepted:** 137 accepted `act` calls, 2 refused (my own tally, kept
  by hand; nothing on screen counts them).
- **Termination reason:** act budget (137 of 140), stopped deliberately on a map
  screen rather than inside a combat, following the previous seat's reasoning.
- **HP trajectory:** 44 (pickup) → 44 (shop) → 44 after fight 7 → 43 → 35
  (fight 8) → **rest 59** → boss: 59 → 53 → 50 → 50 → 30 → 27 → 27 → **8** on
  the killing turn → **65 on entering act 2** (an unexplained heal, see below) →
  62 → 39 (fight 10) → 39 → 38 → 37 (fight 11) → 37 now.
- **Gold:** 71 at pickup. Spent 48 (Ambush), had 20 stolen by Thievery and
  returned by Heist, earned 16+20+11+100+16+12, spent 73 (Cleansing Wave) and 75
  (Card Removal). By arithmetic **30**. The last figure any screen printed was
  `You have 166 gold.` at the act-2 shop.
- **Potions:** one held, **Clarity Extract** (never used, its text never
  printed — it was only ever a reward-screen line). Spent during the round: Flex
  Potion, Fire Potion, Block Potion.

**Relics, exactly as printed** (unchanged all round; no relic was gained):

- **Tamakushi Casket** — Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that enemy. Card rewards after a fight offer a fourth Companion choice.
- **Scroll Boxes** — Upon pickup, choose 1 of 2 packs of cards to add to your Deck.
- **Stone Cracker** — At the start of each combat, Upgrade 2 random cards in your Draw Pile for the rest of combat.
- **Anchor** — Start each combat with 10 Block.

**Deck at the end.** I must flag an error of my own here. The only screen that
prints the whole deck is the Card Removal screen, and when I opened it I piped
it through `sed -n '1,40p'`, which cut it off mid-list. There is no `deck`
command in my two allowed commands, so I could not re-read it. What that screen
printed before my own truncation, exactly as printed:

- **Strike ×4** — cost 1, attack — Deal 6 damage.
- **Defend ×4** — cost 1, skill — Gain 5 Block.
- **Kurage's Oath (proto)+** (upgraded) — cost 1, skill — Play on the Bake-Kurage. Plan: Deal 10 damage to ALL enemies.
- **Slack Water (proto)** [Hydro] — cost 1, attack — Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies.
- **Feint** [Hydro] — cost 1, attack — Deal 6 damage. Plan: Deal 10 damage.
- **Deep Current** [Hydro] — cost 1, attack — Deal 6 damage to ALL enemies.
- **War Council (1)** — cost 1, skill — Play on the Bake-Kurage. Plan: Deal 5 damage and apply 1 Weak to ALL enemies.
- **Stolen Chapter (proto)** — cost 1, skill — *(list truncated by my own sed here)*

Changes after that screen, which I can state exactly because I made them:
**−1 Strike** (the removal I had just bought), **+Cleansing Wave** (bought,
73g), **+Undertow (proto)** (fight-11 reward). And earlier in the round, added
before that screen: **+Ambush** (bought 48g), **+Change of Plans**, **+War
Council ×2**, **+The Moon Overlooks the Waters** (boss reward), **+Princess of
Watatsumi+** (event). Cards known to be in the deck but below my truncation
point: Coral Bulwark, Song of Pearls (proto), Chiori — Fluttering Hasode,
Dahlia — Favonian Favor (proto), Rosaria — Ravaging Confession, Kujou Sara —
Tengu Stormcall (proto), Ambush, Change of Plans, and the second and third War
Councils. **The next seat should re-read the deck; mine is a reconstruction, not
a quotation.**

New card faces, exactly as printed, for the ones that entered this round:

- **Ambush** — cost 1, skill — Play on the Bake-Kurage. Plan: Deal 12 damage.
- **Change of Plans** — cost 1, skill — The Bake-Kurage carries out your first Plan now. Exhaust.
- **The Moon Overlooks the Waters** — cost 2, power — Plans also happen when played.
- **Princess of Watatsumi+** (upgraded) — cost 1, power — At the start of your turn, gain 4 Charge.
- **Cleansing Wave** — cost 1, skill — Gain 5 Block. Remove one of your debuffs. Plan: Gain 10 Block.
- **Undertow (proto)** [Hydro] — cost 1, attack — Deal 7 damage. If the enemy has a debuff, deal 10 instead.

---

## Fight 7: Gremlin Merc 48/48

Opening HP 44/80. Two powers printed on it, one of them deliberately opaque:

> `Surprise 1 (buff) — Something is off about this creature...`
> `Thievery 20 (buff) — Steals 20 Gold when Attacking.`

**Turn 1.** Incoming was `7x2` against Anchor's 10 Block. I worked out that a
single Weak would drop it to `5x2` = 10, which my 10 Block eats entirely, so
defence was free and the whole turn could be offence. Played, in order: Slack
Water at the Merc (48→42: 4 + the Casket's 2), then **the intent line
immediately reprinted `7x2` → `5x2`**, which is the single best small piece of
feedback in the kit — I could see my Weak land on the incoming number before I
committed the rest of the turn. Then Rosaria (42→28), then Kujou Sara (28→8).

**Rejected:** Defend. With Anchor's 10 and the Weak, Defend blocked literally
nothing, and I could prove it from the reprinted intent rather than guessing.

**Ordering was the real decision.** Both Companions grew a reaction preview the
moment Slack Water put a Hydro aura up. Rosaria had to go before Kujou Sara,
because her own text has an aura clause (`If the enemy has an aura, apply 1
Vulnerable`) and because Frozen sets up a Shatter for whoever hits next. That is
a genuine, legible sequencing decision, and the previews are what made it
legible.

**Where the screen and the outcome disagreed.** Kujou Sara prints **"Deal 5
damage"**. The board moved **20** (28 → 8). I can partly reconstruct it —
Vulnerable, a 6-point Shatter, the Casket, an Electro-Charged proc — but
**nothing on any screen accounted for a single point of it**. A card that says 5
and does 20 is the most extreme case of the previous seat's under-reporting
finding I saw all round.

**Turn 2.** Enemy at 8 with an 11-damage Feint in hand (Fantastic Voyage was
up). **No rejected alternative — this turn presented no decision.**

Then `Surprise` paid off: the Merc **split into Sneaky Gremlin 11/11 and Fat
Gremlin 14/14**, both Stunned, the fat one carrying
`Heist 20 (buff) — When killed, returns all the stolen Gold.` So it *had* taken
my 20 gold, and the screen told me exactly how to get it back. This is the kit's
world at its best: an opaque flavour line resolved into a concrete, readable
consequence with a stated remedy.

Deep Current (11 with Fantastic Voyage) killed Sneaky exactly and left Fat at 3;
I spent the spare energy planning **Ambush**, the card I had just bought, to see
whether "Plans hit the front enemy" behaved as printed. It did — the fight ended
in the morning when the Plan fired and killed the Fat Gremlin, and the reward
screen printed `20 Gold (stolen back)`.

**A reporting gap I want on the record:** because the morning Plan's kill ended
the fight, **the "The Bake-Kurage carried these out" block was never printed at
all**. I got the outcome with no accounting. If a Plan closes a fight, the one
line that would tell you what your Plan did does not exist.

---

## Fight 8: Calcified Cultist 38/38 + Seapunk 45/45

**Turn 1.** My hand held exactly one damage card. So I spent the first energy on
**Stolen Chapter+ (Draw 3)** and then decided with a bigger hand — a direct test
of the previous seat's conclusion that Stolen Chapter is always a wash. It is
not: the previous seat's analysis assumed a hand of playable cards, and the case
it misses is *a hand full of cards you do not want to play*, where digging
converts dead energy into live options. It drew two Strikes and Rosaria.

Then Kurage's Oath+ as a Plan (10 to ALL = 20 points of value for one energy
against two enemies) and Rosaria into the Cultist. **Rejected:** Strike +
Rosaria for 15 now, because nothing died this turn either way and the AoE Plan
is worth more than the tempo against two full-HP bodies.

**Turn 2, morning.** `Bake-Kurage: Kurage's Oath (proto)+, 10`. Seapunk moved
exactly 10. The Cultist moved 10 *and gained Frozen* — the Kurage's Hydro Plan
had consumed the Cryo aura Rosaria left behind and triggered a reaction.
**Nothing printed a line saying a reaction had happened.** The morning log
reports a number, not events; I only knew a reaction had occurred because a new
debuff appeared on a body.

Then a good turn. Strike into the Frozen Cultist did **12** (6 + a 6 Shatter),
and the Cultist's intent jumped **4 → 9** the instant Frozen came off. That cost
is legible — the Frozen line states both halves in one sentence
(`next action deals 50% less damage. The first Attack that hits it Shatters...
and removes Frozen`) — so I could see before I swung that Shattering would
double the incoming hit. Credit where due: this is the same shape as the act-1
Hardened Shell complaint and it is *well* written.

Killed the Cultist with the second Strike and banked War Council.
**Rejected:** Coral Bulwark for 6 Block, because the Seapunk was a 35-HP grind
and every turn spent blocking is another turn of its attacks.

**Turn 3, morning.** `Bake-Kurage: War Council, 5` — board moved **7**. The
Casket's 2 unlogged, exactly as the previous seat recorded. Confirmed.

Free turn (both Empowering), so Chiori went in: 18 damage over three turns
ignoring Block for one energy, versus Slack Water's 6 once. **Rejected:** Slack
Water and Song of Pearls.

**Turn 4 — the turn I bought Change of Plans for.** Seapunk at 10 HP behind 7
Block with a 12-damage intent, and my hand was one attack and two Defends. I
wrote **Ambush** as a Plan and immediately cashed it with **Change of Plans**
(12 damage now instead of tomorrow), then Kujou Sara's 5 covered the remainder:
17 against 7 Block + 10 HP, exactly. The Seapunk never landed its 12.
**Rejected:** the two Defends (13 Block against a 12 hit) — surviving was not
the problem, ending the fight was. This is the best turn the kit gave me in a
normal fight, and it only exists because a card exists whose whole job is to
undo the Plan layer's tempo cost.

---

## Fight 9 (Act 1 boss): Waterfall Giant 240/240

Entered 59/80 after resting (Rest heals 30% = 24; a Smith upgrade is worth
maybe 4 damage a fight — not a close call at 44%).

**Turn 1.** Giant Empowering, so a free turn, so the power goes down: Song of
Pearls, then Slack Water and Strike (240→228, exactly 4+2+6). A 240-HP fight is
the first board where Song of Pearls can pay; the previous seat only ever saw it
return 3 Block once in a four-round fight. **Rejected:** Defend, worth zero
against an Empower.

The Empower resolved into
`Steam Eruption 15 (buff) — When killed, deals 15 damage at the end of your next
turn.` It then grew **15 → 18 → 21 → 24 → 27 → 30 → 33**, +3 every turn. That is
an excellent piece of design and it is legible from the number alone: **the boss
charges you a rising price for taking your time, and my deck is built to take
its time.** It reframed every subsequent decision.

**Turn 2.** Chiori (18 over three turns for one energy) + Strike + Defend.
**Rejected:** Stolen Chapter, because I already held the best card in hand.

**Here the screen and the outcome disagreed and I could not reconcile it.** A
15-damage intent against 5 Block cost me **6** HP (59 → 53), not 10. Nothing on
the page accounts for the missing 4. I later found a *different* case where my
prediction was wrong for a reason the page does explain (see fight 11, Strength
double-counting), but that explanation does not apply here — the Giant had no
Strength. I am reporting this as unexplained rather than pretending I solved it.

**Turn 3 — the turn where the kit's mechanic did real work.** The Giant had
Weakened *me*, and every attack in my hand reprinted its own reduced number
(Deep Current showed **"Deal 4 damage"**, not 6). That is the previous seat's
favourite legibility feature working in the negative direction, and it produced
a genuine insight: **while you are Weak, banking is strictly better than
swinging, because the Plan resolves next morning when the Weak has expired.** So
Ambush+ (Stone Cracker had upgraded it to a 15-damage Plan) and War Council both
went to the Kurage, and Dahlia blocked. **Rejected:** Deep Current for a
Weak-reduced 4.

**Turn 4.** Morning `Ambush+, 15` / `War Council, 5`; the board moved **20** from
where Chiori's tick left it. Either the Casket's 2 did not fire on War Council's
Weak here, or Chiori's 6 landed somewhere I could not see. In fight 8 the same
card demonstrably moved the board by 7. **Nothing on the page distinguishes the
two cases.**

Rosaria's preview had rewritten itself for the boss:

> `*Reaction preview: Frozen (Boss)* — Bosses cannot be Frozen. Hydro plus Cryo is consumed and applies 2 Vulnerable instead.`

**This is the best teaching on any screen I saw in either act.** The card tells
you, before you commit, that the rule you learned in act 1 is replaced in this
fight. Nothing else in the kit does this.

The Giant was Healing, so a free turn: Rosaria → Kujou Sara → Feint, front-loaded
into a fresh Vulnerable window (190 → 149 *through a heal*). **Rejected:**
banking Kurage's Oath+ and War Council, because Steam Eruption's +3/turn means
delay has a printed, rising price.

**Turn 5 — the burst.** Fantastic Voyage +5 and Vulnerable 2 both live, so
Strikes printed 11. Spent the Flex Potion I had held one turn precisely for this
overlap: **149 → 74, seventy-five damage in one turn.** **Rejected:** using the
potion the previous turn, when only Vulnerable was up; holding it for the
overlap roughly doubled it. This was the most satisfying decision of the round,
and the card faces reprinting 6→11 are what made it calculable rather than
hopeful.

**Turn 6.** At 30 HP with `Steam Eruption 27`, HP became the binding resource
rather than damage. Banked **Coral Bulwark as a Plan** (8 Block + Weak next
morning, plus Song of Pearls' 3 = 11, versus 6 Block now) and played **Dahlia
before Rosaria** so that Rosaria's reaction would trigger Dahlia's rider. It
fired — Block 10 = 7 + 3. **The previous seat reported that rider never once
firing all act; it fires, and the trick is that Dahlia must be played before the
reaction, not after.** That is a real ordering decision hidden in a card that
looks like a vanilla Defend.

**Turn 7.** Morning `Coral Bulwark, 8` → Block 11, and its Weak dropped the
intent 13 → 11, which my 11 Block then exactly covered. Banking block was right,
and it answers a question the previous seat left open. With defence free, the
third energy was pure profit: Ambush+ and Kurage's Oath+ both banked, Strike for
9. **Rejected:** Defend, worth nothing on a turn my Block already exactly matched
the printed intent.

**Turn 8, morning.** `Ambush+, 16` and `Kurage's Oath (proto)+, 11` — and the
board moved exactly 27. Two findings in one line. First, the logged numbers are
**not** the cards' printed numbers (15 and 10); they are +1 each, and nothing
explains the +1. Second, **Vulnerable did not multiply the Kurage's Plan damage
the way it multiplies my card attacks** — 27 landed where ×1.5 would have been
40. Banked damage and dealt damage obey different rules and no screen says so.

**Then the defect of the round.** My third card would have killed it, and
instead the Giant printed:

> `**Waterfall Giant** — HP 999999997/999999999`

Its HP became **999,999,997 of 999,999,999** and it went Stunned. This is
plainly a phase flip implemented with a sentinel value, rendered raw. For one
whole turn the screen told me the boss had a billion HP and I had 0 energy and
two cards marked `CANNOT BE PLAYED`. I had no way to tell whether I had won,
lost, or broken something.

The next turn resolved it honestly:

> `Intent: Death Blow (DeathBlow) — the number on its icon is 33 — This creature is trying to take you down with it. It will attack you for 33 damage before being destroyed.`

At 27 HP and 0 Block I needed 7 Block to live. My hand held two block cards
worth 11 and a third energy with nothing worth spending it on, so **Stolen
Chapter dug for block** and found Defend+. Played Defend+ and Coral Bulwark for
14, took 19, **survived on 8 HP**. **Rejected:** Rosaria and Ambush+ — every
damage card and the entire Plan layer were dead on that turn, because a Plan
resolves in a morning that will never come.

**Boss beaten.** I then entered act 2 at **65/80**, a jump of 57 HP that **no
screen anywhere explained or announced**.

---

## Fight 10: Tunneler 87/87

Act 2's opening single body has nearly twice act 1's HP.

**Turn 1.** Anchor's 10 covered all but 3 of the 13 incoming, so block cards were
worth ~3 HP and Plans were worth 10-12 damage: banked **Ambush** and **Feint**,
Strike for 6. **Rejected:** playing Feint's face for 6 — against a single 87-HP
enemy with nothing dying, tempo is worth less than the Plan's extra 4. Note this
is the *inverse* of my act-1-boss read, where Fantastic Voyage made Feint's face
(11) beat its own Plan (10). Same card, opposite answer, both times visible from
the card because it prints both numbers. **This is the best-designed card in the
deck.**

**Turn 2, morning.** `Ambush, 12` / `Feint, 10`; board moved exactly 22. Clean —
and the pattern across the round is now clear: the morning log reconciles
perfectly when no Casket proc is involved, and silently under-reports when one
is.

Empower turn, so all three energy into damage, Rosaria first for the Vulnerable
and Frozen (59 → 21). **Rejected:** block, worth zero against an Empower.

**Turn 3.** The Empower resolved into
`Burrowed 1 (buff) — Block is not removed at the start of Tunneler's turn.
Stunned if all Block is removed.` — **32 permanent Block over 21 HP.** A good,
readable puzzle with two printed solutions: Chiori's damage ignores Block, and
stripping all 32 stuns it.

My hand had no block against a 23 intent, so I dug again with Stolen Chapter+
(second time it was correct, second time for the same reason) and drew **The
Moon Overlooks the Waters**. Installed it. **Rejected:** Chiori + Defend, which
is better *this* turn and worse from the next one on: 32 persistent Block means
a long fight, a doubling of the Plan layer compounds over a long fight, and
delaying Chiori costs nothing because her three ticks land either way.

**Turn 4 — the engine turn.** Fire Potion (20) + Kurage's Oath+ written on the
Kurage (Moon fired it immediately for 10) + Change of Plans (fired the queued
copy again for 10) + Slack Water. **Forty-six damage: all 32 Block stripped,
`Stunned`, HP 21 → 7.** "Plans also happen when played" works exactly as
printed, and it stacks with Change of Plans, so one Plan card produced 20 damage
in a single turn.

**Turn 5.** War Council written on the Kurage killed it outright — 5 + the
Casket's 2 = exactly 7 — confirming AoE Plans also fire on play. The page had
also added a line to the Bake-Kurage panel the moment the power went down:
`Plans also happen NOW as you write them.` **The page updating its own
explanation of the pet when a card changes the rules is genuinely good.**

---

## Fight 11: Exoskeleton 26/26 + Exoskeleton 27/27 + Exoskeleton 28/28

All three printed
`Hard To Kill 9 (buff) — Reduce all damage taken and HP lost by Exoskeleton to 9.`

**Turn 1.** I could not tell from that sentence whether 9 was a per-hit cap or a
per-turn allowance — the same ambiguity the previous seat hit on Hardened Shell,
in a new costume. I played to find out: Kurage's Oath+ banked, Strike+ for
exactly 9 into one body, Song of Pearls installed. **Rejected:** Kujou Sara,
because next turn's morning AoE would cap all three at 9 anyway, so her "+5 to
your Attacks next turn" would be worth precisely nothing — **the cap makes a
damage buff worthless on a morning turn**, which is a nice sharp instance of the
previous seat's "banked damage is not free damage against a cap" lesson.

**The answer, from the board:** the first Exoskeleton took 9 from Strike+ *and* 9
from the morning Oath, 18 in one turn. So **`Hard To Kill 9` is a flat per-hit
cap, and act 1's `Hardened Shell 20` was a decrementing per-turn allowance.** Two
powers that read almost identically follow different rules, and the only way to
learn which is to spend a turn testing.

**Turn 2.** Deep Current (6 to all — efficient precisely because it sits *under*
the cap) + Strike to finish the first body + Defend. **Rejected:** Feint's Plan,
whose 10 would be shaved to 9 and arrive a turn late.

**Where I was wrong, and why.** I predicted 7 damage and took 1. The reason is on
the screen and I misread it: **the printed intent already includes Strength**,
while `Strength 2 (buff) — Increases attack damage by 2` prints on the next line
and invites you to add it a second time. I double-counted. That is a legibility
trap rather than a bug, but it caught me twice.

Also on this turn: **the surviving enemies renumbered.** The bodies that had been
`Exoskeleton (2)` and `(3)` became `(1)` and `(2)`. The page warns about
renumbering for *cards in hand*; the same instability applies to *enemy target
names* and is not warned about anywhere.

**Turn 3.** Block Potion (free, 12) + Coral Bulwark for 18 Block against 19
incoming, plus Rosaria+ and Chiori. Stone Cracker had upgraded Rosaria to
**"Deal 12 damage"** — and the 9 cap threw 3 of it away, so the upgrade was worse
than useless here. Chiori's Tamoto finished the second body.
**Rejected:** saving the potion; at 37 HP with two bodies still up, a turn where
one free potion buys a clean zero is the turn to spend it.

**Turn 4.** Last body at 7, Empowering, zero incoming. Slack Water took it to 1
and Chiori's end-of-turn 6 killed it. **No rejected alternative — this turn
presented no decision,** and I deliberately spent only one card to save budget.

---

## Map, shop, rest, events

Nine map screens. **Node counts, in order: 2, 1, 1, 1, 1, 3, 2, 2, 1.**

Every single-node screen was consistent with the *previous* screen's printed
"leads on to" list, so I saw **no dropped sibling** anywhere. One thing does
mislead, though: the "floors ahead" block lists every room on a floor
(`1 floor ahead: Elite, Unknown, Shop, Elite, Unknown`) while the "Where you can
go next" block offers one node, and the page never says which of the five listed
rooms the single offer corresponds to. Twice I had to reason about a route from a
list of rooms I could not actually reach.

**Act-1 shop** (71 gold). Card Removal was 75 and I was four gold short — the
only purchase I actually wanted. Bought **Ambush** (48). The keyword box here
printed a rule that appears nowhere in the previous seat's record: **"Plans hit
the front enemy."** Chose Ambush over Explosive Ampoule and a second Feint
because a Plan-only card with no face is the cleanest possible read on whether
the Plan layer is worth its tempo.

**Rest site** (35/80). `Rest — Heal for 30% of your Max HP (24)` versus
`Smith — Upgrade a card in your Deck`. Rested. An upgrade is worth ~4 damage a
fight; 24 HP is three enemy hits, and the boss was the next room.

**Act-2 "Ancient" node — `Darv`.** **The first `observe` of this screen returned
the title, no body, no options, and a `choose "<option>"` prompt with nothing to
choose from.** A second observe populated it. That is a real render defect: the
page offered a verb against an empty screen.

Once populated:

- **Astrolabe** — Transform 3 cards, then Upgrade them.
- **Empty Cage** — Remove 2 cards from your Deck.
- **Dusty Tome** — Obtain Princess of Watatsumi+.

Chose **Dusty Tome**. My reasoning: "Princess of Watatsumi" is the character's
own epithet, and the one thing no screen in two acts had explained was the
`Kokomi Burst` meter, so a signature card was the likeliest place that rule would
be printed; card removal I could buy later with 166 gold and a Shop three floors
up, whereas this card I could not. **The event then granted the card without ever
printing its face** — I did not learn what it did until I drew it in combat two
rooms later.

**Act-2 shop** (166 gold). Bought **Cleansing Wave** (73) and **Card Removal**
(75), removing a **Strike** — with Moon installed, a 6-damage vanilla attack is
the lowest-value card in the deck, while Defend still answers act 2's pattern of
one very large hit. Note that **`choose` on the removal screen only *toggles* the
selection**; my follow-up `proceed` was refused with
`there is nothing to leave from this screen`, and `confirm` was the verb needed.
The screen's header says "Choose a card to Remove", which reads like one step.

Unbought act-2 shelf, quoted because it bears on the previous seat's findings:
**Gorou — Crystal Collapse** (76g) is still on sale with the exact wording the
previous seat flagged — *"Plan: play a copy of the last other Companion card you
played this turn"* — on a card that resolves next turn. With Moon installed
("Plans also happen when played") that window is now *worse*, not better,
because the same card can now resolve in either of two turns.

Also on the shelf and worth flagging for ambiguity: **Fortifier** (74g) —
*"Triple your Block."* No duration, no scope, no trigger. I did not buy it, and I
could not have told you what it does.

---

## Companions and offers

Every Companion card offered this round, quoted as printed. All arrived in the
fourth slot the Tamakushi Casket promises, or on a shop shelf.

1. **Raiden Shogun — Musou no Hitotachi (proto)** [Electro] — cost 3, attack
   *Deal 20 damage. Deals 5 additional damage for each Companion card you played this combat.*
   Passed. Reads clearly and scales off the thing the Casket keeps pushing. I
   passed because at cost 3 in a deck where every other card costs 1, it *is* the
   whole turn, for roughly what three 1-costs already do — and because it creates
   no decision: you play it when you have 3 energy.

2. **Navia — Cannon Fire Support** — cost 1, power
   *Whenever you play a Companion card, gain 3 Block.*
   Offered twice (act-1 shelf at 155g, boss reward). Passed both times. Sensible
   next to the kit, but with 4 Companions in ~25 cards it is about 9 Block a
   fight for a whole card and a whole energy.

3. **Gorou — Juuga: Forward Unto Victory** — cost 1, skill
   *For 3 turns, at the end of your turn deal 6 Geo damage to a random enemy. Exhaust.*
   Passed. This is **Chiori — Fluttering Hasode with the words "ignoring Block"
   deleted** and nothing given back. I already owned Chiori, and this round
   proved how much that clause is worth: it is the entire answer to the
   Tunneler's 32 persistent Block. Two Companions, near-identical text, one
   strictly dominated.

4. **Lynette — Bogglecat Box** — cost 1, skill
   *Draw 2 cards.*
   Passed. Nothing about it touches the Kurage, an aura, or a Plan — a colourless
   cantrip wearing a character's name. **This is the same defect the previous
   seat recorded against Sucrose — Catalyst Conversion, and it is now the second
   instance.**

5. **Shikanoin Heizou — Heartstopper Strike** — cost 1, attack
   *Deal 6 damage. Deals 4 additional damage for each Swirl this turn.*
   *Swirl — The enemy's aura is consumed and copied onto ALL enemies. No aura, no effect.*
   Passed. I hold **zero** cards that Swirl (the only one I was ever offered was
   Sayu, in act 1, which the previous seat passed). So this is a 6-damage card
   printed with a keyword box explaining a mechanic I cannot perform. **Third
   instance of a Companion payoff offered without its archetype.**

6. **Kaeya — Glacial Waltz** — cost 1, skill, 75g (act-2 shelf, unbought)
   *For 3 turns, at the end of your turn deal 6 Cryo damage to a random enemy. Exhaust.*
   The third card in the Chiori/Gorou family. Cryo would at least react with my
   Hydro, which is more than Gorou's version offers.

7. **Yae Miko — Sesshou Sakura** — cost 1, skill, 78g (act-1 shelf, unbought)
   *Place a Sakura, up to 3. At the end of your turn each deals 4 Electro damage to a random enemy, plus 3 after the first.*

Non-Companion offers that bear on the archetype: **Chain of Command**
(*Plan: Deal 6 damage for each Companion card you played last turn*) was offered
again and passed again — 4 Companions in 25 cards makes it a 6-damage card most
mornings. Note that with Moon installed, its "last turn" clause now collides
with "Plans also happen when played": if the Plan fires on the turn you write it,
"last turn" means something different than if it fires in the morning, and the
card cannot tell you which.

---

## The kit, after 11 fights

**(a) Which decisions felt like real choices, and what they traded off.**

- **Bank or spend, re-priced by the board.** This is still the kit's engine and
  it got better in act 2, because two boards gave the trade a printed price.
  Against the Waterfall Giant, `Steam Eruption` rising +3 a turn meant delay had
  a visible, growing cost, so front-loading was correct and I could say why.
  Against the Tunneler's 32 persistent Block, the fight was long, so compounding
  was correct and I could say why. Same decision, opposite answers, both derivable
  from the screen.
- **Weak inverts the decision.** While the Giant had Weakened me, every attack in
  hand reprinted a smaller number and every Plan kept its full one, because Plans
  resolve after the Weak expires. **Being debuffed is a reason to bank.** Nothing
  states this; the reprinted card faces let you derive it. This was my favourite
  discovery of the round.
- **Ordering within a turn.** Rosaria before Kujou Sara for the Vulnerable and
  the Shatter; Dahlia before Rosaria so the reaction triggers Dahlia's rider.
  These are worth 10-15 damage or 3 Block and they are readable from card text.
- **Change of Plans as a kill-window tool.** Twice it converted a banked 12 into
  a lethal now: once to deny a Seapunk its 12-damage swing, once as half of the
  46-damage turn that stunned the Tunneler.
- **Digging with Stolen Chapter.** Correct three times, always for the same
  reason: **the dig is right when your hand is full of cards you don't want to
  play, not when you're short of energy.**

**(b) What felt automatic, and what never seemed worth playing.**

- **Strike and Defend, still.** Every "no decision" turn in this record is a turn
  where the hand was vanilla cards. I removed one Strike and would remove six
  more.
- **Any turn where the enemy Empowers.** Zero incoming makes block worthless and
  the turn plays itself: dump damage or install a power. This happened in five of
  the five fights and is more of a monster-design note than a kit note.
- **Kujou Sara's "+5 next turn"** is dead whenever next turn is a morning turn
  against a cap, and dead whenever you intend to bank.
- **Slack Water's Plan line** (Weak to all, no damage) — I never once played it,
  across both acts, for the reason the previous seat gave.
- **Song of Pearls** was rehabilitated: worthless in a 4-round fight, genuinely
  good across the boss's 8 rounds, where its 3 Block a turn plus a banked Coral
  Bulwark was the difference between blocking an 11-damage intent exactly and
  not.

**(c) What I could not understand, or that contradicts its own printed text.**

1. **`Waterfall Giant — HP 999999997/999999999`.** A phase transition rendered as
   a raw sentinel. For one turn the boss had a billion HP on screen. This is the
   single worst thing I saw.
2. **`Kokomi Burst: 25/20`.** The meter that no card, relic or keyword explains
   now also **prints above its own stated maximum**. It reset to 5 at the start
   of each fight, climbed, hit 20/20, and then read 25/20. Two acts, two seats,
   still no rule, and now it is self-contradicting.
3. **The aura is not consumed when its own text says it is.** Twice — fight 7 and
   the boss's turn 6 — a Cryo hit triggered a reaction (Frozen / 2 Vulnerable
   applied, so the reaction demonstrably happened) and the `Hydro Aura` was still
   printed afterwards, once at a *higher* number than before. The aura's own text
   says "A hit of a different element consumes the aura and triggers an Elemental
   Reaction."
4. **The morning log prints three different things.** Sometimes the card's base
   number while the board moves more (`War Council, 5` → 7). Sometimes the actual
   number, differing from the card (`Ambush+, 16` where the card says 15).
   Sometimes a number the cap then overrides (`Kurage's Oath (proto)+, 10` while
   each body lost 9). You cannot tell which convention a given line is using.
5. **Vulnerable multiplies card attacks but not Plan damage.** Derived from
   arithmetic on the boss's turn 8; stated nowhere.
6. **`Hard To Kill 9` and `Hardened Shell 20` read alike and behave differently**
   — flat per-hit cap versus decrementing per-turn allowance. The previous seat
   burned a turn learning the second; I burned a turn learning the first.
7. **Strength is printed twice over.** The intent number already includes it, and
   the `Strength N — Increases attack damage by N` line sits right under it.
8. **Two unexplained HP swings**: a 15-damage intent through 5 Block that cost 6
   HP, and a **+57 HP heal on entering act 2** that no screen announced.
9. **Enemy names renumber when one dies**, with no warning (cards get a warning).
10. **`Fortifier` — "Triple your Block."** No duration, scope or trigger.
11. **The `Darv` event rendered empty on first read**, and **granted
    Princess of Watatsumi+ without ever printing its face.**

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted: Defend**, still, for the previous seat's reason — except that
  `Defend+` saved the run against the Death Blow, which is the one time in 11
  fights that a vanilla card decided anything.
- **Happiest to draw: Feint.** It prints its face and its Plan side by side, and
  which one is correct genuinely flipped between fights — face at 11 under
  Fantastic Voyage against the boss, Plan at 10 against the Tunneler. It is the
  card that best expresses what this kit is for. Honourable mention to
  **The Moon Overlooks the Waters**, which is the most fun the kit had, and which
  I would look at hard for balance: it removes the Plan layer's entire drawback
  for 2 energy, and stacked with Change of Plans it produced 20 damage from one
  1-cost card in a single turn.

**(e) Did the previous seat's three headline findings hold up?**

1. **The `Kokomi Burst` meter is unexplained** — **held, and worse.** Still no
   rule after 5 more fights; it now prints `25/20`, above its own maximum. And
   the kit demonstrably *can* explain a resource properly: `Princess of
   Watatsumi+` arrived with a full `Charge` keyword box (a bank, how it grows,
   that it has no maximum, how cards spend it). So Burst is not a missing feature
   — it is the one bank that was not documented.
2. **`Hardened Shell`'s number contradicts its sentence** — **held, and it
   generalises.** Act 2's `Hard To Kill 9` has the same shape and a *different*
   rule, so the confusion is now structural rather than one card's wording.
3. **The morning log under-reports the Casket** — **held, and it is worse than
   under-reporting.** It is inconsistent: I logged one morning that matched
   exactly, one that omitted the Casket, one that printed numbers higher than the
   cards, and one the enemy's cap silently overrode. Also new: **when a Plan's
   morning kill ends the fight, the log is not printed at all.**

I could also re-check three of the previous seat's other items: the rider-name
mismatch **held** (Chiori still leaves `Tamoto`, Kujou Sara still leaves
`Fantastic Voyage`); Dahlia's reaction rider **did not hold** — it fires
reliably, provided you play her *before* the reaction; and Gorou — Crystal
Collapse's "this turn" wording **held**, unchanged, still on the shelf.

**(f) Did act 2 ask anything of the deck that act 1 did not?**

Yes, three things, and this is the clearest signal I can give.

- **Act 2 attacks the deck's shape, not its size.** Act 1's enemies were HP bars.
  Act 2's first two rooms were `Burrowed` (32 persistent Block, answerable only
  by block-ignoring damage or a full strip) and `Hard To Kill 9` (a per-hit cap
  that makes big numbers worthless and small AoE excellent). **Those two demand
  opposite decks**, one turn apart. Chiori answered the first and was near-useless
  for the second; Rosaria+ at 12 damage answered the second badly and the first
  well.
- **The single-hit ceiling went up sharply.** Act 1 asked me to survive 11s and
  15s; act 2 opened with 23 and the boss's Death Blow was 33. With Anchor's flat
  10 and Defends at 5, my defence does not scale with that at all — every act-2
  turn where I blocked, I blocked with a potion or a banked Coral Bulwark, never
  with the deck's actual block cards.
- **It rewarded the Plan layer more, not less.** The act-1 boss punished slowness
  with `Steam Eruption`; act 2's Tunneler rewarded compounding. `The Moon
  Overlooks the Waters` turned the kit from "pay tempo for value" into "value for
  free", and that is where the kit was most fun and most likely over-tuned.

One structural note for the coordinator: **act 2 is 16 floors.** A seat picking
up at the act-2 map cannot reach The Insatiable inside a 140-act budget; I used
137 acts to clear one boss and five rooms. If the act-2 boss is the thing you
want graded, it needs its own seat starting much closer to it.

---

## Non-blindness declaration

- **Commands used:** only `GITS_LANE=1 python -m understudy.blindplay observe`
  and `GITS_LANE=1 python -m understudy.blindplay act "<command>"`. No other
  understudy subcommand was run — no `harness state`, no `scenario`, no
  `staged_turn`, no `soak`.
- **Tools used:** **Bash**, for every one of the above calls. On most calls I
  chained several `act` invocations and one `observe` in a single shell line with
  `&&`, and piped the `observe` through `sed -n '<ranges>p'` to print only the
  sections I needed (HP block, hand, enemies, Bake-Kurage panel). **Read**, once,
  for the previous seat's record. **Write**, once, for this file.
- **The one place my scratch cost me information:** on the Card Removal screen I
  piped through `sed -n '1,40p'` and truncated the deck list. There is no `deck`
  command among my two allowed commands, so I could not recover it, and the deck
  section above is therefore part quotation and part reconstruction. That is my
  error and it is flagged in place.
- I did not create a notes file; the notes are this record.
- **Two `act` calls were refused**, neither consecutive:
  - `play "Strike" on "Tunneler"` → `you are not in a battle`. Deliberate: I
    chained a follow-up attack behind War Council to learn in one call whether
    the AoE Plan's on-play damage had already killed it. It had.
  - `proceed` on the Card Removal screen → `there is nothing to leave from this
    screen`. My error: `choose` only toggles the selection there, and `confirm`
    is the verb. The refusal did not name `confirm`, but the screen's own command
    list did.
- **Other repo files read: none.**
