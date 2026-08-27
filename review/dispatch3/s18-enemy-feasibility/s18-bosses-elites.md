# S18 — Implementation-aware enemy feasibility, **elites and bosses**

> **This decides nothing.** It is an engineering read of what each mapped elite
> and boss encounter is *made of* in the shipped game — rig, animation clips,
> scene nodes, particle contract, sound events, and the three art surfaces that
> only bosses carry — so that the enemy mapping [USER] has not yet made can be
> costed. It does **not** rank Genshin candidates, does not repeat Genshin
> canon, and does not pick a reskin. Two candidate orderings already exist
> (`docs/current/dossiers/remap/reskin-gallery.md` and
> `docs/current/dossiers/bosses/candidates.md`); this file repeats what they
> record and changes neither.

- **Date:** 2026-08-26/27. **Primary checkout:** `223a4ff` (per `PREFLIGHT.md`),
  read-only throughout. No game was launched, nothing was deployed, no game file
  was written, and no decompiled or extracted game data was copied into a repo.
- **Game read:** Slay the Spire 2 **v0.107.1** (`docs/current/STATE.md:157`).
- **Owner split:** this file owns **every elite and boss row** the three act
  files handed off in their §4 pointer tables, plus the one elite the gallery's
  Underdocks block carries. The 30 normal-encounter rows stay with
  `s18-act1.md`, `s18-act2.md`, `s18-act3.md`; they are joined, not repeated,
  in the sibling `s18-joined-matrix.md`.
- **Socket columns here are FINAL where S13 answered them.** Unlike the act
  files, this one was written after `review/dispatch3/s13-engine-sockets.md`
  landed. §6 states, per key, what S13 settled and what it did not. Six
  boss/elite-specific keys (`B1`–`B6`) are new here because nothing in the
  normal-encounter set exercises them.
- **Sibling schema:** the columns, the complexity scale and the socket key
  space are deliberately the same as `s18-act1.md` so the joined matrix has one
  shape.

---

## 0. How the evidence was obtained

Four sources, all read-only, all local.

| Source | What it gives | Cite form used below |
|---|---|---|
| `sts2.dll` decompiled with ilspycmd 8.2 (`--project --nested-directories`), in the scratch tree the Act-1/2 agents built and I re-checked | monster/encounter classes, animation-state declarations, VFX/SFX call sites, Spine-event switches, music-parameter calls | `<Namespace.Type>::<member>` in prose + `Models/…/File.cs:line`, `Nodes/Vfx/File.cs:line` |
| `SlayTheSpire2.pck` directory index, parsed read-only (Godot pack **format 3**, engine **4.5.1**, 15 658 entries) | exact resource paths and byte sizes | `pck:<path>` (+ byte size) |
| Extracted `.tscn` scenes (plain text in this pack) | node graphs, node types, script bindings | `pck:<path>` + node names |
| The repo | shipped sim models, behaviour dossiers, and the two candidate galleries | repo `file:line` |

Scratch tree: `…\scratchpad\s18\` (decompile + `pck_index.txt` + `extracted/`),
shared with the act agents; my own working notes are in
`…\scratchpad\s18-integrator\`. **Nothing there was copied into a repo.**

### 0.1 The four engine facts the act files established, restated so this reads cold

1. **One Spine rig per named body.** `res://animations/monsters/<id>/` holds
   `<id>.atlas`, `<id>.png`, `<id>.skel`, `<id>_skel_data.tres`, plus a scene
   `res://scenes/creature_visuals/<id>.tscn`. `MonsterModel::VisualsPath` is
   `protected virtual`, defaulting to `creature_visuals/<Id.Entry>`
   (`Models/MonsterModel.cs:216`).
2. **The default animator is five clips** — `idle_loop` (looping), `cast`,
   `attack`, `hurt`, `die` (`Models/MonsterModel.cs:602-619`). A missing clip
   warns and continues; a missing visuals scene falls back to
   `creature_visuals/fallback`.
3. **The creature-visuals scene contract is four nodes** — `%Visuals`,
   `%Bounds`, `%CenterPos`, `%IntentPos`; `%OrbPos`, `%TalkPos` and
   `%PhobiaModeVisuals` are optional. **The body need not be Spine**: the Spine
   path is gated on `GetClass() == "SpineSprite"`.
4. **Enemy SFX are id-derived FMOD event paths**,
   `event:/sfx/enemy/enemy_attacks/<id>/<id>_{attack,cast,die}`
   (`Models/MonsterModel.cs:292-296`), resolved out of `pck:banks/desktop/*.bank`.

### 0.2 Five facts that are *new here* because only elites and bosses show them

These are the reason this file is not just nine more rows of the same shape.

**(a) A boss is an `EncounterModel`, and it carries three art surfaces a normal
never does.** There is no `BossModel` (S13 §5.1). What makes a boss expensive is
not the creature — it is what `EncounterModel` hangs off `RoomType.Boss`:

| Surface | Member | Default | Failure mode |
|---|---|---|---|
| **Map node** | `BossNodePath` (`Models/EncounterModel.cs:198`), `BossNodeSpineResource` (`:200-210`), `BossNodeAssetPaths` (`:218-231`) | a **Spine rig** at `res://animations/map/<encounter-id>/<encounter-id>_node_skel_data.tres` | `ResourceLoader.Exists` probe → falls back to a `<path>.png` + `<path>_outline.png` pair |
| **Combat background** | `HasCustomBackground` (`:188`) → `CreateBackgroundAssetsForCustom` (`:311-314`) → `new BackgroundAssets(Id.Entry.ToLowerInvariant(), rng)` | the parent act's generic background | **HARD FAIL.** `BackgroundAssets` opens `res://scenes/backgrounds/<encounter-id>/layers` with `DirAccess.Open` and **throws** `InvalidOperationException("could not find directory …")` if it is absent (`Rooms/BackgroundAssets.cs:49-53`). It then *enumerates the directory* and groups files by the `_bg_##` / `_fg_` prefix. Its own doc comment states "`{title}` must be exactly the same as the class name" (`:43`). |
| **Music** | `CustomBgm` (`:190`), `AmbientSfx` (`:194`) | empty → `HasBgm` false | plus a per-boss FMOD **parameter** the monster drives at runtime, `NRunMusicController.UpdateMusicParameter("<name>_progress", v)` |

**Where the shipped game actually is on those surfaces**, counted from the pack:

- **Three** boss encounters ship a real Spine map node — `ceremonial_beast_boss`,
  `queen_boss`, `the_insatiable_boss` (`pck:animations/map/…`, e.g.
  `ceremonial_beast_boss_node.skel` 4 056 B + `boss_node_ceremonial_beast.png`
  1 651 732 B). **Nine** override `BossNodePath` to
  `res://images/map/placeholder/<id>_icon` and set `BossNodeSpineResource => null`,
  i.e. they ship a **two-PNG placeholder pair** (`pck:images/map/placeholder/…`
  — 9 `_boss_icon.png` + 9 `_boss_icon_outline.png`).
- **Eleven** boss background directories exist. Layer-scene counts:
  `lagavulin_matriarch_boss` 14 · `soul_fysh_boss` 14 · `glory`/`queen_boss`/
  `test_subject_boss` 12 · `ceremonial_beast_boss`/`kaiser_crab_boss`/
  `knowledge_demon_boss`/`the_kin_boss` 11 · `the_insatiable_boss` 8 ·
  `vantom_boss` **3** · `waterfall_giant_boss` **2**. There is **no
  `aeonglass_boss` directory** — and `AeonglassBoss` is the only boss that sets
  `HasCustomBackground => false` (`Models/Encounters/AeonglassBoss.cs:19`).
- **Eleven** bosses drive a music parameter. Two shipped bosses do **not**:
  `LagavulinMatriarch` and `CeremonialBeast` (grep over
  `Models/Monsters/*.cs` for `UpdateMusicParameter`). `LagavulinMatriarchBoss`
  also ships **no `CustomBgm`** — it fights over act music.
- **No elite has any of the three.** Elites inherit the act background, the act
  music and a plain map node. That is the single largest elite-vs-boss cost
  difference and it is invisible from the creature rig.

**(b) Bosses talk to their own visuals scene by exact node path.**
`NCreature::GetSpecialNode<T>(string name)` is `Visuals.GetNodeOrNull<T>(name)`
(`Nodes/Combat/NCreature.cs:441-444`) — a **soft** lookup that returns null. The
model side uses it heavily at elite/boss tier: `Vantom.cs:210`
(`"Visuals/ScalingBone"`), `LagavulinMatriarch.cs:121` (`"%SleepVfxPos"`),
`KinPriest.cs:155` (`"Visuals/Beam"` → `NKinPriestBeamVfx.Fire()`),
`KinFollower.cs:149` / `MagiKnight.cs:128` (`"Visuals/AttackDistanceControl"`),
`TestSubject.cs:345` (`"%CanvasGroup"`), `BygoneEffigy.cs:96`
(`"Visuals/SpineBoneNode"`), and — deepest in the game —
`TorchHeadAmalgam.cs:74-76`, three parallel four-level paths
`"Visuals/torch{1,2,3}Slot/fire{1,2,3}_small_green/light_small"`, plus
`"Visuals/LaserControlBone"` (`:100`). The **driver** side is worse: every
`N…Vfx` node resolves its emitters with **`GetNode<T>` (hard, throws)** — e.g.
`Nodes/Vfx/NWaterfallGiantVfx.cs:249-260` performs **twelve** hard lookups in a
row. So a boss visuals scene is an exact-node-tree contract, half of it silent
on failure and half of it fatal.

**(c) Bosses layer a second Spine animation track.** Five bodies call
`SetAnimation("…tracks/<name>", loop, **1**)` — track index 1, on top of the
clip the animator drives:

| Body | Track content | Site |
|---|---|---|
| Vantom | `_tracks/charge_up_1` then `_tracks/charged_1` | `Vantom.cs:107-112` (inside `SetupSkins`) |
| Lagavulin Matriarch | `_tracks/eyes_closed_loop` | `LagavulinMatriarch.cs:104-107` |
| Waterfall Giant | **`_tracks/buildup{1..3}`, index computed from a power counter at runtime** | `WaterfallGiant.cs:327` |
| Soul Nexus | `tracks/writhe`, swapped to `tracks/empty` | `SoulNexus.cs:38-40`, `:52`, `:59` |
| Queen | `tracks/writhe`, swapped to `tracks/empty` | `Queen.cs:112-114`, `:121`, `:238` |

Note the two spellings (`_tracks/` and `tracks/`) and that four of the five are
installed from inside `SetupSkins`, a method whose name says *skins*. **No
normal encounter in any act does this.**

**(d) Some drivers key off the animation that starts, not off an authored
event.** `MegaSprite::ConnectAnimationStarted` is used alongside
`ConnectAnimationEvent` by `NQueenVfx.cs:78-79`, `NKnowledgeDemonVfx`,
`NKaiserCrabBossVfx`, `NSpectralKnightVfx`, `NTheInsatiableVfx` and
`NTestSubjectVfx`, and each switches on **clip names** (`"attack"`,
`"idle_loop"`, `"attack_thrash"`, `"salivate"`, `"burn"`, `"die3"`,
`"idle_loop3"`, `"empty"`). So for those bodies the *clip name itself* is part
of the VFX contract, not only the events inside it.

**(e) The SFX namespace diverges from the monster id far more often at this
tier.** Cases found: `phantasmal_gardeners` (plural) for `PHANTASMAL_GARDENER`
(`PhantasmalGardener.cs:29-33`); `infested_prisms` (plural) for
`INFESTED_PRISM` (`InfestedPrism.cs:20-32`); `mechaknight` (no underscore) for
`MECHA_KNIGHT` (`MechaKnight.cs:40-48`); `the_kin_minion` for `KIN_FOLLOWER`,
whose `HurtSfx` additionally points at **the priest's** namespace
(`KinFollower.cs:34-61`); and a single `kaiser_crab` namespace serving **both**
`Crusher` and `Rocket` via `_left_` / `_right_` infixes (`Crusher.cs:28-40`,
`Rocket.cs:23-35`). The base game also ships two directory typos at this tier —
`pck:images/vfx/monsters/knowledge_demom/` and (Act 3's find)
`devoted_scultpor.skel`.

---

## 1. Column key

Identical to `s18-act1.md` §1, with one column widened.

| Column | Means |
|---|---|
| **Asset / rig family** | The base creature's actual rig: Spine skeletons with imported byte size as a coarse rig-weight proxy, atlas size, texture size, and the creature-visuals scene size (and node count where the scene was extracted). |
| **Required tells / states** | The animation clips the code actually drives, how the `Hit`/`Dead` branches are wired, and any spawn-time power the player must be able to read. |
| **Variants / reuse** | How many distinct art bodies the encounter needs, what varies in code or skin rather than in art, and any encounter-scene slots / camera override. |
| **VFX / audio surface** | Hit VFX scenes, bespoke `N…Vfx` driver nodes and how many hard node lookups they make, named Spine attach bones/slots, named Spine animation events, layered `tracks/` content, **and — for bosses only — the map node, the background layer directory, the BGM event and the music parameter.** |
| **Complexity** | S / M / L on the scale in §3. |
| **RESKIN vs REDESIGN (as the atlases record it)** | Repeated from `reskin-gallery.md` **and**, for the six shipped act-boss slots, from `dossiers/bosses/candidates.md`. No new judgement. |
| **Socket** | Keys into §6. Keys marked **FINAL** were settled by S13; keys marked *(prov.)* were not. |

---

## 2. Act 1 — elites and bosses

Nine rows: five shipped (`tier05/content/act1_pool.yaml:100-199`) and four
research-only (`docs/current/research/act2-act3-roster-research.md` §4, per the
gallery's "ACT 1 boss pool — research" block).

| # | Encounter (gallery row) | Asset / rig family | Required tells / states | Variants / reuse | VFX / audio surface | Complexity | RESKIN vs REDESIGN (as the atlases record it) | Socket |
|---|---|---|---|---|---|---|---|---|
| E1 | **Byrdonis** (elite, `ByrdonisElite`, solo) | **1 rig.** skel 156 650 B, atlas 1 753 B, texture 233 576 B; scene `pck:scenes/creature_visuals/byrdonis.tscn` **1 160 B** — the same size class as the bare 4-node contract. | **5 clips** — `idle_loop`, `hurt`, `attack`, `die`, **`get_angry`** (i.e. `cast` renamed, on a bespoke `Angry` trigger) (`Monsters/Byrdonis.cs:69-83`). Two moves only, wired as a hard alternation (`SwoopMove.FollowUpState = PeckMove` and back, `:44-48`). Spawn-time **`TerritorialPower` 1** in `AfterAddedToRoom` (`:34-38`) — the ramp the player must read. | Solo, no adds, no slots, no encounter scene, no camera override (`Encounters/ByrdonisElite.cs:9-16`). Rig used nowhere else. | Shared `vfx/vfx_attack_slash` on both attacks (`:57`, `:65`). **No bespoke driver, no attach nodes, no Spine events, no layered track.** Explicit `DeathSfx` and `TakeDamageSfx` in the `byrdonis` namespace (`:30-32`). | **S** — the cheapest elite in the game by asset shape: one rig, five clips, the bare scene, shared hit VFX. | SHIPPED. Gallery `:26`: **8 candidates, six rated S** — "the run's one flying-elite slot and the atlas's most crowded silhouette". Not on the §1 redesign-pressure list. **§5 double-booking:** Consecrated Red Vulture is claimed here *and* at Owl Magistrate. No weekly-boss layer (elite). | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)* |
| E2 | **Bygone Effigy** (elite, `BygoneEffigyElite`, solo) | **1 rig.** skel **34 256 B — the smallest skeleton of any elite or boss**, atlas 993 B, texture **628 404 B** (a small rig carrying a big painted sheet). Scene 1 442 B. | **5 clips** — `idle_loop`, `cast`, `attack`, `hurt`, `die` — but wired as a **branch graph**, `Hit` added per-state rather than as an any-state (`Monsters/BygoneEffigy.cs:110-126`). Tells: a `SleepIntent` opener, a wake-up buff, one huge slash (`:40-46`). Spawn-time **`SlowPower` 1** (`:34-38`). | Solo. **Camera override 0.88 scale / +50 y** (`Encounters/BygoneEffigyElite.cs:14-22`). No slots, no encounter scene. | Shared `vfx/vfx_attack_slash` (`:105`). One **named attach node**: the model reads `"Visuals/SpineBoneNode"` before the slash (`:96`). `TakeDamageSfxType.Stone` (`:32`); attack/cast/die id-derived. No driver, no Spine events. | **M** — an S body plus exactly one extra (the named attach node). | SHIPPED. Gallery `:27`: 7 candidates, **2 rated S** — "'statue that wakes' is uniquely Ruin Guard". Not on the redesign-pressure list. **§5 double-booking:** Ruin Guard ×3, and the gallery's own demotion note orders the Ruin Guard ↔ Punch Construct claim *below* this one. No weekly-boss layer. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, **B4 (soft)** |
| E3 | **Phantasmal Gardener ×4** (elite, `PhantasmalGardenersElite`) | **1 rig ×4 bodies.** skel 208 261 B, atlas 1 103 B, texture 119 524 B; scene **3 556 B**; room scene `pck:scenes/encounters/phantasmal_gardeners_elite.tscn` 530 B. | **10 clips** — `idle_loop`, `buff`, `attack`, `attack_multi`, `hurt_extended`, `hurt`, `die`, `block_start`, `block_loop` (looping), `block_end` (`Monsters/PhantasmalGardener.cs:158-186`). **`Hit` branches on `SkittishPower.HasGainedBlockThisTurn`** — the body has two different hurt animations depending on whether its shield has already fired this turn (`:183-184`), and a three-clip block cycle on its own `BlockStart`/`BlockEnd` triggers. That shield read is the whole encounter. | **Four bodies of one rig, staggered by slot.** `ConditionalBranchState` keys the opening move off `Creature.SlotName` ∈ {first, second, third, fourth} (`:104-107`); the encounter fields four mutable clones into those four slots (`Encounters/PhantasmalGardenersElite.cs:36-44`). **Skin obligation:** `SetupSkins` composes a runtime skin, `FindSkin("tall")` for slots `first`/`third` and `FindSkin("short")` otherwise (`:73-88`) — a **slot-dependent** two-skin contract, not a recolour. Camera 0.85 / +40 y. | **Bespoke.** `NPhantasmalGardenerVfx` resolves `"../SpewSlotNode/SpewParticles"` (`Nodes/Vfx/NPhantasmalGardenerVfx.cs:63`) and is driven by **2 named Spine events**, `spew_start` / `spew_end` (`:71`, `OnSpewStart`/`OnSpewEnd`). 1 bespoke texture (`pck:images/vfx/monsters/phantasmal_gardener/phantasmal_spew_particle.png`). Hit VFX `vfx/vfx_bite` ×2 and `vfx/vfx_attack_blunt`. **SFX namespace is `phantasmal_gardeners`, plural — not the id** (`:29-33`, `:71`); `TakeDamageSfxType.Magic`. | **L** — bespoke event-driven driver **plus** a skin obligation **plus** an encounter scene: three M-grade extras. | SHIPPED. Gallery `:28`: **9 candidates, eight rated S** — "everyone wants Skittish; mages have the most literal mechanic, hilichurls the most iconic scene." Not on the redesign-pressure list. No weekly-boss layer. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S4 **FINAL**, S5 *(prov.)*, S6 **PARTIAL** |
| E4 | **Vantom** (boss, `VantomBoss`, solo) | **1 rig.** skel **393 130 B**, atlas 4 495 B; scene **12 262 B**, plus a companion resource `pck:scenes/creature_visuals/vantom.tres` 2 123 B. | **9 clips** — `idle_loop`, `buff`, `debuff`, `attack`, `attack_double`, `attack_heavy`, `charge_up`, `hurt`, `die`, on five bespoke SHOUTING triggers `CHARGE_UP` / `ATTACK_HEAVY` / `BUFF` / `DEBUFF` / `ATTACK_DOUBLE` (`Monsters/Vantom.cs:219-245`). Tells: the four-beat menu the sim models — Ink Blot, Inky Lance ×2, Prepare, and the telegraphed Dismember (`:114-118`). | Solo, fixed HP (`MaxInitialHp => MinInitialHp`, `:66`). Camera 0.9 / +50 y. No slots, no encounter scene. | **Bespoke and layered.** `NVantomVfx` resolves a `TailSlotNode` shader material plus **four** emitters (`SprayBoneNode/SprayParticles`, `DeathSpraySlotNode/…`, `DeathSprayBackSlotNode/…`, `DeathExplosionSlotNode/…`) and switches on **6 named Spine events** — `dissolve_tail`, `spray_on`, `spray_off`, `death_spray_on`, `death_spray_off`, `death_explosion` (`Nodes/Vfx/NVantomVfx.cs:129-170`). **Layered track:** `SetupSkins` starts `_tracks/charge_up_1` then queues `_tracks/charged_1` on track 1 (`:107-112`). Model also reads `"Visuals/ScalingBone"` (`:210`). 3 bespoke textures (`oil_vfx`, `vantom_basic_particle`, `vantom_death_particle`). Six explicit SFX consts (`:48-58`) incl. a `vfx_giant_horizontal_slash` hit scene (`:184`). **Boss surfaces:** `CustomBgm` `event:/music/act1_boss_vantom`; music parameter `vantom_progress`, four distinct values (`:103`, `:141`, `:160`, `:178`, `:204`); custom background — **only 3 layer scenes**; placeholder map-icon pair. | **L** | SHIPPED. Gallery `:29`: 8 candidates, **1 rated S** (Kongamato); the row warns several candidates lean on Slippery, which §4 flags UNIMPLEMENTED. **Weekly-boss layer** (`candidates.md:38`, `:109-129`): recommended spend **Andrius** — "cleanest claim in both galleries; converged top pick"; alternates La Signora (demoted, spent at Kaiser Crab) and The Knave (uncontended). ⚑ `candidates.md:796-801` flags the stature cost of spending a launch weekly boss at the end of Act 1. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S6 **PARTIAL**, **B1 · B2 · B3 · B4 · B5** |
| E5 | **Lagavulin Matriarch** (boss, `LagavulinMatriarchBoss`, solo) | **1 rig.** skel 267 219 B, atlas 2 439 B, texture 610 814 B; scene 1 411 B. | **9 clips** — `sleep_loop` (initial, looping), `hurt_sleeping`, `wake_up`, `idle_loop` (looping), `cast`, `attack_heavy`, `attack_double`, `hurt`, `die` (`Monsters/LagavulinMatriarch.cs:245-270`). **`Hit` and `Wake` both branch on `IsAwake`** — the sleeping body has its own hurt clip and the wake is gated. The move machine opens with a `ConditionalBranchState` on `AsleepPower` (`:173-174`). | Solo, fixed HP. Camera 0.9. No slots, no encounter scene. | No bespoke `N…Vfx` node. Instead the model reads `"%SleepVfxPos"` and parents the **shared** sleeping VFX to it (`:121`) — the same pattern the Act-2 Slumbering Beetle uses. **Layered track:** `SetupSkins` starts `_tracks/eyes_closed_loop` on track 1 (`:104-107`). Four explicit SFX consts incl. a public `awakenSfx` (`:35-41`, `:193`); `TakeDamageSfxType.ArmorBig`. Hit VFX `vfx/vfx_attack_slash` ×3. **Boss surfaces:** **no `CustomBgm` at all** — this boss fights over act music; **no music parameter**; custom background with **14 layer scenes, the joint-largest in the game**; placeholder map-icon pair (`lagavulin_matriarch_boss_icon.png` 108 468 B + outline). | **L** — three extras: a named marker with a code-managed VFX lifecycle, a layered track, and a dual sleep/awake clip set with its own hurt. | SHIPPED, and the gallery records it as a **[USER]-locked pick** (`:30`): 6 candidates, 2 rated S; "she is a ratified user pick and her signature stat-drain is backlogged — touching her identity is a bigger call than any other row." §4 flags her Plating cap and Soul Siphon UNIMPLEMENTED. **Weekly-boss layer** (`candidates.md:39`): recommended **Magatsu Narukami**, carried with the same ⚑ identity warning; uncontended fallback All-Devouring Narwhal; Azhdaha CUT (spent at Q1 Orobas). | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, **B1 · B2 · B4 · B5** |
| E6 | **Ceremonial Beast** (boss, `CeremonialBeastBoss`, solo) — **RESEARCH**, not in the sim | **1 rig, but the largest total art surface in Act 1.** skel 334 655 B, atlas 2 660 B, texture 363 794 B; scene **69 046 B — the third-largest creature-visuals scene in the game**. Plus **two dedicated animated Spine background rigs**, `ceremonial_beast_bg_animation_top` (skel 5 140 B, texture 554 950 B) and `…_bottom` (skel 82 312 B, texture **1 472 166 B**), two room plates (`overgrowth_00_ceremonial_beast.png` 1 966 132 B, `overgrowth_06_…` 532 532 B) and eight bead textures. | **11 clips** — `idle_loop`, `shrill`, `attack`, `plow`, `plow_end`, **`plow_end_die`**, `stun`, `stun_loop` (looping), `wake_up`, `hurt`, `die` (`Monsters/CeremonialBeast.cs:264-305`). The most heavily branched graph of any Act-1 body: `Dead` splits on `InMidCharge`, and **`Hit` is wired fourteen times** — seven branches to `hurt` under `ShouldPlayRegularHurtAnim` and seven to `stun` under `IsStunnedByPlowRemoval` (`:287-300`). Tells: a charge that begins (`Plow`) and ends (`EndPlow`) as separate beats, a threshold stun and an un-stun, and a `Cast` that applies `RingingPower` to every player (`:225-229`). | Solo, fixed HP. Camera 0.9 / +50 y. `ExtraAssetPaths` = the **`Ringing` affliction overlay** (`Encounters/CeremonialBeastBoss.cs:19`) — a card-surface asset, not a creature asset. | **Bespoke.** `NCeremonialBeastVfx` is driven by **5 named Spine events, and they are the only camelCase event set in the game** — `turnOffEnergy`, `turnOnEnergy`, `deathParticles`, `plowStart`, `plowEnd` (`Nodes/Vfx/NCeremonialBeastVfx.cs:151-165`); five `[Export]` emitter slots. 1 bespoke texture. Hit VFX `vfx/vfx_attack_slash` ×2. Explicit plow / plow_end / shrill / stun / die SFX (`:39-75`); `TakeDamageSfxType.Fur`. **Boss surfaces:** `CustomBgm` `event:/music/act1_boss_ceremonial_beast`; **no music parameter**; custom background, 11 layer scenes **plus the two animated Spine background rigs above**; **a real Spine map node** (`pck:animations/map/ceremonial_beast_boss/*`). | **L** | RESEARCH. Gallery `:32`: 4 candidates, **3 rated S** — "Terrorshroom's rage/collapse is trigger-for-trigger". Not on the redesign-pressure list. **No weekly-boss layer** — `candidates.md` drafted only the six *shipped* act-boss slots. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S6 **PARTIAL**, **B1 · B2 · B3(partial)** |
| E7 | **The Kin** (boss, `TheKinBoss`, 3 bodies / 2 rigs) — **RESEARCH** | **2 rigs.** `kin_priest` skel 199 911 B, atlas 2 487 B, texture 482 192 B, scene **8 028 B**. `kin_follower` skel 86 680 B, atlas 1 771 B, texture 72 022 B, scene **6 371 B**. Room scene `pck:scenes/encounters/the_kin_boss.tscn` 455 B. | Priest: **6 clips** — `idle_loop`, `rally`, `attack_grenade`, `attack_laser`, `hurt`, `die`, on bespoke `Rally`/`AttackGrenade`/`AttackLaser` triggers (`Monsters/KinPriest.cs:178-193`). Follower: **6 clips** — `idle_loop`, `attack_slash`, `attack_boomerang`, `buff`, `hurt`, `die`, on `SlashTrigger`/`BoomerangTrigger` (`Monsters/KinFollower.cs:165-180`); spawn-time **`MinionPower` 1** (`:101`) — the "minions flee" read. | **Three bodies, two rigs**, at named slots `slot1`/`slot2`/`leaderSlot`; the first follower is flagged `StartsWithDance = true` (`Encounters/TheKinBoss.cs:41-50`). Camera 0.85 / +50 y. **Skin obligation:** `KinFollower::SetupSkins` picks a random hair skin from `{hair_1, hair_2, hair_3}` per body (`:26`, `:88-92`), so the two followers differ on screen. | **Bespoke, three drivers.** `NKinPriestVfx` resolves `"TorchFireBone/SparkParticles"` and `"Beam"`, driven by **3 named events** `sparks_start` / `sparks_end` / `laser_fire` (`Nodes/Vfx/NKinPriestVfx.cs:86-106`); the model reaches into it directly, `GetSpecialNode<NKinPriestBeamVfx>("Visuals/Beam")?.Fire()` (`KinPriest.cs:155`). `NKinPriestGrenadeVfx` is a third node. `NKinFollowerVfx` resolves two `NBasicTrail` nodes on `Boomerang1Slot`/`Boomerang2Slot` plus `HaySlot/HayParticles`, driven by **5 named events** `start_trail1` / `end_trail1` / `start_trail2` / `end_trail2` / `start_hay` (`Nodes/Vfx/NKinFollowerVfx.cs:102-128`); the follower model also reads `"Visuals/AttackDistanceControl"` (`:149`). 5 bespoke textures. **SFX namespaces `the_kin_priest` and `the_kin_minion`, neither of which is the follower's id — and the follower's `HurtSfx` points at the priest's namespace** (`KinFollower.cs:34-61`). **Boss surfaces:** `CustomBgm` `event:/music/act1_boss_the_kin`; parameter `the_kin_progress`; custom background 11 layers; placeholder map-icon pair. | **L** | RESEARCH. Gallery `:33`: 3 candidates, **all rated S** — "both human factions own 'flee'; Eremites also own the exact composition." Not on the redesign-pressure list. **No weekly-boss layer.** | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S4 **FINAL**, S5 *(prov.)*, S6 **PARTIAL**, **B1 · B2 · B3 · B4** |
| E8 | **Waterfall Giant** (boss, `WaterfallGiantBoss`, solo) — **RESEARCH** | **1 rig.** skel 187 835 B, atlas **4 938 B — the largest atlas in Act 1**; scene **18 344 B**. | **10 clips** — `idle_loop`, `cast`, `attack`, `attack_buff`, `attack_debuff`, `heal`, `hurt`, `die`, **`die_loop`** (looping) and **`erupt`** (`Monsters/WaterfallGiant.cs:333-358`). `Dead` and `Hit` are both suppressed while `IsAboutToBlow` (`:353-354`), i.e. the death-bomb state has no hurt and no ordinary death. **`HasDeathSfx => false`** (`:155`). Tells: five moves that all add `SteamEruptionPower`, a heal that scales with player count (`:266-268`), and a scripted self-kill with an HP overwrite to 999 999 999 first (`:297`, `:305`). | Solo, fixed HP. Camera 0.9. No slots, no encounter scene. | **The heaviest event contract in the game's monster set.** `NWaterfallGiantVfx` performs **12 hard `GetNode` lookups** — `SteamSlot1..6/steamParticles1..6`, `SteamLeakSlot1..3/steamLeakParticles1..3`, `MistSlot/MistParticles`, `MistSlot/Droplets`, `MouthDropletsSlot/MouthDroplets` (`Nodes/Vfx/NWaterfallGiantVfx.cs:249-260`) plus three leak shader materials — and switches on **15 named Spine events**: `buildup1/2/3`, `clear_death_steam`, `explode`, `steam_{1,2,3,5}_{start,end}`, `waterfall_start`, `waterfall_end`. **Dynamic layered track:** `_tracks/buildup{1|2|3}` on track 1, index derived from `PressureBuildupIdx` at runtime (`:327`). 3 bespoke water textures. **Audio is the most elaborate in the game:** `CustomBgm` `event:/music/act1_b_boss_waterfall_giant`, parameter `waterfall_giant_progress`, **plus a parameter set on its own ambient SFX event**, `SfxCmd.SetParam(…waterfall_giant_ambient, "waterfall_giant_sfx", v)` (`:311`, `:322`). Custom background with **only 2 layer scenes**; placeholder map-icon pair. | **L** | RESEARCH. **On the gallery's §1 redesign-pressure list** (`:99`): one claimant (boss-scale Large Pyro Slime) **with the element inverted** — a waterfall giant becoming a fire slime. "Thin." **No weekly-boss layer.** | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S6 **PARTIAL**, **B1 · B2 · B3 · B5** |
| E9 | **Soul Fysh** (boss, `SoulFyshBoss`, solo) — **RESEARCH** | **1 rig, 2 textures.** skel **410 487 B**, atlas 1 262 B, textures 514 972 B + `soul_fysh_2.png` 6 214 B; scene 2 099 B. | **13 clips — the most of any single Act-1 body** — `idle_loop`, `cast`, `attack_heavy`, `attack_beckon`, `attack_debuff`, `beckon`, `hurt`, `die`, plus a **complete intangible sub-body**: `intangible_start`, `intangible_loop` (looping), `intangible_end`, `hurt_intangible`, `die_intangible` (`Monsters/SoulFysh.cs:208-240`). **`Hit` and `Dead` both branch on `IsInvisible`** — the throttled state has its own hurt and its own death. Spawn/loop powers: `IntangiblePower` 2 on cast (`:203`), `VulnerablePower` on the scream (`:193`). | Solo, fixed HP. No slots, no encounter scene, no camera override. | **Bespoke.** `NSoulFyshVfx` wraps two scene nodes in `MegaSlotNode`s — `"Soundwave"` and `"Beckonwave"` (`Nodes/Vfx/NSoulFyshVfx.cs:98-101`) — and is driven by **4 named events**, `soundwave_start` / `soundwave_end` / `beckon_start` / `beckon_end` (`:112-123`). 3 bespoke textures (`beckonwave`, `soundwave`, `soundwave_edge_mask`). Explicit `HurtSfx` and four SFX consts (`:30-48`); `TakeDamageSfxType.Magic`. **Boss surfaces:** `CustomBgm` `event:/music/act1_b_boss_soul_fysh`; **two** music parameters — `soulfysh_progress` *and* a boolean-shaped `beckon` (`:87`, `:106`, `:188`, `:200`); custom background with **14 layer scenes**; placeholder map-icon pair. | **L** | RESEARCH. **On the gallery's §1 redesign-pressure list, at the bottom** (`:96`): **zero candidates in any of the 16 families** — "Beckon-pollution + Intangible throttling went unclaimed by every family." **No weekly-boss layer**, so this body currently has **no candidate from either gallery**. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S6 **PARTIAL**, **B1 · B2 · B3** |

### 2a. The one Underdocks elite the gallery maps

The gallery's **UNDERDOCKS** block (`reskin-gallery.md:75-84`) is Act-1-alternate
research and was **not** in `s18-act1.md`'s scope — that file scoped itself to
the "ACT 1 — Overgrowth" and "ACT 1 boss pool" headers (`s18-act1.md:159-160`).
One of its rows is an elite and therefore mine.

| # | Encounter (gallery row) | Asset / rig family | Required tells / states | Variants / reuse | VFX / audio surface | Complexity | RESKIN vs REDESIGN | Socket |
|---|---|---|---|---|---|---|---|---|
| E10 | **Skulking Colony** (elite, `SkulkingColonyElite`, solo) — **RESEARCH**, gallery `:83` | **1 rig, 2 texture pages.** skel **320 905 B**, atlas 3 310 B, textures 281 742 B + 243 436 B; scene **10 153 B**. | **7 clips** — `idle_loop`, `cast`, `attack_buff`, `attack_heavy`, `attack_double`, `hurt`, `die` (`Monsters/SkulkingColony.cs:106-125`). Spawn-time **`HardenedShellPower` 20** in `AfterAddedToRoom` (`:56`) — the damage-cap read the gallery's row is about. | Solo, fixed HP, no slots, no encounter scene. | **Bespoke, and it is the only elite or boss in the game with a phobia *skin*.** `protected override bool HasPhobiaSpineSkin => true` (`:33`) — one of only five overrides in the whole assembly (the others are `TwigSlimeM`, `TheObscura`, `FossilStalker`, `HauntedShip`), so the rig must carry Spine skins named exactly `normal` and `phobia`. `NSkulkingColonyVfx` resolves `"../ParticleSlot1/Particles"`, `"../ParticleSlot2/ParticlesWide"`, `"../ParticleSlot3/Particles"` and switches on **3 named events** `take_damage` / `take_fatal_damage` / `final_poof` (`Nodes/Vfx/NSkulkingColonyVfx.cs:82-105`). 1 bespoke texture. Explicit `HurtSfx` + four SFX consts (`:25-35`); `TakeDamageSfxType.Stone`. | **L** — bespoke event-driven driver **plus** an accessibility skin obligation. | RESEARCH (Underdocks harvest only). Gallery `:83`: **1 candidate, rated P** (Large Cryo Slime) — "per-turn damage cap is the truest elemental-shield translation; 'colony' read lost on one body." **The thinnest coverage of any elite in the atlas.** No weekly-boss layer. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S5 *(prov.)*, S6 **PARTIAL** |

---

## 3. The complexity scale used above

The three act files state the scale slightly differently. I use `s18-act2.md`
§3's formulation because it is the most complete, and I say so wherever a letter
would differ under Act 1's narrower wording.

- **S** — one Spine rig; ≤6 clips; hit VFX drawn only from the shared
  `res://scenes/vfx/vfx_attack_{slash,blunt,lightning}.tscn` /
  `vfx_bite.tscn` / `vfx_gaze.tscn` / `vfx_heavy_blunt.tscn` set; no bespoke
  particle nodes; no named Spine attach bones/slots; no named Spine animation
  events; no skin obligation; no layered track.
- **M** — an S body plus **exactly one** of: a second rig, a named attach
  bone/slot, an encounter scene with named body slots, a skin obligation, a
  branched sub-state graph, or a layered `tracks/` animation.
- **L** — several rigs, **or** a bespoke `N…Vfx` script node driven by named
  Spine animation events, **or** more than one M-grade extra on one row.

**The elite/boss set splits 3 S / 1 M / 18 L (22 rows).** For comparison the
three act files' normal-encounter sets split 3 S / 0 M / 3 L (Act 1),
2 S / 3 M / 8 L (Act 2), 1 S / 4 M / 6 L (Act 3) — 6 S / 7 M / 17 L over 30
rows. **Eighty-two per cent of elite and boss rows are L, against fifty-seven
per cent of normals.** The whole cheap end of this file is four rows: **Byrdonis**
and **Infested Prism** (genuine S), **Bygone Effigy** (M), and **Aeonglass**,
whose letter is degenerate (†).

Four things the letters do **not** capture, carried so the joined matrix can
show them separately:

- **The boss surcharge is invisible in the letter.** A boss's map node,
  background-layer directory and music event/parameter are `EncounterModel`
  surfaces, not creature surfaces, so they never move an S/M/L letter. Eleven of
  the twelve boss rows carry all three; no elite carries any. §4 tabulates it.
- **Clip count is not priced.** Soul Fysh (13), Ceremonial Beast (11), Knowledge
  Demon (11), Waterfall Giant (10) and Test Subject (**23**) are all "L", but
  their animation bills differ by a factor of two.
- **Hard node-lookup count is not priced.** Waterfall Giant's driver makes 12
  hard lookups, Torch Head Amalgam's 12, Test Subject's 11, Knowledge Demon's 8,
  Kaiser Crab's 9 — against 1–3 for a typical normal.
- **† Aeonglass's letter is meaningless.** It has no Spine rig at all, so the
  scale — which is defined on rig content — returns "cheap" for a body that
  has nothing to reskin *against*. See row B11 and §7.

---

## 4. Act 2 and Act 3 — elites and bosses

| # | Encounter (gallery row) | Asset / rig family | Required tells / states | Variants / reuse | VFX / audio surface | Complexity | RESKIN vs REDESIGN (as the atlases record it) | Socket |
|---|---|---|---|---|---|---|---|---|
| E11 | **Decimillipede** (Act 2 elite, `DecimillipedeElite`, 3 bodies) | **3 skeletons + a prop rig.** `decimillipede1/2/3.skel` 145 410 / 150 706 / 135 047 B, three atlases ≈5 065 B each, **shared** texture 820 672 B, plus `rockstone` (5 403 B). Scenes: `decimillipede.tscn` **52 474 B** plus three segment scenes 16 865 / 15 470 / 16 262 B. Room scene 459 B. | **5 clips on the shared base class** — `idle_loop`, `hurt`, `dead_loop` (looping), `wither`, `regenerate` (`Monsters/DecimillipedeSegment.cs:264-279`). **There is no attack clip.** The attack is not an `AnimState` at all: `SegmentAttack()` is abstract (`:281`) and each subclass reaches a node by path and calls a method on it (see next column). Spawn-time **`ReattachPower` 25** (`:143`) — the mechanic the gallery says has no analogue anywhere. | **Three subclasses exist for one reason: to resolve three different `VisualsPath`s.** The decompiled class comment says so verbatim — *"Monster class exists to connect this to the correct monster visual scene. All logic lives in the DecimillipedeSegment."* (`Monsters/DecimillipedeSegmentFront.cs:5-8`). Slots `segment1`/`segment2`/`segment3`, opening move index rotated per body (`Encounters/DecimillipedeElite.cs:35-48`); camera 0.87 / +50 y. | **The most unusual driver architecture in the game.** Attacks route through `GetSpecialNode<NDecimillipedeSegmentDriver>` at exact paths — `"%Visuals/SegmentDriver"` on front and back, and **two** paths `"%Visuals/RightSegmentDriver"` + `"%Visuals/LeftSegmentDriver"` on the middle body (`DecimillipedeSegmentMiddle.cs:15-16`). `NDecimillipedeSegmentVfx` adds **2 named events** `explode` / `suck_complete`; `NDecimillipedeRocksVfx` is a fourth node. **Phobia is six id-derived textures**, `monsters/phobia_mode/<id>_phobia.png` and `<id>_shriveled_phobia.png`, loaded with `ResourceLoader.Load` and swapped onto the alternate body when `Visuals.IsUsingPhobiaModeBody` (`DecimillipedeSegment.cs:45-47`, `:112-114`, `:219`, `:251-258`) — 241–278 KB each. 5 bespoke textures incl. three shader textures. Explicit heal / die / attack_triple / attack_buff / attack_weaken SFX in the `decimillipede` namespace. | **L** | SHIPPED. **Top of the gallery's §1 redesign-pressure list** (`:95`): the only claim is a **self-declared stretch** (3× Hilichurl Guard, "offered mainly to show the gap"); **Reattach has no analogue in any of the 16 families** — "shipped content with no reskin cover is the highest-priority gap here." No weekly-boss layer (elite). | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S4 **FINAL**, S5 *(prov.)*, S6 **PARTIAL**, **B4 (soft ×4)** |
| E12 | **Entomancer** (Act 2 elite, solo) | **1 rig.** skel 119 168 B, atlas 1 288 B, texture 136 038 B; scene **8 253 B**. | **6 clips** — `idle_loop`, `cast`, `attack`, `attack_ranged`, `hurt`, `die`, the extra one on a **lower-case trigger `attack_ranged`** (`Monsters/Entomancer.cs:91-106`) — the only lower-case trigger name at this tier. | Solo, no adds, no slots, no encounter scene, no camera override (`Encounters/EntomancerElite.cs:7-16`). | **Bespoke.** `NEntomancerVfx` resolves `"SwarmParticles"`, the nested `"SwarmParticles/AttackingBugParticles"`, and `"SwarmTargetNode"`, drives a Tween across the arena, and switches on **2 named events** `launch_swarm` / `turn_off_swarm` (`Nodes/Vfx/NEntomancerVfx.cs:123-166`). 1 bespoke texture. **Phobia is a texture, and its filename inverts the Decimillipede's convention:** `pck:images/monsters/phobia_mode/phobia_entomancer.png` (398 434 B) — `phobia_<id>`, not `<id>_phobia`. Hit VFX `vfx/vfx_attack_slash` ×2. Explicit ranged-attack and die SFX. | **L** | SHIPPED. **On the gallery's §1 redesign-pressure list** (`:98`): 2 candidates, **neither strong**, "both claims carry an inverted-incentive caveat" — the Churldric's pot punishes *not* hitting it, the exact opposite polarity (`:114`, existence VERIFIED 2026-08-13). No weekly-boss layer. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S5 *(prov.)*, S6 **PARTIAL** |
| E13 | **Infested Prism** (Act 2 elite, solo) | **1 rig.** skel **57 335 B — the lightest body in Act 2**, atlas 993 B, texture 156 462 B; scene **1 382 B — the bare 4-node contract**. | **7 clips** — `idle_loop`, `buff`, `attack`, `attack_block`, `attack_double`, `hurt`, `die`, on bespoke `AttackBlock`/`AttackDouble` triggers (`Monsters/InfestedPrism.cs:119-137`). Fixed HP. | Solo, no adds, no slots, no encounter scene, no camera override. Rig used by no other encounter. (Two sibling rigs, `infested_guardian` and `infested_purifier`, exist in the pack and belong to other bodies.) | **Nothing bespoke: no driver, no attach nodes, no Spine events, no skin, no layered track.** Shared `vfx/vfx_attack_slash` ×4. All four SFX are explicit and sit in the **`infested_prisms` (plural) namespace, not the id** (`:20-32`); `TakeDamageSfxType.Stone`. `ExtraAssetPaths` = the **`Tainted` affliction overlay** (`Encounters/InfestedPrismsElite.cs:12`). | **S** — the only S-grade elite in Act 2, and after Byrdonis the cheapest elite or boss body in the game. | SHIPPED. Gallery `:52`: **6 candidates, five rated S** — "four legitimate strongs; pick by which family anchors Act 2's elites." Not on the redesign-pressure list. No weekly-boss layer. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)* |
| E14 | **Knowledge Demon** (Act 2 boss, solo) | **1 rig, the second-largest in the game.** skel **723 441 B**, atlas 4 792 B, texture 674 250 B; scene **83 838 B — second-largest creature-visuals scene**. | **11 clips** — `idle_loop`, `attack_light`, `attack_medium`, `attack_heavy`, `brain_rot`, `heal`, `burnt_loop` (looping), `hurt`, `die`, **`hurt_burnt`**, **`die_burnt`** (`Monsters/KnowledgeDemon.cs:224-251`). **`Hit` and `Dead` both branch on `_isBurnt`** — a burnt second body state with its own hurt and death. Five bespoke triggers (`LightAttackTrigger`, `MediumAttackTrigger`, `HeavyAttackTrigger`, `MindRotTrigger`, `HealTrigger`). Fixed HP. | Solo, no adds, no slots, no encounter scene. Camera 0.85 / **+70 y** — the largest vertical offset of any elite or boss. | **Bespoke and dense.** `NKnowledgeDemonVfx` makes **8 hard `GetNode` lookups** — four `FireSlot{1..4}/FireHolder{1..4}` pairs plus `ExplosionParticles`, `DamageParticles`, `EmberParticles`, `ThinEmberParticles` (`Nodes/Vfx/NKnowledgeDemonVfx.cs:158-167`) — switches on **8 named events** (`burning_start/end`, `embers_start/end`, `explode`, `take_damage`, `thin_embers_start/end`), **and additionally hooks `ConnectAnimationStarted`, keyed on the clip name `idle_loop`**. 1 bespoke texture, in the base game's own misspelled directory `pck:images/vfx/monsters/knowledge_demom/`. Hit VFX `vfx/vfx_attack_blunt` with an explicit `blunt_attack.mp3` ×3. Three explicit SFX consts. **Boss surfaces:** `CustomBgm` `event:/music/act2_boss_knowledge_demon`; parameter `knowledge_demon_progress` (3 values); custom background 11 layers; placeholder map-icon pair. | **L** | SHIPPED. **On the gallery's §1 redesign-pressure list** (`:98`): 2 candidates, **neither strong** — the Lector is a tier promotion with no self-heal analogue for Ponder, and the Mystifying Megachurl is **retired limited-time event content (v4.4)** with screenshot-only imagery (`:115`). **Weekly-boss layer** (`candidates.md:40`): recommended **Shouki no Kami** — "the literal name match, and the one slot where atlas cover is explicitly soft" (`candidates.md:790-792`). This is the one slot where both galleries agree the weekly layer is the stronger source. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S6 **PARTIAL**, **B1 · B2 · B3 · B6** |
| E15 | **Kaiser Crab** (Act 2 boss, 2 bodies, **1 skeleton**) | **Two bodies on ONE rig.** `kaiser_crab_skeleton_data.tres`, skel 218 157 B across **four texture pages** — 927 636 / 638 116 / 735 706 / 985 318 B = **3.3 MB, the largest texture budget of any body in the game**. Scenes: `kaiser_crab_boss_setup.tscn` **17 036 B** with thin wrappers `crusher.tscn` 894 B and `rocket.tscn` 872 B, plus `kaiser_crab_boss.tscn` 822 B. Room scene 387 B. | **Default 5 clips each.** Neither `Crusher` nor `Rocket` overrides `GenerateAnimator`, so both inherit `idle_loop`/`cast`/`attack`/`hurt`/`die` (`Models/MonsterModel.cs:602-619`) — on the *same* skeleton. Both are fixed-HP (`Crusher.cs:77-79`, `Rocket.cs:57-59`). Each hand-plays SFX per move and each writes the shared music parameter on death. | **Two slots `crusher` / `rocket`** (`Encounters/KaiserCrabBoss.cs:29`, `:49-55`). `FullyCenterPlayers => true` (`:27`) — **the only encounter in the game with it**. Camera **0.75 / +35 y**, the most aggressive camera override in the roster. | **Bespoke, two drivers.** `NKaiserCrabBossVfx` makes **9 hard lookups** (`RegenSplatSlot`, `PlowChunkSlot`, `RocketSlot/{SteamParticles1..3, SparkParticles, SmokeParticles}`, `%LeftArmExplosionPosition`, `SpittleSlot`) and switches on **11 named events** (`charge_steam_start/end`, `claw_explode_l`, `death_spit_start/end`, `plow_chunks_start/end`, `regen_splats_start/end`, `rocket_thrust_start/end`), **plus `ConnectAnimationStarted`** (`Nodes/Vfx/NKaiserCrabBossVfx.cs:184-207`). `NKaiserCrabBossExplosionVfx` adds a tenth lookup and a twelfth event `left_embers_start`. 1 bespoke texture. **One SFX namespace `kaiser_crab` serves both bodies**, split by `_left_`/`_right_` infixes; `Rocket` uses `SfxCmd.PlayLoop` / `StopLoop` for its charge (`Rocket.cs:131`, `:155`, `:162`). **Boss surfaces:** `CustomBgm` `event:/music/act2_boss_kaiser_crab`; parameter `kaiser_crab_progress` (declared as a named const on the encounter, `KaiserCrabBoss.cs:11`); custom background 11 layers; placeholder map-icon pair. | **L** — **but costing note: two bodies, one rig.** Do not price it as two skeletons. | SHIPPED. Gallery `:54`: 5 candidates, **3 rated S** — "Coral Defenders is the only one that is natively a single boss encounter." **Weekly-boss layer** (`candidates.md:41`): **La Signora, explicitly "under protest"** — `candidates.md:767-775` records the structural finding that **no Genshin weekly boss is a matched pair**, so every weekly candidate must either flatten a sequential two-form boss into a simultaneous one or promote adds to co-boss stature. **⚑ The fork lands atlas-side here on merit** (`candidates.md:781-782`). | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S4 **FINAL**, S6 **PARTIAL**, **B1 · B2 · B3 · B6** |
| E16 | **The Insatiable** (Act 2 boss, solo) — **DROPPED in the sim** (`tier05/content/act2_pool.yaml:215-217`), live in the base game and **first in `Hive::BossDiscoveryOrder`** | **1 rig + a real map-node rig.** skel 281 635 B, texture 863 412 B; scene **12 699 B**; `the_insatiable_boss_node` (skel 15 108 B) is a **genuine Spine map node**, not a placeholder pair. Dedicated room props under `pck:images/rooms/hive/the_insatiable/`. | **10 clips** — `intro_loop` (initial, looping), `liquify_sand`, `idle_loop` (looping), `salivate`, `attack_thrash`, `attack_bite`, **`eat_player`**, `intro_hurt`, `hurt`, `die` (`Monsters/TheInsatiable.cs:175-202`). **`Hit` branches on `HasLiquified`** — a two-phase body with a pre-liquify hurt. `EatPlayerAnim` is a **public static string** (`:56`) because the bestiary builds a compendium row straight off the clip name, `BestiaryMonsterMove.FromAnim(…, EatPlayerAnim, …)` (`:209`) — a clip name that is also a data key. | Solo, no adds, no slots, no encounter scene. Camera 0.9. | **Bespoke.** `NTheInsatiableVfx` resolves `SalivaSlotNode/{SalivaFountain,SalivaDrool,SalivaCloud}Particles` and `BaseBlastSlot/BaseBlastParticles`, switches on **7 named events** (`base_blast_start/end`, `death_end`, `drool_start/end`, `saliva_start/end`) **and hooks `ConnectAnimationStarted` on clips `attack_thrash` / `salivate`** (`Nodes/Vfx/NTheInsatiableVfx.cs:132-146`). 2 bespoke textures. **Phobia is a texture — `the_insatiable_phobia.png` at 1 298 132 B, the largest phobia texture on any *monster* in the game** (the pack's single largest phobia asset is an *event* portrait, `zen_weaver_phobia_mode.png`, 2 779 572 B). Hit VFX `vfx/vfx_scratch` and `vfx/vfx_bite`. Five explicit SFX consts. **Boss surfaces:** `CustomBgm` `event:/music/act2_boss_the_insatiable`; **`AmbientSfx` override `event:/sfx/ambience/act2_ambience_the_insatiable` — the only monster encounter in the game with one** (`Encounters/TheInsatiableBoss.cs:15`); music parameter; custom background with **8 layer scenes**; **real Spine map node**. | **L** | DROPPED (sim), live (base). Gallery `:55`: 5 candidates, **2 rated S** — "opens by creating exactly 4 arena Concretions (= 4 Sandpits)". Not on the redesign-pressure list. **No weekly-boss layer** — `candidates.md` drafted the two *shipped* Act-2 slots only. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S5 *(prov.)*, S6 **PARTIAL**, **B1 · B2 · B3 · B6** |
| E17 | **Knight Gang** (Act 3 elite, `KnightsElite`, 3 bodies) | **3 rigs, and they are wildly unequal.** flail: skel 141 092 B, atlas 1 658×523 / 48 regions, scene **1 159 B — the bare 5-node contract**, i.e. an S body. spectral: skel 140 599 B, 994×532 / 27 regions, scene **17 908 B** (11 nodes). magi: skel 157 969 B, 1 313×252 / 21 regions, scene **6 676 B** (12 nodes). Room scene `pck:scenes/encounters/knights_elite.tscn` **451 B — three `Marker2D`s named `first`/`second`/`third`**, nothing else. | Flail: **6 clips** — `idle_loop`, `buff`, `attack_flail`, `attack_ram`, `hurt`, `die` on `FlailAttack`/`RamAttack` (`Monsters/FlailKnight.cs:86-101`). Spectral: **6** — `idle_loop`, `debuff`, `attack_sword`, `attack_flame`, `hurt`, `die` (`SpectralKnight.cs:90-105`). Magi: **6** — `idle_loop`, `attack_bomb`, `attack_ram`, `cast_shield`, `hurt`, `die`, with `Cast` and `BombCast` **both** mapped to `attack_bomb` (`MagiKnight.cs:151-167`). All three `TakeDamageSfxType.Armor`. **Reconciliation:** `s18-act3.md:179` lists a seventh flail clip `attack_breaker`; the code drives six — if the clip exists it is undriven rig content. | Three bodies, three rigs, fixed slots. Camera 0.87 / +50 y. `ExtraAssetPaths` = the **`Hexed` affliction overlay**. **`KnightsElite` is the only elite or boss in the game that declares an `EncounterTag`** (`EncounterTag.Knights`, `Encounters/KnightsElite.cs:14`) — every other elite and boss is untagged and so sits outside the anti-repeat family system. | Flail: **nothing bespoke at all**. Spectral: `NSpectralKnightVfx` with three GPU emitters (`FlameParticlesAdd`, `FlameParticlesFlat`, `CinderParticles`) plus a `HeadFireNode` `SpineSlotNode` carrying a `TextureRect` on a stepped fire shader; **2 named events** `flame_start` / `flame_end`, **plus `ConnectAnimationStarted` keyed on clip `attack`** (`Nodes/Vfx/NSpectralKnightVfx.cs:92-102`); 2 bespoke textures. Magi: a `SpineSlotNode` carrying three shared `fire_*_small` CPU emitters, plus a `SpineBoneNode` named **`AttackDistanceControl`** that the model reads (`MagiKnight.cs:128`); explicit `HurtSfx`. | **L** — three rigs. | SHIPPED **aura-less** (`tier05/content/act3_pool.yaml:158-183`). Gallery `:69`: 6 candidates, **4 rated S**; "since the shipped gang is aura-less, the aura arguments are about future-proofing, not current fit." Not on the redesign-pressure list. No weekly-boss layer. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S4 **FINAL**, S6 **PARTIAL**, **B4 (soft) · B6** |
| E18 | **Mecha Knight** (Act 3 elite, solo) | **2 rigs for one body.** main skel 141 384 B, atlas 1 270×523 / **63 regions — the most of any Act-3 body**; **plus a VFX-only Spine rig** `pck:animations/vfx/vfx_mecha_knight_shield/*` (skel 22 167 B). Scene **19 285 B, 15 nodes**. | **9 clips** — `idle_loop`, `hurt`, `die`, `attack_flame`, `attack_cleave`, `charge`, `wind_up`, **`idle_loop_wound`** (looping), **`hurt_wound`** (`Monsters/MechaKnight.cs:141-175`). **`Hit` is branch-wired fourteen times**, seven to `hurt` and seven to `hurt_wound`, gated on `IsWoundUp` (`:162-175`) — a damaged-state art obligation on both the idle and the hurt. Triggers `flamethrower` / `charge` / `windUp` are lower-case/camelCase, unlike the roster norm. | Solo, no adds, no slots, no encounter scene. Camera 0.9 / +50 y. | **Bespoke.** `NMechaKnightVfx` makes **6 hard lookups** across two attach chains — `EngineSlot/EngineBone/{EngineParticles, EngineParticlesDark}` and `FlameParticlesBone/{FlameParticlesDark, FlameParticlesLight, CinderParticles, GlowParticles}` — and switches on **4 named events** `flame_start` / `flame_end` / `engine_start` / `engine_stop` (`Nodes/Vfx/NMechaKnightVfx.cs:123-148`). Note the asymmetric naming (`_end` vs `_stop`). Explicit `HurtSfx` and `DeathSfx` in the **`mechaknight` namespace, which is not the id** (`:40-58`). Both attacks pass `null` as the hit-VFX scene and supply only a sound (`:102`, `:111`) — unusual. | **L** — a second rig **and** a bespoke event-driven driver. | SHIPPED. Gallery `:70`: **9 candidates, five rated S — "deepest strong bench in the atlas"**; the Burn-pollution beat is the discriminator and #1–4 all carry it natively. §4 flags Artifact 3 UNIMPLEMENTED. **§3 correction on the record:** the Sidorenko candidate is **factually mismatched** — Sidorenko is the *Cryo* Tri-Star, wrong element for a Burns body (`:116`). No weekly-boss layer. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S6 **PARTIAL** |
| E19 | **Soul Nexus** (Act 3 elite, solo) | **1 rig.** skel 245 709 B, atlas 1 063×656 / 29 regions, texture 334 332 B; scene **7 031 B, 14 nodes**. | **Default 5 clips.** `SoulNexus` does **not** override `GenerateAnimator` — the cheapest animator of any elite or boss, and the gallery's "gimmick-free stat block" note is exactly right about *this half*. Move machine is a three-way `RandomBranchState` with cannot-repeat (`Monsters/SoulNexus.cs:70-72`). `TakeDamageSfxType.Magic`. | Solo, no adds, no slots, no encounter scene, no camera override. | **Cheap animator, expensive VFX — the widest split in the roster.** `SetupSkins` starts a **layered track `tracks/writhe`** on track 1 and the model swaps it to `tracks/empty` at two points (`:38-40`, `:52`, `:59`). `NSoulNexusVfx` drives **three `SpineSlotNode` → `Line2D` trails** (`PathSlot1/2/3`) and a `HeadFireSlot` `TextureRect` on `shaders/vfx/vfx_stepped_shader_fire_flat.tres`, switching on **8 named events** — `path_1_start/stop`, `path_2_start/stop`, `path_3_start/stop`, `show_fire`, `hide_fire`. 1 bespoke texture (`soul_nexus_head_fire_base.png`) over four shared noise/gradient textures. Hit VFX `vfx/vfx_attack_slash` ×2. | **L** — bespoke event-driven driver **plus** a layered track. | SHIPPED. Gallery `:71`: 4 candidates, **2 rated S** — "Gimmick-free stat block: donor body is a free pick, Lector is tier-exact." **Read that against the split above:** the animator is free, the fire-and-trail VFX is not. Not on the redesign-pressure list. No weekly-boss layer. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S6 **PARTIAL**, **B5** |
| E20 | **Test Subject** (Act 3 boss, solo, 3 rigs) | **The largest single art contract in the game.** main skel **1 161 899 B — larger than the next-biggest monster skeleton by 60 %**, atlas 1 985×491 / 81 regions, texture 513 460 B; plus two dedicated burn-VFX Spine rigs `test_subject_burn_front` / `_back`. Scene **139 319 B, 30 nodes — the largest creature-visuals scene in the game**. | **23 clips**, three numbered phase variants of one body: `idle_loop{1,2,3}`, `hurt{1,2,3}`, `attack_double{1,2,3}`, `attack_big{1,2,3}`, `heal{1,2,3}`, `knockout{1,2}`, `knocked_out_loop{1,2}`, `regenerate{1,2}`, `burn`, `die` (`Monsters/TestSubject.cs:350-414`). **Every reactive trigger is registered three times, gated on `Respawns == 0 / == 1 / >= 2`** (`:397-412`). Two of the clips carry **`BoundsContainer` overrides** — `regenerate1` → `"RespawnBounds1"`, `regenerate2` → `"RespawnBounds2"` (`:357-371`), so the hitbox changes shape mid-respawn. `DeathSfx` is a **switch on phase** (`:105-118`). | Solo, no adds, no slots, no encounter scene, no camera override (`Encounters/TestSubjectBoss.cs:8-25`). | **Bespoke and the densest in the game.** `NTestSubjectVfx` makes **11 hard lookups**, six of them escaping the visuals subtree with `../../` (`EmberParticles`, `FlameParticles`, `BurnParticles`, `TargetedBurnParticle`, `BurnParticleFountain`, `CeilingSparks`) plus `NeckParticlesSlot/{NeckParticles, DizzyPaticles}` [*sic*, the base game's own typo] and two nested `MegaSprite` wrappers on `../FrontBurnVfxSlot/FrontBurnVfx` and `../BackBurnVfxSlot/BackBurnVfx` (`Nodes/Vfx/NTestSubjectVfx.cs:181-191`). **10 named events** plus **`ConnectAnimationStarted` keyed on clip names `burn` / `die3` / `idle_loop3` / `empty`**. `NTestSubjectBurnVfx` is a second driver. The model also reaches `GetSpecialNode<CanvasGroup>("%CanvasGroup")` to tint the whole body (`:345`). 2 bespoke textures. **Boss surfaces:** `CustomBgm` `event:/music/act3_boss_test_subject`; parameter `test_subject_progress` (3 values); custom background 12 layers; placeholder map-icon pair. | **L** | SHIPPED. Gallery `:72`: 4 candidates, **1 rated S** (Iniquitous Baptist, "the only body in Teyvat built as phase-gated moveset swaps"); §3 records a **factual correction upgrading** the Prism Slime claim — canon is a gauge that fills and makes it big and vulnerable, and its element-absorption immunity is a near-literal Adaptable (`:113`). **Weekly-boss layer** (`candidates.md:42`): recommended **Guardian of Apep** — "the only remaining true sequential-full-bar body with Childe fixed" (`candidates.md:803-811`). **⚑ The fork lands atlas-side here on merit** (`candidates.md:783-784`). | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S6 **PARTIAL**, S8 *(prov.)*, **B1 · B2 · B3 · B4 · B6** |
| E21 | **Aeonglass** (Act 3 boss, solo) | **NO SPINE RIG EXISTS.** There is no `animations/monsters/aeonglass/` entry anywhere in the 15 658-entry pack index. `pck:scenes/creature_visuals/aeonglass.tscn` is **1 134 B, five nodes**: root `Node2D` named **`Doormaker`**, `Visuals` of type **`Sprite2D`** (on `pck:images/monsters/hourglass_placeholder.png`), `Bounds`, `CenterPos`, `IntentPos`. | **No animator is built at all.** `Aeonglass` overrides no `GenerateAnimator`, and because `%Visuals` is not a `SpineSprite`, `NCreatureVisuals` never sets `SpineBody`, `HasSpineAnimation` is false, and `NCreature._Ready` skips animator construction entirely (S13 §4.4; `Nodes/Combat/NCreatureVisuals.cs:185`, `Nodes/Combat/NCreature.cs:503`). Its own moves still call `WithAttackerAnim("Attack", 0.15f)` (`Monsters/Aeonglass.cs:114`, `:123`) — those calls **no-op through a null animator**. Spawn: `WitheringPresencePower` 6 **per player** plus `ArtifactPower` 3 (`:74-84`). | Solo, no adds, no slots, no encounter scene. Camera 0.9 / +60 y. | Shared `vfx/vfx_attack_blunt` ×2. **No Sfx overrides at all** — everything id-derived; `TakeDamageSfxType.Stone`. **Boss surfaces, and every one of them is borrowed or absent:** `HasCustomBackground => **false**` — the only boss in the game without one, and there is no `scenes/backgrounds/aeonglass_boss/` directory; `CustomBgm` is **`event:/music/act3_boss_queen`**, i.e. the Queen's track; its music parameter is **`queen_progress`** (`Monsters/Aeonglass.cs:77`, `:93`); only the placeholder map-icon pair is its own. | **S by the letter — and the letter is meaningless.** There is no base animation set to reskin *against*. See §7. | SHIPPED. Gallery `:73`: 4 candidates, **1 rated S** — "the Wither ↔ Brand of the Abyssal Flame match, **the strongest single boss argument in the atlas**." **Weekly-boss layer** (`candidates.md:43`): recommended **Lord of Eroded Primal Fire** ("uncontended, well-sourced; frees Shouki for the literal slot"). **⚑ The fork lands atlas-side here on merit** (`candidates.md:785-787`). Note the collision the two facts make: the atlas's strongest boss argument sits on the one boss with no shipped animation. | S1 **FINAL**, S2 **FINAL (both halves — this is the non-Spine case S13 §4.4 describes)**, S3 *(prov.)*, **B1 · B3** |
| E22 | **Queen + Torch Head Amalgam** (Act 3 boss, `QueenBoss`, 2 bodies) — **DROPPED in the sim** (`tier05/content/act3_pool.yaml:12`) | **2 rigs, and the add is heavier than the boss.** queen: skel 298 083 B, atlas 2 033×515 / 41 regions, texture 310 510 B; scene **9 540 B, 18 nodes**. amalgam: skel 145 207 B, 1 459×240 / 44 regions; scene **64 486 B, 39 nodes — the fourth-largest creature-visuals scene in the game, on the *minion*.** Room scene 373 B (two `Marker2D`s). | Queen: **default 5 clips** — no `GenerateAnimator` override. Amalgam: **5 clips** — `idle_loop`, `debuff`, `attack`, `hurt`, `die` (`Monsters/TorchHeadAmalgam.cs:124-138`). **Reconciliation:** `s18-act3.md:184` lists six amalgam clips including `buff`; the code drives five — if `buff` exists it is undriven rig content. | Slots `amalgam` / `queen`, amalgam placed first (`Encounters/QueenBoss.cs:17`, `:43-49`). Camera 0.9 / +60 y. `ExtraAssetPaths` = the **`Bound` affliction overlay**. | **Two bespoke drivers, and the amalgam's is the most exacting node contract in the game.** Queen: `SetupSkins` starts **layered track `tracks/writhe`**, swapped to `tracks/empty` twice (`Queen.cs:112-114`, `:121`, `:238`); `NQueenVfx` with 2 named events `attack_start` / `attack_end` **plus `ConnectAnimationStarted` on clip `attack`** (`Nodes/Vfx/NQueenVfx.cs:78-85`); two `eyeSlot` `SpineSlotNode`s each carrying two `ColorRect`s on a fire shader, a `SpineParticleSlot`, three `SpineBoneNode`s, a `TalkPos`. Amalgam: `NAmalgamVfx` makes **12 hard lookups** across three fully mirrored torch sub-trees plus `laserBaseBone/laserBaseParticles`, `CPUDeathParticles` and three `torch{1,2,3}UnscaledBone/hitParticles` (`Nodes/Vfx/NAmalgamVfx.cs:189-212`), and switches on **10 named events** (`go_poof`, `hit1/2/3`, `laser_base_fire/off`, `laser_hit_fire/off`, `torches_on`, `torches_out`). **On top of that the model reaches four exact node paths itself**, three of them four levels deep (`TorchHeadAmalgam.cs:74-76`, `:100`). 4 bespoke textures. **Boss surfaces:** `CustomBgm` `event:/music/act3_boss_queen`; parameter `queen_progress` (3 values); custom background 12 layers; **a real Spine map node** (`pck:animations/map/queen_boss/*`, whose texture is named `boss_node_false_queen.png` — a third naming divergence). | **L** | DROPPED (sim), live (base). **At the top of the gallery's §1 redesign-pressure list** (`:94`): **zero claims across all 16 families** — "a puppeteer boss whose identity is Chains of Binding + a 99-stack debuff execution has no Genshin body shape in the surveyed families… it likely needs a bespoke design or a family outside this dispatch." **No weekly-boss layer.** So, like Soul Fysh, this row currently has **no candidate from either gallery** — while being one of the two most VFX-dense bodies in Act 3. | S1 **FINAL**, S2 **FINAL (scene half)**, S3 *(prov.)*, S4 **FINAL**, S6 **PARTIAL**, **B1 · B2 · B3 · B4 · B5 · B6** |

---

## 5. Coverage

### 5a. Every mapped elite and boss has a row

The three act files handed off **21** elite/boss pointer rows
(`s18-act1.md` §4 = 9, `s18-act2.md` §4 = 6, `s18-act3.md` §4 = 6). All 21 are
rows above (E1–E9, E11–E22). One further gallery row, **Skulking Colony**
(`reskin-gallery.md:83`), is an elite that no act file owned; it is row E10.
**Twenty-two rows, zero mapped elite/boss encounters dropped.**

Against the base game rather than the gallery: `Overgrowth`, `Underdocks`,
`Hive` and `Glory` between them declare elite and boss encounters that this set
covers, **except** for the Underdocks bodies the gallery groups into its
uncosted leftovers row (§5b) and any elite in a base act our pools do not model
(e.g. `PhrogParasiteElite` in Overgrowth, named in `s18-act1.md:182` as
unmapped). Those are scope calls and are [USER]'s.

### 5b. One gallery row is explicitly NOT costed

| Gallery row | Why not costed |
|---|---|
| **Terror Eel · Haunted Ship · Fossil Stalker · Calcified / Damp Cultists** (`reskin-gallery.md:84`, "elite/normals") | The gallery files five bodies of mixed tier under **one** row with **no candidates claimed**, and it is Underdocks research. Costing it would require splitting a gallery row into five, which is a change to an existing ordering and therefore not mine to make. Recorded facts only, no row: `FossilStalker` and `HauntedShip` both override `HasPhobiaSpineSkin => true` (two of the five in the game), and `pck` carries `terror_eel_phobia.png` (1 768 162 B) — so at least three of these five bodies carry an accessibility obligation. **Whether to split this row is a [USER] call** (question Q9, §9). |

### 5c. Where the shipped sim and the base encounter differ, at this tier

Not defects — the sim is a reduced model and flags its own skips. Listed because
each changes how many bodies need art.

| Row | Shipped sim | Base game | Consequence for art |
|---|---|---|---|
| Vantom | Slippery 9 and Wound injection UNIMPLEMENTED (`act1_pool.yaml:159`) | real powers | Gallery §4 already warns: "pick for the shipped 4-beat rotation, not the aspirational gimmick." |
| Lagavulin Matriarch | Plating 12 damage-cap skipped (`act1_pool.yaml:185`), Soul Siphon modelled as a buff/debuff beat pair (`:197-199`) | real `PlatingPower` + a real stat drain | Art must not promise a cap. |
| Ceremonial Beast · The Kin · Waterfall Giant · Soul Fysh | **not modelled at all** — research-only | four live base boss encounters, each with its own background, music and (for three of them) a placeholder map icon | A reader costing Act 1's boss art off the sim sees **two** bosses; the base act has **six**. This is the largest sim-vs-base gap at this tier. |
| Skulking Colony | not modelled | a live Underdocks elite with a phobia-skin obligation | Not visible from any pool file. |
| Exoskeleton-adjacent: Decimillipede | modelled as three segments (`act2_pool.yaml:161-176`) | three segments **plus** six phobia textures and a fourth prop rig | The phobia half is invisible from the sim. |
| The Insatiable | dropped (`act2_pool.yaml:215-217`) | live, and **first** in `Hive::BossDiscoveryOrder` | Its rig, background, ambient event and Spine map node all exist and are costed above. |
| Knight Gang | ships **aura-less** (`act3_pool.yaml:158-183`) | three auras, one per knight | Gallery `:69` already says the aura arguments are future-proofing. |
| Mecha Knight | Artifact 3 UNIMPLEMENTED (`act3_pool.yaml:187`) | real `ArtifactPower` | Art-unsafe per gallery §4. |
| Queen + Amalgam | dropped (`act3_pool.yaml:12`) | live; the *add* carries a 64 KB scene and a 12-lookup driver | A sim-only read shows nothing at all here. |

---

## 6. Socket table — S13's answers joined, plus six new keys

### 6a. S18's original keys S1–S8, after S13

`s18-act1.md` §6 and `s18-act2.md` §6 posed S1–S8 as **PROVISIONAL — S13
pending**. S13 has now landed (`review/dispatch3/s13-engine-sockets.md`). Here
is what it settled and what it did not. **I have changed no act file.**

| Key | S18's question | S13's verdict | Status |
|---|---|---|---|
| **S1** | Can a mod register a **hostile** `MonsterModel` + `EncounterModel` and get it drawn into an act's pool? | **YES, mechanism proven.** `S13-a1` OPEN — BaseLib's `CustomMonsterModel` self-registers via `ModelDb::Inject`. `S13-b1` OPEN — `CustomEncounterModel`. `S13-b2` OPEN — BaseLib **enumerates every `ActModel` subtype, base and modded, and postfixes `GenerateAllEncounters`**, which is exactly the "fixed array" problem all three act files raised. S13 also settles the *hostile-vs-summon* distinction explicitly: side, not type (`CombatState::CreateCreature` vs `PlayerCmd::SpawnPet`). | **FINAL — OPEN** |
| **S1b** | …and a **boss** specifically? | **NARROW.** `S13-b3`: a boss is `EncounterModel` + `RoomType.Boss` + the act's `BossDiscoveryOrder`, which is a plain virtual getter on the *act*. Adding to a **base** act's boss order needs a patch on that act type, not the pool postfix, and **BaseLib does not exercise it**. | **FINAL — NARROW.** Applies to all 12 boss rows. |
| **S2** | Can a mod ship its own `creature_visuals` scene + Spine rig and have the engine resolve it? | **SPLIT.** *Scene half:* **OPEN**. `S13-a4` (`VisualsPath`, `protected virtual`, Harmony-patched by BaseLib already) is the recommended seam; `S13-a5` (`CreateVisuals`) is coarser and bypasses preload; `S13-g6` shows BaseLib's `NodeFactory` will bind a mod-authored `.tscn` to the game's C# node type, and `NCreatureVisualsFactory` will **generate** the missing contract nodes and build a complete `NCreatureVisuals` **from a single `Texture2D`**. *Spine half:* **still UNKNOWN** — S13 read no Spine import path and states plainly that "the practical minimum presentation for a monster under BaseLib is one image, not a rig." | **FINAL for the scene half; the Spine half remains UNKNOWN.** |
| **S2-trap** | — | `S13-g4` **TRAP**: Godot's pack loader replaces colliding `res://` paths, so a mod pck containing `scenes/creature_visuals/<base-id>.tscn` would **globally** overwrite the base scene. Namespacing is the whole of the no-global-overwrite requirement. | **FINAL — hazard.** |
| **S3** | Can a mod supply the **FMOD** events the id-derived SFX paths demand? | **HALF.** `S13-a7` OPEN (base): `AttackSfx`/`CastSfx`/`DeathSfx` are getters BaseLib already patches, so **overriding the string** is proven. **Supplying an actual bank is not** — S13's own note is "replacing one needs an FMOD bank, not a file", and it found no bank-adding mechanism. S13 §3 could not even enumerate the base game's event inventory (`Master.strings.bank` yields no plaintext). | **PARTIAL.** String override FINAL-OPEN; bank content **NON-FINDING**. |
| **S4** | Can a mod ship an **encounter** scene with named body slots (`HasScene = true`)? | **YES.** `S13-b4` OPEN — BaseLib's `CustomEncounterModel` carries three nested Harmony patch classes over `ScenePath`, `HasScene`, `Slots`, `ExtraAssetPaths` and `CreateBackgroundAssetsForCustom`, and slots are read off `Marker2D` children. Corroborated by the shipped scenes: `knights_elite.tscn` is **three `Marker2D`s and nothing else**. | **FINAL — OPEN** |
| **S5** | Skins — the `normal`/`phobia` contract and runtime composed skins | **NOT ANSWERED.** S13 has **no skin key**. Its only touch is §5.4 Q4, which frames a missing `%PhobiaModeVisuals` as a *scope* question ("a replacement body with no `%PhobiaModeVisuals` silently ignores the accessibility toggle"), not a capability answer. | **PROVISIONAL** — cite S13 §5.4 Q4 and the absence of a key. |
| **S6** | Can a mod attach a **custom script node** inside a creature-visuals scene and receive Spine animation events? | **PARTIAL.** `S13-g6` proves the *binding* half: `SceneConversionPatch` postfixes `PackedScene.Instantiate` and `NodeFactory` converts registered scene paths into game C# types. It does **not** cover Spine animation events, and S13 flags its own limit: it read `NCreatureVisualsFactory`'s declaration logic but **not** the `NodeFactory::ConvertScene` body (§4.5 caveat), so "whether conversion reparents/retypes arbitrary children correctly for a hand-built scene is untested here." | **PARTIAL** |
| **S7** | Nested child `SpineSprite` inside a `SpineSlotNode` (Act 2's bowlbug egg) | **NOT ANSWERED.** No S13 key. | **PROVISIONAL** |
| **S8** | Multiple named `BoundsContainer`s swapped by `AnimState` | **NOT ANSWERED.** No S13 key. S13 §4.3 lists `%Bounds` as a **hard-fail** required node but says nothing about alternates. Relevant here to Test Subject (`RespawnBounds1/2`). | **PROVISIONAL** |

### 6b. Six new keys, `B1`–`B6` — boss/elite-specific

A separate `B` namespace so nothing collides with S18's `S1`–`S8` or with the
dispatch's own `S12a`–`g` stream ids. **None of these is answered.** Each is
recorded with the engine evidence and the nearest S13 finding.

| Key | Question | Evidence in the shipped game | Nearest S13 finding | Status |
|---|---|---|---|---|
| **B1** | Can a mod supply a **boss map-node** art surface — and can it replace a base boss's? | `EncounterModel::BossNodePath` (`:198`) and `BossNodeSpineResource` (`:200-210`) are both `virtual`; `BossNodeAssetPaths` (`:218-231`) probes with `ResourceLoader.Exists` and degrades from a Spine rig to a `.png` + `_outline.png` pair. Three bosses ship the rig; nine ship the pair. | None specific. Shape-identical to `S13-a4` (a `virtual` getter Harmony-patched per instance), and `S13-b4` already proves BaseLib patches *other* `EncounterModel` members. | **PROVISIONAL — strong analogy, untested** |
| **B2** | Can a mod supply a **custom combat background** for its encounter? | `HasCustomBackground` → `CreateBackgroundAssetsForCustom` → `new BackgroundAssets(Id.Entry.ToLowerInvariant(), rng)`, which **opens and enumerates a directory** `res://scenes/backgrounds/<id>/layers` with `DirAccess.Open` and **throws** if absent (`Rooms/BackgroundAssets.cs:49-53`), then groups the files it finds by `_bg_##` / `_fg_` prefix. Its doc comment states `{title}` must equal the class name (`:43`). | `S13-b4` names `CreateBackgroundAssetsForCustom` among BaseLib's patched members — so the *hook* is OPEN. **The directory-enumeration behaviour over a mounted mod PCK is not covered anywhere in S13.** | **PROVISIONAL — hook OPEN, `DirAccess`-over-PCK UNKNOWN. Hard-fail if wrong.** |
| **B3** | Can a mod supply **boss music** — a `CustomBgm` FMOD event and a runtime music **parameter**? | `CustomBgm` / `AmbientSfx` are `virtual` strings on `EncounterModel` (`:190`, `:194`); the monster then drives `NRunMusicController.Instance?.UpdateMusicParameter("<name>_progress", v)` (11 bosses) and, uniquely, `SfxCmd.SetParam` on its own ambient event (`WaterfallGiant.cs:311`, `:322`). | **None.** S13 has no audio key beyond `S13-a7` (enemy SFX strings) and records the FMOD bank problem as unsolved. B3 inherits S3's bank NON-FINDING and adds a parameter-graph requirement on top. | **PROVISIONAL — joins S3's NON-FINDING** |
| **B4** | Can a mod body satisfy the **exact-node-path** contracts the model and the driver impose? | Model side: `NCreature::GetSpecialNode<T>(name)` = `Visuals.GetNodeOrNull<T>(name)` (`Nodes/Combat/NCreature.cs:441-444`) — **soft**, returns null, effect silently absent. Driver side: every `N…Vfx` uses **`GetNode<T>` — hard, throws**; 12 lookups in `NWaterfallGiantVfx`, 12 in `NAmalgamVfx`, 11 in `NTestSubjectVfx`, 9 in `NKaiserCrabBossVfx`, 8 in `NKnowledgeDemonVfx`. Paths run up to four levels deep and escape the subtree with `../..`. | Adjacent to `S13-g6` (scene→type binding) but **not the same question**: this is about node **names, paths and types inside** the scene, after binding. S13 §4.3/§4.4 tabulates the four required contract nodes only. | **PROVISIONAL** |
| **B5** | Can a mod body drive a **layered Spine animation track** (`SetAnimation("[_]tracks/<name>", loop, 1)`), including a runtime-computed index? | Five bodies do it — Vantom, Lagavulin Matriarch, Waterfall Giant (dynamic `buildup{1..3}`), Soul Nexus, Queen. Four install it from inside `SetupSkins`, which is `public virtual` on `MonsterModel` (`:598`) and called from `NCreatureVisuals`. | **None.** S13 §4.2 lists "Skins" as resolved immediately after the animator, via `SetupSkins`, but does not distinguish skins from track-1 animation. | **PROVISIONAL** |
| **B6** | Can a mod driver hook **animation *start* by clip name** (`ConnectAnimationStarted`), not only authored events? | Six drivers do — Queen, Knowledge Demon, Kaiser Crab, Spectral Knight, The Insatiable, Test Subject — each switching on exact clip names (`"attack"`, `"idle_loop"`, `"attack_thrash"`, `"salivate"`, `"burn"`, `"die3"`, `"idle_loop3"`, `"empty"`). | **None.** Same family as S6; S13's `S13-g6` caveat applies here too. | **PROVISIONAL** |

### 6c. Socket load, by row

- **Every row** needs S1, S2 (scene half) and S3.
- **Every boss row** additionally needs **S1b** (NARROW) and **B1** — 12 rows.
- **B2** (custom background) binds **11** boss rows: all but E21 (Aeonglass),
  which is the only boss with `HasCustomBackground => false`.
- **B3** (BGM + music parameter) binds **11** boss rows: all but E5 (Lagavulin
  Matriarch), which ships neither. E6 (Ceremonial Beast) has a `CustomBgm` but
  no parameter, so it binds B3 only in part.
- **S4** (encounter scene + slots) binds **6**: E3, E7, E11, E15, E17, E22.
- **S5** (skins) binds **6**: E3 (`tall`/`short`), E7 (random hair), E10
  (phobia **skin**), E11 (six phobia **textures**), E12 and E16 (phobia
  textures).
- **S6** (custom node + Spine events) binds **17 of 22** — everything except
  E1, E2, E5, E13 and E21. It is the most load-bearing partially-answered key
  at this tier.
- **B4** (exact node paths) binds **8**: E2, E4, E5, E7, E11, E17, E20, E22.
- **B5** (layered track) binds **5**: E4, E5, E8, E19, E22.
- **B6** (clip-name hook) binds **6**: E14, E15, E16, E17, E20, E22.
- **E22 (Queen + Amalgam) touches every key in both namespaces except S5, S7 and
  S8** — the single most socket-dependent encounter in the game.

---

## 7. UNKNOWN and NON-FINDING

- **NON-FINDING — no local enemy-modding precedent, unchanged by S13.**
  `klee-mod` references no `MonsterModel` and no `EncounterModel`, ships no
  Spine rig, and S13 §5.1 #4 confirms there is **no public API to replace a base
  monster's art** in either assembly: the seam it found is a Harmony patch on an
  engine member, not a supported extension point.
- **NON-FINDING — nothing here was executed.** S13's standing caveat applies
  verbatim: no game was launched, no pck was built, no DLL was compiled. Every
  "FINAL" in §6a means *S13 settled the source reading*, never *this was run*.
- **Aeonglass is the base game's own instance of S13's non-Spine finding — and
  that cuts both ways.** S13 §4.4 establishes that a non-Spine body is a fully
  supported state end to end (no animator, hitbox-based death fade, everything
  else intact) and calls the trade "a static prop that vanishes… a taste call,
  and it is [USER]'s." Aeonglass proves MegaCrit ships that state in a released
  build **for a boss**. What it does **not** prove is that the state is
  acceptable: this is a placeholder in an early-access game, evidenced by the
  borrowed music, the borrowed music parameter, the `hourglass_placeholder.png`
  texture, the root node still named `Doormaker`, and the absent background.
  Reading it as an endorsement would be exactly the inference the charter
  forbids.
- **UNKNOWN — Byrdonis's extra pack assets.** `pck` carries
  `byrdonis_nest.png` (**5 559 092 B**, the largest single texture I saw),
  `byrdonis_egg.png` (293 132 B), `byrdonis_feathers.png` and
  `byrdonis_nest_shine.png`. **None is referenced by `Byrdonis.cs` or
  `ByrdonisElite.cs`.** The repo separately records that `Byrdpip` is a *player
  pet* spawned by a relic (`s18-act1.md:145`), so a nest/egg event is the
  obvious guess — but I did not chase it, and **these are not attributed to the
  elite's art bill.**
- **UNKNOWN — rig internals.** Bone counts, attachment counts, clip durations,
  mesh-vs-bone deformation ratio, transition mixes and draw-call cost were
  **not** measured. Skeleton byte size and atlas region count are coarse proxies
  only. **S16 owns the animation corpus and is authoritative over this file on
  rig internals.**
- **UNKNOWN — audio content.** FMOD bank contents were not opened. Only the
  event **paths** and **parameter names** the code computes are reported;
  whether an event or a parameter exists behind any given name was verified for
  no body. This is the same boundary all three act files record.
- **UNKNOWN — undriven rig content at this tier.** I read clip lists from the
  **C# `new AnimState("…")` declarations only**, not from a Spine parser or a
  string scan. That makes every clip named above **doubly safe** (the code
  drives it) but means this file **cannot** report clips that exist in a rig and
  are named by nothing — the category Act 3 found for Globe Head, the
  Fabricator, Frog Knight and Living Shield. Two act-file pointer rows list one
  clip more than the code drives (flail knight's `attack_breaker`,
  `s18-act3.md:179`; torch head amalgam's `buff`, `:184`); both are recorded in
  the rows above as reconciliations, **not** as contradictions — the act agent
  read the rig, I read the code, and undriven rig content is exactly the gap
  between the two.
- **UNKNOWN — whether phobia coverage is an obligation.** Measured, not judged:
  1 phobia **skin** (Skulking Colony) and 3 phobia **texture** sets
  (Decimillipede ×6, Entomancer, The Insatiable) among elites and bosses, plus 2
  more skins among the uncosted Underdocks leftovers. Two incompatible filename
  conventions coexist (`<id>_phobia` vs `phobia_<id>`). **Whether a reskin must
  reproduce any of it is a scope call and is [USER]'s.**
- **UNVERIFIED — scene node graphs for 14 of 22 rows.** I extracted and read the
  node graphs for `aeonglass`, `flail_knight`, `magi_knight`, `spectral_knight`,
  `mecha_knight`, `queen`, `soul_nexus`, `test_subject`, `torch_head_amalgam`,
  `knights_elite` and `queen_boss`. For the rest, node contracts above are
  derived from **the driver's own `GetNode` calls**, which are authoritative
  about what the scene must contain but not about what else it contains. Scene
  **byte sizes** are from the pack index and are exact.
- **NOT ATTEMPTED — `SKIP-10.9`.** The dormant unimplemented-mechanic rows are
  cited only where the gallery or a pool file already cites them (Vantom's
  Slippery, Lagavulin's Plating cap and Soul Siphon, Mecha Knight's Artifact 3,
  Knight Gang's auras). No prototype, no promotion (charter §3.2 / R183).

---

## 8. What this does **not** establish

It does not choose or rank a Genshin body for any elite or boss, does not grade
RESKIN vs REDESIGN (it repeats what `reskin-gallery.md` and
`dossiers/bosses/candidates.md` already recorded, including their own confidence
codes and flags), does not resolve the atlas-vs-weekly-boss fork, does not
change any existing ordering, does not prove any enemy can be added or reskinned
in a mod, does not answer a single one of the six new `B` keys, does not measure
runtime performance, does not touch the shipped sim or any governing doc, and
does not open a balance window, stamp, or experiment. The complexity letters are
an engineering count of asset contracts, **not a schedule and not a cost in
hours** — and for Aeonglass the letter is explicitly meaningless. Whether any of
these encounters should be reskinned at all, and from which gallery, is
[USER]'s call.

---

## 9. Questions this file raises for [USER]

Numbered for citation, not ranked. These are **additions** to the deduped list
in `s18-joined-matrix.md` §5, which carries the questions the three act files
raised; they are repeated there so [USER] reads one list.

1. **The atlas-vs-weekly-boss fork.** `candidates.md:27-32` and `:777-794` put
   it plainly: for **Kaiser Crab, Test Subject and Aeonglass** the reskin
   gallery's normal-enemy candidates beat every weekly-boss draft on the merits,
   while **Knowledge Demon** is the one slot where the weekly layer is stronger
   because atlas cover is explicitly soft. Which gallery owns the act-boss slots
   is a structural call. *(pick-one, per slot or once globally)*
2. **Two bosses currently have no candidate from either gallery: Soul Fysh and
   Queen + Torch Head Amalgam.** Both are on the gallery's redesign-pressure
   list with zero claims across all 16 families, and neither has a weekly-boss
   row. *(open)*
3. **Boss art surface scope.** A reskinned boss can inherit its base map node,
   background and music untouched, or replace some or all of them. Eleven of
   twelve bosses carry all three; `vantom_boss` (3 layers) and
   `waterfall_giant_boss` (2 layers) are thin enough to be cheap to replace,
   while `lagavulin_matriarch_boss` and `soul_fysh_boss` (14 each) are not.
   *(pick-one: creature only / creature + map node / everything)*
4. **Act 1's boss art bill is four bosses larger than the sim shows.**
   Ceremonial Beast, The Kin, Waterfall Giant and Soul Fysh are live base
   encounters with full art surfaces and gallery rows, but are not in
   `act1_pool.yaml` at all. Are they in scope for mapping? *(yes-no)*
5. **Phobia-mode coverage.** Reproduce it, drop it, or decide per body? It binds
   1 skin + 3 texture sets among elites/bosses and 2 more skins among the
   uncosted Underdocks leftovers. It is an accessibility surface, so it also
   belongs to S20's census. *(pick-one: reproduce / drop / per-body)*
6. **Kaiser Crab is two bodies on one skeleton.** A reskin that splits them into
   two Genshin bodies from different families pays for two rigs where the base
   pays for one. *(open — costing consequence only)*
7. **Aeonglass has no base animation to reskin against**, and it is
   simultaneously the row the gallery calls its "strongest single boss
   argument". Treat it as (a) a static-body reskin matching the shipped state,
   (b) the row that gets an original rig, or (c) out of scope until MegaCrit
   finishes it? *(pick-one)*
8. **The construct-gang precedent, at boss tier.** No elite or boss body is
   shared across acts, so unlike the Act-3 construct gang no reskin here
   repaints another act. Recorded as a *reassurance*, not a question — but it
   means elite/boss picks can be made act-by-act without cross-act coupling.
   *(no action)*
9. **Does the gallery's five-body Underdocks leftovers row get split?**
   `reskin-gallery.md:84` files Terror Eel, Haunted Ship, Fossil Stalker and the
   two Cultists under one uncosted row with no candidates; at least three of the
   five carry a phobia obligation. Splitting it is a change to an existing
   ordering and is not a drafter's call. *(yes-no)*
