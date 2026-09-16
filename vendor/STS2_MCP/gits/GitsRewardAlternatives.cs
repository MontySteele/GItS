// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// `EB-374`. THE REWARD SCREEN'S OTHER BUTTON HAD NO WORDS ON THE WIRE.
//
// THE FIND (Klee r9, act 2). Pael's Wing adds a SACRIFICE option to the card
// reward screen, and two card rewards in that run printed `choose` and `skip`
// and nothing else -- the seat was holding a relic whose whole rule is that
// button and never saw it. The page half is built: the reward state carries
// the cards and one boolean, and the page names the held relic and says the
// control is not on its feed. This is the wire half that lets that caveat
// come off.
//
// WHAT THE GAME HAS, AND IT IS A SENTENCE. `NCardRewardAlternativeButton`'s
// own summary (decompiled, sts2.dll 0.111.0 `41cef1ea`) reads: "a button that
// sits below the card reward screen that presents alternatives to picking
// cards. The most common is Skip, but some relics dynamically add other
// options such as Pael's Wing." It is built by
// `Create(string optionName, string[] hotkeys)`, which stashes the words in a
// private `_optionName` and, at `_Ready`, pushes them into a `MegaLabel` child
// named `Label`. So the words exist on every such button and the bridge was
// counting the buttons and throwing their names away
// (`state["can_skip"] = altButtons.Count > 0`).
//
// TWO READS, IN THIS ORDER, AND BOTH ARE THE SAME STRING. `_optionName` is
// what `Create` was given and is set before the node enters the tree, so it
// answers on a button this bridge polls early; the `Label` node's own text is
// what a sighted player is reading and is the belt. `McpMod.StateBuilder.cs`
// supplies the second as a callback, because a Godot node read belongs at the
// call site and nothing in this file names a game type
// (`GitsSettledHp.cs`'s rule, and `GitsRefusalSource.cs`'s reason: the field
// is undocumented and a state read must never throw).
//
// THE VERB IS THE OTHER HALF AND IT IS IN `McpMod.Actions.cs`.
// `ExecuteSkipCardReward` pressed `altButtons[0]` unconditionally, so a
// screen with two alternatives could only ever be told to press the first
// one and a page naming both would be lying about what it could do. The
// action takes an index now, and the page's `sacrifice` verb sends the index
// of the button whose words are not the plain skip.
//
// READ-ONLY. Nothing here presses anything. It is a serialiser.

using System;
using System.Reflection;

namespace STS2_MCP;

public static partial class McpMod
{
    /// <summary>The wire key the alternative buttons are published under on
    /// the card reward screen. Always emitted there, so a MISSING key means
    /// "bridge predates `EB-374`" and an EMPTY list means "this screen offers
    /// no alternative at all" -- which are different facts, and the second is
    /// the one `can_skip: false` already stated.</summary>
    internal const string GitsAlternativesKey = "alternatives";

    /// <summary>The words the game itself calls a plain skip. Compared folded,
    /// and used by nothing here -- it is the page that decides what to do with
    /// a button that is not this one. Spelled here because the bridge and the
    /// page have to agree on the string.</summary>
    internal const string GitsPlainSkipWord = "skip";

    private static FieldInfo? _gitsOptionNameField;
    private static bool _gitsOptionNameProbed;

    /// <summary>
    /// One alternative button's printed words, or null.
    ///
    /// NULL IS THE SAFE ANSWER: a button whose words cannot be read is
    /// published with no `name`, and the page prints what it always printed --
    /// that there is a control here and the feed does not say what it does.
    /// </summary>
    /// <param name="button">The `NCardRewardAlternativeButton`, boxed.</param>
    /// <param name="labelText">The call site's read of the button's `Label`
    /// child, which is the words a sighted player has in front of them. Used
    /// when the private field answers nothing.</param>
    internal static string? GitsAlternativeName(object? button,
                                                Func<string?> labelText)
    {
        var fromField = GitsOptionName(button);
        if (!string.IsNullOrWhiteSpace(fromField)) return fromField!.Trim();
        try
        {
            var text = labelText();
            if (!string.IsNullOrWhiteSpace(text)) return text!.Trim();
        }
        catch (Exception)
        {
            // A label that throws on read is not a name.
        }
        return null;
    }

    /// <summary>The words `Create` was handed, by reflection, or null.
    /// Probed once and cached including the null, `GitsCardGrid.cs`'s bargain.
    /// </summary>
    private static string? GitsOptionName(object? button)
    {
        if (button == null) return null;
        try
        {
            if (!_gitsOptionNameProbed)
            {
                _gitsOptionNameProbed = true;
                _gitsOptionNameField = button.GetType().GetField(
                    "_optionName",
                    BindingFlags.Instance | BindingFlags.NonPublic
                    | BindingFlags.Public);
            }
            return _gitsOptionNameField?.GetValue(button) as string;
        }
        catch (Exception)
        {
            return null;
        }
    }
}
