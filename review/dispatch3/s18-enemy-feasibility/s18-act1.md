# S18 — Implementation-aware enemy feasibility, **Act 1**

> **This decides nothing.** It is an engineering read of what each Act 1
> encounter is *made of* in the shipped game — rig, animation clips, scene
> nodes, particle contract, sound events — so that the enemy mapping [USER]
> has not yet made can be costed. It does **not** rank Genshin candidates, does
> not repeat Genshin canon, and does not pick a reskin. The candidate ordering
> already exists in `docs/current/dossiers/remap/reskin-gallery.md` and is not
> touched here.

- **Date:** 2026-08-26. **Primary checkout:** `223a4ff` (per `PREFLIGHT.md`).
- **Game read:** Slay the Spire 2 **v0.107.1** (`docs/current/STATE.md:158-163`),
  read-only. No game was launched, nothing was deployed, no game file was
  written.
- **Owner split:** this file owns **Act 1 normal encounters only**. Act 1
  elites and bosses are the boss/elite integrator's, and appear here as
  one-line pointers (§4), not rows.
- **Socket columns are `PROVISIONAL — S13 pending`** throughout. S13 (engine
  socket probe) is running concurrently; §6 states the exact questions its
  answers must fill.

---

## 0. How the evidence was obtained

Three sources, all read-only, all local:

| Source | What it gives | Cite form used below |
|---|---|---|
| `sts2.dll` decompiled with ilspycmd 8.2 (`--project --nested-directories`) into the scratchpad | monster/encounter classes, animation-state declarations, VFX/SFX call sites | `<Namespace.Type>::<member>` + `Core/…/File.cs:line` |
| `SlayTheSpire2.pck` directory index, parsed read-only (Godot pack **format 3**, engine **4.5.1**, 15 658 entries, dir at offset 1 899 867 440) | exact resource paths and byte sizes; scene node graphs; Spine skeleton string tables | `pck:<path>` (+ byte size) |
| The repo | the shipped sim model of each encounter, and the existing candidate gallery | repo `file:line` |

Decompile root in the scratchpad:
`…/scratchpad/s18/tree/MegaCrit/sts2/…`. Nothing decompiled was copied into any
repo. The Spine clip/event lists in §2 come from an **ASCII string scan of the
imported `.spskel` binaries**, not from a Spine format parser — see §7 for what
that means for confidence.

**Two engine facts that set the whole cost model** (both load-bearing, both
cited once here rather than in every row):

1. **Every base creature is a Spine skeleton.** Each monster owns exactly one
   folder `res://animations/monsters/<id>/` holding `<id>.atlas`, `<id>.png`,
   `<id>.skel` and `<id>_skel_data.tres`, plus a Godot scene
   `res://scenes/creature_visuals/<id>.tscn`. The game ships
   `libspine_godot.windows.template_release.x86_64.dll` next to the executable.
   No Act 1 body reuses another body's rig: `MonsterModel::VisualsPath` is
   `protected virtual` and defaults to `creature_visuals/<Id.Entry>`
   (`Core/Models/MonsterModel.cs:216`), and the only overrides in the whole
   assembly are `BigDummy` and the five test `Mocks`, all pointing at
   `creature_visuals/defect`.
2. **The default animator is five clips.** `MonsterModel::GenerateAnimator`
   (`Core/Models/MonsterModel.cs:602-619`) builds `idle_loop` (looping),
   `cast`, `attack`, `hurt`, `die`, reachable through the triggers `Idle`,
   `Cast`, `Attack`, `Hit`, `Dead`. A monster that overrides the method renames
   or adds clips; a monster that does not (all four slimes) inherits exactly
   these five. **A missing clip does not crash**: `CreatureAnimator::SetNextState`
   logs `could not find '<id>' animation on '<node>'` and returns
   (`Core/Animation/CreatureAnimator.cs:88-93`), which also drops the queued
   return-to-idle (`:114-121`). A missing *visuals scene* also does not crash:
   `MonsterModel::CreateVisuals` catches, logs, reports to Sentry and
   instantiates `creature_visuals/fallback` — a plain `Sprite2D` showing
   `res://images/monsters/error.png` (`Core/Models/MonsterModel.cs:420-437`;
   `pck:scenes/creature_visuals/fallback.tscn`, 1 064 B).

**The creature-visuals scene contract** (identical in every Act 1 body
inspected): root `Node2D` scripted with
`res://src/Core/Nodes/Combat/NCreatureVisuals.cs`; child `%Visuals`
(`SpineSprite`, carrying `skeleton_data_res` and a per-body `scale`); `%Bounds`
(`Control`); `%CenterPos` and `%IntentPos` (`Marker2D`). Everything beyond
those four nodes is per-body extra, and that extra is what separates an S row
from an L row below.

**Audio is path-derived, not authored per move.** `MonsterModel` computes
`AttackSfx`, `CastSfx` and `DeathSfx` as
`event:/sfx/enemy/enemy_attacks/<id>/<id>_{attack,cast,die}`
(`Core/Models/MonsterModel.cs:292-298`); `HurtSfx` is `null` unless overridden
(`:300-302`), and hit feedback is a shared class chosen by
`TakeDamageSfxType`. These are **FMOD event paths**, resolved out of
`res://banks/desktop/*.bank`, not Godot resources.

---

## 1. Column key

| Column | Means |
|---|---|
| **Asset / rig family** | The base creature's actual rig: one Spine skeleton per named body, with the imported skeleton byte size as a coarse rig-weight proxy. |
| **Required tells / states** | The animation clips the code actually drives, plus any spawn-time power the player must be able to read. |
| **Variants / reuse** | How many distinct art bodies the encounter needs, and what varies in code rather than in art. |
| **VFX / audio surface** | Hit VFX scene(s), bespoke particle nodes, named Spine attach points, named Spine animation events, and the FMOD event paths the body's id implies. |
| **Complexity** | S / M / L on the scale in §3. |
| **RESKIN vs REDESIGN (as the atlas records it)** | Repeated from `reskin-gallery.md` only — candidate density and any flag that row already carries. No new judgement. |
| **Socket — PROVISIONAL, S13 pending** | Which of the six socket questions in §6 this row depends on. |

---

## 2. Act 1 normal encounters — the matrix

Six rows. Every Act 1 encounter the gallery maps is either a row here or is
listed in §4 (elite/boss, integrator-owned) or §5 (mapped-but-excluded /
not-mapped). Nothing mapped is silently dropped.

| # | Encounter (gallery row) | Asset / rig family | Required tells / states | Variants / reuse | VFX / audio surface | Complexity | RESKIN vs REDESIGN (as the atlas records it) | Socket — **PROVISIONAL, S13 pending** |
|---|---|---|---|---|---|---|---|---|
| 1 | **Nibbit** (`NibbitsNormal`, 2 bodies; `NibbitsWeak`, 1) | **1 rig**, `pck:animations/monsters/nibbit/*`; imported skeleton 125 070 B, atlas 953 B, texture 65 634 B. Scene `pck:scenes/creature_visuals/nibbit.tscn` (1 190 B) — the bare 4-node contract, `%Visuals` scale 0.28. | **5 clips**, all present in the rig: `idle_loop` (loop), `attack`, `hiss`, `hurt`, `die`; triggers `Attack` / `Cast`→`hiss` / `Hit` / `Dead` (`Monsters/Nibbit.cs:117-133`). Tells needed: one big hit (Butt), one hit **plus a self-Block gain** (Slice, `:102-109`), one self-buff (Hiss, `:111-115`). No spawn power. | **One art body, three code variants.** `IsFront` / `IsAlone` only change the opening beat (`:74-83`; `Encounters/NibbitsNormal.cs:21-30`, `NibbitsWeak.cs:18-23`). Two bodies on screen in the normal room are the *same* rig. | Hit VFX `vfx/vfx_attack_slash` on both attacks (`:98`, `:106`) → `pck:scenes/vfx/vfx_attack_slash.tscn`, a shared scene. **No bespoke particles, no Spine attach nodes, no Spine events.** Audio: `…/nibbit/nibbit_attack`, `…/nibbit_die` (explicit, `:38`), no hurt event; `TakeDamageSfxType.Slime` (`:40`). Room has a dedicated background scene `pck:scenes/encounters/nibbits_normal.tscn` (371 B, `HasScene=true`). | **S** — one rig, five clips, shared hit VFX only. The only extras are a 371 B encounter scene and two named slots. | SHIPPED. Gallery lists **6 candidates**, top rated **S**; not on the §1 redesign-pressure list. Row's own note: only the top candidate's art explains the Block beat. Candidate #6 is a Whopperflower body, which §5 flags as claimed 6+ times. | S1, S2, S3, S4 |
| 2 | **Inklets ×3** (`InkletsNormal`) | **1 rig** ×3 bodies, `pck:animations/monsters/inklet/*`; skeleton 97 918 B, atlas 1 428 B, texture 55 412 B. Scene `pck:scenes/creature_visuals/inklet.tscn` (1 136 B), bare contract, scale 0.338. | Animator declares **6 states**: `idle_loop`, `cast`, `attack`, `attack_fast`, `hurt`, `die`, with an **extra trigger `TRIPLE_ATTACK` → `attack_fast`** (`Monsters/Inklet.cs:112-131`). Tells needed: small filler hit, a **3-hit flurry played as one animation** (`.WithHitCount(3)…OnlyPlayAnimOnce()`, `:96-101`), one large hit. Spawn-time **`SlipperyPower` 1** on every body (`:57-61`) — a status the player must be able to read. | **One art body ×3.** Only `MiddleInklet` differs (`:82`; `Encounters/InkletsNormal.cs:13-25`). The rig ships **more than one Spine skin** (the scene's `preview_skin = "landjellyfish2"`), but `Inklet` does **not** override `SetupSkins`, so no runtime skin variation is applied — the extra skins are UNKNOWN in reachability. | Hit VFX `vfx/vfx_attack_blunt` on all three moves (`:90`, `:100`, `:108`). Audio: id-derived attack event, plus an **explicit** triple-attack event `…/inklet/inklet_attack_triple` (`:28`, `:99`) and an explicit `HurtSfx` `…/inklet_hurt` (`:55`); `TakeDamageSfxType.Magic`. No particles, no attach nodes, no Spine events. No encounter scene. | **S** — one rig, one extra clip over default, shared VFX. The 3× body count costs nothing in art. | SHIPPED. Gallery calls this **"the most-claimed swarm slot"**: 7 candidates rated **S** plus 2 plausible. Not on the redesign-pressure list. | S1, S2, S3 |
| 3 | **Leaf / Twig Slimes** (`SlimesNormal` 4 bodies; `SlimesWeak` 3) | **4 rigs**, one per body: `leaf_slime_m` (skel 53 709 B), `leaf_slime_s` (48 597 B), `twig_slime_m` (79 295 B), `twig_slime_s` (52 554 B). Four scenes, 1 238–1 404 B, scales 0.273–0.5. | **Default animator, 5 clips each** — none of the four overrides `GenerateAnimator`, so all inherit `idle_loop`/`cast`/`attack`/`hurt`/`die` (`Core/Models/MonsterModel.cs:602-619`). Tells needed: a hit, and a **zero-damage spit that adds `Slimed` cards to the player's discard** (`Monsters/LeafSlimeM.cs:50-73`, `LeafSlimeS.cs:50-56`, `TwigSlimeM.cs:55-78`). `TwigSlimeS` has **no** cast move at all (`TwigSlimeS.cs:23-30`) yet still inherits a declared `cast` state. | **Four art bodies = two families × two sizes.** `SlimesNormal` always fields `TwigSlimeM` + `LeafSlimeM` + one small of each, order coin-flipped (`Encounters/SlimesNormal.cs:33-45`); `SlimesWeak` fields 2 smalls + 1 medium (`SlimesWeak.cs:48-58`). Both rooms carry `EncounterTag.Slimes`, shared with `FlyconidNormal`. `SlimesNormal` also overrides **camera scaling 0.9 and offset +50 y** (`:23-31`). | Hit VFX `vfx/vfx_slime_impact` everywhere. **Two hard rig contracts:** (a) the medium bodies expose a Spine bone `spit_target` as a `SpineBoneNode` named `SpitTarget`, which the code repositions to the leftmost target before the cast (`LeafSlimeM.cs:57-67`; `pck:scenes/creature_visuals/leaf_slime_m.tscn`, `twig_slime_m.tscn`); (b) **`TwigSlimeM` requires two Spine skins named exactly `normal` and `phobia`** — `HasPhobiaSpineSkin => true` (`TwigSlimeM.cs:27`) and `MonsterModel::OnPhobiaModeToggled` calls `data.FindSkin(isOn ? "phobia" : "normal")` (`Core/Models/MonsterModel.cs:643-653`); both skin names and `eyes_phobia` / `pupils_phobia` attachments are present in the twig_slime_m rig. Probable spit-release Spine event `fire` on both mediums (string scan). Audio: four id-derived event families; all four `TakeDamageSfxType.Slime`. No encounter scene. | **L** — not because any one body is hard (each is an S), but because the row is **four rigs**, one of which carries an **accessibility skin obligation**, two of which carry a named-bone obligation. | SHIPPED. Gallery: top candidate rated **S**, and the row's note says the family's claim is "close to unlosable". Not on the redesign-pressure list. Candidate #4 involves Whopperflower bodies, flagged double-booked in §5. | S1, S2, S3, S5 |
| 4 | **Mawler** (`MawlerNormal`, solo) | **1 rig**, skeleton 102 607 B, atlas 1 152 B, texture 260 532 B (the heaviest Act-1-normal texture). Scene `pck:scenes/creature_visuals/mawler.tscn` (1 204 B), bare contract, scale 0.25. | **5 clips**: `idle_loop`, `roar`, `attack`, `hurt`, `die` — i.e. the default set with `cast` **renamed to `roar`** (`Monsters/Mawler.cs:70-87`). Tells needed: a 2-hit combo played under **one** attack animation (`.WithHitCount(2)…OnlyPlayAnimOnce()`, `:60-68`), one big hit, and a **zero-damage roar that applies Vulnerable 3 once per combat** (`:54-58`, weight rule `MoveRepeatType.UseOnlyOnce` at `:37`). | **One body, solo, no variants.** Fixed HP (`MaxInitialHp => MinInitialHp`, `:23`). | Hit VFX `vfx/vfx_attack_slash` on both attacks. Audio: fully id-derived (`mawler_attack`, `mawler_cast`, `mawler_die`), no explicit overrides, default `TakeDamageSfxType`. **No particles, no attach nodes, no Spine events, no encounter scene.** | **S** — the cheapest row in Act 1: one rig, five clips, zero bespoke scene work. | SHIPPED. Gallery lists **8 candidates**, four rated **S**. Not on the redesign-pressure list. The row's own note splits the discriminator between silhouette and the roar-as-pure-debuff beat. | S1, S2, S3 |
| 5 | **Fogmog** (`FogmogNormal` — Fogmog + its summon) | **2 rigs.** `fogmog` (skeleton 94 445 B, atlas 1 365 B) **plus** `eye_with_teeth` (skeleton **183 778 B** — the largest Act-1-normal rig, 299 distinct rig strings — atlas 636 B). Fogmog's scene is **8 121 B**, seven times the bare contract. | Fogmog: **5 clips**, `idle_loop`/`summon`/`attack`/`hurt`/`die`, with `cast` **replaced by a `Summon` trigger** (`Monsters/Fogmog.cs:87-103`). Tells: a turn-1 pure summon that spawns nothing else ever (`:60-68`, no path back to `ILLUSION_MOVE` at `:48-51`), a hit-plus-self-buff, a bigger hit. The add: **3 clips only** — `idle_loop`, `attack`, `die`, **no `hurt` state at all**, and its `Dead` trigger is conditional on the parent already being dead (`Monsters/EyeWithTeeth.cs:53-63`). Add carries spawn-time `IllusionPower` 1 (`:30-34`) and adds `Dazed` cards (`:45-51`). | **Two art bodies.** `EyeWithTeeth` is referenced by **exactly one** encounter in the game (`Encounters/FogmogNormal.cs:19-23`) — no reuse to amortise it. Named slots `fogmog` / `illusion` (`:9-15`), `HasScene = true`, room scene `pck:scenes/encounters/fogmog_normal.tscn` (376 B). | **Bespoke.** The visuals scene embeds a script node **`NFogmogVfx`** (`res://src/Core/Nodes/Vfx/NFogmogVfx.cs`) plus **two `SpineSlotNode`s bound to rig slot names `ground_dust_attach` and `head_thrust_attach`**, carrying three `GPUParticles2D` emitters over two bespoke textures (`pck:images/vfx/monsters/fogmog/fogmog_dust_particle.png`, `…_thrust_particle.png`). The emitters are driven by **named Spine animation events `thrust_start` / `thrust_end`** (`NFogmogVfx.cs:87-115`; both names present in the rig string table). Hit VFX otherwise shared (`vfx_attack_slash`). Audio: explicit summon event `…/fogmog/fogmog_summon` (`:26`, `:62`); `TakeDamageSfxType.Plant` (`:36`). | **L** — two rigs, and the parent's rig must expose two named slots *and* fire two named animation events or the bespoke particle layer is silently dead. | SHIPPED. Gallery: 2 candidates rated **S**, 3 plausible; the row explicitly says the wisp "reskins as a Specter or small slime under any parent" and that the parent is the contested part. Not on the redesign-pressure list. Candidate #2 is Large Dendro Slime, flagged double-booked ×5 in §5. | S1, S2, S3, S4, S6 |
| 6 | **Sewer Clam** (`SewerClamNormal`, solo) | **1 rig**, skeleton 106 928 B, atlas 766 B, texture 305 484 B. Scene **7 451 B** — the second-heaviest Act-1-normal scene, scale 0.25. | **5 driven clips**: `idle_loop`, `buff`, `attack`, `hurt`, `die` — `cast` renamed to `buff` (`Monsters/SewerClam.cs:62-79`). The rig additionally holds `attack_straight` and `die_slower`, which nothing in the class drives. Tells: one blunt hit, one self-buff (+4 Strength, unbounded, `:47-52`), and a spawn-time **`PlatingPower`** applied in `AfterAddedToRoom` (`:29-34`). | **One body, solo, fixed HP** (`:23`). No variants, no adds. | **Bespoke and the heaviest in Act 1.** The scene embeds **`NSewerClamVfx`** (`res://src/Core/Nodes/Vfx/NSewerClamVfx.cs`), a `SpineBoneNode` bound to rig bone **`scale_adjuster`**, a `SpineSlotNode` bound to rig slot **`clam_particles_attach`**, and three `GPUParticles2D` emitters (death / buff / chomp) over two **shared** textures (`res://images/vfx/miasma_cloud.png`, `spit_glob_particles.png`). The emitters are driven by **five named Spine animation events**: `death_explode`, `darkness_start`, `darkness_end`, `chomp`, `grow` (`NSewerClamVfx.cs:152-172`); all five are present in the rig string table. A sixth name, `death_end`, is in the rig and has a private `OnDeathEnd` handler (`:179-`) that the event switch never reaches — recorded, not relied on. Hit VFX `vfx/vfx_attack_blunt`. Audio: explicit buff event `…/sewer_clam/sewer_clam_buff` (`:19`, `:49`); `TakeDamageSfxType.Stone` (`:27`). No encounter scene. | **L** — one rig, but five named animation events plus a named bone plus a named slot is the tightest art-to-code contract of any Act 1 normal. | SHIPPED. Gallery: 3 candidates rated **S**, 5 plausible. **Carries the gallery's §4 unimplemented-mechanic warning**: Plating is modelled as flat block in the shipped sim (`tier05/content/act1_pool.yaml:88-96`) with the damage **cap** skipped, so "art shouldn't promise a damage cap that isn't there" (`reskin-gallery.md` §4). Not on the redesign-pressure list. | S1, S2, S3, S6 |

---

## 3. The complexity scale used above

Deliberately coarse, and defined only by what the shipped assets require:

- **S** — one Spine rig; ≤6 clips; hit VFX drawn from the shared
  `res://scenes/vfx/vfx_attack_{slash,blunt}.tscn` / `vfx_slime_impact.tscn`
  set; no bespoke particle nodes; no named Spine attach bones/slots; no named
  Spine animation events; no skin obligation.
- **M** — an S body plus exactly one of: a second rig, a named attach
  bone/slot, an encounter scene with named body slots, or a skin obligation.
  *(No Act 1 normal landed here; the row set is bimodal.)*
- **L** — several rigs, **or** a bespoke `N…Vfx` script node whose emitters are
  driven by named Spine animation events, **or** an accessibility skin
  obligation on top of a multi-body row.

**Act 1 normals split 3 S / 0 M / 3 L.** The three L rows are L for three
different reasons — body count (Slimes), a second unamortised rig plus an event
contract (Fogmog), and a six-event contract on a single body (Sewer Clam) — so
they do not collapse into one batch.

---

## 4. Act 1 elites and bosses — **owned by the boss/elite integrator**

One line each, no rows. Rig paths given only so the integrator does not have to
re-derive them.

| Gallery row | Class(es) | Rig(s) | Pointer |
|---|---|---|---|
| Byrdonis (elite) | `Byrdonis` / `ByrdonisElite` | `animations/monsters/byrdonis/*` (skel 156 650 B); scene 1 160 B | Integrator. **Caution:** `Byrdpip` is **not** this elite's add — it is a *player pet* spawned by the relic of the same name (`Models/Relics/Byrdpip.cs:71`, `Models/Cards/ByrdSwoop.cs:28`). Do not file it as a hostile body. |
| Bygone Effigy (elite) | `BygoneEffigy` / `BygoneEffigyElite` | `animations/monsters/bygone_effigy/*` (skel 34 256 B, texture 628 404 B); scene 1 442 B | Integrator. |
| Phantasmal Gardener ×4 (elite) | `PhantasmalGardener` / `PhantasmalGardenersElite` | `animations/monsters/phantasmal_gardener/*` (skel 208 261 B); scene 3 556 B; room scene 530 B; 1 bespoke VFX texture | Integrator. Note for costing: **four named slots** `first`…`fourth` and a real `SetupSkins` override that gives slots 1 and 3 a Spine skin named `tall` (`Monsters/PhantasmalGardener.cs:73-83`) — a skin obligation, not just a recolour. |
| Vantom (boss) | `Vantom` / `VantomBoss` | `animations/monsters/vantom/*` (skel **393 130 B**, atlas 4 495 B); scene **12 262 B**; 3 bespoke VFX textures | Integrator. Gallery §4 flags Slippery as UNIMPLEMENTED for this row. |
| Lagavulin Matriarch (boss) | `LagavulinMatriarch` / `LagavulinMatriarchBoss` | `animations/monsters/lagavulin_matriarch/*` (skel 267 219 B, texture 610 814 B); scene 1 411 B; `SetupSkins` override | Integrator. Gallery §4 flags the Plating cap and Soul Siphon as UNIMPLEMENTED; the gallery also records this row as a **[USER]-locked pick**. |
| Ceremonial Beast (boss, research) | `CeremonialBeast` | `animations/monsters/ceremonial_beast/*` + `death_emitter.png` | Integrator. |
| The Kin (boss, research) | `KinPriest` + `KinFollower` | two rigs; room scene 455 B, slots `slot1`/`slot2`/`leaderSlot`; both bodies override `SetupSkins`; 5 bespoke VFX textures between them | Integrator. |
| Waterfall Giant (boss, research) | `WaterfallGiant` | 3 bespoke VFX textures | Integrator. **Gallery §1 redesign-pressure: one claimant, element inverted.** |
| Soul Fysh (boss, research) | `SoulFysh` | 3 bespoke VFX textures | Integrator. **Gallery §1 redesign-pressure: zero candidates in any family.** |

---

## 5. Coverage: every mapped Act 1 encounter is accounted for

The gallery's Act 1 block (`reskin-gallery.md`, "ACT 1 — Overgrowth" and "ACT 1
boss pool — research") maps **15 rows**. Disposition:

- **6 rows → §2** (normals): Nibbit, Inklets ×3, Leaf/Twig Slimes, Mawler,
  Fogmog, Sewer Clam.
- **9 rows → §4** (elites and bosses): Byrdonis, Bygone Effigy, Phantasmal
  Gardener ×4, Vantom, Lagavulin Matriarch, Ceremonial Beast, The Kin,
  Waterfall Giant, Soul Fysh. **Excluded from rows by ownership**, per the
  charter's split, not by judgement.

**Zero mapped Act 1 encounters are excluded for any other reason.**

### 5a. Act 1 encounters the gallery does **not** map (context, not a gap claim)

The base game has **two Act 1 regions**, both `Index => 0`: `Overgrowth`
(`IsDefault => true`, 22 encounters, `Models/Acts/Overgrowth.cs:71-98`) and
`Underdocks` (`IsDefault => false`, 20 encounters,
`Models/Acts/Underdocks.cs:44-46`, `:66-91`).
Our shipped `act1_pool.yaml` draws from **both** — Sewer Clam, Phantasmal
Gardener and Lagavulin Matriarch are Underdocks bodies — while the gallery
labels its Act 1 block "Overgrowth". Base-game Overgrowth encounters that our
pool does not model, and which therefore carry no gallery row:
`CubexConstructNormal`, `FlyconidNormal`, `FuzzyWurmCrawlerWeak`,
`OvergrowthCrawlers`, `PhrogParasiteElite`, `RubyRaidersNormal`,
`ShrinkerBeetleWeak`, `SlitheringStranglerNormal`, `SnappingJaxfruitNormal`,
`VineShamblerNormal`. **Reason for exclusion:** they are not in our Act 1 pool
and the atlas maps no row for them; whether they should be is a scope call and
is [USER]'s, not this file's.

### 5b. Where the shipped sim model and the base encounter differ

Not defects — the sim is deliberately a reduced model (`act1_pool.yaml:15-18`
states the layer boundary). Listed because each one changes **how many bodies
need art**, which is the whole point of this file.

| Row | Shipped sim (`tier05/content/act1_pool.yaml`) | Base game | Consequence for art |
|---|---|---|---|
| Slimes | **2 bodies**, `leaf_slime` + `twig_slime`, HP 25–35 each (`:44-58`) | **4 bodies** in `SlimesNormal` (M+M+S+S), HP bands 7–11 / 11–15 / 26–28 / 32–35 | **4 rigs**, not 2, if the encounter is ever reskinned at base fidelity. |
| Slimes | Frail 1 / Weak 1 debuff beats (`:53`, `:58`) | Adds **`Slimed` status cards** to the discard pile (`LeafSlimeM.cs:72`) | The spit tell reads as a card-pollution move, not a debuff. |
| Fogmog | Summons `fog_wisp`, HP 12, attack 5 (`:80-81`) | Summons **`EyeWithTeeth`**, HP 6, adds 3 `Dazed`, carries `IllusionPower` (`EyeWithTeeth.cs:22-51`) | The add is a **named body with its own 183 KB rig**, not a generic wisp. |
| Inklets | attack 4 only (`:34-42`) | 3 moves incl. a hidden 10-damage `Piercing Gaze`, plus spawn `SlipperyPower` (`Inklet.cs:57-61`) | A third tell and one readable spawn status. |
| Sewer Clam | block 8, "UNIMPLEMENTED: Plating damage-CAP" (`:88-96`) | Real `PlatingPower` (`SewerClam.cs:29-34`) | Matches the gallery's §4 art-unsafe warning. |
| Nibbit | one body per row (`:22-32`) | `NibbitsNormal` fields **two** phase-offset bodies | No extra rig; two on-screen bodies of one rig. |

---

## 6. Socket questions — **PROVISIONAL, S13 pending**

The socket cells in §2 are keys into this list. None of these is answered here;
S13 owns them, and Lane D's go/no-go rides on S1 and S2.

| Key | Question | What is already known locally (not an answer) |
|---|---|---|
| **S1** | Can a mod register a **hostile** `MonsterModel` + `EncounterModel` and get it drawn into an act's pool? | `ActModel::GenerateAllEncounters` returns a **fixed array** (`Models/Acts/Overgrowth.cs:71-98`); `MonsterModel` is abstract with `protected abstract`/`virtual` members throughout. **`klee-mod` contains no `MonsterModel` or `EncounterModel` reference at all** — grep over `klee-mod/KleeCode/**/*.cs` returns nothing. So there is **no local precedent**: NON-FINDING on the repo side. |
| **S2** | Can a mod ship its own `creature_visuals` scene + Spine rig and have the engine resolve it? | Two encouraging signals, neither conclusive: `MonsterModel::VisualsPath` is `protected virtual` (`Core/Models/MonsterModel.cs:216`), and the mod loader already merges a mod PCK into `res://` **before** `[ModInitializer]` runs (`klee-mod/KleeCode/KleePck.cs:7-25`). Whether a `SpineSprite`/`skeleton_data_res` authored outside MegaDot imports correctly is UNKNOWN. |
| **S3** | Can a mod supply the **FMOD** events the id-derived SFX paths demand (`event:/sfx/enemy/enemy_attacks/<id>/<id>_attack` etc.)? | The paths are computed from the monster id (`Core/Models/MonsterModel.cs:292-298`) and resolve out of `res://banks/desktop/*.bank`, i.e. FMOD banks, not Godot resources. No local precedent for adding a bank. **This is the least-explored socket in Act 1 and it touches every row.** |
| **S4** | Can a mod ship an **encounter** scene with named body slots (`HasScene = true`)? | Needed by Nibbit and Fogmog rows (`Encounters/NibbitsNormal.cs:13-17`, `FogmogNormal.cs:9-17`). Base scenes are tiny (371 B / 376 B). Reachability from a mod PCK is UNKNOWN. |
| **S5** | Can a mod satisfy the **phobia-skin** contract (`normal` / `phobia` Spine skins) and the runtime skin swap? | `HasPhobiaSpineSkin` is `protected virtual` (`Core/Models/MonsterModel.cs:304`) and the swap goes through `OnPhobiaModeToggled` → `data.FindSkin("phobia"|"normal")` (`:643-653`). Only relevant to the Slimes row in Act 1 (`TwigSlimeM.cs:27`), but it is an **accessibility** obligation, so it also belongs to S20's census. |
| **S6** | Can a mod attach a **custom script node** inside a creature-visuals scene and receive Spine animation events? | The two bespoke Act 1 cases both do exactly this: `NFogmogVfx` and `NSewerClamVfx` call `ConnectAnimationEvent` and switch on `MegaEvent…GetEventName()` (`NFogmogVfx.cs:84-101`, `NSewerClamVfx.cs:152-172`). Whether a mod-supplied C# node type can be referenced from a mod-PCK scene is UNKNOWN. |

---

## 7. UNKNOWN and NON-FINDING

- **NON-FINDING — no local enemy-modding precedent.** `klee-mod` ships player
  characters, cards, relics and a PCK; it references no monster or encounter
  type. Nothing in this repo proves an enemy can be added or reskinned.
- **UNKNOWN — exact Spine clip and event lists.** §2's clip and event names
  come from an ASCII string scan of the imported `.spskel` binaries, not a
  Spine parser. Names that the C# code *also* names (`hiss`, `roar`, `summon`,
  `attack_fast`, `thrust_start`, `chomp`, …) are corroborated twice and are
  safe. Names seen **only** in the scan — `attack_triple` (inklet),
  `attack_straight` / `die_slower` (sewer clam), `fire` (both medium slimes) —
  are **UNVERIFIED as clip-vs-event and may be scan artefacts.**
- **UNKNOWN — declared-but-unbacked animation state.** `Inklet` declares a
  `cast` state (`Monsters/Inklet.cs:115`) and no `cast` string appears in its
  rig scan, but no Inklet move ever fires the `Cast` trigger, so the mismatch
  is never exercised. Whether this is an authoring leftover or a scan miss is
  UNKNOWN. It is recorded because it demonstrates the engine's
  warn-and-continue behaviour is real shipped tolerance, not theory.
- **UNKNOWN — rig internals.** Bone/attachment counts, clip durations,
  mesh-vs-bone deformation ratio, and draw-call cost were **not** measured;
  skeleton byte size is used as a coarse proxy only. S16 owns the animation
  corpus and should be treated as authoritative over this file on rig
  internals.
- **UNKNOWN — inklet's extra Spine skins.** The scene names
  `preview_skin = "landjellyfish2"`, and skin-looking strings (`clipper`,
  `landjellyfish2`) appear in the rig, but `Inklet` does not override
  `SetupSkins`. Whether the alternates are reachable at runtime is UNKNOWN.
- **UNKNOWN — audio content.** FMOD bank contents were not opened; only the
  event **paths** the code computes are reported. Whether an event exists
  behind a path was not verified for any body.
- **NOT ATTEMPTED — `SKIP-10.9`.** The dormant Plating-cap row is cited only
  where the gallery already cites it (Sewer Clam §4 warning). No prototype, no
  promotion (charter §3.2 / R183).

---

## 8. What this does **not** establish

It does not choose or rank a Genshin body for any Act 1 encounter, does not
grade RESKIN vs REDESIGN (it only repeats what the gallery already recorded),
does not prove any enemy can be added or reskinned in a mod, does not measure
runtime performance, does not touch the shipped sim, and does not open a
balance window, stamp, or experiment. The complexity letters are an engineering
estimate from asset shape, not a schedule and not a cost in hours.
