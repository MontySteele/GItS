using System.Collections.Generic;
using System.Linq;
using Godot;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.RelicPools;

namespace KleeMod;

/// <summary>
/// Klee's relic pool: Silent's borrowed contents (the C1 stub, unchanged)
/// PLUS Pounding Surprise.
///
/// This pool is NOT cosmetic — it is what makes Pounding Surprise legal.
/// RelicModel.Pool is non-virtual and does
/// <c>AllRelicPools.First(p =&gt; p.AllRelicIds.Contains(Id))</c>; a relic in no
/// pool THROWS there, and that getter runs inside
/// NCharacterSelectScreen.SelectCharacter (via DynamicDescription's energy
/// icon lookup). The throw aborts SelectCharacter after the panel text
/// updates but before the lobby assignment — finding 11's exact
/// looks-selected-but-is-not failure, reached through a relic this time
/// (finding 27). AllRelicPools derives from AllCharacters.Select(c =&gt;
/// c.RelicPool), so Klee.RelicPool returning this pool is the entire
/// registration — no Harmony.
///
/// Reward safety: relic rewards roll Common/Uncommon/Rare/Shop/Boss, never
/// Starter, so Pounding Surprise cannot drop as loot from being pooled here;
/// Silent relics resolve their own Pool to SilentRelicPool because Silent
/// precedes Klee in AllCharacters and First() takes the earliest hit.
/// </summary>
public sealed class KleeRelicPool : RelicPoolModel
{
    // Same borrowed-red C1 stubs as KleeCardPool.
    public override string EnergyColorName => "ironclad";

    public override Color LabOutlineColor => new Color("E85A4F");

    protected override IEnumerable<RelicModel> GenerateAllRelics()
    {
        return ModelDb.RelicPool<SilentRelicPool>().AllRelics
            .Append(ModelDb.Relic<Relics.PoundingSurprise>());
    }
}
