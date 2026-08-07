# S4-G9 ratification packet — ratify-by-exception (prepared 2026-08-07)

One page per item: the shipped PROPOSED value, its support, what moves if
you change it, and a recommendation. **Everything unvetoed ratifies in one
commit**; veto or adjust by item number. Items the row named that now live
elsewhere are listed at the bottom as exclusions, not silently dropped.

Retrieval note: several primary sources retired from HEAD at the
simplification; each is cited at its git retrieval point. The QUEUE row's
own provenance ("user-queue §2; backlog §3 item 9") points at deleted
paths — this packet is the substance behind the umbrella row.

---

## 1. Fanfare Cap grammar magnitudes — `+5` common/uncommon, `+8` rare

Shipped across 17 rows (`raise_fanfare_cap` 5/8; `gain_fanfare_floor` 8,
one 15 on `the_sea_is_my_stage`). Support: they "restore the retired
invisible rule as printed text" — the old automatic Power grant the rework
deleted for being unreadable. **Adverse evidence, on the record:**
read-at-cap measured **under 1% under every pilot** (`effects.py`
comment), so a cap-only card is close to inert at current constants.
**Recommend: ratify the magnitudes** — the inertness is a property of the
cap constant and the meter economy, not of the per-card numbers, and
repricing 17 rows against a constants question would aim at the wrong
knob. Attach the <1% finding to the D8/Fanfare instrument set instead.

## 2. Track C.1 — `graceful_retreat`: Spend 5 Encore → 10 Block, Retain (+4 on upgrade)

Support: the 2:1 rate is priced against the triple payment (Encore is
deferred HP + a Fanfare leg + the spend-draw window), not against Block
alone; the retired rider fired ~3%. **Recommend: ratify.**

## 3. Track C.2 — `the_final_verdict`: crash X = 30 (upgrade → 20)

Support: her meter sits ~20 at read (pilot-gap P3), so one cast typically
buries the floor below zero and a second cast per combat is genuinely bad
— the number does the design's job. The old card measured fire-rate 0%.
**Recommend: ratify.**

## 4. Track C.3 — `blocking_notes`: 5 Block, +2 per Companion played (+3 upgraded)

The invisible ~1% rider became an aimable slope. (This is EB-24's second
"dead rider" — the zero measured the retired text; see
`eb24-dead-riders-worksheet.md`.) **Recommend: ratify.**

## 5. Negative-floor semantics — readers CLAMP at zero

RULED: the floor may go negative, decay clamps to it, generation climbs
out. PROPOSED half: every reader (`resources.readable`) clamps at zero —
a negative meter turns effects OFF rather than inverting them. The
harsher inversion is a one-line flip if wanted. **Recommend: ratify the
clamp.** The sheet's own sentence carries it: negative member ticks
chipping her own stage would read as a bug, not a cost. Five reader call
sites and a parametrized test pin the clamp today.

## 6. Conversion clauses — Compensation Track 2, the `1_per_4_fanfare` commons tier

Blind Encore generators become meter-readers at a fixed commons rate:
`applause_line` (3 + 1/4F), `held_breath` (4 + 1/4F), `suffering_for_art`
(0 + 1/4F), `an_invitation` (3 + 1/4F), `breathless` (spend 4 → 9
damage), and the starter `aria_of_recompense` (0 + 1/4F). Support: 8 of
the archetype's 10 meter-readers were RARE — "that is the 0.5% winrate
and the 44.7% act-1 in one sentence"; 1_per_4 is a tier rule so commons
can't devalue the payoff slots' 1_per_2. **Recommend: ratify the tier
rule and five of the six bodies.** The one to eye separately is **Track
2.4, the starter** — the sheet's own red-pen warning says it is "the
single number in this sprint that cannot be aimed at one archetype." If
you veto exactly one thing in this packet, that's the candidate; a veto
there costs the track little (the other five carry the diagnosis).

## 7. `lasting_impression` — NOT a ratify: the card needs a body

The track's own text: "the single biggest individual loss… +5 headroom on
a ceiling nothing reaches… close to a deletion of this card's scaling
line. What this card needs is a body, and that is a ruling."
Compensation deliberately shipped no reprice because every candidate was
either more blind Encore or a reader clause (a redesign, out of scope).
**Recommend: commission the body** — a small red-pen worksheet proposing
a reader clause for the pool's declared common floor source — rather than
ratifying the current shape as final. (Name is separately pending the
lore audit.)

## 8. D6 bow probe — `take_your_bow`: cost 0, uncommon, no rider

Track D shipped ONE card, not a family, as the instrument for deliberate-
bow design space; "cost 0 is the proposal and the risk… the number most
likely to come back wrong"; no rider so a null result is attributable.
**Recommend: ratify as the probe, explicitly probe-not-family, with the
next playtest named as its measurement** — which is what the sheet
already says it is.

## 9. `kurages_oath` = 12

Measured, not reasoned: ward 5 was a trap pick (3.8% vs 5.8% no-card);
the 500-run bracket lands 12 at 6.2%/5.8%. Your 2026-07-26 "feels too
strong" flag is preserved and re-filed on the Kokomi playtest protocol as
**first knob back** (R107/F9), where the one instrument that can judge it
lives. The ward×pulse coupling pin guards silent repricing.
**Recommend: ratify 12 with the flag standing.**

## 10. Kurage pulse ×3 (ruled 2; E1 fired the pre-committed ×3 fallback)

The stamp records the landed value on purpose ("write the landed value,
not the ruled one" — ×2 shipped in no build and no measurement cell). At
×3 the payoff hierarchy is upright; the open question playtest three owns
is the **pair** (×3 with `before_sun_and_moon`'s uncapped +1/copy, which
puts a basic above the Rare readers at ×5). **Recommend: ratify ×3 as
the standing value and leave the pair question with playtest three.**
Moving to 2 now re-opens a CONSTANTS window for no measurement gain.

## 11. Curtain Call follow-on: the uptime residual

Prediction 7 failed post-shrink: salon −5.2% (in bound), spotlight
−11.5%, fanfare −17.3% (out). The session's three options: accept the new
baseline / revert the RATIFIED `standing_room_only` retype / schedule
application elsewhere. **Recommend: accept the new baseline.** Salon —
the declared primary engine — is in bound, and item 6 of this packet IS
the "application elsewhere" for fanfare, already in flight; reverting a
ratified retype to chase a residual the compensation tracks exist to
close would pay twice.

## 12. Curtain Call follow-on: the salon trim band

The pre-registered trigger (≥16% routes the trim experiment) did not fire
(15.0 / 13.4 measured). **Recommend: ratify the 12.0–15.0% band and do
not order the trim** — the registration's own rule says no, and ordering
it anyway would re-open the pool R85 just reshaped.

## 13. `scattering_spray` "7→6" — a comment correction, retroactive blessing

Not a Klee card and not a damage change: it is Kokomi's, and the 7→6 is a
sibling-number correction inside its comment (R77 moved `surging_shoal`
7→6; the stale quote was corrected and lint-marked in the same sweep — a
second correction beyond that sweep's countersign, flagged for red pen by
the sweep itself). Zero mechanical stakes; the question is authority.
**Recommend: ratify retroactively.** Reverting would re-certify a stale
number under a lint-ok marker — strictly worse than either honest state.

## 14. Spotlight icons — ten distinct vs one family mark

Shipped ten-distinct on the sprint-1 legibility diagnosis (failures came
from indistinctness); the counter-case ("ten marks are noise at badge
size") is real but **unmeasured on either side**, and two of the ten
still render the BETA placeholder (EB-36). One-line change either way;
art-side only. **Recommend: keep ten icons** (the only evidence in hand
supports it) **and rule before `S4-G17`'s icon picks execute** — deciding
after strands the hunted picks.

## 15. Klee dead-card reworks — `study_of_explosions`, `secret_stash`

The two proposed reworks that never landed and were never waived (the
other two dead cards landed in altered form). Measured: both 0% pick rate
in generic AND their own archetype; the rework sim resurrects them to
13–43% picked, **winrate-neutral (±1%)** — they were non-options, not
drags, so this buys live choices, not power. Proposed shapes (DRAFT):
`study_of_explosions` → 4 damage random + 5 Burst (0-cost ping that
charges the Burst); `secret_stash` → 8 damage ALL + add 2 (the value
engine gets immediate board impact). The review floats sizing them BIGGER
for real tempo; that larger sizing is NOT part of this recommendation.
**Recommend: ratify the DRAFT shapes at the modest numbers.** Upgrade
deltas re-derive against the new bodies; boundary vs X7/X8 is clean (the
retired docket's own scope note assigns these two here).

---

## Exclusions (named by the row, owned elsewhere)

- **Name audit** (Curtain Call follow-on 1) → its own QUEUE row `S4-G11`.
- **Payoff-reach follow-on** (Curtain Call follow-on 3) → escalated into
  the countersigned re-registration and its six-step order (`Q-C`);
  nothing here may touch it.

*Provenance: S4-G9 (QUEUE); three-agent source sweep 2026-08-07; retired
sources at `git show 39078372:` / `9ab7ba26:` / `762e94d^:` as cited by
the underlying reports.*
