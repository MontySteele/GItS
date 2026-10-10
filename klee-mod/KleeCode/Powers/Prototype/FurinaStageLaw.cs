namespace KleeMod.Powers;

/// <summary>
/// FURINA, THE SALON'S TAB -- the kit's numbers, and nothing else.
///
/// <para>THE DESIGN is <c>review/active/furina-research-proposal-2026-10-05.md</c>:
/// sec.2's rules with sec.16's Repay and curtain call, sec.16's slice and
/// sec.17's two edits. The sim's Furina arm (<c>tier0/engine/furina_stage.py</c>,
/// on the rules of <c>tier0/engine/furina_tide.py</c>) declares every number
/// below under the same name, and <c>tools/lint_constant_parity.py</c>
/// compares the two by value.</para>
///
/// <para>PROTOTYPE SEEDS, not ruled balance: measurement law binds only at
/// Balance (<c>docs/current/EXPERIMENTS.md</c>).</para>
/// </summary>
public static class FurinaStageLaw
{
    /// <summary>Rule 5: three guest seats (four with Ensemble Cast). Mirrors
    /// <c>furina_stage.SEATS</c>.</summary>
    public const int Seats = 3;

    /// <summary>Rule 4: Salon Solitaire, "At the end of your turn, Repay 1."
    /// (2026-10-09 playtest trim, was 2.)
    /// Mirrors <c>furina_stage.SINGER_REPAY</c>.</summary>
    public const int SingerRepay = 1;

    /// <summary>Salon Solitaire upgraded ([2], 2026-10-09 trim, was 3): The Curtain Never Falls, its
    /// Touch of Orobas replacement. Mirrors
    /// <c>furina_stage.SINGER_REPAY_UPGRADED</c>.</summary>
    public const int SingerRepayUpgraded = 2;

    // ---- the first four guests (sec.16) ------------------------------------------

    /// <summary>Charlotte's act: "Repay 2."</summary>
    public const int CharlotteActRepay = 2;

    /// <summary>Charlotte's line: "The first time one of your cards Repays
    /// each turn, draw 1 card." (The Spend round 2, 2026-10-10: her own act
    /// and Salon Solitaire no longer count.)</summary>
    public const int CharlotteLineDraw = 1;

    /// <summary>Wriothesley's act: "Deal 4 Cryo damage to a random enemy."
    /// (His line deals the HP drained.)</summary>
    public const int WriothesleyActDamage = 4;

    /// <summary>Lynette's act: "Deal 3 Anemo damage to an enemy with an
    /// aura." (Her line pays the first HP an enemy takes each turn again.)
    /// </summary>
    public const int LynetteActDamage = 3;

    /// <summary>Clorinde's act: "Deal 6 Electro damage to a random enemy."
    /// </summary>
    public const int ClorindeActDamage = 6;

    /// <summary>Clorinde's line: "Whenever you Repay, deal twice that much
    /// Electro damage to a random enemy."</summary>
    public const int ClorindePerRepay = 2;

    // ---- the pool to 39 (review/active/furina-pool-40-2026-10-05.md) ------

    /// <summary>Lyney's line: "Your Drain line is 10 HP lower."</summary>
    public const int LyneyLineDrop = 10;

    /// <summary>Lyney's act: "Drain 2, never past your line (none at or below
    /// it). Deal 8 Pyro
    /// damage to ALL enemies." A guest's Drain stops at the line (the
    /// drain-line round, 2026-10-09): it drains only the room above it, and
    /// the damage lands either way.</summary>
    public const int LyneyActDrain = 2;

    /// <summary>Lyney's act's damage.</summary>
    public const int LyneyActDamage = 8;

    /// <summary>Sigewinne's act: "Repay 2." (Her line gives the Block of
    /// every Repay.)</summary>
    public const int SigewinneActRepay = 2;

    /// <summary>Chevreuse's act: "Deal 4 damage to a random enemy."</summary>
    public const int ChevreuseActDamage = 4;

    /// <summary>Chevreuse's line: "Whenever you Spend, apply 1 Vulnerable to
    /// a random enemy."</summary>
    public const int ChevreuseLineVulnerable = 1;

    /// <summary>THE DRAIN FLOOR (the Drain line rule, 2026-10-09): a Drain
    /// is never refused for the line, but it cannot take her to 0 HP -- the
    /// lowest HP a Drain may reach is 1. Also the floor Lyney's line cannot
    /// push the line below.</summary>
    public const int DrainFloor = 1;

    /// <summary>Fountain of Lucine: "At the start of your next 3 turns,
    /// Repay 3."</summary>
    public const int FountainTurns = 3;

    // ---- the pool to 75 (review/active/furina-pool-growth-2026-10-09.md) --
    // Sec.3's guest rule: a guest's upgrade raises its line or its act,
    // never its cost (the table of seven built guests, and sec.5's four).

    /// <summary>Charlotte upgraded: "Act: Repay 4."</summary>
    public const int CharlotteActRepayUpgraded = 4;

    /// <summary>Sigewinne upgraded: "Act: Repay 4."</summary>
    public const int SigewinneActRepayUpgraded = 4;

    /// <summary>Wriothesley upgraded: "Act: 7."</summary>
    public const int WriothesleyActDamageUpgraded = 7;

    /// <summary>Lyney upgraded: "Act: 11."</summary>
    public const int LyneyActDamageUpgraded = 11;

    /// <summary>Lynette upgraded: "Act: 6."</summary>
    public const int LynetteActDamageUpgraded = 6;

    /// <summary>Chevreuse upgraded: "Line: also 1 Weak."</summary>
    public const int ChevreuseLineWeakUpgraded = 1;

    /// <summary>Clorinde upgraded: "Act: 9."</summary>
    public const int ClorindeActDamageUpgraded = 9;

    /// <summary>Freminet's act: "Deal 5 Cryo damage to a random enemy."
    /// [8] (His line gives the Block of every Drain.)</summary>
    public const int FreminetActDamage = 5;

    public const int FreminetActDamageUpgraded = 8;

    /// <summary>Freminet's act also gives Block (the pool-75 round's card
    /// numbers, ruled 2026-10-09): "gain 6 Block." [9]</summary>
    public const int FreminetActBlock = 6;

    public const int FreminetActBlockUpgraded = 9;

    /// <summary>Navia's line: "Your first Spend each turn costs 2 less (a
    /// spend-all keeps 2)." [3] (Her act deals the Fanfare spent this turn
    /// as Geo.)</summary>
    public const int NaviaLineDiscount = 2;

    public const int NaviaLineDiscountUpgraded = 3;

    /// <summary>Neuvillette's line: "Your Hydro damage deals 2 more." [3]
    /// (His act deals the HP she lost since her last turn -- Drained or
    /// taken -- to ALL as Hydro; 2026-10-09.)</summary>
    public const int NeuvilletteHydroBonus = 2;

    public const int NeuvilletteHydroBonusUpgraded = 3;

    /// <summary>Escoffier's act: "Deal 4 Cryo damage to ALL enemies." [6]
    /// </summary>
    public const int EscoffierActDamage = 4;

    public const int EscoffierActDamageUpgraded = 6;

    /// <summary>Escoffier's line: "Whenever a guest acts, Repay 1."</summary>
    public const int EscoffierLineRepay = 1;

    /// <summary>Ensemble Cast: "You have 4 guest seats."</summary>
    public const int EnsembleSeats = 4;

    /// <summary>Showstopper: "At the end of your turn, Spend 5: your guests
    /// act again."</summary>
    public const int ShowstopperSpend = 5;

    /// <summary>Against the Tide: "within 5 HP of your Drain line".</summary>
    public const int NearLine = 5;

    /// <summary>High Stakes (the Spend round 2, 2026-10-10,
    /// <c>review/records/furina-spend-round-2-2026-10-10.md</c>): "Your
    /// Attacks deal 1 additional damage for every 5 HP you have Drained this
    /// combat." The card's power amount is this divisor. Mirrors
    /// <c>furina_stage.HIGH_STAKES_EVERY</c>.</summary>
    public const int HighStakesEvery = 5;

    /// <summary>High Stakes upgraded: "for every 4".</summary>
    public const int HighStakesEveryUpgraded = 4;

    /// <summary>High Stakes' bonus a hit: the HP drained this combat, gross
    /// (no Repay lowers it), over <paramref name="every"/>, rounded down. 0
    /// for a divisor below 1.</summary>
    public static int HighStakesBonus(int drained, int every) =>
        every > 0 && drained > 0 ? drained / every : 0;

    /// <summary>What a hit's High Stakes bonus counts for the telemetry: the
    /// bonus, never more than the hit dealt (HP and Block).</summary>
    public static int HighStakesCredit(int bonus, int dealt) =>
        System.Math.Max(0, System.Math.Min(bonus, dealt));

    /// <summary>Hymn of Renewal: "Whenever you Repay 4 or more HP at once,
    /// gain 1 Strength." (HP actually repaid.)</summary>
    public const int HymnThreshold = 4;

    /// <summary>Prima Donna: "if you have 10 or more Fanfare, gain 1
    /// Energy."</summary>
    public const int PrimaDonnaFanfare = 10;

    /// <summary>Regina of All Waters: "At the start of your turn, Drain 3.
    /// If you do, gain 1 Strength."</summary>
    public const int ReginaDrain = 3;

    /// <summary>Star Turn: "Costs 1 less for every 6 Fanfare you have."
    /// </summary>
    public const int StarTurnFanfarePer = 6;

    /// <summary>Is <paramref name="hp"/> within <see cref="NearLine"/> HP of
    /// <paramref name="line"/>: at most 5 over it, or at or below it (a Drain
    /// may go past the line since 2026-10-09, and any HP at or below the line
    /// counts).</summary>
    public static bool NearTheLine(int hp, int line) => hp - line <= NearLine;

    /// <summary>
    /// Rule 1: THE LINE (the Drain line rule, ruled 2026-10-09, quarter of
    /// Max HP the same day): the HP she started this combat with, minus 1/4
    /// of the Max HP she started it with, the quarter rounded DOWN (80 Max
    /// HP takes 20, 85 takes 21). Entering at 50/80 the line is 30: 20 HP of
    /// room. Never below 0. A Drain may go past it; HP drained past it is
    /// lost at the curtain call unless Repaid. Integer throughout, so the
    /// sim (<c>furina_tide.half_line</c>) computes the same number.
    /// </summary>
    public static int LineOf(int entryHp, int maxHp) =>
        System.Math.Max(0, System.Math.Max(0, entryHp)
                           - System.Math.Max(0, maxHp) / LineMaxHpDivisor);

    /// <summary>The line's room is 1/4 of her Max HP, rounded down. Mirrors
    /// <c>furina_tide.LINE_MAX_HP_DIVISOR</c>.</summary>
    public const int LineMaxHpDivisor = 4;

    /// <summary>The line with its one mover: Lyney on stage lowers it by 10,
    /// never below 1. (A Five-Century Act no longer moves it: it returns the
    /// HP drained past it instead.)</summary>
    public static int LineOf(int entryHp, int maxHp, bool lyney)
    {
        var line = LineOf(entryHp, maxHp);
        return lyney ? System.Math.Max(DrainFloor, line - LyneyLineDrop)
                     : line;
    }

    /// <summary>Where the line comes from, in words, for its hover and the
    /// seat page (2026-10-05: seats connected the line to their entry HP
    /// only late). The same two branches as
    /// <see cref="LineOf(int, int, bool)"/>.</summary>
    public static string LineWhy(bool lyney) =>
        lyney ? LineWhyBase + ", " + LyneyLineDrop
                + " lower with Lyney on stage"
              : LineWhyBase;

    /// <summary>The base line's source, in the base game's words.</summary>
    public const string LineWhyBase =
        "the HP you started this fight with, minus 1/4 of your Max HP";

    /// <summary>A line of 0 explains itself (the Spend round 2, 2026-10-10:
    /// a seat read a line of 0 as "every Drain is permanent", which is
    /// backwards). At 0 every Drain stays above the line, so all of it
    /// returns. Plain words; the counter's hover golds the verb.</summary>
    public const string LineZeroReturns =
        "all your Drain returns after combat";
}
