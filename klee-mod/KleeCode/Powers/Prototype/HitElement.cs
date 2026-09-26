using System;
using System.Collections.Generic;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// ONE HIT CARRIES THE ELEMENT, NOT THE WHOLE CARD (the Furina seat round of
/// 2026-09-26, act 2 lane 2).
///
/// THE FIND. Quick Cue's Spend mode ("deal 8 and apply Hydro") hit an enemy
/// wearing Pyro: Vaporize was listed and the 8 landed at face value. The row
/// dealt a plain hit and THEN applied Hydro, so the reaction fired on the
/// application, after the hit, and multiplied nothing. Klee's kit has always
/// done it the other way round (brief rule 5: her Attacks' hits carry Pyro,
/// <c>applies_element: true</c> on the damage op), and the ruling puts
/// Furina's Hydro on the hit the same way.
///
/// WHY A SCOPE AND NOT <see cref="IElementalCard"/>. The card-level interface
/// is one answer for the whole card, and two of the four rows need two
/// answers: Quick Cue and Tidal Flourish deal damage in BOTH modes and only the
/// Spend mode's hit carries Hydro, and Bubble Aria's first hit carries it while
/// its second does not. The sim has always read the element per effect
/// (<c>effects._element_for</c>); this is that answer on the mod's side. A row
/// whose every hit carries the element still takes the interface (Grand
/// Deluge), exactly as Klee's rows do.
///
/// HOW IT IS READ. <see cref="CatalystCadence.PrintedElement"/> asks
/// <see cref="For"/> first, so the carried element is the hit's PRINTED
/// element: every site that asks <c>AuraCmd.ElementOfPlay</c> -- the
/// application listener, <see cref="AuraPower"/>'s reaction multiplier and its
/// lifecycle -- sees it for the span of the one <c>DamageCmd</c> the generated
/// play wraps, and the arm riders still win over it, the order they have over
/// an <see cref="IElementalCard"/>.
///
/// KEYED ON THE CARD, so a hit from any other source inside the span (a
/// reaction's splash, a Bomb, another card's power) is untouched. PREVIEW-SAFE:
/// <see cref="FoldedDamageVar"/> opens the same scope over its own read, so a
/// face whose hit carries Hydro previews the reaction the hit will cause.
///
/// QUARANTINED under <c>Powers/Prototype/</c>, which a release build does not
/// compile; nothing outside a generated prototype row opens it.
/// </summary>
public static class HitElement
{
    private static readonly List<(CardModel Card, Element Element)> Open = new();

    /// <summary>A plain static and not a thread-static one: the play's scope
    /// spans awaits, and a continuation is not promised the thread it left.
    /// The lock is for the headless suite, whose classes run in parallel.</summary>
    private static readonly object Gate = new();

    /// <summary>For the span of the returned scope, a hit from
    /// <paramref name="card"/> carries <paramref name="element"/>.</summary>
    public static IDisposable Carry(CardModel card, Element element)
    {
        lock (Gate) Open.Add((card, element));
        return new Scope(card);
    }

    /// <summary>The element a hit from <paramref name="card"/> carries right
    /// now, or <see cref="Element.None"/> when no scope is open for it. The
    /// innermost scope wins. Pure.</summary>
    public static Element For(CardModel? card)
    {
        if (card == null) return Element.None;
        lock (Gate)
        {
            for (var i = Open.Count - 1; i >= 0; i--)
            {
                if (ReferenceEquals(Open[i].Card, card)) return Open[i].Element;
            }
        }
        return Element.None;
    }

    private sealed class Scope : IDisposable
    {
        private CardModel? _card;

        public Scope(CardModel card)
        {
            _card = card;
        }

        public void Dispose()
        {
            if (_card == null) return;
            lock (Gate)
            {
                for (var i = Open.Count - 1; i >= 0; i--)
                {
                    if (ReferenceEquals(Open[i].Card, _card))
                    {
                        Open.RemoveAt(i);
                        break;
                    }
                }
            }
            _card = null;
        }
    }
}
