namespace KleeMod.Powers;

/// <summary>
/// THE KLEE OVERHAUL SWITCH, C# side. Twin of tier0's <c>C.KLEE_OVERHAUL</c>.
///
/// The ruled brief (<c>review/active/klee-brief-2026-09-01.md</c> sec.3)
/// replaces Klee's whole rule set: a Bomb is a numbered charge that GROWS and
/// never goes off by itself, only a card that says <i>Set off</i> pops one, a
/// Bomb whose enemy dies JUMPS at its current size, each explosion mints one
/// Spark, a Mine is a Bomb that also answers the enemy's attack on her, and
/// nothing fires by itself. Slice one (<c>klee-overhaul-slice-1-2026-09-01.md</c>)
/// is the ten-card starter, 28 pool rows and the engine list in its sec.5.
///
/// TWO SWITCHES, NOT ONE, AND THEY DO DIFFERENT JOBS.
///
///   * <c>-p:PrototypeCards=true</c> (defines <c>PROTOTYPE_CARDS</c>) is the
///     QUARANTINE. It compiles <c>Cards/Prototype/**</c> and
///     <c>Powers/Prototype/**</c> -- this file included -- so a release build
///     contains no type from this arm at all. Unchanged, and it still gates
///     the Sparks arm and the Kurage's memory beside this one.
///   * <c>-p:KleeOverhaul=true</c> (defines <c>KLEE_OVERHAUL</c>) is the ARM.
///     It only moves <see cref="Enabled"/>'s default. The rules engine
///     compiles either way, because the headless pins have to be able to
///     exercise the rules AND assert the flag-off wiring in one build -- the
///     same argument <c>KleeTests.csproj</c> already makes for
///     <c>PROTOTYPE_CARDS</c>.
///
/// WHY A SETTABLE STATIC RATHER THAN A BARE <c>#if</c>. The Sparks arm's twin
/// (<c>SparkPower.BaseRuleActive</c>) is a <c>const</c> because that arm has
/// exactly one shape per build. This one does not: it must COEXIST with the
/// Sparks arm, which also rewrites Klee's starter, and a dev build compiles
/// both. So the arm is a runtime read at the two wiring seams
/// (<c>Klee.StartingDeck</c> and <c>KleeCardPool.FilterThroughEpochs</c>), and
/// it wins where they overlap -- see <see cref="KleeOverhaulRoster"/>.
///
/// FLAG OFF IS BYTE-IDENTICAL. Nothing reads a proto overhaul row, no card
/// places a <see cref="ProtoBombPower"/>, and the shipped <c>BombPower</c> is
/// untouched by this arm in every build. That is the acceptance condition and
/// it is pinned by <c>KleeTests/Prototype/KleeOverhaulFlagOffTests.cs</c>.
/// </summary>
public static class KleeOverhaul
{
    /// <summary>
    /// The arm's default: <c>-p:KleeOverhaul=true</c> turns it on. Mirrors
    /// <c>C.KLEE_OVERHAUL</c>, which ships <c>False</c>.
    /// </summary>
    public const bool DefaultEnabled =
#if KLEE_OVERHAUL
        true;
#else
        false;
#endif

    /// <summary>
    /// Is the overhaul arm live? Settable so a headless pin can assert both
    /// sides of the switch in one build; nothing in the mod ever writes it.
    /// </summary>
    public static bool Enabled { get; set; } = DefaultEnabled;
}

/// <summary>
/// The four numbers the overhaul's rules carry. Placeholders, not claims
/// (slice packet sec.1) -- and MIRRORED BY VALUE from tier0, which is why they
/// are named constants rather than literals at the call sites
/// (<c>tools/lint_constant_parity.py</c>).
/// </summary>
public static class KleeOverhaulLaw
{
    /// <summary>Rule 1: every Bomb grows by this at the start of Klee's turn.
    /// Mirrors <c>C.KLEE_OVERHAUL_BOMB_GROWTH</c>.</summary>
    public const int BombGrowth = 4;

    /// <summary>Explosives Workshop: this much growth on top, per stack.
    /// Mirrors <c>C.KLEE_OVERHAUL_WORKSHOP_GROWTH</c>.</summary>
    public const int WorkshopGrowth = 1;

    /// <summary>
    /// Alice's Recipe: growth is MULTIPLIED by this while the power is up --
    /// "your Bombs grow twice each turn". Mirrors
    /// <c>C.KLEE_OVERHAUL_ALICE_MULTIPLIER</c>.
    ///
    /// A MULTIPLIER RATHER THAN A REPLACEMENT since the 2026-09-02 balance
    /// pass. The row used to read "grow by 4 instead of 3", which made the
    /// Rare a strictly weaker Explosives Workshop: a second Workshop reaches
    /// 5 and a second Recipe still read 4. Doubling is the Rare, the Workshop
    /// stays the stacking +1, and the composition is
    /// <see cref="ProtoBombPower.GrowthFor"/>'s one line.
    /// </summary>
    public const int AliceMultiplier = 2;

    /// <summary>Rule 4, and Pounding Surprise's whole body under this arm.
    /// Mirrors <c>C.KLEE_OVERHAUL_SPARK_PER_EXPLOSION</c>.</summary>
    public const int SparkPerExplosion = 1;

    /// <summary>
    /// Rule 4's OTHER half, ruled R242 pick 1: Klee starts every combat with
    /// this many Sparks. Mirrors <c>C.KLEE_OVERHAUL_OPENING_SPARK</c>.
    ///
    /// [USER]: "Regent starts with 3 stars and has to generate more through
    /// cards, so 1 is a reasonable compromise." It answers the r4 seat's
    /// structural find -- "Spark-priced cards cannot open a fight, by
    /// construction: Sparks exist only after a Bomb goes off; no Bomb can have
    /// gone off before your first play of a combat" -- and it is what pays for
    /// draft 4's plainer starter, which has no Spark sink of its own: the first
    /// Spark card drafted is live on arrival.
    ///
    /// A KIT RULE, NOT A RELIC CLAUSE, which is why it is here and not on
    /// <c>PoundingSurprise</c>. The brief's rule 4 carries the line (R242), and
    /// a relic clause would vanish the moment Touch of Orobas upgraded the
    /// relic into <c>ExplosiveFrags</c> -- whose own opening bank this arm
    /// deliberately gates OFF. The grant site is
    /// <c>KleeElementalHooks.AfterPlayerTurnStart</c>, turn 1.
    /// </summary>
    public const int OpeningSpark = 1;

    /// <summary>
    /// GROUNDED'S SPARK (`EB-344`, ruled R248): the held turn pays this many
    /// Sparks alongside the Block. Mirrors
    /// <c>C.KLEE_OVERHAUL_GROUNDED_SPARK</c>.
    ///
    /// A CONSTANT AND NOT THE POWER'S AMOUNT, and the upgrade is why: Grounded
    /// upgrades <c>{power_amount: +2}</c>, so <c>GroundedPower.Amount</c> is
    /// the BLOCK and moves from 6 to 8. The Spark stays 1 at both levels, which
    /// makes it the kit's rate rather than the card's number -- the same
    /// footing as <see cref="SparkPerExplosion"/> and
    /// <see cref="OpeningSpark"/>, and the reason all three are compared by
    /// value against tier0 rather than written as literals at the grant site.
    /// </summary>
    public const int GroundedSpark = 1;
}
