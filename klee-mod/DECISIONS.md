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

## C1 findings from live boot testing (2026-07-19)

Four bugs, found in this order. All four came from *inferring* an API contract
instead of decompiling it — the decompiler was installed and each answer was
one command away. Worth remembering in C2, where the codegen will multiply any
wrong assumption across 60+ cards.

9. **`ModelDb.AllCharacters` is a hardcoded 5-element array, not a registry
   scan.** Subclassing `CharacterModel` registers the type with
   `ModelDb.Get<T>()` (so `ModelDb.Character<Klee>()` resolves fine and throws
   nothing) but never adds it to that array. `NCharacterSelectScreen` iterates
   `AllCharacters` for membership and consults `UnlockState.Characters` only as
   a lock filter — so patching `UnlockState`, as we first did, makes a character
   "unlocked" in a list nothing checks for existence. **Append to
   `ModelDb.AllCharacters`**; it also feeds `UnlockState`, `AllCards`,
   `AllRelics`, and the pool collections.

10. **`StartingRelics` must be non-empty.** `SelectCharacter` does an
    unconditional `characterModel.StartingRelics[0]`. With an empty list the
    `ArgumentOutOfRangeException` lands *mid-method*: name/HP/gold are already
    written to the panel, but the relic widget keeps the previous character's
    data and the lobby's character assignment never runs. Presents as "the
    character is visible but not selectable, and the run starts as whoever was
    picked before" — not as a crash. A character with no starting relic is not
    a supported state.

11. **Loc keys are `ModelId.Entry`, i.e. UPPER_SNAKE_CASE** derived from the
    class name: `DuckAndCover` -> `DUCK_AND_COVER`. Missing keys render as the
    literal `table.key` on the card. The convention was already visible in an
    early log line (`Unknown card ID: CARD.QUICK_FINGERS`) and was missed.

12. **Card description text uses two different syntaxes, and both are easy to
    get wrong.** Values are SmartFormat templates over `DynamicVarSet`
    (keys `Damage`, `Block`, ... per `BlockVar.defaultName`), so placeholders
    are **single** braces — `{Damage}`, not `{{Damage}}`. Square brackets are
    **BBCode**, not keyword markup: descriptions are wrapped in
    `[center]...[/center]`, so a stray `[Block]` throws
    `Found end tag center, expected Block`. Keyword tooltips come from a
    per-mod `card_keywords.json` (Downfall pattern; see
    `docs/card_keywords.json`), which we do not ship yet.

13. **Reward generation requires non-Basic cards in the pool.** With only the
    four Basic starters, `CardFactory.CreateForReward` throws
    `InvalidOperationException: ... couldn't generate a valid card`. Observed
    via `ArcaneScroll.AfterObtained()`, but it applies to every combat card
    reward. Not fixable inside C1: **no** uncommon/rare card on the sheet is
    implementable without the bomb/spark/reaction/burst systems, because those
    systems *are* Klee's identity. Resolves in C2 with the slice list.

## C1 acceptance (2026-07-19)

Met per spec C1.5: game boots modded, Klee appears in character select, a fight
starts and completes with the stub starter deck. Full-run play is explicitly a
C2 activity ("THE PLAYTEST BUILD"), and finding 13 above means card rewards
cannot work until the slice list exists.

## Open items

- **O1 — RESOLVED.** `quick_fingers` `src/bin` and `src/obj` deleted from the
  game's `mods/` tree (user approved); boot spam gone. Its *source* still has
  the D3 API drift and will not rebuild until the `choiceContext` fix is
  applied. The prebuilt dll still loads, and the mod is disabled in settings.
- **O2 — RESOLVED**, the hard way; see finding 10.
- **O3 — Spikes S1 and S2 not yet run.** Both still gate C2 per spec. S1 is now
  cheaper than budgeted: ilspycmd is installed and the decompile loop is fast.
- **O4 — `RunWonAchievement` will throw on a win.** It does
  `Enum.Parse<Achievement>(Id.Entry.Capitalize() + "Win")` and no `KleeWin`
  member exists. Harmless for C1 (acceptance is one fight) but a guaranteed
  crash the first time anyone completes a run. Fix before any real playtest.
- **O5 — `LOCPROBE` diagnostic still in `KleeMod.cs`.** Temporary; dumps
  base-game card descriptions to confirm loc syntax. Delete once C2 text is
  rendering correctly.
- **O6 — Placeholder art is load-bearing.** `KleePlaceholderArt.cs` rewrites 22
  asset/sfx paths from `klee` to `ironclad`. Deleting it without shipping a real
  `.pck` returns us to missing-resource crashes on the select screen.
