# S18 — joined enemy-feasibility matrix

> **This decides nothing.** One row per mapped encounter, joining the four S18
> files into a single ordered read, with the socket columns resolved against
> S13's finished probe. It makes **no mapping verdict**, ranks no Genshin
> candidate, changes no existing ordering, and grades nothing. Where the four
> source files disagree I reconcile and cite both, never silently pick.

- **Date:** 2026-08-27. **Primary checkout:** `223a4ff` (per `PREFLIGHT.md`),
  read-only. **Game read:** Slay the Spire 2 **v0.107.1**
  (`docs/current/STATE.md:157`). No game launched, nothing deployed.
- **Sources joined** (all in `review/dispatch3/`): the four S18 files —
  `s18-enemy-feasibility/s18-act1.md`, `…/s18-act2.md`, `…/s18-act3.md`,
  `…/s18-bosses-elites.md` — resolved against **`s13-engine-sockets.md`**.
- **What is new here and only here:** the socket resolution (§1), the
  cross-cutting counts a single act file could not see (§3), the coverage
  reconciliation against the gallery's own row count (§4), and the deduped
  [USER] question list (§5).

---

## 0. How to read a row

| Column | Means |
|---|---|
| **#** | Stable row id: `A1-1…` act-1 normals, `A2-…`, `A3-…`, `E1…E22` elites/bosses, `U-…` Underdocks. |
| **Encounter** | The gallery row (`docs/current/dossiers/remap/reskin-gallery.md`). |
| **Bodies / rigs** | On-screen bodies, then the number of distinct **Spine skeletons** the row actually pays for. These differ often, and that difference is the single most useful number in the table. |
| **Clips** | Animation clips the C# **drives**. Where a source file also counted clips present-but-undriven in the rig, that is shown as `driven (+undriven)`. |
| **Cx** | S / M / L on the shared scale (`s18-act2.md` §3 wording; see §3d). |
| **The contract that costs** | The one thing that makes the row more than a rig — the reason for the letter. |
| **Sim** | `SHIPPED` = modelled in a `tier05` pool · `DROPPED` = on the re-add list · `RESEARCH` = base-game-live but not in any pool · `UNMAPPED` = no engineering read. |
| **Gallery** | Candidate density as the gallery records it (`S` strong / `P` plausible / `X` stretch), plus its own flags. **⚑RP** = on the §1 redesign-pressure list. **⚑AU** = carries a §4 art-unsafe warning. **⚑FC** = one of the three encounters gallery §5 says needs a family-coherent multi-body pick. **⚑DB** = a candidate on this row is double-booked (§5). |
| **Sockets** | **Row-specific** keys only. `S1`, `S2` and `S3` bind **every row** and are stated once in §1 rather than repeated 60 times. Marks: **✓** S13 settled it OPEN · **◐** S13 settled part of it · **○** S13 did not answer it. |
| **Src** | Which file owns the row: `a1` `a2` `a3` `BE` (bosses/elites). |

---

## 1. Socket resolution after S13

**The three universal keys.** Every one of the 60 rows below depends on these,
so they are not repeated per row:

| Key | Question | Status after S13 | Evidence |
|---|---|---|---|
| **S1 ✓** | Register a **hostile** `MonsterModel` + `EncounterModel` into an act's pool | **OPEN.** `S13-a1` (BaseLib `CustomMonsterModel` self-registers via `ModelDb::Inject`), `S13-b1` (`CustomEncounterModel`), and decisively **`S13-b2`** — BaseLib enumerates every `ActModel` subtype, base and modded, and postfixes `GenerateAllEncounters`. That dissolves the "`GenerateAllEncounters` returns a fixed array" objection all three act files raised (`s18-act1.md:212`, `s18-act2.md:266`, `s18-act3.md:240`). S13 also settles hostile-vs-summon: it is the **side**, not the type. | `s13-engine-sockets.md` §3, §0 |
| **S2 ◐** | Ship a mod `creature_visuals` scene **+ Spine rig** and have the engine resolve it | **SPLIT.** *Scene half OPEN:* `S13-a4` (`VisualsPath`, `protected virtual`, already Harmony-patched by BaseLib; the recommended seam because the preloader reads it too), `S13-a5` (`CreateVisuals`, coarser), `S13-g6` (`NodeFactory` binds a mod `.tscn` to the game's C# node type; `NCreatureVisualsFactory` will generate the missing contract nodes and build a full `NCreatureVisuals` **from one `Texture2D`**). *Spine half still UNKNOWN:* S13 read no Spine import path and states the practical minimum under BaseLib is **one image, not a rig**. **⚠ Trap `S13-g4`:** Godot's pack loader replaces colliding `res://` paths, so shipping the base path inside a mod pck overwrites the base scene **globally**. | `s13-engine-sockets.md` §3, §4.5, §6 |
| **S3 ◐** | Supply the **FMOD** events the id-derived SFX paths demand | **HALF.** `S13-a7` OPEN (base) — the `AttackSfx`/`CastSfx`/`DeathSfx` getters are patchable, so **overriding the string** is proven. **Supplying bank content is not**: S13's own note is "replacing one needs an FMOD bank, not a file", it found no bank-adding mechanism, and it could not even enumerate the base game's own event inventory (`Master.strings.bank` yields no plaintext). **This is the least-answered key and it touches all 60 rows** — exactly what `s18-act1.md:214` and `s18-act3.md:242` predicted. | `s13-engine-sockets.md` §3 |

**Row-specific keys.**

| Key | Question | Status | Note |
|---|---|---|---|
| **S1b ⚠** | …and a **boss** specifically, into a base act's `BossDiscoveryOrder`? | **NARROW.** `S13-b3`: `BossDiscoveryOrder` is a plain virtual getter on the *act*, so changing a base act's boss order needs a patch on that act type rather than the pool postfix — **and BaseLib does not exercise it**. Binds all 12 boss rows. | `s13-engine-sockets.md` §3 |
| **S4 ✓** | Encounter scene with named body slots (`HasScene = true`) | **OPEN.** `S13-b4` — BaseLib's `CustomEncounterModel` carries three nested Harmony patch classes over `ScenePath`, `HasScene`, `Slots`, `ExtraAssetPaths` and `CreateBackgroundAssetsForCustom`; slots are read off `Marker2D` children. Corroborated by the shipped scenes: `pck:scenes/encounters/knights_elite.tscn` is three `Marker2D`s and nothing else. | 17 rows |
| **S5 ○** | Spine **skins** — the `normal`/`phobia` accessibility contract and runtime composed skins | **PROVISIONAL. S13 has no skin key.** Its only touch is §5.4 Q4, which frames a missing `%PhobiaModeVisuals` as a *scope* question ("silently ignores the accessibility toggle"), not a capability answer. | 11 rows |
| **S6 ◐** | Custom script node inside a creature-visuals scene receiving **Spine animation events** | **PARTIAL.** `S13-g6` proves the *binding* half (`SceneConversionPatch` + `NodeFactory`). It does **not** cover Spine events, and S13 flags its own limit: it read `NCreatureVisualsFactory`'s declaration logic but **not** `NodeFactory::ConvertScene`'s body, so "whether conversion reparents/retypes arbitrary children correctly for a hand-built scene is untested here" (§4.5). **28 rows depend on this — the most load-bearing partially-answered key in S18.** | 28 rows |
| **S7 ○** | Nested child `SpineSprite` inside a `SpineSlotNode` of a parent skeleton | **PROVISIONAL. No S13 key.** | 1 row |
| **S8 ○** | Multiple named `BoundsContainer`s swapped by `AnimState` | **PROVISIONAL. No S13 key.** S13 §4.3 lists `%Bounds` as a hard-fail required node and says nothing about alternates. | 4 rows |
| **B1 ○** | Boss **map-node** art (`BossNodePath` / `BossNodeSpineResource`) | **PROVISIONAL — strong analogy, untested.** Both are `virtual`; shape-identical to `S13-a4`. New in `s18-bosses-elites.md` §6b. | 12 rows |
| **B2 ○** | Boss **custom background**: `HasCustomBackground` + a **`DirAccess`-enumerated** `res://scenes/backgrounds/<encounter-id>/layers` directory that **throws** if absent | **PROVISIONAL — hook OPEN via `S13-b4`, `DirAccess`-over-mod-PCK UNKNOWN, and the failure is hard.** New in `s18-bosses-elites.md` §6b. | 11 rows (all bosses but Aeonglass) |
| **B3 ○** | Boss **music**: `CustomBgm` event + `NRunMusicController.UpdateMusicParameter` (+ `SfxCmd.SetParam`) | **PROVISIONAL.** No S13 audio key beyond `S13-a7`; inherits S3's bank NON-FINDING and adds a parameter graph on top. | 11 rows (all bosses but Lagavulin Matriarch, which ships neither) |
| **B4 ○** | Exact-node-**path** contracts: `GetSpecialNode<T>` from the model (**soft**, returns null) and `GetNode<T>` from the driver (**hard**, throws) | **PROVISIONAL.** Adjacent to `S13-g6` but a different question — this is node names, paths and types *inside* the scene, after binding. | 9 rows |
| **B5 ○** | **Layered Spine track** — `SetAnimation("[_]tracks/<name>", loop, 1)`, including a runtime-computed index | **PROVISIONAL. No S13 key.** §4.2 lists skins but does not distinguish track-1 animation from skins. | 5 rows |
| **B6 ○** | Driver keyed on **animation start by clip name** (`ConnectAnimationStarted`) | **PROVISIONAL. No S13 key.** Same family as S6. | 6 rows |

**Two S13 findings that change how every row should be read.**

1. **A non-Spine body is a fully supported state end to end** (`s13-engine-sockets.md` §4.4): no animator is built, animation triggers no-op, the death fade sizes itself off the hitbox `Control`, and everything mechanical survives. **Row E21 (Aeonglass) is the base game shipping exactly that, for a boss.** That is a technical floor, not an endorsement — see `s18-bosses-elites.md` §7.
2. **There is no public API to replace a base monster's art** (`s13-engine-sockets.md` §5.1 #4). The seam is a Harmony patch on an engine member. **Nothing below was executed** — S13's standing blocker holds, and its own recommendation is that the first runtime evidence come from the offline Harmony bite-check, not a deploy.

---

## 2. The joined matrix

### 2a. Act 1 — Overgrowth / Underdocks-imported (15 gallery rows)

| # | Encounter | Bodies / rigs | Clips | Cx | The contract that costs | Sim | Gallery | Sockets | Src |
|---|---|---|---|---|---|---|---|---|---|
| A1-1 | **Nibbit** (`NibbitsNormal` 2 · `NibbitsWeak` 1) | 2 bodies / **1 rig** | 5 | **S** | Nothing bespoke. A 371 B encounter scene with two named slots is the only extra. | SHIPPED | 6 cand, top **S**; ⚑DB (Whopperflower ×6+) | S4 ✓ | a1 |
| A1-2 | **Inklets ×3** | 3 / **1** | 6 | **S** | One extra clip (`attack_fast`) over default; body count is free. Spawn `SlipperyPower` must read. | SHIPPED | **7 S + 2 P** — "the most-claimed swarm slot" | — | a1 |
| A1-3 | **Leaf / Twig Slimes** | 4 / **4** | 5 each | **L** | Four rigs; `spit_target` bone on both mediums; **`TwigSlimeM` needs Spine skins named exactly `normal`/`phobia`**. | SHIPPED | top **S**, "close to unlosable"; ⚑DB | S5 ○ | a1 |
| A1-4 | **Mawler** | 1 / **1** | 5 | **S** | Nothing at all. The cheapest normal in Act 1. | SHIPPED | 8 cand, **4 S** | — | a1 |
| A1-5 | **Fogmog + Eye With Teeth** | 2 / **2** | 5 + 3 | **L** | Second rig (183 KB) used by **exactly one** encounter, plus `NFogmogVfx` on 2 named slots driven by `thrust_start`/`thrust_end`. | SHIPPED | 2 S + 3 P; ⚑DB | S4 ✓ · S6 ◐ | a1 |
| A1-6 | **Sewer Clam** | 1 / **1** | 5 (+2) | **L** | `NSewerClamVfx` + named bone `scale_adjuster` + slot `clam_particles_attach` + **5 named Spine events** — the tightest art-to-code contract of any Act-1 normal. | SHIPPED | 3 S + 5 P; **⚑AU** (Plating cap skipped) | S6 ◐ | a1 |
| **E1** | **Byrdonis** (elite) | 1 / **1** | 5 | **S** | Nothing bespoke. **The cheapest elite in the game.** | SHIPPED | 8 cand, **6 S** — the atlas's most crowded silhouette; ⚑DB (Red Vulture ↔ Owl Magistrate) | — | BE |
| **E2** | **Bygone Effigy** (elite) | 1 / **1** | 5 | **M** | One named attach node (`Visuals/SpineBoneNode`). Smallest skeleton of any elite or boss (34 256 B) on a 628 KB sheet. | SHIPPED | 7 cand, **2 S**; ⚑DB (Ruin Guard ×3) | B4 ○ | BE |
| **E3** | **Phantasmal Gardener ×4** (elite) | 4 / **1** | **10** | **L** | `NPhantasmalGardenerVfx` (2 events) **+** a **slot-dependent** `tall`/`short` skin **+** a 4-slot encounter scene. `Hit` branches on whether the shield already fired this turn. | SHIPPED | **9 cand, 8 S** | S4 ✓ · S5 ○ · S6 ◐ | BE |
| **E4** | **Vantom** (boss) | 1 / **1** | 9 | **L** | `NVantomVfx`, 4 emitters + a shader slot, **6 named events**; layered track `_tracks/charge_up_1`→`charged_1`; music param `vantom_progress`; background is only **3 layers**. | SHIPPED | 8 cand, **1 S**; **⚑AU** (Slippery). **Weekly layer: Andrius** | S1b ⚠ · S6 ◐ · B1 ○ · B2 ○ · B3 ○ · B4 ○ · B5 ○ | BE |
| **E5** | **Lagavulin Matriarch** (boss) | 1 / **1** | 9 | **L** | Named `%SleepVfxPos` marker with a code-managed shared VFX; layered track `_tracks/eyes_closed_loop`; dual sleep/awake clip set. **No `CustomBgm`, no music parameter** — the only boss with neither. Background is **14 layers**. | SHIPPED | 6 cand, 2 S; **[USER]-LOCKED PICK**; **⚑AU** ×2. **Weekly layer: Magatsu Narukami ⚑** | S1b ⚠ · B1 ○ · B2 ○ · B4 ○ · B5 ○ | BE |
| **E6** | **Ceremonial Beast** (boss) | 1 / **1** | **11** | **L** | `NCeremonialBeastVfx`, **5 events and the only camelCase event set in the game**; `Hit` branch-wired **14×**; scene 69 046 B; **two dedicated animated Spine background rigs**; a **real Spine map node**. | **RESEARCH** | 4 cand, **3 S**. No weekly layer | S1b ⚠ · S6 ◐ · B1 ○ · B2 ○ · B3 ○ | BE |
| **E7** | **The Kin** (boss) | 3 / **2** | 6 + 6 | **L** | Three drivers (`NKinPriestVfx` 3 events, `NKinPriestBeamVfx` reached by node path from C#, `NKinFollowerVfx` 5 events); random `hair_1/2/3` skin; 3 slots; **SFX namespaces `the_kin_priest` + `the_kin_minion`, and the follower's hurt borrows the priest's**. | **RESEARCH** | 3 cand, **all S**. No weekly layer | S1b ⚠ · S4 ✓ · S5 ○ · S6 ◐ · B1 ○ · B2 ○ · B3 ○ · B4 ○ | BE |
| **E8** | **Waterfall Giant** (boss) | 1 / **1** | 10 | **L** | **The heaviest event contract in the game**: `NWaterfallGiantVfx` makes **12 hard node lookups** and switches on **15 named Spine events**; a **runtime-indexed** layered track `_tracks/buildup{1..3}`; a parameter on its own ambient event. Background is only **2 layers**. | **RESEARCH** | **⚑RP** — 1 claimant, **element inverted**. No weekly layer | S1b ⚠ · S6 ◐ · B1 ○ · B2 ○ · B3 ○ · B5 ○ | BE |
| **E9** | **Soul Fysh** (boss) | 1 / **1** | **13** | **L** | A complete intangible sub-body (own hurt, own death, own loop); `NSoulFyshVfx` on two `MegaSlotNode`-wrapped nodes, 4 events; **two** music parameters. Background is **14 layers**. | **RESEARCH** | **⚑RP — zero candidates in any of the 16 families**, and no weekly layer. **No candidate from either gallery.** | S1b ⚠ · S6 ◐ · B1 ○ · B2 ○ · B3 ○ | BE |

### 2b. Act 2 — the Hive (19 gallery rows)

| # | Encounter | Bodies / rigs | Clips | Cx | The contract that costs | Sim | Gallery | Sockets | Src |
|---|---|---|---|---|---|---|---|---|---|
| A2-1 | **Bowlbug pod** (Rock + 2 of {Egg, Silk, Nectar}) | 3 / **1 rig, 4 skins** | 9/5/6/5 | **L** | One skeleton with four 18-region skin sets, a `spit_target` bone, a 2-slot encounter scene, **and `bowlbug_egg` nests a second skeleton (`tough_egg`) inside slot `items`**. | SHIPPED | top **S** ×2; **⚑FC** — needs a family-coherent multi-body pick | S4 ✓ · **S7 ○** | a2 |
| A2-2 | **Bowlbug (Nectar)** | (in A2-1) / **skin only** | 6 | **S** | Nothing new — it is one more 18-region skin on a rig A2-1 already pays for. Read alone it is not a body. | RESEARCH (sim) / live (base) | 2 S + 2 P; must match A2-1's family | — | a2 |
| A2-3 | **Exoskeletons ×3 / ×4** | 4 / **1** | 7 | **M** | One extra: a 4-slot encounter scene. Body count is free. Rig carries an **unconsumed** `spray_start`/`spray_end` + `clip_target_slot` contract. | SHIPPED | **6 cand, 5 S** — best-supplied row in Act 2; **⚑AU** (Hard to Kill) | S4 ✓ | a2 |
| A2-4 | **Chompers ×2** | 2 / **1** | 5 | **S** | Nothing. The cheapest row in Act 2. Spawn `ArtifactPower` 2 must read. | SHIPPED | **1 cand, S, uncontested** | — | a2 |
| A2-5 | **Thieving Hopper** | 1 / **1** | **11** | **L** | **Three** bounds containers (`Bounds`/`GroundedBounds`/`FlyingBounds`), two named bones, a marker the code parks the stolen card on, and every tell duplicated grounded/airborne. | **DROPPED** | 5 cand, **3 S** | **S8 ○** | a2 |
| A2-6 | **Tunneler** | 1 / **1** | **12** | **M** | One named bone — but the letter understates it: a complete **burrowed sub-body** (`hidden_loop`, `hidden_attack`, `hidden_die`). | SHIPPED | **9 cand, all S** — "the most-contested body in the atlas"; **⚑AU** ×2 | — | a2 |
| A2-7 | **Hunter Killer** | 1 / **1** | 6 | **L** | `NHunterKillerVfx` on bone `mouth`, gated by named events `spit_start`/`spit_end`. | SHIPPED | 7 cand, **3 S** | S6 ◐ | a2 |
| A2-8 | **Louse Progenitor** | 1 / **1** | 9 | **M** | A **branched** curled sub-graph with its own idle and its own death and **no hurt at all** — a state-machine obligation, not an asset one. | SHIPPED | 5 cand, **3 S**; **⚑AU** (Curl Up) | — | a2 |
| A2-9 | **Mytes ×2** | 2 / **1** | 6 | **L** | `NMyteVfx` re-parks a `projectile_target` bone 150 px above the chosen target on the event `start_cast`; the encounter also overrides the camera. | SHIPPED | 4 cand, **2 S** | S4 ✓ · S6 ◐ | a2 |
| A2-10 | **Ovicopter + Tough Eggs** | up to 4 / **2** | 7 + 9 | **L** | Two rigs, **three** scenes on them, a random `egg1`/`egg2` skin, a **two-phase** egg→hatchling clip set on one rig, a 6-slot encounter scene, and a cross-row rig dependency into A2-1. | SHIPPED | 6 cand, **2 S**; **⚑AU** (eggs never hatch in sim) | S4 ✓ · S5 ○ | a2 |
| A2-11 | **Slumbering Beetle** | **3** (with 2 bowlbugs) / **1 + A2-1's** | 9 | **L** | Three extras: a named bone, a code-managed shared-VFX lifecycle on a marker, and a dual sleep/awake set with its own death. **The base encounter drags A2-1's family in with it.** | **DROPPED** | 9 cand, **5 S**; **⚑AU** (Plating 15) | S4 ✓ | a2 |
| A2-12 | **Spiny Toad** | 1 / **1** | 9 | **L** | `NSpinyToadVfx` gated on the event `explode`, **on top of a whole second "naked" body state** — the Thorns tell is a body change, not an icon. | **DROPPED** | **⚑RP** — 6 cand, **none strong**; "Thorns-as-retaliation has no clean Genshin analogue" | S6 ◐ | a2 |
| A2-13 | **The Obscura + Parafright** | 2 / **2** | 9 + 9 | **L** | Two rigs, two bespoke drivers on named slots driven by `particles_start`/`particles_end`, **plus the only phobia *skin* among Act-2 normals**; every Obscura tell exists twice, before and after it summons. | SHIPPED | 5 cand, **1 S** (thin); **⚑AU** (Wail's party half) | S4 ✓ · S5 ○ · S6 ◐ | a2 |
| **E11** | **Decimillipede** (elite) | 3 / **3 + a prop rig** | 5 (shared) | **L** | **No attack clip exists** — the attack routes through `GetSpecialNode<NDecimillipedeSegmentDriver>` at four exact node paths. Three subclasses exist *only* to resolve three `VisualsPath`s (the class comment says so). **Six id-derived phobia textures** swapped at runtime. | SHIPPED | **⚑RP, top of the list** — only claim is a self-declared stretch; **Reattach has no analogue in any of the 16 families** | S4 ✓ · S5 ○ · S6 ◐ · B4 ○ | BE |
| **E12** | **Entomancer** (elite) | 1 / **1** | 6 | **L** | `NEntomancerVfx` drives a tweened swarm across the arena on `launch_swarm`/`turn_off_swarm`. Phobia is a texture whose filename **inverts** the Decimillipede's convention (`phobia_<id>`). | SHIPPED | **⚑RP** — 2 cand, **neither strong**, both inverted-incentive | S5 ○ · S6 ◐ | BE |
| **E13** | **Infested Prism** (elite) | 1 / **1** | 7 | **S** | Nothing bespoke. Bare 4-node scene. **The only S-grade elite in Act 2.** SFX namespace `infested_prisms` (plural) is not the id. | SHIPPED | **6 cand, 5 S** — "pick by which family anchors Act 2's elites" | — | BE |
| **E14** | **Knowledge Demon** (boss) | 1 / **1** | **11** | **L** | `NKnowledgeDemonVfx`: **8 hard lookups, 8 named events, plus `ConnectAnimationStarted` on clip `idle_loop`**; a burnt second body state with its own hurt and death; the 2nd-largest skeleton and 2nd-largest scene in the game. | SHIPPED | **⚑RP** — 2 cand, neither strong; one is retired event content. **Weekly layer: Shouki no Kami — the one slot both galleries agree the weekly layer is stronger** | S1b ⚠ · S6 ◐ · B1 ○ · B2 ○ · B3 ○ · **B6 ○** | BE |
| **E15** | **Kaiser Crab** (boss) | 2 / **1 skeleton** | 5 + 5 | **L** | **Two bodies on one rig** across **four texture pages (3.3 MB — the largest texture budget in the game)**; `NKaiserCrabBossVfx` 9 lookups / 11 events / `ConnectAnimationStarted`; one SFX namespace split `_left_`/`_right_`; the most aggressive camera override in the roster. | SHIPPED | 5 cand, **3 S**. **Weekly layer: La Signora "under protest" — ⚑ the fork lands atlas-side here on merit** | S1b ⚠ · S4 ✓ · S6 ◐ · B1 ○ · B2 ○ · B3 ○ · B6 ○ | BE |
| **E16** | **The Insatiable** (boss) | 1 / **1 + a real map-node rig** | 10 | **L** | `NTheInsatiableVfx` 7 events + `ConnectAnimationStarted`; a two-phase body branching on `HasLiquified`; **the only monster encounter in the game with an `AmbientSfx` override**; the **largest phobia texture on any monster in the game** (1.3 MB); a clip name that is also a bestiary data key. | **DROPPED** (but **first** in `Hive::BossDiscoveryOrder`) | 5 cand, **2 S**. No weekly layer | S1b ⚠ · S5 ○ · S6 ◐ · B1 ○ · B2 ○ · B3 ○ · B6 ○ | BE |

### 2c. Act 3 — Glory (18 gallery rows, 17 matrix rows)

| # | Encounter | Bodies / rigs | Clips | Cx | The contract that costs | Sim | Gallery | Sockets | Src |
|---|---|---|---|---|---|---|---|---|---|
| A3-1 | **Devoted Sculptor** | 1 / **1** | 5 | **L** | The animator is the cheapest possible, but `NDevotedSculptorVfx` sits on bone `voice_attach` and is driven by named events `caw` and `attack`. | SHIPPED | 6 cand, **4 S** | S6 ◐ | a3 |
| A3-2 | **Scrolls of Biting ×3 / ×4** | 3–4 / **1** | 6 | **M** | One extra: a **random `skin1`/`skin2`** per copy, so the bodies on screen visibly differ — a reskin must ship two skins. | SHIPPED | 1 S + 5 P — the consolation swarm slot | S5 ○ | a3 |
| A3-3 | **Living Shield + Turret Operator** | 2 / **2** | 5 + 5 | **M** | A second rig — and a relationship: Rampart pumps Block onto every living **`TurretOperator`**, filtered **by monster type**, so splitting the pair across families breaks the encounter's whole point. `HasDeathSfx => false` on the shield. | SHIPPED | **10 cand, 8 S — "the most-claimed encounter in the atlas"**; **⚑FC** | — | a3 |
| A3-4 | **Axebot** | 1 body ×3 sequential / **1** | 7 | **L** | `NAxebotVfx` is itself a `SpineSprite`, on 2 named slots + 1 named bone, driven by **5 named events**; plus a `respawn` clip on a **custom** trigger (not the engine's `revive`). | SHIPPED | 6 cand, **5 S**; **⚑AU** (2 Stock) | S4 ✓ · S6 ◐ | a3 |
| A3-5 | **Construct gang** (Punch + 2 Cubex) — *gallery rows `:61` + `:62` joined* | 3 / **2** | 6 + **11** | **L** | Two rigs; `NCubexConstructVfx` on bone `laser_attach` driven by `laser_start`/`laser_end`; a **9-combination** composed skin (3 eyes × 3 moss); **three** bounds containers; **and both bodies also headline Act-1 solo encounters, so a reskin repaints Act 1.** | SHIPPED | Punch 2 S + 4 P, Cubex 2 S + 5 P; **⚑FC**; ⚑DB (Ruin Guard) | S4 ✓ · S5 ○ · S6 ◐ · S8 ○ | a3 |
| A3-6 | **Fabricator + 4 bots** | 5 / **5** | 6 + 5×4 | **L** | Five rigs, and **every bot scene must expose two exactly-named bones** (`height_constrainer`, `height_bone`) or the fall-in silently misplaces. No bespoke `N…Vfx` anywhere. | SHIPPED | 4 S + 3 P — "the single most exact minion pairing in the atlas" | S4 ✓ · B4 ○ | a3 |
| A3-7 | **Frog Knight** | 1 / **1 composite** | 7 (+2) | **M** | No attach contract and no events — it misses **S** only on clip count and on being a **rider-plus-mount composite** (29 of 59 atlas regions are the beetle), so a reskin must design two silhouettes that fit together. | SHIPPED | 3 S + 6 P; **⚑AU** (Plating cap) | — | a3 |
| A3-8 | **Globe Head** | 1 / **1** | 5 (+**14**) | **S** | Nothing driven — but the rig ships a **14-clip apron/cloth system** the code never names, so a like-for-like rig is heavier than the letter. | SHIPPED | **9 cand, most S** — "second-most-contested row, can be assigned last"; **gallery §3 silhouette flag NOT RESOLVED** (partly answered in `s18-act3.md` §7) | — | a3 |
| A3-9 | **Slimed Berserker** | 1 / **1** | 6 | **L** | `NSlimedBerserkerVfx` on **three** named slots driven by **4 named events** — and neither attack uses a hit-VFX scene at all: the goo emitters *are* the impact feedback. | SHIPPED | 2 S + 1 P + 1 X | S6 ◐ | a3 |
| A3-10 | **Owl Magistrate** | 1 / **1, 2 pages** | 9 | **M** | A **second complete body state** — airborne, with its own hurt, its own death, its own bounds container and its own SFX overrides — hand-wired as a per-state graph, not any-state triggers. The heaviest M in Act 3. | **DROPPED** | 3 S + 1 P + 1 X; ⚑DB (Red Vulture ↔ Byrdonis) | S8 ○ | a3 |
| A3-11 | **The Lost + The Forgotten** | 2 / **2** | 5 + 5 | **L** | Two rigs **sharing one driver, one clip vocabulary and one byte-identical second atlas page** — the base art independently corroborates the gallery's "one silhouette in two colorways" note. 4 named slots, events `start_dust`/`stop_dust`. | **DROPPED** | 3 S + 1 P + 2 X | S6 ◐ | a3 |
| **E17** | **Knight Gang** (elite) | 3 / **3** | 6 + 6 + 6 | **L** | Three rigs of wildly unequal cost: the flail knight is the **bare 5-node contract** (an S body), the spectral knight carries a driver with 2 events + `ConnectAnimationStarted`, the magi knight a named `AttackDistanceControl` bone. **The only elite or boss in the game with an `EncounterTag`.** | SHIPPED **aura-less** | 6 cand, **4 S** | S4 ✓ · S6 ◐ · B4 ○ · B6 ○ | BE |
| **E18** | **Mecha Knight** (elite) | 1 / **2** (a VFX-only Spine rig) | 9 | **L** | A second, VFX-only Spine rig for the shield; `NMechaKnightVfx` 6 lookups / 4 events; **`Hit` branch-wired 14×** across a paired wound state (`idle_loop_wound`, `hurt_wound`). 63 atlas regions — the most of any Act-3 body. | SHIPPED | **9 cand, 5 S — "deepest strong bench in the atlas"**; **⚑AU** (Artifact 3); one candidate carries a **factual element mismatch** (`:116`) | S6 ◐ | BE |
| **E19** | **Soul Nexus** (elite) | 1 / **1** | **5 (default)** | **L** | **The widest split in the roster:** the cheapest animator of any elite or boss, on top of a layered track `tracks/writhe`→`tracks/empty` and `NSoulNexusVfx` driving three `Line2D` trails and a shader-driven head fire off **8 named events**. | SHIPPED | 4 cand, **2 S** — "gimmick-free stat block: donor body is a free pick" *(true of the animator half only)* | S6 ◐ · B5 ○ | BE |
| **E20** | **Test Subject** (boss) | 1 / **3** | **23** | **L** | **The largest single art contract in the game**: a 1.16 MB skeleton, a 139 KB / 30-node scene, three numbered phase variants with every trigger registered three times, two `BoundsContainer` overrides, and a driver making 11 hard lookups (six escaping the subtree) with 10 events **plus** clip-name hooks. | SHIPPED | 4 cand, **1 S**; gallery §3 **upgrades** the Prism Slime claim. **Weekly layer: Guardian of Apep — ⚑ fork lands atlas-side on merit** | S1b ⚠ · S6 ◐ · S8 ○ · B1 ○ · B2 ○ · B3 ○ · B4 ○ · B6 ○ | BE |
| **E21** | **Aeonglass** (boss) | 1 / **0 — no Spine rig exists** | **0 driven** | **S†** | **There is nothing to reskin against.** A 5-node scene whose `%Visuals` is a plain `Sprite2D` on `hourglass_placeholder.png`, root node still named `Doormaker`; no animator is ever built; the only boss with **no custom background**; its BGM and its music parameter are **borrowed from the Queen**. | SHIPPED | 4 cand, **1 S — "the strongest single boss argument in the atlas"**. **Weekly layer: Lord of Eroded Primal Fire — ⚑ fork lands atlas-side on merit** | S1b ⚠ · **S2 is the non-Spine case S13 §4.4 describes** · B1 ○ · B3 ○ | BE |
| **E22** | **Queen + Torch Head Amalgam** (boss) | 2 / **2** | 5 + 5 | **L** | **The most exacting node contract in the game, and it is on the *minion***: a 64 KB / 39-node amalgam scene with three fully mirrored torch sub-trees, `NAmalgamVfx` making **12 hard lookups** over **10 named events**, and the model reaching four more exact paths, three of them four levels deep. The Queen adds a layered `tracks/writhe` and a clip-name hook. | **DROPPED** | **⚑RP — zero claims across all 16 families**, and no weekly layer. **No candidate from either gallery.** | S1b ⚠ · S4 ✓ · S6 ◐ · B1 ○ · B2 ○ · B3 ○ · B4 ○ · B5 ○ · B6 ○ | BE |

### 2d. Underdocks — Act 1 alternate (9 gallery rows)

Research-only. **One row is costed (E10); the other eight are not**, and the
reason is ownership, not judgement: `s18-act1.md` scoped itself to the gallery's
"ACT 1 — Overgrowth" and "ACT 1 boss pool" headers (`s18-act1.md:159-160`), so
no S18 agent was assigned the Underdocks block's normals. **This is the one
coverage gap in S18 and it is recorded, not papered over.**

| # | Encounter | Status | Note |
|---|---|---|---|
| **E10** | **Skulking Colony** (elite) | **COSTED — `s18-bosses-elites.md` §2a** | 1 rig / 7 clips / **L**. **The only elite or boss in the game with a phobia *skin*** (`HasPhobiaSpineSkin => true`, one of five overrides in the assembly); `NSkulkingColonyVfx` on 3 slots with 3 named events; spawn `HardenedShellPower` 20. Gallery: **1 candidate, rated P — the thinnest coverage of any elite in the atlas.** Sockets: S5 ○ · S6 ◐ |
| U-1 | Sludge Spinner | **UNMAPPED (not costed)** | Gallery `:76`: 1 cand, **S**, uncontested |
| U-2 | Corpse Slug | **UNMAPPED** | Gallery `:77`: 1 cand, P |
| U-3 | Toadpole | **UNMAPPED** | Gallery `:78`: **stretch-only** (2 X); on the §1 leftovers flag |
| U-4 | Two-Tailed Rat | **UNMAPPED** | Gallery `:79`: 1 P + 1 X |
| U-5 | Seapunk | **UNMAPPED** | Gallery `:80`: 1 cand, P. *(A `NSeapunkVfx` driver exists in the assembly, so this row is not free — but it was not costed.)* |
| U-6 | Gremlin Merc | **UNMAPPED** | Gallery `:81`: 1 P + 1 X; "death-spawn has no faction ability behind it in either case" |
| U-7 | Living Fog + Gas Bombs | **UNMAPPED** | Gallery `:82`: 1 cand, **S** — "the strongest fodder pairing in the atlas regardless of parent choice" |
| U-8 | Terror Eel · Haunted Ship · Fossil Stalker · Calcified + Damp Cultists | **UNMAPPED, and the gallery files five bodies under one row with no candidates** | `reskin-gallery.md:84`. Recorded facts only: `FossilStalker` and `HauntedShip` both override `HasPhobiaSpineSkin => true` (two of the five in the assembly) and `pck` carries `terror_eel_phobia.png` (1 768 162 B), so **at least three of these five carry an accessibility obligation**. Splitting the row is a change to an existing ordering and is [USER]'s — question 13. |

---

## 3. What the joined view shows that no single file could

### 3a. Complexity, across the whole mapped set

| Set | S | M | L | rows | share L |
|---|---|---|---|---|---|
| Act 1 normals | 3 | 0 | 3 | 6 | 50 % |
| Act 2 normals | 2 | 3 | 8 | 13 | 62 % |
| Act 3 normals | 1 | 4 | 6 | 11 | 55 % |
| **All normals** | **6** | **7** | **17** | **30** | **57 %** |
| **Elites + bosses** | **3** | **1** | **18** | **22** | **82 %** |
| **Whole costed set** | **9** | **8** | **35** | **52** | **67 %** |

The distributions are genuinely different, and the cause is not creature size —
it is that **the bespoke-`N…Vfx`-driven-by-named-Spine-events pattern is the
house style at elite and boss tier**: **17 of 22** elite/boss rows carry one,
against **11 of 30** normals.

The **nine S rows in the entire mapped set** are: Nibbit, Inklets, Mawler (A1);
Bowlbug-Nectar-as-skin, Chompers (A2); Globe Head (A3); **Byrdonis, Infested
Prism** and **Aeonglass†** (elites/bosses). Only three sit above normal tier,
one of those three is a boss, and that boss's letter is degenerate — it is S
because it has no rig at all (§2c, E21). Two of the nine are not really bodies
in their own right: Bowlbug-Nectar is a skin on A2-1's rig, and Globe Head ships
14 undriven apron clips a like-for-like rig would have to reproduce.

### 3b. Bodies vs. rigs — where the sim, the gallery and the base game disagree

Six rows cost materially more or less than a naive read suggests. Each is
already in a source file; the joined view is where they line up.

| Row | Naive read | Actual rig bill | Source |
|---|---|---|---|
| A1-3 Slimes | 2 bodies (sim) | **4 rigs** | `s18-act1.md` §5b |
| A2-1 Bowlbug pod | 2 bodies (sim), 4 bodies (base) | **1 rig, 4 skins** — plus a nested second skeleton | `s18-act2.md` §5b |
| A3-6 Fabricator | 3 bodies (sim keeps 2 of 4 bots) | **5 rigs** | `s18-act3.md` §5a |
| E15 Kaiser Crab | 2 bodies | **1 skeleton**, 4 texture pages | `s18-bosses-elites.md` E15 |
| E18 Mecha Knight | 1 body | **2 rigs** (one VFX-only) | `s18-bosses-elites.md` E18 |
| E20 Test Subject | 1 body | **3 rigs**, 23 clips | `s18-bosses-elites.md` E20 |

### 3c. The boss surcharge is invisible in the complexity letter

Three art surfaces belong to `EncounterModel`, not to the creature, so they
never move an S/M/L letter. **Every boss row carries them; no elite row does.**

| Surface | Bosses carrying it | Notable |
|---|---|---|
| Map node | **12 of 12** — but only **3** ship a real Spine rig (Ceremonial Beast, Queen, The Insatiable); the other **9** ship a two-PNG placeholder pair out of `images/map/placeholder/` | The placeholder directory name is the base game's own |
| Custom background (a **`DirAccess`-enumerated** layers directory that **throws** if absent) | **11 of 12** — Aeonglass is the exception | Layer counts run 2 (Waterfall Giant) to 14 (Lagavulin, Soul Fysh) |
| `CustomBgm` + a music parameter | **11 of 12** drive a parameter; **11 of 12** set `CustomBgm` | **Lagavulin Matriarch has neither**; **Aeonglass borrows both from the Queen** |

### 3d. Reconciliations between source files

Recorded so the joined table is honest about where its numbers came from. **No
act file was edited.**

| Item | `s18-act3.md` says | The C# drives | Reading |
|---|---|---|---|
| Flail Knight clips | 7, incl. `attack_breaker` (`:179`) | 6 (`Monsters/FlailKnight.cs:86-101`) | The act agent read the **rig**; I read the **code**. If `attack_breaker` exists it is **undriven rig content** — the same category Act 3 itself named for Globe Head and the Fabricator. Not a contradiction. |
| Torch Head Amalgam clips | 6, incl. `buff` (`:184`) | 5 (`Monsters/TorchHeadAmalgam.cs:126-130`) | Same reading. |
| Soul Nexus driver | `NSoulNexusVfx` + 3 `Line2D` trails (`:181`) | Confirmed — the class exists and `pck:scenes/creature_visuals/soul_nexus.tscn` embeds it | No correction. |
| Byrdpip | "a **player pet** spawned by a relic, not Byrdonis's add" (`s18-act1.md:145`) | Confirmed | Carried into E1: Byrdonis has **no add**. |

**A consequence of the two clip reconciliations:** the elite/boss rows report
**driven** clips only (read from `new AnimState("…")` declarations), while the
three act files report **rig** clips cross-checked against the code. So the
`Clips` column is directly comparable **within** a block but is a **lower bound**
in the E-rows. Anywhere a like-for-like rig matters, the act files' method is the
one to re-run.

**Three socket cells were extended in the join, and only where the source row's
own prose already named the obligation.** No act file was edited; the extension
lives here.

| Row | Act file's socket cell | Extended to | Why |
|---|---|---|---|
| A2-10 Ovicopter | S1, S2, S3, S4 | **+ S5** | The row's own text says `ToughEgg::SetupSkins` picks randomly between skins `egg1` and `egg2` at spawn (`s18-act2.md` row 10). S5 is the skin key; the cell omitted it. |
| A3-5 Construct gang · A3-10 Owl Magistrate | S1–S6 only (Act 3 never used S7/S8) | **+ S8** | `s18-act3.md` §6 identifies exactly these rows plus Test Subject as needing `AnimState.BoundsContainer` to resolve named `Control` children — but files them under **S2**, because Act 3 restated only the S1–S6 key space. Act 2 had already minted **S8** for precisely that question (`s18-act2.md` §6). Joining them under S8 is the whole point of a single key space. |

### 3e. Cross-act coupling — one row, and it is not a boss

Exactly one mapped encounter shares its bodies with another act: **A3-5, the
construct gang** — `PunchConstruct` also headlines `PunchConstructNormal` in
Underdocks and `CubexConstruct` headlines `CubexConstructNormal` in Overgrowth
(`s18-act3.md` §5a). **No elite or boss body is shared across acts at all**, so
elite and boss picks can be made act-by-act without cross-act repaint risk.
Recorded as a reassurance, not a question.

---

## 4. Coverage reconciliation

`reskin-gallery.md` lines 19–85 contain **66 table rows, of which 5 are section
headers → 61 mapped encounters**. Disposition:

| Gallery block | Gallery rows | Matrix rows | Reconciliation |
|---|---|---|---|
| ACT 1 — Overgrowth | 11 | 11 | A1-1…A1-6 (6 normals) + E1…E5 (5 elites/bosses) |
| ACT 1 boss pool — research | 4 | 4 | E6…E9 |
| ACT 2 — the Hive | 19 | 19 | A2-1…A2-13 (13) + E11…E16 (6) |
| ACT 3 — Glory | 18 | **17** | A3-1…A3-11 (11, of which **A3-5 joins two gallery rows**, Punch `:61` and Cubex `:62`, because they are **one** encounter, `ConstructMenagerieNormal`) + E17…E22 (6) |
| UNDERDOCKS — Act 1 alternate | 9 | 9 | E10 (costed) + U-1…U-8 (**not costed**) |
| **Total** | **61** | **60** | 61 gallery rows → 60 matrix rows; the single merge is A3-5 and is stated in-row. |

**Nothing mapped is dropped.** Eight rows (U-1…U-8, covering twelve bodies) are
present but **not costed**, with the ownership reason stated in §2d.

Against the **base game** rather than the gallery, the three act files record
their own boundaries and they are repeated here without change:

- **Act 1** — ten base `Overgrowth` encounters carry **no gallery row** at all
  (`CubexConstructNormal`, `FlyconidNormal`, `FuzzyWurmCrawlerWeak`,
  `OvergrowthCrawlers`, `PhrogParasiteElite`, `RubyRaidersNormal`,
  `ShrinkerBeetleWeak`, `SlitheringStranglerNormal`, `SnappingJaxfruitNormal`,
  `VineShamblerNormal`) — `s18-act1.md:180-186`. Whether they should is a scope
  call.
- **Act 2** — a clean join: all 20 base `Hive` encounters are covered
  (`s18-act2.md` §5a). One loose end: **`TunnelerNormal`** exists as a class,
  the Chomper dossier lists it, and it appears in **no** `ActModel` encounter
  list in v0.107.1 — recorded as UNKNOWN, not interpreted.
- **Act 3** — a clean join: all 18 encounters `Glory::GenerateAllEncounters`
  returns are mapped (`s18-act3.md` §5). One sim-register gap:
  `ScrollsOfBitingNormal` (the 4-copy encounter) is **neither modelled nor on
  `act3_pool.yaml`'s dropped list**, so an encounter count read off the sim is
  one short.

---

## 5. Questions for [USER] — deduped across all four files

Numbered for citation, **not ranked**. Each gives one context sentence, an exact
source pointer, and an answer shape. **No recommendation is attached to any of
them.** QUEUE remains canonical; this list mints nothing.

**Scope calls**

1. **Do the ten unmapped base Overgrowth encounters come into scope?** They are
   live base-game Act-1 encounters with no gallery row and no pool entry.
   *Source:* `s18-act1.md:180-186`. *Shape:* yes-no (or a pick of which).
2. **Do Act 1's four research bosses come into scope?** Ceremonial Beast, The
   Kin, Waterfall Giant and Soul Fysh are live base encounters with complete art
   surfaces and gallery rows, but are absent from `act1_pool.yaml` — so the sim
   shows Act 1 as having two bosses where the base act has six. *Source:*
   `s18-bosses-elites.md` §5c. *Shape:* yes-no.
3. **Does the Underdocks block get costed at all?** Eight gallery rows covering
   twelve bodies are mapped but have no engineering read, because no S18 agent
   owned that block. *Source:* §2d above. *Shape:* yes-no.
4. **Does the gallery's five-body Underdocks leftovers row get split?**
   `reskin-gallery.md:84` files Terror Eel, Haunted Ship, Fossil Stalker and the
   two Cultists under one row with no candidates; at least three carry a phobia
   obligation. Splitting an existing gallery row is not a drafter's call.
   *Shape:* yes-no.

**Structural calls**

5. **The atlas-vs-weekly-boss fork.** For **Kaiser Crab, Test Subject and
   Aeonglass** the reskin gallery's normal-enemy candidates beat every
   weekly-boss draft on the merits; for **Knowledge Demon** the weekly layer is
   stronger because atlas cover is explicitly soft. Which gallery owns the
   act-boss slots is structural. *Source:* `docs/current/dossiers/bosses/candidates.md:27-32`,
   `:777-794`. *Shape:* pick-one, globally or per slot.
6. **Boss art-surface scope.** A reskinned boss can inherit its base map node,
   background and music untouched, or replace some or all. Eleven of twelve
   carry all three; `vantom_boss` (3 layers) and `waterfall_giant_boss` (2) are
   cheap to replace, `lagavulin_matriarch_boss` and `soul_fysh_boss` (14 each)
   are not. *Source:* §3c above. *Shape:* pick-one — creature only / creature +
   map node / everything.
7. **Family coherence on the three multi-body encounters.** `bowlbug_pod`,
   `construct_gang` and `shield_and_turret` need one family across the whole
   encounter, or they produce mixed-faction fights. The implementation read
   **sharpens** this for two of them: Slumbering Beetle's base encounter is a
   three-body room containing two bowlbugs, and both construct bodies also
   headline Act-1 encounters. *Source:* `reskin-gallery.md:128`,
   `s18-act2.md` §5b, `s18-act3.md` §5a. *Shape:* open.
8. **Phobia-mode coverage: reproduce, drop, or per-body?** It binds one Spine
   skin plus three texture sets among elites/bosses, one skin among Act-1
   normals, one among Act-2 normals, and two more among the uncosted Underdocks
   leftovers — under **two incompatible filename conventions**
   (`<id>_phobia` vs `phobia_<id>`). It is an accessibility surface, so it also
   belongs to S20's census. *Source:* `s18-act2.md` §7, `s18-bosses-elites.md`
   §7. *Shape:* pick-one — reproduce / drop / per-body.

**Rows where the candidate galleries are empty or blocked**

9. **Two bosses have no candidate from either gallery: Soul Fysh and
   Queen + Torch Head Amalgam.** Both are on the gallery's redesign-pressure
   list with zero claims across all 16 families, and neither has a weekly-boss
   row. Queen's amalgam is simultaneously one of the two most VFX-dense bodies
   in Act 3. *Source:* `reskin-gallery.md:94`, `:96`; `s18-bosses-elites.md`
   E9, E22. *Shape:* open.
10. **Three more rows are on the redesign-pressure list with shipped content and
    no cover:** Decimillipede (Reattach has no analogue anywhere — the gallery
    calls it "the highest-priority gap"), Spiny Toad (Thorns-as-retaliation, six
    claims none strong — and the implementation read shows the tell is a whole
    second body state, not an icon), Entomancer / Knowledge Demon (plausible-only,
    both with caveats). *Source:* `reskin-gallery.md:90-100`, `s18-act2.md`
    row 12. *Shape:* open.
11. **Aeonglass has no base animation to reskin against**, and is simultaneously
    the row the gallery calls its "strongest single boss argument". *Source:*
    `s18-act3.md` §4, `s18-bosses-elites.md` E21. *Shape:* pick-one — (a) a
    static-body reskin matching the shipped state, (b) the row that gets an
    original rig, (c) out of scope until MegaCrit finishes it.
12. **Globe Head's silhouette flag is now partly answerable.** The gallery
    records it as NOT RESOLVED and asks for someone to look at the sprite;
    `s18-act3.md` §7 describes the base asset from its 52 atlas regions (an
    aproned humanoid biped with individually rigged fingers, a "slappy hand",
    boots, back tubes, and an orb head with lightning pieces). That description
    affects the **ordering** of that row's nine candidates, which remains
    [USER]'s. *Source:* `reskin-gallery.md:120`, `s18-act3.md` §7. *Shape:*
    open — re-order or leave.

**Register hygiene, surfaced by the reads**

13. **`TunnelerNormal` exists as a class, is listed by the Chomper dossier, and
    appears in no `ActModel` encounter list in v0.107.1.** Dead content,
    event-reachable, or reached by a path not searched — UNKNOWN. *Source:*
    `s18-act2.md` §7. *Shape:* open (confirm or ignore).
14. **`ScrollsOfBitingNormal` (the 4-copy Act-3 encounter) is neither modelled
    in `act3_pool.yaml` nor on its dropped list**, so an encounter count read off
    the sim is one short. *Source:* `s18-act3.md` §5a. *Shape:* open (a register
    fix, not a design call).

---

## 6. What this does **not** establish

It makes **no mapping verdict**: it chooses and ranks no Genshin body for any
encounter, resolves no fork between the two candidate galleries, and changes no
existing ordering in either. It does not grade RESKIN vs REDESIGN — the
`Gallery` column repeats what `reskin-gallery.md` and
`dossiers/bosses/candidates.md` already recorded, including their own confidence
codes and flags. It does not prove any enemy can be added or reskinned in a mod:
S13 settled the **source reading** on S1, S4 and half of S2 and S3, and
**nothing was executed** — no game launched, no pck built, no DLL compiled, and
S13's own recommendation is that the first runtime evidence come from the
offline Harmony bite-check. It answers none of `S5`, `S7`, `S8` or `B1`–`B6`. It
does not measure runtime performance, rig internals or audio content (S16 is
authoritative on rig internals; FMOD bank contents were never opened). It
touches no shipped sim, no governing doc, no stamp, no balance window and no
experiment, and it mints no id. The complexity letters are an engineering count
of asset contracts — **not a schedule and not a cost in hours** — and for
Aeonglass the letter is explicitly meaningless. Whether any of these encounters
should be reskinned at all remains [USER]'s call.
