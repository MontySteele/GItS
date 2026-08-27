# Kokomi slice 1 — turn manifest

Eleven staged turns, three arms, four matched groups. R216 fixed the pool and
the arms; R213 B quarantines every prototype row they name; R215 B makes every
number *measured on a row* unquotable — and makes the closeness column below
the one exception, because it reads the **turn**, not the sheet.

**Nothing in this file rates an arm.** The designer of these rows may not grade
them (R213's first guard). The columns record what was set and what happened;
the four-question form is somebody else's.

## The map from filename to turn id

The turn id is printed into the design-blind packet, so it is deliberately
opaque: `...-priced` inside an id would tell the grader which arm it was
holding, which is the one thing a blind grade cannot survive. The **filename**
names the arm, because only the tooling and the packet-writer read filenames.
This table is the map.

| file | turn id | arm | card under test | pair | seed | staged | packet sha | closeness (declared board) |
|---|---|---|---|---|---|---|---|---|
| `pearl-barrage-shipped.yaml` | `kokomi-slice1-t01` | 1 — counting basis | `pearl_barrage` (shipped) | A | unpinned | **pending** | — | SURVIVES, gap 0.0256 over 27 lines |
| `pearl-barrage-turn.yaml` | `kokomi-slice1-t02` | 1 — counting basis | `proto_pearl_barrage_turn` | A | unpinned | **pending** (dev build) | — | SURVIVES, gap 0.1136 over 27 lines |
| `shinobu-sanctifying-ring-shipped.yaml` | `kokomi-slice1-t03` | 2/3 — baseline | `shinobu_sanctifying_ring` (shipped) | B | unpinned | **pending** | — | SURVIVES, gap 0.0372 over 11 lines |
| `shinobu-sanctifying-ring-either.yaml` | `kokomi-slice1-t04` | 2 — mutually exclusive | `proto_shinobu_sanctifying_ring_either` | B | unpinned | **pending** (dev build) | — | SURVIVES, gap 0.2850 over 11 lines |
| `shinobu-sanctifying-ring-priced.yaml` | `kokomi-slice1-t05` | 3 — priced in cost | `proto_shinobu_sanctifying_ring_priced` | B | unpinned | **pending** (dev build) | — | SURVIVES, gap 0.2850 over 8 lines |
| `thoma-crimson-ooyoroi-shipped.yaml` | `kokomi-slice1-t06` | 2/3 — baseline | `thoma_crimson_ooyoroi` (shipped) | C | unpinned | **pending** | — | SURVIVES, gap 0.0717 over 11 lines |
| `thoma-crimson-ooyoroi-either.yaml` | `kokomi-slice1-t07` | 2 — mutually exclusive | `proto_thoma_crimson_ooyoroi_either` | C | unpinned | **pending** (dev build) | — | SURVIVES, gap 0.1932 over 11 lines |
| `thoma-crimson-ooyoroi-priced.yaml` | `kokomi-slice1-t08` | 3 — priced in cost | `proto_thoma_crimson_ooyoroi_priced` | C | unpinned | **pending** (dev build) | — | SURVIVES, gap 0.2850 over 8 lines |
| `itto-superlative-superstrength-shipped.yaml` | `kokomi-slice1-t09` | 2/3 — baseline | `itto_superlative_superstrength` (shipped) | D | unpinned | **pending** | — | SURVIVES, gap 0.1003 over 11 lines |
| `itto-superlative-superstrength-either.yaml` | `kokomi-slice1-t10` | 2 — mutually exclusive | `proto_itto_superlative_superstrength_either` | D | unpinned | **pending** (dev build) | — | SURVIVES, gap 0.0881 over 11 lines |
| `itto-superlative-superstrength-priced.yaml` | `kokomi-slice1-t11` | 3 — priced in cost | `proto_itto_superlative_superstrength_priced` | D | unpinned | **pending** (dev build) | — | SURVIVES, gap 0.0096 over 8 lines |

`DOMINANCE_GAP` is 0.5. Every reading above is a reading of the **declared**
board — the five-card mirror available with no game running — and is written
by `staged_turn closeness` into `review/qa/<turn id>/closeness.json`. Once a
turn is staged, re-read it with `closeness --observed`, which scores the board
the grader actually saw, hand-of-ten and live intent included; the observed
reading is the one the verdict embeds.

**What "SURVIVES" means here, exactly:** no single line on the declared board
is worth more than twice the runner-up in the pilot's own scoring currency, so
the falsifier does not refuse the turn. It is not a claim that the turn is
good, interesting, or better than its twin, and it is not comparable between
two rows of the table — R213 F allows the reading only as a refusal.

## Why every seed is unpinned

The encounter is generated from the run seed, so a seed can only be
**discovered** by staging. Staging needs the live game, and the live game
needs the `STS2_MCP` bridge deployed into the game directory — which is not
installed on this machine right now (`<game>\mods\` holds `klee`,
`STS2AutoSlayMod` and `quick_fingers`, and no bridge), and which a worktree
may not install (`OPERATIONS.md`: from a worktree the one legal command is
`deploy_bridge.ps1 -BuildOnly`). So no turn in this slice has been staged and
no seed exists yet.

**The seed rule for whoever stages first:** within a group (A, B, C, D) the
first half staged rolls a seed, `stage` records it into that turn's
`packet.json` as `run_seed`, and **every other half of the group must be
staged with `--seed <that value>`**. Two halves on two seeds are two different
fights, and the pair has then measured the encounter instead of the card. Fill
the seed, staged and packet-sha columns above as each one lands.

**And the intent check is not optional here.** The declared boards all say the
enemy telegraphs an ATTACK, because defence is worth nothing against anything
else and what defence costs is the entire slice. If the seed's first fight
telegraphs a debuff or a buff instead — which is what happened to the worked
example, `kokomi-first-turn-example`, whose Shrinker Beetle telegraphed a
debuff — **re-roll and stage on another seed** rather than recording the
divergence. For this slice the intent is the question, not an incidental.

## Group boards

| group | energy | HP | Charge | enemies | alternatives in hand |
|---|---|---|---|---|---|
| A (Pearl Barrage) | 2 | 48/70 | 8 | one, 34 HP, attacks for 14 | Gorou opener (0, self-Exhausts), Send the Runner (0, Exhausts one), Coral Guard (1), All Streams Flow (1) |
| B (Shinobu) | 3 | 48/70 | 8 | two, 22 and 18 HP, both attacking | Coral Guard (1), Water's Edge (1), All Streams Flow (1) |
| C (Thoma) | 3 | 48/70 | 8 | one, 40 HP, attacks for 15 | Coral Guard (1), Water's Edge (1), All Streams Flow (1) |
| D (Itto) | 3 | 48/70 | 8 | one, 40 HP, attacks for 15 | Coral Guard (1), Water's Edge (1), All Streams Flow (1) |

Each file's own header says why its board is set that way. In short: group A
runs on **two** energy because three buys every card and a turn with no card
left over has no second line; groups B–D run on **three** because that is the
smallest budget on which the cost-3 priced shape is a hard choice rather than
a dead card. Group B carries two enemies because Shinobu's engine half is an
AoE, and on one body "damage all" and "damage one" are the same card.

## Running them

```sh
# no game needed, any checkout
.venv/Scripts/python -m understudy.staged_turn check
.venv/Scripts/python -m understudy.staged_turn closeness \
    understudy/turns/kokomi-slice-1/pearl-barrage-shipped.yaml

# the live half, from the art-bearing main checkout, attended
.venv/Scripts/python -m understudy.staged_turn stage \
    understudy/turns/kokomi-slice-1/pearl-barrage-shipped.yaml \
    --why "kokomi slice 1, arm 1, shipped half"
# then the twin, on the seed the line above recorded:
.venv/Scripts/python -m understudy.staged_turn stage \
    understudy/turns/kokomi-slice-1/pearl-barrage-turn.yaml \
    --why "kokomi slice 1, arm 1, whole-turn half" --seed <run_seed>
```

The seven prototype halves need a dev build first
(`klee-mod\build\deploy_proto.ps1`); the four shipped halves stage on the
release build as it stands. `OPERATIONS.md` carries both paths, and restoring
the release build afterwards.
