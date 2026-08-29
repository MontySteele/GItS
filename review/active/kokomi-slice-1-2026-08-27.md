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
