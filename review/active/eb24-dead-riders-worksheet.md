# EB-24 worksheet — the three dead riders (prepared 2026-08-07)

Ruled at the 2026-08-07 sitting: "yes, let's rework them." Preparing the
reworks surfaced that **all three cards were already reworked** — what the
measured zeros condemn is, in two cases, text that has since been retired,
and in the third, the pilot rather than the card. No new design is proposed
here; what each card needs instead is listed, and none of it is a rework.

## 1. `the_final_verdict` — 0 fires in 298 (RETIRED text)

The 0/298 measured the old card ("damage 18 + 6 Encore if it triggered a
reaction" — fire-rate 0%, "the deadest card in the pool, and the reason it
is here"). Track C.2 of the Fanfare rework (RULED 2026-07-28) already
replaced it with the Hyperbeam: damage equal to Fanfare, then
`crash_fanfare 30` — archetype moved to `fanfare` so the drafter offers it
to the plan that builds its meter. **What it needs:** ratification of X=30
and the negative-floor semantics — both already on the S4-G9 packet.

## 2. `blocking_notes` — 31 fires in 2,471 (RETIRED text)

The ~1.3% measured the old `spotlight_moved_this_turn` draw rider. Track
C.3 (RULED 2026-07-28) already replaced it: "Gain 5 Block, +2 per Companion
played this turn" — the invisible rider became a slope the player can aim
at. **What it needs:** ratification of the 5 / +2 — added to the S4-G9
packet (it was not on the original ~14 list).

## 3. `audience_participation` — drawn 974, played 0 (PILOT DEFECT)

The 974/0 census read is of the CURRENT card (Curtain Call C, R85): a
reaction-read conditional whose else-branch is honest unconditional glue
(2 Encore + 1 draw). It is unplayed because the pilot cannot see it:
`policy._active_effects` unwraps conditionals only for an allowlist of
predicates, `reaction_triggered_this_turn` is not on it, and an unlisted
predicate skips the WHOLE conditional — both branches, including the
unconditional else. Every value term then sees a card with no effects and
scores it ~0, so it is never played and the design is unmeasurable — the
DECISIONS-53 selector lesson again. The predicate is cleanly readable
(`state.reactions_this_turn`, the Chevreuse window). **What it needs:** the
pilot fix, filed as BACKLOG `EB-24p` (a POLICY-stamp surface, so it lands
in its own window, not inside C7). Re-census after the fix; only if the
card is still dead with a sighted pilot does a design question exist.

## Bottom line

EB-24's QUEUE row retires: its ask ("propose reworked conditions") was
already satisfied by Track C.2/C.3 and R85 before it was filed — the row
was measuring ghosts for two of three cards. Remaining work is number
ratification (S4-G9) and one pilot fix (EB-24p). No red-pen sitting needed
beyond S4-G9 itself.

*Provenance: EB-24 (QUEUE, retired 2026-08-07); EB-20 census; Fanfare
rework Track C.2/C.3; R85; `policy.py _active_effects`.*
