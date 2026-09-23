using BaseLib.Abstracts;
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
/// R276 PICK 2 WIDENED KOKOMI'S HALF TO EVERY DAMAGING CARD OF HERS, Skills
/// included; Klee's stays Attack-only. See
/// <see cref="EveryDamagingCardCarriesElement"/>.
///
/// SCOPED TO THE TWO ARMS AND TO THEIR OWN CHARACTERS. The fallback reads
/// <c>KleeOverhaul.Enabled</c> / <c>KokomiOverhaul.Enabled</c> and the DEALER's
/// identity interface, so a flag-off build -- and any build's Furina, who is
/// Skill-grade and not catalyst -- is byte for byte what it was. Pinned by
/// <c>KleeTests/Prototype/BaseBasicsTests.cs</c> rather than assumed.
///
/// EVERY OFF-SHEET CARD IS OUTSIDE IT ([USER], 2026-09-02: "I think we
/// actually SHOULD remove the elemental application from the basic Strikes for
/// all characters. Those cards are supposed to be bad!"). `EB-307` read R242's
/// swap as "her Strikes must keep applying Pyro"; the ruling is the other
/// reading of the same swap -- the base Strike is the base game's card, weak on
/// purpose, and the element is what her OWN Attacks are for.
///
/// `EB-331` WIDENED IT FROM THE BASICS TO EVERY CARD THIS MOD DID NOT WRITE.
/// `Breakthrough`, an Ironclad event card, put `Hydro Aura 2` on three enemies
/// in a Kokomi run and the next Electro hit reacted with nothing on screen to
/// predict it (r4c act 2b finding 6). R244 ruled the base Strike applies
/// nothing BECAUSE IT PRINTS NOTHING, and that reading does not stop at a
/// rarity: a face with no element on it promises none, whether the run handed
/// it over as a starter, a reward, an event or a curse. See
/// <see cref="IsOffSheet"/>.
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
        if (cardSource is null) return Element.None;
        if (cardSource.Type != CardType.Attack
            && !EveryDamagingCardCarriesElement(dealer)) return Element.None;
        if (IsOffSheet(cardSource)) return Element.None;
        return NativeElementOf(dealer);
    }

    /// <summary>
    /// R276 PICK 2: KOKOMI'S ARM ELEMENTS EVERY DAMAGING CARD OF HERS, Skills
    /// included, not only her Attacks. Five of her Skills dealt damage face-up
    /// and applied nothing (Ambush, War Council, Opening Gambit, Chain of
    /// Command, Kurage's Oath's now-line) while her Attacks applied Hydro, and
    /// the split was a trap when reading a card. The base game's cards still
    /// apply nothing -- <see cref="IsOffSheet"/> is asked after this -- and a
    /// companion is answered above.
    ///
    /// SCOPED TO HER ARM AND TO HER. Klee's arm keeps the Attack-only rule
    /// (her cadence is unmoved), and a flag-off build never reaches the
    /// Kokomi branch. The call sites only ask about a DAMAGE hit, so "any
    /// type" here means "any card of hers that deals damage".
    ///
    /// Twins: <c>tier0/engine/effects._every_damaging_card_carries_element</c>
    /// and the codegen's <c>gen_klee_cards.CATALYST_EVERY_CARD</c>, which puts
    /// <see cref="IElementalCard"/> (and the gem) on the same rows.
    /// </summary>
    public static bool EveryDamagingCardCarriesElement(Creature? dealer) =>
        KokomiOverhaul.Enabled
        && dealer?.Player?.Character is IKokomiCharacter;

    /// <summary>
    /// A card this mod did not write: the base game's own, at any rarity --
    /// Strike and Defend, a colorless, an event card, a curse.
    ///
    /// ONE TEST NOW, AND IT IS THE ONE THAT WAS ALWAYS DOING THE WORK.
    /// <c>CustomCardModel</c> is what every card this mod authors derives
    /// from, so it says "the base game wrote this" in one clause. `EB-331`
    /// deleted the second test: <c>CardRarity.Basic</c> was keeping a base
    /// colorless or EVENT card INSIDE the cadence, which is exactly the face
    /// the r4c seat could not predict a reaction off.
    ///
    /// AN ANCIENT AND A COMPANION ARE BOTH THIS MOD'S CLASSES, so neither is
    /// swept: `JumpyDumptyMkOmega` declares <c>Element.Pyro</c> outright and an
    /// <c>ICompanionCard</c> is answered two lines above this call. The sim's
    /// twin, <c>tier0/engine/effects._is_off_sheet_card</c>, needs three
    /// clauses for the same set because a row has no class to ask -- it names
    /// `rarity: ancient` and the companion flag and compares the row's owning
    /// character against the player's.
    /// </summary>
    private static bool IsOffSheet(CardModel card) =>
        card is not CustomCardModel;

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
