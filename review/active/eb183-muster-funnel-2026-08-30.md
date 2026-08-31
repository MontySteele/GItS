# EB-183 — Muster's Charge subsidy, asked at the funnel

**2026-08-30. Branch `eb183-muster-funnel`, on `main` at `c17a2fe6`.** Built
under R213 E1, which R216 D deferred the question into. Everything here lives
on the quarantined prototype surface (`docs/prototype-surface.yaml`); **no
shipped sheet row moved by one character**, and under R215 B no number measured
on a prototype row is quotable in a packet, a register or a commit message.

**I designed this row, so I am not allowed to say whether it is good.** That is
R213's first guard. What follows is what was built, what the pair asks, and the
two things that need a human before anything is staged.

---

## 1. The question, and why it needed a fifth pair

R216 D deferred Muster's Charge subsidy into R213 E1 rather than settling it,
in these words:

> a Mustered Companion costs 1 less, Exhausts, and pays 1 Charge, so blocking
> with one also advances Kokomi's finisher.

That sentence has **two** readings, and only one of them can be put on a card.

**The first — the subsidy's SIGN.** If fielding a formation currently advances
the finisher for free, perhaps it should cost the finisher instead. Kokomi
slice 2 built that as its arm 4 (*Watatsumi Levy*: Muster 2, spend 6 Charge).
It lives in a card's effect list, and it **retired** on 2026-08-30 with the
rest of slice 2 under R227 / M67 (1) — every arm that priced Charge on a card
retired as authored, and the spend plumbing stayed.

**The second — the recruits' WAGE.** *Recruits from an order that paid for
them pay no Charge when they Exhaust.* One order cannot both cheapen a unit and
be paid for rotating it out. That is not an effect list at all: it is a
property of the exhaust **funnel**, so it wants a flag on the recruit and a
check where the wage is paid. Nothing in slice 2 could express it, which is why
slice 2's own §6 asked for it to be minted as its own item rather than smuggled
into a card row. It was minted as `EB-183`.

**R213 E1 stays open until both readings have been asked.** That is the gate on
this item and it is why the retirement of the four priced arms does not close
it.

### Why this is not a retired arm

R227 closed `M67` at option (1): *slice 2 retires — the four Charge-priced arms
and their round-2 boards delete, the spend plumbing stays, and the Charge
question moves whole to the memory program.* The thing being retired is a card
that **prices Charge**, because R226's signed Charge LAW says no card prints a
Charge price and no card reads the bank proportionally.

The row built here prints no Charge price and reads the bank at no point. It
prints `Muster 2` and one sentence about what the units it musters are paid.
What it moves is an **accrual** the order already paid for.

### The one place it touches signed LAW, disclosed rather than buried

R226 signed Kokomi's Charge accrual rule as PROSPECTIVE law: 1 per Exhaust of
one of her own cards, **Companions INCLUDED**, Status and Curse excluded. It
explicitly did **not** apply v3 §4(iii)'s Companion-exclusion clause, in those
words: *the funnel does not narrow.*

This arm does not narrow the funnel either. It narrows **one prototype order's
own recruits**, by that order's own printed text, and every other Exhaust on
the board pays exactly what R226 says it pays. That is why the flag is stamped
by the **order** rather than keyed on "is a Companion" — a blanket carve-out
would have contradicted signed text, and this does not.

**This paragraph is the thing being countersigned.** If [USER] reads R226's
"the funnel does not narrow" as also forbidding a prototype order that waives
its own recruits' wage, then this row should be deleted rather than staged, and
R213 E1 closes with only one of its two readings asked. I do not think that is
the right reading — a quarantined order asking an open question is what the
prototype surface is for — but it is not mine to settle.

---

## 2. What was built

### Both engines, default off, nothing shipped moved

**The sim.**

| | |
|---|---|
| the flag | `Card.muster_subsidised` (`tier0/engine/state.py`) — a combat-local provenance stamp, in the same class as `conscripted` and `from_kurage_memory` |
| the one writer | `effects._op_conscript` — on a `subsidy: waived` conscript op, which no shipped card carries |
| the vocabulary | `effects._conscript_subsidy_waived` closes it at `paid` / `waived` and **raises** on anything else. A typo'd `waved` silently meaning "paid" would make an arm read as its own control, grade as a null result, and leave nothing in the record saying why |
| the one reader | `refpowers.after_card_exhausted`, beside the Kurage copy clause — the ONE exhaust funnel every route already passes through |

**The mod**, all of it `Compile Remove`d unless `-p:PrototypeCards=true`:

| | |
|---|---|
| the registry | `Powers/Prototype/MusterSubsidy.cs` — a `HashSet<CardModel>` on `KurageMemory.MemoryCopies`' pattern, because `CardModel` has no per-instance field to hang a prototype stamp on and adding one would be a shipped-surface change made for a quarantined arm |
| the clear | `KokomiResourceHooks.BeforeCombatStart`, beside `KurageMemory.ClearForNewCombat` — `EB-196`'s lesson applied before it can bite: a recruit is a combat-local instance and a stamp that outlived its fight would be a stale waiver on top of a slow leak |
| the writer | `KokomiConscript.Run` gains an **optional** `subsidyWaived`, so every shipped conscript face emits byte-identically to what it emitted before the key existed |
| the reader | the funnel seam in `KokomiResources.cs`, inside `#if PROTOTYPE_CARDS` |

**Charge only.** The Burst particle and the `exhaust_muster` income bucket are
untouched on both sides. R216 D's sentence is about the finisher meter, and an
arm that moved two meters would be unattributable. The recruit still rotated,
and the bucket still counts it — what moves is the amount.

### "A paid order" is derived, not picked

R212's derived-not-picked lane, and the derivation is one line: **the order
paid only if it actually put the recruit below its printed cost.** A
`cost_override` landing on the canonical number, or the flat −1 flooring at 0
on an already-free recruit, moved no energy and therefore bought no waiver.

The error direction is **one-way**: wherever there is doubt, nothing is
stamped and the recruit pays the shipped wage. The visible consequence is worth
stating — a recruit that prints 0 (and the Inazuma pool has several) gets no
discount and so keeps its Charge. That is the rule being coherent, not an edge
case being tolerated: no payment, no waiver.

### The tests, red then green

`tier0/tests/test_eb183_muster_subsidy_funnel.py` — **10, all green; three of
them failed first** (a wrong event name, a seed whose recruit printed 0 and
therefore correctly took no waiver, and a loader call that did not exist).

- the flagged recruit exhausts free; keeps its Burst; still counts as a Muster rotation
- the unflagged recruit pays; `subsidy: paid` spelled out is the same thing
- a matched pair on one seed: same recruit, same Burst, and the Charge is the only thing that moves
- **no shipped sheet row carries the op key** — read off the sheets, not asserted
- an unknown value raises
- the waiver is refused where the order paid nothing
- **flag-off byte identity**: a shipped `mass_mobilization` play banks exactly `1 + 2 × CHARGE_PER_EXHAUST` with the branch in place

`klee-mod/KleeTests/Prototype/MusterSubsidyTests.cs` — **8, all green.**
Instance identity, the sibling off the same model that must NOT inherit the
stamp, null-safety both ways, the per-fight clear, the optional parameter's
`false` default (the C# half of the "no shipped card" guard), the funnel's
reader, and the face printing the rule it takes back.

The C# suite passes **220 without the flag and 324 with it**; the mod builds
clean in both configurations. `python -m tools.run_lints --lane ci` is 30/30.

### The row

| | |
|---|---|
| id | `proto_muster_subsidy_funnel` |
| name | **Bounty of the Isles** (provisional and mine, R179) |
| cost | 2, Skill, Uncommon |
| prints | *Muster 2. Units mustered by this order pay no **Charge** when they Exhaust.* |
| shipped twin | `mass_mobilization` — *Rally the Isles*, 2, Skill, Uncommon, Muster 2 and **gain 1 Charge** |

Cost, type, rarity and the Muster count are unmoved, exactly as slice 2's arm 4
held them. The Charge keyword tip attaches to it automatically, because the
generator attaches by the op and not from a card list.

**The face prints the deviation because the keyword does not carry it.** The
Muster tip says the recruit costs 1 less and Exhausts; it says nothing about
what an Exhaust pays, because until this arm every Exhaust of one of her cards
paid the same. A card that takes that back has to print it or the blind grader
is reading a face that lies.

---

## 3. The pair, and the one deviation

`understudy/turns/eb183-muster-funnel/` — `subsidy-shipped.yaml`
(`kokomi-eb183-t09`), `subsidy-prototype.yaml` (`kokomi-eb183-t10`), and
`MANIFEST.md`, which carries the map, the arithmetic and the closeness table.
The numbering continues slice 2's `t01`–`t08` on purpose: this is that
question's fifth pair, not a new slice.

Both halves: **48/70 HP, no Block, turn 3, four energy, a Charge bank of 8, one
enemy at 37 HP telegraphing an attack, `exact_hand: true`.** The hand is the
card under test, Coral Guard, Water's Edge and All Streams Flow to the Sea —
slice 2's arm-4 hand exactly.

**The deviation is FOUR energy where arm 4 took three, and the arm is the
reason.** Arm 4's difference landed AT the order, so three energy reached it.
This pair's difference lands one play LATER — on a recruit's rotation — so the
turn has to afford the order AND a recruit's play, and a recruit costs its
printed cost less one, which the pool puts at anything up to two. At three
energy, whether the arm was askable at all would have depended on the game's
roll of the recruit.

**Nothing is staged.** No seed is pinned and both rows read `pending`. Staging
needs the live game and a dev build carrying the prototype row; this work was
done in a sibling worktree, which by house rule may not launch the game,
install the bridge or deploy.

### Closeness, and what it cannot do here

`staged_turn closeness` on the declared boards: **both SURVIVE**, gap 0.2850
(top1 20.700 / top2 14.800) over 14 lines, against a dominance threshold of
0.5. Read that as a refusal that did not fire, and nothing else (R213 F).

**The two halves read IDENTICALLY and neither top line contains the card under
test.** That is slice 2's own arm-4 disclosure, one step worse. The pilot
values a Muster order by what it puts in hand, not by what the recruits do a
turn later — and this arm's entire difference is what a recruit's rotation pays
a turn later. **So the instrument cannot separate these halves, and the blind
seat is the only reading this pair has.** If the seat cannot separate them
either, that is itself the arm's answer.

The standing second disclosure applies unchanged: the pilot has no Charge
hold-versus-spend term, so Charge income reads as free. Here the prototype half
*loses* income the pilot is not pricing, so if anything the error runs the
other way from slice 2's — and in both directions the falsifier is only being
asked to refuse, which it did not do.

---

## 4. The slate — DRAFTED, unrun, NOT countersigned

Drafted by Claude from the written design intent above and **committed before
any board is staged or any seed is spent** (R212 item 2). Offered for batch
countersign. Nothing below is graded and no seed has been spent.

**Unit:** one staged turn, blind-graded, per half of the pair. Both halves, the
shipped one first to discover the seed. The deciding read must be **GPT** and
not Opus: the row is `authored_by: [claude]`, and R217 C's author-disjointness
is the whole reason the field exists.

| slot | the claim | the falsifier, counted off the run's own artefacts |
|---|---|---|
| `MF1` | **The face teaches the rule.** | On `t10`, the deciding grader's account of what the card does restates the waiver in its own words — that the units it musters give up their Charge, however phrased. **1 of 1 forms.** If it does not, the arm is unaskable as printed and returns on LEGIBILITY, not on design. |
| `MF2` | **The waiver moves the turn.** | The deciding form's named second line on `t10` is a DIFFERENT line from the deciding form's named second line on `t09`. **Differ.** If they are the same line, the subsidy read as a funnel property changes no turn, and R213 E1's second reading answers NULL — which is a real answer and closes the gate. |
| `MF3` | **The price is felt at the turn.** | On `t10`, the grader's stated reason for its chosen line mentions the Charge bank or the finisher at all. **1 of 1.** A waiver nobody notices is a waiver that cannot have moved anything, and `MF2` differing without `MF3` would be a coincidence rather than a reading. |
| `MF4` | RECORDED, NOT GRADED. | Whether either form plays a recruit on the staged turn. The arm's difference is only realised on a recruit's rotation, so a turn where no recruit is played cannot show it. That is an instrument fact for the NEXT board, not a verdict on this one, and it decides nothing here. |

**Contaminations, stated up front:** a granted deck and a hand set by hand
through a dev door; a `+proto` build; four energy rather than the four pairs'
three (§3, with its reason); no seed pinned yet, so the encounter is whatever
the roll gives and the re-roll rule binds (if the telegraph is not an attack,
re-roll — the intent is half the question); and the closeness reading is of the
DECLARED board, which the manifest says cannot separate the halves at all.

**Gate:** [USER]'s countersign on §1's LAW paragraph and on this slate, then
game time — a dev build carrying the row, the pair staged shipped-half-first,
blind grading, replay of every graded line, and the pair read.

---

## 5. What is owed, and what is not

- **The run.** Nothing here is graded. `EB-183` stays open with the run owed.
- **[USER]'s countersign, twice**: on the reading of R226 in §1 (is a
  prototype order allowed to waive its own recruits' wage while the shipped
  funnel stays exactly as R226 signed it?), and on §4's slate.
- **Not owed:** any shipped change. No sheet row, no constant, no stamp and no
  version moved; both builds are clean and the flag-off byte identity is pinned
  by test on both sides.
