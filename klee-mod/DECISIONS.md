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

> **CLOSED by R34 (user-ratified 2026-07-20):** the sim adopts the C#
> exemption — `card.cost == "X"` is exempt from the spark-spend branch in
> tier0 `play_card` (the verified hazard: an X attack at 0 energy tripped
> the spend predicate and whiffed the whole bank for an X=0 cast), with
> `test_x_cost_attack_never_spends_sparks` pinning it. No divergence
> remains. Standing obligation unchanged: when X-cost lands C#-side, the
> SparkPower gate must carry the same exemption — which it already does;
> the codegen X-guard keeps any drift from shipping silently.

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

---

## Burst-energy spike — the meter lands (standing plan item 2, 2026-07-20)

**The CustomResource shape won.** BaseLib auto-registers every concrete
`CustomResource` subclass at early post-init (reflection scan over mod
types → `CustomResources<T>.Register`) — finding 28's ownership family
again: we define `KleeBurstResource`, we never register it. Instances are
per-player per-combat, created lazily by BaseLib's SpireField;
`BasicCustomResource.PrepForCombat` zeroes them, which is exactly the
sim's per-fight reset. The cost machinery is verified for the Burst card
later: `SetCanonicalCost(card, 60)` gates playability through
`CanAfford`/`UnplayableReason`, and `Spend` is virtual so casting can
reset the meter to 0 (sim law: overflow is lost at cast, not at gain).

**BaseLib ships NO ambient meter UI.** Its resource UI is cost-side card
visuals only; `BasicResourceVisualsHandler` is an empty marker interface
with no consumers. So the meter renders as `BurstMeterPower` on Klee —
the SparkPower display idiom. The resource is CANONICAL, the badge is
DISPLAY, and `KleeBurstResource.Gain` is the only writer of either; that
sync invariant must survive when cast lands.

**The economy is LAW (R23 note):** BurstConstants mirrors tier0 —
BURST_PER_SKILL_TAG 5, BURST_PER_REACTION 5, klee.yaml burst_max 60.
Accrual is deliberately uncapped past 60 (sim never clamps; the grant
check is >=).

**Two funnels, both single:** skill tags gain in
`KleeElementalHooks.BeforeCardPlayed` (see the correction below);
reactions gain at the top of `ReactionEffects.Resolve`, which every
reaction passes through exactly once (AuraPower and BombPower.Detonate
both route there), amplifiers included because the sim credits any NAMED
reaction. The funnels are exhaustive TODAY, not forever — the sim's gain
sites are greppable (`burst_energy +=` in tier0/engine): beyond the two
funnels and the burst_energy op, Klee-reachable content still to land
must carry its own gain line — the detonation-splash power's
DETONATION_SPLASH_BURST (effects.py) and Catalytic Conversion's
CATALYTIC_BURST_PER_REACTION * bonus (reactions.py). Two further engine
sites (encore spend, Salon tick) are Furina-stream mechanics Klee never
reaches.

**CORRECTION (2026-07-20, review catch): the skill-tag phase claim above
was wrong as shipped.** The spike originally gained in `AfterCardPlayed`
and recorded "post-resolution, the same phase as play_card's tag check" —
but tier0's play_card adds BURST_PER_SKILL_TAG BEFORE resolve_card (and
before its replay loop; combat.py, the `skill_tag in card.tags` check
sits above `for _ in range(replays)`). Outcome-identical while burst is
pure accumulation, but load-bearing the moment anything rules on the
meter mid-play (the kit grant, a "if meter full" effect). Fixed same day:
the gain moved to `BeforeCardPlayed` gated on `cardPlay.IsFirstInSeries`
— the game fires card hooks once per replay in a series, so the gate is
what reproduces the sim's once-per-play_card grant (the unguarded hook
was ALSO a latent double-grant under future Replay effects; no current
pool card replays, so nothing shipped wrong). `BeforeCardPlayed` carries
no PlayerChoiceContext, so the invariant is now: resource moves
pre-resolution via `GainPreResolution` (context-less ModifyAmount), the
badge catches up in `AfterCardPlayed` via `SyncBadge` (sync-to-truth,
self-healing). The badge may lag the resource only WITHIN a single card
play; rules read the resource, never the badge.

**Deliberately deferred to the power-card pass:** the kit-grant machinery
(grant-to-hand at >= 60, hand-size deferral, Retain) and Sparks 'n'
Splash itself — the Burst lands LAST per the standing plan. Until then a
full meter is visible and spends nothing, which is honest.

**Unblocked by the burst_energy op:** combustion_study AND clockwork_toy
(pool 37 → 39). Sheet `skill_tag` now emits an `ISkillTagCard` marker
(codegen) — Pop is the one hand-written carrier, and the parity lint
gained a tag-parity check so a missing marker (= silently no burst
energy) is a deploy-gate failure, not a playtest surprise.

## Power-card pass — nine kit powers land (standing plan item 3, 2026-07-20)

**Scope:** every sheet power card except Sparks 'n' Splash (kit card, lands
LAST with the grant/cost machinery). Nine PowerModels, each hooked at the
C# site matching its tier0 read site; the codegen `apply_power` op; pool
39 → 48. All numbers LAW from tier0 — mirrored, never re-derived.

**The powers and their read sites:**
- `BombDamageUpPower` (Explosives Workshop, cap 4): read in
  `BombPower.Detonate`, added BEFORE amplification — the sim totals
  `bomb.damage + bonus + bomb_damage_up` and only then enters the
  elemental pipeline.
- `DetonationSplashPower` (Blazing Delight): `IBombDetonationListener` —
  the bus BombPower already had. Per BOMB; splash is element-less and
  block-bypassing (sim: raw `hp -=`), hence Unblockable|Unpowered; the
  +3 Burst sits INSIDE the 3-procs/turn gate (a capped detonation grants
  nothing); the counter resets at player side-turn END, equivalent to the
  sim's turn-start reset because nothing can proc between the two.
- `DetonationVulnPower` (Explosive Frags): same bus, applies Vulnerable
  to the detonated enemy only if it survived (sim: `if enemy.alive`).
- `BombAndSparkPerTurnPower` (Playtime Forever, cap 1): turn-start bomb
  (PLAYTIME_BOMB_DAMAGE 5) on a random enemy + 1 Spark; the Spark is
  unconditional, the bomb needs a living target — sim's exact branch.
- `SparkPerTurnPower` (Endless Fireworks): turn-start Sparks.
- `ZeroCostAttacksUpPower` (Spark Knight Style, cap 4): the sim's
  predicate is PAID cost == 0, not printed — `EnergyCost.GetResolved()`
  is the game's own after-play cost accessor (IntimidatingHelmet
  precedent) and reads 0 mid-resolution for Spark-freed attacks because
  the Spark spend is post-resolution.
- `SparkThresholdDownPower` (True Spark Knight): pure marker.
  `SparkPower.CurrentThreshold` = max(1, 3 − stacks), read at BOTH the
  cost gate and the spend so they can never disagree (the sim calls
  spark_threshold(state) at both sites too).
- `ReactionBonusSparkEnergyPower` (Catalytic Conversion): read in the
  `ReactionEffects.Resolve` funnel right after the flat +5 — same single
  funnel, so it can neither miss nor double-count. **NO upgrade path:**
  tier0's upgrade engine marks it UNAPPLIABLE
  (CATALYTIC_BURST_PER_REACTION is a constant), so the sheet upgrade was
  never measured — hot_hands disposition, awaiting user ruling.
- `AmpReactionUpPower` (Vermillion Pact): percent on the amplifier. New
  dealer-aware `ReactionTable.AmplifierMultiplier(reaction, dealer)` =
  `base * (1 + pct/100)`, additive with future witchs_flame — and it now
  owns the 4x amp-cap detector (moved from AuraPower; the boosted
  multiplier is the one that can run away). Both amp sites (AuraPower
  hit amplification, BombPower detonation) pass the dealer.

**Stack caps** are enforced in `TryModifyPowerAmountReceived` (the sim
clamps at apply in powers.py, POWER UNITS), and the cap is deliberately
double-entered: the C# const enforces, codegen cross-checks the sheet's
max_stacks against its registry and hard-fails the regen on drift.
Blazing Delight's proc cap gets the same treatment.

**Codegen:** `apply_power` op (registry: sheet power id → C# class, cap,
card-text template; self-target only this pass), and the four power
upgrade keys — power_amount / amp_percent / splash_damage / vulnerable —
all meaning "bump the applied amount" (tier0 upgrades.py handles them in
one branch too), rendered via DynamicVar("PowerAmount") only when a
ruled delta exists. Unknown apply_power fields fail loudly (UNPARSEABLE).
The kit card is blocked on `kit_card`/`requires:` explicitly.

**Delivered content unblocked:** blazing_delight, catalytic_conversion,
endless_fireworks, explosive_frags, explosives_workshop,
playtime_forever, spark_knight_style, true_spark_knight, vermillion_pact.
Six needed new portrait rows (the art sprint predates their unblock) and
all nine needed badge icons — three came off the constellation redirect
queue (Nova Burst, Blazing Delight, Explosive Frags), the rest are item
renders; all flagged for red-pen in plan.tsv comments.

**Forward obligations discharged:** the burst gain-site map from the
phase-correction entry is now two entries shorter — detonation-splash
burst and Catalytic Conversion both carry their gain lines. Remaining
sim gain sites are Furina-stream only (encore, Salon).

## Kit-grant sprint -- Sparks 'n' Splash lands (standing plan item 3 closes, 2026-07-20)

The power-card pass's deliberately-last card. The Burst is kit, not loot
(tier0 v1.9): never draftable, granted to hand when the meter fills,
casting empties the whole meter, and a refill re-grants it. Everything
below is a port of `grant_charged_kit` / `play_card` (combat.py) and
`player_turn_end_triggers` (effects.py); constants LAW
(SPARKS_N_SPLASH_HITS=4, HIT_DMG=5, burst_max=60, turns=3 from the sheet).

**Cost model (BaseLib CustomResourceCost).** The card costs 3 energy AND
the full meter. `CustomResources<KleeBurstResource>.SetCanonicalCost(card,
60)` in the ctor wires BaseLib's registered ResourceHandler: `CanAfford`
(Amount >= 60) joins the game's own playability check -- the sim's
`requires: burst_energy_full` gate -- and the play pipeline calls
`Spend`. `KleeBurstResource.Spend` is overridden to drain `Amount` (the
WHOLE meter), not the canonical 60: sim law is `p.burst_energy = 0` at
cast -- overflow is lost at cast, never clamped at gain. The ctor site
covers clones (BaseLib's canonical-cost SpireField is CopyOnClone).

**Grant machinery (`KitGrant.GrantIfCharged`).** Port of
grant_charged_kit's three rules: full meter only (>=, uncapped accrual);
no duplicate while a copy is in hand; full hand DEFERS (meter stays full,
grant retried at the next check) -- load-bearing because the game's own
`AddGeneratedCardToCombat` on a full hand redirects to DISCARD
(CardPileCmd), which would recirculate the Burst as loot, the exact bug
the sim's regression test forbids. Creation is the first-party Shiv
idiom: `combatState.CreateCard<SparksNSplash>(owner)` +
`AddGeneratedCardToCombat(PileType.Hand)`. A fresh instance per grant is
the game-side reading of "returns to the kit, no pile": a played Power
leaves combat entirely.

**Check sites (KleeElementalHooks), the sim's three call sites:**
- `AfterPlayerTurnStart` -- the game fires this AFTER the hand draw
  (CombatManager: energy, draw, then the hook), the sim's exact
  turn-start phase; turn-start meter gains (Blazing Delight splash on
  detonation) land earlier, in BeforeSideTurnStart.
- `AfterCardPlayed` -- after every play, like the sim's end-of-play_card
  call; also now runs the badge sync UNCONDITIONALLY (sync-to-truth is a
  no-op when in sync, and the cast's meter drain happens in the cost
  machinery where no Klee call site sees it).
- `BeforeSideTurnEnd` (player side) -- maps to Hook.BeforeTurnEnd, which
  fires BEFORE the hand flush; mod-model hooks run after power hooks in
  the same broadcast, so the volley (and any reactions it raised) has
  already resolved, the sim's end-triggers-then-grant order. Retain
  carries the granted card through the flush.

**The power (`SparksNSplashPower`).** Amount = turns remaining (3). At
`BeforeSideTurnEnd`: 4 hits of 5, each to a random living enemy
(re-snapshot per hit; `Rng.CombatTargets.NextItem`, the shipped
turn-start-power idiom), each a full Pyro hit through the BombPower
Detonate pipeline -- element resolved first (apply/refresh/react,
Vaporize/Melt amplify the hit, reactions grant burst + Catalytic through
the normal funnel), then `CreatureCmd.Damage` Unpowered with no card
source. Unpowered + sourceless is also what keeps volley hits from
early-detonating bombs, mirroring `_detonate_bombs_on_hit`'s
`source == "attack"` gate for free. Volley first, THEN
`PowerCmd.TickDownDuration` -- the sim decrements after the hits.

**Retain** via `CanonicalKeywords` (the game auto-renders the keyword
text); the sim's turn-end filter keeps burst-tagged cards in hand and the
game's FlushPlayerHand honors Retain identically.

**Enforcement widened with the mechanism, per the lint's own charter:**
sparks_n_splash joins HAND_WRITTEN; lint_handwritten_parity gains an
`apply_power` rule (amount -> DynamicVar multiset) plus two structural
checks -- sheet `kit_card`/`requires` must land as `SetCanonicalCost`
(no resource cost = no gate, no spend) and sheet tag `burst` as
`CardKeyword.Retain`. Upgrades sheet says NO UPGRADE (kit card; Talent
Training = v2 design space): empty OnUpgrade, unreachable anyway since
the kit card is never in the deck. gen_klee_cards' kit guard stays for
FUTURE kit cards (loud, "hand-write it against the KitBurst machinery").

**Art:** power badge = the ability's own wiki talent icon (Talent Sparks
'n' Splash.png, native 128px icon register, x2.0 upscale -- flagged
red-pen with the rest). Card portrait row (Klee Full Wish splash)
predates this sprint.

**Not ported, recorded:** the sim exempts kit cards from random
discard/exhaust-from-hand victim pools (test_random_discard_cannot_touch
the_kit_burst). No Klee card ships a random hand discard today, so there
is no game-side victim pool to filter; the FIRST discard/exhaust_from op
that lands C#-side must add the kit exemption or it recreates the sim's
regression. Codegen still blocks those ops, so the gap cannot ship
silently.

## Playtest-fix + rulings batch -- softlock, keyword, R34-R37 (2026-07-20 night)

**Campfire softlock, root-caused and fixed.** godot.log showed it plainly:
BaseLib's scene-conversion registry is keyed by PATH, and sharing
`character_sprite.tscn` between `CustomRestSiteAnimPath` and
`CustomMerchantAnimPath` made the merchant registration overwrite the
rest-site one ("Overwriting scene registration ... NRestSiteCharacter ->
NMerchantCharacter" -- BaseLib warned at startup). The campfire then
instantiated an NMerchantCharacter, `NRestSiteCharacter.Create`'s cast
threw inside `NRestSiteRoom._Ready`, and the room never finished setup.
Fix: build_pck emits an identical scene under a second path
(`rest_character.tscn`); the rest site points there. Lesson recorded in
Klee.cs: one conversion registry entry per scene path, ever.

**Known-benign merchant error, accepted:** `NMerchantCharacter._Ready`
unconditionally builds a MegaSpineBinding on its first child and throws
on a static Sprite2D ("Expected BoundObject to be a SpineSprite"). The
Godot bridge logs and swallows it; the sprite renders, only the
`relaxed_loop` idle is lost. Unfixable without patching game code.

**ElementalSkill keyword (playtest finding: skill_tag was invisible).**
BaseLib custom keyword: `[CustomEnum("elemental_skill")]` +
`[KeywordProperties(AutoKeywordPosition.After)]` static CardKeyword field
(KleeKeywords.cs) -> key KLEEMOD-ELEMENTAL_SKILL; loc rows ship in the
pck at `klee/localization/eng/card_keywords.json` (the game merges
modded loc JSON per-table; verified in LocManager.LoadTablesFromPath).
Renders a gold "Elemental Skill." line + hover tip on all 16 skill_tag
cards (codegen emits it beside ISkillTagCard; Pop hand-carries it;
parity lint enforces the pairing). DISPLAY ONLY -- gameplay still reads
ISkillTagCard. Badge description reworded to name the keyword.

**R34 executed (X-cost spark exemption):** tier0 play_card exempts
`cost == "X"` from spark spend (verified hazard: X attack at 0 energy
tripped the paid-0/printed-nonzero predicate and whiffed the bank on an
X=0 cast); test pins it. The finding-26 divergence entry is CLOSED --
sim now matches the C# exemption; the codegen X-guard keeps drift loud.

**R35 executed (Blazing Delight reset):** proc-cap reset moved from
side-turn END to BeforeSideTurnStart (player side), structurally the
sim's zero-at-turn-start-before-bombs. Ordering proof: hook listeners
iterate allies before enemies, so the player-power reset always precedes
enemy BombPower detonations in the same broadcast.

**R36 executed (Crackle redesign):** the band-breaching R10 buff is
dead; Crackle = damage 3 + `discard_for_sparks {amount: 1, sparks: 1}`
(forced player-chosen discard, 1 Spark per card ACTUALLY discarded,
empty hand = no Spark, kit cards exempt fodder). Upgrade deltas
{discard: +1, sparks: +1}; the old damage delta died with R10. New tier0
op with shared worst-card heuristic (instrument surface, noted); pilot
unchanged. **Measurement window RUN (1000 fights, seed 42): all
ratified winrate bands hold; spark_weighted vs tank_boss = 56.8% inside
[45%, 65%]** (the R10 buff had hit 66.8%). The CCM + dodge_roll errata
batch may now land per the standing sequencing (window has run).
C# side: codegen learned `discard` (random victim, kit-exempt pool --
bright_idea unblocks, pool 48 -> 49, art shortlist flagged red-pen) and
`discard_for_sparks` (CardSelectCmd.FromHandForDiscard, the
MockDiscardAndAddShivsPotion idiom: forced pick of N, auto-select-all on
short hand, kit-exempt filter). **The kit-exemption forward obligation
above is DISCHARGED** by KitGrant.NotKitCard, the filter both ops ride.

**R37 executed (Catalytic Conversion upgrade = Innate):** upgrade delta
is now `{innate: true}` -- sim-expressible (tier0 Card.innate +
surface_innate: innate cards top the shuffled draw pile), so the R24
no-unmeasured-upgrades law is SATISFIED, not waived; catalytic_conversion
left UNAPPLIABLE. **Measured in its own cells (catalytic_cell_base vs
_innate, 1000 fights/enc, seed 42): flat everywhere within noise
(tank_boss 79.0% vs 77.4%, others <=0.5pt)** -- a consistency upgrade,
not a power upgrade, exactly the safe disposition the ruling wanted.
C# side: codegen `innate: true` delta -> `AddKeyword(CardKeyword.Innate)`
in OnUpgrade (keywords are instance-owned LocalKeywords; Innate is the
base game's own keyword, driving opening-hand placement and card text).
hot_hands adopting the same disposition stays QUEUED for the user.

## Full-suite discipline + R25 errata + R38 -- the gate catches its first bug (2026-07-20 night)

**The finding (user-diagnosed):** "188 tier0 tests green" was a true
statement about a SUBSET. The full repo suite was 236 tests with one
failure: tier05/tests/test_m7.py::test_unappliable_upgrades_never_chosen_
at_rest hard-coded catalytic_conversion as forever-unappliable; R37 made
that upgrade real, tier0 legitimately smiths it at campfires, the stale
assertion tripped. Stale test, not a broken feature -- the deployed build
and the R36 window result stand. The narrowed test command was most
likely a compaction artifact (session compacted mid-sprint).

**Fixes (all landed this batch):**
- **Structural test fix:** the tier05 test now DERIVES the unappliable
  set from the upgrade engine (tier0.content.upgrades.UNAPPLIABLE --
  currently durin_witchs_flame + nicole_celestial_gift, the two
  constants-encoded companion deltas) instead of hard-coding names, and
  sweeps all four rest plans. The next disposition ruling cannot strand
  it. An empty UNAPPLIABLE fails loudly (retire by ruling, not by skip).
- **Process fix:** validate.ps1 gains S7 -- the FULL repo suite
  (pytest at repo root, 1000-fight band locks included) runs before any
  deploy. Green claims name their scope. Memory files updated so the
  narrowed-command compaction artifact does not recur.

**R25 errata batch RELEASED** (sequencing satisfied: R36 window ran,
bands held, user read the result and gave the word): cant_catch_me
block 4 -> 2 (kills the strict domination over warm_glow; lint KNOWN
entry retired, the lint now guards the fix) and dodge_roll block 8 -> 6
(resolves the dodge_roll/hide_and_seek PENDING_RULING domination -- 6 < 7;
entry retired likewise). Upgrades ride unchanged (+2 -> 2->4, +3 -> 6->9).
**Post-errata window (1000 fights, seed 42): all ratified bands hold;
median identity passes. spark_weighted vs tank_boss 56.8% -> 48.5%** --
the CCM nerf is real spark-boss power, band floor 45% now 3.5pt away.
Flagged for the user's eyes; no ruling required while bands hold.
C# side: CantCatchMe regenerated (BlockVar 2). dodge_roll stays
codegen-blocked on exhaust_from; its errata is sheet/tier0-side.

**R38 (user-ratified 2026-07-20 chat, "hot hands as suggested with
innate"):** hot_hands+ adopts the R37 disposition -- upgrade delta is now
`{innate: true}`; the old `{remove: self_damage}` delta is DEAD (it was
codegen-inexpressible, leaving hot_hands the sole no-upgrade-path card;
self-damage now stays on the upgrade as the card's cost). **Measured in
its own cells first (hot_hands_cell_base vs _innate, spark pilot, 1000
fights/enc, seed 42): tank_boss 45.9% -> 49.5% (+3.6pt, ~1.6 SE of the
paired diff), gauntlet +1.6pt, all other encounters <=0.2pt** -- a
modest real consistency gain vs bosses, unlike catalytic's pure noise;
cells only, never the identity median. C# HotHands.cs regenerated with
OnUpgrade AddKeyword(Innate); the codegen no_upgrade_path manifest list
is now EMPTY -- every generated card has an upgrade path.

**Verification:** full suite 236 passed (82s) -- the scope IS the repo;
domination lint CLEAN (both retired entries guard their fixes); parity
lint OK (8 cards); Release build 0 warnings. NOT deployed: the user is
mid-playtest and the game is running (never kill the game); the dll
rides the next deploy window.

## Art vibe-check addendum -- renames, dedupe law, replace list (2026-07-20 night)

User-ratified chat addendum (contact-sheet review, user's eyes on sources).
Rides alongside the standing GO; nothing here blocks bomb ops -> codegen
widening -> companions.

**Display renames (ids STABLE -- future greps must try BOTH names):**
- elemental_ecstasy -> "Sweet Dreams" (the sleeping Birthday-2025 art: the
  nap IS the aura refresh, the draws are the dreams). Hand-written
  ElementalEcstasy.cs title updated.
- clockwork_toy -> "Imaginary Friend" (the chosen item's own name; block 5
  + Burst = a friend who shields and encourages). Generated; regen picked
  up the sheet name. skill_tag stays. The elemental_ecstasy crop question
  is DEAD -- the rename makes the uncropped art correct.
Id-renames were considered and rejected on record: class/manifest/upgrade/
DECISIONS churn for zero player-visible gain.

**Dedupe law codified in art_lint:** L1 (which already implemented the
rule) gains the ruling's vocabulary in its docstring -- effective pick =
auto or shortlist rank 1 unless red-pen resolves otherwise; register-
crossing reuse legal by construction (worked example: Klee Wish =
big_badda_boom card + selection splash); dead shortlist ranks blessed
(Imaginary Friend Dodoco on duck_and_cover r3). NEW: PENDING_RED_PEN
allowlist (the domination lint's KNOWN pattern) -- known collisions print
as notes until resolved, then the entry is DELETED so the lint guards the
resolution.

**Replace list executed, with two premise corrections (PARKED, not
resolved -- both in PENDING_RED_PEN for the red-pen session):**
- spark_knight_style <- Klee Character Card (regular/golden = Style/True
  pairing); Glimmering Firework RETIRED. BUT the ruling's "only a model
  source" premise was wrong: Klee Character Card is kaboom's auto pick.
  Kaboom re-picks or spark_knight_style re-hunts -- user's call.
- catalytic_conversion <- Dodoco's Marvelous Magic (promoted from its
  power icon, which keeps it); Jumbo statue now EXCLUSIVELY the Burst
  badge. BUT Marvelous Magic is ALSO spark_collection's effective r1, and
  spark_collection's r2 (Dodoco's Duet) is vermillion_pact's passed pick.
- bright_idea: REHUNT ruled (r1 generic cheer, r2 reads as crying/panic).
  Hunt term on file: a realization gesture (exclamation, lightbulb,
  raised finger) across emoji/sticker sets. Demoted both candidates to
  ranks 2/3 -- the dead r1 placeholder was tripping L1 (it is
  eager_to_help's pick) and L3 (icon register on a card slot); the card
  ships portrait-less by design until the hunt lands.
- dahlia_*: RESOLVED immediately -- the ruled hunt (Equipment Card first)
  already ran during the taste pass (none exists, recorded in plan.tsv),
  so r1 Character Card is accepted per the ruling's fallback.
- Passed as-is: crackle r1, playtime_forever, true_spark_knight,
  vermillion_pact, the icon queue.

Verification: art_lint OK (2 allowlisted notes), parity lint OK, full
suite 236 passed, Release build clean. Regen delta: ClockworkToy.cs title
only.

## Playtest findings: Snap spark-spend bug (FIXED) + Beetle Swarm design question (QUEUED) (2026-07-20 night)

**Finding: Snap eats the bank it just filled (FIXED, C# divergence).**
Reported: play a 1-cost spark-granting card at 2 Sparks -> energy paid,
3rd Spark granted, then ALL 3 Sparks consumed, no free attack. Root
cause: SparkPower made the spend DECISION in AfterCardPlayed, reading the
POST-RESOLUTION bank -- Snap's own rider pushed 2 -> 3, and the handler
then saw "attack at threshold, printed cost != 0" and consumed. The sim's
play_card evaluates `sparks >= threshold` BEFORE effects resolve (the
spend belongs to spark-freed plays only). Fix: decision snapshotted in
BeforeCardPlayed (IsFirstInSeries = once per play, the burst-grant idiom;
threshold snapshotted with it), consume still executes in AfterCardPlayed
-- mutating the bank pre-payment could un-zero the cost mid-play, and
that ordering has no decompile evidence. Recorded caveat: the sim spends
pre-resolution, so a card that READS the bank mid-play (formula cards,
none shipped) would see sim-vs-C# skew -- revisit with evidence when
formula codegen lands.

**Finding: Kaboom Beetle Swarm's first hit pops the mines (QUEUED for
ruling -- working as simulated, NOT fixed).** Reported: subsequent hits
never get the +3 vs-bombed bonus. Verified against tier0: bonus_vs_bombed
is read per hit at damage time, and hit 1's HP damage detonates that
enemy's bombs early -- [8, 5, 5] vs a single bombed enemy in BOTH
engines (new pinning test test_beetle_swarm_bonus_reads_live_bomb_state_
per_hit). The C# is a faithful mirror, so per house law this is a DESIGN
question, not a bug: options at ruling time include (a) accept -- "the
swarm sets off the mines" is coherent demolition flavor and the detonation
damage usually exceeds the forgone +6, (b) snapshot bombed-state at cast
(the Sizzle idiom), (c) bonus keys off "detonated this play". Sheet
unchanged until ruled.

## Bomb-manipulation ops -- standing plan item 4 lands (2026-07-20 night)

Five cards unblock: quick_fuse (detonate chosen enemy), remote_detonator
(detonate ALL +2, upgradeable), chain_fuse (modify placed-this-turn +3 then
place -- effect order preserved, so its own bomb is NOT buffed, sim-exact),
careful_arrangement (move ALL bombs to chosen enemy +2 each),
chained_reactions (detonate ALL, then per detonation 50% -> fresh 5-dmg
bomb on a random enemy; upgrade replaces chance at 75%). Pool 49 -> 54.

**BombPower surface grown (all tier0-mirrored):** _damages becomes
List<BombCharge>(Damage, RoundPlaced) -- the stamp mirrors Bomb.turn_placed
for modify's placed_this_turn scope (today every live bomb is this-round by
construction, the stamp keeps semantics exact if that ever changes);
private Detonate gains a bonus param (dealt = damage + bonus +
bomb_damage_up, pre-amplification, tier0 detonate_bombs) and returns the
count; public DetonateOn/DetonateAll (count feeds Chained Reactions -- the
sim diffs a counter, here the return IS the count); ModifyAll (pure
mutation, synchronous); MoveAllTo (charges travel with stamps, +bonus,
source powers removed; PowerCmd.Apply with the moved count keeps Amount =
bomb count in sync).

**Codegen widened:** 4 new ops with field whitelists (UNPARSEABLE
discipline), chance-needs-preceding-detonate + single-detonate +
single-bonus-effect guards; deltas `bonus` (DynamicVar "Bonus") and
`chance` (REPLACEMENT per tier0 upgrades.py -- rendered as percent,
codegen computes the delta in points from the sheet base: 50 -> 75 emits
UpgradeValueBy(25m)); enemy-targeted detonate/move set the card's
TargetType. Rng: roll and pick both ride Rng.CombatTargets
(NextFloat/NextItem, decompile-verified).

**quick_fuse ships with NO upgrade path** (delta `add: {draw 1}` is
structural -- codegen cannot add a whole effect+sentence on upgrade; the
same honesty that flagged hot_hands). It re-opens the manifest
no_upgrade_path list that R38 had emptied; hand-finish or re-rule numeric.

Art: chain_fuse / careful_arrangement / chained_reactions have NO plan.tsv
rows -- portrait-less (null-safe) with hunt notes queued for the art pass.

Verification: full suite 237 passed (repo scope; includes the new Beetle
Swarm pinning test), parity lint OK, art lint OK, Release build clean.
NOT deployed (game still running).

## Codegen widening sprint -- 21 cards unblock in five batches (2026-07-21)

Five commits (364acf0, bc02b76, 90c9b58, bc8995f, 7480847), pool 54 -> 71.
Every non-companion sheet card now generates; the blocked list is down to
friendly_visit (cost_mod companion_cards) and the three companion-op
rares, all of which land with the companions phase.

**Weak/Vulnerable (3 cards: spooked, trip_wire, surprise_visit).** The
CORE's own WeakPower/VulnerablePower, decompile-verified == tier0 law
(x0.75 dealt / x1.5 taken, Counter stacks, enemy-side turn-end tick).
APPLY_POWERS grows an ENEMY_APPLY_POWERS split with chosen-target and
all-enemies emission; a debuff-only card (Surprise Visit) gets its
TargetType from the apply.

**Parity bug found and fixed while wiring it: Unpowered mirror hits
skipped the sim's damage modifiers.** tier0 deal_damage_to_enemy runs
EVERY hit -- bombs and the Burst volley included -- through
strength/weak (pre-amp) and vulnerable (post-amp) with ONE final
truncation. The C# Unpowered idiom opts out of the native powers'
IsPoweredAttack gate, so Explosive Frags' Vulnerable amplified follow-up
detonations in the sim but not in the game -- live since the R23 power
pass, observable via explosive_frags or the battery encounter's
weak-on-player. New SimDamagePipeline (DealerMods/TargetMods, constants
mirroring WEAK_DEALT_MULT/VULNERABLE_TAKEN_MULT, NOT the native
DynamicVars -- Paper Krane/Phrog hooks are relics the sim doesn't have)
applied at both call sites; values stay decimal until the single (int).

**Conditionals (6 cards).** Four predicates with verified reads:
this_cost_zero = EnergyCost.GetResolved() == 0 (cost with all modifiers,
so a spark-freed attack reads 0 = sim current_card_cost); has_spark;
reaction_triggered_by_this = diff of the new
ReactionEffects.TotalResolved (monotonic, incremented in the single
funnel for every named reaction, dealer or not); killed_target =
card-start enemy snapshot .Any(IsDead). Snapshots are captured at the
TOP of OnPlay -- the sim resets its per-card counters at resolve_card
start, not at the conditional's site. repeat_this is honored by a repeat
tail exactly like sim resolve_card (re-resolve minus the repeat
machinery); REPEAT_SAFE_OPS keeps the replayed block free of local
redeclarations. Upgrade grammar: conditional_bonus (ExtraDamage var),
draw-both-branches (Cards + DrawElse), and condition: unconditional --
play-time (IsUpgraded || pred) plus a text swap via
{IfUpgraded:show:upgraded|normal}, the runtime form BaseLib SimpleLoc's
MakeUpgradeSwap generates (pipes inside either arm are a loud stop).

**X cost (controlled_demolition; R34).** HasEnergyCostX => true +
ResolveEnergyXValue() (CapturedXValue through Hook.ModifyXValue -- the
game-canonical read, so Chemical-X-style relics compose). X / X_plus_N
amount grammar; times: "X" gates the whole attack on x > 0 (range(0) =
no hits). bombs delta rides a Bombs var ("X+{Bombs:diff()}").
SparkPower.AppliesTo already carried the R34 exemption (!CostsX).

**Formulas (gleeful_barrage, grand_finale).** 2_plus_sparks reads the
NEW SparkPower.SparksAsResolved -- the bank minus the pending spend.
This is the Snap-fix caveat landing on schedule: the sim spends the
charge BEFORE effects resolve, our consume executes in AfterCardPlayed,
so mid-play readers must subtract the pending spend or a spark-freed
Gleeful Barrage counts sparks the sim already spent. has_spark
predicates switched to the same accessor (one truth).
N_per_detonation_this_combat reads BombPower.DetonationsThisCombat --
keyed to the combat-state instance so a fresh combat starts at zero with
no reset hook; incremented per bomb inside Detonate before the damage
lands (sim order); combat-state snapshot taken before PowerCmd.Remove.

**Small ops.** energy -> PlayerCmd.GainEnergy. scry_discard -> top-N
peek (index 0 IS the top; Take(n) = draw_pile[:n]) + FromSimpleGrid
player choice -- the sim's _worst_card is the pilot's stand-in for
player choice (R36 Crackle precedent); the unpicked card stays on top.
add_card both forms: id -> hand-written token class (NEW Confiscated:
Status, cost 1, does nothing, never pooled, outside the parity lint's
sheet charter) and pool -> resolved from the SHEET at generation time
(archetype/rarity live only there), every member verified generated,
picks WITH replacement (tier0 rng.choice per pick), cost_override ->
SetThisCombat (the token keeps it all combat), AddGeneratedCardToCombat's
full-hand redirect-to-discard = the sim's _add_token rule. exhaust_from
status -> RANDOM Status from hand (sim rolls rng, no choice UI).
remove: exhaust delta -> RemoveKeyword(CardKeyword.Exhaust), the base
game's own idiom (sugar_rush).

Verification: every batch closed with the FULL repo suite green (237),
gen --check clean, handwritten-parity OK, Release build clean. NOT
deployed; the last deploy predates this sprint, so the running game has
none of it.

## Companions land -- reaction table completes, 17 cards + the 4th slot + companion ops (2026-07-21)

Four commits (f032cf1, 22b6d86, e307ad2, db06d8c). THE SHEET IS
COMPLETE: every Klee card and every Mondstadt companion is expressed;
the manifest's blocked list is exactly the 8 deliberately hand-written
cards.

**Reaction table completes.** Overload / ElectroCharged / Swirl /
Crystallize were loud stubs because no electro/hydro/cryo/anemo applier
existed C#-side; the roster makes all four reachable, so they became
real: Overload = OVERLOAD_SPLASH Unblockable|Unpowered to all living
enemies dealer-less (sim _splash: raw hp-=; no detonation, no attack
hooks); ElectroCharged = the core's own PoisonPower (the sim's dot IS
poison: owner-turn-start tick of Amount then decrement -- exact match);
Swirl = consumed aura onto EVERY living enemy, target included,
overwrite-or-refresh at full duration; Crystallize = CRYSTALLIZE_BLOCK
to the dealer (Afterimage GainBlock idiom), loud no-op if dealer-less.
RECORDED CAVEAT: overload splash can kill, and the C# killed_target
snapshot counts that death while the sim's kills_this_card (fed only by
deal_damage_to_enemy) does not -- a micro-edge on sparkly_explosion
that only a ruling could align; surfaced, not hidden.

**ElementalHit** is the new single pipeline for every non-attack
element-tagged hit (Deal) and the damage-less ops (ApplyOnly =
resolve_hit at 0 damage). BombPower.Detonate and the Burst volley
refactored onto it; Oz and Witch's Flame ride it too -- one path, no
drift.

**Companion powers** (CompanionPowers.cs), each mirroring its tier0
trigger: OzSummon (end-turn 3-dmg Electro hit, tick after -- sim
order), WitchsFlame (permanent, +Amount% amp additive with Vermillion
Pact inside AmplifierMultiplier, end-turn 4-dmg Pyro hit), SolarIsotoma
(BeforeDamageReceived: powered-attack hits vs aura'd enemies grant 3
Block BEFORE the hit consumes the aura -- the sim's check-then-hit
order), CelestialGift (+2 per attack hit + 4 Block at turn start),
AttackUpThisTurn (removed at player turn end), NextAttackUp (consumed
after the next attack card's series -- the repeat tail is the same
CardPlay, so a repeated Boom Goes the Dynamite keeps the bonus for both
resolutions, exactly the sim's per-resolve pop).

**Companion cards** generate from the sheet with ICompanionCard
(Star/CompanionElement/PersonalPool) + MaxUpgradeLevel 0 (never scale);
cadence exemption honored -- IElementalCard only where the sheet says
applies_element, with the companion's own element. New ops apply_aura /
swirl (swirl IS trigger-anemo) / buff_next_attack. Companions are NOT
in KleeCardPool: the reward slot is their only door (tier05
character_pool excludes them).

**The 4th reward slot** (CompanionSlot.Roll, hosted on
PoundingSurprise.TryModifyRewards -- the starter relic is the one model
guaranteed present all run; relics are the hook's intended listeners
per the AbstractModel doc). tier05 roll_rewards mirrored exactly:
RARITY_ODDS walk, 5-stars ARE the rare tier, empty-tier fall-through,
uniform in-tier pick (nation weighting reduces to uniform
single-nation, deliberately unmirrored until a second nation),
personal-pool gating, the player's Rewards rng stream, native
SpecialCardReward (take-or-skip; fresh RunState.CreateCard instance).
Pity/choose-3 OUT (measured null, ruled); Featured Banner skipped
(no-op at roster size, ruled).

**Companion-op cards**: CompanionCostThisTurnPower (cost hook, removed
next turn start), ReplayNextCompanionPower (ModifyCardPlayCount; the
game's replay series is the sim's replay loop), CompanionPlays ledger
(combat-keyed unique first-play order, recorded in
KleeElementalHooks.BeforeCardPlayed). borrowed_brilliance's
copy_cost_override = play-time IsUpgraded read + IfUpgraded text swap;
`temp: true` accepted and IGNORED because tier0 ignores it (sim is
LAW). study_buddy ships upgrade-less (add-a-draw is structural).

RECORDED CAVEATS: DetonationsThisCombat and CompanionPlays are keyed to
the combat-state instance -- a mid-combat reload restarts the combat
and the counters with it (correct if the game restarts combats on
load, which is the observed model). ART: all 26 new cards
(weak/vuln 3, conditionals 6, X 1, formulas 2, small-ops 5, companions
17 minus overlap, companion-ops 4, Confiscated) have no plan.tsv rows
-- portraitless until the art pass; hunt terms are art-pass work.

Verification: full suite 237 green at every commit, gen --check clean,
handwritten-parity OK, Release build clean. NOT deployed.

## Playtest 1 crash triage -- pool membership is not optional (2026-07-21)

First real playtest of the companion build produced two reports: the
companion offer "did nothing when clicked", and the run softlocked when
a card was drawn. Both are ONE root cause, and the game told us exactly
what it was in godot.log:

    System.InvalidOperationException: You monster!
      at CardModel.NeverEverCallThisOutsideOfTests_ClearOwner()
      at MockCardModel.MockCanonical()
      at MockCardPool.GenerateAllCards()
      at CardPoolModel.get_AllCards()  ->  CardModel.get_Pool()
      at NCard.Reload -> NCard.Create

**Mechanism.** `CardModel.Pool` walks `ModelDb.AllCardPools` for a pool
whose `AllCardIds` contains the card. When nothing matches it probes
`MockCardPool` as a last resort -- and MockCardPool's generator calls a
test-only method that throws in a shipped build. So a card in NO pool
throws. `Pool` is read by `NCard.Reload` (frame + energy visuals), i.e.
on every card NODE creation -- which is why this did not fail on PLAY,
it failed on DRAW and on PREVIEW, taking down whichever task owned the
node. `SpecialCardReward.OnSelect` threw during its take animation
AFTER the card was already added (hence "nothing happened" -- the card
was in fact in the deck), and `CombatManager.SetupPlayerTurn`'s draw
threw and left the turn half-built: the softlock.

**Who was affected.** Everything we deliberately kept out of
KleeCardPool: the 16 companions (the reward slot is their only door),
Confiscated (created at play time), and -- found by the new lint on its
first run, never yet reported by a player -- SparksNSplash, the kit
Burst card, which would have crashed the moment the meter first filled.
"Not rollable" was the right design call; "in no pool at all" was never
a legitimate way to express it.

**Fix.** KleeExtraCardPool: a second pool holding exactly the
never-rollable cards, mirroring KleeCardPool's visuals. Klee.CardPool
still returns KleeCardPool, and reward/transform generation draws from
the CHARACTER's pool, so nothing here became rollable. Membership
tracks CompanionRoster.All wholesale, so a new companion cannot be
added to the roster and forgotten. tools/lint_pool_membership.py fails
the deploy (validate S6b) if any CustomCardModel class escapes both
pools.

**Second finding, same playtest: the slot was the wrong SHAPE.** The
companion arrived as its own reward row, so the player took a card AND
a companion. tier05 roll_rewards returns ONE offers list --
REWARD_CARD_OFFERS cards with the companion appended -- and the policy
picks one from it. SpecialCardReward could not express that. Moved to
`TryModifyCardRewardOptions` (fired from CardFactory.CreateForReward
after the cards roll, gated Source == Encounter), which appends to the
card reward's own option list: the companion is now a genuine 4th
choice competing with the three cards, which is the law. The offer is
instantiated exactly as the native path instantiates its own three
(RunState.CreateCard) and takes no upgrade roll, matching
MaxUpgradeLevel 0.

LESSON: the deploy gate had five static rules and a full test suite,
and none of them could see a runtime-only invariant of the host engine.
Every host invariant we learn the hard way should leave a lint behind;
this one did, and it caught a third victim immediately.

Verification: full suite 237 green, gen --check clean,
handwritten-parity OK, pool-membership OK (93 classes), Release build
clean, DEPLOYED 2026-07-21 (game closed, user go-ahead).

## Bug-hunt parity fixes -- three phase errors and a lying card (2026-07-21)

An adversarial bug hunt (9 finders, each finding put to a 3-lens
refutation panel) returned 14 survivors. These are the ones that needed
no ruling. Its sharpest structural observation: three separate defects
all reduce to the same mistake -- a sim PRE-step implemented in a POST
hook, or the reverse -- and no pass has ever systematically mapped each
sim pipeline step to its C# hook. That sweep is owed.

**Superconduct did not amplify its own triggering hit -- on the card
path only.** tier0 applies the Vulnerable inside resolve_hit (_react)
and only then runs modify_damage_taken, so the triggering hit is itself
x1.5. C# applied VulnerablePower in AfterDamageReceived, after the
number was final: 10 where the sim dealt 15. The tell was
self-inconsistency -- ElementalHit resolves the reaction BEFORE its
TargetMods, so the same reaction off a bomb correctly dealt 15. One
reaction, two payouts. AuraPower.ModifyDamageMultiplicative now carries
the triggering hit's share in the same multiplicative phase the sim
uses, guarded on the target not already being Vulnerable (the sim's
modify_damage_taken is a flat x1.5 on any nonzero stack, never per
stack, so double-counting would be the easy wrong fix).

**Shatter rode ModifyDamageAdditive**, whose own doc claimed the
additive phase kept it from scaling with Vulnerable. Exactly inverted:
the pipeline is (base + additive) * vuln * amp, so Vulnerable scaled it
AND enemy Block absorbed it. tier0 deals it as raw `enemy.hp -=` after
the main hit's block subtraction, commented "Direct HP, like splash".
Frozen + Vulnerable 2 on a 10-damage attack: sim 21, game 24; into 12
Block: sim 6 through, game 4. Now dealt from AfterDamageReceived with
the Overload-splash idiom (Unblockable | Unpowered, no dealer), with the
sim's `enemy.alive` and `source == "attack"` gates mirrored.

**Auras ticked before start-of-turn detonation; the sim ticks after.**
The tick sat in AfterSideTurnEnd(Enemy) -- immediately BEFORE
BombPower.BeforeSideTurnStart(Player) -- so an aura on its last turn
expired before the detonation could react with it. A Hydro aura plus a
bomb lost its Vaporize entirely, and the detonation then left a fresh
Pyro aura the sim never creates. Moved to AfterSideTurnStart(Player):
CombatManager awaits Hook.BeforeSideTurnStart to completion, then
AfterSideTurnStart, both before energy reset and the draw -- separate
broadcasts, so this needs no ordering assumption between two
enemy-owned powers.

**NextAttackUpPower survived a replay series.** tier0 resolve_card POPS
next_attack_up (its siblings celestial_gift/attack_up_this_turn
deliberately use .get(), which is what makes the pop load-bearing), and
the replay loop issues N separate resolve_card calls. Passion Overload
-> Study Buddy -> Kaeya dealt 18 where the sim deals 14. Removal moved
from IsLastInSeries to IsFirstInSeries. The repeat tail is deliberately
unaffected and must be: repeat_this re-runs _resolve_effects INSIDE one
resolve_card, after current_attack_bonus is snapshotted, so the tail
keeps the bonus. A series is the replay loop; the tail is a for-loop.

**Crackle+ lied about its own Sparks.** `sparks` is a CAP
(`gain = min(fx["sparks"], discarded)`), but the template printed it as
a per-card RATE. At 1/1 the two coincide, so only the upgrade lied:
"discard 2: gain 2 Sparks per card discarded" reads as 4 and grants 2 --
the difference between crossing the 3-Spark free-attack threshold and
not. The rate is now printed as the constant 1 it is, and the cap only
when it can actually bind.

**R24 manifest hole closed.** The companion emission loop never called
upgrade_plan, so no_upgrade_path covered zero companions -- and the
safety net that exists to surface "the sim can upgrade this and the mod
cannot" was blind to 14 real cases. All 16 companions now carry a
reason. QUEUED FOR USER RULING: the companion sheet header says
companions never scale (hence MaxUpgradeLevel 0) while
klee-upgrades.yaml ships deltas the sim honors and tier05 smiths at rest
sites. Two ratified documents disagree; every companion-deck power curve
tier05 has produced is unreachable in game until one of them yields.

## Pool fix, attempt 2 -- the first one could never have worked (2026-07-21)

Same playtest, one deploy later. The "You monster!" crash was unchanged:
1137 occurrences in the log, cards rendering with the engine's own
"If you can read this, there is a bug." placeholder (NCard.Reload throws
at the Pool read BEFORE it populates the description label, so the
scene's default text survives), mangled reward layout, empty deck
screen, softlock on draw.

KleeExtraCardPool was never visible. ModelDb.AllCardPools is
`AllCharacters.Select(c => c.CardPool)` concatenated with a HARDCODED
array of 7 shared pools. There is no registration hook. A mod pool that
is not some character's CardPool cannot participate in the very lookup
it was created to satisfy -- so the fix was inert from the moment it was
written, and the lint shipped alongside it went green the whole time.

The correct split is the engine's own: AllCards means "belongs to this
pool" and backs CardModel.Pool; GetUnlockedCards means "may be
generated" and is the SOLE path into both reward rolls
(CardCreationOptions.GetPossibleCards) and transforms (CardFactory).
So the off-pool cards now live in KleeCardPool.GenerateAllCards, and
KleeCardPool overrides FilterThroughEpochs to strip them from
GetUnlockedCards. Pool resolves; no generator can reach them; the design
constraint (companions arrive only via the companion slot) is unchanged.

LESSON, sharper than the first one: the lint checked source membership
and reported OK while the bug was live in front of the player. A static
lint can confirm a card is listed somewhere; it cannot confirm the
engine can see the thing it is listed in. Recorded in the lint's own
docstring so the next person does not read a green line as proof.

## Two rulings executed: companions scale, Fontaine joins the slot (2026-07-21)

USER RULING 1: "the cards should be upgrade-able as per the sheet."
USER RULING 2: "it's fine for Fontaine companions to show up as long as the
50% nationality weighting is respected... it's probably best to have some
non-Mondstadt cards in the pool to make sure Klee doesn't inadvertently
overperform with a 100% Mondstadt roster."

**Companions scale.** MaxUpgradeLevel 0 is gone; companions emit real
upgrade paths from the merged upgrade index. The contradiction is
resolved in the upgrade sheets' favour, so the mod now reproduces the
power curve tier05 has been measuring at rest sites. The remaining
no-upgrade companions are exactly the sim's own UNAPPLIABLE set --
durin_witchs_flame and nicole_celestial_gift, both constants-encoded --
which is the cross-check that the two sides now agree.

New delta grammar: `duration` (Oz, Solar Isotoma) and `buff` (both
Bennetts, Chevreuse) join POWER_UPGRADE_KEYS, and the keys bind to the
first TOP-LEVEL apply_power OR buff_next_attack, mirroring the sim's
`next(fx for fx in top if fx["op"] in (...))`. That precedence is
load-bearing: Chevreuse's base buff scales while her conditional rider
stays at its printed value, exactly as her sheet comment specifies.

**The upgrade index is now merged**, klee-upgrades.yaml + furina-
upgrades.yaml, the same two sheets in the same order as
tier0/content/upgrades.py, duplicate ids a hard error on both sides.
Without this the Fontaine companions would have generated
unupgradeable while the sim smithed them -- the divergence we had just
finished closing, one sheet over.

**Fontaine in the slot.** COMPANION_SHEETS maps each companion sheet to
its home nation (tier0's loader derives the same thing from the
filename) and the roster is 16 + 12 = 28. Guest Star cards are skipped:
they are Furina personal-pool cameos her own generators create
mid-combat, tier05 filters them out of companion_pool, and nothing in
the Klee mod can create one.

**Nation weighting went live**, CompanionSlot.NationWeightedChoice, a
port of tier05 _nation_weighted_choice: SAME_NATION_REWARD_SHARE (0.5)
split evenly across home-nation cards, the remaining half spread across
all cards by NATION_WEIGHTS (1.0 each today). It had always been a
no-op -- with one nation it reduces exactly to a uniform pick -- so this
is the first build where it bites. The no-home-nation fallback is
mirrored too, because a Fontaine-only rare tier actually reaches it.

**Three DSL asks wired** -- the sheet flagged them and the user asked
the right question ("the only issue would be if there are any ops needed
by the Fontaine cards that aren't actually wired yet, meaning we've
shipped something broken"). All three were live in tier0 already:
  - `reaction_triggered_this_turn`: ReactionEffects keeps the per-turn
    window as a snapshot of the existing monotonic counter, opened at
    AfterSideTurnEnd(Enemy) -- one broadcast EARLIER than the
    start-of-turn detonation, so detonation reactions count toward the
    new turn as they do in the sim -- and at BeforeCombatStart, because
    turn 1 has no preceding enemy turn and the counter crosses combats.
  - `block_next_turn`: the game ALREADY SHIPS BlockNextTurnPower, and
    the decompile is an exact tier0 match (grants Amount from
    AfterBlockCleared -- right after the turn's block reset, where the
    sim grants it -- then removes itself, which is the sim's `pop`). A
    mod power was written and then deleted in favour of it, same house
    rule as WeakPower / VulnerablePower / PoisonPower.
  - `shatter_bonus`: ShatterBonusPower, read by FrozenPower inside the
    Shatter it had just been taught to deal as raw unblockable damage.

Nothing shipped broken: a blocked companion is a SystemExit in the
generator, not a manifest entry, so the three unwired ops could never
have reached a build.

CAUGHT IN REVIEW OF OWN OUTPUT: Chevreuse first generated "If an
Elemental Reaction triggered this turn: ." -- BRANCH_OPS gained
buff_next_attack while _branch_text did not, and the empty clause
rendered silently. _branch_text's fallthrough is now a SystemExit
naming the op, so the two tables cannot drift apart again.

ART: 12 Fontaine companions ship portraitless (43 cards now awaiting
the art pass: 21 Klee, 9 Mondstadt companions, 12 Fontaine, Confiscated).

Verification: full suite 237 green, gen --check clean,
handwritten-parity OK, pool-membership OK (105 classes), Release build
clean. NOT deployed -- the game was running.

## Corpse detonation -- OPEN parity question, awaiting playtest (2026-07-21)

STATUS: **OPEN. Do not baseline bomb numbers against it until settled.**
Recorded here deliberately UNRESOLVED rather than closed, because it
cannot be settled from the repo.

QUESTION: does a killing blow on a bombed enemy early-detonate that
enemy's bombs?

EVIDENCE FOR A DEFECT: BombPower.AfterDamageReceived lacks the
`target.IsDead` guard that both of its siblings carry. If the engine
broadcasts AfterDamageReceived on a creature the hit just killed, the
bombs resolve one turn early on the death turn.

EVIDENCE AGAINST: one refuter in the bug-hunt panel claimed the engine
suppresses AfterDamageReceived on a killed creature, which would make
the missing guard harmless. That claim is UNVERIFIED -- no decompile
site was produced for it, and the finding survived the panel on a
contested premise rather than a clean one.

STAKES (why this is worth a real answer despite low probability): the
sim detonates unconditionally. If the game suppresses on death and the
sim does not, then every sim bomb-damage measurement taken against a
KILLABLE enemy overcounts at the margin on the killing-blow turn. Low
probability, high blast radius -- it would touch bomb numbers broadly
rather than one card.

SETTLEMENT (user playtest, ~10 seconds): bombed enemy + Pounding
Surprise equipped, land the kill, watch for the Spark. The relic's
spark-on-detonation is the tell.
  - Spark appears  -> hook fires on death, sim and game agree, close it.
  - No Spark       -> real divergence, opens a sim-side correction.

NOT self-closed from the repo: this needs the eyes-on result.

## Furina character-select crash: preload paths and hook id collision (2026-07-23)

Windows playtest reached character select, then crashed in
`RunManager.GenerateMap`. The background preload had failed exactly four
Furina paths: combat visuals, character icon scene, energy counter scene, and
card trail. `CharacterModel.AssetPaths` derives those from `Id.Entry`; texture
overrides and `CreateCustomVisuals` do not alter the preload list. BaseLib
exposes a supported redirect for each one, but Furina had not overridden
`CustomVisualPath`, `CustomIconPath`, `CustomEnergyCounterPath`, or
`CustomTrailPath`.

Fix: both roster characters now close all four redirects explicitly. Combat
and icon scenes are character-owned PCK resources; the temporary energy
counter and trail borrow valid Ironclad scenes. Furina's remaining PCK scenes
also moved under `res://furina/`. Missing Furina art is copied from Klee at
PCK-build time, so temporary art can be shared without sharing the paths that
BaseLib registers for conversion.

The old PCK was itself a deployment hazard because it is gitignored and a pull
cannot refresh it. `build_pck.ps1` now writes a versioned resource/hash
contract beside the pack; deploy validation rejects an old, missing, or
mismatched contract. S6c checks every roster character's source overrides and
PCK declarations. Runtime self-check R9 evaluates both character asset sets
after the pack merges and reports every unresolved path.

The same log exposed an independent dead-mechanic bug:
`SubscribeForCombatStateHooks` is keyed by id, and both Klee and Furina
registered with `klee`. ModHelper rejected the second subscription, so
`FurinaResourceHooks` never ran. The roster now registers once with a combined
delegate; source tests and S6c enforce one call containing both listeners.

Finally, FrozenPower now supplies the title/description localization that R8
was correctly reporting. The previous four findings were the same two missing
keys observed once during each character sweep.

## Animation sprint 1 opens: scene binding architecture (2026-07-23)

Sprint doc: docs/animation-sprint-1-plan.md (Tracks A-E; A is a hard gate).

LICENSE NOTE (standing for the whole sprint): Downfall (github.com/lamali292/
Downfall) is reference-reading ONLY. Patterns, node inventories, and patch
shapes may be mirrored; scene files, art, and code are never copied verbatim
into our tree. The clone lives in a session scratchpad, not the repo.

Track A architecture finding — how a mod scene becomes the combat model.
Verified against decompiled game v0.107.1 (2026-07-21 decompile; game binary
unchanged since 07-18) and BaseLib.dll 2026-07-21 (re-decompiled this
session; CustomCharacterModel surface unchanged by the 07-21 update):

- `CharacterModel.VisualsPath` is private/non-virtual, but BaseLib patches it
  to return `CustomCharacterModel.CustomVisualPath`, and patches
  `CreateVisuals` to prefer `CreateCustomVisuals()` when non-null.
- BaseLib postfixes `PackedScene.Instantiate` and auto-converts any
  registered scene root via `NodeFactory<T>` (`RegisterSceneForConversion`,
  path-keyed — the campfire-softlock registry). `NCreatureVisualsFactory`
  declares the named-node inventory `%Visuals, %PhobiaModeVisuals, Bounds,
  %CenterPos, IntentPos, %OrbPos, %TalkPos` and GENERATES missing Bounds/
  CenterPos/IntentPos with defaults (Bounds 240x280 at (-120,-280)).
- Therefore a combat scene needs NO script attached. Downfall attaches C#
  scripts to scene roots (`[GlobalClass]` + Godot.NET.Sdk source generators
  give their assembly ScriptPath mapping); our KleeCode builds with plain
  Microsoft.NET.Sdk and our pck pipeline is deliberately script-less
  (build_pck.ps1 standing note). We get the same behavior from the outside:
  script-less `klee/model/combat.tscn` converted by BaseLib's factory, plus
  a Harmony postfix pair on `NCreature.SetAnimationTrigger` /
  `NCreature.StartDeathAnim` (Downfall's own patch shape) that routes
  triggers into an `%AnimationTree` inside the scene when one exists.
  `SetAnimationTrigger` is `_spineAnimator?.SetTrigger(...)` — a no-op
  without spine — so the postfix is purely additive and inert for every
  creature whose visuals carry no AnimationTree.
- `GenerateAnimator` stays un-overridden: NCreature only builds the base
  CreatureAnimator when `Visuals.HasSpineAnimation`, and we ship no spine.

New conventions this sprint:
- `klee-mod/pck-src/` — git-tracked text scene sources copied verbatim into
  the pck work dir by build_pck.ps1. Scenes too large for heredocs
  (AnimationPlayer tracks) live here; the historical heredoc scenes stay in
  the script until they next need editing.
- build id: build_pck.ps1 stamps `klee/build_id.tres` (resource_name =
  timestamp + git short sha) into every pack; boot telemetry logs it, so a
  stale pck is visible in godot.log instead of silently showing old art.
- Boot telemetry (permanent, house pattern): one line per convention scene —
  path, found/missing, root node type from SceneState (no instantiation, so
  logging cannot trigger conversion side effects).
