using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards.Furina;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.Powers;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Marker for Furina's eventual CharacterModel. Keeping the resource hooks
/// behind character identity prevents a generated Furina card obtained by
/// another character from silently granting them Furina's HP-loss engine.
/// </summary>
public interface IFurinaCharacter
{
}

/// <summary>
/// The sim constants that define Furina's two combat resources.
/// </summary>
public static class FurinaResourceConstants
{
    public const int FanfarePerHpLost = 1;
    public const int FanfarePerEncoreGained = 1;
    public const int FanfarePerEncoreSpent = 1;
    public const int BurstPerSkillTag = 5;
    public const int BurstPerReaction = 5;
    public const int BurstPerEncoreSpent = 1;
    public const int BurstPerSalonTick = 2;
    public const int BurstMax = 70;
}

/// <summary>
/// Furina's unbounded, per-combat Encore buffer.
///
/// BaseLib owns reset, affordability, cloning, and card-cost visuals. Encore
/// card costs are exceptional only in their timing: the sim spends them
/// before card effects. <see cref="FurinaResourceHooks.BeforeCardPlayed"/>
/// performs that early spend, so BaseLib's normal post-resolution spend is a
/// deliberate no-op here.
/// </summary>
public sealed class EncoreResource : BasicCustomResource
{
    public EncoreResource() : base("KLEEMOD_ENCORE")
    {
    }

    public override Task<bool> Spend<T>(
        ICombatState combatState, AbstractModel? spender, int amount, bool optional)
    {
        return Task.FromResult(true);
    }
}

/// <summary>
/// Furina's capped, spendable Fanfare. BaseLib's normal custom-cost spend
/// occurs after OnPlay, which is exactly the sim rule: Fanfare formula cards
/// resolve from the pre-spend audience level, then pay their cost.
/// </summary>
public sealed class FanfareResource : BasicCustomResource
{
    public FanfareResource() : base("KLEEMOD_FANFARE")
    {
    }
}

/// <summary>
/// Per-combat extension to Furina's default Fanfare cap. This is state rather
/// than a Power because raise_fanfare_cap is permanent for the combat and
/// should not participate in power-gain modifiers.
/// </summary>
public sealed class FanfareCapBonusResource : BasicCustomResource
{
    public FanfareCapBonusResource() : base("KLEEMOD_FANFARE_CAP_BONUS")
    {
    }
}

/// <summary>
/// Furina's 70-point Burst meter. Like Klee's meter it may overflow and is
/// emptied completely when the kit Burst is cast.
/// </summary>
public sealed class FurinaBurstResource : BasicCustomResource
{
    public FurinaBurstResource() : base("KLEEMOD_FURINA_BURST")
    {
    }

    /// <summary>Meter, not energy: opt out of BaseLib's SetToFree forwarding.
    /// See <see cref="KleeBurstResource.ApplySharedModification"/>.</summary>
    public override bool ApplySharedModification => false;

    /// <summary>Gate on the CANONICAL 70, never a discounted number. See
    /// <see cref="KleeBurstResource.CanAfford"/> for the full reasoning.</summary>
    public override bool CanAfford(CardModel card, int cost)
    {
        var canonical = CustomResources<FurinaBurstResource>.CanonicalCost(card);
        return canonical < 0 ? base.CanAfford(card, cost) : Amount >= canonical;
    }

    /// <summary>DELIBERATE NO-OP; the drain lives in <see cref="DrainOnPlay"/>.</summary>
    public override Task<bool> Spend<T>(
        ICombatState combatState, AbstractModel? spender, int amount, bool optional)
    {
        return Task.FromResult(true);
    }

    /// <summary>
    /// Sim law (combat.py play_card): a requires-full play zeroes the meter,
    /// pre-resolution. Called from FurinaResourceHooks.BeforeCardPlayed.
    /// See <see cref="KleeBurstResource.DrainOnPlay"/> for why this cannot
    /// ride the cost machinery -- the infinite-Burst bug, 2026-07-24.
    /// </summary>
    public static void DrainOnPlay(CardModel card)
    {
        if (CustomResources<FurinaBurstResource>.Cost(card) == null) return;
        var owner = card.Owner;
        if (owner == null || !FurinaResources.IsFurina(owner.Creature)) return;
        var combatState = owner.PlayerCombatState;
        if (combatState == null) return;
        CustomResources<FurinaBurstResource>.Get(combatState).Amount = 0;
        Vfx.GaugeBridge.Refresh(owner.Creature);
    }
}

/// <summary>
/// Canonical accessors and mutations for Encore/Fanfare. Every generated
/// Furina card goes through these methods so gain/spend activity and the
/// Fanfare cap cannot drift between individual card implementations.
/// </summary>
public static class FurinaResources
{
    public static bool IsFurina(Creature creature) =>
        creature.Player?.Character is IFurinaCharacter;

    private static EncoreResource? EncoreResourceFor(Creature creature)
    {
        var combatState = creature.Player?.PlayerCombatState;
        return combatState == null
            ? null
            : CustomResources<EncoreResource>.Get(combatState);
    }

    private static FanfareResource? FanfareResourceFor(Creature creature)
    {
        var combatState = creature.Player?.PlayerCombatState;
        return combatState == null
            ? null
            : CustomResources<FanfareResource>.Get(combatState);
    }

    private static FanfareCapBonusResource? FanfareCapBonusFor(Creature creature)
    {
        var combatState = creature.Player?.PlayerCombatState;
        return combatState == null
            ? null
            : CustomResources<FanfareCapBonusResource>.Get(combatState);
    }

    private static FurinaBurstResource? BurstResourceFor(Creature creature)
    {
        var combatState = creature.Player?.PlayerCombatState;
        return combatState == null
            ? null
            : CustomResources<FurinaBurstResource>.Get(combatState);
    }

    public static int Encore(Creature creature) =>
        EncoreResourceFor(creature)?.Amount ?? 0;

    public static int Fanfare(Creature creature) =>
        FanfareResourceFor(creature)?.Amount ?? 0;

    public static int Burst(Creature creature) =>
        BurstResourceFor(creature)?.Amount ?? 0;

    public static int FanfareCap(Creature creature)
    {
        if (!IsFurina(creature)) return 0;
        return creature.MaxHp / 2 + (FanfareCapBonusFor(creature)?.Amount ?? 0);
    }

    public static void GainFanfare(Creature creature, int amount)
    {
        if (amount <= 0) return;
        var resource = FanfareResourceFor(creature);
        var cap = FanfareCap(creature);
        if (resource == null || cap <= 0) return;
        resource.Amount = Math.Min(cap, resource.Amount + amount);
    }

    public static void GainEncore(Creature creature, int amount)
    {
        if (amount <= 0) return;
        var resource = EncoreResourceFor(creature);
        if (resource == null) return;
        resource.ModifyAmount(amount);
        Vfx.GaugeBridge.Refresh(creature);
        GainFanfare(
            creature, amount * FurinaResourceConstants.FanfarePerEncoreGained);
    }

    public static void GainBurst(Creature creature, int amount)
    {
        if (amount <= 0 || !IsFurina(creature)) return;
        BurstResourceFor(creature)?.ModifyAmount(amount);
    }

    /// <summary>
    /// Spend available Encore without overdraw and return the amount moved.
    /// Deliberate spends create Fanfare; damage absorption uses a separate
    /// method because the sim does not classify absorption as Encore activity.
    /// </summary>
    public static int SpendEncore(Creature creature, int amount)
    {
        if (amount <= 0) return 0;
        var resource = EncoreResourceFor(creature);
        if (resource == null) return 0;
        var spent = Math.Min(resource.Amount, amount);
        if (spent <= 0) return 0;
        resource.ModifyAmount(-spent);
        Vfx.GaugeBridge.Refresh(creature);
        GainFanfare(
            creature, spent * FurinaResourceConstants.FanfarePerEncoreSpent);
        GainBurst(
            creature, spent * FurinaResourceConstants.BurstPerEncoreSpent);
        SpotlightSystem.OnEncoreSpent(creature);
        return spent;
    }

    /// <summary>
    /// The spend_encore op: drain what is available, then pay the shortfall
    /// as true HP loss. The HP-loss hook creates Fanfare for the shortfall.
    /// </summary>
    public static async Task SpendEncoreOrHp(
        PlayerChoiceContext choiceContext, Creature creature, int amount,
        CardModel cardSource)
    {
        var spent = SpendEncore(creature, amount);
        var shortfall = amount - spent;
        if (shortfall <= 0) return;
        await CreatureCmd.Damage(
            choiceContext, creature, shortfall,
            ValueProp.Unblockable | ValueProp.Unpowered, cardSource);
    }

    /// <summary>
    /// Damage remaining after Block may consume Encore before HP. True HP
    /// costs carry Unblockable and never enter this path.
    /// </summary>
    public static decimal AbsorbDamage(Creature creature, decimal amount)
    {
        if (amount <= 0m) return 0m;
        var resource = EncoreResourceFor(creature);
        if (resource == null || resource.Amount <= 0) return amount;
        var absorbed = Math.Min(resource.Amount, (int)Math.Ceiling(amount));
        resource.ModifyAmount(-absorbed);
        Vfx.GaugeBridge.Refresh(creature);
        return Math.Max(0m, amount - absorbed);
    }

    public static void RaiseFanfareCap(Creature creature, int amount)
    {
        if (amount <= 0 || !IsFurina(creature)) return;
        FanfareCapBonusFor(creature)?.ModifyAmount(amount);
    }

    /// <summary>
    /// Resource values are canonical. These powers are the ambient in-combat
    /// display because BaseLib only renders custom resources on card costs.
    /// </summary>
    public static async Task SyncMeters(
        PlayerChoiceContext choiceContext, Creature creature,
        CardModel? cardSource = null)
    {
        if (!IsFurina(creature)) return;
        await SyncMeter<EncoreMeterPower>(
            choiceContext, creature, Encore(creature), cardSource);
        await SyncMeter<FanfareMeterPower>(
            choiceContext, creature, Fanfare(creature), cardSource);
        await SyncMeter<FurinaBurstMeterPower>(
            choiceContext, creature, Burst(creature), cardSource);
        // Salon display sync (Track D): every meter-sync moment is also a
        // dry-badge moment, and the salon reads composition + Encore here.
        Vfx.SalonVisualsBridge.Refresh(creature);
    }

    private static async Task SyncMeter<T>(
        PlayerChoiceContext choiceContext, Creature creature, int target,
        CardModel? cardSource)
        where T : PowerModel
    {
        var current = creature.Powers.OfType<T>().FirstOrDefault()?.Amount ?? 0;
        var delta = target - current;
        if (delta == 0) return;
        await PowerCmd.Apply<T>(
            choiceContext, creature, delta,
            applier: creature, cardSource: cardSource);
    }
}

/// <summary>
/// Global hook bridge for phases that do not carry a PlayerChoiceContext:
/// early Encore costs, post-Block Encore absorption, and true HP-loss
/// Fanfare. The model is registered exactly once through ModHelper.
/// </summary>
public sealed class FurinaResourceHooks : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static FurinaResourceHooks? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<FurinaResourceHooks>(
            ModelDb.GetId<FurinaResourceHooks>());
        yield return _instance;
    }

    public override Task BeforeCardPlayed(CardPlay cardPlay)
    {
        if (!cardPlay.IsFirstInSeries) return Task.CompletedTask;
        // Sim order (combat.py play_card): the requires-full drain first,
        // then the skill-tag bonus, then the Encore cost line.
        FurinaBurstResource.DrainOnPlay(cardPlay.Card);
        if (cardPlay.Card is ISkillTagCard
            && FurinaResources.IsFurina(cardPlay.Card.Owner.Creature))
        {
            FurinaResources.GainBurst(
                cardPlay.Card.Owner.Creature,
                FurinaResourceConstants.BurstPerSkillTag);
        }
        var cost = CustomResources<EncoreResource>.Cost(cardPlay.Card)
            ?.GetAmountToSpend() ?? 0;
        if (cost > 0)
        {
            FurinaResources.SpendEncore(cardPlay.Card.Owner.Creature, cost);
        }
        SpotlightSystem.NotePlay(cardPlay);
        return Task.CompletedTask;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await SpotlightSystem.ResolvePendingDraw(choiceContext, cardPlay);
        await FurinaResources.SyncMeters(
            choiceContext, cardPlay.Card.Owner.Creature, cardPlay.Card);
        await FurinaKitGrant.GrantIfCharged(
            choiceContext, cardPlay.Card.Owner);
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (FurinaResources.IsFurina(player.Creature))
        {
            SpotlightSystem.ResetTurn(player.Creature);
            await FurinaResources.SyncMeters(
                choiceContext, player.Creature);
            await FurinaKitGrant.GrantIfCharged(
                choiceContext, player);
        }
    }

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        foreach (var creature in participants)
        {
            if (creature.Player is not { } player
                || !FurinaResources.IsFurina(creature))
            {
                continue;
            }
            await FurinaResources.SyncMeters(choiceContext, creature);
            await FurinaKitGrant.GrantIfCharged(choiceContext, player);
        }
    }

    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target,
        DamageResult result, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (!FurinaResources.IsFurina(target)) return;
        await FurinaResources.SyncMeters(
            choiceContext, target, cardSource);
        await FurinaKitGrant.GrantIfCharged(
            choiceContext, target.Player);
    }

    public override decimal ModifyHpLostBeforeOsty(
        Creature target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (!FurinaResources.IsFurina(target)
            || (props & ValueProp.Unblockable) != 0)
        {
            return amount;
        }
        return FurinaResources.AbsorbDamage(target, amount);
    }

    public override Task AfterCurrentHpChanged(Creature creature, decimal delta)
    {
        if (delta < 0m && FurinaResources.IsFurina(creature))
        {
            FurinaResources.GainFanfare(
                creature,
                (int)(-delta) * FurinaResourceConstants.FanfarePerHpLost);
        }
        return Task.CompletedTask;
    }
}

public sealed class EncoreMeterPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Encore"),
        ("description",
            "After Block, Encore absorbs incoming damage before HP. "
          + "Gaining or deliberately spending it creates Fanfare."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
}

public sealed class FanfareMeterPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Fanfare"),
        ("description",
            "Generated by HP loss, Encore activity, and Center Stage plays. "
          + "Its default cap is half your maximum HP."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
}

public sealed class FurinaBurstMeterPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Burst Energy"),
        ("description",
            "Skill cards and Reactions grant 5; Salon attacks grant 2; "
          + "deliberately spent Encore grants 1 per point. At 70, "
          + "Let the People Rejoice is added to your hand."),
    };

    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
}

public static class FurinaKitGrant
{
    public static async Task GrantIfCharged(
        PlayerChoiceContext choiceContext, Player? owner)
    {
        if (owner?.Character is not IFurinaCharacter) return;
        var playerCombatState = owner.PlayerCombatState;
        var combatState = owner.Creature.CombatState;
        if (playerCombatState == null || combatState == null) return;

        var resource =
            CustomResources<FurinaBurstResource>.Get(playerCombatState);
        if (resource.Amount < FurinaResourceConstants.BurstMax) return;

        var hand = CardPile.Get(PileType.Hand, owner);
        if (hand == null
            || hand.Cards.Any(card => card is LetThePeopleRejoice)
            || hand.Cards.Count >= CardPile.MaxCardsInHand)
        {
            return;
        }

        var burst = combatState.CreateCard<LetThePeopleRejoice>(owner);
        await CardPileCmd.AddGeneratedCardToCombat(
            burst, PileType.Hand, owner);
    }
}

/// <summary>
/// The Encore engine behind All the World's a Stage (Furina's Ancient card):
/// Amount Encore at the start of every player turn, routed through
/// FurinaResources.GainEncore so the Fanfare mint, gauge refresh and salon
/// dry-badge all behave exactly like any other gain. The explicit SyncMeters
/// keeps the status-strip counters current in the same beat -- hook order
/// between powers and FurinaResourceHooks is not guaranteed.
/// </summary>
public sealed class EncorePerTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "All the World's a Stage"),
        ("description",
            "At the start of your turn, gain {Amount} [gold]Encore[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        FurinaResources.GainEncore(Owner, (int)Amount);
        await FurinaResources.SyncMeters(choiceContext, Owner);
    }
}

/// <summary>
/// "Attacks deal +Amount per 10 Fanfare", capped at two stacks by the sheet.
/// Fanfare is read per hit, so spending or gaining it changes later attacks
/// immediately.
/// </summary>
public sealed class FanfareAttackPer10Power : PowerModel, ILocalizationProvider
{
    public const int MaxStacks = 2;

    public List<(string, string)>? Localization => new()
    {
        ("title", "Rising Ovation"),
        ("description",
            "Your Attacks deal {Amount} more damage per 10 [gold]Fanfare[/gold]. "
          + "Maximum 2 stacks."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return Amount * (FurinaResources.Fanfare(Owner) / 10);
    }

    public override bool TryModifyPowerAmountReceived(
        PowerModel canonicalPower, Creature target, decimal amount,
        Creature? applier, out decimal modifiedAmount)
    {
        modifiedAmount = amount;
        if (canonicalPower is not FanfareAttackPer10Power || target != Owner)
        {
            return false;
        }
        modifiedAmount = Math.Max(0m, Math.Min(amount, MaxStacks - Amount));
        return modifiedAmount != amount;
    }
}
