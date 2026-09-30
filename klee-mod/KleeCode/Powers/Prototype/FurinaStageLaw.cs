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

    /// <summary><i>Sold Out</i> (the supporting pool, 2026-09-26): "Your
    /// stage has a fourth seat." Front, two middles, back, for the rest of the
    /// combat; a second copy adds nothing. What
    /// <see cref="FurinaStageLedger.Capacity"/> reads while the power is on
    /// her. Mirrors <c>furina_stage.SOLD_OUT_SEATS</c>.</summary>
    public const int SoldOutSeats = 4;

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

    // THE GUEST CAST (2026-09-25, review/active/furina-guest-batch-2026-09-25.md
    // and the build packet's table). The acts' own numbers; what each guest
    // ARRIVES with is its card's, on its row. Each mirrors the
    // `furina_stage.ACT_*` of the same name.

    /// <summary>Neuvillette pays this much of his own Fanfare...</summary>
    public const int ActNeuvillettePrice = 3;

    /// <summary>...to deal this much Hydro damage to ALL enemies.</summary>
    public const int ActNeuvilletteDamage = 8;

    /// <summary>Clorinde takes this much from each other performer...
    /// </summary>
    public const int ActClorindeTax = 1;

    /// <summary>...to deal this much Electro damage to a random enemy, however
    /// many paid.</summary>
    public const int ActClorindeDamage = 8;

    /// <summary>Chevreuse Spends this much from the back performer...
    /// </summary>
    public const int ActChevreusePrice = 2;

    /// <summary>...to gain this much Energy next turn.</summary>
    public const int ActChevreuseEnergy = 1;

    /// <summary>Wriothesley's act always deals this much Cryo damage...
    /// (2026-09-27: "I think that Wriothesley needs a buff.")</summary>
    public const int ActWriothesleyBase = 4;

    /// <summary>...plus this many times the Fanfare enemy hits took from him
    /// since his last act...</summary>
    public const int ActWriothesleyRate = 2;

    /// <summary>...plus this many times the damage Furina's Block stopped
    /// from enemy hits while he stood in front ("he also reflects the
    /// Blocked damage").</summary>
    public const int ActWriothesleyBlockedRate = 1;

    /// <summary>Wriothesley's act, before Ousia: the base, plus what hits
    /// took from him, plus what her Block stopped while he was in front.
    /// </summary>
    public static int WriothesleyAct(int lost, int blocked) =>
        ActWriothesleyBase + ActWriothesleyRate * lost
        + ActWriothesleyBlockedRate * blocked;

    /// <summary>Sigewinne the medic (2026-09-29, [USER]: "I think Siegwinne
    /// needs to be rethought - she's strictly fanfare-negative while she's
    /// summoned"): her act is free, and the front performer regains half the
    /// Fanfare hits took from it since her last act, rounded down, at least
    /// this. Mirrors <c>furina_stage.ACT_SIGEWINNE_HEAL_FLOOR</c>.</summary>
    public const int ActSigewinneHealFloor = 2;

    /// <summary>Sigewinne's heal: half of <paramref name="frontLost"/>,
    /// rounded down, at least <see cref="ActSigewinneHealFloor"/>. Mirrors
    /// <c>furina_stage.sigewinne_heal</c>.</summary>
    public static int SigewinneHeal(int frontLost) =>
        System.Math.Max(ActSigewinneHealFloor,
                        frontLost <= 0 ? 0 : frontLost / 2);

    /// <summary>Charlotte: each other performer gains this much.</summary>
    public const int ActCharlotteGift = 1;

    /// <summary>Lynette deals this much Anemo damage to a random enemy, one
    /// with an aura if any (2026-09-25 night, the granted-guest seat round:
    /// the act now always lands).</summary>
    public const int ActLynetteDamage = 3;

    // THE SUPPORTING POOL (2026-09-26, review/active/furina-supporting-pool-
    // 2026-09-26.md): two more guests. Each mirrors the `furina_stage.ACT_*`
    // of the same name.

    /// <summary>Lyney pays this much of his own Fanfare...</summary>
    public const int ActLyneyPrice = 2;

    /// <summary>...to deal this much Pyro damage to a random enemy; then,
    /// if he is not in front, he swaps with the front performer (the
    /// 2026-09-26 seat round).</summary>
    public const int ActLyneyDamage = 6;

    /// <summary>Escoffier pays this much of her own Fanfare...</summary>
    public const int ActEscoffierPrice = 3;

    /// <summary>...to give each other performer this much...</summary>
    public const int ActEscoffierGift = 2;

    /// <summary>...and deal this much Cryo damage to ALL enemies.</summary>
    public const int ActEscoffierDamage = 3;

    /// <summary>
    /// RULE 12, THE APPLAUSE FADES. THE FADE PASS (2026-09-29; [USER]: "What
    /// about a percentage fade, say 25%? Anything below 4 rounds to losing
    /// 0."): at the end of Furina's turn, after the acts, EVERY performer, the
    /// front one included, loses its Fanfare divided by this, rounded down
    /// (<see cref="FadeLoss"/>). Was half of the Fanfare above 5, behind the
    /// front only (draft 3). Mirrors <c>furina_stage.FADE_DIVISOR</c>.
    /// </summary>
    public const int FadeDivisor = 4;

    /// <summary>
    /// Rule 12's arithmetic, ONE function so the divisor is tuned in one
    /// place: a quarter of the Fanfare, rounded down. 0-3 -> 0, 4-7 -> 1,
    /// 8-11 -> 2, 12 -> 3, 20 -> 5. It never takes a whole bar, so it never
    /// empties a performer. Mirrors <c>furina_stage.fade_loss</c>.
    /// </summary>
    public static int FadeLoss(int fanfare) =>
        fanfare <= 0 ? 0 : fanfare / FadeDivisor;
}
