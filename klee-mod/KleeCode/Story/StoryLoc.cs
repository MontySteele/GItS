using System;
using System.Collections.Generic;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Logging;

namespace KleeMod.Story;

/// <summary>
/// THE STORY'S LOC ROWS, merged at boot beside the card rows
/// (<c>LocManager_Initialize_Patch</c>, once the tables exist): the events'
/// pages into <c>events</c>, the Ancient exchanges into <c>ancients</c>, and
/// the spoken lines into <c>characters</c> under the speaker's entry. Every
/// row is built from the story tables; none is written here.
/// </summary>
public static class StoryLoc
{
    /// <summary>The <c>characters</c> rows: each table's combat lines and
    /// pair exchanges.</summary>
    public static Dictionary<string, string> LineRows()
    {
        var rows = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var story in StoryRegistry.All)
        {
            var own = StoryRegistry.EntryOf(story.Character);
            // No combat lines (Kokomi's, an open pick): no rows.
            if (story.Lines is CombatLines l)
            {
                rows[StoryLines.Key(own, StoryLines.BossEntry)] = l.BossEntry;
                rows[StoryLines.Key(own, StoryLines.LowHp)] = l.LowHp;
                rows[StoryLines.Key(own, StoryLines.Signature)] = l.Signature;
                rows[StoryLines.Key(own, StoryLines.BossKill)] = l.BossKill;
                rows[StoryLines.Key(own, StoryLines.RunLoss)] = l.RunLoss;
                rows[StoryLines.Key(own, StoryLines.RunWin)] = l.RunWin;
            }
            foreach (var p in story.Pairs)
            {
                var partner = StoryRegistry.EntryOf(p.Partner);
                rows[StoryLines.PairKey(own, partner, partnerSpeaks: true)] = p.PartnerLine;
                rows[StoryLines.PairKey(own, partner, partnerSpeaks: false)] = p.OwnLine;
            }
        }
        return rows;
    }

    /// <summary>The <c>events</c> rows for every story event.</summary>
    public static Dictionary<string, string> EventRows()
    {
        var rows = new Dictionary<string, string>(StringComparer.Ordinal);
        foreach (var story in StoryRegistry.All)
        {
            foreach (var e in story.Events)
            {
                foreach (var (k, v) in StoryEventModel.Rows(e, StoryRegistry.EntryOf(e.EventType)))
                {
                    rows[k] = v;
                }
            }
        }
        // The co-op story room's own rows: its placeholder page.
        foreach (var (k, v) in StoryEventModel.Rows(
                     StoryCoop.QuietLanding, StoryRegistry.EntryOf(typeof(StoryCoopRoomEvent))))
        {
            rows[k] = v;
        }
        return rows;
    }

    /// <summary>Merge every row. One failure costs the story its text, never
    /// the mod its boot.</summary>
    public static void Inject()
    {
        try
        {
            EnglishLoc.Table(StoryLines.Table).MergeWith(LineRows());
            EnglishLoc.Table(StoryEventModel.Table).MergeWith(EventRows());
            // The "next" buttons are copied from the base game's own, so a
            // non-English table gets its own language's copy.
            EnglishLoc.MergeDerived(StoryAncients.Table,
                table => StoryAncients.Rows(a => StoryAncients.NextButtonFrom(table, a)));
        }
        catch (Exception e)
        {
            Log.Error($"[{KleeMod.ModId}] story: loc merge failed, story text will render as raw keys: {e}");
        }
    }
}
