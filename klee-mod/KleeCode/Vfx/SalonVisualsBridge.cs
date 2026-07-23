using System.Collections.Generic;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// Onscreen Salon members (animation sprint 1, Track D): three slots in a
/// flank line rising behind Furina's left shoulder, one per
/// <see cref="SalonMemberPower"/> stack. Same bridge skeleton as
/// <see cref="GaugeBridge"/> — Displays dict + IsInstanceValid staleness +
/// lazy re-Setup + CombatVfxContainer + RemoteTransform2D tracking. The
/// common-base extraction is deliberately deferred until after both concrete
/// bridges have survived a playtest (plan D2: refactor after the second
/// instance works, not before).
///
/// Slot portraits come from the loose card-art register (KleeArt.CardPortrait
/// — the salon members ARE cards, so their art already ships), not the pck:
/// per plan D1, portraits are placeholder-grade this sprint and the slots +
/// states are the deliverable. A missing PNG just leaves the framed slot
/// empty.
///
/// States (all display-only, re-read from the command layer):
/// - occupied/empty: SalonMemberPower.Count — empty slots show as dim frames.
/// - newly occupied: scene-authored "slotN_pop" scale pop (D3's activate).
/// - dry: Encore below the tick cost — occupied slots desaturate and the
///   badge greys out (D3's deactivate treatment; members attack at 0.75x).
/// </summary>
public static class SalonVisualsBridge
{
    private const string ScenePathRelative = "furina/ui/salon.tscn";

    /// <summary>Anchor relative to Furina's creature node origin.</summary>
    private static readonly Vector2 AnchorOffset = new(-88f, -70f);

    private static readonly string[] MemberCardIds =
    {
        "gentilhomme_usher",
        "surintendante_chevalmarin",
        "mademoiselle_crabaletta",
    };

    private static readonly Color OccupiedTint = new(1f, 1f, 1f, 1f);
    private static readonly Color DryTint = new(0.62f, 0.62f, 0.68f, 1f);
    private static readonly Color EmptyTint = new(1f, 1f, 1f, 0.28f);
    private static readonly Color BadgePaid = new(0.35f, 0.75f, 1f, 1f);
    private static readonly Color BadgeDry = new(0.45f, 0.45f, 0.5f, 1f);

    private const string PreviousCountMeta = "kleemod_salon_count";

    private static readonly Dictionary<Player, Node2D> Displays = new();

    private static bool _warnedMissingScene;

    public static void Setup(NCombatRoom combatRoom, Player player)
    {
        var creature = player.Creature;
        // Guard mirrors the reference bridge's "player.Character is not
        // Hexaghost" check (plan D4): non-Furina players never spawn the scene.
        if (creature == null || player.Character is not IFurinaCharacter)
        {
            return;
        }

        DiscardDisplay(player);

        string? scenePath = KleePck.Path(ScenePathRelative);
        if (scenePath == null)
        {
            if (!_warnedMissingScene)
            {
                _warnedMissingScene = true;
                MegaCrit.Sts2.Core.Logging.Log.Warn(
                    $"[{KleeMod.ModId}] {ScenePathRelative} missing from pck; "
                    + "Salon display disabled");
            }
            return;
        }

        var display = ResourceLoader
            .Load<PackedScene>(scenePath)
            .Instantiate<Node2D>();
        combatRoom.CombatVfxContainer.AddChildSafely(display);

        for (var i = 0; i < MemberCardIds.Length; i++)
        {
            if (display.GetNodeOrNull<TextureRect>($"%Slot{i + 1}Portrait")
                    is { } portrait
                && KleeArt.CardPortrait(MemberCardIds[i]) is { } texture)
            {
                portrait.Texture = texture;
            }
        }

        var creatureNode = combatRoom.GetCreatureNode(creature);
        if (creatureNode != null)
        {
            var anchor = new RemoteTransform2D
            {
                Position = AnchorOffset,
                UpdateRotation = false,
                UpdateScale = false,
                UseGlobalCoordinates = true,
            };
            creatureNode.AddChildSafely(anchor);
            anchor.RemotePath = anchor.GetPathTo(display);
        }

        Displays[player] = display;
        RefreshDisplay(display, creature, allowPop: false);
    }

    /// <summary>
    /// Re-read Salon count + dry state and redraw. Call sites: the Deploy
    /// funnel (same-resolution composition changes) and
    /// FurinaResources.SyncMeters (every Furina display sync moment, which
    /// keeps the dry badge honest as Encore moves).
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

        RefreshDisplay(display, creature, allowPop: true);
    }

    public static void DiscardDisplay(Player player)
    {
        if (Displays.TryGetValue(player, out var old)
            && GodotObject.IsInstanceValid(old))
        {
            old.QueueFree();
        }
        Displays.Remove(player);
    }

    private static Node2D? GetDisplay(Player player)
    {
        var display = Displays.GetValueOrDefault(player);
        if (display != null && GodotObject.IsInstanceValid(display))
        {
            return display;
        }

        Displays.Remove(player);
        return null;
    }

    private static void RefreshDisplay(
        Node2D display, Creature creature, bool allowPop)
    {
        int count = SalonMemberPower.Count(creature);
        bool dry = FurinaResources.Encore(creature)
                   < SalonConstants.TickEncoreCost;

        int previous = display.HasMeta(PreviousCountMeta)
            ? (int)display.GetMeta(PreviousCountMeta)
            : 0;
        display.SetMeta(PreviousCountMeta, count);

        var anim = display.GetNodeOrNull<AnimationPlayer>("%AnimationPlayer");
        var popped = false;
        for (var i = 0; i < SalonConstants.MemberSlots; i++)
        {
            var slot = display.GetNodeOrNull<Node2D>($"%Slot{i + 1}");
            if (slot == null)
            {
                continue;
            }

            bool occupied = i < count;
            slot.Modulate = occupied
                ? (dry ? DryTint : OccupiedTint)
                : EmptyTint;

            if (display.GetNodeOrNull<Panel>($"%Slot{i + 1}Badge") is { } badge)
            {
                badge.Visible = occupied;
                badge.Modulate = dry ? BadgeDry : BadgePaid;
            }

            if (allowPop && occupied && i >= previous && anim != null)
            {
                // One AnimationPlayer: a multi-member deploy queues its pops
                // into a short cascade instead of cutting the first one off.
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
    }
}
