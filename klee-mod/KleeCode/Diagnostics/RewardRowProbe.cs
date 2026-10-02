using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using Godot;
using HarmonyLib;
using MegaCrit.Sts2.Core.Entities.CardRewardAlternatives;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Cards.Holders;
using MegaCrit.Sts2.Core.Nodes.Screens.CardSelection;

namespace KleeMod.Diagnostics;

/// <summary>
/// THE CARD REWARD ROW, MEASURED. An instrument, not a fix.
///
/// The report ([USER], co-op run, 2026-10-02): "In card rewards, sometimes one
/// of the rewards is offscreen but can be controller selected over to and
/// selected anyway."
///
/// WHAT THE DECOMPILE SAYS, and why it does not explain the report on its own.
/// <c>NCardRewardSelectionScreen.RefreshOptions</c> lays the cards out at a
/// fixed 350 px apart, centred on <c>UI/CardRow</c> (anchored at the screen
/// centre): card i goes to x = (i - (n - 1) / 2) * 350. A card is 300 px wide
/// at hover scale and 240 px at the row's 0.8 scale. The canvas size depends
/// on the window's shape, not its resolution (<c>NGlobalUi.OnWindowChange</c>,
/// Auto aspect: 1680x1080 expanded between 4:3 and 21:9, 1260 tall below 4:3,
/// 2580 wide above 21:9), so it is 1920 px wide at 16:9 whether the screen is
/// 1280x720, 1920x1080 or 3840x2160. So four cards span 1350 px and five
/// span 1700 px: both fit at 16:9, and the row first runs off a 16:9 screen at
/// six cards. The mod's companion slot makes a fight reward four cards (three
/// plus one), and the user's 2026-10-02 log shows four on every reward. The row
/// arithmetic therefore cannot put a card off screen in that run, and the
/// cause is something the decompile does not show -- for example a card node
/// that is not where its holder is, or a holder that was not placed.
///
/// WHAT THIS DOES. After the row's own 0.5 s placement tween has finished, it
/// measures every card holder on the screen against the visible canvas and
/// writes ONE line to godot.log: how many options, how many holders, the
/// canvas size, and for each holder its centre, its card body's rect and
/// whether that rect is on screen, partly off, wholly off, or not drawn. A
/// row that is fully on screen is an INFO line; any card that is not is a
/// WARN line that starts "reward row OFF SCREEN". The next time the user sees
/// it, that line names which of the readings above it was.
///
/// It reads and never writes: no position, scale or focus is touched, so the
/// three-card base look is untouched by construction. Every step is inside
/// a try/catch, so a failed reading costs a log line and never the screen.
/// </summary>
internal static class RewardRowProbe
{
    /// <summary>The row's placement tween is 0.5 s; read just after it.</summary>
    internal const double SettleSeconds = 0.75;

    /// <summary>Where a card sits relative to the visible canvas.</summary>
    internal enum Placement
    {
        OnScreen,
        PartlyOff,
        OffScreen,
        NotDrawn,
    }

    /// <summary>
    /// The whole judgement, kept free of nodes so it can be tested without
    /// Godot. A card is NOT DRAWN when it is hidden or has no area (the fly
    /// animation shrinks a card's body to zero). Otherwise it is ON SCREEN when
    /// the canvas wholly contains it, OFF SCREEN when the two do not overlap at
    /// all, and PARTLY OFF in between. A one-pixel tolerance keeps a card that
    /// touches the edge exactly from reading as off.
    /// </summary>
    internal static Placement Classify(Rect2 view, Rect2 card, bool visible)
    {
        if (!visible || !(card.Size.X > 0f) || !(card.Size.Y > 0f))
        {
            return Placement.NotDrawn;
        }
        var grown = view.Grow(1f);
        if (grown.Encloses(card))
        {
            return Placement.OnScreen;
        }
        return grown.Intersects(card) ? Placement.PartlyOff : Placement.OffScreen;
    }

    /// <summary>
    /// The base game's own target for card <paramref name="index"/> of
    /// <paramref name="count"/>, relative to the row's centre. Kept here so the
    /// log can print where each card SHOULD be beside where it is.
    /// </summary>
    internal static float ExpectedX(int index, int count) =>
        (index - (count - 1) * 0.5f) * 350f;

    internal static void Schedule(NCardRewardSelectionScreen screen, int optionCount)
    {
        try
        {
            if (!screen.IsInsideTree())
            {
                return;
            }
            screen.GetTree().CreateTimer(SettleSeconds).Timeout += () =>
            {
                try
                {
                    if (GodotObject.IsInstanceValid(screen) && screen.IsInsideTree())
                    {
                        Report(screen, optionCount);
                    }
                }
                catch (Exception e)
                {
                    Log.Warn($"[{KleeMod.ModId}] reward row probe failed: {e.Message}");
                }
            };
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] reward row probe not scheduled: {e.Message}");
        }
    }

    private static void Report(NCardRewardSelectionScreen screen, int optionCount)
    {
        var row = screen.GetNodeOrNull<Control>("UI/CardRow");
        if (row == null)
        {
            Log.Warn($"[{KleeMod.ModId}] reward row probe: no UI/CardRow on the screen");
            return;
        }
        var view = screen.GetViewportRect();
        var holders = row.GetChildren().OfType<NGridCardHolder>().ToList();
        var parts = new List<string>();
        var anyOff = false;
        for (var i = 0; i < holders.Count; i++)
        {
            var holder = holders[i];
            var card = holder.CardNode;
            var body = card?.Body;
            var rect = body != null ? body.GetGlobalRect() : new Rect2();
            var visible = card != null && card.IsVisibleInTree()
                          && card.Modulate.A > 0.01f
                          && body != null && body.IsVisibleInTree();
            var placement = Classify(view, rect, visible);
            anyOff |= placement != Placement.OnScreen;
            var center = holder.GlobalPosition;
            parts.Add(string.Format(CultureInfo.InvariantCulture,
                "{0}:{1} {2} holder=({3:0},{4:0}) local_x={5:0} card_rect=({6:0},{7:0} {8:0}x{9:0})",
                i, card?.Model?.Id.ToString() ?? "none", placement,
                center.X, center.Y, holder.Position.X,
                rect.Position.X, rect.Position.Y, rect.Size.X, rect.Size.Y));
        }
        var text = new StringBuilder();
        text.Append(anyOff ? "reward row OFF SCREEN" : "reward row ok");
        text.Append(string.Format(CultureInfo.InvariantCulture,
            ": options={0} holders={1} canvas={2:0}x{3:0}",
            optionCount, holders.Count, view.Size.X, view.Size.Y));
        if (holders.Count > 0)
        {
            text.Append(string.Format(CultureInfo.InvariantCulture,
                " expected_local_x={0:0}..{1:0}",
                ExpectedX(0, holders.Count), ExpectedX(holders.Count - 1, holders.Count)));
        }
        text.Append(" | ").Append(string.Join(" | ", parts));
        if (anyOff)
        {
            Log.Warn($"[{KleeMod.ModId}] {text}");
        }
        else
        {
            Log.Info($"[{KleeMod.ModId}] {text}");
        }
    }
}

/// <summary>
/// Called from <c>_Ready</c> and again on a reroll, so every row the player
/// is shown is read once. Read-only; see <see cref="RewardRowProbe"/>.
/// </summary>
[HarmonyPatch(typeof(NCardRewardSelectionScreen),
              nameof(NCardRewardSelectionScreen.RefreshOptions))]
internal static class NCardRewardSelectionScreen_RefreshOptions_RowProbe_Patch
{
    private static void Postfix(NCardRewardSelectionScreen __instance,
                                IReadOnlyList<CardCreationResult> options,
                                IReadOnlyList<CardRewardAlternative> extraOptions) =>
        RewardRowProbe.Schedule(__instance, options?.Count ?? -1);
}
