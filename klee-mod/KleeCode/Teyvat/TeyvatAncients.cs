using System;
using System.Collections.Generic;
using MegaCrit.Sts2.Core.Localization;

namespace KleeMod.Teyvat;

/// <summary>
/// THE DRESSED ANCIENTS' LOC ROWS, built against the LIVE `ancients` table
/// (R275, 2026-09-17). `TeyvatLoc.Inject` merges what this returns; the split
/// is so the whole derivation is a pure function of a table and can be pinned
/// headlessly against a fake one.
///
/// AN EMPTY FIELD IN THE FACES FILE MEANS "KEEP THE GAME'S OWN LINE", and this
/// method is the only place that promise is kept. It cannot be kept
/// statically. A dressed Ancient is a SUBCLASS, `Id.Entry` is its class name
/// slugified (`ModelDb.GetEntry`), and every string the engine builds for an
/// Ancient hangs off that entry:
///
///   `EventModel.Title`                      `Id.Entry + ".title"`
///   `AncientEventModel.Epithet`             `Id.Entry + ".epithet"`
///   `AncientEventModel.DialogueSet`         `PopulateLocKeys(Id.Entry)`, which
///                                           is `<entry>.talk.<char>.<X>-<Y>[r]`
///                                           `.ancient` / `.char` / `.next`
///   `AncientEventModel.Done`                `Id.Entry + ".pages.DONE.description"`
///
/// none of them `virtual`. So a dressed Ancient re-keys its ENTIRE text
/// surface, and without this pass it would render raw keys for everything the
/// face did not write.
///
/// PASS ONE IS THE ALIAS. Every live row under `<BASE>.` is copied to
/// `<DRESSED>.` with the same suffix. That is the game's own words, read out
/// of the pack at boot in whatever language is loaded -- so no base-game prose
/// is in this repo (`.gitignore:28`, `csharp-build-spec.md` sec.0.3), no face
/// owes a translation, and a name-only pass ships intact.
///
/// AND IT IS WHY THE BOONS STAY THE GAME'S. An Ancient's options are
/// `RelicOption&lt;T&gt;()`, and `EventOption.FromRelic` is
/// `eventModel.GetOptionTitle(textKey) ?? relic.Title` --
/// `LocString.GetIfExists`, so an absent row falls through to the RELIC's own
/// rows. The generator writes no option row ever, and the alias copies
/// whatever option rows the base entry has, so a dressed Ancient's boon reads
/// exactly as an undressed one's, from the same source.
///
/// PASS TWO IS THE FACE'S OWN ROWS, laid over the alias. Flat rows are a
/// dictionary. Dialogue lines are not, because a line's key carries an `r`
/// when its dialogue is in the repeating pool and that fact lives in the PACK,
/// not in any C# this repo reads: the stem is resolved here by asking the live
/// table which of the two spellings it has. The line's SPEAKER suffix is the
/// face's -- `AncientDialogue.PopulateLines` picks `.ancient` over `.char` by
/// existence -- so when a face moves a line from one speaker to the other, the
/// alias's copy of the OTHER suffix is dropped. Leaving both would let the
/// engine read the stale one.
///
/// Both passes are nearly empty work today: R275 ships names, so pass two
/// writes one `.title` per body and nothing else.
/// </summary>
public static class TeyvatAncients
{
    /// <inheritdoc cref="TeyvatAncients"/>
    public static Dictionary<string, string> RowsFor(LocTable table)
    {
        var rows = new Dictionary<string, string>(StringComparer.Ordinal);
        if (table == null)
        {
            return rows;
        }

        // Pass one -- the alias. `GetLocStringsWithPrefix` unions the table's
        // own keys with its FALLBACK's, which matters in every language but
        // English: a row the translation has not reached is served from the
        // English table, and a dressing must borrow it from the same place.
        foreach (var (dressed, baseEntry) in TeyvatGeneratedAncients.BaseEntries)
        {
            var prefix = baseEntry + ".";
            foreach (var loc in table.GetLocStringsWithPrefix(prefix))
            {
                var key = loc.LocEntryKey;
                rows[dressed + "." + key.Substring(prefix.Length)] =
                    table.GetRawText(key);
            }
        }

        // Pass two -- the face's dialogue lines, which may displace an alias.
        foreach (var line in TeyvatGeneratedAncients.Lines)
        {
            var baseEntry = TeyvatGeneratedAncients.BaseEntries[line.DressedEntry];
            var tail = $".talk.{line.CharEntry}."
                     + $"{line.DialogueIndex}-{line.LineIndex}";
            var repeating = table.HasEntry(baseEntry + tail + "r.ancient")
                         || table.HasEntry(baseEntry + tail + "r.char");
            var stem = line.DressedEntry + tail + (repeating ? "r" : "");

            rows.Remove(stem + ".ancient");
            rows.Remove(stem + ".char");
            rows[stem + (line.AncientSpeaks ? ".ancient" : ".char")] = line.Text;
        }

        // Pass two -- the flat rows: the name, the epithet, the `extra` keys.
        foreach (var (key, value) in TeyvatGeneratedAncients.Rows)
        {
            rows[key] = value;
        }

        return rows;
    }
}
