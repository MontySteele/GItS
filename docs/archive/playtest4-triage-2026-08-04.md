> **MOVED 2026-08-06 — Clear the Stage, Track R-B (charter R119, rail 1).**
> Old path: `docs/playtest4-triage-2026-08-04.md` — new path: `docs/archive/playtest4-triage-2026-08-04.md`.
> Verbatim move: everything below this banner is byte-identical to the
> pre-move file. Citers repointed in the move commit; see
> `review/stage-clear/rb-move-manifest.tsv`.

# Playtest 4 triage — mapping the co-op weekend onto the register (2026-08-04)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Source: `docs/playtest4-notes-2026-08-04.md` (raw input), against the register
`docs/backlog-2026-07-29.md`. Unlike the playtest-2 triage, **nothing here is
ruled** — this pass sorts findings into closed / unblocked / new / unmoved and
says which owner each needs. Register entries retired by this doc are struck
through there with a reference here, per the register's own rule.

---

## 1. Closed by this playtest

- **Hover targets vs targeting arrows** — no issues across three seats, two of
  them first-time pilots. Closed after going unanswered for two cycles
  (playtest 3 §"What this leaves open").
- **Kokomi priority check 3** ("boots and reaches a fight at all",
  `open-playtest-items.md` §1) — three acts on her own shell, no crash. The
  eight character-shell surfaces implicitly survived first contact; the §2.2
  *aesthetic* review ask (composition, head-crop centring, tide wipe) was not
  performed and stays open as a look item.
- **First play-derived evidence for the `29f5ce6` bug pass in co-op** — no
  black screens, no desync, no anchor-sweep sightings across a full
  three-seat run. The pass's own log said "nothing is play-verified"; this is
  the first run that could have falsified it and didn't. (Courtroom Drama's
  per-dealer window got its first possible exercise; no one-card-did-nothing
  reports.)

## 2. Unblocked — the R87 deferral is satisfied

R87 deferred ruling-queue items **1–3** (Furina strength lever + legibility,
the dead-archetype question, the Salon leak lever) pending the Furina
playtest, with the gating question *"pilot-skill or by-construction?"*
Playtest 4 answers **by construction**, with a mechanism: the game demands
upfront numbers early and multipliers late; Fanfare supplies the inverse
(notes §3). The sim's n=3000 concurrence — fanfare 2.10% ≡ `real_silent`
2.10% — means table and sim now agree from independent directions.

Consequence for the ruling sitting: item 2 (does Furina get three plans or
one?) is probably not a *tuning* question. A flat-add resource cannot be
number-tuned into matching an inverted demand curve; the live options are
reshape (move Fanfare's payoff to where its supply is — [USER] already rates
it as block), retime (front-load generation), or fold down to fewer plans.
The lever named in item 1 (`FANFARE_FLOOR_PER_POWER` + the invisible-rule
print-or-remove) should be ruled in the same sitting so the next measurement
is against a ruled build. Items 1–3 + the stability band (item 5) are now one
sitting with everything on the table.

**Owner: [USER], one sitting.** Nothing in this section is workable until it
happens.

## 3. New items

### N1 — End-of-turn attribution pass (cross-character, one pass not three)

The headline ask (notes §1). Pieces already on the register, now consolidated:

| Piece | Where it already lives | Delta from playtest 4 |
|---|---|---|
| Furina summon damage numbers | **R89 draft** (Furina legibility decision record, awaiting countersign) | Asked for by name; countersign is now on the critical path |
| Kokomi Bake-Kurage | nowhere — new | Render the summon entity (art exists: `Bake-Kurage Summon` 420×720) and preview the pulse's damage before end of turn. Gates re-asking Q1/Q4 at all |
| Klee bomb variety | Klee rework slot (ruling queue item 9, "two dead-card reworks") | Direction sharpened: bombs become varied effects, not only delayed damage — rework-scoped, not UI-scoped |
| Burst visibility (all seats) | nowhere — new | Off-seat bursts are invisible inside the same end-of-turn noise; whatever the pass does for summons should carry burst attribution too |

Sprint-shaped with two [USER] touchpoints (R89 countersign; Klee rework is
design). Sequencing note: this pass now sits **ahead of** the corpse-detonation
check and most of the Kokomi protocol, because those need a legible end of
turn to be answerable.

### N2 — The difficulty valley (easy / spike / easy)

New table data the one-seat sim structurally cannot see (notes §2). Half of it
lands on existing register mass — act-1 frontload is the Salon leak (§2 item
3, now unblocked) and the n=3000 act-1-only movement — but the **act-2 spike**
(centipede elite near-wipe) and **act-3 collapse** have no instrument and no
item. Proposed shape, needs [USER] to accept scope: an act-by-act
winrate/damage-taken column in the anchor table (measurement, freely
workable) before any act-2/act-3 tuning is proposed. Not a sprint yet; a
brief at most.

### N3 — Kokomi deck size soft flag

"Normal sized the whole way" from the next seat over (notes §4). LAW 4 is
machine-checked on Commons; the protocol's own worry was the law "satisfied
on paper and defeated by the reward screen." Not actionable on second-hand
data — carried as a standing flag into her graded playtest, where Q6 wants
end-of-act counts.

## 4. Pending items this playtest did NOT advance

Unmoved, restated so the next agenda doesn't re-derive them:

- **Corpse detonation** (~10 s, open since 07-21) — nobody checked; now
  sequenced behind N1 (notes §4 says why).
- **Kokomi Garment tip vs the hit** (priority check 1 / Q3) — nobody checked;
  still the likeliest hidden defect on the board.
- **Q2 counts, Q5 rotation voice, Q7 companion offers** — need her graded
  solo playtest, which remains blocked on the stability-band declaration
  (ruling item 5) and now also wants N1 first.
- **D5 salon capture and B5 deliberate motion judgment** — "not noticed" at
  the table lowers urgency but satisfies neither. Both stay open as look
  items.
- **Furina G1/G2** (`CC-G1`/`CC-G2`) contact-sheet eyes-on and the desk queue generally —
  untouched, as expected.

## 5. Recommended shape for next week (updates the register's)

The register's strategic finding — "another Furina fix pass is not the best
use of next week" — was written when her rulings were parked. Playtest 4
un-parked them, so the order inverts:

1. **[USER] ruling sitting**: R87 items 1–3 with §2's answer in hand, +
   stability band (item 5), + R88/R89 countersigns. One sitting converts the
   largest parked mass on the board.
2. **N1 attribution pass** as the next build sprint — it gates the corpse
   check, the Kokomi protocol, and every future "how much damage was that"
   playtest question.
3. **Kokomi block** (instrument reading + pool fill red-pen,
   `brief-kokomi-pool-fill.md`) toward her graded solo playtest, which N1 and
   the band declaration jointly unblock.
4. N2's act-by-act instrument rides whatever measurement sprint runs next.
