# S14 — Non-Card Parity Sweep: Fable Triage Memo

Date: 2026-08-05. Companion memo to `noncard-findings-ledger.md` (173 entities, 174
findings, every citation mechanically audited). Merges with the S1 card-sweep triage
(`triage-memo.md`): shared systemic families are cross-referenced to S1's SYS-numbers,
and exploits from the S13 ledger whose enabler turns out to be a *parity defect* are
flagged, because that changes which ledger the mechanism belongs to. **No fixes are
proposed anywhere in this memo.**

Confidence marks: (†) found independently by two or more agents from different
surfaces (e.g. once from the companion side, once from the powers side) — treat as
high-confidence without further reading.

## Ranked systemic defects

### NC-1 · HIGH · Companion/power damage skips the damage pipeline in C# (†)

**DISPOSITION 2026-08-06 — RULED, SIM CANONICAL (R116).** Verbatim: *"They are supposed to also scale with you like your own cards."* C# routes companion-power damage through the full damage pipeline (Strength, Weak ×0.75, Vulnerable ×1.5); parity vectors updated; the Durin's Witch's Flame line evidence below becomes the regression test. **Errata Batch 2 item 3, mod-only; not executed by the paper track.** **NC-11 is explicitly NOT covered** — see its own disposition.
tier0 routes companion-power damage through the full pipeline (Strength, Weak ×0.75,
Vulnerable ×1.5); the mod deals it as raw, dealer-less Unpowered hits. Found from both
sides for Durin's Witch's Flame (`effects.py:2560-2568` vs `CompanionPowers.cs`), and
the same shape underlies the Kurage pulse's direct `p.block +=` write (already routed
to S7 by S13). Blast radius: every buff/debuff-modified fight with these powers prints
different numbers in sim and game.

### NC-2 · HIGH · Face prints a flat number, play grants a Spotlight-scaled one — 4 instances → LINT
`prune_witch_hunt`, `charlotte_enduring_frosthelm`, `freminet_pressurized_floe`,
`itto_superlative_superstrength`: in each, the **Block half** of a generated companion
card renders an unscaled literal while OnPlay grants `SpotlightSystem.PrintedBlock`
(1.5× under Guest Cast) — on cards whose *damage* half does scale on the face. Four
instances of one codegen seam = lint candidate **L-N1** (generator check: any
PrintedBlock grant must render a scaled BlockVar). Same-family cousin: SparkPower's
tooltip hardcodes threshold 3 while True Spark Knight lowers the live value.

### NC-3 · HIGH · `burst_energy` rider is meter-gated in sim, Klee-gated in mod (†)
`barbara_melody` (+4) and `sucrose_astable` (+8/12, on an Exhaust card) grant Burst
Energy to any character with a meter in tier0 (`effects.py:925-926`) but route through
`KleeBurstResource.Gain`, which no-ops unless the owner is Klee — a Furina/Kokomi
player gets a card face promising energy the mod never grants. Two instances found
independently; the routing is codegen-level, so every future burst-rider companion
inherits it.

### NC-4 · HIGH · Retired first-design riders still live in tier0 (†)
`masque_red_death`: the sim still adds a flat per-stack damage rider on every Attack
(`effects.py:546-550`) — a leftover of the pre-2026-07-25 draft that the ratified
redesign (sheet and C# both) replaced with the Strength ratchet + Bond of Life. Found
from the companion side and the powers side. The sim over-deals for the rest of any
combat holding Arlecchino.

### NC-5 · HIGH · Navia pays her own play in C#, not in sim (†)
tier0 grants Cannon Fire Support's block strictly *before* `resolve_card` so her own
play can't observe the power (`combat.py:271-290`); C#'s `AfterCardPlayed` fires after
OnPlay applied the power and has no self-exclusion guard — the mod pays 3 (5 upgraded)
block on the play that created the power. Mirror image of NC-1's direction: here the
*mod* is generous.

### NC-6 · HIGH · The Kurage ward diverges on four axes — confirms S1's SYS-2 (†)
Cap (sheet 6, sim honors, C# uncapped Counter), timing (C# pre-block, sim post-block),
trigger scope (sheet/sim: unblocked *attack* damage; C#: any damage), and latch/mill
behavior on fully-blocked hits. S14's powers agent re-derived S1's SYS-2 from the
other side with new line evidence — the family is confirmed, not new; filed here for
the merge.

### NC-7 · HIGH · Frozen is two different mechanics (†)

**DISPOSITION 2026-08-06 — RULED, EACH ENGINE ADOPTS THE OTHER'S HALF (R116).** Verbatim: *"Ticks down per-turn, applies per-creature."* Canonical Frozen is a **duration counter** decrementing at end of enemy side, stacking extends (the mod's semantics — **the sim adopts the timer**), with **per-creature** substitution (the sim's semantics — **the mod adopts per-creature**, so Kaiser Crab's boss-room adds become freezable in game). Not a win for either engine; reading it as one produces the wrong fix. **Shipped-boss-fight impact noted in the batch. Version-stamp question surfaced** — this changes sim combat math wherever Frozen appears. **Errata Batch 2 item 5, both engines.**
Sim: one-shot boolean consumed when the enemy *acts*, idempotent on re-freeze, kept by
a sleeping enemy. Mod: stacking Counter on an unconditional end-of-enemy-side clock —
double-freeze extends, sleepers lose it, post-action freezes are wiped. And the boss
substitution (`FROZEN_BOSS_VULN`) is per-*creature* in sim and the design doc but
per-*room* in C#, so boss-room adds (Kaiser Crab's second claw) are un-freezable in
game. Three findings across two agents; touches a shipped boss fight.

**EXECUTION NOTE 2026-08-06 (Errata Batch 2 item 5) — the SIM half LANDED, the MOD
half is STOPPED and surfaced.** The sim adopted the timer (`Enemy.frozen` is now a
duration counter decremented at the end of the enemy side, stacking extends, Shatter
clears the whole counter). The mod half did not land, because **the game exposes no
per-creature boss fact to key the substitution on**, and choosing one is a design
call the ruling did not make. Verified by reflection over `sts2.dll`: `MonsterModel`
has no boss/rank/tier member; `Creature` has none; `EncounterModel` carries
`RoomType`, `Tags` (a flavour enum: Slimes, Thieves, Knights…), `MonstersWithSlots`
and `SpawnedEnemies`; the only per-creature "secondary enemy" concept in the assembly
is `MinionPower.OwnerIsSecondaryEnemy`, which Kaiser Crab's claws do not carry —
`KaiserCrabBoss` declares both of them as slotted monsters (`_crusherSlot`,
`_rocketSlot`). The sim's `is_boss` is authored per-enemy data (`kaiser_crusher`
`is_boss: true`, `kaiser_rocket` absent, `tier05/content/act2_pool.yaml`) and the mod
has no equivalent. Two readable predicates, and they disagree on the ruling's own
example: **(α) minions only** — a boss-room creature carrying `MinionPower` gets
Frozen, everything else gets Vulnerable; mechanical, uses the game's only per-creature
secondary-enemy concept, and does **not** make Kaiser Crab's second claw freezable,
so it contradicts R116's stated consequence. **(β) a named non-boss roster** — mirror
the sim's own `is_boss` data as a monster-id list; matches R116's example exactly, and
is new authored content data covering every base-game boss room. Surfaced, not chosen.

> **RESOLVED 2026-08-06 (Q13 / R117) — [USER] selects (α), verbatim: *"I'd say
> A"*.** Minions only: a boss-room creature carrying the game's `MinionPower`
> gets Frozen; every other creature gets the Vulnerable substitution. The sim
> predicate aligns to α semantics (parity, not design) and a parity vector is
> added for a boss room with (a) a minion and (b) a non-minion helper — code
> execution is Track V's, inside the v6 window.
>
> **Required annotation, mirrored from R116:** the ruling's stated consequence
> — Kaiser Crab's second claw remaining freezable — is **overridden
> deliberately** by the α selection. Under α the second claw takes Vulnerable,
> not Frozen. This is a chosen reading, not a missed example: chat flagged the
> contradiction to [USER] before the dispatch was drafted, and the α selection
> stands with that consequence stated. No re-litigation.
>
> **EXECUTED 2026-08-06 (Track V, wave 8, v6 window).** Mod: the Frozen case
> in `ReactionEffects.cs` keys the boss-room substitution on the target NOT
> carrying `MinionPower` — minions freeze, everything else takes Vulnerable.
> Sim: `Enemy.is_minion` mirrors the `MinionPower` fact (summon-spawned adds
> carry it, per the gas-bomb/guardbot/parafright/tough-egg dossiers; no
> authored roster enemy does — the claws are slotted monsters), and
> `reactions._react` substitutes on `boss_room and not enemy.is_minion`,
> where boss-room membership reads the full enemy list like the mod's
> `RoomType`. Parity vector family `frozen_boss_room` (a boss-room minion, a
> boss-room non-minion helper, and two non-boss controls) added to
> `docs/noncard-parity-vectors.json` + `NonCardParityVectors.cs`, derived
> from the shipped sim path.

### NC-8 · HIGH · `spend_potion` is never paid — one defect, four filings

**DISPOSITION 2026-08-06 — RULED BY INCLUSION (R116): potions are consumed.** The queue carried "potions are consumed" as the *presumptive* answer awaiting one word; the final dispatch supplies it by listing the fix as **Errata Batch 2 item 2**, and inclusion in a ratified batch is the answer. Recorded as ruled rather than presumptive so nobody re-opens it looking for a quoted sentence. **Sim-only (`tier05/events.py` throwaway-copy fix); not executed by the paper track.**
The event resolver pops the potion from a **throwaway copy** of the bag
(`tier05/events.py:384-385`) and the run layer never copies it back: "The Future of
Potions?" grants its reward free, potion retained. Filed once per potion id by the
potions agents (weak/fear/energy/fairy) — dedupe to a single defect with four
witnesses.

### NC-9 · HIGH · Turn-start broadcast ordering is a divergence *family* (†)
Four independent findings are the same underlying seam — tier0 resolves turn-start
effects at explicit sequential sites, the mod packs them into `AfterPlayerTurnStart`
broadcasts whose intra-broadcast order differs: Standing Ovation's spend-boost is
zeroed in the same broadcast that feeds it; Supporting Cast's first-play draw is
deferred to AfterCardPlayed (sim draws mid-play); Salon upkeep ticks after the hand
draw in C#, before it in sim; The Gallery Stirs' spend-draw can slip a full phase —
**which is S4's F2 (DRAFTER-13 / Gallery Stirs 0.0) territory: the sim-side
`_static_power` trace and this mod-side ordering drift are two halves of one
question.** Treat as one family for any future repair session.

### NC-10 · HIGH · Shop companion slot 1 can never roll a Rare in the mod

**DISPOSITION 2026-08-06 — RULED, BOTH ENGINES DEFECTIVE (R116).** Verbatim: *"Slot 1 should be 'Uncommon or higher from the home region'; slot 2 should be 'any companion card'; this is a defect."* Neither engine implements that spec; both now do — slot 1 filters the home-region pool to **Uncommon+**, slot 2 is **unrestricted**. **One question is surfaced and deliberately NOT chosen:** rarity-odds renormalization within the Uncommon+ pool (condition the existing `SHOP_COMPANION_RARITY_ODDS` on ≥Uncommon vs. a stated split) — a renormalization picked by an implementer is a balance value picked by an implementer. **Cross-noted to the companion-pricing docket: the shop is now a real Rare source in both slots' math.** **Errata Batch 2 item 6, both engines.**
Sim rolls `SHOP_COMPANION_RARITY_ODDS` for both slots (`tier05/shop.py:151-154`); the
mod hard-wires slot 1 (home-nation) to Uncommon. The value the parity lint compares
(0.875) matches, so the lint is green while the *behavior* diverges — the flagship
example of exactly the semantic-parity gap this sweep was chartered to find.

### NC-11 · HIGH · Power-sourced block is funnel-exempt in sim, funneled in mod (†)
Metallicize, the Ceremonial Garment rider, and the Kurage pulse are added raw in tier0
by documented design (`powers.py:75-81`: deliberately exempt from Frail/Dexterity);
C# grants all three as powered move-scoped block — Frail cuts them 25% and Dexterity
inflates them in game only. ~~**Direct consequence for S13's X10 (Metallicize
treadmill): the exploit's numbers are sim-side; in the mod, Frail alone changes the
wall's arithmetic.** The S13 ledger's S7-caveat applies with named evidence now.~~

**DISPOSITION 2026-08-06 — RULED, SIM CANONICAL (R116).** Verbatim: *"I think that the answer is no; my recollection is that power-sourced block in the base game's kits ignores both of those."* The sim's documented funnel exemption (`powers.py:75-81`) is **canonical**; the **mod is the defect side** and stops routing Metallicize, the Ceremonial Garment rider and the Kurage pulse through Frail/Dexterity. **Errata Batch 2 item 4, mod-only.**

**The X10 caveat above is STRUCK, and resolves post-fix.** Once C# stops applying Frail to power-sourced block, the treadmill's **sim-side numbers hold in the mod too** — so the caveat's premise (Frail alone changes the wall's arithmetic in game) no longer describes the shipped engine. Struck, not deleted, per R101b: it was true when written. `X10`'s own disposition (CANDIDATE, explicitly not ratified — R111) is untouched by this.

**The register this pair creates, recorded for future card work:** power-sourced **damage** runs the damage pipeline (`NC-1`); power-sourced **block** is **raw** (`NC-11`). Adjacent, opposite, and both are the base game's own shape.

### NC-12 · HIGH · Cost-override lifetime — confirms S1's SYS-3, and arms S13's X3

**DISPOSITION (adjacent inversion) 2026-08-06 — `AB-s1` APPROVED (Q9 / R118).** Verbatim: *"Yes."* The mod's copy pool excludes kit cards, matching the sheet and the sim: C#'s Encore Performance adopts the sim's exclusion (`effects.py:1231-1232`), and the undiscardable copied kit Burst stops being reachable. Recorded as a **mod behaviour change, not a parity repair**; ships with the next errata batch that touches C# with parity vectors updated — the code change is Track V's. Blast radius: one card's copy pool; no sim number, no test flip expected — if one flips, stop and surface.
Guest-star generation: sheet and C# say "costs 0 *this turn*" (Discovery parity,
`EnergyCost.SetThisTurn`); tier0 writes `pick.cost = 0` permanently on the token
(`effects.py:1205-1206`). Same defect S1 filed as SYS-3, now with the C# leg read.
S13's `copy_dup_5` exploit (permanent free copies) rides exactly this sim-side
behavior — that line moves from "design material" to "parity-defect material."
Adjacent kit-side inversion: sim excludes kit cards from the spotlight-copy pool
(`effects.py:1231-1232`), C#'s Encore Performance does not — a copied kit Burst is
undiscardable in the mod and clogs a hand slot.

### NC-13 · MEDIUM · Event-layer wiring gaps (run layer)
A cluster of "the hook exists, one path forgot it": `book_of_five_rings` counts only
reward/shop card-adds, never event adds; `potion_belt`'s +2 cap is refreshed on every
path except the event potion grant; `centennial_puzzle`'s first-HP-loss trigger is
wired to exactly one HP-loss site; `astrolabe`'s pickup grant leaks a relic into
seeded `grant_relics=False` runs against `model.py`'s own stated invariant;
`regal_pillow` heals on every campfire action, not just Rest. Five distinct defects,
one shape: run-layer hooks wired to a subset of their trigger sites.

### NC-14 · MEDIUM · Declared-but-unreachable content — 4 instances → LINT
`touch_of_orobas_klee` (its hook has no row in the Neow/Ancient valuation table →
valued 0 → never picked), `hand_of_greed` (amount-blind valuation ties to
`golden_pearl`, deterministic tie-break → never picked), Tablet of Truth stage 5
(harvest has five stages, sim ladder terminates at 4), Byrdonis Nest's second option
(absent → a one-option "choice"). Lint candidate **L-N2**: every pool entry's hook
must appear in the valuation table, and every harvest option-count must match the
shipped entry or carry a stated cut.

### NC-15 · MEDIUM · Event resolver semantics vs the real game's rules
The sim's own grammar says HP costs "can kill; that is the real game's rule," but
`available()` hides any lethal option (`events.py:306-310`) — the death branch is
unreachable (2 filings). Positive `max_hp` grants don't heal in events while the
relic layer's identical phrase does (2 filings). `card_reward`/`card_screens` draw
uniformly from the flattened pool, ignoring `C.RARITY_ODDS` — rares at ~16-24%
instead of 5% (3 filings → lint candidate **L-N3**: one reward-screen constructor,
not per-site sampling). Plus per-event fidelity drift: Room Full of Cheese (pool
rarity + duplicates + named relic), Slippery Bridge (the Hold On loop is absent; the
Basic-rarity filter is absent), The Future of Potions (the entire potion-rarity→
reward mapping is dropped). One S2 cross-check landed here: the shipped gallery text
for Brain Leech promises **two** cards; the option grants a pick-1-of-3 screen —
S2's lore is out ahead of the mechanics on that event.

### NC-16 · MEDIUM · Bare-literal mirrors the parity lint cannot see — 3 instances → LINT
`WEAK_DEALT_MULT` lives in C# only as the literal `0.75m` (twice, in the method whose
sibling constant *is* mirrored); `FANFARE_CAP_FRACTION` exists as `MaxHp / 2`. The
lint's `CONST_RE` only matches declared consts, so these can retune sim-side and
drift silently — in neither MIRRORED nor UNMIRRORED, which the lint's own discipline
says must not happen. Lint candidate **L-N4**. The fanfare fraction also drifts
semantically: sim computes the cap once from *printed* HP; the mod recomputes live
from current MaxHp — any max-HP gain moves the mod's ceiling only (3 filings, 2
agents †).

### NC-17 · MEDIUM · Potion economy paper-vs-practice
The rarity ladder inverts in practice: "uncommon" potions roll 15% each, strictly
more often than "common frequent" ones at 10.83% (tier-then-uniform with a 2-id
uncommon tier; 3 filings, dedupe to one defect). `swift_potion` and `energy_potion`
are in DRINKABLE but no policy branch ever drinks them — dead cargo in a 3-slot bag.
`fire_potion`'s kill-securing gate reads raw HP and ignores Block, failing in exactly
the case it exists for. `strength_potion` on Kokomi converts wholly to Charge (the
casket chokepoint) while both spec surfaces still say "+2 Strength." The understudy
wire aims `fear_potion` with a different helper than the sim's policy used (S7-adjacent:
that one is an *apparatus* divergence, route it to the S7 ledger).

### NC-18 · MEDIUM · Bomb corpse rules + a wrong decision record
C#'s early-detonation listener has no death guard; the sim explicitly refuses to
detonate on a corpse — and `klee-mod/DECISIONS.md:1629-1634` states the sim's
behavior *backwards*, inverting the stakes of the only open bomb parity test. The
record being wrong is itself the finding — flagged for [USER] since ledger text is
his to amend (S4 precedent: the audit amends nothing). Cosmetic sibling: the bomb
badge shows the raw charge sum, excluding BombDamageUp.

### NC-19 · MEDIUM · Measurement gaps (sim cannot express a shipped upgrade)
Kokomi's upgraded starter doubles per-exhaust Charge/Burst accrual in C#; tier0's
exhaust funnel hardcodes base constants and exposes no accrual hook — every simulated
Kokomi run measures the un-upgraded rate. Not a divergence in shipped behavior, a
blind instrument: the sim cannot see a thing the game does.

### NC-20 · LOW cluster
63 low findings: comment drift, stale sheet notes (the companion header still naming
an empty UNAPPLIABLE set — 2 filings †), icon fall-throughs (twelve PowerModel
classes render the base-game placeholder and trip R13 every boot), tooltip literals,
and doc-vs-code wording. All in the ledger with citations; none individually
[USER]-urgent.

## Lint candidates (≥3 instances, per the S1 rule)

| id | rule | instances |
|---|---|---|
| L-N1 | generated card: any Spotlight-scaled grant must render a scaled face var | 4 (NC-2) |
| L-N2 | every pool hook has a valuation row; every harvest option-count matches shipped or carries a stated cut | 4 (NC-14) |
| L-N3 | event card rewards route through one RARITY_ODDS-honoring constructor | 3 (NC-15) |
| L-N4 | mirrored-constant lint extended to literals: known sim constants may not appear as bare numerics in mod power/resource code | 3 (NC-16) |

## Cross-ledger routing

- **To S7 (sim-fidelity ledger), joining S13's five:** NC-1 (raw-hit pipeline skip),
  NC-11 (block funnel classification), NC-12 (cost_override lifetime — tier0 likely
  the drifting leg, as S1 already judged), NC-17's understudy fear_potion aim.
- **To the S4/ledger-repair queue (gated on [USER]'s S4 sitting, not started):**
  NC-9's Gallery Stirs half (S4 F2), NC-18's backwards DECISIONS.md entry.
- **S13 exploit-ledger annotations:** X3/`copy_dup_5` (enabler is NC-12), X10
  (numbers change under NC-11 in-game).
- **S2 gallery:** Brain Leech variant text vs shipped option count (NC-15).

## Coverage statement

173/173 entities verdicted (75 CLEAN — 43%), zero agents lost, all 174 findings
passed the mechanical citation audit. CLEAN is load-bearing: the 25 C# power files,
42 relics, 9 potions, 24 events, 51 companions, and 22 constant groups now each have
a named, evidenced parity status. S14's Fable touchpoint (this memo) is the batch's
second and last — S13 triage was the first.
