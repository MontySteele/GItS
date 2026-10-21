namespace KleeMod.Powers;

/// <summary>
/// THE KOKOMI OVERHAUL, C# side. Twin of tier0's <c>C.KOKOMI_OVERHAUL</c>.
///
/// The ruled brief (<c>review/active/kokomi-brief-2026-09-01.md</c> DRAFT 7,
/// direction ruled R240 and approved R241) replaces her whole rule set with ONE
/// idea: the <b>Bake-Kurage</b> is a pet on her side of the field for the whole
/// combat that enemies cannot touch; a card with a <b>Plan</b> line can be
/// played on the jellyfish instead of where it would normally go, its cost paid
/// now, and at the start of her next turn the jellyfish carries out the Plan
/// line; a planned hit lands on the front enemy unless the line says every
/// enemy, and her Strength and Dexterity count; nothing happens by itself.
/// <b>Mend</b> heals and never above the HP she entered the fight with. Slice
/// one (<c>kokomi-overhaul-slice-1-2026-09-01.md</c> draft 6) was the ten-card
/// starter, 26 pool rows, Tamakushi Casket and the engine list in its sec.5;
/// the pool passes since have made it 46 rows
/// (<c>KokomiOverhaulRoster.Slice()</c>).
///
/// DRAFT 2's RULES ARE GONE, NOT OFF. Tide, Surge, Exert, the pulse and its
/// budget, the Garment, Strength-to-Tide, Orders and Tactics are cut by the
/// brief's sec.6 by name, so their ops, their constants and their C# are
/// deleted. What survives from draft 2 is the typed Plan queue and Mend.
///
/// WHAT THE ARM CHANGES, in two groups.
///
/// The five that REPLACE:
///   * <c>Kokomi.StartingDeck</c> -- the slice's ten cards
///     (<see cref="KokomiOverhaulRoster.StartingDeck"/>).
///   * <c>Kokomi.StartingRelics</c> -- Tamakushi Casket instead of the Pearl
///     of Wisdom, because the Pearl IS the exhaust funnel this arm retires.
///   * <c>KokomiCardPool.FilterThroughEpochs</c> -- her whole offerable pool is
///     the slice's 46 rows (<see cref="KokomiOverhaulRoster.OfferablePool"/>).
///   * <see cref="ArmStarterBasics"/> -- which pair of basics is HERS when a
///     base-game effect asks the character rather than reading her deck.
///     `EB-351` added it: Large Capsule reads `CardPool.AllCards`, which the
///     pool seam above never touches, so it was handing an arm run her two
///     SHIPPED basics.
///   * <c>KokomiResourceHooks.BeforeCombatStart</c> -- the Bake-Kurage pet is
///     summoned, its marker power installed and her entry HP captured.
///
/// The six that TURN OFF, all because the brief retires the rules they are
/// priced inside. The first four are in <c>KokomiResourceHooks</c>:
///   * the Charge and Burst accrual on exhaust,
///   * the Kurage's memory (its entry rules, its fire and its install),
///   * the skill-tag Burst particle and the kit-Burst grant check,
///   * the STRENGTH REFUSAL itself. Draft 2 converted Strength to Tide at the
///     power-application chokepoint; draft 6's rule 3 says "your Strength and
///     Dexterity count, since the plans are hers", so under this arm the
///     shipped refusal is skipped and Strength simply lands. That is the one
///     off-switch that changes what a SHIPPED hook does rather than what an
///     arm rule does, and it is why it is named here.
///
/// The other two sit beside the RESOURCE, in <c>KokomiResources</c>, because
/// each is an answer to "does she have a Burst meter at all" and that question
/// should have one home rather than one per caller:
///   * the Burst FEED -- <c>KokomiResources.GainBurst</c> (`EB-327`), the one
///     funnel every income source lands in. Three of the four sources were
///     already off at their own seams; REACTIONS were not, and a blind seat
///     read the retired meter filling on the status line.
///   * the Burst GAUGE -- <c>KokomiResources.BurstGaugeApplies</c>
///     (`EB-297`), the predicate <c>GaugeBridge</c> selects on, so the
///     overhead bar is not built at all.
/// </summary>
public static class KokomiOverhaul
{


    /// <summary>
    /// Is the arm live FOR THIS CREATURE? The arm is Kokomi's alone, and every
    /// rule below asks through this -- in co-op the other seat may be Klee.
    ///
    /// THE OFF-CHARACTER RULE (2026-10-18), on the base game's Osty and Orbs
    /// precedent: her kit is live on her from turn one, and on anyone else
    /// from the moment it comes up for them (<see cref="KokomiRules.BringUp"/>:
    /// a Plan card reaching their hand, or one of her cards played). Each
    /// player's kit is their own in co-op. Her relics and her telemetry
    /// record stay hers: they ask <see cref="IsHers"/>.
    /// </summary>
    public static bool LiveFor(MegaCrit.Sts2.Core.Entities.Creatures.Creature? creature) =>
        KokomiResources.IsKokomi(creature)
        || (creature?.Player != null && KokomiOverhaulLedger.HasStarted(creature));

    /// <summary>Is this creature Kokomi herself? The gate for what is truly
    /// hers rather than her kit's: her relics (the Tamakushi Casket and her
    /// arm relics) and her telemetry record.</summary>
    public static bool IsHers(MegaCrit.Sts2.Core.Entities.Creatures.Creature? creature) =>
        KokomiResources.IsKokomi(creature);

    /// <summary>Mark this player's kit as up for this combat. True when it
    /// is live afterwards. Synchronous and idempotent; the jellyfish and the
    /// marker are <see cref="KokomiRules.BringUp"/>'s.</summary>
    public static bool Start(MegaCrit.Sts2.Core.Entities.Creatures.Creature? creature)
    {
        if (creature?.Player == null) return false;
        if (LiveFor(creature)) return true;
        KokomiOverhaulLedger.For(creature).Started = true;
        return true;
    }

    /// <summary>Does this card print a Plan line? Every such card is an
    /// <see cref="IPlannedCard"/> and aims at the Bake-Kurage, a Companion's
    /// included.</summary>
    public static bool HasPlanLine(MegaCrit.Sts2.Core.Models.CardModel? card) =>
        card is IPlannedCard;

    /// <summary>Does this seat get the Plan strip (and its peek view)? On
    /// Kokomi from turn one, as always; on anyone else once their kit is up
    /// AND they have written a Plan this combat -- the base game's gauge
    /// rule (the Regent's Star counter appears on first gain). A read: it
    /// creates no ledger.</summary>
    public static bool StripShowsFor(MegaCrit.Sts2.Core.Entities.Creatures.Creature? creature) =>
        IsHers(creature)
        || (creature != null && LiveFor(creature)
            && KokomiOverhaulLedger.Peek(creature) is { PlansWrittenThisCombat: > 0 });

    /// <summary>Is this one of her cards (her roster id)?</summary>
    public static bool IsKokomiCard(MegaCrit.Sts2.Core.Models.CardModel? card) =>
        card is global::KleeMod.Cards.ICharacterCard { CharacterId: "kokomi" };

    /// <summary>Does playing this card bring its player's kit up? One of her
    /// cards, or any card with a Plan line.</summary>
    public static bool BringsUpOnPlay(MegaCrit.Sts2.Core.Models.CardModel? card) =>
        HasPlanLine(card) || IsKokomiCard(card);
}

/// <summary>
/// The numbers the overhaul's RULES carry. Draft 6's rules are structural --
/// where a card lands and when -- so almost every figure is a CARD's and stays
/// on its row. The starting relic's is the exception: the Tamakushi Casket
/// carries a rule printed on the relic and on no card.
///
/// THE RE-FOUNDING (2026-10-12, design pass pick 3, ruled) REPLACED THE ONES
/// THAT WERE HERE. The Casket's count, Open the Casket and The Long Game are
/// gone. Since 2026-10-18 the relic reads "Whenever you play a Plan card or
/// a Companion, gain 1 Block."
///
/// MIRRORED BY VALUE from tier0, which is why it is a named constant rather
/// than a literal at the call site (<c>tools/lint_constant_parity.py</c>).
/// </summary>
public static class KokomiOverhaulLaw
{
    /// <summary>The Tamakushi Casket's Block for each Plan card or Companion
    /// she plays. Mirrors <c>C.KOKOMI_OVERHAUL_CASKET_BLOCK</c>.</summary>
    public const int CasketBlock = 2;
}
