using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Furina;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;

namespace KleeMod.Relics;

/// <summary>
/// Furina's starter talent. After the normal turn draw, it adds the one-use
/// Spotlight selector to hand. It also hosts Furina's fourth companion reward
/// option, mirroring Klee's always-present starter-relic hook.
/// </summary>
public sealed class EtherealSpotlightRelic : CustomRelicModel
{
    public EtherealSpotlightRelic() : base(autoAdd: false)
    {
    }

    public override RelicRarity Rarity => RelicRarity.Starter;

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Ethereal Spotlight"),
        ("description",
            "At the start of each turn, add an [gold]Ethereal Spotlight[/gold] "
          + "to your hand. Post-combat card rewards include a Companion option."),
    };

    // Art-pass fallback.
    protected override string IconBaseName => "snake_ring";

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player != Owner || player.Character is not Furina) return;
        var hand = CardPile.Get(PileType.Hand, player);
        if (hand == null || hand.Cards.Any(card => card is EtherealSpotlight))
        {
            return;
        }
        if (hand.Cards.Count >= CardPile.MaxCardsInHand) return;

        var selector = player.Creature.CombatState!
            .CreateCard<EtherealSpotlight>(player);
        await CardPileCmd.AddGeneratedCardToCombat(
            selector, PileType.Hand, player);
    }

    public override bool TryModifyCardRewardOptions(
        Player player, List<CardCreationResult> cardRewardOptions,
        CardCreationOptions creationOptions)
    {
        if (creationOptions.Source != CardCreationSource.Encounter
            || player.Character is not Furina)
        {
            return false;
        }
        var rarity = creationOptions.RarityOdds
                     == CardRarityOddsType.BossEncounter
            ? CardRarity.Rare
            : (CardRarity?)null;
        var offer = CompanionSlot.Roll(player, rarity);
        if (offer == null) return false;
        cardRewardOptions.Add(new CardCreationResult(offer));
        return true;
    }
}
