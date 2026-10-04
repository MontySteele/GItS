using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// R276 hygiene: FURINA'S ANCIENT UNDER THE STAGE ARM.
///
/// <i>All the World's a Stage</i>, her Ancient, kept in her pool on purpose
/// (`EB-363`: an empty Ancient cell ends the run at the act-two door). Since
/// the re-founding (2026-10-04) Fanfare is one number on Furina, so: "At the
/// start of your turn, gain <see cref="PowerModel.Amount"/> Fanfare."
/// </summary>
public sealed class StageRaisePerTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "All the World's a Stage"),
        ("description",
            "At the start of your turn, gain {Amount} [gold]Fanfare[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player?.Creature != Owner) return;
        if (!FurinaStage.LiveFor(Owner)) return;
        using (FurinaStageLedger.For(Owner)
                   .CausedBy(FurinaStage.AllTheWorldsAStageTitle))
        {
            await FurinaStage.Gain(choiceContext, Owner, (int)Amount,
                                   FurinaStage.AllTheWorldsAStageTitle);
        }
    }
}
