# Klee design review — "how do we make her stop imploding?"

Ratified next step out of the difficulty-calibration phase
(`docs/calibration-notes.md`). Calibration established the finding: **Klee
takes Ironclad-level damage without Ironclad-level sustain** — worst net %HP
bleed in the cast (21.7%), driven by the normal-fight chip (15% vs the
Ironclads' 5%) she carries into elites, from a 22%-smaller bar with no Burning
Blood. The ruling was that this is a *design* problem, not a numbers tweak, and
that the fix should raise offense / mitigation, NOT chase the A3 block axis
(the "are-you-Ironclad" metric we benched).

This review sizes the problem with two crude crutches, then finds the real
lever. All numbers: 150 runs, seed 11, full loadout (relics + potions +
drafted deck), assigned drafter, generic pilot. Target line = **real_ironclad
@ 40% winrate**, the balanced reference.

Tools (committed, re-runnable): `tools/klee_lever_sweep.py` (buckets 1–2),
`tools/klee_dead_cards.py` (bucket 3), `tools/klee_rework_sim.py` (rework
validation). Run e.g. `python -m tools.klee_lever_sweep --knob damage`.

**Reproducibility caveat.** The Klee numbers reproduce from the repo alone —
her whole pool ships in `docs/klee-cards.yaml`. The `real_ironclad` **target
line (40%) needs the local `game_ref/` artifact**: a gitignored decompiled
reference, intentionally absent on a bare clone. On a machine that has it
(e.g. after a normal `git pull`, which leaves gitignored files untouched) the
target line reproduces exactly — verified: `python -m tools.klee_lever_sweep
--knob damage` returns the table above verbatim. The regeneration path is now
complete: `tools/extract_base_game_pool.py` → `tools/build_ironclad_sheet.py`
merges the extractor's 35 cards with the local `ironclad_pool_pass4.yaml`
supplement (22 cards hand-recovered from the DLL) into the loader's 57-card
`ironclad_pool.yaml` (`--verify` confirms the rebuild is byte-faithful). Both
data inputs stay in gitignored `game_ref/`; only the tools are committed. On a
bare clone the `real_ironclad` tests skip and the target line is skipped
gracefully — the Klee sweep still runs.

---

## Bucket 1 — the damage crutch: **~1.3× reaches parity**

Flat multiplier on every point of damage Klee deals (direct hits, bombs,
sparks, burst — scaled at the `deal_damage_to_enemy` choke).

| dmg × | win% | HP/fight | %maxHP | normals% |
|------:|-----:|---------:|-------:|---------:|
| 1.00  | 10%  | 13.4 | 21.6% | 15.2% |
| 1.15  | 16%  | 13.0 | 20.9% | 14.0% |
| **1.30** | **33%** | 12.0 | 19.3% | 12.2% |
| 1.50  | 62%  | 10.7 | 17.2% | 11.1% |
| 1.75  | 85%  |  8.8 | 14.2% |  8.8% |
| 2.00  | 95%  |  6.9 | 11.1% |  6.4% |

**~1.30–1.35× damage reaches the balanced 40% line.** The mechanism is the
important part: **every bleed row falls monotonically with damage.** For Klee,
damage IS defense — a faster kill is one fewer enemy turn, so less incoming.
The knob attacks the exact gap the bleed table flagged (normals 15% → 6%).

## Bucket 2 — the block crutch: **bigger knob, plateaus, only walls spikes**

Flat multiplier on the block *her cards* put up (the `block` op — NOT potion /
relic block, which is loadout).

| blk × | win% | HP/fight | normals% |
|------:|-----:|---------:|---------:|
| 1.00  | 10%  | 13.4 | 15.2% |
| 1.50  | 33%  | 11.8 | 13.1% |
| 2.00  | 64%  | 10.8 | 12.0% |
| 2.50  | 84%  |  9.8 | 11.9% |
| 3.00  | 87%  |  9.1 | 12.1% |
| 4.00  | 95%  |  8.4 | 13.5% |

Block needs **~1.6×** for parity (vs damage's 1.3×), and its normals-bleed
**floors at ~12%** — you cannot block chip that damage would have deleted at
the source. Block's winrate gains come purely from walling the elite/boss
spikes; it is the more expensive, less complete knob, and it is the A3 lever
we agreed not to chase. **Verdict: whatever ships should move offense/tempo,
not wall height.**

---

## Bucket 3 — the real fix: 7 dead cards, and the winrate is NOT in them

Cards offered a lot and drafted ~never, **even in their own archetype** (so
this is not just generic-mode power-blindness):

| card | rar | effect | offered | pick% |
|---|---|---|---:|---:|
| alchemical_curiosity | C | draw 2 | 135 | 3% |
| friendly_visit | C | companion cost −1 + draw | 122 | 0% |
| borrowed_brilliance | U | copy a companion in hand | 109 | 0% |
| study_of_explosions | C | scry 2 + burst energy | 100 | 0% |
| elemental_ecstasy (Sweet Dreams) | U | refresh auras + draw/aura | 91 | 0% |
| surprise_visit | U | Vulnerable 2 | 74 | 1% |
| secret_stash | R | add 2 demolition commons | 18 | 0% |

Everything else "dead in generic" is **LOCKED** — alive in its own archetype
(blazing_delight 100%, chained_reactions 83%, remote_detonator 80%,
true_spark_knight 75%…). **Demolition and spark engines are healthy.** The hole
is **reaction** — 5 of the 7 dead cards — exactly the archetype the design docs
already flag as co-op-primary / weakest.

Split by whether the *solo sim* can fairly judge the card:

- **Dead & solo-fixable** (bodyless enabler/debuff, no co-op dependency):
  `alchemical_curiosity`, `study_of_explosions`, `surprise_visit`,
  `secret_stash`.
- **Dead but co-op-dependent** (need companions/auras a solo Tier-0 fight
  can't supply — sim blind spot, defer to Tier-2, do NOT rework blind):
  `friendly_visit`, `borrowed_brilliance`, `elemental_ecstasy`.

Honesty caveat: the assigned drafter's power sense (`draft._static_power`)
counts only `damage`(non-self) + `block`, so **card draw and debuffs score 0**.
`alchemical_curiosity` (draw 2) may be a *drafter* blind spot as much as a card
problem — fixing the drafter is an alternative to reworking the card.

### Proposed reworks (DRAFT stats — for red-pen, not committed)

| card | old | proposed | intent |
|---|---|---|---|
| alchemical_curiosity | draw 2 | **dmg 4 + draw 1** | pyro cantrip: chips + replaces itself |
| study_of_explosions | scry 2 + burst 5 | **dmg 4 rnd + burst 5** | free 0-cost ping that charges the Burst |
| surprise_visit | Vulnerable 2 | **block 4 + Weak 1 ALL** | *status-as-mitigation*: Weak cuts the spike, block gives it a body |
| secret_stash | add 2 demo commons | **dmg 8 ALL + add 2** | value engine gets an immediate board impact |

`surprise_visit` is the concrete expression of the "status effects as
pseudo-mitigation" lever: Weak-all reduces incoming spike damage (the A3×A4
interaction), which is real mitigation without touching the block axis.

### Measured result of the reworks (`klee_rework_sim.py`, 150 runs)

| card | generic pick% | reaction pick% |
|---|---|---|
| alchemical_curiosity | 3% → **57%** | 0% → **35%** |
| study_of_explosions | 0% → **13%** | 0% → **39%** |
| surprise_visit | 4% → **35%** | 0% → 0% |
| secret_stash | 0% → 14% | 0% → **43%** |

| draft | winrate before → after |
|---|---|
| generic | 10% → 9% |
| reaction | 4% → 5% |

**The reworks resurrect the cards (0% → 13–57% picked) but are winrate-neutral
(±1%, noise).** This is the load-bearing finding of the review: in a real draft
the bot *already skips* the dead cards — it takes a body or skips the screen —
so they were never dragging winrate down; they were non-options. Fixing them
adds live *choices*, not power. (`surprise_visit` staying 0% in reaction is
correct: a block+Weak glue card still loses the slot race to reaction bodies;
it earns its place in generic piles, 35%.)

---

## Synthesis

The two sweeps and the rework sim triangulate the same conclusion from three
sides, and they cleanly separate two problems that were being conflated:

1. **Deck-space quality** (the 7 dead cards). Fix = the reworks above (+ the
   co-op three deferred to Tier-2). Effect = more live choices, richer drafts.
   **Winrate effect ≈ 0.** Worth doing for pool health; it is not the imploding
   fix.
2. **The imploding problem** (the 40% gap). The winrate lever is Klee's
   damage envelope **on the cards she already plays** — bucket 1 scaled those
   and hit parity at 1.3×; the rework touched only dead cards and moved
   nothing. Damage is her defense (faster kills → less bleed, all rows);
   block is the expensive knob that only walls spikes.

**Recommendation.** Two independent workstreams, not one:

- **A. Close the 40% gap** by raising the damage envelope of her *live* cards
  by roughly the bucket-1 magnitude (~1.3×), delivered as design rather than a
  global multiplier — e.g. buff the bodies she actually drafts, and/or make the
  dead-card reworks BIGGER than the modest draftable-floor numbers above so
  they contribute real tempo. Pair with `surprise_visit`-style Weak/Vuln
  appliers as pseudo-mitigation on the spikes she cannot block. Explicitly do
  NOT raise block above Ironclad (bucket 2 / the benched A3 axis).
- **B. Rework the 4 solo-fixable dead cards** for pool health (numbers above),
  and defer the 3 co-op-dependent reaction cards to Tier-2 validation.

## Open questions for red-pen

1. Is 40% (real_ironclad parity) the right winrate target for Klee, or should
   her identity sit deliberately lower/higher?
2. Workstream A: buff live cards, or up-size the reworks toward the tempo
   envelope, or both? What band ceiling constrains it (the tank_boss 0.65
   line)?
3. The reaction archetype is the dead zone AND the sim's blind spot. Is that a
   Klee problem or a "reaction is a Tier-2 co-op archetype" problem we accept?
4. `alchemical_curiosity`: rework the card, or fix the drafter's blindness to
   card draw / debuffs (which under-rates a whole class of cards cast-wide)?
