# Run-Model Rework: a realistic tier0.5 gauntlet

**Status:** DRAFT for red-pen — 2026-07-21. Nothing here is implemented.
**Author:** Claude, from rulings this session.
**Scope owner:** tier0.5 (the draft/run layer) ONLY. See §6 for the hard
layer boundary — tier0's battery does not move.

---

## 0. The reframe (why this exists)

Until now the balance oracle has been tier0's **7-axis battery**: five frozen
encounters, each an *instrument* built to stress one axis, normalized so
`ref_ironclad`'s starter = 3.0 on every axis. This session established that
the anchor is not a real character (its starter IS the divisor; its drafted
pool was contaminated by 11 ownerless reference cards; its relic never fired
at the run layer), and that the battery encounters, while HP-plausible, are
not fights anyone actually plays.

**User ruling (2026-07-21):** *"Fundamentally it is the battery itself that is
broken. What we'll need to do is build the tier 0.5 sims to be realistic-ish
enough that we can run a real character like the Ironclad through to figure
out how they rate along the same scale, and then rebalance from there. The
fights we use in tier 0.5 need to be roughly modeled on real fights. We can
skip enemies with unreasonably-hard-to-code mechanics; it just needs to be
'good enough' to actually stress the characters."*

So the goal of this rework: **make tier0.5 a realistic-ish gauntlet** where a
real character (Ironclad, now implemented) and a designed character (Klee)
run the *same* fights, so designed characters can be rated against a real one
and rebalanced from that footing — instead of against a synthetic 3.0 anchor.

This does NOT delete tier0. The 7 axes still describe a character's *shape*.
What changes is which instrument we trust for **difficulty and survival**:
that becomes the realistic run layer, not the frozen battery.

---

## 1. Scope, as ratified

| Decision | Ruling |
|---|---|
| Enemy fidelity | Realistic-**ish**. Roughly model real fights; skip hard-to-code mechanics. |
| Biomes | **One** biome's worth of content, cherry-picking codeable enemies. Not both. |
| Relics | **Skip** for now. Treasure/shop grant/spend **gold only**; relic slot is a stub. |
| Layer | tier0.5 only. tier0 battery stays FROZEN (§6). |
| Acts | Build **Act 1** first, correctly. Multi-act (2–3) is the same machine repeated with a full heal between; land it once Act 1 is trusted. |

---

## 2. What's broken today, concretely

1. **Template length.** `RUN_NODE_TEMPLATE = "NNNENRNNENRNRB"` is **11 fights
   in one act** (7 normal + 1 burst-check + 2 elite + 1 boss). A real StS2 act
   is ~6–8 fights. Every per-fight effect compounds over this inflated count.

2. **Burning Blood is emit-only.** `combat.py:402` does
   `state.emit("heal", ...)` — an event for the A4 metric — and never touches
   `player.hp`. Correct for tier0 (one fight). At the run layer, `model.py:222`
   reads `hp = state.player.hp`, which the emit never moved, so the Ironclad's
   relic has been **silently inert** across every run measurement. Monkeypatch
   test (this session): applying it turns the 66.6% anchor into 99.9% — because
   6 HP × 11 fights ≈ a full extra health bar. The template length is *why* the
   fix looks explosive; at ~7 fights it lands sanely. **These two are one bug.**

   **Fix location (ratified: apply for Ironclad):** the heal is applied in the
   **run layer** (`tier05/model.py`, after each won fight, on characters whose
   `relic_hooks` contain `heal_after_won_fight`), NOT in `combat.py`.
   `combat.py` stays emit-only so tier0's frozen battery and the anchor lock
   (single-fight winrate 0.525 / avg_turns 9.585) are untouched — post-fight
   healing can't affect a single fight anyway, so tier0 loses nothing. This
   keeps the layer boundary (§6) intact: the relic becomes real exactly where
   HP carries across fights, and nowhere else.

3. **No easy/hard pool.** Real Act 1 draws the first 3 fights from an easy
   pool, the rest from a hard pool. We roll a flat 3-entry table every time.

4. **No economy.** No gold, no shop, no treasure. Two of the six real node
   types don't exist.

5. **Enemies are instruments, not a roster.** HP is realistic (boss 240 sits
   in the real 173–252 band; elite 115 in the 61–140 band) but the fights lack
   real texture: exactly one debuff in the whole set, no summons, no scaling,
   no easy/hard identity. `burst_check` is the Lagavulin *boss* sleep-trope
   pinned onto a 60 HP normal.

---

## 3. Proposed Act 1 structure  ⟵ RED-PEN

### 3.1 Node template

New node kinds: `T` treasure, `$` shop (join existing `N`/`E`/`R`/`B`). Drop
`BC` (burst-check) — it was an A6 instrument, not a fight.

```
RATIFIED:  N N N R E T N $ E R B          (11 nodes, 7 fights)
```

| | count | notes |
|---|---|---|
| Normal `N` | 4 | fights 1–3 easy pool, fight 4 hard pool |
| Elite `E` | 2 | both hard pool |
| Boss `B` | 1 | act finale |
| Rest `R` | 2 | heal 30% max HP **or** smith **or** remove (existing policy) |
| Treasure `T` | 1 | gold + [relic slot stub] |
| Shop `$` | 1 | placed after treasure so there's gold to spend |

That's **7 fights** vs today's 11 — the reduction that makes per-fight effects
(Burning Blood, and any future per-fight relic) read correctly. Fight mix
(4 normal / 2 elite / 1 boss) sits in the middle of the ratified 3–4 / 2–3 / 1.

**The first `R` sits before the first `E` (red-pen 2026-07-21):** you never
path to an elite that early without a chance to heal or upgrade first — it's
suicide. So the first rest precedes elite #1 (node 4 → 5), and the second
rest precedes the boss (node 10 → 11). Both elites and the boss are now
reachable off a rest. Easy/hard split is unaffected: the three easy fights
are still the first three `N`; elite #1 is the fourth fight and draws hard.

### 3.2 Easy vs hard pool

Real rule (StS2, confirmed): **first 3 monster fights → easy pool; fights 4+ →
hard pool; no encounter repeats within an act.** Model exactly this. In the
template above the three easy fights are the first three `N`; the fourth `N`
and both elites draw hard.

### 3.3 Multi-act (later)

Acts 2–3 are the same loop with a different roster and a **full heal at each
act boundary** (StS restores you at every boss-clear rest). Carry the deck and
relics forward; reset HP to max. Deferred until Act 1 is trusted.

---

## 4. Enemy roster — one biome, codeable subset  ⟵ RED-PEN

Numbers are real StS2 (wiki.gg, early-access v0.99.x; HP is a spawn-time
range). We lean **Overgrowth** because its roster is the more codeable one,
and cherry-pick within it. Everything below is expressible with the *existing*
intent kinds (`attack`/`block`/`buff`/`debuff`/`summon`) plus at most a small,
named power addition. Mechanics we **skip** are listed explicitly — the rule
is skip-loudly, never approximate-silently.

### 4.1 Easy pool (fights 1–3)

| Enemy | HP | Modeled intents | Skipped |
|---|---|---|---|
| **Nibbit** | 42–46 | Butt 12 · Hesitant Slice 6 +5 block · Hiss +2 Str | — (fully codeable) |
| **Inklets ×3** | 11–17 ea | small multi-target chip (swarm shape) | — |
| **Leaf/Twig Slime group** | ~25–45 | basic attack + a Frail/Weak dab | slime split-on-hit (skip) |

### 4.2 Hard pool (fights 4+)

| Enemy | HP | Modeled intents | Skipped |
|---|---|---|---|
| **Mawler** | 72 | Claw 4×2 · Rip and Tear 14 · Roar apply 3 Vuln | — |
| **Fogmog** | 74 | summon add (opener) · Thwack 8 +1 Str · Headbutt 14 | — (summon is supported) |
| **Sewer Clam** | 56 | Jet 10 · Pressurize +4 Str · gains block (≈Plating 8) | damage-cap semantics of Plating (model as block) |

### 4.3 Elite pool — 3 enemies, 2 drawn per act  ⟵ RATIFIED

Modeled as a **pool of 3, drawing 2 per run** (real StS elite-draw). Over 1500
runs each elite is well-sampled, and every run faces a mix. The three are
chosen to check **different** things — a character that looks healthy against
one should be exposed by another.

| Elite | HP | Checks | Modeled | Skipped |
|---|---|---|---|---|
| **Byrdonis** | 81–84 | **ramp/clock** — Territorial +1 Str/turn: kill it fast or drown | Swoop 17 · Peck 3×3 · +1 Str end of turn | — (fully codeable) |
| **Bygone Effigy** | 127 | **block/burst** — Sleep→Wake+10 Str→Slashes 13/turn | Sleep → Wake +10 Str → Slashes 13 | **Slow** (per-card +10% dmg) — skip, flavor |
| **Phantasmal Gardener ×4** | 26–31 ea | **AoE** — 4 bodies from turn 1; single-target decks drown, AoE decks faceroll | each cycles Bite 5 · Lash 7 · Flail 1×3 · Enlarge +2 Str (staggered) | **Skittish 6** — skip |

**Why the AoE elite (red-pen 2026-07-21):** Byrdonis and Bygone Effigy are
both single-target block/ramp checks — a fragile-but-fast deck could clear the
whole act never having its AoE weakness probed. Most characters do great on
one of {single-target, multi-body} and poorly on the other, so the elite pool
must contain both shapes or the survival numbers lie. Phantasmal Gardener is
the sharpest AoE check available (4 separate bodies present from turn 1) **and**
the most codeable (4 plain enemies on staggered standard cycles — no summon
hook, no status inject).

**Cross-biome note:** Phantasmal Gardener is an *Underdocks* elite; Byrdonis /
Bygone Effigy / Vantom are *Overgrowth*. This mixes biomes, which the "one
biome" scope (§1) otherwise avoids. Accepted deliberately: the AoE-coverage
requirement outranks biome purity for a *measurement* roster. We are building a
gauntlet that stresses characters, not a faithful single path.

### 4.4 Boss  ⟵ RATIFIED: Vantom

| Boss | HP | Modeled | Skipped |
|---|---|---|---|
| **Vantom** | 173 | Ink Blot 7 · Inky Lance 6×2 · Dismember 27 · Prepare +2 Str | Wound injection · 9 Slippery — skip both |

Vantom's 173 HP is the gentlest of the six real Act-1 bosses — a fair finale
for a first pass, and codeable with only two skipped (flavor) mechanics.
(The Kin and Lagavulin Matriarch remain documented in the research notes as
Act-1 boss alternates if we want boss variety later.)

### 4.5 The skip line (DSL work we are NOT doing)

HP-threshold phase changes · damage-cap Plating · Intangible/Slippery ·
status-card injection (Wounds/Infection/Beckon) · Steam/explosion-on-death ·
Slow. Each is a real mechanic; each is flagged UNIMPLEMENTED on any card/enemy
that wants it, never faked.

---

## 5. Economy: gold + treasure + shop  ⟵ RED-PEN

The smallest closed loop that makes treasure and shop mean something.

- **State:** add `gold: int` to the run (starts 99, StS default).
- **Income:** each won fight pays gold (normal ~10–20, elite ~25–35, boss ~？);
  Treasure node pays a lump (~25–50) + [relic stub].
- **Shop:** offers a few cards + a card-removal at prices (card ~50–75,
  removal ~75 rising). **Buy policy** reuses the draft policy's existing card
  valuation, gated by price and gold — a card is bought iff the policy would
  draft it AND gold allows. Removal bought when a known-dead card (curse,
  unupgradable filler) is present and affordable.

All the `？`/ranges above are OPEN NUMBERS (§8).

---

## 6. Layer boundary (do not cross)

tier0's five battery encounters (`tier0/content/encounters/battery.yaml`,
`punisher.yaml`) are the **frozen calibration** for every ratified 7-axis
score, for Klee and Furina both. This rework adds a realistic roster at
**tier0.5 only**. The battery is not retuned, not extended, not touched. Any
change that reaches `battery.yaml` or the `ref_ironclad` normalization
invalidates existing axis numbers and is out of scope here.

Corollary: the realistic enemies live in a **new** tier0.5 encounter source
(e.g. `tier05/content/act1_pool.yaml`), not in the battery.

---

## 7. Measurement plan (what "done" proves)

After implementation, rerun the same-seed comparison that's been the through
-line all session:

1. `ref_ironclad`, `real_ironclad`, `klee` through the realistic Act 1,
   1500 runs, seed 11: winrate (95% CI), act median HP, share below 30%,
   near-death rate.
2. **The load-bearing read:** with a real character run through realistic
   fights, where does Klee land relative to the Ironclad on the same scale?
   That number — not the 3.0 anchor — becomes the rebalance target.
3. Confirm tier0 axis medians for Klee/Furina are **unchanged** (they must be:
   different layer).
4. Confirm Burning Blood now moves HP and lands in a sane range (not 99.9%).

---

## 8. Decisions — RATIFIED 2026-07-21

- [x] Node template `N N N R E T N $ E R B` (§3.1) — first rest moved before
      first elite.
- [x] Elite pool = Byrdonis + Bygone Effigy + **Phantasmal Gardener** (AoE),
      draw 2 of 3; boss = Vantom (§4.3–4.4).
- [x] Add a real `frail` power (block-gain reduction) — not mapped to Weak.
- [x] Burning Blood **applies** for Ironclad, in the run layer only (§2).
- [x] Gold: start 99; income ~10 normal / ~25 elite / boss TBD; treasure lump
      ~40; card ~60, removal ~75 rising (§5). Defaults accepted; tune post-loop.

Still deferred (NOT this pass):
- [ ] Multi-act enemy rosters (Act 2/3) — same machine, new roster, full heal
      between. Land Act 1 first.
- [x] Furina Tier 0.5 assigned-pilot runner integration — deferred by this
      pass, then closed 2026-07-22. Salon/Spotlight/Fanfare are now ordinary
      character-scoped runner plans; baseline in `furina-tier05-baseline.md`.

---

## 9. What this pass does NOT change

- No card balance numbers (Klee/Furina/Ironclad).
- No tier0 battery, no axis definitions, no 3.0 normalization.
- No relics modeled (gold economy only).
- Historical note: this pass shipped while the CLI's `ARCHETYPE_PILOTS` was
  Klee-scoped. The follow-up closed on 2026-07-22; Furina can now run through
  the realistic Act-1 layer with her three assigned pilots.
