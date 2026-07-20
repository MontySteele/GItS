using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Factories;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Modding;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Characters;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves.Managers;
using MegaCrit.Sts2.Core.Unlocks;

namespace KleeMod;

/// <summary>
/// Mod entry point. The game looks for a class carrying [ModInitializer] and
/// invokes the named method during ModManager initialization.
/// </summary>
[ModInitializer(nameof(Initialize))]
public static class KleeMod
{
    public const string ModId = "klee";

    public static void Initialize()
    {
        Log.Info($"[{ModId}] Initializing Klee (C1 boots)...");

        try
        {
            var harmony = new Harmony(ModId);
            harmony.PatchAll(typeof(KleeMod).Assembly);
        }
        catch (Exception e)
        {
            Log.Error($"[{ModId}] Harmony patching failed: {e}");
        }

        Log.Info($"[{ModId}] Klee registered.");
    }

    /// <summary>English strings for the character and the four starter stubs.</summary>
    internal static void InjectLocStrings()
    {
        try
        {
            // Keys are ModelId.Entry, which is UPPER_SNAKE_CASE derived from the
            // class name (DuckAndCover -> DUCK_AND_COVER), NOT lowercase.
            // CardModel.Description reads "cards" -> "<ENTRY>.description".
            LocManager.Instance.GetTable("cards").MergeWith(new Dictionary<string, string>
            {
                // Two separate syntaxes are in play here, and both bit us:
                //
                // 1. Values are SmartFormat templates over DynamicVarSet, whose
                //    keys are "Damage" / "Block" (see BlockVar.defaultName).
                //    SmartFormat uses SINGLE braces - "{{Damage}}" is not a
                //    placeholder and is emitted literally.
                //
                // 2. Square brackets are BBCode, NOT keyword markup. The game
                //    wraps descriptions in [center]...[/center], so a stray
                //    "[Block]" parses as an unclosed tag and throws
                //    "Found end tag center, expected Block". Keyword tooltips
                //    are declared per-mod via a card_keywords.json (the Downfall
                //    pattern, see docs/card_keywords.json); we ship none yet, so
                //    C1 uses plain text and keywords land with the C2 text pass.
                // ONLY plain CardModel stubs belong here. Cards that derive from
                // BaseLib's CustomCardModel get a prefixed id (KLEEMOD-KABOOM),
                // so they declare loc via an ILocalizationProvider.Localization
                // override on the model instead -- see Kaboom.Localization.
                // KleeSelfCheck.Run() enforces that split at boot.
                ["JUMPY_DUMPTY.title"] = "Jumpy Dumpty",
                ["JUMPY_DUMPTY.description"] = "Deal {Damage:diff()} damage twice.",

                // Pop is now a CustomCardModel and declares its own loc.
            });

            LocManager.Instance.GetTable("characters").MergeWith(new Dictionary<string, string>
            {
                // Same UPPER_SNAKE_CASE Entry convention as cards.
                ["KLEE.title"] = "Klee",
                ["KLEE.description"] = "The Spark Knight of Mondstadt.",
                ["KLEE.titleObject"] = "Klee",
                ["KLEE.pronounSubject"] = "she",
                ["KLEE.pronounObject"] = "her",
                ["KLEE.pronounPossessive"] = "hers",
                ["KLEE.possessiveAdjective"] = "her",
            });

            Log.Info($"[{ModId}] Localization strings injected.");
        }
        catch (Exception e)
        {
            Log.Error($"[{ModId}] Failed to inject loc strings: {e}");
        }
    }

    // O5: ProbeBaseGameLocSyntax removed. It existed to read base-game loc
    // templates at runtime and settle the SmartFormat syntax question (single
    // braces, :diff()); that is now settled, encoded in the codegen emitter,
    // and enforced by KleeSelfCheck R6a/R6b. Keeping it meant a dozen INFO
    // lines per boot in the log we now read for telemetry.
}

// ---------------------------------------------------------------------------
//  Harmony patches
// ---------------------------------------------------------------------------

/// <summary>Injects our loc strings once LocManager has built its tables.</summary>
[HarmonyPatch(typeof(LocManager), nameof(LocManager.Initialize))]
internal static class LocManager_Initialize_Patch
{
    [HarmonyPostfix]
    public static void Postfix() => KleeMod.InjectLocStrings();
}

/// <summary>
/// C1: make Klee selectable.
///
/// ModelDb.AllCharacters is a HARDCODED five-element array, not a registry
/// scan — defining a CharacterModel subclass registers it with ModelDb.Get&lt;T&gt;()
/// but never puts it in that array. The character-select screen iterates
/// AllCharacters and uses UnlockState.Characters only as a lock filter, so
/// appending here is what actually makes Klee appear.
///
/// It also feeds every downstream consumer for free: UnlockState.Characters
/// derives from AllCharacters (removing only locked characters), as do
/// AllCards, AllRelics, and the pool collections. This is the single correct
/// injection point; patching UnlockState instead — as this mod originally did
/// — moves nothing, because the screen never consults it for membership.
/// </summary>
[HarmonyPatch(typeof(ModelDb), nameof(ModelDb.AllCharacters), MethodType.Getter)]
internal static class ModelDb_AllCharacters_Patch
{
    [HarmonyPostfix]
    public static void Postfix(ref IEnumerable<CharacterModel> __result)
    {
        var klee = ModelDb.Character<Klee>();
        if (!__result.Contains(klee))
        {
            __result = __result.Append(klee);
        }
    }
}

/// <summary>
/// Finding 22: any effect that draws N reward cards throws once N exceeds the
/// character's generatable pool, and Klee's pool is smaller than the largest N
/// in the game.
///
/// CardFactory.CreateForReward(player, cardCount, options) loops cardCount
/// times against an accumulating blacklist. Once every generatable card is
/// blacklisted, the surviving options are all Basic, RollForRarity walks
/// Common->Uncommon->Rare->Common, revisits its own start, returns None, and
/// the method throws (`sts2.decompiled.cs:452947`).
///
/// The largest N in the base game is SealedDeck's Neow option, which asks for
/// 30 (`:403214`). Klee ships 24 cards, 4 of them Basic, so 20 are generatable
/// and draw 21 is a guaranteed throw. RoomFullOfCheese.Gorge asks for 8 Commons
/// against her 14 and survives, but only by margin.
///
/// CLAMPING RATHER THAN BLOCKING THE OPTION, deliberately. Sealed Deck's
/// selector asks the player to keep 10, so offering 20 instead of 30 is a
/// smaller, still-playable choice rather than a missing Neow option — and the
/// clamp stops applying by itself the moment the pool grows past 30, which is
/// what C3 does. Removing the option would have to be remembered and undone.
///
/// Base characters are unaffected: their pools exceed every N in the game, so
/// the clamp never triggers for them. The rarity test mirrors the two branches
/// of CreateForReward exactly — Uniform excludes Basic and Ancient, everything
/// else can only roll Common/Uncommon/Rare — because a pool of Curses passes a
/// naive "not Basic" count and still throws.
/// </summary>
[HarmonyPatch(typeof(CardFactory), nameof(CardFactory.CreateForReward),
    new[] { typeof(Player), typeof(int), typeof(CardCreationOptions) })]
internal static class CardFactory_CreateForReward_Clamp_Patch
{
    [HarmonyPrefix]
    public static void Prefix(Player player, ref int cardCount,
                              CardCreationOptions options)
    {
        if (cardCount <= 0)
        {
            return;
        }

        var uniform = options.RarityOdds == CardRarityOddsType.Uniform;
        var available = options.GetPossibleCards(player).Count(c => uniform
            ? c.Rarity != CardRarity.Basic && c.Rarity != CardRarity.Ancient
            : c.Rarity == CardRarity.Common
              || c.Rarity == CardRarity.Uncommon
              || c.Rarity == CardRarity.Rare);

        if (cardCount > available)
        {
            Log.Warn($"[{KleeMod.ModId}] clamped a {cardCount}-card reward draw "
                   + $"to {available}: the pool cannot generate more without "
                   + "exhausting its blacklist and throwing.");
            cardCount = available;
        }
    }
}

/// <summary>
/// Finding 21: winning an Elite or Boss room SOFT LOCKS the run for any
/// character outside the base six.
///
/// ProgressSaveManager.CheckFifteenElitesDefeatedEpoch and its Boss twin are
/// closed type-switches over Ironclad/Silent/Regent/Defect/Necrobinder/Deprived
/// that end in `throw new ArgumentOutOfRangeException("character", ...)`. They
/// are called from UpdateAfterCombatWon, which runs inside
/// CombatManager.EndCombatInternal -> CheckWinCondition. The throw escapes into
/// an async continuation, so EndCombatInternal never completes: the enemies are
/// dead, the win is logged, and combat simply never ends. No crash dialog, no
/// recovery — End Turn does nothing and the run is lost.
///
/// NOW A CANARY, NOT THE FIX. The real cause was that Klee derived from
/// CharacterModel instead of CustomCharacterModel, so BaseLib's own prefix on
/// these exact three methods — `return !(localPlayer.Character is ICustomModel)`
/// — never skipped them. That is fixed at the source in Klee.cs, which means
/// BaseLib now short-circuits both methods before they can throw and this
/// finalizer should NEVER run again.
///
/// It is kept precisely because it logs when it fires. If that line ever
/// appears, BaseLib's guard has stopped applying to Klee — most likely because
/// someone changed her base type back or a BaseLib upgrade moved the interface
/// — and the log line is a far cheaper way to learn that than another soft
/// locked playtest. Deleting it would remove the detector, not dead code.
///
/// A Finalizer rather than a Prefix, deliberately: a Prefix would have to name
/// the six base types to decide whether to skip, and would break again the day
/// MegaCrit adds a seventh. Both methods read Character and then immediately
/// switch, with no side effect before the throw, so suppressing after the fact
/// loses nothing. The ParamName test keeps this narrow — any other exception
/// from these methods still propagates rather than being swallowed.
/// </summary>
[HarmonyPatch]
internal static class ProgressSaveManager_EpochCheck_Patch
{
    [HarmonyTargetMethods]
    public static IEnumerable<MethodBase> TargetMethods()
    {
        yield return AccessTools.Method(typeof(ProgressSaveManager),
            "CheckFifteenElitesDefeatedEpoch");
        yield return AccessTools.Method(typeof(ProgressSaveManager),
            "CheckFifteenBossesDefeatedEpoch");
    }

    [HarmonyFinalizer]
    public static Exception? Finalizer(Exception __exception, MethodBase __originalMethod)
    {
        if (__exception is ArgumentOutOfRangeException { ParamName: "character" })
        {
            Log.Warn($"[{KleeMod.ModId}] CANARY: suppressed {__originalMethod.Name}. "
                   + "BaseLib's ICustomModel prefix should have skipped this "
                   + "already -- check that Klee still derives from "
                   + "CustomCharacterModel (DECISIONS finding 21).");
            return null;                 // suppress; combat can now end
        }

        return __exception;              // anything else is not ours to eat
    }
}
