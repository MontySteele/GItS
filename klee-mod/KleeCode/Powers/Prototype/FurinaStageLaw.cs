namespace KleeMod.Powers;

/// <summary>
/// FURINA, THE STAGE -- the arm's numbers, and nothing else (`EB-723`,
/// `EB-724`, `EB-725`; R269, 2026-09-08).
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
/// reverse of the reframe's order and deliberate: `EB-724` is the sim engine
/// (<c>tier0/engine/furina_stage.py</c>) and `EB-725` the C# one, so every
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
    /// (sec.3 rule 5, sec.12 <i>Rising Applause</i>). Mirrors
    /// <c>furina_stage.REFILL_AMOUNT</c>.</summary>
    public const int RefillAmount = 5;

    /// <summary>Usher's act: Block to Furina, from any seat, at the end of her
    /// turn (sec.3 rule 10). Mirrors
    /// <c>furina_stage.ACT_USHER_BLOCK</c>.</summary>
    public const int ActUsherBlock = 3;

    /// <summary>Chevalmarin's act: plain damage to EVERY enemy. No Hydro
    /// since draft 3 (2026-09-25): no act applies an element. Mirrors
    /// <c>furina_stage.ACT_CHEVALMARIN_DAMAGE</c>.</summary>
    public const int ActChevalmarinDamage = 2;

    /// <summary>Crabaletta's act: plain damage to a random enemy. Mirrors
    /// <c>furina_stage.ACT_CRABALETTA_DAMAGE</c>.</summary>
    public const int ActCrabalettaDamage = 5;

    // RULE 9, THE BOW, HAS NO NUMBERS OF ITS OWN since draft 3 (2026-09-25,
    // the Stage review's pick 1): a performer that Bows performs its own act
    // one more time as it leaves (FurinaStage.Bow). The two bow constants
    // (Usher's Fanfare, Crabaletta's 8) went with the separate Bow effects.

    /// <summary>
    /// RULE 12, THE APPLAUSE FADES (draft 3, 2026-09-25). At the end of
    /// Furina's turn, after the acts, each performer BEHIND THE FRONT loses
    /// half of its Fanfare above this, rounded down (<see cref="FadeLoss"/>).
    /// The front never fades. The knob seat rounds tune. Mirrors
    /// <c>furina_stage.FADE_THRESHOLD</c>.
    /// </summary>
    public const int FadeThreshold = 5;

    /// <summary>
    /// Rule 12's arithmetic, ONE function so the threshold and the halving
    /// are tuned in one place: half of the Fanfare above
    /// <see cref="FadeThreshold"/>, rounded down. 5 -> 0, 6 -> 0, 7 -> 1,
    /// 9 -> 2, 15 -> 5, 25 -> 10. It never takes a bar below the threshold,
    /// so it never empties a performer. Mirrors
    /// <c>furina_stage.fade_loss</c>.
    /// </summary>
    public static int FadeLoss(int fanfare) =>
        fanfare <= FadeThreshold ? 0 : (fanfare - FadeThreshold) / 2;
}
