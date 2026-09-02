namespace KleeMod.Powers;

/// <summary>
/// THE MONDSTADT COMPANION OVERHAUL SWITCH, C# side. Twin of tier0's
/// <c>C.COMPANION_OVERHAUL</c>.
///
/// The approved workshop
/// (<c>companion-workshop-mondstadt-2026-09-01.md</c>, approved 2026-09-01;
/// it is a Paper artefact on the companion-workshop branch and is not in
/// this tree) rewrites
/// Mondstadt's UNIVERSAL companion pool: twelve Commons that import a
/// character's move instead of wearing a Strike's clothes, Uncommons in the
/// base game's colorless shape, one bespoke Rare per five-star. Twelve of the
/// seventeen shipped rows fail its bar in sec.2 and three of them still carry
/// a rider on Burst Energy, a meter R220 retired.
///
/// TWO SWITCHES, NOT ONE, AND THEY DO DIFFERENT JOBS -- the same arrangement
/// <see cref="KleeOverhaul"/> makes, for the same reasons:
///
///   * <c>-p:PrototypeCards=true</c> (defines <c>PROTOTYPE_CARDS</c>) is the
///     QUARANTINE. It compiles <c>Cards/Prototype/**</c> and
///     <c>Powers/Prototype/**</c> -- this file included -- so a release build
///     contains no type from this arm at all.
///   * <c>-p:CompanionOverhaul=true</c> (defines <c>COMPANION_OVERHAUL</c>) is
///     the ARM. It only moves <see cref="Enabled"/>'s default. The powers
///     compile either way, because the headless pins have to exercise the
///     rules AND assert the flag-off wiring in one build.
///
/// WHAT MOVES WHEN IT IS ON, exhaustively. <see cref="CompanionPool.All"/> --
/// the ONE door <see cref="CompanionSlot"/>, <see cref="CompanionBanner"/> and
/// the shop channel all read -- returns
/// <see cref="CompanionOverhaulRoster.Roster"/> instead of the generated
/// <c>CompanionRoster.All</c>. That roster is every INAZUMA and FONTAINE row
/// unchanged plus the overhaul's Mondstadt rows, so the seventeen shipped
/// Mondstadt rows cannot be offered and the other two nations are untouched.
/// The workshop is a Mondstadt document and says so in its sec.6.
///
/// FLAG OFF IS BYTE-IDENTICAL. <see cref="CompanionPool.All"/> returns exactly
/// what it returned before -- the same generated list object -- and no card
/// applies any power in <c>CompanionOverhaulPowers.cs</c>. That is the
/// acceptance condition and it is pinned by
/// <c>KleeTests/Prototype/CompanionOverhaulFlagOffTests.cs</c>.
/// </summary>
public static class CompanionOverhaul
{
    /// <summary>
    /// The arm's default: <c>-p:CompanionOverhaul=true</c> turns it on.
    /// Mirrors <c>C.COMPANION_OVERHAUL</c>, which ships <c>False</c>.
    /// </summary>
    public const bool DefaultEnabled =
#if COMPANION_OVERHAUL
        true;
#else
        false;
#endif

    /// <summary>
    /// Is the arm live? Settable so a headless pin can assert both sides of
    /// the switch in one build; nothing in the mod ever writes it.
    /// </summary>
    public static bool Enabled { get; set; } = DefaultEnabled;
}

/// <summary>
/// The numbers the overhaul's POWERS carry. Every one is lifted verbatim off
/// the workshop's own printed text (its sec.3, re-priced in its sec.8) --
/// nothing here is derived and nothing is picked. They are named constants
/// rather than literals at the call sites because the sim is LAW and the
/// mirrors must be comparable BY VALUE (<c>tools/lint_constant_parity.py</c>).
///
/// A number a CARD prints stays on the card row, where the codegen renders it
/// into a DynamicVar; only a number a POWER carries lands here.
/// </summary>
public static class CompanionOverhaulLaw
{
    /// <summary>Diona, Signature Mix: Block at the start of each of 2 turns.
    /// Mirrors <c>C.MC_SIGNATURE_MIX_BLOCK</c>.</summary>
    public const int SignatureMixBlock = 4;

    /// <summary>Kaeya, Glacial Waltz: Cryo damage per end of turn, 3 turns.
    /// Mirrors <c>C.MC_GLACIAL_WALTZ_DMG</c>.</summary>
    public const int GlacialWaltzDamage = 6;

    /// <summary>Albedo, Solar Isotoma: the platform's own damage.
    /// Mirrors <c>C.MC_ISOTOMA_DMG</c>.</summary>
    public const int IsotomaDamage = 8;

    /// <summary>Albedo, Solar Isotoma: the Crystallize half.
    /// Mirrors <c>C.MC_ISOTOMA_BLOCK</c>.</summary>
    public const int IsotomaBlock = 4;

    /// <summary>Jean, Dandelion Breeze: Block per end of turn.
    /// Mirrors <c>C.MC_DANDELION_BREEZE_BLOCK</c>.</summary>
    public const int DandelionBreezeBlock = 6;

    /// <summary>Fischl, Oz at Your Side: the Electro volley, no turn limit.
    /// Mirrors <c>C.MC_OZ_DMG</c>.</summary>
    public const int OzDamage = 5;

    /// <summary>Nicole, Revelation: Block at the start of your turn.
    /// Mirrors <c>C.MC_REVELATION_BLOCK</c>.</summary>
    public const int RevelationBlock = 5;

    /// <summary>Nicole, Revelation: Theosis, for holding the line.
    /// Mirrors <c>C.MC_REVELATION_STRENGTH</c>.</summary>
    public const int RevelationStrength = 2;

    /// <summary>Mona, Stellaris Phantasm: the delayed doom, one turn of it.
    /// Mirrors <c>C.MC_OMEN_VULNERABLE</c>.</summary>
    public const int OmenVulnerable = 1;

    /// <summary>Lisa, Lightning Rose: Electro damage per end of turn.
    /// Mirrors <c>C.MC_LIGHTNING_ROSE_DMG</c>.</summary>
    public const int LightningRoseDamage = 5;

    /// <summary>Lisa, Lightning Rose: the Vulnerable that rides it.
    /// Mirrors <c>C.MC_LIGHTNING_ROSE_VULN</c>.</summary>
    public const int LightningRoseVulnerable = 1;
}
