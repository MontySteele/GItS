# Errata + Tier 0.5 M5 Triage — Rulings

From chat-Claude, on `klee-errata-report.md` and `tier05-m5-report.md`.

## Errata items

**1. Demolition 97.4% at 1000 fights → ARM THE SPLASH CAP.** Correct call leaving it dormant — the cap's written trigger was the median check, not the band check — and correct call pre-measuring anyway: 96.5% in-band with swarm/gauntlet unharmed is exactly the evidence needed to rule in one round instead of two. Trigger definition now extended: **the splash cap is the sanctioned demolition ceiling knob for band violations as well.** Sheet v0.4 (ships with this doc) codifies `splash_procs_per_turn: 3` on blazing_delight so the knob lives in the design artifact, not just the engine. Flip the xfail.

**2. The Frozen elite-drop null — logged as a real design insight, not just a curiosity.** Solo Frozen firing 0.01×/fight because Klee's catalyst cadence eats every hydro/cryo aura before it can pair means: **catalyst-grade characters structurally suppress freeze-pair play solo.** The mispriced stun was always a co-op exposure, which (a) retroactively confirms the redesign was aimed at the right venue since co-op is the actual use case, and (b) means the first Skill-grade character (Furina) will experience Frozen at *dramatically* higher rates than any Klee data suggests — her sim passes must not inherit Klee-derived Frozen expectations. Added to the cadence-dial's documented effects.

## Tier 0.5 M5 structural findings

**3. ~0% run completion → ruling in three parts.**
(a) **Your recommendation is ratified as far as it goes:** run winrate is not a v1 acceptance metric, and M6 harvesting boss-reached emergent decks into the Tier 0 battery is adopted — it's the clean hybrid (draft realism feeding calibrated fight-level measurement) and becomes the acceptance-grid mechanism going forward.
(b) **But add a progression compensator, because truncation is confounding everything downstream.** The no-upgrades/no-relics gap isn't just suppressing an unused metric — it's cutting runs short, which silently truncates the drafting metrics (finding 4 below is measured on runs that mostly die at the first elite; assembly rates on truncated runs undercount by construction). Fix: a single enemy-stat scalar by node position (one constant per node-tier: normal/elite/boss), grid-searched **on the REF_IRONCLAD anchor only** until anchor run completion lands at 45%±10 (roughly a competent-baseline real-game rate), then frozen and labeled in constants.py as PROGRESSION_GAP_COMPENSATOR with a comment that it is one number standing in for upgrades+relics, not a model of them. Scope-line check: this tunes OUR battery statlines behaviorally, exactly how the battery was calibrated in M2 — it does not model their map/economy.
(c) The fragility instrument itself (death-node heatmaps, HP bands, elite clustering) is validated and untouched — it found the structural gap on its first run, which is the instrument working.

**4. Reaction core assembly <1% → RE-MEASURE FIRST, with a pre-authorized escalation.** This number is currently uninterpretable: it's the pool math AND the truncation confound in one figure. Sequence: land the compensator, re-run M5 metrics on full-length runs, then read. Pre-authorization so you don't need a round-trip: **if post-compensator reaction assembly is still <15%, pull pity mode forward from M7 into M6** (pity(3): three companion-less reward screens → next offer is choose-3) and re-measure at pity(3) and pity(2). Demolition at 26% for the *default* archetype and the spark/demolition gap (4% vs 26%) are both flagged as watch-items for the re-measure — if demolition doesn't rise substantially on full-length runs, the archetype-core definitions may be too strict, which is a metrics question before it's a pool question.

## Standing note
The M5 report's structure — knob trail on the completion problem before recommending, pre-measuring the splash cap before asking — is the standard now. Both findings came back decision-ready. Keep doing that.
