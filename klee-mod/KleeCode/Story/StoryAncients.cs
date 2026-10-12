using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.Ancients;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Story;

/// <summary>
/// THE ANCIENTS GREET HER (batch 1 sec.2): one exchange per Ancient, on her
/// first visit.
///
/// THE GAME'S OWN SEAM. <c>AncientDialogueSet.CharacterDialogues</c> is keyed
/// by a character's <c>Id.Entry</c>, and the five base characters are the
/// only keys an Ancient defines, so a modded character misses
/// <c>TryGetValue</c> and falls through to <c>AgnosticDialogues</c>
/// (<c>AncientDialogueSet.GetValidDialogues</c>). This adds an entry for each
/// story character with a line for that Ancient, once per built set, right
/// after <c>AncientEventModel.DialogueSet</c> builds it; every other
/// character keeps the agnostic set exactly as before.
///
/// "THE FIRST VISIT" IS THE GAME'S FIRST VISIT. The dialogue carries
/// <c>VisitIndex = 0</c>, which the game matches against this profile's
/// visits to that Ancient AS this character
/// (<c>AncientStats.GetVisitsAs</c>, counted at each run's end). So it plays
/// on Klee's first meeting with each Ancient, exactly as a base character's
/// first-visit line does, and never again on that profile. Two consequences
/// the live check owes: a profile that has already met an Ancient as Klee
/// does not see that Ancient's line, and the game's own once-ever
/// introduction (<c>FirstVisitEverDialogue</c>, any character's very first
/// meeting with that Ancient) still comes first, as it does for the base five.
///
/// COMPOSES WITH THE SPIRAL ABYSS PAGE. The Abyss page replaces the
/// Ancient's DESCRIPTION and OPTIONS (<c>AbyssChoicePage</c>, after
/// <c>SetInitialEventState</c>); the dialogue is the room's separate layer,
/// set by <c>NEventRoom.SetupLayout</c> from this set. The two touch nothing
/// in common, so the greeting plays over whichever page is up.
/// </summary>
public static class StoryAncients
{
    internal const string Table = "ancients";

    /// <summary>The game's key stem for a dialogue line:
    /// <c>NEOW.talk.KLEEMOD-KLEE.0-1</c>.</summary>
    public static string LineKey(string ancientEntry, string characterEntry, int line) =>
        $"{ancientEntry}.talk.{characterEntry}.0-{line}";

    /// <summary>
    /// Add every story character's dialogue for this Ancient to the set, as a
    /// two-line exchange (the Ancient, then her) on her first visit. Returns
    /// the character keys it added. With <paramref name="populate"/> the lines
    /// are given their loc keys the way the game's own
    /// <c>PopulateLocKeys</c> gives them (which needs the loc tables up).
    /// </summary>
    public static List<string> AddTo(
        AncientDialogueSet set, string ancientEntry, bool populate,
        Func<Type, string>? entryOf = null)
    {
        entryOf ??= StoryRegistry.EntryOf;
        var added = new List<string>();
        foreach (var story in StoryRegistry.All)
        {
            if (!story.Ancients.Any(a => a.AncientEntry == ancientEntry)) continue;
            var characterEntry = entryOf(story.Character);
            if (set.CharacterDialogues.ContainsKey(characterEntry)) continue;

            var dialogue = new AncientDialogue("", "") { VisitIndex = 0 };
            if (populate)
            {
                dialogue.PopulateLines(ancientEntry, characterEntry, 0);
                // The game sets every line's "next" button in PopulateLocKeys,
                // which ran before this entry existed.
                dialogue.Lines[0].NextButtonText =
                    new LocString(Table, LineKey(ancientEntry, characterEntry, 0) + ".next");
            }
            set.CharacterDialogues[characterEntry] = new[] { dialogue };
            added.Add(characterEntry);
        }
        return added;
    }

    /// <summary>
    /// The <c>ancients</c> rows: the Ancient's line, her answer, and the
    /// "next" button between them. THE BUTTON'S WORD IS THE GAME'S: it is
    /// copied from that Ancient's own two-line exchanges of the same shape
    /// (an Ancient line followed by a character line), so no word on it is
    /// ours.
    /// </summary>
    public static Dictionary<string, string> Rows(Func<string, string?> nextButtonFor)
    {
        var rows = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var story in StoryRegistry.All)
        {
            var characterEntry = StoryRegistry.EntryOf(story.Character);
            foreach (var a in story.Ancients)
            {
                rows[LineKey(a.AncientEntry, characterEntry, 0) + ".ancient"] = a.AncientLine;
                rows[LineKey(a.AncientEntry, characterEntry, 1) + ".char"] = a.CharacterLine;
                var next = nextButtonFor(a.AncientEntry);
                if (next != null)
                {
                    rows[LineKey(a.AncientEntry, characterEntry, 0) + ".next"] = next;
                }
            }
        }
        return rows;
    }

    /// <summary>
    /// The base game's own "next" word for an Ancient: the first of its
    /// dialogues whose line 0 is the Ancient's and whose line 1 is the
    /// character's, else any of its line-0 buttons.
    /// </summary>
    internal static string? NextButtonFrom(LocTable table, string ancientEntry)
    {
        var talk = table.GetLocStringsWithPrefix(ancientEntry + ".talk.");
        var keys = talk.Select(s => s.LocEntryKey).ToHashSet(StringComparer.Ordinal);
        string? fallback = null;
        foreach (var s in talk)
        {
            var key = s.LocEntryKey;
            if (!key.EndsWith("-0.next", StringComparison.Ordinal)
                && !key.EndsWith("-0r.next", StringComparison.Ordinal)) continue;
            var stem = key[..key.LastIndexOf('.')];
            var repeat = stem.EndsWith("r", StringComparison.Ordinal) ? "r" : "";
            var lineOne = stem[..(stem.Length - repeat.Length - 1)] + "1" + repeat;
            fallback ??= s.GetRawText();
            if (keys.Contains(stem + ".ancient") && keys.Contains(lineOne + ".char"))
            {
                return s.GetRawText();
            }
        }
        return fallback;
    }
}

/// <summary>The install seam: once per built set, after the game builds it.</summary>
[HarmonyPatch(typeof(AncientEventModel), nameof(AncientEventModel.DialogueSet), MethodType.Getter)]
internal static class AncientEventModel_DialogueSet_Story_Patch
{
    private static readonly ConditionalWeakTable<AncientDialogueSet, object> Done = new();

    [HarmonyPostfix]
    private static void Postfix(AncientEventModel __instance, AncientDialogueSet __result)
    {
        if (__result == null || Done.TryGetValue(__result, out _)) return;
        Done.Add(__result, new object());
        try
        {
            StoryAncients.AddTo(__result, __instance.Id.Entry, populate: true);
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] story: Ancient greeting for {__instance.Id.Entry} failed: {e}");
        }
    }
}
