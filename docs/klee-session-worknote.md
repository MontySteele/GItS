# Worknote — Klee Session (chat → Code)

**Date:** 2026-07-20. Five items, roughly in priority order. Items 1–2 are
sheet/errata work, 3 is a display ruling, 4 is art follow-ups, 5 is a
cross-session obligation with a test waiting on it.

## 1. Errata: Can't Catch Me! (user catch — strict domination)

CCM (uncommon, 1 cost: block 4 + spark 1 + draw 1) strictly dominates
Warm Glow (common, 1 cost: block 3 + spark 1): same cost, superset of
effects, every shared number ≥. Rarity does not excuse strict supersets —
uncommons buy different or bigger-with-a-twist, never "the common plus
stuff."

**Delta (R11 convention — deltas):**

```
cant_catch_me: {block: -2}    # 4 → 2; spark and draw unchanged
```

Result: Warm Glow = the tankier spark-block at common; CCM = the tempo
spark-block at uncommon. Neither dominates. Rationale: buffing the
common instead would quietly un-shave the spark block riders the pass-3
hardening deliberately shaved (−1 each); this errata respects that
decision.

**Sequencing:** queued BEHIND the R10 Crackle measurement window if it
hasn't run; back-to-back if it has. Do not land both in one window —
spark-deck attribution stays clean. Update the sheet comment comps that
reference CCM's old block if any exist.

## 2. Note: strict-domination lint is ASSIGNED TO THE FURINA SESSION

A mechanical lint (same-cost cross-rarity pairs within a pool; flag
effect-superset with all amounts ≥) is being added to the sheet-lint
suite by the Furina session, which owns tools/lint_* now. Do NOT build
it here — logging so the two sessions don't collide on shared tooling
(DECISIONS 73 working agreement). It already has a second confirmed hit
on the Furina sheet (Pit Orchestra ⊃ Macaron Break), resolving in
Furina pass 2.

## 3. Ruling: Bomb display — Amount = total pending damage

Playtest finding (user): per-bomb count under the enemy is illegible —
"6" could mean 6 damage or 30.

**Ruled: BombPower's displayed Amount becomes TOTAL pending detonation
damage.** The ecosystem convention decides it: enemy-side status numbers
read as incoming damage (Poison trains this); count display fights the
convention AND makes Chain Fuse (+3/bomb) and Careful Arrangement
(+2 on move) completely invisible. Under damage display, bomb buffs
visibly move the number — legible and satisfying.

Implementation constraints:
- **Display layer only.** The per-bomb list stays the internal source of
  truth; detonation still iterates bombs individually, each firing its
  own damage event and IBombDetonationListener tick — Pounding
  Surprise's per-bomb Sparks and all listeners unchanged.
- Amount recomputes on place / modify_bombs / move_bombs / any per-bomb
  mutation (multiplayer sync included).
- Dynamic tooltip carries the count: "Detonates for {total} damage
  ({count} Bombs)." Spark-economy planners hover once; everyone else
  gets the decision-driving number at a glance.
- No .pck dependency — pure PowerModel change.
- Sim: no change (Tier 0 has no display layer; provenance already logs
  per-bomb).

## 4. Art follow-ups (from the chat-side re-render of all 53 finals)

The taste-pass execution is endorsed — including the evidence-based
overrules of the chat doc (the dead VFX register). Three items remain:

1. **blast_radius and cluster_charge are still the minigame grid
   boards** — the chat doc's "AoE render" suggestion was made
   sight-unseen and was wrong (they're board diagrams, not blast
   rings). Targeted re-search: firework-display key art, event
   explosion key visuals (Midsummer-style), or splash-register with
   punch-in.
2. **sparks_n_splash ← Character_Klee_Full_Wish.png** (already in
   art/raw, currently unused). Her Burst is the signature rare and
   currently wears a gray statue render — the weakest image on the most
   important card. The full wish splash is the correct register for an
   ultimate.
3. **Verify prune_witch_hunt and big_badda_boom alpha in-game** — the
   chat contact-sheet renderer showed black fringing on both, but its
   cover path doesn't alpha-flatten the way art_process now does.
   Likely a chat-renderer artifact, not a pipeline bug; one boot
   confirms.

## 5. Obligation: revert the inline `upgrade:` fields (R20)

Convention ruling: `*-upgrades.yaml` sheets won; inline upgrade fields
in card sheets are deprecated. This session's two inline entries in
klee-cards.yaml (sparkly_treasure / spark_collection) duplicate the
klee-upgrades.yaml deltas that M9 already shipped — **revert the inline
fields; nothing is lost.** The shared loader currently emits a loud
warning naming these rows, and test_no_inline_upgrades_on_docs_sheets
carries klee-cards.yaml as its sole temporary allowlist entry — once
the revert lands, tell the Furina session (or note it in DECISIONS) so
the allowlist entry comes out and the convention is fully enforced.

Standing working agreement, now logged as DECISIONS 73: schema changes
to shared loaders require a cross-session note BEFORE landing.

---

## Execution status (Code session, 2026-07-20)

1. **CCM errata: QUEUED, not landed.** Crackle has no `gain_spark` in the
   sheet yet, so the R10 measurement window has not run. The delta and the
   sequencing rule are recorded as a QUEUED ERRATA comment above the
   cant_catch_me row in klee-cards.yaml.
2. **Not touched**, per the assignment. (FYI: the same-cost condition will
   miss CCM ⊃ warm_glow only if cost is compared before the errata lands —
   both are cost 1, so it will flag; the allowlist/errata order may matter.)
3. **Shipped.** `DisplayAmount => PendingDamage` (the game's own
   display-only virtual; NPower badge renders DisplayAmount for Counter
   powers and refreshes on DisplayAmountChanged — verified in decompile).
   Amount stays the count, so stack semantics and multiplayer sync are
   untouched; detonation still iterates per-bomb. Tooltip via
   `smartDescription` loc entry + a "Damage" DynamicVar: "Detonates ... for
   {Damage} total damage ({Amount} Bomb(s))." One boot verifies the loc key
   resolves.
4. **All three done.** blast_radius ← Starlit Sky Firework Card 2 (Klee +
   Albedo under a Jumpy-Dumpty-shaped firework), cluster_charge ← Starlit
   Sky Firework Card 10 (double golden wheel-burst) — firework-display
   register as suggested. sparks_n_splash ← Character Klee Full Wish.
   The alpha fringing was REAL, not a renderer artifact: PIL paste-with-mask
   blends the alpha channel, leaving 191-alpha edge pixels. art_process now
   uses alpha_composite; all 54 card portraits verified min-alpha 255.
5. **Reverted.** Inline fields removed; gen_klee_cards.py now reads the
   `spark:` deltas from klee-upgrades.yaml (only spark — other keys still
   await the wiring ruling and cards keep codegen-default bumps). Regen
   produced byte-identical C#; test_no_inline_upgrades passes. Furina
   session: the klee-cards.yaml allowlist entry in
   test_no_inline_upgrades_on_docs_sheets can come out.
