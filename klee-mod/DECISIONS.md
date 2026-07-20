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
- **O4 — `RunWonAchievement` — DOWNGRADED to latent; see finding 19.** The
  earlier "guaranteed crash the first time anyone completes a run" claim was
  wrong for v0.107.1: the property has *zero callers* in either sts2.dll or
  BaseLib.dll, and every `AchievementsHelper` method is an empty stub. It
  cannot fire in this build. Deliberately NOT patched — see finding 19 for why
  a defensive patch would be worse than the bug. Re-check if MegaCrit wires
  achievements up.
- **O5 — `LOCPROBE` diagnostic still in `KleeMod.cs`.** Temporary; dumps
  base-game card descriptions to confirm loc syntax. Delete once C2 text is
  rendering correctly.
- **O6 — Placeholder art is load-bearing.** `KleePlaceholderArt.cs` rewrites 22
  asset/sfx paths from `klee` to `ironclad`. Deleting it without shipping a real
  `.pck` returns us to missing-resource crashes on the select screen.

## C1 findings from art + BaseLib integration (2026-07-20)

**Finding 14 — `CustomCardModel` requires pool registration, and fails at boot.**
BaseLib's `CustomCardModel(..., bool autoAdd = true)` calls
`CustomContentDictionary.AddModel`, which throws unless the class carries
`[Pool(typeof(...))]`. This is a *startup crash*, not a soft failure: it happens
during model construction and drops the game to an error screen. `KleeCardPool`
already declares membership in `GenerateAllCards`, so the correct answer is
`autoAdd: false` (opting out of a registration path we do not use), not adding
the attribute — which would register every card twice.

**Finding 15 — BaseLib prefixes custom model ids, silently moving loc keys.**
Deriving from `CustomCardModel` changed Kaboom's `Id.Entry` from `KABOOM` to
`KLEEMOD-KABOOM`. The hardcoded `KABOOM.title` strings then pointed at an id
nothing looks up, and the UI rendered the raw key. `JumpyDumpty`, still a plain
`CardModel`, was unaffected — which is what made the failure look selective.
**Ruling: custom models declare loc via the `ILocalizationProvider.Localization`
override, never via the hand-rolled dictionary.** BaseLib writes those against
`Id.Entry` itself (`AddModelLoc`), so the key cannot drift. The dictionary in
`KleeMod.cs` is now reserved for plain `CardModel` stubs only.

**Finding 16 — loose PNG card art works; no `.pck` required. CONFIRMED IN GAME.**
`Image.Load` on an absolute OS path + `ImageTexture.CreateFromImage`, returned
through `CustomPortrait`, renders correctly. Wiring the remaining card portraits
is mechanical. This does NOT extend to character art: `CharacterSelectIcon`
returns `CompressedTexture2D` and the select surface is `res://`-bound, so
character art still gates on the MegaDot editor.

**Finding 17 — the card-reward softlock is a rarity gap, not an empty pool.**
All four C1 cards are `CardRarity.Basic`. Reward and transform generation draws
Common/Uncommon/Rare, finds zero candidates, and leaves a screen that never
becomes dismissable. It is deterministic after every combat, not intermittent.
No workaround short of content: **the pool needs real Common/Uncommon/Rare
cards, which is the C2 slice.**

**Loc syntax, now observed rather than inferred** (via `LOCPROBE`, O5):
`STRIKE_SILENT.description` is `Deal {Damage:diff()} damage.` and
`DEFEND_SILENT.description` is `Gain {Block:diff()} [gold]Block[/gold].`
Single braces; `:diff()` renders the upgrade delta; `[gold]` is the keyword
highlight. Adopted for all four starters.

## Validator (2026-07-20)

Every bug above cost a debug cycle, and each was mechanically detectable. Two
layers, split by what is observable when:

- **`build/validate.ps1`** — gates `deploy.ps1`, runs against the *staged*
  package. S1 stray `*.json` (ModManager recursion), S2 manifest vs. shipped
  reality, S3 dependencies installed (note: workshop mods ship as `<Name>.json`,
  not `manifest.json`), S4 `Custom*Model` without `[Pool]` or `autoAdd: false`
  (finding 14), S5 doubled braces / unknown BBCode tags (findings 12-13).
- **`KleeCode/Diagnostics/KleeSelfCheck.cs`** — postfix on `ModelDb.Init` at
  `Priority.Last`. R1 empty `StartingRelics` (finding 11), R2/R3 empty deck and
  **pool rarity coverage** (finding 17), R4 loc keys resolved through the live
  `Id.Entry` (finding 15), R6 template syntax as it actually landed in the table.

The split is forced, not stylistic: `StartingRelics` is a computed property, loc
keys are rewritten by BaseLib at registration, and the loc tables ship
compressed inside the `.pck`. None of that is visible to a static pass.

The runtime half **never throws** — a validator that bricks the boot is the
failure mode it exists to prevent. Findings log as `SELFCHECK` errors.

S4 is a source regex, not a proof; proving it needs IL analysis of the base
constructor call. It catches the shape that shipped.

## Finding 18 — power icons cannot use the loose-PNG trick (2026-07-20)

Observed in playtest: BombPower renders the "Nope" missing-resource placeholder
under the enemy. This is NOT the same situation as card art, and the difference
is structural rather than a matter of shipping more files.

    public string PackedIconPath => ImageHelper.GetImagePath(
        "atlases/power_atlas.sprites/" + Id.Entry.ToLowerInvariant() + ".tres");
    public Texture2D Icon => ResourceLoader.Load<Texture2D>(PackedIconPath, ...);

Two independent blockers: `ResourceLoader.Load` resolves `res://` only, so an
absolute OS path cannot be handed to it; and the target is a `.tres`
AtlasTexture entry inside a packed sprite atlas, not a raw PNG, so there is no
image file to point at even in principle. BaseLib's `CustomPowerModel` offers
only path overrides (`CustomPackedIconPath`, `CustomBigIconPath`) and its patch
merely substitutes the string -- the load is still the base game's.

**Ruling: power icons join character art behind the `.pck` gate.** The Windows
MegaDot 4.5.1 editor download is therefore blocking more than the character
select surface, and its priority goes up accordingly.

UNVERIFIED lead, worth one experiment before accepting the gate: `Icon` returns
a `Texture2D`, so a Harmony patch on that getter could hand back an
`ImageTexture` built from a loose PNG, exactly as `KleeArt` does for cards. This
only works if the UI consumes `Icon` rather than resolving `PackedIconPath`
itself. BaseLib patches the *path* getter, which hints the path is what gets
consumed -- so this may not work. Do not assume it does.

Cosmetic only; bombs function correctly. Confirmed in playtest: Pop places a
bomb, it detonates early when the enemy is hit, and the debuff name renders.

**Finding 19 — O4 was overstated, and the safe fix is no fix.**
`CharacterModel.RunWonAchievement` really does evaluate
`Enum.Parse<Achievement>(Id.Entry.Capitalize() + "Win")`, and `KleeWin` really
is not a member of the enum -- but the property has **zero callers** in
sts2.dll or BaseLib.dll (checked `RunWonAchievement`, `WonAchievement` and
`get_RunWon*`), and every method on `AchievementsHelper` (`AfterRunEnded`,
`CheckTimelineComplete`, `CheckForDefeatedAllEnemiesAchievement`) is an empty
body in v0.107.1. Achievements are declared but not wired up. The property is
dead code, so it cannot throw in this build, and O4 was never a playtest
blocker.

Deliberately NOT patched. The `Achievement` enum has no `None`/`Invalid`
member -- the lowest value is `IroncladWin = 0`. Any Harmony patch that
swallowed the parse failure would have to return *some* real achievement, i.e.
silently grant the player a Steam achievement they did not earn. That is a
worse failure than a crash, because it is invisible and not locally
reversible. There is no safe return value, so the correct action is to leave
the landmine documented and disarmed by circumstance rather than to defuse it
wrongly.

Re-check when MegaCrit implements achievements. At that point this stops being
a null-safety question and becomes a design one -- what, if anything, a Klee
run completion should award -- which is a chat ruling, not a local edit.

Method note: this is the decompile-before-asserting rule catching one of our
own claims rather than an assumption about the base game. The original entry
inferred the crash from the source line alone and never checked for callers.

**Finding 20 — keyword tooltips: the Downfall pattern does not apply, and BaseLib
already has the real one.**
Finding 12 recorded that keyword tooltips "come from a per-mod
`card_keywords.json` (Downfall pattern)". That was carried over from StS1 and is
wrong here. Nothing in sts2.dll reads such a file. What actually exists:

- `CardKeyword` is a closed 8-member enum (None, Exhaust, Ethereal, Innate,
  Unplayable, Retain, Sly, Eternal). Not extensible by declaration.
- `CardKeywordExtensions.GetTitle/GetDescription` resolve against the
  **`card_keywords` loc table**, as `<slug>.title` / `<slug>.description`.
- BaseLib extends the enum at runtime: a `public static CardKeyword` field
  marked `[CustomEnum]` + `[KeywordProperties]` on a holder class gets an
  allocated ID during its `ModelDb.Init` prefix patch, registered into
  `CustomKeywords.KeywordIDs`. BaseLib then patches `GetLocKeyPrefix` to return
  the custom key and `HoverTipFactory.FromKeyword` to build the tip. The key is
  `<ModPrefix> + FIELDNAME.ToUpperInvariant()`, e.g. `KLEEMOD-BOMB`.
  `BaseLib.Cards.BaseLibKeywords.Purge` is the worked example.

One trap worth recording before anyone implements it: `AutoKeywordPosition`
`Before`/`After` push the keyword onto `AutoKeywordText.Additional*Keywords`,
which are **global lists appended to every card's text**. That is correct for
Exhaust-shaped keywords and wrong for Bomb/Spark, which are terms referenced
inside specific card descriptions. These want `AutoKeywordPosition.None`.

NOT implemented tonight, deliberately. The queue item asked for drafted strings
with placeholder wording, and those are done (`docs/card_keywords.json`, with a
`_mechanism` note pointing here). Registering custom enum values touches model
init -- the same surface that produced findings 14 and 9 -- and doing it
unattended hours before a playtest, to gain a hover tooltip, is a bad trade.
The API above is verified, so it is a cheap change to make deliberately.

**Correctness fix shipped alongside:** the drafted `bomb` tooltip said the charge
explodes "at the start of that enemy's turn". Canon (klee-character-design.md
§3) and our own `BombPower.BeforeSideTurnStart` both detonate at the start of
*Klee's* turn. Text corrected, and it now also states that bombs stack and each
keeps its own damage, which is the rule players are most likely to guess wrong.

---

## Finding 21 — Elite and Boss wins soft lock the run (FIXED)

**Found by playtest, 2026-07-20.** Reported as "duplicator on Jumpy Dumpty Mk.II
soft locks when bombs have no valid target". The card was a red herring — the
mechanic is unrelated and the bomb code is correct.

`ProgressSaveManager.CheckFifteenElitesDefeatedEpoch` (`sts2.decompiled.cs:36648`)
and `CheckFifteenBossesDefeatedEpoch` are closed type-switches over the six base
characters ending in `throw new ArgumentOutOfRangeException("character", ...)`.
`UpdateAfterCombatWon` calls the Elite one on `RoomType.Elite` and the Boss one
on `RoomType.Boss` (`:37003-37010`).

The call chain is `CombatManager.CheckWinCondition -> EndCombatInternal ->
SaveManager.UpdateProgressAfterCombatWon -> UpdateAfterCombatWon`. The throw
escapes into an async continuation, so `EndCombatInternal` never completes:
enemies dead, win logged ("CHARACTER.KLEE fought ENCOUNTER.PHROG_PARASITE_ELITE
... and WON"), combat never ends, End Turn does nothing, run unrecoverable.
No crash dialog — it surfaces only in `godot.log`.

Severity: **every elite and every boss**, deterministic, not a rare interaction.
The playtest reached it on the first elite. It was reachable from the moment
Klee became selectable and no test we own could have caught it, because both
Tier 0 and the self-check model our code, not the base game's progression
tracking.

### The actual root cause — we had opted out of BaseLib

The first fix was a `[HarmonyFinalizer]` suppressing that exception. It worked,
and it was treating a symptom.

BaseLib **already patches all three** of these methods
(`BaseLib.decompiled.cs:20058-20084`) with a prefix reading
`return !(localPlayer.Character is ICustomModel);`. It never fired because
`Klee` derived from the game's `CharacterModel` rather than BaseLib's
`CustomCharacterModel`, and `ICustomModel` is what
`CustomCharacterModel` implements.

**BaseLib gates 29 guards on `is ICustomModel`. None of them were active for
Klee.** Beyond the three epoch methods: `SavedProperties` (×3, save/load for
custom models), `CharacterModel.GenerateAnimator` (×3 — the path Klee.cs
assumes "just works"), `CardModel.CostsEnergyOrStars` (×3), `NPotionLab.
LoadPotions` (×3), `ModelDb.GetEntry`, `NCardLibraryGrid.RefreshVisibility`,
`ImageHelper` room icons (×2), and `AchievementsHelper.
CheckForDefeatedAllEnemiesAchievement`.

**This retires O4.** We reasoned at length about whether patching an
achievement method was worth the risk of granting an unearned Steam
achievement. BaseLib had already solved it; the dilemma existed only because we
were off the mechanism that reaches the solution. The lesson is not about
achievements — it is that deriving from the raw game type **compiles, boots,
and plays**, and the only signal that anything is wrong arrives as an unrelated
soft lock hours later.

**Real fix:** `Klee : CustomCharacterModel`. It declares no abstract members of
its own — every member is virtual with a default — so the migration is a base
type change plus a `using BaseLib.Abstracts`, and there was never a cost to
being on the right type.

**`ModelDb_AllCharacters_Patch` stays.** Checked before assuming: BaseLib does
not append custom characters to `ModelDb.AllCharacters`. It transpiles call
sites to a `VisibleCharacters` filter (`:39172`, `:39484`) that *removes*
characters flagged `HideFromVanillaCharacterSelect`. Nothing adds them, so our
postfix is still the mechanism that makes Klee appear — and there is no
double-add.

**The finalizer is kept as a canary,** not as the fix. Post-migration BaseLib's
prefix short-circuits both methods, so the finalizer can no longer be reached;
it now logs at WARN if it ever is, which would mean the guard has stopped
applying to Klee. Cheaper detector than another soft locked playtest.

**Class of bug, for the C3 sweep:** base-game code that switches on a closed
character set. `ObtainCharUnlockEpoch` (`:36990`) is the same shape but safe —
it builds an epoch id by string concat and logs on miss. Others are likely.
Worth a decompiler sweep for `ArgumentOutOfRangeException("character"` before
the next milestone rather than finding them one playtest at a time.

## Standing rule — sweep before building (2026-07-20, chat ruling)

**Before building infrastructure or reasoning around a limitation, sweep
BaseLib and the decompiled game for an existing solution.**

Codified from the morning triage after three hits in one night, each of
which would otherwise have been built or agonized over redundantly:

1. **The achievement guard** (O4): a long risk analysis about patching an
   achievement method, dissolved by `AchievementsHelper`'s existing
   `ICustomModel` guard.
2. **The character-model guards** (finding 21): 29 separate BaseLib guards
   gated on `is ICustomModel`, all forfeited silently by deriving from raw
   `CharacterModel`. The soft lock was the *last* symptom, not the first.
3. **RunHistory** (Tier 1): the planned telemetry writer was already
   written — by MegaCrit. `CreateRunHistoryEntry` records more per run
   than our design specced, for modded profiles too.

The pattern behind all three: the base game and BaseLib are mature
codebases whose authors hit our problems first. The cost of a sweep is
minutes; the cost of missing the existing mechanism ranges from redundant
code (best case) to hours-later soft locks with misleading symptoms
(finding 21). The sweep is now a required step, same standing as "read
the decompiled reference before patching."

---

## Finding 23 — the finding-21 migration renamed Klee's id, and two consumers hardcoded the old one (FIXED)

**Found by playtest, 2026-07-20** ("Klee is a black box in character select and
can't be picked"). Regression introduced by the finding-21 fix: deriving from
`CustomCharacterModel` puts Klee through BaseLib's id prefixing, so `Id.Entry`
changed from `KLEE` to `KLEEMOD-KLEE` — exactly the rename R4 documents for
cards, applied to the character we forgot also has an id.

Two places still assumed the unprefixed id:

1. **`KleePlaceholderArt`** rewrote asset paths with
   `Replace(KleeMod.ModId, "ironclad")`. Every path embeds
   `Id.Entry.ToLowerInvariant()`, so `char_select_kleemod-klee.png` became
   `char_select_ironcladmod-ironclad.png` ("klee" matches twice) — godot.log:
   `ERROR: No loader found for resource: .../char_select_ironcladmod-ironclad.png`.
   Black select icon, and selection dead because the select surface can't load
   her assets. Fix: replace the live `Id.Entry.ToLowerInvariant()` instead, so
   the substring is by construction the one the paths contain.

2. **Character loc** was still merged under `KLEE.*` in `InjectLocStrings`.
   Fix: moved onto the model as a `Localization` override — BaseLib's
   `AddModelLoc` writes against `Id.Entry` itself, so the keys cannot drift.
   This is the same split the cards already follow; the character was the
   remaining hand-rolled holdout.

**The self-check caught half of this at boot.** `[R5] missing loc key
"KLEEMOD-KLEE.title"` was in the log before anyone clicked character select.
The art half had no rule: R-rules validate models and loc, not asset-path
resolution. If placeholder art outlives the next milestone, a rule that
resolves the select-icon path against the pack would close that gap.

**Not fixed, known:** the progress save carries `CharStats` under
`CHARACTER.KLEE` from pre-migration runs; the game logs a non-fatal
`Unknown character ID` warning and Klee's prior stats don't carry over to
`CHARACTER.KLEEMOD-KLEE`. Cosmetic for a dev profile; a save migration is not
worth writing unless we rename ids again.

**Ruled out during diagnosis:** stale deploy. The deployed dll (built 11:21)
already contained ffd0941 — the log shows R5-labelled findings and the
reward-draw clamp, both of which only exist post-ffd0941. The newest code was
running; the newest code was the regression.

**Class of bug:** an id is an API. Anything that changes `Id.Entry` — base
type migrations especially — must be followed by a sweep for consumers of the
old spelling (loc keys, asset paths, save data, epoch strings). R4/R5 cover
loc; paths and saves have no rule yet.

---

## Finding 24 — every shop soft locks: the merchant unconditionally stocks a Power slot (FIXED)

**Found by playtest, 2026-07-20** — first playtest to reach a shop; black
screen on entry, no crash dialog. Pre-existing since the C2 pool landed, NOT a
regression from findings 21/23: Klee's 24 cards contain zero Power-type cards,
and nothing before this playtest ever entered a merchant.

`MerchantInventory.PopulateCharacterCardEntries` stocks a hardcoded slot
layout from the character pool — `{Attack, Attack, Skill, Skill, Power}` —
and `CardFactory.CreateForMerchant(player, options, type)` rolls a rarity
that must contain a card of the requested type. `GetNextAllowedRarity` wraps
Common→Uncommon→Rare and returns `None` when no rarity qualifies, and the
method throws. godot.log:

    InvalidOperationException: Can't generate valid rarity for merchant card
    type Power with card options: CARD.KLEEMOD-ALCHEMICAL_CURIOSITY, ...
      at CardFactory.CreateForMerchant → MerchantCardEntry.Populate
      → MerchantInventory.CreateForNormalMerchant → MerchantRoom.EnterInternal

The throw escapes into `MerchantRoom.EnterInternal`'s async continuation —
the same swallowed-async shape as finding 21 — so the room never finishes
entering. Deterministic on every shop until the pool stocks a Power.

**Fix:** prefix on `CreateForMerchant` that substitutes a type the pool does
stock (fallback order Skill → Attack → Power; Skill is the closer analogue of
a Power purchase). Substituting rather than emptying the slot because the
5-slot layout is load-bearing — `Populate` has no "no card" path. The
eligibility test mirrors the method exactly: Basic excluded, and only
Common/Uncommon/Rare count, because the shop roll can produce nothing else
(R3a reasoning). The patch self-retires the moment Klee's pool contains a
Power card. Base characters stock every type and never hit the fallback.

**Self-check:** new rule R3d fails the boot check when any of Attack/Skill/
Power is missing from the generatable pool. This gap was knowable statically
— the merchant layout is a constant — and R3d would have flagged it before
the playtest.

**The real fix is content:** Klee needs Power cards on the sheet. Logged as a
C3 item; until then R3d keeps reporting the truth (some shop slots sell a
different type than designed).

**Class of bug, same family as findings 21/22:** base-game code that assumes
base-character pool shape (closed character switches, pool-size floors, and
now per-type coverage), throwing inside async continuations where the failure
surfaces as a hang, not a crash. The C3 decompiler sweep should also grep
factory methods for `InvalidOperationException` with pool-shape preconditions.

---

## Finding 25 — art plan predated the C2 sheet: 8 shipped cards had no sourcing rows (FIXED)

The BETA placeholders the 2026-07-20 playtest showed were not pipeline
failures: `alchemical_curiosity`, `bombs_away`, `cluster_charge`,
`double_pop`, `flame_on_the_wick`, `jumpy_dumpty_mk2`, `no_holding_back` and
`run_away` simply had **no rows in art/plan.tsv** — the plan was written
against an earlier card list. Rows added as provisional `auto` picks reusing
already-resolved wiki titles (demote to `shortlist` for a taste pass any
time); same for the spark-set additions when they shipped (snap, da_da_da,
hot_hands, warm_glow, all_my_treasures). All 33 shipped cards now have
portraits.

**Tool fix that rode along:** `art_fetch.py` rewrote SOURCES.tsv from
scratch out of the current API resolution, and the Fandom API returns
PARTIAL batches under rate limiting — one flaky run truncated the release
checklist from 115 rows to 30 (restored from git). The fetch now MERGES by
filename instead of rewriting, and single-file fallback goes through
`Special:FilePath` (which, note, serves WebP under .png names — Pillow
sniffs content, so processing is unaffected).

## Finding 26 — Sparks, Pounding Surprise, and the spark card set (C3 gap-list unlock #1)

**SparkPower** (player Buff/Counter): while at 3+ Sparks the player's
Attacks cost 0; playing an Attack with nonzero PRINTED cost at threshold
consumes 3. Cost side rides `Hook.ModifyEnergyCostInCombat` via the
`TryModifyEnergyCostInCombat` virtual — CardEnergyCost consults the same
hook for display and payment, so cards visibly read 0 in hand with no UI
patch. Spend side is `AfterCardPlayed` on the same power. Reference:
tier0/engine/combat.py `card_cost`/`play_card`.

**Known divergence from the sim, deliberate:** X-cost attacks are EXEMPT
(sim applies sparks to them). Zeroing an X-card sets X=0 and turns the buff
into a trap; both X-cost cards are blocked on X support anyway, so nothing
observable differs. Reconcile when X-cost lands.

**Detonation event bus** (csharp-build-spec item 2): `BombPower.Detonate`
notifies `IBombDetonationListener`s — discovered by interface over the
applying player's relics and creature powers, once PER BOMB (sim grants the
spark inside the per-bomb loop). Blazing Delight subscribes here when its
power lands.

**Pounding Surprise** (`CustomRelicModel`, Starter, autoAdd: false per
finding 14): +1 Spark per detonation, own-bombs-only in co-op. Replaces the
Burning Blood stub in `Klee.StartingRelics`. Icon borrows Burning Blood's
atlas slug — relic icons are `.tres` atlas entries, so finding 18's `.pck`
gate applies to relic_atlas identically; no collision since the relic it
borrows from is the one it replaces.

**Codegen learned `gain_spark`** (literal amount — no base-game DynamicVar
renders a Spark count, and finding 15 says don't invent placeholder names)
**and `exhaust: true`** (`CanonicalKeywords => Exhaust`; needed the moment
da_da_da/all_my_treasures unblocked — every earlier exhaust card was
blocked, so the gap was invisible). Pool grows 24 -> 33: the 8 spark cards
plus Snap! (sheet v0.6, M8/R1). Rare tier is now 3 deep (was 1).

**Open (M9 ask): upgrade shape for pure-spark cards.** sparkly_treasure and
spark_collection emit an empty OnUpgrade — a literal amount cannot render
an upgrade delta, and an invisibly-changing number is worse than none.
Flagged in Generated/manifest.json `upgrade_defaults`.

## M8 rulings — what binds this build (2026-07-20)

- **R10 (Crackle +gain_spark):** authorized SIM-SIDE in its own measurement
  window; sheet v0.6 does NOT yet carry it. The C# build now has everything
  needed (`gain_spark` op) — when the sheet lands the buff, `gen_klee_cards
  .py` regen picks it up with zero code changes. Do NOT hand-add it first.
- **R11 (upgrade deltas):** ruling-supplied upgrade values are DELTAS.
  Codegen already conforms (`UpgradeValueBy`); manifest `upgrade_defaults`
  comment now states it.
- **R9/R12–R15:** sim-side only (spark online definition, shining_idol,
  divergence note, upgrade economy, R8 aftermath). No build action; R14's
  "dose cells are diagnostics, never acceptance targets" applies to any
  future build-vs-sim comparison we quote.

---

## Finding 27 — two Klees in character select, and neither selectable (FIXED; corrects finding 21)

**Found by playtest, 2026-07-20 (post-Sparks deploy).** Two Klee tiles on the
select screen; clicking either updated the panel but the run would start as
the previously selected character. Suspected Furina-stream contamination;
was not — both halves were klee-mod's own.

### Half 1 — the duplicate: finding 21's "no double-add" verification was WRONG

BaseLib's `AddCustomCharacters` postfix appends every
`CustomContentDictionary.CustomCharacters` entry to `ModelDb.AllCharacters`
— unconditionally, no duplicate check. Klee has been in that dictionary
since the CustomCharacterModel migration (the base ctor registers her), so
BaseLib appended her AND our `ModelDb_AllCharacters_Patch` appended her.
Its `Contains` guard did not save it: the guard sees the enumeration state
at ITS patch position, and the two appends are separate postfixes.

**Correction of record for finding 21:** "Checked before assuming: BaseLib
does not append custom characters" found the `GetVisibleCharacters` FILTER
transpiler and stopped there. The append lives in a different patch class
(`AddCustomCharacters`, undecodable attribute args in the decompile — the
sweep grep missed it). The duplicate appeared the moment finding 21's
migration landed and hid in plain sight among the other mods' tiles until
today's shorter roster made it obvious.

**Fix: the mod-side append patch is DELETED.** Registration is BaseLib's job
for ICustomModel characters — that is the same lesson as finding 21 itself,
one layer up: we were duplicating a mechanism BaseLib already owns.

### Half 2 — unselectable: Pounding Surprise was in no relic pool

`RelicModel.Pool` is non-virtual `AllRelicPools.First(p =>
p.AllRelicIds.Contains(Id))` and it runs inside
`NCharacterSelectScreen.SelectCharacter` (DynamicDescription -> energy icon
lookup). A relic in NO pool throws `InvalidOperationException: Sequence
contains no matching element` right there — godot.log caught it — aborting
SelectCharacter after the panel text updates but before the lobby
assignment. Finding 11's looks-selected-but-is-not failure, reached through
a relic instead of an empty StartingRelics. The screenshot even showed the
mid-throw state: Pounding Surprise's TITLE with the Necrobinder relic's
DESCRIPTION ("Summon 1") — stale widget data from the aborted update.

**Fix: `KleeRelicPool`** — Silent's borrowed contents plus Pounding
Surprise, wired via `Klee.RelicPool`. `AllRelicPools` derives from
`AllCharacters.Select(c => c.RelicPool)`, so the override is the entire
registration. Reward safety: relic rewards never roll Starter, so the relic
cannot drop as loot; Silent relics still resolve their Pool to
SilentRelicPool because Silent precedes Klee in AllCharacters.

**Self-check: new rule R7** — every starting relic must resolve `.Pool`
without throwing. This was knowable at boot; R1 checked non-empty and
stopped one property short of the one that throws.

**Class of bug, again:** non-virtual base-game getters with closed-world
assumptions (`First()` with no fallback), throwing inside UI/async flows
where the symptom is a half-updated screen, not a crash. Siblings: findings
11, 21, 24.

---

## Finding 28 — first-encounter softlock: `new()` on an AbstractModel (FIXED, 915dd0e)

**Found by playtest, 2026-07-20 (first combat after the R23 deploy).** Combat
start hung with no crash. godot.log had the real story:
`TypeInitializationException` wrapping `DuplicateModelException: Trying to
create a duplicate canonical model of type KleeMod.Powers.KleeElementalHooks.
Don't call constructors on models! Use ModelDb instead.`

The new combat-hook subscriber held its singleton as
`private static readonly KleeElementalHooks Instance = new();`. But ModelDb
scans the mod assembly and constructs one canonical of EVERY AbstractModel
subclass itself — the `new()` in our field initializer was the duplicate.

**Fix:** resolve the canonical lazily inside the subscriber delegate —
`_instance ??= ModelDb.GetById<KleeElementalHooks>(ModelDb.GetId<...>())`
(lazy because mod `Initialize` can run before the ModelDb scan).

**Ownership family (finding 27's lesson, one layer down):** ModelDb owns
model construction the way BaseLib owns character registration. If a
mechanism has an owner, calling it yourself is the bug — the engine's own
exception message says so verbatim. Siblings: findings 21, 27.

**New symptom family worth naming:** a static-initializer exception is
CACHED by the runtime as `TypeInitializationException` and re-fires on
every subsequent touch of the type. Here that meant the throw re-fired
inside every combat hook broadcast — hanging the async command pipeline —
so the crash site (every hook iteration) was arbitrarily far from the
fault (one `new()` in a field initializer). When a log shows the same
TypeInitializationException storming from unrelated call sites, read the
INNER exception of the FIRST occurrence; everything after it is echo.
Corollary: keep AbstractModel statics trivial — anything that can throw
belongs in a lazy path where the exception surfaces once, at a call site
that names the actual problem.
