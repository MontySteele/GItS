# S18 — Implementation-aware enemy feasibility, **Act 2**

> **This decides nothing.** It is an engineering read of what each Act 2
> encounter is *made of* in the shipped game — rig, animation clips, scene
> nodes, particle contract, sound events — so that the enemy mapping [USER]
> has not yet made can be costed. It does **not** rank Genshin candidates, does
> not repeat Genshin canon, and does not pick a reskin. The candidate ordering
> already exists in `docs/current/dossiers/remap/reskin-gallery.md` and is not
> touched here.

- **Date:** 2026-08-26. **Primary checkout:** `223a4ff` (per `PREFLIGHT.md`),
  read-only throughout.
- **Game read:** Slay the Spire 2 **v0.107.1** (`docs/current/STATE.md:158-163`),
  read-only. No game was launched, nothing was deployed, no game file was
  written. [USER] was playtesting on mod `0.2-1155` the whole time.
- **Act 2 in the base game is `Models/Acts/Hive.cs`** (`Index => 1`,
  `IsDefault => true`, 14 base rooms, 2 weak encounters,
  `Core/Models/Acts/Hive.cs:45-49`). Our shipped model of it is
  `tier05/content/act2_pool.yaml`.
- **Owner split:** this file owns **Act 2 normal encounters only**. Act 2
  elites and bosses are the boss/elite integrator's, and appear here as
  one-line pointers (§4), not rows.
- **Socket columns are `PROVISIONAL — S13 pending`** throughout. §6 states the
  exact questions their answers must fill. A draft
  `review/dispatch3/s13-engine-sockets.md` exists on this branch; **joining it
  is the integrator's job, not this file's**, and nothing here was changed to
  match it.
- **Sibling file:** `s18-act1.md` (same schema, same method, same socket keys
  S1–S6). Two keys are new in Act 2 (S7, S8) and are flagged as such.

---

## 0. How the evidence was obtained

Three sources, all read-only, all local:

| Source | What it gives | Cite form used below |
|---|---|---|
| `sts2.dll` decompiled with ilspycmd 8.2 into the scratchpad | monster/encounter/act classes, animation-state declarations, VFX/SFX call sites | `<Namespace.Type>::<member>` in prose + `Core/…/File.cs:line` |
| `SlayTheSpire2.pck` directory index, parsed read-only (Godot pack **format 3**, engine **4.5.1**, **15 658** entries) | exact resource paths and byte sizes; scene node graphs; Spine atlas region lists; Spine skeleton string tables | `pck:<path>` (+ byte size) |
| The repo | the shipped sim model of each encounter, and the existing candidate gallery | repo `file:line` |

Decompile root in the scratchpad:
`…/scratchpad/s18/tree/MegaCrit/sts2/…` (shared with the Act 1 agent; line
numbers below were re-checked against that tree). Nothing decompiled or
extracted was copied into any repo. Clip and Spine-event names come from an
**ASCII string scan of the imported `.spskel` binaries** cross-checked against
the C# `new AnimState("…")` declarations — see §7 for what that means for
confidence. Atlas region counts come from the imported `.spatlas` JSON, which
is plain text.

**Four engine facts that set the whole cost model.** All four also hold in
Act 1; they are restated here so this file reads cold.

1. **Every base creature is a Spine skeleton.** Each monster owns a folder
   `res://animations/monsters/<id>/` holding `<id>.atlas`, `<id>.png`,
   `<id>.skel` and `<id>_skel_data.tres`, plus a Godot scene
   `res://scenes/creature_visuals/<id>.tscn`. The game ships
   `libspine_godot.windows.template_release.x86_64.dll` next to the executable.
   `MonsterModel::VisualsPath` is `protected virtual` and defaults to
   `creature_visuals/<Id.Entry>` (`Core/Models/MonsterModel.cs:216`).
2. **The default animator is five clips.** `MonsterModel::GenerateAnimator`
   (`Core/Models/MonsterModel.cs:602-619`) builds `idle_loop` (looping),
   `cast`, `attack`, `hurt`, `die`, reachable through triggers `Idle`, `Cast`,
   `Attack`, `Hit`, `Dead`. The clip vocabulary constants live on `AnimState`
   (`Core/Animation/AnimState.cs:15-27`) and the trigger constants on
   `CreatureAnimator` (`Core/Animation/CreatureAnimator.cs:11-23`).
   **A missing clip does not crash:** `CreatureAnimator::SetNextState` logs
   `could not find '<id>' animation on '<node>'` and returns
   (`Core/Animation/CreatureAnimator.cs:88-93`), which also drops the queued
   return-to-idle (`:114-121`). A missing visuals scene falls back to
   `pck:scenes/creature_visuals/fallback.tscn` (1 064 B)
   (`Core/Models/MonsterModel.cs:171`).
3. **The creature-visuals scene contract is four nodes.** Root `Node2D`
   scripted with `res://src/Core/Nodes/Combat/NCreatureVisuals.cs`; child
   `%Visuals` (`SpineSprite`, carrying `skeleton_data_res` and a per-body
   `scale`); `%Bounds` (`Control`); `%CenterPos` and `%IntentPos`
   (`Marker2D`). Everything past those four nodes is per-body extra, and that
   extra is what separates an **S** row from an **L** row below.
4. **Audio is path-derived FMOD, not authored per move.** `MonsterModel`
   computes `AttackSfx` / `CastSfx` / `DeathSfx` as
   `event:/sfx/enemy/enemy_attacks/<id>/<id>_{attack,cast,die}`
   (`Core/Models/MonsterModel.cs:292-298`); `HurtSfx` is `null` unless
   overridden (`:300-302`); hit feedback is a shared class chosen by
   `TakeDamageSfxType` (`:327-329`). These resolve out of
   `pck:banks/desktop/*.bank` — FMOD banks, not Godot resources. Act 2's own
   music banks are `act2_a1.bank` (41 829 984 B) and `act2_a2.bank`
   (41 946 368 B) (`Core/Models/Acts/Hive.cs:53-57`).

**One Act-2-specific fact.** Act 2 is the insect act, and it is the act that
carries the game's **phobia-mode** accessibility variants. Six Hive room
backgrounds ship a `_phobia` twin (`pck:images/rooms/hive/hive_02_{a,b,c}_phobia.png`,
`hive_03_{a,b,c}_phobia.png`), and the toggle machinery is real shipped code
(`pck:src/Core/Nodes/Animation/NPhobiaAnimationToggler.cs`,
`…/Screens/Settings/NPhobiaModeTickbox.cs`). Bodies do it two ways: a
**Spine skin** named `phobia` (`MonsterModel::HasPhobiaSpineSkin`,
`Core/Models/MonsterModel.cs:304`) — used by **The Obscura**, the only Act 2
*normal* that does — or a **separate texture** under
`pck:images/monsters/phobia_mode/`, used by the Decimillipede segments, the
Entomancer and The Insatiable, all of which are §4 integrator rows. Whether a
reskin keeps that obligation is a scope call and is [USER]'s.

---

## 1. Column key

| Column | Means |
|---|---|
| **Asset / rig family** | The base creature's actual rig: Spine skeletons, their imported byte sizes as a coarse rig-weight proxy, atlas region count as a coarse part-count proxy, and the visuals scene size. |
| **Required tells / states** | The animation clips the code actually drives, plus any spawn-time power the player must be able to read. |
| **Variants / reuse** | How many distinct art bodies the encounter needs, what varies in code or in skin rather than in art, and which other encounters share the rig. |
| **VFX / audio surface** | Hit VFX scene(s), bespoke particle nodes, named Spine attach bones/slots, named Spine animation events, and the FMOD event families the body demands. |
| **Complexity** | S / M / L on the scale in §3. |
| **RESKIN vs REDESIGN (as the atlas records it)** | Repeated from `reskin-gallery.md` only — candidate density and any flag that row already carries. No new judgement. |
| **Socket — PROVISIONAL, S13 pending** | Which of the socket questions in §6 this row depends on. |

---

## 2. Act 2 normal encounters — the matrix

Thirteen rows. Every Act 2 encounter the gallery maps is either a row here or
is listed in §4 (elite/boss, integrator-owned). Nothing mapped is silently
dropped; §5 proves the coverage.

| # | Encounter (gallery row) | Asset / rig family | Required tells / states | Variants / reuse | VFX / audio surface | Complexity | RESKIN vs REDESIGN (as the atlas records it) | Socket — **PROVISIONAL, S13 pending** |
|---|---|---|---|---|---|---|---|---|
| 1 | **Bowlbug pod** — gallery "Bowlbug (Rock) + workers" (`BowlbugsNormal`, 3 bodies; `BowlbugsWeak`, 3) | **ONE rig serving four named bodies.** `pck:animations/monsters/bowlbug/*`: skeleton 162 562 B, atlas 3 788 B, texture 196 856 B, **plus** a second texture `bowlbug_cocoon.png` 58 172 B. The atlas holds **79 regions**, of which four skin-scoped sets of 18 (`rock/…`, `web/…`, `goop/…`, `cocoon/…`) and 13 shared. Four thin scenes: `bowlbug_rock.tscn` 1 146 B, `bowlbug_silk.tscn` 1 316 B, `bowlbug_nectar.tscn` 1 317 B, `bowlbug_egg.tscn` **1 961 B**. | **Four animators off one skeleton.** Rock is the big one — `idle_loop`/`buff`/`headbutt`/`hurt`/`hurt_stunned`/`wake_up`/`die`/`stun`/`stunned_loop`, with `Hit` branching on `IsOffBalance` and a `Stun`/`Unstun` pair (`Monsters/BowlbugRock.cs:109-134`). Silk: 5 clips, `spit` on `Cast` (`BowlbugSilk.cs:88-103`). Nectar: 6, adding a `Buff` trigger (`BowlbugNectar.cs:72-90`). Egg: default-shaped 5 (`BowlbugEgg.cs:74-90`) and its bite also grants itself Block (`:66-72`). | **The pod is randomised.** `BowlbugsNormal` fields one `BowlbugRock` at slot `first`, then **two distinct workers** drawn from `{BowlbugEgg, BowlbugSilk, BowlbugNectar}`, max one each, into `middle`/`last` (`Encounters/BowlbugsNormal.cs:13-27`, `:29`, `:54-71`). `BowlbugsWeak` fields Rock at slot `odd` plus egg/nectar (`BowlbugsWeak.cs:17-31`). Room scenes `pck:scenes/encounters/bowlbugs_normal.tscn` 450 B and `bowlbugs_weak.tscn` 369 B are marker-only slot layouts. `EncounterTag.Workers`, **shared with `SlumberingBeetleNormal`** (row 11). | Shared hit VFX `vfx/vfx_attack_blunt`. **Named Spine bone `spit_target`** exposed as a `SpineBoneNode` on the silk, nectar and egg scenes. **`bowlbug_egg` nests a SECOND skeleton:** a `SpineSlotNode` bound to rig slot `items` carrying a child `SpineSprite` on the **tough_egg** rig, skin `egg1`, clip `egg_idle_loop` (`pck:scenes/creature_visuals/bowlbug_egg.tscn`; `BowlbugEgg.cs:33-49`). **Four separate FMOD families** — `workbug_rock`, `workbug_silk`, `workbug_goop`, `workbug_egg` — plus an explicit rock stun event (`BowlbugRock.cs:28`, `:51-53`); `TakeDamageSfxType.Insect` on rock/nectar/egg. The four families are **not applied uniformly across properties** — see §6 **S3**. | **L** — one rig, but four skins, a nested child rig, a named attach bone and an encounter scene. More than one extra, so it cannot be M. | SHIPPED. Gallery: top candidate rated **S** (anchor + escorts), a second **S** (Fatui squad), then plausibles. Row's own trade-off: "whole-encounter swaps beat body swaps here". **Gallery §5 names `bowlbug_pod` as one of three shipped encounters needing a family-coherent multi-body pick** — per-body best fits would produce a mixed-faction fight. | S1, S2, S3, S4, **S7** |
| 2 | **Bowlbug (Nectar)** — gallery's "kill first" buffer row | **Not a rig — a skin.** The `goop/…` 18-region set on row 1's skeleton, chosen at spawn by `BowlbugNectar::SetupSkins` → `FindSkin("goop")` (`Monsters/BowlbugNectar.cs:37-40`). Scene 1 317 B. | 6 clips: `idle_loop`, `spit`, `buff`, `attack`, `hurt`, `die`; triggers `Cast`→`spit`, `Buff`→`buff`, `Attack`, `Hit`, `Dead` (`BowlbugNectar.cs:72-90`). The buffer beat is the `Buff` trigger (`:68`). | **Corrects a status drift, does not change it.** The gallery marks this row `RESEARCH (not in shipped pod)` — that is a **sim-side** fact: our pod is fixed to Rock+Silk (`tier05/content/act2_pool.yaml:23-38`). In the **base game** the Nectar bowlbug is a live Act 2 worker, drawn by both `BowlbugsNormal` and `BowlbugsWeak` (`Encounters/BowlbugsNormal.cs:22-26`, `BowlbugsWeak.cs:17-21`). No extra rig is needed for it either way. | `vfx/vfx_attack_blunt`; the `spit_target` bone; its own FMOD family `workbug_goop` (`:21`, `:33`, `:61`); `TakeDamageSfxType.Insect`. | **S** — incremental. It is one more 18-region skin set on a rig row 1 already pays for. | RESEARCH (sim), live (base). Gallery: 2 candidates rated **S**, 2 plausible; the row's binding note is that the candidate **must come from whatever family takes the Rock anchor**. | S1, S2, S3 (nothing new over row 1) |
| 3 | **Exoskeletons ×3 / ×4** (`ExoskeletonsNormal` 4 bodies; `ExoskeletonsWeak` 3) | **1 rig**, `pck:animations/monsters/exoskeleton/*`: skeleton 100 868 B, atlas 1 972 B / **45 regions**, texture 84 728 B. Scene `pck:scenes/creature_visuals/exoskeleton.tscn` 1 148 B — the bare 4-node contract, `%Visuals` scale 0.12. | **7 declared states**: `idle_loop`, `die`, `hurt`, `cast`, `buff`, `attack`, `attack_heavy`, with an extra trigger `HeavyAttack` (`Monsters/Exoskeleton.cs:102-123`). Tells needed: a light 3-hit skitter played as one animation (`.OnlyPlayAnimOnce()`, `:78-83`), a heavy mandible bite (`:89-91`), a self-buff (`:97-98`). | **One art body ×4 or ×3.** Named slots `first`…`fourth` / `first`…`third` (`Encounters/ExoskeletonsNormal.cs:20`, `ExoskeletonsWeak.cs:14`), room scenes 530 B / 451 B. `EncounterTag.Exoskeletons`. Body count costs nothing in art. | Shared VFX only: `vfx/vfx_attack_slash` on the skitter, `vfx/vfx_bite` on the mandibles. **No bespoke VFX node, no attach nodes.** FMOD family is **`roaches`**, not `exoskeleton` — the id-derived default is overridden (`:26-28`, `:40-42`); `TakeDamageSfxType.Insect`. The rig additionally carries the strings `spray_start` / `spray_end` and a `clip_target_slot` with **no consumer anywhere in the scene** — recorded as UNKNOWN in §7. Its atlas also holds `millipedestone1/2/3` regions, the same prop family as the Decimillipede's `rockstone` rig — cross-reference for the §4 integrator. | **M** — an S body plus exactly one extra: an encounter scene with named body slots. | SHIPPED. Gallery: **6 candidates, 5 rated S** — the best-supplied row in Act 2. Not on the §1 redesign-pressure list. **Carries the §4 art-unsafe warning:** Hard to Kill 9 is UNIMPLEMENTED in the shipped file (`tier05/content/act2_pool.yaml:40-53`), so armour-flavoured art would promise a damage cap that is not there. | S1, S2, S3, S4 |
| 4 | **Chompers ×2** (`ChompersNormal`) | **1 rig**, `pck:animations/monsters/chomper/*`: skeleton **71 323 B — the lightest Act 2 normal**, atlas 1 700 B / **38 regions**, texture 81 924 B. Scene 1 259 B, bare contract, scale 0.256. | **Exactly the default five.** `Chomper` does **not** override `GenerateAnimator`, so it inherits `idle_loop`/`cast`/`attack`/`hurt`/`die` (`Core/Models/MonsterModel.cs:602-619`), and the rig's string scan holds exactly those five and no more. Tells: a 2-hit clamp under one animation (`Monsters/Chomper.cs:67-74`), and a `Cast` screech that dumps 3 `Dazed` into **every** player's discard (`:76-83`). Spawn-time **`ArtifactPower` 2** applied in `AfterAddedToRoom` (`:49-53`) — a status the player must be able to read. | **One rig ×2, phase-offset in code**: the encounter flips one body's `ScreamFirst` (`:34-45`; `Encounters/ChompersNormal.cs:16-25`) so the pair is permanently out of phase (`docs/current/dossiers/enemies/chomper.md:39-45`). `EncounterTag.Chomper`. No encounter scene. | Shared `vfx/vfx_attack_slash`. **No particles, no attach nodes, no Spine events, no encounter scene.** Explicit `TakeDamageSfx` `chomper_hurt` (`:47`); attack/cast/die id-derived. The screech also plays a **localized bark** through `TalkCmd` keyed `CHOMPER.moves.SCREECH.title` (`:78-79`) — a loc row, not an asset. | **S** — the cheapest row in Act 2: one rig, the stock five clips, one shared hit VFX, zero bespoke scene work. | SHIPPED. Gallery: **one candidate, rated S, uncontested** ("sole claimant and clean"). Not on the redesign-pressure list. | S1, S2, S3 |
| 5 | **Thieving Hopper** (`ThievingHopperWeak`) | **1 rig**, `pck:animations/monsters/thieving_hopper/*`: skeleton 152 578 B, atlas 1 494 B / 31 regions, texture 193 442 B. Scene **2 701 B**, carrying **three** bounds containers. | **11 states** — `idle_loop` (with `BoundsContainer = "GroundedBounds"`), `flee`, `flee_hover`, `hurt`, `hurt_hover`, `attack`, `attack_hover`, `die`, `take_off`, `hover_loop` (`BoundsContainer = "FlyingBounds"`), `steal` (`Monsters/ThievingHopper.cs:290-320`). **Every combat tell exists twice**, grounded and airborne. Powers to read: `EscapeArtistPower` 5 at spawn (`:155`), `FlutterPower` 5 on take-off (`:273`), `SwipePower` on a successful steal (`:241-243`). | Solo (`Encounters/ThievingHopperWeak.cs:16-21`), `EncounterTag.Thieves`, no encounter scene, no rig reuse anywhere. | Shared `vfx_attack_blunt` / `vfx_attack_slash`. **Two named Spine bones**: `card_target_bone`, carrying a `%StolenCardPos` `Marker2D` the code reads when it parks the stolen card (`:232`), and `attack_target_bone` (`:191`). A **looping** hover FMOD event started and stopped by code (`:270`, `:283`); attack, hurt and flee SFX are **mode-dependent properties** that switch on airborne state (`:106`, `:118`, `:134`). | **L** — three bounds containers, two named bones, a marker the code positions, and a dual grounded/airborne clip set. | DROPPED (sim re-add list — theft + flee ops backlogged, `tier05/content/act2_pool.yaml:14-16`); **live in the base game's Act 2** (`Core/Models/Acts/Hive.cs:93`). Gallery: 5 candidates, 3 rated **S**. Row is explicitly "pre-positioning until the card-theft/flee ops land". | S1, S2, S3, **S8** |
| 6 | **Tunneler** (`TunnelerWeak`) | **1 rig**, `pck:animations/monsters/tunneler/*`: skeleton 202 276 B, atlas 1 351 B / 28 regions, texture 97 968 B. Scene 1 330 B + one `SpineBoneNode`. | **12 states** — `idle_loop`, `die`, `hurt`, `attack`, `stun`, `stunned_loop`, `stunned_hurt`, `wake_up`, `burrow`, `hidden_loop`, `hidden_attack`, `hidden_die` (`Monsters/Tunneler.cs:140-171`). `Hit`, `Dead` and `Attack` **all branch on `BurrowedPower`**, so the burrowed body needs its own attack and its own death and has no hurt at all. Tells: bite, burrow, emerge-and-strike, stun, wake. | Solo, `EncounterTag.Burrower`. **`TunnelerNormal` (Tunneler + one Chomper, `Encounters/TunnelerNormal.cs:18-31`) exists as a class but appears in no `ActModel` encounter list in this build** — checked `Overgrowth`, `Underdocks`, `Hive`, `Glory`, `DeprecatedAct`. Recorded as a fact, not interpreted; the Chomper dossier still lists it as one of Chomper's encounters (`docs/current/dossiers/enemies/chomper.md:9`). | Shared `vfx/vfx_attack_slash`. Named Spine bone `attack_target_bone` (`pck:scenes/creature_visuals/tunneler.tscn`). **No bespoke VFX node, no particles.** FMOD family **`burrowing_bug`**, not `tunneler`, with an explicit `HurtSfx` — rare, most bodies have none — and an explicit hidden-attack event (`:34-48`). | **M** — an S body plus exactly one extra (the named attach bone). **The letter understates it:** the real cost is 12 clips including a complete burrowed sub-set, and the scale does not price clip count. | SHIPPED. Gallery calls this **"the most-contested body in the atlas" — every family fields a burrower**, 9 candidates all rated **S**, "effectively a free choice by act theme". Row warns the teleport re-reads cost a VFX rewrite. Not on the redesign-pressure list. **§4 art-unsafe:** untargetable-while-burrowed and the emerging-strike stun are both UNIMPLEMENTED in the sim (`tier05/content/act2_pool.yaml:54-66`). | S1, S2, S3 |
| 7 | **Hunter Killer** (`HunterKillerNormal`) | **1 rig**, `pck:animations/monsters/hunter_killer/*`: skeleton 137 172 B, atlas 2 450 B / 49 regions, texture 237 980 B. Scene **3 296 B**. | **6 states** — `idle_loop`, `cast`, `attack`, `attack_triple`, `hurt`, `die`, plus a `TripleAttack` trigger (`Monsters/HunterKiller.cs:76-94`). Tells: the goop `Cast` that softens (`:52-54`), a single bite, and a 3-hit puncture played once (`.WithHitCount(3).OnlyPlayAnimOnce()`, `:68-72`). | Solo, no adds, no rig reuse, no encounter scene, fixed HP (`MaxInitialHp => MinInitialHp`, `:25`). | **Bespoke.** The scene embeds `NHunterKillerVfx` plus a `SpineBoneNode` bound to rig bone **`mouth`**, carrying a 40-particle `GPUParticles2D` over the **shared** texture `pck:images/vfx/spit_glob_particles.png`. Emission is gated by named Spine animation events **`spit_start` / `spit_end`** (`Nodes/Vfx/NHunterKillerVfx.cs:68`, `:77-82`); both names are present in the rig string table. Hit VFX `vfx/vfx_bite` and `vfx/vfx_attack_slash`. Explicit `TakeDamageSfx` and `DeathSfx` (`:31-33`); attack/cast id-derived. | **L** — a bespoke `N…Vfx` node whose emitter is driven by named Spine animation events. Re-author the rig without those two event names and the particle layer is silently dead. | SHIPPED. Gallery: 7 candidates, 3 rated **S**; "mark-then-punish is well supplied; pick by act faction". Not on the redesign-pressure list. | S1, S2, S3, S6 |
| 8 | **Louse Progenitor** (`LouseProgenitorNormal`) | **1 rig**, `pck:animations/monsters/louse_progenitor/*`: skeleton **265 261 B — the heaviest Act 2 normal**, atlas 963 B / **18 regions — the fewest**, texture 329 456 B. A big body cut into few large parts. Scene 1 178 B, bare contract. | **9 states** — `idle_loop`, `curl`, `uncurl`, `curled_loop`, `attack`, `attack_web`, `hurt`, `die`, **`die_curled`** — and they are wired as a **branched graph**, `AddBranch` per state rather than the usual any-state table (`Monsters/LouseProgenitor.cs:124-155`). The curled sub-state has its own death and **no hurt at all**: while curled the body cannot show a hit. Both attacks auto-uncurl first (`:91-92`, `:115-116`). | Solo, no adds, no rig reuse, no encounter scene. | No bespoke VFX node, **no attach nodes, no Spine events**. Shared `vfx/vfx_attack_blunt`. FMOD family **`giant_louse`**, not `louse_progenitor`, with explicit curl / uncurl / web events (`:26-30`, `:42-44`); `TakeDamageSfxType.Insect`. | **M** — an S body plus exactly one extra, and the extra is a **state-machine** obligation rather than an asset one: a reskin must re-author a curled sub-graph with its own idle and its own death. | SHIPPED. Gallery: 5 candidates, **3 rated S**, "Mitachurl and Whopperflower are both beat-for-beat". Not on the redesign-pressure list. **§4 art-unsafe:** the sim folds Curl Up into a plain block beat (`tier05/content/act2_pool.yaml:94-107`). | S1, S2, S3 |
| 9 | **Mytes ×2** (`MytesNormal`) | **1 rig ×2**, `pck:animations/monsters/myte/*`: skeleton 201 021 B, atlas 2 476 B / 45 regions, texture 209 516 B. Scene 1 818 B. | **6 states** — `idle_loop`, `cast`, `attack`, `hurt`, `die`, `suck`, plus a `Suck` trigger (`Monsters/Myte.cs:97-115`). Tells: the zero-damage Toxic Cornucopia `Cast` (`:75-76`), a bite, and a drain that also buffs (`:90-92`). | Two bodies of one rig, named slots `first`/`second`; room scene `pck:scenes/encounters/mytes_normal.tscn` 373 B. The encounter also overrides **camera scaling and offset** (`Encounters/MytesNormal.cs:22-31`) — a framing obligation that travels with the room, not the body. | **Bespoke.** The scene embeds `NMyteVfx` and a `SpineBoneNode` bound to rig bone **`projectile_target`**, which the code re-parks 150 px above the chosen target creature on the Spine event **`start_cast`** (`Nodes/Vfx/NMyteVfx.cs:72-104`; the target is handed over by the monster at `Monsters/Myte.cs:72`). The scene also applies the shared HSV material `pck:materials/vfx/hsv.tres`. Hit VFX `vfx/vfx_bite`. FMOD family **`mite`**, not `myte` (`:28-44`). | **L** — bespoke `N…Vfx` node driven by a named Spine event, on a rig whose projectile path is part of the skeleton (`projectile_path`, `projectile_rotator`, `toxic_drop*` all appear in the rig string table). | SHIPPED. Gallery: 4 candidates, **2 rated S**; "Samachurl wins on the zero-damage status beat". Not on the redesign-pressure list. | S1, S2, S3, S4, S6 |
| 10 | **Ovicopter + Tough Eggs** (`OvicopterNormal`) | **2 rigs.** `ovicopter` — skeleton 155 044 B, atlas 1 476 B / 29 regions, texture 258 310 B, scene 1 149 B. `tough_egg` — skeleton **45 935 B, the lightest in Act 2**, atlas 1 151 B / 23 regions, texture 63 134 B, scene 1 141 B. | Ovicopter: **7 states** — `idle_loop`, `cast`, `buff`, `attack`, `hurt`, `die`, `lay` — reached through two **bespoke** triggers `layTrigger` and `buffTrigger` (`Monsters/Ovicopter.cs:120-141`). ToughEgg is a **two-phase body on one rig**: `egg_spawn` → `egg_idle_loop` → `egg_hurt` / `egg_die`, then a `Hatch` trigger swaps it to `idle_loop` / `attack` / `hurt` / `die` (`Monsters/ToughEgg.cs:184-207`), with max HP re-rolled at the moment of hatching (`:170-175`). | **Three scenes on two rigs.** `hatchling.tscn` (1 144 B) is a **third** scene on the tough_egg rig, skin `egg1` — its root node is even named `ToughEgg`. `ToughEgg::SetupSkins` picks **randomly** between skins `egg1` and `egg2` at spawn (`:115-120`). `OvicopterNormal` declares **6 slots** (`egg1`…`egg5`, `ovicopter`) but spawns only the parent (`Encounters/OvicopterNormal.cs:16`, `:36-41`); Lay Eggs adds up to 3 eggs into free slots and only while ≤3 allies live (`Monsters/Ovicopter.cs:46`, `:80-95`). Room scene 695 B. The tough_egg rig is **also** the child skeleton nested inside row 1's `bowlbug_egg`. | No bespoke VFX node. Shared `vfx/vfx_attack_slash` (parent) and `vfx/vfx_bite` (egg). **A looping FMOD idle event** started in `AfterAddedToRoom` and stopped in `BeforeRemovedFromRoom` (`:48-57`). FMOD families `egg_layer` (parent) and `tough_egg` (egg), the latter with a **hatched-state-dependent death event** `tough_egg_die` vs `hatchling_die` (`ToughEgg.cs:62-71`); both `TakeDamageSfxType.Slime`. | **L** — two rigs, a randomised skin pair, a two-phase clip set on one body, a 6-slot encounter scene, and a cross-row rig dependency into row 1. | SHIPPED. Gallery: 6 candidates, **2 rated S**; the row's stated discriminator is the **two-stage minion** (dormant → active), which only two candidates handle natively. Not on the redesign-pressure list. **§4 art-unsafe:** the sim's eggs never hatch (`tier05/content/act2_pool.yaml:123-140`). | S1, S2, S3, S4 |
| 11 | **Slumbering Beetle** (`SlumberingBeetleNormal`) | **1 rig**, `pck:animations/monsters/slumbering_beetle/*`: skeleton 121 478 B, atlas 1 882 B / 34 regions, texture **772 780 B — the heaviest single creature texture in Act 2**. Scene 1 504 B. | **9 states** — `sleep_loop` (initial, looping), `wake_up`, `idle_loop`, `cast`, `attack`, `roll`, `hurt`, `die`, **`sleep_die`** (`Monsters/SlumberingBeetle.cs:149-172`); `Hit` branches on `IsAwake`, so the sleeping body has its own hit and its own death. Spawn-time `PlatingPower` **and** `SlumberPower` 3 (`:76-77`), both of which the player must read. | **The base encounter is a three-body room**: `BowlbugRock` + `BowlbugSilk` + `SlumberingBeetle` at slots `first`/`second`/`third` (`Encounters/SlumberingBeetleNormal.cs:15-31`), tagged `EncounterTag.Workers` — the same tag row 1 carries. **Reskinning this row drags row 1's family in with it**, which is exactly the coherence question the gallery row raises. Room scene 449 B; camera scaling and offset overridden (`:34-42`). | A `%SleepVfxPos` `Marker2D` that the code parents a **shared** `NSleepingVfx` to, with explicit stops on wake and on death (`:79-96`). A **looping** sleep FMOD event started at spawn and stopped on wake (`:78`, `:98`), plus explicit roll and wake events (`:29`, `:101`). Named Spine bone `attack_target_bone`, read before the roll (`:136`). Hit VFX `vfx/vfx_attack_blunt`. | **L** — three separate extras (a named bone, a code-managed VFX lifecycle on a marker, a dual sleep/awake clip set with its own death), so it does not fit M's "exactly one". | DROPPED (sim re-add list, `tier05/content/act2_pool.yaml:14-16`); **live in the base game's Act 2** (`Core/Models/Acts/Hive.cs:89`). Gallery: 9 candidates, **5 rated S**. Row's own note — "shipped encounter would bundle it with Bowlbugs — family coherence question rides along" — is **confirmed by the base encounter composition above**. **§4 art-unsafe:** Plating 15 is UNIMPLEMENTED. | S1, S2, S3, S4 |
| 12 | **Spiny Toad** (`SpinyToadNormal`) | **1 rig**, `pck:animations/monsters/spiny_toad/*`: skeleton 177 283 B, atlas 2 870 B / **52 regions**, texture 446 634 B. Scene **4 989 B — the largest Act 2 normal scene**. | **9 states** — `idle_loop`, `hurt`, `die`, `protrude`, `lick`, `explode`, and a whole second body set **`idle_naked_loop`, `hurt_naked`, `die_naked`** (`Monsters/SpinyToad.cs:104-130`), reached by triggers `Spiked` / `Unspiked`; `Hit` and `Dead` both branch on `IsSpiny`. **The Thorns state is a body change, not a status icon** — three of the nine clips exist only to show the toad with its spikes gone. `ThornsPower` 5 on protrude, −5 on explode (`:82`, `:92`). | Solo, no adds, no rig reuse, no encounter scene. | **Bespoke.** `NSpinyToadVfx` drives **two** `GPUParticles2D` — a 30-particle burst over the bespoke texture `pck:images/vfx/monsters/spiny_toad/spiny_toad_spike_particle.png` and a 200-particle sub-burst over the shared `long_rice_no__glow_particle.png` — gated by the named Spine event **`explode`** (`Nodes/Vfx/NSpinyToadVfx.cs:77-92`). Hit VFX `vfx/vfx_attack_slash`. FMOD family `spiny_toad` with explicit lick / protrude / explode / die events (`:23-52`). | **L** — bespoke `N…Vfx` node driven by a named Spine event, on top of a dual spiked/naked body set. | DROPPED (sim re-add list — Thorns); **live in the base game's Act 2** (`Core/Models/Acts/Hive.cs:90`). **On the gallery's §1 redesign-pressure list**: 6 candidates, **none strong**; "Thorns-as-retaliation has no clean Genshin analogue; every family flagged the same seam". The implementation read **sharpens that**: the tell is a whole second body state, not a buff icon, so a candidate that cannot show "spikes out / spikes gone" loses the read entirely. | S1, S2, S3, S6 |
| 13 | **The Obscura + Parafright** (`TheObscuraNormal`) | **2 rigs.** `the_obscura` — skeleton 173 464 B, atlas 2 247 B / **54 regions (17 eyes + 17 irises)**, texture 209 136 B, scene 3 221 B. `parafright` — skeleton 145 598 B, atlas 816 B / **16 regions**, texture **400 720 B**, scene 3 319 B. | Obscura: **9 states** — `intro_loop` (initial, looping), `idle_loop`, `attack`, `cast`, `cast_intro`, `hurt`, `hurt_intro`, `die`, `die_intro` (`Monsters/TheObscura.cs:113-137`). **Every reactive tell exists twice**, before and after it has summoned, branching on `HasSummoned`. Parafright: **9 states** — `spawn` (initial), `idle_loop`, `attack`, `hurt`, `hurt_stunned`, `stunned_loop`, `stun`, `wake_up`, `die` (`Monsters/Parafright.cs:58-82`), branching on `IllusionPower.IsReviving`, and its `Dead` state only plays when no primary enemy is still alive (`:81`). | `TheObscuraNormal` declares slots `illusion` / `obscura` and spawns only the Obscura (`Encounters/TheObscuraNormal.cs:15-28`); the Parafright arrives on the Summon move (`TheObscura.cs:80-81`). Room scene 377 B. Neither rig is reused anywhere else. | **Both bodies are bespoke and they share their assets.** Each embeds an `N…Vfx` node plus a `SpineSlotNode` — slot `particle_attach` on the Obscura, `particles_attach` on the Parafright — carrying a `GPUParticles2D` gated by the named Spine events **`particles_start` / `particles_end`** (`Nodes/Vfx/NTheObscuraVfx.cs:63-92`; `NParafrightVfx.cs:63-92`). **Both use the same texture** `pck:images/vfx/monsters/the_obscura/obscura_particle.png` and the shared additive material. The Obscura's slash is *also* a **baked atlas region** (`attack_slash`) on top of the shared `vfx/vfx_attack_slash`. FMOD family `obscura` for both, the add on `obscura_hologram_*`, and the add has **`HasDeathSfx => false`** (`Parafright.cs:31`). **Accessibility:** `TheObscura` is the only Act 2 *normal* with `HasPhobiaSpineSkin => true` (`:30`); the rig carries skins `normal` / `phobia` and a single `bod_phobia` atlas region — a one-region swap, not a second body. | **L** — two rigs, two bespoke VFX nodes on named slots driven by named Spine events, and an accessibility skin obligation on top. | SHIPPED. Gallery: 5 candidates, **1 rated S** (the buff-every-ally beat is the discriminator and only one candidate has it). Not on the §1 redesign-pressure list, but thin. **§4 art-unsafe:** Wail's all-enemies half is UNIMPLEMENTED in the sim — self-buff only (`tier05/content/act2_pool.yaml:142-158`) — so art must not promise a party-wide buff. | S1, S2, S3, S4, S5, S6 |

---

## 3. The complexity scale used above

Identical to `s18-act1.md` §3, so the two files join. Deliberately coarse, and
defined only by what the shipped assets require:

- **S** — one Spine rig; ≤6 clips; hit VFX drawn from the shared
  `res://scenes/vfx/vfx_attack_{slash,blunt}.tscn` / `vfx_bite.tscn` set; no
  bespoke particle nodes; no named Spine attach bones/slots; no named Spine
  animation events; no skin obligation.
- **M** — an S body plus **exactly one** of: a second rig, a named attach
  bone/slot, an encounter scene with named body slots, a skin obligation, or a
  branched sub-state graph.
- **L** — several rigs, **or** a bespoke `N…Vfx` script node whose emitters are
  driven by named Spine animation events, **or** more than one M-grade extra on
  one row.

**Act 2 normals split 2 S / 3 M / 8 L.** Act 1 split 3 S / 0 M / 3 L, so Act 2
is both larger and heavier: **eight of thirteen rows are L**, and they are L for
four different reasons — bespoke event-driven VFX (rows 7, 9, 12, 13), multiple
rigs (rows 10, 13), stacked extras (rows 1, 5, 11), and an accessibility skin
(row 13). They do not collapse into one batch.

Two caveats on the letters, stated so nobody over-reads them:

- **The scale does not price clip count.** Row 6 (Tunneler, 12 clips) and row 5
  (Thieving Hopper, 11 clips) are M and L respectively, but on clip count alone
  they are the two most expensive bodies in the act.
- **Row 2 is an S only because row 1 already paid for its rig.** Read alone it
  is not a body at all; it is a skin.

---

## 4. Act 2 elites and bosses — **owned by the boss/elite integrator**

One line each, no rows, per the charter's owner split. Rig paths and byte sizes
are given only so the integrator does not have to re-derive them.

| Gallery row | Class(es) | Rig(s) / scenes | Pointer |
|---|---|---|---|
| **Decimillipede** (elite) | `Decimillipede…Segment` / `DecimillipedeElite` | **Three separate skeletons** — `decimillipede1/2/3.skel` (145 410 / 150 706 / 135 047 B), three atlases (~5 065 B each), shared texture 820 672 B, plus a `rockstone` prop rig (5 403 B). Scenes: `decimillipede.tscn` **52 474 B** plus three segment scenes ~15–17 KB each; room scene 459 B. | Integrator. **Heaviest Act-2 elite by a wide margin.** Also carries **six phobia-mode textures** (`pck:images/monsters/phobia_mode/decimillipede_segment_{front,middle,back}{,_shriveled}_phobia.png`, 241–278 KB each) and three shader textures (`decimillipede_suck_{gradient,mask,texture}`). **Gallery §1 redesign-pressure: the only claim is a self-declared stretch, and Reattach has no analogue in any of the 16 families** — the gallery calls it "the highest-priority gap here". |
| **Entomancer** (elite) | `Entomancer` / `EntomancerElite` | Skeleton 119 168 B, atlas 1 288 B, texture 136 038 B; scene **8 253 B**; bespoke `NEntomancerVfx` + `entomancer_bug_particle.png`. | Integrator. Carries a **phobia-mode texture** (`pck:images/monsters/phobia_mode/phobia_entomancer.png`). **Gallery §1 redesign-pressure: plausible-only coverage, both claims carry an inverted-incentive caveat.** |
| **Infested Prism** (elite) | `InfestedPrism` / `InfestedPrismsElite` | Skeleton **57 335 B — the lightest body in the whole act**, atlas 993 B, texture 156 462 B; scene 1 382 B, bare contract. | Integrator. Cheapest Act-2 elite to reskin by asset shape. Gallery gives it **four strong candidates** — "pick by which family anchors Act 2's elites". |
| **Knowledge Demon** (boss) | `KnowledgeDemon` / `KnowledgeDemonBoss` | Skeleton **723 441 B — the largest in Act 2 by 2.5×**, atlas 4 792 B, texture 674 250 B; scene **83 838 B**; bespoke `NKnowledgeDemonVfx` + fibre particle; boss icon/outline set. | Integrator. **Gallery §1 redesign-pressure: no strong candidate; both claims carry a caveat, and one of the two is retired limited-time event content.** |
| **Kaiser Crab** (boss) | `KaiserCrusher` + `KaiserRocket` / `KaiserCrabBoss` | One skeleton 218 157 B across **four texture pages** (927 636 / 638 116 / 735 706 / 985 318 B); `kaiser_crab_boss_setup.tscn` **17 036 B** with thin `crusher.tscn` (894 B) and `rocket.tscn` (872 B) wrappers; bespoke background + explosion VFX nodes; room scene 387 B. | Integrator. **Three strong two-body candidates** in the gallery. Note the two-body-one-skeleton architecture before costing it as two rigs. |
| **The Insatiable** (boss, dropped) | `TheInsatiable` / `TheInsatiableBoss` | Skeleton 281 635 B, texture 863 412 B; scene 12 699 B; a second `the_insatiable_boss_node` rig (15 108 B); dedicated room props under `pck:images/rooms/hive/the_insatiable/`. | Integrator. Carries a **phobia-mode texture** (1 298 132 B — the largest phobia asset in the game). Dropped from our sim (`tier05/content/act2_pool.yaml:215-217`) but **live in the base game's Act 2** and **first in `Hive::BossDiscoveryOrder`** (`Core/Models/Acts/Hive.cs:17-22`). Gallery gives it 2 strong candidates. |

---

## 5. Coverage: every mapped Act 2 encounter is accounted for

The gallery's Act 2 block (`docs/current/dossiers/remap/reskin-gallery.md:36-55`)
maps **19 rows**. Disposition:

- **13 rows → §2** (normals): Bowlbug pod, Bowlbug (Nectar), Exoskeletons,
  Chompers, Thieving Hopper, Tunneler, Hunter Killer, Louse Progenitor, Mytes,
  Ovicopter + Tough Eggs, Slumbering Beetle, Spiny Toad, The Obscura +
  Parafright.
- **6 rows → §4** (elites and bosses): Decimillipede, Entomancer, Infested
  Prism, Knowledge Demon, Kaiser Crab, The Insatiable. **Excluded from rows by
  ownership**, per the charter's split, not by judgement.

**Zero mapped Act 2 encounters are excluded for any other reason.**

### 5a. Base-game Act 2 encounters the gallery does **not** map — there are none

`Hive::GenerateAllEncounters` returns exactly **20** encounters
(`Core/Models/Acts/Hive.cs:71-96`). Every one of them is covered by a gallery
row:

| Base encounter | Covered by |
|---|---|
| `BowlbugsNormal`, `BowlbugsWeak` | rows 1 + 2 |
| `ChompersNormal` | row 4 |
| `ExoskeletonsNormal`, `ExoskeletonsWeak` | row 3 |
| `HunterKillerNormal` | row 7 |
| `LouseProgenitorNormal` | row 8 |
| `MytesNormal` | row 9 |
| `OvicopterNormal` | row 10 |
| `SlumberingBeetleNormal` | row 11 |
| `SpinyToadNormal` | row 12 |
| `TheObscuraNormal` | row 13 |
| `ThievingHopperWeak` | row 5 |
| `TunnelerWeak` | row 6 |
| `DecimillipedeElite`, `EntomancerElite`, `InfestedPrismsElite` | §4 |
| `KaiserCrabBoss`, `KnowledgeDemonBoss`, `TheInsatiableBoss` | §4 |

This is a **cleaner join than Act 1**, where ten base Overgrowth encounters
carry no gallery row. Act 2's gallery block is complete against the shipped
act. The one loose end is `TunnelerNormal` (row 6): the class exists, the
Chomper dossier lists it, and no act references it in this build.

### 5b. Where the shipped sim model and the base encounter differ

Not defects — the sim is deliberately a reduced model, and says so
(`tier05/content/act2_pool.yaml:8-19`). Listed because each one changes **how
many bodies need art**, which is the whole point of this file.

| Row | Shipped sim (`tier05/content/act2_pool.yaml`) | Base game | Consequence for art |
|---|---|---|---|
| 1 / 2 Bowlbug pod | **2 fixed bodies**, Rock + Silk (`:23-38`) | **3 bodies**: Rock + two distinct workers from {Egg, Silk, Nectar} (`Encounters/BowlbugsNormal.cs:54-71`) | Art must cover **four skins**, not two. The gallery's "Nectar not in shipped pod" is a sim fact, not a base fact. |
| 1 Bowlbug Egg | not modelled at all | a live worker with a **nested second skeleton** (tough_egg inside the bowlbug rig's `items` slot) | A fourth bowlbug skin **plus** a rig-inside-a-rig contract. |
| 3 Exoskeletons | **3 bodies** (`:40-53`) | **4** in `ExoskeletonsNormal`, 3 in `…Weak` | No extra rig; one more on-screen body. |
| 4 Chompers | Artifact 2 flagged UNIMPLEMENTED (`:70`) | real `ArtifactPower` 2 at spawn (`Monsters/Chomper.cs:49-53`) | A spawn status the art may want to signal. |
| 6 Tunneler | untargetable burrow + emerging stun UNIMPLEMENTED; a 32-block wall stands in (`:54-66`) | a complete **burrowed sub-body**: `hidden_loop`, `hidden_attack`, `hidden_die` | The burrow is **three extra clips**, not a block number. |
| 8 Louse Progenitor | Curl Up folded into a block beat (`:94-107`) | a real curled sub-state with `curled_loop` and its own `die_curled` | Two extra clips and a hurt-less state. |
| 10 Ovicopter | summons 3 fixed-HP eggs; **hatch step UNIMPLEMENTED** (`:123-140`) | eggs hatch in place into Hatchlings, HP re-rolled, clip set swapped (`Monsters/ToughEgg.cs:160-175`) | The egg is a **two-phase body**: 5 egg clips **and** 4 hatched clips on one rig. |
| 11 Slumbering Beetle | dropped; identity is Plating (`:15-17`) | a **three-body room** with two bowlbugs (`Encounters/SlumberingBeetleNormal.cs:24-31`) | Reskinning it commits row 1's family too. |
| 12 Spiny Toad | dropped; identity is Thorns (`:15-17`) | real `ThornsPower` 5 **and** a whole naked-body clip set | The Thorns tell is a **body swap**, which is why the gallery found no clean analogue. |
| 13 The Obscura | Wail is self-buff only; all-enemies half UNIMPLEMENTED (`:142-158`) | one summon, and the buff beat is the row's whole discriminator | Art must not promise a party-wide buff. |
| 5 Thieving Hopper | dropped; theft + flee ops backlogged (`:15-17`) | `EscapeArtistPower`, `SwipePower`, `FlutterPower`, and an airborne mode with its own clip set | The airborne half **doubles** the tell count. |

---

## 6. Socket questions — **PROVISIONAL, S13 pending**

The socket cells in §2 are keys into this list. **None of these is answered
here.** S13 owns them; keys **S1–S6 are shared verbatim with `s18-act1.md`** so
the integrator can join the two matrices, and **S7 / S8 are new in Act 2** — if
Act 3 also extends the list, the integrator should renumber once rather than
twice.

| Key | Question | What is already known locally (**not** an answer) |
|---|---|---|
| **S1** | Can a mod register a **hostile** `MonsterModel` + `EncounterModel` and get it drawn into an act's pool? | `ActModel::GenerateAllEncounters` returns a **fixed array** (`Core/Models/Acts/Hive.cs:71-96`), and pool exclusion runs off `EncounterTag` values (`Workers`, `Chomper`, `Exoskeletons`, `Burrower`, `Thieves` in Act 2). **`klee-mod` references neither `MonsterModel` nor `EncounterModel` anywhere** — grep over `klee-mod/**/*.cs` returns nothing for either name. NON-FINDING on the repo side; no local precedent. |
| **S2** | Can a mod ship its own `creature_visuals` scene + Spine rig and have the engine resolve it? | Three signals, none conclusive. (a) `MonsterModel::VisualsPath` is `protected virtual` (`Core/Models/MonsterModel.cs:216`). (b) The mod PCK is merged into `res://` **before** `[ModInitializer]` runs (`klee-mod/KleeCode/KleePck.cs:7-25`). (c) **There is real local precedent for the scene half — but for a PLAYER, not a monster:** `klee-mod` builds an `NCreatureVisuals` from a mod-PCK scene through BaseLib's `NodeFactory<NCreatureVisuals>.CreateFromScene` (`klee-mod/KleeCode/Klee.cs:233-256`; also `Furina.cs:125-146`, `Kokomi.cs:184-195`). That is the **player** `CreateCustomVisuals` hook, a different door from `MonsterModel::VisualsPath`, and it must not be read as proof for hostiles. **`klee-mod` ships no `SpineSprite` and no Spine skeleton at all** — Klee's combat scene is static sprites — so the Spine half has **no** local precedent either way. |
| **S3** | Can a mod supply the **FMOD** events the id-derived SFX paths demand? | Paths are computed from the monster id (`Core/Models/MonsterModel.cs:292-298`) and resolve out of `pck:banks/desktop/*.bank`. Act 2 makes this worse than Act 1 in one specific way: **eight of the thirteen rows carry at least one explicit SFX event whose namespace is not the monster id** — `roaches` (Exoskeleton), `burrowing_bug` (Tunneler), `giant_louse` (Louse Progenitor), `mite` (Myte), `egg_layer` (Ovicopter), `obscura` (The Obscura **and** its Parafright add, which is `obscura_hologram_*`, `Monsters/Parafright.cs:21-23`), and `workbug_{rock,silk,goop,egg}` for the four bowlbugs. So a reskin cannot assume a new id yields a new event namespace, and one row deliberately shares one namespace across two bodies. **The override is per-property, not per-body:** `BowlbugSilk` overrides `DeathSfx` to `workbug_silk` but leaves `AttackSfx` id-derived (`Monsters/BowlbugSilk.cs:34`, `:58`), so a single body can straddle two namespaces. Three rows also need **looping** events with explicit start/stop (rows 5, 10, 11). No local precedent for adding a bank. |
| **S4** | Can a mod ship an **encounter** scene with named body slots (`HasScene = true`)? | Needed by seven Act 2 rows (1, 3, 9, 10, 11, 13 and the Decimillipede elite). Base scenes are tiny marker-only layouts, 373–695 B. Two encounters additionally override **camera scaling and offset** (`Encounters/MytesNormal.cs:22-31`, `SlumberingBeetleNormal.cs:34-42`), which is scene-adjacent framing state. Reachability from a mod PCK is UNKNOWN. |
| **S5** | Can a mod satisfy the **phobia-skin** contract (`normal` / `phobia` Spine skins) and the runtime skin swap? | `HasPhobiaSpineSkin` is `protected virtual` (`Core/Models/MonsterModel.cs:304`); `NCreatureVisuals` also supports a whole alternate body node `%PhobiaModeVisuals` (`Core/Nodes/Combat/NCreatureVisuals.cs:193`, `:220`). In Act 2 this binds **The Obscura** (row 13) and, in §4, the Decimillipede, Entomancer and The Insatiable — the last three via separate textures under `pck:images/monsters/phobia_mode/`, not skins. It is an **accessibility** obligation, so it also belongs to S20's census. |
| **S6** | Can a mod attach a **custom script node** inside a creature-visuals scene and receive Spine animation events? | Four Act 2 normals do exactly this — `NHunterKillerVfx`, `NMyteVfx`, `NSpinyToadVfx`, `NTheObscuraVfx` / `NParafrightVfx` — each calling `ConnectAnimationEvent` and switching on `MegaEvent…GetEventName()` (`Nodes/Vfx/NTheObscuraVfx.cs:66-82` is the clearest). The event names are **authored into the Spine rig**, so this socket is jointly an engine question and an authoring question. Whether a mod-supplied C# node type can be referenced from a mod-PCK scene is UNKNOWN. |
| **S7** | *(new in Act 2)* Can a mod nest a **child `SpineSprite` inside a `SpineSlotNode`** of a parent skeleton, with independent skin and clip? | Row 1's `bowlbug_egg` does this: parent bowlbug rig, skin `cocoon`, with a child `SpineSprite` on the **tough_egg** rig pinned to parent slot `items`, skin `egg1`, clip `egg_idle_loop`, all set up in code (`Monsters/BowlbugEgg.cs:33-49`). It is the only rig-inside-a-rig in Act 2's normals. UNKNOWN whether a mod scene can express it. |
| **S8** | *(new in Act 2)* Can a mod body declare **multiple named bounds containers** and have `AnimState.BoundsContainer` swap between them? | Row 5's Thieving Hopper ships three (`Bounds`, `GroundedBounds`, `FlyingBounds`) and swaps on state (`Monsters/ThievingHopper.cs:292-307`; `Core/Animation/AnimState.cs:45`, `CreatureAnimator.cs:104-107`). This drives intent-marker and targeting geometry, not just art. UNKNOWN from a mod. |

---

## 7. UNKNOWN and NON-FINDING

- **NON-FINDING — no local hostile-enemy modding precedent.** `klee-mod` ships
  player characters, cards, relics and a PCK. It references no `MonsterModel`
  and no `EncounterModel`. Nothing in this repo proves an enemy can be added or
  reskinned. The player-side `CreateCustomVisuals` precedent noted under S2 is
  a **different hook** and is not evidence for hostiles.
- **NON-FINDING — no mod-supplied Spine rig anywhere in the repo.**
  `klee-mod` contains no `SpineSprite`, no `.skel`, no
  `SpineSkeletonDataResource`. Every Act 2 body is a Spine skeleton, so this is
  the single largest untested assumption in the whole cost model.
- **UNKNOWN — `TunnelerNormal`'s reachability.** The class exists
  (`Encounters/TunnelerNormal.cs`) and pairs a Tunneler with a Chomper, and
  `docs/current/dossiers/enemies/chomper.md:9` lists it as one of Chomper's
  encounters. It appears in **no** `ActModel` encounter list in v0.107.1
  (checked all five). Whether it is dead content, event-reachable, or reached
  by some path not searched here is UNKNOWN. Recorded, not interpreted.
- **UNKNOWN — the exoskeleton rig's unconsumed contract.** The rig carries the
  strings `spray_start`, `spray_end` and a slot `clip_target_slot`, and
  `exoskeleton.tscn` embeds no VFX node and no slot node to receive them.
  Whether these are authoring leftovers, or are consumed somewhere not
  inspected, is UNKNOWN. It is recorded because it shows the art→code contract
  can be one-sided in the shipped game.
- **UNKNOWN — clip-vs-event classification for scan-only names.** Clip names in
  §2 are corroborated twice wherever the C# also declares them
  (`new AnimState("…")`), which covers **every clip named in every row**. Names
  seen **only** in the string scan — `spray_start` / `spray_end` (exoskeleton),
  `headbutt_stunned` beyond its declaration, `bang` / `dirt` / `drop2` /
  `drop3` (bowlbug) — are **UNVERIFIED as clip vs event vs attachment** and may
  be scan artefacts. The Obscura's `attack_slash` is resolved: it is an **atlas
  region**, i.e. baked art, not a clip.
- **UNKNOWN — rig internals.** Bone counts, mesh-vs-bone deformation ratio,
  clip durations, transition mixes beyond the handful declared in
  `*_skel_data.tres`, and draw-call cost were **not** measured. Skeleton byte
  size and atlas region count are used as coarse proxies only. **S16 owns the
  animation corpus and is authoritative over this file on rig internals.**
- **UNKNOWN — audio content.** FMOD bank contents were not opened; only the
  event **paths** the code computes are reported. Whether an event exists
  behind a path was not verified for any body.
- **UNKNOWN — whether phobia-mode coverage is an obligation.** The base game
  ships it for six Hive backgrounds and four Act 2 bodies. Whether a reskin
  must reproduce it is a **scope call and is [USER]'s**; this file only
  measures it.
- **NOT ATTEMPTED — `SKIP-10.9`.** The dormant unimplemented-mechanic rows are
  cited only where the gallery already cites them (§4 art-unsafe warnings on
  rows 3, 6, 8, 10, 11, 13). No prototype, no promotion (charter §3.2 / R183).

---

## 8. What this does **not** establish

It does not choose or rank a Genshin body for any Act 2 encounter, does not
grade RESKIN vs REDESIGN (it only repeats what the gallery already recorded),
does not prove any enemy can be added or reskinned in a mod, does not measure
runtime performance, does not touch the shipped sim, and does not open a
balance window, stamp, or experiment. The complexity letters are an engineering
estimate from asset shape, not a schedule and not a cost in hours. The socket
columns are placeholders for S13's answers and must not be read as answers.
