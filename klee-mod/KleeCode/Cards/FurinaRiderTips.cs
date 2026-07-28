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

    public static IEnumerable<IHoverTip> ForCard(
        IEnumerable<IHoverTip> inherited,
        CardModel card,
        int fanfarePer = 0,
        int fanfareStep = 0,
        int auraBonus = 0,
        int salonPer = 0,
        bool salonGrantsBlock = false)
    {
        foreach (var tip in inherited) yield return tip;

        if (fanfareStep > 0)
        {
            yield return new HoverTip(
                new LocString(Table, FanfareKey + ".title"),
                FanfareBody(card, fanfarePer, fanfareStep));
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
    }

    /// <summary>The rate, plus what it is worth at this moment. Out of combat
    /// (deck view, reward screen) there is no meter to read, so the rate
    /// stands alone rather than printing a misleading zero.</summary>
    private static string FanfareBody(CardModel card, int per, int step)
    {
        var rate = $"+{per} damage per {step} Fanfare you hold.";
        var owner = card.Owner?.Creature;
        if (owner == null || card.CombatState == null) return rate;

        var fanfare = FurinaResources.Fanfare(owner);
        return $"{rate} You hold {fanfare} Fanfare: +{fanfare / step * per} "
             + "damage, already counted in the number above.";
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
        var owner = card.Owner?.Creature;
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
}
