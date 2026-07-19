# Teyvat Spire — Mod Design Principles (v1)

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
| Hydro×Cryo | Frozen | Enemy skips next intent (bosses: reduced effect) |
| Anemo trigger | Swirl | Copy target's aura to all enemies |
| Geo trigger | Crystallize | Gain Block |

**Iron rule: amplifiers are per-hit and consume the aura.** No persistent damage multipliers from reactions, ever. This is the balance governor; it's also faithful. `Rejected:` reaction-stacks-as-buff designs — they turn ×1.5 into a compounding engine and every deck becomes Vaporize goodstuff.

### 2.3 Application cadence (the "ICD dial")
Per-character setting for how often attacks carry their element:
- **Catalyst-grade** (Klee): every attack applies. Maximum reaction fuel, so these characters get lower base numbers.
- **Skill-grade** (most weapon users): only cards tagged *Skill*/*Burst* apply. Higher base numbers, reactions are punctuation, not rhythm.
This dial is our main cross-character balance lever for reaction frequency.

### 2.4 Burst Energy
- Per-character meter, per-combat, starts at 0. Gained by: playing Skill-tagged cards (+N) and triggering reactions (+N; the "particle economy").
- Each character's **Burst** is a signature rare card, in the starting deck or early pool, unplayable until the meter is full; playing it empties the meter. **Burst cards have Retain** — they stay in hand at end of turn. (v1.4 ruling: without Retain, StS's discard rhythm cycles the Burst away before the meter fills — sim-verified. Retain is also faithful: a charged burst doesn't evaporate.)
- Relic space may carry partial energy between fights (Favonius-flavored). Meter size is a per-character balance knob (Klee ~60-grade; a nuke burst like a Raiden-analogue ~90-grade).

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
- **Acquisition:** every card reward gains a 4th, visually distinct **Companion slot**. Weighting: ~50% same-nation as your character, remainder uniform. Shop carries one rotating "visiting companion."
- Nation-weighting rationale (load-bearing): same-nation ≠ same-element, so a Mondstadt character is preferentially offered *off-element* Mondstadters — exactly the reaction fuel a mono-element character needs. Element-weighting would offer useless same-element appliers. `Rejected:` element-complement weighting — mechanically optimal but kills the nations-as-factions flavor and makes every character's offers identical in structure.
- **Signature companions:** 1–2 lore-linked companions live in a character's *personal* pool instead (Klee → Prune, her fellow Little Hexenzirkel member). Chosen for story resonance AND for patching the character's statline weakness.

### 4.2 Star rank → rarity (the two-tier structure)
Companion cards mirror Genshin's star system through StS rarity:
- **4-star companions** appear at common/uncommon and may have multiple cards (Bennett's Skill as a common, Bennett's Burst as an uncommon).
- **5-star support companions** appear as **Rares — exactly one card per 5-star**, capped at **3 per nation pool per release**. Rare frequency in the companion slot naturally models 5-star scarcity: assembling two 5-star companions means a cracked run or deliberately fishing (extra rewards, shop gold), which is a legitimate deckbuilding strategy that should NOT beat "do your own thing" unless the character is designed for it (see §4.4).
- v0.1 Mondstadt 5-star Rares: **Albedo** (Geo — Crystallize/defense), **Durin** (Pyro — amplifying-reaction booster), **Nicole** (Pyro — party buff + shield). All three are lore-tied to Klee's circle, and note they model Klee's actual best live team (Klee/Durin/Nicole/Prune).
- `Rejected:` 5-star supports as unplayable pool flavor (wastes the rarity system's natural fit and kills dream teams); 5-star cards subsumed into a designed-partner character's personal pool (couples content releases — Klee could never meet Nicole until "Nicole's owner" ships).

### 4.3 The enabler-not-carry principle (load-bearing, amended)
Companion cards come in three **roles**, all of which route their power *through* your character rather than around them:
- **Appliers** put off-element auras on enemies (Xingqiu, Fischl) — reaction fuel.
- **Buffers** boost your character's own output or defenses (Nicole, Bennett) — note Klee's real best team is buffer-based, not applier-based; both roles are first-class.
- **Triggers** act on existing auras (Prune's Swirl, Albedo's Crystallize).
4-star cards stay at uncommon-grade power. 5-star Rares may be payoff-grade **support** payoffs: strong buffs, reaction amplification, aura manipulation — never an independent damage engine, never self-scaling. Test stands: if deleting your character's own cards from a winning deck wouldn't gut it, companions are too strong.

### 4.4 Companion appetite (character-design lever)
A character's statline declaration includes a **companion appetite**: Low (self-sufficient; companions are seasoning), Standard (Klee: reactions are a real archetype but not mandatory), or High (a hypothetical Venti/swirl-themed character *designed* to fish the companion pool — higher aura-starvation tolerance in Tier 0, more companion-synergy hooks in their personal cards). High-appetite characters are the only sanctioned case where companion-fishing outcompetes the character's own plan.

### 4.5 v2 candidate — the Wish banner
Shop-integrated "Wish" draw (pay gold, draw from companion pool, duplicate protection as pity). Pengo's Tarot pack proves shop-draw UI is fully moddable. Deferred: v1 validates the pool via reward slot first. (Also: keep it gold-only and generous. We are not building a real gacha as a joke. The joke stops being funny immediately.)

## 5. Artifacts → Relic Sets
- Artifacts are a relic subcategory with **2-piece set bonuses**: each piece has a modest standalone effect; holding both pieces of a set activates a named set bonus (Crimson Witch: pieces give minor Pyro/reaction perks; set bonus: amplifying reactions +25%).
- Sets per release: 4–6, themed to reaction styles rather than to characters, so they're cross-character content.
- `Rejected:` 4-piece sets (never completes in a run) and artifact main-stat/substat rolls (that's a stat sheet, see §1 Not-adopting).

## 6. Weapons → Starting loadout
- A character's weapon is their "slot 0" relic. **v1: fixed weapon per character** (Klee: Pounding Surprise is the talent-relic; weapon flavor folded in).
- **v2:** run-start choice among 2–3 weapons per character (Neow-adjacent UI patch), functioning as alternate starting relics that nudge archetype choice (e.g., a weapon that starts combats with 1 Bomb placed vs. one that grants Burst Energy). Deferred for UI cost, not design doubt.

## 7. Balance guardrails (enforced via Tier 0 + review)
1. Amplifier hits capped at 4× base in provenance logs; investigate anything above.
2. No character card may apply an off-element aura. Off-element = companions/co-op only. (This is Pillar 2 in card form.)
3. Companion cards: 4-star cards ≤ uncommon power grade; 5-star Rares (max 3/nation, one card each) may be payoff-grade but only as support payoffs (buff/amplify/aura work) — no independent damage engines, no self-scaling.
4. Every archetype must pass the aura-starvation / bricking checks in the simulator before implementation.
5. New keywords per character: ≤2 beyond the shared element system.

## 8. Content roadmap
- **v0.1 (vertical slice):** Element system + Klee (full pool) + 12–16 companion cards (Mondstadt-weighted) + 2 artifact sets. Solo + co-op.
- **v0.2:** Second character, deliberately Skill-grade cadence and Hydro or Cryo (maximizes reaction coverage with Klee in co-op; candidates: Ayaka, Furina, Xiao — pick after Klee data). Wish banner. Weapon choice.
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
