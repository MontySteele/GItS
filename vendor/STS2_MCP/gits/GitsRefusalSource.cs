// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-748`. THE ONE REFUSAL ON THE SCREEN THAT NAMES NOTHING.
//
// WHAT THE SEATS SAW (Furina, the Stage, round two, sec.4). A card refused
// under Smoggy arrived on the wire as the bare enum `BlockedByHook`, which
// `understudy/qa_packet.UNPLAYABLE_REASONS` renders as "something else on the
// board is stopping you right now". Two seats flagged it, and the second one
// GUESSED -- correctly, off `Smoggy 1` in the status list, which is luck and
// not a reading. Every other refusal on that page names its cause ("you have
// no Spark, and this costs 1", "no enemy is holding a Bomb", "you do not have
// enough energy"); this one told a reader that something, somewhere, said no.
//
// WHY THE PAGE COULD NOT FIX IT. `understudy/blindplay_faces._hook_note` says
// so in as many words: "`CardModel.CanPlay` reports the flag and has no slot
// for WHICH model refused, so the sentence cannot come off the wire and this
// page must not invent one." That is true of the FLAG. It is not true of the
// call: `CardModel.CanPlay(out UnplayableReason, out ...)` has a second out
// parameter, and `Hook.ShouldPlay` walks every model in the combat with the
// first refusal winning -- the finding written out on
// `klee-mod/KleeCode/Powers/Prototype/SparkAttackCostPower.cs`, "the first
// refusal wins, NAMING THIS POWER AS THE PREVENTER". The bridge was throwing
// that second answer away (`out _`) at both of its two call sites. This file
// reads it instead.
//
// DEFENSIVELY, AND THAT IS DELIBERATE. The second out parameter's static type
// is the game's, it is not documented in `vendor/STS2_MCP/docs/`, and a state
// read must never throw: so nothing here names a game type. The answer is
// boxed to `object?` at the call site and this file asks it, by reflection,
// for a name a player would recognise -- and answers `null`, which keeps the
// wire key ABSENT and the page exactly as it was, whenever it cannot.
//
// READ-ONLY. Nothing here mutates anything. It is a serialiser.

using System;
using System.Reflection;
using System.Text;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>
    /// The properties a game model might carry its player-facing name on, in
    /// the order they are believed. `Title` first because that is the member
    /// the bridge already prints a CARD by (`McpMod.Actions.cs`:
    /// <c>card.Title</c>); `Name` and `DisplayName` after it because the
    /// mod's own models spell it both ways
    /// (<c>FurinaStageLedger.DisplayName</c>).
    /// </summary>
    private static readonly string[] GitsRefusalNameProps =
        { "Title", "DisplayName", "Name" };

    /// <summary>
    /// The player-facing name of whatever refused a card play, or null.
    ///
    /// NULL IS THE COMMON AND SAFE ANSWER: no preventer, a preventer that is a
    /// primitive (the second out parameter is not what this file hopes it is),
    /// or a model with no readable name. On null the caller emits no
    /// `unplayable_reason_text` at all, so the enum beside it and every reader
    /// that already asserts on it are untouched.
    /// </summary>
    internal static string? GitsRefusalSource(object? preventer)
    {
        if (preventer == null) return null;
        var type = preventer.GetType();
        // A bool, an int or a string in this slot means the second out
        // parameter is not the preventer at all. Say nothing rather than
        // print "True is stopping you".
        if (type.IsPrimitive || preventer is string || preventer is Enum)
        {
            return null;
        }
        var name = GitsRefusalName(preventer, type);
        if (string.IsNullOrWhiteSpace(name)) return null;
        return $"{name} is stopping you right now";
    }

    /// <summary>
    /// A model's name: a readable string property if it has one, else its type
    /// name with the framework's suffixes trimmed and its words separated --
    /// `SmoggyPower` reads as `Smoggy`, `TheBoundHeartModel` as
    /// `The Bound Heart`.
    /// </summary>
    private static string? GitsRefusalName(object preventer, Type type)
    {
        foreach (var prop in GitsRefusalNameProps)
        {
            try
            {
                var info = type.GetProperty(
                    prop, BindingFlags.Instance | BindingFlags.Public);
                if (info == null || info.GetIndexParameters().Length > 0)
                {
                    continue;
                }
                if (info.GetValue(preventer) is string value
                    && value.Trim().Length > 0)
                {
                    return value.Trim();
                }
            }
            catch (Exception)
            {
                // A property that throws on read is not a name.
            }
        }
        return GitsRefusalTypeName(type.Name);
    }

    /// <summary>
    /// The fallback: a CLR type name as words. Not a guess about the rule --
    /// it is the class the game itself named the refusal after, which is the
    /// nearest thing to a printed name a reflection reader can honestly
    /// offer.
    /// </summary>
    private static string? GitsRefusalTypeName(string raw)
    {
        foreach (var suffix in new[] { "Power", "PowerModel", "Model",
                                       "Relic", "RelicModel" })
        {
            if (raw.Length > suffix.Length && raw.EndsWith(suffix, StringComparison.Ordinal))
            {
                raw = raw.Substring(0, raw.Length - suffix.Length);
                break;
            }
        }
        if (raw.Length == 0) return null;
        var words = new StringBuilder();
        for (var i = 0; i < raw.Length; i++)
        {
            if (i > 0 && char.IsUpper(raw[i]) && !char.IsUpper(raw[i - 1]))
            {
                words.Append(' ');
            }
            words.Append(raw[i]);
        }
        return words.ToString();
    }
}
