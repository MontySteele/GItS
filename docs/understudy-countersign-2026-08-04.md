# Countersign Package — Understudy Phase-0 Skim Response

**Filed verbatim, as signed.** House convention for a signed package (cf.
`docs/axis-validity-countersign-2026-08-04.md`, `docs/a2-gate-ratification-2026-07-27.md`):
the text [USER] signed is committed unedited, and the repo's own commentary
lives elsewhere — the R-numbers in `tier0/DECISIONS.md` (R93–R97), the
execution record in `docs/sprint-understudy-p1-log-2026-08-04.md`. Nothing
below this heading was written by Code.

---

# Countersign Package — Understudy Phase-0 Skim Response

Date: 2026-08-04. One sitting closes everything Phase-0 left at your gate.
Read top to bottom, edit anything you disagree with, sign at the bottom.
R-numbers get assigned when this lands in DECISIONS.md. Nothing here
touches the sim, the drafter, or any sheet — items that belong to other
streams are routed there, not acted on here.

---

## Ruling 1 — The policy_v1 list: all seven proceed, two with notes

Approved for implementation before the first soak:

| # | revision | note |
|---|---|---|
| 1 | Play free expiring cards first | none — cannot be wrong |
| 2 | Block-panic gating + kill-vs-block check | **routing note below** |
| 3 | Map arm one ply deeper via `leads_to` | land BEFORE any path number is read |
| 4 | Wire the potion arm | plain delegation, entry point exists |
| 5 | Thread `next_fight` into the rest arm | plain delegation |
| 6 | Arm for in-combat choice overlays | closes unscored coverage |
| 7 | Log resolved card NAMES per action | **elevated: P1 BLOCKER** |

**Why #7 is a blocker:** this pass categorized divergences by hand from
prose notes. A thousand-run soak cannot be read that way. A log that
can't be analyzed automatically produces heat, not data — so no soak
launches until names are in the log.

**The routing note on #2:** this revision deliberately makes Understudy's
policy smarter than the tier05 pilot it was ported from. That's the
intended direction — but the insight it encodes ("check whether the
block on offer can actually matter; check whether killing an enemy
removes more incoming than the block prevents") is also a real gap in
the sim's pilot. It goes on the pilot-improvement backlog as a note.
Nobody changes `tier0/pilot/policy.py` for it now.

## Ruling 2 — Phase 2's default changes, on the evidence

The brief pre-registered: if a full LLM run doesn't fit in one session
(M3), Phase 2 falls back to sampling draft picks only. M3 failed, so
that fallback is technically in force — but the same run measured that
draft is where the cheap policy and the LLM already agree most (60%),
and sequencing is where all the disagreement lives (28% on independent
turn-openers). Sampling draft picks would spend the LLM budget where
it helps least.

**Amended default: hard-state turn sampling.** The LLM tier engages at
turn-openings in flagged hard states — cheap triggers computable from
the wire, e.g. incoming above a set fraction of HP, more than one enemy
alive, or lethal within reach. One state read plans the whole turn
(the 117-of-167 finding: planned steps are nearly free). Draft
sampling is dropped from the default and remains available as an
option. The trigger thresholds are P2 design work, not set here.

## Ruling 3 — The seed fork: read-back now, chosen seeds before comparisons

Three options existed: build a Custom-screen arm, go through the
multiplayer lobby, or accept game-generated seeds read back after the
fact.

**Now (P1 launch): read-back.** For soaking — jank filtering, telemetry
harvest — N random recorded seeds are statistically fine, and this
unblocks the soak immediately.

**Before any build-vs-build number is quoted (P1.5): the Custom-screen
arm.** Comparing an old build to a new build requires running the SAME
seed on both — one variable per measurement window. That needs chosen
seeds, so the Custom arm is gated exactly there: not a launch blocker,
mandatory before the first cross-build comparison.

**Noted, not chosen: the lobby route.** Heavier, but it's the one
option that pays twice — Phase 3's two-seat co-op needs the lobby
modelled anyway. If the Custom arm turns out ugly, evaluate the lobby
before building around the ugliness.

## Ruling 4 — The three sim observations: routed, not opened

None of these becomes a new finding or a new ruling. Each goes to the
stream already chartered to handle its family:

1. **`score_offer` returning 0.0** on the draw-on-Encore power → the
   **DRAFTER 13 stream**, as a regression fixture. R87(3) already
   established that DRAFTER 12 prices 42 of 56 ops at zero at offer
   time; this is almost certainly one of them, observed in the wild.
   The Gallery Stirs card becomes a test case: DRAFTER 13 is not done
   while it scores 0.0.
2. **Vulnerable priced as a flat debuff** (can't see a multiplier on an
   engine already running) → the **`_static_power` repricing session**,
   as an exhibit alongside the one it already has.
3. **No defensive term in `_reaction_value`** (Frozen priced as damage
   only) → the **reactions-promotion session**. This is "reactions are
   weather, not strategy" appearing inside the pilot's own head — a
   third independent sighting of the same disease.

## Ruling 5 — Housekeeping

**5a.** The soak launcher's readiness check watches for the `options`
key in the menu state, never the HTTP health endpoint — the server
answers ~20 seconds before the menu has buttons. Written into the P1
spec now, while it's cheap.

**5b.** The floor-9 run on the local profile (seed `SSRWEGLNRG`) may be
abandoned at any time; the measurement is fully captured in the log and
nothing depends on the live save.

**5c.** Merge sequencing as Code proposed: Track A's repair
fast-forwards main first, then Phase-0 rebase-merges on top. No race.

**5d.** The five adapter defects stay recorded as measurement history.
Any future adapter against this wire meets the same five; the list is
the map.

---

## Signature

- [x] Ruling 1 — seven revisions approved, #7 as P1 blocker,
      #2's routing note filed — COUNTERSIGNED
- [x] Ruling 2 — P2 default amended to hard-state turn sampling — COUNTERSIGNED
- [x] Ruling 3 — read-back now, Custom arm gated at first cross-build
      comparison — COUNTERSIGNED
- [x] Ruling 4 — three observations routed as listed — COUNTERSIGNED
- [x] Ruling 5 — acknowledged

[USER], 2026-08-04 — agreed on all points, recorded from review
conversation. Ready for DECISIONS.md entry and hand-back to Code.
