using System.Collections.Generic;
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

/// <summary>
/// Furina's Ancient-rarity card. Dusty Tome is its only door -- reward,
/// transform and shop generation all filter CardRarity.Ancient upstream, so
/// membership in RosterAncientCards.Furina does not make it rollable.
/// DustyTome.AfterObtained upgrades the grant.
///
/// "At the start of your turn, your back performer gains 2 Fanfare" (3
/// upgraded), through <c>StageRaisePerTurnPower</c> (R276 hygiene). Its
/// shipped face, an Encore drip, went with the shipped kits (legacy cleanup
/// stage 5). Sim twin: EB-30m.
/// </summary>
public sealed class AllTheWorldsAStage : CustomCardModel, ICharacterCard
{
    public string CharacterId => "furina";

    // Art: deliberate reuse of The Sea Is My Stage's portrait until the art
    // pass assigns the ancient its own crop (look-pass item, not a blocker).
    public override Texture2D? CustomPortrait =>
        RosterArt.CardPortrait("the_sea_is_my_stage");

    public override List<(string, string)>? Localization => new()
    {
        ("title", "All the World's a Stage"),
        ("description", Face),
    };

    private const string Face =
        "At the start of your turn, your [gold]back performer[/gold] "
      + "gains {StageRaise:diff()} [gold]Fanfare[/gold].";

    protected override IEnumerable<DynamicVar> CanonicalVars =>
        new List<DynamicVar>
        {
            // The shipped Encore drip's number, kept for both engines'
            // witness (tools/lint_handwritten_parity.ANCIENT_WITNESS).
            new DynamicVar("PowerAmount", 5m),
            // R276: the Stage arm's Raise, 2 and 3 upgraded.
            new DynamicVar("StageRaise", 2m),
        };

    // autoAdd: false -- RosterAncientCards.Furina owns membership (concat
    // into FurinaCardPool.GenerateAllCards).
    public AllTheWorldsAStage()
        : base(1, CardType.Power, CardRarity.Ancient, TargetType.Self, autoAdd: false)
    {
    }

    protected override async Task OnPlay(PlayerChoiceContext choiceContext, CardPlay cardPlay)
    {
        if (!FurinaStage.LiveFor(Owner.Creature)) return;
        await PowerCmd.Apply<StageRaisePerTurnPower>(
            choiceContext, Owner.Creature,
            DynamicVars["StageRaise"].IntValue,
            applier: Owner.Creature, cardSource: this);
    }

    protected override void OnUpgrade()
    {
        DynamicVars["PowerAmount"].UpgradeValueBy(2m);
        DynamicVars["StageRaise"].UpgradeValueBy(1m);
    }
}
