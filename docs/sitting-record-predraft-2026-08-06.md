# Sitting Record Pre-Draft — 2026-08-06 ([USER] verdicts, transcribed and routed)

**Status:** PRE-DRAFT for ledger entry; R-numbers to be assigned at landing against current DECISIONS.md max. Verbatim verdicts are [USER]'s; routing and flags are chat-session synthesis. Nothing below is executed until this lands as a ruling.

## 1. S4 hygiene report — ALL F PROPOSALS APPROVED

F1–F17 approved as proposed. Consequences, now unlocked for mechanical execution:
- The ledger-repair pre-drafts execute (strikes, banners, cross-references per the report's proposed text).
- F1: Furina items 1–3 + fanfare STOP governing condition re-points to Track B / B-G1 as proposed.
- F2 + G8: the Gallery Stirs fixture re-homes to the `_static_power` session and the PROPOSED D13 entry lands as ratified.

## 2. G1 — COUNTERSIGNED: **Zhongli for slot 4** (R88 eligibility resolved)

The Zhongli deep dive is unblocked. Track J's dossier (canon kit inventory, StS2/Downfall precedent scan, open questions; Crystallize fence honored) is on main and ready as the session's opening exhibit. Scheduling is [USER]'s, post-week-off.

## 3. S13 exploit ledger — per-family verdicts (verbatim), with routing

| Family | Verdict (verbatim) | Routing |
|---|---|---|
| X1 cost-delta accumulator | "Let's make a note of this for the Klee rework" | NOTE → Klee rework docket. **FLAG-1 below.** |
| X2 self-replacing 0-cost companions | "Not a problem; power in line with existing Uncommon Colorless… infinite cycling engines gated to Uncommon rarity or higher. If this is Common, it needs a bump." | NEW LAW (cycling-rarity gate) + MECHANICAL AUDIT: rarity check on `sayu_naptime` and all self-replacing 0-cost non-exhaust companions; Common instances flagged for bump. |
| X3 Encore Performance self-closure | "Remove the energy rider and make it free to play instead." | RATIFIED CHANGE → card sheet: upgrade loses `copy_cost_override: 0`; base card becomes 0-cost. **FLAG-2 below.** |
| X4 Guest Cast unfiltered ×1.5 | "Seems totally fine as a damage-boosting power… may need to limit to 'damage only' if the block scaling gets absurd." | WATCH ITEM → telemetry note (block-side Guest Cast readings) + revisit trigger recorded. |
| X5 fanfare floor stacking | "Likewise seems fine; cycling at uncommon does not feel problematic." | **HELD FOR CLARIFICATION — FLAG-3 below.** |
| X6 salon displacement double-pay | "As a strategy, totally fine (Defect does the exact same thing) — it's the power level we need to watch." | WATCH ITEM → power-level telemetry note. |
| X7 Klee spark economy | "Gate repeatable spark generation behind Uncommon or make sure no card below Rare is both 'sparks + draw enabler'" | NEW LAW (spark-gate, disjunctive as stated) + MECHANICAL AUDIT: Klee pool sweep for violating cards → Klee rework docket. |
| X8 bomb two uncapped terms | "Not a problem at higher rarity — need to check these cards." | MECHANICAL AUDIT: rarity check on both terms' carrier cards; findings to Klee rework docket. |
| X9 charge bank | "Probably too strong as-is and needs to be parsed carefully. Review during the next kit workshop." | NOTE → Kokomi kit workshop / pool-rework docket (already queued third). |
| X10 Metallicize treadmill | "10 of the same Companion at common seems exceptionally unlikely. May be worth moving to Uncommon and adjusting power up." | CANDIDATE (not ratified) → companion pricing docket: `gorou_heart_of_the_clan` Uncommon promotion + power adjustment, priced at session. |
| X11 replay_next_companion stacking | "Cap those effects to 'same turn only'" | RATIFIED CHANGE → scope the counter to the turn (write-side or spend-side per implementer's parity check); Study Buddy/Duet parity twins both covered. |
| X12 cross-element reaction splashes | "Seems probably fine; half the fun of co-op. Check actual potency in co-op playthroughs." | WATCH ITEM → co-op playtest note; Track H corpus is the instrument once its denominator defect (O-1) is repaired. |
| X13 14-relic weakness eraser | "Also seems fine; odds of a specific relic combo are low." | NO ACTION; the finding's open drop-rate question recorded as answered-by-judgment. |
| X14 structural softlocks | "Add a fallback: if the hand is full, one random card is discarded before the spotlight is added." | RATIFIED CHANGE → leg (b) only (ethereal-spotlight starvation). **FLAG-4 below.** |

## 4. Flags — clarifications requested before the affected items execute

- **FLAG-1 (X1):** the accumulator has TWO run-plausible enablers: Klee's `friendly_visit` (common) **and Kokomi's `honor_guard` (printed 0-cost)**, riding shared uncapped state (`companion_cost_delta_this_turn`). A Klee-rework-only note leaves the Kokomi leg live. Question: should the note also ride the Kokomi pool-rework docket, and/or should the accumulator itself (shared machinery, uncapped, floor-at-0) get a structural disposition at a systems session?
- **FLAG-2 (X3):** the ruling cleanly kills the energy-positive loop. Two adjacent closures in the same family remain undisposed: (i) a copied `sucrose_catalyst_conversion` regenerates faster than its Exhaust bound removes it — the sheet's stated bound is deleted by the copy op; (ii) `cost_override` writes to the card instance with no turn scoping, so "temporary" 0-cost copies are permanently free (S14 cross-ledger: rides a known parity defect). (ii) reads as a straight bug with an unambiguous fix (turn-scope the override) — bless it and it's mechanical; (i) may want the copy op to respect printed bounds, which is a design call.
- **FLAG-3 (X5):** the verdict's language ("cycling at uncommon") maps onto the family's *cantrip leg* (upgraded `tempo_change`: cost 1, draw 2, +1 refund → infinite). The family's core is different machinery: **stacked fanfare floors permanently delete the 20%/turn decay that is the meter's only sink** (one-card 240, turn-2 boss kill, unloseable stall, turn-3 boss kill on commons-only income). Question: does "seems fine" cover the decay-proof floor stacking, or only the cantrip leg? Held rather than guessed, per the no-supplied-assumptions norm.
- **FLAG-4 (X14):** the fallback resolves leg (b). Legs (a) — `curse_poor_sleep` typed both `status` (unplayable) and `retain: true` (unflushable), ten copies = permanent hand jam — and (c) — Powers route to `result_pile: none`, an all-Power deck erases itself into 27 empty turns — remain undisposed. (a) looks like a data-typo-class bug (a curse that retains forever); (c) may be intended StS-like behavior. One-line verdict each requested.

## 5. Consequential swarm findings placed on the docket (no verdicts requested tonight)

- **O-1 (instrument, HIGH):** `run_battery` merges gauntlet's two stages into one FightStats while rates divide by records — every published Track H per-fight reaction rate overstated (all-row aura apps/fight 7.70 → true 6.60, 16.7%). Unambiguous defect; fix + corrected corpus re-read queued as mechanical, pinned per Track K idiom.
- **N-1 (lore, HIGH):** `gorget` gallery rationale cites Concealed Unguis as Bathysmal Vishap material; it is a Riftwolf drop (The Chasm). A live miss inside the S8-verified set — the retroactive audit found what the original pass cleared. Routed to [USER]'s N-ledger review with the other four TOP-5s.

## 6. Still open on [USER]'s side (carried, not grown)

R102 escrow countersign (pre-draft ready — one strike operation); S2 event-gallery checkboxes; S14 canonicity rulings (NC-1, shop slot 1, Frozen, `spend_potion`); G6 Kokomi stability-band declaration; the four merge-train paperwork one-liners; N/O TOP-5 review; Ancients/boss-pool gallery whenever inspiration strikes.

---

## 7. SECOND SITTING REPLIES — 2026-08-06, recorded verbatim (Track Y)

**Recorded before execution, per standing discipline.** This section is the
authority for every commit on `findings/track-y` of the "Empty the Green Room"
batch. It is a transcription, not a synthesis: the text below is [USER]'s
sixth-wave brief, Track Y, reproduced as received. Nothing in this section is
chat commentary, and nothing in it was reworded to fit the repo's vocabulary.

**Scope note, stated so it is not inferred.** Track Y lands *these* answers and
nothing adjacent. The R102 escrow, the four HELD flags (FLAG-1…FLAG-4), S14
canonicity, `S4-G15`, and the two staged G5/G6 dispositions are explicitly
untouched by this batch and remain open on [USER]'s side.

> **Track Y — Land the answers (mechanical; every item cites its reply)**
>
> * Y-1 (Q1 / F6 / NT-G5): YES — the 08-01/02 session is playtest three; the current Kokomi build was played. Land the yes-form slot. Consequence recorded, not resolved: the fork's evaluation is now DUE and joins the queue as its own item — "did Neap Tide read weak at the table?" → weak = lever 2 isolated cell; fine = lever 3 + the calibration offset finally written as a number. AWAITING-[USER]; no lever is pulled by this batch.
> * Y-2 (Q2): YES — companion-pricing docket owns X2 rarity work. Assignment line lands; "unrouted" marker cleared.
> * Y-3 (Q3): MERGE — `staged/f14-siblings` (`eaa83e5`) merges: four repairs + the citation lint. Suite green on the merge commit.
> * Y-4 (Q4): YES — `copy_cost_override: 0` deletes from Encore Performance's upgrade in `docs/furina-upgrades.yaml`; the pre-positioned exemption becomes load-bearing. Expect no pin flip (the X3 pin runs the self-copy leg); say so in the commit.
> * Y-5 (S4-G1 addendum): new ruling recorded — Itto enters as a COMPANION CARD, not a character (R108 gains the clause, verbatim from [USER]). Fontaine-Rares/roster docs cross-noted; no card is drafted tonight.
> * Y-6 (S4-G2): R89 countersigned — SIGNED as an audit-trail reconstruction of the shipped 07-24 sprint, per [USER]'s characterization. DRAFT banner drops.
> * Y-7 (S4-G3/G4): v1.12/v1.13 amendments RATIFIED; unratified banners drop; law text now matches shipped code.
> * Y-8 (CI hardening, first-instance): `gen_roster_cards.py --check` becomes CI job 4. Pure mechanical gate; the class "sheet changed, generated C# didn't" now fails loudly.
> * Y-9 (staging slots, AWAITING-[USER]): pre-draft both G5/G6 dispositions from chat's recommendation — (a) B-G1 narrowed to the Fanfare axis, six axes closed as reportable-only-permanently, with the R107/F1 fence re-pointed to the narrowed form; (b) S4-G6 + G14 re-anchored to the post-rework Kokomi build, declare-before-playtest law intact. Staged, never landed without the reply.

### How the four one-word asks map onto the queue

| Reply | Queue row | Landing site |
|---|---|---|
| Y-1 | §1 `Q1` | `klee-mod/DECISIONS.md`, the `NT-G5` fork block (slot 1, YES-form) |
| Y-2 | §1 `Q2` | `docs/dockets/companion-pricing.md` §2 (slot 2, YES-form) |
| Y-3 | §1 `Q3` | branch `staged/f14-siblings` merges (slot 3) |
| Y-4 | §1 `Q4` | `docs/furina-upgrades.yaml`, `encore_performance` |
| Y-5 | §2 `S4-G1` rider | `tier0/DECISIONS.md` R108 addendum |
| Y-6 | §2 `S4-G2` | `tier0/DECISIONS.md` R89 banner |
| Y-7 | §2 `S4-G3` / `S4-G4` | `docs/teyvat-spire-design-principles.md` amendment drafts |

### Execution notes worth carrying (recorded at landing, 2026-08-06)

- **Y-8 was already in force.** `python tools/gen_roster_cards.py --check` has
  run in this repo's CI since the sim-hygiene sprint, as the "codegen staleness"
  step of the blocking `lints` job. No new job was added — two invocations of one
  check double the noise and halve the trust — and the step now carries a dated
  comment saying so. It was exercised for real the same day: Y-4's deletion
  turned it red until the generator was re-run.
- **Y-4 produced one consequence nobody predicted**, and it is queued rather
  than decided: X6's exploit line drafts an *upgraded* Encore Performance, so
  with the upgrade deleted the replay harness cannot build the deck and that pin
  went xfail → SKIP. The X3 pin did not flip, exactly as the reply expected. See
  queue row `Q6`.
- **Y-9 landed nothing, by instruction.** Slots 4 and 5 of
  `docs/awaiting-user-slots-2026-08-06.md` carry both forms of both dispositions
  in full; queue rows `Q7` and `Q8` are the one-word asks.

**What Y-1 does NOT do, restated because the reply invites the mistake.** The
trigger firing is not the evaluation. No lever moves on this batch, and the
fine-branch's sim-calibration offset for exhaust-loop kits stays unwritten —
it is owed by the evaluation, which becomes its own AWAITING-[USER] queue row.

---

## 8. THIRD SITTING REPLIES — 2026-08-06, recorded verbatim ("Cold Reading")

**Recorded before execution, per standing discipline.** This section is the
authority for every commit of the "Cold Reading" batch. It is a transcription,
not a synthesis: the text below is [USER]'s seventh-wave brief, Tracks AA/AB/AC,
reproduced as received. Nothing in this section is chat commentary, and nothing
in it was reworded to fit the repo's vocabulary.

**Two supersessions arrived after this text and are recorded in §9 and §10, not
here.** Where §8 and a later section disagree, the later section wins and says
so; §8 is never edited to match it (R101b). The two are: `AC-1` (the Neap Tide
fork deferral, superseded by §9's REVISED record) and `AB-FLAG-4` leg (c) (still
AWAITING here, RULED in §9). `AC-6`'s "none yet in this document" is superseded
in part by §9 and §10, which rule five of the S14 canonicity questions.

> ### Track AA — R102 escrow strike (SIGNED)
> [USER]: *"agreed - signed."* Execute the pre-draft (`ruling-predraft-r102-escrow-2026-08-05.md`) as one ledger operation: all four PROVISIONAL marks struck as instrument-vindicated; companion clauses C-a…C-d land (term-3 filed to the S7 ledger as bounded/direction-known; blind-replay column re-read rule; S13 re-verification NO for C1/C2 with the Family-A grep results attached; standing limits carried to annotations). The term-3 fix candidate (credit only standing-designation plays) is now formally queueable — it joins the next errata batch, NOT this one.
>
> ### Track AB — FLAG resolutions (verbatim verdicts, then execution)
> - **FLAG-3 RESOLVED — INTENDED:** *"We deliberately allowed for powers to raise the fanfare floor (without decaying) as a sort of strength-style scaling effect. I think this is fine."* X5 closes fully (both legs). Ledger + pin docstring annotated; a watch-item rides the register citing the verified magnitudes (one-card 240 / turn-2 boss kill lines) under the X6 pattern — strategy intended, power level watched. The X5 pin converts from xfail to a documented-behavior test.
> - **FLAG-1 RESOLVED — RATIFIED CHANGE:** *"Limit the cost discount to the current turn? Yes."* The companion cost-delta accumulator scopes to the writing turn, both engines, mirroring the X11 boundary. Distinct from FLAG-2(ii)'s `cost_override` — do not conflate; two mechanisms, two fixes, one shared boundary idiom. Note in the report: the within-turn free-companion loop survives this change by design and is governed by the X2 rarity law (its engines now sit at Uncommon), consistent with [USER]'s X2 framework. Pin behavior: report, don't force.
> - **FLAG-2 RESOLVED — BOTH FIXES RATIFIED:** *"Yes."* (i) Copy ops inherit the printed card's bounds — a copied `sucrose_catalyst_conversion` respects its Exhaust limit. (ii) `cost_override` aligns to the sheet/C# semantics ("costs 0 **this turn**") — this is NC-12/SYS-3's sim-side fix; C# is already correct, so (ii) is sim-only parity. **Staged, one word owed (AB-s1):** NC-12's adjacent inversion — C#'s Encore Performance does not exclude kit cards from the copy pool (sheet and sim do; a copied kit Burst clogs a hand slot in game). Sheet-vs-mod parity fix, mod-side; staged because it's a mod behavior change not yet explicitly blessed.
> - **FLAG-4 leg (a) — clarification recorded, root staged:** [USER]'s fallback restatement matches shipped S-3 (spotlight path). Leg (a)'s root is different: `curse_poor_sleep` is typed both `status` (unplayable) and `retain: true` (never flushed) — the jam is the typing, not the spotlight. **Staged options, one word owed (AB-s2):** (α) drop `retain` from the curse; (β) rule that status-typed cards always flush at end of turn (StS precedent), engine-wide. Neither lands without the word.
> - **FLAG-4 leg (c) — AWAITING:** the all-Powers self-erasure explanation was delivered in chat; the queue row now contains it verbatim. Accept-as-StS-precedent or guard: [USER]'s word.
>
> ### Track AC — Fork, gates, and reclassifications
> - **AC-1 (NT-G5 fork):** [USER]: *"nothing stood out besides the charge stacking / missing animation; let's review next playtest."* Recorded: playtest-three read = no Neap Tide weakness observed; **fork evaluation DEFERRED by [USER] to the next playtest; no lever pulled; the calibration offset remains registered to the fine-branch and unwritten.** The queue row rewrites to say exactly this.
> - **AC-2 (S4-G6):** deferral APPROVED — land staged slot (b): stability band + protocol playtest re-anchor to the post-rework Kokomi build; declare-before-playtest law intact.
> - **AC-3 (S4-G5 / B-G1): STILL AWAITING** — the narrow-to-Fanfare-axis disposition (staged slot (a)) has no reply yet. Queue row stays, plain-language form: *"Close six of seven axis scorecards permanently as 'numbers are informational only'; keep only the Fanfare axis, which the Furina work already depends on. YES closes it."*
> - **AC-4 (G15 corpse detonation → probe):** [USER]: *"who knows when it closes."* Convert from table-luck to instrument: stage a registration for a bridge-driven in-game probe — scripted fight, bomb + killable enemy, observe detonation-vs-corpse behavior, compare to the sim's assumption. Ten minutes of agent time replaces waiting for the interaction to occur naturally across playtests. Registration staged for countersign (new probe = pre-registered question per standing law); the table item survives only as fallback.
> - **AC-5 (S2 gallery):** status → INSPIRATION-OPTIONAL (joins the Ancients gallery); leaves the active-ask section of the queue.
> - **AC-6 (S14 rulings received in chat where given):** none yet in this document — all four NC questions sit in the queue **with their full plain-language explanations embedded inline** (NC-8's includes the recommendation "potions are consumed" as the presumptive answer awaiting one word). Discoverability lesson feeds Z-5: a queue row that requires opening another file to understand is a defect.
>
> ### Non-goals
> 1. No S14 fixes land in the Cold Reading paper track (they are Errata Batch 2's).
> 2. AB-s1, AB-s2, FLAG-4(c), AC-3, AC-4's registration: staged/awaiting only.
> 3. Term-3 fix queued, not executed in the paper track. No constants. Version-stamp questions surfaced per precedent for AB's two engine changes.
>
> ### Report-back
> Standard. AB additionally reports both engines' post-change behavior on the affected S13 lines (characterize, don't grade) and any pin transitions with one-line explanations.

---

## 9. FOURTH SITTING REPLIES — 2026-08-06, recorded verbatim (Cold Reading, Addendum 1)

**Extends §8; same discipline.** Transcription, not synthesis. Where this
section and §8 disagree, this section is the later text and wins — and §8 is
left standing rather than edited, per R101b.

> ### AC-6b (NC-1, RULED) — companions scale with the player
> *"They are supposed to also scale with you like your own cards."* Sim canonical; mod defect. C# routes companion-power damage through the full damage pipeline (Strength, Weak ×0.75, Vulnerable ×1.5). Parity vectors updated; NC-1's line evidence (Durin's Witch's Flame) becomes the regression test. **NC-11 explicitly NOT covered** — power-sourced block's funnel exemption is a documented sim design choice cutting the other way; it becomes its own queue one-liner with both sides stated.
>
> ### AC-6c (NC-7, RULED) — Frozen is the timer, applied per-creature
> *"Ticks down per-turn, applies per-creature."* Canonical Frozen: duration counter decrementing at end of enemy side each turn (stacking extends; the mod's semantics); substitution per-creature (the sim's semantics — Kaiser Crab's boss-room adds become freezable in game). Sim adopts the timer; mod adopts per-creature. Shipped-boss-fight impact noted in the commit; version-stamp question surfaced per precedent (this changes sim combat math wherever Frozen appears).
>
> ### AC-6d (NC-10, RULED) — shop slots specified; both engines defective
> *"Slot 1 should be 'Uncommon or higher from the home region'; slot 2 should be 'any companion card'; this is a defect."* Both engines implement the spec: slot 1 filters home-region pool to Uncommon+, slot 2 unrestricted. Rarity-odds renormalization within the Uncommon+ pool: implementer surfaces the candidate readings (condition existing SHOP_COMPANION_RARITY_ODDS on ≥Uncommon vs. a stated split) rather than choosing. Companion-pricing docket cross-noted: shop is now a real Rare source in both slots' math.
>
> ### AB-FLAG-4c (RULED) — all-Powers deck-out is intended
> *"You deck out... don't do that."* Closed, StS-precedent shrug, no guard. Documented-behavior note in the engine docs and the X14 ledger entry; leg (c) drops from the queue.
>
> ### AC-1 REVISED — Neap Tide fork: inconclusive by non-observation
> [USER] clarification: *"I don't remember seeing the card during the playtest, so it did not stand out one way or another."* The prior deferral record is superseded: playtest three did not exercise Neap Tide, so the fork's evaluation was not possible there, favorable-read notwithstanding. New record: fork OPEN, evaluation re-anchored to the next Kokomi playtest **with an explicit observation task** (Neap Tide deliberately drawn/played and reported) added to the playtest checklist. Candidate alternative recorded, not chosen: fold the fork into the queued Kokomi pool-rework session. The strikethrough-and-banner idiom applies to the superseded deferral note — no silent rewrite.
>
> ### Batch mechanics
> NC-1/NC-7/NC-10 changes join the **second errata batch** alongside the queued term-3 fanfare fix — one batch, both engines where applicable, suite green at each boundary, S13 harness characterization run after, pins report their transitions. Non-goals: everything still awaiting (AB-s1 kit exclusion, AB-s2 curse typing, AC-3 axis closure, AC-4 probe registration, NC-11 new) stays staged.

---

## 10. FINAL DISPATCH — 2026-08-06, recorded verbatim (Cold Reading, Addendum 2)

**Extends §8 and §9; same discipline.** This is the consolidated hand-off:
everything in it is ratified and executable; everything not in it stays
staged/awaiting. NC-11, opened as a new question by §9, is ruled here.

> Extends the Cold Reading brief + Addendum 1. This is the consolidated hand-off to Code: everything below is ratified and executable; everything not below stays staged/awaiting. Verbatim verdicts land in the ledger before execution, per standing discipline.
>
> ### AC-6e (NC-11, RULED) — power-sourced block stays raw
> [USER]: *"I think that the answer is no; my recollection is that power-sourced block in the base game's kits ignores both of those."* The sim's documented funnel exemption (`powers.py:75-81`) is canonical; the mod is the defect side — C# stops routing Metallicize, the Ceremonial Garment rider, and the Kurage pulse through Frail/Dexterity. Ruled register, recorded for future card work: power-sourced damage runs the damage pipeline (NC-1); power-sourced block is raw (NC-11). Cross-note on X10: post-fix, the treadmill's sim-side numbers hold in the mod too; the S13 ledger's NC-11 caveat on X10 resolves.
>
> ### Errata Batch 2 — consolidated contents (one batch, ordered, suite green at each boundary)
> 1. Term-3 fanfare credit (escrow companion C-a's queued fix): tier0 credits only plays covered by a standing designation. Sim-only.
> 2. NC-8: potions actually consumed (`tier05/events.py` throwaway-copy fix). Sim-only.
> 3. NC-1: companion-power damage through the full pipeline in C#. Mod-only.
> 4. NC-11: power-sourced block raw in C#. Mod-only.
> 5. NC-7: Frozen unified — timer semantics (sim adopts) + per-creature substitution (mod adopts). Both engines; shipped-boss impact noted.
> 6. NC-10: shop slot spec — slot 1 home-region Uncommon+, slot 2 unrestricted. Both engines; odds-renormalization readings surfaced, not chosen.
> 7. FLAG-1: companion cost-delta accumulator scoped to the writing turn. Both engines. (If already landed by Cold Reading's Track AB, skip here.)
> 8. FLAG-2 (i)/(ii): copies inherit printed bounds; `cost_override` = "this turn" (sim-side SYS-3 fix). (Same skip rule.)
>
> After the batch: parity vectors + all lints; S13 harness characterization on affected lines (report transitions, don't grade); version-stamp questions surfaced in one place (NC-7 at minimum); FLAG-4c's documented-behavior note and the FLAG-3/X5 pin conversion land with the paper.
>
> ### Still staged / awaiting — DO NOT EXECUTE
> AB-s1 (kit-exclusion copy-pool parity fix, mod-side), AB-s2 (curse typing: drop `retain` vs. status-flush law), AC-3 (B-G1 narrowed to Fanfare axis), AC-4 (corpse-detonation probe registration), Neap Tide fork anchoring preference (observation task = default, fold-into-rework = candidate), S2/Ancients galleries (inspiration-optional). All live in the user-queue with explanations inline.

### One discrepancy, recorded rather than resolved by guess

Track AA's text cites a pre-draft at `ruling-predraft-r102-escrow-2026-08-05.md`.
**That file does not exist in this repo**, on any branch, under any directory.
The strike was therefore reconstructed from the paper that does exist —
Track AA's own text above, `docs/sitting-prep-2026-08-05.md` §10.11/§10.12,
`tier0/DECISIONS.md` R102 itself, and the two probe reports
(`docs/probe-a-block-offset.md`, `docs/probe-b-fanfare-residual.md`) — and every
clause records which of those sources fixes its content. See R113's
reconstruction note.
