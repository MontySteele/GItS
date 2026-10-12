using System;
using System.Collections.Generic;
using System.Linq;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Random;

namespace KleeMod.Abyss;

/// <summary>One option on the choice page: the Blessing it gives, and the
/// Shadow it brings into the enemies' roll if it is passed.</summary>
public readonly record struct AbyssOption(AbyssBlessing Blessing, AbyssShadow Shadow);

/// <summary>
/// One act's page: three options and the roll that decides which of the two
/// passed Shadows the enemies take. The roll is drawn when the page is drawn,
/// so it does not depend on when, or by whom, the option is picked.
/// </summary>
public sealed class AbyssOffer
{
    public AbyssOffer(int actIndex, IReadOnlyList<AbyssOption> options, int shadowRoll)
    {
        ActIndex = actIndex;
        Options = options;
        ShadowRoll = shadowRoll;
    }

    public int ActIndex { get; }

    public IReadOnlyList<AbyssOption> Options { get; }

    /// <summary>0 or 1: which of the two passed options' Shadows the enemies
    /// take, counting in page order.</summary>
    public int ShadowRoll { get; }

    /// <summary>The Shadow the enemies take if option <paramref name="chosen"/>
    /// is taken.</summary>
    public AbyssShadow ShadowIfChosen(int chosen)
    {
        var passed = Options.Where((_, i) => i != chosen).ToList();
        if (passed.Count == 0) return AbyssShadow.None;
        return passed[Math.Min(ShadowRoll, passed.Count - 1)].Shadow;
    }
}

/// <summary>
/// The page generator. PURE: a function of the run's seed, the act and what
/// the run has already taken, so a reload draws the same page and the same
/// roll, and two co-op peers draw the same page without a message.
///
/// NO ENTRY REPEATS IN A RUN (paper sec.1): a Blessing already taken and a
/// Shadow already on the enemies are never offered again. Passed entries can
/// come back in a later act -- three acts need nine Blessing slots and the
/// pool has eight, so "never offered twice" cannot be what the rule means.
/// </summary>
public static class AbyssDraft
{
    public const string RngName = "spiral_abyss";

    public const int OptionCount = 3;

    public static IReadOnlyList<AbyssBlessing> AllBlessings { get; } =
        Enum.GetValues<AbyssBlessing>().Where(b => b != AbyssBlessing.None).ToArray();

    public static IReadOnlyList<AbyssShadow> AllShadows { get; } =
        Enum.GetValues<AbyssShadow>().Where(s => s != AbyssShadow.None).ToArray();

    public static AbyssOffer Offer(
        ulong runSeed, int actIndex,
        IEnumerable<AbyssBlessing> taken, IEnumerable<AbyssShadow> applied)
    {
        var rng = new Rng(runSeed + (ulong)Math.Max(0, actIndex), RngName);

        var blessings = AllBlessings.Except(taken).ToList();
        var shadows = AllShadows.Except(applied).ToList();
        rng.Shuffle(blessings);
        rng.Shuffle(shadows);

        var count = Math.Min(OptionCount, Math.Min(blessings.Count, shadows.Count));
        var options = new List<AbyssOption>(count);
        for (var i = 0; i < count; i++)
        {
            options.Add(new AbyssOption(blessings[i], shadows[i]));
        }

        var roll = rng.NextInt(2);
        return new AbyssOffer(actIndex, options, roll);
    }

    /// <summary>The page for <paramref name="actIndex"/> given a record.</summary>
    public static AbyssOffer Offer(ulong runSeed, int actIndex, AbyssRecord record) =>
        Offer(runSeed, actIndex, record.Blessings, record.Shadows);
}

/// <summary>
/// What the run has taken, act by act: three parallel lists, which is the
/// shape the save stores (three <c>int[]</c> SavedProperties on
/// <see cref="SpiralAbyss"/>). Everything else -- the next page, the roll --
/// is recomputed from this and the seed.
/// </summary>
public sealed class AbyssRecord
{
    private readonly List<int> _acts = new();
    private readonly List<AbyssBlessing> _blessings = new();
    private readonly List<AbyssShadow> _shadows = new();

    public IReadOnlyList<int> Acts => _acts;

    public IReadOnlyList<AbyssBlessing> Blessings => _blessings;

    public IReadOnlyList<AbyssShadow> Shadows => _shadows;

    public bool HasPicked(int actIndex) => _acts.Contains(actIndex);

    public bool Has(AbyssBlessing b) => _blessings.Contains(b);

    public bool Has(AbyssShadow s) => _shadows.Contains(s);

    /// <summary>
    /// Record act <paramref name="actIndex"/>'s pick. IDEMPOTENT per act: a
    /// shared event runs the chosen option once per player, and only the first
    /// call records. Returns whether this call recorded.
    /// </summary>
    public bool Record(int actIndex, AbyssBlessing blessing, AbyssShadow shadow)
    {
        if (HasPicked(actIndex)) return false;
        _acts.Add(actIndex);
        _blessings.Add(blessing);
        _shadows.Add(shadow);
        return true;
    }

    public void Clear()
    {
        _acts.Clear();
        _blessings.Clear();
        _shadows.Clear();
    }

    public int[] ActsArray() => _acts.ToArray();

    public int[] BlessingsArray() => _blessings.Select(b => (int)b).ToArray();

    public int[] ShadowsArray() => _shadows.Select(s => (int)s).ToArray();

    public void LoadActs(int[]? acts)
    {
        _acts.Clear();
        if (acts != null) _acts.AddRange(acts);
    }

    public void LoadBlessings(int[]? blessings)
    {
        _blessings.Clear();
        if (blessings != null) _blessings.AddRange(blessings.Select(b => (AbyssBlessing)b));
    }

    public void LoadShadows(int[]? shadows)
    {
        _shadows.Clear();
        if (shadows != null) _shadows.AddRange(shadows.Select(s => (AbyssShadow)s));
    }
}

/// <summary>
/// Every decision a Blessing or Shadow makes, as a pure function, so the
/// headless suite can pin each one without a live combat. The modifier's hooks
/// gather the facts and call these.
/// </summary>
public static class AbyssRules
{
    /// <summary>The Ley Line's "deals 1 less damage", for one hit.</summary>
    public static decimal LeyLineDamageDelta(
        bool dealerIsEnemy, bool dealerHasAura, bool isPoweredAttack, decimal amount)
    {
        if (!dealerIsEnemy || !dealerHasAura || !isPoweredAttack) return 0m;
        return -Math.Min(AbyssNumbers.LeyLineDamageReduction, Math.Max(0m, amount));
    }

    /// <summary>The Ley Line's application: an enemy with no aura takes the
    /// element; one already wearing an aura is left alone.</summary>
    public static bool LeyLineApplies(bool isEnemy, bool isAlive, bool hasAura) =>
        isEnemy && isAlive && !hasAura;

    /// <summary>Abyssal Moon: true when this card is the turn's third, sixth...</summary>
    public static bool AbyssalMoonFires(int cardsPlayedThisTurnIncludingThis) =>
        cardsPlayedThisTurnIncludingThis > 0
        && cardsPlayedThisTurnIncludingThis % AbyssNumbers.AbyssalMoonEvery == 0;

    /// <summary>First Strike: extra plays for this card.</summary>
    /// <summary>First Strike's history read, as a pure function: has
    /// <paramref name="owner"/> already started an Attack this combat? Each
    /// entry is one play the combat history holds (who, whether it was the
    /// first of its series, whether it was an Attack). A replay of a card is
    /// not a new Attack; another player's Attack is not this player's. The
    /// play being sized is not in the history yet (see
    /// <c>SpiralAbyss.ModifyCardPlayCount</c>), so an empty history is
    /// "no".</summary>
    public static bool AttackAlreadyStarted<TPlayer>(
        IEnumerable<(TPlayer Player, bool FirstInSeries, bool IsAttack)> started, TPlayer owner)
        where TPlayer : class =>
        started.Any(e => ReferenceEquals(e.Player, owner) && e.FirstInSeries && e.IsAttack);

    public static int FirstStrikeExtraPlays(bool isAttack, bool attackAlreadyPlayedThisCombat) =>
        isAttack && !attackAlreadyPlayedThisCombat ? 1 : 0;

    /// <summary>Elemental Burst: does this play pay?</summary>
    public static bool ElementalBurstFires(bool isPower, bool isFirstInSeries) =>
        isPower && isFirstInSeries;

    /// <summary>Resonance: turn 1 only.</summary>
    public static bool ResonanceApplies(int playerTurnNumber) =>
        playerTurnNumber <= AbyssNumbers.ResonanceTurn;

    /// <summary>The Clock: from round 5.</summary>
    public static bool ClockApplies(int roundNumber) =>
        roundNumber >= AbyssNumbers.ClockFromRound;

    /// <summary>Sheer Cold: you ended the turn with no Block.</summary>
    public static bool SheerColdApplies(bool isPlayer, bool isAlive, int block) =>
        isPlayer && isAlive && block <= 0;

    /// <summary>Elemental Mark and Riptide share their trigger: an enemy's
    /// attack dealt a player unblocked damage.</summary>
    public static bool EnemyAttackLanded(
        bool targetIsPlayer, bool dealerIsEnemy, bool isPoweredAttack, int unblockedDamage) =>
        targetIsPlayer && dealerIsEnemy && isPoweredAttack && unblockedDamage > 0;

    /// <summary>Abyss Herald: the max HP added to a body. 15%, rounded half
    /// away from zero.</summary>
    public static int HeraldBonus(int maxHp) =>
        maxHp <= 0
            ? 0
            : (int)Math.Round(maxHp * AbyssNumbers.HeraldHpBonus, MidpointRounding.AwayFromZero);

    /// <summary>Abyss Mage Shield and Fatui Skirmishers' room filters.</summary>
    public static bool MageShieldRoom(bool isElite) => isElite;

    public static bool FatuiRoom(bool isElite, bool isBoss) => isElite || isBoss;

    /// <summary>The shield after one hit: the counter element breaks it
    /// whole, any other hit removes 1.</summary>
    public static int ShieldAfterHit(int hits, Element hitElement, Element shieldElement)
    {
        if (hits <= 0) return 0;
        var counter = AbyssElements.CounterOf(shieldElement);
        if (counter != Element.None && hitElement == counter) return 0;
        return Math.Max(0, hits - AbyssNumbers.MageShieldPerHit);
    }

    /// <summary>The shield after one reaction on its wearer.</summary>
    public static int ShieldAfterReaction(int hits) =>
        Math.Max(0, hits - AbyssNumbers.MageShieldPerReaction);
}
