using System;
using System.Runtime.CompilerServices;
using Godot;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes.Vfx;
using MegaCrit.Sts2.Core.TestSupport;

namespace KleeMod.Vfx;

/// <summary>
/// A REACTION'S VISIBLE BEAT (2026-10-02, the combat visual audit, gap 3:
/// "elemental reactions draw nothing"). One base-game effect on the target
/// plus a short coloured flash of its body, called once from the single site
/// every reaction resolves in (<c>ReactionEffects.Resolve</c>).
///
/// | reaction        | base effect                               | flash        |
/// |-----------------|-------------------------------------------|--------------|
/// | Vaporize        | steam-white <c>NSplashVfx</c>             | warm orange  |
/// | Melt            | small <c>NFireBurstVfx</c>, pale tint     | amber        |
/// | Overload        | full <c>NFireBurstVfx</c>, magenta tint   | magenta      |
/// | Superconduct    | <c>vfx/vfx_attack_lightning</c>           | ice violet   |
/// | Electro-Charged | lightning + violet splash                 | violet       |
/// | Frozen          | ice-white <c>NSplashVfx</c>               | ice blue     |
/// | Swirl           | <c>vfx/vfx_flying_slash</c>               | the swirled element's colour |
/// | Crystallize     | <c>vfx/vfx_rock_shatter</c>               | gold         |
///
/// NOTHING HERE WAITS. The beat is fire and forget: the flash is a
/// <see cref="FlashSeconds"/> tween on the target's visuals and the effect
/// scenes free themselves, so a reaction adds no time to the base game's
/// pacing (the brief allows 0.2 s; this spends none of it on the clock).
/// The table is PURE (<see cref="For"/>) so a headless test can read it.
/// </summary>
public static class ReactionFx
{
    /// <summary>Flash length, in and out. Under the 0.2 s budget.</summary>
    public const float FlashSeconds = 0.18f;

    public enum Effect
    {
        None,
        Splash,
        FireBurstSmall,
        FireBurstLarge,
        Lightning,
        LightningSplash,
        FlyingSlash,
        RockShatter,
    }

    /// <summary>One reaction's beat: the effect, its tint, the flash colour
    /// (hex; an HDR multiply on the body, so channels above 1 brighten).</summary>
    public readonly record struct Beat(Effect Effect, string? TintHex, string FlashHex);

    /// <summary>The flash colour per element, for Swirl's "the colour of
    /// what it spread".</summary>
    public static string ElementFlashHex(Element element) => element switch
    {
        Element.Pyro => "#ff9a5c",
        Element.Hydro => "#5cb8ff",
        Element.Electro => "#c08cff",
        Element.Cryo => "#a8f0ff",
        Element.Geo => "#ffd36b",
        _ => "#8fffd6",   // Anemo teal
    };

    /// <summary>The reaction table above. <paramref name="consumedAura"/>
    /// colours Swirl.</summary>
    public static Beat For(Reaction reaction, Element consumedAura = Element.None) => reaction switch
    {
        Reaction.Vaporize => new Beat(Effect.Splash, "#f2f7ff", "#ffb36b"),
        Reaction.Melt => new Beat(Effect.FireBurstSmall, "#ffd2a0", "#ffc070"),
        Reaction.Overload => new Beat(Effect.FireBurstLarge, "#ff5ac8", "#ff6fd0"),
        Reaction.Superconduct => new Beat(Effect.Lightning, null, "#b9a7ff"),
        Reaction.ElectroCharged => new Beat(Effect.LightningSplash, "#b48cff", "#a77bff"),
        Reaction.Frozen => new Beat(Effect.Splash, "#e2f9ff", "#9fe8ff"),
        Reaction.Swirl => new Beat(Effect.FlyingSlash, null, ElementFlashHex(consumedAura)),
        Reaction.Crystallize => new Beat(Effect.RockShatter, null, "#ffd36b"),
        _ => new Beat(Effect.None, null, "#ffffff"),
    };

    /// <summary>Play the beat on <paramref name="target"/>. Never throws,
    /// never waits, does nothing headless.</summary>
    public static void Play(Reaction reaction, Creature target, Element consumedAura)
    {
        if (reaction == Reaction.None || TestMode.IsOn) return;
        try
        {
            PlayLive(For(reaction, consumedAura), target);
        }
        catch (Exception)
        {
            // A visual never breaks a reaction.
        }
    }

    private const string FlashMetaKey = "gits_reaction_flash_base";

    [MethodImpl(MethodImplOptions.NoInlining)]
    private static void PlayLive(Beat beat, Creature target)
    {
        if (target.IsDead) return;
        var creatureNode = target.GetCreatureNode();
        if (creatureNode == null) return;
        var container = target.GetVfxContainer();
        var tint = beat.TintHex != null ? new Color(beat.TintHex) : Colors.White;

        switch (beat.Effect)
        {
            case Effect.Splash:
                container?.AddChildSafely(NSplashVfx.Create(creatureNode.VfxSpawnPosition, tint));
                break;
            case Effect.FireBurstSmall:
                container?.AddChildSafely(NFireBurstVfx.Create(creatureNode.GetBottomOfHitbox(), 0.55f, tint));
                break;
            case Effect.FireBurstLarge:
                container?.AddChildSafely(NFireBurstVfx.Create(creatureNode.GetBottomOfHitbox(), 1.0f, tint));
                break;
            case Effect.Lightning:
                VfxCmd.PlayOnCreatureCenter(target, "vfx/vfx_attack_lightning");
                break;
            case Effect.LightningSplash:
                VfxCmd.PlayOnCreatureCenter(target, "vfx/vfx_attack_lightning");
                container?.AddChildSafely(NSplashVfx.Create(creatureNode.VfxSpawnPosition, tint));
                break;
            case Effect.FlyingSlash:
                VfxCmd.PlayOnCreatureCenter(target, "vfx/vfx_flying_slash");
                break;
            case Effect.RockShatter:
                VfxCmd.PlayOnCreatureCenter(target, "vfx/vfx_rock_shatter");
                break;
        }

        Flash(creatureNode.Visuals, new Color(beat.FlashHex));
    }

    /// <summary>
    /// Tint the body toward <paramref name="flash"/> and back. The resting
    /// modulate is remembered on the node the first time, so two reactions
    /// in one hit (a Swirl spreading) cannot leave the body stuck tinted.
    /// </summary>
    private static void Flash(Node2D? visuals, Color flash)
    {
        if (visuals == null || !GodotObject.IsInstanceValid(visuals)) return;
        var rest = visuals.HasMeta(FlashMetaKey)
            ? visuals.GetMeta(FlashMetaKey).AsColor()
            : visuals.Modulate;
        visuals.SetMeta(FlashMetaKey, rest);
        // Brighten as well as tint: modulate multiplies, so lift the colour
        // above 1 for a readable pop on a dark body.
        // Colour channels only: alpha belongs to the death and revive fades.
        var up = FlashSeconds * 0.3f;
        var down = FlashSeconds * 0.7f;
        var tween = visuals.CreateTween().SetParallel(true);
        tween.TweenProperty(visuals, "modulate:r", flash.R * 1.6f, up);
        tween.TweenProperty(visuals, "modulate:g", flash.G * 1.6f, up);
        tween.TweenProperty(visuals, "modulate:b", flash.B * 1.6f, up);
        tween.Chain().TweenProperty(visuals, "modulate:r", rest.R, down);
        tween.TweenProperty(visuals, "modulate:g", rest.G, down);
        tween.TweenProperty(visuals, "modulate:b", rest.B, down);
        tween.Chain();
        tween.TweenCallback(Callable.From(() =>
        {
            if (GodotObject.IsInstanceValid(visuals)) visuals.RemoveMeta(FlashMetaKey);
        }));
    }
}
