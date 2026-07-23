using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using BaseLib.Utils;
using Godot;
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
            foreach (var character in new CharacterModel[]
                     {
                         ModelDb.Character<Klee>(),
                         ModelDb.Character<Furina>(),
                     })
            {
                CheckCharacterInvariants(character);
                CheckCharacterAssets(character);
                CheckLocalization(character);
            }
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
            Log.Info($"[{KleeMod.ModId}] {Tag} passed "
                   + $"({RuleCount} rule families across 2 characters).");
            return;
        }

        Log.Error($"[{KleeMod.ModId}] {Tag} FAILED with {Findings.Count} finding(s):");
        foreach (var finding in Findings)
        {
            Log.Error($"[{KleeMod.ModId}] {Tag}   - {finding}");
        }
    }

    // Distinct rule labels that can actually reach the log:
    //   R1, R2, R3, R3a, R3b, R3c, R3d, R4, R5, R6a, R6b, R7, R8, R9, R10, R11, R12
    // This was 8 while R5/R6a/R6b were documented but unattributable -- the
    // helpers that emit them hardcoded R4 and R6, so those three strings could
    // never appear. Fixing the labels is what makes the count honest. Note
    // R4 and R5 come from a `rule` parameter, so grepping for Fail("R... will
    // not find them; count the call sites, not the literals.
    private const int RuleCount = 17;

    private static void Fail(string rule, string detail) => Findings.Add($"[{rule}] {detail}");

    // -----------------------------------------------------------------------
    //  Character invariants
    // -----------------------------------------------------------------------

    private static void CheckCharacterInvariants(CharacterModel character)
    {
        // R1. CharacterSelectScreen.SelectCharacter does an unconditional
        // StartingRelics[0]. An empty array does not degrade -- it throws
        // mid-method, leaving the screen in a state where Klee looks selectable
        // but silently starts the run as whoever was highlighted before.
        // This shipped once (finding 11) and cost a full debug cycle.
        var relics = character.StartingRelics?.ToList() ?? new();
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
        var deck = character.StartingDeck?.ToList() ?? new();
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
        var pool = character.CardPool?.AllCards?.ToList() ?? new();
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

        // R10. DynamicVarSet's constructor throws on a duplicate var name, and
        // it is built lazily inside CardFactory.CreateForReward -- so the
        // reward screen dies on whatever run first ROLLS the card, picked or
        // not (playtest 2026-07-23: StageLights/CourtroomDrama each declared
        // "PowerAmount" twice). The generator now fails on collisions at emit
        // time; evaluating the getter here catches hand-written cards too,
        // at boot instead of mid-run.
        foreach (var card in pool.Concat(deck))
        {
            try
            {
                _ = card.DynamicVars;
            }
            catch (ArgumentException e)
            {
                Fail("R10", $"{card.GetType().Name}: DynamicVars getter threw \"{e.Message}\" -- "
                          + "duplicate DynamicVar name; every reward screen that rolls this "
                          + "card will throw.");
            }
        }

        // R11. Base-game content resolves "the character's Strike/Defend" with
        // an unguarded First() over the pool: LargeCapsule.GetStrikeForCharacter
        // is `AllCards.First(c => c.Rarity == Basic && c.Tags.Contains(
        // CardTag.Strike))`, and the throw lands inside the Ancient event's
        // option handler, hanging the room (playtest 2026-07-23: Furina's
        // first relic -- her generated basics carried no CanonicalTags).
        // Mirror that predicate exactly: rarity AND tag together.
        foreach (var tag in new[] { CardTag.Strike, CardTag.Defend })
        {
            if (!pool.Any(c => c.Rarity == CardRarity.Basic && c.Tags.Contains(tag)))
            {
                Fail("R11", $"{character.GetType().Name}: no Basic-rarity card tagged "
                          + $"CardTag.{tag} in the pool; LargeCapsule (and anything else "
                          + "keyed on the tag) does an unguarded First() and will throw.");
            }
        }

        // R12. TheArchitect.WinRun() dereferences Dialogue unconditionally,
        // and LoadDialogue draws ONLY from per-character rows
        // (allowAnyCharacterDialogues: false) -- a character with none
        // softlocks the WIN screen (playtest 2026-07-23: Furina beat Act 3
        // and crashed on PROCEED). The rows ship in the PCK's ancients.json
        // and BaseLib merges them at PopulateLocKeys time. At least one must
        // be REPEATING ("r" keys): GetValidDialogues exact-matches
        // VisitIndex == the character's win count and only repeating rows
        // survive its fallback, so a non-repeating-only set works exactly
        // once, then crashes on the second win.
        //
        // The repeating probe reads the loc keys directly, mirroring
        // AncientDialogue.HasRepeatingSuffix: it CANNOT use
        // GetDialoguesForKey(...).Any(d => d.IsRepeating), because BaseLib's
        // lookup only constructs the dialogues -- IsRepeating stays false
        // until the game's own PopulateLines parses the "r" suffix at
        // dialogue-set build time, so that probe fails unconditionally
        // (false positive shipped 2026-07-23, one debug cycle).
        var baseKey = AncientDialogueUtil.BaseLocKey(
            "THE_ARCHITECT", character.Id.Entry);
        var dialogues = AncientDialogueUtil.GetDialoguesForKey(
            "ancients", baseKey);
        if (dialogues.Count == 0)
        {
            Fail("R12", $"{character.GetType().Name}: no THE_ARCHITECT dialogue rows in the "
                      + "ancients table; WinRun() dereferences a null Dialogue and the "
                      + "win-the-run screen softlocks. Rebuild the PCK (ancients.json).");
        }
        else if (!Enumerable.Range(0, dialogues.Count).Any(i =>
                     LocString.Exists("ancients", $"{baseKey}{i}-0r.ancient")
                  || LocString.Exists("ancients", $"{baseKey}{i}-0r.char")))
        {
            Fail("R12", $"{character.GetType().Name}: THE_ARCHITECT dialogues exist but none "
                      + "repeat; GetValidDialogues' visit-index exact match goes empty after "
                      + "the first win and the second win softlocks.");
        }
    }

    private static void CheckCharacterAssets(CharacterModel character)
    {
        // R9. CharacterModel.AssetPaths contains id-derived scenes for combat
        // visuals, the top-panel icon, the energy counter and the card trail.
        // BaseLib can redirect every one, but only when the Custom*Path
        // override is non-null. Furina shipped with texture/creation overrides
        // but not these preload overrides: four failed background loads left
        // AssetCache incomplete and the run crashed while generating the map.
        //
        // Include character-select paths too. This check runs after the mod PCK
        // has merged and never loads/instantiates a resource; Exists is enough
        // to catch a stale local PCK without risking a validator crash.
        var paths = character.AssetPaths
            .Concat(character.AssetPathsCharacterSelect)
            .Where(path => !string.IsNullOrWhiteSpace(path))
            .Distinct(StringComparer.Ordinal);

        foreach (var path in paths)
        {
            if (!ResourceLoader.Exists(path))
            {
                Fail("R9", $"{character.GetType().Name}: required preload asset "
                         + $"\"{path}\" does not resolve. Rebuild the roster PCK "
                         + "before starting a run.");
            }
        }
    }

    // -----------------------------------------------------------------------
    //  Localization
    // -----------------------------------------------------------------------

    private static void CheckLocalization(CharacterModel character)
    {
        var cards = LocManager.Instance.GetTable("cards");
        var characters = LocManager.Instance.GetTable("characters");

        // Union of pool and starting deck: a starter stub can legitimately sit
        // outside the pool, and both surfaces render text.
        var allCards = new List<CardModel>();
        allCards.AddRange(character.CardPool?.AllCards
                          ?? Enumerable.Empty<CardModel>());
        allCards.AddRange(character.StartingDeck
                          ?? Enumerable.Empty<CardModel>());

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
        CheckLocEntry(
            characters, "characters", character.Id.Entry,
            character.GetType().Name, "R5");

        // R8. Every power this mod ships must have loc. R4 only walks the card
        // pool, so powers were unswept -- and the four AuraPowers shipped
        // without ILocalizationProvider, rendering "powers.PYRO_AURA_POWER.title"
        // as a raw tooltip key (playtest 2026-07-20). ModelDb.AllPowers includes
        // mod models; filter to our assembly so we never police base-game text.
        var powersTable = LocManager.Instance.GetTable("powers");
        foreach (var power in ModelDb.AllPowers
                     .Where(p => p.GetType().Assembly == typeof(KleeSelfCheck).Assembly))
        {
            CheckLocEntry(powersTable, "powers", power.Id.Entry, power.GetType().Name, "R8");
        }
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
