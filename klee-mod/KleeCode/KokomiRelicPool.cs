using System.Collections.Generic;
using System.Linq;
using Godot;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.RelicPools;

namespace KleeMod;

/// <summary>
/// Kokomi borrows the Silent relic roster, exactly as the pool shipped. Her
/// starter, the Tamakushi Casket, and its Touch of Orobas upgrade are appended
/// for legal pool membership: RelicModel.Pool is a non-virtual First() over
/// AllRelicPools and THROWS for a poolless relic. Starter and Ancient rarity
/// keep both out of every reward roll.
/// </summary>
public sealed class KokomiRelicPool : RelicPoolModel
{
    public override string EnergyColorName => "silent";

    public override Color LabOutlineColor => new("6FC8D6");

    protected override IEnumerable<RelicModel> GenerateAllRelics() =>
        // The borrowed roster MINUS Helical Dart and Snecko Skull (the ruling
        // on QUEUE pick `fanout-picks-2026-09-16 4.3`, at its default). See
        // InheritedSilentRelics for why the two go and why the drop is safe.
        InheritedSilentRelics.Curated()
            .Append(ModelDb.Relic<Relics.TamakushiCasket>())
            .Append(ModelDb.Relic<Relics.WatatsumiCasket>());
}
