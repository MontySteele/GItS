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
        // The borrowed roster MINUS Helical Dart and Snecko Skull (the ruling
        // on QUEUE pick `fanout-picks-2026-09-16 4.3`, at its default). See
        // InheritedSilentRelics for why the two go and why the drop is safe.
        // Members only: the offer below is her own pool. Salon Solitaire is
        // the Stage's starting relic; a starter is never rolled, so membership
        // only lets RelicModel.Pool resolve (R269, EB-725).
        IEnumerable<RelicModel> relics = InheritedSilentRelics.Curated()
            .Append(ModelDb.Relic<Relics.SalonSolitaire>())
            // EPOCH 2 / D1 (audit sec.1.2): the upgraded starter was poolless and
            // RelicModel.Pool throws for a poolless relic, mid-run at the Touch
            // of Orobas grant. Ancient rarity keeps it off reward rolls, which
            // take Common/Uncommon/Rare/Shop/Boss only.
            .Append(ModelDb.Relic<Relics.CurtainNeverFalls>());
        // FURINA'S OWN TWO (the Salon's Tab, 2026-10-05); membership only,
        // for the reason above. What may be rolled is `GetUnlockedRelics`.
        relics = relics
            .Append(ModelDb.Relic<Relics.OperaGlasses>())
            .Append(ModelDb.Relic<Relics.GrandTheaterProgram>());
        return relics;
    }

    /// <summary>
    /// THE OFFER: Salon Solitaire, her two and The Curtain Never Falls. The
    /// Silent borrow is not offered.
    /// </summary>
    public override IEnumerable<RelicModel> GetUnlockedRelics(
        MegaCrit.Sts2.Core.Unlocks.UnlockState unlockState) =>
        Relics.ArmRelicPools.Offer(AllRelics, Relics.ArmRelicPools.FurinaArmPool);
}
