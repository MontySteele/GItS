# Sprint Log — Shop Companion Channel (§4.7 build-out)

> **Lifecycle: ARCHIVED** — superseded; kept verbatim as a record and never updated. Status index: `docs/registry/identifiers.md` §15.

> # ARCHIVE BANNER — the shop-channel numbers here are pre-CONSTANTS-6
>
> **Appended 2026-08-06 (Track V, wave 8). `CONSTANTS_VERSION` 5 → 6 was
> approved by [USER] on 2026-08-06 (Q14 / R117, verbatim *"14) Yes"*), and
> the v6 batch's shop half is `NC-10` (R116, Errata Batch 2, both engines):
> slot 1 became "Uncommon or higher from the home region", slot 2 became
> "any companion card", and Q16's CONDITION reading (R118, verbatim
> *"Condition."*) fixed `SHOP_COMPANION_RARITY_ODDS` as the reward odds
> renormalized over ≥Uncommon — a conditioning change, no new values.**
> The tier-0.5 shop maths this document measured predate that spec in both
> engines, so **every measured shop-channel number here is archive and is
> NOT comparable to output taken under 6.** Quote these numbers only with
> the pre-v6 label attached. Nothing above or below is rewritten (R101b);
> the v6 re-baseline sweep is Track M's, after the v6 code lands. Source of
> the bump: `tier0/constants.py`, the `CONSTANTS_VERSION 6` note.
>
> **SWEEP LANDED 2026-08-06 (Track M, wave 8):** the §4.7 channel cell was
> re-run under v6, paired v5↔v6
> (`docs/v6-rebaseline-sweep-2026-08-06.md` §3): unmoved at the
> instrument's resolution; the P1/P2 out-of-band findings reproduce.

**Executed 2026-07-25.** Plan of record:
`docs/shop-companion-channel-sprint.md` (PRE-REGISTERED, rulings R59–R62).
Decision record it superseded: `docs/shop-companion-channel-plan.md`.

Gate at close: **suite 799 passed**, C# **0 errors**, upgrade lint 253
draftable, ancient lint OK, companion-shop lint OK, constant parity
**71 mirrored / 13 declared unmirrored**.

---

## 1. What shipped

| Track | Status | Where |
|---|---|---|
| A — companion pool surface | **Shipped, not as specified.** See §2. | `klee-mod/KleeCode/CompanionPool.cs` |
| B — merchant override | Shipped | `klee-mod/KleeCode/Patches/MerchantCompanionSlots.cs` |
| C — sim channel | Shipped + measured | `tier05/shop.py`, `tier05/exp_shop_companion_channel.py` |
| D — invariants | Shipped | `tier05/tests/test_shop_companion_channel.py`, `tools/lint_companion_shop_coverage.py` |
| E — R62 | Shipped | `docs/mondstadt-companions.yaml`, codegen |

Rulings R59–R62 are in `tier0/DECISIONS.md`. No collision (R58 was latest).

## 2. Track A did not land as written — and the reason inverted twice

The plan sized Track A as "build the companion pool class with
`IsColorless => true`", size L, the prerequisite for B and C.

**First, the repo said it was impossible.** `KleeOffPoolCards.cs` carries a
signed finding that a standalone pool "could never work": `ModelDb.AllCardPools`
is one pool per character concatenated with a **hardcoded** array of seven
shared pools, with no registration hook. A pool that is nobody's character
pool is invisible to `CardModel.Pool`, and an unresolvable Pool crashes on
card *draw* with the engine's "You monster!" placeholder.

**Then the decompile said otherwise.** BaseLib now ships
`ModelDbSharedCardPoolsPatch` — a Harmony postfix on the shared-pools getter
that appends any `CustomCardPoolModel` declaring `IsShared`, registered from
its own constructor. The hardcoded array is still hardcoded; BaseLib grew the
hook around it. **The repo's own finding was stale, and I came within one
commit of asserting it back.** It is now corrected in place, because the next
person to read it would have drawn the same wrong conclusion.

**Built anyway? No — on cost, not feasibility.** A registered pool means
migrating all 47 companion models *out* of the three character pools, because
`CardModel.Pool` must resolve to exactly one pool and Pool supplies the card
frame, energy icon and deck-entry colour. So it is:

- a **visual change to every companion card**, with a live parallel animation
  stream;
- a change to the shared loader surface all three character workstreams sit on
  (the plan itself requires a cross-session note before it lands);
- dependent on our pool being constructed before the first
  `ModelDb.AllCardPools` read — that property caches, `AllSharedCardPools`
  does not — which **no C# test can check**, because there is no C# test
  project.

Nothing in the sprint needs the object: `MerchantCardEntry` takes a plain
`IEnumerable<CardModel>`, so the shop reads a query surface directly. Track A
therefore shipped as `CompanionPool` — nation/rarity/personal-pool filtering
over the one roster — and the migration is a **de-risked follow-up**, not a
prerequisite. **[USER] call at close-out.**

Track A's acceptance gate (reward-slot offers byte-identical) holds by
construction rather than by measurement: `CompanionSlot.Roll` does not route
through the new class. It delegates two identity lookups (`CharacterId`,
`HomeNation`) that are pure switches over `Player.Character` and consume no
rng. No cross-session note was needed because the shared loader surface was
never touched.

## 3. Track B — what the decompile changed

`MerchantCardEntry.GetCost` **does** price off rarity (50 / 75 / 150), which
was the plan's "verify before reuse" item. It also multiplies by **1.15 when
`card.Pool is ColorlessCardPool`** — a type check on the concrete pool class.

**Consequence, recorded not fixed:** companions resolve `Pool` to their
character's pool, so they never collect the colorless surcharge. That matches
§4.7 as written ("base shop-card gold bands by drawn rarity"), but it means
the mod's premium channel is ~15% cheaper than the base channel it replaces —
in a section whose thesis is that pricing is the balance governor. The sim
mirrors the same bands, so the two sides agree. **Flagged for [USER].**

Two sanctioned hooks (`Hook.ModifyMerchantCardPool`,
`Hook.ModifyMerchantCardRarity`) would have avoided Harmony entirely and were
**rejected on discrimination, not taste**: both also fire for the five
character-card entries, the pool hook fires before the rarity hook so it
cannot know which colorless slot it is serving, and neither is told which
entry is being populated. Slot 1 differs from slot 2 only by the nation
filter, so a surface that cannot tell the slots apart cannot implement §4.7.

Banner gating was **not** wired. `BANNER_FEATURED_SLOTS` is 3 and no nation
designs more than 3 Rare companions, so the Featured Banner currently features
every 5-star everywhere and is exactly a no-op — the same standing ruling the
reward slot already operates under. Wiring it into the shop alone would make
the two channels disagree about a rule neither can exercise.

## 4. Track C — the measurement

500 runs/arm, seed 20260725, realistic (relics + potions), 3 acts. One
variable: the channel.

| character | arm off | arm on | delta |
|---|---|---|---|
| klee / demolition | 5.2% | 6.4% | +1.20pp |
| furina / salon | 20.6% | 18.8% | −1.80pp |
| kokomi / priest | 7.8% | 7.8% | +0.00pp |

### Prediction grading (Claude's read; [USER] countersigns per §5.4)

**P1 — slot-1 buy rate 10–35%. OUT OF BAND: 49.2%** (1755 of 3569 visits).

**P2 — positive but ≤ +2.0pp. OUT OF BAND, and the honest read is a NULL,**
not a negative. Mean −0.20pp; the three characters split +1.2 / −1.8 / 0.0 and
every Wilson interval overlaps its own control. The channel did not move
winrate in either direction.

**P3 — slot-2 mix ≥60% Uncommon. IN BAND: 91.7%** of 648 slot-2 purchases.
Diagnostic only (R14). Offered mix was 3127 uncommon / 442 rare, so the
realized mix is close to the offered mix — gold pressure is *not* visibly
biasing the choice, which is itself the P1 story below.

### Why P1 is out of band is NOT what the band assumed

The band's stated diagnosis for >35% is "under-priced relative to
card-remove/relic competition for gold". A crowd-out check across the same
arms says otherwise:

| door | channel off | channel on | change |
|---|---|---|---|
| removals bought | 0 | 0 | — |
| relics bought | 1356 | 958 | **−29.4%** |
| gold unspent at run end | 332277 | 334174 | +0.6% |

Three things follow, and they matter more than the buy rate:

1. **Card removal is not a competitor at all.** Zero removals in either arm,
   because `is_known_dead` fires only on curses and unupgradable basic filler,
   and all three characters ship clean decks. Half of P1's premise does not
   exist in tier 0.5.
2. **The channel crowds out relics, ~30% of them** — and winrate does not
   move. The drafter is trading a relic for a companion at par. That is a real
   finding about companion value, not about price.
3. **Gold was never the constraint.** Unspent gold is unchanged (+0.6%);
   runs end holding ~220 gold. **A price cannot govern a purse that is not
   binding.** §4.7's central claim — "pricing is the balance governor" — is
   not currently true in the sim at these gold levels. The governor is the
   *shelf*, not the price.

There is also a structural confound worth stating plainly: `visit_shop` buys
cards **before** removal, and `model.py` offers the relic later still. So
companions get first claim on the purse by construction. A high buy rate is
partly an artifact of that ordering, which is why the crowd-out table — not
the buy rate — is the load-bearing evidence here.

**No knob was turned.** The plan's retune order is gold bands first, and
findings 1–3 say a gold-band change would be aimed at the wrong thing. This
goes to [USER] as a design question — *should the shop's purse ever bind?* —
rather than as a tuning pass.

## 5. Track D — and a gate that was not watching

The companion coverage lint (`tools/lint_companion_shop_coverage.py`) is
instance **two** of the empty-draw class, after Dusty Tome. It checks the
sheets (can the roster fill both slots at every rarity the ladder can request)
and the C# source (are all three fallback rungs still there — a source
tripwire, because there is no C# test project). It is wired into the suite,
not left as a tool.

Live roster note it prints on every run: **Fontaine designs zero Rare
companions**, so Furina's home-region slot 1 widens the nation whenever it
rolls a Rare. That is exactly the brittleness R59 cites when it rejects a
guaranteed-Rare slot 2 — the ruling's hypothetical is already live.

**Separately, and not in the plan:** adding one C# constant surfaced that
`lint_constant_parity.py` only ever read `public const int`. Eight
non-integer balance constants were escaping the gate whose docstring promises
that "every balance number in the mod lives twice" — including **VaporizeMult
(1.5), MeltMult (1.75), AmpStackLimit (4.0), FrozenDamageMult (0.5),
FanfareDecayFraction (0.20), SalonDryDamageMultiplier (0.75) and
GuestCastBaseMultiplier (1.5)**. Those are headline tuning numbers; a sim-side
retune of any of them would have drifted in silence, which is the precise
failure the file exists to prevent.

The lint now reads `int`, `float`, `double` and `decimal`, and `private` as
well as `public` — visibility is a C# concern, a balance number is a balance
number. Coverage went **58 → 71 mirrored, 3 → 13 declared unmirrored**, and
**every newly-watched value already matched**. No drift had happened yet. The
gate simply was not looking.

## 6. Three tests were repaired, none of them for a real defect

The channel's extra rng draws renumber runs, which broke three tests that were
asserting through proxies rather than at their subject:

- `test_randomized_starter_uses_a_dedicated_replayable_stream` asserted ≥2
  companions in the **final** deck on the theory that "starters never vanish".
  They can: `events.py` removes cards, and a removal event ate
  `prune_witch_hunt`. Now reads the starter deck directly.
- `test_pity_slot_fires_after_k_companionless_screens` needed three reward
  screens and pinned one seed; the renumbered run died after two. Now scans
  seeds for a run that survives three.
- `test_neow_booming_conch_...` used a `_no_grants` helper that closed the
  reward door but left the **shop** relic door open, with a comment saying so.
  A shop relic started injecting `combat_start_energy`. The helper now closes
  both — the isolation it always claimed.

## 7. Open, and owned by [USER]

1. **Close-out ratification** of the sprint (plan §5.1).
2. **P1–P3 grading countersign** (plan §5.4) — especially §4 above, which
   argues the out-of-band P1 is not a pricing fault and that no knob should
   move yet.
3. **Does the shop's purse ever bind?** Runs end with ~220 unspent gold. This
   is upstream of §4.7 and decides whether "pricing is the balance governor"
   can be true at all.
4. **The colorless 1.15× surcharge** companions do not collect (§3).
5. **Track A's pool migration** — now known to be feasible; the question is
   whether a visual change to every companion card is wanted (§2).
6. **R60 phase 2 fantasy-leak grading**, after table time with phase 1.
7. **Track D fallback taste check**: an unfillable slot falls through to one
   base colorless card in the mod, and is omitted in the sim (the sim has no
   base pool to fall back on). Unreachable on today's roster.
