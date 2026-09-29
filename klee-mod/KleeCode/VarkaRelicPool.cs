#if PROTOTYPE_CARDS && VARKA_PROTOTYPE
using System.Collections.Generic;
using System.Linq;
using Godot;
using MegaCrit.Sts2.Core.Models;

namespace KleeMod;

/// <summary>
/// Varka's relic pool: the Silent's curated borrow (the Kokomi arrangement)
/// plus Boreas's Fang, a member so <c>RelicModel.Pool</c> resolves at
/// character select; Starter rarity keeps it out of every reward roll.
/// </summary>
public sealed class VarkaRelicPool : RelicPoolModel
{
    public override string EnergyColorName => "silent";

    public override Color LabOutlineColor => new("4CC2A8");

    protected override IEnumerable<RelicModel> GenerateAllRelics() =>
        InheritedSilentRelics.Curated()
            .Append(ModelDb.Relic<Relics.BoreasFang>());
}
#endif
