# Kokomi slice 2 — the Charge arms, the boards, and what is waiting on you

**2026-08-29. Branch `kokomi-slice-2`, stacked on `hygiene-state-diet` at
`6562b25`.** Authorised by R217 F, executing R213 E1. Everything below lives on
the quarantined prototype surface (`docs/prototype-surface.yaml`); **no shipped
sheet row moved by one character**, and under R215 B no number measured on a
prototype row is quotable in a packet, a register or a commit message. The one
exception is the decision-closeness reading, because it reads a *turn* and not
a row.

**I designed these cards, so I am not allowed to say whether any of them is
good.** That is R213's first guard, and nothing in this document grades an arm.
What follows is what was built, why each board is set the way it is, and what
still needs a human.

---

## 1. The question this slice is asking

Slice 1 asked what Companion Block costs. It could not ask the other half of
the same 2026-08-26 finding, because nothing in it gave the Charge bank a
second use. R217 F routed that here, before Klee, in those words: slice 1
"tests priced Companion Block at the turn, and cannot answer 'is there a payoff
besides waiting for Charge'."

Four pieces of evidence say the same thing from four directions.

**Your playtest, 2026-08-26.** *"Kokomi's Charge mechanic is ridiculously
powerful (often hitting for 100+) but otherwise suffers from low numbers... her
best turn is usually 'spam companion cards to block until you can hit with the
Charge'."*

**The blind seat, run B5.** *"The recurring tension was immediate survival
versus investing energy in Charge and future value."* Nobody told that seat
what Charge was for; it found the tension and named it unprompted.

**The blind seat, run B6.** *"Burst Energy accumulated alongside that plan,
although I never saw how to spend it,"* and Gorou's free attack granting Charge
and Burst was *"not explained in its displayed rules text."* That is the
keyword gap R215 D deferred into E1, now with a witness who hit it while
playing.

**R216 D.** Muster's Charge subsidy — a Mustered Companion costs 1 less,
Exhausts, and pays 1 Charge, *so blocking with one also advances Kokomi's
finisher* — was deferred into E1 rather than settled, because settling it would
have been pricing a resource whose rules were already open. E1 carries it.

So the hypothesis under test is:

> A bank that can only be watched feeds one decision — wait, or don't. A bank
> that can be **spent, thresholded, chosen against another currency, or paid
> for a formation** feeds a decision the player steers. If none of the four
> shapes changes how a turn plays, the answer to R213 E1 is that the null
> option was right and the rule closes again.

The three charter questions that bind (LAW D2, D3, D8) are: does Charge feed a
decision the player can **steer** rather than only watch; does the spend carry
a **binding price**; does a Charge line change the **shape** of a turn rather
than only its number. The slice does not settle any of them by argument. It
builds the four shapes, puts each on the same board as its shipped twin, and
lets the funnel ask.

---

## 2. The four rows, and how they will print

All four are on `docs/prototype-surface.yaml`, compiled only into a dev build.
A shipped mod does not contain the classes at all, so there is no id a normal
game could be talked into granting.

### Arm 1 — the bank buys something now

| | |
|---|---|
| id | `proto_charge_spend_strike` |
| name | **Sounding Line** |
| cost | 1, Attack, Uncommon |
| prints | *Spend 6 **Charge**. Deal `{Damage}` damage.* |
| shipped twin | `all_streams_flow` — *All Streams Flow to the Sea*, 1, Attack, Uncommon, 5 damage +1 per 2 Charge, **bank untouched** |

Same cost, type, rarity, target and noun as the twin. The pair differs in one
thing: that card reads the bank and keeps it, this one spends it.

### Arm 2 — a bar to bank to, not a slope to wait on

| | |
|---|---|
| id | `proto_charge_threshold_strike` |
| name | **Fathom the Tide** |
| cost | 1, Attack, Uncommon |
| prints | *Deal `{Damage}` damage. If you have at least 6 **Charge**: spend 6 **Charge** and deal 6 damage.* |
| shipped twin | `read_the_current` — *Read the Current*, 1, Attack, Uncommon, 7 damage, +6 more at 10 or more Charge, **bank untouched** |

Both of the twin's numbers, 7 and +6, are unmoved. Two things differ and they
are one idea: the bonus now **costs** the Charge it read, and the bar moves to
the slice's single price so that the bar and the price are the same fact. It
does not scale past the bar — R58's threshold grammar, which is what makes this
shape legal below Rare at all.

### Arm 3 — two prices for one outcome

| | |
|---|---|
| id | `proto_charge_mode_guard` |
| name | **Twin Tides** |
| cost | 1, Skill, Uncommon |
| prints | *Choose one: Gain 5 Block \| Spend 6 **Charge**: gain 12 Block.* |
| shipped twin | `coral_guard` — *Coral Guard*, 1, Skill, 5 Block |

Slice 1 arm 2's shape (Prune's "choose one") with the currency swapped: there
the two halves cost each other, here one half costs nothing but the card and
the other costs the bank. The cheap half is Coral Guard's 5 exactly, so the
shipped twin **is** the prototype's first mode printed alone — the pair asks
what the second mode is worth, and nothing else.

### Arm 4 — the formation is bought, not subsidised

| | |
|---|---|
| id | `proto_charge_muster_price` |
| name | **Watatsumi Levy** |
| cost | 2, Skill, Uncommon |
| prints | *Spend 6 **Charge**. **Muster** 2.* |
| shipped twin | `mass_mobilization` — *Rally the Isles*, 2, Skill, Uncommon, Muster 2 and **gain 1 Charge** |

Cost, type, rarity and the Muster count are unmoved; the Charge line's **sign**
flips. That is R216 D's deferral put as a price: if fielding a formation
currently advances the finisher for free, this asks whether it should cost the
finisher instead.

### The one price, and the one number that is not a shipped number

Every row that charges Charge charges **six**. That is an attribution call, not
a balance one: four arms differing in shape *and* in price would leave nothing
about a turn attributable to the shape. Six also sits under the eight the
boards bank, so a spend leaves a bank behind and the shipped readers stay live
on both halves of a pair.

Every other number is lifted off a shipped face. The exception is **12**, and
it is derived rather than picked: the shipped readers pay 1 per 2 Charge *per
cast* and keep the bank, so a spend of 6 that empties the bank has to be worth
about four casts of a reader to compete at all — 2 per Charge spent. It is used
twice, as arm 1's whole payload and as arm 3's Charge half, so that arm 3 adds
nothing to arm 1 except an alternative.

### The Charge keyword decision

**There was no Charge keyword in the mod.** The meter's name is printed on
about a dozen faces and nothing on screen said what it was. R215 D found that
and deferred the label into E1 — labelling a resource whose rules are open
would have been settling them. Run B6's seat then walked into it from the
player's side.

**The decision: the keyword ships here, on the prototype surface, scoped to
cards that print a Charge PRICE.** It is `KokomiRiderTips.ForCharge`, in the
same class and on the same bargain as the Muster keyword R78 added: a hover tip
whose title is a loc row and whose body is built live, quoting
`CHARGE_PER_EXHAUST` from the constant rather than a typed numeral, and adding
what the bank holds right now when there is a combat to read. It is attached
**by the op**, not from a card list, so a new spender cannot ship printing a
word nothing explains.

**Scoped to spenders deliberately, and this is the part to push back on if you
want to.** The shipped `gain_charge` faces have exactly the same gap. Fixing
them is wording-only hygiene and is allowed — but it re-emits roughly thirty
generated files, and a diff that large does not belong in the same commit as
four arms it would be read beside. It is listed in §6 as owed, not skipped.
Two smaller reasons point the same way: it is the *spending* rows that made the
word answerable at all (until a card printed a price there was no sentence to
write about what holding one is worth), and if the slice is rejected the rows
and their keyword leave together under the surface's deletion rule.

### What the engine had to grow, and why it is quarantined

`ChargeResource.Spend` was a documented no-op and tier0 had no `spend_charge`.
Both engines now have one, on `spend_spark`'s rail end to end:

- **All or nothing, no overdraw.** That is her LAW rather than a taste call:
  shortfall-drains-HP is Furina's Encore alone, and "no self-damage anywhere in
  her kit or personal pool" forbids the shape outright.
- **A visible cost line.** A top-level price is derived from the printed op
  (`combat.charge_cost`, `IsPlayable`), so the card is unplayable below its
  price and the price shown and the price paid cannot drift apart.
- **`ChargeResource.Spend` stays inert.** It is still the "never spent"
  contract for every route the *game* can take generically — a canonical cost,
  a cost modifier, anything reaching a CustomResource without naming it. R80 is
  reopened, not repealed, and the reopening comes through one named, greppable
  door.

**One thing the game cannot do, and it is a real gap:** the choose-a-card
screen has **no per-mode playability**. Arm 3's Charge mode is offered whatever
the bank holds. It does not pay out on a short bank — the emitted body is
`if (!await SpendCharge(...)) return;` and the sim raises the same refusal at
the same point — but the face cannot grey the mode out, so a player with 4
Charge can pick a mode that does nothing. On these boards the bank is always 8
and it never fires; as a shipped shape it would be a D4 defect. §6 carries it.

---

## 3. The names, and what they lost to

Provisional names are mine under R212's ladder (R179), and these are all
provisional — they are deleted with the rows when the slice closes.

**Sounding Line. Fathom the Tide. Twin Tides. Watatsumi Levy.** Ordinary card
names, Watatsumi-flavoured, and none of them says spend, threshold, mode,
formation or prototype. The reason is slice 1's and has not changed: a blind QA
grader reads printed card titles, and a title that names the experiment tells
the grader which arm they are holding, which is the one thing a blind grade
cannot survive.

Two collisions were checked and one bit: **Undertow** was the first choice for
arm 1 and is already a shipped Kokomi Uncommon (`undertow`, `docs/kokomi-cards.yaml`).
`docs/reserved-card-names.txt` and all three card sheets were grepped for the
four names that shipped here; none appears anywhere.

The **turn ids** (`kokomi-slice2-t01` … `t08`) are opaque for the same reason —
they are printed into the packet. The filenames name the arm, because only the
tooling and the packet-writer read filenames.
`understudy/turns/kokomi-slice-2/MANIFEST.md` is the map.

---

## 4. The boards, and why each is set that way

Eight turns in four matched pairs. Within a pair the two files declare the
**same board** — HP, Block, energy, Charge, enemy, and the same alternatives in
hand — and differ in exactly one card. Every board carries `exact_hand: true`
(EB-165), so the staged hand is the declared hand and not the declared hand
plus whatever the game dealt.

Every board is **48/70 HP, no Block, turn 3, one enemy telegraphing an
attack.** Defence is worth nothing against any other intent, and what the bank
is worth against an incoming hit is half the question.

| pair | arm | energy | Charge | enemy | shipped half | prototype half |
|---|---|---|---|---|---|---|
| 1 | spend | 2 | 8 | 34 HP, attack 14 | `t01` All Streams Flow | `t02` Sounding Line |
| 2 | threshold | 2 | 12 | 40 HP, attack 14 | `t03` Read the Current | `t04` Fathom the Tide |
| 3 | mode | 2 | 8 | 34 HP, attack 14 | `t05` Coral Guard | `t06` Twin Tides |
| 4 | formation | 3 | 8 | 46 HP, attack 16 | `t07` Rally the Isles | `t08` Watatsumi Levy |

**No line on any board is lethal**, and the arithmetic is written per board in
the manifest: the largest total damage each board can produce at true values is
15 or 18 against 34, 24 against 40, 15 against 34, and 15 (or one recruit's 14)
against 46. "Just kill it" never ends a turn here, so the turn is always about
what to do with the bank.

**Why the Charge bank is 8 on three pairs and 12 on one.** Eight sits above the
six every prototype charges, so a spend leaves a bank behind and the shipped
readers stay live on both halves — the spend and the read are both real answers
to the same energy. Pair 2 is the exception and it is **forced**, not chosen:
its shipped twin's threshold bars at ten, so at a bank of eight that card's
bonus half is dead and the pair would be comparing a live card against a dead
one. At twelve both halves clear their bar for the same 13, and the only
difference left between them is whether the bank survives the play.

**Why two energy on three pairs and three on one.** Two energy against four
cards means the turn buys two plays at most and the last energy is contested,
which is where the attack/defend tension lives. Pair 4 needs three, because the
whole point of the formation arm is what the recruits do *once they are on the
table*; at two energy the order is the entire turn and the recruits just sit in
hand.

**Why Coral Guard, and only Coral Guard.** It is the one standalone Block on
these boards, in hand wherever it is not the card under test, because a Charge
payoff that nothing competes with is not a decision. A second flat-Block card
would make "defend" the answer by arithmetic rather than by choice. Pair 1 and
pair 3 also carry **Gyorin Formation** — not a standalone Block but the third
answer the bank already has, Block that *reads* the bank without spending it,
at 2 energy so taking it is the whole turn.

### The closeness reading

`staged_turn closeness` was run on all eight declared boards. **All eight
SURVIVE**: gaps 0.0000 to 0.2850 against a dominance threshold of 0.5, over 7
to 11 distinct lines. Per-turn numbers are in the manifest and in
`review/qa/<turn id>/closeness.json`.

That means no line on any of these boards is worth more than twice the
runner-up in the pilot's own currency, so the falsifier refuses none of them.
It is **not** a claim that any turn is good, and the numbers are not comparable
between two rows — R213 F allows the reading only as a refusal.

**Two things the reading cannot do, and both are disclosed rather than
buried.**

1. **The pilot does not price Charge as a cost.** It gained a Spark
   hold-versus-spend term at `P11` and has no Charge equivalent, so on these
   boards a spend looks free and a spender scores high. The error runs **one
   way**: an over-valued spender is a spender more likely to *dominate* its
   board, and dominance is exactly what the falsifier refuses. So a SURVIVE
   here is the conservative direction and a refusal would have been the
   suspect result. Building the term is a `POLICY_VERSION` change carrying its
   own re-baseline, which is frozen and is not this slice's to make.
2. **Pair 4's two halves read identically, and neither top line contains the
   card under test.** The pilot values a Muster order by what it puts in hand,
   not by what the recruits do a turn later, so at three energy it prefers
   three 1-cost plays on both halves. That pair is not separated by this
   instrument at all. The blind seat is the only reading it has, and if the
   seat cannot separate them either, that is itself the arm's answer.

---

## 5. What is staged, and what is waiting

**Nothing is staged.** Not one of the eight, including the four shipped halves.
Every seed is unpinned and every row reads `staged: pending`.

Staging needs the live game, and the live game and the art-bearing main
checkout belong to another session for the duration of this branch. This work
was done in a sibling worktree, which by house rule may not launch the game,
install the bridge or deploy. So what is waiting is, in order:

1. **A dev build** carrying the four prototype rows
   (`klee-mod\build\deploy_proto.ps1`), on the main checkout.
2. **Staging the four pairs**, shipped half first to discover the seed, then
   every other half of that pair with `--seed <that value>`. Two halves on two
   seeds are two different fights and the pair has measured the encounter
   instead of the card. **If a seed's fight telegraphs anything but an attack,
   re-roll** — here the intent is the question, so a wrong telegraph is a wrong
   board.
3. **Blind grading** — a fresh grader per packet, the four-question form,
   design-blind, and then the independent seat (a different model family, R217
   C) on every one of the eight.
4. **Replay** of every graded line (`staged_turn execute`, EB-170). Arm 3's
   card is a modal, so its form must carry a `choose` key or the replay stops
   with `modal_unanswered` rather than guessing.
5. **The pair read** — shipped half against prototype half, arm by arm.

And the same seat guardrail slice 1 ran under: seat testimony is iteration
feedback, never validation, never balance evidence, never approval (R217 G).

---

## 6. Register moves I think should be minted

I did not mint or close anything. Next free id is **EB-181**. My reading of
what should be, in the order I would file them:

- **Nothing closes.** The slice is not run.

- **A defect, and the sharpest thing this slice found: the choose-a-card screen
  has no per-mode playability.** A "choose one" mode that carries a resource
  price is offered whatever the bank holds. It cannot pay out — the generated
  body returns and the sim raises the same refusal — but the face cannot grey
  the mode out, so a player can pick a mode that does nothing and is told why
  only by its not happening. Next action: read `CardSelectCmd`'s
  choose-a-card path off the decompile for a per-option disabled state; if
  there is none, decide whether a priced mode may ship at all or must carry its
  price in the card's own cost line. Gate: none today (the boards bank 8). It
  gates any *shipped* modal that prices a resource.

- **`EB-172`'s pinned-assembly switch was broken in a clean worktree, and is
  fixed in place (commit D).** `dotnet build -p:UsePinnedAssemblies=true`
  failed on `GameDir is not set`: `Directory.Build.props`'s `RequireLocalProps`
  target's first `Error` fired whenever `GameDir` was empty, even after the
  pinned block had already set `GameDataDir`. A worktree has no `local.props`,
  which is exactly the case the switch exists for. The condition now also
  requires `GameDataDir` to be empty; proven by a `--no-incremental` build in
  this worktree with the switch and nothing else, 0 errors, with and without
  `-p:PrototypeCards=true`. Hygiene under the norms, no row minted.

- **Owed hygiene, wording only: the shipped `gain_charge` faces still print
  "Charge" with no keyword.** The definition now exists
  (`KokomiRiderTips.ForCharge`) and is attached only where a card prints a
  Charge *price*. Attaching it where a card prints a Charge *gain* re-emits
  roughly thirty generated files and closes the R215 D / EB-152 half that has a
  blind witness in run B6. Deliberately not done in slice 2's commits; it is a
  clean standalone change. Acceptance: every Kokomi face naming Charge carries
  the tip, and the lint that would catch the next one bites on a red fixture.

- **Owed engineering, the per-companion half of R216 D.** This slice put the
  Muster subsidy's *sign* on a card — the order costs Charge instead of paying
  it. The other reading, "recruits from this order pay no Charge when they
  Exhaust", is a property of the exhaust **funnel** rather than of a card's
  effect list, and needs a flag on the recruit plus a check at the funnel in
  both engines. It is a different arm and should be minted as one, not smuggled
  into a card row. Gate: R213 E1 stays open until both readings have been
  asked.

- **For the slate, not a register row: the pilot has no Charge
  hold-versus-spend term.** `P11` built one for Sparks. Charge now has a sink,
  and until the pilot prices it, every closeness reading on a Charge spender is
  taken by a pilot that thinks the spend is free. The error direction is
  conservative (§4), so this does not invalidate anything here — but it is a
  `POLICY_VERSION` change with a re-baseline attached, and both are frozen.
  **This is yours.**

- **For the slate, not a register row: no `DRAFTER_VERSION` bump was taken for
  the new `spend_charge` price.** `lint_op_parity` says a change to the priced
  op set is a `DRAFTER_VERSION` bump. I did not take one, and the reason is a
  claim about output rather than a request for an exemption: `spend_charge`
  lives on the quarantined surface alone, which no pool, digest or drafter can
  see, so every drafted number in the world is byte-identical with and without
  the branch. Bumping would archive a standing baseline for a change that moves
  nothing. If a spender is ever re-authored onto a real sheet, **that** is the
  change that moves the drafter. The reasoning is recorded in `tier05/draft.py`
  beside the branch; **flag it if you disagree**, because it is the one place
  this slice declined an instruction a lint printed.

- **Two defects fixed in place rather than filed**, both hygiene under the
  norms, both named here because they touched code outside the slice:
  `gen_klee_cards` gated Kokomi's hover tips on profile *identity*, so every
  Kokomi row on the prototype surface silently lost the Muster, Garment and
  pulse tips (a prototype row is emitted through a copy of the owner's
  profile). Now gated by `character_id`. The visible consequence is one hover
  tip added to slice 1's `proto_pearl_barrage_turn`; no face text moved.
  Second, `lint_op_parity` and the connectivity table are total by
  construction and both needed a `spend_charge` row.

---

## 7. What I could not do

- **Stage anything live** (§5): the live game and the main checkout belong to
  another session, and a worktree may not launch the game, install the bridge
  or deploy.
- **Discover seeds**, for the same reason. The declared boards are therefore
  the only reading that exists.
- **Run either deploy script**, or `build_pck`. A worktree has no
  `local.props`, no `game_ref/` and no art.
- **See a prototype card render.** Prototype rows have no art by design — art
  is commissioned when a slice is accepted and its rows move to a real sheet —
  so they will draw with no portrait. That is correct, not a defect.
- **Compile without a workaround — until commit D.** Commits A–C built
  against the pinned assemblies in the OneDrive vault only with a dummy
  `-p:GameDir=`; §6's one-condition fix removed the need, and the branch now
  builds in a clean worktree with the switch alone. Zero errors either way.

---

## 8. THE RUN (2026-08-29) — what actually happened

Everything §5 and §7 said was waiting is now done. This section is written after
the fact and by a different session from the one that designed the rows; it
records what the funnel did and settles nothing.

**The build:** `0.2.1293+proto`, built and deployed by `deploy_proto.ps1` on the
art-bearing main checkout, game closed, `validate.ps1` OK. The pin had not moved:
game v0.111.0, commit `41cef1ea`, buildid `24724944`, branch `public-beta`,
BaseLib 3.4.5.0 — all four read off disk before any live work.

### The staging, and the twenty-nine rolls it took

Every pair's seed was discovered by staging the shipped half, then pinned onto
both halves — in each file's own `seed:` key and in the manifest. Twenty-nine
rolls in total, because the packet asks for ONE enemy telegraphing an ATTACK and
most Act-1 first fights are two or three bodies, a debuff, or an attack too small
for the board to mean anything.

| pair | rolls | seed | the body it settled on |
|---|---|---|---|
| 1 — spend | 4 | `JMKCFWFSN8N0` | Sludge Spinner 34/38, attacks for 8 |
| 2 — threshold | 3 | `EXET6AYQYN9N` | Nibbit 40/42, attacks for 12 |
| 3 — mode | 12 | `4E4D9AV2RPPU` | Nibbit 34/42, attacks for 12 |
| 4 — formation | 10 | `QWVYM3T6J6RF` | Sludge Spinner 37/37, attacks for 8 |

**Pair 3 needed twelve rolls and they were the point.** Its question is 5 Block
against 12 Block for a bank of six, and a body telegraphing 4 answers both modes
with room to spare — the choice would have died on the board rather than in the
card. Twelve rolls found one single body telegraphing 12.

**Pair 4 settled at 37 HP where the design asked for 46, and that is an operator
call worth seeing.** `set_hp` clamps at a creature's maximum, and in ten rolls the
only single Act-1 body whose maximum reaches 46 was the Fuzzy Wurm Crawler, which
telegraphed 4 damage every single time. The choice was a 46 HP body against which
defence is worth nothing, or a 37 HP body telegraphing 8. Both of the board's
stated properties hold at 37 — one enemy, an attack telegraphed, and no lethal
line, since the largest total the board can produce is 15 — while at 4 damage the
defensive half of the question would not have been asked at all.

Each file now declares the LIVE body rather than the design's placeholder, so the
declared and observed closeness readings read the same board. Both were taken:
**all eight SURVIVE both ways and every number is identical between them.**

### The grades — sixteen forms, two graders on every turn

A fresh Claude grader per packet (`opus-5-fresh`, `claude-opus-5`; one agent, one
turn, never reused, no repo access, the packet inline) and the R217 C independent
seat (`codex-gpt-5.6-sol-fresh`, blindness proven from the transcript). No seat
refused; no answer was edited on the way in.

**The Claude grader SURVIVES all eight. The seat SURVIVES seven and REFUSES one.**

> `t08` — *"Water's Edge and All Streams Flow to the Sea on Sludge Spinner, then
> Coral Guard. This deals 15 damage and blocks 5 of the telegraphed 8 damage."*
> Refused `intent_insensitive`: question four is no.

### The replays — sixteen of sixteen, and one flagged

Every graded line was replayed live on its own pinned seed and board. **Fifteen
confirm the form's arithmetic to the hit point. One is flagged `misread` —
recorded, never re-graded — and it is the arm's own subject.**

| turn | grader | the board's answer |
|---|---|---|
| `t01` | Claude | confirms — Sludge Spinner 34 → 19, the 15 claimed; Block 0 |
| `t01` | seat | confirms — 34 → 25, the 9 claimed; Block 0 → 5 |
| `t02` | Claude | confirms — 34 → 16, the 18 claimed; **bank 8 → 2** |
| `t02` | seat | confirms — 34 → 22, the 12 claimed; Block 0 → 5; bank 8 → 2 |
| `t03` | Claude | confirms — Nibbit 40 → 16, the 24 claimed; **bank 12 → 12, untouched** |
| `t03` | seat | confirms — 40 → 16 |
| `t04` | Claude | confirms — 40 → 16, the 11-then-13 its ORDER argument predicts; bank 12 → 6 |
| `t04` | seat | **`misread`** — the form claims 13 then 11 for 24; the board produced **21**. This line plays the spender FIRST, so the reader behind it reads a bank the spend has already emptied and deals 8, not 11. Bank 12 → 6 |
| `t05` | Claude | confirms — 34 → 19, the 15 claimed |
| `t05` | seat | confirms — Nibbit 34 → 34, **zero damage**: the line was Gyorin Formation alone. Block 0 → 10 |
| `t06` | Claude | confirms — 34 → 25 (the 9), **Block 0 → 12**, bank 8 → 2 |
| `t06` | seat | confirms — identical |
| `t07` | Claude | confirms — Sludge Spinner 37 → 22, the 15 claimed; Block 0 → 5; bank 8 → 8 |
| `t07` | seat | confirms — identical |
| `t08` | Claude | confirms — 37 → 22; Block 0 → 5; **bank 8 → 8, the Levy unplayed** |
| `t08` | seat | confirms — identical |

**`t04`'s single flag is the most useful thing the replay step produced all
round.** Both graders played the same two cards; they differ only in the order,
and the board says the order is worth three damage. The arm is about exactly that.

### The defect the replay found in the instrument, fixed in place

Both `t06` replays first stopped `modal_unanswered`. The choose-a-card screen
names its options with the game's markup left in —
`Spend 6 [gold]Charge[/gold]: gain 12 Block` — while the packet a blind grader
reads is scrubbed of markup before the face is printed. So a form answering in the
only vocabulary it has (`Spend 6 Charge: gain 12 Block.`) could not match its own
option, and **every priced modal line would have stopped**. The operator override
could not rescue it either, and that is by design: it never overrides a form's own
answer, and the form HAD one.

`scenario.card_key` now folds the game's rich-text tags alongside case, the
BaseLib prefix and the separators it already folded; the words between the tags
are kept, because they are part of the name. The red test carries the live strings
verbatim, suite 3528 green, and both `t06` replays then completed **from the
form's own answer**, source `form`, no operator answer anywhere. Hygiene under the
norms, fixed rather than filed.

### The pair read

Shipped half against prototype half, arm by arm, on all eight packets with the
sixteen forms, verdicts and live replay post-states inline. Reply unedited:
`review/qa/kokomi-slice-2-pair-review-codex-gpt-5.6-sol.md`; prompt kept at
`review/qa/kokomi-slice-2-review-prompt.txt`, sha256
`4bbc6681e0ebf23288821fa2c6e70222548650e64ce0a074f0d974b44d1bbdef`.

**Two ADVANCE, two RETURN, no ESCALATE.** Seat testimony is iteration feedback,
never validation, never balance evidence, never approval (R217 G); ADVANCE means
worth asking again with whole-fight play, not ship.

| arm | card | outcome | the reviewer's own reason |
|---|---|---|---|
| 1 — spend | Sounding Line | **RETURN** | *"Only the numbers changed: both halves presented the same damage-versus-Block allocation, with the prototype simply offering more damage while consuming Charge."* The repair it names is the BOARD, not the arm: *"include another current-turn Charge use or reader so spending six Charge creates an observable sacrifice rather than merely a future hypothetical."* |
| 2 — threshold | Fathom the Tide | **ADVANCE** | *"The shipped half only cashed a threshold already reached, while the prototype introduced sequencing between a Charge reader and spender, plus a conserve-versus-spend line."* The cost bound: *"a concrete three-damage sequencing penalty."* |
| 3 — mode | Twin Tides | **ADVANCE** | *"The shipped pair disagreed between pure offense and formation defense, while the prototype added a chosen price for defense and let both graders combine offense with exact mitigation."* |
| 4 — formation | Watatsumi Levy | **RETURN** | *"Both shipped and prototype halves chose the identical three cheap cards; replacing Charge gain with a Charge payment did not alter the realized decision."* The repair: *"give Muster an observable near-term payoff and a credible window to choose it, so Levy's Charge payment competes with known value rather than unspecified randomness under incoming damage."* |

The reviewer's closing, verbatim: *"Overall, the round supports spending Charge as
steerable when it creates an immediate interaction—especially ordering or a
selected alternate price, as in Arms 2 and 3. Arms 1 and 4 did not establish that
on their boards. Nothing warrants ESCALATE: the one disagreement in Arm 2 is
resolved by replay, and Arm 4's conflicting intent answer was formally refused."*

### What the outcome means, and what it does not

The R213 E1 hypothesis is **not settled and not refuted**. Two of the four shapes
produced a decision a blind reader steered, and the reviewer's account of why is
the same in both cases: the spend had to interact with something else ON THE SAME
TURN — an ordering against a reader, or an alternative price for the same
outcome. The two that RETURNED are the two where the spend interacted with nothing
on its turn, and in both the reviewer returned the BOARD rather than the card.
That is a claim about the instrument, not about the design, and both prescriptions
are concrete enough to execute.

**The falsifier refused nothing.** Closeness SURVIVES on all eight, declared and
observed, which is a refusal that did not fire and never a rating (R213 F). §4's
first disclosure stands unchanged and is now load-bearing rather than theoretical:
the pilot still does not price Charge as a cost, so on every board here a spend
looked free to it. The error direction is conservative.

**Two rows are still unasked in any useful sense.** Arms 1 and 4 were graded,
replayed and read, and none of that is evidence about the shapes: on arm 4 the
card *was never played on either half*, which is exactly what §4's second
disclosure predicted before the round ran.

---

## 9. What the run leaves — what is already moving, and two picks that are yours

The independent seat RETURNS or ADVANCES with no [USER] form
(`docs/current/OPERATIONS.md`), so what to do with a returned board, and in what
order to build the work behind it, is Claude's call and is recorded here as
status rather than returned as a question. Two things are genuinely yours, and
they are below.

### What is already moving

- **The two RETURNed arms — executed.** Round-2 boards for arms 1 and 4 are
  drafted on branch `kokomi-slice-2-round-2`, unstaged. The reviewer returned
  the boards, not the cards, and wrote both prescriptions itself.
- **What ADVANCE buys arms 2 and 3 — the automatic next gate.** Whole-fight
  blind play on the `blindplay` seat is what follows an ADVANCE; there is no
  pick in it. It is **blocked on `EB-188`**, not skipped: prototype rows are
  quarantined out of every pool, so a blind run on a dev build cannot draw one
  until the build grows a `+proto` inclusion or a dev door that grants the arm.
- **The fifth pair, `EB-183` — sequenced.** The Muster board repair comes
  first, because arm 4's board could not ask a Muster question at all (the
  prototype was never played on either half), and a fifth pair staged on a
  comparable board would produce a fifth uninterpretable result. `EB-183` is
  built against a board that has been proven able to separate a Muster arm.

### PICK 1 — the pilot's Charge term

Unchanged from §6 and still yours: it is a `POLICY_VERSION` change with a
re-baseline attached, and both are frozen.

### PICK 2 — the Charge rule itself (`M67`)

**RE-SCOPED 2026-08-30 (later the same day): the accrual question below is
ANSWERED by R226, one branch over.** `r226-sitting-2026-08-30`, `git show
425912a`, signs Kokomi's accrual as *"uncapped, accrued at 1 per Exhaust of one
of her own cards, Companions included"* with exactly one destination — the
Bake-Kurage pays it at the threshold — and adds *"no card prints a Charge price
and no card reads the bank proportionally."* Against the five options below:
**1–4 are foreclosed** (a per-turn wipe is a passive spend the clause forbids;
the accrual funnel was widened, not narrowed, and R226 explicitly declined both
the Companion-exclusion clause and the relic-face edit; Charge is retained as the
kit's fuel), and **(5) survives as amended by the kit** — the bank is not a pure
ramp, because the jellyfish drains it. The clause is PROSPECTIVE on the
`C.KURAGE_MEMORY` flip; until the flip the shipped rule is still R80's *"Charge
is never spent"*, which forecloses the priced arms today just as firmly.

**What returns to [USER] is therefore the consequence, not the rule.** All four
slice-2 arms print a Charge PRICE — Sounding Line, Fathom the Tide (its bonus
costs the Charge it read), Twin Tides (mode 2), Watatsumi Levy — so all four
retire as authored, **including the two that ADVANCED**, which is what the memory
packet already stated at `review/active/kokomi-kurage-memory-2026-08-29.md:391-399`.
No round-2 board survives: `t01`/`t02` are arm 1's and `t03`/`t04` are arm 4's,
both category (a). `M67` stays OPEN and keeps its number, re-scoped to:

1. **R226 stands — CLAUDE'S DEFAULT.** The four prototype rows and the four
   `kokomi-slice-2-r2` boards delete under the prototype surface's own deletion
   rule. The engine machinery is KEPT — `spend_charge` on `spend_spark`'s rail in
   both engines, `ChargeResource.Spend` through its one named door,
   `combat.charge_cost` / `IsPlayable`, and `KokomiRiderTips.ForCharge` — because
   the kit's threshold fire is a spend. The Charge question moves whole into
   `KURAGEMEM002`'s whole-fight rerun.
2. **Carve-out — amend the R226 clause to admit priced arms.** A LAW amendment,
   [USER]'s alone, needing R226 re-countersigned. It reopens exactly the
   Encore-shaped-face precedent the clause was written to close.
3. **Hold slice 2 entire until `KURAGEMEM002` reruns**, deciding nothing now.

**Gate: [USER]** — a signed LAW's consequence reaching two graded arms is not
Claude's to take under R212.

The five options and the hold text below are kept as the record of what was
asked, unstruck: this is a design packet, not a measurement record.

**REGISTERED 2026-08-30 as QUEUE `M67`.** This pick was written here and never
minted, so `STATE.md` — which reads the register — reported that no
prototype-slice row was open while this hold was in force. The round-2 run was
scheduled against it on 2026-08-30 and STOPPED at the door, unstaged: no board
was staged, no model was called, no Codex budget was spent. The hold below is
why. Nothing here is answered.

Charge accrues universally on Exhaust and never resets, so the bank is a ramp
and a spend on it is an investment rather than a decision on the turn. This is
the rule the four arms were authored against.

1. Charge becomes per-turn — resets at end of turn; the jellyfish pulses on this
   turn's Exhausts; Exhaust stays her identity, relic and summon stay; readers'
   numbers re-derived; LAW R80 amended.
2. The relic loses the universal Exhaust→Charge rule, keeps Strength→Charge;
   Charge comes only from cards that print it.
3. Both 1 and 2.
4. Retire Charge outright and scale the summon on something else.
5. Leave Charge; accept a ramp character and get the interesting turns from
   Companions (the E3 slice).

**Staging the round-2 boards and whole-fight play of the two advanced arms are
HELD on this pick.** Options 1–4 retire arms 1–4 as authored — every one of them
prices or banks Charge under the current accrual rule — so running them first
would spend the instrument on a rule that is about to move. And a per-turn rule
is testable only by whole-fight blind play, never by a staged turn: a single
turn cannot show a bank that resets.

The accrual rule was an open choice from the start:
`docs/current/characters/kokomi-kickoff-v1.md` §2.1 lists it as item 5, *"Charge
accrual rule — universal exhaust→Charge (recommended) vs tag-gated"*, and it has
never been ruled.

## §10. Round 2 — the two boards, re-set

**THESE BOARDS ARE MOOT UNDER §9 PICK 2 OPTION (1), and held pending `M67`
(2026-08-30).** Both re-boarded arms price Charge — `t01`/`t02` are arm 1
(Sounding Line), `t03`/`t04` are arm 4 (Watatsumi Levy) — so under R226 they
retire with their arms and nothing in round 2 survives to run. What survives is
METHOD, not boards: round 1's two RETURN prescriptions (*"another current-turn
Charge use or reader so spending six Charge creates an observable sacrifice"*;
*"give Muster an observable near-term payoff and a credible window to choose
it"*) are the design brief for the memory kit's gate, and belong in
`KURAGEMEM002`'s board design rather than here. The section below is kept as
written, because it is the record of the repair those prescriptions bought.

**2026-08-29, branch `kokomi-slice-2-round-2`, cut from `main` at `a51b0ea`.**
This section is written by a session that owns neither the live game nor the
main checkout, so **nothing here is staged, seeded, built or launched**. It
records the two RETURNed boards re-set as declared boards, and it settles
nothing: §9's picks are untouched, no register row is minted or closed, and no
printed card number moved (R213 freeze). It executes the re-board of the two RETURNed arms — PICK 1 option 1 under the
§9 numbering of the day, which `a1df7d6` then took as an iteration call and
recorded under *What is already moving*.
**`EB-183` is deliberately not built** — PICK 3's own first option says arm 4's
board must be proved able to separate a Muster arm before anything is built
against it, and that proof does not exist yet.

The four files are `understudy/turns/kokomi-slice-2-r2/`, mapped by
`MANIFEST.md` there. Turn ids `kokomi-slice2-r2-t01` … `t04`: `t01`/`t02` are
arm 1's shipped and prototype halves, `t03`/`t04` are arm 4's.

**No seed is pinned, and that is not an omission.** A re-set board is a new
board and its encounter is a fresh roll, so round 1's four seeds belong to
round 1's four boards; slice 1's round 4 also found that a seed only reproduces
within one game build. Every file reads `staged: pending` with no `seed:` key.

### Arm 1 — the spend

> *"Only the numbers changed: both halves presented the same damage-versus-Block
> allocation, with the prototype simply offering more damage while consuming
> Charge."* The repair: *"include another current-turn Charge use or reader so
> spending six Charge creates an observable sacrifice rather than merely a
> future hypothetical."*

**What changed: one energy, from two to three.** The board already carried the
other Charge use the reviewer asked for — **Gyorin Formation**, a shipped Rare,
2 energy, Block that reads the bank at `6 + charge // 2` and never spends it.
At two energy taking it was the whole turn, so the card under test and the
reader could not be played together and the price of a spend was always a
next-turn question. At three they share the turn, and the price lands where a
grader can see it.

Both halves: player **30/70**, no Block, **3 energy**, bank **8**, one enemy at
**24 HP** telegraphing an attack of **12**. Hand on both: Coral Guard (1, 5
Block), Water's Edge (1, 6), Gyorin Formation (2), and the card under test —
All Streams Flow to the Sea on `t01`, Sounding Line on `t02`. Every card beside
the arm is shipped; a second prototype would confound the attribution.

| line, bank 8 | `t01` shipped | `t02` prototype |
|---|---|---|
| reader-Block, then the card | 10 Block, 9 damage | 10 Block, 12 damage |
| the card, then reader-Block | 10 Block, 9 damage | **7 Block**, 12 damage |
| bank at end of turn | **8** | **2** |

On the shipped half the two orders are identical, because neither card touches
the bank. On the prototype half they are **three Block apart** — the spend has
already emptied what the reader-Block reads. That is a sacrifice inside the
turn rather than a hypothetical about the next one, and it is the same
structure the reviewer credited on the arm that ADVANCED (*"sequencing between
a Charge reader and spender"*, at *"a concrete three-damage sequencing
penalty"*), asked here of a flat spender.

**Two other numbers moved as consequences.** The enemy sits at 24 against a
prototype-half ceiling of 18 (Sounding Line 12 + Water's Edge 6), so no line is
lethal on either half; the shipped ceiling is 15. And the player sits at 30/70
against a telegraph of 12 — 18 left with no Block, 25 at 7 Block, 28 at 10 — so
three Block is three hit points rather than the rounding error it was at 48/70.

### Arm 4 — the formation

> *"Both shipped and prototype halves chose the identical three cheap cards;
> replacing Charge gain with a Charge payment did not alter the realized
> decision."* The repair: *"give Muster an observable near-term payoff and a
> credible window to choose it, so Levy's Charge payment competes with known
> value rather than unspecified randomness under incoming damage."*

**Three changes, one per clause of that sentence.**

1. **The three-cheap-cards line is gone.** Round 1's hand was the order plus
   three 1-costs, which at three energy was a complete turn (15 damage, 5
   Block) that never touched the card. One 1-cost is replaced by a **0-cost
   shipped Inazuma Companion** — Shinobu — Grass Ring of Sanctification, 4
   Block — so the alternatives cost two energy instead of three and the order
   has a window to be chosen in. This is slice 1 round 4's repair for the same
   failure, on a different hand.
2. **The payoff is near-term and the cost is printed.** A Muster transforms
   cards already in hand and never takes one that is already a Companion, so
   this hand holds **exactly two** cards it can take: All Streams Flow to the
   Sea and Coral Guard. Muster 2 takes both, so what the order costs is a known
   number — **9 damage** (the reader at a bank of 8) and **5 Block** — instead
   of the "unspecified randomness" the reviewer named. A Mustered recruit costs
   one less, so the recruits are affordable on the turn that makes them; the
   payoff no longer sits a turn away. Three energy stays the budget, and it is
   also the guard that keeps the pool's 3-cost recruit unaffordable behind a
   2-cost order.
3. **A Companion is in hand, printed and immediate.** It is not a Muster
   victim, costs nothing to play, and shows on the face of the board what a
   recruit is worth, so the order is weighed against known value on both sides
   of the trade.

**The window is the telegraph.** The incoming hit is **8**; Coral Guard (5, one
energy) and the Companion in hand (4, no energy) cover **nine** between them, so
the whole attack can be answered for one of three energy and the other two stay
free for the order. A set-up turn is affordable, which is what makes declining
it a choice. Player **40/70**, one enemy at **26 HP**.

**What the halves differ by, at a bank of 8.** The shipped order takes both
takeable cards and pays a Charge on top: bank 8 → **9**, and the reader it
consumed is gone. The prototype order takes the same two victims and costs six:
bank 8 → **2** — the outlet and the fuel leave together. Either half can
instead cash the reader FIRST for 9 and then give the order, which leaves
Muster one victim, one recruit and one whiff; that trade is identical on both
halves and the bank at the end of it is not.

**What this board still cannot write** is which recruits the game rolls. That
is the game's pick, and it stays random. What it can now write — and does — is
the cost side and the timing, which is what the prescription asked for.

**Round 1's `set_hp` finding is honoured rather than repeated.** Arm 4 asked for
46 HP last round and settled at 37, because `set_hp` clamps at a creature's
maximum and no single Act-1 body reaching 46 telegraphed anything worth
defending against. Both boards here are designed **below** the maxima the run
actually rolled — 24 and 26 against Nibbit's 42 and Sludge Spinner's 38 — so
the staging can reach them without a hunt.

### The arithmetic, and no lethal line

Card values: Water's Edge 6, Coral Guard 5 Block, All Streams Flow to the Sea
`5 + charge // 2` = 9 at a bank of 8, Gyorin Formation `6 + charge // 2` Block
now plus 6 next turn, Sounding Line 12 for a spend of 6, the Companion in hand 4
Block. No Strength, no aura on either enemy, so every number is the printed one.

| turn | energy | Charge | enemy HP | largest damage the board can produce | headroom |
|---|---|---|---|---|---|
| `t01` | 3 | 8 | 24 | All Streams Flow (9) + Water's Edge (6) = **15** | 9 |
| `t02` | 3 | 8 | 24 | Sounding Line (12) + Water's Edge (6) = **18** | 6 |
| `t03` | 3 | 8 | 26 | reader first (9), then the order, then a 0-cost recruit — the pool's largest 0-cost hit is 7 → **16** | 10 |
| `t04` | 3 | 8 | 26 | the same line; the spend adds no damage → **16** | 10 |

On arm 4 the recruits' identity is the roll, so that column is the pool's
ceiling and not a number the file can write: the largest single recruit hit is
14 at a cost of 1 after Muster's discount, and even substituting it for the 7
the board totals 23 against 26. The 3-cost recruit lands at 2 after the
discount and is unaffordable behind a 2-cost order at three energy.

### Closeness

`staged_turn closeness` on all four **declared** boards (there is no observed
reading, because nothing is staged). `DOMINANCE_GAP` is 0.5. **All four
SURVIVE.**

| turn | gap | top1 / top2 | lines |
|---|---|---|---|
| `t01` | 0.0000 | 20.700 / 20.700 | 11 |
| `t02` | 0.0000 | 23.700 / 23.700 | 11 |
| `t03` | 0.1957 | 18.400 / 14.800 | 13 |
| `t04` | 0.1957 | 18.400 / 14.800 | 13 |

Receipts: `review/qa/kokomi-slice2-r2-t0*/closeness.json`. Read this as a
refusal that did not fire and nothing else (R213 F); it is not a rating and the
rows are not comparable to each other. §4's two disclosures carry forward
unchanged — the pilot still does not price Charge as a cost, with the error
running one way (an over-valued spender is a spender more likely to *dominate*,
which is what the falsifier refuses), and arm 4's two halves still read
identically to the pilot, which values a Muster order by what it puts in hand
rather than by what the recruits do when played. The one thing that did move
there: **the order now appears in the pilot's ranked lines at all**, where in
round 1 neither half's top lines contained the card under test. The blind
graders and the pair read remain the only reading that arm has.

### What is waiting

All of it needs the live game and the art-bearing main checkout, which this
branch may not touch:

1. A dev build carrying the prototype rows (`deploy_proto.ps1`).
2. Staging both pairs — shipped half first to discover the seed, prototype half
   with `--seed <that value>`. **Re-roll on any telegraph that is not a
   single-body attack**; pin the seed into each file and into
   `understudy/turns/kokomi-slice-2-r2/MANIFEST.md`, and re-declare the live
   body if it differs from the design so the declared and observed readings
   read one board.
3. `closeness --observed` on all four, beside the declared reading above.
4. Blind grading — a fresh grader per packet on the four-question form, and the
   R217 C independent seat on all four.
5. Replay of every graded line (`staged_turn execute`, EB-170).
6. The pair read, shipped half against prototype half, arm by arm.

Seat testimony is iteration feedback, never validation, never balance evidence,
never approval (R217 G).
