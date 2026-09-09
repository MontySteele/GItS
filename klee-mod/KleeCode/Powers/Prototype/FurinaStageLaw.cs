namespace KleeMod.Powers;

/// <summary>
/// FURINA, THE STAGE -- the arm's numbers, and nothing else (`EB-719`,
/// `EB-720`, `EB-721`; R269, 2026-09-08).
///
/// <para>THE DESIGN is
/// <c>review/active/furina-stage-brief-2026-09-08.md</c>. Its sec.3 states
/// every rule and its sec.10 default 3 discloses the opening values as a
/// D default: "Opening Fanfare 3, regen 1 from turn two, Refill 5, the nominal
/// rate 2, the acts and the bows at the numbers in sec.3 (D, the sim's)". So
/// these are PROTOTYPE SEEDS, not ruled balance -- under R215 B no number
/// measured on a prototype is quotable -- but they are the seeds both engines
/// have to agree on, and <c>tools/lint_constant_parity.py</c> is what makes
/// that true rather than intended.</para>
///
/// <para>THE SIM DECLARED THEM FIRST and this file mirrors it, which is the
/// reverse of the reframe's order and deliberate: `EB-720` is the sim engine
/// (<c>tier0/engine/furina_stage.py</c>) and `EB-721` the C# one, so every
/// value here names the module constant it copies.</para>
///
/// <para>WHY A LAW CLASS AND NOT <c>constants.py</c>'s twin: the sim keeps
/// these in the quarantined arm module rather than in <c>constants.py</c>, so
/// that a prototype moves neither the constant census nor the world stamp
/// (<c>furina_stage</c>'s own header). Mirroring is a different question from
/// stamping, and the parity gate reads them out of where the sim keeps
/// them.</para>
///
/// <para>WHAT IS NOT HERE: the stage itself. The seats, the pet creatures,
/// the damage order and the acts are the C# arm's, and they are being built
/// beside this file. This class is only the numbers they and the keyword tips
/// both read, declared once.</para>
/// </summary>
public static class FurinaStageLaw
{
    /// <summary>Front, middle, back. Mirrors <c>furina_stage.SEATS</c>.</summary>
    public const int Seats = 3;

    /// <summary>What the starting relic Salon Solitaire puts Usher on stage
    /// with, at combat start (sec.3 rule 2). Mirrors
    /// <c>furina_stage.OPENING_FANFARE</c>.</summary>
    public const int OpeningFanfare = 3;

    /// <summary>What a summoned performer arrives at (sec.3 rule 3). Mirrors
    /// <c>furina_stage.SUMMON_FANFARE</c>.</summary>
    public const int SummonFanfare = 1;

    /// <summary>What the LEAD regains at the start of her turn, from her
    /// second turn on (sec.3 rule 4). Mirrors
    /// <c>furina_stage.LEAD_REGEN</c>.</summary>
    public const int LeadRegen = 1;

    /// <summary>What the starter's Refill raises on the back performer
    /// (sec.3 rule 5, sec.12 <i>Standing Ovation</i>). Mirrors
    /// <c>furina_stage.REFILL_AMOUNT</c>.</summary>
    public const int RefillAmount = 5;

    /// <summary>Usher's act: Block to Furina, from any seat, at the end of her
    /// turn (sec.3 rule 10). Mirrors
    /// <c>furina_stage.ACT_USHER_BLOCK</c>.</summary>
    public const int ActUsherBlock = 3;

    /// <summary>Chevalmarin's act: damage to EVERY enemy, and Hydro with it.
    /// Mirrors <c>furina_stage.ACT_CHEVALMARIN_DAMAGE</c>.</summary>
    public const int ActChevalmarinDamage = 2;

    /// <summary>Crabaletta's act: damage to a random enemy. Mirrors
    /// <c>furina_stage.ACT_CRABALETTA_DAMAGE</c>.</summary>
    public const int ActCrabalettaDamage = 5;

    /// <summary>Usher's bow: Block to Furina, once, when a Spend empties him
    /// (sec.3 rule 9). Mirrors <c>furina_stage.BOW_USHER_BLOCK</c>.</summary>
    public const int BowUsherBlock = 4;

    /// <summary>Crabaletta's bow: damage to a random enemy. Chevalmarin's bow
    /// is Hydro on every enemy and carries no number, which is why there are
    /// two bow constants and not three. Mirrors
    /// <c>furina_stage.BOW_CRABALETTA_DAMAGE</c>.</summary>
    public const int BowCrabalettaDamage = 8;
}
