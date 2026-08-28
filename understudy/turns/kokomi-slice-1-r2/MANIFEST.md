# Kokomi slice 1, round 2 — turn manifest

Eleven staged turns, three arms, four matched groups — the same eleven cards
round 1 staged, on rebuilt boards. R216 fixed the pool and the arms; R213 B
quarantines every prototype row they name; R215 B makes every number *measured
on a row* unquotable — and makes the closeness column below the one exception,
because it reads the **turn**, not the sheet.

**Nothing in this file rates an arm.** The designer of these rows may not grade
them (R213's first guard). The columns record what was set and what happened;
the four-question form is somebody else's.

## Why there is a round 2

The independent seat's pair read of round 1
(`review/qa/kokomi-slice-1-pair-review-codex-gpt-5.6-sol.md`) returned all
seven prototype arms, and its reason on six of the seven was the same: **the
boards, not the cards**. Its summary line for the two Shinobu arms is the
shortest statement of the failure — *"Neither grader played or seriously
weighed the card"* and *"Ascension and Coral Guard supplied the entire
choice"*.

Three things caused it, and round 2 changes all three and no printed number.

1. **The hand was not the declared hand.** The game deals its own opening hand
   on top of the granted one, so a file declaring four cards was staged with
   ten — two extra Coral Guards, two free Gorou attacks and, in group B, a
   Nereid's Ascension. Those cards supplied the race-versus-turtle choice
   before the card under test was reached. Every round-2 file declares
   `exact_hand: true`, so the packet shows the declared hand and nothing else.
2. **A redundant standalone Block sat beside every Block half.** A 5-Block card
   at 1 energy beats a 3-Block rider by inspection; groups B, C and D now carry
   no standalone Block at all, and group A carries exactly one with its reason
   written in the file.
3. **Nothing crossed a threshold.** Round 1's enemies sat at HP nothing on the
   board could reach and the player sat at 48/70 where a single-digit telegraph
   is cosmetic. Every round-2 board writes enemy HP against the turn's own
   ceiling and player HP so the telegraph takes at least a quarter of what is
   left.

## The map from filename to turn id

The turn id is printed into the design-blind packet, so it is deliberately
opaque: `-priced` inside an id would tell the grader which arm it was holding,
which is the one thing a blind grade cannot survive. The **filename** names the
arm, because only the tooling and the packet-writer read filenames. This table
is the map.

| file | turn id | arm | card under test | group | seed | staged | packet sha | closeness (declared board) |
|---|---|---|---|---|---|---|---|---|
| `pearl-barrage-shipped.yaml` | `kokomi-slice1-r2-t01` | 1 — counting basis | `pearl_barrage` (shipped) | A | `HUMWKRKNCE` | `0.2.1248+proto` (2026-08-28) | `8177100724862e2ead263683e89414b32e7eaa45ec0267f1260b320d31d90b51` | SURVIVES, gap 0.0256 over 27 lines; observed gap 0.0256 over 27 lines |
| `pearl-barrage-turn.yaml` | `kokomi-slice1-r2-t02` | 1 — counting basis | `proto_pearl_barrage_turn` | A | `HUMWKRKNCE` | `0.2.1248+proto` (2026-08-28) | `cc315eb12b32e562fc2e38ef8e588f1cb7eb2c52e353da9377fdff4f080ecdc0` | SURVIVES, gap 0.1136 over 27 lines; observed gap 0.1136 over 27 lines |
| `shinobu-sanctifying-ring-shipped.yaml` | `kokomi-slice1-r2-t03` | 2/3 — baseline | `shinobu_sanctifying_ring` (shipped) | B | `NMQLUYZDLV` | `0.2.1248+proto` (2026-08-28) | `65909dacab6b365c8240517c541c7cac9388967f099ea212117c8e3dea52822b` | SURVIVES, gap 0.1224 over 6 lines; observed gap 0.1224 over 6 lines |
| `shinobu-sanctifying-ring-either.yaml` | `kokomi-slice1-r2-t04` | 2 — mutually exclusive | `proto_shinobu_sanctifying_ring_either` | B | `NMQLUYZDLV` | `0.2.1248+proto` (2026-08-28) | `48ab4f50b2e25b47528b54cdf80e8824a9d13f44b59ea86fc887a383faa9b564` | SURVIVES, gap 0.1638 over 6 lines; observed gap 0.1638 over 6 lines |
| `shinobu-sanctifying-ring-priced.yaml` | `kokomi-slice1-r2-t05` | 3 — priced in cost | `proto_shinobu_sanctifying_ring_priced` | B | `NMQLUYZDLV` | `0.2.1248+proto` (2026-08-28) | `d1c4571cc92a71596c14302852d001009901909e236efc9f6ce9bfcf89d12939` | SURVIVES, gap 0.0452 over 4 lines; observed gap 0.0452 over 4 lines |
| `thoma-crimson-ooyoroi-shipped.yaml` | `kokomi-slice1-r2-t06` | 2/3 — baseline | `thoma_crimson_ooyoroi` (shipped) | C | `XVE3PVZEPT` | `0.2.1248+proto` (2026-08-28) | `063982445db33e6f012a05a2a17de0ee1056a82aa1a0a332a8abccee1413b3cf` | SURVIVES, gap 0.0717 over 11 lines; observed gap 0.0717 over 11 lines |
| `thoma-crimson-ooyoroi-either.yaml` | `kokomi-slice1-r2-t07` | 2 — mutually exclusive | `proto_thoma_crimson_ooyoroi_either` | C | `XVE3PVZEPT` | `0.2.1248+proto` (2026-08-28) | `09766ea5d2d1bf2b1a4e4cacfa31fb9ad3358525cd93438b56c48a894833646d` | SURVIVES, gap 0.1932 over 11 lines; observed gap 0.1932 over 11 lines |
| `thoma-crimson-ooyoroi-priced.yaml` | `kokomi-slice1-r2-t08` | 3 — priced in cost | `proto_thoma_crimson_ooyoroi_priced` | C | `XVE3PVZEPT` | `0.2.1248+proto` (2026-08-28) | `4e6edce831e230b21ffa4d4a0a5a0362b005fa467c10bb0154a0259d6b82d645` | SURVIVES, gap 0.2850 over 8 lines; observed gap 0.2850 over 8 lines |
| `itto-superlative-superstrength-shipped.yaml` | `kokomi-slice1-r2-t09` | 2/3 — baseline | `itto_superlative_superstrength` (shipped) | D | `X1BQR3FU4G` | `0.2.1248+proto` (2026-08-28) | `f8a71aac32bb00b46066ce212a4c8e690b71ed3232c925fd0d9414908219e6d9` | SURVIVES, gap 0.1003 over 11 lines; observed gap 0.1003 over 11 lines |
| `itto-superlative-superstrength-either.yaml` | `kokomi-slice1-r2-t10` | 2 — mutually exclusive | `proto_itto_superlative_superstrength_either` | D | `X1BQR3FU4G` | `0.2.1248+proto` (2026-08-28) | `fff51fbc3096422baf4b56d1d2a586dc9a7b84580b16ff1a4595d695a396ba04` | SURVIVES, gap 0.0881 over 11 lines; observed gap 0.0881 over 11 lines |
| `itto-superlative-superstrength-priced.yaml` | `kokomi-slice1-r2-t11` | 3 — priced in cost | `proto_itto_superlative_superstrength_priced` | D | `X1BQR3FU4G` | `0.2.1248+proto` (2026-08-28) | `5df4cdbf73427af62b5f8f4d038989c50673dc8854772ad6f14a52a707b43b56` | SURVIVES, gap 0.0096 over 8 lines; observed gap 0.0096 over 8 lines |

`DOMINANCE_GAP` is 0.5. The first reading in each cell is of the **declared**
board — the mirror available with no game running; the second is
`closeness --observed`, which scores the board the grader actually saw. Both
are written into `review/qa/<turn id>/closeness.json`.

**The two readings are identical on all eleven turns, to four decimal places
and line for line.** That is the exact-hand door's whole effect, stated as a
number: in round 1 the observed board carried the game's dealt hand and the two
readings disagreed on every turn (`0.0256` against `0.0175` on the first one,
and four observed ties of `0.0000` where the declared boards read between
`0.0881` and `0.2850`). Here the live hand IS the declared hand, the live
intents are the declared intents, and there is nothing left for the two records
to disagree about.

**All eleven were staged on ONE build**, `0.2.1248+proto`, including the four
shipped halves. Round 1 put the shipped halves on a release build and the
prototype halves on a dev build, which is one more difference between the halves
of a pair than a matched pair should have. The dev build's extra rows are
off-pool and unreachable except by the grant that names them, so a shipped half
staged on it is the same board it would have been on the release build.

**What "SURVIVES" means here, exactly:** no single line on the declared board
is worth more than twice the runner-up in the pilot's own scoring currency, so
the falsifier does not refuse the turn. It is not a claim that the turn is
good, interesting, or better than its twin, and it is not comparable between
two rows of the table — R213 F allows the reading only as a refusal.

## Group boards, and the prescription each executes

The prescriptions are quoted from the round-1 pair read. Each file's own header
carries the same quote beside the arithmetic.

| group | energy | player HP | Charge | enemies | alternatives in hand |
|---|---|---|---|---|---|
| A (Pearl Barrage) | 2 | 24/70 | 8 | one, 38 HP, attacks for 12 | Gorou opener (0, self-Exhausts), Send the Runner (0, Exhausts one), Coral Guard (1), All Streams Flow (1) |
| B (Shinobu) | 3 | 16/70 | 8 | three: 10 HP attacking for 4, two at 3 HP handing out Status cards | Water's Edge (1), All Streams Flow (1) |
| C (Thoma) | 3 | 22/70 | 8 | one, 22 HP, attacks for 11 | Water's Edge ×2 (1 each), All Streams Flow (1) |
| D (Itto) | 3 | 16/70 | 8 | one, 24 HP, attacks for 8 | Water's Edge ×2 (1 each), All Streams Flow (1) |

**Group A — *"Raise Nibbit's HP enough that Tidal Barrage cannot guarantee
lethal, while keeping its exhaust scaling relevant."*** The turn's whole
ceiling is 29 damage on the half that counts the turn and 23 on the half that
counts the one card it chose; the body is written to **38**, which is above
both by a margin a card drawn mid-turn cannot close. Round 1's 34 was inside
the turn's reach, both graders took the lethal line, and the fourth question
was then being asked about a fight that was already over — which is exactly
what GPT refused `t02` for. Two free rotations stay on the board because they
are the only thing that separates the two counting bases. One Block card stays
because this arm is about a counting basis and the card under test has no Block
half of its own; with none, the 12-damage telegraph would be a fact the turn
cannot act on.

**Group B — *"Change the board so Warding Ring itself controls a threshold —
ideally where its 3 AoE damage kills or sets up multiple enemies, while its 4
Block answers meaningful surviving damage"*** and *"create AoE thresholds where
3 damage plus 4 Block is a credible full-turn package."* Both halves now land
on a threshold exactly: the two non-attacking bodies are written to **3 HP**,
which is the AoE's own number, so one card removes both; and the attacker's
telegraph is **4**, which is the Block half's own number, so the Block half
answers the hit whole. The pinned seed is what makes both true at once — its
first fight is three bodies with one attacker telegraphing 4. The hand holds
**two** attacks against **three** bodies, deliberately: with three attacks the
small bodies can be cleared one at a time and "damage all" stops being a
different card. Those two attacks together are also exactly enough to kill the
attacker, which is the third line and the one the Block half competes with.

**Group C — *"remove or constrain the Coral Guards that make the 3-Block mode
redundant"*** and *"construct a board where 8 damage and 3 Block jointly cross
thresholds."* No mode value moved — repricing and rebuilding were the
reviewer's two options and moving a printed number would make whatever this
round shows unattributable. The 3-Block half is now **the only Block on the
board**. Three energy of ordinary attacks is 21 and the body is written to
**22**, so there is no lethal line on any half: every line ends with the hit
landing, and what the turn bought is measured against what it costs to take 11
at 22 HP.

**Group D — *"Use a board where Oni Rush's two modes — not Coral Guard — are
the pivotal alternatives"*** and *"change the board so the combined 14 damage
and 6 Block cross both an offensive and defensive threshold."* The standalone
Block is gone, so the two modes are the only things on the board that do what
they do. Offensively: three ordinary attacks are 21 and the damage mode plus
the Charge reader is 23, against a body written to **24** — neither crosses,
and the 14 is a large fraction of a fight rather than a kill, because a kill
would end the turn's argument the way group A's did in round 1.
**Defensively the threshold does not land exactly, and that is a limit rather
than a choice:** the pinned fight's attacker telegraphs 8 and the Block half is
6, so it answers three quarters of the hit. The staging grammar has no verb
that writes an intent (an enemy composition and intent setter is named and
deferred, R217 E), and re-rolling for a body that telegraphs exactly 6 would
change the fight this group's other two halves stand on. The threshold that IS
written is the player's: at 16 of 70, taking 8 is half of what is left and
taking 2 is not.

## The seeds

Each group's seed is **carried over from round 1**, so the fight is the one
these boards were written against — group A's Nibbit, group B's three slimes
with one attacker, group C's Seapunk, group D's Sludge Spinner. Within a group
every half is staged with `--seed <that value>`; two halves on two seeds are two
different fights, and the pair has then measured the encounter instead of the
card.

**If the pinned seed's live fight is not the one above** — a different body
count, or a telegraph that is not an attack — the round-1 rule applies:
re-roll, record every roll, and stage every half of that group on whatever seed
was reached. Writing HP onto the rolled bodies is the normal case; re-rolling
is the exception, and group B's round-1 seed took seven rolls to reach a
multi-body first fight.

**And the intent check is not optional.** The declared boards all say the enemy
telegraphs an ATTACK, because defence is worth nothing against anything else
and what defence costs is the entire slice.

## Running them

```sh
# no game needed, any checkout
.venv/Scripts/python -m understudy.staged_turn check
.venv/Scripts/python -m understudy.staged_turn closeness \
    understudy/turns/kokomi-slice-1-r2/pearl-barrage-shipped.yaml

# the live half, from the art-bearing main checkout, attended
.venv/Scripts/python -m understudy.staged_turn stage \
    understudy/turns/kokomi-slice-1-r2/pearl-barrage-shipped.yaml \
    --why "kokomi slice 1 round 2, arm 1, shipped half" --seed HUMWKRKNCE
```

The seven prototype halves need a dev build first
(`klee-mod\build\deploy_proto.ps1`); the four shipped halves stage on a release
build. `OPERATIONS.md` carries both paths, and restoring the release build
afterwards.
