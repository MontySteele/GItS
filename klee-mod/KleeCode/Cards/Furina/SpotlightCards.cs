using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Localization.DynamicVars;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Furina;

/// <summary>The zero-cost Ethereal selector granted by Furina's starter relic.</summary>
public sealed class EtherealSpotlight : CustomCardModel, ICharacterCard
{
    public string CharacterId => "furina";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("ethereal_spotlight");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Ethereal Spotlight"),
        ("description",
            "Choose [gold]Center Stage[/gold] or [gold]Guest Cast[/gold]. "
          + "Center Stage makes Furina cards generate Fanfare. Guest Cast "
          + "empowers all Companion cards."),
    };

    public override IEnumerable<CardKeyword> CanonicalKeywords =>
        new[] { CardKeyword.Ethereal, CardKeyword.Exhaust };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        System.Array.Empty<DynamicVar>();

    public EtherealSpotlight()
        : base(0, CardType.Skill, CardRarity.Token, TargetType.Self, autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var options = new List<CardModel>
        {
            ModelDb.Card<CenterStageOption>(),
        };
        if (Owner.PlayerCombatState?.AllCards.Any(
                card => card is ICompanionCard) == true)
        {
            options.Add(ModelDb.Card<GuestCastOption>());
        }
        var selected = await CardSelectCmd.FromChooseACardScreen(
            choiceContext, options, Owner, canSkip: false);
        var mode = selected is GuestCastOption
            ? SpotlightMode.GuestCast
            : SpotlightMode.CenterStage;
        await SpotlightSystem.Designate(
            choiceContext, Owner.Creature, mode, this);
    }

    protected override void OnUpgrade()
    {
    }
}

public sealed class CenterStageOption : CustomCardModel
{
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("spotlight_center_stage");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Center Stage"),
        ("description",
            "Spotlight Furina. Her cards generate 2 Fanfare when played, "
          + "but receive no numeric boost."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        System.Array.Empty<DynamicVar>();

    public CenterStageOption()
        : base(0, CardType.Skill, CardRarity.Token, TargetType.Self, autoAdd: false)
    {
    }

    protected override Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay) =>
        Task.CompletedTask;

    protected override void OnUpgrade()
    {
    }
}

public sealed class GuestCastOption : CustomCardModel
{
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("spotlight_guest_cast");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Guest Cast"),
        ("description",
            "Spotlight every Companion card. Their printed damage and Block "
          + "are 50% stronger, but their plays do not generate Fanfare."),
    };

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        System.Array.Empty<DynamicVar>();

    public GuestCastOption()
        : base(0, CardType.Skill, CardRarity.Token, TargetType.Self, autoAdd: false)
    {
    }

    protected override Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay) =>
        Task.CompletedTask;

    protected override void OnUpgrade()
    {
    }
}
