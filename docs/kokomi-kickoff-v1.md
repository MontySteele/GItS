# Kokomi Character Kickoff — v1

(Received from design chat 2026-07-23; archived verbatim per the
no-chat-side-only-artifacts rule. The Code-workstream response is
docs/kokomi-roster-v0.1-report.md.)

Status: DRAFT — ruling asks open, constants proposed not ratified
Owner: design chat → hands off to Kokomi Claude Code workstream on close
Slot: 3 (per roster amendment A1)

## 0. Governing inputs

- Roster amendment A1–A4 (2026-07-23): Kokomi confirmed slot 3. The healing
  amendment is an output of this thread. Both co-op-forward characters carry
  the hard solo-viability gate (A2). Act-weighted composite form
  pre-registered (A3); constants remain [USER]-gated at battery freeze.
- Slot-4 ruling (this thread): Zhongli takes slot 4. Supersedes the
  Itto-vs-Zhongli open item in A1. Consequence: Itto is now eligible for the
  Inazuma companion pool (mirror of the Neuvillette-reserved pattern in
  reverse). Record in DECISIONS.md.
- Healing law (conjunctive): true in-combat healing is Rare AND Exhaust;
  sub-Rare sustain routes through Block (incl. pre-emptive/delayed Block) or
  capped buffer pools. Potions and relic-scale trickles exempt by existing
  policy.
- Volatility/stability axis (standing): Furina = HP volatility, Kokomi = HP
  stability. Element spread accepted (second Hydro).
- SUPPORT_CARRY / enabler-not-carry, control_uptime detector, KNOB_READS law,
  one-variable-per-window discipline, dose/oracle-cells-are-diagnostics
  (R14), reserved-card-names lint, [USER]-only closure of gated items — all
  binding as usual.
- Klee lesson applied: kit-critical mechanics live at kit level, not as
  draftable rares (Burst ~10% acquisition → burst-as-kit ruling). Kokomi's
  Charge engine is therefore kit-level (relic + starter), never draft-gated.
- R16 spirit respected: power in the cards, not the relic. Kokomi's relic
  carries bookkeeping and conversion rules (Charge accrual, Strength
  conversion); all payoff magnitude lives in cards.

## 1. Identity declaration

Sangonomiya Kokomi — Hydro. General and priest of Watatsumi Island.

Identity sentence: Kokomi converts card economy into damage. She pays in
cards, never in HP.

Binding character laws:

1. No self-damage anywhere in her kit or personal pool. Her risk axis is
   tempo and card economy exclusively. The moment a Kokomi card costs HP,
   the Furina boundary blurs. (Extends to shared-pool errata below:
   Shinobu.)
2. No healing exception taken. This thread's healing-amendment output is: no
   amendment. The conjunctive law stands unmodified. Kokomi builds Block and
   Charge, not HP. Her "healer" fantasy is expressed through damage
   prevention, Block, and the fact that the law's Rare+Exhaust heals are
   themselves premium Charge events (§2.1).
3. Flawless Strategy (the Genshin twist): Kokomi cannot gain Strength. Any
   Strength she would gain becomes Charge instead. This is the −100% crit
   trade translated: all damage scaling routes exclusively through the
   priest identity. It is simultaneously the lore wink and the balance
   guardrail — no Strength-stacking on an uncapped-meter finisher, ever.
4. Deck-size grammar (user ruling, this thread): In Kokomi's personal pool,
   Common cards may not increase deck size — they may only reduce it or
   replace themselves (net card delta ≤ 0). Uncommon and Rare may create
   cards (e.g. "2 energy: Exhaust 1, create 2"), priced so that a
   positive-sum engine requires Rare payoffs plus solved draw/energy
   velocity, and is not guaranteed to assemble in any given run. Scope:
   Kokomi's personal pool only (not mod-wide, not companion pools).
   → Lint: lint_kokomi_decksize.py — fail any Common in her pool whose
   effect list nets card-creation > card-consumption. Catch→lint culture:
   this law is machine-checkable, so it ships with a gate, not a convention.

The decision loop (analogue of Furina's "every point held is safety, every
point spent is tempo"):

> Every card kept is engine; every card burned is Charge.

Cycle the engine (discard/Sly/support velocity) or spend the deck down for
Exhaust payoffs. The deck is her second HP bar — defense literally spends
future draws.

## 2. Core systems

### 2.1 Charge (the Bake-Kurage meter)

- Accrual (proposed base rule): Whenever one of your cards is Exhausted,
  gain 1 Charge. Universal — includes Commander-consumed conscripts, the
  law-mandated Exhaust on every legal heal (Qiqi/Sigewinne become premium
  Charge events — the healing law is her enabler, not her obstacle),
  prevention-power procs, and even exhausted statuses/curses (accepted
  quirk: she is uniquely status-resistant; knob if it distorts).
- Alternative considered: tag-gated accrual ("Consumed" keyword only).
  Rejected in draft for rules-weight; revisit only if sim shows universal
  accrual makes non-priest decks accidentally elite on A2.
- Knob: CHARGE_PER_EXHAUST = 1. Premium cards may grant bonus Charge as
  explicit effect lines (KNOB_READS applies).
- Properties: uncapped; never expended; read (not consumed) by finisher
  effects; card-event-driven only — no per-turn passive accrual.
- Anti-stall argument (pre-registered for the inevitable challenge): Charge
  cannot be stalled into. Accrual events shrink the deck; fuel is finite per
  fight; the Exhaust economy is self-milling and imposes a natural fight
  clock. The genuine risk is not stall but multiplicative finisher reads
  (uncapped meter × repeated reads) — mitigated in §2.2 and by Flawless
  Strategy.

### 2.2 Finisher — two shapes, [USER]-gated choice

- Shape A — Nereid's Ascension as nuke: single large attack reading Charge.
  Rate limits mandatory: Rare, low copy count, Exhaust on the finisher
  itself, cost ≥ 2.
- Shape B — Ceremonial Garment as duration state (recommended): enter a
  transformed state for N turns; her attacks during it read Charge (scaled
  down per hit). Truer to the burst (a stance, not a hit), converts the
  one-shot balance cliff into repeated-but-bounded payoff, and hands the
  animation pipeline a showpiece. Interacts cleanly with Shape-A-style cards
  as the state's capstone if we want both.
- Either shape: finisher magnitude constants are knobs, [USER]-gated at
  first battery.

### 2.3 Commander — conscription

- Transform verb (working keyword: Conscript): transform a card in hand into
  a random Inazuma Companion card; it costs 1 less and gains Exhaust. Pays
  card identity; feeds Charge on consumption.
- Discard verb: discard-based generation and Sly triggers — pays tempo,
  synergizes with the Assist lane. Two distinct costs give the archetype
  internal texture (spark/demolition precedent).
- Differentiation from Furina (on record): Furina's companion grammar is
  additive and empowering (Guest Stars from outside the deck; Spotlight
  makes them the payoff). Kokomi's is transformative and consumptive
  (conscripts existing cards, burns them as fuel; the payoff routes through
  her own finisher). Kokomi does not get a Guest Star mechanic.

### 2.4 Damage-prevention power (the "healing" slot)

Sample (user, this thread): "If an attack would inflict damage, Exhaust a
random card from your draw pile" — prevention priced in future draws.

- Draft shape: Rare power, procs limited (first unblocked hit per turn),
  prevention magnitude a knob. Rationale: prevention + positive-sum engine
  is an invincibility loop; the deck-size grammar breaks the loop
  structurally at Common, and the rate limit + Rare gating breaks it at the
  power. Both guards ship; neither alone is trusted.
- Each proc is an Exhaust event → Charge. Getting attacked fuels the
  finisher. This is the stability identity as mechanic: her HP bar doesn't
  move; her deck does.

### 2.5 Starting relic (working name: Tamakushi Casket)

Carries the two conversion laws, no payoff magnitude (R16-compliant):

> Whenever you would gain Strength, gain that much Charge instead.
> Whenever one of your cards is Exhausted, gain 1 Charge.

Charge engine is thereby kit-guaranteed (Klee burst lesson). Name pending
lore/naming audit ([USER]-gated, as always).

## 3. Archetypes (bands declared at battery time, per A3 convention)

- Commander — conscription engine: transform/discard into companion fuel;
  Uncommon+ card creation lives here; the archetype that can attempt the
  (deliberately difficult) engine.
- Priest — Charge scaling and finisher payoff; wants Exhaust density, Rare
  heals as premium Charge, the prevention power.
- Assist — Sly/discard glue: draw and energy velocity, low internal payoff
  by design (Box Trick philosophy: honest glue no archetype warps around).
  Feeds both other lanes.

Elite-axis declaration (proposed, [USER]-gated): A2 Scaling + A4 Utility.
This forces the invariant question: is A1>A2 mod-wide or Klee-scoped? If
mod-wide, it needs a per-identity amendment before any Kokomi battery is
meaningful — she is a declared scaler and will breach by design. Ruling ask
§6.3.

Identity telemetry: her acceptance signature is HP-trajectory flatness, not
winrate margin — the HP-lost logging from Experiment 2 is her native
instrument. Propose: stability band (max HP-loss variance across battery)
declared alongside axis bands.

## 4. Inazuma companion pool v0.1 (candidates, not final)

Conventions: 4-star caps at Uncommon; heals below Rare convert to Block per
law (Charlotte precedent); star-5 Rares are the only true-heal slots.

Starter-reserved trio (per user ruling, matching Klee/Furina convention —
starter deck reserves slots for randomly drafted cards of):

- Gorou (4★, Geo, buffer/general) — def-adjacent buffs; the literal
  adjutant; Commander lane sings.
- Sayu (4★, Anemo, healer) — heal converts to Block/pre-emptive Block
  (Charlotte pattern).
- Kuki Shinobu (4★, Electro, healer) — heal converts to Block; her canonical
  self-HP cost is dropped per character law 1. Errata note in the pool sheet
  so it isn't "rediscovered."

Pool candidates: Thoma (shield/buffer — watch overlap with Kokomi's own
Block identity), Kujou Sara (attack buffer), Heizou, Yun Jin(?—Liyue, out),
Kazuha (Inazuma-born; strong Sly/discard flavor — "let the wind carry it"),
and 5★ Rares: Itto (now eligible per slot-4 ruling — taunt/bruiser
Uncommon-or-Rare, conscription's favorite meal), Ayaka, Ayato, Yoimiya, Yae
Miko.

Open disposition ([USER]-gated): Raiden Shogun. Options: reserve (future
playable / act antagonist), or admit as apex 5★ Rare. Lore cuts both ways
(Shogunate vs resistance; post-canon allies). No draft position taken.

## 5. Co-op posture

Healer/support party role, designed co-op-forward per A2 — but the solo gate
is hard: she clears the battery solo at declared identity before any co-op
tuning is credited. In solo, party-wide effects read self+companions. Co-op
validation follows the Klee A4 pattern (fixed-partner sim) once solo gate is
green.

## 6. Ruling asks ([USER] closes; enumerate in DECISIONS.md on close)

1. Healing-amendment output = no amendment. Ratify that this thread
   discharges the A1 note with the law unchanged.
2. Deck-size grammar as written in §1.4, Kokomi-pool scope, plus the lint.
   (User-authored this thread; ask is formal ratification + scope.)
3. A1>A2 invariant scoping — mod-wide with per-identity amendment, or
   Klee-scoped? Blocks battery interpretation.
4. Elite axes A2+A4, and the stability-band addition to her scorecard.
5. Charge accrual rule — universal exhaust→Charge (recommended) vs
   tag-gated.
6. Finisher shape — nuke vs Ceremonial Garment state (recommended) vs
   both-with-capstone.
7. SUPPORT_CARRY attribution — Kokomi-conscripted companions count as
   self-sourced; drafted Inazuma pool cards count normally.
8. Statline constants — proposed: hp 70 (highest of the three; lore: her HP
   pool, and stability wants headroom), energy 3, starter deck composition
   incl. reserved companion slots. All numbers knobs.
9. Raiden disposition (§4).
10. Naming/lore audit — card-name candidates herein are placeholders; audit
    is irreplaceable and [USER]-only. Reserved-names lint runs on the full
    sheet before any C-milestone.

## 7. Sim / instrumentation asks (handoff to Code workstream)

- New tier0 ops: transform_to_companion, charge_gain, charge-reading damage
  formula, prevent_damage_exhaust, create_cards, Sly/discard triggers,
  duration-state (if Shape B).
- New detector, report-only at first: engine_closure — flags any turn cycle
  where cards created ≥ cards consumed with energy/draw closure (the
  infinite-engine detector). Diagnostics, never acceptance targets (R14).
- SUPPORT_CARRY attribution patch per ask §6.7.
- HP-trajectory telemetry first-class in her batteries (Experiment 2 logging
  is a dependency, not an option).
- Shared-loader schema changes (new ops) require the cross-session note
  before landing, per standing rule.

## 8. Non-goals (this kickoff)

- Art, animation, VFX (separate sprint; Ceremonial Garment noted as a future
  showpiece only).
- Act 2/3 batteries, composite weights (A3 constants stay [USER]-gated at
  freeze).
- Co-op tuning before the solo gate is green.
- Zhongli design (slot-4 deep dive is its own thread; only the slot ruling
  lands here).
- Any healing-law rewording.

## 9. Definition of done

Ruling asks 1–10 closed by [USER]; constants recorded in DECISIONS.md;
companion pool v0.1 ratified with errata notes; sim asks acknowledged by the
Code workstream; then and only then does the card-sheet pass begin.
