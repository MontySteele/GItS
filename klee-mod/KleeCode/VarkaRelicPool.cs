#if PROTOTYPE_CARDS
using System.Collections.Generic;
using System.Linq;
using Godot;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// Varka's relic pool. MEMBERS: the Silent's curated borrow (the Kokomi
/// arrangement), Boreas's Fang, Wolf's Gravestone and his own seven
/// (<c>review/active/varka-expansion-2026-10-01.md</c> sec.4). The Fang is a
/// member so <c>RelicModel.Pool</c> resolves at character select (Starter
/// rarity keeps it out of every reward roll); the Gravestone, its Touch of
/// Orobas upgrade, for the same reason at the mid-run grant (Ancient is never
/// rolled either); the seven for the Casket's reason (<c>KokomiRelicPool</c>).
///
/// THE OFFER is <see cref="GetUnlockedRelics"/>, Klee's and Furina's rule
/// (<c>Relics.ArmRelicPools</c>): the Fang, his seven and
/// the Gravestone, and the Silent borrow goes (the paper's pick 1, default
/// (a)). Pick 1(b), the borrow kept beside them, is
/// <c>VarkaArmRelics.KeepSilentBorrow</c>: every member is offered.
/// </summary>
public sealed class VarkaRelicPool : RelicPoolModel
{
    public override string EnergyColorName => "silent";

    public override Color LabOutlineColor => new("4CC2A8");

    protected override IEnumerable<RelicModel> GenerateAllRelics() =>
        InheritedSilentRelics.Curated()
            .Append(ModelDb.Relic<Relics.BoreasFang>())
            .Append(ModelDb.Relic<Relics.WolfsGravestone>())
            .Append(ModelDb.Relic<Relics.KnightsCommission>())
            .Append(ModelDb.Relic<Relics.WindblumeGarland>())
            .Append(ModelDb.Relic<Relics.DandelionSeeds>())
            .Append(ModelDb.Relic<Relics.BannerOfTheWestWind>())
            .Append(ModelDb.Relic<Relics.StormterrorsScale>())
            .Append(ModelDb.Relic<Relics.AndriussHowl>())
            .Append(ModelDb.Relic<Relics.FavoniusDutyRoster>());

    public override IEnumerable<RelicModel> GetUnlockedRelics(
        MegaCrit.Sts2.Core.Unlocks.UnlockState unlockState) =>
        Relics.ArmRelicPools.Offer(
            AllRelics,
            !Relics.VarkaArmRelics.KeepSilentBorrow,
            Relics.ArmRelicPools.VarkaArmPool,
            System.Array.Empty<System.Type>());
}
#endif
