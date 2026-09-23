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
/// <i>All the World's a Stage</i> printed "gain N Encore" -- a meter the arm
/// retires (`EB-745`), so under the arm the card was a dead pick at the one
/// door Darv's Dusty Tome opens. It is kept in her pool on purpose (`EB-363`:
/// an empty Ancient cell ends the run at the act-two door), so it gets the
/// Stage's own version of the same idea: at the start of her turn, Raise
/// <see cref="PowerModel.Amount"/> Fanfare on the BACK performer (rule 5 --
/// the bank; alone on stage, the lead). An empty stage raises nothing.
///
/// AFTER THE TURN START, beside the lead's regen (<c>FurinaStageHooks</c>):
/// both are "at the start of your turn" moves on the bars, and neither reads
/// the other -- the regen is the lead's, this is the back's, and with one
/// performer the two simply add.
/// </summary>
public sealed class StageRaisePerTurnPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "All the World's a Stage"),
        ("description",
            "At the start of your turn, [gold]Raise[/gold] {Amount} "
          + "[gold]Fanfare[/gold] on the [gold]back performer[/gold]."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player?.Creature != Owner) return Task.CompletedTask;
        FurinaStage.Raise(Owner, (int)Amount);
        return Task.CompletedTask;
    }
}
