using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using MegaCrit.Sts2.Core.CardSelection;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Gold;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Nodes.CommonUi;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// WHISPERING HOLLOW, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/WhisperingHollow.cs` and cross-checked
/// against the harvest (2 options: Gold, Hug).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same `GoldVar(35)` moved by
/// `Rng.NextInt(-9, 10)` -- the 26-44 band the harvest prints as "50 Mora" in
/// round numbers -- the same `HpLossVar(9)`, the same 44-gold gate, the same
/// static Transform tip AND damage annotation together on the second option,
/// the same TWO potion rewards on the first, and the same
/// transform-then-damage ORDER on the second.
///
/// THE ORDER ON THE SECOND OPTION IS LOAD-BEARING and is the base event's:
/// the card is transformed BEFORE the 9 unblockable unpowered damage lands,
/// so a player the damage kills has already had the transform. Swapping the
/// two would be a different event at low HP.
///
/// THE GATE ASKS FOR 44 AND THE OPTION SPENDS THE ROLLED VALUE. 44 is the
/// top of the band, so the room is only offered where the dearer reading of
/// the price can be paid; what is actually taken is `DynamicVars.Gold`, which
/// `CalculateVars` has already rolled.
/// </summary>
public abstract class WhisperingHollowMirror : TeyvatEventMirror
{
    /// <summary>`WhisperingHollow.cs:24-28`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new GoldVar(35),
            new HpLossVar(9m),
        };

    /// <summary>The base event's gate: every player holding 44.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) => p.Gold >= 44);

    /// <summary>The base event's roll: -9 to +9 on the 35 (`NextInt` is
    /// exclusive at the top).</summary>
    public override void CalculateVars()
    {
        DynamicVars.Gold.BaseValue += (decimal)Rng.NextInt(-9, 10);
    }

    /// <summary>Two options, in the base event's order, under its names, with
    /// the static Transform tip and the damage annotation both on the
    /// second.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions() =>
        new List<EventOption>
        {
            new EventOption(this, Gold, InitialOptionKey("GOLD")),
            new EventOption(this, Hug, InitialOptionKey("HUG"),
                HoverTipFactory.Static(StaticHoverTip.Transform))
                .ThatDoesDamage(DynamicVars.HpLoss.IntValue),
        };

    /// <summary>`Gold`: the rolled price spent, then two potion
    /// rewards.</summary>
    private async Task Gold()
    {
        await PlayerCmd.LoseGold(DynamicVars.Gold.IntValue, Owner, GoldLossType.Spent);
        await RewardsCmd.OfferCustom(Owner, new List<Reward>(2)
        {
            new PotionReward(Owner),
            new PotionReward(Owner),
        });
        SetEventFinished(L10NLookup(PageKey("GOLD.description")));
    }

    /// <summary>`Hug`: one chosen card transformed, and only THEN the
    /// damage.</summary>
    private async Task Hug()
    {
        List<CardModel> cards = (await CardSelectCmd.FromDeckForTransformation(
            player: Owner, prefs: new CardSelectorPrefs(CardSelectorPrefs.TransformSelectionPrompt, 1)))
            .ToList();
        foreach (CardModel card in cards)
        {
            await CardCmd.TransformToRandom(card, Rng, CardPreviewStyle.EventLayout);
        }

        await CreatureCmd.Damage(
            new ThrowingPlayerChoiceContext(), Owner.Creature, DynamicVars.HpLoss.BaseValue,
            ValueProp.Unblockable | ValueProp.Unpowered, null, null, null);
        SetEventFinished(L10NLookup(PageKey("HUG.description")));
    }
}
