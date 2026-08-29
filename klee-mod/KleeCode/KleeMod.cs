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

        // F2: per-type patching, NOT harmony.PatchAll. PatchAll aborts the
        // whole walk on the first patch class that throws, so one dead
        // reflection lookup silently disarms every patch after it -- including
        // the two shop/reward softlock guards below. KleePatchBootstrap applies
        // each class in its own try/catch and names any casualty at boot.
        KleePatchBootstrap.ApplyAll(new Harmony(ModId), typeof(KleeMod).Assembly);

        // The game already merged klee.pck (has_pck) before invoking us; this
        // logs proof-of-merge so a stale/missing pack shows up in godot.log.
        KleePck.LogStatus();

        // Convention-scene + build-id telemetry (animation sprint 1, A3 —
        // permanent). One line per shipped scene: path, found/missing, root
        // node type. A missing scene falls back quietly at the use site, so
        // this is where the miss gets loud.
        Diagnostics.KleeSceneTelemetry.LogStatus();

        // Aura application (R23): a standing combat-hook listener, registered
        // through the game's own mod-subscriber API. Elemental card hits apply
        // auras; AuraPower handles everything after that. See ElementalApplication.cs.
        // ModHelper keys subscriptions by id and silently rejects a duplicate.
        // Keep the roster behind ONE delegate so every character hook is live.
        ModHelper.SubscribeForCombatStateHooks(
            ModId,
            combatState =>
                Powers.KleeElementalHooks.Subscribe(combatState)
                    .Concat(Powers.FurinaResourceHooks.Subscribe(combatState))
                    .Concat(Powers.KokomiResourceHooks.Subscribe(combatState))
                    .Concat(Powers.KokomiGarmentHooks.Subscribe(combatState))
                    // EB-19/races-a + races-c: the four end-of-turn tenants
                    // that share the player's Block and the enemy reaction
                    // board no longer each override BeforeSideTurnEnd. This
                    // one listener drives them in the sim's fixed order.
                    .Concat(Powers.TurnEndSequencer.Subscribe(combatState))
                    // Track B's human feed: per-fight telemetry from normal
                    // play, in the schema the soak writes. Reads only -- see
                    // the three rules in PlayTelemetry.cs, the first of which
                    // is that a measurement must never desync a co-op table.
                    .Concat(Diagnostics.PlayTelemetryHooks.Subscribe(combatState)));

        Log.Info($"[{ModId}] Klee, Furina and Kokomi registered.");
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

                // EB-122: the three SELECTION-SCREEN prompts, ruled copy
                // 2026-08-25. Not card rows and not an exception to the split
                // above -- `<ENTRY>.selectionScreenPrompt` in the `cards`
                // table is the base game's own shape for this screen
                // (HAND_TRICK's and HEADBUTT's rows are exactly these two
                // verbs), and a LocString is a table plus a key with no
                // raw-text constructor, so ruled copy can only reach the
                // screen as a row. They are keyed on the VERB rather than on a
                // card id because one screen serves every carrier that prints
                // it -- the same "one member, one string" discipline the three
                // Prompt properties were written with. The pck carries no copy
                // of these, so this dictionary is their only source and a
                // missing entry is directly player-visible as a raw key.
                [Powers.SlyGrant.PromptKey] = Powers.SlyGrant.PromptText,
                [Powers.RecallFromDiscard.PromptKey] =
                    Powers.RecallFromDiscard.PromptText,
                [Powers.RecallFromExhaust.PromptKey] =
                    Powers.RecallFromExhaust.PromptText,
            });

            // Runtime copy of the custom-keyword loc. The pck carries the
            // same table for normal packaged builds, but keeping these rows in
            // the DLL makes a code-only playtest rebuild safe: newly generated
            // aura badges and combat-aware reaction tips never render raw keys
            // merely because the local art pack predates this code pass.
            //
            // EB-89: the numerals here are INTERPOLATED from the constants
            // they quote, never hand-typed. The pck's card_keywords.json wins
            // wherever it has a row (see the MergeWith below), so the two
            // copies still read identically today -- but a repricing must not
            // be able to leave the code-only playtest build telling a player a
            // retired number. The MULTIPLIERS (1.5x, 1.75x) stay literals on
            // purpose: they are floats, and interpolating a float renders it
            // under the host's culture, so a comma locale would print "1,5x".
            var keywordTable = LocManager.Instance.GetTable("card_keywords");
            var keywordFallback = new Dictionary<string, string>
                {
                    ["KLEEMOD-ELEMENTAL_SKILL.title"] = "Elemental Skill",
                    ["KLEEMOD-ELEMENTAL_SKILL.description"] =
                        $"Playing this card grants {Powers.BurstConstants.PerSkillTag} Burst Energy.",
                    ["KLEEMOD-APPLIES_PYRO.title"] = "Applies Pyro",
                    ["KLEEMOD-APPLIES_PYRO.description"] =
                        $"If the target has no aura, this applies Pyro for {Elements.ReactionConstants.AuraDurationTurns} turns. A different aura is consumed to trigger a Reaction instead.",
                    ["KLEEMOD-APPLIES_HYDRO.title"] = "Applies Hydro",
                    ["KLEEMOD-APPLIES_HYDRO.description"] =
                        $"If the target has no aura, this applies Hydro for {Elements.ReactionConstants.AuraDurationTurns} turns. A different aura is consumed to trigger a Reaction instead.",
                    ["KLEEMOD-APPLIES_ELECTRO.title"] = "Applies Electro",
                    ["KLEEMOD-APPLIES_ELECTRO.description"] =
                        $"If the target has no aura, this applies Electro for {Elements.ReactionConstants.AuraDurationTurns} turns. A different aura is consumed to trigger a Reaction instead.",
                    ["KLEEMOD-APPLIES_CRYO.title"] = "Applies Cryo",
                    ["KLEEMOD-APPLIES_CRYO.description"] =
                        $"If the target has no aura, this applies Cryo for {Elements.ReactionConstants.AuraDurationTurns} turns. A different aura is consumed to trigger a Reaction instead.",
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
                    ["KLEEMOD-OVERLOAD_PREVIEW.title"] = "Reaction preview: Overloaded",
                    ["KLEEMOD-OVERLOAD_PREVIEW.description"] =
                        $"This card supplies Pyro or Electro while an enemy has the other aura. It deals {Elements.ReactionConstants.OverloadSplash} splash damage to all enemies and applies {Elements.ReactionConstants.OverloadWeak} Weak to the reacted enemy.",
                    ["KLEEMOD-SUPERCONDUCT_PREVIEW.title"] = "Reaction preview: Superconduct",
                    ["KLEEMOD-SUPERCONDUCT_PREVIEW.description"] =
                        $"This card supplies Electro or Cryo while an enemy has the other aura. The reacted enemy gains {Elements.ReactionConstants.SuperconductVuln} Vulnerable.",
                    ["KLEEMOD-ELECTRO_CHARGED_PREVIEW.title"] = "Reaction preview: Electro-Charged",
                    ["KLEEMOD-ELECTRO_CHARGED_PREVIEW.description"] =
                        $"This card supplies Hydro or Electro while an enemy has the other aura. The reacted enemy gains a {Elements.ReactionConstants.ElectroChargedDot}-damage decaying damage-over-time effect.",
                    ["KLEEMOD-FROZEN_PREVIEW.title"] = "Reaction preview: Frozen",
                    ["KLEEMOD-FROZEN_PREVIEW.description"] =
                        $"This card supplies Hydro or Cryo while an enemy has the other aura. Its next action deals half damage; attacking it Shatters for {Elements.ReactionConstants.ShatterDamage} damage.",
                    ["KLEEMOD-FROZEN_BOSS_PREVIEW.title"] = "Reaction preview: Frozen (Boss)",
                    ["KLEEMOD-FROZEN_BOSS_PREVIEW.description"] =
                        $"Bosses cannot be Frozen. Hydro plus Cryo is consumed and applies {Elements.ReactionConstants.FrozenBossVuln} Vulnerable instead.",
                    ["KLEEMOD-SWIRL_PREVIEW.title"] = "Reaction preview: Swirl",
                    ["KLEEMOD-SWIRL_PREVIEW.description"] =
                        "This card supplies Anemo to an existing aura. The aura is consumed and copied onto all enemies.",
                    ["KLEEMOD-CRYSTALLIZE_PREVIEW.title"] = "Reaction preview: Crystallize",
                    ["KLEEMOD-CRYSTALLIZE_PREVIEW.description"] =
                        $"This card supplies Geo to an existing aura. The aura is consumed and you gain {Elements.ReactionConstants.CrystallizeBlock} Block.",

                    // Legibility sprint L-C: titles for the re-homed rider
                    // tips (FurinaRiderTips). These are NOT card keywords --
                    // they are hover-tip titles, which need a LocString --
                    // but they live in the same table so the one merge point
                    // covers them and a code-only rebuild never shows a raw
                    // key. The bodies are built per card in C#, because a
                    // shared row cannot carry a per-card rate.
                    [Cards.FurinaRiderTips.FanfareKey + ".title"] =
                        "Fanfare scaling",
                    [Cards.FurinaRiderTips.AuraKey + ".title"] =
                        "Elemental aura bonus",
                    [Cards.FurinaRiderTips.SalonKey + ".title"] =
                        "Salon scaling",
                    // The fourth rider tip had no row and shipped as the raw
                    // key: `Blocking Notes+` rendered
                    // "card_keywords.KLEEMOD-COMPANION_RIDER.title" on the
                    // card-reward screen of a live run (0.2-589). The pck's
                    // card_keywords.json carries none of these four either, so
                    // this dictionary is their only source and a missing entry
                    // is directly player-visible.
                    [Cards.FurinaRiderTips.CompanionKey + ".title"] =
                        "Companion scaling",

                    // B5: the member tips the deploy faces hand off to. Only
                    // the TITLES are rows -- the bodies are built live in
                    // SalonMemberTips, because the numbers live in
                    // SalonConstants and the cap is a per-player stat.
                    ["KLEEMOD-SALON_CRABALETTA.title"] =
                        "Mademoiselle Crabaletta",
                    ["KLEEMOD-SALON_USHER.title"] = "Gentilhomme Usher",
                    ["KLEEMOD-SALON_CHEVALMARIN.title"] =
                        "Surintendante Chevalmarin",
                    [Cards.SalonMemberTips.SalonRulesKey + ".title"] =
                        "Salon",

                    // EB-53/N1: the end-of-turn docket's per-slot hovers.
                    // TITLES only, the same bargain as the member tips above --
                    // every body is built live in TurnEndAttribution from the
                    // constants the resolution reads, so a repricing cannot
                    // leave a row quoting a retired number.
                    [Powers.TurnEndAttribution.MasqueKey + ".title"] =
                        "Bond of Life",
                    [Powers.TurnEndAttribution.SparksKey + ".title"] =
                        "Sparks 'n' Splash",
                    [Powers.TurnEndAttribution.OzKey + ".title"] =
                        "Oz, at Your Side",
                    [Powers.TurnEndAttribution.KurageKey + ".title"] =
                        "Bake-Kurage",

                    // Kokomi's two hidden reads (KokomiRiderTips). Both
                    // resolve somewhere no card face can print -- the pulse at
                    // end of turn, the Garment rider on OTHER cards -- so the
                    // tip is the only surface either number has.
                    [Cards.KokomiRiderTips.PulseKey + ".title"] =
                        "Bake-Kurage pulse",
                    [Cards.KokomiRiderTips.GarmentKey + ".title"] =
                        "Ceremonial Garment is active",
                    // L4b: the printed Charge rider's rate. Unlike the two
                    // above, the NUMBER was always visible -- this row titles
                    // the tip that says what the number is made of.
                    [Cards.KokomiRiderTips.ChargeKey + ".title"] =
                        "Charge scaling",
                    // EB-64's shape, one key over: Muster had no row and
                    // shipped as the raw key -- `Reinforcements` rendered
                    // "card_keywords.KLEEMOD-MUSTER.title" as the keyword name
                    // on a live shop screen (0.2-634, EB-53 capture session).
                    [Cards.KokomiRiderTips.MusterKey + ".title"] = "Muster",
                    // QUARANTINED (R213 E1): the Charge KEYWORD's title. The
                    // BODY is built live in KokomiRiderTips, because it
                    // quotes CHARGE_PER_EXHAUST and reads the current bank --
                    // the same bargain the Muster and pulse tips already
                    // make. Distinct from CHARGE_RIDER above, which titles a
                    // per-card RATE tip on a card that READS the meter.
                    [Cards.KokomiRiderTips.ChargeWordKey + ".title"] =
                        "Charge",
                    // The Charge keyword's twin, one meter over and three
                    // characters wide: the Burst KEYWORD's title. The body is
                    // built live in KleeCardTooltips because the meter's size
                    // is per character and the tip says what the owner holds.
                    // The retired BurstMeterPower badge used to be the only
                    // surface that ever defined the word; nothing replaced it
                    // until now.
                    [Cards.KleeCardTooltips.BurstKey + ".title"] =
                        "Burst Energy",
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

        // C2: gate on OUR roster before touching anything.
        //
        // The clamp was written to be self-limiting -- base pools exceed every
        // N in the game, so `cardCount > available` is false for them and the
        // patch returns having changed nothing. That is true today and it is
        // an argument, not a guarantee: it rests on a claim about six pools
        // this mod does not own and cannot test. If it were ever wrong, the
        // failure would be this mod silently reducing a base character's Neow
        // reward, which is the one thing a roster mod must never do.
        //
        // The gate also stops us counting a base character's whole generatable
        // pool on every reward draw, which is what the check below costs.
        if (!CompanionPool.IsRosterCharacter(player))
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
    // F2: null-guarded. AccessTools.Method returns null when a name stops
    // resolving, and yielding that null makes Harmony throw about a null
    // element rather than about the method that died. Routing through
    // KleePatchBootstrap records the miss BY NAME and drops the null, so a
    // rename of one of these two costs the one canary rather than the batch.
    // If BOTH die the class arms nothing, which the bootstrap reports as a
    // failure -- the alternative is a canary that silently stopped watching.
    [HarmonyTargetMethods]
    public static IEnumerable<MethodBase> TargetMethods()
    {
        var targets = new[]
        {
            KleePatchBootstrap.ResolveMethod(typeof(ProgressSaveManager),
                "CheckFifteenElitesDefeatedEpoch"),
            KleePatchBootstrap.ResolveMethod(typeof(ProgressSaveManager),
                "CheckFifteenBossesDefeatedEpoch"),
        };

        return targets.Where(m => m != null)!;
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
