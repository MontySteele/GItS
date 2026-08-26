using System.Collections.Generic;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// Legibility sprint, Track L-C (text re-homing). Once a rider renders inside
/// the card's own number (CalculatedDamageVar), restating the arithmetic in
/// the rules text is duplicate bookkeeping -- the face already shows the
/// answer, live and greened. The face keeps a SHORT marker naming the
/// mechanism, so a card read on a reward screen still declares that it
/// scales, and the arithmetic moves here, where it can additionally say what
/// the rider is worth right now.
///
/// `ExtraHoverTips` is evaluated when the card is inspected, so these numbers
/// are live -- the same property KleeCardTooltips uses for its board-aware
/// reaction previews.
///
/// On the API: `HoverTipFactory`'s entry points are all typed (FromKeyword,
/// FromPower, FromPotion, FromOrb, FromEnchantment, FromAffliction), which is
/// why a shared keyword tip cannot carry a per-card rate. `HoverTip` itself,
/// however, has a `(LocString title, string description)` constructor -- free
/// text for the body, so no custom IHoverTip implementation is needed. Only
/// the title needs a loc row; those ship beside the custom-keyword fallbacks
/// in KleeMod.InjectLocStrings under the same KLEEMOD- prefix.
/// </summary>
public static class FurinaRiderTips
{
    private const string Table = "card_keywords";

    public const string FanfareKey = "KLEEMOD-FANFARE_RIDER";
    public const string AuraKey = "KLEEMOD-AURA_RIDER";
    public const string SalonKey = "KLEEMOD-SALON_RIDER";
    public const string CompanionKey = "KLEEMOD-COMPANION_RIDER";

    public static IEnumerable<IHoverTip> ForCard(
        IEnumerable<IHoverTip> inherited,
        CardModel card,
        int fanfarePer = 0,
        int fanfareStep = 0,
        bool grantsBlock = false,
        int auraBonus = 0,
        int salonPer = 0,
        bool salonGrantsBlock = false,
        int companionPer = 0)
    {
        foreach (var tip in inherited) yield return tip;

        if (fanfareStep > 0)
        {
            yield return new HoverTip(
                new LocString(Table, FanfareKey + ".title"),
                FanfareBody(card, fanfarePer, fanfareStep, grantsBlock));
        }

        if (auraBonus > 0)
        {
            yield return new HoverTip(
                new LocString(Table, AuraKey + ".title"),
                $"+{auraBonus} damage against an enemy that carries an "
              + "elemental aura. Hover an enemy to see this card's number "
              + "for that target.");
        }

        if (salonPer > 0)
        {
            yield return new HoverTip(
                new LocString(Table, SalonKey + ".title"),
                SalonBody(card, salonPer, salonGrantsBlock));
        }

        if (companionPer > 0)
        {
            yield return new HoverTip(
                new LocString(Table, CompanionKey + ".title"),
                CompanionBody(card, companionPer));
        }
    }

    /// <summary>The rate, plus what it is worth at this moment. Out of combat
    /// (deck view, reward screen) there is no meter to read, so the rate
    /// stands alone rather than printing a misleading zero.</summary>
    private static string FanfareBody(
        CardModel card, int per, int step, bool grantsBlock)
    {
        var noun = grantsBlock ? "Block" : "damage";
        var rate = $"+{per} {noun} per {step} Fanfare you hold.";
        var owner = TipOwner.CreatureOf(card);
        if (owner == null || card.CombatState == null) return rate;

        var fanfare = FurinaResources.ReadableFanfare(owner);
        return $"{rate} You hold {fanfare} Fanfare: +{fanfare / step * per} "
             + $"{noun}, already counted in the number above.";
    }

    /// <summary>A13/A14: the per-member slope, plus what the stage is paying
    /// right now. Says "on stage" rather than naming the meter, because the
    /// thing being counted is visible -- the members are standing there --
    /// and the whole point of the rework is that the pilot can watch each
    /// deploy move this number.</summary>
    private static string SalonBody(CardModel card, int per, bool grantsBlock)
    {
        var noun = grantsBlock ? "Block" : "damage";
        var rate = $"+{per} {noun} per Salon member on stage.";
        var owner = TipOwner.CreatureOf(card);
        if (owner == null || card.CombatState == null) return rate;

        var members = SalonMemberPower.Count(owner);
        if (members == 0)
        {
            return $"{rate} Your stage is empty, so this card is paying "
                 + "nothing extra right now.";
        }
        return $"{rate} You have {members} on stage: +{members * per} {noun}, "
             + "already counted in the number above.";
    }

    /// <summary>Fanfare rework Track C.3 (2026-07-28): Blocking Notes'
    /// Companion tempo. Same shape as SalonBody -- the rate, then what it is
    /// worth right now -- because the thing being counted is a fact about
    /// THIS TURN and the player needs to know whether playing the Companion
    /// first is worth the sequencing.
    ///
    /// The count INCLUDES Guest Star token plays. That is the ruling and it
    /// is worth the tip saying so, because a generated Companion does not
    /// look like a drafted one and a player who assumed otherwise would
    /// mis-sequence the whole turn.</summary>
    private static string CompanionBody(CardModel card, int per)
    {
        var rate = $"+{per} Block per Companion card you have played this "
                 + "turn, including Guest Stars.";
        var owner = TipOwner.CreatureOf(card);
        if (owner == null || card.CombatState == null) return rate;

        var plays = CurtainCallHooks.CompanionPlaysThisTurn(owner);
        if (plays == 0)
        {
            return $"{rate} You have played none this turn, so this card is "
                 + "paying nothing extra right now.";
        }
        return $"{rate} You have played {plays}: +{plays * per} Block, "
             + "already counted in the number above.";
    }
}
