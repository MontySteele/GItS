using System.Collections.Generic;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Logging;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// VARKA'S WINDS (sec.10.1): "for the rest of the fight, each paid on every
/// Swirl you make". One per element, gained the first time he Absorbs that
/// element (<see cref="VarkaAbsorb"/>), held until the fight ends. A power on
/// him, so the badge row IS the list of Winds he holds and the seat page reads
/// it off the wire like any other status.
///
/// A <c>Single</c> power: a Wind is held or not, and the game draws no number
/// on its icon.
/// </summary>
public abstract class WindPower : PowerModel, ILocalizationProvider
{
    /// <summary>The element this Wind was absorbed from.</summary>
    public abstract Element Element { get; }

    /// <summary>The badge's sentence, the Wind's one payout.</summary>
    protected abstract string Rule { get; }

    public List<(string, string)>? Localization => new()
    {
        ("title", $"{Element} Wind"),
        ("description", Rule),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Single;

    /// <summary>What this Wind pays when its holder Swirls
    /// <paramref name="swirled"/>. Called by <see cref="VarkaWinds.OnSwirl"/>
    /// in the fixed order of <see cref="VarkaWinds.Order"/>.</summary>
    internal abstract Task PayOnSwirl(
        PlayerChoiceContext choiceContext, Creature swirled);
}

/// <summary>Pyro Wind: deal 3 damage to the enemy you Swirled.</summary>
public sealed class PyroWindPower : WindPower
{
    public override Element Element => Element.Pyro;

    protected override string Rule =>
        "Whenever you [gold]Swirl[/gold], deal [blue]"
      + VarkaLaw.PyroWindDamage + "[/blue] damage to the enemy you hit.";

    /// <summary>A power's damage: no Strength, the target's Vulnerable, no
    /// element (<see cref="ElementalHit.DealUnelemented"/>, the Stage acts'
    /// door).</summary>
    internal override async Task PayOnSwirl(
        PlayerChoiceContext choiceContext, Creature swirled)
    {
        if (!swirled.IsAlive) return;
        await ElementalHit.DealUnelemented(
            choiceContext, swirled, VarkaLaw.PyroWindDamage, Owner,
            powered: false);
    }
}

/// <summary>Hydro Wind: gain 3 Block.</summary>
public sealed class HydroWindPower : WindPower
{
    public override Element Element => Element.Hydro;

    protected override string Rule =>
        "Whenever you [gold]Swirl[/gold], gain [blue]"
      + VarkaLaw.HydroWindBlock + "[/blue] [gold]Block[/gold].";

    internal override async Task PayOnSwirl(
        PlayerChoiceContext choiceContext, Creature swirled)
    {
        await CreatureCmd.GainBlock(
            Owner, VarkaLaw.HydroWindBlock, ValueProp.Unpowered, null,
            fast: true);
    }
}

/// <summary>Cryo Wind: the enemy you Swirled gains 1 Weak.</summary>
public sealed class CryoWindPower : WindPower
{
    public override Element Element => Element.Cryo;

    protected override string Rule =>
        "Whenever you [gold]Swirl[/gold], apply [blue]"
      + VarkaLaw.CryoWindWeak + "[/blue] [gold]Weak[/gold] to the enemy you "
      + "hit.";

    internal override async Task PayOnSwirl(
        PlayerChoiceContext choiceContext, Creature swirled)
    {
        if (!swirled.IsAlive) return;
        await PowerCmd.Apply<WeakPower>(
            choiceContext, swirled, VarkaLaw.CryoWindWeak,
            applier: Owner, cardSource: null);
    }
}

/// <summary>Electro Wind: your first Swirl each turn gives 1 Energy
/// (sec.10.1: "Untested; the sim's draw versions were last everywhere").
/// </summary>
public sealed class ElectroWindPower : WindPower
{
    public override Element Element => Element.Electro;

    protected override string Rule =>
        "The first time you [gold]Swirl[/gold] each turn, gain [blue]"
      + VarkaLaw.ElectroWindEnergy + "[/blue] [gold]Energy[/gold].";

    /// <summary>Has this turn's Energy been paid? Cleared when his turn
    /// ends, so the next turn's first Swirl pays again.</summary>
    public bool PaidThisTurn { get; private set; }

    internal override async Task PayOnSwirl(
        PlayerChoiceContext choiceContext, Creature swirled)
    {
        if (PaidThisTurn || Owner.Player == null) return;
        PaidThisTurn = true;
        await PlayerCmd.GainEnergy(VarkaLaw.ElectroWindEnergy, Owner.Player);
    }

    public override Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side == CombatSide.Player) PaidThisTurn = false;
        return Task.CompletedTask;
    }
}

/// <summary>
/// THE WINDS' ONE DOOR: who holds which, gaining one, and paying them on a
/// Swirl. <see cref="OnSwirl"/> is called from <c>ReactionEffects.Resolve</c>,
/// the single site every reaction in the mod passes, so no Swirl can pay twice
/// or not at all.
/// </summary>
public static class VarkaWinds
{
    /// <summary>The four elements a Wind can come from, in the order their
    /// payouts resolve on one Swirl: the Weak lands before the damage, which
    /// changes nothing today and keeps the order stated rather than implied.
    /// </summary>
    public static readonly IReadOnlyList<Element> Order = new[]
    {
        Element.Cryo, Element.Pyro, Element.Hydro, Element.Electro,
    };

    /// <summary>The Winds this creature holds, in <see cref="Order"/>. PURE.
    /// </summary>
    public static IReadOnlyList<Element> Held(Creature? creature)
    {
        if (creature == null) return System.Array.Empty<Element>();
        var held = creature.Powers.OfType<WindPower>()
            .Select(w => w.Element).ToHashSet();
        return Order.Where(held.Contains).ToList();
    }

    /// <summary>How many Winds this creature holds. PURE; the count Four
    /// Winds' Ascension, Eye of the Storm, Wind Wall and Tailwind Stride
    /// read.</summary>
    public static int HeldCount(Creature? creature) =>
        creature?.Powers.OfType<WindPower>().Count() ?? 0;

    /// <summary>Does this creature hold the Wind of
    /// <paramref name="element"/>? PURE.</summary>
    public static bool Holds(Creature? creature, Element element) =>
        creature?.Powers.OfType<WindPower>().Any(w => w.Element == element)
        ?? false;

    /// <summary>Is <paramref name="element"/> one a Wind can come from? The
    /// four aura elements; Anemo and Geo leave no aura to absorb. PURE.
    /// </summary>
    public static bool IsWindElement(Element element) => element.LeavesAura();

    /// <summary>Give <paramref name="creature"/> the Wind of
    /// <paramref name="element"/>. A Wind already held is not stacked.
    /// </summary>
    public static async Task Gain(
        PlayerChoiceContext choiceContext, Creature creature, Element element,
        CardModel? cardSource)
    {
        if (Holds(creature, element)) return;
        switch (element)
        {
            case Element.Pyro:
                await PowerCmd.Apply<PyroWindPower>(
                    choiceContext, creature, 1, applier: creature,
                    cardSource: cardSource);
                break;
            case Element.Hydro:
                await PowerCmd.Apply<HydroWindPower>(
                    choiceContext, creature, 1, applier: creature,
                    cardSource: cardSource);
                break;
            case Element.Electro:
                await PowerCmd.Apply<ElectroWindPower>(
                    choiceContext, creature, 1, applier: creature,
                    cardSource: cardSource);
                break;
            case Element.Cryo:
                await PowerCmd.Apply<CryoWindPower>(
                    choiceContext, creature, 1, applier: creature,
                    cardSource: cardSource);
                break;
        }
    }

    // ---- the Swirl count --------------------------------------------------

    private sealed class Count
    {
        public int Value;
    }

    /// <summary>Per creature, never reset: only DIFFS are read (Tempest
    /// Charge's "If it Swirls" snapshots it at the top of its play), the
    /// <c>ReactionEffects.TotalResolved</c> discipline. Weak keys, so a
    /// finished fight's creatures are collected.</summary>
    private static readonly ConditionalWeakTable<Creature, Count> Swirls = new();

    /// <summary>How many Swirls <paramref name="creature"/> has made. PURE.
    /// </summary>
    public static int SwirlsMadeBy(Creature? creature) =>
        creature != null && Swirls.TryGetValue(creature, out var n)
            ? n.Value : 0;

    /// <summary>
    /// A SWIRL <paramref name="dealer"/> MADE, on <paramref name="swirled"/>.
    /// Counts it, then pays every Wind the dealer holds, in
    /// <see cref="Order"/>. Called once per Swirl from
    /// <c>ReactionEffects.Resolve</c>, after the Swirl's own spread and flat
    /// damage. A dealer that is not a player (a Swirl from nobody) pays
    /// nothing; with the arm off nothing is counted or paid.
    /// </summary>
    internal static async Task OnSwirl(
        PlayerChoiceContext choiceContext, Creature swirled, Creature? dealer)
    {
        if (!VarkaPrototype.Enabled || dealer?.Player == null) return;
        Swirls.GetOrCreateValue(dealer).Value++;
        var winds = dealer.Powers.OfType<WindPower>().ToList();
        foreach (var element in Order)
        {
            foreach (var wind in winds.Where(w => w.Element == element))
            {
                await wind.PayOnSwirl(choiceContext, swirled);
            }
        }
        if (winds.Count > 0)
        {
            Log.Info($"[{KleeMod.ModId}] VARKA Swirl on {swirled.Name} paid "
                   + $"{winds.Count} Wind(s).");
        }
    }
}
