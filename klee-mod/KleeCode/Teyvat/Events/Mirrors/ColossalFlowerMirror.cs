using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE COLOSSAL FLOWER, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/ColossalFlower.cs` and cross-checked
/// against the frozen harvest and `tier05/content/events.yaml`
/// (`colossal_flower` / `_2` / `_3`).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same three prizes (35 / 75 / 135
/// gold), the same three reach prices (5 / 6 / 7 HP), the same unblockable
/// unpowered damage dealt through a `ThrowingPlayerChoiceContext`, the same
/// 19-HP gate on every player, the same Pollinous Core at the bottom -- and
/// the same order at the bottom, where the damage is dealt BEFORE the relic is
/// obtained, so a reach that kills does not hand out a relic first.
///
/// THE DIG KEYS ARE WRITTEN OUT, NOT INTERPOLATED, and that is Slippery
/// Bridge's rule applied to a shorter ladder. The base event builds them with
/// `$"...EXTRACT_CURRENT_PRIZE_{NumberOfDigs + 1}"`, which leaves the index a
/// brace expression rather than a key and would leave this mirror's IL
/// carrying the fragment `REACH_DEEPER_` -- a literal that looks like a key,
/// is not one, and would read to
/// `A_mirrors_key_literals_are_exactly_its_shape` as a key the shape does not
/// have. Spelling the reachable ordinals costs nothing, because there are only
/// ever two of them:
///
///   * `GenerateInitialOptions` runs once, at `NumberOfDigs == 0`, so the
///     INITIAL page's options are always `_1`;
///   * `ReachDeeper` INCREMENTS before it branches, so its `&lt; 2` arm is only
///     ever entered at one -- page `REACH_DEEPER_1`, options `_2`;
///   * the `else` arm is `REACH_DEEPER_2`, whose two options are named rather
///     than numbered.
///
/// Six option keys and five pages, which is exactly what the faces write.
///
/// WHY IT WAS PARKED. The two per-level repeats would have borrowed a line
/// cleanly, but the bottom page's Pollinous Core (the relic, for 7
/// unblockable) and its Extract Instead sibling are different outcomes with no
/// line between them. Both have keyed lines now.
/// </summary>
public abstract class ColossalFlowerMirror : TeyvatEventMirror
{
    /// <summary>`ColossalFlower.cs`, value for value.</summary>
    private static readonly string[] PrizeKeys = { "Prize1", "Prize2", "Prize3" };

    private static readonly int[] PrizeCosts = { 35, 75, 135 };

    private static readonly int[] PrizeDamage = { 5, 6, 7 };

    private int _numberOfDigs;

    private int NumberOfDigs
    {
        get => _numberOfDigs;
        set
        {
            AssertMutable();
            _numberOfDigs = value;
        }
    }

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new GoldVar(PrizeKeys[0], PrizeCosts[0]),
            new GoldVar(PrizeKeys[1], PrizeCosts[1]),
            new GoldVar(PrizeKeys[2], PrizeCosts[2]),
        };

    /// <summary>The base event's gate: nobody is offered a 5 + 6 + 7 ladder
    /// they could not survive.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) => p.Creature.CurrentHp >= 19);

    /// <summary>Two options, at the ONE ordinal this method can be called at
    /// -- see the class comment.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, ExtractCurrentPrize,
                InitialOptionKey("EXTRACT_CURRENT_PRIZE_1")),
            new EventOption(this, ReachDeeper, InitialOptionKey("REACH_DEEPER_1"))
                .ThatDoesDamage(PrizeDamage[NumberOfDigs]),
        };

    private async Task ReachDeeper()
    {
        await DealReachDeeperDamage();
        NumberOfDigs++;
        if (NumberOfDigs < 2)
        {
            SetEventState(L10NLookup(PageKey("REACH_DEEPER_1.description")),
                new List<EventOption>
                {
                    new EventOption(this, ExtractCurrentPrize,
                        PageKey("REACH_DEEPER_1.options.EXTRACT_CURRENT_PRIZE_2")),
                    new EventOption(this, ReachDeeper,
                        PageKey("REACH_DEEPER_1.options.REACH_DEEPER_2"))
                        .ThatDoesDamage(PrizeDamage[NumberOfDigs]),
                });
        }
        else
        {
            SetEventState(L10NLookup(PageKey("REACH_DEEPER_2.description")),
                new List<EventOption>
                {
                    new EventOption(this, ExtractInstead,
                        PageKey("REACH_DEEPER_2.options.EXTRACT_INSTEAD")),
                    new EventOption(this, ObtainPollinousCore,
                        PageKey("REACH_DEEPER_2.options.POLLINOUS_CORE"),
                        HoverTipFactory.FromRelic<PollinousCore>())
                        .ThatDoesDamage(PrizeDamage[NumberOfDigs]),
                });
        }
    }

    private async Task ExtractCurrentPrize()
    {
        await PlayerCmd.GainGold(PrizeCosts[NumberOfDigs], Owner);
        SetEventFinished(L10NLookup(PageKey("EXTRACT_CURRENT_PRIZE.description")));
    }

    /// <summary>135 gold rather than the core and 7 unblockable.</summary>
    private async Task ExtractInstead()
    {
        await PlayerCmd.GainGold(PrizeCosts[NumberOfDigs], Owner);
        SetEventFinished(L10NLookup(PageKey("EXTRACT_INSTEAD.description")));
    }

    /// <summary>The damage first, then the relic -- the base event's
    /// order.</summary>
    private async Task ObtainPollinousCore()
    {
        await DealReachDeeperDamage();
        await RelicCmd.Obtain<PollinousCore>(Owner);
        SetEventFinished(L10NLookup(PageKey("POLLINOUS_CORE.description")));
    }

    private async Task DealReachDeeperDamage() =>
        await CreatureCmd.Damage(new ThrowingPlayerChoiceContext(), Owner.Creature,
            PrizeDamage[NumberOfDigs], ValueProp.Unblockable | ValueProp.Unpowered,
            null, null);
}
