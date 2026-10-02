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

namespace KleeMod.Cards.Kokomi;

/// <summary>
/// Kokomi's second Ancient-rarity card (pool completion, 2026-10-01;
/// review/active/pool-completion-2026-10-01.md sec.3, ruled at the default):
/// "The first time each turn you play a card on the Bake-Kurage, its now-line
/// happens too." Bends the Kokomi arm's rule 2, where a card does one half or
/// the other. Cards with no now-line (Nip) do not use up the once. The rule
/// and its readings are <see cref="DivineStrategyPower"/>'s; the generated
/// Plan branch asks it.
///
/// Game-side only, like every Ancient: the Dusty Tome draws one of her
/// Ancients at random and grants it UPGRADED (read it at 1 Energy).
/// Membership is <c>RosterAncientCards.Kokomi</c>. Compiled with the prototype
/// surface only. Numbers witnessed by
/// <c>tools/lint_handwritten_parity.ANCIENT_WITNESS</c>. Art: the placeholder
/// until the art pass.
/// </summary>
public sealed class DivineStrategy : CustomCardModel, ICharacterCard
{
    public string CharacterId => "kokomi";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("divine_strategy");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Divine Strategy"),
        ("description",
            "The first time each turn you play a card on the "
          + "[gold]Bake-Kurage[/gold], its now-line happens too."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForPlan(base.ExtraHoverTips, this);

    // autoAdd: false -- RosterAncientCards.Kokomi owns membership.
    public DivineStrategy()
        : base(2, CardType.Power, CardRarity.Ancient, TargetType.Self,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<DivineStrategyPower>(
            choiceContext, Owner.Creature, 1, applier: Owner.Creature,
            cardSource: this);
    }

    protected override void OnUpgrade()
    {
        EnergyCost.UpgradeBy(-1);
    }
}
