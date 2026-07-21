using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Cards;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// tier0/constants.py mirrors for the companion powers. Numbers mirrored,
/// never re-derived (sim is LAW).
/// </summary>
public static class CompanionConstants
{
    public const int OzDamage = 3;             // OZ_DMG (applies electro)
    public const int WitchsFlameDamage = 4;    // WITCHS_FLAME_DMG (applies pyro)
    public const int SolarIsotomaBlock = 3;    // SOLAR_ISOTOMA_BLOCK per hit
    public const int CelestialGiftBlock = 4;   // CELESTIAL_GIFT_BLOCK per turn
}

/// <summary>
/// Which companions have been played this combat, unique in first-play
/// order (tier0 companions_played + dict.fromkeys) -- Best Friends Forever
/// reads it. Keyed to the combat-state instance, the
/// DetonationsThisCombat pattern: a fresh combat starts empty with no
/// reset hook. Recorded from KleeElementalHooks.BeforeCardPlayed
/// (IsFirstInSeries = once per play, the sim's play_card append site).
/// </summary>
public static class CompanionPlays
{
    private static ICombatState? _combat;
    private static readonly List<ModelId> _played = new();

    public static void Record(ICombatState? combatState, CardModel card)
    {
        if (combatState == null) return;
        if (!ReferenceEquals(combatState, _combat))
        {
            _combat = combatState;
            _played.Clear();
        }
        if (!_played.Contains(card.Id))
        {
            _played.Add(card.Id);
        }
    }

    public static IReadOnlyList<ModelId> PlayedThisCombat(ICombatState combatState)
        => ReferenceEquals(combatState, _combat)
            ? _played
            : (IReadOnlyList<ModelId>)System.Array.Empty<ModelId>();
}

/// <summary>
/// Friendly Visit: Companion cards cost Amount less this turn (tier0
/// companion_cost_delta_this_turn, reset at the next player turn start).
/// Rides the same Hook.ModifyEnergyCostInCombat surface as SparkPower's
/// zeroing; the game clamps at 0 via GetAmountToSpend's Math.Max.
/// </summary>
public sealed class CompanionCostThisTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Friendly Visit"),
        ("description",
            "[gold]Companion[/gold] cards cost {Amount} less this turn."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override bool TryModifyEnergyCostInCombat(
        CardModel card, decimal originalCost, out decimal modifiedCost)
    {
        modifiedCost = originalCost;
        if (card is not ICompanionCard) return false;
        if (card.Owner?.Creature != Owner) return false;
        if (originalCost <= 0m) return false;
        modifiedCost = System.Math.Max(0m, originalCost - Amount);
        return true;
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Study Buddy: the next Companion card played this turn is played Amount
/// extra times (tier0 replay_next_companion: consumed whole by the next
/// companion play_card, reset at turn start). ModifyCardPlayCount is the
/// game's replay surface -- the extra plays are a series on one CardPlay,
/// which is also what the sim's `for _ in range(replays)` is.
/// </summary>
public sealed class ReplayNextCompanionPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Study Buddy"),
        ("description",
            "The next [gold]Companion[/gold] card you play this turn is "
          + "played {Amount} extra time{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override int ModifyCardPlayCount(
        CardModel card, Creature? target, int playCount)
    {
        if (card is not ICompanionCard) return playCount;
        if (card.Owner?.Creature != Owner) return playCount;
        return playCount + Amount;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        // Consumed by that one companion play (sim zeroes the counter as it
        // captures the replays); the play count was read at play creation,
        // so removing after the series cannot shorten it.
        if (cardPlay.Card is not ICompanionCard) return;
        if (cardPlay.Card.Owner.Creature != Owner) return;
        if (!cardPlay.IsLastInSeries) return;
        await PowerCmd.Remove(this);
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        // Expires with the turn (sim resets at the next turn start).
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Fischl: at the end of your turn, Oz makes one full-pipeline Electro hit
/// (tier0 player_turn_end_triggers: deal_damage_to_enemy(OZ_DMG,
/// element="electro") to a random living enemy), then the summon ticks down.
/// Sim order is hit THEN decrement, hence the manual TickDownDuration after
/// the volley -- the AuraPower own-decay idiom.
/// </summary>
public sealed class OzSummonPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Oz, at Your Side"),
        ("description",
            "At the end of your turn, Oz deals "
          + $"{CompanionConstants.OzDamage} damage and applies "
          + "[gold]Electro[/gold] to a random enemy. "
          + "Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        if (Owner.Player == null) return;

        var candidates = CombatState.HittableEnemies.ToList();
        if (candidates.Count > 0)
        {
            var target = CombatState.RunState.Rng.CombatTargets.NextItem(candidates);
            if (target != null)
            {
                await ElementalHit.Deal(
                    choiceContext, target, Element.Electro,
                    CompanionConstants.OzDamage, Owner);
            }
        }

        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Durin: PERMANENT. Amount is a PERCENT boost to amplifying reactions
/// (ReactionTable.AmplifierMultiplier reads it, additive with Vermillion
/// Pact's AmpReactionUpPower -- tier0 reactions._amp_mult), plus one
/// end-of-turn Pyro hit to a random enemy (no tick-down; the sim's
/// witchs_flame never decrements).
/// </summary>
public sealed class WitchsFlamePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Witch's Flame"),
        ("description",
            "[gold]Vaporize[/gold] and [gold]Melt[/gold] amplify {Amount}% "
          + "more. At the end of your turn, deal "
          + $"{CompanionConstants.WitchsFlameDamage} damage and apply "
          + "[gold]Pyro[/gold] to a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        if (Owner.Player == null) return;

        var candidates = CombatState.HittableEnemies.ToList();
        if (candidates.Count == 0) return;
        var target = CombatState.RunState.Rng.CombatTargets.NextItem(candidates);
        if (target == null) return;

        await ElementalHit.Deal(
            choiceContext, target, Element.Pyro,
            CompanionConstants.WitchsFlameDamage, Owner);
    }
}

/// <summary>
/// Albedo, 3 turns: every powered-attack hit you deal to an enemy holding an
/// aura grants Block (tier0 deal_damage_to_enemy: the Solar Isotoma check
/// runs BEFORE the hit resolves, so the hit that consumes the aura still
/// pays out -- hence BeforeDamageReceived, which fires before the damage and
/// before AuraPower's AfterDamageReceived consumption). Ticks down at the
/// player's turn end (sim player_turn_end_triggers).
/// </summary>
public sealed class SolarIsotomaPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Solar Isotoma"),
        ("description",
            "Your Attacks against enemies holding an elemental aura grant "
          + $"{CompanionConstants.SolarIsotomaBlock} [gold]Block[/gold] per "
          + "hit. Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task BeforeDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, decimal amount,
        ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (dealer != Owner || target == Owner) return;
        if (!props.IsPoweredAttack()) return;
        if (AuraCmd.Find(target) == null) return;

        await CreatureCmd.GainBlock(
            Owner, CompanionConstants.SolarIsotomaBlock,
            ValueProp.Unpowered, null, fast: true);
    }

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// Nicole: your attack cards deal +Amount per hit (tier0 resolve_card adds
/// celestial_gift into current_attack_bonus, which lands on every hit's
/// base), and you gain Block at the start of your turn
/// (player_turn_start_triggers).
/// </summary>
public sealed class CelestialGiftPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Celestial Gift"),
        ("description",
            "Your Attacks deal {Amount} more damage. At the start of your "
          + $"turn, gain {CompanionConstants.CelestialGiftBlock} [gold]Block[/gold]."),
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
        return Amount;
    }

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner) return;
        await CreatureCmd.GainBlock(
            Owner, CompanionConstants.CelestialGiftBlock,
            ValueProp.Unpowered, null, fast: true);
    }
}

/// <summary>
/// Bennett burst (Fantastic Voyage): attacks +Amount for the REST OF THIS
/// TURN; the sim pops attack_up_this_turn at player_turn_end_triggers.
/// </summary>
public sealed class AttackUpThisTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Fantastic Voyage"),
        ("description", "Your Attacks deal {Amount} more damage this turn."),
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
        return Amount;
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.Remove(this);
    }
}

/// <summary>
/// Bennett Passion's rider (buff_next_attack): your NEXT attack card deals
/// +Amount per hit, then the whole stack is consumed. tier0 resolve_card
/// pops next_attack_up into the play's attack bonus, so the bonus covers
/// every hit of that one card (its repeat tail included -- same CardPlay)
/// and is gone afterwards; here the modify hook pays out during the play
/// and AfterCardPlayed removes the power once the attack's series ends.
/// </summary>
public sealed class NextAttackUpPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Passion Overload"),
        ("description", "Your next Attack deals {Amount} more damage."),
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
        return Amount;
    }

    /// <summary>
    /// Consumed by the FIRST resolution of an attack card, not the last.
    ///
    /// CORRECTION (bug hunt 2026-07-21). This gated on IsLastInSeries, which
    /// let the bonus ride every replay of a Study Buddy series: Passion
    /// Overload (+4) -> Study Buddy -> Kaeya dealt 18 where the sim deals 14.
    /// tier0 resolve_card POPS next_attack_up (its siblings celestial_gift and
    /// attack_up_this_turn deliberately use .get(), which is what makes the pop
    /// load-bearing rather than incidental), and combat.py's replay loop issues
    /// N separate resolve_card calls -- so replay #2 sees nothing.
    ///
    /// The repeat tail is unaffected and must be: repeat_this re-runs
    /// _resolve_effects INSIDE one resolve_card, after current_attack_bonus is
    /// already snapshotted, so the tail keeps the bonus. A series is the replay
    /// loop; the tail is an in-OnPlay for-loop. Removing at IsFirstInSeries
    /// draws the line in exactly the same place the sim does.
    /// </summary>
    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (cardPlay.Card.Type != CardType.Attack) return;
        if (cardPlay.Card.Owner.Creature != Owner) return;
        if (!cardPlay.IsFirstInSeries) return;
        await PowerCmd.Remove(this);
    }
}
