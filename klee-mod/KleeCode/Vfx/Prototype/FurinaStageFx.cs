using System;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// FURINA'S STAGE EFFECTS (2026-10-13, her model art, phase B;
/// review/active/furina-visual-paper-2026-10-13.md). Spend, Drain and Repay
/// had no look of their own: the Fanfare number dropped, and the base damage
/// and heal numbers played. Each now plays a short effect clip on her body:
///
///   * Spend: a golden burst thrown up from her chest (0.8 s, Fanfare gold);
///   * Drain: Hydro droplets drawn out of her and along a shallow arc to the
///     guest seat nearest her (0.9 s);
///   * Repay: the droplets come back from that seat and slow into her, then a
///     soft heal glow blooms (1.0 s).
///
/// THE SCENE CONTRACT (tools/furina_rig/rig.py): under <c>%StageFx</c>, at her
/// chest, the Sprite2Ds <c>%SpendFx</c>, <c>%DrainFx</c>, <c>%RepayFx</c>, each
/// on a material of its own wearing its manifest tint, and the
/// AnimationPlayers <c>%SpendFxPlayer</c>, <c>%DrainFxPlayer</c>,
/// <c>%RepayFxPlayer</c>, each with one animation named for its effect. A
/// player of its own per effect, so a Repay straight after a Spend does not
/// cut the burst short; a repeat of the same effect restarts it.
///
/// NON-BLOCKING. <see cref="StageDirector"/> calls the board's
/// <see cref="IStageBoard.Effect"/> and never waits: the effect plays over
/// whatever she is doing, and the rules go on at once. Display only, and
/// inert without a scene tree (headless, a stale pack, a body that is not
/// hers): every lookup is null-guarded and the whole body is inside a catch,
/// the rule every bridge in this mod is written to.
///
/// THE REACH. Drain and Repay were drawn for a run of <c>reach</c> px (the
/// node's metadata: chest to the first guest seat of the review sheet). The
/// guest nearest her may stand nearer or further, so the sprite is stretched
/// along x to land on that guest's feet line, within
/// [<see cref="MinStretch"/>, <see cref="MaxStretch"/>]; with no guest
/// seated it plays as drawn.
/// </summary>
internal static class FurinaStageFx
{
    internal const string GroupNode = "StageFx";
    internal const string ReachMeta = "reach";

    /// <summary>The narrowest and widest a reaching effect is stretched to:
    /// past these the droplets read as a smear or a dot.</summary>
    internal const float MinStretch = 0.6f;

    internal const float MaxStretch = 2.5f;

    /// <summary>The animation an effect plays, named for it. Pure.</summary>
    internal static string AnimationFor(StageEffect effect) => effect switch
    {
        StageEffect.Spend => "spend",
        StageEffect.Drain => "drain",
        _ => "repay",
    };

    /// <summary>The effect's sprite, by unique name. Pure.</summary>
    internal static string SpriteFor(StageEffect effect) => effect switch
    {
        StageEffect.Spend => "SpendFx",
        StageEffect.Drain => "DrainFx",
        _ => "RepayFx",
    };

    /// <summary>The effect's own AnimationPlayer, by unique name. Pure.</summary>
    internal static string PlayerFor(StageEffect effect) => SpriteFor(effect) + "Player";

    /// <summary>Whether the effect runs between her and the stage. Pure.</summary>
    internal static bool Reaches(StageEffect effect)
        => effect is StageEffect.Drain or StageEffect.Repay;

    /// <summary>
    /// The x stretch for a run of <paramref name="run"/> px from her chest to
    /// the guest, against the <paramref name="reach"/> the effect was drawn
    /// for: 1 when either is unknown or the guest is behind her, else their
    /// ratio within [<see cref="MinStretch"/>, <see cref="MaxStretch"/>]. Pure.
    /// </summary>
    internal static float StretchFor(float run, float reach)
        => run <= 0f || reach <= 0f ? 1f : Math.Clamp(run / reach, MinStretch, MaxStretch);

    /// <summary>
    /// Play <paramref name="effect"/> on <paramref name="furina"/>'s body.
    /// Never throws and never waits.
    /// </summary>
    public static void Play(Creature? furina, StageEffect effect)
    {
        if (furina == null || furina.IsDead) return;
        try
        {
            var room = NCombatRoom.Instance;
            var node = room?.GetCreatureNode(furina);
            if (node == null || !GodotObject.IsInstanceValid(node)) return;
            var visuals = node.Visuals;
            if (visuals == null || !GodotObject.IsInstanceValid(visuals)) return;
            if (visuals.GetNodeOrNull<AnimationPlayer>("%" + PlayerFor(effect)) is not { } player) return;
            if (Reaches(effect)) Stretch(room!, furina, visuals, effect);
            player.Stop();
            player.Play(AnimationFor(effect));
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] stage effect {effect} skipped: {e.Message}");
        }
    }

    private static void Stretch(NCombatRoom room, Creature furina, Node visuals, StageEffect effect)
    {
        if (visuals.GetNodeOrNull<Node2D>("%" + SpriteFor(effect)) is not { } sprite
            || sprite.GetParent() is not Node2D group
            || !sprite.HasMeta(ReachMeta))
        {
            return;
        }
        var reach = (float)sprite.GetMeta(ReachMeta).AsDouble();
        var run = 0f;
        foreach (var seat in FurinaStageLedger.For(furina).Seats)
        {
            if (seat.Pet is not { IsDead: false } pet) continue;
            var body = room.GetCreatureNode(pet);
            if (body == null || !GodotObject.IsInstanceValid(body)) continue;
            var x = group.ToLocal(body.GlobalPosition).X;
            if (x > 0f && (run <= 0f || x < run)) run = x;
        }
        var y = Math.Abs(sprite.Scale.Y);
        sprite.Scale = new Vector2(y * StretchFor(run, reach), sprite.Scale.Y);
    }
}
