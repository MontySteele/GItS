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
/// BASELIB GETS THERE FIRST, AND LOSES. BaseLib 3.4.x prefixes
/// <c>AncientDialogueSet.PopulateLocKeys</c> (<c>AddAncientDialogues</c>) and
/// registers, for every <c>CustomCharacterModel</c>, the dialogues it finds
/// under <c>&lt;ANCIENT&gt;.talk.&lt;CHAR&gt;.N-*</c>: our rows. Its entry is
/// <c>VisitIndex = 0</c> and not repeating, so it plays on her first visit
/// only, and the stock repeating line wins every visit after (seen live on
/// 0.2.5073). This postfix runs after <c>PopulateLocKeys</c>, so it is always
/// last to touch the built set, and it replaces that entry with ours: one
/// owner, whichever mod registered first and whatever BaseLib version.
///
/// EVERY VISIT, NOT ONLY THE FIRST (coordinator, 2026-10-12: the owner's
/// profile has already met these Ancients as Klee, and the game's per-profile
/// first visit would never show them). The dialogue is repeating with no
/// visit index, and <see cref="Ancient_GetValidDialogues_Story_Patch"/> hands
/// it back on every visit (<see cref="StoryDialogueFor"/>) ahead of the
/// agnostic and repeating pools. The game's own once-ever introduction
/// (<c>FirstVisitEverDialogue</c>, anyone's very first meeting with that
/// Ancient on the profile) still comes first, as it does for the base five.
///
/// COMPOSES WITH THE SPIRAL ABYSS PAGE. The Abyss page replaces the
/// Ancient's DESCRIPTION and OPTIONS (<c>AbyssChoicePage</c>, after
/// <c>SetInitialEventState</c>); the dialogue is the room's separate layer,
/// set by <c>NEventRoom.SetupLayout</c> from this set. Since the Blessing
/// screen (2026-10-12, <c>AbyssOverlay</c>) the greeting is held while the
/// Abyss page is up and plays after the screen closes, over the Ancient's own
/// page, as in a normal run.
/// </summary>
public static class StoryAncients
{
    internal const string Table = "ancients";

    /// <summary>The game's key stem for a dialogue line:
    /// <c>NEOW.talk.KLEEMOD-KLEE.0-1</c>.</summary>
    public static string LineKey(string ancientEntry, string characterEntry, int line) =>
        $"{ancientEntry}.talk.{characterEntry}.0-{line}";

    /// <summary>
    /// Put every story character's dialogue for this Ancient in the set, as a
    /// two-line exchange (the Ancient, then her) on every visit, replacing
    /// any entry already there for her (BaseLib's, from the same rows). Returns
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
            // ONE OWNER OF THE ENTRY. BaseLib's PopulateLocKeys prefix
            // (AddAncientDialogues) scans the same `<ANCIENT>.talk.<CHAR>.0-*`
            // rows and registers its own entry for every CustomCharacterModel
            // before this postfix runs: a first-visit-only dialogue
            // (VisitIndex 0, not repeating), so a profile that has met the
            // Ancient as her never sees it again. Ours replaces whatever is
            // there; the rows are ours, so nothing of anyone else's is lost.
            if (set.CharacterDialogues.TryGetValue(characterEntry, out var existing)
                && existing.Any(d => Added.TryGetValue(d, out _))) continue;

            var dialogue = new AncientDialogue("", "") { VisitIndex = null, IsRepeating = true };
            if (populate)
            {
                dialogue.PopulateLines(ancientEntry, characterEntry, 0);
                // The game sets every line's "next" button in PopulateLocKeys,
                // which ran before this entry existed.
                dialogue.Lines[0].NextButtonText =
                    new LocString(Table, LineKey(ancientEntry, characterEntry, 0) + ".next");
            }
            Added.AddOrUpdate(dialogue, new object());
            set.CharacterDialogues[characterEntry] = new[] { dialogue };
            added.Add(characterEntry);
        }
        return added;
    }

    /// <summary>
    /// The story dialogue the game should show this visit, or null to let the
    /// game choose: hers on every visit, except the once-ever introduction
    /// (the same first test <c>GetValidDialogues</c> makes).
    /// </summary>
    public static AncientDialogue? StoryDialogueFor(
        AncientDialogueSet set, string characterEntry, int totalVisits)
    {
        if (totalVisits == 0 && set.FirstVisitEverDialogue != null) return null;
        if (!set.CharacterDialogues.TryGetValue(characterEntry, out var own)) return null;
        return own.FirstOrDefault(d => Added.TryGetValue(d, out _));
    }

    /// <summary>The dialogues this class added, so a base character's own
    /// repeating lines are never mistaken for a story line.</summary>
    internal static readonly ConditionalWeakTable<AncientDialogue, object> Added = new();

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
            // Read off THIS table, not the live manager's: the English pass
            // and the local pass each copy their own language's word.
            fallback ??= table.GetRawText(key);
            if (keys.Contains(stem + ".ancient") && keys.Contains(lineOne + ".char"))
            {
                return table.GetRawText(key);
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

/// <summary>
/// EVERY VISIT: a story character's own exchange is the answer whenever the
/// set holds one for her, after the game's once-ever introduction. Anyone
/// else gets the game's own choice, untouched.
/// </summary>
[HarmonyPatch(typeof(AncientDialogueSet), nameof(AncientDialogueSet.GetValidDialogues))]
internal static class Ancient_GetValidDialogues_Story_Patch
{
    [HarmonyPrefix]
    private static bool Prefix(AncientDialogueSet __instance, ModelId characterId, int totalVisits,
                               ref IEnumerable<AncientDialogue> __result)
    {
        try
        {
            var own = StoryAncients.StoryDialogueFor(__instance, characterId.Entry, totalVisits);
            if (own == null) return true;
            __result = new[] { own };
            return false;
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: greeting lookup fell back to the game's: {e.Message}");
            return true;
        }
    }
}
