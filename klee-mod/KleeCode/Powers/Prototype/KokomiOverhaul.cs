namespace KleeMod.Powers;

/// <summary>
/// THE KOKOMI OVERHAUL SWITCH, C# side. Twin of tier0's <c>C.KOKOMI_OVERHAUL</c>.
///
/// The ruled brief (<c>review/active/kokomi-brief-2026-09-01.md</c> sec.4, all
/// eight picks ruled at their defaults 2026-09-01) replaces her whole rule set:
/// the Bake-Kurage is always on the field and holds <b>Tide</b>, which never
/// resets on its own; her cards add Tide; <b>Surge</b> spends the whole of it as
/// one Hydro hit; on a turn she did not Surge the jellyfish <b>Mends</b> her a
/// chip, capped per combat on the relic; <b>Exert N</b> is an HP cost on Skills
/// and Powers taken from Block first; the <b>Garment</b> is a short window where
/// her Attacks Mend; Strength becomes Tide; and a <b>Plan</b> happens at the
/// start of her next turn. Slice one
/// (<c>kokomi-overhaul-slice-1-2026-09-01.md</c>) is the ten-card starter, 28
/// pool rows, the relic and the engine list in its sec.5.
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
/// property and there are seven of them, in two groups.
///
/// The four that REPLACE:
///   * <c>Kokomi.StartingDeck</c> -- the slice's ten cards
///     (<see cref="KokomiOverhaulRoster.StartingDeck"/>).
///   * <c>Kokomi.StartingRelics</c> -- Tamanooya's Casket instead of the Pearl
///     of Wisdom, because the Pearl IS the exhaust funnel this arm retires.
///   * <c>KokomiCardPool.FilterThroughEpochs</c> -- her whole offerable pool is
///     the slice's 28 rows (<see cref="KokomiOverhaulRoster.OfferablePool"/>).
///   * <c>KokomiResourceHooks.BeforeCombatStart</c> -- the jellyfish is
///     installed and her entry HP is captured.
///
/// The three that TURN OFF, all in <c>KokomiResourceHooks</c> and all for the
/// same one sentence in the brief's sec.4 ("What leaves: the Charge bank, ...
/// Muster as a transform, ... the Burst gate"):
///   * the Charge and Burst accrual on exhaust,
///   * the Kurage's memory (its entry rules, its fire and its install),
///   * the skill-tag Burst particle and the kit-Burst grant check.
/// Rule 7 (Strength becomes Tide) REPLACES the shipped Strength-to-Charge
/// conversion at the same chokepoint, so that hook moves rather than stopping.
///
/// FLAG OFF IS BYTE-IDENTICAL. Every one of those seven is an early branch on
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
/// The numbers the overhaul's RULES carry. Placeholders, not claims (slice
/// packet sec.1: "No number in it is a claim") -- and MIRRORED BY VALUE from
/// tier0, which is why they are named constants rather than literals at the
/// call sites (<c>tools/lint_constant_parity.py</c>).
///
/// A number a CARD prints stays on the card row, where the codegen renders it
/// into a DynamicVar or a literal; only a number a RULE or a POWER carries
/// lands here. That is why Exert 2, Tide +5 and Mend 12 are absent and the
/// pulse's 2-and-8 are present: the pulse is the relic's rule, not a card's.
/// </summary>
public static class KokomiOverhaulLaw
{
    /// <summary>Rule 4: the pulse Mends this on a turn she did not Surge.
    /// Mirrors <c>C.KOKOMI_OVERHAUL_PULSE_MEND</c>.</summary>
    public const int PulseMend = 2;

    /// <summary>Rule 4: and never more than this in one combat. Mirrors
    /// <c>C.KOKOMI_OVERHAUL_PULSE_BUDGET</c>.</summary>
    public const int PulseBudget = 8;

    /// <summary>Song of Pearls: the pulse Mends this instead. Mirrors
    /// <c>C.KOKOMI_OVERHAUL_SONG_MEND</c>.</summary>
    public const int SongOfPearlsMend = 3;

    /// <summary>Song of Pearls: and the budget is this instead. Mirrors
    /// <c>C.KOKOMI_OVERHAUL_SONG_BUDGET</c>.</summary>
    public const int SongOfPearlsBudget = 12;

    /// <summary>Rule 6: each Attack that hits Mends this while the Garment is
    /// worn. Mirrors <c>C.KOKOMI_OVERHAUL_GARMENT_MEND</c>.</summary>
    public const int GarmentMend = 2;

    /// <summary>Reading the Tide: one card per this much Tide. Mirrors
    /// <c>C.KOKOMI_OVERHAUL_TIDE_PER_CARD</c>.</summary>
    public const int TidePerCard = 5;
}
