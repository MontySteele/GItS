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
