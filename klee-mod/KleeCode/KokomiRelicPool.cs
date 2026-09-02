using System.Collections.Generic;
using System.Linq;
using Godot;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.RelicPools;

namespace KleeMod;

/// <summary>
/// Kokomi borrows the Silent relic roster for the playtest build, exactly as
/// Furina does. Her starter is appended for legal pool membership; Starter
/// rarity keeps it out of ordinary reward rolls.
///
/// The borrow has a KNOWN consequence worth stating rather than discovering:
/// a real Silent relic can co-occur with Pearl of Wisdom in one run, which is
/// why the relic ships a packed icon path of its own instead of leaning on
/// the borrowed snake_ring slug (see PearlOfWisdomRelic).
/// </summary>
public sealed class KokomiRelicPool : RelicPoolModel
{
    public override string EnergyColorName => "silent";

    public override Color LabOutlineColor => new("6FC8D6");

    protected override IEnumerable<RelicModel> GenerateAllRelics()
    {
        var relics = Shipped();
#if PROTOTYPE_CARDS
        // QUARANTINED (the Kokomi overhaul, slice one). MEMBERSHIP, not loot,
        // and it is the same non-negotiable the two Appends below record:
        // RelicModel.Pool is a non-virtual First() over AllRelicPools and
        // THROWS for a poolless relic, so the arm's starting relic has to be
        // a member of a pool the moment a run hands it over -- which is at
        // character select, the earliest moment there is.
        //
        // APPENDED UNDER THE COMPILE FLAG AND NOT UNDER THE ARM'S OWN, which
        // is deliberate: `GenerateAllRelics` runs once at pool construction,
        // long before anything reads `KokomiOverhaul.Enabled`, so gating it on
        // the arm would be a race rather than a quarantine. The compile flag
        // is the quarantine here as everywhere else -- a release build does
        // not contain the type -- and Starter rarity keeps it out of every
        // reward roll in a dev build, exactly as it keeps the Pearl out.
        relics = relics.Append(ModelDb.Relic<Relics.TamakushiCasket>());
#endif
        return relics;
    }

    private static IEnumerable<RelicModel> Shipped() =>
        ModelDb.RelicPool<SilentRelicPool>().AllRelics
            .Append(ModelDb.Relic<Relics.PearlOfWisdomRelic>())
            // EPOCH 2 / D1 (audit sec.1.2). The UPGRADED starter was in no pool at
            // all. RelicModel.Pool is a non-virtual First() over AllRelicPools
            // and THROWS for a poolless relic -- finding 27's crash class, one
            // door over: this one is reachable not at character select but the
            // moment Touch of Orobas hands the upgrade over mid-run.
            //
            // Membership does NOT make it loot. Relic rewards roll
            // Common/Uncommon/Rare/Shop/Boss (decompiled; the same enumeration
            // KleeRelicPool's header records for the Starter-rarity case), and
            // these are RelicRarity.Ancient. Same shape as the Ancient CARDS in
            // the card pools: visible members, never rolled.
            .Append(ModelDb.Relic<Relics.PearlOfInsightRelic>());
}
