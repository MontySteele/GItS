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

## Results (2026-08-27, after the merge)

All eleven turns were staged live and graded blind. Every packet went to a
fresh grader (`opus-5-fresh`, a new agent per packet, the page inline, no
tools) and every one of the eleven **survives** the falsifier: each form
names a second line it seriously weighed, and each says a different intent
would have moved it. The forms and verdicts sit beside each packet under
`review/qa/kokomi-slice1-t01..t11/`; the ledger is `review/qa/ledger.tsv`.

| group | shipped half | prototype halves | seed | builds |
|---|---|---|---|---|
| A — Pearl Barrage counting basis | t01 SURVIVES | t02 SURVIVES | `HUMWKRKNCE` | 0.2.1209 / 0.2.1232+proto |
| B — Shinobu | t03 SURVIVES | t04 (either) SURVIVES · t05 (priced) SURVIVES | `NMQLUYZDLV` | same |
| C — Thoma | t06 SURVIVES | t07 (either) SURVIVES · t08 (priced) SURVIVES | `XVE3PVZEPT` | same |
| D — Itto | t09 SURVIVES | t10 (either) SURVIVES · t11 (priced) SURVIVES | `X1BQR3FU4G` | same |

Two things the record shows without rating anything. First, the observed
closeness reading is exactly 0.0000 on t07, t08, t10 and t11 — the pilot
scores its top two lines identically on those boards — while their shipped
twins read 0.0208 and 0.1217; a tie is a survival, not a refusal, but it is
a different shape of survival from the rest of the table. Second, group B's
live fight is three bodies with one attacking, not the two attackers the
declared board mirrors; every half of group B was staged on that same fight,
so the pair is matched, but the declared and observed boards are two
records there.

Nothing is owed from [USER] here: R217 A (2026-08-28) struck the cold
calibration play, so the `user` grader row stays empty by rule and the
ledger's down-weighting is dormant. The dev build `0.2.1232+proto` is still
the installed package — harmless for ordinary play, prototype rows being
off-pool — and `klee-mod\build\deploy.ps1` restores the release build
whenever one is wanted.

## The seat's grades and the pair read (2026-08-28)

R217 C made the independent seat a different model FAMILY from the author,
so every one of the eleven turns was graded a second time by
`codex-gpt-5.6-sol-fresh` (OpenAI, through `understudy/seat.py`), each form
blind, transcript-guarded, and beside the Opus form in
`review/qa/kokomi-slice1-*/`. The ledger holds both graders for all eleven.

| turn | half | Opus | GPT |
|---|---|---|---|
| t01 | A shipped | SURVIVES | SURVIVES |
| t02 | A prototype (Tidal Barrage) | SURVIVES | **REFUSED — `intent_insensitive`** |
| t03 / t04 / t05 | B shipped / either / priced | SURVIVES ×3 | SURVIVES ×3 |
| t06 / t07 / t08 | C shipped / either / priced | SURVIVES ×3 | SURVIVES ×3 |
| t09 / t10 / t11 | D shipped / either / priced | SURVIVES ×3 | SURVIVES ×3 |

**The one disagreement, t02.** Both graders took the same lethal line
(Gorou ×2, Send the Runner, Tidal Barrage, All Streams Flow into Nibbit).
GPT's fourth answer: *"No. This line deals enough damage to defeat Nibbit
before its intent resolves, so a different telegraphed action would not
have changed my play."* Opus's: *"Yes. The intent barely mattered for the
kill itself, but it decides the fallback. If Nibbit's HP had been high
enough that lethal was off the table…"* — a yes that changes the board to
get there. The refusal is recorded as the seat's verdict; the reviewer
below reads the disagreement the same way.

**The pair read.** The seat's reviewer role (same model, read-only,
everything inline) was handed all eleven packets and all twenty-two forms
and asked, per arm: was the card under test played or seriously weighed;
did the priced form change the KIND of choice; did the cost bind; any text
a grader tripped on; then RETURN / ADVANCE / ESCALATE. Its reply is
`review/qa/kokomi-slice-1-pair-review-codex-gpt-5.6-sol.md`, unedited. The
outcome is **RETURN on all seven arms**, and the reason is the same on
six of them: *the boards, not the cards*. Two Coral Guards, two free Gorou
attacks and an 8-Charge finisher already supplied the whole race-versus-
turtle choice, so the card under test was bypassed (B either/priced: neither
grader played or weighed Shinobu; C priced: dismissed *"by direct
arithmetic"*) or reproduced a choice the board already had (D either: *"a
real, felt cost"* but *"not a new kind of choice"*). Group A's board had
guaranteed lethal, which made both the alternative and the intent
non-binding. Two text findings ride along: Tidal Barrage does not say
whether the card it exhausts counts toward its own total, and the *either*
faces (*"Choose one: … | Gain 4 Block. Applies Electro"*) leave it unclear
whether the element applies after either mode.

**What RETURN means next, in the seat's own prescriptions:** re-stage the
same eleven cards on boards where the card under test is the pivot — remove
the redundant standalone Block (the Coral Guards), take Group A's enemy HP
off lethal, and set thresholds the priced package can cross (damage that
kills or Block that fully answers the telegraph) — on the same group seeds,
then grade again. No number on a shipped row moves; no shipped form is
graded; nothing here is a claim about fun.

## Round 2 (2026-08-28)

The seat returned all seven arms on *the boards, not the cards*, so round 2
re-staged the same eleven cards on rebuilt boards. **No printed number moved.**
The files are `understudy/turns/kokomi-slice-1-r2/`, the manifest there carries
the per-group arithmetic, and each file's header quotes the prescription it
executes.

**What changed, and it is three things.** (1) The hand is now exactly the
declared hand — `EB-165` built the dev door and closed, and `exact_hand: true`
empties the game's dealt hand to the bottom of the draw pile before the grants.
Round 1's packets carried ten cards where the files declared four or five, and
the pair read named those extra cards as the thing that supplied the whole
choice. (2) The redundant standalone Block is gone: groups B, C and D carry
none, so each card's Block half is the only Block on its board; group A keeps
exactly one and its file says why. (3) Thresholds are written on both halves —
enemy HP against the turn's own ceiling, player HP so the telegraph takes at
least a quarter of what is left.

All eleven staged live on the pinned round-1 group seeds, on one build
(`0.2.1248+proto`), and every seed was honoured. **The exact-hand door shows up
as a number:** the declared and observed closeness readings are now identical
on all eleven turns, to four decimal places and line for line, where in round 1
they disagreed on every turn.

### The verdicts

One grader this round, the R217 C independent seat (`codex-gpt-5.6-sol-fresh`,
blind, transcript-guarded, one fresh agent per packet).

| turn | half | verdict |
|---|---|---|
| t01 | A shipped | SURVIVES |
| t02 | A prototype (Tidal Barrage) | SURVIVES |
| t03 | B shipped | **REFUSED — `intent_insensitive`** |
| t04 | B either | **REFUSED — `intent_insensitive`** |
| t05 | B priced | SURVIVES |
| t06 | C shipped | **REFUSED — `intent_insensitive`** |
| t07 | C either | SURVIVES |
| t08 | C priced | **REFUSED — `intent_insensitive`** |
| t09 | D shipped | **REFUSED — `intent_insensitive`** |
| t10 | D either | **REFUSED — `intent_insensitive`** |
| t11 | D priced | **REFUSED — `intent_insensitive`** |

Seven refusals, all the same rule, and all with the same shape of reason in the
grader's own words: *"this line clears all three enemies this turn"* (t03),
*"the chosen line defeats Seapunk immediately"* (t06), *"this line kills the
only enemy"* (t09). **Three of the seven are shipped controls**, which is the
fact that matters: intent-insensitivity cannot be blamed on a prototype when
the shipped half on the same board answers "no" too. Two of those three
(`t06`, `t09`) refused on the misread the next section describes; `t03`
refused on a lethal line that was really there.

### Five of the seven refusals were bought with a face defect, and the game settled it

**Five of them** — `t06`, `t08`, `t09`, `t10`, `t11`, which is all of groups C
and D — count *All Streams Flow to the Sea* at **13** damage. The card deals
**9**: the sheet row is base 5 plus one per two Charge, and the printed face
already folds the scaler in, so a reader who adds the Charge bonus to the
printed number adds it twice. That is `EB-164` — a face that states its scaling
twice — and this round is the first time it has been seen to corrupt a blind
grade rather than merely confuse one.

Settled by the game and not by argument: `staged_turn execute` replayed the
group C grader's own three-attack line on its own seed and board, board check
MATCHES, **Seapunk 22 HP → 1 HP**. The line dealt 21, not 25. There was no
lethal line on group C, and by the same arithmetic none on group D.

**Group B's two refusals (`t03`, `t04`) are SOUND, and this section does not
cover them.** That board's attacker sat at 10 HP with no Block, and two 1-cost
attacks are Water's Edge 6 + All Streams **9** = 15 for two of the three
energy — a real lethal line at the card's TRUE value, not a phantom one. So
`t03` is a shipped control that refused on correct arithmetic, and **two**
shipped controls, `t06` and `t09`, refused on the misread. Round 3 removes B's
lethal line by giving that attacker 6 Block.

### The pair read

The seat's reviewer role was handed all eleven packets and all eleven forms and
verdicts and asked, per arm: was the card under test played or seriously
weighed; did the prototype form change the KIND of choice against its shipped
half; did the cost bind; any text a grader tripped on; then RETURN / ADVANCE /
ESCALATE. Its reply is
`review/qa/kokomi-slice-1-r2-pair-review-codex-gpt-5.6-sol.md`, unedited, with
one correction noted in the header rather than in the text: **the reviewer made
the same 13-for-9 reading the graders did**, and every "unconditional lethal"
in its reply rests on it.

| group | arm | outcome | the reviewer's one-line reason |
|---|---|---|---|
| A | counting basis | **ADVANCE** | *"Played and changed the turn from sacrifice-cost selection to Exhaust sequencing, with 5 Block genuinely surrendered."* |
| B | either | RETURN | *"Played, but area damage enabled a full clear, so giving up 4 Block cost nothing."* |
| B | priced | **ADVANCE** | *"The extra energy forced an all-in line and concretely cost the kill on the remaining enemy."* |
| C | either | RETURN | *"The apparent trade rests on treating a 13-damage card as 9; actual chosen damage was lethal."* |
| C | priced | RETURN | *"The tempo restriction was visible, but an unconditional lethal alternative made the card one-sided."* |
| D | either | RETURN | *"Damage mode produced lethal, so surrendering the 6-Block outcome had no felt consequence."* |
| D | priced | RETURN | *"The extra energy excluded follow-ups, but the competing cheap-card line simply ended combat."* |

Two arms ADVANCE where round 1 advanced none. On the boards it did read
correctly, the reviewer's readings of card exposure are unambiguous: **every
one of the seven prototype cards was either played or named as the serious
alternative**, where round 1 recorded *"Neither grader played or seriously
weighed the card"* on two of them.

### What the outcome means next

**Two arms advance and five return, and the five returns share one cause with
each other and with the round's seven refusals.** The reviewer's own summary of
the refusals is that they *"primarily diagnose the boards and, secondarily, the
funnel's fourth question — not the cards"*, and it reads the fourth question as
*"an intent-sensitivity gate, not a general exposure or cost-binding
measure"* — a refusal invalidates a turn's advancement evidence and does not
mean the card went unseen.

What a round 3 would have to settle first is not a board at all: **`EB-164`
now has to be fixed before another round is graded.** Four of eleven graders
and the reviewer read one shipped face 44% high, and on three of the four
groups that misreading manufactured a lethal line that the game does not
have — so the boards were returned for a property they did not possess. Its
`BACKLOG` row carries that evidence now.

Nothing here rates a card, and nothing here is a ship approval: a seat's
SURVIVES and a seat's ADVANCE are both "not yet falsified" (R217 G).

## Round 3 (2026-08-28)

Round 2's own finding blocked it: `EB-164`, a face that printed a number with
its scaler already folded in and then asserted the scaling again beneath it.
Round 3 is the same eleven cards, on round 2's boards, against faces that state
a scaling once — plus one new protocol step that would have caught the defect
at grade time. Files: `understudy/turns/kokomi-slice-1-r3/`, manifest there.
Build `0.2.1252+proto`. **No printed card number moved.**

### What changed, and only this

**The faces.** One rule for the whole roster, in `gen_klee_cards.py`'s
docstring: where the printed number already carries the rider, the source is
named in that number's own sentence and nothing else asserts it; where the
count does not exist until the card resolves, the per-unit rate is printed
beside the number (R215 C, untouched). Eighteen faces re-worded, seventeen
generated and one hand-written. The card at the centre of round 2's misread now
reads, verbatim from the live packet:

> All Streams Flow to the Sea — *Deal 9 damage, already including Charge.
> Applies Hydro.*

**Two boards, both to remove a lethal line, both checked with the CORRECT card
values.** The manifest states the arithmetic per group rather than asserting
it.

* **Group B's attacker gets 6 Block.** At 10 HP with none it died to Water's
  Edge 6 + All Streams 9 = 15 for two of three energy — a real lethal line at
  the true value, which is why round 2's two group-B refusals were sound. Six
  Block is an effective 16 against a ceiling of 15, so the best line leaves it
  on 1. Block and not HP because `set_hp` clamps at a creature's maximum and
  this body generates at 10/10.
* **Group D is on a new seed.** Round 2 could not land its defensive threshold:
  the attacker telegraphed 8 against a 6-Block half, and no verb writes an
  intent. Fourteen rolls, all recorded in the manifest, looking for one body
  telegraphing at most 6; `21RD94VY60` (Fuzzy Wurm Crawler, attacks for 4) is
  the first that qualifies, and all three group-D halves stage on it. **No roll
  in fourteen produced a 5 or a 6** — the one-body Act-1 telegraphs that
  appeared were 4, 8, 11 and 12 — so the Block half now fully answers the hit
  with 2 of its 6 spare rather than three quarters of it.

Groups A and C are round 2's boards on round 2's seeds, unchanged.

### The new protocol step: REPLAY

After grading and before the pair read, every graded line is replayed on the
live game on its own pinned seed and board, and the grader's stated damage or
kill expectation is set against what the board actually did. A form whose
refusal or survival rests on an arithmetic claim the game contradicts is
flagged `misread` in the table below — **recorded, never re-graded**. This is
the check that would have caught `EB-164` in round 2 at grade time instead of
at pair-read time.

### Verdicts, and the replay beside each

Grader: the R217 C independent seat, blind and transcript-guarded, one fresh
agent per packet, `codex-gpt-5.6-sol-fresh`. **7 SURVIVES / 4 REFUSED**, where
round 2 was 4 / 7.

| turn | half | verdict | replay: the board's answer to the form's arithmetic |
|---|---|---|---|
| t01 | A shipped | SURVIVES | **confirms** — Nibbit 38 → 23, the 15 damage q1 claims; Block 0 → 5 |
| t02 | A proto (counting) | SURVIVES | **confirms** — Nibbit 38 → 21, the 6 + 11 the form's line adds up to with two cards Exhausted this turn; Block 0 → 5. Replayed through the Exhaust prompt on `EB-170`'s answer |
| t03 | B shipped | **REFUSED — `intent_insensitive`** | **confirms** — both Leaf Slimes died; the attacker went 10 HP behind 6 Block → 4 HP, 0 Block; Block 0 → 4. It lived and its telegraph landed |
| t04 | B proto (either) | SURVIVES | **confirms** — both Leaf Slimes died and Twig Slime (S) went 10 HP behind 6 Block → 4 HP, 0 Block, exactly the "4 HP after Block" q1 claims. Replayed through the mode choice on `EB-170`'s answer |
| t05 | B proto (priced) | **REFUSED — `intent_insensitive`** | **confirms**, including the part a reader would doubt — the attacker took ZERO HP damage (10 → 10), its Block 6 → 3; player Block 0 → 4 |
| t06 | C shipped | SURVIVES | **confirms** — Seapunk 22 → 1, exactly the 21 q1 claims |
| t07 | C proto (either) | **REFUSED — `intent_insensitive`** | **confirms** — Seapunk 22 → 1. The form's claim that no line here can defeat it this turn is TRUE |
| t08 | C proto (priced) | SURVIVES | **confirms** — Seapunk 22 → 1 |
| t09 | D shipped | **REFUSED — `intent_insensitive`** | **confirms** — Fuzzy Wurm Crawler 24 → 1 (23 damage) AND Block 0 → 6, in one line |
| t10 | D proto (either) | SURVIVES | **confirms** — Fuzzy Wurm Crawler 24 → 1, the 14 + 9 q1 claims; Block 0 → 0, the damage mode taken. Replayed through the mode choice on `EB-170`'s answer |
| t11 | D proto (priced) | SURVIVES | **confirms** — 24 → 3 (21 damage), Block 0 → 0 |

**No turn was flagged `misread`, and all eleven replays are now complete.**
Eight completed on the day and every one confirmed the grader's arithmetic to
the hit point. The other three — `t02`, `t04`, `t10` — stopped for one shared
mechanical reason: each line passes through a modal card-selection or
mode-choice prompt `staged_turn execute` could not answer. That was a real gap
in the tool rather than a disagreement about a number, and it is now closed
(`EB-170`): a play in `chosen_line` may state `exhaust` / `choose` in the
printed vocabulary, an unanswered prompt STOPS the replay by name rather than
being guessed at, and the three forms above — written before those keys existed
— were replayed on 2026-08-28 with the choice each grader's own q1 prose names,
supplied as an operator `--answer` and logged as `source: "operator"` in every
record. **All three confirm the form**, so the round's replay column now reads
eleven of eleven and none of them a contradiction. The pair read below was
written when three cells said *incomplete*; its reasoning is unchanged by three
confirmations, and it is left as published (R101b).

The four refusals in the grader's own words:

* `t03` — *"Given only this hand and board, the same line efficiently removes
  both 3-HP enemies, uses the strongest remaining hit on Twig Slime (S), and
  adds Block, so a different telegraphed intent would not have changed it."*
* `t05` — *"With both Leaf Slimes at 3 HP, the all-enemy hit removes both for
  one play, and its Block is useful against the shown attack without costing
  those removals."*
* `t07` — *"From the printed information, the three one-cost attacks still
  produce the highest known damage for the available energy, and no listed line
  can defeat Seapunk this turn."*
* `t09` — *"With only the printed effects available, this line gives the
  highest damage while also gaining Block, so a different telegraphed intent
  would not have changed my play."*

Two of the four are shipped controls (`t03`, `t09`), and `t09`'s reason is the
slice's own hypothesis stated by a blind reader: the shipped card gives the
most damage **and** the Block in one play, so the telegraph cannot matter.

### The pair read

Same shape as round 2 — all eleven packets, forms and verdicts inline — with
the replay post-state added beside each form and the three incompletes named.
Reply, unedited:
`review/qa/kokomi-slice-1-r3-pair-review-codex-gpt-5.6-sol.md`; prompt kept at
`review/qa/kokomi-slice-1-r3-review-prompt.txt`, sha256
`c2466b75e85f5ad34e4dde00d40246dfed43d781223999cdcd21c6f3a189dc87`. **No
correction is attached this round**, where round 2's read needed one.

| turn | arm | outcome | the reviewer's one-line reason |
|---|---|---|---|
| t02 | A counting basis | **ADVANCE** | *"Played; whole-turn counting moved the scaling attack into the defended line, while Coral Guard explicitly cost nine damage."* |
| t04 | B either | **ADVANCE** | *"Played in damage mode; unlike shipped, killing both Leaf Slimes required giving up four Block and taking the attack."* |
| t05 | B priced | RETURN | *"Played, but the bundled AOE removal plus Block remained intent-insensitive; the extra cost removed only a follow-up."* |
| t07 | C either | RETURN | *"Seriously weighed, but Block mode sacrificed twelve damage for three Block and never became competitive on this board."* |
| t08 | C priced | **ADVANCE** | *"Seriously weighed; pricing Block into the cost line created an explicit 13-damage defensive price."* |
| t10 | D either | **ADVANCE** | *"Played in damage mode; the prototype forced a clean choice between 14 damage and six Block."* |
| t11 | D priced | **ADVANCE** | *"Seriously weighed; paying for six Block cost seven damage and the entire three-energy turn."* |

**Five ADVANCE, two RETURN, no ESCALATE** — against round 2's two ADVANCE and
five RETURN, and round 1's seven RETURN. The reviewer's own summary: *"mutually
exclusive modes work on the Shinobu and Itto boards but need a better Thoma
test. Cost-line pricing works for Thoma and Itto, while Shinobu's multi-enemy
removal remains strong enough to carry the Block without an intent-dependent
decision."* Its opening line is the reason the round is readable at all:
*"None warrants ESCALATE: every completed replay confirms the form, and the
three incomplete replays are mechanically untested rather than contradictory."*

### What the outcome means next

Both of R213 E's shapes for pricing Companion defence now have a majority of
their arms advancing on boards a blind reader and an independent reviewer both
read correctly. The two RETURNs are specific and each names its own repair in
the reviewer's words: Thoma's **either** shape needs *"a stronger or more
discriminating board"* — its Block mode lost by twelve damage rather than
losing a decision — and Shinobu's **priced** shape needs a board where the
multi-enemy removal does not carry the Block for free, since *"paying for Block
did not compete with the card's decisive two-enemy removal."*

The refusals still cluster on the same property, and round 3 sharpens what it
is. Two of the four are shipped halves whose single best line delivers maximum
damage AND the Block together; that is not a board defect and it is not a
grading artifact — it is the subsidy the slice exists to price, showing up as a
turn where the telegraph cannot matter.

Nothing here rates a card, and nothing here is a ship approval: a seat's
SURVIVES and a seat's ADVANCE are both "not yet falsified" (R217 G). What a
round 4 would carry, if one runs, is the two named board repairs — `EB-170` is
done, so a modal line replays rather than being left untested, and `EB-169`'s
preflight now refuses a board carrying a card with an open face defect before
the round is staged at all.

## Round 4 (2026-08-29)

Round 3 RETURNED two arms and named a repair for each. Round 4 is those two
repairs and nothing else: **the two returned arms and their shipped controls, on
repaired boards, with no printed card number moved by one character.** The other
two groups are not touched and the five arms that ADVANCED are not re-run. Files:
`understudy/turns/kokomi-slice-1-r4/`, manifest there. Build `0.2.1293+proto`.

### What changed, and only this

**Group C — one card leaves the hand.** Round 3's group C held four cards against
three energy: the card under test plus TWO Water's Edge plus All Streams Flow.
The three 1-cost attacks alone came to 21 damage, so the turn had a complete line
that never touched the card, and the Block mode was not losing to the card's own
other mode — it was losing to the rest of the hand. That is what *"sacrificed
twelve damage"* was measuring. One Water's Edge is removed; every line worth
playing now goes through the card, and the two modes sit **8 damage apart**
rather than twelve. Two consequences follow: the enemy goes to 24 HP, above the
17 the board can now produce, so no line is lethal; and the player goes to 14/70,
so the three Block is a real share of what is left rather than a rounding error.

**Group B — one number moves.** Round 3's group B carried two bodies at 3 HP,
which is the all-enemy hit's own number, so the card removed both whatever else
was true and its Block rode in free. A grader answering "a different telegraph
would not have changed it" was reading the board correctly. **The two
non-attacking bodies go from 3 HP to 6.** Three damage now removes nothing, so
the card must be bought for its Block; the removal is still available, just not
from this card — Water's Edge kills one small body and All Streams Flow kills the
other, for two energy, and choosing between that and the card is a choice about
the incoming attack.

### The thing this round found out the hard way: a seed is only reproducible within one game build

Round 3 ran on game **v0.107.1**. `R218` ported the mod and moved the pin to
**v0.111.0**, and the encounter generator moved with the game. Re-staging round
3's two seeds on the new build produced two DIFFERENT fights:

* Group C's `XVE3PVZEPT` gave Seapunk 22/44 attacking for 11 in round 3, and here
  gives **Nibbit 24/45 attacking for 12**. One body, an attack telegraphed, and
  the HP the file writes lands — the board is still the board this round
  designed, so group C keeps the seed and its mirror is re-declared to the body
  that appeared.
* Group B's `NMQLUYZDLV` gave three slimes in round 3 and here gives **one
  Shrinker Beetle telegraphing a debuff**. No second body, no third, no attack.
  Group B was re-rolled: **sixteen rolls**, the first fifteen one or two bodies,
  and roll sixteen `R7W86HG7WHUD` the first three-body fight — Twig Slime (S)
  9/9 attacking for 4, Leaf Slime (M) handing out two Status cards, Leaf Slime
  (S) attacking for 3.

One number moved because of that roll, and the manifest states it rather than
burying it: round 3's attacker sat at 10 HP behind 6 Block, an effective 16
against a single-target ceiling of 15. This seed's attacker generates at 9/9 and
`set_hp` clamps at a creature's maximum, so **nine behind eight** is the
arithmetic that reaches the same property — effective 17 against the same ceiling
of 15. The property is identical; only the numbers reaching it moved.

`R95` already says live numbers are not comparable across a game build. This adds
the ENCOUNTER to that list, which is worth writing down because a pinned seed
looks like it survived a port and does not.

### Closeness

All four SURVIVE, declared and observed, and the two readings are identical:
`t01` gap 0.1345, `t02` 0.1138, `t03` 0.1224, `t04` 0.0452, against
`DOMINANCE_GAP` 0.5. A refusal that did not fire, and never a rating (R213 F).

### Verdicts, and the replay beside each

**TWO graders on every turn this round**, where round 3 had one: a fresh Claude
per packet (`opus-5-fresh`, one agent, one turn, never reused) and the R217 C
independent seat (`codex-gpt-5.6-sol-fresh`). **Eight forms, 8 SURVIVES, 0
REFUSED** — against round 3's 7/4 and round 2's 4/7 on eleven.

| turn | half | grader | verdict | replay: the board's answer |
|---|---|---|---|---|
| `t01` | C shipped | Claude | SURVIVES | **flagged** — form claims 17, board dealt **21** (Nibbit 24 → 3); Block 0 → 3 |
| `t01` | C shipped | seat | SURVIVES | **flagged** — same 21, same reason |
| `t02` | C proto (either) | Claude | SURVIVES | **flagged** — took the DAMAGE mode; form claims 17, board dealt 21 (24 → 3). The mode choice itself replayed exactly as written |
| `t02` | C proto (either) | seat | SURVIVES | **INCOMPLETE** — took the BLOCK mode and the game refused the play. See below |
| `t03` | B shipped | Claude | SURVIVES | **confirms** — both Leaf Slimes dead, Twig Slime untouched at 9 behind 8 Block |
| `t03` | B shipped | seat | SURVIVES | **confirms** — identical |
| `t04` | B proto (priced) | Claude | SURVIVES | **confirms** — both Leaf Slimes dead, Twig Slime untouched; the card unplayed at 3 energy |
| `t04` | B proto (priced) | seat | SURVIVES | **confirms** — identical |

**The three flags are one fact and it does not move the comparison.** On group C
the board dealt 21 where every form said 17. The extra four is an **elemental
reaction** between the Pyro the companion applies and the Hydro that follows it.
One grader guessed at exactly that and declined to count it — *"if the Pyro it
applies interacts with the Hydro that follows, the order costs me nothing and
might gain something — I am not counting on that, the 17 is all printed
numbers."* The reaction fires on the shipped half and the prototype half alike,
so the pair still differs in one card. It is recorded because a form's arithmetic
and the board's answer disagreed, which is what the flag is for.

**The one incomplete replay is a DEFECT, and it is the round's sharpest find.**
The seat took the Block half of the modal — which gains Block and has no target —
and wrote no target, correctly, from the printed face. The game refused the play:
*"Card requires a target. Provide 'target' with an entity_id."* The card is typed
as an **Attack**, so the game demands a target even on the mode that attacks
nothing. The grader's line is mechanically untested rather than contradicted, and
the defect is `EB-184`.

### The pair read

Same shape as round 3, with both graders' forms and the replay post-state inline.
Reply unedited: `review/qa/kokomi-slice-1-r4-pair-review-codex-gpt-5.6-sol.md`;
prompt at `review/qa/kokomi-slice-1-r4-review-prompt.txt`, sha256
`21633739efddb73e1bf79ed381f25f8dbc9cb480683a4a0d405f9895e17375ae`. The reviewer
was told what round 3 had asked for, and asked a fifth question this round: **did
the repair work?**

| turn | arm | outcome | the reviewer's one-line reason |
|---|---|---|---|
| `t02` | C either | RETURN | *"Return the arm for an implementation repair, not a board redesign: the game incorrectly demands a target for the targetless Block mode, so the grader's defensive line could not be mechanically replayed."* |
| `t04` | B priced | **ADVANCE** | *"The repaired board isolated the intended pricing question and showed a concrete change from bundled defence-plus-follow-up to an all-in defensive turn."* |

**Both repairs are reported to have worked**, which is the answer round 4 was run
to get:

* Group C — *"Yes. Removing the routing attack and lowering HP made both modes
  credible enough to split the graders, directly correcting round 3's
  noncompetitive Block mode."* The two graders did split: one took the damage
  mode, the other took Block.
* Group B — *"Yes. Raising the bodies to 6 HP removed the AOE's decisive-removal
  role: it killed nothing, so considering the prototype meant considering whether
  4 Block justified abandoning the board clear."*

The reviewer's closing, verbatim: *"Round 4 supports both intended decision
shapes: exclusivity created a genuinely contested mode choice, and added price
converted defence into a distinct turn-level commitment. Nothing warrants
ESCALATE: Pair 1's divergent choices demonstrate closeness rather than an
irreconcilable contradiction, while its failed replay is a specific mechanical
defect that must be fixed before advancement."*

### What the outcome means next

**The slice's tally across four rounds is now six ADVANCE and one open RETURN**,
and the one RETURN is not a design finding at all — it is `EB-184`, an
implementation defect with a named fix, and the reviewer said so in as many
words. Group C's arm was returned for the defect, not for the board; the board it
was returned for in round 3 is reported repaired.

Nothing here rates a card, and nothing here is ship approval: a seat's SURVIVES
and a seat's ADVANCE are both "not yet falsified" (R217 G). What a round 5 would
carry, if one runs, is one turn: `EB-184` fixed, and group C's `either` arm
re-staged on the same board so the Block-mode line finally replays.

## Whole-fight blind play (`KOKOMI-SLICE1-WF`) — registration, DRAFTED before any run

**DRAFTED 2026-08-30. Not run, not countersigned.** Under R212(2) the slate is
Claude's to draft from written design intent and commit DRAFTED before any seed
is spent; [USER] countersigns it in batch, or vetoes within five days. Nothing
below is staged: **no board is staged, no seed is pinned, no Codex call is
spent, and no fight has been played.** `KURAGEMEM002` and `KURAGEMEM003` stay
UNSPENT — they are the memory kit's seeds, not this slate's, and this slate
pins none.

> **COUNTERSIGNED (R227, 2026-08-30): `KOKOMI-SLICE1-WF` is SIGNED**, in the
> batch of three, at PICK 3 option (1) — none vetoed. Signed once and never
> re-signed (R212, EXPERIMENTS *Countersign once*). **Two of the three
> sequencing preconditions below are now DISCHARGED:** `M67` is RULED at
> option (1) (R227), so the Kokomi prototype surface loses slice 2's four rows
> in this same sitting and no fight here is staged twice; and
> `KURAGEMEM002`'s rerun has RUN and been GRADED (2026-08-30, `P3` ADVANCE).
> **`EB-184` is still OPEN and still precedes `F3`, and only `F3`** — the
> Attack-typed `choose_one` target demand is unfixed, so `WF6` cannot be
> answered for Itto — Oni Rush until it lands. `F1` and `F2` are unblocked.

**Why it exists.** Six of slice 1's seven arms read ADVANCE across four rounds,
and the decision inventory of 2026-08-30 found that those six results feed
**nothing registered**. They land only on the accept-to-sheet signoff — the
prototype surface's own deletion rule, *"once a slice is ACCEPTED or REJECTED,
its rows LEAVE this surface"* (`docs/prototype-surface.yaml` header, R213 B),
under which an accepted row is re-authored onto a real sheet with its numbers
ruled, its stamp bumped and its art commissioned. That is a one-way door with
no measurement in front of it. This registration puts one in front of it, and
it is the same automatic gate slice 1's own *what the outcome means next*
paragraphs assume without ever registering: an ADVANCE is *"not yet
falsified"* (R217 G), and what has not been asked yet is whether the shape
survives a whole fight.

### What a whole fight can ask that a staged turn structurally cannot

Every one of slice 1's four rounds read a SINGLE staged turn per arm, and three
things about these arms are invisible on one:

1. **Cadence.** Whether the priced or exclusive shape produces its decision
   more than once in a fight, or once and then never again as the deck opens
   up. Arm 1's whole-turn count is a *sequencing* question by construction —
   it separates from the shipped count only on turns that stack rotations, and
   a staged turn holds exactly the rotations it was dealt.
2. **The arm's play share.** A staged board puts the card in a four-card hand;
   a fight decides how often the row is reached and played at all against a
   whole deck. Round 1's *"neither grader played or seriously weighed the
   card"* was a board finding; the same sentence about a fight would be an
   arm finding.
3. **The Muster/memory interaction**, which did not exist when the boards were
   set. Arms 2 and 3 are Companion rows, and under `C.KURAGE_MEMORY` a Muster
   creates a memory and a Mustered Companion costs one less — so the kit hands
   arm 3's cost-line price a discount the staged boards never applied to it,
   and hands arm 2's exclusive modes a 0-energy replay of whichever mode was
   taken. Neither is reachable on one turn.

### The six arms, and what is NOT in this slate

| # | arm | row | printed shape | the ADVANCE read this slate drafts from |
|---|---|---|---|---|
| A | counting basis | `proto_pearl_barrage_turn` — **Tidal Barrage** (1, Attack) | base 5, +3 per card Exhausted **this turn** | r2: *"changed the turn from sacrifice-cost selection to Exhaust sequencing, with 5 Block genuinely surrendered"*; r3: *"whole-turn counting moved the scaling attack into the defended line, while Coral Guard explicitly cost nine damage."* |
| B-e | exclusive modes | `proto_shinobu_sanctifying_ring_either` — **Shinobu — Warding Ring** (2, Skill) | 3 to ALL **or** 4 Block | r3: *"Played in damage mode; unlike shipped, killing both Leaf Slimes required giving up four Block and taking the attack."* |
| B-p | cost-line price | `proto_shinobu_sanctifying_ring_priced` — **Shinobu — Sanctifying Circle** (3, Skill) | 3 to ALL **and** 4 Block, at 3 energy | r4: *"The repaired board isolated the intended pricing question and showed a concrete change from bundled defence-plus-follow-up to an all-in defensive turn."* |
| C-p | cost-line price | `proto_thoma_crimson_ooyoroi_priced` — **Thoma — Crimson Guard** (3, Attack) | 8 **and** 3 Block, at 3 energy | r3: *"Seriously weighed; pricing Block into the cost line created an explicit 13-damage defensive price."* |
| D-e | exclusive modes | `proto_itto_superlative_superstrength_either` — **Itto — Oni Rush** (2, Attack) | 14 **or** 6 Block | r3: *"Played in damage mode; the prototype forced a clean choice between 14 damage and six Block."* |
| D-p | cost-line price | `proto_itto_superlative_superstrength_priced` — **Itto — Superlative Guard** (3, Attack) | 14 **and** 6 Block, at 3 energy | r3: *"Seriously weighed; paying for six Block cost seven damage and the entire three-energy turn."* |

**NOT in this slate: `proto_thoma_crimson_ooyoroi_either` — Thoma — Blazing
Ooyoroi.** It is slice 1's one open RETURN, returned in round 4 on `EB-184`
(*"the game incorrectly demands a target for the targetless Block mode"*) — an
implementation defect with a named fix, not a design finding. It re-enters at
round 5, not here.

**None of the six is Charge-PRICED, so none falls under `M67`'s consequence.**
Checked row by row against `docs/prototype-surface.yaml`: the only `spend_charge`
rows on the surface are slice 2's four. Arm A COUNTS Exhausts — which is what
accrues Charge — but prints no Charge price and reads no bank; arms 2 and 3 are
priced in outcome and in energy. The signed Charge clause (R226) touches
none of them. `M67` still sequences this slate, for the reason under
*Sequencing* below, but it deletes none of it.

### The unit, the fights, and the budget

**The unit is ONE COMPLETE FIGHT**, as it is for `KLEESPARK-W1` (§12.1 of
`review/active/klee-sparks-2026-08-29.md`) — the first Monster room of a live
Act-1 Kokomi run, played end to end by the Codex seat through
`understudy.blindplay session`, with the arm granted into the starting deck by
`understudy.embark --arm`. The screens before the first Monster room are driven
by the operator with `blindplay act`, at zero Codex cost; the seat sees its
first page at the combat screen.

**Codex budget: 30 calls per fight, enforced in the driver and not trusted to
the fight's length** — `--max-actions 24`, `--max-refusals 2`, so the worst case
is 24 command calls + 2 refusals + 1 fight record + 1 run record = **28**. Three
fights is a **90-call ceiling**, which is why they are three sittings and not
one; pace them against the seat's own rate-limit window (`EB-227`).

Three fights, because three groups of arms ask three different questions and a
fight that granted all six rows at once could attribute nothing:

| fight | rows granted | the arms it asks about |
|---|---|---|
| **F1** | Tidal Barrage, one copy | A |
| **F2** | Shinobu — Sanctifying Circle, Thoma — Crimson Guard, Itto — Superlative Guard, one copy each | B-p, C-p, D-p |
| **F3** | Shinobu — Warding Ring, Itto — Oni Rush, one copy each | B-e, D-e |

The three priced rows ride ONE fight together deliberately: they are the same
question at three prices, and a hand that can hold two of them at once is the
only way to see whether the 3-energy price competes with itself. The two
`either` rows ride one fight for the mirror reason. Arm A rides alone because
its question is about the turn's own Exhaust sequence, and any second prototype
in the deck adds Exhaust fodder the shipped deck does not have.

### The slate — eight slots, mechanical falsifiers

Every falsifier is computed from artefacts the run writes by itself: the
per-turn `thinking` sentences in `turn-*/reply.json`, the rendered observations
in `turn-*/prompt.md`, and the command rows of `transcript.jsonl`. **No grade
reads a judgement, and no falsifier carries a card number out of this packet** —
R213 B forbids quoting a number measured on a prototype row, so every threshold
below counts PLAYS, TURNS or SENTENCES.

#### Arm A — Tidal Barrage (fight F1)

| # | slot | prediction | falsifier | the decision the outcome changes |
|---|---|---|---|---|
| `WF1` | Does whole-turn counting produce **sequencing** across a fight, and not only on a board set to reward it? | **YES, on ≥ 2 combat turns.** | Count combat turns whose `thinking` names playing an Exhaust source BEFORE Tidal Barrage, or names the running Exhaust count as a reason to order the turn. **≥ 2 = PREDICTED, 1 = SPLIT, 0 = MISS.** | PREDICTED: arm A is an ADVANCE-to-sheet candidate and its re-author is unblocked. SPLIT: the shape is real but rare, and a sheet row needs a second Exhaust source in the starter before it is worth a slot — a design item, not a delete. MISS: the two counting bases are indistinguishable in play, R215 C's shipped basis STANDS, and the row is deleted under the surface's deletion rule. |
| `WF2` | Does a **stacked-rotation turn** ever actually happen in a fight? | **YES, ≥ 1 resolution at an Exhaust count ≥ 2.** | Count successful `play` commands naming Tidal Barrage whose observation shows a damage figure above the base rung — i.e. the turn held ≥ 2 Exhausts at resolution, the card's own included. **≥ 1 = PREDICTED, 0 = MISS.** No SPLIT: it is a yes/no. | MISS makes `WF1` unreadable rather than negative — the two counting bases land on the same number whenever a turn holds exactly one rotation (§2, arm 1), so a fight with no stacked turn asked the question and had no board to ask it on. That is an UNREACHED slot under R221 B's rule, and it escalates to *rerun F1 on a deck carrying a second rotation source*, not to a verdict. |

#### Arms B-p, C-p, D-p — the cost-line price (fight F2)

| # | slot | prediction | falsifier | the decision the outcome changes |
|---|---|---|---|---|
| `WF3` | Does 3 energy **bind** across a fight — is a priced row ever left in hand because the turn bought two cheaper cards instead? | **YES, on ≥ 2 turns.** | Count turns ended with `end turn` while the hand held a priced row the turn's starting energy could have paid for alone. **≥ 2 = PREDICTED, 1 = SPLIT, 0 = MISS.** | PREDICTED: all three priced arms are ADVANCE-to-sheet candidates together — the shape, not any individual number, is what carried. SPLIT: the price binds but thinly; the arms advance and the re-author carries an explicit note that the 3-energy rung is the whole mechanism. MISS: defence is still riding along, R213 E3's diagnosis is unaddressed by this shape, and the three priced rows RETURN to a staged round on a board built out of competing 1-costs. |
| `WF4` | Is the price **named** as a trade, or only paid? | **YES, on ≥ 3 combat turns.** | Count combat turns whose `thinking` names a priced row AND either a second card it was played instead of, or an explicit decision to forgo the turn's other line. **≥ 3 = PREDICTED, 1–2 = SPLIT, 0 = MISS.** | A `WF3` PREDICTED beside a `WF4` MISS is the arm's own escalation: the price binds mechanically and is invisible to the player, which is a LEGIBILITY defect (the `EB-220` badge family), filed to BACKLOG rather than returning the design. Both PREDICTED is the strongest ADVANCE-to-sheet reading this funnel can produce. |
| `WF5` | Does the kit's **Muster discount defuse the price**? | **NO — fewer than half of the priced rows' plays are at a discount.** | Of the successful `play` commands naming a priced row, count those whose observation shows a cost below the printed 3 (a Mustered Companion costs one less). **< 50% = PREDICTED, 50–75% = SPLIT, > 75% = MISS.** | MISS: the cost-line price is a price the kit routinely refunds, and the arm cannot advance to a sheet at 3 until the Muster discount and the price are reconciled — a design call for [USER], minted as a QUEUE row, NOT a delete. SPLIT: advance with the interaction named in the re-author. This slot is the reason the flag is ON, and it is stated as a contamination below. |

#### Arms B-e, D-e — exclusive modes (fight F3)

| # | slot | prediction | falsifier | the decision the outcome changes |
|---|---|---|---|---|
| `WF6` | Is the **Block mode ever taken** in live play, or is exclusivity a decision only a set board creates? | **YES, ≥ 1 Block-mode play across the fight.** | Count successful `play` commands on a granted `either` row that select the Block mode. **≥ 1 per row = PREDICTED, ≥ 1 across the two = SPLIT, 0 = MISS.** | MISS: the exclusive shape reduces to a strictly worse attack in play and the two `either` rows RETURN — a mode that is never the answer is not an option. PREDICTED on both rows makes arm 2 an ADVANCE-to-sheet candidate whole. |
| `WF7` | Is the **forgone mode** named as the cost? | **YES, on ≥ 2 combat turns.** | Count combat turns whose `thinking` names the mode NOT taken as something given up. **≥ 2 = PREDICTED, 1 = SPLIT, 0 = MISS.** | Mirrors `WF4`: mechanical exclusivity with no named cost is a legibility finding, not a design return. `WF6` and `WF7` both PREDICTED closes R216 C option 1 in the direction the round-3 pair read pointed. |
| `WF8` | Does the **memory replay re-subsidise** what exclusivity removed — does the jellyfish replay a mode the player already paid to forgo? | **NO — ≤ 1 turn where a replayed `either` row fires the mode the player did not choose that turn.** | Read the memory panel in the observation beside each jellyfish fire; count fires whose replayed card is a granted `either` row, and whether the fired mode differs from the mode last played. **≤ 1 = PREDICTED, 2–3 = SPLIT, ≥ 4 = MISS.** | MISS: the kit hands back the outcome the arm exists to make you choose between, so arm 2 cannot advance while `C.KURAGE_MEMORY` is on — a genuine interaction finding that goes to [USER] as a numbered pick (re-author the arm, or scope the memory), never a silent delete. |

### Contaminations, stated before the run

1. **The deck is GRANTED, not drafted.** Rows arrive in the starting deck via
   `understudy.embark --arm`, so nothing here says anything about draft rates,
   pool pressure, or how often a player would ever own the card. Every slot
   above is conditional on holding the row.
2. **`+proto` dev build.** `klee-mod/build/deploy_proto.ps1`
   (`-p:PrototypeCards=true`); the shipped release does not compile these
   classes and cannot reach them by any route, including a hand-typed id.
3. **The memory kit is ON, under `C.KURAGE_MEMORY` — a deliberate second
   variable, and D4 requires that it be named.** It is on because it is the
   world these rows would ship into and because `WF5` and `WF8` ARE the
   interaction. **The error direction is stated:** the kit adds free tempo (a
   0-energy replay of the memory's front) and a Muster discount, both of which
   make a priced Companion EASIER to afford — so a `WF3` PREDICTED (*the price
   binds*) is a **floor**, and a `WF3` MISS is **confounded** and must be
   re-read with the flag OFF before it fires any repricing. `WF5` exists to
   measure that confound rather than argue about it.
4. **Seat policy.** The Codex seat (GPT family) plays and writes the run
   record; all seven slice-1 rows are `authored_by: [claude]`, so the seat is
   author-disjoint under R217 C and `understudy/seat.py` will not refuse it.
   **R217 G rides on every line of the record: iteration feedback, never
   validation, never balance evidence, never approval.** Guardrail-7: bot
   numbers are floors. No number here is a win-rate or a comparison with any
   other build.
5. **R213 B.** No number measured on a prototype row is quotable. The slots
   count plays, turns and sentences; the two places a printed figure is read
   (`WF2`, `WF5`) read it as *above the base rung* or *below the printed cost* —
   a comparison inside one row's own face, never a figure carried out of this
   packet.
6. **Slice 1's four staged rounds have been read, and they set no threshold
   above.** The thresholds are drafted from the ADVANCE reads' own language and
   from §1's hypothesis, never from a staged number.

### Sequencing, and the preconditions

In order, and none of it is Claude's to start:

1. **`M67` is ruled.** It deletes none of these six rows, but it decides
   whether the Kokomi prototype surface is being emptied of slice 2 in the same
   sitting, and a fight staged into a surface that is about to lose four rows
   is a fight staged twice.
2. **`KURAGEMEM002`'s rerun happens first** — `EB-214`'s Muster keyword, then
   the memory gate re-posed on the unspent seed. Every fight here runs with the
   kit ON, and running them before the kit's own gate is re-read would put two
   unread instruments in one window.
3. **`EB-184` before F3, and only F3.** An Attack-typed `choose_one` demands a
   target even on a mode that attacks nothing; **Itto — Oni Rush is
   Attack-typed with a Block mode**, so `WF6` cannot be answered for it until
   the fix lands. Shinobu — Warding Ring is Skill-typed and is not blocked.
   Running F3 early would return a second arm for the defect that already
   returned Thoma's.
4. **Then F1, then F2, then F3** — arm A first because it has no kit dependency
   beyond the flag, the priced trio second, the exclusive pair last behind its
   defect.

**What this slate does not do.** It stages no board, pins no seed, spends no
call and grades nothing. It advances no row to a sheet: an ADVANCE-to-sheet
CANDIDATE is a candidate, and the accept-to-sheet signoff — re-authoring onto a
real sheet, ruling the numbers, bumping the stamp, commissioning the art —
stays [USER]'s one-way door, which is the whole reason this registration was
written.

---

## `KOKOMI-SLICE1-WF` — RUN AND GRADED

**RUN 2026-08-30 on `0.2.1786+proto.dirty`** (`-p:PrototypeCards=true`, game
v0.111.0 `public-beta`), branch `bt3-w5-run`. **Three fights, three separate
game sessions** — the whole-fight lifecycle cap is one per session, so the game
was relaunched and torn down between each. The kit was ON throughout
(`KurageMemoryLaw.AlwaysOn` is `true` in a `+proto` build), which is
contamination 3 as registered.

| fight | sealed record | run seed | arms granted |
|---|---|---|---|
| **F1** | `review/qa/blindplay/20260831-025000/` | `1L130R6XTSRQ` | Tidal Barrage |
| **F2** | `review/qa/blindplay/20260831-025720/` | (sidecar `embark-20260830-225629`) | Shinobu — Sanctifying Circle, Thoma — Crimson Guard, Itto — Superlative Guard |
| **F3** | `review/qa/blindplay/20260831-030325/` | (sidecar `embark-20260830-230248`) | Shinobu — Warding Ring, Itto — Oni Rush |

Each ran `--max-actions 24 --max-refusals 2`, all three terminated
`max_actions`, **0 refusals across all three**. Codex meter, unsmoothed: **5h
8% / week 1%** before F1, **5h 28% / week 4%** after F3 — **well inside**
`EB-227`'s guard (85% of the window, 50% of the week). **`EB-184` was closed
live in this window's phase 1**, which discharged the one precondition R227's
countersign left standing, so F3 ran.

**The operator drove to the first Monster room on each run, at zero Codex
cost**, and the seat's first page was the combat screen, as registered.
**Neow, by `KLEESPARK-W4` §19.5's rule** — *the boon that changes neither the
deck's card list nor the counted ratio, and if more than one qualifies, the
first the screen prints*:

| fight | boons offered | taken | why |
|---|---|---|---|
| F1 | Arcane Scroll / **Neow's Talisman** / Cursed Pearl | **Neow's Talisman** | the other two ADD a card (a Rare, and Greed); the Talisman upgrades in place and changes no card LIST |
| F2 | Scroll Boxes / **Fishing Rod** / Hefty Tablet | **Fishing Rod** | the other two add a pack and a Rare-plus-Injury |
| F3 | **Winged Boots** / Lost Coffer / Dowsing Rod | **Winged Boots** | the other two add a card reward and a Dowsing |

**A note that belongs to `EB-243` and is recorded here because this window
found it:** *Fishing Rod* — the relic `KLEESPARK-BT3`'s boards had declared —
is a **Neow boon**, offered here and taken. So the run-start "gift" those
boards named is the boon the staging path takes off a seed-derived offer, which
is exactly why it differed per seed and why a single registered name was wrong.

### The slate, graded mechanically

**The unit is ONE COMPLETE FIGHT** and each session's action budget carried it
past that fight; **every grade below is counted on the FIRST COMPLETE FIGHT
only**, and later pages are recorded and graded nowhere. Two readings are
disclosed before the grades because they are readings and not counts: the
falsifiers name `turn-*/reply.json` as their artefact and the driver writes one
of those per ACTION rather than per player turn, so "combat turn" is read as
"an action carrying a `thinking` sentence"; and `WF3`'s *"turns ended with
`end turn`"* is read on the `end turn` snapshots themselves.

#### Arm A — Tidal Barrage (F1)

| slot | grade | the reading |
|---|---|---|
| `WF1` | **PREDICTED** (≥ 2) | **2** actions name it. Action 6: *"Exhaust immediately activates Pearl of Wisdom … **before Tidal Barrage can scale from the Exhaust**"* — an Exhaust source played BEFORE the card, said in those words. Action 7: *"**One card has already Exhausted, so Tidal Barrage is now stronger**, and will Exhaust another card"* — the running count as the reason to order the turn. **Whole-turn counting produced sequencing in a fight, not only on a board built to reward it.** |
| `WF2` | **PREDICTED** (≥ 1) | One resolution at **2 Exhausts** — Gorou's, then the card's own. The wire has the arithmetic: Nibbit **34 → 23**, so Tidal Barrage dealt **11**, which is the sheet's `base 5 + 3 × 2` exactly. The page showed a live preview move **5 → 8** after Gorou and then delivered 11. `WF1` is therefore readable rather than confounded. |

**A registration note, not a grade.** `WF2`'s falsifier says *"whose observation
shows a damage figure above the base rung"*; the printed face is a formula with
a live preview number, not a resolved figure, so the count was taken on the
falsifier's own *"i.e."* clause — the turn held ≥ 2 Exhausts at resolution — and
confirmed against the wire's HP delta. The tester named the preview and could
not explain it: *"Tidal Barrage's printed damage changed from 5 to 8 after Gorou
without an explicit explanation on the screen."*

#### Arms B-p, C-p, D-p — the cost-line price (F2)

| slot | grade | the reading |
|---|---|---|
| `WF3` | **SPLIT** (1, threshold 2) | **One** turn ended with a priced row in hand that the turn's starting energy could have paid for alone: turn 1's `end turn` held **Thoma — Crimson Guard (3)** against a starting 3. The other two `end turn`s held no priced row at all — one on an empty hand. Registered consequence: *"the price binds but thinly; the arms advance and the re-author carries an explicit note that the 3-energy rung is the whole mechanism."* |
| `WF4` | **SPLIT** (1, threshold 3) | **One** action names a priced row together with a line forgone — action 16, *"Itto immediately deals more than the remaining 8 HP, ending the fight **without relying on Poison timing or another random companion**"*. **This is the marginal one and it is disclosed as marginal:** the other two priced-row plays (actions 6 and 14) name only what the card itself bought, and on a stricter reading that takes *"forgo the turn's other line"* to require a named CARD, `WF4` reads **0 = MISS**. The grade taken is SPLIT, on the falsifier's second clause as written; a reader who reads that clause narrowly should read MISS, and both readings sit in the same region — **the price is paid far more often than it is named.** |
| `WF5` | **PREDICTED** (< 50%) | **0 of 3** priced-row plays resolved below the printed 3 — every one of Itto ×2 and Shinobu ×1 shows `energy_cost: 3` on its own page. **The Muster discount is real and it landed elsewhere:** action 1's *To the Front!* converted a Coral Guard into a 0-cost *Gorou — General's War Banner* and the tester named the discount in those words, but no Muster ever discounted a PRICED row. The kit does not defuse the price. |

#### Arms B-e, D-e — exclusive modes (F3)

| slot | grade | the reading |
|---|---|---|
| `WF6` | **MISS** (0 Block-mode plays) | **0** on the literal falsifier, and **the denominator has to travel with it.** *Itto — Oni Rush* was held and played **once**, choosing *"Deal 14 damage"* on a page where the enemy stood at **10 HP** and that mode was exactly lethal. ***Shinobu — Warding Ring never reached the hand at all***, so the PREDICTED band — *"≥ 1 per row"* — was **unreachable by construction**, and contamination 1 (*"every slot is conditional on holding the row"*) applies to that half. The registered consequence of a MISS is that the two `either` rows RETURN; **a RETURN moves no number by itself** (R215 B, Guardrail-7), and Shinobu's half of it rests on evidence the fight never produced. **The honest act this grade licenses is a rerun with both rows held, not a design edit.** |
| `WF7` | **MISS** (0, threshold 2) | Neither the play nor the mode selection names the forgone Block as something given up: *"choosing this card's 14-damage mode should end the fight immediately and avoid the incoming attack"*, then *"this option is lethal and prevents its 11-damage attack."* Registered consequence, quoted: *"mechanical exclusivity with no named cost is a **legibility finding, not a design return**."* On a denominator of one mode choice. |
| `WF8` | **PREDICTED, and VACUOUSLY so** | **0** fires replayed a granted `either` row, which satisfies *"≤ 1"* — but **no granted `either` row ever entered the memory**, so the interaction the slot exists to test was never posed. The one fire of the fight replayed *Gorou* at price 0; the queue's other entries were a Mustered *Coral Guard* (price 3) and the SHIPPED *Itto — Superlative Superstrength* (price 3), neither a granted row. The threshold is a ceiling, so absence passes it as written; **the grade is recorded as registered and its vacuity is recorded beside it.** |

### What this round bought, and what it did not

- **Arm A is the clear result.** Both its slots PREDICTED on their registered
  thresholds, and the wire's own arithmetic (11 damage on two Exhausts) shows
  the mechanism doing in a fight what the staged boards said it did. Under the
  slot's own decision column that makes arm A an **ADVANCE-to-sheet candidate**
  and its re-author unblocked — **a candidate, and the accept-to-sheet signoff
  stays [USER]'s one-way door**, which is the whole reason this registration
  was written.
- **The three priced arms carry a matched pair of SPLITs.** The price binds,
  once, in a four-turn fight; it is named, once, and marginally. `WF5` clears
  the confound the flag introduced — the Muster discount never touched a priced
  row — so `WF3`'s reading is not confounded in the direction contamination 3
  warned about. Under `WF3`'s own decision column a SPLIT advances the three
  arms **with the 3-energy rung named explicitly in the re-author**.
- **The two exclusive arms are the weak half of the round.** `WF6` MISSES on
  one lethal-range play of one of the two rows, `WF7` MISSES on the same single
  choice, and `WF8` passes on an empty denominator. **What the three of them
  jointly show is that the fight was too short and one row never arrived** —
  three turns, one `either` play, one memory fire. The registered consequences
  stand as written and nothing is edited on them.
- **No number, threshold, sheet row or constant moved, and no row was accepted
  to a sheet.** Every sentence the tester wrote is R217 G iteration feedback,
  and every observation is about a prototype row on a `+proto` build (R213 B).

### Recorded, and graded nowhere (R101b)

- **The jellyfish's own text disagrees with what it does — a THIRD independent
  witness.** F1's fight record: *"the jellyfish's displayed end-turn action
  changed according to cards played even though its headline text only described
  Hydro damage."* F3's run record says the same from the other side: *"The
  jellyfish's end-of-turn action seemed to follow the last card played."* Both
  corroborate **`EB-247`**, minted the same night off `KURAGECAD-W1` — three
  witnesses now, across two characters and three sessions.
- **The kit reads as the engine to a blind player.** All three run records name
  Exhaust → Charge → memory as the character's spine without being asked, and
  F2's names the memory's own affordability as a tension: *"the memory queue
  also encouraged Charge generation while sometimes making that investment feel
  inaccessible."* That is the scarcity `KURAGECAD-W1`'s enriched deck could not
  produce, seen here on a deck nobody enriched. **It grades nothing in either
  packet** and is written down because the next kurage cell will want it.
