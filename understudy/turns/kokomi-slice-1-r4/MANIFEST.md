# Kokomi slice 1, round 4 — turn manifest

Four staged turns, two matched pairs. **This round exists only to answer the
two RETURNs round 3 left**, and it changes nothing else: the two arms that
ADVANCED in each of these groups are not re-run, the other two groups are not
touched, and no printed card number moved anywhere (R213 freeze).

**Nothing in this file rates an arm.** The designer of these rows may not grade
them (R213's first guard). The columns record what was set and what happened;
the four-question form is somebody else's. Under R215 B no number measured on a
prototype row is quotable — the closeness column is the exception, because it
reads the **turn** and not the sheet.

## What round 3 asked for, in the reviewer's own words

Round 3 graded 7 SURVIVES / 4 REFUSED and its pair read ADVANCED five arms and
RETURNED two. Both RETURNs came with a prescription, and this round is those two
prescriptions and nothing more.

* **Group C, the `either` shape** (round 3 `t07`) — *"Seriously weighed, but
  Block mode sacrificed twelve damage for three Block and never became
  competitive on this board."* What it needs: *"a stronger or more
  discriminating board."*
* **Group B, the `priced` shape** (round 3 `t05`) — *"Played, but the bundled
  AOE removal plus Block remained intent-insensitive; the extra cost removed
  only a follow-up,"* and in the round's summary, the shape needs a board where
  *"paying for Block did not compete with the card's decisive two-enemy
  removal."*

## The two repairs, one per group

**A pair is re-staged together**, so each group's shipped control is re-staged
beside its returned arm on the same seed.

**A SEED IS ONLY REPRODUCIBLE WITHIN ONE GAME BUILD, and this round is where we
found that out.** Round 3 ran on game v0.107.1; `R218` ported the mod and moved
the pin to v0.111.0, and the encounter generator moved with the game. Re-staging
round 3's two seeds on the new build produced two DIFFERENT fights:

* Group C's `XVE3PVZEPT` gave Seapunk 22/44 attacking for 11 in round 3, and on
  0.111.0 gives **Nibbit 24/45 attacking for 12**. One body, an attack
  telegraphed, and the enemy HP the file writes lands: the board is still the
  board this round designed, so group C KEEPS the seed and its mirror is
  re-declared to the body that actually appeared.
* Group B's `NMQLUYZDLV` gave three slimes in round 3 and on 0.111.0 gives **one
  Shrinker Beetle telegraphing a debuff** — no second body, no third, and no
  attack. Group B therefore could not keep its seed and was re-rolled.

`R95` already says live numbers are not comparable across a game build. This
adds the encounter itself to that list, which is worth writing down because a
pinned seed LOOKS like it survived a port and does not.

### Group C — one card leaves the hand

Round 3's group C held FOUR cards against THREE energy: the card under test plus
**two** Water's Edge plus All Streams Flow. The three 1-cost attacks alone came
to 21 damage, so the turn had a complete line that never touched the card, and
the Block mode was not losing to the card's own other mode — it was losing to
the rest of the hand. That is what "sacrificed twelve damage" measures.

**One Water's Edge is removed.** The hand is the card (2) plus Water's Edge (1)
plus All Streams Flow (1), and every line worth playing now goes through the
card:

| line | damage | Block |
|---|---|---|
| the card's damage half + All Streams Flow | **17** | 0 |
| the card's Block half + All Streams Flow | **9** | 3 |
| skip the card: Water's Edge + All Streams Flow | 15, one energy idle | 0 |

So the two modes are **8 damage apart** rather than twelve, and the hand cannot
route around the card.

**Two other numbers move with it, and both are consequences.** The enemy goes to
**24 HP**, which sits above the 17 this board can now produce, so no line is
lethal on either half — round 1's group A showed what a guaranteed kill does to
the fourth question. And the player goes to **14/70**. The live telegraph is 12,
so without Block the turn ends at 2 and with the three Block it ends at 5. At
22/70 three Block was a rounding error; here it more than doubles what is left
standing.

### Group B — one number moves

Round 3's group B carried two bodies at **3 HP**, which is the all-enemy hit's
own number. The card removed both whatever else was true, the removal alone
justified playing it, and the four Block rode in free. A grader answering "a
different telegraph would not have changed it" was reading the board correctly.

**The two non-attacking bodies go from 3 HP to 6 HP.** That is the repair.
Everything else the round intended to keep is round 3's: same player HP, same
Charge, same energy, same hand, an attacker behind Block and out of lethal
reach. The seed and the attacker's exact numbers are the exception, and the
re-roll section below says why.

Three damage now removes nothing. The card stops being a board clear and becomes
what it prints — chip damage spread three ways, plus Block — so the reason to
play it has to be the Block and the telegraph, which is the arm. The removal is
still available, just not from this card: Water's Edge (6) kills one small body
and All Streams Flow (9) kills the other, for two energy. That is the competing
line, and choosing between it and the card is now a choice about the incoming
attack.

**One staging detail.** The two non-attackers start as the LARGEST bodies on
the board, so they are written down through `highest_hp` twice; after those two
writes the attacker is the largest thing left, and `highest_hp` then names IT.
That is why the attacker's own two writes come third.

## The lethal and clear check, at TRUE card values

Card values: Water's Edge 6, All Streams Flow **9** at 8 Charge (base 5, +1 per
2), Coral Guard 5 Block, Thoma 8 damage + 3 Block, Shinobu 3 to ALL + 4 Block.

| group | energy | most damage on the attacker | attacker's effective HP | lethal? | board clear? |
|---|---|---|---|---|---|
| C | 3 | 17 — the card's 8 + All Streams 9 | 24 | **no** | n/a, one body |
| B | 3 | 15 — Water's Edge 6 + All Streams 9 | 9 HP **+ 8 Block = 17** | **no** | **no** — clearing both smalls costs 2 energy and leaves 1, on which neither half's card is affordable |

## The map from filename to turn id

The turn id is printed into the design-blind packet, so it is deliberately
opaque: `-priced` or `-either` inside an id would tell the grader which arm it
was holding. The **filename** names the arm, because only the tooling and the
packet-writer read filenames.

All four were staged on ONE build, **`0.2.1293+proto`** (2026-08-29), the
shipped halves included.

| file | turn id | arm | card under test | group | seed |
|---|---|---|---|---|---|
| `thoma-crimson-ooyoroi-shipped.yaml` | `kokomi-slice1-r4-t01` | 2/3 — baseline | `thoma_crimson_ooyoroi` (shipped) | C | `XVE3PVZEPT` |
| `thoma-crimson-ooyoroi-either.yaml` | `kokomi-slice1-r4-t02` | 2 — mutually exclusive | `proto_thoma_crimson_ooyoroi_either` | C | `XVE3PVZEPT` |
| `shinobu-sanctifying-ring-shipped.yaml` | `kokomi-slice1-r4-t03` | 2/3 — baseline | `shinobu_sanctifying_ring` (shipped) | B | `R7W86HG7WHUD` |
| `shinobu-sanctifying-ring-priced.yaml` | `kokomi-slice1-r4-t04` | 3 — priced in cost | `proto_shinobu_sanctifying_ring_priced` | B | `R7W86HG7WHUD` |

### Group B's re-roll — sixteen of them

The condition: THREE bodies, at least one telegraphing an ATTACK, and an
attacker the board can put out of lethal reach. Sixteen rolls on `0.111.0`; the
first fifteen drew one or two bodies (Seapunk, Nibbit, Sludge Spinner, Fuzzy
Wurm Crawler, Shrinker Beetle, paired Toadpoles). Roll sixteen,
**`R7W86HG7WHUD`**, is the first three-body fight: Twig Slime (S) 9/9 attacking
for 4, Leaf Slime (M) handing out two Status cards, Leaf Slime (S) attacking
for 3.

**One number moved because of the roll.** Round 3's attacker sat at 10 HP behind
6 Block, an effective 16 against a ceiling of 15. This seed's attacker generates
at **9/9** and `set_hp` clamps at a creature's maximum, so nine behind **eight**
is the arithmetic that reaches the same property — an effective 17 against the
same ceiling of 15, best line leaves it alive on 2. The property is identical
and only the numbers reaching it moved.

**The third body telegraphs an attack rather than a Status card**, which round 3's
did not. That is the roll's, not a choice; it makes the total incoming 7 against
the card's 4 Block and if anything sharpens the defensive question the arm asks.

## Closeness

`DOMINANCE_GAP` is 0.5. **All four SURVIVE.** What that means exactly: no single
line on the board is worth more than twice the runner-up in the pilot's own
scoring currency, so the falsifier does not refuse the turn. It is not a claim
that the turn is good, interesting, or better than its twin, and it is not
comparable between two rows of the table — R213 F allows the reading only as a
refusal.

| turn | gap | top1 / top2 | lines |
|---|---|---|---|
| `t01` | 0.1345 | 22.300 / 19.300 | 6 |
| `t02` | 0.1138 | 16.700 / 14.800 | 6 |
| `t03` | 0.1224 | 24.500 / 21.500 | 6 |
| `t04` | 0.0452 | 15.500 / 14.800 | 4 |
