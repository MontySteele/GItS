using System.Collections.Generic;
using System.Linq;
using Godot;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// Yae Miko's relic pool, Kokomi's arrangement: the Silent's curated borrow
/// (her own relics are a later paper), plus Meditations of a Yako and its
/// Orobas upgrade Enlightened Blessing as MEMBERS so <c>RelicModel.Pool</c>
/// resolves (Starter and Ancient rarity keep both out of every reward roll).
/// </summary>
public sealed class YaeRelicPool : RelicPoolModel
{
    public override string EnergyColorName => "defect";

    public override Color LabOutlineColor => new("B07FE0");

    protected override IEnumerable<RelicModel> GenerateAllRelics() =>
        InheritedSilentRelics.Curated()
            .Append(ModelDb.Relic<Relics.MeditationsOfAYako>())
            .Append(ModelDb.Relic<Relics.EnlightenedBlessing>());
}
