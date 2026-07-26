using System.Collections.Generic;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// The Salon stage (animation sprint 2, Track D — the D4 redesign).
///
/// WHAT FAILED, and why this is a re-layout rather than a restyle: sprint 1
/// put three card-art portraits in framed squares beside Furina. The portraits
/// are 500x380 gameplay screenshots, and at combat scale the three read as
/// three identical blue smudges — member identity did not survive. The
/// [USER] verdict (2026-07-24) failed the styling and kept the concept. So the
/// members are now freestanding SILHOUETTE mini-sprites standing on a shallow
/// stage arc: no frame, no square crop, identity carried by outline.
/// Ghost-outline-for-empty is the one sprint-1 idea that did read, restyled
/// here to the stage language.
///
/// SLOT-INDEX-KEYED, per Funnel Contract §1. Deploy is by card and duplicates
/// are legal — three of the same member is a valid stage — so nothing here may
/// assume a fixed member-to-slot mapping or distinct members. Slot i renders
/// whatever <see cref="SalonMemberPower.CompanyOf"/> reports at index i, and a
/// company of three Ushers renders as three Ushers. This retires sprint-1
/// D1's fixed member-to-slot portrait assignment, which silently assumed both.
///
/// The Encore gauge lives here now (D3). It was evicted from the overhead slot
/// by the C4 verdict — overhead means Burst for every character — and re-homes
/// as the ribbon beneath the arc, so the members visibly stand ON their fuel
/// and draining to zero visibly dims the stage they stand on. That causality
/// is the thing the old layout could not show.
///
/// Bridge skeleton is unchanged from sprint 1 (Displays dict + IsInstanceValid
/// staleness + lazy re-Setup + CombatVfxContainer + RemoteTransform2D tracking
/// + the NCombatUi.Activate postfix), which is what survived the playtest and
/// what the G1 extraction covers.
/// </summary>
public static class SalonVisualsBridge
{
    private const string ScenePathRelative = "furina/ui/salon_stage.tscn";

    /// <summary>
    /// Anchor relative to Furina's creature node origin. The stage sits low
    /// and to her left; it is wider than the old flank line (three sprites
    /// plus a ribbon), so the span is deliberately kept inside the creature's
    /// own 240-wide bounds box to stay clear of enemy intent positions and
    /// targeting arrows.
    ///
    /// Y was -30 until the 2026-07-25 playtest read the Encore ribbon as
    /// having no number at all. The ribbon's value label hung BELOW the ribbon,
    /// which put it at creature-relative y -4..+14 — i.e. under the feet, in
    /// the band NCreatureStateDisplay owns. That band is not ours: the HP bar
    /// spans the full bounds width, and NHealthBar.UpdateLayoutForCreatureBounds
    /// pins the block badge to `bounds.GlobalPosition.X - halfWidth`, the LEFT
    /// edge of the 240-wide box — which is exactly where this stage sits. The
    /// number was drawn and then covered. The label moved up onto the ribbon
    /// (see salon_stage.tscn) and the whole stage lifted clear of the band.
    /// Both are layout, so both are [USER] D5's to judge.
    /// </summary>
    private static readonly Vector2 AnchorOffset = new(-104f, -52f);

    /// <summary>Sprite art per member identity, pck-relative.</summary>
    private static readonly Dictionary<SalonMember, string> MemberSprites = new()
    {
        [SalonMember.Usher] = "furina/salon/member_usher.png",
        [SalonMember.Chevalmarin] = "furina/salon/member_chevalmarin.png",
        [SalonMember.Crabaletta] = "furina/salon/member_crabaletta.png",
    };

    private static readonly Color ActiveTint = new(1f, 1f, 1f, 1f);
    private static readonly Color DryTint = new(0.55f, 0.6f, 0.68f, 0.92f);
    private static readonly Color PoolActive = new(0.62f, 0.85f, 1f, 0.3f);
    private static readonly Color PoolDry = new(0.5f, 0.55f, 0.62f, 0.14f);
    private static readonly Color BeamActive = new(0.7f, 0.88f, 1f, 0.12f);
    private static readonly Color BeamDry = new(0.7f, 0.88f, 1f, 0.03f);

    /// <summary>Ribbon renders full at this many Encore (display only).</summary>
    private const int RibbonVisualSpan = 20;

    private const float RibbonFullWidth = 180f;

    private const string PreviousCountMeta = "kleemod_salon_count";
    private const string PreviousEncoreMeta = "kleemod_salon_encore";

    private static readonly TrackedDisplayBridge.Registry<Player> Displays = new();

    private static bool _warnedMissingScene;

    public static void Setup(NCombatRoom combatRoom, Player player)
    {
        var creature = player.Creature;
        // Non-Furina players never spawn the stage (mirrors the reference
        // bridge's is-not-Hexaghost check).
        if (creature == null || player.Character is not IFurinaCharacter)
        {
            return;
        }

        DiscardDisplay(player);

        var display = TrackedDisplayBridge.Spawn(
            combatRoom, ScenePathRelative, ref _warnedMissingScene,
            "Salon stage disabled");
        if (display == null)
        {
            return;
        }

        TrackedDisplayBridge.Track(combatRoom, creature, display, AnchorOffset);
        Displays.Set(player, display);
        RefreshDisplay(display, creature, animate: false);
    }

    /// <summary>
    /// Re-read company, dry state and Encore, then redraw. Call sites are the
    /// Funnel Contract's own funnels: SalonMemberPower.Deploy (the single
    /// composition funnel) and the Encore gain/spend/absorb trio, plus
    /// FurinaResources.SyncMeters for the every-sync dry check.
    /// </summary>
    public static void Refresh(Creature? creature)
    {
        var player = creature?.Player;
        if (creature == null || player == null
            || player.Character is not IFurinaCharacter)
        {
            return;
        }

        var display = GetDisplay(player);
        if (display == null)
        {
            if (NCombatRoom.Instance is not { } room)
            {
                return;
            }
            Setup(room, player);
            display = GetDisplay(player);
            if (display == null)
            {
                return;
            }
        }

        RefreshDisplay(display, creature, animate: true);
    }

    public static void DiscardDisplay(Player player) => Displays.Discard(player);

    private static Node2D? GetDisplay(Player player) => Displays.Get(player);

    private static Texture2D? SpriteFor(SalonMember member) =>
        MemberSprites.TryGetValue(member, out var relative)
        && KleePck.Path(relative) is { } path
            ? ResourceLoader.Load<Texture2D>(path)
            : null;

    private static void RefreshDisplay(
        Node2D display, Creature creature, bool animate)
    {
        var company = SalonMemberPower.CompanyOf(creature);
        int encore = FurinaResources.Encore(creature);
        bool dry = encore < SalonConstants.TickEncoreCost;

        int previousCount = display.HasMeta(PreviousCountMeta)
            ? (int)display.GetMeta(PreviousCountMeta)
            : 0;
        display.SetMeta(PreviousCountMeta, company.Count);

        var anim = display.GetNodeOrNull<AnimationPlayer>("%AnimationPlayer");
        var popped = false;

        for (var i = 0; i < SalonConstants.MemberSlots; i++)
        {
            bool occupied = i < company.Count;
            var sprite = display.GetNodeOrNull<Sprite2D>($"%Sprite{i + 1}");
            if (sprite != null)
            {
                // Identity is read per SLOT from state, every refresh —
                // duplicates render as duplicates, and an out-of-order deploy
                // cannot desync the stage from the company.
                sprite.Texture = occupied ? SpriteFor(company[i]) : null;
                sprite.Visible = occupied && sprite.Texture != null;
                sprite.Modulate = dry ? DryTint : ActiveTint;
            }

            // Empty slot = ghost outline on the stage floor (the surviving
            // sprint-1 idea, restyled to the stage language).
            if (display.GetNodeOrNull<ColorRect>($"%Ghost{i + 1}") is { } ghost)
            {
                ghost.Visible = !occupied;
            }

            if (display.GetNodeOrNull<ColorRect>($"%Pool{i + 1}") is { } pool)
            {
                pool.Visible = occupied;
                pool.Color = dry ? PoolDry : PoolActive;
            }

            if (display.GetNodeOrNull<ColorRect>($"%Beam{i + 1}") is { } beam)
            {
                beam.Visible = occupied;
                beam.Color = dry ? BeamDry : BeamActive;
            }

            if (animate && occupied && i >= previousCount && anim != null)
            {
                // One AnimationPlayer: a multi-member deploy queues its pops
                // into a short cascade instead of cutting the first one off
                // (the sprint-1 behaviour, kept).
                if (popped)
                {
                    anim.Queue($"slot{i + 1}_pop");
                }
                else
                {
                    anim.Play($"slot{i + 1}_pop");
                    popped = true;
                }
            }
        }

        RefreshRibbon(display, encore, anim, animate);
    }

    /// <summary>
    /// D3's Encore ribbon: the members stand on their fuel. Draining to zero
    /// plays the flash and dims the whole stage — the overdraw moment, shown
    /// as a consequence rather than as a number changing somewhere else.
    /// </summary>
    private static void RefreshRibbon(
        Node2D display, int encore, AnimationPlayer? anim, bool animate)
    {
        if (display.GetNodeOrNull<ColorRect>("%RibbonFill") is { } fill)
        {
            float pct = Mathf.Clamp(encore / (float)RibbonVisualSpan, 0f, 1f);
            fill.Size = new Vector2(RibbonFullWidth * pct, fill.Size.Y);
        }

        if (display.GetNodeOrNull<Label>("%RibbonLabel") is { } label)
        {
            label.Text = encore.ToString();
        }

        int previous = display.HasMeta(PreviousEncoreMeta)
            ? (int)display.GetMeta(PreviousEncoreMeta)
            : encore;
        display.SetMeta(PreviousEncoreMeta, encore);

        if (animate && previous > 0 && encore <= 0 && anim != null)
        {
            anim.Stop();
            anim.Play("overdraw");
        }
    }
}
