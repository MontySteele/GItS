# Kokomi slice 1 — the rows, the boards, and what is waiting on you

**2026-08-27. Branch `kokomi-slice-1`, from `main` at `461fa5a`.**
Authorised by R216. Everything below lives on the quarantined prototype
surface (`docs/prototype-surface.yaml`); **no shipped sheet row moved by one
character**, and under R215 B no number measured on a prototype row is
quotable in a packet, a register or a commit message. The one exception is the
decision-closeness reading, because it reads a *turn* and not a row.

**I designed these cards, so I am not allowed to say whether any of them is
good.** That is R213's first guard, and nothing in this document grades an
arm. What follows is what was built, why each board is set the way it is, and
what still needs a human.

---

## 1. The question this slice is asking

The playtest of 2026-08-26 found that every route in the game comes back to a
bigger damage number or a bigger Block number, and the diagnosis everyone
agreed on was **subsidised defence**: Companion cards hand you Block attached
to the play you already wanted to make, so the choice between attacking and
defending never actually happens. Waiting is safe. R213 E3 reopened this and
put the rule precisely: Companion Block is not banned — *unpriced* Block is.
Defence has to cost tempo, identity position, resource, or the loss of another
outcome.

So the hypothesis under test is:

> A turn holding the shipped form of one of these cards has no second
> plausible line, because nothing was traded. A turn holding a priced form
> does, because something was.

The slice does not settle that by argument. It builds both forms, puts them on
the same board, and lets the funnel ask.

---

## 2. The seven prototype rows, and how they will print

All seven are on `docs/prototype-surface.yaml`. They are compiled only into a
dev build; a shipped mod does not contain the classes at all, so there is no
id a normal game could be talked into granting.

### Arm 1 — what Pearl Barrage counts (R215 C)

The shipped card reads **the cost of the one card you chose to Exhaust**. Your
words on 2026-08-27 were: *"I thought it was tracking how many cards had been
exhausted that whole turn."* That is this row.

| | |
|---|---|
| id | `proto_pearl_barrage_turn` |
| name | **Tidal Barrage** |
| cost | 1, Attack, Uncommon |
| prints | *Exhaust 1 card from your hand. Deal `{CalculatedDamage}` damage, plus `{ExtraDamage}` per card **Exhausted** this turn.* |

Base 5 and per-3 are the shipped numbers, **deliberately unmoved**. The
counting basis is the question; if a number moved too, whatever the turn
showed could not be attributed to either change.

The card still Exhausts one card itself, and **that card is inside its own
count** — so on a turn with one rotation in it the two shapes land on the same
number, and only a turn that stacks rotations separates them.

### Arm 2 — the Block, or the other half, never both

Prune's shape. Same amounts, same cost, same element as the shipped card; the
only thing that moved is the word *and* becoming *or*. Defence costs an
**outcome**.

| id | name | cost | prints |
|---|---|---|---|
| `proto_shinobu_sanctifying_ring_either` | **Shinobu — Warding Ring** | 2, Skill | *Choose one: Deal 3 damage to ALL enemies \| Gain 4 Block.* |
| `proto_thoma_crimson_ooyoroi_either` | **Thoma — Blazing Ooyoroi** | 2, Attack | *Choose one: Deal 8 damage \| Gain 3 Block.* |
| `proto_itto_superlative_superstrength_either` | **Itto — Oni Rush** | 2, Attack | *Choose one: Deal 14 damage \| Gain 6 Block.* |

Shinobu's Electro and Thoma's Pyro still land on the attack half. Itto's
shipped card applies no element and neither does this one.

### Arm 3 — the Block, priced in the cost line

The shipped effects to the digit, and one more energy. Defence costs
**tempo**. You keep the whole card; it just competes for the turn instead of
riding along inside it.

| id | name | cost | prints |
|---|---|---|---|
| `proto_shinobu_sanctifying_ring_priced` | **Shinobu — Sanctifying Circle** | **3**, Skill | *Deal 3 damage to ALL enemies. Gain 4 Block.* |
| `proto_thoma_crimson_ooyoroi_priced` | **Thoma — Crimson Guard** | **3**, Attack | *Deal 8 damage. Gain 3 Block.* |
| `proto_itto_superlative_superstrength_priced` | **Itto — Superlative Guard** | **3**, Attack | *Deal 14 damage. Gain 6 Block.* |

---

## 3. The names, and what they lost to

Provisional names are mine under R212's ladder (R179), and these are all
provisional — they are deleted with the rows when the slice closes.

**What I did not do: call them "(Priced)" and "(Either)".** A blind QA grader
reads printed card titles. A title that names the experiment tells the grader
which arm they are holding, and the blind grade is the only thing standing
between us and grading our own homework. So every name is an ordinary card
name and says nothing about the arm.

The three alternatives I considered and dropped:

1. **Suffix the shipped name** — "Pearl Barrage (Whole-Turn Count)". Clearest
   for us, useless for the funnel, for the reason above.
2. **Reuse the shipped display name on both rows.** Would have made the pairs
   perfectly matched, but `give_card` matches on id *or exact title*, so two
   cards sharing a title makes every grant ambiguous.
3. **Numbered placeholders** — "Kokomi Prototype 1". Blind, but unreadable in
   a packet: the grader has to hold four cards in their head and one of them
   would have no name to hold it by.

The same reasoning drove the **turn ids** (`kokomi-slice1-t01` … `t11`), which
are printed into the packet and so say nothing about the arm either. The
filenames say it; `understudy/turns/kokomi-slice-1/MANIFEST.md` is the map.

---

## 4. The boards, and why each is set that way

Eleven turns in four matched groups. Within a group the files declare the
**same board** — HP, Block, energy, Charge, enemies, and the same alternatives
in hand — and differ in exactly one card. Anything else differing would let a
change in how the turn plays be blamed on the staging instead of the card.

Every board telegraphs an **attack**, because defence is worth nothing against
any other intent and what defence costs is the entire slice. Every board banks
**8 Charge**, so Kokomi's Charge reader is a live finisher — if it were not on
the table, spending the energy on Block would not be giving anything up.

**Group A — Pearl Barrage, two energy.** Hand: the card under test, Gorou's
0-cost opener (which Exhausts itself), Send the Runner (0 cost, Exhausts one
card you pick), Coral Guard, and All Streams Flow. Two free rotations means
the turn can put three cards in the pile without paying for any of them —
which is the *only* thing that separates the two counting bases. Two energy
rather than three because three buys every card on this board, and a turn with
nothing left over has no second line to be close to. At two, the last energy
goes to the Block or to the finisher.

**Groups B, C and D — the Companions, three energy.** Hand: the card under
test, Coral Guard (flat defence), Water's Edge (flat damage), All Streams Flow
(the Charge finisher). Three energy is the smallest budget where all three
shapes are real: the shipped card at 2 leaves a play spare, so the Block came
free; the *either* card at 2 leaves the same play but does one half, so the
Block cost an outcome; the *priced* card at 3 is the whole turn, so the Block
cost tempo. At two energy the cost-3 shape is not a hard choice, it is a dead
card, and a dead card is not an arm.

**Group B carries two enemies.** Shinobu's engine half is an AoE, and on a
single body "damage all" and "damage one" are the same card — the
mutually-exclusive arm would be asking its question about something that is
not on the board.

### The closeness reading

`staged_turn closeness` was run on all eleven declared boards. **All eleven
SURVIVE**: gaps 0.0096 to 0.2850 against a dominance threshold of 0.5, over 8
to 27 distinct lines. That means no line on any of these boards is worth more
than twice the runner-up in the pilot's own currency, so the falsifier refuses
none of them. It is **not** a claim that any turn is good, and the numbers are
not comparable between two rows — R213 F allows the reading only as a refusal.
Per-turn numbers are in the manifest and in `review/qa/<turn id>/closeness.json`.

---

## 5. What is staged, and what is waiting

**Nothing is staged.** Not one of the eleven, including the four shipped
halves.

Staging needs the live game, and the live game needs the `STS2_MCP` bridge
installed in the game directory. It is not there — `<game>\mods\` currently
holds `klee`, `STS2AutoSlayMod` and `quick_fingers`, and no bridge — and a
worktree is not allowed to install one (`OPERATIONS.md` permits
`deploy_bridge.ps1 -BuildOnly` from a worktree and nothing else). The harness
is also attended-only by standing rule, and nobody was attending.

So every seed in the manifest is unpinned and every row reads `staged:
pending`. The four shipped halves can be staged on the release build as it
stands (`0.2.1209`); the seven prototype halves need a dev build first.

**The seed rule, because it is the thing that will be got wrong once:** within
a group, the first half staged rolls a seed and `stage` records it; **every
other half of that group must then be staged with `--seed <that value>`**. Two
halves on two seeds are two different fights, and the pair has measured the
encounter instead of the card. And if the seed's first fight telegraphs
anything but an attack, **re-roll**. The worked example's Shrinker Beetle
telegraphed a debuff and that was recorded as a divergence; here the intent is
the question, so a wrong telegraph means a wrong board.

---

## 6. The dev deploy, and one thing that needs ratifying

`klee-mod\build\deploy_proto.ps1` is new. It is `deploy.ps1` plus three
things — it checks the prototype codegen is in sync first, it builds with the
prototype flag, and it marks the package version — and minus one: no handoff
zip, because a dev build is never given to a co-op peer.

**It runs the same `validate.ps1`, whole.** Every rule, the full test suite,
nothing skipped. A prototype build that skipped gates would prove nothing
about the cards it exists to try.

It is a **second script** rather than a switch on `deploy.ps1` because the
quarantine's own guard forbids the other shape: a test asserts that
`deploy.ps1` and `validate.ps1` never so much as mention the compile flag, and
a switch would have to name it. That test is untouched and still green.

### The thing for the next ruling — RATIFIED by R217 D (2026-08-28)

R214 ruled the version shape `MAJOR.AUTO`, with `+dirty` as semantic-version
build metadata. **This extends that use.** A dev package is stamped
`0.2.NNNN+proto`, or `+proto.dirty` when the tree is dirty — a second token on
the same channel.

The reason it needs one at all is that `deploy_proto.ps1` writes to the *same*
`mods\klee` directory the release path writes to. Without a mark on the
version string, "which build is installed right now?" has no answer anywhere
on screen, and the answer matters: one of them contains prototype classes and
one does not. The mark costs nothing — the game's parser ignores everything
after the `+`, so a marked package is still a valid version and still refuses
no dependent mod.

The gate is symmetric: a `+proto` package reaching the release path is refused
by name, and the dev path refuses a package that *lost* its mark.

**This is flagged, not assumed.** It is R214's channel being used for a build
shape R214 did not contemplate, and it belongs in the next slate. **R217 D
ratified it**, and the mark and its symmetric refusal are now in LAW beside
R214.

---

## 7. Register moves I think should be minted

I did not mint or close anything. My reading of what should be:

- **Nothing closes.** The slice is not run.
- **One BACKLOG row is worth minting:** *the prototype surface's blind-QA
  turns cannot be staged from a worktree, and the bridge is not installed.*
  Next action: install the bridge (`deploy_bridge.ps1`) on the main checkout,
  then stage the four shipped halves and record their seeds. Acceptance: four
  packets under `review/qa/` with `run_seed` recorded and an attack telegraph.
- **One item for the next slate, not a register row:** the R214 metadata
  extension in §6 — **RATIFIED by R217 D (2026-08-28)** and written into LAW's
  version-string clause.
- **`EB-164` is touched but not addressed.** Tidal Barrage's face prints a
  live per-unit rate beside a calculated number, which is the wording R215 C
  settled on for the exhaust-selection count — the same wording EB-164 says
  can be double-counted by a careful reader. I copied the ruled precedent
  rather than inventing a new one on a prototype row, and the row inherits
  whatever EB-164 decides.

---

## 8. What I could not do

- **Stage anything live** (§5): no bridge installed, worktree not allowed to
  install one, harness attended-only.
- **Discover seeds**, for the same reason. The declared boards are therefore
  the only reading that exists.
- **Run either deploy script.** A worktree has no `local.props`, no
  `game_ref/` and no art. `dotnet build` was run both ways and both succeed;
  the version-policy tests exercise the shipped PowerShell directly.
- **See a prototype card render.** Prototype rows have no art by design — art
  is commissioned when a slice is *accepted* and its rows move to a real
  sheet — so they will draw with no portrait. That is correct, not a defect.
