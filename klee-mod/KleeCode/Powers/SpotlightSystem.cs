using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

public enum SpotlightMode
{
    None = 0,
    CenterStage = 1,
    GuestCast = 2,
}

public sealed class SpotlightModeResource : BasicCustomResource
{
    public SpotlightModeResource() : base("KLEEMOD_SPOTLIGHT_MODE")
    {
    }
}

public sealed class SpotlightMovedResource : BasicCustomResource
{
    public SpotlightMovedResource() : base("KLEEMOD_SPOTLIGHT_MOVED")
    {
    }
}

public sealed class SpotlightPlaysResource : BasicCustomResource
{
    public SpotlightPlaysResource() : base("KLEEMOD_SPOTLIGHT_PLAYS")
    {
    }
}

public sealed class SpotlightSpendBoostResource : BasicCustomResource
{
    public SpotlightSpendBoostResource() : base("KLEEMOD_SPOTLIGHT_SPEND_BOOST")
    {
    }
}

/// <summary>
/// Spotlight v5. Center Stage marks Furina's own cards and generates Fanfare
/// without changing their numbers. Guest Cast marks every Companion and
/// multiplies printed damage/Block; card-mediated bonuses ride the same pipe.
/// </summary>
public static class SpotlightSystem
{
    public const decimal GuestCastBaseMultiplier = 1.5m;
    public const int FanfarePerCenterStagePlay = 2;

    private static readonly Dictionary<CardPlay, int> PendingDraws = new();

    private static T? Resource<T>(Creature creature)
        where T : CustomResource, new()
    {
        var combat = creature.Player?.PlayerCombatState;
        return combat == null ? null : CustomResources<T>.Get(combat);
    }

    public static SpotlightMode Mode(Creature creature) =>
        (SpotlightMode)(Resource<SpotlightModeResource>(creature)?.Amount ?? 0);

    public static bool MovedThisTurn(Creature creature) =>
        (Resource<SpotlightMovedResource>(creature)?.Amount ?? 0) > 0;

    public static int PlaysThisTurn(Creature creature) =>
        Resource<SpotlightPlaysResource>(creature)?.Amount ?? 0;

    public static async Task Designate(
        PlayerChoiceContext choiceContext, Creature creature,
        SpotlightMode mode, CardModel? cardSource)
    {
        if (!FurinaResources.IsFurina(creature) || mode == SpotlightMode.None)
        {
            return;
        }
        var resource = Resource<SpotlightModeResource>(creature);
        if (resource == null || resource.Amount == (int)mode) return;
        resource.Amount = (int)mode;
        var moved = Resource<SpotlightMovedResource>(creature);
        if (moved != null) moved.Amount = 1;

        foreach (var old in creature.Powers
                     .Where(power => power is CenterStagePower
                                     or GuestCastPower)
                     .ToList())
        {
            await PowerCmd.Remove(old);
        }
        if (mode == SpotlightMode.CenterStage)
        {
            await PowerCmd.Apply<CenterStagePower>(
                choiceContext, creature, 1,
                applier: creature, cardSource: cardSource);
        }
        else
        {
            await PowerCmd.Apply<GuestCastPower>(
                choiceContext, creature, 1,
                applier: creature, cardSource: cardSource);
        }
    }

    public static bool IsSpotlighted(CardModel card)
    {
        var owner = card.Owner?.Creature;
        if (owner == null) return false;
        return Mode(owner) switch
        {
            SpotlightMode.CenterStage =>
                card is ICharacterCard { CharacterId: "furina" },
            SpotlightMode.GuestCast => card is ICompanionCard,
            _ => false,
        };
    }

    private static int PowerAmount<T>(Creature owner) where T : PowerModel =>
        owner.Powers.OfType<T>().FirstOrDefault()?.Amount ?? 0;

    private static decimal OutwardMultiplier(CardModel card)
    {
        if (!IsSpotlighted(card)
            || Mode(card.Owner.Creature) != SpotlightMode.GuestCast)
        {
            return 1m;
        }
        var owner = card.Owner.Creature;
        var percentagePoints =
            PowerAmount<SpotlightMultBonusPower>(owner)
            + PowerAmount<SpotlightMultBonusTurnPower>(owner)
            + (Resource<SpotlightSpendBoostResource>(owner)?.Amount ?? 0);
        return GuestCastBaseMultiplier + percentagePoints / 100m;
    }

    public static decimal PrintedDamage(CardModel card, decimal amount)
    {
        var scaled = Math.Truncate(amount * OutwardMultiplier(card));
        if (!IsSpotlighted(card)
            || Mode(card.Owner.Creature) != SpotlightMode.GuestCast)
        {
            return scaled;
        }
        return scaled
               + PowerAmount<SpotlightFlatDamagePower>(card.Owner.Creature)
               + PowerAmount<SpotlightFlatDamageTurnPower>(card.Owner.Creature);
    }

    public static decimal PrintedBlock(CardModel card, decimal amount) =>
        Math.Truncate(amount * OutwardMultiplier(card));

    public static void ResetTurn(Creature creature)
    {
        var moved = Resource<SpotlightMovedResource>(creature);
        var plays = Resource<SpotlightPlaysResource>(creature);
        var spendBoost = Resource<SpotlightSpendBoostResource>(creature);
        if (moved != null) moved.Amount = 0;
        if (plays != null) plays.Amount = 0;
        if (spendBoost != null) spendBoost.Amount = 0;
        foreach (var play in PendingDraws.Keys
                     .Where(play => play.Card.Owner.Creature == creature)
                     .ToList())
        {
            PendingDraws.Remove(play);
        }
    }

    public static void NotePlay(CardPlay cardPlay)
    {
        var card = cardPlay.Card;
        if (!cardPlay.IsFirstInSeries || !IsSpotlighted(card)) return;
        var owner = card.Owner.Creature;
        var plays = Resource<SpotlightPlaysResource>(owner);
        if (plays == null) return;
        var first = plays.Amount == 0;
        plays.ModifyAmount(1);

        if (Mode(owner) == SpotlightMode.CenterStage)
        {
            FurinaResources.GainFanfare(owner, FanfarePerCenterStagePlay);
        }
        if (!first) return;

        var encore = PowerAmount<SpotlightEncoreFirstPower>(owner);
        if (encore > 0)
        {
            FurinaResources.GainEncore(owner, encore);
        }
        var draw = PowerAmount<SpotlightDrawPower>(owner);
        if (draw > 0)
        {
            PendingDraws[cardPlay] = draw;
        }
    }

    public static async Task ResolvePendingDraw(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!PendingDraws.Remove(cardPlay, out var amount) || amount <= 0)
        {
            return;
        }
        await CardPileCmd.Draw(
            choiceContext, amount, cardPlay.Card.Owner);
    }

    public static void OnEncoreSpent(Creature creature)
    {
        var boost = PowerAmount<OvationSpendBoostPower>(creature);
        if (boost <= 0) return;
        Resource<SpotlightSpendBoostResource>(creature)?.ModifyAmount(boost);
    }
}

public sealed class CenterStagePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Center Stage"),
        ("description",
            "Furina is Spotlighted. Playing her cards generates "
          + "2 Fanfare; their printed numbers are unchanged."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Single;
}

public sealed class GuestCastPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Guest Cast"),
        ("description",
            "Companion cards are Spotlighted. Their printed damage and Block "
          + "are 50% stronger; their plays generate no Fanfare."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Single;
}

/// <summary>
/// Shared shape for every Spotlight texture power: a Buff counter with NO
/// stack ceiling.
///
/// The 2026-07-24 cap ruling landed in two rounds. Round one dropped the four
/// non-compounding caps and split a CappedSpotlightPower subclass out for the
/// two percentage multipliers (spotlight_mult_bonus, ovation_spend_boost).
/// Round two -- after a 2000-run x 2-seed A/B showed the whole cap set moving
/// run success by at most +0.5pp (favorable, p~0.02) -- uncapped those two as
/// well, to match base StS where Power dupes always stack. That emptied
/// CappedSpotlightPower, so it is gone and every Spotlight power lives here.
///
/// KleePowerIcons keys its Spotlight icon off this base type, so keeping the
/// common base (rather than folding straight into PowerModel) keeps the icon
/// match a single case. The two multipliers are genuinely compounding and were
/// FLAGGED for a ceiling re-check when difficulty calibration makes the
/// spotlight plan viable enough to measure them.
/// </summary>
public abstract class SpotlightPower : PowerModel
{
    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;
}

public sealed class SpotlightDiscountPower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Leading Role"),
        ("description",
            "The first [gold]Spotlighted[/gold] card each turn costs "
          + "{Amount} less."),
    };

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (card.Owner?.Creature != Owner
            || !SpotlightSystem.IsSpotlighted(card)
            || SpotlightSystem.PlaysThisTurn(Owner) > 0
            || originalCost <= 0m)
        {
            return false;
        }
        modifiedCost = Math.Max(0m, originalCost - Amount);
        return modifiedCost != originalCost;
    }
}

public sealed class SpotlightDrawPower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Supporting Cast"),
        ("description",
            "The first [gold]Spotlighted[/gold] card each turn draws "
          + "{Amount} card."),
    };
}

public sealed class SpotlightMultBonusPower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Top Billing"),
        ("description",
            "[gold]Spotlighted[/gold] Companion numbers are {Amount}% "
          + "stronger this combat."),
    };
}

public sealed class SpotlightMultBonusTurnPower
    : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Limelight"),
        ("description",
            "[gold]Spotlighted[/gold] Companion numbers are {Amount}% "
          + "stronger this turn."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side == CombatSide.Player) await PowerCmd.Remove(this);
    }
}

public sealed class SpotlightFlatDamagePower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Star of the Show"),
        ("description",
            "[gold]Spotlighted[/gold] Companion damage gains {Amount}."),
    };
}

public sealed class SpotlightFlatDamageTurnPower
    : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Stage Lights"),
        ("description",
            "[gold]Spotlighted[/gold] Companion damage gains {Amount} "
          + "this turn."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side == CombatSide.Player) await PowerCmd.Remove(this);
    }
}

public sealed class OvationSpendBoostPower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Standing Ovation"),
        ("description",
            "Whenever you spend Encore, [gold]Spotlighted[/gold] Companion "
          + "numbers are {Amount}% stronger this turn."),
    };
}

public sealed class SpotlightEncoreFirstPower
    : SpotlightPower, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Ovation Trickle"),
        ("description",
            "The first [gold]Spotlighted[/gold] card each turn grants "
          + "{Amount} Encore."),
    };
}
