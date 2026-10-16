using System;
using System.Runtime.CompilerServices;
using Godot;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;

namespace KleeMod.Vfx;

/// <summary>
/// VARKA'S ELEMENT LAYER (2026-10-13, his model art, phase B). [USER]: "In his
/// case, I think we'd want special animations (effect colors) for the element
/// of his attack - anemo, pyro, hydro, electro or cryo."
///
/// His body is drawn colourless; the slash trails, impact bursts and the
/// Ascension's ground burst are a separate neutral heat layer (R=G=B heat, A
/// coverage) that one ShaderMaterial colours (tools/varka_rig/rig.py). This
/// class sets that material's <c>element</c> as the tree enters a clip that
/// draws the layer, from the element of the card being played, and places the
/// ground burst's second copy under the target.
///
/// THE SCENE CONTRACT: <c>%AttackFx</c>, <c>%AscensionFx</c>,
/// <c>%GroundBurst</c> and <c>%TargetBurst</c>, Sprite2Ds sharing one
/// ShaderMaterial (local to the scene, so two Varkas strike in two colours).
/// The clips themselves show and step them; nothing here animates. Inert for
/// every scene without them, which is every body but his and Furina's.
///
/// FURINA (2026-10-13, her model art, phase B) carries <c>%AttackFx</c> only:
/// her phantom rapier's trail and streak, on the same shader. It rests at
/// Hydro, hers, not at Anemo: the node's <c>rest_element</c> metadata names
/// the colour a play with no element keeps (<see cref="RestElementMeta"/>).
///
/// THE ELEMENT is the played card's own: <see cref="CardPlayMotion"/> notes
/// it as the card's play begins (<see cref="ElementHitFx.ElementOf"/>, the
/// funnel the aura and the hit effect read, so Varka's current element shows),
/// and the next attack or Ascension clip within <see cref="NoteStaleMs"/> takes
/// it. A card with no element, an attack with no card behind it, or a stale
/// note draws Anemo, his own.
///
/// THE GROUND BURST (visual paper, Round 3): "driving one blade into the
/// ground, with a mirrored ground particle effect on him and the target
/// enemy". %GroundBurst sits at the blade's point by the scene; %TargetBurst
/// is moved to the bottom of the noted target's hitbox as the clip starts,
/// and hidden when there is no live target to stand under.
/// </summary>
internal static class ElementTrail
{
    internal const string AttackState = "attack";
    internal const string AscensionState = "ascension";
    internal const string AttackFxNode = "AttackFx";
    internal const string AscensionFxNode = "AscensionFx";
    internal const string GroundBurstNode = "GroundBurst";
    internal const string TargetBurstNode = "TargetBurst";
    internal const string ElementParam = "element";
    internal const string RestElementMeta = "rest_element";

    /// <summary>A note older than this belongs to a play whose clip never
    /// started, not to the clip now starting.</summary>
    internal const ulong NoteStaleMs = 1500;

    private sealed class Note
    {
        public Element Element;
        public Creature? Target;
        public ulong AtMs;
    }

    private static readonly ConditionalWeakTable<Creature, Note> Pending = new();

    /// <summary>
    /// The colour the layer takes for an element: the mod's one element table
    /// (<see cref="ReactionFx.ElementFlashHex"/>), and Anemo for a play that
    /// carries no element. Pure.
    /// </summary>
    internal static string TintHex(Element element)
        => TintHexResting(element, Element.Anemo);

    /// <summary>
    /// The colour for an element on a layer that rests at
    /// <paramref name="rest"/>: the element's own, or the rest colour for a
    /// play that carries none. Pure.
    /// </summary>
    internal static string TintHexResting(Element element, Element rest)
        => ReactionFx.ElementFlashHex(element == Element.None
            ? (rest == Element.None ? Element.Anemo : rest)
            : element);

    /// <summary>The element a layer node rests at, from its
    /// <c>rest_element</c> metadata ("hydro" on Furina's); Anemo, Varka's,
    /// when it names none. Pure.</summary>
    internal static Element RestElementOf(string? meta)
        => meta != null && Enum.TryParse<Element>(meta, ignoreCase: true, out var e) && e != Element.None
            ? e
            : Element.Anemo;

    /// <summary>
    /// Whether a travel colours the layer: a fresh entry into a clip that
    /// draws it. A second attack trigger while the clip runs is a no-op
    /// travel, and keeps the colour it started with. Pure.
    /// </summary>
    internal static bool Tints(string? fromState, string toState)
        => toState != fromState && toState is AttackState or AscensionState;

    /// <summary>Whether a travel places the ground burst under the target:
    /// a fresh entry into the Ascension. Pure.</summary>
    internal static bool PlacesTargetBurst(string? fromState, string toState)
        => toState != fromState && toState == AscensionState;

    /// <summary>The layer nodes a clip colours. The ground bursts share the
    /// material, so colouring them with the Ascension's own is the same
    /// call. Pure.</summary>
    internal static string[] NodesFor(string state) => state switch
    {
        AttackState => new[] { AttackFxNode },
        AscensionState => new[] { AscensionFxNode, GroundBurstNode, TargetBurstNode },
        _ => Array.Empty<string>(),
    };

    /// <summary>
    /// Called by <see cref="CardPlayMotion"/> as every play begins, before
    /// any trigger it or the card sends. Never throws: a colour must never
    /// cost a card play.
    /// </summary>
    public static void NotePlay(Creature creature, CardModel card, Creature? target)
    {
        try
        {
            Pending.AddOrUpdate(creature, new Note
            {
                Element = ElementHitFx.ElementOf(card),
                Target = target,
                AtMs = Time.GetTicksMsec(),
            });
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] element trail note skipped: {e.Message}");
        }
    }

    /// <summary>
    /// Called by <see cref="CreatureAnimationRouter"/> after every travel.
    /// </summary>
    public static void OnTravel(NCreature creature, string? fromState, string toState)
    {
        if (!Tints(fromState, toState))
        {
            return;
        }
        try
        {
            Apply(creature, toState, PlacesTargetBurst(fromState, toState));
        }
        catch (Exception e)
        {
            Log.Warn($"[{KleeMod.ModId}] element trail skipped: {e.Message}");
        }
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    private static void Apply(NCreature creature, string state, bool placeTarget)
    {
        var visuals = creature.Visuals;
        var entity = creature.Entity;
        if (visuals == null || entity == null || !GodotObject.IsInstanceValid(visuals))
        {
            return;
        }

        Note? note = null;
        if (Pending.TryGetValue(entity, out var noted)
            && Time.GetTicksMsec() - noted.AtMs <= NoteStaleMs)
        {
            note = noted;
        }
        foreach (var name in NodesFor(state))
        {
            var node = visuals.GetNodeOrNull<CanvasItem>("%" + name);
            if (node?.Material is ShaderMaterial material)
            {
                var rest = RestElementOf(node.HasMeta(RestElementMeta)
                    ? node.GetMeta(RestElementMeta).AsString()
                    : null);
                var tint = new Color(TintHexResting(note?.Element ?? Element.None, rest));
                material.SetShaderParameter(ElementParam, tint);
            }
        }

        if (placeTarget
            && visuals.GetNodeOrNull<Node2D>("%" + TargetBurstNode) is { } burst)
        {
            var under = note?.Target is { IsAlive: true } target
                        && NCombatRoom.Instance?.GetCreatureNode(target) is { } targetNode
                        && GodotObject.IsInstanceValid(targetNode)
                ? targetNode.GetBottomOfHitbox()
                : (Vector2?)null;
            burst.Visible = under.HasValue;
            if (under.HasValue)
            {
                burst.GlobalPosition = under.Value;
            }
        }
    }
}
