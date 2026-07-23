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
        Log.Info($"[{ModId}] Initializing Teyvat Spire roster...");

        try
        {
            var harmony = new Harmony(ModId);
            harmony.PatchAll(typeof(KleeMod).Assembly);
        }
        catch (Exception e)
        {
            Log.Error($"[{ModId}] Harmony patching failed: {e}");
        }

        // The game already merged klee.pck (has_pck) before invoking us; this
        // logs proof-of-merge so a stale/missing pack shows up in godot.log.
        KleePck.LogStatus();

        // Aura application (R23): a standing combat-hook listener, registered
        // through the game's own mod-subscriber API. Elemental card hits apply
        // auras; AuraPower handles everything after that. See ElementalApplication.cs.
        // ModHelper keys subscriptions by id and silently rejects a duplicate.
        // Keep the roster behind ONE delegate so every character hook is live.
        ModHelper.SubscribeForCombatStateHooks(
            ModId,
            combatState =>
                Powers.KleeElementalHooks.Subscribe(combatState)
                    .Concat(Powers.FurinaResourceHooks.Subscribe(combatState)));

        Log.Info($"[{ModId}] Klee and Furina registered.");
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
                //    "Found end tag center, expected Block". Custom keyword
                //    ids are allocated by BaseLib from KleeKeywords; their
                //    strings ship in the pck's card_keywords loc table.
                // ONLY plain CardModel stubs belong here. Cards that derive from
                // BaseLib's CustomCardModel get a prefixed id (KLEEMOD-KABOOM),
                // so they declare loc via an ILocalizationProvider.Localization
                // override on the model instead -- see Kaboom.Localization.
                // KleeSelfCheck.Run() enforces that split at boot.
                ["JUMPY_DUMPTY.title"] = "Jumpy Dumpty",
                ["JUMPY_DUMPTY.description"] = "Deal {Damage:diff()} damage twice.",

                // Pop is now a CustomCardModel and declares its own loc.
            });

            // Runtime copy of the custom-keyword loc. The pck carries the
            // same table for normal packaged builds, but keeping these rows in
            // the DLL makes a code-only playtest rebuild safe: newly generated
            // aura badges and combat-aware reaction tips never render raw keys
            // merely because the local art pack predates this code pass.
            var keywordTable = LocManager.Instance.GetTable("card_keywords");
            var keywordFallback = new Dictionary<string, string>
                {
                    ["KLEEMOD-ELEMENTAL_SKILL.title"] = "Elemental Skill",
                    ["KLEEMOD-ELEMENTAL_SKILL.description"] =
                        "Playing this card grants 5 Burst Energy.",
                    ["KLEEMOD-APPLIES_PYRO.title"] = "Applies Pyro",
                    ["KLEEMOD-APPLIES_PYRO.description"] =
                        "If the target has no aura, this applies Pyro for 2 turns. A different aura is consumed to trigger a Reaction instead.",
                    ["KLEEMOD-APPLIES_HYDRO.title"] = "Applies Hydro",
                    ["KLEEMOD-APPLIES_HYDRO.description"] =
                        "If the target has no aura, this applies Hydro for 2 turns. A different aura is consumed to trigger a Reaction instead.",
                    ["KLEEMOD-APPLIES_ELECTRO.title"] = "Applies Electro",
                    ["KLEEMOD-APPLIES_ELECTRO.description"] =
                        "If the target has no aura, this applies Electro for 2 turns. A different aura is consumed to trigger a Reaction instead.",
                    ["KLEEMOD-APPLIES_CRYO.title"] = "Applies Cryo",
                    ["KLEEMOD-APPLIES_CRYO.description"] =
                        "If the target has no aura, this applies Cryo for 2 turns. A different aura is consumed to trigger a Reaction instead.",
                    ["KLEEMOD-BOMB.title"] = "Bomb",
                    ["KLEEMOD-BOMB.description"] =
                        "Detonates at the start of your turn or early when its enemy takes unblocked Attack damage. The first attack that enemy makes while Bombed each combat deals 25% less damage.",
                    ["KLEEMOD-CONFISCATED.title"] = "Confiscated",
                    ["KLEEMOD-CONFISCATED.description"] =
                        "A 1-cost Status card that does nothing.",
                    ["KLEEMOD-VAPORIZE_PREVIEW.title"] = "Reaction preview: Vaporize",
                    ["KLEEMOD-VAPORIZE_PREVIEW.description"] =
                        "This card supplies Pyro or Hydro while an enemy has the other aura. The triggering hit deals 1.5x damage and consumes the aura.",
                    ["KLEEMOD-MELT_PREVIEW.title"] = "Reaction preview: Melt",
                    ["KLEEMOD-MELT_PREVIEW.description"] =
                        "This card supplies Pyro or Cryo while an enemy has the other aura. The triggering hit deals 1.75x damage and consumes the aura.",
                    ["KLEEMOD-OVERLOAD_PREVIEW.title"] = "Reaction preview: Overload",
                    ["KLEEMOD-OVERLOAD_PREVIEW.description"] =
                        "This card supplies Pyro or Electro while an enemy has the other aura. It deals 6 splash damage to all enemies and applies 1 Weak to the reacted enemy.",
                    ["KLEEMOD-SUPERCONDUCT_PREVIEW.title"] = "Reaction preview: Superconduct",
                    ["KLEEMOD-SUPERCONDUCT_PREVIEW.description"] =
                        "This card supplies Electro or Cryo while an enemy has the other aura. The reacted enemy gains 2 Vulnerable.",
                    ["KLEEMOD-ELECTRO_CHARGED_PREVIEW.title"] = "Reaction preview: Electro-Charged",
                    ["KLEEMOD-ELECTRO_CHARGED_PREVIEW.description"] =
                        "This card supplies Hydro or Electro while an enemy has the other aura. The reacted enemy gains a 4-damage decaying damage-over-time effect.",
                    ["KLEEMOD-FROZEN_PREVIEW.title"] = "Reaction preview: Frozen",
                    ["KLEEMOD-FROZEN_PREVIEW.description"] =
                        "This card supplies Hydro or Cryo while an enemy has the other aura. Its next action deals half damage; attacking it Shatters for 6 damage.",
                    ["KLEEMOD-FROZEN_BOSS_PREVIEW.title"] = "Reaction preview: Frozen (Boss)",
                    ["KLEEMOD-FROZEN_BOSS_PREVIEW.description"] =
                        "Bosses cannot be Frozen. Hydro plus Cryo is consumed and applies 2 Vulnerable instead.",
                    ["KLEEMOD-SWIRL_PREVIEW.title"] = "Reaction preview: Swirl",
                    ["KLEEMOD-SWIRL_PREVIEW.description"] =
                        "This card supplies Anemo to an existing aura. The aura is consumed and copied onto all enemies.",
                    ["KLEEMOD-CRYSTALLIZE_PREVIEW.title"] = "Reaction preview: Crystallize",
                    ["KLEEMOD-CRYSTALLIZE_PREVIEW.description"] =
                        "This card supplies Geo to an existing aura. The aura is consumed and you gain 4 Block.",
                };
            keywordTable.MergeWith(keywordFallback
                .Where(pair => !keywordTable.HasEntry(pair.Key))
                .ToDictionary(pair => pair.Key, pair => pair.Value));

            // Klee's character strings moved onto the model itself
            // (Klee.Localization) when she became a CustomCharacterModel:
            // BaseLib prefixed her id to KLEEMOD-KLEE, so the hardcoded
            // "KLEE.*" keys that used to live here targeted an id nothing
            // looks up -- finding 23, same failure mode R4 documents for
            // cards. The self-check's R5 rule caught it at boot.

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

// ---------------------------------------------------------------------------
// ModelDb_AllCharacters_Patch — REMOVED (finding 27). BaseLib's
// AddCustomCharacters postfix appends every CustomContentDictionary character
// to ModelDb.AllCharacters, unconditionally and with no duplicate check.
// Klee has been in that dictionary since the CustomCharacterModel migration
// (her base ctor registers her), so from finding 21 onward BOTH appends ran
// and character select showed two Klees. Finding 21's "verified BaseLib does
// not append custom characters" was wrong — that check found the
// GetVisibleCharacters FILTER transpiler and stopped there, missing the
// separate append postfix. The append is BaseLib's job now; a mod-side
// append patch would be reintroducing the duplicate.
// ---------------------------------------------------------------------------

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
/// Finding 24: entering ANY shop soft locks the run while Klee's pool has no
/// Power cards.
///
/// MerchantInventory.PopulateCharacterCardEntries stocks a hardcoded slot
/// layout — 2 Attacks, 2 Skills, 1 Power — and CreateForMerchant(player,
/// options, type) rolls a rarity that must contain a card of that type.
/// GetNextAllowedRarity wraps Common->Uncommon->Rare and returns None when no
/// rarity has one, and the method throws. The throw happens inside
/// MerchantRoom.EnterInternal's async continuation, so the room never finishes
/// entering: black screen, no crash dialog, run lost. Klee ships 24 cards and
/// not one is a Power, so this was every shop, deterministically.
///
/// SUBSTITUTING THE TYPE RATHER THAN EMPTYING THE SLOT, deliberately. The
/// merchant's 5-slot layout is load-bearing UI — Populate has no "no card"
/// path — so the safe degradation is offering a Skill or Attack where the
/// Power would sit. The fallback order prefers Skill (the closer analogue of
/// a Power purchase: utility, not damage). Like the reward-draw clamp above,
/// this patch stops changing anything the moment the pool contains a Power
/// card, which is the real fix and a C3 content item.
///
/// The eligibility test mirrors CreateForMerchant exactly: it excludes Basic
/// (the method's own filter) and demands Common/Uncommon/Rare, because the
/// shop rarity roll can only ever land on those three (same reasoning as
/// self-check R3a). Base characters stock every type and never hit the
/// fallback.
/// </summary>
[HarmonyPatch(typeof(CardFactory), nameof(CardFactory.CreateForMerchant),
    new[] { typeof(Player), typeof(IEnumerable<CardModel>), typeof(CardType) })]
internal static class CardFactory_CreateForMerchant_TypeFallback_Patch
{
    [HarmonyPrefix]
    public static void Prefix(IEnumerable<CardModel> options, ref CardType type)
    {
        // Callers pass materialized lists; guard anyway so a lazy sequence is
        // only enumerated here once.
        var pool = options as IReadOnlyCollection<CardModel> ?? options.ToList();

        bool Stocks(CardType t) => pool.Any(c => c.Type == t
            && (c.Rarity == CardRarity.Common
                || c.Rarity == CardRarity.Uncommon
                || c.Rarity == CardRarity.Rare));

        if (Stocks(type))
        {
            return;
        }

        foreach (var fallback in new[] { CardType.Skill, CardType.Attack, CardType.Power })
        {
            if (Stocks(fallback))
            {
                Log.Warn($"[{KleeMod.ModId}] merchant slot wanted a {type} card but the "
                       + $"pool has none at a rollable rarity; offering a {fallback} "
                       + "instead. This stops happening once the pool stocks that type.");
                type = fallback;
                return;
            }
        }

        // Nothing of any type is rollable; fall through and let the game's own
        // descriptive exception surface the truly-broken pool.
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
