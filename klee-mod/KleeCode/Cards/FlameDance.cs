using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards;

/// <summary>
/// Sheet: uncommon attack, cost 2, 7 damage to ALL enemies, +4 vs enemies
/// with any aura. Hand-written (R23).
///
/// The per-target bonus lives in ModifyDamageAdditive -- cards in piles are
/// hook listeners, and this is the Strength/Vigor idiom, so each enemy's hit
/// (and its damage preview) picks up the bonus only when that enemy carries
/// an aura. The bonus reads the aura but does not consume it; consumption
/// stays AuraPower's job (this card's Pyro hits trigger it as usual).
/// </summary>
public sealed class FlameDance : CustomCardModel, IElementalCard
{
    /// <summary>All of Klee's attacks apply Pyro (sheet: catalyst-grade cadence).</summary>
    public Element Element => Element.Pyro;

    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("flame_dance");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Flame Dance"),
        ("description",
            "Deal {Damage:diff()} damage to ALL enemies. "
          + "Enemies with an aura take {ExtraDamage} more."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(7m, ValueProp.Move),
            new ExtraDamageVar(4m),
        };

    // autoAdd: false -- KleeCardPool declares pool membership itself (see Kaboom).
    public FlameDance()
        : base(2, CardType.Attack, CardRarity.Uncommon, TargetType.AllEnemies, autoAdd: false)
    {
    }

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (cardSource != this || target == null) return 0m;
        return AuraCmd.Find(target) != null ? DynamicVars.ExtraDamage.BaseValue : 0m;
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .FromCard(this)
            .TargetingAllOpponents(CombatState!)
            .WithHitFx("vfx/vfx_attack_slash")
            .SpawningHitVfxOnEachCreature()
            .Execute(choiceContext);
    }

    protected override void OnUpgrade()
    {
        // klee-upgrades.yaml: damage +2 (7 -> 9 all); the aura bonus stays 4.
        DynamicVars.Damage.UpgradeValueBy(2m);
    }
}
