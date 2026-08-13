using System;
using System.Linq;
using System.Threading.Tasks;
using KleeMod.Cards;
using KleeMod.Cards.Furina.Generated;
using KleeMod.Cards.Generated;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// Furina's Guest Star generation pool: every shared Companion plus the
/// purpose-built Neuvillette cameos, filtered to exactly the generator's
/// rarity. Generated cards exist only in combat piles and never enter the
/// permanent deck.
/// </summary>
public static class GuestStarGenerator
{
    public static async Task Generate(
        PlayerChoiceContext choiceContext, CardModel source, string rarity,
        int amount, int? costOverride)
    {
        var targetRarity = rarity switch
        {
            "common" => CardRarity.Common,
            "uncommon" => CardRarity.Uncommon,
            _ => throw new ArgumentOutOfRangeException(
                nameof(rarity), rarity, "Guest Stars must be Common or Uncommon."),
        };
        var pool = CompanionRoster.All
            .Concat(GuestStarRoster.All)
            .Where(card => card.Rarity == targetRarity)
            // personal_pool rows are the owning character's kit, distinct
            // from a generated cameo (LAW.md 98-110). Honored HERE so no pool
            // source can forget it: PruneWitchHunt is a shared uncommon
            // companion whose PersonalPool is "klee", and this generator was
            // the SOLE consumer that skipped the predicate every other door
            // applies (CompanionPool.IsOfferable, CompanionSlot,
            // CompanionBanner, the shop). EB-99; tier0
            // loader.guest_star_generation_pool carries the twin.
            .Where(card => card is not ICompanionCard comp
                           || comp.PersonalPool is null)
            .OrderBy(card => card.Id.ToString())
            .ToList();
        if (pool.Count == 0)
        {
            throw new InvalidOperationException(
                $"Guest Star pool is empty at rarity {rarity}.");
        }

        for (var i = 0; i < amount; i++)
        {
            var canonical = source.Owner.RunState.Rng.CombatTargets.NextItem(pool);
            if (canonical == null) break;
            var generated = source.CombatState!.CreateCard(canonical, source.Owner);
            if (costOverride is int cost)
            {
                generated.EnergyCost.SetThisTurn(cost);
            }
            await CardPileCmd.AddGeneratedCardToCombat(
                generated, PileType.Hand, source.Owner);
        }
    }
}
