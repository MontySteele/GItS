# Axis-Validity Design Session — Charter (v0.2, PROPOSED)

Date: 2026-08-04. Status: **RATIFIED 2026-08-04 — AV-G2 countersigned via [USER] go-ahead** (A-G1 and B-G1 remain deferred gates).
Discharges the session opened by **D3** (2026-07-26). Supersedes the v0.1 draft
of the same day; v0.2 folds in three review passes conducted in-session:
(i) the GItS sheet audit (219 cards), (ii) the two-anchor canon audit
(Silent 92 / Ironclad 91, wiki route), (iii) the remaining-roster canon audit
(Defect 91 / Necrobinder 91 / Regent 91, wiki route).

**Canon card count — CORRECTED 2026-08-04 (R92/3a).** This line read "402
canon cards total", which was an arithmetic slip: it is neither the wiki sum
(456) nor anything else. The DLL prints **439**, of which **410 are
draftable** (5 × 82 common+uncommon+rare); the wiki route runs 3–4 high per
pool, flat, exactly as the caveat below predicted. **No percentage in this
charter moves**, because every percentage in it is within-pool. Full
reconciliation table: `docs/role-tempo-baseline.md` §0.

Sequencing per D3 §2: after EPOCH 1 (landed 2026-07-26) — clear. Before the
Zhongli deep dive — R88 sits in DRAFT on this session, so this is the blocker.

Canon-data caveat, standing: all canon numbers here are **wiki-derived and
within-pool percentages only** (wiki runs ~4 high vs DLL on raw counts;
percentages are the reliable signal). Wiki text lags monthly balance patches.
**Owed to Code: re-verification against local DLL extraction** (`game_ref/`,
gitignored, cannot reproduce in cloud — flagged, not approximated).

---

## §1. The R87(1) pre-registered question: GRADED

> *Is the pilot simply BETTER at Salon than at the other archetypes, or does
> everything feed Salon BY CONSTRUCTION?*

**Verdict: BY CONSTRUCTION.** Instrument: three-seat human co-op playtest
(Klee / Kokomi / Furina), Acts 1–3, build `0.2-247`, 2026-08-01/02 — the
holdout D3 named, never visible to any design loop. [USER]'s report:

1. Fanfare and companion options read strictly weaker than Salon spam to a
   human pilot with full-kit knowledge — eliminating the sim-pilot-limitation
   alternative hypothesis.
2. Mechanism identified, structural not numeric: the game demands upfront
   numbers early and multiplicative scaling late; **Fanfare is a flat adder —
   the wrong shape at both ends.** Too slow to generate early (payoff may not
   be drafted); underwhelming damage late (serviceable block).
3. Consistent with the Curtain Call null (R85 world): payoff-reach was never
   an odds problem — the cards the archetype needed at that tempo band did
   not exist at any rarity. Frozen-drafter and human evidence now agree.

Consequences (PROPOSED): R87(1)'s "no Furina balance value moves" standing
converts from *waiting on the playtest* to *waiting on Track A's first lint
run* (§3) — the three deferred items are one coverage question and get
patched against a defined coverage target, not card-by-card. The fanfare
STOP holds until the fanfare cells have floors to fill toward.

## §2. Diagnosis — REVISED against canon

v0.1 claimed mechanics-first generation was the disease: kit-serving cards
become resource-delta carriers. **The canon audit falsified half of that.**
Every official pool carries a mechanic-machinery layer at comparable density
to ours (Defect orb plumbing ~16% of pool, Regent Forge/Stars ~13%,
Necrobinder Summon verbs ~5%; ours ~12%). Carriers are not the disease.

The difference is where the carriers' roles live: **canon tokens cash into
role-diverse, legible payoffs.** Lightning IS scaling damage; Frost IS
block; Osty attacks AND shields, visibly, with numbers on screen. A canon
carrier's role is readable through its token. Our failure mode is a token
(early-game Fanfare) with no payoff of the demanded shape at the demanded
band — so its carriers have no role to inherit, and the archetype is
correctly routed around by drafter and human alike.

Three playtest findings remain one finding on different surfaces:
same-y pools (role coverage), the Act 1 easy / Act 2 wall / Act 3 easy curve
(output shape vs demand curve, unmeasured), and the end-of-turn trigger
cascade (legibility — distinct cards *feel* identical when damage cannot be
attributed to card). The distinctness gates (R81) measure pairwise textual
difference; they are necessary, stay, and cannot see any of the above.

**Catch → lint, third instance:** Klee ("more varied effects than delayed
damage"), Furina (Fanfare payoff-reach, caught twice), Kokomi ("machinery
fun, card pool iffy"). The class becomes an automated gate.

## §3. Track A — Extend `solve`, add tempo, lint coverage

**Not greenfield — v0.1 was wrong about scope.** All three ratified sheets
already carry multi-valued `solve:` with vocabulary
`frontload | scaling | block | sustain | velocity | utility`
(219/219 cards tagged; Furina 33/82 multi, Kokomi 34/61, Klee 7/76).
Track A **extends this field**; no parallel `combat_role` field is created
(two fields answering "what does this card do" will drift).

**A0 — Vocabulary amendments (PROPOSED, canon-validated):**
- Add **`support`** — co-op roles. Present in every canon pool at ~2–7%
  (Flanking, Tank, Blade Symphony, Ignition, Imitation Learning, Largesse,
  Legion of Bone…), concentrated in the two new characters. Kokomi's Assist
  archetype lives here and the current vocabulary cannot see it. D4 clause
  written in at birth: the sim is one-seat, so support cells are graded by
  play sessions only, never sim-predicted.
- **`aoe` is a modifier tag, not a role** — delivery shape (14 GItS cards,
  ~15% of canon attacks); the swarm axis already exists to care about it.
- Add **`tempo_band:`** — the genuinely new axis. Two orthogonal scales:
  `fight: early|mid|late` and `run: early|late` (a scaling Power is
  fight-late and must be run-early-draftable to assemble by Act 2 — the
  playtest's Act 2 wall is this cell failing at party scale). Multi-band
  legal; threshold and "pays on the way down" cards wear two bands.

**A0.1 — Tag-through rule (PROPOSED RULING, number on ratification):**
*A mechanic-carrier card inherits the `solve` roles its token or resource
cashes into.* Zap tags scaling through Lightning; Glacier tags block through
Frost; Poke tags frontload through Osty; `generate_guest_star` tags through
the companion generated. **Corollary, load-bearing:** a carrier that
inherits no role at a tempo band is a structural defect of the *resource*,
not the card — this is exactly the Fanfare disease, and the rule makes the
lint detect it without a special case.

**A0.2 — Design-space protections (PROPOSED RULING):**
1. **The lint is floors-only.** Pools fail for under-floor cells; **no card
   can ever fail** for being unclassifiable, hybrid, or strange.
2. **`utility` is protected free space, never linted, never split.** Canon
   spends 3–7% of each pool on genuinely role-less cards (Echo Form, Burst,
   Nightmare, BEGONE!, Buffer) — the same space our `move_bombs`,
   `conscript`, `replay_next_companion`, `copy_companions_played_this_combat`
   live in. Canon legitimizes every one of our novel verbs by direct
   analogue (Shiv economy ≈ guest stars/bombs; replay/copy family ≈
   companion replay; Master Planner/Bullet Time ≈ `cost_mod`).
3. **Floors are per-identity, from declared archetypes** (sheet header
   canonical per R66) — never universal. Canon variance proves some empty
   cells are identity statements: sustain runs 1% (Silent) to 15%
   (Ironclad); disrupt 3% (Defect) to 14% (Ironclad). Klee at zero sustain
   is Silent-shaped, not deficient.
   > **Amended by R91/2d, 2026-08-04.** The "15% (Ironclad)" counted
   > BETWEEN-FIGHT healing, which a combat taxonomy rightly ignores. Under
   > the ruled definition — sustain is in-combat healing and prevention of
   > YOUR OWN HP; enemy-output reduction (Weak, Frail) is disrupt; absorbing
   > a hit this turn is block — canon carries **0.0–2.3%** sustain.
   > Consequence: `sustain` is NEVER LINTED, beside `utility` and `support`.
   > The clause's conclusion outlives its number: zero sustain is a legal
   > identity.
   >
   > **Amended by R90/1c, same day.** "Per-identity" now also means
   > per-POPULATION: an archetype is measured against the canon PACKAGE
   > shaped like it, not against a whole 88-card canon pool. See
   > `docs/role-tempo-baseline.md` §5.

**A1 — Baseline extraction.** The (solve × tempo_band × rarity) matrix for
all five canon pools, percentages, per-identity. Wiki route now; DLL
re-verification owed. Necrobinder is designated **Furina's summon-economy
anchor** (the canon character her machinery most resembles). Deliverable:
`docs/role-tempo-baseline.md` + machine-readable floors.

**A2 — Tagging pass, three sheets** (add `tempo_band`, apply A0 amendments
and tag-through to existing `solve`). Code tags mechanically; **[USER] gate
A-G1** reviews assignments — tag-through targets especially, since a token's
payoff set is a design fact.

**A3 — `lint_role_tempo_coverage.py`.** Fails a pool when a declared
archetype is under-floor in a mandatory cell. Joins the lint battery; suite
green at the track boundary. **Pre-registered predictions, instrument = the
lint itself against the tagged sheets (D4-visible):**
- P1: first run fails Furina on (fanfare × frontload × fight-early) and
  (fanfare × scaling × fight-late). **Binding null:** if these cells pass
  as currently authored, the taxonomy is mis-specified and Track A returns
  to design.
- P2: at least one Klee bomb cell and one Kokomi cell fail.
- P3 (metric, not gate): Klee multi-solve rises toward the canon floor in
  her rework — currently 9% vs canon range 29% (Regent, the deliberately
  simple character) to 51% (Ironclad).
- Noted, downgraded from v0.1: party-wide disrupt (all three characters at
  the canon *minimum* simultaneously; multiplied in co-op) is a **Kokomi-
  rework note**, not a lint failure — per-identity floors rule it in-band.

**A4 — PROPOSED RULING: "Kit in the keywords, verbs in the cards."**
Restated post-canon: the kit lives in the resource/token layer, **and every
token must cash into payoffs that cover its archetype's mandatory cells.**
Binding on Zhongli (R88) and Fontaine Rares before either authors a card.

## §4. Track B — Curve-shape instrumentation

Unchanged from v0.1 in structure; adopts the Acts 2/3 telemetry-first work.
B1: empirical demand curve (incoming damage / required output per turn, per
act, per fight class). B2: archetype output curves overlaid — "Fanfare is a
flat adder" becomes a gradeable shape, **diagnostic surface, never an
acceptance target** (R14). B3: per-axis disposition of the seven-axis
scorecard against both holdouts (this playtest; `realistic_axis_scores.py`)
— each axis individually confirmed / retired / left parked; blanket
restoration off the table. D4 note: party-level claims are sim-scoped
one-seat; the three-seat Act 2 wall is co-op evidence graded by play only.

## §5. Track C — Legibility principle (ratify only)

**Attributability is part of distinctness**: a card whose effect cannot be
attributed to it at the table gets no credit for being different. Canon
evidence: token legibility is *how* official carriers stay readable — orbs
sit on screen with numbers and fire in order; Osty's contribution is drawn.
Execution stays where it lives (Furina summon numbers + Kokomi jellyfish →
Animation Sprint 2 / art pipeline; Klee variety → her rework under the
matrix); this session only makes the principle a requirement those sprints
inherit.

## §6. Sequencing

1. This session ratifies §1, A0–A0.2, A4, §5. Then:
2. **Track A** first (sheet-and-tools, collides with nothing, blocking
   input to three queued items). Track B in parallel (separate surface).
3. **Furina balance pass** on A3's first lint run; R87(1) items 1–3 route
   here. **Kokomi pool rework** inherits the matrix (starvation numbers
   become cell findings; disrupt note rides along).
4. **Zhongli** unblocks on A4 + B3 — the D3 fence held as drafted. The
   alternative (A4 only, accepting slot 4 declares axes against a parked
   framework) was offered and stands rejected unless [USER] says "A only."
5. DRAFTER 13 (R87(3)) proceeds independently; nothing here reads prices.
6. `_static_power` repricing reads B2's curves when it opens.

Non-goals: no balance value moves; no card authored or reworked; no axis
band ratified; no new keyword or subsystem (standing rule — everything in
Track A is measurement and vocabulary on existing fields).

## §7. [USER] gates (triaged)

Live now: **AV-G2** — countersign the ratification bundle in §6.1 (one
signature; §1's grade quotes your own report, the principles you've assented
to in session, the canon evidence is attached).
Deferred until artifacts exist: **A-G1** (tag review, esp. tag-through
targets) · **B-G1** (per-axis disposition).

> **A-G1 DISCHARGED 2026-08-04.** Countersigned at
> `docs/axis-validity-countersign-2026-08-04.md`; recorded as R90 (the null's
> direction), R91 (the tag review), R92 (housekeeping). The seven entity
> payoffs confirmed as proposed, the salon double-credit kept with a
> bounded-meter amendment, meter-reading damage ruled, the sustain boundary
> clarified. Tags are LANDED on all three sheets and `tempo_band` is on the
> schema. **B-G1 remains deferred**, and §3's P1 now lives there: per R90/1b
> it was *aimed at the wrong instrument; withdrawn and re-registered, not
> failed.*
Discharged in session: vocabulary review (validated against ~~402~~ **439** canon
cards); the Zhongli fork (held, per §6.4, silence = stands).
