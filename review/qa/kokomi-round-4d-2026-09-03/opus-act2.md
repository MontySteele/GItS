# KLEEMOD-KOKOMI — blind seat, lane 1, act 2

## Identity

- **Model / seat:** Claude Opus, blind TESTER seat, round 4d, **second of three seats** (act 2 only).
- **Lane:** 1.
- **Character:** KLEEMOD-KOKOMI.
- **Picked up:** on the act-2 map screen where the first seat stopped, at its only offered node
  (`Ancient (path 1)`). The first seat's record said HP 58/87; the first screen that printed an HP
  line in act 2 read **81/87**.
- **Act:** 2. Sixteen floors. Boss named by the map: **The Insatiable** (321 HP).
- **Actions accepted / refused:** **226 accepted, 1 refused.** The single refusal was
  `play "Deep Current" on "Infested Prism"`, and the refusal named the form that works
  (`play "Deep Current"`). No bare `observe` ever produced a traceback or a `PacketLeak`.
- **Termination reason:** **stop condition (1)** — the act-2 boss was resolved, its reward screen was
  handled, and the lane now stands on the act-3 map screen. 24 of the 250-action budget unspent.
- **Where the run stands:** **act-3 map screen**, at its single offered node (`Ancient (path 1)`),
  HP **35/87**. The act-3 boss is printed as **Aeonglass**.
- **HP trajectory (every reading the screens printed, in order):**
  81/87, 81, 77, 77 (fight 6) — 77, 77, 77, 77 (fight 7) — 77, 61, 61, 61, 57 (fight 8) —
  **72** on entering elite 4, i.e. `Meal Ticket` had healed 15 at the first shop with no screen
  saying so — 72, 60, 45, 40 (elite 4) — **55** on entering fight 9, `Meal Ticket` again at the
  second shop — 55, 55 (fight 9) — 51, 46, 41 (fight 10) — **63** on entering elite 5, i.e. the
  Spirit Grafter's 25 HP landed on 38, three lower than the last figure any screen had shown me —
  63, 54, 42, 32, 25, 25 (elite 5) — 25 at the rest site, **51** after resting —
  51, 51, 51, 35, 35 (boss). **Final: 35/87.**
- **Gold:** the map screen prints none. Last figure quoted by a screen was **84** at the second shop,
  of which 51 went on `Vanguard`; the reward rows claimed after that were 12+15, 15+15, 36+15 and
  100+15. The first shop read **647** against 445 of claimed rows — see the findings.
- **Potions held at the stop:** `Colorless Potion`, `Vulnerable Potion`, `Speed Potion` — the belt is
  3 of 3 and has been full since fight 8, so `Energy Potion`, `Explosive Ampoule` and
  `Cunning Potion` were all left unclaimed on their reward screens. **I used no potion in act 2.**
- **Relics, exactly as printed (13):**
  - **Tamakushi Casket** — "Start each combat with the Bake-Kurage. Whenever you apply a debuff to an enemy, it deals 2 Hydro damage to that enemy. Card rewards after a fight offer a fourth Companion choice."
  - **Kaleidoscope** — "Upon pickup, obtain 2 card rewards from other characters."
  - **Oddly Smooth Stone** — "Start each combat with 1 Dexterity."
  - **Snecko Skull** — "Whenever you apply Poison, apply an additional 1 Poison."
  - **Meal Ticket** — "Whenever you enter a shop room, heal 15 HP."
  - **Anchor** — "Start each combat with 10 Block."
  - **Amethyst Aubergine** — "Enemies drop 15 additional Gold."
  - **Gear Glass** — "See 15 cards from The Defect. Choose any number of them to add to your Deck." (an event *option* that became a relic)
  - **Orrery** — "Upon pickup, gain 5 card rewards."
  - **Tungsten Rod** — "Whenever you would lose HP, lose 1 less."
  - **Juzu Bracelet** — "Regular enemy combats are no longer encountered in ? rooms."
  - **Intimidating Helmet** — "Whenever you play a card that costs [Energy][Energy] or more, gain 4 Block."
  - **Candelabra** — "At the start of your 2nd turn, gain [Energy][Energy]."

### Deck at the stop — 36 cards

The 25-card list below is not reconstructed: the shop's Card Removal screen printed my whole deck,
which is how I know **no Status card has ever persisted** despite twelve being forced on me.

Carried in from act 1 (22): `Strike` x4, `Defend` x4, `Kurage's Oath (proto)`, `Slack Water (proto)`,
`Uproar`, `Pounce`, `Amber — Explosive Puppet`, `Razor — Lightning Fang`, `War Council`,
`Razor — Claw and Thunder`, `Sango Isshin (proto)`, `Kamisato Ayaka — Soumetsu` x2, `Vanguard`,
`Battle Plan`, `Undertow (proto)+`.

Added in act 2 (+15, and one `Defend` removed):

- `Go for the Eyes` — 0, attack, "Deal 3 damage. If the enemy intends to attack, apply 1 Weak." (Orobas event)
- `War Council` (2nd) — 1, skill, Plan: 5 damage + 1 Weak to ALL. (fight 6)
- `Kujou Sara — Crowfeather Cover (proto)` — 0, skill, "Your next Attack this turn deals 4 additional damage and applies Electro." (fight 7)
- `The General's Banner+` — 1, power, Innate, "Once per turn, when you play a Companion card, apply 1 Weak to the front enemy." (Orrery)
- `Moon's Reflection+` — 0, skill, "Choose a card in your Exhaust Pile. Next turn, the Bake-Kurage carries out its Plan line, or plays it if it has none. Exhaust." (Orrery)
- `Deep Current` [Hydro] — 1, attack, "Deal 6 damage to ALL enemies." (Orrery)
- `Coral Bulwark` — 1, skill, "Gain 6 Block. Plan: Gain 8 Block and apply 1 Weak." (Orrery)
- `Sango Isshin (proto)` (2nd) — 2, attack. (shop 1, 72 gold)
- `Vanguard` (2nd) — 0, skill. (shop 2, 51 gold)
- `Shinobu — Grass Ring of Sanctification (proto)` — 0, skill, "Gain 4 Block. If you lost HP this turn, gain 4 additional Block." (elite 4)
- `Change of Plans+` — 1, skill, "The Bake-Kurage carries out your first Plan now." (fight 9)
- `Amber — Fiery Rain` [Pyro] — 1, attack, "Deal 4 damage to ALL enemies 3 times." (fight 10)
- `Metamorphosis` — 2, skill, "Add 3 random Attacks into your Draw Pile. They're free to play this combat. Exhaust." (Spirit Grafter event)
- `Sea-Salt Prayer+` — 1, skill, "Gain 7 Block. Apply 2 Weak." (elite 5)
- `Itto — Superlative Superstrength (proto)` — 2, attack, "Deal 14 damage. Gain 12 Block." (boss)

One `Kamisato Ayaka — Soumetsu` carries the enchantment **`Perfect Fit`** — "Whenever this would be
shuffled into your Draw Pile, place it on the top instead" — from the Field of Man-Sized Holes.

**Rooms cleared in act 2, in order:** Orobas (event), fight 6 Thieving Hopper, The Lost Wisp (event),
fight 7 Tunneler, fight 8 Chomper x2, shop, elite 4 Infested Prism, shop, treasure, fight 9 Myte x2,
fight 10 Bowlbug x3, Field of Man-Sized Holes (event), Spirit Grafter (event), elite 5
Decimillipede x3, rest site, **BOSS The Insatiable**. Sixteen rooms, no room skipped, no fight lost.
Seven of the sixteen map screens offered exactly one node.

---

## Event 1 (act 2, floor 1) — Orobas

Picked up from the act-2 map at the only offered node, `Ancient (path 1)`.

```
# Orobas
- **Gear Glass**      See 15 cards from The Defect. Choose any number of them to add to your Deck.
- **Sand Castle**     Upon pickup, Upgrade 6 random cards.
- **Touch of Orobas** Replace Tamakushi Casket with Circlet.
```

`Touch of Orobas` was never in play: the Casket is the glue of this deck (the previous seat proved it
re-arms the aura the next off-element card reacts with), and `Circlet` is a word this screen never
defines. So the real choice was **6 guaranteed random upgrades against a look at 15 cards with the
option to take none**. I took **Gear Glass** because choice-with-sight beats a random roll, and
because the option's own text ("choose any number") means the floor is zero, not a forced bad card.

The 15 were all Defect cards and **not one of them carries an element tag** — no `[Hydro]`,
`[Electro]`, `[Pyro]`, `[Cryo]`. That is the whole verdict on this screen: my deck's real engine is
the reaction chain, and fourteen of these fifteen cards cannot touch it. Twelve of the fifteen also
reference `Orb`, `Channel`, `Evoke`, `Focus` or `Orb Slot` — machinery my character has no printed
access to (one of the fifteen, `Modded`, is "Gain 1 Orb Slot", which reads like an admission that I
have none).

I took exactly one: **`Go for the Eyes`** — cost 0, attack, "Deal 3 damage. If the enemy intends to
attack, apply 1 Weak." At 0 energy it is 3 damage **plus** a debuff, and a debuff is 2 more Hydro
damage off the Casket *and* an aura for the next card to react with. It is the only card on the
screen that pays the relic. I declined the other fourteen.

**Silently granted:** the option `Gear Glass` also became a **relic**. It appears in the next battle
screen's relic list reading "See 15 cards from The Defect. Choose any number of them to add to your
Deck." — the event text verbatim, as a permanent relic. Nothing on the event screen said I was
picking up a relic, and as a relic that line describes an action that has already happened once and
cannot happen again.

**Silently granted, second:** the previous seat left the lane at **HP 58/87**. The first battle
screen of act 2 reads **HP 81/87**. **+23 HP arrived with no screen printing it** — not the map, not
the event, not a reward. It is not 30% of max (26) and not a full heal (29). I cannot say what paid it.

---

## Fight 6 — Thieving Hopper (79 HP)

Entered at **81/87**, `Block 10` from Anchor before playing anything, deck 23.

```
- **Thieving Hopper** — HP 79/79
    Intent: Aggressive (Attack) — the number on its icon is 17
    Escape Artist 5 (buff) — Tries to escape the combat after 5 turns.
```

A shot clock written into a buff line: 5 turns to kill 79 HP or it leaves. Clean, and it counts down
visibly (5 → 4 → 3).

**Round 1.** Hand: Amber, Strike, Defend, Undertow+, Battle Plan. 3 energy.
**Predicted:** `Battle Plan` onto the Kurage (next turn +1 energy and draw 2, worth more than the 6
damage a Strike buys now), `Undertow+` for 10 and a Hydro aura, `Amber` banked so its 8 Pyro lands
*into* that Hydro aura for 12. Enemy to 57, me to 77.
**Happened: exactly that.** 79 → 69 (Undertow's printed 10; no Casket proc, because an aura is not a
debuff) and 69 → 57 across the enemy turn, i.e. **Amber's printed 8 Pyro landed for 12**. Third
independent confirmation of Pyro-into-Hydro ×1.5, a multiplier no screen names.

**A thing the screen did well:** the moment `Baron Bunny` went up, the enemy's intent line rewrote
itself from **17 to 14** — the printed intent is the number *after* my mitigation. HP went 81 → 77,
exactly 14 − 10 Block. The previous seat could not tell whether Baron Bunny's −3 applied on a given
turn; here the intent line answers it before I commit.

**A thing the screen did not do at all:** at the start of round 2 the enemy carried a new buff,
`Swipe 1 (buff) — Upon killing this enemy, the stolen card is returned.` **No line anywhere said a
card had been stolen, or which one.** The only hard evidence is arithmetic: round 1 was draw 18 +
hand 5 = 23 = my whole deck; round 2 is draw 10 + discard 5 + hand 7 = **22**. One card left my piles
during the enemy's turn and the game reported it only obliquely, through a buff on the thief.

**Round 2.** Energy **4/3** (Battle Plan's plan resolved), enemy 57, intent Empower — a free turn.
The Kurage having carried out a Plan *this turn* switches `Sango Isshin` from "Deal 8" to "deal a
quarter of your Max HP to ALL enemies" = 21.
**Predicted:** `Lightning Fang` (1) → `Go for the Eyes` (0) for 3+3 = 6, its Fang-Electro applying an
Electro aura to a bare enemy → `Sango Isshin` (2) for 21 Hydro **into** that Electro aura =
Electro-Charged → Poison 4 +1 Snecko = 5, the Poison being a debuff so the Casket fires 2 Hydro and
re-arms Hydro → `Strike` (1) for 6+3 = 9 whose Fang-Electro consumes that re-armed Hydro for a second
Electro-Charged, +5 Poison, +2 Casket. Total **6 + 21 + 2 + 9 + 2 = 40**, Poison 10, enemy to 17.
**Happened: exactly 40** (57 → **17**), **Poison exactly 10**, `Hydro Aura 2` standing. The whole
four-card chain resolved to the number.

Two precise facts fall out of that arithmetic:

- **Sango's "a quarter of your Max HP" is a flat 21 and does NOT take `Lightning Fang`'s +3.** The
  same Fang gave `Go for the Eyes` 3→6 and `Strike` 6→9 on the same turn. Had Sango taken it the
  total would have been 43, not the 40 measured.
- **Lightning Fang's Electro reacted on both attacks here** — the boss-round-3 behaviour the previous
  seat recorded, not the elite-1 behaviour. My instance is a clean 2-for-2.

**Round 3.** The Empower turned out to be `Flutter 5 (buff) — Receives 50% less damage from Attacks.
Deal attack damage 5 times to Stun it.` Enemy at 7 (Poison had ticked it 17 → 7, exactly) with
Poison 9 and an intent of 21. Poison alone would have killed it, but energy does not carry over, so
killing it myself was free insurance: `Uproar` (9 twice under Fang, halved by Flutter, plus the
reaction) ended it. **Zero damage taken on rounds 2 and 3.**

**Result: won on round 3 at HP 77/87, 10 damage taken.**

### Fight 6 rewards

`13 Gold`, `15 Gold` (Amethyst Aubergine's separate row again), `Colorless Potion`, **`Take your
stolen card back.`**, and a card. The stolen-card reward is the only place the theft is ever named,
and it is named *after* the fight, still without saying which card.

Card reward (four options, the Casket's fourth Companion slot being `Lynette`):

- `War Council` — 1, skill, Plan: "Deal 5 damage and apply 1 Weak to ALL enemies."
- `Song of Pearls (proto)+` — 1, power, "Once per turn, when the Bake-Kurage carries out a Plan, gain 4 Block."
- `Vanguard` — 0, skill, Plan: "Apply 1 Vulnerable and 1 Weak. Exhaust."
- `Lynette — Enigmatic Feint` — 1, skill, "Swirl an enemy's aura. Gain 5 Block."

Took a **second `War Council`**. The real contest was against a second `Vanguard`: Vanguard is free
and applies Vulnerable, but it **Exhausts** and the glossary says "Plans hit the front enemy", so it
is one enemy, once per fight. War Council does not exhaust, hits **ALL** enemies for 5 (7 with the
Casket) and Weakens all of them, and — the reason that decided it — every War Council turn is also a
turn `Sango Isshin` is live at 21 AoE. Two copies means I can arm Sango on consecutive turns.

`Lynette — Enigmatic Feint` says "Swirl an enemy's aura" and **no glossary line on the screen defines
Swirl**, the second time this run a card has been offered with an undefined verb as its only
mechanic (`Sayu — Yoohoo Art: Fuuin Dash` did it in act 1).

---

## Fight 7 — Tunneler (87 HP)

Entered at **77/87**. Draw 19 + hand 5 = **24**, i.e. 23 + the War Council I had just taken — so the
stolen card *was* returned, and the return is confirmable only by counting piles.

On this screen the glossary line for **Plan** changed wording from every previous screen. It had read
"Play this on the Bake-Kurage: it carries out the Plan line at the start of your next turn. Cost is
paid now. Plans hit the front enemy." It now reads:

> **Plan** — On the Bake-Kurage, paid now; the Plan lands first thing next turn on the front enemy.
> **Enemy Vulnerable raises it; your Weak does not.**

That second sentence is the answer to the previous seat's sharpest unexplained mechanic (Shrink
visibly rewrote Strike from 6 to 4 while the plan dealt its full 7). The rule *is* printed — just not
on the screen where it first mattered, and only in one of the two wordings the same word gets.

**Round 1.** Intent Attack 13. Hand: Slack Water, Undertow+, Go for the Eyes, Battle Plan, Defend.
**Predicted:** `Go for the Eyes` (0) — it intends to attack, so Weak lands, so the Casket adds 2:
3+2 = **5**; `Undertow+` (1) now reads 13 because the enemy has a debuff; `Slack Water` (1) 4 + Weak
+ Casket 2 = **6**; `Battle Plan` (1) onto the Kurage. Total **24**, and Weak takes 13 down to 9,
which Anchor's 10 Block eats whole.
**Happened: exactly 24** (87 → **63**), the intent rewrote itself 13 → 9 the moment Weak landed, and I
took **0**.

**Round 2.** Energy 4/3, intent "Empower (Buff) **and also:** Defensive (Defend)" — the screen prints
*both* halves of a two-part intent, which is more than most screens show.
**Predicted:** the Kurage had carried out Battle Plan this turn, so `Sango Isshin` (2) = 21 to all;
then `Kamisato Ayaka — Soumetsu` (2), whose end-of-turn 8 Cryo would land on the Hydro aura Sango
refreshes = **Frozen**, a debuff, so +2 Casket. 21 now, 10 at end of turn.
**Happened: exactly.** 63 → **42** from Sango, then 42 → **32** across the turn end (8 Cryo + 2
Casket), with `Hydro Aura 1` back on the board — the Casket Hydro hit re-arming the aura its own
reaction had just consumed, exactly as the previous seat reconstructed.

Its Empower was `Burrowed 1 (buff) — Block is not removed at the start of Tunneler's turn. Stunned if
all Block is removed.` and it took **Block 32**. That is a good puzzle: 32 Block that does not decay,
with a printed reward (a Stun) for stripping it.

**Round 3.** 32 HP behind 32 Block, intent 23.
**Predicted:** `Vanguard` (0) onto the Kurage, `Uproar` (2) at 9 twice under Fang, `Strike` (1) at 9 —
about 27 from cards, plus Soumetsu 8 + 16 at end of turn, which should strip the block and Stun it.
**Happened:** Block 32 → **8**, i.e. **24** from cards. Uproar two hits (18) plus Strike (6, since
Fang had expired) is 24 — which leaves **nothing at all for Uproar's "Play a random Attack from your
Draw Pile."** The draw pile did drop by one extra (15 → 14 with only three cards played) and the
discard rose by one extra, so a card *was* drawn and played; the Kurage read "Nothing is planned. The
morning is empty." So it was played, not planned, and it contributed **0 measurable damage**.
**No screen anywhere names the card Uproar plays or reports what it did.**

At the turn end Soumetsu 8 + 16 stripped the last 8 Block and took the enemy 32 → **6** (24 Cryo, one
Frozen reaction, +2 Casket), and at the start of round 4 the Vanguard plan applied Vulnerable + Weak,
which cost the enemy a further **8 HP through Casket procs alone**.

**Round 4.** 6 HP, Vulnerable 1 — one Strike (9 × 1.5) ended it.

**Result: won on round 4 at HP 77/87 — zero damage taken in the entire fight.**

Rewards `20 Gold`, `15 Gold`, and a card from `Stolen Chapter (proto)`, `Rally`, `Treatise+`,
`Kujou Sara — Crowfeather Cover (proto)`. Took **Kujou Sara** — cost **0**, "Your next Attack this
turn deals 4 additional damage and applies Electro." At zero energy it is 4 free damage *and* an
element-setter, which on this deck means a free Electro-Charged whenever the Casket has left a Hydro
aura lying around.

---

## Fight 8 — Chomper x2 (60 HP and 64 HP)

Entered at **77/87**, deck 25 (draw 20 + hand 5). Both Chompers carried
`Artifact 2 (buff) — Negates 2 debuffs.` — the hardest counter to this deck act 2 has shown me,
because every debuff I apply is also a Casket proc and an aura.

**Round 1.** Intents 8x2 and "give you 3 Status cards".
**Predicted:** `Kujou Sara` (0) → `Razor — Claw and Thunder` (1) for 8+4 = **12** → `Strike` (1) 6 →
`Defend` (1) for 6, giving 16 Block against 16 incoming = **0 damage**, 18 dealt.
**Happened: exactly 18** (60 → **42**) and **exactly 0 taken**. `Electro Aura 2` landed on the target
and **Artifact was untouched**, which is the screen own aura note ("an aura is tagged `(aura)` rather
than `(buff)` or `(debuff)`, because it is neither") paying off as a rule you can plan around: auras
slip past Artifact, debuffs do not.

**Round 2.** `Lightning Fang` (1) → `Go for the Eyes` (0) → `Uproar` (2) into Chomper (1).
**Predicted** about 33. **Happened: 24** (42 → **18**) — 6 + 9 + 9, and once again **the Uproar random
attack did nothing measurable**, with the pile counts again showing that a card was drawn and played.
Two fights, two Uproars, two unattributable random attacks.

I took the printed 16 (77 → **61**) and Chomper (2) gave me 3 Status cards silently: no line, no face,
just hand + draw + discard rising from 25 to 28.

**Round 3 opened with a number I cannot explain.** Chomper (1) had been left at **18** at the end of
my round 2. At the start of round 3 it read **9/60**. It carried no Poison, no aura-borne DoT and no
debuff of any kind; the Bake-Kurage block read "Nothing is planned. The morning is empty." with no
"carried these out" line; nothing of mine was pending. **9 HP left an enemy with no printed cause.**

**Round 3.** Killed Chomper (1) with a Fang-boosted `Strike` for exactly its remaining 9, put
`Undertow+` into Chomper (2) for exactly **13**, and stacked two plans (`Vanguard` then `Battle
Plan`). Undertow is a **[Hydro]** card and it left an **Electro Aura** — so **`Lightning Fang`
overrides a card own printed element**, which is the cleanest explanation available for the previous
seat "Fang reacts inconsistently" finding.

**Round 4** proved the Artifact rule outright: the Vanguard plan applied Vulnerable and Weak, both
were negated, **both Artifact stacks were consumed, and the enemy took exactly 0** — it stood at 51
before and 51 after. **A negated debuff also cancels its Casket proc.**

Then, with Artifact stripped: `Slack Water` (1) → 51 → **43**, which is **8**, not the 6 that 4 damage
plus one Casket proc predicts. Two debuffs landed off that one card (Weak, and Poison from the
Electro-Charged reaction) and **the Casket fired twice for them**. That directly contradicts the
previous seat elite-1 reading that the Casket fires at most once per card.

`Amber` + `Ayaka` then produced exactly the chain I priced: end of turn Ayaka 8 Cryo into the Casket
Hydro = Frozen, +2 Casket (43 → 33); Poison 5 at the start of its turn (→ 28); Amber 8 Pyro into the
re-armed Hydro = Vaporize x1.5 = 12 (→ **16**). **27 predicted, 27 measured.** I took 4 where the
intent printed 3x2 — Frozen had halved the whole action.

**Round 5** needed no cards: Soumetsu 8 + 16 at the end of my turn killed it from 16, before it could
hand me three more Status cards.

**Result: won on round 5 at HP 57/87, 20 damage taken.** Rewards `15 Gold` x2, `Speed Potion`, and a
card I **skipped** (`Song of Pearls (proto)+`, `The Clouds Like Waves Rippling`, `Salt Line (proto)`,
`Sucrose — Astable Anemohypostasis (proto)`) — none of them beat what my deck already does, and at
that point I believed my deck was carrying 9 dead Status cards.

**The Status cards do not persist.** The shop Card Removal screen, two rooms later, listed my deck in
full: **exactly 25 cards, and not one Status among them.** Twelve Status cards had been forced on me
across act 1 and act 2 and every one of them was gone. The previous seat inference that three were
permanently added (from a 22-vs-19 pile count) does not survive a look at the actual list.

---

## Shop (act 2, floor 6)

The shop screen prints gold but **never prints HP**, so `Meal Ticket` ("Whenever you enter a shop
room, heal 15 HP") gives no visible confirmation at the moment it fires.

**Gold does not reconcile.** Adding up every reward row I claimed since the previous seat stop:
304 (act-1 close) + 13 + 15 + 48 + 20 + 15 + 15 + 15 = **445**. The shop screen read **647**. I cannot
account for 202 gold from anything a screen printed.

Stock, verbatim in price order: `Tungsten Rod` 296 ("Whenever you would lose HP, lose 1 less"),
`Letter Opener` 257, `Orrery` 171 ("Upon pickup, gain 5 card rewards"), `Gorou — Crystal Collapse` 77,
`Song of Pearls (proto)` 75, `Card Removal` 75, `Sango Isshin (proto)` 72, `Kujou Sara — Tengu
Stormcall (proto)` 72, `Salt Line (proto)` 51, `Deep Current` 49, `Sea-Salt Prayer` 49, and three
potions at 48-52.

**Bought:** `Orrery` (171), `Sango Isshin (proto)` (72), `Tungsten Rod` (296), `Card Removal` (75) —
614 of 647, leaving 33.

The five `Orrery` card rewards are worth recording on their own:

- Reward 1 offered **three** options, not four: the Casket promised fourth Companion slot is
  specifically "Card rewards **after a fight**", and a relic-granted reward is not one. Took
  **`The General's Banner+`** — 1, power, Innate, "Once per turn, when you play a Companion card,
  apply 1 Weak to the front enemy." Innate removes the draw variance, and on this deck a Weak is also
  a Casket proc and a fresh Hydro aura.
- Reward 2: took **`Moon's Reflection+`** — cost **0**, "Choose a card in your Exhaust Pile. Next
  turn, the Bake-Kurage carries out its Plan line, or plays it if it has none. Exhaust." My exhaust
  pile fills with `Kamisato Ayaka — Soumetsu` (32 Cryo AoE). Replaying that for zero energy is the
  largest number anyone has offered me. Its cost line is also the best-written text in the game:
  "The cost printed on this card is 1; it is showing 0 here, because this copy is upgraded — that is
  permanent."
- Reward 3: took **`Deep Current`** [Hydro] — 1, "Deal 6 damage to ALL enemies", my only cheap AoE and
  a Hydro applier that arms a whole board for a Cryo or Pyro follow-up.
- Rewards 4 and 5 offered the **identical three cards** (`Cleansing Wave`, `Treatise`, `Coral
  Bulwark`). I skipped both — and **skipping did not consume the row**: after five `choose` calls the
  screen still listed two "Add a card to your deck." rows. Reopening one showed **the same three cards
  a third time**; the offer does not reroll. I took `Coral Bulwark` in the end and left the last row on
  the screen, where `proceed` discarded it.

**Card Removal** listed the deck as **25 cards** — which is the deck *before* the five cards I had
just added in this same shop (`General's Banner+`, `Moon's Reflection+`, `Deep Current`, `Coral
Bulwark`, the bought `Sango`). The removal screen is stale by a full shop visit. Removed a `Defend`.

---

## Elite 4 — Infested Prism (161 HP)

Entered at **72/87** — which is 57 + 15, so `Meal Ticket` did fire on the shop, though the shop screen
never printed an HP line and this battle screen is the first confirmation. Draw 24 + hand 5 = **29**,
which is 25 − 1 removed + 5 added, so the shop purchases *had* applied and the Card Removal screen was
simply showing a stale list.

```
- **Infested Prism** — HP 161/161
    Intent: Aggressive (Attack) — the number on its icon is 15
    Vital Spark 2 (buff) — ALL Skills are Tainted 2.
```

`Vital Spark` is the best-designed enemy rule I met in act 2, and it is aimed squarely at this deck:
19 of my 30 cards are Skills, and every Plan card — the whole `Sango Isshin` engine — is a Skill.

The card faces did the right thing immediately: `Defend` re-printed as "Gain 6 Block. **Gain 2
Tainted.**", `Kurage's Oath` as "...Deal 7 damage to ALL enemies. **Gain 2 Tainted.**", and when the
elite later Empowered to `Vital Spark 4` every one of those lines re-printed as "Gain **4** Tainted".

**The glossary for it is circular and useless.** The Words-on-this-screen entry reads, in full:

> **Tainted** — Gain 2 Tainted when played.

That says what applies it, not what it does. The actual rule only appears once you have some, on your
own status line: `Tainted 2 (debuff) — Take 2 additional damage from Attacks this turn.` So the one
place a player can price the decision *before* making it is the one place the text is empty.

**Round 1.** `Slack Water` (4 + Weak + 2 Casket = 6) then two `Strike`s.
**Predicted 18 dealt and 0 taken** — Weak drops the 15 to 11, Anchor's 10 Block plus Tungsten Rod's −1
eats the rest. **Happened: exactly 18** (161 → 143) and **exactly 0 taken**.

**Round 2.** `Razor — Lightning Fang` (1, and my first Tainted) then `Uproar` (2).
**Predicted about 22.** **Happened: 40** (143 → **103**) with **Poison 15**. Poison 15 is three
Electro-Charged reactions at 4 + 1 Snecko, so all three of Uproar's attacks reacted — its two hits and
**its random attack, which for the first time in three fights visibly did something**. The only
arithmetic that closes is 9 + 2 + 9 + 2 + **16** + 2 = 40, and 16 is exactly `Undertow (proto)+`
(13 against a debuffed enemy, +3 from Fang). So the random attack pulled Undertow and dealt 16 — and
I know that only by solving for it. **No screen names the card Uproar plays.**

**Round 3 is where `Vital Spark` bites**, and it is a genuinely good puzzle. The intent was `5x3`.
Tainted is "+n damage from Attacks", and against a three-hit intent that is +n *per hit*. So a
`Defend` that buys 6 Block also buys 6 extra incoming damage. I worked it three ways:

- no skills at all: 3 × 5 = 15, −3 Tungsten Rod = **12**
- one skill (`Coral Bulwark`, 7 Block): 3 × 7 = 21, −7 Block, −3 Rod = **11**
- two skills: 3 × 9 = 27, −13 Block, −3 Rod = **11**

**Blocking against this enemy is worth about one hit point.** That is a real, legible, printed trap,
and it is the only fight in either act where the correct answer was "do not defend".

I played `Razor — Claw and Thunder` (11 under Fang, +2 Casket = 13, of which Block 11 ate 11 → enemy
88 → **86**, Poison 14 → **19**), then `Amber` and `Coral Bulwark`.
**Then the intent lied.** With `Tainted 4` and `Baron Bunny` up, the screen printed **`6x3`** = 18. I
had 7 Block and Tungsten Rod, so 18 − 7 − 3 = 8 expected. **I took 15** (60 → 45). The number that
reconciles is 3 × 9 (5 + 4 Tainted) − 3 Baron Bunny − 7 Block − 3 Rod ≈ 14–15. **The printed multi-hit
intent understated the real damage by about 7.**

**Round 4** was the best turn of the act and it came out of a card interaction, not a big number:
`Pounce` (2) → its "the next Skill you play costs 0" paid for `Kamisato Ayaka — Soumetsu` (2 → **0**)
→ leaving exactly 1 energy for `War Council` onto the Kurage. Three cards, 3 energy, for what should
cost 5. Pounce dealt exactly **14** (55 → 41).

**And then the intent lied the other way.** With `Tainted 4` the single-hit intent printed **12**
(8 + 4), which is correct — Tainted *is* folded into a one-hit intent. I then took **5**, not 11
(45 → 40). Same fight, same debuff: the intent under-reported by 7 on a three-hit attack and
over-reported by 7 on a one-hit attack, and I cannot reconcile either from the screen.

**Round 5.** The elite had Empowered `Vital Spark` from 2 to 4 and sat at 13 HP behind 13 Block with
Poison 17, and `Soumetsu` was due to fire 8 + 16 at my turn end. Two attacks and no skills (so no
Tainted) put it out of reach: `Strike` for 6, then Soumetsu's 24 for 30 total against 26.

**Result: elite down on round 5 at HP 40/87, 32 damage taken.**

**My one refusal of the act happened here**, and it was a good one:

> `'Deep Current' does its own aiming, so it takes no `on "Infested Prism"`. The form that resolves:
> play "Deep Current"`

It names the exact string that would have worked.

### Elite 4 rewards, and a fixed defect

`36 Gold`, `15 Gold`, `Energy Potion`, `Juzu Bracelet`, and a card. The screen printed:

> *Your potion slots are full: 3 of 3. A potion claimed now has nowhere to go, and the game says
> nothing when one is dropped -- so this page will not claim it until a slot is free.*

That is a direct fix for the previous seat's finding that a selected `Power Potion` was silently not
granted. The belt size, the fullness and the consequence are all printed, and the page refuses to
throw the potion away on my behalf. I left the `Energy Potion` unclaimed.

Card reward: `Nereid's Ascension (proto)` (2, Plan: for 2 turns the Kurage carries out every Plan
twice), a third `Sango Isshin`, `Cleansing Wave`, and **`Shinobu — Grass Ring of Sanctification
(proto)`** — cost **0**, "Gain 4 Block. If you lost HP this turn, gain 4 additional Block."

Took Shinobu. At 0 energy 4–8 Block already beats `Defend`'s 6-for-1, but the reason is that Shinobu
is a **Companion** card, so it also trips `The General's Banner+` for a free Weak — and a Weak on this
deck is a Casket proc (2 Hydro damage) plus a fresh Hydro aura for the next off-element card. One
zero-cost card doing four things is the tightest design I have been handed all act.

---

## Shop 2 (act 2, floor 8)

Entered at 40/87 and, again with no printed confirmation, `Meal Ticket` took me to **55/87**.

**Gold reconciled exactly this time:** 33 left over + 36 + 15 from the elite = **84**, which is what
the screen read. Whatever produced the 202-gold discrepancy at the first shop did not recur.

**Card Removal had risen from 75 gold to 100** — the price is not fixed between shops, and nothing on
either screen says so.

Stock included `Sango Isshin (proto)` at **156 gold**, where the first shop sold the identical card
for **72**. Same card, same act, same run, 2.2x the price, with no visible reason.

Bought **`Vanguard`** (51) — a second 0-cost Plan enabler. With two `Sango Isshin` in the deck, a free
card that turns them both from "Deal 8" into "21 to ALL enemies" is the cheapest damage on the shelf.
Left with 33 gold.

---

## Treasure (act 2, floor 9) — Intimidating Helmet

> **Intimidating Helmet** — Whenever you play a card that costs [Energy][Energy] or more, gain 4 Block.

Taken. Six of my cards cost 2, so it is roughly a free `Defend` on any turn I play one.

The battle screen after it also finally printed the relic I had claimed off the elite:
**`Juzu Bracelet` — "Regular enemy combats are no longer encountered in ? rooms."** That is a routing
fact, and it is the only relic in the run that changes how I read the map: from that point every
`Unknown` is a guaranteed non-combat room.

---

## Fight 9 — Myte x2 (64 HP and 67 HP)

Entered at **55/87**, deck 30.

**Round 1.** Incoming was only 4, so the turn was pure setup: `Vanguard` (0) onto the Kurage,
`Deep Current` (1) for 6 to both (arming Hydro on both), `Kamisato Ayaka — Soumetsu` (2).
**Predicted 16 to each** — 6 from Deep Current, then Ayaka's end-of-turn 8 Cryo landing on that
Hydro for a Frozen plus a 2-damage Casket proc.
**Happened: exactly 16 to Myte (2)** (67 → 51). Myte (1) took **22**, the extra 6 being Vanguard's
plan at the start of round 2: it applies Vulnerable and Weak, and the Casket procs for those are
themselves amplified by the Vulnerable the same plan just applied — 2 x 1.5, twice. That is the
identical 6 the previous seat measured on the act-1 boss, reproduced exactly.

I took **0**.

**This is the fight where I finally saw a Status card's face**, and it matters:

> **Toxic** — cost 1, status. "At the end of your turn, if this is in your Hand, take 5 damage.
> Exhaust."

Two of them arrived in my round-2 hand. Across act 1 and act 2 the previous seat and I have been
handed twelve Status cards by three different enemies and this is the first time either of us has
seen what one does. They are not filler: two in hand is 10 HP, and the card is the reason the
`Strategic (StatusCard)` intent is a real threat rather than a deck-thinning nuisance.

**Round 2.** The Kurage had carried out Vanguard's plan, so `Sango Isshin` was live.
`Sango` (2) + `Kujou Sara` (0) + `Undertow+` (1).
**Predicted** Myte (1) to 11 and Myte (2) to about 13, with Soumetsu's 8 + 16 killing both at the
turn end. **Happened: Myte (1) to exactly 11** — 42 − 31, i.e. Sango's 21 raised to 31 by
`Vulnerable`, so **Vulnerable does multiply Sango's quarter-Max-HP mode** — and Myte (2) to 14.
Both died to Soumetsu at the end of my turn, before Myte (2) could hand me two more Toxics.

**Result: won on round 2.** The Toxics cost me 4 on the way out (55 → 51), which is one Toxic's 5
less Tungsten Rod's 1; the second one seems not to have fired, and no line says why.

Card reward: took **`Change of Plans+`** — 1, skill, "The Bake-Kurage carries out your first Plan
**now**", and this upgraded copy does not Exhaust. That converts the whole Plan engine from a
tempo tax into a same-turn combo: `Vanguard` (0) writes a plan, `Change of Plans+` (1) fires it
immediately, and `Sango Isshin` (2) is live on the same turn for 21 to ALL — 3 energy, from a cold
start, repeatable.

---

## Fight 10 — Bowlbug x3 (Rock 45, Silk 41, Egg 21)

Entered at **51/87**. The best-signposted fight of the act:

> **Bowlbug (Rock)** — Imbalanced 1 (debuff) — If Bowlbug (Rock)'s attacks are fully blocked, it
> becomes Stunned.

Rock's intent was 15 and Anchor gives 10 Block for free, so one `Defend` (6) puts me at 16 and buys a
Stun. That is a printed, exact, checkable target number, and it is the kind of thing this game does
well when it does it at all.

**Round 1.** `War Council` (1) onto the Kurage, `Defend` (1) to reach 16 Block, `Razor — Claw and
Thunder` (1) into Rock for 8 and an Electro aura.
**Happened: Rock Stunned** and I took **exactly 5** (Rock's 15 fully absorbed, Egg's 7 through the
last 1 of Block, less Tungsten Rod).

At the start of round 2 War Council's plan hit all three, and the numbers separate the Casket's rule
cleanly: **Rock lost 7, Silk lost 5, Egg lost 5 into its Block.** All three got Weak. Rock's extra 2
is the Casket, and Rock is the front enemy — so **one plan that applies a debuff to three enemies
produces exactly one 2-damage Casket proc, on the front enemy only.** Rock also picked up `Poison 5`,
because the plan's damage is Hydro and Rock was wearing the Electro aura my Razor Claw had left.

**Round 2** produced the sharpest card-text finding of the act. `Kujou Sara` (0) then `Sango Isshin`
(2), with `Vanguard` and `Kurage's Oath` written onto the Kurage behind them.

Sango's live mode should have been 21. I was carrying `Weak 1` (Silk had debuffed me). Kujou Sara
promises "Your next Attack this turn deals **4 additional damage** and **applies Electro**."

**Sango dealt exactly 15 to each of the three** (Rock 30 → 15, Silk 36 → 21, Egg 21 → 8 through
2 Block). 15 is 21 x 0.75. So:

- **My `Weak` DOES reduce Sango's quarter-Max-HP mode** (21 → 15).
- **Kujou Sara's +4 does NOT apply to it** (it would have been 18, not 15).
- **Kujou Sara's "applies Electro" does NOT apply to it either** — all three enemies came out of it
  wearing `Hydro Aura 2`, refreshed, with no Electro-Charged and no new Poison anywhere.

That last one is the contradiction, because two fights earlier `Razor — Lightning Fang` *did* override
`Undertow (proto)+`'s printed [Hydro] and leave an Electro aura. So one element-override effect
overrides a card's element and another does not, and the difference is invisible in both card texts.
The consistent reading is that **Sango's alternate mode ignores every attack modifier except Weak** —
but nothing on the card says it is anything other than an Attack.

**Round 3.** Rock died at the start of the turn to Poison 5 plus the `Kurage's Oath` plan, which
`Vanguard`'s Vulnerable raised — exactly what the Plan glossary promises ("Enemy Vulnerable raises
it"), and the first place in the run where that printed sentence was directly confirmed.
`Deep Current` + `Strike` + a banked `Amber` finished Silk and Egg on the enemy turn.

**Result: won on round 3 at HP 41/87, 10 damage taken.**

Card reward: took **`Amber — Fiery Rain`** [Pyro] — 1, "Deal 4 damage to ALL enemies 3 times." Twelve
to every enemy for one energy is the best AoE rate I have been shown, the first hit Vaporizes off any
Hydro aura my own Casket keeps re-arming, and it is a Companion card so it also trips
`The General's Banner+`.

---

## Event — Field of Man-Sized Holes

> - **Resist** — Remove 2 cards from your Deck. Add Normality to your Deck.
> - **Enter Your Hole** — Enchant a card with Perfect Fit.

**Neither `Normality` nor `Perfect Fit` is defined anywhere on the screen**, which makes this the
third and fourth unpriceable proper noun of the act after `Circlet`, `Decay` and `Lost Wisp`. I took
`Enter Your Hole` on one piece of structural evidence rather than any text: **the game let me choose
the target**, and games do not usually let you aim a curse. The follow-up screen listed my whole deck
and still never said what Perfect Fit does. I put it on `Kamisato Ayaka — Soumetsu`. **No screen has
told me what changed**, and I never drew that copy again before the stop.

## Event — Spirit Grafter

> - **Let It In** — Heal 25 HP. Add Metamorphosis to your Deck.
> - **Rejection** — Lose 10 HP. Upgrade a card.

`Metamorphosis` is the fifth undefined proper noun. It did not matter: I was at **41/87** with a
forced Elite on the only outgoing path, and the elite before it had cost me 32. `Rejection` would
have put me into that fight at 31. Took **Let It In** for 25 HP.

---

## Elite 5 — Decimillipede x3 (44 / 46 / 42 HP)

Entered at **63/87** (the Spirit Grafter heal landed on 38, not the 41 I had last seen — the last
Bowlbug's hit went through as the fight ended, and no screen printed the intervening HP).

```
Reattach 25 (buff) — If other segments are still alive, revives in 2 turns with 25 HP.
```

This is the hardest room in act 2 and the rule is the whole reason. Killing a segment while any other
lives buys you a 25 HP segment back two turns later, so the fight punishes exactly what my deck is
best at — focusing one target down — and rewards the thing it is worst at: bringing three health bars
to zero on the same tick.

**Round 1.** `The General's Banner+` (1), then `Kujou Sara` (0) — a Companion, so Banner applied Weak
to the front segment, the Casket proc'd 2 and left a Hydro aura — then a Sara-boosted `Strike` into
that segment, whose Electro consumed the aura for an Electro-Charged.
**Predicted 14 to segment 1. Happened: exactly 14** (44 → 30), Poison exactly 5. Banner does what it
says, and the chain Banner → Weak → Casket → Hydro aura → Electro card → Poison is a genuine engine
that costs one card.

**Round 2** produced the run's most misleading event text. `Metamorphosis`, the card the Spirit
Grafter charged me for healing, turned out to read:

> **Metamorphosis** — cost 2, skill. "Add 3 random Attacks into your Draw Pile. They're free to play
> this combat. Exhaust."

That is a **good** card. The event framed it as the price of 25 HP ("Heal 25 HP. **Add Metamorphosis
to your Deck**"), in the same grammatical slot where `Resist` put "Add Normality to your Deck" as an
explicit cost. One of those two is a drawback and one is a benefit and the screen presents them
identically.

**Rounds 3–6** were a grind against the revive. Round 3 killed segment 1; round 5 it was back at
**25/44** while a different segment sat at 1 HP with `Strength 4` and a 9x2 intent — 26 incoming
against my 25 HP. That turn was the only point in the act where I was in real danger, and the answer
was entirely printed: `Deep Current` (showing **cost 0**, one of Metamorphosis's free attacks) killed
the 1 HP segment outright, `Coral Bulwark` bought 7 Block, `Kamisato Ayaka — Soumetsu` bought 4 more
off `Intimidating Helmet`, and I took **0**.

The kill came from reading `Reattach` literally. On round 6 the two live segments sat at **3** and
**9**, both wearing Hydro auras, with Soumetsu due to fire 8 Cryo at my turn end. Cryo into Hydro is
Frozen, which is a debuff, which is a Casket proc — so that single 8 lands as **10 on each**, and 10
kills both **on the same tick**, so neither is ever "still alive" while the other dies.
**No revive, and the fight ended.**

**Result: elite down on round 6 at HP 25/87, 38 damage taken** — by far the most expensive room of
the act.

That turn is the best thing in act 2. The rule is printed, the counter-play is printed, the numbers
needed to execute it are printed, and it is not the obvious line.

Rewards: `36 Gold`, `15 Gold`, an `Explosive Ampoule` the page again refused to drop on my behalf,
**`Candelabra`** ("At the start of your 2nd turn, gain [Energy][Energy]"), and a card — took
**`Sea-Salt Prayer+`** (1, "Gain 7 Block. Apply 2 Weak"), which is block, two Casket procs and a fresh
aura on one card, for the boss.

## Rest site (act 2, floor 15)

`HP 25/87`. Rest heals 30% of max (26). Took it: **51/87**. An upgrade I could not name in advance
was not competitive with 26 HP against a boss I had not seen.

---

## BOSS — The Insatiable (321 HP)

Entered at **51/87**, deck 35, with 13 relics.

```
- **The Insatiable** — HP 321/321
    Intent: Empower (Buff) — This enemy intends to use a Buff.
      and also: Strategic (StatusCard) — the number on its icon is 6 — intends to give you 6 Status cards.
```

Six Status cards on the opening turn, and I now knew from fight 9 what one of those can be
(`Toxic`: 5 damage a turn while it sits in hand). That is a real opening threat and it is legible
only because a Myte had shown me a Toxic two fights earlier.

**Round 1 takes no damage**, so it was pure setup, and `Candelabra` made it a two-turn setup:
`The General's Banner+` (1); `Shinobu` (0), whose Companion tag tripped Banner for a Weak, a 2-damage
Casket proc and a Hydro aura; then **two plans stacked** — `Vanguard` (0) and `Coral Bulwark` (1).
**Round 1 dealt 11 damage without a single attack card** (321 → 310), all of it Casket procs off
debuffs, and left the boss `Vulnerable 1`, `Weak 2` and wearing Hydro.

**Round 2**, energy **5/3** off Candelabra. `Razor — Lightning Fang`, two `Strike`s (9 each under
Fang, x1.5 into Vulnerable), then `Kamisato Ayaka — Soumetsu`.
**Predicted about 35 and a Poison stack. Happened: exactly 35** (310 → 275), `Poison 10`.

Then the boss rule the reaction table had promised paid out. Ayaka's end-of-turn 8 Cryo hit the
standing Hydro aura, and:

> **Frozen** — ... **Bosses cannot be Frozen: the pair is consumed and applies 2 Vulnerable instead.**

The boss went to **Vulnerable 2**, and every subsequent Cryo tick did it again — `Vulnerable 5` by
round 4 and **`Vulnerable 7`** by round 5. A printed exception that reads like a nerf ("bosses cannot
be Frozen") is in fact the single strongest interaction available to this deck against this boss, and
the card that exploits it is the one I had been playing for its damage.

**Round 3 was the turn of the act.** `Moon's Reflection+` (0) reached into the exhaust pile and
picked `Kamisato Ayaka — Soumetsu` to be replayed by the Kurage next turn; then `Go for the Eyes` (0),
`Pounce` (2), `Razor — Claw and Thunder` **as the third attack** for its energy refund, and the
refund paid for `Deep Current` (1).
**Predicted about 63 from cards. Happened: 81** (250 → **169**), and **Poison 9 → 29** — four
Electro-Charged reactions at 4 + 1 Snecko, every one of them off a Hydro aura the Casket kept
re-arming between hits.

From there it was arithmetic: 169 → 95 → 34 → dead on **round 5**, with Poison ticking 29, 28 and 27
and Soumetsu firing 8 and then 16, both multiplied by a Vulnerable the Cryo itself kept renewing.

**Result: The Insatiable dead on round 5 at HP 35/87, 16 damage taken across the whole fight** — all
of it on one turn, round 3, when I had no block card in hand.

Rewards: `100 Gold`, `15 Gold`, a `Cunning Potion` left unclaimed (slots full, and the page said so),
and a card from `The Clouds Like Waves Rippling`, `The Moon, A Ship O'er the Seas`, a third
`Sango Isshin`, and **`Itto — Superlative Superstrength (proto)`** (2, "Deal 14 damage. Gain 12
Block"). Took Itto: it is damage and defence on one card, it is a Companion so it trips Banner, and
it costs 2 so it trips `Intimidating Helmet` for 4 more Block. My deck's weakest axis all act was
defence.

Proceeded to the **act-3 map**, whose boss is named **Aeonglass**. Stopped there.

---

## The questions

### (a) Which decisions felt like real choices, and what they traded off

Four, and unlike act 1 they are not all "bigger number wins".

1. **Elite 4, round 3 — the fight where blocking is wrong.** `Vital Spark 2 — ALL Skills are Tainted
   2`, and `Tainted n` is "+n damage from Attacks this turn", which against a `5x3` intent is +n
   *per hit*. I priced the turn three ways and got 12, 11 and 11 damage taken for zero, one and two
   Block cards. **A 6-Block `Defend` buys 6 extra incoming damage.** The trade was Block against
   Tainted and the answer was to play attacks and eat it.
2. **Elite 5, round 6 — killing two health bars on the same tick.** `Reattach 25` gives a segment back
   if any other is alive when it dies. With segments at 3 and 9 and Soumetsu's 8 Cryo landing on Hydro
   auras for 10 apiece (Frozen is a debuff, so the Casket adds 2), both die to the same effect and
   neither revives. The trade was tempo — I could have killed one a turn earlier — against ending the
   fight at all.
3. **Elite 4, round 4 — a three-card turn on three energy.** `Pounce` (2) makes the next Skill free,
   which paid for `Kamisato Ayaka — Soumetsu` (2 → 0), leaving exactly 1 for `War Council`. Five
   energy of cards for three. The trade was Pounce's 14 damage now against Ayaka's 32 over two turns,
   and the discount meant I did not have to choose.
4. **The Orobas event, floor 1.** Six guaranteed random upgrades against a look at fifteen cards with
   the option to take none. I took the look, found that **not one of the fifteen carried an element
   tag**, and took exactly one card. That is a real choice about deck identity rather than power.

### (b) What felt automatic, and what never seemed worth playing

**Automatic:** any turn where the intent was `Empower` or `StatusCard` and my hand was Strikes and
Defends. Also every turn Soumetsu was up and the enemy was under 24 — I ended the turn and the fight
ended itself, three times (fight 8 round 5, fight 9 round 2, boss round 5). A card that wins turns by
being ended is efficient but not interesting.

**Never worth playing:** `Defend`. I played 4 in the whole act and one of those was a mistake. Anchor
gives 10 Block free every combat, `Coral Bulwark` gives 7 with a Plan mode, `Shinobu` gives 5–9 for
**zero**, `Sea-Salt Prayer+` gives 7 and two debuffs, and `Intimidating Helmet` gives 4 for a card I
was playing anyway. A 6-Block 1-cost card is last in a queue of six better answers, and against
`Vital Spark` it is actively negative.

`Kurage's Oath` is still the card with no non-Plan mode, and I played it exactly twice in eleven
rooms.

### (c) What I could not understand, or that contradicted its own printed text

- **The `Tainted` glossary is circular.** "Tainted — Gain 2 Tainted when played." The rule
  ("Take 2 additional damage from Attacks this turn") appears only on the status line *after* you
  have some. The one place you could price the decision is empty.
- **The intent number is unreliable exactly when Tainted is in play.** Elite 4 round 3: `Tainted 4`,
  printed intent `6x3` = 18, 7 Block, Tungsten Rod — I took **15**. Elite 4 round 4: `Tainted 4`,
  printed intent `12` (correctly 8 + 4) — I took **5**. Under-reported by 7, then over-reported by 7,
  same fight, same debuff.
- **Two element-override effects behave differently.** `Razor — Lightning Fang` ("your Attacks apply
  Electro") **overrode** `Undertow (proto)+`'s printed `[Hydro]` and left an Electro aura (fight 8,
  round 3). `Kujou Sara — Crowfeather Cover` ("Your next Attack this turn ... applies Electro")
  **did not** override `Sango Isshin`'s Hydro — all three Bowlbugs came out wearing refreshed Hydro
  (fight 10, round 2). Neither card's text distinguishes them.
- **`Sango Isshin`'s alternate mode ignores flat bonuses but not Weak.** Measured three times: it took
  no `+3` from Lightning Fang (fight 6: 40 total, not 43), no `+4` from Kujou Sara (fight 10: 15, not
  18), but **was** cut 25% by my own Weak (21 → 15) and **was** raised 50% by enemy Vulnerable
  (21 → 31, fight 9). Nothing on the card says it is anything but an Attack.
- **The Casket's proc rule still cannot be pinned down**, and I have three fresh, mutually
  inconsistent instances. `Slack Water` applying Weak *and* a reaction Poison in fight 8 fired it
  **twice** (8 damage, not 6). A `War Council` plan applying Weak to *three* enemies fired it
  **once**, on the front enemy only (fight 10: 7 / 5 / 5). A Vanguard plan whose two debuffs were both
  negated by Artifact fired it **zero** times (fight 8: 51 before, 51 after).
- **An enemy lost 9 HP with no printed cause.** Fight 8: Chomper (1) ended my round 2 at **18** and
  opened round 3 at **9**, with no Poison, no aura, no debuff, and the Kurage reading "Nothing is
  planned. The morning is empty."
- **`Uproar`'s random attack is never named.** Three Uproars: two contributed **0** measurable damage
  (fight 7 round 3, fight 8 round 2) while the pile counts proved a card had been drawn and played,
  and one contributed **16**, identifiable only by solving 9+2+9+2+X+2 = 40 for X and recognising
  `Undertow+`. No screen ever says what it played.
- **Five proper nouns are offered as choices and never defined**: `Circlet`, `Decay`, `Lost Wisp`,
  `Normality`, `Perfect Fit` and `Metamorphosis`. `Swirl` is defined on the screen that offers
  `Sucrose` and undefined on the screen that offers `Lynette — Enigmatic Feint`.
- **`Sango Isshin (proto)` cost 72 gold in the first shop and 156 in the second** — same card, same
  act, same run. `Card Removal` went 75 → 100 over the same two shops.

### (d) The card I never wanted to play, and the one I was happiest to draw

**Never wanted: `Defend`.** See (b) — it is last in a queue of six better answers and against
`Vital Spark` it is worse than nothing.

**Happiest to draw: `Kamisato Ayaka — Soumetsu`.** In act 1 the previous seat took it for the raw 32.
In act 2 it turned out to be the deck's control card as well as its damage: its Cryo makes **Frozen**
off any Hydro aura (which my own relic keeps re-arming), **Melt** at 1.75x off a Pyro one, and
against a boss the Frozen substitution stacks **2 Vulnerable every single tick** — the boss finished
on `Vulnerable 7` without my ever playing a card that says Vulnerable. It also ends fights by itself
on turns where I have nothing to play.

Runner-up, and the better *design*: **`Moon's Reflection+`** at cost 0. Reaching into the exhaust pile
to replay a 32-damage AoE for zero energy is the only card in the deck that made me plan two turns
ahead about a pile I do not normally look at.

### (e) Did the previous seat's three sharpest findings hold up?

**Finding 1 — `Uproar` sometimes plans its random attack instead of playing it.** *Not reproduced,
but the underlying defect is worse than reported.* In three Uproars across act 2 the Kurage read
"Nothing is planned" every time, so it was always played. But twice it dealt **0** measurable damage
(fight 7 round 3: cards totalled exactly 24 = 18 + 6 with nothing left over; fight 8 round 2: exactly
24 = 6 + 9 + 9), while the pile counts proved a card had left the draw pile and entered the discard.
The general fault stands and generalises: **whatever Uproar does with that card, no screen reports
it.**

**Finding 2 — plan damage ignores a debuff that visibly reduces card damage.** *Confirmed, and it is
printed after all — on some screens.* From fight 7 onward the glossary entry for `Plan` reads
"**Enemy Vulnerable raises it; your Weak does not**", which is exactly the Shrink behaviour the
previous seat had to infer. I confirmed the first half directly: fight 10 round 3, a `Kurage's Oath`
plan into a Vulnerable segment killed it from 10 through Poison, i.e. the plan's 7 arrived amplified.
The defect is not the rule, it is that the same word gets two different glossary texts and the
informative one did not appear on the screens where it first mattered.

**Finding 3 — the elemental reaction chain is entirely unprinted.** *No longer true, and this is the
biggest single improvement between the two acts.* From fight 7 the glossary prints **all six
reactions with their exact numbers** — Melt 1.75x, Vaporize 1.5x, Overloaded 6 splash + Weak,
Superconduct 2 Vulnerable, Electro-Charged a 4-damage DoT, Frozen with its explicit boss exception —
plus a paragraph stating that the aura is consumed so the hit leaves none of its own. Every
multiplier the previous seat reverse-engineered from corpses is now a printed number, and I used them
to price turns in advance: Amber's 8 Pyro landing for exactly **12** into Hydro (fight 6), Ayaka's
8 Cryo landing for exactly **14** into Pyro (elite 5). What remains unprinted is the *relic's* half:
that the Casket's 2 Hydro damage re-arms the aura the next off-element card needs.

Two smaller ones also resolved: the belt is now printed ("**Your potion slots are full: 3 of 3** ...
this page will not claim it until a slot is free"), which fixes the silently-dropped potion; and the
three Status cards the previous seat believed were permanently added to the deck **were not** — the
Card Removal screen lists 25 cards with no Status among them, after twelve had been forced on me.

### (f) Did act 2 ask anything of the deck that act 1 did not?

Yes — four things, and they are the act's best work.

1. **`Artifact 2` (Chompers) blanks the relic.** My whole engine is "apply a debuff → Casket procs →
   aura re-arms → next card reacts". Two negated debuffs per enemy shut all four steps off, and I
   measured it exactly: a Vanguard plan applying Vulnerable and Weak consumed both Artifact stacks
   and dealt **0**.
2. **`Vital Spark` (Infested Prism) taxes the card *type* the deck is made of.** 19 of my 30 cards
   were Skills and every Plan card is a Skill, so the engine cannot be run without feeding the tax.
3. **`Reattach` (Decimillipede) punishes single-target focus** and demands a simultaneous kill, which
   is the one thing a deck built on `Undertow+` and `Razor — Claw and Thunder` is bad at.
4. **`Escape Artist` and `Burrowed` put clocks and thresholds on fights** — five turns to kill 79 HP,
   or 32 non-decaying Block with a Stun for stripping it.

Act 1 asked "how much damage this turn". Act 2 asked "which *kind* of card, in which order, on which
tick". The act-1 seat's complaint that roughly a third of turns had no decision in them is much less
true here; I count two automatic turns in eleven rooms.

### (g) Anything a screen granted or changed without saying so

- **+23 HP between the acts.** The previous seat stopped at 58/87; my first battle screen read 81/87.
  No map, event or reward screen printed it.
- **+202 gold.** Every reward row I claimed sums to 445; the first shop read **647**. (The second
  shop reconciled to the gold exactly, so it is not a systematic offset.)
- **The `Gear Glass` event option became a permanent relic**, printing the event's own text as its
  relic line. The event never said I was picking up a relic.
- **A card was stolen from my draw pile** by the Thieving Hopper with no line saying so; the only
  evidence was a `Swipe 1` buff on the thief and piles totalling 22 against a 23-card deck.
- **Nine Status cards entered my piles** across fight 8 with no line, no face and no destination —
  and I never drew one, so I could not have known what they were.
- **`Meal Ticket`'s 15 HP is never confirmed on the shop screen**, which prints gold but no HP. Both
  times I could only verify it on the next battle screen.
- **A card's cost changed with no stated reason.** `Deep Current` printed "cost 0" mid-fight with the
  note "This copy is not upgraded, so the cut is this turn's board and not the card". The note is
  excellent and the cause (a `Metamorphosis` played three turns earlier) is not named anywhere.
- **`Perfect Fit` was applied to a card of my choosing without ever being defined**, and the event
  gave no confirmation of what changed. I learned it two rooms later from the card face.

---

## Findings, ranked by sharpness

1. **The `Tainted` glossary tells you nothing, and the intent line that should compensate is wrong on
   multi-hit attacks.** `Vital Spark 2 — ALL Skills are Tainted 2` is the elite's whole design, and
   the Words-on-this-screen entry for it reads, in full, "Tainted — Gain 2 Tainted when played."
   The real rule ("Take 2 additional damage from Attacks this turn") only appears on your own status
   line once you already have it. And with `Tainted 4` up, the printed intent `6x3` (18) preceded
   **15** damage taken through 7 Block and Tungsten Rod, while the printed intent `12` in the same
   fight preceded **5**. A player deciding whether to play a Block card cannot get the number right
   from anything on the screen.

2. **`Uproar`'s random attack is unreportable.** Three plays: 0, 0, and 16 measurable damage. The
   16 is only identifiable by solving 9 + 2 + 9 + 2 + X + 2 = 40 and recognising `Undertow+`'s
   debuffed 13 + Fang's 3. The two zeroes are consistent with the pile counts (a card left the draw
   pile and entered the discard both times) and with nothing else. **No screen names the card, its
   target, or its result**, in a game whose every other number is checkable.

3. **Two "applies Electro" effects disagree about whether they override a card's printed element.**
   `Razor — Lightning Fang` turned `Undertow (proto)+` `[Hydro]` into an Electro applier (fight 8:
   Electro Aura 2 on the target). `Kujou Sara — Crowfeather Cover` did not turn `Sango Isshin`
   `[Hydro]` into one (fight 10: all three targets on refreshed Hydro, no reaction, no Poison). Both
   cards say "applies Electro".

4. **`Sango Isshin`'s alternate mode is not modified like an Attack, and nothing says so.** It takes
   no `+3` from Lightning Fang and no `+4` from Kujou Sara (measured at 21 in fight 6 where 24 was
   due, and 15 in fight 10 where 18 was due), yet it **is** cut 25% by my Weak (21 → 15) and raised
   50% by enemy Vulnerable (21 → 31). Three different modifier rules on one line of card text.

5. **The Casket fires 0, 1 or 2 times for the same-looking event.** Twice for one card that applied
   Weak and a reaction Poison (fight 8: 8 damage where 6 was due). Once for a plan that applied Weak
   to three enemies, on the front one only (fight 10: 7 / 5 / 5). Zero for a plan whose two debuffs
   were negated by `Artifact` (fight 8: 51 before and after). The relic is load-bearing for the whole
   deck and its rule is not printed anywhere.

6. **The reaction table is printed now, but the relic that drives it is not.** All six reactions and
   their multipliers appear in the glossary from fight 7 onward, including `Frozen`'s boss exception.
   What is still invisible is that **the Tamakushi Casket's 2 Hydro damage applies a Hydro aura**,
   which is what makes a Hydro card followed by an Electro card chain indefinitely — boss round 3
   took `Poison 9 → 29` on four consecutive reactions off an aura no card of mine re-applied.

7. **An enemy lost 9 HP with no printed cause.** Fight 8: Chomper (1) at **18** at the end of my
   round 2, **9/60** at the start of round 3, carrying no Poison, no aura and no debuff, with the
   Kurage empty and nothing of mine pending.

8. **Two silent grants across the act boundary: +23 HP and +202 gold.** 58/87 became 81/87 with no
   screen printing it; claimed reward rows summing to 445 gold became 647 at the first shop. The
   second shop's arithmetic was exact, so this is not a display offset.

9. **A relic-granted card reward does not reroll, and skipping it does not consume it.** `Orrery`'s
   five rewards: three distinct offers, then the identical trio (`Cleansing Wave`, `Treatise`,
   `Coral Bulwark`) on the fourth, fifth **and** on reopening a skipped row. Skipping left the row on
   the screen, so five `choose` calls left two rows outstanding.

10. **The `Card Removal` screen is stale by a whole shop visit.** It listed 25 cards; I had added five
    in that same shop before opening it, and the next battle confirmed 29. It also proved the useful
    fact that **Status cards never persist** — twelve had been forced on me and none were in the list.

11. **Shop prices for the same card differ by 2.2x between two shops in the same act.**
    `Sango Isshin (proto)` at 72 gold and then 156; `Card Removal` at 75 and then 100.

12. **Six proper nouns are offered as choices without ever being defined**: `Circlet`, `Decay`,
    `Lost Wisp`, `Normality`, `Perfect Fit`, `Metamorphosis`. Two of them turned out to matter a lot
    in opposite directions — `Perfect Fit` is a real benefit and `Metamorphosis` is a *good card sold
    as a cost*, sitting in the same sentence slot where the other option put an explicit drawback.
    `Swirl` is defined on one card-reward screen and undefined on another.

13. **Things done well, which a rewrite should not break.** The intent line nets out `Weak`, `Baron
    Bunny` and single-hit `Tainted` before you commit (17 → 14 the moment Amber went up). Card faces
    re-print every modifier (`Deal 11 damage` under Fang, `cost 2` and `Gain 4 Tainted` under Vital
    Spark 4, `Deal 4 damage` under my own Weak). The potion screen prints the belt state and refuses
    to silently drop a potion. `Moon's Reflection+` explains its own cost ("The cost printed on this
    card is 1; it is showing 0 here, because this copy is upgraded — that is permanent") and
    `Deep Current` explains the opposite case. The one refusal I got named the exact string that
    would have worked. `Imbalanced`, `Burrowed`, `Escape Artist`, `Reattach` and `Flutter` all state a
    threshold you can aim at, and I hit four of the five.

**Where I could not tell:** whether the Bake-Kurage is a good mechanic. It is much better than act 1
made it look, but almost entirely because of three cards the previous seat did not have —
`Change of Plans+` (fire a plan *this* turn), `Moon's Reflection+` (replay an exhausted card through
it), and a second `Sango Isshin` to spend the plans on. With those, the Kurage is a real engine and
the boss's round 1 (11 damage and four debuffs from zero attack cards) is its best turn. Without
them it is still a one-turn delay tax, and I cannot separate "the mechanic is good" from "the three
cards that fix it are good". I also could not tell what `Perfect Fit` was worth: I put it on a card
that Exhausts, so its "place it on top of the draw pile" only ever fires once per combat, and I never
saw a screen tell me it had.

---

## Non-blindness declaration

- **Commands outside the two allowed ones: none.** Every game action was
  `GITS_LANE=1 python -m understudy.blindplay observe` or
  `GITS_LANE=1 python -m understudy.blindplay act "<command>"`, run from the repo root
  `C:\Users\Monty\Documents\GitHub\GItS`.
- **Other shell usage:** `grep`, `sed`, `cat`, `head`, `tail`, `wc` and `mkdir`, used only to trim
  `observe` output for readability and to assemble my own record file; and one `python` run of a
  three-line script I wrote in the scratchpad, whose only purpose was to delete a paragraph from my
  own record (see the correction note below). No understudy command other than `observe` and `act`.
- **Tools used:** Bash, Write (this record and five scratchpad fragments), and **Read exactly once**,
  on `review/qa/kokomi-round-4d-2026-09-03/opus-act1.md`, the previous seat's record, as instructed.
- **Repo files read: one** — that act-1 record. No source, no YAML, no docs, no rulings, no backlog,
  no logs. Everything else here comes from what `observe` and `act` printed.
- **The only repo file written is this record**,
  `review/qa/kokomi-round-4d-2026-09-03/opus-act2.md`. No identifiers were minted.
- **A correction I made to my own record.** Twice during play I noted that a battle screen had
  "printed the whole `The other side` block twice". That was wrong and I removed the claim: it was an
  artefact of my own `sed` invocation, which had two overlapping line ranges and therefore printed
  the same lines twice. **The game did not duplicate anything.** I am recording the mistake rather
  than the false defect.
- **Lane:** lane 1 only. Lane 2 was never touched. The game was never launched, closed, restarted or
  torn down. **The lane is left standing on the act-3 map screen**, at its single offered node
  (`Ancient (path 1)`), HP **35/87**, with the act-3 boss named **Aeonglass**. The map screen prints no gold line, so the last gold figure I can quote from a screen is **84** at the second shop; the reward rows claimed after it were 12+15, 15+15, 36+15 and 100+15, less 51 spent on `Vanguard`.

*you are playing the real game through a tool that shows you only what the screen prints; nothing recorded here is a measurement, a comparison with any other run, or a judgement of whether the game is fun or good that anyone will treat as approval*
