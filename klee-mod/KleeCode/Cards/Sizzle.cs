using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards;

/// <summary>
/// Sheet: common attack, cost 1, 7 damage; +5 more if the target has a
/// non-Pyro aura. Hand-written (R23): the conditional op is aura state, and
/// aura state now exists.
///
/// The predicate is SNAPSHOTTED before the first hit, ported from tier0
/// _predicate("target_has_nonpyro_aura"): the card's own Pyro hit consumes an
/// off-element aura via reaction, and that consumption is exactly what the
/// bonus rewards -- reading the aura after the hit would make the bonus
/// unreachable.
/// </summary>
public sealed class Sizzle : CustomCardModel, IElementalCard
{
    /// <summary>All of Klee's attacks apply Pyro (sheet: catalyst-grade cadence).</summary>
    public Element Element => Element.Pyro;

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { KleeKeywords.AppliesPyro };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        KleeCardTooltips.ForCard(base.ExtraHoverTips, this, Element.Pyro);

    public override Texture2D? CustomPortrait => KleeArt.CardPortrait("sizzle");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Sizzle"),
        ("description",
            "Deal {Damage:diff()} damage. If the target has a non-[gold]Pyro[/gold] "
          + "aura, deal {ExtraDamage:diff()} more damage."),
    };

    // ExtraDamage, not a second "Damage": DynamicVarSet is keyed by name, and
    // ExtraDamageVar is the base-game var for a card's second damage number
    // (same reasoning as the generated bomb cards).
    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            new DamageVar(8m, ValueProp.Move),
            new ExtraDamageVar(6m),
        };

    // autoAdd: false -- KleeCardPool declares pool membership itself (see Kaboom).
    public Sizzle()
        : base(1, CardType.Attack, CardRarity.Common, TargetType.AnyEnemy, autoAdd: false)
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        ArgumentNullException.ThrowIfNull(cardPlay.Target, "cardPlay.Target");

        var hadOffElementAura =
            AuraCmd.Find(cardPlay.Target) is { } aura && aura.Element != Element.Pyro;

        await DamageCmd.Attack(DynamicVars.Damage.BaseValue)
            .FromCard(this)
            .Targeting(cardPlay.Target)
            .WithHitFx("vfx/vfx_attack_slash")
            .Execute(choiceContext);

        if (hadOffElementAura && cardPlay.Target.IsAlive)
        {
            await DamageCmd.Attack(DynamicVars.ExtraDamage.BaseValue)
                .FromCard(this)
                .Targeting(cardPlay.Target)
                .WithHitFx("vfx/vfx_attack_slash")
                .Execute(choiceContext);
        }
    }

    protected override void OnUpgrade()
    {
        // klee-upgrades.yaml: conditional_bonus +3 (6 -> 9).
        DynamicVars.ExtraDamage.UpgradeValueBy(3m);
    }
}
