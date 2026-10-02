using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// The kit-exempt filter for discard, exhaust and recall effects. The kit
/// Burst cards it exempted (Sparks 'n' Splash, Ceremonial Garment, Let the
/// People Rejoice) went with the shipped kits (legacy cleanup stage 5), so
/// every card passes; the generated selectors still name the filter.
/// </summary>
public static class KitGrant
{
    /// <summary>True for every card: no kit Burst card exists.</summary>
    public static bool NotKitCard(CardModel card) => true;
}
