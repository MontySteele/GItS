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
#if PROTOTYPE_CARDS && FURINA_REFRAME
        // THE ARM'S FACE, and it is chosen by the COMPILE constant rather than
        // by the runtime property on purpose: a card's Localization is read
        // once at registration, so a face that asked a settable flag would be
        // whatever the flag happened to be at boot. `-p:FurinaReframe=true` is
        // the dev build that plays this rule, and this is the face it prints;
        // a release build compiles the line below and is byte-identical.
        //
        // It says what R228 option (1) does and nothing more: Center Stage is
        // gone, so there is no choice to describe, and the price is
        // interpolated from the mirrored constant rather than typed -- the
        // same rule `CenterStageOption` follows (EB-89), so a repricing cannot
        // leave the card telling the player a retired number.
        ("description",
            "Spotlight every Companion card. Their printed damage and Block "
          + $"are 50% stronger. Costs {FurinaReframeLaw.SpotlightDesignateEncoreCost} "
          + "[gold]Encore[/gold]."),
#else
        ("description",
            "Choose [gold]Center Stage[/gold] or [gold]Guest Cast[/gold]. "
          + "Center Stage makes Furina cards generate [gold]Fanfare[/gold]. "
          + "Guest Cast "
          + "empowers all Companion cards."),
#endif
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
#if PROTOTYPE_CARDS
        // FURINA REFRAME, R228 option (1): ONE MODE, PRICED. With the arm's
        // SPOTLIGHT leg on there is no choice left to offer -- Center Stage
        // retires -- so the screen below is skipped entirely rather than shown
        // with one option on it, and the selector aims Guest Cast for its
        // Encore price. Mirrors tier0 `_op_spotlight_designate`, which takes
        // the same early branch above its own heuristic.
        if (FurinaReframe.SpotlightLiveFor(Owner.Creature))
        {
            await SpotlightSystem.DesignateOneMode(
                choiceContext, Owner.Creature, this);
            return;
        }
#endif
        // The choose-a-card screen dereferences the first option's Owner
        // (asserting mutability, then initializing the pile viewer from it),
        // so the options must be combat-scoped owned instances -- canonical
        // ModelDb templates softlock it, and so do bare ToMutable() copies
        // (Owner == null). CombatState.CreateCard is the base game's own
        // pattern for screen options (AttackPotion / Discovery via
        // CardFactory.GetDistinctForCombat).
        var combatState = Owner.Creature!.CombatState!;
        var options = new List<CardModel>
        {
            combatState.CreateCard(ModelDb.Card<CenterStageOption>(), Owner),
        };
        if (Owner.PlayerCombatState?.AllCards.Any(
                card => card is ICompanionCard) == true)
        {
            options.Add(combatState.CreateCard(ModelDb.Card<GuestCastOption>(), Owner));
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
            // EB-89: the rate is interpolated, not printed.
            $"Spotlight Furina. Her cards generate "
          + $"{SpotlightSystem.FanfarePerCenterStagePlay} [gold]Fanfare[/gold] "
          + "when "
          + "played, but receive no numeric boost."),
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
          + "are 50% stronger, but their plays do not generate "
          + "[gold]Fanfare[/gold]."),
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
