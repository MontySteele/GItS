namespace KleeMod.Powers;

/// <summary>
/// FURINA, THE STAGE (v2, the re-founding) -- the arm's numbers, and nothing
/// else.
///
/// <para>THE DESIGN is <c>review/active/furina-refounding-2026-10-03.md</c>:
/// sec.1's rules as sec.8 amends them, sec.2's cast, and sec.10's full sheet,
/// which overrides the earlier text where they differ. The sim's reference
/// implementation is <c>tier0/engine/furina_v2.py</c>; the sim's Furina arm
/// (<c>tier0/engine/furina_stage.py</c>) declares every number below under the
/// same name, and <c>tools/lint_constant_parity.py</c> compares the two by
/// value.</para>
///
/// <para>PROTOTYPE SEEDS, not ruled balance: measurement law binds only at
/// Balance (<c>docs/current/EXPERIMENTS.md</c>).</para>
/// </summary>
public static class FurinaStageLaw
{
    /// <summary>Rule 1: three seats. Mirrors <c>furina_stage.SEATS</c>.</summary>
    public const int Seats = 3;

    /// <summary><i>Sold Out</i>: "Your stage has a fourth seat." Mirrors
    /// <c>furina_stage.SOLD_OUT_SEATS</c>.</summary>
    public const int SoldOutSeats = 4;

    /// <summary><i>Casting Agent</i>: "Choose 1 of 3 random Guest Star
    /// cards." Mirrors <c>furina_stage.CASTING_AGENT_OFFER</c>.</summary>
    public const int CastingAgentOffer = 3;

    /// <summary>Rule 3: every Bow gives this much Fanfare, after its act.
    /// Mirrors <c>furina_stage.BOW_FANFARE</c>.</summary>
    public const int BowFanfare = 1;

    // ---- the Salon trio (sec.2) ----------------------------------------

    /// <summary>Usher's act: Block. Mirrors <c>ACT_USHER_BLOCK</c>.</summary>
    public const int ActUsherBlock = 4;

    /// <summary>Chevalmarin's act: damage to ALL enemies. Mirrors
    /// <c>ACT_CHEVALMARIN_DAMAGE</c>.</summary>
    public const int ActChevalmarinDamage = 2;

    /// <summary>Crabaletta's act: damage to a random enemy. Mirrors
    /// <c>ACT_CRABALETTA_DAMAGE</c>.</summary>
    public const int ActCrabalettaDamage = 5;

    // ---- the stars (sec.2, sec.8, sec.10): they pay for their acts --------

    /// <summary>Neuvillette pays this much...</summary>
    public const int ActNeuvillettePrice = 2;

    /// <summary>...for this much Hydro damage to ALL enemies.</summary>
    public const int ActNeuvilletteDamage = 7;

    /// <summary>His line: "Your Hydro damage deals 2 more" (sec.10), per
    /// Hydro hit, cards and acts alike, while he is on stage.</summary>
    public const int NeuvilletteHydroBonus = 2;

    /// <summary>Clorinde pays this much...</summary>
    public const int ActClorindePrice = 1;

    /// <summary>...for this much Electro damage to a random enemy
    /// (sec.10: 6, was 8).</summary>
    public const int ActClorindeDamage = 6;

    /// <summary>Her line: "Whenever you Spend, deal 4 Electro damage to a
    /// random enemy." A line, not an act: Rehearsal does not touch it.
    /// </summary>
    public const int ClorindeSpendDamage = 4;

    /// <summary>Lyney pays this much to add a Trick to your hand.</summary>
    public const int ActLyneyPrice = 1;

    /// <summary>The Trick token: "Deal 4 Pyro damage. Retain. Exhaust."
    /// </summary>
    public const int TrickDamage = 4;

    /// <summary>Escoffier pays this much: "your Salon members act".</summary>
    public const int ActEscoffierPrice = 2;

    /// <summary>Navia's act is free: Geo damage equal to this times the
    /// Fanfare you spent this turn.</summary>
    public const int NaviaPerSpent = 2;

    // ---- the supports (sec.2): free ----------------------------------------

    /// <summary>Charlotte's act: gain 1 Fanfare.</summary>
    public const int ActCharlotteGain = 1;

    /// <summary>Charlotte's line: at the start of your turn, draw 1 more.
    /// </summary>
    public const int CharlotteExtra = 1;

    /// <summary>Lynette's act: Anemo damage to an enemy with an aura, if
    /// any.</summary>
    public const int ActLynetteDamage = 3;

    /// <summary>Chevreuse's act, the first time each turn: pay 2...</summary>
    public const int ActChevreusePrice = 2;

    /// <summary>...to gain 1 Energy next turn.</summary>
    public const int ActChevreuseEnergy = 1;

    /// <summary>Sigewinne's act: 3 Block...</summary>
    public const int ActSigewinneBlock = 3;

    /// <summary>...plus 2 for each time you lost HP since her last act.
    /// </summary>
    public const int SigewinnePerHpLoss = 2;

    /// <summary>Wriothesley's act: 4 Cryo damage to a random enemy...
    /// </summary>
    public const int ActWriothesleyDamage = 4;

    /// <summary>...plus 1 per damage your Block stopped since his last act.
    /// </summary>
    public const int WriothesleyPerBlocked = 1;

    /// <summary>The price a star's (or Chevreuse's) act pays, 0 for every
    /// free act.</summary>
    public static int PriceOf(StagePerformer who) => who switch
    {
        StagePerformer.Neuvillette => ActNeuvillettePrice,
        StagePerformer.Clorinde => ActClorindePrice,
        StagePerformer.Lyney => ActLyneyPrice,
        StagePerformer.Escoffier => ActEscoffierPrice,
        StagePerformer.Chevreuse => ActChevreusePrice,
        _ => 0,
    };

    /// <summary>Sigewinne's act before Rehearsal.</summary>
    public static int SigewinneBlock(int hpLosses) =>
        ActSigewinneBlock + SigewinnePerHpLoss * System.Math.Max(0, hpLosses);

    /// <summary>Wriothesley's act before Rehearsal.</summary>
    public static int WriothesleyDamage(int blocked) =>
        ActWriothesleyDamage + WriothesleyPerBlocked * System.Math.Max(0, blocked);
}
