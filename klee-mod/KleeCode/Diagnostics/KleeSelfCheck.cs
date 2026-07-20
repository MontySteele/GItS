using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Cards;

namespace KleeMod.Diagnostics;

/// <summary>
/// Boot-time conformance check for the invariants the base game assumes but
/// never documents. Every rule here corresponds to a bug that actually shipped
/// and cost a debug cycle -- see DECISIONS.md findings 9-13.
///
/// WHY RUNTIME RATHER THAN A COMPILE STEP: all of these depend on *evaluated*
/// values, not source text. StartingRelics is a computed property; a card's loc
/// key is Id.Entry, which BaseLib rewrites at registration; the loc tables live
/// compressed inside the game's .pck. None of it is visible to a static pass.
/// The complementary static rules that ARE source-visible live in
/// build/validate.ps1, which gates deploy.
///
/// THIS NEVER THROWS. A validator that bricks the boot is the same failure mode
/// it exists to prevent. Findings are logged as errors and counted; the game
/// continues. Grep the log for "SELFCHECK".
/// </summary>
internal static class KleeSelfCheck
{
    private const string Tag = "SELFCHECK";

    /// <summary>
    /// BBCode tags the base game's loc strings actually use. Anything else in
    /// square brackets is almost certainly a DynamicVar written with the wrong
    /// syntax -- "[Block]" collides with the [center] wrapper the card renderer
    /// adds and throws "Found end tag center, expected Block".
    /// </summary>
    private static readonly HashSet<string> KnownBbcodeTags = new(StringComparer.OrdinalIgnoreCase)
    {
        "center", "left", "right", "b", "i", "u", "s",
        "color", "bgcolor", "fgcolor", "font", "img", "url",
        "gold", "keyword", "wave", "shake", "p",
    };

    private static readonly List<string> Findings = new();

    public static void Run()
    {
        Findings.Clear();

        try
        {
            var klee = ModelDb.Character<Klee>();

            CheckCharacterInvariants(klee);
            CheckLocalization(klee);
        }
        catch (Exception e)
        {
            // A throw in here means an assumption is wrong somewhere upstream,
            // which is itself the kind of finding this class exists to surface.
            Log.Error($"[{KleeMod.ModId}] {Tag} aborted: {e}");
            return;
        }

        if (Findings.Count == 0)
        {
            Log.Info($"[{KleeMod.ModId}] {Tag} passed ({RuleCount} rules).");
            return;
        }

        Log.Error($"[{KleeMod.ModId}] {Tag} FAILED with {Findings.Count} finding(s):");
        foreach (var finding in Findings)
        {
            Log.Error($"[{KleeMod.ModId}] {Tag}   - {finding}");
        }
    }

    private const int RuleCount = 8;

    private static void Fail(string rule, string detail) => Findings.Add($"[{rule}] {detail}");

    // -----------------------------------------------------------------------
    //  Character invariants
    // -----------------------------------------------------------------------

    private static void CheckCharacterInvariants(Klee klee)
    {
        // R1. CharacterSelectScreen.SelectCharacter does an unconditional
        // StartingRelics[0]. An empty array does not degrade -- it throws
        // mid-method, leaving the screen in a state where Klee looks selectable
        // but silently starts the run as whoever was highlighted before.
        // This shipped once (finding 11) and cost a full debug cycle.
        var relics = klee.StartingRelics?.ToList() ?? new();
        if (relics.Count == 0)
        {
            Fail("R1", "StartingRelics is empty; SelectCharacter indexes [0] unconditionally "
                     + "and will throw, making the character appear selectable but not select.");
        }

        // R2. An empty starting deck means no draw pile and an immediate soft
        // lock on the first combat turn.
        var deck = klee.StartingDeck?.ToList() ?? new();
        if (deck.Count == 0)
        {
            Fail("R2", "StartingDeck is empty; first combat will have nothing to draw.");
        }

        // R3. The reward-screen small-pool guard. Kept permanently: finding 17
        // was fixed incidentally, by the codegen happening to produce a rarity
        // spread, and an incidental fix is one refactor away from regressing.
        //
        // The rules below are derived from CardFactory.CreateForReward as it is
        // actually written, not from the symptom we observed. Reading it
        // corrected our own earlier comment here, which claimed any missing
        // rarity soft locks deterministically. It does not: RollForRarity is
        // handed the set of rarities present in the *post-blacklist* pool and
        // GetNextAllowedRarity walks to the next one with wrapping, so a single
        // dry rarity degrades gracefully. Three narrower things do throw.
        var pool = klee.CardPool?.AllCards?.ToList() ?? new();
        if (pool.Count == 0)
        {
            Fail("R3", "CardPool.AllCards is empty; card rewards and transforms will soft lock.");
            return;
        }

        // R3a. THE softlock invariant. Basic and Ancient are excluded from
        // reward generation outright, and the rarity-wrapping fallback cycles
        // only Common/Uncommon/Rare -- it can never land back on Basic. So a
        // pool with no card in those three rarities makes GetNextAllowedRarity
        // wrap to its start and return CardRarity.None, which throws. This is
        // the real shape of finding 17: not "no rares", but "nothing but
        // Basic". It is the one condition here that locks every reward screen.
        var generatable = pool
            .Where(c => c.Rarity != CardRarity.Basic && c.Rarity != CardRarity.Ancient)
            .ToList();
        if (generatable.Count == 0)
        {
            Fail("R3a", "CardPool has no Common/Uncommon/Rare cards. Reward generation excludes "
                      + "Basic and Ancient and its rarity fallback cannot wrap back onto them, "
                      + "so every reward screen will throw. This is the finding-17 soft lock.");
        }

        // R3b. Blacklist exhaustion. CreateForReward draws cardCount times,
        // adding each pick to a blacklist that is subtracted from the pool
        // before the next draw. If the whole generatable pool is smaller than
        // one screen's worth of offers, the last draw sees an empty pool and
        // throws -- and no rarity fallback can save it, because there is
        // nothing of any rarity left. Three is the standard reward count;
        // Discovery-style effects can ask for more, so this is a floor.
        const int MaxRewardOffers = 3;
        if (generatable.Count > 0 && generatable.Count < MaxRewardOffers)
        {
            Fail("R3b", $"CardPool has only {generatable.Count} generatable card(s), fewer than the "
                      + $"{MaxRewardOffers} a reward screen offers. Each pick is blacklisted from the "
                      + "next draw, so the screen will exhaust the pool and throw.");
        }

        // R3c. Rarity coverage. Not a soft lock on its own, per the fallback
        // above -- but a missing rarity means the declared rarity odds silently
        // collapse onto whatever remains, so the pool no longer plays the way
        // the sheet says it does. Worth knowing about; distinct from R3a.
        foreach (var rarity in new[] { CardRarity.Common, CardRarity.Uncommon, CardRarity.Rare })
        {
            if (!pool.Any(c => c.Rarity == rarity))
            {
                Fail("R3c", $"CardPool has no {rarity} cards. Not a soft lock -- reward generation "
                          + "falls through to the next rarity -- but the rarity odds collapse onto "
                          + "the remaining tiers, so drafts will not match the sheet.");
            }
        }
    }

    // -----------------------------------------------------------------------
    //  Localization
    // -----------------------------------------------------------------------

    private static void CheckLocalization(Klee klee)
    {
        var cards = LocManager.Instance.GetTable("cards");
        var characters = LocManager.Instance.GetTable("characters");

        // Union of pool and starting deck: a starter stub can legitimately sit
        // outside the pool, and both surfaces render text.
        var allCards = new List<CardModel>();
        allCards.AddRange(klee.CardPool?.AllCards ?? Enumerable.Empty<CardModel>());
        allCards.AddRange(klee.StartingDeck ?? Enumerable.Empty<CardModel>());

        var seen = new HashSet<string>(StringComparer.Ordinal);

        foreach (var card in allCards)
        {
            var entry = card.Id.Entry;
            if (!seen.Add(entry)) continue;

            // R4. The key is Id.Entry, which is NOT simply the class name
            // uppercased: BaseLib prefixes custom models (KABOOM ->
            // KLEEMOD-KABOOM). Hardcoding the unprefixed key registers strings
            // against an id nothing looks up, and the UI renders the raw key.
            // Reading Id.Entry back off the live model is the only way to be
            // certain the string we wrote is the string that will be read.
            CheckLocEntry(cards, "cards", entry, card.GetType().Name);
        }

        // R5. Same check for the character surface.
        CheckLocEntry(characters, "characters", klee.Id.Entry, nameof(Klee));
    }

    private static void CheckLocEntry(LocTable table, string tableName, string entry, string owner)
    {
        foreach (var suffix in new[] { "title", "description" })
        {
            var key = $"{entry}.{suffix}";

            if (!table.HasEntry(key))
            {
                Fail("R4", $"{owner}: missing loc key \"{key}\" in table \"{tableName}\". "
                         + "The UI will render the raw key.");
                continue;
            }

            CheckLocSyntax(owner, key, table.GetRawText(key));
        }
    }

    private static void CheckLocSyntax(string owner, string key, string raw)
    {
        if (string.IsNullOrWhiteSpace(raw)) return;

        // R6a. Values are SmartFormat templates, which use SINGLE braces.
        // "{{Damage}}" is not a placeholder and renders literally.
        if (raw.Contains("{{", StringComparison.Ordinal))
        {
            Fail("R6", $"{owner} [{key}]: contains \"{{{{\". SmartFormat uses single braces; "
                     + "doubled braces render literally.");
        }

        // R6b. Square brackets are BBCode, not keyword markup. A DynamicVar
        // written as "[Block]" parses as an unclosed tag and throws inside the
        // renderer, taking the whole card description with it.
        foreach (Match m in Regex.Matches(raw, @"\[/?([A-Za-z_][A-Za-z0-9_]*)"))
        {
            var tag = m.Groups[1].Value;
            if (!KnownBbcodeTags.Contains(tag))
            {
                Fail("R6", $"{owner} [{key}]: \"[{tag}]\" is not a known BBCode tag. "
                         + "If this is a variable it must be written {" + tag + "}; "
                         + "an unknown tag throws \"Found end tag center, expected " + tag + "\".");
            }
        }
    }
}

/// <summary>
/// Runs the self-check once every model is constructed and every loc table is
/// populated. ModelDb.Init is the correct join point: it is where the game
/// builds its content registry, and it is the same method BaseLib postfixes to
/// inject ILocalizationProvider strings.
///
/// Priority.Last so we observe the final state -- BaseLib's loc injection is
/// also a postfix here, and checking before it runs would report every custom
/// model as missing its strings.
/// </summary>
[HarmonyPatch(typeof(ModelDb), "Init")]
internal static class ModelDb_Init_SelfCheck_Patch
{
    [HarmonyPostfix]
    [HarmonyPriority(Priority.Last)]
    public static void Postfix() => KleeSelfCheck.Run();
}
