using System;
using System.Collections;
using System.Reflection;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Events;
using MegaCrit.Sts2.Core.Nodes.GodotExtensions;

namespace KleeMod.Story;

/// <summary>
/// A PAGE CHANGE IN THE MIDDLE OF AN EXCHANGE CLOSES IT, not only empties it.
///
/// <c>NEventRoom.RefreshEventState</c> calls
/// <c>NAncientEventLayout.ClearDialogue</c> on every Ancient page change, and
/// <c>ClearDialogue</c> removes the line nodes and empties the line list but
/// leaves the dialogue hitbox and the fake "next" button as the last
/// <c>SetDialogueLineAndAnimate</c> set them. The base game never notices:
/// its Ancients change page only through an option, and an option is only
/// reachable on the last line, where the hitbox is already off. The Spiral
/// Abyss page is an Ancient page whose option can land while a two-line
/// greeting is still on line 0 (the bridge clicks option buttons
/// directly), and then the hitbox stays up over an empty container: the
/// "Respond" button still shows, and the next advance runs
/// <c>SetDialogueLineAndAnimate(1)</c>, whose stale-line loop calls
/// <c>GetChild(0)</c> on no children and throws (live, lane 1, 0.2.5077).
///
/// The fix is the layout's own last-line state, applied only when the clear
/// came mid-exchange: hitbox hidden and disabled, the "next" button hidden,
/// the content container back to its full height. A clear on the last line
/// (every base-game page change) is untouched.
/// </summary>
public static class AncientDialogueClose
{
    /// <summary>Was the exchange still going (a line after this one) when the
    /// layout was cleared? The game's own <c>IsDialogueOnLastLine</c>,
    /// negated: <c>current &gt;= count - 1</c> is the last line.</summary>
    public static bool MidExchange(int currentLine, int lineCount) => currentLine < lineCount - 1;

    public static readonly FieldInfo? DialogueField =
        AccessTools.Field(typeof(NAncientEventLayout), "_dialogue");
    public static readonly FieldInfo? CurrentLineField =
        AccessTools.Field(typeof(NAncientEventLayout), "_currentDialogueLine");
    public static readonly FieldInfo? HitboxField =
        AccessTools.Field(typeof(NAncientEventLayout), "_dialogueHitbox");
    public static readonly FieldInfo? FakeNextField =
        AccessTools.Field(typeof(NAncientEventLayout), "_fakeNextButtonContainer");
    public static readonly FieldInfo? ContentContainerField =
        AccessTools.Field(typeof(NAncientEventLayout), "_contentContainer");
    public static readonly FieldInfo? OriginalHeightField =
        AccessTools.Field(typeof(NAncientEventLayout), "_originalContentContainerHeight");

    internal static bool IsMidExchange(NAncientEventLayout layout)
    {
        if (DialogueField?.GetValue(layout) is not ICollection lines
            || CurrentLineField?.GetValue(layout) is not int current) return false;
        return MidExchange(current, lines.Count);
    }

    /// <summary>The <c>IsDialogueOnLastLine</c> branch of
    /// <c>SetDialogueLineAndAnimate</c>, minus the option buttons (the room
    /// sets the new page's options right after the clear).</summary>
    internal static void Close(NAncientEventLayout layout)
    {
        if (HitboxField?.GetValue(layout) is NClickableControl hitbox)
        {
            hitbox.Visible = false;
            hitbox.Disable();
        }
        if (FakeNextField?.GetValue(layout) is Control fakeNext) fakeNext.Visible = false;
        if (ContentContainerField?.GetValue(layout) is Control content
            && OriginalHeightField?.GetValue(layout) is float height)
        {
            content.Size = new Vector2(content.Size.X, height);
        }
    }
}

[HarmonyPatch(typeof(NAncientEventLayout), nameof(NAncientEventLayout.ClearDialogue))]
internal static class NAncientEventLayout_ClearDialogue_Close_Patch
{
    [HarmonyPrefix]
    private static void Prefix(NAncientEventLayout __instance, out bool __state)
    {
        __state = false;
        try
        {
            __state = AncientDialogueClose.IsMidExchange(__instance);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: could not read the Ancient dialogue before a clear: {e.Message}");
        }
    }

    [HarmonyPostfix]
    private static void Postfix(NAncientEventLayout __instance, bool __state)
    {
        if (!__state) return;
        try
        {
            AncientDialogueClose.Close(__instance);
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] story: could not close the cleared Ancient dialogue: {e.Message}");
        }
    }
}
