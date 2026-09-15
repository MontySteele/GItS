Status: RECORD (spike deploy proofs; feasibility only, nothing measured)

# Spike 4, deploy half: what the four items do in the real game

The build half is `review/records/teyvat-spike-build-2026-09-15.md`; its four "A deploy
must prove" lines are the agenda. **Nothing here is measured or quotable** — no
pre-registration, no blind grading, no slate.

## Installed, loadout, soak

`tools/deploy_round.py --arms klee,companion,kokomi,furina-stage,teyvat` from the main
checkout; the pck rebuilt (the Tier F placeholder had moved). Read back: **installed
version `0.2.3248+proto.dirty`**, bridge present at `mods\STS2_MCP`, 406 staged card
png(s), and `klee.pck.contract.txt` carrying both
`res://teyvat/creature_visuals/hilichurl_guard.{png,tscn}`. The `.dirty` is a
**pre-existing** uncommitted edit to `review/records/reaction-census-2026-09-05.md`; no
git command but `status`/`log` ran in the main checkout.

**Loadout**, set by [USER] and left as-is: `BaseLib` (Workshop), `klee` and `STS2_MCP`
**on**; `PengoTarot`, `Downfall`, `STS2AutoSlayMod`, `quick_fingers` **off**; original
at `settings.save.pre-teyvat-proofs`. **The arm is ON in the installed build** — the
next calibration deploy must turn it off (`prototype.md`, frame packet §5).

**Soak (R225):** `--runs 1 --character KLEEMOD-KLEE --max-fights 3` → **`bounded
seed=3DBMV5XQF4HJ actions=57 fights=3 defects=0`**. An earlier attempt read `died
seed=Y3U29JX8DE5W actions=79 fights=2 defects=0` — policy_v1 lost, a run outcome and not
a defect. No crash in either.

## The one defect under three of the four items

`[ERROR] [klee] teyvat: loc merge failed, the arm's text will render as raw keys:
System.NullReferenceException` at `TeyvatLoc.Inject()`, **every boot**. It is called
from `KleeMod.Initialize` (`KleeMod.cs:50`), a `[ModInitializer]`, where `LocManager`'s
tables do not exist yet; the shipped card rows reach the same `MergeWith` from a Harmony
**postfix on `LocManager.Initialize`** (`KleeMod.cs:716-720`, doc line: "Injects our loc
strings once LocManager has built its tables"). Wrong seam — the call-site comment
reasons about when a table is *read*, not when it *exists*. Zero rows merge, so every
dressed string renders as its raw key. Not fixed here (C# out of scope); wants a
`BACKLOG` row.

## Item 1 — a zone dressed two ways: PROVEN WITH A COST

- **The `get_Acts` postfix lands before `ModelDb` is first read**, and both dressings
  appear while neither base zone does. Over **14 embarks**, `Preloading 'Act=…'` read
  **MONDSTADT 8, LIYUE 6** (excluding the first, 7 and 6); not one run preloaded
  `OVERGROWTH` or `UNDERDOCKS` — replacement, not addition.
- **`get_FilePathIdentifier` takes the patch** — the sharpest question, a one-expression
  getter being a JIT inline candidate. The predicted symptom of a miss,
  `InvalidOperationException` out of `BackgroundAssets` on the first Mondstadt combat,
  is **absent from every combat entered**.
- **Coin FAIRNESS is NOT PROVEN, and the shape is why.** The sequence was eight
  Mondstadt then six Liyue — one switch, no interleaving, across five separate soak
  invocations (the flip does not sit on a session boundary), which is not what fourteen
  independent coins usually look like. Act **discovery** is the obvious suspect — the
  `ActModel.cs:563` neighbourhood both dressings were made `IsDefault` to dodge — and is
  cheap to read.
- **Save/load round trip: PROVEN.** Run embarked (seed `NH4CSR6V5YVL`, `Act=MONDSTADT`,
  floor 1), process killed by pid, game relaunched: the menu offered `continue`, taking
  it resumed **the same seed**, and that session asked for **`MONDSTADT.title`** — the
  dressing came back off the save.
- **The act's NAME does not render:** `GetRawText: Key 'MONDSTADT.title' not found in
  table 'acts'` — the loc defect, and the cost. It is *drawn* as Overgrowth by design;
  today it is also *titled* `MONDSTADT.title`. `NBestiary`, run history and the epoch
  screens were not opened — no wire route.

## Item 2 — the Springvale Cheese Cellar: NOT PROVEN

Never reached, because **there is no forcing route**: `bridge.DEBUG_OPS` has no event op
(`set_resource / set_energy / set_hp / set_block / set_power / clear_hand / hover /
unhover`), and the scenario runner starts at the first fight and asserts combat numbers
only, so it cannot stand on a map. The tally runs stop before a `?` room; reaching it by
luck needs full runs whose path the policy does not steer, which the launch stall below
made unaffordable. Regardless, its eleven loc rows are in the same failed merge, so a
run reaching it today would read eleven raw keys. Both options and the relic are
untested.

## Item 3 — Nibbit as the Wooden Shield Hilichurl Guard: SPLIT

- **The name-rewrite mechanism WORKS, the name does not render.** Every line of a
  Mondstadt fight names the monster `monsters.NIBBIT.name@MONDSTADT` — the
  `L10NMonsterLookup` postfix fires, and only under the dressing — but `GetRawText: Key
  'NIBBIT.name@MONDSTADT' not found in table 'monsters'`.
- **`get_VisualsPath` DOES take the patch — and the portrait still fails.** The engine
  reaches our scene and throws `System.InvalidCastException: Unable to cast object of
  type 'Godot.Node2D' to type 'MegaCrit.Sts2.Core.Nodes.Combat.NCreatureVisuals'` at
  `MonsterModel.CreateVisuals_Patch1` → `Creature.CreateVisuals` → `NCreature.Create` →
  `NCombatRoom.CreateEnemyNodes`, **"Falling back to error scene."** `CreateVisuals`
  **casts** the instantiated root, it does not adapt it, so `pck-src/teyvat/README.md`'s
  "instantiates whatever is at `VisualsPath` as an `NCreatureVisuals`" is the wrong
  reading; BaseLib's `Registered scene '…' for auto-conversion to NCreatureVisuals`
  lines are the mechanism the scene is missing.
- **The two ungated Spine doors were NOT exercised** — `GetCurrentAnimationLength` /
  `GetCurrentAnimationTimeRemaining` never appear, because the still body never loaded;
  that question needs the cast fixed first. The failure is graceful: the fight completes
  on the error scene (`KLEEMOD-KLEE has won against encounter ENCOUNTER.NIBBITS_WEAK`).
  No frame was captured — it would show the error scene, which the exception says
  better.

## Item 4 — music: PROVEN WITH A COST (the fall-through)

With no track in the pack the postfix falls through and the run continues — but **not
silently**. Every `UpdateMusic` logs `ERROR: Couldn't open directory at path
"res://teyvat/music/mondstadt"` with a 31-frame C# backtrace through
`TeyvatMusic.TrackFor` → `Play` →
`NRunMusicController_TeyvatTrack_Patch.UpdateMusicPostfix`. `DirAccess.GetFilesAt` on a
missing directory is a logged engine error, so the build record's "both postfixes fall
straight through" is true of control flow and false of the log; an existence check
before it costs one line. The stack also answers half of the fourth question — the call
arrives via `NRun._Ready` → `PreloadManager.LoadActAssets`, so **run/act start routes
through `UpdateMusic`** (the other three surfaces were not separated). Whether a Godot
`AudioStreamPlayer` is audible while FMOD holds the device is **NOT PROVEN**, no track
existing, and nor is `StopMusic` re-entrancy, never called with no file.

## An operational finding that is not the arm's

Four batches died with `menu never became ready within 180s`. The game was alive and the
bridge had started (`[STS2 MCP] v0.4.0 server started`); it was writing the profile's
**869 run-history files, 23 MB**, to the Steam remote store on every boot, and the stall
worsened as batches added to them. Batches of four were the workaround, and are why the
tally is 14 and not 20. No run history was deleted — it is [USER]'s data.
