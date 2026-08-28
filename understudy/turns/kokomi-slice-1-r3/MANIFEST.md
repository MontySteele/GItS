# Kokomi slice 1, round 3 — turn manifest

Eleven staged turns, three arms, four matched groups — **round 2's boards
unchanged except where this file says otherwise**, re-staged against faces that
state their scaling once. R216 fixed the pool and the arms; R213 B quarantines
every prototype row they name; R215 B makes every number *measured on a row*
unquotable — and makes the closeness column below the one exception, because it
reads the **turn**, not the sheet.

**Nothing in this file rates an arm.** The designer of these rows may not grade
them (R213's first guard). The columns record what was set and what happened;
the four-question form is somebody else's.

## Why there is a round 3

Round 2 graded **4 SURVIVES / 7 REFUSED**, every refusal `intent_insensitive`.
Its own finding, `EB-164`, explains most of them: *All Streams Flow to the Sea*
printed a number that **already carried** its Charge rider and then said
"Scales with Charge" beneath it, so four of eleven graders and the pair reviewer
counted the rider twice and read the card as **13** where the game deals **9**.
`understudy.staged_turn execute` settled it live on the staged board — Seapunk
22 HP → 1.

EB-164 is fixed at the generator and the fix is in the build these eleven are
staged on. **Not one printed number moved**; the sheets are frozen (R213). The
live face now reads, verbatim from `t09`'s packet:

> All Streams Flow to the Sea — *Deal 9 damage, already including Charge.
> Applies Hydro.*

**Two board changes, and they are the only ones.** Both are lethal-line
repairs, made with the CORRECT card values.

1. **Group B's attacker gets 6 Block.** At 10 HP and no Block it died to two
   1-cost attacks — Water's Edge 6 + All Streams Flow **9** = 15, for two of
   the three energy, with an energy to spare. That is a line that removes the
   telegraph, so the Block-versus-AoE choice was never actually asked. It is
   given 6 Block (effective 16 against a ceiling of 15), so the best
   single-target line leaves it alive on 1. **Block and not HP** because
   `set_hp` clamps at a creature's own maximum and this body generates at
   10/10 — a write of 16 came back as 10, which is how we know. The two small
   bodies stay at 3 (the AoE's own number) and the telegraph stays at 4 (the
   Block half's own number).

   **This also narrows round 2's account of itself.** Group B's two refusals
   were **SOUND**, not EB-164 misreads: the lethal line existed at the TRUE
   value of 9. Only groups C and D rested on the phantom 13.

2. **Group D is on a new seed.** Round 2 could not land group D's defensive
   threshold — the pinned attacker telegraphed 8 against a 6-Block half — and
   no verb in the staging grammar writes an intent (`R217 E` names and defers
   an enemy composition and intent setter). The only lever is the seed, and it
   is pulled here. See **the group D re-roll** below.

Groups A and C are the round-2 boards on the round-2 seeds, unchanged.

## The lethal check, per group, at TRUE card values

Round 2's defect was a phantom lethal line. This round states the arithmetic
for every board before staging, so a real one cannot hide behind it. Card
values: Water's Edge 6, All Streams Flow **9** at 8 Charge (base 5, +1 per 2),
Gorou 6 (cost 0, self-Exhausts), Coral Guard 5 Block, Pearl Barrage 5 + 3 per
cost of the card it Exhausts, Tidal Barrage 5 + 3 per card Exhausted this turn
including its own, Shinobu 3 to ALL + 4 Block, Thoma 8 + 3 Block, Itto 14 + 6
Block.

| group | energy | most damage this hand can put on the attacker | attacker's effective HP | lethal? |
|---|---|---|---|---|
| A | 2 | 29 — Gorou 6 (free) + Tidal Barrage 14 + All Streams 9; the shipped half's ceiling is 23 | 38 | **no** |
| B | 3 | 15 — Water's Edge 6 + All Streams 9 (2 energy) | 10 HP **+ 6 Block = 16** | **no** (round 2: yes, at 10) |
| C | 3 | 21 — Water's Edge 6 ×2 + All Streams 9 | 22 | **no** |
| D | 3 | 21 — Water's Edge 6 ×2 + All Streams 9; the card's own mode is 14 + 6 = 20 | 24 | **no** |

Board clears are checked the same way: group B's three bodies are 16
(effective) / 3 / 3 and the largest total this hand can distribute across them
is 3 AoE + 6 = 9, so no line ends the fight.

## The group D re-roll

Round 1's rule, applied: roll fresh seeds, record every roll, stage all three
halves of the group on whatever seed is reached. **The condition:** the first
fight is ONE body telegraphing an ATTACK of at most 6. Fourteen rolls, on the
`0.2.1252+proto` build, staging `itto-superlative-superstrength-shipped.yaml`:

| # | seed | first fight |
|---|---|---|
| 1 | `979VFWLPFX` | one body — Sludge Spinner, attacks for 8 |
| 2 | `BAB9GR0MMP` | two bodies — Toadpole (Buff), Toadpole attacks for 7 |
| 3 | `KYWG41SXUP` | three bodies — Twig Slime (S) attacks for 4, two Slimes give Status |
| 4 | `LNZAZWPE96` | one body — Sludge Spinner, attacks for 8 |
| 5 | `A1CQZ9QMD6` | one body — Shrinker Beetle, applies a Debuff |
| 6 | `3588WBL3B1` | two bodies — Toadpole (Buff), Toadpole attacks for 7 |
| 7 | `4P3QVZ8Z74` | one body — Seapunk, attacks for 11 |
| 8 | `VSEECP1HMA` | one body — Sludge Spinner, attacks for 8 |
| 9 | `XT0R5DJR75` | one body — Sludge Spinner, attacks for 8 |
| 10 | **`21RD94VY60`** | **one body — Fuzzy Wurm Crawler, attacks for 4** — meets it |
| 11 | `6H4P3654P2` | two bodies — Corpse Slug attacks for 8, Corpse Slug applies a Debuff |
| 12 | `LDNFDA0DT9` | one body — Sludge Spinner, attacks for 8 |
| 13 | `CXFU8AFEHA` | one body — Fuzzy Wurm Crawler, attacks for 4 |
| 14 | `LF5SRE4MQM` | one body — Nibbit, attacks for 12 |

Roll 10 is the first that meets the condition and is the seed all three group-D
halves are staged on. It was not drawn at random: it is a candidate lifted from
round 1's own recorded roll list and confirmed live here, which is why it
appears in sequence rather than at the end. Rolls 11–14 were taken after it,
looking for a telegraph of exactly 6.

**No roll in fourteen produced a 5 or a 6.** The one-body Act-1 telegraphs that
appeared at all were 4, 8, 11 and 12, so "exactly 6" was not available to be
chosen — 4 is the value the condition could actually reach. The consequence is
that group D's Block half now **fully answers** the telegraph with 2 of its 6
spare, where round 2's answered three quarters of it. The player-side threshold
sits at its floor: at 16 of 70, taking 4 is a quarter of what is left.

## The map from filename to turn id

The turn id is printed into the design-blind packet, so it is deliberately
opaque: `-priced` inside an id would tell the grader which arm it was holding.
The **filename** names the arm, because only the tooling and the packet-writer
read filenames. This table is the map.

All eleven were staged on ONE build, **`0.2.1252+proto`** (2026-08-28), the
shipped halves included — the same rule round 2 adopted, and the first build
carrying `EB-164`'s faces.

| file | turn id | arm | card under test | group | seed | packet sha | closeness (declared board) |
|---|---|---|---|---|---|---|---|
| `pearl-barrage-shipped.yaml` | `kokomi-slice1-r3-t01` | 1 — counting basis | `pearl_barrage` (shipped) | A | `HUMWKRKNCE` | `72c92d38d218f53e05de2b44a1551756c6c9ce76df0d4bf71c83dfae439fefdf` | SURVIVES, gap 0.0256 over 27 lines; observed identical |
| `pearl-barrage-turn.yaml` | `kokomi-slice1-r3-t02` | 1 — counting basis | `proto_pearl_barrage_turn` | A | `HUMWKRKNCE` | `9741934c8dad3bcdaceee758bdd98a95bf910248a8de060264f9c31e55806822` | SURVIVES, gap 0.1136 over 27 lines; observed identical |
| `shinobu-sanctifying-ring-shipped.yaml` | `kokomi-slice1-r3-t03` | 2/3 — baseline | `shinobu_sanctifying_ring` (shipped) | B | `NMQLUYZDLV` | `a344a746ad16a6fc421a59308af050a38f97af262f294f2998aa12bfa793b3ce` | SURVIVES, gap 0.1224 over 6 lines; observed identical |
| `shinobu-sanctifying-ring-either.yaml` | `kokomi-slice1-r3-t04` | 2 — mutually exclusive | `proto_shinobu_sanctifying_ring_either` | B | `NMQLUYZDLV` | `ff4e6a54d3183d7b299eb7e045bfda3c81461d686d0c1300eed103a47caa57c1` | SURVIVES, gap 0.1638 over 6 lines; observed identical |
| `shinobu-sanctifying-ring-priced.yaml` | `kokomi-slice1-r3-t05` | 3 — priced in cost | `proto_shinobu_sanctifying_ring_priced` | B | `NMQLUYZDLV` | `0feffa23d1cc823057a5f85a9b2a0bdf2b13ee947e6049623fd92d50bfc4d516` | SURVIVES, gap 0.0452 over 4 lines; observed identical |
| `thoma-crimson-ooyoroi-shipped.yaml` | `kokomi-slice1-r3-t06` | 2/3 — baseline | `thoma_crimson_ooyoroi` (shipped) | C | `XVE3PVZEPT` | `4711afe5d2721035a63e2795cb5e58a98ce3f512f09778bf2782e363ba3e5b58` | SURVIVES, gap 0.0717 over 11 lines; observed identical |
| `thoma-crimson-ooyoroi-either.yaml` | `kokomi-slice1-r3-t07` | 2 — mutually exclusive | `proto_thoma_crimson_ooyoroi_either` | C | `XVE3PVZEPT` | `09cf0ab1b96e714565dcd558a1ea25e6cd4a6d11f50a0d1b60a329b6a93780d1` | SURVIVES, gap 0.1932 over 11 lines; observed identical |
| `thoma-crimson-ooyoroi-priced.yaml` | `kokomi-slice1-r3-t08` | 3 — priced in cost | `proto_thoma_crimson_ooyoroi_priced` | C | `XVE3PVZEPT` | `aaee7a683ba4d2624e4b1ebd8cd8cfb0b614a4f297210732c4f4125d13c951da` | SURVIVES, gap 0.2850 over 8 lines; observed identical |
| `itto-superlative-superstrength-shipped.yaml` | `kokomi-slice1-r3-t09` | 2/3 — baseline | `itto_superlative_superstrength` (shipped) | D | `21RD94VY60` | `9bbd0d2ff30aff698275ed02fa1d0e05c372a273a21b96d57463eddd1508117f` | SURVIVES, gap 0.1091 over 11 lines; observed identical |
| `itto-superlative-superstrength-either.yaml` | `kokomi-slice1-r3-t10` | 2 — mutually exclusive | `proto_itto_superlative_superstrength_either` | D | `21RD94VY60` | `7367f43dbeacc0e73b35e1b41b822fbfcf9cfc389904ddc05a375118f9b66a4f` | SURVIVES, gap 0.0881 over 11 lines; observed identical |
| `itto-superlative-superstrength-priced.yaml` | `kokomi-slice1-r3-t11` | 3 — priced in cost | `proto_itto_superlative_superstrength_priced` | D | `21RD94VY60` | `7f5cc99378f5528418e8375c3a51eaed74a96b084642eb3087aec0261ccfd66e` | SURVIVES, gap 0.1063 over 8 lines; observed identical |

`DOMINANCE_GAP` is 0.5. The first reading in each cell is of the **declared**
board — the mirror available with no game running; "observed identical" means
`closeness --observed`, which scores the board the grader actually saw, returned
the same verdict and the same gap to four decimal places over the same number of
lines. That is true on **all eleven**, as it was in round 2: the exact-hand door
leaves the two records nothing to disagree about. Both are written into
`review/qa/<turn id>/closeness.json`.

**What "SURVIVES" means here, exactly:** no single line on the board is worth
more than twice the runner-up in the pilot's own scoring currency, so the
falsifier does not refuse the turn. It is not a claim that the turn is good,
interesting, or better than its twin, and it is not comparable between two rows
of the table — R213 F allows the reading only as a refusal.

**Every packet's hand is the declared hand**, `exact_hand: true` on all eleven:
5/5 on group A, 3/3 on B, 4/4 on C and D. `stage` refuses to write a packet
whose live hand is not the declared multiset, so this is a precondition of the
files above existing rather than an observation about them.

**Enemies and intents match across every half of every group**, name for name,
HP for HP and telegraph for telegraph: A — Nibbit 38/45 attacking 12; B — Twig
Slime (S) 10/10 behind 6 Block attacking 4, Leaf Slime (M) 3/32 and Leaf Slime
(S) 3/15 each handing out Status cards; C — Seapunk 22/44 attacking 11; D —
Fuzzy Wurm Crawler 24/56 attacking 4.

## Group boards, and the prescription each executes

The prescriptions are quoted from the round-1 pair read. Each file's own header
carries the same quote beside the arithmetic. Only the two rows marked
**changed** differ from round 2.

| group | energy | player HP | Charge | enemies | alternatives in hand |
|---|---|---|---|---|---|
| A (Pearl Barrage) | 2 | 24/70 | 8 | one, 38 HP, attacks for 12 | Gorou opener (0, self-Exhausts), Send the Runner (0, Exhausts one), Coral Guard (1), All Streams Flow (1) |
| B (Shinobu) — **changed** | 3 | 16/70 | 8 | three: 10 HP **behind 6 Block** attacking for 4, two at 3 HP handing out Status cards | Water's Edge (1), All Streams Flow (1) |
| C (Thoma) | 3 | 22/70 | 8 | one, 22 HP, attacks for 11 | Water's Edge ×2 (1 each), All Streams Flow (1) |
| D (Itto) — **changed** | 3 | 16/70 | 8 | one, 24 HP, **attacks for 4** (new seed) | Water's Edge ×2 (1 each), All Streams Flow (1) |

Every file's header carries its group's full rationale and, on the two changed
groups, the round-3 change and the arithmetic behind it. Round 2's own
prescriptions — the exact-hand door, no redundant standalone Block, thresholds
written on both halves — are unchanged and are quoted in the files.

## The seeds

Groups A, B and C keep round 2's seeds, which round 2 carried over from round 1,
so those fights are the ones their boards were written against — group A's
Nibbit, group B's three slimes with one attacker, group C's Seapunk. Group D is
on `21RD94VY60`, reached by the re-roll above. Within a group every half is
staged with `--seed <that value>`; two halves on two seeds are two different
fights, and the pair has then measured the encounter instead of the card.

**The intent check is not optional.** The declared boards all say the enemy
telegraphs an ATTACK, because defence is worth nothing against anything else and
what defence costs is the entire slice. All four groups honoured it live.

## Running them

```sh
# no game needed, any checkout
.venv/Scripts/python -m understudy.staged_turn check
.venv/Scripts/python -m understudy.staged_turn closeness \
    understudy/turns/kokomi-slice-1-r3/pearl-barrage-shipped.yaml

# the live half, from the art-bearing main checkout, attended
.venv/Scripts/python -m understudy.staged_turn stage \
    understudy/turns/kokomi-slice-1-r3/pearl-barrage-shipped.yaml \
    --why "kokomi slice 1 round 3, arm 1, shipped half" --seed HUMWKRKNCE
```

All eleven need the dev build (`klee-mod\build\deploy_proto.ps1`): the seven
prototype halves for their rows, and the four shipped halves so that both halves
of a pair sit on one build. `OPERATIONS.md` carries both paths, and restoring
the release build afterwards.
