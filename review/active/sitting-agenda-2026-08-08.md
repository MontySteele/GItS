# Sitting agenda — 2026-08-08

> **Lifecycle: ACTIVE.** This is a walking order, not a register.
> `docs/current/QUEUE.md` stays the single source of truth. Every item below
> points at its QUEUE row. It repeats nothing from that row as fact.
> This packet decides nothing. It recommends nothing on any design, taste or
> money call. It invents no number. Where a number appears, it is quoted from
> the file named beside it, with the same stamp that file gives it.

## Terms used here

Read this once. The rest of the document uses these words without re-explaining
them.

- **Sitting.** One session where you read the material and make the calls.
- **QUEUE row.** A line in `docs/current/QUEUE.md`. Each row is one open
  decision that only you can make.
- **BACKLOG row.** A line in `docs/current/BACKLOG.md`. Those are engineering
  jobs, not decisions. Two items below are BACKLOG-side because they need your
  signature before the work can run.
- **Ratify.** Say "yes, this is now the official version".
- **Countersign.** Your written sign-off on something already drafted.
- **LAW.** `docs/current/LAW.md`. Rules that bind future work. Putting a rule
  "into LAW" makes it binding.
- **The stamp.** A version label like `RT9/D14/P6/C8`. It says which version of
  the game world produced a number. Numbers from different stamps are not
  comparable. `RT9/D14/P6/C8` is the world that ships today.
- **Plan (also "archetype", also "arm").** One way to build a character's deck.
  Furina has three plans: salon, spotlight, fanfare. Kokomi has priest,
  commander, assist, and a generic build.
- **Anchor.** A reference character we measure against. `real_ironclad` and
  `real_silent` are the two real Slay the Spire characters. `ref_ironclad` is a
  reference build of the Ironclad.
- **Floor.** An anchor's winrate used as a "must clear this" line.
- **95% interval.** The range a measured percentage could really be, given the
  sample size. Two intervals that do not overlap mean the difference is real at
  this sample size. Two that overlap mean we cannot tell them apart.
- **Structure HELD.** The shape of a result survived a world change: the same
  things are above and below each other, even though the raw percentages moved.
- **Fence.** One decision blocks another. The fenced decision cannot be taken
  first.
- **Packet.** A review document under `review/active/` that gathers the evidence
  for a decision.
- **Paste-ready.** The content is fully drafted and machine-checked. If you
  approve it, it can go into the sheets with no further authoring.
- **Pre-registration.** Writing down what an experiment will measure, and what
  we predict, *before* running it. Required by `docs/current/EXPERIMENTS.md`.
- **Sheet.** One of the `docs/*-cards.yaml` / `*-upgrades.yaml` /
  `*-companions.yaml` files. These are the card data.
- **Contact sheet.** A generated page of candidate art images, so you can pick
  by eye.
- **Rank 1.** The chosen art candidate for a card. Nothing ships until
  something is ranked 1.

---

## What this is

This is one consolidated sitting. It covers all 35 QUEUE rows, plus one
BACKLOG-side countersign (`EB-17p`). Items are sorted into what can close today
and what cannot. The order keeps related material in front of you at the same
time.

Every fresh number quoted here comes from the world stamped **`RT9/D14/P6/C8`**.
All of it was measured **after** two instrument fixes:

- `EB-57` — the reaction amplification counter was re-settled as realized
  uplift.
- `EB-58` — aura-uptime intervals are now cut off when the target dies.

## State of play

Three QUEUE rows quoted percentages from a world two stamp boundaries back.
Those numbers were declared not comparable to today's world. So they were
re-read this morning under the current world, with the same sample size, the
same seed and the same recipe. The re-read is
`review/active/sitting-reads-2026-08-08.md`.

**All three structures HELD.** In plain terms:

- Furina's salon plan still separates from spotlight and fanfare, with no
  interval overlap. Fanfare still overlaps the `real_silent` floor.
- All three Kokomi plans still sit below `real_ironclad`. The assist plan sits
  below even `real_silent`.
- Kokomi's meter-20 act-1 band membership is intact. The priest plan moved
  *into* the band.

The raw percentages fell across the boundary. The two reference anchors fell
with them.

**One ordering fact MOVED.** On the prior table `furina/salon` sat **above**
`real_ironclad` (11.20% vs 8.53%). On the fresh read it sits **below** it
(4.70% [4.00, 5.52] vs 6.13% [5.33, 7.05]), with no interval overlap. The whole
Furina table fell under the current world. Nothing else about any row's
structural claim changed.

**Counts:** 33 items ready to close. 3 items explicitly out.

---

# A. Ready now

## A1 — measurement-backed calls

Take these while the fresh numbers are open.

Order note: `S4-G5` / `B-G1` runs first. `S4-G7` is fenced behind it and cannot
be taken until `S4-G5` is settled.

### 1. `S4-G5` / `B-G1` — the Fanfare axis

**What you are deciding.** What to do with the Fanfare axis of the seven-axis
scorecard, axis by axis. The other six axes are already closed as
reportable-only. As part of the same call, say **which of the seven axes A1–A7
"Fanfare axis" actually names** — that was never written down anywhere.

**What to look at.** The charter, §4 and §7:
`git show pre-simplification-2026-08-06:docs/axis-validity-session-charter.md`

**What it unblocks.** It unfences item 2 (`S4-G7`) and the fanfare STOP, through
the R107/F1 fence.

### 2. `S4-G7` — Furina: three plans or one

**What you are deciding.** Whether Furina keeps three viable plans, or only one,
with the other two declared dead archetypes.

**What to look at.** The fresh twelve-arm read at
`review/active/sitting-reads-2026-08-08.md` §1. The prior table is
`docs/current/roster/roster-anchor-v14-v6-2026-08-06.md`.

**What moved.** Structure HELD. Fresh numbers: salon **4.70%** [4.00, 5.52],
spotlight **1.50%** [1.12, 2.00], fanfare **1.30%** [0.95, 1.77]. Fanfare still
overlaps the `real_silent` floor at **1.37%** [1.01, 1.85]. Salon now sits
**below** `real_ironclad` at 6.13% [5.33, 7.05]. On the prior table salon sat
above it, at 11.20%.

**Note.** This call is fenced behind item 1.

### 3. `S4-G13` — Kokomi below the Ironclad floor

**What you are deciding.** Two things. First, pick one of three levers to lift
Kokomi, who measures below the Ironclad-anchored floor. Code can build any of
the three, and can pull none of them. Second, the `NT-G5` fork: is the Neap Tide
card weak, or is it fine?

**What to look at.** `review/active/sitting-reads-2026-08-08.md` §2.

**What moved.** Structure HELD. Fresh numbers: priest **1.10%** [0.78, 1.54],
commander **2.20%** [1.73, 2.79], assist **0.57%** [0.35, 0.91], against
`real_ironclad` 6.13% [5.33, 7.05]. Assist is still below `real_silent`, with no
overlap. Act-1 clear rates are within a point of the prior read on all three
plans: 42.20 / 51.83 / 35.37.

**Note.** The `NT-G5` half cannot close today. Its only accepted input is
`OT-1`, and `OT-1` is not ready. See section B.

### 4. `M9` — Kokomi meter 20, and the Garment watch

**What you are deciding.** Two leftovers from the Kokomi v0.4 work. First,
ratify the meter-20 number on the 500-run confirm. Second, keep or drop the
commander Garment-uptime watch.

**What to look at.** `review/active/sitting-reads-2026-08-08.md` §3. The source
report is `git show pre-simplification-2026-08-06:docs/archive/kokomi-v0.4-report.md`
§6.

**What moved.** Structure HELD. The priest plan moved **into** the 35–50% band,
rising from 30% to 41%. Commander sits at 50%, the upper edge of the band. Every
run winrate is 2.2% or lower.

**One thing to know before you ratify.** The old comparison column in §2.3, "vs
W1 baseline", is dead. It was not replaced. Rebuilding it, or testing meter 15
instead, would mean editing `burst_max` in the ratified `kokomi.yaml`. That is a
content change, not a measurement, so it was not done. This means the trade that
§6 ask 2 names cannot be re-read. Ratifying against this read is therefore
one-sided. Whether that matters is your call.

### 5. `M5` — the A6 debuff term

**What you are deciding.** Whether the A6 instrument's debuff term is
mis-anchored. You either amend the instrument or accept it as is. This is the
only live line left in `M5`. Routes (a) and (c) were closed by the
descriptive-only axis ruling. Either answer has zero balance consequence.

**What to look at.** The read is written into the QUEUE row itself, stamped
`A6v2 · RT9/D14/P6/C8 · fights=1000 · seed=20260719`.

**What moved.** Archetype median 3.5, against a declared 4.2. The median is
numerically unchanged but recomposed: salon 3.53, spotlight 4.19, fanfare 3.24.
The debuff term reads 0.05–0.46 across all three archetype decks, against a 0.90
anchor baseline. The call is unblocked.

### 6. `Q-C` — payoff-reach predictions, plus the `EB-63` gate question

**What you are deciding.** Three things, in one commit, before any sprint number
is read:

1. Ratify, amend or reject the payoff rubric in §2 of the census. This includes
   one open choice: LOOSE or STRICT attribution for pools P2 and P3.
2. Confirm or overrule the §6.1 exclusion of second-hand mentions.
3. Say whether `EB-63` gates the aim. `EB-63` is an extraction change that would
   attribute the 24 payoff cards the census currently cannot place. Right now 60%
   of payoff-shaped cards sit unattributed. Either `EB-63` runs first, or the aim
   is taken against a floor with those cards still unattributed.

Then aim each roster archetype high, medium or low inside the census bands. That
aim **is** the `Q-C` answer. Also state a direction and a threshold for Q-A and
Q-B.

**What to look at.** `review/active/payoff-census-2026-08-08.md`, whose §7 states
the three asks. Also `review/active/payoff-reach-reregistration.md` §5.

**What it unblocks.** See section C.

---

## A2 — countersigns

### 7. `EB-17p` — the force-first-copy experiment

This is a BACKLOG row, carried here because it needs your signature.

**What you are deciding.** Countersign the pre-registration for the
force-first-copy paired-winrate experiment. That experiment runs two decks on
the same seeds: one with a chosen card forced in, one without. Your countersign
also has to settle three things the draft leaves open:

- which filler card acts as the negative control,
- the value of `N` and the cost ceiling,
- the per-card predictions, which get their own commit before any run.

**What to look at.** `review/active/eb17p-registration-draft-2026-08-08.md`, and
the `EB-17p` row in BACKLOG.

**Note.** The mechanism is settled as deck-injection at run start. Because of
that, the R121 `DRAFTER 14` pin does not gate this experiment.

**What it unblocks.** The engineering prerequisites in packet §10 land, then the
run executes.

### 8. `N + O countersign` — the reactions corpus

**What you are deciding.** Countersign the PROVISIONAL banner on the reactions
corpus. This is the countersign that follows the R101 precedent. It is the only
open item left in the two audit ledgers.

**What to look at.**
`git show pre-simplification-2026-08-06:docs/archive/lore-fidelity-audit-2026-08-05.md`
and `…/instrument-redteam-2026-08-05.md`.

**Note.** The top-5 triage of those ledgers already ran, as `EB-51`. It landed
`EB-57` through `EB-62`, plus the titles row at item 14 below.

**What it unblocks.** It closes the last open item in both audit ledgers.

---

## A3 — paste-ready ratifications

Both packets below are fully drafted and machine-checked. Neither is in the
measured pool today.

### 9. `EB-22` — the Kokomi pool fill

**What you are deciding.** RATIFY, REVISE or DROP a 15-card fill for Kokomi's
card pool. The draft is assist-weighted: 10 of the 15 cards serve the assist
plan. It is machine-checked and paste-ready. There are also four sub-decisions
named in the brief.

**What to look at.**
`git show pre-simplification-2026-08-06:docs/archive/brief-kokomi-pool-fill.md`

**What it unblocks.** Sheet edits to `docs/kokomi-cards.yaml` and
`docs/kokomi-upgrades.yaml`, then codegen.

### 10. `EB-26` — the lesser ward card

**What you are deciding.** RATIFY, REVISE or DROP `watch_of_the_shallows`. It is
an uncommon 1-cost card granting `prevent_exhaust_ward` 3, with a complete
upgrade delta. It passes every sheet gate green against a shadow tree. It is
**not** in the live sheet. There are also seven sub-decisions.

**What to look at.** `review/active/eb26-lesser-ward-draft.md` §5. The seven
sub-decisions are: D1 the name, D2 `max_stacks`, D3 magnitude and cost, D4 the
lane, D5 the tempo band, D6 the upgrade slope, D7 scope — meaning re-baseline
now or wait.

**Note.** P3 is still unowned, and it sits outside `EB-26`'s scope as the packet
is written.

**What it unblocks.** Sheet edits, codegen, and whatever re-measurement D7(a)
decides.

---

## A4 — money

### 11. `EB-42q` — the Spine licence, $379

**What you are deciding.** Approve or decline $379 for a Spine licence. The
alternative is to stay on the Path C layered approach, which already ships, and
put the investment into Godot-native rigs instead.

**What to look at.** `tools/skeleton2d_spike/PROBE-2026-08-08.md`.

**What the probe found.** The one remaining unknown was whether the rig can sit
in live combat. That is answered **YES on every leg**: it seats as creature
Visuals, the RIDs are valid under the real renderer, the AnimationTree drives
the bones, the deformation reaches the screen, and no engine error came from the
rig.

**What is still open.** Nothing engineering-side is left to wait for. But the
probe rig is spike-grade art. It proves nothing about how the motion actually
looks. That half is your call.

**What it unblocks.** Either a purchase, or Path C layered stays the shipped
fallback and Godot-native rig work is what gets invested in.

### 12. `X10` — pricing Gorou's Heart of the Clan

**What you are deciding.** Price the `gorou_heart_of_the_clan` power
adjustment. The adjustment is a CANDIDATE and is explicitly not ratified. Note
that the 81-hit exploit lines target the power itself, not its price.

**What to look at.**
`git show pre-simplification-2026-08-06:docs/dockets/companion-pricing.md` §1,
and `…/review/redteam/exploit-ledger.md` entry X10.

### 13. `S4-G10` — the companion-shop close-out session

**What you are deciding.** This is a session, not a single call. It covers:

- grading `SHOP-P1` through `SHOP-P3`,
- settling whether money is ever really the constraint,
- the 1.15× surcharge,
- Track A pool migration,
- R60 phase-2 fantasy-leak grading,
- whether shop slot 2 should carry a rarity floor at all,
- the §7.7 Track D fallback taste check, merged in from `M11`.

**What to look at.** R60 and R63, and principles §4.7 through the row's
provenance.

**Note.** The slot-2 item wants empirical data on how often Commons are offered,
picked and skipped. The row records that data as wanted, not as held. So you do
not have it.

**What it unblocks.** The session consumes the `EB-33` / `EB-34` / `EB-35`
repricing exhibits, which are filed as inputs waiting for it.

---

## A5 — taste batches

### 14. `N3 + N4 titles` — six companion card titles

**What you are deciding.** Six shipped companion cards carry titles that name
talents Genshin does not have. For each one: rename it to the canon name, ratify
it as authored flavor, or amend it case by case.

**What to look at.** All six were re-verified as still shipped on 2026-08-08, in
`docs/{fontaine,mondstadt,inazuma}-companions.yaml` and in the matching title
strings in `Cards/Generated/*.cs`.

**Why this is a call and not a cleanup.** A rename moves card ids, art keys and
the C# roster.

### 15. `S4-G11` — read card names and lore by eye

**What you are deciding.** Read card names and lore text yourself, before they
ship. This covers the R29d Furina pass, Kokomi's 20 authored-but-unaudited fill
cards, and kickoff ask 10. This was ruled to have no substitute.

**What to look at.**
`git show pre-simplification-2026-08-06:tier0/DECISIONS.md` entry 75, plus R29d.

### 16. `S4-G12` / `CC-G1` / `CC-G2` — art eyes-on and screenshots

**What you are deciding.** Two eyes-on passes. First, look at the art contact
sheet: re-hunt candidates including `grand_gala`, and confirm the
`standing_room_only` crop by eye. Second, review in-game screenshots of the
twelve Curtain Call cards and the A0 smoke run.

**What to look at.** The frozen bundle is
`git show pre-simplification-2026-08-06:docs/archive/g12-review-2026-08-05.md`.
The sheet was regenerated in the primary checkout at
`art/contact_sheet_eb54_s4g12.html`, with 6 gate rows and 25 candidates
(`review/active/art-runs-2026-08-08.md` §3).

**Note.** The `standing_room_only` overturn has already been executed.
`Opera Epiclese.png` is now its rank 1. That is what left `grand_gala` with no
pick.

**What it unblocks.** See the art entry in section C.

### 17. `S4-G17` — three running-game looks

**What you are deciding.** Taste calls on three looks in the running game: the
`AS2-D5` salon look, and `AS2-B5` motion and facing. The `AS2-E2` icon picks are
handled canonically in the Art debt row, item 20.

**What to look at.** Captures are staged. The manifest is
`review/active/livegame-captures-2026-08-08.md`, §1 for B5 and §2 for D5. The
files sit under the gitignored `art/eb52_captures/`, from package `0.2-589`.

**Note.** The row's own status says urgency is reduced.

### 18. `S4-G20` — a bundle of small leftovers

**What you are deciding.** Four small things:

- Accept or fix the sim-versus-C# salon RNG divergence.
- One taste pass: is `kaboom` the same as `spark_knight_style`?
- Two infra toggles: branch protection and `gh`; and the manifest MAJOR bump,
  which is dormant by design.

**What to look at.** The QUEUE row, plus backlog §1 P3-cluster and §5.

### 19. `S8 + S10 galleries` — potions, relics and enemies

**What you are deciding.** Two taste calls. First, eight flagged potions and
relics (S8). Second, for each enemy, RESKIN or REDESIGN (S10).

**What to look at.** `docs/current/dossiers/content/potion-relic-conversion-gallery.md`
and `docs/current/dossiers/remap/reskin-gallery.md`. Both are in HEAD.

### 20. `Art debt` — the art picks

**What you are deciding.** The art picks. Specifically: Kokomi's 58 faces and 15
companions, the `AS2-E2` icons, `grand_gala`, the two `ART-L12` duplicate pairs,
the three EB-36 placeholder cards, `curtain_cue`, `breathless`, A7, and six
Curtain Call power sigils.

**Plus one one-line answer.** Which **three** re-hunt rows does the `S4-G12` row
mean? The frozen bundle describes four REHUNT rows plus the overturn. The sheet
shows all six rather than guessing.

**What to look at.** `review/active/art-runs-2026-08-08.md`.

**What the production run delivered.** `EB-54` production is DONE: 37 candidate
rows and 34 new PNGs. Everything is **rank 2 or lower by design**, so nothing
shipped a pick. Per-run contact sheets are named in that packet, and are
gitignored in the primary checkout.

**Three facts the packet records.**

- If you promote any of the seven power sigils to rank 1, the same change must
  delete that sigil's `$pckDeferred` entry. Otherwise S12 fails.
- `docs/art-claimed-sources.tsv` reads **271 claimed / 180 free**. Three of the
  eight runs had to reach outside the free Furina pool to produce a third
  candidate.
- The phrase "four missing Kokomi portraits" is **stale, not blocked**.
  `art_coverage` bills Kokomi at 61/61 and Inazuma at 15/15.

### 21. `M8` — three Kokomi card-art rulings

**What you are deciding.** Three rulings:

- The crop-reuse budget. Give a number, or say eyes-on per card.
- Whether Watatsumi and shrine environment art counts as a card face.
- Whether to hand-crop the banned `Character Details 1` for a Rare.

**What to look at.** `docs/current/art/kokomi-art-pass-requirements.md` §6, in
HEAD.

### 22. `M10` — Fontaine Rares close-out

**What you are deciding.** Four items:

- Companion art picks for Navia, Clorinde, Neuvillette and Arlecchino.
- The v1.7 lore and naming eyes-on audit. This one cannot be delegated.
- The C2 grading countersign.
- Close-out ratification.

Neuvillette's "different facet" question is parked with these.

**What to look at.** The QUEUE row, plus
`git show aa09b97:docs/current/backlog/missed-requirements.md` §4.4.

---

## A6 — structural rulings

### 23. `S4-G6` — Kokomi's HP stability band

**What you are deciding.** Declare Kokomi's HP stability band. You must declare
it from design intent, before her confirmatory playtest. It may not be revised
against that playtest afterwards.

**What to look at.** `DEC-D5` clauses 2–4. The band is re-anchored to the
post-rework build.

**What it unblocks.** Her protocol playtest. See section C for the full chain.

### 24. `S4-G18` — the archetype-size band

**What you are deciding.** Klee's three archetypes carry 28, 22 and 14 cards.
The constitution names a 15–20 band, but that band is absent from LAW. Choose
one of three branches:

- restore the band to LAW as written,
- restore it amended, for example to the shipped 28/22/14,
- rule that it was never law.

The branch choice and the count question are one call.

**What to look at.** The QUEUE row. Counts were recounted on 2026-08-07:
28/22/14.

### 25. `S4-G19` — Sly unification

**What you are deciding.** Two mechanics do nearly the same thing. Say whether
they become one.

**What to look at.**
`git show pre-simplification-2026-08-06:docs/archive/tech-debt-audit-2026-07-26.md`
§5.

### 26. `M7` — the Enchant op

**What you are deciding.** Build the Enchant op, or leave the fields as they
are.

**What to look at.** `docs/current/dossiers/content/event-conversion-gallery.md`
in HEAD. It carries a live `FLAG — [USER] decision needed` on Stone of All Time.

**Background.** R82 settled only the data-model half of this. The op itself is
still unbuilt.

### 27. `M12(a)` — convergence-cell membership

**What you are deciding.** Three different places say how many cards belong in
the convergence cell: three, four, or two. Rule which statement governs, before
the cell is built.

**What to look at.** `docs/furina-cards.yaml:127`, `:391–395` and `:647`. The
2026-08-06 Class-P re-attestation marked this DOWNGRADED TO DOUBT and never
closed it.

**Note.** Sub-item (b) was found PREMISE FALSE. It needs nothing from you.

### 28. `M13` — the route regret margin

**What you are deciding.** Rule `ROUTE_REGRET_MARGIN`, and its twin, the `+ 1.0`
in `draft_regret`. Or, instead of ruling it, pre-register a measurement for it.

**What to look at.** The margin note in `tier05/run_metrics.py`, in HEAD.

**Why it matters.** Until this is settled, only the margin-free reads are
quotable.

### 29. `shared_billing` — cost upgrades on Commons

**What you are deciding.** Either rule "no cost upgrades on Commons" into LAW,
in which case the card needs a re-price, or allow the card as it is.

**What to look at.** The QUEUE row. The "delta-grammar convention" the row cites
exists in no LAW, and nowhere at the tag beyond the row itself. Both engines
currently ship the card.

### 30. `EB-27p` — the personal-pool companion sweep

**What you are deciding.** Settle, for the whole class of personal-pool
companion cards, how they enter a run. This is a design-level call and comes
ahead of placing any single card.

**What to look at.** The QUEUE row. It lists three inherited options:

- a guaranteed fixed floor,
- entry through the act-1 event pool,
- a run-start Neow-shaped offer.

The row also records that the old "node 2" anchor is dead, and that LAW and the
spec are in tension on this.

**Note.** Nothing is being built while the sweep is pending.

### 31. klee-rework `X7` — Klee spark-economy violations

**What you are deciding.** Rule on three cards that violate the Klee spark
economy: `skip_and_hop`, `sparkly_treasure` and `crackle`. Rule them on R109's
disjunction.

**What to look at.** `dockets/klee-rework`.

### 32. klee-rework `X8` — two Common bomb-damage writers

**What you are deciding.** Promote, re-price or accept two non-exhaust
**Common** cards that write bomb damage: `chain_fuse` and
`careful_arrangement`.

**What to look at.** `dockets/klee-rework` §3.

**Note.** The audit already ran. It falsified the premise that these would be
"fine at higher rarity".

### 33. kokomi-workshop `X9` — the Kokomi charge bank

**What you are deciding.** The Kokomi charge bank. The note on it reads
"probably too strong, parse carefully". This is the next kit workshop.

**What to look at.** `dockets/kokomi-workshop`.

---

# B. Not ready, or explicitly out

Four items cannot close at this sitting.

### `S4-G14` / `OT-1` — the Kokomi protocol playtest

This needs table time. It is blocked on two things at once: `S4-G6` (item 23
above), and the `EB-53` N1 attribution pass. The pass has two engineering legs.
Both are built, but neither is run-verified. So the playtest cannot be asked for
yet.

### `EB-53` capture review — BACKLOG side

**The captures have not been taken.**
`review/active/n1-kokomi-burst-legs-2026-08-08.md` §6 lists nine owed captures,
C1 through C9. It states that the game was owned by another agent this session,
so `deploy.ps1` was never invoked and the game was never launched. The build,
deploy and `godot.log` verification steps are owed first.

The **R89 half** of `EB-53` is also out. It is a countersign, but there is no
draft in HEAD to countersign. The BACKLOG row names "the R89 draft" without
giving a path.

Its Klee bomb-variety leg is rework-scoped design, and is untouched by design.

### `M1` — Furina's co-op Fanfare mechanic

BUILD or WAIVE. No packet was assembled for it this pass. The row also records
that the chartered mechanism cites the `encore_gained` leg, which Track A
deleted in both engines. So a BUILD here is a re-specification, not an
implementation.

### `M2` — passing a Spotlight between co-op players

BUILD or WAIVE. No packet was assembled this pass.

### Also carried, but blocking nothing above

`EB-52`(a) is the fourth Fanfare evidence shape. It is still owed. Its obstacle
is acquisition, not instrumentation — see `docs/current/BACKLOG.md` `EB-52`. It
is not a QUEUE row and it is not on this agenda.

---

# C. What unblocks on your signatures

- **`EB-17p` countersign.** The experiment's engineering prerequisites, in
  packet §10, land. Then the run executes. The `DRAFTER 14` pin does not gate
  it.
- **`Q-C` — ratify, confirm, answer `EB-63`, then aim.** R137's six-step order
  proceeds. `EB-63`, the extraction change that attributes the 24 unattributed
  payoff cards, either goes first or is deferred. `EB-43` / D15 remains held as
  step (5), after blind-first grading.
- **`S4-G6`.** Kokomi's protocol playtest (`S4-G14` / `OT-1`) becomes askable,
  but only once `EB-53` also run-verifies. `OT-1` is in turn the only accepted
  input to the `NT-G5` fork inside `S4-G13`.
- **`EB-22` and `EB-26` ratify.** Sheet edits to `docs/kokomi-cards.yaml` and
  `docs/kokomi-upgrades.yaml`, then codegen, then whatever re-measurement
  `EB-26` D7(a) decides. Both packets are paste-ready. Neither is in the
  measured pool today.
- **`S4-G10` session.** It consumes the `EB-33` / `EB-34` / `EB-35` repricing
  exhibits, which are filed as inputs waiting for that session.
- **`Art debt` and `S4-G12` picks.** `art_process` promotions to rank 1 can
  happen. The four `art_coverage` misses can close: `grand_gala`, `confiscated`,
  `spotlight_center_stage`, `spotlight_guest_cast`. Each power-sigil promotion
  must delete its `$pckDeferred` entry in the same change.
- **`EB-42q`.** Either a purchase, or Path C layered stays the shipped fallback
  and Godot-native rig work is what gets invested in.
- **`S4-G5` / `B-G1`.** It unfences `S4-G7` and the fanfare STOP, through the
  R107/F1 fence.
- **`N + O countersign`.** It closes the last open item in both audit ledgers.
