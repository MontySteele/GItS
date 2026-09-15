using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Potions;
using MegaCrit.Sts2.Core.Events;
using MegaCrit.Sts2.Core.Localization;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.CardPools;
using MegaCrit.Sts2.Core.Rewards;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Teyvat.Events.Mirrors;

/// <summary>
/// THE FUTURE OF POTIONS, mirrored clause for clause from
/// `MegaCrit.Sts2.Core.Models.Events/TheFutureOfPotions.cs` and cross-checked
/// against the frozen harvest (the five-rarity insert table).
///
/// NOTHING MECHANICAL IS AUTHORED HERE: the same leftmost-three belt slice,
/// the same one random card TYPE rolled per potion with Power dropped for a
/// Common or a Token, the same potion-rarity to card-rarity map (Event reads
/// Rare, Token reads Common), the same three upgraded cards offered from the
/// owner's OWN pool with rarity and pool modifications switched off, the same
/// two-potion gate, and the same lock on using or dropping potions for as long
/// as the desk is open.
///
/// ITS OPTIONS COME OFF THE BELT, AND THAT IS WHY THIS EVENT WAS PARKED. Every
/// option -- up to three of them -- is built under the ONE key
/// `pages.INITIAL.options.POTION`, with `ThatHasDynamicTitle()` and a
/// `LocString` per potion carrying `Rarity` on the title and `Potion`,
/// `Rarity` and `Type` on the description. There is nothing for a face's five
/// lines to pair with one to one, because there is one key; the mirror
/// ledger's `table_option` carries all five into it instead -- the labels as a
/// SmartFormat `choose` over the potion's rarity, the description as the first
/// line with the three vars slotted in. The shipped German row for this very
/// key already uses `choose`, so the device is the base game's.
///
/// THE DONE PAGE TAKES THE RAW LINE. A page is looked up through
/// `L10NLookup`, which adds only the event's own `DynamicVars` -- and this
/// event declares none -- so a page row carrying `{Potion}` would be a format
/// call on a var nobody supplies. The generator writes page text from the
/// unslotted face line for exactly that reason.
/// </summary>
public abstract class TheFutureOfPotionsMirror : TeyvatEventMirror
{
    private const string _potionKey = "Potion";

    private const string _rarityKey = "Rarity";

    private const string _typeKey = "Type";

    private Dictionary<PotionModel, CardType> _cardTypes;

    /// <summary>This DRESSING's option title and description, which is the
    /// whole of what a face changes here -- `Id.Entry` re-keys both.</summary>
    private LocString ChoiceTitle =>
        new LocString("events", InitialOptionKey("POTION") + ".title");

    private LocString ChoiceDescription =>
        new LocString("events", InitialOptionKey("POTION") + ".description");

    /// <summary>
    /// One card type per potion on the belt, rolled ONCE and remembered: the
    /// option's description promises a type, and the reward has to keep that
    /// promise. Power is off the table for a Common or a Token, which is the
    /// base event's own rule.
    /// </summary>
    private Dictionary<PotionModel, CardType> PotionToCardType
    {
        get
        {
            AssertMutable();
            if (_cardTypes == null)
            {
                _cardTypes = new Dictionary<PotionModel, CardType>();
                foreach (PotionModel potion in Owner.Potions)
                {
                    List<CardType> types = new List<CardType>
                    {
                        CardType.Attack,
                        CardType.Skill,
                        CardType.Power,
                    };
                    if (potion.Rarity == PotionRarity.Common || potion.Rarity == PotionRarity.Token)
                    {
                        types.Remove(CardType.Power);
                    }

                    _cardTypes.Add(potion, Rng.NextItem(types));
                }
            }

            return _cardTypes;
        }
    }

    /// <summary>
    /// The library entry, with placeholders where a run would have a potion.
    /// The base event throws if the shape it expects -- exactly one title row
    /// and one description row -- is not what it gets, and the throw is kept:
    /// it is the only thing that would say out loud that a dressing's rows had
    /// drifted from the base's.
    /// </summary>
    public override IEnumerable<LocString> GameInfoOptions
    {
        get
        {
            List<LocString> options = base.GameInfoOptions.ToList();
            if (options.Count != 2)
            {
                throw new InvalidOperationException(
                    "TheFutureOfPotions must've changed loc format, please update its\n"
                  + "GameInfoOptions method.");
            }

            LocString title = options.First((LocString o) => o.LocEntryKey.EndsWith(".title"));
            title.Add(_rarityKey, "[rarity]");
            LocString description = options.First(
                (LocString o) => o.LocEntryKey.EndsWith(".description"));
            description.Add(_potionKey, "[potion]");
            description.Add(_rarityKey, "[same-rarity]");
            description.Add(_typeKey, "[card of random type]");
            return options;
        }
    }

    /// <summary>The base event's gate: two potions on every belt, so the desk
    /// is never a room that takes the only one you have.</summary>
    public override bool IsAllowed(IRunState runState) =>
        runState.Players.All((Player p) => p.Potions.Count() >= 2);

    /// <summary>Potions are frozen while the desk is open -- otherwise the
    /// option could name a flask that is no longer there.</summary>
    protected override Task BeforeEventStarted(bool isPreFinished)
    {
        Owner.CanUseOrRemovePotions = false;
        return Task.CompletedTask;
    }

    protected override void OnEventFinished()
    {
        Owner.CanUseOrRemovePotions = true;
    }

    /// <summary>
    /// Up to three options, all under the ONE key, each dressed with its own
    /// potion's words. `ThatHasDynamicTitle` is what lets three options share
    /// a key without the page reading three identical lines.
    /// </summary>
    protected override IReadOnlyList<EventOption> GenerateInitialOptions()
    {
        List<EventOption> options = new List<EventOption>();
        List<PotionModel> belt = Owner.Potions.ToList();
        int count = Mathf.Min(3, belt.Count);
        for (int i = 0; i < count; i++)
        {
            PotionModel potion = belt[i];
            LocString title = ChoiceTitle;
            title.Add(_rarityKey, potion.Rarity.ToLocString().GetFormattedText());
            LocString description = ChoiceDescription;
            description.Add(_potionKey, potion.Title.GetFormattedText());
            description.Add(_rarityKey, GetCardRarity(potion).ToLocString().GetFormattedText());
            description.Add(_typeKey, PotionToCardType[potion].ToLocString().GetFormattedText());
            options.Add(new EventOption(this, async delegate
            {
                await Trade(potion);
            }, title, description, InitialOptionKey("POTION"), potion.HoverTips)
                .ThatHasDynamicTitle());
        }

        return options;
    }

    /// <summary>
    /// `Trade`: the flask goes, and three cards of the promised rarity and
    /// type come back upgraded. The upgrade runs on `AfterGenerated` -- before
    /// the reward is shown -- which is why the player never sees the
    /// un-upgraded three.
    /// </summary>
    private async Task Trade(PotionModel potion)
    {
        CardRarity targetRarity = GetCardRarity(potion);
        await PotionCmd.Discard(potion);
        CardCreationOptions options = CardCreationOptions
            .ForNonCombatWithUniformOdds(
                new List<CardPoolModel> { Owner.Character.CardPool },
                (CardModel c) => c.Rarity == targetRarity && c.Type == PotionToCardType[potion])
            .WithFlags(CardCreationFlags.NoRarityModification | CardCreationFlags.NoCardPoolModifications);
        CardReward reward = new CardReward(options, 3, Owner);
        reward.AfterGenerated += UpgradeCardsInReward;
        await RewardsCmd.OfferCustom(Owner, new List<Reward>(1) { reward });
        await Done();

        void UpgradeCardsInReward()
        {
            foreach (CardModel card in reward.Cards)
            {
                CardCmd.Upgrade(card);
            }
        }
    }

    private Task Done()
    {
        SetEventFinished(L10NLookup(PageKey("DONE.description")));
        return Task.CompletedTask;
    }

    /// <summary>The base event's map, with its throw kept: Event reads Rare
    /// and Token reads Common, and a rarity outside the five is a defect
    /// rather than a silent Common.</summary>
    private CardRarity GetCardRarity(PotionModel potion)
    {
        switch (potion.Rarity)
        {
            case PotionRarity.Rare:
            case PotionRarity.Event:
                return CardRarity.Rare;
            case PotionRarity.Uncommon:
                return CardRarity.Uncommon;
            case PotionRarity.Common:
            case PotionRarity.Token:
                return CardRarity.Common;
            default:
                throw new InvalidOperationException(
                    $"Potion {potion.Id.Entry} has invalid rarity {potion.Rarity}");
        }
    }
}
