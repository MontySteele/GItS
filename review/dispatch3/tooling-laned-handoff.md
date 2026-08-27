# Lane D handoff — neutral enemy seam (surplus-dispatch-3, 2026-08-26)

> **This decides nothing.** It is a spike on a branch. Nothing merged, nothing
> deployed, nothing packed, and the game was never launched — you were
> playtesting `0.2-1155` the whole time. Whether any base enemy should ever be
> re-presented, which one, and what it should look like are all yours; the
> questions are numbered at the bottom.

**Branch:** `dispatch3-laneD-enemy-seam`, worktree
`C:\Users\Monty\Documents\GitHub\GItS-laneD`, branched from `main` at
`c09b6b6`.

*Note on the base commit:* the dispatch preflight recorded `main` at `223a4ff`,
but by the time this lane started `main` was `c09b6b6` (PR #108, the Kokomi
icons, had merged). The branch is from the newer one.

---

## 1. The one-paragraph version

The charter asked whether one ordinary enemy's *presentation* can be replaced
with original art while its mechanics and every base resource stay untouched.
**It can, and this branch does it** — with a Harmony prefix on the one engine
member that produces a monster's scene path, a second prefix on the one that
builds the node, and a proof scene made of shapes drawn as coordinates in a
text file. The evidence is offline: the spike is armed against the real game
assembly in a bare .NET process, and the path is then read back on **all 120
concrete monsters in the base game**. One changes. 119 do not. Nothing was
rendered, because rendering needs Godot and Godot needs the game.

---

## 2. What was built

Everything lives in one lane-owned directory,
`klee-mod/spikes/lane-d-enemy-seam/`, plus one new test file. No shared build
script, no `docs/current/`, no sheet, no constant, no production asset was
touched.

| File | What it is |
|---|---|
| `EnemySeamSpike/NeutralEnemySeam.cs` | The seam. Two Harmony prefixes, one monster id, one namespaced scene path. |
| `EnemySeamSpike/SeamBootstrap.cs` | Arms patches one class at a time and reports what armed, in the same shape as the mod's own `KleePatchBootstrap`. |
| `bitecheck/Program.cs` | The evidence harness. Runs the seam against the real `sts2.dll` outside Godot and sweeps every monster. |
| `pck-src/laned/creature_visuals/proof_prism.tscn` | The proof art. |
| `README.md`, `BUILD-PCK-PATCH-NOTE.md` | How to run it; what a shared-file change would be if you ever want one. |
| `tier0/tests/test_lane_d_enemy_seam.py` | 20 tests, runs anywhere, no game install needed. |

### The art

A "prism sentinel": a hexagonal base plate, a five-sided gem body, a crown
triangle, two floating shards, and a slit visor, with a slow idle bob and a
pulsing visor. **Every shape is a `Polygon2D` whose vertices are written out in
the scene file.** There is no texture, no image import, no external resource of
any kind, and nothing traced or derived from Slay the Spire 2, from Genshin, or
from anywhere else. That was deliberate: a proof of a rendering seam should not
smuggle a rights question into the morning, and coordinates in a file are the
cheapest way to make "we drew this" checkable rather than assertable.

It is deliberately abstract. It is proof geometry, not a design proposal, and
it looks nothing like the enemy it stands in for.

### The seam, in plain terms

A monster's art is found through one property, `MonsterModel.VisualsPath`,
which by default builds a path out of the monster's own id. The spike
intercepts that property, and *only* when the monster's id is the one named in
a single constant, hands back a different path — one inside the mod's own
folder. Every other monster falls straight through to the base game's answer.

Two things make that safe rather than clever:

- **The base file is never replaced.** The mod serves a *different string*
  (`res://laned/…`), not a different file at the base path. This matters more
  than it sounds: Godot's pack loader replaces colliding paths outright, so a
  mod that packed the base path would swap that enemy's art for **every** run
  of the game, not just ours, and it would look identical in play to doing it
  correctly. There is a test whose whole job is to make that mistake fail.
- **The mechanics are unreachable from here.** HP, the move state machine,
  intents, damage and rewards never read the visuals path. The seam produces a
  picture and nothing else. A test asserts the spike's source cannot even name
  the mechanics types.

---

## 3. Exact commands

Run from the lane worktree, `C:\Users\Monty\Documents\GitHub\GItS-laneD`.

```sh
# 1. the automated gate (no game install needed)
PYTHONPATH=. python -m pytest tier0/tests/test_lane_d_enemy_seam.py -q

# 2. the mod's existing C#-contract gates, to show nothing else moved
PYTHONPATH=. python -m pytest \
  tier0/tests/test_roster_runtime_contracts.py \
  tier0/tests/test_harmony_bootstrap_contract.py \
  tier0/tests/test_creature_facing_contract.py \
  tier0/tests/test_canonical_model_misuse.py -q

# 3. the pre-push lint lane
python tools/run_lints.py --lane ci

# 4. build the spike
cd klee-mod/spikes/lane-d-enemy-seam/EnemySeamSpike && dotnet build

# 5. build + run the offline evidence harness (needs the Steam install)
cd klee-mod/spikes/lane-d-enemy-seam/bitecheck && dotnet build
./bin/Debug/laned-seam-bitecheck.exe
```

`klee-mod/local.props` had to be created in this worktree (it is gitignored and
per-machine). It is a verbatim copy of `local.props.example`, which already
carries your paths.

**One environment note, not a repo problem.** Running the whole suite from this
agent's shell, four `tier0/tests/test_art_coverage.py` tests fail with
`OSError: [WinError 6] The handle is invalid` out of `subprocess._get_handles`.
They fail in a run that touches no Lane D file, and they pass with
`--capture=sys` or `-s` — pytest's default fd-level capture leaves stderr
without an inheritable handle in this shell, and those four are the only tests
that shell out. `pytest -n auto` fails the same way here, which is why the
runs used `--capture=sys` and no xdist:

```
PYTHONPATH=. python -m pytest tier0/tests -q -m "not battery" --capture=sys
# 2950 passed, 46 skipped, 61 deselected, 12 xfailed
```

Nothing to fix; recorded so the number is reproducible.

---

## 4. Findings

### 4.1 The seam works, offline, against the real assembly

The harness output, in full, on an unmodified tree:

```
BaseLib BaseLib.Abstracts.VisualsPath: armed 1 method(s)
BaseLib BaseLib.Abstracts.CreateVisuals: armed 1 method(s)
[laneD-seam] harmony: 2 patch class(es) armed: VisualsPathPatch, CreateVisualsPatch.
prefixes on MonsterModel.get_VisualsPath: 2 (bitecheck.baselib, bitecheck.laned)

monsters swept        120
  claimed by seam     1
  base path intact    119
  UNEXPECTED value    0
declare own getter    6 (BigDummy, MockArtifactMonster, MockAttackAndSummonMinionMonster,
                        MockAttackMonster, MockIntangibleMonster, MockPlatingMonster)

  CLAIMED  NIBBIT -> res://laned/creature_visuals/proof_prism.tscn

RESULT: all checks passed.
```

Read that middle block as the answer to the charter's second requirement: the
replacement is not global, and it is not global *measurably*, across the whole
bestiary, rather than by argument.

### 4.2 The composition question S13 left open is now answered

S13 reasoned from source that a second Harmony prefix on
`MonsterModel.get_VisualsPath` **should** compose with BaseLib's own, and said
plainly that it had not been executed. It has now. BaseLib's real patch class
is armed first, the spike's second, and the harness reads the prefix list off
Harmony itself: two prefixes, both present, and the value that comes back is
the spike's. The spike runs at low priority on purpose so BaseLib always gets
first refusal — a monster belonging to another mod is resolved by its owner and
never by this seam.

### 4.3 Six base monsters cannot be reached this way — a real limit

`BigDummy` and five `Mock*` monsters declare their own `VisualsPath` override,
so the call never reaches the patched base property. None of the six is an
ordinary encounter enemy, so it costs nothing today, but a production seam that
had to cover an arbitrary enemy would need to check for an override per type
rather than assume the base one. **Nobody would have noticed this from reading
source**; the sweep found it.

### 4.4 A non-Spine enemy loses its motion tells, and that is a taste call

This is the honest cost, and it is unchanged from S13's reading — now with the
mechanism named. The engine builds a creature's animator **only** when the
body node is a Spine sprite. Original geometry is not, so:

- **Kept:** spawning, HP bar, intents, targeting, hitbox, damage, powers,
  death, removal, rewards — and a looping idle, which the scene's own
  `AnimationPlayer` plays without any code involvement.
- **Lost:** attack, hurt and death *tells*. The engine routes those through the
  animator it did not build, so they silently do nothing, and death is instant
  rather than animated.

So the proof enemy will bob in place, take hits without flinching, and vanish
when killed. That is a legible, non-crashing, slightly lifeless enemy. Making
the tells work would mean patching `NCreature` to drive an `AnimationPlayer`
when there is no Spine body — a real piece of work, out of scope tonight, and
worth pricing only if the direction is one you want (question 3).

### 4.5 The failure modes are all soft, by construction

No pack, an unresolvable path, or a throw while building the node each end with
the base method running instead. Below that, the engine has its own catch that
substitutes a visible error scene and logs it. There is no path here that ends
in a crash or a lost run, which is why this was safe to build without being
able to test it live.

### 4.6 The offline harness catches the defect that has no symptom

Removing the id guard — one clause — makes the spike re-skin **all 119**
reachable monsters. The game would still boot, still fight, and log nothing;
the only symptom is looking at every enemy in the game. The harness turns that
into a one-line failure naming every casualty. That case was run: exit 1, 119
listed. The mutation was reverted.

---

## 5. Known debt

1. **Nothing has been rendered.** The scene has never been parsed by Godot, no
   `.pck` was built, and no `NCreatureVisuals` was constructed. Every claim
   here is about strings and method dispatch. The live procedure is in §7.
2. **The `.tscn` is unvalidated by a Godot parser.** It was hand-authored
   against the shipped `klee/model/combat.tscn` as a template and is
   structurally checked by the Python tests, but the first real parse happens
   in the morning. Comments were stripped from it for exactly this reason — the
   one artifact that cannot be tested tonight should carry no untested syntax.
3. **The spike is not loaded by anything.** It builds to its own assembly that
   no mod loads. Making it run in game is a scope decision, not a task —
   see `BUILD-PCK-PATCH-NOTE.md` §2 and question 2.
4. **Co-op is untouched and unknown.** Every seat builds its own visuals, and
   whether a replacement present on one seat only matters is not established.
   This project has no simulator backstop for co-op, so that is play-derived
   or nothing.
5. **Phobia mode is a silent no-op** for the proof scene: it declares no
   `%PhobiaModeVisuals`, so the accessibility toggle does nothing for this
   enemy. Fine for a spike; a question for anything shipped.
6. **`BaseLib`'s scene-conversion internals are still partly unread.** The
   spike calls the same factory entry point `Klee.cs:238` already ships in
   production, so the route is proven by use rather than by reading — but the
   conversion body itself was not audited.

---

## 6. Merge risks

Low, and deliberately so.

- **New files only.** No existing file was modified — `git diff --stat main`
  against tracked files shows additions only. Nothing to conflict with.
- **Outside every scanned tree.** The spike sits at `klee-mod/spikes/`, not
  `klee-mod/KleeCode/`, which is what `lint_constant_parity`,
  `lint_pool_membership`, `test_roster_runtime_contracts` and the codegen
  manifests walk. That placement is asserted by a test so it cannot drift.
- **The existing bite-check is untouched.** Its `17 patch class(es) armed.`
  expectation still holds, because the spike's patch classes are in a different
  assembly.
- **One new test file** in `tier0/tests/`, uniquely named, editing nothing.
- **The only real risk is accidental promotion.** If someone later moves
  `pck-src/laned/` into `klee-mod/pck-src/`, the proof art ships — the pack
  overlay is a wildcard copy, so that single move is enough. There is a test
  guarding the *reverse* (that no build script names the spike), but nothing
  can stop a deliberate move. That is what question 1 is for.

---

## 7. The live test procedure for the morning

Do this **after** you have stopped playtesting. Order matters; each step is
falsifiable on its own.

1. **Re-run the offline gates first.** §3 commands 1–3 and 5. If the harness
   does not print `120 / 1 / 119 / 0`, stop — the game updated and the line
   numbers and member names in the spike need re-deriving before anything else
   is worth doing.
2. **Decide question 1** (below). Everything after this step puts the proof art
   into a pack you will look at.
3. **Pack it.** `git mv klee-mod/spikes/lane-d-enemy-seam/pck-src/laned
   klee-mod/pck-src/laned`, then `tools/build_pck.ps1`. Watch the import log
   for a parse error on `proof_prism.tscn` — that is the one thing this branch
   could not test. Confirm the scene appears in the derived
   `klee.pck.contract.txt`.
4. **Load it.** Per `BUILD-PCK-PATCH-NOTE.md` §2 — the smaller route is moving
   the two `.cs` files into `klee-mod/KleeCode/Patches/`, after which the mod's
   own bootstrap arms them and the existing bite-check should read **19**, not
   17. Confirm that number before deploying.
5. **Deploy and boot.** Grep `godot.log` for `laneD-seam`. Expect the
   registration line and no `proof scene missing` warning. A missing-scene
   warning means the pack did not merge; stop there, the rest proves nothing.
6. **Fight it.** Start a fresh run — the subject enemy is pinned to the first
   normal encounter on a brand-new profile, which is the cheapest way to reach
   it. Check, in this order:
   - the prism renders where the enemy should be, and idles;
   - the HP bar sits above it and is the right width (that comes from
     `%Bounds`, so a wrong-looking bar means the bounds are wrong, not the art);
   - the intent icon sits above the HP bar (`%IntentPos`);
   - hit VFX land on the body, not on the floor (`%CenterPos`);
   - it attacks for its normal damage on its normal schedule — **mechanics
     unchanged is the claim, and this is the check**;
   - killing it removes it cleanly and gives normal rewards.
7. **Confirm the negative.** In the same run, reach any *other* enemy and
   confirm it looks exactly as it always has. This is the visual half of the
   119.
8. **Save/reload.** Save mid-fight, quit, reload. Then remove the mod and load
   the same save: the engine's own tombstone behaviour should carry it, since
   nothing here writes a save key.

If step 3 or 5 fails, the finding is worth as much as a success — write down
which one and the exact log line.

---

## 8. Questions — numbered, and each a pick, not a blank

1. **Does the proof art go into the shipped pack at all?**
   (a) Yes, move it into `klee-mod/pck-src/` so it can be seen in game.
   (b) Yes, but only behind a build flag / debug-only path.
   (c) No — keep it in the spike directory; the offline evidence is enough for
   now.
   *Nothing is packed until this is answered; §7 step 2 is the gate.*

2. **If it runs in game, how does it load?**
   (a) Move the two `.cs` files into `klee-mod/KleeCode/Patches/` — smallest
   change, but the spike becomes part of the shipped mod and enters four
   linted trees.
   (b) Keep it a separate assembly with its own mod id, manifest and pack —
   isolated, but two of everything.
   (c) Neither yet.

3. **Is a motion-less enemy acceptable for a proof, or should the tells be
   built first?**
   (a) Acceptable — idle-only is enough to judge the seam.
   (b) Not acceptable — price the `NCreature` work that would drive an
   `AnimationPlayer` when there is no Spine body (§4.4) before going further.
   (c) Only judge it after seeing step 6 live.

4. **Which enemy is the subject, if any?**
   (a) Keep the current one for the proof only, and treat the choice as
   disposable.
   (b) Name a different one now.
   (c) Do not name any enemy — re-target the spike at a mod-declared monster
   instead, so no base enemy is ever claimed.
   *The current subject was picked for one reason: it is the simplest and
   earliest base enemy, so it is the cheapest to reach in a live test. It is
   not a mapping and this branch proposes none.*

5. **Do the six override-declaring monsters matter?** (§4.3)
   (a) No — none is an ordinary encounter enemy; note it and move on.
   (b) Yes — the seam should handle a per-type override before it is trusted.

---

## What this does NOT establish

It does not establish that any enemy should be re-presented, which one, or what
it should look like. It does not establish that the scene renders — nothing was
rendered. It says nothing about co-op, save migration, performance, or
accessibility. It measures nothing, moves no stamp, registers no experiment,
and interprets no playtest. It is a seam and a proof that the seam behaves;
every mapping, art, rights, scope and ship call is still yours.
