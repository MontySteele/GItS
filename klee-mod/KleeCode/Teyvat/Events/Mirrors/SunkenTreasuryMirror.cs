using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models.Cards;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// SUNKEN TREASURY, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/SunkenTreasury.cs` and cross-checked
/// against the harvest (2 options: First Chest, Second Chest).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same two gold vars (60 and 333),
/// no act gate, the same Greed card hover tip on the second option, the same
/// two jitters in `CalculateVars`, and the same gold-then-curse order.
///
/// THE TWO JITTERS ARE WRITTEN THE BASE EVENT'S WAY, which is not the way the
/// other events in this surface write theirs: `Rng.NextInt(16) - 8` and
/// `Rng.NextInt(61) - 30`, a single-argument roll shifted, rather than the
/// two-argument `NextInt(-8, 9)` Whispering Hollow uses. They produce the same
/// bands -- 52-68 and 303-363, which is what the face prints -- but they are
/// different calls on the rng, and this arm does not tidy a call sequence.
///
/// THE SECOND CHEST ADDS A CHARACTER LINE, as Aroma of Chaos does: the page
/// takes `Monologue` from `characters/&lt;entry&gt;.goldMonologue`. That is a
/// base-game row per character and not this arm's to write; the mirror adds
/// the var exactly as the base event does, and a dressing that does not
/// reference `{Monologue}` simply never prints it.
/// </summary>
public abstract class SunkenTreasuryMirror : TeyvatEventMirror
{
    /// <summary>`SunkenTreasury.cs:19-23`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DynamicVar("SmallChestGold", 60m),
            new DynamicVar("LargeChestGold", 333m),
        };

    /// <summary>Two options, in the base event's order, under its names, with
    /// Greed's card hover tip on the second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, FirstChest, InitialOptionKey("FIRST_CHEST")),
            new EventOption(this, SecondChest, InitialOptionKey("SECOND_CHEST"),
                HoverTipFactory.FromCardWithCardHoverTips<Greed>()),
        };

    /// <summary>The base event's two rolls, in its own shape.</summary>
    public override void CalculateVars()
    {
        DynamicVars["SmallChestGold"].BaseValue += (decimal)(Rng.NextInt(16) - 8);
        DynamicVars["LargeChestGold"].BaseValue += (decimal)(Rng.NextInt(61) - 30);
    }

    /// <summary>`FirstChest`: the smaller purse, and nothing else.</summary>
    private async Task FirstChest()
    {
        await PlayerCmd.GainGold(DynamicVars["SmallChestGold"].BaseValue, Owner);
        SetEventFinished(L10NLookup(PageKey("FIRST_CHEST.description")));
    }

    /// <summary>`SecondChest`: the larger purse, then Greed, then the page
    /// with the character's own line on it.</summary>
    private async Task SecondChest()
    {
        await PlayerCmd.GainGold(DynamicVars["LargeChestGold"].BaseValue, Owner);
        await CardPileCmd.AddCurseToDeck<Greed>(Owner);
        LocString description = L10NLookup(PageKey("SECOND_CHEST.description"));
        description.Add("Monologue", new LocString("characters", Owner.Character.Id.Entry + ".goldMonologue"));
        SetEventFinished(description);
    }
}
