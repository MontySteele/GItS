# Teyvat Spire — Mod Design Principles (v1)

> **Lifecycle: LIVING** — expected to change; read it to work on the project. Status index: `docs/registry/identifiers.md` §15.

**Project:** Genshin Impact character mod for Slay the Spire 2 (working title: "Teyvat Spire")
**Status:** Master design doc. Governs all character/card/system design. Changes here ripple everywhere — amend deliberately, log amendments at the bottom.
**Companion docs:** `tier0-simulator-spec.md` (testing harness), Klee character doc (forthcoming).

---

## 0. Handoff commentary

For any Claude instance (or human) picking this up: this doc records *decisions*, not options. Where a decision was contested, the losing alternative and the reason it lost are in a `Rejected:` note so we don't relitigate by accident. The design has three load-bearing ideas — the aura/reaction system (§2), the companion pool (§4), and the enabler-not-carry principle (§4.3). If a proposed card or system violates one of these, the proposal is wrong, not the principle. Everything else is negotiable.

Engineering context: StS2 = Godot 4.5 + C#, modded via BaseLib; our structural reference is the Downfall port (per-character module layout). The one large custom system is §2; est. scope comparable to Downfall's Ghostflames subsystem. All numeric values in this doc are design intent — live numbers get validated in the Tier 0 simulator first, then in-game.

---

## 1. Vision & design pillars

**One line:** Genshin's team-building brain in Slay the Spire's body.

**Pillars, in priority order (conflicts resolve upward):**
1. **Spire first.** This must be a good StS2 character mod that happens to be Genshin, not a Genshin fangame in StS2 clothes. StS2 mechanical conventions (energy, rarity, intents, keyword style) win over Genshin fidelity when they conflict.
2. **Reactions are earned, not given.** A mono-element character cannot react alone. Off-element access is scarce and drafted (companions) or brought by a co-op partner. The hunger for that second element IS the game.
3. **Character identity = statline asymmetry.** Every character scores 4–5 on exactly two of the seven evaluation axes and ≤2 on at least one (see Tier 0 spec §2). The weakness is load-bearing.
4. **Co-op is amplified, never required.** Every character must clear solo. Co-op makes reactions easier and team comps meaningful; it never gates content.

**Not adopting (deliberate):** elemental resistance matrices, crit rate/damage as stats, Energy Recharge / Elemental Mastery as numeric stats (their *roles* are absorbed by relics and card design), stamina, cooldowns, and any open-world system. Genshin's stat sheet stays home; its combat grammar comes with us.

---

## 2. The element & reaction system (core engineering)

### 2.1 Auras
- Elements v1: **Pyro, Hydro, Electro, Cryo, Anemo, Geo.** Dendro deferred to v2 — its Bloom chains are Genshin's most combinatorial subsystem and v1 needs a stable base. (Charmingly, this matches Genshin's own release history.)
- An **aura** is an enemy-side status: one aura per enemy (v1), duration 2 player-turns, refreshed by same-element application.
- Cards apply elements via an `Applies: <Element>` line on damage, or `Apply <Element>` as a pure effect. Anemo and Geo don't leave auras (as in Genshin); they only trigger.

### 2.2 Reactions
Damage tagged element E hitting an enemy holding aura A ≠ E consumes A and triggers:

| Pair | Reaction | Effect (intent; Tier 0 validates) |
|---|---|---|
| Pyro×Hydro | Vaporize | That hit ×1.5 |
| Pyro×Cryo | Melt | That hit ×1.75 |
| Pyro×Electro | Overload | +damage splash to ALL enemies |
| Electro×Cryo | Superconduct | Apply Vulnerable |
| Hydro×Electro | Electro-Charged | Apply stacking DoT |
| Hydro×Cryo | Frozen | Enemy's next action −50% damage; while Frozen, first attack that hits it **Shatters**: bonus damage, removes Frozen. Bosses: Vulnerable 2 instead. **No skip/stun at base** — see §2.2a |
| Anemo trigger | Swirl | Copy target's aura to all enemies |
| Geo trigger | Crystallize | Gain Block |

**§2.2a — Hard-CC pricing rule (v1.5).** Base StS2 deliberately makes reliable stun scarce (an act-3 Ancient reward at 3 energy + Exhaust; looping it is a known degenerate win). No reaction, and no companion card, may produce an intent-skip at repeatable-common economics. Frozen's base effect is soft control (above); **full stun is payoff-tier design space only** (rare character cards, artifact sets, 5-star kits), priced at or above the base game's stun scarcity, with per-combat diminishing returns (an enemy that thaws gains Freeze Resist). Detector: `control_uptime` — % of enemy actions negated by companion-sourced effects; winning fights above threshold flag SUPPORT_CARRY.

**§2.2a extension (v1.10):** Spotlight empowerment applies to numbers only — **never turn-economy effects**. Character-level designation touches a companion's entire kit; if any companion ever ships a soft-control card, Spotlight must not be the thing that upgrades it into stun economics. *(Engine note: enforced structurally for damage and Block; element-application counts are covered by the law and will join the plumbing when a card first prints a numeric count — documented gap in `spotlight_mult`.)*

**Iron rule: amplifiers are per-hit and consume the aura.** No persistent damage multipliers from reactions, ever. This is the balance governor; it's also faithful. `Rejected:` reaction-stacks-as-buff designs — they turn ×1.5 into a compounding engine and every deck becomes Vaporize goodstuff.

### 2.3 Application cadence (the "ICD dial")
Per-character setting for how often attacks carry their element:
- **Catalyst-grade** (Klee): every attack applies. Maximum reaction fuel, so these characters get lower base numbers.
- **Skill-grade** (most weapon users): only cards tagged *Skill*/*Burst* apply. Higher base numbers, reactions are punctuation, not rhythm.
This dial is our main cross-character balance lever for reaction frequency.

### 2.4 Burst Energy
- Per-character meter, per-combat, starts at 0. Gained by: playing Skill-tagged cards (+N) and triggering reactions (+N; the "particle economy").
- Each character's **Burst** is a signature rare card that is **kit, not loot** (v1.9): it does not occupy the draftable pool or the starting deck. When the meter first fills in a combat, the Burst is granted to hand; playing it empties the meter, and it re-arrives if the meter refills. This is Genshin-faithful (your burst is your kit, charged by play) and solves the discovered acquisition problem: as a 1-of-15 rare, only ~10% of runs ever saw their own signature ability. **Burst cards have Retain** — they stay in hand at end of turn. (v1.4 ruling: without Retain, StS's discard rhythm cycles the Burst away before the meter fills — sim-verified. Retain is also faithful: a charged burst doesn't evaporate.)
- Relic space may carry partial energy between fights (Favonius-flavored). Meter size is a per-character balance knob; Klee's playtest-tuned 40-grade meter is deliberately quicker than a nuke Burst.

### 2.5 Co-op rules
- Auras live on shared enemies → cross-player reactions work with zero special-casing.
- Reaction credit (damage attribution + Burst Energy) goes to the **triggering** player.
- Expected emergent meta: Anemo/Geo and applier-heavy characters rise in co-op value; that's desirable, not a bug.

---

## 3. Character design template
Every playable character ships with:
1. **Element + cadence grade** (§2.3) and a 7-axis target statline declared *before* card design.
2. **Signature mechanic** — one Ghostflames-scale subsystem (Klee: Bombs+Sparks). One. `Rejected:` two novel subsystems per character; Downfall's data says the subsystem is 70% of the engineering.
3. **Three archetypes**, tagged per the enabler/payoff/glue schema (Tier 0 spec §4.1): a default plan, a draft-gated high-ceiling plan, and a velocity/tempo plan. Archetypes separate by card-slot competition.
4. **~75-card pool** (v1 floor): 4–5 basics, ~30 commons, ~25 uncommons, ~15 rares. Each archetype: 15–20 tagged cards, commons-heavy on enablers, rares as payoffs.
5. **Talent-relic** (starting relic = a Genshin passive talent), **Burst card**, ~8–10 character relics, 2–3 character potions.
6. **Naming sources:** constellations for rares/upgrades, talent names for relics, voice lines for flavor text. The material writes itself; use it.

## 4. The Companion Pool ("4-stars as cards")

### 4.1 Structure & acquisition
- A shared, colorless-style pool (`CustomCardPoolModel.IsColorless` — first-class in the StS2 API). Each companion card = one 4-star character's iconic action ("Xingqiu — Raincutter", "Fischl — Oz, at your side").
- **Acquisition:** every card reward gains a 4th, visually distinct **Companion slot**. Weighting: ~50% same-nation as your character, remainder uniform. **This is the free, stochastic channel — enabler-grade (§4.3).** The shop is a separate, *paid* channel with its own tiering (§4.7, which supersedes the earlier "one rotating visiting companion").
- Nation-weighting rationale (load-bearing): same-nation ≠ same-element, so a Mondstadt character is preferentially offered *off-element* Mondstadters — exactly the reaction fuel a mono-element character needs. Element-weighting would offer useless same-element appliers. `Rejected:` element-complement weighting — mechanically optimal but kills the nations-as-factions flavor and makes every character's offers identical in structure.
- **Signature companions:** 1–2 lore-linked companions live in a character's *personal* pool instead (Klee → Prune, her fellow Little Hexenzirkel member). Chosen for story resonance AND for patching the character's statline weakness.

### 4.2 Star rank → rarity (the two-tier structure)
Companion cards mirror Genshin's star system through StS rarity:
- **4-star companions** appear at common/uncommon and may have multiple cards (Bennett's Skill as a common, Bennett's Burst as an uncommon).
- **5-star support companions** appear as **Rares — exactly one card per 5-star**. Availability is governed at runtime, not authoring time (v1.8): each run, the seed rolls a **Featured Banner** of 3 limited 5-stars per nation from the full designed roster; only featured 5-stars appear in that run's companion offers. The banner is shown at run start (the player knows their run's "featured lineup"). In co-op, each player rolls their own banner and drafts from it — divergent lineups per player are the point. Rare frequency still models scarcity: two 5-stars in one deck means a cracked run or deliberate fishing, which should NOT beat "do your own thing" unless the character is designed for it (§4.4). Design consequence: the 5-star roster per nation can now grow without limit; the banner is the governor. Nations with ≤3 designed 5-stars feature all of them (v0.1 Mondstadt: the roll is degenerate and current builds are unaffected).
- **Standard-banner 5-stars** (Jean, Mona, Diluc → Mondstadt; Keqing, Qiqi → Liyue; Tighnari, Dehya → Sumeru; Mizuki → Inazuma) are subsumed as ordinary nation-pool Rare companions with support-shaped cards (their live kits are supports or weak carries anyway; Tighnari waits for Dendro v2). They participate in the banner roll like anyone else, but carry a `standard: true` schema tag so that, if Tier 0.5 banner-variance data shows bad-roll bricking, flipping them to always-available "off-banner floor" status is a one-flag change rather than a redesign.
- v0.1 Mondstadt 5-star Rares: **Albedo** (Geo — Crystallize/defense), **Durin** (Pyro — amplifying-reaction booster), **Nicole** (Pyro — party buff + shield). All three are lore-tied to Klee's circle, and note they model Klee's actual best live team (Klee/Durin/Nicole/Prune).
- `Rejected:` 5-star supports as unplayable pool flavor (wastes the rarity system's natural fit and kills dream teams); 5-star cards subsumed into a designed-partner character's personal pool (couples content releases — Klee could never meet Nicole until "Nicole's owner" ships).

### 4.3 The enabler-not-carry principle (load-bearing, amended)
Companion cards come in three **roles**, all of which route their power *through* your character rather than around them:
- **Appliers** put off-element auras on enemies (Xingqiu, Fischl) — reaction fuel.
- **Buffers** boost your character's own output or defenses (Nicole, Bennett) — note Klee's real best team is buffer-based, not applier-based; both roles are first-class.
- **Triggers** act on existing auras (Prune's Swirl, Albedo's Crystallize).
4-star cards stay at uncommon-grade power. 5-star Rares may be payoff-grade **support** payoffs: strong buffs, reaction amplification, aura manipulation — never an independent damage engine, never self-scaling. Test stands: if deleting your character's own cards from a winning deck wouldn't gut it, companions are too strong. **This applies to the control axis too (v1.5):** if companions negate the enemy while 'your character does stuff,' the supports are the key ingredient — companions never source hard CC, and the SUPPORT_CARRY detector enforces it.

### 4.4 Companion appetite (character-design lever)
A character's statline declaration includes a **companion appetite**: Low (self-sufficient; companions are seasoning), Standard (Klee: reactions are a real archetype but not mandatory), or High (a hypothetical Venti/swirl-themed character *designed* to fish the companion pool — higher aura-starvation tolerance in Tier 0, more companion-synergy hooks in their personal cards). High-appetite characters are the only sanctioned case where companion-fishing outcompetes the character's own plan.

### 4.5 The Spotlight system & `character:` schema field (v1.10)
Every card carries an optional `character:` field (shared schema — all sheets; companion rows derive it from their id prefix, personal sheets from the filename, explicit field wins). Cards with no character tag are invalid Spotlight targets. One Spotlighted character per Furina-class player at a time (per-player in co-op); designation is movable freely and persists until moved; duplicate selectors are inert. Baseline empowerment: +50% printed numbers (flat rate is the knob; texture lives in cards). Self-Spotlight at a reduced rate is the solo fallback and the primary anti-self-buff lever. A per-turn Spotlighted-card cap exists in schema but ships OFF. Empowerment is numbers-only per §2.2a's extension.

> **v1.14 — DRAFT (unratified), 2026-08-06 (R107; S4 finding F3): the designation model above is the RETIRED one.** The section states a character-level, self-Spotlight-at-a-reduced-rate design that [USER] rulings replaced in July, and it states it as current law. The live design is two modes: **CENTER STAGE** — Furina's own cards generate Fanfare and *"receive no numeric Spotlight bonus"* (R41, 2026-07-22) — and **GUEST CAST**, which *"designates the Companion category rather than one character"* (R41; confirmed live in `docs/red-pen-2026-07-26.md` R2(a), which rules on exactly the two-mode split). Consequence for readers: "self-Spotlight at a reduced rate is the primary anti-self-buff lever" is **not** the shipped lever — Center Stage grants no numeric bonus at all. The `character:` field, the invalid-target rule, movable designation, inert duplicate selectors, the +50% baseline for Guest Cast targets and the OFF per-turn cap are unaffected. DRAFT until countersigned; the rulings it records are already live in both engines.

**Generated companion cards (Guardrail 2 ruling, v1.10):** generated companion cards retain their element application. Stochastic, exhausting, drafted off-element access via a personal pool is consistent with "scarce and drafted" — explicit ruling, not silent precedent. Guest Star guardrails: this-combat-only; generators Exhaust; equal-rarity clause; pulls from shared companion pool + purpose-built Guest Star sets, never from playable characters' pools.

### 4.6 v2 candidate — the Wish banner
Shop-integrated "Wish" draw (pay gold, draw from companion pool, duplicate protection as pity). Pengo's Tarot pack proves shop-draw UI is fully moddable. Deferred: v1 validates the pool via reward slot first. (Also: keep it gold-only and generous. We are not building a real gacha as a joke. The joke stops being funny immediately.)

### 4.7 Colorless channel — base-pool removal & the shop two-channel split (v1.11)

> **STATUS: BUILT 2026-07-25, with three amendments.** The shop carries
> companions in both slots, in the mod and in tier 0.5. Read this section as
> live behaviour EXCEPT where the three notes below say otherwise — they are
> amendments to the design, not implementation notes.
>
> **1. Slot 2 has an Uncommon floor (R59), not full card-reward odds.** The
> text below says "full card-reward rarity odds", which is ~60% Common and
> would have made the mod's second colorless slot *worse than base's
> guaranteed Rare* — at the one slot whose entire argument is that it is the
> premium paid channel. Study §7's finding that StS2 colorless has **no common
> tier** points the same way. Slot 2 is wildcard-nation, Uncommon-or-Rare at
> renormalized odds. Not hypothetical: **Fontaine designs zero Rare
> companions**, so Furina's home-region slot 1 already widens the nation
> whenever it rolls a Rare — exactly the brittleness that killed the
> guaranteed-Rare alternative.
>
> *Annotated 2026-08-06 (R107; S4 finding F8): Fontaine Rares are **four**
> since R64 — same day as R59 — and the banner is therefore selective. The
> zero-Rares claim above is historical context for why the slot-2 floor was
> set, not a current fact about the roster.*
>
> **2. The base colorless pool is NOT removed (R60, phase 1).** "Replaces the
> base-game colorless card pool wholesale" below is the ratified *intent*; what
> ships is a shop-only override. `ColorlessCardPool` has **seven consumers**,
> six of them outside the shop, including three `GetDistinctForCombat` sites —
> asking N distinct cards of an emptied pool is the empty-draw class that
> softlocked Dusty Tome. Full removal needs a seven-consumer audit and is a
> sprint of its own; whether base colorless surfacing through in-combat
> generation is a fantasy leak worth that blast radius is a [USER] taste call,
> graded after table time. Deferred, not rejected.
>
> **3. Companions are still not a `CustomCardPoolModel`.** §4.1 above describes
> them as one. They are queried through `CompanionPool`, a filter surface over
> the single roster, because `MerchantCardEntry` takes a plain card list and
> needs no pool object. Registering a real shared pool is now **feasible**
> (BaseLib grew `ModelDbSharedCardPoolsPatch` after the repo recorded that it
> could not be done) but would migrate all 47 companions out of the character
> pools, changing every companion's card frame. A cost decision, open for
> [USER].
>
> **Pricing carries one silent discount.** `MerchantCardEntry.GetCost` adds
> **×1.15 only when `card.Pool is ColorlessCardPool`**, which companions are
> not — so the mod's premium channel is ~15% cheaper than the base channel it
> replaces. Sim and mod agree on the bands.
>
> **Measured, and it complicates the thesis below.** The channel moved winrate
> by a null (−0.2pp mean over 500 runs/arm × 3 characters), crowded out relic
> purchases by ~30%, and left unspent gold unchanged — runs end holding ~220
> gold. **"Gold price is the balance governor" is not currently true in the
> sim, because the purse does not bind.** See
> `docs/archive/shop-companion-channel-sprint-log.md` §4; open for [USER].


**Decision:** the companion pool **replaces the base-game colorless card pool wholesale.** The mod ships *no* base StS2 colorless cards; every channel that would have offered a colorless card offers a companion instead. Rationale: the companion pool already *is* this mod's colorless content (`IsColorless`, §4.1). A generic base colorless card sitting next to "Fischl — Oz, at your side" dilutes the Teyvat fantasy and steps on the identity we spent the most engineering on.

**The value-inversion problem this must solve:** base colorless is conventionally costed *above* rate on value-per-energy — it's the premium "splash." Companion cards are costed *below* rate as enabler fuel (§4.3). So companions cannot fill the colorless slot 1:1. The resolution is that the two acquisition channels are **different economies rolling different tiers** — not a stat buff:

- **Free channel (reward slot, §4.1):** unchanged. Stochastic, nation-weighted (~50%), enabler-grade. Its value proposition is **capability** — the only *free* source of off-element access (Pillar 2) — not per-energy stat efficiency. A whiff is "fuel I didn't need," never a dead pick, because no character is required to react to clear (Pillars 1 & 4).
- **Paid channel (shop):** the premium/targeted channel, where StS colorless is conventionally strongest *because you paid gold for it*. **Two colorless slots**, replacing base StS2's two shop colorless slots:
  - **Slot 1 — Home-region draw:** always rolls from the player character's own **nation**, guaranteed **Uncommon or higher**. The reliable, targeted slot — "buy your dream support." Leans off-element *by construction*: same-nation ≠ same-element (§4.1 rationale), so the guaranteed slot-1 companion is preferentially reaction fuel. 5-star Rares here are banner-gated (§4.2); if the banner has emptied the nation's Rare tier, slot 1 falls through to Uncommon exactly as the reward slot does.
  - **Slot 2 — Wildcard draw:** a complete free-for-all — any nation, full card-reward rarity odds (mostly Common/Uncommon, Rare rarely), banner-gated 5-stars. The "you never know what's on offer" slot; where an out-of-nation 5-star can surface.
  - **Pricing is the balance governor.** Both slots price by the drawn card's rarity at base shop-card gold bands; slot 1's Uncommon floor makes it the pricier, premium buy. Gold cost — not a stat nerf — is what keeps a payoff-grade 5-star support fair, exactly as base StS prices its shop rares. This is why the shop can safely roll the strong end of the pool while the free reward slot stays enabler-grade.

**Guardrail note:** routing 5-star Rares and burst-grade 4-stars through the *paid* channel does **not** violate §4.3 — that principle caps power *per rarity grade*, and §4.3 already permits 5-star Rares to be payoff-grade support payoffs. The shop changes *where* premium companions appear, not *how strong* they're allowed to be.

**Utility-coverage checklist (must clear before deleting the base pool):** base colorless also carried **neutral fixing/velocity** that isn't reaction-flavored — raw card draw, energy, in-combat card removal/thinning, block splash. Removing the pool removes those functional roles unless they're covered elsewhere. Before ship, confirm each is reachable via (a) companion cards that happen to provide it, or (b) each character's velocity/tempo archetype (the §3 archetype-3 slot). If neither covers "thin / draw / fix," the removal has quietly opened a deckbuilding hole base StS never had — patch by seeding a few neutral-utility companions (a Sucrose-draw, a Katheryne-style thin), **not** by re-admitting base colorless. (Card-removal as a shop *service* is separate from colorless *cards* and is unaffected.)

**Audit result (v1.11 — checklist cleared, one ruling).** Ran against the live pool (Klee + Furina + both companion sheets):
- **Card draw** ✅ covered — character pools carry it heavily (Klee 8 / Furina 15 draw effects) plus companions (Lynette *Box Trick* draw 2, Charlotte, Sucrose).
- **Block splash** ✅ covered — companions (Charlotte, Dahlia, Barbara, Bennett) + every character's own defense.
- **Permanent thinning / removal** ✅ unaffected — the shop card-removal *service* is not a colorless card.
- **In-combat exhaust/thin** ✅ present but character-scoped (Klee's status-exhaust cards); no neutral Purity-analog, an acceptable minor loss.
- **Energy generation** ❌ **genuine pool gap.** No companion sources real (StS action-) energy — companions grant only `burst_energy` (the meter). Current characters happen to self-provide (Klee ×1 `sugar_rush`, Furina ×3), but **that is the wrong test** (see corrected framing below). Base colorless let *any* character draft a fixer (Production: +2 energy, Exhaust) to patch a kit gap; the pool inherited that mandate and currently fails it for energy. **Fix: add a neutral-energy companion** (Production-analog — Exhaust, uncommon; a Mondstadt support such as Sucrose is the natural home), not a per-character patch. **FILLED (v1.11a):** `sucrose_catalyst_conversion` — *Sucrose — Catalyst Conversion*, Uncommon, `0-cost, gain 1 energy, draw 1, Exhaust`. Anemo (no aura → clean fixer, not stealth reaction-fuel); reliably shoppable at shop slot-1 (home-region, Uncommon-floor). 239 tests pass.

**Corrected framing (v1.11a) — the pool must cover gaps, not just the current roster.** The audit's first pass asked "does a current character have X"; the right question is "can *any* character, present or future, **draft** X from the shared pool to patch a kit gap" — because that universal gap-filling is precisely what base colorless did, and the companion pool now inherits it. A future playable Mondstadter with a hole in its kit must be able to shop the pool for the fix, exactly as it could shop base colorless. Draw (Lynette *Box Trick*) and block (Charlotte, Dahlia) already satisfy this pool-wide; **energy does not, and is the one concrete hole to fill before more characters ship.** In-combat thinning is a lesser pool gap (no neutral Purity-analog companion; permanent removal remains the shop service).

**Two-part energy ruling (supersedes the earlier "character-kit-only" wording):** (1) neutral **StS action-energy / draw / thin** are *legal* companion utility — enabler-grade one-shot fixers, gated exactly as base colorless gates them (costed, usually Exhaust), which does **not** breach §4.3 because a one-shot fixer is an enabler, not an engine; (2) **Burst-meter (`burst_energy`) generation stays character-kit-scoped** and must never be cheaply repeatable from companions (the Sucrose Exhaust guard is an instance). The two "energies" are different resources: action-economy is universal colorless-role fixing that the pool owes every character; the Burst meter is character-defining and stays home.

`Rejected:` (a) *additive* model — base colorless still appears in its own slot alongside companions; rejected for fantasy dilution and for making the reward economy carry two colorless-shaped things. (b) buffing companion base numbers up to the colorless value bar; rejected — breaks enabler-not-carry (§4.3) directly. The value-per-energy gap is real and is resolved by **channel and pricing**, not by inflating companion cards. Empirical validation of the gap lives in `companion-value-vs-colorless-study.md`.

## 5. Artifacts → Relic Sets
- Artifacts are a relic subcategory with **2-piece set bonuses**: each piece has a modest standalone effect; holding both pieces of a set activates a named set bonus (Crimson Witch: pieces give minor Pyro/reaction perks; set bonus: amplifying reactions +25%).
- Sets per release: 4–6, themed to reaction styles rather than to characters, so they're cross-character content.
- `Rejected:` 4-piece sets (never completes in a run) and artifact main-stat/substat rolls (that's a stat sheet, see §1 Not-adopting).

## 6. Weapons → Starting loadout
- A character's weapon is their "slot 0" relic. **v1: fixed weapon per character** (Klee: Pounding Surprise is the talent-relic; weapon flavor folded in).
- **v2:** run-start choice among 2–3 weapons per character (Neow-adjacent UI patch), functioning as alternate starting relics that nudge archetype choice (e.g., a weapon that starts combats with 1 Bomb placed vs. one that grants Burst Energy). Deferred for UI cost, not design doubt.

## 7. Balance guardrails (enforced via Tier 0 + review)
1. Amplifier hits capped at 4× base in provenance logs; investigate anything above.
2. No character card may apply an off-element aura. Off-element = companions/co-op only. (This is Pillar 2 in card form.) **v1.10 ruling:** generated companion cards retain their element application (§4.5) — stochastic, exhausting, drafted access stays consistent with "scarce and drafted."
3. Companion cards: 4-star cards ≤ uncommon power grade; 5-star Rares (max 3/nation, one card each) may be payoff-grade but only as support payoffs (buff/amplify/aura work) — no independent damage engines, no self-scaling.
4. Every archetype must pass the aura-starvation / bricking checks in the simulator before implementation.
5. New keywords per character: ≤2 beyond the shared element system; support-protagonists (§4.4 High-appetite or Appendix A lineage) may carry one additional keyword via logged amendment with compensating cuts. (v1.10 — the amendment sanctions *one* extra, not open season; Columbina will pressure even this budget.)
6. True in-combat healing is Rare-tier AND Exhausts (conjunctive — R8 law, v1.10); below Rare, sustain routes through Block or character-specific buffer pools; no 4-star companion may true-heal. Exempt: potions (base-game-priced consumables) and relic-scale trickles.
7. **What the simulator's authority actually is (G-E4, 2026-07-25).** Absolute tier-0.5 winrates are **pilot-limited floors, not predictions about human play**. The pilot plays a fixed policy; it does not read the board the way a person does, does not learn across a run, and does not save a resource for a turn it can see coming. So a 4% arm is not a claim that a human wins 4% of the time — it is a claim about what that deck does *when piloted that way*. The 2026-07-25 co-op playtest confirmed the direction: two A8 regulars full-cleared A0 against sim winrates in the single digits. **"Sims are worse than real players" is settled, and it is written here so it stops being re-litigated once per pass.**

    The instrument's authority is **relative deltas and structural findings**, and there it is strong — the playtest agreed with it directionally on every structural claim it had made (Fanfare saturation, payoff reach, the decoupling of act-1 clear from run winrate, salon-versus-the-rest). Read the sim for *which* of two things is better and *why* a plan fails; do not read it for how often a person will win. A ratification that rests on an absolute winrate is resting on the wrong number.

    Corollary, learned the same day: this cuts *both* ways. A plan-committed drafter is also better than a human at *staying on plan*, so an archetype's measured winrate can be an over-estimate of what a real drafter reaches — see the G-E3 free-draft cell, where salon fell 18.3% → 4.0% once the drafter was no longer told the plan.

## 8. Content roadmap
- **v0.1 (vertical slice):** Element system + Klee (full pool) + 12–16 companion cards (Mondstadt-weighted) + 2 artifact sets. Solo + co-op.
- **v0.2:** Second character: **Furina** (Skill-grade, Hydro — picked; kickoff docs/furina-kickoff-v0.1.md), shipping with the **Fontaine 4-star companion set v0.1** (Lynette, Freminet, Charlotte, Chevreuse at 3-card kits — the complete Fontaine 4-star bench; loaded and simming as of 2026-07-20). Wish banner. Weapon choice.
- **v0.3+:** Dendro + third character + artifact set expansion.

## 9. Asset & IP policy
All card art, character art, and audio are original or commissioned "in the StS style" — no extracted HoYoverse game assets, no official splash art, in anything publicly distributed. Fan-made original art is the norm HoYoverse's fan policies tolerate; ripped assets are what gets Workshop items DMCA'd. Placeholder art in private builds is fine; nothing ripped ships.


## Appendix A — The support-protagonist design space (the Columbina problem)

Flagged for v0.2+ planning: characters whose Genshin identity is *support* (Columbina being the motivating case: Nod-Krai's universal support, functioning either as the super-buffer for any of the region's team archetypes or as a "driver" who steals the supports and triggers their kits herself — the best support or the worst carry, by choice). "5-star support as playable character" is a different design space from "5-star carry" and needs its own template extensions:

1. **The precedent already exists in StS2.** Necrobinder proves driver+carried-unit works as a solo archetype (she pilots Osty). A support-protagonist generalizes this: her "carry" is whatever she drafts.
2. **Solo mode = the Driver.** She is the sanctioned **High companion-appetite** character (§4.4). Her personal pool is deliberately thin on damage; her cards act ON companion cards — replay them, discount them, duplicate them, upgrade them, trigger their effects twice. Companions are her chips; she is the mult. Guardrail 3's "no independent companion damage engines" stays intact because the engine is HER cards acting on them.
3. **Bricking mitigation is mandatory.** High-appetite characters die to bad companion offers. Her starting relic must guarantee acquisition (e.g., companion slot becomes choose-1-of-3, or a free Wish at each shop). Aura-starvation tolerance in Tier 0 is raised for her, but zero-companion runs must remain *possible* — Pillar 4: "worst carry" must still clear solo, worst ≠ nonviable. Her floor is the design's hardest tuning problem.
4. **Co-op mode = the Buffer.** First character to need **ally-targeted cards** (cross-player buffs/shields/energy). New engineering: TargetType ally + cross-player effect sync. Every ally-target card needs a solo fallback line ("no ally: apply to self at reduced effect") so her pool isn't half-dead solo.
5. **Statline shape:** A1≈1, A5/A6 = 4–5, everything else borrowed. This violates nothing — it's the template's extreme legal corner.
6. **Region coupling:** she ships with the Nod-Krai companion pool by necessity (a driver needs a garage). Nod-Krai's lunar-reaction family is deferred alongside Dendro — do not couple her release to a new reaction subsystem; her v1 drives the base six elements.

## 10. Amendment log
- v1 (initial): decisions as above. Open items intentionally deferred: Dendro design, Wish banner economy, weapon-choice UI, second-character selection.
- v1.1: Corrected Albedo to 5-star. Added two-tier companion structure (§4.2): 5-star supports as Rares (one card each, ≤3/nation), 4-stars at common/uncommon with multi-card kits. Companion roles taxonomy (Applier/Buffer/Trigger) — buffers promoted to first-class after checking Klee's live best team (Klee/Durin/Nicole/Prune) is buffer+swirl, not applier-based. Prune replaces Albedo as Klee's personal-pool signature companion (Little Hexenzirkel lore); Albedo/Durin/Nicole become Mondstadt shared Rares. Added companion-appetite lever (§4.4). Guardrail 3 amended to match.
- v1.2: Added Appendix A (support-protagonist design space / Columbina). No changes to v1 systems; Columbina explicitly targets the §4.4 High-appetite slot.
- v1.4: Burst cards gain Retain (§2.4), per Tier 0 pass-1 finding that discard rhythm made Bursts uncastable.
- v1.5: Frozen redesigned (soft control + Shatter; stun becomes payoff-tier per §2.2a hard-CC pricing rule) after user caught the base-game stun-scarcity mismatch. Enabler-not-carry extended to the control axis with SUPPORT_CARRY detector. Healing-grade policy added: true in-combat healing is rare-tier or Exhausts; repeatable sustain routes through capped buffer pools (see furina-predesign-notes.md — the pattern debuts with Furina and becomes mod-wide). Companion sheet errata: Barbara/Bennett heals gain Exhaust.
- v1.6: Encore revised to unbounded-per-combat (Regent-star pattern) after user ecosystem review; Fanfare becomes the capped resource (%-of-maxHP, Rare uncappers at setup cost). Buffer-pool policy wording updated. Carry Companion / Spotlight design space opened for support-protagonists.
- v1.7: Lore-audit correction — Xingqiu (Liyue) removed from Mondstadt pool, cards re-flavored to Dahlia. Lore audit added to companion checklist.
- v1.8: 3-per-release cap replaced by the seeded **Featured Banner** (3 limited 5-stars per nation rolled per run; per-player in co-op; shown at run start). Rotation moves from authoring-time (which someone must remember) to runtime (which the seed remembers). Standard 5-stars subsumed as ordinary support-shaped nation Rares with a `standard` tag as the off-banner-floor escape hatch. v1.7's rotation-bench concept superseded. Mona's Omen card flagged for the amp-cap watchlist when designed.
- v1.9: Bursts become kit cards (innate-on-charge) after Tier 0.5 decomposition showed Burst acquisition was the binding constraint on reaction assembly (5.8% = 79% × 71% × 10%, the 10% being 'ever saw the Burst'). Retain (v1.4) is retained for the in-hand behavior. Rare pool: 14 draftable rares.
- v1.10 (2026-07-20): **Furina kickoff batch ratified** (furina-principles-amendment-batch.md; red-pen record furina-sprint-1-redpen.md). New §4.5 Spotlight system + `character:` schema field; §2.2a extension (Spotlight numbers-only, never turn-economy); Guardrail 5 support-protagonist keyword exception; Guardrail 2 generated-companion-cards ruling; R8 conjunctive healing law codified as Guardrail 6 with potion/relic-trickle exemptions; Fontaine 4-star set v0.1 into Furina's release scope (§8). **Encore & Fanfare final definitions (supersede furina-predesign-notes.md Part 2):** Encore = unbounded per-combat buffer (v1.6 house style), absorbs after Block and before HP; potent cards carry "Spend N Encore:" cost lines; overdraw drains true HP; Tier 0 accounting binding — Encore absorption credits A4, never A3. Fanfare = capped at %maxHP; generation strictly activity-based (HP lost, Encore gained, Encore spent, Spotlighted card played); no passive per-turn accrual, ever; a global pool that survives Spotlight moves. Wish banner renumbered §4.5→§4.6.
- v1.11 (2026-07-21): **Base colorless pool removed; the companion pool becomes the mod's sole colorless content (new §4.7).** Two-channel model resolves the value-inversion problem (base colorless is costed above-rate, companions below-rate per §4.3): the free reward slot stays enabler-grade/stochastic (value = capability, not per-energy stats); the shop is the paid premium/targeted channel with two slots — **Slot 1** home-region, Uncommon floor ("dream support"); **Slot 2** wildcard at card-reward odds. Gold pricing is the governor that lets the shop roll payoff-grade 5-stars without violating §4.3 (which caps power per grade, not per channel). Supersedes §4.1's "one rotating visiting companion." Added the utility-coverage checklist (neutral draw/energy/thin must remain reachable post-removal, patched via neutral-utility companions, never by re-admitting base colorless). Value-inversion gap referred to `companion-value-vs-colorless-study.md` for empirical validation; resolution is channel + pricing, not stat buffs. Study since completed: real StS2 colorless data (study §7) confirms StS2 colorless has **no common tier** (voids the hypothesis's bottom rung) and clean rare bodies top ~10 v/e (below StS1's 15+) — the companion pool clears the bar comfortably. Utility-coverage audit run (§4.7 audit result): draw + block covered pool-wide, but **energy is a genuine pool gap** — corrected framing (v1.11a): the shared pool must let *any* character (present or future) draft a gap-patch, as base colorless did, so "a current character self-provides" is the wrong test. Two-part energy ruling: neutral action-energy/draw/thin are legal enabler-grade companion utility (one-shot, Exhaust-gated), while Burst-meter generation stays character-kit-scoped. **Action: add a neutral-energy companion** (Production-analog, Exhaust; Mondstadt/Sucrose). `sucrose_astable` rebalanced 2→0 cost + Exhaust — the pool's one genuinely undercosted card.
- v1.11b (2026-07-25): **R62 — `sucrose_astable` restored to the v1.11a numbers (free, Exhaust), superseding main's interim rebalance.** The two edits collided in the 2026-07-26 merge and main won on recency, which quietly dropped the Exhaust. Red-pen ruled the Exhaust back in: it was never only a cost fix but a *guard* against the card becoming a repeatable multi-copy Burst battery (§2.4, §4.3). The guard does not currently bind — Bursts are not priced strongly enough for replaying the card to be worth the energy — so it is retained as cheap insurance against a future Burst reprice rather than as a live constraint. §4.7's v1.11a changelog text is accurate again as written.

---

### ~~Amendment DRAFTS — proposed, NOT ratified (added 2026-07-29)~~ Amendments v1.12 and v1.13 — **RATIFIED 2026-08-06**

> **RATIFIED 2026-08-06, and the fence comes down — recorded, not silently.**
> Second sitting of 2026-08-06 (sixth-wave brief, Track Y item Y-7;
> transcribed at `docs/sitting-record-predraft-2026-08-06.md` §7): *"v1.12/v1.13
> amendments RATIFIED; unratified banners drop; law text now matches shipped
> code."* Gates `S4-G3` (v1.12) and `S4-G4` (v1.13) are discharged. **Both
> entries below are LAW.** They keep their position in the file rather than
> being re-cut into the ratified log above, so that the fence's own history —
> drafted 2026-07-29 against already-shipped code, ratified eight days later —
> stays readable; every DRAFT marker in them is struck, never deleted (R101b).
>
> **The ratification was conditioned on a code read, and the read was done.**
> Y-7's instruction was to ratify only if the law text matches what ships, and
> to stop and surface otherwise. Verified before the banners dropped:
>
> - **v1.12.** `tier0/constants.py` carries exactly the four live generation
>   legs — `FANFARE_PER_HP_LOST`, `FANFARE_PER_ENCORE_SPENT`,
>   `FANFARE_PER_ENCORE_ABSORBED`, `FANFARE_PER_SPOTLIGHT_CARD` — and
>   `FANFARE_PER_ENCORE_GAINED` is deleted with its reason in place. The
>   invariant is pinned in the sim by
>   `test_every_point_past_block_prints_exactly_one_fanfare`
>   (`tier0/tests/test_furina.py`), and C#'s two halves round to it deliberately
>   (`FurinaResources.cs`, the HP-loss mint's ceiling cast, matching
>   `AbsorbDamage`). `FANFARE_FLOOR_PER_POWER`/`_RARE` are absent from BOTH
>   engines, and the printed keywords that replaced them are enforced by rule R6
>   of `tools/lint_furina_registers.py`. What the amendment says it does not
>   touch is untouched: `FANFARE_CAP_FRACTION` is still a fraction of maxHP, and
>   there is still no passive per-turn accrual.
> - **v1.13.** `SalonVisualsBridge.cs` declares `SpriteScaleMax = 0.5f` and
>   applies `Mathf.Min(SpriteScaleMax, spacing / width)` — the bound is written
>   down AND answers to the pitch, which is exactly the amendment's condition —
>   and `tier0/tests/test_visual_contract_gaps.py` asserts all three facts (the
>   cap equals beam/`TARGET_H`, a scale is set at all, and the pitch is read).
>
> **One nuance recorded rather than smoothed over,** because the amendment text
> says it: v1.12 describes the every-point invariant as *"pinned as a test in
> both engines"*. It is a test in the sim and a documented, parity-swept
> construction in C# — there is no C# test project to hold a pin (see the
> standing note that co-op has no sim backstop). The LAW the amendment states —
> which legs generate Fanfare — matches shipped code in both engines exactly,
> so this is a claim about test infrastructure, not a mismatch in the rule, and
> it was not treated as one.
>
> **What ratifying does NOT ratify,** restated from v1.12's own closing
> paragraph so the discharge cannot be over-read: the X values remain PROPOSED
> (the `S4-G9` ratification batch), and the fanfare archetype's pre-registered
> STOP at 1.8% against its 2.0% floor is untouched.

> ~~These two entries are **DRAFT (unratified)**. They are written in the
> amendment-log style so they can be ratified by countersign without being
> re-drafted, and they are fenced off below the ratified log so no reader
> mistakes them for law.~~ **Both are ratified as of 2026-08-06; the fence is
> historical.** Nothing above this line was renumbered, reworded or
> altered. Both record changes that have **already shipped in code** while the
> principles text still states the superseded rule — which is the situation
> the fence existed to make visible. Filed by the doc de-drift pass
> (`docs/backlog-2026-07-29.md` §2).

- **v1.12 — ~~DRAFT (unratified)~~ RATIFIED 2026-08-06: Fanfare generation is SINGLE-LEG on Encore.**
  Amends the v1.10 entry's Fanfare definition, which still reads *"generation
  strictly activity-based (HP lost, Encore gained, Encore spent, Spotlighted
  card played)"*. **The "Encore gained" leg is dead.** Ruled [USER]
  2026-07-28 (post-playtest-3) and shipped the same day in both engines —
  `docs/sprint-fanfare-rework-2026-07-28.md` Track A, executed and measured in
  `docs/sprint-fanfare-rework-log-2026-07-28.md`.

  Proposed replacement text: *Fanfare prints when Encore goes DOWN, never when
  it goes up.* All three reduction paths qualify — salon upkeep ticks, explicit
  card spends, and absorption (`encore_absorbed`, a NEW leg: absorbed Encore is
  deferred Block that will never block a future hit, so cashing it is a real
  cost). The live generation set is therefore **HP lost / Encore spent / Encore
  absorbed / Spotlighted card played**. The design invariant that replaces the
  old asymmetry, and that is pinned as a test in both engines: **every point of
  damage that gets past Block prints exactly 1 Fanfare** — through absorption
  if the buffer eats it, through HP loss if HP does. Before the change,
  absorbed damage printed 0.

  Measured price at ratification (stoker arm): total generation fell **34%**
  (44% was predicted; the two surviving reduction legs both grew). Post-change
  source shares: hp_lost 45.4%, encore_spent 24.1%, encore_absorbed 20.8%,
  center_stage 9.7%. **Every Fanfare number taken before 2026-07-28 is
  archive.**

  Rider, same sprint, same ruling session and part of the same amendment if it
  is taken: the invisible `FANFARE_FLOOR_PER_POWER` rule is **deleted** and
  replaced by printed keywords — **`Fanfare Cap +X`** (raises the cap only) and
  **`Fanfare +X`** (the full grant: current, floor and cap; a **rare POWER
  payoff only**, enforced by lint R6). Spelled "Fanfare Cap", never bare "Cap".
  Consequence to state plainly because it changes how those cards read: the cap
  has been a non-binding safety rail since F-A5, so a card printing only
  `Fanfare Cap +X` is paying close to nothing at current constants.

  **What this amendment does NOT touch:** the no-passive-per-turn-accrual law
  is untouched and remains binding, and the cap stays at %maxHP.

  **Status: ~~DRAFT~~ RATIFIED 2026-08-06 (Track Y / Y-7); `S4-G3` discharged.**
  The direction is [USER]-ruled; the X values remain
  PROPOSED (`docs/backlog-2026-07-29.md` §3 item 9, the ratification batch),
  and the fanfare archetype itself is under a pre-registered STOP at 1.8%
  against its 2.0% floor. Ratifying this text does **not** ratify those
  numbers.

- **v1.13 — ~~DRAFT (unratified)~~ RATIFIED 2026-08-06: the pre-scaled-art house rule is amended for
  per-player-stat pitches.** The standing house rule is *"ship pre-sized art,
  no runtime minification"* (`docs/art-asset-manifest.md`, enforced in
  `tools/cut_salon_members.py` and `tier0/tests/test_visual_contract_gaps.py`).
  It is **already amended in code** and the amendment is recorded nowhere but a
  playtest note — `docs/playtest3-notes-2026-07-28.md` (answer 2), following
  **A12**, which promoted the Salon member cap from a constant to a per-player
  stat.

  Proposed text: *pre-scaled art remains the rule wherever the layout pitch is
  fixed. Where the pitch is a function of a per-player stat, no single cut size
  can serve it, and runtime fitting is permitted — bounded, with the bound
  written down and asserted by a test.* The shipped instance: member art is cut
  at 144px tall and was drawn 1:1 on a 62px pitch (members had always
  overlapped by about half); A12 tightened the pitch to 39.5px and turned
  "ugly" into "unreadable". The fix fits the art to the slot at runtime
  **capped at 0.5** — exactly half the master and exactly the 72px beam, so a
  three-member stage is a clean 2x downscale and only a RAISED cap ever goes
  below it. Pool, beam and ghost decorations squash horizontally on the same
  rule, because the pool carries the accent hue and overlapping pools blur the
  identity signal the hue exists to provide.

  Why it belongs in the principles rather than in the art manifest alone: the
  rule it amends is a *ship* rule that three tools and a suite test enforce,
  and the amendment's condition ("the pitch is a per-player stat") is a design
  fact, not an art fact — the next character with a stat-sized board inherits
  it.

  **Status: ~~DRAFT~~ RATIFIED 2026-08-06 (Track Y / Y-7); `S4-G4` discharged.**
  Shipped and deployed (playtest 3 fix); ~~the general rule
  change has never been ratified~~ **the general rule change is now law**, and
  the gap test it replaced was rewritten as the arithmetic check it always said
  it should become.
