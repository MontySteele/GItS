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

namespace KleeMod.Cards.Furina;

/// <summary>
/// Furina's second Ancient-rarity card (pool completion, 2026-10-01;
/// review/active/pool-completion-2026-10-01.md sec.3, ruled at the default):
/// "The first Spend you choose each turn takes no Fanfare." The Furina rules
/// pass (2026-10-01) dropped its short-bar clause: rule 8 now pays back
/// first, then forward, so the mode is offered on the same board as any. The rule and its readings are
/// <see cref="CenterOfAttentionPower"/>'s, read at the Spend gate and the
/// Spend payment (<c>FurinaStage.CanSpend</c> / <c>Spend</c>).
///
/// Game-side only, like every Ancient: the Dusty Tome draws one of her
/// Ancients at random and grants it UPGRADED (read it at 1 Energy).
/// Membership is <c>RosterAncientCards.Furina</c>. Compiled with the
/// prototype surface only. Numbers witnessed by
/// <c>tools/lint_handwritten_parity.ANCIENT_WITNESS</c>. Art: the placeholder
/// until the art pass.
/// </summary>
public sealed class CenterOfAttention : CustomCardModel, ICharacterCard
{
    public string CharacterId => "furina";

    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("center_of_attention");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "Center of Attention"),
        ("description",
            "The first [gold]Spend[/gold] you choose each turn takes no "
          + "[gold]Fanfare[/gold]."),
    };

    protected override IEnumerable<IHoverTip> ExtraHoverTips =>
        ArmKeywordTips.ForSpend(base.ExtraHoverTips, this);

    // autoAdd: false -- RosterAncientCards.Furina owns membership.
    public CenterOfAttention()
        : base(2, CardType.Power, CardRarity.Ancient, TargetType.Self,
               autoAdd: false)
    {
    }

    protected override async Task OnPlay(
        PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        await PowerCmd.Apply<CenterOfAttentionPower>(
            choiceContext, Owner.Creature, 1, applier: Owner.Creature,
            cardSource: this);
    }

    protected override void OnUpgrade()
    {
        EnergyCost.UpgradeBy(-1);
    }
}
