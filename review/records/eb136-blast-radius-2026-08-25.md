Status: RECORD

# EB-136 — same-target binding: blast-radius audit

**Date:** 2026-08-25 · **Branch:** `eb136-audit-2026-08-25` · **Base:** `113876c`
**Ruling in force:** R208 ([USER] 2026-08-25) — a card's `target: enemy` ops
resolve against ONE target for the whole card, adopting C#'s `cardPlay.Target`
semantics; destination *scoring* is severed as a later policy question.

**OUTCOME: the implementation is STOPPED at the audit gate.** (b) is
decompile-settled. (c) is **not** pure parity, and (d) is **not** a clean
single declared window, on the ground recorded in §4 and §5. Three questions go
to [USER] in §6.

---

## 1. What the audit was gated on

The repair was authorised to land only if all three held:

- **(b)** C#'s dead-target semantics for an aimed op are established from the
  decompile, not guessed.
- **(c)** the repair is pure engine parity with zero policy-shaped choices —
  "make the existing lowest-HP pick once per card, hold it for every
  `target: enemy` op, reproduce C#'s dead-target behaviour exactly".
- **(d)** the published numbers that move are bounded by the affected-card
  enumeration into one clean declared window.

(b) holds. (c) and (d) do not.

---

## 2. The blast radius (part (a))

Enumerated mechanically over every committed sheet plus the `game_ref/` canon
extractions read read-only from the primary checkout — 633 card rows across
`docs/*-cards.yaml`, `docs/*-companions.yaml`, `tier0/content/cards/*.yaml`,
and the `game_ref/` pools the loader actually reads (`ironclad_pool.yaml`,
`silent_pool.yaml` and their pass overlays, `tier0/content/loader.py:45-64`).

A pair counts only if both ops can **co-resolve**: an op in a `then` arm and an
op in the matching `else` arm never both fire, and `modes` arms are likewise
exclusive. `ic_dismantle` and `ic_spite` drop out on exactly that test — their
two damage rows are the two arms of one conditional.

### 2.1 The row's NARROW op list — `damage` / `detonate` / `move_bombs` — 6 cards

| card | sheet | ops | changes outcome when… |
|---|---|---|---|
| `sparkly_explosion` | klee | `move_bombs` + `detonate bonus:3` + `damage 14` | the detonation kills the aim → the 14 fizzles instead of hitting the next enemy |
| `sizzle` | klee | `damage 8` + `damage 6` under `target_has_nonpyro_aura` | the 8 kills → the 6 fizzles (today it lands on the next-lowest) |
| `tail_of_flame` | klee | `damage 5` + `damage 4` under `this_cost_zero` | the 5 kills → the 4 fizzles |
| `matinee_performance` | furina | `damage 5` + `damage 2 times: salon_members` | the 5 kills → **all** the 2s fizzle; today they spread across survivors |
| `flood_of_emotion` | furina | `damage 14` + `damage 14` under `fanfare_at_least_20` | the first 14 kills → the second fizzles |
| `read_the_current` | kokomi | `damage 7` + `damage 6` under `charge_at_least_10` | the 7 kills → the 6 fizzles |

**Even the narrow reading moves all three roster characters, not Klee alone.**

### 2.2 The ruled SCOPE sentence — every `target: enemy` op — 28 distinct live cards

Adding the rest of the generator's `AIMING_OPS` (`place_bomb`, `apply_aura`,
`swirl`) plus `apply_power` on an enemy-landing power
(`gen_klee_cards.py:1070-1086`, `_aims_at_chosen_enemy`):

| sheet | cards |
|---|---|
| klee | + `fish_flavored_bait` (`damage 5` + `place_bomb`), `trip_wire` (`place_bomb` + `weak 1`) |
| furina | + `usher_the_waves` (`damage 5` + `weak 1`) |
| kokomi | + `exposing_current` (`damage 8` + `vulnerable 2`) |
| inazuma-companions | `sayu_yoohoo_windwheel` (`damage 4` + `swirl`), `raiden_musou_no_hitotachi` (`damage 40` + `vulnerable 2`) |
| colorless_event | `squash` (`damage 10` + `vulnerable 2`) |
| **`ironclad_starter.yaml`** | **`bash` (`damage 8` + `vulnerable 2`)** |
| `silent.yaml` | `neutralize_like` (`damage 3` + `weak 1`) |
| `game_ref/ironclad_pool.yaml` | `ic_bash`, `ic_break`, `ic_fight_me`, `ic_mangle`, `ic_molten_fist`, `ic_uppercut` |
| `game_ref/silent_pool.yaml` | `si_assassinate`, `si_malaise`, `si_neutralize`, `si_poisoned_stab`, `si_strangle`, `si_sucker_punch`, `si_suppress` |

`bash` is in **`ref_ironclad`'s starter deck** (`tier0/content/characters/ref_ironclad.yaml:16`).
`("ref_ironclad", "starter")` under the `generic` pilot is the scoring anchor
normalised so every axis reads exactly `3.0`. The wide reading therefore
changes the **anchor's combat behaviour**, and the `real_ironclad` /
`real_silent` pools it also touches are the two floor rows STATE.md's standing
baseline §8 addendum publishes.

### 2.3 The same defect INSIDE one op — multi-hit — 7 more live cards

`_op_damage` re-picks per hit (`for _ in range(times): for enemy in
_pick_targets(...)`, `effects.py:904`); `_op_apply_power` does the same
(`:1212`). C# holds `_singleTarget` across hits and **breaks** when it dies
(§3.1). Live rows: `matinee_performance` (furina), `ic_twin_strike`,
`ic_fight_me`, `ic_dismantle`, `ic_fiend_fire`, `ic_spite` (real_ironclad),
`si_skewer` (real_silent). **The row's next-action does not mention this case
at all.**

### 2.4 When the divergence actually bites

Damage to the lowest-HP enemy keeps that enemy lowest, so **without a kill the
per-op re-pick is a no-op** — which is why the divergence is essentially
kill-gated, plus the board-reshuffle cases where an AoE, a swirl or a reaction
damages a *different* enemy mid-card. The fully-blocked board changes nothing
in tier0 (a blocked hit does not kill, so the aim is stable); it matters only
through the bomb early-detonation guard. The empty board is already pinned.

---

## 3. The decompile (part (b)) — SETTLED, and the answer is NOT uniform

Decompiled from the pinned `sts2.dll` v0.107.1 with `ilspycmd` 8.2.0.7535.

### 3.1 Aimed DAMAGE against a dead target — **FIZZLES**

`AttackCommand.GetPossibleTargets()` returns a **one-element list** for a
single-target attack:

```csharp
private IReadOnlyList<Creature> GetPossibleTargets()
{
    if (IsSingleTargeted) return new <>z__ReadOnlySingleElementList<Creature>(_singleTarget);
    ...
}
```

and `AttackCommand.Execute` filters it by `IsAlive` **on every hit**:

```csharp
for (int i = 0; (decimal)i < attackCount; i++)
{
    if (Attacker.IsDead) break;
    List<Creature> validTargets = (from c in GetPossibleTargets() where c.IsAlive select c).ToList();
    if (validTargets.Count == 0 && combatState.IsLiveCombat()) break;
    ...
    singleTarget = ((validTargets.Count != 1) ? null : validTargets[0]);
```

`CombatState.IsLiveCombat()` returns literally `true` (already established at
W2b), so the `break` is unconditional. A dead aim yields an empty
`validTargets` → the hit loop ends. **No retarget, no corpse hit, no throw.**
Double-guarded downstream: `CreatureCmd.Damage` runs `if
(originalTarget2.IsDead) continue;` (`CreatureCmd.cs:256`). There is no
retarget-on-death path anywhere in `AttackCommand`.

This is also what settles §2.3: hits 2..N of a `.Targeting(x).WithHitCount(n)`
attack re-check the **same** `_singleTarget` and break when it dies.

### 3.2 Aimed `apply_power` against a dead target — **LANDS ON THE CORPSE**

`PowerCmd.Apply` guards on `CanReceivePowers` only — and `Creature`'s own
first-party doc comment is explicit:

```csharp
/// Can this creature have powers applied to it?
/// ... It's also different from hittable; a creature is not hittable if it's
/// dead, but dead creatures can still have powers applied to them.
public bool CanReceivePowers
{
    get
    {
        if (CombatState == null) return false;
        if (!Hook.ShouldAllowHitting(CombatState, this)) return false;
        return true;
    }
}
```

Compare `IsHittable`, three lines above, which *does* open with `if (IsDead)
return false;`. The omission in `CanReceivePowers` is deliberate and
documented.

**So C#'s dead-target rule is op-dependent: damage fizzles, powers stick to the
corpse.** That is reproducible as parity, but it is not one rule.

### 3.3 `cardPlay.Target` is bound once, and the AUTOPLAY pick is settled too

`CardPlay.Target` is `public required Creature? Target { get; init; }` —
immutable once the play is constructed. On an autoplay, `CardCmd.AutoPlay`
picks it **once**, before resolution:

```csharp
if (card2.TargetType == TargetType.AnyEnemy)
{
    if (target == null)
        target = card2.Owner.RunState.Rng.CombatTargets.NextItem(combatState.HittableEnemies);
    if (target == null) { await MoveToResultPileWithoutPlaying(choiceContext, card2); return; }
}
...
await card2.OnPlayWrapper(choiceContext, target, isAutoPlay: true, resources, skipCardPileVisuals);
```

This settles two things. The binding moment is **card-play construction, before
any op resolves** — so a bound aim is picked pre-AoE, not lazily at the first
aimed op. And tier0's `force_random_targeting` path should roll **once per
card**, not once per op, which it currently does not (`_pick_targets`,
`effects.py:360-365`).

For a *manual* play, `cardPlay.Target` is the human's mouse pick; there is no
engine rule to mirror, which is exactly why R208 preserves tier0's lowest-HP
aim as the documented identity choice. **The initial-aim story is therefore
clean:** make the existing pick once, hold it. That half of (c) is fine.

### 3.4 The mod-authored ops have no engine law to reproduce

`detonate`, `move_bombs`, `place_bomb`, `apply_aura` and `swirl` are **our own
C# in `klee-mod/KleeCode`**, not engine ops. `BombPower.DetonateOn` reads
`target.Powers.OfType<BombPower>()` with **no aliveness test**;
`BombPower.MoveAllTo` applies to `dest` through `PowerCmd.Apply`, which per
§3.2 accepts a corpse. Their dead-target behaviour is whatever falls out — it
was never ruled. It is *recorded* in one place only, as an instrument:
`BombPower`'s EB-18 corpse-detonation counter, which "REPORTS, NEVER GRADES".

So "reproduce C#'s dead-target behaviour exactly" has an engine answer for
`damage` and `apply_power`, and for the other five ops it means *reproduce our
own unreviewed mod behaviour in the sim* — which is a ruling about what those
ops should do, not a parity read.

---

## 4. Classification (part (c)) — NOT pure parity

Three places where tier0 must **choose**, each moving a different set of
published numbers.

**C1 — which ops bind.** The row's scope sentence says "a card's `target:
enemy` ops"; the row's next-action names exactly three
(`_op_move_bombs`, `_op_detonate`, "the card's damage line"). Narrow = 6 cards,
no anchors. Wide = 28 cards **including the scoring anchor's `bash` and both
`real_*` floor pools**. Choosing narrow leaves `bash`, `usher_the_waves`,
`exposing_current`, `trip_wire`, `fish_flavored_bait` and thirteen `ic_*`/`si_*`
rows scattering on exactly the defect the row closes — the row would close with
half its own scope sentence still live. Choosing narrow *because* it avoids
moving the anchor is a measurement-convenience choice, which is policy by
definition.

**C2 — whether intra-op `times` binds.** §2.3. Not in the ruled next-action.
C# is settled (later hits fizzle), so the parity answer is known; whether it
rides this repair or a later one is a window-shape choice, and it is the half
that reaches `real_ironclad`'s `twin_strike` / `fiend_fire` and `real_silent`'s
`skewer`.

**C3 — whether tier0 applies powers to corpses.** Parity says yes (§3.2). tier0
has never done it: `_pick_targets` filters `state.living_enemies` and no op can
currently reach a dead enemy. Standing it up means a dead `Enemy` carrying
Vulnerable / Weak / Poison / a Bomb, and the consequences are unexamined —
`combat.py:91` **revives** a phased enemy from `hp <= 0`, so a power banked on
a "corpse" can come back with it; `reactions.py:92` clears the aura on death
but not the powers; `effects.py:889`'s `bombed_at_cast` already iterates
`state.enemies` including the dead. Under binding, `bash`'s Vulnerable moves
from a **living** enemy #2 to a corpse, i.e. the repair *removes* a live debuff
that today lands — a real strength loss for the anchor deck, not a rounding
difference.

Only the initial-aim half of (c) is clean (§3.3).

---

## 5. Stamp story (part (d)) — NOT a clean single window

The row's own gate premise is falsified by the enumeration. It reads: *"it
moves Klee tier-0.5 numbers on one observation and takes its OWN window and
re-baseline"*.

- **Narrow** already moves Furina (`matinee_performance`, `flood_of_emotion`)
  and Kokomi (`read_the_current`) as well as Klee — a `C` window archiving all
  three characters' combat numbers, exactly like `C17`. That is declarable, but
  it is not what the row authorised.
- **Wide** additionally moves `ref_ironclad`'s starter deck, `ref_silent`, and
  the `real_ironclad` / `real_silent` pools. The `(ref_ironclad, starter)`
  anchor renormalises to 3.0 by construction, but every axis number in the repo
  was taken against the *old* anchor's behaviour, and the `real_*` floors
  (5.5% / 67.2% and 1.3% / 54.4%) are published in STATE.md's standing-baseline
  addendum. That archives the standing baseline itself — a far larger stamp
  event than one window's re-baseline, and one that no pending decision has
  asked for.
- **C2 on top** widens it again.

Which window is owed cannot be declared until C1–C3 are answered, so (d) is
downstream of (c) and fails with it.

---

## 6. Recommendation and the open questions for [USER]

**Recommendation: hold EB-136 for one ruling, then implement in a single pass.**
The engineering is small and now fully specified by §3; what is missing is the
scope decision, and it is worth one answer rather than a narrow landing that
has to be reopened. Nothing about this write-up is blocked on further
investigation.

**Q1 — which ops bind?** (a) the three the next-action names, closing the row
with `bash` and the `ic_*`/`si_*` debuff attacks still scattering and the scope
sentence narrowed to match; or (b) every `target: enemy` op, which is what the
scope sentence says, and which moves the scoring anchor's deck and both
`real_*` pools.

**Q2 — does intra-op `times` bind in the same pass?** C# is settled: hits after
the aim dies fizzle. Same pass, or a second row?

**Q3 — does tier0 apply powers to corpses, matching C# exactly, or drop an
aimed power whose target died?** Exact parity is the corpse; the sim-visible
consequence is that a debuff that today lands on a living enemy stops landing
at all, and it needs the dead-enemy power state §4/C3 describes. Dropping it
instead is a declared, documented tier0 divergence — cheaper, and invisible in
the mod, but a divergence.

An answer to Q1(b) implies the window in §5's third bullet, so Q1 and the
window declaration are one call, not two.

**Until this is ruled, everything the row already protects stands unchanged:**
`sparkly_explosion`'s simulated number remains DIAGNOSTIC (declared at
`tier0/constants.py` C17 (a) and in STATE.md's `C` row), and a weak tier-0.5
number on a gather-and-detonate card is still not a verdict on the card.

---

## 7. Method

- Enumeration: mechanical walk of every sheet's `effects`, `then`/`else` arms,
  `modes` bodies and `sly` riders, with a co-resolution test on the exclusive
  branch keys. Not a grep.
- Decompile: `ilspycmd` 8.2.0.7535 against the pinned
  `sts2.dll` v0.107.1 — `AttackCommand`, `CardPlay`, `CardCmd`, `CreatureCmd`,
  `PowerCmd`, `Creature`. All quotations above are verbatim decompiler output.
- `game_ref/` was read read-only from the primary checkout and was never linked
  into this worktree.
- No engine, sheet or stamp was modified on this branch by this audit.
