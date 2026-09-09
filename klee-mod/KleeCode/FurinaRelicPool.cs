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

    protected override IEnumerable<RelicModel> GenerateAllRelics()
    {
        IEnumerable<RelicModel> relics = ModelDb.RelicPool<SilentRelicPool>().AllRelics
            .Append(ModelDb.Relic<Relics.EtherealSpotlightRelic>())
            // EPOCH 2 / D1 (audit sec.1.2): the upgraded starter was poolless and
            // RelicModel.Pool throws for a poolless relic, mid-run at the Touch
            // of Orobas grant. Ancient rarity keeps it off reward rolls, which
            // take Common/Uncommon/Rare/Shop/Boss only.
            .Append(ModelDb.Relic<Relics.CurtainNeverFalls>());
#if PROTOTYPE_CARDS
        // THE STAGE'S STARTING RELIC (R269, EB-725). The first Stage deploy
        // read back Ironclad at character select: KleeSelfCheck R7 named it --
        // Salon Solitaire was in NO pool, RelicModel.Pool threw inside
        // SelectCharacter, and the character looked selected but was not. A
        // starter is never rolled as a reward, so pool membership is only
        // what lets Pool resolve.
        relics = relics.Append(ModelDb.Relic<Relics.SalonSolitaire>());
#endif
        return relics;
    }
}
