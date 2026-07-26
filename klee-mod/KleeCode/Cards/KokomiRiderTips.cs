using System.Collections.Generic;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// Live arithmetic for Kokomi's two hidden scaling reads, following
/// <see cref="FurinaRiderTips"/>'s shape.
///
/// THE PROBLEM THESE SOLVE is specific to her. Furina's riders render inside
/// the card's own printed number, so a face already shows the answer and the
/// tip only has to explain it. Kokomi's two big reads cannot do that:
///
///   - the Bake-Kurage pulse resolves at END OF TURN, from a bank that will
///     have moved by then, so the summon card's face can never print it;
///   - the Ceremonial Garment rider lands on OTHER cards -- every attack she
///     plays while the state holds -- so no single face owns it.
///
/// Both are therefore invisible: the numbers are real, large, and computed
/// somewhere the player cannot see. That is the exact failure the Furina
/// legibility sprint named (a preview and an effect that compute separately
/// will drift, and the player believes the preview), one step worse -- here
/// there was no preview at all.
///
/// Every number below is read through the SAME accessors the resolution uses
/// (KurageSummonPower.PulseDamage, CeremonialGarmentPower.ChargeBonus), so a
/// tip cannot disagree with the hit. Do not re-derive the arithmetic here.
/// </summary>
public static class KokomiRiderTips
{
    private const string Table = "card_keywords";

    public const string PulseKey = "KLEEMOD-KURAGE_PULSE_RIDER";
    public const string GarmentKey = "KLEEMOD-GARMENT_RIDER";
    public const string MusterKey = "KLEEMOD-MUSTER";

    /// <summary>
    /// R78: the [gold]Muster[/gold] keyword, defined ONCE.
    ///
    /// Nine cards used to restate the full rule on their faces -- "transform
    /// N cards in your hand into a random Inazuma Companion that costs 1 less
    /// and Exhausts" -- about ninety characters of identical text apiece, and
    /// the reason several of them sat at text budget. The faces now say
    /// "Muster N" and this tip carries the definition.
    ///
    /// Unlike the two rider tips in this file, this one is NOT live
    /// arithmetic: there is no per-card number to compute, so it prints the
    /// rule and stops. It is here rather than in a keyword table because the
    /// hover tip is the surface the other two Kokomi explanations already
    /// use, and a player looking for "what does this word mean" should not
    /// have to learn which of two mechanisms a given term lives in.
    ///
    /// The cost is stated from the constant, so a CONSCRIPT_COST_DELTA retune
    /// cannot leave nine card faces and this definition disagreeing -- which
    /// is exactly the failure mode the restatements had.
    /// </summary>
    public static IEnumerable<IHoverTip> ForMuster(
        IEnumerable<IHoverTip> inherited, CardModel card)
    {
        foreach (var tip in inherited) yield return tip;
        var cheaper = -KokomiConstants.ConscriptCostDelta;
        yield return new HoverTip(
            new LocString(Table, MusterKey + ".title"),
            $"[gold]Muster N[/gold]: transform N cards in your hand into "
          + $"random Inazuma [gold]Companion[/gold] cards. Each costs "
          + $"{cheaper} less and [gold]Exhausts[/gold]. Kit cards and "
          + "Companions you already hold are never chosen.");
    }

    /// <summary>
    /// Attach to any card that FIELDS the jellyfish. The tip states the rate
    /// and, in combat, what the next pulse would hit for at the current bank.
    /// </summary>
    public static IEnumerable<IHoverTip> ForKuragePulse(
        IEnumerable<IHoverTip> inherited, CardModel card)
    {
        foreach (var tip in inherited) yield return tip;
        yield return new HoverTip(
            new LocString(Table, PulseKey + ".title"), PulseBody(card));
    }

    /// <summary>
    /// Attach to any ATTACK. While the Garment holds, this card is carrying a
    /// bonus its face does not print.
    ///
    /// The tip is silent when the state is down: a card that advertises a
    /// window it is not in is noise on 90% of the plays it appears on, and
    /// noise is how a legibility layer trains players to stop reading it.
    /// </summary>
    public static IEnumerable<IHoverTip> ForGarmentAttack(
        IEnumerable<IHoverTip> inherited, CardModel card)
    {
        foreach (var tip in inherited) yield return tip;

        var owner = card.Owner?.Creature;
        if (owner == null || card.CombatState == null) yield break;
        if (!CeremonialGarmentPower.IsUp(owner)) yield break;

        var bonus = CeremonialGarmentPower.ChargeBonus(owner);
        yield return new HoverTip(
            new LocString(Table, GarmentKey + ".title"),
            $"[gold]Ceremonial Garment[/gold] is active: this attack deals "
          + $"+{bonus} damage (1 per {KokomiConstants.GarmentChargeDivisor} "
          + $"of your {KokomiResources.GetCharge(owner)} [gold]Charge[/gold]) "
          + $"and grants {KokomiConstants.GarmentAttackBlock} Block. "
          + "Not included in the number above.");
    }

    /// <summary>
    /// The rate, plus what it is worth right now. Out of combat (deck view,
    /// reward screen) there is no bank to read, so the rate stands alone
    /// rather than printing a misleading zero -- the FurinaRiderTips rule.
    /// </summary>
    private static string PulseBody(CardModel card)
    {
        // R73/A2: in combat the rate is the AMPED one. Before Sun and Moon
        // raises the multiplier, and a tip that kept quoting the base would
        // understate the pulse by exactly the card the player just bought --
        // the drift the legibility sprint exists to prevent. Out of combat
        // there is no owner to read copies off, so the base rate stands.
        var owner = card.Owner?.Creature;
        var perCharge = owner == null
            ? KokomiConstants.KuragePulsePerCharge
            : KurageSummonPower.PulseMultiplier(owner);
        var rate = $"The pulse deals {KokomiConstants.KuragePulseBase} damage "
                 + $"plus {perCharge} per "
                 + "[gold]Charge[/gold] you hold, at the END of your turn.";
        if (owner == null || card.CombatState == null) return rate;

        var charge = KokomiResources.GetCharge(owner);
        return $"{rate} You hold {charge} Charge: the next pulse hits for "
             + $"{KurageSummonPower.PulseDamage(owner)}. Charge banked before "
             + "the pulse counts, so the number can still move.";
    }
}
