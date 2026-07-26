# Harmony bootstrap bite-check

A manual gate for `KleeCode/KleePatchBootstrap.cs` (Serenitea Sweep II, F2).
It loads the built `klee.dll` **outside Godot**, runs the mod's real patch
bootstrap against the real game assembly, and prints the boot report.

```
cd klee-mod/build/bitecheck
dotnet build
./bin/Debug/harmony-bitecheck.exe            # defaults to KleeCode/bin/Debug/klee.dll
./bin/Debug/harmony-bitecheck.exe <path/to/klee.dll>
```

Expected on an unmodified tree:

```
[klee] harmony: 14 patch class(es) armed.
```

No warnings, no errors, and **14** is the number to compare against.

## Why it is not in CI

It needs the Slay the Spire 2 install and the Workshop BaseLib, neither of
which exists on a GitHub runner — the same reason `validate.ps1` is not in CI
(see `docs/pending/serenitea-g3-ci-proposal.md`). The automated half of F2 is
`tier0/tests/test_harmony_bootstrap_contract.py`, which pins the *shape* of the
bootstrap and runs everywhere. This harness checks the *behaviour*, by hand,
when the bootstrap changes.

It works at all because `sts2.dll` is a plain `net9.0` assembly: Harmony can
patch its methods with no scene tree and no native Godot runtime. Anything that
touches a Godot object would fail here, so the harness only patches and reports.
The game's logger writes where this process cannot see it, so the first thing
the harness does is Harmony-patch `Log.Info/Warn/Error` to stdout — using the
mechanism under test to observe the mechanism under test.

## Running an actual bite-check

Break exactly one lookup, rebuild `KleeCode`, re-run, and read the report. Then
revert. Three cases are worth knowing, all three run on 2026-07-27:

| Break | Expected | Observed |
|---|---|---|
| Class-level target renamed — `[HarmonyPatch(typeof(MerchantInventory), "PopulateColorlessCardEntries")]` | 13 armed; 1 FAILED naming the class *and its target*; softlock-guard escalation | as expected |
| One of two `TargetMethods` lookups renamed (`CheckFifteenElitesDefeatedEpoch`) | 14 armed; one **DEGRADED** warning naming the dead lookup; no error | as expected |
| *Both* `TargetMethods` lookups renamed | 13 armed; 1 FAILED listing both dead lookups; softlock-guard escalation | as expected |

The middle row is the one that justifies the degraded/failed split: a class that
armed one of its two targets is still doing half its job, and calling that an
ERROR would train an operator to skim past errors.

The first row is also how a real defect was caught while F2 was being written:
the failure report named the casualty by string-splitting its own rendered line
on `:`, and adding the patch target to that line silently broke softlock-guard
escalation. The pin suite could not have caught that. This harness did, on the
first run after the change.

## What "armed" means

- **armed** — the class patched at least one method and every lookup resolved.
- **DEGRADED** (warn) — patched at least one method, but named lookups failed.
  Partial behaviour is live.
- **FAILED** (error) — patched *nothing*, whether it threw or silently matched
  no methods. Reported loudly because a patch that silently arms nothing is the
  exact failure F2 exists to make impossible.

If a failing class is one of the four softlock guards, the report says so in
those words and tells the operator not to playtest that build.
