# Kokomi Roster v0.1 — Code-Workstream Response & Early Sims

**Date:** 2026-07-24. **Governing doc:** docs/kokomi-kickoff-v1.md (archived
verbatim). **Status:** kickoff roster built and simulated; EVERYTHING here is
PROPOSED — no ruling ask is closed, no number ratified, no band declared.
Cross-session note: docs/kokomi-session-worknote.md (landed before the
schema changes, per standing rule). Suite: 623 green at repo root.

## 1. Design read — what was clear, what needed decisions

The kickoff was implementable nearly as written. The engine already owned
most of her machinery before this session started:

- **The exhaust funnel already exists and is singular.**
  `refpowers.after_card_exhausted` is the one chokepoint every exhaust in
  the game passes through (played-Exhaust routing, mid-card exhausts via
  the per-play sweep, ethereal, the autoplay sweep). The §2.1 "universal
  accrual" rule is therefore one guarded branch, structural rather than
  per-site discipline. The same is true of Strength (`powers.apply_power`
  is the one gain site) — Flawless Strategy is a chokepoint conversion.
- **Her uncommon exhaust-payoff rails were already engine-proven**: Feel No
  Pain (block per exhaust) and Dark Embrace (draw per exhaust) ship with
  the Ironclad parity layer. Mercy of the Deep and Epiphany of the Deep
  reuse them outright — check-if-solved before building machinery.
- **Conscript rode the transform/generation precedents** (PrimalForce's
  transform-at-index, the Guest Star pool grammar) rather than novel
  plumbing.

Decisions I had to make that the kickoff left open (all flagged PROPOSED,
none silently):

1. **Cadence: catalyst** (kickoff silent). She is a catalyst in lore, and
   every-attack-applies-hydro gives the pool its reaction/co-op voice
   without leaning any archetype on reactions. The live alternative is
   skill cadence if hydro-application convergence with Furina bites.
   → new ruling ask (§6 below).
2. **The finisher is her kit Burst, and the roster ships the
   both-with-capstone world**: Ceremonial Garment (Shape B, the kickoff
   recommendation) as the v1.9 kit card on a 50-point meter; Nereid's
   Ascension (Shape A) as a rate-limited draftable Rare (Rare + Exhaust +
   cost 2, every §2.2 limit). This lets the sims INFORM ask 6 instead of
   preempting it — deleting either shape is a one-line change.
3. **Her particle economy**: meter 50; particles from skill tags (5),
   reactions (5), and exhaust events (KOKOMI_BURST_PER_EXHAUST = 2 — her
   Salon-tick analogue). Exhausting fuels both payoff size (Charge) and
   payoff frequency (meter): the §1 decision loop with teeth.
4. **The A4 instrument problem, surfaced now rather than at battery
   freeze**: the kickoff declares elite axes "A2 Scaling + A4 Utility" —
   but in the house axis system A4 is SUSTAIN and A6 is utility, and A4's
   raw is `healing + encore_absorbed`. Kokomi has neither: her stability
   is Block (A3) and ward prevention (damage that never lands anywhere).
   Without an accounting ruling her declared second elite axis is
   **structurally invisible to its own instrument** — the exact Encore
   precedent. Ward prevention is therefore logged as its own event stream
   (`prevent_exhaust`, reported per-fight) and deliberately NOT folded
   into A4 or A3: axis credit is a metric redefinition and metric
   redefinitions are red-pen. → ruling ask.
5. **Starter trio asymmetry**: the reserved trio is three characters
   across the two-slot randomized-starter convention (Klee/Furina are
   2×2). Shipped: the attack slot is Gorou's alone (the adjutant always
   enlists); Sayu/Shinobu contest the support slot. A fourth shortlist
   name would restore symmetry if wanted.
6. **Conscript pool includes the 5★ Rare** (Itto): the random-recruit
   jackpot is the verb's advertised dream ("conscription's favorite
   meal"). Knob if sims show rare-fishing distortion.
7. **Sly scoping**: card-effect discards from hand ONLY — the end-of-turn
   hand flush pays nothing (activity-gating law) and draw-pile discards
   (scry) don't trigger. Loud comments at the one trigger site.
8. **Itto's taunt**: no taunt/redirect verb exists in the DSL. Logged as
   out-of-scope (implement-or-log; NOT silently approximated) — he ships
   as a bruiser body (14 damage + 6 Block).

## 2. What landed (all tested; suite 623 green)

**Engine** (every branch guarded; ref/Klee/Furina paths dead — anchor
untouched):
- Charge: `Player.charge`, `resources.gain_charge`, accrual at the exhaust
  funnel + Strength conversion at `apply_power`, per-combat reset.
- Ops: `gain_charge`, `conscript` (transform mode, `mode: create`,
  `cost_override`), `N_per_M_charge` bonus formulas, Sly resolution in
  `_op_discard`.
- Ceremonial Garment state: `ceremonial_garment` power (DECAYING; stacks =
  turns), attack cards read `charge // GARMENT_CHARGE_DIVISOR` while
  active (KNOB_READS-instrumented).
- Prevention ward: `prevent_exhaust_ward` power + `prevent_damage_exhaust`
  (first unblocked hit per round; prevent up to stacks; exhausts a random
  draw-pile card THROUGH the funnel so the proc is itself a Charge event;
  reshuffles first, and an empty deck cannot pay — the fight clock is
  real).
- engine_closure detector (report-only, R14): flags turns where cards
  created ≥ cards consumed. v0 heuristic; full energy/draw closure
  accounting is a later instrument. KNOWN NOISE: Furina's guest-star
  generators trip it (create-1/exhaust-1 turns) — it is a candidate
  flag, not a verdict.
- Telemetry: `FightStats.prevented / charge_gained / engine_closure_turns`
  (reported, never axis-credited without a ruling).
- SUPPORT_CARRY attribution per ask §6.7 (PROPOSED): conscripted
  companions are self-sourced for control provenance; drafted ones count
  normally.

**Content:**
- `docs/kokomi-cards.yaml` — 33 rows: 5 basics, 11 commons, 9 uncommons,
  7 draftable rares + the kit Burst. Laws 1–4 hold by construction
  (no self-damage op anywhere; one true heal, Rare+Exhaust; no
  strength-granting card; commons net delta ≤ 0).
- `docs/inazuma-companions.yaml` — 14 rows: the reserved trio (Gorou /
  Sayu / Shinobu — Shinobu's canonical self-HP cost DROPPED, errata note
  in the header), Thoma, Kujou Sara, and Itto as the first Inazuma 5★.
  Sara's Tengu Stormcall grants real Strength on purpose: it is the one
  deliberate Flawless-Strategy exerciser (Charge in her hands, Strength
  in anyone else's). Raiden deliberately NOT authored (ask 9).
- `tier0/content/characters/kokomi.yaml` — hp 70, catalyst hydro, meter
  50, kit garment, Tamakushi Casket hook, constraint
  `A2_scaling>A1_frontload` (PROPOSED shape for ask 3), three archetype
  decks + pilots (new `charge` pilot term, inert for everyone else).
- `tools/lint_kokomi_decksize.py` + suite gate — the §1.4 law as a
  machine check. Already earned its keep in-session: see §4.
- The strict-domination lint runs on both new sheets automatically (they
  joined DOCS_CARD_SHEETS).

## 3. Early sim results (discussion input, NOT acceptance)

All numbers below are the frozen tier0 battery at 1000 fights/encounter,
seed 20260719, REF_IRONCLAD = 3.0 anchor. Telemetry probe: 300
fights/encounter. PROPOSED world; no bands.

**World label:** frozen tier0 battery, `--fights 1000`, seed 20260719,
vigil-in-priest package (the pre-vigil run is archived in the session log;
priest A2 6.2 / A4 4.0 there — never compare unlabeled). Telemetry: 300
fights/encounter, same seed.

### 3.1 Seven-axis scorecards (REF_IRONCLAD starter = 3.0)

| axis | starter | commander | priest | assist | MEDIAN |
|---|---|---|---|---|---|
| A1 frontload | **1.3** | 1.8 | 2.1 | 1.0 | 1.8 |
| A2 scaling | **4.7** | 6.0 | **7.7** | 5.4 | **6.0** |
| A3 block | 1.5 | 3.6 | 3.5 | 3.3 | 3.5 |
| A4 sustain | 0.5 | 0.5 | 3.5 | 0.5 | **0.5** |
| A5 velocity | 3.4 | 3.5 | 3.2 | 3.8 | 3.5 |
| A6 utility | 1.8 | 2.2 | 2.8 | 1.7 | 2.2 |
| A7 setup tax | 1.8 | 1.3 | 1.0 | 0.8 | 1.0 |

Winrates (battery pool, 300f telemetry): starter **30.5%**, commander
**78.7%**, priest **91.1%**, assist **34.9%**. Anchors: Klee starter 99.9%,
Furina starter 51.8%, ref_ironclad starter 59.6%.

Constraint `A2_scaling>A1_frontload` holds on starter and median; the
shape heuristic passes everywhere.

### 3.2 What the numbers say (discussion, not verdicts)

1. **The identity landed on its axes.** A1 is genuinely dreadful
   (1.0–2.1), A2 is elite everywhere the engine assembles (4.7 on the
   STARTER, 6.0 median, 7.7 priest). She is a declared scaler from card
   one — which makes ask 3 (A1>A2 scoping) unavoidable exactly as the
   kickoff predicted.
2. **A2 comes with the R19 caveat pre-attached.** Tank-boss curve
   exponents are flat-to-negative (priest −0.48): her late DPT doesn't
   grow so much as her early DPT is tiny, and the ratio instrument
   inflates A1-dreadful engines (the ruled lag-not-growth reading from
   Furina's bands). A 7.7 should be read through that lens before anyone
   panics or celebrates.
3. **A4 median is 0.5 — the floor — while her stability mechanic
   demonstrably works.** Priest with the ward: 14.7 damage/fight
   prevented, hp-loss mean 20.8 (best of her four configs; Klee starter
   is 21.0 for comparison) — but none of it credits any axis, so the
   declared A2+A4 elite pair is HALF invisible to the scorecard. This is
   the N2 instrument ask made concrete: rule the accounting before the
   sheet pass tunes to a broken meter.
4. **Starter is very weak (30.5%; 0% on gauntlet/punisher/tank_boss).**
   Deliberate direction, open magnitude: Furina's ratified starter
   weakness measures 51.8% on the same battery. The starter accrues
   Charge (7.1/fight) that nothing in the starter reads — the engine
   arrives only via drafting, which is the Klee-lesson inversion worth an
   explicit look at red-pen: is 30% the right floor for the stability
   character?
5. **Vigil moved HP trajectory, not winrate.** Adding the ward to priest:
   wr 93.3%→91.1% (noise-range), hp-loss mean 29.0→20.8. That is the
   §2.4 design thesis measured: her HP bar moves less; her deck pays.
   The per-encounter hp-loss stdev matrix is in the probe log — proposed
   stability-band instrument = max per-encounter hp-loss stdev
   (currently: priest 22.6 on tank_boss).
6. **Assist behaves as declared** (34.9% wr, A5-highest, lowest regret
   rate 3.0%): honest glue, no internal payoff. Box Trick philosophy
   confirmed by sim.
7. **Commander runs and the detector watches it.** 78.7% wr, charge
   28.9/fight (highest — conscripts burn hot), and 972 engine_closure
   candidate turns from the create-mode cards. No INFINITE degeneracy
   flags anywhere; the closure detector is doing its report-only job.
8. **The Gardener wall would repeat.** The v0.1 roster shipped with ZERO
   sub-Rare AoE — the exact structural floor that held Furina at 0%
   across three act-1 passes (doc §10.8.2). Caught at review;
   `surging_shoal` (common 4-to-all, mass hydro under her cadence) is now
   ON the sheet but OUTSIDE every measured package, so these battery
   numbers stand unlabeled and packaging it is sheet-pass material. It
   also joins the hydro-convergence watchlist.

## 4. Findings the session itself produced

1. **The deck-size lint caught nothing (yet) — the domination lint caught
   me.** First-draft Communion of Tides (uncommon: Exhaust 1, draw 2)
   strictly dominated Undertow Shuffle (common: draw 2, discard 1): the
   lint sees exhaust-as-benefit, and for Kokomi it IS one. Fixed by the
   CCM remedy — Undertow is now draw 3 / discard 2 (harder churn, two Sly
   bells): churn-vs-fuel is a real choice. The catch→lint culture works
   in both directions.
2. **Itto changed a pinned world.** `test_furina_offers_concentrate_on_
   fontaine` asserted every 5★ reward offer is Mondstadt ("Fontaine has
   no designed 5-stars" fall-through). Inazuma now has one, so the
   assertion pins the construction (fall-through to nations that HAVE
   designed 5★s) instead of the single-nation snapshot. Furina's reward
   world genuinely changed shape: her uniform half now spans two other
   nations.

## 5. Watchlists (registered now, measured at the sheet pass)

- **Multiplicative-read cell**: Nereid's Ascension (meter-read) +
  Judgment of the Depths / Pearl Barrage (pile-reads). The pile-readers
  are bounded by the fight's finite fuel BY construction; the meter-read
  is bounded by Exhaust+Rare+cost. One measurement covers the set.
- **Hydro convergence**: catalyst Kokomi + the existing hydro/cryo
  convergence cells (Furina redpen flag 8). If her application density
  distorts the freeze economy, the cadence ask (skill cadence) is the
  lever — not per-card nerfs.
- **Conscript rare-fishing**: Itto-in-pool as jackpot. Knob: rarity
  weighting on `companion_pool`, currently uniform.
- **engine_closure noise**: Furina generator turns trip the v0 detector;
  if it graduates from report-only, it needs the energy/draw-closure term
  before any gate.

## 6. Ruling asks (kickoff asks 1–10 all still open; new asks from this pass)

The kickoff's ten asks remain [USER]-gated and untouched. This pass ADDS:

- **N1 — Cadence**: catalyst (shipped, PROPOSED) vs skill. Blocks nothing
  now; blocks the sheet pass.
- **N2 — A4 instrument**: the kickoff's "A2 + A4 Utility" elite pair
  needs (a) the A4-vs-A6 naming clarified (A4 is sustain in the house
  system), and (b) an accounting ruling for ward prevention (own event
  stream → A4, the Encore precedent, is the natural shape; currently
  reported-only). Without it her second elite axis cannot be measured
  honestly — declared identity vs instrument gap, surfaced before
  anyone tunes to a broken meter.
- **N3 — Starter trio geometry**: Gorou-always in the attack slot
  (shipped) vs adding a fourth shortlist name for 2×2 symmetry.
- **N4 — KOKOMI_BURST_PER_EXHAUST = 2 and meter 50**: her burst cadence
  in the batteries below is a direct function of these; both are knobs.
- **N5 — Conscript pool geometry**: uniform over all draftable Inazuma
  rarities incl. the 5★ (shipped) vs rarity-weighted.

## 7. Non-goals honored

No DECISIONS.md entries written (ask closure is [USER]-only). No bands, no
winrate floors, no C# mod work, no tier05/act batteries (kickoff §8), no
healing-law text touched, no art. The sheet pass proper starts only when
asks 1–10 close (§9 of the kickoff).
