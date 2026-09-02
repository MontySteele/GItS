using KleeMod.Cards;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// THE ELEMENT BELONGS TO THE CHARACTER, NOT TO THE CARD (`EB-307`, R242).
///
/// WHAT BROKE. R242 replaced both overhaul arms' renamed basics with the BASE
/// GAME's Strike and Defend. A base card is <c>public sealed</c> and knows
/// nothing about this mod, so it can never implement <see cref="IElementalCard"/>
/// -- and the mod's whole answer to "what does this hit apply?" was
/// <c>cardSource is IElementalCard</c>. A base Strike played by Klee would have
/// applied NO Pyro, silently, and half of rule 5 ("her Attacks are ordinary
/// Pyro hits, so every shared reaction applies with nothing printed") would
/// have been true only of the cards this mod happens to have authored.
///
/// THE SIM HAS ALWAYS DISAGREED WITH THE MOD HERE, and the sim is right.
/// <c>tier0/engine/effects._element_for</c> reads the PLAYER's cadence: a
/// catalyst character's damaging Attack applies <c>state.player.element</c>
/// whenever the CARD names none. Both Klee and Kokomi are
/// <c>cadence="catalyst_attack"</c> (`tools/gen_klee_cards.py`
/// <c>KLEE_PROFILE</c> / <c>KOKOMI_PROFILE</c>). The mod got away with the
/// per-card read only because the codegen puts <see cref="IElementalCard"/> on
/// every Attack it emits for those two, which made a character rule look like a
/// card property. It is not one, and a base card is the proof.
///
/// THE PREDICATE IS "SAYS NOTHING ABOUT ELEMENTS", not "declares None". Two
/// kinds of card must NOT be caught by this:
///
///   * a row that declares <see cref="Element.None"/> on purpose -- Kirara is
///     Dendro, this engine has no Dendro aura, and her companion row prints no
///     element at all. She IS an <see cref="IElementalCard"/>, so the first
///     branch answers her and the fallback never runs.
///   * any <see cref="ICompanionCard"/>. Companions are exempt from cadence in
///     both engines (the sim: "Companion cards are exempt from cadence
///     entirely: what a companion applies is the sheet's explicit call"), and a
///     companion Attack whose damage is all <c>applies_element: false</c> gets
///     no <see cref="IElementalCard"/> from the codegen -- so without this
///     second guard the fallback would hand it Klee's Pyro.
///
/// SCOPED TO THE TWO ARMS AND TO THEIR OWN CHARACTERS. The fallback reads
/// <c>KleeOverhaul.Enabled</c> / <c>KokomiOverhaul.Enabled</c> and the DEALER's
/// identity interface, so a flag-off build -- and any build's Furina, who is
/// Skill-grade and not catalyst -- is byte for byte what it was. Pinned by
/// <c>KleeTests/Prototype/BaseBasicsTests.cs</c> rather than assumed.
///
/// PURE, because <c>AuraCmd.ElementOfPlay</c> is reached from preview paths.
/// </summary>
public static class CatalystCadence
{
    /// <summary>
    /// What element this card PRINTS for this dealer, before any rider.
    ///
    /// This is the expression <c>AuraCmd.ElementOfPlay</c> and
    /// <c>CompanionOverhaulRiders.ElementFor</c> used to write inline as
    /// <c>cardSource is IElementalCard e ? e.Element : Element.None</c>, plus
    /// the character fallback for a card that declares nothing.
    /// </summary>
    public static Element PrintedElement(CardModel? cardSource, Creature? dealer)
    {
        if (cardSource is IElementalCard elemental) return elemental.Element;
        if (cardSource is ICompanionCard) return Element.None;
        if (cardSource is not { Type: CardType.Attack }) return Element.None;
        return NativeElementOf(dealer);
    }

    /// <summary>
    /// The dealer's own element, IF the dealer is a catalyst character whose
    /// overhaul arm is live. <see cref="Element.None"/> for everyone else,
    /// which is every creature in a flag-off build.
    ///
    /// The elements are literals rather than mirrored constants on purpose:
    /// they are the roster's declared identity (`tier0/roster.py`, STATE's
    /// roster table -- Klee Pyro, Kokomi Hydro), not a balance number, so
    /// `tools/lint_constant_parity.py` has nothing to compare and inventing a
    /// number-shaped constant for a name would only hide that.
    /// </summary>
    private static Element NativeElementOf(Creature? dealer)
    {
        var character = dealer?.Player?.Character;
        if (character == null) return Element.None;
        if (KleeOverhaul.Enabled && character is IKleeCharacter) return Element.Pyro;
        if (KokomiOverhaul.Enabled && character is IKokomiCharacter) return Element.Hydro;
        return Element.None;
    }
}
