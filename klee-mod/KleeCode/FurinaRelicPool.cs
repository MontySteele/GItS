using System.Collections.Generic;
using System.Linq;
using Godot;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.RelicPools;

namespace KleeMod;

/// <summary>
/// Furina borrows the Silent relic roster for the first playable build. Her
/// starter relic is appended for legal pool membership but Starter rarity
/// keeps it out of ordinary reward rolls.
/// </summary>
public sealed class FurinaRelicPool : RelicPoolModel
{
    public override string EnergyColorName => "silent";

    public override Color LabOutlineColor => new("4AA6C8");

    protected override IEnumerable<RelicModel> GenerateAllRelics() =>
        ModelDb.RelicPool<SilentRelicPool>().AllRelics
            .Append(ModelDb.Relic<Relics.EtherealSpotlightRelic>());
}
