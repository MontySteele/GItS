using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using BaseLib.Abstracts;
using MegaCrit.Sts2.Core.Entities.Creatures;
using MegaCrit.Sts2.Core.Entities.Powers;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod.Powers;

/// <summary>
/// ALICE'S MASTERPIECE, Klee's second Ancient (pool completion, 2026-10-01;
/// <c>Cards/AlicesMasterpiece.cs</c>, paper
/// <c>review/active/pool-completion-2026-10-01.md</c> sec.3): "When one of
/// your Bombs goes off, it stays on the enemy at half its size, rounded down."
/// Bends rule 2, under which a set-off Bomb is gone.
///
/// READINGS, recorded in the provenance note:
///   * EVERY CHARGE THAT GOES OFF, Mines included (her keyword: "A Bomb that
///     also goes off just before its enemy attacks"), whatever set it off.
///   * HALF THE PRINTED SIZE, rounded down -- the charge's own size, before
///     The Big One's multiplier or Boom Badge; a 1 leaves nothing.
///   * THE HALF KEEPS ITS KIND (a Mine stays a Mine) and LOSES ITS PAYLOAD
///     (Jumpy Dumpty's Mines ride the first explosion only), so the remnant
///     is a smaller charge and nothing more.
///   * A MOVE, NOT A PLACEMENT (<c>ProtoBombPower.Place</c>'s `relocated`):
///     the Dodoco Charm is paid once per Bomb, when it arrived.
///   * IT STAYS ON ITS ENEMY, dead or alive; on a dead one it jumps (rule 3)
///     through the same sweep every charge on a corpse takes.
/// Copies do not stack (a second Masterpiece is a dead Power). Game-side only,
/// like every Ancient (the sim models no events).
/// </summary>
public sealed class AlicesMasterpiecePower : PowerModel, ILocalizationProvider
{
    public List<(string, string)>? Localization => new()
    {
        ("title", "Alice's Masterpiece"),
        ("description",
            "When one of your [gold]Bombs[/gold] goes off, it stays on the "
          + "enemy at half its size, rounded down."),
    };

    public override PowerType Type => PowerType.Buff;

    public override PowerStackType StackType => PowerStackType.Counter;

    /// <summary>The size that stays: half, rounded down.</summary>
    public static int Remnant(int size) => size <= 1 ? 0 : size / 2;

    internal static async Task Remain(
        PlayerChoiceContext choiceContext, Creature applier, Creature target,
        ProtoBombPower.ProtoCharge charge, CardModel? cardSource)
    {
        if (!applier.Powers.OfType<AlicesMasterpiecePower>().Any()) return;
        var half = Remnant(charge.Size);
        if (half <= 0) return;
        await ProtoBombPower.Place(choiceContext, target, half, charge.IsMine,
                                   payloadMineAll: 0, applier, cardSource,
                                   relocated: true);
    }
}
