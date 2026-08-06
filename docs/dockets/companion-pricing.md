# Docket — companion pricing

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

**Status:** DOCKET. Candidates only. **Nothing in this file is ratified.**
Zero design authority. Opened 2026-08-06 (Track R) against the sitting of
2026-08-06 (`docs/sitting-record-predraft-2026-08-06.md`); ruling R111.

---

## 1. X10 — the Metallicize treadmill — **CANDIDATE, NOT RATIFIED**

**Verdict, verbatim:** *"10 of the same Companion at common seems exceptionally
unlikely. May be worth moving to Uncommon and adjusting power up."*

### Why this is a candidate and not a change

**"May be worth" is not a ratification**, and R111 declines to upgrade it into
one. The verdict does two separate things and only the first is settled:

1. **Settled:** the exploit line's reachability argument is rejected. Ten
   copies of one common companion is judged exceptionally unlikely in a real
   run, so the finding does not stand as a live degeneracy.
2. **Not settled:** whether `gorou_heart_of_the_clan` should move to
   **Uncommon** with a **power adjustment upward**. That is a pricing decision
   with a number in it, and it gets **priced at a sitting**.

### The candidate, stated once so the sitting has something to price

- Card: `gorou_heart_of_the_clan`.
- Proposed direction: Common → **Uncommon**, power adjusted **up** to match the
  new slot.
- Magnitude: **none proposed.** No number is written here, deliberately.
- Blocked on: a sitting. Nothing else.

**Mechanism, from `review/redteam/exploit-ledger.md` (X10):** turn-start
Metallicize is uncapped, never decays, and is granted *after* the block clear —
one common outruns every ramp in the roster. Pin:
`tier0/tests/test_s13_exploit_pins.py::test_x10_metallicize_treadmill_is_outpaced`,
which stays xfail(strict) because a candidate is not a fix.

---

## 2. ~~Not in this docket, and it needs a home~~ X2 rarity work — **THIS DOCKET OWNS IT (2026-08-06)**

> **VENUE ASSIGNED 2026-08-06 ([USER]): this docket owns X2 rarity work going
> forward** — the cycling-rarity law's audits, the Common instances it flags,
> and the pricing of any bump — on the same terms as §1: candidates only, no
> number written here, priced at a sitting.

> **Landing note, 2026-08-06 (Track Y).** The paragraph above is the 2-YES form
> pre-drafted at `docs/awaiting-user-slots-2026-08-06.md` slot 2, landed
> verbatim against [USER]'s reply *"YES — companion-pricing docket owns X2
> rarity work"* (sixth-wave brief, Track Y item Y-2; transcribed at
> `docs/sitting-record-predraft-2026-08-06.md` §7). The section's **"Recorded
> here as unrouted" standing is cleared** — struck below, not deleted (R101b) —
> and the heading is amended to say what is now true. The X2 audit results
> table is untouched: it never moved, under either answer.
>
> **Carried, because it was never a venue question:** §2's closing parity
> finding — the C# side reads companion rarity from `Star`, not the sheet's
> `rarity` field, so whether the cycling-rarity gate is enforceable in C# at
> all is open — is now *this docket's* open question, since this docket owns
> the work.

### The routing question as it stood before the reply (struck, kept for the record)

~~**X2's mechanical audit (R109) has no docket assigned by the sitting.**~~ The
cycling-rarity law — *"infinite cycling engines gated to Uncommon rarity or
higher. If this is Common, it needs a bump"* — comes with a rarity check owed
on `sayu_naptime` and on every self-replacing 0-cost non-exhaust companion, and
Common instances are to be **flagged for a bump**.

That is companion-rarity work and it is plausibly this docket's business, but
the routing was not given and Track R does not assign it. ~~**Recorded here as
unrouted**, so it is visible rather than lost, and surfaced to the
coordinator.~~ **MARKER CLEARED 2026-08-06 by the venue assignment above: the
work is routed, and this docket is where it is routed to.**

**Coordinator note, 2026-08-06:** the audit itself was Track T's brief and it
ran the same night (`docs/track-t-audits-2026-08-06.md` §T-1); its *results*
are recorded below so they are not lost, while the *venue* question — whether
this docket owns X2 rarity work going forward — ~~stays open for [USER]~~
**was answered YES on 2026-08-06; see the banner at the head of this section.**

### X2 audit results (Track T, 2026-08-06)

Sweep of all 298 committed rows; predicate = printed cost 0, non-exhaust, net
hand delta ≥ 0. Three matches:

| card | pool | rarity | disposition |
|---|---|---|---|
| `sayu_naptime` | inazuma companions | uncommon | compliant, no action |
| `sucrose_gust` | mondstadt companions | **common → UNCOMMON** | the verdict's ratified conditional executed (rarity field only, no stat change) — it is `sayu_naptime`'s shape line for line, and S13's own corpus runs 14 copies of it as the engine of `klee_bombs_3` (verified infinite) |
| `florid_cadenza` | furina-cards | uncommon | compliant, no action |

Borderline, **no action taken**: `quick_fuse+`, `to_the_front+`, `moon_signal+`
(all Common, all self-replacing only *after upgrade*, none a companion —
`to_the_front+` is the sharpest, hand-positive). Also noted:
`barbara_shining_idol` (uncommon, needs X1's discount to reach 0),
`curtain_cue` (uncommon, conditional draw).

Rider forced by the bump: `sucrose_gust` now strictly dominates `moon_signal`
at cost 0, so `tools/lint_strict_domination.py` gained an allowlist entry
beside the identical, already-red-pen-queued `sayu_naptime`→`moon_signal` pair.

**Parity question for the implementer:** the C# side reads companion rarity
from `Star`, not the sheet's `rarity` field — this bump moves the sim/design
sheet, and whether the cycling-rarity gate is enforceable in C# at all is open.

---

## 3. Cross-notes landed on this docket by the Cold Reading sitting (2026-08-06)

Neither is a price and neither is this docket's to decide. Both change the
**assumptions** the pricing sitting works from, which is why they are here
rather than in a log somebody has to remember to read.

**`NC-10` — the shop is now a real Rare source, in both slots (R116).**
Verbatim: *"Slot 1 should be 'Uncommon or higher from the home region'; slot 2
should be 'any companion card'; this is a defect."* Both engines implement the
spec. **What that does to this docket:** every companion-acquisition assumption
priced against "slot 1 caps at Uncommon" is now wrong in the generous
direction — a Rare companion is reachable through the shop in both slots, so
Rare-companion scarcity is not what the old readings assumed. `R59`'s slot-2
floor and `R60`'s shop-only override sit in the same neighbourhood and should
be read together with it.

**One question is deliberately open and is NOT this docket's to close by
default:** rarity-odds **renormalization within the Uncommon+ pool** — condition
the existing `SHOP_COMPANION_RARITY_ODDS` on ≥Uncommon, or state a fresh split.
R116 surfaced the candidate readings rather than choosing, because a
renormalization chosen by an implementer is a balance value chosen by an
implementer. If the pricing sitting wants to choose it, it may; it may not be
chosen silently on the way to something else.

**`NC-11` — `X10`'s S14 caveat resolves, and §1's candidate is unaffected
(R116).** S14 had filed that X10's numbers were sim-side because Frail changes
the wall's arithmetic in the mod. `NC-11` is ruled: **power-sourced block is
raw**, the sim's exemption is canonical, and the mod is the defect side. So
post-fix, **the treadmill's sim-side numbers hold in the mod too**, and §1's
candidate is priced against numbers that describe both engines rather than one.
§1's status is untouched — still a CANDIDATE, explicitly not ratified.
