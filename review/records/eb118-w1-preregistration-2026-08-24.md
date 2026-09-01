Status: RECORD

# EB-118 Phase 3, Window 1 — pre-registration

> **Status: PRE-REGISTERED, 2026-08-24.** Written before the window opens, as
> R202 call (7) requires. Nothing in this document is a result. The build it
> describes sits INERT on `eb118-w1-labels`: Window 1 does **not** open with
> that branch. It opens after Phase 2's three integration windows close
> separately (R191) and their post-read is taken — that read, not this one, is
> W1's pre-state (R202 sequence steps (iii) and (iv)).

Plain English throughout; nothing here assumes you have read the code.

---

## 1. What Window 1 is

One window, containing metadata only: **sixteen `role` conversions and five
`archetypes` changes**, across nineteen cards on the three character sheets. No
card body moves. No cost, rarity or `solve` moves. No new op is used, no
drafter code moves, no pilot policy moves.

The card-by-card verdicts are the ones [USER] adopted on 2026-08-24 ("Agreed on
the per-card judgments for now"; "The current phase 3 ledger is ratified.").
They are named by card in the branch's commit messages.

The **fifth** tag change is `big_badda_boom`, which arrived later the same day
with the W1 audit ruling (§6.1) rather than with the ledger. It is counted here
because the window is what it will land as, not what it was first scoped as.

**One window, not a 1a/1b split.** R202 call (7) settled that, and this file is
the record it required.

## 2. The attribution claim, registered in advance

**Any movement in the connectivity instrument after Window 1 belongs to the
tag-changed cards, and to no others. In fact it belongs to four of the five:
the fifth, `big_badda_boom`, is measured at exactly zero.**

The five are `showstopper` (retagged `[fanfare]` to `[generic]`), `high_tide`
(drops `salon`), `rain_of_roses` (drops both `salon` and `spotlight`),
`singer_of_many_waters` (drops `salon`), and `big_badda_boom` (drops
`demolition`, §6.1).

The sixteen role conversions **provably cannot** move that instrument. `role`
appears in `tools/card_connectivity_report.py` exactly once, as an entry in the
`CARD_FIELDS_NO_HOOK` field list; no aggregate reads it. The report's
cross-archetype edges and its "cards in two non-generic plans" list are built
off `archetypes` alone.

This was verified rather than asserted, at build time on the branch: a
roles-only probe — the sixteen role conversions applied, the four Furina tag
changes reverted — reproduced the pre-window report **line for line, all 172
lines, with zero differences.** The Big Badda Boom drop was measured the same
way, on top of the finished label batch, and also moves **zero of 172 lines**
(§6.1): it sat in exactly one non-generic plan, and neither archetype-driven
aggregate in the report counts such a card.

So the registered attribution narrows rather than widens: the only connectivity
movement W1 can produce is Furina's, from four named cards.

## 3. What may not be claimed afterwards

**No causal role-versus-tag claim may be read out of tier-0.5 numbers after
Window 1.** Both fields move the offer scorer — `is_on_plan_payoff` is
literally `role == "payoff" and archetype in card.archetypes`, and both fields
are read a second time by the adaptive scorer — so a drafted-world number after
W1 cannot separate the role effect from the tag effect. The attribution in §2
holds for the **connectivity** instrument only.

If such a claim ever turns out to matter, the honest repair is to split the
window and re-run, not to reason backwards from a mixed number.

## 4. The post-read that is owed

Window 1 owes a **paired** connectivity re-read after it lands, against the
Phase-2 post-read that is its pre-state. That re-read reports **per-card
diffs as well as pool aggregates**, per packet §2.3 step 5.

Two standing constraints carry into it, unchanged: the classifier stays FROZEN
at `VOCAB_VERSION = "eb118-connectivity-v3"` and may not be revised mid-batch
(a wrong vocabulary means **both** sides are re-run, never just the post
reading); and the report must run in the primary checkout, not a worktree,
because its canon half reads `game_ref/`, which is gitignored and
primary-local.

## 5. Three build-time facts, recorded so they are not mistaken for results

None of these is the official read. All were measured on the build branch,
before the window opens, and are written down here so that nothing about them
can be discovered later and read as a finding.

**(a) The connectivity numbers the four Furina tag changes move.** Exactly two
lines of the 172-line report move, both in the Furina pool:

| measure | before | after |
|---|---|---|
| `cards in two non-generic plans` | 6 | **4** (High Tide and Rain of Roses drop out) |
| `fanfare\|salon` edge | 11 shared states | **9** (loses `private:fanfare` and `shared:hp_ledger`) |

Every other aggregate in every pool, on both the mod side and the vocabulary
table, is byte-identical. `UNCLASSIFIED` stays at none in all pools.

**(b) One coverage pin was added, and it is said out loud here rather than
buried in a diff.** `tools/lint_role_tempo_coverage.py --gate` gained one new
finding, `furina/spotlight frontload|mid`, and the debt list was regenerated
from 17 pins to 18 by the tool's own `--write-debt`.

The cause is entirely Rain of Roses' tag drop. Before: the spotlight sub-pool
held 18 cards, of which 5 covered `frontload|mid` — 27.8% against a floor of
25.0%. After: 17 cards, of which 4 cover it — 23.5%, which is under the floor.
Rain of Roses was the fifth carrier.

This is the same shape as the Phase-2A disclosure about
`furina/spotlight frontload|late`: **the coverage was inherited, not real.**
Rain of Roses reads no Spotlight state of any kind — that is precisely why the
tag was dropped — so its contribution to the spotlight plan's coverage was an
artifact of the tag rather than a card doing the job. Nothing was fixed and
nothing was lost; a card that was never covering the cell stopped being counted
as though it were. The gate is green again at 18 pins.

**(c) The Big Badda Boom tag drop moves the connectivity report by nothing at
all** — 172 lines in, 172 identical lines out, klee's included. It also adds no
coverage finding: the gate stays green at those same 18 pins. The numbers it
*does* move are the derived `demolition_commons` draw pool (8 to 7) and the
klee `demolition` sub-pool (28 to 27). Both are stated with the ruling at §6.1,
and the first of them is a combat outcome-distribution change rather than a
drafting one.

---

## 6. THE W1 AUDIT — both items RULED 2026-08-24

R202 call (9) opened this list. **Both items on it are now settled by [USER],
2026-08-24, verbatim: "Agreed on all of those rulings."** Nothing in this
section is open. The analysis that was put to [USER] is kept below the ruling
in each case, because it is the ground the ruling was made on and a later
reader should be able to check it rather than take it on trust.

## 6.1 Big Badda Boom's `demolition` tag — **RULED: DROPPED** (2026-08-24)

`archetypes` moves `[demolition, generic]` → `[generic]`. `role` stays `glue`;
the body, cost, rarity, Ethereal keyword and upgrade are all untouched.

**The ruled ground:** the tag means Bomb-plan *participation* everywhere else
in the arm, and this body has none of the arm's five verbs. The edit is on the
branch, and its consequence is priced on `secret_stash`'s row where it lands.

**What it did, measured after the edit rather than predicted:**

| | before | after |
|---|---|---|
| `demolition_commons` draw pool | 8 members | **7** |
| klee `demolition` sub-pool | 28 cards | **27** |
| klee `generic` sub-pool | 19 cards | 19 — unchanged, the card already carried `generic` |
| every payoff supply, all twelve arms | — | **unchanged**, the card is `glue` |
| `role x tempo` coverage gate | 18 pins, green | 18 pins, green |
| the connectivity report | 172 lines | **byte-identical, all 172** |

The connectivity null is worth stating plainly, because it is stronger than
the audit predicted: **not one line of the report moves**, klee's included.
The report's aggregates are hook-based and its only archetype-driven numbers
are cross-archetype edges and cards-in-two-non-generic-plans. Big Badda Boom
sat in exactly one non-generic plan, so it contributed to neither.

### The mechanical facts the ruling was made on

The row as it stood at Option A (R201, PR #65), before this ruling:

```
big_badda_boom, common, cost 2, attack, ethereal: true
  damage 16 to enemy
  if this killed its target: damage 8 to a random other enemy
  upgrade: {remove: ethereal}
  archetypes: [demolition, generic], role: glue
```

1. **The body carries no bomb machinery of any kind.** No `place_bomb`, no
   `detonate`, no `modify_bombs`, no `move_bombs`, no `chance_bomb_per_detonation`,
   and no read of the bomb board. Those five verbs are what the rest of the
   demolition arm is built out of — 16 `place_bomb`, 3 `detonate`, one each of
   `modify_bombs`, `move_bombs` and `chance_bomb_per_detonation` across the arm.
   Big Badda Boom's two ops are `damage` and a `conditional` on
   `killed_target`. On the printed body alone, it is a big Ethereal common
   attack.
2. **This is a pre-existing gap that Option A neither created nor closed.** The
   pre-Option-A row (PR #64) was a bare Deal 16 with the same tag. The on-kill
   splash Option A added is existing grammar shared with `sparkly_explosion`
   and `showstopper`, neither of which is a bomb verb either.
3. **The tag is not carrying any of the five arms' supply arithmetic.** The
   card is `role: glue`, so it has never been in `klee/demolition`'s payoff
   supply. Dropping the tag would move none of the Window-1 counts.
4. **But the tag is load-bearing in two places that are easy to miss.**
   - **Secret Stash's add-pool.** `secret_stash` adds a card from the derived
     `demolition_commons` pool, built at load time as "every non-kit Common
     whose `archetypes` contain `demolition`". Big Badda Boom is one of its
     **eight** members today. Dropping the tag takes that pool to seven and
     changes what Secret Stash can produce — a combat-engine consequence, not
     only a drafting one.
   - **The drafter's offer weight.** A card in `[generic]` only is offered on a
     flat weight rather than a plan weight, so a Klee demolition draft would
     see Big Badda Boom less often.
5. **Two things the drop would NOT disturb, measured on the branch rather than
   assumed.** The `role x tempo` coverage gate stays green at 18 pins with the
   tag dropped, and the klee pool's "cards in two non-generic plans" list is
   unchanged at two (`playtime_forever`, `sparkly_explosion`) — Big Badda
   Boom's second tag is `generic`, which that measure does not count.

### The two options that were put, and which was taken

**Option 1 — keep `demolition`, with a rationale printed on the row.** The
defensible reading was that the tag marks *plan membership* rather than
*mechanism*: a 16-damage Ethereal common is a card a bomb deck genuinely wants,
the demolition plan is the one that most wants a cheap Common finisher, and the
`demolition_commons` pool is a place where "cards a bomb deck drafts" is the
useful population rather than "cards that place bombs". Cost: the sheet keeps a
tag that no line of the card's body supports, which is exactly the class of
metadata Phase 3 exists to remove. **NOT TAKEN.**

**Option 2 — drop to `[generic]`. TAKEN.** The consistent application of the
Phase-3 rubric: the label follows the body, and this body has no demolition
mechanism. Its cost was known before the ruling rather than found after it —
`demolition_commons` goes 8 to 7, a real change to Secret Stash's outcome
distribution, which is a combat number and not a label; and the demolition
plan loses a Common the drafter would otherwise weight onto the plan. Both
were accepted with the ruling.

### What was not on the table

Redesigning the body to earn the tag is a Window-2 act behind the body-sheet
gate (R202 call (5)), and Big Badda Boom's body was ruled *the same day*
(R201). Nothing here reopens it.

## 6.2 `lasting_impression`'s `fanfare` tag — **RULED: KEPT** (2026-08-24)

**No sheet edit.** The row stands as it is: `archetypes: [fanfare]`,
`role: enabler`, Common, cost 1, `gain_encore 4`, Exhaust.

**The ruled ground, verified against the engine this session:** since the
Fanfare rework, **spending Encore IS the Fanfare generation leg.**
`resources.spend_encore` says so in its own docstring — *"Spending is Fanfare
flux (the drain->refill->spend cycle)"* — and its body proves it: every
successful drain calls `gain_fanfare(state, spent * FANFARE_PER_ENCORE_SPENT,
"encore_spent")`. An Encore battery is therefore a genuine *fanfare* enabler,
not a card wearing a plan tag it has no connection to.

This is the same reasoning that carried `reginas_mercy` in Window 1 — an
Encore battery keeps `[fanfare]` and converts to `enabler` on the *role*
axis, because it fuels the meter rather than cashing it. The two cards now
agree, and the Track A rule they are usually read against ("Fanfare prints
when Encore goes DOWN, never when it goes up", `docs/furina-cards.yaml`) is
the reason the tag is honest rather than a reason to drop it: the card fills
the buffer that the spend leg later converts.
