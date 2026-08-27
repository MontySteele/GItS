# S18 — Implementation-aware enemy feasibility, **Act 3**

> **This decides nothing.** It is an engineering read of what each Act 3
> encounter is *made of* in the shipped game — rig, animation clips, scene
> nodes, particle contract, sound events — so that the enemy mapping [USER]
> has not yet made can be costed. It does **not** rank Genshin candidates, does
> not repeat Genshin canon, and does not pick a reskin. The candidate ordering
> already exists in `docs/current/dossiers/remap/reskin-gallery.md` and is not
> touched here.

- **Date:** 2026-08-26. **Primary checkout:** `223a4ff` (per `PREFLIGHT.md`).
- **Game read:** Slay the Spire 2 **v0.107.1** (`docs/current/STATE.md:158-163`),
  read-only. No game was launched, nothing was deployed, no game file was
  written, and no decompiled or extracted game data was copied into any repo.
- **Owner split:** this file owns **Act 3 normal encounters only** (11 rows).
  Act 3 elites and bosses are the boss/elite integrator's and appear here as
  one-line pointers (§4), not rows.
- **Socket columns are `PROVISIONAL — S13 pending`** throughout, per dispatch
  instruction. The socket keys `S1`–`S6` are the **same keys** used in
  `s18-act1.md` §6, restated in §6 below so this file reads cold and so the
  joined matrix has one key space. (`s13-engine-sockets.md` was present in
  `review/dispatch3/` when this file was written; joining its answers to these
  cells is the integrator's step, not this file's.)
- **Sibling file:** `s18-act1.md`. The complexity scale in §3 and the engine
  facts in §0 are deliberately identical to it so the two files join.

---

## 0. How the evidence was obtained

Three sources, all read-only, all local.

| Source | What it gives | Cite form used below |
|---|---|---|
| `sts2.dll` decompiled per-type with ilspycmd 8.2 (`-t <FullTypeName>`) into the scratchpad | monster/encounter/act classes, animation-state declarations, VFX/SFX call sites, Spine-event switches | `<Namespace.Type>::<member>` + `<File>.cs:line` (scratch tree `…/scratchpad/s18/decompile/`) |
| `SlayTheSpire2.pck` directory index, parsed read-only (Godot pack **format 3**, engine **4.5.1**, 15 658 entries, directory offset read from header `+0x20` = 1 899 867 440) | exact resource paths and byte sizes; scene node graphs; Spine atlas region lists; Spine skeleton string tables | `pck:<path>` (+ byte size) |
| The repo | the shipped sim model of each encounter, the behaviour dossiers, and the existing candidate gallery | repo `file:line` |

Scratch tree: `…/scratchpad/s18/` — `pck_index.txt` (the parsed directory),
`extracted/` (the handful of scenes/atlases pulled out), `decompile/` (44
single-type decompiles). Nothing there was copied into a repo.

**Spine version.** Every monster skeleton in the pack carries the Spine binary
header `4.2.43` (read at byte 9 of each imported `.spskel`). The runtime plugin
`libspine_godot.windows.template_release.x86_64.dll` ships next to the
executable.

**Four engine facts that set the whole cost model** (cited once here, not in
every row):

1. **Every base creature is a Spine skeleton, one rig per named body.** Each
   monster owns `res://animations/monsters/<id>/` holding `<id>.atlas`,
   `<id>.png`, `<id>.skel`, `<id>_skel_data.tres`, plus a scene
   `res://scenes/creature_visuals/<id>.tscn`. `MonsterModel::VisualsPath` is
   `protected virtual` and defaults to `creature_visuals/<Id.Entry>`
   (`MonsterModel.cs:216`). **No Act 3 body reuses another Act 3 body's rig.**
   *The one exception in Act 3 is not a Spine rig at all — see Aeonglass, §4.*
2. **The default animator is five clips.** `MonsterModel::GenerateAnimator`
   (`MonsterModel.cs:602-619`) builds `idle_loop` (looping), `cast`, `attack`,
   `hurt`, `die`, reached through triggers `Idle`, `Cast`, `Attack`, `Hit`,
   `Dead`. The engine's canonical clip names are constants on
   `AnimState`: `attack`, `cast`, `die`, `hurt`, `idle_loop`, `revive`, `stun`
   (`AnimState.cs:15-27`); the trigger constants are on `CreatureAnimator`:
   `Idle`, `Attack`, `PowerUp`, `Cast`, `Dead`, `Hit`, `Revive`
   (`CreatureAnimator.cs:11-23`). **A missing clip does not crash:**
   `CreatureAnimator::SetNextState` logs `could not find '<id>' animation on
   '<node>'` and returns (`CreatureAnimator.cs:88-93`), and the queued
   return-to-idle is dropped the same way (`:116-121`). A missing *visuals
   scene* also does not crash: `MonsterModel::CreateVisuals` catches, logs,
   reports to Sentry, and instantiates `creature_visuals/fallback`
   (`MonsterModel.cs:421-437`; `pck:scenes/creature_visuals/fallback.tscn`,
   1 064 B, a `Sprite2D` on `pck:images/monsters/error.png`).
3. **The creature-visuals scene contract is four nodes.**
   `NCreatureVisuals::_Ready` resolves `%Visuals` (`Node2D`), `%Bounds`
   (`Control`), `%IntentPos` and `%CenterPos` (`Marker2D`), with `%OrbPos` and
   `%TalkPos` optional and `%PhobiaModeVisuals` optional
   (`NCreatureVisuals.cs:219-225`). **The body does not have to be Spine:** the
   Spine path is gated on `_body.GetClass() == "SpineSprite"` (`:185`), so a
   plain `Sprite2D` body is a legal creature. Everything past those four nodes
   is per-body extra, and that extra is what separates an S row from an L row.
4. **Audio is id-derived, not authored per move.** `MonsterModel` computes
   `AttackSfx`, `CastSfx`, `DeathSfx` as
   `event:/sfx/enemy/enemy_attacks/<id>/<id>_{attack,cast,die}`
   (`MonsterModel.cs:292-296`); `HurtSfx` is `null` unless overridden
   (`:300-302`); hit feedback is a shared class chosen by `TakeDamageSfxType`
   (`:327-329`), whose values are `None, Armor, ArmorBig, Fur, Insect, Magic,
   Plant, Slime, Stone` (`DamageSfxType.cs`). These are **FMOD event paths**
   resolved out of `res://banks/desktop/*.bank` (12 banks, including
   `act3_a1.bank` / `act3_a2.bank`), not Godot resources. **Consequence for a
   reskin:** a body that keeps its base monster id inherits its audio for free;
   a body under a new id needs either new bank content or an explicit Sfx
   override.

---

## 1. Column key

| Column | Means |
|---|---|
| **Asset / rig family** | The base creature's actual rig: one Spine skeleton per named body, with imported skeleton byte size as a coarse rig-weight proxy, plus atlas page size / region count and the creature-visuals scene size. |
| **Required tells / states** | The animation clips the code actually drives (from the class's `GenerateAnimator`), which clips exist in the rig but are undriven, and any spawn-time power the player must be able to read. |
| **Variants / reuse** | How many distinct art bodies the encounter needs, what varies in code rather than in art, and which other encounters share the same body. |
| **VFX / audio surface** | Hit VFX scene(s), bespoke `N…Vfx` script nodes, named Spine attach bones/slots, named Spine animation events, skin obligations, and the FMOD event paths the body's id implies. |
| **Complexity** | S / M / L on the scale in §3 — the same scale `s18-act1.md` uses. |
| **RESKIN vs REDESIGN (as the atlas records it)** | Repeated from `reskin-gallery.md` only — candidate density and any flag that row already carries. No new judgement. |
| **Socket — PROVISIONAL, S13 pending** | Which of the socket questions in §6 this row depends on. |

---

## 2. Act 3 normal encounters — the matrix

Eleven rows. Nine are shipped in the sim's Act 3 pool; two (Owl Magistrate,
The Lost + The Forgotten) are on the sim's dropped/re-add list but are live
base-game Act 3 encounters and are mapped by the gallery, so they get full
rows. Every encounter in the base game's Act 3 list is accounted for in §5.

| # | Encounter (gallery row) | Asset / rig family | Required tells / states | Variants / reuse | VFX / audio surface | Complexity | RESKIN vs REDESIGN (as the atlas records it) | Socket — **PROVISIONAL, S13 pending** |
|---|---|---|---|---|---|---|---|---|
| 1 | **Devoted Sculptor** (`DevotedSculptorWeak`, solo, 162 HP) — gallery `reskin-gallery.md:57` | **1 rig.** Skeleton **202 502 B**, atlas 1 page `1539×237` with **53 regions**, texture 210 238 B. Scene `pck:scenes/creature_visuals/devoted_sculptor.tscn` **5 715 B**, `%Visuals` scale 0.25, extra `%TalkPos` marker. Note the base game's own filename typo: the skel is `devoted_scultpor.skel`. | **5 clips, the default set** — `DevotedSculptor` does **not** override `GenerateAnimator`, so `idle_loop`/`cast`/`attack`/`hurt`/`die` (`MonsterModel.cs:602-619`). Tells needed: one turn-1 cast that applies **Ritual 9 to itself** and speaks a line (`DevotedSculptor.cs:44-48`), and one ramping attack. Scan of the rig finds exactly those five clip names. | **One body, solo, no variants, no adds.** Rig used by no other encounter. | **Bespoke.** `NDevotedSculptorVfx` (`pck:src/Core/Nodes/Vfx/NDevotedSculptorVfx.cs`) on a `SpineBoneNode` bound to bone **`voice_attach`**, driving two `GPUParticles2D` over two bespoke textures (`…/devoted_sculptor_voice_particle.png`, `…_spark_particle.png`). Emitters are driven by **named Spine events `caw` and `attack`** (`NDevotedSculptorVfx.cs:89-101`). Also fires the shared scene `vfx/vfx_scream` on creature centre (`DevotedSculptor.cs:47`) and a `TalkCmd` banter line at `%TalkPos` (`:48`). Hit VFX `vfx/vfx_attack_blunt` (`:57`). Audio: fully id-derived; `TakeDamageSfxType.Fur` (`:27`). | **L** — bespoke `N…Vfx` node whose emitters are driven by named Spine animation events. The animator itself is the cheapest possible (default 5). | SHIPPED. Gallery lists **6 candidates, four rated S**; row note: "Four strong ritual-casters; assign by act faction." Not on the §1 redesign-pressure list. | S1, S2, S3, S6 |
| 2 | **Scrolls of Biting ×3 / ×4** (`ScrollsOfBitingWeak` 3 bodies, `ScrollsOfBitingNormal` 4 bodies; 31–38 HP each) — gallery `:58` | **1 rig ×3–4 bodies.** Skeleton 177 205 B, atlas `493×524` with **33 regions**, texture 138 496 B. Scene 1 166 B — the bare 4-node contract, scale 0.27. | **6 clips**: `idle_loop`, `buff`, `attack`, `attack_double`, `hurt`, `die`, with `Cast`→`buff` and a **non-standard trigger `ATTACK_DOUBLE`** (`ScrollOfBiting.cs:128-146`). Tells needed: one big bite (Chomp), a 2-hit bite (Chew), one self-buff (+2 Str). Move machine is a `RandomBranchState` with a cannot-repeat rule (`:89-90`), so intents vary run to run. | **One art body, 3 or 4 copies, two encounters.** The two encounters differ only in count (`E_ScrollsOfBitingWeak.cs:20-22` = 3 bodies; `E_ScrollsOfBitingNormal.cs:18-21` = 4). | **Skin obligation.** `ScrollOfBiting::SetupSkins` composes a runtime skin from a **random pick between Spine skins `skin1` and `skin2`** per body (`:21`, `:64-71`) — so the copies on screen are visibly different and a reskin must ship **two** skins, not one. Otherwise clean: no particles, no attach points, no Spine events, no encounter scene. Hit VFX `vfx/vfx_bite` (`:107`). Audio: explicit `DeathSfx` string (`:49`), `TakeDamageSfxType.Magic` (`:45`). | **M** — an S body plus exactly one extra: a skin obligation. | SHIPPED. Gallery: **1 candidate rated S, 5 plausible**; row note calls it the consolation slot for whoever lost the Act-1/Act-2 swarm rows. Not on the redesign-pressure list. | S1, S2, S3, S5 |
| 3 | **Living Shield + Turret Operator** (`TurretOperatorWeak`, 55 + 41 HP) — gallery `:59` | **2 rigs.** `living_shield`: skeleton **58 440 B** — the lightest skeleton of any Act-3 body that is not a summoned bot — atlas `1953×650` / **49 regions**, texture 455 106 B, scene 1 158 B (bare contract, scale 0.15). `turret_operator`: skeleton 127 893 B, atlas `380×1023` / **50 regions**, texture 244 528 B, scene 1 166 B (bare contract). | Living Shield: **default 5 clips** (no `GenerateAnimator` override). Turret Operator: **5 clips** with `cast` renamed **`crank`** and a non-standard trigger `Crank` (`TurretOperator.cs:67-83`). Tells needed: one small hit and one big hit + self-buff (Shield Slam / Smash); one 5-hit volley played under **one** attack animation, and one hand-crank buff. **A spawn-time power with no animation at all:** Living Shield applies **Rampart 25 to itself** in `AfterAddedToRoom` (`LivingShield.cs:32-36`), and that counter pumps Block onto every living **`TurretOperator`** — a filter **by monster type** (`docs/current/dossiers/enemies/living-shield.md`). **Undriven rig content:** the Living Shield rig also contains `barricade_loop` and `barricade_hurt`, which no code path names. | **Two art bodies, hard-wired as a pair.** `TurretOperatorWeak` always fields exactly one of each (`E_TurretOperatorWeak.cs:23-24`); neither body appears in any other encounter. The pairing is enforced by the type filter above, not by slots — so a reskin that splits the two bodies across Genshin families breaks the one relationship the encounter is about. | No bespoke VFX node, no attach points, no Spine events, no encounter scene on either body. Hit VFX `vfx/vfx_attack_slash` (Living Shield, `:58`) and `vfx/vfx_attack_blunt` (Turret Operator, `:63`). Audio: Living Shield **has no death sound** — `HasDeathSfx => false` (`:24`) — and `TakeDamageSfxType.Armor` (`:22`), i.e. it reads as equipment, not a creature (`living-shield.md:45`). Turret Operator overrides `HurtSfx` explicitly (`:25`) and is `TakeDamageSfxType.Fur` (`:31`). | **M** — an S body plus exactly one extra: a second rig. | SHIPPED. Gallery calls this **"the most-claimed encounter in the atlas" (10+ families)**, lists **10 candidates, eight rated S**, and notes only #1–2 are ones where the front body's canon ability is protecting the back body. Not on the redesign-pressure list. | S1, S2, S3 |
| 4 | **Axebot** (`AxebotsNormal`, one body per spawn, 70–78 HP) — gallery `:60` | **1 rig.** Skeleton 102 313 B, atlas `1365×507` / **39 regions**, texture 254 048 B. Scene `pck:scenes/creature_visuals/axebot.tscn` **8 261 B** — seven times the bare contract, scale 0.13. | **7 clips**: `idle_loop`, `attack`, `special`, `sharpen`, `respawn`, `hurt`, `die`, with non-standard triggers `uppercut`→`special`, `sharpen`, `respawn` (`Axebot.cs:131-152`). Tells needed: Boot Up (block + Str), One-Two (2 hits, one animation), Hammer Uppercut (hit + Weak + Frail), and **a death-and-replace**: the body carries a Stock counter that spawns a fresh Axebot in the same slot, plays `respawn`, and blocks combat from ending (`axebot.md:70`). **Note:** `respawn` is a *custom* trigger, **not** the engine's `revive` constant (`AnimState.cs:25`), so a reskin cannot get it for free from the default contract. | **One art body, played three times sequentially.** One encounter, one named slot `front`, `HasScene = true` (`E_AxebotsNormal.cs:11-21`; `pck:scenes/encounters/axebots_normal.tscn`, 294 B — a single `front` marker). Rig used nowhere else. | **Bespoke and the second-densest in Act 3.** `NAxebotVfx` (`pck:src/Core/Nodes/Vfx/NAxebotVfx.cs`) is itself a **`SpineSprite`** child of `%Visuals`. Two `SpineSlotNode`s bound to slots **`thrust_right_attach`** / **`thrust_left_attach`** carry smoke emitters; a `SpineBoneNode` on bone **`spark_attach`** carries two hurt emitters. Emitters are driven by **five named Spine events**: `start_hurt_sparks`, `start_death_sparks1`, `start_death_sparks2`, `landing_smoke_start`, `landing_smoke_end` (`NAxebotVfx.cs:129-147`). Textures: one bespoke (`axebot_spark_particle.png`) + one shared (`images/vfx/shared_use/smoke_vfx.png`). Hit VFX `vfx_attack_slash` and `vfx_attack_blunt`. Audio id-derived; `TakeDamageSfxType.Armor` (`:48`). | **L** — bespoke `N…Vfx` node driven by named Spine events, on top of a 7-clip set with a respawn state and an encounter scene. | SHIPPED. Gallery lists **6 candidates, five rated S**; row note: "Electro hammer-bruisers are over-supplied; the Mitachurl is the only non-Fatui option that keeps the weapon." Not on the redesign-pressure list. | S1, S2, S3, S4, S6 |
| 5 | **Punch Construct + 2 Cubex Constructs** (`ConstructMenagerieNormal`, 55 + 65 + 65) — gallery `:61` (Punch) and `:62` (Cubex) | **2 rigs.** `punch_construct`: skeleton 169 125 B, atlas `1307×207` / **44 regions**, texture 182 030 B, scene 1 244 B (bare contract, scale 0.32). `cubex_construct`: skeleton 68 259 B, atlas `396×703` / **29 regions**, texture 145 796 B, scene **5 608 B**, scale 0.33. | Punch: **6 clips** — `idle_loop`, `block`, `attack`, `attack_double`, `hurt`, `die`, with `Cast`→`block` and a non-standard `DoubleAttack` trigger (`PunchConstruct.cs:121-139`). Cubex: **11 clips** — `burrow`, `burrowed_loop`, `unburrow`, `charge_start`, `charge_loop`, `attack_loop`, `attack_finish`, `idle_loop`, `hurt`, `hurt_idling`, `die`. Its animator also declares **three `BoundsContainer`s** (`BurrowedBounds`, `ChargingBounds`, `IdleBounds`) and **two conditional `Hit` branches** keyed on `IsBurrowed` / `IsCharging` (`CubexConstruct.cs:163-197`); the visuals scene carries the matching named `Control` groups. So the Cubex's hitbox and its hurt animation both change with its body state. | **Two art bodies — and both are shared with Act 1.** `ConstructMenagerieNormal` is listed **only** in Glory's encounter set (`Glory.cs:72`), but the same two bodies headline Act-1 solo encounters: `PunchConstructNormal` in Underdocks (`Underdocks.cs:79`) and `CubexConstructNormal` in Overgrowth (`Overgrowth.cs:78`); Punch Construct additionally appears in the Underdocks `PunchOffEventEncounter` (`punch-construct.md:8-11`). **A reskin of either body repaints Act 1 as well as Act 3.** | Punch: nothing bespoke — no particles, no attach points, no Spine events; hit VFX `vfx_attack_blunt` (`:106`); `TakeDamageSfxType.Armor` (`:43`). Cubex: **bespoke.** `NCubexConstructVfx` + a `SpineBoneNode` on bone **`laser_attach`**, a `MeshInstance2D` sphere driven by `shaders/vfx/2d_sphere_shader.tres`, ring texture `cubex_blast_rings.png`, and the shared `pck:scenes/vfx/laser_vfx.tscn`. Emitters are driven by **named Spine events `laser_start` / `laser_end`** (`NCubexConstructVfx.cs:98-111`). Cubex also carries a **skin obligation**: `SetupSkins` composes one skin from **3 eye options (`diamondeye`/`circleeye`/`squareeye`) × 3 moss options (`moss1`/`moss2`/`moss3`)** picked at random per body (`CubexConstruct.cs:20-22`, `:77-84`) — nine visible combinations. Hit VFX `vfx_attack_blunt` with an explicit `blunt_attack.mp3` (`:143`, `:157`); `TakeDamageSfxType.Stone` (`:49`). | **L** — two rigs, a bespoke event-driven `N…Vfx` node, a skin obligation, three bounds containers, and cross-act blast radius. The heaviest normal-encounter row in Act 3. | SHIPPED. Gallery: Punch **2 S + 4 P**, Cubex **2 S + 5 P**. Both rows carry the same note — *"gang coherence beats per-body fit"* — and §5 names `construct_gang` as one of three encounters needing a **family-coherent multi-body pick**. Not on the redesign-pressure list. | S1, S2, S3, S5, S6 |
| 6 | **Fabricator (+ bots)** (`FabricatorNormal`, Fabricator 150 HP + up to four 16–24 HP bots) — gallery `:63` | **5 rigs.** `fabricator` skeleton 144 732 B, atlas `2029×221` / **45 regions**, texture 196 192 B, scene 1 231 B (bare contract, scale 0.13). Bots, all tiny: `zapbot` 85 898 B / `204×269` / 15 regions; `stabbot` 21 687 B / `356×144` / 9; `noisebot` 22 541 B / `263×254` / 9; `guardbot` 21 557 B / `426×517` / 11. Bot scenes 1 524–1 732 B. | Fabricator: **driven set is 6** — `idle_loop`, `cast`, `attack`, `hurt`, `die` plus **`fabricate`** on its own trigger, with `Hit` wired as per-state branches rather than an any-state (`Fabricator.cs:120-140`). The rig additionally contains **four `arm_*_path_const` clips** (`arm_bl/br/fl/fr_path_const`) that nothing in the class names — path-constraint clips, an authoring layer. Bots: **5 clips each** — `appear`, `attack` or `cast`, `hurt`, `die`, `idle_loop`; none of the four bot classes overrides `GenerateAnimator`, so they inherit the default set and `appear` is undriven by their own classes (see §7). Tells needed: a summon beat that drops a new body mid-move with a fall-in (`fabricator.md:93`), an attack that also summons, a plain attack, and four distinct bot behaviours (zap / stab+Frail / block-the-parent / Dazed-injection). | **Five art bodies, one encounter.** `FabricatorNormal` declares five named slots `bot1, bot2, fabricator, bot3, bot4` and only places the Fabricator at start (`FabricatorNormal.cs:19`, `:45-47`); `HasScene = true`, room scene `pck:scenes/encounters/fabricator_normal.tscn` (607 B, five markers). The encounter also overrides **camera scaling 0.85 and offset +60 y** (`:51-59`). None of the five rigs is reused anywhere else. | **A named-bone contract on every bot.** Each bot scene exposes two `SpineBoneNode`s — `HeightControl` on bone **`height_constrainer`** and `FallControl` on bone **`height_bone`** — and `FabricatorNormal::SetBotFallPosition` writes `Visuals/FallControl`'s position directly (`FabricatorNormal.cs:61-69`, called from each bot's `AfterAddedToRoom` — `Zapbot.cs:29-37`, `Stabbot.cs:35`, `Noisebot.cs:37`, `Guardbot.cs:33`). Zapbot additionally exposes bone **`laser_attach`**. **No bespoke `N…Vfx` node anywhere in this row**; hit VFX `vfx/vfx_attack_slash`. Audio: Fabricator overrides `HurtSfx` explicitly (`:39`); all four bots are `TakeDamageSfxType.Armor`. | **L** — five rigs, and every bot rig must expose two exactly-named bones or the fall-in silently misplaces. Per body each rig is an S; the count is the cost. | SHIPPED. Gallery: **4 candidates rated S, 3 plausible**; row note calls the meka **Guardbot** match "the single most exact minion pairing in the atlas". Not on the redesign-pressure list. | S1, S2, S3, S4 |
| 7 | **Frog Knight** (`FrogKnightNormal`, solo, 191 HP) — gallery `:64` | **1 rig, but a composite body.** Skeleton **289 454 B** — the largest Act-3 normal — atlas `332×922` with **59 regions**, the most of any Act-3 normal; texture 141 518 B; scene 1 177 B (bare contract, scale 0.15). **Over half the regions are the mount, not the rider**: 29 carry the `beetle_` prefix — `beetle_head`, `beetle_chest`, `beetle_carapace 1/2/back`, six legs × three parts each, `beetle_top joint 1–3`, `beetle_leg_hole_1/2`, `beetle_saddle strap` — plus `saddle`, `reigns`, `reigns_back`. The rider adds `head`, `head bottom`, `neck armor`, `neck backing`, arms/elbows/hands, `cloth`, `trident`, `tongue`, `spit drop`, `eye`/`side eye`/`pupil`/`closed_eye`. A like-for-like reskin therefore has to design **two silhouettes that fit together**, not one. | **9 clips in the rig, 7 driven**: `idle_loop`, `buff`, `attack`, `attack_tongue`, `charge`, `hurt`, `die`, with non-standard triggers `Buff`, `Lash`→`attack_tongue`, `charge` (`FrogKnight.cs:123-149`). **Undriven rig content:** `charge_end` and `charge_stat` are present in the skeleton and named by nothing in the class. Tells needed: Tongue Lash (hit + Frail), Strike Down Evil (heavy hit), For the Queen (+5 Str, no cap), Beetle Charge (once per fight, fires on a half-HP branch polled only every third turn — `frog-knight.md`). Plus a spawn-time **Plating 15** counter the player must read. | **One body, solo, fixed HP, no adds, no variants** (`E_FrogKnightNormal.cs:15`). Rig used nowhere else. | Nothing bespoke: no `N…Vfx` node, no attach bones or slots, no Spine events, no encounter scene. Hit VFX `vfx/vfx_attack_blunt` (`:100`) and `vfx/vfx_attack_slash` (`:118`). Audio fully id-derived; `TakeDamageSfxType.Armor` (`:58`) — the dossier records hits reading as armoured, consistent with Plating (`frog-knight.md:84`). | **M** — it misses **S** only on clip count (9 present / 7 driven) and on the composite rider-plus-mount body. It has none of the M/L triggers: no second rig, no attach contract, no Spine events, no skin obligation. Flagged here because the scale has no clip-count-only tier. | SHIPPED. Gallery: **3 candidates rated S, 6 plausible**; row note: "Armored-devotee charger; three clean strongs from three factions." **Carries the gallery's §4 unimplemented-mechanic warning** — the sim skips the Plating damage **cap** (`tier05/content/act3_pool.yaml:119`), so art must not promise a cap that is not there. | S1, S2, S3 |
| 8 | **Globe Head** (`GlobeHeadNormal`, solo, 148 HP) — gallery `:65` | **1 rig.** Skeleton 190 895 B, atlas `1476×205` / **52 regions**, texture 171 864 B. Scene 1 256 B — the bare contract **plus one extra `%OrbPos` marker**, which `NCreatureVisuals` reads and falls back to `%IntentPos` for when absent (`NCreatureVisuals.cs:224`). Root node is named `OrbHead`. | **19 clips in the rig, 5 driven.** `GlobeHead` does **not** override `GenerateAnimator`, so the driven set is the default `idle_loop`/`cast`/`attack`/`hurt`/`die`. The other **14 are an apron/cloth system** — `apron_l2`…`apron_l7`, `apron_r2`…`apron_r8`, `apron_middleweight` — named by nothing in the class. Tells needed: Shocking Slap (hit + Frail), Thunder Strike (3 separate hits), Galvanic Burst (hit + permanent +2 Str, and the dossier records this third beat as deliberately hidden from the bestiary — `globe-head.md`). | **One body, solo, no variants, no adds** (`E_GlobeHeadNormal.cs:18`). Rig used nowhere else. | No bespoke `N…Vfx` node, no attach bones/slots, no Spine events. Hit VFX `vfx/vfx_attack_lightning` (`:68`) and `vfx/vfx_attack_blunt` (`:76`). Audio fully id-derived; `TakeDamageSfxType.Armor` (`:39`). The **encounter preloads the Galvanized card-affliction overlay art** (`globe-head.md:8`) — a card-surface asset, not a creature asset. | **S** — one rig, the default five driven clips, shared hit VFX, nothing bespoke. **Surcharge flagged, not graded:** the 14-clip apron system is real authoring work the code never names, so a like-for-like rig is heavier than the S letter suggests. | SHIPPED. Gallery calls this the **"second-most-contested row"** — **9 candidates, most rated S** — and says it "can be assigned last". **Gallery §3 records the Globe Head silhouette as NOT RESOLVED** (`reskin-gallery.md:120`) and asks for someone to look at the sprite. §7 of this file offers the base-asset description that flag was waiting on. | S1, S2, S3 |
| 9 | **Slimed Berserker** (`SlimedBerserkerNormal`, solo, 266 HP) — gallery `:67` | **1 rig.** Skeleton **283 477 B** (second-largest Act-3 normal), atlas `2033×459` / **55 regions**, texture **493 324 B** — the heaviest Act-3-normal texture. Scene 6 636 B, scale 0.15. | **6 clips**: `idle_loop`, `attack`, `hug`, `vomit`, `hurt`, `die`, with non-standard triggers `Hug` and `Vomit` (`SlimedBerserker.cs:97-115`). Tells needed: Vomit Ichor (the deck-pollution beat — injects 10 `Slimed` cards), Furious Pummeling (4 hits under one animation, `:82-86`), Leeching Hug (Weak + self-Str), Smother (one big hit). | **One body, solo, no variants, no adds** (`E_SlimedBerserkerNormal.cs:15`). Rig used nowhere else. | **Bespoke.** `NSlimedBerserkerVfx` plus **three `SpineSlotNode`s bound to slots `goo_emitter_l`, `goo_emitter_r`, `vomit_emitter`**, each carrying a `GPUParticles2D`, over three bespoke drop textures. Emitters are driven by **four named Spine events**: `goo_start`, `goo_stop`, `vomit_start`, `vomit_stop` (`NSlimedBerserkerVfx.cs:105-121`). **Neither attack uses a hit-VFX scene at all** (`:82-94`) — the goo emitters *are* the impact feedback, which is unusual for the roster. Audio: `CastSfx` overridden to `…/slimed_berserker/slimed_berserker_buff` (`:41`); `TakeDamageSfxType.Slime` (`:37`). | **L** — bespoke `N…Vfx` node driven by named Spine events, on three named slots. | SHIPPED. Gallery: **2 candidates rated S** ("two name-level strongs"), 1 plausible, 1 stretch; row note splits the discriminator — "slime wins the Vomit Ichor beat, lawachurl wins the Berserker beat". Not on the redesign-pressure list. | S1, S2, S3, S6 |
| 10 | **Owl Magistrate** (`OwlMagistrateNormal`, solo, 234 HP) — gallery `:66`. **DROPPED in the sim** (`tier05/content/act3_pool.yaml:11-12`), live in the base game | **1 rig, 2 atlas pages.** Skeleton 233 291 B, pages `2020×539` (441 862 B) + a second page (368 960 B), **34 regions**. Scene 2 134 B, scale 0.13, carrying **two named bounds groups `IdleBounds` and `FlyingBounds`**. | **9 clips, all driven** — and this is the only Act-3 normal with a **hand-wired per-state graph rather than any-state triggers**: `idle_loop`, `attack_peck`, `hurt`, `die` on the ground; `take_off`, `fly_loop` (looping, `BoundsContainer = "FlyingBounds"`), `attack_dive` (`BoundsContainer = "IdleBounds"`), `hurt_flying`, `die_flying` in the air, with explicit branches between every pair (`OwlMagistrate.cs:150-190`). **The airborne state is a second complete body state**: its own hurt, its own death, its own hitbox, and its own `HurtSfx` / `DeathSfx` overrides (`:47`, `:59`). The dossier records the visual state as a reliable read on whether Soar is up, independent of the power icon (`owl-magistrate.md:74`). | **One art body, two body states, solo** (`E_OwlMagistrateNormal.cs:15`). Rig used nowhere else. | No bespoke `N…Vfx` node, no attach bones/slots, no Spine events, no encounter scene. Hit VFX `vfx/vfx_gaze` (`:114`) and `vfx/vfx_attack_slash` (`:124`). Audio: state-dependent `HurtSfx` and `DeathSfx` overrides; `TakeDamageSfxType.Armor` (`:45`). | **M** — an S body plus exactly one extra, but the extra is unusually heavy: a second full body state with its own hurt/death clips and its own bounds container. The heaviest **M** in Act 3. | DROPPED (re-add list — Soar/untargetable is a skipped op). Gallery: **3 candidates rated S**, 1 plausible, 1 stretch; row note: "Ngoubou's published loop is the base intent cycle nearly verbatim." §5 flags **Consecrated Red Vulture** as double-booked between this row and Byrdonis (Act 1). | S1, S2, S3 |
| 11 | **The Lost + The Forgotten** (`TheLostAndForgottenNormal`, 93 + 106 HP) — gallery `:68`. **DROPPED in the sim** (`act3_pool.yaml:11-12`), live in the base game | **2 rigs, and they share art.** `the_lost`: skeleton 56 756 B, pages `890×308` + `93×264`, **13 regions**, scene 3 889 B, scale 0.3. `the_forgotten`: skeleton 62 678 B, pages `715×529` + `93×264`, **14 regions**, scene 3 811 B, scale 0.3. The two second pages are **byte-identical** — both imported `.ctex` are 7 884 B with md5 `116f9bf2047b…` — i.e. one shared VFX page across the twins. | **5 clips each, identical names**: `idle_loop`, `debuff`, `attack`, `hurt`, `die`, with `Cast`→`debuff` on both (`TheLost.cs:65-80`, `TheForgotten.cs:71-86`). Tells needed: one stat-theft cast per body (Strength on The Lost, Dexterity on The Forgotten) and one attack each. | **Two art bodies, always as a fixed pair, never alone, never with anything else** (`E_TheLostAndForgottenNormal.cs:21-22`; `the-forgotten.md:8`). Neither rig is reused. | **Bespoke, and shared between the two bodies.** Both scenes embed the **same** driver `NLostAndForgottenVfx` and both expose **four named slots** — `dustPosition`, `smoke mesh`, `smoke mesh2`, `smoke mesh3` — over the shared granule texture and the `lost_smoke_*` materials. Emitters are driven by **named Spine events `start_dust` / `stop_dust`** (`NLostAndForgottenVfx.cs:83-97`). Hit VFX `vfx/vfx_attack_blunt` on both. Audio: both `TakeDamageSfxType.Stone` (`TheLost.cs:29`, `TheForgotten.cs:35`) — the dossier calls the family "stone" (`the-lost.md:19`). | **L** — two rigs **and** a bespoke `N…Vfx` node driven by named Spine events. Partly amortised: one driver, one shared atlas page, one clip set covering both. | DROPPED (re-add list — stat-theft op is backlogged). Gallery: **3 candidates rated S**, 1 plausible, 2 stretch; row note: "one silhouette in two colorways is the paired-encounter grammar" — which the shared second atlas page above independently corroborates. Not on the redesign-pressure list. | S1, S2, S3, S6 |

---

## 3. The complexity scale used above

Identical to `s18-act1.md` §3, so the two act files join. Deliberately coarse,
and defined only by what the shipped assets require:

- **S** — one Spine rig; ≤6 clips; hit VFX drawn from the shared
  `res://scenes/vfx/vfx_attack_{slash,blunt,lightning}.tscn` /
  `vfx_bite.tscn` / `vfx_gaze.tscn` set; no bespoke particle nodes; no named
  Spine attach bones/slots; no named Spine animation events; no skin
  obligation.
- **M** — an S body plus exactly one of: a second rig, a named attach
  bone/slot, an encounter scene with named body slots, or a skin obligation.
- **L** — several rigs, **or** a bespoke `N…Vfx` script node whose emitters are
  driven by named Spine animation events, **or** a skin obligation on top of a
  multi-body row.

**Act 3 normals split 1 S / 4 M / 6 L.** The distribution is the opposite of
Act 1's (3 S / 0 M / 3 L): Act 3 has almost no cheap bodies. The six L rows are
L for four different reasons — an event-driven VFX driver on a single body
(Devoted Sculptor, Slimed Berserker), a driver *plus* a slot/bone contract
(Axebot), two rigs plus a driver (Lost + Forgotten), two rigs plus a driver
plus a skin obligation plus cross-act reuse (construct gang), and sheer body
count with a named-bone contract per body (Fabricator). They do not collapse
into one batch.

Two things the letters do **not** capture, recorded so the integrator can carry
them:

- **Undriven rig content.** Five Act-3 bodies ship clips no code names: Globe
  Head's 14 apron clips, the Fabricator's 4 `arm_*_path_const` clips, Frog
  Knight's `charge_end` / `charge_stat`, Living Shield's `barricade_loop` /
  `barricade_hurt`, and the four bots' `appear`. A like-for-like rig is heavier
  than its letter; a minimum-viable rig can skip these and the engine will only
  warn (§0 fact 2).
- **Cross-act blast radius.** Only one Act-3 normal-encounter row shares its
  bodies with another act: the construct gang (row 5).

---

## 4. Act 3 elites and bosses — **owned by the boss/elite integrator**

One-line pointers, not rows. Rig figures given only so the integrator does not
have to re-derive them.

| Gallery row | Class(es) | Rig(s) | Pointer |
|---|---|---|---|
| Knight Gang (elite, `:69`) | `KnightsElite` → `FlailKnight` + `SpectralKnight` + `MagiKnight` | **3 rigs.** flail: skel 141 092 B / atlas `1658×523` / 48 regions; clips `idle_loop, attack_ram, attack_flail, attack_breaker, buff, hurt, die`. spectral: skel 140 599 B / `994×532` / 27; clips `idle_loop, attack_sword, attack_flame, debuff, hurt, die`; bespoke `NSpectralKnightVfx` + head-fire `TextureRect` + 3 particle systems. magi: skel 157 969 B / `1313×252` / 21; clips `idle_loop, attack_ram, attack_bomb, cast_shield, hurt, die`; shared `little_light_script.gd` fire nodes. Room scene `knights_elite.tscn` (451 B, markers `first`/`second`/`third`). | Integrator. **Costing note: this is three separate rigs plus one bespoke VFX driver** — the most expensive single row in Act 3 by body count. Gallery `:69` records **4 candidates rated S**. The sim ships the gang **aura-less** (`act3_pool.yaml:161-162`), so the gallery's aura arguments are future-proofing, not current fit. |
| Mecha Knight (elite, `:70`) | `MechaKnightElite` → `MechaKnight` | **2 rigs for one body.** Main: skel 141 384 B / atlas `1270×523` / **63 regions** (most of any Act-3 body); clips `idle_loop, idle_loop_wound, attack_cleave, attack_flame, charge, wind_up, hurt, hurt_wound, die` — note the **paired wound variants of idle and hurt**, a damaged-state art obligation. Second rig purely for the shield VFX: `pck:animations/vfx/vfx_mecha_knight_shield/*` (skel 22 167 B). Scene **19 285 B** with `NMechaKnightVfx` + 6 particle emitters on engine/flame bones. | Integrator. Gallery `:70` calls this the "deepest strong bench in the atlas" — **5 candidates rated S**. Gallery §4 flags Artifact 3 as UNIMPLEMENTED (`act3_pool.yaml:187`). |
| Soul Nexus (elite, `:71`) | `SoulNexusElite` → `SoulNexus` | **1 rig.** skel 245 709 B / atlas `1063×656` / 29 regions / texture 334 332 B. **Only the default 5 clips** (`idle_loop, attack, cast, hurt, die`) — the cheapest animator in the Act-3 elite/boss set. Scene 7 031 B: `NSoulNexusVfx` + three `Line2D` trails on Spine slots + a head-fire `TextureRect` on a stepped fire shader. | Integrator. Gallery `:71`: "Gimmick-free stat block: donor body is a free pick." **The cheapest Act-3 elite to reskin on animation grounds; the cost is entirely in the fire/trail VFX.** |
| Test Subject (boss, `:72`) | `TestSubjectBoss` → `TestSubject` | **3 rigs.** Main skeleton **1 161 899 B — by far the largest in the game's monster set**, atlas `1985×491` / **81 regions**, texture 513 460 B; **23 clips** covering three numbered phase variants (`idle_loop1/2/3`, `hurt1/2/3`, `attack_big1/2/3`, `attack_double1/2/3`, `heal1/2/3`, `knockout1/2`, `knocked_out_loop1/2`, `regenerate1/2`, `burn`, `die`). Plus two dedicated burn-VFX Spine rigs (`test_subject_burn_vfx_front/back`). Scene **139 319 B** with `NTestSubjectVfx`, a `CanvasGroup`, 9 particle systems, and `RespawnBounds1`/`RespawnBounds2` bounds groups. | Integrator. **This is the largest single art contract in Act 3 by an order of magnitude** — three phase bodies in one skeleton. Gallery `:72` lists 1 S + 2 P + 1 X and records a factual correction on the Prism Slime candidate (§3, `:113`). |
| Aeonglass (boss, `:73`) | `AeonglassBoss` → `Aeonglass` | **No Spine rig exists.** There is **no `animations/monsters/aeonglass/` entry anywhere in the 15 658-entry pack index**. `pck:scenes/creature_visuals/aeonglass.tscn` (1 134 B) has a root `Node2D` named **`Doormaker`** and a `%Visuals` that is a plain **`Sprite2D`** on `pck:images/monsters/hourglass_placeholder.png`. | Integrator — **and read this one first.** The shipped v0.107.1 build gives this boss a static placeholder body, which is legal (§0 fact 3: the Spine path is gated on `GetClass() == "SpineSprite"`). Consequence: there is **no base animation set to reskin against** for the Act-3 boss the gallery calls its "strongest single boss argument" (`:73`). This is a fact about the build we pin, not a claim about MegaCrit's plans. |
| Queen + Torch Head Amalgam (boss, `:74`) | `QueenBoss` → `Queen` + `TorchHeadAmalgam` | **2 rigs.** queen: skel 298 083 B / atlas `2033×515` / 41 regions / texture 310 510 B; **only the default 5 clips**; scene 9 540 B with `NQueenVfx`, two eye-fire `ColorRect` shaders on Spine slots, and eye bones. amalgam: skel 145 207 B / `1459×240` / 44 regions; 6 clips (`idle_loop, attack, buff, debuff, hurt, die`); scene **64 486 B** — three torch slots × five nodes each, laser base/hit bones, three per-torch hit emitters, `NAmalgamVfx`. Room scene `queen_boss.tscn` (373 B, markers `amalgam`/`queen`). | Integrator. **DROPPED in the sim** (`act3_pool.yaml:12-13`). **Gallery §1 redesign-pressure: zero candidates across all 16 families** (`reskin-gallery.md:94`). Worth pairing that flag with the 64 KB amalgam scene: it is simultaneously the least-covered and one of the most VFX-dense bodies in Act 3. |

---

## 5. Coverage: every mapped Act 3 encounter is accounted for

`Glory::GenerateAllEncounters` returns a fixed array of **18 encounters**
(`Glory.cs:69-89`), and `NumberOfWeakEncounters => 2` (`:41`). All 18 are
mapped by the gallery's Act 3 block (`reskin-gallery.md:56-74`). Nothing in
Act 3 is excluded for lack of a mapping.

| Base encounter (`Glory.cs`) | Where it lands |
|---|---|
| `DevotedSculptorWeak` | §2 row 1 |
| `ScrollsOfBitingWeak` (3 bodies) + `ScrollsOfBitingNormal` (4 bodies) | §2 row 2 — the gallery covers both under one row ("×3–4") |
| `TurretOperatorWeak` | §2 row 3 |
| `AxebotsNormal` | §2 row 4 |
| `ConstructMenagerieNormal` | §2 row 5 — the gallery splits it into two rows (`:61` Punch, `:62` Cubex); joined here because it is one encounter |
| `FabricatorNormal` | §2 row 6 |
| `FrogKnightNormal` | §2 row 7 |
| `GlobeHeadNormal` | §2 row 8 |
| `SlimedBerserkerNormal` | §2 row 9 |
| `OwlMagistrateNormal` | §2 row 10 (dropped in the sim, mapped by the gallery) |
| `TheLostAndForgottenNormal` | §2 row 11 (dropped in the sim, mapped by the gallery) |
| `KnightsElite`, `MechaKnightElite`, `SoulNexusElite` | §4 — integrator |
| `TestSubjectBoss`, `AeonglassBoss`, `QueenBoss` | §4 — integrator |

**No exclusions.** 3 weak + 9 normal + 3 elite + 3 boss = 18.

### 5a. Where the shipped sim model and the base encounter differ

Not defects — the sim's job is comparability, and every skip in the file is
flagged there. Listed only because a reader costing art from the sim alone
would under- or mis-count.

| Row | Shipped sim (`tier05/content/act3_pool.yaml`) | Base game | Consequence for art |
|---|---|---|---|
| Scrolls of Biting | one encounter, **3 copies**, in the *easy* pool (`:30-42`) | **two** encounters — `ScrollsOfBitingWeak` (3) *and* `ScrollsOfBitingNormal` (4) (`Glory.cs:82-83`) | None for art (same rig, same skins). But the 4-copy encounter is neither modelled nor named on the file's dropped list (`:10-13`), so an encounter-count read off the sim is one short. |
| Fabricator | keeps **only** Zapbot and Stabbot; Guardbot and the Noisebot Dazed minion are explicitly skipped (`:100-102`) | **four** bot bodies, two defensive and two aggro (`fabricator.md:64-72`) | The art bill for this row is **five rigs, not three**. A sim-only read understates it by two bodies. |
| Axebot | "UNIMPLEMENTED: 2 Stock" (`:64`) | Stock 2 → the body dies and is replaced twice in the same slot, with a `respawn` clip (`axebot.md:70`) | The sim never shows the respawn; the rig has a clip for it and the fight is three sequential bodies. |
| Construct gang | placed in Act 3's HARD pool (`:76`), "UNIMPLEMENTED: Artifact 1" (`:78`) | Placement agrees — `ConstructMenagerieNormal` is Act 3 only (`Glory.cs:72`) — **but both bodies also headline Act-1 solo encounters** (`Underdocks.cs:79`, `Overgrowth.cs:78`) | A reskin of Punch or Cubex repaints Act 1 as well. The dossiers' "Act: Act 1" fields (`punch-construct.md:7`, `cubex-construct.md:7`) name the body's *home* act, not this encounter's — the two are not in conflict. |
| Living Shield | Rampart 25 modelled as the Shield's own opening **block beat**, "one enemy-turn late versus the real power, accepted" (`:45-46`) | A counter that pumps Block onto every living **`TurretOperator`** at each *player* turn start, filtered by monster type, never onto itself (`LivingShield.cs:32-36`; `living-shield.md`) | The visual read is "this body shields *that* body", not "this body blocks". Art that makes the Living Shield look self-protective teaches the wrong rule. |
| Frog Knight | "UNIMPLEMENTED: Plating 15 (damage cap)" (`:119`) | Real `PlatingPower` counter | Matches the gallery's §4 art-unsafe warning verbatim. |
| Globe Head | "UNIMPLEMENTED: Galvanic 6" (`:132`) | The encounter **preloads a Galvanized card-affliction overlay** (`globe-head.md:8`) | The fight's identity is a *card* surface the sim has no equivalent for; a reskin's tax lands on card art, not creature art. |
| Knight Gang | ships **aura-less**; Hex, the Ethereal aura and the Downgrade aura all skipped (`:161-162`) | Three auras, each tied to one knight's life | Gallery `:69` already says the aura arguments are future-proofing. |
| Owl Magistrate · The Lost + The Forgotten · Queen | on the dropped/re-add list (`:10-13`) | Live encounters in `Glory.cs:80`, `:87`, `:81` | Their rigs exist and are costed above (§2 rows 10–11, §4). |

---

## 6. Socket questions — **PROVISIONAL, S13 pending**

Same key space as `s18-act1.md` §6, restated so this file reads cold. **None of
these is answered here.** The "known locally" column is context, not an answer.

| Key | Question | What is known locally (not an answer) |
|---|---|---|
| **S1** | Can a mod register a **hostile** `MonsterModel` + `EncounterModel` and get it drawn into an act's pool? | `Glory::GenerateAllEncounters` returns a **fixed 18-element array** (`Glory.cs:69-89`), and `NumberOfWeakEncounters` is a `protected override int` (`:41`). `klee-mod` contains no `MonsterModel` or `EncounterModel` reference — no local precedent. Applies to **every row**. |
| **S2** | Can a mod ship its own `creature_visuals` scene + Spine rig and have the engine resolve it? | `MonsterModel::VisualsPath` is `protected virtual` (`MonsterModel.cs:216`) and failure is caught and swapped for `creature_visuals/fallback` (`:421-437`). The four-node contract is small (`NCreatureVisuals.cs:219-225`). **Act-3-specific extension:** three rows need `AnimState.BoundsContainer` to resolve *named `Control` children* of the visuals scene — Cubex (`BurrowedBounds`/`ChargingBounds`/`IdleBounds`), Owl Magistrate (`IdleBounds`/`FlyingBounds`), Test Subject (`RespawnBounds1/2`). Whether a mod-PCK scene satisfies that lookup is UNKNOWN. Applies to **every row**. |
| **S3** | Can a mod supply the **FMOD** events the id-derived SFX paths demand? | Paths are computed from the monster id (`MonsterModel.cs:292-296`) and resolve out of `res://banks/desktop/*.bank`. `Master.strings.bank` (31 078 B) contains **no plaintext `event:/` strings** — the string table is not readable, so even the base game's own event inventory could not be enumerated here. No local precedent for adding a bank. **The least-explored socket, and it touches every row.** |
| **S4** | Can a mod ship an **encounter** scene with named body slots (`HasScene = true`) and camera overrides? | Needed by rows 4 and 6 (`E_AxebotsNormal.cs:11-13`; `FabricatorNormal.cs:19`, `:51-59`). Base scenes are tiny (294 B / 607 B) and contain only `Marker2D`s. Reachability from a mod PCK is UNKNOWN. |
| **S5** | Can a mod ship **multi-skin** Spine data and drive `MegaSprite::NewSkin` / `FindSkin` at spawn? | Act 3's instances are **randomised composed skins**, not Act 1's phobia toggle: `ScrollOfBiting::SetupSkins` picks between `skin1`/`skin2` (`ScrollOfBiting.cs:64-71`), `CubexConstruct::SetupSkins` composes an eye skin × a moss skin from two 3-element sets (`CubexConstruct.cs:77-84`). `SetupSkins` is `public virtual` on `MonsterModel` (`:598`) and is called from `NCreatureVisuals` (`:273`). **No Act 3 body has a phobia-skin obligation** (`HasPhobiaSpineSkin` is nowhere overridden in the Act-3 set) — that half of S5 is an Act 1 concern only. |
| **S6** | Can a mod attach a **custom script node** inside a creature-visuals scene and receive Spine animation events? | **Five Act-3 rows depend on this** (Devoted Sculptor, Axebot, Cubex, Slimed Berserker, Lost + Forgotten). All five drivers call `ConnectAnimationEvent` and switch on `MegaEvent…GetEventName()` (`NAxebotVfx.cs:116`/`:129-147`; `NCubexConstructVfx.cs:90`/`:98-111`; `NDevotedSculptorVfx.cs:80`/`:89-101`; `NSlimedBerserkerVfx.cs:97`/`:105-121`; `NLostAndForgottenVfx.cs:74`/`:83-97`). Whether a mod-supplied C# node type can be referenced from a mod-PCK scene is UNKNOWN. |

**Socket load by row, provisional:** every row needs S1–S3. Rows 4 and 6 add
S4. Rows 2 and 5 add S5. Rows 1, 4, 5, 9 and 11 add S6. **Row 5 (the construct
gang) is the only Act-3 normal that touches five of the six.**

---

## 7. UNKNOWN and NON-FINDING

- **NON-FINDING — no local enemy-modding precedent.** `klee-mod` ships player
  characters, cards, relics and a PCK. Nothing in this repo proves an enemy can
  be added or reskinned. Every socket cell above is provisional for that
  reason, independent of S13.
- **UNKNOWN — exact Spine clip lists.** The clip names in §2 come from an
  **ASCII length-prefixed-string scan** of the imported `.spskel` binaries,
  taking the last strictly-alphabetically-increasing run of lowercase
  identifiers, **not** from a Spine format parser. **Cross-check:** every clip
  id that a monster class *declares* via `new AnimState("…")` was found by the
  scan, for all 18 Act-3 bodies examined — so the *driven* clip lists are
  corroborated twice and are safe. The **undriven extras rest on the scan
  alone** and are UNVERIFIED: Globe Head's `apron_*` (14), the Fabricator's
  `arm_*_path_const` (4), Frog Knight's `charge_end` / `charge_stat`, Living
  Shield's `barricade_loop` / `barricade_hurt`, the four bots' `appear`.
- **UNVERIFIED — `charge_stat` (Frog Knight).** Read verbatim as an 11-character
  string (length prefix `0x0c` at offset 185 577 of the imported `.spskel`). It
  looks like a truncated `charge_start`, but the length byte says 11, not 12.
  Recorded as read; **do not** repeat it as `charge_start`.
- **UNKNOWN — where `appear` is driven.** All four Fabricator bots ship an
  `appear` clip, none of the four classes declares an `AnimState("appear")`,
  and no `SetTrigger("appear")` was found in the classes examined
  (`Fabricator.cs`, the four bot classes, `CreatureCmd.cs`). It may be driven
  from the creature-spawn path, or it may be dead. Not chased further.
- **NON-FINDING — purpose of the undriven Living Shield and Frog Knight clips.**
  `barricade_loop` / `barricade_hurt` and `charge_end` / `charge_stat` exist in
  their rigs and are named by nothing in their model classes. No claim is made
  about why.
- **UNKNOWN — audio content.** FMOD bank contents were not opened and could not
  be: `pck:banks/desktop/Master.strings.bank` yields no plaintext event paths.
  Only the event **paths the code computes** are reported. Whether an event
  exists behind any given path was verified for no body.
- **UNKNOWN — rig internals.** Bone counts, attachment counts, clip durations,
  mesh-vs-bone deformation ratio, and draw-call cost were **not** measured.
  Skeleton byte size and atlas region count are used as coarse proxies only.
  **S16 owns the animation corpus and is authoritative over this file on rig
  internals.**
- **UNKNOWN — runtime cost.** No game was launched, so nothing here is a
  performance claim.
- **Note on the packed C# sources.** `SlayTheSpire2.pck` contains 3 324
  `src/**/*.cs` entries, but each is a **1-byte stub** — source is stripped at
  export. The pack therefore proves *file and class names* only; **every code
  fact in this file comes from the `sts2.dll` decompile.**
- **Partial answer available for a gallery flag — Globe Head silhouette.**
  `reskin-gallery.md:120` records the Globe Head body as **NOT RESOLVED** and
  asks for someone to look at the sprite. The rig's own atlas region list
  (`pck:.godot/imported/globe_head.atlas-*.spatlas`, 52 regions) describes it
  without opening an image: **an aproned humanoid biped** — `apron`,
  `apron bottom`, `l boot`, `r boot`, `l sleeve inside`, `r sleeve inside`,
  two arms (`l arm top`, `l arm bottom`, `r arm upper`, `r arm lower`, `r arm highlight`, `l hand`, `r hand`) with
  **individually rigged fingers** (`l index`, `l middle`, `l ring`, `l pinky`,
  `l thumb`; `r index`, `r middle`, `r ring`, `r pinky`), a separate
  `slappy hand` (matching the move name *Shocking Slap*), `neck` and
  `neck highlights`, `bod` and `bod highlight`, `back tubes` — and, in place of
  a face, an **`orb` + `orb center`** head carrying `head zaps 0`,
  `head zap short`, `head zaps branched`, `lightning main1–4`,
  `lightning branch1–4`, `zap flash`, `zap glow`, plus `burn smudge 1–3` and
  `smoke`/`smoke 2/3/4`. **This is a description of the base asset, not a
  mapping verdict and not a re-ranking** of that row's nine candidates; the
  ordering call remains [USER]'s.
- **NOT ATTEMPTED — `SKIP-10.9`.** The dormant rows are cited only where the
  gallery or the sim file already cites them (Frog Knight's Plating cap, Globe
  Head's Galvanic, Axebot's Stock, the construct Artifact, the Knight Gang
  auras). No prototype, no promotion (charter §3.2 / R183).

---

## 8. What this does **not** establish

It does not choose or rank a Genshin body for any Act 3 encounter, does not
grade RESKIN vs REDESIGN (it only repeats what `reskin-gallery.md` already
recorded, including that row's own confidence codes), does not change any
existing ordering, does not prove any enemy can be added or reskinned in a mod,
does not answer a single socket question, does not measure runtime performance,
does not touch the shipped sim or any governing doc, and does not open a
balance window, stamp, or experiment. The complexity letters are an engineering
count of asset contracts, **not a schedule and not a cost in hours**. Whether
any of these encounters should be reskinned at all is [USER]'s call.
