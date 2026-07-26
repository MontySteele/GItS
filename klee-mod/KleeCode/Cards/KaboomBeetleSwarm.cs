using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards;

/// <summary>
/// Sheet: uncommon attack, cost 2, 5 damage x3 at random enemies, +3 per hit
/// vs Bombed enemies. Hand-written (R23 batch -- the bonus needs the bomb
/// system, and ModifyDamageAdditive is the verified per-target idiom).
///
/// The bonus checks the bomb AT HIT TIME: the first hit of this card can pop
/// the bombs (early detonation), and later hits on that enemy then get no
/// bonus -- same as the sim, where bonus_vs_bombed is evaluated per hit
/// against live bomb state.
/// </summary>
public sealed class KaboomBeetleSwarm : CustomCardModel, IElementalCard
{
    /// <summary>All of Klee's attacks apply Pyro (sheet: catalyst-grade cadence).</summary>
    public Element Element => Element.Pyro;

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { KleeKeywords.AppliesPyro };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        KleeCardTooltips.ForCard(base.ExtraHoverTips, this, Element.Pyro);

    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("kaboom_beetle_swarm");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Kaboom Beetle Swarm"),
        ("description",
            "Deal {Damage:diff()} damage to random enemies 3 times. "
          + "[gold]Bombed[/gold] enemies take {ExtraDamage:diff()} more per hit."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(5m, ValueProp.Move),
            new ExtraDamageVar(3m),
        };

    // autoAdd: false -- KleeCardPool declares pool membership itself (see Kaboom).
    public KaboomBeetleSwarm()
        : base(2, CardType.Attack, CardRarity.Uncommon, TargetType.AllEnemies, autoAdd: false)
    {
    }

    public override decimal ModifyDamageAdditive(
        Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? cardSource)
    {
        if (cardSource != this || target == null) return 0m;
        return target.Powers.OfType<BombPower>().Any()
            ? DynamicVars.ExtraDamage.BaseValue
            : 0m;
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .WithHitCount(3)
            .FromCard(this)
            .TargetingRandomOpponents(CombatState!)
            .WithHitFx("vfx/vfx_attack_slash")
            .Execute(choiceContext);
    }

    protected override void OnUpgrade()
    {
        // klee-upgrades.yaml: bonus_vs_bombed +2 (3 -> 5).
        DynamicVars.ExtraDamage.UpgradeValueBy(2m);
    }
}
