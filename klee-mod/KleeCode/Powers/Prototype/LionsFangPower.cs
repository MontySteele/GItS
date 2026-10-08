using System.Collections.Generic;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Commands;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.ValueProps;

namespace KleeMod.Powers;

/// <summary>
/// Jean, Lion's Fang, Fair Protector: "At the start of your turn, if none of
/// your Bombs went off last turn, gain 8 Block and draw 1 card."
///
/// GROUNDED'S SHAPE WITH A CARD ON IT, and it reads the ledger the same way for
/// the same reason: <c>For</c> rolls to this round, so <c>SetOffLastTurn</c> is
/// exactly the count that stood when the player last passed.
///
/// In Klee's own draftable pool since the Klee-only companions (2026-10-03);
/// no longer a stand-in. Sim twin: <c>tier0.engine.lions_fang</c>.
/// </summary>
public sealed class LionsFangPower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Lion's Fang, Fair Protector"),
        ("description",
            "At the start of your turn, if none of your [gold]Bombs[/gold] "
          + "went off last turn, gain [blue]{Amount}[/blue] [gold]Block[/gold] "
          + "and draw 1 card."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    public override async Task AfterPlayerTurnStart(
        PlayerChoiceContext choiceContext, Player player)
    {
        if (Owner == null || player.Creature != Owner) return;
        if (Amount <= 0) return;
        if (KleeOverhaulLedger.For(Owner).SetOffLastTurn > 0) return;
        await CreatureCmd.GainBlock(Owner, Amount, ValueProp.Unpowered, null);
        // A LITERAL 1, in both engines and for the reason tier0's
        // `MC_LIONS_FANG_DRAW` comment gives: naming it would make
        // `lint_prose_constants` read every "Draw 1 card" in the mod as an
        // un-interpolated copy of this slice's constant. The row's own
        // `description:` is what both engines print.
        await CardPileCmd.Draw(choiceContext, 1, player);
    }
}
