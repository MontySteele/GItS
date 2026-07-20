# C-Milestones — Decision log

Per csharp-build-spec.md §0. Environment facts and implementation rulings made
while building. Amend here, not in chat history.

## Pinned environment (2026-07-19)

| Thing | Value |
|---|---|
| Slay the Spire 2 | **v0.107.1**, commit `59260271`, dated 2026-06-18 |
| Steam buildid | **23811903**, appid `2868840`, branch `public` |
| `main_assembly_hash` | `-1555940892` |
| MegaDot | **v4.5.1**.m.12.mono.custom_build |
| BaseLib | 3.3.7.0 (265 Harmony patches, 0 failed) |
| .NET SDK | 9.0.316 (installed this session; machine had runtimes only) |
| ilspycmd | 8.2.0.7535 (pinned — see D4) |

Spec §0.2 asks for a beta-branch pin. **Not available**: the app manifest shows
only `BetaKey "public"`. Version churn therefore remains an unmitigated risk;
the mitigation is that the exact build is recorded above, so a breakage after a
Steam update is diagnosable rather than mysterious.

## C1 (2026-07-19)

1. **Template: `quick_fingers`, not the Downfall fork.** Spec C1.2 called for
   cloning lamali292/Downfall and proving it builds unmodified. Two facts
   changed this: Downfall is installed here as a *binary* Workshop package
   (`.dll`/`.pck`), not source; and the machine already had a working
   first-party-pattern mod (`quick_fingers`) that loads against this exact game
   build from a 20-line csproj referencing `sts2.dll` / `0Harmony.dll` /
   `GodotSharp.dll`. That is the spec's own named fallback shape
   (jiegec/STS2FirstMod) already validated. C1.3's intent — isolate
   "environment problem" from "our problem" — was satisfied by rebuilding
   `quick_fingers` from source on this machine before writing any Klee code.

2. **Reference implementation is `Silent`, not Hexaghost.** Since we're not on
   the Downfall codebase, the character template is the game's own
   `MegaCrit.Sts2.Core.Models.Characters.Silent`, decompiled from v0.107.1.
   First-party and current, which beats a third-party fork's copy.

3. **API drift is real and already bit us.** `quick_fingers` failed to compile
   against v0.107.1: `PowerCmd.Apply<T>` now takes `PlayerChoiceContext` as a
   required first parameter. One-line fix, but it confirms the spec's
   "BaseLib/game API drift" standing risk is live, not theoretical, and that
   mod source rots against EA patches within weeks.

4. **ilspycmd pinned to 8.2.0.7535.** The current release ships a broken
   package (`DotnetToolSettings.xml` missing) and fails to install. 8.2 works.

5. **`sts2.xml` is a partial shortcut, not a replacement for decompiling.** The
   game ships 5.3 MB / 99k lines of XML doc comments, but only for members that
   carry `///` comments — `CharacterModel` is absent. Useful for intent on
   documented APIs; decompilation is still required for signatures.

6. **`GenerateAnimator` is virtual, so C1 needs no art.** `CharacterModel` has
   exactly 14 abstract members, all data. Animation has a working base
   implementation. This removes spine/`MegaSprite` art from the critical path
   for "boots" entirely — a bigger de-risk than expected.

7. **Build output must never live under the game's `mods/`.** `ModManager`
   walks `mods/` recursively and parses every `*.json` as a manifest. The
   existing `quick_fingers/src/bin` and `src/obj` cause a `[ERROR]` per stray
   `deps.json` and a `JsonException` on `project.assets.json` **every boot**.
   `build/deploy.ps1` therefore stages a clean manifest+dll package and copies
   only that. (The pre-existing `quick_fingers` spam is untouched — it is
   outside the repo; see open item O1.)

8. **C1 stubs, explicitly not final.** Recorded so they aren't mistaken for
   design intent later:
   - `Pop!` deals its 5 damage *immediately* instead of placing a bomb. The
     delayed place-then-detonate rhythm is the entire point of the card and of
     playtest question 1; this stub deliberately does not test it. Fix in C2.2.
   - `Jumpy Dumpty` omits its bomb half and targets a chosen enemy rather than
     random ones.
   - Klee has **no starting relic** (Pounding Surprise depends on Sparks, C2.3)
     and borrows Silent's relic/potion pools to keep the run loop functional.
   - Card frame and energy colour borrow Ironclad's red assets; we ship no
     `.pck` yet (`has_pck: false`).

## Open items

- **O1 — `quick_fingers` boot spam.** Its `src/bin` and `src/obj` sit inside the
  game's `mods/` tree and error on every launch. Harmless but noisy, and it
  makes our own logs harder to read. Deleting it touches files outside the repo,
  so it needs the user's go-ahead (§0.4).
- **O2 — Klee with no starting relic is untested.** Every base character has
  one; if the run/reward flow assumes it, this is where a boot failure will
  surface first.
- **O3 — Spikes S1 and S2 not yet run.** Both are still gating C2 per spec.
