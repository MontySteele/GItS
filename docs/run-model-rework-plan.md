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
      between. Land Act 1 first. **→ picked up 2026-07-23, plan in §10.**
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

---

# §10. Multi-act extension: Acts 2–3

**Status:** RATIFIED 2026-07-23 (red-pen answers logged in §10.8; skip
backlog in §10.9). Implementation started 2026-07-23 (Pass 1).
**Rationale (user):** an Act-1-only sim over-rewards builds that frontload
power with minimal scaling into later acts. The §3.3 deferral is now due:
Act 1 is trusted (relic/potion layer + calibration landed).

**Source data:** `docs/act2-act3-roster-research.md` (STS2 wiki harvest,
2026-07-23). Act 2 = **the Hive**, Act 3 = **Glory**. (Underdocks is an
*Act 1 alternate zone*, not Act 2 — fan sites get this wrong.) STS2's real
act transition matches the proposal here: boss → 100 gold + choice of 3
Rares → Ancient floor = heal 100% of missing HP + choice of 3 boons/relics.

## 10.0 Rulings already given (user, 2026-07-23)

1. **Boss pools: ≥2 bosses per act, INCLUDING Act 1.** The single-Vantom
   compromise (§4.4) existed to avoid engine ops that Acts 2–3 now require
   anyway, so it no longer buys anything — expand Act 1 too (§10.5).
2. **The Klee design review is NOT a gate** — concluded for now pending more
   playtesting. Act-3 winrate being much lower than Act-1 winrate is
   accepted and expected, not a blocker.
3. Housekeeping (separate from this plan): old docs still quote pre-latest-
   playtest Klee numbers and need a scrub pass.

## 10.1 Pass 1 — act machinery (roster-agnostic)

The structural review confirms §3.3's premise: `run_one()` already carries
hp / max_hp / deck / gold / relics / potions as locals across the node loop,
so multi-act is an outer loop, not a rework.

- **Act loop:** wrap the node walk in `for act in range(n_acts)`. Boss win on
  a non-final act continues; any death or final-boss win returns. CLI gains
  `--acts N` (default 3); `--acts 1` is kept as a supported instrument for
  continuity with existing Act-1 tooling (`measure_realistic_act1.py`, the
  calibration surfaces).
- **Template:** same ratified 11-node `N N N R E T N $ E R B` for every act
  (STS2 acts share the shape: mid-act treasure, pre-boss rest, one shop).
  Per-act template variation is NOT proposed — one lever at a time.
- **Easy/hard rule per act:** Act 1 first **3** `N` easy (unchanged);
  Acts 2–3 first **2** `N` easy, third `N` draws hard (real STS2 rule).
- **Boss pool:** `ActDraw` generalizes to per-act pool files and draws the
  boss from a pool of ≥2 (ruling §10.0.1), like elites draw 2-of-3 today.
- **Act boundary event** (after non-final boss win, before next act):
  1. Boss reward: **100 gold** (resolves §5's `boss ~？` open number) +
     choice-of-3 **Rare** cards via the existing, currently-unused
     `roll_rewards(companion_rarity="rare")` hook.
  2. **Ancient:** heal to full (`hp = max_hp`) + choice of 1 from 3 offered
     **Ancient boons** — a new pool (the boss-tier stub in `relics.py`
     finally gets filled). SHIPPED (Pass 1): a 7-boon representative sample
     of the REAL StS2 Act-2/3 Ancient boons, each mapping 1:1 onto existing
     hooks — Sand Castle (upgrade 6), Yummy Cookie (upgrade 4), Very Hot
     Cocoa (+4 energy/combat), Pael's Blood (+1 draw/turn), Looming Fruit
     (+31 max HP), Signet Ring (+999 gold), Diamond Diadem (20 start-block;
     its 1-turn retention skipped loudly). Wiki caveat: the 100%-missing-HP
     heal number comes from the Mobalytics guide; the wiki proper confirms
     the choice-of-3 but not the heal fraction — the full heal is our
     ratified rule either way.
- **Shops 2 and 3** exist for free (template repeat); the rising removal
  price (`constants.py` note) finally bites as designed.

## 10.2 DSL promotions off the §4.5 skip line  ⟵ RED-PEN

Acts 2–3 lean on mechanics §4.5 skipped. Rule stays skip-loudly, but two ops
graduate because they are *everywhere* (skipping them would sand the acts'
identity off entirely):

| Op | Promote? | Why / scope |
|---|---|---|
| **Status-card injection** (shuffle Dazed/Burn/Wither/Slimed/Toxic into player deck/discard/hand) | **YES** | The signature Act 2/3 pressure; appears on normals, elites, and 2 of 3 proposed bosses per act. One generic `inject {card, count, pile}` intent op. |
| **HP-threshold boss phases** | **YES** | Required for Test Subject (the most codeable Act-3 boss); useful later for Act-1 alternates. `phases: [{hp, moves…}]` on a boss spec. |
| Enemy self-heal intent | small | Knowledge Demon's Ponder (heal 30). Trivial op; needed only if that boss is picked. |
| On-death partner trigger | defer | Kaiser Crab's Crab Rage. Only if Kaiser is picked (§10.3); else stays skipped. |
| Stat-theft (Lost/Forgotten), Back Attack, untargetable/Burrow, card theft, Ethereal/Downgrade auras, 99-stack gimmicks (Queen, Terror Eel), Intangible, Artifact, Thorns, damage caps (Hard to Kill / Plating) | **NO — stay skipped** | Flagged UNIMPLEMENTED per enemy below; enemies whose *identity* is one of these are dropped from the roster instead of faked. |

## 10.3 Act 2 roster — the Hive, codeable subset  ⟵ RED-PEN

Same format as §4: modeled intents use existing kinds + the §10.2 promotions;
skips are explicit.

**Easy pool (fights 1–2):**

| Enemy | HP | Modeled | Skipped |
|---|---|---|---|
| Bowlbug (Rock) + 1 worker | 45–48 + worker | Headbutt 15; worker per type (Egg 7+7blk / Silk 4x2+Weak / Nectar +Str-to-Rock) | Dizzy self-stun (model as stagger) |
| Exoskeleton ×3 | 24–28 ea | Skitter 1x3 · Mandibles 8 · Enrage +2 Str | Hard to Kill damage cap |
| Tunneler | 87 | Bite 13 · Burrow +32 block · Attack from Below 23 | untargetable + stun |

**Hard pool (fights 3+):**

| Enemy | HP | Modeled | Skipped |
|---|---|---|---|
| Chomper ×2 | 60–64 ea | Clamp 8x2 · Screech **inject 3 Dazed** | Artifact 2 |
| Hunter Killer | 121 | Bite 17 · Puncture 7x3 · Goop → 2 Vulnerable | Tender (mapped to Vuln) |
| Louse Progenitor | 134–136 | Web Cannon 9 + 2 Frail · Curl and Grow +14 blk +5 Str · Pounce 14 | Curl Up (fold into block) |
| Myte ×2 | 61–67 ea | Bite 13 · Suck 4 +2 Str · Cornucopia **inject 2 Toxic** (Toxic ≈ Dazed-with-teeth: unplayable, 2 dmg on draw ⟵ RED-PEN) | — |
| Ovicopter | 124–130 | Lay Eggs summon 3× egg (14–18, Nibble 4) · Smash 16 · Tenderizer 7 + 2 Vuln · +3 Str | Hatch upgrade step |
| The Obscura | 123 | summon Parafright (21, Slam 16) · Piercing Gaze 10 · Wail +3 Str all · Hardening Strike 6 + 6 blk | Illusion status |

Dropped from roster (identity = skipped op): Thieving Hopper (card theft +
flee), Spiny Toad (Thorns), Slumbering Beetle (Plating; sleep already covered
by Bygone Effigy in Act 1).

**Elite pool — 3, draw 2** (same checks-different-things doctrine as §4.3):

| Elite | HP | Checks | Modeled | Skipped |
|---|---|---|---|---|
| Decimillipede | 3 × 46–52 | **AoE/multi-body** | 3 bodies, offset cycles: Bulk 7 +2 Str · Writhe 6x2 · Outgas 9 + 1 Weak | Reattach |
| Entomancer | 145 | **ramp + deck pollution** | Beeeees 3x7 · Spear 18 · Pheromone Spit +1 Str and **inject 1→2→3 Dazed** (escalating, approximates Personal Hive) | Hive-on-hit trigger (made periodic) |
| Infested Prism | 161 | **block/burst clock** | Jab 15 · Radiate 11 + 16 blk · Whirlwind 5x3 · Pulsate 8 + 20 blk | Vital Spark |

**Boss pool — 2 of the 3 real bosses ⟵ RED-PEN (pick 2):**

| Boss | HP | Codability | Modeled / skipped |
|---|---|---|---|
| **Knowledge Demon** (recommended) | 379 | good | Slap 17 · Overwhelming 8x3 · Ponder 11 + self-heal 30 + 2 Str · Curse → fixed **Disintegration 6/turn dot** (drops the pick-your-poison). Needs: self-heal op. |
| **Kaiser Crab** (recommended) | 209 + 199 | medium | two bodies on fixed cycles (Crusher melee / Rocket ramp-to-Laser 31). Skip Back Attack. Crab Rage needs the on-death trigger — or approximate as the survivor's cycle gaining +6 Str permanently ⟵ RED-PEN. |
| The Insatiable | 321 | poor | identity IS the Frantic-Escape death timer; statline-only version (Thrash 8x2 / Bite 28 / +2 Str) would be a plain punchbag. Recommend **drop, skip-loudly**. |

## 10.4 Act 3 roster — Glory, codeable subset  ⟵ RED-PEN

**Easy pool (fights 1–2):**

| Enemy | HP | Modeled | Skipped |
|---|---|---|---|
| Devoted Sculptor | 162 | Incantation → +Str/turn ritual ramp · Savage 12 | — |
| Scroll of Biting ×3 | 31–38 ea | Chomp 14 · More Teeth +2 Str · Chew 5x2 | Paper Cuts |
| Living Shield + Turret Operator | 55 + 41 | Shield: starts 25 block, Slam 6 / Smash 16; Turret: Unload 3x5 · +1 Str | Rampart semantics (start-block) |

**Hard pool (fights 3+):**

| Enemy | HP | Modeled | Skipped |
|---|---|---|---|
| Axebot | 70–78 | Boot Up +10 blk +3 Str · One-Two 9x2 · Uppercut 12 + Weak/Frail | Stock |
| Punch Construct + 2 Cubex | 55 + 65×2 | Punch: READY +10 blk → 14 → 5x2 + Weak; Cubex: +2 Str then repeater 7 + 2 Str cycle | Artifact 1 each |
| Fabricator | 150 | summon bots (Zapbot 14 / Stabbot 11+Frail / Guardbot +15 blk to Fabricator) · Fabricating Strike 18 + summon · Disintegrate 11 | Noisebot (Dazed inject minion — optional) |
| Frog Knight | 191 | Tongue Lash 13 + Frail · Strike Down 21 · +5 Str · Beetle Charge 35 | Plating 15 |
| Globe Head | 148 | Shocking Slap 13 + Frail · Thunder Strike 6x3 · Galvanic Burst 16 + Str | Galvanic 6 |
| Slimed Berserker | 266 | Vomit Ichor **inject 10 Slimed** · Pummeling 4x4 · Leeching Hug Weak +Str · Smother 30 | — (the deck-pollution stress test) |

Dropped: Owl Magistrate (Soar/untargetable), The Lost + The Forgotten
(stat-theft is its whole identity).

**Elite pool — 3, draw 2:**

| Elite | HP | Checks | Modeled | Skipped |
|---|---|---|---|---|
| Knight Gang | 101/93/82 | **multi-body** | 3 knights on their real cycles (Ram 15 / Flail 9x2 / Soul Slash 15 / Soul Flame 3x3 / Magic Bomb 35 …) | Hex, Ethereal aura, Downgrade aura |
| Mecha Knight | 300 | **burst + pollution** | Charge 25 → Flamethrower **inject 4 Burn** → Windup +15 blk +5 Str → Heavy Cleave 35 | Artifact 3 |
| Soul Nexus | 234 | **pure damage race** | Soul Burn 29 · Maelstrom 6x4 · Drain Life 18 + 2 Vuln + 2 Weak (random no-repeat) | — (fully codeable) |

**Boss pool — 2 of the 3 real bosses ⟵ RED-PEN (pick 2):**

| Boss | HP | Codability | Modeled / skipped |
|---|---|---|---|
| **Test Subject** (recommended) | 100→200→300 phases | good *with the phase op* | P1 Bite 20 / Skull Bash 14 + Vuln; P2 Multi-Claw 10x3 growing +1 hit/turn + **inject Wounds on unblocked dmg → approximate as inject 1 Wound/turn**; P3 Lacerate 10x3 · Big Pounce 45 · **inject 3 Burn** +2 Str. Skip Intangible (P3 already scales). |
| **Aeonglass** (recommended) | 512 | good | Ebb 22 + 33 blk · Eye Lasers 11x2 · Intensity **inject 1 Wither** (+2 Str, escalating). Cadence trigger (every-6-cards) → approximate as on-cycle injection. Skip Artifact 3. |
| Queen + Amalgam | 400 + 199 | poor | identity = Chains of Binding + 99 Frail/Weak/Vuln + scripted two-part duet. Recommend **drop, skip-loudly**. |

## 10.5 Act 1 boss pool expansion (ruling §10.0.1)

**LOCKED (user, 2026-07-23): Lagavulin Matriarch**, 222 HP (Underdocks —
another accepted biome import, precedent Phantasmal Gardener §4.3). The
harvest showed no literal crab in either Act-1 pool (Kaiser Crab is Act 2's);
asked, the user confirmed the shelled Matriarch is "the crab." She checks the
opposite shape from Vantom: sleeps 3 turns, then Slash 19 / Disembowel 9x2 /
Slash 12 + 12 block / Soul Siphon — modeled with her +2 Str ramp half, so
long fights get strictly worse (anti-turtle, anti-slow-scaling). Skipped
loudly (§10.9): Plating 12 damage-cap, Soul Siphon's player stat-drain (the
stat-theft op). Full Act-1 boss-pool harvest (all six bosses, both zones) is
archived in `act2-act3-roster-research.md` for future pool growth.

## 10.6 Metrics & measurement

- `RunResult` gains an `act_by_node` (or boundary-index) record; `run_metrics`
  survival profiles segment **per act** instead of positional whole-run
  (they currently index the fixed 11-node template and would silently lie on
  a 33-node run).
- New headline surfaces: overall winrate + **per-act funnel** (reached Act 2 /
  cleared Act 2 / reached Act 3 / won), per-act median HP and share-below-30%.
- Measurement plan (mirrors §7): `ref_ironclad`, `real_ironclad`, `klee`,
  `furina` through 3 acts, 1500 runs, seed 11. The load-bearing read is the
  same — where do designed characters land relative to the real Ironclad on
  the SAME 3-act gauntlet — plus the new one this whole extension exists for:
  **which builds' winrates collapse between Act 1 and Act 3** (frontload vs
  scaling).
- tier0 axis medians must remain unchanged (layer boundary §6, untouched).

## 10.7 Version stamps & test re-stamps

- `RUNTEMPLATE_VERSION` 3 → 4. NOTE: even `--acts 1` under v4 is **not**
  seed-comparable to v3 — the boss-pool draw adds an rng call that shifts the
  whole downstream stream. All existing run-layer numbers are archived as v3;
  no unlabeled cross-stamp comparisons (house rule).
- `RUNTEMPLATE_VERSION` 4 → 5 (Ironclad-0.6% diagnosis, 2026-07-23): the
  act-boundary CARD offers are now forced Rare — §10.1's ratified
  "choice-of-3 Rares", which v4 shipped as a forced-Rare *companion* slot
  only (a no-companion character got plain commons at the boundary).
  Boundary screens skip their rarity rolls, so v5 runs diverge from v4 after
  the first boss; `--acts 1` runs (no boundary) are v4-identical.
- Tests to re-stamp: `test_m5` template-shape asserts (goes per-act),
  run-layer cadence tests (shop economy, relic granting, Burning Blood,
  potions — all assume 7 fights/run), determinism lock re-baselined.
- New tests: act-boundary event (full heal + rare companion + Ancient grant),
  boss-pool draw coverage, carryover invariants (deck/gold/relics persist,
  hp resets), per-act easy-pool rule (3/2/2), injection op unit tests.
- Untouched by design: the 0.525 single-fight anchor and every tier0
  1000-fight battery band (other side of the layer boundary).

## 10.8 Sequencing (4 passes) & decision checklist

Passes: **(1)** act machinery §10.1 + stamps §10.7 + Act-1 boss harvest
§10.5 → **(2)** DSL promotions §10.2 + Hive roster §10.3 → **(3)** Glory
roster §10.4 → **(4)** metrics + 3-act baseline measurement §10.6. Rosters
sequence after machinery so each lands against a green suite.

RED-PEN — RATIFIED 2026-07-23:
- [x] §10.1 Ancient relic pool: grab a **representative sample of the real
      STS2 Ancients, biased to easy-to-implement** (~6 first pass; harvest
      the real list, pick from it).
- [x] §10.2 promotions in (injection op + phase op); everything else stays
      skipped **and goes on the §10.9 backlog to fill in later** (user
      condition on this ratification).
- [x] §10.3 Act 2 roster + Toxic semantics as proposed; bosses = **Knowledge
      Demon + Kaiser Crab**.
- [x] §10.4 Act 3 roster as proposed; bosses = **Test Subject + Aeonglass**.
- [x] §10.5 second Act 1 boss: **Lagavulin Matriarch** (user-confirmed
      2026-07-23 — "the crab"; no literal crab exists in the Act-1 pools).

**Pass 1 SHIPPED 2026-07-23** (full suite 574 green): act loop + per-act
registry (`RUN_ACTS`, `tier05/acts.py` replacing `act1.py`), boss pools with
Lagavulin Matriarch beside Vantom, boundary event (forced-Rare companion
slot + Ancient full heal + 7-boon Ancient pick), boss gold 40→100, `--acts`
CLI flag, RUNTEMPLATE_VERSION 3→4, act-1 calibration tools pinned
`n_acts=1`, `tier05/tests/test_multiact.py`.

**Act-1 sanity (500 runs, seed 11, realistic, v4):** Klee 57.6% / Furina
45.8% / real_ironclad 49.6% / ref_ironclad 22.0% — no 0%/100%. Boss split:
Lagavulin as modeled is the SOFTER boss (win-given-reached 94–97% vs
Vantom's 67–85%) because her anti-turtle teeth (player stat-drain, Plating)
sit on the §10.9 backlog — her sleep reads as free setup. Flagged: if she
should actually check turtling, the stat-drain op needs promoting (red-pen).

**Pass 2 SHIPPED 2026-07-23** (suite 585 green, frozen 0.525 anchor
untouched): the §10.2 engine ops — `inject` intent + engine status cards
(`tier0/engine/statuses.py`: Dazed = ethereal, Wound/Slimed = clogs, Burn 2
/ Wither 3 end-of-turn-in-hand blockable, Toxic 2-on-draw), enemy `heal`
intent, `on_ally_death` (implemented as a real once-latched trigger polled
at the survivor's turn start — the §10.2 "only if Kaiser is picked"
condition fired, so no approximation needed), and HP-threshold `phases`
(settled at every damage site; fatal-exempt until the last bar so Feed
cannot farm phase-downs). `act2_pool.yaml` (the Hive) registered with
easy_fights = 2. Act-1 cadence suites (shop/potion/relic/neow tests) pinned
to a single-act registry via autouse fixtures — the §10 re-stamp.

**Pass 3 SHIPPED 2026-07-23** (suite 586 green): `act3_pool.yaml` (Glory)
registered. Test Subject runs the phase op (100→200→300, 600 total);
Aeonglass runs Wither injection; Slimed Berserker injects 10 Slimed; Mecha
Knight puts 4 Burn in hand; Knight Gang ships aura-less.

**Pass 4 (metrics) SHIPPED 2026-07-23:** `run_metrics.act_funnel` + the CLI
funnel line (§10.6); `RunResult.n_acts/acts_completed` carry the per-act
segmentation.

**First 3-act signals (500 runs, seed 11, realistic):** overall Klee 0.8% /
Furina 0.2% / real_ironclad 0.6%; Klee funnel 58% clear act 1 → 8% clear
act 2 → 1% win. Loss anatomy (200 runs): ZERO stalls — every loss is a real
death — and **the Act-2 boss is the wall**: 32–33% of ALL runs die on that
one node (≈65–80% of arrivals), for every character. Read: act-2/3 boss
spikes (Laser 31, Knowledge Overwhelming 8x3 + the dot Curse) sit far above
the measured block ceilings (~17–21, burst_defense), so the A3×A4
burst-vs-sustain finding generalizes upward. What to do about it — pilot/
drafter act-awareness, per-act power cadence, roster-vs-battery levers — is
the difficulty-calibration conversation (red-pen), NOT unilateral tuning.

## 10.8.1 The Ironclad-0.6% diagnosis (2026-07-23, post-ship)

User challenge: an average A0 Ironclad player wins far more than 0.6%, so
the 3-act floor smells like sim error, not difficulty. Verdict: **confirmed
— the floor was mostly instrument artifact**, four causes, each measured on
200-run counterfactual arms (real_ironclad, seed 11, realistic):

1. **Boundary Rares missing (FIXED, v5).** §10.1 ratified "choice-of-3 Rare
   cards"; the implementation forced only the companion slot, so Ironclad
   (no companions) got plain commons at act transitions and nobody got the
   Rare cards. Rares were 4.6% of all card offers; Demon Form / Barricade
   effectively unobtainable. Fix: `roll_rewards(card_rarity=...)`, forced
   "rare" at non-final-boss screens. Alone: +0.5pp win, act-2 clears
   12%→15%.
2. **The Ancient energy class missing (FIXED: Prismatic Gem).** The real
   Act-2/3 Ancient pools carry THREE +1-energy-per-turn boons (Prismatic
   Gem / Blessed Antler / Philosopher's Stone) — the class that replaces
   STS1's energy boss-relics. The shipped 7-boon sample had none, so every
   character fought Acts 2–3 at a flat 3 energy. Counterfactual (+1 energy
   in acts 2–3, guaranteed): **0.5% → 11.5% win** — the single largest
   lever found. Shipped fix: Prismatic Gem on the existing
   `every_n_turns_energy` hook (its color-reward rider is faithfully a
   no-op in a single-character pool — the ratified 1:1 sampling rule);
   Antler (3 Dazed at combat start) and Stone (enemies +1 Str) need new
   hooks → §10.9. Pick-weight for the hook corrected 8→12 (a permanent
   engine outranks Cocoa's one-shot 4).
3. **Enemy counterplay skipped as "flavor" (RATIFIED + SHIPPED
   2026-07-23).** §4.3 skipped Bygone Effigy's Slow — but Slow is the
   fight's designed player counterplay (per-card damage amp). As shipped
   she was 127 HP × 23/turn with no non-attack beats: she killed **45% of
   the Ironclad runs that face her** (Byrdonis 5%, Gardener 20%) and act-1
   elites took 52% of ALL runs. Slow-proxy arm (127→104 HP ≈ +22% player
   damage): act-1 clears 48%→62%. SHIPPED as real engine ops (inert-by-
   default Enemy fields, battery never sets them): Slow 10 = "+10% damage
   from Attacks per card played this turn, the playing card counts itself,
   resets each turn" (wiki wording); Skittish 6 on the Gardener = "the
   first time it is hit each turn, it gains 6 Block" (post-resolution,
   per-turn latch). Tests in `tier0/tests/test_multiact_ops.py`.
4. **Run-layer discipline degeneracies (RATIFIED + SHIPPED 2026-07-23 —
   DRAFTER_VERSION 5).** Pick rate 99%: `DRAFT_DECK_SOFT_CAP = 22` could
   not fire in a one-act world (10 screens ⇒ ≤20 cards) and never re-tuned
   for 30 screens ⇒ 28–35-card decks at the act-2 boss. Lean-draft arm
   (stop non-power/block/tempo picks past 15): act-2-boss deaths
   32%→19–23%. Rest policy smithed in the 40–65% HP band while BOTH
   template rests sit directly before E and B — runs entered fatal elites
   at ~48/80 HP. Heal-first arm: act-1 deaths 52%→47%. SHIPPED: the lean
   gate in `assigned_policy` (draft.DRAFT_LEAN_CAP 15 /
   DRAFT_LEAN_BLOCK_CAP 20; adaptive unchanged pending its own
   measurement) and the pre-fight rest lookahead
   (C.REST_PREFIGHT_HEAL_THRESHOLD 0.90). Consequence: in this template
   both rests precede E/B, so rest-SMITHING now fires only on near-full
   arrivals — if smithing should matter again, that is a template or
   threshold conversation. Arms archived in scratchpad
   (`ic_counterfactuals.py`, `ic_rest_arms.py`, `ic_redpen_arms.py`).

All four together (proxies): **18.0% win, funnel 73%/57%/18%** — a
plausible dumb-pilot A0 shape. Remaining structural honesty items for the
calibration conversation: forced 2 elites/act with no pathing agency (the
real game lets weak decks skip elites), and no boss-relic tier at all.

**Shipped v5 numbers (500 runs, seed 11, realistic, fixes 1+2 only):**

| character | v4 win | v5 win (Wilson 95%) | v5 funnel | got Gem |
|---|---|---|---|---|
| real_ironclad | 0.6% | **5.4%** (3.7–7.7%) | 50%/17%/5.4% | 20% |
| klee | 0.8% | 1.2% (0.6–2.6%) | 58%/15%/1.2% | 24% |
| furina | 0.2% | 0.0% (0–0.8%) | 33%/3.2%/0% | 14% |
| ref_ironclad | — | 0.8% (0.3–2.0%) | 26%/4.8%/0.8% | 12% |

Read: the fidelity fixes moved the character with the deep real pool 9×
(rare powers + energy are exactly what his pool can cash), and barely moved
Klee/Furina — their 3-act result is still gated on the red-pen levers
(items 3–4 above) and, for Furina, her known act-1 elite floor (55% of runs
die on a1E; `furina-tier05-baseline.md`). Klee/Furina diagnosis is the
staged next step after ratification.

**Lever world (RATIFIED + SHIPPED 2026-07-23: items 3+4 above, plus
Furina's Burst to cost 0 by user ruling — the charged meter is the cost,
matching Klee's). 500 runs, seed 11, realistic:**

| character | v5 win | lever-world win (Wilson 95%) | funnel | got Gem |
|---|---|---|---|---|
| real_ironclad | 5.4% | 3.0% (1.8–4.9%) | 59%/20%/3.0% | 26% |
| klee | 1.2% | **6.2%** (4.4–8.7%) | 84%/34%/6.2% | 38% |
| furina | 0.0% | 0.0% (0–0.8%) | 34%/6.2%/0% | 14% |
| ref_ironclad | 0.8% | **4.8%** (3.2–7.0%) | 53%/24%/4.8% | 23% |

Read: Slow + the discipline pass fixed the act-1 elite wall for the
characters whose decks are commons-dense (Klee a1E deaths 155→53;
ref_ironclad 336→197) and Klee's funnel is now the healthiest in the
roster. real_ironclad's act-1 improved the same way (a1E 214→174, act-1
clears 50%→59%) but his WIN went 5.4%→3.0% (CIs overlap): the lean gate
past 15 cards admits only Powers/tempo/Block, which filters exactly his
rare attack payoffs (Bludgeon-class) — the measured arm's docstring said
"genuinely strong picks make the cut" but its code never implemented that
clause, and what shipped is the measured code. FLAG for red-pen: a
strong-pick escape hatch on the lean gate (e.g. rare payoffs above a
score bar are always eligible). Furina alone did not move — her a1E floor
(267/500) is character-shaped, not world-shaped; see the Furina
diagnosis (staged next).

## 10.8.2 The Furina-0% diagnosis (2026-07-23, lever world)

User hypotheses on her 3-act 0%: (H1) Fanfare cap too low; (H2) rares
overpriced for her energy-cheat access; (H3) the two true heals (Singer of
Many Waters 14 / Unheard Confession 8+6) are busted Rare sustain carrying
her vs chip; plus "bad rares + bad payoff lategame". Arms: 300 runs each,
seed 11, realistic, `furina_diagnosis.py` / `furina_skittish_arm.py`
(scratchpad).

**Verdict: every card-side lever measured NON-BINDING today — the floor is
an act-1 AoE wall plus zero rare exposure.**

| arm | win | funnel | rares/deck |
|---|---|---|---|
| baseline | 0.0% | 32%/5%/0% | 0.13 |
| cap100 (cap 30→60) | 0.0% | 32%/6%/0% | 0.13 |
| cheap_rares (−1 on cost≥2) | 0.0% | 34%/5%/0% | 0.17 |
| no_heals (both removed) | 0.3% | 34%/4%/0% | 0.17 |
| cap100+cheap | 0.0% | 34%/6%/0% | 0.17 |

Findings, in causal order:

1. **The Phantasmal Gardener swarm is her killer, and it is HERS, not
   Skittish's.** Died-given-faced: Gardener **54%** (Effigy 29%, Byrdonis
   8%). With Skittish removed: Gardener 34% — still her worst elite.
   Skittish (+20pp) sharpened a pre-existing wall: her starter has ZERO
   AoE, her only common AoE is 2-cost Undercurrent, and elites land at
   fights 4 and 6 while her plan is still assembling. Note the identity
   contradiction: her DECLARED elite axes are A4 4.3 / A6 4.2 — the
   1-act archetype-deck instruments measured a Furina that had already
   assembled; the run world's fight-4 Furina has not.
2. **Rares are statistically invisible, so H2/H3 cannot bind.** 0.13
   rares/deck; the true heals were drafted in act 1 in 0/300 runs (a1
   clear WITH heal 0/0, WITHOUT 32%) and removing them changed nothing.
   Rares are ~5% of offers and she dies at median fight 5-6; repricing
   (cheap_rares) lifted holdings only to 0.17. Their pricing is still a
   fair SHEET critique — her draftable-rare curve averages 1.93 vs Klee
   1.38 / real_ironclad 1.55, with three 3-costs and seven 2-costs, and
   her energy cheat is thin (Deep Breath exhausts; the refund lines are
   spotlight machinery) — but it is not what kills her today.
3. **The Fanfare cap clips 23% of generated Fanfare** (banked 59.6k of
   77.5k requested) — H1 is real at the meter level, but cap100 moved
   nothing: she dies before held-Fanfare payoffs matter.
4. **Drafter AoE blindness (structural, run layer).** `_static_power`
   counts `target: all_enemies` damage ONCE — no body-count term — so
   Undercurrent reads as 3.5/energy against a 4-body elite where its
   table value is ~4×7. The one lever that attacks finding 1 directly is
   valuing AoE (and/or cheap early AoE on the sheet); both are red-pen
   (drafter change = DRAFTER_VERSION bump; sheet change = card law).
5. **Acts 2–3 are a second, masked wall**: of the ~32% reaching act 2,
   ~70% die there (a2N+a2B), and 0 of 800 measured lever-world runs won.
   "Bad lategame payoff" cannot be cleanly measured until the act-1
   floor is fixed; re-instrument after.

Shipped from this pass (user ruling): her Burst `let_the_people_rejoice`
cost 2→0, matching Klee's — the charged meter is the cost. (No measurable
winrate effect at the current floor; correct on identity regardless.)

## 10.9 Skip backlog (ratified condition: track to fill in later)

Mechanics skipped or approximated by §10.2–10.4, kept as a living list so
later passes can promote them instead of rediscovering them:

- [ ] Stat-theft (The Lost / The Forgotten — enemies dropped; also Lagavulin
      Matriarch's Soul Siphon player-drain half, §10.5)
- [ ] Back Attack positioning (Kaiser Crab)
- [x] On-death partner trigger (Crab Rage) — SHIPPED Pass 2 as a real
      once-latched `on_ally_death` field (+6 Str, 99 block), not the
      approximation: Kaiser was picked, so §10.2's condition promoted it.
- [ ] Untargetable states: Burrow (Tunneler), Soar (Owl Magistrate — dropped)
- [ ] Card theft + flee (Thieving Hopper — dropped)
- [ ] Ethereal / Downgrade auras + Hex (Knight Gang — auras stripped)
- [ ] 99-stack scripted gimmicks (Queen — dropped; Terror Eel)
- [ ] Death-timer injection (The Insatiable's Frantic Escape — dropped)
- [ ] On-hit-triggered injection (Entomancer Personal Hive — made periodic)
- [ ] Every-N-cards cadence trigger (Aeonglass Withering Presence — made
      per-cycle)
- [ ] Pick-your-poison curse choice (Knowledge Demon — fixed Disintegration)
- [ ] Intangible (Test Subject P3), Artifact (several), Thorns (Spiny Toad —
      dropped), damage caps (Hard to Kill / Plating / Hardened Shell)
- [ ] Unblocked-damage-triggered injection (Test Subject P2 Wounds — made
      per-turn)
- [ ] Enemy self-stun (Bowlbug Dizzy — shipped as an idle block-0 beat),
      slime split
- [x] **Slow (Bygone Effigy) + Skittish (Phantasmal Gardener)** — SHIPPED
      2026-07-23 (red-pen ratified) as real per-card-played engine ops on
      inert-by-default Enemy fields (§10.8.1 item 3); the §4.5 "flavor"
      label was the mislabel. Tests in test_multiact_ops.py.
- [ ] Ancient energy-boon riders: Blessed Antler (3 Dazed into draw pile at
      combat start — Dazed exists since Pass 2; needs a combat-start
      status-inject relic hook) and Philosopher's Stone (all enemies +1
      Str at combat start — needs an enemy-side relic hook). Prismatic Gem
      shipped (§10.8.1 item 2).
- [ ] Buff-ALL-enemies (The Obscura's Wail — shipped as its self half only)
- [ ] Block-an-ally (Fabricator's Guardbot — bot dropped from the wave)
- [ ] Slimed's "1: exhaust" self-removal (shipped as a plain clog)
- [ ] Minor unmodeled powers met in Acts 2–3: Imbalanced, Ringing, Paper
      Cuts, Stock, Galvanic, Enrage (Test Subject P1), Rampart-as-power
      (shipped as an opener block beat), random-no-repeat move AI
      (Soul Nexus — shipped as a fixed cycle)
- [ ] Player stat-drain, again: Lagavulin's Soul Siphon half is why she
      measures SOFTER than Vantom (Pass-1 sanity) — promoting it is the
      single highest-leverage backlog item for boss identity

Dropped-enemy re-add list (each unlocks when its backlog op lands):
Thieving Hopper, Spiny Toad, Slumbering Beetle (Act 2); Owl Magistrate,
The Lost + The Forgotten (Act 3); The Insatiable, Queen (bosses).

