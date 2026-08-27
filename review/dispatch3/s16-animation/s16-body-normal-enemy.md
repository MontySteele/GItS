# S16 — corpus body: **normal enemy = Mawler**

> **This file decides nothing.** Research artifact from surplus-dispatch-3, research
> rail. Every technical read below is descriptive or labelled `PROPOSED`; taste,
> lore, art-direction, rights, spend, scope and ship calls remain [USER]'s. No
> balance window opened, no stamp moved, no id minted, no playtest interpreted,
> no game launched.

*Filename note for the integrator:* the schema's ownership map (`s16-00-schema.md`
§4) names this file `s16-03-enemy-normal.md`; the dispatch assigned the path
`s16-body-normal-enemy.md`. Same file, one owner, no second draft exists.

*Schema compliance:* sections **A–L** below follow `s16-00-schema.md` §2 in order.
Facts established once in the schema's §1 shared grammar are **cited, not
re-derived** — except where this body **contradicts** the schema, which §1 says to
report loudly. It does, twice. See §M.

---

## A. Identity and provenance

| Field | Content |
|---|---|
| `body_id` | `mawler` |
| `role` | `enemy-normal` |
| `class` | `MegaCrit.Sts2.Core.Models.Monsters.Mawler` (`sealed`, extends `MonsterModel`) — `sts2src/MegaCrit.Sts2.Core.Models.Monsters/Mawler.cs:17` |
| `scene` | `res://scenes/creature_visuals/mawler.tscn` — **1,204 B** packed (pck directory row; `…/scratchpad/s16/pck.tsv`) |
| `reachability` | Act 1 `Overgrowth` **only**; the act's encounter list carries `MawlerNormal` once (`sts2src/MegaCrit.Sts2.Core.Models.Acts/Overgrowth.cs:83`). `MawlerNormal` generates **exactly one** Mawler, alone (`…/Models.Encounters/MawlerNormal.cs:13-16`). On a player's **first run ever** (`unlockState.NumberOfRuns == 0`) the act pins it to `normalEncounters` **index 4 — the 5th normal fight** (`Overgrowth.cs:112-121`). Repo reference: `docs/current/dossiers/enemies/mawler.md:5-10`. |
| `read_on` | 2026-08-26. Game **v0.107.1**, commit `59260271`, Steam buildid `23811903` (`docs/current/STATE.md:159`). PCK: `C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2\SlayTheSpire2.pck`, 1,901,378,340 B, mtime 2026-07-18 22:34. Read-only; extractions went to the scratchpad, never a repo. |

The reachability claim is **verified in code**, not only in the dossier: the
first-run pin is a literal `RoomSet.SwapToOrCreateAtIndex<EncounterModel,
MawlerNormal>(_rooms.normalEncounters, 4)`. For capture planning this is the
strongest guarantee in the corpus — a fresh save reaches this body deterministically.

---

## B. Scene / resource topology

`res://scenes/creature_visuals/mawler.tscn`, `format=3`, `load_steps=3`, 37 lines.
Extracted read-only to `…/scratchpad/s16/x/scenes/creature_visuals/mawler.tscn`;
line numbers below are that file.

| # | path | type | unique name? | purpose | depends_on |
|---|---|---|---|---|---|
| 1 | `.` (`Mawler`) | `Node2D` | — (root) | body root; carries the shared `NCreatureVisuals` script (`:6-8`) | `ext_resource 1_iwtm2` |
| 2 | `Visuals` | `SpineSprite` | `%Visuals` | the entire visible body (`:10-20`) | `ext_resource 2_41vxg` |
| 3 | `Bounds` | `Control` | `%Bounds` | hitbox / HP-bar rect (`:22-29`) | — |
| 4 | `CenterPos` | `Marker2D` | `%CenterPos` | `VfxSpawnPosition` (`:31-33`) | — |
| 5 | `IntentPos` | `Marker2D` | `%IntentPos` | intent anchor (`:35-37`) | — |

**`ext_resource` list (2):**

| type | `res://` path | shared? |
|---|---|---|
| `Script` | `res://src/Core/Nodes/Combat/NCreatureVisuals.cs` | **shared** — the single root script every creature body in the game uses (schema §1.1) |
| `SpineSkeletonDataResource` | `res://animations/monsters/mawler/mawler_skel_data.tres` | **private** to this body |

**Node-contract conformance (schema §1.1).** All four required unique names are
present (`%Visuals`, `%Bounds`, `%IntentPos`, `%CenterPos`); all three optional
ones are absent (`%PhobiaModeVisuals`, `%OrbPos`, `%TalkPos`). Consequences,
cited: no alternate phobia body; `OrbPosition` silently falls back to
`IntentPosition` (`…/Nodes/Combat/NCreatureVisuals.cs:224`); `TalkPosition` stays
null (`:225`).

**Nodes the contract does not require: none.** Mawler carries no node beyond the
four required plus the root. Remove any one of the four and `_Ready`'s
`GetNode<T>` throws, the `try/catch` in `MonsterModel::CreateVisuals`
(`…/Models/MonsterModel.cs:420-432`) swallows it, and the body becomes
`fallback.tscn`. That is the whole failure ladder for this body — see §H.

**Geometry facts worth carrying to a capture (all `mawler.tscn`):** `Visuals`
sits at `(2, −26)` with `scale = (0.25, 0.25)` and is editor-locked
(`metadata/_edit_lock_`); `Bounds` is `anchors_preset = 0`, offsets
L −255 / T −327 / R 255 / B **absent → 0**, i.e. a **510 × 327** rect rising from
the origin; `CenterPos` `(0, −166)`; `IntentPos` `(0, −328)` — one pixel above the
top of `Bounds`. `Visuals.preview_animation = "roar"` and `preview_time = 1.32`
are editor-only fields, but see §D: `preview_animation` is a schema-blessed
verified source for a skeleton animation name.

**Contrast body — `fallback.tscn` (1,064 B, `…/s16/x/scenes/creature_visuals/fallback.tscn`).**
Same five-node shape, same required names, but `%Visuals` is a plain `Sprite2D`
with `res://images/monsters/error.png` and no skeleton. It is the shape a broken
enemy body becomes, and it is a **working example of a spine-less body inside the
base game** — `IsSpineNode` is false (`NCreatureVisuals.cs:183-188`), so
`HasSpineAnimation` is false, so no animator is ever built. Everything §H lists
as "silent" is true of the fallback body by construction.

---

## C. Node / layer / bone counts

Scene numbers are **fact** (counted in the extracted `.tscn`). Skeleton-internal
numbers are **UNVERIFIED** per schema §2C — they come from a raw length-prefixed
string scan of the binary `.spskel`, not from a format parser.

| metric | value | status |
|---|---|---|
| `nodes_total` | **5** (root + 4) | fact — `mawler.tscn` |
| `spine_sprites` | **1** | fact |
| `particle_emitters` (CPU / GPU) | **0 / 0** | fact — no `CPUParticles2D`, no `GPUParticles2D` in the file |
| `bone_nodes` (`SpineBoneNode` in scene) | **0** | fact |
| `slot_nodes` (`SpineSlotNode` in scene) | **0** | fact |
| `markers` (`Marker2D`) | **2** | fact |
| `sprite_layers` (`Sprite2D`) | **0** | fact |
| `driver_scripts` | **0** | fact — the only `Script` ext_resource is the shared `NCreatureVisuals`; there is **no `NMawlerVfx`** in `sts2src/MegaCrit.Sts2.Core.Nodes.Vfx/` (searched; absent) |
| shared materials | **0** | fact — no `material =` line anywhere in the scene |

**Inside the skeleton (all `UNVERIFIED`, string-scan; boundary: length-prefixed
ASCII names in the first 34,000 of 102,607 bytes of
`…/scratchpad/s16-body-normal-enemy/.godot/imported/mawler.skel-2e8c4bbaee7b9a37aa399e272e74f1eb.spskel`):**

| metric | value | note |
|---|---|---|
| Spine exporter version | `4.2.43` | header string at offset 9 |
| atlas regions | **21**, one page `mawler.png` 457 × 1031, `filter:Linear,Linear`, `scale:0.3325` | **fact** — the `.spatlas` is JSON-wrapped plain text and was read in full |
| bones | **~80** | incl. a **20-bone `tail_proportional*` chain**, 7 `tail_ctrl*`, 4 `*_ik`, `breathe`, `snarl`, `jaw_1`/`jaw_2`, three `ear_f_*` and three `ear_l_*` |
| slots | **~23** | 21 regions to 23 slots — `drool1/2/3` reuse one region |
| constraints | **~13** | 4 IK (`arm_b_ik`, `arm_f_ik`, `leg_b_ik`, `leg_f_ik`), ~8 transform (`*_rot_const`, `shoulder_*_lock`, `ear_const_f`, `head_crown_const`), 1 path (`tail_path_const`) |

Spine bone *icon* attributes (`gear`, `cog`, `arrows`, `rotate`, `arrowDown`,
`square`, `straightLine`) appear interleaved in the same string region and were
excluded from the bone count; a naive scan inflates it by ~7.

**This is the headline number of the file.** The "simplest enemy in the game" has
a five-node scene and an ~80-bone rig with IK, a path constraint and a
twenty-bone proportional tail. The scene is small *because* the complexity moved
into the skeleton, not because the body is cheap. §I and §M carry the consequence.

---

## D. Animation / state names

### D.1 Referenced states — complete and verified

`Mawler::GenerateAnimator` (`sts2src/MegaCrit.Sts2.Core.Models.Monsters/Mawler.cs:70-87`).

| `AnimState` id | looping | reached by trigger | branch condition | `NextState` |
|---|---|---|---|---|
| `idle_loop` | **yes** (`:72`) | `Idle` (`:81`) | none | — |
| `roar` | no (`:73`) | `Cast` (`:82`) | none | `idle_loop` (`:77`) |
| `attack` | no (`:74`) | `Attack` (`:83`) | none | `idle_loop` (`:78`) |
| `hurt` | no (`:75`) | `Hit` (`:85`) | none | `idle_loop` (`:79`) |
| `die` | no (`:76`) | `Dead` (`:84`) | none | — (terminal) |

Five states, five triggers, **zero conditions, zero per-state branches** — every
branch is an `AddAnyState`, i.e. registered on `_anyState`, which
`CreatureAnimator::SetTrigger` consults first (`…/Animation/CreatureAnimator.cs:67-78`).
Initial state is `idle_loop` (`Mawler.cs:80`), so the constructor's random
start-phase path runs (`CreatureAnimator.cs:44-59`).

**Mawler's override is `MonsterModel::GenerateAnimator` with one string changed.**
Compare `MonsterModel.cs:602-619` to `Mawler.cs:70-87` line for line: identical
structure, identical trigger set including `Idle`, `cast` → `roar`. Nothing else
differs.

### D.2 Skeleton-resident animations

Schema-blessed verified sources first:

| name | verified how |
|---|---|
| `roar` | `preview_animation = "roar"` — `mawler.tscn:14` |
| `idle_loop` | appears as `from` in two mix rows — `mawler_skel_data.tres:7`, `:12` |
| `hurt` | `to`/`from` in three of the four mix rows — `:8`, `:17`, `:18`, `:21` |
| `die` | `to` in two mix rows — `:13`, `:22` |
| `attack` | **not** named in the mix table or the preview field; verified only as an `AnimState` id (`Mawler.cs:74`) and as a `WithAttackerAnim("Attack", …)` target (`:48`, `:63`) |

Raw-string scan of the `.spskel` (**UNVERIFIED** by schema rule) finds **exactly
five** length-prefixed animation-block names — `attack` (offset 34008), `die`
(45852), `hurt` (64853), `idle_loop` (80729), `roar` (87106) — each preceded by a
correct `len+1` varint. No sixth candidate exists anywhere in the file.

### D.3 Orphans, both directions

**None, in either direction.** The five `AnimState` ids and the five
skeleton-resident names are the same five. That is the cleanest 1:1 in the corpus
so far and is itself the finding: the enemy floor has no `weak_loop`-style
leftovers (contrast the schema's Ironclad example, §2D).

Two consequences fall out of `MonsterModel::GenerateBestiaryMoveList`
(`…/Models/MonsterModel.cs:497-509`), which probes the skeleton for `revive`,
`hurt` and `die`:

- `revive` is **absent** from the skeleton, so Mawler gets no bestiary revive row.
- `hurt` and `die` are present, so Mawler gets bestiary rows carrying
  `TakeDamageSfx` and `DeathSfx` respectively, both `.StopOtherSfx()`.

### D.4 The `Idle` trigger is registered and **never fired** — engine-wide

Mawler registers `AddAnyState("Idle", idle_loop)` (`Mawler.cs:81`), as does
`MonsterModel` (`:613`), `CharacterModel` (`:235`) and every player body. **No
call site in the decompile ever passes `"Idle"` to a trigger.** Method:
enumerated every `SetAnimationTrigger(...)` and `CreatureCmd.TriggerAnim(...)`
call in `sts2src/` — 64 distinct literal trigger names fired, `Idle` not among
them — then enumerated the 14 non-literal call sites and resolved each
(plumbing pass-throughs in `CreatureCmd.cs`/`NCreature.cs`;
`AttackCommand._attackerAnimName`, whose **55** distinct literal values via
`WithAttackerAnim(...)` also exclude `Idle`; and
`Necrobinder.GetSummonAnimIfApplicable`, which returns `"Cast"` or
`"summonTrigger"` — `…/Models.Characters/Necrobinder.cs:124-131`).
`CharacterModel._idleTrigger` (`:25`) is likewise declared and never read.

Return-to-idle is done entirely by `AnimState.NextState` queuing on the same
track (`CreatureAnimator.cs:108-132`), not by a trigger. **A replacement
animation grammar does not need an `Idle` trigger to reproduce base behaviour.**

---

## E. Durations and transitions

From `res://animations/monsters/mawler/mawler_skel_data.tres` (1,068 B packed;
extracted at `…/s16/x/animations/monsters/mawler/mawler_skel_data.tres`):

| from | to | mix | source |
|---|---|---|---|
| *(default)* | *(default)* | **0.05** | `:27` `default_mix` — the house default (schema §2E) |
| `idle_loop` | `hurt` | **0.02** | `:6-9` |
| `idle_loop` | `die` | **0.02** | `:11-14` |
| `hurt` | `hurt` | **0 — instant cut** (no `mix =` line) | `:16-18` |
| `hurt` | `die` | **0 — instant cut** (no `mix =` line) | `:20-22` |

Four rows, two of them deliberate hard cuts. The authoring signal reads clearly:
everything entering a *reaction* from calm is softened to 0.02, and everything
entering a reaction from *another reaction* snaps — re-hitting a flinching enemy
restarts the flinch on frame one, and dying mid-flinch cuts straight to the death
pose. Nothing softens into `attack` or `roar`; those inherit `default_mix` 0.05.

From code — `NextState` chains (`Mawler.cs:77-79`): `roar → idle_loop`,
`attack → idle_loop`, `hurt → idle_loop`. **No `AddBranch` calls at all** (every
registration is `AddAnyState`), so there is no conditional transition on this body.

**Clip durations are UNKNOWN.** They live in the binary `.skel` and the runtime
reads them through `MegaTrackEntry::GetAnimationEnd`
(`CreatureAnimator.cs:52`, `:172`; `NCreature.cs:873-876`). Not estimated.

Two timings that are **not** clip durations and **are** verified — these are the
numbers combat actually waits on:

- attack: `WithAttackerAnim("Attack", **0.35f**)` (`Mawler.cs:48`, `:63`)
- roar: `CreatureCmd.TriggerAnim(Creature, "Cast", **0.5f**)` (`Mawler.cs:56`)

Both are consumed by `CreatureCmd.TriggerAnim`'s tail:
`await Cmd.CustomScaledWait(Mathf.Min(waitTime * 0.5f, 0.25f), waitTime)`
(`…/Commands/CreatureCmd.cs:947`) — a scaled wait between `min(waitTime/2, 0.25)`
and `waitTime`. **The animation length is never consulted for these two tells.**

Idle desynchronisation applies (schema §1.2): random time-scale in `[0.9, 1.1]`
and ±0.1 s phase (`CreatureAnimator.cs:169-174`). Mawler is a **solo** encounter,
so the two-copies-breathing-out-of-step effect is **not observable on this body** —
noted so the `cap-1` slot does not chase it.

---

## F. Intent / attack / hit / death tells

| tell | trigger | state played | who fires it (`file:line`) | blocking? | co-op visible? |
|---|---|---|---|---|---|
| claw (2 hits) | `Attack` | `attack` | `Mawler.cs:62-67` → `AttackCommand.cs:570-573` → `CreatureCmd.cs:946` | yes — `await`ed, scaled wait ≤ 0.35 s (`CreatureCmd.cs:947`) | yes — one shared monster body, all seats see it |
| rip and tear (1 hit) | `Attack` | `attack` | `Mawler.cs:48-51` (same chain) | yes, ≤ 0.35 s | yes |
| roar | `Cast` | `roar` | `Mawler.cs:56` directly | yes, ≤ 0.5 s | yes |
| flinch | `Hit` | `hurt` | `CreatureCmd.cs:325` — only when `damage > 0`, `receiver != dealer`, and **not** `ValueProp.SkipHurtAnim` (`:323`); all such triggers `await Task.WhenAll` at `:337` | yes | yes |
| death | `Dead` | `die` | `NCreature::StartDeathAnim` `:944`, itself called from `CreatureCmd.cs:513` | yes — the returned length gates the reward flow | yes |
| revive | `Revive` | — | `NCreature::StartReviveAnim` `:962` | n/a | n/a — **Mawler registers no `Revive` trigger and the skeleton has no `revive` clip** |

Notes the schema asks for explicitly:

- **Multi-hit:** claw calls `.OnlyPlayAnimOnce()` (`Mawler.cs:64`), which sets
  `_playOnEveryHit = false` (`AttackCommand.cs:466-470`), so the attacker
  animation, attacker VFX and attacker SFX all fire once for two hits
  (`AttackCommand.cs:552`) while `HitSfx` still plays per hit (`:579-582`). One
  lunge, two impacts.
- **`BoundsContainer`:** **not used.** No `AnimState` on this body sets it, so
  `CreatureAnimator.BoundsUpdated` never fires from a state change and the hitbox
  is the static `%Bounds` rect for the whole fight. Mawler's silhouette is
  therefore assumed constant across all five clips — worth an eyes-on check in
  `cap-2`/`cap-3`, because a big roar or a sprawled death pose that exceeds
  510 × 327 would not move the hitbox.
- **Death length source:** the **animation**, not an override. `Mawler` does not
  override `DeathAnimLengthOverride`, so it is the `MonsterModel` default `0f`
  (`MonsterModel.cs:321-323`), `HasDeathAnimLengthOverride` is false (`:323`), and
  `StartDeathAnim` returns `Mathf.Min(GetCurrentAnimationLength(), 30f)`
  (`NCreature.cs:945`, `:954`).
- **Corpse:** removed. `ShouldFadeAfterDeath` is the default `true`
  (`MonsterModel.cs:311`), so `AnimDie` waits
  `min(remaining + 0.5, 20)` s (`NCreature.cs:1006-1010`), spawns
  `NMonsterDeathVfx` (`:1029-1036`) and `QueueFreeSafely()`s the node (`:1053`).
  `ExtraDeathVfxPadding` is the default `1.2 × Vector2.One` (`MonsterModel.cs:173`,
  `:208`) — the death VFX viewport is sized from the spine bounds in the final
  pose, so a death clip that grows the silhouette needs that padding raised, and
  Mawler does not raise it.
- **Intents are not animation states** (schema §1.3). Mawler's three intents
  (`SingleAttackIntent`, `DebuffIntent`, `MultiAttackIntent` —
  `Mawler.cs:32-34`) are `NIntent` nodes parented at `%IntentPos`. The
  frozen-on-death pass is `NCreature.cs:923-926`.

---

## G. VFX and audio hooks

### VFX — everything is command-side; the body contributes nothing

| surface | mechanism | cite |
|---|---|---|
| particle emitters in scene | **none** | `mawler.tscn` (§C) |
| `SpineSlotNode` / `SpineBoneNode` attachment points | **none** | `mawler.tscn` (§C) |
| per-body driver script | **none** — no `NMawlerVfx` exists | `sts2src/MegaCrit.Sts2.Core.Nodes.Vfx/` searched |
| attacker VFX | **none** — both attacks pass `WithAttackerFx(null, AttackSfx)`, VFX slot explicitly null | `Mawler.cs:49`, `:65` |
| hit VFX | `"vfx/vfx_attack_slash"` on both attacks, via `WithHitFx` | `Mawler.cs:50`, `:66` |
| generic damage VFX | `NHitSparkVfx.Create(receiver)` + `NDamageNumVfx` | `CreatureCmd.cs:307-322` |
| death VFX | `NMonsterDeathVfx` fade | `NCreature.cs:1029-1036` |
| in-art slash | the skeleton itself carries an `attack_slash` region **and** a slot of the same name | `.spatlas` region list; `.spskel` slot scan (§C) |

That last row matters: the visible slash on a Mawler attack is **partly baked into
the Spine art** (an `attack_slash` attachment keyed inside the `attack` clip) and
partly a command-spawned `vfx_attack_slash` on the target. A replacement body
that reproduced only the command-side VFX would lose the attacker-side half.

**Spine animation events are inert on this body.** `MegaSprite` exposes an
`animation_event` signal (`…/Bindings.MegaSpine/MegaSprite.cs:18`, `:50-53`), but
every consumer in the game is a per-body `N*Vfx` driver script (`NIroncladVfx`,
`NCeremonialBeastVfx`, `NAxebotVfx`, … — searched: **49** call sites, 48 of them
under `sts2src/MegaCrit.Sts2.Core.Nodes.Vfx/` and the 49th `NSoulNexusVfx.cs`,
i.e. **every one is an `N*Vfx` driver type**). Mawler has no driver, so **no
Spine event on this body reaches any
C# handler.** Its timing surface is trigger-and-wait only (the 0.35 / 0.5 numbers
in §E), never event-driven.

### Audio — the model exposes four paths; **one of them is never played**

| property | resolved value for `mawler` | played from | status |
|---|---|---|---|
| `AttackSfx` | `event:/sfx/enemy/enemy_attacks/mawler/mawler_attack` (`MonsterModel.cs:292`) | `AttackCommand.cs:562-565`, passed explicitly at `Mawler.cs:49`, `:65` | **plays** |
| `CastSfx` | `event:/sfx/enemy/enemy_attacks/mawler/mawler_cast` (`MonsterModel.cs:294`) | — | **never played — see below** |
| `DeathSfx` | `event:/sfx/enemy/enemy_attacks/mawler/mawler_die` (`MonsterModel.cs:296`); `HasDeathSfx` default `true` (`:298`) | `SfxCmd.PlayDeath(monster)` at `NCreature.cs:936-939`, **inside `if (_spineAnimator != null)`** | plays, Spine-gated |
| `HurtSfx` | **null** — `MonsterModel.cs:300` default, not overridden, so `HasHurtSfx` is false (`:302`) | `CreatureCmd.cs:326-329` skipped | no hurt sound |
| `TakeDamageSfx` | `event:/sfx/enemy/enemy_impact_enemy_size/enemy_impact_armor` — `TakeDamageSfxType` is the default `DamageSfxType.Armor` (`MonsterModel.cs:327`, `:329`) | generic damage path | plays |

**The roar is silent.** `RoarMove` calls only
`CreatureCmd.TriggerAnim(Creature, "Cast", 0.5f)` (`Mawler.cs:56`), and
`TriggerAnim`'s SFX switch runs **only `if (creature.IsPlayer)`**
(`CreatureCmd.cs:926-945`). Every other monster that wants a cast sound plays it
itself — `SfxCmd.Play(CastSfx)` appears in `BruteRubyRaider.cs:50`,
`Chomper.cs:80`, `DevotedSculptor.cs:44`, `Entomancer.cs:57`, `Flyconid.cs:58`,
`FuzzyWurmCrawler.cs:86`, `Guardbot.cs:49`, `HauntedShip.cs:74`,
`HunterKiller.cs:53`, `LeafSlimeM.cs:69`, `Noisebot.cs:53`, `PhrogParasite.cs:67`,
`ShrinkerBeetle.cs:48`, `SlimedBerserker.cs:75` and more. **Mawler does not.** Its
inherited `CastSfx` string is computed and never used. Whether the `mawler_cast`
FMOD event even exists in the bank is **UNKNOWN** (banks not opened). This is a
cited observation, not a verdict: it is equally consistent with "no roar sound was
authored" and with "a play call was forgotten." Not ours to rule.

One further observation, flagged and not ruled: a fur-and-teeth beast resolves
`TakeDamageSfx` to the **`Armor`** impact bank while `DamageSfxType.Fur` exists
(`…/Core.Audio/DamageSfxType.cs:5-13`). Base-game content choice; recorded because
S19 joins on exactly these strings.

**S19 join key:** trigger names, per schema §2G — `Attack`, `Cast`, `Hit`, `Dead`.
Note the asymmetry this body demonstrates: `Attack` audio rides the *command*
(`WithAttackerFx`), `Dead` audio rides the *node* (`StartDeathAnim`), `Hit` audio
rides the *model property* (`HasHurtSfx`), and `Cast` audio rides *nothing*. Four
tells, four different owners.

---

## H. Fallback behaviour

| failure | class | what happens | cite |
|---|---|---|---|
| scene missing / fails to load | **HARD** | `CreateVisuals` catches, `Log.Error`, `SentryService.CaptureException`, instantiates `res://scenes/creature_visuals/fallback.tscn` | `MonsterModel.cs:420-437`, path at `:171` |
| a required unique node missing (`%Visuals`, `%Bounds`, `%IntentPos`, `%CenterPos`) | **HARD** | `_Ready`'s `GetNode<T>` throws inside the same `try` → same fallback scene | `NCreatureVisuals.cs:219-223` + `MonsterModel.cs:422-431` |
| skeleton data fails to load (`.skel`/atlas missing or bad) | **SILENT** | `GD.PushWarning("Spine skeleton data failed to load for …, disabling spine animation.")`, `SpineBody = null` → `HasSpineAnimation` false → `NCreature` **never builds an animator** (`NCreature.cs:503-513`). Body renders as an un-animated `SpineSprite`; **no death SFX, death length `0f`** (§F) | `NCreatureVisuals.cs:226-234` |
| an animation name missing from the skeleton | **SILENT** | `SetNextState` logs `could not find '<id>' animation on '<node>'` and **returns without changing the pose**; queued variant logs `… (queued) …` | `CreatureAnimator.cs:88-92`, `:116-120` |
| phobia mode with no `%PhobiaModeVisuals` | **SILENT, benign** | `_phobiaModeBody` is null, the visibility swap is skipped; `HasPhobiaSpineSkin` is the default `false` so `OnPhobiaModeToggled` is a no-op | `NCreatureVisuals.cs:251-263`, `MonsterModel.cs:304`, `:643-653` |
| skin not found | **N/A here** | `SetUpSkin` → `MonsterModel::SetupSkins`, which is an empty virtual and is **not overridden by Mawler** | `NCreatureVisuals.cs:266-276`, `MonsterModel.cs:598-600` |

The middle two rows are the ones a visual-QA gate must catch, and they are the
two that produce **no user-visible error at all** — a body that stands perfectly
still and dies without a sound. Schema §1.4 names the missing-animation case as
the single most important failure mode; this body adds a second of equal weight
(missing skeleton data), because on a body with **zero** scene-side visuals the
two are indistinguishable by eye.

---

## I. Authoring dependency

**What the base game needed to make this body.** Spine (Esoteric Software),
exporter **4.2.43** (from the `.skel` header), producing `mawler.skel` +
`mawler.atlas` + `mawler.png`. Those are consumed by the MegaDot Spine importer
into `SpineSkeletonFileResource` / `SpineAtlasResource` /
`SpineSkeletonDataResource` (the three `[ext_resource]`/`[resource]` types in
`mawler_skel_data.tres:3-4`, `:24-26`), and driven at runtime by
`libspine_godot.windows.template_release.x86_64.dll` in the game directory.
`.import` sidecars ship in the pack alongside the sources
(`mawler.atlas.import` 168 B, `mawler.png.import` 194 B, `mawler.skel.import` 171 B).

**Per charter §4/S16, no Spine purchase or other proprietary authoring dependency
may be PROPOSED as the answer**, and none is proposed here. What is recorded is
the size of the gap, plainly: to match this body a no-paid-tools path would have
to reproduce an ~80-bone hierarchy, ~23 slots, 4 IK chains, ~8 transform
constraints, a path constraint driving a 20-bone tail, region-swap attachments
(the three `drool*` slots sharing one region), a single-page 457 × 1031 atlas, and
five clips whose blend behaviour is expressed as four mix rows. That is the
authoring cost of the game's *simplest* enemy. Whether any of it is *necessary* to
read as an enemy on screen is a different question, and it is Lane A's bake-off to
answer, not this file's.

**What our own pipeline needs, for cost baseline.** A text `.tscn` under
`klee-mod/pck-src/<char>/model/`, script-less by standing rule
(`klee-mod/pck-src/README.md:14-17`), PNG layers living in the gitignored
`ImageGen/` tree and referenced by `res://` path (`:11-13`), a `resource=` line in
the contract list at the bottom of `tools/build_pck.ps1` or `validate.ps1` S6c
fails the deploy (`:18-20`), MegaDot import, `build_pck.ps1`. Behaviour attaches
from C# via BaseLib scene conversion plus Harmony routing — never from a script in
the scene. The authoring tool is a raster editor; there is no rig format.

---

## J. Runtime / performance observables

Static, all fact, all from the pck directory (`…/scratchpad/s16/pck.tsv`) unless
marked:

| artifact | packed bytes |
|---|---|
| `scenes/creature_visuals/mawler.tscn` | 1,204 |
| `animations/monsters/mawler/mawler_skel_data.tres` | 1,068 |
| `.godot/imported/mawler.skel-…spskel` | 102,607 |
| `.godot/imported/mawler.png-…ctex` | 260,532 |
| `.godot/imported/mawler.atlas-…spatlas` | 1,152 |
| three `.import` sidecars | 533 |
| **total body footprint** | **367,096 B ≈ 358 KiB** |

Ratios worth carrying to the matrix: the scene is **0.33 %** of the body; the
texture is **71 %**; the skeleton is **28 %**. Textures are **private** to this
body — the atlas is a single page named `mawler.png` and nothing else in the pack
references it. Materials affecting draw: **0** in the scene. Emitters: **0**, so
no `amount` to report.

**Comparison to our own layered rig — same measurement, different pack, not a
controlled comparison.** Read read-only from the deployed
`…\Slay the Spire 2\mods\klee\klee.pck` (mod `0.2-1155`; the file was listed, not
modified, and the game was not launched). Klee's combat body resolves through
`klee/model/combat.tscn.remap` to `export-a0975a521cfd81b181c1575f7747fdee-combat.scn`
= 13,663 B, plus five imported layer textures — `klee_combat_body` 27,766,
`klee_combat_dumpty` 16,058, `klee_combat_floaters` 24,798, `klee_combat_smoke`
23,768, `klee_combat_dodoco` 2,866 — for **108,919 B ≈ 106 KiB**. So our layered
five-layer player rig is roughly **a third the packed size** of the base game's
simplest enemy, and its scene is **11×** larger while its art is **3×** smaller.
Different character, different on-screen size, different art budget: this is a
shape observation, not a quality one.

**Dynamic observables — UNKNOWN, capture pending.** Draw calls, frame cost, load
time, actual on-screen silhouette against the 510 × 327 `%Bounds` rect. Never
guessed (schema §2J).

---

## K. Three annotated capture slots — **CAPTURE PENDING**

No captures tonight: [USER] is playtesting mod `0.2-1155` and no agent may launch,
deploy to, or touch the game installation (PREFLIGHT, *Deployed mod*).

### `cap-1` — idle

- `status:` capture pending
- `blocked_by:` [USER] playtest — no game launch (PREFLIGHT)
- `how_to_capture:` attended session, fresh save (`NumberOfRuns == 0`) so
  `Overgrowth` pins `MawlerNormal` to normal-encounter slot 5 (`Overgrowth.cs:119`);
  enter the fight, hold on the first player turn; still frame + 3 s clip.
- `what_it_would_settle:` where the rendered silhouette sits inside the
  510 × 327 `%Bounds` rect and whether `IntentPos (0, −328)` clears the head at
  `Visuals` scale 0.25. **Loop desync is NOT observable here** — solo encounter,
  one body (§E); do not chase it on this slot.

### `cap-2` — the roar (the signature tell)

- `status:` capture pending
- `blocked_by:` [USER] playtest — no game launch (PREFLIGHT)
- `how_to_capture:` same fight; the roar arrives on turn 2 with 50 % probability
  and by turn 4 with 87.5 % (`docs/current/dossiers/enemies/mawler.md:57-65`), and
  fires exactly once per combat. Clip from the `Cast` trigger to return-to-idle.
- `what_it_would_settle:` the `roar` clip's real duration against the fixed
  `0.5 s` wait (`Mawler.cs:56`) — i.e. whether combat resumes before the roar
  finishes; whether the silhouette exceeds `%Bounds` (no `BoundsContainer`, §F);
  and **whether any sound plays**, which is the direct eyes-on/ears-on test of the
  silent-roar finding in §G.

### `cap-3` — hit → death

- `status:` capture pending
- `blocked_by:` [USER] playtest — no game launch (PREFLIGHT)
- `how_to_capture:` same fight; land a non-killing hit, then the killing blow.
  Clip covering `Hit` then `Dead` through corpse removal.
- `what_it_would_settle:` the two instant cuts in §E made visible
  (`hurt → hurt` re-hit snap; `hurt → die` snap when the killing blow lands during
  a flinch); whether the `die` clip length matches the reward-screen delay
  (`min(GetCurrentAnimationLength(), 30)`, `NCreature.cs:945`, `:954`); the
  `NMonsterDeathVfx` fade and `QueueFree` (`:1029-1053`); and presence of the
  `mawler_die` sound.

**A capture-pending slot is a complete answer for tonight.** No frame was
described that was not seen.

---

## L. Closing sections

### 1. UNKNOWN

| question | what would answer it |
|---|---|
| Clip durations for `idle_loop`, `roar`, `attack`, `hurt`, `die` | a Spine 4.2 binary parser over the `.spskel`, or `cap-2`/`cap-3` timed against a frame counter |
| Exact bone / slot / constraint counts | same parser; the §C figures are string-scan estimates and are marked `UNVERIFIED` |
| Does the FMOD event `event:/sfx/enemy/enemy_attacks/mawler/mawler_cast` exist in the bank? | open the FMOD banks in the game directory, or `cap-2` (ears-on) |
| Do the `attack`/`roar` clips carry Spine events? | the same parser; behaviourally moot — no listener exists on this body (§G) |
| Does any clip change the silhouette beyond `%Bounds`? | `cap-2` / `cap-3` |
| On-screen size, draw calls, frame cost, load time | attended capture with a profiler |
| Whether BaseLib exposes a monster-registration seam at all | out of scope here; that is S13's socket table and Lane D's go/no-go |

### 2. NON-FINDINGS

Each is a thing looked for and genuinely absent, with the boundary searched.

1. **No per-body VFX driver for Mawler.** Searched all of
   `sts2src/MegaCrit.Sts2.Core.Nodes.Vfx/`: no `NMawlerVfx`. 49 `N*Vfx` driver
   types wire a Spine `animation_event` handler for other bodies (§G).
2. **No particles, no bone/slot nodes, no materials, no scripts** in
   `mawler.tscn` beyond the shared `NCreatureVisuals`. Whole file read (37 lines).
3. **No `revive` clip and no `Revive` trigger** on this body. `AnimState` list
   read in full (`Mawler.cs:70-87`); skeleton scanned for `revive` — zero hits.
4. **No `stun`, `cast`, or any sixth animation** in the skeleton. Same scan:
   zero hits for `stun` and `cast`; exactly five length-prefixed animation names.
5. **No conditional branches and no `BoundsContainer`** anywhere on this body —
   the machinery of `AnimState.cs:45`, `:54-82` is entirely unused here.
6. **The `"Idle"` trigger is never fired anywhere in the base game.** Boundary:
   every `SetAnimationTrigger`/`TriggerAnim` call in `sts2src/` (64 literal names
   enumerated, 14 non-literal call sites individually resolved) plus every
   `WithAttackerAnim` literal (21 names). See §D.4.
7. **Our mod ships no enemy body of any kind.** `klee-mod/pck-src/` contains
   exactly two creature bodies, both players (`klee/model/combat.tscn`,
   `furina/model/combat.tscn`); `klee-mod/KleeCode/` contains **zero** files
   mentioning `MonsterModel` or `EncounterModel` (searched `--include=*.cs`).
   There is therefore no prior art on our side for the body this file describes.

### 3. Transfer questions — questions only, against our BaseLib/Harmony path (schema §1.5)

1. Our router maps seven game triggers onto four `AnimationTree` states, folding
   `Cast` and `PowerUp` into `attack` (`klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs:45-54`).
   Mawler's whole identity is that its `Cast` slot is a **bespoke, non-attack**
   tell (`roar`). If a modded enemy ever needs a distinct fifth state, does the
   router grow a fifth mapping, or does the scene contract grow a per-body
   override table? Which of those is one change and which is N changes?
2. The base game says **`die`**; our scenes say **`death`** (schema §1.5). If a
   future gate cross-checks a mod scene's state names against base convention,
   which spelling is authoritative for a *mod* body, and who owns that call?
3. Death is special-cased in our patch pair because `StartDeathAnim` only emits
   `"Dead"` when a Spine animator exists (`CreatureAnimationRouter.cs:92-103`).
   The same gate also swallows the **death SFX** and returns length `0f`
   (`NCreature.cs:933-954`, §F). Our patch restores the *animation*. Is the
   missing death sound and the zero-length reward delay a known accepted gap for
   spine-less bodies, or an unfiled defect?
4. `AnimState.NextState` queues a follow-on clip **on the same track**
   (`CreatureAnimator.cs:114-132`); our router calls `playback.Travel(state)` on
   an `AnimationTree` state machine, where return-to-idle is a scene-authored
   transition. Are those two return-to-idle semantics equivalent under
   interruption — a `Hit` landing mid-`attack`, or a `Dead` landing mid-`hurt`,
   which the base game handles as an instant cut (§E)?
5. Mawler's tells wait on **fixed constants** (0.35 / 0.5 s), never on clip
   length, and its only length-dependent moment is death. Does that make a
   fixed-duration authoring target sufficient for a modded enemy's non-death
   tells — and if so, what would a QA gate assert, given that a body with a
   frozen pose and a correct wait time is indistinguishable from a working one
   (§H)?
6. Mawler's visible slash is **split** between a skeleton attachment
   (`attack_slash`) and a command-spawned `vfx_attack_slash` (§G). For a layered
   rig, does the attacker-side half belong in the sprite layers, in a scene
   particle node, or in C#? Which of those our pipeline can currently express is
   not established here.
7. Spine `animation_event` reaches C# only through a per-body driver script, and
   our scenes are script-less by rule (`pck-src/README.md:14-17`). If a modded
   body ever needs frame-accurate event callbacks, what is the script-less
   equivalent — an `AnimationPlayer` method track, a Harmony hook, or something
   else?
8. §C's ~80 bones versus our five sprite layers is the real bake-off gap. Which
   of the ~13 constraints (IK chains, the path-driven tail, the rotation locks)
   have *any* expression in an `AnimationTree` + `Sprite2D` rig, and which are
   simply unavailable? This file establishes the base-game requirement; it does
   not answer the question.

### 4. What this does NOT establish

This file describes one enemy body as it is built and driven in the shipped game.
It does **not** say that Mawler will be reskinned, remapped, replaced, or used as
Lane D's target; it does not rank layered sprites against skeletal 2D or against
anything else; it does not propose an animation approach, a tool, a purchase, or
a budget; and it does not rule on the two base-game oddities it records (the
never-played `CastSfx` and the `Armor` impact type on a fur beast) — both are
reported as cited observations for [USER], not as defects to fix. Nothing here was
seen on screen: the game was never launched, no frame was captured, and every
clip duration, bone count and runtime cost stays UNKNOWN or UNVERIFIED exactly as
marked. The size comparison to Klee's rig in §J is a shape observation between two
different characters in two different packs, not a controlled measurement.

---

## M. Two corrections to the schema's own text

Schema §1 instructs a corpus file that **contradicts** the shared grammar to say
so loudly. Neither correction below is in §1 itself — both are in the §5.3
rationale for picking this body — but the same rule applies, and the body pick is
unaffected: Mawler remains the right normal-enemy corpus body for every reason
§5.3 gives about reachability, solo capture, and floor-sized scene.

**M.1 — "the single most common variation in the whole monster corpus" is not
supported by a count.** Schema §5.3 describes Mawler's animator override as *"the
single most common variation in the whole monster corpus — rename `cast` to a
bespoke idle-adjacent tell (`roar`) and change nothing else."* Classifying every
file in `sts2src/MegaCrit.Sts2.Core.Models.Monsters/` (121 files; method: regex
over each `GenerateAnimator` body counting `new AnimState("…")` ids,
`AddAnyState("…")` triggers, and `AddBranch` presence — a heuristic classifier,
declared as such):

| shape | count |
|---|---|
| bespoke triggers and/or per-state branches | **66** |
| **no override at all** — pure `MonsterModel` default | **39** |
| 5 states, default triggers only, one renamed tell | **9** |
| default triggers only, other state count | **7** |

So the most common thing a monster does is carry **bespoke triggers** (66 of 121),
and the most common thing it does *to the default animator* is **nothing at all**
(39). The rename-only family is 9 of the 82 overriding files (11 %) — it is the
largest *minimal* variation, which is probably what §5.3 meant, but it is not the
most common variation. The nine: `BowlbugEgg`/`BowlbugSilk` (`spit`),
`CalcifiedCultist`/`DampCultist`/`SewerClam` (`buff`), `Mawler` (`roar`),
`Nibbit` (`hiss`), `TheForgotten`/`TheLost` (`debuff`). (Caveat: the 121 files
include debug and deprecated stubs — `BigDummy`, `OneHpMonster`, `TenHpMonster`,
`DeprecatedMonster`, `SingleAttackMoveMonster`, `MultiAttackMoveMonster` — which
inflate the "no override" bucket; the ranking is unchanged if they are removed.)

**M.2 — a sharper true statement is available, and it is the better reason to
pick this body.** Of those nine, **only Mawler and `SewerClam` also re-register
the `Idle` trigger**, which the `MonsterModel` default does (`:613`). Every other
member drops it — `Nibbit.cs:117-133` registers only `Cast`/`Attack`/`Dead`/`Hit`.
So Mawler is one of exactly **two** monster bodies in the game whose animator is
`MonsterModel::GenerateAnimator` **verbatim with one string changed**. That is a
stronger and more useful claim than the one §5.3 makes, and it is the precise
sense in which this body is the enemy floor. Combined with §D.4 — the `Idle`
trigger being dead engine-wide — Mawler's animator is, behaviourally, the base
monster animator exactly.

Nothing in either correction changes the schema's evidence contract, the four-body
split, or the ownership map. Recorded so the matrix integrator (§3, `s16-05-matrix.md`)
does not carry the "most common variation" phrasing forward as established.
