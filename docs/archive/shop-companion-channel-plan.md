# Sprint Design Pass — the Shop Companion Channel (§4.7)

**Status: SUPERSEDED 2026-07-25 — retained as the DECISION RECORD, not a build
input.** D1/D2/D3 below were answered as R59/R60/R61 (`tier0/DECISIONS.md`);
the sprint that executed them is `docs/shop-companion-channel-sprint.md` and
its outcome is `docs/shop-companion-channel-sprint-log.md`.

Two things in this document were **wrong** and the log explains both: §2's
claim that a companion pool class cannot be registered (BaseLib grew the hook
since), and §3's D1 framing that slot 2's floor was the only open question
(the shop's *purse never binds*, so the price floor governs less than either
document assumed). Read §2's table as the state of the tree on 2026-07-26.

Original header follows.

**Status: DRAFT FOR RED-PEN. Nothing here is ratified and nothing is built.**
Opened 2026-07-26, out of the feasibility pass on
`claude/genshin-sts2-design-lqstz1` (merged as specification only).

Governing spec: `docs/teyvat-spire-design-principles.md` §4.7 (v1.11/v1.11a),
now on main with an UNBUILT banner. Empirical backing:
`docs/companion-value-vs-colorless-study.md`.

This document exists to be argued with. It carries **three decisions the spec
does not settle**, and building before they are settled would bake in a guess.

---

## 1. What §4.7 asks for

1. The companion pool **replaces** the base-game colorless pool wholesale.
2. The shop gets **two companion slots**, replacing base's two colorless slots:
   - **Slot 1** — home-nation draw, **Uncommon floor**. The targeted "buy your
     dream support" slot.
   - **Slot 2** — wildcard, any nation, at card-reward rarity odds.
3. **Gold price is the balance governor**, not a stat nerf — which is what lets
   the paid channel roll payoff-grade 5-stars without breaching §4.3.

The free reward slot (§4.1) is unchanged in all of this.

## 2. What is actually true today

| Claim in the spec | Reality |
|---|---|
| Companions are a colorless `CustomCardPoolModel` (§4.1) | **False.** No companion pool class exists. `KleeCardPool`, `FurinaCardPool`, `KokomiCardPool` all declare `IsColorless => false`. `CompanionSlot.Roll` builds offers ad hoc and injects them via `TryModifyCardRewardOptions`. |
| The shop has two colorless slots to replace | **True.** `MerchantInventory._colorlessCardRarities = [Uncommon, Rare]`, filled by `PopulateColorlessCardEntries()` from `ModelDb.CardPool<ColorlessCardPool>()`. |
| We can patch the merchant | **True, with precedent.** `CardFactory_CreateForMerchant_TypeFallback_Patch` already Harmony-patches merchant card creation. |
| The sim models a shop | **Partly.** `tier05/shop.py` exists, but `shop_offer` reuses `rewards.character_pool`, which is *ownership-required and companion-free* by construction. |

**The load-bearing gap: there is no companion pool.** Everything in §4.7 is
written on top of an abstraction that was never built. That is the first work
item and it is not small.

## 3. THE THREE DECISIONS ([USER])

### D1 — Slot 2's rarity floor

Base slot 2 is a **guaranteed Rare**. §4.7 makes it a wildcard at card-reward
odds, which is ~60% Common.

**That makes the shop's second colorless slot worse than the base game's**, in
direct tension with §4.7's own thesis that the shop is the premium channel
"where StS colorless is conventionally strongest *because you paid gold for
it*." The branch's own study §7 pushes the same way: StS2 colorless has **no
common tier at all**, so a wildcard at reward odds would put a rarity in that
slot the base game never does.

- **(a) Uncommon floor** — wildcard nation, Uncommon-or-Rare. Preserves "you
  never know what's on offer" while keeping the slot premium. *Recommended.*
- **(b) Keep base's guaranteed Rare** — maximum premium, least surprise, and
  the strictest read of "replace base's two slots".
- **(c) As written** — full reward odds. Cheapest to implement, and the option
  that contradicts the section's own framing.

### D2 — Remove the base colorless pool, or override only the shop?

`ColorlessCardPool` has **seven consumers** in the decompile, not one: card
creation options, a concat path, a from-hand colorless filter, and **three
`GetDistinctForCombat(pool, N, rng)` sites**. Requesting N distinct cards from
an emptied pool is exactly the empty-draw class that softlocked Dusty Tome and
that `tools/lint_ancient_coverage.py` was written to prevent.

- **(a) Shop-only override** — patch `PopulateColorlessCardEntries` to draw
  from the companion pool; leave `ColorlessCardPool` populated for the
  in-combat generation sites. Gets the headline intent (the shop carries
  companions) with a fraction of the blast radius. §4.7 rejects the "additive
  model", but that rejection argues *fantasy dilution in the reward economy* —
  which does not obviously extend to a Discovery-style in-combat effect the
  player never drafts from. *Recommended as phase 1.*
- **(b) Full removal** — replace the pool's contents everywhere. Matches the
  spec exactly. Requires auditing all seven consumers and a curated invariant
  test per site. Materially larger, with a crash class at the end of it.
- **(c) Full removal, phased** — (a) first, then (b) once the companion pool
  is proven in the shop.

### D3 — Does the sim model this at all?

tier 0.5's shop is companion-free by construction. Options:

- **(a) Model it** — companions become shoppable in `tier05/shop.py`, so the
  channel's value shows up in winrates and the drafter can price it.
- **(b) Recorded divergence** — ship the channel unmeasured, as R2's Furina
  relic already is.

Worth noting the pattern: **R2 already ships unmeasured, and Orobas is only
modelled for Klee.** A third unmeasured channel starts to compound — at some
point "the sim does not model relics or shops" stops being a series of local
exemptions and becomes a statement about what tier 0.5 is for. That is worth a
deliberate answer rather than a third exemption.

## 4. Work breakdown (once D1–D3 are settled)

| # | Item | Size | Notes |
|---|---|---|---|
| 1 | **Companion `CardPoolModel`** with `IsColorless => true` | **L** | The prerequisite. Must not disturb the existing reward-slot path, which does not go through a pool today. |
| 2 | Merchant slot override | M | Harmony on `PopulateColorlessCardEntries`; precedent exists. Slot 1 needs nation filtering + rarity floor. |
| 3 | Pricing | S | Spec says base shop-card gold bands by drawn rarity — i.e. reuse, not invent. Verify `MerchantCardEntry` prices off rarity before assuming. |
| 4 | Banner gating for 5-stars in slot 1 | S | §4.2 already defines the rule; this is wiring. |
| 5 | Base-pool disposition | S or **L** | Entirely D2's answer. |
| 6 | Sim channel | M | Entirely D3's answer. |
| 7 | Invariant tests | M | The house pattern: a curated list plus a check per empty-draw site touched. |

## 5. Ride-alongs found during the feasibility pass

- **`sucrose_astable` lost a guard.** The branch proposed 0-cost **+ Exhaust**;
  main's later rebalance took 2 → 1 cost **without** Exhaust, and main wins on
  recency. But the Exhaust was not only a cost fix — it capped `burst_energy`
  from becoming a repeatable, multi-copy Burst battery for Klee and Furina
  (§2.4 meter tuning, §4.3 enabler-not-carry). **That guard is currently absent
  rather than rejected.** Red-pen should decide explicitly.
- **`sucrose_catalyst_conversion` is live but unreachable as designed.** The
  card merged and is draftable from the free reward slot; §4.7's claim that it
  is "reliably shoppable at shop slot-1" is false until this sprint lands.
- **The energy-gap finding stands on its own.** The corrected framing —
  *the shared pool must let any character, present or future, draft a
  gap-patch, so "a current character self-provides" is the wrong test* — is
  the most reusable idea on that branch and applies well beyond energy.

## 6. Explicit non-goals

- The Wish banner (§4.6). Still deferred.
- Card-removal shop *service* — unaffected; it is not a colorless card.
- Re-opening §4.3 enabler-not-carry. §4.7's whole resolution is that channel
  and pricing carry the balance, precisely so card numbers do not have to.
- Any change to the free reward slot.
