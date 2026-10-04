using KleeMod.Cards;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE ELEMENT BELONGS TO THE CARD, NOT TO WHOEVER PLAYS IT.
///
/// [USER], 2026-10-05: "I think that that Kokomi effect is a legacy design. We
/// changed things (or tried to change them) so that that effect just lives in
/// the card pool as a symbol on relevant elemental cards and the card states
/// 'deals [element] damage' or 'applies [element]'."
///
/// So a card applies exactly the element it DECLARES -- <see cref="HitElement"/>
/// for a hit that carries its own, else <see cref="IElementalCard"/> -- and a
/// card that declares neither applies nothing, whoever holds it. The codegen
/// reads each kit's cadence ONCE, at emit time, and writes it onto that kit's
/// own rows as <see cref="IElementalCard"/> and the gem keyword
/// (`tools/gen_klee_cards.py`, <c>CharacterProfile.damage_applies_element</c>),
/// so the card and its face are one declaration.
///
/// WHAT THIS REPLACED. Until 2026-10-05 a card that declared nothing fell back
/// to the DEALER's element (`EB-307`, written when R242 put the base game's
/// Strike into both arms' starters): Pyro in Klee's hand, Hydro in Kokomi's,
/// and R276 pick 2 widened Kokomi's half to every damaging card of hers.
/// Off-character play made that a trap: Furina's plain Attacks applied Pyro for
/// Klee and Hydro for Kokomi with no element on the face, and in combat the gem
/// (<c>KleeCardTooltips.AppliedElement</c>, which reads this funnel) drew a
/// Hydro gem on element-less cards Kokomi held. The two Skills of hers that
/// relied on the widening, Opening Gambit and Second Wave, print Hydro and now
/// declare it on the sheet. The base game's cards were already outside the
/// fallback ("Those cards are supposed to be bad!", 2026-09-02); now nothing
/// is inside it. Sim twin: <c>tier0/engine/effects.printed_element</c>.
///
/// Riders still override what the card prints:
/// <c>CompanionOverhaulRiders.ElementFor</c> reads this, then its riders.
///
/// PURE, because <c>AuraCmd.ElementOfPlay</c> is reached from preview paths.
/// </summary>
public static class CatalystCadence
{
    /// <summary>
    /// What element this card PRINTS, before any rider. Who plays it is never
    /// asked.
    /// </summary>
    public static Element PrintedElement(CardModel? cardSource)
    {
        // The Furina seat round (2026-09-26): a row whose element rides ONE of
        // its hits rather than the whole card. See `HitElement`.
        var carried = HitElement.For(cardSource);
        if (carried != Element.None) return carried;
        return cardSource is IElementalCard elemental
            ? elemental.Element
            : Element.None;
    }
}
