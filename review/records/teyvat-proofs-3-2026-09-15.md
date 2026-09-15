Status: RECORD (asset-set boot proof and six dressed events; feasibility only, nothing measured)

# The placeholder asset sets break combat, and that blocks everything downstream

**Nothing here is measured or quotable** — no pre-registration, no blind grading, no slate.

**Installed.** `tools/gen_act_placeholders.py` wrote **36 files**: 16 committed scene
sources under `klee-mod/pck-src/scenes` (byte-identical to what #505 already committed —
`git status --short klee-mod/pck-src` prints nothing, so the generator is deterministic)
and 20 gitignored textures under `ImageGen/images/teyvat`. `git status --short ImageGen`
prints nothing. Then `deploy_round.py --arms klee,companion,kokomi,furina-stage,teyvat`
(pck REBUILD, as expected). Read back: **`0.2.3290+proto.dirty`**, bridge present, 406
staged card png(s). The pck contract carries both dressings' full sets — 7
`scenes/backgrounds/<act>` entries, 2 `rest_site/<act>`, 3 `map_bgs/<act>` each. **The
arm is ON in the installed build.** Profile untouched.

## The soak: FAILS R225

`--runs 1 --character KLEEMOD-KLEE --max-fights 3` →
**`defect seed=EVLR8Z0MTNSW actions=23 fights=1 defects=1`** on `Version=0.2.3290.0`.
That is `fights=3 defects=0` unmet, and the cause is DEFECT 1 below.

## DEFECT 1 — the background LAYER scenes cannot be loaded, and combat aborts

The background **root** is fine, so #505's new factory works:

```
[INFO] [BaseLib] Auto-converted 'res://scenes/backgrounds/liyue/liyue_background.tscn'
       from Control to NCombatBackground
```

The **layers** are not:

```
ERROR: No loader found for resource:
  res://scenes/backgrounds/liyue/layers/liyue_bg_00_a.tscn.remap (expected type: unknown)
[ERROR] MegaCrit.Sts2.Core.Assets.AssetLoadException: Asset previously failed to load:
  res://scenes/backgrounds/liyue/layers/liyue_bg_00_a.tscn.remap.
   at AssetCache.LoadAsset(String path)
   at AssetCache.GetAsset(String path)
   at AssetCache.GetScene(String path)
   at NCombatBackground.AddLayer(String layerName, String layerPath)
   at NCombatBackground.SetBackgroundLayers(IReadOnlyList`1 backgroundLayers)
   at NCombatBackground.SetLayers_Patch1(NCombatBackground this, BackgroundAssets bg)
   at NCombatBackground.Create(BackgroundAssets bg)
   at EncounterModel.CreateBackground(ActModel parentAct, Rng rng)
   at NCombatRoom.SetUpBackground(IRunState state) / .OnCombatSetUp(CombatState state)
   at CombatManager.SetUpCombat(CombatState state)
   at CombatRoom.StartCombat(IRunState runState)
```

**The throw is inside `SetUpCombat`, so combat setup aborts.** The room is created
(`Creating NCombatRoom with mode=ActiveCombat encounter=TOADPOLES_WEAK`) and then nothing:
no card is ever played, no win or loss is logged, the run is stuck. The frame shows it —
no background at all, no hand, no enemy intent, energy `0/3`.

**Both dressings, same stack** — Liyue 27 remap errors (the soak run), Mondstadt 6 (a
separate embark), so it is not one act's file set.

**Why**, as a reading rather than a fix: the base game is an *exported* Godot project and
`AssetCache.GetScene` resolves through the export remap (`<path>.tscn.remap`), while our
pck ships raw `.tscn`. BaseLib's auto-conversion path loads a raw `.tscn` happily — which
is why the background root, and `creature_visuals/hilichurl_guard.tscn` before it, both
work — but `AssetCache` does not. The layers need to ship exported, or be reached by a
loader that is not `AssetCache`. No C# was changed.

**This is a regression against the alias.** #505 made the `FilePathIdentifier` alias
conditional on the set being *absent*; the set is now present, so the alias correctly does
not fire, and the real layer paths are used for the first time. Before #505 the alias sent
every asset path to the base zone's and combat worked.

**Frames** (gitignored, not committed), under `understudy/logs/frames/`:
`frame-20260915-043033-teyvat-map-mondstadt.png` (map screen) and
`frame-20260915-043035-teyvat-combat-mondstadt.png` (the dead combat). MATERIAL, not
evidence (Guardrail-7).

## What does work

- **The map screen draws** with the placeholder plates: a flat green field, the node
  graph, the legend, the boss node — the three `map_bgs` PNGs load, being textures rather
  than scenes.
- **The background root scene converts** through the new `NCombatBackgroundFactory`.
- **The loc merge grew to `369 converted-event row(s)`** (from 10), so #506's 23 mirrors
  are merged, and there is **no** raw-key miss for `MONDSTADT.title` or `LIYUE.title` —
  the act-title rows resolve. I could not confirm the title *on screen*: the map header
  in the capture shows no act name at all, and the wire carries only an act index
  (`McpMod.StateBuilder.cs:608`), so this is unconfirmed rather than failed.

## BLOCKED — the rest site and all six dressed events

Neither could be tested, and the reason is DEFECT 1 rather than anything about them: **a
run cannot leave floor 1 on this build.** Act 1's first floor offers only combat —
observed `['Monster','Monster','Monster']`, `['Monster','Monster']` and `['Monster']` on
every map reached this session, with no `?`, rest, treasure or merchant among them — and
combat aborts, so there is no second floor. The six events sit on `?` rooms and the rest
site on a rest node, both past a fight that cannot be had; twenty-six embarks went into
confirming that before I stopped.

**A second finding, which would have bitten anyway.** The six dressed ids are **not** what
the act's pending pool holds. Read live from the map at floor 1: Mondstadt **31 pending**,
Liyue **28**, and `GUILD_DESKS_RETURNED_COPY`, `CUT_ROPE_BRIDGE_ABOVE_CIDER_LAKE`,
`ANGELS_SHARES_TASTING_FLIGHT`, `SIX_CONTRACTS_TO_A_BETTER_YOU`,
`GUYUN_STONE_CONSTRUCTS`, `FLOODED_LEDGER_ROOM` are **all absent** from both. The pool
carries BASE ids (`AROMA_OF_CHAOS`, `BRAIN_LEECH`, `DOLL_ROOM`, `ABYSSAL_BATHS`,
`DOORS_OF_LIGHT_AND_DARK`, …), exactly as the cheese cellar behaved: the substitution
happens downstream at `PullNextEvent`, so a dressed event is forced by **its base id**.
The six map to `SELF_HELP_BOOK`, `SLIPPERY_BRIDGE`, `TEA_MASTER`, `SELF_HELP_BOOK`,
`PUNCH_OFF` and `WATERLOGGED_SCRIPTORIUM` (two of the six mirror the same base event).
So a later pass should force the base id, not the dressed one.

## Defects

1. **Background layer scenes fail to load; combat aborts in both dressings.** Blocking.
   `AssetLoadException … liyue_bg_00_a.tscn.remap` at `NCombatBackground.AddLayer` inside
   `CombatManager.SetUpCombat`. Act 1 is unplayable past floor 1 with the arm on.
2. **R225 unmet on this build** — `defect … fights=1 defects=1`, caused by (1).
3. **Unconfirmed, not failed:** the act title on the map header and the rest site's
   `%RestSiteLighting`, neither reachable while (1) stands. No row is retired here, and
   no C# was changed.
