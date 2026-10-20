using System.Collections.Generic;
using System.Linq;
using Godot;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Models.RelicPools;

namespace KleeMod;

/// <summary>
/// Kokomi's relic pool. MEMBERS: the Silent's curated borrow, her starter (the
/// Tamakushi Casket), its Touch of Orobas upgrade (the Watatsumi Casket) and
/// her own seven (<c>review/active/kokomi-relics-potions-2026-10-15.md</c>).
/// The starter and the Ancient are members for legal pool membership:
/// RelicModel.Pool is a non-virtual First() over AllRelicPools and THROWS for
/// a poolless relic; Starter and Ancient rarity keep both out of every reward
/// roll. The seven are members for the same reason.
///
/// THE OFFER is <see cref="GetUnlockedRelics"/>, Klee's and Varka's rule
/// (<c>Relics.ArmRelicPools</c>): the Casket, her seven and the Watatsumi
/// Casket. The Silent borrow leaves the offer (kit census pick 2, ruled
/// 2026-10-15: "drop the whole Silent borrow from each kit once it has its
/// own full set").
/// </summary>
public sealed class KokomiRelicPool : RelicPoolModel
{
    // Her own orb (card frames stage 2): the kit card pool's energy name, so
    // BaseLib's icon hook draws the same orb on this pool's tooltips.
    public override string EnergyColorName => KitEnergyIcon.NameOf<KokomiCardPool>();

    public override Color LabOutlineColor => new("6FC8D6");

    protected override IEnumerable<RelicModel> GenerateAllRelics() =>
        // The borrowed roster MINUS Helical Dart and Snecko Skull (the ruling
        // on QUEUE pick `fanout-picks-2026-09-16 4.3`, at its default). See
        // InheritedSilentRelics for why the two go and why the drop is safe.
        // Tingsha and Tough Bandages go too: no card here discards (kit
        // census pick 2, ruled 2026-10-15).
        InheritedSilentRelics.Curated(dropDiscard: true)
            .Append(ModelDb.Relic<Relics.TamakushiCasket>())
            .Append(ModelDb.Relic<Relics.WatatsumiCasket>())
            .Append(ModelDb.Relic<Relics.SangoPearl>())
            .Append(ModelDb.Relic<Relics.ResistanceArmband>())
            .Append(ModelDb.Relic<Relics.ElectroSigil>())
            .Append(ModelDb.Relic<Relics.EverlastingMoonglow>())
            .Append(ModelDb.Relic<Relics.OceanHuedClam>())
            .Append(ModelDb.Relic<Relics.KurageLantern>())
            .Append(ModelDb.Relic<Relics.ResistanceMusterRoll>());

    public override IEnumerable<RelicModel> GetUnlockedRelics(
        MegaCrit.Sts2.Core.Unlocks.UnlockState unlockState) =>
        Relics.ArmRelicPools.Offer(AllRelics, Relics.ArmRelicPools.KokomiArmPool);
}
