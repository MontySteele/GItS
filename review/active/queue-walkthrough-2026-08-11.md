# Queue walkthrough — 2026-08-11

> **Lifecycle: ACTIVE.** This is a walking order, not a register.
> `docs/current/QUEUE.md` stays the single source of truth. Every item below
> points at its QUEUE row and repeats nothing from that row as fact.
> This packet decides nothing. Where it recommends something, the
> recommendation is labelled and comes from work verified this session. Where
> the call is pure taste, it says so and stays silent.

---

## Terms used here

Read this once. The rest of the document uses these words without explaining
them again.

- **QUEUE row.** A line in `docs/current/QUEUE.md`. Each row is one open
  decision that only you can make.
- **BACKLOG row.** A line in `docs/current/BACKLOG.md`. Those are engineering
  jobs, not decisions.
- **Ratify.** Say "yes, this is now the official version".
- **Countersign.** Your written sign-off on something already drafted.
- **LAW.** `docs/current/LAW.md`. Rules that bind future work.
- **Packet.** A review document under `review/active/` that gathers the
  evidence for one decision.
- **The stamp.** A version label like `RT10/D14/P7/C9`. It says which version
  of the game world produced a number. Numbers from different stamps are not
  comparable. The four letters are: `RT` the run template (map and events),
  `D` the drafter (what picks cards), `P` the policy or pilot (what plays
  them), `C` the balance constants.
- **The world today.** `RT10/D14/P7/C9`. The `P` moved from 6 to 7 this
  morning; see the note under "What changed since the last sitting".
- **The pilot.** The automatic player. It plays the cards the drafter picked.
  It is a stand-in for a person and it is not a good player.
- **The drafter.** The automatic deck-builder. It chooses which cards to take.
- **Pre-registration.** Writing down what an experiment will measure, and what
  you predict, *before* it runs. Required by `docs/current/EXPERIMENTS.md`.
- **Blind grading.** Comparing the result to the prediction without having
  looked at the result first.
- **Sheet.** One of the `docs/*-cards.yaml` / `*-upgrades.yaml` /
  `*-companions.yaml` files. These hold the card data.
- **Contact sheet.** A generated page of candidate art images, so you can pick
  by eye.
- **Rank 1.** The chosen art candidate for a card. Nothing ships until
  something is ranked 1.
- **Arm.** One side of a measurement. A two-arm run measures the same thing
  with one setting changed.
- **Winrate floor.** A reference character's winrate, used as a "must clear
  this" line. `real_ironclad` and `real_silent` are the two real Slay the Spire
  characters we measure against.

---

## What this is

The QUEUE holds **18 open rows**. This document walks all 18. It sorts them by
what is actually blocking each one, not by topic:

- **Section 1 — ready today.** Eight rows. You can decide these at the desk,
  right now, with what is in HEAD.
- **Section 2 — waits on the playtest.** Four rows. Nothing here can be
  honestly decided until Kokomi is played.
- **Section 3 — waits on the art pass.** Five rows. These are eyes-on picks
  and they want a sitting with the images in front of you.
- **Closing note — two rows that fit none of the three.** They are blocked on a
  document that does not exist yet. They are listed so nothing is silently
  dropped.

## What changed since the last sitting

Three things, and all three affect how you should read the rows below.

**One. The pilot got smarter about one specific thing, and that moved every
Klee number.** Until this morning the pilot placed no value at all on two card
effects: copying a companion you are holding, and replaying the next companion
you play. A card whose whole payoff was one of those scored at or below zero,
and the pilot has a hard rule that it never plays a card scoring at or below
zero. So it never played them — not rarely, *never*. That is now fixed
(`R176`, commit `fbe6e13`), and the version letter moved from `P6` to `P7`.
Two consequences you will meet below: every Klee measurement taken before this
morning describes a different world, and the one card this was discovered
through (`borrowed_brilliance`) turns out to be playable after all.

**Two. Three queue rows closed without needing you.** They were on the list and
they are gone, because on inspection none of them held a decision:

- `M18` asked which of two readings of the corpse-detonation counter was
  intended. Neither prose site was the authority — the code and its pinned test
  already settle it, and two stale comments simply contradicted them. Fixed as
  hygiene.
- `M20` asked you to accept or amend a card's tempo classification. `R158`
  already accepted it and already granted you the option to contest it later. A
  standing option you may take is not a decision you owe.
- `M21` asked you to choose when Kokomi's next measurement happens. The
  measurement law (`EXPERIMENTS` D4, one change per measurement window) already
  decides that, and the thing that would have made it a real choice went away
  when `R158` ruled a different question.

**Three. The shop re-run packet was re-stamped.** It demanded the world
`RT10/D14/P6/C9` in four places and declared any other stamp uncitable. That
world stopped existing this morning. It now reads `RT10/D14/P7/C9`, and its
world list says out loud that the Klee arm's baseline moved. Nothing was
predicted or graded, so amending it was clean.

---

# Section 1 — ready today

Eight rows. Each is decidable now.

### 1. `Q-C` — the payoff-reach rubric, then the predictions

**What you are deciding.** Two acts, in this order, in one commit. First,
ratify the amended rubric text — the written rules for what counts as a
"payoff" card and how a card is attributed to a plan, including the
Necrobinder third-spelling sub-question. Second, commit the aims and the
Q-A/Q-B predictions: which direction each number should move, and the
threshold that counts as success. Both happen **before** any sprint number is
read.

**What to look at.** `review/active/payoff-census-2026-08-08.md` §7 for the
census as amended, and `review/active/payoff-reach-reregistration.md` §5 for
the prediction slots. The tentative aims sit in census §7.2 and are explicitly
**not** ratified.

**What it unblocks.** The whole payoff-reach sprint. No number from it can be
read until this is signed.

**Worth knowing.** This now happens in a settled world. `P7` landed first
deliberately, so the predictions you write today are written against the pilot
that will actually run the sweep. If it had landed after, every prediction here
would have been written against a Klee baseline that no longer existed. The
registration pins only the drafter version (`D14`) and `P7` did not touch the
drafter, so the pin holds and the packet needed no edit.

**Recommendation.** None on the rubric content — that is a measurement-taste
call. On sequencing: take this first today, because it is the only item whose
value decays if other work lands ahead of it.

### 2. `M15` — the card-sheet version-signal rule

**What you are deciding.** Whether to ratify, amend, or reject a proposed rule.
The rule in plain terms: *if you edit a card sheet in a way that changes what
the game actually plays — adding or removing a card, changing a cost, changing
an effect number, changing a rarity — that is a change to the world. It has to
land under a version bump, and numbers taken either side of it are not
comparable.*

**Why it is open at all.** The card sheets sit outside the four-letter stamp.
So today you can change what the game plays and the stamp will not move. A
reader of the stamp cannot tell the two worlds apart.

**What to look at.** The QUEUE row carries the exact proposed text. Two live
demonstrations, both of which have already happened:

- The `X7`/`X8` rarity erratum joined the open `C9` window on 2026-08-10 under
  a single constants bump — done that way by house judgement, because no rule
  required it.
- `EB-26` **added a draftable card** to Kokomi's pool (61 cards to 62) with no
  stamp component moving at all. This is the fresh one, and it is why the rule
  was broadened from "rarity changes" to "any material sheet edit".

**A third demonstration, from today.** The shop re-run packet had to be
re-stamped by hand because a world change landed after it was written. That one
*did* move the stamp, and it was caught precisely because the stamp moved. It
is the same problem from the other side: the stamp is the only signal anyone
reads, so anything that moves the world must move it.

**What it unblocks.** Nothing is waiting on it, but every future sheet edit
either follows it or does not.

**Recommendation. Ratify.** Two of the three occasions above would have been
mis-read by a future reader without it, and the third only worked because the
stamp did its job. If the exact wording bothers you, amend the wording — the
principle is carrying real weight already.

### 3. `M14` — the shop re-run: fill six slots, then countersign

**What you are deciding.** Two acts, and the order matters. First, **fill the
six prediction slots** in §5 of the shop re-run packet. Second, **countersign
the packet**. Then, and only then, runs happen.

The six slots are:

1. **Q1** — of the companions bought from shop slot 2, what share are Uncommon
   rather than Rare? Give a band, and say whether it is an acceptance target or
   a diagnostic.
2. **Q2** — is gold ever what actually stops a purchase? `YES` or `NO`, plus a
   band, plus what result would count as "price is not governing this channel".
3. **Q3** — of the shop visits that offered slot 1, what share end in a slot-1
   purchase? Give a band, and say whether the old 10–35% band still stands.
4. **Q4** — does buying a companion reduce the chance of also buying a relic at
   that same shop? Direction, and a size if you predict one.
5. **P2** — the winrate delta from the whole channel. The old band was
   "positive and no more than +2.0 points". Does it stand?
6. **The redesign trigger** — what result, if any, reopens the shop design
   rather than just being written down.

**What to look at.** `review/active/shop-rerun-registration-2026-08-10.md`. §3
explains each question in plain English; §5 holds the slots.

**What changed since the row was written.** The packet is now **in HEAD on this
branch** — the row used to call it "incoming", and it is not. The world it
measures (`C9`, the restored slot-2 Uncommon floor) is **landed**, not
in-flight. And it was re-stamped this morning to `RT10/D14/P7/C9`.

**The one thing to hold in mind while filling Q1–Q4.** Klee is one of the three
characters this run measures, and the `P7` change moved every Klee number. So
do not anchor these predictions on any Klee figure you remember from before
today. The packet's §2 spells this out.

**What it unblocks.** The entire shop re-measurement. The old numbers are
archive and there is currently no honest shop read at all.

**Recommendation.** None on the numbers — a prediction is yours by definition.
On process: fill and countersign in one sitting, because a half-filled §5 is
the state that invites someone to peek at a run first.

### 4. `M17` — two cards fired a redesign trigger

**What you are deciding.** Whether to redesign two Klee-side cards —
`borrowed_brilliance` and `elemental_ecstasy` — or accept them as they stand.
They tripped the redesign trigger written into the `EB-17p` experiment before
it ran: the "dead in hand" clause.

**What to look at.** `review/active/eb17p-registration-draft-2026-08-08.md`
§13, and especially **§13.8**. Results are frozen at
`review/active/eb17p-results-2026-08-10.txt`.

**What the experiment found.** It was graded blind against predictions
committed ahead of it: three predicted, one split, one miss. The miss was
`borrowed_brilliance`, and it missed on the *wrong sign* — it moved the
opposite way from the prediction.

**The thing that changed today, and it is the crux.** The evidence against
`borrowed_brilliance` was a single striking row: 40,396 draws and **zero**
plays. Two readings fit that row — either the card asks for something
impossible, or the pilot simply refused to play it — and the experiment could
not tell them apart. **It is now settled: it was pilot refusal.** The pilot
valued the card's payoff at nothing, so the card scored `-0.1`, and the pilot
never plays a card scoring at or below zero. Under `P7` the base card plays
about **6.1%** of the time it is drawn. Reachable, not favoured. So the card is
not broken in the way the row implied.

**Two faithful routes, and you pick one:**

- **(a) Act now.** Design against `P7` behaviour — the ~6.1% figure and what
  you think of it — rather than against the frozen pre-`P7` row.
- **(b) Defer.** Register a `P7` re-measure of the same five-card sweep, run
  it, and take the design act against fresh numbers.

**What is not faithful.** Re-grading the frozen §13 against `P7` without a new
registration. The registration and its results file stay unedited (`R101b`).

**Note.** `elemental_ecstasy` is untouched by any of this. Its trigger firing
stands on its own and route (a) or (b) does not change it.

**What it unblocks.** `EB-17p` is otherwise complete. This design act is the
last thing left in it.

**Recommendation.** Route (a) for `elemental_ecstasy` either way, since nothing
about it is in question. On `borrowed_brilliance`, both routes are honest; (b)
costs a measurement window and (a) costs you designing against one measured
number rather than a sweep.

### 5. `M22` — the "dormant marker" class in BACKLOG

**What you are deciding.** The BACKLOG header says the file holds *"only OPEN
executable engineering work"*. Six rows are not that. They are markers: things
we keep written down so that budget is never spent on them by accident, or so a
known hazard is not rediscovered the hard way. The six are `EB-1`, `EB-12`,
`EB-15`, `EB-41`, `EB-80`, and `SKIP-10.9`.

**Three options:**

- **(a) Bless the class.** Amend the BACKLOG header to admit dormant, no-spend
  markers, and name which rows are in the class. Everything stays where it is
  and the header stops being wrong.
- **(b) Adopt an external reviewer's triage.** A review proposed disposing of
  several of these rows. **Flag before you take this one:** its treatment of
  `EB-41` would delete two open questions that exist nowhere else in the repo.
  One asks whether Encore and Fanfare are one meter abstraction or two
  deliberately different things — that question is load-bearing on the sheets.
  The other asks which experiment scripts stop being re-runnable, which is a
  call only you can make. **If you take (b), `EB-41` must be ruled on its own
  and not bulk-closed.**
- **(c) Direct per-row disposal.** Say for each of the six whether it becomes
  LAW, becomes a dossier entry, or is deleted.

**What to look at.** The BACKLOG header, and the six rows themselves. `EB-41`
is the long one and the one worth reading in full.

**What it unblocks.** Nothing is waiting. But until this is ruled, the BACKLOG
header describes a file that does not exist, and six rows sit there without a
ruling behind them.

**Recommendation. (a).** The rows earn their place; the header is the thing
that is wrong. (a) is the cheapest true fix. If you prefer (b), rule `EB-41`
separately.

### 6. `S4-G11` — read the card names and lore by eye

**What you are deciding.** Whether the card names and lore text are good enough
to ship. This was ruled to have no substitute — no tool checks taste.

**What to look at, and an honest note on what exists.** The pile has three
parts and they are not equally ready:

- The Furina pass (the `R29d` ask) — the sheet is in HEAD, readable now.
- `EB-26`'s one new name, `Watch of the Shallows` — in HEAD now, at
  `docs/kokomi-cards.yaml:515`. One line, readable in a minute.
- The `EB-22` fill names — **not in a sheet yet.** `EB-69` has not executed, so
  those names live in the docket, not in the card data. They were declared
  provisional pending this pass.

**What it unblocks.** `EB-69` cannot land its fill as final until the names it
carries are read. The `EB-26` name is already shipped, so reading it is a
confirm-or-erratum, not a gate.

**Recommendation.** Do the Furina pass and the one `EB-26` line today — that is
a short sitting and it clears real ground. Leave the `EB-22` names until they
are in a sheet, so you read them in the shape they will ship in.

### 7. `M19` — the five-layer Hydro orb art set

**What you are deciding.** Approve or choose an art set: five orb layers, in
Hydro colours, for Furina's energy counter.

**Why five.** The base game's energy counter scene fills its layer slot with
exactly five textures. A Furina counter has to match that shape, so the art set
is five pieces and not some other number. Nobody has authored one of these
before — all three of our characters currently return the base game's Ironclad
counter scene, so there is no precedent to copy.

**What to look at.** `docs/current/art/furina-art-pass-requirements.md` §8. The
matching icons already shipped on 2026-08-08, so this is only the layer set.

**What it unblocks.** BACKLOG `EB-40`, the engineering half. That row cannot
start without this pick, and it is a crash-class piece of work with no test
backstop, so it wants a clean run at it.

**Recommendation.** None — this is taste. Flagging only that it is genuinely
small and it unblocks a whole row, so it is good value for the minutes.

### 8. `M13` — the route-regret margin (read this, but expect to do nothing)

**What you are deciding.** Eventually: countersigning a pre-registration for
measuring `ROUTE_REGRET_MARGIN` and its twin, the `+ 1.0` in `draft_regret`.
Neither number has a recorded derivation — they were chosen and never
justified.

**Why it is not actually decidable today.** `R164` already ruled the shape:
pre-register the measurement, and do **not** ratify `+1.0` as it stands. The
draft you would countersign does not exist yet. Building it needs a
distribution printer first, because the current output prints no percentiles
and the route-regret block prints nothing at all. Printer and draft are BACKLOG
`EB-72`.

**What to look at.** Nothing today. When `EB-72` lands, the packet comes to you.

**What it unblocks.** Until then, only the margin-free reads
(`mean`/`p50`/`p90`/`max_regret`) are quotable.

**Recommendation.** No action. It is listed here so you can confirm you are
happy with that sequencing and then skip it.

---

# Section 2 — waits on the playtest

Four rows. Kokomi has to be played before any of these can be answered
honestly. `R175` settled the sequence and it is worth holding in your head,
because three of the four rows depend on it:

> **The post-wave playtest and the confirmatory protocol run are two separate
> events.** The post-wave run comes first and is **exploratory** — you play, you
> observe, you fill in no answer sheet, and it consumes nothing. Then you
> declare Kokomi's HP band from design intent. Then, and only then, the
> confirmatory protocol run happens, graded against the written question list.

### 9. `S4-G6` — declare Kokomi's HP stability band

**What you are deciding.** A number: the band Kokomi's HP should stay inside.
You declare it **from design intent** — from what she is supposed to feel like
— and you may not revise it against the run that tests it. That is the whole
point of declaring it first.

**What to look at.** `review/active/volatility-read-2026-08-10.md`. A fresh
volatility read is already in hand, so this waits on *observation*, not on more
measurement.

**One finding worth carrying in.** The **inversion**: Kokomi is the worst of
the three on time-spent-low, while Furina is the flattest. That is the opposite
of the intuition her kit suggests.

**When.** After the exploratory post-wave run. Not before, and not after the
confirmatory run.

**Recommendation.** None — this is a design-intent number and it is yours by
construction.

### 10. `S4-G13` — which lever to lift Kokomi, and whether to pull it

**What you are deciding.** `R154` already ruled that Kokomi needs a general
power lift. What stays open is **which lever, and whether to pull one at all**,
after you have watched her.

**What to look at.** `review/active/sitting-reads-2026-08-08.md` §2 for the
standing numbers. Note the stamp on them is `RT9/D14/P6/C8` — two boundaries
back — so read them for **structure**, not for level: all three plans sit below
the Ironclad floor with no interval overlap, and assist sits below even the
Silent floor.

**What is already happening.** A legal lever-2 candidate is being built
(BACKLOG `EB-74`) and **nothing will be pulled** until you have observed.
`R154` named the suspicion: assist has no internal payoffs — *"she really has
two archetypes not three"*.

**Recommendation.** None on the pull. On reading: when you play her, watch
specifically for whether assist ever pays you back for committing to it.

### 11. `S4-G14` — the confirmatory protocol run

**What you are deciding.** Table time: sitting down and playing Kokomi
deliberately against the written question list, so the answers can be graded.

**What to look at.** `docs/current/playtest/kokomi-playtest-protocol.md`.

**What changed.** `R152` retired `OT-1` as a card question — *"Neap Tide"* was
a sprint name, not a card, and an earlier ruling turned it into one in error.
`R175` split this row's event from the exploratory one and dropped `S4-G6` from
its gate list.

**What still gates it.** One engineering remnant in `EB-53`. Nothing else.

**Recommendation.** None. This is scheduling, and it follows `S4-G6`.

### 12. `M16` — the fourth end-of-turn slot

**What you are deciding.** One of two: re-specify the `C7` capture, or keep the
end-of-turn docket's fourth slot as deliberate headroom.

**Why it is a real question.** `C7` asked for a capture showing all four
end-of-turn effect sources at once. That cannot happen. Sparks 'n' Splash is
Klee-only and Bake-Kurage is Kokomi-only, so no single creature can ever hold
all four — three is the reachable maximum. So either the capture spec changes,
or the fourth slot is accepted as space for something that does not exist yet.

**What to look at.** BACKLOG `EB-53` §7.4.

**When.** `R170` deferred this to after the post-wave playtest, on the grounds
that how the docket reads *in combat* is the input.

**Recommendation.** None — it turns on how it looks to you when you play it.

---

# Section 3 — waits on the art pass

Five rows. These want one sitting with images in front of you, not five
sittings.

### 13. `S4-G12` / `CC-G1` / `CC-G2` — the Curtain Call art review

**What you are deciding.** Eyes-on the contact sheets and the in-game
screenshots for the twelve Curtain Call cards, plus the A0 smoke run. Plus one
small written answer that has been owed for a while: the row says "three
cards", and **which three was never written down**. The sheet was regenerated
over all six gate rows, so you have more than you need — you just have to name
the set.

**What to look at.** `review/active/art-runs-2026-08-08.md`.

**What changed.** `R166` corrected the re-hunt set: it is **four** cards, not
three — `warmup_act`, `crowd_work`, `tempo_change`, `audience_participation`.
`standing_room_only` is overturned and `grand_gala` is displaced from that set.
The A0 elite smoke is partial.

**Status.** Materials ready.

**Recommendation.** None on the picks. Take the "which three" answer first — it
is one line and it stops the ambiguity propagating.

### 14. `S4-G17` — three running-game looks

**What you are deciding.** Taste on three things seen in motion, not a full
playtest: the salon look, the motion-and-facing feel, and the icon picks.

**What to look at.** `docs/animation-sprint-2-plan.md`, items B5, D5 and E2. The
captures are staged by BACKLOG `EB-52`.

**Note on urgency.** Reduced. The hover-target problem closed in playtest 4, and
B5 was recorded as "not noticed" in play.

**Recommendation.** Fold this into the art sitting rather than giving it its
own slot.

### 15. Art debt — the pick list

**What you are deciding.** A list of individual art picks. Most are
straightforward. Three parts need calling out:

- **The one open collision.** `ovation_trickle` and `stagehands_encore` were
  both given the **same source image** for their power sigils. Two different
  powers cannot wear the same picture. One of the two needs a different pick,
  and which one moves is yours.
- **`EB-39` (`no_holding_back`).** Four candidates, and a finding that bounds
  the reject branch: **no large landscape blast illustration exists in the free
  Klee pool.** The other survivors carry burnt-in wordmarks or are wiki
  infographics. So if you reject all four, the honest next step is a manual
  crop or commissioned art — not another hunt.
- **The `ART-L12` pair.** `crowd_work` and `standing_ovation` currently share a
  card face, and there is nothing to pick from for `standing_ovation` because
  only an icon sheet exists. Production of the card sheet is BACKLOG `EB-76`;
  the pick comes after.

**Also still open in the row:** Kokomi's 58 faces and 15 companions, the `E2`
icon picks, and the `spark_knight_style` replacement.

**Recommendation.** None on any pick. Sequencing only: do the collision first,
because it is the only one where the *current* state is wrong rather than
merely unchosen.

### 16. S8 + S10 galleries

**What you are deciding.** Two taste calls, both on proposal galleries you have
not walked yet. S8: eight flagged potions and relics. S10: which enemies could
be **reskinned** rather than **redesigned** — that split is yours per the north
star.

**What to look at.**
`docs/current/dossiers/content/potion-relic-conversion-gallery.md` and
`docs/current/dossiers/remap/reskin-gallery.md`.

**Recommendation.** None — pure taste.

### 17. `M10` — Fontaine Rares close-out

**What you are deciding.** This row is already countersigned on the grading
(`R165`). It stays open for one reason: it closes on **your full card review**.
Inside it, two things are still yours and cannot be delegated:

- The companion art picks — Navia, Clorinde, Neuvillette, Arlecchino.
- The v1.7 lore and naming eyes-on audit.

**Note.** Neuvillette **ships as-is** to unblock, and carries an owed redesign.
That was already ruled; it is not reopened here.

**Recommendation.** Take the four companion art picks inside the art sitting.
The card review is its own thing and does not need to be in the same session.

---

## Closing note — two rows that fit none of the three

Both are blocked on a document nobody has written yet. They are listed so they
are not silently dropped.

### `S4-G7` — Furina: rebalance the weak plans, or widen salon

**What you are deciding, eventually.** `R153` ruled that Furina keeps three
plans. The open call is **which remedy**: rebalance the weak plans until they
are viable, or expand salon so it contains multiple archetypes.

**What is blocking it.** The options packet does not exist. It is BACKLOG
`EB-81`, and its whole job is to lay out what each remedy costs, what each
moves, and what each forecloses, taking no position. The fence that used to
block this row is gone (`R138`), so `EB-81` is the only thing left.

**Standing read** (`RT9/D14/P6/C8`, two boundaries back — read for structure,
not level): salon 4.70%, spotlight 1.50%, fanfare 1.30%; `real_silent` 1.37%,
`real_ironclad` 6.13%. Salon separates from both other plans; fanfare still
overlaps the Silent floor; salon now sits **below** `real_ironclad`.

**Recommendation.** Wait for `EB-81`. Choosing between two remedies without the
cost comparison in front of you is the exact thing the packet exists to
prevent.

### `M13` — see item 8

Listed in Section 1 for completeness, but it is blocked on BACKLOG `EB-72` in
the same way. No action today.

---

## Suggested order for the day

1. `Q-C` — rubric, then predictions. Do it first.
2. `M14` — six slots, then countersign.
3. `M15` — ratify the version-signal rule. Short.
4. `M17` — pick route (a) or (b), then design or defer.
5. `M22` — bless the class, or rule `EB-41` on its own.
6. `S4-G11` — Furina names plus the one `EB-26` line.
7. `M19` — the orb set, if the art sitting is not happening today.

Everything else waits on a table or on images.
