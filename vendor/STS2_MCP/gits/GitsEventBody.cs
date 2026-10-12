// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// THE EVENT'S PARAGRAPH, AS PLAIN TEXT (2026-10-12).
//
// THE FIND. `BuildEventState` read `body` off the room's CANONICAL event, and
// the canonical event never has a page set: `EventModel.Description` is
// assigned only by `SetEventState`, which asserts a MUTABLE model. So every
// event answered `"body": null`, and no seat ever read an event's story text
// (Starsnatch Cliff's paragraph, every base event's). #1155 patched the Spiral
// Abyss choice page alone; this is the general read.
//
// THE READ IS THE GAME'S OWN. `NEventRoom.SetDescription` shows the room's
// model's `Description`, dressed with the character's details,
// `IsMultiplayer` and the event's `DynamicVars`, as `GetFormattedText()`.
// `gits/GitsEventPage.cs` makes that same read off the player's local copy
// (`EventRoom.LocalMutableEvent`, guarded by `GitsLocalEvent.OrNothing`), then
// the canonical event as a fallback, and hands the formatted strings here.
//
// THIS FILE NAMES NO GAME TYPE, so `KleeTests` compiles it and pins the two
// rules with event-shaped strings: the first page that has text wins, and the
// text is plain (BBCode tags gone, an [img] reduced to its file name the way
// `StripRichTextTags` does, paragraphs kept, nothing else rewritten). A read
// that throws counts as no text: a state read must never throw
// (`GitsRefusalSource.cs`).

using System;
using System.Text;
using System.Text.RegularExpressions;

namespace STS2_MCP;

public static class GitsEventBody
{
    /// <summary>The first read that yields text, as plain text; null when
    /// none does. Each read is guarded.</summary>
    public static string? Choose(params Func<string?>[] reads)
    {
        foreach (var read in reads)
        {
            string? formatted;
            try { formatted = read(); }
            catch (Exception) { continue; }
            var plain = Plain(formatted);
            if (plain != null) return plain;
        }
        return null;
    }

    private static readonly Regex Img = new(
        @"\[img(?:[^\]\[]*)\]([^\[]*)\[/img\]", RegexOptions.Compiled);

    // A BBCode tag: `[b]`, `[/color]`, `[color=#ff0]`, `[font_size=20]`,
    // `[url=res://x]`. A bracket that does not open with a tag name stays.
    private static readonly Regex Tag = new(
        @"\[/?[A-Za-z_][A-Za-z0-9_]*(?:[= ][^\[\]\n]*)?\]", RegexOptions.Compiled);

    private static readonly Regex Blank = new(@"\n{3,}", RegexOptions.Compiled);

    /// <summary>Formatted page text to plain text: tags stripped, line ends
    /// normalised, trailing space and runs of blank lines trimmed. Null for
    /// null or blank.</summary>
    public static string? Plain(string? formatted)
    {
        if (string.IsNullOrWhiteSpace(formatted)) return null;
        var text = formatted.Replace("\r\n", "\n").Replace('\r', '\n');
        text = Img.Replace(text, m =>
        {
            var path = m.Groups[1].Value;
            var slash = path.LastIndexOf('/');
            return "[" + (slash >= 0 ? path[(slash + 1)..] : path) + "]";
        });
        text = Tag.Replace(text, "");
        var sb = new StringBuilder();
        foreach (var line in text.Split('\n'))
        {
            if (sb.Length > 0) sb.Append('\n');
            sb.Append(line.TrimEnd());
        }
        text = Blank.Replace(sb.ToString(), "\n\n").Trim();
        return text.Length == 0 ? null : text;
    }
}
