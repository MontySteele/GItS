namespace KleeMod.Powers;

/// <summary>
/// THE KOKOMI OVERHAUL SWITCH, C# side. Twin of tier0's <c>C.KOKOMI_OVERHAUL</c>.
///
/// The ruled brief (<c>review/active/kokomi-brief-2026-09-01.md</c> DRAFT 6,
/// direction ruled R240 and approved R241) replaces her whole rule set with ONE
/// idea: the <b>Bake-Kurage</b> is a pet on her side of the field for the whole
/// combat that enemies cannot touch; a card with a <b>Plan</b> line can be
/// played on the jellyfish instead of where it would normally go, its cost paid
/// now, and at the start of her next turn the jellyfish carries out the Plan
/// line; a planned hit lands on the front enemy unless the line says every
/// enemy, and her Strength and Dexterity count; nothing happens by itself.
/// <b>Mend</b> heals and never above the HP she entered the fight with. Slice
/// one (<c>kokomi-overhaul-slice-1-2026-09-01.md</c> draft 6) is the ten-card
/// starter, 26 pool rows, Tamakushi Casket and the engine list in its sec.5.
///
/// DRAFT 2's RULES ARE GONE, NOT OFF. Tide, Surge, Exert, the pulse and its
/// budget, the Garment, Strength-to-Tide, Orders and Tactics are cut by the
/// brief's sec.6 by name, so their ops, their constants and their C# are
/// deleted rather than left inert behind a second switch. What survives from
/// draft 2 is the typed Plan queue, Mend, and this switch.
///
/// TWO SWITCHES, NOT ONE, AND THEY DO DIFFERENT JOBS -- the same arrangement
/// <see cref="KleeOverhaul"/> and <see cref="CompanionOverhaul"/> make, for the
/// same reasons:
///
///   * <c>-p:PrototypeCards=true</c> (defines <c>PROTOTYPE_CARDS</c>) is the
///     QUARANTINE. It compiles <c>Cards/Prototype/**</c> and
///     <c>Powers/Prototype/**</c> -- this file included -- so a release build
///     contains no type from this arm at all.
///   * <c>-p:KokomiOverhaul=true</c> (defines <c>KOKOMI_OVERHAUL</c>) is the
///     ARM. It only moves <see cref="Enabled"/>'s default. The rules engine
///     compiles either way, because the headless pins have to exercise the
///     rules AND assert the flag-off wiring in one build.
///
/// WHAT MOVES WHEN IT IS ON, exhaustively. Every seam is one <c>if</c> on this
/// property and there are ten of them, in two groups.
///
/// The four that REPLACE:
///   * <c>Kokomi.StartingDeck</c> -- the slice's ten cards
///     (<see cref="KokomiOverhaulRoster.StartingDeck"/>).
///   * <c>Kokomi.StartingRelics</c> -- Tamakushi Casket instead of the Pearl
///     of Wisdom, because the Pearl IS the exhaust funnel this arm retires.
///   * <c>KokomiCardPool.FilterThroughEpochs</c> -- her whole offerable pool is
///     the slice's 26 rows (<see cref="KokomiOverhaulRoster.OfferablePool"/>).
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
///
/// FLAG OFF IS BYTE-IDENTICAL. Every one of those ten is an early branch on
/// this property, so with it off her starter, her relic, her pool and her
/// funnel are exactly what they were, and no card applies a power from this
/// arm. That is the acceptance condition and it is pinned by
/// <c>KleeTests/Prototype/KokomiOverhaulRuleTests.cs</c> and
/// <c>tier0/tests/test_kokomi_overhaul.py</c> rather than intended.
/// </summary>
public static class KokomiOverhaul
{
    /// <summary>
    /// The arm's default: <c>-p:KokomiOverhaul=true</c> turns it on. Mirrors
    /// <c>C.KOKOMI_OVERHAUL</c>, which ships <c>False</c>.
    /// </summary>
    public const bool DefaultEnabled =
#if KOKOMI_OVERHAUL
        true;
#else
        false;
#endif

    /// <summary>
    /// Is the arm live? Settable so a headless pin can assert both sides of
    /// the switch in one build; nothing in the mod ever writes it.
    /// </summary>
    public static bool Enabled { get; set; } = DefaultEnabled;

    /// <summary>
    /// Is the arm live FOR THIS CREATURE? The arm is Kokomi's alone, and every
    /// rule below asks through this rather than through
    /// <see cref="Enabled"/> directly -- in co-op the other seat may be Klee,
    /// and a bare flag read would hand him a Tide counter.
    /// </summary>
    public static bool LiveFor(MegaCrit.Sts2.Core.Entities.Creatures.Creature? creature) =>
        Enabled && KokomiResources.IsKokomi(creature);
}

/// <summary>
/// The number the overhaul's RULES carry, and it is ONE. Draft 6's rules are
/// structural -- where a card lands and when -- so almost every figure is a
/// CARD's and stays on its row. The relic's strike is the exception: it is a
/// rule Tamakushi Casket carries, printed on the relic and on no card.
///
/// MIRRORED BY VALUE from tier0, which is why it is a named constant rather
/// than a literal at the call site (<c>tools/lint_constant_parity.py</c>).
/// </summary>
public static class KokomiOverhaulLaw
{
    /// <summary>Tamakushi Casket: the jellyfish's Hydro strike, per debuff she
    /// applies to an enemy. Mirrors
    /// <c>C.KOKOMI_OVERHAUL_CASKET_STRIKE</c>.</summary>
    public const int CasketStrike = 2;
}
