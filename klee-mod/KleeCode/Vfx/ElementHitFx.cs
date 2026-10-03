using System;
using System.Runtime.CompilerServices;
using Godot;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Commands.Builders;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.TestSupport;

// Namespace `KleeMod`, not `KleeMod.Vfx`: the generated cards already import
// `KleeMod`, so `.WithElementHitFx(this)` needs no new using in 300 files.
namespace KleeMod;

/// <summary>
/// THE ONE DOOR A HIT'S LOOK GOES THROUGH (2026-10-02, the combat visual audit,
/// gap 3: "every hit looks the same"). A card's element picks its hit effect,
/// reusing the base game's own scenes, so no art is new:
///
/// | element | base effect                                   | base precedent  |
/// |---------|-----------------------------------------------|-----------------|
/// | Pyro    | <c>NFireBurstVfx</c> at the target's feet     | Cinder          |
/// | Hydro   | <c>NSplashVfx</c>, water blue                 | Bouncing Flask  |
/// | Electro | <c>vfx/vfx_attack_lightning</c>               | Globe Head      |
/// | Cryo    | <c>vfx/vfx_starry_impact</c> + pale ice splash | Regent stars    |
/// | Anemo   | <c>vfx/vfx_flying_slash</c>                   | base slashes    |
/// | Geo     | <c>vfx/vfx_rock_shatter</c>                   | Giant Rock      |
/// | none    | <c>vfx/vfx_attack_slash</c> (unchanged)       | Strike          |
///
/// The element enum has no Dendro, so there is no Dendro row; were one added,
/// <c>NSporeImpactVfx</c> in green is the base scene that fits.
///
/// Every scene named here is in <c>VfxCmd.AssetPaths</c>, which the game
/// preloads for every combat, so the switch costs no load. None of it waits:
/// the hit's timing is the base game's.
///
/// The mapping is PURE (<see cref="For"/>) so a headless test can read it;
/// the spawning half returns null in <c>TestMode</c>, as the base factories do.
/// </summary>
public static class ElementHitFx
{
    /// <summary>The slash every hit used before this door existed.</summary>
    public const string SlashPath = "vfx/vfx_attack_slash";

    /// <summary>A node the base game builds by factory rather than by path.</summary>
    public enum HitNode
    {
        None,
        FireBurst,
        Splash,
    }

    /// <summary>One element's hit: a path scene, a factory node, the node's
    /// tint as hex. Either half may be absent.</summary>
    public readonly record struct Spec(string? ScenePath, HitNode Extra, string? TintHex);

    public const string HydroTint = "#3fa9ff";
    public const string CryoTint = "#cdf3ff";

    /// <summary>The element-to-effect table above.</summary>
    public static Spec For(Element element) => element switch
    {
        Element.Pyro => new Spec(null, HitNode.FireBurst, null),
        Element.Hydro => new Spec(null, HitNode.Splash, HydroTint),
        Element.Electro => new Spec("vfx/vfx_attack_lightning", HitNode.None, null),
        Element.Cryo => new Spec("vfx/vfx_starry_impact", HitNode.Splash, CryoTint),
        Element.Anemo => new Spec("vfx/vfx_flying_slash", HitNode.None, null),
        Element.Geo => new Spec("vfx/vfx_rock_shatter", HitNode.None, null),
        _ => new Spec(SlashPath, HitNode.None, null),
    };

    /// <summary>The element this card's hit carries right now: the same one
    /// funnel the aura and the reaction read (<c>AuraCmd.ElementOfPlay</c>),
    /// so a one-hit <c>HitElement</c> scope, Varka's current element and the
    /// companion riders all show. None for a card that carries none.</summary>
    public static Element ElementOf(CardModel? card) =>
        card == null ? Element.None
                     : Powers.AuraCmd.ElementOfPlay(card, card.Owner?.Creature);

    /// <summary>The attack builder's hit effect, chosen by the card's element.
    /// Replaces <c>.WithHitFx("vfx/vfx_attack_slash")</c>.</summary>
    public static AttackCommand WithElementHitFx(this AttackCommand cmd, CardModel? card) =>
        cmd.WithElementHitFx(ElementOf(card));

    public static AttackCommand WithElementHitFx(this AttackCommand cmd, Element element)
    {
        var spec = For(element);
        // A null path still clears the builder's hit scene, exactly as Cinder
        // (no WithHitFx at all) leaves it.
        cmd.WithHitFx(spec.ScenePath);
        if (spec.Extra != HitNode.None)
        {
            cmd.WithHitVfxNode(target => CreateNode(spec, target));
        }
        return cmd;
    }

    /// <summary>
    /// The same look for a hit that is not an attack (bombs, performers,
    /// Plans, every <c>ElementalHit.Deal</c>), which otherwise draws only the
    /// engine's generic spark. Fire and forget.
    /// </summary>
    public static void SpawnOn(Creature target, Element element)
    {
        if (element == Element.None || TestMode.IsOn) return;
        try
        {
            SpawnLive(target, For(element));
        }
        catch (Exception)
        {
            // A visual never breaks a hit.
        }
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    private static void SpawnLive(Creature target, Spec spec)
    {
        if (target.IsDead) return;
        if (spec.ScenePath != null)
        {
            VfxCmd.PlayOnCreatureCenter(target, spec.ScenePath);
        }
        if (spec.Extra != HitNode.None)
        {
            target.GetVfxContainer()?.AddChildSafely(CreateNode(spec, target));
        }
    }

    /// <summary>The factory half; null when there is no live body.</summary>
    internal static Node2D? CreateNode(Spec spec, Creature target)
    {
        if (TestMode.IsOn) return null;
        var node = target.GetCreatureNode();
        if (node == null) return null;
        return spec.Extra switch
        {
            HitNode.FireBurst => NFireBurstVfx.Create(target, 0.75f),
            HitNode.Splash => NSplashVfx.Create(
                node.VfxSpawnPosition, new Color(spec.TintHex ?? "#ffffff")),
            _ => null,
        };
    }
}
