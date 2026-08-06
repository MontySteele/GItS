> **MOVED 2026-08-06 — Clear the Stage, Track R-B resumption (R121 `Q20`, MOVE-WITH-RESOLVER; charter R119, rail 1).**
> Old path: `docs/brief-coop-charter-items.md` — new path: `docs/archive/brief-coop-charter-items.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Live citers repointed in the move commit; ledger and other
> frozen citations keep the old path on purpose (rail 1: ledger bytes are
> never rewritten) and resolve through the moved-path resolver table,
> `docs/registry/identifiers.md` §17. Per-file map:
> `review/stage-clear/rb-move-manifest.tsv`.

# Design brief — the two co-op charter items: build or waive (2026-07-29)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

**Status: BRIEF. Nothing here is ruled and nothing here is a recommendation.**
Two items, each with what was promised, what exists, and options. No numbers
are PROPOSED; the numbers come after a direction is picked.

**Trigger:** [USER] ruling 2026-07-29 against `docs/backlog-2026-07-29.md` §3
item 8 — the charter items go to a **design pass, taken together with the
`unheard_confession` rework** (`docs/brief-unheard-confession-rework.md`).
Recorded as **R87 (4)**. Both items were deferred behind conditions that have
since lapsed: **co-op is live and has been played twice.**

**World:** RUNTEMPLATE 7 / CONSTANTS 4 / DRAFTER 12, going to DRAFTER 13.
Deployed artefact **0.2-247** (`29f5ce6`).

**Read first, because it governs every option below:** tier 0.5 models **one
seat**, and there is no C# test project
(`docs/coop-no-sim-backstop.md`). **Every co-op defect is play-derived, and
every co-op feature ships without a simulator behind it.** That is not an
argument against building either item; it is the price tag that must appear on
both.

---

## Item 1 — Fanfare partner-flux, with the mandatory Hot Hands anti-farm audit

### What was promised

`docs/furina-kickoff-v0.1.md` §4, verbatim:

> **Co-op:** partner HP/Encore flux counts toward Fanfare (her Genshin
> identity; first ally-coupled mechanic). **Audit at sheet pass:** exclude or
> discount self-inflicted partner damage (Klee's Hot Hands) or Fanfare farms
> itself.

Also `archive/furina-predesign-notes.md` Part 2. Two things are promised, not
one: the **mechanic**, and a **mandatory audit** that is a precondition of the
mechanic — the charter names the exploit in advance.

### What happened

Deferred to "Tier 2" by `archive/furina-sprint-1-report.md` §5. **There is no
Tier 2** — the repo has `tier0/`, `tier05/`, `tier1/`. The deferral pointed at
a milestone that does not exist, which is why it never came back.

### What exists today

- **Zero ally coupling**, either side: no partner/ally read in
  `klee-mod/KleeCode/Powers/FurinaResources.cs` or in
  `tier0/engine/resources.py`. Fanfare is generated entirely by its owner's
  own activity.
- The mechanic is absent from `open-playtest-items.md` §4 (the co-op section)
  and from the red-pen — i.e. it is not merely unbuilt, it was untracked until
  the 2026-07-26 recap audit caught it (`docs/missed-requirements.md` §1.1).

### What changed under it while it was parked — this is the part worth reading

**Fanfare generation went single-leg on 2026-07-28** (`docs/sprint-fanfare-rework-log-2026-07-28.md`
Track A; DRAFT amendment v1.12 in the principles). Fanfare now prints when
Encore goes **DOWN**, never when it goes up; `encore_gained` is **deleted in
both engines** and `encore_absorbed` is new.

The charter's promise was "partner **HP/Encore flux**". Under single-leg that
sentence has to be re-read before it can be built:

- **The partner-Encore half is half-dead by construction.** A partner gaining
  Encore now generates nothing even for themselves, so "partner Encore flux"
  can only mean partner Encore *spent* or *absorbed* — and only a second
  Furina has Encore at all.
- **The partner-HP half is the whole surface**, and it is exactly the half the
  charter's audit was written about. Klee's **Hot Hands** damages its own
  owner. Under the current invariant — *every point of damage past Block
  prints exactly 1 Fanfare* — a coupled partner-HP leg means **a Klee playing
  her own kit correctly farms her partner's Fanfare meter for free**, at a
  rate set by Klee's card economy rather than by anything Furina paid for.
- **Absorption changes the farm's shape too.** A partner's damage absorbed
  into *their* Encore is a real cost to them and would print for Furina under
  a naive port — a second seat's defensive plays becoming a first seat's
  offence.

So the audit is not a nice-to-have appended to the feature: **under single-leg
Fanfare the audit is most of the design work**, and it must now cover
absorption as well as self-inflicted damage.

### Options

- **BUILD (full).** Partner HP loss and partner Encore reduction both count,
  with the anti-farm audit as a gating deliverable: a documented exclusion or
  discount rule for self-inflicted partner damage, applied identically in
  both engines. **Costs:** a new ally-coupled read in `FurinaResources.cs`
  with no sim backstop and no test project; a sim that cannot model it at all
  (one seat), so it is measurement-free forever; and a first-of-its-kind
  cross-player state read in a **lockstep** game, where a divergent read is a
  desync rather than a wrong number.
- **BUILD (narrowed).** Partner **HP loss only**, discounted (a fraction, or
  a per-turn cap), self-inflicted damage excluded by source. Keeps the
  identity — "the audience's suffering feeds the performance" — while making
  the farm bounded by construction rather than by an exclusion list that has
  to stay current as Klee's and Kokomi's kits change.
- **WAIVE, on the record.** Fanfare stays owner-scoped; the charter line is
  struck with a dated note and the reason written down (single-leg made the
  Encore half vacuous; the HP half is a farm; co-op has no backstop). A waiver
  is cheap and honest; an unbuilt promise sitting in a charter is neither.
- **DEFER again — only with a named, existing trigger.** The previous deferral
  failed because it pointed at a milestone that does not exist. Any new
  deferral must name a condition that can actually fire.

---

## Item 2 — Cross-player Spotlight selector passing

### What was promised

`docs/furina-kickoff-v0.1.md` §3.1:

> **Delivery:** her starting relic adds an **Ethereal Spotlight selector** card
> to hand each turn. Applying it to a card in your hand reads that card's
> character tag and designates that character. **In co-op, the selector may
> instead be passed to a teammate, who applies it to one of their own cards
> (first cross-player designation — Appendix A.4's engineering, arriving
> early).**

Restated at §11.5. The registry is already specified as per-player ("two
Furinas = two independent Spotlights"), so the feature is *passing the
selector*, not sharing the designation.

### What happened

Deferred with "solo path first" in the sprint-1 docs. Co-op is live, so the
deferral condition has lapsed. No implementation, no tracking anywhere: no hit
in `klee-mod/KleeCode/`; `csharp-build-spec` §C4 (co-op hardening) never names
it; absent from both ledgers until the recap audit
(`docs/missed-requirements.md` §1.2).

### What exists today

The solo path is fully built and has been through two playtests and a UI
sprint. Relevant current facts:

- **A funnel can legitimately go quiet.** A Furina who takes Touch of Orobas
  never fires the designation funnel again, so the Spotlight beam stops
  appearing for that player for the rest of the run — **per-run and
  per-player**, so one Furina may still be firing it while another has stopped
  (`open-playtest-items.md` §4). Any cross-player passing must not make that
  legitimate silence look like a bug to the *other* seat.
- The guest pilot's standing UI note from the co-op playtest is **"extremely
  confusing"**. Cross-player passing adds a second player's hand to a mechanic
  that is already the hardest thing in the kit to read.
- Today's bug-fix pass repaired **three co-op ownership defects** in adjacent
  machinery (`docs/sprint-bugfix-log-2026-07-29.md`): Courtroom Drama's
  once-per-turn window was globally consumed and is now per-dealer;
  `CompanionPlays` had no clearing path for a partner's keys; `Company` never
  dropped a key. **None is play-verified** — the log says so plainly, and the
  co-op items "cannot be exercised at all without a second seat."

  That is the direct evidence for the shape of this feature's risk: **the
  ownership bugs we have found in co-op were all "whose is this?" bugs**, and
  a selector that legally crosses seats is a whose-is-this mechanic by
  definition.

### Options

- **BUILD.** The selector becomes targetable at a teammate; they apply it to
  one of their own cards; designation registers to the **passing Furina's**
  registry (per §3.1's per-player registry). **Costs:** cross-player card
  handoff in a lockstep game — new sync surface, no test project, no sim; and
  a legibility problem on top of an already-flagged legibility problem.
- **BUILD, minimum viable.** Pass the *designation*, not the card: the
  selector stays in Furina's hand and may name a teammate's character
  directly. Loses the "they choose which of their cards" texture; avoids
  cross-player card movement entirely, which is where the desync risk lives.
- **WAIVE, on the record.** Struck with a dated note. Appendix A.4's
  cross-player engineering then arrives with **Columbina**, which is where the
  charter originally said it belonged ("arriving early" was the deviation, not
  the plan).
- **Sequencing note, either way:** this is a co-op-only feature in a kit whose
  co-op behaviour has three unverified fixes in it as of today. Nothing forces
  it to precede a play session on `0.2-247`.

---

## The open hypothesis both items sit inside

`docs/sprint-pilot-gap-log-2026-07-28.md` closed one half of a two-part
question and left the other half explicitly routed here:

- **"Furina is stronger than her sim rows say" — SUPPORTED**, widely. Every
  Furina row on record is a floor.
- **"The saturated Encore runway is a pilot artifact" — NOT SUPPORTED.** The
  stoker pilot more than doubles her winrate *while the stage stays dry almost
  half the time* (dry 46.9% vs greedy 49.8%; R-A required it below ~25%), and
  the `runway5+` column — the direct analogue of the bar a playtester reads as
  "I am not going to run out" — sits at **11–13% under every pilot including
  the best one**. The sim does not produce a saturated runway for anybody.

> **The co-op seat is the leading remaining hypothesis for the saturation
> divergence**, and it "routes to a FUTURE brief" that did not exist. This is
> that brief for the *charter* half of the question; the measurement half
> still has nowhere to live, because the sim models one seat.

Why this matters to both items: if the second seat is what makes Furina's
Encore runway read as full at the table, then **both charter items are levers
on the exact mechanism nobody can measure** — item 1 couples her generation to
a partner directly, and item 2 couples her multiplier to a partner's hand.
Building either before the seat question is understood means adding a term to
an equation that already disagrees with the table.

**Open question for the pen:** does the Furina playtest deferred by R87 (1) —
whose pre-registered question is *is the pilot better at Salon, or does
everything feed Salon by construction* — get a **co-op arm**? It is the only
instrument that can see a second seat at all, and asking it while a seat is
open costs one session rather than one sprint.
