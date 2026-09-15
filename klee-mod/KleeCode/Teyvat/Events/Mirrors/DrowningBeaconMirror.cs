using System.Collections.Generic;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Potions;
using MegaCrit.Sts2.Core.Models.Relics;
using MegaCrit.Sts2.Core.Rewards;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// DROWNING BEACON, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/DrowningBeacon.cs` and cross-checked
/// against the harvest (2 options: Bottle, Climb).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `HpLossVar(13)`, the same
/// two `StringVar`s naming the Glowwater Potion and the Fresnel Lens, no act
/// gate, the same potion and relic hover tips, `.ThatDecreasesMaxHp` on the
/// second option, and the same max-HP-then-relic order.
///
/// BOTH REWARDS ARE NAMED AND NEITHER IS ROLLED. The bottle is specifically
/// `GlowwaterPotion` and the climb is specifically `FresnelLens`, so this
/// event costs the run no rng at all -- and both are the base game's models
/// with the base game's global loc rows, which a dressing renames no more
/// than it renames the Chosen Cheese. The face's "Fresnel Lens (relic)" and
/// "Glowwater Potion" are the dressing telling the player the truth about
/// what it grants.
/// </summary>
public abstract class DrowningBeaconMirror : TeyvatEventMirror
{
    /// <summary>`DrowningBeacon.cs:20-25`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new HpLossVar(13m),
            new StringVar("Potion", ModelDb.Potion<GlowwaterPotion>().Title.GetFormattedText()),
            new StringVar("Relic", ModelDb.Relic<FresnelLens>().Title.GetFormattedText()),
        };

    /// <summary>Two options, in the base event's order, under its names, with
    /// the potion's tip on the first and the relic's tip plus the max-HP
    /// annotation on the second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, BottleOption, InitialOptionKey("BOTTLE"),
                HoverTipFactory.FromPotion(ModelDb.Potion<GlowwaterPotion>())),
            new EventOption(this, ClimbOption, InitialOptionKey("CLIMB"),
                HoverTipFactory.FromRelic<FresnelLens>())
                .ThatDecreasesMaxHp(DynamicVars.HpLoss.BaseValue),
        };

    /// <summary>`BottleOption`: the named potion, offered as a custom
    /// reward.</summary>
    private async Task BottleOption()
    {
        await RewardsCmd.OfferCustom(Owner, new List<Reward>(1)
        {
            new PotionReward(ModelDb.Potion<GlowwaterPotion>().ToMutable(), Owner),
        });
        SetEventFinished(L10NLookup(PageKey("BOTTLE.description")));
    }

    /// <summary>`ClimbOption`: 13 max HP, then the named relic.</summary>
    private async Task ClimbOption()
    {
        await CreatureCmd.LoseMaxHp(
            new ThrowingPlayerChoiceContext(), Owner.Creature,
            DynamicVars.HpLoss.BaseValue, isFromCard: false);
        await RelicCmd.Obtain(ModelDb.Relic<FresnelLens>().ToMutable(), Owner);
        SetEventFinished(L10NLookup(PageKey("CLIMB.description")));
    }
}
