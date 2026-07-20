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

    // Distinct rule labels that can actually reach the log:
    //   R1, R2, R3, R3a, R3b, R3c, R3d, R4, R5, R6a, R6b, R7
    // This was 8 while R5/R6a/R6b were documented but unattributable -- the
    // helpers that emit them hardcoded R4 and R6, so those three strings could
    // never appear. Fixing the labels is what makes the count honest. Note
    // R4 and R5 come from a `rule` parameter, so grepping for Fail("R... will
    // not find them; count the call sites, not the literals.
    private const int RuleCount = 12;

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

        // R7. Every starting relic must RESOLVE ITS POOL. RelicModel.Pool is
        // non-virtual First() over AllRelicPools; a relic in no pool throws
        // InvalidOperationException — and that getter runs inside
        // SelectCharacter via DynamicDescription, aborting selection after the
        // panel updates but before the lobby assignment (finding 27: Pounding
        // Surprise shipped poolless and Klee looked selected while the run
        // would start as the previously clicked character — finding 11's
        // symptom through a new door).
        foreach (var relic in relics)
        {
            try
            {
                _ = relic.Pool;
            }
            catch (InvalidOperationException)
            {
                Fail("R7", $"starting relic {relic.GetType().Name} is in NO relic pool; "
                         + "RelicModel.Pool throws and SelectCharacter aborts mid-method, "
                         + "so the character looks selected but is not.");
            }
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
        // The test is "is Common/Uncommon/Rare", NOT "is not Basic/Ancient".
        // Those differ, and the difference is a false negative: CardRarity also
        // has Event, Token, Status, Curse and Quest. Those survive a
        // not-Basic-not-Ancient filter but can never satisfy the rarity roll,
        // because RollForRarity only ever produces Common/Uncommon/Rare and the
        // wrapping fallback only cycles between them. A pool of 1 Common and 2
        // Curses would pass both R3a and R3b under the old filter and still
        // throw on the second draw of a three-card screen.
        // (`!= Basic && != Ancient` is correct for exactly one caller -- the
        // Uniform-odds branch at `sts2.decompiled.cs:452938` -- which is not
        // the branch ordinary reward screens take.)
        var generatable = pool
            .Where(c => c.Rarity == CardRarity.Common
                     || c.Rarity == CardRarity.Uncommon
                     || c.Rarity == CardRarity.Rare)
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
        // nothing of any rarity left.
        //
        // The bound is NOT 3. Three is an ordinary reward screen, but the
        // largest single draw in the base game is SealedDeck's Neow option
        // asking for 30 (`sts2.decompiled.cs:403214`); RoomFullOfCheese.Gorge
        // asks for 8. A threshold of 3 passed Klee's 20-card pool without
        // comment while Sealed Deck was a guaranteed throw -- the earlier
        // comment here conceded that "Discovery-style effects can ask for more"
        // and then used the floor anyway, which is how the gap survived review.
        //
        // KleeMod's CreateForReward prefix now clamps oversized draws, so this
        // is a WARNING about pool depth rather than a live soft lock: below
        // this bound, some effects quietly offer fewer cards than designed.
        const int LargestRewardDraw = 30;
        if (generatable.Count > 0 && generatable.Count < LargestRewardDraw)
        {
            Fail("R3b", $"CardPool has {generatable.Count} generatable card(s), fewer than the "
                      + $"{LargestRewardDraw} the largest reward draw (SealedDeck) requests. Each "
                      + "pick is blacklisted from the next draw, so without the clamp patch this "
                      + "would throw; with it, such effects silently offer fewer cards.");
        }

        // R3d. Merchant type coverage. MerchantInventory stocks a hardcoded
        // slot layout from the character pool -- 2 Attacks, 2 Skills, 1 Power
        // -- and CreateForMerchant throws if the requested type has no card at
        // a rollable rarity (Common/Uncommon/Rare; Basic is filtered and the
        // shop roll cannot produce anything else). The throw escapes into
        // MerchantRoom.EnterInternal's async continuation, so entering ANY
        // shop is a black-screen soft lock -- finding 24, hit on the first
        // shop playtest. KleeMod's CreateForMerchant prefix now substitutes a
        // stocked type, so this reports as pool-depth truth rather than a live
        // soft lock: below full coverage, some shop slots sell a different
        // type than designed.
        foreach (var type in new[] { CardType.Attack, CardType.Skill, CardType.Power })
        {
            if (!generatable.Any(c => c.Type == type))
            {
                Fail("R3d", $"CardPool has no {type} cards at a rollable rarity. The merchant "
                          + "always stocks this type; without the type-fallback patch every "
                          + "shop soft locks, with it the slot silently sells another type.");
            }
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
            CheckLocEntry(cards, "cards", entry, card.GetType().Name, "R4");
        }

        // R5. Same check for the character surface.
        CheckLocEntry(characters, "characters", klee.Id.Entry, nameof(Klee), "R5");
    }

    // `rule` is a parameter rather than a literal because this helper serves
    // both R4 (cards) and R5 (character). It used to hardcode "R4", which meant
    // a missing CHARACTER loc key reported as R4 and the string "R5" could
    // never appear in output at all -- the rule was documented, reachable, and
    // unattributable.
    private static void CheckLocEntry(LocTable table, string tableName, string entry,
                                      string owner, string rule)
    {
        foreach (var suffix in new[] { "title", "description" })
        {
            var key = $"{entry}.{suffix}";

            if (!table.HasEntry(key))
            {
                Fail(rule, $"{owner}: missing loc key \"{key}\" in table \"{tableName}\". "
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
            Fail("R6a", $"{owner} [{key}]: contains \"{{{{\". SmartFormat uses single braces; "
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
                Fail("R6b", $"{owner} [{key}]: \"[{tag}]\" is not a known BBCode tag. "
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
