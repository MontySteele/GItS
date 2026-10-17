using System.Collections.Generic;
using System.Linq;
using Godot;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// Yae Miko's relic pool, Kokomi's arrangement. MEMBERS: the Silent's curated
/// borrow, Meditations of a Yako, its Orobas upgrade Enlightened Blessing and
/// her own seven (the Yae pass, 2026-10-16,
/// <c>review/active/yae-ancients-relics-2026-10-16.md</c> sec.3), members so
/// <c>RelicModel.Pool</c> resolves (Starter and Ancient rarity keep the two
/// Meditations out of every reward roll).
///
/// THE OFFER is <see cref="GetUnlockedRelics"/>, the arms' rule
/// (<c>Relics.ArmRelicPools</c>): Meditations, her seven and Enlightened
/// Blessing. The Silent borrow stays a member only, as for Klee, Furina,
/// Varka and Kokomi.
/// </summary>
public sealed class YaeRelicPool : RelicPoolModel
{
    public override string EnergyColorName => "defect";

    public override Color LabOutlineColor => new("B07FE0");

    protected override IEnumerable<RelicModel> GenerateAllRelics() =>
        InheritedSilentRelics.Curated()
            .Append(ModelDb.Relic<Relics.MeditationsOfAYako>())
            .Append(ModelDb.Relic<Relics.EnlightenedBlessing>())
            .Append(ModelDb.Relic<Relics.KitsuneMask>())
            .Append(ModelDb.Relic<Relics.SacredSakuraBranch>())
            .Append(ModelDb.Relic<Relics.ProofreadersGlasses>())
            .Append(ModelDb.Relic<Relics.Electroculus>())
            .Append(ModelDb.Relic<Relics.SaiguusInkstone>())
            .Append(ModelDb.Relic<Relics.KaguraBell>())
            .Append(ModelDb.Relic<Relics.FoxOfuda>());

    public override IEnumerable<RelicModel> GetUnlockedRelics(
        MegaCrit.Sts2.Core.Unlocks.UnlockState unlockState) =>
        Relics.ArmRelicPools.Offer(AllRelics, Relics.ArmRelicPools.YaeArmPool);
}
