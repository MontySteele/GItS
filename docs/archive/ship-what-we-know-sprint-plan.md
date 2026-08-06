# Implementation Sprint — "Ship What We Know"

> **Lifecycle: ARCHIVED** — superseded; kept verbatim as a record and never updated. Status index: `docs/registry/identifiers.md` §15.

Verbatim record of the governing sprint doc from the 2026-07-25 co-op playtest
review (house rule: no chat-side-only artifacts). Execution log:
docs/ship-what-we-know-sprint-log.md.

---

Date: 2026-07-25. Direction RATIFIED by user; every NUMBER is PROPOSED pending red-pen. Governing intent, verbatim: "Let's take everything we already know about and implement it so we don't stack a giant backlog of design ideas on top of one another." This sprint therefore contains zero new design. Every item below is either a known bug, a known gap, a ratified-but-unshipped design, a known-weak number, or an instrument the next design pass is already blocked on. Anything that smells like a new idea goes to §Non-goals.

Inputs: co-op A0 playtest 2026-07-25 (Klee + Furina, two A8-regular players, full clear "by the skin of our teeth"; verbatim notes recorded in G-F3) · docs/furina-fanfare-sprint-log.md incl. close-out and both ghost checks · the fanfare sprint's F-D/F-E deferrals · klee-mod DECISIONS ("Funnel Contract") · tier05/draft.py instrument bugs as documented in the close-out.

The decoder fact governing this sprint: the playtest note "Furina fanfare still capped" confirms the live build predates the read-only Fanfare rework — F-D never opened, so the C# layer still implements the retired spendable/capped design. Until G-A lands, every live playtest generates feedback against a kit that no longer exists in the design of record. G-A is therefore blocking, and playtest findings are triaged below with that lens (some notes describe the superseded kit, not a bug).

## Ordering law

G-A first among all Furina-touching items — it unblocks meaningful playtesting and the G-D4 ruling, and the animation stream is editing the same file's display sites today. G-B is independent and can land any time. G-C, G-E, G-F run parallel. G-D's numbers land whenever, but its red-pen session should happen once, late, over the whole set.

## Track G-A — C# parity: the orphaned F-D (BLOCKING)

The fanfare sprint closed with the read-only package ratified, tested, and shipped to sim + sheet — and hard-gated F-D behind an F-C that will never run. This track is F-D resurrected as its own pass with its own modest acceptance, decoupled from the dead F-C bars.

* G-A1. Port the ratified engine behavior to the C# command layer (`Powers/FurinaResources.cs` + call sites): proportional decay (`FANFARE_DECAY_FRACTION 0.20` of the meter, clamped at floor, ≥1 removed while above floor, from turn 2, at the true top of the player turn before Salon upkeep); floor state (grant raises floor + cap + current together; floors reset per combat — port the cap-rewind fix, it was a real bug in sim and will be a real bug here); Power grants (+5 common/uncommon, +8 rare, once per card after resolution); no spend path (`fanfare_cost` has no C# meaning anymore — delete its payment/gate branches).
* G-A2. Un-defer `the_sea_is_my_stage` and `lasting_impression`: `gain_fanfare_floor` gets its C# home, codegen emits both cards, and the `FURINA_DEFERRED_TO_FD` curated set in `tier0/tests/test_roster_codegen.py` empties (kept, not deleted — the invariant stays asserted positively, per the `florid_cadenza` precedent).
* G-A3. Call-site census in the PR description: every C# site that reads or writes Fanfare, each marked ported / deleted / display-only (the C3 lesson; a missed site is a stale value and the next playtest report).
* G-A4. Funnel Contract check (klee-mod DECISIONS): Fanfare is explicitly OUT of contract, so this track is free to move it — but the animation stream is editing display call sites in this file now. Expect gauge/stage Refresh calls at the Encore funnels; leave them in place (display-only, own no state). If any Encore funnel identity would change, note it in both logs BEFORE landing. Nothing in G-A1 should require that.
* G-A5. Acceptance: (a) a scripted parity fight — same seed, same scripted plays — produces the same Fanfare trajectory in sim and in a C# harness/log dump, turn by turn; (b) [USER] eyes-on live capture showing the meter decaying, flooring on a Power play, and never being spent; (c) suite + codegen green. No winrate bar — this track ships behavior, not balance.

## Track G-B — Co-op correctness

* G-B1. Best Friends Forever ownership bug (playtest: "pulled the co-op partner's cards"). Root cause is visible in the generated C#: `CompanionPlays.PlayedThisCombat(CombatState!)` is combat-wide and the result is never filtered by `Owner`. Fix: owner-scoped query (or filter on the play records' owner) so the card copies your companions played this combat. Sheet text unchanged — the yaml op (`copy_companions_played_this_combat`) always meant the owner's.
* G-B2. Bug-class audit, not just the instance (house pattern: structurally-invisible defects). Census every C# consumer of combat-wide trackers (`PlayedThisCombat`, `CombatState`-scoped histories, "this combat" counters) that feeds a card effect, and mark each owner-scoped / correctly-global / needs-fix. Co-op is the config where these diverge, and — worth recording in the log explicitly — co-op has no sim backstop: tier 0.5 models one seat. Every co-op finding is play-derived until that changes (and changing it is a design-stage question, not this sprint).
* G-B3. Regression: a co-op-shaped unit test for G-B1's fix (two owners, interleaved companion plays, assert the copy set), so the bug class has at least one tripwire in the suite.

## Track G-C — Upgrade-coverage lint + known gaps

* G-C1. New `tools/lint_upgrade_coverage.py` (house lint conventions, sits beside `lint_unique_names` et al.): every draftable card across all sheets has an entry in its `*-upgrades.yaml`, or is on a curated exemption list with a reason (the existing header precedents: Bursts are kit, Guest Stars upgrade via their generator). Companions are IN scope — the `eager_to_help` precedent already has companion cards upgrading. Wire it into the test suite so a missing upgrade is red, not a playtest note.
* G-C2. Fill what the lint finds. Known from the playtest: `nicole_celestial_gift` (mondstadt-companions.yaml carries no upgrade entries at all — the lint will likely surface the whole companion class, which is exactly why it's a lint and not a spot-fix). Deltas PROPOSED per the upgrade-conventions grammar; red-pen with G-D.
* G-C3. Starting-relic upgrade forms ([USER]-clarified 2026-07-25). Touch of Orobas is a base-game act-2 ancient reward that upgrades the character's starting relic; base-game characters register upgraded forms, modded characters don't, so on Klee/Furina it swapped the starter for an effect-less placeholder — a strict downgrade dressed as a reward. Work items:
   * (a) Decompile check first (house norm): find the exact registration surface Touch of Orobas resolves upgraded forms through — the fix plugs into vanilla's mechanism, it doesn't reinvent it.
   * (b) Register upgraded variants for every modded starter: Pounding Surprise (Klee, `spark_on_detonation`) and Ethereal Spotlight (Furina, the Spotlight selector) — Kokomi's rides along only if her starter relic already exists in-tree. Upgrade deltas are PROPOSED conservative tune-ups of the existing effect (same hook, better numbers — the card-upgrade grammar applied to relics), red-penned with G-D. No new mechanics: an upgraded starter that changes behavior is pool-sweep material, not this sprint.
   * (c) Sim parity: tier05 already models act-2 ancients (`relics.yaml: ancient:`), so add the upgraded hook variants to tier0/tier05 and model the swap, or record explicitly in the log that Orobas-class relics are outside the sim's relic model — either is fine; silent divergence is not.
   * (d) Curated-invariant test (the placeholder is a structurally-invisible defect): every roster character's starting relic has a registered upgraded form; Touch of Orobas applied to each yields it and never a placeholder.

## Track G-D — Known-weak and known-confusing cards (bounded list)

This is NOT the pool sweep (see §Non-goals). It is exactly the cards the playtest named, plus one ruling. All numbers PROPOSED; one red-pen session over the whole set.

* G-D1. `rain_of_roses` (Furina rare, 2-cost, salon/spotlight payoff) — "weak" at 2 energy is consistent with the v2 reprice lesson (rares were overpriced as a tier). Candidate: cost or effect up; number at red-pen.
* G-D2. `star_of_the_show` (Furina rare power, +3 printed per Spotlight copy) — "weak" and consistent with spotlight's measured 2.3% line. Bounded fix: the magnitude, not the archetype (spotlight's structural problems belong to the pool sweep).
* G-D3. `controlled_demolition` (Klee uncommon, X-cost enabler) — "seems weak"; X-cost enablers price against their best turn and play their median one. Candidate: base rider so X=0..1 isn't dead.
* G-D4. `ebb_and_flow` ruling (spend 1 Encore, gain Encore + draw). In the live (pre-G-A) build the churn feeds a pinned meter and is genuinely pointless — the playtest "???" was correct about the build it played. In the design of record the churn is flux that a decaying meter actually wants. Decide AFTER G-A lands, against the real design: either the text says what the churn is for (legibility item, cheap) or the card still fails to justify itself and gets a redesign slot in the pool sweep. The ruling this sprint makes is only which of those two it is.

## Track G-E — Instruments & anchors (everything the next pass is blocked on)

* G-E1. Fix `core_complete("fanfare")` (tier05/draft.py:249) to require at least one payoff/reader, per the close-out's standing instruction that nothing be measured against it until then. Re-print the ghost-check online% under the fixed definition (one command) so the draft-reach pass opens with a truthful instrument.
* G-E2. Re-anchor the roster under RUNTEMPLATE 7: Klee and ref_ironclad, realistic, seed 11, 600+ runs — same worlds as the v7 ghost check, so salon's 18.5% finally has same-world anchors. This unblocks the standing salon ruling (which itself stays out of scope).
* G-E3. Free-drafting pilot variant — instrument only. The tier-0.5 drafter is plan-committed: it forces an archetype through every reward screen, so it structurally cannot see the playtest's headline finding (archetype cards losing screens to neutral engine pieces — the player "went for engine pieces… rarely bothered" with Salon while the sim calls salon dominant). Build the non-committed scorer (cards compete on standalone + synergy value; POLICY_VERSION bump per house discipline) and run ONE measurement cell: salon under free draft vs plan-committed, v7, seed 11. The number goes in the log as the opening evidence of the pool-sweep pass. The design response to whatever it shows is out of scope here — this track ends at the measurement.
* G-E4. Sim-vs-player calibration note, one paragraph in principles: absolute sim winrates are pilot-limited floors, not human predictions; the instrument's authority is relative deltas and structural findings (saturation, reach, decoupled limbs — each of which the playtest agreed with directionally). "Sims are worse than real players" is now confirmed and goes in the doc so it stops being re-litigated per pass.

## Track G-F — Doc hygiene (small, known, overdue)

* G-F1. Kickoff §4: annotate the uncapper clause as retired grammar with a pointer to the DECISIONS entry (one line; not an amendment — the no-accrual law is untouched and F-B4's non-opening reasoning stands).
* G-F2. Fanfare sprint log: one bookkeeping line confirming the decay ruling took the conservative 20% (vs the proposed 10%) deliberately, so the ruling's placement ahead of its evidence in the log's physical order doesn't read as ruling-before-measurement.
* G-F3. `docs/playtest-2026-07-25-coop-a0.md`: the verbatim playtest notes, the build decoder (pre-F-D — which findings describe the superseded kit), the triage mapping each note to its track here, and the two observations this sprint deliberately does NOT act on: Salon going unused in co-op free-draft (evidence for the pool-sweep pass, via G-E3), and A0 feeling skin-of-teeth to A8 players (one more playtest before it's a finding — learning curve and floor-difficulty are not yet separable).

## Non-goals (explicit — this is the backlog we are NOT stacking)

* The card-pool sweep / draft-reach design pass. It is the next pass, it opens with G-E1's fixed instrument and G-E3's measurement in hand, and it inherits: salon-felt-weak vs salon-sims-strong, the fanfare reach null, spotlight's collapse, per-archetype own-payoff reach measurement, pool dilution, drafter valuation, and any G-D4 redesign. Nothing from that list gets "just quickly" done here.
* The salon trim/intentional ruling — needs G-E2's anchors first.
* Any new Fanfare, Encore, or Salon design. The resource rework is closed; this sprint ships it, full stop.
* Co-op sim modeling — real gap, design-stage question, noted in G-B2's log entry and not started.
* A0 difficulty tuning — one more playtest first (G-F3).
* Kokomi anything.

## Gates & rulings

* [USER]: G-A5's live capture · the single red-pen session over G-D + G-C2 numbers + G-C3(b)'s relic deltas · G-D4's ruling (after G-A) · `lasting_impression` lore audit rides along if still outstanding. (G-C3's clarification is received and folded in — no open question remains on it.)
* Hard gate: G-D4 does not get decided before G-A lands.
* Null discipline: G-E3's measurement is recorded whatever it shows; if free-draft salon holds near plan-committed salon, the "sim artifact" hypothesis is weakened and the pool-sweep pass opens knowing that.

## Risks & mitigations

* Parity drift: C# reimplementation quietly diverging from sim. Mitigation: G-A5(a)'s turn-by-turn trace parity is the acceptance, not an aspiration; divergence is a bug in G-A by definition.
* Two streams in one file: animation is editing FurinaResources.cs display sites now. Mitigation: G-A4's leave-Refresh-calls rule + note before landing anything that moves an Encore funnel.
* Lint scope-creep: G-C1 discovering a large companion gap and turning into a design session. Mitigation: fills are PROPOSED conventional deltas; anything contentious is listed and deferred to red-pen, not workshopped inline.
* The free-draft scorer is itself design-flavored. Kept honest by G-E3's hard stop at one measurement cell and a POLICY_VERSION stamp so its numbers never mix with plan-committed ones.

## Definition of done

The live build implements the design of record: Fanfare decays, floors, and cannot be spent, verified by trace parity and a live capture. BFF copies its owner's companions and the bug class has a census and a tripwire test. No draftable card lacks an upgrade path without a curated reason. The playtest's named cards have red-penned numbers and `ebb_and_flow` has its ruling. The instruments the next pass needs — truthful `core_complete`, v7 anchors, a free-drafting scorer with its first measurement — exist and are logged. The playtest itself is in the repo with its build-decoder, and the backlog for the pool-sweep pass is written down in one place instead of stacked on top of this one.
