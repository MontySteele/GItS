# Punch Off crash (seed `8B97LMCL2F`) — static reading

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

**Date:** 2026-08-05 · **Track F2, findings-only.** No game process was launched
for this memo and nothing was written to the game install or the Godot user
directory. Every check below is an offline read and is re-runnable.

---

> **RECLASSIFICATION EXECUTED 2026-08-06 (Class-P, R119 / P-B item C-3 —
> dated annotation; the frozen memo below is untouched).** The recommendation
> this memo closes on — SUSPECTED-OURS → game-side/spine-side — is now the
> classification of record: `EB-1`'s owner note flips and queue row 10.6 is
> struck. The rotation caveat is preserved verbatim (the 2026-08-04 crash log
> is gone; this memo's quotations are the surviving copy). Ledger:
> `docs/registry/p-ledger.md`.

## Verdict, up front

**Does the double-connect hypothesis survive static reading? NO.**

The signed hypothesis (R99/2) is: *"'Signal already connected' with the
animation-router patch on the stack reads as our patch double-connecting on
event-screen re-entry."* Read statically, that mechanism is not available to us:

- **our shipped assembly contains no signal connection of any kind** — not to
  this signal, not to any signal;
- **the signal named in the error does not exist in the game's C# assembly at
  all.** It exists only inside the native `spine-godot` GDExtension;
- **our creature scenes contain no `SpineSprite`**, so no instance of ours can
  be party to a connection on a spine resource;
- **our patch is a Harmony *postfix*.** The frame that raised the error,
  `CreatureAnimator.SetNextState`, is inside the *original* method body, which
  runs to completion before our code is reached.

**Recommended reclassification: SUSPECTED-OURS → game-side / spine-side.** The
routing ruling explicitly provides for this ("If it proves game-side, the
routing note flips and nothing is lost"). One low-ranked our-side lead survives
and is listed in §5; it is *not* a double-connect.

**No fix was committed.** The FIX-ONLY-IF condition was a mechanical
double-connect guard in our code. There is no connect in our code to guard.
Writing one would be inventing a defect to fix.

---

## 1. Evidence chain

Each row is a check, its result, and how to re-run it offline.

| # | Check | Result |
|---|---|---|
| 1 | Every `Connect` / `Disconnect` / `Callable` / `EmitSignal` / `+=`-on-signal across the mod's **349 `.cs` files** | **zero hits.** The only matches for the string "Signal" are two Kokomi card class names, `MoonSignal` and `SignalArrow`. |
| 2 | The deployed binary, `mods/klee/klee.dll`, scanned (ASCII + UTF-16) for `spine`, `set_skeleton`, `Connect` | **zero hits.** The build in the game directory matches the source on this point; `CreatureAnimationRouter`, `NCreature_SetAnimationTrigger_AnimationTreeRoute`, `NCreature_StartDeathAnim_AnimationTreeRoute` and `%AnimationTree` are all present, so this is the right binary and it simply contains no spine or signal surface. |
| 3 | `_internal_spine_objects_invalidated` searched in `data_sts2_windows_x86_64/sts2.dll` | **not present.** |
| 4 | Same string searched in `libspine_godot.windows.template_release.x86_64.dll` | **present — the only binary on the machine that names it.** Neighbouring strings place it with `SpineAtlasResource.cpp` and `SpineSkeletonDataResource.cpp`. |
| 5 | Same string searched in the other two installed mods (`STS2AutoSlayMod.dll`, `quick_fingers.dll`) | **zero hits** in either; neither names `SpineSprite` or spine at all. |
| 6 | Our two convention creature scenes (`klee-mod/pck-src/{klee,furina}/model/combat.tscn`) node census | `Node2D` / `Sprite2D` ×4–5 / `Control` / `Marker2D` ×2 / `AnimationPlayer` / `AnimationTree`. **Zero `SpineSprite`.** |
| 7 | Full Harmony patch inventory of the mod | 13 patch classes. `NCreature` is touched by exactly two, both `[HarmonyPostfix]`. Nothing patches spine, resource loading, `NCombatRoom`, `CreatureAnimator`, or any event. |
| 8 | `CreatureAnimationRouter.Route` body | `GetNodeOrNull<AnimationTree>("%AnimationTree")` → early-return null for any spine creature → `playback.Travel(state)`. No allocation, no connection, no resource touch. Re-confirms the measured fact already recorded in `docs/animation-sprint-2-log.md`. |
| 9 | `sts2.dll` strings around the animation path | `_spineAnimator`, `CreatureAnimator`, **`ConnectSpineAnimatorSignals`**, **`set_skeleton_data_res`**. The game's own C# both connects spine animator signals and calls the native setter. |

### What that adds up to

`_internal_spine_objects_invalidated` is emitted by
`SpineSkeletonDataResource` / `SpineAtlasResource` and subscribed by
`SpineSprite` **inside native `spine-godot` code**, on the path reached through
`set_skeleton_data_res`. The subscription is per-`SpineSprite`-instance. The
"already connected" message is therefore produced when a `SpineSprite` that is
already bound to a skeleton-data resource is bound again — a second
`set_skeleton_data_res` on a live sprite, or a sprite re-entering `_ready`
against a resource it never released.

`set_skeleton_data_res` is called from `sts2.dll`. It is called from neither
`klee.dll` nor the other two mods. **No mod on this machine can reach the
subscription.**

---

## 2. The one inference that made this look ours, corrected

The trace as recorded reads:

```
PunchOff.PunchEachOther
  -> CreatureCmd.TriggerAnim
    -> NCreature.SetAnimationTrigger
      -> CreatureAnimator.SetNextState
```

**No frame in that trace names our code.** `NCreature.SetAnimationTrigger`
appears because it is a base-game method that appears in a base-game call
chain. It is *also* a method we patch, and the note "our animation-router patch
is on the stack" is an inference drawn from that coincidence, not a frame that
reads `KleeMod.Vfx`. That inference is what set the classification.

Two properties of the patch make the inference unsafe:

1. **Postfix ordering.** Harmony weaves a postfix after the original body. For
   our code to have caused an error raised inside `CreatureAnimator.SetNextState`
   — which the original body calls — the postfix would have to run before the
   method it postfixes.
2. **Inertness for spine creatures.** The creature reaching `SetNextState` has a
   live `_spineAnimator`, which `NCreature` builds only when
   `Visuals.HasSpineAnimation`. That creature is a base-game rig (a Punch
   Construct). Our postfix then looks for `%AnimationTree` under its `Visuals`,
   finds none, and returns. The two conditions are mutually exclusive by
   construction: a creature with a spine animator is a creature our router does
   nothing to.

---

## 3. Suspected connect site(s)

**In our code: none.** That is the finding, not an omission.

**Behavioral note on where it does live** (no decompiled code reproduced): the
subscription is made in native `spine-godot`, in the `SpineSprite` binding path
that `SpineSkeletonDataResource` participates in; the caller that can trigger it
twice is `sts2.dll`'s use of `set_skeleton_data_res`. The extension declares
itself in-pack at `addons/spine/spine_godot_extension.gdextension`
(`entry_symbol = spine_godot_library_init`, `compatibility_minimum = 4.1`).

A scene built twice and freed once looks exactly like this from the log, which
is the shape the routing note already guessed at — it simply attributed the
double build to us rather than to the `VisualOnly` construction/teardown that
`PunchOff` performs. `PunchOff.PunchEachOther` compiles to an **async state
machine** (`<PunchEachOther>d__12` in `sts2.dll`), so it yields across frames
and its teardown can interleave with a screen change. That is a game-side
re-entry surface, and it is the one the evidence points at.

---

## 4. Two evidence-preservation findings

**4a. The crash log is gone.** `%APPDATA%/SlayTheSpire2/logs/` currently holds
five files, the oldest timestamped **2026-08-05**. The 2026-08-04 log that
carried the backtrace has rotated out. The quotations in
`docs/sprint-understudy-p1-log-2026-08-04.md`, `docs/animation-sprint-2-log.md`
and `tier0/DECISIONS.md` R99/2 are now **the only surviving copy of the
evidence**. Nothing here can recover it. Recommendation for whoever owns the
next soak: copy `godot.log` into the run's artifact directory at teardown, not
after triage.

**4b. The field that would settle native-vs-managed did not exist yet.**
`proc_exit_code` was added to the defect record by the *fix* for soak defect
11 — i.e. by the same pass that observed this crash. The `8B97LMCL2F`
observation therefore has **no recorded exit code**. The value in the red test
(`tier0/tests/test_understudy_soak.py:548`, `-1073741819` = `0xC0000005`,
STATUS_ACCESS_VIOLATION) is a *fixture default*, not the observed code, and
must not be cited as evidence that the crash was a native access violation. A
re-run will capture the real one.

---

## 5. The one our-side lead that survives (low)

Not a double-connect, and stated as a lead rather than a hypothesis:

**BaseLib scene conversion is path-keyed, and our pipeline forbids scripts in
scenes** (`klee-mod/pck-src/README.md`: "One scene path = one conversion
target. Never point two conversion registrations at the same .tscn"; the rule
exists because of the 2026-07-20 first-campfire softlock, which was a
double-registration). If a `VisualOnly` `NCombatRoom` instantiates the player's
converted convention scene on a path that is also live in the ordinary combat
room, the double-build is on our side of the registry rather than the game's.
We do not patch `NCombatRoom` and cannot see its construction offline, so this
is unresolvable statically. It predicts a *scene* double-build, not a signal
double-connect, and it would produce this log line only indirectly. Rank it
below the game-side explanation.

---

## 6. Minimal repro script for a game-owning session

Ordered so the cheapest discriminator runs first. Steps 1–2 alone settle the
classification.

**Prerequisites:** klee build deployed; a session that owns the game process;
`%APPDATA%/SlayTheSpire2/logs/` emptied or its current contents archived first.

1. **A/B the mod, one variable.**
   a. Launch with `mods/klee/` present. Seed `8B97LMCL2F`. Reach total floor
      ≥ 6 in the Underdocks pool, take the **Punch Off** event, accept the
      fight (it costs a relic and a potion per player — that is expected).
   b. **Immediately copy `godot.log` out of the logs directory**, before any
      relaunch. Record the process exit code.
   c. Move `mods/klee/` aside entirely. Repeat (a) on the same seed.
   - **Still crashes without our mod → game-side, confirmed. Classification
     flips and the item closes as not-ours.**
   - **Crashes only with our mod → our involvement is real but is not the
     router**, and step 2 localises it.

2. **A/B the router only** (run only if 1c came back clean). Rebuild `klee.dll`
   with the two `[HarmonyPatch]` attributes in
   `klee-mod/KleeCode/Vfx/CreatureAnimationRouter.cs` commented out — nothing
   else changed — and repeat. If it still crashes, the router is exonerated and
   the lead in §5 is next.

3. **Bound the observation.** Three passes of step 1a on the same seed. Two
   observations exist today and both were incidental to other work; a
   crash-every-time and a crash-one-time-in-three are different bugs.

4. **Capture, whatever the outcome.** `godot.log`, `proc_exit_code`, and — if
   the process leaves one — the crashpad dump beside `crashpad_handler.exe`.
   File all three with the seed.

**Do not attempt this from a soak run.** The soak's own note is right that a
crashing process and an exited process are different things; drive it by hand
so the moment of death is observed rather than inferred.

---

## 7. What this memo did not do

- No live reproduction — Track F was barred from the game process tonight.
- No commit to `klee-mod/`. The FIX-ONLY-IF gate was a mechanical guard on one
  of our own connects; we have none.
- No claim about the *fatal* mechanism. "Signal is already connected" is a
  Godot error print, not by itself a process kill; what actually ended the
  process is unknown, and §4b explains why the repo cannot say.
