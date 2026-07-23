using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

public static class SalonConstants
{
    public const int MemberDamage = 4;
    public const int MemberSlots = 3;
    public const int ReplacementNumericMultiplier = 2;
    public const int ReplacementDamageMultiplier = 3;
    public const int TickEncoreCost = 1;
    public const decimal DryDamageMultiplier = 0.75m;
}

/// <summary>
/// Furina's fixed three-slot Salon. Each member attacks at the start of the
/// player's turn. Deploying beyond the cap replaces members: each replacement
/// performs a triple-damage final bow, while the rest of that card's numbers
/// are scaled by the generated card body.
/// </summary>
public sealed class SalonMemberPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Salon Member"),
        ("description",
            "At the start of your turn, each [gold]Salon Member[/gold] spends "
          + "1 Encore to deal 4 Hydro damage to a random enemy. Without "
          + "Encore, it deals 3. Maximum 3. Replacing a member performs a "
          + "triple-damage final bow."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int Count(Creature creature) =>
        creature.Powers.OfType<SalonMemberPower>().FirstOrDefault()?.Amount ?? 0;

    public static async Task<int> Deploy(
        PlayerChoiceContext choiceContext, Creature owner, int amount,
        CardModel cardSource)
    {
        var current = Count(owner);
        var added = Math.Min(Math.Max(0, SalonConstants.MemberSlots - current), amount);
        if (added > 0)
        {
            await PowerCmd.Apply<SalonMemberPower>(
                choiceContext, owner, added, applier: owner, cardSource: cardSource);
        }

        var replacements = Math.Max(0, amount - added);
        for (var i = 0; i < replacements; i++)
        {
            var targets = owner.CombatState?.HittableEnemies.ToList();
            if (targets == null || targets.Count == 0) break;
            var target = owner.Player?.RunState.Rng.CombatTargets.NextItem(targets);
            if (target == null) break;
            var damage = SalonConstants.ReplacementDamageMultiplier
                         * (SalonConstants.MemberDamage
                            + SalonDamageUpPower.AmountFor(owner));
            await ElementalHit.Deal(
                choiceContext, target, Elements.Element.Hydro, damage, owner);
            FurinaResources.GainBurst(
                owner, FurinaResourceConstants.BurstPerSalonTick);
        }
        return replacements;
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        for (var i = 0; i < Amount; i++)
        {
            var targets = CombatState?.HittableEnemies.ToList();
            if (targets == null || targets.Count == 0 || Owner.IsDead) break;

            var paid = FurinaResources.Encore(Owner) >= SalonConstants.TickEncoreCost;
            if (paid)
            {
                FurinaResources.SpendEncore(Owner, SalonConstants.TickEncoreCost);
            }

            var damage = SalonConstants.MemberDamage
                         + SalonDamageUpPower.AmountFor(Owner);
            if (!paid)
            {
                damage = (int)(damage * SalonConstants.DryDamageMultiplier);
            }

            var target = CombatState!.RunState.Rng.CombatTargets.NextItem(targets);
            if (target == null) break;
            await ElementalHit.Deal(
                choiceContext, target, Elements.Element.Hydro, damage, Owner);
            FurinaResources.GainBurst(
                Owner, FurinaResourceConstants.BurstPerSalonTick);
        }
    }

    public override bool TryModifyPowerAmountReceived(
        PowerModel canonicalPower, Creature target, decimal amount,
        Creature? applier, out decimal modifiedAmount)
    {
        modifiedAmount = amount;
        if (canonicalPower is not SalonMemberPower || target != Owner)
        {
            return false;
        }
        modifiedAmount = Math.Max(
            0m, Math.Min(amount, SalonConstants.MemberSlots - Amount));
        return modifiedAmount != amount;
    }
}

/// <summary>Flat damage added to every paid/dry Salon tick and final bow.</summary>
public sealed class SalonDamageUpPower : PowerModel, ILocalizationProvider
{
    public const int MaxStacks = 6;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Grand Salon"),
        ("description",
            "[gold]Salon Members[/gold] deal {Amount} more damage. Maximum 6."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int AmountFor(Creature creature) =>
        creature.Powers.OfType<SalonDamageUpPower>().FirstOrDefault()?.Amount ?? 0;

    public override bool TryModifyPowerAmountReceived(
        PowerModel canonicalPower, Creature target, decimal amount,
        Creature? applier, out decimal modifiedAmount)
    {
        modifiedAmount = amount;
        if (canonicalPower is not SalonDamageUpPower || target != Owner)
        {
            return false;
        }
        modifiedAmount = Math.Max(0m, Math.Min(amount, MaxStacks - Amount));
        return modifiedAmount != amount;
    }
}
