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

    /// <summary>QUARANTINED (R213 E1). The CHARGE KEYWORD -- the meter's own
    /// rules text, which is a different surface from ChargeKey above (that
    /// one titles a per-card RATE tip on a reader).</summary>
    public const string ChargeWordKey = "KLEEMOD-CHARGE";

    // `EB-484`. THE FOLD READ ON A SCREEN WITH NO ENEMY ON IT.
    //
    // THE FIND (Kokomi r16 (c) 7). On a SHOP shelf, `Undertow` printed "Deal 7
    // damage, already including 3 if the enemy has a debuff" and "I could not
    // determine whether that card deals 4 or 7."
    //
    // BOTH READINGS OF THAT SENTENCE ARE AVAILABLE and only one is true. The
    // number is `CalculationBase + ExtraDamage * (debuff ? 1 : 0)`, so it is 7
    // with nothing aimed at and 10 on a debuffed enemy -- "already including
    // 3" is the clause `EB-441` needed for the HOVERED case, where the 10 does
    // already include the 3, and it reads as 4 + 3 everywhere else.
    //
    // WHY THE FACE CANNOT SAY WHICH. A card's `Localization` is read ONCE at
    // registration and neither `CardModel.Description` nor
    // `GetDescriptionForPile` is virtual (checked by reflection against the
    // shipped `sts2.dll`), so a card has exactly one face and it is the same
    // face in a shop as in a fight. The rider tip is the surface that CAN
    // branch, which is the split this whole file exists for.
    public const string DebuffRiderKey = "KLEEMOD-DEBUFF_RIDER";

    /// <summary>
    /// L4b: the printed Charge rider's RATE.
    ///
    /// This is the third failure shape in the same family, and the quietest.
    /// The pulse and the Garment rider are invisible because they resolve
    /// where no face can print them. `all_streams_flow` / `nereids_ascension`
    /// are the opposite: their rider renders INSIDE the card's own number
    /// (CalculatedDamageVar), so the face shows a live, correct total -- and
    /// the face text was cut to a bare marker naming Charge on the strength
    /// of that (a trailing ", already including [gold]Charge[/gold]" clause
    /// since EB-164). What no surface carried was the RATE. A player could
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
    /// QUARANTINED (R213 E1): the [gold]Charge[/gold] KEYWORD.
    ///
    /// THE GAP THIS CLOSES was named twice before it had a witness. R215 D
    /// found that her Charge-gaining faces print the word and nothing on
    /// screen says what it is, and deferred the label into E1 because
    /// labelling a resource whose rules are open would have been settling
    /// them. The blind seat then said it from the other side, unprompted, on
    /// run B6: "Burst Energy accumulated ... although I never saw how to
    /// spend it". A meter with no rules text is a meter a player can only
    /// learn by watching it.
    ///
    /// It arrives HERE first, on the prototype surface, because it is the
    /// spending rows that make the word answerable: until a card printed a
    /// Charge PRICE there was no sentence to write about what holding one is
    /// worth. Attached from the `spend_charge` op by codegen, so a spender
    /// cannot ship printing a word nothing explains. The shipped gain faces
    /// have the same gap and are not touched here -- that is wording-only
    /// hygiene across thirty generated files and belongs in its own commit.
    ///
    /// The accrual rate is stated FROM THE CONSTANT, the Muster tip's
    /// bargain: a retune must not be able to leave the definition quoting a
    /// retired number. In combat the tip also says what the bank holds right
    /// now, because the whole decision the keyword describes is whether to
    /// keep it.
    /// </summary>
    public static IEnumerable<IHoverTip> ForCharge(
        IEnumerable<IHoverTip> inherited, CardModel card)
    {
        foreach (var tip in inherited) yield return tip;
        yield return new HoverTip(
            new LocString(Table, ChargeWordKey + ".title"), ChargeWordBody(card));
    }

    private static string ChargeWordBody(CardModel card)
    {
        var per = KokomiConstants.ChargePerExhaust;
        var rule =
            $"[gold]Charge[/gold]: a bank that grows by {per} whenever one of "
          + "your cards [gold]Exhausts[/gold]. It has no maximum. Cards that "
          + "read it are stronger the more you hold; a card printing a "
          + "[gold]Charge[/gold] price spends it, and cannot be played below "
          + "that price.";
        var owner = TipOwner.CreatureOf(card);
        if (owner == null || card.CombatState == null) return rule;
        return $"{rule} You hold {KokomiResources.GetCharge(owner)} Charge.";
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
    ///
    /// `EB-254`: THE DISCOUNT NAMES ITS DURATION, and the duration is the
    /// COMBAT. `KokomiConscript.Recruit` writes the modifier with
    /// `EnergyCost.AddThisCombat`, the sim twin rewrites `recruit.cost` on the
    /// combat token itself, and the memory price rule is built on that
    /// permanence -- a Muster's own -1 counts on the recruit's entry precisely
    /// because it is NOT a temporary combat discount (packet §11.7). The tip
    /// shipped the phrase bare while four sibling faces in the same pool print
    /// "cost 1 less THIS TURN" for a genuinely turn-scoped rider
    /// (`honor_guard`, `crane_wing`, `friendly_visit`, and `all_hands`, which
    /// prints the Muster and a `this turn` cost_mod in one sentence), so a
    /// reader trained by those four read the elision as the same duration.
    /// `playtest 2026-08-31 B2` is that reader. "this combat" is the game's
    /// own word for the scope -- `secret_stash` prints "They cost 0 this
    /// combat" for the same kind of modifier.
    ///
    /// `EB-214` / R224 item 6 (`M54` pick 1): RULE 1 IS PRINTED HERE, and only
    /// under the flag. The blind run graded `P3` at 0 of 10 turns and 0 of six
    /// Musters naming a Memory consequence -- every Muster target was chosen
    /// BECAUSE the card was dead, the exact inverse of the rule -- and the
    /// diagnosis was wording, not dose. So the rule joins the keyword's OWN
    /// text rather than becoming a second tip: "hover text is that keyword's
    /// detail, and 'tooltip' is not a third surface"
    /// (review/ruled/sitting-2026-08-30.md, item 6).
    ///
    /// The sentence is the packet's §11.7 v3 ruled wording ("a Muster now
    /// creates a memory of the card it ate, and the recruit creates a second
    /// when it burns") plus the price, which is what `P3` asks a tester to be
    /// able to state ("this puts X in the queue at price Y"). The multiplier
    /// is read from `KurageMemoryLaw.CostPerEnergy` for the same reason the
    /// discount above is read from its constant. R55 voice law: the word is
    /// never "sacrifice" on a player-facing surface, which is why the packet's
    /// §12.2 phrasing is not the one printed.
    ///
    /// THE `#if` IS THE WHOLE GUARANTEE. The release build's preprocessed
    /// source for this method is character-for-character what it was, so the
    /// shipped keyword text cannot move; `tier0/tests/test_kurage_base_kit.py`
    /// and `KokomiMusterKeywordTests` pin both halves.
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
          + $"{cheaper} less this combat and [gold]Exhausts[/gold]. Kit "
          + "cards and Companions you already hold are never chosen."
#if PROTOTYPE_CARDS
          + " A [gold]Muster[/gold] creates a memory of the card it ate, and "
          + "the recruit creates a second when it burns. A memory replays for "
          + $"[gold]Charge[/gold] equal to "
          + $"{Powers.KurageMemory.KurageMemoryLaw.CostPerEnergy}x its Cost."
#endif
            );
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
    /// `EB-484`. BOTH NUMBERS OF A `bonus_vs_debuff` FOLD, on every screen.
    ///
    /// See <see cref="DebuffRiderKey"/> for the find and for why the FACE
    /// cannot answer it: a card's description is registered once and neither
    /// description getter is virtual, so the face a shop shows is the face a
    /// fight shows. What varies is what is aimed at, and the fold makes the
    /// printed number vary with it -- which is `EB-441` working, and is
    /// exactly what leaves a buyer with one number and two readings.
    ///
    /// SO THE TIP PRINTS THE PAIR, always, and says which one the face is
    /// showing. It does not branch on being in combat -- unlike every other
    /// tip in this file, whose numbers come off a live meter: these two are
    /// the SHEET's, handed down by the generator from the same
    /// `debuff_calc_rider` that emits the vars, so they are as true on a shop
    /// shelf as on a board and a branch would only make the shelf the screen
    /// that says less.
    /// </summary>
    public static IEnumerable<IHoverTip> ForDebuffRider(
        IEnumerable<IHoverTip> inherited, CardModel card,
        int baseDamage, int bonus)
    {
        foreach (var tip in inherited) yield return tip;
        yield return new HoverTip(
            new LocString(Table, DebuffRiderKey + ".title"),
            $"{baseDamage} against an undebuffed enemy, {baseDamage + bonus} "
          + "against a debuffed one. The face shows whichever applies to the "
          + "enemy you are aiming at.");
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
#if PROTOTYPE_CARDS
        // `EB-247`. QUARANTINED. Under the memory rule the pulse reads the
        // bank NOT AT ALL -- it keys on the type of the last card Kokomi
        // played this turn and pays a flat number per branch. Everything below
        // this block quotes `KuragePulsePerCharge`, which is exactly the term
        // that retired, so under the flag the rate paragraph would be a
        // falsehood on two more surfaces: the fielding cards' hover tip, and
        // the end-of-turn docket, which asks this method for the same
        // paragraph (TurnEndAttribution's `kurage` slot, one copy by design).
        //
        // The live half is READ FROM THE WIRE. `KurageMemory.Forecast` is the
        // same kind/unit/amount triple the observed-board payload publishes,
        // so the tip, the docket and the wire cannot say three things about
        // one pulse -- which is what the three `EB-247` witnesses caught them
        // doing.
        {
            var rule =
                "The pulse answers the LAST card you played this turn, at the "
              + $"END of your turn: Attack -> {KokomiConstants.KuragePulseBase} "
              + "damage and [gold]Hydro[/gold]; Skill -> "
              + $"{Powers.KurageMemory.KurageMemoryLaw.PulseBlock} Block; "
              + "Power -> "
              + (Powers.KurageMemory.KurageMemoryLaw.PowerPulse == "charge"
                    ? $"{KokomiConstants.ChargePerExhaust} [gold]Charge[/gold]"
                    : "[gold]Hydro[/gold]")
              + ". No card played, no pulse.";
            if (owner == null || !inCombat) return rule;

            var (kind, unit, amount) =
                Powers.KurageMemory.Forecast(owner);
            var next = kind == "none"
                ? "You have played nothing yet this turn: no pulse."
                : $"Last card played: {kind}. The next pulse is "
                  + $"{amount} {unit}.";
            return $"{rule} {next} Playing another card of a different type "
                 + "before you end the turn changes it.";
        }
#else
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
#endif
    }
}
