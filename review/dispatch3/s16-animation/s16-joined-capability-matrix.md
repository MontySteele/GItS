# S16 — the joined capability matrix

> **This file decides nothing.** It is the integrator artifact for surplus-dispatch-3's
> S16 stream (charter §4/S16). It joins five research files that were written
> independently; it may select, dedupe, order and resolve contradictions between them,
> and it may **not** turn any of their candidates into verdicts or strengthen any of
> their claims. Every technical read is labelled `PROPOSED`. Taste, lore, art
> direction, rights, spend, scope and ship calls remain [USER]'s and are written below
> as numbered pick lists, never blanks. Nothing here opens a balance window, moves a
> stamp, mints an id, or interprets a playtest. **The game was never launched** —
> [USER] was playtesting mod `0.2-1155` throughout (PREFLIGHT).

*Filename note.* The schema's §4 ownership map calls the integrator file
`s16-05-matrix.md`; the dispatch assigned `s16-joined-capability-matrix.md`. Same
slot, same owner, one file. The public-mod sidecar the schema wanted "beside the
matrix" was written separately as `s16-sidecar-public-mods.md` and is joined here as a
source, not absorbed.

---

## 0. How to read this, and what the citation tags mean

### 0.1 Source key

Every cell in every table below carries at least one tag. All five source files live in
`review/dispatch3/s16-animation/`.

| tag | file | body / scope |
|---|---|---|
| `[schema]` | `s16-00-schema.md` | the shared evidence grammar |
| `[iron]` | `s16-body-base-simple-player-character.md` | Ironclad — `player-simple` |
| `[regent]` | `s16-body-base-complex-player-character.md` | Regent — `player-complex` |
| `[mawler]` | `s16-body-normal-enemy.md` | Mawler — `enemy-normal` |
| `[beast]` | `s16-body-elite-or-boss.md` | Ceremonial Beast — `elite-boss` |
| `[mods]` | `s16-sidecar-public-mods.md` | 11 pinned public repos incl. Downfall@`32e6113` |
| `[here]` | **read first-hand by this integrator, 2026-08-27** | always accompanied by an absolute-path `file:line`; see §0.3 |

Where a source file gave an underlying repo / decompile / pck pointer, that pointer is
carried through in the row-detail sections (§2) and the cross-cutting sections (§3) so
a reader can go to the primary evidence without re-opening the body file. Where a claim
is a string scan rather than a parse, the source file's own `UNVERIFIED` label travels
with it.

### 0.2 The rows are not mutually exclusive, and that is the first finding

The charter names four approaches — layered sprites, cutout/skeletal 2D, mesh
deformation, particles/tweens — as if a body picked one. **No shipped body in the
corpus picks one.** Every single one is a composite:

| body | skeletal | layered sprites | particles / tweens | shader-on-mesh |
|---|---|---|---|---|
| Ironclad | Spine, 1 `SpineSprite` | 0 `Sprite2D` | 0 emitters; **a tween drives the slash shader** | 1 `ShaderMaterial` in Spine slot `slash_mesh` |
| Regent | Spine ×3 (body + 2 weapons) | 0 `Sprite2D` | **6 GPU emitters**; a **tween** is the shipped revive | shared additive material only |
| Mawler | Spine, 1 | 0 | **0 of everything** | 0 |
| Ceremonial Beast | Spine, 1 | 0 | 2 CPU + 1 GPU; death **gated on a particle signal** | 0 |
| Downfall Hexaghost | **none** | 2 `Sprite2D` | 4 GPU emitters | 3 `MeshInstance2D` shader quads |
| Downfall Gremlins | none | none on the player body | **pure `Tween`, nothing else** | none |
| our `klee` | none | **5 `Sprite2D` layers** | 0 in the body (3 in separate VFX scenes) | none |

Sources: `[iron §C]`, `[regent §C]`, `[mawler §C]`, `[beast §C]`, `[mods §2, §2.1]`,
`[here]` — `klee-mod/pck-src/klee/model/combat.tscn` node census (14 nodes, 5
`Sprite2D`, 0 particles) and `klee-mod/pck-src/{klee,furina}/vfx/*.tscn` (3
`GPUParticles2D`, all outside the body).

So the matrix's rows are **capabilities a body can compose**, not products to choose
between. The decision-relevant question the corpus actually supports is narrower and is
stated in §5.

### 0.3 What this integrator verified first-hand, and why

Four things, all read-only, none of which the five source files could settle alone:

1. **A direct contradiction between two corpus files** about where a missing required
   `%` node throws (`[mawler §H]` vs `[beast §M.1]`). Settled in §3.1 by reading the
   decompile both cite.
2. **Our own rigs' transition table** — no source file reported it, and it is the
   sharpest available comparison to the base game's mix tables. §3.5.
3. **Our own rigs' animation track types** — `[iron §L Q3]` asserted "value tracks
   only"; confirmed as 25/25. §3.5.
4. **Downfall Hexaghost's transition table**, to corroborate `[mods §2.1]` and to give
   the three-way blend join a third leg. §3.5.

Absolute paths and line numbers are given at each use. Nothing was written outside this
file; no git command was run; the primary checkout was read-only.

---

## 1. THE JOINED MATRIX

One row per approach. Columns are the six the dispatch asked for. **No approach is
ranked here** — ranking is partly Lane A's bake-off evidence and finally [USER]'s.
Long cells are expanded in §2.

| approach | authoring dependency | runtime contract | fallback behaviour | performance observables | source / licence | explicit unknowns |
|---|---|---|---|---|---|---|
| **A. Layered sprites** — static `Sprite2D` / `TextureRect` layers moved, swapped or keyed by `AnimationPlayer` / `AnimationTree` / `Tween` / `_Process` | **Raster editor only.** No importer, no rig format, no external tool, no licence `[mawler §I]` `[mods §4]`. Our added cost is pipeline, not art tooling: text `.tscn` under `pck-src/`, script-less scene rule, a `resource=` contract line or `validate.ps1 S6c` fails the deploy, one MegaDot `--headless --import` `[iron §I]` `[regent §I.3]` | `%Visuals` must be `Node2D`-derived and **must not** be a `SpineSprite`: `NCreatureVisuals.IsSpineNode` is literally `_body.GetClass() == "SpineSprite"`, so any other type takes the spine-less door automatically `[here]` `NCreatureVisuals.cs:179-189`. `HasSpineAnimation` false ⇒ **no `CreatureAnimator` is ever built** `[schema §1.2]`, `SetAnimationTrigger` is a no-op, so **something external must route triggers** — three shapes exist in the wild `[mods §4.1]`. The four required `%` nodes still apply `[here]` `NCreatureVisuals.cs:217-225` | The base game's **own** fallback body is this approach: `fallback.tscn` is a plain `Sprite2D` with `error.png`, no skeleton `[mawler §B]`. But **player bodies have no fallback at all** — `CharacterModel::CreateVisuals` has no try/catch `[iron corr. 7]` `[regent §H.1]`, and a missing required `%` node throws outside the monster try/catch too (§3.1). Missing-state behaviour inside a Godot `AnimationTree` is **UNKNOWN** — it is *not* the base game's silent-freeze path | Klee body: **14,109 B** source scene, 14 nodes, 5 layers, 20 sub-resources `[iron §I]` `[here]`; **108,919 B packed** incl. 5 layer textures, measured off the deployed `klee.pck` `[mawler §J]`. Furina: 15,359 B / 13 nodes / 4 layers `[here]`. 0 emitters, 0 draw-affecting materials in the body `[here]`. **Every dynamic number UNKNOWN** | Ours. Public exemplars: Pael (**no LICENSE detected**), a third-party Furina mod (**none detected**), Downfall MIT `[mods §3]` | Whether it reads at combat distance (no frame seen, `[mods §10]`); whether layer count scales to a complex silhouette; what a `Travel()` to a missing state does; **five capabilities Spine gives free are absent by construction** (§3.2) |
| **B1. Cutout / skeletal 2D — *Godot-native* (`Skeleton2D` + `Bone2D` + `Polygon2D`)** | n/a — **no exemplar exists to price** | n/a | n/a | n/a | n/a | **NON-FINDING, and a strong one.** Zero occurrences across all 171 Downfall `.tscn`/`.tres`/`.cs` and in every body scene read in the widened 11-repo set `[mods NF-1]`; zero in `klee-mod/pck-src/` `[here]`; zero in all 126 base creature scenes `[iron §C]` `[regent §L.2]`. This is an absence **inside a stated boundary**, not proof the engine lacks it |
| **B2. Cutout / skeletal 2D — *as the ecosystem actually does it*: Spine** | **The Spine editor, commercial.** Base game exports **4.2.43** `[iron §D.2]` `[mawler §C]` `[beast §I]`; Downfall ships **4.2.39** raw and **4.2.11** imported, in one shipping configuration `[mods §2.4]`. Six Downfall characters commit the `.spine` **editor project** itself, and `build/setup.ps1:22` downloads Esoteric's runtime `[mods §4]`. Spine Runtimes License, retrieved 2026-08-26: *"each user of the Products must obtain their own Spine Editor license"* `[mods §4]`. **Charter §4/S16 forbids proposing this as our answer** | `%Visuals` is a `SpineSprite`, wrapped as `MegaSprite` at `_Ready` `[here]` `NCreatureVisuals.cs:226-234`. The state machine is **C# built at spawn — there is no `.tres` state machine anywhere** `[schema §1.2]` `[beast §L.2]`. `AnimState` id **is** the Spine animation name; trigger resolution is anyState-first `[beast §D.4]`; `NextState` queues on the same track; a per-pair mix table carries blend times incl. explicit zero; looping tracks get free per-instance desync | **Skeleton data fails to load ⇒ silent DOWNGRADE**, not a throw: warning `"Spine skeleton data failed to load for {name}, disabling spine animation."`, `SpineBody = null`, body becomes a static pose, **no death SFX, death length `0f`** `[here]` `NCreatureVisuals.cs:229-233` + `[iron corr. 6]`. **Missing animation name ⇒ silent FREEZE**: logs, returns, `_currentState` has already advanced, and the `NextState` queue is skipped `[iron §H]`. Missing bone for a `SpineBoneNode` ⇒ **UNKNOWN**, native DLL `[beast §L]` | Packed body totals: Ironclad **364,451 B**, Mawler **367,096 B**, Ceremonial Beast **773,563 B**, Regent **≈703,000 B** (3 skeletons) `[iron §J]` `[mawler §J]` `[beast §J]` `[regent §J.1]`. Shape is stable: on Mawler, texture **71 %** / skeleton **28 %** / scene **0.33 %** `[mawler §J]`. Scene text is a rounding error **except** where baked particle data is inlined (§3.6) | Base game assets are MegaCrit's, read-only, never ours to ship. Downfall's MIT covers **its code, not Spine** `[mods §4]` | **Every clip duration** (binary `.skel`, unparsed) — all four bodies `[iron §L]` `[regent §L.1]` `[mawler §L]` `[beast §L]`; bone/slot/constraint counts (string scans only); `bone_mode = 1` semantics; **whether our build's stock MegaDot editor even registers the `spine.skel`/`spine.atlas` importers** `[iron UNKNOWN 1]`; **whether any base skeleton uses Spine *mesh* attachments at all** (§2.C) |
| **C. Mesh deformation** — two different things wear this name | **(a) shader-on-quad:** a shader + noise texture, no licence `[mods §4]`. **(b) true vertex deformation:** a full 3D DCC exporting glTF, plus Godot's glTF importer — which Downfall's own `project.godot:69` disables for Blender `[mods §4]` | **(a)** an ordinary `CanvasItem` child — **no special contract**. The base game's analogue is stronger: Ironclad hangs a `ShaderMaterial` on a `SpineSlotNode` bound to slot `slash_mesh`, so the effect draws **inside the skeleton's own z-order** `[iron §B, §G]`. **(b) UNKNOWN** — a `Skeleton3D` is not a `Node2D`; how it hosts under the 2D body contract was not determined `[mods UNKNOWN-3]` | **(a)** shader-compile failure not tested — **UNKNOWN**. A *non-shader* material on Ironclad's slot **throws**, via an unchecked cast at `NIroncladVfx.cs:93` `[iron §H]`. **(b) UNKNOWN** | **(a)** Ironclad's whole private VFX cost is **20,202 B**, but its shared noise texture is **339,824 B across 7 bodies** — the shared asset dwarfs the private one `[iron §J]`. **(b)** nothing measured anywhere `[mods NF-4]` | **(a)** Downfall MIT. **(b)** Samus: **no LICENSE detected** `[mods §3]` | **(b)** is a **single unreplicated instance whose shipped status could not be confirmed** — `CustomVisualPath` names a file absent from the repo `[mods UNKNOWN-2]`. And, newly named here: **nothing in the corpus establishes that Spine mesh attachments (as opposed to region/cutout attachments) are used by any base body** — `slash_mesh` is a *name*, and a filename match is not proof (charter §3.5) |
| **D. Particles / tweens** | **None beyond one texture per emitter** `[mods §4]`. The exception is baked emission data: Regent inlines a **2048×1 `RGFloat` image of 977 points** as **60,020 B — 79.3 % of its whole scene** `[regent §J.1]`; the Beast inlines **1,732 points as 60,071 B — 87 % of its scene** `[beast §B]`. That is authored in a tool and serialised as decimal text | Emitters are ordinary children. `Tween` is created per call and persists nothing `[mods §4]`. Two shipped base-game uses raise this above decoration: **`AnimTempRevive` is a pure `Tween` used as the revive animation on a player body** `[regent §F.2]` `[iron §F]`, and **`IDeathDelayer` gates the Beast's death on a particle `Finished` signal** — the only implementor in the entire decompile `[beast §F]`. Emitters reach the animation **only** through a per-body driver script: all 49 `ConnectAnimationEvent` call sites are `N*Vfx` types `[mawler §G]` | **"Valid, loads, and wrong."** Delete the Beast's driver and the scene still loads, but `DeathParticles` keeps the scene's `emitting = true` — **1,500 particles fire at spawn instead of at death**, and the death gate silently disappears `[beast §B]`. Driver present but a node path missing ⇒ **hard throw at `_Ready`**, no null guards `[regent §B]` `[beast §H]`. The base game admits in a shipped comment that event-driven VFX teardown is unreliable under interruption and papers over it with a per-animation-start reset `[regent §G.3]` | Regent: 6 emitters, **1,330** max simultaneous `[regent §J.1]`. Beast: **1,500** GPU one-shot at `fixed_fps = 0` (uncapped) + 6 CPU looping at `preprocess = 7.0`, i.e. saturated on frame one `[beast §G, §J]`. Ironclad and Mawler: **zero** `[iron §C]` `[mawler §C]`. Ours: 0 in the body, 3 `GPUParticles2D` in separate VFX scenes, and exactly **one** `KleeCode` file calling `CreateTween` `[here]` `klee-mod/KleeCode/Vfx/KleeCombatVfx.cs:71,74` | No dependency; Downfall MIT `[mods §4]` | Every dynamic cost `[beast §J]`. Whether a **script-less** mod scene can host an `IDeathDelayer` implementor at all `[beast §L Q5]`. Whether the base game's interruption-reset convention is needed for `AnimationPlayer`-driven VFX `[regent §L.3 Q7]` |

---

## 2. Row detail

### 2.A Layered sprites

**What the corpus proves it can do.** A shipped, released public StS2 mod animates a
**player** body with a native Godot `AnimationTree` state machine and no Spine at all —
Downfall's Hexaghost, five hand-keyed clips (`idle` 8.0 s looping, `cast` 1.3 s, `die`
4.0 s, `hurt` 0.9 s, `attack`) over 4 `GPUParticles2D`, 3 shader quads and 2 `Sprite2D`
`[mods §2.1]`. At the other end, Pael is **one static `Sprite2D`** whose entire motion
is a sine "breath" in `_Process` `[mods §3.1]`, and a third-party Furina mod's whole
animation system is flipping `Visible` between two layers `[mods §3.1]`.

**What it cannot do without extra work.** Five capabilities are free with Spine and
absent here by construction — see §3.2. The one with the sharpest evidence is the
**timed event channel**: `NIroncladVfx` is driven entirely by two Spine events fired
from *inside* the clip (`attack_slash_start`, `heavy_slash_start`), which is the
skeleton's complete event set `[iron §G]`. The native analogue is an `AnimationPlayer`
method-call track — and **our rigs have none**: all 25 tracks in
`klee-mod/pck-src/klee/model/combat.tscn` are `type = "value"` `[here]`.

**The cheapest credible tell in the whole corpus is in this row.** Downfall's slimes
key **one bezier track on `Visuals:position:x`, 0.5 s, two keys** — a lunge. No new
art, no new clip `[mods §2.2]`.

### 2.B Cutout / skeletal 2D

**B1 (Godot-native) is a non-finding with teeth.** Nobody in the sampled ecosystem uses
`Skeleton2D`/`Bone2D`/`Polygon2D`. When public StS2 mods say "skeletal 2D" they mean
Spine `[mods NF-1]`. Four of the eleven repos were read at tree depth only, so the
boundary is real `[mods UNKNOWN-7]`.

**B2 (Spine) — the size gap is in the rig, not the scene.** The single most useful
correction the corpus makes to intuition: *the game's simplest enemy has a five-node
scene and an ~80-bone rig.* Mawler's `.tscn` is 1,204 B — four required nodes and a
root, no particles, no driver, no materials — while a string scan of its skeleton finds
**~80 bones incl. a 20-bone path-driven tail, ~23 slots, ~13 constraints incl. 4 IK**
(counts `UNVERIFIED`) `[mawler §C]`. **The scene is small because the complexity moved
into the skeleton.** Any comparison that prices bodies by scene size is measuring the
wrong file.

**Complexity lives in different places on the two sides.** On the player side it lives
in the **scene**: Regent's animator is the base player floor **plus one row**, while its
scene is 28× Ironclad's `[regent §D.0]`. On the boss side it lives in the **state
machine**: the Beast's scene is smaller than Regent's, but it carries **11 states, 15
conditional `Hit` branches and two conditional deaths** `[beast §D.1]`.

**The animator contract, restated once so no row re-derives it.** Named clips
addressable by string; anyState-first trigger resolution with `Func<bool>` branch
conditions; `NextState` queued on the same track; per-pair mix incl. explicit zero;
free loop desync `[schema §1.2]` `[beast §D.4]`.

### 2.C Mesh deformation

Two unrelated techniques share the name, and the corpus supports only weak claims about
either.

**(a) Shader-on-mesh is real and shipped, but it is *not* deformation.** Hexaghost's
three `MeshInstance2D`/`QuadMesh` smoke planes are a mesh used as a shader canvas
`[mods §4]`. The base game's equivalent is better evidence for us because it sits
*inside* a body: Ironclad's `SpineSlotNode` binds a shader to Spine slot `slash_mesh`,
so the slash draws in that slot's z-order — behind an arm, in front of a torso — and a
tween on a shader parameter is what animates it `[iron §B, §G]`. A layered `Sprite2D`
rig has z-order only between its own sprites `[iron §L Q4]`.

**(b) True vertex deformation is one unreplicated instance.** Samus's `.glb` +
`Skeleton3D` (40+ bones) wrapped in an `AnimationTree` is the only mesh-deforming rig
found anywhere in the sample, it is 3D imported into a 2D game, and the repo's declared
combat body is **not committed** `[mods §3.1, UNKNOWN-2/3]`.

**A gap this integrator is naming that no source file named.** Spine supports both
region attachments (cutout) and mesh attachments (deformation). **Nothing in the corpus
establishes which the base game's skeletons actually use.** The evidence available
tonight is a slot *named* `slash_mesh` `[iron §G]` and 82 atlas regions `[iron §C]` —
and attachment type is encoded numerically in the binary `.skel`, so no string scan can
distinguish them. Recorded as UNKNOWN-M in §8; a filename match is not proof (charter
§3.5).

### 2.D Particles / tweens

**This row carries two shipped mechanisms that are easy to miss because they look like
decoration.**

1. **A tween is a first-class animation substitute on a shipped player body.**
   `AnimTempRevive` — fade `modulate:a` to 0 over 0.2 s, snap the animator to `Idle`,
   fade back over 0.2 s — is what every base player actually does on revive, because
   **no player registers a `Revive` trigger** `[regent §F.2]` `[iron corr. 2]`.
2. **A particle system can gate combat flow.** `IDeathDelayer` holds the `NCreature`
   alive until the death emitter raises `Finished`; the Beast is its only implementor,
   and the gate is **skipped entirely at `FastMode.Instant`** `[beast §F]`.

**The coupling that makes both work is the per-body driver script**, and that is
exactly the seam our pipeline closes by rule: all 49 `ConnectAnimationEvent` call sites
in the decompile are `N*Vfx` driver types `[mawler §G]`, and our scenes are script-less
`[iron §I]`. Mawler is the control case — **no driver, so no Spine event on that body
reaches any C# handler at all**, and its timing surface is trigger-and-wait only
`[mawler §G]`.

**Baked emission data is the one real authoring cost in this row**, and it is large:
79.3 % of Regent's scene and 87 % of the Beast's scene are single inline
`PackedByteArray` lines of point positions `[regent §J.1]` `[beast §B]`. Strip Regent's
and the scene is ~15.7 kB — **the same order as our own 14,109 B Klee rig**
`[regent §J.1]`.

---

## 3. Cross-cutting joins the matrix rows cannot hold

### 3.1 The failure ladder — corrected, and one conflict between corpus files RESOLVED

`[mawler §H]` and `[beast §M.1]` **directly contradict each other** on what happens when
a monster body's scene loads but a required `%` node is missing. Mawler's file says the
throw happens *inside* `MonsterModel::CreateVisuals`'s `try` and the body becomes
`fallback.tscn`. The Beast's file says the `try/catch` is not on the stack.

**Resolved first-hand, by reading the decompile both files cite** `[here]`, at
`…/scratchpad/sts2src/`:

- `MonsterModel::CreateVisuals` wraps **only** `Instantiate<NCreatureVisuals>(...)` —
  `MonsterModel.cs:420-432`.
- `NCreature.Create` calls `entity.CreateVisuals()` at **`NCreature.cs:454`** and
  returns.
- `NCreature._Ready` adds the visuals to the tree at **`NCreature.cs:487`** — a
  different call stack.
- `NCreatureVisuals._Ready` does the four `GetNode<T>` lookups at
  **`NCreatureVisuals.cs:219-223`**, and `_Ready` runs on **tree entry**, not on
  `Instantiate`.

**`[beast §M.1]` is correct; `[mawler §H]`'s second row is wrong.** The failure ladder
therefore has **three** classes, not two, for **both** players and monsters:

| failure | class | outcome |
|---|---|---|
| scene **file** missing or unparseable | **hard, recovered — monsters only** | caught → `fallback.tscn` (`MonsterModel.cs:420-437`). **Players have no equivalent**: `CharacterModel::CreateVisuals` is three unguarded lines `[iron corr. 7]` `[regent §H.1]` |
| scene loads, **required `%` node missing** | **hard, NOT recovered — everyone** | uncaught throw at tree entry `[here]` `NCreature.cs:487` + `NCreatureVisuals.cs:219-223` |
| scene loads, **skeleton data fails** | **silent DOWNGRADE** | warning, `SpineBody = null`, static pose, **no death SFX, death length `0f`** `[here]` `NCreatureVisuals.cs:229-233` |
| scene loads, **animation name missing** | **silent FREEZE** | logs, returns, `_currentState` already advanced, `NextState` queue skipped `[iron §H]` |
| optional node missing (`%OrbPos` / `%TalkPos` / `%PhobiaModeVisuals`) | **silent, benign** | `%OrbPos` → `%IntentPos`, `%TalkPos` → null, phobia mode inert for every body in the corpus `[here]` `NCreatureVisuals.cs:220,224,225` |

The two silent classes are the ones a visual-QA gate exists for, and on a body with no
scene-side visuals they are **indistinguishable by eye** `[mawler §H]`.

### 3.2 What Spine gives free — the five-item list every other row must price

Assembled once from all four bodies. Each item names its native analogue and the cost
the corpus attaches to it.

| # | free with Spine | cited | native analogue | what the corpus says it costs |
|---|---|---|---|---|
| 1 | **Per-pair blend time, including an authored exact zero** | `[iron §E]` (10 rows, 6 zeros), `[regent §E.1]` (4 rows, 3 zeros), `[mawler §E]` (4 rows, 2 zeros), `[beast §E]` (4 rows, 3 zeros); `default_mix = 0.05` everywhere else | `AnimationNodeStateMachineTransition.xfade_time` | Authored per transition. **Ours are all 0** — see §3.5 |
| 2 | **A queued follow-on clip on the same track** (`NextState`) | `[schema §1.2]`, 4 chains on Ironclad, 6 on the Beast `[beast §E]` | `switch_mode`/`advance_mode` auto-return | Structurally present in our rigs (§3.5); **interruption semantics untested** `[mawler §L Q4]` |
| 3 | **Per-instance loop desync** — random time-scale `[0.9, 1.1]` and ±0.1 s phase | `[schema §1.2]`, `CreatureAnimator.cs:169-174` | none automatic | **Absent for every spine-less body**, because the whole `CreatureAnimator` is skipped. Downfall re-implemented it **by hand in 299 lines of reflection** for its Spine bodies `[mods §5.1]` |
| 4 | **Named events fired from inside a clip, delivered as a signal** | `[iron §G]` (2 events, the complete set), `[beast §D.3]` (5 events, **exact 1:1** with its handlers), `[regent §D.3]` (9 declared, 6 handled) | `AnimationPlayer` method-call track | **We have zero method tracks** `[here]`; and reaching C# at all currently requires a scene script, which our rule forbids `[mawler §L Q7]` |
| 5 | **Named bone / slot attachment with correct draw order** | `[regent §G.2]` (4 `*_particle_attach` bones authored *for* this), `[iron §B]` (slot `slash_mesh`), `[beast §G]` (2 bone targets pinned to world positions) | `RemoteTransform2D`, `Skeleton2D`, or a per-layer track | Unpriced. A layered rig has z-order only among its own sprites `[iron §L Q4]` |

**Item 3 is the one nobody is currently paying and nobody currently notices**, because
we ship no two-of-a-kind body. It becomes visible the moment two copies share a screen
`[regent §L.3 Q8]`.

### 3.3 The trigger seam: three shapes, one naming skew, one takeover

The base game's `NCreature.SetAnimationTrigger` is `_spineAnimator?.SetTrigger(...)` — a
guaranteed no-op without Spine — **but the method still runs**, so a Harmony patch fires
regardless. All three public shapes exploit exactly that `[mods §4.1]`.

| shape | who | dispatch target |
|---|---|---|
| interface on a scene script | Downfall | `Visuals is IAnimatedVisuals v → v.OnAnimationTrigger(trigger)`; 9 implementors |
| node lookup, script-less scene | **ours** | `visuals.GetNodeOrNull<AnimationTree>("%AnimationTree")` → `playback.Travel(state)` |
| generic adapter in the shared library | **BaseLib** | `CustomAnimation.PlayCustomAnimation(...)` → first of `AnimationTree` / `AnimationPlayer` / `AnimatedSprite2D` found |

**Three facts join here that no single source file could state:**

1. **BaseLib — already a hard dependency of ours — ships the generic route**, and the
   **installed** DLL (3.4.5.0 = `Alchyr/BaseLib-StS2@4a97642`) contains it
   `[mods §4.2]`. `docs/current/STATE.md:159` pins **3.3.7.0**; the installed DLL is
   **3.4.5.0**. Recorded as a fact; reconciling the pin is not this file's call.
2. **BaseLib's death-name probe is `Dead` / `Die` / `dead` / `die`. Our scenes name the
   state `death`** `[mods §4.2]` — confirmed first-hand: `states/death/node` and
   `resource_name = "death"` in **both** our rigs `[here]`
   `klee-mod/pck-src/klee/model/combat.tscn:385,290` and
   `klee-mod/pck-src/furina/model/combat.tscn:313`. Downfall's Hexaghost names it
   **`die`** and is inside the probe list `[here]`
   `…/scratchpad/Downfall/Hexaghost/scenes/character/hexaghost_main.tscn:863`.
3. **BaseLib takes over the death *length***: `CustomAnimationPatch` replaces
   `StartDeathAnim`'s return with `min(CustomCharacterModel.DeathAnimTime, 5f)` whenever
   a custom animation exists `[mods §4.2]`. Four separate corpus files ask whether our
   spine-less death returns `0f` and shortens combat `[iron §L Q5]` `[regent §L.3 Q4]`
   `[mawler §L Q3]` `[beast §L Q6]` — **the sidecar's evidence suggests the length half
   may already be handled and the SFX half is not.** Neither half was observed in a
   running game by anyone; this is a join between two cited readings, not a finding.

### 3.4 Combat is paced by C# constants, not by clip length

Independently established on three bodies, and it is the most consequential thing in the
corpus for anyone building a replacement grammar:

- `CreatureCmd.TriggerAnim` awaits `CustomScaledWait(min(waitTime*0.5, 0.25), waitTime)`
  on a `waitTime` **the caller passes** `[regent §E.3]` `[mawler §E]` `[beast §E]`.
- Ironclad: attack 0.15 s, cast/power-up 0.25 s, heavy 0.2 s `[iron §F]`. Regent: same
  plus `sovereignBladeAnimDelay` 0.25 s `[regent §E.3]`. Mawler: attack 0.35 s, roar
  0.5 s `[mawler §E]`. Beast: 0.6 s / 1.0 s, with three moves passing **0 s** and
  hand-waiting around their own VFX `[beast §E]`.
- **The only place a real clip length is read back is death** — and it gates
  `Hook.AfterDeath` and the reward screen `[beast §E]` `[regent §F.1]`.

**Consequence for any approach in the matrix:** clip-duration accuracy is nearly free
everywhere except death, and death is exactly where the spine-less path currently
returns `0f` and plays no sound (§3.1, §3.3).

### 3.5 The blend convention — a three-way join, first-hand

No source file could make this comparison, because it needs the base tables, our rigs,
and a public native rig side by side.

**Base game (Spine mix tables).** `default_mix = 0.05` everywhere, plus a handful of
authored rows. The authored rows are *concentrated on damage*:

| body | rows | zeros | what the zeros are |
|---|---|---|---|
| Ironclad | 10 | 6 | all attack→attack or damage→damage `[iron §E]` |
| Regent | 4 | 3 | every path *into* `hurt` or `die` `[regent §E.1]` |
| Mawler | 4 | 2 | `hurt→hurt`, `hurt→die` `[mawler §E]` |
| Ceremonial Beast | 4 | 3 | `attack→attack`, `hurt→hurt`, `hurt→die` `[beast §E]` |

The legible rule, stated in two files independently: **blend into and out of rest, hard
cut between blows** `[iron §E]` `[regent §E.1]`. Ironclad's *slowest* authored blend is
`hurt → idle_loop` at **0.10 s** `[iron §E]`.

**Downfall's Hexaghost (native `AnimationTree`, no Spine)** does the same thing with
Godot's own knobs `[here]`
`…/scratchpad/Downfall/Hexaghost/scenes/character/hexaghost_main.tscn:824-863`:

- into-a-tell transitions (`idle→hurt`, `idle→attack`, `idle→die`, `idle→cast`): **all
  properties defaulted** — no `xfade_time`;
- `Start→idle`: `advance_mode = 2`;
- **return-to-idle** (`hurt→idle`, `attack→idle`, `cast→idle`): **`xfade_time = 0.1`,
  `switch_mode = 2`, `advance_mode = 2`** — the same 0.1 s ease back to rest Ironclad
  authors, and an auto-return that is the structural analogue of `NextState`.

**Ours** `[here]` `klee-mod/pck-src/klee/model/combat.tscn:350-391`: four states
(`idle`/`attack`/`hurt`/`death`) + `Start`/`End`, nine transitions, and the same shape —
`hurt→idle` and `attack→idle` carry `switch_mode = 2` + `advance_mode = 2`;
into-a-tell transitions are travel-only. **But `grep -c xfade_time` returns 0 in both
`klee/model/combat.tscn` and `furina/model/combat.tscn`.** Every one of our transitions
is therefore at Godot's default, i.e. an instant cut.

**So:** structurally our rigs already reproduce free-capability #2 (queued return to
idle). On free-capability #1 we are at one extreme — **we blend nothing**, where the
base game blends everything it did not deliberately hard-cut, and the one public native
body that solved this problem blends back to rest at exactly the base game's number.

Two honesty notes. **(a)** The raw property values above are fact; the *semantic*
reading of Godot's `switch_mode`/`advance_mode` enum integers is **UNVERIFIED by this
integrator** — it would be settled by the Godot 4.x
`AnimationNodeStateMachineTransition` documentation or engine source, neither of which
was opened. **(b)** Whether a 0 s cut back to idle is visibly wrong is an eyes-on
question, and eyes-on is [USER]'s.

### 3.6 Packed size, all bodies, one table

Every figure is packed bytes from the pck directory, except our own which are measured
off the deployed `klee.pck`.

| body | scene | body total | note | cite |
|---|---|---|---|---|
| `silent.tscn` | 1,141 | — | the scene floor, 5 nodes | `[iron §C]` |
| `defect.tscn` | 1,149 | — | ties the floor | `[iron corr. 5]` |
| `fallback.tscn` | 1,064 | — | **spine-less by construction** — `Sprite2D` + `error.png` | `[mawler §B]` |
| `mawler.tscn` | 1,204 | **367,096** | texture 71 % / skeleton 28 % / scene 0.33 % | `[mawler §J]` |
| `ironclad.tscn` | 2,701 | **364,451** | + 20,202 private VFX; + a 339,824 B noise texture **shared with 6 other bodies** | `[iron §J]` |
| `necrobinder.tscn` | 19,435 | — | the intermediate player rung; named, not profiled | `[regent §C]` |
| `ceremonial_beast.tscn` | 69,046 | **773,563** | **87 % of the scene is one baked emission mask** | `[beast §B, §J]` |
| `regent.tscn` | 75,694 | **≈703,000** | **79.3 % of the scene is one baked emission mask** | `[regent §J.1]` |
| `test_subject.tscn` | 139,319 | — | largest creature scene; out of corpus | `[beast §C]` |
| **our `klee` combat** | **14,109** (source) | **108,919** packed | 5 layers; ~⅓ the packed size of the game's simplest enemy | `[mawler §J]` `[here]` |
| **our `furina` combat** | **15,359** (source) | — | 13 nodes, 4 layers | `[here]` |

**Two readings the corpus supports and one it does not.** (i) Scene byte size is a bad
proxy for structural complexity — strip the two baked masks and both big scenes fall to
~16 kB `[regent §J.1]` `[beast §B]`. (ii) Skeletal bodies are texture-dominated
`[mawler §J]`. (iii) It does **not** support a quality or performance comparison between
our rig and any base body: different characters, different on-screen sizes, different
art budgets, and **not a controlled measurement** `[mawler §J]`.

### 3.7 Orphan census — the evidence for a "declared but unreferenced" QA class

Collected from all five files. Every row is a shipped, packed, unreachable thing.

| orphan | kind | cite |
|---|---|---|
| `weak_loop` | skeleton animation; appears **nowhere** in the decompile; smallest block in the file | `[iron §D.3]` |
| `Relaxed` / `relaxed_loop` | trigger registered by **all five** player classes and fired by **nobody** in 3,425 decompiled files | `[iron corr. 3]` `[regent §D.3]` |
| `Idle` trigger | registered by every player **and** every monster; **never fired anywhere** — return-to-idle runs entirely through `NextState` | `[mawler §D.4]` |
| `PlowHit` | trigger registered on the Beast, fired nowhere | `[beast §D.4]` |
| `_ignore/die_deluxe` | a second death animation in the Beast's skeleton; the string occurs **exactly once pack-wide** | `[beast §D.3]` |
| `death_emitter.png` | **11,128 B of shipped texture** in the Beast's own directory; its uid appears once, inside its own `.import` | `[beast §D.3]` |
| `attack2` / `attack_end` / `attack_test` | declared in both Regent skeletons, unhandled by its driver | `[regent §D.3]` |
| `idle_loop --Plow--> plow` | a per-state branch permanently shadowed by an anyState registration | `[beast §D.4]` |
| `AddBranch("Idle")` on `relaxed_loop` | unreachable for the same reason — and it is in the **base** player animator, so **every** player body carries it | `[regent §D.1]` |
| 3 `GpuParticles2D` fields in `NRegentVfx` | never assigned, never read | `[regent §G.3]` |
| `Regent.GetSovereignBladeAnim/DelayIfApplicable` | no callers; the card inlines the ternaries | `[regent §L.2]` |
| Mawler's `CastSfx` | computed and never played — its roar is silent | `[mawler §G]` |
| Beast's `CastSfx` | inherited and dead; the cry plays an explicit event instead | `[beast §G]` |

**Reading, and its limit:** "declared but unreferenced" is a real and *frequent* class
in a shipped, polished commercial game — thirteen instances across four bodies. That is
evidence that a detector is cheap and would fire; it is **not** evidence that any of
these is a defect, and none of them is ours.

---

## 4. Corrections carried forward

The four body files corrected the schema's shared grammar independently, and several
corrected the same thing. Deduped, so a matrix reader does not re-inherit an error. **No
correction changes a body pick or the evidence contract.**

| # | the schema said | the corpus says | agreeing files |
|---|---|---|---|
| 1 | seven canonical `CreatureAnimator` triggers are the player set | Those seven are the **class constants**. The **player floor** is 6 states / 7 anyState triggers: `Idle, Dead, Hit, Attack, Cast, PowerUp, **Relaxed**` — and **no player registers `Revive`** | `[iron corr. 1, 2]`, `[regent §D.0]` — independently |
| 2 | (silent) | **`Relaxed` is an orphan trigger** — registered by all five players, fired by nobody | `[iron corr. 3]`, `[regent §D.3]` |
| 3 | Ironclad is "the seven-state player shape" | Ironclad is base **+1 state +1 trigger** = 7 states / 8 triggers. Silent is base+1 too (`shiv`), so Silent is only the **scene** floor, and `defect.tscn` ties it | `[iron corr. 1, 5]` |
| 4 | `silent.tscn` has four nodes | **Five** | `[iron corr. 4]` |
| 5 | `CreateVisuals` wraps the scene load in try/catch → `fallback.tscn` | **`MonsterModel` only.** `CharacterModel::CreateVisuals` has no try/catch and no fallback — **a broken player body throws** | `[iron corr. 7]`, `[regent §H.1]` |
| 6 | a missing required `%` node ⇒ "whole body falls back" | **It does not** — `_Ready` runs at tree entry, outside the `try`. Three failure classes, not two | `[beast §M.1]`, **confirmed first-hand** §3.1; contradicts `[mawler §H]`, which is wrong |
| 7 | (silent) | **A skeleton that fails to load silently downgrades the body to spine-less** — a `§1.1` row the table lacks | `[iron corr. 6]`, confirmed `[here]` `NCreatureVisuals.cs:226-234` |
| 8 | player attack/cast/power-up audio is not gated on Spine | True, **but the switch matches only `"Attack"`/`"Cast"`/`"PowerUp"`**. A bespoke trigger gets the animation and **loses the sound** — Ironclad's nine heavy cards, Regent's Sovereign Blade (whose card hardcodes its own FMOD path) | `[iron §F]`, `[regent §F.4]` — independently |
| 9 | Mawler's rename-only override is "the most common variation in the monster corpus" | **Not supported by a count**: of 121 monster files, 66 carry bespoke triggers/branches, 39 override nothing, 9 are rename-only. The stronger true claim: Mawler and `SewerClam` are the **only two** whose animator is the default with one string changed | `[mawler §M.1, §M.2]` |
| 10 | the Beast's `PlowStartTarget`/`PlowEndTarget` are "gameplay anchors" | **Presentation anchors.** Their only consumers restore a cached `GlobalPosition`; damage, targeting and the hitbox never touch them | `[beast §M.2]` |
| 11 | (silent) | The Beast is the **only implementor of `IDeathDelayer`** in the decompile, and its animator/event contract is **exactly 1:1** — the two most transferable facts about it | `[beast §M.3]` |

---

## 5. `PROPOSED` — the technical read

Everything in this section is a **technical** read labelled `PROPOSED`, in the charter
§3.1 sense. It ranks no approach, proposes no art, no purchase, no scope and no ship
choice, and it is not a recommendation about what any character should look like.

**P1 — `PROPOSED`: the four rows are the wrong decision axis; the five free-with-Spine
capabilities are the right one.** §0.2 shows every shipped body composes rows rather
than picking one, and §3.2 shows the real difference is a **five-item capability list**,
each with a named native analogue and a named cost. A bake-off framed as "layered vs
skeletal" measures a distinction no shipped body makes; a bake-off framed as "which of
the five does a body need, and what does each cost natively" measures the thing that
actually differs. Lane A owns the measurement; this is a framing proposal only.

**P2 — `PROPOSED`: the required-motion suite has an evidence-derived floor.** Read off
the four bodies rather than invented: `idle` looping · one attack · `hurt` · death ·
return-to-idle on each non-looping clip · one bespoke tell · one sub-clip-timed VFX
cue · one blend authored to exactly zero. That is the union of what all four bodies
actually use `[iron §D.1]` `[regent §D.1]` `[mawler §D.1]` `[beast §D.1]`. Whether Lane
A's suite should also carry the slime pattern — one bezier keyframe pair on
`position:x` `[mods §2.2]` — is Lane A's call, not this file's.

**P3 — `PROPOSED`: three cheap gates fall straight out of §3.1, and they are Lane C's to
accept or refuse.** (a) assert the four required `%` names exist in every creature
scene — this catches the one failure class the engine does **not** recover from
(`[beast §M.1]`, confirmed §3.1); (b) assert every state name a router can travel to
exists in the scene's `AnimationLibrary` — the silent-freeze analogue; (c) assert a
body's declared assets are referenced — §3.7 shows thirteen instances of the class in a
shipped commercial game. None of these needs a running game or a Spine parser.

**P4 — `PROPOSED`: three UNKNOWNs are cheap and unblock disproportionately much.**
(i) whether BaseLib's prefix and our postfix both fire and double-travel a state — one
targeted `KleeTests` case or one attended log read `[mods UNKNOWN-4]`; (ii) whether the
stock MegaDot editor our `build_pck.ps1` drives registers the `spine.skel`/`spine.atlas`
importers at all — a `--headless --import` over a throwaway pair `[iron UNKNOWN 1]`;
(iii) what a `Travel()` to a missing state does in a Godot `AnimationTree`, which is the
one failure class in row A with **no** evidence at all. Each is a lane experiment, not a
research one, and none was run tonight.

**P5 — `PROPOSED`: the death seam is the single highest-value thing to settle, and it is
one observation.** Four independent body files flagged it `[iron §L Q5]`
`[regent §L.3 Q4]` `[mawler §L Q3]` `[beast §L Q6]`; the sidecar supplies evidence that
BaseLib may already cover the **length** half but not the **SFX** half `[mods §4.2]`;
and §3.4 shows death is the *only* moment the engine reads a clip length back. One
attended death capture on a modded character, with audio, settles all four questions and
half of P4.

---

## 6. [USER] questions — deduped, numbered, with answer shapes

The five source files raised **46** transfer questions. They are deduped to **15** below.
Each carries an answer **shape** (pick-one / yes-no / open) and, where the option set is
a matter of fact rather than taste, the options are enumerated so the answer is a pick
and never a blank (charter §3.1). **No option is recommended.** §6.2 maps every original
question to its destination so nothing was dropped.

### 6.1 The questions

**Q1 — the death-state name.** Our scenes name the state `death`; the base game's
constant is `die`; BaseLib's probe list is `Dead` / `Die` / `dead` / `die` and **does
not contain `death`** `[mods §4.2]`, confirmed first-hand in both our rigs and in
Hexaghost §3.3. **Shape: pick-one.** (1) rename ours to `die`; (2) keep `death` and rely
on our own router only; (3) keep `death` and add the alias; (4) defer until Q2 is
answered.

**Q2 — who owns the trigger seam.** BaseLib already implements the generic route and the
installed DLL contains it `[mods §4.2]`; our `CreatureAnimationRouter` implements a
second one `[here]`. **Shape: pick-one, after one measurement.** (1) keep ours, treat
BaseLib's as unused; (2) drop ours, adopt BaseLib's; (3) keep both deliberately with a
documented precedence; (4) answer only after P4(i) shows whether both currently fire.

**Q3 — is a modded character's death currently silent, and is combat not waiting for
it?** Both follow from cited code; neither was observed in play. `StartDeathAnim` puts
the death SFX and the length read inside `if (_spineAnimator != null)`, and
`DeathAnimLengthOverride` is monster-only `[regent §F.1]`; BaseLib may already replace
the length `[mods §4.2]`. **Shape: yes-no ×2, settled by one capture (P5).** Then, if
yes: (1) file it; (2) accept it as a known gap for spine-less bodies; (3) route it to
Lane C as a gate.

**Q4 — revive.** Our router maps `Revive → idle`; the base game registers **no** `Revive`
on any player and falls to a pure `Tween` (`AnimTempRevive`), whose recovery calls
`_spineAnimator?.SetTrigger` **directly**, bypassing the public method we patch
`[iron §L Q1]` `[regent §F.2]`. So after a mid-combat revive a modded player may never
leave the `death` state. **Shape: yes-no + pick.** Is revive a surface we care about at
all? If yes: (1) patch `StartReviveAnim` as Downfall does `[mods §4.1]`; (2) handle it in
the scene; (3) leave it.

**Q5 — bespoke tells.** Every base body that wants a signature move gets a bespoke
trigger — `heavyAttack`, `shiv`, `sovereignBladeTrigger`, `summonTrigger`, and five on
the Beast — and our router **silently ignores unmapped triggers by design** `[here]`
`CreatureAnimationRouter.cs:41-43`. **Shape: pick-one.** (1) the router grows rows;
(2) the scene contract grows a per-body override table; (3) modded bodies do not have
bespoke tells. Note the joined cost of any bespoke trigger: **it wins the animation and
loses the character-derived SFX** (§4 row 8).

**Q6 — conditional state selection.** The Beast picks between two deaths by `Func<bool>`,
resolves `Hit` three ways, and **deliberately does not flinch mid-charge**
`[beast §D.1]`; no player body uses the machinery at all `[iron §L NF-1]`
`[regent §L.2]`. **Shape: pick-one.** (1) declare conditional branching out of scope for
modded bodies; (2) want it and route it to a lane; (3) revisit only if a boss is ever
built.

**Q7 — where sub-clip VFX timing lives.** Spine puts it in the **art** (a named event
inside the clip); the native analogue puts it in an `AnimationPlayer` method track; the
third option puts it in the C# that fired the trigger `[iron §L Q3]` `[beast §L Q4]`.
Our rigs currently have **zero** method tracks `[here]`. And the base game's own driver
admits event-driven teardown is unreliable under interruption and adds a
per-animation-start reset `[regent §G.3]`. **Shape: pick-one + yes-no.** (1) method
track; (2) C#-side timing; (3) no sub-clip timing. And: do we want the interruption
reset as a standing convention?

**Q8 — attachment points.** Regent anchors five emitters to four bones authored purely as
particle anchors and nests two whole sub-skeletons in a named slot `[regent §G.2]`;
Ironclad's slash draws **inside** the skeleton's z-order `[iron §G]`; Mawler's visible
slash is **split** between a skeleton attachment and a command-spawned VFX
`[mawler §G]`. **Shape: yes-no, then pick-one.** Does anything we plan need a VFX layer
*interleaved* with body parts, or a prop that follows a moving hand? If yes:
(1) `RemoteTransform2D` chain; (2) `Skeleton2D`; (3) a track per layer; (4) put the
attacker-side half in C# instead.

**Q9 — idle desync.** Free for Spine bodies, **absent for ours**, and Downfall paid 299
lines of reflection to keep it `[mods §5.1]` `[regent §L.3 Q8]`. It is invisible until
two copies share a screen. **Shape: yes-no + owner pick.** Do we care? If yes: (1) the
router; (2) the scene; (3) Lane A's suite.

**Q10 — the script-less scene rule.** Downfall attaches a script to every body and
dispatches through an interface `[mods §4.1]`; `IDeathDelayer` is a **node interface**
found by `GetChildrenRecursive<T>` `[beast §L Q5]`; all 49 Spine-event consumers are
scene-attached driver types `[mawler §G]`. **Shape: yes-no + pick.** Is the rule costing
a capability or only a convenience? If a capability: (1) relax the rule; (2) find a
runtime-attach route from `KleeCode`; (3) declare the capability out of scope.

**Q11 — visual-QA gates.** Three classes, all cited, all cheap: required `%` names;
travellable state names; declared-but-unreferenced assets (§3.7). Plus the hardest one —
**a body with a frozen pose and a correct wait time is indistinguishable from a working
one** `[mawler §L Q5]`. **Shape: pick-many, Lane C owns the build.** Which of (a)/(b)/(c)
from P3, and does the frozen-pose class need a capture-based gate rather than a static
one?

**Q12 — baked data in scenes.** 79 % of Regent's scene and 87 % of the Beast's are
inline baked emission point clouds `[regent §J.1]` `[beast §B]`. **Shape: pick-one.**
If a Teyvat body ever wants a comparable death burst: (1) inline in the `.tscn`; (2) a
separate resource; (3) our pipeline does not carry baked point clouds.

**Q13 — variant economy.** Downfall runs 15 slimes on **5 skeletons** with per-variant
atlases; AveMujica duplicates both halves instead `[mods §2.2]`. The economy is
technique-independent. **Shape: yes-no.** Is "one rig, many skins" the target shape for
our pipeline whatever the rigging technique?

**Q14 — the blend convention.** The base game blends into and out of rest and hard-cuts
between blows; **our rigs blend nothing** (§3.5). **Shape: pick-one.** (1) adopt "hard
cut into hurt/death, ease back to rest" as a written convention; (2) leave transitions
at 0 and decide by eye per character; (3) treat it as an eyes-on item per rig. Note
this one is partly taste and the eyes-on half is [USER]'s by definition.

**Q15 — capability scope declarations, and one hygiene item.** Four capabilities the
corpus documents that we have never needed, each answerable "in scope / out of scope /
revisit later": (a) `BoundsContainer` silhouette-following hitboxes — **no corpus body
uses it** `[beast §L]`; (b) a second idle (`relaxed_loop`) — shipped on all five base
players and **fired by nobody** `[regent §L.3 Q3]`; (c) a boss whose presentation
extends into the room background as a second skeleton plus FMOD music parameters
`[beast §G]`; (d) true mesh deformation (§2.C). **Plus the hygiene item:**
`docs/current/STATE.md:159` pins BaseLib **3.3.7.0**; the installed DLL is **3.4.5.0**
`[mods §4.2]`. **Shape: pick-many + one pick-one for the pin.** *(This file mints no id
and files nothing; the pin is reported, not triaged.)*

### 6.2 Dedupe map — where all 46 original questions went

| destination | absorbs |
|---|---|
| **Q1** naming | `[iron Q6]`, `[mawler Q2]`, `[mods Q1]` |
| **Q2** seam ownership | `[mods Q2]`, `[mods UNKNOWN-4]` |
| **Q3** death sound / length | `[iron Q5]`, `[regent Q4]`, `[mawler Q3]`, `[beast Q6]` |
| **Q4** revive | `[iron Q1]`, `[regent Q2]`, `[mods Q3]` |
| **Q5** bespoke tells | `[iron Q2]`, `[regent Q1]`, `[mawler Q1]`, `[beast Q1]` |
| **Q6** conditional selection | `[beast Q2]`, `[beast Q3]` |
| **Q7** sub-clip VFX timing | `[iron Q3]`, `[regent Q7]`, `[mawler Q7]`, `[beast Q4]` |
| **Q8** attachment points | `[iron Q4]`, `[regent Q6]`, `[mawler Q6]` |
| **Q9** idle desync | `[regent Q8]`, `[mods Q4]` |
| **Q10** script-less rule | `[iron Q7]`, `[mods Q7]`, `[beast Q5]` |
| **Q11** QA gates | `[regent Q5]`, `[mawler Q5]`, `[beast Q10]`, `[beast M.1 PROPOSED]` |
| **Q12** baked data | `[regent Q10]`, `[beast Q9]` |
| **Q13** variant economy | `[mods Q8]` |
| **Q14** blend convention | `[regent Q9]`, `[mawler Q4]` (interruption half also in §3.5) |
| **Q15** scope + pin | `[beast Q7]`, `[beast Q8]`, `[regent Q3]`, `[mods Q10]` |
| **§7 Lane A** | `[mawler Q8]`, `[mods Q5]`, `[mods Q9]` |
| **eyes-on, [USER]'s alone** | `[iron Q8]` — does a facing flip read as style or as a bug beside a base body |
| **closed by standing LAW, no question needed** | `[mods Q6]` — Downfall junctions the extracted base-game tree into its project root; `CLAUDE.md` forbids exactly that, and `tools/purge_worktree.py` enforces the adjacent half (`STATE.md:96-100`) |

---

## 7. Lane A — the concurrent bake-off, and what this matrix hands it

**Lane A is running its own native-animation bake-off in a separate worktree
(`../GItS-laneA`, charter §5) and was deliberately not read while writing this file.**
Its handoff joins this matrix in the morning read; where the two disagree, Lane A ran
code and this file read files, and that difference should decide.

Three questions from the corpus belong to Lane A rather than to [USER], and are recorded
here so they are not lost between the two documents:

1. **Which of a skeletal rig's constraints have *any* expression in an `AnimationTree` +
   `Sprite2D` rig?** Mawler's ~80 bones include 4 IK chains, a path-driven 20-bone tail
   and ~8 transform locks `[mawler §C, §L Q8]`. This file establishes the base-game
   requirement; it does not answer which parts are reproducible.
2. **Should the required-motion suite include the one-bezier-keyframe-pair attack tell?**
   `[mods Q5]` — the cheapest credible tell in the corpus.
3. **Does a native-`AnimationTree` route materially reduce version-drift exposure?** The
   game's Spine binding signature changed between 0.107 and 0.108 (`PRG-6985`) and public
   mods absorb it with cached reflection; a native route's API is Godot's `[mods §5.1,
   Q9]`. Worth measuring rather than assuming.

Lane A also owns P4(ii) — whether our stock MegaDot editor registers the Spine importers
at all — which is the one question that would change what "no-paid-tools" even means for
the import half.

---

## 8. UNKNOWN

Every item below is unanswered and says what would answer it. None was estimated.

| # | unknown | what would answer it |
|---|---|---|
| U1 | **Every clip duration** in the corpus — all four bodies | a Spine binary parser, or an attended capture timed against a frame counter |
| U2 | **Skeleton-internal bone / slot / constraint counts** — all figures are string scans marked `UNVERIFIED` | the same parser |
| U3 | **UNKNOWN-M, new here: whether any base skeleton uses Spine *mesh* attachments at all**, as opposed to region/cutout attachments | attachment type is numeric in the binary `.skel`; the same parser. `slash_mesh` is a name, not proof |
| U4 | **What a `Travel()` to a missing state does** in a Godot `AnimationTree` — the one failure class in row A with no evidence | a Lane C fixture; ten minutes, no game launch |
| U5 | **Whether BaseLib's prefix and our postfix both fire**, and whether that double-travels a state | one `KleeTests` case or one attended log read `[mods UNKNOWN-4]` |
| U6 | **Whether the stock MegaDot editor registers `spine.skel`/`spine.atlas`** | a `--headless --import` over a throwaway pair `[iron UNKNOWN 1]` |
| U7 | **Whether our characters' deaths are currently silent and unwaited-for** in play | one attended death capture with audio (P5) |
| U8 | **`bone_mode = 1` semantics, and what a missing `bone_name` does** — resolution is inside the native `libspine_godot` DLL, not decompilable | an attended probe `[beast §L]` |
| U9 | **Whether animation triggers replicate per-seat in co-op** or are re-derived locally | tracing the multiplayer command path `[regent §F.3]` `[beast §L]` |
| U10 | **Godot's `switch_mode` / `advance_mode` enum semantics** — §3.5 states the raw integers as fact and the reading as unverified | the Godot 4.x `AnimationNodeStateMachineTransition` documentation or engine source |
| U11 | **Every dynamic performance number** — draw calls, frame cost, load time, memory, and whether the Beast's `IDeathDelayer` pause is perceptible | all twelve capture slots across the four body files, plus a profiler, in an attended session |
| U12 | **Who actually drives Hexaghost's state machine** — both halves verified, the join not observed | an attended capture with Downfall installed, or a BaseLib debug-line log read `[mods UNKNOWN-1]` |

**All twelve capture slots in the corpus remain `capture pending`** — three per body ×
four bodies, plus a proposed fourth on the Beast (the phase break, the only place the
conditional-branch machinery is visible) `[beast §K]`. Every one is blocked by the same
line: [USER] is playtesting, and no agent may launch the game (PREFLIGHT).

---

## 9. What this does NOT establish

This file joins five research files and adds four first-hand checks. It does **not**
recommend an animation approach, rank layered sprites against skeletal 2D against
anything else, propose or refuse a purchase, or say that any of the four base bodies
should be reskinned, remapped, matched, or built. It sets no scope, no budget and no
ship target, and it mints no id.

**Nothing here was seen on screen.** The game was never launched. Every duration, every
frame cost, every "does that read right" question is capture-pending and marked so
rather than guessed. Several claims about skeleton contents rest on byte-string scans
rather than a parser and carry their source files' `UNVERIFIED` labels; a name present
in a file is not proof of a timeline that uses it.

Three specific limits are worth restating because they are easy to read past. **(a)** The
size comparison in §3.6 is a shape observation between different characters in different
packs with different art budgets — **not a controlled measurement**, and not a quality
or performance claim. **(b)** The absence of Godot-native cutout rigs (row B1) is an
absence inside a stated search boundary of eleven repositories, four of which were read
at directory-listing depth only — **not** a statement about the engine. **(c)** The
behaviours identified in our own mod — the possibly-silent death, the possible
never-leaves-`death`-after-revive, the zero-length reward delay — are read out of code
by four separate agents and reproduced in a running game by **none**. They are written
as questions for that reason, and Q3 and Q4 are the right shape for them; they are not
defect filings and this file files nothing.

Finally, this file resolved exactly one contradiction between its sources (§3.1) and
resolved it by reading the primary source both sides cite. It did not resolve any other
disagreement by preference, and where a source file's claim is weaker than it sounds —
the "most common variation" phrasing, the "gameplay anchors" phrasing — the correction
is recorded in §4 rather than silently applied.
