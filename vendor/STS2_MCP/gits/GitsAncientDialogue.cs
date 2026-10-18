// GItS LOCAL ADDITION - not upstream STS2MCP.
//
// AN ANCIENT'S GREETING, AS TEXT (seat page backlog, 2026-10-18).
//
// The event state said only `in_dialogue: true` while an Ancient's lines
// played, so the blind page printed "(the scene is still being told)" and a
// seat never read the story. The lines are on screen: `NAncientEventLayout`
// adds one `NAncientDialogueLine` per line to its `%DialogueContainer`, and
// each line's `_Ready` writes its formatted text into its own `%Text` label
// (the character's details and the Ancient's vars already folded in, the
// game's own `GetFormattedText`). `_currentDialogueLine` is how far the
// player has clicked, so the lines up to and including it are the ones
// shown.
//
// PRIVATE FIELDS, READ BY NAME AND GUARDED. The layout keeps both behind
// private fields (decompiled `NAncientEventLayout`: `_dialogueContainer`,
// `_currentDialogueLine`; `NAncientDialogueLine._line`). A read that throws or
// finds nothing answers null and the key stays absent, which is the page's
// old behaviour.

using System;
using System.Collections.Generic;
using System.Reflection;
using Godot;
using MegaCrit.Sts2.Core.Entities.Ancients;
using MegaCrit.Sts2.Core.Nodes.Events;

namespace STS2_MCP;

public static class GitsAncientDialogue
{
    /// <summary>The wire key, inside the event state.</summary>
    public const string Key = "dialogue";

    /// <summary>What a line's `speaker` says for the Ancient and for the
    /// player's character.</summary>
    public const string SpeakerAncient = "ancient";

    public const string SpeakerYou = "you";

    private const BindingFlags Private =
        BindingFlags.Instance | BindingFlags.NonPublic;

    /// <summary>The lines shown so far, oldest first, each
    /// <c>{speaker, text}</c>; null where there are none or the read
    /// failed.</summary>
    public static List<Dictionary<string, object?>>? Lines(
        NAncientEventLayout? layout)
    {
        if (layout == null) return null;
        try
        {
            var type = typeof(NAncientEventLayout);
            if (type.GetField("_dialogueContainer", Private)?.GetValue(layout)
                is not Node container)
            {
                return null;
            }
            var current = type.GetField("_currentDialogueLine", Private)
                ?.GetValue(layout) is int at ? at : 0;
            var lineField = typeof(NAncientDialogueLine).GetField("_line", Private);
            var lines = new List<Dictionary<string, object?>>();
            var count = container.GetChildCount();
            for (var i = 0; i < count && i <= current; i++)
            {
                if (container.GetChild(i) is not NAncientDialogueLine node) continue;
                var label = node.GetNodeOrNull<RichTextLabel>("%Text");
                var text = GitsEventBody.Plain(label?.Text);
                if (text == null) continue;
                var speaker = lineField?.GetValue(node) is AncientDialogueLine data
                              && data.Speaker == AncientDialogueSpeaker.Character
                    ? SpeakerYou
                    : SpeakerAncient;
                lines.Add(new Dictionary<string, object?>
                {
                    ["speaker"] = speaker,
                    ["text"] = text,
                });
            }
            return lines.Count > 0 ? lines : null;
        }
        catch (Exception)
        {
            return null;
        }
    }
}
