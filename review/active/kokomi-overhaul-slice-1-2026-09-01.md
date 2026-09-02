Status: OPEN (draft 4, Paper; to be rewritten on brief draft 6 once read)

# Kokomi overhaul, slice one: the rules, the starter, and 28 cards (draft 4)

Draft 4, 2026-09-02, rewritten whole on the brief's draft 4
(`review/active/kokomi-brief-2026-09-01.md`). The draft-2 slice was built,
played by two seats and by you, and failed its gate question 1; its
records are `review/ruled/kokomi-overhaul-round-1-2026-09-02.md` (R237).
This is the Paper artefact for the rebuild: the same starter shape, the
same 28-card pool size, the exhaust pile as the jellyfish's memory and
the Tide as what it costs to read from it.

## 1. What the slice is for

**What the slice must show:** a player who has never read the brief can
find "Exhaust it, feed, Surge it back" in fight one; the order of the pile
is felt at least once per fight; the Tide reads as fuel and never as a
tax; and Surge has a right turn.

## 2. The rules, one line each (the brief's §4, unchanged)

1. **The Bake-Kurage** is always out and holds **Tide** (a number from 0,
   never resetting on its own).
2. **Tide**: her cards add it; any card of hers that Exhausts adds 1.
3. **Surge**: the jellyfish plays the top card of her exhaust pile (the
   last card exhausted) at no energy, with its own target and choices,
   paying its price from the Tide: 3 per energy of printed cost, 0-cost
   free. If the Tide cannot pay, it plays nothing and the rest of the
   card still happens.
4. **Plan**: paid and Exhausted now, doing nothing yet; at the start of
   her next turn the jellyfish plays it at no Tide price, unless a Surge
   already has.
5. **Tactics**: a card the jellyfish has played. When it would go to the
   exhaust pile, it leaves the fight instead.
6. **Mend**: heal, never above entry HP; Uncommon and up only.
7. **Garment**: a state for N turns; each Attack that hits Mends 2.
8. **Flawless Strategy**: no Strength; Strength becomes Tide.

A dead target is replaced by a random living one. Keywords with tooltips:
Tide, Surge, Plan, Tactics, Mend, Garment.

## 3. The starter (ten cards, six ids)

| Card | Cost | Type | Printed text | Copies |
|---|---|---|---|---|
| Water's Edge | 1 | Attack | Deal 6. | 3 |
| Coral Guard | 1 | Skill | Gain 5 Block. | 2 |
| Salt Line | 1 | Skill | Exhaust. Gain 7 Block. | 1 |
| Kurage's Oath | 1 | Skill | Tide +4. | 2 |
| Rising Tide | 1 | Attack | Deal 4. Surge. | 1 |
| Stolen Chapter | 1 | Skill | Plan: draw 2. | 1 |

Relic: **Tamanooya's Casket**. The jellyfish is out from the start of
combat, and the first card it plays each combat costs no Tide. It pays
for the first Surge: fight one's turn two brings Salt Line back whatever
the Tide, and the second Surge teaches the price. Script A in the brief
(§12) plays fight one out.

## 4. The pool (28 cards)

Prototype numbers, generous on purpose. Every Exhaust card below is also
one Surge away from a second play; the job column says what the second
play is for.

### Priestess, Exhaust it, feed, Surge it back (9)

| Card | R | Cost | Type | Printed text | Job |
|---|---|---|---|---|---|
| Tidal Prayer | C | 1 | Skill | Tide +3. Draw 1. | The cheap feed that replaces itself |
| Sea Spray | C | 1 | Attack | Deal 5. Tide +2. | The Attack that feeds |
| Deep Current | C | 1 | Attack | Deal 4 to every enemy. Tide +1 per enemy hit. | Hallway feed |
| Breaker | C | 2 | Attack | Deal 8. Surge. | The big cash at Common |
| Undertow | C | 1 | Skill | Gain 3 Block. Surge. | The Surge that defends |
| High Tide | U | 1 | Skill | Exhaust. Tide +8. | Fuel that comes back as fuel, for 3 |
| Song of Pearls | U | 1 | Power | Whenever the jellyfish plays a card, Tide +2. | Surges pay part of the next |
| Nereid's Ascension | U | 1 | Skill | Exhaust. Wear the Garment for 2 turns. | The lifesteal window, twice |
| Sango Isshin | R | 2 | Power | Mend that would go past your entry HP becomes Hydro damage to a random enemy. | Breaks rule 6's ceiling |

### Strategist, the plan was written last turn (8)

| Card | R | Cost | Type | Printed text | Job |
|---|---|---|---|---|---|
| Battle Plan | C | 1 | Skill | Plan: gain 2 Energy. | Delayed energy, the one net-positive card |
| Ambush | C | 1 | Skill | Plan: deal 12 to a random enemy. | Delayed damage, better rate than now |
| Read the Field | C | 1 | Skill | Gain 3 Block. Plan: gain 5 Block. | Defence now and later |
| Feint | C | 1 | Attack | Deal 4. Plan: deal 8 to the same enemy. | The Attack version |
| Contingency | U | 1 | Skill | Plan: Mend 6. | The scheduled heal |
| Treatise | U | 1 | Power | Whenever the jellyfish plays a card, draw 1. | Replays into cards |
| War Council | U | 1 | Skill | Plan: Surge twice. | A delayed double, paid in Tide then |
| The Art of War | R | 2 | Power | Plans also happen now. | Breaks rule 4 |

### Commander, Gorou, go (4)

Companions come from the Inazuma Universals (R236) already in the pool;
no Personal and no stand-in is authored for slice one.

| Card | R | Cost | Type | Printed text | Job |
|---|---|---|---|---|---|
| Rally | C | 1 | Skill | Exhaust a Companion card from your hand. Tide +2. | The one door for companions, chosen |
| Vanguard | C | 0 | Skill | The next Companion you play this turn costs 0. | Tempo |
| Orders | U | 1 | Power | Whenever you play a Companion, Tide +2. | Companions into Tide |
| The General's Banner | R | 2 | Power | Companions the jellyfish plays are not Tactics. | Breaks rule 5, for companions |

### Currencies and defence (7)

| Card | R | Cost | Type | Printed text | Job |
|---|---|---|---|---|---|
| Quiet Study | C | 1 | Skill | Gain 4 Block. Tide +2. | Block and feed; the plain turn |
| Change of Plans | C | 1 | Skill | Choose a card in your exhaust pile and put it on top. Draw 1. | The reorder |
| Moon's Reflection | U | 1 | Skill | Put a card from your exhaust pile into your hand. | The one door to a second replay |
| Cleansing Tide | U | 1 | Skill | Exhaust. Mend 6. | The true heal, twice at most |
| Reading the Tide | U | 0 | Skill | Draw 1, plus 1 per 5 Tide. | Tide into cards; never a blank |
| The Clouds Like Waves | U | 1 | Power | While you are under half HP, each card the jellyfish plays Mends you 2. | The comeback |
| Watatsumi's Blessing | R | 2 | Skill | Exhaust. Mend 12. Draw 2. | The big heal, twice at most, for 6 Tide the second time |

Pool by rarity: 13 Common, 11 Uncommon, 4 Rare. Block in the pool: four
cards, one of them a Plan; the scarcity the brief asks for.

## 5. What the engine has to do (the C# build list)

Most of this exists. The Memory arm
(`klee-mod/KleeCode/Powers/Prototype/KurageMemory.cs`, tier0's
`C.KURAGE_MEMORY`) carries "the jellyfish plays a card with its stored
target and choices," the price at 3 per energy, same-target with random
fallback, and the never-re-remembered rule, which is Tactics by another
name. The draft-2 arm (`KokomiOverhaul*.cs`, `KokomiPlan.cs`) carries
Tide, Mend with the entry-HP cap, Garment, Strength → Tide, and a Plan
queue. The build joins them under `KOKOMI_OVERHAUL` and retires what
draft 2 had that draft 4 does not.

- **Tide** stays the jellyfish's counter, fed by cards and by 1 per
  Exhaust; **Exert** and **the pulse** and its budget are removed; the
  Casket's text becomes the free first replay.
- **No automatic replay.** The old arm's start-of-turn spend is removed.
  The jellyfish plays only from **Surge** (the top of the exhaust pile,
  paying the Tide, nothing if short) and from a **Plan**'s morning (free).
- **The exhaust pile's order** is the memory: the game's pile in exhaust
  order, top = last. Change of Plans reorders it; Moon's Reflection takes
  from it to hand.
- **Tactics**: a flag set on the card instance when the jellyfish plays
  it; on that card's next Exhaust it is removed from combat instead. The
  General's Banner exempts Companions.
- **Plan**: paid now, Exhausted to the pile with its target, played by the
  jellyfish at the start of her next turn at no Tide unless already
  Surged; The Art of War also resolves it now; War Council's Plan is two
  Surges.
- **Hooks on "the jellyfish played a card"** for Song of Pearls, Treatise
  and The Clouds Like Waves; **Orders** on Companion play; **Vanguard** as
  next-Companion-free (exists in the companion arm); **Rally** as a hand
  pick that Exhausts.
- **Mend**, **Garment**, **Sango Isshin**, **Strength → Tide** as built.
- **UI**: the Tide number on the jellyfish, the top card of the pile face
  up beside it with its price, the Tactics tag, the Garment count. The
  wire carries the Tide, the pile in order with prices, and the tag
  (EB-273's fix widens to these).
- **Off under the switch:** Charge accrual, Muster, the Burst gate, the
  draft-2 pulse and Exert, the draft-3 row. The shipped 76-card Kokomi
  stays in the release build untouched.

All of it behind the prototype switch, C# first; the sim twin follows for
the rows the sim can carry, since the Memory's play-with-stored-target
already lives in tier0.

## 6. The Prototype gate, and who plays

1. Opus builds the slice under `KOKOMI_OVERHAUL` from this document's
   surface rows, and runs the soak and the lints.
2. Seats play first: Opus, GPT and Qwen each play an act-one run on the
   build with this 28-card pool as Kokomi's only reward pool, with the
   Inazuma companions offered. They catch soft-locks, text that lies,
   Surges that played nothing, and cards nobody plays.
3. Then you play: one act-one run, three or four fights including an
   elite. The rules changed, so this is the "first build of a kit's
   rules" gate.
4. You answer four questions, in a sentence each:
   1. Did you choose what went on top of the pile, and did the order
      matter?
   2. Did the Tide feel like fuel or like a tax?
   3. Did Surge have a right turn, and was one ever wasted on the wrong
      top or a short Tide?
   4. Which card did you never want to play?

A pass is not a number. It is your four answers plus the seats' defect
list. A fail on question 1 or 3 goes back to the brief's rules, not to
the card numbers.

## 7. Not in slice one, on purpose

- The remaining own cards: Commons to bring each loop to 14 to 16, more
  Rares, the stand-ins (Thoma's barrier, Shinobu's ring, Sara's stormcall)
  and Gorou's Personal.
- Any Watatsumi relic beyond the Casket.
- Upgrades beyond the Prototype-stage rule (EB-283).
