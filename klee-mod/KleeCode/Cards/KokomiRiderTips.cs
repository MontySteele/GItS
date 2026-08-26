using System.Collections.Generic;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards;

/// <summary>
/// Live arithmetic for Kokomi's hidden scaling reads, following
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
/// A third read (L4b, <see cref="ForChargeRider"/>) fails the other way: the
/// printed Charge rider's TOTAL renders fine, inside the card's own number,
/// and it was the RATE that no surface carried.
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
    public const string ChargeKey = "KLEEMOD-CHARGE_RIDER";

    /// <summary>
    /// L4b: the printed Charge rider's RATE.
    ///
    /// This is the third failure shape in the same family, and the quietest.
    /// The pulse and the Garment rider are invisible because they resolve
    /// where no face can print them. `all_streams_flow` / `nereids_ascension`
    /// are the opposite: their rider renders INSIDE the card's own number
    /// (CalculatedDamageVar), so the face shows a live, correct total -- and
    /// the face text was cut to "Scales with [gold]Charge[/gold]" on the
    /// strength of that. What no surface carried was the RATE. A player could
    /// watch the number move and never learn it moves by 1 per 2 Charge, so
    /// they could not price a Charge before spending one, which is the only
    /// decision the meter asks them to make.
    ///
    /// Same bargain, and the same shape as <see cref="FurinaRiderTips"/>'s
    /// Fanfare tip: the face keeps the short marker naming the mechanism, the
    /// arithmetic lives here, and out of combat the rate stands alone rather
    /// than printing a misleading zero.
    /// </summary>
    public static IEnumerable<IHoverTip> ForChargeRider(
        IEnumerable<IHoverTip> inherited,
        CardModel card,
        int chargePer = 0,
        int chargeStep = 0,
        bool chargeGrantsBlock = false)
    {
        foreach (var tip in inherited) yield return tip;
        if (chargePer <= 0 || chargeStep <= 0) yield break;
        yield return new HoverTip(
            new LocString(Table, ChargeKey + ".title"),
            ChargeBody(card, chargePer, chargeStep, chargeGrantsBlock));
    }

    /// <summary>The rate, plus what it is worth right now -- the
    /// FurinaRiderTips.FanfareBody wording, one meter over.
    ///
    /// EB-122: the NOUN is a parameter for exactly the reason SYS-7 made it
    /// one on the Fanfare tip. `gyorin_formation` is the first Charge rider on
    /// a BLOCK op, and this tip is the ONLY surface that carries the rate --
    /// so a hardcoded "damage" would be the single place the player can read
    /// the rate and would read it wrong.</summary>
    private static string ChargeBody(
        CardModel card, int per, int step, bool grantsBlock)
    {
        var noun = grantsBlock ? "Block" : "damage";
        var rate = $"+{per} {noun} per {step} [gold]Charge[/gold] you hold.";
        var owner = TipOwner.CreatureOf(card);
        if (owner == null || card.CombatState == null) return rate;

        var charge = KokomiResources.GetCharge(owner);
        return $"{rate} You hold {charge} Charge: +{charge / step * per} "
             + $"{noun}, already counted in the number above.";
    }

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

        var owner = TipOwner.CreatureOf(card);
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
    private static string PulseBody(CardModel card) =>
        PulseBody(TipOwner.CreatureOf(card), inCombat: card.CombatState != null);

    /// <summary>
    /// Creature overload (EB-53/N1). The end-of-turn docket's Bake-Kurage slot
    /// has no card to ask, and the copy MUST NOT FORK -- the same bargain
    /// <see cref="SalonMemberTips"/> struck when the Salon stage started
    /// hovering the member paragraphs the deploy cards print (D1 §4). One
    /// paragraph, two surfaces.
    /// </summary>
    public static string PulseBody(Creature? owner, bool inCombat)
    {
        // R73/A2: in combat the rate is the AMPED one. Before Sun and Moon
        // raises the multiplier, and a tip that kept quoting the base would
        // understate the pulse by exactly the card the player just bought --
        // the drift the legibility sprint exists to prevent. Out of combat
        // there is no owner to read copies off, so the base rate stands.
        var perCharge = owner == null
            ? KokomiConstants.KuragePulsePerCharge
            : KurageSummonPower.PulseMultiplier(owner);
        var rate = $"The pulse deals {KokomiConstants.KuragePulseBase} damage "
                 + $"plus {perCharge} per "
                 + "[gold]Charge[/gold] you hold, at the END of your turn.";
        if (owner == null || !inCombat) return rate;

        var charge = KokomiResources.GetCharge(owner);
        return $"{rate} You hold {charge} Charge: the next pulse hits for "
             + $"{KurageSummonPower.PulseDamage(owner)}. Charge banked before "
             + "the pulse counts, so the number can still move.";
    }
}
