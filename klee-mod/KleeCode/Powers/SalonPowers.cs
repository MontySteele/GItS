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

/// <summary>Salon v2 member identities (rework plan §1 — the Defect-orb
/// grammar; mirrors tier0 constants.SALON_MEMBERS).</summary>
public enum SalonMember
{
    Crabaletta,
    Usher,
    Chevalmarin,
}

public static class SalonConstants
{
    public const int MemberSlots = 3;

    // Fanfare is the Focus analogue: +1 to member NUMERIC amounts per this
    // much held Fanfare, read live at resolution (rework plan §1).
    public const int FocusPerFanfare = 10;

    public const int ReplacementNumericMultiplier = 2;
    public const int ReplacementDamageMultiplier = 3;
    public const int TickEncoreCost = 1;
    public const decimal DryDamageMultiplier = 0.75m;

    // Member tick / bow numbers — PROPOSED pending red-pen; the sim's
    // C.SALON_MEMBERS table is the source of truth.
    public const int CrabalettaTick = 6;
    public const int CrabalettaBow = 14;
    public const int UsherTick = 3;
    public const int UsherBow = 9;
    public const int ChevalmarinTick = 2;
    public const int ChevalmarinBowEncore = 3;
}

/// <summary>
/// Furina's fixed three-slot Salon, v2 (rework 2026-07-23): the company is
/// a TYPED FIFO queue. Each member performs its unique slot passive at the
/// start of the player's turn (Crabaletta hits, Usher blocks, Chevalmarin
/// applies); deploying into a full stage bows the OLDEST member out — its
/// unique payoff — and the new member takes the vacated slot. Fanfare acts
/// as Focus: +1 to member numerics per 10 held.
/// </summary>
public sealed class SalonMemberPower : PowerModel, ILocalizationProvider
{
    // The typed company per owner. The counter power (Amount) mirrors the
    // queue length so every count read stays valid; this dictionary is the
    // member-identity half the counter cannot carry. Entries are reset on
    // the first deploy of a combat (queue outliving the power is harmless:
    // a fresh combat's first Deploy clears a stale list).
    private static readonly Dictionary<Creature, List<SalonMember>> Company =
        new();

    public List<(string, string)>? Localization => new()
    {
        ("title", "Salon Member"),
        ("description",
            "At the start of your turn, each [gold]Salon Member[/gold] "
          + "spends 1 Encore for its act: Crabaletta deals 6 Hydro damage, "
          + "the Usher gains 3 Block, Chevalmarin deals 2 Hydro damage. "
          + "Dry members act at three-quarters. Member numbers gain +1 per "
          + "10 [gold]Fanfare[/gold]. Maximum 3; a full stage bows its "
          + "OLDEST member out: Crabaletta deals 14, the Usher gains 9 "
          + "Block, Chevalmarin applies Hydro to ALL enemies and grants "
          + "3 Encore."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int Count(Creature creature) =>
        creature.Powers.OfType<SalonMemberPower>().FirstOrDefault()?.Amount ?? 0;

    private static List<SalonMember> CompanyFor(Creature owner)
    {
        if (!Company.TryGetValue(owner, out var list))
        {
            list = new List<SalonMember>();
            Company[owner] = list;
        }
        // Stale list from a previous combat: the counter power died with
        // that combat, so a nonempty list with a zero counter is garbage.
        if (Count(owner) == 0 && list.Count > 0) list.Clear();
        return list;
    }

    private static int Scaled(Creature owner, int baseAmount) =>
        baseAmount
        + FurinaResources.Fanfare(owner) / SalonConstants.FocusPerFanfare
        + SalonDamageUpPower.AmountFor(owner);

    private static async Task Bow(
        PlayerChoiceContext choiceContext, Creature owner, SalonMember member)
    {
        switch (member)
        {
            case SalonMember.Crabaletta:
            {
                var targets = owner.CombatState?.HittableEnemies.ToList();
                if (targets == null || targets.Count == 0) break;
                var target = owner.Player?.RunState.Rng.CombatTargets
                    .NextItem(targets);
                if (target == null) break;
                await ElementalHit.Deal(
                    choiceContext, target, Elements.Element.Hydro,
                    Scaled(owner, SalonConstants.CrabalettaBow), owner);
                break;
            }
            case SalonMember.Usher:
                await CreatureCmd.GainBlock(
                    owner, Scaled(owner, SalonConstants.UsherBow),
                    ValueProp.Unpowered, null, fast: true);
                break;
            case SalonMember.Chevalmarin:
            {
                var targets = owner.CombatState?.HittableEnemies.ToList();
                if (targets != null)
                {
                    foreach (var enemy in targets)
                    {
                        await ElementalHit.ApplyOnly(
                            choiceContext, enemy, Elements.Element.Hydro,
                            owner);
                    }
                }
                FurinaResources.GainEncore(
                    owner, SalonConstants.ChevalmarinBowEncore);
                break;
            }
        }
        FurinaResources.GainBurst(
            owner, FurinaResourceConstants.BurstPerSalonTick);
    }

    /// <summary>Salon v2 deploy: into a full stage, the OLDEST member bows
    /// out and the new member enters. Returns the replacement count (the
    /// generated card bodies scale their later numerics off it).</summary>
    public static async Task<int> Deploy(
        PlayerChoiceContext choiceContext, Creature owner, int amount,
        CardModel cardSource, SalonMember member)
    {
        var company = CompanyFor(owner);
        var replacements = 0;
        for (var i = 0; i < amount; i++)
        {
            if (company.Count >= SalonConstants.MemberSlots)
            {
                var displaced = company[0];
                company.RemoveAt(0);
                replacements++;
                await Bow(choiceContext, owner, displaced);
            }
            company.Add(member);
        }

        var delta = company.Count - Count(owner);
        if (delta > 0)
        {
            await PowerCmd.Apply<SalonMemberPower>(
                choiceContext, owner, delta, applier: owner,
                cardSource: cardSource);
        }
        Vfx.SalonVisualsBridge.Refresh(owner);
        return replacements;
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        foreach (var member in CompanyFor(Owner).ToList())
        {
            if (Owner.IsDead) break;
            var targets = CombatState?.HittableEnemies.ToList();
            if (targets == null || targets.Count == 0) break;

            var paid = FurinaResources.Encore(Owner)
                       >= SalonConstants.TickEncoreCost;
            if (paid)
            {
                FurinaResources.SpendEncore(
                    Owner, SalonConstants.TickEncoreCost);
            }

            int Num(int baseAmount)
            {
                var amt = Scaled(Owner, baseAmount);
                return paid
                    ? amt
                    : (int)(amt * SalonConstants.DryDamageMultiplier);
            }

            switch (member)
            {
                case SalonMember.Crabaletta:
                case SalonMember.Chevalmarin:
                {
                    var tick = member == SalonMember.Crabaletta
                        ? SalonConstants.CrabalettaTick
                        : SalonConstants.ChevalmarinTick;
                    var target = CombatState!.RunState.Rng.CombatTargets
                        .NextItem(targets);
                    if (target == null) break;
                    await ElementalHit.Deal(
                        choiceContext, target, Elements.Element.Hydro,
                        Num(tick), Owner);
                    break;
                }
                case SalonMember.Usher:
                    await CreatureCmd.GainBlock(
                        Owner, Num(SalonConstants.UsherTick),
                        ValueProp.Unpowered, null, fast: true);
                    break;
            }
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

/// <summary>Grand Salon, v2 semantics: +N to every member NUMERIC tick and
/// bow amount (Block included), stacking with the Fanfare Focus term.</summary>
public sealed class SalonDamageUpPower : PowerModel, ILocalizationProvider
{
    public const int MaxStacks = 6;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Grand Salon"),
        ("description",
            "[gold]Salon Member[/gold] numbers are {Amount} higher. "
          + "Maximum 6."),
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
