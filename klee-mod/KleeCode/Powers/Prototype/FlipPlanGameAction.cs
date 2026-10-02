using System.Threading.Tasks;
using MegaCrit.Sts2.Core.Entities.Multiplayer;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.GameActions;
using MegaCrit.Sts2.Core.GameActions.Multiplayer;
using MegaCrit.Sts2.Core.Multiplayer.Serialization;

namespace KleeMod.Powers;

/// <summary>
/// FLIP A WAITING PLAN (Kokomi, a Plan stays open, pick 5 (a), 2026-10-01):
/// "Plans carry out on their Plan line; click a waiting Plan to flip it."
///
/// A GAME ACTION AND NOT A DIRECT WRITE, because the flip changes what the
/// next morning does, and the game runs co-op in lockstep: a click that only
/// moved the local queue would carry out one line here and the other on the
/// peer's machine. So the click goes where a card play goes,
/// <c>ActionQueueSynchronizer.RequestEnqueue</c>, and every peer runs
/// <see cref="KokomiPlan.Flip"/> on the same entry. The game finds this
/// action's net twin by reflection over mod assemblies
/// (<c>ActionTypes.Initialize</c>: <c>ReflectionHelper.GetSubtypesInMods</c>),
/// the same door the base game's <c>DiscardPotionGameAction</c> uses for its
/// own.
///
/// PLAY PHASE ONLY (<see cref="GameActionType.CombatPlayPhaseOnly"/>), and
/// <see cref="KokomiPlan.Flip"/> refuses again outside her play phase, so a
/// flip that arrives late cannot land on the next turn's queue.
/// </summary>
public sealed class FlipPlanGameAction : GameAction
{
    private readonly Player _player;
    private readonly uint _index;

    public FlipPlanGameAction(Player player, uint index)
    {
        _player = player;
        _index = index;
    }

    /// <summary>The queue position, front at 0.</summary>
    public uint Index => _index;

    public override ulong OwnerId => _player.NetId;

    public override GameActionType ActionType =>
        GameActionType.CombatPlayPhaseOnly;

    protected override Task ExecuteAction()
    {
        KokomiPlan.Flip(_player, (int)_index);
        return Task.CompletedTask;
    }

    public override INetAction ToNetAction() =>
        new NetFlipPlanAction { index = _index };

    public override string ToString() =>
        $"FlipPlanGameAction for player {_player.NetId} plan {_index}";
}

/// <summary>The wire form of <see cref="FlipPlanGameAction"/>.</summary>
public struct NetFlipPlanAction : INetAction, IPacketSerializable
{
    public uint index;

    public GameAction ToGameAction(Player player) =>
        new FlipPlanGameAction(player, index);

    public void Serialize(PacketWriter writer) => writer.WriteUInt(index, 8);

    public void Deserialize(PacketReader reader) => index = reader.ReadUInt(8);

    public override string ToString() => $"NetFlipPlanAction plan {index}";
}
