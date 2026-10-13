using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using Godot;
using KleeMod.Powers;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.HoverTips;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Cards.Varka;

/// <summary>
/// Varka's Dusty Tome Ancient (the Varka review,
/// review/active/varka-review-2026-10-12.md sec.6, ruled 2026-10-12: "Both
/// sound workable to me"): "Your cards read your Oath of every element
/// together." The Rare Elixir of the Four Winds' one-turn effect for the whole
/// combat, and the review's "both at once" power, sold openly as the
/// once-a-run bend of his rule that cards read only the current element's
/// Oath. The rule is the ledger's
/// (<see cref="VarkaOathLedger.AllFourThisCombat"/>);
/// <see cref="AllFourWindsPower"/> is its badge.
///
/// Game-side only, like every kit's second Ancient: the Darv event's Dusty
/// Tome draws it (the vanilla Tome skips Dandelion Gale, an Archaic Tooth
/// card) and grants it UPGRADED, so read it at 2 Energy. Membership is
/// <c>RosterAncientCards.Varka</c>. Numbers witnessed by
/// <c>tools/lint_handwritten_parity.ANCIENT_WITNESS</c>.
/// </summary>
public sealed class AllFourWinds : CustomCardModel, ICharacterCard
{
    public string CharacterId => "varka";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("all_four_winds");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "All Four Winds"),
        ("description",
            "Your cards read your [gold]Oath[/gold] of every element "
          + "together."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForOath(base.ExtraHoverTips, this);

    // autoAdd: false -- RosterAncientCards.Varka owns membership.
    public AllFourWinds()
        : base(3, CardType.Power, CardRarity.Ancient, TargetType.Self,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        var owner = Owner.Creature;
        if (!VarkaOath.Live(owner)) return;
        VarkaOathLedger.For(owner).ReadAllFourThisCombat();
        await PowerCmd.Apply<AllFourWindsPower>(
            choiceContext, owner, 1, applier: owner, cardSource: this);
        await OathBadge.Sync(choiceContext, owner);
    }

    protected override void OnUpgrade()
    {
        EnergyCost.UpgradeBy(-1);
    }
}
