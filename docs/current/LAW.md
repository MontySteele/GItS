# LAW

The normative constraints that govern future work — design, behavior,
engineering, art. Rules only; a line earns its place only if it constrains what
future work may do. Status and shipped facts live in `STATE.md`; open decisions
in `QUEUE.md`; measurement *method* in `EXPERIMENTS.md`; the working *norms*
(hygiene vs. [USER] calls, audit triage, closed-items-leave-HEAD, worktrees) in
`CLAUDE.md` and are not restated here.

Provenance strings (`R44`, `principles §2.2`, `kokomi Law 2`, …) are plain
pointers into the tagged history — uncounted, unlinted. **Current numbers and
shipped behavior are not law here; they live in the YAML sheets and the code,
which are their own source of truth.**

---

## Pillars (conflicts resolve upward)

1. **Spire first.** This is a good StS2 mod that happens to be Genshin, not a
   Genshin fangame in StS2 clothes. StS2 conventions (energy, rarity, intents,
   keyword style) win over Genshin fidelity when they conflict.
2. **Reactions are earned, not given** (Combat, below).
3. **Character identity is not pinned here** (moved out 2026-09-01) — it lives
   in the character's brief, or `docs/current/characters/*-identity-record.md`.
4. **Co-op is amplified, never required** — every character clears solo.

When two rules below conflict, the higher pillar wins.

**Deliberately not adopted (durable exclusions — do not add these):** elemental
resistance matrices; crit rate/damage as stats; Energy Recharge / Elemental
Mastery as numeric stats (their *roles* are absorbed by relics and card design);
stamina; cooldowns; any open-world system. Genshin's stat sheet stays home; its
combat grammar comes with us. (principles §1)

---

## Combat — elements & reactions

- **Reactions are earned, not given.** No character card applies an off-element
  aura; off-element access comes only from companions or a co-op partner.
  (principles Pillar 2 / Guardrail 2)
- **Amplifiers are per-hit and consume the aura.** No reaction ever produces a
  persistent or compounding damage multiplier — this is the iron rule and the
  balance governor. (Whether a particular card's scaling that happens to get
  duplicated is *too strong* is a balance question, not a law.) (principles §2.2)
- **One aura per enemy (v1), 2 player-turns, refreshed by same-element hit.**
  Anemo/Geo leave no aura — they only trigger. (principles §2.1)
- **Canonical Frozen is a per-turn-decrementing, per-creature duration counter.**
  Non-boss Frozen = −50% next-action damage + Shatter (first Attack hit only,
  direct HP damage, cannot shatter the freeze it just applied). In boss rooms
  only creatures carrying `MinionPower` are Frozen; every other creature takes
  the Vulnerable substitution. (principles §2.2; R44; R116 NC-7 / R117 Q13)
- **Elemental application coexists with Artifact.** An Aura or a Bomb lands
  beside Artifact rather than consuming a charge — only an actual debuff
  reduces Artifact. Scope: Auras and Bombs coexist; Frozen and
  reaction-applied Vulnerable/Weak/Poison stay real debuffs and are negated
  as normal. Bomb's "first attack −25%" rider lands through Artifact under
  the same rule — ruled acceptable. ([USER] 2026-08-23)
- **Hard CC is payoff-tier only.** No reaction and no companion card produces an
  intent-skip/stun at repeatable-common economics; full stun is priced at or
  above base-game stun scarcity with per-combat diminishing returns. Companions
  never source hard CC (the `control_uptime` / `SUPPORT_CARRY` detector enforces
  it). (principles §2.2a, §4.3; R45)
- **Reaction credit — damage attribution and Burst energy — goes to the
  triggering player;** auras live on shared enemies so cross-player reactions
  need no special-casing. (principles §2.5)
- **Overload splash (to all enemies) and Electro-Charged (stacking DoT) bypass
  Block and are damage-pipeline-free** (no strength/vulnerable recursion).
  **Shatter** is separate: bonus damage on the first Attack hit against a Frozen
  enemy, which removes Frozen — it is not a DoT. (M1; principles §2.2)
- **Application cadence is a per-character dial** — catalyst-grade (every attack
  applies, low base numbers) vs. skill-grade (only Skill/Burst-tagged cards
  apply, higher base numbers). (principles §2.3)
- **Spotlight/empowerment boosts numbers only, never turn-economy effects.**
  (principles §2.2a, v1.10)

## Economy — companion pool, shop, banner, artifacts

- **The companion pool is the mod's sole colorless content;** the mod ships no
  base StS2 colorless cards. *Live tension:* principles §4.7 states the base
  pool is removed, but ship reality is a shop-only override (R60 phase 1); full
  removal needs a seven-consumer audit and is deferred, not rejected — treat the
  pool as sole-colorless in design, but do not assume the base pool is gone in
  code. **R60 phase 2 is graded ACCEPTABLE for v1 and is not scheduled** — the
  remaining in-combat colorless fantasy leak stands as a known, priced v1
  condition rather than an open defect. (principles §4.7; R60; R149)
- **Companion cards route power through your character, never around them**
  (Applier / Buffer / Trigger). **The delete-test always holds, unmodified, no
  detector carve-outs:** removing your character's own cards from a winning deck
  must gut it — if companions win anyway, that is `SUPPORT_CARRY`, a real failure
  even for a support character. A **High-appetite** archetype (§4.4 — a
  hypothetical swirl-fisher) may make companion-fishing the *dominant* plan; a
  **companion-synergy** mechanic like Furina's Spotlight / Guest Cast may route a
  character's damage through *empowered* companions. In both cases it is the
  character's own enabling cards that the delete-test deletes, and deleting them
  must still gut the deck. (Furina is Standard-appetite, not the High-appetite
  case.) (principles §4.3, §4.4; furina §8)
- **Rarity grades:** 4-star companions ≤ uncommon power; 5-star companions are
  Rares, **exactly one card per 5-star**, payoff-grade only as *support* (buff /
  amplify / aura) — never an independent or self-scaling damage engine.
  Availability is a **runtime** governor, not an authoring cap: the designed
  5-star roster per nation may grow without limit, and the Featured Banner (3
  per nation per run) is what gates it.
- **Personal-pool companions are the character's kit, and may carry.** A
  character's own signature companions (e.g. Klee's Prune) are **drafted
  normally** — rewards, shop, a possible randomized starter — and kept to the
  **rarity guardrails** (power tracks rarity), but are **exempt from the
  enabler-not-carry power limit**: a personal-pool card may be deliberately
  **load-bearing / deck-warping**, not only a flavorful assist. Because they *are*
  the character's own cards, the **delete-test still governs them** (deleting them
  must gut the deck). This is distinct from **generated Guest Star cameos**, which
  are minted mid-combat and are neither draftable nor banner-governed
  (equal-rarity, this-combat-only, Exhausting — see the Furina Guest Star
  guardrails). **Amendment (R160):** a personal-pool companion may also enter by
  an **optional, visible run-start offer** — the randomized-starter family, not
  new Neow machinery. The offer is **declinable**: taking it is a choice the
  player makes, on the same footing as choosing a different Ancient door, so it
  does not make the card mandatory kit. (principles §4.2, §4.3, §4.5; furina §9;
  R160)
- **Free reward channel is enabler-grade and stochastic,** nation-weighted ~50%
  same-nation; its value is capability (off-element access), not per-energy
  stats — a whiff is never a dead pick. (principles §4.1, §4.7)
- **Shop is the paid premium channel, two colorless slots, both Uncommon-or-higher:**
  slot 1 = home-region, slot 2 = wildcard nation. Both roll
  `SHOP_COMPANION_RARITY_ODDS` (reward odds renormalized over the ≥Uncommon pool);
  the **nation filter is the only difference between the slots**. Slot 2's floor was
  removed by R116/NC-10 and **restored 2026-08-10** — the paid channel does not sell
  Commons. (principles §4.7; R59; R116 NC-10; R117/R118 Q16; [USER] 2026-08-10)
- **An empty companion slot is omitted, never faked, in both engines.** When the
  fallback ladder runs out (no drawable companion at any nation or band) the slot is
  not created; the mod does not substitute a base colorless card. Omission happens
  upstream of `MerchantCardEntry.Populate`, which has no no-card path.
  ([USER] 2026-08-10; R59, R60)
- **Gold price is the balance governor, never a stat nerf.** Companion pricing is
  50/75/150 by rarity; the ×1.15 colorless surcharge applies to `ColorlessCardPool`
  only, so companions are exempt. (principles §4.7; R61, R63)
- **Price, shelf composition, and shelf order JOINTLY govern the premium channel.**
  Price alone is not the governor: what is on the shelf (the rarity floor) and when
  the player is asked (companions resolve before the relic shelf, so they get first
  claim on the purse) move the same outcome, and a channel tuned on price alone is
  tuned on one of three levers. Amends the older "pricing is the governor" thesis,
  which stands as the pricing half of it. ([USER] 2026-08-10, S4-G10)
- **Neutral action-energy / draw / thin are legal enabler-grade companion utility**
  (one-shot, Exhaust-gated, costed) — the pool must let any character draft a
  kit-gap fix. **Burst-meter (`burst_energy`) generation stays character-kit-scoped**
  and must never be cheaply repeatable from companions. (principles §4.7, §2.4)
- **The Featured Banner governs 5-star availability:** each run rolls
  min(roster, slots) limited 5-stars per nation, without replacement, fixed for
  the run, per-player in co-op; 4-stars never gated; reward slot, shop slot 1,
  and sim are wired together. Standard-banner 5-stars carry `standard: true` so
  an off-banner floor is one flag, not a redesign. (principles §4.2, v1.8; R64)
- **An unreleased-nation character sits in their nation of operation until their
  home sheet ships** (Arlecchino→Fontaine, Childe→Liyue). (R65)
- **Artifacts are relic subcategories with 2-piece set bonuses** — no 4-piece
  sets, no main/substat rolls; themed to reaction styles, not characters
  (cross-character content). (principles §5)
- **Infinite cycling engines gate to Uncommon+** (a hand- and energy-neutral
  self-replacing card is a cycling engine whatever else it does). (R109 X2; R114
  FLAG-1)

## Character identity — moved out of LAW (2026-09-01)

Per-character identity statements left LAW under the machinery review's change
6. They are not law any more: they are revised by a sentence in the character's
brief, with no amendment ceremony.

- **Klee** → `review/active/klee-brief-2026-09-01.md` §18 (the brief is the
  live artefact; its §3 is the live rule list).
- **Furina** → `docs/current/characters/furina-identity-record.md`.
- **Kokomi** → `docs/current/characters/kokomi-identity-record.md`.
- **Roster-wide statline lines** → `docs/current/characters/roster-identity-record.md`.

## Roster

- **Playability and a companion card are compatible** — the exclusivity clause is
  struck. Itto is a COMPANION CARD (no roster slot); Zhongli holds slot 4
  (countersigned, unscheduled); Kokomi slot 3. (R118 §2 10.8; R108)
- **Every playable character ships to the §3 template:** element + cadence +
  7-axis statline declared before card design; exactly one Ghostflames-scale
  signature subsystem; three archetypes (default / draft-gated ceiling /
  velocity) separated by card-slot competition; ~75-card pool; talent-relic +
  kit-Burst + character relics/potions. (principles §3)
- **Every character clears solo; co-op is amplified, never required.**
  (principles Pillar 4). The statline half of this bullet moved out of LAW
  2026-09-01 → `docs/current/characters/roster-identity-record.md`.
- **Co-op mechanics arrive as multiplayer-only CARDS, never as modifications to a
  character's base kit.** A character's basic functionality is identical solo and
  in co-op; co-op depth is added by a few multiplayer-only cards — the route
  StS2's own beta branch took. (R144)
- **All art and audio is original or commissioned "in the StS style"** — no
  extracted HoYoverse assets ship publicly (placeholder art in private builds is
  fine). Naming: constellations for rares/upgrades, talent names for relics,
  voice lines for flavor. (principles §9, §3)

## Content authoring — card-sheet rules

- **True in-combat healing is Rare-tier AND Exhausts (conjunctive R8 law);**
  below Rare, sustain routes through Block or buffer pools; no 4-star companion
  true-heals (potions and relic-scale trickles exempt). A rider otherwise banned
  is legal only conjunctively — dropping one half is not a "simplification."
  (principles Guardrail 6; R8; R79/B4)
- **No card starts the game with AoE;** AoE must be drafted, never in any
  starter. (R56)
- **Ancient carve-out (R127, 2026-08-07):** an Ancient-rarity card — Dusty
  Tome's single acquisition door, one visible Ancient per roster character —
  may grant per-turn accrual that its owner's resource laws otherwise ban
  (Kokomi's no-passive-accrual Charge; Furina's no-per-turn-Encore trickle).
  A bounded, opt-in, once-per-run power spike is the rarity's design: the one
  door out of the character's central bargain. Scoped to Ancient rarity
  exactly — no other rarity, no relic, and no event may inherit the
  exception. (EB-30q)
- **Strict-domination is scoped to adjacent rarities:** a card must not be a
  strictly-better superset of another at similar weight; two-step gaps are
  informational. Self-damage/discard/spend_encore count as costs; prefer base-StS
  "twist" shapes over pure supersets. (R26/R77)
- **Threshold predicates pay a flat printed bonus once, not proportional reads;**
  charge/meter bars are Uncommon+; thresholds encode base-plus-bonus so the
  always-live half moves on upgrade and the bar cannot drift down (lowering a
  threshold is forbidden). (R58, invoking R1)
- **A meter-reading damage card is tagged `scaling`, and also `frontload` only if
  it deals damage at meter zero.** `sustain` = healing/prevention of your own HP
  only; zero sustain is a legal identity and `sustain` is never linted. (R91 2c,
  2d)
- **≤2 new keywords per character beyond the shared element system;**
  support-protagonists may carry one extra via logged amendment with compensating
  cuts. Muster's definition attaches from the card's OP. (principles Guardrail 5;
  furina §6; R78)
- **Every card carries a per-character `register` field** (shared schema column,
  per-character vocabulary; Focalors register caps at two Rares). **The register
  guides art selection only** — nothing under `tier0/engine` or `tier05` may read
  it, codegen ignores it, and moving a card between registers must never move win
  rate. (R85; R86)
- **Upgraded starters get a distinct name, not a "+" suffix;** display names live
  in the unique-names namespace, reserved names annotated with the owning kind. A
  full-sheet reserved-names lint runs before any C-milestone; the naming/lore
  audit is [USER]-only and eyes-on. (R69; R29d)
- **Distinctness gate (red test):** uniq ≥ 70, maxclu ≤ 5, neardup ≤ 0.40/card;
  `top%`/`vocab` carry no permanent gate; a partial-pool anchor can only loosen a
  threshold, never certify it. (R81)
- **Enchantment support is a minimal per-card rider;** the run-wide enchantment
  subsystem stays outside the parity world. Encore Performance is 0-cost with no
  energy-positive loop; copies inherit printed bounds; kit cards are not legal
  copy targets. `replay_next_companion` / cost-delta accumulators are
  writing-turn-scoped. (R82; R110 X3/X11; R114 FLAG-1/2; R118 Q9)
- **Ancient-tier pool gaps are fixed with real content, never option removal;**
  each character needs one Ancient card, gated by a deploy lint that fails on an
  empty ledger. (klee-mod Ancient ruling)
- **A material card-sheet edit is a world change and lands under a
  `CONSTANTS_VERSION` bump.** *"A card-sheet edit that materially changes the
  drafted or combat world — card additions or removals, cost changes,
  effect-number changes, rarity moves — is a world change. It lands under a
  `CONSTANTS_VERSION` bump like any other balance constant, and numbers are not
  comparable across it."* The sheets sit outside the `RT/D/P/C` stamp, so
  without this rule two worlds differing in whether a card exists at all are
  indistinguishable to a reader of the stamp. **Rename amendment:** a
  *cosmetic* rename is exempt from the bump **only when neither the card id nor
  the display name is read mechanically** — and the burden is on the renamer to
  establish that, because at least one relic reads both. `card_name_damage_bonus`
  matches a **substring** against the card id **OR** the display name
  (`tier0/engine/relics.py:385-398`); its one carrier is `strike_dummy`,
  substring `"strike"`, `+3` to attacks only, FROZEN. A rename that adds or
  removes such a substring on either field moves damage and is not cosmetic.
  (R179; M15 draft text ratified as written, amended on the rename clause)
  **Role/archetype amendment (RATIFIED 2026-08-24, R202):** a change to a card's
  `role` or `archetypes` is a material card-sheet edit because both fields are
  mechanically read by drafting. It requires a `CONSTANTS_VERSION` bump, and
  drafted-world numbers are not comparable across it.

## Design governance & measurement authority

- **The simulator's authority is relative deltas and structural findings, not
  absolute human-play winrates;** a ratification resting on an absolute winrate
  rests on the wrong number. (principles §7)
- **Seven-axis numbers are reportable, not load-bearing:** **all seven** axes are
  permanently CLOSED as reportable-only (never a gate, target, or justification
  to move a value). There is **no "Fanfare axis"** — R118's term names no axis;
  Fanfare is a Furina mechanic that falls under **scaling**, and the per-axis
  disposition therefore collapses to one disposition for all seven. (principles
  §7; D3; R90 Q7; R118; R138)
- **Every archetype passes aura-starvation / bricking checks in the sim before
  implementation;** test packages model plausible drafts, never monocultures.
  (principles Guardrail 4)
- **Ratified 1000-fight winrate bands change only by ruling, with archives;**
  small-n heuristic locks may be retuned to measured-noise reality only with a
  dated comment and disclosure. Authored Tier-0 25-card batteries are
  ceiling-saturated and keep only their matchup floors; Tier 0.5 owns the
  upper-power comparison. (R62; R47)
- **No number measured on a prototype row is quotable** — not in a packet, not
  in a register, not in a commit message. The quarantined prototype surface
  exists to be played, not to be measured against the shipped world: its rows
  reach no pool, no digest, no balance report and no stamp, so a figure taken
  off one has no comparable. The single exception is the decision-closeness
  falsifier (R213 F), which reads the TURN rather than the row. (R213 B; R215)
- Measurement *method* (stamp law, one-variable windows, versioning,
  pre-registration + blind grading, instrument visibility) is in `EXPERIMENTS.md`.

### Design charter (R217) - now a checklist

- **The nine rules D1 to D9 left LAW on 2026-09-01** (machinery review,
  change 6) and are the checklist a brief, a package and a sheet are read
  against: `docs/current/kit-checklist.md`. They are qualitative by
  construction, they are a review instrument rather than a gate rows pass,
  and they are provisional through the Klee slice.
- **Nothing in that checklist is a numeric band and nothing in it gates:**
  hook share, bridge %, payoff-role %, scalar-payoff %, random-target %,
  Powers-per-universal-verb count, plain-card %, word count and "turns with
  a named alternative" rate are descriptive only. No subjective
  front-matter fields enter card YAML, and there is no waiver mechanism.
  **Decision closeness (R213 F) remains the only numeric design falsifier,
  and it falsifies one way.** (R217, drafted by GPT, sharpened by Claude,
  ratified by [USER].)

## Engineering invariants

- **Every C# numeric balance constant is classified — mirrored or explicitly
  unmirrored.** A mirrored constant is LAW from tier0, parity-linted, and a
  divergence is fixed in both engines; an unclassified `public const int` is a
  lint finding, not a skip. (`lint_constant_parity` / `lint_op_parity`, total by
  construction; R63 is the economy-is-LAW mirror specifically.)
- **Any shared-loader / shared-schema change** (a field read by both `loader.py`
  and codegen, or by both engines) is called out in the PR/commit and updates
  **every** consumer atomically in the same change — never land one side and
  leave the other to a follow-up. (R20; R92)
- **Version stamps and game version are read live at call time** from the
  canonical source (`constants.py`, `release_info.json`), never stored or read
  from a comment/exe. **manifest.json version is MAJOR.AUTO:** MAJOR (`0.2`,
  exactly two dotted integers) bumped only by [USER] at release, AUTO is the
  commit count emitted as the PATCH component (`0.2.1159`); deploy refuses to
  overwrite a versioned zip; dirty builds append `+dirty` as semver build
  metadata (`0.2.1159+dirty`), which the game's comparator ignores. A **dev
  package built off the quarantined prototype surface is marked on the same
  build-metadata channel**: `0.2.NNNN+proto`, or `0.2.NNNN+proto.dirty` when
  the tree is dirty, so "which build is installed" has an answer on screen when
  both paths write the same `mods\klee` directory. **The gate is symmetric:**
  the release path refuses a `+proto` package by name, and the dev path refuses
  a package that lost its mark. The string must parse as a semantic version:
  the game's parser throws on a `-` before patch, leaves an unparseable version
  `null`, and then refuses any dependent mod declaring a `min_version` on us.
  (R68; R70; R214; R217 D)
- **State-reading damage/spark riders snapshot state at cast;** because "when
  state is read" is invisible to the sim, the timing is pinned by a C#-side
  source-text check. Rules read the resource, never the badge (display may lag
  only within one card play). (R72; R39)
- **Every meter carries a bounded/unbounded property whose cap is read from
  `constants.py`** (bounded: salon_member 3, fanfare; unbounded: encore,
  charge, burst, exhaust_pile, spark). (R91 2b; `spark` moved to unbounded by
  R220 F — R219 C's re-author prices Sparks as an alternative card cost with
  **no cap**, the governor being generator scarcity, so the bounded-at-3 entry
  was a dead reference the moment `M51` was countersigned)
- **A structurally-invisible defect gets a machine-readable allowlist/manifest +
  a lint or boot check** (house pattern; the allowlist checks itself for rot):
  empty starting relics, pool rarity coverage, Ancient coverage, required-node
  contracts. (klee-mod findings 21/24/27)
- **Sweep BaseLib and the decompiled game for an existing solution before
  building infrastructure;** derive from `CustomCharacterModel`/BaseLib
  abstractions, never raw game types. Downfall is reference-reading only —
  patterns may be mirrored; scene files, art, and code are never copied verbatim.
  (klee-mod standing rule; license note)
- **Build output never lives under the game's `mods/` tree** (ModManager parses
  every `*.json` as a manifest). **Custom models declare loc via the
  `ILocalizationProvider.Localization` override**, never a hand-rolled dict; an id
  is an API — any `Id.Entry` change is followed by a consumer sweep (loc keys,
  asset paths, saves, epoch strings). (klee-mod findings 7/15/23)

## Art & visual layer

- **Ship pre-sized art, no runtime minification** — except where the layout pitch
  is a per-player stat, where bounded runtime fitting is allowed with the bound
  written down and asserted (Salon members capped at 0.5). (principles v1.13
  RATIFIED)
- **Visuals bind to funnels, never to values (Funnel Contract):** a number a kit
  redesign moves must not be able to break a display. Contracted binding points:
  Salon = 3 slot-index-keyed slots (duplicates legal); Encore-absorbs-before-HP;
  Spotlight-is-a-designation-event. A breach = stop-work on that track, flagged
  in the PR/commit; visuals never chase an unlanded kit change. (animation-sprint-2)
- **The centered-overhead creature-space slot is the cross-character Burst
  indicator;** gauge skins are unique per character. A mirror belongs above the
  animated node, never on it; **never write `Visuals.Scale`** (a sign flip inverts
  the hitbox — a gameplay bug in visual-bug clothing). A node a bridge depends on
  is a contract with a side-effect-free boot check. (animation-sprint-2 C4;
  klee-mod placement rules)
- **Art dedupe (`art_lint` L1):** effective pick = auto or shortlist rank 1 unless
  red-pen resolves; register-crossing reuse is legal; known collisions sit in a
  `PENDING_RED_PEN` allowlist until resolved, then the entry is deleted so the
  lint guards the resolution. **No Spine** — the animation-path spike ran, the
  licence question was reopened and **answered: no purchase.** Rigs are
  **Godot-native**, and how far native gets us is the thing being found out.
  (klee-mod art addendum; animation-sprint-2; R141)
- **Crop reuse is judged by eye, per card — there is no numeric crop-reuse cap.**
  **Environment art counts as a card face** when the location is central to the
  card and the composition is distinct (a random hallway still does not).
  **Exactly one** hand-cropped `Character Details` Rare is allowed, and it rides
  an approved-exception entry in `art_lint` rather than an edit around the ban.
  (R151)

## Process constraints that bind design

- **The delegation ladder — seven standing authorizations.** Claude decides
  these and ships them; none of them waits on [USER].
  1. **Art picks.** Apply shortlist rank 1 and ship it. The contact sheet is
     committed with the change, and `art_lint` L6/L9/L11/L12 still bite.
     [USER] vetoes on the sheet, with no deadline; a veto is a one-line revert.
  2. **Prediction slates.** Claude DRAFTS the slate from written design intent
     and commits it as its own commit, labelled DRAFTED, BEFORE any seed run;
     [USER] countersigns in batch, or vetoes within five days. Blind grading is
     unchanged. Pre-registration holds on commit-before-run, not on authorship.
  3. **Countersign once — restamp-and-hold is abolished.** The packet's own
     world-check refuses to run on a moved world, and a moved world means
     re-drafting the affected slots and disclosing the diff in the row. Never
     re-sign.
  4. **One batch per sitting** (amends R206), assembled by Claude. *"Does the
     original band stand?"* defaults to **STANDS** unless the estimand itself
     moved, and nothing already answered gets a transient register row.
  5. **Window sharing** (R207) is Claude's call whenever the scratch read is
     null — no interval separation on any arm — disclosed as the scratch hash
     plus the null read, in the row and in the PR text.
  6. **Hygiene inside a registered packet** never needs authorization (stale
     sentences, filenames, rarity typos, dead paths) — except inside a
     countersigned prediction block, where R101b holds: strike, don't rewrite.
  7. **Derived numbers land unratified** when the number is derived rather than
     picked, the error direction is stated and one-way, the archive scope is
     disclosed, and the value lives in exactly one constant. Names ship
     provisional, flagged in the loc file, and must be proved cosmetic at ship
     time by lint (R179), or the later rename is not free. Excluded: R58
     one-way doors, and shipped player-facing numbers.

  **Form rule:** anything that still returns to [USER] is presented as a
  **NUMBERED PICK LIST**, never a blank to fill.

  **Still [USER]'s:** eyes-on judgments no test can take (the docket read,
  in-game looks, the naming/lore audit); merging a staged balance lever; money;
  one-way doors (R58 thresholds, major version bumps); amendments to LAW or to
  measurement law; and a pick between genuinely different design directions.
  (R212; amends class-p-charter §2 and kokomi §0)
- **A WATCH ITEM is a blessing of the mechanism + a named quantity + a named
  trigger;** it does not return until the trigger fires, and then it returns with
  a reading, not an argument. (R111)
- **An active decision packet is self-contained** — it carries the context it
  needs; reference-by-incorporation to unregistered or deleted documents is a
  known anti-pattern. (klee-mod Neap Tide addendum)
