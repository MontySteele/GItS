using System;
using Godot;
using HarmonyLib;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// THE RETURNING HP ON FURINA'S HP BAR (her HP legibility pass, 2026-10-19,
/// `review/active/furina-hp-legibility-2026-10-19.md` change 1, ruled (a)):
/// "The HP that will come back after combat shows as a pale segment beyond
/// her current HP, the way the base game's bar shows Block over HP." Both
/// seats of the UI check missed the refund until the fight ended.
///
/// THE NUMBER is <see cref="FurinaStageLedger.ReturningAt"/>: the drained HP
/// within the buffer and, under A Five-Century Act, the past-line part too,
/// never past Max HP -- the figure the Drained counter's hover prints
/// (<see cref="DrainedCounter.ReturnsLine"/>).
///
/// THE PICTURE is one <c>ColorRect</c> inside the bar's fill container
/// (<c>NHealthBar</c>'s <c>%HpForegroundContainer</c>, where the base game
/// lays its poison and doom previews and <see cref="FurinaStageCueNodes"/>
/// its chips), anchored from current HP to current HP plus the returning HP
/// as shares of Max HP, the foreground's own top and bottom. Drawn on every
/// client that draws her bar: the ledger runs the same on each, so a co-op
/// partner sees the same segment. Nothing here moves a number or reaches the
/// wire, so seats read the hover and the page, not this.
///
/// THE FEED: a postfix on <c>NHealthBar.RefreshValues</c> (every HP or Block
/// change) and <see cref="FurinaStage.RefreshBadges"/> (a Drain, a Repay, A
/// Five-Century Act played). Nothing here may throw at its caller.
/// </summary>
public static class FurinaReturningHpBar
{
    /// <summary>The node this file owns.</summary>
    internal const string SegmentName = "KleeModReturningHp";

    /// <summary>The segment's colour: the base bar's red
    /// (<c>NHealthBar._redForegroundColor</c>, #F1373E) washed pale toward
    /// cream, half see-through, so it reads as HP not yet held.</summary>
    public static readonly Color SegmentColour = new(0.98f, 0.70f, 0.70f, 0.55f);

    private static readonly AccessTools.FieldRef<NHealthBar, Creature> CreatureOf =
        AccessTools.FieldRefAccess<NHealthBar, Creature>("_creature");

    private static bool _warned;

    /// <summary>The segment's span as shares of the bar, [left, right), or
    /// null when nothing returns. Pure: the pins read it.</summary>
    public static (float Left, float Right)? Span(int hp, int maxHp,
                                                  int returning)
    {
        if (maxHp <= 0 || hp <= 0 || returning <= 0) return null;
        var right = Math.Min(maxHp, hp + returning);
        if (right <= hp) return null;
        return ((float)hp / maxHp, (float)right / maxHp);
    }

    /// <summary>The returning HP for <paramref name="creature"/> now; 0 for
    /// anyone whose Stage is not up.</summary>
    public static int Returning(Creature? creature)
    {
        if (creature == null || !FurinaStage.LiveFor(creature)) return 0;
        return FurinaStageLedger.For(creature)
            .ReturningAt((int)creature.CurrentHp, (int)creature.MaxHp);
    }

    /// <summary>From <see cref="FurinaStage.RefreshBadges"/>: find her bar
    /// and repaint it. Headless-safe: it returns before any node work when
    /// there is no combat room.</summary>
    public static void Refresh(Creature? creature)
    {
        try
        {
            if (creature == null || NCombatRoom.Instance is not { } room) return;
            if (room.GetCreatureNode(creature) is not { } node) return;
            var display = node.GetNodeOrNull<Control>("%HealthBar");
            var bar = display?.GetNodeOrNull<NHealthBar>("%HealthBar");
            if (bar != null) Paint(bar, creature);
        }
        catch (Exception e)
        {
            Warn(e);
        }
    }

    /// <summary>The postfix's body: repaint the bar the game just refreshed,
    /// for Furina (or anyone whose Stage is up) only.</summary>
    internal static void OnRefresh(NHealthBar bar)
    {
        try
        {
            if (!GodotObject.IsInstanceValid(bar)) return;
            var creature = CreatureOf(bar);
            if (creature == null) return;
            if (!FurinaResources.IsFurina(creature)
                && !FurinaStage.LiveFor(creature))
            {
                return;
            }
            Paint(bar, creature);
        }
        catch (Exception e)
        {
            Warn(e);
        }
    }

    private static void Paint(NHealthBar bar, Creature creature)
    {
        var fill = bar.GetNodeOrNull<Control>("%HpForegroundContainer");
        if (fill == null || !GodotObject.IsInstanceValid(fill)) return;
        var segment = fill.GetNodeOrNull<ColorRect>(SegmentName);
        var span = Span((int)creature.CurrentHp, (int)creature.MaxHp,
                        Returning(creature));
        if (span is not { } s)
        {
            if (segment != null) segment.Visible = false;
            return;
        }
        if (segment == null)
        {
            var template = fill.GetNodeOrNull<Control>("%HpForeground");
            segment = new ColorRect
            {
                Name = SegmentName,
                Color = SegmentColour,
                MouseFilter = Control.MouseFilterEnum.Ignore,
                AnchorTop = template?.AnchorTop ?? 0f,
                AnchorBottom = template?.AnchorBottom ?? 1f,
                OffsetTop = template?.OffsetTop ?? 0f,
                OffsetBottom = template?.OffsetBottom ?? 0f,
            };
            fill.AddChildSafely(segment);
        }
        segment.AnchorLeft = s.Left;
        segment.AnchorRight = s.Right;
        segment.OffsetLeft = 0f;
        segment.OffsetRight = 0f;
        segment.Visible = true;
    }

    private static void Warn(Exception e)
    {
        if (_warned) return;
        _warned = true;
        Log.Warn($"[{KleeMod.ModId}] returning HP segment skipped: {e}");
    }
}

/// <summary>Every refresh of a bar repaints Furina's returning segment.
/// </summary>
[HarmonyPatch(typeof(NHealthBar), nameof(NHealthBar.RefreshValues))]
internal static class NHealthBar_RefreshValues_FurinaReturningHp_Patch
{
    [HarmonyPostfix]
    public static void Postfix(NHealthBar __instance) =>
        FurinaReturningHpBar.OnRefresh(__instance);
}
