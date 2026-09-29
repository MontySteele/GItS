using System;
using System.Collections.Generic;
using KleeMod.Cards;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>What kind of source caused a reaction (the element port, §7.3).</summary>
public enum ReactionSourceKind
{
    /// <summary>No card was resolving: a Bomb at turn start, a power's
    /// turn-end volley, a performer, a relic, a Core on its timer.</summary>
    Automatic = 0,
    /// <summary>A card's play (a Set off inside it included).</summary>
    Card,
    /// <summary>A Companion card's play.</summary>
    Companion,
}

/// <summary>
/// One reaction, as every listener sees it: what fired, on whom, who dealt it,
/// and from what kind of source.
///
/// A CO-OP PARTNER IS NOT A KIND OF SOURCE; it is a relation between the
/// dealer and whoever is listening, so the event carries the dealer and
/// <see cref="IsPartnerOf"/> answers it for a given listener. Tier 0 seats one
/// player and has no partner at all.
/// </summary>
public readonly record struct ReactionEvent(
    Reaction Reaction, Creature Target, Creature? Dealer,
    ReactionSourceKind Source)
{
    /// <summary>Did another player's creature cause this, seen from
    /// <paramref name="listener"/>? False for no dealer, for the listener
    /// itself, and for a dealer that is not a player.</summary>
    public bool IsPartnerOf(Creature? listener) =>
        Dealer?.Player != null && listener != null
        && !ReferenceEquals(Dealer, listener);
}

/// <summary>
/// THE ONE REACTION EVENT (<c>review/ruled/element-home-review-2026-09-28.md</c>
/// §7.3): "Every reaction reports what fired, on whom, and from what source
/// ... shaped so that a later listener (Nahida's Purification, Varka's Winds)
/// needs no new hook."
///
/// Raised from <c>ReactionEffects.Resolve</c>, the single site every reaction
/// in the mod passes, once per named reaction. The listeners that predate it
/// (<see cref="ReactionLog"/>, the Courtroom Drama gate, the companion
/// overhaul's readers, the Stage's Tide of Applause, the Burst credit) keep
/// their direct calls; a new listener subscribes to <see cref="Reacted"/>.
///
/// Sim twin: the <c>reaction</c> event <c>reactions._react</c> emits, whose
/// <c>source_kind</c> key is <c>reactions.reaction_source_kind</c>.
/// </summary>
public static class ReactionEvents
{
    /// <summary>Every named reaction, in resolution order.</summary>
    public static event Action<ReactionEvent>? Reacted;

    /// <summary>The cards whose plays are resolving now, innermost last.
    /// Pushed from <c>KleeElementalHooks.BeforeCardPlayed</c>, popped from
    /// <c>AfterCardPlayed</c>, cleared at combat start.</summary>
    private static readonly List<CardModel> Resolving = new();

    public static void CardPlayBegins(CardModel card) => Resolving.Add(card);

    public static void CardPlayEnds(CardModel card)
    {
        var i = Resolving.LastIndexOf(card);
        if (i >= 0) Resolving.RemoveAt(i);
    }

    public static void ResetFight() => Resolving.Clear();

    /// <summary>
    /// The kind of source for a reaction with this <paramref name="cardSource"/>
    /// (an attack's own card), or else the card whose play is resolving. Pure.
    /// Sim twin: <c>reactions.reaction_source_kind</c>.
    /// </summary>
    public static ReactionSourceKind SourceKindFor(CardModel? cardSource)
    {
        var card = cardSource ?? (Resolving.Count > 0 ? Resolving[^1] : null);
        return card switch
        {
            null => ReactionSourceKind.Automatic,
            ICompanionCard => ReactionSourceKind.Companion,
            _ => ReactionSourceKind.Card,
        };
    }

    internal static void Raise(Reaction reaction, Creature target,
                               Creature? dealer, CardModel? cardSource)
    {
        if (reaction == Reaction.None) return;
        Reacted?.Invoke(new ReactionEvent(
            reaction, target, dealer, SourceKindFor(cardSource)));
    }
}
