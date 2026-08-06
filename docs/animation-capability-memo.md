# Animation capability memo — north-star v0.2

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

**Date:** 2026-08-05 · **Track F1, findings-only.** Options with costs. Nothing
here is a decision, a recommendation of a technology, or a pipeline change. No
game process was launched; every measurement is an offline read of
`SlayTheSpire2.pck`, the shipped DLLs, and the repo.

Builds on `docs/s5-animation-tech-note.md` (which established *what the base
game uses*) and answers the next question: *what could we use, and what would
each cost per entity.*

---

## 0. The three paths in one line each

| Path | Licence | Authoring tool | Proven where |
|---|---|---|---|
| **A — Spine** | Spine Editor, **per person**; mesh deform needs **Professional** | Spine Editor (not owned) | 101/101 base-game monster rigs |
| **B — Godot-native `Skeleton2D` + `Polygon2D` deform** | **$0** | MegaDot 4.5.1 editor (**already owned**) | **Nowhere.** Zero instances in the base game, zero in our mod |
| **C — layered `Sprite2D` + `AnimationPlayer`/`AnimationTree`** | **$0** | scripted cut + text `.tscn` (**already built**) | Klee and Furina, in production today |

---

## 1. Path A — Spine

### 1a. Evidence that it works here

The strongest possible: the entire shipped bestiary is this and nothing else.
`animations/monsters/` holds 101 rig folders, every one of them
`.skel` + `.atlas` + `.png` + `_skel_data.tres`; the pack carries 163 imported
`.spskel` and 169 `.spatlas`; `scenes/creature_visuals/*.tscn` contain 131
`SpineSprite` and **zero** `AnimatedSprite2D`, `Skeleton2D` or `AnimationPlayer`
(all from S5). Skeleton binaries carry `4.2.43` in their header. The runtime
`.dll` ships in the game root and would be loaded, not redistributed, by a mod.

### 1b. What a base-game rig actually contains — measured tonight

Parsed directly out of the pack: the Spine 4.2 binary header (hash → version
string → `x, y, width, height, referenceScale` → nonessential flag → `fps`,
images path, audio path → string table → bone count) plus a text parse of each
`.spatlas`. **83 of 91 rigs parse cleanly and self-report `4.2.43`**; of the
remaining eight, two report older point releases (`4.2.08`, `4.2.38`) and six
exceed the header reader's tolerance and were dropped rather than guessed at.

| Measure | min | p25 | median | p75 | max |
|---|---:|---:|---:|---:|---:|
| Bones per rig (n=83) | 6 | 41 | **64** | 107 | 264 |
| Atlas regions per rig (n=83) | 4 | 20 | **28** | 45 | 99 |
| `.skel` bytes (n=91) | 5.4 KB | 83 KB | **138 KB** | 198 KB | 1.11 MB |
| Imported texture bytes (n=91) | 19 KB | — | **153 KB** | — | 5.3 MB |

Worked example, the enemy from tonight's other track: `punch_construct` —
**54 bones, 44 atlas regions**, one 1307×207 atlas page, 165 KB skeleton,
30 fps, 570×1154 authoring box. Its `_skel_data.tres` names the clip graph
(`idle_loop`, `hurt`, `die`, with four explicit `SpineAnimationMix` pairs and
`default_mix = 0.05`).

**Read that as the cost floor, not the ceiling.** A median rig is 64 bones and
28 separately-drawn pieces of art. That is a character rig built by someone
whose job is rigging.

### 1c. Licence cost

From S5, sourced to Esoteric's own agreements:

- Runtime redistribution: **clean.** The game ships `libspine_godot...dll`; a
  mod adds no runtime binary.
- Authoring: **one Editor licence per person who creates or modifies the rig.**
  The Runtimes agreement defers to §2 of the Editor agreement; §2.4 extends it
  per-person and the SDK carve-out says explicitly that each user of a library
  must obtain a licence. No free, non-commercial or hobby exemption exists, and
  there is no licence-clean free exporter — producing a `.skel`/`.atlas` at all
  requires the Editor.
- Tiers: **Essential from ~$69**, one-time. **Professional is required for
  meshes**, and every shipped enemy rig uses them; Professional is priced
  higher with upgrade-by-difference. *(The exact Professional figure was not
  re-verified offline tonight and is deliberately not quoted.)* Both tiers are
  available only while trailing-12-month gross revenue/financing is under
  $500k USD; above that, Enterprise.

**Dollar line: ~$69 minimum per person for a mesh-less rig; Professional per
person for anything matching what the base game ships.**

### 1d. A blocker that is not licence money — found tonight

`addons/spine/spine_godot_extension.gdextension` declares four Windows
binaries, including `windows.editor.x86_64 = libspine_godot.windows.editor.x86_64.dll`.

**Only `template_release` ships with the game.** There is no editor build of
the extension in the game directory, and none in
`megadot-4.5.1-m.14-.../` — the MegaDot editor our pipeline drives has no spine
support at all (`find -iname "*spine*"` over the editor install: zero hits).

This matters because of how our pack is produced. `tools/build_pck.ps1` runs
`MegaDot --headless --import` and then `--export-pack`, and the importers used
for spine assets are **`importer="spine.skel"` and `importer="spine.atlas"`**,
which are registered *by the extension*. Without a spine-enabled editor binary,
**our pipeline cannot import a Spine rig — the pack build fails before any
question of how the rig looks.**

Resolving it means obtaining or building `libspine_godot` against the
**MegaDot 4.5.1 fork's** ABI, not stock Godot 4.5. That is unquantified
engineering, it is a prerequisite to the *first* rig rather than a per-entity
cost, and it is the single largest unknown on this path.

### 1e. Cost per entity — Path A

| Component | Range | Evidence for the bound |
|---|---|---|
| Licence, one-off per person | **~$69 → Professional tier** | §1c; Professional is not optional if meshes are used, and 100% of shipped rigs use them |
| Pipeline enablement, one-off | **unknown; non-zero and possibly large** | §1d — no editor extension exists for MegaDot 4.5.1 on this machine |
| Authoring, per entity | **~1 day (low) → 5–10 days (base-game parity)** | Low bound = the `infested_purifier` class: 6 bones, 4 regions, 5.5 KB. High bound = the median rig, 64 bones / 28 regions, which is professional character-rig work. We have no in-house Spine hours to calibrate against, so the range is deliberately wide |
| Runtime risk | **low, once loading works** | The runtime is the game's own, exercised 101 times per install |

---

## 2. Path B — Godot-native `Skeleton2D` + `Polygon2D` mesh deform

### 2a. Does spine-godot's presence constrain us? No — measured

Two independent findings say the engine does not care:

1. **`NCreatureVisuals` binds children by NAME, not by type** (S5, load-bearing
   find). The contract is the node names `Visuals`, `Bounds`, `CenterPos`,
   `IntentPos`. It is satisfied today by base-game placeholder scenes whose
   `Visuals` is a plain `Sprite2D` (`fallback.tscn`, the three
   `the_adversary_mk_*` scenes, `crusher.tscn`), and it is satisfied in
   production by our two scenes, whose `Visuals` is a plain `Node2D`.
2. **Our shipped scenes already prove the seat.** `combat.tscn` for both Klee
   and Furina is `Node2D → Visuals(Node2D) → Facing(Node2D) → Rig(Node2D) →`
   4–5 `Sprite2D`, plus `Bounds`, `CenterPos`, `IntentPos`, `AnimationPlayer`,
   `AnimationTree`. **Zero `SpineSprite`.** They load, animate and take hits.

A `Skeleton2D` under a correctly-named `Visuals` therefore seats exactly as a
`Sprite2D` does. The GDExtension is additive; nothing routes creature visuals
through it.

Two real constraints, neither from spine:

- **`_spineAnimator` is the game's only animation channel.** `NCreature` builds
  it only when `Visuals.HasSpineAnimation`, so for any non-spine visual
  `SetAnimationTrigger` is a guaranteed no-op. This is already solved: our
  Harmony postfix pair in `klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs`
  routes triggers into `%AnimationTree` instead, is character-agnostic by
  construction, and is inert for any visual lacking that node. **Path B and
  Path C share this plumbing unchanged.**
- **No scripts in scenes** (`klee-mod/pck-src/README.md`). `Skeleton2D` /
  `Bone2D` / `Polygon2D` bone weights and `AnimationPlayer` bone tracks are all
  declarative `.tscn` data, so the rule is satisfiable — but it has never been
  exercised, and it is exactly the kind of rule that turns out to bite at
  import time rather than at authoring time.

### 2b. Cost per entity — Path B

| Component | Range | Evidence for the bound |
|---|---|---|
| Licence | **$0** | No third-party tool; the MegaDot 4.5.1 editor is already installed and already drives the pack build |
| Pipeline enablement, one-off | **low, but unproven** | The importer for a `.tscn` with `Skeleton2D` is Godot's own scene importer, already used for our five-clip scenes. Nothing new must be obtained. But **zero instances exist** in the base game or our mod, so "low" is an inference, not a measurement |
| Authoring, per entity | **~1 day (low) → 3+ days (high)** | Low bound anchors on Path C's measured first-cut cost (§3b) plus bone-painting on the same layer masks. High bound is wide *because there is no in-house instance*: weight-painting is hand work in a GUI, and our pipeline has never done hand work in the Godot editor for a shipped asset |
| Runtime risk | **low–medium** | The nodes are core Godot, but a `Polygon2D`-deform rig is a scene shape neither MegaDot's headless import nor BaseLib's scene conversion has ever seen from us |

**The honest summary of Path B: it is the only path with no licence and no
tooling gap, and it is also the only path with no working example anywhere in
reach — not in the base game, not in our repo.** Its cost range is wide for
that reason and cannot be narrowed without building one.

---

## 3. Path C — layered `Sprite2D` + `AnimationPlayer` / `AnimationTree`

### 3a. What is already shipped

Two characters, in production, through one generalized tool.

- `tools/cut_combat_layers.py <character>` (375 lines) — fences, hard
  partition, inpaint, export — reading a per-character fence config from
  `tools/combat_layer_fences/` (`klee.yaml` 86 lines, `furina.yaml` 120 lines).
- Klee: 5 layers cut from one 1069×1245 splash (smoke / floaters / dumpty /
  body / dodoco). Furina: 4 (coat-back / sword / body / hat).
- Each `combat.tscn` is ~15 KB of text carrying **5 `Animation` sub-resources**
  (RESET, idle, attack, hurt, death) and a 4-state `AnimationTreeStateMachine`
  — `states/idle`, `states/attack`, `states/hurt`, `states/death`.
- Method is fully scripted: alpha connected components, hand-digitized fence
  polylines + flood fill, priority dilation for outline pixels, edge-extension
  onion-peel inpainting sized so worst-case idle motion never reveals a hole.
  `--check` asserts byte-identical re-generation (12/12 outputs for Klee).

### 3b. Cost per entity — Path C

| Component | Range | Evidence for the bound |
|---|---|---|
| Licence | **$0** | No tool beyond the repo |
| Pipeline enablement | **$0, done** | Two characters through it; the cut tool was generalized on the second and proved byte-identical on the first |
| Authoring, first cut | **~0.5 → 1.5 days** | The per-character delta is one fence config (86–120 lines), 3–5 layer masks, and 5 clips. The manifest's original "an afternoon of work" is the low bound and it is a *pre-shipping estimate*; the two real characters are the high bound |
| **Review iteration** | **2–4 rounds, and this is where the hours actually are** | Measured from the record: animation sprint 1 shipped Klee's rig, and its D4 / C4-Encore / badge deliverables came back FAILED and were **rebuilt in sprint 2**; playtest 1 then produced **three** defects (ribbon number, character icon, facing) and playtest 2 **two more** findings. Four review rounds across two characters is the observed rate |
| Runtime risk | **lowest of the three** | It is what is running now |
| Ceiling | **rigid bodies; no deformation** | Layers translate, rotate, scale and modulate. A limb cannot bend. Klee's cut is explicit that a head cut "runs through hair overlaps and buys visible seams for a weak effect" |

**The cost of Path C is not the rig. It is the review loop**, and the review
loop is the same size on Paths A and B — plus their authoring cost, not
instead of it.

---

## 4. Cost table, consolidated

Per entity, unless marked one-off. Ranges, with §-references to the evidence.

| | **A — Spine** | **B — Skeleton2D** | **C — layered Sprite2D** |
|---|---|---|---|
| Licence $ (per person, one-off) | **~$69 → Professional tier** (§1c) | **$0** | **$0** |
| Tooling gap (one-off) | **BLOCKER: no spine editor extension for MegaDot 4.5.1** (§1d) | none known, unproven (§2b) | none — shipped (§3a) |
| Authoring hours class | **1 day → 5–10 days** (§1e) | **1 day → 3+ days** (§2b) | **0.5 → 1.5 days** (§3b) |
| Review rounds (all paths) | 2–4 (§3b) | 2–4 (§3b) | **2–4, measured** (§3b) |
| Runtime risk | low once loading works | low–medium | lowest |
| Visual ceiling | base-game parity (median 64 bones / 28 regions, §1b) | true deformation, unproven | rigid layers only (§3b) |
| Working example in reach | 101 (base game) | **0** | 2 (ours) |

---

## 5. Kokomi as pilot

Framed as asked: **a recommended pilot for whichever path [USER] picks — not a
vote for a path.**

The evidence that she is the pilot-shaped entity:

1. **She is the only one of our three characters without a layered combat
   rig.** Klee and Furina each have a `pck-src/<char>/model/combat.tscn` with
   its fence config. Kokomi has neither. Her combat model is
   `model/combat_model.png`, a **static 240×280 still** produced by
   `tools/gen_kokomi_stills.py` (`docs/kokomi-art-pass-requirements.md` §5a).
   Whichever path is chosen, she is the entity where the delta between "before"
   and "after" is largest and cleanest to judge.
2. **Her open art item is already the live one.** Track D — 58 card faces + 15
   companion faces awaiting the [USER] taste pass
   (`docs/kokomi-playtest-protocol.md`, `docs/open-playtest-items.md` §6.1).
   A rig pilot lands in a stream that is already open rather than opening a new
   one.
3. **Her source art is already prepared to the point every path needs.** The
   4900×5700 Portrait has a solved cutout (`cutout_from_plate`, keyed by
   connectivity rather than colour, because she wears white on white) and a
   solved head-centring rule (median alpha column, chosen over the min/max
   midpoint on measured evidence). All three paths start from a clean
   transparent full-body figure; hers exists.
4. **Her shell track is DONE and pinned**, so a rig change cannot be confused
   with a shell change: eight non-card surfaces shipped 2026-07-25, all but one
   registered in `art_lint.GENERATOR_OWNED` under L11.
5. **She has never been seen in-game with her own combat model.** The protocol
   records it as shipped with "**no eyes on it in-game**". A pilot would be
   collecting a first look either way.

The counter-consideration, recorded rather than buried: she is also the
character with the thinnest source pool (the scarcity ruling and its correction,
`docs/kokomi-art-pass-requirements.md` §2), and Path A's atlas-region median of
28 separately-drawn pieces is a *drawing* bill, not a rigging bill. If a Spine
rig is what gets piloted, her source scarcity is a cost the other two characters
would not pay.

---

## 6. What a real prototype needs that tonight could not verify offline

Explicitly enumerated. None of these are inferable from a pck read.

**All paths**

1. **In-engine load of a custom creature skeleton.** Nothing here proves a
   non-`Sprite2D` `Visuals` child survives `NCreatureVisuals`' name-based bind
   *at runtime*. The name-not-type finding is read from scene structure and
   from placeholder scenes, not from a load.
2. **BaseLib scene conversion of a new scene shape.** Our conversion registry is
   path-keyed and every registered scene to date is layered `Sprite2D`.
3. **`build_pck.ps1` round-trip.** `--headless --import` must import the new
   scene without an `ERROR` line — the script throws on any — and `validate.ps1`
   S6c must find the resource in the staged contract.
4. **Look, at combat scale.** Every measurement above is structural. Whether a
   rig reads as alive at a 240×280 shipped box is a taste pass, and taste passes
   are [USER]'s.
5. **Timing against `AttackAnimDelay` / `CastAnimDelay`.** Damage sync is a
   played-frame question.

**Path A only**

6. **That a spine-enabled MegaDot 4.5.1 editor binary can be obtained or
   built at all.** This is the gate on everything else in Path A (§1d).
7. **That a self-authored `.skel` at `4.2.43` imports and plays** through the
   shipped runtime — our rigs would be authored in a Spine Editor version we do
   not yet own, against a runtime we cannot rebuild.
8. **Actual licence tier prices**, re-verified at purchase time. Only the
   ~$69 Essential floor is carried here, and the tier structure can move.

**Path B only**

9. **That `Polygon2D` bone weights survive headless import and pack export.**
   Zero instances exist anywhere in reach to copy from.
10. **Mesh deform on our own art** — specifically whether a cut-from-splash
    layer, which is a flat painted region rather than art drawn for
    deformation, tolerates weighting without tearing. This is the single
    largest unknown on Path B and it is unanswerable without doing it once.
11. **Whether hand weight-painting in the MegaDot GUI is reproducible.** Every
    art artefact we ship today is regenerable from a committed script
    (`--check` byte-identical). A hand-painted rig is the first asset that
    would not be, which is a pipeline-invariant question, not an art question.

**Path C only**

12. Nothing. It is the only path with no open verification — which is a fact
    about how much it has already been paid for, not an argument.
