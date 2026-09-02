using System.Collections.Generic;
using Godot;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Context;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.addons.mega_text;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// THE PENDING PLANS, FACE UP, IN ORDER (slice draft 6 sec.5, the UI list).
///
/// IT IS THE `EB-198` STRIP RE-POINTED, not a second element, and that is why
/// this file is short: <see cref="KurageMemoryCard"/> settled the hard
/// questions -- where a HUD element can live without colliding with the relic
/// column, how it is built and freed through
/// <c>TrackedDisplayBridge.Registry</c>, why the local seat is the only seat,
/// and that a MOD card's thumbnail is <c>CustomCardModel.CustomPortrait</c> and
/// never <c>CardModel.Portrait</c> (its own header records that live catch).
/// Everything here reuses those answers.
///
/// WHAT CHANGED IS WHAT THERE IS TO SHOW. The memory arm had ONE front card and
/// a bank, and the interesting fact was affordability -- so it drew one
/// thumbnail with a coloured ring. Draft 6 has no bank and no price: what the
/// player needs is WHICH Plans are waiting and IN WHAT ORDER, because "three
/// Plans land together the next morning" is the moment the kit is built around
/// (brief sec.3). So this draws a COLUMN, front at the top, one thumbnail per
/// pending Plan.
///
/// A COLUMN, CAPPED, AND THE CAP IS HONEST. <see cref="MaxDrawn"/> thumbnails
/// fit the band; a longer queue draws the first four and says "+N" under them
/// rather than silently dropping the tail. The count under the column is the
/// queue's whole length, which is the same number
/// <c>PendingPlansPower</c>'s badge carries -- both read
/// <c>KokomiPlan.Pending</c>, so the two cannot disagree.
///
/// ON THE JELLYFISH IS WHERE THE SLICE ASKS FOR IT, and the honest report is
/// that this is a SCREEN-EDGE HUD element, not a node parented to the pet.
/// The reading taken, and why: a creature-parented strip is a
/// <c>Node2D</c> that has to track a creature node the combat room can move,
/// scale and tween (<c>NCreature.DoScaleTween</c>), and the memory arm's own
/// §14.5 records that the creature-tracked version was the one that misread.
/// The pet sits beside her at the left of the field and this element sits at
/// the left edge of the screen, so they read as one column in practice --
/// whether they actually do is a live question and nothing headless can answer
/// it.
///
/// QUARANTINED. `Vfx/Prototype/**` is Compile Remove'd without
/// `-p:PrototypeCards=true`. Revert is the flag.
/// </summary>
internal static class KokomiPlanStrip
{
    private const string RootName = "KleeModKokomiPlanStrip";

    private const float ThumbWidth = 92f;
    private const float ThumbHeight = 124f;
    private const float ThumbGap = 6f;
    private const float EdgeMargin = 24f;
    private const int CountFontSize = 30;

    /// <summary>How many Plans get a picture. A fifth would run off the band.</summary>
    internal const int MaxDrawn = 4;

    private static readonly Color CountColor = StsColors.cream;

    /// <summary>One element per seat, freed by the shared display skeleton the
    /// way the gauges are.</summary>
    private static readonly
        TrackedDisplayBridge.Registry<Player, Control> Displays = new();

    /// <summary>Is the Plan strip the element this seat should have?</summary>
    private static bool Live(Creature? creature) =>
        KokomiOverhaul.LiveFor(creature);

    /// <summary>Build for the LOCAL seat and nothing else. Called from the same
    /// `NCombatUi.Activate` postfix the gauges and the memory card use, so
    /// there is one combat-lifecycle entry point rather than three that can
    /// disagree about when a room is live.</summary>
    public static void Setup(CombatState? state)
    {
        var me = TryGetMe(state);
        var creature = me?.Creature;
        if (me == null || !Live(creature)) return;
        if (NCombatRoom.Instance?.Ui is not { } ui) return;

        Displays.Discard(me);
        var root = Build();
        ui.AddChildSafely(root);
        Displays.Set(me, root);
        Paint(root, me);
    }

    /// <summary>Re-read the queue and redraw. Driven by
    /// <c>KokomiPlan.RefreshStrip</c>, which fires on every queue move --
    /// exactly the funnel the memory arm's strip rides, and for the same
    /// reason: no polling anywhere.</summary>
    public static void Refresh(Creature? creature)
    {
        var player = creature?.Player;
        if (player == null || !LocalContext.IsMe(player)) return;
        if (!Live(creature)) return;

        var root = Displays.Get(player);
        if (root == null)
        {
            // Stale or never built (mid-combat reload): rebuild in place, the
            // reference-bridge idiom `GaugeBridge.Refresh` uses.
            Setup(creature!.CombatState as CombatState);
            root = Displays.Get(player);
            if (root == null) return;
        }
        Paint(root, player);
    }

    /// <summary>Teardown, character-scoped like every other door into a
    /// prototype HUD element (EB-225 / R225 item 6).</summary>
    public static void DiscardAll(CombatState? state)
    {
        var me = TryGetMe(state);
        if (me == null || !Live(me.Creature)) return;
        Displays.Discard(me);
    }

    private static Player? TryGetMe(CombatState? state)
    {
        // `LocalContext.GetMe` THROWS for "not in this combat" rather than
        // answering null -- the catch `KurageMemoryCard.TryGetMe` records at
        // length, which ended two whole-fight blind sessions. Same guard here.
        if (state == null || LocalContext.NetId is not { } netId) return null;
        try
        {
            return state.GetPlayer(netId);
        }
        catch (System.InvalidOperationException)
        {
            return null;
        }
    }

    private static Control Build()
    {
        var height = MaxDrawn * ThumbHeight + (MaxDrawn - 1) * ThumbGap
                     + CountFontSize + 8f;
        var root = new Control
        {
            Name = RootName,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            // Left edge, vertically centred -- the anchor
            // `KurageMemoryCard.Build` argues for, so the two elements occupy
            // the same band and a resize moves them together.
            AnchorLeft = 0f,
            AnchorRight = 0f,
            AnchorTop = 0.5f,
            AnchorBottom = 0.5f,
            OffsetLeft = EdgeMargin,
            OffsetRight = EdgeMargin + ThumbWidth,
            OffsetTop = -height / 2f,
            OffsetBottom = height / 2f,
        };

        for (var i = 0; i < MaxDrawn; i++)
        {
            var thumb = new TextureRect
            {
                Name = "Plan" + i,
                MouseFilter = Control.MouseFilterEnum.Ignore,
                ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
                StretchMode = TextureRect.StretchModeEnum.KeepAspectCovered,
                Position = new Vector2(0f, i * (ThumbHeight + ThumbGap)),
                Size = new Vector2(ThumbWidth, ThumbHeight),
                Visible = false,
            };
            root.AddChildSafely(thumb);
        }

        var count = new Label
        {
            Name = "Count",
            MouseFilter = Control.MouseFilterEnum.Ignore,
            HorizontalAlignment = HorizontalAlignment.Center,
            Position = new Vector2(
                0f, MaxDrawn * (ThumbHeight + ThumbGap) + 4f),
            Size = new Vector2(ThumbWidth, CountFontSize + 8f),
        };
        count.AddThemeFontSizeOverride(ThemeConstants.Label.FontSize,
                                       CountFontSize);
        count.AddThemeColorOverride(ThemeConstants.Label.FontColor, CountColor);
        root.AddChildSafely(count);
        return root;
    }

    /// <summary>
    /// Draw the queue: front at the top, in writing order.
    ///
    /// AN EMPTY QUEUE DRAWS NOTHING AT ALL -- no thumbnails and no count. The
    /// memory arm's `EB-198` lesson was that a HUD element showing a number
    /// over an empty state reads as a state; nothing pending is nothing to say.
    /// </summary>
    private static void Paint(Control root, Player player)
    {
        var pending = KokomiPlan.Pending(player);
        var count = root.GetNodeOrNull<Label>("Count");

        for (var i = 0; i < MaxDrawn; i++)
        {
            var thumb = root.GetNodeOrNull<TextureRect>("Plan" + i);
            if (thumb == null) continue;
            if (i >= pending.Count)
            {
                thumb.Visible = false;
                continue;
            }
            thumb.Visible = true;
            thumb.Texture = Portrait(pending[i].Source);
        }

        if (count == null) return;
        count.Text = pending.Count switch
        {
            0 => string.Empty,
            var n when n > MaxDrawn => "+" + (n - MaxDrawn),
            _ => string.Empty,
        };
    }

    /// <summary>
    /// The card's picture, OURS FIRST -- the correction `EB-198`'s live
    /// acceptance forced on the memory strip, restated here rather than
    /// re-learned: a MOD card has no `PortraitPath` to load, and its art is a
    /// runtime `ImageTexture` handed over as
    /// <c>CustomCardModel.CustomPortrait</c>.
    /// </summary>
    private static Texture2D? Portrait(CardModel? card)
    {
        if (card == null) return null;
        if (card is CustomCardModel custom && custom.CustomPortrait != null)
        {
            return custom.CustomPortrait;
        }
        return card.HasPortrait ? card.Portrait : null;
    }
}

/// <summary>The element dies with the combat, like the gauges and the memory
/// card do -- one teardown per HUD element, on the game's own hook.</summary>
// lint: no-seat: pure static teardown of this file's own registry. It reaches
// `DiscardAll`, which resolves the seat through the guarded `TryGetMe` and
// then asks `KokomiOverhaul.LiveFor` -- the character scope is one call in and
// spelled there rather than restated here.
[HarmonyPatch(typeof(NCombatUi), nameof(NCombatUi.Deactivate))]
internal static class NCombatUi_Deactivate_KokomiPlanStrip_Patch
{
    [HarmonyPostfix]
    public static void Postfix() =>
        KokomiPlanStrip.DiscardAll(KokomiRules.Combat as CombatState);
}
