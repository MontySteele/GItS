using System;
using System.Threading;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;

namespace KleeMod.Diagnostics;

/// <summary>
/// WHO A DEALER-LESS HIT BELONGS TO, for the play telemetry and nothing else.
///
/// THE GAP (the Klee+Varka co-op fact-check, 2026-10-02). <see cref="PlayTelemetry"/>
/// credited a hit to a seat only when the engine named that seat's own
/// creature as the dealer. Every element hit (<c>ElementalHit</c>), every
/// reaction (<c>ReactionEffects</c>), every Bomb and Mine and every Furina act
/// reaches <c>CreatureCmd.Damage</c> with <c>dealer: null</c> ON PURPOSE --
/// a dealer would make the hit a powered attack, early-detonate Bombs and
/// trip attack hooks -- so in that run the credited damage covered 36% of the
/// enemies' HP plus Block, and 29% in bosses.
///
/// THE FIX LEAVES THE ENGINE'S ARGUMENT ALONE. The paths that know their owner
/// open a scope around the hit; the telemetry hook reads it. A scope is an
/// <see cref="AsyncLocal{T}"/>, so it flows down the awaited call chain into
/// <c>CreatureCmd.Damage</c> and the hook listeners it runs, and an async
/// method's change never leaks back to its caller. It touches no game object,
/// consumes no RNG and changes no argument: rule 1 of
/// <see cref="PlayTelemetry"/>.
///
/// TWO STRENGTHS. <see cref="Open"/> replaces whatever is open (a reaction
/// inside a Bomb is a reaction). <see cref="OpenIfNone"/> keeps an outer
/// scope (an element hit inside a Bomb or a jellyfish's Plan stays a Bomb or
/// a pet hit), which is how <c>ElementalHit</c> -- the funnel every one of
/// those paths shares -- can label its own hits without relabelling theirs.
///
/// OPEN SCOPES ONLY IN AN <c>async</c> METHOD. A synchronous method that sets
/// an <see cref="AsyncLocal{T}"/> and returns a Task hands the value to its
/// caller; an async method does not.
/// </summary>
public static class DamageCredit
{
    /// <summary>The engine named the seat's own creature as the dealer.</summary>
    public const string Direct = "direct";

    /// <summary>An element-tagged non-attack hit (<c>ElementalHit.Deal</c>).</summary>
    public const string Element = "element";

    /// <summary>A reaction's own damage: Overload's splash, Swirl's flat hit,
    /// Shatter.</summary>
    public const string Reaction = "reaction";

    /// <summary>A pet's hit: the Bake-Kurage's Plan, Furina's performers, or
    /// any creature whose <c>PetOwner</c> is a seat.</summary>
    public const string Pet = "pet";

    /// <summary>A Bomb or a Mine going off (the label says which).</summary>
    public const string Bomb = "bomb";

    /// <summary>An unelemented non-attack hit off a power or relic
    /// (<c>ElementalHit.DealUnelemented</c>).</summary>
    public const string Power = "power";

    /// <summary>One open scope: the seat it credits, the kind, and a label
    /// that stands in for a card name when the hit has no card.</summary>
    public sealed record Frame(Player? Owner, string Kind, string? Label);

    private static readonly AsyncLocal<Frame?> _current = new();

    /// <summary>The innermost open scope on this call chain, or null.</summary>
    public static Frame? Current => _current.Value;

    /// <summary>Restores the scope that was open before; a default value
    /// (nothing was opened) restores nothing.</summary>
    public readonly struct Scope : IDisposable
    {
        private readonly Frame? _prior;
        private readonly bool _set;

        internal Scope(Frame? prior)
        {
            _prior = prior;
            _set = true;
        }

        public void Dispose()
        {
            if (_set) _current.Value = _prior;
        }
    }

    /// <summary>Opens a scope that replaces any open one. The owner is
    /// <paramref name="source"/>'s seat (a pet answers its owner), or the
    /// outer scope's owner when the source names none.</summary>
    public static Scope Open(Creature? source, string kind, string? label = null)
    {
        try
        {
            var prior = _current.Value;
            _current.Value = new Frame(OwnerOf(source) ?? prior?.Owner, kind, label);
            return new Scope(prior);
        }
        catch (Exception)
        {
            return default;
        }
    }

    /// <summary>Opens a scope only when none is open, so an outer Bomb, pet
    /// or reaction scope keeps its kind and its owner.</summary>
    public static Scope OpenIfNone(Creature? source, string kind, string? label = null)
    {
        if (_current.Value != null) return default;
        return Open(source, kind, label);
    }

    /// <summary>The seat a creature's damage belongs to: a pet's owner, else
    /// the creature's own player, else nobody (an enemy).</summary>
    public static Player? OwnerOf(Creature? creature)
    {
        if (creature == null) return null;
        try
        {
            return creature.PetOwner ?? creature.Player;
        }
        catch (Exception)
        {
            return null;
        }
    }
}
