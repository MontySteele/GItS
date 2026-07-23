using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Elements;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Cards.Furina;

/// <summary>
/// Furina's 70-energy kit Burst. It is granted to hand at a full meter,
/// Retained until cast, and never enters draft or transform pools.
/// </summary>
public sealed class LetThePeopleRejoice
    : CustomCardModel, IElementalCard, ICharacterCard
{
    public Element Element => Element.Hydro;

    public string CharacterId => "furina";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("let_the_people_rejoice");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Let the People Rejoice"),
        ("description",
            "Costs your full [gold]Burst Energy[/gold] meter. "
          + "Deal {Damage} damage to ALL enemies, plus 1 damage per "
          + "4 [gold]Fanfare[/gold]. Gain 6 [gold]Encore[/gold]."),
    };

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Retain, KleeKeywords.AppliesHydro };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new DynamicVar[]
        {
            new DamageVar(8m, ValueProp.Move),
        };

    public LetThePeopleRejoice()
        : base(2, CardType.Attack, CardRarity.Rare,
            TargetType.AllEnemies, autoAdd: false)
    {
        CustomResources<FurinaBurstResource>.SetCanonicalCost(
            this, FurinaResourceConstants.BurstMax);
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var damage = DynamicVars.Damage.BaseValue
            + FurinaResources.Fanfare(Owner.Creature) / 4;
        await DamageCmd.Attack(damage)
            .FromCard(this)
            .TargetingAllOpponents(CombatState!)
            .WithHitFx("vfx/vfx_attack_slash")
            .SpawningHitVfxOnEachCreature()
            .Execute(choiceContext);
        FurinaResources.GainEncore(Owner.Creature, 6);
    }

    protected override void OnUpgrade()
    {
        // Kit cards are not smithable.
    }
}
