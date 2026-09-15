using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE COLORFUL PHILOSOPHERS, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/ColorfulPhilosophers.cs` and
/// cross-checked against the harvest (5 options, one per card pool).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same fixed pool ORDER, the same
/// `CardsVar(3)`, the same more-than-one-pool-unlocked gate, the same filter
/// (every unlocked pool that is not the player's OWN), the same trim down to
/// three by removing random entries, and the same three uniform-odds card
/// rewards -- one Common, one Uncommon, one Rare, `Cards` cards each.
///
/// THE OPTION KEYS ARE BUILT BY CONCATENATION, which is why the index's scrape
/// reports NO option keys for this event: the key is
/// `...options.` + `cardPool.EnergyColorName.ToUpperInvariant()`, so the five
/// it can be are `IRONCLAD`, `SILENT`, `DEFECT`, `NECROBINDER` and `REGENT` --
/// each named after the pool, none of them written as a literal anywhere. The
/// mirror's spec declares all five, in the FACE's order rather than in
/// `CardPoolColorOrder`, because the pairing here is BY NAME (each key is its
/// own colour) rather than by build order, and the face writes its five
/// wagers in whatever order the nation's own colour scheme runs. Like Hungry
/// for Mushrooms' relic-keyed pair, no literal exists on either side for the
/// key-literal pin to compare, and the pin's table says so.
///
/// HOW MANY OPTIONS A RUN SEES IS NOT FIXED. Between one and three survive the
/// filter and the trim, and WHICH three is rolled off the event's own `Rng`.
/// All five rows are written regardless: a row costs nothing and a missing one
/// is a null `GetOptionTitle` and a blank page (EB-765).
///
/// THE POOLS ARE THE BASE GAME'S and their cards keep their global rows. A
/// dressing renames the event and its options; it never renames a character's
/// cards.
/// </summary>
public abstract class ColorfulPhilosophersMirror : TeyvatEventMirror
{
    /// <summary>The base event's fixed order, which is the order the surviving
    /// options are BUILT in -- not the order the face writes its lines in.</summary>
    private static IEnumerable<CardPoolModel> CardPoolColorOrder =>
        new List<CardPoolModel>
        {
            ModelDb.CardPool<NecrobinderCardPool>(),
            ModelDb.CardPool<IroncladCardPool>(),
            ModelDb.CardPool<RegentCardPool>(),
            ModelDb.CardPool<SilentCardPool>(),
            ModelDb.CardPool<DefectCardPool>(),
        };

    /// <summary>`ColorfulPhilosophers.cs:27`, value for value.</summary>
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar> { new CardsVar(3) };

    /// <summary>The base event's gate: every player has more than one
    /// character pool unlocked, or there is nothing to offer.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) => p.UnlockState.CharacterCardPools.Count() > 1);

    /// <summary>Every unlocked pool that is not the player's own, in the fixed
    /// order, trimmed at random to at most three.</summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        List<EventOption> options = new List<EventOption>();
        CharacterModel character = Owner.Character;
        List<CardPoolModel> unlocked = Owner.UnlockState.CharacterCardPools.ToList();
        foreach (CardPoolModel cardPool in CardPoolColorOrder)
        {
            if (character.CardPool != cardPool && unlocked.Contains(cardPool))
            {
                options.Add(new EventOption(
                    this, () => OfferRewards(cardPool),
                    InitialOptionKey(cardPool.EnergyColorName.ToUpperInvariant())));
            }
        }

        int keep = Mathf.Min(3, options.Count);
        while (options.Count > keep)
        {
            options.RemoveAt(Rng.NextInt(options.Count));
        }

        return options;
    }

    /// <summary>The three rewards: Common, Uncommon and Rare from the chosen
    /// pool, uniform odds, with the base event's two flags on each so the
    /// offer moves neither the rarity odds nor the pool.</summary>
    private async Task OfferRewards(CardPoolModel pool)
    {
        CardCreationOptions common = RewardOptions(pool, CardRarity.Common);
        CardCreationOptions uncommon = RewardOptions(pool, CardRarity.Uncommon);
        CardCreationOptions rare = RewardOptions(pool, CardRarity.Rare);
        await RewardsCmd.OfferCustom(Owner, new List<Reward>(3)
        {
            new CardReward(common, DynamicVars.Cards.IntValue, Owner),
            new CardReward(uncommon, DynamicVars.Cards.IntValue, Owner),
            new CardReward(rare, DynamicVars.Cards.IntValue, Owner),
        });
        SetEventFinished(L10NLookup(PageKey("DONE.description")));
    }

    /// <summary>The base event's three identical constructions, written once.
    /// Shape only: the arguments, the flags and the call order are its own.</summary>
    private static CardCreationOptions RewardOptions(CardPoolModel pool, CardRarity rarity) =>
        new CardCreationOptions(
            new List<CardPoolModel> { pool }, CardCreationSource.Other,
            CardRarityOddsType.Uniform, (CardModel c) => c.Rarity == rarity)
            .WithFlags(CardCreationFlags.NoRarityModification
                     | CardCreationFlags.NoCardPoolModifications);
}
