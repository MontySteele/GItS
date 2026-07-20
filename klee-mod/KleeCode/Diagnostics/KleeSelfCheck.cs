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

    private const int RuleCount = 6;

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

        // R3. Card rewards and transforms draw by RARITY, so "pool is non-empty"
        // is not the invariant that matters -- a pool of four Basic cards has
        // zero valid reward candidates and soft locks the reward screen after
        // EVERY combat, deterministically. That is exactly how this shipped:
        // the pool looked populated, and the check that would have caught it was
        // testing the wrong property.
        var pool = klee.CardPool?.AllCards?.ToList() ?? new();
        if (pool.Count == 0)
        {
            Fail("R3", "CardPool.AllCards is empty; card rewards and transforms will soft lock.");
        }
        else
        {
            foreach (var rarity in new[] { CardRarity.Common, CardRarity.Uncommon, CardRarity.Rare })
            {
                if (!pool.Any(c => c.Rarity == rarity))
                {
                    Fail("R3", $"CardPool has no {rarity} cards. Reward and transform screens draw "
                             + "by rarity and will soft lock with nothing valid to offer.");
                }
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
