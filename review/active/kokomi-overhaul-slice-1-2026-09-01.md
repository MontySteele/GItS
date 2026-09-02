Status: OPEN (draft 3, Paper; built once the brief's draft-3 picks are ruled)

# Kokomi overhaul, slice one: the rules, the starter, and 28 cards (draft 3)

Draft 3, 2026-09-02, rewritten whole on the brief's draft 3
(`review/active/kokomi-brief-2026-09-01.md`). The draft-2 slice was built,
played by two seats and by you, and failed its gate question 1; its
records are `review/ruled/kokomi-overhaul-round-1-2026-09-02.md` (R237).
This is the Paper artefact for the rebuild: the same starter shape, the
same 28-card pool size, the jellyfish's Memory at the centre.

## 1. What the slice is for

**What the slice must show:** a player who has never read the brief can
find "do a thing, the jellyfish does it again" in fight one; the order you
queue things in is felt at least once per fight; the Tide reads as fuel
and never as a tax; and Surge has a right turn.

## 2. The rules, one line each (the brief's §4, unchanged)

1. **The Bake-Kurage** is always out and holds **Tide** (a number from 0,
   never resetting on its own) and its **Memory** (a row of cards, in
   order).
2. **Tide**: her cards add it; any card of hers that Exhausts adds 1.
3. **Remember**: a card she owns that Exhausts (her own or a Companion)
   joins the row with its target and choices. A card the jellyfish played
   is never remembered again.
4. **The replay**: at the start of her turn, if the Tide covers the front
   memory's price (3 per energy of printed cost; 0-cost is free), the
   jellyfish pays, plays it, forgets it. One a turn. An unaffordable front
   card holds the row.
5. **Surge**: the jellyfish plays remembered cards from the front, paying
   each from the Tide, until it cannot; then the Tide is 0.
6. **Plan**: paid for now, not played now; joins the row at no price, and
   the jellyfish carries it out.
7. **Mend**: heal, never above entry HP; Uncommon-and-up only, all
   Exhaust.
8. **Flawless Strategy**: no Strength; Strength becomes Tide.

Garment is a card state (N turns; each Attack that hits Mends 2). A
remembered card keeps its target; dead or gone, a random living one.
Keywords with tooltips: Tide, Memory, Surge, Plan, Mend, Garment.

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
for the first replay: fight one's turn two opens with Salt Line coming
back whatever was drawn. Script A in the brief (§12) plays fight one out.

## 4. The pool (28 cards)

Prototype numbers, generous on purpose. Every Exhaust card below is also
its own replay (rule 3); the job column says what the second play is for.

### Priestess, feed, remember, surge (9)

| Card | R | Cost | Type | Printed text | Job |
|---|---|---|---|---|---|
| Tidal Prayer | C | 1 | Skill | Tide +3. Draw 1. | The cheap feed that replaces itself |
| Sea Spray | C | 1 | Attack | Deal 5. Tide +2. | The Attack that feeds |
| Deep Current | C | 1 | Attack | Deal 4 to every enemy. Tide +1 per enemy hit. | Hallway feed |
| Breaker | C | 2 | Attack | Deal 8. Surge. | The big cash at Common |
| Undertow | C | 1 | Skill | The jellyfish plays the front memory now, paying its price. Gain 3 Block. | Tempo; collect a Plan the turn it was written |
| High Tide | U | 1 | Skill | Exhaust. Tide +8. | Fuel that comes back as fuel |
| Song of Pearls | U | 1 | Power | Whenever the jellyfish plays a card, Tide +2. | The row feeds itself |
| Nereid's Ascension | U | 1 | Skill | Exhaust. Wear the Garment for 2 turns. | The lifesteal window, twice |
| Sango Isshin | R | 2 | Power | Mend that would go past your entry HP becomes Hydro damage to a random enemy. | Breaks rule 7's ceiling |

### Strategist, the plan was written last turn (8)

| Card | R | Cost | Type | Printed text | Job |
|---|---|---|---|---|---|
| Battle Plan | C | 1 | Skill | Plan: gain 2 Energy. | Delayed energy |
| Ambush | C | 1 | Skill | Plan: deal 12 to a random enemy. | Delayed damage, better rate than now |
| Read the Field | C | 1 | Skill | Gain 3 Block. Plan: gain 5 Block. | Defence now and later |
| Feint | C | 1 | Attack | Deal 4. Plan: deal 8 to the same enemy. | The Attack version |
| Contingency | U | 1 | Skill | Exhaust. Plan: Mend 6. | The scheduled heal, twice at most |
| Treatise | U | 1 | Power | Whenever the jellyfish plays a card, draw 1. | The row into cards |
| War Council | U | 1 | Skill | Plan: play the top 2 cards of your draw pile for free. | The gamble |
| The Art of War | R | 2 | Power | Plans also happen now. | Breaks rule 6 |

### Commander, Gorou, go (4)

Companions come from the Inazuma Universals (R236) already in the pool;
no Personal and no stand-in is authored for slice one.

| Card | R | Cost | Type | Printed text | Job |
|---|---|---|---|---|---|
| Rally | C | 1 | Skill | Exhaust a Companion card from your hand; the jellyfish remembers it. Tide +2. | The one door for companions, chosen |
| Vanguard | C | 0 | Skill | The next Companion you play this turn costs 0. | Tempo |
| Orders | U | 1 | Power | Whenever you play a Companion, Tide +2. | Companions into Tide |
| The General's Banner | R | 2 | Power | The jellyfish plays two memories a turn. | Breaks rule 4's one |

### Currencies and defence (7)

| Card | R | Cost | Type | Printed text | Job |
|---|---|---|---|---|---|
| Quiet Study | C | 1 | Skill | Gain 4 Block. Tide +2. | Block and feed; the plain turn |
| Change of Plans | C | 0 | Skill | Forget the front memory. Draw 1. | The eject for a jammed row |
| Coral Bulwark | U | 2 | Skill | Gain 6 Block. Tide +4. | The setup turn in one card |
| Cleansing Tide | U | 1 | Skill | Exhaust. Mend 6. | The true heal, twice at most |
| The Clouds Like Waves | U | 1 | Power | While you are under half HP, each card the jellyfish plays Mends you 2. | The comeback |
| Reading the Tide | U | 0 | Skill | Draw 1, plus 1 per 5 Tide. | Tide into cards; never a blank |
| Watatsumi's Blessing | R | 2 | Skill | Exhaust. Mend 12. Tide +6. | The big heal, twice at most, at Rare |

Pool by rarity: 13 Common, 11 Uncommon, 4 Rare. Block in the pool: five
cards, one of them a Plan; the scarcity the brief asks for.

## 5. What the engine has to do (the C# build list)

Most of this exists. The Memory arm
(`klee-mod/KleeCode/Powers/Prototype/KurageMemory.cs`, tier0's
`C.KURAGE_MEMORY`) carries the row, the price at 3 per energy, the
start-of-turn replay, same-target with random fallback, and the never-
re-remembered rule; the memory strip is EB-198. The draft-2 arm
(`KokomiOverhaul*.cs`, `KokomiPlan.cs`) carries Tide, Mend with the
entry-HP cap, Garment, Strength → Tide, and a Plan queue. The build joins
them under `KOKOMI_OVERHAUL` and retires what draft 2 had that draft 3
does not.

- **Tide** stays the jellyfish's counter; **Exert** and **the pulse** and
  its budget are removed; the Casket's text becomes the free first
  replay.
- **The Memory's doors**: her own cards on Exhaust (new; the old arm took
  Companions only), Companions on Exhaust (kept), Rally's chosen Exhaust
  (a hand pick), and **Plan** as "into the row at price 0, unplayed, with
  its target" (the old Plan queue retired; one row).
- **The replay** as it is; **Surge** as "play from the front, paying, while
  the Tide can; then Tide 0"; **Undertow** as one paid replay now; **Change
  of Plans** as forget-front; **The General's Banner** as two replays a
  turn; **The Art of War** as "a Plan also resolves now".
- **Hooks on "the jellyfish played a card"** for Song of Pearls, Treatise
  and The Clouds Like Waves; **Orders** on Companion play; **Vanguard**
  as next-Companion-free (exists in the companion arm).
- **Mend**, **Garment**, **Sango Isshin**, **Strength → Tide** as built.
- **UI**: the Tide number on the jellyfish, the memory strip with a price
  on each face, the Garment count. The wire carries the Tide, the row and
  its prices (EB-273's fix widens to the row).
- **Off under the switch:** Charge accrual, Muster, the Burst gate, the
  draft-2 pulse. The shipped 76-card Kokomi stays in the release build
  untouched.

All of it behind the prototype switch, C# first; the sim twin follows for
the rows the sim can carry, since the Memory already lives in tier0.

## 6. The Prototype gate, and who plays

1. Opus builds the slice under `KOKOMI_OVERHAUL` from this document's
   surface rows, and runs the soak and the lints.
2. Seats play first: Opus, GPT and Qwen each play an act-one run on the
   build with this 28-card pool as Kokomi's only reward pool, with the
   Inazuma companions offered. They catch soft-locks, text that lies, and
   cards nobody plays.
3. Then you play: one act-one run, three or four fights including an
   elite. The rules changed, so this is the "first build of a kit's
   rules" gate.
4. You answer four questions, in a sentence each:
   1. Did you want to give the jellyfish cards, and did the order matter?
   2. Did the Tide feel like fuel or like a tax?
   3. Did Surge have a right turn, and did you find it?
   4. Which card did you never want to play?

A pass is not a number. It is your four answers plus the seats' defect
list. A fail on question 1 or 3 goes back to the brief's rules, not to
the card numbers.

## 7. Not in slice one, on purpose

- The remaining own cards: Commons to bring each loop to 14 to 16, more
  Rares, the stand-ins (Thoma's barrier, Shinobu's ring, Sara's stormcall)
  and Gorou's Personal.
- Any Watatsumi relic beyond the Casket.
- The row's cap, if EB-234's measure returns on the new rules; a Balance
  number.
- Upgrades beyond the Prototype-stage rule (EB-283).
