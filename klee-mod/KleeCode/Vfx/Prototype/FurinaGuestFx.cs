using System;
using System.Collections.Generic;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Nodes.Rooms;
using MegaCrit.Sts2.Core.TestSupport;

namespace KleeMod.Vfx;

/// <summary>When a guest's effect may play.</summary>
public enum GuestFxTrigger
{
    /// <summary>The guest acts (the end of her turn, Encore!, Tutti!, a
    /// Bow, Showstopper's second sweep: every act).</summary>
    Act,

    /// <summary>The guest's line fires (<see cref="IStageBoard.LineCue"/>):
    /// Navia's Spend discount, Chevreuse's Vulnerable on a Spend.</summary>
    Line,

    /// <summary>Neuvillette's "Your Hydro damage deals 2 more" adds to a
    /// Hydro hit.</summary>
    HydroBonus,
}

/// <summary>Where a guest's effect plays.</summary>
public enum GuestFxPlace
{
    /// <summary>No effect for this guest on this trigger.</summary>
    None,

    /// <summary>On each enemy the act or the bonus hits.</summary>
    Target,

    /// <summary>On Furina.</summary>
    Furina,

    /// <summary>On the guest's own body.</summary>
    Self,
}

/// <summary>
/// FURINA'S GUEST EFFECTS (2026-10-16, her plan item "guest-star pizazz";
/// [USER]: "unique particle effects or similar for each guest";
/// review/active/furina-guest-fx-2026-10-16.md). Until now a guest's act drew
/// only its lunge (<see cref="StagePerformerBeat"/>) and the damage number.
/// Each guest now plays one short effect (0.5 to 0.7 s), over the lunge:
///
/// | guest       | when                    | where       |
/// |-------------|-------------------------|-------------|
/// | Wriothesley | act (Cryo hit)          | the target  |
/// | Lynette     | act (Anemo hit)         | the target  |
/// | Clorinde    | act (Electro hit)       | the target  |
/// | Lyney       | act (Pyro to ALL)       | each enemy  |
/// | Escoffier   | act (Cryo to ALL)       | each enemy  |
/// | Charlotte   | act (Repay)             | Furina      |
/// | Sigewinne   | act (Repay)             | Furina      |
/// | Freminet    | act (Block)             | Furina      |
/// | Navia       | her Spend discount      | Navia       |
/// | Neuvillette | his bonus on a Hydro hit| the target  |
/// | Chevreuse   | her line on a Spend     | Chevreuse   |
///
/// THE SCENE CONTRACT (tools/furina_rig/guest_fx.py): one scene per guest,
/// <c>furina/model/guest_fx_&lt;name&gt;.tscn</c>, its root carrying
/// <c>metadata/anchor</c> ("feet": the bottom of the creature's hitbox;
/// "center": its effect spawn point) and <c>metadata/length</c>, its
/// <c>%FxPlayer</c> autoplaying the one animation named for the guest. A
/// scene of its own and not a node on her rig, as the stage effects are,
/// because most of these play on enemies (base-game scenes) and an act to
/// ALL plays one per enemy at once. Each instance goes into the room's
/// <c>CombatVfxContainer</c> and frees itself when its animation ends (a
/// timer catches a straggler).
///
/// THE HOOKS are the game board's (<see cref="GameStageBoard"/>), so the
/// rules call nothing new: an act's <c>Lunge</c> plays the Furina-placed
/// effects once the lunge lands; an act's hit plays the target effects on
/// the enemy it lands on (one per enemy for an act to ALL); a line's
/// <c>LineCue</c> plays Navia's and Chevreuse's on their bodies. A repeated
/// act (Full House's Spend is no act, but Bottled Encore, Showstopper, a
/// Bow and Encore! are) lunges and hits again, so it plays again.
/// Neuvillette's is on the two doors his bonus is added in: a non-card hit
/// (<see cref="ElementalHit.Deal"/>) and her card hits
/// (<see cref="FanfarePower"/>'s <c>AfterDamageGiven</c>).
///
/// NON-BLOCKING AND HEADLESS-SAFE: nothing here is awaited; every lookup is
/// null-guarded, <c>TestMode</c> returns at once, and the whole body is
/// inside a catch, the rule every bridge in this mod is written to.
/// </summary>
public static class FurinaGuestFx
{
    public const string SceneDir = "furina/model";
    public const string SpriteNode = "Fx";
    public const string PlayerNode = "FxPlayer";
    public const string AnchorMeta = "anchor";
    public const string LengthMeta = "length";
    public const string FeetAnchor = "feet";

    /// <summary>The leak guard: a node still standing this long after it
    /// started is freed (the longest effect runs 0.7 s).</summary>
    public const double LeakSeconds = 3.0;

    /// <summary>The guest's file and animation name. Pure.</summary>
    public static string NameOf(StagePerformer who) =>
        who.ToString().ToLowerInvariant();

    /// <summary>The guest's effect scene, relative to the pck. Pure.</summary>
    public static string ScenePath(StagePerformer who) =>
        $"{SceneDir}/guest_fx_{NameOf(who)}.tscn";

    /// <summary>The table above: where <paramref name="who"/>'s effect plays
    /// on <paramref name="trigger"/>, or <see cref="GuestFxPlace.None"/>.
    /// Pure.</summary>
    public static GuestFxPlace PlaceFor(StagePerformer who, GuestFxTrigger trigger) =>
        (who, trigger) switch
        {
            (StagePerformer.Wriothesley or StagePerformer.Lynette or StagePerformer.Clorinde
                or StagePerformer.Lyney or StagePerformer.Escoffier, GuestFxTrigger.Act)
                => GuestFxPlace.Target,
            (StagePerformer.Charlotte or StagePerformer.Sigewinne or StagePerformer.Freminet,
                GuestFxTrigger.Act) => GuestFxPlace.Furina,
            (StagePerformer.Navia or StagePerformer.Chevreuse, GuestFxTrigger.Line)
                => GuestFxPlace.Self,
            (StagePerformer.Neuvillette, GuestFxTrigger.HydroBonus) => GuestFxPlace.Target,
            _ => GuestFxPlace.None,
        };

    /// <summary>Whether a scene's anchor puts it on the creature's feet
    /// rather than its centre. Pure.</summary>
    public static bool OnFeet(string? anchor) => anchor == FeetAnchor;

    /// <summary>Whether Neuvillette's bonus added anything to a hit of
    /// <paramref name="element"/>: his ring plays only then. Pure.</summary>
    public static bool BonusShows(int bonus, Element element) =>
        bonus > 0 && element == Element.Hydro;

    /// <summary>An act's lunge landed: the Furina-placed effects
    /// (Charlotte, Sigewinne, Freminet) play on her.</summary>
    public static void OnAct(Creature? furina, StageSeat? seat)
    {
        if (seat == null) return;
        if (PlaceFor(seat.Who, GuestFxTrigger.Act) == GuestFxPlace.Furina)
        {
            Play(furina, seat.Who);
        }
    }

    /// <summary>An act's hit lands on <paramref name="enemy"/>: the target
    /// effects play there.</summary>
    public static void OnHit(StagePerformer who, Creature? enemy)
    {
        if (PlaceFor(who, GuestFxTrigger.Act) == GuestFxPlace.Target) Play(enemy, who);
    }

    /// <summary>A guest's line fired: Navia's and Chevreuse's play on
    /// their bodies.</summary>
    public static void OnLine(StageSeat? seat)
    {
        if (seat == null) return;
        if (PlaceFor(seat.Who, GuestFxTrigger.Line) == GuestFxPlace.Self) Play(seat.Pet, seat.Who);
    }

    /// <summary>Neuvillette's bonus of <paramref name="bonus"/> was added to
    /// a hit of <paramref name="element"/> on <paramref name="target"/>.
    /// </summary>
    public static void OnHydroBonus(int bonus, Element element, Creature? target)
    {
        if (BonusShows(bonus, element)) Play(target, StagePerformer.Neuvillette);
    }

    private static readonly Dictionary<StagePerformer, PackedScene?> Scenes = new();

    /// <summary>Play <paramref name="who"/>'s effect on
    /// <paramref name="body"/>. Never throws and never waits.</summary>
    private static void Play(Creature? body, StagePerformer who)
    {
        if (body == null || body.IsDead || TestMode.IsOn) return;
        try
        {
            if (NCombatRoom.Instance is not { } room) return;
            var node = room.GetCreatureNode(body);
            if (node == null || !GodotObject.IsInstanceValid(node)) return;
            if (SceneOf(who) is not { } scene) return;
            var fx = scene.Instantiate<Node2D>();
            room.CombatVfxContainer.AddChildSafely(fx);
            var anchor = fx.HasMeta(AnchorMeta) ? fx.GetMeta(AnchorMeta).AsString() : null;
            fx.GlobalPosition = OnFeet(anchor) ? node.GetBottomOfHitbox() : node.VfxSpawnPosition;
            if (fx.GetNodeOrNull<AnimationPlayer>("%" + PlayerNode) is { } player)
            {
                player.AnimationFinished += _ =>
                {
                    if (GodotObject.IsInstanceValid(fx)) fx.QueueFree();
                };
            }
            var tree = room.GetTree();
            if (tree != null)
            {
                tree.CreateTimer(LeakSeconds).Timeout += () =>
                {
                    if (GodotObject.IsInstanceValid(fx)) fx.QueueFree();
                };
            }
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] guest effect {who} skipped: {e.Message}");
        }
    }

    private static PackedScene? SceneOf(StagePerformer who)
    {
        if (Scenes.TryGetValue(who, out var cached)) return cached;
        var path = KleePck.Path(ScenePath(who));
        var scene = path == null ? null : ResourceLoader.Load<PackedScene>(path);
        if (scene == null)
        {
            Log.Warn($"[{KleeMod.ModId}] {ScenePath(who)} missing from pck; its guest effect is off");
        }
        Scenes[who] = scene;
        return scene;
    }
}
