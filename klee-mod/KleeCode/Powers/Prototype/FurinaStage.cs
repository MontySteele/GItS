using MegaCrit.Sts2.Core.Entities.Creatures;

namespace KleeMod.Powers;

/// <summary>
/// THE FURINA STAGE SWITCH, C# side, and the arm that REPLACES the reframe.
///
/// The design is <c>review/active/furina-stage-brief-2026-09-08.md</c> --
/// sec.3 is the rules, sec.10 the defaults it discloses, and every number in
/// <see cref="FurinaStageLaw"/> is one of that section's. Nothing here was
/// decided on this side of the wire; where the brief left a number to the sim
/// it is marked as such on the constant.
///
/// TWO SWITCHES, NOT ONE, exactly as the four arms before it arrange
/// themselves and for their reasons:
///
///   * <c>-p:PrototypeCards=true</c> (defines <c>PROTOTYPE_CARDS</c>) is the
///     QUARANTINE. It compiles <c>Powers/Prototype/**</c>, <c>Cards/Prototype/**</c>
///     and <c>Vfx/Prototype/**</c>, so a release build contains no type from
///     this arm at all and every seam that calls in from a shipped file is
///     itself inside <c>#if PROTOTYPE_CARDS</c>.
///   * <c>-p:FurinaStage=true</c> (defines <c>FURINA_STAGE</c>) is the ARM. It
///     moves ONE default, <see cref="Enabled"/>. The rules compile either way,
///     because the headless pins have to exercise the rules AND assert the
///     flag-off wiring in one build -- the argument
///     <c>KleeTests.csproj</c> already makes for <c>PROTOTYPE_CARDS</c>.
///
/// ONE FLAG, NOT FIVE, and the difference from <see cref="FurinaReframe"/> is
/// the shape of the thing being switched. The reframe was four independent
/// edits to a shipped engine, so each leg had to be settable on its own to
/// pin "this rule moved and the other three did not". The stage is not an edit
/// to anything: with the flag off there is no stage, no performer, no relic
/// and no card, and every seam below is one early return. A per-leg flag would
/// describe a state no board can be in.
///
/// WHAT THE ARM MOVES, exhaustively. Every seam is one <c>if</c> on
/// <see cref="LiveFor"/>:
///
///   * <c>Furina.StartingRelics</c> -- Salon Solitaire replaces the Ethereal
///     Spotlight (brief sec.3 rule 2).
///   * <c>Furina.StartingDeck</c> -- the two kit slots become three: Salon
///     Debut, Curtain Rise, Standing Ovation (sec.7's named starter).
///   * <c>FurinaResourceHooks.ModifyHpLostBeforeOsty</c> -- the damage order,
///     sec.3 rule 6. The one seam that touches a SHIPPED file's behaviour, and
///     it returns the shipped number with the arm off.
///   * <c>FurinaStageHooks</c> -- the lead's regen at her turn start (rule 4)
///     and the performers' acts at her turn end (rule 10), an arm-only
///     listener that does nothing on a board with no stage.
///
/// FURINA'S OWN HP IS TOUCHED BY NOTHING HERE (sec.3 rule 11), and that is
/// worth stating as a property of the code and not only of the design: no path
/// in this arm heals, drains or caps her bar. What the arm adds is three bars
/// that are not hers.
///
/// THE REFRAME IS NOT DELETED BY THIS BRANCH, and that is disclosed rather
/// than assumed: brief sec.2 retires <c>FURINA_REFRAME</c>, but the brief is
/// OPEN (its sec.11 picks are unruled) and the reframe's surface is a sim
/// engine module, twenty-odd sheet rows and some five thousand lines of pins.
/// Building this arm BESIDE it is the reversible move; the two are
/// independent switches and a build carrying both is not a supported
/// configuration of the design, only of the compiler.
/// </summary>
public static class FurinaStage
{
    /// <summary>
    /// The arm's default: <c>-p:FurinaStage=true</c> turns it on, and a
    /// release package never passes it.
    /// </summary>
    public const bool DefaultEnabled =
#if FURINA_STAGE
        true;
#else
        false;
#endif

    /// <summary>The master, and the only flag. Settable so one build can pin
    /// both sides of it.</summary>
    public static bool Enabled { get; set; } = DefaultEnabled;

    /// <summary>
    /// Is the stage live for THIS creature? Identity is
    /// <see cref="FurinaResources.IsFurina"/>, which is what
    /// <c>tools/lint_prototype_patch_scope.py</c> requires of anything running
    /// on every seat at the table under the one prototype switch: in co-op the
    /// other seat is not hers and must not grow a stage.
    /// </summary>
    /// <remarks>The null test is FIRST and is load-bearing:
    /// <c>FurinaResources.IsFurina</c> dereferences its argument, so a caller
    /// with no creature -- a compendium page, a card on a shelf, a hook fired
    /// on a board being torn down -- would throw rather than answer.</remarks>
    public static bool LiveFor(Creature? creature) =>
        creature != null && Enabled && FurinaResources.IsFurina(creature);
}

/// <summary>
/// THE THREE PERFORMERS. Genshin's Salon Solitaire summons Surintendante
/// Chevalmarin, Mademoiselle Crabaletta and the Gentilhomme Usher; the brief's
/// sec.2 table keeps the three and gives each an act and a bow.
///
/// A NEW ENUM RATHER THAN <c>SalonMember</c>, which spells the same three
/// names one arm over. They are different things wearing one cast list: a
/// <c>SalonMember</c> is a POWER on Furina with a tick value and an Encore
/// price, a performer here is a PET with a bar. Sharing the enum would have
/// made every reader of either arm ask which rule a value carried, and the two
/// arms' rules contradict each other on every clause.
/// </summary>
public enum StagePerformer
{
    Usher,
    Chevalmarin,
    Crabaletta,
}

/// <summary>
/// THE NUMBERS, all of them, from brief sec.3 and sec.10 default 3.
///
/// UNMIRRORED, DECLARED, AND WHY. Every arm before this one mirrored its
/// constants out of the sim by value through
/// <c>tools/lint_constant_parity.py</c>, because R220 B sequenced their C#
/// legs last. This one is the other way round: `docs/current/operations/prototype.md`
/// says **C# FIRST, sim at Balance** -- "a new kit rule is implemented in the
/// C# mod behind the prototype switch and nowhere else, and the Python sim is
/// brought up only once the rule survives the Prototype gate". So these are
/// the FIRST declaration of each number, filed UNMIRRORED with that reason
/// rather than mirrored against a module that does not exist yet, and the sim
/// twin inherits them when the stage reaches Balance.
///
/// THEY ARE PLACEHOLDERS AND NOT CLAIMS, the same standing
/// <c>KleeOverhaulLaw</c>'s four opened on -- but they are the placeholders
/// both engines will have to agree on, so they are written down once and
/// interpolated into every face and tip that quotes one (`EB-89`).
/// </summary>
public static class FurinaStageLaw
{
    /// <summary>Front, middle, back (rule 1).</summary>
    public const int SeatCount = 3;

    /// <summary>Usher's opening bar, granted by the relic (rule 2).</summary>
    public const int OpeningFanfare = 3;

    /// <summary>What a summon fields a performer at (rule 3).</summary>
    public const int SummonFanfare = 1;

    /// <summary>The lead's regen at the start of her turn (rule 4).</summary>
    public const int LeadRegen = 1;

    /// <summary>
    /// The FIRST turn the regen pays. Rule 4 says "from her SECOND turn on":
    /// the relic's 3 is the opening bar and a regen on turn one would make it
    /// a 4 nobody printed.
    /// </summary>
    public const int RegenFromTurn = 2;

    /// <summary>Standing Ovation's Raise, on the back performer (rule 5).
    /// </summary>
    public const int RefillAmount = 5;

    /// <summary>Usher's act: Furina gains Block (rule 10).</summary>
    public const int UsherActBlock = 3;

    /// <summary>Chevalmarin's act: damage to every enemy, plus Hydro
    /// (rule 10).</summary>
    public const int ChevalmarinActDamage = 2;

    /// <summary>Crabaletta's act: damage to a random enemy (rule 10).</summary>
    public const int CrabalettaActDamage = 5;

    /// <summary>Usher's bow: Furina gains Block (rule 9).</summary>
    public const int UsherBowBlock = 4;

    /// <summary>Crabaletta's bow: damage to a random enemy (rule 9).</summary>
    public const int CrabalettaBowDamage = 8;
}
