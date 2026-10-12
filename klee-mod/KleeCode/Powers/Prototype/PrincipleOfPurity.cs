using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using KleeMod.Elements;
using MegaCrit.Sts2.Core.Combat;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

// ---------------------------------------------------------------------------
// DURIN, PRINCIPLE OF PURITY (AoE trim, 2026-10-03,
// review/active/aoe-trim-2026-10-03.md sec.5): "At the start of your turn,
// deal 4 [6] Pyro damage to a random enemy. Choose one for the combat.
// White: Enemies take 50% [75%] more damage from Elemental Reactions. Dark:
// Your Pyro damage deals 4 [6] more." Sim twins: `mc_purity_strike`,
// `mc_purity_white` and `mc_purity_dark` in `tier0/engine/effects.py`.
// ---------------------------------------------------------------------------

/// <summary>
/// The turn-start hit. PERMANENT; the stack IS the damage, so two copies add
/// into one hit. A powered Pyro hit of its owner's through
/// <see cref="ElementalHit.Deal"/> (Strength and Weak apply, as on the sim's
/// companion hit). Sim twin: the `mc_purity_strike` read at the tail of
/// `effects.companion_overhaul_turn_start`'s Mondstadt block.
/// </summary>
public sealed class PurityStrikePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Principle of Purity"),
        ("description",
            "At the start of your turn, deal [blue]{Amount}[/blue] "
          + "[gold]Pyro[/gold] damage to a random enemy."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (player.Creature != Owner || Amount <= 0) return;
        var combat = CombatState;
        if (combat == null) return;
        var target = CompanionOverhaulTargeting.RandomEnemy(combat);
        if (target == null) return;
        await ElementalHit.Deal(
            choiceContext, target, Element.Pyro, Amount, Owner);
    }
}

/// <summary>
/// WHITE, THE TEAM FORM: "Enemies take 50% [75%] more damage from Elemental
/// Reactions." The stack IS the percentage and copies add. It hooks nothing:
/// <see cref="CompanionOverhaulReactions.DamageMultiplier"/> sums every
/// player's White, so ANY player's reaction against an enemy is boosted while
/// any player holds it.
/// </summary>
public sealed class PurityWhitePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Principle of Purity: White"),
        ("description",
            "Enemies take [blue]{Amount}[/blue]% more damage from "
          + "[gold]Elemental Reactions[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>Every player's White, in percentage points. Pure.</summary>
    public static int TeamPercent(Creature? anyone)
    {
        var players = anyone?.CombatState?.PlayerCreatures;
        if (players == null)
        {
            return anyone == null ? 0
                : anyone.Powers.OfType<PurityWhitePower>().Sum(p => (int)p.Amount);
        }
        return players.Sum(c => c.Powers.OfType<PurityWhitePower>()
            .Sum(p => (int)p.Amount));
    }
}

/// <summary>
/// DARK: "Your Pyro damage deals 4 [6] more." Every Pyro hit its owner deals:
/// a card's hit (<see cref="ModifyDamageAdditive"/>, the additive phase, so a
/// Vaporize amplifies it with the rest) and every hit through
/// <see cref="ElementalHit"/> -- a Bomb, a Mine, a companion volley, the turn-
/// start hit above -- which adds <see cref="BonusFor"/> before its amplifier.
/// A reaction's splash is the reaction's damage, not Pyro damage, and goes
/// through neither door. Sim twin: the `mc_purity_dark` read in
/// `effects.deal_damage_to_enemy`.
/// </summary>
public sealed class PurityDarkPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Principle of Purity: Dark"),
        ("description",
            "Your [gold]Pyro[/gold] hits deal [blue]{Amount}[/blue] additional "
          + "damage."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The flat bonus <paramref name="dealer"/>'s Pyro hit takes, or
    /// 0 for any other element. Pure; the non-card door's read.</summary>
    public static int BonusFor(Creature? dealer, Element element)
    {
        if (dealer == null || element != Element.Pyro) return 0;
        return dealer.Powers.OfType<PurityDarkPower>().Sum(p => (int)p.Amount);
    }

    /// <summary>NO TARGET IS ASKED FOR (2026-10-10): the bonus is the
    /// owner's, and a card in the hand previews with a null target, so a
    /// <c>target == null</c> gate dropped it from the face. The owner's own
    /// body is still refused.</summary>
    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer,
        CardModel? cardSource, CardPlay? cardPlay)
    {
        if (dealer != Owner || target == Owner) return 0m;
        if (cardSource == null || !props.IsPoweredAttack()) return 0m;
        return CompanionOverhaulRiders.ElementFor(cardSource, dealer) == Element.Pyro
            ? Amount : 0m;
    }
}
