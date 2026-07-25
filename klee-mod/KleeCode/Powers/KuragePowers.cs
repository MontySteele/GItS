using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
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
/// Bake-Kurage on the field.
///
/// Stacks ARE turns remaining (the OzSummonPower grammar). Re-summoning
/// REFRESHES rather than adds -- a second jellyfish is not a bigger jellyfish
/// -- which is why <see cref="KurageSummon.Field"/> below sets the duration to
/// max(current, turns) instead of applying stacks.
///
/// The pulse reads Charge and never spends it. Sim order is HIT, then Block,
/// then tick down; the manual TickDownDuration after the volley preserves it,
/// same as Oz.
/// </summary>
public sealed class KurageSummonPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Bake-Kurage"),
        ("description",
            "At the end of your turn, the jellyfish deals "
          + $"{KokomiConstants.KuragePulseBase} plus "
          + $"{KokomiConstants.KuragePulsePerCharge} per [gold]Charge[/gold] "
          + "damage and applies [gold]Hydro[/gold] to a random enemy. "
          + "Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>
    /// The number the pulse will deal right now. Public so the card face and
    /// the hover tip read the SAME arithmetic the hit uses -- the Furina
    /// legibility lesson (preview and effect must not be able to drift).
    /// </summary>
    public static int PulseDamage(Creature? owner) =>
        KokomiConstants.KuragePulseBase
        + KokomiConstants.KuragePulsePerCharge * KokomiResources.GetCharge(owner);

    public override async Task BeforeSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        if (Owner.Player == null) return;

        var damage = PulseDamage(Owner);

        var candidates = CombatState.HittableEnemies.ToList();
        if (candidates.Count > 0)
        {
            var target = CombatState.RunState.Rng.CombatTargets.NextItem(candidates);
            if (target != null)
            {
                await ElementalHit.Deal(
                    choiceContext, target, Element.Hydro, damage, Owner);
            }
        }

        // Block lands whether or not an enemy was standing: under the R52
        // healing law her mending is Block, and a pulse into an empty board
        // still mends. Baseline is 0 since the starter rework; the drafted
        // half rides the same line so restoring the baseline is one constant.
        var block = KokomiConstants.KuragePulseBlock
                    + KurageWardPower.WardAmount(Owner);
        if (block > 0)
        {
            await CreatureCmd.GainBlock(Owner, block, ValueProp.Move, null);
        }

        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>Fielding and refreshing the jellyfish.</summary>
public static class KurageSummon
{
    /// <summary>
    /// REFRESH, NEVER STACK. tier0 _op_summon_kurage:
    /// powers["kurage_summon"] = max(existing, turns).
    /// </summary>
    public static async Task Field(
        PlayerChoiceContext choiceContext, Creature owner, int turns,
        CardModel? source)
    {
        var existing = owner.Powers
            .FirstOrDefault(p => p is KurageSummonPower);
        if (existing != null)
        {
            var have = (int)existing.Amount;
            if (turns > have)
            {
                await PowerCmd.ModifyAmount(
                    choiceContext, existing, turns - have, owner, source, false);
            }
            return;
        }

        await PowerCmd.Apply(
            choiceContext, ModelDb.Power<KurageSummonPower>(), owner, turns,
            owner, source, false);
    }
}

/// <summary>
/// Kurage's Oath -- the jellyfish's canon second job, drafted rather than
/// baseline.
///
/// COUPLING, on the record (playtest sprint P1): this power pays out once per
/// PULSE, so its real value is (ward x pulses per play). It owns only the
/// first factor -- the second is KurageDuration and the bake_kurage upgrade.
/// The 12 was measured at duration 1. Raising the duration reprices this card
/// without editing it; the sim pins that (see
/// test_oath_ward_is_pinned_to_the_pulse_frequency_it_was_measured_at) and it
/// carries a [USER] "maybe too strong" flag as the first knob back.
/// </summary>
public sealed class KurageWardPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Kurage's Oath"),
        ("description",
            "Each [gold]Bake-Kurage[/gold] pulse also grants {Amount} Block."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static int WardAmount(Creature? owner)
    {
        if (owner == null) return 0;
        var power = owner.Powers.FirstOrDefault(p => p is KurageWardPower);
        return power == null ? 0 : (int)power.Amount;
    }
}

/// <summary>
/// The Ceremonial Garment: her Burst's state (kit card
/// <see cref="Cards.Kokomi.CeremonialGarment"/>; Nereid's Ascension enters it
/// too).
///
/// TWO riders, and the damage one is the whole point of the Burst. While the
/// state holds:
///   - her ATTACKS read the Charge bank, +1 damage per
///     <see cref="KokomiConstants.GarmentChargeDivisor"/> Charge, per hit;
///   - her attacks ALSO grant Block (the Charlotte precedent; in canon the
///     burst's attacks damage AND restore the party).
///
/// The read is a READ: nothing here decrements the bank, and if it ever
/// starts to, every scaling number on her sheet was measured against a bank
/// that only grows and is silently wrong.
///
/// Both riders are applied from outside the card faces -- the damage one here
/// in ModifyDamageAdditive, the Block one in
/// <see cref="KokomiGarmentHooks"/> -- because they must catch every attack
/// she plays, drafted and generated alike, and no card face can know that.
///
/// THE CASKET LINK IS INERT AND SHIPS ANYWAY. Casting the Burst refreshes a
/// fielded Bake-Kurage (Tamakushi Casket, her A1). At KurageDuration 1 a
/// fielded jellyfish is always at exactly 1, so refresh-to-full is a no-op
/// unless the Burst goes off the same turn the Kurage was played. Parity means
/// parity: the sim carries the same dead link, [USER] confirmed shipping it
/// rather than holding the build, and the Burst rework inherits it with the
/// playtest's evidence attached.
/// </summary>
public sealed class CeremonialGarmentPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Ceremonial Garment"),
        ("description",
            "Your Attacks deal 1 more damage per "
          + $"{KokomiConstants.GarmentChargeDivisor} [gold]Charge[/gold] and "
          + $"grant {KokomiConstants.GarmentAttackBlock} Block. "
          + "Lasts {Amount} more turn{Amount:plural:|s}."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public static bool IsUp(Creature? owner) =>
        owner != null && owner.Powers.Any(p => p is CeremonialGarmentPower);

    /// <summary>
    /// The bonus her attacks are carrying RIGHT NOW. Public so card faces and
    /// hover tips read the same arithmetic the hit uses -- the Furina
    /// legibility lesson: a preview and an effect that compute separately will
    /// eventually disagree, and the player believes the preview.
    /// </summary>
    public static int ChargeBonus(Creature? owner) =>
        IsUp(owner)
            ? KokomiResources.GetCharge(owner) / KokomiConstants.GarmentChargeDivisor
            : 0;

    /// <summary>
    /// tier0 flat_attack_bonus: `bonus += p.charge // GARMENT_CHARGE_DIVISOR`,
    /// folded in flat BEFORE Strength and Vulnerable, and applied PER TARGET
    /// (the sim adds current_attack_bonus inside its per-target damage
    /// computation, so an AoE attack pays it to each enemy). Additive is
    /// exactly that phase, which is why this is not a multiplier hook.
    ///
    /// Stacking is irrelevant by construction: the power's Amount is TURNS
    /// REMAINING, not a magnitude, so re-casting the Burst extends the window
    /// and never doubles the read.
    /// </summary>
    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (!props.IsPoweredAttack()) return 0m;
        if (cardSource is not { Type: CardType.Attack }) return 0m;
        return KokomiResources.GetCharge(Owner) / KokomiConstants.GarmentChargeDivisor;
    }

    public override async Task AfterSideTurnEnd(
        PlayerChoiceContext choiceContext, CombatSide side,
        IEnumerable<Creature> participants)
    {
        if (side != CombatSide.Player) return;
        await PowerCmd.TickDownDuration(this);
    }
}

/// <summary>
/// The Garment's attack rider, and the Casket link. Separate from
/// <see cref="KokomiResourceHooks"/> so the Burst's behaviour reads in one
/// place when the rework lands.
/// </summary>
public sealed class KokomiGarmentHooks : AbstractModel
{
    public override bool ShouldReceiveCombatHooks => true;

    private static KokomiGarmentHooks? _instance;

    public static IEnumerable<AbstractModel> Subscribe(CombatState combatState)
    {
        _instance ??= ModelDb.GetById<KokomiGarmentHooks>(
            ModelDb.GetId<KokomiGarmentHooks>());
        yield return _instance;
    }

    public override async Task AfterCardPlayed(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var owner = cardPlay.Card.Owner?.Creature;
        if (!KokomiResources.IsKokomi(owner)) return;
        if (cardPlay.Card.Type != CardType.Attack) return;
        if (!CeremonialGarmentPower.IsUp(owner)) return;

        await CreatureCmd.GainBlock(
            owner!, KokomiConstants.GarmentAttackBlock, ValueProp.Move,
            cardPlay);
    }
}

/// <summary>
/// Vigil of the Deep -- the prevention ward (kickoff §2.4).
///
/// The first time each turn an attack would land unblocked damage, prevent up
/// to Amount of it and Exhaust a random card from the draw pile. Prevention is
/// priced in FUTURE DRAWS, not HP: R52's healing law says her HP bar never
/// moves, the incoming does.
///
/// The exhaust routes through the ordinary funnel, so being attacked feeds
/// Charge -- getting hit fuels the finisher, which is the stability identity
/// expressed as a mechanic rather than as flavour.
///
/// IT CAN RUN OUT, and that is the design. If draw and discard are both empty
/// the ward cannot pay and does not proc: the deck really is her second HP bar.
/// A version that prevents for free would be a different, much safer card.
/// </summary>
public sealed class PreventExhaustWardPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Vigil of the Deep"),
        ("description",
            "The first time you would take unblocked attack damage each turn, "
          + "prevent up to {Amount} of it and [gold]Exhaust[/gold] a random "
          + "card from your draw pile."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Reset with the other per-turn windows, matching the sim's
    /// `prevention_used_this_turn`.</summary>
    private bool _usedThisTurn;

    public override Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature == Owner) _usedThisTurn = false;
        return Task.CompletedTask;
    }

    public override decimal ModifyDamageAdditive(
        Creature target, decimal amount, ValueProp props, Creature dealer,
        CardModel cardSource)
    {
        if (target != Owner || _usedThisTurn || amount <= 0) return 0m;
        if (Owner.Player == null) return 0m;
        // Block resolves first in the sim (the ward reads what is left
        // UNBLOCKED), and the engine applies Block after additive modifiers,
        // so the reduction is capped at the ward rather than at the raw hit.
        var drawPile = CardPile.Get(PileType.Draw, Owner.Player);
        var discard = CardPile.Get(PileType.Discard, Owner.Player);
        var fuel = (drawPile?.Cards.Count ?? 0) + (discard?.Cards.Count ?? 0);
        if (fuel == 0) return 0m;        // defenceless: the deck is spent

        _usedThisTurn = true;
        _pendingExhaust = true;
        return -System.Math.Min(amount, Amount);
    }

    private bool _pendingExhaust;

    /// <summary>
    /// The fuel is paid AFTER the hit resolves. Exhausting inside the damage
    /// modifier would mutate piles mid-calculation, which is the class of bug
    /// that produces "the number changed while I was reading it".
    /// </summary>
    public override async Task AfterDamageReceived(
        PlayerChoiceContext choiceContext, Creature target, DamageResult result,
        ValueProp props, Creature dealer, CardModel cardSource)
    {
        if (target != Owner || !_pendingExhaust) return;
        _pendingExhaust = false;
        if (Owner.Player == null) return;

        var drawPile = CardPile.Get(PileType.Draw, Owner.Player);
        if (drawPile == null || drawPile.Cards.Count == 0) return;
        var victim = Owner.Player.RunState.Rng.CombatTargets
            .NextItem(drawPile.Cards.ToList());
        if (victim != null)
        {
            await CardCmd.Exhaust(choiceContext, victim);
        }
    }
}
